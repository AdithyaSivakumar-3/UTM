"""Figures for the camera-resolution story: sensor -> ROI -> rotation, the travel budget,
and the exposure-fps ceiling. Every number is read from the code or a real capture.

    Sensor 2448x2048 (docs/RECALIBRATE_ROI.md), ROI [0, 988, 2348, 419] and the 90 deg CW
    rotation from camera_manager.py; L0 about 1665 px from the preset note; 33 %% / 39 %%
    travel limits from set_roi's own docstring; exposure 50 ms and the x0.3-x2.8 sweep from
    main.AUTOCAL_EXPOSURE_STEPS; 19.9 fps measured on S24-S26.
"""
import glob
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                       # noqa: E402
import matplotlib.patches as mpatches                                 # noqa: E402

import cv2                                                            # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.abspath(os.path.join(HERE, "..", "figures"))
APP = os.path.abspath(os.path.join(HERE, "..", "..", "Software", "UTM_PyQt6"))
ROOT = os.path.join(APP, "Test data", "Fracture tests")
sys.path.insert(0, APP)

import utm_postproc as PP                                             # noqa: E402

INK, GRID, ACC = "#212529", "#DDDDDD", "#E8590C"
BLUE, GREEN = "#1F6FB4", "#2E9E4F"

SENSOR_W, SENSOR_H = 2448, 2048
ROI = [0, 988, 2348, 419]                     # OffsetX, OffsetY, Width, Height
L0 = 1665.0
MARKER_R = 60.0


def _frame():
    """A real stored frame (portrait, rows along the specimen), from S26."""
    d = glob.glob(os.path.join(ROOT, "Specimen_S26_*"))[0]
    vid = (glob.glob(os.path.join(d, "*", "video.avi"))
           + glob.glob(os.path.join(d, "*", "video.mkv")))[0]
    return PP.read_frame(vid, 0)


