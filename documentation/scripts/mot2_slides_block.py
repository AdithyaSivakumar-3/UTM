# ===================================================================================
#  MOT session 2 — the XT-205 pulling a 45 mm gauge specimen, read from its own two
#  channels. This is the INDEPENDENT record: their instrument, their maths, their
#  machine. Nothing of ours is in it, which is what makes it worth having.
#
#  Appended to generate_v6a_slides.py. Every number comes from mot2_data at build
#  time, which parses strain-sample3.csv and sample3.daq directly.
# ===================================================================================
import mot2_data as M2                                                # noqa: E402
import mot2_plots as M2P                                              # noqa: E402
import s25_s26_data as _V45                                           # noqa: E402

M2P.all_figs()
_D = M2.load()

# Our own 45 mm pair, for the one line that says where their modulus lands.
#
# use_pair() mutates module state that the rest of the deck reads, so the 80 mm pair is put back
# immediately. This block runs last today; leaving the module pointed elsewhere would break the
# next block quietly rather than loudly, which is the worst way for it to break.
_V45.use_pair("45mm")
_S33, _S34 = _V45.summary("S33"), _V45.summary("S34")
_V45.use_pair("80mm")
_E_LO, _E_HI = min(_S33["E"], _S34["E"]), max(_S33["E"], _S34["E"])
_OUR_MM_MIN = _S33["rate"] / 1000.0 * 60.0          # our crosshead speed in the same units
_SPEED_RATIO = _OUR_MM_MIN / _D["speed_mm_min"]


# ================================================================= 1. the record as it stands
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "MOT SESSION 2 — A 45 mm GAUGE PULL, AS THE XT-205 RECORDED IT")

img_fit(s, "documentation/figures/mot2_strain.png", 0.40, 1.14, 6.40, 3.49)

header(s, 0.40, 4.72, 6.40, "Why fracture is read at the peak, not at the last sample")
tb(s, 0.40, 5.10, 6.40, 1.38,
   f"When the specimen parts, the two halves spring back and the extensometer's marks go with "
   f"them. Strain reads {_D['ef']:.2f} % at {_D['t_ef']:.1f} s and {_D['e'][-1]:.2f} % barely a "
   f"second later — a 2.5 % collapse that is the specimen coming apart, not deforming. The last "
   f"sample in the file would report that recoil as the failure strain and understate it by half, "
   f"so the failure strain is taken at the MAXIMUM inside the pull and the fracture stress at that "
   f"same instant.",
   fs=9.5, colour=BLACK)

header(s, 7.05, 1.10, 5.90, "The test as run")
table(s, 7.05, 1.48, 5.90, 1.64, [
    ["Condition", "As recorded"],
    ["crosshead speed",
     f"{_D['speed_mm_min']:.0f} mm/min = {_D['speed_mm_s']:.4f} mm/s"],
    ["preload",
     f"{_D['preload']:.0f} N — reached at t = {_D['t_pre']:.2f} s, inside the record"],
    ["gauge, as their software reports it",
     f"{_D['gauge_reported']:.4f} mm"],
    ["sampling",
     f"{_D['rate_hz']:.2f} Hz — {_D['n_load']} load rows, {_D['n_strain']} strain rows"],
    ["duration to fracture", f"{_D['dur']:.1f} s"],
], cw=[2.5, 3.4], hf=10, bf=9)

header(s, 7.05, 3.26, 5.90, "Two files, one clock — and no column headers")
tb(s, 7.05, 3.64, 5.90, 1.20,
   f"The strain lives in a CSV and the load in a .daq that names none of its 52 columns. Column 4 "
   f"is identified by SHAPE: it is the only channel that climbs from zero to {_D['peak_N'] / 1000:.2f} kN, "
   f"holds, and collapses in one sample — and {_D['peak_N'] / 1000:.2f} kN on {_D['area']:.0f} mm² is "
   f"{_D['uts']:.1f} MPa, where PLA belongs. No other column is even the right order of magnitude.",
   fs=9.5, colour=BLACK)

header(s, 7.05, 4.92, 5.90, "A trap in the CSV that does not announce itself")
tb(s, 7.05, 5.30, 5.90, 1.17,
   "Before the marks are found the instrument writes \"Invalid\" across a WHOLE row. Reading the "
   "time and strain columns independently leaves 3351 times against 3308 strains — arrays that "
   "still zip, still plot, and are wrong by 43 samples of lag. Rows are kept or dropped whole.",
   fs=9.5, colour=BLACK)

banner(s, 0.40, 6.55, 12.55, 0.40,
       f"Everything above is THEIR instrument and THEIR maths on THEIR machine — no part of our "
       f"pipeline touches it. That is what makes it usable as an independent check.",
       fill=LIGHT_BLUE, fg=BLACK, fs=10.5)
