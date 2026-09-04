# ===================================================================================
#  OTSU'S METHOD — what it does, and why the rig evaluates it but does not default to it.
#
#  Inserted straight after the SF12 auto-calibration slide, because that dialog is where
#  Otsu is actually scored against fixed thresholds.
#
#  Measured numbers come from otsu_data (recomputed from S13's saved stills). The
#  detection RATES are quoted from the project's own replay validation and are labelled
#  as quoted — see the otsu_data docstring for why they are not re-derived here.
# ===================================================================================
import otsu_data as _OD                                               # noqa: E402
import otsu_plots as _OP                                              # noqa: E402
import otsu_valley as _OV                                             # noqa: E402

_OP.all_figs()
_V = _OV.all_figs()
# The two optional probes are appended last, so indices 0-5 are fixed but 6 is only the
# glare if a glare pixel was found. Fail the build rather than silently label the glint.
_PROBE_ERR = "otsu_valley probe order changed - the valley slides index it positionally"
assert _V["halo_px"] and _V["probes"][6][2].startswith("the grip's glare"), _PROBE_ERR
_O = _OD.load()

_OTSU_URL = "https://ieeexplore.ieee.org/document/4310076"
_OTSU_CITE = ("N. Otsu, “A Threshold Selection Method from Gray-Level Histograms”, "
              "IEEE Trans. Systems, Man, and Cybernetics 9(1):62–66, 1979")


# ================================================================= 1. what Otsu does
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "OTSU'S METHOD — WHAT IT DOES, AND WHAT IT ASSUMES")

img_fit(s, "documentation/figures/otsu_hist.png", 0.35, 1.14, 6.35, 3.60)

header(s, 0.40, 4.86, 6.30, "Read on the histogram above")
tb(s, 0.40, 5.24, 6.30, 1.55,
   f"•  The dark mass at 25–100 is the specimen body.\n"
   f"•  The bright mass above 170 is the spray dots AND the grips.\n"
   f"•  Between them sits a broad valley — that is where any threshold has to go.\n"
   f"•  Otsu puts it at {_O['otsu_med']:.0f}; the rig's Black preset uses "
   f"{_O['fixed']:.0f}. {_O['fixed'] - _O['otsu_med']:.0f} grey levels apart, both inside the "
   f"valley.",
   fs=9.6, colour=BLACK)

header(s, 7.00, 1.10, 5.95, "What it does — in one sentence")
tb(s, 7.00, 1.48, 5.95, 1.95,
   "•  THE JOB: decide which pixels are “marker” and which are “background”. That needs one "
   "brightness number — above it is a marker, below it is not.\n"
   "•  Otsu picks that number by itself, from the picture alone. No setting to turn, nothing to "
   "train, no guess about what the specimen looks like.\n"
   "•  HOW: it tries all 254 possible numbers and keeps the one that leaves the two groups as "
   "tidy as possible — dark pixels alike, bright pixels alike.\n"
   "•  Written out, it maximises   σ²b(t) = ω₀ω₁ (μ₀ − μ₁)²   (ω = group sizes, μ = group means), "
   "which is the same thing as making each group internally consistent.",
   fs=9.6, colour=BLACK)

header(s, 7.00, 3.52, 5.95, "Why that is a respectable choice")
tb(s, 7.00, 3.90, 5.95, 1.35,
   "•  It is Fisher's linear discriminant applied to the intensity histogram — a real statistical "
   "criterion, not a heuristic.\n"
   "•  Non-parametric: it assumes no distribution, only that there are two classes.\n"
   "•  Cheap — one pass over 256 bins, O(L). It can run on every frame.",
   fs=9.6, colour=BLACK)

header(s, 7.00, 5.34, 5.95, "…and what it quietly assumes")
tb(s, 7.00, 5.72, 5.95, 1.15,
   "•  A BIMODAL histogram with a deep, sharp valley.\n"
   "•  Two classes of comparable SIZE and comparable VARIANCE — the derivation models them as two "
   "equal normals.\n"
   "•  Even illumination and low noise.",
   fs=9.6, colour=BLACK)

