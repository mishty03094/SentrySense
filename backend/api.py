# uvicorn backend.api:app --reload

from fastapi import FastAPI
from pydantic import BaseModel
import json
from backend.slack_alerts import send_slack_alert
from fastapi_utils.tasks import repeat_every
from typing import List
import os

app = FastAPI()

class ThreatReport(BaseModel):
    threat_type: str
    predicted_time: str | None = None
    description: str
    risk_level: str
    affected_systems: list[str]
    suggested_fixes: list[str]
    confidence_score: float
    confidence_reasoning: str
    file: str

# --- ROUTES ---

@app.post("/report/anomaly")
async def report_anomaly(_: dict):
    log_path = "simulation_and_detection_/logs/stream_logs.jsonl"
    seen_path = "backend/seen_anomalies.json"

    try:
        with open(log_path, "r") as f:
            lines = f.readlines()
            if not lines:
                return {"status": "no logs to process"}
            latest_entry = json.loads(lines[-1])
    except Exception as e:
        return {"error": f"Log read error: {e}"}

    stream_index = latest_entry.get("stream_index")
    anomaly = latest_entry.get("anomaly", "")
    reason = latest_entry.get("reason", "")
    raw = latest_entry.get("raw_features", {})

    # Load seen anomaly indexes
    try:
        with open(seen_path, "r") as f:
            seen = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        seen = []

    if stream_index in seen:
        return {"status": "already alerted"}

    if anomaly in [True, "medium", "high", "low_level"]:
        unknown_fields = []
        if raw.get("masked_user", 0) == -1:
            unknown_fields.append("user")
        if raw.get("source_ip", 0) == -1:
            unknown_fields.append("source IP")
        if raw.get("destination_ip", 0) == -1:
            unknown_fields.append("destination IP")

        if unknown_fields:
            reason += f"\n⚠️ Unknown {', '.join(unknown_fields)} involved."

        message = (
            f"🚨 Anomaly Detected!\n"
            f"• Stream Index: {stream_index}\n"
            f"• Type: {anomaly}\n"
            f"• Reason: {reason.strip()}"
        )
        send_slack_alert(message)

        seen.append(stream_index)
        with open(seen_path, "w") as f:
            json.dump(seen, f, indent=2)

        return {"status": "new anomaly alerted"}

    return {"status": "no actionable anomaly"}


@app.post("/report/threat")
async def report_threat(data: ThreatReport):
    file_path = "predictive_ai/predicted_threats.json"

    try:
        with open(file_path, "r") as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.insert(0, data.dict())  # Newest on top

    with open(file_path, "w") as f:
        json.dump(existing_data[:10], f, indent=2)  # Keep latest 10 threats

    if data.risk_level.lower() == "high":
        fixes = "\n• " + "\n• ".join(data.suggested_fixes[:3])
        message = f"⚠️ High Risk Threat: {data.threat_type}"
        blocks = [
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*🚨 High Risk Threat Detected*\n*Type:* {data.threat_type}\n*Affected Systems:* {', '.join(data.affected_systems)}\n*Confidence:* {round(data.confidence_score * 100)}%"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Description:*\n{data.description}"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Top Suggested Fixes:*{fixes}"}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": f"📄 Report File: `{data.file}`"}]}
        ]
        send_slack_alert(message, blocks)

    elif data.risk_level.lower() == "medium":
        fixes = "\n• " + "\n• ".join(data.suggested_fixes[:2])
        message = f"🔎 Medium Risk Threat Identified: {data.threat_type}"
        blocks = [
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*🔎 Medium Risk Threat Identified*\n*Type:* {data.threat_type}\n*Confidence:* {round(data.confidence_score * 100)}%"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Description:*\n{data.description[:250]}..."}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Suggested Next Steps:*{fixes}"}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": f"📄 Reference: `{data.file}`"}]}
        ]
        send_slack_alert(message, blocks)

    return {"status": "threat recorded"}

# --- BACKGROUND TASK ---

