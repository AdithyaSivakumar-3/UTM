# -*- coding: utf-8 -*-
"""Figures made specifically for the project report.

  report_dic_explain.png   the two-marker principle on a real frame, aspect-true
  report_px2strain.png     freeze L0 / measure L on two real frames, aspect-true
  report_cover_thresh.png  the thresholded gauge strip (from otsu_valley_where) for the cover
  report_protocols.png     schematic of the six closed-loop protocols, drawn from the
                           literature descriptions (not from our runs)

The deck versions of the first two use aspect="auto", which stretches the 5.6:1 ROI band to
the axes shape and makes the round markers elliptical; the report versions keep aspect
equal so the specimen looks like the specimen."""
import glob
import os
import sys

import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppd_figs as P                                     # noqa: E402  (RUN, _dots_in, colours)

FIGS = os.path.join(HERE, "..", "figures")
INK, TAN, SAGE = P.INK, P.TAN, P.SAGE
plt.rcParams["font.family"] = "Segoe UI"


def _frame(idx):
    hits = sorted(glob.glob(os.path.join(P.RUN, "*", "frames", "f*.png")))
    k = int(len(hits) * idx) if isinstance(idx, float) else idx
    g = cv2.imread(hits[k], cv2.IMREAD_GRAYSCALE)
    if g.shape[0] > g.shape[1]:
        g = np.ascontiguousarray(np.rot90(g))
    return g


