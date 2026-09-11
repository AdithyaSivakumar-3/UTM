# -*- coding: utf-8 -*-
"""Front matter: abstract (one page, keywords), acknowledgments, acronyms."""

TITLE = "1-D Digital Image Correlation on a Universal Testing Machine " \
        "for real-time stress-strain measurement"
SUBTITLE = "A contactless strain measurement — built, validated against a certified " \
           "extensometer, and applied to various printed polymers"
AUTHOR = "Adithya Sivakumar"
DEPT = "Department of Product Development, Production and Design"
DATE = "September 2026"
SUPERVISORS = ["Supervisors: Johan Jansson · Mirza Cenanovic",
               "Department of Product Development, Production and Design, Jönköping University"]
REPORT_TYPE = "Project report"
ROLE = "Graduate Research Assistant, School of Engineering, 2026"

ACRONYMS = [
    ("AI", "Artificial Intelligence"),
    ("API", "Application Programming Interface"),
    ("ASTM", "American Society for Testing and Materials (ASTM International)"),
    ("AVI", "Audio Video Interleave (video container)"),
    ("CAD", "Computer-Aided Design"),
    ("CO₂e", "Carbon dioxide equivalent"),
    ("CSV", "Comma-Separated Values"),
    ("CV", "Coefficient of Variation"),
    ("DAQ", "Data Acquisition"),
    ("DIC", "Digital Image Correlation"),
    ("DOI", "Digital Object Identifier"),
    ("E", "Young's (elastic) modulus"),
    ("E-stop", "Emergency stop"),
    ("FDM / FFF", "Fused Deposition Modelling / Fused Filament Fabrication"),
    ("FEA", "Finite Element Analysis"),
    ("fps", "Frames per second"),
    ("GUI", "Graphical User Interface"),
    ("HUD", "Head-Up Display (the live DIC health panel)"),
    ("iDICs", "International Digital Image Correlation Society"),
    ("ISO", "International Organization for Standardization"),
    ("JU / JTH", "Jönköping University / Jönköping School of Engineering (Tekniska Högskolan)"),
    ("L, L₀", "Marker separation, and its reference value at the tare"),
    ("LED", "Light-Emitting Diode"),
    ("MDF", "Medium-Density Fibreboard"),
    ("MFI", "Melt Flow Index"),
    ("MOT", "The external materials-testing laboratory used for cross-validation"),
    ("Mpx", "Megapixel"),
    ("µε", "Microstrain (10⁻⁶ strain)"),
    ("OEM", "Original Equipment Manufacturer"),
    ("PCF", "Product Carbon Footprint"),
    ("PDF", "Portable Document Format"),
    ("PETG", "Polyethylene terephthalate glycol"),
    ("PLA", "Polylactic acid"),
    ("PPD", "Product Development, Production and Design (department)"),
    ("PPD-UTM", "This project's universal testing machine, as named in its evidence"),
    ("Px₀", "Reference marker separation in pixels (the frozen L₀)"),
    ("px/mm", "Pixels per millimetre (optical scale)"),
    ("RH", "Relative Humidity"),
    ("RMS", "Root Mean Square"),
    ("ROI", "Region Of Interest (the sensor window that is read)"),
    ("RQ", "Research Question"),
    ("SDK", "Software Development Kit"),
    ("SF", "Smart Feature (the numbered rig automations, SF1–SF20)"),
    ("TDS", "Technical Data Sheet"),
    ("TPU", "Thermoplastic polyurethane"),
    ("UI", "User Interface"),
    ("USB", "Universal Serial Bus"),
    ("UTM", "Universal Testing Machine"),
    ("UTS", "Ultimate Tensile Strength"),
    ("V&V", "Verification and Validation"),
    ("XT-205", "The commercial video extensometer used as the reference instrument"),
    ("εf", "Strain at fracture (failure strain)"),
    ("σy", "Yield strength"),
]


