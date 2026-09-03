"""Figures for MOT Test 2 against the PPD-UTM's own 45 mm runs.

  mot2cmp_stress.png    the two stress-strain curves, with every landmark marked
  mot2cmp_strain.png    strain against time — the DIC records side by side
  mot2cmp_elastic.png   the elastic region, both modulus methods on both machines
  mot2cmp_noise.png     residual scatter, and our floor against the 1/Px0 prediction

Everything is read from mot2_compare, which reads the raw records. Nothing is retyped.
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

import mot2_compare as C                                              # noqa: E402

INK, GRID, MUTED = "#212529", "#DDDDDD", "#666666"
# The XT-205 keeps the red it wears on the two MOT Test 2 slides before these; the PPD-UTM
# takes blue and the second reference grey, so MOT-vs-PPD-UTM reads at a glance.
COL = {"MOT": "#d62728", "S34": "#1F6FB4", "S33": "#9AA5AB"}
LW = {"MOT": 1.9, "S34": 1.9, "S33": 1.3}


def _style(ax):
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def _order(B):
    return ["MOT", B["primary"], B["second"]]


def _name(B, k):
    return "MOT XT-205" if k == "MOT" else "%s · PPD-UTM" % k


# --------------------------------------------------------------------------- stress-strain
def fig_stress(B=None):
    B = B or C.build()
    fig, ax = plt.subplots(figsize=(6.30, 3.55))

    for k in _order(B):
        r = B["recs"][k]
        ax.plot(r["e"], r["sig"], "-", color=COL[k], lw=LW[k], label=_name(B, k),
                alpha=1.0 if k != "S33" else 0.75)

    for k in ("MOT", B["primary"]):
        l = B["L"][k]
        ax.plot([l["uts_e"]], [l["uts"]], "o", ms=7, color=COL[k], mec="white", mew=1.2, zorder=5)
        ax.plot([l["ef"]], [l["sigf"]], "s", ms=6.5, color=COL[k], mec="white", mew=1.2, zorder=5)
        if np.isfinite(l["sy_steep"]):
            ax.plot([l["sy_steep_e"]], [l["sy_steep"]], "^", ms=7, color=COL[k],
                    mec="white", mew=1.2, zorder=5)

    lu, pu = B["L"]["MOT"], B["L"][B["primary"]]
    ax.annotate("UTS  %.2f vs %.2f MPa\n(%+.1f %%)"
                % (lu["uts"], pu["uts"], C.offset_pct(lu["uts"], pu["uts"])),
                xy=(pu["uts_e"], pu["uts"]), xytext=(2.35, 30.5), fontsize=8.2, color=INK,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.1))
    ax.annotate("fracture  %.2f vs %.2f %%\n(%+.1f %%)"
                % (lu["ef"], pu["ef"], C.offset_pct(lu["ef"], pu["ef"])),
                xy=(lu["ef"], lu["sigf"]), xytext=(3.05, 17.5), fontsize=8.2, color=INK,
                fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.1))

    ax.set_xlabel("strain (%)  —  both on our preload-frozen zero", fontsize=9)
    ax.set_ylabel("engineering stress (MPa)", fontsize=9)
    ax.set_title("Stress–strain: MOT XT-205 against the PPD-UTM's 45 mm runs",
                 fontsize=10, color=INK)
    ax.legend(fontsize=8.2, loc="upper left", frameon=False, ncol=1,
              title="▲ yield   ● UTS   ■ fracture", title_fontsize=7.6)
    # Both curves start at the preload stress rather than at zero, and they start at the SAME one —
    # which is the visual form of the two zeros having been put on one convention.
    ax.annotate("both start at the preload stress,\nnot at zero — the zeros are aligned",
                xy=(0.02, B["recs"]["MOT"]["sig"][0]), xytext=(0.75, 6.0),
                fontsize=7.8, color=MUTED,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0))
    ax.tick_params(labelsize=8.5)
    ax.set_xlim(-0.15, 6.0)
    ax.set_ylim(0, 54)
    _style(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "mot2cmp_stress.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  mot2cmp_stress.png")


# --------------------------------------------------------------------------- strain vs time
def fig_strain(B=None):
    B = B or C.build()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.60, 3.35),
                                 gridspec_kw={"width_ratios": [1.35, 1]})

    for k in _order(B):
        r = B["recs"][k]
        a1.plot(r["t"], r["e"], "-", color=COL[k], lw=LW[k], label="%s  (%.1f Hz)"
                % (_name(B, k), r["hz"]), alpha=1.0 if k != "S33" else 0.75)
    # res["rate"] is mm/s straight out of analyze(); x60 is mm/min, the units MOT reports in.
    _ours_mm_min = B["recs"][B["primary"]]["res"]["rate"] * 60.0
    a1.set_xlabel("time from first motion (s)", fontsize=9)
    a1.set_ylabel("strain (%)", fontsize=9)
    a1.set_title("(a) the DIC strain records — %.1f vs %.0f mm/min, a %.1f× difference"
                 % (_ours_mm_min, B["recs"]["MOT"]["res"]["speed_mm_min"],
                    _ours_mm_min / B["recs"]["MOT"]["res"]["speed_mm_min"]),
                 fontsize=9.5, color=INK)
    a1.legend(fontsize=8, loc="upper left", frameon=False)
    a1.tick_params(labelsize=8.5)
    a1.annotate("they take %.0f s to reach the same\nstrain we reach in %.0f s"
                % (B["recs"]["MOT"]["t"].max(), B["recs"][B["primary"]]["t"].max()),
                xy=(B["recs"]["MOT"]["t"].max() * 0.99, 5.15), xytext=(84, 0.45),
                fontsize=7.9, color=MUTED,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0))
    _style(a1)

    # (b) THE QUESTION TEST 1 HAD TO LEAVE OPEN.
    #
    # Test 1 could only say "MOT reads strain faster than us, and that is what a stiffer frame
    # looks like — but we cannot prove it without their load or crosshead channel." Session 2 has
    # the load channel, so the share can be put on the page instead of hypothesised.
    ks = _order(B)
    ys = np.arange(len(ks))[::-1]
    for y, k in zip(ys, ks):
        s = B["share"][k]
        a2.barh(y, s["pct"], height=0.55, color=COL[k], alpha=0.9)
        a2.text(s["pct"] + 1.2, y, "%.1f %%" % s["pct"], va="center", fontsize=9.5,
                fontweight="bold", color=COL[k])
        a2.text(1.5, y + 0.34, "%s  —  %s" % (_name(B, k), s["src"]), fontsize=7.4, color=MUTED)
    a2.set_yticks(ys); a2.set_yticklabels([])
    a2.set_xlim(0, 62)
    a2.set_ylim(-0.6, len(ks) - 0.35)
    a2.set_xlabel("share of crosshead travel that reaches the gauge (%)", fontsize=9)
    a2.set_title("(b) their frame IS stiffer — Test 1's open question, closed",
                 fontsize=9.5, color=INK)
    a2.tick_params(labelsize=8.5)
    _style(a2)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "mot2cmp_strain.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  mot2cmp_strain.png")


# --------------------------------------------------------------------------- the elastic slope
def _tangent(e_pct, sig, span=0.12):
    """Local dσ/dε in GPa, from a least-squares fit over a sliding STRAIN span.

    Slope against strain rather than the curves themselves, because on a stress-strain plot the
    three records lie on top of one another over the whole elastic region — the differences that
    decide E are a few per cent of slope and are invisible there. Differentiating is what makes
    them visible, and it is also what shows WHY the two methods disagree: the curve is not
    straight, so where you fit changes what you get.
    """
    out = np.full(len(e_pct), np.nan)
    for i in range(len(e_pct)):
        m = (e_pct >= e_pct[i] - span / 2) & (e_pct <= e_pct[i] + span / 2)
        if m.sum() >= 12:
            out[i] = np.polyfit(e_pct[m] / 100.0, sig[m], 1)[0] / 1000.0
    return out


def fig_elastic(B=None):
    """(a) the slope itself, against strain. (b) what each method makes of it.

    The point of the pair: the METHOD moves the answer further than the MACHINE does. Our two
    moduli differ by 12 % on the same record; the two machines differ by 4-6 %.
    """
    B = B or C.build()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.60, 3.45),
                                 gridspec_kw={"width_ratios": [1.25, 1]})
    win = B["fix_win"]

    a1.axvspan(win[0], win[1], color="#F0C808", alpha=0.22, lw=0, zorder=0)
    a1.text(np.mean(win), 4.02, "fixed window", ha="center", fontsize=7.6, color="#8a6d00")

    for k in _order(B):
        r, l = B["recs"][k], B["L"][k]
        m = (r["e"] <= 1.05) & (r["e"] >= 0)
        e, tg = r["e"][m], _tangent(r["e"][m], r["sig"][m])
        a1.plot(e, tg, "-", color=COL[k], lw=LW[k], alpha=1.0 if k != "S33" else 0.7,
                label=_name(B, k))
        s = l["E_steep"]
        a1.plot([s["lo"], s["hi"]], [s["E"], s["E"]], "-", color=COL[k], lw=3.4, alpha=0.45,
                solid_capstyle="butt")

    a1.set_xlabel("strain (%)", fontsize=9)
    a1.set_ylabel("local slope dσ/dε (GPa)", fontsize=9)
    a1.set_title("(a) the slope itself — flat means straight", fontsize=9.5, color=INK)
    a1.legend(fontsize=8, loc="lower right", frameon=False)
    a1.set_xlim(-0.02, 1.05)
    a1.set_ylim(2.0, 4.2)
    a1.tick_params(labelsize=8.5)
    a1.annotate("the XT-205 holds one slope from the origin.\nOurs DIPS to 2.7 GPa near 0.15 % and "
                "only\nreaches its steepest at ~0.45 % — that swing\nIS the 12 % between our two "
                "methods",
                xy=(0.155, 2.76), xytext=(0.40, 3.80), fontsize=7.8, color=INK,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0))
    _style(a1)

    # (b) the same six numbers as a dumbbell, so the method spread reads at a glance
    ks = _order(B)
    ys = np.arange(len(ks))[::-1]
    for y, k in zip(ys, ks):
        f, s = B["L"][k]["E_fix"]["E"], B["L"][k]["E_steep"]["E"]
        a2.plot([f, s], [y, y], "-", color=COL[k], lw=2.4, alpha=0.55, zorder=2)
        a2.plot([f], [y], "o", ms=9, color="white", mec=COL[k], mew=2.4, zorder=5)
        a2.plot([s], [y], "o", ms=9, color=COL[k], mec="white", mew=1.4, zorder=5)
        a2.text(min(f, s) - 0.062, y, "%.3f" % min(f, s), ha="right", va="center", fontsize=8.2,
                color=COL[k])
        a2.text(max(f, s) + 0.062, y, "%.3f" % max(f, s), ha="left", va="center", fontsize=8.2,
                color=COL[k], fontweight="bold")
        a2.text(3.34, y + 0.30, "%s   —  methods %.1f %% apart"
                % (_name(B, k), abs(s - f) / min(f, s) * 100), fontsize=7.5, color=MUTED,
                ha="center")
    a2.plot([], [], "o", ms=8, color="white", mec="#555", mew=2.0, label="fixed %.2f–%.2f %%" % win)
    a2.plot([], [], "o", ms=8, color="#555", label="steepest straight run")
    a2.legend(fontsize=7.6, loc="lower center", frameon=False, ncol=2)
    a2.set_yticks(ys); a2.set_yticklabels([])
    a2.set_xlim(2.72, 3.68)
    a2.set_ylim(-0.85, len(ks) - 0.30)
    a2.set_xlabel("E (GPa)", fontsize=9)
    a2.set_title("(b) the method moves it more than the machine", fontsize=9.5, color=INK)
    a2.tick_params(labelsize=8.5)
    _style(a2)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "mot2cmp_elastic.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  mot2cmp_elastic.png")


# --------------------------------------------------------------------------- noise
def fig_noise(B=None):
    """Left: what the scatter actually looks like. Right: the prediction that could have failed."""
    B = B or C.build()
    G = C.gauge_scaling()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.60, 3.45),
                                 gridspec_kw={"width_ratios": [1.15, 1]})

    for k in _order(B):
        r = B["recs"][k]
        w = C.NOISE_WIN
        m = (r["e"] >= w[0]) & (r["e"] <= w[1])
        tt, ee = r["t"][m], r["e"][m] / 100.0
        sl, ic = np.polyfit(tt, ee, 1)
        res = (ee - (sl * tt + ic)) * 1e6
        a1.plot(tt - tt.min(), res, "-", color=COL[k], lw=1.15,
                alpha=1.0 if k != "S33" else 0.55,
                label="%s   %.0f µε rms" % (_name(B, k), B["noise_s"][k]["rms"]))
    a1.axhline(0, color=MUTED, lw=0.9)
    a1.set_xlabel("time inside the %.2f–%.2f %% window (s)" % C.NOISE_WIN, fontsize=9)
    a1.set_ylabel("residual about the straight fit (µε)", fontsize=9)
    a1.set_title("(a) what the scatter looks like", fontsize=9.5, color=INK)
    a1.legend(fontsize=8, loc="upper right", frameon=False)
    a1.tick_params(labelsize=8.5)
    _style(a1)

    # (b) our floor against 1/Px0 — a line with no free parameters, anchored on the 80 mm pair
    xs = np.array([1.0 / G["px80"], 1.0 / G["px45"]]) * 1e4
    # S25/S26 share a pixel span to within 1 px, and so do S33/S34, so the markers sit on top of
    # each other; the labels are pushed apart by hand rather than left overlapping.
    for k, dy in (("S25", 9), ("S26", -12), ("S33", -12), ("S34", 9)):
        r = G["runs"][k]
        a2.plot([1e4 / r["px0"]], [r["noise"]["rms"]], "o", ms=9, alpha=0.8,
                color="#1F6FB4" if r["gauge"] < 60 else "#2E7D32", mec="white", mew=1.3, zorder=5)
        a2.annotate("%s  %.0f µε" % (k, r["noise"]["rms"]),
                    xy=(1e4 / r["px0"], r["noise"]["rms"]), xytext=(-4 if k in ("S33", "S34") else 8, dy),
                    textcoords="offset points", fontsize=7.9, color=INK,
                    ha="right" if k in ("S33", "S34") else "left")
    a2.plot(xs, [G["n80"], G["n80"] * G["predicted"]], "-", color="#444444", lw=2.0, zorder=2)
    a2.annotate("noise ∝ 1/Px₀,\nanchored on the 80 mm pair", xy=(xs.mean(), G["n80"] * 1.38),
                xytext=(xs[0] + 0.35, 46), fontsize=8.1, color="#444444",
                arrowprops=dict(arrowstyle="->", color="#444444", lw=1.0))
    a2.text(0.5, 0.055,
            "predicted %.3f×   measured %.3f×   —  %.1f %% apart"
            % (G["predicted"], G["measured"],
               abs(G["measured"] - G["predicted"]) / G["predicted"] * 100),
            transform=a2.transAxes, ha="center", fontsize=8.6, fontweight="bold", color="#1B5E20",
            bbox=dict(boxstyle="round,pad=0.34", fc="#E8F5E9", ec="#A5D6A7", lw=0.9))
    a2.set_xlabel("10⁴ / Px₀   (1676 px at 80 mm, 939 px at 45 mm)", fontsize=9)
    a2.set_ylabel("noise floor (µε rms)", fontsize=9)
    a2.set_title("(b) our floor is set by the PIXEL SPAN", fontsize=9.5, color=INK)
    a2.tick_params(labelsize=8.5)
    a2.set_ylim(0, 56)
    _style(a2)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "mot2cmp_noise.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  mot2cmp_noise.png")


def all_figs():
    print("MOT Test 2 comparison figures:")
    B = C.build()
    fig_stress(B)
    fig_strain(B)
    fig_elastic(B)
    fig_noise(B)
    return B


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    all_figs()
