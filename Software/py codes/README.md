# Software/py codes/

Standalone analysis and plotting scripts, one per test series. These sat loose in the repository
root until 2026-08-25.

They are **scripts, not a package** — nothing imports anything else here, so each one can be read
and run on its own.

## Run them from the REPOSITORY ROOT

Every data and figure path inside these files is written relative to the repo root, e.g.
`"Software/UTM_PyQt6/Test data/Fracture tests/Specimen_S10_V2_Spray/UTM_Test_20260625_151046_V6c_TensionFailure.csv"`
and `"documentation/figures/V6a/V6a_stress_strain.png"`. That was true when they lived in the
root and it is still true now — moving the file did not move the working directory they expect.
The figure folders themselves moved once, from `images/` into `documentation/figures/`; the
paths above are the current ones.

> **Five of these scripts have lost their data.** The series folders under `Test data/` were
> renamed on 2026-09-10 (`8.6.20 - Tensile test to Failure` → `Fracture tests`,
> `Smart Features - Advanced Test Modes` → `… data`, `Trial for traverse markers` →
> `Trial for lateral strain`) and every path here was repointed, but 13 CSVs no longer exist
> anywhere in the repository: the eleven loose V2/V3 runs of June 2026 and two V4b/V4c
> staircase runs, which lived in an `8.6.3/` folder that is also gone. So
> `peak_strain_extraction.py` (11 references), `stress_strain_8_6_19.py`,
> `v4b_v4c_slope_plot.py`, `v4b_vs_v4c_compare.py` (2 each) and
> `staircase_engaged_analysis.py` (1) cannot run until that data is restored from a backup.
> Everything else here resolves.

```
cd  <repo root>
python "Software/py codes/v6_compare.py"
```

Running one from inside this folder will fail on the first data file it opens.

`v6_compare.py`, `v6_fracture_montage.py` and `v6_quintet_plots.py` additionally locate
`Software/UTM_PyQt6` from `__file__` in order to import `utm_analysis`; those paths were adjusted
for the new depth when the files moved.

## What is here

| script | series |
|---|---|
| `stress_strain_8_6_19.py`, `staircase_analysis.py`, `staircase_engaged_analysis.py` | 8.6.19 staircase |
| `v4b_v4c_slope_plot.py`, `v4b_vs_v4c_compare.py` | V4b / V4c linearity |
| `v5_full_analysis.py`, `v5_v5b_compare.py`, `v5abc_compare.py` | V5 and the V5a/b/c set |
| `v6_compare.py`, `v6_quintet_plots.py`, `v6_fracture_montage.py` | V6 quintet |
| `v6a_analyze.py`, `v6a_plots.py`, `v6a_epla_offset.py`, `v6a_offset_window.py` | V6a 100 % infill |
| `tensile_failure_analysis.py`, `peak_strain_extraction.py`, `preload_schedule.py`, `generate_report.py` | general-purpose |

`staircase_analysis.py` expects a CSV as its argument and exits 1 with a usage message without one.
That is by design, not a broken path.

## Related

- `Documentation/Scripts/*.py` — the slide builders, which have their own conventions and are run the same
  way, from the repository root.
- `Software/UTM_PyQt6/app/utm_analysis.py` — the shared analyser these scripts increasingly defer to.
  `v6a_plots.py` and `v6a_analyze.py` have not been migrated to it yet; see `ROADMAP.md`.
