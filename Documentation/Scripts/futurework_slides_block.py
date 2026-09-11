# ===================================================================================
#  FUTURE WORK — THE ROAD AHEAD. Mirrors the PPD final deck's "Future work" slide as
#  pinned on 2026-09-06 (his order, his trimmed titles, the new fracture-behaviour
#  item, and the worth-a-thesis line). One diary slide, appended at the end of the
#  Weekly like every other dated block. ROADMAP §6 carries the same slate (FW1/FW2/FW3).
# ===================================================================================

s = prs.slides.add_slide(BLANK); ju(s)
title(s, "FUTURE WORK — THE ROAD AHEAD (SEPT 2026)")
tb(s, 0.40, 1.02, 12.55, 0.40,
   "The slate as pinned in the PPD final presentation on 6 Sept 2026 — six named extensions, "
   "in order. Each is blocked by something known and quantified; none is a finishing touch.",
   fs=11, italic=True, colour=GREY_TEXT)

_fw6 = [
    ("1 · POISSON & TRUE STRESS",
     "Four markers → lateral strain, ν, Cauchy stress. The offline maths is BUILT and "
     "self-tested (post-processor extras pairs).\nHOW — blocked on optics: a gauge-zoomed "
     "second camera or a wider specimen; the day such a video exists, it is one click."),
    ("2 · 2D-DIC STRAIN FIELD",
     "Full-field strain over a speckled gauge, not just two dots.\nHOW — offline first, in "
     "the existing post-processor; needs lower exposure — the white specimen body currently "
     "saturates the sensor."),
    ("3 · FEED SIMULATION MODELS",
     "Measured strain fields calibrating FE material cards.\nHOW — export the field per "
     "frame; compare predicted vs measured maps on the same geometry."),
    ("4 · STUDYING FRACTURE BEHAVIOUR",
     "Full-field strain maps around the crack tip; crack propagation speed and direction.\n"
     "HOW — film the necking zone at higher magnification and run the 2D-DIC field around "
     "the growing crack; builds directly on item 2."),
    ("5 · CORRELATION, NOT BINARY",
     "Sub-pixel tracking that keeps the grey levels instead of thresholding them away.\n"
     "HOW — measured gain 1.1–2.1× less jitter; add as a post-processing option before "
     "touching the live loop."),
    ("6 · DESIGN BETTER GRIPS",
     "Printed jaws that seat deterministically — no low-strain slack, no 21 % / 33 % "
     "lottery.\nHOW — size the slack (re-mount one specimen, elastic pulls only), redesign, "
     "reprint, re-run; success: one cluster, shorter toe."),
]
for _i, (_h, _b) in enumerate(_fw6):
    _r, _c = divmod(_i, 2)
    _x, _y = 0.40 + _c * 6.55, 1.58 + _r * 1.70
    header(s, _x, _y, 6.05, _h)
    tb(s, _x, _y + 0.36, 6.05, 1.28, _b, fs=9.3, colour=BLACK)

banner(s, 0.4, 6.78, 12.55, 0.36,
       "THE 2D-DIC FIELD, FRACTURE BEHAVIOUR AND THE SIMULATION COUPLING ARE EACH WORTH A "
       "THESIS OF THEIR OWN.",
       fill=GREEN_PASS, fg=DARK_GREEN, fs=10)
pageno(s)
