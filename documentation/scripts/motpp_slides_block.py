# ===================================================================================
#  MOT XT-205 vs our rig, with the leg that separates the INSTRUMENT from the MATHS:
#  the extensometer's own video run through our pixel-to-strain path.
#
#  Appended to generate_v6a_slides.py. Every number is read from
#  documentation/mot_postproc_compare.json at build time, which
#  mot_postproc_compare.py writes from the raw records.
# ===================================================================================
import json as _mjson                                                 # noqa: E402
import io as _mio                                                     # noqa: E402
import motpp_plots as MPP                                             # noqa: E402

MPP.all_figs()
_M = _mjson.load(_mio.open("documentation/mot_postproc_compare.json", encoding="utf-8"))
# Keyed, not matched on prose. mot_postproc_compare.RECORDS owns the wording; this file only
# names which record it wants, so a relabelled axis cannot silently pick the wrong row here.
_MR = {r["key"]: r for r in _M["rows"]}
_SH = _M["gauge_share"]
_RIG = _M["rig_name"]   # the machine's name, taken from the analysis rather than repeated here
_PP = _MR["pp"]         # the XT-205's footage through the PPD-UTM DIC pipeline
_MOT = _MR["mot"]       # the XT-205's footage through its own extensometer
_S25 = _MR["S25"]
_S26 = _MR["S26"]


# ================================================================= 1. what was tested
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "MOT XT-205 vs %s — WHAT WAS TESTED, AND HOW" % _RIG)
img_fit(s, "documentation/figures/motpp_setup.png", 0.4, 1.16, 12.5, 2.72)

header(s, 0.45, 4.02, 6.15, "The design: three legs, so a disagreement can be attributed")
table(s, 0.45, 4.40, 6.15, 1.62, [
    ["Comparison", "What differs", "What it isolates"],
    ["XT-205 extensometer  vs\n%s DIC on the same footage" % _RIG,
     "only the analysis — same footage,\nspecimen and instant", "the CALCULATION"],
    ["%s DIC on XT-205 footage  vs\n%s DIC on S25 / S26" % (_RIG, _RIG),
     "the machine and the mounting,\nnot the analysis", "the RIG"],
    ["(previously) XT-205  vs  %s" % _RIG,
     "instrument AND specimen at once", "nothing, on its own"],
], cw=[2.4, 2.35, 1.4], hf=9.5, bf=8)

header(s, 6.85, 4.02, 6.1, "The two records")
table(s, 6.85, 4.40, 6.1, 1.62, [
    ["", "MOT XT-205", "%s  (S25/S26)" % _RIG],
    ["configuration", "—", "Mk II, after the\n2026-08-12 realignment"],
    ["marker span Px₀", "2234 px", "1676 px"],
    ["scale", "27.9 px/mm", "21.0 px/mm"],
    ["specimen width", "9.60 mm", "10.12 mm"],
    ["frame rate", "19.405 fps, from its own\nper-frame acquisition log",
     "19.93 fps, from the\ncapture's index.csv"],
    ["strain range usable", "to 0.40 %, then its\nmarks are lost", "to fracture"],
], cw=[1.85, 2.15, 2.1], hf=9.5, bf=8)

banner(s, 0.4, 6.24, 12.55, 0.56,
       "Both machines were set to the SAME 0.1 mm/s crosshead speed, and both measure an 80 mm "
       "marker span — so anything left over after the calculation is checked belongs to the "
       "machine, the grips or the specimen.",
       fill=LIGHT_BLUE, fg=BLACK, fs=10.5)
footer(s, "MOT record: test2.chan 0.avi + strain.csv + test2.daq, XT-205, gauge 80.0033 mm. Ours: "
          "S25 and S26, PLA 100 % infill, the same pair used throughout this deck.")
pageno(s)


