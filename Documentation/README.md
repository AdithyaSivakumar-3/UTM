# Documentation/

The report, the slide decks, the posters, every figure in them, and the code that builds all
of it. The repository-wide maps are at the root: `MASTER_README.md` (every folder and
subfolder) and `LOCAL_README.md` (top level only).

| folder | what is in it |
|---|---|
| `Data/` | the computed caches the builders read: `estimator_measurements.json`, `mot_matched_points.csv`, `mot_postproc_compare.json`, `pxmm_reasoning.json` |
| `Decks/` | `Weekly progress updated.pptx` (the progress diary) and `PPD_Final_Presentation.pptx`, plus `small decks/` for the single-topic ones and `deck_png_gauge/` for text-fit renders |
| `Figures/` | every figure the builders read or write — see `Figures/README.md` |
| `Final Report/` | the report: `UTM_DIC_Report.docx` and `.pdf` at its root, with `generator/`, `pages/`, `sheets/`, `harvest/` and `notes/` beside them |
| `Posters/` | `Smart_UTM_poster_A0`, `Smart_UTM_poster_A4` and `Smart_UTM_progress_A4`, each as `.pptx` and `.pdf` |
| `Reference documents/` | the literature read during the project, plus `Literature/` and `AL profiles/` |
| `Scripts/` | 110 Python files — the deck and poster builders and the data/plot modules they import |
| `Todo md files/` | `PROJECT_REQUIREMENTS.md`, `Starting_TODO.md`, `TODO.md`, `VERSIONING.md` |

Nothing else belongs at this folder's root — figures go in `Figures/`, caches in `Data/`,
documents in their own folder.

## Run the builders from the REPOSITORY ROOT

```
cd  <repo root>
python Documentation/Scripts/generate_v6a_slides.py
```

Each builder `chdir`s to the repo root itself, so it works from anywhere — but its output lands
relative to that root, which is where the paths in this repo are all written from. The report
is the exception: it is built from its own folder,
`cd "Documentation/Final Report/generator" && python build_report.py`.

Nothing in `Scripts/` is a package. The builders import the data modules by bare name
(`import petg_data as PD`), which works because Python puts the running script's own directory on
the path, and they all live together. Keep them together. Of the 110 files, roughly 9 are
`generate_*` deck builders, 28 are `*_block` slide blocks the builders import, and the rest are
the `*_data` / `*_plots` modules plus the `wk_*` deck-surgery, `report_*` and `pcf_*` scripts.

## A missing figure does NOT fail the build

`pic_or_ph()` substitutes a placeholder box for an image it cannot find, so a broken path produces
a deck that builds cleanly, reports the right slide count, and is quietly wrong. **After moving or
renaming anything, rebuild and compare the PICTURE count**, not just the slide count:

```
python -c "from pptx import Presentation as P; d=P('Documentation/Decks/small decks/V6a_8_6_20_slides.pptx'); \
print(len(d.slides._sldIdLst),'slides', sum(1 for s in d.slides for sh in s.shapes if sh.shape_type==13),'pictures')"
```

Counts as measured on 2026-09-10, all of these now under `Decks/small decks/`:

| deck | slides | pictures |
|---|---|---|
| `E_modulus_explained.pptx` | 5 | 5 |
| `Learnings.pptx` | 18 | 9 |
| `UTM DIC Implementation.pptx` | 2 | 0 |
| `V2_capture_validation.pptx` | 11 | 8 |
| `V4_8_6_3_slides.pptx` | 5 | 1 |
| `V5_8_6_20_slides.pptx` | 9 | 5 |
| `V5abc_comparison_slides.pptx` | 7 | 5 |
| `V6a_8_6_20_slides.pptx` | 227 | 154 |

The two big decks in `Decks/` are edited surgically instead, by the `wk_*` scripts, which prove
every untouched slide is byte-identical before and after. Never rebuild `V6a_8_6_20_slides.pptx`
from scratch.

## Two traps worth knowing

**Paths are built three different ways.** Some modules hop from `__file__` to the repo root, some
prefix a folder constant onto a bare filename (`FROOT + r"\Specimen_S4\S4.jpg"`,
`os.path.join("documentation", "figures", name)`), and some rely on the working directory. A
search-and-replace that rewrites a *bare filename* into a full path will silently double any
prefix that was already there. Rebuild and check picture counts.

**Long paths.** This repo sits under a deep OneDrive path. An un-normalised
`.../Scripts/../../Software/...` can exceed Windows' 260-character limit and fail to open a file
that is plainly there. The root/APP constants are wrapped in `os.path.abspath()` for that reason —
keep it that way.

**Test data paths were repointed on 2026-09-10.** The series folders under
`Software/UTM_PyQt6/Test data/` were renamed (`8.6.20 - Tensile test to Failure` →
`Fracture tests`, `Smart Features - Advanced Test Modes` → `… data`, `Trial for traverse
markers` → `Trial for lateral strain`), which left 43 literals across 27 of these scripts
resolving to nothing. All of them now resolve. If a series folder is renamed again, the fix
is a substitution on the folder name plus a basename search for anything still broken.

**A note on case.** The scripts spell these folders in lowercase — `documentation/figures/...`,
`documentation/scripts/...` — from before the folders were capitalised. Windows does not care, so
everything resolves; a Linux or macOS checkout would. Worth normalising before this repo is
cloned anywhere else.
