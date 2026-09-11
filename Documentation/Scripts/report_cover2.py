# -*- coding: utf-8 -*-
"""Report cover picture: the rig photo beside a DARK-MODE PLA stress–strain plot on top;
below them the specimen pack — the thresholded gauge strip (what the camera decides, at true
aspect) over the live Px₀ overlay from the application (what the operator sees). The curve is
read from the CSV through trio_plots.curve, so nothing on it is typed in."""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import trio_plots as T                                    # noqa: E402

FIGS = os.path.join(HERE, "..", "figures")
TAN = "#B29E84"
BG, FG, MUTED, LINE = "#0E1417", "#E8EDEF", "#9AA7AD", "#4FA3E3"
plt.rcParams["font.family"] = "Segoe UI"

W, GAP = 2400, 26


def fit_w(im, w):
    return im.resize((w, int(round(im.height * w / im.width))), Image.LANCZOS)


# ---- rig photo, left: cropped to the machine (the original has half a room around it), so
# the rig itself fills its box instead of the office floor and the cabinet
rig = Image.open(os.path.join(FIGS, "UTM rig_12-08-26.jpg")).convert("RGB")
rig = rig.crop((150, 0, 1250, 1980))
H2 = 1250
rig = rig.resize((int(round(rig.width * H2 / rig.height)), H2), Image.LANCZOS)

# ---- PLA curve, right, dark mode
cw = W - rig.width - GAP
fig, ax = plt.subplots(figsize=(cw / 200, H2 / 200))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
e, s, a = T.curve("S25")
ax.plot(e, s, color=LINE, lw=3.0)
i = int(s.argmax())
ax.plot([e[i]], [s[i]], "o", color=LINE, ms=8, mec=FG, mew=1.2)
ax.annotate("UTS %.1f MPa" % s[i], xy=(e[i], s[i]), xytext=(e[i] + 0.55, s[i] - 5.5),
            fontsize=12, color=FG, arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
ax.set_xlabel("DIC gauge strain (%)", fontsize=12.5, color=FG)
ax.set_ylabel("engineering stress (MPa)", fontsize=12.5, color=FG)
ax.set_title("PLA specimen S25 — strain from the camera, stress from the load cell",
             fontsize=11.5, color=MUTED, loc="left", pad=10)
ax.tick_params(labelsize=10.5, colors=MUTED)
ax.grid(color="#243038", lw=0.9)
ax.set_axisbelow(True)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
for sp in ("left", "bottom"):
    ax.spines[sp].set_color("#3A4750")
ax.set_xlim(left=0)
ax.set_ylim(bottom=0)
fig.tight_layout(pad=0.7)
tmp = os.path.join(FIGS, "_cover_curve.png")
fig.savefig(tmp, dpi=200, facecolor=BG)
plt.close(fig)
curve = Image.open(tmp).convert("RGB").resize((cw, H2), Image.LANCZOS)
os.remove(tmp)

# ---- the app's live Px₀ overlay: just the camera feed, with the window chrome above it
# (group title, button row, status line) and the panel margins cropped away
live = Image.open(os.path.join(FIGS, "CalibratePxo_live marker.png")).convert("RGB")
live = fit_w(live.crop((128, 88, 1226, 284)), W)      # the camera image only, measured edges

# ---- compose
H = H2 + GAP + live.height
out = Image.new("RGB", (W, H), "white")
out.paste(rig, (0, 0))
out.paste(curve, (rig.width + GAP, 0))
y = H2 + GAP
out.paste(Image.new("RGB", (W, 6), TAN), (0, y - GAP // 2 - 3))
out.paste(live, (0, y))
out.save(os.path.join(FIGS, "report_cover2.png"))
print("report_cover2.png %dx%d" % out.size)
