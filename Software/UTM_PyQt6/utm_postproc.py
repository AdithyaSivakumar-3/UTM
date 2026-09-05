"""DIC post-processing: measure strain from a RECORDED video, the same way the rig measures it live.

Point it at any video OpenCV can open, place two tracking boxes on the speckle (or on two sprayed
dots), and it reports separation in pixels and strain per frame — using utm_dic.dic_strain, the
same function the live camera path calls. Nothing about the strain maths is re-implemented here.

WHY THIS EXISTS
    Two uses. (1) Re-check our own recordings against what the rig reported live: same pull, same
    frames, an independent measurement path. (2) Measure specimens filmed on the MOT XT-205 video
    extensometer with OUR pixel-to-strain rule, so the two instruments can be compared on the same
    footing and the rig's offset factor can be quantified rather than assumed.

HOW THE TRACKING WORKS
    Each box is matched by normalised cross-correlation against its REFERENCE patch — not against
    the previous frame. Frame-to-frame tracking accumulates drift, and over a 1682-frame pull a
    drift of a fraction of a pixel per frame is a strain error larger than the strain being
    measured. Matching to the reference is drift-free by construction.

    The cost is that the patch must still resemble the reference late in the pull, which fails once
    the speckle around a marker deforms badly. So when peak correlation falls below `min_corr` the
    tracker re-seeds from the last good frame and FLAGS that frame. A flagged frame is reported,
    never silently blended in — the same principle as the live path's dropouts.

    Sub-pixel: a parabola through the correlation peak and its two neighbours, per axis. Without
    it, separation quantises to whole pixels and the strain trace looks like a staircase.

WHAT IS MEASURED
    The rig measures separation along the loading axis only — abs(dy) of the two centroids — and
    reports the perpendicular offset separately as dx_px. A recorded video may be rotated any way
    at all, so here the displacement is projected onto the axis of the REFERENCE pair. For an
    axis-aligned pair that is identical to the rig's abs(dy); for a rotated one it is the correct
    generalisation of it. The perpendicular component is reported as dx_px, as on the rig.

FRAME RATE IS AN INPUT, NOT AN ASSUMPTION
    A container's fps field is metadata, and it is often wrong. S26's video.avi declares 35 fps
    while the capture index proves it recorded 1682 frames in 84.4 s = 19.93 fps — a 1.75x error
    that would silently stretch the whole time axis. fps is therefore a parameter; the file's
    value is only the default, and `fps_warning()` says when it looks implausible.
"""
import io
import os
import time
from dataclasses import dataclass, field, replace

import numpy as np

try:
    import cv2
except ImportError:                                    # pragma: no cover - cv2 always present in the app
    cv2 = None

from utm_dic import dic_strain, px_per_mm


@dataclass
class Box:
    """A square tracking patch, by centre and half-size, in frame pixels."""
    cx: float
    cy: float
    half: int = 24

    def clamp(self, w, h):
        self.cx = float(min(max(self.cx, self.half + 1), w - self.half - 2))
        self.cy = float(min(max(self.cy, self.half + 1), h - self.half - 2))
        return self

    def patch(self, gray):
        x, y, r = int(round(self.cx)), int(round(self.cy)), self.half
        return gray[y - r:y + r + 1, x - r:x + r + 1]


@dataclass
class Settings:
    gauge_mm: float = 80.0        # physical distance between the two boxes, for px/mm only
    # Has anyone actually said this gauge is right for THIS video? False means it is the default
    # or a value carried over from another run. It changes no arithmetic; it changes what the
    # results sheet claims, which is the part that misled a reader once already.
    gauge_confirmed: bool = False
    # WHERE a confirmed gauge came from — "typed", "measured from px/mm", "measured from
    # video.csv calibration"… Display-only provenance for the results sheet; no arithmetic
    # reads it. Empty when unconfirmed (the ASSUMED stamp is the provenance then).
    gauge_src: str = ""
    box_half: int = 24            # patch half-size
    search: int = 40              # how far a box may move between reference and current frame
    min_corr: float = 0.55        # below this the match is not trusted
    ref_frame: int = 0            # which frame defines L0
    fps: float = 0.0              # 0 = take the container's value
    step: int = 1                 # analyse every Nth frame
    # "auto"        correlate to find the patch, then refine on the marker centroid when the
    #               patch holds one. Best of both: correlation survives large motion, the
    #               centroid gives the rig's precision on a dot.
    # "correlation" correlation only — the honest choice for a speckle pattern, which has no
    #               marker to take a centroid of.
    # "rig"         the marker centroid computed exactly as camera_manager does it: a plain
    #               binary contour centroid. Noisier, and that is the point — it removes the
    #               estimator as a variable when post-processing is compared against a live run
    #               or against the extensometer.
    refine: str = "auto"
    # Stop as soon as tracking is lost, rather than carrying on past it. Two CONSECUTIVE analysed
    # frames rather than one: a row is only marked lost when the reference patch AND the re-seeded
    # patch both fail, so a single one is already a strong signal — but a lone frame can still dip
    # under min_corr on a flicker, and aborting a good run for one flickering frame is worse than
    # carrying two useless rows that are dropped anyway.
    stop_on_loss: bool = True
    loss_tolerance: int = 2
    # After the markers are declared lost, keep decoding for this long, attempting a full-frame
    # re-acquisition each frame — a snap can throw the specimen sideways past any local search
    # window while leaving it perfectly trackable (S38 lost 4.2 s of video this way). A marker
    # that is genuinely gone never re-acquires and the run still stops, just this much later.
    loss_grace_s: float = 4.0
    # A still image to use as the reference frame instead of the video's own frame `ref_frame`.
    # The zero has to be a frame with the specimen at rest, and a recording does not always hold
    # one. Must match the video's dimensions — see reference_gray().
    ref_image: str = ""


@dataclass
class FrameResult:
    idx: int
    t: float
    a: tuple
    b: tuple
    l_px: float
    dx_px: float
    cauchy: float
    true: float
    corr: float
    ok: bool
    note: str = ""
    # One entry per EXTRA tracked pair (see analyse(extras=...)): (ax, ay, bx, by, l_px,
    # strain, ok). `strain` is (l - l0)/l0 along that pair's own axis — for a transverse pair
    # that IS the lateral strain, negative in tension as the width shrinks.
    extra: tuple = ()


@dataclass
class Summary:
    n: int = 0
    tracked: int = 0
    reseeds: int = 0
    centroid_frames: int = 0     # frames measured by marker centroid rather than correlation
    l0_px: float = 0.0
    px_mm: float = None
    fps: float = 0.0
    rows: list = field(default_factory=list)
    # Set when the run was CUT SHORT because the markers were lost, rather than because the video
    # ended. None means the run reached the end of the file.
    lost_at_frame: int = None
    lost_at_t: float = None
    lost_reason: str = ""
    data_ends_t: float = None      # t of the last row kept, i.e. where the plot stops
    # The strain the specimen already carried at the preload instant, when a companion load
    # channel says where that was. None means the noise window has to find its own zero.
    strain_zero: float = None
    strain_zero_note: str = ""
    # Per EXTRA pair: {"label", "kind" ("axial"|"transverse"), "l0_px", "tracked", "n",
    # "centroid_frames", "reseeds"} in the order the pairs were given to analyse().
    extras: list = field(default_factory=list)

    @property
    def stopped_early(self):
        return self.lost_at_frame is not None

    @property
    def coverage(self):
        return 100.0 * self.tracked / self.n if self.n else 0.0


