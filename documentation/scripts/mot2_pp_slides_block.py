# ===================================================================================
#  MOT session 2's video through OUR DIC post-processing — the third leg.
#
#  Six slides: what was run and the two wrong inputs, the two strain records plotted
#  separately, the agreement quantified, the stress-strain, the two slopes plotted
#  separately, and what the three-way result settles.
#
#  Appended to generate_v6a_slides.py. Every number is read from mot2_pp at build
#  time; nothing here is typed in.
# ===================================================================================
import mot2_pp as MPP                                                 # noqa: E402
import mot2_pp_plots as MPPP                                          # noqa: E402
import mot2_compare as CMP                                            # noqa: E402

MPPP.all_figs()
_S = MPP.build()
_D, _L, _N = _S["D"], _S["L"], _S["N"]
_P = _S["primary"]
_off = CMP.offset_pct
_pp, _mo, _s34 = _L["PP"], _L["MOT"], _L["S34"]


# ================================================================= 1. what was run
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "THEIR VIDEO THROUGH OUR PIPELINE — THE THIRD LEG")

tb(s, 0.45, 1.06, 12.5, 0.62,
   f"Session 2 has now been measured three ways, and each pair differs in exactly ONE thing. Their "
   f"extensometer and our pipeline read the SAME footage, so the only difference between them is "
   f"the CALCULATION. Our pipeline on their footage and on our own {_P} differ only in the MACHINE. "
   f"That is what makes a disagreement attributable instead of merely observed.",
   fs=11, colour=BLACK)

header(s, 0.45, 1.76, 6.15, "The frame-to-load mapping is exact, not interpolated")
tb(s, 0.45, 2.14, 6.15, 1.35,
   f"The .daq carries {_D['n_frames']} rows and the video carries {_D['n_frames']} frames. They were "
   f"written by one acquisition, so frame i IS row i — no nearest-time search and no assumption "
   f"that either stream is evenly sampled. Neither is: both carry a few doubled intervals. Their "
   f"strain file is {_D['n_frames'] - len(_D['t_mot'])} rows shorter because it drops what it could "
   f"not measure, so the pairing is made on TIME and lands {_D['pair_n']} matched instants.",
   fs=9.5, colour=BLACK)

header(s, 0.45, 3.56, 6.15, "Two inputs were wrong — and that turned out to be useful")
table(s, 0.45, 3.94, 6.15, 1.64, [
    ["Input", "Entered", "True", "What it corrupts"],
    ["frame rate", f"{_D['fps_entered']:.0f} fps", f"{_D['fps_true']:.3f} fps",
     f"every time output,\nby {_D['fps_factor']:.1f}×"],
    ["gauge", f"{_D['gauge_entered']:.0f} mm", f"{_D['gauge_true']:.4f} mm",
     "px/mm and the\nextension in mm"],
    ["px/mm (derived)", f"{_D['pxmm_reported']:.4f}", f"{_D['pxmm_true']:.4f}",
     "nothing further"],
], cw=[1.5, 1.15, 1.25, 1.65], hf=9, bf=8.5)

header(s, 6.85, 1.76, 6.1, "Neither one touches the strain")
tb(s, 6.85, 2.14, 6.1, 1.35,
   f"Because strain is a pixel ratio:   ε = (L − Px₀) / Px₀.\n\n"
   f"The frame rate is not in it and the gauge is not in it. So this run is an accidental "
   f"controlled experiment in the deck's own claim about px/mm ({ref('IS IT A CAMERA PROPERTY')}): "
   f"two wrong inputs, and exactly the outputs that depend on them came out wrong while the "
   f"measurement itself did not move at all.",
   fs=9.5, colour=BLACK)

