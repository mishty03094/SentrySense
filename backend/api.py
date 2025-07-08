# uvicorn backend.api:app --reload

from fastapi import FastAPI
from pydantic import BaseModel
import json
from backend.slack_alerts import send_slack_alert
from fastapi_utils.tasks import repeat_every
from typing import List

app = FastAPI()

# Pydantic models
class AnomalyReport(BaseModel):
    user: str
    time: str
    anomaly_type: str

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
async def report_anomaly(data: AnomalyReport):
    with open("simulation_and_detection/logs/sample_logs.json", "w") as f:
        json.dump(data.dict(), f, indent=2)

    alert_types = [
        "high_frequency_action", "impossible_location", "role_action_mismatch",
        "hard_negative", "feature_swap", "unusual_time", "subtle_time",
        "subtle_location", "random_label_noise"
    ]
    if data.anomaly_type in alert_types:
        send_slack_alert(f"🚨 Anomaly Detected: {data.anomaly_type} for {data.user} at {data.time}")

    return {"status": "anomaly recorded"}

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
