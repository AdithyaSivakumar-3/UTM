# ===================================================================================
#  EVERY SMART FEATURE ON ONE SLIDE — the poster page, at the end of the deck.
#
#  The deck already carries a card REGISTER early on (SF number + a 2-4 word tag) and
#  a slide per feature. This is neither: it is the one-page answer to "so what does
#  the rig actually do?", with a real sentence against every feature.
#
#  The list is _sf_cards itself, not a copy of it, so a renumber or a status change
#  reaches this page without anyone remembering to come back here. The sentences are
#  keyed BY NUMBER and every one is asserted present — a renumber that orphans a line
#  fails the build rather than silently printing the register's short tag instead.
# ===================================================================================
_SF_LINE = {
    1:  "Live badge on both test tabs: markers found, % frames tracked, pixel jitter.",
    2:  "One click tares load, position and strain together before a pull.",
    3:  "Save and reload a whole setup — camera, protocol, limits — as one recipe.",
    4:  "One click turns a finished run into a PDF report with the plots embedded.",
    5:  "Watches for load collapse and halts the motor at fracture on its own.",
    6:  "Closes the loop on strain rate, not crosshead speed — constant dε/dt.",
    7:  "Detects a motor commanded to move that is not moving, and halts.",
    8:  "Unloads to a true zero instead of leaving the specimen held in tension.",
    9:  "Six closed-loop protocols: monotonic, cyclic, programmable-cyclic, to fracture.",
    10: "Finds first contact in three slowing stages, 0.2 → 0.1 → 0.02 mm/s.",
    11: "Pairs each video with its CSV automatically, by timestamp overlap.",
    12: "Sweeps exposure × threshold and reports the setting that tracks best.",
    13: "Twelve-step guided setup for a new operator — optional, off by default.",
    14: "Every run recorded with its own force anchor, so a number can be traced back.",
    15: "Freezes the plot at 0.2 s without DIC, halts the test at 1.0 s.",
    16: "Draws the frozen Px₀ pair against the live pair, on the camera feed.",
    17: "PNG stills plus three AVI styles, with zero dropped frames on record.",
    18: "Re-measures any recorded video — ours or a foreign rig's — after the fact.",
    19: "Records the instrument at rest, so the noise floor is measured, not assumed.",
}
assert set(_SF_LINE) == {c[0] for c in _sf_cards}, "SF register and poster lines disagree"

_PF = {"done": (GREEN_PASS, DARK_GREEN), "built": (_SF_BUILT, DARK_GREEN),
       "plan": (LIGHT_BLUE, BLACK), "block": (YELLOW_WARN, BLACK)}

_PCOLS = 4
_PX0, _PY0 = 0.40, 1.52
_PW, _PH = 3.13, 0.99
_PGX, _PGY = 0.16, 0.08


def _sf_poster_card(slide, x, y, w, h, n, name, line, fill, edge, fg=None):
    """One card: the number and name on top in the status colour, the sentence under it.

    flow() puts a single run in the box, so the name and the sentence would have to share
    a size. At the size that fits 19 sentences on a page that makes the names unreadable
    as headings, which is the one thing someone scanning a poster needs.
    """
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                 Inches(x), Inches(y), Inches(w), Inches(h))
    box.fill.solid(); box.fill.fore_color.rgb = fill
    box.line.color.rgb = edge; box.line.width = Pt(1.2)
    tf = box.text_frame
    tf.margin_left = Inches(0.07); tf.margin_right = Inches(0.07)
    tf.margin_top = Inches(0.04); tf.margin_bottom = Inches(0.04)
    tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE

    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.LEFT; p.text = ""
    r = p.add_run()
    r.text = ("SF%d · %s" % (n, name)) if n else name
    r.font.size = Pt(10.0); r.font.bold = True; r.font.color.rgb = fg or edge
    r.font.name = "Calibri"

    p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.LEFT
    p2.space_before = Pt(1)
    r2 = p2.add_run(); r2.text = line
    r2.font.size = Pt(8.2); r2.font.bold = False; r2.font.color.rgb = BLACK
    r2.font.name = "Calibri"
    return box


s = prs.slides.add_slide(BLANK); ju(s)
title(s, "THE PPD-UTM AT A GLANCE — ALL %d SMART FEATURES" % len(_sf_cards))

tb(s, 0.42, 1.14, 12.5, 0.32,
   "Everything the rig does beyond pulling a specimen and logging force. "
   "GREEN = built and rig-validated · BLUE = built, offline-verified, awaiting rig time. "
   "Each has a slide of its own earlier in this deck.",
   fs=10.5, italic=True, colour=GREY_TEXT)

for _i, (_n, _name, _tag, _st) in enumerate(_sf_cards):
    _r, _c = divmod(_i, _PCOLS)
    _f, _e = _PF[_st]
    _sf_poster_card(s, _PX0 + _c * (_PW + _PGX), _PY0 + _r * (_PH + _PGY), _PW, _PH,
                    _n, _name, _SF_LINE[_n], _f, _e)

# 19 features in a 4 x 5 grid leaves exactly one slot — the safety layers go in it, because
# they are not an SF and have nowhere else to sit on a page that claims to be everything.
_r, _c = divmod(len(_sf_cards), _PCOLS)
_sf_poster_card(s, _PX0 + _c * (_PW + _PGX), _PY0 + _r * (_PH + _PGY), _PW, _PH,
                None, "ALWAYS ON — the safety net", "Four safety layers on every driven test: load collapse · "
                "stall guard · 4.5 kN / 30 mm · dead-DIC freeze.", WHITE, GREY_BORDER, fg=BLACK)

banner(s, 0.40, _PY0 + 5 * (_PH + _PGY) - _PGY + 0.07, 12.55, 0.42,
       "%d of %d done and validated on the rig · %d built and waiting on rig time · "
       "every one of them reachable from the two test tabs, no scripting required."
       % (_n_done, len(_sf_cards), _n_built),
       fill=GREEN_PASS, fg=DARK_GREEN, fs=11)
pageno(s)
