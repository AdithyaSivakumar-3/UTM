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
    # Three short lines, nudged right: centred on the band as two lines, the leading digit
    # of "18" sat directly under the red Otsu rule and read as a stray mark.
    ax.text((D["otsu_med"] + D["fixed"]) / 2 + 1.5, 0.19, "%.0f grey\nlevels\napart"
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


def fig_explain(D=None):
    """The same histogram, explained from first principles for someone who has not met one.

    Two panels because the question "what is a grey level" is answered by NUMBERS ON PIXELS, and
    the question "what is share of pixels" is answered by the tally those numbers make. Showing the
    tally without first showing the numbers is where a histogram loses a general audience.
    """
    D = D or OD.load()
    g = OD.sample_frame()
    if g.shape[0] > g.shape[1]:
        g = np.rot90(g)

    # A patch that genuinely straddles a marker edge — SEARCHED for, not guessed at. The first
    # attempt took a window near the median bright pixel and landed wholly inside a marker: eight
    # columns of 240-odd, which shows a number per pixel but not the contrast the histogram is
    # about. This scans for the window with the widest spread of values in it.
    H, W = 6, 8
    best = None
    for r in range(0, g.shape[0] - H, 4):
        for c in range(0, g.shape[1] - W, 4):
            w = g[r:r + H, c:c + W]
            spread = int(w.max()) - int(w.min())
            if best is None or spread > best[0]:
                best = (spread, r, c)
    _sp, r0, c0 = best
    patch = g[r0:r0 + H, c0:c0 + W].astype(int)

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.6, 3.55),
                                 gridspec_kw={"width_ratios": [1.0, 1.25], "wspace": 0.22})

    a1.imshow(patch, cmap="gray", vmin=0, vmax=255, interpolation="nearest")
    for (r, c), v in np.ndenumerate(patch):
        a1.text(c, r, "%d" % v, ha="center", va="center", fontsize=8.6,
                color="black" if v > 140 else "white")
    a1.set_xticks([]); a1.set_yticks([])
    a1.set_title("STEP 1 — every pixel is just a number, 0 (black) to 255 (white)",
                 fontsize=9.8, color=INK)
    a1.set_xlabel("a real 8 × 6 patch from the frame, straddling a marker's edge", fontsize=8.8)
    for sp in a1.spines.values():
        sp.set_color("#BBBBBB")

    h = D["hist"]
    a2.fill_between(np.arange(256), h, 0, color="#9AA5AB", alpha=0.55, lw=0)
    a2.plot(np.arange(256), h, "-", color="#5A6570", lw=1.0)
    a2.axvline(D["otsu_med"], color=C_OTSU, lw=2.0)

    a2.annotate("MOST pixels are dark —\nthe specimen body", xy=(66, 2.4), xytext=(6, 7.0),
                fontsize=8.6, color=INK,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.1))
    a2.annotate("a FEW are bright —\nthe markers and the grips", xy=(196, 0.16),
                xytext=(150, 1.9), fontsize=8.6, color=INK,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.1))
    a2.annotate("hardly any in between:\nthe VALLEY", xy=(122, 0.045), xytext=(52, 0.10),
                fontsize=8.6, color="#8a6d00", fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="#8a6d00", lw=1.1))
    a2.annotate("Otsu's cut, %.0f" % D["otsu_med"], xy=(D["otsu_med"], 0.6),
                xytext=(D["otsu_med"] + 12, 1.1), fontsize=8.8, color=C_OTSU,
                fontweight="bold", arrowprops=dict(arrowstyle="->", color=C_OTSU, lw=1.2))

    a2.set_yscale("log")
    a2.set_ylim(0.02, 30)
    a2.set_xlim(0, 255)
    a2.set_xlabel("grey level — that same 0–255 number", fontsize=9.2)
    a2.set_ylabel("share of pixels (%)\nlog scale", fontsize=9.2)
    a2.set_title("STEP 2 — count how many pixels have each number", fontsize=9.8, color=INK)
    a2.tick_params(labelsize=8.8)
    _style(a2)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "otsu_explain.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  otsu_explain.png")


def all_figs():
    print("Otsu figures:")
    D = OD.load()
    fig_hist(D)
    fig_explain(D)
    fig_frame(D)
    return D


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    all_figs()
