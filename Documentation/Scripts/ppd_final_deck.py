# -*- coding: utf-8 -*-
"""The PPD final presentation — a fresh deck in the thesis-defence template language.

NOT part of the V6a build. This deck is presented, not archived: 19 physical pages, low text
density, one idea per page, in the palette of the reference template he supplied
("Gray and White Simple Thesis Defense", Canva):

    cream F6F4F1 · ink 253439 · tan B29E84 · sage 7C898B

with its motifs — the left rail (dark block over a long sage bar), the tri-square corner mark,
the tricolour underline, vertical edge text — and the JU logo lifted from the Weekly deck's own
master. Lato is not installed on this machine, so Segoe UI Light / Segoe UI stand in.

Slide 5 is TWO pages on purpose: python-pptx cannot author animations, so "all 20 visible, then
three highlighted and the rest greyed on click" is done as consecutive slides — the click IS the
transition.

The three demo videos are re-encoded timelapses (15 s each) of real pulls, embedded in the file;
they regenerate from Test data if the cached MP4s are missing. Numbers on the validation pages
are the ones mot2_compare / mot2_pp print today, not remembered ones.

Build: python documentation/scripts/ppd_final_deck.py
Writes to the scratchpad first (OneDrive corrupts freshly written media parts), then the caller
copies into documentation/decks/.
"""
import os
import subprocess
import sys

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FIGS = os.path.join(ROOT, "documentation", "figures")
SP = os.environ.get("PPD_SCRATCH", os.path.join(HERE, "_ppd_build"))
MEDIA = os.path.join(SP, "media")
OUT = os.path.join(SP, "PPD_Final_Presentation.pptx")

# ---- palette (measured from the reference pptx) and type
CREAM = RGBColor(0xF6, 0xF4, 0xF1)
INK = RGBColor(0x25, 0x34, 0x39)
TAN = RGBColor(0xB2, 0x9E, 0x84)
SAGE = RGBColor(0x7C, 0x89, 0x8B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FAINT = RGBColor(0xDE, 0xDA, 0xD2)          # greyed-out tiles, hairlines on cream
DISP, BODY, SEMI = "Segoe UI Light", "Segoe UI", "Segoe UI Semibold"

EW, EH = 13.333, 7.5

prs = Presentation()
prs.slide_width = Inches(EW)
prs.slide_height = Inches(EH)
BLANK = prs.slide_layouts[6]


# ================================================================ drawing vocabulary
def rect(s, x, y, w, h, fill, line=None, lw=1.0):
    r = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    r.fill.solid(); r.fill.fore_color.rgb = fill
    if line is None:
        r.line.fill.background()
    else:
        r.line.color.rgb = line; r.line.width = Pt(lw)
    r.shadow.inherit = False
    return r


def text(s, x, y, w, h, runs, *, fs=12, font=BODY, colour=INK, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, spacing=1.0, wrap=True):
    """One box, many paragraphs. `runs` is a string, or a list of paragraphs, each a string or a
    list of (txt, {font/fs/colour/bold/italic}) run tuples."""
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    paras = [runs] if isinstance(runs, str) else runs
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        for run in ([(para, {})] if isinstance(para, str) else para):
            t, kw = run
            r = p.add_run(); r.text = t
            r.font.name = kw.get("font", font)
            r.font.size = Pt(kw.get("fs", fs))
            r.font.bold = kw.get("bold", bold)
            r.font.italic = kw.get("italic", False)
            r.font.color.rgb = kw.get("colour", colour)
            if kw.get("url"):
                r.hyperlink.address = kw["url"]
    return box


def bullets(s, x, y, w, h, items, *, fs=11.5, gap=6, colour=INK):
    """Tan square markers, ink text. An item may be (text, dict-overrides)."""
    paras = []
    for it in items:
        t, kw = it if isinstance(it, tuple) else (it, {})
        paras.append([("▪  ", {"colour": TAN, "fs": kw.get("fs", fs), "bold": True}),
                      (t, {"fs": kw.get("fs", fs), "colour": kw.get("colour", colour),
                           "bold": kw.get("bold", False), "font": kw.get("font", BODY)})])
    box = text(s, x, y, w, h, paras, fs=fs, spacing=1.04)
    for p in box.text_frame.paragraphs:
        p.space_after = Pt(gap)
    return box


def card(s, x, y, w, h, *, fill=WHITE, line=FAINT, lw=1.0):
    return rect(s, x, y, w, h, fill, line=line, lw=lw)


def pic(s, path, x, y, maxw, maxh, *, frame=True, pad=0.10):
    """Image fitted and centred inside a white card."""
    iw, ih = Image.open(path).size
    availw, availh = maxw - 2 * pad, maxh - 2 * pad
    sc = min(availw / iw, availh / ih)
    w, h = iw * sc, ih * sc
    if frame:
        card(s, x, y, maxw, maxh)
    s.shapes.add_picture(path, Inches(x + (maxw - w) / 2), Inches(y + (maxh - h) / 2),
                         width=Inches(w))
    return h


def chip(s, x, y, txt, *, fill=INK, fg=WHITE, fs=9.5, w=None, h=0.30):
    w = w or (0.16 + 0.092 * len(txt))
    c = rect(s, x, y, w, h, fill)
    tf = c.text_frame
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = False
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = txt
    r.font.name = SEMI; r.font.size = Pt(fs); r.font.color.rgb = fg
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    return c


# ---- the template furniture
def base(s, *, rail=True):
    rect(s, 0, 0, EW, EH, CREAM)
    if rail:
        rect(s, 0, 0, 0.16, 1.02, INK)
        rect(s, 0, 1.14, 0.16, EH - 1.14, SAGE)


def ju(s, x=0.46, y=0.28, hgt=0.44):
    # the real JU lockup (mark + wordmark), lifted from his own deck's layout media and
    # tinted to this template's ink - it carries its own transparency, nothing to compose
    s.shapes.add_picture(os.path.join(FIGS, "ju_mark.png"), Inches(x), Inches(y),
                         height=Inches(hgt))


def squares(s, x=12.32, y=0.38, a=0.13, gap=0.115):
    for i, c in enumerate((INK, TAN, SAGE)):
        rect(s, x + i * (a + gap), y, a, a, c)


def vside(s, txt):
    box = text(s, 12.70, 2.6, 3.0, 0.34, txt, fs=8.5, font=SEMI, colour=SAGE,
               align=PP_ALIGN.CENTER, wrap=False)
    box.rotation = 270
    box.left, box.top = Inches(11.62), Inches(3.62)   # rotate about centre, then place on the edge


def tricolour(s, x, y, w=3.6, h=0.055):
    rect(s, x, y, w * 0.26, h, INK)
    rect(s, x + w * 0.26, y, w * 0.13, h, TAN)
    rect(s, x + w * 0.39, y, w * 0.61, h, SAGE)


_PAGE = [0]


def pageno(s):
    _PAGE[0] += 1
    text(s, 12.55, 7.08, 0.62, 0.3, "%02d" % _PAGE[0], fs=10, font=SEMI, colour=SAGE,
         align=PP_ALIGN.RIGHT)


def header(s, kicker, title_txt, *, tfs=29):
    text(s, 0.85, 0.86, 11.4, 0.30, kicker.upper(), fs=10.5, font=SEMI, colour=TAN)
    text(s, 0.83, 1.10, 11.9, 0.62, title_txt, fs=tfs, font=DISP, colour=INK)
    tricolour(s, 0.85, 1.74)


def content_slide(kicker, title_txt, side=None, *, tfs=29):
    s = prs.slides.add_slide(BLANK)
    base(s)
    ju(s)
    squares(s)
    header(s, kicker, title_txt, tfs=tfs)
    vside(s, side or "PPD-UTM DIC  ·  FINAL PRESENTATION")
    pageno(s)
    return s


def ghost(s, x, y, w, h, label, sub):
    """A dashed placeholder for content that arrives later - visibly intentional."""
    g = rect(s, x, y, w, h, CREAM, line=SAGE, lw=1.2)
    g.line.dash_style = 4                                    # dashed
    text(s, x, y + h / 2 - 0.34, w, 0.4, label, fs=13, font=SEMI, colour=SAGE,
         align=PP_ALIGN.CENTER)
    text(s, x + 0.3, y + h / 2 + 0.02, w - 0.6, 0.5, sub, fs=10, colour=SAGE,
         align=PP_ALIGN.CENTER)
    return g


# ================================================================ demo media (cached)
_T = os.path.join(ROOT, "Software", "UTM_PyQt6", "Test data",
                  "Fracture tests")
_VID = [
    # speed = container duration / 12 s — 12-second lapses, his ask 2026-09-06; S26 and S32
    # chosen for MARKER CLARITY (S13 was dark-on-dark, S30's dots carry overspray crescents)
    ("demo_pla.mp4", "PLA — S26", "quasi-brittle — snaps in one clean break at ~5 % strain",
     os.path.join(_T, "Specimen_S26_V2_Spray_Video3", "20260817_111525", "video.avi"), 3.21),
    # S30, not S32: S32's capture ends with the specimen drawn but UNBROKEN — the snap the
    # audience waits for is only on S30's film (checked frame-by-frame 2026-09-06)
    ("demo_petg.mp4", "PETG — S30", "glossier, more ductile — it draws, then tears",
     os.path.join(_T, "Specimen_S30_V3_PETG_Spray_Video9", "20260822_180252", "video.avi"), 4.50),
    ("demo_tpu.mp4", "TPU — S35", "rubber-like · leaves the frame before it fractures",
     os.path.join(_T, "Specimen_S35_V5_TPU_Spray_Video14", "20260824_151610", "video.avi"), 6.64),
]


def ensure_media():
    os.makedirs(MEDIA, exist_ok=True)
    for name, _t, _s, src, speed in _VID:
        dst = os.path.join(MEDIA, name)
        post = dst[:-4] + "_poster.png"
        if not os.path.exists(dst):
            print("  encoding", name)
            subprocess.run(
                ["ffmpeg", "-y", "-v", "error", "-i", src,
                 "-vf", "transpose=1,scale=1280:-2,setpts=PTS/%.2f,fps=30,tpad=stop_mode=clone:stop_duration=2" % speed,
                 "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "26",
                 "-movflags", "+faststart", dst], check=True)
        if not os.path.exists(post):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "5", "-i", dst,
                            "-frames:v", "1", post], check=True)