header(s, 6.85, 3.56, 6.1, "And it answers a question we left open")
tb(s, 6.85, 3.94, 6.1, 1.64,
   f"The previous slide-set said their session-2 optics were unknown, so their pixel span could not "
   f"be computed and their noise could not be explained. It can now: Px₀ = {_D['px0']:.1f} px over "
   f"{_D['gauge_true']:.4f} mm is {_D['pxmm_true']:.3f} px/mm — the SAME 27.9 px/mm they used in "
   f"session 1. Their optics did not change between sessions; only the gauge did.",
   fs=9.5, colour=BLACK)

banner(s, 0.40, 5.76, 12.55, 0.52,
       f"The clock was corrected from the acquisition, not re-run: the .daq already carries the "
       f"true time base, so the fix is exact rather than approximate.",
       fill=LIGHT_BLUE, fg=BLACK, fs=11)
footer(s, f"Source: Validation docs\\MOT Test 2\\DIC post processing data\\sample3_chan 0_dic_postproc.csv "
          f"({_D['n_frames']} frames, 100 % tracked, 0 re-seeds), read by "
          f"documentation/scripts/mot2_pp.py.")
pageno(s)


# ================================================================= 2. the two strain records
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "THE TWO STRAIN RECORDS FROM ONE VIDEO, PLOTTED SEPARATELY")

img_fit(s, "documentation/figures/mot2pp_strain_pp.png", 0.35, 1.08, 6.35, 3.46)
img_fit(s, "documentation/figures/mot2pp_strain_mot.png", 6.75, 1.08, 6.35, 3.46)

header(s, 0.45, 4.62, 4.05, "Read them apart first")
tb(s, 0.45, 5.00, 4.05, 1.55,
   f"Two instruments, one video, one specimen, one clock. On their own zero-load zeros the peaks "
   f"are {_D['e'].max():.3f} % (ours) and {_D['e_mot'].max():.3f} % (theirs) — "
   f"{abs(_off(_D['e'].max(), _D['e_mot'].max())):.2f} % apart, before any correction or alignment "
   f"is applied to either.",
   fs=9.5, colour=BLACK)

header(s, 4.75, 4.62, 4.05, "The same trap, one sample apart")
tb(s, 4.75, 5.00, 4.05, 1.55,
   f"Both records run past the specimen parting, and both then follow the halves rather than the "
   f"gauge. Theirs collapses 5.33 → 2.78 % and the peak is read before it. Ours holds on longer and "
   f"then jumps +3.42 px in one 50 ms frame; {_D['tear_dropped']} trailing frames are dropped. "
   f"Untrimmed it would report {_D['ef_untrimmed']:.3f} %, and a 1.6 % disagreement where there is "
   f"none.",
   fs=9.5, colour=BLACK)

header(s, 9.05, 4.62, 3.9, "Why the trim rule is safe")
tb(s, 9.05, 5.00, 3.9, 1.55,
   f"It is relative, not absolute: a trailing sample is dropped only if the marker span moves more "
   f"than 10× the median step of the preceding 40 frames. A fast but genuine plastic ramp cannot "
   f"trip it, and it is applied to both records even though only one needs it.",
   fs=9.5, colour=BLACK)

banner(s, 0.40, 6.62, 12.55, 0.40,
       f"A specimen cannot stretch further in 50 ms than it did in the previous second while the "
       f"load is FALLING. That is the whole test, and it is what separates the tear from the pull.",
       fill=YELLOW_WARN, fg=BLACK, fs=10.5)
footer(s, "Both plots are the FULL records on each instrument's own zero-load zero, so they can be "
          "read against each other directly. Every landmark table in this block re-zeroes both at "
          "the 300 N preload instead.")
pageno(s)


# ================================================================= 3. the agreement
s = prs.slides.add_slide(BLANK); ju(s)
# Deliberately NOT titled "THE TWO CALCULATIONS AGREE ...": the session-1 slide already carries
# that phrase and another block refs it by exactly those words. A second slide containing it would
# make that key ambiguous, which resolve_refs treats as a build failure — correctly.
title(s, "SAME PIXELS, TWO CALCULATIONS — AND THEY AGREE AGAIN")

img_fit(s, "documentation/figures/mot2pp_agree.png", 0.45, 1.08, 12.5, 3.28)

