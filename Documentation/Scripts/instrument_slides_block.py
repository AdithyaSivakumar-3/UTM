# ===================================================================================
#  HOW STRAIN IS MEASURED — the instrument family, drawn rather than described.
#
#  Four slides born from his own question chain (2026-09-05): is a strain gauge
#  clipped on? can an extensometer be a camera? what is the PRINCIPLE of a clip-on?
#  The answers kept needing diagrams, so they became slides: flowcharts and one
#  schematic, one or two lines of text per idea, per his ask.
#
#  Colour code across all four: orange = touches the specimen, blue = the sensing
#  chain, green = what comes out.
# ===================================================================================
import instrument_figs as _IF                                         # noqa: E402
_IF.fig_clipon()

_ORANGE = RGBColor(0xE8, 0x59, 0x0C)
_ORANGE_BG = RGBColor(0xFD, 0xE8, 0xDC)


# ============================================== 1. the three instruments, one lane each
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "THREE WAYS TO MEASURE STRAIN — GLUED, CLIPPED, WATCHED")

_LANES = [
    ("STRAIN GAUGE\nglued on", _ORANGE_BG, _ORANGE, [
        ("foil zigzag GLUED\nto the surface", _ORANGE_BG, _ORANGE),
        ("surface stretches\n→ foil stretches", WHITE, FLOW_NEUTRAL),
        ("its resistance\nrises a little", LIGHT_BLUE, RGBColor(0x2E, 0x6D, 0xA4)),
        ("strain at ONE SPOT\n~1 µε resolution", GREEN_PASS, DARK_GREEN)],
     "single-use — dies with the specimen · gives up near 5 % strain · it is what LOAD CELLS "
     "are built from, including ours"),
    ("CLIP-ON\nEXTENSOMETER", _ORANGE_BG, _ORANGE, [
        ("two knife edges\nclip on, L₀ apart", _ORANGE_BG, _ORANGE),
        ("points move apart\n→ arms splay", WHITE, FLOW_NEUTRAL),
        ("a spring bends;\ngauges read IT", LIGHT_BLUE, RGBColor(0x2E, 0x6D, 0xA4)),
        ("strain over a\nGAUGE LENGTH", GREEN_PASS, DARK_GREEN)],
     "reusable, certification-grade · can slip or nick the part · taken OFF before fracture — "
     "the curve loses its tail"),
    ("VIDEO\nEXTENSOMETER", LIGHT_BLUE, RGBColor(0x2E, 0x6D, 0xA4), [
        ("a camera watches\ntwo marks", LIGHT_BLUE, RGBColor(0x2E, 0x6D, 0xA4)),
        ("pixels track the\ntwo centres", WHITE, FLOW_NEUTRAL),
        ("ΔL in pixels —\nnothing touches", LIGHT_BLUE, RGBColor(0x2E, 0x6D, 0xA4)),
        ("strain to FRACTURE\nXT-205 · PPD-UTM", GREEN_PASS, DARK_GREEN)],
     "no contact, no slip, nothing to rescue at fracture · works on TPU that stretches past "
     "any clip's travel"),
]
for li, (name, nf, ne, steps, note) in enumerate(_LANES):
    y = 1.30 + li * 1.86
    flow(s, 0.40, y, 1.80, 0.80, name, fill=nf, border=ne, fs=10.5, bold=True, fg=BLACK)
    for i, (txt, f, e) in enumerate(steps):
        x = 2.55 + i * 2.68
        flow(s, x, y, 2.38, 0.80, txt, fill=f, border=e, fs=9.5)
        arrow(s, (2.30 if i == 0 else x - 0.30), y + 0.40, x - 0.02, y + 0.40,
              colour=FLOW_NEUTRAL, width=1.5)
    tb(s, 2.55, y + 0.88, 10.4, 0.34, note, fs=9.0, italic=True, colour=GREY_TEXT)

banner(s, 0.40, 6.95, 12.55, 0.38,
       "glued = strain gauge · clipped = extensometer · camera = video extensometer — "
       "all three end at the same number, strain.",
       fill=GREEN_PASS, fg=DARK_GREEN, fs=11.5)
pageno(s)