def probe(path):
    """What the file says about itself. Never trusted for fps — see the module docstring."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise IOError("cannot open video: %s" % path)
    info = {"frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "fps": float(cap.get(cv2.CAP_PROP_FPS) or 0.0),
            "w": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "h": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "name": os.path.basename(path)}
    cap.release()
    info["duration_s"] = info["frames"] / info["fps"] if info["fps"] > 0 else 0.0
    return info


def true_fps_from_sidecar(video_path):
    """The MEASURED frame rate for one of our own captures, or None.

    A container's fps field is what the writer claimed, not what the camera did. Our capture
    folders record the truth beside the video: frames/index.csv timestamps every frame, and
    run.json brackets the recording with captured_from/captured_to. S26 declares 35 fps and
    actually ran at 19.93 — believing the container would stretch its whole time axis by 1.76x.

    Returns (fps, source, n_frames) so the UI can say WHERE the number came from, or None when
    the video has no sidecar (anything filmed on the extensometer, or any other camera).
    """
    d = os.path.dirname(os.path.abspath(video_path))
    idx = os.path.join(d, "frames", "index.csv")
    if os.path.isfile(idx):
        try:
            import csv as _csv
            import datetime as _dt
            with open(idx, encoding="utf-8") as fh:
                rows = list(_csv.DictReader(fh))
            if len(rows) > 1:
                t0 = _dt.datetime.fromisoformat(rows[0]["pc_time_iso"])
                t1 = _dt.datetime.fromisoformat(rows[-1]["pc_time_iso"])
                span = (t1 - t0).total_seconds()
                if span > 0:
                    return (len(rows) - 1) / span, "frames/index.csv timestamps", len(rows)
        except Exception:
            pass
    rj = os.path.join(d, "run.json")
    if os.path.isfile(rj):
        try:
            import json as _json
            import datetime as _dt
            with open(rj, encoding="utf-8") as fh:
                m = _json.load(fh)
            t0 = _dt.datetime.fromisoformat(m["captured_from"])
            t1 = _dt.datetime.fromisoformat(m["captured_to"])
            span = (t1 - t0).total_seconds()
            n = probe(video_path)["frames"]
            if span > 0 and n > 1:
                return (n - 1) / span, "run.json capture window", n
        except Exception:
            pass
    return None


def scale_from_sidecar(video_path):
    """The rig's own DIC calibration for one of OUR captures: (px_per_mm, gauge_mm, source_name),
    or None. Same idea as true_fps_from_sidecar, for the OTHER number a foreign video lacks.

    A capture folder's CSV header records "# DIC Calibration - px_per_mm:" and the gauge the
    session ran with. Reading it at load time is what lets the gauge box MEASURE the picked pair
    instead of assuming 80 mm — px alone carry no mm, so this is the one legitimate way the
    warning can retire itself.

    Only a folder that is demonstrably one of ours is trusted: run.json or frames/ must sit
    beside the video. A flat folder of several exports (the MOT directory holds three samples'
    CSVs side by side) must never anchor a video to a neighbouring sample's calibration.
    """
    d = os.path.dirname(os.path.abspath(video_path))
    if not (os.path.isfile(os.path.join(d, "run.json"))
            or os.path.isdir(os.path.join(d, "frames"))):
        return None
    import glob as _glob
    import re as _hre
    cands = sorted(_glob.glob(os.path.join(d, "*.csv"))
                   + _glob.glob(os.path.join(os.path.dirname(d), "*.csv")),
                   key=lambda p: -os.path.getmtime(p))
    cands = [p for p in cands if os.path.basename(p) != "index.csv"]
    fallback = None
    for path in cands:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                head = [next(fh, "") for _ in range(60)]
        except OSError:
            continue
        ppm = gauge = None
        for ln in head:
            if not ln.startswith("#"):
                continue
            m = _hre.search(r"px_per_mm[:\s]+([0-9]+(?:\.[0-9]+)?)", ln)
            if m:
                ppm = float(m.group(1))
            m = _hre.search(r"[Gg]auge\s*[Ll]ength\D*?([0-9]+(?:\.[0-9]+)?)", ln)
            if m:
                gauge = float(m.group(1))
        if ppm:
            return ppm, gauge, os.path.basename(path)
        if gauge and fallback is None:
            fallback = (None, gauge, os.path.basename(path))
    return fallback


def fps_warning(info, known_duration_s=None):
    """A sentence when the declared fps looks wrong, else ''."""
    fps = info.get("fps") or 0.0
    if fps <= 0:
        return "This file declares no frame rate — set it by hand, or the time axis is meaningless."
    if known_duration_s and known_duration_s > 0:
        real = info["frames"] / known_duration_s
        if abs(real - fps) / fps > 0.05:
            return ("The file declares %.2f fps, but %d frames over %.1f s is %.2f fps. "
                    "Using the declared value would scale the time axis by %.2fx."
                    % (fps, info["frames"], known_duration_s, real, fps / real))
    if fps > 120 or fps < 1:
        return "Declared %.2f fps is implausible for this rig — check it before trusting time." % fps
    return ""


def fps_is_suspect(fps, verified):
    """Is this frame rate one that should stop a run rather than merely warn?

    A round number at or above 100 fps is the signature of a container field nobody filled in:
    1000, 500 and 240 all appear in the wild and none of them is what a tensile rig records.
    The XT-205's export declares 1000 fps and actually ran at 19.864 — a 50x error that reaches
    every time output while leaving the strain untouched, which is exactly the kind of fault that
    survives a review because the headline number still looks right.
    """
    if verified:
        return ""
    if fps <= 0:
        return "no frame rate at all"
    if fps >= 100 and abs(fps - round(fps)) < 1e-6:
        return "%.0f fps is a round number over 100 — almost certainly a container default" % fps
    if fps > 120:
        return "%.2f fps is faster than this rig has ever recorded" % fps
    if fps < 1:
        return "%.4f fps is slower than any real recording" % fps
    return ""


# ---------------------------------------------------------------------------------------------
#  COMPANION DATA FILE
#
#  A video that this rig recorded has a capture folder beside it and needs none of this. A video
#  from anywhere else arrives with nothing, and three separate things then have to be guessed:
#  the frame rate, the gauge length, and where the specimen was actually loaded. All three were
#  guessed wrong on the first foreign video this dialog was given (MOT session 2, 2026-09-03):
#  1000 fps instead of 19.864, 80 mm instead of 45.0034, and a noise window that landed inside the
#  preload ramp.
#
#  Every one of those is answerable from the acquisition file that came WITH the video. So rather
#  than three separate guards, the dialog can be handed that file once.
# ---------------------------------------------------------------------------------------------
_T_NAMES = ("t", "time", "time_s", "seconds", "sec", "timestamp", "elapsed")
_F_NAMES = ("f", "force", "load", "force_n", "load_n", "n", "kn", "force (n)", "load (n)")
_G_NAMES = ("gauge", "gauge length", "gauge_mm", "gauge length (units)", "l0")


@dataclass
class Companion:
    """The acquisition record that came with a foreign video, as far as it can be read.

    Only `t` is required. Everything else is optional and absent rather than invented: a headerless
    .daq gives a time base and nothing more, and a time base alone already fixes the frame rate.
    """
    path: str = ""
    source: str = ""
    n_rows: int = 0
    t: object = None                 # np.ndarray, seconds
    load: object = None              # np.ndarray, newtons, or None
    gauge_mm: float = None           # if the file reports one
    px_per_mm: float = None          # the rig's own DIC calibration, from the CSV header
    columns: list = field(default_factory=list)
    note: str = ""

    @property
    def duration_s(self):
        if self.t is None or len(self.t) < 2:
            return 0.0
        return float(self.t[-1] - self.t[0])


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def companion_columns(path):
    """(names, n_columns, n_rows) for a file, so a caller can offer a column to pick.

    A headerless acquisition log — the XT-205 writes a 52-column .daq with none of them labelled —
    cannot be read by name, and its load channel is not something this module will guess at. What
    it can do is say what is in there and let a person choose.
    """
    try:
        c = read_companion(path)
    except ValueError:
        return [], 0, 0
    import csv as _csv
    with io.open(path, encoding="utf-8-sig", errors="replace") as _fh:
        raw = _fh.read().splitlines()
    body = [ln for ln in raw if ln.strip() and not ln.lstrip().startswith("#")]
    sep = "\t" if body[0].count("\t") >= max(1, body[0].count(",")) else ","
    width = max(len(r) for r in list(_csv.reader(body[:50], delimiter=sep)))
    return c.columns, width, c.n_rows


def read_companion(path, load_col=None, load_scale=1.0):
    """Read a rig CSV, a foreign CSV, or a tab-separated .daq into a Companion.

    `load_col` names a column index to use as load when the file has no usable header — the
    XT-205's .daq carries its force in column 4, in kN, and labels nothing. `load_scale` converts
    it to newtons (1000 for kN).

    Deliberately forgiving about layout and deliberately strict about naming: a column is used as
    LOAD or GAUGE only when its header says so. Guessing a load column by its shape is a judgement
    that belongs in an analysis script, not in a dialog that will quietly apply it to the next file
    as well.

    Raises ValueError with a readable reason when there is no usable time column.
    """
    import csv as _csv
    with io.open(path, encoding="utf-8-sig", errors="replace") as _fh:
        raw = _fh.read().splitlines()
    body = [ln for ln in raw if ln.strip() and not ln.lstrip().startswith("#")]
    if not body:
        raise ValueError("the file has no data rows")

    # Our own rig's CSVs carry the session's DIC calibration and gauge in "#" header lines
    # ("# DIC Calibration - px_per_mm: 20.8528", "# ... Gauge Length: 80.0 mm ..."). A scale
    # read here lets the dialog anchor to px/mm automatically, so on a multi-marker specimen
    # the gauge box simply MEASURES whichever pair is picked - no typing.
    import re as _hre
    hdr_ppm = hdr_gauge = None
    for ln in raw[:40]:
        if not ln.lstrip().startswith("#"):
            continue
        m = _hre.search(r"px_per_mm[:\s]+([0-9]+(?:\.[0-9]+)?)", ln)
        if m:
            hdr_ppm = float(m.group(1))
        m = _hre.search(r"[Gg]auge\s*[Ll]ength\D*?([0-9]+(?:\.[0-9]+)?)", ln)
        if m:
            hdr_gauge = float(m.group(1))

    sep = "\t" if body[0].count("\t") >= max(1, body[0].count(",")) else ","
    rows = list(_csv.reader(body, delimiter=sep))

    # A header row is one whose first cell will not parse as a number. MOT's export has TWO: names
    # then units, and the units row is where "Gauge length (units)" actually lives.
    head, first_data = [], 0
    for i, r in enumerate(rows[:3]):
        if r and _num(r[0]) is None:
            head.append([c.strip() for c in r])
            first_data = i + 1
        else:
            break
    names = []
    if head:
        width = max(len(h) for h in head)
        for c in range(width):
            parts = [h[c] for h in head if c < len(h) and h[c]]
            names.append(" ".join(parts).strip().lower())

    data = []
    for r in rows[first_data:]:
        vals = [_num(c) for c in r]
        if vals and vals[0] is not None:
            data.append(vals)
    if len(data) < 2:
        raise ValueError("fewer than two numeric rows")
    width = max(len(r) for r in data)
    cols = [np.array([(r[c] if c < len(r) and r[c] is not None else np.nan) for r in data], float)
            for c in range(width)]

    def find(cands):
        """The first column whose header contains one of these names as a WHOLE WORD.

        Not a prefix test: a real export labels its columns for a human, so the MOT strain file
        calls its gauge column "Extensometer 1 Gauge length (units)" and a prefix rule misses it
        entirely — which is how a 45 mm specimen came to be analysed as 80 mm even though the
        gauge was sitting in the file all along. Whole-word rather than plain substring so that
        "load" does not match "unloaded" and "n" does not match every column in the sheet.
        """
        import re as _re
        for cand in cands:                       # candidate order is the priority order
            pat = _re.compile(r"(?<![a-z0-9_])" + _re.escape(cand) + r"(?![a-z0-9_])")
            for i, nm in enumerate(names):
                if pat.search(nm):
                    return i
        return None

    i_t = find(_T_NAMES)
    if i_t is None:
        # Unnamed columns: column 0 is the time base on every acquisition file this project has
        # seen, and it is checked for monotonicity before being believed.
        i_t = 0
    t = cols[i_t]
    if not np.all(np.diff(t[np.isfinite(t)]) >= 0):
        raise ValueError("column %d is not monotonic, so it is not a time base" % i_t)
    if np.nanmax(t) - np.nanmin(t) <= 0:
        raise ValueError("the time column does not advance")

    load = None
    if load_col is not None and 0 <= int(load_col) < width:
        load = cols[int(load_col)] * float(load_scale)
    else:
        i_f = find(_F_NAMES)
        if i_f is not None:
            load = cols[i_f]
            # kN is common on commercial machines; a channel that never exceeds 50 is not newtons
            # on a specimen this rig can break.
            if names[i_f].endswith("kn") or "(kn)" in names[i_f]:
                load = load * 1000.0

    gauge = None
    i_g = find(_G_NAMES)
    if i_g is not None:
        vals = cols[i_g][np.isfinite(cols[i_g])]
        if len(vals):
            g = float(np.median(vals))
            if 1.0 < g < 1000.0:
                gauge = g

    got = []
    if load is not None:
        got.append("load")
    if gauge is not None:
        got.append("gauge %.4f mm" % gauge)
    return Companion(
        path=path, source=os.path.basename(path), n_rows=len(data), t=t, load=load,
        gauge_mm=(gauge if gauge else hdr_gauge), px_per_mm=hdr_ppm,
        columns=names,
        note=("%d rows over %.3f s" % (len(data), float(t[-1] - t[0]))
              + ("; " + ", ".join(got) if got else "; time only")))


def fps_from_companion(info, comp):
    """(fps, sentence) taken from the companion's own duration, or None.

    The frame count is the video's and the duration is the acquisition's, which is the whole point:
    neither file can state the frame rate on its own, and together they cannot avoid it.
    """
    if comp is None or comp.duration_s <= 0:
        return None
    n = info.get("frames") or 0
    if n < 2:
        return None
    fps = (n - 1) / comp.duration_s
    declared = info.get("fps") or 0.0
    if declared > 0 and abs(fps - declared) / declared > 0.02:
        return round(fps, 4), (
            "Using %.4f fps: %d frames over the %.3f s in %s. The file itself declares %.2f fps — "
            "believing it would scale the time axis by %.2f×."
            % (fps, n, comp.duration_s, comp.source, declared, declared / fps))
    return round(fps, 4), ("Frame rate %.4f fps confirmed against %s (%d frames, %.3f s)."
                           % (fps, comp.source, n, comp.duration_s))


def preload_strain_zero(rows, comp, preload_n=None, frac=0.90):
    """The strain the specimen already carried when the preload was reached. (e0, sentence).

    WHY THIS EXISTS. The noise and strain-rate window is a band of STRAIN, and a band of strain is
    only meaningful relative to a zero. The reference frame is usually the video's first, which on
    a foreign recording can be minutes before the specimen is loaded at all — so the 0.05-0.35 %
    band lands inside the seating ramp and measures the specimen bedding in rather than the
    instrument's noise. On MOT session 2 that read 57 ue where the settled record gives 24.

    With a load channel the fix is exact: find where the load first reaches the preload, and take
    the strain there as the working zero. Returns (0.0, "") when there is no load to use.
    """
    if comp is None or comp.load is None or not rows:
        return 0.0, ""
    t = np.array([r.t for r in rows], float)
    e = np.array([r.cauchy for r in rows], float)
    ct, cf = comp.t, comp.load
    ok = np.isfinite(ct) & np.isfinite(cf)
    ct, cf = ct[ok], cf[ok]
    if len(ct) < 5:
        return 0.0, ""
    target = preload_n if preload_n else frac * float(np.nanmax(cf))
    hit = np.nonzero(cf >= target)[0]
    if not len(hit):
        return 0.0, ""
    t_pre = float(ct[hit[0]])
    # The video clock starts at the reference frame; the companion's starts where it starts. They
    # share an origin only when the companion covers the whole recording, which is the case that
    # matters — anything else is reported rather than silently corrected.
    if t_pre < t.min() or t_pre > t.max():
        return 0.0, ("The preload instant (%.2f s) falls outside the analysed frames (%.2f-%.2f s), "
                     "so the noise window was not re-anchored." % (t_pre, t.min(), t.max()))
    e0 = float(np.interp(t_pre, t, e))
    return e0, ("Noise and rate re-zeroed at %.0f N, reached at %.2f s, where the strain already "
                "read %.4f %%." % (target, t_pre, e0 * 100.0))


def _grab(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise IOError("cannot open video: %s" % path)
    return cap


# Files whose seek cannot be trusted, and one open capture each for walking them.
# Keyed by path; holds (capture, next_frame_index). Kept because a sequential fallback that
# re-opened the file for every scrub step would make the slider unusable on a long video.
_SEQ = {}
_SEEK_OK = {}


def _seek_is_trustworthy(path):
    """Does this file return the frame you ask for? Measured once, then remembered.

    Asks for a frame well into the file and checks the decoder ended up where it said it would.
    A container can report a frame count far larger than it holds, so the probe index is kept
    small enough to exist in almost any real recording.
    """
    if path in _SEEK_OK:
        return _SEEK_OK[path]
    ok = True
    try:
        # Deep enough to matter: this file seeks CORRECTLY for the first ~40 frames and only starts
        # returning stale pictures past ~80, so a shallow probe passes and learns nothing.
        probe = 120
        # Decode to `probe` the slow, always-correct way. Forty frames is cheap and it is the only
        # answer that can be trusted: the position PROPERTY is no use here, because the file that
        # motivated this reports position 41 perfectly correctly while handing back frame 0's
        # picture. Content is the only thing that reveals it.
        # grab() decodes without handing the frame back, which is three times cheaper than read()
        # on a 2464x2056 file — 0.7 s instead of 2.0 s. Only the probe frame is retrieved.
        cap = cv2.VideoCapture(path)
        for _ in range(probe):
            if not cap.grab():
                cap.release()
                _SEEK_OK[path] = True       # too short to judge; leave seeking alone
                return True
        got, truth = cap.read()
        cap.release()
        if not got:
            _SEEK_OK[path] = True
            return True

        cap = cv2.VideoCapture(path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, probe)
        got, seek_fr = cap.read()
        cap.release()
        if got and truth is not None and seek_fr.shape == truth.shape:
            d = float(np.abs(seek_fr.astype(np.int16) - truth.astype(np.int16)).mean())
            ok = d < 0.5                     # identical frames differ by exactly zero
    except Exception:
        ok = True                       # never let a probe failure disable ordinary playback
    _SEEK_OK[path] = ok
    return ok


def _read_sequential(path, idx):
    """Decode forward to `idx`, reusing the open capture when we are already before it."""
    ent = _SEQ.get(path)
    if ent is None or ent[1] > idx:      # asked to go backwards: start again
        if ent is not None:
            ent[0].release()
        cap = cv2.VideoCapture(path)
        ent = [cap, 0]
        _SEQ[path] = ent
    cap, pos = ent
    frame = None
    while pos <= idx:
        got, fr = cap.read()
        if not got:
            ent[1] = pos
            return None
        frame = fr
        pos += 1
    ent[1] = pos
    return frame


def reference_image(path):
    """A still, as greyscale, or None. Any format cv2 can read."""
    if not path or not os.path.exists(path):
        return None
    g = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    return g


# How much LARGER than the video a reference image may be and still be usable. Generous enough for
# an encoder rounding the width down to an even number — which is exactly what happens to our own
# captures, 419 px of ROI written as a 418 px AVI — and far too small to let an arbitrarily
# different crop through.
REF_SIZE_TOLERANCE = 8


def reference_align(img_path, video_path, ref_frame=0):
    """Fit a reference image onto the video's coordinate system.

    Returns (gray, (ox, oy), note) on success, or (None, None, why) when it cannot be done.

    Equal sizes are taken as they are. An image up to REF_SIZE_TOLERANCE pixels LARGER is cropped
    to the video's frame, with the offset found by matching against a real frame rather than
    assumed: rounding down from the top-left is what this encoder does, but that is a library's
    behaviour, and library behaviour taken on trust has already produced two wrong answers in this
    project. A smaller image is refused, because the missing pixels cannot be invented.

    What is deliberately NOT enforced is that the picture LOOKS like the video. A reference may
    legitimately be a separate photograph of the unloaded specimen, which will not match frame 0 at
    all; the operator judges that by eye, and the tab shows the image so it can be judged.
    """
    g = reference_image(img_path)
    if g is None:
        return None, None, "that file could not be read as an image"
    try:
        info = probe(video_path)
    except Exception as e:
        return None, None, "the video could not be probed: %s" % e

    vw, vh = info["w"], info["h"]
    ih, iw = g.shape[0], g.shape[1]
    if (iw, ih) == (vw, vh):
        return g, (0, 0), ""
    if iw < vw or ih < vh:
        return None, None, ("the image is %d x %d, SMALLER than the video's %d x %d. The missing "
                            "pixels cannot be invented, and Px\u2080 must be measured in the "
                            "video's own coordinates." % (iw, ih, vw, vh))
    dw, dh = iw - vw, ih - vh
    if dw > REF_SIZE_TOLERANCE or dh > REF_SIZE_TOLERANCE:
        return None, None, ("the image is %d x %d and the video %d x %d — too different to line up. "
                            "Px\u2080 and every later separation are measured in frame pixels, so "
                            "the two must share a coordinate system." % (iw, ih, vw, vh))

    # Which offset? Ask the pictures. Falls back to the top-left if the video will not read.
    best, frame = (0, 0), read_frame(video_path, int(ref_frame))
    if frame is not None and frame.shape[0] >= vh and frame.shape[1] >= vw:
        import numpy as _np
        score = None
        for oy in range(dh + 1):
            for ox in range(dw + 1):
                crop = g[oy:oy + vh, ox:ox + vw]
                if crop.shape != (vh, vw):
                    continue
                d = float(_np.abs(crop.astype(_np.int16) - frame.astype(_np.int16)).mean())
                if score is None or d < score:
                    score, best = d, (ox, oy)
        note = ("the image is %d x %d and the video %d x %d — a video writer rounds the width down "
                "to an even number. Cropped at x+%d, y+%d, which matches frame %d to %.1f grey "
                "levels." % (iw, ih, vw, vh, best[0], best[1], int(ref_frame), score or 0.0))
    else:
        note = ("the image is %d x %d and the video %d x %d; cropped at the top-left (the video "
                "frame could not be read to check the alignment)." % (iw, ih, vw, vh))
    ox, oy = best
    return g[oy:oy + vh, ox:ox + vw], best, note


def reference_mismatch(img_path, video_path, ref_frame=0):
    """Why this image cannot serve as `video_path`'s reference, or "" if it can."""
    _g, _off, note = reference_align(img_path, video_path, ref_frame)
    return "" if _g is not None else note


