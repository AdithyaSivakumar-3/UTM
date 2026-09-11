"""The DIC Post-Processing tab: load a recorded video, place a virtual extensometer, get strain.

Left half is the video and everything that decides the measurement; right half is the strain-vs-time
plot, drawn live as the analysis runs. The split is deliberate — the operator sets up on the left
and watches the answer appear on the right, without either half moving.

The measurement itself is utm_postproc; nothing here computes strain. That module in turn calls
utm_dic.dic_strain, the same function the live rig calls, so a video replayed here and the pull
that produced it cannot disagree about what strain means.

Placing the extensometer:
    Click the frame to drop box A, click again for box B, or press Auto-detect for sprayed dots.
    A click near a marker snaps to its computed centre; a click in open space stays where it is
    put, which is what a speckle pattern needs. Drag a box to move it freely, and nudge it with
    the arrow keys — one frame pixel at a time, ten with Shift.

    The gauge length in mm is the physical distance BETWEEN THE BOXES — it sets px/mm and nothing
    else. Strain is a pixel ratio, so an unknown or wrong gauge cannot corrupt the strain trace;
    it only makes the px/mm readout meaningless.

Comparing several videos:
    Add as many as you like. Each keeps its OWN extensometer, frame rate, box size and method —
    two videos never have their markers in the same place, and an extensometer recording shares
    neither the frame rate nor the scale of ours. Set each up, then Run all pending: they are
    measured one after another, and every completed run stays on the plot with its own colour and
    legend label. Rename a run by double-clicking it; the label is what the legend shows.

    Sequential rather than parallel on purpose. The point is watching each pull as it is measured,
    and several videos decoding at once would compete for the same disk while showing nothing.
"""
import os
import time
from dataclasses import dataclass

import numpy as np
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint, QSize, QTimer
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QFont
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
                             QFileDialog, QDoubleSpinBox, QSpinBox, QGroupBox, QSplitter,
                             QProgressBar, QMessageBox, QSlider, QCheckBox, QComboBox,
                             QListWidget, QListWidgetItem, QInputDialog, QDialog, QFrame,
                             QScrollArea, QTableWidget, QTableWidgetItem,
                             QApplication)

from matplotlib.backends.backend_qtagg import (FigureCanvasQTAgg as FigureCanvas,
                                                NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

import utm_postproc as PP

# The tab is constructed inside a try/except in main._setup_postproc_tab, and a missing theme
# module must not be what removes the tab — so this one is optional and every use is guarded.
try:
    import theme as _theme
except Exception:                                                    # pragma: no cover
    _theme = None


# Extra-pair colours, ONE rule for the frame view and the plot: what you place as purple
# boxes arrives as the purple curve. Colour says WHICH pair; linestyle on the plot still says
# what KIND it is (dash-dot axial, dotted width). Indexed within kind so a second axial pair
# stays tellable from the first.
PAIR_COLOURS = {"axial": ["#b197fc", "#9775fa", "#7048e8"],
                "transverse": ["#fcc419", "#f59f00"]}


def pair_colour(pairs, j):
    """Colour for extra pair j of `pairs` — by kind, cycling within kind."""
    kind = pairs[j][4]
    k = sum(1 for p in pairs[:j] if p[4] == kind)
    pal = PAIR_COLOURS.get(kind, PAIR_COLOURS["axial"])
    return pal[k % len(pal)]


class FrameView(QLabel):
    """The video frame, the two tracking boxes, and everything needed to place them precisely.

    Three ways to position a box, because clicking alone is not enough on every specimen:
      * click       — places the next box, snapping to a marker centre when one is near
      * drag        — grab an existing box and move it freely, no snapping, for a speckle pattern
                      or a marker the detector will not find
      * arrow keys  — nudge the selected box one frame-pixel at a time (ten with Shift)

    The centre is drawn as a crosshair, not just a box outline. The box is usually much smaller
    than the dot it sits on, so an outline alone gives the eye nothing to judge centring against —
    which is exactly the complaint that prompted the drag and the crosshair.
    """
    clicked = pyqtSignal(float, float)          # in FRAME pixel coordinates
    moved = pyqtSignal(int, float, float)       # box index dragged to a new frame position
    selected = pyqtSignal(int)

    GRAB_SLACK_PX = 14.0                        # extra grab radius, in WIDGET pixels

    def __init__(self):
        super().__init__()
        # 320 px here made the left column taller than the window could show, which pushed
        # the main status line below the fold. The pane still grows to fill whatever is
        # spare — this is only the floor.
        self.setMinimumSize(260, 200)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background:#101317; border:1px solid #2b3138;")
        self.setText("Load a video to begin")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)   # so the arrow keys reach us
        self.setMouseTracking(True)
        self._gray = None
        self._boxes = [None, None]
        self._half = 24
        self._scale = 1.0
        self._ox = self._oy = 0
        self._drag = None            # index of the box being dragged
        self._sel = None             # index of the selected box, for the arrow keys
        self._markers = []           # drawn as faint rings, so the operator sees what will snap
        self._extra = []             # extra pairs: (ax, ay, bx, by, kind, label)

    def set_extra(self, pairs):
        self._extra = list(pairs or [])
        self._redraw()

    def set_frame(self, gray):
        self._gray = gray
        self._redraw()

    def set_boxes(self, a, b, half):
        self._boxes = [a, b]
        self._half = half
        self._redraw()

    def play(self, gray, a, b, half, extra=None):
        """One repaint for a frame AND its box positions — used while the analysis runs.

        set_frame() followed by set_boxes() would redraw twice per frame, which at 25 Hz on a
        2348 px frame is enough scaling work to make the GUI feel heavy for no benefit.
        `extra`, when given, is the extra pairs at THIS frame's scale — the preview stream is
        downscaled before crossing the thread, so the caller scales them with the same factor.
        """
        self._gray = gray
        self._boxes = [a, b]
        self._half = half
        if extra is not None:
            self._extra = extra
        self._redraw()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._redraw()

    def _redraw(self):
        if self._gray is None:
            return
        h, w = self._gray.shape
        buf = np.ascontiguousarray(self._gray)
        img = QImage(buf.data, w, h, w, QImage.Format.Format_Grayscale8)
        pm = QPixmap.fromImage(img).scaled(self.width(), self.height(),
                                           Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation)
        self._scale = pm.width() / w if w else 1.0
        self._ox = (self.width() - pm.width()) // 2
        self._oy = (self.height() - pm.height()) // 2
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Every marker the snap knows about, as a faint ring. Without this the operator cannot
        # tell whether a click will snap or land free — the detector's opinion is invisible.
        p.setPen(QPen(QColor(77, 171, 247, 130), 1, Qt.PenStyle.DotLine))
        for m in self._markers:
            mx, my, mr = m[0] * self._scale, m[1] * self._scale, m[2] * self._scale
            p.drawEllipse(int(mx - mr), int(my - mr), int(2 * mr), int(2 * mr))

        cols = (QColor("#2ecc71"), QColor("#e8590c"))
        pts = []
        for i, bx in enumerate(self._boxes):
            if bx is None:
                continue
            cx, cy = bx[0] * self._scale, bx[1] * self._scale
            r = max(3.0, self._half * self._scale)
            pts.append((cx, cy))
            sel = (i == self._sel)
            p.setPen(QPen(cols[i], 3 if sel else 2))
            p.drawRect(int(cx - r), int(cy - r), int(2 * r), int(2 * r))
            # The crosshair IS the placement: it marks the exact pixel that becomes L0's endpoint.
            p.setPen(QPen(cols[i], 1))
            p.drawLine(int(cx - r - 6), int(cy), int(cx + r + 6), int(cy))
            p.drawLine(int(cx), int(cy - r - 6), int(cx), int(cy + r + 6))
            p.setPen(QPen(QColor("#ffffff"), 1))
            p.drawPoint(int(cx), int(cy))
            p.setPen(QPen(cols[i], 2))
            p.drawText(int(cx + r + 4), int(cy - r - 4), "AB"[i] + (" ◄" if sel else ""))
        if len(pts) == 2:
            p.setPen(QPen(QColor("#4dabf7"), 1, Qt.PenStyle.DashLine))
            p.drawLine(int(pts[0][0]), int(pts[0][1]), int(pts[1][0]), int(pts[1][1]))
        # Extra pairs, drawn lighter than the primary so the extensometer that sets L0 stays
        # visually the main event. Purple = a second axial pair, amber = a width (transverse) one.
        for j, (eax, eay, ebx, eby, kind, _lbl) in enumerate(self._extra):
            col = QColor(pair_colour(self._extra, j))
            r = max(3.0, self._half * self._scale)
            p.setPen(QPen(col, 1, Qt.PenStyle.DashLine))
            p.drawLine(int(eax * self._scale), int(eay * self._scale),
                       int(ebx * self._scale), int(eby * self._scale))
            p.setPen(QPen(col, 2))
            for (x, y) in ((eax, eay), (ebx, eby)):
                cx, cy = x * self._scale, y * self._scale
                p.drawRect(int(cx - r), int(cy - r), int(2 * r), int(2 * r))
            p.drawText(int(ebx * self._scale + r + 4), int(eby * self._scale - r - 4),
                       "P%d" % (j + 1))
        p.end()
        self.setPixmap(pm)

    def set_markers(self, markers):
        self._markers = list(markers or [])
        self._redraw()

    def select(self, i):
        self._sel = i
        self._redraw()

    def _to_frame(self, pos):
        if self._gray is None or self._scale <= 0:
            return None
        x = (pos.x() - self._ox) / self._scale
        y = (pos.y() - self._oy) / self._scale
        h, w = self._gray.shape
        return (float(min(max(x, 0), w - 1)), float(min(max(y, 0), h - 1)))

    def _box_under(self, pos):
        """Which box is under the cursor, in WIDGET pixels — so the grab feels the same at any zoom."""
        for i, bx in enumerate(self._boxes):
            if bx is None:
                continue
            cx = bx[0] * self._scale + self._ox
            cy = bx[1] * self._scale + self._oy
            reach = max(8.0, self._half * self._scale) + self.GRAB_SLACK_PX
            if abs(pos.x() - cx) <= reach and abs(pos.y() - cy) <= reach:
                return i
        return None

    def mousePressEvent(self, e):
        p = self._to_frame(e.position())
        if p is None:
            return
        self.setFocus()
        hit = self._box_under(e.position())
        if hit is not None:
            # Grabbing an existing box MOVES it, and never snaps: this is the manual override for
            # a speckle pattern, or a marker the detector will not find.
            self._drag = hit
            self._sel = hit
            self.selected.emit(hit)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self._redraw()
            return
        self.clicked.emit(*p)

    def mouseMoveEvent(self, e):
        if self._drag is None:
            if self._gray is not None:
                over = self._box_under(e.position())
                self.setCursor(Qt.CursorShape.OpenHandCursor if over is not None
                               else Qt.CursorShape.CrossCursor)
            return
        p = self._to_frame(e.position())
        if p is None:
            return
        self._boxes[self._drag] = p
        self.moved.emit(self._drag, p[0], p[1])
        self._redraw()

    def mouseReleaseEvent(self, e):
        if self._drag is not None:
            self._drag = None
            self.setCursor(Qt.CursorShape.OpenHandCursor)

    def keyPressEvent(self, e):
        """Arrow keys nudge the selected box by one FRAME pixel — ten with Shift.

        The mouse cannot address a single frame pixel once the frame is scaled down to fit the
        pane: one widget pixel is several frame pixels. This is how a placement is finished.
        """
        if self._sel is None or self._boxes[self._sel] is None:
            super().keyPressEvent(e); return
        step = 10.0 if e.modifiers() & Qt.KeyboardModifier.ShiftModifier else 1.0
        dx = dy = 0.0
        k = e.key()
        if k == Qt.Key.Key_Left:
            dx = -step
        elif k == Qt.Key.Key_Right:
            dx = step
        elif k == Qt.Key.Key_Up:
            dy = -step
        elif k == Qt.Key.Key_Down:
            dy = step
        elif k in (Qt.Key.Key_Tab, Qt.Key.Key_Space):
            other = 1 - self._sel
            if self._boxes[other] is not None:
                self._sel = other
                self.selected.emit(other)
                self._redraw()
            return
        else:
            super().keyPressEvent(e); return
        x, y = self._boxes[self._sel]
        h, w = self._gray.shape
        x = float(min(max(x + dx, 0), w - 1)); y = float(min(max(y + dy, 0), h - 1))
        self._boxes[self._sel] = (x, y)
        self.moved.emit(self._sel, x, y)
        self._redraw()


class BigPickDialog(QDialog):
    """The frame at desk size, for placing boxes and pairs the small pane makes guesswork.

    His complaint (2026-09-05): "it is hard to choose from the small window". This is not a
    second implementation of placement — every click, drag and arrow-key nudge is routed into
    the TAB's own handlers (snap-to-marker, pair arming, box-size suggestion included), and the
    view here only MIRRORS the tab's state afterwards. One source of truth, twice the pixels.
    """

    def __init__(self, tab):
        super().__init__(tab)
        self.setWindowTitle("Place boxes — large view")
        self._tab = tab
        lay = QVBoxLayout(self)
        self.hint = QLabel("")
        self.hint.setWordWrap(True)
        self.hint.setStyleSheet("color:#4dabf7; font-weight:bold;")
        lay.addWidget(self.hint)
        self.fv = FrameView()
        scr = QApplication.primaryScreen().availableGeometry()
        self.fv.setMinimumSize(int(scr.width() * 0.70), int(scr.height() * 0.58))
        self.fv.clicked.connect(self._clicked)
        self.fv.moved.connect(self._moved)
        self.fv.selected.connect(tab.view.select)      # keep the two views' selection in step
        lay.addWidget(self.fv)
        row = QHBoxLayout()
        row.addStretch(1)
        done = QPushButton("Done")
        done.clicked.connect(self.close)
        row.addWidget(done)
        lay.addLayout(row)
        self.refresh()

    def _clicked(self, x, y):
        self._tab.on_click(x, y)                       # same snapping, same arming, same logs
        self.refresh()

    def _moved(self, i, x, y):
        self._tab.on_box_moved(i, x, y)
        self.refresh()

    def refresh(self):
        t = self._tab
        src = t.view
        if src._gray is not None:
            self.fv._gray = src._gray
        self.fv._markers = list(getattr(t, "_markers", []) or [])
        self.fv._half = t.boxHalf.value()
        self.fv._boxes = list(t.boxes)
        r = t.run
        self.fv._extra = list(r.extra_pairs) if r is not None else []
        self.fv._redraw()
        if getattr(t, "_arm_extra", None):
            n = 1 if getattr(t, "_extra_first", None) is None else 2
            self.hint.setText("placing a %s pair — click point %d of 2 (clicks snap to a "
                              "marker centre when one is near)"
                              % ("width" if t._arm_extra == "transverse" else "second axial", n))
        else:
            self.hint.setText("click places box %s — drag a box to adjust, arrow keys nudge "
                              "(Shift = ×10)" % "AB"[getattr(t, "_next_box", 0)])


class TrackPopout(QDialog):
    """A big live view of the pull while it is measured, parked at the LEFT of the screen so it
    never covers the plot on the tab's right.

    Fed by the same throttled preview stream as the small pane — no extra decoding, no extra
    load on the analysis; the frames were crossing the thread anyway.
    """

    def __init__(self, tab):
        super().__init__(tab)
        self.setWindowFlag(Qt.WindowType.Window, True)
        self.setWindowTitle("Tracking — live")
        lay = QVBoxLayout(self)
        self.fv = FrameView()
        lay.addWidget(self.fv, 1)
        self.status = QLabel("waiting for the first frame…")
        self.status.setStyleSheet("color:#4dabf7;")
        lay.addWidget(self.status)
        scr = QApplication.primaryScreen().availableGeometry()
        self.resize(int(scr.width() * 0.46), int(scr.height() * 0.60))
        self.move(scr.left() + 12, scr.top() + 80)

    def play(self, gray, a, b, half, extra=None):
        self.fv.play(gray, a, b, half, extra=extra)


