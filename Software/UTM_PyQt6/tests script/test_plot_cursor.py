"""The hover data cursor on the post-processing plot.

    python "tests script/test_plot_cursor.py"            (run from Software/UTM_PyQt6)

His ask (2026-09-05): wander the cursor over the strain plot and read the data point under it.
The readout must snap to the nearest RECORDED point (not interpolate), name the right series
when several runs are overlaid, survive the ax.clear() every live redraw performs, stay out of
the toolbar's way while panning or zooming, and never leak into "Save plot…" output — animated
artists are invisible to savefig, so the last one is checked by construction here.
"""
import os as _os
import sys as _sys
_os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import unittest

import numpy as np
from PyQt6.QtWidgets import QApplication

from matplotlib.backend_bases import MouseEvent

_app = QApplication.instance() or QApplication([])

import utm_postdlg as PD


def _tab():
    t = PD.PostProcTab()
    t._report_loss = lambda *a, **k: None          # never let a modal block an offscreen run
    t.resize(1200, 700)
    return t


def _move_to(tab, tx, ty, dx=0.0, dy=0.0):
    """Synthesise a mouse move at data point (tx, ty) plus a screen-pixel nudge."""
    px, py = tab.ax.transData.transform((tx, ty))
    ev = MouseEvent("motion_notify_event", tab.canvas, px + dx, py + dy)
    tab.canvas.callbacks.process("motion_notify_event", ev)


class CursorReadsTheCurve(unittest.TestCase):
    def setUp(self):
        self.tab = _tab()
        self.t = np.arange(0.0, 8.0, 0.05)
        self.e = 0.4 * self.t                       # % strain, easy to predict
        self.tab.ax.plot(self.t, self.e, color="#e8590c", label="S26")
        self.tab.canvas.draw()

    def test_hover_snaps_to_the_nearest_recorded_point(self):
        _move_to(self.tab, 4.02, 0.4 * 4.02, dx=3, dy=-2)   # near t=4.00, between samples
        cur = self.tab.plotCursor
        self.assertTrue(cur._visible)
        txt = cur._note.get_text()
        self.assertIn("S26", txt)
        self.assertIn("t = 4.000 s", txt, "must snap to the recorded sample, not interpolate")
        self.assertIn("ε = 1.600 %", txt)
        self.assertEqual(list(cur._dot.get_xdata()), [4.0])

    def test_far_from_any_curve_shows_nothing(self):
        _move_to(self.tab, 1.0, 3.0)                 # empty space well above the line
        self.assertFalse(self.tab.plotCursor._visible)

    def test_names_the_nearer_of_two_series(self):
        self.tab.ax.plot(self.t, self.e + 1.0, color="#1f6fb4", label="S27")
        self.tab.canvas.draw()
        _move_to(self.tab, 5.0, 0.4 * 5.0 + 1.0, dy=2)
        self.assertIn("S27", self.tab.plotCursor._note.get_text())
        _move_to(self.tab, 5.0, 0.4 * 5.0, dy=-2)
        self.assertIn("S26", self.tab.plotCursor._note.get_text())
        self.assertNotIn("S27", self.tab.plotCursor._note.get_text())

    def test_toolbar_pan_zoom_suppresses_it(self):
        self.tab.plotCursor._mode = lambda: "zoom rect"
        _move_to(self.tab, 4.0, 1.6)
        self.assertFalse(self.tab.plotCursor._visible)

    def test_survives_the_clear_every_redraw_performs(self):
        _move_to(self.tab, 4.0, 1.6)
        self.assertTrue(self.tab.plotCursor._visible)
        self.tab._redraw_plot()                      # no runs -> clears the axes entirely
        self.tab.canvas.draw()
        self.assertFalse(self.tab.plotCursor._visible, "artists died with ax.clear()")
        self.tab.ax.plot(self.t, self.e, color="#e8590c", label="S26")   # a later replot
        self.tab.canvas.draw()
        _move_to(self.tab, 2.0, 0.8)
        self.assertTrue(self.tab.plotCursor._visible, "must re-create its artists lazily")
        self.assertIn("t = 2.000 s", self.tab.plotCursor._note.get_text())

    def test_never_reaches_a_saved_plot(self):
        _move_to(self.tab, 4.0, 1.6)
        cur = self.tab.plotCursor
        self.assertTrue(cur._dot.get_animated() and cur._note.get_animated(),
                        "animated is what keeps savefig and reports clean of the cursor")
        self.assertTrue(str(cur._dot.get_label()).startswith("_"),
                        "an unprefixed label would put the cursor dot in the legend")


if __name__ == "__main__":
    try:
        _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    unittest.main(verbosity=2)
