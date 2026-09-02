# ===================================================================================
#  SF18 · the built-in guide, and the procedure it walks through.
#
#  Appended to generate_v6a_slides.py. The steps are READ FROM THE APP —
#  PostProcTab.GUIDE_STEPS — rather than retyped, so the deck and the tool cannot
#  drift apart. Importing utm_postdlg needs no QApplication; the steps are a class
#  attribute.
# ===================================================================================
import sys as _gsys                                                    # noqa: E402
import re as _gre                                                      # noqa: E402

_gsys.path.insert(0, "Software/UTM_PyQt6")
from utm_postdlg import PostProcTab as _GTab                           # noqa: E402

_GSTEPS = _GTab.GUIDE_STEPS


def _gplain(html):
    """The guide writes light HTML for the widget; slides want the words."""
    return " ".join(_gre.sub(r"<[^>]+>", "", html).split())


# ================================================================= 1. the guide itself
s = prs.slides.add_slide(BLANK); ju(s)
title(s, "SF18 · THE BUILT-IN GUIDE — THE PROCEDURE, IN THE TOOL")
img_fit(s, "documentation/figures/sf20_guide.png", 0.4, 1.20, 7.35, 3.55)

header(s, 8.0, 1.16, 4.95, "Why the tool carries its own instructions")
tb(s, 8.0, 1.54, 4.95, 1.70,
   "Post-processing has an order that matters and one step — the frame rate — that silently "
   "distorts everything if it is skipped. A procedure that lives in a document is a procedure "
   "nobody reads at the machine, so it lives in the tab: the Guide button beside Add video(s), or "
   "View ▸ Guided wizard ▸ DIC post-processing.",
   fs=10, colour=BLACK)

header(s, 8.0, 3.38, 4.95, "It follows what you have actually done")
tb(s, 8.0, 3.76, 4.95, 1.70,
   "Each step is ticked when the state it produces EXISTS — a video loaded, both boxes placed, a "
   "run finished — not when the reader was told to do it. So it doubles as a “what is left” "
   "indicator, and it cannot claim a step is done when it is not.\n"
   "It is modeless, so it stays open while you work, and “Follow my progress” switches itself off "
   "the moment you turn a page by hand.",
   fs=10, colour=BLACK)

banner(s, 0.4, 5.00, 7.35, 0.52,
       "Ticked · current · pending, at a glance. The window is a real screenshot, rendered by "
       "driving the widget — so it cannot go stale unnoticed.",
       fill=LIGHT_BLUE, fg=BLACK, fs=10)

header(s, 0.4, 5.68, 12.55, "The seven steps")
_gflow = " → ".join("%d %s" % (_i + 1, _t) for _i, (_t, _b, _p) in enumerate(_GSTEPS))
tb(s, 0.4, 6.06, 12.55, 0.72, _gflow, fs=11.5, bold=True, colour=DARK_GREEN)
footer(s, "The step list on these slides is read from PostProcTab.GUIDE_STEPS when the deck is "
          "built, not retyped — so the deck and the tool cannot say different things.")
pageno(s)


# ================================================================= 2-3. the steps themselves
for _half, (_lo, _hi, _sub) in enumerate((
        (0, 4, "SETTING IT UP"), (4, len(_GSTEPS), "MEASURING, AND TAKING THE RESULTS"))):
    s = prs.slides.add_slide(BLANK); ju(s)
    title(s, "SF18 · THE PROCEDURE — %s" % _sub)
    tb(s, 0.45, 1.12, 12.5, 0.34,
       "Steps %d–%d of %d, as the tool states them. The right-hand column is the part that is easy "
       "to get wrong." % (_lo + 1, _hi, len(_GSTEPS)),
       fs=11, italic=True, colour=GREY_TEXT)

    _rows = [["#", "Step", "What to do", "The part that catches people out"]]
    for _i in range(_lo, _hi):
        _t, _b, _tips = _GSTEPS[_i]
        _rows.append(["%d" % (_i + 1), _t, _gplain(_b), _gplain(_tips[0])])
    table(s, 0.45, 1.56, 12.5, 0.95 * len(_rows), _rows,
          cw=[0.34, 2.05, 5.15, 4.96], hf=10, bf=8.5)
    footer(s, "Read from the tool at build time. Every step's remaining notes are in the guide "
              "window itself — Guide, or Ctrl+Shift+P.")
    pageno(s)