class DataCursor:
    """Hover the plot, read the curve: a dot snaps to the nearest RECORDED point and a small
    box names its series, time and value. The toolbar's corner (x, y) readout is wherever the
    mouse happens to be — this is the data, which is what an operator studying a curve wants.

    Built for axes that are redrawn while being watched:
      · the artists are animated + blitted, so a live run's throttled redraws and the readout
        never fight, and — because savefig ignores animated artists — "Save plot…" and the
        report can never carry the cursor into a document;
      · ax.clear() (which every redraw here does) silently discards the artists, so they are
        re-created lazily on the next mouse move rather than owned once at start-up;
      · lines are found at event time from the axes, never held, because every redraw builds
        new ones. Lines labelled "_…" are ignored — that is matplotlib's own "not for the
        legend" convention, and it is what keeps the cursor from chasing its own dot.

    Nearest is nearest ON SCREEN (display space), not in data units — with time in seconds and
    strain in percent, a data-space distance would be dominated by whichever axis has the
    bigger numbers. While the toolbar is panning or zooming the cursor stays hidden: the zoom
    rectangle blits too, and two owners of one background tear the canvas.
    """

    SNAP_PX = 50.0            # how close (screen px) the mouse must be before anything shows

    def __init__(self, canvas, ax, mode=None, colours=None):
        self.canvas, self.ax = canvas, ax
        self._mode = mode or (lambda: "")
        self._colours = colours or (lambda: ("#111111", "#ffffff"))
        self._bg = None
        self._dot = None
        self._note = None
        self._visible = False
        canvas.mpl_connect("motion_notify_event", self._on_move)
        canvas.mpl_connect("draw_event", self._on_draw)
        canvas.mpl_connect("axes_leave_event", lambda ev: self._hide())
        canvas.mpl_connect("figure_leave_event", lambda ev: self._hide())

    # ---- artists ----------------------------------------------------------------------------
    def _alive(self):
        return self._dot is not None and self._dot in self.ax.get_children()

    def _ensure_artists(self):
        if self._alive():
            return
        import matplotlib.lines as mlines
        self._dot = mlines.Line2D([], [], marker="o", ms=8, mfc="none", mew=1.8, ls="",
                                  animated=True, label="_datacursor", zorder=49)
        self.ax.add_line(self._dot)
        self._note = self.ax.annotate(
            "", xy=(0, 0), xytext=(14, 14), textcoords="offset points",
            fontsize=8.5, animated=True, zorder=50, label="_datacursor",
            bbox=dict(boxstyle="round,pad=0.45", lw=1.1, alpha=0.94))
        self._dot.set_visible(False)
        self._note.set_visible(False)

    # ---- events -----------------------------------------------------------------------------
    def _on_draw(self, ev):
        """A real draw happened: cache the clean background, and re-paint the cursor on top if
        it was showing — otherwise a live run's next throttled redraw would wipe it."""
        self._bg = self.canvas.copy_from_bbox(self.ax.bbox)
        if self._visible and self._alive():
            self.ax.draw_artist(self._dot)
            self.ax.draw_artist(self._note)
            self.canvas.blit(self.ax.bbox)
        elif self._visible:
            self._visible = False            # ax.clear() took the artists mid-hover

    def _on_move(self, ev):
        if ev.inaxes is not self.ax or self._mode() or ev.x is None:
            self._hide()
            return
        best = None                          # (d², line, x, y)
        for ln in self.ax.get_lines():
            if str(ln.get_label()).startswith("_") or not ln.get_visible():
                continue
            xd = np.asarray(ln.get_xdata(), float)
            yd = np.asarray(ln.get_ydata(), float)
            if xd.size == 0:
                continue
            pts = ln.get_transform().transform(np.column_stack([xd, yd]))
            d2 = (pts[:, 0] - ev.x) ** 2 + (pts[:, 1] - ev.y) ** 2
            d2 = np.where(np.isfinite(d2), d2, np.inf)
            i = int(np.argmin(d2))
            if np.isinf(d2[i]):
                continue
            if best is None or d2[i] < best[0]:
                best = (d2[i], ln, float(xd[i]), float(yd[i]))
        if best is None or best[0] > self.SNAP_PX ** 2:
            self._hide()
            return
        _, ln, px, py = best
        self._ensure_artists()
        fg, bg = self._colours()
        c = ln.get_color()
        self._dot.set_data([px], [py])
        self._dot.set_markeredgecolor(c)
        self._note.xy = (px, py)
        self._note.set_text("\n".join((str(ln.get_label()),
                                       "t = %.3f s" % px,
                                       "ε = %.3f %%" % py)))
        self._note.set_color(fg)
        patch = self._note.get_bbox_patch()
        patch.set_facecolor(bg)
        patch.set_edgecolor(c)
        # Keep the box inside the axes: flip it to the other side of the point near an edge.
        xa, ya = self.ax.transAxes.inverted().transform((ev.x, ev.y))
        self._note.xyann = (14 if xa < 0.62 else -14, 14 if ya < 0.72 else -18)
        self._note.set_ha("left" if xa < 0.62 else "right")
        self._note.set_va("bottom" if ya < 0.72 else "top")
        self._dot.set_visible(True)
        self._note.set_visible(True)
        self._visible = True
        self._blit()

    def _hide(self):
        if not self._visible:
            return
        self._visible = False
        if self._alive():
            self._dot.set_visible(False)
            self._note.set_visible(False)
        if self._bg is not None:
            self.canvas.restore_region(self._bg)
            self.canvas.blit(self.ax.bbox)
        else:
            self.canvas.draw_idle()

    def _blit(self):
        if self._bg is None:                 # nothing cached yet — the first full draw will
            self.canvas.draw_idle()          # land in _on_draw and paint the cursor itself
            return
        self.canvas.restore_region(self._bg)
        self.ax.draw_artist(self._dot)
        self.ax.draw_artist(self._note)
        self.canvas.blit(self.ax.bbox)


class Worker(QThread):
    """Runs the analysis off the GUI thread and streams results back a frame at a time."""
    row = pyqtSignal(object)
    done = pyqtSignal(object)
    failed = pyqtSignal(str)
    progress = pyqtSignal(int, int)
    frame = pyqtSignal(object, object, object, float)   # gray, box A now, box B now, half-size

    # The analysis runs several times faster than the recording (S26: ~126 fps against a 19.9 fps
    # capture), so every frame must NOT be shipped to the GUI thread. Two brakes: a time throttle
    # for a steady display rate, and a pending flag so a slow repaint applies back-pressure
    # instead of letting a queue of 1 MB frames build up behind it.
    PREVIEW_HZ = 25.0
    # Downscale BEFORE crossing the thread. The preview pane is a few hundred pixels tall, so
    # shipping a full 2348 px frame 25 times a second copies ~1 MB and then throws most of it
    # away in the scaler — measured at a 4x slowdown of the analysis itself. Shrinking here costs
    # one resize and keeps the displayed detail the pane can actually show. Box coordinates are
    # scaled with it, so the view still draws them in frame coordinates.
    PREVIEW_MAX_PX = 720

    def __init__(self, path, a, b, cfg, preview=True, extras=None):
        super().__init__()
        self.path, self.a, self.b, self.cfg = path, a, b, cfg
        self.extras = extras or []
        self._stop = False
        self._preview = preview
        self._last_emit = 0.0
        self._pending = False

    def stop(self):
        self._stop = True

    def frame_shown(self):
        """Called from the GUI thread once a preview frame has actually been painted."""
        self._pending = False

    def _on_frame(self, gray, a_xy, b_xy):
        if not self._preview or self._pending:
            return
        now = time.monotonic()
        if now - self._last_emit < 1.0 / self.PREVIEW_HZ:
            return
        self._last_emit = now
        self._pending = True
        import cv2
        h, w = gray.shape
        k = min(1.0, self.PREVIEW_MAX_PX / float(max(h, w)))
        if k < 1.0:
            small = cv2.resize(gray, (max(1, int(w * k)), max(1, int(h * k))),
                               interpolation=cv2.INTER_AREA)
            a_xy = (a_xy[0] * k, a_xy[1] * k)
            b_xy = (b_xy[0] * k, b_xy[1] * k)
        else:
            small, k = gray, 1.0
        # cv2.resize returns a fresh array; the full-size path still needs a copy because the
        # decoder reuses its buffer and this crosses a thread.
        # The drawn box must shrink with the frame, or it would be drawn at full-frame size
        # over a downscaled image and stop matching the patch that is actually being correlated.
        self.frame.emit(np.ascontiguousarray(small) if k < 1.0
                        else np.ascontiguousarray(gray).copy(),
                        a_xy, b_xy, self.cfg.box_half * k)

    def run(self):
        try:
            gen = PP.analyse(self.path, self.a, self.b, self.cfg,
                             progress=lambda d, t: self.progress.emit(d, t),
                             should_stop=lambda: self._stop,
                             preview=self._on_frame, extras=self.extras)
            while True:
                try:
                    self.row.emit(next(gen))
                except StopIteration as stop:
                    self.done.emit(stop.value)
                    return
        except Exception as e:                       # a bad file must not take the app down
            self.failed.emit(str(e))


@dataclass
class Run:
    """One video and everything that decides how it is measured, plus its result.

    Each video needs its OWN extensometer: two videos never have their markers in the same place,
    and an extensometer recording has neither the same frame rate nor the same scale as ours. So
    the boxes and every setting belong to the run, not to the tab — selecting a run in the list
    swaps the whole setup, and running it cannot pick up a stray value left over from another.
    """
    path: str
    info: dict
    label: str
    colour: str
    boxes: list = None
    box_half: int = 24
    search: int = 40
    min_corr: float = 0.55
    ref_frame: int = 0
    ref_image: str = ""              # a still used as the zero instead of the video's own frame
    fps: float = 30.0
    step: int = 1
    refine: str = "auto"
    stop_on_loss: bool = True
    fps_note: str = ""
    # The gauge belongs to the RUN, not to the tab. It used to be a single spin box shared by
    # every video, so loading a 45 mm specimen after an 80 mm one silently kept the 80 — which is
    # exactly what happened to MOT session 2.
    gauge_mm: float = 80.0
    gauge_confirmed: bool = False    # has anyone said this is right for THIS video?
    gauge_src: str = ""              # where it came from, for the results sheet
    # Which of gauge / px-per-mm the operator actually KNOWS — the other one follows the boxes.
    # "gauge" (default): the marker spacing is the given, px/mm floats as boxes move — right for
    # a foreign video. "pxmm": the optics are calibrated (our own rig), so the SCALE is the given
    # and the gauge box becomes a live MEASUREMENT, re-derived at every placement and drag.
    # Set implicitly by whichever field was typed last; no extra widget to explain.
    scale_anchor: str = "gauge"
    # The calibrated scale itself, when the anchor is "pxmm" — owned by the RUN for the same
    # reason the gauge is: the spin box is shared UI, and switching to another video must not
    # let the previous video's calibration leak into this one's millimetres.
    px_mm: float = 0.0
    fps_verified: bool = False       # measured from a sidecar or a companion, not merely declared
    fps_override: bool = False       # the operator was warned and chose to proceed anyway
    companion: object = None         # PP.Companion, when a data file has been attached
    # EXTRA tracked pairs: [ (ax, ay, bx, by, kind, label), ... ] — a second axial pair, or a
    # transverse ("width") pair that feeds the Poisson / true-stress maths. Owned by the run for
    # the same reason the boxes are: no two videos have their markers in the same place.
    extra_pairs: list = None
    area_mm2: float = 80.0           # nominal cross-section — only true stress consumes it
    xe: list = None                  # per-extra strain series, mirrored against t for plotting
    poisson_rows: object = None      # per-row nu/area/true-stress dicts, once computed
    poisson_note: str = ""
    t: list = None
    e: list = None
    tr: list = None
    summary: object = None

    def __post_init__(self):
        if self.boxes is None:
            self.boxes = [None, None]
        if self.extra_pairs is None:
            self.extra_pairs = []
        for k in ("t", "e", "tr", "xe"):
            if getattr(self, k) is None:
                setattr(self, k, [])

    @property
    def ready(self):
        return bool(self.boxes[0] and self.boxes[1])

    @property
    def done(self):
        return self.summary is not None and bool(self.t)

    @property
    def peak(self):
        """Highest strain reached, ignoring the NaN holes that mark dropouts."""
        vals = [v for v in self.e if v == v]
        return max(vals) if vals else 0.0

    def status(self):
        # A lost marker is NOT announced here. It is reported in the three places that survive
        # being saved — the dialog when the run ends, the results table, and the report — and a
        # fourth copy in the list is just the same warning shouted again. What the row does owe
        # the reader is that the trace is SHORT, so the alarm becomes a plain fact about where
        # the data stops; without it a stopped run reads exactly like a complete one.
        if self.done:
            if getattr(self.summary, "stopped_early", False):
                _end = getattr(self.summary, "data_ends_t", None)
                if _end is None:
                    _end = self.summary.lost_at_t
                tail = "  ·  ends at %.2f s" % _end
            elif self.summary.coverage < 99.95:
                tail = "  ·  %d frame(s) not tracked" % (self.summary.n - self.summary.tracked)
            else:
                tail = ""
            return "%.3f %% peak, %.0f %% tracked%s" % (self.peak * 100,
                                                        self.summary.coverage, tail)
        return "ready to run" if self.ready else "needs two boxes"


