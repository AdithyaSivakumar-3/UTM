# ===================================================================================
#  THE BASIC PCF — operational carbon of the whole project, his scoping (2026-09-05):
#  "just CF from our work from developing to printing to testing", PLA cradle-to-gate
#  deliberately OUT, and the AI collaboration IN as the interesting aspect.
#
#  Method anchored on ISO 14067 / GHG Protocol Product Standard. Every number on these
#  slides is computed by documentation/scripts/pcf_figs.py from the agreed inputs, so
#  the figure and the text cannot drift apart.
# ===================================================================================
import pcf_figs as _PCF                                               # noqa: E402
_PCF.fig_bars()
_LOCAL, _AI3, _TOT = _PCF.totals()
_PER_TEST = 1000 * _TOT / 39
_KM = 1000 * _TOT / 107

_PCF_ISO = "https://www.eea.europa.eu/en/analysis/indicators/greenhouse-gas-emission-intensity-of-1"
_PCF_GEM = "https://cloud.google.com/blog/products/infrastructure/measuring-the-environmental-impact-of-ai-inference"
_PCF_PRUSA = ("https://forum.prusa3d.com/forum/english-forum-original-prusa-i3-mk4-general-"
              "discussion-announcements-and-releases/power-consumption-2/")
_PCF_CAR = "https://www.eea.europa.eu/en/analysis/indicators/co2-performance-of-new-passenger"

# ---------------------------------------------------- 0. what gets calculated (his ask:
# an initial slide with a flowchart of everything this PCF computes)
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "WHAT THIS PCF CALCULATES — THE FOUR TERMS AT A GLANCE")
tb(s, 0.4, 1.08, 12.55, 0.40,
   "One picture of the whole calculation before any number: four activity terms, each turned "
   "into energy, each turned into carbon, summed, and divided by what the project delivered.",
   fs=11.5, italic=True, colour=GREY_TEXT)

flow(s, 4.42, 1.62, 4.55, 0.52,
     "5½ MONTHS OF PROJECT ACTIVITY — everything WE switched on", fill=WHITE, fs=9.6)
_pterms = [
    ("PRINTING\n60 specimens\n× 48 min × 105 W", "#FFF4E6"),
    ("TEST RIG\n7 h powered\n× 45 W", "#EBFBEE"),
    ("PC\n955 h at the desk —\n8 h/day · 5 d/week ·\n5.5 months × 60 W", "#E7F5FF"),
    ("AI COMPUTE\n≈ 7 800 prompt-eq.\n× 0.24 Wh each", "#F8F0FC"),
]
for i, (t_, f) in enumerate(_pterms):
    x = 0.55 + i * 3.22
    arrow(s, 6.70, 2.14, x + 1.45, 2.52, colour=FLOW_NEUTRAL, width=1.4)
    flow(s, x, 2.54, 2.90, 1.02, t_, fill=RGBColor(int(f[1:3], 16), int(f[3:5], 16),
                                                   int(f[5:7], 16)), fs=9.2)
    arrow(s, x + 1.45, 3.56, x + 1.45, 3.94, colour=FLOW_NEUTRAL, width=1.4)
_pconv = [
    ("→ 5.04 kWh × Swedish grid\n0.040 kg CO₂e/kWh", LIGHT_BLUE),
    ("→ 0.32 kWh × the same\ngrid factor", LIGHT_BLUE),
    ("→ 57.3 kWh × the same\ngrid factor", LIGHT_BLUE),
    ("→ 1.9 kWh in a DATA CENTRE\n— two carbon methods, kept\nas a band", "#F3D9FA"),
]
for i, (t_, f) in enumerate(_pconv):
    x = 0.55 + i * 3.22
    fill = f if not isinstance(f, str) or not f.startswith("#") else RGBColor(
        int(f[1:3], 16), int(f[3:5], 16), int(f[5:7], 16))
    flow(s, x, 3.96, 2.90, 0.88, t_, fill=fill, fs=8.8)
    arrow(s, x + 1.45, 4.84, 6.70, 5.28, colour=FLOW_NEUTRAL, width=1.4)
flow(s, 3.60, 5.30, 6.20, 0.58,
     "Σ  =  TOTAL kg CO₂e for the campaign   →   ÷ 39 completed tests  =  the functional unit",
     fill=GREEN_PASS, fs=10.0, bold=True)

