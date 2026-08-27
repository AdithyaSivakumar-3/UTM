"""Figures for the DIC position-estimator slides.

  est_whatfor.png     what an estimator is FOR: the whole-pixel staircase against the real curve
  est_methods.png     the four candidate estimators, drawn on a real marker
  est_box.png         why the patch must be wider than the marker — the sharp threshold at 1x r
  est_compare.png     noise per estimator on both specimens, against the live rig
  est_threshold.png   how far each estimator's centre drifts as the binarising level is swept
  est_accuracy.png    the chosen estimator against the live rig, over a whole test

Every number comes from documentation/estimator_measurements.json, which is written by
estimator_data.py from the recorded S25/S26 video. Nothing here re-derives a measurement; if a
figure and the cache disagree, the cache is right and the figure is broken.
"""
import io
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                       # noqa: E402
from matplotlib.patches import Circle, Rectangle                      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FIGS = os.path.abspath(os.path.join(HERE, "..", "figures"))
CACHE = os.path.abspath(os.path.join(HERE, "..", "estimator_measurements.json"))
sys.path.insert(0, os.path.abspath(os.path.join(ROOT, "Software", "UTM_PyQt6")))

import cv2                                                            # noqa: E402
import utm_postproc as PP                                             # noqa: E402

GRID, MUTED, INK = "#DDDDDD", "#666666", "#212529"
C_CORR, C_BIN, C_W, C_RIG = "#e08a1e", "#c0392b", "#1f6fb4", "#6c757d"
GOOD, BAD = "#2e7d32", "#c0392b"


def _style(ax):
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def load():
    return json.load(io.open(CACHE, encoding="utf-8"))


def _save(fig, name):
    fig.savefig(os.path.join(FIGS, name), dpi=200, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    print("  " + name)


def _video(spec):
    import glob
    return glob.glob(os.path.join(ROOT, "Software", "UTM_PyQt6", "Test data", "**",
                                  "Specimen_%s_*" % spec, "**", "video.avi"), recursive=True)[0]


# ================================================================== 0. what an estimator is FOR
def fig_whatfor(D):
    """The staircase. A tracker that returns whole pixels cannot resolve the elastic region.

    Left: the rig's own strain against what the SAME marker separation would have produced if the
    position had been rounded to the nearest pixel. Right: what that quantum is worth in strain,
    against the noise floor we actually achieve.
    """
    a = D["accuracy"]["S26"]
    t = np.array(a["post_t"])
    e = np.array(a["post_e"])
    l0 = D["method"]["S26"]["auto"]["l0"]
    m = (e > 0) & (e < 0.006)
    t, e = t[m], e[m]

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11.6, 4.0),
                                 gridspec_kw={"width_ratios": [1.55, 1]})

    # Round the SEPARATION to the nearest whole pixel and see what survives.
    L = l0 * (1 + e)
    e_q = (np.round(L) - round(l0)) / round(l0)
    ax.step(t, e_q * 100, where="post", color=BAD, lw=1.6,
            label="whole-pixel positions — a %d µε staircase" % round(1e6 / l0))
    ax.plot(t, e * 100, color=C_W, lw=2.0, label="sub-pixel positions (what we use)")
    ax.set_xlabel("time (s)"); ax.set_ylabel("DIC strain (%)")
    ax.set_title("S26, the elastic region: the same marker pair,\nread two ways",
                 fontsize=10.5, color=INK)
    ax.legend(fontsize=8.5, loc="upper left", framealpha=0.95)
    _style(ax)

    labels = ["whole pixel\n(no estimator)", "live rig\nS26", "post-processing\nS26"]
    vals = [1e6 / l0, D["live_rig"]["S26"], D["method"]["S26"]["auto"]["noise_ue"]]
    cols = [BAD, C_RIG, C_W]
    b = bx.bar(labels, vals, color=cols, width=0.6)
    bx.set_yscale("log")
    bx.set_ylabel("strain resolution / noise (µε)")
    bx.set_title("What one pixel is worth on a %d px gauge" % round(l0), fontsize=10.5, color=INK)
    for r, v in zip(b, vals):
        bx.text(r.get_x() + r.get_width() / 2, v * 1.15, "%.0f µε" % v,
                ha="center", fontsize=9.5, fontweight="bold", color=INK)
    bx.set_ylim(5, 2000)
    _style(bx)
    fig.tight_layout()
    _save(fig, "est_whatfor.png")


