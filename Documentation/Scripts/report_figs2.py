# -*- coding: utf-8 -*-
"""Second batch of report-only figures.

  report_rig_schematic.png  the rig as it stands in September 2026: frame, drive, load cell,
                            grips, specimen with markers, camera on its mount, LED strip,
                            matte backdrop, electronics box, PC — drawn, labelled
  report_travel.png         aspect-true replacement for cam_travel.png: the pixel budget on
                            a real S26 tare frame plus the frame-edge bar chart
  report_tracking_strip.png the Px0 tracking image for the cover: the tare frame with the
                            two tracked markers and the frozen L0
"""
import os
import sys

import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Polygon

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppd_figs as P                                     # noqa: E402

FIGS = os.path.join(HERE, "..", "figures")
INK, TAN, SAGE = "#253439", "#B29E84", "#7C898B"
BLUE, ORANGE, GREEN, GREY = "#1f6fb2", "#e8590c", "#1e8449", "#9aa3aa"
plt.rcParams["font.family"] = "Segoe UI"


# ------------------------------------------------------------------ 1. the rig schematic
def fig_schematic():
    fig, ax = plt.subplots(figsize=(11.0, 7.0))
    ax.set_xlim(-4.6, 15.4); ax.set_ylim(-1.3, 10.7); ax.set_aspect("equal"); ax.axis("off")

    def box(x, y, w, h, fc="#e9ecef", ec=INK, lw=1.3, z=2, r=0.0):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=%.2f" % r,
                                    fc=fc, ec=ec, lw=lw, zorder=z))

    def lab(x, y, text, tx, ty, ha="left", col=INK, fs=9.2, z=6):
        ax.annotate(text, xy=(x, y), xytext=(tx, ty), fontsize=fs, color=col, ha=ha, va="center",
                    arrowprops=dict(arrowstyle="-", color=GREY, lw=0.9, shrinkA=0, shrinkB=2), zorder=z)

    # backdrop / enclosure (behind everything)
    ax.add_patch(Rectangle((0.9, 0.55), 8.2, 8.9, fc="#f6f3ee", ec="none", zorder=0))
    box(3.05, 1.35, 3.9, 4.15, fc="#c9c4bd", ec="#a49d94", lw=1.0, z=1)             # matte MDF backdrop
    # base, feet and pedestal
    box(0.6, 0.0, 8.8, 0.55, fc="#d5d9dd", z=2)
    for x in (0.6, 8.9):
        box(x, -0.45, 0.5, 0.45, fc="#b9bfc5", z=2)
    box(4.55, 0.55, 0.9, 0.85, fc="#cfd4d8", z=3)                                   # lower load holder
    # lead screws and their nuts
    for x in (2.0, 8.0):
        ax.plot([x, x], [0.55, 8.9], color="#5c6670", lw=5, solid_capstyle="butt", zorder=2)
        ax.plot([x, x], [0.55, 8.9], color="#9aa3aa", lw=1.2, ls=(0, (1, 1.2)), zorder=3)
        box(x - 0.55, 0.55, 1.1, 0.9, fc="#8d949b", z=3, r=0.08)                     # stepper + gearbox
        box(x - 0.5, 5.4, 1.0, 0.75, fc="#7f8790", z=4, r=0.06)                     # lead-screw nuts
        box(x - 0.42, 8.55, 0.84, 0.55, fc="#8d949b", z=4, r=0.06)                  # top bearings
    # members
    box(1.3, 8.9, 7.4, 0.55, fc="#adb5bd", z=4)                                     # top member
    box(1.3, 5.45, 7.4, 0.62, fc="#adb5bd", z=4)                                    # central member (crosshead)
    # load cell + adapter + upper grip
    box(4.6, 4.75, 0.8, 0.7, fc="#f0d9a8", ec="#a9832f", z=5, r=0.08)              # S-beam load cell
    box(4.75, 4.45, 0.5, 0.3, fc="#cfd4d8", z=5)
    box(4.35, 3.75, 1.3, 0.7, fc="#f5f5f5", ec=INK, z=5, r=0.1)                     # upper grip (printed)
    box(4.35, 1.4, 1.3, 0.7, fc="#f5f5f5", ec=INK, z=5, r=0.1)                      # lower grip
    # specimen with two markers
    ax.add_patch(Polygon([(4.65, 1.5), (5.35, 1.5), (5.35, 2.05), (5.18, 2.3), (5.18, 3.55), (5.35, 3.8),
                          (5.35, 4.35), (4.65, 4.35), (4.65, 3.8), (4.82, 3.55), (4.82, 2.3), (4.65, 2.05)],
                         closed=True, fc="white", ec=INK, lw=1.1, zorder=6))
    for y in (2.55, 3.30):
        ax.add_patch(Circle((5.0, y), 0.11, fc=INK, ec="none", zorder=7))
    # LED strip (above the field of view, inside the enclosure)
    box(3.2, 5.05, 3.6, 0.16, fc="#fff1b8", ec="#c9a227", z=6)
    for x in np.linspace(3.45, 6.55, 9):
        ax.plot([x], [5.13], marker="o", ms=3, color="#e0b400", zorder=7)
    # camera on its mount
    box(11.0, 2.55, 1.35, 1.05, fc="#3d434a", ec=INK, z=6, r=0.1)                   # camera body
    box(10.1, 2.78, 0.9, 0.6, fc="#2b2f34", ec=INK, z=6, r=0.05)                    # lens
    ax.add_patch(Polygon([(10.1, 2.7), (5.7, 2.05), (5.7, 3.8), (10.1, 3.45)], closed=True,
                         fc=BLUE, ec="none", alpha=0.08, zorder=1))                  # field of view
    ax.plot([10.1, 5.7], [3.08, 2.93], color=BLUE, lw=0.8, ls="--", zorder=1)
    box(11.45, 0.55, 0.45, 2.0, fc="#8d949b", z=5)                                  # mount post
    box(10.9, 2.35, 1.55, 0.2, fc="#6c757d", z=6)                                   # mount plate
    box(10.6, 0.0, 2.2, 0.55, fc="#d5d9dd", z=2)                                    # camera base plate
    # E-stops
    ax.add_patch(Circle((0.25, 7.6), 0.26, fc="#c0392b", ec=INK, lw=1.0, zorder=6))
    box(-0.05, 7.05, 0.6, 0.3, fc="#f1c40f", ec=INK, z=5)
    # electronics box
    box(-4.3, 3.7, 2.6, 2.3, fc="#eef2f5", ec=INK, z=5, r=0.1)
    ax.text(-3.0, 5.62, "Electronics box", ha="center", fontsize=9.2, color=INK, fontweight="bold", zorder=7)
    for i, t in enumerate(("ESP32 (STEP/DIR)", "2 × TMC stepper drivers", "load-cell amplifier", "24 V supply")):
        ax.text(-3.0, 5.2 - 0.36 * i, t, ha="center", fontsize=8, color=INK, zorder=7)
    # PC
    box(-4.3, 0.55, 2.6, 2.1, fc="#eef2f5", ec=INK, z=5, r=0.1)
    ax.text(-3.0, 2.3, "PC · PyQt6 app", ha="center", fontsize=9.2, color=INK, fontweight="bold", zorder=7)
    for i, t in enumerate(("control loop ≈11 Hz", "DIC ≈20 fps", "registry · reports")):
        ax.text(-3.0, 1.85 - 0.36 * i, t, ha="center", fontsize=8, color=INK, zorder=7)
    # cabling
    ax.plot([-1.7, 1.45], [4.85, 4.85], color=GREY, lw=1.2, zorder=1)               # box -> motors (bus)
    ax.plot([1.45, 1.45], [4.85, 1.0], color=GREY, lw=1.2, zorder=1)
    ax.plot([1.45, 2.0], [1.0, 1.0], color=GREY, lw=1.2, zorder=1)
    ax.plot([1.45, 8.0], [4.85, 4.85], color=GREY, lw=1.2, ls=(0, (3, 2)), zorder=1)
    ax.plot([8.0, 8.0], [4.85, 1.45], color=GREY, lw=1.2, ls=(0, (3, 2)), zorder=1)
    ax.plot([-1.7, 4.6], [5.1, 5.1], color="#a9832f", lw=1.0, zorder=1)             # load-cell signal
    ax.plot([-1.7, -1.7], [1.6, 3.7], color=GREY, lw=1.2, zorder=1)                 # serial PC<->box
    ax.text(-1.55, 2.65, "serial", fontsize=7.5, color=SAGE, rotation=90, va="center", zorder=7)
    ax.plot([-1.7, 11.65], [0.75, 0.75], color=BLUE, lw=1.3, zorder=1)              # USB 3.0 PC<->camera
    ax.plot([11.65, 11.65], [0.75, 2.55], color=BLUE, lw=1.3, zorder=1)
    ax.text(3.0, 0.9, "USB 3.0 — frames", fontsize=7.8, color=BLUE, zorder=7)
    ax.plot([0.25, -1.7], [7.6, 7.6], color=GREY, lw=1.0, zorder=1)
    ax.plot([-1.7, -1.7], [7.6, 6.0], color=GREY, lw=1.0, zorder=1)

    # labels
    lab(5.0, 9.17, "Top member (fixed)", 9.6, 9.3)
    lab(8.0, 7.5, "Lead screws ×2 — 5 mm pitch", 9.6, 7.5)
    lab(8.0, 8.8, "Top bearings", 9.6, 8.85)
    lab(7.9, 5.75, "Central member = crosshead\n(rides on both nuts)", 9.6, 6.4)
    lab(5.4, 5.1, "Load cell — S-beam, 4.5 kN cap\n(ANYLOAD 101BH)", 9.6, 5.35, fs=8.8)
    lab(5.65, 4.1, "Upper grip (printed jaw)", 9.6, 4.3)
    lab(3.2, 5.13, "LED strip", 2.2, 4.6, ha="right", fs=8.8)
    lab(5.18, 2.95, "Specimen — 80 mm gauge,\ntwo spray-paint markers", 6.95, 1.0, fs=8.8)
    lab(6.95, 4.9, "Matte backdrop + enclosure\n(room light kept out)", 7.6, 6.9, fs=8.8)
    lab(4.35, 1.75, "Lower grip", 1.15, 2.1, ha="right", fs=8.8)
    lab(2.0, 1.0, "Steppers ×2, 20:1 gearbox", 1.15, 1.35, ha="right", fs=8.8)
    lab(1.3, 0.28, "Base — aluminium profile", 1.15, -0.55, ha="right", fs=8.8)
    lab(11.7, 3.6, "Basler acA2440-35um + 25 mm lens\non its printed mount, ≈371 mm off", 12.5, 4.9, fs=8.8)
    lab(11.65, 1.5, "Camera mount post", 12.5, 1.2, fs=8.8)
    lab(0.25, 7.6, "E-stop (cuts motor power)\n+ software stop", 0.5, 8.55, fs=8.8)
    ax.text(5.0, 10.3, "PPD-UTM DIC rig — schematic, September 2026", ha="center", fontsize=12.5,
            color=INK, fontweight="bold")
    ax.text(5.0, -1.1, "load path: lead screws → crosshead → load cell → grip → specimen → grip → base;  "
                       "strain: camera → PC;  force and position: electronics box → PC",
            ha="center", fontsize=8.4, color=SAGE)
    fig.tight_layout(pad=0.4)
    fig.savefig(os.path.join(FIGS, "report_rig_schematic.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  report_rig_schematic.png")


# ------------------------------------------------------------------ 2. the travel budget, aspect-true
def _frame(spec="S26"):
    p = os.path.join(FIGS, "wk_specimens", "%s_tare.png" % spec)
    g = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
    return g


def fig_travel():
    g = _frame("S26")
    (x1, y1, r1), (x2, y2, r2) = P._dots_in(g)
    h, w = g.shape
    fig = plt.figure(figsize=(13.0, 6.2))
    gs = fig.add_gridspec(2, 1, height_ratios=[h / w * 13.0 + 0.25, 2.6], hspace=0.35)
    ax = fig.add_subplot(gs[0])
    ax.imshow(g, cmap="gray", vmin=0, vmax=255)
    for x, y, r in ((x1, y1, r1), (x2, y2, r2)):
        ax.add_patch(Circle((x, y), r * 1.5, fill=False, ec=TAN, lw=2.2))
    ax.annotate("", xy=(6, y1), xytext=(x1 - r1 * 1.6, y1), arrowprops=dict(arrowstyle="<->", color=BLUE, lw=1.8))
    ax.annotate("", xy=(w - 6, y2), xytext=(x2 + r2 * 1.6, y2), arrowprops=dict(arrowstyle="<->", color=BLUE, lw=1.8))
    ax.annotate("", xy=(x2 - r2 * 1.6, y1 - r1 * 2.2), xytext=(x1 + r1 * 1.6, y1 - r1 * 2.2),
                arrowprops=dict(arrowstyle="<->", color=GREEN, lw=1.8))
    ax.text((x1 + x2) / 2, y1 - r1 * 2.9, "pair ≈ %.0f px" % abs(x2 - x1), ha="center", va="bottom",
            fontsize=11, color=GREEN, fontweight="bold")
    ax.text((x2 + w) / 2, y2 + r2 * 2.6, "room the walking marker spends", ha="center", fontsize=9.5,
            color=BLUE, bbox=dict(fc="white", ec="none", alpha=0.8, pad=1.5))
    ax.set_xlim(0, w); ax.set_ylim(h, 0); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color("#cccccc")
    ax.set_title("the budget on a real tare frame (S26, 2348 × 419 px region, shown at true aspect)",
                 fontsize=11, color=INK, pad=22)
    ax2 = fig.add_subplot(gs[1])
    rows = [("shipped region — 2348 px along the axis", 33.0, TAN),
            ("full sensor width — 2448 px (TPU recipes)", 39.0, BLUE)]
    for yi, (labt, v, c) in enumerate(rows):
        ax2.barh(yi, v, height=0.52, color=c, ec=INK, lw=0.6)
        ax2.text(v + 0.5, yi, "%.0f %%" % v, va="center", fontsize=11, color=INK, fontweight="bold")
        ax2.text(0.6, yi, labt, va="center", fontsize=10, color="white", fontweight="bold")
    ax2.axvline(37.5, color=INK, lw=1.6, ls="--")
    ax2.text(37.5, -0.75, "30 mm travel backstop = 37.5 % on an 80 mm gauge", fontsize=9.5, color=INK, ha="center")
    ax2.set_yticks([]); ax2.set_xlim(0, 46); ax2.set_ylim(-1.05, 1.75)
    ax2.set_xlabel("strain at which a marker reaches the frame edge (%)", fontsize=10)
    ax2.grid(True, color="#e3e6e8", lw=0.6, axis="x"); ax2.set_axisbelow(True)
    for spn in ("top", "right", "left"):
        ax2.spines[spn].set_visible(False)
    ax2.set_title("what the width buys: 2348 px runs out before the 30 mm backstop, 2448 px after it — "
                  "that gap is how S35/S36 walked out of frame", fontsize=10, color=INK, pad=8)
    fig.savefig(os.path.join(FIGS, "report_travel.png"), dpi=200, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print("  report_travel.png")


# ------------------------------------------------------------------ 3. the Px0 tracking strip for the cover
def fig_tracking_strip():
    g = _frame("S26")
    (x1, y1, r1), (x2, y2, r2) = P._dots_in(g)
    h, w = g.shape
    fig, ax = plt.subplots(figsize=(12.0, 12.0 * h / w))
    ax.imshow(g, cmap="gray", vmin=0, vmax=255)
    for x, y, r in ((x1, y1, r1), (x2, y2, r2)):
        ax.add_patch(Circle((x, y), r * 1.5, fill=False, ec=ORANGE, lw=2.4))
        ax.plot([x], [y], "+", ms=12, mew=2.0, color=ORANGE)
    ax.annotate("", xy=(x2 - r2 * 1.7, y1), xytext=(x1 + r1 * 1.7, y1),
                arrowprops=dict(arrowstyle="<|-|>", color=ORANGE, lw=2.4, mutation_scale=20))
    ax.text((x1 + x2) / 2, y1 - r1 * 2.4, "Px₀ = %.0f px  — frozen at the tare, tracked every frame" % abs(x2 - x1),
            ha="center", va="bottom", fontsize=14, color=ORANGE, fontweight="bold",
            bbox=dict(fc="white", ec="none", alpha=0.85, pad=2))
    ax.text(18, h - 14, "2 / 2 markers · Px₀ locked", fontsize=11.5, color="white", va="bottom",
            fontweight="bold", bbox=dict(boxstyle="round,pad=0.3", fc=GREEN, ec="none"))
    ax.set_xlim(0, w); ax.set_ylim(h, 0); ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(os.path.join(FIGS, "report_tracking_strip.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  report_tracking_strip.png")


if __name__ == "__main__":
    fig_schematic()
    fig_travel()
    fig_tracking_strip()
