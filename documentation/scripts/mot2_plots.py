"""Figures for MOT session 2 — the XT-205's own 45 mm gauge pull.

  mot2_strain.png    strain against time, the instrument's raw output
  mot2_stress.png    engineering stress against that strain, with the landmarks

Both are drawn from mot2_data, which reads the extensometer CSV and the acquisition log and
identifies the load column by its shape. Nothing is retyped.
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

import mot2_data as M                                                 # noqa: E402

INK, GRID, MUTED = "#212529", "#DDDDDD", "#666666"
C_MOT, GOOD, BAD = "#d62728", "#2e7d32", "#c0392b"


def _style(ax):
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def fig_strain(D=None):
    """Strain against time, including the samples AFTER the break.

    The recoil is drawn rather than trimmed: when the specimen parts, the halves spring back and
    the markers go with them, so the instrument reports 5.33 % falling to 2.78 % in two samples.
    Showing it is the honest way to explain why the failure strain is read at the peak and not at
    the last sample.
    """
    D = D or M.load()
    t_e, e, _ = M._read_strain()

    fig, ax = plt.subplots(figsize=(6.15, 3.35))
    ax.plot(t_e, e, "-", color=C_MOT, lw=1.6)

    # The preload lands INSIDE the record, and that is the whole strain-zero question in one mark:
    # everything left of it is deformation their strain counts and ours does not.
    ax.axvspan(t_e[0], D["t_pre"], color="#F0C808", alpha=0.22, lw=0)
    ax.annotate("their zero is here, at 0 N.\n300 N is only reached at %.1f s,\nby which point they read %.3f %%"
                % (D["t_pre"], D["e_pre"]),
                xy=(D["t_pre"], 0.10), xytext=(16, 3.55), fontsize=8.2, color="#8a6d00",
                fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="#8a6d00", lw=1.2))

    ax.axvline(D["t_peak"], color=MUTED, ls=":", lw=1.2)
    ax.annotate("UTS  %.2f MPa\nat %.2f %%" % (D["uts"], D["uts_e"]),
                xy=(D["t_peak"], D["uts_e"]), xytext=(D["t_peak"] + 8, 1.05),
                fontsize=8.4, color=INK,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.1))

    ax.plot([D["t_ef"]], [D["ef"]], "o", ms=8, color=GOOD, zorder=5)
    ax.annotate("fracture  %.2f %%" % D["ef"], xy=(D["t_ef"], D["ef"]),
                xytext=(D["t_ef"] - 74, D["ef"] - 0.62), fontsize=8.6, color=GOOD,
                fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=GOOD, lw=1.2))

    ax.annotate("the halves recoil —\nnot deformation", xy=(t_e[-1], e[-1]),
                xytext=(t_e[-1] - 58, 2.05), fontsize=8.2, color=BAD, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=BAD, lw=1.2))

    ax.set_xlabel("time (s)", fontsize=9)
    ax.set_ylabel("extensometer strain (%)", fontsize=9)
    ax.set_title("XT-205 strain over the whole pull — %.0f mm gauge, %.0f mm/min"
                 % (D["gauge_mm"], D["speed_mm_min"]), fontsize=10, color=INK)
    ax.tick_params(labelsize=8.5)
    ax.set_xlim(0, t_e[-1] + 3)
    ax.set_ylim(-0.25, e.max() * 1.11)
    _style(ax)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "mot2_strain.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  mot2_strain.png")
    return D


def fig_stress(D=None):
    """Engineering stress against the extensometer's strain, with the three landmarks."""
    D = D or M.load()
    # Draw only as far as the strain peak. Past it the markers are riding on two halves that
    # have already parted, so the curve doubles back on itself — true of the record, but it is the
    # specimen coming apart, not a stress-strain path, and drawing it invites the wrong reading.
    k = int(np.argmax(D["e_on_f"])) + 1
    e, sig = D["e_on_f"][:k], D["sig"][:k]

    fig, ax = plt.subplots(figsize=(6.15, 3.35))
    ax.plot(e, sig, "-", color=C_MOT, lw=1.8)

    # the modulus fit, drawn over the window it was actually taken from
    w = D["E_window"]
    xs = np.linspace(w[0], w[1], 20)
    m = (e >= w[0]) & (e <= w[1])
    if m.sum() > 3:
        A = np.polyfit(e[m] / 100.0, sig[m], 1)
        ax.plot(xs, np.polyval(A, xs / 100.0), "-", color=INK, lw=2.4, alpha=0.85)
        ax.annotate("E = %.3f GPa\n(%.2f–%.2f %% window, R² %.4f)"
                    % (D["E"], w[0], w[1], D["E_R2"]),
                    xy=(w[1], np.polyval(A, w[1] / 100.0)), xytext=(2.55, 9.0),
                    fontsize=8.4, color=INK,
                    arrowprops=dict(arrowstyle="->", color=INK, lw=1.1))

    for x, y, lab, col, dx, dy in (
            (D["sy_e"], D["sy"], "σ_y  %.2f MPa" % D["sy"], "#e8a80c", 0.55, -7.5),
            (D["uts_e"], D["uts"], "UTS  %.2f MPa" % D["uts"], GOOD, 0.60, 4.2),
            (D["ef"], D["sigf"], "fracture  %.2f %%" % D["ef"], BAD, -1.60, 6.4)):
        ax.plot([x], [y], "o", ms=8, color=col, zorder=5)
        ax.annotate(lab, xy=(x, y), xytext=(x + dx, y + dy), fontsize=8.4,
                    color=col, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=col, lw=1.1))

    ax.set_xlabel("extensometer strain (%)", fontsize=9)
    ax.set_ylabel("engineering stress (MPa)", fontsize=9)
    ax.set_title("Stress–strain from the XT-205's own two channels\n"
                 "(load ÷ %.0f mm² nominal)" % D["area"], fontsize=10, color=INK)
    ax.tick_params(labelsize=8.5)
    ax.set_xlim(-0.15, D["ef"] + 0.9)
    ax.set_ylim(0, D["uts"] * 1.18)
    _style(ax)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "mot2_stress.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  mot2_stress.png")
    return D


def all_figs():
    print("MOT session 2 figures:")
    D = M.load()
    fig_strain(D)
    fig_stress(D)
    return D


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    all_figs()
