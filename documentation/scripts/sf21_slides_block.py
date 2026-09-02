# ===================================================================================
#  SF21 — noise capture. One slide: what it records, and the distinction that
#  decides what the numbers may be used for.
#
#  Appended to generate_v6a_slides.py.
# ===================================================================================

s = prs.slides.add_slide(BLANK); ju(s)
title(s, "SF21 · NOISE CAPTURE — MEASURING THE INSTRUMENT ALONE")

tb(s, 0.45, 1.12, 12.5, 0.46,
   "Every number this rig reports is specimen plus instrument. This records the instrument ALONE "
   "— preloaded, mounted, and completely still — so the two can be told apart. The button sits "
   "beside Prepare test and Fracture test, and it is the only one there that does not move the "
   "motor.",
   fs=11, colour=BLACK)

header(s, 0.45, 1.72, 12.5, "Three numbers per channel — and only two of them are subtractable")
table(s, 0.45, 2.10, 12.5, 1.64, [
    ["", "What it is", "Can it be removed from a later run?"],
    ["OFFSET", "the mean while at rest",
     "YES — it is a constant, so it subtracts exactly"],
    ["DRIFT", "the slope while at rest (N/s, µε/s)",
     "YES — it is systematic, so the fitted line subtracts"],
    ["RESIDUAL SD", "what is left once that line is removed",
     "NO. This is the measurement uncertainty — quote it, do not subtract it"],
], cw=[1.85, 4.30, 6.35], hf=9.5, bf=9)

header(s, 0.45, 3.94, 6.25, "Why the SD cannot be subtracted")
tb(s, 0.45, 4.32, 6.25, 2.00,
   "Because it is RANDOM, and two random records do not cancel. Subtracting one independent "
   "recording from another gives √2 times the variance, not zero — so a “noise-corrected” curve "
   "built that way would be noisier than the raw one, while looking cleaner on the slide.\n\n"
   "What the sd is FOR is the uncertainty band on a result, and the threshold below which a "
   "reported change is not a measurement. That is the honest use, and it is the one this feature "
   "supports.\n\n"
   "The straight line is removed BEFORE the sd is computed. A raw sd over a drifting window folds "
   "the drift in and reports a removable trend as irreducible noise.",
   fs=10, colour=BLACK)

header(s, 6.95, 3.94, 6.0, "Two things it insists on")
tb(s, 6.95, 4.32, 6.0, 2.00,
   "PRELOAD FIRST, judged from the live load rather than from history — a preload that relaxed, or "
   "one applied to a different specimen, should not count. Without it the operator gets the "
   "warning and an explicit “Measure anyway”, because a bare-machine baseline is a legitimate "
   "thing to want; the override is written into the file. It matters because unseated grips "
   "settle, and that settling is recorded as a drift that will not be there during the run.\n\n"
   "THE WINDOW TRAVELS WITH THE NUMBER. This rig's DIC noise floor GROWS with observation time — "
   "about 12 µε over 40 s against 26 µε over 900 s (⟪DIC NOISE — THE BLACK SPECIMEN⟫). A 30 s "
   "figure applied to a 900 s creep test understates the noise by roughly half, so the duration is "
   "chosen per capture and written into the header.",
   fs=10, colour=BLACK)

banner(s, 0.4, 6.44, 12.55, 0.50,
       "STATUS: BUILT AND VERIFIED OFFLINE — NOT YET RUN ON THE RIG. The statistics are checked "
       "against a synthetic signal with a known 0.25 N/s drift and 2.0 N sd, and recover 0.249 and "
       "2.015. What has not happened yet is a capture on the real machine, so no measured noise "
       "floor is claimed here.",
       fill=YELLOW_WARN, fg=BLACK, fs=10)
footer(s, "Saves every sample and the summary where the operator chooses. No DIC gives a "
          "load-only capture with the strain columns EMPTY, never zero.")
pageno(s)
