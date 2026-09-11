"""One schematic: inside a clip-on extensometer — the lever-and-spring machine, drawn.

Words kept losing this explanation ("the arms splay, a flexure bends..."), so the geometry is
drawn instead: specimen, two knife edges defining L0, arms carrying the motion out to a flexure,
and the four foil gauges bonded to THAT — the strain gauge never touches the part.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                       # noqa: E402
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle    # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.abspath(os.path.join(HERE, "..", "figures"))

INK, SPEC, ARM, FLEX, GAUGE = "#212529", "#B9C4CC", "#5A6570", "#1F6FB4", "#C0392B"


def fig_clipon():
    fig, ax = plt.subplots(figsize=(6.1, 5.4))

    # ---- the specimen: a vertical strip being pulled
    ax.add_patch(Rectangle((0.8, 0.4), 1.1, 9.2, fc=SPEC, ec=INK, lw=1.4))
    for y, dy in ((9.6, 0.75), (0.4, -0.75)):
        ax.add_patch(FancyArrowPatch((1.35, y), (1.35, y + dy), arrowstyle="-|>",
                                     mutation_scale=22, color=INK, lw=2.4))
    ax.text(1.35, 10.55, "pull", ha="center", fontsize=11, color=INK, fontweight="bold")
    ax.text(1.35, -0.6, "specimen", ha="center", fontsize=11, color=INK)

    # ---- two knife edges, the ONLY contact, defining L0
    ky1, ky2 = 7.2, 2.8
    for ky in (ky1, ky2):
        ax.add_patch(Polygon([(1.9, ky), (2.75, ky + 0.33), (2.75, ky - 0.33)],
                             closed=True, fc="#E8590C", ec=INK, lw=1.2))
    ax.annotate("", xy=(1.62, ky1), xytext=(1.62, ky2),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=1.6))
    ax.text(1.38, (ky1 + ky2) / 2, "L₀", fontsize=15, color=INK, fontweight="bold",
            ha="right", va="center")
    ax.text(3.0, ky1 + 0.75, "knife edges — spring-clipped,\nthe only touch", fontsize=9.5,
            color="#E8590C", fontweight="bold")

    # ---- arms carrying the two points out to the body
    ax.add_patch(Polygon([(2.75, ky1 + 0.16), (6.0, ky1 + 0.16), (6.0, ky1 - 0.16),
                          (2.75, ky1 - 0.16)], fc=ARM, ec=INK, lw=1.1))
    ax.add_patch(Polygon([(2.75, ky2 + 0.16), (6.0, ky2 + 0.16), (6.0, ky2 - 0.16),
                          (2.75, ky2 - 0.16)], fc=ARM, ec=INK, lw=1.1))
    ax.text(4.4, (ky1 + ky2) / 2, "arms follow\nthe two points", fontsize=9.5, color=ARM,
            ha="center", fontweight="bold")

    # ---- the flexure joining the arms: a thin S of leaf springs
    xs = 6.35
    yy = np.linspace(ky2, ky1, 120)
    xx = xs + 0.32 * np.sin((yy - ky2) / (ky1 - ky2) * 2 * np.pi)
    ax.plot(xx, yy, color=FLEX, lw=5, solid_capstyle="round")
    ax.plot([6.0, xs], [ky1, ky1], color=FLEX, lw=5)
    ax.plot([6.0, xs], [ky2, ky2], color=FLEX, lw=5)
    ax.text(7.6, (ky1 + ky2) / 2 + 1.15, "FLEXURE — a soft spring:\nΔL becomes bending",
            fontsize=10, color=FLEX, fontweight="bold")

    # ---- four foil gauges bonded to the flexure, bridged
    for i, frac in enumerate((0.18, 0.40, 0.60, 0.82)):
        y = ky2 + frac * (ky1 - ky2)
        x = xs + 0.32 * np.sin(frac * 2 * np.pi)
        ax.add_patch(Rectangle((x - 0.14, y - 0.22), 0.28, 0.44, fc=GAUGE, ec="none"))
    ax.text(7.6, (ky1 + ky2) / 2 - 0.4,
            "4 strain gauges GLUED\nto the flexure —\nnever to the part",
            fontsize=10, color=GAUGE, fontweight="bold")

    # ---- output
    ax.add_patch(FancyArrowPatch((7.0, ky2 - 0.35), (8.3, 1.35), arrowstyle="-|>",
                                 mutation_scale=20, color=INK, lw=1.8,
                                 connectionstyle="arc3,rad=-0.25"))
    ax.text(8.35, 0.9, "bridge voltage ∝ ΔL\nstrain = ΔL / L₀", fontsize=11, color=INK,
            fontweight="bold", ha="center",
            bbox=dict(boxstyle="round,pad=0.4", fc="#E7F1F8", ec="#2E6DA4", lw=1.2))

    ax.set_xlim(0, 10.6)
    ax.set_ylim(-1.1, 11.1)
    ax.axis("off")
    fig.tight_layout(pad=0.2)
    fig.savefig(os.path.join(FIGS, "ext_clipon.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  ext_clipon.png")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    fig_clipon()