# =========================================================================== 01 · title
s = prs.slides.add_slide(BLANK)
base(s, rail=False)
rect(s, 0.30, 0, 0.52, 1.00, INK)
rect(s, 0.30, 1.14, 0.52, EH - 1.14, SAGE)
ju(s, x=1.30, y=0.40, hgt=0.52)
squares(s)
# Slide 1 mirrors the edits HE made on his own copy after delivery (2026-09-04): the
# project name in full, real supervisor names, the date under the rule instead of on the
# edge, and no programme footer. A rebuild must never regress them.
text(s, 1.28, 2.02, 11.3, 2.0, [
    [("1-D DIC IMPLEMENTATION ON", {})],
    [("UNIVERSAL TESTING MACHINE", {})],
], fs=38, font=SEMI, colour=INK, spacing=1.22)
text(s, 1.32, 3.62, 11.0, 0.6,   # his rewrite 2026-09-07
     "A camera-instrumented desktop tensile tester — built, tested, validated, and "
     "documented.",
     fs=15, font=BODY, colour=SAGE)
tricolour(s, 1.32, 4.22, w=4.3, h=0.075)
text(s, 1.32, 4.42, 3.0, 0.35, "SEPTEMBER 2026", fs=10, font=SEMI, colour=INK)
text(s, 1.32, 5.55, 7.4, 1.5, [
    [("Adithya Sivakumar", {"font": SEMI, "fs": 14})],
    [("adithya.sivakumar@ju.se", {"fs": 11, "colour": SAGE})],
    [("", {"fs": 5})],
    [("Supervisors:  Johan Jansson · Mirza Cenanovic", {"fs": 11, "colour": SAGE})],
], spacing=1.15)
pageno(s)

# ========================================================================== 02 · agenda
s = content_slide("agenda", "Content, in six parts")
# he deleted the side-rail text on this slide (2026-09-07) — keep it deleted on rebuilds
for _sh in list(s.shapes):
    if _sh.has_text_frame and _sh.text_frame.text == "PPD-UTM DIC  ·  FINAL PRESENTATION":
        _sh._element.getparent().remove(_sh._element)
_AG = [
    ("01", "DIC, in one picture", "what the rig measures, and why no sensor touches the part"),
    ("02", "What was built", "hardware, software — and 20 things it does on its own"),
    ("03", "Live demo", "a specimen pulled to fracture, live on the rig"),
    ("04", "Validation", "the same material through a MOT lab test — and how close we land"),
    ("05", "AI in the loop", "how this was built by one engineer and a coding agent"),
    ("06", "Future work", "What comes next and interesting numbers"),  # his retitle
]
for i, (n, t, d) in enumerate(_AG):
    r, c = divmod(i, 2)
    x, y = 0.85 + c * 6.15, 2.20 + r * 1.45
    card(s, x, y, 5.75, 1.18)
    text(s, x + 0.22, y + 0.16, 0.95, 0.8, n, fs=30, font=DISP, colour=TAN)
    text(s, x + 1.05, y + 0.18, 4.55, 0.4, t, fs=14.5, font=SEMI, colour=INK)
    text(s, x + 1.05, y + 0.60, 4.55, 0.5, d, fs=10.5, colour=SAGE)
text(s, 0.85, 6.72, 11.6, 0.3,
     "Appendix: Thresholding · PLA vs PETG vs TPU · rig-to-rig noise.",
     fs=10.5, colour=SAGE)

# ================================================================ 03a · where DIC is used
# Inserted 2026-09-07 before the principle slide: six arenas, ours highlighted. Carries a
# LITERAL "03" page number (the background block's number, same convention as the click
# slides) and does NOT touch the page counter — so no downstream slide renumbers.
s = prs.slides.add_slide(BLANK)
base(s); ju(s); squares(s)
header(s, "01 · background", "Where DIC is used — and where this project sits")
vside(s, "BACKGROUND")
text(s, 12.55, 7.08, 0.62, 0.3, "03", fs=10, font=SEMI, colour=SAGE, align=PP_ALIGN.RIGHT)
text(s, 0.85, 1.94, 11.6, 0.28,
     "DIC — Digital Image Correlation — measures how a surface deforms by comparing "
     "photographs of it under load: no contact, no wires, just pixels tracked frame to "
     "frame.", fs=10.5, colour=SAGE)
_arenas = [
    ("Material testing & characterization",
     "stress–strain curves, E, σy, UTS, εf — strain measured without touching the "
     "specimen. THIS PROJECT: a desktop tensile rig whose only extensometer is a camera.",
     True),
    ("Manufacturing quality control",
     "warpage, springback and assembly distortion checked on the line — parts against "
     "CAD, contactless and in minutes", False),
    ("Aerospace structural monitoring",
     "wing bend and fuselage-skin strain in full-scale tests — thousands of virtual "
     "gauges from a pair of cameras", False),
    ("Fracture mechanics & crack propagation",
     "strain concentration at the crack tip, crack speed and direction — our future-work "
     "item 4 builds exactly this on the same rig", False),
    ("Biomechanics & medical devices",
     "tissue, implants and prostheses under load — contactless is the only option when "
     "the specimen must stay untouched", False),
    ("Thermal stress analysis",
     "expansion and warpage under heating — where a glued strain gauge would cook, the "
     "camera just watches", False),
]
for _i, (_t, _d, _ours) in enumerate(_arenas):
    _r, _c = divmod(_i, 3)
    _x, _y = 0.85 + _c * 3.98, 2.26 + _r * 2.20
    if _ours:
        # a PLAIN twin sits underneath: before his click the card reads like the other
        # five; the dark THIS-PROJECT stack (drawn last) fades in over it on click
        card(s, _x, _y, 3.72, 2.05)
        rect(s, _x, _y, 0.09, 2.05, FAINT)
        text(s, _x + 0.24, _y + 0.18, 3.3, 0.55, _t, fs=12.5, font=SEMI, colour=INK)
        text(s, _x + 0.24, _y + 0.76, 3.32, 1.18,
             _d.split(" THIS PROJECT")[0], fs=9.3, colour=SAGE, spacing=1.0)
        card(s, _x, _y, 3.72, 2.05, fill=INK)
        rect(s, _x, _y, 0.09, 2.05, TAN)
        chip(s, _x + 0.24, _y + 0.16, "THIS PROJECT", fill=TAN, fg=INK, fs=8.5)
        text(s, _x + 0.24, _y + 0.54, 3.3, 0.55, _t, fs=12.5, font=SEMI, colour=WHITE)
        text(s, _x + 0.24, _y + 1.08, 3.32, 0.88, _d, fs=9.3, colour=CREAM, spacing=1.0)
    else:
        card(s, _x, _y, 3.72, 2.05)
        rect(s, _x, _y, 0.09, 2.05, FAINT)
        text(s, _x + 0.24, _y + 0.18, 3.3, 0.55, _t, fs=12.5, font=SEMI, colour=INK)
        text(s, _x + 0.24, _y + 0.76, 3.32, 1.18, _d, fs=9.3, colour=SAGE, spacing=1.0)