def read_frame(path, idx):
    """One frame as greyscale — for the UI preview and for placing the boxes.

    Verifies that this file's seek actually works, and walks the file instead when it does not.
    A preview showing a different frame from the one requested is worse than a slow preview: the
    reference frame, the marker detection and Px0 all come from whatever this returns.
    """
    idx = int(idx)
    if _seek_is_trustworthy(path):
        cap = _grab(path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        cap.release()
        if not ok:
            return None
    else:
        frame = _read_sequential(path, idx)
        if frame is None:
            return None
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if frame.ndim == 3 else frame


def seek_warning(path):
    """A line for the UI when this file needs walking rather than seeking, else ""."""
    if _seek_is_trustworthy(path):
        return ""
    return ("This file does not support seeking reliably, so frames are decoded in order. "
            "Scrubbing forward is normal speed; jumping backwards re-reads from the start.")


def find_markers(gray, min_area=300, max_area=200000, min_circ=0.45, dedupe_px=25.0):
    """Every round blob in the frame, at either polarity. [(cx, cy, radius, circ)], best first.

    Used for two things that must agree: Auto-detect, which wants exactly two, and click-to-snap,
    which wants the one nearest the cursor. One finder means a marker cannot be good enough to
    auto-detect but invisible to the snap, or the reverse.

    Both polarities are swept because the rig runs both — dark sprayed dots on white PLA, and
    bright dots on dark TPU — and a post-processed video carries no setting to say which. Several
    thresholds are tried because one fixed value does not survive a change of lighting; blobs
    found more than once are collapsed by proximity so a marker seen at four thresholds counts as
    one marker, ranked by its best circularity.
    """
    import cv2 as _cv
    found = []
    for mode in (_cv.THRESH_BINARY_INV, _cv.THRESH_BINARY):
        for thr in (90, 110, 130, 150, 170, 190, 210):
            _, b = _cv.threshold(gray, thr, 255, mode)
            contours, _ = _cv.findContours(b, _cv.RETR_EXTERNAL, _cv.CHAIN_APPROX_SIMPLE)
            for c in contours:
                area = _cv.contourArea(c)
                per = _cv.arcLength(c, True)
                if per <= 0 or not (min_area < area < max_area):
                    continue
                circ = 4 * np.pi * area / (per * per)
                if circ < min_circ:
                    continue
                M = _cv.moments(c)
                if M["m00"] <= 0:
                    continue
                found.append((M["m10"] / M["m00"], M["m01"] / M["m00"],
                              float(np.sqrt(area / np.pi)), float(circ)))
    found.sort(key=lambda m: -m[3])
    out = []
    for m in found:
        if all(np.hypot(m[0] - o[0], m[1] - o[1]) > dedupe_px for o in out):
            out.append(m)
    return out


def reference_threshold(patch, dark=True):
    """One grey level for a marker, chosen once from its reference patch.

    Fixed rather than recomputed per frame, for REPRODUCIBILITY rather than precision: the level
    then depends only on the reference frame, so re-running the same video cannot produce a
    different answer because a later frame's histogram drifted.

    It is worth being straight about what this does not buy. Measured over a fixed frame window,
    a per-frame Otsu centroid comes out at 18.2 microstrain on S25 and 11.2 on S26, against 18.5
    and 11.5 for a level fixed once — the same within 2 %. The choice is not what makes the
    centroid quiet; the intensity weighting in centroid_refine is, and it is precisely because
    that weighting uses the edge PROFILE rather than where the threshold cuts that the level stops
    mattering much. An earlier note here claimed a factor of six in favour of the fixed level.
    That was an artefact of a noise window each configuration chose from its own strain estimate,
    and it is withdrawn.
    """
    thr, _ = cv2.threshold(patch, 0, 255,
                           (cv2.THRESH_BINARY_INV if dark else cv2.THRESH_BINARY) | cv2.THRESH_OTSU)
    return float(thr)


def centroid_refine(gray, cx, cy, half, dark=True, thr=None, min_frac=0.02, max_frac=0.9,
                    weighted=True):
    """Re-locate a round marker by its intensity CENTROID, the way the live rig does.

    Correlation is what FINDS a patch that has moved; it is not the most dependable way to pin
    down where a large uniform dot is. Its peak on a flat disc is broad, so sub-pixel position
    comes from a poorly-conditioned parabola, and how well that behaves varies with the specimen:
    over a fixed frame window, correlation alone gives 25.8 microstrain on S25 but 11.0 on S26.
    The centroid averages every pixel of the disc instead of reading one peak, and lands at 18.4
    and 11.3 — best or tied-best on both, which is the property worth having.

    Threshold is Otsu WITHIN the patch, not a fixed global level: the patch is mostly dot and
    surround, which is exactly the bimodal case Otsu is for, and it follows lighting drift down
    the specimen for free.

    Returns (cx, cy, area) or None when the patch holds nothing that looks like a marker — in
    which case the caller keeps the correlation result rather than inventing a position.
    """
    h, w = gray.shape
    r = int(half)
    x0, y0 = int(round(cx)) - r, int(round(cy)) - r
    x1, y1 = x0 + 2 * r + 1, y0 + 2 * r + 1
    if x0 < 0 or y0 < 0 or x1 > w or y1 > h:
        return None
    patch = gray[y0:y1, x0:x1]
    mode = cv2.THRESH_BINARY_INV if dark else cv2.THRESH_BINARY
    if thr is None:                       # no reference level available — Otsu, and noisier for it
        _, b = cv2.threshold(patch, 0, 255, mode | cv2.THRESH_OTSU)
    else:
        _, b = cv2.threshold(patch, thr, 255, mode)
    contours, _ = cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    n = patch.size
    best, best_c, best_d = None, None, None
    mid = float(r)
    for c in contours:
        a = cv2.contourArea(c)
        if not (min_frac * n < a < max_frac * n):
            continue
        M = cv2.moments(c)
        if M["m00"] <= 0:
            continue
        px, py = M["m10"] / M["m00"], M["m01"] / M["m00"]
        # The marker is the blob nearest the patch centre; anything else in view is not it.
        d = (px - mid) ** 2 + (py - mid) ** 2
        if best_d is None or d < best_d:
            best, best_c, best_d = (px, py, a), c, d
    if best is None or best_d > (0.6 * r) ** 2:
        return None

    # ---- INTENSITY-WEIGHTED centre, inside the contour that was just selected.
    #
    # A binary centroid weights every pixel inside the threshold equally, so where the threshold
    # cuts through the marker's soft edge decides the answer: move the level and the contour grows
    # on whichever side is darker, taking the centre with it. Sweeping the level 120-190 on the
    # reference frame moves a binary centre by 0.221 px on S25 and 0.932 px on S26 — 132 and 556
    # microstrain of L0, both larger than the whole measurement's noise floor.
    #
    # Weighting by how dark each pixel is uses the edge PROFILE instead of guessing where the edge
    # ends, and the same sweep then moves the centre only 0.091 px (54 ue) and 0.372 px (222 ue).
    # The contour still SELECTS which blob is the marker — dropping that is what makes a plain
    # grey-weighted centroid fragile, because anything else dark in the patch pulls on it.
    #
    # Measured over a window fixed in frame numbers so every estimator is scored over the same
    # slice of the test (documentation/estimator_measurements.json):
    #
    #     estimator            S25 noise   S26 noise   threshold sweep (S25 / S26)
    #     correlation only      25.8 ue     11.0 ue         --
    #     binary contour        25.2 ue     20.5 ue      132 / 556 ue
    #     contour + weighting   18.4 ue     11.3 ue       54 / 222 ue
    #
    # against 28.2 / 28.9 ue for the live rig, which uses the binary form. All three agree on L0
    # to 0.9 px and on peak strain to 0.05 %, so the estimator sets PRECISION, not the value.
    if not weighted:
        # Rig-matched: the plain binary centroid, so a comparison against a live run differs by
        # physics rather than by estimator.
        return (x0 + best[0], y0 + best[1], best[2])
    mask = np.zeros(patch.shape, np.uint8)
    cv2.drawContours(mask, [best_c], -1, 255, cv2.FILLED)
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))     # take in the soft edge, where the information is
    outside = patch[mask == 0]
    bg = float(np.median(outside)) if outside.size else float(patch.max())
    pf = patch.astype(np.float32)
    w = np.where(mask > 0, (bg - pf) if dark else (pf - bg), 0.0)
    np.clip(w, 0, None, out=w)
    tot = float(w.sum())
    if tot > 1e-6:
        ys, xs = np.mgrid[0:patch.shape[0], 0:patch.shape[1]]
        return (x0 + float((xs * w).sum() / tot), y0 + float((ys * w).sum() / tot), best[2])
    return (x0 + best[0], y0 + best[1], best[2])


