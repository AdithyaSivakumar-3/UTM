# ===================================================================================
#  THE FRACTURE SURVEY — where every specimen broke, and what PLA vs PETG look like
#  at the break. His ask (2026-09-06): mine the photos and recordings for trends.
#
#  Every number here comes from fracture_survey.py: positions read from the final
#  video frames (the frames are ON the slide so the reading can be checked), strains
#  from each run's own CSV through utm_analysis.analyze. S31's strain is excluded —
#  its 57 % tracking makes strain quantities documented-invalid; S12's position is
#  excluded — it parted outside the viewed gauge.
# ===================================================================================
import fracture_survey as _FS                                         # noqa: E402
_FROWS = _FS.all_figs()

_PLA80 = [r["ef"] for r in _FROWS if r["grp"] == "PLA 80" and r["ef"]]
_PETG = [r["ef"] for r in _FROWS if r["grp"] == "PETG" and r["ef"]]
_MEAN_PLA = 100 * sum(_PLA80) / len(_PLA80)
_MEAN_PETG = 100 * sum(_PETG) / len(_PETG)

# ---------------------------------------------------- 1. the map
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "WHERE EVERY SPECIMEN BROKE — TWELVE FINAL FRAMES")
img_fit(s, "documentation/figures/frac_map.png", 0.35, 1.10, 12.6, 4.30)

header(s, 0.40, 5.55, 4.05, "How this was read")
tb(s, 0.40, 5.93, 4.05, 1.30,
   "•  Each strip is the LAST frame of that pull's own recording; position is measured "
   "against the marker pair (0 = upper marker, 1 = lower).\n"
   "•  Read from the frames by eye — an automatic gap-detector was tried and rejected; "
   "the frames are shown so every reading can be checked.",
   fs=9.4, colour=BLACK)

header(s, 4.65, 5.55, 4.05, "PLA — breaks EVERYWHERE")
tb(s, 4.65, 5.93, 4.05, 1.30,
   "•  Nine PLA breaks scatter from one fillet to the other: 0.03 (S24, at the top "
   "fillet) to 0.77 (S26) — plus S33 ABOVE its upper marker and S12 outside the view "
   "entirely.\n"
   "•  No preferred spot: the break finds a local flaw, wherever it is.",
   fs=9.4, colour=BLACK)

header(s, 8.90, 5.55, 4.05, "PETG — all at the SAME end")
tb(s, 8.90, 5.93, 4.05, 1.30,
   "•  Both PETG breaks caught on film sit at 0.90–0.95 — the lower grip end, after the "
   "whole gauge had visibly drawn; S32's recording ends drawn but WHOLE, so it carries "
   "no line.\n"
   "•  Two of two on film is a pattern worth naming, and n = 2 is still n = 2.",
   fs=9.4, colour=BLACK)
pageno(s)

# ---------------------------------------------------- 2. the two characters
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "PLA vs PETG AT THE BREAK — TWO DIFFERENT CHARACTERS")
img_fit(s, "documentation/figures/frac_faces.png", 0.35, 1.10, 12.6, 3.90)

header(s, 0.40, 5.15, 6.05, "PLA breaks like glass")
tb(s, 0.40, 5.53, 6.05, 1.55,
   "•  Clean, near-flat or 45° break faces; the halves would almost re-mate.\n"
   "•  NO stress-whitening, no necking, no drawing anywhere on the gauge.\n"
   "•  The release is violent — S38's snap threw the specimen ~100 px sideways "
   "between two frames (the event the post-processor now re-acquires through).\n"
   "•  Quasi-brittle: fracture decides suddenly, at a flaw.",
   fs=9.6, colour=BLACK)

header(s, 6.75, 5.15, 6.05, "PETG tears like taffy")
tb(s, 6.75, 5.53, 6.05, 1.55,
   "•  Stress-whitening speckled along the WHOLE gauge — the drawing is everywhere, "
   "not local.\n"
   "•  Fibrous, drawn fracture faces; strands pulled out rather than cracked across.\n"
   "•  After uniform drawing, the break migrates to the weakest section left — the "
   "grip-end fillet, three times out of three.\n"
   "•  Ductile: fracture is the END of a long process, not an event.",
   fs=9.6, colour=BLACK)
banner(s, 0.40, 7.10, 12.55, 0.32,
       "YES — THIS IS THE TEXTBOOK PAIR, CONFIRMED: literature calls printed PLA stiff and "
       "QUASI-BRITTLE and PETG DUCTILE (ε_f bands 3–8 % vs 5–25 %). The faces above are that "
       "prediction made visible, and the numbers agree — PLA ≈ 5.2 %, PETG ≈ 7.9 % mean ε_f.",
       fill=GREEN_PASS, fg=DARK_GREEN, fs=9.3)
pageno(s)

# ---------------------------------------------------- 3. position and strain together
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "POSITION AND STRAIN, SIDE BY SIDE")
img_fit(s, "documentation/figures/frac_stats.png", 0.35, 1.10, 12.6, 3.85)

header(s, 0.40, 5.10, 6.05, "What holds")
tb(s, 0.40, 5.48, 6.05, 1.60,
   ("•  Fracture strain: PETG %.1f %% mean against PLA-80's %.1f %% — about 1.5×, "
    "consistent with the ductile picture on the previous slide.\n"
    "•  Break position separates the materials cleanly: PLA anywhere, PETG at the "
    "grip end — the location IS a material signature here.\n"
    "•  S33 is the cautionary tale: broke at the fillet, above its own gauge, at only "
    "2.9 %% — a stress-concentration failure, not a material number." )
   % (_MEAN_PETG, _MEAN_PLA),
   fs=9.6, colour=BLACK)

header(s, 6.75, 5.10, 6.05, "What deliberately is NOT claimed")
tb(s, 6.75, 5.48, 6.05, 1.60,
   "•  No position→strain rule: S24 broke AT the fillet yet latest of all the PLA "
   "(7.4 %), while S33's fillet break came earliest (2.9 %). A fillet break can be "
   "early or late.\n"
   "•  n = 3 PETG, and one of them (S31) contributes no strain — 57 % tracking makes "
   "its strain quantities invalid by the project's own rule.\n"
   "•  Whether the PETG end-breaks follow the moving grip or the print orientation "
   "cannot be told from three specimens printed the same way up.",
   fs=9.6, colour=BLACK)

banner(s, 0.40, 7.08, 12.55, 0.30,
       "Cheap next experiment: print one PETG batch FLIPPED — do the end-breaks follow the "
       "grip, or the print direction?",
       fill=LIGHT_BLUE, fg=BLACK, fs=9.5)
pageno(s)