text(s, 0.85, 6.68, 11.6, 0.4,
     "…and more: FEA model validation, civil-structure monitoring, electronics "
     "reliability, high-speed impact. One method, many arenas — the next slides are our "
     "corner: the tensile test.", fs=9.5, colour=SAGE)

# =========================================================================== 03 · DIC?
s = content_slide("01 · background", "DIC — the camera is the strain gauge", side="BACKGROUND")
text(s, 0.85, 1.98, 11.6, 0.4,
     "How WE use DIC — the simplest form there is: two painted dots on the gauge; the "
     "camera tracks their separation L every frame, and strain is just (L − L₀) / L₀.",
     fs=12, colour=INK)
pic(s, os.path.join(FIGS, "ppd_dic_explain.png"), 2.47, 2.52, 8.4, 2.45)
# Reworded with him 2026-09-05 ("no clip?" - say plainly what touches nothing; "no calibration
# is misleading" - lead with the live curve instead). The third card is HIS in-file edit, mirrored
# here so a rebuild cannot regress it.
_c = [("Contactless", "No strain gauge glued on, no clip-on extensometer — nothing touches "
      "the specimen"),
      ("Pixels become strain", "Each frame, the marker spacing L is measured in pixels and "
      "compared with the frozen L₀ — strain = (L − L₀) / L₀, no millimetres needed"),
      ("Live stress–strain", "Load cell gives force, the camera gives strain — the "
      "stress–strain curve draws itself live during the pull")]
for i, (t, d) in enumerate(_c):
    x = 0.85 + i * 3.95
    card(s, x, 5.30, 3.70, 1.45)
    rect(s, x, 5.30, 0.07, 1.45, TAN)
    text(s, x + 0.25, 5.47, 3.3, 0.35, t, fs=13.5, font=SEMI, colour=INK)
    text(s, x + 0.25, 5.85, 3.3, 0.85, d, fs=10.5, colour=INK, spacing=1.05)
# Speaker note he asked for (2026-09-05) - the glued/clipped/camera mnemonic, so the
# instrument-terminology question has its answer in his pocket. Notes survive rebuilds only
# if the generator writes them, hence here and not only in the file.
s.notes_slide.notes_text_frame.text = (
    "glued = strain gauge, clipped = extensometer, camera = video extensometer "
    "(XT-205, and our rig)")

# ---- 03 · the click sequence (his ask, 2026-09-06): one claim per click. Each click-slide
# highlights ONE card with its own picture while everything else greys out — the same
# consecutive-slides trick the SF hero pair (05/06) uses, because python-pptx cannot author
# animations and the click IS the transition. All three carry the literal page number 03:
# they are builds of page 03, not new pages, so the deck's later numbering never shifts.
_GREYED = RGBColor(0xC6, 0xC2, 0xBA)
# Contactless gets THREE pictures side by side (his ask 2026-09-05): the principle drawing, a
# commercial clip-on (his photo), and our rig with the camera touching nothing. Each column
# sits exactly above one of the three claim cards, so the row reads as one family.
_CLICK_PAIR = [
    ("ppd_clipon_combo.png", 0.85, 7.55,
     "the clip-on extensometer — the principle, and a commercial one (Zwick/Roell): knife "
     "edges TOUCH the specimen"),
    ("DIC camera setup.jpg", 8.75, 3.70, "our rig — the camera, touching nothing"),
]
_CLICK_IMGS = {
    1: ("ppd_pixels.png", ""),          # the reference calc is baked into the figure
    2: ("ppd_ui_curve.png",
        "S26 · PLA — the curve exactly as the rig draws it live, one point per frame"),
}


def _click_slide(hi):
    s = prs.slides.add_slide(BLANK)
    base(s); ju(s); squares(s)
    header(s, "01 · background", "DIC — the camera is the strain gauge")
    vside(s, "BACKGROUND")
    text(s, 12.55, 7.08, 0.62, 0.3, "03", fs=10, font=SEMI, colour=SAGE,
         align=PP_ALIGN.RIGHT)
    text(s, 0.85, 1.98, 11.6, 0.4,
         "DIC — Digital Image Correlation — measures how a part deforms by comparing "
         "photographs of its surface while it is loaded; here in its simplest two-dot form.",
         fs=11.5, colour=_GREYED)
    # clear air between the greyed intro line and the picture row — the first cut had the
    # card's top edge running through the text
    if hi == 0:
        for img, x, w, cap in _CLICK_PAIR:
            pic(s, os.path.join(FIGS, img), x, 2.46, w, 2.42)
            text(s, x, 4.94, w, 0.42, cap, fs=9, colour=SAGE, align=PP_ALIGN.CENTER)
    else:
        img, cap = _CLICK_IMGS[hi]
        pic(s, os.path.join(FIGS, img), 1.60, 2.36, 10.10, 2.78)
        if cap:
            text(s, 1.60, 5.02, 10.10, 0.26, cap, fs=9.5, colour=SAGE,
                 align=PP_ALIGN.CENTER)
    for i, (t, d) in enumerate(_c):
        x = 0.85 + i * 3.95
        on = (i == hi)
        card(s, x, 5.30, 3.70, 1.45)
        rect(s, x, 5.30, 0.07, 1.45, TAN if on else FAINT)
        text(s, x + 0.25, 5.47, 3.3, 0.35, t, fs=13.5, font=SEMI,
             colour=INK if on else _GREYED)
        text(s, x + 0.25, 5.85, 3.3, 0.85, d, fs=10.5, colour=INK if on else _GREYED,
             spacing=1.05)
    return s


for _hi in range(3):
    _click_slide(_hi)

# ==================================================================== 04 · what was built
# 2026-09-07 rework, his asks: motors + electronics join hardware; camera/LED/enclosure
# fold into ONE highlighted point (his main hands-on hardware); the WHOLE software block
# is highlighted (built in-house); OpenCV and the 20 one-click features named; fps set to
# the MEASURED ≈20 (the requested 35 is never delivered at our 50 ms exposure); the stale
# right-hand stat boxes are gone — the one fact no other slide carries (9 weeks) closes
# the slide instead.
s = content_slide("02 · the build", "DIC rig and Application built together",
                  side="THE BUILD")
pic(s, os.path.join(FIGS, "UTM rig_12-08-26.jpg"), 0.85, 2.00, 3.05, 4.35)
text(s, 0.85, 6.42, 3.05, 0.3, "the PPD-UTM DIC", fs=10, colour=SAGE, align=PP_ALIGN.CENTER)

text(s, 4.25, 2.02, 3.9, 0.34, "HARDWARE", fs=11, font=SEMI, colour=TAN)
bullets(s, 4.25, 2.40, 3.85, 1.85, [
    "Aluminium-profile frame — twin ball screws, brackets, load holders",
    "4.5 kN load cell, 3D-printed grips",
    "drive motors + their control electronics, emergency stops",
], fs=10.5, gap=5)
# the Basler line stays IN the list flow — a small tint behind it, not a separate box
_HL = RGBColor(0xEF, 0xE6, 0xD8)
rect(s, 4.20, 4.32, 3.95, 0.78, _HL, line=TAN, lw=1.0)
text(s, 4.25, 4.40, 3.85, 0.66,
     [[("▪  ", {"colour": TAN, "bold": True}),
       ("Basler camera · LED panels · light enclosure", {"bold": True, "colour": INK}),
       (" — the DIC eye, and the hardware I worked on most", {})]],
     fs=10.5, colour=SAGE, spacing=1.0)
