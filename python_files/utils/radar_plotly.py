import plotly.graph_objects as go
import plotly.io as pio
from io import BytesIO
import base64


def create_radar_chart(data_dict):
    """
    Create a radar chart using Plotly instead of matplotlib
    """
    labels = list(data_dict.keys())
    scores = list(data_dict.values())
    
    # Clean up labels for better display
    cleaned_labels = [label.replace('_', ' ') for label in labels]
    
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=cleaned_labels,
        fill='toself',
        fillcolor='rgba(135, 206, 235, 0.6)',  # skyblue with transparency
        line=dict(color='blue', width=3),
        name='Competency Scores'
    ))
    
    # Update layout with single color background
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 35],
                tickfont=dict(size=8, color='black'),
                gridcolor='lightgray',
                linecolor='gray',
                showticklabels=True
            ),
            angularaxis=dict(
                tickfont=dict(size=8, color='black', family='Arial'),
                linecolor='gray',
                rotation=90,  # Start from top
                showticklabels=True
            )
        ),
        showlegend=False,
        width=400,  # Slightly larger to accommodate labels
        height=400,  # Slightly larger to accommodate labels
        margin=dict(l=100, r=100, t=100, b=100),  # Increased margins for label space
        paper_bgcolor='#f8f9fa',  # Light gray single color background
        plot_bgcolor='#f8f9fa'  # Light gray single color plot background
    )
    
    # Convert to image bytes with white background
    img_bytes = pio.to_image(fig, format="png", width=400, height=400, scale=2, engine="kaleido")
    
    # Create BytesIO buffer
    buf = BytesIO(img_bytes)
    buf.seek(0)
    
    return buf


def create_radar_chart_base64(data_dict):
    """
    Alternative function that returns base64 encoded string
    Useful if you want to embed directly in HTML or other formats
    """
    labels = list(data_dict.keys())
    scores = list(data_dict.values())
    
    # Clean up labels for better display
    cleaned_labels = [label.replace('_', ' ') for label in labels]
    
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=cleaned_labels,
        fill='toself',
        fillcolor='rgba(135, 206, 235, 0.6)',
        line=dict(color='blue', width=3),
        name='Competency Scores'
    ))
    
    # Update layout with single color background
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 35],
                tickfont=dict(size=8, color='black'),
                gridcolor='lightgray',
                linecolor='gray',
                showticklabels=True
            ),
            angularaxis=dict(
                tickfont=dict(size=8, color='black', family='Arial'),
                linecolor='gray',
                rotation=90,
                showticklabels=True
            )
        ),
        showlegend=False,
        width=400,  # Slightly larger to accommodate labels
        height=400,  # Slightly larger to accommodate labels
        margin=dict(l=100, r=100, t=100, b=100),  # Increased margins for label space
        paper_bgcolor='#f8f9fa',  # Light gray single color background
        plot_bgcolor='#f8f9fa'  # Light gray single color plot background
    )
    
    # Convert to base64 with white background
    img_bytes = pio.to_image(fig, format="png", width=400, height=400, scale=2, engine="kaleido")
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    
    return img_base64