def abstract(R):
    R.h1("Abstract")
    R.p("A universal testing machine measures force directly, but it measures strain "
        "only through its two points of contact with the specimen: the crosshead counts "
        "everything between the grips, dominated by the machine's own compliance and the "
        "seating of the specimen rather than by the material. Laboratories fix this with "
        "an extensometer that watches the gauge length itself. This project gave a "
        "desktop, 4.5 kN universal testing machine that capability with a single "
        "industrial camera and its own software: a one-dimensional Digital Image "
        "Correlation (DIC) channel that tracks two painted markers and reports strain as "
        "the ratio of their separation to its reference value, live, while the pull is "
        "running. The purpose is a low-cost, customisable rig that students can use in "
        "course laboratories on the materials they print — a certified extensometer "
        "cannot be handed to a class, and an in-house channel can be extended, to "
        "two-dimensional DIC among other things.", align="justify")
    R.p("The work covered the whole chain. A camera mount, light enclosure and fixtures "
        "were designed and printed; a Python application was written that runs the "
        "machine, grabs and analyses frames at ≈20 fps, matches strain to force in time, "
        "and draws the stress–strain curve as it forms. Twenty operator-facing automations "
        "followed — automatic preload, auto-stop at fracture, stall protection, a guided "
        "checklist, six closed-loop test protocols, one-click reporting — and a "
        "post-processor that re-measures any recorded video the same way the rig measures "
        "live. The evidence trail was kept as a 393-page diary in which every figure is "
        "regenerated from the raw runs.", align="justify")
    R.p("The channel was validated three ways: against itself, through known-displacement "
        "and repeatability tests; against the literature, with PLA, PETG and TPU landing "
        "inside their published property bands in the predicted order; and against a "
        "certified instrument. A Zwick/Roell Z100 with an XT-205 video extensometer agreed "
        "with this rig within 1 % on yield strength and fracture strain, and when the "
        "laboratory's own footage was re-measured by this project's pipeline the two "
        "strain records matched in scale to 0.07 % with a constant offset of −55 µε — seven "
        "hundredths of a pixel — over 3 153 frames. The noise floor is tens of microstrain "
        "and scales with pixel span exactly as predicted; the remaining ultimate-strength "
        "gap to the laboratory (−7.7 %) was traced to pull rate, grip seating and specimen "
        "batch, not to the measurement. Secondary studies quantified the effect of "
        "filament moisture and the project's carbon footprint (≈3.2 kg CO₂e). The software "
        "was written with an AI coding agent in the loop, and that collaboration is "
        "reported with measured numbers.", align="justify")
    R.p("Keywords: Digital Image Correlation · contactless strain measurement · universal "
        "testing machine · computer vision · tensile testing · additive manufacturing · "
        "PLA · PETG · TPU · verification and validation · measurement uncertainty · "
        "closed-loop control · AI-assisted development", italic=True, size=10.5)


def acknowledgments(R):
    R.h1("Acknowledgments")
    R.p("This project was carried out at the Department of Product Development, "
        "Production and Design of Jönköping University's School of Engineering, as a "
        "Graduate Research Assistant, between February and September 2026.", align="justify")
    R.p("I would like to thank my supervisors, Johan Jansson and Mirza Cenanovic, for taking "
        "me on board and giving the freedom to build this project, and for providing "
        "valuable suggestions that became features, not least the manual marker selection "
        "that closed a real gap in the tracker.", align="justify")
    R.p("I thank Anette Johansson for all the support along the way — and for the invitation "
        "to Tallnäs for the department day and the amazing gifts from the department.",
        align="justify")
    R.p("I am grateful to everyone at PPD for an amazing time: for the lunch room talks, for "
        "the workshop hours, the printer time, the loaned tools and the questions that "
        "turned into features and slides. I thank Jacob Steggo, Research Engineer at the "
        "Department of Materials and Manufacturing, for helping at the materials-testing "
        "laboratory, where two of my specimens were pulled on the Zwick/Roell Z100 with the XT-205 "
        "video extensometer and the footage was shared — without that session, the "
        "central validation of this report would not exist.", align="justify")
    R.p("The software in this project was developed with an AI coding agent (Claude Code) "
        "in the loop. The division of labour is described in Section 3.10 and measured "
        "rather than asserted: every decision, every specimen and every observation on the "
        "rig was mine; every number in this report was produced by the rig or recomputed "
        "from its raw data by scripts, and the agent never saw the machine. So I have to "
        "acknowledge the Claude agent for its efficient work: for turning weeks of plumbing "
        "into days.", align="justify")
    R.p("Finally, to my family and friends: thank you.", align="justify")
    R.p("Adithya Sivakumar, Jönköping, September 2026", italic=True)


def acronyms(R):
    R.h1("Acronyms")
    R.p("{{tab:acr}} lists the acronyms and symbols used throughout this report, in "
        "alphabetical order.")
    rows = [("Acronym", "Meaning")] + [(a, m) for a, m in ACRONYMS]
    R.tab(rows, "Acronyms and symbols used in this report", col_widths_cm=(3.2, 12.8),
          font=9.5, label="acr")
