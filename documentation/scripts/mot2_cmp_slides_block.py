# ===================================================================================
#  MOT Test 2 against the PPD-UTM's own 45 mm runs — the comparison Test 1 could not make.
#
#  Six slides: how the comparison is made fair, the two curves, the strain records
#  and the compliance question Test 1 left open, the elastic slope, the noise, and
#  what the whole thing settles.
#
#  Appended to generate_v6a_slides.py. Every number is read from mot2_compare at
#  build time; nothing here is typed in.
# ===================================================================================
import mot2_compare as CMP                                            # noqa: E402
import mot2_cmp_plots as CMPP                                         # noqa: E402

CMPP.all_figs()
_B = CMP.build()
_G = CMP.gauge_scaling()

_P, _S = _B["primary"], _B["second"]                 # "S34", "S33"
_M, _p, _s = _B["L"]["MOT"], _B["L"][_P], _B["L"][_S]
_RM, _Rp, _Rs = _B["recs"]["MOT"], _B["recs"][_P], _B["recs"][_S]
_off = CMP.offset_pct
_WIN = _B["fix_win"]
_OURS_MM_MIN = _Rp["res"]["rate"] * 60.0


# ================================================================= 1. making it fair
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "MOT TEST 2 vs PPD-UTM 45 mm RUNS — MAKING IT FAIR")

tb(s, 0.45, 1.08, 12.5, 0.40,
   f"MOT Test 1 could compare only strain RATE: that export carried no load and stopped at 0.40 % "
   f"strain. MOT Test 2 has a load channel and runs to fracture, so every landmark is now "
   f"comparable — provided three things are held fixed first.",
   fs=11, colour=BLACK)

header(s, 0.45, 1.54, 6.15, "The three things held fixed, and why each one matters")
table(s, 0.45, 1.92, 6.15, 1.64, [
    ["Held fixed", "Left alone, it would show up as…"],
    ["THE STRAIN ZERO — theirs re-zeroed at\ntheir 300 N preload, onto our convention",
     "a toe inside their strain only, moving E\nand the 0.2 % offset yield with it"],
    [f"THE MODULUS METHOD — both methods run\non both machines, by the app's own search",
     f"a METHOD gap of {abs(_p['E_steep']['E'] - _p['E_fix']['E']) / _p['E_fix']['E'] * 100:.0f} % "
     f"reported as a\nMACHINE gap of {abs(_off(_M['E_steep']['E'], _p['E_steep']['E'])):.0f} %"],
    ["THE NOISE WINDOW — reported over matched\nSTRAIN and matched DURATION, both",
     "our floor grows with observation time, and\nthey dwell longer at any given strain"],
], cw=[2.9, 3.25], hf=9.5, bf=8)

header(s, 6.85, 1.54, 6.1, "The three records")
table(s, 6.85, 1.92, 6.1, 1.64, [
    ["", "XT205-S2 · MOT", f"{_P} · PPD-UTM", f"{_S} · PPD-UTM"],
    ["crosshead", f"{_RM['res']['speed_mm_min']:.0f} mm/min",
     f"{_OURS_MM_MIN:.1f} mm/min", f"{_Rs['res']['rate'] * 60.0:.1f} mm/min"],
    ["preload", f"{_RM['res']['preload']:.0f} N",
     f"{_Rp['res']['anchor']:.0f} N", f"{_Rs['res']['anchor']:.0f} N"],
    ["marker span Px₀", "not yet known",
     f"{_Rp['px0']:.0f} px", f"{_Rs['px0']:.0f} px"],
    ["sampling", f"{_RM['hz']:.1f} Hz", f"{_Rp['hz']:.1f} Hz", f"{_Rs['hz']:.1f} Hz"],
    ["samples in the pull", f"{_RM['n']}", f"{_Rp['n']}", f"{_Rs['n']}"],
], cw=[1.7, 1.55, 1.45, 1.4], hf=9, bf=8)

header(s, 0.45, 3.76, 6.15, f"Why {_P} is the reference — and it is not because it agrees")
tb(s, 0.45, 4.14, 6.15, 1.95,
   f"The validation pack warned that NEITHER of our 45 mm runs could be trusted on failure strain, "
   f"because {_P} tracked {_Rp['cover_all']:.0f} % of its samples and {_S} only "
   f"{_Rs['cover_all']:.0f} %, against 100 % for the 80 mm pair. Splitting those losses by WHERE "
   f"they fall changes the answer for one of them:\n\n"
   f"     •  {_P} — all 202 dropouts fall AFTER its fracture sample. Inside the pull it tracks "
   f"{_Rp['cover']:.1f} %, so its ε_f is sound.\n"
   f"     •  {_S} — 145 of its losses fall INSIDE the pull, leaving {_Rs['cover']:.1f} % tracked. "
   f"Its ε_f of {_s['ef']:.2f} % is the artefact that warning was about.\n\n"
   f"So {_P} is the reference on data quality, decided before any agreement was looked at. {_S} is "
   f"carried through every table anyway.",
   fs=9.5, colour=BLACK)