linkbox(s, 0.40, 6.86, 12.5,
        "Otsu 1979 — “A Threshold Selection Method from Gray-Level Histograms”, "
        "IEEE Trans. SMC 9(1):62–66   ·   ieeexplore.ieee.org/document/4310076",
        _OTSU_URL, fs=10)
pageno(s)


# ================================================================= 1b. the graph, in plain words
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "READING THAT GRAPH — GREY LEVELS AND WHAT OTSU IS DOING")

img_fit(s, "documentation/figures/otsu_explain.png", 0.35, 1.06, 12.6, 3.30)

header(s, 0.40, 4.52, 4.05, "“Grey level” — the number on a pixel")
tb(s, 0.40, 4.90, 4.05, 1.85,
   "•  The camera records no colour. Each pixel is ONE number: 0 is black, 255 is white, and "
   "everything between is a shade of grey.\n\n"
   "•  The left panel is a real 8 × 6 corner of a frame with those numbers printed on it. Read "
   "across the top row and the marker's edge is visible as the numbers fall from 234 to 104.\n\n"
   "•  Nothing is interpreted yet. This is just what the sensor wrote down.",
   fs=9.6, colour=BLACK)

header(s, 4.65, 4.52, 4.05, "“Share of pixels” — a headcount")
tb(s, 4.65, 4.90, 4.05, 1.85,
   "•  Go through every pixel in the picture and tally how many have each of the 256 numbers. "
   "That tally is the graph on the right.\n\n"
   "•  The height is the SHARE: “this percentage of the picture is exactly this bright”.\n\n"
   "•  The scale is logarithmic because the two markers are a fraction of one per cent of the "
   "pixels. On an ordinary scale the specimen body would be a spike and the markers would be an "
   "invisible flat line.",
   fs=9.6, colour=BLACK)

header(s, 8.90, 4.52, 4.05, "What Otsu does with it — plainly")
tb(s, 8.90, 4.90, 4.05, 1.85,
   "•  It tries EVERY possible cut, 1 to 254, and for each one splits the pixels into a dark pile "
   "and a bright pile.\n\n"
   "•  It keeps the cut where each pile is most alike INSIDE itself — where the two piles are "
   "most cleanly separated.\n\n"
   "•  Like sorting a room of people into “short” and “tall”: you put the line where you get two "
   "tidy groups, not one where half the tall people end up with the short ones.\n\n"
   "•  On this picture that lands at 131 — down in the valley, where few pixels live.",
   fs=9.6, colour=BLACK)

banner(s, 0.40, 6.86, 12.55, 0.36,
       "The valley is the whole point: a threshold put where hardly any pixels sit can drift a "
       "little without changing which side anything falls on.",
       fill=LIGHT_BLUE, fg=BLACK, fs=10.5)
pageno(s)


# ================================================================= 1c. the valley, on the specimen
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "WHAT THE VALLEY ACTUALLY IS — READ OFF THE SPECIMEN")

img_fit(s, "documentation/figures/otsu_greymap.png", 0.35, 0.98, 12.6, 3.48)

header(s, 0.40, 4.60, 4.05, "The three bands, as things you can point at")
tb(s, 0.40, 4.98, 4.05, 1.80,
   f"•  25–100, the big peak — the specimen and the field behind it. Plain body reads "
   f"{_V['probes'][2][4]:.0f}, a dark print line {_V['probes'][3][4]:.0f}, the background "
   f"{_V['probes'][4][4]:.0f}.\n"
   f"•  Above 150 — the two spray dots ({_V['probes'][0][4]:.0f} at centre) and the grips "
   f"({_V['probes'][5][4]:.0f}).\n"
   f"•  101–150, the valley — {_V['v_pct']:.2f} % of the frame. Every ring in amber above is one "
   f"of these, and none of them is an object.",
   fs=9.6, colour=BLACK)