tb(s, 0.40, 6.10, 12.4, 0.75,
   "•  Every term is the same shape: ACTIVITY (hours, prints, prompts — measured or agreed) × "
   "POWER (measured, literature, or a stated assumption) × EMISSION FACTOR (grid or "
   "data-centre).\n"
   "•  What is NOT in the picture is stated on the boundary slide: filament production, "
   "embodied hardware, the room itself.",
   fs=9.8, colour=BLACK)
footer(s, "The four slides that follow: method & boundary · the inventory with every source · "
          "the arithmetic in full · the result with its honest band.")
pageno(s)

# ---------------------------------------------------- 1. method and boundary
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "A BASIC PCF OF THIS PROJECT — METHOD AND BOUNDARY")
tb(s, 0.4, 1.10, 12.55, 0.42,
   "Product Carbon Footprint, done the standard way but kept deliberately small: the "
   "OPERATIONAL carbon of 5½ months of work — developing, printing, testing — including "
   "the AI collaboration, on the ISO 14067 / GHG Protocol recipe.",
   fs=11.5, italic=True, colour=GREY_TEXT)

_psteps = [
    ("① goal & scope\n+ FUNCTIONAL UNIT:\nkg CO₂e per completed\ntensile test", WHITE),
    ("② system boundary\noperational only —\nwhat the project ITSELF\nswitched on", WHITE),
    ("③ inventory\nactivity data: hours,\nprints, runs — from the\nrepo and the registry", LIGHT_BLUE),
    ("④ activity × emission\nfactor, summed —\nSweden's grid for local,\nGoogle's figures for AI", LIGHT_BLUE),
    ("⑤ report with the\nuncertainty and the\nexclusions IN THE OPEN", GREEN_PASS),
]
for i, (t_, f) in enumerate(_psteps):
    x = 0.45 + i * 2.55
    flow(s, x, 1.80, 2.35, 1.30, t_, fill=f, fs=8.8)
    if i < 4:
        arrow(s, x + 2.35, 2.45, x + 2.55, 2.45, colour=FLOW_NEUTRAL, width=1.8)

header(s, 0.40, 3.45, 6.05, "Inside the boundary")
tb(s, 0.40, 3.81, 6.05, 1.45,
   "•  Printing 60 specimens (39 tested — the 21 spares and fails are still project inputs "
   "and are charged).\n"
   "•  The rig's electricity across every run, setup included.\n"
   "•  The PC through all development, testing and analysis hours.\n"
   "•  The AI collaboration's data-centre compute — the interesting term.",
   fs=9.8, colour=BLACK)

header(s, 6.85, 3.45, 6.05, "Deliberately OUTSIDE (stated, not hidden)")
tb(s, 6.85, 3.81, 6.05, 1.45,
   "•  Filament cradle-to-gate (his call — it deepens the study without changing what WE "
   "operate).\n"
   "•  Embodied carbon of rig, printer, camera and PC — durable capital, and the amortisation "
   "judgement would dominate every measured term.\n"
   "•  Lab heating/lighting, travel, and the 96.9 GB stored on an already-spinning disk.",
   fs=9.8, colour=BLACK)

banner(s, 0.4, 5.45, 12.55, 0.52,
       "ONE RULE HELD THROUGHOUT: measured where possible (hours, prints, runs), literature "
       "where offered (printer watts, AI energy), assumption where unavoidable (rig watts) — "
       "and every assumption is printed on the next slide.",
       fill=LIGHT_BLUE, fg=BLACK, fs=10.5)
linkbox(s, 0.40, 6.25, 5.5, "EEA — grid intensity of electricity generation (Sweden lowest tier)",
        _PCF_ISO, fs=9.5)
linkbox(s, 6.30, 6.25, 6.0, "Google Cloud — measuring the environmental impact of AI inference "
        "(0.24 Wh / 0.03 g per median prompt)", _PCF_GEM, fs=9.5)
footer(s, "Frame: ISO 14067 (on ISO 14040/44 LCA) and the GHG Protocol Product Standard — "
          "functional unit, boundary, inventory, factors, open reporting.")
pageno(s)

# ---------------------------------------------------- 2. inventory and assumptions
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "THE INVENTORY — EVERY NUMBER AND WHERE IT CAME FROM")

