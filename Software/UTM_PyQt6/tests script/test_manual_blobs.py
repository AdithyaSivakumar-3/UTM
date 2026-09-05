"""Manual blob selection (Mirza's suggestion, 2026-09-05) — does the override actually override?

    python "tests script/test_manual_blobs.py"           (run from Software/UTM_PyQt6)

The feature exists for the case where the auto gates fight the markers, so the central test
manufactures exactly that: a circularity gate strict enough to reject S13's real spray dots.
Auto must fail on that frame and manual must keep tracking the same two centroids — on the REAL
detect_blobs, real frames, no reimplementation.

The seed-following test walks a stretch of the actual pull and requires the picked pair to keep
reporting 2/2 while the separation grows, which is the property that makes one pick before the
pull survive the whole test.

Runs headless (QCoreApplication, no camera) — the same construction dic_replay uses.
"""
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import glob
import unittest

import cv2
import numpy as np

_RUN = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                     "Test data", "8.6.20 - Tensile test to Failure",
                     "Specimen_S13_V2_Spray_Video7")
_FRAMES = sorted(glob.glob(_os.path.join(_RUN, "*", "frames", "f*.png")))


def _cm(mode="Black", px0=None):
    from PyQt6.QtCore import QCoreApplication
    from camera_manager import CameraManager
    if QCoreApplication.instance() is None:
        _cm._app = QCoreApplication([])
    cm = CameraManager()
    cm.set_specimen_mode(mode)
    cm.initial_distance = px0
    cm.error_occurred.connect(lambda _m: None)
    return cm


def _frame(i):
    g = cv2.imread(_FRAMES[i], cv2.IMREAD_GRAYSCALE)
    assert g is not None
    return g


@unittest.skipUnless(_FRAMES, "S13 frames not present on this machine")
class ManualOverridesTheGates(unittest.TestCase):

    def test_auto_baseline_finds_the_pair(self):
        cm = _cm()
        found = cm.detect_blobs(_frame(200))
        self.assertEqual(len(found), 2)

    def test_manual_survives_a_gate_that_kills_auto(self):
        """The reason the feature exists, as a test."""
        cm = _cm()
        base = cm.detect_blobs(_frame(200))
        self.assertEqual(len(base), 2)

        cm.MIN_CIRCULARITY = 0.995          # no sprayed dot is this round — auto must now fail
        self.assertLess(len(cm.detect_blobs(_frame(200))), 2)

        cm.set_manual_seeds([(x + 4, y - 3) for x, y in base])   # clicks land NEAR, not ON
        cm.set_blob_mode("manual")
        got = cm.detect_blobs(_frame(200))
        self.assertEqual(len(got), 2)
        for (gx, gy), (bx, by) in zip(got, base):
            self.assertLess(abs(gx - bx) + abs(gy - by), 2.0,
                            "manual pick did not land on the same marker")

    def test_seeds_follow_through_the_pull(self):
        """One pick before the pull must survive the whole test: 2/2 on every strided frame,
        with the separation growing as the specimen stretches."""
        cm = _cm()
        base = cm.detect_blobs(_frame(100))
        self.assertEqual(len(base), 2)
        cm.MIN_CIRCULARITY = 0.995
        cm.set_manual_seeds(base)
        cm.set_blob_mode("manual")
        seps = []
        for i in range(100, 1100, 25):
            got = cm.detect_blobs(_frame(i))
            self.assertEqual(len(got), 2, "lost the pair at frame %d" % i)
            seps.append(abs(got[1][1] - got[0][1]))
        self.assertGreater(seps[-1], seps[0] + 2.0, "separation never grew — not tracking a pull")
        # and the seeds themselves moved with the markers
        s0, s1 = cm.manual_seeds
        self.assertGreater(abs(s1[1] - s0[1]), seps[0])

    def test_manual_without_seeds_falls_back_to_auto(self):
        cm = _cm()
        cm.set_blob_mode("manual")           # setting flipped first, seeds never picked
        self.assertIsNone(cm.manual_seeds)
        self.assertEqual(len(cm.detect_blobs(_frame(200))), 2)

    def test_merged_or_missing_component_is_a_dropout_not_a_pair(self):
        """Both seeds resolving to ONE component must yield one marker, never a fabricated two."""
        cm = _cm()
        base = cm.detect_blobs(_frame(200))
        top = min(base, key=lambda p: p[1])
        cm.set_manual_seeds([(top[0] - 20, top[1] - 20), (top[0] + 20, top[1] + 20)])
        cm.set_blob_mode("manual")
        got = cm.detect_blobs(_frame(200))
        self.assertEqual(len(got), 1)

    def test_far_seed_is_lost_not_substituted(self):
        """A seed pointing at empty specimen must find nothing — not grab the nearest bright
        thing beyond the search radius."""
        cm = _cm()
        base = cm.detect_blobs(_frame(200))
        (tx, ty) = min(base, key=lambda p: p[1])
        mid_gauge = (tx, (base[0][1] + base[1][1]) / 2.0)   # dark specimen, no component here
        cm.set_manual_seeds([(tx, ty), mid_gauge])
        cm.set_blob_mode("manual")
        got = cm.detect_blobs(_frame(200))
        self.assertEqual(len(got), 1)

    def test_pair_guards_still_protect_manual_mode(self):
        """The Px0-separation plausibility guard runs after the branch, so a manual pair that
        collapses (post-fracture) is rejected exactly as an auto pair would be."""
        cm = _cm(px0=1668.0)
        base = cm.detect_blobs(_frame(200))
        top = min(base, key=lambda p: p[1])
        # a "pair" ~100 px apart against Px0 1668, via a synthetic dot painted onto the frame.
        # SAME COLUMN as the real marker: the frames are portrait (419 wide) and Black mode's
        # mask_x blanks the side columns, so a dot offset in x lands in the masked zone and
        # simply vanishes — which is how the first version of this test fooled itself.
        # 100 px below centre clears the ~60 px marker radius, so they stay two components.
        g = _frame(200).copy()
        cv2.circle(g, (int(top[0]), int(top[1]) + 100), 12, 255, -1)
        cm.set_manual_seeds([top, (top[0], top[1] + 100)])
        cm.set_blob_mode("manual")
        self.assertEqual(cm.detect_blobs(g), [])


class ViewToFrameMapping(unittest.TestCase):
    """The picker dialog's click maths, as the pure function it is."""

    def test_roundtrip_centre_and_corners(self):
        from utm_blobpick import view_to_frame
        vw, vh, iw, ih = 1180, 560, 2348, 419      # the real letterboxed geometry
        sc = min(vw / iw, vh / ih)
        offy = (vh - ih * sc) / 2
        self.assertAlmostEqual(view_to_frame(vw, vh, iw, ih, vw / 2, vh / 2)[0],
                               iw / 2, delta=1.0)
        # one pixel IN from the top-left of the image area — the exact border pixel is allowed
        # to miss either way (it sits on a float boundary), a real click never lands there
        fx, fy = view_to_frame(vw, vh, iw, ih, 1, offy + 1)
        self.assertLess(fx, 4)
        self.assertLess(fy, 4)

    def test_letterbox_margin_is_a_miss(self):
        from utm_blobpick import view_to_frame
        self.assertIsNone(view_to_frame(1180, 560, 2348, 419, 5, 5))
        self.assertIsNone(view_to_frame(1180, 560, 2348, 419, 5, 555))


if __name__ == "__main__":
    try:
        _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    unittest.main(verbosity=2)
