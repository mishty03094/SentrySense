"""
Setup script for SentrySense Dashboard
Creates necessary directories and files
"""

import os
import json

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        "static",
        "visuals",
        "../simulation_and_detection",
        "../predictive_ai"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Directory created/verified: {directory}")

def create_sample_data():
    """Create sample data files if they don't exist"""
    
    # Sample anomaly data
    anomaly_data = [
        {
            "timestamp": "2024-01-15T10:30:00Z",
            "type": "Network Intrusion",
            "severity": "Critical",
            "description": "Suspicious network activity detected from external IP",
            "source_ip": "192.168.1.100",
            "destination_ip": "10.0.0.50",
            "confidence": 0.95
        },
        {
            "timestamp": "2024-01-15T09:15:00Z",
            "type": "Malware Detection",
            "severity": "High",
            "description": "Potential malware signature detected in file transfer",
            "source_ip": "192.168.1.75",
            "destination_ip": "external",
            "confidence": 0.87
        },
        {
            "timestamp": "2024-01-15T08:45:00Z",
            "type": "Authentication Anomaly",
            "severity": "Medium",
            "description": "Multiple failed login attempts detected",
            "source_ip": "192.168.1.200",
            "destination_ip": "server.local",
            "confidence": 0.72
        }
    ]
    
    # Sample threat prediction data
    threat_data = [
        {
            "threat_type": "DDoS Attack",
            "confidence": 0.89,
            "predicted_time": "2024-01-15T14:00:00Z",
            "description": "High probability of distributed denial of service attack based on traffic patterns",
            "risk_level": "High",
            "affected_systems": ["web-server-01", "load-balancer"]
        },
        {
            "threat_type": "Data Exfiltration",
            "confidence": 0.76,
            "predicted_time": "2024-01-15T16:30:00Z",
            "description": "Unusual data transfer patterns suggest potential data theft attempt",
            "risk_level": "Critical",
            "affected_systems": ["database-server", "file-server"]
        }
    ]
    
    # Create anomaly data file
    anomaly_path = "../simulation_and_detection/detected_anomalies.json"
    if not os.path.exists(anomaly_path):
        with open(anomaly_path, 'w') as f:
            json.dump(anomaly_data, f, indent=2)
        print(f"✅ Sample anomaly data created: {anomaly_path}")
    
    # Create threat prediction data file
    threat_path = "../predictive_ai/predicted_threats.json"
    if not os.path.exists(threat_path):
        with open(threat_path, 'w') as f:
            json.dump(threat_data, f, indent=2)
        print(f"✅ Sample threat data created: {threat_path}")

def main():
    """Main setup function"""
    print("🛡️ Setting up SentrySense Dashboard...")
    
    # Create directories
    create_directories()
    
    # Create sample data
    create_sample_data()
    
    print("\n✅ Setup complete! You can now run the dashboard with:")
    print("   streamlit run app.py")

if __name__ == "__main__":
    main()
