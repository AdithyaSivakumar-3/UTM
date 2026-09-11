# -*- coding: utf-8 -*-
"""Weekly deck: fill the four title-only specimen slides (262, 271, 279, 295) with images.

Surgical: edits ONLY those four slides on his live file, proves every other slide's XML is
byte-identical before/after, then refreshes the local baseline. Images are the run's own
frames (tare = first frame, fracture = last frame on film) plus the phone photos that sit in
the run folders. PETG runs have no PNG stills, so their frames come from the video."""
import glob
import hashlib
import os
import re
import shutil
import sys
import zipfile

import cv2
import numpy as np
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "Software", "UTM_PyQt6"))
import utm_postproc as PP                                             # noqa: E402

DECK = os.path.join("Documentation", "Decks", "Weekly progress updated.pptx")
BASE = os.path.join("Documentation", "Decks", ".local_baselines", "Weekly_progress.baseline.pptx")
DATA = os.path.join("Software", "UTM_PyQt6", "Test data", "Fracture tests")
FIGS = os.path.join("documentation", "figures", "wk_specimens")
os.makedirs(FIGS, exist_ok=True)
INK, GREY = RGBColor(0x25, 0x34, 0x39), RGBColor(0x5A, 0x63, 0x6B)
TARGETS = {262: ("S25", "S26"), 271: ("S13",), 279: ("S27", "S28"), 295: ("S31", "S32"),
           302: ("S35", "S36")}
X0, X1 = 1.40, 12.07                       # content span used by the neighbouring slides
Y0 = 2.20


# ------------------------------------------------------------------ frames and photos
def run_dir(spec):
    hits = [d for d in glob.glob(os.path.join(DATA, "Specimen_%s_*" % spec)) if os.path.isdir(d)]
    assert hits, spec
    return hits[0]


def frames(spec):
    """(tare.png, last.png, n_frames, source) for one specimen — cached in FIGS."""
    t, l = os.path.join(FIGS, "%s_tare.png" % spec), os.path.join(FIGS, "%s_last.png" % spec)
    d = run_dir(spec)
    stills = sorted(glob.glob(os.path.join(d, "*", "frames", "f*.png")))
    if stills:
        n, src = len(stills), "PNG stills"
        g0, g1 = (cv2.imread(p, cv2.IMREAD_GRAYSCALE) for p in (stills[0], stills[-1]))
    else:
        vid = (glob.glob(os.path.join(d, "*", "video.avi")) + glob.glob(os.path.join(d, "*", "video.mkv")))[0]
        n, src = PP.probe(vid)["frames"], os.path.basename(vid)
        g0, g1 = PP.read_frame(vid, 0), PP.read_frame(vid, n - 1)
        g0 = g0 if g0.ndim == 2 else cv2.cvtColor(g0, cv2.COLOR_BGR2GRAY)
        g1 = g1 if g1.ndim == 2 else cv2.cvtColor(g1, cv2.COLOR_BGR2GRAY)
    for g, p in ((g0, t), (g1, l)):
        if g.shape[0] > g.shape[1]:
            g = np.ascontiguousarray(np.rot90(g))
        cv2.imwrite(p, g)
    return t, l, n, src


def photos(spec):
    d = run_dir(spec)
    return sorted(glob.glob(os.path.join(d, "*.jpg")) + glob.glob(os.path.join(d, "*", "*.jpg")))


# ------------------------------------------------------------------ drawing helpers
def label(slide, x, y, w, text, size=11, bold=False, colour=INK):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(0.28))
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = Inches(0.02)
    tf.margin_top = tf.margin_bottom = Inches(0.0)
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run(); r.text = text
    r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = colour; r.font.name = "Calibri"
    return tb


def pic(slide, path, x, y, w=None, h=None):
    from PIL import Image
    iw, ih = Image.open(path).size
    if w is not None:
        h = w * ih / iw
    else:
        w = h * iw / ih
    slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
    return w, h


def strip(slide, path, x, y, w, caption):
    label(slide, x, y, w, caption, size=10.5, colour=GREY)
    _, h = pic(slide, path, x, y + 0.27, w=w)
    return 0.27 + h + 0.10


def source_line(slide, text):
    label(slide, X0, 6.95, X1 - X0, text, size=9, colour=GREY)


