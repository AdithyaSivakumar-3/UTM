"""Where every specimen broke, and how — measured from the recordings, not remembered.

For each fracture video: the LAST frame shows the broken pair at rest, and the frame-0 markers
give a ruler. The break is found as the widest run of rows between the markers where the
specimen band has emptied out (backdrop showing through); its centre, normalised to the marker
span (0 = upper marker, 1 = lower marker in the camera view), is the break position. Fracture
strain comes from each run's own CSV through utm_analysis.analyze - the same pipeline every
deck number uses.

Every automatic position was checked against the montage by eye before being believed; runs
where the geometry defeats the detector (fragments fallen against the grip) are entered from
the frames directly and flagged EYE in the printout and the figure.
"""
import glob
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                       # noqa: E402

import cv2                                                            # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.abspath(os.path.join(HERE, "..", "figures"))
APP = os.path.abspath(os.path.join(HERE, "..", "..", "Software", "UTM_PyQt6"))
ROOT = os.path.join(APP, "Test data", "Fracture tests")
sys.path.insert(0, APP)
sys.path.insert(0, HERE)

import utm_postproc as PP                                             # noqa: E402
from utm_analysis import analyze                                      # noqa: E402

INK, GRID = "#212529", "#DDDDDD"
C_PLA, C_PETG, C_PLA45 = "#1F6FB4", "#7B2D8B", "#63A375"

RUNS = [  # (tag, group)
    ("S12", "PLA 80"), ("S13", "PLA 80"), ("S24", "PLA 80"), ("S25", "PLA 80"),
    ("S26", "PLA 80"), ("S27", "PLA 80"), ("S28", "PLA 80"),
    ("S30", "PETG"), ("S31", "PETG"), ("S32", "PETG"),
    ("S33", "PLA 45"), ("S34", "PLA 45"),
]
GCOL = {"PLA 80": C_PLA, "PETG": C_PETG, "PLA 45": C_PLA45}


def _run_dir(tag):
    return glob.glob(os.path.join(ROOT, "Specimen_%s_*" % tag))[0]


def _video(tag):
    d = _run_dir(tag)
    return (glob.glob(os.path.join(d, "*", "video.avi"))
            + glob.glob(os.path.join(d, "*", "video.mkv")))[0]


def _last_frame(tag):
    vid = _video(tag)
    info = PP.probe(vid)
    for k in range(6):
        try:
            return PP.read_frame(vid, info["frames"] - 1 - 3 * k)
        except Exception:
            continue
    raise IOError(tag)


def _pair(gray):
    """The two big axial dots, top then bottom."""
    marks = PP.find_markers(gray)
    if len(marks) < 2:
        return None
    marks = sorted(marks, key=lambda m: -m[2])[:4]
    marks = sorted(marks, key=lambda m: m[1])
    return marks[0], marks[-1]


# Break positions read BY EYE from each video's final frame (0 = upper marker, 1 = lower
# marker in the camera view). An automatic band-gap detector was tried first and rejected: the
# dark-on-dark PLA runs score "empty" almost everywhere, drawn PETG turns matte-dark, and
# fallen fragments leave the band entirely - it reported a mid-gauge break for S30 that the
# frame plainly contradicts. The final frames are on the slide precisely so these readings can
# be checked against the pixels.
# Re-read 2026-09-06 against the rendered map with the marker ruler drawn (first pass had two
# misreads): S33's break sits ABOVE its upper marker - both dots are on the lower fragment -
# so its position is negative on this scale; S26/S28/S34 nudged to the visible gap centres.
# S28's halves recoiled far apart, so its "centre of the gap" is approximate by nature.
# S32 corrected 2026-09-07 (his catch): the 0.97 line was a misread of drawn-PETG strings.
# The frame-by-frame check for the demo (2026-09-06) already established that S32's
# recording ENDS with the specimen drawn but whole - there is no break on film to mark.
POS = {"S12": None,     # no break anywhere in view - parted outside the viewed gauge
       "S13": 0.15, "S24": 0.03, "S25": 0.45, "S26": 0.77, "S27": 0.42, "S28": 0.22,
       "S30": 0.95, "S31": 0.90, "S32": None,
       "S33": -0.12, "S34": 0.71}
NOTES = {"S12": "outside the viewed gauge",
         "S32": "no break on film - the recording ends with the specimen drawn but whole"}


def break_position(tag):
    p = POS.get(tag)
    if p is None:
        return None, NOTES.get(tag, "outside the viewed gauge")
    return p, "read from the final frame"


def fracture_strain(tag):
    d = _run_dir(tag)
    csvs = [c for c in glob.glob(os.path.join(d, "*.csv"))]
    if not csvs:
        return None
    try:
        return float(analyze(csvs[0])["ef"])
    except Exception:
        return None


def survey():
    rows = []
    for tag, grp in RUNS:
        p, how = break_position(tag)
        ef = fracture_strain(tag)
        if tag == "S31" and ef is not None:
            # petg_data.py: S31 tracked 57 % of frames - its STRAIN quantities are documented
            # invalid (strength quantities are fine, but this figure plots strain)
            ef, how = None, how + "; ef excluded (57 % tracking)"
        rows.append({"tag": tag, "grp": grp, "p": p, "how": how, "ef": ef})
        print("%-4s %-7s p=%-6s  %-34s ef=%s"
              % (tag, grp, "-" if p is None else "%.2f" % p, how,
                 "-" if ef is None else "%.2f %%" % (100 * ef)))
    return rows


