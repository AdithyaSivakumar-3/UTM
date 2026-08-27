"""Measure how each DIC position estimator actually behaves, and cache the result.

Everything the estimator slides claim is measured here, on real recorded video, and written to
documentation/estimator_measurements.json. The plots and slides read that cache rather than
re-running the analyses, because a full sweep is minutes of video decoding and the deck is built
many times a day.

Run this directly to refresh the cache:

    python documentation/scripts/estimator_data.py

The cache records WHEN it was measured and with what step, so a number on a slide can always be
traced back to a run rather than to somebody's memory.
"""
import io
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CACHE = os.path.join(HERE, "..", "estimator_measurements.json")
sys.path.insert(0, os.path.join(ROOT, "Software", "UTM_PyQt6"))

import cv2                                                             # noqa: E402
import utm_postproc as PP                                              # noqa: E402
from utm_analysis import read_csv, analyze                             # noqa: E402

STEP = 3                      # every 3rd frame: the window still holds >100 points on both runs
SPECIMENS = ("S25", "S26")


def _video(spec):
    import glob
    return glob.glob(os.path.join(ROOT, "Software", "UTM_PyQt6", "Test data", "**",
                                  "Specimen_%s_*" % spec, "**", "video.avi"), recursive=True)[0]


def _csv(spec):
    import glob
    f = glob.glob(os.path.join(ROOT, "Software", "UTM_PyQt6", "Test data", "**",
                               "Specimen_%s_*" % spec, "*.csv"), recursive=True)
    return sorted(f)[0] if f else None


def _markers(video):
    g = PP.read_frame(video, 0)
    return g, sorted(PP.find_markers(g)[:2], key=lambda m: m[1])


def capture_offset(spec):
    """Seconds into the test at which the video's first frame was written.

    The capture does not start with the test — S25's begins 33.7 s in, S26's 10.8 s in — so the
    frame sidecar's wall-clock stamp, not the frame number, is what puts a frame on the test's
    timeline. Reading it from index.csv rather than hard-coding it is the whole point: a hard-coded
    offset is right for exactly the specimen it was measured on.
    """
    import csv
    import datetime
    import glob
    d = glob.glob(os.path.join(ROOT, "Software", "UTM_PyQt6", "Test data", "**",
                               "Specimen_%s_*" % spec), recursive=True)[0]
    idx = glob.glob(os.path.join(d, "**", "index.csv"), recursive=True)
    if not idx:
        return 0.0
    t0 = None
    for ln in io.open(_csv(spec), encoding="utf-8", errors="replace"):
        if ln.startswith("# Test Date:"):
            t0 = datetime.datetime.strptime(ln.split(":", 1)[1].strip(), "%Y-%m-%d %H:%M:%S")
            break
    if t0 is None:
        return 0.0
    row0 = next(csv.DictReader(io.open(idx[0], encoding="utf-8")))
    return (datetime.datetime.fromisoformat(row0["pc_time_iso"]) - t0).total_seconds()


def window_frames(spec, fps):
    """The FRAME range covering the rig's own 0.05-0.35 % strain window.

    Every configuration below is scored over this same range. That matters more than it sounds:
    if each run picks its window from its OWN strain estimate, a configuration that tracks badly
    gets judged over a different slice of the test, and the comparison stops being a comparison.
    The range comes from the rig's strain, which no post-processing setting can influence.
    """
    rows = [r for r in read_csv(_csv(spec)) if r["lpx"] > 100]
    off = capture_offset(spec)
    t = [r["t"] for r in rows if 0.0005 <= r["ec"] <= 0.0035]
    if not t:
        return None
    return int(round((min(t) - off) * fps)), int(round((max(t) - off) * fps))


def _window_noise(rows, l0, span):
    """Scatter about a straight line over the fixed frame window.

    The window is short and the material is still elastic there, so a straight line is the right
    model and what it leaves behind is noise rather than the curve's own shape. Detrend a whole
    fracture curve with a polynomial instead and you measure the polynomial.
    """
    i0, i1 = span
    s = np.array([r.l_px for r in rows if r.ok and i0 <= r.idx <= i1], float)
    if len(s) < 20:
        return None, len(s)
    t = np.arange(len(s))
    return float((s - np.polyval(np.polyfit(t, s, 1), t)).std() / l0 * 1e6), len(s)