# ================================================================== 1. the candidate methods
def fig_methods(D):
    """The four candidates drawn on a real marker, so the geometry is visible rather than asserted.

    All four answer the same question — where is this dot, to a fraction of a pixel — and they
    differ only in which pixels they let vote.
    """
    g = PP.read_frame(_video("S26"), 0)
    ms = sorted(PP.find_markers(g)[:2], key=lambda m: m[1])
    cx, cy, r = ms[0][0], ms[0][1], ms[0][2]
    half = int(round(1.25 * r))
    x0, y0 = int(cx) - half, int(cy) - half
    patch = g[y0:y0 + 2 * half + 1, x0:x0 + 2 * half + 1]
    thr = PP.reference_threshold(patch, True)
    _, binimg = cv2.threshold(patch, thr, 255, cv2.THRESH_BINARY_INV)

    fig, axes = plt.subplots(1, 4, figsize=(12.4, 3.5))
    n = patch.shape[0]

    # (a) correlation — the whole patch votes, through one peak
    axes[0].imshow(patch, cmap="gray", vmin=0, vmax=255)
    axes[0].add_patch(Rectangle((0.5, 0.5), n - 2, n - 2, fill=False, ec=C_CORR, lw=2.2))
    axes[0].set_title("(a) correlation\nwhole patch → one peak", fontsize=9.5, color=C_CORR)

    # (b) binary contour centroid — every pixel inside the cut, equally
    axes[1].imshow(binimg, cmap="gray")
    axes[1].set_title("(b) binary centroid\nevery pixel inside the cut,\nweighted equally",
                      fontsize=9.5, color=C_BIN)

    # (c) intensity-weighted — the same pixels, weighted by how dark they are
    # The edge width is measured, not asserted: 10 %-to-90 % rise on the mid-row profile.
    mask = (binimg > 0).astype(np.uint8) * 255
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))
    bg = float(np.median(patch[mask == 0])) if (mask == 0).any() else 255.0
    w = np.where(mask > 0, bg - patch.astype(np.float32), 0.0)
    np.clip(w, 0, None, out=w)
    axes[2].imshow(w, cmap="magma")
    axes[2].set_title("(c) contour + intensity weight  ← CHOSEN\ninterior at full weight, edge GRADED\n(no hard cut anywhere)",
                      fontsize=9.5, color=C_W, fontweight="bold")

    # (d) the edge profile the weighting is reading
    mid = patch[patch.shape[0] // 2, :].astype(float)
    lo, hi = mid.min(), mid.max()
    rise = mid[:n // 2]
    xs = np.arange(len(rise))
    p10 = np.interp(lo + 0.10 * (hi - lo), rise[::-1], xs[::-1])
    p90 = np.interp(lo + 0.90 * (hi - lo), rise[::-1], xs[::-1])
    width = abs(p10 - p90)
    axes[3].plot(mid, color=INK, lw=1.8)
    axes[3].axhline(thr, color=C_BIN, ls="--", lw=1.4, label="binary cut (%d)" % thr)
    axes[3].axvspan(min(p10, p90), max(p10, p90), color=C_W, alpha=0.25,
                    label="edge, %.0f px wide" % width)
    axes[3].set_xlabel("pixel across the marker", fontsize=9)
    axes[3].set_ylabel("grey level", fontsize=9)
    axes[3].set_title("(d) the marker edge is %.0f px of GRADIENT —\nthe binary cut throws all of it away"
                      % width, fontsize=9.5, color=INK)
    axes[3].legend(fontsize=7.6, loc="center", framealpha=0.95)
    axes[3].set_ylim(lo - 8, hi + 30)
    _style(axes[3])
    for a in axes[:3]:
        a.set_xticks([]); a.set_yticks([])
    fig.tight_layout()
    _save(fig, "est_methods.png")


# ================================================================== 2. the patch-size threshold
def fig_box(D):
    """Noise against patch size, in units of the marker's own radius.

    The x axis is deliberately the RATIO, not pixels, because that is what makes the two specimens
    fall on the same curve and what makes the rule transferable to a different marker size.
    """
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11.8, 4.1),
                                 gridspec_kw={"width_ratios": [1.35, 1]})
    for spec, col, mk in (("S25", C_W, "o"), ("S26", C_CORR, "s")):
        rows = D["box"][spec]["rows"]
        x = [r["ratio"] for r in rows]
        y = [r["noise_ue"] for r in rows]
        ax.plot(x, y, mk + "-", color=col, lw=1.8, ms=7, label="%s (marker r = %.0f px)"
                % (spec, D["box"][spec]["marker_radius"]))
    ax.axvspan(0.3, 1.0, color=BAD, alpha=0.07)
    ax.axvspan(1.0, 1.2, color="#f0a030", alpha=0.10)
    ax.axvspan(1.2, 1.6, color=GOOD, alpha=0.07)
    ax.axvline(1.0, color=INK, ls="--", lw=1.3)
    ax.axvline(1.2, color=INK, ls=":", lw=1.3)
    ax.text(0.63, 60, "patch lies INSIDE the dot —\nnothing but flat black to lock onto",
            fontsize=8.8, color=BAD, ha="center", va="top")
    ax.text(1.40, 2.2e3, "patch clears the dot's EDGE —\nposition is constrained",
            fontsize=8.8, color=GOOD, ha="center")
    ax.annotate("tracking wanders inside\nthe featureless interior",
                xy=(0.53, 9.8e3), xytext=(0.80, 1.1e4), fontsize=8.2, color=BAD,
                ha="left", va="center",
                arrowprops=dict(arrowstyle="->", color=BAD, lw=1.1))
    ax.set_yscale("log")
    ax.set_xlabel("patch half-width ÷ marker radius")
    ax.set_ylabel("noise over the fixed window (µε)")
    ax.set_title("Patch size is the biggest single lever — and it has a threshold, not a trend",
                 fontsize=10.5, color=INK)
    ax.legend(fontsize=8.5, loc="lower left")
    ax.set_ylim(5, 3e4)
    _style(ax)

    # the two regimes, averaged
    ins, out = [], []
    for spec in ("S25", "S26"):
        for r in D["box"][spec]["rows"]:
            (ins if r["ratio"] < 1.0 else out if r["ratio"] >= 1.2 else []).append(r["noise_ue"])
    labels = ["patch inside the dot\n(ratio < 1.0)", "patch clear of the edge\n(ratio ≥ 1.2)"]
    vals = [float(np.median(ins)), float(np.median(out))]
    b = bx.bar(labels, vals, color=[BAD, GOOD], width=0.55)
    bx.set_yscale("log"); bx.set_ylim(5, 3e3)
    bx.set_ylabel("median noise (µε)")
    bx.set_title("Median over both specimens", fontsize=10.5, color=INK)
    for r, v in zip(b, vals):
        bx.text(r.get_x() + r.get_width() / 2, v * 1.2, "%.0f µε" % v, ha="center",
                fontsize=11, fontweight="bold", color=INK)
    bx.text(0.5, 700, "≈ %.0f× quieter" % (vals[0] / vals[1]), ha="center", fontsize=12.5,
            fontweight="bold", color=INK)
    _style(bx)
    fig.tight_layout()
    _save(fig, "est_box.png")


