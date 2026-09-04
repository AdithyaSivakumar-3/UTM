# ===================================================================================
#  STRAIN RATE ON ONE SHARED WINDOW — the same figure for both MOT tests, side by side.
#
#  Test 1's version already appears in its own context earlier in the deck
#  (⟪MOT TEST 1 — THE TWO CALCULATIONS AGREE⟫). It is repeated here so the two tests
#  can be read against each other on one layout: the point of the pair is what CHANGED
#  between them, and that is invisible when the two figures are 25 slides apart.
#
#  Appended to generate_v6a_slides.py. Test 1's numbers come from
#  documentation/mot_postproc_compare.json; Test 2's are computed in mot2_pp_plots.
# ===================================================================================
import json as _rjson                                                 # noqa: E402
import io as _rio                                                     # noqa: E402
import mot2_pp_plots as _RP                                           # noqa: E402

_R1 = _rjson.load(_rio.open("documentation/mot_postproc_compare.json", encoding="utf-8"))
_R1ROW = {r["key"]: r for r in _R1["rows"]}
_RIGN = _R1["rig_name"]

_R2 = {nm: st for nm, st, _c in _RP.fig_rate()}
_R2PP = _R2["XT205-S2 · PPD-UTM DIC"][0]
_R2MOT = _R2["XT205-S2 · XT-205 extensometer"][0]
_R2S33 = _R2["S33 · PPD-UTM"][0]
_R2S34 = _R2["S34 · PPD-UTM"][0]
_R2OURS = 0.5 * (_R2S33 + _R2S34)
_S3 = _RP.PP.build()
_R2EF = _S3["L"]["MOT"]["ef"]                     # XT205-S2 fracture strain, %
_N_PP, _N_MOT = _S3["N"]["PP"]["rms"], _S3["N"]["MOT"]["rms"]
_N_QUAD = (_N_PP ** 2 + _N_MOT ** 2) ** 0.5       # if the two noises were independent


# ================================================================= 1. MOT Test 1
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "MOT TEST 1 — STRAIN RATE ON ONE SHARED WINDOW")

img_fit(s, "documentation/figures/mot_postproc_compare.png", 0.40, 1.10, 12.5, 3.40)

header(s, 0.45, 4.62, 6.15, "What the two panels do")
tb(s, 0.45, 5.00, 6.15, 1.55,
   f"LEFT — one video, two calculations. The XT-205's own extensometer and the {_RIGN} DIC "
   f"pipeline read the SAME 80 mm footage, so anything between them is arithmetic and nothing "
   f"else. They lie on each other.\n\n"
   f"RIGHT — the same fitted window applied to four records, so the rates are commensurable. The "
   f"top two are that one video; the bottom two are {_RIGN} pulls of our own specimens.",
   fs=9.5, colour=BLACK)

header(s, 6.85, 4.62, 6.1, "And what it could NOT settle")
tb(s, 6.85, 5.00, 6.1, 1.55,
   f"The XT-205 reads strain about 2.2× faster than {_RIGN} at the same commanded speed. That is "
   f"not a calibration error and Test 1 said so: only 19–29 % of our crosshead motion reaches the "
   f"gauge, the rest going into frame flex, grips and shoulders, and a stiffer frame delivers a "
   f"larger share. MOT reading faster is what a stiffer frame LOOKS like — but with no load or "
   f"crosshead channel from them, Test 1 could not prove it. "
   f"{ref('MOT TEST 2 — TEST 1')} closes it.",
   fs=9.5, colour=BLACK)

banner(s, 0.40, 6.60, 12.55, 0.40,
       f"Two calculations on one video agree; two MACHINES on the same commanded speed do not — "
       f"and only the second of those is a question about the rig.",
       fill=LIGHT_BLUE, fg=BLACK, fs=10.5)
footer(s, "80 mm marker spacing, 0.05–0.35 % strain window on each record's own axis. Built by "
          "documentation/scripts/mot_postproc_compare.py.")
pageno(s)


# ================================================================= 2. MOT Test 2
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "MOT TEST 2 — STRAIN RATE ON ONE SHARED WINDOW")

img_fit(s, "documentation/figures/mot2pp_rate.png", 0.40, 1.02, 12.5, 2.90)

header(s, 0.45, 4.02, 6.15, "The same layout, the 45 mm test")
table(s, 0.45, 4.40, 6.15, 1.39, [
    ["", "XT205-S1 · 80 mm", "XT205-S2 · 45 mm"],
    ["the MOT bar · PPD-UTM DIC",
     "%.2e /s" % _R1ROW["pp"]["rate"], "%.2e /s" % _R2PP],
    ["the MOT bar · XT-205",
     "%.2e /s" % _R1ROW["mot"]["rate"], "%.2e /s" % _R2MOT],
    ["the two calculations, apart",
     "%.1f %%" % abs(100 * (_R1ROW["pp"]["rate"] / _R1ROW["mot"]["rate"] - 1)),
     "%.1f %%" % abs(100 * (_R2PP / _R2MOT - 1))],
    ["XT-205 ÷ PPD-UTM specimens",
     "%.2fx" % (_R1ROW["mot"]["rate"] / (0.5 * (_R1ROW["S25"]["rate"] + _R1ROW["S26"]["rate"]))),
     "%.2fx" % (_R2MOT / _R2OURS)],
], cw=[2.6, 1.75, 1.8], hf=9, bf=8.5)

