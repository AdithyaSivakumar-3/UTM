# ===================================================================================
#  DIC POSITION ESTIMATORS — what they do, what the candidates are, which one we use,
#  and the measurements that justify it.
#
#  Appended to generate_v6a_slides.py. Every number on these five slides is read from
#  documentation/estimator_measurements.json at build time, which estimator_data.py
#  writes from the recorded S25/S26 video. Nothing is typed in by hand.
#
#  Layout follows the deck's own conventions, which are not arbitrary: body 0.38 in
#  below its header, and NOTHING below y = 6.90, because footer() occupies 7.00-7.40
#  across the full width and pageno() sits at x = 12.45-13.05.
# ===================================================================================
import estimator_plots as EP                                          # noqa: E402

_FIGS = EP.all_figs()
_E = EP.load()
_ND = _FIGS["noise_demo"]          # the worked example on the figure, so slide and figure agree

_L0 = _E["method"]["S25"]["auto"]["l0"]
_PX_UE = 1e6 / _L0                              # what one whole pixel is worth, in microstrain
_LIVE = (_E["live_rig"]["S25"] + _E["live_rig"]["S26"]) / 2.0


def _m(spec, key):
    return _E["method"][spec][key]["noise_ue"]


def _worst(key):
    return max(_m("S25", key), _m("S26", key))


def _box_regimes():
    ins = [r["noise_ue"] for s in ("S25", "S26") for r in _E["box"][s]["rows"] if r["ratio"] < 1.0]
    out = [r["noise_ue"] for s in ("S25", "S26") for r in _E["box"][s]["rows"] if r["ratio"] >= 1.2]
    ins.sort(); out.sort()
    med = lambda v: v[len(v) // 2] if len(v) % 2 else (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2.0
    return med(ins), med(out)


_BOX_IN, _BOX_OUT = _box_regimes()
_THR = _E["threshold"]
_ACC = _E["accuracy"]


# ================================================================= 1. what an estimator is FOR
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "WHAT A DIC POSITION ESTIMATOR DOES, AND WHY IT IS NEEDED")
img_fit(s, "documentation/figures/est_whatfor.png", 0.4, 1.20, 12.5, 3.02)

header(s, 0.45, 4.38, 6.15, "Where it sits in the chain")
tb(s, 0.45, 4.76, 6.15, 1.45,
   "frame  →  find the two markers  →  ESTIMATE EACH CENTRE  →  L_px  →  ε = (L_px − Px₀) / Px₀\n\n"
   "Everything else in that chain is bookkeeping. The estimator is the only step that decides a "
   "NUMBER, and it decides it for both markers on every frame. DIC strain is a ratio of PIXELS "
   "(⟪DOES MARKER SPACING CHANGE THE STRAIN⟫), so its precision is set entirely by how well those "
   "two centres are known.",
   fs=10, colour=BLACK)

header(s, 6.85, 4.38, 6.1, "Why a whole pixel is nowhere near good enough")
table(s, 6.85, 4.76, 6.1, 1.45, [
    ["Quantity", "Value"],
    ["Marker separation Px₀", "%.0f px" % _L0],
    ["Strain per WHOLE pixel", "%.0f µε — the red staircase" % _PX_UE],
    ["Rig's measured noise floor", "%.0f µε" % _LIVE],
    ["…so a centre must be known to", "%.3f px" % (_LIVE * 1e-6 * _L0)],
], cw=[3.0, 3.1], hf=9.5, bf=9)

banner(s, 0.4, 6.34, 12.55, 0.5,
       "Without sub-pixel estimation the elastic region — the part that gives E — would be a "
       "%.0f µε staircase, about %.0f× coarser than the noise floor the rig actually achieves."
       % (_PX_UE, _PX_UE / _LIVE),
       fill=LIGHT_BLUE, fg=BLACK, fs=10.5)
footer(s, "Left: S26's own elastic region, the same marker pair read with and without sub-pixel "
          "estimation. Measurements cached %s." % _E["measured"])
pageno(s)


# ================================================================= 2. the candidates
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "FOUR WAYS TO FIND A MARKER CENTRE — AND WHAT EACH COSTS")
img_fit(s, "documentation/figures/est_methods.png", 0.4, 1.18, 12.5, 2.48)

