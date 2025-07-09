# 🛡️ SentrySense Dashboard - Enhanced Version

A comprehensive cybersecurity dashboard for GNN-based anomaly detection and CVE threat intelligence monitoring.

## 🆕 New Features

### Enhanced UI/UX
- **Sidebar Navigation**: Comprehensive control panel with system status
- **Tabbed Interface**: Separate tabs for Anomalies, Threats, and Analytics
- **Dynamic Animations**: Glowing effects, hover animations, and smooth transitions
- **Real-time Charts**: Interactive Plotly visualizations for data analysis

### Advanced Analytics
- **GNN Model Explainability**: Feature importance analysis for anomaly detection
- **Timeline Visualization**: Anomaly detection over time
- **Threat Distribution**: CVE severity breakdown
- **Feature Heatmaps**: Contributing factors to anomaly scores

### Smart Monitoring
- **Location-based Time Analysis**: Timezone-aware anomaly detection
- **CVE Integration**: Real-time threat intelligence from NVD database
- **Auto-refresh**: Configurable refresh intervals with live updates
- **Alert System**: Pop-up notifications for new threats and anomalies

## 🚀 Quick Start

1. **Install Dependencies**:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

2. **Run Dashboard**:
   \`\`\`bash
   streamlit run app.py
   \`\`\`
   Or use the launch script:
   \`\`\`bash
   chmod +x run_dashboard.sh
   ./run_dashboard.sh
   \`\`\`

3. **Run Background Monitoring** (Optional):
   \`\`\`bash
   # Terminal 1: GNN Anomaly Detection
   python simulation_and_detection_/src/stream_inference.py
   
   # Terminal 2: CVE Threat Fetching
   python predictive_ai/fetch_threats.py
   \`\`\`

## 📊 Dashboard Features

### 🔍 Anomaly Detection Tab
- **Real-time GNN Analysis**: Stream-based anomaly detection
- **Model Explainability**: Top contributing features with error analysis
- **Location Intelligence**: Timezone-aware behavioral analysis
- **Timeline Visualization**: Anomaly patterns over time

### 🎯 Threat Intelligence Tab
- **CVE Integration**: Live threat data from National Vulnerability Database
- **Severity Classification**: HIGH/MEDIUM threat filtering
- **Reference Links**: Direct access to vulnerability details
- **Distribution Analysis**: Threat severity breakdown

### 📊 Analytics Dashboard Tab
- **Interactive Charts**: Plotly-powered visualizations
- **Feature Heatmaps**: Anomaly contribution analysis
- **Trend Analysis**: Historical pattern recognition
- **System Metrics**: Real-time performance monitoring

## 🛡️ Security Features

### GNN-Based Detection
- **Graph Neural Network**: Advanced pattern recognition
- **Feature Reconstruction**: Autoencoder-based anomaly scoring
- **Contextual Analysis**: User, IP, and resource correlation
- **Explainable AI**: Feature-level anomaly explanation

### Threat Intelligence
- **CVE Monitoring**: Automated vulnerability tracking
- **Severity Scoring**: CVSS-based risk assessment
- **Real-time Updates**: Live threat feed integration
- **Reference Tracking**: Source verification and links

## 🎨 UI Enhancements

### Visual Design
- **Cybersecurity Theme**: Dark mode with neon accents
- **Animated Elements**: Glowing effects and smooth transitions
- **Responsive Layout**: Mobile-friendly design
- **Interactive Components**: Hover effects and dynamic updates

### User Experience
- **Sidebar Control Panel**: Centralized system management
- **Tabbed Navigation**: Organized content sections
- **Real-time Updates**: Live data refresh with notifications
- **Customizable Refresh**: User-controlled update intervals

## 📁 File Structure

\`\`\`
SentrySense/
├── app.py                              # Enhanced Streamlit dashboard
├── requirements.txt                    # Updated dependencies
├── run_dashboard.sh                   # Launch script
├── simulation_and_detection_/
│   ├── logs/
│   │   └── stream_logs.jsonl         # GNN anomaly results
│   ├── src/
│   │   └── stream_inference.py       # GNN inference engine
│   ├── splits/                       # Training data splits
│   └── models/                       # Trained GNN models
└── predictive_ai/
    ├── threats/                      # CVE text files
    │   └── *.txt                     # Individual threat reports
    └── fetch_threats.py              # CVE fetching script
\`\`\`

## 🔧 Configuration

### Dashboard Settings
- **Auto-refresh**: 15/30/60 second intervals
- **Alert Thresholds**: Customizable anomaly scoring
- **Display Options**: Configurable data views
- **Theme Settings**: Dark mode cybersecurity styling

### Data Sources
- **Anomaly Logs**: `simulation_and_detection_/logs/stream_logs.jsonl`
- **Threat Data**: `predictive_ai/threats/*.txt`
- **Model Files**: `simulation_and_detection_/models/`
- **Training Data**: `simulation_and_detection_/splits/`

## 🚨 Alert System

### Notification Types
- **New Anomaly Detected**: GNN model alerts
- **New Threat Identified**: CVE database updates
- **System Status Changes**: Health monitoring alerts
- **High Severity Warnings**: Critical threat notifications

### Alert Features
- **Pop-up Banners**: Animated alert displays
- **Dismissible Notifications**: User-controlled alerts
- **Severity Indicators**: Color-coded warning levels
- **Real-time Updates**: Live notification system