# ================================================================== 3. estimator vs estimator
def fig_compare(D):
    """Noise per estimator, both specimens, with the live rig for scale.

    Two specimens is the whole point of the figure. A single specimen would have made correlation
    look either best or worst depending on which one was picked.
    """
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11.8, 4.1),
                                 gridspec_kw={"width_ratios": [1.3, 1]})
    keys = ["correlation", "rig", "auto"]
    names = ["correlation\nonly", "binary contour\ncentroid (rig form)", "contour + intensity\nweight  (CHOSEN)"]
    cols = [C_CORR, C_BIN, C_W]
    w, xs = 0.36, np.arange(3)
    for i, (spec, hatch) in enumerate((("S25", ""), ("S26", "//"))):
        v = [D["method"][spec][k]["noise_ue"] for k in keys]
        b = ax.bar(xs + (i - 0.5) * w, v, w, color=cols, hatch=hatch,
                   edgecolor="white", lw=0.8, label=spec)
        for r, val in zip(b, v):
            ax.text(r.get_x() + r.get_width() / 2, val + 0.6, "%.1f" % val, ha="center",
                    fontsize=8.8, color=INK)
    live = np.mean([D["live_rig"][s] for s in ("S25", "S26")])
    ax.axhline(live, color=C_RIG, ls="--", lw=1.6)
    ax.text(-0.42, live + 0.7, "live rig  %.0f µε" % live, fontsize=8.8, color=C_RIG,
            ha="left", fontweight="bold")
    ax.set_xticks(xs); ax.set_xticklabels(names, fontsize=9)
    ax.set_ylabel("noise over the fixed window (µε)")
    ax.set_title("Left bar S25, hatched bar S26 — the SAME frames, the same window",
                 fontsize=10.5, color=INK)
    ax.legend(fontsize=8.5, loc="upper right", framealpha=0.95, ncol=2)
    ax.set_ylim(0, 36)
    _style(ax)

    # worst case per estimator: the number that should decide the choice
    worst = [max(D["method"][s][k]["noise_ue"] for s in ("S25", "S26")) for k in keys]
    b = bx.bar(["correlation", "binary", "weighted"], worst, color=cols, width=0.6)
    for r, v in zip(b, worst):
        bx.text(r.get_x() + r.get_width() / 2, v + 0.5, "%.1f µε" % v, ha="center",
                fontsize=10.5, fontweight="bold", color=INK)
    bx.set_ylabel("WORST of the two specimens (µε)")
    bx.set_title("An estimator is chosen on its worst case,\nnot its best", fontsize=10.5, color=INK)
    bx.set_ylim(0, 36)
    _style(bx)
    fig.tight_layout()
    _save(fig, "est_compare.png")


