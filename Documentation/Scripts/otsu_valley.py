"""What the histogram's VALLEY actually is, on the specimen itself.

The Otsu slides say a threshold belongs in the valley "because hardly any pixels live there". That
is true and it is not an answer: every one of those pixels is somewhere real. This module finds
where, and what it is, and marks the grey level on the frame directly.

WHAT IS MEASURED HERE (all on one real S13 frame, and reproducible line by line):

  * every pixel's grey level, and which of the three bands it falls in
        25-100    the dark mass - the specimen body AND the field behind it
        101-150   the valley
        151-255   the spray dots and the grips

  * where the valley pixels sit relative to the two kinds of bright object. This is the finding:
    80.3 % of the valley is nearer a GRIP than a marker. The valley is mostly grip glare, not the
    edge of the markers - which matters, because it is the grips that make the frame yield six
    qualifying blobs instead of two.

  * why, decomposed into two factors that between them account for the ratio:
        outline      grips 2370 px vs spray dots 1053 px       = 2.25x
        edge width   grip 6 px vs spray dot 2 px to fall out
                     of the valley                             = 3.00x
        product 6.8x, against an observed 80.3/10.1 = 8.0x. Close, not exact - the two factors
        are the bulk of it, and the residual is the grips' glare skirt reaching further than the
        width metric's own cut-off. Do not present 6.8 and 8.0 as the same number.

  * the small remainder that is neither: a specular glint off a raised print artefact out on the
    gauge, far from anything bright, peaking at grey 145.

A NOTE ON A SIMPLIFICATION THIS CORRECTS. The dark peak has been described as "the specimen body".
It is the specimen AND the dark surround: in the middle columns the body averages grey 79.3 and the
field behind it 66.4, and 99.6 % of both land in 25-100. They are one peak because they are not
separable by brightness - only by where they are.
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
C_DARK, C_VALLEY, C_BRIGHT = "#2E6DA4", "#C8860D", "#C0392B"
LO, HI = 101, 150                       # the valley, between the two masses
BRIGHT = 150

_cache = {}


def _frame():
    g = OD.sample_frame()
    if g.shape[0] > g.shape[1]:         # stills are stored portrait; the rig sees it landscape
        g = np.rot90(g)
    return np.ascontiguousarray(g)


def measure():
    """Everything the two slides quote. Nothing here is read off a screenshot."""
    if "d" in _cache:
        return _cache["d"]
    g = _frame()
    Hh, Ww = g.shape
    med = cv2.medianBlur(g, 5).astype(int)      # label a 5x5 median, never a single hot pixel
    valley = (g >= LO) & (g <= HI)
    bright = (g > BRIGHT).astype(np.uint8)

    # ---- separate the two kinds of bright object by whether they run off a frame edge.
    # A spray dot is compact and wholly inside; a grip is cut by the field of view.
    n, lab, stats, _c = cv2.connectedComponentsWithStats(bright, 8)
    mark = np.zeros_like(bright)
    grip = np.zeros_like(bright)
    marks = []
    for i in range(1, n):
        a = int(stats[i, cv2.CC_STAT_AREA])
        if a < 200:
            continue
        x, y = int(stats[i, cv2.CC_STAT_LEFT]), int(stats[i, cv2.CC_STAT_TOP])
        w_, h_ = int(stats[i, cv2.CC_STAT_WIDTH]), int(stats[i, cv2.CC_STAT_HEIGHT])
        if x <= 2 or y <= 2 or x + w_ >= Ww - 2 or y + h_ >= Hh - 2:
            grip[lab == i] = 1
        else:
            mark[lab == i] = 1
            marks.append((x + w_ // 2, y + h_ // 2, a, w_, h_))
    marks.sort()

    dm = cv2.distanceTransform(1 - mark, cv2.DIST_L2, 5)
    dg = cv2.distanceTransform(1 - grip, cv2.DIST_L2, 5)
    V = int(valley.sum())
    near_m = valley & (dm <= dg) & (dm <= 60)
    near_g = valley & (dg < dm) & (dg <= 160)
    other = valley & ~near_m & ~near_g

    # ---- how each edge falls away, and how wide each transition is
    def profile(m):
        d = cv2.distanceTransform(1 - m, cv2.DIST_L2, 5)
        xs, ys = [], []
        for r in range(1, 40):
            sel = (d >= r) & (d < r + 1)
            if sel.any():
                xs.append(r); ys.append(float(med[sel].mean()))
        return np.array(xs), np.array(ys)

    def width(m):
        """px from the object's edge until the mean grey has dropped out of the valley."""
        x, y = profile(m)
        below = np.where(y < LO)[0]
        return int(x[below[0]]) if len(below) else int(x[-1])

    def outline(m):
        d = cv2.distanceTransform(1 - m, cv2.DIST_L2, 5)
        return int(((d >= 1) & (d < 2)).sum())

    d = dict(
        g=g, med=med, Hh=Hh, Ww=Ww, n_px=int(g.size),
        valley=valley, bright=bright.astype(bool), mark=mark.astype(bool),
        grip=grip.astype(bool), marks=marks,
        V=V, v_pct=100.0 * V / g.size,
        near_m=near_m, near_g=near_g, other=other,
        pct_m=100.0 * near_m.sum() / V, pct_g=100.0 * near_g.sum() / V,
        pct_o=100.0 * other.sum() / V,
        prof_m=profile(mark), prof_g=profile(grip),
        w_m=width(mark), w_g=width(grip),
        out_m=outline(mark), out_g=outline(grip),
        area_m=int(mark.sum()), area_g=int(grip.sum()),
    )
    d["ratio_outline"] = d["out_g"] / d["out_m"]
    d["ratio_width"] = d["w_g"] / d["w_m"]
    d["ratio_pred"] = d["ratio_outline"] * d["ratio_width"]
    d["ratio_obs"] = d["pct_g"] / d["pct_m"]

    # ---- the specimen band vs the field behind it, in the columns where both are visible
    mid = g[:, 700:1500]
    rp = mid.mean(axis=1)
    sel = rp > (rp.min() + rp.max()) / 2
    runs, cur = [], None
    for i, v in enumerate(sel):
        if v and cur is None:
            cur = i
        if not v and cur is not None:
            runs.append((cur, i - 1)); cur = None
    if cur is not None:
        runs.append((cur, len(sel) - 1))
    runs.sort(key=lambda r: r[1] - r[0], reverse=True)
    a, b = runs[0]
    d["band"] = (a, b)
    d["grey_body"] = float(mid[a:b + 1].mean())
    d["grey_back"] = float(np.vstack([mid[:a], mid[b + 1:]]).mean())

    # ---- the odd one out: the brightest thing on the gauge that is not near anything bright
    far = valley & (np.minimum(dm, dg) > 150)
    ys, xs = np.where(far)
    if len(xs):
        k = int(np.argmax(med[ys, xs]))
        d["glint"] = (int(xs[k]), int(ys[k]), int(med[ys[k], xs[k]]), int(far.sum()))
    else:
        d["glint"] = None

    # ---- the probe points the annotated frame labels, each one FOUND, not eyeballed
    mx, my, _a, mw, _mh = marks[-1]
    r = mw // 2
    body = med[150:260, 700:1400]
    by, bx = np.where(body == int(np.percentile(body, 50)))
    dy, dx = np.where(body <= np.percentile(body, 2))

    # A point INSIDE the biggest single grip - the pixel furthest from that blob's own boundary.
    # The centroid of `grip` is useless here: it averages four separate blobs at the four corners
    # and lands in the middle of the specimen, which then labelled plain body as "grip face".
    gn, glab, gst, _gc = cv2.connectedComponentsWithStats(grip, 8)
    gi = 1 + int(np.argmax([gst[i, cv2.CC_STAT_AREA] for i in range(1, gn)]))
    one = (glab == gi).astype(np.uint8)
    gy, gx = np.unravel_index(int(np.argmax(cv2.distanceTransform(one, cv2.DIST_L2, 5))), one.shape)
    gx, gy = int(gx), int(gy)
    # walk from there toward the frame's centre and stop at the first valley pixel - that is the
    # glare skirt, and its distance is how far the grip's brightness reaches onto the specimen
    sx = 1 if gx < Ww // 2 else -1
    sy = 1 if gy < Hh // 2 else -1
    halo = None
    for step in range(1, 220):
        px, py = gx + sx * step, gy + sy * step
        if not (0 <= px < Ww and 0 <= py < Hh):
            break
        if LO <= med[py, px] <= HI:
            halo = (px, py, step); break
    pts = [
        (mx, my, "spray dot, centre", "bright"),
        (mx + r + 2, my, "2 px outside the dot", "valley"),
        (700 + int(bx[0]), 150 + int(by[0]), "plain specimen body", "dark"),
        (700 + int(dx[0]), 150 + int(dy[0]), "a dark print line", "dark"),
        (781, 300, "the field behind the specimen", "dark"),
        (gx, gy, "grip face", "bright"),
    ]
    if halo:
        pts.append((halo[0], halo[1], "the grip's glare, %d px out" % halo[2], "valley"))
    if d["glint"]:
        pts.append((d["glint"][0], d["glint"][1], "glint on a print defect", "valley"))
    d["grip_pt"] = (gx, gy)
    d["halo_px"] = halo[2] if halo else None
    d["halo_pt"] = (halo[0], halo[1]) if halo else (gx, gy)
    d["probes"] = [(x, y, lbl, band, int(med[y, x])) for x, y, lbl, band in pts]

    _cache["d"] = d
    return d


