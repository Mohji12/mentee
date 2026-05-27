import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Lambda
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas


def create_radar_chart(data_dict):
    labels = list(data_dict.keys())
    scores = list(data_dict.values())
    num_vars = len(labels)

    # Compute angle for each axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    scores += scores[:1]
    angles += angles[:1]

    # Increase figure size here
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))  # Changed from (5, 5) to (8, 8)
    ax.plot(angles, scores, color='blue', linewidth=3)
    ax.fill(angles, scores, color='skyblue', alpha=0.8)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontweight='bold')

    ax.set_ylim(0, 35)
    ax.yaxis.set_tick_params(labelsize=10)
    for label in ax.get_yticklabels():
        label.set_fontsize(15)
        label.set_fontweight('bold')
    plt.tight_layout()

    # Save chart to buffer
    buf = BytesIO()
    plt.savefig(buf, format="PNG")
    plt.close(fig)
    buf.seek(0)
    return buf