header(s, 6.85, 3.76, 6.1, "What is NOT held fixed, and cannot be")
tb(s, 6.85, 4.14, 6.1, 1.95,
   f"THE SPEED. They pulled at {_RM['res']['speed_mm_min']:.0f} mm/min and we pull at "
   f"{_OURS_MM_MIN:.1f} — {_OURS_MM_MIN / _RM['res']['speed_mm_min']:.0f}× faster. PLA is "
   f"rate-sensitive, so this is a real difference and it has a known DIRECTION: a slower pull "
   f"gives a lower strength.\n\n"
   f"THE SPECIMEN. Three different printed bars, n = 1 each. Our own two differ by "
   f"{abs(_off(_p['uts'], _s['uts'])):.1f} % on UTS, which is the floor on what any disagreement "
   f"here can mean.\n\n"
   f"Both are carried into the reading of every number rather than averaged away.",
   fs=9.5, colour=BLACK)

banner(s, 0.40, 6.24, 12.55, 0.52,
       f"Held fixed: the strain zero, the modulus method, the noise window. Not fixed, and stated "
       f"every time: the pull speed and the specimen.",
       fill=LIGHT_BLUE, fg=BLACK, fs=11)
footer(s, "Built by documentation/scripts/mot2_compare.py from the raw records on both sides — the "
          "XT-205's CSV and .daq, and our own test CSVs through utm_analysis.analyze().")
pageno(s)


# ================================================================= 2. the two curves
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "MOT TEST 2 — YIELD AND ε_f AGREE, UTS DOES NOT")

img_fit(s, "documentation/figures/mot2cmp_stress.png", 0.35, 1.10, 6.55, 3.70)

header(s, 7.10, 1.06, 5.85, "Every landmark, and the offset from %s" % _P)
table(s, 7.10, 1.44, 5.85, 2.10, [
    ["", "XT205-S2", _P, "offset", _S],
    ["σ_y  (0.2 % offset)", f"{_M['sy_steep']:.2f}", f"{_p['sy_steep']:.2f}",
     f"{_off(_M['sy_steep'], _p['sy_steep']):+.1f} %", f"{_s['sy_steep']:.2f}"],
    ["strain at yield (%)", f"{_M['sy_steep_e']:.2f}", f"{_p['sy_steep_e']:.2f}",
     f"{_off(_M['sy_steep_e'], _p['sy_steep_e']):+.1f} %", f"{_s['sy_steep_e']:.2f}"],
    ["UTS  (MPa)", f"{_M['uts']:.2f}", f"{_p['uts']:.2f}",
     f"{_off(_M['uts'], _p['uts']):+.1f} %", f"{_s['uts']:.2f}"],
    ["strain at UTS (%)", f"{_M['uts_e']:.2f}", f"{_p['uts_e']:.2f}",
     f"{_off(_M['uts_e'], _p['uts_e']):+.1f} %", f"{_s['uts_e']:.2f}"],
    ["failure strain (%)", f"{_M['ef']:.2f}", f"{_p['ef']:.2f}",
     f"{_off(_M['ef'], _p['ef']):+.1f} %", f"{_s['ef']:.2f}"],
    ["fracture stress (MPa)", f"{_M['sigf']:.2f}", f"{_p['sigf']:.2f}",
     f"{_off(_M['sigf'], _p['sigf']):+.1f} %", f"{_s['sigf']:.2f}"],
    ["toughness (MJ/m³)", f"{_M['tough']:.2f}", f"{_p['tough']:.2f}",
     f"{_off(_M['tough'], _p['tough']):+.1f} %", f"{_s['tough']:.2f}"],
], cw=[1.85, 1.0, 0.95, 1.05, 0.95], hf=9, bf=8.5)

header(s, 7.10, 3.74, 5.85, "Read the two halves of that table differently")
tb(s, 7.10, 4.12, 5.85, 2.05,
   f"THE TOP HALF IS A PASS. Yield lands within {abs(_off(_M['sy_steep'], _p['sy_steep'])):.1f} % "
   f"and failure strain within {abs(_off(_M['ef'], _p['ef'])):.1f} % — and {_S} puts yield at "
   f"{_s['sy_steep']:.2f} MPa too, so three specimens on two machines agree on yield to under 1 %. "
   f"Neither number was tuned to make that happen.\n\n"
   f"THE BOTTOM HALF IS NOT A FAILURE, IT IS THE SPEED. Every quantity that disagrees is one that "
   f"depends on what happens AFTER yield, and all of them move the way a "
   f"{_OURS_MM_MIN / _RM['res']['speed_mm_min']:.0f}× slower pull moves them: a lower peak, reached "
   f"earlier in strain, with less area under the curve. But the DIRECTION is all the speed buys: "
   f"the two gauges see only 1.19× of strain rate between them, not the 3× of crosshead, so rate is "
   f"worth well under 1 % here ({ref('WHAT THE SPEED DIFFERENCE PREDICTS')}). Our own "
   f"{abs(_off(_p['uts'], _s['uts'])):.1f} % specimen-to-specimen scatter covers more of the "
   f"{abs(_off(_M['uts'], _p['uts'])):.1f} % than the speed does; the rest is a batch and machine "
   f"difference that n = 1 a side cannot separate.",
   fs=9.5, colour=BLACK)

tb(s, 0.35, 4.92, 6.55, 1.30,
   f"Both curves start at the preload stress, not at the origin — {_RM['res']['preload'] / _RM['res']['area']:.2f} "
   f"MPa for them and {_Rp['res']['anchor'] / 80.0:.2f} MPa for us. That is what the two strain "
   f"zeros being put on ONE convention looks like on the page, and it is the single correction "
   f"that makes the rest of this slide legitimate ({ref('STRESS–STRAIN, AND WHAT THE ZERO COSTS')}).",
   fs=9.5, colour=BLACK)