# ================================================================== 4. threshold robustness
def fig_threshold(D):
    """How far the estimated centre moves as the binarising level is swept 120–190.

    A free parameter that moves the answer is a free parameter that has to be tuned per specimen.
    The point of the weighting is that it stops being one.
    """
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11.8, 4.0),
                                 gridspec_kw={"width_ratios": [1.35, 1]})
    for spec, ls in (("S25", "-"), ("S26", "--")):
        t = D["threshold"][spec]
        lv = np.array(t["levels"], float)
        for key, col, nm in (("binary_y", C_BIN, "binary centroid"),
                             ("weighted_y", C_W, "contour + intensity weight")):
            y = np.array([np.nan if v is None else v for v in t[key]], float)
            y = y - np.nanmean(y)
            ax.plot(lv, y, ls, color=col, lw=1.9,
                    label="%s — %s" % (nm, spec))
    ax.set_xlabel("binarising grey level")
    ax.set_ylabel("estimated marker centre, y (px, mean removed)")
    ax.set_title("Sweep the one free parameter and watch the answer move",
                 fontsize=10.5, color=INK)
    ax.legend(fontsize=8, loc="upper left", ncol=2, framealpha=0.95)
    ax.set_ylim(-0.62, 0.72)
    _style(ax)

    l0 = D["threshold"]["S25"]["l0"]
    xs = np.arange(2); w = 0.36
    for i, (spec, hatch) in enumerate((("S25", ""), ("S26", "//"))):
        t = D["threshold"][spec]
        v = [t["binary_spread_px"], t["weighted_spread_px"]]
        b = bx.bar(xs + (i - 0.5) * w, v, w, color=[C_BIN, C_W], hatch=hatch,
                   edgecolor="white", lw=0.8, label=spec)
        for r, val in zip(b, v):
            bx.text(r.get_x() + r.get_width() / 2, val + 0.02,
                    "%.3f px\n%.0f µε" % (val, val / l0 * 1e6), ha="center", fontsize=8.4,
                    color=INK)
    bx.set_xticks(xs); bx.set_xticklabels(["binary\ncentroid", "contour + intensity\nweight"],
                                          fontsize=9)
    bx.set_ylabel("total movement over the sweep (px)")
    bx.set_title("Weighting cuts the sensitivity ~2.5×", fontsize=10.5, color=INK)
    bx.legend(fontsize=8.5)
    bx.set_ylim(0, 1.18)
    _style(bx)
    fig.tight_layout()
    _save(fig, "est_threshold.png")


