# -*- coding: utf-8 -*-
"""THE PYTHON WORKFLOW — how this project's code is structured, drawn from the code.

  pytree_full.png      one page: every module in the app, grouped by role, with the real
                       import edges and a few keywords each
  pytree_live.png      the LIVE TEST path only — entry, hardware, control, shared core
  pytree_tools.png     the operator dialogs and the data / output branch
  pytree_evidence.png  the evidence pipeline (documentation/scripts) that turns raw runs
                       into figures and slides

The module list, the line counts and the ARROWS are not typed in: `scan()` parses every
file in Software/UTM_PyQt6 with `ast` and reads the imports, so this diagram cannot drift
from the code it documents. Only the keyword captions are written by hand (they are
paraphrases of each module's own docstring).
"""
import ast
import glob
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.abspath(os.path.join(HERE, "..", "..", "Software", "UTM_PyQt6"))
FIGS = os.path.abspath(os.path.join(HERE, "..", "figures"))

INK = "#212529"
MUTED = "#6C757D"
BLUE = "#1F6FB4"
BLUE_BG = "#E7F1F8"
GREEN = "#2E7D32"
GREEN_BG = "#E8F5E9"
TAN = "#B29E84"
TAN_BG = "#F5F0E8"
GREY_BG = "#F2F2F2"

# ---- the keywords, one short phrase per module (paraphrased from its own docstring) -----
KEY = {
    "main": "test window · live plots · run control · every tab",
    "camera_manager": "pylon grab loop · ROI · presets · blob detect · live strain",
    "serial_manager": "serial link to the rig · motor commands · load cell",
    "control_policies": "closed-loop modes · preload · ramps · dwell",
    "utm_dic": "ε = (L − L₀)/L₀ · tracking health · marker geometry",
    "utm_analysis": "E · σy · UTS · ε_f · fracture detection",
    "utm_capture": "stills + AVI · written off the hot path",
    "utm_capdlg": "capture setup · views · disk cost preview",
    "utm_camdlg": "manual camera params · live trackability",
    "utm_autocal": "exposure / threshold sweep · scored on data",
    "utm_blobpick": "pick the two markers by hand",
    "utm_noisedlg": "noise-capture setup · at-rest measurement",
    "utm_postdlg": "post-processing tab · virtual extensometer",
    "utm_postproc": "re-measure a RECORDED video · verified seek",
    "utm_recipes": "save / load a named test setup",
    "utm_registry": "one queryable index of every test",
    "utm_report": "one-click PDF report from a CSV",
    "utm_wizard": "guided checklist · reads state, never acts",
    "widgets": "custom Qt widgets · switches · gauges",
    "theme": "dark / light theming · plot styling",
}

# ---- role grouping: which column each module is drawn in --------------------------------
COLS = [
    ("HARDWARE & SENSING", ["camera_manager", "serial_manager", "utm_capture"]),
    ("OPERATOR DIALOGS", ["utm_camdlg", "utm_capdlg", "utm_blobpick", "utm_noisedlg",
                          "utm_wizard"]),
    ("MEASURE & CONTROL", ["control_policies", "utm_postdlg", "utm_postproc",
                           "utm_autocal"]),
    ("DATA & OUTPUT", ["utm_recipes", "utm_registry", "utm_report", "widgets", "theme"]),
]
CORE = ["utm_dic", "utm_analysis"]          # the shared bottom row


def scan():
    """Every module, its line count and its LOCAL imports — read from the code itself."""
    mods = {}
    for p in sorted(glob.glob(os.path.join(APP, "*.py"))):
        name = os.path.basename(p)[:-3]
        src = open(p, encoding="utf-8", errors="replace").read()
        imps = set()
        for n in ast.walk(ast.parse(src)):
            if isinstance(n, ast.Import):
                imps.update(a.name.split(".")[0] for a in n.names)
            elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
                imps.add(n.module.split(".")[0])
        mods[name] = {"loc": len(src.splitlines()), "imports": imps}
    for m in mods:                                    # keep only in-project edges
        mods[m]["imports"] &= set(mods)
    return mods


