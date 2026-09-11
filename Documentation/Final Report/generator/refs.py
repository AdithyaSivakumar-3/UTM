# -*- coding: utf-8 -*-
"""The bibliography registry for the project report.

Every source the two decks link (harvest_refs.py, 23 real targets) plus the sources a
report must name that a slide never had to: the DIC textbook, the standards, the software.
Numbering is assigned in ORDER OF FIRST CITATION by the build script (numeric [n] style,
as in the EENX30 report), so this file only needs stable keys.

Fields: authors · title · venue · year · url (DOI link preferred). `note` is for the
report's own use (e.g. where the deck cited it) and is never printed.
"""

REFS = {
    # ------------------------------------------------------------- DIC and image analysis
    "sutton2009": dict(
        authors="M. A. Sutton, J.-J. Orteu and H. W. Schreier",
        title="Image Correlation for Shape, Motion and Deformation Measurements: Basic "
              "Concepts, Theory and Applications",
        venue="Springer, New York", year=2009,
        url="https://doi.org/10.1007/978-0-387-78747-3"),
    "idics2018": dict(
        authors="International Digital Image Correlation Society, Standardization Committee",
        title="A Good Practices Guide for Digital Image Correlation, Edition 2",
        venue="iDICs, October", year=2025,
        url="https://idics.org/guide/", note="W3; the edition read in the pre-study"),
    "otsu1979": dict(
        authors="N. Otsu",
        title="A Threshold Selection Method from Gray-Level Histograms",
        venue="IEEE Transactions on Systems, Man, and Cybernetics, 9(1), pp. 62–66",
        year=1979, url="https://doi.org/10.1109/TSMC.1979.4310076", note="W233, W239"),

    # ------------------------------------------------------------- the camera and its SDK
    "basler_aca2440": dict(
        authors="Basler AG",
        title="acA2440-35um — product documentation (Sony IMX264 sensor, 2448 × 2048 px, "
              "3.45 µm pixels, USB 3.0, 35 fps)",
        venue="Basler Product Documentation", year=2026,
        url="https://docs.baslerweb.com/aca2440-35um", note="W3, W27"),
    "basler_pylon": dict(
        authors="Basler AG",
        title="pylon Camera Software Suite and pypylon (version 25.11.0 used)",
        venue="Basler AG", year=2026,
        url="https://www.baslerweb.com/en/software/pylon/", note="W10–13"),

    # ------------------------------------------------------------- the project's repositories
    "cenmir_utm": dict(
        authors="M. Cenanovic",
        title="UTM — the department's universal testing machine (source repository)",
        venue="GitHub, accessed 10 September", year=2026,
        url="https://github.com/cenmir/UTM",
        note="the initial reference this work started from"),
    "sivakumar_utm": dict(
        authors="A. Sivakumar",
        title="UTM — the PPD-UTM DIC rig: application, tests and evidence scripts "
              "(source repository)",
        venue="GitHub, accessed 10 September", year=2026,
        url="https://github.com/AdithyaSivakumar-3/UTM",
        note="the code and data behind this report"),

    # ------------------------------------------------------------- software
    "vscode_editing": dict(
        authors="Microsoft",
        title="Code editing in Visual Studio Code — introductory video tutorial",
        venue="Visual Studio Code documentation", year=2026,
        url="https://code.visualstudio.com/docs/introvideos/codeediting",
        note="the editor the application was written in"),
    "opencv2000": dict(
        authors="G. Bradski",
        title="The OpenCV Library",
        venue="Dr. Dobb's Journal of Software Tools", year=2000,
        url="https://opencv.org"),
    "pyqt6": dict(
        authors="Riverbank Computing Ltd.",
        title="PyQt6 — Python bindings for the Qt application framework",
        venue="Riverbank Computing", year=2026,
        url="https://www.riverbankcomputing.com/software/pyqt/"),
    "numpy2020": dict(
        authors="C. R. Harris, K. J. Millman, S. J. van der Walt et al.",
        title="Array programming with NumPy",
        venue="Nature, 585, pp. 357–362", year=2020,
        url="https://doi.org/10.1038/s41586-020-2649-2"),
    "matplotlib2007": dict(
        authors="J. D. Hunter",
        title="Matplotlib: A 2D graphics environment",
        venue="Computing in Science & Engineering, 9(3), pp. 90–95", year=2007,
        url="https://doi.org/10.1109/MCSE.2007.55"),

    # ------------------------------------------------------------- standards
    "iso527": dict(
        authors="International Organization for Standardization",
        title="ISO 527-1:2019 and ISO 527-2:2012 — Plastics: Determination of tensile "
              "properties (general principles; moulding and extrusion plastics)",
        venue="ISO, Geneva", year=2019, url="https://www.iso.org/standard/75824.html",
        note="W166, W169, W186, W214"),
    "astm_d638": dict(
        authors="ASTM International",
        title="ASTM D638-22 — Standard Test Method for Tensile Properties of Plastics",
        venue="ASTM International, West Conshohocken", year=2022,
        url="https://www.astm.org/d0638-22.html", note="W370"),
    "iso9513": dict(
        authors="International Organization for Standardization",
        title="ISO 9513:2012 — Metallic materials: Calibration of extensometer systems "
              "used in uniaxial testing",
        venue="ISO, Geneva", year=2012, url="https://www.iso.org/standard/56547.html",
        note="W363"),
    "astm_e83": dict(
        authors="ASTM International",
        title="ASTM E83-23 — Standard Practice for Verification and Classification of "
              "Extensometer Systems",
        venue="ASTM International, West Conshohocken", year=2023,
        url="https://www.astm.org/e0083-23.html", note="W363"),
    "iso14040": dict(
        authors="International Organization for Standardization",
        title="ISO 14040:2006 — Environmental management: Life cycle assessment — "
              "Principles and framework",
        venue="ISO, Geneva", year=2006, url="https://www.iso.org/standard/37456.html",
        note="W374"),
    "iso14067": dict(
        authors="International Organization for Standardization",
        title="ISO 14067:2018 — Greenhouse gases: Carbon footprint of products — "
              "Requirements and guidelines for quantification",
        venue="ISO, Geneva", year=2018, url="https://www.iso.org/standard/71206.html",
        note="W374"),

    # ------------------------------------------------------------- materials literature
    "chacon2017": dict(
        authors="J. M. Chacón, M. A. Caminero, E. García-Plaza and P. J. Núñez",
        title="Additive manufacturing of PLA structures using fused deposition modelling: "
              "Effect of process parameters on mechanical properties and their optimal "
              "selection",
        venue="Materials & Design, 124, pp. 143–157", year=2017,
        url="https://doi.org/10.1016/j.matdes.2017.03.065", note="P22, W137–W157"),
    "tymrak2014": dict(
        authors="B. M. Tymrak, M. Kreiger and J. M. Pearce",
        title="Mechanical properties of components fabricated with open-source 3-D "
              "printers under realistic environmental conditions",
        venue="Materials & Design, 58, pp. 242–246", year=2014,
        url="https://doi.org/10.1016/j.matdes.2014.02.038", note="P22, W299"),
    "durgashyam2019": dict(
        authors="K. Durgashyam, M. Indra Reddy, A. Balakrishna and K. Satyanarayana",
        title="Experimental investigation on mechanical properties of PETG material "
              "processed by fused deposition modeling method",
        venue="Materials Today: Proceedings, 18, pp. 2052–2059", year=2019,
        url="https://doi.org/10.1016/j.matpr.2019.06.082", note="P22, W299, W307"),
    "hsueh2021": dict(
        authors="M.-H. Hsueh, C.-J. Lai, S.-H. Wang et al.",
        title="Effect of Printing Parameters on the Thermal and Mechanical Properties of "
              "3D-Printed PLA and PETG, Using Fused Deposition Modeling",
        venue="Polymers, 13(11), 1758", year=2021,
        url="https://doi.org/10.3390/polym13111758", note="P22, W299"),
    "hohimer2017": dict(
        authors="C. Hohimer, J. Christ, N. Aliheidari, C. Mo and A. Ameli",
        title="3D printed thermoplastic polyurethane with isotropic material properties",
        venue="Proc. SPIE 10165, Behavior and Mechanics of Multifunctional Materials and "
              "Composites 2017, 1016511", year=2017,
        url="https://doi.org/10.1117/12.2259810",
        note="deck labels this 'Hohimer 2020' (W307, P22 footer) — the paper is 2017"),
    "prusament_pla": dict(
        authors="Prusa Research a.s.",
        title="Prusament PLA — technical data sheet",
        venue="Prusa Research", year=2025,
        url="https://prusament.com/materials/prusament-pla/", note="P22"),
    "prusament_petg": dict(
        authors="Prusa Research a.s.",
        title="Prusament PETG — technical data sheet",
        venue="Prusa Research", year=2025,
        url="https://prusament.com/materials/prusament-petg/", note="P22"),
    "addnorth_epla_tds": dict(
        authors="add:north AB",
        title="E-PLA — technical data sheet, rev. 21 (ISO 527 / ISO 178)",
        venue="add:north", year=2024,
        url="https://storage.googleapis.com/addnorth-com.appspot.com/imgix/assets/"
            "production/epla_tds_rev21_XTkw2P.pdf", note="W166, W169, W214"),
    "addnorth_pla_product": dict(
        authors="add:north AB",
        title="PLA Economy 1.75 mm, Light Grey — product page",
        venue="add:north", year=2026,
        url="https://addnorth.com/product/PLA%20Economy/PLA%20Economy%20-%201.75mm%20-"
            "%201000g%20-%20Light%20Grey", note="W166"),
    "tpu_tds_ultimaker": dict(
        authors="Ultimaker B.V.",
        title="Ultimaker TPU 95A — technical data sheet",
        venue="Ultimaker", year=2024,
        url="https://ultimaker.com/materials/s-series-tpu-95a/", note="W307 band"),
    "tpu_tds_ninjaflex": dict(
        authors="NinjaTek",
        title="NinjaFlex TPU 85A — technical specifications",
        venue="NinjaTek (Fenner Inc.)", year=2024,
        url="https://ninjatek.com/shop/ninjaflex/", note="W307 band"),
    "toner_plastics": dict(
        authors="Toner Plastics",
        title="Tensile testing results of Toner Plastics 3D filament",
        venue="Toner Plastics (vendor page)", year=2023,
        url="https://tonerplastics.com/tesile-testing-results-of-toner-plastics-3d-filament/",
        note="W35 — early literature slide"),

    # ------------------------------------------------------------- humidity study
    "hamid2022": dict(
        authors="R. A. Hamid, F. H. Hamezah and J. Abd Razak",
        title="Influence of Humidity on the Tensile Strength of 3D Printed PLA Filament",
        venue="in: Intelligent Manufacturing and Mechatronics (Proceedings of SympoSIMM "
              "2021), Lecture Notes in Mechanical Engineering, Springer, Singapore, "
              "pp. 497–502", year=2022,
        url="https://doi.org/10.1007/978-981-16-8954-3_47", note="W369–W372, P14, P18"),
    "quader2024": dict(
        authors="R. Quader, E. Dramko, D. Grewell, J. Randall and L. K. Narayanan",
        title="Characterizing the Effect of Filament Moisture on Tensile Properties and "
              "Morphology of Fused Deposition Modeled Polylactic Acid/Polybutylene "
              "Succinate Parts",
        venue="3D Printing and Additive Manufacturing, 11(3), e1151–e1161", year=2024,
        url="https://doi.org/10.1089/3dp.2022.0222", note="W369–W372, P18"),
    "aco_humidity": dict(
        authors="ACO",
        title="Impact of Humidity on 3D Printing Filament Performance (vendor note)",
        venue="acotoner.com", year=2024,
        url="https://www.acotoner.com/mn/impact-humidity-3d-printing-filament-performance.html",
        note="W369 — weighted below the two papers"),

    # ------------------------------------------------------------- carbon footprint
    "eea_grid": dict(
        authors="European Environment Agency",
        title="Greenhouse gas emission intensity of electricity generation in Europe",
        venue="EEA indicator", year=2024,
        url="https://www.eea.europa.eu/en/analysis/indicators/greenhouse-gas-emission-intensity-of-1",
        note="W374"),
    "eea_cars": dict(
        authors="European Environment Agency",
        title="CO₂ performance of new passenger cars in Europe",
        venue="EEA indicator", year=2024,
        url="https://www.eea.europa.eu/en/analysis/indicators/co2-performance-of-new-passenger",
        note="W377 — 107 g/km"),
    "google_ai_energy": dict(
        authors="Google Cloud",
        title="Measuring the environmental impact of AI inference",
        venue="Google Cloud Blog", year=2025,
        url="https://cloud.google.com/blog/products/infrastructure/measuring-the-environmental-impact-of-ai-inference",
        note="W374 — 0.24 Wh per prompt"),
    "prusa_forum_power": dict(
        authors="Prusa Research community",
        title="Original Prusa MK4 — power consumption (forum thread)",
        venue="forum.prusa3d.com", year=2024,
        url="https://forum.prusa3d.com/forum/english-forum-original-prusa-i3-mk4-general-discussion-announcements-and-releases/power-consumption-2/",
        note="W375 — the 80–130 W bench numbers"),

    # ------------------------------------------------------------- hardware and tools
    "prusa_mk4s": dict(
        authors="Prusa Research a.s.",
        title="Original Prusa MK4S — 3D printer",
        venue="Prusa Research", year=2025,
        url="https://www.prusa3d.com/product/original-prusa-mk4s/"),
    "prusaslicer": dict(
        authors="Prusa Research a.s.",
        title="PrusaSlicer",
        venue="Prusa Research", year=2025,
        url="https://www.prusa3d.com/page/prusaslicer_424/"),
    "dold_cad": dict(
        authors="DOLD Mechatronik GmbH",
        title="CAD data — linear rails and carriages",
        venue="dold-mechatronik.de", year=2026,
        url="https://www.dold-mechatronik.de/CAD-Data", note="W51 — camera-rail CAD source"),
    "zwick_z100": dict(
        authors="ZwickRoell GmbH & Co. KG",
        title="Z100 universal testing machine and videoXtens (XT-205) video extensometer",
        venue="ZwickRoell", year=2026,
        url="https://www.zwickroell.com/", note="the MOT lab's reference instruments"),
    "solidworks": dict(
        authors="Dassault Systèmes",
        title="SOLIDWORKS",
        venue="Dassault Systèmes", year=2025,
        url="https://www.solidworks.com/"),
    "claude_code": dict(
        authors="Anthropic",
        title="Claude Code — agentic coding tool",
        venue="Anthropic", year=2026,
        url="https://claude.com/claude-code", note="AI in the loop, section 3.9"),
    "astm_d2990": dict(
        authors="ASTM International",
        title="ASTM D2990-17 — Standard Test Methods for Tensile, Compressive, and Flexural Creep and Creep-Rupture of Plastics",
        venue="ASTM International, West Conshohocken", year=2017,
        url="https://www.astm.org/d2990-17.html", note="creep and relaxation protocols, 2.6"),
    "astm_d7791": dict(
        authors="ASTM International",
        title="ASTM D7791-17 — Standard Test Method for Uniaxial Fatigue Properties of Plastics",
        venue="ASTM International, West Conshohocken", year=2017,
        url="https://www.astm.org/d7791-17.html", note="cyclic protocol, 2.6"),
    "iso899": dict(
        authors="International Organization for Standardization",
        title="ISO 899-1:2017 — Plastics — Determination of creep behaviour — Part 1: Tensile creep",
        venue="ISO, Geneva", year=2017,
        url="https://www.iso.org/standard/70247.html", note="creep, 2.6"),
    "findley1976": dict(
        authors="W. N. Findley, J. S. Lai and K. Onaran",
        title="Creep and Relaxation of Nonlinear Viscoelastic Materials",
        venue="North-Holland, Amsterdam (Dover reprint 1989)", year=1976,
        url="https://store.doverpublications.com/products/9780486660165", note="Findley power law, 2.6"),
    "ward2013": dict(
        authors="I. M. Ward and J. Sweeney",
        title="Mechanics of Solid Polymer Materials, 3rd ed.",
        venue="Wiley, Chichester", year=2013,
        url="https://doi.org/10.1002/9781119967125", note="viscoelasticity, relaxation, 2.6"),
    "pan2018": dict(
        authors="B. Pan",
        title="Digital image correlation for surface deformation measurement: historical developments, recent advances and future goals",
        venue="Measurement Science and Technology, 29(8), 082001", year=2018,
        url="https://doi.org/10.1088/1361-6501/aac55b", note="2D/3D DIC, 2.3"),
    "ghg_product": dict(
        authors="World Resources Institute and World Business Council for Sustainable Development",
        title="Product Life Cycle Accounting and Reporting Standard (GHG Protocol)",
        venue="WRI/WBCSD, Washington DC", year=2011,
        url="https://ghgprotocol.org/product-standard", note="PCF method, 2.9"),
    "iso14044": dict(
        authors="International Organization for Standardization",
        title="ISO 14044:2006 — Environmental management — Life cycle assessment — Requirements and guidelines",
        venue="ISO, Geneva", year=2006,
        url="https://www.iso.org/standard/38498.html", note="LCA requirements, 2.9"),
    "ipcc_ar6": dict(
        authors="Intergovernmental Panel on Climate Change",
        title="Climate Change 2021: The Physical Science Basis (AR6 WG I), Chapter 7 — global warming potentials",
        venue="Cambridge University Press", year=2021,
        url="https://doi.org/10.1017/9781009157896", note="GWP100 factors, 2.9"),
    "basler_docs": dict(
        authors="Basler AG",
        title="acA2440-35um — Basler product documentation (specifications)",
        venue="docs.baslerweb.com", year=2026,
        url="https://docs.baslerweb.com/aca2440-35um", note="camera table, 3.1.2"),
    "blaber2015": dict(
        authors="J. Blaber, B. Adair and A. Antoniou",
        title="Ncorr: Open-Source 2D Digital Image Correlation Matlab Software",
        venue="Experimental Mechanics, 55, 1105–1122", year=2015,
        url="https://doi.org/10.1007/s11340-015-0009-1", note="in-house DIC literature"),
    "belloni2019": dict(
        authors="V. Belloni, R. Ravanelli, A. Nascetti, M. Di Rita, D. Mattei and M. Crespi",
        title="py2DIC: A New Free and Open Source Software for Displacement and Strain Measurements in the Field of Experimental Mechanics",
        venue="Sensors, 19(18), 3832", year=2019,
        url="https://doi.org/10.3390/s19183832", note="in-house DIC literature"),
    "atkinson2020": dict(
        authors="D. Atkinson and T. Becker",
        title="A 117 Line 2D Digital Image Correlation Code Written in MATLAB",
        venue="Remote Sensing, 12(18), 2906", year=2020,
        url="https://doi.org/10.3390/rs12182906", note="in-house DIC literature"),
    "olufsen2020": dict(
        authors="S. N. Olufsen, M. E. Andersen and E. Fagerholt",
        title="µDIC: An open-source toolkit for digital image correlation",
        venue="SoftwareX, 11, 100391", year=2020,
        url="https://doi.org/10.1016/j.softx.2019.100391", note="in-house DIC literature"),
    "azure_lens": dict(
        authors="Azure Photonics",
        title="AZURE-2514MML — 25 mm f/1.4 fixed-focal-length machine vision lens, specification sheet",
        venue="Azure Photonics", year=2026,
        url="https://www.azurephotonicsus.com/products/azure-2514MML.html",
        note="the lens on the rig, from the pre-study deck"),
}


def entry(key):
    e = REFS[key]
    return "%s. %s. %s, %d. %s" % (e["authors"], e["title"], e["venue"], e["year"], e["url"])


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    todo = [k for k, e in REFS.items() if "TODO" in e["title"]]
    print("%d references, %d still to complete: %s" % (len(REFS), len(todo), todo))
