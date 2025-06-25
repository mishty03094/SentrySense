from fastapi import FastAPI
from pydantic import BaseModel
import json
from backend.slack_alerts import send_slack_alert

app = FastAPI()

# Define models
class AnomalyReport(BaseModel):
    user: str
    severity: str
    time: str

class ThreatReport(BaseModel):
    summary: str
    urgency: str

@app.post("/report/anomaly")
async def report_anomaly(data: AnomalyReport):
    with open("backend/simulation_and_detection/detected_anomalies.json", "w") as f:
        json.dump(data.dict(), f, indent=2)
    if data.severity.lower() == "high":
        send_slack_alert(f"🚨 High Anomaly Detected: {data.user} at {data.time}")
    return {"status": "anomaly recorded"}

@app.post("/report/threat")
async def report_threat(data: ThreatReport):
    with open("backend/predictive_ai/predicted_threats.json", "w") as f:
        json.dump(data.dict(), f, indent=2)
    if data.urgency.lower() == "high":
        send_slack_alert(f"⚠️ Predicted Threat: {data.summary}")
    return {"status": "threat recorded"}