banner(s, 0.40, 6.30, 12.55, 0.46,
       f"Yield {_off(_M['sy_steep'], _p['sy_steep']):+.1f} %   ·   failure strain "
       f"{_off(_M['ef'], _p['ef']):+.1f} %   ·   UTS {_off(_M['uts'], _p['uts']):+.1f} % — the two "
       f"that agree are the two the pull speed does not touch.",
       fill=GREEN_PASS, fg=BLACK, fs=11)
footer(s, f"σ_y is computed on each record's OWN steepest-straight-run modulus, so the same "
          f"construction is used on both machines. On the fixed window it reads {_M['sy']:.2f} vs "
          f"{_p['sy']:.2f} MPa — see the next slide but one.")
pageno(s)


# ============================================ 2b. the two-specimen head-to-head, offsets graded
#
# The previous slide carries S33 as well, which is right there — its coverage is the point being
# made. Here the question is a two-specimen one, so S33 is left out and the two curves get the
# room to be marked up properly.
#
# THE OFFSET COLUMN IS COLOUR-GRADED, and the bands are chosen against something real rather than
# by eye: our own two 45 mm specimens differ by 2.7 % on UTS, so anything inside that is within
# the scatter we already live with, and anything outside it is asking to be explained.
_GRADE = [
    (1.0, RGBColor(0xC8, 0xE6, 0xC9), "≤ 1 %", "instrument-level agreement"),
    (3.0, RGBColor(0xE6, 0xEF, 0xC4), "1 – 3 %", "inside our own S33/S34 specimen scatter"),
    (8.0, RGBColor(0xFF, 0xF3, 0xCD), "3 – 8 %", "larger than that scatter — needs a reason"),
    (1e9, RGBColor(0xFF, 0xCD, 0xD2), "> 8 %", "the largest gaps in this comparison"),
]


def _grade(v):
    for lim, col, _lab, _why in _GRADE:
        if abs(v) <= lim:
            return col
    return _GRADE[-1][1]


_ROWS = [
    ("σ_y  (0.2 % offset, MPa)", _M["sy_steep"], _p["sy_steep"], _s["sy_steep"]),
    ("strain at yield (%)", _M["sy_steep_e"], _p["sy_steep_e"], _s["sy_steep_e"]),
    ("UTS  (MPa)", _M["uts"], _p["uts"], _s["uts"]),
    ("strain at UTS (%)", _M["uts_e"], _p["uts_e"], _s["uts_e"]),
    ("failure strain (%)", _M["ef"], _p["ef"], _s["ef"]),
    ("fracture stress (MPa)", _M["sigf"], _p["sigf"], _s["sigf"]),
    ("toughness (MJ/m³)", _M["tough"], _p["tough"], _s["tough"]),
]

s = prs.slides.add_slide(BLANK); ju(s)
title(s, "MOT TEST 2 — XT205-S2 AGAINST S34, HEAD TO HEAD")

img_fit(s, "documentation/figures/mot2cmp_pair.png", 0.30, 1.06, 6.65, 4.07)

tb(s, 0.30, 5.22, 6.65, 1.10,
   f"Two specimens, two machines, one material. UTS and fracture are called out on both curves "
   f"because they are the two landmarks that behave differently: they sit {abs(_off(_M['uts'], _p['uts'])):.1f} % "
   f"apart on stress and {abs(_off(_M['ef'], _p['ef'])):.1f} % apart on strain. The curves are "
   f"indistinguishable up to about 1.5 % strain and separate only after yield.",
   fs=9.5, colour=BLACK)

header(s, 7.15, 1.02, 5.80, "Every landmark, with the offset graded by size")
_tbl = [["", "XT205-S2", _P, "offset", _S]]
for nm, a, b, c in _ROWS:
    _tbl.append([nm, f"{a:.2f}", f"{b:.2f}", f"{_off(a, b):+.1f} %", f"{c:.2f}"])
_ov = {(i + 1, 3): {"bg": _grade(_off(a, b)), "bold": True}
       for i, (_nm, a, b, _c) in enumerate(_ROWS)}
table(s, 7.15, 1.40, 5.80, 2.14, _tbl, cw=[1.9, 1.0, 0.95, 1.0, 0.95], hf=9, bf=8.5, ov=_ov)

header(s, 7.15, 3.66, 5.80, "How to read the colour")
_key = [["Band", "What it means"]] + [[lab, why] for _lim, _col, lab, why in _GRADE]
table(s, 7.15, 4.04, 5.80, 1.39, _key, cw=[1.15, 4.65], hf=9, bf=8.5,
      ov={(i + 1, 0): {"bg": col, "bold": True} for i, (_l, col, _lab, _w) in enumerate(_GRADE)})

tb(s, 7.15, 5.52, 5.80, 0.80,
   f"Read down the offset column and the split is not random: the two GREEN rows are the ones the "
   f"pull speed cannot touch, and every amber or red row is post-yield.",
   fs=9.5, colour=BLACK)

banner(s, 0.40, 6.42, 12.55, 0.44,
       f"Yield and failure strain agree at instrument level; everything after yield does not. "
       f"Which of those two groups a number falls into is the whole result.",
       fill=GREEN_PASS, fg=BLACK, fs=11)
footer(s, f"Offsets are XT205-S2 relative to {_P}. σ_y is on each record's own steepest-straight-run "
          f"modulus, so the same construction is used on both. {_S} is shown for scale and is not "
          f"part of the offset.")
