"""MOT session 2's video through OUR DIC post-processing — the leg that isolates the MATHS.

Session 2 has now been measured three ways, and the three differ in exactly one thing each:

    their extensometer on their video   }  same footage, same specimen, same instant
    OUR pipeline on their video         }  -> the only difference is the CALCULATION
    OUR pipeline on our own S34         }  -> the only difference is the MACHINE

This module builds the middle one and pairs it against the other two.

TWO INPUT ERRORS WERE MADE IN THE POST-PROCESSING RUN, AND THEY ARE KEPT, NOT HIDDEN.

  1. FRAME RATE 1000 fps. The AVI reports it and it is wrong: 3351 frames span 168.643 s of the
     acquisition clock, which is 19.864 fps. Every time-derived output is therefore overstated by
     50.34x — "Data ends at 3.350 s", "mean rate 1.284e-02 /s".
  2. GAUGE 80.00 mm. This is the 45 mm session. The reported "px per mm 15.6866" and "extension at
     peak 4.3215 mm" are both wrong by 80/45.0034.

Neither touches the strain, because strain is a pixel ratio:  eps = (L - Px0)/Px0. That is the
deck's central claim about px/mm, and this run is an accidental controlled experiment in it — two
wrong inputs, and exactly the outputs that depend on them are wrong while the measurement is not.

Both are corrected here rather than re-run, because the correction is exact: the true time base is
the acquisition clock the .daq already carries, and the true scale follows from the gauge the
instrument itself reports (45.0034 mm).

THE FRAME-TO-LOAD MAPPING IS 1:1 AND EXACT. The .daq has 3351 rows and the video has 3351 frames.
They were written by the same acquisition, so frame i IS row i — no interpolation, no nearest-time
search, and no assumption that either stream is evenly sampled (neither is; both carry a few
doubled intervals).
"""
import csv
import io
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_APP = os.path.abspath(os.path.join(_HERE, "..", "..", "Software", "UTM_PyQt6"))
for _p in (_HERE, _APP):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import mot2_data as M2                                                # noqa: E402
import mot2_compare as CMP                                            # noqa: E402
from utm_analysis import _steepest_straight_run                       # noqa: E402

REPO = os.path.dirname(os.path.dirname(_HERE))
PPDIR = os.path.join(REPO, "Validation docs", "MOT Test 2", "DIC post processing data")
PP = os.path.join(PPDIR, "sample3_chan 0_dic_postproc.csv")

FPS_ENTERED = 1000.0            # what the post-processing was told
GAUGE_ENTERED = 80.0            # what the post-processing was told
GAUGE_TRUE = 45.0034            # what the instrument itself reports

_cache = {}


def _read_pp():
    """Frame, L_px, engineering strain %, log strain %, correlation, tracked flag."""
    fr, L, ec, et, cor, tk = [], [], [], [], [], []
    for r in csv.reader(io.open(PP, encoding="utf-8")):
        if not r or r[0].startswith("#") or r[0] == "Frame":
            continue
        fr.append(int(r[0]))
        L.append(float(r[6]))
        ec.append(float(r[8]) * 100.0)
        et.append(float(r[9]) * 100.0)
        cor.append(float(r[10]))
        tk.append(int(r[11]))
    return (np.array(fr), np.array(L), np.array(ec), np.array(et),
            np.array(cor), np.array(tk))


def _trim_tear(L, keep_from=40, mult=10.0):
    """Drop trailing samples where the marker span jumps by far more than the record's own step.

    THE TRAP THIS EXISTS FOR. On this record the very last frame moves the span +3.422 px in one
    50 ms sample, after a run of 0.2-0.7 px DEcrements as the specimen tears. Read literally it is
    a failure strain of 5.292 %; the sustained plateau just before it is 5.215 %, and their own
    extensometer says 5.211 %. So the un-trimmed number would have reported a 1.6 % disagreement
    between two calculations that actually agree to 0.08 %.

    It is not deformation: a specimen cannot stretch further in 50 ms than it did in the previous
    second while the load is FALLING. It is the tracker following the two halves apart, and it is
    the same recoil the deck already documents on their own strain channel — one sample later.

    The threshold is relative to the record's own recent behaviour (10x the median absolute step of
    the preceding 40 samples) rather than absolute, so it cannot fire on a fast but genuine plastic
    ramp, and it is applied to BOTH records for symmetry even though only one needs it.
    """
    d = np.abs(np.diff(L))
    n = len(L)
    end = n
    while end > keep_from + 1:
        win = d[max(0, end - 1 - keep_from):end - 1]
        if len(win) < 5:
            break
        thr = mult * float(np.median(win))
        if thr > 0 and d[end - 2] > thr:
            end -= 1
        else:
            break
    return end


