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


def _our_preload_state():
    """When our frame 0 sits in the test, and at what force. Read, not assumed.

    The capture does not start with the test — S26's begins 10.81 s in — so the frame sidecar's
    wall-clock stamp is what places frame 0 on the load record.
    """
    import csv
    import datetime
    import glob
    sp = glob.glob(os.path.join(MC.DATA, "Specimen_S26_*"))
    if not sp:
        return None
    c = sorted(glob.glob(os.path.join(sp[0], "*.csv")))
    idx = glob.glob(os.path.join(sp[0], "**", "index.csv"), recursive=True)
    if not c or not idx:
        return None
    t0 = None
    for ln in io.open(c[0], encoding="utf-8", errors="replace"):
        if ln.startswith("# Test Date:"):
            t0 = datetime.datetime.strptime(ln.split(":", 1)[1].strip(), "%Y-%m-%d %H:%M:%S")
            break
    if t0 is None:
        return None
    row0 = next(csv.DictReader(io.open(idx[0], encoding="utf-8")))
    off = (datetime.datetime.fromisoformat(row0["pc_time_iso"]) - t0).total_seconds()
    from utm_analysis import read_csv
    rows = read_csv(c[0])
    t = np.array([r["t"] for r in rows]); F = np.array([r["F"] for r in rows])
    return off, float(np.interp(off, t, F))


def fig_setup(D=None):
    """What each machine filmed, at ONE COMMON millimetre scale.

    A common scale is the whole point: both gauges are 80 mm, so at a true scale the two marker
    spans must draw the same length, and any difference the eye sees is a difference in FIELD OF
    VIEW rather than in what is being measured. Letting each subplot auto-scale — which is what
    this did before — destroys exactly that comparison.
    """
    import glob
    mot = os.path.join(os.path.dirname(MC.MOT), "test2.chan 0.avi")
    ours = glob.glob(os.path.join(MC.DATA, "**", "Specimen_S26_*", "**", "video.avi"),
                     recursive=True)[0]
    gm, go = _first_frame(mot), _first_frame(ours)
    if gm is None or go is None:
        return
    if go.shape[0] > go.shape[1]:                 # ours is filmed upright; lay it the same way
        go = np.rot90(go)

    PPM_M, PPM_O = 2234.4 / 80.0033, 1676.3 / 80.0
    st = _our_preload_state()

    # Crop the XT-205 frame to a band the height of ours. Its sensor sees 73.6 mm vertically
    # against our 19.9, and at a true common scale that panel would be four times the height for
    # no information. The crop is stated in the title.
    band_mm = go.shape[0] / PPM_O
    msm = sorted(PP.find_markers(gm)[:2], key=lambda m: m[0])
    yc = int(np.mean([m[1] for m in msm])) if len(msm) == 2 else gm.shape[0] // 2
    half = int(round(band_mm * PPM_M / 2))
    y0 = max(0, yc - half)
    gm_c = gm[y0:min(gm.shape[0], yc + half), :]

    fig, axes = plt.subplots(2, 1, figsize=(11.6, 4.5))
    panels = [
        (axes[0], gm_c, PPM_M, y0, C_MOT,
         "MOT XT-205 — frame 0, before the pull (strain 0.0001 %%, its ramp still 15 s away)\n"
         "%d × %d px sensor, cropped vertically to match" % (gm.shape[1], gm.shape[0])),
        (axes[1], go, PPM_O, 0, C_OURS,
         ("%s — frame 0, at preload (%.0f N after tare, %.1f s into the test)\n%d × %d px, "
          "uncropped" % (RIG, st[1], st[0], go.shape[1], go.shape[0])) if st else
         "%s — frame 0, at preload" % RIG),
    ]
    xmax = max(gm_c.shape[1] / PPM_M, go.shape[1] / PPM_O) + 2

    for ax, g, ppm, yoff, col, ttl in panels:
        w_mm, h_mm = g.shape[1] / ppm, g.shape[0] / ppm
        ax.imshow(g, cmap="gray", vmin=0, vmax=255, extent=(0, w_mm, h_mm, 0))
        ax.set_aspect("equal")                    # millimetres are millimetres, both ways
        ax.set_xlim(0, xmax)
        ax.set_ylim(h_mm, 0)
        ms = sorted(PP.find_markers(g)[:2], key=lambda m: m[0])
        if len(ms) == 2:
            xa, ya = ms[0][0] / ppm, ms[0][1] / ppm
            xb, yb = ms[1][0] / ppm, ms[1][1] / ppm
            for (mx, my, mr) in ((xa, ya, ms[0][2] / ppm), (xb, yb, ms[1][2] / ppm)):
                ax.add_patch(Circle((mx, my), mr * 1.35, fill=False, ec=col, lw=1.6))
            ax.annotate("", xy=(xb, yb), xytext=(xa, ya),
                        arrowprops=dict(arrowstyle="<->", color=col, lw=1.6))
            # Pinned near the TOP of the panel, not offset from the markers. Offset from the
            # markers put it on the specimen itself, where bold red on bright white is close to
            # unreadable; the panels differ in height so a fraction of the height is what keeps
            # both captions in the dark band above the bar. The backing box makes it legible
            # whatever it lands on.
            ax.text((xa + xb) / 2, 0.11 * h_mm,
                    "80.0 mm gauge  ·  %.0f px  ·  %.1f px/mm"
                    % (np.hypot(ms[1][0] - ms[0][0], ms[1][1] - ms[0][1]), ppm),
                    ha="center", va="top", fontsize=9.5, color=col, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.28", fc="white", ec=col, lw=0.9, alpha=0.92))
        ax.set_title(ttl, fontsize=9.5, color=INK, loc="left")
        ax.set_yticks([])
        ax.set_xlabel("millimetres — BOTH PANELS AT THE SAME SCALE", fontsize=8.5, color=MUTED)
        ax.tick_params(labelsize=8)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "motpp_setup.png"), dpi=170, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    print("  motpp_setup.png")


