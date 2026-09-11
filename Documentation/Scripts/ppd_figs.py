"""Figures that exist only for the PPD final presentation.

One so far: the lay-audience DIC explainer. It uses the WHITE specimen (S26), not the black one
every internal Otsu slide uses, because for someone who has never seen DIC the story is simply
"two dark dots on a bright part" - no thresholds, no histograms, no grips. The dots are FOUND by
the same geometry the rig uses (dark, round, big), never eyeballed, so the arrow really does span
the measured pair.
"""
import glob
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                       # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch                # noqa: E402

import cv2                                                            # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.abspath(os.path.join(HERE, "..", "figures"))
RUN = os.path.abspath(os.path.join(
    HERE, "..", "..", "Software", "UTM_PyQt6", "Test data",
    "Fracture tests", "Specimen_S26_V2_Spray_Video3"))

INK, TAN, SAGE = "#253439", "#B29E84", "#7C898B"
plt.rcParams["font.family"] = "Segoe UI"


def fig_dic_explain():
    hits = sorted(glob.glob(os.path.join(RUN, "*", "frames", "f*.png")))
    g = cv2.imread(hits[len(hits) // 4], cv2.IMREAD_GRAYSCALE)
    if g.shape[0] > g.shape[1]:
        g = np.ascontiguousarray(np.rot90(g))

    # the two dots: dark, round, large, and INSIDE the frame - the rig's own gates, mirrored
    _t, b = cv2.threshold(g, 130, 255, cv2.THRESH_BINARY_INV)
    n, lab, st, cen = cv2.connectedComponentsWithStats(b, 8)
    dots = []
    for i in range(1, n):
        a = int(st[i, cv2.CC_STAT_AREA])
        x, y = int(st[i, cv2.CC_STAT_LEFT]), int(st[i, cv2.CC_STAT_TOP])
        w_, h_ = int(st[i, cv2.CC_STAT_WIDTH]), int(st[i, cv2.CC_STAT_HEIGHT])
        if a < 4000 or x <= 2 or y <= 2 or x + w_ >= g.shape[1] - 2 or y + h_ >= g.shape[0] - 2:
            continue
        if 0.6 <= w_ / max(1, h_) <= 1.7:
            dots.append((cen[i][0], cen[i][1], (w_ + h_) / 4))
    dots.sort()
    assert len(dots) >= 2, "did not find the two dots"
    (x1, y1, r1), (x2, y2, r2) = dots[0], dots[-1]

    fig, ax = plt.subplots(figsize=(11.8, 2.95))
    ax.imshow(g, cmap="gray", vmin=0, vmax=255, aspect="auto", interpolation="bilinear")
    for x, y, r in ((x1, y1, r1), (x2, y2, r2)):
        ax.add_patch(Circle((x, y), r * 1.55, fill=False, ec=TAN, lw=3.0))
    ax.add_patch(FancyArrowPatch((x1 + r1 * 1.8, y1), (x2 - r2 * 1.8, y2),
                                 arrowstyle="<|-|>", mutation_scale=26, color=TAN, lw=3.0))
    # WHITE, because the label sits over the dark grip region at the top of the frame — ink on
    # that background was invisible, which he caught on the slide. "Speckle patterns" is his
    # wording for the sprayed markers.
    ax.annotate("the camera tracks these speckle patterns", xy=(x1, y1 - r1 * 1.6),
                xytext=(x1 + 150, 46), fontsize=15, color="white", fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="white", lw=1.8))
    ax.text((x1 + x2) / 2, (y1 + y2) / 2 - 46, "distance  L", fontsize=17,
            color=TAN, fontweight="bold", ha="center")
    ax.text((x1 + x2) / 2, g.shape[0] - 26,
            "pull the specimen  →  the markers move apart  →  strain = (L − L₀) / L₀",
            fontsize=15.5, color=INK, ha="center", va="bottom",
            bbox=dict(boxstyle="round,pad=0.45", fc="white", ec=SAGE, lw=1.2, alpha=0.95))
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    fig.tight_layout(pad=0.3)
    fig.savefig(os.path.join(FIGS, "ppd_dic_explain.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  ppd_dic_explain.png   dots %.0f px apart" % abs(x2 - x1))


RUN34 = os.path.abspath(os.path.join(
    HERE, "..", "..", "Software", "UTM_PyQt6", "Test data",
    "Fracture tests", "Specimen_S34_V4_Spray_Video13"))


def _band_and_dots(run_dir=None, idx=0):
    """The landscape ROI band and its two dots — same finder fig_dic_explain uses.
    Defaults to FRAME 0: its separation IS the L0 the reference-calculation line quotes,
    so lattice and formula tell one story. idx may be an int frame number or a 0–1
    fraction of the record. Captures without PNG stills (S34) fall back to the video."""
    run_dir = run_dir or RUN
    hits = sorted(glob.glob(os.path.join(run_dir, "*", "frames", "f*.png")))
    if hits:
        n = len(hits)
        k = int(n * idx) if isinstance(idx, float) and 0 < idx < 1 else int(idx)
        g = cv2.imread(hits[k if k >= 0 else n + k], cv2.IMREAD_GRAYSCALE)
    else:
        APP = os.path.abspath(os.path.join(HERE, "..", "..", "Software", "UTM_PyQt6"))
        if APP not in sys.path:
            sys.path.insert(0, os.path.join(APP, "app"))
        import utm_postproc as _PP
        vid = (glob.glob(os.path.join(run_dir, "*", "video.avi"))
               + glob.glob(os.path.join(run_dir, "*", "video.mkv")))[0]
        n = _PP.probe(vid)["frames"]
        k = int(n * idx) if isinstance(idx, float) and 0 < idx < 1 else int(idx)
        g = _PP.read_frame(vid, k if k >= 0 else n + k)
    if g.shape[0] > g.shape[1]:
        g = np.ascontiguousarray(np.rot90(g))
    _t, b = cv2.threshold(g, 130, 255, cv2.THRESH_BINARY_INV)
    n, lab, st, cen = cv2.connectedComponentsWithStats(b, 8)
    dots = []
    for i in range(1, n):
        a = int(st[i, cv2.CC_STAT_AREA])
        x, y = int(st[i, cv2.CC_STAT_LEFT]), int(st[i, cv2.CC_STAT_TOP])
        w_, h_ = int(st[i, cv2.CC_STAT_WIDTH]), int(st[i, cv2.CC_STAT_HEIGHT])
        if a < 4000 or x <= 2 or y <= 2 or x + w_ >= g.shape[1] - 2 or y + h_ >= g.shape[0] - 2:
            continue
        if 0.6 <= w_ / max(1, h_) <= 1.7:
            dots.append((cen[i][0], cen[i][1], (w_ + h_) / 4))
    dots.sort()
    assert len(dots) >= 2, "did not find the two dots"
    return g, dots[0], dots[-1]


def fig_ui_curve():
    """Stress vs Strain exactly as the rig's tab draws it — same theme code, real S26 data,
    trimmed at fracture. The 'Stressstrain plot.png' saved in the capture folders predates the
    tracking fixes (strain runs to 20 % on a 4 % specimen) and must never reach a slide."""
    APP = os.path.abspath(os.path.join(HERE, "..", "..", "Software", "UTM_PyQt6"))
    if APP not in sys.path:
        sys.path.insert(0, os.path.join(APP, "app"))
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import theme
    import petg_data as PD
    a = PD.get("S26")
    c = np.asarray(a["curve"], float)          # col 0 is strain ALREADY IN PERCENT (fig_trio)
    c = c[np.argsort(c[:, 0])]
    c = c[c[:, 0] <= a["ef"] * 100 * 1.02]
    fig, ax = plt.subplots(figsize=(10.6, 3.35))
    ax.set_title("Stress vs Strain")
    ax.set_xlabel("Engineering strain, DIC (%)")
    ax.set_ylabel("Stress, tared (MPa)")
    theme.style_axes(fig, ax, "dark")
    ax.plot(c[:, 0], c[:, 1], lw=1.9, color="#4dabf7")
    ax.set_xlim(left=-0.15)
    fig.tight_layout(pad=0.8)
    fig.savefig(os.path.join(FIGS, "ppd_ui_curve.png"), dpi=200,
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print("  ppd_ui_curve.png      S26 to fracture at %.2f %%" % (100 * a["ef"]))


def fig_pixels():
    """The ROI as the machine sees it: a lattice of pixels, and L0 counted in them.

    S34, his call 2026-09-06: its ~5 % fracture strain echoes the validation slides, so the
    reference calculation baked into the bottom of this figure lands on a number the audience
    meets again two slides later. L0 from frame 0; L from a late frame just before fracture."""
    g, (x1, y1, r1), (x2, y2, r2) = _band_and_dots(RUN34, 0)
    L0 = abs(x2 - x1)
    L = eps = None
    for frac in (0.96, 0.94, 0.92, 0.90, 0.97):
        try:
            _g2, (ax_, _ay, _r), (bx_, _by, _r2) = _band_and_dots(RUN34, frac)
            L = abs(bx_ - ax_)
            eps = (L - L0) / L0
            if 0.040 <= eps <= 0.056:
                break
        except (AssertionError, IndexError):
            continue
    assert L is not None, "no late frame with both dots"
    fig = plt.figure(figsize=(12.6, 3.80))
    gs = fig.add_gridspec(1, 2, width_ratios=[2.35, 1.0], wspace=0.06)

    ax = fig.add_subplot(gs[0])
    ax.imshow(g, cmap="gray", vmin=0, vmax=255)
    step = 16                                  # SCHEMATIC: the true lattice is 1 px — drawing
    for gx in range(0, g.shape[1], step):      # all 2348 lines would render as solid grey
        ax.axvline(gx, color=SAGE, lw=0.45, alpha=0.50)
    for gy in range(0, g.shape[0], step):
        ax.axhline(gy, color=SAGE, lw=0.45, alpha=0.50)
    ax.add_patch(FancyArrowPatch((x1, (y1 + y2) / 2), (x2, (y1 + y2) / 2),
                                 arrowstyle="<|-|>", mutation_scale=22, color=TAN, lw=2.6))
    for x, y in ((x1, y1), (x2, y2)):
        ax.plot([x], [y], "+", ms=16, mew=2.4, color="#E8590C")
    ax.text((x1 + x2) / 2, (y1 + y2) / 2 - 40, "L₀ = %.0f px" % L0, fontsize=15,
            color=TAN, fontweight="bold", ha="center")
    ax.text(g.shape[1] / 2, g.shape[0] - 18,
            "the REAL lattice is %d × %d = %s pixels — L₀ is a COUNT of them"
            % (g.shape[1], g.shape[0], format(g.shape[1] * g.shape[0], ",").replace(",", " ")),
            fontsize=11.5, color=INK, ha="center", va="bottom",
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=SAGE, lw=1.0, alpha=0.95))
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color(SAGE)
    ax.set_title("what the camera delivers — SCHEMATIC grid, drawn %d× coarser than reality\n"
                 "(one drawn cell = %d × %d = %d real pixels; the true 1-px grid is on the right)"
                 % (step, step, step, step * step), fontsize=9.5, color=INK)

    # the zoom: real pixels of the marker edge, one square each
    axz = fig.add_subplot(gs[1])
    half = 8
    cy, cx = int(round(y1)), int(round(x1 + r1))       # ON the boundary: dark dot -> bright body
    patch = g[cy - half:cy + half, cx - half:cx + half]
    axz.imshow(patch, cmap="gray", vmin=0, vmax=255, interpolation="nearest")
    for k in range(patch.shape[1] + 1):
        axz.axvline(k - 0.5, color="white", lw=0.8, alpha=0.7)
    for k in range(patch.shape[0] + 1):
        axz.axhline(k - 0.5, color="white", lw=0.8, alpha=0.7)
    axz.set_xticks([]); axz.set_yticks([])
    for sp in axz.spines.values():
        sp.set_color("#E8590C"); sp.set_linewidth(2.0)
    axz.set_title("the marker edge, single pixels —\nthe centroid lands BETWEEN them "
                  "(sub-pixel)", fontsize=10, color=INK)
    fig.text(0.5, 0.045,
             "strain  =  (L − L₀) / L₀  =  (%.0f − %.0f) / %.0f  =  %.4f  =  %.2f %%      "
             "— pixels over pixels, the units cancel: no millimetres needed"
             % (L, L0, L0, eps, 100 * eps),
             ha="center", fontsize=13, color=INK, fontweight="bold")
    fig.tight_layout(rect=(0, 0.10, 1, 1), pad=0.5)
    fig.savefig(os.path.join(FIGS, "ppd_pixels.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  ppd_pixels.png        S34: L0 %.0f px, L %.0f px, strain %.2f %%"
          % (L0, L, 100 * eps))


def _dots_in(g):
    """The two dots of a given landscape frame — same gates as fig_dic_explain."""
    _t, b = cv2.threshold(g, 130, 255, cv2.THRESH_BINARY_INV)
    n, lab, st, cen = cv2.connectedComponentsWithStats(b, 8)
    dots = []
    for i in range(1, n):
        a = int(st[i, cv2.CC_STAT_AREA])
        x, y = int(st[i, cv2.CC_STAT_LEFT]), int(st[i, cv2.CC_STAT_TOP])
        w_, h_ = int(st[i, cv2.CC_STAT_WIDTH]), int(st[i, cv2.CC_STAT_HEIGHT])
        if a < 4000 or x <= 2 or y <= 2 or x + w_ >= g.shape[1] - 2 or y + h_ >= g.shape[0] - 2:
            continue
        if 0.6 <= w_ / max(1, h_) <= 1.7:
            dots.append((cen[i][0], cen[i][1], (w_ + h_) / 4))
    dots.sort()
    assert len(dots) >= 2
    return dots[0], dots[-1]


def fig_px2strain():
    """The whole conversion on two REAL frames of one pull: freeze L0, measure L, divide.

    The arithmetic on the figure is computed by this script from the frames it shows —
    the same (L - L0) / L0 that utm_dic.dic_strain applies on the rig and in the
    post-processor. Nothing is typed in."""
    hits = sorted(glob.glob(os.path.join(RUN, "*", "frames", "f*.png")))
    g0 = cv2.imread(hits[0], cv2.IMREAD_GRAYSCALE)
    g1 = cv2.imread(hits[int(len(hits) * 0.75)], cv2.IMREAD_GRAYSCALE)
    if g0.shape[0] > g0.shape[1]:
        g0 = np.ascontiguousarray(np.rot90(g0))
        g1 = np.ascontiguousarray(np.rot90(g1))
    (ax1, ay1, ar1), (bx1, by1, br1) = _dots_in(g0)
    (ax2, ay2, ar2), (bx2, by2, br2) = _dots_in(g1)
    L0, L = abs(bx1 - ax1), abs(bx2 - ax2)
    eps = (L - L0) / L0

    fig, axes = plt.subplots(2, 1, figsize=(12.2, 3.55))
    for ax, g, pair, lab, col in (
            (axes[0], g0, ((ax1, ay1), (bx1, by1)), "reference frame — freeze  L₀ = %.0f px" % L0, INK),
            (axes[1], g1, ((ax2, ay2), (bx2, by2)), "later frame — measure  L = %.0f px" % L, "#E8590C")):
        ax.imshow(g, cmap="gray", vmin=0, vmax=255, aspect="auto")
        (xa, ya), (xb, yb) = pair
        ax.annotate("", xy=(xb - 40, (ya + yb) / 2), xytext=(xa + 40, (ya + yb) / 2),
                    arrowprops=dict(arrowstyle="<|-|>", color=col, lw=2.6, mutation_scale=22))
        for x, y in pair:
            ax.plot([x], [y], "+", ms=15, mew=2.2, color=col)
        ax.text(30, g.shape[0] - 30, lab, fontsize=12.5, color=col, fontweight="bold",
                va="bottom", bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=col, lw=1.0,
                                       alpha=0.92))
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color("#CCCCCC")
    fig.suptitle("strain  =  (L − L₀) / L₀  =  (%.0f − %.0f) / %.0f  =  %.4f  =  %.2f %%      "
                 "— pixels over pixels: the units cancel, no millimetres needed"
                 % (L, L0, L0, eps, 100 * eps), fontsize=12.5, color=INK, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(os.path.join(FIGS, "ppd_px2strain.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  ppd_px2strain.png     L0 %.1f px, L %.1f px, strain %.2f %%" % (L0, L, 100 * eps))


def fig_clipon_combo():
    """The clip-on principle drawing and his Zwick/Roell photo as ONE image — they describe
    the same instrument, so they share a card on the Contactless click-slide (his ask
    2026-09-06). Equal heights, white ground, a small gutter."""
    from PIL import Image as _Im

    def _on_white(path):
        im = _Im.open(path)
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = _Im.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[-1])
            return bg
        return im.convert("RGB")

    a = _on_white(os.path.join(FIGS, "ext_clipon.png"))
    b = _on_white(os.path.join(FIGS, "Clip-On.png"))
    H = 1000
    a = a.resize((int(a.width * H / a.height), H), _Im.LANCZOS)
    b = b.resize((int(b.width * H / b.height), H), _Im.LANCZOS)
    gap = 60
    combo = _Im.new("RGB", (a.width + gap + b.width, H), (255, 255, 255))
    combo.paste(a, (0, 0))
    combo.paste(b, (a.width + gap, 0))
    combo.save(os.path.join(FIGS, "ppd_clipon_combo.png"))
    print("  ppd_clipon_combo.png  %dx%d" % combo.size)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    fig_dic_explain()
    fig_ui_curve()
    fig_pixels()
    fig_px2strain()
    fig_clipon_combo()
