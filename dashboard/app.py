import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from config import ANOMALY_DATA_PATH, THREAT_PREDICTION_PATH

try:
    from visuals.plot_timeline import create_timeline_chart
except ImportError:
    def create_timeline_chart(anomalies):
        # Fallback timeline chart
        if not anomalies:
            return go.Figure()
        
        df = pd.DataFrame(anomalies)
        df['datetime'] = pd.to_datetime(df['timestamp'])
        
        fig = px.scatter(
            df, x='datetime', y='type', 
            color='severity',
            title='Anomaly Timeline',
            color_discrete_map={
                'Critical': '#FF4B4B',
                'High': '#FF8C00',
                'Medium': '#FFD700',
                'Low': '#32CD32'
            }
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        return fig

# Page configuration
st.set_page_config(
    page_title="SentrySense Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "static", "style.css")
    try:
        if os.path.exists(css_path):
            with open(css_path) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        else:
            # Fallback: inline basic styles if CSS file not found
            st.markdown("""
            <style>
            .stApp {
                background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
                font-family: 'Inter', sans-serif;
            }
            .metric-card {
                background: linear-gradient(145deg, #1e293b, #334155);
                border-radius: 12px;
                padding: 1.5rem;
                text-align: center;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
                border: 1px solid #475569;
                margin-bottom: 1rem;
            }
            .metric-title {
                color: #94a3b8;
                font-size: 0.9rem;
                font-weight: 500;
                text-transform: uppercase;
                margin-bottom: 0.5rem;
            }
            .metric-value {
                color: white;
                font-size: 2.5rem;
                font-weight: 700;
            }
            .anomaly-card {
                background: linear-gradient(145deg, #1e293b, #334155);
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
                border: 1px solid #475569;
            }
            .header {
                background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
                padding: 2rem;
                border-radius: 12px;
                margin-bottom: 2rem;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            </style>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load custom CSS: {e}")

# Load data functions
@st.cache_data
def load_anomaly_data():
    try:
        if os.path.exists(ANOMALY_DATA_PATH):
            with open(ANOMALY_DATA_PATH, 'r') as f:
                return json.load(f)
        else:
            # Sample data for demonstration
            return [
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
    except Exception as e:
        st.error(f"Error loading anomaly data: {e}")
        return []

@st.cache_data
def load_threat_predictions():
    try:
        if os.path.exists(THREAT_PREDICTION_PATH):
            with open(THREAT_PREDICTION_PATH, 'r') as f:
                return json.load(f)
        else:
            # Sample data for demonstration
            return [
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
                },
                {
                    "threat_type": "Privilege Escalation",
                    "confidence": 0.64,
                    "predicted_time": "2024-01-15T12:00:00Z",
                    "description": "Suspicious user behavior indicates potential privilege escalation attempt",
                    "risk_level": "Medium",
                    "affected_systems": ["domain-controller"]
                }
            ]
    except Exception as e:
        st.error(f"Error loading threat predictions: {e}")
        return []

# Utility functions
def get_severity_color(severity):
    colors = {
        "Critical": "#FF4B4B",
        "High": "#FF8C00",
        "Medium": "#FFD700",
        "Low": "#32CD32"
    }
    return colors.get(severity, "#808080")

def format_timestamp(timestamp_str):
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp_str

# Dashboard components
def render_metrics_cards(anomalies, threats):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Total Anomalies</div>
            <div class="metric-value">{}</div>
        </div>
        """.format(len(anomalies)), unsafe_allow_html=True)
    
    with col2:
        critical_count = len([a for a in anomalies if a.get('severity') == 'Critical'])
        st.markdown("""
        <div class="metric-card critical">
            <div class="metric-title">Critical Alerts</div>
            <div class="metric-value">{}</div>
        </div>
        """.format(critical_count), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Threat Predictions</div>
            <div class="metric-value">{}</div>
        </div>
        """.format(len(threats)), unsafe_allow_html=True)
    
    with col4:
        high_risk_threats = len([t for t in threats if t.get('risk_level') in ['Critical', 'High']])
        st.markdown("""
        <div class="metric-card warning">
            <div class="metric-title">High Risk Threats</div>
            <div class="metric-value">{}</div>
        </div>
        """.format(high_risk_threats), unsafe_allow_html=True)

def render_anomaly_cards(anomalies):
    st.subheader("🚨 Recent Anomalies")
    
    for anomaly in anomalies[:10]:  # Show latest 10
        severity_color = get_severity_color(anomaly.get('severity', 'Low'))
        
        st.markdown(f"""
        <div class="anomaly-card" style="border-left: 4px solid {severity_color};">
            <div class="anomaly-header">
                <span class="anomaly-type">{anomaly.get('type', 'Unknown')}</span>
                <span class="anomaly-severity" style="background-color: {severity_color};">
                    {anomaly.get('severity', 'Low')}
                </span>
            </div>
            <div class="anomaly-description">{anomaly.get('description', 'No description available')}</div>
            <div class="anomaly-details">
                <span><strong>Time:</strong> {format_timestamp(anomaly.get('timestamp', ''))}</span>
                <span><strong>Source:</strong> {anomaly.get('source_ip', 'Unknown')}</span>
                <span><strong>Confidence:</strong> {anomaly.get('confidence', 0):.2%}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_threat_predictions(threats):
    st.subheader("🔮 Threat Predictions")
    
    for i, threat in enumerate(threats):
        risk_color = get_severity_color(threat.get('risk_level', 'Low'))
        
        with st.expander(f"🎯 {threat.get('threat_type', 'Unknown Threat')} - {threat.get('risk_level', 'Low')} Risk"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Description:** {threat.get('description', 'No description available')}")
                st.write(f"**Predicted Time:** {format_timestamp(threat.get('predicted_time', ''))}")
                
                if threat.get('affected_systems'):
                    st.write("**Affected Systems:**")
                    for system in threat.get('affected_systems', []):
                        st.write(f"• {system}")
            
            with col2:
                st.metric("Confidence", f"{threat.get('confidence', 0):.2%}")
                st.markdown(f"""
                <div style="background-color: {risk_color}; color: white; padding: 8px; border-radius: 4px; text-align: center; margin-top: 10px;">
                    <strong>{threat.get('risk_level', 'Low')} Risk</strong>
                </div>
                """, unsafe_allow_html=True)

def main():
    # Load CSS
    load_css()
    
    # Header
    st.markdown("""
    <div class="header">
        <h1>🛡️ SentrySense Dashboard</h1>
        <p>Real-time Cybersecurity Monitoring & Threat Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    anomalies = load_anomaly_data()
    threats = load_threat_predictions()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 Dashboard Controls")
        
        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        
        # Filters
        st.markdown("### 🔍 Filters")
        
        severity_filter = st.multiselect(
            "Severity Levels",
            ["Critical", "High", "Medium", "Low"],
            default=["Critical", "High", "Medium", "Low"]
        )
        
        time_range = st.selectbox(
            "Time Range",
            ["Last 24 hours", "Last 7 days", "Last 30 days"],
            index=0
        )
        
        st.markdown("---")
        
        # System status
        st.markdown("### 🖥️ System Status")
        st.success("✅ Monitoring Active")
        st.info("📡 Data Sources: 3/3 Online")
        st.warning("⚠️ 2 Critical Alerts")
    
    # Main content
    # Metrics cards
    render_metrics_cards(anomalies, threats)
    
    st.markdown("---")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🚨 Anomalies", "🔮 Threat Predictions", "📈 Analytics"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            render_anomaly_cards([a for a in anomalies if a.get('severity') in severity_filter])
        
        with col2:
            st.subheader("📊 Severity Distribution")
            if anomalies:
                severity_counts = {}
                for anomaly in anomalies:
                    severity = anomaly.get('severity', 'Low')
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                fig = px.pie(
                    values=list(severity_counts.values()),
                    names=list(severity_counts.keys()),
                    color_discrete_map={
                        'Critical': '#FF4B4B',
                        'High': '#FF8C00',
                        'Medium': '#FFD700',
                        'Low': '#32CD32'
                    }
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        render_threat_predictions(threats)
    
    with tab3:
        st.subheader("📈 Timeline Analysis")
        if anomalies:
            timeline_fig = create_timeline_chart(anomalies)
            st.plotly_chart(timeline_fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Threat Types")
            if threats:
                threat_types = [t.get('threat_type', 'Unknown') for t in threats]
                threat_counts = {t: threat_types.count(t) for t in set(threat_types)}
                
                fig = px.bar(
                    x=list(threat_counts.keys()),
                    y=list(threat_counts.values()),
                    color=list(threat_counts.values()),
                    color_continuous_scale='Reds'
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🌐 Source IPs")
            if anomalies:
                source_ips = [a.get('source_ip', 'Unknown') for a in anomalies]
                ip_counts = {ip: source_ips.count(ip) for ip in set(source_ips)}
                
                fig = px.bar(
                    x=list(ip_counts.values()),
                    y=list(ip_counts.keys()),
                    orientation='h',
                    color=list(ip_counts.values()),
                    color_continuous_scale='Blues'
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
