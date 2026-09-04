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
import otsu_modes as _OM                                              # noqa: E402

_OP.all_figs()
_V = _OV.all_figs()
_M = _OM.all_figs()
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


# ============================================== 1e. it is not a black-specimen method
_MR = _M["runs"]
_WHITE = [r for r in _MR.values() if r["light"]]
_BLACK = [r for r in _MR.values() if not r["light"]]


def _margins(r):
    """How far the cut sits from each population it is meant to separate, whichever way round."""
    lo, hi = (r["marker"], r["specimen"]) if r["light"] else (r["specimen"], r["marker"])
    return r["otsu"] - lo, hi - r["otsu"]


s = prs.slides.add_slide(BLANK); ju(s)
title(s, "OTSU IS NOT A BLACK-SPECIMEN METHOD — IT WORKS ON WHITE TOO")

img_fit(s, "documentation/figures/otsu_polarity.png", 0.35, 1.06, 6.35, 4.30)

header(s, 0.40, 5.50, 6.30, "Why every earlier example here was black")
tb(s, 0.40, 5.88, 6.30, 1.30,
   "•  Because that is where the measured evidence was — S13 and the abandoned PETG run. It was "
   "an accident of which specimens had saved frames, not a property of the method.\n"
   "•  S24–S26 are light-bodied: mean grey ~172 against S13's 79. They have now been measured, "
   "and the claim is no longer resting on one polarity.",
   fs=9.6, colour=BLACK)

header(s, 7.00, 1.06, 5.95, "The polarity and the rule are separate settings")
tb(s, 7.00, 1.44, 5.95, 1.42,
   "•  The rig has a WHITE preset — THRESH_BINARY_INV, dark dots on a light body — beside the "
   "BLACK one.\n"
   "•  Every Otsu call in the app does the same two steps: strip the flag, then re-apply it — "
   "base = type & ~THRESH_OTSU, then base | THRESH_OTSU.\n"
   "•  So Otsu supplies the LEVEL; BINARY vs BINARY_INV decides which side counts as “marker”. "
   "The two never interfere.",
   fs=9.6, colour=BLACK)

header(s, 7.00, 3.00, 5.95, "Measured on four runs — and white has MORE room")
table(s, 7.00, 3.38, 5.95, 1.39, [
    ["Run", "marker", "body", "Otsu", "margin either side"],
] + [[r["label"].split(" · ")[0] + (" · white" if r["light"] else " · black"),
      "%.0f" % r["marker"], "%.0f" % r["specimen"], "%.0f" % r["otsu"],
      "%.0f  /  %.0f" % _margins(r)]
     for r in sorted(_MR.values(), key=lambda r: (not r["light"], r["label"]))],
    cw=[1.55, 0.95, 0.85, 0.85, 1.75], hf=9.2, bf=9.0)

tb(s, 7.00, 4.92, 5.95, 1.95,
   f"•  Otsu lands at {min(r['otsu'] for r in _WHITE):.0f}–{max(r['otsu'] for r in _WHITE):.0f} "
   f"on all three white runs — as stable as the {_BLACK[0]['otsu']:.0f} it picks on black.\n"
   f"•  The white specimens give it MORE clearance, not less: the nearest margin is "
   f"{min(min(_margins(r)) for r in _WHITE):.0f} grey levels against "
   f"{min(_margins(_BLACK[0])):.0f} on black.\n"
   f"•  So nothing about Otsu prefers a dark specimen. What differs is the SCENE, and that is the "
   f"next slide.",
   fs=9.6, colour=BLACK)
pageno(s)


# ============================================== 1f. …but it never looks at the markers
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "BUT OTSU NEVER LOOKS AT THE MARKERS — ON EITHER POLARITY")

img_fit(s, "documentation/figures/otsu_setby.png", 0.35, 1.06, 6.35, 3.95)

header(s, 0.40, 5.18, 6.30, "The test")
tb(s, 0.40, 5.56, 6.30, 1.60,
   f"•  Paint the two markers out of the frame — fill them with the body's own grey — and "
   f"recompute Otsu on the doctored picture.\n"
   f"•  If Otsu were choosing a marker/specimen boundary, deleting the markers would move it a "
   f"long way. It moves by at most 3 grey levels, on all four runs.\n"
   f"•  The markers are {min(r['share'] for r in _MR.values()):.2f}–"
   f"{max(r['share'] for r in _MR.values()):.2f} % of the frame. They cannot shift an optimum "
   f"computed over the whole picture.",
   fs=9.6, colour=BLACK)

header(s, 7.00, 1.06, 5.95, "What Otsu is actually separating")
tb(s, 7.00, 1.44, 5.95, 1.55,
   "•  The two DOMINANT populations — and on this rig neither of them is a marker.\n"
   "•  On a WHITE specimen: the bright body against the dark background.\n"
   "•  On a BLACK specimen: the dark body against the bright grips.\n"
   "•  The markers survive because they happen to land on the far side of a boundary that was "
   "chosen without reference to them.",
   fs=9.6, colour=BLACK)