def snap_to_marker(markers, x, y, max_dist=None):
    """The marker centre nearest (x, y), or None if nothing is close enough.

    Clicking the exact centre of a dot by eye is guesswork, and the centre is what sets L0 — so a
    click near a marker should mean that marker's centroid, computed, not the pixel the cursor
    happened to be over. Falls back to None on a speckle pattern, which has no discrete markers
    and must stay free-placed.
    """
    if not markers:
        return None
    best = min(markers, key=lambda m: np.hypot(m[0] - x, m[1] - y))
    d = float(np.hypot(best[0] - x, best[1] - y))
    limit = max_dist if max_dist is not None else max(30.0, best[2] * 2.5)
    return (best[0], best[1], d, best) if d <= limit else None


def _subpixel(corr, mx, my):
    """Parabola through the correlation peak and its neighbours, per axis.

    Without this the peak is an integer pixel, separation quantises to 1 px, and on a 1600 px
    gauge that is a 625 microstrain staircase — coarser than the rig's own noise floor.
    """
    dx = dy = 0.0
    h, w = corr.shape
    if 0 < mx < w - 1:
        l, c, r = float(corr[my, mx - 1]), float(corr[my, mx]), float(corr[my, mx + 1])
        d = l - 2 * c + r
        if abs(d) > 1e-12:
            dx = 0.5 * (l - r) / d
    if 0 < my < h - 1:
        u, c, d_ = float(corr[my - 1, mx]), float(corr[my, mx]), float(corr[my + 1, mx])
        d = u - 2 * c + d_
        if abs(d) > 1e-12:
            dy = 0.5 * (u - d_) / d
    # A parabola fit only means anything within one sample of the peak.
    return (dx if abs(dx) <= 1 else 0.0), (dy if abs(dy) <= 1 else 0.0)