def fig_pixels(D):
    """Same 80 mm gauge, different pixel counts — drawn so the reason is obvious.

    The pixel counts differ because the two cameras magnify differently, and for a strain that is
    irrelevant: strain is (L - Px0)/Px0, a ratio of pixels, so px/mm cancels exactly. What the
    magnification DOES buy is the size of one pixel's worth of strain, which is the honest reason
    to care about it.
    """
    L0_M, L0_O = 2234.4, 1676.3
    PPM_M, PPM_O = L0_M / 80.0033, L0_O / 80.0
    noise_pp = D["rows"][0]["noise_ue"]          # our pipeline on the XT-205's footage
    noise_s25 = next(r["noise_ue"] for r in D["rows"] if r["key"] == "S25")

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11.6, 3.9),
                                 gridspec_kw={"width_ratios": [1.35, 1.0], "wspace": 0.26})

    # ---- ONE MILLIMETRE on each camera, a tick per pixel
    for row, (ppm, name, col) in enumerate(((PPM_M, "MOT XT-205", C_MOT),
                                            (PPM_O, "%s" % RIG, C_OURS))):
        y = 1 - row
        ax.add_patch(plt.Rectangle((0, y - 0.17), 1.0, 0.34, fill=False, ec=col, lw=2.0))
        n = int(round(ppm))
        for i in range(n + 1):
            ax.plot([i / ppm, i / ppm], [y - 0.17, y + 0.17], "-", color=col, lw=0.7, alpha=0.75)
        ax.text(1.045, y, "%s\n%.1f px per mm" % (name, ppm), va="center", ha="left",
                fontsize=10, color=col, fontweight="bold")
        ax.text(0.5, y - 0.245, "%d pixels across ONE millimetre" % n, ha="center", va="top",
                fontsize=9, color=INK)
    ax.set_xlim(-0.03, 1.62); ax.set_ylim(-0.55, 1.45)
    ax.set_xticks([0, 0.5, 1.0]); ax.set_xticklabels(["0", "0.5 mm", "1 mm"], fontsize=9)
    ax.set_yticks([])
    ax.set_title("The same millimetre, sampled two ways.\nThat is the entire reason the pixel "
                 "counts differ.", fontsize=10.5, color=INK)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)

    # ---- what the magnification buys, and what it does not
    labels = ["MOT XT-205\n%d px gauge" % round(L0_M), "%s\n%d px gauge" % (RIG, round(L0_O))]
    per_px = [1e6 / L0_M, 1e6 / L0_O]
    got = [noise_pp, noise_s25]
    x = np.arange(2); w = 0.36
    b1 = bx.bar(x - w / 2, per_px, w, color=[C_MOT, C_OURS], alpha=0.45,
                label="one WHOLE pixel")
    b2 = bx.bar(x + w / 2, got, w, color=[C_MOT, C_OURS],
                label="actually achieved (sub-pixel)")
    for r, v in list(zip(b1, per_px)) + list(zip(b2, got)):
        bx.text(r.get_x() + r.get_width() / 2, v * 1.12, "%.0f" % v if v > 50 else "%.1f" % v,
                ha="center", fontsize=9, color=INK, fontweight="bold")
    bx.set_yscale("log"); bx.set_ylim(2, 5000)   # headroom so the bar labels clear the legend
    bx.set_xticks(x); bx.set_xticklabels(labels, fontsize=9)
    bx.set_ylabel("strain (µε)")
    bx.set_title("What the extra magnification buys:\na finer pixel — but sub-pixel buys far more",
                 fontsize=10.5, color=INK)
    bx.legend(fontsize=8.4, loc="upper right", framealpha=0.95)
    _style(bx)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "motpp_pixels.png"), dpi=200, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    print("  motpp_pixels.png")


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


