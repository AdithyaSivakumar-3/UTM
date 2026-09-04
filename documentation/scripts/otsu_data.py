"""Where Otsu puts the cut on a real rig frame, measured — and what is quoted rather than measured.

WHAT THIS COMPUTES, and can be checked line by line:

    Otsu's chosen threshold on S13's saved stills, frame by frame, and the grey histogram those
    frames actually have. That is enough to show the MECHANISM: where Otsu's cut lands relative to
    the preset's fixed 149, and why the histogram puts it there.

WHAT THIS DOES NOT COMPUTE, deliberately:

    The marker-detection RATE. The rig's detect_blobs was driven directly here and returned 0 %
    on both settings, against a validated 99.8 % — the saved stills are stored transposed relative
    to the live camera feed, and the detector's masking, pair-choosing and separation checks are
    all orientation-dependent. Rather than reimplement the pipeline and quietly get it wrong (a
    hand-rolled contour filter scored the fixed threshold at 36.7 %, which is nonsense), the
    detection rates on the slide are QUOTED from the project's own replay validation
    (dic_replay.py, two full runs) and labelled as such.

    That distinction is the point: measured numbers here, cited numbers there, and never the two
    presented as the same kind of thing.
"""
import glob
import os
import sys

import numpy as np

try:
    import cv2
except ImportError:                                    # pragma: no cover
    cv2 = None

_HERE = os.path.dirname(os.path.abspath(__file__))
_APP = os.path.abspath(os.path.join(_HERE, "..", "..", "Software", "UTM_PyQt6"))
if _APP not in sys.path:
    sys.path.insert(0, _APP)

from camera_manager import CameraManager as _CM                       # noqa: E402

PRESET = _CM.SPECIMEN_PRESETS["Black"]
FIXED = float(PRESET["threshold"])

# The project's own replay validation, quoted. Source: the SPECIMEN_PRESETS["Black"] note in
# camera_manager.py, measured with dic_replay.py over two complete runs of saved frames.
REPLAY = [
    ("S29 · PETG", 48.5, 99.5, "the run that had to be abandoned"),
    ("S13 · black PLA", 99.8, 99.8, "Otsu happened to land inside the working band"),
]

FRAMES_GLOB = os.path.join(
    _APP, "Test data", "8.6.20 - Tensile test to Failure",
    "Specimen_S13_V2_Spray_Video7", "*", "frames", "f*.png")

_cache = {}


def frames(n=120):
    """A spread across the whole run, not the first n — the specimen changes as it pulls."""
    hits = sorted(glob.glob(FRAMES_GLOB))
    if not hits:
        raise SystemExit("no S13 frames found under %s" % FRAMES_GLOB)
    return hits[::max(1, len(hits) // n)][:n]


def load(n=120):
    if "rows" in _cache:
        return _cache
    rows, hist = [], np.zeros(256, float)
    for p in frames(n):
        g = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
        if g is None:
            continue
        t, _b = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        rows.append(dict(path=p, otsu=float(t), mean=float(g.mean()),
                         lo=int(g.min()), hi=int(g.max()),
                         above=float((g >= FIXED).mean() * 100.0)))
        hist += np.bincount(g.ravel(), minlength=256)
    o = np.array([r["otsu"] for r in rows])
    _cache.update(
        rows=rows, n=len(rows), hist=hist / hist.sum() * 100.0,
        otsu_med=float(np.median(o)), otsu_lo=float(o.min()), otsu_hi=float(o.max()),
        above_med=float(np.median([r["above"] for r in rows])),
        mean_grey=float(np.mean([r["mean"] for r in rows])),
        fixed=FIXED, sample=rows[len(rows) // 2]["path"])
    return _cache


def sample_frame():
    """One representative frame, as grey, for the picture on the slide."""
    d = load()
    return cv2.imread(d["sample"], cv2.IMREAD_GRAYSCALE)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    d = load()
    print("S13 black PLA — %d frames sampled across the run\n" % d["n"])
    print("  MEASURED HERE")
    print("    Otsu, recomputed per frame     : median %.0f   (range %.0f-%.0f)"
          % (d["otsu_med"], d["otsu_lo"], d["otsu_hi"]))
    print("    the Black preset's fixed cut   : %.0f" % d["fixed"])
    print("    gap between them               : %.0f grey levels" % (d["fixed"] - d["otsu_med"]))
    print("    frame mean grey                : %.1f" % d["mean_grey"])
    print("    pixels at or above the fixed cut: %.2f %%" % d["above_med"])
    print()
    print("  QUOTED from the project's replay validation (dic_replay.py, two full runs)")
    print("    %-18s %8s %10s" % ("", "Otsu", "fixed 149"))
    for nm, a, b, _why in REPLAY:
        print("    %-18s %7.1f %% %9.1f %%" % (nm, a, b))