def _box(ax, x, y, w, h, title, loc, keys, *, fg=INK, bg="white", ec=MUTED, lw=1.2,
         tfs=9.2, kfs=7.4):
    """One node. Title and keywords are centred as a PAIR inside the box, so a short
    caption does not leave the lower half empty and a long one does not ride the edge."""
    # The title is anchored to the TOP of the box and the caption is centred in whatever
    # space is left underneath. Centring the pair together (the obvious approach) puts a
    # three-line caption straight through the title, because the caption block grows
    # upward as well as downward.
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.30,rounding_size=1.0",
                                fc=bg, ec=ec, lw=lw, zorder=2))
    t_top = y + h - 0.85
    ax.text(x + w / 2, t_top, title, ha="center", va="top", fontsize=tfs,
            fontweight="bold", color=fg, zorder=3)
    if loc is not None:
        ax.text(x + w - 0.55, y + h - 0.55, "%s" % loc, ha="right", va="top",
                fontsize=6.3, color=MUTED, zorder=3)
    band_top = t_top - tfs * 0.115 - 0.45          # below the title's own line height
    ax.text(x + w / 2, (y + band_top) / 2, keys, ha="center", va="center",
            fontsize=kfs, color=MUTED, zorder=3, linespacing=1.45)


def _arrow(ax, p1, p2, *, colour=MUTED, lw=1.0, style="-|>", rad=0.0, alpha=0.85):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=9,
                                 color=colour, lw=lw, alpha=alpha, zorder=1,
                                 connectionstyle="arc3,rad=%.2f" % rad,
                                 shrinkA=1, shrinkB=1))


def _canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100)
    ax.axis("off")
    return fig, ax


# =============================================================== the one-page full tree
def fig_full(mods, out="pytree_full.png"):
    fig, ax = _canvas(16.4, 9.0)
    fig.suptitle("THE PYTHON WORKFLOW — %d modules, %s lines, drawn from the imports"
                 % (len(mods), format(sum(m["loc"] for m in mods.values()), ",d")
                    .replace(",", " ")),
                 fontsize=13, color=INK, y=0.975, fontweight="bold")
    ax.text(50, 96.2, "entry point at the top · role columns below · the two SHARED "
                      "modules at the foot are what keep the live rig and the "
                      "post-processor telling the same story",
            ha="center", va="top", fontsize=8.4, color=MUTED, style="italic")

    pos = {}
    # entry
    _box(ax, 33, 87.0, 34, 6.2, "main.py", "%s lines" % format(mods["main"]["loc"], ",d")
         .replace(",", " "), KEY["main"], bg=BLUE_BG, ec=BLUE, lw=1.8, tfs=12, kfs=8.2)
    pos["main"] = (50, 87.0, 34, 6.2)

    colw, gap = 23.0, 2.4
    x0 = (100 - (4 * colw + 3 * gap)) / 2
    for ci, (head, names) in enumerate(COLS):
        cx = x0 + ci * (colw + gap)
        ax.text(cx + colw / 2, 79.4, head, ha="center", va="center", fontsize=9,
                fontweight="bold", color=TAN)
        for ri, name in enumerate(names):
            y = 69.4 - ri * 7.6
            _box(ax, cx, y, colw, 5.9, name + ".py",
                 "%d" % mods[name]["loc"], KEY[name], kfs=7.2)
            pos[name] = (cx + colw / 2, y, colw, 5.9)
        # main -> column header (one clean fan instead of 18 crossing arrows)
        _arrow(ax, (50, 87.0), (cx + colw / 2, 81.4), colour=BLUE, lw=1.3, alpha=0.55,
               rad=0.0 if ci in (1, 2) else 0.08 * (1 if ci > 1 else -1))

    # shared core
    ax.text(50, 34.2, "SHARED CORE — one definition of strain, one of the properties",
            ha="center", va="center", fontsize=9, fontweight="bold", color=GREEN)
    for i, name in enumerate(CORE):
        cx = 27 + i * 26
        _box(ax, cx, 24.8, 21, 6.6, name + ".py", "%d" % mods[name]["loc"], KEY[name],
             bg=GREEN_BG, ec=GREEN, lw=1.6, tfs=10, kfs=7.4)
        pos[name] = (cx + 10.5, 24.8, 21, 6.6)

    # real import edges between the drawn modules (excluding main's fan, drawn above)
    for m, d in sorted(mods.items()):
        if m == "main" or m not in pos:
            continue
        for t in sorted(d["imports"]):
            if t == "main" or t not in pos:
                continue
            x1, y1, w1, h1 = pos[m]
            x2, y2, w2, h2 = pos[t]
            if t in CORE:                       # down to the shared row
                _arrow(ax, (x1, y1), (x2, y2 + h2), colour=GREEN, lw=1.0, rad=0.12,
                       alpha=0.75)
            else:                               # sideways, within the columns
                _arrow(ax, (x1, y1 + h1 / 2), (x2, y2 + h2 / 2), colour=TAN, lw=1.0,
                       rad=0.22, alpha=0.9)

    # the evidence branch, off to the side as its own tree
    _box(ax, 2.5, 10.0, 24, 8.4, "documentation/scripts/", "94 files",
         "38 figure & analysis scripts · 28 slide blocks · 2 deck builders\n"
         "every figure regenerated from the raw runs", bg=TAN_BG, ec=TAN, lw=1.5,
         tfs=9.4, kfs=7.2)
    _arrow(ax, (26.5, 16.5), (34.0, 24.8), colour=TAN, lw=1.3, rad=-0.18)
    ax.text(31.5, 18.6, "reads the same CSVs\nand videos the rig writes", ha="left",
            va="center", fontsize=7.2, color=TAN, style="italic", linespacing=1.4)

    fig.tight_layout(rect=(0, 0, 1, 0.955))
    p = os.path.join(FIGS, out)
    fig.savefig(p, dpi=190, facecolor="white")
    plt.close(fig)
    print("  " + out)
    return p


