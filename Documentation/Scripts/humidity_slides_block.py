# ===================================================================================
#  HUMIDITY vs FILAMENT — the literature study he asked for (2026-09-05), from the
#  three references he supplied. Both papers were read IN FULL from the PDFs in
#  documentation/Literature/; the vendor page is uncited practice guidance and is
#  weighted accordingly (his instruction: trust literature more than website).
#
#    A — Hamid, Hamezah & Abd Razak 2022, SympoSIMM 2021 / LNME 497-502,
#        doi 10.1007/978-981-16-8954-3_47   (documentation/Literature/2022_Book_...)
#    B — Quader, Dramko, Grewell, Randall & Narayanan 2024, 3D Printing and
#        Additive Manufacturing 11(3):e1151-e1161, doi 10.1089/3dp.2022.0222
#        (documentation/Literature/3dp.2022.0222.pdf)
#    C — ACO "Impact of Humidity on 3D Printing Filament Performance" (vendor note)
#
#  Every number on these four slides is quoted from those sources or from this
#  project's own V6 quintet (repeatability slide) — nothing remembered, nothing invented.
# ===================================================================================

_HUM_A = "https://doi.org/10.1007/978-981-16-8954-3_47"
_HUM_B = "https://doi.org/10.1089/3dp.2022.0222"
_HUM_B_PMC = "https://pmc.ncbi.nlm.nih.gov/articles/PMC11442157/"
_HUM_C = "https://www.acotoner.com/mn/impact-humidity-3d-printing-filament-performance.html"

# ---------------------------------------------------- 1. the mechanism, and the sources
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "HUMIDITY AND FILAMENT — WHAT THE LITERATURE SAYS")
tb(s, 0.4, 1.10, 12.55, 0.42,
   "Two peer-reviewed studies (read in full) and one vendor note, on one question: what does "
   "absorbed moisture do to the tensile strength of printed PLA? The short answer — PLA is "
   "hygroscopic, and the damage is done AT THE NOZZLE, not on the shelf.",
   fs=11.5, italic=True, colour=GREY_TEXT)

_hchain = [
    ("room air\n(relative humidity)", WHITE),
    ("hygroscopic PLA absorbs water\n≤ 0.7 wt % in a week at 80 % RH\n(Quader, weighed)", WHITE),
    ("at the ~210 °C nozzle the\nabsorbed water flashes to steam", LIGHT_BLUE),
    ("bubbles + porosity in the bead\nSEM: 1.2 % dried → 3.0 % soaked\n(Quader)", LIGHT_BLUE),
    ("plasticization + chain hydrolysis\nwater H-bonds between chains\n(both papers)", LIGHT_BLUE),
    ("weaker, rougher part:\nUTS DOWN · ε_f UP\nstiffness down", GREEN_PASS),
]
for i, (t_, f) in enumerate(_hchain):
    r, c = divmod(i, 3)
    x, y = 0.55 + c * 4.25, 1.75 + r * 1.45
    flow(s, x, y, 3.85, 1.10, t_, fill=f, fs=9.6)
    if c < 2:
        arrow(s, x + 3.85, y + 0.55, x + 4.25, y + 0.55, colour=FLOW_NEUTRAL, width=2.0)
arrow(s, 0.55 + 2 * 4.25 + 1.9, 1.75 + 1.10, 0.55 + 1.9, 1.75 + 1.45 + 0.2,
      colour=FLOW_NEUTRAL, width=2.0)

header(s, 0.40, 4.68, 12.4, "The three sources, and the weight each carries")
tb(s, 0.40, 5.04, 12.4, 1.05,
   "•  A — Hamid et al. 2022 (UTeM Malaysia): one spool, three storage conditions, humidifier "
   "exposure 24–150 h, printed and pulled. The cleanest storage experiment of the three.\n"
   "•  B — Quader et al. 2024 (North Dakota State Univ.): four PLA grades × five humidity "
   "levels in a calibrated chamber + a 3-month room-storage arm; ANOVA, SEM, melt-flow. The "
   "most complete methodology.\n"
   "•  C — ACO (vendor page, uncited): used ONLY for the workshop symptoms and drying "
   "practice — not for numbers.",
   fs=9.8, colour=BLACK)

linkbox(s, 0.40, 6.30, 4.0, "A · Hamid 2022 — doi 10.1007/978-981-16-8954-3_47", _HUM_A, fs=9.5)
linkbox(s, 4.55, 6.30, 4.4, "B · Quader 2024 — doi 10.1089/3dp.2022.0222 (open at PMC)", _HUM_B_PMC, fs=9.5)
linkbox(s, 9.15, 6.30, 3.7, "C · ACO vendor note on filament humidity", _HUM_C, fs=9.5)
footer(s, "Both PDFs are archived in documentation/Literature/. Slide numbers quote the papers "
          "directly; the project's own numbers appear only on the last slide of this block.")
pageno(s)

# ---------------------------------------------------- 2. methods and magnitudes
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "HOW THE EFFECT WAS MEASURED — AND HOW BIG IT IS")

