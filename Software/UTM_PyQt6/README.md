# Software/UTM_PyQt6/

The UTM DIC application. Start it from the **repository root**:

```
python "Software/UTM_PyQt6/app/main.py"
```

## Where the Python is

All 20 modules live in `app/`. They import each other by bare module name — `from
camera_manager import CameraManager` — which keeps working because Python puts the running
script's own directory on the path, and they all sit together in `app/`. They were loose in
this folder until September 2026; moving them into `app/` meant re-basing seven paths that
climb from `__file__` and repointing every `sys.path` line outside the app, but no import
inside it had to change.

| module | role |
|---|---|
| `app/main.py` | the window, the state machine, the control loop, the live plots and HUD, the CSV writer, the guards, and the UI of all twenty smart features |
| `app/camera_manager.py` | Basler capture, blob detection, DIC strain |
| `app/control_policies.py` | closed-loop test modes (strain rate, cyclic, staircase, …) |
| `app/serial_manager.py` | the link to the rig firmware |
| `app/theme.py` · `app/widgets.py` | look and custom controls |
| `app/utm_analysis.py` | the shared analyser: E, σ_y, UTS, ε_f, force anchor, fracture detection |
| `app/utm_autocal.py` · `app/utm_camdlg.py` | auto-calibration and DIC camera setup |
| `app/utm_blobpick.py` | manual marker selection, for when automatic detection cannot win |
| `app/utm_capture.py` · `app/utm_capdlg.py` | frame/video capture and its setup dialog |
| `app/utm_dic.py` · `app/utm_wizard.py` | the pixel-to-strain rule and the guided wizard |
| `app/utm_noisedlg.py` | the noise-floor measurement |
| `app/utm_postproc.py` · `app/utm_postdlg.py` | DIC post-processing: strain from a RECORDED video, and its tab |
| `app/utm_recipes.py` | saved settings profiles (`recipes/`) — Default, TPU |
| `app/utm_registry.py` · `app/utm_report.py` | the test registry and the one-click per-test report |

## Folders

| folder | what |
|---|---|
| `Test data/` | every test CSV and its per-specimen folder — see below |
| `Test Scripts/` | 15 test scripts; five run offline, the rest need the camera or the rig |
| `app/` | the 20 application modules, above |
| `output/` | everything the app and its tools WRITE: `captures/`, `diagnostics/`, `full_frame_output/`, `setup_output/`, `test_images/`. Gitignored in one line |
| `recipes/` | saved settings profiles, seeded on first launch (Default, TPU) |
| `tools/` | diagnostic and build scripts — ROI picker, blob checker, DIC replay, control-loop simulation, exe build |
| `ui/` | the Qt Designer `.ui` file, and `ui/help/` — the six mode-help images |
| `workflow/` | ROADMAP, TESTING_TODO, TEST_FAILURES, RECALIBRATE_ROI, COMMANDS, PYTHON_WORKFLOW, and the code summary |

`registry.json` and `requirements.txt` sit at this folder's root, beside this file.

`CAPTURE_ROOT`, the `.ui` path, `ui/help` and `RECIPES_DIR` are all built from `__file__`, and
since the modules moved into `app/` each of them now climbs one level first — the resources
did **not** move. A wrong one does not raise; it points at a directory that is not there, and
the symptom is a capture that never appears or a help image that is blank. If you move any of
these, check `app/main.py` (`UI_FILE`, `CAPTURE_ROOT`, the `ui/help` lookup),
`app/utm_recipes.py` (`RECIPES_DIR`), `app/utm_registry.py` (`DEFAULT_REGISTRY`, `REPO_ROOT`)
and `app/utm_report.py` (the reports folder).

## Running anything in `tools/` or `Test Scripts/`

From **this** directory, not from inside the subfolder:

```
cd Software/UTM_PyQt6
python tools/dic_replay.py
```

Their data and output paths are relative to this directory, and the ones that import app
modules carry a two-line header putting `app/` on `sys.path`.

The five that run with no hardware at all: `test_threshold.py`, `test_postproc_guards.py`,
`test_scale_sidecar.py`, `test_multipair_postproc.py`, `test_plot_cursor.py`. There is no
pytest suite — each is a script that exits non-zero on failure.

## DIC post-processing (the fourth tab)

Measures strain from a **recorded video** — ours, or a specimen filmed on the MOT XT-205 video
extensometer — so the two instruments can be compared on the same footing.

Load a video, place two tracking boxes on the speckle (or press Auto-detect for sprayed dots),
press Run. The strain-vs-time plot builds on the right as it goes.

