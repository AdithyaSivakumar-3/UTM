# ===================================================================================
#  HOW A MARKER IS ACTUALLY READ — the workflow, from the Start Camera button to a
#  strain number, drawn rather than described.
#
#  Three slides:
#    1. the per-frame loop, end to end
#    2. inside detect_blobs — the step that decides what a marker IS
#    3. where the grey levels come back — the one-way path and the closed loop
#
#  THE COLOUR CARRIES THE ARGUMENT. Every box is filled by which DOMAIN it works in:
#
#      amber  the pixel still has its grey value, 0-255
#      blue   the pixel is only 0 or 255; the grey level is gone
#      red    the threshold itself — the one step that converts one into the other
#
#  Read that way the slides answer the question they were asked for: the two halves
#  do not exchange information, they are separated by a lossy one-way step, and the
#  only place the grey levels come back is frame_score, which uses the BINARY as a
#  mask to re-read the ORIGINAL frame.
#
#  Native shapes, not a rendered image: this is a diagram he will want to edit, and
#  flow()/arrow() are the deck's existing vocabulary for one.
# ===================================================================================
_GREY_DOM = RGBColor(0xFD, 0xEF, 0xC8)      # pixels still carry a grey level
_GREY_EDGE = RGBColor(0xC8, 0x86, 0x0D)
_BIN_DOM = RGBColor(0xDB, 0xEA, 0xF7)       # pixels are 0 or 255 and nothing else
_BIN_EDGE = RGBColor(0x2E, 0x6D, 0xA4)
_CUT = RGBColor(0xFF, 0xCD, 0xD2)           # the threshold: the boundary between them
_CUT_EDGE = RGBColor(0xC0, 0x39, 0x2B)
_SETUP = RGBColor(0xEC, 0xEC, 0xEC)
_SETUP_EDGE = RGBColor(0x88, 0x88, 0x88)


def _legend(s, x, y):
    """The key, repeated on all three slides — the colour IS the point being made."""
    flow(s, x, y, 2.55, 0.30, "grey level still there (0–255)",
         fill=_GREY_DOM, border=_GREY_EDGE, fs=8.6)
    flow(s, x + 2.68, y, 2.05, 0.30, "the cut itself",
         fill=_CUT, border=_CUT_EDGE, fs=8.6)
    flow(s, x + 4.86, y, 2.55, 0.30, "0 or 255 only — grey gone",
         fill=_BIN_DOM, border=_BIN_EDGE, fs=8.6)


# =================================================================== 1. the whole loop
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "FROM “START CAMERA” TO A STRAIN NUMBER — THE WHOLE LOOP")

header(s, 0.40, 1.00, 12.55, "ONCE — when the button is pressed")
_su = [("Start Camera\npressed", 0.42, 2.32),
       ("set_specimen_mode(preset)\nROI · exposure · THRESHOLD · polarity", 3.02, 3.35),
       ("connect_camera()\napply ROI to the sensor", 6.65, 2.75),
       ("start_acquisition()\ngrab thread starts", 9.68, 2.85)]
for txt, x, w in _su:
    flow(s, x, 1.38, w, 0.62, txt, fill=_SETUP, border=_SETUP_EDGE, fs=9.2)
for x0, x1 in ((2.80, 3.00), (6.42, 6.63), (9.44, 9.66)):
    arrow(s, x0, 1.69, x1, 1.69, colour=FLOW_NEUTRAL, width=1.6)

tb(s, 0.42, 2.06, 12.55, 0.30,
   "The preset is applied BEFORE connecting — the specimen dropdown decides the ROI, the "
   "threshold value and the polarity, and every one of those is wrong to change later.",
   fs=9.4, italic=True, colour=GREY_TEXT)

header(s, 0.40, 2.48, 12.55, "THEN — every frame, ~35 times a second, on the grab thread")
_pf = [("RetrieveResult()\none frame from the camera", 0.42, 2.42, _GREY_DOM, _GREY_EDGE),
       ("rotate 90° CW\nsensor → rig orientation", 3.06, 2.16, _GREY_DOM, _GREY_EDGE),
       # this box SPANS the boundary — the threshold runs inside it — so filling it pure
       # binary would contradict the legend printed on the same slide
       ("detect_blobs(img)\nthe THRESHOLD lives in here → NEXT SLIDE", 5.44, 2.30,
        _CUT, _CUT_EDGE),
       ("calculate_dic_strain()\nonly if EXACTLY 2 found", 7.96, 2.42, _BIN_DOM, _BIN_EDGE),
       ("frame_ready.emit()\nfeed · overlay · badge", 10.60, 2.37, _BIN_DOM, _BIN_EDGE)]
