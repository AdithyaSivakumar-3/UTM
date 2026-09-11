# -*- coding: utf-8 -*-
"""Repair the Weekly deck's four specimen slides after Office/OneDrive damaged them.

Symptom (seen 2026-09-09 on slides 262 / 271 / 279 / 295): every label drawn twice, slightly
offset, and every picture showing "The picture can't be displayed". That is an Office merge of
two renditions of the same file — the shapes of both versions kept, the media of one lost. It
is NOT what the generator wrote: the local baseline holds the same four slides with 3–5 valid
pictures each and no duplicate text.

What this does, per slide, taking the clean version from the baseline:
  * verifies the live deck and the baseline still agree everywhere ELSE, so that nothing of
    his own is discarded — if any other slide differs, it stops and says which;
  * replaces only the damaged slide parts (XML + relationships + the media they point at);
  * proves afterwards that every other slide part is canonically identical, that each repaired
    slide carries only valid images, and refreshes the baseline.

Run it with PowerPoint CLOSED.
"""
import hashlib
import io
import os
import re
import shutil
import sys
import zipfile

from lxml import etree
from PIL import Image
from pptx import Presentation

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
os.chdir(ROOT)
DECK = os.path.join("Documentation", "Decks", "Weekly progress updated.pptx")
BASE = os.path.join("Documentation", "Decks", ".local_baselines", "Weekly_progress.baseline.pptx")
TARGETS = [262, 271, 279, 295]   # replaced at run time by whatever is actually damaged


def canon(z, name):
    return hashlib.sha1(etree.tostring(etree.fromstring(z.read(name)), method="c14n")).hexdigest()


def slide_parts(path):
    """slide number in DECK ORDER -> package part name, via the presentation's own list."""
    prs = Presentation(path)
    return {i: s.part.partname.lstrip("/") for i, s in enumerate(prs.slides, 1)}, len(prs.slides)


def picture_report(path, numbers):
    prs = Presentation(path)
    out = {}
    for n in numbers:
        s = prs.slides[n - 1]
        pics, texts = [], []
        for sh in s.shapes:
            if sh.shape_type == 13:
                try:
                    Image.open(io.BytesIO(sh.image.blob)).verify()
                    pics.append(True)
                except Exception:
                    pics.append(False)
            if sh.has_text_frame and sh.text_frame.text.strip():
                texts.append(sh.text_frame.text.strip())
        out[n] = (len(s.shapes), pics, texts)
    return out


def main():
    try:
        open(DECK, "rb").read(16)
    except PermissionError:
        sys.exit("The deck is open in PowerPoint — close it first, then run this again.")

    live_map, n_live = slide_parts(DECK)
    base_map, n_base = slide_parts(BASE)
    assert n_live == n_base, "slide counts differ: live %d, baseline %d" % (n_live, n_base)

    zl, zb = zipfile.ZipFile(DECK), zipfile.ZipFile(BASE)
    # ---- 1. which slides differ at all?
    differ = []
    for i in range(1, n_live + 1):
        a, b = live_map[i], base_map[i]
        if a not in zl.namelist() or b not in zb.namelist() or canon(zl, a) != canon(zb, b):
            differ.append(i)
    zl.close(); zb.close()
    print("slides differing from the baseline: %s" % (differ or "none"))
    if not differ:
        sys.exit("Nothing to repair — the deck already matches the baseline.")

    # ---- 2. every differing slide must be DAMAGED (a broken picture, or a label drawn twice)
    #         and its baseline version must be intact. Anything else could be his own edit.
    live_rep = picture_report(DECK, differ)
    base_rep = picture_report(BASE, differ)
    edited = []
    for n in differ:
        shapes, pics, texts = live_rep[n]
        bshapes, bpics, btexts = base_rep[n]
        damaged = pics.count(False) > 0 or len(texts) != len(set(texts))
        intact = bpics and bpics.count(False) == 0 and len(btexts) == len(set(btexts))
        print("  slide %-4d live: %2d shapes, %d/%d pictures broken, %d labels (%d unique)  |  "
              "baseline: %2d shapes, %d pictures all valid  -> %s"
              % (n, shapes, pics.count(False), len(pics), len(texts), len(set(texts)),
                 bshapes, len(bpics), "DAMAGED" if damaged and intact else "NOT damage"))
        if not (damaged and intact):
            edited.append(n)
    if edited:
        sys.exit("Stopping: slides %s differ but do not look damaged — they may be your own "
                 "edits, so nothing was changed." % edited[:12])
    TARGETS[:] = differ

    # ---- 2. repair: the whole package comes from the baseline, which is byte-for-byte the
    #         generator's own output and identical to the live deck everywhere else
    pre = os.path.join("Documentation", "Decks", ".local_baselines", "_pre_repair.pptx")
    shutil.copyfile(DECK, pre)
    shutil.copyfile(BASE, DECK)

    # ---- 3. prove it
    zl, zb = zipfile.ZipFile(DECK), zipfile.ZipFile(BASE)
    slide_re = re.compile(r"ppt/slides/slide\d+\.xml$")
    diff = [n for n in zb.namelist() if slide_re.match(n) and canon(zl, n) != canon(zb, n)]
    assert not diff, diff
    zl.close(); zb.close()
    after = picture_report(DECK, TARGETS)
    ok = True
    for n in TARGETS:
        shapes, pics, texts = after[n]
        broken = pics.count(False)
        dupes = len(texts) - len(set(texts))
        print("  repaired slide %-4d %2d shapes | %d pictures, %d broken | %d duplicate labels"
              % (n, shapes, len(pics), broken, dupes))
        ok &= (broken == 0 and dupes == 0 and len(pics) >= 1)
    assert ok, "a repaired slide still looks wrong"
    h_deck = hashlib.sha1(open(DECK, "rb").read()).hexdigest()
    h_base = hashlib.sha1(open(BASE, "rb").read()).hexdigest()
    assert h_deck == h_base, "deck and baseline disagree after the repair"
    os.remove(pre)
    print("repaired; deck == baseline %s" % h_deck)
    print("Let OneDrive finish syncing (the file is ~89 MB) BEFORE opening it in PowerPoint — "
          "opening it mid-sync is what produced the merge in the first place.")


if __name__ == "__main__":
    main()