def fig_pipeline():
    """Sensor rectangle -> the ROI band it reads -> the rotated frame everything else sees."""
    g = _frame()                              # portrait: ~2348 rows x ~420 cols
    land = cv2.rotate(g, cv2.ROTATE_90_COUNTERCLOCKWISE)     # back to sensor orientation

    fig = plt.figure(figsize=(12.4, 4.4))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.55, 0.16, 0.55], wspace=0.02)

    # -- the sensor, with the ROI band shown as the only live pixels
    ax = fig.add_subplot(gs[0])
    ax.add_patch(mpatches.Rectangle((0, 0), SENSOR_W, SENSOR_H, fc="#2b3036", ec=INK, lw=1.4))
    x0, y0, w, h = ROI
    band = cv2.resize(land, (w, h))
    ax.imshow(band, cmap="gray", extent=(x0, x0 + w, y0 + h, y0), zorder=3)
    ax.add_patch(mpatches.Rectangle((x0, y0), w, h, fill=False, ec=ACC, lw=2.4, zorder=4))
    ax.annotate("", xy=(x0 + w, y0 - 150), xytext=(x0, y0 - 150),
                arrowprops=dict(arrowstyle="<->", color="white", lw=1.2))
    ax.text(x0 + w / 2, y0 - 230, "Width 2348 px (of 2448)", ha="center", fontsize=9,
            color="white")
    ax.annotate("", xy=(2510, y0 + h), xytext=(2510, y0),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=1.2))
    ax.text(2560, y0 + h / 2, "419 px", rotation=90, va="center", fontsize=9, color=INK)
    ax.annotate("", xy=(80, y0), xytext=(80, 0),
                arrowprops=dict(arrowstyle="<->", color="#9aa4ad", lw=1.1))
    ax.text(120, y0 / 2, "OffsetY 988 px", fontsize=8.5, color="#9aa4ad", va="center")
    ax.text(SENSOR_W / 2, -120, "Basler sensor — 2448 × 2048 px, Mono8, never scaled",
            ha="center", fontsize=10, color=INK)
    ax.text(SENSOR_W / 2, 2200,
            "the other 1 629 rows are never read out — they hold grips and background, "
            "not specimen", ha="center", fontsize=8.8, color="#777777")
    ax.set_xlim(-40, 2740); ax.set_ylim(2320, -260)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title("1 · the sensor, and the ROI it actually reads", fontsize=10.5, color=INK)

    # -- the arrow
    axm = fig.add_subplot(gs[1]); axm.axis("off")
    axm.annotate("", xy=(0.9, 0.5), xytext=(0.1, 0.5), xycoords="axes fraction",
                 arrowprops=dict(arrowstyle="-|>", color=INK, lw=2.2))
    axm.text(0.5, 0.60, "rotate\n90° CW", ha="center", va="bottom", fontsize=9.5, color=INK)

    # -- the stored frame
    ax2 = fig.add_subplot(gs[2])
    ax2.imshow(g, cmap="gray", aspect="auto")
    ax2.set_xticks([]); ax2.set_yticks([])
    for sp in ax2.spines.values():
        sp.set_color(ACC); sp.set_linewidth(2.0)
    ax2.set_title("2 · the stored frame — 420 × 2348\n(rows run along the pull)",
                  fontsize=10, color=INK, pad=8)
    fig.text(0.34, 0.955, "From sensor to frame: crop first, rotate second — never scale, "
                          "so a pixel is always the same 48 µm",
             ha="center", fontsize=11.5, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(os.path.join(FIGS, "cam_pipeline.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  cam_pipeline.png")


def fig_travel():
    """The along-axis pixel budget: where the pair sits, and how far it may separate."""
    g = _frame()
    marks = PP.find_markers(g)
    marks = sorted(sorted(marks, key=lambda m: -m[2])[:2], key=lambda m: m[1])
    span = g.shape[0]

    fig = plt.figure(figsize=(12.4, 4.1))
    gs = fig.add_gridspec(1, 2, width_ratios=[0.42, 1.6], wspace=0.14)

    ax = fig.add_subplot(gs[0])
    ax.imshow(g, cmap="gray", aspect="auto")
    for m in marks:
        ax.add_patch(mpatches.Circle((m[0], m[1]), MARKER_R, fill=False, ec=ACC, lw=2.0))
    (xt, yt), (xb, yb) = [(m[0], m[1]) for m in marks]
    ax.annotate("", xy=(xt, yt - MARKER_R), xytext=(xt, 6),
                arrowprops=dict(arrowstyle="<->", color=BLUE, lw=1.6))
    ax.annotate("", xy=(xb, yb + MARKER_R), xytext=(xb, span - 6),
                arrowprops=dict(arrowstyle="<->", color=BLUE, lw=1.6))
    ax.text(12, (yb + span) / 2, "room the walking\nmarker spends",
            fontsize=8.2, color=BLUE, va="center")
    ax.annotate("", xy=(g.shape[1] - 24, yt), xytext=(g.shape[1] - 24, yb),
                arrowprops=dict(arrowstyle="<->", color=GREEN, lw=1.6))
    ax.text(g.shape[1] - 92, (yt + yb) / 2, "pair ≈ 1665 px", rotation=90, fontsize=8.4,
            color=GREEN, va="center",
            bbox=dict(fc="white", ec="none", alpha=0.75, pad=1.2))
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("the budget (S26)", fontsize=10, color=INK)

    ax2 = fig.add_subplot(gs[1])
    rows = [("shipped ROI — 2348 px along the axis", 33.0, ACC),
            ("full sensor width — 2448 px (TPU recipes)", 39.0, BLUE)]
    y = np.arange(len(rows))
    for yi, (lab, v, c) in zip(y, rows):
        ax2.barh(yi, v, height=0.52, color=c, ec=INK, lw=0.6)
        ax2.text(v + 0.5, yi, "%.0f %%" % v, va="center", fontsize=10, color=INK,
                 fontweight="bold")
        ax2.text(0.6, yi, lab, va="center", fontsize=9.6, color="white", fontweight="bold")
    ax2.axvline(37.5, color=INK, lw=1.6, ls="--")
    ax2.text(37.5, -0.72, "30 mm travel backstop = 37.5 % on an 80 mm gauge", fontsize=9,
             color=INK, ha="center")
    ax2.set_yticks([]); ax2.set_xlim(0, 46); ax2.set_ylim(-1.0, 1.8)
    ax2.set_xlabel("strain at which a marker reaches the frame edge (%)", fontsize=9.5)
    ax2.grid(True, color=GRID, lw=0.6, axis="x"); ax2.set_axisbelow(True)
    for spn in ("top", "right", "left"):
        ax2.spines[spn].set_visible(False)
    ax2.set_title("what the width buys: 2348 px runs out BEFORE the 30 mm backstop, 2448 px "
                  "after it —\nthat gap is how S35/S36 walked out of frame", fontsize=10,
                  color=INK, pad=10)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "cam_travel.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  cam_travel.png")


def fig_exposure():
    """fps = 1/exposure is a law of physics; the requested 35 fps never was available at 50 ms."""
    fig, ax = plt.subplots(figsize=(12.4, 3.9))
    e = np.linspace(8, 150, 400)
    ax.plot(e, 1000.0 / e, color=INK, lw=2.0,
            label="the ceiling: fps = 1 / exposure — the sensor cannot expose faster than time passes")
    lo, hi = 50 * 0.3, 50 * 2.8
    ax.axvspan(lo, hi, color="#DCE8F5", zorder=0,
               label="auto-calibrate sweep: ×0.3 … ×2.8 of the current exposure (15–140 ms here)")
    ax.axhline(35, color="#999999", lw=1.4, ls=":")
    ax.text(146, 35.8, "35 fps requested — needs ≤ 28.6 ms", fontsize=8.8, color="#666666",
            ha="right")
    ax.plot([50], [20], "o", ms=10, color=ACC, zorder=5)
    ax.annotate("running point: 50 ms → ceiling 20.0 fps\nmeasured on the rig: 19.9 fps",
                xy=(50, 20), xytext=(68, 26.5), fontsize=9.6, color=ACC,
                arrowprops=dict(arrowstyle="->", color=ACC, lw=1.4))
    ax.plot([28.6], [35], "s", ms=7, color="#666666", zorder=5)
    ax.set_xlabel("exposure time (ms)", fontsize=10)
    ax.set_ylabel("frames per second", fontsize=10)
    ax.set_xlim(8, 150); ax.set_ylim(0, 80)
    ax.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
    for spn in ("top", "right"):
        ax.spines[spn].set_visible(False)
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    ax.set_title("Exposure sets the frame rate — not the resolution. Longer exposure = more "
                 "light per frame = better marker contrast, but fewer frames per second.",
                 fontsize=11, color=INK)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "cam_exposure.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  cam_exposure.png")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    print("Camera figures:")
    fig_pipeline()
    fig_travel()
    fig_exposure()
