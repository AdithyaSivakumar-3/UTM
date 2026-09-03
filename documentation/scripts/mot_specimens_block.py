# ===================================================================================
#  THE SIX RECORDS, NAMED — and the pull speed of each, which is not the same across
#  the two MOT tests and is the first thing to reach for when a slope differs.
#
#  Appended to generate_v6a_slides.py. Every speed is READ BACK from the records
#  (utm_analysis reports the measured crosshead rate for ours; the MOT tests have no
#  position channel, so theirs is the commanded figure and is labelled as such).
# ===================================================================================
import s25_s26_data as _NV                                            # noqa: E402
import mot2_data as _NM2                                              # noqa: E402
import mot_compare as _NM1                                            # noqa: E402
import mot2_pp_plots as _NRP                                          # noqa: E402
from utm_analysis import analyze as _nanalyze, read_csv as _nread      # noqa: E402

_MOT1_MM_MIN = 6.0        # 0.100 mm/s commanded; both machines were set to it for Test 1
_MOT2_MM_MIN = _NM2.load()["speed_mm_min"]

# our four runs, measured rather than commanded
_NSPD = {}
for _pair, _tags in (("80mm", ("S25", "S26")), ("45mm", ("S33", "S34"))):
    _NV.use_pair(_pair)
    for _t in _tags:
        _r = _nanalyze(_nread(_NV.csv_path(_t)), 80.0, _NV.RUNS[_t].get("gauge", 80.0))
        _NSPD[_t] = _r["rate"] * 60.0
_NV.use_pair("80mm")

# the gauge strain rates already computed for the two rate slides
_NR2 = {nm: st for nm, st, _c in _NRP.fig_rate()}
_NR1 = {r["key"]: r for r in __import__("json").load(
    __import__("io").open("documentation/mot_postproc_compare.json", encoding="utf-8"))["rows"]}


s = prs.slides.add_slide(BLANK); ju(s)
title(s, "THE SIX RECORDS, NAMED — AND THE SPEED EACH WAS PULLED AT")

tb(s, 0.45, 1.06, 12.5, 0.40,
   "Two tests on the MOT XT-205 and four pulls on the PPD-UTM. The MOT specimens had no names of "
   "their own, which made \"the XT-205\" mean the instrument and the bar it was holding at the "
   "same time. They have names now.",
   fs=11, colour=BLACK)

header(s, 0.45, 1.52, 12.5, "The naming")
table(s, 0.45, 1.90, 12.5, 1.13, [
    ["Name", "What it is", "Which test"],
    ["XT205-S1", "the specimen the MOT XT-205 pulled in its first session, 80 mm marker spacing",
     "MOT Test 1"],
    ["XT205-S2", "the specimen it pulled in its second, 45 mm marker spacing", "MOT Test 2"],
    ["XT-205", "the INSTRUMENT — the video extensometer and its software, not a specimen",
     "both"],
    ["PPD-UTM", "our rig, and the DIC pipeline that runs on it", "both"],
    ["S25 · S26 · S33 · S34", "our own printed bars, named as they are in the specimen registry",
     "—"],
], cw=[1.7, 7.3, 1.4], hf=9.5, bf=9)

header(s, 0.45, 3.60, 12.5, "…and the speed each one was pulled at — the two MOT tests do NOT match")
table(s, 0.45, 3.98, 12.5, 1.64, [
    ["Record", "Test", "Gauge", "Crosshead speed", "Source of that speed",
     "Gauge strain rate"],
    ["XT205-S1", "MOT Test 1", "80 mm", "%.2f mm/min  (0.100 mm/s)" % _MOT1_MM_MIN,
     "commanded — no position channel", "%.2e /s" % _NR1["mot"]["rate"]],
    ["S25 · PPD-UTM", "MOT Test 1", "80 mm", "%.2f mm/min" % _NSPD["S25"],
     "MEASURED from the rig's own channel", "%.2e /s" % _NR1["S25"]["rate"]],
    ["S26 · PPD-UTM", "MOT Test 1", "80 mm", "%.2f mm/min" % _NSPD["S26"],
     "MEASURED from the rig's own channel", "%.2e /s" % _NR1["S26"]["rate"]],
    ["XT205-S2", "MOT Test 2", "45 mm", "%.2f mm/min  (%.4f mm/s)"
     % (_MOT2_MM_MIN, _MOT2_MM_MIN / 60.0), "operator-reported — no position channel",
     "%.2e /s" % _NR2["XT205-S2 · XT-205 extensometer"][0]],
    ["S33 · PPD-UTM", "MOT Test 2", "45 mm", "%.2f mm/min" % _NSPD["S33"],
     "MEASURED from the rig's own channel", "%.2e /s" % _NR2["S33 · PPD-UTM"][0]],
    ["S34 · PPD-UTM", "MOT Test 2", "45 mm", "%.2f mm/min" % _NSPD["S34"],
     "MEASURED from the rig's own channel", "%.2e /s" % _NR2["S34 · PPD-UTM"][0]],
], cw=[1.6, 1.25, 0.85, 2.35, 3.1, 1.45], hf=9, bf=8.5)

header(s, 0.45, 5.74, 6.15, "Test 1 was speed-matched. Test 2 was not.")
tb(s, 0.45, 6.12, 6.15, 1.05,
   f"Both machines ran {_MOT1_MM_MIN:.0f} mm/min in Test 1, so a difference between them could not "
   f"be the speed. In Test 2 the XT-205 ran {_MOT2_MM_MIN:.0f} mm/min against the PPD-UTM's "
   f"{_NSPD['S34']:.2f} — a {_NSPD['S34'] / _MOT2_MM_MIN:.0f}× mismatch that was introduced "
   f"between the two MOT sessions and not by us.",
   fs=9.5, colour=BLACK)

header(s, 6.85, 5.74, 6.1, "Which is where a slope difference comes from")
tb(s, 6.85, 6.12, 6.1, 1.05,
   f"PLA is rate-sensitive: pull it faster and it reads stiffer and stronger. On the like-for-like "
   f"steepest-run modulus S34 reads 3.451 GPa against XT205-S2's 3.229 — the FASTER specimen is "
   f"the stiffer one, by 6.4 %, which is the direction rate predicts. It is a candidate, not a "
   f"proof: one PPD-UTM pull at {_MOT2_MM_MIN:.0f} mm/min would separate it from specimen scatter.",
   fs=9.5, colour=BLACK)

footer(s, "Our speeds are read back from each run's own position channel by utm_analysis, not "
          "restated from the recipe. The MOT tests log no position, so theirs are the commanded "
          "values and are marked as such.")
pageno(s)
