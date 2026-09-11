# The Python workflow — how this project's code is structured

*The written half of the flowchart. The figures are drawn by `documentation/scripts/pytree_flow.py`, which parses the source with `ast` — the module list, the line counts and the import arrows are READ from the code, so the diagram cannot drift from the program. This file says the same thing in prose, with a sentence per module instead of a keyword.*

**At a glance:** 20 modules and 19 147 lines in the rig application, plus a second tree of 95 scripts (30 315 lines) that turns raw runs into figures and slides.

![The Python workflow](../../../documentation/figures/pytree_full.png)

A printable one-pager of the same diagram sits beside this file: `PYTHON_WORKFLOW.pdf`.

---

## 1. The shape of it

`main.py` owns the window and the run. Everything else is a role it calls into — and the two modules at the foot of the diagram are the reason the measurements can be trusted:

- **`utm_dic.py` (191 lines)** defines strain ONCE: ε = (L − L₀)/L₀. The live rig and the post-processor both call it, so they physically cannot disagree about what strain means.
- **`utm_analysis.py` (501 lines)** does the same for the properties — E, σy, UTS, ε_f and fracture detection — and serves the live run, the post-processor, the registry and the report alike.

That is the whole architectural idea: a small shared core, with everything else arranged around it by ROLE rather than by convenience.

---

## 2. Module by module

### Hardware & Sensing

| module | lines | what it does | imports |
|---|---|---|---|
| `camera_manager.py` | 992 | The DIC eye. Opens the Basler camera through pylon, applies the ROI and the specimen preset, runs the grab loop (LatestImageOnly), detects the two markers on every frame and emits live strain. Also carries the per-stage loop timing. | `utm_dic` |
| `serial_manager.py` | 380 | The link to the machine. Serial communication with the controller: motor commands out, load-cell and position stream back. | — |
| `utm_capture.py` | 565 | Recording. Lossless stills and/or an AVI, written OFF the hot path so that recording never costs strain samples. | — |

### Operator Dialogs

| module | lines | what it does | imports |
|---|---|---|---|
| `utm_camdlg.py` | 228 | Manual camera parameters, with a live trackability readout so a change can be judged before it is accepted. | `utm_autocal` |
| `utm_capdlg.py` | 321 | Capture setup: what to record, in which views, where it lands, and what it will cost on disk. | `utm_capture` |
| `utm_blobpick.py` | 144 | Manual marker selection (SF20) — pick the two markers by hand when automatic detection should not be trusted. | — |
| `utm_noisedlg.py` | 131 | Noise-capture setup: the rig measured at rest, which is how the noise floor is characterised. | — |
| `utm_wizard.py` | 273 | The guided checklist (SF13). Deliberately read-only: it reports state the app already has and can never act on the machine. | — |

### Measure & Control

| module | lines | what it does | imports |
|---|---|---|---|
| `control_policies.py` | 620 | The closed-loop engine. Auto-preload, ramps, dwells and the six test modes (creep, relaxation, staircase, cyclic, and the two fracture protocols). | `utm_analysis` |
| `utm_postdlg.py` | 3046 | The post-processing tab: load a recorded video, place a virtual extensometer, get strain back. | `theme`, `utm_postproc` |
| `utm_postproc.py` | 1740 | The measurement half of the post-processor — re-measures ANY recorded video the same way the rig measures it live, with the frame seek verified rather than trusted. This is the module that audited the commercial lab's own footage. | `utm_dic` |
| `utm_autocal.py` | 189 | DIC auto-calibration: sweeps exposure and threshold, scores each setting on measured trackability, and proposes the winner. | — |

### Data & Output

| module | lines | what it does | imports |
|---|---|---|---|
| `utm_recipes.py` | 286 | Test recipes — save and load a named setup (dimensions, specimen preset, preload, speed, mode and its parameters). | — |
| `utm_registry.py` | 221 | The test registry: one queryable index of every tensile test, scanned from the CSVs. | `utm_analysis` |
| `utm_report.py` | 251 | One-page tensile-test report — a standalone engine that turns one CSV into a PDF. | `utm_analysis` |
| `widgets.py` | 667 | Custom Qt widgets: toggle switches, gauges and the other controls the UI is built from. | — |
| `theme.py` | 300 | Dark and light theming for the app, including the plot styling. | — |

### Shared core

| module | lines | what it does | imported by |
|---|---|---|---|
| `utm_dic.py` | 191 | The shared DIC maths: strain from a marker pair, the health summary behind the live tracking badge, and multi-marker geometry. | `camera_manager`, `main`, `utm_postproc` |
| `utm_analysis.py` | 501 | The shared analysis: fracture detection and the property extraction (E, σy, UTS, ε_f) that every consumer uses. | `control_policies`, `main`, `utm_registry`, `utm_report` |

---

## 3. The live test path

![The live path](../../../documentation/figures/pytree_live.png)

1. `camera_manager.py` grabs a frame, rotates it, hands it to the sink, detects both markers and computes strain — at ≈20 fps MEASURED (the requested 35 never arrives, because a 50 ms exposure caps delivery at 20).
2. `utm_dic.py` turns the two centroids into ε = (L − L₀)/L₀ — pixels over pixels, so the units cancel and no calibration error can enter the strain.
3. `control_policies.py` decides what the motor should do next.
4. `serial_manager.py` says it, and streams the load cell back.
5. Force and strain are matched IN TIME before they become a point on the curve.

Because the driver uses `LatestImageOnly`, it discards whatever the loop cannot collect — so **the loop's own speed IS the DIC delivery rate**. That is why `camera_manager.py` times each stage of the loop (wait / rotate / sink / detect / strain / emit) on the running rig: a slow stage does not queue up, it silently costs strain samples.

---

## 4. The operator's tools, and what each run leaves behind

![Tools and outputs](../../../documentation/figures/pytree_tools.png)

Six dialogs cover the decisions made once per specimen — camera parameters, auto-calibration, manual marker picking, what to record, the noise capture and the guided checklist. After the pull, `utm_postproc.py` can re-measure the recording, `utm_registry.py` indexes the test, and `utm_report.py` turns one CSV into a one-page PDF.

---

## 5. The second tree — the evidence pipeline

![The evidence pipeline](../../../documentation/figures/pytree_evidence.png)

`documentation/scripts/` holds 95 scripts (30 315 lines), kept deliberately separate from the rig software:

- **~38 analysis and figure scripts** read the raw runs and compute the numbers.
- **~28 slide blocks** place those figures and their text into deck sections.
- **2 deck builders** assemble the Weekly diary and the final presentation.

The rule that makes it evidence rather than decoration: **no number is transcribed by hand.** Every figure is regenerated from the raw CSVs and videos on each build, and a slide quoting a number the scripts do not produce fails the build rather than shipping stale. The CSVs the rig writes are the ones the decks read.

---

## 6. Regenerating the diagrams

```
python documentation/scripts/pytree_flow.py
```

Writes `pytree_full.png`, `pytree_live.png`, `pytree_tools.png` and `pytree_evidence.png` into `documentation/figures/`. Add a module to the app and it appears in the diagram on the next run — only its one-line keyword caption needs adding to `KEY` in the script.

These four figures are also slides **390–393** of the Weekly progress deck.