header(s, 0.40, 1.10, 6.0, "A · Hamid 2022 — the storage experiment")
tb(s, 0.40, 1.46, 6.0, 1.00,
   "One PLA spool, three fates: brand-new (reference), used but sealed in a vacuum bag with "
   "50 g desiccant, and used but left open next to a humidifier for 24–150 h. ASTM D638 "
   "Type IV, 100 % infill, printed at 210 °C, pulled at 5 mm/min, n = 3 per condition.",
   fs=9.6, colour=BLACK)
table(s, 0.40, 2.52, 6.0, 1.95, [
    ["Spool condition", "UTS (MPa)", "vs reference"],
    ["new spool (reference)", "16.49", "—"],
    ["vacuum bag + desiccant", "16.47", "−0.1 %"],
    ["open + humid, 24 h", "15.09", "−8.5 %"],
    ["open + humid, 150 h", "14.68", "−11.0 %"],
], cw=[2.7, 1.5, 1.6], hf=9.5, bf=9.5,
    ov={(2, 2): {"bg": GREEN_PASS, "bold": True},
        (3, 2): {"bg": RED_FAIL, "bold": True},
        (4, 2): {"bg": RED_FAIL, "bold": True}})
tb(s, 0.40, 4.60, 6.0, 0.72,
   "•  Most of the damage lands in the FIRST 24 h; after that it creeps.\n"
   "•  Fracture strain went UP in every humidified group — the plasticization signature.",
   fs=9.6, colour=BLACK)

header(s, 6.85, 1.10, 6.0, "B · Quader 2024 — the chamber study")
tb(s, 6.85, 1.46, 6.0, 1.42,
   "Four PLA grades dried per datasheet, then one week in a calibrated Binder chamber at "
   "25 °C — 50 / 65 / 80 % RH and water-submerged — weighed before and after, printed "
   "(100 % infill), pulled per ASTM D638-IV with an extensometer, n = 3, two-way ANOVA + "
   "Tukey. Plus SEM porosity of the fracture faces, melt-flow index, filament-level tensile "
   "tests, and a separate 3-MONTH room-storage arm.",
   fs=9.6, colour=BLACK)
table(s, 6.85, 2.94, 6.0, 1.68, [
    ["Condition (1 week unless said)", "Effect on printed UTS"],
    ["dried / 50 % / 65 % RH", "within 3.73 % of each other"],
    ["80 % RH / submerged", "drastic drop (sensitive grade ~ −35 %)"],
    ["3 months at ROOM condition", "−24 % to −36 % — despite ≤0.25 wt % gain"],
], cw=[3.0, 3.0], hf=9.5, bf=9.3,
    ov={(1, 1): {"bg": GREEN_PASS}, (2, 1): {"bg": RED_FAIL}, (3, 1): {"bg": RED_FAIL, "bold": True}})
tb(s, 6.85, 4.72, 6.0, 0.62,
   "•  Melt-flow index rose ~50 % with moisture — wet filament FLOWS differently, so the "
   "print itself changes, not just the chemistry.\n"
   "•  Sensitivity is grade chemistry: the 4.3 % d-lactide grade fell hardest.",
   fs=9.6, colour=BLACK)

banner(s, 0.4, 5.75, 12.55, 0.52,
       "THE TWO STUDIES AGREE ON DIRECTION AND MECHANISM: moisture in the FILAMENT costs "
       "tensile strength and buys ductility. Below ~65 % RH and a week, the cost is a few "
       "per cent; open humid air or months on a shelf cost tens of per cent.",
       fill=LIGHT_BLUE, fg=BLACK, fs=10.5)
footer(s, "Numbers quoted from the papers' own tables and figures — Hamid Table 3; Quader "
          "Figs. 2, 5, 7, 8 and the drying/storage section.")
pageno(s)

# ---------------------------------------------------- 3. control while printing
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "HUMIDITY CONTROL WHILE PRINTING — WHAT ACTUALLY WORKS")
tb(s, 0.4, 1.10, 12.55, 0.42,
   "Both papers condition the FILAMENT, not the finished part — what matters is the water "
   "arriving at the nozzle. So control is a storage-and-drying problem, and it is cheap.",
   fs=11.5, italic=True, colour=GREY_TEXT)

header(s, 0.40, 1.70, 6.0, "Symptoms during a print (vendor note C)")
tb(s, 0.40, 2.06, 6.0, 1.35,
   "•  Steam bubbles and popping at the nozzle — moisture vaporising.\n"
   "•  Stringing, pits and rough surfaces; in bad cases nozzle clogs.\n"
   "•  Weakened interlayer adhesion — the strength loss you later measure.\n"
   "•  These are the FREE early warnings: if a print hisses, the spool is wet.",
   fs=9.8, colour=BLACK)

header(s, 6.85, 1.70, 6.0, "What the papers measured about control")
tb(s, 6.85, 2.06, 6.0, 1.35,
   "•  Sealed vacuum bag + 50 g desiccant kept a USED spool at reference strength — "
   "16.47 vs 16.49 MPa. A drying cabinet is not required (Hamid).\n"
   "•  Store at ~25 °C / ≤50 % RH; a spool lives ~7 days in room air before it needs "
   "re-drying (Quader).\n"
   "•  Drying per the datasheet recovers >90 % of the absorbed water (Quader, reverse-"
   "drying experiment). Vendor practice says 40–60 °C for 3–6 h — same ballpark.",
   fs=9.8, colour=BLACK)