table(s, 0.40, 1.20, 12.55, 3.55, [
    ["Term", "Activity data", "Power / factor", "Source / status"],
    ["printing", "60 prints × 48 min = 48.0 h", "105 W",
     "slicer screenshot · middle of the 80–130 W test-bench range (Prusa forum)"],
    ["rig testing", "2.3 h pulling × 3 for setup ≈ 7 h", "45 W",
     "registry CSVs · ASSUMED: 2 × NEMA-23 ≈ 15 W each at creep speed + drivers, ESP32, "
     "LED, camera ≈ 15 W"],
    ["PC", "8 h/day × 5 days/week × 5.5 months ≈ 955 h at the desk", "60 W",
     "his stated working pattern · laptop + monitor assumed"],
    ["AI compute", "195 h × 40 prompt-equivalents/h ≈ 7 800 (band 20–80/h)", "0.24 Wh & "
     "0.03 g CO₂e per prompt",
     "Google's published median (Aug 2025); agentic multiplier is OUR assumption"],
    ["electricity", "all local terms", "0.040 kg CO₂e/kWh",
     "Sweden — 'tens of grams', among Europe's lowest (EEA)"],
], cw=[1.5, 4.1, 1.9, 5.0], hf=9.5, bf=8.8)

tb(s, 0.40, 4.95, 12.4, 0.90,
   "•  The rig wattage is the softest number on this page — and it multiplies the SMALLEST "
   "term, so even ×3 error moves the total by under 3 %.\n"
   "•  A PROMPT-EQUIVALENT = one median chat prompt in Google's accounting (0.24 Wh, one "
   "question → one answer). An agentic hour fires MANY model calls — every tool use and file "
   "edit is one — so we charge 40 chat-prompts' worth per hour of AI time (195 h), with a "
   "20–80 band carried all the way to the result.",
   fs=9.8, colour=BLACK)

banner(s, 0.4, 6.00, 12.55, 0.52,
       "WHAT A PLUG-IN ENERGY METER WOULD FIX: the printer and rig watts become measurements "
       "in an afternoon. The shape of the result would not change — the grid factor guarantees "
       "that — but two assumptions would retire.",
       fill=YELLOW_WARN, fg=BLACK, fs=10.5)
linkbox(s, 0.40, 6.70, 5.0, "Prusa forum — MK4 power consumption thread (the 80–130 W bench "
        "numbers)", _PCF_PRUSA, fs=9.5)
pageno(s)

# ---------------------------------------------------- 2b. the arithmetic, in full (his ask:
# say HOW the calculation is done — so here it is, every step, no hidden spreadsheet)
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "HOW EACH NUMBER IS COMPUTED — THE ARITHMETIC IN FULL")
tb(s, 0.4, 1.10, 12.55, 0.40,
   "activity × power = energy;  energy × emission factor = carbon. Four rows, one sum, one "
   "division. These cells are printed by the same script that draws the chart, so they cannot "
   "disagree with it.",
   fs=11.5, italic=True, colour=GREY_TEXT)

table(s, 0.40, 1.70, 12.55, 2.85, [
    ["Term", "activity × power", "= energy", "× emission factor", "= kg CO₂e"],
    ["printing", "60 × 0.80 h × 105 W", "%.2f kWh" % _PCF.PRINT_KWH,
     "0.040 kg/kWh (SE grid)", "%.3f" % (_PCF.PRINT_KWH * _PCF.GRID_EF)],
    ["test rig", "7 h × 45 W", "%.2f kWh" % _PCF.RIG_KWH,
     "0.040 kg/kWh (SE grid)", "%.3f" % (_PCF.RIG_KWH * _PCF.GRID_EF)],
    ["PC", "955 h × 60 W", "%.2f kWh" % _PCF.PC_KWH,
     "0.040 kg/kWh (SE grid)", "%.3f" % (_PCF.PC_KWH * _PCF.GRID_EF)],
    ["AI compute", "195 h × 40 prompt-eq/h × 0.24 Wh", "%.2f kWh" % _PCF.AI_KWH[1],
     "two methods — see below", "%.2f  (%.2f–%.2f)" % (_AI3[1], _AI3[0], _AI3[2])],
    ["TOTAL", "", "%.1f kWh local + %.1f kWh cloud"
     % (_PCF.PRINT_KWH + _PCF.RIG_KWH + _PCF.PC_KWH, _PCF.AI_KWH[1]), "",
     "%.2f  (%.2f–%.2f)" % (_TOT, _LOCAL + _AI3[0], _LOCAL + _AI3[2])],
    ["per completed test", "÷ 39 fracture tests", "", "", "≈ %.0f g CO₂e" % _PER_TEST],
], cw=[1.7, 3.6, 2.6, 2.5, 2.1], hf=9.5, bf=9.0,
    ov={(5, 4): {"bg": GREEN_PASS, "bold": True}, (6, 4): {"bg": GREEN_PASS, "bold": True},
        (4, 4): {"bg": YELLOW_WARN}})

