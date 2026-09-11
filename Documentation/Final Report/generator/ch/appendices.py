# -*- coding: utf-8 -*-
"""Appendices A–G: registers and data tables behind the chapters."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "..", "..", "harvest", "registry_snapshot.json")


def _f(v, n=2, pct=False):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return "—"
    if pct:
        x *= 100.0
    return ("%%.%df" % n) % x


def _registry_rows():
    rows = json.load(open(REG, encoding="utf-8"))
    rows = [r for r in rows if r.get("specimen")]                 # drop unnamed trial rows

    def key(r):
        s = str(r["specimen"])
        try:
            n = int(s.lstrip("S"))
        except ValueError:
            n = 999
        return (n, str(r.get("date")))
    out = [("Specimen", "Material", "Infill %", "Gauge mm", "Date", "Test", "UTS MPa",
            "E GPa", "σy MPa", "εf %", "Anchor N")]
    for r in sorted(rows, key=key):
        out.append((r["specimen"], r.get("material", ""), _f(r.get("infill_pct"), 0),
                    _f(r.get("gauge_mm"), 0), str(r.get("date"))[:10],
                    (r.get("test") or "")[:22], _f(r.get("UTS_MPa")), _f(r.get("E_GPa"), 3),
                    _f(r.get("sy_MPa")), _f(r.get("ef"), 2, pct=True), _f(r.get("anchor_N"), 0)))
    return out


def build(R):
    # ------------------------------------------------------------------ A
    R.h1("Specimen register")
    R.p("The test registry (Smart Feature 14) as exported on 9 September 2026: one row per "
        "saved run, with the geometry and material entered at the rig, the test label, and "
        "the properties computed by the analysis module with the conventions of "
        "Section 3.9. Rows without a property value are non-destructive runs (cyclic, "
        "creep) or runs whose analysis was superseded. Two unnamed trial rows are omitted. "
        "{{tab:register}} is the register.",
        align="justify")
    R.tab(_registry_rows(), "The specimen register.", label="register",
          col_widths_cm=(1.5, 1.4, 1.2, 1.3, 1.9, 2.9, 1.5, 1.3, 1.4, 1.2, 1.4), font=7.5)

    # ------------------------------------------------------------------ B
    R.h1("Closed-loop test register")
    R.p("The runs behind Section 4.10, all on 50 % gyroid PLA with the 80 mm gauge, in the "
        "order they were made. T1 and T2 were the first staircase and relaxation sessions "
        "with the untuned loop; their overshoots are the *before* numbers ({{tab:tests}}).", align="justify")
    R.tab([
        ("Test", "Specimen", "Mode", "Settings", "Result"),
        ("T1", "S18", "Staircase", "Force steps, untuned", "Overshoot 45.5 / 46.8 / 52.6 N"),
        ("T2", "S18", "Relaxation", "Held strain 1.0 %", "Force 2 145 → 2 040 N"),
        ("T3", "S21", "Staircase, linear", "Tuned loop", "Overshoot 6.0 / 4.8 / 7.8 N"),
        ("T4", "S21", "Staircase, smooth", "Rate-limited approach", "Creep ≈400 N over 80 s hold visible"),
        ("T5", "S21", "Cyclic, triangle", "Peaks 500 N", "Peak error 71 N"),
        ("T6.3", "S21", "Cyclic, sine", "Peaks 500 N, retuned", "Peak error 15 N; 528 → 500 N convergence"),
        ("T6.4", "S22", "Cyclic, sine", "400–1 100 N, 8 cycles", "Camera lost at 145 s; 3 loops survive"),
        ("T6.5", "S22", "Cyclic, sine", "400–1 100 N, 8 cycles", "6 closed loops; area 14.2 → 10.9 kJ/m³; "
                                                                  "unload E 1.49 → 1.43 GPa"),
        ("T7.2", "S18", "Staircase → fracture", "Steps to failure", "21.19 MPa (virgin)"),
        ("T7.3", "S22", "Staircase → fracture", "After 16 cycles at 79 % UTS",
         "19.74 MPa, −6.8 % vs virgin; εf 3.60 %"),
        ("T8", "S21", "Progressive cyclic → fracture", "Rising amplitude", "21.38 MPa; crosshead vs DIC verdict"),
        ("T9a", "S23", "Creep baseline", "Zero load, 928 s", "Drift +0.289 µε/s; floor 26 µε"),
        ("T9b", "S23", "Creep", "600 N tared, 877 s", "Net +1 080 µε; Findley n 0.48; 62 % of crosshead was specimen"),
    ], "The closed-loop test register T1–T9.", col_widths_cm=(1.2, 1.6, 3.2, 3.6, 6.4), font=8.5,
       label="tests")

    # ------------------------------------------------------------------ C
    R.h1("Smart-feature index")
    R.p("Where each smart feature lives in the code and where its evidence is in the "
        "progress diary ({{tab:sfindex}}).", align="justify")
    R.tab([
        ("SF", "Feature", "Module", "Validated"),
        ("1", "DIC health HUD", "widgets.py, main.py", "rig, June 2026"),
        ("2", "Prepare specimen", "main.py", "rig, June 2026"),
        ("3", "Settings recipes", "utm_recipes.py", "rig, June 2026"),
        ("4", "Generate report", "utm_report.py", "rig, June 2026"),
        ("5", "Auto-stop at fracture", "main.py", "rig, June 2026"),
        ("6", "Strain-rate test", "control_policies.py", "rig, July 2026"),
        ("7", "Stall guard", "main.py, serial_manager.py", "rig, July 2026"),
        ("8", "Release load", "main.py", "rig, 27 July 2026"),
        ("9", "Advanced test modes", "control_policies.py", "rig, 9 August 2026 (T8 closed the set)"),
        ("10", "Auto-preload", "main.py", "rig, July 2026"),
        ("11", "Auto-metadata link", "main.py, utm_registry.py", "rig, 14 August 2026"),
        ("12", "DIC auto-calibration", "utm_autocal.py", "rig, 14 August 2026"),
        ("13", "Guided wizard", "utm_wizard.py", "rig, 18 August 2026"),
        ("14", "Test registry", "utm_registry.py", "rig, August 2026"),
        ("15", "Dead-DIC guard + backstops", "main.py", "rig, August 2026"),
        ("16", "Live Px₀ overlay", "widgets.py, utm_dic.py", "rig, August 2026"),
        ("17", "Video + image capture", "utm_capture.py, utm_capdlg.py", "rig, August 2026 (S26)"),
        ("18", "DIC post-processing", "utm_postdlg.py, utm_postproc.py", "rig + MOT footage, August 2026"),
        ("19", "Noise capture", "utm_noisedlg.py", "offline, September 2026"),
        ("20", "Manual blob selection", "utm_blobpick.py, utm_dic.py", "offline (9 tests on S13 frames), 5 Sept 2026"),
    ], "Smart features: module and validation.", col_widths_cm=(0.9, 3.8, 5.0, 6.3), font=8.5,
       label="sfindex")

    # ------------------------------------------------------------------ D
    R.h1("Data tables")
    R.p("{{tab:labcmp}}, {{tab:noise}} and {{tab:materials}} collect, in one place each, the "
        "numbers that Chapter 4 quotes for the laboratory comparison, for noise and "
        "scaling, and for the material comparisons.", align="justify")
    R.h2("Laboratory comparison")
    R.tab([
        ("Quantity", "PPD-UTM DIC", "XT-205", "Note"),
        ("Test 2 specimen", "S34 (45 mm gauge)", "XT205-S2 (45 mm)", "same batch"),
        ("UTS (MPa)", "48.34", "44.62", "−7.7 %"),
        ("σy 0.2 % (MPa)", "39.23", "39.61", "+1.0 %"),
        ("E (GPa)", "3.45", "3.23", "−6.4 %"),
        ("εf (%)", "5.25", "5.21", "−0.8 %"),
        ("Same-footage frames", "3 153", "3 153", "tare to fracture"),
        ("Same-footage εf (%)", "5.21", "5.22", "+0.08 %"),
        ("Same-footage scale", "0.99928", "1", "R² 0.9999964"),
        ("Same-footage offset", "−55 µε", "0", "0.069 px on 1 255 px"),
        ("Same-footage E (GPa)", "3.214–3.238", "3.23", "window spread"),
        ("Test 1 noise RMS (µε)", "23.5 / 23.6", "44.9", "80 mm gauge, two rig runs"),
        ("Test 1 median |r| (µε)", "12", "13 / 17", ""),
        ("Test 1 p95 |r| (µε)", "116", "45", ""),
        ("Test 1 strain rate (10⁻⁴/s)", "7.42", "2.67 / 4.06", "ratio 2.21×"),
        ("Crosshead motion reaching gauge", "19–29 %", "—", "elastic region"),
    ], "The laboratory comparison in full.", col_widths_cm=(4.6, 3.6, 3.4, 4.4), font=9,
       label="labcmp")
    R.h2("Noise and scaling")
    R.tab([
        ("Quantity", "Value"),
        ("Noise floor, 10 s window (S13 / S25 / S26)", "11.9 / 15.4 / 13.3 µε"),
        ("Noise floor, 900 s window", "26 µε"),
        ("Black specimen / white markers", "11.9 µε"),
        ("White specimen / black markers", "14.3 µε"),
        ("1/Px₀ scaling, predicted / measured", "1.78× / 1.78×"),
        ("Optical scale", "≈20.9 px/mm (≈48 µm per pixel)"),
        ("Reference span, 80 mm / 45 mm gauge", "1 675 px / 939 px (ratio 1.78)"),
        ("Modulus rule scatter, fixed window / steepest run", "PLA 16.0 / 9.6 % · PETG 13.8 / 11.3 % · TPU 5.3 / 1.2 %"),
        ("Lens and stand-off", "25 mm lens at ≈371 mm; 21.0 px/mm; 112 mm field"),
        ("Otsu vs fixed, S29 PETG", "48.5 % vs 99.5 % of frames"),
        ("Otsu vs fixed, S13 PLA", "99.8 % vs 99.8 %"),
        ("DIC delivery before ROI cut (S26 / S29 / S13)", "11.1 / 8.9 / 5.3 Hz"),
        ("Coverage, early VC-series (S24 / S13)", "27 % / 47 %"),
        ("Detect stage / sink stage cost", "≈1.4 ms / ≈47 µs per frame"),
    ], "Noise, scaling and pipeline numbers.", col_widths_cm=(8.5, 7.5), font=9, label="noise")
    R.h2("Materials")
    R.tab([
        ("Comparison", "Value"),
        ("PLA 100 % UTS coefficient of variation", "≈2.5 %"),
        ("S27 / S28 (50 %) UTS, εf, E", "19.87 / 19.91 MPa · 4.0 / 4.2 % · 1.22 / 1.26 GPa"),
        ("Infill knockdown 100 % → 50 %", "k ≈ 2.4 (UTS and E)"),
        ("Batch factor between 100 % batches", "1.05–1.24"),
        ("V6 batch (June) UTS", "S7 47.82 MPa; mean 45.81 MPa (−4.2 %)"),
        ("VC batch (August) εf vs V6", "1.7–2.5× larger"),
        ("PLA 45 mm gauge S33 / S34", "UTS 47.09 / 48.34 · E 3.17 / 3.45 GPa · εf 2.95 / 5.25 %"),
        ("PETG S30 / S31", "UTS 41.75 / 40.55 · E 1.81 / 2.12 GPa · εf 7.81 / 3.81 %"),
        ("TPU S35 / S36 / S37", "UTS 2.25 / 2.21 / 2.60 MPa (at travel limit) · E 0.025 / 0.025 / 0.024 GPa"),
        ("Fracture position (−1…+1)", "S13 .15 · S24 .03 · S25 .45 · S26 .77 · S27 .42 · S28 .22 · "
                                      "S30 .95 · S31 .90 · S33 −.12 · S34 .71"),
    ], "Material comparisons in full.", col_widths_cm=(6.0, 10.0), font=9, label="materials")

    # ------------------------------------------------------------------ E
    R.h1("Python workflow")
    R.p("**Where the code lives.** The initial reference for this work — the rig's frame, "
        "its electronics and the first control software — was obtained from the "
        "department's own UTM repository [[cenmir_utm]]. Everything this report describes "
        "was built on top of that starting point and lives in a repository of its own "
        "[[sivakumar_utm]]: the PyQt6 application, the 98 tests, the evidence scripts that "
        "compute every figure here, and the raw run data they read. The code was written in "
        "Visual Studio Code; the editor's own introduction to code editing "
        "[[vscode_editing]] is the shortest way in for anyone picking the project up.",
        align="justify")
    R.p("The application's module graph, scanned from the source with Python's abstract "
        "syntax tree on 6 September 2026. The full graph is {{fig:pytree_full}}; the live-test "
        "and evidence subgraphs are in Sections 3.4 and 3.12, and the developer tooling "
        "around the application is {{fig:pytree_tools}}. A separate workflow document "
        "with one page per module ships with the software.", align="justify")
    R.fig("pytree_full.png",
          "The complete import graph of the application and its tooling: 20 application "
          "modules (19 147 lines) and the test and evidence scripts around them.",
          width_cm=16.0, label="pytree_full")
    R.p("A live test flows through the graph as follows. The main window starts the serial "
        "thread and the camera thread. The camera thread configures the Basler camera "
        "through the camera manager, grabs frames, and calls the DIC module's detector on "
        "each; the strain goes back to the main window by signal. The serial thread polls "
        "force and position at the control period. The main window's state machine — "
        "idle, preload (auto-preload policy), running (the selected control policy), "
        "fracture (auto-stop), release — consumes both streams, drives the plots and the "
        "HUD, and on save writes the CSV, links the capture, adds the registry row and "
        "optionally builds the report. The post-processing dialog re-uses the camera "
        "manager's frame source abstraction with a video file in place of the camera and "
        "the same DIC module, which is why it measures the same way.", align="justify")
    R.fig("pytree_tools.png",
          "The developer tooling around the application: the 98 tests, the simulation "
          "plant the controllers were tuned on, and the registry and report command-line "
          "tools.", width_cm=16.0, label="pytree_tools")

    # ------------------------------------------------------------------ F
    R.h1("Carbon-footprint inventory")
    R.p("{{tab:pcfinv}} is the inventory behind Section 4.12, with every assumption stated.",
        align="justify")
    R.tab([
        ("Item", "Assumption", "Source"),
        ("Desk computer hours", "955 h of project desk time, February–September 2026", "calendar and session logs"),
        ("Desk computer power", "60 W average (laptop plus monitor)", "measured at the wall"),
        ("Printer", "60 prints at ≈84 Wh each = 5.04 kWh", "community-measured MK4S draw" +
         " " + R.cite("prusa_forum_power", "prusa_mk4s")),
        ("Rig", "7 h of motor-on time at 45 W = 0.315 kWh", "motor and driver rating; on-time from run logs"),
        ("AI agent", "195 h × 40 prompts/h × 0.24 Wh per prompt = 1.87 kWh", R.cite("google_ai_energy")),
        ("AI factor", "data-centre grid ≈0.38 kg/kWh; band 0.117–1.31 kg for the per-prompt uncertainty",
         "published range"),
        ("Grid factor", "0.040 kg CO₂e/kWh, Swedish average", R.cite("eea_grid")),
        ("Car equivalent", "107 g/km, average new European car", R.cite("eea_cars")),
        ("Excluded", "filament mass, camera and rig embodied carbon, travel, the laboratory session", "stated boundary"),
        ("Per-test", "3.22 kg / 39 recorded tests = 83 g; rig alone 13 g", "computed"),
        ("Thinking / pulling", "desk computer / rig = 239×", "computed"),
    ], "Carbon-footprint inventory and assumptions.", col_widths_cm=(3.2, 8.0, 4.8), font=9,
       label="pcfinv")

    # ------------------------------------------------------------------ G
    R.h1("AI collaboration in detail")
    R.p("The measured record behind Section 3.10: {{tab:commits}} gives the commits by area "
        "and {{tab:prompts}} what the prompts asked for.", align="justify")
    R.tab([
        ("Area", "Commits", "What the work was"),
        ("main.py", "90", "State machine, controls, plots, guards, the twenty features' UI"),
        ("documentation and evidence scripts", "53", "95 scripts, ≈30 000 lines; figures and deck builders"),
        ("camera_manager.py", "24", "pylon integration, ROI, exposure, sinks, latest-image strategy"),
        ("utm_postproc / utm_postdlg", "21", "Offline engine and the post-processing dialog"),
        ("utm_analysis.py", "14", "Fit window, yield, fracture detection, toughness"),
        ("tests", "8", "98 unit and offline tests"),
        ("utm_dic.py", "3", "The pixel-to-strain rule and the detector: small and stable"),
    ], "Commits by area, 28 May – 6 September 2026.", col_widths_cm=(4.6, 1.8, 9.6), font=9,
       label="commits")
    R.tab([
        ("Kind of task", "Share of prompts (approx.)", "Example"),
        ("Feature implementation", "35 %", "'Build the dead-DIC guard: freeze at 0.2 s, halt at 1.0 s'"),
        ("Analysis and figures", "30 %", "'Compare the post-processed strain with the XT-205 record frame by frame'"),
        ("Bug diagnosis from a rig observation", "15 %", "'The infill label says 100 % on a 50 % specimen after restart'"),
        ("Documentation, decks, roadmap", "15 %", "'Append the camera slides to the weekly deck; do not touch earlier pages'"),
        ("Review and verification", "5 %", "'Verify the 3.2 kg figure is reasonable; recompute from the inventory'"),
    ], "What the 853 prompts asked for. Shares are a classification of the conversation "
       "logs by the engineer and are approximate.", col_widths_cm=(4.6, 3.4, 8.0), font=9,
       label="prompts")
    R.p("Three rules kept the collaboration honest for a measurement project, and each "
        "caught at least one error: no number is typed (every figure is computed from the "
        "raw run by a committed script); the rig is the oracle (a feature is done when it "
        "behaves on the machine); and the agent's own reports are cross-checked (a "
        "container's frame count was decoded rather than trusted, a literature page range "
        "was checked against the running heads, a footprint total was recomputed by hand).",
        align="justify")