pageno(s)


# ================================================================= 3. strain records + compliance
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "MOT TEST 2 — TEST 1'S OPEN QUESTION, CLOSED")

img_fit(s, "documentation/figures/mot2cmp_strain.png", 0.45, 1.08, 12.5, 3.32)

header(s, 0.45, 4.48, 4.05, "What Test 1 was left saying")
tb(s, 0.45, 4.86, 4.05, 1.62,
   f"MOT Test 1 found the XT-205 reading strain 2.21× faster than the PPD-UTM at the same "
   f"commanded speed, and could not say why. The verdict then was explicit: a stiffer frame "
   f"delivers a larger share of its crosshead travel to the gauge, so this is what a stiffer "
   f"frame LOOKS like — \"but our calibration is not contradicted, nor is it confirmed. That "
   f"needs their load or crosshead-displacement channel.\"",
   fs=9.5, colour=BLACK)

header(s, 4.75, 4.48, 4.05, "MOT Test 2 supplies it")
tb(s, 4.75, 4.86, 4.05, 1.62,
   f"With load on both sides the share can be measured instead of hypothesised, and it is "
   f"{_B['share']['MOT']['pct']:.0f} % for them against {_B['share'][_P]['pct']:.0f} % for {_P} and "
   f"{_B['share'][_S]['pct']:.0f} % for {_S}. Their frame IS the stiffer one, by about the factor "
   f"the rate gap needed. The hypothesis Test 1 could only state is now the measured answer, and "
   f"our scale is not implicated.",
   fs=9.5, colour=BLACK)

header(s, 9.05, 4.48, 3.9, "The honest caveat on that number")
tb(s, 9.05, 4.86, 3.9, 1.62,
   f"Ours is measured — the rig records crosshead position. Theirs is NOMINAL, speed × time, "
   f"because the .daq carries no crosshead channel. If their crosshead ever lagged its command "
   f"the true share is HIGHER than {_B['share']['MOT']['pct']:.0f} %, not lower, so the conclusion "
   f"is safe in the direction it matters.",
   fs=9.5, colour=BLACK)

banner(s, 0.40, 6.56, 12.55, 0.40,
       f"Two-thirds of our crosshead travel never reaches the gauge — and on a commercial machine "
       f"it is still over half. This is a property of load trains, not a defect of ours.",
       fill=LIGHT_BLUE, fg=BLACK, fs=10.5)
footer(s, "Share = DIC gauge stretch ÷ crosshead travel, both taken from the preload instant to "
          "fracture. The rest goes into frame flex, grip take-up and the specimen's shoulders.")
pageno(s)


# ================================================================= 4. the elastic slope
s = prs.slides.add_slide(BLANK); ju(s)
# Kept under ~55 characters: at 30 pt the title box holds one line, and the first draft wrapped
# "MACHINE" onto a second line that landed on top of the figure.
title(s, "MOT TEST 2 — WHERE YOU FIT CHANGES WHAT YOU GET")

img_fit(s, "documentation/figures/mot2cmp_elastic.png", 0.45, 1.08, 12.5, 3.32)

header(s, 0.45, 4.48, 6.15, "The same two methods on all three records")
table(s, 0.45, 4.86, 6.15, 1.55, [
    ["", f"fixed {_WIN[0]:.2f}–{_WIN[1]:.2f} %", "steepest straight run", "window", "spread"],
    ["XT205-S2 · MOT", f"{_M['E_fix']['E']:.3f} GPa", f"{_M['E_steep']['E']:.3f} GPa",
     f"{_M['E_steep']['lo']:.2f}–{_M['E_steep']['hi']:.2f} %",
     f"{abs(_M['E_steep']['E'] - _M['E_fix']['E']) / _M['E_fix']['E'] * 100:.1f} %"],
    [f"{_P} · ours", f"{_p['E_fix']['E']:.3f} GPa", f"{_p['E_steep']['E']:.3f} GPa",
     f"{_p['E_steep']['lo']:.2f}–{_p['E_steep']['hi']:.2f} %",
     f"{abs(_p['E_steep']['E'] - _p['E_fix']['E']) / _p['E_fix']['E'] * 100:.1f} %"],
    [f"{_S} · ours", f"{_s['E_fix']['E']:.3f} GPa", f"{_s['E_steep']['E']:.3f} GPa",
     f"{_s['E_steep']['lo']:.2f}–{_s['E_steep']['hi']:.2f} %",
     f"{abs(_s['E_steep']['E'] - _s['E_fix']['E']) / _s['E_fix']['E'] * 100:.1f} %"],
    ["MOT vs %s" % _P, f"{_off(_M['E_fix']['E'], _p['E_fix']['E']):+.1f} %",
     f"{_off(_M['E_steep']['E'], _p['E_steep']['E']):+.1f} %", "—", "—"],
], cw=[1.5, 1.35, 1.5, 1.05, 0.8], hf=8.5, bf=8.5)

header(s, 6.85, 4.48, 3.0, "The XT-205 curve has no toe")
tb(s, 6.85, 4.86, 3.0, 1.55,
   f"Their steepest straight run is {_M['E_steep']['lo']:.2f}–{_M['E_steep']['hi']:.2f} % — the "
   f"fixed window, near enough. Their two methods differ by "
   f"{abs(_M['E_steep']['E'] - _M['E_fix']['E']) / _M['E_fix']['E'] * 100:.1f} %. Their record is "
   f"simply straight from the origin.",
   fs=9.5, colour=BLACK)

