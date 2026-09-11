# Documentation/Figures/

Every figure the report, the decks and the posters read or write. 158 PNGs and 9 JPGs sit at
this folder's root — the current figures, written by the scripts in `Documentation/Scripts/` —
and the subfolders below hold the ones that belong to a particular test series or purpose.

These lived loose in the repository root until 2026-08-25, then in a root `images/` folder, and
moved here in September 2026. The names always said which series they belonged to; the folders
just make that visible.

| folder | what is in it |
|---|---|
| `JTH Black/` | Jönköping University logos — EPS, SVG, PNG and JPG |
| `UTM rig/` | hardware and UI: the GUI, the rig schematic, the dimensioned drawing, the buck-converter enclosure render. Embedded in the root `PROJECT_OVERVIEW.md` and `Documentation/Todo md files/PROJECT_REQUIREMENTS.md` |
| `V4/` | 8.6.19 / 8.6.3 staircase and linearity series |
| `V5/` | 8.6.20 V5 tensile-to-failure, and the V5a/b/c comparison set |
| `V6/` | V6 quintet — ductility, fracture patterns, offset factor, repeatability |
| `V6a/` | V6a 100 % infill series, including the V6a-vs-V5 overlays |
| `cad/` | the design figures extracted from the deck for the report's CAD chapter |
| `features/` | `feat_*` — proof figures for the app's smart features (auto-stop, strain rate, DIC halt …), plus the UI screenshots |
| `thresholding/` | the `binary_*.png` sweep — one frame at six threshold values |
| `wk_specimens/` | specimen photographs used across the weekly deck |

## If you move one of these

The scripts `chdir` to the repository root, so every reference is a path from the root such as
`"documentation/figures/V6a/V6a_stress_strain.png"`. Grep for the filename before moving it — and
note that `pic_or_ph()` in the deck builders substitutes a PLACEHOLDER BOX for a missing image
rather than failing, so a broken path produces a deck that builds cleanly and is quietly wrong.

That is not hypothetical: the move out of `images/` left 82 dangling references behind, in the
V4/V5/V6/V6a builders, in `Software/py codes/` and in the poster blocks. All were repointed and
all 203 figure paths in those scripts now resolve, but the lesson stands — after any move,
rebuild and check the picture count is unchanged:

```
python Documentation/Scripts/generate_v6a_slides.py
python -c "from pptx import Presentation; p=Presentation('Documentation/Decks/small decks/V6a_8_6_20_slides.pptx'); \
print(sum(1 for s in p.slides for sh in s.shapes if sh.shape_type==13), 'pictures')"
```

Measured 2026-09-10, that deck is **154 pictures across 227 slides**; `Documentation/README.md`
lists the counts for the rest. (The report has its own check: it prints its figure count on
every build — 81 at present.)

## Naming

`report_*` figures are drawn for the report, `wk_*` for the weekly deck, `ppd_*` for the final
presentation, `sf_*` for the posters and smart-feature proofs, `mot*` for the laboratory
comparison, and `pcf_*` for the carbon footprint. A figure with no prefix predates the
convention.