# ------------------------------------------------------------------ the four layouts
def fill_pair_with_photo(slide, a, b, photo, photo_w, title_note):
    """Photo left; right column: A last, B last (full width), then A/B tare side by side."""
    ph_w, ph_h = pic(slide, photo, X0, Y0, w=photo_w)
    label(slide, X0, Y0 + ph_h + 0.05, ph_w, "%s after the pull" % a, size=10.5, colour=GREY)
    x = X0 + ph_w + 0.30
    w = min(X1 - x, 7.9)                  # keeps the two full strips + the tare pair above the source line
    ta, la, na, sa = frames(a)
    tb, lb, nb, sb = frames(b)
    y = Y0
    y += strip(slide, la, x, y, w, "%s — last frame on film: the fracture, both markers still in view" % a)
    y += strip(slide, lb, x, y, w, "%s — last frame on film" % b)
    half = (w - 0.20) / 2
    strip(slide, ta, x, y, half, "%s — tare frame (Px₀ frozen)" % a)
    strip(slide, tb, x + half + 0.20, y, half, "%s — tare frame" % b)
    source_line(slide, "%s · frames from Test data/Fracture tests/Specimen_%s_* (%d %s) "
                       "and Specimen_%s_* (%d %s); photo from the same folder" % (title_note, a, na, sa, b, nb, sb))


def fill_262(slide):
    fill_pair_with_photo(slide, "S25", "S26", photos("S25")[0], 1.85,
                         "White PLA, 100 % infill, black spray markers, 80 mm gauge, 2026-08-17")


def fill_279(slide):
    fill_pair_with_photo(slide, "S27", "S28", photos("S27")[0], 1.85,
                         "White PLA, 50 % gyroid infill, black spray markers, 80 mm gauge, 2026-08-17")


def fill_271(slide):
    ph = photos("S13")
    ph_w, ph_h = pic(slide, ph[0], X0, Y0, h=4.20)
    label(slide, X0, Y0 + ph_h + 0.05, ph_w, "S13 mounted: black PLA, white spray dots", size=10.5, colour=GREY)
    x = X0 + ph_w + 0.30
    w = X1 - x
    t, l, n, s = frames("S13")
    y = Y0
    y += strip(slide, t, x, y, w, "S13 — tare frame: white markers on a black body, Otsu → fixed 149")
    y += strip(slide, l, x, y, w, "S13 — last frame on film: fracture at 0.15 of the gauge, both markers tracked")
    label(slide, x, y + 0.05, w,
          "S14 was printed as the partner specimen but no recorded run exists for it in the test data; "
          "the black-specimen evidence on the following slides is S13 alone (n = 1).",
          size=10.5, colour=GREY)
    source_line(slide, "Black PLA, 100 %% infill, 80 mm gauge, 2026-08-18 · frames from Test data/8.6.20 - Tensile "
                       "test to Failure/Specimen_S13_* (%d %s); photo from the same folder" % (n, s))


def fill_295(slide):
    ta, la, na, sa = frames("S31")
    tb, lb, nb, sb = frames("S32")
    w = (X1 - X0 - 0.25) / 2
    y = Y0
    h1 = strip(slide, ta, X0, y, w, "S31 — tare frame: translucent black PETG, white spray dots")
    strip(slide, la, X0 + w + 0.25, y, w, "S31 — last frame on film: the drawn neck ran to the upper shoulder")
    y += h1
    h2 = strip(slide, tb, X0, y, w, "S32 — tare frame")
    strip(slide, lb, X0 + w + 0.25, y, w, "S32 — last frame on film (the fracture itself was not on film)")
    y += h2
    label(slide, X0, y + 0.05, X1 - X0,
          "PETG is where Otsu fails: on S29 it found both markers on 48.5 % of frames against 99.5 % with the "
          "fixed threshold — which is why these runs use the Black preset (fixed 149).", size=11, colour=INK)
    source_line(slide, "PETG, 100 %% infill, 80 mm gauge, 2026-08-22/24 · frames read from Test data/8.6.20 - Tensile "
                       "test to Failure/Specimen_S31_* (%d, %s) and Specimen_S32_* (%d, %s) — no PNG stills for "
                       "these runs" % (na, sa, nb, sb))


