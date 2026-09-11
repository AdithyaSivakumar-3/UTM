# -*- coding: utf-8 -*-
"""Chapter 5 — Conclusion and future work."""


def build(R):
    R.h1("Conclusion and Future Work")

    # ------------------------------------------------------------------ 5.1
    R.h2("Conclusions")
    R.p("A desktop universal testing machine that could only report its own crosshead now "
        "has a strain channel. It is one industrial camera, two painted dots and a "
        "program, and it has been shown — on the same frames — to measure what a "
        "certified video extensometer measures. The project's conclusions follow the "
        "objectives of Section 1.3.", align="justify")
    R.numbered([
        "**The channel was built, at negligible cost, and it runs live.** Strain from the "
        "camera is matched in time to force from the load cell at ≈20 frames per second, "
        "and the stress–strain curve forms on screen during the pull. The strain channel "
        "cost of the order of a thousand euros in camera, lens, lighting and printed "
        "parts, against the tens of thousands a commercial video extensometer costs and "
        "the six figures of the machine it sits on; and because every part of it is the "
        "department's own, it can be changed. The pixel-to-strain rule is one function, "
        "used unchanged by the live path, the post-processor and the tests.",
        "**The rig is operable by someone other than its builder.** Twenty automations "
        "remove the steps that used to waste specimens — one-click tare, auto-stop at "
        "fracture, stall and dead-DIC guards, a guided wizard, material recipes, one-click "
        "reporting — and every run leaves a linked, indexed, re-measurable record.",
        "**It is a measurement.** Analysis 2, against the XT-205 on its own footage: scale "
        "0.99928, R² 0.9999964, fracture strain within 0.08 %, a constant 0.07-pixel offset "
        "that vanishes from every slope. Analysis 1, against the laboratory on separate "
        "specimens: yield and fracture strain within 1 %. Noise floor 12–26 µε, below the "
        "reference instrument, and scaling with pixel span exactly as predicted. The "
        "remaining UTS and modulus gaps of 6–8 % are explained by pull rate, grip seating "
        "and batch — a batch offset the rig has measured on its own at 4.2 % — not by the "
        "channel.",
        "**It measures the material.** PLA, PETG and TPU fall inside their published bands "
        "in the expected order across two decades of modulus; matched specimens repeat to "
        "0.2 % in strength; the 50 % infill knockdown is the expected 2.4; the gauge "
        "length moves the properties by less than the same-gauge scatter; fracture does "
        "not nucleate at the markers; and the rig can now say what a crosshead-only "
        "machine cannot — that only a fifth to a third of its own motion was the "
        "specimen.",
    ])
    R.p("Two secondary results stand on their own. The moisture history of a PLA spool "
        "changes the parts printed from it by amounts the literature predicts — a few per "
        "cent in strength, a factor of two in fracture strain — which means batch is a "
        "variable to be controlled, not averaged. And the carbon footprint of building "
        "the whole thing was about 3.2 kg CO₂e, of which the machine itself was less than "
        "half a per cent; the cost of a measurement project is the thinking, not the "
        "pulling.", align="justify")
    R.p("On method: the software was written with an AI coding agent in the loop, and the "
        "collaboration is reported with its numbers — 853 prompts, 337 commits at 94 % "
        "co-authored, 98 tests, ≈195 engineer-hours against an estimated ≈1 300 solo — so "
        "that the reader can weigh it. The division that made it safe for a measurement "
        "project was that the agent never produced a number and the rig was always the "
        "oracle.", align="justify")
    R.p("The rig now does what it was built for. A student can print a specimen, paint two "
        "dots, follow the wizard and pull it, and leave with a stress–strain curve whose "
        "strain axis is the material's — on a machine the department owns, can lend to a "
        "class, and can change. The commercial extensometer in the materials-testing "
        "laboratory stays where it is; the in-house channel is the teaching instrument, "
        "and because its software and fixtures are the department's own, the next "
        "gauge, the next material preset and the next camera are a week's work rather "
        "than a purchase.", align="justify")

    # ------------------------------------------------------------------ 5.2
    R.h2("Future work")
    R.p("The future-work list is the one presented at the close of the project, in the "
        "order of nearness. The first item is closer than it looks: the post-processor "
        "already tracks the specimen's silhouette frame by frame, so lateral strain from "
        "the edges is a matter of resolution and validation rather than new machinery.",
        align="justify")

    R.h3("Poisson's ratio and true stress — the nearest step")
    R.p("The channel is one-dimensional, so every stress in this report is engineering "
        "stress and true stress is the analytical estimate of Equation 2.2. The lateral "
        "strain that turns the estimate into a measurement is within reach of the "
        "existing post-processor: the four-marker mathematics — two axial and two "
        "transverse markers giving ε_axial, ε_lateral, ν and the Cauchy stress from the "
        "current section — is written and self-tested, and the specification for tracking "
        "the specimen's edges instead of a transverse pair was written during the "
        "project (the necking correction must use the local width, not a row average, "
        "because necking is local). What blocks it is optics, not code: at 20.9 px/mm the "
        "specimen's width spans about 80 pixels and its elastic width change is "
        "sub-pixel. A gauge-zoomed second camera, or a wider specimen under the present "
        "one, unblocks it. With lateral strain in hand the report's true-stress curves "
        "become measured rather than estimated, and Poisson's ratio becomes a fourth "
        "property the rig can rank materials by.", align="justify")

    R.h3("2D-DIC strain field")
    R.p("A speckle pattern on the gauge and a correlation-based tracker would turn the "
        "same camera into a full-field instrument, giving the strain map over the gauge "
        "rather than two dots — strain concentration at print defects, the necking "
        "profile, the strain gradient at the shoulders. The way in is offline first, in "
        "the existing post-processor, where a correlation stage replaces the detection "
        "stage while the tare, the guards, the recording and the registry stay as they "
        "are; the open-source correlation codes of Section 2.4.1 are the reference "
        "implementations. It needs a lower exposure — the white specimen currently "
        "saturates the sensor, which is fine for a threshold and useless for a speckle — "
        "and a speckle fine enough for the 48 µm pixels.", align="justify")

    R.h3("Feeding simulation models")
    R.p("A measured strain field is the natural calibration and validation input for a "
        "finite-element material card. Exporting the field per frame, on the same "
        "geometry as the simulation, and comparing predicted with measured maps under the "
        "same load history would close the loop between the department's printing, "
        "testing and simulation courses: the specimen that is printed, pulled and mapped "
        "is the one the model is asked to predict.", align="justify")

    R.h3("Studying fracture behaviour")
    R.p("Every fracture is on film at 20 frames per second, and the post-processor can "
        "re-measure it. A fracture study would film the necking zone at higher "
        "magnification, run the 2D-DIC field around the growing crack, and read the "
        "strain concentration at the crack tip and the crack's speed and direction from "
        "the frames — the fracture-mechanics arena of Section 1.2, on the same rig. The "
        "survey of Section 4.9 is the start; a higher frame rate on a reduced region (the "
        "camera allows several hundred frames per second on a small window) would show "
        "the crack run. This item builds directly on the strain-field item above.",
        align="justify")

    R.h3("Correlation instead of a binary centroid")
    R.p("The present centroid is computed on the thresholded blob and discards the grey "
        "levels. An intensity-weighted, sub-pixel centroid — or a correlation-based "
        "tracker on the marker itself — was measured offline to cut the frame-to-frame "
        "jitter by 1.1–2.1× on the rig's own recordings. It should be added as a "
        "post-processing option first, and touch the live loop only once its behaviour on "
        "a lost or partial marker is proven, because the binary centroid's failure modes "
        "are the ones the guards already know.", align="justify")

    R.h3("Better grips")
    R.p("The printed jaws seat unpredictably: 19–29 % of early crosshead travel reaches "
        "the gauge, and which specimen gets 21 % and which 33 % is a lottery decided in "
        "the first tenth of a millimetre. A jaw that seats deterministically — sized from "
        "elastic-only re-mounts of one specimen, redesigned, reprinted and re-run — would "
        "shorten the toe of every curve and make the crosshead record more useful even "
        "with the camera present. Success is one cluster instead of two.", align="justify")

    R.h3("The controlled moisture study")
    R.p("Condition three sets of PLA specimens from one spool — dried at 50 °C for 4 h, "
        "ambient for 24 h, ambient for a week — record their masses, and pull them on the "
        "rig in one session. The literature predicts a strength loss of about 8 % and a "
        "rise in fracture strain after a day, and the rig's repeatability of better than "
        "1 % on a matched pair is enough to resolve it. This also closes the laboratory "
        "comparison, because it prices the batch term in the −7.7 % gap; together with "
        "one pull at the laboratory's 2 mm/min and the laboratory's load channel, it "
        "would separate rate, seating and batch completely.", align="justify")

    R.p("The upcoming stages are more than features. The 2D-DIC field, the fracture "
        "behaviour and the simulation coupling are each a thesis in size, and the rig, "
        "its software and its evidence pipeline are now in a state where a thesis can "
        "start from them rather than from a bare frame.", align="justify")
    R.p("The larger point of the project is not the instrument. It is that a measurement "
        "chain — camera, software, protocols, evidence — can be built, validated to a "
        "stated agreement with a certified reference, and applied to real material "
        "questions in one project on a desktop machine, for a small fraction of the cost "
        "of buying it, and that the record of how it was done is complete enough for the "
        "next person to continue it.", align="justify")