for txt, x, w, f, e in _pf:
    flow(s, x, 2.86, w, 0.72, txt, fill=f, border=e, fs=9.2)
for x0, x1 in ((2.86, 3.04), (5.24, 5.42), (7.76, 7.94), (10.40, 10.58)):
    arrow(s, x0, 3.22, x1, 3.22, colour=FLOW_NEUTRAL, width=1.6)

# the recording branch — it hangs off the frame BEFORE detection and never blocks it
flow(s, 3.06, 3.92, 2.16, 0.52, "frame_sink(img)\nvideo capture, ~47 µs",
     fill=_GREY_DOM, border=_GREY_EDGE, fs=8.8)
arrow(s, 4.14, 3.58, 4.14, 3.90, colour=FLOW_NEUTRAL, width=1.4)
tb(s, 5.34, 3.90, 4.10, 0.55,
   "Recording branches off the RAW frame, before any threshold — so a recorded video can be "
   "re-measured later at a different setting.",
   fs=8.8, italic=True, colour=GREY_TEXT)

header(s, 0.40, 4.66, 6.20, "What the strain number actually is")
tb(s, 0.40, 5.04, 6.20, 1.65,
   "•  Two centroids, one separation: L_px = |y₂ − y₁|. Strain is (L_px − Px₀) / Px₀ — a pure "
   "PIXEL RATIO.\n"
   "•  No gauge length, no px/mm, no calibration constant enters it. They cancel.\n"
   "•  Px₀ is frozen once, by the Calibrate Px₀ button — the same detect_blobs runs, and its "
   "separation is stored as initial_distance.\n"
   "•  The identical conversion is shared with the offline post-processor (utm_dic.dic_strain), so "
   "a live pull and its own recording cannot disagree.",
   fs=9.4, colour=BLACK)

header(s, 6.75, 4.66, 6.20, "What happens when it is NOT exactly 2")
tb(s, 6.75, 5.04, 6.20, 1.65,
   "•  No strain row is written. A dropout is always preferable to a confident wrong number.\n"
   "•  The health badge says which — “DIC BAD 1/2” — and the near-miss reporter names the gate "
   "that rejected the blob, throttled to once every 3 s.\n"
   "•  If the loop itself falls below 12 Hz, load samples would start going out with no strain "
   "beside them, and that is reported too.",
   fs=9.4, colour=BLACK)

_legend(s, 0.42, 6.94)
pageno(s)


# ============================================================ 2. inside detect_blobs
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "INSIDE detect_blobs — HOW A MARKER IS IDENTIFIED")

_x, _w = 0.42, 3.05
_col2, _col3 = 4.62, 8.82
_y0, _h, _gap = 1.10, 0.66, 0.30

# ---- column 1: still in the grey domain, then the cut
_c1 = [("① the frame arrives\n2348 × 419, grey 0–255", _GREY_DOM, _GREY_EDGE),
       ("② mask_x — blank the columns\noutside the specimen (Black mode)", _GREY_DOM, _GREY_EDGE),
       ("③ cv2.threshold(frame, THRESHOLD,\n255, THRESHOLD_TYPE)", _CUT, _CUT_EDGE),
       ("④ binary image\nevery pixel now 0 or 255", _BIN_DOM, _BIN_EDGE)]
for i, (t_, f, e) in enumerate(_c1):
    y = _y0 + i * (_h + _gap)
    flow(s, _x, y, _w, _h, t_, fill=f, border=e, fs=9.0)
    if i < len(_c1) - 1:
        arrow(s, _x + _w / 2, y + _h, _x + _w / 2, y + _h + _gap, colour=FLOW_NEUTRAL, width=1.6)

banner(s, _x, _y0 + 4 * (_h + _gap) - 0.06, _w, 0.72,
       "THE GREY LEVELS END HERE. Nothing after step ③ ever reads the frame again — only the "
       "binary and the contours taken from it.",
       fill=_CUT, fg=BLACK, fs=9.0)

# ---- column 2: the binary domain — shapes, and the gates
_c2 = [("⑤ findContours(binary,\nRETR_EXTERNAL)", _BIN_DOM, _BIN_EDGE),
       ("⑥ per contour, measure\narea · perimeter → circularity\nmoments → centroid",
        _BIN_DOM, _BIN_EDGE),
       ("⑦ THE GATE\nMIN_AREA < area < MAX_AREA\nand circularity > MIN_CIRC",
        _BIN_DOM, _BIN_EDGE),
       ("⑧ sort the survivors by Y\ntop marker first", _BIN_DOM, _BIN_EDGE)]
