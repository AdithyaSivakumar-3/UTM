# -*- coding: utf-8 -*-
"""Chapter 1 — Introduction."""


def build(R):
    R.h1("Introduction")

    # ------------------------------------------------------------------ 1.1
    R.h2("Background")
    R.p("A universal testing machine (UTM) pulls a specimen apart between two grips and "
        "records the force it takes. Force is the easy half: a load cell in the load train "
        "reads it directly, and a 4.5 kN cell resolves a few newtons without difficulty. "
        "Strain is the hard half. The quantity a materials engineer wants is the "
        "elongation of the specimen's gauge length divided by that length — but what the "
        "machine can measure for free is the travel of its own crosshead, and the "
        "crosshead counts everything between the two grips: the elastic stretch of the "
        "load train, the bedding-in of the grips, the specimen's shoulders, and only "
        "lastly the gauge. On the desktop rig at the centre of this report, only "
        "19–29 % of the early crosshead motion reaches the gauge; the rest is the machine "
        "settling. A stress–strain curve drawn from crosshead travel is therefore a curve "
        "of the machine, not of the material, and every derived quantity that depends on "
        "the slope — the elastic modulus first of all — inherits the error.",
        align="justify")
    R.p("Commercial laboratories solve this with an extensometer, an instrument that "
        "watches the gauge length itself and ignores the rest of the load train. The "
        "classical clip-on extensometer is a spring with knife edges that touch the "
        "specimen and a strain gauge glued to the spring; the modern alternative is a video "
        "extensometer — a camera that tracks two marks on the specimen and reports their "
        "separation. Both are calibrated, certified instruments [[iso9513, astm_e83]], "
        "and both cost more than a desktop rig.", align="justify")
    R.p("The department's own tensile rig — a compact, twin-ball-screw frame built for "
        "teaching and research on 3D-printed specimens — had a load cell and a crosshead "
        "and nothing else. It exists for the course laboratories: students print "
        "specimens and pull them to study how material, infill and print settings change "
        "the properties, and for that they need a machine they can run themselves. The "
        "certified extensometers of a commercial materials-testing laboratory cannot be "
        "handed to a class; an instrument built in the department can, and it can be "
        "customised — a new gauge length, a new material preset, a second camera for "
        "two-dimensional DIC — as the coursework and the research need. Its software plotted force against crosshead position and "
        "called the result a stress–strain curve. The initial reference for this work was "
        "obtained from that machine's own repository [[cenmir_utm]], which supplied the "
        "starting point for the frame, the electronics and the control software; everything "
        "this report describes was built on top of it, and the result is a separate "
        "repository of its own [[sivakumar_utm]]. This project set out to give that rig a "
        "real strain channel with the cheapest possible instrument: one industrial camera "
        "and software written for the purpose, using the principle of Digital Image "
        "Correlation (DIC) in its simplest, one-dimensional, two-marker form. "
        "{{fig:dic_explain}} shows the whole idea on one real frame from the rig: two "
        "painted markers on the gauge, the camera tracks their separation, and strain is "
        "the change in that separation divided by its starting value.", align="justify")
    R.fig("report_dic_explain.png",
          "The principle in one picture: two painted markers on the specimen's gauge, the "
          "camera tracks their separation L every frame, and strain is (L − L₀)/L₀ — a "
          "ratio of pixel counts, so no calibration enters the strain itself.",
          width_cm=16.0, label="dic_explain")

    # ------------------------------------------------------------------ 1.2
    R.h2("Where DIC is used, and where this project sits")
    R.p("Digital Image Correlation measures how a surface deforms by comparing photographs "
        "of it under load [[sutton2009]]. In its full-field form it tracks a random speckle "
        "pattern across the whole surface and returns a displacement — and hence strain — "
        "map; in its reduced form it tracks a few discrete markers and returns a few "
        "numbers. The same trick earns its keep in very different rooms:", align="justify")
    R.bullets([
        "**Material testing and characterisation** — stress–strain curves, modulus, yield, "
        "ultimate strength and failure strain, measured without touching the specimen. "
        "This is the arena of the present project.",
        "**Manufacturing quality control** — warpage, springback and assembly distortion "
        "checked against CAD, contactless and in minutes.",
        "**Aerospace structural monitoring** — wing bend and fuselage-skin strain in "
        "full-scale tests, thousands of virtual gauges from a pair of cameras.",
        "**Fracture mechanics** — strain concentration at a crack tip, crack speed and "
        "direction; an item on this project's future-work list.",
        "**Biomechanics and medical devices** — tissue, implants and prostheses under load, "
        "where a contact instrument is not an option.",
        "**Thermal stress analysis** — expansion and warpage under heating, where a glued "
        "gauge would not survive.",
    ])
    R.p("The two-marker form used here is deliberately the simplest member of that family. "
        "It gives up the strain map for a single axial strain, and in return it needs no "
        "speckle, no correlation window, no calibration target, and no more than a few "
        "hundred lines of tracking code — which is what made it possible to build, "
        "validate and apply the whole channel within one project.", align="justify")

    # ------------------------------------------------------------------ 1.3
    R.h2("Problem statement and objectives")
    R.p("The problem was not to demonstrate that a camera can see two dots. It was to turn "
        "that observation into a measurement an engineer would trust — one whose "
        "agreement with a certified instrument is known, whose noise floor is "
        "characterised, and whose failure modes are understood — and then to use it. Four "
        "objectives followed:", align="justify")
    R.numbered([
        "**Build the channel, low-cost and customisable.** Mount a camera on the rig, light "
        "the specimen, write the software that finds the markers on every frame, and "
        "deliver strain live, matched in time to the load cell — with hardware of the "
        "order of a thousand euros, and with every part of it the department's own to "
        "change.",
        "**Make the rig operable.** Automate the steps that make a tensile test repeatable "
        "— preload, calibration, tare, stop-at-fracture, reporting — so that the "
        "measurement does not depend on the operator's attention.",
        "**Prove it is a measurement.** Validate the channel against itself (repeatability, "
        "known displacement), against the literature (published property bands), and "
        "against a certified video extensometer in a commercial laboratory.",
        "**Apply it.** Characterise three printed polymers — PLA, PETG and TPU — and answer "
        "the material questions the department actually asks: infill, marker spacing, "
        "moisture, fracture character.",
    ])

    # ------------------------------------------------------------------ 1.4
    R.h2("Research questions")
    R.p("The objectives reduce to three questions that the analysis chapter answers "
        "explicitly:", align="justify")
    R.bullets([
        "**RQ1** — Can a two-marker DIC channel built on a low-cost industrial camera match "
        "a certified video extensometer, and to what agreement?",
        "**RQ2** — What sets the channel's noise floor and measurement uncertainty, and can "
        "those be predicted rather than merely observed?",
        "**RQ3** — Does the rig reproduce the expected ordering and published property "
        "ranges across polymers of very different character?",
    ])

    # ------------------------------------------------------------------ 1.5
    R.h2("Scope and limitations")
    R.p("The channel is one-dimensional: two markers, one axial strain. Full-field strain "
        "maps, lateral strain and hence Poisson's ratio are outside the scope, and the "
        "report says so where it matters (true stress is estimated analytically, not "
        "measured). The rig is a desktop machine with a 4.5 kN load cell and about 30 mm "
        "of usable travel; the specimens are 3D-printed mini-dogbones rather than "
        "standard-size coupons, so no claim of compliance with ISO 527 or ASTM D638 "
        "[[iso527, astm_d638]] is made — those standards are used as vocabulary and as the "
        "definition of the properties, not as a certificate.", align="justify")
    R.p("Sample sizes are small: five to nine specimens per PLA condition, three PETG, three "
        "TPU, and a single specimen on each side of the laboratory comparison. The "
        "comparison itself involved one external laboratory and one instrument. Where a "
        "result rests on n = 1 or n = 2 the text says so, and the conclusions are sized "
        "accordingly. Numbers that are estimated rather than measured — the solo-effort "
        "comparison in the AI section, the AI energy term in the carbon footprint — are "
        "labelled as estimates and kept separate from the measurements.", align="justify")

    # ------------------------------------------------------------------ 1.6
    R.h2("Method of work and outline of the report")
    R.p("The project ran from February to September 2026 as a weekly cycle of build, test "
        "on the rig, analyse, and record. The record is a 393-page progress diary in which "
        "every figure is regenerated from the raw test data on each build, so that a plot "
        "cannot drift from the numbers behind it; this report is written from that diary "
        "and from the code, and its figures are the same regenerated ones. The software was "
        "written with an AI coding agent in the loop, a method described and measured in "
        "Section 3.10.", align="justify")
    R.p("Chapter 2 gives the theory: tensile properties, the ways strain is measured, DIC "
        "and its two-marker form, image formation and thresholding, noise, the closed-loop "
        "protocols the rig runs, the materials, and the carbon-footprint method. Chapter 3 "
        "describes what was built and how it was validated — hardware, specimens, "
        "software, the DIC pipeline, the camera settings, the automations, the validation "
        "campaigns and the evidence pipeline. Chapter 4 presents and discusses the results, "
        "ending with explicit answers to RQ1–RQ3. Chapter 5 concludes, lists what is still "
        "open, and names the future work. The bibliography and appendices follow.",
        align="justify")
