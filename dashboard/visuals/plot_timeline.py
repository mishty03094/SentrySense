"""
Timeline visualization for SentrySense Dashboard
Creates interactive timeline charts using Plotly
"""

import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

def create_timeline_chart(anomalies):
    """
    Create an interactive timeline chart showing anomalies over time
    
    Args:
        anomalies (list): List of anomaly dictionaries
    
    Returns:
        plotly.graph_objects.Figure: Timeline chart
    """
    if not anomalies:
        # Return empty chart if no data
        fig = go.Figure()
        fig.add_annotation(
            text="No anomaly data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(anomalies)
    
    # Convert timestamp to datetime
    df['datetime'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('datetime')
    
    # Create color mapping for severity
    color_map = {
        'Critical': '#FF4B4B',
        'High': '#FF8C00',
        'Medium': '#FFD700',
        'Low': '#32CD32'
    }
    
    df['color'] = df['severity'].map(color_map)
    
    # Create the timeline chart
    fig = go.Figure()
    
    # Add scatter plot for anomalies
    for severity in df['severity'].unique():
        severity_data = df[df['severity'] == severity]
        
        fig.add_trace(go.Scatter(
            x=severity_data['datetime'],
            y=severity_data['type'],
            mode='markers',
            marker=dict(
                size=12,
                color=color_map.get(severity, '#808080'),
                symbol='circle',
                line=dict(width=2, color='white')
            ),
            name=f'{severity} ({len(severity_data)})',
            text=severity_data['description'],
            hovertemplate='<b>%{y}</b><br>' +
                         'Time: %{x}<br>' +
                         'Severity: ' + severity + '<br>' +
                         'Description: %{text}<br>' +
                         '<extra></extra>'
        ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': '🕒 Anomaly Timeline',
            'x': 0.5,
            'font': {'size': 20, 'color': 'white'}
        },
        xaxis_title='Time',
        yaxis_title='Anomaly Type',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=400
    )
    
    # Update axes
    fig.update_xaxes(
        gridcolor='#333333',
        linecolor='#666666'
    )
    fig.update_yaxes(
        gridcolor='#333333',
        linecolor='#666666'
    )
    
    return fig

def create_severity_timeline(anomalies, time_window='24h'):
    """
    Create a timeline showing severity levels over time
    
    Args:
        anomalies (list): List of anomaly dictionaries
        time_window (str): Time window for aggregation ('1h', '24h', '7d')
    
    Returns:
        plotly.graph_objects.Figure: Severity timeline chart
    """
    if not anomalies:
        return go.Figure()
    
    df = pd.DataFrame(anomalies)
    df['datetime'] = pd.to_datetime(df['timestamp'])
    
    # Set time grouping based on window
    if time_window == '1h':
        df['time_group'] = df['datetime'].dt.floor('H')
    elif time_window == '24h':
        df['time_group'] = df['datetime'].dt.floor('D')
    else:  # 7d
        df['time_group'] = df['datetime'].dt.floor('D')
    
    # Count anomalies by severity and time
    severity_counts = df.groupby(['time_group', 'severity']).size().unstack(fill_value=0)
    
    fig = go.Figure()
    
    colors = {
        'Critical': '#FF4B4B',
        'High': '#FF8C00',
        'Medium': '#FFD700',
        'Low': '#32CD32'
    }
    
    for severity in ['Critical', 'High', 'Medium', 'Low']:
        if severity in severity_counts.columns:
            fig.add_trace(go.Scatter(
                x=severity_counts.index,
                y=severity_counts[severity],
                mode='lines+markers',
                name=severity,
                line=dict(color=colors[severity], width=3),
                marker=dict(size=8)
            ))
    
    fig.update_layout(
        title='📊 Severity Trends Over Time',
        xaxis_title='Time',
        yaxis_title='Number of Anomalies',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=300
    )
    
    fig.update_xaxes(gridcolor='#333333', linecolor='#666666')
    fig.update_yaxes(gridcolor='#333333', linecolor='#666666')
    
    return fig

def create_threat_confidence_chart(threats):
    """
    Create a chart showing threat predictions by confidence level
    
    Args:
        threats (list): List of threat prediction dictionaries
    
    Returns:
        plotly.graph_objects.Figure: Confidence chart
    """
    if not threats:
        return go.Figure()
    
    df = pd.DataFrame(threats)
    
    # Create confidence bins
    df['confidence_bin'] = pd.cut(
        df['confidence'], 
        bins=[0, 0.5, 0.7, 0.85, 1.0],
        labels=['Low (0-50%)', 'Medium (50-70%)', 'High (70-85%)', 'Very High (85%+)']
    )
    
    confidence_counts = df['confidence_bin'].value_counts()
    
    fig = px.bar(
        x=confidence_counts.index,
        y=confidence_counts.values,
        color=confidence_counts.values,
        color_continuous_scale='Reds',
        title='🎯 Threat Prediction Confidence Distribution'
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False,
        height=300
    )
    
    fig.update_xaxes(gridcolor='#333333', linecolor='#666666')
    fig.update_yaxes(gridcolor='#333333', linecolor='#666666')
    
    return fig
