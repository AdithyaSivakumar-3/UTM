"""The cross-protocol figure: two fracture protocols, two specimens, one strength.

Every number is read from sf9_data — the same module that draws the SF9 results slides — so the
comparison cannot drift from the runs it describes.

The figure deliberately draws the ANCHOR CORRECTION alongside the 0.9 % difference being discussed.
The correction is about 3.9 MPa and the difference is about 0.19 MPa, and a reader who sees only
the second has no way to judge whether the first was applied consistently. It was: both runs are
anchored within 6 N of each other.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                       # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.abspath(os.path.join(HERE, "..", "figures"))
sys.path.insert(0, HERE)

import sf9_data as SF                                                 # noqa: E402

INK, GRID, MUTED = "#212529", "#DDDDDD", "#666666"
C_SF, C_PC = "#1f77b4", "#e8590c"
GOOD = "#2e7d32"


def data():
    M = SF.M if hasattr(SF, "M") else SF.load()
    a, b = M["sf"], M["pc"]
    d = {
        "t72": {"label": "T7.2 · staircase → fracture", "spec": "S18",
                "uts": a["uts"], "nom": a["uts_nom"], "anchor": a["anchor"],
                "sd": a["anchor_sd"], "halt": a["halt"]},
        "t8": {"label": "T8 · progressive cyclic → fracture", "spec": "S21",
               "uts": b["uts"], "nom": b["uts_nom"], "anchor": b["anchor"],
               "sd": b["anchor_sd"], "halt": b["halt"]},
    }
    d["gap_pct"] = 100.0 * (d["t8"]["uts"] - d["t72"]["uts"]) / d["t72"]["uts"]
    d["gap_mpa"] = d["t8"]["uts"] - d["t72"]["uts"]
    d["corr_mpa"] = 0.5 * ((d["t72"]["uts"] - d["t72"]["nom"]) + (d["t8"]["uts"] - d["t8"]["nom"]))
    d["anchor_gap_n"] = abs(d["t8"]["anchor"] - d["t72"]["anchor"])
    return d


def fig_xprotocol(D=None):
    D = D or data()
    a, b = D["t72"], D["t8"]

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(13.0, 3.05),
                                 gridspec_kw={"width_ratios": [1.0, 1.12], "wspace": 0.26})

    # ---- LEFT: the correction dwarfs the difference, which is the honest framing
    x = [0, 1]
    ax.plot(x, [a["nom"], b["nom"]], "o--", color=MUTED, ms=9, lw=1.6,
            label="as recorded (nominal)")
    ax.plot(x, [a["uts"], b["uts"]], "o-", color=INK, ms=11, lw=2.2,
            label="anchor-corrected (reported)")
    for i, d in enumerate((a, b)):
        ax.annotate("", xy=(i, d["uts"]), xytext=(i, d["nom"]),
                    arrowprops=dict(arrowstyle="->", color=GOOD, lw=1.6))
        ax.text(i + 0.06, 0.5 * (d["uts"] + d["nom"]), "+%.1f MPa\nanchor" % (d["uts"] - d["nom"]),
                fontsize=8.4, color=GOOD, fontweight="bold", va="center")
        ax.text(i, d["uts"] + 0.55, "%.2f" % d["uts"], ha="center", fontsize=10,
                fontweight="bold", color=INK)
        ax.text(i, d["nom"] - 0.95, "%.2f" % d["nom"], ha="center", fontsize=9, color=MUTED)
    ax.set_xticks(x)
    ax.set_xticklabels(["T7.2  ·  %s\nstaircase" % a["spec"],
                        "T8  ·  %s\nprogressive cyclic" % b["spec"]], fontsize=9)
    # Room at the top for the legend: the only band that is empty right across the panel, since
    # the corrected line runs at ~21 and the nominal one at ~17.4.
    ax.set_xlim(-0.42, 1.62); ax.set_ylim(15.4, 24.6)
    ax.set_ylabel("UTS (MPa)", fontsize=9)
    ax.tick_params(labelsize=8.5)
    ax.set_title("The anchor correction is %.1f MPa.\nThe protocol difference under discussion is "
                 "%.2f MPa." % (D["corr_mpa"], D["gap_mpa"]), fontsize=10, color=INK)
    ax.legend(fontsize=8.2, frameon=False, loc="upper center", ncol=2,
              bbox_to_anchor=(0.5, 1.005), handletextpad=0.5, columnspacing=1.6)
    ax.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    # ---- RIGHT: what n = 1 per protocol can and cannot separate
    bx.axis("off")
    bx.set_xlim(0, 1); bx.set_ylim(0, 1)
    bx.text(0.0, 0.95, "What the %.1f %% does and does not settle" % D["gap_pct"],
            fontsize=10.5, fontweight="bold", color=INK, va="top")

    rows = [
        (GOOD, "The two protocols agree to %.1f %%" % D["gap_pct"],
         "%.2f vs %.2f MPa. Both anchored within %.0f N of each other\n(%.0f and %.0f N, sd %.2f "
         "and %.2f), so the correction is applied alike."
         % (a["uts"], b["uts"], D["anchor_gap_n"], a["anchor"], b["anchor"], a["sd"], b["sd"])),
        ("#c0392b", "It CANNOT separate protocol from specimen",
         "Different specimens — %s and %s — and n = 1 each. That %.1f %%\ncontains specimen "
         "scatter as well as any protocol effect." % (a["spec"], b["spec"], D["gap_pct"])),
        (INK, "What it DOES establish is a bound",
         "Whatever the protocol effect is, it is no bigger than %.1f %% plus\nthe scatter — which "
         "is the useful statement, and it is enough to say\nthe two fracture routes give the same "
         "answer." % D["gap_pct"]),
    ]
    y = 0.79
    for col, head, body in rows:
        bx.plot([0.006], [y + 0.012], marker="s", ms=7, color=col, clip_on=False)
        bx.text(0.045, y + 0.015, head, fontsize=9.6, fontweight="bold", color=col, va="center")
        bx.text(0.045, y - 0.055, body, fontsize=8.8, color=INK, va="top", linespacing=1.45)
        y -= 0.30

    fig.subplots_adjust(left=0.055, right=0.995, top=0.845, bottom=0.155)
    fig.savefig(os.path.join(FIGS, "xprotocol.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  xprotocol.png")
    return D


def all_figs():
    print("cross-protocol figure:")
    return fig_xprotocol()


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    d = all_figs()
    print()
    for k in ("t72", "t8"):
        r = d[k]
        print("%-34s %s  UTS %.4f MPa (nominal %.4f, anchor %.1f N)"
              % (r["label"], r["spec"], r["uts"], r["nom"], r["anchor"]))
    print("difference %.4f MPa = %.2f %%" % (d["gap_mpa"], d["gap_pct"]))