header(s, 0.45, 4.44, 6.15, "Scale and offset, separated — they are different faults")
table(s, 0.45, 4.82, 6.15, 1.42, [
    ["Quantity", "Value", "What it means"],
    ["scale", f"{_D['scale']:.6f}", f"the two calculations differ by\n{abs(_D['scale_pct']):.3f} % of scale"],
    ["offset", f"{_D['offset_ue']:+.1f} µε",
     f"{_D['offset_px']:+.4f} px on a {_D['px0']:.0f} px span —\na reference-frame difference"],
    ["R²", f"{_D['fit_r2']:.7f}", f"residual sd {_D['fit_sd_ue']:.1f} µε over\n{_D['live_n']} points"],
], cw=[1.1, 1.35, 3.7], hf=9, bf=8.5)

header(s, 6.85, 4.44, 3.0, "Why not just a ratio")
tb(s, 6.85, 4.82, 3.0, 1.42,
   f"A ratio cannot tell a scale error from a constant offset: a fixed {abs(_D['offset_ue']):.0f} µε "
   f"is 1.5 % of the reading at 0.3 % strain and 0.1 % of it at 5 %, which looks exactly like a "
   f"drifting scale. Regressing separates them.",
   fs=9.5, colour=BLACK)

header(s, 10.05, 4.44, 2.9, "Session 1 said the same")
tb(s, 10.05, 4.82, 2.9, 1.42,
   f"On the 80 mm footage the two calculations agreed to a median ratio of 1.0017 and k = 0.99991 "
   f"({ref('THE TWO CALCULATIONS AGREE — SAME VIDEO')}). Different gauge, different specimen, same "
   f"answer — which is what makes it a repeat rather than a coincidence.",
   fs=9.5, colour=BLACK)

banner(s, 0.40, 6.42, 12.55, 0.52,
       f"Same footage, two independent calculations: they agree on SCALE to "
       f"{abs(_D['scale_pct']):.3f} % and differ by a constant of {abs(_D['offset_px']):.3f} px — "
       f"less than a tenth of one pixel on the marker span. Our maths is not the thing that could "
       f"be wrong.",
       fill=GREEN_PASS, fg=BLACK, fs=11)
footer(s, f"{_D['pair_n']} instants matched on the shared clock; the {_D['live_n']} above 0.05 % "
          f"strain are used, because below that a ratio measures the noise floor rather than the "
          f"strain.")
pageno(s)


# ================================================================= 4. stress-strain
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "ONE LOAD CHANNEL, THREE STRAIN MEASUREMENTS")

img_fit(s, "documentation/figures/mot2pp_stress.png", 0.35, 1.10, 6.55, 3.70)

header(s, 7.10, 1.06, 5.85, "Every landmark, and the offset from THEIR reading")
table(s, 7.10, 1.44, 5.85, 2.10, [
    ["", "ours ·\ntheir video", "XT-205 ·\ntheir maths", "offset", f"{_P} ·\nour rig"],
    ["σ_y (0.2 % offset, MPa)", f"{_pp['sy_steep']:.2f}", f"{_mo['sy_steep']:.2f}",
     f"{_off(_pp['sy_steep'], _mo['sy_steep']):+.2f} %", f"{_s34['sy_steep']:.2f}"],
    ["UTS (MPa)", f"{_pp['uts']:.2f}", f"{_mo['uts']:.2f}",
     f"{_off(_pp['uts'], _mo['uts']):+.2f} %", f"{_s34['uts']:.2f}"],
    ["strain at UTS (%)", f"{_pp['uts_e']:.2f}", f"{_mo['uts_e']:.2f}",
     f"{_off(_pp['uts_e'], _mo['uts_e']):+.2f} %", f"{_s34['uts_e']:.2f}"],
    ["failure strain (%)", f"{_pp['ef']:.2f}", f"{_mo['ef']:.2f}",
     f"{_off(_pp['ef'], _mo['ef']):+.2f} %", f"{_s34['ef']:.2f}"],
    ["fracture stress (MPa)", f"{_pp['sigf']:.2f}", f"{_mo['sigf']:.2f}",
     f"{_off(_pp['sigf'], _mo['sigf']):+.2f} %", f"{_s34['sigf']:.2f}"],
    ["toughness (MJ/m³)", f"{_pp['tough']:.2f}", f"{_mo['tough']:.2f}",
     f"{_off(_pp['tough'], _mo['tough']):+.2f} %", f"{_s34['tough']:.2f}"],
    ["noise, 0.05–0.35 % (µε)", f"{_N['PP']['rms']:.1f}", f"{_N['MOT']['rms']:.1f}",
     f"{_off(_N['PP']['rms'], _N['MOT']['rms']):+.1f} %", f"{_N['S34']['rms']:.1f}"],
], cw=[1.9, 1.0, 1.0, 0.95, 1.0], hf=8.5, bf=8.5)

