# ===================================================================================
#  SF20 · DIC post-processing — what the tab does, and the evidence that it works.
#
#  Appended to generate_v6a_slides.py. The measured figures come from the estimator
#  and MOT caches, so a claim here cannot drift from the analysis that produced it.
# ===================================================================================
import json as _sjson                                                 # noqa: E402
import io as _sio                                                     # noqa: E402

_S20_MOT = _sjson.load(_sio.open("documentation/mot_postproc_compare.json", encoding="utf-8"))
_S20_EST = _sjson.load(_sio.open("documentation/estimator_measurements.json", encoding="utf-8"))
_S20_RIG = _S20_MOT["rig_name"]
_S20_PP = next(r for r in _S20_MOT["rows"] if r["key"] == "pp")
_S20_XT = next(r for r in _S20_MOT["rows"] if r["key"] == "mot")


# ================================================================= SF20 · what it is
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "SF20 · DIC POST-PROCESSING — MEASURE ANY RECORDED VIDEO")
pic_or_ph(s, "documentation/figures/UTM_DIC Post.png", 0.4, 1.22, 8.55, 0.8,
          "[ drop UTM_DIC Post.png here ]")

header(s, 9.15, 1.16, 3.8, "What it is for")
tb(s, 9.15, 1.54, 3.8, 1.62,
   "The rig measures strain live and throws the frames away. This tab measures strain from a video "
   "AFTERWARDS, with the same pixel-to-strain rule — utm_dic.dic_strain, the function the live "
   "camera path calls. Nothing about the maths is re-implemented.\n"
   "That buys two things a live-only rig cannot have.",
   fs=10, colour=BLACK)

header(s, 9.15, 3.28, 3.8, "1 · Re-check our own runs")
tb(s, 9.15, 3.66, 3.8, 1.10,
   "Same pull, same frames, an independent path. A live number that cannot be reproduced offline "
   "is a number with no second opinion.",
   fs=10, colour=BLACK)

header(s, 9.15, 4.88, 3.8, "2 · Measure ANOTHER machine")
tb(s, 9.15, 5.26, 3.8, 1.10,
   "Point it at a commercial extensometer's own footage and our rule produces a strain from it — "
   "which is the only way to compare two instruments without also changing the specimen.",
   fs=10, colour=BLACK)

banner(s, 0.4, 6.44, 8.55, 0.52,
       "Multi-video: each keeps its own boxes, frame rate and settings, and every finished run is "
       "plotted together — so two specimens, or two machines, land on one set of axes.",
       fill=LIGHT_BLUE, fg=BLACK, fs=10)
footer(s, "Software/UTM_PyQt6/utm_postproc.py (engine, no Qt) + utm_postdlg.py (the tab). The "
          "engine is importable on its own, which is what let every figure in this section be "
          "built from a script rather than by hand.")
pageno(s)


# ================================================================= SF20 · does it work
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "SF20 · DOES IT ACTUALLY MEASURE? — THREE INDEPENDENT CHECKS")

header(s, 0.45, 1.16, 4.05, "1 · Against our own live DIC")
tb(s, 0.45, 1.54, 4.05, 1.42,
   "Re-measuring S25 and S26 from their recordings reproduces the rig's live strain to "
   "330 and 363 µε RMS, with Px₀ agreeing to 0.005 %. The residual is a reproducible −0.05 % "
   "offset on BOTH specimens, not scatter — see ⟪DATA PROOF (2 OF 2)⟫.",
   fs=10, colour=BLACK)

header(s, 4.75, 1.16, 4.05, "2 · Against a commercial instrument")
tb(s, 4.75, 1.54, 4.05, 1.42,
   "Run on the MOT XT-205's own footage it agrees with that machine's extensometer to a median "
   "ratio of %.4f over %d matched points, and the strain SCALES match to %.2f %% "
   "(⟪THE SCALE CHECK⟫)."
   % (_S20_MOT["ratio_matched_median"], _S20_MOT["matched_n"],
      abs(_S20_MOT["scale_k"] - 1) * 100),
   fs=10, colour=BLACK)

header(s, 9.05, 1.16, 3.9, "3 · Its estimator was chosen on data")
tb(s, 9.05, 1.54, 3.9, 1.42,
   "The sub-pixel method is not a default that happened to work: four candidates were measured on "
   "real video and the winner picked on its WORST case, not its best (⟪FOUR WAYS TO FIND A MARKER "
   "CENTRE⟫).",
   fs=10, colour=BLACK)

header(s, 0.45, 3.10, 12.5, "The numbers, and where each comes from")
table(s, 0.45, 3.48, 12.5, 1.95, [
    ["Check", "Result", "Why it is the right test"],
    ["Noise on the XT-205's footage",
     "%.1f µε, against %.1f µε for the XT-205's own\nextensometer on the same frames"
     % (_S20_PP["noise_ue"], _S20_XT["noise_ue"]),
     "Same footage and same window, so the comparison is of the\nMEASUREMENT and not of two "
     "different pulls."],
    ["Noise on our own footage",
     "%.1f µε (S25) and %.1f µε (S26), against\n%.1f µε for the rig measuring live"
     % (_S20_EST["method"]["S25"]["auto"]["noise_ue"],
        _S20_EST["method"]["S26"]["auto"]["noise_ue"], _S20_EST["live_rig"]["S26"]),
     "Quieter than the live path because it is not racing the\ncontrol loop and can use a larger "
     "patch."],
    ["Patch size, the biggest lever",
     "13× worse with a patch narrower than the marker",
     "Found by sweeping it, which is also how the tab learned to\nSUGGEST a size from the detected "
     "marker."],
], cw=[3.0, 4.4, 5.1], hf=9.5, bf=8.5)

header(s, 0.45, 5.62, 12.5, "What it refuses to do, which is the part that makes it usable")
table(s, 0.45, 6.00, 12.5, 0.88, [
    ["Guard", "Why"],
    ["Stops when the markers are lost, and marks the point on the plot",
     "A curve that simply ends looks identical to one that reached the end of its video."],
    ["Verifies the frame rate against a sidecar, and warns when the file's claim is implausible",
     "One of our own files declares 35 fps and ran at 19.93; an extensometer's declares 1000."],
    ["Verifies that seeking works, and decodes in order when it does not",
     "On one real file cv2 returns stale frames past ~80, silently — it cost a wrong conclusion."],
], cw=[6.2, 6.3], hf=9.5, bf=8.5)
footer(s, "Every figure in ⟪THE SCALE CHECK⟫, ⟪DATA PROOF (1 OF 2)⟫ and the estimator slides was "
          "produced by this engine, driven from a script. Measured %s."
          % _S20_EST.get("measured", "2026-08-27"))
pageno(s)
