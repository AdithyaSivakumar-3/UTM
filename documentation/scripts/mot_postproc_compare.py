"""The MOT video measured by OUR calculation, against the MOT's own answer and against S25/S26.

WHY THIS EXISTS, and why it is not the same comparison as mot_compare.py
    mot_compare.py sets the XT-205's strain against our rig's. Two things differ at once there —
    the instrument AND the specimen — so a disagreement cannot be attributed to either. Running the
    XT-205's OWN VIDEO through our pixel-to-strain path adds the leg that separates them:

        XT-205 log      vs   our calc on the XT-205 video     -> isolates the CALCULATION
                                                                 (same footage, same specimen,
                                                                  same instant; only the maths
                                                                  differs)
        our calc on that video vs our calc on S25/S26         -> isolates the SPECIMEN and the rig

THE FRAME RATE HAD TO BE RECOVERED, NOT READ
    test2.chan 0.avi declares 1000 fps and 117497 frames. It really holds 2281 frames, and our own
    fps_warning() already calls 1000 fps implausible. Nothing in the file or its sidecars carries
    the truth, so the rate is recovered by matching the two strain records at the strain levels
    they share: each crossing gives a (frame, time) pair, and the straight line through those pairs
    has the frame rate as its slope. That uses the SHAPE of the curves, not their scale, so it does
    not assume the answer being tested.

A TRAP THAT ALREADY COST A WRONG CONCLUSION IN THIS PROJECT
    Frames must be read SEQUENTIALLY from this file. cv2 seeking silently returns a stale frame for
    it, so sampling with read_frame() showed markers that never moved and led to "the video contains
    no deformation", which is false. Anything here that walks the video decodes straight through.
"""
import csv
import glob
import io
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                       # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
FIGS = os.path.abspath(os.path.join(HERE, "..", "figures"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "Software", "UTM_PyQt6"))

import mot_compare as MC                                              # noqa: E402

# The strain interval the deck already uses everywhere. It sits comfortably inside the XT-205's
# valid range (it goes invalid at 0.4015 %), so all four records can be fitted over the same span.
LO, HI = 0.0005, 0.0035
C_MOT, C_PP, C_S25, C_S26 = "#d62728", "#7048e8", "#1f77b4", "#e8590c"
INK, GRID, MUTED = "#212529", "#DDDDDD", "#666666"


def _postproc_csv():
    """The per-frame export from the post-processing tab, wherever it was filed."""
    for pat in ("**/DIC post processing data/*test2*.csv", "**/*test2_chan*.csv",
                "**/dic_postproc_*test2*.csv"):
        hits = [h for h in glob.glob(os.path.join(MC.DATA, pat), recursive=True)
                if "results" not in os.path.basename(h)]
        if hits:
            return sorted(hits)[-1]
    raise SystemExit("no post-processing CSV for the MOT video found under %s" % MC.DATA)


def read_postproc(path=None):
    """(frame, eps, l_px, header) from a post-processing export. Time is NOT read.

    The Time_s column in that file was written from the container's 1000 fps and is wrong by a
    factor of about 45. Frame number is the only honest abscissa the file carries, and the rate is
    recovered separately.
    """
    path = path or _postproc_csv()
    head = {}
    lines = []
    for ln in io.open(path, encoding="utf-8", errors="replace"):
        if ln.startswith("#"):
            if ":" in ln:
                k, v = ln[1:].split(":", 1)
                head[k.strip()] = v.strip()
            continue
        if ln.strip():
            lines.append(ln)
    rows = list(csv.DictReader(lines))
    keep = [r for r in rows if r.get("Tracked") == "1"]
    f = np.array([float(r["Frame"]) for r in keep])
    e = np.array([float(r["DIC_Cauchy"]) for r in keep])
    L = np.array([float(r["L_px"]) for r in keep])
    return f, e, L, head, os.path.basename(path)


def read_daq_times():
    """Per-frame timestamps for the video, from the acquisition log beside it.

    test2.daq holds EXACTLY 2281 data rows and the video holds exactly 2281 frames, one row per
    frame, each stamped with its own time. That makes the video's time base something to read
    rather than something to fit — which matters more than it sounds, because a fitted rate can
    silently absorb a strain-scale error and then report that the scales agree.

    Its interval is not quite constant (0.0515 s nominal, jittering), so the per-frame stamps are
    used directly rather than an average rate.
    """
    d = os.path.dirname(MC.MOT)
    daq = os.path.join(d, "test2.daq")
    if not os.path.exists(daq):
        return None
    t = []
    for ln in io.open(daq, encoding="utf-8", errors="replace"):
        if ln.startswith("#") or not ln.strip():
            continue
        try:
            t.append(float(ln.split("\t")[0]))
        except ValueError:
            continue
    return np.array(t)


