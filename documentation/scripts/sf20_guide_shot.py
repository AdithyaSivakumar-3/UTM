"""Render the post-processing guide window to documentation/figures/sf20_guide.png.

A real screenshot of the real widget, produced by driving it rather than by cropping a photograph
of a screen — so it can be regenerated after the guide changes and cannot go stale unnoticed.

Deliberately NOT run under QT_QPA_PLATFORM=offscreen: the offscreen platform has no fonts on this
machine and every glyph renders as a tofu box. It needs the ordinary platform plugin, which means
this script is run by hand rather than from the deck build.

    python documentation/scripts/sf20_guide_shot.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
FIGS = os.path.abspath(os.path.join(HERE, "..", "figures"))
sys.path.insert(0, os.path.join(REPO, "Software", "UTM_PyQt6"))

if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
    raise SystemExit("run this WITHOUT QT_QPA_PLATFORM=offscreen — offscreen has no fonts here "
                     "and every glyph comes out as a box")

from PyQt6.QtWidgets import QApplication                               # noqa: E402
from utm_postdlg import GuideDialog, PostProcTab                       # noqa: E402

# The app's own dark styling, close enough that the figure matches what the operator sees.
QSS = """
QWidget       { background:#1c2128; color:#c9d1d9; font-family:'Segoe UI'; }
QPushButton   { background:#2d333b; border:1px solid #444c56; border-radius:4px; padding:5px 12px; }
QPushButton:disabled { color:#6b7280; border-color:#333; }
QCheckBox     { color:#c9d1d9; }
QScrollArea   { border:none; }
"""


def main(step=3):
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)

    # A state where the first few steps are done, so the figure shows the ticks, the current step
    # and the dimmed remainder all at once — an all-pending window would show none of that.
    done = [True, True, True, False, False, False, False]
    dlg = GuideDialog(PostProcTab.GUIDE_STEPS, lambda: done)
    dlg.resize(880, 520)
    dlg.show()
    app.processEvents()
    dlg.followChk.setChecked(False)
    dlg.list.setCurrentRow(step)
    app.processEvents()

    out = os.path.join(FIGS, "sf20_guide.png")
    dlg.grab().save(out)
    print("wrote %s  (showing step %d of %d)"
          % (os.path.relpath(out, REPO), step + 1, len(PostProcTab.GUIDE_STEPS)))


if __name__ == "__main__":
    main()