def _match(gray, tmpl, guess, search):
    """Locate `tmpl` near `guess`. Returns (cx, cy, peak_correlation) or None."""
    r = (tmpl.shape[0] - 1) // 2
    h, w = gray.shape
    x0 = int(round(guess[0])) - r - search
    y0 = int(round(guess[1])) - r - search
    x1 = int(round(guess[0])) + r + search + 1
    y1 = int(round(guess[1])) + r + search + 1
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w, x1), min(h, y1)
    win = gray[y0:y1, x0:x1]
    if win.shape[0] < tmpl.shape[0] or win.shape[1] < tmpl.shape[1]:
        return None
    corr = cv2.matchTemplate(win, tmpl, cv2.TM_CCOEFF_NORMED)
    _, peak, _, loc = cv2.minMaxLoc(corr)
    mx, my = loc
    sx, sy = _subpixel(corr, mx, my)
    return (x0 + mx + sx + r, y0 + my + sy + r, float(peak))


def _patch_is_dark(t):
    """Dark-on-light or light-on-dark, decided from the patch itself: middle vs border. A video
    carries no setting to say which, and the rig runs both (dark spray on white PLA, bright on
    dark TPU)."""
    m = t.shape[0] // 2
    q = max(2, t.shape[0] // 6)
    middle = float(t[m - q:m + q + 1, m - q:m + q + 1].mean())
    border = float(np.concatenate([t[0, :], t[-1, :], t[:, 0], t[:, -1]]).mean())
    return middle < border


class _PairTracker:
    """One tracked pair with the exact per-frame policy analyse() used to carry inline.

    Factored out 2026-09-05 so the SAME code can track the primary pair and any number of extra
    pairs (a second axial pair, or a transverse pair for Poisson / true stress) in one pass over
    the video. The policy is unchanged and pinned: the pre-refactor analyse() was run on S13's
    real recording and the refactored primary path reproduces it row for row.

    Policy, per frame: centroid chained from the marker's own previous position when the markers
    are discrete dots (with the blob-area window that stops it following a dot merged with a
    shadow); template correlation as the fallback; on low correlation, one retry against the last
    good frame's patch carrying its offset, so the measurement stays anchored to l0.
    """

    def __init__(self, gray0, box_a, box_b, cfg, kind="axial", label=""):
        h, w = gray0.shape
        self._w, self._h = w, h
        for b in (box_a, box_b):
            b.half = int(cfg.box_half)
            b.clamp(w, h)
        self.box_a, self.box_b = box_a, box_b
        self.cfg = cfg
        self.kind, self.label = kind, label
        tmpl_a, tmpl_b = box_a.patch(gray0), box_b.patch(gray0)
        if tmpl_a.size == 0 or tmpl_b.size == 0:
            raise ValueError("a tracking box falls outside the frame")

        a0 = np.array([box_a.cx, box_a.cy], float)
        b0 = np.array([box_b.cx, box_b.cy], float)
        # l0 MUST be measured the same way every later frame is. If the frames are refined to the
        # marker centroid but l0 is taken from wherever the box was dropped, the difference
        # becomes a constant offset on every strain in the run.
        self.refine = cfg.refine
        if self.refine in ("auto", "rig"):
            for pt, t in ((a0, tmpl_a), (b0, tmpl_b)):
                dark_ = _patch_is_dark(t)
                got = centroid_refine(gray0, pt[0], pt[1], cfg.box_half, dark_,
                                      reference_threshold(t, dark_),
                                      weighted=(self.refine != "rig"))
                if got:
                    pt[0], pt[1] = got[0], got[1]
        axis = b0 - a0
        self.l0 = float(np.hypot(*axis))
        if self.l0 < 5:
            raise ValueError("the two boxes are on top of each other — place them apart")
        self.axis = axis / self.l0
        self.perp = np.array([-self.axis[1], self.axis[0]])

        self.dark_a, self.dark_b = _patch_is_dark(tmpl_a), _patch_is_dark(tmpl_b)
        self.thr_a = reference_threshold(tmpl_a, self.dark_a)
        self.thr_b = reference_threshold(tmpl_b, self.dark_b)
        _ra = centroid_refine(gray0, a0[0], a0[1], cfg.box_half, self.dark_a, self.thr_a)
        _rb = centroid_refine(gray0, b0[0], b0[1], cfg.box_half, self.dark_b, self.thr_b)
        self.area_a = _ra[2] if _ra else 0.0
        self.area_b = _rb[2] if _rb else 0.0
        if not (_ra and _rb):
            # No discrete markers here — a speckle pattern. Correlation is the only honest
            # option, and the centroid path is disabled rather than left to latch onto texture.
            self.refine = "correlation"

        self.tmpl_a, self.tmpl_b = tmpl_a, tmpl_b
        self.live_a, self.live_b = tmpl_a, tmpl_b    # re-seeded templates, used after a drop
        self.off_a = self.off_b = np.zeros(2)
        self.last_a, self.last_b = a0.copy(), b0.copy()
        self.n = self.tracked = self.reseeds = self.centroid_frames = 0
        self.reacquires = 0

    def reacquire(self, gray):
        """Search the WHOLE frame for the pair after a violent displacement.

        Why this exists (S38, 2026-09-06): at the snap the specimen recoiled ~100 px sideways
        and came to rest intact, markers sharp — but every per-frame search is anchored within
        cfg.search of the LAST position, so 4.2 s of perfectly trackable video were unreachable.
        This runs only on frames already declared lost, so it costs nothing on a healthy run.

        The pair is re-found by GEOMETRY, the way _choose_marker_pair reasons on the rig: among
        all detected markers, take the pairing whose separation along the pair's own axis is
        closest to the last good separation (the specimen may also have RELAXED, so up to 30 %
        shorter is allowed — that release is real data). Each candidate is then verified by the
        reference template before it is believed.
        """
        marks = find_markers(gray)
        if len(marks) < 2:
            return False
        last_sep = float(abs(np.dot(self.last_b - self.last_a, self.axis)))
        best = None
        for i in range(len(marks)):
            for j in range(i + 1, len(marks)):
                pa = np.array(marks[i][:2], float)
                pb = np.array(marks[j][:2], float)
                if np.dot(pb - pa, self.axis) < 0:
                    pa, pb = pb, pa
                sep = float(abs(np.dot(pb - pa, self.axis)))
                if not (0.7 * last_sep <= sep <= 1.3 * last_sep):
                    continue
                err = abs(sep - last_sep)
                if best is None or err < best[0]:
                    best = (err, pa, pb)
        if best is None:
            return False
        _e, pa, pb = best
        ra = _match(gray, self.tmpl_a, pa, self.cfg.search)
        rb = _match(gray, self.tmpl_b, pb, self.cfg.search)
        if not (ra and rb and min(ra[2], rb[2]) >= self.cfg.min_corr):
            return False
        self.last_a = np.array(ra[:2], float)
        self.last_b = np.array(rb[:2], float)
        self.reacquires += 1
        return True

    def step(self, gray):
        """Track one frame. Returns (pa, pb, l_px, dx_px, cauchy, true, corr, ok, note,
        reseeded); on a lost frame pa/pb are the last good positions and the floats are NaN."""
        cfg = self.cfg
        note, reseeded = "", False
        ra = rb = None
        corr = 0.0
        if self.refine in ("auto", "rig"):
            ca = centroid_refine(gray, self.last_a[0], self.last_a[1], cfg.box_half,
                                 self.dark_a, self.thr_a, weighted=(self.refine != "rig"))
            cb = centroid_refine(gray, self.last_b[0], self.last_b[1], cfg.box_half,
                                 self.dark_b, self.thr_b, weighted=(self.refine != "rig"))
            # A blob is only the marker if it is still about the size the marker was.
            if ca and cb and 0.5 * self.area_a < ca[2] < 2.0 * self.area_a \
                    and 0.5 * self.area_b < cb[2] < 2.0 * self.area_b:
                ra, rb = (ca[0], ca[1], 1.0), (cb[0], cb[1], 1.0)
                corr = 1.0
                self.centroid_frames += 1

        if ra is None or rb is None:
            ra = _match(gray, self.tmpl_a, self.last_a, cfg.search)
            rb = _match(gray, self.tmpl_b, self.last_b, cfg.search)
            corr = min(ra[2] if ra else 0.0, rb[2] if rb else 0.0)
        if corr < cfg.min_corr:
            ra2 = _match(gray, self.live_a, self.last_a, cfg.search)
            rb2 = _match(gray, self.live_b, self.last_b, cfg.search)
            if ra2 and rb2 and min(ra2[2], rb2[2]) >= cfg.min_corr:
                ra = (ra2[0] + self.off_a[0], ra2[1] + self.off_a[1], ra2[2])
                rb = (rb2[0] + self.off_b[0], rb2[1] + self.off_b[1], rb2[2])
                corr = min(ra2[2], rb2[2])
                note, reseeded = "re-seeded (reference correlation %.2f)" % corr, True
                self.reseeds += 1
            else:
                note = "LOST — best correlation %.2f" % corr

        self.n += 1
        if ra and rb and corr >= cfg.min_corr:
            pa = np.array(ra[:2], float)
            pb = np.array(rb[:2], float)
            d = pb - pa
            l_px = float(abs(np.dot(d, self.axis)))
            dx_px = float(abs(np.dot(d, self.perp)))
            cauchy, true = dic_strain(l_px, self.l0)
            self.last_a, self.last_b = pa, pb
            if not reseeded:
                self.live_a = Box(pa[0], pa[1], cfg.box_half).clamp(self._w, self._h).patch(gray)
                self.live_b = Box(pb[0], pb[1], cfg.box_half).clamp(self._w, self._h).patch(gray)
                self.off_a = self.off_b = np.zeros(2)
            self.tracked += 1
            return pa, pb, l_px, dx_px, cauchy, true, corr, True, note, reseeded
        return (self.last_a, self.last_b, float("nan"), float("nan"), float("nan"),
                float("nan"), corr, False, note or "no match", reseeded)


def analyse(path, box_a, box_b, cfg=None, progress=None, should_stop=None, preview=None,
            extras=None):
    """Track both boxes through the video and yield a FrameResult per analysed frame.

    progress(done, total) is called for the UI; should_stop() aborts cleanly between frames.
    preview(gray, a_xy, b_xy) hands the caller the decoded frame and where the boxes are NOW, so
    the pull can be shown while it is measured — the frame is already in memory here, and asking
    the UI to re-read it would fight the sequential decoder this loop depends on. The callback is
    handed the live array, not a copy: a caller that keeps it must copy it itself, because the
    decoder reuses the buffer.

    extras: optional list of (box_a, box_b, kind, label) — ADDITIONAL pairs tracked in the same
    pass over the video: a second axial pair, or a transverse pair whose strain is the lateral
    strain the Poisson / true-stress maths needs (see poisson_true_stress). Each extra pair is
    tracked with the identical policy but lives its own life: an extra losing its markers never
    stops the run — only the PRIMARY pair drives stop_on_loss, exactly as before.
    The generator's return value is a Summary (use `yield from` / .value via StopIteration).
    """
    cfg = cfg or Settings()
    info = probe(path)
    fps = cfg.fps if cfg.fps and cfg.fps > 0 else info["fps"]
    cap = _grab(path)

    # ---- reference frame: templates and L0
    #
    # From a still image when one is given, otherwise from the video's own frame `ref_frame`. The
    # image only replaces the ZERO; `ref_frame` still says where the analysis starts, so a run can
    # be zeroed on a separate picture of the specimen at rest and still measure the whole video.
    if cfg.ref_image:
        gray0, _off, _note = reference_align(cfg.ref_image, path, cfg.ref_frame)
        if gray0 is None:
            cap.release()
            raise ValueError("reference image rejected — %s" % _note)
    else:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(cfg.ref_frame))
        ok, frame = cap.read()
        if not ok:
            cap.release()
            raise IOError("cannot read reference frame %d" % cfg.ref_frame)
        gray0 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if frame.ndim == 3 else frame
    try:
        prim = _PairTracker(gray0, box_a, box_b, cfg)
        extra_tr = [_PairTracker(gray0, ea, eb, cfg, kind=k, label=lb)
                    for (ea, eb, k, lb) in (extras or [])]
    except ValueError:
        cap.release()
        raise

    summary = Summary(l0_px=prim.l0, px_mm=px_per_mm(prim.l0, cfg.gauge_mm), fps=fps)
    summary.extras = [{"label": t.label, "kind": t.kind, "l0_px": t.l0,
                       "tracked": 0, "n": 0, "centroid_frames": 0, "reseeds": 0}
                      for t in extra_tr]
    total = max(1, (info["frames"] - cfg.ref_frame) // max(1, cfg.step))

    # Read SEQUENTIALLY. Seeking with CAP_PROP_POS_FRAMES per frame forces the decoder to rewind
    # to the previous keyframe every time, which on a 1682-frame lossless AVI is minutes rather
    # than seconds. One seek to the reference frame, then straight reads, skipping for step>1.
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(cfg.ref_frame))
    idx = cfg.ref_frame
    done = 0
    lost_run = 0                 # consecutive analysed frames with no usable match
    while True:
        if should_stop and should_stop():
            break
        ok, frame = cap.read()
        if not ok:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if frame.ndim == 3 else frame

        # CENTROID FIRST when the markers are discrete dots, correlation as the fallback, one
        # retry against the last good patch — the whole policy lives in _PairTracker.step now,
        # unchanged (measured on S25: centroid off its own last position 25 microstrain, off a
        # correlation estimate 215, correlation alone 175, the live rig 28).
        pa, pb, l_px, dx_px, cauchy, true, corr, ok, note, reseeded = prim.step(gray)
        if reseeded:
            summary.reseeds += 1

        # The extras live their own lives: tracked with the identical policy, but a lost extra
        # never stops the run and never marks the primary row as lost.
        ext = []
        for t, meta in zip(extra_tr, summary.extras):
            epa, epb, el, _edx, ec, _et, _ecorr, eok, _en, _ers = t.step(gray)
            meta["n"] += 1
            if eok:
                meta["tracked"] += 1
            ext.append((float(epa[0]), float(epa[1]), float(epb[0]), float(epb[1]),
                        el, ec, eok))

        t_s = (idx - cfg.ref_frame) / fps if fps > 0 else float(idx)
        if ok:
            summary.tracked += 1
            res = FrameResult(idx, t_s, tuple(pa), tuple(pb), l_px, dx_px, cauchy, true,
                              corr, True, note, tuple(ext))
        else:
            res = FrameResult(idx, t_s, tuple(pa), tuple(pb), float("nan"), float("nan"),
                              float("nan"), float("nan"), corr, False, note or "no match",
                              tuple(ext))

        summary.n += 1
        summary.rows.append(res)

        # ---- give up at the point the markers are actually gone.
        #
        # The rows that recorded the loss are dropped, not kept: they carry NaN, they would show
        # up in the CSV as measurements, and the last thing the record should end on is a frame
        # where nothing was found. What remains ends at the last frame that genuinely tracked.
        if res.ok:
            lost_run = 0
        elif cfg.stop_on_loss:
            lost_run += 1
            if lost_run == 1:
                # the INSTANT the streak began - with the grace window the stop can land
                # seconds later, and "markers gone at" must name the loss, not the give-up
                first_lost = (idx, (idx - cfg.ref_frame) / fps if fps > 0 else float(idx))
            # Past the tolerance the markers are LOST — but for the grace window the loop keeps
            # decoding and tries to re-find the pair anywhere in the frame. Success rewinds the
            # loss and the run continues (the gap stays in the record as untracked rows).
            grace_frames = max(1, int(round(cfg.loss_grace_s * (fps if fps > 0 else 30.0)
                                            / max(1, cfg.step))))
            if lost_run >= max(1, cfg.loss_tolerance) and prim.reacquire(gray):
                lost_run = 0
                summary.rows[-1] = replace(res, note=res.note + "  → re-acquired after "
                                           "displacement")
                for tr in extra_tr:
                    tr.reacquire(gray)
            elif lost_run >= max(1, cfg.loss_tolerance) + grace_frames:
                summary.lost_at_frame, summary.lost_at_t = first_lost
                summary.lost_reason = ("no match, and nothing re-acquired within %.1f s"
                                       % cfg.loss_grace_s)
                while summary.rows and not summary.rows[-1].ok:
                    summary.rows.pop()
                    summary.n -= 1
                # Where the DATA ends, which is not the same instant as where tracking failed and
                # is the one the operator reads off the plot.
                summary.data_ends_t = summary.rows[-1].t if summary.rows else 0.0
                break

        if preview is not None:
            # Where the boxes are NOW, so the drawn overlay follows the markers apart rather than
            # sitting where they started. On a lost frame these are the last good positions.
            preview(gray, tuple(prim.last_a), tuple(prim.last_b))
        yield res
        done += 1
        if progress:
            progress(done, total)
        idx += max(1, cfg.step)
        for _ in range(max(1, cfg.step) - 1):        # skip forward without decoding a seek
            if not cap.grab():
                break

    summary.centroid_frames = prim.centroid_frames
    for t, meta in zip(extra_tr, summary.extras):
        meta["centroid_frames"], meta["reseeds"] = t.centroid_frames, t.reseeds
    cap.release()
    return summary