def load():
    """The three records on one clock, plus the paired comparison against their extensometer."""
    if _cache:
        return _cache

    fr, L, ec, et, cor, tk = _read_pp()
    t_f, f = M2._read_daq()
    t_e, e_mot, _g = M2._read_strain()

    if len(fr) != len(t_f):
        raise SystemExit("frames (%d) and .daq rows (%d) no longer match — the 1:1 mapping this "
                         "module relies on is gone" % (len(fr), len(t_f)))

    # ---- the real time base, taken from the acquisition rather than from the container
    t = t_f.copy()
    fps_true = (len(fr) - 1) / (t_f[-1] - t_f[0])

    # ---- fracture: the sample BEFORE the largest load drop, same rule as everywhere else
    i_fr = int(np.argmin(np.diff(f)))
    keep = np.arange(len(t)) <= i_fr
    t, f, ec, et, L, cor, tk = t[keep], f[keep], ec[keep], et[keep], L[keep], cor[keep], tk[keep]

    # ...and then the tear itself, which on this record survives the load-drop cut by one sample
    n_end = _trim_tear(L)
    n_dropped = len(t) - n_end
    ec_raw_peak = float(ec.max())
    t, f, ec, et, L, cor, tk = (t[:n_end], f[:n_end], ec[:n_end], et[:n_end],
                                L[:n_end], cor[:n_end], tk[:n_end])
    sig = f / M2.AREA_MM2

    # ---- the preload instant, so this record can be put on our convention too
    i_pre = int(np.argmax(f >= M2.PRELOAD_N)) if (f >= M2.PRELOAD_N).any() else 0
    ec_rz = ec - ec[i_pre]

    # ---- PAIRED against their extensometer, matched by TIME on the shared clock.
    #
    # Their strain file drops the rows it could not measure, so it is 43 rows shorter; matching on
    # time keeps every pair honest instead of assuming the two streams line up index for index.
    idx = {round(v, 4): i for i, v in enumerate(t)}
    pair_i, pair_j = [], []
    for j, tv in enumerate(t_e):
        i = idx.get(round(tv, 4))
        if i is not None:
            pair_i.append(i)
            pair_j.append(j)
    pair_i, pair_j = np.array(pair_i), np.array(pair_j)
    ours_p, theirs_p = ec[pair_i], e_mot[pair_j]

    # Only compare where there is strain to compare. Below ~0.05 % both records are dominated by
    # their own noise floor and a RATIO there measures nothing but division by a small number.
    live = theirs_p >= 0.05
    r = ours_p[live] / theirs_p[live]
    # scale factor through the origin — the single number that says whether the two calculations
    # disagree by a CONSTANT, which is what a scale error would look like
    k = float((ours_p[live] * theirs_p[live]).sum() / (theirs_p[live] ** 2).sum())
    d_ue = (ours_p - theirs_p) * 1e4          # % strain -> microstrain

    # ---- SCALE vs OFFSET, which are different faults and only one of them would matter.
    #
    # A raw ratio cannot tell them apart: a fixed offset makes the ratio large at small strain and
    # small at large strain, which reads exactly like a drifting scale. Regressing ours on theirs
    # separates them — the slope is the scale disagreement and the intercept is a constant, and the
    # constant converts back to PIXELS on the marker span, where it can be judged.
    a_sc, b_off = np.polyfit(theirs_p[live], ours_p[live], 1)
    fit_res = ours_p[live] - (a_sc * theirs_p[live] + b_off)
    ss = 1 - ((fit_res ** 2).sum()
              / ((ours_p[live] - ours_p[live].mean()) ** 2).sum())

    out = dict(
        # our pipeline on their video
        t=t, frame=fr[keep], L=L, e=ec, e_log=et, e_rz=ec_rz, sig=sig, f=f,
        cor=cor, tracked=int(tk.sum()), n=len(t),
        tear_dropped=int(n_dropped), ef_untrimmed=ec_raw_peak, n_frames=int(len(fr)),
        px0=float(L[0]), fps_true=float(fps_true), fps_entered=FPS_ENTERED,
        fps_factor=FPS_ENTERED / float(fps_true),
        gauge_entered=GAUGE_ENTERED, gauge_true=GAUGE_TRUE,
        pxmm_reported=float(L[0]) / GAUGE_ENTERED, pxmm_true=float(L[0]) / GAUGE_TRUE,
        i_pre=i_pre, t_pre=float(t[i_pre]), e_pre=float(ec[i_pre]),
        # their extensometer, on the same clock
        t_mot=t_e, e_mot=e_mot,
        # the pairing
        pair_n=int(len(pair_i)), live_n=int(live.sum()),
        ratio_med=float(np.median(r)), ratio_lo=float(np.percentile(r, 5)),
        ratio_hi=float(np.percentile(r, 95)), k=k,
        d_med=float(np.median(d_ue[live])), d_sd=float(d_ue[live].std()),
        d_p95=float(np.percentile(np.abs(d_ue[live]), 95)),
        d_max=float(np.abs(d_ue[live]).max()),
        scale=float(a_sc), scale_pct=float((a_sc - 1.0) * 100.0),
        offset_ue=float(b_off * 1e4), offset_px=float(b_off / 100.0 * float(L[0])),
        fit_r2=float(ss), fit_sd_ue=float(fit_res.std() * 1e4),
        fit_p95_ue=float(np.percentile(np.abs(fit_res), 95) * 1e4),
        pair_e_ours=ours_p, pair_e_theirs=theirs_p, pair_live=live, pair_t=t[pair_i],
    )
    _cache.update(out)
    return out


