# ===================================================================================
#  CAMERA RESOLUTION — sensor, ROI, what the crop changes, and the exposure/fps law.
#  His ask (2026-09-05): where is resolution set, what does it affect, and one slide
#  on why exposure — not resolution — sets the frame rate.
#
#  Every number is read from code or a capture: sensor 2448×2048 and the rounding
#  rules from docs/RECALIBRATE_ROI.md; ROI [0, 988, 2348, 419], the 90° rotation and
#  the 33 %/39 % travel limits from camera_manager.py; the ×0.3–×2.8 sweep from
#  main.AUTOCAL_EXPOSURE_STEPS; 19.9 fps as measured on S24–S26.
# ===================================================================================

# ---------------------------------------------------- 1. sensor -> ROI -> rotation
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "WHAT THE CAMERA SEES — SENSOR, ROI AND THE ROTATION")
img_fit(s, "documentation/figures/cam_pipeline.png", 0.35, 1.06, 12.6, 3.95)

header(s, 0.40, 5.15, 4.05, "Resolution is fixed")
tb(s, 0.40, 5.53, 4.05, 1.55,
   "•  The Basler sensor is 2448 × 2048 px and always runs at full resolution — no binning, "
   "no scaling, anywhere in the pipeline.\n"
   "•  What we choose is WHICH pixels to read: a Region Of Interest (ROI), set in "
   "camera_manager.py and applied on connect.",
   fs=9.6, colour=BLACK)

header(s, 4.65, 5.15, 4.05, "The ROI we chose, and why")
tb(s, 4.65, 5.53, 4.05, 1.55,
   "•  [OffsetX 0, OffsetY 988, Width 2348, Height 419] — a band 2348 px long and 419 px "
   "across, framed with roi_tool.py so both markers sit inside with room to move.\n"
   "•  One ROI for every specimen colour: where the specimen sits is a property of the RIG, "
   "so White and Black share it.",
   fs=9.6, colour=BLACK)

header(s, 8.90, 5.15, 4.05, "Then rotate, never resize")
tb(s, 8.90, 5.53, 4.05, 1.55,
   "•  Every frame is rotated 90° so rows run along the pull — that is why recordings are "
   "420 × 2348.\n"
   "•  Rotation reorders pixels; it invents none. A pixel is the same 48 µm on the sensor, "
   "on screen and in the saved video.",
   fs=9.6, colour=BLACK)
footer(s, "The camera has no “resolution setting” in the app — the sensor always delivers full "
          "resolution and the ROI decides the field of view. Recalibration workflow: "
          "docs/RECALIBRATE_ROI.md.")
pageno(s)

# ---------------------------------------------------- 2. the travel budget
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "WHY 2348 OF 2448 px — THE TRAVEL BUDGET")
img_fit(s, "documentation/figures/cam_travel.png", 0.35, 1.10, 12.6, 3.95)

header(s, 0.40, 5.20, 6.05, "The pixels are room to stretch")
tb(s, 0.40, 5.58, 6.05, 1.50,
   "•  The pair starts ≈ 1665 px apart and only ONE marker really walks — the crosshead end; "
   "the other creeps about a quarter as much.\n"
   "•  At 2348 px a marker reaches the frame edge at ≈ 33 % strain — BEFORE the 30 mm travel "
   "backstop (37.5 % on an 80 mm gauge). At the full 2448 px it is ≈ 39 % — after it.\n"
   "•  PLA and PETG break long before either limit; an elastomer does not.",
   fs=9.6, colour=BLACK)

header(s, 6.75, 5.20, 6.05, "How the rig handles it")
tb(s, 6.75, 5.58, 6.05, 1.50,
   "•  TPU recipes override the ROI to the full sensor width — that is what a per-specimen "
   "ROI in the test profile is FOR.\n"
   "•  The guided wizard's “marker travel room” step reads the live frame and says which "
   "end has the room, before the pull.\n"
   "•  S35/S36 are the lesson: their markers walked out of the picture and the strain trace "
   "simply ended — pixels, not physics, ended those measurements.",
   fs=9.6, colour=BLACK)
pageno(s)

# ---------------------------------------------------- 3. what the ROI does and does not change
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "WHAT THE ROI CHANGES — AND WHAT IT CANNOT")