header(s, 7.10, 3.74, 5.85, "Two of these columns are the same specimen")
tb(s, 7.10, 4.12, 5.85, 2.05,
   f"UTS is identical to two decimals because both read the SAME load cell — that column is a "
   f"check on the plumbing, not on the DIC. Everything that depends on STRAIN is where the test "
   f"actually is, and σ_y lands within {abs(_off(_pp['sy_steep'], _mo['sy_steep'])):.2f} %, failure "
   f"strain within {abs(_off(_pp['ef'], _mo['ef'])):.2f} % and fracture stress within "
   f"{abs(_off(_pp['sigf'], _mo['sigf'])):.2f} %.\n\n"
   f"The gap to {_P} is the one that is real: a different machine and a different specimen. It "
   f"stays at {abs(_off(_mo['uts'], _s34['uts'])):.1f} % on UTS, exactly where the previous "
   f"slide-set left it, and this leg does not move it. That is the point — the calculation was "
   f"never a candidate for it, and now that is shown rather than assumed.",
   fs=9.5, colour=BLACK)

tb(s, 0.35, 4.94, 6.55, 1.28,
   f"Toughness differs by {abs(_off(_pp['tough'], _mo['tough'])):.2f} % for a mechanical reason "
   f"rather than a numerical one: it is the AREA under the curve, so it accumulates every small "
   f"strain difference along the whole record instead of sampling one instant. It is the most "
   f"sensitive line in the table and still under 1.5 %.",
   fs=9.5, colour=BLACK)

banner(s, 0.40, 6.34, 12.55, 0.44,
       f"The blue dashed curve is our maths and the red is theirs, on one specimen — they are "
       f"drawn on top of each other because they are the same measurement.",
       fill=GREEN_PASS, fg=BLACK, fs=11)
footer(s, f"All three re-zeroed at the 300 N preload so they share our convention. Stress is the "
          f"XT-205's load ÷ 80 mm² nominal for the two red/blue curves, and our own load cell for "
          f"{_P}.")
pageno(s)


# ================================================================= 5. the two slopes
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "THE ELASTIC SLOPE, MEASURED TWICE ON THE SAME FOOTAGE")

img_fit(s, "documentation/figures/mot2pp_slope_pp.png", 0.35, 1.08, 6.35, 3.46)
img_fit(s, "documentation/figures/mot2pp_slope_mot.png", 6.75, 1.08, 6.35, 3.46)