# ===================================================================== figure 1: values on the frame
def fig_greymap(D=None):
    """The frame itself, with the grey level written where it was read.

    The point of putting the numbers ON the picture: the histogram is an abstraction, and until the
    three bands are attached to things a viewer can point at, "the valley" is just a dip in a curve.
    """
    D = D or measure()
    g = D["g"]
    col = {"dark": C_DARK, "valley": C_VALLEY, "bright": C_BRIGHT}

    fig = plt.figure(figsize=(12.35, 4.35))
    # The frame is 5.6:1, so it occupies a thin horizontal band and the labels live in the space
    # above and below it. Fixed axes rather than tight_layout: the callouts are drawn OUTSIDE the
    # axes and tight_layout cannot see them, so it crops or crowds them.
    ax = fig.add_axes([0.012, 0.335, 0.976, 0.30])
    ax.imshow(g, cmap="gray", vmin=0, vmax=255, interpolation="nearest", aspect="auto")
    ax.set_xticks([]); ax.set_yticks([])

    # One slot per label, spread along the row so no two boxes can touch. The x fractions are
    # chosen for the LABEL WIDTHS, not for the probe positions - the leader line does the pointing.
    place = {
        "a dark print line": (0.085, -0.62),
        "plain specimen body": (0.315, -0.62),
        "spray dot, centre": (0.620, -0.62),
        "the grip's glare": (0.880, -0.62),
        "the field behind the specimen": (0.150, 1.62),
        "glint on a print defect": (0.480, 1.62),
        "2 px outside the dot": (0.745, 1.62),
        "grip face": (0.938, 1.62),
    }
    Hh, Ww = D["Hh"], D["Ww"]
    for x, y, lbl, band, val in D["probes"]:
        key = lbl if lbl in place else [k for k in place if k.split(",")[0] in lbl][0]
        fx, fy = place[key]
        c = col[band]
        ax.annotate("%d   %s" % (val, lbl), xy=(x, y), xytext=(fx * Ww, fy * Hh),
                    textcoords="data", fontsize=8.8, color=c, fontweight="bold",
                    ha="center", va="center", annotation_clip=False,
                    bbox=dict(boxstyle="round,pad=0.30", fc="white", ec=c, lw=1.1),
                    arrowprops=dict(arrowstyle="->", color=c, lw=1.3,
                                    shrinkA=3, shrinkB=3))
        ax.plot([x], [y], "o", ms=6, mfc="none", mec=c, mew=1.8)

    fig.text(0.5, 0.975, "One S13 frame, with the grey level read off where the ring sits",
             ha="center", va="top", fontsize=10.4, color=INK)
    fig.text(0.5, 0.925,
             "blue 25–100 the dark mass   ·   amber 101–150 the valley   ·   red above 150 bright",
             ha="center", va="top", fontsize=9.2, color=MUTED)
    for sp in ax.spines.values():
        sp.set_color("#CCCCCC")
    # tight crop AFTER the manual layout: the callouts sit outside the axes, and this trims
    # the dead margin the fixed geometry leaves under the lower label row without moving them
    fig.savefig(os.path.join(FIGS, "otsu_greymap.png"), dpi=200, facecolor="white",
                bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    print("  otsu_greymap.png")


# ============================================================ figure 2: where the valley pixels are
def fig_valley_where(D=None):
    """Paint every valley pixel in place, then show why the grips own most of them."""
    D = D or measure()
    g = D["g"]

    fig = plt.figure(figsize=(12.35, 4.55))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.00, 1.15], hspace=0.30, wspace=0.20,
                          left=0.035, right=0.985, top=0.90, bottom=0.09)

    # ---- top: the whole frame, valley painted in
    a0 = fig.add_subplot(gs[0, :])
    vis = np.dstack([g, g, g]).astype(np.uint8)
    vis[D["bright"]] = (192, 57, 43)
    vis[D["valley"]] = (240, 173, 20)
    a0.imshow(vis, interpolation="nearest", aspect="auto")
    a0.set_xticks([]); a0.set_yticks([])
    a0.set_title("Every pixel in the 101–150 valley, painted amber — %.2f %% of the frame. "
                 "Red is everything above 150." % D["v_pct"], fontsize=9.6, color=INK, pad=5)
    for sp in a0.spines.values():
        sp.set_color("#CCCCCC")

    mx, my, _a, mw, mh = D["marks"][-1]
    R = 105

    def _zoom(ax, x0, x1, y0, y1, ttl):
        sub = vis[y0:y1, x0:x1]
        ax.imshow(sub, interpolation="nearest")
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(ttl, fontsize=8.8, color=INK, pad=4)
        for sp in ax.spines.values():
            sp.set_color("#CCCCCC")

    a1 = fig.add_subplot(gs[1, 0])
    _zoom(a1, mx - R, mx + R, max(0, my - R), min(D["Hh"], my + R),
          "a spray dot: a thin amber rim, ~%d px wide" % D["w_m"])

    a2 = fig.add_subplot(gs[1, 1])
    gx, gy = D["grip_pt"]
    hx, hy = D["halo_pt"]
    cx, cy = (gx + hx) // 2, (gy + hy) // 2      # frame the grip face AND its glare skirt
    _zoom(a2, max(0, cx - 210), min(D["Ww"], cx + 210),
          max(0, cy - 140), min(D["Hh"], cy + 140),
          "a grip: a broad amber glare, ~%d px wide" % D["w_g"])

    # ---- the two edge profiles, on one axis
    a3 = fig.add_subplot(gs[1, 2])
    a3.axhspan(LO, HI, color="#F0C808", alpha=0.22, lw=0)
    a3.text(38, (LO + HI) / 2, "the valley", fontsize=8.2, color="#8a6d00",
            fontweight="bold", ha="right", va="center")
    for (xs, ys), c, nm in ((D["prof_m"], "#1F6FB4", "out from a spray dot"),
                            (D["prof_g"], C_BRIGHT, "out from a grip")):
        a3.plot(xs, ys, "-", color=c, lw=2.0, label=nm)
    a3.axhline(BRIGHT, color=MUTED, lw=1.0, ls=":")
    a3.set_xlim(1, 40); a3.set_ylim(55, 175)
    a3.set_xlabel("pixels out from the object's edge", fontsize=8.8)
    a3.set_ylabel("grey level", fontsize=8.8)
    a3.set_title("how fast each edge falls away", fontsize=8.8, color=INK, pad=4)
    a3.legend(fontsize=8.0, frameon=False, loc="upper right")
    a3.tick_params(labelsize=8.2)
    a3.grid(True, color=GRID, lw=0.6); a3.set_axisbelow(True)
    for s in ("top", "right"):
        a3.spines[s].set_visible(False)

    fig.savefig(os.path.join(FIGS, "otsu_valley_where.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  otsu_valley_where.png")


def all_figs():
    print("Otsu valley figures:")
    D = measure()
    fig_greymap(D)
    fig_valley_where(D)
    return D


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    D = all_figs()
    print("\nvalley %.3f %% of the frame  ·  markers %.1f %%  grips %.1f %%  neither %.1f %%"
          % (D["v_pct"], D["pct_m"], D["pct_g"], D["pct_o"]))
    print("outline %d vs %d = %.2fx  ·  width %d vs %d = %.2fx  ·  product %.1fx  vs observed %.1fx"
          % (D["out_g"], D["out_m"], D["ratio_outline"], D["w_g"], D["w_m"],
             D["ratio_width"], D["ratio_pred"], D["ratio_obs"]))
    print("body %.1f  ·  surround %.1f  ·  glint %s" % (D["grey_body"], D["grey_back"], D["glint"]))
    for p in D["probes"]:
        print("   %-32s (%4d,%3d)  grey %3d  [%s]" % (p[2], p[0], p[1], p[4], p[3]))