# The noise/rate band: 0.30 % of strain wide, starting 0.05 % above the working zero. Kept at the
# historical numbers so the figure stays comparable with every one already in the deck; what has
# changed is WHERE the zero comes from.
NOISE_LO, NOISE_SPAN, NOISE_MIN_PTS = 0.0005, 0.0030, 20
NOISE_SEARCH_MAX = 0.012        # never look for a window above 1.2 % strain — past the elastic ramp


def noise_window(t, e, e_zero=None):
    """Which samples the noise and strain-rate figures are taken from. (mask, zero, sentence).

    THE BUG THIS REPLACES. The band used to be 0.05-0.35 % of the RAW strain, measured from the
    reference frame. That is right when the reference frame is a loaded, settled specimen — every
    video this rig records — and wrong when it is not. On a foreign recording the reference frame
    can precede the preload entirely, so the band lands inside the seating ramp, where the record
    is genuinely curved. A straight-line fit then measures the CURVATURE and calls it noise: MOT
    session 2 reported 57 ue where the settled part of the same record gives 24.

    Two ways out, in order of preference:

      1. A load channel says where the preload was reached, so the zero is known exactly. That is
         what a companion file buys (see `preload_strain_zero`).
      2. Without one, take the STRAIGHTEST band of the same width below NOISE_SEARCH_MAX. The
         measurement is defined as scatter about a straight line, so the honest place to make it
         is where the record is straight. This cannot invent a good number on a bad record — if
         nothing is straight, the best R2 is poor and the window is reported with it.

    Either way the window is RETURNED and printed, because a noise figure whose window is invisible
    is a number nobody can check.
    """
    if e is None or len(e) < NOISE_MIN_PTS:
        return None, 0.0, "too few points"

    if e_zero is not None:
        lo = float(e_zero) + NOISE_LO
        m = (e >= lo) & (e <= lo + NOISE_SPAN)
        if m.sum() >= NOISE_MIN_PTS:
            return m, float(e_zero), ("%.2f-%.2f %% strain, anchored on the preload"
                                      % (lo * 100, (lo + NOISE_SPAN) * 100))

    base = float(np.nanmin(e))
    hi_cap = min(float(np.nanmax(e)), base + NOISE_SEARCH_MAX)
    if hi_cap - base < NOISE_SPAN:
        m = np.isfinite(e)
        return (m, base, "whole record — it never spans %.2f %% of strain"
                % (NOISE_SPAN * 100)) if m.sum() >= NOISE_MIN_PTS else (None, base, "too few points")

    best = None
    for lo in np.linspace(base + NOISE_LO, hi_cap - NOISE_SPAN, 60):
        m = (e >= lo) & (e <= lo + NOISE_SPAN)
        if m.sum() < NOISE_MIN_PTS:
            continue
        tt, ee = t[m], e[m]
        if tt.max() - tt.min() <= 0:
            continue
        r = np.corrcoef(tt, ee)[0, 1]
        r2 = float(r * r)
        if best is None or r2 > best[0]:
            best = (r2, m, float(lo))
    if best is None:
        m = (e >= base + NOISE_LO) & (e <= base + NOISE_LO + NOISE_SPAN)
        return (m if m.sum() >= NOISE_MIN_PTS else None), base, "fixed band from the record's own minimum"
    r2, m, lo = best
    return m, lo - NOISE_LO, ("%.2f-%.2f %% strain, the straightest band (R² %.5f)"
                              % (lo * 100, (lo + NOISE_SPAN) * 100, r2))