@app.on_event("startup")
@repeat_every(seconds=30)
def monitor_predicted_threats():
    try:
        with open("predictive_ai/predicted_threats.json", "r") as f:
            current_threats: List[dict] = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        current_threats = []

    try:
        with open("backend/seen_threats.json", "r") as f:
            seen: List[str] = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        seen = []

    new_alerts = []
    for threat in current_threats:
        threat_id = threat.get("file")
        risk_level = threat.get("risk_level", "").lower()
        if threat_id in seen:
            continue

        if risk_level == "high":
            fixes = "\n• " + "\n• ".join(threat.get("suggested_fixes", [])[:3])
            message = f"⚠️ High Risk Threat: {threat.get('threat_type')}"
            blocks = [
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*🚨 High Risk Threat Detected*\n*Type:* {threat.get('threat_type')}\n*Affected Systems:* {', '.join(threat.get('affected_systems', []))}\n*Confidence:* {round(threat.get('confidence_score', 0) * 100)}%"}},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*Description:*\n{threat.get('description')}"}},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*Top Suggested Fixes:*{fixes}"}},
                {"type": "context", "elements": [{"type": "mrkdwn", "text": f"📄 Report File: `{threat.get('file')}`"}]}
            ]
            send_slack_alert(message, blocks)
            new_alerts.append(threat_id)

        elif risk_level == "medium":
            fixes = "\n• " + "\n• ".join(threat.get("suggested_fixes", [])[:2])
            message = f"🔎 Medium Risk Threat Identified: {threat.get('threat_type')}"
            blocks = [
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*🔎 Medium Risk Threat Identified*\n*Type:* {threat.get('threat_type')}\n*Confidence:* {round(threat.get('confidence_score', 0) * 100)}%"}},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*Description:*\n{threat.get('description', '')}"}},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*Suggested Next Steps:*{fixes}"}},
                {"type": "context", "elements": [{"type": "mrkdwn", "text": f"📄 Reference: `{threat.get('file')}`"}]}
            ]
            send_slack_alert(message, blocks)
            new_alerts.append(threat_id)

    if new_alerts:
        seen.extend(new_alerts)
        with open("backend/seen_threats.json", "w") as f:
            json.dump(seen, f, indent=2)

@app.on_event("startup")
@repeat_every(seconds=20)
def monitor_anomaly_logs():
    log_path = "simulation_and_detection_/logs/stream_logs.jsonl"
    seen_path = "backend/seen_anomalies.json"

    # Load seen
    try:
        with open(seen_path, "r") as f:
            seen = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        seen = []

    if not os.path.exists(log_path):
        return

    with open(log_path, "r") as f:
        lines = f.readlines()

    new_alerts = []
    for line in lines:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        idx = entry.get("stream_index")
        if idx in seen:
            continue

        anomaly = entry.get("anomaly")
        raw = entry.get("raw_features", {})

        if anomaly not in [True, "medium", "low_level"]:
            continue  # skip noise

        header = ""
        emoji = ""
        if anomaly is True:
            emoji = "⚠️"
            header = f"{emoji} High Anomaly Detected"
        elif anomaly == "medium":
            emoji = "🔍"
            header = f"{emoji} Medium Time-Based Anomaly"
        elif anomaly == "low_level":
            emoji = "ℹ️"
            header = f"{emoji} Low-Level Anomaly Insight"

        # Check for unknowns
        unknowns = []
        if raw.get("masked_user", 0) == -1:
            unknowns.append("User")
        if raw.get("source_ip", 0) == -1:
            unknowns.append("Source IP")
        if raw.get("destination_ip", 0) == -1:
            unknowns.append("Destination IP")

        unknown_text = ""
        if unknowns:
            unknown_text = f"\n*Detected Unknown Entities:* {', '.join(unknowns)}"

        # Reason text
        reasons = entry.get("why", [])
        reason_text = "\n• " + "\n• ".join(reasons) if reasons else ""
        simple_reason = entry.get("reason", "")
        if simple_reason and not reason_text:
            reason_text = f"\n• {simple_reason}"

        message = (
            f"{header}\n"
            f"*Log Index:* {idx}"
            f"{unknown_text}"
            f"\n*Why:*\n{reason_text}"
        )

        send_slack_alert(message)
        new_alerts.append(idx)

    if new_alerts:
        seen.extend(new_alerts)
        with open(seen_path, "w") as f:
            json.dump(seen, f, indent=2)
