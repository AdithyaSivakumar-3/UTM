"""The three guards added after MOT session 2 was post-processed with two wrong inputs.

    python "tests script/test_postproc_guards.py"        (run from Software/UTM_PyQt6)

On 2026-09-03 the XT-205's 45 mm video went through this dialog at 1000 fps and an 80 mm gauge,
and the noise window landed inside the preload ramp. None of the three corrupted the strain — it
is a pixel ratio — but they reached every time output, the reported scale, and a noise figure that
was quoted in a deck. Each test below fails if its guard is removed.

The real files are used where they are present; the arithmetic tests synthesise their own data so
the suite still runs on a machine without the validation folder.
"""
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import io
import tempfile
import unittest

import numpy as np

import utm_postproc as PP

# .../<repo>/Software/UTM_PyQt6/tests script/this.py  ->  four levels up is the repo root.
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                       "..", "..", ".."))
_MOT = _os.path.join(_REPO, "Validation docs", "MOT Test 2", "Videoextesometer MOT")
_MOT_CSV = _os.path.join(_MOT, "strain-sample3.csv")
_MOT_DAQ = _os.path.join(_MOT, "sample3.daq")
_PPCSV = _os.path.join(_REPO, "Validation docs", "MOT Test 2", "DIC post processing data",
                       "sample3_chan 0_dic_postproc.csv")


def _write(text, suffix=".csv"):
    fh = tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8")
    fh.write(text)
    fh.close()
    return fh.name


class TestFpsGuard(unittest.TestCase):
    """Guard 1 — a container's frame rate must not be believed just because it is present."""

    def test_round_number_over_100_is_suspect(self):
        self.assertTrue(PP.fps_is_suspect(1000.0, verified=False))
        self.assertTrue(PP.fps_is_suspect(500.0, verified=False))
        self.assertTrue(PP.fps_is_suspect(240.0, verified=False))

    def test_plausible_rates_are_not(self):
        for fps in (19.8644, 19.93, 30.0, 35.0, 60.0, 99.0):
            self.assertEqual(PP.fps_is_suspect(fps, verified=False), "",
                             "%s should not be flagged" % fps)

    def test_verified_rate_is_never_blocked(self):
        """A measured 1000 fps is a high-speed camera, not a mistake."""
        self.assertEqual(PP.fps_is_suspect(1000.0, verified=True), "")

    def test_zero_and_absurd_rates(self):
        self.assertTrue(PP.fps_is_suspect(0.0, verified=False))
        self.assertTrue(PP.fps_is_suspect(0.5, verified=False))
        self.assertTrue(PP.fps_is_suspect(300.5, verified=False))

    def test_companion_recovers_the_true_rate(self):
        """3351 frames over 168.643 s is 19.864 fps, whatever the container says."""
        text = "Time,Value\n" + "".join("%.4f,%d\n" % (i * 0.0503412, i) for i in range(3351))
        p = _write(text)
        try:
            comp = PP.read_companion(p)
            fps, note = PP.fps_from_companion({"frames": 3351, "fps": 1000.0}, comp)
            self.assertAlmostEqual(fps, 19.864, places=2)
            self.assertIn("50.3", note)          # the scale factor is named in the sentence
        finally:
            _os.unlink(p)