def metrics(summary, cfg=None, label="", source_video=""):
    """Headline numbers for one analysed video, as an ordered list of (name, value) pairs.

    Two of these are worth more than the rest for comparing instruments, and both follow the
    convention this project's deck already uses so the numbers are directly comparable with the
    MOT extensometer slides:

      STRAIN RATE and NOISE are measured over the 0.05-0.35 % strain window. That window is
      small and nearly straight, so a straight-line fit leaves NOISE rather than model error.
      Detrending a whole fracture curve with a polynomial measures how badly the polynomial fits,
      which is a mistake that has already been made once in this project.

    Settings are included because provenance matters: a peak strain means nothing without the
    frame rate, box size and method that produced it.
    """
    cfg = cfg or Settings()
    ok = [r for r in summary.rows if r.ok]
    out = [("Label", label or "-"),
           ("Video", os.path.basename(source_video) if source_video else "-")]
    if not ok:
        out.append(("Result", "nothing tracked"))
        return out
    L = np.array([r.l_px for r in ok], float)
    e = np.array([r.cauchy for r in ok], float)
    et = np.array([r.true for r in ok], float)
    t = np.array([r.t for r in ok], float)

    m, e0, win_why = noise_window(t, e, e_zero=getattr(summary, "strain_zero", None))
    rate = noise = float("nan")
    if m is not None and m.sum() >= NOISE_MIN_PTS:
        sl, ic = np.polyfit(t[m], e[m], 1)
        rate = float(sl)
        noise = float((L[m] - np.polyval(np.polyfit(np.arange(m.sum()), L[m], 1),
                                         np.arange(m.sum()))).std() / summary.l0_px * 1e6)
    span = t[-1] - t[0]
    out += [
        # Two very different stories share the stopped_early flag, and the table used to shout
        # MARKER LOST for both. When every kept frame tracked, the loss IS the end of the data -
        # at fracture the marker physically leaves, and 100 % tracked plus an alarming red row
        # read as a contradiction (his words, 2026-09-06). The alarm is kept for the case that
        # earns it: frames dropping BEFORE the loss.
        ("Tracking ended",
         (("markers gone at %.2f s (frame %d) — the normal end at fracture; every frame "
           "before it tracked"
           % (summary.lost_at_t or 0.0, summary.lost_at_frame))
          if summary.coverage >= 99.95 else
          ("MARKER LOST at frame %d, t %.2f s — %s (%d earlier frames also untracked)"
           % (summary.lost_at_frame, summary.lost_at_t or 0.0, summary.lost_reason,
              summary.n - summary.tracked)))
         if summary.stopped_early else "end of video"),
        ("Data ends at", "%.3f s" % (summary.data_ends_t if summary.data_ends_t is not None
                                      else t[-1])),
        ("Frames analysed", "%d" % summary.n),
        ("Frames tracked", "%d  (%.1f %%)" % (summary.tracked, summary.coverage)),
        ("Measured by centroid", "%d" % summary.centroid_frames),
        ("Re-seeds", "%d" % summary.reseeds),
        ("Duration", "%.2f s" % span),
        ("Frame rate used", "%.4f fps" % summary.fps),
        ("Px0 (L0)", "%.2f px" % summary.l0_px),
        # The gauge is stamped with WHERE IT CAME FROM. It sets px/mm and the extension in mm and
        # nothing else — but "80.00 mm" read off a results sheet is indistinguishable from a
        # measured 80.00 mm, and on the first foreign video this dialog was given it was neither:
        # it was the spin-box default, on a 45 mm specimen.
        ("Gauge", "%.2f mm%s" % (cfg.gauge_mm,
                                 ("  (%s)" % cfg.gauge_src if cfg.gauge_src else "")
                                 if cfg.gauge_confirmed
                                 else "   ** ASSUMED — not confirmed for this video **")),
        ("px per mm", ("%.4f%s" % (summary.px_mm, "" if cfg.gauge_confirmed else "  (assumed)"))
         if summary.px_mm else "-"),
        ("L at peak", "%.2f px" % L.max()),
        ("Extension at peak", ("%.4f mm%s" % ((L.max() - summary.l0_px) / summary.px_mm,
                                              "" if cfg.gauge_confirmed else "  (assumed gauge)"))
         if summary.px_mm else "-"),
        ("Peak strain (engineering)", "%.4f %%" % (e.max() * 100)),
        ("Peak strain (true/log)", "%.4f %%" % (et.max() * 100)),
        ("Mean rate over the run", "%.3e /s" % ((e[-1] - e[0]) / span) if span > 0 else "-"),
        ("Noise / rate window", win_why),
        ("Strain rate, in that window", ("%.3e /s" % rate) if rate == rate else "too few points"),
        ("Noise, in that window", ("%.1f ue" % noise) if noise == noise else "too few points"),
        ("Tracking method", cfg.refine),
        ("Box half-size", "%d px" % cfg.box_half),
        ("Search window", "%d px" % cfg.search),
        ("Min correlation", "%.2f" % cfg.min_corr),
        ("Reference", ("image: %s" % os.path.basename(cfg.ref_image)) if cfg.ref_image
         else "frame %d" % cfg.ref_frame),
        ("Analysis starts at frame", "%d" % cfg.ref_frame),
        ("Analysed every", "%d frame(s)" % cfg.step),
    ]
    return out


def to_csv(summary, path, source_video="", cfg=None, poisson_rows=None):
    """Write the run out in the same spirit as the rig's CSV: a header that says how, then rows.

    Extra tracked pairs land as P1_*, P2_* column blocks; pass `poisson_rows` (from
    poisson_true_stress) to append the Nu / Area / true-stress block beside them."""
    cfg = cfg or Settings()
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("# UTM DIC Post-Processing\n#\n")
        f.write("# Source video: %s\n" % source_video)
        if cfg.ref_image:
            f.write("# Reference: image %s (analysis starts at frame %d)\n"
                    % (os.path.basename(cfg.ref_image), cfg.ref_frame))
        else:
            f.write("# Reference frame: %d\n" % cfg.ref_frame)
        f.write("# L0 (Px0): %.3f px\n" % summary.l0_px)
        f.write("# Gauge: %.2f mm  ->  px_per_mm: %s\n"
                % (cfg.gauge_mm, ("%.4f" % summary.px_mm) if summary.px_mm else "n/a"))
        f.write("# Frame rate used: %.4f fps\n" % summary.fps)
        f.write("# Box half-size: %d px   search: %d px   min correlation: %.2f\n"
                % (cfg.box_half, cfg.search, cfg.min_corr))
        f.write("# Frames analysed: %d   tracked: %d (%.1f %%)   re-seeds: %d\n"
                % (summary.n, summary.tracked, summary.coverage, summary.reseeds))
        # Whether the record stops because the VIDEO ended or because TRACKING did is the first
        # thing anyone reading this file later needs to know, and it is not recoverable from the
        # rows — they look identical either way, because the untracked ones were dropped.
        if summary.stopped_early:
            f.write("# Tracking ended: MARKER LOST at frame %d (t %.3f s) - %s\n"
                    "#                 Rows stop at t %.3f s; nothing past that was measured.\n"
                    % (summary.lost_at_frame, summary.lost_at_t or 0.0, summary.lost_reason,
                       summary.data_ends_t or 0.0))
        else:
            f.write("# Tracking ended: end of video\n")
        f.write("# DIC_Cauchy    = (L - L0)/L0   engineering strain\n")
        f.write("# DIC_LogStrain = ln(L / L0)    log / Hencky strain (the rig's CSVs call this\n")
        f.write("#                 DIC_True, which is the same quantity under a misleading name:\n")
        f.write("#                 it needs only the markers, not the cross-section)\n")
        f.write("# Both via utm_dic.dic_strain - the same function the live rig uses.\n#\n")
        # DIC_LogStrain, not "DIC_True". The rig's own CSVs call this column DIC_True and keep
        # that name for backward compatibility with every test since S1 — but the name has always
        # been misleading. It is ln(L/L0): a KINEMATIC quantity needing nothing but the two
        # markers. What genuinely cannot be measured on this rig is true (Cauchy) STRESS, which
        # needs the current cross-section. Nothing reads this export's header, so it is named for
        # what it actually is.
        for i, m in enumerate(summary.extras, 1):
            f.write("# Extra pair P%d: %s (%s), L0 %.3f px, tracked %d/%d\n"
                    % (i, m.get("label") or "pair %d" % i, m["kind"], m["l0_px"],
                       m["tracked"], m["n"]))
        if poisson_rows is not None:
            f.write("# Nu           = -eps_lateral / eps_axial, per row (needs |eps_axial| to be\n"
                    "#                real - early rows where it is ~0 are left blank)\n"
                    "# Area_mm2     = A0 (1 + eps_lateral)^2 - measured lateral contraction,\n"
                    "#                isotropic through-thickness assumption (utm_dic.current_area)\n"
                    "# Sigma_true   = F / current area, MPa - TRUE (Cauchy) stress\n")
        head = "Frame,Time_s,Ax,Ay,Bx,By,L_px,dx_px,DIC_Cauchy,DIC_LogStrain,Correlation,Tracked"
        for i in range(1, len(summary.extras) + 1):
            head += (",P%d_Ax,P%d_Ay,P%d_Bx,P%d_By,P%d_L_px,P%d_strain,P%d_ok"
                     % ((i,) * 7))
        if poisson_rows is not None:
            head += ",Nu,Area_mm2,F_N,Sigma_eng_MPa,Sigma_true_MPa"
        f.write(head + ",Note\n")

        def _n(v, fmt="%.4f"):
            return "" if v is None or v != v else fmt % v

        for k, r in enumerate(summary.rows):
            line = ("%d,%.4f,%.3f,%.3f,%.3f,%.3f,%s,%s,%s,%s,%.4f,%d"
                    % (r.idx, r.t, r.a[0], r.a[1], r.b[0], r.b[1],
                       _n(r.l_px), _n(r.dx_px), _n(r.cauchy, "%.8f"), _n(r.true, "%.8f"),
                       r.corr, 1 if r.ok else 0))
            for (eax, eay, ebx, eby, el, ec, eok) in r.extra:
                line += (",%.3f,%.3f,%.3f,%.3f,%s,%s,%d"
                         % (eax, eay, ebx, eby, _n(el), _n(ec, "%.8f"), 1 if eok else 0))
            if poisson_rows is not None:
                p = poisson_rows[k] if k < len(poisson_rows) else None
                if p:
                    line += ",%s,%s,%s,%s,%s" % (_n(p.get("nu")), _n(p.get("area_mm2")),
                                                 _n(p.get("F_N"), "%.2f"),
                                                 _n(p.get("sigma_eng")), _n(p.get("sigma_true")))
                else:
                    line += ",,,,,"
            f.write(line + ",%s\n" % r.note.replace(",", ";"))
    return path