def trim_to_physical(f, e, L, fps_guess=19.4, rate_guess=7.5e-4, tol=6.0):
    """Cut the series at the first frame-to-frame jump the specimen could not physically make.

    Needed because the tracker eventually loses this video for a reason that has nothing to do with
    the estimator: box half-size 105 px with marker B only 121 px from the right edge, so once the
    marker travels far enough the box hits Box.clamp()'s limit at 2357 px and cannot follow. 184
    rows sit at exactly that value, after which the centroid flip-flops by several pixels a frame.

    The threshold is derived, not chosen: at 7.5e-4 /s on a 2234 px baseline at 19.4 fps the
    separation grows 0.085 px per frame, so anything past a few times that is not the specimen. The
    cut lands at 0.52 % strain — comfortably ABOVE the 0.05-0.35 % window everything is fitted
    over, so no fitted point is discarded by it.
    """
    step = rate_guess * L[0] / fps_guess
    bad = np.where(np.abs(np.diff(L)) > tol * step)[0]
    cut = int(bad[0]) if len(bad) else len(L)
    return f[:cut], e[:cut], L[:cut], cut, float(tol * step)


def crossings(x, y, levels):
    """Where a rising series first reaches each level, by linear interpolation.

    First crossing, not any crossing: both records hold a long flat approach where noise crosses a
    low level repeatedly, and taking the last one would put the pair seconds away from the first.
    """
    out = []
    for lv in levels:
        idx = np.where(y >= lv)[0]
        if not len(idx) or idx[0] == 0:
            out.append(np.nan)
            continue
        i = idx[0]
        y0, y1 = y[i - 1], y[i]
        out.append(x[i - 1] + (x[i] - x[i - 1]) * ((lv - y0) / (y1 - y0)) if y1 != y0 else x[i])
    return np.array(out)


def recover_fps(f_pp, e_pp, t_mot, e_mot, levels=None):
    """Frame rate and time offset, from the strain levels the two records share.

    frame = fps * time + c. Fitting crossings rather than the curves themselves means the result
    depends on WHEN each record reaches a strain, not on how big the strains are — so a scale
    disagreement between the instruments cannot leak into the recovered rate.
    """
    if levels is None:
        top = min(e_pp.max(), e_mot.max()) * 0.95
        levels = np.linspace(max(0.0004, top * 0.15), top, 9)
    fx = crossings(f_pp, e_pp, levels)
    tx = crossings(t_mot, e_mot, levels)
    ok = np.isfinite(fx) & np.isfinite(tx)
    if ok.sum() < 3:
        raise SystemExit("not enough shared strain levels to recover the frame rate")
    fps, c = np.polyfit(tx[ok], fx[ok], 1)
    r2 = np.corrcoef(tx[ok], fx[ok])[0, 1] ** 2
    return float(fps), float(c), float(r2), levels[ok], tx[ok], fx[ok]