table(s, 0.4, 3.86, 12.55, 3.00, [
    ["Method", "How it decides where the centre is", "Advantage", "Disadvantage"],
    ["(a) Correlation +\nparabola peak-fit",
     "Slides the reference patch over the search area; the best-matching\n"
     "offset, refined by a parabola through the peak and its neighbours.",
     "Needs no threshold at all, and works on any\ntexture — so it is what FINDS a moved patch.",
     "On a large flat disc the correlation peak is broad, so the\n"
     "parabola is ill-conditioned. Erratic: %.1f µε on S25, %.1f on S26."
     % (_m("S25", "correlation"), _m("S26", "correlation"))],
    ["(b) Binary contour\ncentroid  (the live rig)",
     "Thresholds the patch, takes the blob nearest the centre, and averages\n"
     "the coordinates of every pixel inside it — each pixel counting once.",
     "Simple, fast and robust. Runs at frame rate\non the rig today.",
     "Where the threshold cuts the soft edge DECIDES the answer.\n"
     "Worst of the three on the harder specimen (%.1f µε, S26)." % _m("S26", "rig")],
    ["(c) Contour + intensity\nweighting   ← CHOSEN",
     "The same contour still selects the blob, but each pixel then votes in\n"
     "proportion to how dark it is, using the graded edge instead of cutting it.",
     "Best or tied-best on BOTH specimens (%.1f / %.1f µε)\nand ~2.5× less sensitive to the threshold."
     % (_m("S25", "auto"), _m("S26", "auto")),
     "Assumes a symmetric marker — which is why the detector\n"
     "requires circularity ≥ 0.40 before it accepts a blob."],
    ["(d) Full-field subset DIC\n(Ncorr / DICe style)",
     "Correlates thousands of small subsets across a sprayed speckle pattern\n"
     "and solves for a whole displacement field, not two points.",
     "Gives strain FIELDS, Poisson's ratio and\nlocalisation. The research standard.",
     "Needs a speckle pattern rather than two dots, and is minutes\n"
     "of offline compute — so it cannot drive a live control loop."],
], cw=[2.05, 4.35, 3.05, 3.10], hf=9.5, bf=8)

footer(s, "Panels drawn from a real S26 marker at the reference frame. All four answer the SAME "
          "question and differ only in which pixels vote, and how loudly — except (d), which is a "
          "different instrument. Noise over the fixed window; see ⟪DATA PROOF (1 OF 2)⟫.")
pageno(s)


# ================================================================= 3. the theory behind the choice
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "WHY THE INTENSITY-WEIGHTED CENTROID — THE REASONING")

header(s, 0.45, 1.22, 6.15, "1 · Position information lives in the GRADIENT, nowhere else")
tb(s, 0.45, 1.60, 6.15, 1.52,
   "For a feature in an image carrying noise σ_n, the best achievable position variance is bounded\n"
   "        var(x̂)  ≥  σ_n²  ⁄  Σ (∂I/∂x)²\n"
   "summed over pixels. A flat region contributes EXACTLY ZERO: the interior of the dot and the "
   "background say nothing about where the dot is. All of it sits in the brightness ramp at the "
   "rim — measured on our markers at 12 px wide.",
   fs=10, colour=BLACK)

header(s, 6.85, 1.22, 6.1, "2 · A binary threshold throws that gradient away")
tb(s, 6.85, 1.60, 6.1, 1.52,
   "Thresholding replaces the 12 px ramp with a step, and the centroid then depends on WHERE the "
   "step landed. Move the level — or the illumination, or the exposure — and the boundary slides "
   "along the ramp, taking the centre with it.\n"
   "Weighting by darkness uses the ramp's shape instead, averaging over the whole transition "
   "rather than over one arbitrary contour of it.",
   fs=10, colour=BLACK)

header(s, 0.45, 3.26, 6.15, "3 · Two jobs, deliberately kept separate")
table(s, 0.45, 3.64, 6.15, 1.50, [
    ["Job", "Done by", "Why that one"],
    ["Which blob is\nthe marker?", "the contour\n(binary)", "A yes/no question — robustness\nmatters, precision does not."],
    ["Where exactly is\nits centre?", "intensity\nweighting", "A continuous question — needs the\ngradient, so no hard cut is used."],
], cw=[1.55, 1.35, 3.25], hf=9.5, bf=8.5)

header(s, 6.85, 3.26, 6.1, "4 · Why not simply correlate, as the tracker already does")
tb(s, 6.85, 3.64, 6.1, 1.50,
   "Correlation is the right tool for FINDING a patch that has moved, and it is still what the "
   "post-processor uses for that. But its peak on a near-uniform disc is broad — low curvature — "
   "so the sub-pixel parabola through it is poorly conditioned and prone to peak-locking toward "
   "whole pixels. Correlation locates the marker; the centroid then measures it.",
   fs=10, colour=BLACK)

