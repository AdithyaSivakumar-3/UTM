"""Re-acquisition after a violent displacement, and the grace window that hosts it.

    python "tests script/test_reacquire.py"              (run from Software/UTM_PyQt6)

Born from S38 (2026-09-06): at the snap the specimen recoiled sideways past the local search
window and came to rest intact — 4.2 s of perfectly trackable video were unreachable, because
every per-frame search is anchored to the LAST position. analyse() now hunts the whole frame
for the pair while a loss is inside the grace window, resumes when geometry and template both
agree, and still stops — at the ORIGINAL loss instant, correctly reported — when nothing ever
comes back. On S38 itself the defaults now track 2679/2686 frames to the video's final frame.
"""
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import tempfile
import unittest

import cv2
import numpy as np

import utm_postproc as PP


def _video(n, dots):
    """dots(i) -> list of (x, y) dark dots to draw on frame i (empty list = markers gone)."""
    path = _os.path.join(tempfile.mkdtemp(prefix="utm_reacq_"), "v.avi")
    vw = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"MJPG"), 30.0, (640, 480))
    for i in range(n):
        fr = np.full((480, 640, 3), 235, np.uint8)
        for (x, y) in dots(i):
            cv2.circle(fr, (int(round(x * 16)), int(round(y * 16))), 12 * 16,
                       (25, 25, 25), -1, lineType=cv2.LINE_AA, shift=4)
        vw.write(fr)
    vw.release()
    return path


def _run(path, cfg):
    gen = PP.analyse(path, PP.Box(320, 100, cfg.box_half), PP.Box(320, 380, cfg.box_half), cfg)
    try:
        while True:
            next(gen)
    except StopIteration as st:
        return st.value


class DisplacementIsSurvivable(unittest.TestCase):
    def test_snap_sideways_reacquires_and_runs_to_the_end(self):
        """Markers jump 90 px sideways at frame 30 (far past the 40 px search window) and stay
        there. The old behaviour lost the rest of the video; now: re-acquire, run to the end."""
        def dots(i):
            dx = 0 if i < 30 else 90
            return [(320 + dx, 100), (320 + dx, 380)]
        s = _run(_video(90, dots), PP.Settings(step=1))
        self.assertFalse(s.stopped_early)
        self.assertEqual(s.rows[-1].idx, 89, "did not reach the end of the video")
        self.assertGreater(s.coverage, 90)
        self.assertTrue(any("re-acquired" in r.note for r in s.rows))
        # tracking is genuinely ON the displaced markers afterwards
        tail = [r for r in s.rows[35:] if r.ok][-1]
        self.assertLess(abs(tail.a[0] - 410), 3)

    def test_relaxed_pair_is_accepted(self):
        """After a snap the specimen may spring BACK — the pair comes to rest up to 30 % shorter.
        That release is real data and must be re-acquired, not rejected as implausible."""
        def dots(i):
            if i < 30:
                return [(320, 100), (320, 380)]
            return [(400, 128), (400, 352)]          # displaced AND 20 % shorter
        s = _run(_video(90, dots), PP.Settings(step=1))
        self.assertFalse(s.stopped_early)
        tail = [r for r in s.rows if r.ok][-1]
        self.assertLess(abs(tail.l_px - 224), 4)

    def test_truly_gone_still_stops_and_names_the_loss_instant(self):
        """Markers vanish for good at frame 50. The run must still stop — after the grace —
        and 'markers gone at' must name frame ~50, not the moment the search gave up."""
        def dots(i):
            return [(320, 100), (320, 380)] if i < 50 else []
        s = _run(_video(300, dots), PP.Settings(step=1))
        self.assertTrue(s.stopped_early)
        self.assertLess(abs(s.lost_at_frame - 50), 4,
                        "lost_at must be the loss, not the give-up (%s)" % s.lost_at_frame)
        self.assertLess(s.rows[-1].idx, 55, "trailing lost rows must be trimmed")
        self.assertIn("re-acquired within", s.lost_reason)

    def test_extras_ride_the_reacquire(self):
        """An extra pair jumps with the specimen and must come back with it."""
        def dots(i):
            dx = 0 if i < 30 else 90
            return [(320 + dx, 100), (320 + dx, 380),
                    (200 + dx, 240), (440 + dx, 240)]
        s = _run_extra(_video(90, dots))
        self.assertFalse(s.stopped_early)
        ext_ok = [r.extra[0][6] for r in s.rows[40:] if r.ok and r.extra]
        self.assertTrue(ext_ok and all(ext_ok[-20:]), "extra pair did not follow the jump")


def _run_extra(path):
    cfg = PP.Settings(step=1)
    gen = PP.analyse(path, PP.Box(320, 100, cfg.box_half), PP.Box(320, 380, cfg.box_half), cfg,
                     extras=[(PP.Box(200, 240, 24), PP.Box(440, 240, 24),
                              "transverse", "width")])
    try:
        while True:
            next(gen)
    except StopIteration as st:
        return st.value


if __name__ == "__main__":
    try:
        _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    unittest.main(verbosity=2)
