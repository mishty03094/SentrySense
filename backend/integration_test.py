import requests
import json

anomaly = json.load(open("simulation_and_detection/logs/sample_logs.json"))
threat = json.load(open("backend/predictive_ai/predicted_threats.json"))

# Post anomaly
res1 = requests.post("http://127.0.0.1:8000/report/anomaly", json=anomaly)
print("Anomaly Response:", res1.json())

# Post threat
res2 = requests.post("http://127.0.0.1:8000/report/threat", json=threat)
print("Threat Response:", res2.json())