table(s, 0.40, 3.70, 12.4, 1.62, [
    ["Control", "Evidence", "Cost", "Verdict"],
    ["vacuum bag + desiccant between prints", "measured = new spool (A)", "~nothing",
     "DO ALWAYS"],
    ["room storage ≤50 % RH, re-dry after ~7 days", "B's storage arm", "a hygrometer",
     "do when spool is out"],
    ["dry 40–60 °C, 3–6 h before critical prints", "B reverse-dry >90 % · C practice",
     "oven time", "do before test batches"],
    ["watch grade quirks (one grade deformed at 80 °C)", "B — dried that grade at 50 °C",
     "—", "check the TDS"],
], cw=[4.3, 3.4, 1.6, 2.2], hf=9.5, bf=9.0,
    ov={(1, 3): {"bg": GREEN_PASS, "bold": True}})

banner(s, 0.4, 5.60, 12.55, 0.52,
       "FOR THIS PROJECT: the specimens that feed a comparison should come from a spool with "
       "the SAME storage history — sealed with desiccant between sessions, dried before a "
       "batch. That is the whole discipline, and it costs a zip bag.",
       fill=GREEN_PASS, fg=DARK_GREEN, fs=10.5)
footer(s, "Print-room RH itself matters mainly through the hours a spool hangs open on the "
          "printer — the papers' exposure clocks start exactly there.")
pageno(s)

# ---------------------------------------------------- 4. does it explain OUR spread?
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "DOES THIS EXPLAIN OUR OWN UTS SPREAD?")
tb(s, 0.4, 1.10, 12.55, 0.42,
   "The question: our specimens print with slightly different UTS — can the humidity "
   "literature justify that? The honest answer: it is direction-consistent and size-plausible "
   "for the between-BATCH gap, and unproven without a humidity log.",
   fs=11.5, italic=True, colour=GREY_TEXT)

table(s, 0.40, 1.68, 6.0, 2.30, [
    ["V6 quintet (100 % infill)", "UTS (MPa)", "ε_f (–)"],
    ["S7 — pilot, printed 8 days EARLIER", "47.82", "0.030"],
    ["S8 (matched batch)", "44.83", "0.052"],
    ["S10 (matched batch)", "46.82", "0.073"],
    ["S11 (matched batch)", "46.10", "0.050"],
    ["S9 (matched batch)", "45.47", "0.074"],
    ["batch mean vs pilot", "45.81  (−4.2 %)", "↑ 1.7–2.5×"],
], cw=[3.3, 1.5, 1.0], hf=9.3, bf=9.0,
    ov={(1, 0): {"bold": True}, (6, 1): {"bg": YELLOW_WARN, "bold": True},
        (6, 2): {"bg": YELLOW_WARN, "bold": True}})

header(s, 6.85, 1.62, 6.0, "The direction test — both signatures match")
tb(s, 6.85, 1.98, 6.0, 1.30,
   "•  Literature: moisture ⇒ UTS DOWN and ε_f UP (plasticization), never one without the "
   "other.\n"
   "•  Ours: the batch printed 8 days later off the same spool is 4.2 % WEAKER and 1.7–2.5× "
   "MORE DUCTILE than the pilot. Both arrows point the moisture way.\n"
   "•  Size is plausible too: −4 % per extra week in room air sits between B's ≤3.7 % "
   "(≤65 % RH, 1 week) and A's −8.5 % (open humid air, 24 h).",
   fs=9.6, colour=BLACK)

header(s, 6.85, 3.42, 6.0, "What is deliberately NOT claimed")
tb(s, 6.85, 3.78, 6.0, 1.30,
   "•  n = 1 pilot against one batch — a single 8-day story, not a trend.\n"
   "•  No RH log exists for the print room, and the spool's open-air hours were not recorded.\n"
   "•  Same-day specimens still differ by ~2 % (matched-batch CV 1.9 %) — that floor is NOT "
   "humidity, it is ordinary print scatter.\n"
   "•  Bed adhesion, first-layer luck and ambient temperature were not controlled either.",
   fs=9.6, colour=BLACK)

banner(s, 0.4, 5.30, 12.55, 0.62,
       "VERDICT: humidity is a PLAUSIBLE, direction-consistent contributor to the pilot-vs-"
       "batch UTS gap — and unprovable in hindsight. The decisive experiment is cheap: DRY the "
       "spool (50 °C · 4 h), reprint two specimens, compare. Drying recovers >90 % of absorbed "
       "water (B), so if strength rebounds toward the pilot, moisture is convicted.",
       fill=YELLOW_WARN, fg=BLACK, fs=10.5)
footer(s, "This is the study behind the final presentation's 'moisture — study pending' card. "
          "The V6 quintet numbers are this project's own repeatability slide, unchanged.")
pageno(s)