card(s, 8.45, 2.02, 4.0, 3.95, fill=_HL, line=TAN, lw=1.4)
rect(s, 8.45, 2.02, 0.07, 3.95, TAN)
text(s, 8.70, 2.16, 3.6, 0.34, "SOFTWARE — BUILT IN-HOUSE", fs=11, font=SEMI, colour=TAN)
bullets(s, 8.70, 2.56, 3.62, 3.3, [
    "One PyQt6 application runs the whole test — written line by line in this project",
    "OpenCV does the seeing: thresholding, blob detection, sub-pixel centroids",
    "live DIC strain at ≈20 fps (measured — the exposure sets it), six closed-loop "
    "protocols",
    "20 smart features, each automated behind a single click",
    "every run leaves CSV + video + PDF; the post-processor re-measures any recording",
], fs=10, gap=5)

# (the 9-weeks line is gone — he deleted it 2026-09-07)

# ============================================================= 05a · the twenty features
_SF = [
    (1, "DIC health HUD"), (2, "Prepare specimen"), (3, "Settings / recipes"),
    (4, "1-click PDF report"), (5, "Auto-stop at fracture"), (6, "Strain-rate control"),
    (7, "Stall guard"), (8, "Release load"), (9, "Advanced test modes"),
    (10, "Auto-preload"), (11, "Auto-metadata link"), (12, "DIC auto-calibrate"),
    (13, "Guided wizard"), (14, "Test registry"), (15, "Dead-DIC guard"),
    (16, "Live Px₀ overlay"), (17, "Video + stills capture"), (18, "DIC post-processing"),
    (19, "Noise capture"), (20, "Manual blob selection"),
]
_HERO = {
    5: "sees the load collapse and halts the motor itself — no hand on the stop button",
    9: "6 closed-loop protocols in one tab — the tests beyond a plain pull to fracture",
    18: "re-measures ANY recorded video — it is how the commercial lab's test got audited",
}


def sf_grid(s, heroes=False):
    cols, x0, y0 = 4, 0.85, 2.10
    w, h, gx, gy = 2.83, 0.82, 0.12, 0.14
    # Heroes are drawn LAST: shapes stack in draw order, and a hero card grown beyond its cell
    # was being overlapped by the very next greyed tile — its right edge visibly clipped.
    draw_order = sorted(enumerate(_SF), key=lambda t: (heroes and t[1][0] in _HERO, t[0]))
    for i, (n, name) in draw_order:
        r, c = divmod(i, cols)
        x, y = x0 + c * (w + gx), y0 + r * (h + gy)
        hero = heroes and n in _HERO
        if heroes and not hero:
            t = card(s, x, y, w, h, fill=CREAM, line=FAINT)
            text(s, x + 0.14, y + 0.10, w - 0.28, 0.3, "SF%d" % n, fs=8.5, font=SEMI,
                 colour=FAINT)
            text(s, x + 0.14, y + 0.32, w - 0.28, 0.42, name, fs=10.5, colour=FAINT)
        elif hero:
            dx, dy = 0.17, 0.13
            t = card(s, x - dx, y - dy, w + 2 * dx, h + 2 * dy, fill=INK, line=TAN, lw=1.4)
            text(s, x - dx + 0.16, y - dy + 0.09, w + 2 * dx - 0.3, 0.3, "SF%d" % n,
                 fs=9, font=SEMI, colour=TAN)
            text(s, x - dx + 0.16, y - dy + 0.30, w + 2 * dx - 0.3, 0.4, name,
                 fs=12.5, font=SEMI, colour=WHITE)
            text(s, x - dx + 0.16, y - dy + 0.60, w + 2 * dx - 0.3, 0.5, _HERO[n],
                 fs=8.2, colour=RGBColor(0xC9, 0xD2, 0xD4), spacing=0.98)
        else:
            t = card(s, x, y, w, h)
            rect(s, x, y, 0.05, h, SAGE)
            text(s, x + 0.16, y + 0.10, w - 0.28, 0.3, "SF%d" % n, fs=8.5, font=SEMI,
                 colour=TAN)
            text(s, x + 0.16, y + 0.32, w - 0.28, 0.42, name, fs=11, colour=INK)
    return t


s = content_slide("02 · the build", "20 Smart Features - rig does on its own",  # his retitle
                  side="THE BUILD")
sf_grid(s, heroes=False)
text(s, 0.85, 7.00, 11.6, 0.3,
     "each of these has its own evidence page in the final project deck",  # his wording
     fs=10, colour=SAGE)

# ============================================================= 05b · the three that matter
s = content_slide("02 · the build", "3 of my best picks for the smart features",
                  side="THE BUILD")
sf_grid(s, heroes=True)
text(s, 0.85, 7.00, 11.6, 0.3,
     "SF5 protects the specimen · SF9 runs the six closed-loop protocols · SF18 made the "
     "validation possible",
     fs=10.5, font=SEMI, colour=INK)

# ======================================================================= 06 · live demo
ensure_media()
s = content_slide("03 · live demo", "PLA snaps, PETG draws, TPU stretches — then live demo",
                  side="LIVE DEMO")
for i, (name, label, sub, _src, _sp) in enumerate(_VID):
    y = 1.98 + i * 1.645
    vw, vh = 9.35, 1.54
    card(s, 0.85, y, vw, vh)
    s.shapes.add_movie(os.path.join(MEDIA, name), Inches(0.94), Inches(y + 0.045),
                       Inches(vw - 0.18), Inches(vh - 0.09),
                       poster_frame_image=os.path.join(MEDIA, name[:-4] + "_poster.png"),
                       mime_type="video/mp4")
    chip(s, 0.85, y - 0.005, label, fill=INK, fs=9)
    text(s, 10.35, y + 0.24, 2.6, 0.4, label.split(" — ")[0], fs=15, font=SEMI, colour=INK)
    text(s, 10.35, y + 0.58, 2.6, 0.9, sub, fs=9.5, colour=SAGE, spacing=1.0)
text(s, 0.85, 6.97, 11.6, 0.3,
     "15-second timelapses of real pulls on this rig — then we "
     "switch to the "
     "live software and break one for real.", fs=10, colour=SAGE)

# ===================================================================== 07 · validation setup
# NOTE 2026-09-06: his disk copy of this slide has diverged — retitled, bullets trimmed, the
# condition chips and analyses card replaced by his own pictures. Never copy_content this
# slide over his; the title below is synced so a rebuild at least cannot regress it.
s = content_slide("04 · validation", "The same specimen, tested at MOT lab",
                  side="VALIDATION")
pic(s, os.path.join(FIGS, "XT205-MOT_Wideview.jpg"), 0.85, 2.05, 2.72, 4.35)
pic(s, os.path.join(FIGS, "XT205-MOT Closerview.jpg"), 3.72, 2.05, 2.72, 4.35)
text(s, 0.85, 6.46, 5.6, 0.30, "the MOT lab: Zwick/Roell Z100, XT-205 video extensometer "
     "on our specimen", fs=9, colour=SAGE, align=PP_ALIGN.CENTER)
text(s, 6.85, 2.05, 5.7, 0.34, "THE REFERENCE", fs=11, font=SEMI, colour=TAN)
bullets(s, 6.85, 2.42, 5.55, 1.9, [
    ("MOT materials lab — commercial tensile frame", {"bold": True}),
    "XT-205 video extensometer: a camera that tracks two painted marks — the same principle "
    "as our DIC, in certified form",
    "two specimens from our own print batch: XT205-S1 and XT205-S2",
], fs=11, gap=6)
text(s, 6.85, 4.35, 5.7, 0.34, "TEST CONDITIONS · XT205-S2", fs=11, font=SEMI, colour=TAN)
for i, t in enumerate(("45 mm gauge", "2 mm/min", "300 N preload")):
    chip(s, 6.85 + i * 1.75, 4.72, t, fill=SAGE, fs=10)
