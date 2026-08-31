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
    ["marker span Px₀", "2234 px", "1676 px"],
    ["scale", "27.9 px/mm", "21.0 px/mm"],
    ["specimen width", "9.60 mm", "10.12 mm"],
    ["frame rate", "19.405 fps (from its DAQ)", "19.93 fps (from index.csv)"],
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
    ["independent scale check (see below)", "k = %.5f" % _M["scale_k"]],
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
       "The scale check is the load-bearing one. Recovering the frame rate by matching strain "
       "levels returns fps ÷ k for any scale error k — so comparing it against the rate the DAQ "
       "actually recorded measures k directly. k = %.5f, so the two pipelines put the same number "
       "on the same pixels." % _M["scale_k"],
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
     "Replaced by the DAQ's own timestamps; the honest\nfigure is %.1f %%. The matching fit is "
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
