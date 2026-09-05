"""The scale that retires the ASSUMED-gauge warning — and where it may come from.

    python "tests script/test_scale_sidecar.py"          (run from Software/UTM_PyQt6)

His ask (2026-09-05): after picking markers, the amber "gauge is the default 80 mm" text felt
pointless. Pixels alone carry no millimetres — Px₀ is measured, the mm scale is not — so the
warning cannot simply vanish at selection. What CAN retire it honestly is the capture's own
record: the rig writes "# DIC Calibration - px_per_mm:" into every run's CSV. These tests pin
the whole chain: the sidecar sniff (and its refusal to sniff foreign folders), the anchor it
sets at load, the gauge turning into a measurement at box placement, the per-run isolation of
the calibrated scale, and the provenance stamped into the results sheet.
"""
import os as _os
import sys as _sys
_os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import json
import shutil
import tempfile
import unittest

import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QFileDialog

_app = QApplication.instance() or QApplication([])

import utm_postproc as PP
import utm_postdlg as PD

PPM = 20.8528


def _avi(path, n=8):
    vw = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"MJPG"), 30.0, (640, 480))
    for _ in range(n):
        fr = np.full((480, 640, 3), 235, np.uint8)
        cv2.circle(fr, (320, 100), 12, (25, 25, 25), -1)
        cv2.circle(fr, (320, 380), 12, (25, 25, 25), -1)
        vw.write(fr)
    vw.release()
    return path


def _capture_tree(ppm=PPM, gauge=80.0):
    """Specimen_X/cap/video.avi + run.json, calibration CSV beside the capture — our layout."""
    spec = tempfile.mkdtemp(prefix="utm_scale_")
    cap = _os.path.join(spec, "cap")
    _os.makedirs(cap)
    vid = _avi(_os.path.join(cap, "video.avi"))
    with open(_os.path.join(cap, "run.json"), "w", encoding="utf-8") as f:
        json.dump({"note": "capture marker only"}, f)
    with open(_os.path.join(spec, "test.csv"), "w", encoding="utf-8") as f:
        f.write("# UTM capture\n")
        if ppm:
            f.write("# DIC Calibration - px_per_mm: %s\n" % ppm)
        f.write("# Gauge Length: %s mm\n" % gauge)
        f.write("time,load\n0,0\n1,1\n")
    return spec, vid


class SidecarSniff(unittest.TestCase):
    def test_our_capture_yields_its_calibration(self):
        spec, vid = _capture_tree()
        try:
            ppm, gauge, src = PP.scale_from_sidecar(vid)
            self.assertAlmostEqual(ppm, PPM, places=4)
            self.assertAlmostEqual(gauge, 80.0, places=2)
            self.assertEqual(src, "test.csv")
        finally:
            shutil.rmtree(spec, ignore_errors=True)

    def test_a_foreign_flat_folder_is_never_sniffed(self):
        """The MOT folder holds three samples' CSVs side by side — guessing which belongs to a
        video would anchor it to a NEIGHBOUR's optics. No run.json/frames -> no sniff."""
        d = tempfile.mkdtemp(prefix="utm_foreign_")
        try:
            vid = _avi(_os.path.join(d, "video.avi"))
            with open(_os.path.join(d, "other_sample.csv"), "w", encoding="utf-8") as f:
                f.write("# DIC Calibration - px_per_mm: 99.9\ntime\n0\n")
            self.assertIsNone(PP.scale_from_sidecar(vid))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_gauge_only_header_still_helps(self):
        spec, vid = _capture_tree(ppm=None, gauge=45.0)
        try:
            ppm, gauge, src = PP.scale_from_sidecar(vid)
            self.assertIsNone(ppm)
            self.assertAlmostEqual(gauge, 45.0, places=2)
        finally:
            shutil.rmtree(spec, ignore_errors=True)