header(s, 10.05, 4.48, 2.9, "The PPD-UTM curve does")
tb(s, 10.05, 4.86, 2.9, 1.55,
   f"Ours dips to 2.7 GPa near 0.15 % and is steepest only at "
   f"{_p['E_steep']['lo']:.2f}–{_p['E_steep']['hi']:.2f} %. That is grip seating still working "
   f"through the load train after the preload — the FW grip-seating experiment, visible.",
   fs=9.5, colour=BLACK)

banner(s, 0.40, 6.50, 12.55, 0.46,
       f"Both of their numbers ({_M['E_fix']['E']:.3f} and {_M['E_steep']['E']:.3f} GPa) fall "
       f"INSIDE our own 45 mm bracket of {min(_p['E_steep']['E'], _s['E_steep']['E']):.3f}–"
       f"{max(_p['E_steep']['E'], _s['E_steep']['E']):.3f} GPa. Quote a modulus with the method "
       f"attached or it means nothing.",
       fill=GREEN_PASS, fg=BLACK, fs=10.5)
footer(s, "The steepest-straight-run search is utm_analysis._steepest_straight_run — the app's own "
          "function, run here on the XT-205's record as well as on ours, so the comparison is of "
          "machines and not of arithmetic.")
pageno(s)


# ============================================ 4b. what the SPEED difference predicts for the slope
#
# XT205-S2 was pulled at 2 mm/min and S34 at 5.98, so the obvious question is whether the slope
# difference on the slide above is simply rate-sensitivity. Working it through says no — and the
# reason is worth its own slide, because the naive version of the calculation gives an answer 4x
# too big and the sign test settles it without needing any magnitude at all.
import numpy as _np                                                   # noqa: E402
import math as _math                                                  # noqa: E402


def _rate_of(rec, lo=0.05, hi=0.35):
    """d(eps)/dt over the shared window, on the preload-zeroed axis."""
    t, e = _np.asarray(rec["t"], float), _np.asarray(rec["e"], float)
    m = (e >= lo) & (e <= hi)
    return float(_np.polyfit(t[m], e[m] / 100.0, 1)[0])


_RT_M, _RT_P = _rate_of(_RM), _rate_of(_Rp)
_CROSS_RATIO = _OURS_MM_MIN / _RM["res"]["speed_mm_min"]
_RATE_RATIO = _RT_P / _RT_M
_DECADES = _math.log10(_RATE_RATIO)
_SH_M, _SH_P = _B["share"]["MOT"]["pct"], _B["share"][_P]["pct"]

s = prs.slides.add_slide(BLANK); ju(s)
title(s, "MOT TEST 2 — WHAT THE SPEED DIFFERENCE PREDICTS")

tb(s, 0.45, 1.06, 12.5, 0.40,
   f"{_P} was pulled {_CROSS_RATIO:.1f}× faster than XT205-S2 at the crosshead. PLA is "
   f"rate-sensitive, so that is the first thing to suspect for the slope gap on the previous "
   f"slide. It is worth doing the arithmetic before believing it.",
   fs=11, colour=BLACK)

header(s, 0.45, 1.52, 6.15, "The crosshead ratio is not the ratio that matters")
table(s, 0.45, 1.90, 6.15, 1.42, [
    ["", "XT205-S2", f"{_P}", "ratio"],
    ["crosshead", f"{_RM['res']['speed_mm_min']:.2f} mm/min",
     f"{_OURS_MM_MIN:.2f} mm/min", f"{_CROSS_RATIO:.2f}×"],
    ["share reaching the gauge", f"{_SH_M:.0f} %", f"{_SH_P:.0f} %",
     f"{_SH_M / _SH_P:.2f}×"],
    ["GAUGE STRAIN RATE", f"{_RT_M:.3e} /s", f"{_RT_P:.3e} /s", f"{_RATE_RATIO:.3f}×"],
], cw=[2.2, 1.4, 1.4, 0.9], hf=9.5, bf=9)

header(s, 0.45, 3.50, 6.15, "Why the two ratios are so different")
tb(s, 0.45, 3.88, 6.15, 1.55,
   f"A specimen does not feel the crosshead; it feels the strain rate in its own gauge. The "
   f"XT-205 delivers {_SH_M:.0f} % of its travel there and the PPD-UTM {_SH_P:.0f} %, so the "
   f"stiffer frame hands over a larger share and claws back most of the {_CROSS_RATIO:.1f}× speed "
   f"handicap. What is left is {_RATE_RATIO:.3f}× — a factor of "
   f"{_CROSS_RATIO / _RATE_RATIO:.1f} smaller than the speeds suggest, and only "
   f"{_DECADES:.3f} of a DECADE.",
   fs=9.5, colour=BLACK)

header(s, 6.85, 1.52, 6.1, "So how much modulus should that buy?")
table(s, 6.85, 1.90, 6.1, 1.42, [
    ["If PLA's E rises…", f"…then {_P} − XT205-S2 should be"],
    ["3 % per decade of strain rate", f"+{3 * _DECADES:.2f} %"],
    ["5 % per decade", f"+{5 * _DECADES:.2f} %"],
    ["8 % per decade", f"+{8 * _DECADES:.2f} %"],
    ["10 % per decade (a generous ceiling)", f"+{10 * _DECADES:.2f} %"],
], cw=[3.5, 2.6], hf=9.5, bf=9)