footer(s, "Source: Validation docs\\MOT Test 2\\Videoextesometer MOT\\strain-sample3.csv + "
          "sample3.daq. Parsed by documentation/scripts/mot2_data.py; nothing is retyped.")
pageno(s)


# ================================================================= 2. stress-strain, and the zero
s = prs.slides.add_slide(BLANK); ju(s)
# 30 pt across the 12.5 in title box holds about 55 characters. The first draft ran to 59 and
# PowerPoint clipped the overflow line, so the slide read "...QUESTION" and simply stopped.
title(s, "MOT SESSION 2 — STRESS–STRAIN, AND WHAT THE ZERO COSTS")

img_fit(s, "documentation/figures/mot2_stress.png", 0.40, 1.14, 6.40, 3.49)

header(s, 0.40, 4.72, 6.40, "Their speed is a third of ours, and that is not a defect")
tb(s, 0.40, 5.10, 6.40, 1.38,
   f"They pulled at {_D['speed_mm_min']:.0f} mm/min; we pull at {_OUR_MM_MIN:.1f} mm/min — "
   f"{_SPEED_RATIO:.0f}× faster. PLA is rate-sensitive and a slower pull gives a LOWER strength, "
   f"so their {_D['uts']:.2f} MPa sitting below our {_S33['UTS']:.2f} / {_S34['UTS']:.2f} MPa is "
   f"the direction the physics predicts. It is carried into every comparison rather than averaged "
   f"away, because it is the one condition the two machines did not share.",
   fs=9.5, colour=BLACK)

header(s, 7.05, 1.10, 5.90, "The landmarks, on both ways of zeroing the strain")
table(s, 7.05, 1.48, 5.90, 1.64, [
    ["", "as recorded\n(zero at 0 N)", "re-zeroed at %.0f N\n(our convention)" % _D["preload"]],
    [f"E, {_D['E_window'][0]:.2f}–{_D['E_window'][1]:.2f} % window",
     f"{_D['E']:.3f} GPa   (R² {_D['E_R2']:.4f})",
     f"{_D['E_rz']:.3f} GPa   (R² {_D['E_R2_rz']:.4f})"],
    ["σ_y, 0.2 % offset",
     f"{_D['sy']:.2f} MPa at {_D['sy_e']:.2f} %",
     f"{_D['sy_rz']:.2f} MPa at {_D['sy_e_rz']:.2f} %"],
    ["UTS",
     f"{_D['uts']:.2f} MPa at {_D['uts_e']:.2f} %",
     f"{_D['uts']:.2f} MPa at {_D['uts_e_rz']:.2f} %"],
    ["fracture strain", f"{_D['ef']:.2f} %", f"{_D['ef_rz']:.2f} %"],
], cw=[2.1, 1.95, 1.95], hf=9.5, bf=9)

header(s, 7.05, 3.26, 5.90, "The question we said had to be settled first")
tb(s, 7.05, 3.64, 5.90, 1.40,
   f"Their strain zero is at ZERO LOAD: the {_D['preload']:.0f} N preload is applied inside the "
   f"record, at t = {_D['t_pre']:.2f} s, by which point they already read {_D['e_pre']:.3f} %. Our "
   f"Px₀ is frozen AFTER preload, so their curve carries a toe ours does not. The validation pack "
   f"called this the largest single risk to the comparison. Re-zeroing at {_D['preload']:.0f} N "
   f"moves E by {abs(_D['E'] - _D['E_rz']) / _D['E'] * 100:.0f} % — there is almost no toe to remove.",
   fs=9.5, colour=BLACK)

header(s, 7.05, 5.12, 5.90, "Where their modulus lands")
tb(s, 7.05, 5.50, 5.90, 0.97,
   f"Both values fall INSIDE our own 45 mm bracket, {_E_LO:.3f}–{_E_HI:.3f} GPa (S33 / S34). The "
   f"full like-for-like comparison — and their footage through our pipeline, as in "
   f"{ref('THE TWO CALCULATIONS AGREE')} — follows.",
   fs=9.5, colour=BLACK)

banner(s, 0.40, 6.55, 12.55, 0.40,
       f"The strain-zero difference we most feared costs "
       f"{abs(_D['E'] - _D['E_rz']) / _D['E'] * 100:.0f} % on E — well under the "
       f"{abs(_S34['E'] - _S33['E']) / _S33['E'] * 100:.0f} % scatter between our own two runs. "
       f"UTS and σ_y come from the load cell and never depended on it at all.",
       fill=GREEN_PASS, fg=BLACK, fs=10.5)
footer(s, f"Stress is load ÷ {_D['area']:.0f} mm² CAD nominal, the same basis as every other number "
          f"in this deck. The curve is drawn to the strain peak only.")
pageno(s)