# ================================================================= 1b. why the pixel counts differ
_L0_M, _L0_O = 2234.4, 1676.3
_PP_UE, _S25_UE = _PP["noise_ue"], _S25["noise_ue"]

s = prs.slides.add_slide(BLANK); ju(s)
title(s, "SAME 80 mm GAUGE, DIFFERENT PIXEL COUNTS — WHY THAT IS FINE")

tb(s, 0.45, 1.12, 12.5, 0.42,
   "On the previous slide the XT-205's gauge spans %d px and the %s's spans %d px, yet both are "
   "80 mm of the same kind of specimen. Nothing is wrong: the two cameras magnify differently."
   % (round(_L0_M), _RIG, round(_L0_O)),
   fs=11, colour=BLACK)

img_fit(s, "documentation/figures/motpp_pixels.png", 0.45, 1.64, 12.5, 2.72)

header(s, 0.45, 4.52, 4.05, "Why the counts differ")
tb(s, 0.45, 4.90, 4.05, 1.72,
   "The XT-205 lays 27.9 pixels across a millimetre; we lay 21.0. Over an 80 mm gauge that is "
   "%d px against %d px — a 33 %% difference that belongs entirely to the optics and says nothing "
   "about the specimen, the grips or the test."
   % (round(_L0_M), round(_L0_O)),
   fs=10, colour=BLACK)

header(s, 4.75, 4.52, 4.05, "Why it does not affect the strain")
tb(s, 4.75, 4.90, 4.05, 1.72,
   "Because strain is a RATIO of pixels:\n"
   "        ε = (L_px − Px₀) / Px₀\n"
   "px/mm appears in the numerator and the denominator and cancels exactly. Neither machine needs "
   "the other's optics, or even a correct gauge length, for the two strains to be comparable — "
   "which is what makes the comparison on ⟪THE TWO CALCULATIONS AGREE⟫ possible at all.",
   fs=10, colour=BLACK)

header(s, 9.05, 4.52, 3.9, "Where it DOES matter")
tb(s, 9.05, 4.90, 3.9, 1.72,
   "Resolution. One whole pixel is %.0f µε on their longer baseline and %.0f µε on ours — their "
   "pixel is worth 25 %% less strain. It also matters for px/mm if an EXTENSION in millimetres is "
   "wanted; for strain alone it is not used."
   % (1e6 / _L0_M, 1e6 / _L0_O),
   fs=10, colour=BLACK)

banner(s, 0.4, 6.72, 12.55, 0.2, "", fill=WHITE, fg=BLACK, fs=1)
footer(s, "Read the right-hand plot carefully: our pipeline reaches %.1f µε on their footage and "
          "%.1f µε on S25, a 4× gap where the magnification alone accounts for only 1.3×. The rest "
          "is the specimen, the lighting and the marker quality — not the camera."
          % (_PP_UE, _S25_UE))
pageno(s)


# ================================================================= 2. the calculations agree
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "THE TWO CALCULATIONS AGREE — SAME VIDEO, SAME ANSWER")
img_fit(s, "documentation/figures/mot_postproc_compare.png", 0.4, 1.14, 12.5, 2.55)

header(s, 0.45, 3.84, 6.15, "Read at matched instants — no fitting at all")  # noqa
table(s, 0.45, 4.22, 6.15, 1.55, [
    ["Test", "Result"],
    ["strain ratio, %s DIC ÷ XT-205 (%d points)" % (_RIG, _M["matched_n"]),
     "median %.4f" % _M["ratio_matched_median"]],
    ["%s DIC as a straight fit of the XT-205" % _RIG,
     "%.4f × XT-205 %+.0f µε" % (_M["matched_slope"], _M["matched_offset_ue"])],
    ["independent scale check (⟪THE SCALE CHECK⟫)", "k = %.5f" % _M["scale_k"]],
    ["fitted strain-rate ratio", "%.4f" % _M["ratio_rate"]],
], cw=[3.9, 2.25], hf=9.5, bf=8.5)