header(s, 0.45, 5.26, 12.5, "5 · What that reasoning PREDICTS — which is what the next two slides test")
table(s, 0.45, 5.64, 12.5, 1.20, [
    ["If the reasoning is right, then…", "Testable consequence", "Result"],
    ["information is in the edge, not the interior",
     "a patch too small to reach the rim tracks badly however good the estimator",
     "confirmed — %.0f× worse" % (_BOX_IN / _BOX_OUT)],
    ["weighting uses the ramp; thresholding cuts it",
     "sweeping the threshold moves a binary centre much further than a weighted one",
     "confirmed — %.1f× and %.1f× further"
     % (_THR["S25"]["binary_spread_px"] / _THR["S25"]["weighted_spread_px"],
        _THR["S26"]["binary_spread_px"] / _THR["S26"]["weighted_spread_px"])],
    ["the estimator sets precision, not the value",
     "all three agree on Px₀ and on peak strain, and differ only in scatter",
     "confirmed — Px₀ within 0.05 %"],
], cw=[4.0, 5.6, 2.9], hf=9.5, bf=8.5)
footer(s, "The bound in (1) is the Cramér–Rao limit for feature localisation; it is quoted to say "
          "WHERE the information is, not to claim the estimator attains it. Proof on "
          "⟪DATA PROOF (1 OF 2)⟫ and ⟪DATA PROOF (2 OF 2)⟫.")
pageno(s)


# ================================================================= 4. data proof, part one
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "DATA PROOF (1 OF 2) — PATCH SIZE FIRST, THEN THE ESTIMATOR")
img_fit(s, "documentation/figures/est_box.png", 0.4, 1.16, 12.5, 2.28)
img_fit(s, "documentation/figures/est_compare.png", 0.4, 3.52, 12.5, 2.28)

kpi(s, 0.45, 5.92, 2.95, "PATCH TOO SMALL (< 1× r)", "%.0f µε" % _BOX_IN,
    fill=RED_FAIL, h=0.88, vfs=17)
kpi(s, 3.60, 5.92, 2.95, "PATCH CLEAR OF THE EDGE", "%.0f µε" % _BOX_OUT,
    fill=GREEN_PASS, h=0.88, vfs=17)
kpi(s, 6.75, 5.92, 2.95, "BINARY CENTROID, WORST CASE", "%.1f µε" % _worst("rig"),
    fill=YELLOW_WARN, h=0.88, vfs=17)
kpi(s, 9.90, 5.92, 2.95, "WEIGHTED, WORST CASE", "%.1f µε" % _worst("auto"),
    fill=GREEN_PASS, h=0.88, vfs=17)

footer(s, "Order of operations matters: patch size buys %.0f×, the estimator a further %.1f× — so "
          "a wrong patch cannot be repaired by a better estimator. Every configuration is scored "
          "over the same fixed FRAME window taken from the rig's own strain."
          % (_BOX_IN / _BOX_OUT, _worst("rig") / _worst("auto")))
pageno(s)


# ================================================================= 5. data proof, part two
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "DATA PROOF (2 OF 2) — ROBUSTNESS AND ACCURACY")
img_fit(s, "documentation/figures/est_threshold.png", 0.4, 1.14, 12.5, 2.12)
img_fit(s, "documentation/figures/est_accuracy.png", 0.4, 3.34, 12.5, 2.12)

header(s, 0.45, 5.50, 6.15, "Precision bought without buying error")
table(s, 0.45, 5.88, 6.15, 1.00, [
    ["", "S25", "S26"],
    ["ε_f measured by the rig (%)", "%.2f" % _ACC["S25"]["ef_pct"], "%.2f" % _ACC["S26"]["ef_pct"]],
    ["peak ε re-measured here (%)", "%.2f" % _ACC["S25"]["post_peak_pct"],
     "%.2f" % _ACC["S26"]["post_peak_pct"]],
    ["scatter against the live rig (µε)", "%.0f" % _ACC["S25"]["rms_ue"],
     "%.0f" % _ACC["S26"]["rms_ue"]],
], cw=[3.35, 1.4, 1.4], hf=9.5, bf=8.5)