**The strain maths is not re-implemented.** `utm_postproc` calls `utm_dic.dic_strain()`, and so
does the live camera path in `camera_manager.calculate_dic_strain()`. Strain is a pixel ratio —
`(L − L₀)/L₀` — with no gauge, calibration or unit in it, so a pull and the same pull replayed
from its recording must not be able to disagree.

Two things it gets right that are easy to get wrong:

- **Tracking is against the REFERENCE patch, not the previous frame.** Frame-to-frame tracking
  accumulates drift, and over 1682 frames a fraction of a pixel per frame exceeds the strain being
  measured. When correlation falls below the floor it re-seeds and FLAGS that frame rather than
  silently accumulating error.
- **Frame rate is measured, not believed.** Every video this rig has produced declares 35 fps in
  its container; S26 and S35 actually ran at 19.93 and S37 at 33.55. On load the tab reads the
  true rate from the capture folder's `frames/index.csv` (or `run.json`) and says where it got it.
  Videos from another camera have no sidecar, and the tab says so instead of assuming.

**Comparing several videos.** Add any number; each keeps its own extensometer, frame rate, box
size and tracking method, because two videos never have their markers in the same place and an
extensometer recording shares neither the frame rate nor the scale of ours. `Run all pending`
measures them one after another and every completed run stays on the plot with its own colour and
legend label. That is how an extensometer recording is put beside one of ours on the same axes,
measured with the same pixel-to-strain rule.

**Tracking method** is selectable, and the choice matters when comparing:

| mode | what it does | when |
|---|---|---|
| intensity-weighted centroid | contour selects the marker, intensity weights the centre | default — most precise |
| binary centroid | exactly what `camera_manager` does | comparing against a live run: removes the estimator as a variable |
| correlation | matches the pattern, no marker needed | speckle; chosen automatically when no marker is found |

Measured on S25/S26 over a matched strain window: intensity-weighted 15–17 µε, binary ~25 µε,
live rig 28 µε. Note the box size dominates all of it — a 24 px half-box on a 60 px dot gives
313 µε, because it sees only flat interior. Auto-detect and snapping now size the box to the marker.

Validated against S26: post-processing its `video.avi` reproduces that run's own live DIC to
**273 µε RMS over a 5.6 % strain range** (~0.5 % of reading), with L₀ agreeing to 0.005 %.

## Test data

Everything lives under **`Test data/`**, in three folders:

| folder | what |
|---|---|
| `Test data/Fracture tests/` | the tensile-to-fracture campaign — 29 runs, one folder per specimen (`Specimen_S<n>_…`), each holding the CSV, its generated report/plots, and the frame-capture folder if the run recorded one |
| `Test data/Smart Features - Advanced Test Modes data/` | the closed-loop protocol runs — 12 of them: cyclic, staircase, relaxation, creep, progressive cyclic |
| `Test data/Trial for lateral strain/` | the Poisson's-ratio trial, `S38` and `S39` |

**`registry.json` records every test by path**, and the deck builders and the poster read those
same paths, so a rename here invalidates all of them at once. The check is one line, run
**from the repository root** — the paths in `registry.json` are stored relative to the root, so
from this directory every one of them looks missing:

```
python -c "import json,os; r=json.load(open('Software/UTM_PyQt6/registry.json')); print(sum(1 for x in r if not os.path.isfile(x['csv'])),'unresolved of',len(r))"
```

That must print `0 unresolved`, and as of 2026-09-10 it does. It printed `36 unresolved of
36` earlier that day: the three series folders had been renamed (`8.6.20 - Tensile test to
Failure` → `Fracture tests`, `Smart Features - Advanced Test Modes` → `… data`,
`Trial for traverse markers` → `Trial for lateral strain`) while the rows still pointed at
the old names. All 36 were repointed by basename. Repoint the same way if it ever breaks
again — by searching for each CSV's **basename** rather than assuming where the folder went — specimen folders get renamed too
(S37's gained a `_Video15` suffix after its run, which broke its row and a hard-coded path in
the deck scripts).

**The CSVs themselves are gitignored** (`*.csv`), as are the capture folders (`**/frames*/`,
`*.avi`, `*.mkv`, `*.tif`) — one specimen's stills run to 1.7 GB, and the tree as a whole is 54 GB.
What IS committed per specimen is the small stuff: `run.json`, the generated report PDF/PNGs, and
photographs. So the folder structure is in git while the bulk data stays local.
