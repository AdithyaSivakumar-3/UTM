"""The Noise capture setup dialog.

Its own module for two reasons: main.py is already long enough that adding a dialog to it costs
more than it saves, and everything here is pure presentation — it is handed the state it displays
and hands back a duration, so it can be exercised without a rig.

It carries the preload warning as well as the duration. Two separate pop-ups (a warning, then a
duration prompt) would ask the operator to acknowledge the same decision twice, and the warning
matters most at the moment the duration is being chosen: the whole reason to preload first is that
the noise being measured should be the noise of the state the specimen will be pulled from.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton,
                             QFrame, QDialogButtonBox)

# The window a figure came from has to travel with it: on this rig the DIC noise floor GROWS with
# observation time, about 12 ue over 40 s against 26 ue over 900 s. A 30 s number applied to a
# 900 s creep test understates the noise by roughly half, so the dialog says so where the choice
# is actually made rather than in a tooltip nobody opens.
PRESETS = [("30 s", 30), ("60 s", 60), ("2 min", 120), ("5 min", 300), ("15 min", 900)]


class NoiseCaptureDialog(QDialog):
    """Choose the window, see the state the capture will run in, and start it.

    Returns via .duration() and .exec(); Accepted means go.
    """

    def __init__(self, parent, duration_s, preload_ok, preload_note, dic_live, specimen=""):
        super().__init__(parent)
        self.setWindowTitle("Noise capture")
        self.setMinimumWidth(560)
        self._ok = bool(preload_ok)

        v = QVBoxLayout(self)
        v.setSpacing(10)

        head = QLabel("Record the machine AT REST, to measure what the instrument reports when "
                      "nothing is happening.")
        head.setWordWrap(True)
        head.setStyleSheet("font-weight: bold;")
        v.addWidget(head)

        why = QLabel(
            "It gives three numbers per channel. The OFFSET and the DRIFT are systematic and can be "
            "corrected out of a later run. The SD is what remains once that straight line is "
            "removed — it does not subtract, and it is the measurement uncertainty to quote.")
        why.setWordWrap(True)
        why.setStyleSheet("color: #8a8f98;")
        v.addWidget(why)

        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine)
        v.addWidget(line)

        # ---- duration
        row = QHBoxLayout()
        row.addWidget(QLabel("Record for"))
        self.spin = QSpinBox()
        self.spin.setRange(5, 3600)
        self.spin.setValue(int(duration_s))
        self.spin.setSuffix(" s")
        self.spin.setFixedWidth(90)
        row.addWidget(self.spin)
        for label, secs in PRESETS:
            b = QPushButton(label)
            b.setFixedWidth(58)
            b.setToolTip("Set the window to %d s." % secs)
            b.clicked.connect(lambda _c, n=secs: self.spin.setValue(n))
            row.addWidget(b)
        row.addStretch()
        v.addLayout(row)

        warn_time = QLabel(
            "Match this to the test you mean to apply it to. This rig's DIC noise floor GROWS with "
            "observation time — about 12 µε over 40 s against 26 µε over 900 s — so a short capture "
            "understates the noise on a long test. The window is written into the saved file.")
        warn_time.setWordWrap(True)
        warn_time.setStyleSheet("color: #8a8f98; font-size: 11px;")
        v.addWidget(warn_time)

        line2 = QFrame(); line2.setFrameShape(QFrame.Shape.HLine)
        v.addWidget(line2)

        # ---- the state this will run in
        if specimen:
            sp = QLabel("Specimen:  %s" % specimen)
            sp.setWordWrap(True)
            sp.setStyleSheet("color: #8a8f98;")
            v.addWidget(sp)

        if preload_ok:
            pl = QLabel("✔  Preload applied — %s" % preload_note)
            pl.setStyleSheet("color: #2f9e44; font-weight: bold;")
        else:
            pl = QLabel(
                "⚠  USE NOISE CAPTURE AFTER THE PRELOAD IS APPLIED.\n"
                "Right now %s.\n\n"
                "It matters because the point of this measurement is the noise the machine shows in "
                "the state the SPECIMEN will be pulled from. Unseated grips settle, and that "
                "settling is recorded as drift that is not there during the run.\n\n"
                "You can measure anyway — a bare-machine or unloaded baseline is a legitimate thing "
                "to want, and the override is recorded in the saved file." % preload_note)
            pl.setStyleSheet("color: #e8a80c; font-weight: bold;")
        pl.setWordWrap(True)
        v.addWidget(pl)

        if not dic_live:
            dic = QLabel("⚠  DIC is not tracking two markers, so strain noise cannot be measured. "
                         "The LOAD channel will be recorded as normal, and the DIC columns will be "
                         "left EMPTY in the file rather than written as zero.")
            dic.setWordWrap(True)
            dic.setStyleSheet("color: #e8a80c;")
            v.addWidget(dic)

        v.addStretch()

        # The affirmative button says what it will DO, so an override cannot be given absent-mindedly.
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        go = QPushButton("Start recording" if preload_ok else "Measure anyway")
        if not preload_ok:
            go.setToolTip("Record without a detected preload. This is written into the saved file.")
        bb.addButton(go, QDialogButtonBox.ButtonRole.AcceptRole)
        # Cancel is the default when there is no preload: an override should be deliberate.
        bb.button(QDialogButtonBox.StandardButton.Cancel).setDefault(not preload_ok)
        go.setDefault(preload_ok)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        v.addWidget(bb)

    def duration(self):
        return int(self.spin.value())