header(s, 6.85, 4.02, 6.1, "The row that changed, and why")
tb(s, 6.85, 4.40, 6.1, 1.45,
   f"The two CALCULATIONS agree in both tests, and more tightly here: "
   f"{abs(100 * (_R2PP / _R2MOT - 1)):.1f} % against Test 1's "
   f"{abs(100 * (_R1ROW['pp']['rate'] / _R1ROW['mot']['rate'] - 1)):.1f} %.\n\n"
   f"The two MACHINES have swapped places. In Test 1 the XT-205 read 2.2× faster than our "
   f"specimens; here it reads {_R2MOT / _R2OURS:.2f}× — slightly SLOWER. Nothing about either "
   f"instrument changed. The XT-205 pulled at 2 mm/min against our 6.0, a 3× handicap, and it "
   f"delivers 45 % of that travel to the gauge against our 33 %. The two effects very nearly "
   f"cancel, which is exactly what a compliance explanation predicts and a calibration error "
   f"could not.",
   fs=9.5, colour=BLACK)

banner(s, 0.40, 6.02, 12.55, 0.38,
       f"Same figure, same window, one test apart: the CALCULATION agreement holds and the MACHINE "
       f"gap moves with the pull speed — which is the difference between a method and a machine.",
       fill=GREEN_PASS, fg=BLACK, fs=10.5)

# What "fitted window" means, said once and plainly. It is the single thing on this slide a reader
# could reasonably take the wrong way: nothing here is smoothed, and the only fit is the straight
# line whose slope IS the reported rate.
tb(s, 0.45, 6.46, 12.55, 0.42,
   f"WHAT \"FITTED WINDOW\" MEANS: the shaded band is a slice of RAW samples — nothing is smoothed, "
   f"filtered or resampled. The only fitting is one least-squares straight line through the "
   f"strain-against-time points inside that band, and its SLOPE is the rate reported in the bars. "
   f"The band is narrow and nearly straight on purpose, so what the fit leaves behind is instrument "
   f"noise rather than the curvature of the pull ({ref('THE WHOLE PULL, BOTH CALCULATIONS')}).",
   fs=10, colour=BLACK)
footer(s, "45 mm marker spacing. The window is 0.05–0.35 % of the PRELOAD-ZEROED strain: Test 2's "
          "preload lands inside the recording, so a raw window would sit on the seating ramp.")
pageno(s)


# ================================================================= 3. the whole pull, not the window
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "THE WHOLE PULL, BOTH CALCULATIONS — XT205-S2 TO FRACTURE")

img_fit(s, "documentation/figures/mot2pp_full.png", 0.40, 1.02, 12.5, 3.62)

header(s, 0.45, 4.76, 4.05, "Why this had to be shown at full scale")
tb(s, 0.45, 5.14, 4.05, 1.30,
   f"Every other view of these two records either stops at 0.9 % strain — the fitted window and a "
   f"little either side — or puts them on separate axes. Neither answers the question a reader "
   f"should be asking: does the agreement SURVIVE past the elastic ramp, out to "
   f"{_R2EF:.2f} % where the specimen is drawing and "
   f"then tearing? The window is 6 % of the record. This is the other 94 %.",
   fs=9.5, colour=BLACK)

header(s, 4.75, 4.76, 4.05, "And it does")
tb(s, 4.75, 5.14, 4.05, 1.30,
   f"The two traces are indistinguishable at this scale for the whole 156 s. The lower panel is "
   f"the difference on the same time axis: it sits on a constant −55 µε — which is 0.069 px on a "
   f"1255 px marker span, a reference-frame difference and not a calibration one — with no drift, "
   f"no divergence at large strain, and no step at yield. Fracture strain lands 0.08 % apart.",
   fs=9.5, colour=BLACK)

header(s, 9.05, 4.76, 3.9, "What the lower panel is NOT")
tb(s, 9.05, 5.14, 3.9, 1.30,
   f"It is a DIFFERENCE, and a difference cannot say whose noise is larger — subtracting two "
   f"records ADDS their scatter. That answer comes from fitting each record separately over one "
   f"window: PPD-UTM {_N_PP:.1f} µε against the XT-205's {_N_MOT:.1f} µε, so ours is the quieter "
   f"by {_N_MOT / _N_PP:.2f}×.",
   fs=9.5, colour=BLACK)

banner(s, 0.40, 6.52, 12.55, 0.40,
       f"The difference scatters by 36.7 µε, within 2 % of the {_N_QUAD:.1f} µε those two noises "
       f"give added in quadrature — so they are INDEPENDENT. Neither instrument is picking up a "
       f"common flicker from the footage they share; each is limited by its own marker-locating.",
       fill=LIGHT_BLUE, fg=BLACK, fs=10.5)
footer(s, "Raw samples throughout; the lower panel is a plain difference, not a fit. Both records "
          "are re-zeroed at the 300 N preload so they share one convention.")
pageno(s)
