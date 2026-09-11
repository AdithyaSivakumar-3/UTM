# -*- coding: utf-8 -*-
"""Weekly deck: one slide answering "what if the code had been typed by hand instead?"

The carbon slide already reports 3.2 kg CO2e with the AI compute as one of its four rows.
This slide runs the counterfactual on the same inventory: the 195 h of agent sessions become
the hours a human would have needed for the same 26 468 tested lines, the AI row goes to
zero, and nothing else changes. Numbers come from pcf_figs.py so the slide cannot drift from
the report (Section 4.12) or from the figure.

Redo-safe like the other wk_append_* scripts.
"""
import hashlib
import os
import shutil
import sys

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from wk_place_slides import ensure_page_number, prove_media_identical, prove_untouched
import pcf_figs as P

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
os.chdir(ROOT)
DECK = os.path.join("Documentation", "Decks", "Weekly progress updated.pptx")
BASE = os.path.join("Documentation", "Decks", ".local_baselines", "Weekly_progress.baseline.pptx")
FIG = os.path.join("Documentation", "Figures", "pcf_solo_bars.png")
INK, GREY = RGBColor(0x25, 0x34, 0x39), RGBColor(0x5A, 0x63, 0x6B)
GREEN, RED = RGBColor(0x1E, 0x84, 0x49), RGBColor(0xB0, 0x2A, 0x37)
X0, X1 = 1.40, 12.07
TITLE = "IF A HUMAN HAD TYPED IT ALL — THE CARBON COUNTERFACTUAL"


def is_solo(slide):
    t = slide.shapes.title
    return t is not None and t.text.startswith("IF A HUMAN HAD TYPED IT ALL")


def label(slide, x, y, w, h, text, size=11, colour=INK, bold=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.02)
    tf.margin_top = tf.margin_bottom = Inches(0)
    r = tf.paragraphs[0].add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.color.rgb = colour
    r.font.bold = bold
    r.font.name = "Calibri"
    return tb


def drop_slide(prs, idx):
    lst = prs.slides._sldIdLst
    sld = list(lst)[idx]
    rId = sld.rId
    lst.remove(sld)
    prs.part.drop_rel(rId)