card(s, 6.70, 5.24, 5.95, 1.86, fill=WHITE, line=TAN, lw=1.4)
rect(s, 6.70, 5.24, 0.07, 1.86, TAN)
text(s, 6.95, 5.35, 5.6, 0.30, "TWO ANALYSES ON THE SAME SESSION", fs=11, font=SEMI,
     colour=TAN)
bullets(s, 6.95, 5.68, 5.55, 1.4, [
    ("Analysis 1 — instrument vs instrument: the XT-205's certified strain readout against "
     "our rig's DIC on matched specimens; E, σy, UTS and ε_f each computed twice, "
     "independently", {"fs": 9.3}),
    ("Analysis 2 — our method on THEIR data: the session's raw XT-205 video re-measured "
     "frame-by-frame by our DIC post-processor (SF18) — marker-centroid detection, frozen "
     "Px₀, strain as the pixel ratio (L − L₀)/L₀ — on the commercial lab's own footage",
     {"fs": 9.3}),
], fs=9.3, gap=5)

# ===================================================================== 08 · validation results
s = content_slide("04 · validation", "Analysis 1 : Two rigs, two specimens, one material",
                  side="VALIDATION")
pic(s, os.path.join(FIGS, "mot2cmp_pair.png"), 0.85, 2.02, 7.45, 4.90)
_tbl = [("UTS", "48.34 / 44.62 MPa", "−7.7 %"),
        ("Yield σy", "39.23 / 39.61 MPa", "+1.0 %"),
        ("Modulus E", "3.45 / 3.23 GPa", "−6.4 %"),
        ("Fracture εf", "5.25 / 5.21 %", "−0.8 %")]
text(s, 8.55, 2.02, 3.9, 0.32, "S34 (PPD-UTM DIC)  /  XT205-S2 (MOT)", fs=10.5, font=SEMI,
     colour=TAN)
for i, (q, v, o) in enumerate(_tbl):
    y = 2.40 + i * 0.62
    card(s, 8.55, y, 3.9, 0.53)
    text(s, 8.72, y + 0.09, 1.35, 0.35, q, fs=11, font=SEMI, colour=INK)
    text(s, 9.95, y + 0.11, 1.75, 0.35, v, fs=9.5, colour=SAGE)
    _off = abs(float(o.replace("−", "-").replace("%", "").strip()))
    text(s, 11.65, y + 0.08, 0.72, 0.35, o, fs=11, font=SEMI,
         colour=RGBColor(0x2E, 0x9E, 0x4F) if _off <= 2.0
         else RGBColor(0xB9, 0x8A, 0x00))
# one textbox PER bullet so each can carry its own entrance animation (his ask 2026-09-06);
# order and geometry are HIS — he rewrote this box before asking for the split
for y, h, row in (
    (5.26, 0.62, "UTS and E gaps (6–8 %) carry a 3× speed difference plus normal specimen "
                 "scatter (CV ≈ 2.5 %) — within family, and the whole curve shape matches"),
    (5.90, 0.34, "Yield within 1 % — stress scale agrees where the curve is stable"),
    (6.26, 0.34, "Fracture strain 5.25 vs 5.21 % — two different optical instruments, "
                 "0.8 % apart"),
    (6.62, 0.48, "Analysis 2 closes the loop: their own video through our post-processor "
                 "lands on the same line (two slides on)"),
):
    bullets(s, 8.53, y, 3.9, h, [row], fs=9.3, gap=3)

# ===================================================================== 09 · why differences
# (his reorder 2026-09-06: the offset explanation now sits BETWEEN Analysis 1 and Analysis 2)
s = content_slide("04 · validation", "Analysis 1 : why the offset? ", side="VALIDATION")
# cards in the honest-ranking order (his ask 2026-09-06): seating, specimen, then speed; the
# moisture card now carries the humidity literature verdict + our own two-batch evidence
# his order 2026-09-07: SPECIMEN & MOISTURE leads (it dominates), grips second, speed
# third; the accents travel with their cards so the deck's swap and this list agree
_why = [
    ("Specimen & moisture", "studied",
     ["Different print batches, weeks apart, unconditioned storage",   # his capital D
      "even within ONE batch, UTS scatters print-to-print (CV ≈ 2.5 %) — the batch "
      "effects sit on top of that",
      "literature: 24 h of humid filament storage already costs PLA ≈8.5 % UTS; "
      "150 h ≈11 % (Hamid 2022)"]),
    # (his deletion 2026-09-07: the "our two batches moved exactly that way" bullet is out)
    ("Pull speed", "measured",                                         # his rewrite, verbatim
     ["Travel speed we INPUT is the CROSSHEAD's, in mm/sec (ours 0.1 mm/sec) — an open "
      "loop: no feedback tracks whether the specimen is stretched at that speed",
      "→ Strain-rate moves the SLOPE (E) more than the UTS — and predicts under 1 % of "
      "the stress gap"]),
    ("Grips & seating", "measured",
     ["55–79 % of the EARLY crosshead travel is eaten by slack in our printed grips "
      "before the gauge feels anything",
      "our four runs cluster at 21 % of travel reaching the gauge — a joint that "
      "either seats or doesn't",                                       # his trim
      "→ costs only EARLY crosshead travel and bends the curve's toe — the DIC strain "
      "never sees it: the camera watches the gauge, not the crosshead"]),
]
for i, (t, tag, rows) in enumerate(_why):
    x = 0.85 + i * 3.98
    card(s, x, 2.10, 3.72, 3.95)
    rect(s, x, 2.10, 3.72, 0.09, (SAGE, TAN, INK)[i])
    text(s, x + 0.24, 2.32, 3.3, 0.4, t, fs=15, font=SEMI, colour=INK)
    chip(s, x + 0.24, 2.76, tag, fill=(INK if tag == "measured" else TAN), fs=8.5)
    bullets(s, x + 0.24, 3.28, 3.30, 3.1, rows, fs=10, gap=7)
text(s, 1.09, 5.75, 3.35, 0.26,
     [[("Hamid et al. 2022 · doi 10.1007/978-981-16-8954-3_47",
        {"url": "https://doi.org/10.1007/978-981-16-8954-3_47"})]], fs=7.8, colour=SAGE)
# (the honest-ranking footer is gone — he deleted it 2026-09-07; the card ORDER carries it)

# ===================================================================== 10 · can it be trusted
# NOTE 2026-09-06: on HIS disk copy this slide carries his own figure geometry (pic 1.26/2.01/
# 10.52/3.22 on a resized card), the bottom cards moved up under it, and those cards + footer
# grouped into one shape named "analysis2_bottom". copy_content would regress all of that —
# in-place edits only.
s = content_slide("04 · validation", "Analysis 2 : Same video, Same specimen, two calculation "
                  "methods", side="VALIDATION")
pic(s, os.path.join(FIGS, "mot2pp_full.png"), 0.85, 2.02, 11.65, 3.80)
# three cards since 2026-09-07 (the "one line" card told him nothing); instrument names,
# never ours/theirs — his standing rule from the same date
_big = [("+0.08 %", "fracture strain apart",
         "5.21 (XT-205) vs 5.22 (PPD-UTM DIC), on the same footage"),
        ("−55 µε", "constant difference, flat to fracture", "= 0.07 px on a 1255 px gauge"),
        ("3.21–3.24 vs 3.23", "Young's modulus E (GPa), elastic region — PPD-UTM DIC fits "
         "on the XT-205 footage vs the XT-205 machine",
         "fixed-window fit 3.21 · steepest-window 3.24 · machine 3.23 — the SLOPE agrees, "
         "not just the endpoints")]
for i, (n, t, d) in enumerate(_big):
    x = 0.85 + i * 3.98
    card(s, x, 6.00, 3.72, 1.28)
    rect(s, x, 6.00, 0.07, 1.28, TAN)
    text(s, x + 0.22, 6.08, 3.4, 0.40, n, fs=16, font=DISP, colour=INK)
    text(s, x + 0.22, 6.48, 3.42, 0.42, t, fs=9, font=SEMI, colour=INK, spacing=0.95)
    text(s, x + 0.22, 6.90, 3.42, 0.36, d, fs=8, colour=SAGE, spacing=0.95)