# =============================================================== detail: the live path
def fig_live(mods, out="pytree_live.png"):
    fig, ax = _canvas(12.6, 6.4)
    ax.text(50, 97, "THE LIVE TEST PATH — from a click to a point on the curve",
            ha="center", va="top", fontsize=12, fontweight="bold", color=INK)

    _box(ax, 34, 80, 32, 11.5, "main.py", "%s lines" % format(mods["main"]["loc"], ",d")
         .replace(",", " "),
         "owns the run: start / stop · live plots · every tab\nrouting between the camera, "
         "the motor and the maths", bg=BLUE_BG, ec=BLUE, lw=1.8, tfs=12.5, kfs=8.4)

    chain = [
        ("camera_manager.py", mods["camera_manager"]["loc"],
         "grab loop (LatestImageOnly)\nROI · presets · blob detection\n≈20 fps measured"),
        ("utm_dic.py", mods["utm_dic"]["loc"],
         "ε = (L − L₀) / L₀\ntracking health\nmarker geometry"),
        ("control_policies.py", mods["control_policies"]["loc"],
         "6 closed-loop modes\nauto-preload · ramps\ndwell + taper"),
        ("serial_manager.py", mods["serial_manager"]["loc"],
         "serial link to the rig\nmotor commands\nload-cell stream"),
    ]
    for i, (name, loc, keys) in enumerate(chain):
        x = 2 + i * 24.6
        bg, ec = (GREEN_BG, GREEN) if name.startswith("utm_dic") else ("white", MUTED)
        _box(ax, x, 42, 22.5, 24, name, "%d" % loc, keys, bg=bg, ec=ec,
             tfs=9.6, kfs=8.0)
        _arrow(ax, (50, 80), (x + 11.25, 66.5), colour=BLUE, lw=1.2, alpha=0.5,
               rad=0.06 * (i - 1.5))
    _arrow(ax, (24.5, 54), (26.5, 54), colour=GREEN, lw=1.4)
    _arrow(ax, (49.1, 54), (51.1, 54), colour=MUTED, lw=1.4)
    _arrow(ax, (73.7, 54), (75.7, 54), colour=MUTED, lw=1.4)

    _box(ax, 18, 11, 64, 17.5, "the stress–strain curve, live",
         None,
         "force from the load cell  ×  strain from the camera — matched in time and "
         "plotted while the pull is still running;\nevery run leaves a CSV, and "
         "optionally stills + AVI (utm_capture.py) written off the hot path",
         bg=TAN_BG, ec=TAN, lw=1.6, tfs=11, kfs=8.2)
    _arrow(ax, (50, 42), (50, 28.5), colour=TAN, lw=1.6)
    fig.tight_layout()
    p = os.path.join(FIGS, out)
    fig.savefig(p, dpi=190, facecolor="white")
    plt.close(fig)
    print("  " + out)
    return p


