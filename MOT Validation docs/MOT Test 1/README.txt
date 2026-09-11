VALIDATION DOCS — PLA vs video extensometer, MOT session
=========================================================
Assembled 2026-08-19.

THE COMPARISON PAIR IS S25 AND S26.
Both were run on 2026-08-17 with frame capture armed expressly for extensometer
cross-validation. They are the only two runs where every frame still exists, so
MOT's software can re-process our actual pixels rather than re-testing a new
specimen. That is the strongest form of validation available here: identical
pixels, two independent algorithms, no specimen, machine or operator in the
difference.

    S25   UTS 46.16 MPa   E 3.167 GPa   eps_f 4.18 %   1445 frames, 0 dropped
    S26   UTS 47.17 MPa   E 3.549 GPa   eps_f 5.74 %   1682 frames, 0 dropped
    both  100 % infill PLA, spray markers, LED on, 100 % DIC coverage,
          Px0 frozen AFTER preload, 0.10 mm/s, 80 mm gauge, 80 mm2 nominal

They differ by 2.2 % on UTS and 12 % on E. The E gap is real and understood: S26
has a longer toe, which is exactly the kind of thing this validation exists to
settle.


WHAT IS IN THIS FOLDER
----------------------
Three subfolders and the register. (Everything below was flat until September 2026,
and these session folders now sit under "MOT Validation docs/".)

Videoextesometer MOT\                  What the laboratory produced:
                                       test2.chan 0.avi   the XT-205's own recording
                                       strain.csv         its strain record
                                       test2.daq          the machine's force/position log
                                       test2.vgtest       the test definition

DIC post processing data\               What this rig's post-processor made of that same
                                       video -- report PDF/PNG, results CSV and the
                                       per-frame CSV. This is Analysis 2 in the report:
                                       one video, two strain calculations, scale 0.99928.

PPD UTM DIC rig reference docs\         The rig side of the comparison:
                                       MOT_extensometer_validation_pack.pdf  READ THIS
                                         FIRST. 6 pages: the parameters that must match,
                                         our reference values, a comparison sheet to fill
                                         in at the bench, the traps, and what to bring.
                                       S25_S26_stress_strain_reference.pdf  Stress at
                                         every 0.10 % strain step, in print, so a number
                                         read off their software can be looked up rather
                                         than eyeballed off a curve.
                                       E_modulus_explained.pdf  Why our modulus fit
                                         window is what it is.
                                       s25_s26_overlay.png / _elastic.png  The two
                                         curves, and the elastic region.
                                       S25\  raw CSV, generated report PDF, photos and
                                         the capture folder for that specimen.

registry.json                          The whole specimen register.

Note: S26's own folder is not here -- its numbers are in the reference PDF and the
overlay, and the raw run stays in Software/UTM_PyQt6/Test data/.

WHAT IS NOT HERE, AND WHY
-------------------------
THE FRAMES AND VIDEOS — 3.5 GB, deliberately not copied.

    S25   ...\Specimen_S25_V2_Spray_Video2\20260817_103811\    1.6 GB
    S26   ...\Specimen_S26_V2_Spray_Video3\20260817_111525\    1.9 GB

Each holds frames\ (PNG stills), video.avi, video_boost.avi, video_speckle.avi
and run.json. Copy them onto a USB stick rather than into this OneDrive folder —
3.5 GB will sync for a long time and this folder is meant to be light.

Take video.avi (the raw view) in preference to the boost or speckle views: those
two are processed for human viewing and are NOT what the detector measured.
If their software can read image sequences, frames\ is better still — it is the
exact pixels our numbers came from.

THE add:north E-PLA TECHNICAL DATA SHEET is not in the repo. The published
figures we compare against are UTS 58 MPa, E 2.87 GPa, eps_f 8 %, Tg 55-60 degC
(rev 2.1, ISO 527 / 178). Download it and drop it in here before you travel — the
pack's checklist lists it as a printed item.


THE ONE THING TO SETTLE BEFORE THE FIRST PULL
---------------------------------------------
THE STRAIN ZERO. Our Px0 is frozen AFTER a ~300 N preload, so our strain axis
starts at an already-seated specimen. An extensometer zeroed at 0 N carries the
toe — grip take-up and specimen straightening — inside its strain, which lowers
apparent modulus and moves the 0.2 % offset yield with it. That single difference
is larger than the 8.5 % scatter of our whole 11-specimen set.

If they cannot preload to 300 N, compare on the 0.05–0.25 % secant instead. It
does not care where either axis was zeroed. Record both numbers regardless.
