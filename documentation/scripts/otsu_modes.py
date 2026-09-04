"""Otsu is not a black-specimen method, and it is not a "method" in the sense the question implies.

THREE THINGS THIS SETTLES, all measured on the rig's own saved frames.

1. OTSU WORKS ON A WHITE SPECIMEN TOO. The rig's White preset carries THRESH_BINARY_INV; every
   Otsu call in the app does `base = ttype & ~THRESH_OTSU` then `base | THRESH_OTSU`, so the
   polarity and the Otsu flag are orthogonal. S24-S26 are light-bodied - mean grey ~172 against
   S13's 79 - and Otsu lands at 156-158 with margins on both sides that are WIDER than on black.

2. THE MARKERS DO NOT SET THE CUT - ON EITHER POLARITY. Paint the two markers out with the body's
   own grey and recompute: the cut moves by 0-1 grey level. Otsu is splitting the two DOMINANT
   populations (specimen against background on white, specimen against grips on black). The
   markers are 0.4-0.9 % of the frame and cannot move the optimum. They survive because they land
   on the far side of a boundary chosen without reference to them.

   That is a stronger reason not to default to Otsu than "the scene changed": on PETG, Otsu was
   never optimising for the thing that matters, so when the dominant populations shifted the
   by-product went with them.

3. WHAT THE ALTERNATIVES ACTUALLY ARE. Otsu is a rule for choosing the threshold NUMBER inside the
   binary method. It is not an alternative to "the intensity method" - those sit at different
   levels. Binary blob tracking (what the rig does) throws the grey levels away at the threshold;
   an intensity-weighted centroid keeps them for sub-pixel position; full intensity correlation -
   true DIC - never thresholds at all and returns a field rather than one number. The gain from
   tier 2 is measured here rather than asserted: 1.09x on black, 1.31x on white.

WHAT IS NOT COMPUTED HERE: marker-detection RATES. Reimplementing detect_blobs produced 36.7 %
against a validated 99.8 % once already in this project. Rates stay quoted from dic_replay.

The frame loops are slow (hundreds of PNGs), so results are cached to otsu_modes_cache.json and
the deck build reads that. Delete the file to force a recompute.
"""
import glob
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                       # noqa: E402

import cv2                                                            # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.abspath(os.path.join(HERE, "..", "figures"))
CACHE = os.path.join(HERE, "otsu_modes_cache.json")
ROOT = os.path.abspath(os.path.join(
    HERE, "..", "..", "Software", "UTM_PyQt6", "Test data",
    "8.6.20 - Tensile test to Failure"))

INK, GRID, MUTED = "#212529", "#DDDDDD", "#666666"
C_MARK, C_SPEC, C_BACK = "#C0392B", "#2E6DA4", "#7F8C8D"
C_OTSU, C_FIX = "#d62728", "#1F6FB4"

# (run, fixed threshold, cv2 threshold type, light body?, label)
RUNS = [
    ("Specimen_S24_V2_Spray_Video1", 150, cv2.THRESH_BINARY_INV, True, "S24 · white body"),
    ("Specimen_S25_V2_Spray_Video2", 150, cv2.THRESH_BINARY_INV, True, "S25 · white body"),
    ("Specimen_S26_V2_Spray_Video3", 150, cv2.THRESH_BINARY_INV, True, "S26 · white body"),
    ("Specimen_S13_V2_Spray_Video7", 149, cv2.THRESH_BINARY, False, "S13 · black body"),
]
MIN_AREA, MAX_AREA, MIN_CIRC = 2000, 200000, 0.5