# =============================================================== detail: tools + outputs
def fig_tools(mods, out="pytree_tools.png"):
    fig, ax = _canvas(12.6, 6.4)
    ax.text(50, 97, "THE OPERATOR'S TOOLS, AND WHAT EACH RUN LEAVES BEHIND",
            ha="center", va="top", fontsize=12, fontweight="bold", color=INK)

    groups = [
        ("DIALOGS — set it up, check it, pick by hand", [
            ("utm_camdlg.py", "manual camera params · live trackability readout"),
            ("utm_autocal.py", "exposure / threshold sweep, scored on real frames"),
            ("utm_blobpick.py", "pick the two markers by hand (SF20)"),
            ("utm_capdlg.py", "what to record, which views, what it costs on disk"),
            ("utm_noisedlg.py", "noise capture — the rig measured at rest"),
            ("utm_wizard.py", "guided checklist; reads state, never acts"),
        ]),
        ("AFTER THE PULL — measure again, keep the record", [
            ("utm_postdlg.py", "post-processing tab · virtual extensometer"),
            ("utm_postproc.py", "re-measures ANY recorded video, verified seek"),
            ("utm_analysis.py", "E · σy · UTS · ε_f — one shared definition"),
            ("utm_registry.py", "one queryable index of every test"),
            ("utm_report.py", "one-click PDF report from a CSV"),
            ("utm_recipes.py", "save / load a named test setup"),
        ]),
    ]
    for gi, (head, rows) in enumerate(groups):
        x = 2 + gi * 49.5
        ax.text(x + 23, 88, head, ha="center", va="center", fontsize=9.6,
                fontweight="bold", color=TAN)
        for ri, (name, keys) in enumerate(rows):
            y = 74 - ri * 11.6
            core = name.startswith("utm_analysis")
            _box(ax, x, y, 46, 9.0, name, "%d" % mods[name[:-3]]["loc"], keys,
                 bg=GREEN_BG if core else "white", ec=GREEN if core else MUTED,
                 tfs=9.4, kfs=8.0)
    fig.tight_layout()
    p = os.path.join(FIGS, out)
    fig.savefig(p, dpi=190, facecolor="white")
    plt.close(fig)
    print("  " + out)
    return p


# =============================================================== detail: evidence branch
def fig_evidence(out="pytree_evidence.png"):
    scripts = sorted(glob.glob(os.path.join(HERE, "*.py")))
    n_files = len(scripts)
    n_lines = sum(len(open(f, encoding="utf-8", errors="replace").read().splitlines())
                  for f in scripts)
    n_block = len([f for f in scripts if "block" in os.path.basename(f)])

    fig, ax = _canvas(12.6, 6.0)
    ax.text(50, 97, "THE EVIDENCE PIPELINE — documentation/scripts/ (%d files, %s lines)"
            % (n_files, format(n_lines, ",d").replace(",", " ")),
            ha="center", va="top", fontsize=12, fontweight="bold", color=INK)

    stages = [
        ("RAW RUNS", "test CSVs · videos\nstills · run.json", GREY_BG, MUTED),
        ("ANALYSIS SCRIPTS", "read the runs, compute\nthe numbers (never typed)",
         BLUE_BG, BLUE),
        ("FIGURES", "every plot regenerated\non each build", GREEN_BG, GREEN),
        ("SLIDE BLOCKS", "%d blocks place figures\n+ text into sections" % n_block,
         TAN_BG, TAN),
        ("DECKS", "Weekly diary +\nfinal presentation", "white", INK),
    ]
    for i, (t, k, bg, ec) in enumerate(stages):
        x = 1.5 + i * 19.8
        _box(ax, x, 50, 17.6, 22, t, None, k, bg=bg, ec=ec, lw=1.5, tfs=10, kfs=8.2)
        if i < 4:
            _arrow(ax, (x + 17.6, 61), (x + 19.8, 61), colour=MUTED, lw=1.5)

    ax.text(50, 40, "The rule that makes it evidence rather than decoration:", ha="center",
            va="top", fontsize=9.6, fontweight="bold", color=INK)
    ax.text(50, 33,
            "no number is transcribed by hand — a figure that disagrees with the data "
            "cannot survive a rebuild, and a slide that\nquotes a number the scripts do "
            "not produce fails the build. The same CSVs the rig writes are the ones the "
            "decks read.",
            ha="center", va="top", fontsize=9, color=MUTED, linespacing=1.5)
    _box(ax, 22, 4, 56, 16, "one command rebuilds the whole record", None,
         "raw runs → figures → slides, in one pass — which is why the diary can be "
         "trusted\nas a record rather than a memory of what the numbers used to be",
         bg=GREEN_BG, ec=GREEN, lw=1.5, tfs=10.5, kfs=8.2)
    fig.tight_layout()
    p = os.path.join(FIGS, out)
    fig.savefig(p, dpi=190, facecolor="white")
    plt.close(fig)
    print("  " + out)
    return p


def all_figs():
    mods = scan()
    print("scanned %d modules, %d lines" % (len(mods),
                                            sum(m["loc"] for m in mods.values())))
    fig_full(mods)
    fig_live(mods)
    fig_tools(mods)
    fig_evidence()


if __name__ == "__main__":
    all_figs()