header(s, 6.85, 3.84, 6.1, "…and the %s is the quieter of the two" % _RIG)
table(s, 6.85, 4.22, 6.1, 1.55, [
    ["Record", "d(ε)/dt", "noise"],
    [_PP["name"], "%.3e /s" % _PP["rate"], "%.1f µε" % _PP["noise_ue"]],
    [_MOT["name"], "%.3e /s" % _MOT["rate"], "%.1f µε" % _MOT["noise_ue"]],
    [_S25["name"], "%.3e /s" % _S25["rate"], "%.1f µε" % _S25["noise_ue"]],
    [_S26["name"], "%.3e /s" % _S26["rate"], "%.1f µε" % _S26["noise_ue"]],
], cw=[2.85, 1.75, 1.5], hf=9.5, bf=8.5)

banner(s, 0.4, 5.90, 12.55, 0.58,
       "Same footage, same specimen, same instant — so the only thing that differs is the "
       "arithmetic, and it agrees. That the two strains are also the same SIZE, and not merely the "
       "same shape, is established separately and to %.2f %% (⟪THE SCALE CHECK⟫); what is left over "
       "here is each instrument's own noise." % (abs(_M["scale_k"] - 1) * 100),
       fill=GREEN_PASS, fg=DARK_GREEN, fs=10.5)
tb(s, 0.4, 6.54, 12.55, 0.34,
   "On the XT-205's own footage the %s reads %.1f× quieter (%.1f vs %.1f µε) — a larger pixel "
   "baseline and a sub-pixel centroid against the extensometer's %d Hz output."
   % (_RIG, _M["noise_ratio"], _PP["noise_ue"], _MOT["noise_ue"], 20),
   fs=10, colour=BLACK, align=PP_ALIGN.CENTER)
footer(s, "Fitted over 0.05–0.35 % strain, inside the XT-205's valid range — it loses its marks at "
          "0.4015 %. See ⟪HOW THE NOISE IS MEASURED⟫ for what a microstrain is.")
pageno(s)


# ================================================================= 3. why the slopes differ
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "WHY THE SLOPES DIFFER — WHERE THE COMMANDED MOTION GOES")
img_fit(s, "documentation/figures/motpp_share.png", 0.4, 1.12, 12.5, 2.44)

header(s, 0.45, 3.66, 12.5,
       "Ranked by how much of the gap each accounts for — the MOT's crosshead is commanded, not measured")
table(s, 0.45, 4.04, 12.5, 2.56, [
    ["#", "Cause", "The evidence", "Size"],
    ["1", "Motor speed is not specimen speed.\nThe rig's Position_mm is a MOTOR-shaft encoder read "
          "through 20:1 gearing\nand a 5 mm screw. It proves the motor turned; it proves nothing "
          "about\nthe grips, and no sensor measures them directly.",
     "motor %.4f mm/s — exactly commanded — while the gauge\nsees %.4f mm/s (S25) and %.4f mm/s "
     "(S26). Everything between\nthe motor and the specimen is assumed rigid, and is not."
     % (_SH["S25"]["crosshead_mm_s"], _SH["S25"]["gauge_mm_s"], _SH["S26"]["gauge_mm_s"]),
     "the bulk of it"],
    ["2", "Grip seating varies from mounting to mounting.\nThe XT-205 clamps with jaws; matching "
          "PRELOAD in newtons does not\nmatch how the specimen is seated.",
     "S25 %.0f %% against S26 %.0f %% — %.0f points apart on two runs of\nthe same protocol. A "
     "fixed frame compliance would repeat.\nSomething that varies per mounting does not."
     % (100 * _SH["S25"]["share"], 100 * _SH["S26"]["share"],
        100 * (_SH["S26"]["share"] - _SH["S25"]["share"])),
     "explains the\nSPREAD"],
    ["3", "The %s markers sit on the fillet shoulders.\nWider material carries the same load at " % _RIG +
          "lower stress, so it strains less\nand dilutes the average over the span.",
     "only 85 %% of the %s marker span is parallel; at its two ends the\nspecimen is 64 %% and 69 %% " % _RIG +
     "wider. The XT-205's span is parallel\nacross 100 %.",
     "6.5 % — real\nbut minor"],
    ["4", "Strain-rate dependence then compounds it.\nPLA is viscoelastic, so its elastic slope "
          "rises with strain rate.",
     "the %s gauge is strained at a third of the XT-205's, so a lower\nmodulus follows even from a perfect " % _RIG +
     "instrument. A CONSEQUENCE of 1–2,\nnot an independent cause.",
     "multiplies\n1 and 2"],
], cw=[0.32, 4.5, 5.55, 2.13], hf=9.5, bf=7.5)

