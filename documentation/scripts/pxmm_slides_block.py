# ===================================================================================
#  Why 20.9 px/mm — the reasoning, and whether more would be better.
#
#  Appended to generate_v6a_slides.py. Every figure is arithmetic on the rig's own
#  ROI (read from camera_manager) and on the measured gauges, via pxmm_data.py.
# ===================================================================================
import pxmm_plots as _PXP                                             # noqa: E402

_PX = _PXP.all_figs()
_PO, _PM = _PX["ours"], _PX["mot"]


# ================================================================= 1. why that number
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "WHY 20.9 px/mm — NOT A SETTING, BUT WHAT THE FRAME LEAVES")

tb(s, 0.45, 1.12, 12.5, 0.46,
   "px/mm is not a number anyone typed in. It is fixed by the lens, the working distance and the "
   "sensor crop, and it is what the FIELD OF VIEW leaves behind. The field of view is the thing "
   "that was actually chosen, and this is the constraint that chose it.",
   fs=11, colour=BLACK)

img_fit(s, "documentation/figures/pxmm_tradeoff.png", 0.4, 1.62, 12.55, 2.92)

header(s, 0.45, 4.66, 4.05, "The binding constraint")
tb(s, 0.45, 5.04, 4.05, 1.62,
   "A fracture test is only useful if the markers stay in frame until the specimen breaks. On a "
   "%d px crop with a %d px box, a marker reaches the edge at %.0f %% strain. The rig's own travel "
   "backstop is %.1f %% on an 80 mm gauge, so the frame very nearly outlasts the machine — and the "
   "full %d px sensor takes it to %.0f %%, past the backstop."
   % (_PX["roi"][2], _PO["box_half"], 100 * _PO["strain_to_edge"],
      100 * _PX["travel_backstop_strain"], _PX["sensor_axis_px"],
      100 * _PO["strain_to_edge_full_sensor"]),
   fs=10, colour=BLACK)

header(s, 4.75, 4.66, 4.05, "How much margin that actually is")
table(s, 4.75, 5.04, 4.05, 1.62, [
    ["", "strain"],
    ["S25 fractured at", "%.2f %%" % (100 * _PX["ef_s25"])],
    ["S26 fractured at", "%.2f %%" % (100 * _PX["ef_s26"])],
    ["a marker leaves the frame at", "%.0f %%" % (100 * _PO["strain_to_edge"])],
    ["margin on PLA", "%.0f×" % (_PO["strain_to_edge"] / _PX["ef_s26"])],
], cw=[2.75, 1.3], hf=9.5, bf=8.5)

header(s, 9.05, 4.66, 3.9, "Where it is NOT enough")
tb(s, 9.05, 5.04, 3.9, 1.62,
   "TPU. An elastomer runs to hundreds of per cent, so the markers leave the frame long before "
   "anything stops the test and the trace simply ends mid-pull. That is a known limit of the "
   "shipped crop, recorded in camera_manager.set_roi, and the reason a wider ROI exists as an "
   "override rather than the ROI being treated as fixed.",
   fs=10, colour=BLACK)

footer(s, "Basler acA2440-35um, shipped ROI %s. The 80 mm gauge lands on %.0f px, so px/mm = "
          "%.2f — an OUTPUT of the optics, not an input."
          % (_PX["roi"], _PO["gauge_px"], _PO["ppm"]))
pageno(s)


# ================================================================= 2. would more be better?
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "WOULD MORE PIXELS PER mm BE BETTER? — THE XT-205 ANSWERS IT")

tb(s, 0.45, 1.12, 12.5, 0.40,
   "The XT-205 sits at the other end of the same trade: 33 % more pixels per millimetre, and a "
   "field of view that holds almost nothing but the gauge. It is the experiment we did not have "
   "to run ourselves.",
   fs=11, colour=BLACK)

header(s, 0.45, 1.66, 12.5, "What the extra magnification bought, and what it cost")
table(s, 0.45, 2.04, 12.5, 2.30, [
    ["", "PPD-UTM", "MOT XT-205", "What it means"],
    ["pixels per millimetre", "%.1f" % _PO["ppm"], "%.1f" % _PM["ppm"],
     "the XT-205 magnifies 33 % more"],
    ["one whole pixel, in strain", "%.0f µε" % _PO["per_px_ue"], "%.0f µε" % _PM["per_px_ue"],
     "so its quantisation floor is 25 % finer — a real gain"],
    ["field of view", "%.1f mm" % _PO["fov_mm"], "%.1f mm" % _PM["fov_mm"],
     "and it holds only %.1f mm beyond an 80 mm gauge"
     % (_PM["fov_mm"] - 80.0)],
    ["a marker leaves the frame at", "%.0f %% strain" % (100 * _PO["strain_to_edge"]),
     "%.2f %% strain" % (100 * _PM["strain_to_edge"]),
     "which is the whole cost, in one number"],
    ["what actually happened", "ran to fracture", "degraded at 0.52 %",
     "its box hit the frame edge; 184 rows pinned there (⟪WHAT HAD TO BE FIXED⟫)"],
], cw=[2.85, 2.15, 2.15, 5.35], hf=9.5, bf=8.5)