header(s, 0.40, 1.15, 6.05, "Changes exactly one thing")
tb(s, 0.40, 1.53, 6.05, 1.90,
   "•  THE FIELD OF VIEW — which patch of the scene the camera reads, and with it the travel "
   "budget on the previous slide.\n"
   "•  That is the whole list. A tighter crop shows less scene, not worse pictures.",
   fs=10.0, colour=BLACK)

header(s, 6.75, 1.15, 6.05, "Cannot change")
tb(s, 6.75, 1.53, 6.05, 1.90,
   "•  SHARPNESS — no pixels are resampled; cropping keeps every pixel it keeps, unchanged.\n"
   "•  THE SCALE — px/mm is set by the lens and the working distance (20.85 px/mm ⇒ 48 µm "
   "per pixel). The crop moves the WINDOW, not the optics: calibration survives any ROI "
   "change, and dies the moment the camera or lens moves.\n"
   "•  STRAIN RESOLUTION per pixel — on a 1665 px pair one whole pixel is ≈ 600 µε; the "
   "sub-pixel centroid resolves far finer. More pixels across the GAUGE would help; more "
   "pixels of background would not.",
   fs=10.0, colour=BLACK)

header(s, 0.40, 3.75, 12.4, "Two footnotes that keep the numbers honest")
tb(s, 0.40, 4.13, 12.4, 1.75,
   "•  The blob gates live in pixels: min_area 2000 px², marker radius ≈ 60 px, search window "
   "40 px. They are tuned to THIS optical scale — change the lens or distance and they need "
   "re-tuning along with px/mm (Auto-calibrate covers threshold and exposure).\n"
   "•  Frame rate: a smaller ROI CAN raise a sensor's fps ceiling (fewer rows to read out), "
   "but on this rig it never gets the chance — the exposure time binds first. Next slide.",
   fs=10.0, colour=BLACK)

banner(s, 0.40, 6.15, 12.55, 0.50,
       "RESOLUTION HERE = WHICH PIXELS WE READ, NOT HOW GOOD THEY ARE. THE ROI BUYS TRAVEL "
       "ROOM; SHARPNESS, SCALE AND NOISE BELONG TO THE OPTICS AND THE EXPOSURE.",
       fill=LIGHT_BLUE, fg=BLACK, fs=11)
pageno(s)

# ---------------------------------------------------- 4. exposure sets the frame rate
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "EXPOSURE SETS THE FRAME RATE — NOT THE RESOLUTION")
img_fit(s, "documentation/figures/cam_exposure.png", 0.35, 1.10, 12.6, 3.85)

header(s, 0.40, 5.10, 6.05, "Why 19.9 and not 35")
# the WHY bullet mirrors the final deck's appendix A4 (added there 2026-09-07, brought
# across on his "make sure the resolution info is conveyed here" check)
tb(s, 0.40, 5.44, 6.05, 1.82,
   "•  Each frame must be EXPOSED before it can be delivered: at 50 ms per frame the ceiling "
   "is 1 / 0.050 s = 20 fps, whatever rate is requested.\n"
   "•  WHY the request is a CEILING, not a promise: the sensor cannot begin sending a frame "
   "until it has finished gathering light for it, so the true rate is min(requested, "
   "1 / exposure) — and readout overhead shaves that 20 down to 19.9.\n"
   "•  The app asks for 35 fps and the camera would honour it — below 28.6 ms of exposure. "
   "At 50 ms it delivers 19.9 fps, and that MEASURED rate (not the requested one) is what "
   "timestamps every capture.",
   fs=9.6, colour=BLACK)

header(s, 6.75, 5.10, 6.05, "Where auto-calibrate comes in")
tb(s, 6.75, 5.48, 6.05, 1.55,
   "•  Exposure is a trade: more light per frame = stronger marker contrast, but fewer "
   "frames per second.\n"
   "•  Auto-calibrate sweeps ×0.3 … ×2.8 of the current exposure (15–140 ms here), scores "
   "each on measured trackability — contrast margin dominates — and PROPOSES the winner; "
   "Cancel restores the camera exactly.\n"
   "•  A winner at the sweep's edge is reported as “run it again”, never presented as the "
   "answer.",
   fs=9.6, colour=BLACK)
footer(s, "How the score itself is built: ⟪AUTO-CALIBRATE — HOW A SETTING EARNS ITS SCORE⟫. "
          "The 19.9 fps is measured per capture from frames/index.csv timestamps — the "
          "container's declared 35 fps is never believed.")
pageno(s)