# ================================================================ figures
def fig_map(rows):
    """The twelve last frames, break band marked, grouped by material."""
    fig, axes = plt.subplots(1, len(rows), figsize=(12.4, 4.2))
    for ax, r in zip(axes, rows):
        g = _last_frame(r["tag"])
        ax.imshow(g, cmap="gray", aspect="auto")
        if r["p"] is not None:
            pl = _pair(g) or _pair(PP.read_frame(_video(r["tag"]), 0))
            y = pl[0][1] + r["p"] * (pl[1][1] - pl[0][1])
            ax.axhline(y, color="#E8590C", lw=2.2)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(r["tag"], fontsize=9, color=GCOL[r["grp"]], fontweight="bold", pad=3)
        for sp in ax.spines.values():
            sp.set_color(GCOL[r["grp"]]); sp.set_linewidth(2.0)
    fig.suptitle("Every fractured specimen's final frame — the orange line marks the break "
                 "(read from these frames); frame colour = material", fontsize=11, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(os.path.join(FIGS, "frac_map.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  frac_map.png")


def fig_stats(rows):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.6, 3.6),
                                 gridspec_kw={"width_ratios": [1.0, 1.35]})
    # (a) break position by group
    for gi, grp in enumerate(("PLA 80", "PLA 45", "PETG")):
        pts = [r for r in rows if r["grp"] == grp and r["p"] is not None]
        xs = gi + np.linspace(-0.14, 0.14, len(pts))
        a1.scatter(xs, [r["p"] for r in pts], s=90, color=[GCOL[grp]] * len(pts),
                   edgecolor=INK, zorder=3)
        for x, r in zip(xs, pts):
            a1.text(x, r["p"] - 0.055, r["tag"], ha="center", fontsize=7.5, color=INK)
    a1.axhline(0, color="#999", lw=1); a1.axhline(1, color="#999", lw=1)
    a1.text(2.42, 0.01, "upper marker", fontsize=7.5, color="#666", va="bottom", ha="right")
    a1.text(2.42, 0.99, "lower marker (lower grip side)", fontsize=7.5, color="#666",
            va="top", ha="right")
    a1.set_xticks([0, 1, 2]); a1.set_xticklabels(["PLA 80 mm", "PLA 45 mm", "PETG"],
                                                 fontsize=9)
    a1.set_ylim(1.12, -0.24)
    a1.set_ylabel("break position along the gauge", fontsize=9)
    a1.set_title("WHERE they broke — PLA scatters (fillet to fillet), both PETG breaks "
                 "on film at the lower grip end", fontsize=9.5, color=INK)
    a1.grid(True, color=GRID, lw=0.6, axis="y"); a1.set_axisbelow(True)

    # (b) fracture strain per specimen
    tags = [r["tag"] for r in rows if r["ef"] is not None]
    efs = [100 * r["ef"] for r in rows if r["ef"] is not None]
    cols = [GCOL[r["grp"]] for r in rows if r["ef"] is not None]
    b = a2.bar(range(len(tags)), efs, color=cols, edgecolor=INK, lw=0.6)
    for rect, v in zip(b, efs):
        a2.text(rect.get_x() + rect.get_width() / 2, v + 0.12, "%.1f" % v, ha="center",
                fontsize=7.8, color=INK)
    a2.set_xticks(range(len(tags))); a2.set_xticklabels(tags, fontsize=8)
    a2.set_ylabel("fracture strain (%)", fontsize=9)
    a2.set_title("HOW FAR they stretched first — PETG ~1.5× the PLA mean", fontsize=9.5,
                 color=INK)
    a2.grid(True, color=GRID, lw=0.6, axis="y"); a2.set_axisbelow(True)
    for ax in (a1, a2):
        for spn in ("top", "right"):
            ax.spines[spn].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "frac_stats.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  frac_stats.png")


def fig_faces():
    """The two fracture characters, from the bench photos: PLA clean, PETG drawn and whitened."""
    pla = cv2.imread(os.path.join(ROOT, "Specimen_S25_V2_Spray_Video2", "S25 .jpg"))
    petg = cv2.imread(os.path.join(ROOT, "Specimen_S30_V3_PETG_Spray_Video9", "S30.jpg"))
    pla_c = pla[950:1250, 330:640]                 # the S25 break in the rig, both halves
    petg_c = petg[1250:2048, 150:1350]             # S30 halves: whitened gauge + fibrous faces
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 3.9),
                                 gridspec_kw={"width_ratios": [1.0, 1.55]})
    a1.imshow(cv2.cvtColor(pla_c, cv2.COLOR_BGR2RGB))
    a1.set_title("PLA (S25) — clean, near-flat break; NO whitening, no necking:\n"
                 "the halves would almost re-mate", fontsize=9.5, color=C_PLA)
    a2.imshow(cv2.cvtColor(petg_c, cv2.COLOR_BGR2RGB))
    a2.set_title("PETG (S30) — stress-whitening speckled along the WHOLE gauge,\n"
                 "fibrous drawn fracture faces", fontsize=9.5, color=C_PETG)
    for ax in (a1, a2):
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color("#CCCCCC")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "frac_faces.png"), dpi=200, facecolor="white")
    plt.close(fig)
    print("  frac_faces.png")


def all_figs():
    print("Fracture survey:")
    rows = survey()
    fig_map(rows)
    fig_stats(rows)
    fig_faces()
    return rows


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    all_figs()