header(s, 7.00, 3.12, 5.95, "Why this is the real reason not to default to it")
tb(s, 7.00, 3.50, 5.95, 1.80,
   "•  The deck has said “Otsu follows the SCENE, not the markers”. This is the proof, and it is "
   "sharper than the PETG story alone.\n"
   "•  Otsu was never optimising for the quantity that matters. Marker separation is a BY-PRODUCT "
   "of a specimen/background split.\n"
   "•  On PETG the dominant populations shifted, the by-product went with them, and one marker "
   "fell under the cut on half the frames. Nothing warned anyone, because nothing in the "
   "algorithm was watching the markers.",
   fs=9.6, colour=BLACK)

header(s, 7.00, 5.44, 5.95, "What the rig does instead")
tb(s, 7.00, 5.82, 5.95, 1.05,
   "•  A FIXED threshold does not follow the scene at all — it stays put and is wrong in a way "
   "you can predict.\n"
   "•  Auto-calibrate sweeps fixed values AND Otsu, scores them on contrast margin — the thing "
   "Otsu ignores — and applies the winner.",
   fs=9.6, colour=BLACK)

banner(s, 0.40, 6.98, 12.55, 0.36,
       "The margin is what protects the markers, and nothing inside Otsu is defending it.",
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


# ============================== 3. where Otsu sits among the methods, and what the others are for
#
# Answering a question the deck had left open: Otsu keeps being called "the method", and the
# obvious follow-up is what the binary and intensity methods are then. They are not alternatives to
# it - they sit a level above. Otsu chooses a NUMBER inside the binary method; the intensity family
# is a different way of locating a marker altogether, and full correlation is a different
# measurement entirely.
_J = _M["jitter"]
_JW = [j for j in _J.values() if "white" in j["label"]]
_JB = [j for j in _J.values() if "black" in j["label"]]
_SAT = {r["label"]: r["hist"][255] for r in _M["runs"].values() if r["light"]}
_SAT_LO, _SAT_HI = min(_SAT.values()), max(_SAT.values())

s = prs.slides.add_slide(BLANK); ju(s)
title(s, "THRESHOLD, BINARY, INTENSITY — WHAT EACH ONE IS ACTUALLY FOR")

header(s, 0.40, 1.02, 12.55, "Three different levels, often confused for three options")
table(s, 0.40, 1.40, 12.55, 1.39, [
    ["", "What it decides", "What comes out", "Used here?"],
    ["THRESHOLDING RULE\nfixed value · Otsu · auto-calibrate",
     "ONE number: the grey level that splits bright from dark",
     "a single threshold, per run or per frame",
     "YES — fixed by default, Otsu offered and scored"],
    ["BINARY / blob method",
     "which shapes past that cut are markers — by area, circularity, pairing",
     "two centroids → one axial strain",
     "YES — this is what the PPD-UTM measures with"],
    ["INTENSITY methods\nweighted centroid · full correlation",
     "position from the grey levels themselves — no cut at all",
     "sub-pixel centres, or a whole displacement FIELD",
     "NO — measured below, and the reason"],
], cw=[2.95, 3.85, 2.95, 2.80], hf=9.5, bf=8.8,
    ov={(1, 3): {"bg": GREEN_PASS}, (2, 3): {"bg": GREEN_PASS}, (3, 3): {"bg": YELLOW_WARN}})

tb(s, 0.40, 3.08, 12.55, 0.32,
   "So Otsu is not an alternative to “the binary method” — it is a rule INSIDE it. Its only "
   "alternatives are a fixed number or the swept value auto-calibrate picks.",
   fs=10, italic=True, colour=GREY_TEXT)

img_fit(s, "documentation/figures/otsu_methods.png", 0.35, 3.44, 6.20, 2.92)

header(s, 6.80, 3.42, 6.15, "What keeping the grey levels would buy")
tb(s, 6.80, 3.80, 6.15, 1.62,
   f"•  The rig throws the grey levels away at the threshold: every pixel inside the blob counts "
   f"1, every pixel outside 0, and the centroid is the contour's moments.\n"
   f"•  Weighting each pixel by its contrast instead cuts frame-to-frame jitter by "
   f"{min(j['gain'] for j in _JB):.2f}× on black and "
   f"{min(j['gain'] for j in _JW):.2f}–{max(j['gain'] for j in _JW):.2f}× on white. Real, "
   f"and not transformative.\n"
   f"•  Jitter about a 9-frame local trend — NOT the noise floor, which also carries drift.",
   fs=9.4, colour=BLACK)

header(s, 6.80, 5.50, 6.15, "Why full correlation DIC is a different animal")
tb(s, 6.80, 5.88, 6.15, 1.30,
   "•  It never thresholds. It matches the grey-level pattern of small subsets between frames, so "
   "it needs a random speckle over the whole gauge — not two dots — and returns a strain FIELD "
   "that shows necking and localisation.\n"
   f"•  On this rig it would have nothing to match: {_SAT_LO:.1f}–{_SAT_HI:.1f} % of every "
   f"white frame sits at exactly 255. The body is CLIPPED, so it carries no pattern to "
   f"correlate. Exposure would have to come down first.",
   fs=9.4, colour=BLACK)

footer(s, "Jitter measured over 250 consecutive frames per run at 1/5 through the pull, on the "
          "frame as the camera delivers it (documentation/scripts/otsu_modes.py). Detection rates "
          "are quoted, never re-derived.")
pageno(s)
