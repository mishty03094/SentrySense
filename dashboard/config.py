"""
Configuration file for SentrySense Dashboard
Contains file paths and configuration constants
"""

import os

# Data file paths
ANOMALY_DATA_PATH = os.path.join("..", "simulation_and_detection", "detected_anomalies.json")
THREAT_PREDICTION_PATH = os.path.join("..", "predictive_ai", "predicted_threats.json")

# Dashboard configuration
DASHBOARD_TITLE = "SentrySense Dashboard"
REFRESH_INTERVAL = 30  # seconds
MAX_ANOMALIES_DISPLAY = 50
MAX_THREATS_DISPLAY = 20

# Color scheme for severity levels
SEVERITY_COLORS = {
    "Critical": "#FF4B4B",
    "High": "#FF8C00", 
    "Medium": "#FFD700",
    "Low": "#32CD32"
}

# Risk level colors
RISK_COLORS = {
    "Critical": "#FF4B4B",
    "High": "#FF8C00",
    "Medium": "#FFD700", 
    "Low": "#32CD32"
}

# Chart configuration
CHART_CONFIG = {
    "background_color": "rgba(0,0,0,0)",
    "font_color": "white",
    "grid_color": "#333333"
}

# System monitoring endpoints (if applicable)
MONITORING_ENDPOINTS = {
    "anomaly_detector": "http://localhost:8001/status",
    "threat_predictor": "http://localhost:8002/status",
    "data_collector": "http://localhost:8003/status"
}