def fig_dic_explain():
    g = _frame(0.25)
    (x1, y1, r1), (x2, y2, r2) = P._dots_in(g)
    h, w = g.shape
    fig, ax = plt.subplots(figsize=(12.0, 12.0 * h / w + 0.9))
    ax.imshow(g, cmap="gray", vmin=0, vmax=255, interpolation="bilinear")
    for x, y, r in ((x1, y1, r1), (x2, y2, r2)):
        ax.add_patch(Circle((x, y), r * 1.55, fill=False, ec=TAN, lw=2.6))
    ax.add_patch(FancyArrowPatch((x1 + r1 * 1.8, y1), (x2 - r2 * 1.8, y2),
                                 arrowstyle="<|-|>", mutation_scale=22, color=TAN, lw=2.6))
    ax.text((x1 + x2) / 2, (y1 + y2) / 2 - 0.16 * h, "distance  L", fontsize=15,
            color=TAN, fontweight="bold", ha="center")
    ax.set_xlim(0, w); ax.set_ylim(h, 0)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    fig.text(0.5, 0.06, "pull the specimen  →  the markers move apart  →  strain = (L − L₀) / L₀",
             fontsize=14, color=INK, ha="center",
             bbox=dict(boxstyle="round,pad=0.45", fc="white", ec=SAGE, lw=1.0))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.22)
    fig.savefig(os.path.join(FIGS, "report_dic_explain.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  report_dic_explain.png")


def fig_px2strain():
    g0, g1 = _frame(0), _frame(0.75)
    (ax1, ay1, _), (bx1, by1, _) = P._dots_in(g0)
    (ax2, ay2, _), (bx2, by2, _) = P._dots_in(g1)
    L0, L = abs(bx1 - ax1), abs(bx2 - ax2)
    eps = (L - L0) / L0
    h, w = g0.shape
    fig, axes = plt.subplots(2, 1, figsize=(12.0, 2 * 12.0 * h / w + 1.1))
    for ax, g, pair, lab, col in (
            (axes[0], g0, ((ax1, ay1), (bx1, by1)), "reference frame — freeze  L₀ = %.0f px" % L0, INK),
            (axes[1], g1, ((ax2, ay2), (bx2, by2)), "later frame — measure  L = %.0f px" % L, "#E8590C")):
        ax.imshow(g, cmap="gray", vmin=0, vmax=255)
        (xa, ya), (xb, yb) = pair
        ax.annotate("", xy=(xb - 40, (ya + yb) / 2), xytext=(xa + 40, (ya + yb) / 2),
                    arrowprops=dict(arrowstyle="<|-|>", color=col, lw=2.4, mutation_scale=20))
        for x, y in pair:
            ax.plot([x], [y], "+", ms=14, mew=2.0, color=col)
        ax.text(30, h - 25, lab, fontsize=12, color=col, fontweight="bold", va="bottom",
                bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=col, lw=1.0, alpha=0.92))
        ax.set_xlim(0, w); ax.set_ylim(h, 0)
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color("#CCCCCC")
    fig.suptitle("strain  =  (L − L₀) / L₀  =  (%.0f − %.0f) / %.0f  =  %.4f  =  %.2f %%"
                 % (L, L0, L0, eps, 100 * eps), fontsize=13, color=INK, y=0.985)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.90, bottom=0.02, hspace=0.06)
    fig.savefig(os.path.join(FIGS, "report_px2strain.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  report_px2strain.png   L0 %.0f  L %.0f  eps %.2f %%" % (L0, L, 100 * eps))


def fig_cover_thresh():
    """Crop the thresholded strip out of otsu_valley_where.png (top panel, no title)."""
    im = np.asarray(Image.open(os.path.join(FIGS, "otsu_valley_where.png")).convert("RGB"))
    nonwhite = (im.min(axis=2) < 235)
    rows = np.where(nonwhite.mean(axis=1) > 0.5)[0]          # the strip is a wide dark band
    top = rows[rows < im.shape[0] * 0.5]
    y0, y1 = top.min(), top.max()
    cols = np.where(nonwhite[y0:y1].mean(axis=0) > 0.5)[0]
    x0, x1 = cols.min(), cols.max()
    crop = Image.fromarray(im[y0:y1 + 1, x0:x1 + 1])
    crop.save(os.path.join(FIGS, "report_cover_thresh.png"))
    print("  report_cover_thresh.png  %dx%d" % crop.size)


def fig_protocols():
    """Six schematic protocols, idealised from their standard descriptions."""
    t = np.linspace(0, 10, 800)
    fig, axs = plt.subplots(2, 3, figsize=(13.5, 7.0))
    C_F, C_E = "#1f6fb2", "#c0392b"

    def two_axes(ax, title):
        ax.set_title(title, fontsize=11.5, color=INK, fontweight="bold")
        ax.set_xlabel("time"); ax.set_xticks([]); ax.set_yticks([])
        ax.set_ylabel("force", color=C_F)
        ax2 = ax.twinx(); ax2.set_yticks([]); ax2.set_ylabel("strain", color=C_E)
        return ax2

    # 1 staircase
    ax = axs[0, 0]; ax2 = two_axes(ax, "Staircase (stepped load hold)")
    F = np.floor(t / 2.5) + 1; F[t >= 10] = 4
    ax.step(t, F, color=C_F, lw=2.2, where="post")
    e = np.zeros_like(t)
    for k in range(4):
        m = (t >= 2.5 * k)
        e[m] += 1.0 + 0.25 * (1 - np.exp(-(t[m] - 2.5 * k) / 1.2))
    ax2.plot(t, e, color=C_E, lw=1.8)
    ax.text(0.3, 4.6, "overshoot and settling\nmeasure the loop; strain\ncreeping in the hold\nmeasures the material",
            fontsize=8.5, color=SAGE, va="top")
    ax.set_ylim(0, 5.2)
    # 2 cyclic
    ax = axs[0, 1]; ax2 = two_axes(ax, "Cyclic loading (sine between two levels)")
    F = 2 + 1 * np.sin(2 * np.pi * t / 2.5 - np.pi / 2)
    ax.plot(t, F, color=C_F, lw=2.2)
    e = 2 + 1 * np.sin(2 * np.pi * t / 2.5 - np.pi / 2 - 0.35) + 0.05 * t
    ax2.plot(t, e, color=C_E, lw=1.8)
    ax.text(0.3, 3.6, "strain lags force: the loop's\narea is the energy dissipated\nper cycle, its slope the\ndynamic stiffness",
            fontsize=8.5, color=SAGE, va="top")
    ax.set_ylim(0.5, 3.8)
    # 3 creep
    ax = axs[0, 2]; ax2 = two_axes(ax, "Creep (constant force)")
    F = np.where(t > 0.3, 3.0, 0.0)
    ax.plot(t, F, color=C_F, lw=2.2)
    tc = np.clip(t - 0.3, 0, None)
    e = 1.0 + 0.9 * (1 - np.exp(-tc / 1.5)) + 0.08 * tc + 0.02 * np.exp((tc - 8.5) * 1.6)
    e[t <= 0.3] = 0
    ax2.plot(t, e, color=C_E, lw=1.8)
    for x, lab in ((1.6, "primary"), (5.0, "secondary"), (9.2, "tertiary")):
        ax2.text(x, 0.25, lab, fontsize=8.5, color=SAGE, ha="center")
    ax2.set_ylim(0, 4.5); ax.set_ylim(0, 5)
    ax.text(0.3, 4.8, "ε(t) = ε₀ + m·tⁿ  (Findley)", fontsize=9, color=SAGE, va="top")
    # 4 relaxation
    ax = axs[1, 0]; ax2 = two_axes(ax, "Stress relaxation (constant strain)")
    e = np.where(t > 0.3, 2.0, 0.0)
    ax2.plot(t, e, color=C_E, lw=1.8)
    F = np.where(t > 0.3, 1.2 + 1.8 * np.exp(-(np.clip(t - 0.3, 0, None) / 3.0) ** 0.6), 0.0)
    ax.plot(t, F, color=C_F, lw=2.2)
    ax.set_ylim(0, 3.6); ax2.set_ylim(0, 2.8)
    ax.text(3.0, 3.3, "strain held by the loop, force\ndecays: σ(t)/σ₀ = E(t)/E₀,\nthe relaxation modulus",
            fontsize=8.5, color=SAGE, va="top")
    # 5 progressive cyclic
    ax = axs[1, 1]; ax2 = two_axes(ax, "Progressive cyclic (rising amplitude)")
    amp = 0.4 + 0.28 * np.floor(t / 2.0)
    F = amp * (1 - np.cos(2 * np.pi * (t % 2.0) / 2.0)) / 2 * 2
    ax.plot(t, F, color=C_F, lw=2.2)
    perm = 0.06 * np.floor(t / 2.0) ** 1.6
    e = perm + F * (0.9 + 0.03 * np.floor(t / 2.0))
    ax2.plot(t, e, color=C_E, lw=1.8)
    ax2.plot(t, perm, color=C_E, lw=1.0, ls="--")
    ax.set_ylim(0, 4.2)
    ax.text(0.3, 4.0, "each unload separates recoverable\nfrom permanent strain (dashed)",
            fontsize=8.5, color=SAGE, va="top")
    # 6 staircase to fracture
    ax = axs[1, 2]; ax2 = two_axes(ax, "Staircase to fracture")
    F = np.floor(t / 1.6) * 0.8 + 0.8; F[t > 8.6] = 0
    ax.step(t, F, color=C_F, lw=2.2, where="post")
    e = np.zeros_like(t)
    for k in range(6):
        m = (t >= 1.6 * k)
        e[m] += 0.6 * (1 + 0.15 * k) + 0.2 * (1 + 0.3 * k) * (1 - np.exp(-(t[m] - 1.6 * k) / 0.8))
    e[t > 8.6] = np.nan
    ax2.plot(t, e, color=C_E, lw=1.8)
    ax.axvline(8.6, color=SAGE, ls=":", lw=1.2)
    ax.text(8.5, 4.9, "fracture", fontsize=9, color=SAGE, ha="right", va="top")
    ax.text(0.3, 4.9, "a modulus at each step;\nstrength under near-static load",
            fontsize=8.5, color=SAGE, va="top")
    ax.set_ylim(0, 5.2)
    fig.suptitle("The six closed-loop protocols — schematic force (blue) and strain (red) histories, "
                 "idealised from their standard descriptions", fontsize=12, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(os.path.join(FIGS, "report_protocols.png"), dpi=180, facecolor="white")
    plt.close(fig)
    print("  report_protocols.png")


if __name__ == "__main__":
    fig_dic_explain()
    fig_px2strain()
    fig_cover_thresh()
    fig_protocols()
