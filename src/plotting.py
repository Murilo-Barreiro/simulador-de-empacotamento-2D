import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def fig_from_layout(placements_mm: list[tuple[float, float, float, float]], page_w_mm: float, page_h_mm: float, margin_mm: float, title: str):
    """Cria um plot que simula o layout de impressão"""

    fig, ax = plt.subplots(figsize=(8, 8 * (page_h_mm / page_w_mm)))

    for (x, y, w, h) in placements_mm:
        rect = Rectangle((x, y), w, h, edgecolor="blue", facecolor="skyblue", alpha=0.5)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, f"{w:.1f}x{h:.1f}", ha="center", va="center", fontsize=8)

    ax.add_patch(Rectangle((margin_mm, margin_mm),
                           page_w_mm - 2 * margin_mm,
                           page_h_mm - 2 * margin_mm,
                           fill=False, ls="--", ec="red", lw=1, label="Área útil"))

    ax.add_patch(Rectangle((0, 0), page_w_mm, page_h_mm, fill=False, ec="black", lw=1, label="Folha"))

    ax.set_xlim(0, page_w_mm)
    ax.set_ylim(0, page_h_mm)
    ax.set_aspect('equal', adjustable='box')
    ax.invert_yaxis()
    ax.set_title(title)
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    return fig