# ================================================================== 5. against the live rig
def fig_accuracy(D):
    """The chosen estimator re-measuring a whole test, against the rig's own live DIC.

    Precision is what the other figures measure. This one is the check that being quiet has not
    been bought by being wrong.
    """
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11.8, 4.1),
                                 gridspec_kw={"width_ratios": [1.4, 1]})
    for spec, col in (("S25", C_W), ("S26", C_CORR)):
        a = D["accuracy"][spec]
        lt, le = np.array(a["live_t"]), np.array(a["live_e"])
        pt, pe = np.array(a["post_t"]), np.array(a["post_e"])
        # Stop a whisker BEFORE fracture: the last sample is the markers flying apart, and a
        # 20 % spike compresses the part of the curve the comparison is actually about.
        cut = a["t_fr"] - 1.0
        m = lt <= cut
        ax.plot(lt[m], (le[m] - a["base"]) * 100, color=col, lw=3.0, alpha=0.32,
                label="%s — live rig" % spec)
        k = pt <= cut
        ax.plot(pt[k], pe[k] * 100, color=col, lw=1.4, ls="--",
                label="%s — post-processed" % spec)
    ax.set_xlabel("time (s)"); ax.set_ylabel("DIC strain (%)")
    ax.set_title("Same video, same markers, measured twice\n(to 1 s before fracture)",
                 fontsize=10.5, color=INK)
    ax.legend(fontsize=8.3, loc="upper left", framealpha=0.95)
    _style(ax)

    xs = np.arange(2); w = 0.35
    rms = [D["accuracy"][s]["rms_ue"] for s in ("S25", "S26")]
    mean = [abs(D["accuracy"][s]["mean_ue"]) for s in ("S25", "S26")]
    bx.bar(xs - w / 2, mean, w, color=C_RIG, label="mean offset |µε|")
    bx.bar(xs + w / 2, rms, w, color=C_W, label="scatter about it (µε)")
    for i in range(2):
        bx.text(i - w / 2, mean[i] + 12, "%.0f" % mean[i], ha="center", fontsize=9.5, color=INK)
        bx.text(i + w / 2, rms[i] + 12, "%.0f" % rms[i], ha="center", fontsize=9.5, color=INK)
    bx.set_xticks(xs); bx.set_xticklabels(["S25", "S26"])
    bx.set_ylabel("difference from the live rig (µε)")
    bx.set_title("Reproducible on both specimens:\n≈ −0.05 % offset, not scatter",
                 fontsize=10.5, color=INK)
    bx.legend(fontsize=8.5)
    bx.set_ylim(0, 700)
    _style(bx)
    fig.tight_layout()
    _save(fig, "est_accuracy.png")


def all_figs():
    D = load()
    print("estimator figures (cache measured %s):" % D["measured"])
    fig_whatfor(D)
    fig_methods(D)
    fig_box(D)
    fig_compare(D)
    fig_threshold(D)
    fig_accuracy(D)
    return D


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    all_figs()