header(s, 0.45, 4.52, 6.15, "And the finer pixel did NOT set the precision")
table(s, 0.45, 4.90, 6.15, 1.35, [
    ["", "PPD-UTM", "XT-205 footage"],
    ["one whole pixel", "%.0f µε" % _PO["per_px_ue"], "%.0f µε" % _PM["per_px_ue"]],
    ["achieved by our pipeline", "%.1f µε" % _PO["noise_ue"], "%.1f µε" % _PM["noise_ue"]],
    ["sub-pixel factor", "%.0f×" % _PO["subpixel_factor"], "%.0f×" % _PM["subpixel_factor"]],
], cw=[2.6, 1.8, 1.75], hf=9.5, bf=8.5)

header(s, 6.85, 4.52, 6.1, "The honest answer")
tb(s, 6.85, 4.90, 6.1, 1.35,
   "More px/mm IS better — but only while the frame still outlasts the test. Both machines achieve "
   "%.0f–%.0f× better than one pixel, so the magnification sets the floor and the ESTIMATOR sets "
   "the result. Buying resolution with field of view is a bad trade for a fracture test, and a "
   "good one for a machine that only measures the elastic region."
   % (min(_PO["subpixel_factor"], _PM["subpixel_factor"]),
      max(_PO["subpixel_factor"], _PM["subpixel_factor"])),
   fs=10, colour=BLACK)

banner(s, 0.4, 6.42, 12.55, 0.52,
       "What we could NOT establish: no standard or literature basis for a px/mm target is "
       "recorded anywhere in this project. The choice is an engineering one — field of view "
       "against the machine's own travel limit — and it should be described that way rather than "
       "as a specification.",
       fill=YELLOW_WARN, fg=BLACK, fs=10)
footer(s, "The 0.52 % figure is where the XT-205 run's own tracking degraded, measured "
          "independently; the 0.70 % is where its box geometry says it must. They agree.")
pageno(s)


# ================================================================= 3. where the number comes from
_OPT = _PX["optics"]

s = prs.slides.add_slide(BLANK); ju(s)
title(s, "IS IT A CAMERA PROPERTY? — YES, AND A TAPE MEASURE CAN CHECK IT")

tb(s, 0.45, 1.12, 12.5, 0.46,
   "px/mm is the optical magnification divided by the pixel pitch — nothing else goes into it. "
   "Two constants of the hardware and one distance produce the number, and the last of those is "
   "the only thing anyone chose.",
   fs=11, colour=BLACK)

img_fit(s, "documentation/figures/pxmm_optics.png", 0.4, 1.58, 12.55, 2.70)

header(s, 0.45, 4.34, 6.25, "The chain, end to end")
table(s, 0.45, 4.72, 6.25, 1.64, [
    ["", "value", "where it comes from"],
    ["pixel pitch", "%.2f µm" % _OPT["pitch_um"], "acA2440 datasheet"],
    ["lens", "%.0f mm" % _OPT["f_mm"], "Azure-2514M f/1.4 — TODO.md, README.md"],
    ["measured px/mm", "%.2f" % _PO["ppm"], "%.0f px of gauge over %.0f mm, on S26"
     % (_PO["gauge_px"], 80.0)],
    ["so the magnification is", "%.4f×" % _OPT["ours"]["mag"], "pitch × px/mm — one pixel covers "
     "%.1f µm" % _OPT["ours"]["um_per_px"]],
    ["so the lens must stand", "%.0f mm away" % _OPT["ours"]["obj_mm"], "f(1 + 1/M) — a PREDICTION"],
], cw=[2.0, 1.15, 3.10], hf=9.5, bf=8.5)

header(s, 6.95, 4.34, 6.0, "What that buys us — and what changing it would cost")
tb(s, 6.95, 4.72, 6.0, 1.64,
   "Run a tape from the lens to the specimen. If it reads about %.0f mm, the chain on the left is "
   "the entire explanation for %.1f px/mm and nothing else is involved.  Move the camera %.0f mm "
   "closer and the same camera and the same lens give the XT-205's %.1f px/mm — no new hardware. "
   "It would also cut the field of view to %.0f mm and take the frame limit from %.0f %% strain "
   "to nothing. Placement matters at this scale: %.0f mm of error is worth 0.5 px/mm, which is "
   "why the scale is measured on the image and never assumed."
   % (_OPT["ours"]["obj_mm"], _PO["ppm"], _OPT["move_closer_mm"], _PM["ppm"], _PM["fov_mm"],
      100 * _PO["strain_to_edge"], _OPT["mm_per_half_ppm"]),
   fs=10, colour=BLACK)

banner(s, 0.4, 6.44, 12.55, 0.50,
       "Two caveats. The pixel pitch is a datasheet figure rather than one measured here, and the "
       "thin-lens relation ignores the real lens's principal-plane separation — so treat the "
       "%.0f mm as a prediction good to a few per cent, not a specification. Neither touches the "
       "measured %.2f px/mm, which is read off the gauge in the image."
       % (_OPT["ours"]["obj_mm"], _PO["ppm"]),
       fill=YELLOW_WARN, fg=BLACK, fs=10)
footer(s, "Sensitivity: near our operating point, one millimetre of camera movement is worth "
          "%.2f px/mm." % (0.5 / _OPT["mm_per_half_ppm"]))
pageno(s)