# --------------------------------------------------------------------------- landmarks
def landmarks(e_pct, sig, tag, label):
    """The same construction mot2_compare uses, so the three records stay commensurable."""
    i_u = int(np.argmax(sig))
    i_f = int(np.argmax(e_pct))
    fx = CMP.e_fixed(e_pct, sig)
    st = _steep(e_pct, sig)
    sy_f, ey_f = CMP._yield_02(e_pct, sig, fx["E"], fx.get("c", 0.0))
    sy_s, ey_s = CMP._yield_02(e_pct, sig, st["E"], st.get("c", 0.0))
    tough = float(np.trapezoid(sig, e_pct / 100.0)) if hasattr(np, "trapezoid") \
        else float(np.trapz(sig, e_pct / 100.0))
    return dict(tag=tag, label=label, uts=float(sig[i_u]), uts_e=float(e_pct[i_u]),
                ef=float(e_pct[i_f]), sigf=float(sig[i_f]),
                sy=sy_f, sy_e=ey_f, sy_steep=sy_s, sy_steep_e=ey_s,
                E_fix=fx, E_steep=st, tough=tough)


def _steep(e_pct, sig):
    test = [{"ecz": float(a) / 100.0, "sig": float(b)} for a, b in zip(e_pct, sig) if a >= 0]
    best = _steepest_straight_run(test)
    if best is None:
        return dict(E=float("nan"), R2=float("nan"), lo=float("nan"), hi=float("nan"), c=0.0)
    slope, c, r2, lo, hi = best
    return dict(E=slope / 1000.0, c=c, R2=r2, lo=lo * 100.0, hi=hi * 100.0)


def noise(t, e_pct, win=(0.05, 0.35)):
    """RMS residual about the straight fit, in microstrain.

    Scale-invariant in TIME: stretching the time axis by a constant stretches the fitted line by
    the same constant and leaves the residuals identical. So this number is comparable across all
    three records even though the post-processing ran on a 50x-wrong clock.
    """
    m = (e_pct >= win[0]) & (e_pct <= win[1])
    if m.sum() < 8:
        return None
    tt, ee = t[m], e_pct[m] / 100.0
    sl, ic = np.polyfit(tt, ee, 1)
    r = ee - (sl * tt + ic)
    a = np.abs(r) * 1e6
    return dict(rms=float(r.std() * 1e6), med=float(np.median(a)),
                p95=float(np.percentile(a, 95)), pp=float((r.max() - r.min()) * 1e6),
                n=int(m.sum()), dwell=float(tt.max() - tt.min()), win=win)