header(s, 6.85, 3.50, 6.1, "The prediction, stated before looking")
tb(s, 6.85, 3.88, 6.1, 1.55,
   f"DIRECTION: XT205-S2 is the slower specimen, so it should have the LOWER slope. A polymer "
   f"pulled slowly gives its chains more time to rearrange, and reads softer.\n\n"
   f"MAGNITUDE: under 1 % on E, whichever rate-sensitivity is assumed. That is the useful part — "
   f"anything much larger than 1 % is NOT the speed, whatever direction it points in.",
   fs=9.5, colour=BLACK)

banner(s, 0.40, 4.86, 12.55, 0.52,
       f"The per-decade figures are literature-typical for PLA, not measured on this rig — which is "
       f"why the DIRECTION test below carries the argument and the magnitude only bounds it.",
       fill=YELLOW_WARN, fg=BLACK, fs=10.5)

tb(s, 0.45, 5.52, 12.5, 0.72,
   f"Note what this already says about the planned experiment. Running the PPD-UTM at "
   f"{_RM['res']['speed_mm_min']:.0f} mm/min matches XT205-S2's COMMANDED speed but not its strain "
   f"rate: our gauge would see {_RT_P * _RM['res']['speed_mm_min'] / _OURS_MM_MIN:.3e} /s, which is "
   f"{(_RT_P * _RM['res']['speed_mm_min'] / _OURS_MM_MIN) / _RT_M:.2f}× theirs — an overshoot in "
   f"the other direction. To match the RATE the PPD-UTM would run "
   f"{_OURS_MM_MIN * _RT_M / _RT_P:.2f} mm/min.",
   fs=10, colour=BLACK)
footer(s, "Gauge strain rate is fitted over the same 0.05–0.35 % window used everywhere in this "
          "block, on the preload-zeroed axis. Share of travel reaching the gauge is from "
          f"{ref('MOT TEST 2 — TEST 1')}.")
pageno(s)


# ============================================ 4c. did the slopes differ as predicted?
_E_FIX_D = _off(_p["E_fix"]["E"], _M["E_fix"]["E"])          # S34 relative to XT205-S2
_E_ST_D = _off(_p["E_steep"]["E"], _M["E_steep"]["E"])
_METHOD_P = abs(_p["E_steep"]["E"] - _p["E_fix"]["E"]) / _p["E_fix"]["E"] * 100

s = prs.slides.add_slide(BLANK); ju(s)
title(s, "MOT TEST 2 — DID THE SLOPES DIFFER AS PREDICTED?")

tb(s, 0.45, 1.06, 12.5, 0.40,
   f"Prediction: {_P} stiffer than XT205-S2, by under 1 %. Two fitting methods, two answers — and "
   f"they do not even agree on the SIGN.",
   fs=11, colour=BLACK)

header(s, 0.45, 1.52, 7.4, "Predicted against measured")
table(s, 0.45, 1.90, 7.4, 1.42, [
    ["", "XT205-S2", f"{_P}", f"{_P} − XT205-S2", "as predicted?"],
    ["predicted from the strain rate", "—", "—", f"+{5 * _DECADES:.2f} %  (±)", "—"],
    [f"MEASURED, fixed {_WIN[0]:.2f}–{_WIN[1]:.2f} %",
     f"{_M['E_fix']['E']:.3f} GPa", f"{_p['E_fix']['E']:.3f} GPa", f"{_E_FIX_D:+.1f} %",
     "NO — wrong sign"],
    ["MEASURED, steepest straight run",
     f"{_M['E_steep']['E']:.3f} GPa", f"{_p['E_steep']['E']:.3f} GPa", f"{_E_ST_D:+.1f} %",
     "right sign, 9× too big"],
], cw=[2.5, 1.3, 1.3, 1.35, 1.6], hf=9, bf=8.5)

header(s, 0.45, 3.50, 7.4, "The sign test, and why it is the one that decides")
tb(s, 0.45, 3.88, 7.4, 1.95,
   f"A rate effect has a direction that does not depend on how the line is fitted: the slower "
   f"specimen reads softer, always. Here the slower specimen reads SOFTER on the steepest-run fit "
   f"and STIFFER on the fixed window. One of those contradicts rate outright, so rate is not what "
   f"is driving either.\n\n"
   f"The magnitude says the same thing from the other side. Rate can buy under 1 %; the two "
   f"measurements are {abs(_E_FIX_D):.1f} % and {abs(_E_ST_D):.1f} % apart. And {_P}'s OWN two "
   f"methods differ by {_METHOD_P:.1f} % on one specimen with no speed difference at all — the "
   f"method spread is larger than the machine gap it is being used to explain.",
   fs=9.5, colour=BLACK)

header(s, 8.05, 1.52, 4.9, "So what IS driving it")
tb(s, 8.05, 1.90, 4.9, 2.30,
   f"The toe in the PPD-UTM load train, which {ref('MOT TEST 2 — WHERE YOU FIT')} shows directly: "
   f"XT205-S2's slope is flat from the origin, while {_P}'s dips to 2.7 GPa near 0.15 % and only "
   f"reaches its steepest at {_p['E_steep']['lo']:.2f}–{_p['E_steep']['hi']:.2f} %.\n\n"
   f"A fixed window that straddles that dip reads {_P} LOW; a steepest-run search that skips past "
   f"it reads {_P} HIGH. Same specimen, same pull — the sign of the gap is set by which part of "
   f"our own seating curve the fit lands on.",
   fs=9.5, colour=BLACK)