class GuideDialog(QDialog):
    """The procedure, one step at a time, beside a list showing where that step sits.

    Modeless: it is meant to be read WHILE working in the tab behind it, so it never takes the
    input focus away and never blocks. `follow` keeps it pointed at whatever the tab has not done
    yet, and switches itself off the moment the reader navigates by hand — an auto-advance that
    fights the reader is worse than none.
    """

    def __init__(self, steps, state_fn, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DIC Post-Processing — Guide")
        self.setModal(False)
        self.resize(880, 520)
        self.steps = steps
        self.state_fn = state_fn
        self._follow = True
        self._navigating = False          # True while WE move the selection, so it is not read
                                          # as the reader taking over

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        head = QLabel("Measuring strain from a recorded video, in %d steps" % len(steps))
        head.setStyleSheet("font-size:15px; font-weight:bold; color:#e6edf3;")
        lay.addWidget(head)

        body = QHBoxLayout(); body.setSpacing(12)

        self.list = QListWidget()
        self.list.setFixedWidth(268)
        self.list.setSpacing(1)
        self.list.setStyleSheet(
            "QListWidget { background:#0e1116; border:1px solid #2b3138; border-radius:4px;"
            "              padding:5px; font-size:12px; }"
            # No colour here on purpose: a stylesheet colour wins over setForeground(), which is
            # what marks done / current / pending. Padding and shape only.
            "QListWidget::item { padding:7px 8px; border-radius:3px; }"
            "QListWidget::item:selected { background:#1f6fb4; color:#ffffff; }")
        self.list.currentRowChanged.connect(self._on_pick)
        body.addWidget(self.list)

        pane = QScrollArea()
        pane.setWidgetResizable(True)
        pane.setFrameShape(QFrame.Shape.NoFrame)
        inner = QWidget()
        iv = QVBoxLayout(inner); iv.setContentsMargins(16, 14, 16, 14); iv.setSpacing(10)
        self.stepNo = QLabel()
        self.stepNo.setStyleSheet("color:#6b7280; font-size:11px; font-weight:bold;"
                                  "letter-spacing:1px;")
        self.stepTitle = QLabel(); self.stepTitle.setWordWrap(True)
        self.stepTitle.setStyleSheet("font-size:19px; font-weight:bold; color:#e6edf3;")
        rule = QFrame(); rule.setFrameShape(QFrame.Shape.HLine)
        rule.setStyleSheet("color:#2b3138;")
        self.stepBody = QLabel(); self.stepBody.setWordWrap(True)
        self.stepBody.setTextFormat(Qt.TextFormat.RichText)
        self.stepBody.setStyleSheet("font-size:13px; color:#c9d1d9; line-height:150%;")
        self.stepBody.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.stepTips = QLabel(); self.stepTips.setWordWrap(True)
        self.stepTips.setTextFormat(Qt.TextFormat.RichText)
        self.stepTips.setStyleSheet(
            "background:#12171d; border-left:3px solid #e8a80c; border-radius:3px;"
            "padding:9px 12px; font-size:12px; color:#b9c2cc;")
        iv.addWidget(self.stepNo); iv.addWidget(self.stepTitle); iv.addWidget(rule)
        iv.addWidget(self.stepBody); iv.addWidget(self.stepTips)
        iv.addStretch(1)
        pane.setWidget(inner)
        pane.setStyleSheet("QScrollArea { background:#0e1116; border:1px solid #2b3138;"
                           "              border-radius:4px; }")
        body.addWidget(pane, 1)
        lay.addLayout(body, 1)

        foot = QHBoxLayout()
        self.followChk = QCheckBox("Follow my progress")
        self.followChk.setChecked(True)
        self.followChk.setToolTip("Jump to whichever step is next as you work. Turning the pages "
                                  "by hand switches this off so the window stops moving under you.")
        self.followChk.toggled.connect(self._on_follow)
        self.progressLbl = QLabel(); self.progressLbl.setStyleSheet("color:#8b949e;")
        self.backBtn = QPushButton("‹ Back"); self.backBtn.clicked.connect(lambda: self._step(-1))
        self.nextBtn = QPushButton("Next ›"); self.nextBtn.clicked.connect(lambda: self._step(1))
        closeBtn = QPushButton("Close"); closeBtn.clicked.connect(self.close)
        foot.addWidget(self.followChk); foot.addSpacing(10); foot.addWidget(self.progressLbl)
        foot.addStretch(1)
        foot.addWidget(self.backBtn); foot.addWidget(self.nextBtn); foot.addWidget(closeBtn)
        lay.addLayout(foot)

        for i, st in enumerate(self.steps):
            self.list.addItem(QListWidgetItem("%d.  %s" % (i + 1, st[0])))
        self.refresh()

    # ---- state -------------------------------------------------------------------------
    def current_step(self):
        """The first step whose result does not exist yet — i.e. the one to do next."""
        done = self.state_fn()
        return next((i for i, d in enumerate(done) if not d), len(done))

    def refresh(self):
        """Re-read the tab's state: re-tick the list, and follow along if asked to."""
        done = self.state_fn()
        cur = self.current_step()
        for i in range(self.list.count()):
            it = self.list.item(i)
            mark = "✔" if done[i] else ("▶" if i == cur else "  ")
            it.setText("%s  %d.  %s" % (mark, i + 1, self.steps[i][0]))
            it.setForeground(QColor("#2f9e44") if done[i]
                             else QColor("#ffffff") if i == cur else QColor("#6b7280"))
            f = it.font(); f.setBold(i == cur); it.setFont(f)
        n = sum(1 for d in done if d)
        self.progressLbl.setText("%d of %d done" % (n, len(self.steps)))
        if self._follow:
            self._navigating = True
            self.list.setCurrentRow(min(cur, len(self.steps) - 1))
            self._navigating = False
        elif self.list.currentRow() < 0:
            self.list.setCurrentRow(0)
        self._show(self.list.currentRow())

    # ---- navigation --------------------------------------------------------------------
    def _on_pick(self, i):
        if not self._navigating and self._follow:
            # The reader took over. Stop moving the page under them.
            self.followChk.setChecked(False)
        self._show(i)

    def _on_follow(self, on):
        self._follow = on
        if on:
            self.refresh()

    def _step(self, d):
        i = max(0, min(len(self.steps) - 1, self.list.currentRow() + d))
        self.followChk.setChecked(False)
        self.list.setCurrentRow(i)

    def _show(self, i):
        if not (0 <= i < len(self.steps)):
            return
        title, body, tips = self.steps[i]
        done = self.state_fn()
        tag = "STEP %d OF %d" % (i + 1, len(self.steps))
        tag += "   ·   DONE" if done[i] else ("   ·   DO THIS NEXT" if i == self.current_step()
                                              else "")
        self.stepNo.setText(tag)
        self.stepTitle.setText(title)
        self.stepBody.setText(body)
        self.stepTips.setText("".join(
            '<p style="margin:0 0 7px 0;">•&nbsp;&nbsp;%s</p>' % t for t in tips))
        self.stepTips.setVisible(bool(tips))
        self.backBtn.setEnabled(i > 0)
        self.nextBtn.setEnabled(i < len(self.steps) - 1)


class PostProcTab(QWidget):
    log = pyqtSignal(str)
    PLOT_HZ = 8.0            # live plot refresh; the data is kept in full regardless
    # Distinguishable at a glance and colourblind-safe enough to name in conversation.
    PALETTE = ("#e8590c", "#1f6fb4", "#2f9e44", "#7048e8", "#c92a2a",
               "#0c8599", "#e8a80c", "#5f3dc4")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.runs = []
        self._cur = -1
        self._next_box = 0
        self._bigpick = None          # the large placement window, reused
        self._popout = None           # the live tracking window, reused
        self._last_extra_pts = []     # latest extra-pair positions, raw frame px
        self._run_boxhalf = None      # box_half the RUNNING cfg used, for preview scale
        self.worker = None
        self._queue = []                 # indices still to run in a Run-all sweep
        self._running = None             # index being measured right now, for the legend tag
        self._line_c = self._line_t = None
        self._last_plot = 0.0
        self._guide_dlg = None           # the guide window, built on first use and then kept
        self._losses = []                # marker losses seen during a Run-all sweep, reported at its end
        self._loading = False            # guard: writing widgets must not write back to the run
        # Set before _build(), because the status label and the plot are coloured as they are made.
        # main.apply_theme calls back with the real choice immediately after construction.
        self._theme_name = _theme.DEFAULT if _theme is not None else "dark"
        self._build()

    # ---- the current run, and the working views onto it -------------------------------
    @property
    def run(self):
        return self.runs[self._cur] if 0 <= self._cur < len(self.runs) else None

    @property
    def path(self):
        r = self.run
        return r.path if r else None

    @property
    def info(self):
        r = self.run
        return r.info if r else None

    @property
    def boxes(self):
        r = self.run
        return r.boxes if r else [None, None]

    @boxes.setter
    def boxes(self, v):
        r = self.run
        if r:
            r.boxes = v

    @property
    def summary(self):
        r = self.run
        return r.summary if r else None

    @property
    def _t(self):
        r = self.run
        return r.t if r else []

    @property
    def _e(self):
        r = self.run
        return r.e if r else []

    @property
    def _tr(self):
        r = self.run
        return r.tr if r else []

    # ------------------------------------------------------------------ UI
    def _build(self):
        split = QSplitter(Qt.Orientation.Horizontal)

        # ---- LEFT: the video and the measurement setup
        # The left column's setup stack measures ~1050 px of minimum height, and a
        # QTabWidget's minimum is the MAX over its pages — so this one column was forcing the
        # OUTER window scroll on EVERY tab (measured 2026-09-06: +314 px overflow at an
        # 860 px window, identical on all four tabs). The setup groups therefore live in their
        # own scroll now, and the run controls sit OUTSIDE it, always visible — which is also
        # exactly the complaint that surfaced it: "I have to scroll to run the analysis."
        left = QWidget()
        leftv = QVBoxLayout(left); leftv.setContentsMargins(0, 0, 0, 0); leftv.setSpacing(4)
        _setup_w = QWidget()
        lv = QVBoxLayout(_setup_w); lv.setContentsMargins(6, 6, 6, 6)

        row = QHBoxLayout()
        self.loadBtn = QPushButton("Add video(s)…")
        self.loadBtn.setToolTip("Select one or several videos. Each keeps its own extensometer, "
                                "frame rate and settings, and all completed runs are plotted "
                                "together for comparison.")
        self.loadBtn.clicked.connect(self.on_load)
        self.removeBtn = QPushButton("Remove"); self.removeBtn.clicked.connect(self.on_remove)
        self.clearAllBtn = QPushButton("Clear all"); self.clearAllBtn.clicked.connect(self.on_clear_all)
        # Beside the button that starts the procedure, because that is where somebody who does not
        # know the procedure is already looking. Also on View ▸ Guided wizard ▸ DIC post-processing.
        self.guideBtn = QPushButton("Guide")
        self.guideBtn.setToolTip("Open the step-by-step guide. It ticks each step off as you "
                                 "complete it, and stays open while you work.")
        self.guideBtn.clicked.connect(self.on_guide)
        row.addWidget(self.loadBtn, 1); row.addWidget(self.guideBtn)
        row.addWidget(self.removeBtn); row.addWidget(self.clearAllBtn)
        lv.addLayout(row)

        self.runList = QListWidget()
        self.runList.setMaximumHeight(112)
        self.runList.setToolTip("Each video and its state. Select one to set it up; double-click "
                                "to rename it — the name is what appears in the plot legend.")
        self.runList.currentRowChanged.connect(self.on_select_run)
        self.runList.itemDoubleClicked.connect(self.on_rename)
        lv.addWidget(self.runList)

        self.fileLbl = QLabel("no video loaded"); self.fileLbl.setStyleSheet("color:#8a8f98;")
        lv.addWidget(self.fileLbl)

        # ---- the separation, live, directly above the specimen it is measured from.
        # Px0 and the current L are the two numbers the whole measurement reduces to, and seeing
        # them move while the specimen stretches is what makes the tracking believable — a strain
        # trace alone gives no way to tell a real 2 % from a marker that has quietly slipped.
        self.pxLbl = QLabel()
        self.pxLbl.setTextFormat(Qt.TextFormat.RichText)
        self.pxLbl.setStyleSheet(
            "background:#0e1116; border:1px solid #2b3138; border-left:3px solid #4dabf7;"
            "border-radius:3px; padding:6px 9px;")
        self.pxLbl.setToolTip("Px₀ is the separation frozen at the reference frame. L is the "
                              "separation right now. Strain is (L − Px₀)/Px₀ — nothing else.")
        lv.addWidget(self.pxLbl)

        self.view = FrameView()
        self.view.clicked.connect(self.on_click)
        self.view.moved.connect(self.on_box_moved)
        self.view.selected.connect(lambda i: self._refresh_l0())
        lv.addWidget(self.view, 1)

        fr = QHBoxLayout()
        fr.addWidget(QLabel("Reference frame"))
        # Scrub the video without analysing it — for choosing a reference frame, checking that the
        # markers survive the whole pull before committing to a run, and seeing where a video ends.
        self.playPauseBtn = QPushButton("▶")
        self.playPauseBtn.setFixedWidth(30)
        self.playPauseBtn.setToolTip("Play / pause the video. This only scrubs frames — it does "
                                     "not measure anything.")
        self.playPauseBtn.setEnabled(False)
        self.playPauseBtn.clicked.connect(self.on_play_pause)
        self.stopPlayBtn = QPushButton("■")
        self.stopPlayBtn.setFixedWidth(30)
        self.stopPlayBtn.setToolTip("Stop and return to the reference frame.")
        self.stopPlayBtn.setEnabled(False)
        self.stopPlayBtn.clicked.connect(self.on_stop_play)
        self.frameSlider = QSlider(Qt.Orientation.Horizontal)
        self.frameSlider.setEnabled(False)
        self.frameSlider.valueChanged.connect(self.on_browse_frame)
        self.frameLbl = QLabel("0")
        fr.addWidget(self.playPauseBtn); fr.addWidget(self.stopPlayBtn)
        fr.addWidget(self.frameSlider, 1); fr.addWidget(self.frameLbl)
        lv.addLayout(fr)

        # ---- committing the reference is a deliberate act, not a side effect of scrubbing.
        rf = QHBoxLayout()
        self.setRefBtn = QPushButton("Set this frame as the reference")
        self.setRefBtn.setEnabled(False)
        self.setRefBtn.setToolTip(
            "Fix the frame you are looking at as the reference — the frame that defines Px₀ and "
            "therefore zero strain.\n\nThe slider only browses. Nothing you do with it changes "
            "the reference until you press this.")
        self.setRefBtn.clicked.connect(self.on_set_ref)
        # The zero does not have to come from the video. A recording may start after the pull
        # began, or the best picture of the unloaded specimen may have been taken separately.
        self.refImgBtn = QPushButton("Use an image…")
        self.refImgBtn.setEnabled(False)
        self.refImgBtn.setMaximumWidth(120)
        self.refImgBtn.setToolTip(
            "Use a still image as the reference instead of a frame of this video — for when the "
            "recording holds no clean frame of the specimen at rest.\n\nIt must have the SAME "
            "dimensions as the video, because Px₀ and every later separation are measured in "
            "frame pixels. Press again to go back to using the video.")
        self.refImgBtn.clicked.connect(self.on_ref_image)
        self.refLbl = QLabel()
        self.refLbl.setToolTip("Which frame, or which image, is currently the reference.")
        rf.addWidget(self.setRefBtn); rf.addWidget(self.refImgBtn); rf.addWidget(self.refLbl, 1)
        lv.addLayout(rf)

        g = QGroupBox("Virtual extensometer"); gl = QGridLayout(g)
        self.autoBtn = QPushButton("Auto-detect markers")
        self.autoBtn.setToolTip("Find two sprayed dots the way the rig does. For a speckle pattern, "
                                "click the frame twice instead.")
        self.autoBtn.clicked.connect(self.on_auto)
        self.clearBtn = QPushButton("Clear boxes"); self.clearBtn.clicked.connect(self.on_clear)
        # Manual placement of the MAIN pair, in the desk-sized window — right beside
        # Auto-detect, where the choice between the two is actually made (his ask,
        # 2026-09-06: the markers are hard to see, let alone click, in the small pane).
        self.manualBtn = QPushButton("Select manually…")
        self.manualBtn.setToolTip("Open the frame in a large window and click the two markers "
                                  "yourself — box A then box B, snapping to a marker centre "
                                  "when one is near. For when Auto-detect picks wrong or the "
                                  "markers are hard to see at this size.")
        self.manualBtn.clicked.connect(self.on_manual_main)
        # One row of three, sharing the group's existing width (an HBox inside the grid row,
        # so no third grid column widens the page).
        _pick_row = QHBoxLayout()
        _pick_row.addWidget(self.autoBtn); _pick_row.addWidget(self.manualBtn)
        _pick_row.addWidget(self.clearBtn)
        gl.addLayout(_pick_row, 0, 0, 1, 2)

        self.gauge = QDoubleSpinBox(); self.gauge.setRange(0.1, 1000); self.gauge.setValue(80.0)
        self.gauge.setSuffix(" mm"); self.gauge.setDecimals(4)
        self.gauge.setToolTip("Physical distance BETWEEN THE BOXES. Sets px/mm only — strain is a "
                              "pixel ratio and does not depend on it.\n\n"
                              "Enter whichever of this and px/mm you actually know: once the boxes "
                              "are placed they are the same number, and each one sets the other.")
        self.gauge.valueChanged.connect(self._on_gauge_edited)
        # px/mm as a FIRST-CLASS input rather than a derived read-out.
        #
        # Px0 ties the two together — px/mm = Px0 / gauge — so knowing either one fixes the other.
        # Which one a person actually knows depends on where the video came from: for our own rig
        # the optics are calibrated and px/mm is the known quantity, while the marker spacing is
        # whatever it was set to that day. Forcing the gauge to be the only input made the operator
        # convert in their head, and the default 80.00 was the number that survived when they
        # didn't.
        self.pxmm = QDoubleSpinBox(); self.pxmm.setRange(0.01, 10000); self.pxmm.setDecimals(4)
        self.pxmm.setSuffix(" px/mm")
        self.pxmm.setToolTip("The other way round. Type the calibrated scale and the gauge follows "
                             "from Px₀, or type the gauge and this follows.")
        self.pxmm.valueChanged.connect(self._on_pxmm_edited)
        self.boxHalf = QSpinBox(); self.boxHalf.setRange(6, 200); self.boxHalf.setValue(24)
        self.boxHalf.setSuffix(" px"); self.boxHalf.valueChanged.connect(self._refresh_boxes)
        self.boxHalf.setToolTip("Half-size of each tracked patch. Bigger is steadier but blurs "
                                "local deformation; it must comfortably contain the speckle or dot.")
        self.search = QSpinBox(); self.search.setRange(4, 500); self.search.setValue(40)
        self.search.setSuffix(" px")
        self.search.setToolTip("How far a box may travel from the reference frame. Must exceed the "
                               "largest expected movement, or the match will hit the window edge.")
        self.method = QComboBox()
        self.method.addItem("Marker centroid, intensity-weighted (best precision)", "auto")
        self.method.addItem("Marker centroid, binary — MATCHES THE RIG", "rig")
        self.method.addItem("Pattern correlation only (speckle)", "correlation")
        self.method.setToolTip(
            "How each frame's marker position is found.\n\n"
            "Intensity-weighted is the most precise and the least sensitive to threshold.\n\n"
            "MATCHES THE RIG reproduces camera_manager's own binary centroid. Use it when "
            "comparing this video against a live run or against the extensometer — it is noisier, "
            "and that is the point: it removes the estimator as a variable so the difference you "
            "measure is physics rather than method.\n\n"
            "Correlation only is for a speckle pattern, which has no discrete marker to take a "
            "centroid of. It is selected automatically when no marker is found.")
        self.minCorr = QDoubleSpinBox(); self.minCorr.setRange(0.05, 0.99)
        self.minCorr.setSingleStep(0.05); self.minCorr.setValue(0.55)
        self.minCorr.setToolTip("Below this peak correlation the frame is not trusted: the tracker "
                                "re-seeds and flags it rather than reporting a confident wrong value.")
        for r, (lab, wdg) in enumerate((("Gauge (A→B)", self.gauge), ("…or px per mm", self.pxmm),
                                        ("Box half-size", self.boxHalf),
                                        ("Search window", self.search),
                                        ("Min correlation", self.minCorr),
                                        ("Tracking method", self.method)), start=1):
            gl.addWidget(QLabel(lab), r, 0); gl.addWidget(wdg, r, 1)
        self.l0Lbl = QLabel("place two boxes to set Px₀")
        self.l0Lbl.setStyleSheet("color:#4dabf7; font-weight:bold;")
        gl.addWidget(self.l0Lbl, 7, 0, 1, 2)

        # ---- extra pairs: a second axial extensometer, or a WIDTH pair for Poisson/true stress.
        # They ride the same analysis pass; the width pair is what unlocks the one quantity the
        # rig's CSVs have always disclaimed — true (Cauchy) stress needs the current cross-section.
        self.addAxialBtn = QPushButton("+ Axial pair")
        self.addAxialBtn.setToolTip("Track a SECOND axial pair in the same run — e.g. a shorter "
                                    "gauge inside the main one, to compare strain along the "
                                    "specimen. Next two clicks on the frame place it.")
        self.addAxialBtn.clicked.connect(lambda: self._arm_pair("axial"))
        self.addTransBtn = QPushButton("+ Width pair")
        self.addTransBtn.setToolTip("Track a TRANSVERSE pair across the specimen's width. Its "
                                    "contraction gives lateral strain → Poisson's ratio → area "
                                    "change → TRUE stress (with a load channel attached).\n\n"
                                    "Honesty note: on the mini-dogbone at ~21 px/mm the width "
                                    "change is sub-pixel and the result is noise — the run says "
                                    "so when that happens. Next two clicks place the pair.")
        self.addTransBtn.clicked.connect(lambda: self._arm_pair("transverse"))
        self.clearPairsBtn = QPushButton("Clear pairs")
        self.clearPairsBtn.clicked.connect(self.on_clear_pairs)
        self.bigViewBtn = QPushButton("Large view…")
        self.bigViewBtn.setToolTip("Open the frame in a desk-sized window to place the boxes and "
                                   "pairs — same clicks, same snapping, just visible.")
        self.bigViewBtn.clicked.connect(self.on_big_view)
        # 2x2, not one row of four: four buttons abreast made this the WIDEST page in the app,
        # and a QTabWidget's minimum width is the max over its pages — the whole window paid.
        prow = QGridLayout()
        prow.addWidget(self.addAxialBtn, 0, 0); prow.addWidget(self.addTransBtn, 0, 1)
        prow.addWidget(self.clearPairsBtn, 1, 0); prow.addWidget(self.bigViewBtn, 1, 1)
        gl.addLayout(prow, 9, 0, 1, 2)
        self.extraLbl = QLabel("")
        self.extraLbl.setWordWrap(True)
        self.extraLbl.setStyleSheet("color:#b197fc;")
        gl.addWidget(self.extraLbl, 10, 0, 1, 2)
        self.area = QDoubleSpinBox(); self.area.setRange(0.01, 100000); self.area.setDecimals(2)
        self.area.setValue(80.0); self.area.setSuffix(" mm²")
        self.area.setToolTip("Nominal cross-section A₀. Consumed ONLY by the true-stress maths "
                             "of a width pair — strain and engineering quantities never touch it.")
        gl.addWidget(QLabel("Area A₀"), 11, 0); gl.addWidget(self.area, 11, 1)
        # An unconfirmed gauge is stated, not hidden. It corrupts no strain — but it does reach
        # px/mm, the extension in mm and the results sheet, where a default is indistinguishable
        # from a measurement.
        self.gaugeWarn = QLabel(""); self.gaugeWarn.setWordWrap(True)
        self.gaugeWarn.setStyleSheet("color:#f39c12;")
        gl.addWidget(self.gaugeWarn, 8, 0, 1, 2)
        lv.addWidget(g)

        g2 = QGroupBox("Timebase"); g2l = QGridLayout(g2)
        self.fps = QDoubleSpinBox(); self.fps.setRange(0.01, 10000); self.fps.setDecimals(4)
        self.fps.setValue(30.0); self.fps.setSuffix(" fps")
        self.fps.setToolTip("The file's own value is only a default. Containers frequently declare "
                            "a frame rate the recording never had.")
        self.step = QSpinBox(); self.step.setRange(1, 100); self.step.setValue(1)
        self.step.setPrefix("every "); self.step.setSuffix(" frame(s)")
        g2l.addWidget(QLabel("Frame rate"), 0, 0); g2l.addWidget(self.fps, 0, 1)
        g2l.addWidget(QLabel("Analyse"), 1, 0); g2l.addWidget(self.step, 1, 1)
        # ONE attachment answers three questions that are otherwise three separate guesses: the
        # true frame rate (frames ÷ the acquisition's own duration), the gauge (if the file names
        # one), and where the specimen was actually preloaded (if it carries a load channel).
        self.compBtn = QPushButton("Attach data file…")
        self.compBtn.setToolTip(
            "The CSV or .daq recorded alongside this video.\n\n"
            "Its duration fixes the frame rate — a container's own figure is what the writer "
            "claimed, not what the camera did.\n"
            "A gauge column sets the gauge.\n"
            "A load column anchors the noise window at the preload instead of at the first frame.")
        self.compBtn.clicked.connect(self.on_attach_companion)
        self.compLbl = QLabel("no data file attached"); self.compLbl.setWordWrap(True)
        self.compLbl.setStyleSheet("color:#888;")
        g2l.addWidget(self.compBtn, 2, 0, 1, 2)
        g2l.addWidget(self.compLbl, 3, 0, 1, 2)
        self.fpsWarn = QLabel(""); self.fpsWarn.setWordWrap(True)
        self.fpsWarn.setStyleSheet("color:#f39c12;")
        g2l.addWidget(self.fpsWarn, 4, 0, 1, 2)
        lv.addWidget(g2)

        for _w in (self.boxHalf, self.search, self.minCorr, self.step, self.fps):
            _w.valueChanged.connect(lambda *_: self._store_widgets())
        self.method.currentIndexChanged.connect(lambda *_: self._store_widgets())

        self.playChk = QCheckBox("Play the video while analysing")
        self.playChk.setChecked(True)
        self.playChk.setToolTip("Show each frame with the tracking boxes following the markers, so "
                                "the pull can be watched as it is measured. Turn it off for a "
                                "slightly faster run on a long video.")
        self.stopLossChk = QCheckBox("Stop when the markers are lost")
        self.stopLossChk.setChecked(True)
        self.stopLossChk.setToolTip(
            "ON (default): the run ends the moment tracking is lost, and the plot holds only what "
            "actually tracked. On a fracture test that point is normally the fracture itself.\n\n"
            "OFF: the run carries on to the end of the video and keeps trying to re-acquire. Use "
            "it when a marker drops out briefly and comes back, or to see what the tracker did "
            "after losing its grip. Frames with no match leave a visible BREAK in the curve — "
            "they are not bridged, because a line drawn across a dropout looks like measurement.")
        self.stopLossChk.toggled.connect(self._store_widgets)
        cks = QHBoxLayout()
        cks.addWidget(self.playChk); cks.addWidget(self.stopLossChk); cks.addStretch(1)
        lv.addLayout(cks)

        lv.addStretch(1)
        _setup_scroll = QScrollArea()
        _setup_scroll.setWidgetResizable(True)
        _setup_scroll.setFrameShape(QFrame.Shape.NoFrame)
        _setup_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        _setup_scroll.setWidget(_setup_w)
        # 220 keeps the video pane usable at the floor; everything below it scrolls within the
        # column instead of pushing the whole window into a scrollbar.
        _setup_scroll.setMinimumHeight(220)
        leftv.addWidget(_setup_scroll, 1)

        rr = QHBoxLayout()
        self.runBtn = QPushButton("Run this video"); self.runBtn.setEnabled(False)
        self.runBtn.clicked.connect(self.on_run)
        self.runAllBtn = QPushButton("Run all pending"); self.runAllBtn.setEnabled(False)
        self.runAllBtn.setToolTip("Run every video that has its boxes placed and has not been run "
                                  "yet, one after another, plotting each as it finishes.")
        self.runAllBtn.clicked.connect(self.on_run_all)
        self.stopBtn = QPushButton("Stop"); self.stopBtn.setEnabled(False)
        self.stopBtn.clicked.connect(self.on_stop)
        self.expBtn = QPushButton("Export CSV"); self.expBtn.setEnabled(False)
        self.expBtn.clicked.connect(self.on_export)
        self.reportBtn = QPushButton("Generate report"); self.reportBtn.setEnabled(False)
        self.reportBtn.setToolTip("One page carrying the plot, the results table and the settings "
                                  "behind them, as PDF and PNG — plus the table and every run's "
                                  "per-frame data as CSV, in a folder you choose.")
        self.reportBtn.clicked.connect(self.on_report)
        rr.addWidget(self.runBtn); rr.addWidget(self.runAllBtn)
        rr.addWidget(self.stopBtn); rr.addWidget(self.expBtn); rr.addWidget(self.reportBtn)
        leftv.addLayout(rr)
        self.bar = QProgressBar(); self.bar.setValue(0)
        leftv.addWidget(self.bar)
        self.status = QLabel("—"); self.status.setWordWrap(True)
        self.status.setStyleSheet("color:%s;" % self._status_fg())
        leftv.addWidget(self.status)

        # ---- RIGHT: the answer — plot above, the numbers behind it below.
        # A vertical splitter rather than a fixed split: on a short screen the table can be
        # collapsed away entirely, and when comparing six runs it can be pulled up instead.
        right = QSplitter(Qt.Orientation.Vertical)

        plotBox = QWidget(); rv = QVBoxLayout(plotBox); rv.setContentsMargins(6, 6, 6, 6)
        self.fig = Figure(figsize=(6, 5))
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        self._reset_plot()
        # The same toolbar the Load and Stress/Strain plots carry — pan, zoom to rectangle, back
        # and forward through views, Home, and matplotlib's own save. Above the canvas, as on the
        # other two, so the three plots are operated the same way.
        self.plotToolbar = NavigationToolbar(self.canvas, plotBox)
        self.plotToolbar.setFixedHeight(24)
        self.plotToolbar.setIconSize(QSize(16, 16))
        self.plotToolbar.setStyleSheet(
            "background-color: %s;"
            % (_theme.get(self._theme_name)["plot_bg"] if _theme is not None else "#f0f0f0"))
        self.plotToolbar.setToolTip("Pan, zoom to a rectangle, step back through views, or Home "
                                    "to return to the full curve.")
        rv.addWidget(self.plotToolbar)
        rv.addWidget(self.canvas, 1)
        # Hover any curve to read the exact recorded point — series, t, ε — without zooming.
        # Suppressed while the toolbar is panning/zooming, invisible to Save plot… and reports.
        self.plotCursor = DataCursor(self.canvas, self.ax,
                                     mode=lambda: str(getattr(self.plotToolbar, "mode", "") or ""),
                                     colours=self._cursor_colours)
        prow = QHBoxLayout()
        self.showTrue = QCheckBox("also plot true (log) strain")
        self.showTrue.stateChanged.connect(lambda *_: self._redraw_plot())
        self.savePlotBtn = QPushButton("Save plot…")
        self.savePlotBtn.setToolTip("Write the plot exactly as shown to PNG, PDF or SVG. "
                                    "PDF and SVG stay sharp at any size — use them for a report.")
        self.savePlotBtn.clicked.connect(self.on_save_plot)
        prow.addWidget(self.showTrue, 1); prow.addWidget(self.savePlotBtn)
        rv.addLayout(prow)
        right.addWidget(plotBox)

        tableBox = QWidget(); tv = QVBoxLayout(tableBox); tv.setContentsMargins(6, 0, 6, 6)
        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("Results — one column per run"))
        hdr.addStretch(1)
        self.copyBtn = QPushButton("Copy table")
        self.copyBtn.setToolTip("Copy as tab-separated text — pastes straight into Excel.")
        self.copyBtn.clicked.connect(self.on_copy_table)
        self.saveTableBtn = QPushButton("Save table…")
        self.saveTableBtn.clicked.connect(self.on_save_table)
        hdr.addWidget(self.copyBtn); hdr.addWidget(self.saveTableBtn)
        tv.addLayout(hdr)
        self.table = QTableWidget(0, 0)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.table.verticalHeader().setVisible(False)
        tv.addWidget(self.table, 1)
        right.addWidget(tableBox)
        right.setStretchFactor(0, 3); right.setStretchFactor(1, 2)

        self._left_pane = left            # the popout parks exactly over this
        split.addWidget(left); split.addWidget(right)
        split.setStretchFactor(0, 3); split.setStretchFactor(1, 4)
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(split)
        self._refresh_table()
        # The readout and the guide are both built empty and filled here; without this they are
        # blank boxes until the first video is loaded.
        self._update_px_label()
        self._refresh_guide()

    # Each step: (title, what to do, [things worth knowing]). Which are DONE comes from
    # _guide_state, which reads real state — a step is ticked because its result exists, not
    # because the operator was told to do it. That is what makes this a wizard rather than a
    # poster, and it is why the window can say "do this next" and be right.
    GUIDE_STEPS = (
        ("Add the video or videos",
         "Press <b>Add video(s)…</b> at the top left and pick one file, or several at once. "
         "Any format OpenCV can read works — .avi, .mp4, .mkv, .mov and more.",
         ["Every video keeps its OWN boxes, frame rate and settings, so a rig recording and an "
          "extensometer recording can sit in the same list without one spoiling the other.",
          "Double-click a name in the list to rename it. That name is what labels the curve in "
          "the plot and the column in the results table.",
          "Select a video in the list to set it up; everything below the list then belongs to "
          "that video."]),
        ("Check the frame rate",
         "Look at <b>Timebase ▸ Frame rate</b> and make sure it is the rate the camera actually "
         "ran at. This is the one setting that silently distorts a result, because it scales the "
         "whole time axis.",
         ["A container's fps field is what the writer claimed, not what the camera did. One of "
          "our own recordings declares 35 fps and actually ran at 19.93 — believing it would "
          "stretch time by 1.76×.",
          "For our own captures the true rate is read automatically from the recording's "
          "frames/index.csv timestamps, and the note under the box says so.",
          "For a video from anywhere else, press <b>Attach data file…</b> and pick the CSV or "
          ".daq recorded with it. The rate is then frames ÷ that file's own duration, which is "
          "exact — and the same file supplies the gauge and the preload if it carries them.",
          "An unverified rate that also looks wrong — a round number over 100 fps is the usual "
          "sign of a container default — now STOPS the run rather than colouring a label. The "
          "XT-205's export declares 1000 fps and actually ran at 19.864.",
          "<b>Analyse every N frames</b> below it trades detail for speed and does NOT affect "
          "the time axis."]),
        ("Fix the reference frame",
         "Drag the <b>Reference frame</b> slider, or play the video with ▶ ⏸ ⏹, to the frame "
         "where strain should read zero — normally just after preload, before the pull starts — "
         "then press <b>Set this frame as the reference</b>.",
         ["If the recording holds no clean frame of the specimen at rest — it starts after the pull "
          "began, or the early frames are mid-adjustment — press <b>Use an image…</b> and pick a "
          "still instead. It must be the SAME size as the video, and the boxes are then placed on "
          "it, because that is where Px₀ is measured.",
          "The slider only BROWSES. Nothing you do with it moves the reference until you press "
          "that button, so you can scrub and play the whole video without disturbing the setup. "
          "The readout beside the button says which frame is fixed, and turns amber while you are "
          "looking at a different one.",
          "That frame sets Px₀, the marker separation everything is measured against. Strain is "
          "(L − Px₀) / Px₀ and nothing else, so this choice IS the zero.",
          "Play through the whole video once before committing: it is worth knowing that the "
          "markers survive to the end before spending a run finding out.",
          "Frame 0 is fine if the recording already starts at the preloaded state."]),
        ("Place the two boxes",
         "Press <b>Auto-detect markers</b>, or click near each marker and the box snaps to that "
         "marker's centre. Drag a box to move it, or select one and nudge it with the arrow keys.",
         ["Make the box <b>wider than the marker's radius</b>. This is the single biggest lever "
          "on precision: a patch that sits inside the dot has only flat black to lock onto and is "
          "about 13× noisier than one that reaches past the edge.",
          "The box half-size is suggested from the detected marker size — there is usually no "
          "reason to shrink it.",
          "Px₀ appears under the boxes as soon as both are placed. On a speckle pattern with no "
          "discrete dots, place the boxes by hand; snapping has nothing to snap to.",
          "<b>Search window</b> is how far a box may travel between frames. Raise it if a fast "
          "pull loses tracking; leave it alone otherwise."]),
        ("Confirm the gauge",
         "Type the real distance between the two markers into <b>Gauge (A→B)</b> — or, if what "
         "you actually know is the calibrated scale, type that into <b>…or px per mm</b> and the "
         "gauge follows.",
         ["The two are the SAME NUMBER once the boxes are placed: px/mm = Px₀ ÷ gauge. Enter "
          "whichever one you measured and let the dialog do the arithmetic.",
          "This only sets px per mm and the extension in mm. Strain itself is a ratio of PIXELS, "
          "so getting the gauge wrong changes no strain — but it does change what the results "
          "sheet says the scale was.",
          "Until you set it, the value is the leftover default and the results sheet stamps it "
          "<b>ASSUMED</b>. That is deliberate: a foreign video was once analysed at the default "
          "80 mm when the specimen was 45 mm, and nothing on the sheet said so.",
          "Use the distance you actually measured on the specimen, not the nominal gauge length "
          "of the specimen geometry. If the attached data file names a gauge column, it is taken "
          "from there and counts as confirmed."]),
        ("Run it",
         "Press <b>Run this video</b>, or <b>Run all pending</b> to work through every video that "
         "has its boxes placed, one after another, plotting each as it finishes.",
         ["Watch the Px₀ / L / ε readout directly above the video. Seeing L climb while the "
          "specimen stretches is what makes the tracking believable — a strain curve alone gives "
          "no way to tell a real 2 % from a marker that has quietly slipped.",
          "<b>Play the video while analysing</b> shows each frame with the boxes following the "
          "markers. Turn it off for a slightly faster run on a long video.",
          "If the markers are lost the run STOPS there, marks the point on the plot with an ×, "
          "and keeps only what actually tracked. On a fracture test that point is normally the "
          "fracture itself.",
          "<b>Stop when the markers are lost</b> decides what happens at that point. Leave it on "
          "and the run ends there. Turn it off and the run carries on trying to re-acquire, and "
          "any frame with no match leaves a visible BREAK in the curve rather than being bridged.",
          "<b>Stop</b> ends a run early and keeps everything measured so far."]),
        ("Take the results away",
         "The plot and the results table are both live. When you are happy with them, save what "
         "you need.",
         ["The toolbar above the plot pans and zooms it, the same one the Load and Stress/Strain "
          "plots carry. A zoom set during a run is kept as the curve grows; <b>Home</b> returns to "
          "the whole curve, and a new run starts fresh.",
          "<b>Save plot…</b> writes the plot exactly as shown — PDF or SVG stay sharp at any "
          "size, so use those for a report.",
          "<b>Copy table</b> puts it on the clipboard as tab-separated text, which pastes "
          "straight into Excel. <b>Save table…</b> writes the same thing to a file.",
          "<b>Export CSV</b> writes the per-frame data — one file per run, because the runs have "
          "different frame rates and lengths and a merged sheet would need resampling.",
          "<b>Generate report</b> is the one-press option: plot, table, settings and every run's "
          "data, into a folder you choose.",
          "Add another video and run it to compare two specimens on the same axes."]),
    )

    def _guide_state(self):
        """Which steps are done, read from real state rather than remembered."""
        r = self.run
        return [
            bool(self.runs),                            # 1 a video is loaded
            bool(r and r.fps > 0 and not self._fps_block_reason()),   # 2 a TRUSTED frame rate
            bool(r),                                    # 3 a reference frame exists (0 counts)
            bool(r and r.ready),                        # 4 both boxes placed
            bool(r and r.gauge_confirmed),              # 5 a gauge CONFIRMED for this video
            bool(r and r.done),                         # 6 this video has been measured
            bool(any(x.done for x in self.runs)),       # 7 there is something to take away
        ]

    def _refresh_guide(self):
        """Re-tick the guide window, if one is open. Cheap enough to call on any state change."""
        d = getattr(self, "_guide_dlg", None)
        if d is not None and d.isVisible():
            d.refresh()

    def on_guide(self):
        """Open the guide, or bring it forward if it is already up.

        One instance, kept rather than rebuilt, so the page the reader was on survives closing and
        reopening it — and so "Follow my progress" does not silently switch itself back on.
        """
        if getattr(self, "_guide_dlg", None) is None:
            self._guide_dlg = GuideDialog(self.GUIDE_STEPS, self._guide_state, self)
        self._guide_dlg.refresh()
        self._guide_dlg.show()
        self._guide_dlg.raise_()
        self._guide_dlg.activateWindow()

    def _want_true(self):
        """The checkbox is built after the axes, so this must survive not existing yet."""
        c = getattr(self, "showTrue", None)
        return bool(c and c.isChecked())

    def _style_plot(self):
        """Everything ax.clear() throws away: the labels, and the theme.

        Both the reset and the live redraw clear the axes, so this has to run after each of them.
        Putting it anywhere else means a theme switch lasts until the next frame arrives — which,
        during a run, is about an eighth of a second.
        """
        self.ax.set_xlabel("time (s)")
        self.ax.set_ylabel("DIC strain (%)")
        self.ax.set_title("DIC strain vs time")
        self.ax.grid(alpha=0.3)
        if _theme is not None:
            _theme.style_axes(self.fig, self.ax, self._theme_name)

    def _reset_plot(self):
        # Autoscale back on, and the toolbar's view history cleared. A new run means new data, and
        # a window framed around the previous one is unlikely to contain it — nor should Back walk
        # into views of a curve that is no longer on the axes.
        self.ax.clear()
        self.ax.set_autoscale_on(True)
        tb = getattr(self, "plotToolbar", None)
        if tb is not None:
            try:
                tb.update()                      # empties the pan/zoom history
            except Exception:
                pass
        self._style_plot()
        self._last_plot = 0.0
        self.fig.tight_layout()
        self.canvas.draw_idle()

    # ---- theme -------------------------------------------------------------------------------
    #
    # Only the PLOT and its toolbar follow the light/dark switch. The video preview and the pixel
    # readout beside it are deliberately dark in both themes: they show a camera frame, and a frame
    # of a black specimen is read against a dark surround, not a white page.

    def _status_fg(self):
        """The status line's resting colour. Its amber and green states are set per-event and are
        legible on either background, so those are left alone."""
        if _theme is None:
            return "#c9d1d9"
        return _theme.get(self._theme_name)["text"]

    def _cursor_colours(self):
        """(text, box) for the hover readout — read per event, so a theme switch mid-session
        restyles the very next hover without anyone re-wiring the cursor."""
        if _theme is None:
            return "#e6edf3", "#20262e"
        t = _theme.get(self._theme_name)
        return t["plot_fg"], t["plot_bg"]

    def apply_theme(self, name):
        """Follow the application's theme. Called by main.apply_theme, which cannot reach this
        figure itself — it walks a fixed list of the two canvases the main window owns."""
        if _theme is None:
            return
        t = _theme.get(name)
        self._theme_name = t["name"]
        self._style_plot()
        self.canvas.draw_idle()
        tb = getattr(self, "plotToolbar", None)
        if tb is not None:
            tb.setStyleSheet("background-color: %s;" % t["plot_bg"])
        st = getattr(self, "status", None)
        if st is not None:
            st.setStyleSheet("color:%s;" % self._status_fg())

    # ------------------------------------------------------------------ actions
    @staticmethod
    def _label_for(path):
        """A legend name a human would choose: the specimen if the path names one, else the file.

        Our captures live under Specimen_S26_V2_Spray_Video3/, so "S26" is right there. Anything
        else — an extensometer recording, a phone video — falls back to the file name.
        """
        import re
        m = re.search(r"Specimen_(S\d+)", path.replace("\\", "/"))
        if m:
            return m.group(1)
        return os.path.splitext(os.path.basename(path))[0][:28]

    def on_load(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Add recorded video(s)", "",
            "Video (*.avi *.mp4 *.mkv *.mov *.wmv *.m4v *.mpg *.mpeg);;All files (*)")
        added = 0
        for path in paths or []:
            try:
                info = PP.probe(path)
            except Exception as e:
                QMessageBox.warning(self, "Cannot open video", "%s\n\n%s" % (path, e))
                continue
            fps, note, verified = self._fps_for(path, info)
            r = Run(path=path, info=info, label=self._label_for(path),
                    colour=self.PALETTE[len(self.runs) % len(self.PALETTE)],
                    fps=fps, fps_note=note, fps_verified=verified,
                    box_half=self.boxHalf.value(), search=self.search.value(),
                    min_corr=self.minCorr.value(), step=self.step.value(),
                    refine=self.method.currentData())
            # The OTHER number a capture folder knows: the session's own DIC calibration. With
            # the scale known at load, the gauge box measures whichever pair gets picked and the
            # ASSUMED warning never appears for our own videos — pixels alone carry no mm, so
            # this sidecar is the one honest way to retire it without the operator typing.
            sc = PP.scale_from_sidecar(path)
            if sc:
                ppm, hdr_gauge, src = sc
                if ppm:
                    r.px_mm = float(ppm)
                    r.scale_anchor = "pxmm"
                    r.gauge_src = "measured from %s calibration" % src
                    self.log.emit("[PostProc] %s: scale %.4f px/mm from the capture's own %s — "
                                  "the gauge box will MEASURE the picked pair."
                                  % (info["name"], ppm, src))
                elif hdr_gauge:
                    r.gauge_mm, r.gauge_confirmed = float(hdr_gauge), True
                    r.gauge_src = "from %s" % src
                    self.log.emit("[PostProc] %s: gauge %.2f mm from the capture's own %s."
                                  % (info["name"], hdr_gauge, src))
            self.runs.append(r)
            added += 1
            self.log.emit("[PostProc] added %s as \"%s\" — %d frames, %.4f fps"
                          % (info["name"], r.label, info["frames"], fps))
            # Whether this file can be seeked decides whether the PREVIEW is the frame it claims
            # to be. Probing here rather than on first scrub keeps the cost in the load, and the
            # result is remembered per file.
            sw = PP.seek_warning(path)
            if sw:
                r.fps_note = (r.fps_note + "  " + sw).strip()
                self.log.emit("[PostProc] %s: %s" % (info["name"], sw))
        if not added:
            return
        self._refresh_list()
        self.runList.setCurrentRow(len(self.runs) - 1)

    @staticmethod
    def _fps_for(path, info):
        """(fps, sentence, verified). Verified means MEASURED, not merely declared.

        The container's value is only a fallback: every video this rig has produced declares 35 fps
        and none recorded at it. A capture folder beside the video records what the camera actually
        did; a video from another camera has no such record and is flagged as unverified rather
        than quietly believed.

        The third return value is what makes the flag actionable — an unverified rate that also
        looks implausible now blocks the run instead of colouring a label amber.
        """
        fps = info["fps"] if info["fps"] > 0 else 30.0
        true = PP.true_fps_from_sidecar(path)
        if true:
            fps_true, src, _n = true
            if info["fps"] > 0 and abs(fps_true - info["fps"]) / info["fps"] > 0.02:
                return round(fps_true, 4), (
                    "Using %.4f fps measured from %s. The file itself declares %.2f fps — "
                    "believing it would scale time by %.2f×."
                    % (fps_true, src, info["fps"], info["fps"] / fps_true)), True
            return (round(fps_true, 4),
                    "Frame rate %.4f fps confirmed from %s." % (fps_true, src), True)
        suspect = PP.fps_is_suspect(fps, False)
        if suspect:
            return fps, ("This video's frame rate is UNVERIFIED and %s. Attach the data file "
                         "recorded with it, or type the rate you know is right — the run is "
                         "blocked until one of those happens." % suspect), False
        return fps, (PP.fps_warning(info)
                     or "No capture sidecar beside this video — the frame rate is the file's own "
                        "claim. Check it before trusting the time axis."), False

    def _refresh_list(self):
        self._refresh_guide()
        """Rebuild the list without disturbing which row is current."""
        cur = self.runList.currentRow()
        self.runList.blockSignals(True)
        self.runList.clear()
        for r in self.runs:
            it = QListWidgetItem("%s   —   %s" % (r.label, r.status()))
            it.setForeground(QColor(r.colour))
            self.runList.addItem(it)
        if 0 <= cur < self.runList.count():
            self.runList.setCurrentRow(cur)
        self.runList.blockSignals(False)
        pending = sum(1 for r in self.runs if r.ready and not r.done)
        self.runAllBtn.setEnabled(pending > 0 and not self._busy())
        self.runAllBtn.setText("Run all pending (%d)" % pending if pending else "Run all pending")
        self.expBtn.setEnabled(any(r.done for r in self.runs))
        self.reportBtn.setEnabled(any(r.done for r in self.runs))

    def _busy(self):
        return bool(self.worker and self.worker.isRunning())

    # ------------------------------------------------------------------ scrub playback
    def _ensure_play_timer(self):
        if getattr(self, "_playTimer", None) is None:
            from PyQt6.QtCore import QTimer
            self._playTimer = QTimer(self)
            self._playTimer.timeout.connect(self._play_tick)
            self._play_at = 0
        return self._playTimer

    def on_play_pause(self):
        """Scrub the video. Deliberately NOT an analysis — nothing is measured while it plays.

        Its job is letting the operator see whether the markers survive the whole pull before
        spending a run on it, and find a sensible reference frame.
        """
        if self.run is None or self._busy():
            return
        t = self._ensure_play_timer()
        if t.isActive():
            t.stop()
            self.playPauseBtn.setText("▶")
            return
        self._play_at = self.frameSlider.value()
        self._play_from = self.frameSlider.value()
        # Real time where the frame rate is known, capped so a 200 fps file does not thrash the UI.
        fps = max(1.0, min(60.0, self.fps.value() or 25.0))
        t.start(int(1000.0 / fps))
        self.playPauseBtn.setText("❚❚")
        self.stopPlayBtn.setEnabled(True)

    def _play_tick(self):
        r = self.run
        if r is None:
            self.on_stop_play(); return
        self._play_at += max(1, self.step.value())
        if self._play_at >= r.info["frames"]:
            self.on_stop_play(); return
        g = PP.read_frame(r.path, self._play_at)
        if g is None:
            self.on_stop_play(); return
        self.view.set_frame(g)
        self.frameLbl.setText("%d  (playing)" % self._play_at)
        self._update_px_label(frame_idx=self._play_at)

    def on_stop_play(self):
        t = getattr(self, "_playTimer", None)
        if t is not None:
            t.stop()
        self.playPauseBtn.setText("▶")
        self.stopPlayBtn.setEnabled(False)
        if self.run is not None:
            # Back to the COMMITTED reference frame: that is the one the boxes belong to.
            ref = self.run.ref_frame
            self.frameSlider.blockSignals(True)
            self.frameSlider.setValue(ref)
            self.frameSlider.blockSignals(False)
            self.frameLbl.setText(str(ref))
            self._show_reference()
            self._refresh_ref_label()

    # ------------------------------------------------------------------ live pixel readout
    # Readout colours: the reference, the live value, the change, and the answer.
    C_REF, C_LIVE, C_DELTA, C_STRAIN, C_DIM = ("#4dabf7", "#ffffff", "#f0a030", "#2ecc71", "#7d8590")

    @staticmethod
    def _px_html(items, headline):
        """Small grey label, large bold monospaced value, plus one headline set larger still.

        Monospaced so the digits line up: with a proportional font a number changing from 1676 to
        1757 also changes width, and the eye reads the movement rather than the magnitude.
        """
        mono = "Consolas,'DejaVu Sans Mono',monospace"
        gap = "<span style=\"font-size:11px;\">&nbsp;&nbsp;&nbsp;</span>"
        parts = []
        for name, val, col in items:
            parts.append(
                "<span style=\"color:#7d8590;font-size:10px;\">%s</span>"
                "<span style=\"color:%s;font-family:%s;font-size:14px;font-weight:bold;\">"
                "&nbsp;%s</span>" % (name, col, mono, val))
        html = gap.join(parts)
        if headline:
            name, val, col = headline
            html += (gap + gap +
                     "<span style=\"color:#7d8590;font-size:11px;\">%s</span>"
                     "<span style=\"color:%s;font-family:%s;font-size:19px;font-weight:bold;\">"
                     "&nbsp;%s</span>" % (name, col, mono, val))
        return html

    def _update_px_label(self, l_px=None, frame_idx=None, corr=None):
        """Px₀ and the separation right now, above the specimen.

        Called from three places: when boxes move (the reference value), every analysed frame
        (the measured value), and while scrubbing (where only Px₀ is known — the label says so
        rather than showing a stale L from a previous run).
        """
        r = self.run
        if r is None or not r.ready:
            self.pxLbl.setText(self._px_html(
                [("Px₀", "—", self.C_DIM),
                 ("L", "—", self.C_DIM)],
                ("ε", "—", self.C_DIM)))
            return
        a, b = r.boxes
        l0 = float(np.hypot(b[0] - a[0], b[1] - a[1]))
        # The NUMBER carries the emphasis, not the word in front of it. Values are set large,
        # bold and monospaced (so digits line up and the eye sees a change of magnitude rather
        # than a change of width); the labels stay small and grey. Strain is the headline and is
        # sized and coloured accordingly — it is the one figure the operator is actually reading.
        # The RUN's L0, not the raw box separation, once one is known. analyse() refines the
        # reference by centroid exactly as it does every frame, so the two differ by a fraction of
        # a pixel — enough to show a non-zero ΔL on the first frame of a run, which reads as the
        # specimen already being strained. Recovered exactly from the pair: L0 = L / (1 + cauchy).
        if l_px is not None and self._e:
            c0 = self._e[-1]
            if c0 > -1.0:
                l0 = l_px / (1.0 + c0)
        elif r.summary is not None and r.summary.l0_px:
            l0 = r.summary.l0_px
        if l_px is None:
            if frame_idx is not None:
                self.pxLbl.setText(self._px_html(
                    [("Px₀", "%.2f px" % l0, self.C_REF),
                     ("frame", "%d" % frame_idx, self.C_DIM),
                     ("L", "not measured while scrubbing", self.C_DIM)], None))
            else:
                self.pxLbl.setText(self._px_html(
                    [("Px₀", "%.2f px" % l0, self.C_REF),
                     ("L", "= Px₀ at the reference frame", self.C_DIM)], None))
            return
        d = l_px - l0
        left = [("Px₀", "%.2f px" % l0, self.C_REF),
                ("L", "%.2f px" % l_px, self.C_LIVE),
                ("ΔL", "%+.2f px" % d, self.C_DELTA)]
        if corr is not None:
            left.append(("corr", "%.2f" % corr, self.C_DIM))
        self.pxLbl.setText(self._px_html(
            left, ("ε", "%+.4f %%" % (100.0 * d / l0 if l0 else 0.0),
                   self.C_STRAIN)))

    # ------------------------------------------------------------------ results table
    def _table_rows(self):
        """[[header...], [row...], ...] — parameters down the side, one column per completed run.

        This orientation because the table is read on screen to compare a handful of runs, and a
        human compares two numbers faster side by side than down a long column. Copy and Save emit
        exactly what is shown, so a pasted table matches the screen.
        """
        done = [r for r in self.runs if r.done]
        if not done:
            return []
        cols = []
        for r in done:
            cfg = PP.Settings(gauge_mm=r.gauge_mm, gauge_confirmed=r.gauge_confirmed,
                              gauge_src=r.gauge_src,
                              box_half=r.box_half, search=r.search,
                              min_corr=r.min_corr, ref_frame=r.ref_frame, ref_image=r.ref_image,
                              fps=r.fps, step=r.step, refine=r.refine)
            cols.append(PP.metrics(r.summary, cfg, label=r.label, source_video=r.path))
        names = [n for n, _ in cols[0]]
        rows = [["Parameter"] + [r.label for r in done]]
        for i, n in enumerate(names):
            rows.append([n] + [(c[i][1] if i < len(c) else "-") for c in cols])
        return rows

    def _refresh_table(self):
        rows = self._table_rows()
        self.table.clear()
        if not rows:
            self.table.setRowCount(0); self.table.setColumnCount(0)
            for b in (self.copyBtn, self.saveTableBtn):
                b.setEnabled(False)
            return
        hdr, body = rows[0], rows[1:]
        self.table.setColumnCount(len(hdr))
        self.table.setRowCount(len(body))
        self.table.setHorizontalHeaderLabels(hdr)
        done = [r for r in self.runs if r.done]
        for ri, row in enumerate(body):
            for ci, val in enumerate(row):
                it = QTableWidgetItem(str(val))
                if ci == 0:
                    it.setForeground(QColor("#8a8f98"))
                else:
                    # Colour each column to its trace, so a column and a curve are obviously the
                    # same run without reading the header.
                    it.setForeground(QColor(done[ci - 1].colour))
                self.table.setItem(ri, ci, it)
        self.table.resizeColumnsToContents()
        for b in (self.copyBtn, self.saveTableBtn):
            b.setEnabled(True)

    def on_copy_table(self):
        rows = self._table_rows()
        if not rows:
            return
        text = "\n".join("\t".join(str(c) for c in r) for r in rows)
        from PyQt6.QtWidgets import QApplication as _QA
        _QA.clipboard().setText(text)
        self.log.emit("[PostProc] results table copied (%d rows x %d columns)"
                      % (len(rows) - 1, len(rows[0]) - 1))

    def on_save_table(self):
        rows = self._table_rows()
        if not rows:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save the results table",
                                              "dic_postproc_results.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            import csv as _csv
            with open(path, "w", encoding="utf-8", newline="") as f:
                w = _csv.writer(f)
                w.writerow(["# UTM DIC post-processing — results"])
                w.writerow(["# Strain rate and noise are measured over the 0.05-0.35 % strain "
                            "window, the same convention this project's deck uses."])
                w.writerow([])
                for r in rows:
                    w.writerow(r)
            self.log.emit("[PostProc] wrote " + path)
        except Exception as e:
            QMessageBox.warning(self, "Could not write the table", str(e))

    def _run_dicts(self):
        """The completed runs in the plain form utm_postproc.build_report wants.

        An adapter rather than passing Run objects: utm_postproc must stay free of Qt so it can
        be tested and scripted without a display.
        """
        out = []
        for r in self.runs:
            if not r.done:
                continue
            out.append({"label": r.label, "colour": r.colour, "path": r.path,
                        "t": r.t, "e": r.e, "tr": r.tr, "summary": r.summary,
                        "cfg": PP.Settings(gauge_mm=r.gauge_mm, gauge_confirmed=r.gauge_confirmed,
                                           gauge_src=r.gauge_src,
                                            box_half=r.box_half,
                                           search=r.search, min_corr=r.min_corr,
                                           ref_frame=r.ref_frame, ref_image=r.ref_image,
                                           fps=r.fps, step=r.step,
                                           refine=r.refine, stop_on_loss=r.stop_on_loss)})
        return out

    def on_report(self):
        runs = self._run_dicts()
        if not runs:
            return
        folder = QFileDialog.getExistingDirectory(self, "Choose a folder for the report")
        if not folder:
            return
        try:
            files = PP.build_report(runs, folder,
                                    title="DIC post-processing — %s"
                                          % " vs ".join(r["label"] for r in runs),
                                    note="%d run(s)" % len(runs))
        except Exception as e:
            QMessageBox.warning(self, "Could not build the report", str(e))
            return
        self.log.emit("[PostProc] report written to %s:" % folder)
        for f in files:
            self.log.emit("           " + os.path.basename(f))
        QMessageBox.information(
            self, "Report written",
            "%d file(s) in:\n%s\n\n%s"
            % (len(files), folder, "\n".join(os.path.basename(f) for f in files)))

    def on_save_plot(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save the plot", "dic_strain_vs_time.png",
            "PNG image (*.png);;PDF (*.pdf);;SVG (*.svg)")
        if not path:
            return
        try:
            # facecolor from the figure so a dark-themed canvas does not save as a grey slab.
            self.fig.savefig(path, dpi=200, bbox_inches="tight",
                             facecolor=self.fig.get_facecolor())
            self.log.emit("[PostProc] wrote " + path)
        except Exception as e:
            QMessageBox.warning(self, "Could not write the image", str(e))

    # ------------------------------------------------------------------ gauge ⇄ px/mm
    def _l0_now(self):
        """Px₀ for the current run, or 0 when both boxes are not yet placed."""
        r = self.run
        if not (r and r.ready):
            return 0.0
        try:
            (ax, ay), (bx, by) = r.boxes[0][:2], r.boxes[1][:2]
            return float(((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5)
        except Exception:
            return 0.0

    def _on_gauge_edited(self, val):
        """The operator typed a gauge. Mirror it into px/mm and mark it confirmed."""
        if self._loading:
            return
        r = self.run
        if r is not None:
            r.gauge_mm = float(val)
            r.gauge_confirmed = True
            r.gauge_src = "typed"
            r.scale_anchor = "gauge"
        l0 = self._l0_now()
        if l0 > 0 and val > 0:
            self.pxmm.blockSignals(True)
            self.pxmm.setValue(l0 / float(val))
            self.pxmm.blockSignals(False)
        self._refresh_gauge_state()
        self._refresh_l0()

    def _on_pxmm_edited(self, val):
        """The operator typed a scale. The gauge follows from Px₀ — the same number, inverted."""
        if self._loading:
            return
        if val <= 0:
            return
        l0 = self._l0_now()
        if l0 <= 0:
            # No Px₀ yet, but the typed scale is real knowledge — keep it as this run's anchor
            # so the gauge is measured the moment boxes exist, instead of throwing it away.
            r = self.run
            if r is not None:
                r.px_mm = float(val)
                r.scale_anchor = "pxmm"
                r.gauge_src = "measured from px/mm"
            self._refresh_gauge_state()
            return
        g = l0 / float(val)
        self.gauge.blockSignals(True)
        self.gauge.setValue(g)
        self.gauge.blockSignals(False)
        r = self.run
        if r is not None:
            r.gauge_mm = float(g)
            r.gauge_confirmed = True
            r.gauge_src = "measured from px/mm"
            r.scale_anchor = "pxmm"
            r.px_mm = float(val)
        self._refresh_gauge_state()
        self._refresh_l0()

    def _refresh_gauge_state(self):
        """Keep px/mm in step with Px₀, and say plainly what the mm scale rests on.

        Three states, three colours: nothing (the gauge is confirmed — typed, measured from a
        known px/mm, or taken from the capture's own record); GREEN when the scale is already
        known but Px₀ does not exist yet, because that is an instruction, not a doubt; AMBER
        only when the mm scale genuinely rests on the unconfirmed 80 mm default.
        """
        r = self.run
        anchor = getattr(r, "scale_anchor", "gauge") if r is not None else "gauge"
        l0 = self._l0_now()
        if l0 > 0 and self.gauge.value() > 0 and anchor != "pxmm":
            self.pxmm.blockSignals(True)
            self.pxmm.setValue(l0 / self.gauge.value())
            self.pxmm.blockSignals(False)
        if r is None:
            self.gaugeWarn.setText("")
            return
        if r.gauge_confirmed:
            self.gaugeWarn.setText("")
        elif anchor == "pxmm" and getattr(r, "px_mm", 0) > 0:
            self.gaugeWarn.setStyleSheet("color:#2e9e4f;")
            self.gaugeWarn.setText(
                "Scale is known: %.4f px/mm (%s). Place or pick the two markers and the gauge "
                "box MEASURES that pair — nothing to type." % (r.px_mm, r.gauge_src or "typed"))
        else:
            self.gaugeWarn.setStyleSheet("color:#f39c12;")
            self.gaugeWarn.setText(
                "Gauge is the default %.2f mm — nobody has confirmed it for this video. Strain is "
                "unaffected (it is a pixel ratio), but px/mm and the extension in mm are, and the "
                "results sheet will say ASSUMED until you set it. Type the real marker distance "
                "into Gauge, or a known px/mm — either one anchors the other." % r.gauge_mm)

    # ------------------------------------------------------------------ companion data file
    def on_attach_companion(self):
        """Attach the acquisition file recorded beside this video, and use what it knows.

        Written as one action rather than three separate prompts because the operator has one
        thing to hand — the file — and the dialog is the thing that should know what to do with it.
        """
        r = self.run
        if r is None:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Data file recorded with this video", os.path.dirname(r.path),
            "Data (*.csv *.daq *.txt *.tsv);;All files (*)")
        if not path:
            return
        try:
            comp = PP.read_companion(path)
        except Exception as e:
            QMessageBox.warning(self, "Cannot read that file",
                                "%s\n\n%s\n\nIt needs a monotonic time column; everything else is "
                                "optional." % (os.path.basename(path), e))
            return

        msgs = []
        r.companion = comp

        got = PP.fps_from_companion(r.info, comp)
        if got:
            fps, note = got
            self.fps.blockSignals(True)
            self.fps.setValue(fps)
            self.fps.blockSignals(False)
            r.fps, r.fps_note, r.fps_verified, r.fps_override = fps, note, True, False
            msgs.append(note)
        else:
            msgs.append("The file gave no usable duration, so the frame rate is unchanged.")

        if comp.gauge_mm:
            self.gauge.blockSignals(True)
            self.gauge.setValue(comp.gauge_mm)
            self.gauge.blockSignals(False)
            r.gauge_mm, r.gauge_confirmed = float(comp.gauge_mm), True
            r.gauge_src = "from %s" % comp.source
            r.scale_anchor = "gauge"
        if getattr(comp, "px_per_mm", None):
            # The file carries the session's own DIC calibration - the strongest anchor there
            # is. With the SCALE known, the gauge box measures whichever pair is picked: his
            # multi-marker case (45 mm pair, 60 mm pair...) reads the right number with no
            # typing at all.
            self.pxmm.blockSignals(True)
            self.pxmm.setValue(float(comp.px_per_mm))
            self.pxmm.blockSignals(False)
            r.scale_anchor = "pxmm"
            r.px_mm = float(comp.px_per_mm)
            r.gauge_src = "measured from %s calibration" % comp.source
            msgs.append("Scale anchored to the file's own calibration: %.4f px/mm - the gauge "
                        "box now MEASURES whichever marker pair you pick." % comp.px_per_mm)
            self._refresh_l0()
        elif comp.gauge_mm:
            msgs.append("Gauge set to %.4f mm from the file's own gauge column." % comp.gauge_mm)

        if comp.load is not None:
            msgs.append("Load channel found — the noise window will be anchored at the preload "
                        "rather than at the first frame.")
        else:
            msgs.append("No named load column, so the noise window will fall back to the "
                        "straightest part of the record.")

        self.compLbl.setText("%s — %s" % (comp.source, comp.note))
        self.compLbl.setStyleSheet("color:#2e9e4f;")
        self.fpsWarn.setText(r.fps_note)
        self._refresh_gauge_state()
        self._refresh_l0()
        self._refresh_list()
        for m in msgs:
            self.log.emit("[PostProc] %s" % m)
        QMessageBox.information(self, "Data file attached", "\n\n".join(msgs))

    def _fps_block_reason(self):
        """Why this run must not start yet, or '' — the frame-rate half of the guard.

        The warning existed before and was ignorable, which is how a 1000 fps container field
        reached a published time axis. It now stops the run until the operator either fixes the
        number, attaches the acquisition file, or says explicitly that they mean it.
        """
        r = self.run
        if r is None or r.fps_verified or r.fps_override:
            return ""
        return PP.fps_is_suspect(r.fps, False)

    def _store_widgets(self):
        """Write the controls back into the selected run, so each keeps its own setup."""
        r = self.run
        if r is None or self._loading:
            return
        r.box_half = self.boxHalf.value()
        r.search = self.search.value()
        r.min_corr = self.minCorr.value()
        # ref_frame is NOT taken from the slider: the slider browses, and only on_set_ref commits.
        if abs(r.fps - self.fps.value()) > 1e-9:
            # An operator who types a frame rate has looked at it, which is the whole point of the
            # guard; a value that arrives from a sidecar or a companion sets fps_verified itself.
            r.fps_override = True
        r.fps = self.fps.value()
        r.step = self.step.value()
        r.refine = self.method.currentData()
        r.stop_on_loss = self.stopLossChk.isChecked()
        r.gauge_mm = self.gauge.value()
        r.area_mm2 = self.area.value()

    def on_select_run(self, i):
        if self._busy():
            return
        self._cur = i
        r = self.run
        if r is None:
            return
        self._loading = True
        try:
            self.gauge.blockSignals(True); self.pxmm.blockSignals(True)
            self.boxHalf.setValue(r.box_half); self.search.setValue(r.search)
            self.minCorr.setValue(r.min_corr); self.fps.setValue(r.fps)
            self.step.setValue(r.step)
            self.gauge.setValue(r.gauge_mm)
            if getattr(r, "px_mm", 0) > 0:
                # This run's own calibration back into the shared spin — without it, a
                # px/mm-anchored run inherits whatever scale the PREVIOUS run left behind.
                self.pxmm.setValue(r.px_mm)
            k = self.method.findData(r.refine)
            if k >= 0:
                self.method.setCurrentIndex(k)
            self.stopLossChk.setChecked(r.stop_on_loss)
            self.area.setValue(getattr(r, "area_mm2", 80.0))
            self.gauge.blockSignals(False); self.pxmm.blockSignals(False)
            self.fpsWarn.setText(r.fps_note)
            c = r.companion
            self.compLbl.setText(("%s — %s" % (c.source, c.note)) if c
                                 else "no data file attached")
            self.compLbl.setStyleSheet("color:#2e9e4f;" if c else "color:#888;")
            self.fileLbl.setText("%s — %d frames, %dx%d"
                                 % (r.info["name"], r.info["frames"], r.info["w"], r.info["h"]))
            self.frameSlider.setEnabled(True)
            self.playPauseBtn.setEnabled(True)
            self.frameSlider.blockSignals(True)
            self.frameSlider.setRange(0, max(0, r.info["frames"] - 1))
            self.frameSlider.setValue(r.ref_frame)
            self.frameSlider.blockSignals(False)
            self.frameLbl.setText(str(r.ref_frame))
            self.setRefBtn.setEnabled(True)
            self._next_box = 0
            self._show_reference()
        finally:
            self._loading = False
        self._refresh_ref_label()
        self._refresh_gauge_state()
        self._refresh_l0()
        self.status.setText("%s — %s" % (r.label, r.status()))

    def on_rename(self, item):
        r = self.run
        if r is None:
            return
        name, ok = QInputDialog.getText(self, "Rename", "Legend label:", text=r.label)
        if ok and name.strip():
            r.label = name.strip()
            self._refresh_list()
            self._refresh_table()
            self._redraw_plot()

    def on_remove(self):
        if self._busy() or self.run is None:
            return
        i = self._cur
        self.runs.pop(i)
        self._cur = min(i, len(self.runs) - 1)
        self._refresh_list()
        self._refresh_table()
        if self.runs:
            self.runList.setCurrentRow(self._cur)
            self.on_select_run(self._cur)
        else:
            self.view.set_frame(np.zeros((10, 10), np.uint8))
            self.fileLbl.setText("no video loaded")
        self._redraw_plot()

    def on_clear_all(self):
        if self._busy():
            return
        self.runs = []
        self._cur = -1
        self._refresh_list()
        self.fileLbl.setText("no video loaded")
        self.runBtn.setEnabled(False)
        self._refresh_table()
        self._reset_plot()

    def _show_frame(self, idx):
        g = PP.read_frame(self.path, idx)
        if g is None:
            return
        self.view.set_frame(g)
        # Found once per displayed frame, not once per click: the sweep is the expensive part and
        # the frame does not change between clicks.
        self._markers = PP.find_markers(g)
        self._markers_frame = idx
        self.view.set_markers(self._markers)
        self._refresh_boxes()

    def on_browse_frame(self, v):
        """Scrubbing shows a frame. It does NOT decide which frame is the reference."""
        self.frameLbl.setText(str(v))
        if self.path:
            self._show_frame(v)
        self._refresh_ref_label()

    def on_set_ref(self):
        """Fix the frame now on screen as the reference, and say what that changed."""
        r = self.run
        if r is None:
            return
        was, now = r.ref_frame, self.frameSlider.value()
        r.ref_frame = now
        self._refresh_ref_label()
        self._refresh_l0()
        if was != now:
            self.log.emit("[PostProc] %s — reference frame %d → %d. Px₀ is re-measured at that "
                          "frame when the run starts, so check the boxes still sit on the markers."
                          % (r.label, was, now))
            self.status.setText("Reference frame set to %d. Px₀ will be measured there — check "
                                "the boxes are still on the markers." % now)
        else:
            self.log.emit("[PostProc] %s — reference frame confirmed at %d" % (r.label, now))
            self.status.setText("Reference frame confirmed at %d." % now)
        self.status.setStyleSheet("color:%s;" % self._status_fg())
        self._refresh_list()

    def on_ref_image(self):
        """Pick a still to use as the reference, or go back to the video.

        The image is shown as soon as it is accepted. That is deliberate rather than cosmetic: the
        boxes and Px₀ belong to the reference, so the reference has to be what is on screen when
        they are placed.
        """
        r = self.run
        if r is None:
            return
        if r.ref_image:                       # already using one — this press reverts
            r.ref_image = ""
            self.boxes = [None, None]
            self._next_box = 0
            self.log.emit("[PostProc] %s — reference back to the video, frame %d. Boxes cleared: "
                          "they belonged to the image." % (r.label, r.ref_frame))
            self.status.setText("Reference is the video again, frame %d. Place the boxes again."
                                % r.ref_frame)
            self._show_frame(r.ref_frame)
            self._refresh_ref_label(); self._refresh_l0(); self._refresh_list()
            return

        path, _ = QFileDialog.getOpenFileName(
            self, "Choose a reference image", os.path.dirname(r.path),
            "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff);;All files (*)")
        if not path:
            return
        aligned, off, note = PP.reference_align(path, r.path, r.ref_frame)
        if aligned is None:
            QMessageBox.warning(self, "That image cannot be the reference",
                                "%s\n\n%s" % (os.path.basename(path), note))
            return
        r.ref_image = path
        if note:
            # It fitted, but not exactly. Say how it was made to fit rather than adjusting
            # silently — our own capture stills are one column wider than the AVI beside them,
            # because the video writer rounds an odd width down to an even one.
            self.log.emit("[PostProc] reference image %s — %s" % (os.path.basename(path), note))
        # The old boxes were placed on a different picture. Keeping them would silently measure
        # Px₀ at coordinates chosen against something else.
        self.boxes = [None, None]
        self._next_box = 0
        self._show_reference()
        self.log.emit("[PostProc] %s — reference image %s. Boxes cleared; place them on it."
                      % (r.label, os.path.basename(path)))
        self.status.setText("Reference image set. Place the two boxes on IT — Px₀ is measured here.")
        self._refresh_ref_label(); self._refresh_l0(); self._refresh_list()

    def _show_reference(self):
        """Put the reference on screen — the image if there is one, else its video frame."""
        r = self.run
        if r is None:
            return
        if r.ref_image:
            # The ALIGNED image, so the boxes are placed on exactly the pixels analyse() will use.
            # Showing the raw still instead would put them one column out on our own captures.
            g, _off, _note = PP.reference_align(r.ref_image, r.path, r.ref_frame)
            if g is None:
                return
            self.view.set_frame(g)
            self._markers = PP.find_markers(g)
            self._markers_frame = -1          # not a video frame; see on_auto's off-reference check
            self.view.set_markers(self._markers)
            self._refresh_boxes()
        else:
            self._show_frame(r.ref_frame)

    def _refresh_ref_label(self):
        """Say which frame is fixed, and flag it when the view has wandered off that frame.

        Without this the only clue that you are looking at frame 900 while the reference is frame 0
        is the small number beside the slider, which reads the same either way.
        """
        if not getattr(self, "refLbl", None):
            return
        r = self.run
        if r is None:
            self.refLbl.setText("")
            return
        self.refImgBtn.setEnabled(True)
        self.refImgBtn.setText("Use the video" if r.ref_image else "Use an image…")
        here = self.frameSlider.value()
        if r.ref_image:
            # With an image as the zero, the slider cannot change the reference at all, so the
            # "set this frame" button has nothing to do and says so by being unavailable.
            self.setRefBtn.setEnabled(False)
            if self._markers_frame == -1:
                self.refLbl.setText("reference = image: %s  ✔"
                                    % os.path.basename(r.ref_image))
                self.refLbl.setStyleSheet("color:#2ecc71; font-weight:bold;")
            else:
                self.refLbl.setText("viewing video frame %d — the reference is the image %s"
                                    % (here, os.path.basename(r.ref_image)))
                self.refLbl.setStyleSheet("color:#ffc046; font-weight:bold;")
            return
        if here == r.ref_frame:
            self.refLbl.setText("reference = frame %d  ✔" % r.ref_frame)
            self.refLbl.setStyleSheet("color:#2ecc71; font-weight:bold;")
            self.setRefBtn.setEnabled(False)
        else:
            self.refLbl.setText("viewing frame %d — reference is still %d"
                                % (here, r.ref_frame))
            self.refLbl.setStyleSheet("color:#ffc046; font-weight:bold;")
            self.setRefBtn.setEnabled(True)

    def _arm_pair(self, kind):
        """The next TWO clicks on the frame define an extra pair of the given kind."""
        if self.run is None:
            return
        self._arm_extra, self._extra_first = kind, None
        self.log.emit("[PostProc] click the %s of the %s pair"
                      % ("first point", "axial" if kind == "axial" else "width"))
        self.status.setText("placing a %s pair — click point 1 of 2"
                            % ("second axial" if kind == "axial" else "width"))
        # He asked for exactly this: picking in the small pane is guesswork, so arming a pair
        # brings up the desk-sized view. Clicks there land in the same handlers.
        self.on_big_view()

    def on_manual_main(self):
        """Select manually… — the big window, primed for the MAIN pair: next click is box A."""
        if self.run is None:
            return
        self._arm_extra = self._extra_first = None
        self._next_box = 0
        self.log.emit("[PostProc] manual marker selection — click box A, then box B "
                      "(existing boxes stay until replaced; drag to adjust)")
        self.on_big_view()

    def on_big_view(self):
        if self.run is None:
            return
        if self._bigpick is None:
            self._bigpick = BigPickDialog(self)
        self._bigpick.refresh()
        self._bigpick.show()
        self._bigpick.raise_()
        self._bigpick.activateWindow()

    def on_clear_pairs(self):
        if self.run is not None:
            self.run.extra_pairs = []
        self._arm_extra = self._extra_first = None
        self._refresh_boxes()

    def _click_extra(self, x, y):
        """Second half of _arm_pair: collect the two clicks, snapping like the main boxes do."""
        snapped = PP.snap_to_marker(getattr(self, "_markers", []), x, y)
        if snapped:
            x, y = snapped[0], snapped[1]
        if self._extra_first is None:
            self._extra_first = (x, y)
            self.status.setText("placing the pair — click point 2 of 2")
            return
        (x1, y1), kind = self._extra_first, self._arm_extra
        r = self.run
        n_axial = sum(1 for p in r.extra_pairs if p[4] == "axial")
        label = ("width" if kind == "transverse" else "axial %d" % (n_axial + 2))
        r.extra_pairs.append((x1, y1, x, y, kind, label))
        self._arm_extra = self._extra_first = None
        dx, dy = abs(x - x1), abs(y - y1)
        self.log.emit("[PostProc] %s pair \"%s\" placed — %.1f px apart%s"
                      % (kind, label, (dx * dx + dy * dy) ** 0.5,
                         "" if (kind == "transverse") == (dx > dy) else
                         "  (NB: separation runs mostly %s — is the kind right?)"
                         % ("axially" if dy > dx else "across")))
        self._refresh_boxes()

    def on_click(self, x, y):
        """Place a box — on the nearest marker's CENTRE when there is one near the click.

        The centre is what sets L0, and hitting it by eye is guesswork. A click near a dot
        therefore means that dot's computed centroid. On a speckle pattern there are no discrete
        markers, nothing is close enough, and the click stands exactly where it was made.
        """
        if getattr(self, "_markers_frame", None) != self.frameSlider.value():
            # The view is showing the last analysed frame after a run, or the markers are stale.
            # Boxes are always placed on the REFERENCE frame, so put that back before placing —
            # otherwise the click would be measured against a picture it does not belong to.
            self._show_frame(self.frameSlider.value())
            self.log.emit("[PostProc] back to the reference frame (%d) to place a box"
                          % self.frameSlider.value())
        if getattr(self, "_arm_extra", None):
            self._click_extra(x, y)
            return
        snapped = PP.snap_to_marker(getattr(self, "_markers", []), x, y)
        if snapped:
            cx, cy, moved, m = snapped
            self.boxes[self._next_box] = (cx, cy)
            self.log.emit("[PostProc] box %s snapped to a marker centre — moved %.1f px "
                          "(r %.0f px, circularity %.2f)"
                          % ("AB"[self._next_box], moved, m[2], m[3]))
            self._suggest_box_size(m[2])
        else:
            self.boxes[self._next_box] = (x, y)
            if getattr(self, "_markers", None):
                self.log.emit("[PostProc] box %s placed as clicked — no marker within snapping "
                              "range" % "AB"[self._next_box])
        self._next_box = 1 - self._next_box
        self._refresh_boxes()

    def on_box_moved(self, i, x, y):
        """A drag or an arrow-key nudge — free placement, deliberately without snapping."""
        self.boxes[i] = (x, y)
        self._refresh_l0()

    def on_clear(self):
        self.boxes = [None, None]
        self._next_box = 0
        self._refresh_boxes()

    def on_auto(self):
        """Find the two markers with the shared finder, so it agrees with click-to-snap."""
        if not self.path:
            return
        g = PP.read_frame(self.path, self.frameSlider.value())
        markers = PP.find_markers(g)
        self._markers = markers
        # Drop specks: a marker pair is made of the BIG round things. Without this a 13 px
        # artefact at the frame edge competes with a 60 px sprayed dot on circularity alone.
        if markers:
            rmax = max(m[2] for m in markers)
            markers = [m for m in markers if m[2] >= 0.35 * rmax]
        if len(markers) < 2:
            QMessageBox.information(
                self, "No marker pair found",
                "Could not find two round markers in this frame.\n\n"
                "That is expected on a speckle pattern, which has no discrete dots — click the "
                "frame twice to place the boxes by hand instead. Clicks snap to a marker centre "
                "when there is one, and stay where you put them when there is not.")
            return
        pair = sorted(markers[:2], key=lambda m: m[1])
        self.boxes = [(pair[0][0], pair[0][1]), (pair[1][0], pair[1][1])]
        self._next_box = 0
        # Size the patch to the marker it is tracking. The 24 px default is a fraction of a 60 px
        # sprayed dot, which both correlates on less of the pattern than it could AND draws a box
        # far smaller than the dot, leaving nothing to judge centring by. 1.25x the radius keeps
        # the whole dot plus a little of its surround.
        self._suggest_box_size(max(pair[0][2], pair[1][2]))
        self._refresh_boxes()
        self.log.emit("[PostProc] auto-detected 2 markers — r %.0f/%.0f px, circularity %.2f/%.2f"
                      % (pair[0][2], pair[1][2], pair[0][3], pair[1][3]))
        # Boxes belong to the reference frame, but detection runs on whatever is on screen. Now
        # that scrubbing no longer drags the reference along, detecting on a browsed frame and
        # running against a different reference is an easy mistake to make silently.
        r = self.run
        here = self.frameSlider.value()
        if r is not None and r.ref_image:
            if self._markers_frame != -1:
                self.status.setText("⚠  Markers were detected on video frame %d, but the reference "
                                    "is the image %s. Press 'Use the video' to switch back, or "
                                    "re-show the image before detecting."
                                    % (here, os.path.basename(r.ref_image)))
                self.status.setStyleSheet("color:#ffc046; font-weight:bold;")
                self.log.emit("[PostProc] NOTE: detected on frame %d, reference is an image" % here)
        elif r is not None and here != r.ref_frame:
            self.status.setText("⚠  Markers were detected on frame %d, but the reference is frame "
                                "%d. Press 'Set this frame as the reference', or go back to frame "
                                "%d and detect again." % (here, r.ref_frame, r.ref_frame))
            self.status.setStyleSheet("color:#ffc046; font-weight:bold;")
            self.log.emit("[PostProc] NOTE: detected on frame %d, reference is %d"
                          % (here, r.ref_frame))

    def _suggest_box_size(self, marker_radius):
        """Size the patch to the marker. This is the single biggest lever on noise.

        A box smaller than the dot sees only its flat interior — no gradient, nothing to localise
        on, because the information is at the EDGE. Measured on S25 over a matched strain window:
        24 px half-size gives 313 microstrain of noise, 40 gives 150, and 1.25x the marker radius
        (75 px here) gives 22 — against 28 for the live rig. A 14x difference from one number
        nobody would think to change.
        """
        want = int(round(1.25 * marker_radius))
        want = max(self.boxHalf.minimum(), min(self.boxHalf.maximum(), want))
        if want > self.boxHalf.value():
            old = self.boxHalf.value()
            self.boxHalf.setValue(want)
            self.log.emit("[PostProc] box half-size %d -> %d px to cover a %.0f px marker. A box "
                          "smaller than the dot sees only flat interior and tracks it poorly."
                          % (old, want, marker_radius))

    def _refresh_boxes(self):
        self.view.set_boxes(self.boxes[0], self.boxes[1], self.boxHalf.value())
        r = self.run
        pairs = r.extra_pairs if r is not None else []
        self.view.set_extra(pairs)
        self.extraLbl.setText("  ·  ".join(
            "P%d %s (%s)" % (i + 1, p[5], p[4]) for i, p in enumerate(pairs)))
        if self._bigpick is not None and self._bigpick.isVisible():
            self._bigpick.refresh()
        self._refresh_l0()
        self._refresh_list()

    def _refresh_l0(self):
        a, b = self.boxes
        if a and b:
            l0 = float(np.hypot(b[0] - a[0], b[1] - a[1]))
            r = self.run
            anchor = getattr(r, "scale_anchor", "gauge") if r is not None else "gauge"
            if anchor == "pxmm" and self.pxmm.value() > 0:
                # The scale is the known thing (he typed a calibrated px/mm), so the GAUGE is
                # the measurement: re-derived live at every placement, snap and drag — his ask
                # (2026-09-06): "show the value that you measured instead" of the 80 mm default.
                g = l0 / self.pxmm.value()
                self.gauge.blockSignals(True)
                self.gauge.setValue(g)
                self.gauge.blockSignals(False)
                if r is not None:
                    r.gauge_mm, r.gauge_confirmed = float(g), True
                    # keep a richer provenance ("measured from S38….csv calibration") if one
                    # is already on record — this runs at every drag and must not flatten it
                    r.gauge_src = r.gauge_src or "measured from px/mm"
                self.l0Lbl.setText("Px₀ = %.2f px    →    gauge MEASURED: %.2f mm at the "
                                   "known %.4f px/mm" % (l0, g, self.pxmm.value()))
                self._refresh_gauge_state()
                self.runBtn.setEnabled(self.path is not None
                                       and not (self.worker and self.worker.isRunning()))
                self._update_px_label()
                return
            ppm = l0 / self.gauge.value() if self.gauge.value() > 0 else 0
            # keep the px/mm SPIN live too — it used to go stale the moment a box moved
            if ppm > 0:
                self.pxmm.blockSignals(True)
                self.pxmm.setValue(ppm)
                self.pxmm.blockSignals(False)
            self.l0Lbl.setText("Px₀ = %.2f px    →    %.4f px/mm at %.2f mm"
                               % (l0, ppm, self.gauge.value()))
            self.runBtn.setEnabled(self.path is not None and not (self.worker and self.worker.isRunning()))
            self._update_px_label()
        else:
            self.l0Lbl.setText("place two boxes to set Px₀")
            self.runBtn.setEnabled(False)
            self._update_px_label()

    def _cfg(self):
        r = self.run
        return PP.Settings(gauge_mm=self.gauge.value(),
                           gauge_confirmed=bool(r and r.gauge_confirmed),
                           gauge_src=(r.gauge_src if r else ""),
                           box_half=self.boxHalf.value(),
                           search=self.search.value(), min_corr=self.minCorr.value(),
                           ref_frame=(r.ref_frame if r else 0),
                           ref_image=(r.ref_image if r else ""),
                           fps=self.fps.value(),
                           step=self.step.value(), refine=self.method.currentData(),
                           stop_on_loss=self.stopLossChk.isChecked())

    def _confirm_suspect_fps(self):
        """Stop a run whose frame rate is unverified AND implausible. True = go ahead.

        The dialog already warned about this in amber and was ignored, which is the whole lesson:
        a warning that does not interrupt is a warning that gets published. The operator can still
        proceed — but only by saying so, and the choice is remembered for that video.
        """
        why = self._fps_block_reason()
        if not why:
            return True
        r = self.run
        m = QMessageBox(self)
        m.setIcon(QMessageBox.Icon.Warning)
        m.setWindowTitle("Check the frame rate before running")
        m.setText("%s is about to be measured at %.4f fps, and that number has not been verified."
                  % (r.info["name"], r.fps))
        m.setInformativeText(
            "%s.\n\nStrain will be correct either way — it is a pixel ratio. Everything with time "
            "in it will not be: duration, strain rate, and the whole time axis.\n\n"
            "Attach the data file recorded with this video and the rate is computed from it "
            "exactly, or type the rate you know is right." % why.capitalize())
        attach = m.addButton("Attach data file…", QMessageBox.ButtonRole.AcceptRole)
        anyway = m.addButton("Run at %.4f fps anyway" % r.fps, QMessageBox.ButtonRole.DestructiveRole)
        m.addButton(QMessageBox.StandardButton.Cancel)
        m.setDefaultButton(attach)
        m.exec()
        if m.clickedButton() is attach:
            self.on_attach_companion()
            return False
        if m.clickedButton() is anyway:
            r.fps_override = True
            self.log.emit("[PostProc] %s: running at an UNVERIFIED %.4f fps by operator override"
                          % (r.info["name"], r.fps))
            return True
        return False

    def on_run(self, _checked=False, queued=False):
        # Any amber left over from setup — the off-reference detect hint — stops applying the
        # moment a run starts, and nothing else would clear it now that the marker-lost warning
        # has moved to a dialog.
        self.status.setStyleSheet("color:%s;" % self._status_fg())
        # A zoom chosen for the previous run should not frame this one.
        self.ax.set_autoscale_on(True)
        r = self.run
        if r is None or not r.ready or self._busy():
            return
        self._store_widgets()
        if not self._confirm_suspect_fps():
            self._queue = []               # a queued Run-all stops here rather than rolling on
            self.runBtn.setEnabled(True)
            self._refresh_list()
            return
        r.t, r.e, r.tr, r.summary = [], [], [], None
        r.xe = [[] for _ in r.extra_pairs]
        r.poisson_rows, r.poisson_note = None, ""
        a, b = r.boxes
        self.on_stop_play()                    # scrubbing and measuring must not share the file
        self.playPauseBtn.setEnabled(False)
        self.runBtn.setEnabled(False); self.runAllBtn.setEnabled(False)
        self.stopBtn.setEnabled(True)
        cfg = self._cfg()
        extras = [(PP.Box(p[0], p[1], cfg.box_half), PP.Box(p[2], p[3], cfg.box_half),
                   p[4], p[5]) for p in r.extra_pairs]
        self._run_boxhalf = cfg.box_half
        self._last_extra_pts = []
        self._popout_gen = getattr(self, "_popout_gen", 0) + 1
        if self.playChk.isChecked():
            # The pop-out covers the LEFT column exactly — the setup pane it hides is idle
            # during a run, and the plot on the right stays fully visible (sized to the pane
            # rather than the screen at his request, from the geometry he liked on the rig).
            if self._popout is None:
                self._popout = TrackPopout(self)
            pane = getattr(self, "_left_pane", None)
            if pane is not None and pane.isVisible():
                g = pane.mapToGlobal(pane.rect().topLeft())
                self._popout.setGeometry(g.x(), g.y(), pane.width(), pane.height())
            self._popout.setWindowTitle("Tracking — %s" % r.label)
            self._popout.status.setText("waiting for the first frame…")
            self._popout.show()
        self.worker = Worker(r.path, PP.Box(a[0], a[1], cfg.box_half),
                             PP.Box(b[0], b[1], cfg.box_half), cfg,
                             preview=self.playChk.isChecked(), extras=extras)
        self.worker.row.connect(self.on_row)
        self.worker.done.connect(self.on_done)
        self.worker.failed.connect(self.on_failed)
        self.worker.frame.connect(self.on_frame)
        self.worker.progress.connect(lambda d, t: self.bar.setValue(int(100 * d / max(1, t))))
        self._running = self._cur
        self.worker.start()
        self.log.emit("[PostProc] analysing \"%s\" (%s) from frame %d at %.4f fps, %s"
                      % (r.label, r.info["name"], cfg.ref_frame, cfg.fps, cfg.refine))

    def on_run_all(self):
        """Queue every ready, un-run video and work through them one at a time.

        Sequential rather than parallel on purpose: the point is watching each pull as it is
        measured, and four videos decoding at once would compete for the same disk and CPU while
        showing nothing useful.
        """
        if self._busy():
            return
        self._queue = [i for i, r in enumerate(self.runs) if r.ready and not r.done]
        if not self._queue:
            QMessageBox.information(self, "Nothing to run",
                                    "Every video with its boxes placed has already been run.\n\n"
                                    "Add another video, or place boxes on one that still needs them.")
            return
        self.log.emit("[PostProc] running %d video(s) back to back" % len(self._queue))
        self._next_in_queue()

    def _next_in_queue(self):
        while self._queue:
            i = self._queue.pop(0)
            if 0 <= i < len(self.runs) and self.runs[i].ready and not self.runs[i].done:
                self.runList.setCurrentRow(i)
                self.on_select_run(i)
                self.on_run(queued=True)
                return
        self._refresh_list()

    def on_stop(self):
        # Stop means stop the SWEEP, not just this video — otherwise the next one starts
        # immediately and the button appears not to have worked.
        self._queue = []
        if self.worker:
            self.worker.stop()

    def on_frame(self, gray, a, b, half):
        """Paint one frame of the pull, then tell the worker it may send the next.

        The preview stream is downscaled before crossing the thread and `half` was scaled with
        it, so half / the running box_half recovers the factor — the cached extra-pair points
        are in raw frame pixels and scale by the same k to land on this frame."""
        k = half / max(1e-9, float(self._run_boxhalf or self.boxHalf.value()))
        ext = [(ax * k, ay * k, bx * k, by * k, kind, lbl)
               for (ax, ay, bx, by, kind, lbl) in self._last_extra_pts]
        self.view.play(gray, a, b, half, extra=ext)
        if self._popout is not None and self._popout.isVisible():
            self._popout.play(gray, a, b, half, extra=ext)
        if self.worker:
            self.worker.frame_shown()

    def on_row(self, r):
        cur = self.run
        if cur is not None:
            if r.ok:
                cur.t.append(r.t); cur.e.append(r.cauchy); cur.tr.append(r.true)
                for j, xs in enumerate(cur.xe):
                    ej = r.extra[j] if j < len(r.extra) else None
                    xs.append(ej[5] if (ej and ej[6]) else float("nan"))
                self._last_extra_pts = [
                    (e[0], e[1], e[2], e[3], pair[4], pair[5])
                    for e, pair in zip(r.extra, cur.extra_pairs) if e[6]]
                self._update_px_label(l_px=r.l_px, corr=r.corr)
            elif not cur.stop_on_loss and cur.t and cur.e[-1] == cur.e[-1]:
                # An untracked frame, with "stop when lost" OFF. Record it as a HOLE rather than
                # skipping it: matplotlib breaks a line at NaN, so the curve shows the dropout
                # instead of drawing a straight segment across it. One NaN per gap is enough.
                #
                # Only when the option is off. With it on, the generator still yields the first
                # lost row before giving up on the second, so holing that one would leave a NaN as
                # the series' LAST point — making t[-1] the instant tracking failed rather than the
                # last instant actually measured, which is not what "where the data ends" means.
                cur.t.append(r.t)
                cur.e.append(float("nan")); cur.tr.append(float("nan"))
                for xs in cur.xe:
                    xs.append(float("nan"))
        _live = ("frame %d   t %.2f s   L %s px   ε %s   corr %.2f%s"
                 % (r.idx, r.t,
                    "—" if r.l_px != r.l_px else "%.2f" % r.l_px,
                    "—" if r.cauchy != r.cauchy else "%.4f %%" % (r.cauchy * 100),
                    r.corr, ("   " + r.note) if r.note else ""))
        self.status.setText(_live)
        if self._popout is not None and self._popout.isVisible():
            # it read "waiting for the first frame…" for the entire run — the label was set at
            # open and only touched again at the end
            self._popout.status.setText(_live)
        self._redraw_plot(force=False)

    def _redraw_plot(self, force=True):
        """One line per run, plus the one being measured. force=False obeys a time throttle.

        Lines are rebuilt rather than kept as fixed handles because runs are added and removed;
        the throttle is what keeps that affordable during a live run.
        """
        if not force:
            now = time.monotonic()
            if now - getattr(self, "_last_plot", 0.0) < 1.0 / self.PLOT_HZ:
                return
            self._last_plot = now
        # A live run redraws several times a second, and ax.clear() would reset the view every
        # time — so a zoom set during a run would vanish before it could be read. Matplotlib turns
        # autoscale OFF when the operator pans or zooms, which is exactly the signal for "this
        # window was chosen deliberately, keep it".
        keep = None
        if not (self.ax.get_autoscalex_on() and self.ax.get_autoscaley_on()):
            keep = (self.ax.get_xlim(), self.ax.get_ylim())
        self.ax.clear()
        self._style_plot()
        any_data = False
        for i, r in enumerate(self.runs):
            if not r.t:
                continue
            any_data = True
            live = (i == self._running)
            self.ax.plot(r.t, [v * 100 for v in r.e], color=r.colour, lw=1.6,
                         label=r.label + (" (running)" if live else ""))
            for j, xs in enumerate(getattr(r, "xe", []) or []):
                if not xs or j >= len(r.extra_pairs):
                    continue
                kind, lbl = r.extra_pairs[j][4], r.extra_pairs[j][5]
                n = min(len(r.t), len(xs))
                self.ax.plot(r.t[:n], [v * 100 for v in xs[:n]],
                             color=pair_colour(r.extra_pairs, j), lw=1.4,
                             ls=":" if kind == "transverse" else "-.", alpha=0.95,
                             label="%s — %s%s" % (r.label, lbl,
                                                  " (lateral ε)" if kind == "transverse" else ""))
            if self._want_true():
                self.ax.plot(r.t, [v * 100 for v in r.tr], color=r.colour, lw=1.0, ls="--",
                             alpha=0.7, label="%s — true" % r.label)
            # A lost marker is deliberately NOT annotated on the plot. It used to get a cross and a
            # caption here; with several runs overlaid those pile up on the busiest part of the
            # chart, and the plot is also what gets saved and pasted into a document, where an
            # annotation aimed at the operator becomes clutter aimed at a reader.
            #
            # It is reported in three places that survive being saved instead: a dialog when the
            # run ends, the "Tracking ended" and "Data ends at" rows of the results table, and the
            # generated report.
        if any_data:
            leg = self.ax.legend(frameon=False, fontsize=9)
            if _theme is not None:
                for txt in leg.get_texts():
                    txt.set_color(_theme.get(self._theme_name)["plot_fg"])
        if keep:
            self.ax.set_xlim(keep[0]); self.ax.set_ylim(keep[1])
        self.fig.tight_layout()
        self.canvas.draw_idle()

    def on_done(self, summary):
        r = self.run
        self._running = None
        if self._popout is not None and self._popout.isVisible():
            if summary.stopped_early and summary.coverage >= 99.95:
                tail = "  ·  data ends at %.2f s (markers gone — fracture)" % summary.lost_at_t
            elif summary.stopped_early:
                tail = "  ·  MARKER LOST at %.2f s" % summary.lost_at_t
            else:
                tail = ""
            self._popout.status.setText("finished — %d frames, %.1f %% tracked%s"
                                        % (summary.n, summary.coverage, tail))
            gen = self._popout_gen
            QTimer.singleShot(3000, lambda: self._popout_autoclose(gen))
        if r is not None and any(p[4] == "transverse" for p in r.extra_pairs):
            # FW1's maths, offline: nu, area change and true stress from the width pair. The
            # note is printed VERBATIM - it is the honesty line that says when the width change
            # is sub-pixel and the numbers are noise wearing units.
            r.poisson_rows, r.poisson_note = PP.poisson_true_stress(
                summary, self.area.value(), comp=r.companion)
            self.log.emit("[PostProc] %s" % r.poisson_note)
            got = [p for p in (r.poisson_rows or []) if p and p.get("nu") is not None]
            if got:
                med_nu = sorted(p["nu"] for p in got)[len(got) // 2]
                line = "[PostProc] Poisson (median where defined): %.3f" % med_nu
                st = [p for p in got if p.get("sigma_true") is not None]
                if st:
                    pk = max(st, key=lambda p: p["sigma_true"])
                    line += ("   ·   true stress peak %.2f MPa vs %.2f engineering "
                             "(area %.2f -> %.2f mm2)"
                             % (pk["sigma_true"], pk["sigma_eng"],
                                self.area.value(), pk["area_mm2"]))
                self.log.emit(line)
        if r is not None:
            # An attached load channel says where the specimen was actually preloaded, and the
            # noise/rate window is anchored there instead of at the reference frame. Done here
            # rather than in the worker because it needs the companion, which belongs to the run.
            if r.companion is not None and summary.rows:
                try:
                    e0, note = PP.preload_strain_zero(
                        [x for x in summary.rows if x.ok], r.companion)
                    if note:
                        summary.strain_zero = e0 if e0 else None
                        summary.strain_zero_note = note
                        self.log.emit("[PostProc] %s" % note)
                except Exception as e:                       # never lose a finished run to this
                    self.log.emit("[PostProc] could not anchor the noise window: %s" % e)
            r.summary = summary
        self._redraw_plot()
        # The FRAME is the last one analysed — on a fracture run that is the broken specimen, and
        # it is the picture worth ending on. The BOXES are from the last frame that actually
        # tracked, because after a fracture there is no honest position to draw. The preview is
        # throttled, so the last frame PAINTED is not the last frame ANALYSED; read it explicitly.
        if summary.rows and r is not None:
            end = summary.rows[-1]
            pos = next((x for x in reversed(summary.rows) if x.ok), end)
            g = PP.read_frame(r.path, end.idx)
            if g is not None:
                self.view.play(g, pos.a, pos.b, self.boxHalf.value())
                self._markers = []      # tracked positions, not detections to snap to
                self._markers_frame = None
                self.view.set_markers([])
        self.stopBtn.setEnabled(False)
        self.playPauseBtn.setEnabled(bool(r))
        self.runBtn.setEnabled(bool(r and r.ready))
        peak = (r.peak if r else 0.0) * 100
        msg = ("%s — %d frames, %d tracked (%.1f %%), %d re-seed(s). Px₀ %.2f px, peak strain "
               "%.3f %%." % (r.label if r else "?", summary.n, summary.tracked, summary.coverage,
                             summary.reseeds, summary.l0_px, peak))
        # The status line stays factual and one line long. A lost marker is worth interrupting for,
        # so it goes to a dialog; the durable record of it is the table, the CSV and the report,
        # which is where anyone looks after the run rather than during it.
        self.status.setStyleSheet("color:%s;" % self._status_fg())
        self.status.setText(msg)
        self.log.emit("[PostProc] " + msg)
        note = None
        if summary.stopped_early:
            note = ("Tracking stopped at %.2f s (frame %d), and the plot ends at %.2f s.\n\n"
                    "On a fracture test this is normally the fracture itself. Everything plotted "
                    "before that point tracked cleanly."
                    % (summary.lost_at_t, summary.lost_at_frame,
                       summary.data_ends_t if summary.data_ends_t is not None else 0.0))
        elif summary.tracked < summary.n:
            note = ("%d of %d frames had no match.\n\n\"Stop when the markers are lost\" is off, "
                    "so the run carried on to the end of the video and the curve is BROKEN where "
                    "those frames are — it is not bridged across them."
                    % (summary.n - summary.tracked, summary.n))
        if note:
            self.log.emit("[PostProc] %s — %s" % (r.label if r else "?",
                                                  " ".join(note.split())))
            self._report_loss(r.label if r else "?", note)
        if summary.coverage < 90:
            self.log.emit("[PostProc] coverage below 90 % — try a larger box, a wider search "
                          "window, or a lower minimum correlation.")
        self._refresh_list()
        self._refresh_table()
        # Back to back: the next queued video starts as soon as this one is drawn.
        if self._queue:
            self._next_in_queue()
        elif self._losses:
            # The sweep has finished; report everything it ran into, in one dialog.
            last = self._losses.pop()
            self._report_loss(*last)

    def _report_loss(self, label, note):
        """Tell the operator a run lost its markers — once, and never mid-sweep.

        During a Run-all sweep a modal dialog between every pair of videos would turn an unattended
        batch into a babysitting job, so losses are collected and reported together when the sweep
        finishes.
        """
        if self._queue:
            self._losses.append((label, note))
            return
        pending = self._losses + [(label, note)]
        self._losses = []
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        if len(pending) == 1:
            box.setWindowTitle("Markers lost — %s" % pending[0][0])
            box.setText("<b>%s</b>" % pending[0][0])
            box.setInformativeText(pending[0][1])
        else:
            box.setWindowTitle("Markers lost in %d of the runs" % len(pending))
            box.setText("<b>%d runs did not reach the end of their video.</b>" % len(pending))
            box.setInformativeText("\n\n".join("%s — %s" % (lab, " ".join(n.split()))
                                                for lab, n in pending))
        box.setDetailedText("The full per-run figures are in the results table, and in the CSV and "
                            "report if you export them: look for the 'Tracking ended' row.")
        box.exec()

    def _popout_autoclose(self, gen):
        """Hide the tracking pop-out 3 s after ITS run ended — never someone else's.

        Run-all starts the next video inside that window, so the close is tied to a generation
        counter and stands down if a newer run owns the pop-out or a worker is live."""
        if (self._popout is not None and gen == getattr(self, "_popout_gen", 0)
                and not (self.worker and self.worker.isRunning())):
            self._popout.hide()

    def _popout_failed(self, err):
        if self._popout is not None and self._popout.isVisible():
            self._popout.status.setText("FAILED — %s" % err)
            gen = getattr(self, "_popout_gen", 0)
            QTimer.singleShot(3000, lambda: self._popout_autoclose(gen))

    def on_failed(self, err):
        self._popout_failed(err)
        self._running = None
        self.runBtn.setEnabled(True); self.stopBtn.setEnabled(False)
        if self._queue:
            self.log.emit("[PostProc] skipping to the next queued video after the failure")
            self._next_in_queue()
            return
        self.status.setText("failed: " + err)
        self.log.emit("[PostProc] FAILED: " + err)
        QMessageBox.warning(self, "Analysis failed", err)

    def on_export(self):
        """Write one CSV per completed run, into a folder the operator picks.

        One file each rather than a merged table: the runs have different frame rates, different
        L0 and different lengths, so a single sheet would need padding or resampling — and a
        resampled export is a derived product masquerading as data.
        """
        done = [r for r in self.runs if r.done]
        if not done:
            return
        folder = QFileDialog.getExistingDirectory(self, "Choose a folder for the CSV files")
        if not folder:
            return
        written = []
        for r in done:
            cfg = PP.Settings(gauge_mm=r.gauge_mm, gauge_confirmed=r.gauge_confirmed,
                              gauge_src=r.gauge_src,
                              box_half=r.box_half, search=r.search,
                              min_corr=r.min_corr, ref_frame=r.ref_frame, ref_image=r.ref_image,
                              fps=r.fps, step=r.step, refine=r.refine)
            safe = "".join(c if c.isalnum() or c in "-_ " else "_" for c in r.label).strip()
            out = os.path.join(folder, "%s_dic_postproc.csv" % (safe or "run"))
            try:
                PP.to_csv(r.summary, out, source_video=r.path, cfg=cfg,
                          poisson_rows=getattr(r, "poisson_rows", None))
                written.append(os.path.basename(out))
            except Exception as e:
                QMessageBox.warning(self, "Could not write a CSV", "%s\n\n%s" % (out, e))
        if written:
            self.log.emit("[PostProc] wrote %d file(s) to %s: %s"
                          % (len(written), folder, ", ".join(written)))