# (the bottom-strip explainer footer is gone — he deleted it from his grouped set
#  2026-09-07; the figure's own in-strip labels carry the message now)

# ===================================================================== 11 · AI in the loop
s = content_slide("05 · process", "AI in the loop - Built by one engineer and a coding agent",
                  side="PROCESS")   # his retitle 2026-09-07
_steps = [("intent", "“the rig must stop itself at fracture”"),
          ("prompt", "precise ask + constraints + how to verify"),
          ("Claude Code", "writes app code, tests, analysis"),
          ("verify on rig", "real pulls; failures go straight back in"),
          ("evidence", "every claim becomes a measured deck page")]
for i, (t, d) in enumerate(_steps):
    y = 2.10 + i * 0.99
    card(s, 0.85, y, 4.55, 0.84)
    rect(s, 0.85, y, 0.07, 0.84, TAN if i % 2 else INK)
    text(s, 1.08, y + 0.10, 1.55, 0.4, t, fs=12.5, font=SEMI, colour=INK)
    text(s, 2.65, y + 0.13, 2.7, 0.6, d, fs=9.5, colour=SAGE, spacing=0.98)
from pptx.enum.shapes import MSO_SHAPE as _MS
for i in range(4):                                   # solid arrows ON TOP of the cards
    ar = s.shapes.add_shape(_MS.DOWN_ARROW, Inches(0.99), Inches(2.10 + i * 0.99 + 0.76),
                            Inches(0.30), Inches(0.32))
    ar.fill.solid(); ar.fill.fore_color.rgb = TAN
    ar.line.color.rgb = WHITE; ar.line.width = Pt(1.2)
# the feedback loop (his ask 2026-09-07): verify-on-rig runs back up to prompt — a clean
# left-hand spine with an arrowhead re-entering the prompt card, captioned along the spine
_y_prompt, _y_verify = 2.10 + 0.99 + 0.42, 2.10 + 3 * 0.99 + 0.42   # card mid-heights
for geo in ((0.52, _y_prompt - 0.022, 0.26, 0.045),                 # stub into prompt
            (0.52, _y_prompt - 0.022, 0.045, _y_verify - _y_prompt + 0.045),  # spine
            (0.52, _y_verify - 0.022, 0.33, 0.045)):                # stub from verify
    r_ = rect(s, *geo, TAN)
ah = s.shapes.add_shape(_MS.RIGHT_ARROW, Inches(0.72), Inches(_y_prompt - 0.105),
                        Inches(0.22), Inches(0.21))
ah.fill.solid(); ah.fill.fore_color.rgb = TAN
ah.line.fill.background()

# counts refreshed 2026-09-07 (unchanged): 370 commits / ~26 k dev lines / 853 prompts /
# 195 vs ~1 300 h. The 98-tests tile is gone — his call: four tiles only.
_ai = [("370", "commits · 94 % co-authored with the agent"),
       ("~26 k", "lines of Python in the rig software itself — app, DIC engine, analysis, "
        "tests (deck-builder scripts not counted)"),
       ("853", "prompts, measured from the session log (28 May → 6 Sep) — about two per "
        "shipped commit"),
       ("≈7×", "the leverage: 195 h hands-on with the agent over 6 months vs ≈1 300 h "
        "estimated solo (26 k lines of hardware-coupled GUI + vision code at ~20 finished "
        "lines/hour)")]
for i, (n, d) in enumerate(_ai):
    y = 2.10 + i * 0.99
    card(s, 5.70, y, 6.78, 0.84)
    text(s, 5.95, y + 0.14, 1.75, 0.55, n, fs=20, font=DISP, colour=INK)
    text(s, 7.55, y + 0.17, 4.8, 0.5, d, fs=9.5, colour=SAGE, spacing=0.96)
bullets(s, 5.70, 6.12, 6.8, 1.0, [
    ("the prompt is the engineering: what to build, what would falsify it, how to prove it ran",
     {"bold": True}),
    "the agent measures instead of assuming — it renders every page and looks at it",
], fs=10.5, gap=5)


# ===================================================================== 12 · future work
# his order 2026-09-06 (title also his); the rate-matched MOT rerun card gave its seat to the
# new fracture-behaviour item — the rerun stays on the roadmap, just not on this slide.
s = content_slide("06 · outlook", "Future work", side="OUTLOOK")
_fw = [
    ("Poisson & true stress", "four markers → lateral strain, ν, Cauchy stress",
     "maths written and self-tested; blocked on optics — needs a gauge-zoomed second camera "
     "or a wider specimen"),
    ("2D-DIC strain field", "full-field strain over the speckled gauge, not just two dots",
     "offline first, in the existing post-processor; needs lower exposure — the white body "
     "currently saturates the sensor"),
    ("Feed simulation models", "measured strain fields calibrating FE material cards",
     "export the field per frame; compare predicted vs measured maps on the same geometry"),
    ("Studying fracture behaviour", "full-field strain maps around the crack tip; crack "
     "propagation speed and direction",
     "film the necking zone at higher magnification and run the 2D-DIC field around the "
     "growing crack — builds directly on the strain-field item above"),
    ("Correlation, not binary", "sub-pixel tracking that keeps the grey levels",
     "measured gain: 1.1–2.1× less jitter; add as a post-processing option before touching "
     "the live loop"),
    ("Design better grips", "printed jaws that seat deterministically — no low-strain "
     "slack, no 21 % / 33 % lottery",
     "size the slack (re-mount one specimen, elastic pulls only), redesign, reprint, "
     "re-run — success: one cluster, shorter toe"),
]
for i, (t, what, how) in enumerate(_fw):
    r, c = divmod(i, 3)
    x, y = 0.85 + c * 3.98, 2.05 + r * 2.42
    card(s, x, y, 3.72, 2.24)
    rect(s, x, y, 0.07, 2.24, TAN)
    text(s, x + 0.22, y + 0.13, 3.35, 0.4, t, fs=12.5, font=SEMI, colour=INK)
    text(s, x + 0.22, y + 0.50, 3.35, 0.65, what, fs=9.5, colour=INK, spacing=1.0)
    text(s, x + 0.22, y + 1.24, 0.9, 0.3, "HOW", fs=8, font=SEMI, colour=TAN)
    text(s, x + 0.22, y + 1.44, 3.35, 0.75, how, fs=8.8, colour=SAGE, spacing=1.0)
text(s, 0.85, 6.90, 11.6, 0.4,
     "The upcoming stages are more than features — the 2D-DIC field, fracture behaviour and "
     "the simulation coupling are each worth a thesis of their own.",
     fs=10.5, font=SEMI, colour=INK)

# ===================================================================== 13 · fun facts
# The PCF is computed in documentation/scripts/pcf_figs.py (operational boundary he chose:
# developing + printing + testing, filament cradle-to-gate excluded); the full method,
# inventory and arithmetic live in the Weekly deck's PCF block. This slide carries only
# the interesting aspects — his instruction 2026-09-05.
import pcf_figs as _PCF
_pcf_local, _pcf_ai, _pcf_tot = _PCF.totals()
# his redesign 2026-09-06: one "interesting numbers" slide, TWO sections — emissions on the
# left (headline + the components counted, in one line), moisture on the right (our own
# two-batch evidence + the literature verdict, references hyperlinked).
# his order 2026-09-07: MOISTURE first (left, appears with the slide), CO2 second (right,
# fades in on click — the whole column is grouped by the surgery + COM pass). The emissions
# "counted" line carries its four considerations in bold; the per-test gram gave way to the
# out-emit factor; the moisture card carries a mini-table of the V6-quintet values.
s = content_slide("06 · outlook", "Interesting numbers — moisture effects & emissions",
                  side="OUTLOOK")

text(s, 0.85, 2.02, 5.65, 0.32, "MOISTURE → UTS & FAILURE STRAIN", fs=12, font=SEMI,
     colour=TAN)