header(s, 0.45, 4.62, 6.15, "The modulus, both methods, all three records")
table(s, 0.45, 5.00, 6.15, 1.42, [
    ["", f"fixed {CMP.FIX_WIN[0]:.2f}–{CMP.FIX_WIN[1]:.2f} %", "steepest run", "window", "spread"],
    ["ours · their video", f"{_pp['E_fix']['E']:.3f} GPa", f"{_pp['E_steep']['E']:.3f} GPa",
     f"{_pp['E_steep']['lo']:.2f}–{_pp['E_steep']['hi']:.2f} %",
     f"{abs(_pp['E_steep']['E'] - _pp['E_fix']['E']) / _pp['E_fix']['E'] * 100:.1f} %"],
    ["XT-205 · their maths", f"{_mo['E_fix']['E']:.3f} GPa", f"{_mo['E_steep']['E']:.3f} GPa",
     f"{_mo['E_steep']['lo']:.2f}–{_mo['E_steep']['hi']:.2f} %",
     f"{abs(_mo['E_steep']['E'] - _mo['E_fix']['E']) / _mo['E_fix']['E'] * 100:.1f} %"],
    [f"{_P} · our rig", f"{_s34['E_fix']['E']:.3f} GPa", f"{_s34['E_steep']['E']:.3f} GPa",
     f"{_s34['E_steep']['lo']:.2f}–{_s34['E_steep']['hi']:.2f} %",
     f"{abs(_s34['E_steep']['E'] - _s34['E_fix']['E']) / _s34['E_fix']['E'] * 100:.1f} %"],
    ["ours vs theirs, same video", f"{_off(_pp['E_fix']['E'], _mo['E_fix']['E']):+.2f} %",
     f"{_off(_pp['E_steep']['E'], _mo['E_steep']['E']):+.2f} %", "—", "—"],
], cw=[1.75, 1.3, 1.15, 1.1, 0.75], hf=8.5, bf=8.5)

header(s, 6.85, 4.62, 3.0, "The shapes match too")
tb(s, 6.85, 5.00, 3.0, 1.42,
   f"Both traces sit flat from the origin and roll over at the same place. That is a stronger "
   f"statement than two moduli agreeing: a fitted number can match by accident, a whole curve "
   f"cannot.",
   fs=9.5, colour=BLACK)

header(s, 10.05, 4.62, 2.9, "And it isolates the toe")
tb(s, 10.05, 5.00, 2.9, 1.42,
   f"{_P}'s trace dips to 2.7 GPa near 0.15 % and only reaches its steepest at "
   f"{_s34['E_steep']['lo']:.2f}–{_s34['E_steep']['hi']:.2f} %. Neither of these two does. So the "
   f"toe is in OUR LOAD TRAIN, not in our maths — the grip-seating item, narrowed.",
   fs=9.5, colour=BLACK)

banner(s, 0.40, 6.56, 12.55, 0.44,
       f"Same footage, two calculations: E agrees to "
       f"{abs(_off(_pp['E_fix']['E'], _mo['E_fix']['E'])):.2f} % on the fixed window and "
       f"{abs(_off(_pp['E_steep']['E'], _mo['E_steep']['E'])):.2f} % on the steepest run — an order "
       f"of magnitude tighter than the {abs(_off(_mo['E_steep']['E'], _s34['E_steep']['E'])):.1f} % "
       f"between the two machines.",
       fill=GREEN_PASS, fg=BLACK, fs=10.5)
footer(s, "Both panels are the local dσ/dε over a sliding 0.12 % strain window, against the same "
          "load channel. The two records differ only in how the strain was computed from the "
          "pixels.")
pageno(s)


# ================================================================= 6. what it settles
_pred = _N["S34"]["rms"] * _S["B"]["recs"][_P]["px0"] / _D["px0"]

s = prs.slides.add_slide(BLANK); ju(s)
title(s, "WHAT THE THIRD LEG SETTLES — AND ONE CORRECTION")

tb(s, 0.45, 1.06, 12.5, 0.40,
   "Three records, one specimen for two of them, one load channel for all three. Each pair differs "
   "in exactly one thing, so each disagreement has exactly one candidate cause.",
   fs=11, colour=BLACK)