class TheWarningRetiresItself(unittest.TestCase):
    def setUp(self):
        self.spec, self.vid = _capture_tree()
        self.tab = PD.PostProcTab()
        self.tab._report_loss = lambda *a, **k: None
        self._old = QFileDialog.getOpenFileNames
        QFileDialog.getOpenFileNames = staticmethod(lambda *a, **k: ([self.vid], ""))

    def tearDown(self):
        QFileDialog.getOpenFileNames = self._old
        shutil.rmtree(self.spec, ignore_errors=True)

    def test_load_anchors_to_the_captures_own_calibration(self):
        self.tab.on_load()
        r = self.tab.run
        self.assertEqual(r.scale_anchor, "pxmm")
        self.assertAlmostEqual(r.px_mm, PPM, places=4)
        self.assertIn("test.csv", r.gauge_src)
        self.assertAlmostEqual(self.tab.pxmm.value(), PPM, places=3)
        txt = self.tab.gaugeWarn.text()
        self.assertIn("Scale is known", txt)
        self.assertNotIn("default", txt, "the amber doubt must not show when the scale is known")

    def test_boxes_turn_the_gauge_into_a_measurement(self):
        self.tab.on_load()
        self.tab.boxes = [(320.0, 100.0), (320.0, 380.0)]      # Px0 = 280 px
        self.tab._refresh_boxes()
        r = self.tab.run
        self.assertTrue(r.gauge_confirmed)
        self.assertAlmostEqual(self.tab.gauge.value(), 280.0 / PPM, places=2)
        self.assertEqual(self.tab.gaugeWarn.text(), "", "nothing left to warn about")
        self.assertIn("MEASURED", self.tab.l0Lbl.text())
        self.assertIn("test.csv", r.gauge_src, "provenance must survive the box placement")

    def test_a_foreign_video_still_gets_the_amber_warning(self):
        d = tempfile.mkdtemp(prefix="utm_foreign_")
        try:
            vid2 = _avi(_os.path.join(d, "mot.avi"))
            QFileDialog.getOpenFileNames = staticmethod(lambda *a, **k: ([vid2], ""))
            self.tab.on_load()
            self.assertEqual(self.tab.run.scale_anchor, "gauge")
            self.assertIn("default", self.tab.gaugeWarn.text())
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_each_run_keeps_its_own_scale(self):
        """Selecting a foreign run and coming back must restore THIS run's calibration — the
        spin box is shared UI, and the previous behaviour let one video's scale leak in."""
        self.tab.on_load()
        d = tempfile.mkdtemp(prefix="utm_foreign_")
        try:
            vid2 = _avi(_os.path.join(d, "mot.avi"))
            QFileDialog.getOpenFileNames = staticmethod(lambda *a, **k: ([vid2], ""))
            self.tab.on_load()                                  # selects the foreign run
            self.assertEqual(self.tab.run.scale_anchor, "gauge")
            self.tab.runList.setCurrentRow(0)
            self.tab.on_select_run(0)
            self.assertAlmostEqual(self.tab.pxmm.value(), PPM, places=3)
            self.assertIn("Scale is known", self.tab.gaugeWarn.text())
        finally:
            shutil.rmtree(d, ignore_errors=True)


class TheSheetNamesTheSource(unittest.TestCase):
    def test_gauge_row_carries_where_it_came_from(self):
        cfg = PP.Settings(gauge_mm=13.43, gauge_confirmed=True,
                          gauge_src="measured from test.csv calibration")
        s = PP.Summary(l0_px=280.0, px_mm=PPM, fps=30.0)
        s.rows = [PP.FrameResult(idx=i, t=i / 30.0, ok=True, a=(320, 100), b=(320, 380),
                                 l_px=280.0 + i, dx_px=float(i), cauchy=i / 280.0,
                                 true=i / 280.0, corr=1.0)
                  for i in range(6)]
        s.n = s.tracked = 6
        rows = dict(PP.metrics(s, cfg))
        self.assertIn("measured from test.csv calibration", rows["Gauge"])
        self.assertNotIn("ASSUMED", rows["Gauge"])
        self.assertIn("280.00 px", rows["Px0 (L0)"])

    def test_unconfirmed_still_says_assumed(self):
        cfg = PP.Settings(gauge_mm=80.0, gauge_confirmed=False)
        s = PP.Summary(l0_px=280.0, px_mm=280.0 / 80.0, fps=30.0)
        s.rows = [PP.FrameResult(idx=i, t=i / 30.0, ok=True, a=(320, 100), b=(320, 380),
                                 l_px=280.0, dx_px=0.0, cauchy=0.0, true=0.0, corr=1.0)
                  for i in range(6)]
        s.n = s.tracked = 6
        rows = dict(PP.metrics(s, cfg))
        self.assertIn("ASSUMED", rows["Gauge"])


if __name__ == "__main__":
    try:
        _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    unittest.main(verbosity=2)
