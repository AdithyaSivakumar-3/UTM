"""The two extra figures for the MOT post-processing slides.

  motpp_setup.png   what each machine actually filmed, side by side and to the same scale
  motpp_share.png   where the commanded 0.1 mm/s goes on each machine

Both read documentation/mot_postproc_compare.json, which mot_postproc_compare.py writes, so a
number on a slide and a number in a figure cannot disagree.

Frames are decoded SEQUENTIALLY. The MOT file's seek returns stale pictures past about frame 80,
which is what made an earlier pass of this analysis conclude the video held no deformation.
"""
import io
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                       # noqa: E402
from matplotlib.patches import Circle                                 # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
FIGS = os.path.abspath(os.path.join(HERE, "..", "figures"))
CACHE = os.path.abspath(os.path.join(HERE, "..", "mot_postproc_compare.json"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "Software", "UTM_PyQt6"))

import cv2                                                            # noqa: E402
import utm_postproc as PP                                             # noqa: E402
import mot_compare as MC                                              # noqa: E402

RIG = MC.RIG

INK, GRID, MUTED = "#212529", "#DDDDDD", "#666666"
C_MOT, C_OURS, C_S25, C_S26 = "#d62728", "#1f77b4", "#1f77b4", "#e8590c"
GOOD, BAD = "#2e7d32", "#c0392b"


def load():
    return json.load(io.open(CACHE, encoding="utf-8"))


def _style(ax):
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def _first_frame(path):
    """Frame 0, decoded rather than sought — see the module docstring."""
    cap = cv2.VideoCapture(path)
    ok, fr = cap.read()
    cap.release()
    if not ok:
        return None
    return cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY) if fr.ndim == 3 else fr


def fig_setup():
    """What each machine filmed. Drawn to the same PIXELS-PER-MILLIMETRE, not the same width.

    Scaling both to the frame width would hide the thing that matters: the MOT resolves the same
    80 mm gauge across 2234 px where we use 1676 px, so its pixel is worth a third less strain.
    """
    import glob
    mot = os.path.join(os.path.dirname(MC.MOT), "test2.chan 0.avi")
    ours = glob.glob(os.path.join(MC.DATA, "**", "Specimen_S26_*", "**", "video.avi"),
                     recursive=True)[0]
    gm, go = _first_frame(mot), _first_frame(ours)

    fig, axes = plt.subplots(2, 1, figsize=(11.4, 5.4))
    for ax, g, name, ppm, l0, col in (
            (axes[0], gm, "MOT XT-205 — test2.chan 0.avi", 2234.4 / 80.0033, 2234.4, C_MOT),
            (axes[1], go, "%s — S26 video.avi" % RIG, 1676.3 / 80.0, 1676.3, C_OURS)):
        if g is None:
            continue
        # Our specimen is filmed upright, theirs on its side; rotate ours so the gauge runs the
        # same way in both panels and the two can actually be compared by eye.
        if g.shape[0] > g.shape[1]:
            g = np.rot90(g)
        ax.imshow(g, cmap="gray", vmin=0, vmax=255)
        ms = sorted(PP.find_markers(g)[:2], key=lambda m: m[0])
        for m in ms:
            ax.add_patch(Circle((m[0], m[1]), m[2] * 1.35, fill=False, ec=col, lw=1.8))
        if len(ms) == 2:
            ax.annotate("", xy=(ms[1][0], ms[1][1]), xytext=(ms[0][0], ms[0][1]),
                        arrowprops=dict(arrowstyle="<->", color=col, lw=1.6))
            ax.text((ms[0][0] + ms[1][0]) / 2, ms[0][1] - 0.10 * g.shape[0],
                    "Px₀ = %.0f px  ·  %.1f px/mm" % (l0, ppm),
                    ha="center", fontsize=9.5, color=col, fontweight="bold")
        ax.set_title("%s   —   %d × %d px" % (name, g.shape[1], g.shape[0]),
                     fontsize=10, color=INK, loc="left")
        ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "motpp_setup.png"), dpi=170, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    print("  motpp_setup.png")


def fig_share(D):
    """Where the commanded 0.1 mm/s goes, and the part that is easy to miss — the SPREAD."""
    sh = D["gauge_share"]
    # Wide and short on purpose: on the slide this is height-limited, so a squarer figure would be
    # scaled down to a narrow strip in the middle of a 12.5 in page.
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(13.4, 3.7),
                                 gridspec_kw={"width_ratios": [1.25, 1]})

    keys = ["S25", "S26", "MOT"]
    labels = ["S25\n%s" % RIG, "S26\n%s" % RIG, "MOT\nXT-205"]
    cols = [C_S25, C_S26, C_MOT]
    share = [100 * sh[k]["share"] for k in keys]
    b = ax.bar(labels, share, color=cols, width=0.6)
    ax.axhline(100, color=INK, ls="--", lw=1.3)
    ax.text(2.45, 101.5, "all of it reaching the gauge", fontsize=8.4, color=INK, ha="right")
    for r, v, k in zip(b, share, keys):
        ax.text(r.get_x() + r.get_width() / 2, v + 2.5, "%.0f %%" % v, ha="center",
                fontsize=12, fontweight="bold", color=INK)
        ax.text(r.get_x() + r.get_width() / 2, v / 2, "%.4f\nmm/s" % sh[k]["gauge_mm_s"],
                ha="center", va="center", fontsize=8.6, color="white", fontweight="bold")
    ax.set_ylim(0, 118)
    ax.set_ylabel("share of the commanded 0.1 mm/s\nthat reaches the gauge (%)")
    ax.set_title("Both machines were set to 0.1 mm/s.\nThe gauge does not see all of it on either.",
                 fontsize=10.5, color=INK)
    _style(ax)

    # the spread, which is the diagnostic
    bx.plot([0, 0], [share[0], share[1]], "-", color=C_OURS, lw=2.2)
    bx.plot([0], [share[0]], "o", color=C_S25, ms=11, label="S25")
    bx.plot([0], [share[1]], "s", color=C_S26, ms=11, label="S26")
    bx.plot([1], [share[2]], "D", color=C_MOT, ms=11, label="MOT")
    bx.annotate("", xy=(0.09, share[1]), xytext=(0.09, share[0]),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=1.3))
    bx.text(0.14, (share[0] + share[1]) / 2,
            "%.0f points apart\non two runs of the\nSAME protocol" % (share[1] - share[0]),
            fontsize=9, color=INK, va="center")
    bx.set_xlim(-0.35, 1.5); bx.set_ylim(0, 75)
    bx.set_xticks([0, 1])
    bx.set_xticklabels(["%s\n(two specimens)" % RIG, "MOT XT-205"])
    bx.set_ylabel("share reaching the gauge (%)")
    bx.set_title("A fixed compliance would repeat.\nThis does not — so it is not fixed.",
                 fontsize=10.5, color=INK)
    bx.legend(fontsize=8.5, loc="upper right")
    _style(bx)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "motpp_share.png"), dpi=200, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    print("  motpp_share.png")


def all_figs():
    D = load()
    print("MOT post-processing figures:")
    fig_setup()
    fig_share(D)
    return D


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    all_figs()