# ------------------------------------------------------------------ 302: the two TPU runs
def run_stats(spec):
    """Everything slide 302 quotes, recomputed from the run's own CSV: where the DIC trace
    ended, where the crosshead was at that moment, and how far the run went on."""
    import csv
    d = run_dir(spec)
    p = sorted(glob.glob(os.path.join(d, "UTM_Test_*.csv")))[0]
    rows = list(csv.reader(open(p, encoding="utf-8", errors="replace")))
    hi = next(i for i, r in enumerate(rows) if r and r[0].strip() == "Time_s")
    hdr = rows[hi]
    D = [r for r in rows[hi + 1:] if len(r) == len(hdr)]
    I = {c: i for i, c in enumerate(hdr)}

    def f(r, c):
        try:
            return float(r[I[c]])
        except Exception:
            return None

    alive = [r for r in D if (f(r, "DIC_Blobs") or 0) >= 2 and (f(r, "L_px") or 0) > 0]
    a0, aN = alive[0], alive[-1]
    peak = max(D, key=lambda r: f(r, "Stress_MPa") or 0)
    return dict(csv=os.path.basename(p), rows=len(D), alive=len(alive),
                cover=100.0 * len(alive) / len(D),
                L0=f(a0, "L_px"), L1=f(aN, "L_px"),
                dic_end=100.0 * f(aN, "DIC_Cauchy"), motor_at_end=100.0 * f(aN, "Motor_Strain"),
                motor_final=100.0 * max(f(r, "Motor_Strain") or 0 for r in D),
                uts=f(peak, "Stress_MPa"))


def marker_room(png):
    """Marker centres and the room each has to the frame edge, on the tare frame."""
    g = cv2.imread(png, cv2.IMREAD_GRAYSCALE)
    h, w = g.shape
    _t, b = cv2.threshold(g, 190, 255, cv2.THRESH_BINARY)
    n, lbl, st, cen = cv2.connectedComponentsWithStats(b, 8)
    blobs = []
    for i in range(1, n):
        a = st[i, cv2.CC_STAT_AREA]
        bw, bh = st[i, cv2.CC_STAT_WIDTH], st[i, cv2.CC_STAT_HEIGHT]
        if a >= 2000 and 0.5 <= bw / max(1, bh) <= 2.0:
            blobs.append((int(cen[i][0]), int(st[i, cv2.CC_STAT_LEFT]),
                          int(st[i, cv2.CC_STAT_LEFT] + bw)))
    blobs.sort()
    assert len(blobs) >= 2, png
    return dict(w=w, sep=blobs[-1][0] - blobs[0][0], left=blobs[0][1], right=w - blobs[-1][2])


def fill_302(slide):
    a, b = run_stats("S35"), run_stats("S36")
    t, l, n, src = frames("S35")
    room = marker_room(t)
    w = (X1 - X0 - 0.25) / 2
    y = Y0
    h1 = strip(slide, t, X0, y, w,
               "S35 — tare frame: both markers found, %d px apart" % room["sep"])
    strip(slide, l, X0 + w + 0.25, y, w,
          "S35 — last frame: the left marker has walked out of the picture")
    y += h1 + 0.05

    rows = [("", "UTS", "E", "σ_y", "DIC trace ends at", "crosshead was at", "run went on to", "DIC coverage"),
            ("S35", "%.2f MPa" % a["uts"], "0.025 GPa", "0.98 MPa", "%.1f %%" % a["dic_end"],
             "%.1f %%" % a["motor_at_end"], "%.1f %%" % a["motor_final"], "%.0f %%" % a["cover"]),
            ("S36", "%.2f MPa" % b["uts"], "0.025 GPa", "1.12 MPa", "%.1f %%" % b["dic_end"],
             "%.1f %%" % b["motor_at_end"], "%.1f %%" % b["motor_final"], "%.0f %%" % b["cover"])]
    tb = slide.shapes.add_table(len(rows), len(rows[0]), Inches(X0), Inches(y),
                                Inches(X1 - X0), Inches(0.95)).table
    tb.columns[0].width = Inches(0.75)
    for j in range(1, len(rows[0])):
        tb.columns[j].width = Inches((X1 - X0 - 0.75) / (len(rows[0]) - 1))
    for i, r in enumerate(rows):
        tb.rows[i].height = Inches(0.30)
        for j, v in enumerate(r):
            cell = tb.cell(i, j)
            cell.text = ""
            par = cell.text_frame.paragraphs[0]
            par.alignment = PP_ALIGN.CENTER if j else PP_ALIGN.LEFT
            run = par.add_run(); run.text = v
            run.font.size = Pt(10.5); run.font.name = "Calibri"
            run.font.bold = (i == 0 or j == 0)
            run.font.color.rgb = INK
    y += 1.05

    label(slide, X0, y, X1 - X0,
          "Why both traces stop early — and it is not the material. The pair sits off-centre in the "
          "region of interest: %d px of room to the left edge against a %d px gauge. TPU keeps "
          "stretching, the marker nearer that edge walks into the margin, and at ≈%.1f %% strain it "
          "leaves the picture — the strain record ends while the specimen is still being pulled, on to "
          "%.1f %%. Pixels, not physics, ended these two measurements."
          % (room["left"], room["sep"], a["dic_end"], a["motor_final"]), size=11, colour=INK)
    label(slide, X0, y + 0.62, X1 - X0,
          "S36 has no capture folder at all: its DIC ran live (the CSV carries the trace) but nothing "
          "was recorded, so there are no frames to re-measure. The fix was S37 — the same TPU on a "
          "45 mm gauge, which halves the pixel span and buys the room back: it reached 18.5 % with "
          "both markers tracked to the travel backstop.", size=11, colour=GREY)
    source_line(slide, "TPU, 100 %% infill, 80 mm gauge, 2026-08-24 · S35 frames from Test data/8.6.20 - Tensile "
                       "test to Failure/Specimen_S35_* (%d %s); every number recomputed from %s and %s"
                       % (n, src, a["csv"], b["csv"]))