# ===================================== 2. inside the clip-on: a gauge measuring a spring
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "INSIDE A CLIP-ON — A STRAIN GAUGE MEASURING A SPRING")

img_fit(s, "documentation/figures/ext_clipon.png", 0.40, 1.15, 6.10, 5.10)

_CHAIN = [
    ("knife edges define L₀ on the specimen", _ORANGE_BG, _ORANGE),
    ("specimen stretches — the two points part by ΔL", WHITE, FLOW_NEUTRAL),
    ("arms carry ΔL to a FLEXURE, far softer than the part", WHITE, FLOW_NEUTRAL),
    ("the flexure bends — ΔL becomes bending", LIGHT_BLUE, RGBColor(0x2E, 0x6D, 0xA4)),
    ("4 foil gauges on the flexure → bridge voltage ∝ ΔL", LIGHT_BLUE,
     RGBColor(0x2E, 0x6D, 0xA4)),
    ("strain = ΔL / L₀ — certified class (ASTM E83 / ISO 9513)", GREEN_PASS, DARK_GREEN),
]
for i, (txt, f, e) in enumerate(_CHAIN):
    y = 1.30 + i * 0.86
    flow(s, 6.90, y, 6.00, 0.62, txt, fill=f, border=e, fs=10.5)
    if i:
        arrow(s, 9.90, y - 0.24, 9.90, y - 0.02, colour=FLOW_NEUTRAL, width=1.6)

tb(s, 0.55, 6.32, 6.0, 0.60,
   "The spring costs the test a few grams — it rides along without pulling back. And the "
   "strain gauge is glued to the SPRING, never to your part.",
   fs=10, italic=True, colour=GREY_TEXT)

banner(s, 0.40, 6.95, 12.55, 0.38,
       "Limits fall straight out of the principle: knife edges can slip · a spring has "
       "limited travel · off before fracture, or the snap whips it.",
       fill=YELLOW_WARN, fg=BLACK, fs=11)
pageno(s)


# ============================== 3. why an extensometer at all — what it refuses to count
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "WHY MEASURE AT THE GAUGE — THE CROSSHEAD COUNTS EVERYTHING")

flow(s, 0.40, 1.45, 2.60, 0.95, "motor commands\ntravel", fill=WHITE, border=FLOW_NEUTRAL,
     fs=11, bold=True)
_SINKS = [
    ("grips seat and slip", RED_FAIL, RGBColor(0xC0, 0x39, 0x2B),
     "the joint beds in — different every mounting"),
    ("frame and load path flex", YELLOW_WARN, RGBColor(0xD2, 0xA6, 0x1B),
     "elastic, invisible from outside"),
    ("the GAUGE stretches", GREEN_PASS, DARK_GREEN,
     "the only part that is the material"),
]
for i, (txt, f, e, sub) in enumerate(_SINKS):
    y = 1.10 + i * 1.15
    arrow(s, 3.00, 1.92, 3.60, y + 0.42, colour=FLOW_NEUTRAL, width=1.6)
    flow(s, 3.62, y, 2.90, 0.85, txt, fill=f, border=e, fs=10.5, bold=True)
    tb(s, 6.65, y + 0.22, 2.55, 0.6, sub, fs=9.0, italic=True, colour=GREY_TEXT)

header(s, 9.45, 1.10, 3.45, "measured on OUR runs")
tb(s, 9.45, 1.46, 3.45, 0.35, "share of travel reaching the gauge:", fs=9.5, colour=BLACK)
_SHARES = [("S25", "21.3 %"), ("S33", "21.2 %"), ("S26", "32.5 %"), ("S34", "32.7 %"),
           ("XT-205 rig", "45.0 %")]
for i, (nm, v) in enumerate(_SHARES):
    y = 1.86 + i * 0.50
    flow(s, 9.45, y, 1.55, 0.42, nm, fill=WHITE, border=FLOW_NEUTRAL, fs=9.5)
    flow(s, 11.10, y, 1.20, 0.42, v, fill=RED_FAIL if float(v[:4]) < 40 else YELLOW_WARN,
         border=FLOW_NEUTRAL, fs=9.5, bold=True)

