"""Manual blob selection — the picker dialog behind the Select Blobs button.

Mirza's suggestion (2026-09-05): when the auto detector's gates fight the markers (odd shape,
wrong size, an interloper the chooser keeps preferring), let the operator SAY which two things
are the markers. This dialog shows one frozen frame from the live camera; the operator clicks
the two markers; the CameraManager then tracks the component nearest each pick, seeds following
the markers frame to frame (see CameraManager._manual_pick).

Deliberately a frozen frame, not a live view: picking on a moving image invites a click that
lands where the marker WAS, and the seed-follow logic makes staleness of a few seconds
irrelevant — the search radius is 150 px and the specimen is not moving between opening this
dialog and pressing OK.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QFont
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QDialogButtonBox)

import numpy as np

VIEW_W, VIEW_H = 1180, 560          # the picking canvas is scaled to fit this box


def view_to_frame(view_w, view_h, img_w, img_h, x, y):
    """Map a click on the letterboxed view back to raw-frame pixels, or None if it missed.

    Pure function, no Qt in the signature, so the mapping maths is testable without a display:
    the image is scaled by min(view/img) and centred, so undo the offsets then the scale.
    """
    sc = min(view_w / img_w, view_h / img_h)
    w, h = img_w * sc, img_h * sc
    offx, offy = (view_w - w) / 2.0, (view_h - h) / 2.0
    fx, fy = (x - offx) / sc, (y - offy) / sc
    if 0 <= fx < img_w and 0 <= fy < img_h:
        return fx, fy
    return None


class _Canvas(QLabel):
    """The clickable frame view. Owns the pick list; the dialog reads it."""

    def __init__(self, frame, seeds, on_change):
        super().__init__()
        self._frame = np.ascontiguousarray(frame)
        self._picks = list(seeds or [])[:2]
        self._on_change = on_change
        h, w = self._frame.shape[:2]
        sc = min(VIEW_W / w, VIEW_H / h)
        self._view = (int(round(w * sc)), int(round(h * sc)))
        self.setFixedSize(*self._view)
        self.setCursor(Qt.CursorShape.CrossCursor)
        qi = QImage(self._frame.data, w, h, self._frame.strides[0],
                    QImage.Format.Format_Grayscale8)
        self._base = QPixmap.fromImage(qi).scaled(
            *self._view, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self._redraw()

    def picks(self):
        return list(self._picks)

    def reset(self):
        self._picks = []
        self._redraw()
        self._on_change()

    def mousePressEvent(self, ev):
        h, w = self._frame.shape[:2]
        pt = view_to_frame(self.width(), self.height(), w, h,
                           ev.position().x(), ev.position().y())
        if pt is None:
            return
        if len(self._picks) >= 2:
            self._picks = []                    # third click starts over — cheaper than a mode
        self._picks.append(pt)
        self._redraw()
        self._on_change()

    def _redraw(self):
        h, w = self._frame.shape[:2]
        sc = min(self.width() / w, self.height() / h)
        pm = QPixmap(self._base)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        p.setFont(font)
        for i, (fx, fy) in enumerate(self._picks):
            x, y = fx * sc, fy * sc
            pen = QPen(QColor("#ff9500"))
            pen.setWidth(2)
            p.setPen(pen)
            p.drawEllipse(int(x - 14), int(y - 14), 28, 28)
            p.drawLine(int(x - 20), int(y), int(x + 20), int(y))
            p.drawLine(int(x), int(y - 20), int(x), int(y + 20))
            p.drawText(int(x + 18), int(y - 12), "%d" % (i + 1))
        p.end()
        self.setPixmap(pm)


class BlobPickDialog(QDialog):
    """Click the two markers; OK arms manual mode with those seeds.

    `picks()` returns the two (x, y) raw-frame points after accept().
    """

    def __init__(self, frame, seeds=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select blobs — click the two markers")
        lay = QVBoxLayout(self)
        self._hint = QLabel()
        self._hint.setWordWrap(True)
        lay.addWidget(self._hint)
        self._canvas = _Canvas(frame, seeds, self._refresh)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self._canvas)
        row.addStretch(1)
        lay.addLayout(row)

        btns = QDialogButtonBox()
        self._reset = QPushButton("Reset")
        self._reset.clicked.connect(self._canvas.reset)
        btns.addButton(self._reset, QDialogButtonBox.ButtonRole.ResetRole)
        self._ok = btns.addButton(QDialogButtonBox.StandardButton.Ok)
        btns.addButton(QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)
        self._refresh()

    def picks(self):
        return self._canvas.picks()

    def _refresh(self):
        n = len(self._canvas.picks())
        self._ok.setEnabled(n == 2)
        self._hint.setText(
            ("Click marker <b>%d of 2</b>. The exact centre does not matter — the tracker takes "
             "the bright component nearest the click and follows it from there. A third click "
             "starts over." % (n + 1)) if n < 2 else
            "Both markers picked — <b>OK</b> switches detection to manual and tracks these two. "
            "Shape and size gates no longer apply to them.")
