# -*- coding: utf-8 -*-
"""Third batch of report-only figures.

  report_rig_schematic.png   the rig in FRONT and SIDE view, September 2026, with the data
                             path as a chain underneath — replaces the single-view drawing
  report_cover_thresh.png    the thresholded gauge strip at TRUE aspect (2348 x 419), for the
                             cover; the old one was cropped out of a plot drawn with
                             aspect="auto" and was therefore horizontally stretched
  report_frac_faces.png      the two fracture characters, with a wider, clearer PLA crop —
                             report-only, so the decks' own frac_faces.png is untouched
"""
import glob
import os
import sys

import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FIGS = os.path.join(ROOT, "documentation", "figures")
DATA = os.path.join(ROOT, "Software", "UTM_PyQt6", "Test data", "Fracture tests")

INK, TAN, SAGE = "#253439", "#B29E84", "#7C898B"
BLUE, ORANGE, GREEN, GREY = "#1f6fb2", "#e8590c", "#1e8449", "#9aa3aa"
STEEL, ALU, PRINT = "#8d949b", "#adb5bd", "#f5f5f5"
plt.rcParams["font.family"] = "Segoe UI"


# ================================================================= 1. the schematic, two views
def fig_schematic():
    fig = plt.figure(figsize=(15.5, 9.2))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 0.155], width_ratios=[1.0, 1.06],
                          hspace=0.06, wspace=0.05)
    axF = fig.add_subplot(gs[0, 0])
    axS = fig.add_subplot(gs[0, 1])
    axD = fig.add_subplot(gs[1, :])
    for ax in (axF, axS, axD):
        ax.axis("off")

    def box(ax, x, y, w, h, fc=ALU, ec=INK, lw=1.2, z=2, r=0.0):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                                    boxstyle="round,pad=0,rounding_size=%.2f" % r,
                                    fc=fc, ec=ec, lw=lw, zorder=z))

    def lab(ax, x, y, text, tx, ty, ha="left", fs=9.0, col=INK, z=9):
        ax.annotate(text, xy=(x, y), xytext=(tx, ty), fontsize=fs, color=col, ha=ha,
                    va="center", zorder=z,
                    arrowprops=dict(arrowstyle="-", color=GREY, lw=0.85, shrinkA=0, shrinkB=2))

    def specimen(ax, cx, y0, y1, w=0.34, markers=True, edge_on=False):
        """A dogbone between y0 and y1; edge-on it is a plain bar."""
        if edge_on:
            ax.add_patch(Rectangle((cx - w * 0.42, y0), w * 0.84, y1 - y0, fc="white",
                                   ec=INK, lw=1.0, zorder=6))
        else:
            a, b = w, w * 0.52
            ax.add_patch(Polygon([(cx - a, y0), (cx + a, y0), (cx + a, y0 + 0.42),
                                  (cx + b, y0 + 0.68), (cx + b, y1 - 0.68), (cx + a, y1 - 0.42),
                                  (cx + a, y1), (cx - a, y1), (cx - a, y1 - 0.42),
                                  (cx - b, y1 - 0.68), (cx - b, y0 + 0.68), (cx - a, y0 + 0.42)],
                                 closed=True, fc="white", ec=INK, lw=1.0, zorder=6))
        if markers:
            for y in (y0 + (y1 - y0) * 0.30, y0 + (y1 - y0) * 0.70):
                ax.add_patch(Circle((cx, y), 0.105, fc=INK, ec="none", zorder=7))

    # ---------------------------------------------------------------- FRONT VIEW
    axF.set_xlim(-0.4, 10.5); axF.set_ylim(-0.9, 11.1); axF.set_aspect("equal")
    axF.text(5.05, 10.75, "FRONT VIEW", ha="center", fontsize=12.5, color=INK, fontweight="bold")
    axF.text(5.05, 10.35, "the load train, seen along the camera's axis", ha="center",
             fontsize=9.4, color=SAGE)
    # enclosure ground + matte backdrop
    axF.add_patch(Rectangle((1.1, 0.55), 8.2, 8.6, fc="#f7f4ef", ec="none", zorder=0))
    box(axF, 3.15, 1.35, 3.9, 4.0, fc="#c9c4bd", ec="#a49d94", lw=1.0, z=1)
    # base, feet, pedestal
    box(axF, 0.8, 0.0, 8.8, 0.55, fc="#d5d9dd", z=2)
    for x in (0.85, 8.85):
        box(axF, x, -0.45, 0.55, 0.45, fc="#b9bfc5", z=2)
    box(axF, 4.72, 0.55, 0.96, 0.8, fc="#cfd4d8", z=3)
    # lead screws, motors, nuts, bearings
    for x in (2.2, 8.2):
        axF.plot([x, x], [0.55, 8.75], color="#5c6670", lw=5.0, solid_capstyle="butt", zorder=2)
        axF.plot([x, x], [0.55, 8.75], color=GREY, lw=1.1, ls=(0, (1, 1.2)), zorder=3)
        box(axF, x - 0.56, 0.55, 1.12, 0.92, fc=STEEL, z=3, r=0.08)      # stepper + gearbox
        box(axF, x - 0.5, 5.35, 1.0, 0.76, fc="#7f8790", z=5, r=0.06)    # nut
        box(axF, x - 0.42, 8.45, 0.84, 0.5, fc=STEEL, z=4, r=0.06)       # top bearing
    box(axF, 1.4, 8.95, 7.6, 0.55, fc=ALU, z=4)                          # top member
    box(axF, 1.4, 5.4, 7.6, 0.66, fc=ALU, z=4)                           # crosshead
    # load cell, adapter, grips, specimen
    box(axF, 4.75, 4.62, 0.9, 0.78, fc="#f0d9a8", ec="#a9832f", z=5, r=0.08)
    box(axF, 4.95, 4.34, 0.5, 0.28, fc="#cfd4d8", z=5)
    box(axF, 4.45, 3.62, 1.5, 0.72, fc=PRINT, ec=INK, z=5, r=0.1)
    box(axF, 4.45, 1.35, 1.5, 0.72, fc=PRINT, ec=INK, z=5, r=0.1)
    specimen(axF, 5.2, 1.5, 4.3)
    # LED strip
    box(axF, 3.3, 4.98, 3.7, 0.17, fc="#fff1b8", ec="#c9a227", z=6)
    for x in np.linspace(3.55, 6.75, 9):
        axF.plot([x], [5.07], marker="o", ms=3.0, color="#e0b400", zorder=7)
    # E-stop
    axF.add_patch(Circle((0.35, 7.5), 0.27, fc="#c0392b", ec=INK, lw=1.0, zorder=6))
    box(axF, 0.05, 6.95, 0.6, 0.3, fc="#f1c40f", ec=INK, z=5)
    # front-view labels (right side, stacked so the leaders never cross)
    lab(axF, 5.2, 9.22, "Top member (fixed)", 9.35, 9.6, fs=9.4)
    lab(axF, 8.2, 8.7, "Top bearings", 9.35, 8.9, fs=9.4)
    lab(axF, 8.2, 7.2, "Lead screws ×2,\n5 mm pitch", 9.35, 7.4, fs=9.4)
    lab(axF, 8.9, 5.72, "Crosshead —\nrides on both nuts", 9.35, 5.85, fs=9.4)
    lab(axF, 5.65, 5.0, "Load cell,\n4.5 kN S-beam", 9.35, 4.35, fs=9.4)
    lab(axF, 5.95, 3.98, "Printed grips ×2", 9.35, 3.1, fs=9.4)
    lab(axF, 5.35, 2.9, "Specimen — 80 mm\ngauge, two markers", 9.35, 1.85, fs=9.4)
    lab(axF, 0.35, 7.5, "E-stop\n+ software stop", 1.8, 8.4, ha="right", fs=9.4)
    lab(axF, 1.68, 1.0, "Steppers ×2, 20:1", 1.5, 1.55, ha="right", fs=9.4)
    lab(axF, 1.6, 0.28, "Base", 1.8, -0.5, ha="right", fs=9.4)

    # ---------------------------------------------------------------- SIDE VIEW
    axS.set_xlim(-0.4, 12.3); axS.set_ylim(-0.9, 11.1); axS.set_aspect("equal")
    axS.text(5.4, 10.75, "SIDE VIEW", ha="center", fontsize=12.5, color=INK, fontweight="bold")
    axS.text(5.4, 10.35, "the optics: backdrop behind the specimen, camera ≈371 mm in front",
             ha="center", fontsize=9.4, color=SAGE)
    axS.add_patch(Rectangle((0.9, 0.55), 2.9, 8.6, fc="#f7f4ef", ec="none", zorder=0))
    box(axS, 0.6, 0.0, 3.6, 0.55, fc="#d5d9dd", z=2)                     # base, in profile
    box(axS, 0.7, -0.45, 0.55, 0.45, fc="#b9bfc5", z=2)
    box(axS, 3.5, -0.45, 0.55, 0.45, fc="#b9bfc5", z=2)
    axS.plot([2.35, 2.35], [0.55, 8.75], color="#5c6670", lw=5.0, solid_capstyle="butt", zorder=2)
    box(axS, 1.8, 0.55, 1.12, 0.92, fc=STEEL, z=3, r=0.08)
    box(axS, 1.85, 5.35, 1.0, 0.76, fc="#7f8790", z=5, r=0.06)
    box(axS, 1.93, 8.45, 0.84, 0.5, fc=STEEL, z=4, r=0.06)
    box(axS, 1.5, 8.95, 1.9, 0.55, fc=ALU, z=4)                          # top member, in profile
    box(axS, 1.5, 5.4, 1.9, 0.66, fc=ALU, z=4)                           # crosshead, in profile
    box(axS, 2.28, 4.62, 0.85, 0.78, fc="#f0d9a8", ec="#a9832f", z=5, r=0.08)
    box(axS, 2.35, 3.62, 0.72, 0.72, fc=PRINT, ec=INK, z=5, r=0.1)
    box(axS, 2.35, 1.35, 0.72, 0.72, fc=PRINT, ec=INK, z=5, r=0.1)
    box(axS, 2.5, 0.55, 0.45, 0.8, fc="#cfd4d8", z=3)
    specimen(axS, 2.71, 1.5, 4.3, w=0.30, markers=False, edge_on=True)
    # the matte backdrop sits BEHIND the specimen, i.e. away from the camera
    box(axS, 1.62, 1.35, 0.12, 4.0, fc="#c9c4bd", ec="#a49d94", lw=1.0, z=4)
    box(axS, 2.15, 4.98, 1.1, 0.17, fc="#fff1b8", ec="#c9a227", z=6)     # LED strip, edge-on
    # camera, its post and the optical axis
    box(axS, 8.05, 2.4, 1.5, 1.1, fc="#3d434a", ec=INK, z=6, r=0.1)
    box(axS, 7.2, 2.62, 0.85, 0.62, fc="#2b2f34", ec=INK, z=6, r=0.05)
    box(axS, 8.5, 0.55, 0.5, 1.85, fc=STEEL, z=5)
    box(axS, 7.9, 2.2, 1.8, 0.22, fc="#6c757d", z=6)
    box(axS, 7.6, 0.0, 2.2, 0.55, fc="#d5d9dd", z=2)
    axS.add_patch(Polygon([(7.2, 2.72), (2.9, 1.55), (2.9, 4.25), (7.2, 3.12)], closed=True,
                          fc=BLUE, ec="none", alpha=0.09, zorder=1))
    axS.plot([7.2, 2.9], [2.93, 2.9], color=BLUE, lw=0.9, ls="--", zorder=2)
    # stand-off dimension
    axS.annotate("", xy=(2.9, 6.75), xytext=(7.2, 6.75),
                 arrowprops=dict(arrowstyle="<->", color=INK, lw=1.2), zorder=6)
    for x in (2.9, 7.2):
        axS.plot([x, x], [3.0, 6.9], color=GREY, lw=0.7, ls=":", zorder=1)
    axS.text(5.05, 6.95, "≈371 mm stand-off  →  20.9 px/mm, 112 mm of field",
             ha="center", fontsize=9.4, color=INK, zorder=7)
    lab(axS, 9.55, 3.0, "Basler acA2440-35um\n+ 25 mm C-mount lens", 10.0, 4.35, ha="left", fs=9.4)
    lab(axS, 8.75, 1.45, "Printed camera mount\non its own base plate", 10.0, 1.15, ha="left", fs=9.4)
    lab(axS, 1.68, 1.9, "Matte backdrop — BEHIND the specimen", 0.1, -0.62, ha="left", fs=9.4)
    lab(axS, 2.71, 2.2, "Specimen, edge-on", 3.7, 1.35, ha="left", fs=9.4)
    lab(axS, 3.25, 5.07, "LED strip, above the field of view", 3.7, 5.95, ha="left", fs=9.4)
    axS.text(5.6, 4.25, "field of view", fontsize=9.2, color=BLUE, ha="center", zorder=9)

    # ---------------------------------------------------------------- the data path
    axD.set_xlim(0, 24); axD.set_ylim(-0.55, 1.45); axD.set_aspect("equal")
    chain = [(0.4, "Electronics box\nESP32 · 2× TMC drivers · load-cell amp", 5.2, "#eef2f5"),
             (7.6, "PC — PyQt6 application\ncontrol loop ≈11 Hz · DIC ≈20 fps · registry", 6.6, "#eef2f5"),
             (17.0, "Camera\nUSB3 Vision", 3.0, "#e6eef7")]
    for x, t, w, fc in chain:
        axD.add_patch(FancyBboxPatch((x, 0.0), w, 1.0, boxstyle="round,pad=0,rounding_size=0.08",
                                     fc=fc, ec=INK, lw=1.1))
        axD.text(x + w / 2, 0.5, t, ha="center", va="center", fontsize=8.6, color=INK)
    axD.annotate("", xy=(7.5, 0.5), xytext=(5.7, 0.5),
                 arrowprops=dict(arrowstyle="<->", color=INK, lw=1.2))
    axD.text(6.6, 0.95, "serial\nforce · position", ha="center", fontsize=8.0, color=SAGE)
    axD.annotate("", xy=(16.9, 0.5), xytext=(14.3, 0.5),
                 arrowprops=dict(arrowstyle="<->", color=BLUE, lw=1.3))
    axD.text(15.6, 0.95, "USB 3.0\nframes", ha="center", fontsize=8.0, color=BLUE)
    axD.text(21.0, 0.5, "Guards on top of everything: 4.5 kN and 30 mm backstops,\n"
                        "stall guard, dead-DIC guard, both E-stops",
             ha="left", va="center", fontsize=8.4, color=SAGE)

    # no suptitle: the report's caption carries the title, and dropping it lets the drawing
    # itself fill the frame — the figure is printed at body width, so every millimetre counts
    fig.savefig(os.path.join(FIGS, "report_rig_schematic.png"), dpi=190, facecolor="white",
                bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    print("  report_rig_schematic.png (front + side)")


# ================================================================= 2. the cover threshold strip
def fig_cover_thresh():
    """The thresholded gauge strip at TRUE aspect: what the fixed threshold keeps and what it
    would have kept had the cut been lower. Built from the S13 tare frame (black PLA, white
    markers, preset 149) so the two markers are the small bright class."""
    g = cv2.imread(os.path.join(FIGS, "wk_specimens", "S13_tare.png"), cv2.IMREAD_GRAYSCALE)
    h, w = g.shape
    rgb = cv2.cvtColor(g, cv2.COLOR_GRAY2RGB).astype(np.float32)
    fg = g >= 149                                   # the rig's Black preset
    loose = (g >= 131) & ~fg                        # what Otsu's lower cut would have added
    # Everything the threshold keeps is shown in red, with the looser cut in amber behind it —
    # no marker highlight, no rings, no rule: the cover shows the thresholding, nothing else.
    rgb[loose] = 0.45 * rgb[loose] + 0.55 * np.array([245, 166, 35], np.float32)   # amber
    rgb[fg] = 0.35 * rgb[fg] + 0.65 * np.array([214, 69, 45], np.float32)          # red
    out = np.clip(rgb, 0, 255).astype(np.uint8)
    cv2.imwrite(os.path.join(FIGS, "report_cover_thresh.png"), cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
    print("  report_cover_thresh.png  %dx%d (true aspect %.2f)" % (w, h, w / h))


# ================================================================= 3. fracture faces, better PLA
def fig_faces():
    pla = cv2.imread(os.path.join(DATA, "Specimen_S25_V2_Spray_Video2", "S25 .jpg"))
    petg = cv2.imread(os.path.join(DATA, "Specimen_S30_V3_PETG_Spray_Video9", "S30.jpg"))
    pla_c = pla[930:1430, 160:790]                  # break + gauge + the grip below it
    petg_c = petg[1250:2048, 150:1350]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.4, 4.2),
                                 gridspec_kw={"width_ratios": [1.16, 1.5]})
    a1.imshow(cv2.cvtColor(pla_c, cv2.COLOR_BGR2RGB))
    a1.set_title("PLA (S25) — clean, near-flat break; NO whitening, no necking:\n"
                 "the halves would almost re-mate", fontsize=9.5, color=BLUE)
    a2.imshow(cv2.cvtColor(petg_c, cv2.COLOR_BGR2RGB))
    a2.set_title("PETG (S30) — stress-whitening speckled along the WHOLE gauge,\n"
                 "fibrous drawn fracture faces", fontsize=9.5, color="#7b4fd6")
    for ax in (a1, a2):
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color("#CCCCCC")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "report_frac_faces.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  report_frac_faces.png")


if __name__ == "__main__":
    fig_schematic()
    fig_cover_thresh()
    fig_faces()