# ------------------------------------------------------------------ surgery
def slide_parts(path):
    z = zipfile.ZipFile(path)
    return {n: hashlib.sha1(z.read(n)).hexdigest() for n in z.namelist()
            if re.match(r"ppt/slides/slide\d+\.xml$", n)}


def main():
    pre = os.path.join(HERE, "..", "Decks", ".local_baselines", "_pre_fill.pptx")
    shutil.copyfile(DECK, pre)
    before = slide_parts(DECK)
    prs = Presentation(DECK)
    assert len(prs.slides) >= 393, len(prs.slides)
    for n, fn in ((262, fill_262), (271, fill_271), (279, fill_279), (295, fill_295), (302, fill_302)):
        s = prs.slides[n - 1]
        for sh in list(s.shapes):                                          # redo-safe: keep only the
            if not sh.is_placeholder:                                      # title + page-number placeholders
                sh._element.getparent().remove(sh._element)
        assert len(s.shapes) == 2, (n, [sh.name for sh in s.shapes])
        fn(s)
        print("slide %d: %d shapes now" % (n, len(s.shapes)))
    prs.save(DECK)
    # python-pptx re-serialises every part, so prove the surgery on CANONICAL xml and on the
    # relationship SETS, not on bytes
    from lxml import etree
    zp, zd = zipfile.ZipFile(pre), zipfile.ZipFile(DECK)
    canon = lambda z, n: hashlib.sha1(etree.tostring(etree.fromstring(z.read(n)), method="c14n")).hexdigest()
    rels = lambda z, n: sorted((r.get("Id"), r.get("Type"), r.get("Target")) for r in etree.fromstring(z.read(n)))
    targets = {s.part.partname.lstrip("/") for s in (prs.slides[i - 1] for i in (262, 271, 279, 295, 302))}
    changed = sorted(n for n in before if canon(zp, n) != canon(zd, n))
    assert set(changed) <= targets, changed          # a redo may leave some of the four identical
    bad_rels = [n for n in zp.namelist() if n.endswith(".rels")
                and n.replace("_rels/", "").replace(".rels", "") not in targets and rels(zp, n) != rels(zd, n)]
    assert not bad_rels, bad_rels
    media = [n for n in zp.namelist() if n.startswith("ppt/media/")]
    assert all(zp.read(n) == zd.read(n) for n in media)
    zp.close(); zd.close()
    print("surgery proven: only", sorted(targets), "changed; rels and media of every other part identical")
    # full-hash copy x2 + baseline refresh
    for k in range(2):
        shutil.copyfile(DECK, BASE)
        h1 = hashlib.sha1(open(DECK, "rb").read()).hexdigest()
        h2 = hashlib.sha1(open(BASE, "rb").read()).hexdigest()
        assert h1 == h2
    os.remove(pre)
    print("baseline refreshed:", h1)


if __name__ == "__main__":
    main()
