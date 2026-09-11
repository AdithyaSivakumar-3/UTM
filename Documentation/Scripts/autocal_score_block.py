# ===================================================================================
#  AUTO-CALIBRATE — how a setting earns its score. One slide, from his question
#  (2026-09-06) in front of the real dialog: why does 25 ms at contrast 0.69 BEAT
#  100 ms at contrast 1.00?
#
#  Numbers mirror utm_autocal.py: weights 0.45/0.25/0.15/0.15, margin band 12→45
#  grey levels, clipping band 0→2 %, and the two rules the dialog cannot show —
#  the hard 2-marker gate and the widest-run tie-break. The worked example is his
#  own dialog's rows, quoted, not invented.
# ===================================================================================
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "AUTO-CALIBRATE — HOW A SETTING EARNS ITS SCORE")

# ---- the gate first: no partial credit
flow(s, 0.40, 1.15, 3.30, 0.80, "try each exposure ×\nthreshold on live frames",
     fill=WHITE, border=FLOW_NEUTRAL, fs=10, bold=True)
flow(s, 4.10, 1.15, 2.85, 0.80, "exactly 2 markers\nfound?", fill=YELLOW_WARN,
     border=RGBColor(0xD2, 0xA6, 0x1B), fs=10.5, bold=True)
flow(s, 7.35, 1.15, 2.30, 0.80, "NO → that frame\nscores 0", fill=RED_FAIL,
     border=RGBColor(0xC0, 0x39, 0x2B), fs=10, bold=True)
flow(s, 10.05, 1.15, 2.85, 0.80, "YES → four ingredients,\nweighted", fill=GREEN_PASS,
     border=DARK_GREEN, fs=10, bold=True)
arrow(s, 3.72, 1.55, 4.08, 1.55, colour=FLOW_NEUTRAL, width=1.6)
arrow(s, 6.97, 1.55, 7.33, 1.55, colour=FLOW_NEUTRAL, width=1.6)
arrow(s, 6.97, 1.55, 10.03, 1.55, colour=FLOW_NEUTRAL, width=1.6)

# ---- the four ingredients
_ING = [
    ("0.45", "CONTRAST MARGIN",
     "how far marker grey AND background grey sit from the cut — 12 levels scores 0, "
     "45 scores full. Predicts SURVIVING a lighting flicker; the thing Otsu ignores.",
     GREEN_PASS, DARK_GREEN),
    ("0.25", "HEADROOM",
     "share of pixels clipped at pure 0 or 255 — none scores full, 2 % scores zero. "
     "A saturated pixel has thrown its information away.",
     LIGHT_BLUE, RGBColor(0x2E, 0x6D, 0xA4)),
    ("0.15", "AREA FIT",
     "blob size sits comfortably mid-band, not scraping the min/max gates",
     WHITE, FLOW_NEUTRAL),
    ("0.15", "CIRCULARITY",
     "how round the blobs are above the 0.5 gate — roundness is what tells dots from grips",
     WHITE, FLOW_NEUTRAL),
]
for i, (wgt, name, txt, f, e) in enumerate(_ING):
    x = 0.40 + i * 3.18
    flow(s, x, 2.30, 2.95, 0.52, "%s  ·  %s" % (wgt, name), fill=f, border=e, fs=10.5,
         bold=True)
    tb(s, x + 0.05, 2.92, 2.90, 1.30, txt, fs=9.0, colour=BLACK)

# ---- the worked example: HIS dialog, quoted
header(s, 0.40, 4.30, 7.6, "Why 25 ms beat 100 ms — one real calibration, quoted")
table(s, 0.40, 4.68, 7.60, 1.42, [
    ["exposure", "detect", "contrast", "clipped", "score", ""],
    ["25 ms", "100 %", "0.69", "0.0 %", "0.71", "← best"],
    ["100 ms", "100 %", "1.00", "57.5 %", "0.61", "clipping zeroes headroom"],
    ["35 ms", "75 %", "0.75", "24.5 %", "0.34", "1 in 4 frames found ≠ 2 markers"],
], cw=[1.25, 1.0, 1.15, 1.1, 0.95, 2.15], hf=9.5, bf=9.2,
    ov={(1, 4): {"bg": GREEN_PASS, "bold": True}, (2, 3): {"bg": RED_FAIL, "bold": True},
        (3, 1): {"bg": RED_FAIL, "bold": True}})
tb(s, 0.40, 6.20, 7.6, 0.6,
   "Perfect contrast LOST: at 100 ms over half the picture is saturated, so headroom scores "
   "zero and 0.45 + 0 + the shape terms lands on 0.61. The winner trades a little contrast "
   "for a clean image.",
   fs=9.5, colour=BLACK)

header(s, 8.30, 4.30, 4.6, "Two rules the dialog can't show")
tb(s, 8.30, 4.68, 4.6, 2.1,
   "•  ONE FRAME IS NOT ENOUGH — every candidate is scored over several frames and averaged; "
   "a 75 % detect rate drags the mean down by itself.\n"
   "•  THE WIDEST RUN WINS — among thresholds that work, the sweep takes the CENTRE of the "
   "widest band of working values, not the lone peak: a setting with room on both sides "
   "survives a drift, a peak on a cliff does not. Otsu is scored once as a named candidate "
   "in the same sweep.",
   fs=9.4, colour=BLACK)

banner(s, 0.40, 6.95, 12.55, 0.38,
       "The score is not “does it track right now” — everything from 15 to 140 ms tracked. It is "
       "“which setting still tracks when the scene drifts”.",
       fill=GREEN_PASS, fg=DARK_GREEN, fs=11)
pageno(s)
