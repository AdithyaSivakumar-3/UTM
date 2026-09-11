VALIDATION DOCS — 45 mm MARKER SPACING, MOT session 2
======================================================
Assembled 2026-09-03. Built by Documentation/Scripts/mot_session_45mm.py.

THE COMPARISON PAIR IS S33 AND S34.
Test 1 compared S25 and S26 at 80 mm marker spacing. This session repeats that
comparison at 45 mm, and S33/S34 are the right reference for it: same PLA, same
rig, same capture feature armed, run three weeks apart on the SAME machine
configuration. The only variable deliberately moved is how far apart the two
markers sit. Anything else — a different batch, a different day, a different
operator — would confound the one thing being checked.

    S33   UTS 47.09 MPa   E 3.174 GPa   eps_f 2.95 %   2371 frames
    S34   UTS 48.34 MPa   E 3.451 GPa   eps_f 5.25 %   2200 frames
    both  100 % infill PLA (the CSV header says 99 — a typed label that enters
          no calculation), spray markers, LED on, 0.10 mm/s, 45 mm marker
          spacing, 80 mm2 nominal section, Px0 frozen AFTER preload

For orientation, the 80 mm pair from Test 1 was S25 46.16 MPa / 3.167 GPa and
S26 47.17 MPa / 3.549 GPa. The 45 mm pair lands on top of it — which is the
finding the marker-spacing test already reported, and the thing an independent
extensometer can now confirm or refute.


READ THIS FIRST, AND IT IS THE ONE REAL DIFFERENCE FROM TEST 1
--------------------------------------------------------------
DIC COVERAGE IS NOT 100 %. S33 tracked 78 % of its load samples and S34 83 %,
against 100 % for both runs of Test 1. Test 1's pack could say "every frame has
a matching load and DIC sample"; this one cannot.

What that does and does not touch:

    UTS and sigma_y      UNAFFECTED. Both come from the LOAD CELL and never
                         touch the DIC. Quote them with full confidence.
    E                     Largely unaffected — the fit window is 0.05-0.40 %
                         strain and both runs still have plenty of points there.
    eps_f                 TREAT WITH CARE, especially S33's 2.95 %. Failure
                         strain depends on catching the LAST samples before
                         fracture, which is exactly what missing coverage takes
                         away. S34's 5.25 % is the more trustworthy of the two,
                         and the 80 mm pair spans 4.18-5.74 %.

So: compare E and UTS first. If their software also reports a fracture strain,
record it, but do not treat a disagreement on eps_f alone as a failed
validation until the coverage question is settled.


WHAT IS IN THIS FOLDER
----------------------
Three subfolders and the register, the same shape as Test 1. (Flat until September
2026; these session folders now sit under "MOT Validation docs/".)

Videoextesometer MOT\                  What the laboratory produced:
                                       sample3.chan 0.avi     the XT-205's recording
                                       strain-sample3.csv     its strain record
                                       sample3.daq            the machine's log

DIC post processing data\               What this rig's post-processor made of that same
                                       video -- report PDF/PNG, results CSV, and the
                                       per-frame CSVs.

PPD UTM DIC rig reference docs\         The rig side of the comparison:
                                       MOT_extensometer_validation_pack_45mm.pdf  READ
                                         FIRST. 6 pages: the parameters that must match,
                                         our reference values, a comparison sheet to fill
                                         in at the bench, the traps, and what to bring.
                                       S33_S34_stress_strain_reference.pdf  10 pages.
                                         Stress at every 0.10 % strain step plus every raw
                                         sample, in print, so a number read off their
                                         software can be looked up rather than eyeballed.
                                       s33_s34_overlay.png / _elastic.png  The two curves,
                                         and the elastic region.
                                       S33\ and S34\  raw CSV and the generated report PDF.

registry.json                          The whole specimen register.

WHAT IS NOT HERE, AND WHY
-------------------------
THE FRAMES AND VIDEOS — deliberately not copied, same as Test 1.

    S33   ...\\Specimen_S33_V4_Spray_Video12\\20260824_111820\\   2371 stills
    S34   ...\\Specimen_S34_V4_Spray_Video13\\20260824_113221\\   2200 stills

Each holds frames\\ (PNG stills), video.avi, video_speckle.avi and run.json.
Copy them to a USB stick rather than into this OneDrive folder.

Take video.avi (the raw view) in preference to video_speckle.avi: the speckle
view is processed for human viewing and is NOT what the detector measured. If
their software reads image sequences, frames\\ is better still — it is the exact
pixels our numbers came from.

NOTE: these two runs have only TWO AVI views, not three. There is no
video_boost.avi, unlike S25/S26. Nothing is lost — the raw view is the one that
matters — but do not go looking for a third file.

THE add:north E-PLA TDS is not in the repo. The published figures are UTS 58 MPa,
E 2.87 GPa, eps_f 8 %, Tg 55-60 degC (rev 2.1, ISO 527 / 178). Download it and
drop it in here before travelling; the pack lists it as a printed item.


THE ONE THING TO SETTLE BEFORE THE FIRST PULL
---------------------------------------------
Same as Test 1, and it has not got easier: THE STRAIN ZERO. Our Px0 is frozen
AFTER a ~310 N preload, so our strain axis starts at an already-seated specimen.
An extensometer zeroed at 0 N carries the toe — grip take-up and specimen
straightening — inside its strain, which lowers apparent modulus and moves the
0.2 % offset yield with it. That single difference is larger than the scatter of
our whole PLA set.

If they cannot preload to ~310 N, compare on the 0.05-0.25 % secant instead. It
does not care where either axis was zeroed. Record both numbers regardless.


WHAT IS NEW TO CHECK AT 45 mm
------------------------------
The gauge is the variable this session exists for, so record the things that
scale with it:

  1. PX/MM. Ours is about 20.87 px/mm on both runs — unchanged from the 80 mm
     session, because px/mm is a property of the OPTICS, not of the marker
     spacing. If their software reports a scale, it should agree.

  2. THE SHORTER GAUGE RESOLVES LESS STRAIN PER PIXEL. At 45 mm the marker pair
     spans about 939 px instead of 1676, so one pixel is worth roughly 1065
     microstrain against 597 at 80 mm. Their noise floor should be correspondingly
     higher, and so should ours. A like-for-like noise comparison has to be made
     over the SAME number of seconds — our own floor grows with observation time.

  3. WHETHER THE SHORTER GAUGE MOVES E AT ALL. Our answer is that it does not,
     by less than the run-to-run scatter of the 80 mm pair. That is the claim
     under test.
