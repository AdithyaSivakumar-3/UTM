# -*- coding: utf-8 -*-
"""Chapter 3 — Methodology: what was built, how it was configured, how it was validated."""

SF_ROWS = [
    ("SF", "Feature", "What it does for the operator", "Status"),
    ("1", "DIC health HUD", "Live 2/2 marker count, tracking %, jitter on the camera feed", "rig-validated"),
    ("2", "Prepare specimen", "One click tares position, force and DIC (Px₀) together", "rig-validated"),
    ("3", "Settings recipes", "Save and reload a whole setup — camera, thresholds, test", "rig-validated"),
    ("4", "Generate report", "One-click PDF and PNGs of the run with the key numbers", "rig-validated"),
    ("5", "Auto-stop at fracture", "Halts the crosshead on load collapse", "rig-validated"),
    ("6", "Strain-rate test", "Constant gauge dε/dt using the DIC channel as the sensor", "rig-validated"),
    ("7", "Stall guard", "Halts a frozen motor under load before the driver overheats", "rig-validated"),
    ("8", "Release load", "Controlled return through zero to −preload after a test", "rig-validated"),
    ("9", "Advanced test modes", "Six closed-loop protocols: cyclic, staircase, relaxation, creep, "
          "staircase→fracture, progressive cyclic→fracture", "rig-validated"),
    ("10", "Auto-preload", "Speed schedule 0.2→0.1→0.02 mm/s, stops at 1.03× target", "rig-validated"),
    ("11", "Auto-metadata link", "Every save links CSV, capture and registry row", "rig-validated"),
    ("12", "DIC auto-calibration", "Exposure/threshold sweep with a live parameter readout", "rig-validated"),
    ("13", "Guided wizard", "Nine-step checklist from power-on to saved run", "rig-validated"),
    ("14", "Test registry", "Every run indexed with E, σy, UTS, εf, toughness and force anchor", "rig-validated"),
    ("15", "Dead-DIC guard + backstops", "Freeze at 0.2 s of frozen strain, halt at 1.0 s; 4.5 kN / 30 mm caps",
     "rig-validated"),
    ("16", "Live Px₀ overlay", "Frozen reference pair and live pair drawn on the feed", "rig-validated"),
    ("17", "Video + image capture", "PNG stills plus three AVI views recorded with the run", "rig-validated"),
    ("18", "DIC post-processing", "Measures strain from any recorded video with the rig's own rule",
     "rig-validated"),
    ("19", "Noise capture", "Records the instrument at rest; separates drift from residual sd",
     "built, offline-verified"),
    ("20", "Manual blob selection", "Operator picks the two markers on a frozen frame; gates off",
     "built, offline-verified"),
]

MODULES = [
    ("Module", "Lines", "Role"),
    ("main.py", "8 101", "Application window, test state machine, all controls and plots"),
    ("utm_postdlg.py", "3 046", "DIC post-processing dialog (SF18): measures any recorded video"),
    ("utm_postproc.py", "1 740", "Video reading, frame probing, offline pixel-to-strain engine"),
    ("camera_manager.py", "992", "Basler pylon grab thread, ROI/exposure/gamma, frame sinks"),
    ("widgets.py", "667", "Custom Qt widgets: camera view, HUD, gauges"),
    ("control_policies.py", "620", "Closed-loop controllers for the six advanced modes (SF9)"),
    ("utm_capture.py", "565", "Video and still recording (SF17)"),
    ("utm_analysis.py", "501", "Modulus, yield, UTS, fracture and toughness from a run"),
    ("serial_manager.py", "380", "Serial link to the motor controller and load cell"),
    ("utm_capdlg.py", "321", "Capture settings dialog"),
    ("theme.py", "300", "Application theme and colours"),
    ("utm_recipes.py", "286", "Settings recipes and material presets (SF3)"),
    ("utm_wizard.py", "273", "Guided wizard (SF13)"),
    ("utm_report.py", "251", "One-click report generation (SF4)"),
    ("utm_camdlg.py", "228", "Camera setup dialog"),
    ("utm_registry.py", "221", "Test registry (SF14)"),
    ("utm_dic.py", "191", "Marker detection and the pixel-to-strain rule"),
    ("utm_autocal.py", "189", "DIC auto-calibration sweep (SF12)"),
    ("utm_blobpick.py", "144", "Manual blob picker (SF20)"),
    ("utm_noisedlg.py", "131", "Noise-capture dialog (SF19)"),
]

CAMERA = [
    ("Item", "Specification", "Why it matters for DIC"),
    ("Model", "Basler ace acA2440-35um", "—"),
    ("Sensor", "Sony IMX264, progressive-scan CMOS, global shutter",
     "A global shutter exposes every row at the same instant, so a moving marker is not skewed "
     "and its centroid is not smeared"),
    ("Colour", "Monochrome",
     "No Bayer filter to interpolate across, so better contrast and signal-to-noise on the "
     "grey level the threshold actually uses"),
    ("Resolution", "2448 × 2048 px (5.0 Mpx) of 2464 × 2056 on the die",
     "Sets the pixels across the gauge, and with them the strain resolution (Equation 2.5)"),
    ("Pixel size", "3.45 µm × 3.45 µm",
     "With the lens and stand-off, fixes the object size of one pixel — here ≈48 µm"),
    ("Sensor format", "2/3 inch, 11.1 mm diagonal",
     "Decides which lenses cover the sensor and what field of view a focal length gives"),
    ("Frame rate", "35 fps at full resolution",
     "Caps how fast a test can be sampled; the region of interest raises it, the exposure lowers it"),
    ("Exposure and gain", "Programmable, all automatic functions disabled",
     "Auto-exposure or auto-gain would change the grey levels mid-test and move the threshold"),
    ("Pixel bit depth", "10 / 12 bit ADC; Mono8 and Mono12 output",
     "8 bits are ample once the marker is thresholded; more depth costs bandwidth"),
    ("Dynamic range", "73.4 dB", "Headroom between the dark specimen and the bright marker"),
    ("Triggering", "Hardware and software trigger, free-run",
     "Free-run is used here; a hardware trigger is what a two-camera 2D setup would need"),
    ("Interface", "USB 3.0 (USB3 Vision), 5 Gbit/s, Micro-B with screw locks",
     "Streams full-resolution frames without compression; the screw locks stop a knock "
     "unplugging a run"),
    ("Power", "2.5 W over the USB cable", "No separate supply to route past the moving crosshead"),
    ("Lens mount", "C-mount; Azure-2514MML 25 mm f/1.4 fitted",
     "A fixed focal length with lockable focus and aperture rings, as the guide requires"),
    ("Size and mass", "29.3 × 29 × 30 mm, 80 g",
     "Light enough for a printed carriage to hold without creeping"),
    ("Software", "pylon SDK 25.11 through pypylon",
     "Native control of exposure, gain, gamma, region of interest and the grab strategy"),
]

PRINT = [
    ("Item", "Setting"),
    ("Printer", "Original Prusa MK4S, 0.4 mm nozzle"),
    ("Slicer and profile", "PrusaSlicer, 0.20 mm STRUCTURAL"),
    ("Materials", "PLA (white and black), PETG, TPU — generic profiles"),
    ("Infill", "100 % (solid, rectilinear fill pattern as suggested by Prusa for solid infill) or 50 % gyroid"),
    ("Supports / brim", "supports everywhere, no brim"),
    ("Specimen geometry", "Mini-dogbone, 80 mm gauge (standard) or 45 mm gauge; 80 mm² section"),
    ("Filament per specimen", "23.4 g, 7.85 m (100 % PLA)"),
    ("Print time per specimen", "48 min (normal mode)"),
    ("Markers", "Two spray-paint dots through a stencil at the gauge ends, ≈10 000 px each"),
    ("Marker polarity", "Black on white PLA; white on black PLA and on PETG"),
]


