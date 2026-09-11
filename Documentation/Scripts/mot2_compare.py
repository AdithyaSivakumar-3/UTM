"""MOT session 2 against our own 45 mm gauge runs — the comparison Test 1 could not make.

Test 1's MOT export was STRAIN ONLY and stopped at 0.40 %, so E, sigma_y, UTS and eps_f were all
out of reach and the honest verdict was "noise is the only comparison that survives". Session 2
carries a load channel and runs to fracture, so every landmark can be compared, and the compliance
question Test 1 had to leave open can be closed with a number.

THREE THINGS ARE HELD FIXED SO THE COMPARISON MEANS SOMETHING:

  1. THE STRAIN ZERO. Ours is frozen after a ~310 N preload; theirs is at zero load, with the
     300 N preload applied inside the record. Their strain is therefore re-zeroed at the instant
     their load first reaches 300 N (mot2_data does this), which puts both on our convention. The
     as-recorded numbers are kept beside it so nothing is hidden.
  2. THE MODULUS METHOD. Our headline E comes from the app's steepest-straight-run search, not
     from a fixed window, and the two disagree by ~12 % on our own runs. Comparing our steepest
     run against their fixed window would be a method difference dressed up as a machine
     difference, so BOTH methods are run on BOTH machines, using the app's own search function.
  3. THE NOISE WINDOW. Our DIC noise floor grows with observation time, and they dwell 3x longer
     in any given strain interval because they pull 3x slower. A matched STRAIN window therefore
     flatters us and a matched DURATION window flatters them, so both are reported.

WHICH OF OUR TWO RUNS IS THE REFERENCE, decided on data quality BEFORE any agreement was looked
at: S34. It tracked 83 % of its load samples against S33's 78 %, and eps_f depends on catching the
last samples before fracture, which is exactly what missing coverage takes away — S33's 2.95 %
sits below the 80 mm pair's whole 4.18-5.74 % range and is not trustworthy. S33 is carried through
every table anyway, as the second reference.
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_APP = os.path.abspath(os.path.join(_HERE, "..", "..", "Software", "UTM_PyQt6"))
for _p in (_HERE, _APP):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import mot2_data as M2                                                # noqa: E402
import s25_s26_data as V45                                            # noqa: E402
from utm_analysis import analyze, read_csv, _steepest_straight_run    # noqa: E402

FIX_WIN = (0.05, 0.40)          # % strain — the project's fixed modulus window
NOISE_WIN = (0.05, 0.40)        # % strain — matched-strain noise interval
NOISE_SECONDS = 4.5             # s — matched-duration noise interval (fits inside our short ramp)
PRIMARY = "S34"
SECOND = "S33"

_cache = {}


# --------------------------------------------------------------------------- the three records
def ours(tag):
    """One of our runs as time / strain % / stress MPa, on the LOADING RAMP ONLY.

    analyze() mutates the sample dicts it is given, so it is fed the list rather than the path:
    that is what makes `ecz` (preload-zeroed strain) and `sig` available per sample WITH the time
    column still attached. Calling it on the path would compute the same numbers and throw the
    per-sample record away.

    Samples with lpx <= 100 are dropped — that is the app's own MARKER LOST sentinel, and on these
    two runs it accounts for the 17-22 % of samples the coverage note is about. Keeping them would
    put strain 0 next to a real load.
    """
    if ("ours", tag) in _cache:
        return _cache[("ours", tag)]
    rows = read_csv(V45.csv_path(tag))
    r = analyze(rows, V45.AREA_MM2, V45.RUNS[tag].get("gauge", V45.GAUGE_MM))
    ramp = [d for d in rows[r["mv_i"]:r["fr_i"]] if d["lpx"] > 100]
    lost_all = sum(1 for d in rows if d["lpx"] <= 100)
    out = dict(
        tag=tag, label=V45.RUNS[tag]["label"], res=r,
        t=np.array([d["t"] for d in ramp]) - ramp[0]["t"],
        e=np.array([d["ecz"] for d in ramp]) * 100.0,
        sig=np.array([d["sig"] for d in ramp]),
        n=len(ramp), n_raw=len(rows),
        # TWO coverage numbers, because they say opposite things and only one of them matters.
        # The validation pack quoted whole-record coverage (S34 83 %, S33 78 %) and warned that
        # eps_f could not be trusted on either. Split by WHERE the losses fall and that warning
        # survives for S33 only: all 202 of S34's dropouts are after its fracture sample, so
        # 99.9 % of its actual pull is tracked, while 145 of S33's fall inside the pull.
        cover_all=100.0 * (len(rows) - lost_all) / len(rows),
        cover=100.0 * len(ramp) / max(1, r["fr_i"] - r["mv_i"]),
        px0=float(np.median([d["lpx"] for d in ramp[:20]])),
        gauge=V45.RUNS[tag].get("gauge", V45.GAUGE_MM),
        hz=1.0 / float(np.median(np.diff([d["t"] for d in ramp]))),
    )
    _cache[("ours", tag)] = out
    return out


def mot():
    """MOT session 2 on the load clock, strain re-zeroed at their 300 N preload.

    Trimmed at the strain peak: past it the marks ride on two halves that have already parted, and
    the curve doubles back. Time is re-origined at the preload instant so it lines up with ours,
    which starts at the moment the crosshead moves off an already-preloaded specimen.
    """
    if "mot" in _cache:
        return _cache["mot"]
    d = M2.load()
    k = int(np.argmax(d["e_on_f"])) + 1
    i0 = d["i_pre"]
    out = dict(
        tag="MOT", label="MOT XT-205 · 45 mm", res=d,
        t=d["t_f"][i0:k] - d["t_pre"],
        e=d["e_rz"][i0:k],
        sig=d["sig"][i0:k],
        n=k - i0, hz=d["rate_hz"], cover=100.0,
    )
    _cache["mot"] = out
    return out


# --------------------------------------------------------------------------- the two E methods
def e_fixed(e_pct, sig, win=FIX_WIN):
    """Least squares over a FIXED strain window. (E GPa, R2, n)."""
    m = (e_pct >= win[0]) & (e_pct <= win[1])
    if m.sum() < 5:
        return dict(E=float("nan"), R2=float("nan"), n=int(m.sum()), lo=win[0], hi=win[1])
    A = np.polyfit(e_pct[m] / 100.0, sig[m], 1)
    pred = np.polyval(A, e_pct[m] / 100.0)
    ss = 1 - ((sig[m] - pred) ** 2).sum() / ((sig[m] - sig[m].mean()) ** 2).sum()
    return dict(E=float(A[0]) / 1000.0, c=float(A[1]), R2=float(ss), n=int(m.sum()),
                lo=win[0], hi=win[1])


def e_steep(e_pct, sig):
    """The app's own steepest-straight-run search, run on whichever record it is given.

    This is the point of the module: our headline modulus is not a fixed-window fit, so comparing
    our steepest run against their fixed window would report a METHOD difference as a MACHINE
    difference. The same function the app's report button calls is used on both.
    """
    test = [{"ecz": float(a) / 100.0, "sig": float(b)} for a, b in zip(e_pct, sig) if a >= 0]
    best = _steepest_straight_run(test)
    if best is None:
        return dict(E=float("nan"), R2=float("nan"), lo=float("nan"), hi=float("nan"), n=0)
    slope, c, r2, lo, hi = best
    n = int(((e_pct / 100.0 >= lo) & (e_pct / 100.0 <= hi)).sum())
    return dict(E=slope / 1000.0, c=c, R2=r2, lo=lo * 100.0, hi=hi * 100.0, n=n)


# --------------------------------------------------------------------------- landmarks
def _yield_02(e_pct, sig, E_gpa, c):
    """0.2 % offset yield on a given modulus line. (sigma_y, eps_y) or (nan, nan)."""
    if not np.isfinite(E_gpa):
        return float("nan"), float("nan")
    off = (E_gpa * 1000.0) * ((e_pct / 100.0) - 0.002) + c
    d = sig - off
    x = np.nonzero((d[:-1] > 0) & (d[1:] <= 0))[0]
    if not len(x):
        return float("nan"), float("nan")
    j = int(x[0])
    return float(sig[j]), float(e_pct[j])


def landmarks(rec):
    """UTS, 0.2 % offset yield and fracture for one record, all from ITS OWN arrays.

    Yield is recomputed here rather than taken from each record's own analysis, because the offset
    line is drawn from the modulus and the two machines' moduli come from different methods. Using
    each source's stored sigma_y would compare two different constructions.
    """
    e, sig = rec["e"], rec["sig"]
    i_u = int(np.argmax(sig))
    i_f = int(np.argmax(e))
    fx, st = e_fixed(e, sig), e_steep(e, sig)
    sy_f, ey_f = _yield_02(e, sig, fx["E"], fx.get("c", 0.0))
    sy_s, ey_s = _yield_02(e, sig, st["E"], st.get("c", 0.0))
    return dict(
        tag=rec["tag"], label=rec["label"],
        uts=float(sig[i_u]), uts_e=float(e[i_u]),
        ef=float(e[i_f]), sigf=float(sig[i_f]),
        sy=sy_f, sy_e=ey_f, sy_steep=sy_s, sy_steep_e=ey_s,
        E_fix=fx, E_steep=st,
        tough=float(np.trapezoid(sig, e / 100.0)) if hasattr(np, "trapezoid")
        else float(np.trapz(sig, e / 100.0)),
    )


def offset_pct(theirs, ours_):
    """Signed difference as a percentage OF OURS — ours is the reference being checked."""
    if not (np.isfinite(theirs) and np.isfinite(ours_)) or ours_ == 0:
        return float("nan")
    return (theirs - ours_) / ours_ * 100.0


# --------------------------------------------------------------------------- noise
def noise_strain(rec, win=NOISE_WIN):
    """RMS scatter about the straight fit over a matched STRAIN window, in microstrain.

    Also returns how long each instrument DWELLED in that window, because that is the confound:
    our noise floor grows with observation time, and they are 3x slower.
    """
    e, t = rec["e"], rec["t"]
    m = (e >= win[0]) & (e <= win[1])
    if m.sum() < 8:
        return None
    tt, ee = t[m], e[m] / 100.0
    sl, ic = np.polyfit(tt, ee, 1)
    r = ee - (sl * tt + ic)
    a = np.abs(r) * 1e6
    return dict(rms=float(r.std() * 1e6), med=float(np.median(a)), p95=float(np.percentile(a, 95)),
                pp=float((r.max() - r.min()) * 1e6),
                step=float(np.median(np.abs(np.diff(ee)) * 1e6)),
                dwell=float(tt.max() - tt.min()), n=int(m.sum()), win=win)


def noise_dur(rec, secs=NOISE_SECONDS, win=NOISE_WIN):
    """The same measurement over a matched DURATION instead — the fair half of the pair.

    The window is anchored at the END of the strain interval so both records are on the loading
    ramp and neither is sitting in the toe.
    """
    e, t = rec["e"], rec["t"]
    m = (e >= win[0]) & (e <= win[1])
    if m.sum() < 8:
        return None
    t_end = t[m].max()
    k = (t >= t_end - secs) & (t <= t_end)
    if k.sum() < 8:
        return None
    tt, ee = t[k], e[k] / 100.0
    sl, ic = np.polyfit(tt, ee, 1)
    r = ee - (sl * tt + ic)
    a = np.abs(r) * 1e6
    return dict(rms=float(r.std() * 1e6), med=float(np.median(a)), p95=float(np.percentile(a, 95)),
                pp=float((r.max() - r.min()) * 1e6),
                step=float(np.median(np.abs(np.diff(ee)) * 1e6)),
                dwell=float(tt.max() - tt.min()), n=int(k.sum()),
                de=float((e[k].max() - e[k].min())))


# --------------------------------------------------------------------------- gauge share
def share(rec):
    """What fraction of crosshead travel actually reached the gauge.

    Ours is measured (the rig records crosshead position); theirs is nominal (speed x time), because
    the .daq carries no crosshead channel. Flagged rather than smoothed over — if their crosshead
    ever lagged its command, their true share is HIGHER than this, not lower.
    """
    if rec["tag"] == "MOT":
        return dict(pct=rec["res"]["share_total"], src="nominal (speed x time)",
                    stretch=rec["res"]["stretch"], travel=rec["res"]["travel"])
    r = rec["res"]
    return dict(pct=r["gauge_share"], src="measured (crosshead channel)",
                stretch=r["ef"] * V45.RUNS[rec["tag"]].get("gauge", V45.GAUGE_MM),
                travel=r["travel"])


# --------------------------------------------------------------------------- noise across gauges
#
# Test 1 found the XT-205 NOISIER than us and said so. Test 2 finds it QUIETER. Before that is
# reported as a reversal, the obvious confound has to be ruled out: the gauge changed too, and a
# shorter gauge spans fewer pixels, so one pixel of jitter is worth more strain. Both machines'
# sessions are therefore put on ONE window and the ratio is checked against what the pixel counts
# predict — a real prediction that can fail.
GAUGE_WIN = (0.05, 0.35)        # % — Test 1's window, which stays clear of its record's last point


def _noise_of(t, e_pct, win=GAUGE_WIN):
    m = (e_pct >= win[0]) & (e_pct <= win[1])
    if m.sum() < 8:
        return None
    tt, ee = t[m], e_pct[m] / 100.0
    sl, ic = np.polyfit(tt, ee, 1)
    r = ee - (sl * tt + ic)
    return dict(rms=float(r.std() * 1e6), n=int(m.sum()),
                dwell=float(tt.max() - tt.min()))


def gauge_scaling():
    """Our noise floor against 1 / (marker span in pixels), across both gauges.

    The prediction, if our floor is set by how finely the marker centres can be located rather than
    by the specimen or the lighting: strain noise scales as 1/Px0, because strain is a pixel ratio
    with Px0 in the denominator. Going from an 80 mm gauge to a 45 mm one takes the span from
    ~1676 px to ~939 px, so the floor should rise by 1676/939 = 1.78x. That is a number to be
    measured against, not asserted.

    MOT's two sessions are listed beside ours, but NOT fitted to the same prediction: their Test 2
    optics are unknown, so their pixel span at 45 mm cannot be computed here. It is the first thing
    their footage through our pipeline will give us.
    """
    V45.use_pair("45mm")
    runs = {t: ours(t) for t in ("S25", "S26", "S33", "S34")}
    V45.use_pair("80mm")
    for k, v in runs.items():
        v["noise"] = _noise_of(v["t"], v["e"])

    g80 = [runs[k] for k in ("S25", "S26")]
    g45 = [runs[k] for k in ("S33", "S34")]
    px80 = float(np.mean([r["px0"] for r in g80]))
    px45 = float(np.mean([r["px0"] for r in g45]))
    n80 = float(np.mean([r["noise"]["rms"] for r in g80]))
    n45 = float(np.mean([r["noise"]["rms"] for r in g45]))

    # the XT-205's own two sessions, on the same window
    import mot_compare as M1
    tm, em, gl_m1 = M1.read_mot()
    mot1 = _noise_of(tm, em * 100.0)
    mot2 = _noise_of(mot()["t"], mot()["e"])

    return dict(
        runs=runs, px80=px80, px45=px45, n80=n80, n45=n45,
        predicted=px80 / px45, measured=n45 / n80,
        mot1=mot1, mot2=mot2, mot1_gauge=gl_m1,
        mot_ratio=(mot2["rms"] / mot1["rms"]) if (mot1 and mot2) else float("nan"),
        win=GAUGE_WIN,
    )


# --------------------------------------------------------------------------- the whole picture
def build():
    if "build" in _cache:
        return _cache["build"]
    V45.use_pair("45mm")
    recs = {"MOT": mot(), PRIMARY: ours(PRIMARY), SECOND: ours(SECOND)}
    V45.use_pair("80mm")                       # module state is shared; put it back
    L = {k: landmarks(v) for k, v in recs.items()}
    out = dict(
        recs=recs, L=L, primary=PRIMARY, second=SECOND,
        noise_s={k: noise_strain(v) for k, v in recs.items()},
        noise_d={k: noise_dur(v) for k, v in recs.items()},
        share={k: share(v) for k, v in recs.items()},
        fix_win=FIX_WIN,
    )
    _cache["build"] = out
    return out


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    B = build()
    K = ["MOT", PRIMARY, SECOND]
    print("MOT session 2 vs our 45 mm pair — primary reference is %s\n" % PRIMARY)

    print("  %-6s %8s %9s %8s %8s %8s %8s" % ("", "n", "Hz", "cover%", "UTS", "eps_f", "tough"))
    for k in K:
        r, l = B["recs"][k], B["L"][k]
        print("  %-6s %8d %9.2f %8.1f %8.2f %8.2f %8.0f"
              % (k, r["n"], r["hz"], r["cover"], l["uts"], l["ef"], l["tough"]))

    print("\n  MODULUS — the same two methods on both machines")
    print("  %-6s %22s %28s" % ("", "fixed 0.05-0.40 %", "steepest straight run"))
    for k in K:
        f, s = B["L"][k]["E_fix"], B["L"][k]["E_steep"]
        print("  %-6s   %6.3f GPa (R2 %.4f) %10.3f GPa (R2 %.4f, %.2f-%.2f %%)"
              % (k, f["E"], f["R2"], s["E"], s["R2"], s["lo"], s["hi"]))

    print("\n  LANDMARKS, and MOT's offset from %s" % PRIMARY)
    p = B["L"][PRIMARY]
    m = B["L"]["MOT"]
    for name, a, b in (("sigma_y (fixed E)", m["sy"], p["sy"]),
                       ("sigma_y (steepest E)", m["sy_steep"], p["sy_steep"]),
                       ("UTS", m["uts"], p["uts"]),
                       ("failure strain", m["ef"], p["ef"]),
                       ("E, fixed window", m["E_fix"]["E"], p["E_fix"]["E"]),
                       ("E, steepest run", m["E_steep"]["E"], p["E_steep"]["E"])):
        print("    %-22s MOT %8.3f   %s %8.3f   offset %+7.1f %%"
              % (name, a, PRIMARY, b, offset_pct(a, b)))

    print("\n  NOISE — matched strain window %.2f-%.2f %%" % NOISE_WIN)
    print("  %-6s %9s %9s %9s %9s %8s" % ("", "rms ue", "med ue", "p95 ue", "step ue", "dwell s"))
    for k in K:
        n = B["noise_s"][k]
        if n:
            print("  %-6s %9.1f %9.1f %9.1f %9.1f %8.1f"
                  % (k, n["rms"], n["med"], n["p95"], n["step"], n["dwell"]))
    print("\n  NOISE — matched duration %.1f s (the fair half of the pair)" % NOISE_SECONDS)
    for k in K:
        n = B["noise_d"][k]
        if n:
            print("  %-6s %9.1f %9.1f %9.1f %9.1f %8.1f   over %.3f %% strain"
                  % (k, n["rms"], n["med"], n["p95"], n["step"], n["dwell"], n["de"]))

    print("\n  GAUGE SHARE — the question Test 1 had to leave open")
    for k in K:
        s = B["share"][k]
        print("  %-6s %6.1f %%   %.3f mm of %.3f mm   [%s]"
              % (k, s["pct"], s["stretch"], s["travel"], s["src"]))

    G = gauge_scaling()
    print("\n  NOISE ACROSS BOTH GAUGES — window %.2f-%.2f %%, all six records" % G["win"])
    for k in ("S25", "S26", "S33", "S34"):
        r = G["runs"][k]
        print("    %-4s %2.0f mm gauge  Px0 %6.1f px   rms %6.1f ue   (%d pts, %.1f s)"
              % (k, r["gauge"], r["px0"], r["noise"]["rms"], r["noise"]["n"], r["noise"]["dwell"]))
    print("    MOT  %.0f mm gauge  (session 1)      rms %6.1f ue" % (G["mot1_gauge"], G["mot1"]["rms"]))
    print("    MOT  45 mm gauge  (session 2)      rms %6.1f ue" % G["mot2"]["rms"])
    print("\n    ours, 80 -> 45 mm : Px0 %.0f -> %.0f px, so 1/Px0 predicts %.3fx"
          % (G["px80"], G["px45"], G["predicted"]))
    print("                        noise %.1f -> %.1f ue, MEASURED %.3fx   (%.1f %% from prediction)"
          % (G["n80"], G["n45"], G["measured"],
             abs(G["measured"] - G["predicted"]) / G["predicted"] * 100))
    print("    XT-205, session 1 -> 2 : noise %.1f -> %.1f ue, %.2fx — moved the OTHER way"
          % (G["mot1"]["rms"], G["mot2"]["rms"], G["mot_ratio"]))