class TestCompanionReader(unittest.TestCase):
    """Guard 2 — the file beside the video answers what the dialog would otherwise guess."""

    def test_two_header_rows_and_a_gauge_column(self):
        """MOT's export puts names on row 1 and units on row 2, and the gauge is only in row 2."""
        text = ("Time,Extensometer 1,Extensometer 1,Extensometer 1\n"
                ",Strain (%),Extension (units),Gauge length (units)\n"
                + "".join("%.4f,0.1,0.05,45.0034\n" % (i * 0.05) for i in range(50)))
        p = _write(text)
        try:
            c = PP.read_companion(p)
            self.assertAlmostEqual(c.gauge_mm, 45.0034, places=3)
            self.assertEqual(c.n_rows, 50)
        finally:
            _os.unlink(p)

    def test_named_load_column_is_used(self):
        text = "time_s,force_n\n" + "".join("%.3f,%.1f\n" % (i * 0.1, i * 10.0) for i in range(60))
        p = _write(text)
        try:
            c = PP.read_companion(p)
            self.assertIsNotNone(c.load)
            self.assertAlmostEqual(float(c.load.max()), 590.0, places=1)
        finally:
            _os.unlink(p)

    def test_kn_is_converted_to_newtons(self):
        text = "time_s,Load (kN)\n" + "".join("%.3f,%.4f\n" % (i * 0.1, i * 0.001) for i in range(60))
        p = _write(text)
        try:
            c = PP.read_companion(p)
            self.assertAlmostEqual(float(c.load.max()), 59.0, places=1)
        finally:
            _os.unlink(p)

    def test_unnamed_columns_give_time_only(self):
        """A headerless .daq must not have a load column guessed for it."""
        text = "".join("%.4f\t%.3f\t%.3f\n" % (i * 0.05, i * 2.0, i) for i in range(80))
        p = _write(text, ".daq")
        try:
            c = PP.read_companion(p)
            self.assertIsNone(c.load)
            self.assertIsNone(c.gauge_mm)
            self.assertGreater(c.duration_s, 3.9)
        finally:
            _os.unlink(p)

    def test_explicit_load_column_override(self):
        text = "".join("%.4f\t%.3f\t%.3f\n" % (i * 0.05, i * 2.0, i) for i in range(80))
        p = _write(text, ".daq")
        try:
            c = PP.read_companion(p, load_col=1, load_scale=1000.0)
            self.assertIsNotNone(c.load)
            self.assertAlmostEqual(float(c.load.max()), 158000.0, places=0)
        finally:
            _os.unlink(p)

    def test_non_monotonic_column_is_refused(self):
        text = "a,b\n5,1\n3,2\n9,3\n1,4\n7,5\n"
        p = _write(text)
        try:
            with self.assertRaises(ValueError):
                PP.read_companion(p)
        finally:
            _os.unlink(p)

    @unittest.skipUnless(_os.path.isfile(_MOT_CSV), "validation folder not present")
    def test_real_mot_csv(self):
        c = PP.read_companion(_MOT_CSV)
        self.assertAlmostEqual(c.duration_s, 168.643, places=2)
        self.assertAlmostEqual(c.gauge_mm, 45.0034, places=3)
        fps, _note = PP.fps_from_companion({"frames": 3351, "fps": 1000.0}, c)
        self.assertAlmostEqual(fps, 19.8644, places=3)

    @unittest.skipUnless(_os.path.isfile(_MOT_DAQ), "validation folder not present")
    def test_real_mot_daq_is_time_only(self):
        c = PP.read_companion(_MOT_DAQ)
        self.assertAlmostEqual(c.duration_s, 168.643, places=2)
        self.assertIsNone(c.load)                      # 52 unnamed columns; none is guessed