header(s, 0.40, 4.80, 12.4, "The AI term's two carbon methods — why it is a band, not a number")
tb(s, 0.40, 5.16, 12.4, 1.20,
   ("•  LOW END, %.2f kg: Google's own published 0.03 g CO₂e per median prompt (their "
    "market-based renewable accounting) on the low prompt count.\n"
    "•  HIGH END, %.2f kg: a location-based 0.35 kg CO₂e/kWh data-centre factor on the high "
    "prompt count — the sceptic's method.\n"
    "•  The slide quotes the midpoint %.2f kg and CARRIES THE BAND — that spread, not the "
    "wattage of any machine here, is the study's real uncertainty.")
   % (_AI3[0], _AI3[2], _AI3[1]),
   fs=9.8, colour=BLACK)

banner(s, 0.4, 6.50, 12.55, 0.50,
       "REPRODUCIBLE BY DESIGN: documentation/scripts/pcf_figs.py holds every input and "
       "prints every cell above — change one assumption and the chart, the table and the "
       "verdict all move together.",
       fill=LIGHT_BLUE, fg=BLACK, fs=10)
pageno(s)

# ---------------------------------------------------- 3. the result
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "THE RESULT — %.1f kg CO₂e, AND WHERE IT SITS" % _TOT)
img_fit(s, "documentation/figures/pcf_bars.png", 0.35, 1.10, 12.6, 3.30)

header(s, 0.40, 4.55, 6.05, "The numbers")
tb(s, 0.40, 4.91, 6.05, 1.50,
   ("•  5½ months, everything on: ≈ %.1f kg CO₂e (honest band %.1f–%.1f).\n"
    "•  Per completed tensile test: ≈ %.0f g CO₂e — about %.0f m in an average new EU car.\n"
    "•  The whole campaign ≈ a %.0f km drive (107 g/km, EEA 2023 WLTP).\n"
    "•  Local electricity is only %.2f kg of it — Sweden's grid makes energy almost free, "
    "carbon-wise.")
   % (_TOT, _LOCAL + _AI3[0], _LOCAL + _AI3[2], _PER_TEST, _PER_TEST / 107 * 1000, _KM,
      _LOCAL),
   fs=9.8, colour=BLACK)

header(s, 6.85, 4.55, 6.05, "The interesting aspects")
tb(s, 6.85, 4.91, 6.05, 1.50,
   ("•  The AI term and the LAPTOP are the two biggest lines — together ≈ %.0f× the test rig "
    "itself. The thinking out-emits the pulling.\n"
    "•  Run on the EU-average grid instead of Sweden's, the local share alone would be ~6× "
    "larger — geography is a real emission factor.\n"
    "•  And the rig's own share is %.0f GRAMS — the 0.4 kJ of mechanical work that breaks "
    "every specimen is, for carbon purposes, nothing.")
   % ((_AI3[1] + _PCF.PC_KWH * _PCF.GRID_EF) / (_PCF.RIG_KWH * _PCF.GRID_EF),
      1000 * _PCF.RIG_KWH * _PCF.GRID_EF),
   fs=9.8, colour=BLACK)

banner(s, 0.4, 6.55, 12.55, 0.52,
       "THE WHOLE 5½-MONTH CAMPAIGN — SIXTY PRINTS, THIRTY-NINE FRACTURES, AN AI "
       "COLLABORATION — COSTS ABOUT ONE %.0f km CAR TRIP. STATED WITH ITS BAND, ITS "
       "EXCLUSIONS AND ITS ASSUMPTIONS ON THE PREVIOUS SLIDE." % _KM,
       fill=GREEN_PASS, fg=DARK_GREEN, fs=10.5)
linkbox(s, 0.40, 7.18, 5.2, "EEA — average CO₂ of new passenger cars (107 g/km, 2023 WLTP)",
        _PCF_CAR, fs=9)
pageno(s)