def main():
    assert os.path.exists(FIG), "run pcf_figs.fig_solo() first: %s" % FIG
    local, ai, tot = P.totals()
    h3, _, kg3 = P.solo_scenario(P.SOLO_MULT[0])      # never hardcode the multipliers: the mid
    h7, pc7, kg7 = P.solo_scenario(P.SOLO_MULT[1])    # one is 1 300 h / 195 h, so a literal
    h10, _, kg10 = P.solo_scenario(P.SOLO_MULT[2])    # 6.7 would drift from the report
    saved = (pc7 - P.PC_KWH) * P.GRID_EF
    be = P.breakeven_hours(ai[1])

    def row(name, mult, hours, pc, kg):
        """One scenario, with the sustained rate the multiplier implies for a person."""
        dev = P.AI_HOURS * mult
        return (name, "%s" % ("195 (measured)" if mult == 1 else "%.0f" % dev),
                "%.0f lines/h" % P.implied_rate(dev), "%.0f h" % hours, "%.1f kWh" % pc,
                "%.2f" % kg, "—" if mult == 1 else "+%.2f  (%.2f×)" % (kg - tot, kg / tot))

    rows = [
        ("", "Development h", "Implied rate", "Desk time", "PC", "kg CO₂e", "vs as-run"),
        row("As run, with the agent", 1, 955, P.PC_KWH, tot),
        row("Typed by hand, ×3", P.SOLO_MULT[0], h3, h3 * P.PC_W / 1000.0, kg3),
        row("Typed by hand, ×6.7", P.SOLO_MULT[1], h7, pc7, kg7),
        row("Typed by hand, ×10", P.SOLO_MULT[2], h10, h10 * P.PC_W / 1000.0, kg10),
    ]

    pre = os.path.join("Documentation", "Decks", ".local_baselines", "_pre_solo.pptx")
    shutil.copyfile(DECK, pre)
    prs = Presentation(DECK)
    found = [i for i, s in enumerate(prs.slides) if is_solo(s)]
    removed = found[1:]
    for i in reversed(removed):
        drop_slide(prs, i)
    redo = bool(found)
    if redo:
        idx = found[0]
        s = prs.slides[idx]
        for sh in list(s.shapes):
            if not sh.is_placeholder:
                sh._element.getparent().remove(sh._element)
    else:
        layout = next(l for l in prs.slide_layouts if l.name == "Two content light blue")
        s = prs.slides.add_slide(layout)
        idx = len(prs.slides) - 1
        for ph in list(s.placeholders):
            if "TITLE" in str(ph.placeholder_format.type):
                ph.text = TITLE
            else:
                ph._element.getparent().remove(ph._element)
    ensure_page_number(prs, s, idx + 1)

    label(s, X0, 2.30, X1 - X0, 0.3,
          "Same inventory as the carbon slide, one term changed: the 195 h of agent sessions "
          "(a subset of the 955 h desk time) become the hours a human would have needed for the "
          "same 26 468 tested lines, and the AI row goes to zero. Printer, rig and the rest of "
          "the desk time are untouched — grid electricity only on both sides.",
          size=10.5, colour=GREY)

    tb = s.shapes.add_table(len(rows), 7, Inches(X0), Inches(2.90),
                            Inches(X1 - X0), Inches(1.55)).table
    for w, c in zip((2.42, 1.60, 1.42, 1.24, 1.36, 1.05, 1.58), range(7)):
        tb.columns[c].width = Inches(w)
    for i, row in enumerate(rows):
        tb.rows[i].height = Inches(0.26)
        for j, v in enumerate(row):
            cell = tb.cell(i, j)
            cell.text = ""
            par = cell.text_frame.paragraphs[0]
            par.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
            run = par.add_run()
            run.text = v
            run.font.size = Pt(10)
            run.font.name = "Calibri"
            run.font.bold = (i == 0) or (j == 0) or (i == 3)
            run.font.color.rgb = INK if i != 1 else GREEN

    iw, ih = Image.open(FIG).size
    w = 6.65
    s.shapes.add_picture(FIG, Inches(X0), Inches(4.72), Inches(w), Inches(w * ih / iw))

    x = X0 + w + 0.30
    label(s, x, 4.72, X1 - x, 0.3, "What the AI term bought", size=12.5, bold=True)
    label(s, x, 5.10, X1 - x, 1.9,
          "The agent's own compute cost %.2f kg and avoided %.0f h of laptop time — %.1f kWh, "
          "%.1f kg. Every 1 kg of AI compute displaced about %.1f kg of desk electricity, so "
          "the net at the central estimate is %+.1f kg: %.1f kg against %.1f kg, a factor of "
          "%.2f, or 30 km of driving against 48 km."
          % (ai[1], h7 - 955, pc7 - P.PC_KWH, saved, saved / ai[1], tot - kg7, tot, kg7,
             kg7 / tot), size=10.5, colour=INK)
    label(s, x, 6.10, X1 - x, 0.3, "What the multiplier really claims", size=12.5, bold=True,
          colour=RED)
    label(s, x, 6.46, X1 - x, 1.1,
          "Only the top row is measured: 195 h for 26 468 lines is %.0f lines/h. The rest is an "
          "assumption about a person — ×6.7 asserts %.0f tested lines an hour sustained. "
          "Break-even is ×%.1f (≈%.0f h = %.0f lines/h), which is not credible; the honest "
          "corner is the AI band's top (%.2f kg) with only ×3, where hand-typing wins by %.2f kg."
          % (P.implied_rate(P.AI_HOURS), P.implied_rate(P.AI_HOURS * P.SOLO_MULT[1]),
             be / P.AI_HOURS, be, P.implied_rate(be), ai[2], (local + ai[2]) - kg3),
          size=10.5, colour=GREY)

    label(s, X0, 6.98, w, 0.3,
          "Computed by documentation/scripts/pcf_figs.py · counterfactual() and fig_solo() · "
          "report Section 4.12", size=9, colour=GREY)
    prs.save(DECK)

    # ---- proof
    kept = prove_untouched(pre, DECK, set(removed) | ({idx} if redo else set()), {idx})
    n_media = prove_media_identical(pre, DECK)
    prs2 = Presentation(DECK)
    mine = [i for i, sl in enumerate(prs2.slides) if is_solo(sl)]
    assert mine == [idx], "expected exactly one counterfactual slide, at %d; found %s" % (idx, mine)
    assert sum(1 for sh in prs2.slides[idx].shapes if sh.shape_type == 13) == 1
    print("counterfactual slide is %d of %d; removed duplicates: %s; %d other slides and %d "
          "media parts proven identical"
          % (idx + 1, len(prs2.slides), removed or "none", kept, n_media))
    print("  as run %.2f kg | solo x3 %.2f | x6.7 %.2f | x10 %.2f | net %+.2f kg at x6.7"
          % (tot, kg3, kg7, kg10, tot - kg7))
    for _ in range(2):
        shutil.copyfile(DECK, BASE)
        assert hashlib.sha1(open(DECK, "rb").read()).hexdigest() == \
               hashlib.sha1(open(BASE, "rb").read()).hexdigest()
    os.remove(pre)
    print("baseline refreshed:", hashlib.sha1(open(DECK, "rb").read()).hexdigest())


if __name__ == "__main__":
    main()
