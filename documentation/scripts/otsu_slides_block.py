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

_OP.all_figs()
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

header(s, 7.00, 1.10, 5.95, "What it does")
tb(s, 7.00, 1.48, 5.95, 1.95,
   "•  Picks ONE global grey level by looking only at the histogram — no user setting, no "
   "training, no assumption about the shape of either class.\n"
   "•  It tries every level and keeps the one that splits the pixels into two classes that are "
   "internally as alike as possible.\n"
   "•  Formally it MAXIMISES the between-class variance\n"
   "        σ²b(t) = ω₀ω₁ (μ₀ − μ₁)²\n"
   "   where ω are the two class shares and μ their means — which is exactly equivalent to "
   "MINIMISING the variance within them.",
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