def build(R):
    R.h1("Methodology")
    R.p("This chapter describes what was built and how it was used: the hardware and the "
        "specimens, the software and its DIC pipeline, the camera configuration, the "
        "operator automations, the analysis conventions, the working method with an AI "
        "coding agent, the validation campaigns, and the evidence pipeline that produced "
        "every figure in Chapter 4.", align="justify")

    # ------------------------------------------------------------------ 3.1
    R.h2("The PPD-UTM DIC rig")
    R.h3("Frame, drive and load cell")
    R.fig_beside([
        "The machine is a desktop, vertical tensile frame built in the department from "
        "aluminium extrusion; {{fig:rig}} shows it as used for the validation campaigns "
        "and {{fig:rig_schematic}} its load path. Two ball screws driven by stepper "
        "motors move a crosshead between fixed lower grips and the load cell; the motor "
        "controller and the load-cell amplifier sit in an electronics box and talk to the "
        "computer over one serial link.",
        "The load cell is rated to 4.5 kN, which caps the machine; the usable travel is "
        "about 30 mm, which on an 80 mm gauge is a 37.5 % strain backstop. Brackets, load "
        "holders and the specimen grips are 3D-printed or machined in the department's "
        "workshop. Two emergency stops — a hardware mushroom button that cuts motor power "
        "and a software stop in the application — are wired in parallel, and the "
        "software adds hard backstops at 4.5 kN and 30 mm (Smart Feature 15).",
        "The rig was built to be used: the department's course laboratories need a "
        "tensile machine that students can run themselves on the materials they print, "
        "and the certified extensometers of a commercial laboratory cannot be handed to "
        "a class. An in-house channel can, and it can be changed — a different gauge, a "
        "new material preset, a second camera — without asking a vendor.",
    ], "UTM rig_12-08-26.jpg",
       "The PPD-UTM DIC rig as used for the validation campaigns: aluminium frame, twin "
       "ball screws, the load cell above the upper grip, the camera on its mount in front "
       "of the specimen and the LED-lit enclosure.", width_cm=6.0, label="rig")
    R.fig("report_rig_schematic.png",
          "Schematic of the rig as it stands in September 2026, in two views. **Front view**: "
          "the load path from the lead screws through the crosshead and the load cell to the "
          "specimen and the base, with the LED strip, the matte backdrop and the emergency "
          "stop. **Side view**: the optics — the backdrop behind the specimen, the camera on "
          "its printed mount ≈371 mm in front of it, and the field of view that stand-off "
          "produces. Underneath, the data path: force and position from the electronics box "
          "over the serial link, frames from the camera over USB 3.0.",
          width_cm=16.5, label="rig_schematic")
    R.h3("What it cost")
    R.p("The strain channel is cheap by the standards of the instrument it replaces. The "
        "camera is a stock industrial USB 3.0 model, the lens a stock 25 mm C-mount, and "
        "the lighting, enclosure, mount and grips are an LED strip, a sheet of MDF and "
        "printed parts: together of the order of a thousand euros, and the software is "
        "the department's own. A commercial video extensometer of the XT-205's class is "
        "priced in the tens of thousands of euros, and the universal testing machine it "
        "is bolted to in the six figures; those are approximate market figures rather "
        "than quotations, but the ratio is two orders of magnitude. The whole rig — "
        "frame, motors, load cell, electronics and the channel — cost a few thousand euros "
        "in parts. Low cost was an objective in its own right (Section 1.3), because the "
        "department needs an instrument it can lend to a class and change at will, and "
        "the price of a commercial extensometer rules both out.", align="justify")
    R.h3("Camera, lens and lighting")
    R.p("The strain channel is one Basler ace acA2440-35um industrial camera, whose "
        "specifications are collected in {{tab:camspec}} from the manufacturer's "
        "documentation [[basler_aca2440, basler_docs]]. It is a 2/3-inch Sony IMX264 "
        "global-shutter monochrome sensor of 2448 × 2048 pixels with 3.45 µm pixels, read "
        "over USB 3.0 at up to 35 frames per second, driven through Basler's pylon SDK "
        "[[basler_pylon]]. The table gives each specification with the reason it matters "
        "for this measurement, because most of them are not free choices: the good-practice "
        "guide of Section 2.4.2 asks for a global shutter, a monochrome sensor and every "
        "automatic function switched off, and this camera is the cheapest stock model that "
        "satisfies all three.", align="justify")
    R.tab(CAMERA, "Specifications of the Basler ace acA2440-35um, from the manufacturer's "
          "product documentation [[basler_docs]], with what each one buys the strain "
          "channel.", col_widths_cm=(2.8, 5.0, 8.2), font=8.5, label="camspec")
    R.p("The lens is an Azure-2514MML, a 25 mm f/1.4 fixed-focal-length C-mount lens "
        "[[azure_lens]]. Fixed focal length is a guide requirement — a zoom changes the "
        "optical scale the moment it is nudged — and this lens has the second property the "
        "guide asks for: both rings lock. The front ring sets focus, and the rear ring sets "
        "the aperture between f/1.4 and f/16. Wide open at f/1.4 the image is bright but the "
        "depth of field is shallow, so a specimen that is not perfectly flat to the sensor "
        "goes soft at one end; stopped down to about f/8 the whole gauge is sharp at the "
        "cost of light, which the LED strip supplies. Both rings are set once for a given "
        "stand-off and then locked, because a change in either invalidates the optical "
        "scale and the grey-level margin that the threshold preset was chosen for.",
        align="justify")
    R.p("At ≈371 mm from the specimen that lens frames the gauge so that about 20.9 pixels "
        "cover one millimetre — one pixel is ≈48 µm in object space; the reference "
        "instrument stands closer, at 27.9 px/mm.", align="justify")
    R.p("The specimen is lit by a strip of white LEDs inside a matte enclosure that "
        "blocks room light, so the grey-level histogram of the frame does not change when "
        "someone walks past or the sun comes out. This turned out to be the single most "
        "important piece of hardware for the threshold's stability (Section 4.7). The "
        "camera sits on a printed mount on the frame, normal to the specimen, at a "
        "distance set once for the 80 mm gauge and re-set for the 45 mm one; "
        "{{fig:cam_setup}} shows the arrangement.", align="justify")
    R.fig("DIC camera setup.jpg",
          "The camera on its mount inside the enclosure, looking at the gauge with its two "
          "painted markers. The LED strip is above the field of view.", width_cm=9.0,
          label="cam_setup")

    # ------------------------------------------------------------------ 3.2
    R.h2("Designed and manufactured parts")
    R.p("The machine already existed as a frame, two motors and a load cell. Everything that "
        "turns it into a DIC instrument had to be designed: a stand that holds the camera "
        "still and square to the specimen, a base for that stand, a vibration path between "
        "the base and a machine that pulls specimens apart, a light and its power supply, "
        "and the fixtures that put repeatable markers on a specimen. Those parts were "
        "modelled in SolidWorks [[solidworks]] and made in the department — laser-cut MDF, "
        "band-sawn aluminium profile and fused-filament printed PLA and TPU. "
        "{{tab:cadparts}} lists them; the subsections that follow take each in turn, with "
        "what it does, how it was decided and how it was made.", align="justify")
    R.tab([
        ("Part", "What it does", "Material", "Made by", "Versions"),
        ("MDF base plate", "Carries the camera stand, locates it to the rig and adds damping mass",
         "MDF, 8 mm", "Laser cut", "V2–V4"),
        ("TPU damping pad", "Isolates the base plate from the machine's vibration",
         "TPU, 2–3 mm", "3D printed", "1"),
        ("Rail base bracket", "Gusset that clamps the aluminium stand to the base plate",
         "PLA", "3D printed", "V1, V2"),
        ("Aluminium stand", "The rigid column the camera rides on", "Al T-slot profile",
         "Band saw", "20×20 / 30×30"),
        ("Camera carriage", "Slides on the stand, sets camera height without tools", "PLA",
         "3D printed", "V1–V6"),
        ("Camera housing", "Holds the Basler and slides onto the carriage", "PLA",
         "3D printed", "V4–V6"),
        ("Captive-nut holders", "Hold M3 and M4 nuts inside the printed joints", "PLA",
         "3D printed", "M3, M4"),
        ("LED light mount", "Places the LED above the field of view", "PLA", "3D printed",
         "V1–V3"),
        ("Buck-converter enclosure", "Houses the converter powering the LEDs, and its switch",
         "PLA", "3D printed", "V1–V4 + lid"),
        ("Marker template", "Locates the two spray dots repeatably on a specimen", "PLA",
         "3D printed", "v1–v6"),
        ("Bottom rail extension", "Lengthens the rig's base rail for stability",
         "Al profile", "Band saw", "0.4 → 1 m"),
    ], "The parts designed and made for this project. Versions are the CAD revisions kept in "
       "the model library.", col_widths_cm=(3.3, 6.0, 2.2, 2.2, 2.3), font=8.5, label="cadparts")

    R.h3("The camera mount, and what it has to do")
    R.p("The stand carries about 100 g of camera and lens, but its job is not to bear load — "
        "it is to hold that camera in the same place, frame after frame, on a machine whose "
        "motors and lead screws shake it. Any movement of the camera relative to the "
        "specimen is read as strain, so the mount is part of the measurement. Four "
        "requirements followed, and the first two come straight from the good-practice "
        "guide's rig section (Section 2.4.2): rigid location so the camera does not drift "
        "within a pull, and decoupling from the load frame, so the machine's own vibration "
        "does not reach the sensor. Two more came from using the thing: adjustment in "
        "height without tools, so a new gauge length can be framed in seconds, and a "
        "repeatable seat, so remounting does not change the optical scale.",
        align="justify")
    R.p("The answer is a chain, drawn in {{fig:cad_xsec}}: the rig's own base carries a TPU "
        "pad, the pad carries the MDF base plate, the plate carries a printed gusset "
        "bracket, the bracket clamps the aluminium stand, the stand carries the printed "
        "carriage, and the carriage carries the camera housing. Each link was chosen "
        "separately, and the two that mattered most — what the base plate is made of, and "
        "how the housing locks to the carriage — were decided with a written comparison "
        "rather than by preference. {{fig:cad_concept}} is the concept that chain came from. "
        "The same exercise made two changes to the machine itself: it gained the camera base "
        "plate, and its bottom rail was lengthened from 0.4 m to 1 m, because a stand "
        "bolted to a narrow base would have rocked the whole rig rather than steadied the "
        "camera.", align="justify")
    R.fig("cad/cad_cross_section.png",
          "Cross-section of the mount: the machine's surface, the 2–3 mm TPU pad, the MDF "
          "base plate, the printed gusset corner bracket and the aluminium stand, bolted "
          "through as one stack.", width_cm=13.0, label="cad_xsec")
    R.fig("cad/cad_concept_v1.png",
          "The camera-stand concept: aluminium profile for rigidity, a printed carriage and "
          "brackets, and a base plate with a locating pocket that fixes where the stand "
          "sits.", width_cm=11.5, label="cad_concept")

    R.h3("The base plate: MDF against sheet metal")
    R.p("The plate does two jobs at once. It is the structure that locates the stand, and it "
        "is the mass that damps it. The two candidates were a sealed MDF board and a thin "
        "sheet-metal plate, and they were compared in a Pugh matrix with sheet metal as the "
        "datum ({{tab:pugh}}). Four criteria were weighted: vibration isolation highest, "
        "because the plate sits on a machine that vibrates; machinability next, because the "
        "plate needed slots and a locating pocket cut in the department; moisture and "
        "durability, where MDF is the weaker of the two; and weight, where neither has an "
        "advantage that matters for a plate that never moves.", align="justify")
    R.tab([
        ("Criterion", "Weight", "Sheet metal (datum)", "MDF"),
        ("Vibration isolation", "5", "0", "+  (+5)"),
        ("Machinability", "4", "0", "+  (+4)"),
        ("Moisture / durability", "3", "0", "−  (−3)"),
        ("Weight (portability)", "2", "0", "S  (0)"),
        ("Weighted score", "—", "0 (baseline)", "+6"),
        ("+ / S / −", "—", "0+  4S  0−", "2+  1S  1−"),
    ], "Pugh matrix for the base-plate material. Scoring is + better than the datum, S the "
       "same, − worse; the weighted score is ±1 × weight. MDF leads at +6, carried by "
       "vibration isolation and machinability.", col_widths_cm=(5.2, 2.0, 4.4, 4.4), font=9,
       label="pugh")
    R.p("MDF wins by the two criteria the application cares about most, and loses only on "
        "moisture, which is answered by sealing the board and by the fact that it lives "
        "indoors on a bench. The thickness was then set at 8 mm: an M8 bolt wants about "
        "6 mm of material for full thread engagement, so 8 mm leaves a margin; it is stiff "
        "enough to resist flexing under the stand's cantilever load without being "
        "overbuilt; and it keeps enough mass to serve the damping criterion that won the "
        "matrix in the first place. The plate carries slots rather than holes so the stand "
        "can be moved along it, which is how the camera is squared to a new specimen; "
        "{{fig:cad_mdf}} shows the plate as cut.", align="justify")
    R.fig("cad/cad_mdf_v2.png",
          "The base plate as cut: 8 mm MDF with slots for the stand and clearance for the "
          "rig's own feet.", width_cm=13.0, label="cad_mdf")

    R.h3("The damping pad: TPU against neoprene")
    R.p("Between the MDF plate and the machine sits a 2–3 mm pad. Its job is to break the "
        "direct path from the frame into the plate, so that the motors' vibration reaches "
        "the camera attenuated rather than through steel and aluminium. The obvious choice "
        "is neoprene rubber sheet, and it was compared against two grades of printable TPU "
        "({{tab:tpu}}).", align="justify")
    R.tab([
        ("Property", "Neoprene / rubber", "TPU 95A", "TPU 87A"),
        ("Shore hardness", "40–50A", "95A (too hard)", "87A (closer)"),
        ("Vibration damping", "Excellent", "Good", "Very good"),
        ("Compression set", "Low", "Medium", "Medium"),
        ("Sourcing", "Buy as sheet", "Print yourself", "Print yourself"),
        ("Custom shape and slots", "Cut by hand", "Print the exact shape", "Print the exact shape"),
        ("Cost", "Low", "Filament cost", "Filament cost"),
        ("Consistency", "Uniform", "Depends on the print", "Depends on the print"),
    ], "The damping pad: neoprene sheet against two printable TPU grades.",
       col_widths_cm=(4.0, 4.0, 4.0, 4.0), font=9, label="tpu")
    R.p("Neoprene damps better and is more uniform, and on those two rows it wins. It loses "
        "on the row that decided it: the pad is not a rectangle. It has to clear the rig's "
        "feet and carry the same slots as the plate above it, and a hand-cut sheet gives a "
        "different outline every time it is remade, whereas a printed pad comes out of the "
        "same CAD file as the plate it sits under. Of the two TPU grades to hand, the "
        "softer 87A is the closer match to neoprene's 40–50A and damps better than the 95A, "
        "which the comparison marks as too hard to be worth printing. TPU was therefore "
        "chosen as printable and sufficiently damping, with the honest caveat in the last "
        "row: a printed pad's consistency depends on the print, so a pad that is reprinted "
        "should be reprinted with the same settings. The same material is one of the three "
        "the rig later characterised (Section 4.8) — the pad's stiffness is a property this "
        "machine can now measure for itself.", align="justify")

    R.h3("The stand: 20 × 20 against 30 × 30 profile")
    R.p("Two T-slot aluminium profiles were available in the laboratory, and the comparison "
        "is in {{tab:profile}}. The 30 × 30 was selected: it is the stiffer column for a "
        "cantilevered camera, and its 6 mm slot takes M5 hardware rather than the M4 of the "
        "20 × 20. In practice the stand was first built with the 20 × 20 profile, because a "
        "dimensionally accurate 30 × 30 model was not available at the time and scaling the "
        "20 × 20 model would have produced parts that did not fit; the printed parts were "
        "therefore dimensioned for both, with M5 nuts for the 20 × 20 and M6 for the "
        "30 × 30.", align="justify")
    R.tab([
        ("", "20 × 20", "30 × 30"),
        ("Weight", "≈0.5 kg/m", "≈0.9 kg/m"),
        ("Rigidity", "Moderate", "High"),
        ("Camera weight supported", "Up to ≈400 g easily", "Up to ≈2 kg easily"),
        ("Slot width", "5 mm (M4 bolts)", "6 mm (M5 bolts)"),
    ], "The two T-slot profiles available, as compared before the stand was designed. Profile "
       "models from the supplier's library [[dold_cad]].", col_widths_cm=(5.4, 5.3, 5.3),
       font=9, label="profile")

    R.h3("The rail base bracket")
    R.p("The bracket is the joint between the aluminium stand and the MDF plate, and it is "
        "the one part where a printed component carries a bending moment. It is a gusset "
        "corner bracket — a right angle with a diagonal web — printed in PLA and, by "
        "design, replaceable with an aluminium one if it ever proved too flexible. Two "
        "versions were made ({{fig:cad_bracket}}): the first used a slot and M5 hardware so "
        "the bracket could slide before being locked; the second replaced the slot with a "
        "plain M8 hole, because the plate's own slots already provide the adjustment, and "
        "tightened the sliding fit to 0.18 mm.", align="justify")
    R.fig_pair(["cad/cad_basemount_v1.png", "cad/cad_basemount_v2.png"],
               "The rail base bracket: (a) V1 with a slot for M5 and a looser slider fit, "
               "(b) V2 with an M8 hole and a 0.18 mm fit, the version that was printed.",
               widths_cm=(6.3, 6.2), label="cad_bracket")

    R.h3("The carriage, and the rib that stiffens it")
    R.p("The carriage is the printed part that rides the stand and carries the housing. Its "
        "weak direction is the cantilever: the camera hangs off one side, so the carriage "
        "wants to twist. The fix is a rib, and six rib geometries were scored against three "
        "weighted criteria — rigidity at 45 %, printability at 30 % and low weight at 25 % "
        "— because a rib that cannot be printed without supports, or that doubles the mass "
        "hanging off the stand, is not a fix ({{fig:cad_rib}}).", align="justify")
    R.fig("cad/cad_rib_matrix.png",
          "Weighted decision matrix for the carriage rib. The hybrid rib — a straight "
          "diagonal with filleted ends — wins at 4.30 out of 5.00, ahead of the curved arc "
          "at 4.00; the triangle fill is the most rigid but the heaviest, and scores 3.40.",
          width_cm=15.0, label="cad_rib")
    R.p("The hybrid won for reasons that are all manufacturing reasons. Its rigidity nearly "
        "matches the solid triangle fill without the weight penalty; the fillets at both "
        "ends remove the crack-starting sharp corners and the overhangs; and a straight "
        "diagonal at 45° is self-supporting in PLA, so the part prints with no support "
        "material and no scarred surfaces where support would have been removed. That is "
        "the recurring theme in these parts: the geometry that prints cleanly usually beats "
        "the geometry that is theoretically stiffest. {{fig:cad_carriage}} shows the part "
        "that resulted, with the winning rib arrowed.", align="justify")
    R.fig("cad/cad_carriage_hybrid.png",
          "The camera carriage as designed, with the hybrid rib arrowed: a straight diagonal "
          "web, filleted where it meets the platform and the back plate, carrying the "
          "cantilever load from the camera platform into the part that clamps the stand.",
          width_cm=10.0, label="cad_carriage")

    R.h3("The camera housing, and how it locks to the carriage")
    R.p("The housing holds the camera body and presents it to the carriage. Four concepts "
        "were modelled: V1 a volume template used only to check that the camera fits, V2 a "
        "version bolted directly to the rail, V3 a dovetail slider and V4 a mushroom-head "
        "slider. Direct bolting was rejected because it makes every height change a tool "
        "job; that left the question of which sliding profile to cut into the two parts. "
        "{{fig:cad_housing}} is the housing that resulted: a printed shell that captures the "
        "camera body and presents a foot underneath it.", align="justify")
    R.fig("cad/camera_carriage.png",
          "The camera housing: a printed shell around the camera body, open at the front for "
          "the lens and at the top for the mounting thread, with the mushroom-head foot "
          "underneath that mates with the carriage.", width_cm=9.5, label="cad_housing")
    R.p("Six sliding profiles were then drawn as cross-sections and scored on printability "
        "(35 %), rigidity (40 %) and ease of assembly (25 %), with each option carrying the "
        "printing tolerance it would need ({{fig:cad_rail}}). The T-slot mushroom head won "
        "at 4.65 out of 5.00. It locks in two directions at once — vertically under the "
        "mushroom head, laterally against the channel walls — which is why it scores full "
        "marks on rigidity alongside the dovetail, and it slides in from the side and is "
        "secured with a single M3 bolt, which is why it beats the dovetail on assembly. The "
        "built pair carries 0.22 mm of total clearance: enough to slide by hand, little "
        "enough not to rattle.", align="justify")
    R.fig("cad/cad_rail_matrix.png",
          "The six sliding profiles considered for the housing-to-carriage joint, each with "
          "its printing tolerance, and the weighted matrix that chose between them. The "
          "T-slot mushroom head wins at 4.65 out of 5.00.", width_cm=15.5, label="cad_rail")
    R.p("{{fig:cad_joint}} shows the joint itself: the mushroom-head rail standing on the "
        "carriage platform, and the housing seated on it in the assembly. The camera "
        "therefore hangs from a joint with no fastener in its load path — the single bolt "
        "only stops the housing sliding back off the way it came.", align="justify")
    R.fig_pair(["cad/Camera mount slider base.png", "cad/carriage and mount slider assembly 2.png"],
               "The housing-to-carriage joint: (a) the carriage, with the selected T-slot "
               "mushroom-head rail standing proud of its platform and the hybrid rib "
               "underneath, (b) the housing seated on that rail, the assembly the camera "
               "hangs from.", widths_cm=(5.6, 6.0), label="cad_joint")

    R.h3("Captive-nut holders")
    R.p("Printed parts cannot hold a thread reliably, so the joints between them use ordinary "
        "steel nuts trapped in printed pockets. Holders were drawn for M3 and M4 so the nut "
        "is captured before assembly and cannot fall out or spin while a bolt is tightened. "
        "It is a small part, but it is the reason the mount can be taken apart and put back "
        "together without the fit changing — which matters for a stand whose whole purpose "
        "is repeatable placement.", align="justify")

    R.h3("The light mount and the buck-converter enclosure")
    R.p("Section 4.7 shows how much the threshold depends on lighting, so the light needed a "
        "mount of its own rather than being propped in place. Three template versions "
        "({{fig:cad_light}}) fixed the LED strip above the field of view, out of the "
        "camera's line of sight but lighting the gauge evenly. The converter that powers "
        "those LEDs then needed a home: a printed PLA enclosure ({{fig:cad_buck}}) with "
        "locating pins that align and hold the converter board, a side extrusion that "
        "houses the on/off switch, and an open top with side slots for the wiring. Neither "
        "part is glamorous, and both remove a source of variation — a light that moves "
        "between runs, and a loose board on the bench.", align="justify")
    R.fig_pair(["cad/cad_light_mount.png", "cad/cad_buck_enclosure.png"],
               "(a) The LED light mount: two printed uprights on footed feet that bolt to "
               "the base plate and carry the strip above the field of view. (b) The "
               "buck-converter enclosure: locating pins for the board, a side pocket for the "
               "switch, and an open top for wiring.", widths_cm=(5.6, 6.6), label="cad_light")
    R.labels["fig:cad_buck"] = R.labels["fig:cad_light"]

    R.h3("The specimen marker template")
    R.p("The two painted dots are the measurement, so where they sit has to be repeatable "
        "from specimen to specimen: they define the gauge, and a dot placed 2 mm off shifts "
        "the reference span. A printed template solves it — a plate that drops over the "
        "specimen with two holes at the gauge ends, through which the paint is applied "
        "({{fig:cad_dots}}). Six versions were made, and the interesting part is that the "
        "revisions were about *fit*, not about the hole positions.", align="justify")
    R.bullets([
        "**v1 — running fit** (clearance). The template rocked on the specimen, so the dots "
        "moved with it.",
        "**v3 — sliding fit** (clearance). Better, still enough play to blur the edge of the "
        "dot where paint crept under the template.",
        "**v4, v5 and v6 — light push fit** (transition). The template stays put by itself "
        "and the dot edge is clean. v4 is the 80 mm-gauge template; **v5 and v6 place the "
        "dots for the 45 mm gauge** used in the laboratory comparison and for TPU "
        "(Section 4.5), with v6 also offered in a 3 mm dot diameter.",
        "**Paint** — enamel and spray were both tried through v4. Spray paint through a "
        "push-fit template is what the specimens in this report use: **white spray on the "
        "black specimens and black spray on the white ones**, so the markers are the small "
        "high-contrast class the detector expects either way (Section 4.7).",
    ])
    R.p("A permanent marker also makes a usable dot, and for a single quick pull it is the "
        "faster option. The template exists because the dot's *shape and size* have to be "
        "the same from specimen to specimen: the centroid of a hand-drawn blob is as good "
        "as its outline, and the area gate in the detector is set for a dot of a known "
        "size. Standardising the pattern is what lets one threshold preset and one set of "
        "blob gates work across a whole batch without retuning.", align="justify")
    R.fig_pair(["cad/cad_dot_template.png", "cad/cad_dot_results.png"],
               "(a) The marker template: a printed plate that locates the two dots at the "
               "gauge ends. (b) The four combinations tried — template fit from running to "
               "light push, and enamel against spray paint — and the dots each produced.",
               widths_cm=(6.6, 5.4), label="cad_dots")

    R.h3("Manufacturing and assembly")
    R.p("Three routes made everything. The MDF base plate was **laser "
        "cut** from a DXF exported straight out of the CAD model, which is what makes the "
        "slots and the locating pocket accurate enough to seat the stand without shimming. "
        "The aluminium profiles — the stand and the rig's lengthened bottom rail — were cut "
        "on the workshop's **automatic band saw**. Everything else was **3D printed**: the "
        "carriage, the housing, the brackets, the nut holders, the light mount, the "
        "enclosure and the templates in PLA, and the damping pad in TPU. The whole set of "
        "printed parts is a few days of printer time and a few euros of filament, which is "
        "the point of Section 3.1.2: the mount is cheap because it is printed, and it is "
        "adjustable because it was designed to be. {{fig:cad_mfg}} shows the printed parts "
        "doing their job on the machine.", align="justify")
    R.fig("cad/cad_mfg_carriage.png",
          "The printed camera carriage and housing assembled together on the rig: the "
          "carriage bolted to the aluminium stand, the housing seated on its rail, and the "
          "camera and lens carried by the housing.", width_cm=8.5, label="cad_mfg")
    R.p("{{fig:cad_built}} closes the loop: the assembly as modelled, and the same assembly "
        "on the machine. The stand bolts to the base plate through the gusset, the plate "
        "sits on the TPU pad under the rig's own frame, and the camera looks across at the "
        "specimen from the height its carriage was slid to.", align="justify")
    R.fig_pair(["cad/cad_assembly_cad.png", "UTM rig_12-08-26 (1).jpg"],
               "The camera mount (a) in CAD and (b) built and bolted to the rig, with the "
               "printed light-mount uprights standing on the same base plate and the camera "
               "looking across at a specimen in the grips.", widths_cm=(5.4, 6.4),
               label="cad_built")

    # ------------------------------------------------------------------ 3.3
    R.h2("Specimens and their preparation")
    R.p("All specimens were fused-filament mini-dogbones printed on a Prusa MK4S "
        "[[prusa_mk4s]] sliced in PrusaSlicer [[prusaslicer]] from CAD models drawn in "
        "SolidWorks [[solidworks]]; {{tab:printspec}} lists the print specification and "
        "{{fig:slicer}} shows the specimen as sliced. The standard geometry has an 80 mm "
        "gauge and an 80 mm² cross-section; a shorter 45 mm-gauge variant was made for the "
        "laboratory comparison and for TPU, whose strain would otherwise run a marker out "
        "of the frame. Cross-section and gauge are entered per specimen in the "
        "application and stored in the run's CSV header and in the registry, so stress "
        "and strain are always computed from the specimen's own numbers.", align="justify")
    R.tab(PRINT, "Specimen print specification.", col_widths_cm=(4.0, 12.0), font=9,
          label="printspec")
    R.fig("Specimen_filament_mass.png",
          "The specimen in PrusaSlicer: 0.20 mm STRUCTURAL profile, 100 % infill, MK4S with "
          "a 0.4 mm nozzle — 23.4 g of filament and 48 minutes per specimen.", width_cm=14.0,
          label="slicer")
    R.p("Two print settings were varied on purpose: infill (100 % solid, or 50 % gyroid) "
        "and, for PLA, the spool and its age, which is the moisture variable of Sections "
        "2.8 and 4.11. For the 100 % specimens the rectilinear fill pattern was used, as "
        "Prusa suggests for solid infill; it lays every layer's lines parallel and "
        "alternates the direction between layers, which is the pattern behind the "
        "raster-orientation effect discussed in Section 2.7. Specimen masses were recorded with a laboratory balance as a check "
        "on infill and porosity.", align="justify")
    R.p("The DIC markers are two dots of spray paint through a stencil, placed at the ends "
        "of the gauge. On white PLA they are black; on black PLA and on PETG they are "
        "white. Marker size is a compromise: a large dot has a better centroid "
        "(Section 2.5) but must stay inside the gauge and inside the frame at the end of "
        "the pull. The dots used here cover about 10 000 pixels each and pass the "
        "detector's area gate of 2 000–200 000 pixels with a wide margin.", align="justify")

    # ------------------------------------------------------------------ 3.3
    R.h2("Software architecture")
    R.p("The application is a single Python program built on PyQt6 [[pyqt6]], OpenCV "
        "[[opencv2000]], NumPy [[numpy2020]] and Matplotlib [[matplotlib2007]], twenty "
        "modules and 19 147 lines in total ({{tab:modules}}). The main window owns the "
        "test state machine — idle, preload, running, fracture, release — and everything "
        "the operator sees. Two worker threads feed it: a serial thread that polls the "
        "controller for force and position, and a camera thread that grabs frames and "
        "runs the DIC pipeline. Both post their results to the GUI thread through Qt "
        "signals, and the main window stamps each with the same monotonic clock, which is "
        "how a strain sample is matched to a force sample. {{fig:pytree_live}} shows which "
        "modules a live test pulls in.", align="justify")
    R.tab(MODULES, "The application's modules, with line counts from an abstract-syntax-tree "
          "scan of the source on 6 September 2026.", col_widths_cm=(3.6, 1.6, 10.8), font=9,
          label="modules")
    R.fig("pytree_live.png",
          "The live-test import graph: which modules the main window pulls in for a running "
          "test, from the serial and camera threads through detection to the plots.",
          width_cm=16.0, label="pytree_live")
    R.p("Three design rules run through the code. **The pixel-to-strain rule lives in one "
        "place** (the DIC module) and is imported by the live path, the post-processor and "
        "the tests, so the rig and the offline re-measurement cannot disagree by "
        "construction. **Every automation is a guard or a policy, not a special case in "
        "the main loop**: the stall guard, the dead-DIC guard, the auto-stop and the six "
        "closed-loop modes are separate objects that the state machine consults. **Every "
        "run leaves a complete record**: a CSV with a header of the whole setup, the "
        "captured video and stills, a registry row, and optionally a report — linked by "
        "name so that nothing can be orphaned.", align="justify")

    # ------------------------------------------------------------------ 3.4
    R.h2("The DIC pipeline")
    R.p("Each frame passes through six stages in the camera thread; the region it works "
        "on is the gauge strip of {{fig:roi}}.", align="justify")
    R.numbered([
        "**Wait** — the grab call blocks until the camera delivers a frame. The grab strategy "
        "is *latest image only*: if the pipeline falls behind, frames are dropped rather than "
        "queued, so the strain the operator sees is never stale.",
        "**Rotate** — the sensor is mounted so that the specimen's axis runs along the "
        "sensor's long side; the frame is rotated for display only.",
        "**Sink** — the frame is handed to the recorder (video and stills, Smart Feature 17) "
        "when recording is on. Measured cost ≈47 µs per frame.",
        "**Detect** — threshold (Otsu or fixed, with polarity), connected components, area "
        "and circularity gates, then the two best candidates by the pair rule (similar "
        "area, aligned along the axis). Measured cost ≈1.4 ms per frame on the 2348 × 419 "
        "region.",
        "**Strain** — the centroid separation Px is divided by the frozen Px₀ "
        "(Equation 2.4); a separation guard and a speed guard reject a physically "
        "impossible jump.",
        "**Emit** — strain, marker count, jitter and the overlay geometry are posted to the "
        "GUI, which draws the HUD (Smart Feature 1) and the live Px₀ overlay (Smart "
        "Feature 16).",
    ])
    R.fig("cam_pipeline.png",
          "The region of interest on the sensor: the 2348 × 419 px gauge strip is read from "
          "the 2448 × 2048 frame, so each frame the pipeline handles is about a fifth of the "
          "full sensor.", width_cm=15.0, label="roi")
    R.p("Two thresholds are kept as material presets (Smart Feature 3): *White* uses a "
        "fixed threshold of 150 with inverted polarity (dark markers on a light specimen), "
        "and *Black* uses a fixed threshold of 149 (light markers on a dark specimen). "
        "Otsu remains available as the default for an untuned setup, with the caveat of "
        "Section 2.5 that Section 4.7 quantifies. {{fig:calib}} shows the application at "
        "the moment the reference is frozen.", align="justify")
    R.fig("CalibratePxo_live marker.png",
          "The application during Calibrate Px₀: both markers detected (2/2), the frozen "
          "reference pair and the live pair drawn on the feed, and the strain readout at "
          "zero.", width_cm=15.0, label="calib")

    # ------------------------------------------------------------------ 3.5
    R.h2("Camera configuration")
    R.p("The camera's settings are the result of the exposure, region and frame-rate "
        "trade-off of Section 2.5, and each was measured rather than assumed; "
        "{{tab:camsettings}} lists them.", align="justify")
    R.tab([
        ("Setting", "Value", "Why"),
        ("Pixel format", "Mono8", "Grey level only; 8 bits are ample for a thresholded marker"),
        ("Region of interest", "2348 × 419 px at (0, 988)",
         "The gauge strip only — ≈20 % of the 5.0 Mpx sensor, so frames are ≈5× lighter"),
        ("Exposure", "50 000 µs", "Enough light for a wide grey-level margin under the LED strip"),
        ("Gamma", "0.5", "Lifts the dark tones so the dark marker separates cleanly"),
        ("Frame-rate limit", "35 fps", "The camera's ceiling at full resolution"),
        ("Delivered rate", "19.9 fps", "1 / 50 ms exposure — the exposure, not the sensor, sets the rate"),
        ("Grab strategy", "Latest image only", "Never a stale frame; drops rather than queues"),
        ("Blob gates", "area 2 000–200 000 px, circularity ≥ 0.5",
         "Rejects scratches, edges and grips; passes the ≈10 000 px markers"),
        ("Optical scale", "≈20.9 px/mm (≈48 µm/px)", "Set by lens and distance for the 80 mm gauge"),
    ], "Camera and detection settings used for every run in Chapter 4.",
       col_widths_cm=(3.4, 4.6, 8.0), font=9, label="camsettings")
    R.p("Why 19.9 frames per second and not 35: the exposure is 50 ms, and a global-shutter "
        "camera cannot deliver frames faster than it exposes them ({{fig:exposure}}). A "
        "shorter exposure would raise the rate but narrow the grey-level margin unless "
        "the light were raised with it; for a pull at 1–2 mm/min the specimen moves a few "
        "micrometres per frame, so 20 frames per second oversamples the strain by a wide "
        "margin and the exposure was kept. The optical scale is not a setting but a "
        "distance: {{fig:optics}} shows how px/mm and field of view follow from where the "
        "camera stands, and {{fig:travel}} what the region's width buys in strain before a "
        "marker leaves the frame.", align="justify")
    R.fig("cam_exposure.png",
          "Delivered frame rate against exposure time with the 50 000 µs setting marked: "
          "beyond the sensor's own read-out time the exposure, not the sensor, sets the rate.",
          width_cm=14.0, label="exposure")
    R.fig("pxmm_optics.png",
          "Pixels per millimetre is where the camera stands: with a 25 mm lens and 3.45 µm "
          "pixels, 371 mm gives the rig's 21.0 px/mm and 112 mm of field; matching the "
          "XT-205's 27.9 px/mm would need 284 mm and leave 84 mm of field for an 80 mm "
          "gauge.", width_cm=16.0, label="optics")
    R.fig("report_travel.png",
          "What the region's width buys, on a real S26 tare frame at true aspect: the marker "
          "pair spans ≈1 676 px and the walking marker has the room to its right. With the "
          "2348 px strip a marker reaches the frame edge at 33 % strain, with the full "
          "2448 px at 39 %, against the 37.5 % travel backstop on an 80 mm gauge. That gap "
          "is how the TPU specimens S35 and S36 walked out of frame, and why S37 was pulled "
          "on the 45 mm gauge.", width_cm=16.0, label="travel")

    # ------------------------------------------------------------------ 3.6
    R.h2("Capture, recording and the post-processor")
    R.p("Every run can be recorded (Smart Feature 17) as PNG stills at a chosen interval "
        "and as three AVI views written together: the raw frame, a contrast-boosted view "
        "for the human eye, and an adaptive-speckle view that shows the threshold's "
        "decision. Codecs and still formats were chosen by measurement — the cost of each "
        "sink in the camera thread ({{fig:capture_timing}}) and the file size per minute — "
        "so that recording cannot slow detection.", align="justify")
    R.fig("v2_capture_timing.png",
          "Measured per-frame cost of each capture sink in the camera thread: recording "
          "adds tens of microseconds and never touches the detection budget.", width_cm=14.0,
          label="capture_timing")
    R.p("The DIC post-processor (Smart Feature 18, {{fig:postdlg}}) is a dialog that opens "
        "any recorded video — the rig's own, or another machine's — and measures it with "
        "the same detection code and the same pixel-to-strain rule as the live path. The "
        "operator picks the tare frame, the threshold and polarity, and the gauge; the "
        "tool returns the strain record, a health trace and a stress–strain curve if a "
        "force CSV is supplied. Three guards were added after running an external "
        "laboratory's footage through it: a frame-count check against the container's "
        "metadata, a tare-frame sanity check, and a marker-count trace so that lost "
        "frames are visible rather than interpolated. The post-processor is the tool "
        "behind the same-footage comparison of Section 4.2.", align="justify")
    R.fig("UTM_DIC Post.png",
          "The DIC post-processing dialog: the video, the detection overlay, the tare frame "
          "and threshold controls, and the resulting strain trace.", width_cm=15.0,
          label="postdlg")

    # ------------------------------------------------------------------ 3.7
    R.h2("The twenty smart features")
    R.p("Twenty operator-facing automations were built over the project; {{tab:sf}} lists "
        "them. The rule for admitting one to the list was that the person running a test "
        "can invoke it, or that it acts on the machine during a run; developer tooling — "
        "the simulation harness the controllers were tuned on before hardware, the test "
        "suite — is methodology, not a feature. Eighteen have been validated on the rig; "
        "two are built and verified offline on recorded frames and await a rig session.",
        align="justify")
    R.tab(SF_ROWS, "The smart features SF1–SF20 as of 6 September 2026.",
          col_widths_cm=(0.9, 3.6, 9.0, 2.5), font=8.5, label="sf")
    R.p("Three of them carry most of the operator's day. **Prepare specimen** (SF2) "
        "collapses three tares — position, force and Px₀ — and a marker check into one "
        "button, which removed the most common source of a wasted specimen: a run started "
        "with a stale reference. **Auto-stop at fracture** (SF5) halts the crosshead on "
        "load collapse, so the grips are never driven into each other and the fracture "
        "frame is the last frame with load. The **guided wizard** (SF13) walks a new user "
        "from power-on to a saved run in nine steps and refuses to advance past a step "
        "whose check fails; {{fig:wizard}} shows it beside the auto-calibration dialog "
        "(SF12), which sweeps exposure and threshold and scores each candidate on marker "
        "count and centroid stability.", align="justify")
    R.fig_pair(["UTM_GuidedWizard.png", "UTM_Autocalibrate.png"],
               "(a) The guided wizard (SF13): nine steps from power-on to a saved run, each "
               "with a check that must pass before the next is enabled. (b) DIC "
               "auto-calibration (SF12): the exposure and threshold sweep, scored on marker "
               "count and centroid stability, with the winning setting applied.",
               widths_cm=(5.6, 9.0), label="wizard")
    R.p("The six closed-loop modes (SF9) are the largest single feature. Each is a policy "
        "object with a target profile, a controller and its own limits; the state machine "
        "runs the policy at the control period and the policy commands a crosshead speed. "
        "{{fig:sf9_overview}} shows the six as the rig actually ran them; Section 4.10 "
        "reports the loop's behaviour in detail.", align="justify")
    R.fig("sf9_overview.png",
          "The six closed-loop protocols as measured on the rig: force (or strain) against "
          "time for staircase, cyclic, relaxation, creep, staircase-to-fracture and "
          "progressive cyclic.", width_cm=16.0, label="sf9_overview")

    # ------------------------------------------------------------------ 3.8
    R.h2("Analysis conventions")
    R.p("Every number in Chapter 4 comes from the same analysis module, applied to the "
        "run's CSV, with these conventions.", align="justify")
    R.bullets([
        "**Force anchor.** The force at the end of preload is recorded as the anchor; "
        "stress is computed from the tared load unless stated. The anchor is stored with "
        "the run so that the choice is auditable.",
        "**Modulus.** The steepest straight run: a window of fixed strain width is slid along "
        "the rising curve and the least-squares line with the largest slope among the "
        "linear candidates is taken. Chosen over a fixed 0.05–0.40 % window because it "
        "repeats better (PLA 9.6 % against 16.0 % run-to-run scatter) while staying inside "
        "the published bands. The window's position and residual are stored with the "
        "result.",
        "**Yield.** The 0.2 % offset intersection with the fitted modulus line.",
        "**UTS.** The maximum engineering stress.",
        "**Fracture strain.** The DIC strain on the last frame before the load-collapse "
        "detector fires; where the markers were lost before fracture the value is flagged.",
        "**Toughness.** Trapezoidal area under the σ–ε curve to fracture.",
        "**Noise floor.** Standard deviation of the DIC strain over a window with the "
        "crosshead stopped; a short window (10–40 s) gives ≈12 µε, a 900 s window ≈26 µε, "
        "and the report says which is used. Windows are kept equal when specimens are "
        "compared, because the RMS moves with the window length.",
    ])
    R.p("The test registry (SF14) holds one row per run with these values, the specimen's "
        "geometry, material and infill, and the file links; Appendix A reproduces it.",
        align="justify")

    # ------------------------------------------------------------------ 3.9
    R.h2("AI in the loop: how the software was written")
    R.h3("The working method")
    R.p("The application, its tests and the evidence scripts were written in Visual Studio "
        "Code [[vscode_editing]], with an AI coding "
        "agent — Claude Code [[claude_code]] — in the loop in the editor's own terminal, in "
        "a division of labour that "
        "was kept the same for the whole project. The engineer owned the machine and the "
        "questions: what to test, what a result meant, what the next feature was, whether "
        "a number was plausible. The agent owned the typing: implementing a feature "
        "against a spec written in the conversation, writing the tests for it, refactoring, "
        "generating the plots and slides from the data, and reviewing its own and the "
        "engineer's code. The agent never ran the rig, never saw the machine, and never "
        "produced a measurement; every number in this report was produced by the rig or "
        "recomputed from its raw CSVs by a script that is itself in the repository.",
        align="justify")
    R.p("The loop for one feature ran as follows. The engineer described the feature and "
        "its acceptance test in plain language — usually with a rig observation that "
        "motivated it. The agent proposed an implementation, wrote it and its unit tests, "
        "and ran the tests. The engineer ran the feature on the rig, reported what "
        "happened, and the cycle repeated until the rig behaviour matched the intent. "
        "Every commit records the agent as co-author, so the share is measurable rather "
        "than remembered.", align="justify")
    R.h3("What the agent did")
    R.bullets([
        "**Features.** All twenty smart features were implemented this way, from the "
        "one-line stall guard to the six closed-loop policies and the 3 000-line "
        "post-processing dialog.",
        "**Tests.** A suite of 98 unit and offline tests, including detection tests on real "
        "recorded frames — the manual-blob feature, for instance, is proven on frames from "
        "specimen S13 where the circularity gate is deliberately set to kill automatic "
        "detection.",
        "**Analysis and evidence.** The 95 scripts (≈30 000 lines) that compute every "
        "figure in this report from the raw runs, and the two deck builders that assemble "
        "the progress diary and the final presentation from those figures.",
        "**Review.** Reading the code for a bug the rig had exposed — the infill label that "
        "reverted after a restart, the frame-count lie in a video container, the dangling "
        "hyperlink that broke a slide deck — and proposing the fix.",
        "**Writing.** Drafting documentation, the roadmap and this report from the diary, "
        "with the engineer editing for correctness and voice.",
    ])
    R.h3("Measured, not estimated")
    R.p("{{tab:ai}} gives the collaboration in numbers.", align="justify")
    R.tab([
        ("Quantity", "Value", "Source"),
        ("Prompts to the agent", "853", "Conversation logs, 28 May – 6 September 2026 (101 days)"),
        ("Commits in the period", "337 (370 in the repository)", "git log"),
        ("Commits co-authored by the agent", "94 %", "git log trailers"),
        ("Development lines (app + tests + scripts)", "26 468", "AST scan"),
        ("Unit and offline tests", "98", "test runner"),
        ("Engineer hours with the agent", "≈195 h", "Session logs"),
        ("Estimated solo-development hours", "≈1 300 h", "Estimate: lines and features at a conventional rate"),
        ("Ratio", "≈7×", "Estimate, see text"),
    ], "The AI collaboration in numbers. The first six rows are measured; the solo estimate "
       "and the ratio are estimates and are labelled as such.", col_widths_cm=(5.6, 4.4, 6.0),
       font=9, label="ai")
    R.p("The solo estimate is the weakest number in the table and is presented as such: it "
        "assumes a conventional rate of tested lines per engineer-day for a GUI "
        "application with hardware in the loop, and it does not credit the engineer with "
        "the speed-up they would have gained by writing the code themselves and knowing "
        "it better. A factor of seven is the right order of magnitude; a factor of three "
        "would still have made the project possible in the time. What is not an estimate "
        "is the shape of the work: with the typing delegated, the engineer's hours went to "
        "the rig, the specimens and the questions — 39 recorded tests, three materials, "
        "one laboratory comparison — rather than to Qt boilerplate.", align="justify")
    R.p("Where the commits went is also measurable: the main window took 90, the camera "
        "manager 24, the post-processor 21, the analysis module 14, the tests 8, and the "
        "documentation and evidence scripts 53. The detection module itself — the "
        "pixel-to-strain rule — took three commits in the whole project, which is the "
        "point: the measurement is small and stable, and the effort went into making it "
        "usable and proving it.", align="justify")
    R.h3("Risks and how they were handled")
    R.p("An agent that writes plausible code is a risk to a measurement project in one "
        "specific way: it can produce a number that looks right. Three rules contained "
        "that. First, **no number is typed**: every figure and every table in the diary "
        "is generated from the raw CSV by a script, and the script is committed. Second, "
        "**the rig is the oracle**: a feature is done when it behaves on the machine, not "
        "when its tests pass. Third, **the agent's own reports are cross-checked** — video "
        "metadata that claimed one frame count was verified by decoding the file; a "
        "carbon-footprint total was recomputed by hand; a literature page range was "
        "checked against the running heads of the paper. Each of these caught an error.",
        align="justify")

    # ------------------------------------------------------------------ 3.10
    R.h2("Validation campaigns")
    R.p("The channel was validated in three campaigns of increasing independence.", align="justify")
    R.h3("V-series: does the channel work?")
    R.p("The early V-series pulls (specimens S2–S11, June 2026) established that the "
        "markers could be tracked from tare to fracture, that the strain record was "
        "continuous, and that the stress–strain curve had the right shape. They also "
        "produced the first published-band comparison for PLA and the first "
        "infill-knockdown measurement, and they exposed the failure modes — lost markers, "
        "a threshold that wandered with the light, a stall under load — that became "
        "Smart Features 1, 5, 7 and 12.", align="justify")
    R.h3("VC-series: repeatability and noise")
    R.p("The VC-series (S12–S28, August 2026) ran the same PLA under controlled "
        "conditions, in pairs and triplets, to measure specimen-to-specimen scatter, the "
        "noise floor and its 1/Px₀ scaling, the black-versus-white marker question, the "
        "50 % versus 100 % infill knockdown, and the DIC coverage of a run. This series "
        "is the source of most of Sections 4.4 to 4.9.", align="justify")
    R.h3("MOT: the external laboratory")
    R.p("Two specimens from the rig's own print batch, XT205-S1 and XT205-S2, were pulled "
        "in an external materials-testing laboratory on a Zwick/Roell Z100 universal "
        "testing machine [[zwick_z100]] equipped with an XT-205 video extensometer "
        "({{fig:xt205}}) — a camera that tracks two painted marks, the same principle as "
        "the rig's DIC in certified form. There were two sessions: Test 1 with the rig's "
        "standard 80 mm gauge, and Test 2 with a 45 mm gauge at 2 mm/min and a 300 N "
        "preload, after Test 1 showed that an 80 mm marker pair leaves the XT-205's field "
        "of view within the first per cent of strain (Section 4.2.3). The laboratory "
        "provided its stress–strain data and, for Test 2, the extensometer's own video.",
        align="justify")
    R.p("Two analyses were defined on that material and are used by name throughout "
        "Chapter 4:", align="justify")
    R.bullets([
        "**Analysis 1 — instrument against instrument.** The XT-205's certified strain "
        "readout on the laboratory's specimen against the rig's DIC on a matched specimen "
        "from the same batch; E, σy, UTS and εf each computed twice, independently, on the "
        "two machines. It compares two rigs, two specimens and one material, so specimen "
        "scatter and pull conditions are inside the difference.",
        "**Analysis 2 — the rig's calculation on the laboratory's footage.** The session's "
        "raw XT-205 video re-measured frame by frame by the rig's post-processor (SF18) "
        "with the rig's own pixel-to-strain rule, and compared with the XT-205's own strain "
        "record on the same frames. Specimen, machine and pull drop out; only the two "
        "strain calculations remain. {{fig:motpp_setup}} shows the two records aligned at "
        "the tare frame.",
    ])
    R.fig_pair(["XT205-MOT_Wideview.jpg", "XT205-MOT Closerview.jpg"],
               "The external laboratory's Zwick/Roell Z100 with the XT-205 video "
               "extensometer: (a) the machine and the extensometer camera; (b) the specimen "
               "in the grips with its two markers — the footage the post-processor later "
               "re-measured.", widths_cm=(6.6, 6.6), label="xt205")
    R.fig("motpp_setup.png",
          "The same-footage comparison: the XT-205's own strain record against the "
          "post-processor's measurement of the XT-205's video, with the tare frame aligned.",
          width_cm=14.0, label="motpp_setup")

    # ------------------------------------------------------------------ 3.11
    R.h2("The evidence pipeline")
    R.p("The project's record is a 393-page weekly progress diary, built by a script from "
        "the figures, and a 24-page final presentation. The figures are produced by "
        "38 analysis scripts that read the raw run CSVs and videos and write PNGs; 28 "
        "slide-block scripts place them ({{fig:pytree_evidence}}). No figure is edited by "
        "hand and no number is transcribed: when a run is re-analysed, the figure and its "
        "slide change with it. A drift gate compares each rebuilt deck with a stored "
        "baseline so that an unintended change to a slide is caught before it is "
        "presented. This report's figures are the same files.", align="justify")
    R.fig("pytree_evidence.png",
          "The evidence pipeline's import graph: analysis scripts read the raw runs, "
          "figure scripts write PNGs, slide-block scripts place them, and the deck builders "
          "assemble the diary and the final presentation.", width_cm=16.0,
          label="pytree_evidence")