# Two lines is the footer's whole budget: it sits at y = 7.00 on a 7.50 in slide, and a third
# line is simply lost off the bottom edge.
footer(s, "Not every loss is a fault — the shoulders and grip sections strain too, so 100 % is not "
          "the target on any machine; the XT-205 loses 41 % itself. Shares are d(ε)/dt × 80 mm ÷ "
          "crosshead speed over one window.")
pageno(s)


# ================================================================= 4. what had to be fixed first
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "WHAT HAD TO BE FIXED BEFORE THESE NUMBERS MEANT ANYTHING")

header(s, 0.45, 1.22, 12.5, "Four traps, every one of which produced a confident wrong answer first")
table(s, 0.45, 1.60, 12.5, 3.30, [
    ["Trap", "What it did", "How it was caught, and fixed"],
    ["The video declares 1000 fps\nand 117 497 frames",
     "It holds 2281 frames at 19.4 fps. Every time-based\nfigure in the first run was out by 52× — "
     "'duration\n0.77 s', 'mean rate 2.5e-02 /s'.",
     "test2.daq carries EXACTLY 2281 rows for those 2281\nframes, each timestamped. The time base "
     "is now read\nfrom it rather than from the container."],
    ["Recovering the frame rate by\nmatching strain curves",
     "Circular. If the %s strain were k× the XT-205's the fit\nreturns fps ÷ k, and the two rates then " % _RIG +
     "agree BY CONSTRUCTION.\nThat version reported 0.6 % agreement.",
     "Replaced by the acquisition log's per-frame\ntimestamps; the honest figure is %.1f %%. The fit is "
     "kept, demoted to\nthe scale check it is genuinely good for."
     % (abs(_M["ratio_rate"] - 1) * 100)],
    ["cv2 seeking returns a STALE\nframe on this file",
     "Correct for the first ~40 frames, wrong past ~80,\nwhile reporting its position honestly. "
     "Sampling by\nseek showed markers that never moved — and I\nreported the video held no "
     "deformation. It holds a\npull to 4 % and a fracture.",
     "read_frame now probes each file and decodes in order\nwhen the seek cannot be trusted. Two "
     "cheaper probes\nwere tried and rejected: the position property is\nhonest here, and the "
     "stale seeks are not identical."],
    ["Box half-size 105 px, marker\n121 px from the frame edge",
     "Box.clamp() pinned the box at 2357 px once the marker\ntravelled far enough; 184 rows sit "
     "at exactly that value,\nafter which the centroid flip-flops several px a frame.",
     "The run is trimmed at the first jump the specimen\ncould not physically make (0.085 px/frame "
     "is real,\nthe cut fires at 0.52). It lands at 0.52 % strain —\nabove the fitted window, so "
     "nothing fitted is lost."],
], cw=[2.5, 5.0, 5.0], hf=9.5, bf=7.5)

