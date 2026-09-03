"""Build the MOT bench documents for a 45 mm gauge session, into Validation docs/MOT Test 2.

Test 1 compared S25 and S26 at 80 mm marker spacing. This session repeats that comparison at
45 mm, and S33/S34 are the right reference for it: same PLA, same rig, same capture feature armed,
and the only variable moved is how far apart the two markers sit. Anything else — a different
specimen batch, a different day — would confound the one thing being checked.

Nothing here is a fork of the Test 1 generators. They iterate D.ORDER and read a session config,
so this file only says WHICH pair and writes the output somewhere else.

    python documentation/scripts/mot_session_45mm.py
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

OUT_DIR = os.path.join(REPO, "Validation docs", "MOT Test 2")
PAIR = ("S33", "S34")
GAUGE_MM = 45.0
REF_PDF = "S33_S34_stress_strain_reference.pdf"
PACK_PDF = "MOT_extensometer_validation_pack_45mm.pdf"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    import s25_s26_data as D
    D.use_pair("45mm")
    print("pair: %s at %.0f mm marker spacing" % (", ".join(D.ORDER), GAUGE_MM))

    # ---- the numbers, printed here as well as into the PDFs, because a build that quietly
    # ---- produced the wrong pair's figures would look identical from the outside.
    for tag in D.ORDER:
        r = D.summary(tag)
        print("   %-4s UTS %6.2f MPa   E %5.3f GPa   eps_f %5.2f %%   %d frames"
              % (tag, r["UTS"], r["E"], r["ef"], r["frames"]))

    # overlay() and elastic() take the output path and write it themselves
    import s25_s26_plots as P
    for fn, name in ((P.overlay, "s33_s34_overlay.png"),
                     (P.elastic, "s33_s34_elastic.png")):
        fn(os.path.join(OUT_DIR, name))
        print("   -> %s" % name)

    import s25_s26_reference_pdf as R
    ref = os.path.join(OUT_DIR, REF_PDF)
    R.build(ref)
    print("   -> %s" % REF_PDF)

    import mot_validation_pack as M
    M.set_session(PAIR, GAUGE_MM, REF_PDF)
    pack = os.path.join(OUT_DIR, PACK_PDF)
    _, n = M.build(pack)
    print("   -> %s  (%d specimens in the reference table)" % (PACK_PDF, n))

    # ---- the raw material a bench session needs beside the PDFs
    base = os.path.join(REPO, "Software", "UTM_PyQt6", "Test data",
                        "8.6.20 - Tensile test to Failure")
    for tag in D.ORDER:
        cfg = D.RUNS[tag]
        dst = os.path.join(OUT_DIR, tag)
        os.makedirs(dst, exist_ok=True)
        src_dir = os.path.join(base, cfg["folder"])
        for f in sorted(os.listdir(src_dir)):
            if f.endswith(".csv") or f.endswith("_report.pdf"):
                shutil.copy2(os.path.join(src_dir, f), os.path.join(dst, f))
        print("   -> %s/  (CSV + report)" % tag)

    shutil.copy2(os.path.join(REPO, "Software", "UTM_PyQt6", "registry.json"),
                 os.path.join(OUT_DIR, "registry.json"))
    print("   -> registry.json")
    return OUT_DIR


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    print(main())