header(s, 6.85, 5.50, 6.1, "Tested, and WITHDRAWN — artefacts of a moving window")
table(s, 6.85, 5.88, 6.1, 1.00, [
    ["Claim previously made here", "Re-measured", "Verdict"],
    ["a centroid anchored to its own last position\nbeats one re-centred on correlation",
     "%.2f vs %.2f µε (S25)\n%.2f vs %.2f µε (S26)"
     % (_E["anchor"]["S25"]["own"]["noise_ue"], _E["anchor"]["S25"]["correlation"]["noise_ue"],
        _E["anchor"]["S26"]["own"]["noise_ue"], _E["anchor"]["S26"]["correlation"]["noise_ue"]),
     "no effect —\nwithdrawn"],
    ["a fixed grey level beats per-frame Otsu,\nby about six times",
     "%.1f vs %.1f µε (S25)\n%.1f vs %.1f µε (S26)"
     % (_E["threshold_policy"]["S25"]["fixed"]["noise_ue"],
        _E["threshold_policy"]["S25"]["per_frame_otsu"]["noise_ue"],
        _E["threshold_policy"]["S26"]["fixed"]["noise_ue"],
        _E["threshold_policy"]["S26"]["per_frame_otsu"]["noise_ue"]),
     "equal within 2 %\n— withdrawn"],
], cw=[2.85, 1.95, 1.30], hf=9.5, bf=7.5)

footer(s, "The fixed level is KEPT — for reproducibility, since it depends only on the reference "
          "frame — but it is not what makes the centroid quiet; the weighting is, which is why the "
          "level stopped mattering. The −%.0f / −%.0f µε offset against the live rig is the same "
          "in every mode, so it is not the estimator."
          % (abs(_ACC["S25"]["mean_ue"]), abs(_ACC["S26"]["mean_ue"])))
pageno(s)


# ================================================================= 6. how noise is measured
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "HOW THE NOISE IS MEASURED — AND WHAT A MICROSTRAIN IS")
img_fit(s, "documentation/figures/est_noise_method.png", 0.4, 1.16, 12.5, 2.62)

header(s, 0.45, 4.00, 4.05, "The unit: microstrain (µε)")
tb(s, 0.45, 4.38, 4.05, 2.05,
   "Strain is a length divided by a length, so it carries NO unit. That makes the raw numbers "
   "inconveniently small — a good measurement here is 0.000011 — so they are quoted in millionths.\n\n"
   "        1 µε  =  10⁻⁶ strain  =  0.0001 %%\n\n"
   "On this rig's 80 mm gauge, 1 µε is 0.08 µm of extension. Across the %.0f px pixel baseline it "
   "is %.4f px of marker movement — which is why sub-pixel estimation is not optional."
   % (_L0, _L0 * 1e-6), fs=10, colour=BLACK)

header(s, 4.75, 4.00, 4.05, "The measurement, in three steps")
table(s, 4.75, 4.38, 4.05, 2.05, [
    ["", "Step", "Why"],
    ["1", "Take a SHORT window where the\ntrue response is nearly straight",
     "%.2f – %.2f %% strain, %d points" % (_ND["eps_lo"] * 100, _ND["eps_hi"] * 100, _ND["n"])],
    ["2", "Fit a straight line to the marker\nseparation L over that window",
     "the material is still elastic\nthere, so a line IS the model"],
    ["3", "Take the standard deviation of\nwhat is left, ÷ Px₀, × 10⁶",
     "%.3f px  →  %.1f µε" % (_ND["sd_px"], _ND["sd_ue"])],
], cw=[0.35, 2.0, 1.7], hf=9.5, bf=8)

header(s, 9.05, 4.00, 3.9, "What it is NOT")
tb(s, 9.05, 4.38, 3.9, 2.05,
   "Noise is the SCATTER, not the error in the answer. A measurement can be quiet and still be "
   "offset — which is why accuracy is checked separately, against the live rig "
   "(⟪DATA PROOF (2 OF 2)⟫).\n\n"
   "It is not a fixed property of the rig either. It depends on the estimator, the patch size and "
   "the marker, so a microstrain figure only means something alongside the settings that "
   "produced it.",
   fs=10, colour=BLACK)

banner(s, 0.4, 6.55, 12.55, 0.52,
       "The window must be SHORT and nearly straight, and fixed the same way for anything being "
       "compared. Detrending a whole fracture curve with a polynomial measures how badly the "
       "polynomial fits — a mistake already made once in this project, and the reason every "
       "figure here is scored over one window pinned in frame numbers.",
       fill=YELLOW_WARN, fg=BLACK, fs=10)
footer(s, "Worked on S26 with the chosen estimator, over the same window every other estimator "
          "figure uses — so this walkthrough lands on %.1f µε, the same number quoted on "
          "⟪DATA PROOF (1 OF 2)⟫." % _ND["quoted_ue"])
pageno(s)
