"""Multi-pair post-processing: a second pair tracked in the same pass, and FW1's maths on it.

    python "tests script/test_multipair_postproc.py"     (run from Software/UTM_PyQt6)

The decisive test is a synthetic pull whose answer is known exactly: four markers move with
eps_axial ramping to 5 % and eps_lateral = -nu_true * eps_axial at nu_true = 0.35, force ramping
with strain. The tracker has never seen the numbers; it only sees the video. If the recovered
Poisson ratio, area change and true stress do not land on the synthesis, the feature is wrong.

Also here: the refactor guarantee (primary-pair results must be identical with and without
extras riding along), the second-axial-pair path, the honesty note for sub-pixel width change,
and the CSV round trip.
"""
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import math
import tempfile
import unittest

import cv2
import numpy as np

import utm_postproc as PP

NU_TRUE = 0.35
EPS_MAX = 0.05
N_FRAMES = 60
A0_MM2 = 80.0


def _synth_video(nu=NU_TRUE, eps_max=EPS_MAX, n=N_FRAMES, w0=240.0, l0=280.0):
    """A 640x480 pull: axial dots part along y, transverse dots close along x, all by the book."""
    path = _os.path.join(tempfile.mkdtemp(prefix="utm_multipair_"), "synth.avi")
    vw = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"MJPG"), 30.0, (640, 480))
    assert vw.isOpened()
    cx, cy = 320.0, 240.0
    for i in range(n):
        ea = eps_max * i / (n - 1)
        el = -nu * ea
        frame = np.full((480, 640, 3), 235, np.uint8)
        pts = [(cx, cy - (l0 / 2) * (1 + ea)), (cx, cy + (l0 / 2) * (1 + ea)),       # axial
               (cx - (w0 / 2) * (1 + el), cy), (cx + (w0 / 2) * (1 + el), cy)]       # transverse
        for (x, y) in pts:
            # shift=4 gives sixteenth-pixel centres, so the dots MOVE sub-pixel between frames
            # the way real markers do — integer centres made every recovered series a staircase
            # and dominated the tolerances with the synthesis's own quantisation
            cv2.circle(frame, (int(round(x * 16)), int(round(y * 16))), 12 * 16,
                       (25, 25, 25), -1, lineType=cv2.LINE_AA, shift=4)
        vw.write(frame)
    vw.release()
    return path


def _run(path, extras):
    cfg = PP.Settings(step=1, stop_on_loss=False)
    gen = PP.analyse(path, PP.Box(320, 100, cfg.box_half), PP.Box(320, 380, cfg.box_half),
                     cfg, extras=extras)
    try:
        while True:
            next(gen)
    except StopIteration as st:
        return st.value


def _companion(n=N_FRAMES, fps=30.0):
    t = np.arange(n) / fps
    load = 100.0 + 900.0 * (t / t[-1])
    return PP.Companion(path="synth", source="test", n_rows=n, t=t, load=load)