rect(s, 0.85, 2.36, 5.65, 0.03, TAN)
card(s, 0.85, 2.56, 5.65, 2.42)
rect(s, 0.85, 2.56, 0.07, 2.42, SAGE)
text(s, 1.15, 2.72, 5.1, 0.50, "our rig: 4.2 % drop in UTS, Fracture strain UP",  # his
     fs=19, font=DISP, colour=INK)
text(s, 1.15, 3.26, 5.2, 0.56,
     "the batch whose filament sat unconditioned 8 days longer prints weaker but more "
     "ductile — the plasticizing signature:",                          # his spelling
     fs=9.5, colour=SAGE, spacing=1.0)
rect(s, 1.15, 3.90, 5.05, 0.015, TAN)
for _y, _cells, _kw in (
    (3.96, ("", "S7 · (8 days earlier)", "batch b–e", "offset"),
     dict(font=SEMI, colour=TAN, fs=8.2)),
    (4.24, ("UTS", "47.82 MPa", "45.81 MPa", "−4.2 %"), dict(colour=INK, fs=9)),
    (4.52, ("εf", "0.030", "0.05–0.075", "↑1.7–2.5×"), dict(colour=INK, fs=9)),
):
    for _x, _w, _c in ((1.15, 0.70, 0), (1.90, 1.75, 1), (3.62, 1.30, 2), (4.92, 1.20, 3)):
        text(s, _x, _y, _w, 0.26, _cells[_c], **_kw)
card(s, 0.85, 5.18, 5.65, 1.42)
rect(s, 0.85, 5.18, 0.07, 1.42, SAGE)
text(s, 1.15, 5.30, 5.1, 0.42, "literature: 8.5 % drop in 24 h",       # his wording
     fs=15, font=DISP, colour=INK)
text(s, 1.15, 5.74, 3.53, 0.44,                                        # his narrower box
     "humid filament storage costs PLA strength (150 h: −11 %); ≤65 % RH keeps UTS "
     "within 3.7 %.", fs=9.5, colour=SAGE, spacing=1.0)
text(s, 1.15, 6.24, 2.55, 0.24,
     [[("Hamid et al. 2022 (doi)", {"url": "https://doi.org/10.1007/978-981-16-8954-3_47"})]],
     fs=7.8, colour=SAGE)
text(s, 3.80, 6.24, 2.55, 0.24,
     [[("Quader et al. 2024 (doi)", {"url": "https://doi.org/10.1089/3dp.2022.0222"})]],
     fs=7.8, colour=SAGE)

text(s, 6.85, 2.02, 5.65, 0.32, "CARBON FOOTPRINT – Rough estimate",  # his header wording
     fs=12, font=SEMI, colour=TAN)
rect(s, 6.85, 2.36, 5.65, 0.03, TAN)
card(s, 6.85, 2.56, 5.65, 2.00)
rect(s, 6.85, 2.56, 0.07, 2.00, TAN)
text(s, 7.15, 2.66, 5.1, 0.46, "≈%.1f kg CO₂e" % _pcf_tot, fs=30, font=DISP, colour=INK)
text(s, 7.15, 3.14, 5.2, 0.24, "For the WHOLE 6-month project — counted:",
     fs=9.5, colour=SAGE)
for _i, (_kw, _info) in enumerate([
    ("the work PC", "955 h at 60 W → 57.3 kWh"),
    ("the AI compute", "195 h of sessions, 0.24 Wh per prompt"),
    ("the Mk4S printer", "60 specimen prints → 5.0 kWh"),
    ("the rig + camera", "45 W, all 39 fractures → 0.3 kWh"),
]):
    text(s, 7.15, 3.40 + _i * 0.23, 5.2, 0.23,
         [[("▪  ", {"colour": TAN}), (_kw, {"bold": True, "colour": INK}),
           ("  (%s)" % _info, {})]], fs=9.3, colour=SAGE)
text(s, 7.15, 4.33, 5.2, 0.22, "— all on Sweden's 0.040 kg CO₂e/kWh grid.",
     fs=9.3, colour=SAGE)
card(s, 6.85, 4.76, 5.65, 1.60)
rect(s, 6.85, 4.76, 0.07, 1.60, TAN)
text(s, 7.15, 4.90, 5.1, 0.55, "≈%.0f× — thinking over pulling"
     % ((_pcf_ai[1] + _PCF.PC_KWH * _PCF.GRID_EF) / (_PCF.RIG_KWH * _PCF.GRID_EF)),
     fs=17, font=DISP, colour=INK)
text(s, 7.15, 5.48, 5.2, 0.80,
     "the AI + the work PC out-emit the test rig itself by that factor — the rig's whole "
     "share, all 39 fractures, is ≈%.0f g. Honest band for the total: %.1f–%.1f kg."
     % (1000 * _PCF.RIG_KWH * _PCF.GRID_EF,
        _pcf_local + _pcf_ai[0], _pcf_local + _pcf_ai[2]),
     fs=10, colour=SAGE, spacing=1.02)
# (the "full method: Weekly deck" footer is gone — he deleted it 2026-09-07)

# ===================================================================== 14 · thanks
s = prs.slides.add_slide(BLANK)
base(s, rail=False)
rect(s, 0.30, 0, 0.52, 1.00, INK)
rect(s, 0.30, 1.14, 0.52, EH - 1.14, SAGE)
ju(s, x=1.30, y=0.40, hgt=0.52)
squares(s)
# 2026-09-07, his closing gag: the SOLIDWORKS out-of-memory popup ("where it began") with
# an arrow to the twelve fractured final frames ("where it went") — on screen from the
# start; the thank-you heading and notes fade in on CLICK (grouped by the surgery).
text(s, 1.05, 1.00, 3.3, 0.30, "where it began", fs=13, font=SEMI, colour=TAN)
pic(s, os.path.join(FIGS, "Errors.png"), 1.05, 1.34, 3.30, 1.56)
from pptx.enum.shapes import MSO_SHAPE as _MSX
_ar = s.shapes.add_shape(_MSX.CURVED_DOWN_ARROW, Inches(4.55), Inches(2.10),
                         Inches(1.30), Inches(1.55))
_ar.fill.solid(); _ar.fill.fore_color.rgb = TAN
_ar.line.fill.background()
text(s, 9.35, 3.42, 2.95, 0.30, "where it went", fs=13, font=SEMI, colour=TAN,
     align=PP_ALIGN.RIGHT)
pic(s, os.path.join(FIGS, "frac_map.png"), 1.15, 3.76, 11.15, 3.60)

text(s, 6.30, 0.85, 6.2, 0.95, "Thank you.", fs=44, font=DISP, colour=INK)
tricolour(s, 6.35, 1.78, w=3.6, h=0.075)
text(s, 6.35, 2.02, 6.1, 0.35,
     "A big thank you to everyone at PPD — for an amazing time here.",
     fs=12.5, font=SEMI, colour=INK)
text(s, 6.35, 2.40, 6.1, 0.30, "Questions — or come break a specimen with me.",
     fs=12, colour=SAGE)
text(s, 6.35, 2.78, 5.5, 0.60, [
    [("Adithya Sivakumar", {"font": SEMI, "fs": 11.5})],
    [("adithya.sivakumar@ju.se", {"fs": 10, "colour": SAGE})],
], spacing=1.15)
pageno(s)

# ===================================================================== 15 · appendix toc
s = content_slide("appendix", "For the curious", side="APPENDIX")
_ap = [("A1", "Otsu thresholding", "how the camera decides what is a marker"),
       ("A2", "PLA vs PETG vs TPU", "our curves against what literature expects"),
       ("A3", "Noise, rig against rig", "how quiet each instrument is, measured at rest"),
       ("A4", "Camera properties", "resolution is a window, exposure sets the frame rate — "
        "what was set, and based on what")]
for i, (n, t, d) in enumerate(_ap):
    y = 2.10 + i * 1.24
    card(s, 0.85, y, 11.6, 1.08)
    text(s, 1.10, y + 0.18, 1.2, 0.8, n, fs=28, font=DISP, colour=TAN)
    text(s, 2.30, y + 0.20, 6.0, 0.45, t, fs=15, font=SEMI, colour=INK)
    text(s, 2.30, y + 0.64, 8.5, 0.45, d, fs=10.5, colour=SAGE)

