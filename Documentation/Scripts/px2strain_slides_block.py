# ===================================================================================
#  FROM PIXELS TO A STRAIN NUMBER — the whole conversion on two real frames.
#  Moved here from the final presentation's appendix (his call 2026-09-06): the final
#  deck now carries the reference calculation inline on its pixels click-slide, and the
#  full explainer lives in this diary where the pipeline story already runs
#  (threshold → blobs → centroids → THIS).
#
#  The figure's arithmetic is computed from the frames it shows by the same
#  (L − L₀)/L₀ rule the rig runs — utm_dic.dic_strain, one shared function for the
#  live pull and the post-processor (verified in code before the slide was written).
# ===================================================================================

s = prs.slides.add_slide(BLANK); ju(s)
title(s, "FROM PIXELS TO A STRAIN NUMBER — THE WHOLE CONVERSION")
img_fit(s, "documentation/figures/ppd_px2strain.png", 0.35, 1.10, 12.6, 3.55)

header(s, 0.40, 4.85, 6.05, "What the two frames show")
tb(s, 0.40, 5.21, 6.05, 1.45,
   "•  The camera never measures millimetres — it finds WHERE each marker is, to a fraction "
   "of a pixel, every frame.\n"
   "•  “Calibrate Px₀” freezes the reference separation L₀; from then on every frame is just "
   "ε = (L − L₀) / L₀.\n"
   "•  Pixels divided by pixels: the units cancel, so the strain needs no calibration and no "
   "gauge length.",
   fs=9.8, colour=BLACK)

header(s, 6.85, 4.85, 6.05, "Why this is trustworthy")
tb(s, 6.85, 5.21, 6.05, 1.45,
   "•  ONE shared function does this everywhere (utm_dic.dic_strain) — the live rig and the "
   "video post-processor cannot disagree about what strain means.\n"
   "•  px/mm exists only for millimetre quantities (extension, gauge) — the strain itself "
   "never touches it.\n"
   "•  The arithmetic on the figure is computed FROM the frames shown, by that same rule — "
   "nothing typed in.",
   fs=9.8, colour=BLACK)

banner(s, 0.4, 6.80, 12.55, 0.36,
       "STRAIN ON THIS RIG IS A COUNT DIVIDED BY A COUNT — (1736 − 1676) / 1676 = 3.62 % ON "
       "THESE TWO REAL FRAMES OF S26.",
       fill=GREEN_PASS, fg=DARK_GREEN, fs=10)
pageno(s)
