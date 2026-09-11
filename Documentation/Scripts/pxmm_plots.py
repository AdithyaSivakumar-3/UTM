"""Figures for the px/mm reasoning.

  pxmm_tradeoff.png   the field of view each magnification leaves, and where each machine sits
  pxmm_optics.png     px/mm and field of view against where the camera stands, for the 25 mm lens

Every panel is arithmetic on the rig's own crop, its own lens and the measured gauges — nothing
drawn to illustrate a point that was not first computed in pxmm_data.py.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                       # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
FIGS = os.path.abspath(os.path.join(HERE, "..", "figures"))
sys.path.insert(0, HERE)

import pxmm_data as PX                                                # noqa: E402

INK, GRID, MUTED = "#212529", "#DDDDDD", "#666666"
C_MOT, C_OURS = "#d62728", "#1f77b4"
GOOD, BAD = "#2e7d32", "#c0392b"


def _style(ax):
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def fig_tradeoff(D=None):
    D = D or PX.load()
    o, m = D["ours"], D["mot"]

    # The slide gives this 12.55 x 2.92 in. Matching that aspect is what keeps the figure from
    # being height-limited and floating in the middle of two inches of white space.
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(13.0, 3.05),
                                 gridspec_kw={"width_ratios": [1.30, 1.0], "wspace": 0.30})

    # ---- what each frame actually holds, in millimetres, to one scale
    for row, (d, name, col) in enumerate(((m, "MOT XT-205", C_MOT),
                                          (o, "PPD-UTM", C_OURS))):
        y = 1 - row
        fov, gauge_mm = d["fov_mm"], 80.0
        pad = (fov - gauge_mm) / 2.0
        ax.barh(y, fov, height=0.44, color="#e9ecef", edgecolor=col, lw=1.6)
        ax.barh(y, gauge_mm, left=pad, height=0.44, color=col, alpha=0.85)
        ax.text(fov / 2, y, "80 mm gauge", ha="center", va="center", fontsize=9.5,
                color="white", fontweight="bold")
        # The spare margin is written in the caption, not inside the bar: on the XT-205 that
        # margin is 4 mm wide and no legible text fits in it.
        ax.text(fov + 2.5, y, "%s  —  %.1f px/mm\n%.1f mm of frame, so %.1f mm spare each side\n"
                             "markers leave the frame at %.1f %% strain"
                % (name, d["ppm"], fov, pad, 100 * d["strain_to_edge"]),
                ha="left", va="center", fontsize=8.8, color=col, fontweight="bold")
    ax.set_xlim(0, 215); ax.set_ylim(-0.55, 1.55)
    ax.set_yticks([]); ax.set_xlabel("millimetres of specimen the sensor can see", fontsize=9)
    ax.set_xticks([0, 25, 50, 75, 100, 125])
    ax.tick_params(labelsize=8.5)
    ax.set_title("More pixels per millimetre means LESS specimen in frame — "
                 "that is the whole trade.", fontsize=10, color=INK)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)

    # ---- the trade as a curve, on OUR sensor, with both operating points on it
    N, half = D["roi"][2], o["box_half"]
    p = np.linspace(8, 30, 400)
    gauge_px = 80.0 * p
    usable = (N - gauge_px) / 2.0 - (half + 2)
    lim = np.clip(2.0 * usable / gauge_px, 0, None) * 100
    bx.plot(p, lim, "-", color=INK, lw=2.0)
    bx.fill_between(p, 0, lim, color=C_OURS, alpha=0.10)

    bx.axhline(100 * D["ef_s26"], color=GOOD, ls="--", lw=1.4)
    bx.text(8.4, 100 * D["ef_s26"] + 1.6, "PLA fractures here (%.1f %%)" % (100 * D["ef_s26"]),
            fontsize=8.2, color=GOOD, fontweight="bold")

    # The curve is steep on the left and flat on the right, so each callout goes into the clear
    # space on ITS side — the blue one under the steep part, the red one out to the right of the
    # tail — and neither the text nor its leader crosses the curve.
    bx.plot([o["ppm"]], [100 * o["strain_to_edge"]], "o", ms=10, color=C_OURS, zorder=5)
    bx.annotate("PPD-UTM sits here\n%.1f px/mm, good to %.0f %% strain"
                % (o["ppm"], 100 * o["strain_to_edge"]),
                xy=(o["ppm"] - 0.55, 100 * o["strain_to_edge"] + 0.7), xytext=(8.5, 38),
                ha="left", va="center", fontsize=8.6, color=C_OURS, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C_OURS, lw=1.3,
                                connectionstyle="arc3,rad=-0.15"))
    # The XT-205's magnification, put on OUR curve — where it lands on zero, because at that
    # magnification a 75 px box no longer fits between the gauge and the frame edge at all.
    bx.plot([m["ppm"]], [0.0], "D", ms=9, color=C_MOT, zorder=5)
    bx.annotate("at %.1f px/mm our own\nframe would give %.0f %%"
                % (m["ppm"], 0.0), xy=(m["ppm"] - 0.25, 1.1), xytext=(21.8, 27),
                ha="left", va="center", fontsize=8.6, color=C_MOT, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C_MOT, lw=1.3,
                                connectionstyle="arc3,rad=-0.2"))
    bx.set_xlabel("pixels per millimetre", fontsize=9)
    bx.set_ylabel("strain at which a marker\nleaves the frame (%)", fontsize=9)
    bx.set_title("On our own %d px crop:\nthe resolution we could gain is strain we could not "
                 "measure" % N, fontsize=10, color=INK)
    bx.set_ylim(0, 62); bx.set_xlim(8, 30)
    # The 30 tick sits exactly on the spine and renders as a clipped "30." — stop the labels short.
    bx.set_xticks([10, 15, 20, 25])
    bx.tick_params(labelsize=8.5)
    _style(bx)

    fig.subplots_adjust(left=0.038, right=0.995, top=0.86, bottom=0.155)
    fig.savefig(os.path.join(FIGS, "pxmm_tradeoff.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  pxmm_tradeoff.png")
    return D


def fig_optics(D=None):
    """px/mm and field of view as functions of where the camera stands, for the 25 mm lens.

    This is the answer to "is it a camera property". It is, exactly: px/mm = M / pitch, and M is
    fixed by the lens and the distance. Both panels are the same thin-lens relation read two ways,
    so they share an x axis — one shows what is gained, the other what it costs.
    """
    D = D or PX.load()
    o, m, opt = D["ours"], D["mot"], D["optics"]
    N = D["roi"][2]

    wd = np.linspace(210.0, 620.0, 500)
    mag = 1.0 / (wd / opt["f_mm"] - 1.0)            # invert WD = f(1 + 1/M)
    ppm = mag / (opt["pitch_um"] * 1e-3)
    fov = N / ppm

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(13.0, 3.05),
                                 gridspec_kw={"width_ratios": [1.0, 1.0], "wspace": 0.22})

    # ---- what the distance buys
    ax.plot(wd, ppm, "-", color=INK, lw=2.0)
    # The curve falls away to the right, so the empty quadrant is upper-right — both callouts go
    # there and lead back to their point, rather than sitting on top of the curve.
    for d, lab, col, mk, ty in ((opt["mot"], "to match the XT-205", C_MOT, "D", 34.0),
                                (opt["ours"], "PPD-UTM, as built", C_OURS, "o", 25.5)):
        p = d["mag"] / (opt["pitch_um"] * 1e-3)
        ax.plot([d["obj_mm"]], [p], mk, ms=10, color=col, zorder=5)
        ax.vlines(d["obj_mm"], 0, p, color=col, ls=":", lw=1.2)
        ax.annotate("%s\n%.0f mm  →  %.1f px/mm" % (lab, d["obj_mm"], p),
                    xy=(d["obj_mm"] + 5, p + 0.5), xytext=(432, ty), ha="left", va="center",
                    fontsize=8.6, color=col, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=col, lw=1.2))
    ax.set_xlabel("lens-to-specimen distance (mm)", fontsize=9)
    ax.set_ylabel("pixels per millimetre", fontsize=9)
    ax.set_ylim(6, 42); ax.set_xlim(210, 620)
    ax.tick_params(labelsize=8.5)
    ax.set_title("px/mm is not a setting — it is where the camera stands\n"
                 "(%.0f mm lens, %.2f µm pixels)" % (opt["f_mm"], opt["pitch_um"]),
                 fontsize=10, color=INK)
    _style(ax)

    # ---- and what it costs, on the same axis
    bx.plot(wd, fov, "-", color=INK, lw=2.0)
    bx.axhspan(0, 80.0, color=BAD, alpha=0.10)
    bx.axhline(80.0, color=BAD, ls="--", lw=1.4)
    bx.text(615, 72, "below this the 80 mm gauge does not fit in the frame at all",
            ha="right", va="top", fontsize=8.4, color=BAD, fontweight="bold")
    # Two points on a rising curve with a measure drawn between them leaves very little clear
    # space, so these are labelled directly — short text, one on each side of its marker — and
    # no leader lines to cross each other.
    for d, col, mk, dx, dy, ha in ((opt["mot"], C_MOT, "D", -11, 26, "right"),
                                   (opt["ours"], C_OURS, "o", 11, -22, "left")):
        f = N / (d["mag"] / (opt["pitch_um"] * 1e-3))
        bx.plot([d["obj_mm"]], [f], mk, ms=10, color=col, zorder=5)
        bx.vlines(d["obj_mm"], 0, f, color=col, ls=":", lw=1.2)
        bx.text(d["obj_mm"] + dx, f + dy, "%.0f mm" % f, ha=ha, va="center", fontsize=9.5,
                color=col, fontweight="bold")
    bx.annotate("", xy=(opt["mot"]["obj_mm"], 178), xytext=(opt["ours"]["obj_mm"], 178),
                arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1.4))
    bx.text(0.5 * (opt["mot"]["obj_mm"] + opt["ours"]["obj_mm"]), 172,
            "%.0f mm of camera travel is the whole difference" % opt["move_closer_mm"],
            ha="center", va="top", fontsize=8.6, color=MUTED, fontweight="bold")
    bx.set_xlabel("lens-to-specimen distance (mm)", fontsize=9)
    bx.set_ylabel("field of view along the specimen (mm)", fontsize=9)
    bx.set_ylim(0, 205); bx.set_xlim(210, 620)
    bx.tick_params(labelsize=8.5)
    bx.set_title("the same distance, read as what it costs", fontsize=10, color=INK)
    _style(bx)

    fig.subplots_adjust(left=0.048, right=0.995, top=0.855, bottom=0.155)
    fig.savefig(os.path.join(FIGS, "pxmm_optics.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  pxmm_optics.png")
    return D


def all_figs():
    print("px/mm figures:")
    D = PX.build()
    fig_tradeoff(D)
    fig_optics(D)
    return D


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    all_figs()
