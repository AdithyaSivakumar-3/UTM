# ===================================================================================
#  The two remaining deck gaps: the cross-protocol result, and the two workflow guards.
#
#  Appended to generate_v6a_slides.py. The cross-protocol numbers come from sf9_data,
#  the same module the SF9 results slides use, so they cannot drift apart.
# ===================================================================================
import xprotocol_plots as _XPP                                        # noqa: E402

_XP = _XPP.all_figs()
_T72, _T8 = _XP["t72"], _XP["t8"]


# ================================================================= 1. cross-protocol result
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "TWO FRACTURE PROTOCOLS, ONE STRENGTH — T7.2 AGAINST T8")

tb(s, 0.45, 1.12, 12.5, 0.46,
   "The rig can break a specimen two ways: a staircase that climbs to failure, and a progressive "
   "cyclic schedule that fatigues then breaks it. If the machine is measuring the MATERIAL, the "
   "route it took should not change the answer.",
   fs=11, colour=BLACK)

img_fit(s, "documentation/figures/xprotocol.png", 0.4, 1.60, 12.55, 2.70)

header(s, 0.45, 4.34, 6.25, "The two runs, side by side")
table(s, 0.45, 4.72, 6.25, 1.64, [
    ["", "T7.2 staircase", "T8 prog. cyclic"],
    ["specimen", _T72["spec"], _T8["spec"]],
    ["UTS, as recorded", "%.2f MPa" % _T72["nom"], "%.2f MPa" % _T8["nom"]],
    ["preload anchor", "%.0f N (sd %.2f)" % (_T72["anchor"], _T72["sd"]),
     "%.0f N (sd %.2f)" % (_T8["anchor"], _T8["sd"])],
    ["UTS, anchor-corrected", "%.2f MPa" % _T72["uts"], "%.2f MPa" % _T8["uts"]],
    ["halted within", "%.2f s" % _T72["halt"], "%.2f s" % _T8["halt"]],
], cw=[2.35, 1.95, 1.95], hf=9.5, bf=8.5)

header(s, 6.95, 4.34, 6.0, "Why this is worth a slide")
tb(s, 6.95, 4.72, 6.0, 1.64,
   "It is the only cross-check the rig can run on ITSELF. Every other agreement in this deck is "
   "the same protocol repeated, or our DIC against our own crosshead. Here two different control "
   "loops, two different load histories and two different specimens land %.2f MPa apart — %.1f %% "
   "— and both auto-stopped on load collapse inside %.2f s.  The anchor correction is worth "
   "%.1f MPa, twenty times the difference being discussed, which is why the figure shows it: a "
   "%.1f %% agreement means nothing unless the correction behind it was applied the same way to "
   "both, and it was, to within %.0f N."
   % (_XP["gap_mpa"], _XP["gap_pct"], max(_T72["halt"], _T8["halt"]), _XP["corr_mpa"],
      _XP["gap_pct"], _XP["anchor_gap_n"]),
   fs=10, colour=BLACK)

banner(s, 0.4, 6.44, 12.55, 0.50,
       "THE CAVEAT, AND IT IS NOT A SMALL ONE: these are DIFFERENT SPECIMENS, n = 1 each. The "
       "%.1f %% contains specimen-to-specimen scatter as well as any protocol effect, and nothing "
       "here can separate the two. It bounds the protocol effect; it does not measure it."
       % _XP["gap_pct"],
       fill=YELLOW_WARN, fg=BLACK, fs=10)
footer(s, "Both values are anchor-corrected true UTS from sf9_data, computed from the CSVs rather "
          "than restated. Nominal (uncorrected) values are on the figure.")
pageno(s)


# ================================================================= 2. the two workflow guards
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "TWO GUARDS BETWEEN THE OPERATOR AND A WASTED SPECIMEN")

tb(s, 0.45, 1.12, 12.5, 0.46,
   "Recipes are covered on ⟪SF3 · SETTINGS (RECIPES)⟫. These are the other two workflow features, "
   "and both share a property that makes them easy to overlook: when they are working correctly, "
   "nothing happens.",
   fs=11, colour=BLACK)

header(s, 0.45, 1.72, 6.25, "The destructive-test confirmation")
tb(s, 0.45, 2.10, 6.25, 2.05,
   "A fracture test destroys the specimen and cannot be repeated, so it is the one place where a "
   "stale setting is unrecoverable. The dialog therefore does not just ask “are you sure” — it "
   "reads the specimen back:  area, gauge, material and INFILL, in the same order and wording the "
   "CSV header will carry, so what is confirmed and what is recorded cannot drift apart.\n\n"
   "Underneath it lists the preparation steps, ordered by the CURRENT strain-zero convention — "
   "under the after-preload rule the preload comes first, so the checklist changes with the "
   "setting rather than describing the opposite procedure.\n\n"
   "Cancel is the DEFAULT button. A returned keypress does not start a destructive test.",
   fs=10, colour=BLACK)

header(s, 6.95, 1.72, 6.0, "Why it exists — a real cost, already paid")
tb(s, 6.95, 2.10, 6.0, 2.05,
   "T6.4, T6.5 and both T9 runs recorded “Infill: 100 %” on 50 % specimens. T7.3 — the same "
   "mistake waiting to happen — came out right, and the reason is exactly this dialog: it was a "
   "fracture test, so the label was echoed back and caught.\n\n"
   "The four that went wrong were NON-destructive and had no such gate. That asymmetry is what "
   "prompted the 2026-09-01 change putting the same read-back into Prepare test, which every test "
   "type performs.",
   fs=10, colour=BLACK)

header(s, 0.45, 4.32, 12.5, "The stall guard, and why a flat threshold could not work")
table(s, 0.45, 4.70, 12.5, 1.60, [
    ["", "Value", "Why this and not something simpler"],
    ["window", "%.0f s" % 6.0,
     "long enough that one slow load-cell sample cannot trip it"],
    ["must advance by", "min(0.05 mm, 35 % of commanded)",
     "a FLAT 0.05 mm assumed every mode runs near 0.1 mm/s, where 0.6 mm is expected and the bar "
     "is 8 %"],
    ["at a tapered crawl", "0.01–0.02 mm/s → 0.06–0.12 mm expected",
     "a flat 0.05 mm would demand 42–83 % of commanded travel, and a HEALTHY motor trips on "
     "rounding alone"],
    ["only guards above", "200 N",
     "below that the crosshead may legitimately be taking up slack, not pulling"],
    ["nothing commanded", "threshold 0 — cannot fire",
     "a hold is not a stall, and the guard must not invent one"],
], cw=[2.05, 3.05, 7.40], hf=9.5, bf=8.5)

banner(s, 0.4, 6.44, 12.55, 0.50,
       "BOTH ARE JUDGED BY WHAT THEY DID NOT DO. The stall guard stayed silent through every "
       "ductile 100 % draw — the case that looks most like a stall and is not — and fired on T7, "
       "which really had stopped advancing. A guard that cries wolf gets switched off.",
       fill=GREEN_PASS, fg=DARK_GREEN, fs=10)
footer(s, "Constants read from main.py: STALL_WINDOW_S, STALL_MIN_ADVANCE_MM, "
          "STALL_SHORTFALL_FRAC, STALL_MIN_LOAD_N.")
pageno(s)