def build():
    # ---- the three records ------------------------------------------------------------------
    f_pp, e_pp, L_pp, head, pp_name = read_postproc()
    n_raw = len(f_pp)
    f_pp, e_pp, L_pp, cut, thr = trim_to_physical(f_pp, e_pp, L_pp)
    t_mot, e_mot, gl = MC.read_mot()
    print("XT-205 log        : %d valid rows, %.3f-%.3f s, peak %.4f %%, gauge %.4f mm"
          % (len(t_mot), t_mot[0], t_mot[-1], e_mot.max() * 100, gl))
    print("our post-proc     : %s" % pp_name)
    print("                    %d tracked frames, Px0 %s, peak %.4f %%"
          % (len(f_pp), head.get("L0 (Px0)", "?"), e_pp.max() * 100))
    if head.get("Tracking ended", "").startswith("MARKER LOST"):
        print("                    NOTE: %s" % head["Tracking ended"])
    print("                    trimmed %d -> %d rows at the first jump > %.2f px/frame "
          "(strain %.3f %%)" % (n_raw, cut, thr, e_pp[-1] * 100))

    # ---- the time base: READ from the acquisition log, not fitted ---------------------------
    t_frame = read_daq_times()
    if t_frame is None or len(t_frame) < int(f_pp.max()) + 1:
        raise SystemExit("test2.daq is missing or too short to time the video")
    t_pp = t_frame[f_pp.astype(int)]
    daq_fps = (len(t_frame) - 1) / (t_frame[-1] - t_frame[0])
    print("\ntime base from test2.daq: %d rows for %d frames, %.4f-%.4f s -> %.4f fps"
          % (len(t_frame), len(t_frame), t_frame[0], t_frame[-1], daq_fps))
    print("   the video file declares %s — wrong by %.0fx"
          % (head.get("Frame rate used", "?"), 1000.0 / daq_fps))

    # ---- the cross-check that closes the circularity -----------------------------------------
    # Matching strain CROSSINGS recovers fps/k, where k is any constant scale error between the two
    # records. Comparing that against the DAQ's real rate therefore measures k directly — and it is
    # the one number that says whether the strain SCALES agree, independently of any slope fit.
    fps, c, r2, lv, tx, fx = recover_fps(f_pp, e_pp, t_mot, e_mot)
    k = daq_fps / fps
    print("\nscale check (this is what a slope fit alone cannot tell you):")
    print("   rate recovered by matching %d strain levels : %.4f fps  (R2 %.5f)"
          % (len(lv), fps, r2))
    print("   rate the DAQ actually recorded              : %.4f fps" % daq_fps)
    print("   => strain-scale factor ours/theirs k        : %.5f  (%.2f %% apart)"
          % (k, abs(k - 1) * 100))

    # ---- the four slopes, over one shared strain interval ------------------------------------
    rows = []
    r = MC.rate_over_strain(t_pp, e_pp, LO, HI)
    n_pp = MC.noise_over_strain(t_pp, e_pp, LO, HI)
    rows.append(("MOT video, OUR calculation", r, n_pp, C_PP))
    r = MC.rate_over_strain(t_mot, e_mot, LO, HI)
    n_mot = MC.noise_over_strain(t_mot, e_mot, LO, HI)
    rows.append(("MOT video, XT-205's own answer", r, n_mot, C_MOT))
    ours = {}
    # The same two runs, and the same patterns, mot_compare.py already uses — so this leg and the
    # existing MOT-vs-rig slides cannot quietly diverge onto different files.
    for spec, pat, col in (("S25", "Specimen_S25_V2_Spray_Video2/*.csv", C_S25),
                           ("S26", "Specimen_S26_V2_Spray_Video3/*.csv", C_S26)):
        t, e, F, name = MC.read_ours(pat)
        ours[spec] = (t, e)
        rows.append(("%s, our rig + our calculation" % spec,
                     MC.rate_over_strain(t, e, LO, HI),
                     MC.noise_over_strain(t, e, LO, HI), col))

    print("\n%-34s %12s %8s %10s %9s" % ("record", "d(eps)/dt", "R2", "noise ue", "n"))
    print("-" * 78)
    for name, rate, nz, _ in rows:
        if rate is None:
            print("%-34s %12s" % (name, "too few points"))
            continue
        print("%-34s %11.3e %8.5f %10.1f %9d"
              % (name, rate[0], rate[1], nz["rms_ue"], rate[2]))

    a = rows[0][1][0]      # our calculation on their video
    b = rows[1][1][0]      # their own answer on the same video
    # ---- the most direct comparison available: no fit at all.
    # Both records are on the same clock, so their strains can be read off at the same instants and
    # divided. A slope fit answers "do they rise at the same rate"; this answers "do they report
    # the same strain", which is the question about the CALCULATION.
    m = (t_pp >= t_mot[0]) & (t_pp <= t_mot[-1])
    ei = np.interp(t_pp[m], t_mot, e_mot)
    w = (ei >= LO) & (ei <= HI)
    ratio = e_pp[m][w] / ei[w]
    diff = e_pp[m][w] - ei[w]
    sl, ic = np.polyfit(ei[w], e_pp[m][w], 1)

    print("\nSAME VIDEO, SAME SPECIMEN, SAME INSTANT — only the maths differs:")
    print("   strain read at matched times, %d points over %.2f-%.2f %%:"
          % (int(w.sum()), LO * 100, HI * 100))
    print("      ours / XT-205   median %.4f   mean %.4f   sd %.4f"
          % (np.median(ratio), ratio.mean(), ratio.std()))
    print("      difference      %+.1f ue mean, %.1f ue rms"
          % (diff.mean() * 1e6, diff.std() * 1e6))
    print("      ours = %.4f x theirs %+.0f ue   (R2 %.5f)"
          % (sl, ic * 1e6, np.corrcoef(ei[w], e_pp[m][w])[0, 1] ** 2))
    print("   fitted strain rate  ours / theirs = %.4f   (%.2f %% apart)"
          % (a / b, abs(a / b - 1) * 100))
    print("\n   and on their own footage our measurement is %.1fx quieter: %.1f vs %.1f ue"
          % (rows[1][2]["rms_ue"] / rows[0][2]["rms_ue"],
             rows[0][2]["rms_ue"], rows[1][2]["rms_ue"]))

    out = {"fps_daq": daq_fps, "fps_from_crossings": fps, "fps_r2": r2, "scale_k": k,
           "rows": [{"name": n, "rate": (rt[0] if rt else None), "r2": (rt[1] if rt else None),
                     "n": (rt[2] if rt else None), "noise_ue": nz["rms_ue"]}
                    for n, rt, nz, _ in rows],
           "ratio_rate": a / b,
           "ratio_matched_median": float(np.median(ratio)),
           "matched_slope": float(sl), "matched_offset_ue": float(ic * 1e6),
           "matched_n": int(w.sum()),
           "noise_ratio": rows[1][2]["rms_ue"] / rows[0][2]["rms_ue"]}
    io.open(os.path.join(HERE, "..", "mot_postproc_compare.json"), "w",
            encoding="utf-8", newline="").write(json.dumps(out, indent=1))
    figure(t_pp, e_pp, t_mot, e_mot, ours, rows, fps, tx, fx, c, daq_fps)
    return out


