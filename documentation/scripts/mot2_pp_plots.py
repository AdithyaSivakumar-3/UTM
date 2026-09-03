"""Figures for MOT Test 2's video through the PPD-UTM DIC pipeline.

Separate plots, deliberately, so each record can be read on its own terms before the overlay:

  mot2pp_strain_pp.png    full strain record — PPD-UTM DIC on XT-205 footage
  mot2pp_strain_mot.png   full strain record — the XT-205's own extensometer
  mot2pp_slope_pp.png     elastic slope — PPD-UTM DIC
  mot2pp_slope_mot.png    elastic slope — XT-205
  mot2pp_agree.png        the two against each other, and the difference
  mot2pp_stress.png       stress-strain from both strains against the one shared load
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

import mot2_pp as PP                                                  # noqa: E402
import mot2_compare as CMP                                            # noqa: E402

INK, GRID, MUTED = "#212529", "#DDDDDD", "#666666"
# PPD-UTM keeps the blue it wears through this block; the XT-205 keeps its red.
C_PP, C_MOT, C_S34 = "#1F6FB4", "#d62728", "#7FAF3F"
GOOD, BAD = "#2e7d32", "#c0392b"


def _style(ax):
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def _tangent(e_pct, sig, span=0.12):
    out = np.full(len(e_pct), np.nan)
    for i in range(len(e_pct)):
        m = (e_pct >= e_pct[i] - span / 2) & (e_pct <= e_pct[i] + span / 2)
        if m.sum() >= 12:
            out[i] = np.polyfit(e_pct[m] / 100.0, sig[m], 1)[0] / 1000.0
    return out


# --------------------------------------------------------------------------- full strain records
def _strain_panel(t, e, colour, who, extra, fname, note=None):
    fig, ax = plt.subplots(figsize=(6.15, 3.35))
    ax.plot(t, e, "-", color=colour, lw=1.7)
    i = int(np.argmax(e))
    ax.plot([t[i]], [e[i]], "o", ms=8, color=GOOD, zorder=5)
    ax.annotate("peak  %.3f %%" % e[i], xy=(t[i], e[i]), xytext=(t[i] - 96, e[i] + 0.42),
                fontsize=8.6, color=GOOD, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=GOOD, lw=1.2))
    ax.set_xlabel("time on the acquisition clock (s)  —  the .daq clock, not the AVI's", fontsize=9)
    ax.set_ylabel("strain (%)  —  on each record's own zero-load zero", fontsize=9)
    ax.set_title(who, fontsize=10, color=INK)
    ax.text(0.035, 0.955, extra, transform=ax.transAxes, fontsize=8.1, va="top",
            family="DejaVu Sans Mono",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#CCCCCC", lw=0.8))
    if note:
        ax.annotate(note[0], xy=note[1], xytext=note[2], fontsize=8.0, color=BAD,
                    fontweight="bold", arrowprops=dict(arrowstyle="->", color=BAD, lw=1.1))
    ax.tick_params(labelsize=8.5)
    ax.set_xlim(0, max(t) * 1.02)
    ax.set_ylim(-0.25, 6.0)
    _style(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, fname), dpi=200, facecolor="white")
    plt.close(fig)
    print("  " + fname)


def fig_strain_pp(S=None):
    S = S or PP.build()
    D = S["D"]
    _strain_panel(
        D["t"], D["e"], C_PP,
        "PPD-UTM DIC on the XT-205's footage — full record",
        "Px₀     %.1f px\nframes  %d, %.0f %% tracked\nto fracture %d"
        % (D["px0"], D["n_frames"], 100.0 * D["tracked"] / D["n"], D["n"]),
        "mot2pp_strain_pp.png",
        note=("%d trailing frames dropped:\nthe tracker follows the tear,\nnot the specimen"
              % D["tear_dropped"],
              (D["t"][-1], D["e"][-1]), (D["t"][-1] - 120, 3.40)))


def fig_strain_mot(S=None):
    S = S or PP.build()
    D = S["D"]
    _strain_panel(
        D["t_mot"], D["e_mot"], C_MOT,
        "The XT-205's own extensometer on the SAME footage — full record",
        "gauge   %.4f mm\nrows    %d of %d frames\n(the rest read \"Invalid\")"
        % (D["gauge_true"], len(D["t_mot"]), D["n_frames"]),
        "mot2pp_strain_mot.png",
        note=("their record keeps the recoil;\nthe peak is read before it",
              (D["t_mot"][-1], D["e_mot"][-1]), (D["t_mot"][-1] - 78, 1.55)))


# --------------------------------------------------------------------------- slopes, separately
def _slope_panel(e, sig, colour, who, L, fname):
    fig, ax = plt.subplots(figsize=(6.15, 3.35))
    m = (e <= 1.05) & (e >= 0)
    ax.plot(e[m], _tangent(e[m], sig[m]), "-", color=colour, lw=1.8)

    w = CMP.FIX_WIN
    ax.axvspan(w[0], w[1], color="#F0C808", alpha=0.22, lw=0, zorder=0)
    ax.text(np.mean(w), 4.06, "fixed window", ha="center", fontsize=7.6, color="#8a6d00")

    st = L["E_steep"]
    ax.plot([st["lo"], st["hi"]], [st["E"], st["E"]], "-", color=colour, lw=4.0, alpha=0.45,
            solid_capstyle="butt")
    ax.axhline(L["E_fix"]["E"], color=INK, ls=":", lw=1.4)
    # The two moduli are within 1 % of each other on this record, so their labels have to be pushed
    # apart deliberately — one above the pair of lines, one below.
    ax.text(1.03, L["E_fix"]["E"] - 0.06, "fixed window  %.3f" % L["E_fix"]["E"], fontsize=8.0,
            ha="right", va="top", color=INK)
    ax.text(st["hi"] + 0.03, st["E"] + 0.30, "steepest run  %.3f\n(%.2f–%.2f %%)"
            % (st["E"], st["lo"], st["hi"]), fontsize=8.0, va="center", color=colour,
            fontweight="bold")

    ax.set_xlabel("strain (%)", fontsize=9)
    ax.set_ylabel("local slope dσ/dε (GPa)", fontsize=9)
    ax.set_title(who, fontsize=10, color=INK)
    ax.tick_params(labelsize=8.5)
    ax.set_xlim(-0.02, 1.05)
    ax.set_ylim(2.0, 4.25)
    _style(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, fname), dpi=200, facecolor="white")
    plt.close(fig)
    print("  " + fname)


def fig_slope_pp(S=None):
    S = S or PP.build()
    _slope_panel(S["ours"]["e"], S["ours"]["sig"], C_PP,
                 "Elastic slope — PPD-UTM DIC on XT-205 footage", S["L"]["PP"],
                 "mot2pp_slope_pp.png")


def fig_slope_mot(S=None):
    S = S or PP.build()
    _slope_panel(S["mot"]["e"], S["mot"]["sig"], C_MOT,
                 "Elastic slope — the XT-205's own extensometer", S["L"]["MOT"],
                 "mot2pp_slope_mot.png")


# --------------------------------------------------------------------------- agreement
def fig_agree(S=None):
    S = S or PP.build()
    D = S["D"]
    x = D["pair_e_theirs"][D["pair_live"]]
    y = D["pair_e_ours"][D["pair_live"]]

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.60, 3.45),
                                 gridspec_kw={"width_ratios": [1, 1.2]})

    a1.plot([0, 5.6], [0, 5.6], "-", color="#BBBBBB", lw=1.6, zorder=1)
    a1.plot(x, y, ".", ms=2.2, color=C_PP, alpha=0.55, zorder=3)
    a1.set_xlabel("XT-205 extensometer, strain (%)", fontsize=9)
    a1.set_ylabel("PPD-UTM DIC, strain (%)", fontsize=9)
    a1.set_title("(a) %d matched instants on one video" % D["live_n"], fontsize=9.5, color=INK)
    a1.text(0.05, 0.95,
            "ours = %.6f × theirs\n           %+.1f µε\nR² = %.7f"
            % (D["scale"], D["offset_ue"], D["fit_r2"]),
            transform=a1.transAxes, fontsize=8.4, va="top", family="DejaVu Sans Mono",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#CCCCCC", lw=0.8))
    a1.set_xlim(-0.2, 5.7); a1.set_ylim(-0.2, 5.7)
    a1.tick_params(labelsize=8.5)
    _style(a1)

    d = (y - x) * 1e4
    a2.plot(x, d, ".", ms=2.2, color=C_PP, alpha=0.5)
    a2.axhline(0, color="#BBBBBB", lw=1.4)
    a2.axhline(D["offset_ue"], color=INK, ls="--", lw=1.6)
    a2.annotate("the constant part: %.1f µε,\nwhich is %.3f px on a %.0f px span"
                % (D["offset_ue"], D["offset_px"], D["px0"]),
                xy=(0.55, D["offset_ue"]), xytext=(0.30, 76), fontsize=8.2, color=INK,
                fontweight="bold", arrowprops=dict(arrowstyle="->", color=INK, lw=1.0))
    a2.annotate("the slow drift across the record is the\nremaining %.3f %% of scale — %d µε over 5 %%"
                % (abs(D["scale_pct"]), abs(D["scale_pct"]) / 100 * 5 * 1e4),
                xy=(5.05, np.median(d[x > 4.6])), xytext=(1.15, -232), fontsize=8.0, color=MUTED,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0))
    a2.set_xlabel("their extensometer, strain (%)", fontsize=9)
    a2.set_ylabel("PPD-UTM − XT-205 (µε)", fontsize=9)
    a2.set_title("(b) the difference, and what it is made of", fontsize=9.5, color=INK)
    a2.set_xlim(-0.2, 5.7)
    a2.set_ylim(-260, 130)
    a2.tick_params(labelsize=8.5)
    _style(a2)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "mot2pp_agree.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  mot2pp_agree.png")


# --------------------------------------------------------------------------- stress-strain
def fig_stress(S=None):
    S = S or PP.build()
    fig, ax = plt.subplots(figsize=(6.30, 3.55))

    ax.plot(S["s34"]["e"], S["s34"]["sig"], "-", color=C_S34, lw=1.5, alpha=0.85,
            label="%s · PPD-UTM" % S["primary"])
    ax.plot(S["mot"]["e"], S["mot"]["sig"], "-", color=C_MOT, lw=2.0,
            label="XT-205 · own extensometer")
    ax.plot(S["ours"]["e"], S["ours"]["sig"], "--", color=C_PP, lw=1.9,
            label="XT-205 footage · PPD-UTM DIC")

    for k, col in (("MOT", C_MOT), ("PP", C_PP)):
        l = S["L"][k]
        ax.plot([l["uts_e"]], [l["uts"]], "o", ms=7, color=col, mec="white", mew=1.2, zorder=6)
        ax.plot([l["ef"]], [l["sigf"]], "s", ms=6.5, color=col, mec="white", mew=1.2, zorder=6)

    lp, lm = S["L"]["PP"], S["L"]["MOT"]
    ax.annotate("the two red/blue curves are ONE specimen\nread two ways — they lie on each other",
                xy=(2.55, np.interp(2.55, S["mot"]["e"], S["mot"]["sig"])), xytext=(1.02, 16.0),
                fontsize=8.2, color=INK,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.1))
    ax.annotate("fracture  %.2f vs %.2f %%\n(%+.2f %%)"
                % (lp["ef"], lm["ef"], CMP.offset_pct(lp["ef"], lm["ef"])),
                xy=(lm["ef"], lm["sigf"]), xytext=(3.15, 30.0), fontsize=8.2, color=INK,
                fontweight="bold", arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.1))

    ax.set_xlabel("strain (%)  —  all three on the preload-frozen zero", fontsize=9)
    ax.set_ylabel("engineering stress (MPa)", fontsize=9)
    ax.set_title("One specimen read twice, with the PPD-UTM run beside it",
                 fontsize=10, color=INK)
    ax.legend(fontsize=8.2, loc="upper left", frameon=False)
    ax.tick_params(labelsize=8.5)
    ax.set_xlim(-0.15, 6.0)
    ax.set_ylim(0, 54)
    _style(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "mot2pp_stress.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  mot2pp_stress.png")


# --------------------------------------------------------------------------- strain rate, Test 2
#
# Deliberately the same two panels, colours and titles as MOT Test 1's figure
# (mot_postproc_compare.figure) so the two tests can be read against each other without the reader
# having to re-learn a layout. Only the records and the window change.
# Test 1's exact four colours, so the two figures can be laid side by side and read as one series
# of results: purple is always "PPD-UTM DIC on XT-205 footage", red is always the XT-205's own
# extensometer, and our own runs keep blue and orange.
C_RATE_PP, C_RATE_MOT, C_S33, C_S34 = "#7048e8", "#d62728", "#1f77b4", "#e8590c"
RATE_LO, RATE_HI = 0.05, 0.35            # % strain, on the preload-zeroed axis


def _rate_over(t, e, lo=RATE_LO, hi=RATE_HI):
    t, e = np.asarray(t, float), np.asarray(e, float)
    m = (e >= lo) & (e <= hi)
    if m.sum() < 10:
        return None
    sl = float(np.polyfit(t[m], e[m] / 100.0, 1)[0])
    return sl, float(np.corrcoef(t[m], e[m])[0, 1] ** 2), int(m.sum())


def fig_rate(S=None):
    """MOT Test 2's version of Test 1's strain-rate figure.

    The window is 0.05-0.35 % of the PRELOAD-ZEROED strain rather than of the raw strain. Test 1's
    records began at a seated specimen so the two are the same thing there; Test 2's preload lands
    inside the recording, and a raw window would sit on the seating ramp — the same fault that made
    the noise figure read 57 ue instead of 24.
    """
    S = S or PP.build()
    B = S["B"]
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.9),
                             gridspec_kw={"width_ratios": [1.0, 1.12], "wspace": 0.20})

    ax = axes[0]
    ax.plot(S["mot"]["t"], S["mot"]["e"], "-", color=C_RATE_MOT, lw=2.4, alpha=0.85,
            label="XT-205 extensometer")
    ax.plot(S["ours"]["t"], S["ours"]["e"], "--", color=C_RATE_PP, lw=1.5,
            label="PPD-UTM DIC")
    ax.axhspan(RATE_LO, RATE_HI, color="#1f77b4", alpha=0.10)
    ax.set_xlim(-1, 40)
    ax.set_ylim(-0.05, 0.90)
    ax.set_xlabel("time from the preload (s)")
    ax.set_ylabel("strain (%)")
    ax.set_title("The XT-205's own footage, measured two ways\n(shaded: the fitted window)",
                 fontsize=10.5, color=INK)
    ax.legend(fontsize=8.4, loc="upper left", framealpha=0.95)
    _style(ax)

    rows = [("XT-205 footage · PPD-UTM DIC",
             _rate_over(S["ours"]["t"], S["ours"]["e"]), C_RATE_PP),
            ("XT-205 footage · XT-205 extensometer",
             _rate_over(S["mot"]["t"], S["mot"]["e"]), C_RATE_MOT),
            ("S33 · PPD-UTM", _rate_over(B["recs"]["S33"]["t"], B["recs"]["S33"]["e"]), C_S33),
            ("S34 · PPD-UTM", _rate_over(B["recs"]["S34"]["t"], B["recs"]["S34"]["e"]), C_S34)]
    rows = [r for r in rows if r[1]]

    ax = axes[1]
    from matplotlib.transforms import blended_transform_factory
    y = np.arange(len(rows))[::-1]
    vals = [r[1][0] for r in rows]
    b = ax.barh(y, [v * 1e4 for v in vals], color=[r[2] for r in rows], height=0.40)
    tr = blended_transform_factory(ax.transAxes, ax.transData)
    for rr, v, (nm, _s, _c) in zip(b, vals, rows):
        yc = rr.get_y() + rr.get_height() / 2
        ax.text(0.012, yc + 0.30, nm, transform=tr, va="bottom", ha="left",
                fontsize=8.2, color=INK)
        ax.text(v * 1e4 + 0.04, yc, "%.2e /s" % v, va="center", fontsize=8.2,
                color=INK, fontweight="bold")
    ax.set_yticks([])
    ax.set_ylim(-0.62, len(rows) - 0.32)
    ax.set_xlim(0, max(vals) * 1e4 * 1.34)
    ax.set_xlabel("d(ε)/dt over %.2f–%.2f %%  (×10⁻⁴ /s)" % (RATE_LO, RATE_HI))
    ax.set_title("Strain rate on one shared window", fontsize=10.5, color=INK)
    _style(ax)

    fig.subplots_adjust(left=0.062, right=0.995, top=0.86, bottom=0.145)
    fig.savefig(os.path.join(FIGS, "mot2pp_rate.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  mot2pp_rate.png")
    return rows


def all_figs():
    print("MOT Test 2 post-processing figures:")
    S = PP.build()
    fig_strain_pp(S)
    fig_strain_mot(S)
    fig_slope_pp(S)
    fig_slope_mot(S)
    fig_agree(S)
    fig_stress(S)
    fig_rate(S)
    return S


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    all_figs()