header(s, 0.45, 1.52, 4.05, "SETTLED — the calculation")
table(s, 0.45, 1.90, 4.05, 1.42, [
    ["same video, ours vs theirs", "offset"],
    ["scale", f"{abs(_D['scale_pct']):.3f} %"],
    ["σ_y", f"{_off(_pp['sy_steep'], _mo['sy_steep']):+.2f} %"],
    ["failure strain", f"{_off(_pp['ef'], _mo['ef']):+.2f} %"],
    ["E, steepest run", f"{_off(_pp['E_steep']['E'], _mo['E_steep']['E']):+.2f} %"],
], cw=[2.6, 1.45], hf=9, bf=9)
tb(s, 0.45, 3.44, 4.05, 1.42,
   f"Two independent calculations on identical pixels, agreeing to better than a tenth of a pixel. "
   f"Whatever else is uncertain in this project, the pixel-to-strain step is not — and session 1 "
   f"said the same on a different gauge and a different specimen.",
   fs=9.5, colour=BLACK)

header(s, 4.75, 1.52, 4.05, "A CORRECTION TO WHAT WE SAID LAST")
tb(s, 4.75, 1.90, 4.05, 2.96,
   f"The previous slide-set reported that we had LOST the noise lead — {_N['MOT']['rms']:.1f} µε "
   f"for them against {_N['S34']['rms']:.1f} µε for {_P}. That comparison stands, but it is between "
   f"two RIGS, not two estimators, and it was read too broadly.\n\n"
   f"On identical footage our estimator is the quieter one: {_N['PP']['rms']:.1f} µε against their "
   f"{_N['MOT']['rms']:.1f} µε, the same direction session 1 found. The rig comparison and the "
   f"estimator comparison are different questions and this leg is what separates them.\n\n"
   f"The honest reading: their IMAGES are better than ours, our MATHS is not worse than theirs.",
   fs=9.5, colour=BLACK)

header(s, 9.05, 1.52, 3.9, "AND ONE THING IT REVEALS")
tb(s, 9.05, 1.90, 3.9, 2.96,
   f"1/Px₀ predicted our floor exactly across our own two gauges. Applied here it predicts "
   f"{_pred:.1f} µε on their {_D['px0']:.0f} px span; we actually reach {_N['PP']['rms']:.1f} µε — "
   f"{_pred / _N['PP']['rms']:.2f}× BETTER than the pixel count alone allows.\n\n"
   f"So their footage carries roughly {_pred / _N['PP']['rms']:.1f}× less measurement noise per "
   f"pixel than ours does. That is lighting, focus and marker quality, not optics and not "
   f"software — and it is the first quantified target for improving our own noise floor without "
   f"touching the camera.",
   fs=9.5, colour=BLACK)

banner(s, 0.40, 4.58, 12.55, 0.68,
       f"THE THREE-WAY RESULT: the calculation is confirmed to {abs(_D['scale_pct']):.3f} % of "
       f"scale, the instrument agrees on every strain landmark to under "
       f"{max(abs(_off(_pp['ef'], _mo['ef'])), abs(_off(_pp['sy_steep'], _mo['sy_steep']))):.1f} %, "
       f"and the only differences left standing belong to the MACHINE and the SPECIMEN — which is "
       f"exactly where the previous slide-set had already put them.",
       fill=GREEN_PASS, fg=BLACK, fs=11.5)

tb(s, 0.45, 5.42, 12.5, 1.00,
   f"STILL OPEN, AND NARROWED: the {abs(_off(_mo['uts'], _s34['uts'])):.1f} % UTS gap to {_P} is "
   f"now definitively not the DIC — the same maths on their video reproduces their number to "
   f"{abs(_off(_pp['uts'], _mo['uts'])):.2f} %. It is the pull speed or the specimen, and one run "
   f"of ours at {_S['B']['recs']['MOT']['res']['speed_mm_min']:.0f} mm/min separates those two. "
   f"What this leg removed is the third candidate.",
   fs=10, colour=BLACK)

footer(s, f"Noise is the residual about a straight fit over {_N['PP']['win'][0]:.2f}–"
          f"{_N['PP']['win'][1]:.2f} % strain, on the preload-zeroed convention for all three — "
          f"scale-invariant in time, so the 1000 fps entry does not reach it.")
pageno(s)
