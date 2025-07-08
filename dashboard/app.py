import streamlit as st
import json
import time
import os
import glob
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title="SentrySense Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced dark theme and animations
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #ffffff !important;
        font-size: 3.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-shadow: 0 4px 8px rgba(0,0,0,0.5);
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 20px #00ff88, 0 0 30px #00ff88; }
        to { text-shadow: 0 0 30px #00ff88, 0 0 40px #00ff88; }
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #00ff88;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 255, 136, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 255, 136, 0.2);
    }
    
    .anomaly-card {
        background: linear-gradient(135deg, #2d1b1b 0%, #3d2b2b 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #ff4444;
        margin: 1rem 0;
        box-shadow: 0 6px 20px rgba(255, 68, 68, 0.2);
        transition: all 0.3s ease;
    }
    
    .anomaly-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 25px rgba(255, 68, 68, 0.3);
    }
    
    .threat-card {
        background: linear-gradient(135deg, #1b1b2d 0%, #2b2b3d 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #444;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    
    .threat-card:hover {
        transform: scale(1.02);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.6);
    }
    
    .badge-high {
        background: linear-gradient(45deg, #ff4444, #ff6666);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(255, 68, 68, 0.3);
    }
    
    .badge-medium {
        background: linear-gradient(45deg, #ff8800, #ffaa00);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(255, 136, 0, 0.3);
    }
    
    .badge-low {
        background: linear-gradient(45deg, #00aa44, #00cc55);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0, 170, 68, 0.3);
    }
    
    .alert-banner {
        background: linear-gradient(90deg, #ff4444, #ff6666, #ff4444);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
        animation: pulse-alert 2s infinite, slide-in 0.5s ease-out;
        box-shadow: 0 8px 25px rgba(255, 68, 68, 0.4);
    }
    
    @keyframes pulse-alert {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(1.02); }
    }
    
    @keyframes slide-in {
        from { transform: translateY(-100px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 10px;
        animation: pulse 2s infinite;
    }
    
    .status-active {
        background-color: #00ff88;
        box-shadow: 0 0 15px #00ff88;
    }
    
    .status-warning {
        background-color: #ff8800;
        box-shadow: 0 0 15px #ff8800;
    }
    
    .status-critical {
        background-color: #ff4444;
        box-shadow: 0 0 15px #ff4444;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%);
    }
    
    .feature-card {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #00ff88;
        margin: 0.5rem 0;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        background: linear-gradient(135deg, #2d2d2d 0%, #3d3d3d 100%);
        transform: translateY(-2px);
    }
    
    .explainability-card {
        background: linear-gradient(135deg, #2d2d1b 0%, #3d3d2b 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffaa00;
        margin: 0.5rem 0;
    }

    .element-container:empty {
        display: none !important;
    }

    .stPlotlyChart:empty {
        display: none !important;
    }

    div[data-testid="column"]:empty {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'last_anomaly_count' not in st.session_state:
    st.session_state.last_anomaly_count = 0
if 'last_threat_count' not in st.session_state:
    st.session_state.last_threat_count = 0
if 'show_alert' not in st.session_state:
    st.session_state.show_alert = False
if 'alert_message' not in st.session_state:
    st.session_state.alert_message = ""
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True

def get_badge_html(level):
    """Generate HTML for severity badges"""
    if isinstance(level, bool):
        level = "high" if level else "normal"
    
    level_lower = str(level).lower()
    if level_lower in ['high', 'critical', 'true']:
        return f'<span class="badge-high">HIGH</span>'
    elif level_lower in ['medium', 'moderate']:
        return f'<span class="badge-medium">MEDIUM</span>'
    elif level_lower in ['low', 'low_level']:
        return f'<span class="badge-low">LOW</span>'
    else:
        return f'<span class="badge-low">NORMAL</span>'

def load_anomaly_data():
    """Load anomaly data from stream_logs.jsonl based on actual format"""
    try:
        log_file = Path("simulation_and_detection_/logs/stream_logs.jsonl")
        if not log_file.exists():
            # Create sample data matching the actual format
            sample_data = [
                {
                    "stream_index": 3147,
                    "raw_features": {"masked_user": 1, "source_ip": 2, "location": 0},
                    "anomaly": "low_level",
                    "reason": "Unknown value(s) for: masked_user, source_ip",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "stream_index": 3148,
                    "raw_features": {"masked_user": -1, "source_ip": 3, "location": 1},
                    "anomaly": "medium",
                    "reason": "Local time in Tokyo is 2:00 — time is not good (12am-4am)",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "stream_index": 3149,
                    "raw_features": {"masked_user": 2, "source_ip": 1, "location": 2},
                    "anomaly": True,
                    "score": 25000000.5,
                    "why": [
                        {"feature": "source_ip", "original": 1.0, "reconstructed": 0.2, "abs_error": 0.8},
                        {"feature": "masked_user", "original": 2.0, "reconstructed": 1.1, "abs_error": 0.9},
                        {"feature": "location", "original": 2.0, "reconstructed": 1.8, "abs_error": 0.2}
                    ],
                    "timestamp": datetime.now().isoformat()
                }
            ]
            return sample_data
        
        anomalies = []
        with open(log_file, 'r') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line.strip())
                    # Add timestamp if not present
                    if 'timestamp' not in data:
                        data['timestamp'] = datetime.now().isoformat()
                    anomalies.append(data)
        
        return anomalies[-10:] if len(anomalies) >= 10 else anomalies
    except Exception as e:
        st.error(f"Error loading anomaly data: {e}")
        return []

def load_threat_data():
    """Load threat data from CVE text files in threats folder"""
    try:
        threats_dir = Path("predictive_ai/threats")
        if not threats_dir.exists():
            # Create sample data
            return [
                {
                    "cve_id": "CVE-2024-0001",
                    "published_date": "2024-01-08",
                    "description": "Critical buffer overflow vulnerability in network service allowing remote code execution",
                    "severity": "HIGH",
                    "score": "9.8",
                    "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-0001"]
                },
                {
                    "cve_id": "CVE-2024-0002", 
                    "published_date": "2024-01-07",
                    "description": "SQL injection vulnerability in web application allowing unauthorized data access",
                    "severity": "MEDIUM",
                    "score": "6.5",
                    "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-0002"]
                }
            ]
        
        threats = []
        for txt_file in threats_dir.glob("*.txt"):
            try:
                with open(txt_file, 'r') as f:
                    content = f.read()
                    
                threat = {"cve_id": txt_file.stem}
                lines = content.split('\n')
                
                for line in lines:
                    if line.startswith("Published Date:"):
                        threat["published_date"] = line.split(":", 1)[1].strip()
                    elif line.startswith("Description:"):
                        threat["description"] = line.split(":", 1)[1].strip()
                    elif line.startswith("Severity:"):
                        severity_part = line.split(":", 1)[1].strip()
                        if "(" in severity_part:
                            threat["severity"] = severity_part.split("(")[0].strip()
                            score_part = severity_part.split("Score: ")[1].replace(")", "") if "Score: " in severity_part else "Unknown"
                            threat["score"] = score_part
                        else:
                            threat["severity"] = severity_part
                            threat["score"] = "Unknown"
                
                # Extract references
                threat["references"] = []
                in_references = False
                for line in lines:
                    if line.startswith("References:"):
                        in_references = True
                    elif in_references and line.startswith(" - "):
                        threat["references"].append(line.strip("- ").strip())
                
                threats.append(threat)
            except Exception as e:
                st.warning(f"Error reading {txt_file}: {e}")
        
        return threats
    except Exception as e:
        st.error(f"Error loading threat data: {e}")
        return []

def create_anomaly_timeline(anomalies):
    """Create timeline chart for anomalies"""
    if not anomalies:
        return None
    
    df = pd.DataFrame(anomalies)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Create severity mapping
    severity_map = {'low_level': 1, 'medium': 2, 'high': 3, True: 3, False: 0}
    df['severity_num'] = df['anomaly'].map(lambda x: severity_map.get(x, 1))
    
    fig = px.scatter(df, x='timestamp', y='severity_num', 
                     color='severity_num',
                     color_continuous_scale=['green', 'orange', 'red'],
                     title="Anomaly Detection Timeline",
                     labels={'severity_num': 'Severity Level', 'timestamp': 'Time'})
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_color='#00ff88'
    )
    
    return fig

def create_threat_distribution(threats):
    """Create threat severity distribution chart"""
    if not threats:
        return None
    
    severity_counts = {}
    for threat in threats:
        severity = threat.get('severity', 'Unknown')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    colors = {'HIGH': '#ff4444', 'MEDIUM': '#ff8800', 'LOW': '#00aa44', 'Unknown': '#666666'}
    
    fig = go.Figure(data=[
        go.Bar(x=list(severity_counts.keys()), 
               y=list(severity_counts.values()),
               marker_color=[colors.get(k, '#666666') for k in severity_counts.keys()])
    ])
    
    fig.update_layout(
        title="Threat Severity Distribution",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_color='#00ff88'
    )
    
    return fig

def display_anomaly_explainability(anomaly):
    """Display GNN model explainability for anomalies"""
    if 'why' in anomaly and anomaly['why']:
        st.markdown("#### 🔍 Model Explainability")
        st.markdown("**Top contributing features to anomaly score:**")
        
        for i, feature in enumerate(anomaly['why'][:3], 1):
            with st.container():
                st.markdown(f"""
                <div class="explainability-card">
                    <strong>{i}. {feature['feature']}</strong><br>
                    Original: {feature['original']:.4f} | 
                    Reconstructed: {feature['reconstructed']:.4f} | 
                    <strong>Error: {feature['abs_error']:.4f}</strong>
                </div>
                """, unsafe_allow_html=True)

def check_for_new_data(anomalies, threats):
    """Check for new data and trigger alerts"""
    current_anomaly_count = len(anomalies)
    current_threat_count = len(threats)
    
    if current_anomaly_count > st.session_state.last_anomaly_count:
        st.session_state.show_alert = True
        st.session_state.alert_message = "⚠️ New Anomaly Detected!"
    elif current_threat_count > st.session_state.last_threat_count:
        st.session_state.show_alert = True
        st.session_state.alert_message = "🚨 New Threat Identified!"
    
    st.session_state.last_anomaly_count = current_anomaly_count
    st.session_state.last_threat_count = current_threat_count

def main():
    # Sidebar
    with st.sidebar:
        st.markdown("## 🛡️ SentrySense Control Panel")
        
        # System Status
        st.markdown("### 📊 System Status")
        
        # Auto-refresh controls
        st.session_state.auto_refresh = st.checkbox("🔄 Auto Refresh", value=st.session_state.auto_refresh)
        refresh_interval = st.selectbox("Refresh Interval", [15, 30, 60], index=0)
        
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.rerun()
        
        st.markdown("---")
        
        # Quick Stats
        anomalies = load_anomaly_data()
        threats = load_threat_data()
        
        st.markdown("### 📈 Quick Stats")
        st.metric("Active Anomalies", len(anomalies))
        st.metric("Threat Alerts", len(threats))
        
        high_severity_threats = sum(1 for t in threats if t.get('severity') == 'HIGH')
        st.metric("High Severity", high_severity_threats, delta=high_severity_threats if high_severity_threats > 0 else None)
        
        st.markdown("---")
        
        # System Health
        st.markdown("### 🏥 System Health")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<span class="status-indicator status-active"></span>**GNN Model**', unsafe_allow_html=True)
        with col2:
            st.markdown("🟢 Active")
            
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<span class="status-indicator status-active"></span>**CVE Monitor**', unsafe_allow_html=True)
        with col2:
            st.markdown("🟢 Active")
        
        if high_severity_threats > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<span class="status-indicator status-critical"></span>**Threat Level**', unsafe_allow_html=True)
            with col2:
                st.markdown("🔴 High")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<span class="status-indicator status-active"></span>**Threat Level**', unsafe_allow_html=True)
            with col2:
                st.markdown("🟢 Normal")

    # Main content
    st.markdown('<h1 class="main-header">SentrySense Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    anomalies = load_anomaly_data()
    threats = load_threat_data()
    
    # Check for new data and show alerts
    check_for_new_data(anomalies, threats)
    
    # Show alert banner if needed
    if st.session_state.show_alert:
        st.markdown(f'<div class="alert-banner">{st.session_state.alert_message}</div>', 
                   unsafe_allow_html=True)
        if st.button("✕ Dismiss Alert"):
            st.session_state.show_alert = False
            st.rerun()
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        anomaly_count = len(anomalies)
        high_anomalies = len([a for a in anomalies if a.get('anomaly') in [True, 'high', 'medium']])
        st.metric(
            label="🔍 Total Anomalies", 
            value=anomaly_count, 
            delta=f"+{high_anomalies}" if high_anomalies > 0 else None
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        threat_count = len(threats)
        high_severity_threats = sum(1 for t in threats if t.get('severity') == 'HIGH')
        st.metric(
            label="🎯 CVE Threats", 
            value=threat_count, 
            delta=f"+{high_severity_threats} High" if high_severity_threats > 0 else None
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        last_update = datetime.now().strftime("%H:%M:%S")
        st.metric(
            label="⏰ Last Update", 
            value=last_update, 
            delta="Live"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        if high_severity_threats > 2:
            system_status = "Critical"
            status_delta = "🔴"
        elif high_severity_threats > 0:
            system_status = "Warning" 
            status_delta = "🟡"
        else:
            system_status = "Normal"
            status_delta = "🟢"
        
        st.metric(
            label="🛡️ Security Status", 
            value=system_status,
            delta=status_delta
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["🔍 Anomaly Detection", "🎯 Threat Intelligence", "📊 Analytics Dashboard"])
    
    with tab1:
        st.markdown("## 🔍 GNN-Based Anomaly Detection")
        
        if not anomalies:
            st.info("No anomalies detected recently. System is running normally.")
        else:
            # Timeline chart
            timeline_fig = create_anomaly_timeline(anomalies)
            if timeline_fig:
                st.plotly_chart(timeline_fig, use_container_width=True)
            
            st.markdown("### Recent Anomaly Events")
            
            for anomaly in reversed(anomalies[-5:]):  # Show last 5
                with st.container():
                    st.markdown('<div class="anomaly-card">', unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col1:
                        st.markdown(f"**Stream #{anomaly.get('stream_index', 'N/A')}**")
                        timestamp = anomaly.get('timestamp', datetime.now().isoformat())
                        st.markdown(f"*{timestamp[:19].replace('T', ' ')}*")
                    
                    with col2:
                        if 'reason' in anomaly:
                            st.markdown(f"**Reason:** {anomaly['reason']}")
                        elif 'score' in anomaly:
                            st.markdown(f"**Anomaly Score:** {anomaly['score']:,.2f}")
                        
                        # Show raw features if available
                        if 'raw_features' in anomaly:
                            with st.expander("🔧 Raw Features"):
                                st.json(anomaly['raw_features'])
                    
                    with col3:
                        st.markdown(get_badge_html(anomaly.get('anomaly', 'unknown')), unsafe_allow_html=True)
                    
                    # Show explainability if available
                    if 'why' in anomaly:
                        display_anomaly_explainability(anomaly)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("")
    
    with tab2:
        st.markdown("## 🎯 CVE Threat Intelligence")
        
        if not threats:
            st.info("No high/medium severity threats detected currently.")
        else:
            # Threat distribution chart
            dist_fig = create_threat_distribution(threats)
            if dist_fig:
                st.plotly_chart(dist_fig, use_container_width=True)
            
            st.markdown("### Active Threat Alerts")
            
            for threat in threats:
                with st.container():
                    st.markdown('<div class="threat-card">', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"### {threat.get('cve_id', 'Unknown CVE')}")
                        st.markdown(f"**Published:** {threat.get('published_date', 'Unknown')}")
                        
                        if 'score' in threat and threat['score'] != 'Unknown':
                            st.markdown(f"**CVSS Score:** {threat['score']}")
                    
                    with col2:
                        severity = threat.get('severity', 'Unknown')
                        st.markdown(get_badge_html(severity), unsafe_allow_html=True)
                    
                    # Description
                    with st.expander("📋 Description"):
                        st.markdown(threat.get('description', 'No description available.'))
                    
                    # References
                    if threat.get('references'):
                        with st.expander("🔗 References"):
                            for ref in threat['references']:
                                st.markdown(f"- [{ref}]({ref})")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("")
    
    with tab3:
        st.markdown("## 📊 Security Analytics Dashboard")
        
        # Only show charts if we have data
        has_anomaly_data = anomalies and len(anomalies) > 0
        has_threat_data = threats and len(threats) > 0
        
        if has_anomaly_data or has_threat_data:
            col1, col2 = st.columns(2)
            
            with col1:
                if has_anomaly_data:
                    timeline_fig = create_anomaly_timeline(anomalies)
                    if timeline_fig:
                        st.plotly_chart(timeline_fig, use_container_width=True)
                else:
                    st.markdown("### 📈 Anomaly Timeline")
                    st.info("No anomaly data available. Run the GNN inference script to generate data.")
            
            with col2:
                if has_threat_data:
                    dist_fig = create_threat_distribution(threats)
                    if dist_fig:
                        st.plotly_chart(dist_fig, use_container_width=True)
                else:
                    st.markdown("### 🎯 Threat Distribution")
                    st.info("No threat data available. Run the CVE fetching script to generate data.")
            
            # Feature importance heatmap for recent anomalies
            if anomalies and any('why' in a for a in anomalies):
                st.markdown("### 🔥 Feature Importance Analysis")
                
                feature_data = []
                for anomaly in anomalies:
                    if 'why' in anomaly:
                        for feature in anomaly['why']:
                            feature_data.append({
                                'stream_index': anomaly.get('stream_index', 0),
                                'feature': feature['feature'],
                                'abs_error': feature['abs_error']
                            })
                
                if feature_data:
                    df_features = pd.DataFrame(feature_data)
                    pivot_df = df_features.pivot(index='feature', columns='stream_index', values='abs_error')
                    
                    fig = px.imshow(pivot_df, 
                                   color_continuous_scale='Reds',
                                   title="Feature Contribution to Anomaly Detection")
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        title_font_color='#667eea'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("### 🚀 Getting Started")
            st.info("No data available yet. Please run the background scripts to start monitoring:")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                **🔍 Start Anomaly Detection:**
                \`\`\`bash
                python simulation_and_detection_/src/stream_inference.py
                \`\`\`
                """)
            
            with col2:
                st.markdown("""
                **🎯 Start Threat Monitoring:**
                \`\`\`bash
                python predictive_ai/fetch_threats.py
                \`\`\`
                """)
    
    # Auto-refresh logic
    if st.session_state.auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()
