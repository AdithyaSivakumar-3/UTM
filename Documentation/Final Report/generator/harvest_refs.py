# -*- coding: utf-8 -*-
"""Harvest every reference link from the two decks for the bibliography.

Three sources per slide, so nothing hides: run-level hyperlinks (text links), shape-level
click hyperlinks, and bare URLs / DOIs sitting in plain text. Groups and tables are walked.
Output: documentation/report/refs_harvest.md (one row per unique target, with every slide
that cites it and the anchor text used) and refs_harvest.json for the build script."""
import json
import os
import re
import sys
from collections import OrderedDict

from pptx import Presentation

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
DECKS = {
    "W": os.path.join(ROOT, "Documentation", "Decks", "Weekly progress updated.pptx"),
    "P": os.path.join(ROOT, "Documentation", "Decks", "PPD_Final_Presentation.pptx"),
}
URL_RE = re.compile(r"(https?://[^\s\)\]\>\"']+|doi:\s*10\.\d{4,9}/\S+|\b10\.\d{4,9}/[^\s\)\]\>\"']+)",
                    re.I)


def norm(u):
    u = u.strip().rstrip(".,;:")
    if re.match(r"^doi:\s*", u, re.I):
        u = "https://doi.org/" + re.sub(r"^doi:\s*", "", u, flags=re.I)
    elif re.match(r"^10\.\d{4,9}/", u):
        u = "https://doi.org/" + u
    return u


def walk(shapes):
    for sh in shapes:
        if sh.shape_type == 6:
            yield from walk(sh.shapes)
            continue
        yield sh


found = OrderedDict()   # url -> {"slides": [...], "anchors": set()}


def add(url, tag, anchor):
    url = norm(url)
    if not url:
        return
    e = found.setdefault(url, {"slides": [], "anchors": set()})
    if tag not in e["slides"]:
        e["slides"].append(tag)
    if anchor:
        e["anchors"].add(anchor.strip()[:80])


for key, path in DECKS.items():
    prs = Presentation(path)
    for i, s in enumerate(prs.slides):
        tag = "%s%d" % (key, i + 1)
        for sh in walk(s.shapes):
            # shape-level click link
            try:
                a = sh.click_action.hyperlink.address
                if a:
                    add(a, tag, sh.text_frame.text if sh.has_text_frame else "")
            except Exception:
                pass
            frames = []
            if sh.has_text_frame:
                frames.append(sh.text_frame)
            if getattr(sh, "has_table", False) and sh.has_table:
                frames += [c.text_frame for r in sh.table.rows for c in r.cells]
            for tf in frames:
                for p in tf.paragraphs:
                    for r in p.runs:
                        if r.hyperlink and r.hyperlink.address:
                            add(r.hyperlink.address, tag, r.text)
                for m in URL_RE.finditer(tf.text):
                    add(m.group(1), tag, "")

# ---- write outputs
lines = ["# Reference links harvested from the decks", "",
         "W = Weekly slide, P = final-presentation slide. %d unique targets." % len(found), "",
         "| # | target | cited on | anchor text |", "|---|---|---|---|"]
out = []
for n, (url, e) in enumerate(found.items(), 1):
    anchors = "; ".join(sorted(e["anchors"])) or "(bare URL in text)"
    lines.append("| %d | %s | %s | %s |" % (n, url, ", ".join(e["slides"]), anchors))
    out.append({"n": n, "url": url, "slides": e["slides"], "anchors": sorted(e["anchors"])})
here = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "harvest")        # the artifacts live beside the report, not here
open(os.path.join(here, "refs_harvest.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
json.dump(out, open(os.path.join(here, "refs_harvest.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("\n".join(lines))
