# LOCAL README — the top level of this repository

> **The two map files, and the difference between them**
>
> - **LOCAL README** (this file) describes **only the folders at this level**. One line each,
>   no going inside them. Read it to find out which door to open.
> - **MASTER README** ([`MASTER_README.md`](MASTER_README.md)) describes **every folder and
>   every subfolder**, branch by branch, all the way down. Read it to find a specific file.
>
> A third file, [`PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md), is not a map: it describes the
> machine itself — what it is, the firmware, the bills of material, the DIC channel, and how
> to get the software running.

The project: a 1-D digital image correlation strain channel built onto the Department of
Product Development, Production and Design's desktop universal testing machine, validated
against a certified video extensometer and applied to printed polymers.

## Folders at this level

| folder | what is in it |
|---|---|
| `CAD/` | Every part designed for the rig: SolidWorks models, STEP and STL exports, print files, and photographs of the printed parts. |
| `Conferences-Seminars/` | Material from the seminars and department days attended during the project. Nothing here feeds the rig or the report. |
| `D32_Firmware/` | The ESP32 firmware that drives the motors and reads the load cell — a PlatformIO project, C++ sources. |
| `Documentation/` | Everything written or drawn about the project: the report, the slide decks, the posters, every figure, the scripts that generate them, and the literature read along the way. |
| `MOT Validation docs/` | The two laboratory sessions on the certified Zwick/Roell machine with the XT-205 video extensometer — the external validation this project rests on. |
| `Software/` | All the code: the PyQt6 application that runs the rig, the standalone analysis scripts, and the original MATLAB application the project started from. |
| `Test Search application/` | A small side utility for finding and checking reference URLs. Unrelated to the rig. |

## Files at this level

| file | what it is |
|---|---|
| `PROJECT_OVERVIEW.md` | The machine: firmware, software, hardware and electronics BOM, the DIC setup, getting started, and the conventions to know before changing anything. |
| `MASTER_README.md` | The full folder-by-folder map, including every subfolder. |
| `LOCAL_README.md` | This file. |
| `GEMINI.md` | Instructions for an AI agent working in this repository. It has to sit at the root to be found. |
| `LICENSE` | The licence. |
| `requirements.txt` | Python dependencies, grouped by what you want to do — read the comments before installing everything. |
| `.gitignore` | What git ignores: build output, caches, the app's `output/` folder, diagnostic images. |

## Where to start

- **To understand the machine** → `PROJECT_OVERVIEW.md`
- **To find a particular file** → `MASTER_README.md`
- **To read the result** → `Documentation/Final Report/UTM_DIC_Report.pdf`
- **To run the application** → `python "Software/UTM_PyQt6/app/main.py"` from the repository root
- **To see the status of every feature** → `Software/UTM_PyQt6/workflow/ROADMAP.md`
