"""The PCF bar figure — every number is computed here from the agreed inputs, so the figure
and the slides cannot drift apart. Inputs and their sources:

    printer 105 W    middle of the ~80-130 W test-bench range in the Prusa forum thread he sent
    rig      45 W    assumption: 2x NEMA-23 at ~15 W each at creep speed + drivers/ESP32/LED
                     ~12 W + Basler acA2440 ~3 W  (never measured - no energy meter on site)
    PC       60 W    assumption: laptop + monitor, mid value
    PC time  955 h   his working pattern: 8 h/day x 5 days/week x 5.5 months (2026-09-05)
                     - the DESK time; the 195 h below is only the AI-collaboration subset
    grid   0.040 kg CO2e/kWh   Sweden, "tens of grams" per EEA - among the lowest in Europe
    AI     0.24 Wh and 0.03 g CO2e per median prompt (Google, Aug 2025); agentic coding
           bracketed at 20-80 prompt-equivalents per hour, mid 40
    hours  90 h (first 3 months x 1 h/day) + 105 h (42 active days x 2.5 h) = 195 h
    prints 60 x 48 min      pulls 2.3 h x3 for setup = 7 h rig-on
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                       # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.abspath(os.path.join(HERE, "..", "figures"))
INK, GRID = "#212529", "#DDDDDD"

GRID_EF = 0.040                      # kg CO2e/kWh, Sweden
PC_KWH = 955 * 60 / 1000.0           # 57.3 - 8 h/day x 5 d/wk x 5.5 months at the desk
PRINT_KWH = 60 * (48 / 60.0) * 105 / 1000.0     # 5.04
RIG_KWH = 7 * 45 / 1000.0            # 0.315
AI_PROMPTS = (195 * 20, 195 * 40, 195 * 80)
AI_KWH = tuple(p * 0.24 / 1000.0 for p in AI_PROMPTS)                 # 0.94 / 1.87 / 3.74
AI_KG = (AI_PROMPTS[0] * 0.03 / 1000.0,          # low: Google's own market-based g/prompt
         0.5 * (AI_PROMPTS[0] * 0.03 / 1000.0 + AI_KWH[2] * 0.35),    # mid of the two methods
         AI_KWH[2] * 0.35)                       # high: location-based 0.35 kg/kWh on max use

TERMS = [
    ("AI compute (cloud)", AI_KG[1], (AI_KG[0], AI_KG[2]), "#7B2D8B"),
    ("PC — develop, test, analyse", PC_KWH * GRID_EF, None, "#1F6FB4"),
    ("printing 60 specimens", PRINT_KWH * GRID_EF, None, "#E8590C"),
    ("the test rig itself", RIG_KWH * GRID_EF, None, "#2E9E4F"),
]


def totals():
    local = (PC_KWH + PRINT_KWH + RIG_KWH) * GRID_EF
    return local, AI_KG, local + AI_KG[1]


def fig_bars(out="pcf_bars.png"):
    fig, ax = plt.subplots(figsize=(11.8, 3.1))
    names = [t[0] for t in TERMS][::-1]
    vals = [t[1] for t in TERMS][::-1]
    cols = [t[3] for t in TERMS][::-1]
    bars = ax.barh(names, vals, color=cols, ec=INK, lw=0.6, height=0.55)
    lo, hi = TERMS[0][2]
    ax.errorbar([TERMS[0][1]], [3], xerr=[[TERMS[0][1] - lo], [hi - TERMS[0][1]]],
                fmt="none", ecolor=INK, elinewidth=1.4, capsize=5)
    for b, v in zip(bars, vals):
        ax.text(v + 0.015, b.get_y() + b.get_height() / 2,
                ("%.3f" % v if v < 0.05 else "%.2f" % v) + " kg", va="center", fontsize=9.5,
                color=INK, fontweight="bold")
    local, ai, tot = totals()
    ax.text(0.985, 0.06,
            "TOTAL ≈ %.1f kg CO₂e  (band %.1f–%.1f)   ·   ≈ %.0f km in an average new EU car "
            "(107 g/km)" % (tot, local + ai[0], local + ai[2], 1000 * tot / 107),
            transform=ax.transAxes, ha="right", fontsize=10.5, color=INK, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", fc="#F1F3F5", ec="#ADB5BD"))
    ax.set_xlabel("kg CO₂e — 5½ months of the project, operational boundary", fontsize=10)
    ax.grid(True, color=GRID, lw=0.6, axis="x")
    ax.set_axisbelow(True)
    for spn in ("top", "right"):
        ax.spines[spn].set_visible(False)
    ax.set_title("Where the project's operational carbon actually sits — whisker = the honest "
                 "uncertainty on the AI term", fontsize=11, color=INK)
    fig.tight_layout()
    p = os.path.join(FIGS, out)
    fig.savefig(p, dpi=200, facecolor="white")
    plt.close(fig)
    print("  %s   local %.2f kg, AI %.2f (%.2f-%.2f), total %.2f kg, per test %.0f g"
          % (out, local, ai[1], ai[0], ai[2], tot, 1000 * tot / 39))
    return p


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    fig_bars()


# ---------------------------------------------------------------------------------------
# The counterfactual: what if the 26 468 lines had been typed by hand instead?
#
# Only ONE term changes. The 195 h of agent sessions are a subset of the 955 h of desk
# time; in the solo scenario those 195 h become the hours a human would have needed for
# the same tested code, the AI term goes to zero, and the printer, the rig and the rest of
# the desk time (analysis, writing, rig-side work) are untouched. Boundary is the same
# operational one as above: grid electricity only, no metabolism, commuting or embodied
# hardware on either side, so the two scenarios are like for like.
#
# The multipliers come from Section 3.10 of the report, which brackets its own estimate:
# x6.7 (the ~1 300 h figure) is the stated order of magnitude, x3 is the floor it says
# would still have made the project possible, x10 the pessimistic end.
AI_HOURS = 195                                   # the agent-session subset of the 955 h
SOLO_EST_H = 1300                                # the report's solo estimate, Section 3.10
SOLO_MULT = (3.0, SOLO_EST_H / 195.0, 10.0)      # x3 floor, x6.67 = 1 300 h / 195 h, x10
PC_W = 60
LINES = 26468                                    # development lines, AST scan (Table 23)


def implied_rate(dev_hours):
    """Tested lines per hour the scenario asserts — what the multiplier actually claims."""
    return LINES / float(dev_hours)


def solo_scenario(mult):
    """(solo hours, PC kWh, total kg) if the code had been written without the agent."""
    hours = 955 - AI_HOURS + AI_HOURS * mult
    pc = hours * PC_W / 1000.0
    return hours, pc, (pc + PRINT_KWH + RIG_KWH) * GRID_EF


def breakeven_hours(ai_kg):
    """Solo hours at which the extra PC electricity exactly cancels an AI term of ai_kg."""
    return AI_HOURS + ai_kg / (PC_W / 1000.0 * GRID_EF)


def counterfactual():
    local, ai, tot = totals()
    print("ACTUAL (with the agent)")
    print("  desk 955 h -> PC %.1f kWh; printer %.2f; rig %.2f; AI %.2f kg (%.2f-%.2f)"
          % (PC_KWH, PRINT_KWH, RIG_KWH, ai[1], ai[0], ai[2]))
    print("  total %.2f kg CO2e  (band %.2f-%.2f)" % (tot, local + ai[0], local + ai[2]))
    print("\nSOLO (same code typed by hand, no agent)")
    print("  %-7s %-7s %-7s %-8s %-8s %-13s %s"
          % ("mult", "dev h", "desk h", "PC kWh", "kg", "implied rate", "vs actual"))
    print("  %-7s %-7d %-7d %-8.1f %-8.2f %-13s %s"
          % ("as run", AI_HOURS, 955, PC_KWH, tot,
             "%.0f lines/h" % implied_rate(AI_HOURS), "(measured)"))
    for m in SOLO_MULT:
        h, pc, kg = solo_scenario(m)
        dev = AI_HOURS * m
        print("  x%-6.2f %-7.0f %-7.0f %-8.1f %-8.2f %-13s %+.2f kg (%.2fx)"
              % (m, dev, h, pc, kg, "%.0f lines/h" % implied_rate(dev), kg - tot, kg / tot))
    print("\nWHAT THE AI TERM BOUGHT (mid case, the 1 300 h estimate)")
    h, pc, kg = solo_scenario(SOLO_MULT[1])
    saved = (pc - PC_KWH) * GRID_EF
    print("  %.0f h of PC time avoided = %.1f kWh = %.2f kg, for an AI term of %.2f kg"
          % (h - 955, pc - PC_KWH, saved, ai[1]))
    print("  every 1 kg of AI compute avoided %.1f kg of PC electricity; net %+.2f kg"
          % (saved / ai[1], tot - kg))
    print("\nWHERE IT FLIPS")
    for name, v in (("AI mid", ai[1]), ("AI high", ai[2]), ("AI low", ai[0])):
        b = breakeven_hours(v)
        print("  %-8s break-even at %5.0f solo hours (x%.1f = %.0f lines/h) - below that, "
              "typing by hand emits less" % (name, b, b / AI_HOURS, implied_rate(b)))
    print("\nCORNERS")
    _, _, kg3 = solo_scenario(SOLO_MULT[0])
    _, _, kg10 = solo_scenario(SOLO_MULT[2])
    print("  worst for the agent : solo x3 (%.2f kg) vs actual at AI-high (%.2f kg) -> "
          "hand-typing lower by %.2f kg" % (kg3, local + ai[2], local + ai[2] - kg3))
    print("  best for the agent  : solo x10 (%.2f kg) vs actual at AI-low (%.2f kg) -> "
          "agent lower by %.2f kg" % (kg10, local + ai[0], kg10 - (local + ai[0])))
    print("\nIN CAR-KILOMETRES (107 g/km)")
    print("  actual %.0f km; solo mid %.0f km; difference %.0f km"
          % (1000 * tot / 107, 1000 * solo_scenario(SOLO_MULT[1])[2] / 107,
             1000 * (solo_scenario(SOLO_MULT[1])[2] - tot) / 107))


def fig_solo(out="pcf_solo_bars.png"):
    """The counterfactual as two bars: the project as run, against typing the code by hand."""
    local, ai, tot = totals()
    h3, _, kg3 = solo_scenario(SOLO_MULT[0])
    h7, pc7, kg7 = solo_scenario(SOLO_MULT[1])
    h10, _, kg10 = solo_scenario(SOLO_MULT[2])

    fig, ax = plt.subplots(figsize=(11.8, 3.0))
    dev7 = AI_HOURS * SOLO_MULT[1]
    names = ["same code, typed by hand\n×%.1f → %.0f dev h, %.0f lines/h"
             % (SOLO_MULT[1], dev7, implied_rate(dev7)),
             "as run, with the agent\n%d dev h, %.0f lines/h"
             % (AI_HOURS, implied_rate(AI_HOURS))]
    vals = [kg7, tot]
    ax.barh(names, vals, color=["#B02A37", "#1F6FB4"], ec=INK, lw=0.6, height=0.46)
    # honest band on each bar: the x3-x10 speed-up bracket, and the AI term's own band
    ax.errorbar([kg7], [0], xerr=[[kg7 - kg3], [kg10 - kg7]], fmt="none", ecolor=INK,
                elinewidth=1.4, capsize=5)
    ax.errorbar([tot], [1], xerr=[[ai[1] - ai[0]], [ai[2] - ai[1]]], fmt="none", ecolor=INK,
                elinewidth=1.4, capsize=5)
    for y, v in ((0, kg7), (1, tot)):        # at the bar's left, where no whisker can reach
        ax.text(0.10, y, "%.1f kg" % v, va="center", ha="left", fontsize=12,
                color="white", fontweight="bold")
    ax.annotate("+%.1f kg" % (kg7 - tot), xy=(kg7, 0.34), xytext=(tot, 0.34),
                fontsize=10.5, color=INK, fontweight="bold", va="center", ha="left",
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.3))
    ax.set_xlabel("kg CO$_2$e — same operational boundary on both sides, grid electricity only",
                  fontsize=10)
    ax.set_xlim(0, max(kg10, tot) * 1.06)
    ax.set_ylim(-0.6, 1.6)
    ax.grid(True, color=GRID, lw=0.6, axis="x")
    ax.set_axisbelow(True)
    for spn in ("top", "right"):
        ax.spines[spn].set_visible(False)
    ax.tick_params(labelsize=9.5)
    ax.set_title("What the AI term bought — whiskers: the AI band above, the ×3–×10 "
                 "speed-up bracket below", fontsize=11, color=INK)
    saved = (pc7 - PC_KWH) * GRID_EF
    fig.text(0.5, 0.035,
             "the agent's own %.2f kg of compute avoided %.0f h of laptop time = %.1f kWh = "
             "%.1f kg   ·   net %+.1f kg (%.2f×)   ·   break-even at ×%.1f speed-up"
             % (ai[1], h7 - 955, pc7 - PC_KWH, saved, tot - kg7, kg7 / tot,
                breakeven_hours(ai[1]) / AI_HOURS),
             ha="center", fontsize=10, color=INK,
             bbox=dict(boxstyle="round,pad=0.4", fc="#F1F3F5", ec="#ADB5BD"))
    fig.tight_layout(rect=(0, 0.11, 1, 1))
    p = os.path.join(FIGS, out)
    fig.savefig(p, dpi=200, facecolor="white")
    plt.close(fig)
    print("  %s   actual %.2f kg, solo x6.7 %.2f kg (x3 %.2f, x10 %.2f), net %+.2f kg"
          % (out, tot, kg7, kg3, kg10, tot - kg7))
    return p