def poisson_true_stress(summary, area0_mm2, comp=None, pair_index=None, min_axial=0.002):
    """nu, area change and TRUE (Cauchy) stress from a tracked TRANSVERSE pair.

    This is FW1's four-marker mathematics (utm_dic) applied offline: the live rig cannot see the
    transverse contraction of the mini-dogbone (sub-pixel at 20.9 px/mm — the documented FW1
    blocker), but the post-processor can be pointed at ANY video, including one with a wider
    specimen, better optics, or another lab's markers.

    Returns (rows, note): `rows` aligned one-to-one with summary.rows, each None (untracked) or
    {eps_ax, eps_lat, nu, area_mm2, F_N, sigma_eng, sigma_true}; `note` is the honesty line —
    it SAYS when the measured width change is sub-pixel, because then nu and everything built on
    it is noise wearing units, exactly what FW1 warned writing the code would produce.

      * nu is left None while |eps_axial| < min_axial (0.2 %): dividing two near-zeros early in
        the ramp produces spectacular nonsense that would dominate any plot autoscale.
      * area and sigma_true come straight from utm_dic.current_area / cauchy_stress.
      * force is interpolated from the companion's load channel at each row's time (the shared-
        origin convention preload_strain_zero already relies on); without a companion the stress
        fields stay None and the geometric ones are still returned.
    """
    from utm_dic import current_area, cauchy_stress, poisson_ratio
    idx = pair_index
    if idx is None:
        idx = next((i for i, m in enumerate(summary.extras) if m["kind"] == "transverse"), None)
    if idx is None or idx >= len(summary.extras):
        return None, "no transverse pair tracked"
    w0 = summary.extras[idx]["l0_px"]
    have_f = comp is not None and comp.load is not None and comp.t is not None

    rows, dws = [], []
    for r in summary.rows:
        e = r.extra[idx] if idx < len(r.extra) else None
        if not r.ok or e is None or not e[6] or e[4] != e[4]:
            rows.append(None)
            continue
        eps_lat = e[5]
        dws.append(abs(e[4] - w0))
        F = float(np.interp(r.t, comp.t, comp.load)) if have_f else None
        area = current_area(area0_mm2, eps_lat)
        rows.append({
            "eps_ax": r.cauchy, "eps_lat": eps_lat,
            "nu": (poisson_ratio(r.cauchy, eps_lat)
                   if abs(r.cauchy) >= min_axial else None),
            "area_mm2": area,
            "F_N": F,
            "sigma_eng": (F / area0_mm2) if F is not None else None,
            "sigma_true": cauchy_stress(F, area0_mm2, eps_lat) if F is not None else None,
        })

    got = [r for r in rows if r]
    if not got:
        return rows, "transverse pair never tracked"
    dw_p95 = float(np.percentile(dws, 95)) if dws else 0.0
    note = ("width change over the run: %.2f px (p95) on a %.1f px width" % (dw_p95, w0))
    if dw_p95 < 1.0:
        note += (" — SUB-PIXEL: nu and true stress from this pair are noise wearing units. "
                 "This needs closer optics or a wider specimen (FW1), not more maths.")
    if not have_f:
        note += "  No load channel attached, so only the geometric quantities are computed."
    return rows, note


# ===================================================================================
#  Report — one page carrying the plot, the numbers and their provenance.
#
#  Deliberately self-contained: a report that needs the app open to be understood is
#  not a record. Everything on the page was computed from the videos named on it.
# ===================================================================================
BLUE, GREY = "#1f77b4", "#555555"


def build_report(runs, out_dir, title="DIC post-processing", note=""):
    """Write a one-page PDF+PNG comparing every completed run, plus a CSV of the table.

    `runs` is a list of dicts: {label, colour, path, t, e, tr, summary, cfg}. The tab hands its
    own Run objects through a small adapter rather than this module importing Qt.

    Returns the list of files written. PDF first, because it is the one that stays sharp in a
    document; the PNG is for pasting into a message.
    """
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["pdf.fonttype"] = 42        # embedded TrueType: selectable, editable text
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg

    runs = [r for r in runs if r.get("t")]
    if not runs:
        raise ValueError("no completed runs to report")
    os.makedirs(out_dir, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    stem = os.path.join(out_dir, "dic_postproc_%s" % stamp)

    fig = Figure(figsize=(11.69, 8.27))             # A4 landscape
    FigureCanvasAgg(fig)
    fig.patch.set_facecolor("white")

    fig.text(0.035, 0.960, title, fontsize=17, fontweight="bold")
    fig.text(0.035, 0.934,
             "Strain from recorded video. Marker separation in pixels -> strain via "
             "utm_dic.dic_strain, the same function the live rig uses.",
             fontsize=9.2, color=GREY)
    fig.text(0.035, 0.916, time.strftime("%Y-%m-%d %H:%M") + ("   ·   " + note if note else ""),
             fontsize=8.6, color=GREY)

    # ---- the plot. Left 55 % of the page; the table owns the right.
    ax = fig.add_axes([0.06, 0.46, 0.47, 0.42])
    for r in runs:
        ax.plot(r["t"], [v * 100 for v in r["e"]], color=r["colour"], lw=1.6, label=r["label"])
    ax.set_xlabel("time (s)"); ax.set_ylabel("DIC strain (%)")
    ax.set_title("DIC strain vs time", fontsize=11)
    ax.grid(alpha=0.3)
    ax.legend(frameon=False, fontsize=9)

    # ---- what each run is, two short lines each so nothing reaches the table's column
    y = 0.395
    fig.text(0.06, y, "Runs", fontsize=11, fontweight="bold"); y -= 0.030
    for r in runs:
        s_ = r["summary"]
        fig.text(0.062, y, "■", fontsize=11, color=r["colour"])
        fig.text(0.082, y, "%s — %s" % (r["label"], os.path.basename(r["path"])),
                 fontsize=9, fontweight="bold")
        y -= 0.024
        fig.text(0.082, y, "%d of %d frames tracked (%.1f %%)   ·   Px0 %.2f px   ·   %.4f fps"
                 % (s_.tracked, s_.n, s_.coverage, s_.l0_px, s_.fps), fontsize=8.4, color=GREY)
        y -= 0.022
        # nanmax, not max: with "stop when the markers are lost" turned off, the series carries a
        # NaN at each dropout so the plotted curve breaks there. Plain max() on a list holding a
        # NaN returns whatever the comparison order happened to give, which is not a peak.
        fig.text(0.082, y, "peak %.3f %% engineering   ·   %.3f %% log   ·   %s"
                 % (np.nanmax(r["e"]) * 100, np.nanmax(r["tr"]) * 100, r["cfg"].refine),
                 fontsize=8.4, color=GREY)
        y -= 0.034
        if s_.stopped_early:
            fig.text(0.082, y, "tracking ended early: markers lost at %.2f s" % s_.lost_at_t,
                     fontsize=8.4, color="#c0392b")
            y -= 0.022
        elif s_.tracked < s_.n:
            fig.text(0.082, y, "%d frame(s) not tracked — the curve is broken where they are"
                     % (s_.n - s_.tracked), fontsize=8.4, color="#c0392b")
            y -= 0.022

    # ---- the table, as text so it stays selectable in the PDF
    rows = report_table(runs)
    x0, y0 = 0.575, 0.885
    pw = 0.145                                     # parameter column
    avail = 0.985 - x0 - pw
    colw = avail / max(1, len(rows[0]) - 1)
    fig.text(x0, y0 + 0.026, "Results", fontsize=11, fontweight="bold")
    for ri, row in enumerate(rows):
        yy = y0 - ri * 0.0232
        head = (ri == 0)
        fig.text(x0, yy, row[0], fontsize=7.4, color="#222" if head else GREY,
                 fontweight="bold" if head else "normal")
        for ci, val in enumerate(row[1:]):
            fig.text(x0 + pw + ci * colw, yy, str(val), fontsize=7.4,
                     color=runs[ci]["colour"], fontweight="bold" if head else "normal")

    out = []
    for ext, kw in ((".pdf", {}), (".png", {"dpi": 160})):
        p = stem + "_report" + ext
        fig.savefig(p, facecolor="white", **kw)
        out.append(p)

    # the same table as data, so nobody has to retype it out of a PDF
    tcsv = stem + "_results.csv"
    with open(tcsv, "w", encoding="utf-8", newline="") as f:
        import csv as _csv
        w = _csv.writer(f)
        w.writerow(["# UTM DIC post-processing results", time.strftime("%Y-%m-%d %H:%M")])
        w.writerow([])
        for row in rows:
            w.writerow(row)
    out.append(tcsv)

    # and every run's per-frame data beside it
    for r in runs:
        safe = "".join(c if c.isalnum() or c in "-_ " else "_" for c in r["label"]).strip()
        p = "%s_%s.csv" % (stem, safe or "run")
        to_csv(r["summary"], p, source_video=r["path"], cfg=r["cfg"])
        out.append(p)
    return out


def report_table(runs):
    """The comparison table as rows: parameters down the side, one column per run."""
    cols = [metrics(r["summary"], r["cfg"], label=r["label"], source_video=r["path"])
            for r in runs]
    names = [n for n, _ in cols[0]]
    rows = [["Parameter"] + [r["label"] for r in runs]]
    for i, n in enumerate(names):
        rows.append([n] + [(c[i][1] if i < len(c) else "-") for c in cols])
    return rows