class FourMarkerPoisson(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.video = _synth_video()
        cls.summary = _run(cls.video, extras=[
            (PP.Box(200, 240, 24), PP.Box(440, 240, 24), "transverse", "width")])

    def test_primary_recovers_the_axial_ramp(self):
        s = self.summary
        self.assertGreater(s.coverage, 95)
        self.assertLess(abs(s.rows[-1].cauchy - EPS_MAX), 0.002)

    def test_transverse_pair_recovers_the_lateral_strain(self):
        last = [r.extra[0] for r in self.summary.rows if r.ok and r.extra and r.extra[0][6]][-1]
        self.assertLess(abs(last[5] - (-NU_TRUE * EPS_MAX)), 0.001)

    def test_poisson_area_and_true_stress_land_on_the_synthesis(self):
        rows, note = PP.poisson_true_stress(self.summary, A0_MM2, comp=_companion())
        nus = [p["nu"] for p in rows if p and p["nu"] is not None]
        self.assertGreater(len(nus), 20)
        self.assertLess(abs(float(np.median(nus)) - NU_TRUE), 0.02)
        self.assertNotIn("SUB-PIXEL", note)      # 4.2 px of width change is a real signal
        # true stress: F / (A0 (1+eps_lat)^2), and in tension it must exceed engineering stress
        p = [p for p in rows if p and p["sigma_true"] is not None][-1]
        expect = p["F_N"] / (A0_MM2 * (1.0 + p["eps_lat"]) ** 2)
        self.assertAlmostEqual(p["sigma_true"], expect, places=9)
        self.assertGreater(p["sigma_true"], p["sigma_eng"])
        # 0.2 mm2 on 80 mm2 is the same tolerance as the 0.001 strain allowed above — the
        # synthesis draws its dots at INTEGER pixel centres, so ±0.5 px of quantisation on a
        # 240 px width is the synthesis's error, not the tracker's
        self.assertLess(abs(p["area_mm2"] - A0_MM2 * (1 - NU_TRUE * EPS_MAX) ** 2), 0.2)

    def test_extras_do_not_change_the_primary_measurement(self):
        """The refactor promise, restated for extras: tracking more pairs must not move the
        primary numbers by a nanometre."""
        alone = _run(self.video, extras=None)
        self.assertEqual(len(alone.rows), len(self.summary.rows))
        for ra, rb in zip(alone.rows, self.summary.rows):
            self.assertEqual((ra.l_px, ra.cauchy, ra.corr, ra.ok),
                             (rb.l_px, rb.cauchy, rb.corr, rb.ok))

    def test_second_axial_pair_tracks_like_the_primary(self):
        s = _run(self.video, extras=[
            (PP.Box(320, 100, 24), PP.Box(320, 380, 24), "axial", "pair2")])
        for r in s.rows:
            if r.ok and r.extra and r.extra[0][6]:
                self.assertLess(abs(r.extra[0][5] - r.cauchy), 5e-4)

    def test_csv_round_trip_carries_the_new_columns(self):
        rows, _note = PP.poisson_true_stress(self.summary, A0_MM2, comp=_companion())
        out = _os.path.join(tempfile.mkdtemp(prefix="utm_csv_"), "multi.csv")
        PP.to_csv(self.summary, out, source_video=self.video, poisson_rows=rows)
        with open(out, encoding="utf-8") as fh:
            text = fh.read()
        head = [ln for ln in text.splitlines() if ln.startswith("Frame,")][0]
        for col in ("P1_L_px", "P1_strain", "Nu", "Area_mm2", "Sigma_true_MPa"):
            self.assertIn(col, head)
        n_data = len([ln for ln in text.splitlines() if ln and ln[0].isdigit()])
        self.assertEqual(n_data, len(self.summary.rows))
        self.assertIn("Extra pair P1: width (transverse)", text)


class HonestyNotes(unittest.TestCase):
    def test_subpixel_width_change_is_called_noise(self):
        """FW1's blocker, enforced: a run whose width change never exceeds a pixel must SAY that
        nu from it is noise wearing units."""
        video = _synth_video(nu=0.004)          # 0.05 strain x 0.004 x 240 px = 0.05 px of width
        s = _run(video, extras=[(PP.Box(200, 240, 24), PP.Box(440, 240, 24),
                                 "transverse", "width")])
        _rows, note = PP.poisson_true_stress(s, A0_MM2, comp=_companion())
        self.assertIn("SUB-PIXEL", note)

    def test_no_companion_means_no_stress_and_says_so(self):
        s = FourMarkerPoisson.summary if hasattr(FourMarkerPoisson, "summary") else None
        if s is None:
            s = _run(_synth_video(), extras=[(PP.Box(200, 240, 24), PP.Box(440, 240, 24),
                                              "transverse", "width")])
        rows, note = PP.poisson_true_stress(s, A0_MM2, comp=None)
        self.assertIn("No load channel", note)
        got = [p for p in rows if p]
        self.assertTrue(all(p["sigma_true"] is None for p in got))
        self.assertTrue(all(p["area_mm2"] is not None for p in got))


if __name__ == "__main__":
    try:
        _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    unittest.main(verbosity=2)