def fig_scalecheck(D):
    """The scale check, given room to explain itself.

    Left: the two routes to ONE video's frame rate. Right: the calibration of the argument — feed
    the check a known scale error and it reports that error back, which is what makes agreement
    mean something rather than being a foregone conclusion.
    """
    cr = D["crossings"]
    sens = D["scale_sensitivity"]
    tx = np.array(cr["t"]); fx = np.array(cr["frame"])
    inferred, daq = D["fps_from_crossings"], D["fps_daq"]

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11.4, 4.0),
                                 gridspec_kw={"width_ratios": [1.0, 1.0], "wspace": 0.24})

    ax.plot(tx, fx, "o", color="#7048e8", ms=7, label="the 9 shared strain levels")
    xs = np.array([tx.min(), tx.max()])
    ax.plot(xs, inferred * xs + cr["fit_intercept"], "-", color="#7048e8", lw=1.6,
            label="INFERRED from strain: %.3f fps" % inferred)
    ax.plot(xs, daq * xs + cr["fit_intercept"], "--", color=INK, lw=1.6,
            label="RECORDED in the log: %.3f fps" % daq)
    ax.set_xlabel("time on the XT-205 clock (s)")
    ax.set_ylabel("frame number in the XT-205's video")
    ax.set_title("Both lines describe ONE video — the XT-205's.\nNot two machines.",
                 fontsize=10.5, color=INK)
    ax.legend(fontsize=8.6, loc="upper left", framealpha=0.95)
    _style(ax)

    k = np.array([r["k"] for r in sens])
    got = np.array([r["recovered_k"] for r in sens])
    bx.plot([k.min() - 0.02, k.max() + 0.02], [k.min() - 0.02, k.max() + 0.02], "--",
            color=MUTED, lw=1.2, label="perfect detection")
    bx.plot(k, got, "o-", color=BAD, lw=1.8, ms=8, label="what the check reports")
    _i = int(np.argmin(np.abs(k - 1.0)))
    bx.plot([k[_i]], [got[_i]], "o", ms=15, mfc="none", mec=GOOD, mew=2.4)
    bx.annotate("the real data:\nk = %.4f" % got[_i], xy=(k[_i], got[_i]),
                xytext=(k[_i] - 0.075, got[_i] + 0.055), fontsize=9, color=GOOD,
                fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=GOOD, lw=1.3))
    bx.set_xlabel("scale error deliberately injected into our strain")
    bx.set_ylabel("scale error the check reports")
    bx.set_title("Does the check actually detect an error?\nStretch the strain by k and it says k.",
                 fontsize=10.5, color=INK)
    bx.legend(fontsize=8.6, loc="lower right", framealpha=0.95)
    _style(bx)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "mot_scalecheck.png"), dpi=200, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    print("  mot_scalecheck.png")


def all_figs():
    """Re-run the ANALYSIS, then draw everything that depends on it.

    The analysis is rebuilt here rather than assumed fresh. mot_postproc_compare.py owns both the
    cache these figures read AND mot_postproc_compare.png, so leaving it out meant a deck build
    refreshed two of the three figures and silently kept a stale third — which is exactly what
    happened after its axis labels were rewritten: the slide still carried the old wording with
    nothing to say so.
    """
    import mot_postproc_compare as MP
    print("MOT post-processing analysis + figures:")
    MP.build()                      # writes the cache and mot_postproc_compare.png
    D = load()
    fig_setup()
    fig_share(D)
    fig_pixels(D)
    fig_scalecheck(D)
    return D


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    all_figs()