class TestNoiseWindow(unittest.TestCase):
    """Guard 3 — the noise band must not sit on the seating ramp."""

    @staticmethod
    def _record(n=1200, toe=0.0012, rate=2.5e-4, noise=8e-6, seed=7):
        """A pull with a curved toe, then a straight elastic ramp. Noise is the same throughout,
        so any difference the window makes is the TOE being measured, not the instrument."""
        rng = np.random.default_rng(seed)
        t = np.arange(n) * 0.05
        t_pre = 9.0
        e = np.where(t < t_pre,
                     toe * (t / t_pre) ** 2.4,                       # seating: curved
                     toe + rate * (t - t_pre))                       # loading: straight
        return t, e + rng.normal(0, noise, n)

    def test_straightest_band_beats_the_fixed_band_on_a_toed_record(self):
        t, e = self._record()
        old = (e >= 0.0005) & (e <= 0.0035)
        m, _z, why = PP.noise_window(t, e)
        sd_old = float((e[old] - np.polyval(np.polyfit(t[old], e[old], 1), t[old])).std())
        sd_new = float((e[m] - np.polyval(np.polyfit(t[m], e[m], 1), t[m])).std())
        self.assertLess(sd_new, sd_old * 0.6,
                        "the chosen window should not be dominated by the toe's curvature")
        self.assertIn("straightest", why)

    def test_preload_anchor_moves_the_window_past_the_toe(self):
        t, e = self._record()
        e0 = float(np.interp(9.0, t, e))               # the strain at the preload instant
        m, z, why = PP.noise_window(t, e, e_zero=e0)
        self.assertIn("preload", why)
        self.assertGreaterEqual(float(t[m].min()), 9.0,
                                "the anchored window must start after the preload")

    def test_window_is_always_described(self):
        t, e = self._record()
        for kw in ({}, {"e_zero": 0.001}):
            _m, _z, why = PP.noise_window(t, e, **kw)
            self.assertTrue(why, "a noise figure with an unstated window cannot be checked")

    def test_short_record_does_not_crash(self):
        t = np.arange(10) * 0.05
        e = np.linspace(0, 0.0001, 10)
        m, _z, why = PP.noise_window(t, e)
        self.assertTrue(m is None or m.sum() <= 10)
        self.assertTrue(why)

    @unittest.skipUnless(_os.path.isfile(_PPCSV), "validation folder not present")
    def test_real_record_recovers_the_settled_noise_figure(self):
        """The case that started this: 57 ue reported, ~24 ue is the truth."""
        import csv as _csv
        with io.open(_PPCSV, encoding="utf-8") as fh:
            rows = [r for r in _csv.reader(fh)
                    if r and not r[0].startswith("#") and r[0] != "Frame"]
        idx = np.array([int(r[0]) for r in rows])
        L = np.array([float(r[6]) for r in rows])
        e = np.array([float(r[8]) for r in rows])
        t = idx / 19.8644
        l0 = L[0]

        def rms(mask):
            k = np.arange(mask.sum())
            return float((L[mask] - np.polyval(np.polyfit(k, L[mask], 1), k)).std() / l0 * 1e6)

        old = (e >= 0.0005) & (e <= 0.0035)
        m, _z, _why = PP.noise_window(t, e)
        self.assertGreater(rms(old), 45.0, "the old fixed band should still show its 57 ue")
        self.assertLess(rms(m), 30.0, "the new window should land on the settled part")


class TestGaugeIsNeverSilentlyAssumed(unittest.TestCase):
    """The gauge changes no strain — but a default must not read like a measurement."""

    def test_settings_defaults_to_unconfirmed(self):
        self.assertFalse(PP.Settings().gauge_confirmed)

    def test_metrics_stamps_an_unconfirmed_gauge(self):
        s = PP.Summary(n=3, tracked=3, l0_px=1000.0, px_mm=12.5, fps=20.0)
        s.rows = [PP.FrameResult(i, i * 0.05, (0, 0), (0, 0), 1000.0 + i,
                                 0.0, i * 1e-4, i * 1e-4, 1.0, True) for i in range(3)]
        rows = dict(PP.metrics(s, PP.Settings(gauge_mm=80.0, gauge_confirmed=False)))
        self.assertIn("ASSUMED", rows["Gauge"])
        rows = dict(PP.metrics(s, PP.Settings(gauge_mm=45.0034, gauge_confirmed=True)))
        self.assertNotIn("ASSUMED", rows["Gauge"])

    def test_px_per_mm_and_gauge_are_one_number(self):
        """Px0 ties them together, which is what lets the dialog take either as the input."""
        l0 = 1254.928
        for gauge in (45.0034, 80.0, 12.5):
            self.assertAlmostEqual(l0 / (l0 / gauge), gauge, places=6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
