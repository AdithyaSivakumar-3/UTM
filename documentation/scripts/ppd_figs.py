"""Figures that exist only for the PPD final presentation.

One so far: the lay-audience DIC explainer. It uses the WHITE specimen (S26), not the black one
every internal Otsu slide uses, because for someone who has never seen DIC the story is simply
"two dark dots on a bright part" - no thresholds, no histograms, no grips. The dots are FOUND by
the same geometry the rig uses (dark, round, big), never eyeballed, so the arrow really does span
the measured pair.
"""
import glob
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                       # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch                # noqa: E402

import cv2                                                            # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.abspath(os.path.join(HERE, "..", "figures"))
RUN = os.path.abspath(os.path.join(
    HERE, "..", "..", "Software", "UTM_PyQt6", "Test data",
    "8.6.20 - Tensile test to Failure", "Specimen_S26_V2_Spray_Video3"))

INK, TAN, SAGE = "#253439", "#B29E84", "#7C898B"
plt.rcParams["font.family"] = "Segoe UI"


def fig_dic_explain():
    hits = sorted(glob.glob(os.path.join(RUN, "*", "frames", "f*.png")))
    g = cv2.imread(hits[len(hits) // 4], cv2.IMREAD_GRAYSCALE)
    if g.shape[0] > g.shape[1]:
        g = np.ascontiguousarray(np.rot90(g))

    # the two dots: dark, round, large, and INSIDE the frame - the rig's own gates, mirrored
    _t, b = cv2.threshold(g, 130, 255, cv2.THRESH_BINARY_INV)
    n, lab, st, cen = cv2.connectedComponentsWithStats(b, 8)
    dots = []
    for i in range(1, n):
        a = int(st[i, cv2.CC_STAT_AREA])
        x, y = int(st[i, cv2.CC_STAT_LEFT]), int(st[i, cv2.CC_STAT_TOP])
        w_, h_ = int(st[i, cv2.CC_STAT_WIDTH]), int(st[i, cv2.CC_STAT_HEIGHT])
        if a < 4000 or x <= 2 or y <= 2 or x + w_ >= g.shape[1] - 2 or y + h_ >= g.shape[0] - 2:
            continue
        if 0.6 <= w_ / max(1, h_) <= 1.7:
            dots.append((cen[i][0], cen[i][1], (w_ + h_) / 4))
    dots.sort()
    assert len(dots) >= 2, "did not find the two dots"
    (x1, y1, r1), (x2, y2, r2) = dots[0], dots[-1]

    fig, ax = plt.subplots(figsize=(11.8, 2.95))
    ax.imshow(g, cmap="gray", vmin=0, vmax=255, aspect="auto", interpolation="bilinear")
    for x, y, r in ((x1, y1, r1), (x2, y2, r2)):
        ax.add_patch(Circle((x, y), r * 1.55, fill=False, ec=TAN, lw=3.0))
    ax.add_patch(FancyArrowPatch((x1 + r1 * 1.8, y1), (x2 - r2 * 1.8, y2),
                                 arrowstyle="<|-|>", mutation_scale=26, color=TAN, lw=3.0))
    ax.annotate("the camera tracks these two dots", xy=(x1, y1 - r1 * 1.6),
                xytext=(x1 + 150, 46), fontsize=15, color=INK, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=INK, lw=1.6))
    ax.text((x1 + x2) / 2, (y1 + y2) / 2 - 46, "distance  L", fontsize=17,
            color=TAN, fontweight="bold", ha="center")
    ax.text((x1 + x2) / 2, g.shape[0] - 26,
            "pull the specimen  →  the dots move apart  →  strain = (L − L₀) / L₀",
            fontsize=15.5, color=INK, ha="center", va="bottom",
            bbox=dict(boxstyle="round,pad=0.45", fc="white", ec=SAGE, lw=1.2, alpha=0.95))
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    fig.tight_layout(pad=0.3)
    fig.savefig(os.path.join(FIGS, "ppd_dic_explain.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  ppd_dic_explain.png   dots %.0f px apart" % abs(x2 - x1))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    fig_dic_explain()