header(s, 4.65, 4.60, 4.05, "A correction worth making here")
tb(s, 4.65, 4.98, 4.05, 1.80,
   f"•  Calling the big peak “the specimen body” is a simplification. It is the specimen AND the "
   f"dark field behind it.\n"
   f"•  Measured in the columns where both are visible: the body averages grey "
   f"{_V['grey_body']:.1f}, the surround {_V['grey_back']:.1f}, and 99.6 % of BOTH fall in 25–100.\n"
   f"•  They are one peak because brightness cannot tell them apart — only position can. It does "
   f"not matter here, because neither is anywhere near the cut.",
   fs=9.6, colour=BLACK)

header(s, 8.90, 4.60, 4.05, "So what IS in the valley?")
tb(s, 8.90, 4.98, 4.05, 1.80,
   f"•  Edges. A pixel lying across a boundary averages the bright side and the dark side, and the "
   f"lens is not perfectly sharp — so a marker's rim reads {_V['probes'][1][4]:.0f} two pixels out, "
   f"on its way from {_V['probes'][0][4]:.0f} to {_V['probes'][2][4]:.0f}.\n"
   f"•  Glare. The grip is still at {_V['probes'][6][4]:.0f} some "
   f"{_V['halo_px']:.0f} px away from its own face.\n"
   f"•  One real oddity: a glint off a raised print artefact out on the gauge, peaking at "
   f"{_V['glint'][2]:.0f}. Next slide.",
   fs=9.6, colour=BLACK)

banner(s, 0.40, 6.86, 12.55, 0.36,
       "Nothing in this scene IS mid-grey. The valley is what you get at the boundaries between "
       "the things that are — which is exactly why a threshold is safe there.",
       fill=LIGHT_BLUE, fg=BLACK, fs=10.5)
pageno(s)


# ================================================= 1d. and it is mostly the grips', not the markers'
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "THE VALLEY IS AN EDGE — AND MOSTLY THE GRIPS' EDGE")

img_fit(s, "documentation/figures/otsu_valley_where.png", 0.35, 0.98, 12.6, 3.85)

header(s, 0.40, 5.00, 6.05, "Where every valley pixel sits")
table(s, 0.40, 5.38, 6.05, 1.14, [
    ["Nearest bright object", "share of the valley", "what those pixels are"],
    ["a GRIP", "%.1f %%" % _V["pct_g"], "glare along a long, bright edge"],
    ["a SPRAY DOT", "%.1f %%" % _V["pct_m"], "the marker's own thin rim"],
    ["neither", "%.1f %%" % _V["pct_o"], "glints on the print, sensor noise"],
], cw=[1.85, 1.55, 2.65], hf=9.5, bf=9.2,
    ov={(1, 1): {"bg": RED_FAIL, "bold": True}, (2, 1): {"bg": GREEN_PASS, "bold": True}})

tb(s, 0.40, 6.55, 6.05, 0.80,
   "The markers contribute a tenth of it. If the valley looks mushy, that is the GRIPS being "
   "mushy — and the grips are exactly what the blob detector has to reject.",
   fs=9.6, italic=True, colour=GREY_TEXT)

header(s, 6.75, 5.00, 6.20, "Why the grips own it — two factors, both measured")
tb(s, 6.75, 5.38, 6.20, 1.90,
   f"•  MORE EDGE. The grips have {_V['out_g']:,} px of outline against the two dots' "
   f"{_V['out_m']:,} — {_V['ratio_outline']:.2f}×. Four big shapes cut by the frame beat two "
   f"circles 125 px across.\n"
   f"•  A SOFTER EDGE. Out from a spray dot the grey is back under 100 within {_V['w_m']:.0f} px; "
   f"out from a grip it takes {_V['w_g']:.0f} — {_V['ratio_width']:.2f}×. Matte paint on matte "
   f"plastic gives a crisp step; a bright specular face throws a skirt of glare.\n"
   f"•  Together {_V['ratio_pred']:.1f}×, against the {_V['ratio_obs']:.1f}× observed. The two "
   f"factors are the bulk of it; the residual is glare reaching past where the width metric "
   f"stops counting — not the same number, and not claimed as one.",
   fs=9.4, colour=BLACK)