for i, (t_, f, e) in enumerate(_c2):
    y = _y0 + i * (_h + _gap)
    flow(s, _col2, y, _w, _h, t_, fill=f, border=e, fs=8.8)
    if i < len(_c2) - 1:
        arrow(s, _col2 + _w / 2, y + _h, _col2 + _w / 2, y + _h + _gap,
              colour=FLOW_NEUTRAL, width=1.6)
arrow(s, _x + _w, _y0 + 3 * (_h + _gap) + _h / 2, _col2, _y0 + _h / 2,
      colour=FLOW_NEUTRAL, width=1.6)

flow(s, _col2, _y0 + 4 * (_h + _gap) - 0.06, _w, 0.72,
     "a REJECTED blob over 200 px is kept as a\nNEAR MISS and reported with the reason",
     fill=YELLOW_WARN, border=RGBColor(0xD2, 0xA6, 0x1B), fs=8.6)

# ---- column 3: from candidates to a trustworthy pair
_c3 = [("⑨ more than 2 survived?\nthe grips qualify too", RED_FAIL, _CUT_EDGE),
       ("⑩ _choose_marker_pair\nPx₀ known → the pair closest to it\nelse → the two nearest the "
        "centre-line", _BIN_DOM, _BIN_EDGE),
       ("⑪ plausibility check\nseparation ≥ 0.85 × Px₀\n(asymmetric — tension only pulls apart)",
        _BIN_DOM, _BIN_EDGE),
       ("⑫ two centroids\n→ calculate_dic_strain", GREEN_PASS, DARK_GREEN)]
for i, (t_, f, e) in enumerate(_c3):
    y = _y0 + i * (_h + _gap)
    flow(s, _col3, y, _w, _h, t_, fill=f, border=e, fs=8.6)
    if i < len(_c3) - 1:
        arrow(s, _col3 + _w / 2, y + _h, _col3 + _w / 2, y + _h + _gap,
              colour=FLOW_NEUTRAL, width=1.6)
arrow(s, _col2 + _w, _y0 + 3 * (_h + _gap) + _h / 2, _col3, _y0 + _h / 2,
      colour=FLOW_NEUTRAL, width=1.6)

tb(s, _col3, _y0 + 4 * (_h + _gap) - 0.06, _w, 0.80,
   "Step ⑪ exists because one S13 frame passed with the markers 112 px apart against a 1668 px "
   "Px₀ — post-fracture, one marker gone.",
   fs=8.6, italic=True, colour=GREY_TEXT)

banner(s, 0.42, 5.62, 12.55, 0.52,
       "THE ANSWER TO “WHAT METHOD IDENTIFIES A MARKER”: not the threshold, and not Otsu. "
       "Steps ⑦ and ⑩ do it — AREA, CIRCULARITY, and separation against Px₀. The threshold only "
       "decides which pixels are candidates.",
       fill=GREEN_PASS, fg=DARK_GREEN, fs=10.5)

tb(s, 0.42, 6.24, 12.55, 0.62,
   "This is why the grips are not a problem even though they pass the cut: they are the wrong "
   "SHAPE (aspect 2.45–4.24 against the dots' 0.95–1.04), the wrong SIZE, and no pairing of them "
   "sits near Px₀. Brightness alone never separates them — geometry does.",
   fs=9.4, colour=BLACK)

_legend(s, 0.42, 6.94)
pageno(s)


# ================================================ 3. the two loops, and where grey returns
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "WHERE THE GREY LEVELS COME BACK — TWO PATHS, NOT ONE")

header(s, 0.40, 1.00, 12.55, "PATH 1 — measurement. One way, and lossy.")
_p1 = [("the raw frame\ngrey 0–255", 0.42, 2.05, _GREY_DOM, _GREY_EDGE),
       ("THRESHOLD", 2.72, 1.55, _CUT, _CUT_EDGE),
       ("binary\n0 or 255", 4.52, 1.65, _BIN_DOM, _BIN_EDGE),
       ("shapes + gates\narea · circularity", 6.42, 2.35, _BIN_DOM, _BIN_EDGE),
       ("two centroids", 9.02, 1.85, _BIN_DOM, _BIN_EDGE),
       ("strain", 11.12, 1.30, GREEN_PASS, DARK_GREEN)]
for t_, x, w, f, e in _p1:
    flow(s, x, 1.38, w, 0.60, t_, fill=f, border=e, fs=9.0)
