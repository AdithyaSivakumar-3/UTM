"""Otsu on a real rig frame: the picture, its histogram, and where the two rules cut.

  otsu_frame.png    a live S13 frame and the same frame binarised at Otsu's cut and at the preset's
  otsu_hist.png     the grey histogram of 120 frames, with both thresholds marked
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                       # noqa: E402

import cv2                                                            # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.abspath(os.path.join(HERE, "..", "figures"))
sys.path.insert(0, HERE)

import otsu_data as OD                                                # noqa: E402

INK, GRID, MUTED = "#212529", "#DDDDDD", "#666666"
C_OTSU, C_FIX = "#d62728", "#1F6FB4"


def _style(ax):
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def fig_hist(D=None):
    """The grey histogram Otsu actually sees, with both cuts on it.

    Plotted on a LOG count axis. On a linear one the two marker blobs are invisible — they are a
    fraction of a per cent of the pixels — and the whole argument of the slide is that Otsu is
    balancing two classes in which the markers barely register.
    """
    D = D or OD.load()
    h = D["hist"]
    fig, ax = plt.subplots(figsize=(6.60, 3.55))

    ax.fill_between(np.arange(256), h, 0, color="#9AA5AB", alpha=0.55, lw=0)
    ax.plot(np.arange(256), h, "-", color="#5A6570", lw=1.0)

    ax.axvline(D["otsu_med"], color=C_OTSU, lw=2.2)
    ax.axvline(D["fixed"], color=C_FIX, lw=2.2, ls="--")
    ax.axvspan(D["otsu_med"], D["fixed"], color="#F0C808", alpha=0.20, lw=0)

    ax.annotate("Otsu\n%.0f" % D["otsu_med"], xy=(D["otsu_med"], 3.0),
                xytext=(D["otsu_med"] - 52, 6.5), fontsize=9, color=C_OTSU, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C_OTSU, lw=1.3))
    ax.annotate("the rig's fixed cut\n%.0f" % D["fixed"], xy=(D["fixed"], 1.2),
                xytext=(D["fixed"] + 14, 3.2), fontsize=9, color=C_FIX, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C_FIX, lw=1.3))
    ax.text((D["otsu_med"] + D["fixed"]) / 2, 0.19, "%.0f grey\nlevels apart"
            % (D["fixed"] - D["otsu_med"]), ha="center", fontsize=8.2, color="#8a6d00",
            fontweight="bold")

    ax.set_yscale("log")
    ax.set_ylim(0.02, 30)
    ax.set_xlim(0, 255)
    ax.set_xlabel("grey level", fontsize=9.5)
    ax.set_ylabel("share of pixels (%, log)", fontsize=9.5)
    ax.set_title("What Otsu sees — %d frames of S13 pooled" % D["n"], fontsize=10.5, color=INK)
    ax.tick_params(labelsize=9)
    _style(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "otsu_hist.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  otsu_hist.png")


def fig_frame(D=None):
    """The frame itself, and the two binaries it produces."""
    D = D or OD.load()
    g = OD.sample_frame()
    if g.shape[0] > g.shape[1]:          # stills are stored portrait; the rig sees it landscape
        g = np.rot90(g)
    _t, b_otsu = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    _t2, b_fix = cv2.threshold(g, int(D["fixed"]), 255, cv2.THRESH_BINARY)

    # Captions state what is VISIBLE, not what would make the better story. On S13 both cuts find
    # both markers — the replay record says 99.8 % either way — and the honest thing the picture
    # shows is that the GRIPS are as bright as the spray dots at both settings, so the frame
    # yields six qualifying blobs and the detector has to choose the pair. Otsu's cut simply
    # bleeds them a little wider.
    fig, axes = plt.subplots(3, 1, figsize=(6.60, 3.95))
    for ax, im, ttl, col in (
            (axes[0], g, "the frame as the camera sees it — S13, black PLA, two spray dots",
             INK),
            (axes[1], b_otsu, "at Otsu's %.0f — both markers found, and the bright GRIPS bloom "
                              "with them" % D["otsu_med"], C_OTSU),
            (axes[2], b_fix, "at the rig's %.0f — the same two markers, the grips pulled back"
             % D["fixed"], C_FIX)):
        ax.imshow(im, cmap="gray", aspect="auto", interpolation="nearest")
        ax.set_title(ttl, fontsize=8.6, color=col, pad=3)
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color("#CCCCCC")
    fig.tight_layout(h_pad=0.6)
    fig.savefig(os.path.join(FIGS, "otsu_frame.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  otsu_frame.png")


def all_figs():
    print("Otsu figures:")
    D = OD.load()
    fig_hist(D)
    fig_frame(D)
    return D


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    all_figs()