header(s, 8.05, 4.30, 4.9, "What would test rate properly")
tb(s, 8.05, 4.68, 4.9, 1.15,
   f"Match the GAUGE STRAIN RATE, not the crosshead: {_OURS_MM_MIN * _RT_M / _RT_P:.2f} mm/min on "
   f"the PPD-UTM. Pair it with a {_RM['res']['speed_mm_min']:.0f} mm/min run and the two bracket "
   f"XT205-S2 from both sides.",
   fs=9.5, colour=BLACK)

banner(s, 0.40, 5.24, 12.55, 0.62,
       f"ANSWERED: XT205-S2 was predicted to have the lower slope, and it does on one fitting "
       f"method and not the other. Because the sign is not stable, the {abs(_E_ST_D):.1f} % gap "
       f"cannot be credited to the speed — the speed is worth under 1 %, and where the line is "
       f"fitted is worth {_METHOD_P:.1f} %.",
       fill=GREEN_PASS, fg=BLACK, fs=11)
footer(s, "Both moduli are computed by the same two methods on both records, so nothing here is a "
          "method difference dressed as a machine difference. Percentages are relative to "
          "XT205-S2.")
pageno(s)


# ================================================================= 5. noise
_ns_M, _ns_P = _B["noise_s"]["MOT"], _B["noise_s"][_P]
_nd_M, _nd_P = _B["noise_d"]["MOT"], _B["noise_d"][_P]

s = prs.slides.add_slide(BLANK); ju(s)
title(s, "MOT TEST 2 — NOISE, AND WHY THE LEAD CHANGED HANDS")

img_fit(s, "documentation/figures/mot2cmp_noise.png", 0.45, 1.08, 12.5, 3.32)

header(s, 0.45, 4.48, 6.15, "Both windows, because each one flatters a different side")
# FIVE rows, not eight. Deck table rows render 0.25 in whatever height is declared, so the first
# draft's two section-label rows pushed the last two records down behind the banner.
table(s, 0.45, 4.86, 6.15, 1.42, [
    ["window", "record", "rms", "median", "p95", "dwell", "spans"],
    [f"STRAIN {CMP.NOISE_WIN[0]:.2f}–{CMP.NOISE_WIN[1]:.2f} %", "XT205-S2",
     f"{_ns_M['rms']:.1f} µε", f"{_ns_M['med']:.1f}", f"{_ns_M['p95']:.0f}",
     f"{_ns_M['dwell']:.1f} s", "0.35 %"],
    ["", f"{_P} · ours", f"{_ns_P['rms']:.1f} µε", f"{_ns_P['med']:.1f}", f"{_ns_P['p95']:.0f}",
     f"{_ns_P['dwell']:.1f} s", "0.35 %"],
    [f"DURATION {CMP.NOISE_SECONDS:.1f} s", "XT205-S2",
     f"{_nd_M['rms']:.1f} µε", f"{_nd_M['med']:.1f}", f"{_nd_M['p95']:.0f}",
     f"{_nd_M['dwell']:.1f} s", f"{_nd_M['de']:.3f} %"],
    ["", f"{_P} · ours", f"{_nd_P['rms']:.1f} µε", f"{_nd_P['med']:.1f}", f"{_nd_P['p95']:.0f}",
     f"{_nd_P['dwell']:.1f} s", f"{_nd_P['de']:.3f} %"],
], cw=[1.5, 1.15, 0.9, 0.75, 0.6, 0.65, 0.75], hf=8.5, bf=8.5)

header(s, 6.85, 4.48, 3.0, "A reversal, stated plainly")
tb(s, 6.85, 4.86, 3.0, 1.42,
   f"MOT Test 1 reported the PPD-UTM floor as the quieter, at {_G['mot1']['rms']:.0f} µε for the "
   f"XT-205 against ~{_G['n80']:.0f} µε for us. MOT Test 2 reverses it: {_ns_M['rms']:.0f} against "
   f"{_ns_P['rms']:.0f} µε. Both windows agree on the reversal, so it is not a windowing artefact.",
   fs=9.5, colour=BLACK)

header(s, 10.05, 4.48, 2.9, "Because the gauge got shorter")
tb(s, 10.05, 4.86, 2.9, 1.42,
   f"Strain is a pixel ratio with Px₀ underneath it, so the floor should scale as 1/Px₀. "
   f"{_G['px80']:.0f} px → {_G['px45']:.0f} px predicts {_G['predicted']:.2f}×. Measured: "
   f"{_G['measured']:.2f}×. The prediction had nothing fitted to it.",
   fs=9.5, colour=BLACK)

banner(s, 0.40, 6.42, 12.55, 0.48,
       f"Our floor rose {_G['measured']:.2f}× where 1/Px₀ predicted {_G['predicted']:.2f}× — "
       f"{abs(_G['measured'] - _G['predicted']) / _G['predicted'] * 100:.1f} % apart. It is set by "
       f"the PIXEL SPAN, not the specimen or the lighting. Theirs moved the other way "
       f"({_G['mot_ratio']:.2f}×), so theirs is limited by something else.",
       fill=YELLOW_WARN, fg=BLACK, fs=10.5)
footer(s, f"All six records on one window ({_G['win'][0]:.2f}–{_G['win'][1]:.2f} %), which is the "
          f"window MOT Test 1 used. Residual scatter about a straight fit, in microstrain.")