def _run(video, ms, half, refine, span, step=STEP):
    A = PP.Box(ms[0][0], ms[0][1])
    B = PP.Box(ms[1][0], ms[1][1])
    # stop_on_loss OFF here, deliberately. The app stops a run the moment tracking is lost, which
    # is right for measuring a specimen — but these sweeps deliberately include configurations that
    # track badly, and letting the run abort would score them over a shorter slice of the test than
    # the good ones. That is the very bias the fixed frame window exists to remove.
    cfg = PP.Settings(gauge_mm=80, box_half=half, search=60, fps=19.9273, step=step,
                      refine=refine, stop_on_loss=False)
    gen = PP.analyse(video, A, B, cfg)
    try:
        while True:
            next(gen)
    except StopIteration as stop:
        S = stop.value
    ue, n = _window_noise(S.rows, S.l0_px, span)
    return {"noise_ue": ue, "n_window": n, "l0": S.l0_px, "coverage": S.coverage,
            "peak_pct": max((r.cauchy for r in S.rows if r.ok), default=0) * 100}


# ---------------------------------------------------------------- A. box size
def box_sweep():
    out = {}
    for spec in SPECIMENS:
        v = _video(spec)
        _g, ms = _markers(v)
        span = window_frames(spec, 19.9273)
        r_marker = max(ms[0][2], ms[1][2])
        rows = []
        for half in (24, 32, 40, 56, 76, 90):
            res = _run(v, ms, half, "auto", span)
            rows.append({"half": half, "ratio": half / r_marker, **res})
            print("  %s box %3d -> %s ue" % (spec, half, res["noise_ue"]))
        out[spec] = {"marker_radius": r_marker, "rows": rows}
    return out


# ---------------------------------------------------------------- B. method
def method_compare():
    out = {}
    for spec in SPECIMENS:
        v = _video(spec)
        _g, ms = _markers(v)
        half = int(round(1.25 * max(ms[0][2], ms[1][2])))
        span = window_frames(spec, 19.9273)
        out[spec] = {"half": half, "window_frames": span}
        for refine in ("correlation", "rig", "auto"):
            out[spec][refine] = _run(v, ms, half, refine, span)
            print("  %s %-11s -> %s ue" % (spec, refine, out[spec][refine]["noise_ue"]))
    return out


# ---------------------------------------------------------------- C. threshold sensitivity
def threshold_sensitivity():
    """How far the estimated CENTRE moves as the binarising level is swept, for each estimator.

    This is the property that makes a threshold a free parameter landing in the measurement.
    """
    out = {}
    levels = list(range(120, 191, 5))
    for spec in SPECIMENS:
        v = _video(spec)
        g, ms = _markers(v)
        r = int(round(1.25 * max(ms[0][2], ms[1][2])))
        cx, cy = ms[0][0], ms[0][1]
        binary, weighted = [], []
        for thr in levels:
            b = PP.centroid_refine(g, cx, cy, r, True, float(thr), weighted=False)
            w = PP.centroid_refine(g, cx, cy, r, True, float(thr), weighted=True)
            binary.append(None if not b else b[1])
            weighted.append(None if not w else w[1])
        def spread(vals):
            v2 = [x for x in vals if x is not None]
            return (max(v2) - min(v2)) if len(v2) > 1 else None
        out[spec] = {"levels": levels, "binary_y": binary, "weighted_y": weighted,
                     "binary_spread_px": spread(binary), "weighted_spread_px": spread(weighted),
                     "l0": float(np.hypot(ms[1][0] - ms[0][0], ms[1][1] - ms[0][1]))}
        print("  %s spread: binary %.3f px, weighted %.3f px"
              % (spec, out[spec]["binary_spread_px"], out[spec]["weighted_spread_px"]))
    return out


