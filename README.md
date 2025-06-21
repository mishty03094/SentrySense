# 🛡️ SentrySense – AI-Powered Retail Cyber Defense

> Real-time anomaly detection meets predictive threat intelligence using GenAI + Graph AI.

## 🔧 Components

1. `simulation_and_detection/` – Builds user-behaviour graph and detects anomalies in log data.
2. `predictive_ai/` – Uses Gemini to analyze threat intel and suggest future vulnerabilities.
3. `dashboard/` – Streamlit dashboard showing live alerts and predictive risks.
4. `backend/` – FastAPI server to connect detection + prediction to the dashboard or Slack.

## 📦 Installation

```bash
pip install -r requirements.txt

Running Each Part

cd simulation_and_detection
python anomaly_detection.py

cd predictive_ai
python predict_threats.py

cd dashboard
streamlit run app.py

cd backend
uvicorn api:app --reload