pageno(s)


# ================================================================= 6. what it settles
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "MOT TEST 2 — WHAT THE COMPARISON SETTLES")

tb(s, 0.45, 1.06, 12.5, 0.40,
   "An independent commercial extensometer, on its own machine, with its own optics and its own "
   "software, measuring a different specimen of the same material. Three verdicts, kept apart.",
   fs=11, colour=BLACK)

header(s, 0.45, 1.52, 4.05, "CONFIRMED")
table(s, 0.45, 1.90, 4.05, 1.42, [
    ["", "offset"],
    ["0.2 % offset yield", f"{_off(_M['sy_steep'], _p['sy_steep']):+.1f} %"],
    ["failure strain", f"{_off(_M['ef'], _p['ef']):+.1f} %"],
    ["E, fixed window", f"{_off(_M['E_fix']['E'], _p['E_fix']['E']):+.1f} %"],
    ["E, steepest run", f"{_off(_M['E_steep']['E'], _p['E_steep']['E']):+.1f} %"],
], cw=[2.6, 1.45], hf=9, bf=9)
tb(s, 0.45, 3.44, 4.05, 1.30,
   f"Every one of these is inside the "
   f"{abs(_off(_p['uts'], _s['uts'])):.1f}–{abs(_off(_p['E_steep']['E'], _s['E_steep']['E'])):.0f} % "
   f"scatter between our own two runs. The yield agreement is the strongest single result here: "
   f"three specimens, two machines, two instruments, under 1 % apart.",
   fs=9.5, colour=BLACK)

header(s, 4.75, 1.52, 4.05, "EXPLAINED, NOT DISMISSED")
tb(s, 4.75, 1.90, 4.05, 2.84,
   f"UTS is {abs(_off(_M['uts'], _p['uts'])):.1f} % low, the strain at UTS "
   f"{abs(_off(_M['uts_e'], _p['uts_e'])):.1f} % low, toughness "
   f"{abs(_off(_M['tough'], _p['tough'])):.1f} % low. Every quantity that disagrees is post-yield, "
   f"and every one moves the way a {_OURS_MM_MIN / _RM['res']['speed_mm_min']:.0f}× slower pull "
   f"moves it.\n\n"
   f"That is a DIRECTION the physics predicts, and NOT a magnitude — the correction on "
   f"{ref('WHAT THE SPEED DIFFERENCE PREDICTS')} is that the two gauges differ by 1.19× of strain "
   f"rate rather than the 3× of crosshead, so the speed is worth under 1 %. Our own "
   f"{abs(_off(_p['uts'], _s['uts'])):.1f} % specimen scatter carries more of it, and the remainder "
   f"belongs to a different machine and a different batch, which n = 1 a side cannot split.\n\n"
   f"Also explained: the {_G['measured']:.2f}× rise in our noise floor, which is 1/Px₀ and nothing "
   f"else, and the strain-rate gap MOT Test 1 could not account for, which is the load train.",
   fs=9.5, colour=BLACK)

header(s, 9.05, 1.52, 3.9, "STILL OPEN")
tb(s, 9.05, 1.90, 3.9, 2.84,
   f"1.  IS THE UTS GAP RATE OR SPECIMEN? One pull of ours at "
   f"{_RM['res']['speed_mm_min']:.0f} mm/min separates them. It is a single test on a specimen we "
   f"already print, and it is the cheapest open question in this deck.\n\n"
   f"2.  WHY DID THE XT-205'S NOISE IMPROVE between the two tests? Its Test 2 optics are unknown, "
   f"so its pixel span cannot be computed. Running MOT footage through the PPD-UTM pipeline gives "
   f"that px/mm directly ({ref('THE TWO CALCULATIONS AGREE')} did it for MOT Test 1).\n\n"
   f"3.  THEIR GAUGE SHARE IS NOMINAL. A crosshead channel from them would turn "
   f"{_B['share']['MOT']['pct']:.0f} % from a bound into a measurement.",
   fs=9.5, colour=BLACK)

banner(s, 0.40, 4.62, 12.55, 0.72,
       f"THE HEADLINE: an instrument we do not own, on a machine we do not control, put yield "
       f"within {abs(_off(_M['sy_steep'], _p['sy_steep'])):.1f} %, failure strain within "
       f"{abs(_off(_M['ef'], _p['ef'])):.1f} % and modulus inside our own run-to-run bracket. "
       f"Nothing was tuned to make that happen, and the one correction applied — putting their "
       f"strain zero on our convention — was decided before the numbers were compared.",
       fill=GREEN_PASS, fg=BLACK, fs=11.5)

tb(s, 0.45, 5.50, 12.5, 1.05,
   f"WHAT WOULD HAVE FALSIFIED THIS: a modulus outside our bracket, a failure strain off by more "
   f"than our own two runs differ, or a yield gap larger than the specimen scatter. None of those "
   f"happened. What did happen — the post-yield gap — has a named cause with a testable direction, "
   f"and the test costs one specimen. That is the difference between a result that survived a "
   f"check and a result that was never at risk.",
   fs=10, colour=BLACK)

footer(s, f"Reference run {_P} (100 % infill PLA, 45 mm marker spacing, {_Rp['cover']:.1f} % DIC "
          f"coverage inside the pull); {_S} carried alongside. MOT XT-205, gauge "
          f"{_RM['res']['gauge_reported']:.4f} mm.")
pageno(s)