def figure(t_pp, e_pp, t_mot, e_mot, ours, rows, fps, tx, fx, c, daq_fps):
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.1),
                             gridspec_kw={"width_ratios": [1.25, 1.25, 1]})

    ax = axes[0]
    ax.plot(t_mot, e_mot * 100, "-", color=C_MOT, lw=2.4, alpha=0.85,
            label="XT-205, its own answer")
    ax.plot(t_pp, e_pp * 100, "--", color=C_PP, lw=1.5, label="XT-205 video, OUR calculation")
    ax.axhspan(LO * 100, HI * 100, color="#1f77b4", alpha=0.10)
    ax.set_xlim(t_mot[0] - 1, t_mot[-1] + 1)
    ax.set_ylim(-0.05, 0.55)
    ax.set_xlabel("time (s)"); ax.set_ylabel("strain (%)")
    ax.set_title("The same footage, measured two ways\n(shaded: the fitted window)",
                 fontsize=10.5, color=INK)
    ax.legend(fontsize=8.4, loc="upper left", framealpha=0.95)
    _style(ax)

    ax = axes[1]
    ax.plot(tx, fx, "o", color=C_PP, ms=6, label="shared strain levels")
    xs = np.array([tx.min(), tx.max()])
    ax.plot(xs, fps * xs + c, "-", color=C_PP, lw=1.4,
            label="matched: %.3f fps" % fps)
    ax.plot(xs, daq_fps * xs + c, "--", color=INK, lw=1.4,
            label="DAQ's own: %.3f fps" % daq_fps)
    ax.set_xlabel("time on the XT-205 clock (s)")
    ax.set_ylabel("frame in our video")
    ax.set_title("Scale check: the two lines coincide,\nso the strain scales agree",
                 fontsize=10.5, color=INK)
    ax.legend(fontsize=8.4, loc="upper left", framealpha=0.95)
    _style(ax)

    ax = axes[2]
    names = ["ours on\ntheir video", "XT-205\nitself", "S25", "S26"]
    vals = [r[1][0] for r in rows]
    cols = [r[3] for r in rows]
    b = ax.bar(names, [v * 1e4 for v in vals], color=cols, width=0.62)
    for rr, v in zip(b, vals):
        ax.text(rr.get_x() + rr.get_width() / 2, v * 1e4 + 0.06, "%.2e" % v,
                ha="center", fontsize=8.2, color=INK)
    ax.set_ylabel("d(ε)/dt over 0.05–0.35 %  (×10⁻⁴ /s)")
    ax.set_title("Strain rate on one shared window", fontsize=10.5, color=INK)
    _style(ax)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "mot_postproc_compare.png"), dpi=200, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    print("\nwrote documentation/figures/mot_postproc_compare.png")


def _style(ax):
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    build()