# ---------------------------------------------------------------- D. what the centroid is anchored to
def anchor_compare():
    """Centroid chained from its OWN last position vs re-centred on a correlation estimate.

    Same estimator, same threshold, same patch size — only the window's anchor differs. It is the
    cleanest demonstration that a precise estimator can be spoiled by what you point it at.
    """
    out = {}
    for spec in SPECIMENS:
        v = _video(spec)
        g0, ms = _markers(v)
        span = window_frames(spec, 19.9273)
        half = int(round(1.25 * max(ms[0][2], ms[1][2])))
        tmpl = [PP.Box(m[0], m[1], half).clamp(g0.shape[1], g0.shape[0]).patch(g0) for m in ms]
        thr = [PP.reference_threshold(t, True) for t in tmpl]
        res = {}
        for mode in ("own", "correlation"):
            cap = cv2.VideoCapture(v)
            pos = [np.array([m[0], m[1]], float) for m in ms]
            L, keep, n = [], [], 0
            while n < 1400:
                ok, fr = cap.read()
                if not ok:
                    break
                if n % STEP:
                    n += 1
                    continue
                gray = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY) if fr.ndim == 3 else fr
                new = []
                for i in (0, 1):
                    anchor = pos[i]
                    if mode == "correlation":
                        m = PP._match(gray, tmpl[i], pos[i], 60)
                        if m is None:
                            new = None
                            break
                        anchor = np.array(m[:2])
                    c = PP.centroid_refine(gray, anchor[0], anchor[1], half, True, thr[i])
                    if c is None:
                        new = None
                        break
                    new.append(np.array([c[0], c[1]]))
                if new:
                    pos = new
                    L.append(abs(pos[1][1] - pos[0][1]))
                    keep.append(n)
                n += 1
            cap.release()
            fake = [type("R", (), {"l_px": x, "idx": i, "ok": True})
                    for x, i in zip(L, keep)]
            ue, cnt = _window_noise(fake, L[0], span) if L else (None, 0)
            res[mode] = {"noise_ue": ue, "n_window": cnt, "frames": len(L)}
            print("  %s anchored to %-11s -> %s ue" % (spec, mode, ue))
        out[spec] = res
    return out


# ---------------------------------------------------------------- F. threshold POLICY
def threshold_policy():
    """One level fixed at the reference frame, against Otsu recomputed every frame.

    Both are the same estimator on the same patches; only where the grey level comes from differs.
    Otsu per frame sounds strictly better — it adapts to lighting — but it re-decides the cut every
    frame, and the centroid inherits every wobble of that decision. This is the measurement behind
    the choice, and it is the one number in the set that is purely a policy question rather than a
    property of the optics.
    """
    out = {}
    for spec in SPECIMENS:
        v = _video(spec)
        g0, ms = _markers(v)
        span = window_frames(spec, 19.9273)
        half = int(round(1.25 * max(ms[0][2], ms[1][2])))
        fixed = [PP.reference_threshold(
            PP.Box(m[0], m[1], half).clamp(g0.shape[1], g0.shape[0]).patch(g0), True) for m in ms]
        res = {}
        for mode in ("fixed", "per_frame_otsu"):
            cap = cv2.VideoCapture(v)
            pos = [np.array([m[0], m[1]], float) for m in ms]
            L, keep, n = [], [], 0
            while n <= span[1] + 5:
                ok, fr = cap.read()
                if not ok:
                    break
                if n % STEP:
                    n += 1
                    continue
                gray = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY) if fr.ndim == 3 else fr
                new = []
                for i in (0, 1):
                    c = PP.centroid_refine(gray, pos[i][0], pos[i][1], half, True,
                                           fixed[i] if mode == "fixed" else None)
                    if c is None:
                        new = None
                        break
                    new.append(np.array([c[0], c[1]]))
                if new:
                    pos = new
                    L.append(abs(pos[1][1] - pos[0][1]))
                    keep.append(n)
                n += 1
            cap.release()
            rows = [type("R", (), {"l_px": x, "idx": i, "ok": True}) for x, i in zip(L, keep)]
            ue, cnt = _window_noise(rows, L[0], span) if L else (None, 0)
            res[mode] = {"noise_ue": ue, "n_window": cnt, "frames": len(L)}
            print("  %s %-14s -> %s ue" % (spec, mode, ue))
        out[spec] = res
    return out