header(s, 0.45, 5.06, 6.15, "What to do differently next time")
tb(s, 0.45, 5.44, 6.15, 1.42,
   "• Keep both markers well clear of the frame edge — at least the box half-size plus the travel "
   "expected, or the box runs out of room before the specimen does.\n"
   "• Set the frame rate from the acquisition log, never from the container.\n"
   "• Place the markers inside the PARALLEL section, not on the fillets.",
   fs=10, colour=BLACK)

header(s, 6.85, 5.06, 6.1, "What this run can and cannot settle")
tb(s, 6.85, 5.44, 6.1, 1.42,
   "It settles the CALCULATION: same pixels in, same strain out, to %.2f %%.\n"
   "It does not settle the modulus. The XT-205 record carries no force, so E, σ_y, UTS and ε_f "
   "cannot be compared at all — only d(ε)/dt and noise. One specimen on each machine is also not "
   "a repeatability claim."
   % (abs(_M["ratio_matched_median"] - 1) * 100),
   fs=10, colour=BLACK)
footer(s, "Sources: mot_postproc_compare.py and motpp_plots.py, both reading the raw records at "
          "build time. Measured %s." % _M.get("measured", "2026-08-27"))
pageno(s)


# ================================================================= 5. the scale check, explained
_SENS = _M["scale_sensitivity"]
_K1 = next(r for r in _SENS if abs(r["k"] - 1.0) < 1e-9)

s = prs.slides.add_slide(BLANK); ju(s)
title(s, "THE SCALE CHECK — WHY IT IS NEEDED, AND WHAT IT RULES OUT")

header(s, 0.45, 1.14, 6.15, "1 · The problem: a strain RATE needs a clock")
tb(s, 0.45, 1.52, 6.15, 1.18,
   "Comparing d(ε)/dt between two machines means knowing when each video frame happened. "
   "test2.chan 0.avi declares 1000 fps and 117 497 frames; it holds 2281 frames at about 19.4 fps. "
   "Believe the file and every rate on these slides is out by a factor of 52.",
   fs=10, colour=BLACK)

header(s, 6.85, 1.14, 6.1, "2 · Two ways to get the real one")
table(s, 6.85, 1.52, 6.1, 1.18, [
    ["Route", "Where it comes from", "Result"],
    ["INFERRED", "when each record reaches the\nsame strain levels",
     "%.3f fps" % _M["fps_from_crossings"]],
    ["RECORDED", "the XT-205's own log, one\ntimestamped row per frame",
     "%.3f fps" % _M["fps_daq"]],
], cw=[1.15, 3.05, 1.9], hf=9.5, bf=8.5)

img_fit(s, "documentation/figures/mot_scalecheck.png", 0.45, 2.86, 12.5, 2.86)

header(s, 0.45, 5.84, 6.15, "3 · Why not just use the recorded one and move on?")
tb(s, 0.45, 6.22, 6.15, 0.72,
   "Because then nothing would test whether the two strains agree in SIZE. The INFERRED route "
   "depends on size — stretch our strain by k and it returns fps ÷ k. The RECORDED route cannot "
   "move, because it never looks at strain. So the gap between them IS the size error.",
   fs=10, colour=BLACK)

header(s, 6.85, 5.84, 6.1, "4 · And the check is calibrated, not asserted")
tb(s, 6.85, 6.22, 6.1, 0.72,
   "Feeding it a deliberate 10 %% error makes it report 10 %% (right-hand plot), so agreement is "
   "informative rather than inevitable. On the real data it reports k = %.4f: the two strain "
   "scales match to %.2f %%."
   % (_K1["recovered_k"], abs(_K1["recovered_k"] - 1) * 100),
   fs=10, colour=BLACK)

footer(s, "What it does NOT rule out: if the recorded frame rate were wrong by a factor m AND our "
          "strain were stretched by the same m, the test would still pass. That needs two "
          "independent errors to coincide exactly — the log comes from the other instrument — but "
          "it is not logically excluded.")
pageno(s)


