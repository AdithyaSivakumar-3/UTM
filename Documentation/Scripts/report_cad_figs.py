# -*- coding: utf-8 -*-
"""Pull the CAD / design-process figures the report needs out of the Weekly progress deck.

The mechanical design record lives on Weekly slides 27–101: concepts, the rib and rail
decision matrices, the MDF Pugh matrix, the TPU pad, the assembly and the manufacturing
routes. Those pictures were made once, in the deck; rather than redraw them, the report
reuses them. This script copies the wanted pictures out of the deck's own package into
documentation/figures/cad/ so the report build has stable filenames.

Reads the BASELINE copy, never the live file, and writes nothing back to any deck.
"""
import os
import sys

from pptx import Presentation
from pptx.util import Emu

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
os.chdir(ROOT)
DECK = os.path.join("Documentation", "Decks", ".local_baselines", "Weekly_progress.baseline.pptx")
OUT = os.path.join("documentation", "figures", "cad")
os.makedirs(OUT, exist_ok=True)

# slide -> [(index of the picture on that slide, output name)]   index counts pictures only,
# in shape order, skipping the tiny JU watermark gif
WANTED = {
    39: [(0, "cad_utm_assembly.png")],
    49: [(0, "cad_cross_section.png")],
    50: [(0, "cad_concept_v1.png")],
    61: [(0, "cad_dot_template.png")],
    62: [(1, "cad_dot_results.png")],
    121: [(2, "cad_light_template.png")],
    124: [(0, "cad_light_assembly.png"), (1, "cad_light_part.png")],
    173: [(0, "cad_buck_enclosure.png")],
    80: [(0, "cad_housing_concepts.png")],
    81: [(0, "cad_rib_options.png")],
    82: [(0, "cad_rib_matrix.png")],
    88: [(0, "cad_rail_options.png")],
    89: [(0, "cad_rail_matrix.png")],
    91: [(0, "cad_basemount_v1.png"), (1, "cad_basemount_v2.png")],
    92: [(0, "cad_mdf_pugh.png"), (1, "cad_mdf_v1.png"), (2, "cad_mdf_v2.png")],
    94: [(0, "cad_tpu_pad.png")],
    100: [(0, "cad_mfg_mdf.png"), (1, "cad_mfg_carriage.png"),
          (2, "cad_mfg_rail.png"), (3, "cad_mfg_tpu.png")],
    101: [(0, "cad_assembly_cad.png"), (1, "cad_assembly_actual.png")],
}


def walk(shapes):
    for sh in shapes:
        if sh.shape_type == 6:
            yield from walk(sh.shapes)
        else:
            yield sh


def main():
    prs = Presentation(DECK)
    for n, wants in sorted(WANTED.items()):
        pics = []
        for sh in walk(prs.slides[n - 1].shapes):
            if sh.shape_type == 13:
                w, h = Emu(sh.width).inches, Emu(sh.height).inches
                if w < 0.9 or h < 0.35:          # the JU watermark and page furniture
                    continue
                pics.append(sh)
        for idx, name in wants:
            if idx >= len(pics):
                print("  slide %-4d %-28s MISSING (only %d pictures)" % (n, name, len(pics)))
                continue
            sh = pics[idx]
            blob = sh.image.blob
            p = os.path.join(OUT, name)
            with open(p, "wb") as f:
                f.write(blob)
            print("  slide %-4d %-28s %5d KB  %.1f x %.1f in"
                  % (n, name, len(blob) // 1024, Emu(sh.width).inches, Emu(sh.height).inches))


if __name__ == "__main__":
    main()