# ---------------------------------------------------------------- E. accuracy against the rig
def accuracy_vs_live():
    out = {}
    for spec in SPECIMENS:
        c = _csv(spec)
        if not c:
            continue
        v = _video(spec)
        g, ms = _markers(v)
        half = int(round(1.25 * max(ms[0][2], ms[1][2])))
        a = analyze(c, 80, 80)
        rows = read_csv(c)
        t_fr = rows[a["fr_i"]]["t"]
        lt = np.array([r["t"] for r in rows if r["lpx"] > 100])
        le = np.array([r["ec"] for r in rows if r["lpx"] > 100])
        sc = PP.true_fps_from_sidecar(v)
        fps = sc[0] if sc else 19.9273
        off = capture_offset(spec)
        A = PP.Box(ms[0][0], ms[0][1]); B = PP.Box(ms[1][0], ms[1][1])
        cfg = PP.Settings(gauge_mm=80, box_half=half, search=60, fps=fps, step=STEP,
                          stop_on_loss=False)
        gen = PP.analyse(v, A, B, cfg)
        try:
            while True:
                next(gen)
        except StopIteration as stop:
            S = stop.value
        ok = [r for r in S.rows if r.ok]
        pt = np.array([r.t for r in ok]) + off
        pe = np.array([r.cauchy for r in ok])
        base = float(np.interp(pt[0], lt, le))
        grid = np.linspace(pt[0], min(t_fr - 1.0, pt.max()), 600)
        d = np.interp(grid, pt, pe) - (np.interp(grid, lt, le) - base)
        out[spec] = {"mean_ue": float(d.mean() * 1e6), "rms_ue": float(d.std() * 1e6),
                     "post_peak_pct": float(pe.max() * 100), "ef_pct": float(a["ef"] * 100),
                     "live_t": lt.tolist(), "live_e": le.tolist(),
                     "post_t": pt.tolist(), "post_e": pe.tolist(),
                     "base": base, "t_fr": float(t_fr)}
        print("  %s vs live: mean %+.0f ue, RMS %.0f ue" % (spec, out[spec]["mean_ue"],
                                                            out[spec]["rms_ue"]))
    return out


def build():
    t0 = time.time()
    data = {"measured": time.strftime("%Y-%m-%d %H:%M"), "step": STEP,
            "gauge_px_note": "noise quoted over the 0.05-0.35 % strain window, fixed in FRAME "
                             "numbers from the rig's own strain so every configuration is scored "
                             "over the same slice of the test",
            "capture_offset_s": {sp: round(capture_offset(sp), 2) for sp in SPECIMENS},
            "window_frames": {sp: window_frames(sp, 19.9273) for sp in SPECIMENS}}
    print("box size sweep..."); data["box"] = box_sweep()
    print("method comparison..."); data["method"] = method_compare()
    print("threshold sensitivity..."); data["threshold"] = threshold_sensitivity()
    print("anchor comparison..."); data["anchor"] = anchor_compare()
    print("threshold policy..."); data["threshold_policy"] = threshold_policy()
    print("accuracy vs live..."); data["accuracy"] = accuracy_vs_live()
    # the live rig's own noise, over the same window, for the comparison bar
    live = {}
    for spec in SPECIMENS:
        c = _csv(spec)
        if not c:
            continue
        rows = [r for r in read_csv(c) if r["lpx"] > 100]
        lp = np.array([r["lpx"] for r in rows]); ec = np.array([r["ec"] for r in rows])
        m = (ec >= 0.0005) & (ec <= 0.0035)
        s = lp[m]; t = np.arange(len(s))
        live[spec] = float((s - np.polyval(np.polyfit(t, s, 1), t)).std() / lp[0] * 1e6)
    data["live_rig"] = live
    print("  live rig:", {k: round(v, 1) for k, v in live.items()})
    io.open(CACHE, "w", encoding="utf-8", newline="").write(json.dumps(data, indent=1))
    print("\nwrote %s in %.0f s" % (os.path.relpath(CACHE, ROOT), time.time() - t0))
    return data


def load():
    if not os.path.exists(CACHE):
        return build()
    return json.load(io.open(CACHE, encoding="utf-8"))


SECTIONS = {"box": box_sweep, "method": method_compare, "threshold": threshold_sensitivity,
            "threshold_policy": threshold_policy, "anchor": anchor_compare,
            "accuracy": accuracy_vs_live}


def refresh(key):
    """Re-measure ONE section and merge it into the cache, leaving the rest untouched."""
    data = json.load(io.open(CACHE, encoding="utf-8"))
    data[key] = SECTIONS[key]()
    data["measured"] = time.strftime("%Y-%m-%d %H:%M")
    io.open(CACHE, "w", encoding="utf-8", newline="").write(json.dumps(data, indent=1))
    print("refreshed %r in %s" % (key, os.path.relpath(CACHE, ROOT)))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if len(sys.argv) > 1:
        if sys.argv[1] not in SECTIONS:
            sys.exit("unknown section %r; pick one of %s" % (sys.argv[1], ", ".join(SECTIONS)))
        refresh(sys.argv[1])
    else:
        build()