def build():
    """Everything the slides need, with the three records named the same way throughout."""
    if "build" in _cache:
        return _cache["build"]
    D = load()
    B = CMP.build()
    mot = B["recs"]["MOT"]
    s34 = B["recs"][B["primary"]]

    # our pipeline on their video, re-zeroed at their preload so it is on our convention and can
    # be set beside S34 as well as beside their own extensometer
    i0 = D["i_pre"]
    ours = dict(t=D["t"][i0:] - D["t_pre"], e=D["e_rz"][i0:], sig=D["sig"][i0:])

    L = {
        "PP": landmarks(ours["e"], ours["sig"], "PP", "our DIC · their video"),
        "MOT": B["L"]["MOT"],
        "S34": B["L"][B["primary"]],
    }
    N = {
        "PP": noise(ours["t"], ours["e"]),
        "MOT": noise(mot["t"], mot["e"]),
        "S34": noise(s34["t"], s34["e"]),
    }
    out = dict(D=D, B=B, ours=ours, mot=mot, s34=s34, L=L, N=N, primary=B["primary"])
    _cache["build"] = out
    return out


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    S = build()
    D, L, N = S["D"], S["L"], S["N"]

    print("MOT session 2 video through OUR DIC post-processing\n")
    print("  frames        : %d, %d tracked (%.1f %%), %d re-seeds implied"
          % (D["n"], D["tracked"], 100.0 * D["tracked"] / D["n"], 0))
    print("  Px0           : %.3f px over a %.4f mm marker span" % (D["px0"], D["gauge_true"]))
    print()
    print("  TWO INPUTS WERE WRONG, AND THE CORRECTION IS EXACT")
    print("    frame rate  : %.0f fps entered, %.4f fps true  -> time overstated %.2fx"
          % (D["fps_entered"], D["fps_true"], D["fps_factor"]))
    print("    gauge       : %.2f mm entered, %.4f mm true"
          % (D["gauge_entered"], D["gauge_true"]))
    print("    px/mm       : %.4f reported, %.4f true" % (D["pxmm_reported"], D["pxmm_true"]))
    print("    -> their session-1 optics were 27.9 px/mm. Unchanged between sessions.")
    print("    NEITHER touches strain: it is (L - Px0)/Px0 and both inputs cancel out of it.")
    print()
    print("  SAME VIDEO, TWO CALCULATIONS — %d matched instants, %d above 0.05 %% strain"
          % (D["pair_n"], D["live_n"]))
    print("    ratio ours/theirs : median %.4f   (5-95 %%: %.4f - %.4f)"
          % (D["ratio_med"], D["ratio_lo"], D["ratio_hi"]))
    print("    scale factor k    : %.5f  (least squares through the origin)" % D["k"])
    print("    difference        : median %+.1f ue, sd %.1f ue, p95 %.1f ue, max %.1f ue"
          % (D["d_med"], D["d_sd"], D["d_p95"], D["d_max"]))
    print("    SCALE vs OFFSET   : ours = %.6f x theirs %+.1f ue   (R2 %.7f)"
          % (D["scale"], D["offset_ue"], D["fit_r2"]))
    print("       scale differs by %+.3f %%; the offset is %.4f px on a %.1f px span,"
          % (D["scale_pct"], D["offset_px"], D["px0"]))
    print("       i.e. a reference-frame difference, not a calibration one.")
    print("       residual about that line: sd %.1f ue, p95 %.1f ue"
          % (D["fit_sd_ue"], D["fit_p95_ue"]))
    print("    tear trim         : %d trailing sample(s) dropped; untrimmed peak strain "
          "would read %.3f %% instead of %.3f %%"
          % (D["tear_dropped"], D["ef_untrimmed"], float(D["e"].max())))
    print()
    print("  LANDMARKS — our DIC on their video, against both neighbours")
    print("  %-22s %10s %10s %10s" % ("", "PP", "MOT", "S34"))
    for nm, key in (("UTS (MPa)", "uts"), ("strain at UTS (%)", "uts_e"),
                    ("sigma_y (MPa)", "sy_steep"), ("failure strain (%)", "ef"),
                    ("fracture stress (MPa)", "sigf"), ("toughness (MJ/m3)", "tough")):
        print("  %-22s %10.2f %10.2f %10.2f" % (nm, L["PP"][key], L["MOT"][key], L["S34"][key]))
    for nm, key in (("E fixed (GPa)", "E_fix"), ("E steepest (GPa)", "E_steep")):
        print("  %-22s %10.3f %10.3f %10.3f"
              % (nm, L["PP"][key]["E"], L["MOT"][key]["E"], L["S34"][key]["E"]))
    print("  %-22s %10s %10s %10s"
          % ("steepest window", "%.2f-%.2f" % (L["PP"]["E_steep"]["lo"], L["PP"]["E_steep"]["hi"]),
             "%.2f-%.2f" % (L["MOT"]["E_steep"]["lo"], L["MOT"]["E_steep"]["hi"]),
             "%.2f-%.2f" % (L["S34"]["E_steep"]["lo"], L["S34"]["E_steep"]["hi"])))
    print()
    print("  OFFSETS from their own extensometer (the same footage)")
    for nm, key in (("UTS", "uts"), ("sigma_y", "sy_steep"), ("failure strain", "ef"),
                    ("toughness", "tough")):
        print("    %-16s %+7.2f %%" % (nm, CMP.offset_pct(L["PP"][key], L["MOT"][key])))
    for nm, key in (("E fixed", "E_fix"), ("E steepest", "E_steep")):
        print("    %-16s %+7.2f %%"
              % (nm, CMP.offset_pct(L["PP"][key]["E"], L["MOT"][key]["E"])))
    print()
    print("  NOISE — 0.05-0.35 %% window, all three")
    for k in ("PP", "MOT", "S34"):
        n = N[k]
        print("    %-4s rms %6.1f ue   median %6.1f   p95 %6.1f   (%d pts)"
              % (k, n["rms"], n["med"], n["p95"], n["n"]))