banner(s, 0.40, 6.94, 12.55, 0.36,
       "This is the mechanism behind “six qualifying blobs, not two”: the grips are bright, "
       "large, and soft-edged, so they pass any threshold the markers pass.",
       fill=YELLOW_WARN, fg=BLACK, fs=10.5)
pageno(s)


# ================================================================= 2. why not by default
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "OTSU ON THIS RIG — EVALUATED EVERY TIME, DEFAULTED TO NEVER")

img_fit(s, "documentation/figures/otsu_frame.png", 0.35, 1.10, 6.35, 3.80)

header(s, 0.40, 4.98, 6.30, "What the three strips show")
tb(s, 0.40, 5.36, 6.30, 1.22,
   f"•  Both cuts find both markers on THIS specimen — the replay record is 99.8 % either way.\n"
   f"•  The grips are as bright as the dots and pass the same gates, so the frame yields six "
   f"qualifying blobs, not two.\n"
   f"•  Otsu's lower cut blooms them wider, which is why the detector has to choose the pair "
   f"rather than trust the count.",
   fs=9.6, colour=BLACK)

header(s, 7.00, 1.06, 5.95, "Where the rig DOES use it")
tb(s, 7.00, 1.44, 5.95, 1.30,
   "•  It is a per-frame option in DIC camera setup — “Threshold automatically (Otsu)”.\n"
   "•  Auto-calibrate scores it as a NAMED candidate against every swept fixed value, so the "
   "operator is told when Otsu wins rather than it being assumed either way.",
   fs=9.6, colour=BLACK)

header(s, 7.00, 2.86, 5.95, "Why it is not the default for black specimens")
table(s, 7.00, 3.24, 5.95, 1.13, [
    ["Frames holding 2/2 markers", "Otsu", "fixed 149"],
    ["S29 · PETG — run abandoned", "48.5 %", "99.5 %"],
    ["S13 · black PLA", "99.8 %", "99.8 %"],
], cw=[3.2, 1.35, 1.4], hf=9, bf=9,
    ov={(1, 1): {"bg": RED_FAIL, "bold": True}, (1, 2): {"bg": GREEN_PASS, "bold": True}})

tb(s, 7.00, 4.28, 5.95, 2.20,
   "•  Otsu recomputes from the WHOLE picture, so it follows the SCENE, not the markers.\n"
   "•  The markers are a fraction of a per cent of the pixels — the very case Otsu's own "
   "literature flags, where the within-class variance swamps the between-class variance.\n"
   "•  On black PLA it lands at 131 and works. On PETG — glossier, more translucent, brighter "
   "body — the histogram shifts and it lands at 127, three grey levels BELOW that specimen's "
   "130–160 working band. One marker fell under the cut on half the frames.\n"
   "•  Nothing was wrong with the markers, the ROI or the lighting. The RULE chose a value just "
   "outside the band that works.",
   fs=9.6, colour=BLACK)

banner(s, 0.40, 6.60, 12.55, 0.36,
       "A fixed threshold is not better than Otsu — it is only STABLE. When the LEDs or the "
       "material change, re-run auto-calibrate: it sweeps both and applies the winner.",
       fill=LIGHT_BLUE, fg=BLACK, fs=10)
footer(s, "Otsu's threshold measured on %d S13 frames (documentation/scripts/otsu_data.py); the "
          "48.5 / 99.5 / 99.8 rates are quoted from the project's replay validation over two full "
          "runs. Limitations per Otsu 1979 and its review literature." % _O["n"])
pageno(s)