for a, b in ((2.47, 2.70), (4.27, 4.50), (6.17, 6.40), (8.77, 9.00), (10.87, 11.10)):
    arrow(s, a, 1.68, b, 1.68, colour=FLOW_NEUTRAL, width=1.6)
tb(s, 0.42, 2.04, 12.55, 0.30,
   "Nothing flows right-to-left. Once the threshold has run, the grey level of a pixel is gone and "
   "no later step can recover it.",
   fs=9.4, italic=True, colour=GREY_TEXT)

header(s, 0.40, 2.46, 12.55, "PATH 2 — calibration and monitoring. Here the loop CLOSES.")
flow(s, 0.42, 2.84, 2.05, 0.66, "the raw frame\ngrey 0–255", fill=_GREY_DOM, border=_GREY_EDGE,
     fs=9.0)
flow(s, 2.92, 2.84, 1.55, 0.66, "THRESHOLD", fill=_CUT, border=_CUT_EDGE, fs=9.0)
flow(s, 4.92, 2.84, 1.65, 0.66, "binary\n0 or 255", fill=_BIN_DOM, border=_BIN_EDGE, fs=9.0)
flow(s, 7.02, 2.84, 2.35, 0.66, "frame_score()\nutm_autocal.py", fill=WHITE,
     border=RGBColor(0x1E, 0x84, 0x49), fs=9.4, bold=True)
arrow(s, 2.47, 3.17, 2.90, 3.17, colour=FLOW_NEUTRAL, width=1.6)
arrow(s, 4.47, 3.17, 4.90, 3.17, colour=FLOW_NEUTRAL, width=1.6)
arrow(s, 6.57, 3.17, 7.00, 3.17, colour=FLOW_NEUTRAL, width=1.6)
# the return leg: the binary goes back to the ORIGINAL frame as a mask
arrow(s, 8.19, 3.50, 8.19, 3.86, colour=RGBColor(0x1E, 0x84, 0x49), width=2.2)
flow(s, 4.92, 3.86, 4.45, 0.62,
     "cv2.mean(FRAME, mask=BINARY)  ·  cv2.mean(FRAME, mask=NOT binary)",
     fill=_GREY_DOM, border=RGBColor(0x1E, 0x84, 0x49), fs=8.8, bold=True)
# land the return leg ON the raw-frame box, not in the space beside it — the whole point of
# the panel is that the loop visibly closes
arrow(s, 4.90, 4.17, 1.55, 3.55, colour=RGBColor(0x1E, 0x84, 0x49), width=2.2)
tb(s, 0.42, 4.42, 4.35, 0.50,
   "…and reads the ORIGINAL frame again. THAT is where the two halves meet.",
   fs=8.8, italic=True, colour=RGBColor(0x1E, 0x84, 0x49))

tb(s, 9.55, 2.84, 3.42, 0.70,
   "The binary says WHICH pixels. The frame says WHAT VALUE. Neither could compute the margin "
   "alone — that is the intersection.",
   fs=8.8, italic=True, colour=GREY_TEXT)

header(s, 0.40, 4.66, 6.20, "What frame_score weighs — 70 % grey, 30 % shape")
table(s, 0.40, 5.04, 6.20, 1.39, [
    ["Term", "Weight", "Comes from"],
    ["contrast margin", "0.45", "GREY — how far the markers sit from the cut"],
    ["headroom (clipping)", "0.25", "GREY — share of pixels at 0 or 255"],
    ["area fit + circularity", "0.30", "BINARY — the shapes that survived"],
], cw=[1.85, 0.90, 3.45], hf=9.2, bf=9.0,
    ov={(1, 2): {"bg": _GREY_DOM}, (2, 2): {"bg": _GREY_DOM}, (3, 2): {"bg": _BIN_DOM}})

header(s, 6.75, 4.66, 6.20, "Where that closed loop runs, and why it matters")
tb(s, 6.75, 5.04, 6.20, 1.85,
   "•  AUTO-CALIBRATE sweeps thresholds and scores each by what the blob stage made of it — so "
   "here the binary result CHOOSES the threshold. Full feedback.\n"
   "•  THE LIVE BADGE runs the same function on the current setting, throttled. It is what turns "
   "“DIC OK” into “DIC FRAGILE”: still tracking, but only N grey levels from the cut.\n"
   "•  Path 1 cannot warn you it is about to fail — it threw away the evidence. Path 2 is the "
   "thing that goes back and looks.\n"
   "•  And it is the correction to Otsu: Otsu scores a cut on the HISTOGRAM, which is blind to the "
   "markers. frame_score scores it on where the markers actually landed.",
   fs=9.4, colour=BLACK)

_legend(s, 0.42, 6.94)
pageno(s)