# ===================================================================== 16 · A1 otsu
s = content_slide("appendix · A1", "Otsu — how the camera picks its threshold", side="APPENDIX")
pic(s, os.path.join(FIGS, "otsu_hist.png"), 0.85, 2.05, 7.05, 4.55)
bullets(s, 8.20, 2.15, 4.25, 4.6, [
    ("WHY it exists", {"font": SEMI, "fs": 11.5}),
    "every frame must be split into “marker” and “not marker” — that takes "
    "one brightness number",
    ("WHAT it does", {"font": SEMI, "fs": 11.5}),
    "tries all 254 cuts, keeps the one giving the two tidiest groups — lands in the histogram's "
    "empty valley",
    ("THE CATCH", {"font": SEMI, "fs": 11.5}),
    "it follows the SCENE, not the markers — so the rig scores it against fixed values "
    "(auto-calibrate) instead of trusting it blindly",
], fs=10.5, gap=6)
text(s, 0.85, 6.90, 11.6, 0.3,
     "Otsu (1979), IEEE Trans. SMC 9(1):62–66 · measured here on 120 frames of specimen S13.",
     fs=9.5, colour=SAGE)

# ===================================================================== 17 · A2 materials
s = content_slide("appendix · A2", "Three materials — measured, against expectations",
                  side="APPENDIX")
pic(s, os.path.join(FIGS, "trio_curves.png"), 0.85, 1.98, 11.6, 2.95)
pic(s, os.path.join(FIGS, "petg_expect.png"), 0.85, 5.00, 9.10, 2.02)
bullets(s, 10.12, 5.06, 2.35, 2.0, [
    "ordering exactly as published",
    "TPU never fractured — it left the frame at 19 % strain",
], fs=9.5, gap=6)
# The bands on the chart are literature, not our data — so the sources are ON the slide, and
# clickable. UTS bands aligned 2026-09-06 with petg_data.LIT (PLA 32–60, PETG 30–50).
_LINK = RGBColor(0x2E, 0x6E, 0xA6)
text(s, 0.85, 6.98, 11.6, 0.50, [
    [("published ranges — PLA: ", {}),
     ("Chacón et al. 2017", {"url": "https://doi.org/10.1016/j.matdes.2017.03.065",
                             "colour": _LINK}),
     (" · ", {}),
     ("Tymrak et al. 2014", {"url": "https://doi.org/10.1016/j.matdes.2014.02.038",
                             "colour": _LINK}),
     (" · ", {}),
     ("Prusament PLA TDS", {"url": "https://prusament.com/materials/prusament-pla/",
                            "colour": _LINK})],
    [("PETG: ", {}),
     ("Durgashyam et al. 2019", {"url": "https://doi.org/10.1016/j.matpr.2019.06.082",
                                 "colour": _LINK}),
     (" · ", {}),
     ("Hsueh et al. 2021", {"url": "https://doi.org/10.3390/polym13111758",
                            "colour": _LINK}),
     (" · ", {}),
     ("Prusament PETG TDS", {"url": "https://prusament.com/materials/prusament-petg/",
                             "colour": _LINK}),
     ("   —   TPU: filament TDS + Hohimer et al. 2020, per the material notes.", {})],
], fs=8.8, colour=SAGE)

# ===================================================================== 18 · A3 noise
s = content_slide("appendix · A3", "How quiet is each instrument?", side="APPENDIX")
pic(s, os.path.join(FIGS, "mot2cmp_noise.png"), 0.85, 2.02, 8.15, 4.90)
bullets(s, 9.25, 2.15, 3.25, 4.6, [
    ("both rigs sit in the tens of microstrain", {"font": SEMI}),
    "our floor is set by pixel quantisation: noise ∝ 1/Px₀",
    "predicted 1.78× between our two gauge lengths — measured 1.78×",
    "so the noise is understood, not just small",
], fs=10.5, gap=7)

# ===================================================================== 19 · A4 camera
# Facts lifted from the Weekly's camera block (which reads them from code and captures):
# sensor 2448x2048, ROI [0, 988, 2348, 419] framed with roi_tool.py, 90-degree rotation,
# ~33 % strain travel budget, 50 ms exposure -> 19.9 fps measured, autocal sweep x0.3-x2.8.
s = content_slide("appendix · A4", "Camera properties — resolution & exposure",
                  side="APPENDIX")
card(s, 0.85, 2.10, 5.80, 4.30)
rect(s, 0.85, 2.10, 0.07, 4.30, TAN)
text(s, 1.12, 2.28, 5.3, 0.4, "RESOLUTION — chosen as a window", fs=13.5, font=SEMI,
     colour=INK)
bullets(s, 1.12, 2.80, 5.35, 3.5, [
    "the Basler sensor always runs full resolution, 2448 × 2048 px — no binning, no "
    "scaling anywhere",
    "what we SET is which pixels to read: ROI [offset 0, 988 · size 2348 × 419], framed "
    "with roi_tool.py so both markers sit inside with room to move; rotated 90° → the "
    "420 × 2348 recordings",
    "the ROI is ≈20 % of the sensor (0.98 of 5.0 Mpx) — every frame grabbed, tracked and "
    "written is ≈5× lighter, which is what keeps live DIC plus video recording comfortable "
    "in real time",
    "the value is a TRAVEL budget: at 2348 px a marker reaches the frame edge at ≈33 % "
    "strain — sharpness, scale and noise belong to the optics and exposure, not the ROI",
], fs=9.3, gap=5)
card(s, 6.85, 2.10, 5.80, 4.30)
rect(s, 6.85, 2.10, 0.07, 4.30, TAN)
text(s, 7.12, 2.28, 5.3, 0.4, "EXPOSURE — sets the frame rate", fs=13.5, font=SEMI,
     colour=INK)
bullets(s, 7.12, 2.80, 5.35, 3.5, [
    "each frame must be exposed before it can be delivered: at 50 ms per frame the ceiling "
    "is 1/0.050 s = 20 fps — the app may ask for 35, the camera delivers 19.9",
    "WHY: the requested rate is a ceiling, not a promise — the sensor cannot start sending "
    "a frame until it has finished gathering light for it, so the true rate is "
    "min(requested, 1/exposure); readout overhead shaves 20 to 19.9, and below 28.6 ms of "
    "exposure the full 35 would return",
    "the 19.9 is MEASURED from frame timestamps on every capture; the video container's "
    "declared 35 fps is never believed",
    "the value is chosen by Auto-calibrate: it sweeps ×0.3–×2.8 of the current exposure "
    "(15–140 ms), scores each setting on measured marker trackability, and proposes the "
    "winner — more light means stronger contrast but fewer frames per second",
], fs=9.3, gap=5)
text(s, 0.85, 6.65, 11.6, 0.4,
     "In short: resolution decides WHERE we look, exposure decides HOW OFTEN — both set "
     "once per rig geometry, by tools, not by hand. Full story: the Weekly deck's camera "
     "block.", fs=9.5, colour=SAGE)

# ---- page numbers = slide position, always (his rule 2026-09-07: no repeated numbers;
# ---- normalizes the old shared-"03" background block and any literal pagenos)
for _i, _s in enumerate(prs.slides):
    for _sh in _s.shapes:
        if _sh.has_text_frame and abs((_sh.left or 0) / 914400 - 12.55) < 0.1 \
                and abs((_sh.top or 0) / 914400 - 7.08) < 0.1:
            _runs = [r for p in _sh.text_frame.paragraphs for r in p.runs]
            if _runs and _runs[0].text.strip().isdigit():
                _runs[0].text = "%02d" % (_i + 1)
                for _r in _runs[1:]:
                    _r.text = ""

# ============================================================================ save
os.makedirs(SP, exist_ok=True)
prs.save(OUT)
import zipfile
with zipfile.ZipFile(OUT) as z:
    assert z.testzip() is None
    n = len([x for x in z.namelist() if x.startswith("ppt/slides/slide")
             and x.endswith(".xml")])
print("Saved: %s  (%d slides, zip verified)" % (OUT, n))