# ============================================================================ measurement
def _frames(run, n):
    hits = sorted(glob.glob(os.path.join(ROOT, run, "*", "frames", "f*.png")))
    if not hits:
        return []
    step = max(1, len(hits) // n)
    return hits[::step][:n]


def _load(p, rotate=False):
    g = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
    if g is None:
        return None
    if rotate and g.shape[0] > g.shape[1]:
        g = np.ascontiguousarray(np.rot90(g))
    return g


def _split(g, light):
    """Locate the three populations by GEOMETRY, never by the threshold under test.

    Using the threshold to decide what the threshold should separate is circular, so the specimen
    band is found with a coarse split at the midpoint of the frame's own range and refined by
    connected components; the markers are then the round HOLES in that band.
    """
    mid = (int(g.min()) + int(g.max())) // 2
    spec = ((g > mid) if light else (g < mid)).astype(np.uint8)
    spec = cv2.morphologyEx(spec, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, st, _c = cv2.connectedComponentsWithStats(spec, 8)
    if n < 2:
        return None
    i = 1 + int(np.argmax([st[k, cv2.CC_STAT_AREA] for k in range(1, n)]))
    band = (lab == i)
    filled = cv2.morphologyEx(band.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((81, 81), np.uint8))
    holes = (filled.astype(bool) & ~band)
    hn, hlab, hst, _hc = cv2.connectedComponentsWithStats(holes.astype(np.uint8), 8)
    blobs = []
    for k in range(1, hn):
        a = int(hst[k, cv2.CC_STAT_AREA])
        w_, h_ = int(hst[k, cv2.CC_STAT_WIDTH]), int(hst[k, cv2.CC_STAT_HEIGHT])
        if a >= 2000 and 0.6 <= w_ / max(1, h_) <= 1.7:
            blobs.append((a, hlab == k))
    if len(blobs) < 2:
        return None
    blobs.sort(key=lambda b: -b[0])
    return (blobs[0][1] | blobs[1][1]), band


def _blobs(g, thr, ttype):
    """The rig's own gates, so any comparison starts from the two blobs it would have used."""
    _t, b = cv2.threshold(g, thr, 255, ttype)
    cnts, _h = cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    for c in cnts:
        a = cv2.contourArea(c)
        p = cv2.arcLength(c, True)
        circ = (4 * np.pi * a / (p ** 2)) if p > 0 else 0.0
        M = cv2.moments(c)
        if MIN_AREA < a < MAX_AREA and circ > MIN_CIRC and M["m00"] > 0:
            x, y, w_, h_ = cv2.boundingRect(c)
            out.append((M["m10"] / M["m00"], M["m01"] / M["m00"], (x, y, w_, h_)))
    out.sort(key=lambda t: t[1])
    return out


def _icent(g, box, light_marker, pad=10):
    """Centre of mass weighted by CONTRAST against the local background.

    Raw grey as the weight would drag the centre toward whichever side of the box happens to be
    brighter, so the local background is subtracted and negatives clipped: the weight is "how much
    more marker-like than its surroundings is this pixel".
    """
    x, y, w_, h_ = box
    x0, y0 = max(0, x - pad), max(0, y - pad)
    x1, y1 = min(g.shape[1], x + w_ + pad), min(g.shape[0], y + h_ + pad)
    sub = g[y0:y1, x0:x1].astype(np.float64)
    if sub.size == 0:
        return None
    base = float(np.median(np.concatenate([sub[0, :], sub[-1, :], sub[:, 0], sub[:, -1]])))
    wgt = np.clip((sub - base) if light_marker else (base - sub), 0, None)
    if wgt.sum() <= 0:
        return None
    yy, xx = np.mgrid[y0:y1, x0:x1]
    return float((wgt * xx).sum() / wgt.sum()), float((wgt * yy).sum() / wgt.sum())


def _detrend_rms(v, k=9):
    """Jitter about the LOCAL trend. A plain de-mean would count the pull itself as noise."""
    v = np.asarray(v, float)
    if len(v) < 3 * k:
        return float("nan")
    r = (v - np.convolve(v, np.ones(k) / k, "same"))[k:-k]
    return float(np.sqrt(np.mean(r ** 2)))


def compute():
    out = {"runs": {}, "jitter": {}}
    for run, fixed, ttype, light, label in RUNS:
        rows, cuts, cuts_no = [], [], []
        for p in _frames(run, 60):
            g = _load(p, rotate=True)
            if g is None:
                continue
            t, _b = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            cuts.append(float(t))
            sp = _split(g, light)
            if sp is None:
                continue
            mk, band = sp
            body = float(np.median(g[band & ~mk]))
            rows.append(dict(marker=float(np.median(g[mk])), specimen=body,
                             background=float(np.median(g[~(band | mk)])),
                             share=100.0 * float(mk.sum()) / g.size))
            g2 = g.copy(); g2[mk] = np.uint8(body)          # delete the markers, keep everything else
            t2, _b2 = cv2.threshold(g2, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            cuts_no.append(float(t2))
        if not rows:
            print("   %-32s markers not located geometrically - excluded" % label)
            continue
        out["runs"][run] = dict(
            label=label, light=bool(light), fixed=float(fixed),
            marker=float(np.median([r["marker"] for r in rows])),
            specimen=float(np.median([r["specimen"] for r in rows])),
            background=float(np.median([r["background"] for r in rows])),
            share=float(np.median([r["share"] for r in rows])),
            otsu=float(np.median(cuts)), otsu_nomark=float(np.median(cuts_no)),
            n=len(rows), hist=_pooled_hist(run))
        print("   %-32s otsu %5.1f  without markers %5.1f" %
              (label, out["runs"][run]["otsu"], out["runs"][run]["otsu_nomark"]))

    # ---- binary vs intensity-weighted centroid, on the frame as the CAMERA delivers it
    for run, fixed, ttype, light, label in RUNS:
        if run not in out["runs"]:
            continue
        hits = sorted(glob.glob(os.path.join(ROOT, run, "*", "frames", "f*.png")))
        if not hits:
            continue
        seg = hits[len(hits) // 5: len(hits) // 5 + 250]
        light_marker = (ttype == cv2.THRESH_BINARY)
        sb, si = [], []
        for p in seg:
            # NO rotation here. calculate_dic_strain takes abs(c[1][1] - c[0][1]) on the raw
            # portrait frame; rotating for viewing puts the pair apart in X and a 1680 px
            # separation comes out as 7.
            g = _load(p, rotate=False)
            if g is None:
                continue
            bs = _blobs(g, fixed, ttype)
            if len(bs) != 2:
                continue
            ic = [_icent(g, b[2], light_marker) for b in bs]
            if any(c is None for c in ic):
                continue
            sb.append(abs(bs[1][1] - bs[0][1]))
            si.append(abs(ic[1][1] - ic[0][1]))
        if len(sb) < 40:
            continue
        L0 = float(np.median(sb))
        jb, ji = _detrend_rms(sb), _detrend_rms(si)
        out["jitter"][run] = dict(label=label, n=len(sb), L0=L0, jb=jb, ji=ji,
                                  ue_b=1e6 * jb / L0, ue_i=1e6 * ji / L0, gain=jb / ji)
        print("   %-32s jitter binary %.4f px  intensity %.4f px  (%.2fx)"
              % (label, jb, ji, jb / ji))
    return out


def _pooled_hist(run, n=40):
    h = np.zeros(256, float)
    for p in _frames(run, n):
        g = _load(p)
        if g is None:
            continue
        h += cv2.calcHist([g], [0], None, [256], [0, 256]).ravel()
    return (100.0 * h / max(1.0, h.sum())).tolist()


def load(force=False):
    if not force and os.path.exists(CACHE):
        with open(CACHE, encoding="utf-8") as f:
            return json.load(f)
    print("otsu_modes: measuring (slow, cached afterwards)")
    d = compute()
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(d, f)
    return d


# ================================================================================ figures
def _style(ax):
    ax.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def fig_polarity(D=None):
    """One white specimen and one black one, with the three populations marked on each histogram.

    Side by side because the claim is a MIRROR: same algorithm, same shape of problem, opposite
    polarity. Two separate figures would let the reader assume the white one is a special case.
    """
    D = D or load()
    pick = [("Specimen_S26_V2_Spray_Video3", "WHITE body, DARK dots  ·  THRESH_BINARY_INV"),
            ("Specimen_S13_V2_Spray_Video7", "BLACK body, BRIGHT dots  ·  THRESH_BINARY")]
    fig, axes = plt.subplots(2, 1, figsize=(6.60, 4.30))
    for ax, (run, ttl) in zip(axes, pick):
        r = D["runs"][run]
        h = np.asarray(r["hist"])
        ax.fill_between(np.arange(256), h, 0, color="#9AA5AB", alpha=0.55, lw=0)
        ax.plot(np.arange(256), h, "-", color="#5A6570", lw=1.0)
        for v, c, nm in ((r["marker"], C_MARK, "markers"), (r["specimen"], C_SPEC, "specimen"),
                         (r["background"], C_BACK, "background")):
            ax.axvline(v, color=c, lw=1.4, ls=":")
            ax.text(v, 17, nm, rotation=90, fontsize=7.4, color=c, ha="right", va="top",
                    fontweight="bold")
        ax.axvline(r["otsu"], color=C_OTSU, lw=2.2)
        ax.axvline(r["fixed"], color=C_FIX, lw=2.0, ls="--")
        ax.text(r["otsu"] + 4, 3.0, "Otsu %.0f" % r["otsu"], fontsize=8.2, color=C_OTSU,
                fontweight="bold")
        ax.text(r["fixed"] - 4, 0.35, "preset %.0f" % r["fixed"], fontsize=8.2, color=C_FIX,
                fontweight="bold", ha="right")
        ax.set_yscale("log"); ax.set_ylim(0.02, 40); ax.set_xlim(0, 255)
        ax.set_ylabel("share (%)", fontsize=8.6)
        ax.set_title(ttl, fontsize=9.0, color=INK, pad=3)
        ax.tick_params(labelsize=8.2)
        _style(ax)
    axes[1].set_xlabel("grey level", fontsize=9.0)
    fig.tight_layout(h_pad=0.9)
    fig.savefig(os.path.join(FIGS, "otsu_polarity.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  otsu_polarity.png")


def fig_setby(D=None):
    """The deletion test, as a number line per run.

    A bar chart of two nearly-equal thresholds says nothing; what has to be visible is that the cut
    sits at the SPECIMEN/BACKGROUND boundary and nowhere near the markers, and that removing the
    markers leaves it there.
    """
    D = D or load()
    runs = [r for r in D["runs"].values()]
    runs.sort(key=lambda r: (not r["light"], r["label"]))
    fig, ax = plt.subplots(figsize=(6.60, 3.55))
    for i, r in enumerate(runs):
        y = len(runs) - 1 - i
        ax.plot([r["marker"], r["specimen"]], [y, y], "-", color="#CCCCCC", lw=6, zorder=1,
                solid_capstyle="butt")
        ax.plot(r["marker"], y, "o", ms=9, color=C_MARK, zorder=3)
        ax.plot(r["specimen"], y, "s", ms=9, color=C_SPEC, zorder=3)
        ax.plot(r["background"], y, "^", ms=9, color=C_BACK, zorder=3)
        ax.plot(r["otsu"], y, "|", ms=22, mew=3.0, color=C_OTSU, zorder=4)
        ax.plot(r["otsu_nomark"], y + 0.22, "|", ms=14, mew=2.0, color="#000000", zorder=4)
        ax.text(262, y, r["label"], fontsize=8.6, va="center", color=INK)
        ax.text(r["otsu"], y - 0.30, "%+.0f" % (r["otsu_nomark"] - r["otsu"]), fontsize=8.0,
                color=INK, ha="center", fontweight="bold")
    ax.set_yticks([]); ax.set_xlim(0, 300); ax.set_ylim(-1.15, len(runs) - 0.3)
    ax.set_xlabel("grey level", fontsize=9.2)
    # "does not move" is not what the picture shows - S25 shifts 3. Say the number.
    ax.set_title("Delete the markers and the cut barely moves — at most 3 grey levels,\n"
                 "against margins of 46–99 on either side of it\n"
                 "red | = Otsu   ·   black | = Otsu with the markers painted out   ·   "
                 "number = the shift", fontsize=9.0, color=INK)
    ax.plot([], [], "o", color=C_MARK, label="markers")
    ax.plot([], [], "s", color=C_SPEC, label="specimen")
    ax.plot([], [], "^", color=C_BACK, label="background / grips")
    ax.legend(fontsize=8.0, frameon=False, loc="lower left", ncol=3)
    _style(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "otsu_setby.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  otsu_setby.png")


def fig_methods(D=None):
    """What the intensity method would buy, in the rig's own units."""
    D = D or load()
    js = [j for j in D["jitter"].values()]
    js.sort(key=lambda j: j["label"])
    fig, ax = plt.subplots(figsize=(6.20, 3.30))
    x = np.arange(len(js)); w = 0.34
    b = ax.bar(x - w / 2, [j["ue_b"] for j in js], w, color="#5A6570",
               label="binary centroid — what the rig does")
    i = ax.bar(x + w / 2, [j["ue_i"] for j in js], w, color="#2E86C1",
               label="intensity-weighted centroid")
    for r in list(b) + list(i):
        ax.text(r.get_x() + r.get_width() / 2, r.get_height() + 0.25, "%.1f" % r.get_height(),
                ha="center", fontsize=8.4, color=INK)
    for k, j in enumerate(js):
        ax.text(k, max(j["ue_b"], j["ue_i"]) + 2.0, "%.2f×" % j["gain"], ha="center",
                fontsize=9.0, fontweight="bold", color="#1E8449")
    ax.set_xticks(x); ax.set_xticklabels([j["label"] for j in js], fontsize=8.6)
    ax.set_ylabel("frame-to-frame jitter, µε", fontsize=9.0)
    ax.set_ylim(0, max(max(j["ue_b"], j["ue_i"]) for j in js) * 1.35)
    ax.set_title("Keeping the grey levels: what it would actually buy", fontsize=9.6, color=INK)
    ax.legend(fontsize=8.2, frameon=False, loc="upper left")
    ax.tick_params(labelsize=8.4)
    _style(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "otsu_methods.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  otsu_methods.png")


def all_figs():
    print("Otsu polarity / method figures:")
    D = load()
    fig_polarity(D)
    fig_setby(D)
    fig_methods(D)
    return D


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    D = all_figs()
    for r in D["runs"].values():
        print("%-18s marker %5.1f  spec %5.1f  bg %5.1f  otsu %5.1f  (no markers %5.1f, %+.1f)  "
              "markers %.3f %% of frame"
              % (r["label"], r["marker"], r["specimen"], r["background"], r["otsu"],
                 r["otsu_nomark"], r["otsu_nomark"] - r["otsu"], r["share"]))