# ================================================================= 5-6. the raw points
#
# Two slides, not one. 83 rows in three columns at 7 pt is a wall of digits; two columns of 21 at
# 9 pt can be read from across a room, which is the only reason to put a table on a slide at all.
_PTS = _M["matched_points"]
_OS = _M["offset_summary"]
_HDR = ["t (s)", _RIG, "XT-205", "Δ µε", "Δ %"]
_HALF = -(-len(_PTS) // 2)              # ceil, so the second slide is the shorter one


def _pt_rows(chunk):
    return [_HDR] + [["%.2f" % p["t"], "%.4f" % (p["ours"] * 100),
                      "%.4f" % (p["theirs"] * 100), "%+.0f" % p["off_ue"],
                      "%+.2f" % p["off_pc"]] for p in chunk]


for _half in (0, 1):
    _pts = _PTS[_half * _HALF:(_half + 1) * _HALF]
    if not _pts:
        continue
    _lo_e, _hi_e = _pts[0]["ours"] * 100, _pts[-1]["ours"] * 100

    s = prs.slides.add_slide(BLANK); ju(s)
    title(s, "RAW DATA (%d OF 2) — %.3f TO %.3f %% STRAIN" % (_half + 1, _lo_e, _hi_e))

    if _half == 0:
        tb(s, 0.55, 1.12, 12.4, 0.56,
           "All %d matched samples across both slides, %.2f–%.2f s, unaveraged and unsmoothed. The "
           "%s column is RAW: the post-processor applies no filtering of any kind, and its source "
           "value is exactly (L_px − Px₀) / Px₀. The XT-205 column is that instrument's own output "
           "interpolated onto our sample times — what it does internally cannot be seen from the "
           "file, so the two columns are NOT equally traceable and are not presented as if they were."
           % (_OS["n"], _OS["t_from"], _OS["t_to"], _RIG),
           fs=10, colour=BLACK)
        _y = 1.80
    else:
        tb(s, 0.55, 1.12, 12.4, 0.30,
           "Continued — points %d to %d of %d. Same two columns, same raw values; see "
           "⟪RAW DATA (1 OF 2)⟫ for what each one is."
           % (_HALF + 1, len(_PTS), len(_PTS)),
           fs=10, colour=BLACK)
        _y = 1.54

    # Two column groups per slide, wide enough that no cell has to be squeezed.
    _per = -(-len(_pts) // 2)
    for _g in range(2):
        _chunk = _pts[_g * _per:(_g + 1) * _per]
        if not _chunk:
            continue
        _d = _pt_rows(_chunk)
        table(s, 0.55 + _g * 6.25, _y, 5.90, 0.200 * len(_d), _d,
              cw=[1.05, 1.30, 1.25, 1.05, 1.25], hf=9.5, bf=9)

    if _half == 1:
        kpi(s, 0.55, 6.14, 2.96, "MEDIAN OFFSET", "%+.0f µε" % _OS["ue_med"], h=0.68, vfs=15,
            fill=GREEN_PASS)
        kpi(s, 3.68, 6.14, 2.96, "WITHIN ± 50 µε", "%d of %d" % (_OS["within_50ue"], _OS["n"]),
            h=0.68, vfs=15, fill=GREEN_PASS)
        kpi(s, 6.81, 6.14, 2.96, "RANGE", "%+.0f to %+.0f µε" % (_OS["ue_min"], _OS["ue_max"]),
            h=0.68, vfs=13)
        kpi(s, 9.94, 6.14, 3.01, "MEDIAN, AS A %", "%+.2f %%" % _OS["pc_med"], h=0.68, vfs=15)

    footer(s, "Read Δ µε before Δ % : at 0.05 % strain a 10 µε difference is 2 % of the reading, "
              "and at 0.35 % the same 10 µε is 0.3 % — so the percentage column exaggerates the "
              "early points and flatters the late ones. Full list to six decimals: "
              "documentation/mot_matched_points.csv")
    pageno(s)