flow(s, 3.62, 4.68, 5.55, 0.90,
     "an EXTENSOMETER rides the gauge itself —\nboth points ON the specimen, so grips and "
     "frame never enter", fill=LIGHT_BLUE, border=RGBColor(0x2E, 0x6D, 0xA4), fs=10.5,
     bold=True)
arrow(s, 5.05, 4.30, 5.05, 4.66, colour=DARK_GREEN, width=2.0)

tb(s, 0.40, 5.85, 12.55, 0.55,
   "Between half and four-fifths of commanded travel never reaches the gauge — measured, "
   "not assumed. Crosshead-based strain counts all of it as if it were the specimen.",
   fs=10.5, colour=BLACK)

banner(s, 0.40, 6.95, 12.55, 0.38,
       "The crosshead counts everything in the load path; an extensometer — clip-on, camera, "
       "ours — counts only the specimen.",
       fill=GREEN_PASS, fg=DARK_GREEN, fs=11.5)
pageno(s)


# ================================================= 4. the family tree, and where we sit
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "THE FAMILY TREE — AND WHERE THE PPD-UTM SITS")

flow(s, 4.85, 1.20, 3.60, 0.62, "measuring strain", fill=WHITE, border=FLOW_NEUTRAL,
     fs=12, bold=True)

flow(s, 1.20, 2.35, 4.10, 0.80, "at ONE SPOT\nstrain gauge — GLUED on", fill=_ORANGE_BG,
     border=_ORANGE, fs=10.5, bold=True)
flow(s, 8.00, 2.35, 4.10, 0.80, "over a GAUGE LENGTH\nextensometer — ΔL / L₀",
     fill=LIGHT_BLUE, border=RGBColor(0x2E, 0x6D, 0xA4), fs=10.5, bold=True)
arrow(s, 5.90, 1.82, 3.30, 2.33, colour=FLOW_NEUTRAL, width=1.6)
arrow(s, 7.40, 1.82, 10.00, 2.33, colour=FLOW_NEUTRAL, width=1.6)

flow(s, 6.15, 3.65, 2.90, 0.80, "CONTACT\nclip-on, knife edges", fill=WHITE,
     border=FLOW_NEUTRAL, fs=10, bold=True)
flow(s, 9.55, 3.65, 3.35, 0.80, "NON-CONTACT\na camera and marks", fill=LIGHT_BLUE,
     border=RGBColor(0x2E, 0x6D, 0xA4), fs=10, bold=True)
arrow(s, 9.60, 3.17, 7.90, 3.63, colour=FLOW_NEUTRAL, width=1.6)
arrow(s, 10.55, 3.17, 11.10, 3.63, colour=FLOW_NEUTRAL, width=1.6)

flow(s, 7.35, 4.95, 2.75, 0.90, "TWO MARKERS\nXT-205 · PPD-UTM live DIC",
     fill=GREEN_PASS, border=DARK_GREEN, fs=10, bold=True)
flow(s, 10.35, 4.95, 2.58, 0.90, "FULL-FIELD speckle\n2D-DIC — future work",
     fill=GREY_PLANNED, border=FLOW_NEUTRAL, fs=10, bold=True)
arrow(s, 10.75, 4.47, 8.90, 4.93, colour=FLOW_NEUTRAL, width=1.6)
arrow(s, 11.55, 4.47, 11.60, 4.93, colour=FLOW_NEUTRAL, width=1.6)

# tb() takes a plain string, not a list — the ⟪ref⟫ resolver re.subs the text
tb(s, 1.20, 3.45, 4.1, 1.9,
   "•  one small spot, one direction\n"
   "•  superb resolution — it is the LOAD CELL's sensor\n"
   "•  single-use, ≤ ~5 % strain",
   fs=10, colour=BLACK)

tb(s, 1.20, 5.55, 5.6, 0.9,
   "Same maths everywhere on the right branch: two points, ΔL / L₀. Only the transducer "
   "changes — knife edges and a spring, or pixels.",
   fs=10.5, colour=BLACK)

banner(s, 0.40, 6.95, 12.55, 0.38,
       "The XT-205 and the PPD-UTM sit in the SAME green box — which is why their agreement "
       "(0.072 % on one video) validates the implementation, not just the idea.",
       fill=GREEN_PASS, fg=DARK_GREEN, fs=11)
pageno(s)
