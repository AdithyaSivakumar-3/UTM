# -*- coding: utf-8 -*-
"""Chapter 2 — Theory."""


def build(R):
    R.h1("Theory")
    R.p("This chapter collects the background the rest of the report leans on: what a "
        "tensile test measures and why the strain axis is the hard one; how strain is "
        "measured in practice; what Digital Image Correlation is and what its two-marker "
        "form reduces to; how a camera turns a painted dot into a number, and how that "
        "number can be wrong; the closed-loop test protocols the rig runs; the three "
        "polymers tested; and the method used to estimate the project's carbon "
        "footprint.", align="justify")

    # ------------------------------------------------------------------ 2.1
    R.h2("The tensile test and its properties")
    R.p("In a tensile test a specimen of known cross-section A₀ and gauge length L₀ is "
        "pulled at a controlled rate until it breaks, while force F and elongation ΔL are "
        "recorded. Engineering stress and engineering strain normalise these by the "
        "original geometry:", align="justify")
    R.eq("σ = F / A₀        ε = ΔL / L₀ = (L − L₀) / L₀", "2.1")
    R.p("From the σ–ε curve the standard properties follow [[iso527, astm_d638]]. The "
        "**elastic modulus** E is the slope of the initial linear region. The **yield "
        "strength** σy is the stress at which the material departs from that line; for "
        "polymers, which yield gradually, this report uses the 0.2 % offset construction — a "
        "line of slope E displaced by 0.002 strain, intersected with the curve. The "
        "**ultimate tensile strength** (UTS) is the maximum engineering stress. The **strain "
        "at fracture** εf is the strain at the last frame before the load drops to zero. "
        "**Toughness** is the area under the curve to fracture, in kJ/m³. For the fits in "
        "this report the modulus is the slope of the *steepest straight run* of the rising "
        "curve — a window of fixed strain width slid along the curve, the least-squares "
        "line with the largest slope among those that are linear — searched the same way "
        "for every specimen, so that moduli are comparable across the study (Section 3.9).",
        align="justify")
    R.p("Engineering stress divides by the original area, but a stretched specimen thins. "
        "**True stress** accounts for this; under the assumption of constant volume "
        "(Poisson's ratio ν = 0.5, exact only for incompressible flow) it is", align="justify")
    R.eq("σ_true = σ (1 + ε)        ε_true = ln(1 + ε)", "2.2")
    R.p("{{fig:strain_terms}} draws the two strain definitions side by side, and "
        "{{fig:true_stress}} shows what the correction does to a real PLA curve: the true "
        "curve keeps rising past the engineering ultimate strength, because the thinning "
        "section is accounted for. The rig measures neither lateral strain nor volume, so "
        "true stress in this report is always the analytical estimate of Equation 2.2, "
        "shown only where the distinction matters (Section 4.10).", align="justify")
    R.fig("sf9_strain_terms.png",
          "One measurement, two definitions: engineering strain against the tared reference "
          "and true (logarithmic) strain, with the difference between them growing with "
          "strain — small for PLA, large for the elastomer.", width_cm=14.0, label="strain_terms")
    R.fig("sf9_true_stress.png",
          "Engineering and true stress–strain for a printed PLA specimen: the true curve keeps "
          "rising past the engineering UTS because the thinning cross-section is accounted "
          "for. Analytical estimate (ν = 0.5), not a measurement.", width_cm=13.5, label="true_stress")

    # ------------------------------------------------------------------ 2.2
    R.h2("Why the crosshead is not an extensometer")
    R.p("A universal testing machine records the displacement of its crosshead, which is "
        "not the elongation of the gauge. Between the two grips the load path contains "
        "the frame, the load cell, the grips themselves, the clamped ends of the "
        "specimen, its shoulders, and finally the gauge. Every element has a compliance, "
        "and at low load the grips also settle: knurled jaws bite into a polymer "
        "specimen, and any slack between the specimen and the grip faces is taken up "
        "before the gauge feels the full force. The crosshead therefore reports", align="justify")
    R.eq("ΔL_crosshead = ΔL_gauge + ΔL_shoulders + ΔL_grips + ΔL_machine + ΔL_slack", "2.3")
    R.p("and only the first term is the material. The consequence is a slope error: the "
        "crosshead-based strain is larger than the true strain by the ratio of the whole "
        "load path's compliance to the gauge's, so the apparent modulus is low by the "
        "same factor. The error is not constant — the slack term is largest at the start "
        "of the pull and the grip term depends on the clamping force — so it cannot be "
        "calibrated out with a single correction. Standards therefore require an "
        "extensometer for modulus determination [[iso527, iso9513]].", align="justify")
    R.p("On the rig studied here, the share of crosshead motion that reaches the gauge "
        "was measured directly — with the DIC channel — at 19–29 % during the elastic "
        "region (Section 4.3). Put the other way: the crosshead curve of this machine "
        "overstates strain, and understates modulus, by a factor of three to five.",
        align="justify")

    # ------------------------------------------------------------------ 2.3
    R.h2("Measuring strain: the extensometer family")
    R.p("Instruments that watch the gauge itself fall into four families.", align="justify")
    R.bullets([
        "**Bonded strain gauges** — a metal foil glued to the specimen changes resistance "
        "as it stretches. Precise (sub-microstrain) but single-use, limited to small "
        "strain, and the glue and the gauge stiffen a soft polymer.",
        "**Clip-on (contact) extensometers** — a spring frame with knife edges pressed onto "
        "the specimen at the gauge marks; a bonded gauge on the spring reads the "
        "separation ({{fig:clipon}}). The laboratory workhorse, ISO 9513 class 0.5 or "
        "better, but it touches the specimen, adds mass, can slip at the knife edges, and "
        "must be removed before fracture.",
        "**Video extensometers** — a camera tracks two marks (or the specimen's edges) and "
        "reports their separation. Contactless, survives fracture, and reaches the same "
        "class as a clip-on with a calibrated optical scale. The reference instrument of "
        "this project, the XT-205 on a Zwick/Roell Z100 [[zwick_z100]], is one of these.",
        "**Stereo-camera Digital Image Correlation (2D and 3D DIC)** — a speckle pattern on "
        "the surface is tracked by correlation over the whole field of view. With one "
        "camera normal to a flat specimen this is 2D DIC and returns in-plane displacement "
        "and strain maps; with two calibrated cameras looking at the surface from "
        "different angles it is 3D (stereo) DIC, which triangulates every point and adds "
        "out-of-plane motion and shape, so that curved or bending surfaces are measured "
        "correctly [[sutton2009, pan2018]]. The most information of the four, at the cost "
        "of a speckle, a calibration target, two cameras for 3D, and computation.",
    ])
    R.fig("ext_clipon.png",
          "Schematic of a clip-on extensometer, the instrument DIC replaces: knife edges "
          "touch the gauge marks and a strain gauge on the spring reads their separation.",
          width_cm=11.0, label="clipon")
    R.p("The two-marker DIC channel of this project sits between the third and fourth "
        "families. It is a video extensometer in what it returns — one axial strain from "
        "two marks — and a DIC instrument in how it is built: the marks are found by "
        "image processing on every frame, with no dedicated optics, no calibration target "
        "and no vendor software.", align="justify")

    # ------------------------------------------------------------------ 2.4
    R.h2("Digital Image Correlation and its two-marker form")
    R.p("Digital Image Correlation [[sutton2009]] measures deformation by locating the same "
        "physical points in successive images. In the full-field method a reference image "
        "is divided into subsets, each subset is searched for in the deformed image by "
        "maximising a correlation coefficient, and the resulting displacement field is "
        "differentiated to give strain. Good practice for the method — speckle size, subset "
        "size, calibration, uncertainty reporting — is codified by the International DIC "
        "Society [[idics2018]].", align="justify")
    R.p("The two-marker form discards the field and keeps the principle. Two high-contrast "
        "markers are placed on the gauge; each is located on every frame; their separation "
        "L in pixels is the measurand. With L₀ the separation frozen at the start of the "
        "test (the *tare*), the axial strain is", align="justify")
    R.eq("ε = (L − L₀) / L₀ = (Px − Px₀) / Px₀", "2.4")
    R.p("{{fig:px2strain}} applies Equation 2.4 to two real frames of one pull: the "
        "separation frozen on the reference frame, the separation measured on a later "
        "frame, and the strain as their ratio. Three properties of the equation do the "
        "work of this project:", align="justify")
    R.bullets([
        "**Strain is a ratio of pixel counts.** The optical scale in px/mm cancels. No "
        "calibration target is needed for strain, and a small error in the scale does not "
        "propagate into ε — it only affects the conversion of L to millimetres, which the "
        "strain never uses.",
        "**The marker centroid is a sub-pixel quantity.** A marker covering thousands of "
        "pixels has a centroid known to a small fraction of a pixel, because the centroid "
        "averages over every pixel of the blob. The channel's resolution is therefore far "
        "finer than one pixel over the gauge.",
        "**The reference Px₀ is frozen once and never re-estimated.** Everything after "
        "the tare is measured against the same number, so the strain record cannot drift "
        "through re-referencing; if Px₀ is wrong, every strain is wrong by the same "
        "factor, which is a scale error and not noise.",
    ])
    R.fig("report_px2strain.png",
          "From pixels to strain on two real frames of specimen S26: the marker separation "
          "frozen on the reference frame (L₀) and measured on a later frame (L); the strain "
          "is their ratio (Equation 2.4), computed by the script from the frames shown.",
          width_cm=15.0, label="px2strain")
    R.p("The price of the reduction is that only the average strain between the markers is "
        "measured. A specimen that necks between the markers reports the average of a "
        "localised and an unloaded region; a specimen that necks outside them reports the "
        "elastic unloading. Both cases occur in this study and are noted where they "
        "affect a number.", align="justify")
    R.h3("Good practice for DIC, and what it asks of a rig")
    R.p("The International DIC Society's good-practices guide ({{fig:idics}}) is a 166-page "
        "reference rather than a standard, but it is the closest thing the method has to "
        "one, and its second edition [[idics2018]] was read at the start of this project as "
        "a specification for the rig rather than as background. Its requirements fall into "
        "two groups, and the distinction matters for a two-marker channel.", align="justify")
    R.fig("DIC good practices book.png",
          "The reference this project was built against: the International DIC Society's "
          "*A Good Practices Guide for Digital Image Correlation*, Edition 2, October 2025. "
          "Ten sections covering principles, rig setup, the factors that affect a result, "
          "calibration, running the test, analysis, and minimum reporting requirements.",
          width_cm=8.0, label="idics")
    R.p("The first group is about the **rig**, and applies to any DIC measurement including "
        "this one. The camera should have a global shutter and a monochrome sensor, and "
        "every automatic function — exposure, gain, white balance — should be disabled, "
        "because an automatic adjustment mid-test changes the grey levels the analysis "
        "depends on. The lens should be a fixed focal length with lockable focus and "
        "aperture rings, set once and locked. The mount should be rigid and *decoupled from "
        "the load frame*, so that the machine's own motion does not reach the camera. The "
        "lighting should be diffuse, symmetric and locked before the test begins. Exposure "
        "should be short enough that motion blur stays under half a pixel, and long enough "
        "to put the image in the 50–80 % range of the grey scale; the frame rate follows "
        "from the test speed by the sampling theorem. Every one of these shaped a decision "
        "in Chapter 3, and the mount requirement in particular is why the camera stand "
        "stands on its own base plate with a damping pad under it (Section 3.2.1) rather "
        "than being bolted to the frame.", align="justify")
    R.p("The second group is about the **pattern and the correlation**, and applies to the "
        "full-field method rather than to two markers. {{tab:idics}} lists those numbers, "
        "because they are the specification the future 2D channel of Section 5.2 has to "
        "meet, and because they show what the two-marker reduction buys: with discrete "
        "markers there is no speckle to size, no subset to choose, no step size and no "
        "correlation criterion — the virtual strain gauge is simply the marker separation, "
        "and it is set by where the two dots are painted.", align="justify")
    R.tab([
        ("Parameter", "What the guide asks", "In the two-marker channel"),
        ("Speckle feature size", "3–5 px per feature, random, matte, ≈50 % coverage, well bonded",
         "No speckle — two ≈10 000 px sprayed markers instead"),
        ("Subset size", "31–41 px as a starting point; must contain 3–5 speckles",
         "Not applicable — the marker is segmented, not correlated"),
        ("Step size", "1/3 to 1/5 of the subset size", "Not applicable"),
        ("Virtual strain gauge", "The physical gauge length over which strain is reported",
         "The marker separation itself: 80 mm or 45 mm, chosen when the dots are painted"),
        ("Aperture", "Sets depth of field; set once and lock", "f/8 on a lockable-ring lens"),
        ("Exposure", "Motion blur < 0.5 px; aim for 50–80 % grey level",
         "50 000 µs; at 1–2 mm/min the specimen moves micrometres per frame"),
        ("Frame rate", "From the test speed, by the sampling theorem",
         "≈20 fps, which oversamples these pull rates by a wide margin"),
        ("Reporting", "Every acquisition and analysis parameter documented",
         "{{tab:camsettings}} and the run's own CSV header, written on every save"),
    ], "The guide's pattern-and-correlation requirements, and how a two-marker channel "
       "relates to each. The rows marked not applicable are the ones the reduction removes; "
       "they return as requirements the moment the channel becomes full-field.",
       col_widths_cm=(3.4, 6.6, 6.0), font=8.5, label="idics")
    R.p("The guide also names the path this project took. Its own recommended entry point "
        "is a flat tensile specimen, a single camera and a virtual extensometer, moving to "
        "full 2D-DIC afterwards — which is exactly the channel built here, and exactly the "
        "order of the future work in Section 5.2.", align="justify")

    R.h3("In-house and open-source DIC systems")
    R.p("Building one's own DIC instrument is an established practice, and the open "
        "literature documents several systems that a laboratory can reproduce. Blaber, "
        "Adair and Antoniou released Ncorr [[blaber2015]], an open-source 2D DIC code in "
        "MATLAB with subset-based correlation, and validated it against commercial "
        "software on standard image sets; Belloni et al. released py2DIC [[belloni2019]], "
        "a Python implementation validated on tensile tests with a consumer camera; "
        "Atkinson and Becker showed that a working 2D DIC code fits in 117 lines of MATLAB "
        "[[atkinson2020]], which makes the method teachable line by line; and Olufsen, "
        "Andersen and Fagerholt published µDIC [[olufsen2020]], a Python toolkit with a "
        "finite-element mesh formulation aimed at research laboratories that want to "
        "modify the method rather than buy it. All four are full-field correlation codes: "
        "they need a speckle, a calibration and a subset size, and they run offline on "
        "recorded images. The channel built here sits below them in the hierarchy — two "
        "markers, one strain, no speckle — and above them in one respect: it runs live "
        "inside the machine's control loop, with the guards and protocols of Chapter 3 "
        "built around it, and it was validated against a certified instrument on the "
        "instrument's own footage. The open-source codes are the natural next layer, "
        "which is why the 2D-DIC item of Section 5.2 starts from them.", align="justify")

    # ------------------------------------------------------------------ 2.5
    R.h2("Image formation, thresholding and the noise floor")
    R.h3("From light to grey level")
    R.p("A monochrome industrial camera converts the light falling on each photodiode "
        "during the exposure time into a count, scaled by the analogue gain and, "
        "optionally, a gamma curve, into an 8-bit grey level. For the marker to be found "
        "reliably it must be separated from the background in grey level by a margin "
        "much larger than the sensor noise. Two variables set that margin: the "
        "**exposure time**, which trades signal against motion blur and frame rate, and the "
        "**lighting**, which sets the contrast between marker and specimen. Gamma, applied "
        "after exposure, redistributes the grey levels — a gamma below one lifts the dark "
        "tones and compresses the highlights, which widens the usable margin when the "
        "marker is dark on a light specimen.", align="justify")
    R.h3("Thresholding: Otsu and the fixed threshold")
    R.p("The marker is segmented from the frame by thresholding: every pixel above (or "
        "below) a grey level T is foreground. Otsu's method [[otsu1979]] chooses T "
        "automatically as the level that minimises the within-class variance of the two "
        "resulting classes — equivalently, that best separates the two peaks of the "
        "grey-level histogram, as {{fig:otsu_explain}} illustrates. It needs no parameters "
        "and adapts to the lighting, which makes it the right default for an operator who "
        "has not tuned anything.", align="justify")
    R.p("Otsu's method has a known failure mode. It assumes the histogram is bimodal with "
        "comparable populations. When one class is tiny — two small markers on a large "
        "specimen — the histogram has one dominant peak and Otsu's T slides towards it, "
        "so the threshold lands on the wrong side of the valley. The symptom is a marker "
        "that grows or shrinks with the lighting, and a centroid that moves with it. The "
        "remedy is a **fixed threshold** chosen once from the histogram valley, with the "
        "polarity (marker darker or lighter than the specimen) set explicitly. This "
        "project keeps both: Otsu as the default and a fixed threshold as the preset for "
        "each material, selected on the evidence of Section 4.7.", align="justify")
    R.fig("otsu_explain.png",
          "Otsu's threshold on a bimodal histogram: T is placed where the between-class "
          "variance is maximal, which separates the two peaks. The method fails when one "
          "class is very small, as it is for two markers on a large specimen.",
          width_cm=14.0, label="otsu_explain")
    R.h3("Marker detection and the centroid")
    R.p("After thresholding, connected components are labelled and filtered by area and "
        "circularity, so that a scratch, a shadow edge or the grip does not pass as a "
        "marker. The centroid of each surviving blob is its area-weighted mean position, "
        "computed from the image moments. For a blob of N pixels whose edge pixels each "
        "carry an uncertainty of about half a pixel, the centroid uncertainty scales as "
        "1/√N — for the ≈10 000-pixel markers used here, a few hundredths of a pixel.",
        align="justify")
    R.h3("The noise floor and how it scales")
    R.p("The strain noise follows from Equation 2.4 by propagation. If each centroid has an "
        "uncertainty δ (in pixels) and the two are independent, the separation has an "
        "uncertainty √2·δ and the strain", align="justify")
    R.eq("σ_ε = √2 · δ / Px₀", "2.5")
    R.p("Two consequences are testable and were tested. First, the noise floor in strain "
        "is inversely proportional to the reference pixel span: a gauge that spans twice "
        "as many pixels has half the strain noise for the same centroid quality. Second, "
        "the noise floor does not depend on the strain itself, so it can be measured on an "
        "unloaded specimen and used as a specification. Section 4.4 reports the measured "
        "floor (tens of microstrain) and the 1/Px₀ scaling, which matched the prediction "
        "to two decimals. The other side of the same coin is framing: {{fig:pxmm_tradeoff}} "
        "shows that more pixels per millimetre means less specimen in the frame, so a "
        "tighter framing lowers the noise but loses a marker earlier in the pull.",
        align="justify")
    R.fig("pxmm_tradeoff.png",
          "The optical trade-off: more pixels per millimetre means less specimen in frame. "
          "The XT-205 at 27.9 px/mm sees 88 mm and loses a marker at 0.7 % strain on an "
          "80 mm gauge; the PPD-UTM at 21.0 px/mm sees 112 mm and keeps both markers to "
          "31 %.", width_cm=16.0, label="pxmm_tradeoff")
    R.h3("Modulus from a noisy curve")
    R.p("The modulus is a slope, and a slope from noisy data has its own uncertainty. For a "
        "least-squares line through n points spanning a stress range Δσ with strain noise "
        "σ_ε, the relative uncertainty of the slope is of order σ_ε·E/(Δσ·√n). With the "
        "noise floor of this channel, a 15 MPa fit window and a few hundred frames, the "
        "modulus uncertainty from noise alone is well under one per cent — smaller than "
        "the specimen-to-specimen scatter. What limits the modulus in practice is not "
        "noise but the *choice of window*: polymers have no sharp linear region, so the "
        "slope depends on where it is taken. {{fig:e_method}} compares the two candidate "
        "rules on one run. This report searches for the steepest straight run and reports "
        "its position (Section 3.9); on the same runs, that rule lowers the run-to-run "
        "scatter of the modulus from 16 % to 9.6 % for PLA, 13.8 % to 11.3 % for PETG and "
        "5.3 % to 1.2 % for TPU compared with a fixed 0.05–0.40 % strain window, while both "
        "rules stay inside the published bands.", align="justify")
    R.fig("e_method.png",
          "The two candidate modulus rules on one run (S26): a fixed 0.05–0.40 % strain window "
          "against the steepest straight run (0.42–0.68 % here). The steepest run repeats "
          "better on all three materials and both rules stay inside the published bands.",
          width_cm=16.0, label="e_method")

    # ------------------------------------------------------------------ 2.6
    R.h2("Closed-loop test protocols")
    R.p("A tensile test in displacement control is open-loop with respect to the specimen: "
        "the crosshead moves at a set rate regardless of what the force does. Several "
        "material questions need the machine to *hold* or *track* a force or strain "
        "instead, which requires a control loop closed on the measurement. The rig "
        "implements six such protocols. {{fig:protocols}} sketches the force and strain "
        "history of each, idealised from the standards and textbooks that define them "
        "[[astm_d2990, iso899, astm_d7791, findley1976, ward2013]]; the rig's own "
        "measured versions are in Section 4.10.", align="justify")
    R.fig("report_protocols.png",
          "The six closed-loop protocols as schematic force (blue) and strain (red) "
          "histories, idealised from their descriptions in ASTM D2990 and ISO 899-1 (creep, "
          "relaxation), ASTM D7791 (cyclic) and the viscoelasticity texts of Findley and "
          "of Ward and Sweeney. Not measured data.", width_cm=16.0, label="protocols")
    R.h3("Staircase (stepped load hold)")
    R.p("The force is raised in steps and held at each level. Two things are measured at "
        "once. The *loop's* quality is the overshoot on arrival at a step and the time it "
        "takes to settle — a proportional controller with too much gain overshoots, one "
        "with too little arrives slowly. The *material's* response is the strain that "
        "continues to grow during the hold at constant force, which is short-term creep; "
        "on a polymer the creep during a 60 s hold is visible at the microstrain level and "
        "grows with the stress level. A staircase is therefore also a quick way to obtain "
        "a stiffness at several stress levels from one specimen.", align="justify")
    R.h3("Cyclic loading")
    R.p("The force follows a sine (or triangle) between two levels at a set period. ASTM "
        "D7791 [[astm_d7791]] defines the uniaxial fatigue test for plastics in exactly "
        "this form — sinusoidal by default, at frequencies of a few hertz or lower to avoid "
        "self-heating, with the stress kept below the proportional limit. Plotting force "
        "against strain over one cycle gives a hysteresis loop: the strain lags the force "
        "because the polymer is viscoelastic, the *area* of the loop is the energy "
        "dissipated per cycle, and the *slope* of the loop is the dynamic stiffness. On a "
        "damaged specimen the loop area and the unloading stiffness both fall with cycle "
        "count, which is how fatigue damage is tracked. The control metric is the "
        "peak-tracking error, the difference between the commanded and the reached "
        "peak force.", align="justify")
    R.h3("Creep")
    R.p("A constant force is applied and strain is recorded against time. ASTM D2990 "
        "[[astm_d2990]] and ISO 899-1 [[iso899]] specify the test: a fixed load applied "
        "quickly and held, with strain read at logarithmically spaced times over hours to "
        "thousands of hours, and the results reported as creep strain, creep modulus "
        "(stress divided by the time-dependent strain) and, at higher loads, time to "
        "rupture. The classical creep curve has three stages: *primary* creep, in which "
        "the strain rate decreases; *secondary* creep, in which it is nearly constant; and "
        "*tertiary* creep, in which it accelerates to failure. For polymers below their "
        "yield stress the primary stage is described well by the Findley power law "
        "[[findley1976]],", align="justify")
    R.eq("ε(t) = ε₀ + m · tⁿ", "2.6")
    R.p("with ε₀ the instantaneous strain, m a stress-dependent amplitude and n an exponent "
        "typically between 0.2 and 0.5; a fit of n is a compact way to say whether a "
        "measured curve has the decelerating shape of genuine creep or the linear shape "
        "of instrument drift, which is how Section 4.10 uses it.", align="justify")
    R.h3("Stress relaxation")
    R.p("The complement of creep: a constant strain is imposed and the force decays. "
        "Relaxation is the direct view of the polymer's viscoelasticity — the ratio "
        "σ(t)/ε₀ is the relaxation modulus E(t), which for a linear viscoelastic solid is "
        "a sum of exponentials with a spectrum of relaxation times, and for real polymers "
        "is usually described by a stretched exponential or a power law [[ward2013]]. "
        "For the DIC rig, relaxation is also the sharpest test of the strain channel's "
        "stability, since the strain must be *held* by the loop using the camera as the "
        "sensor: any drift in the strain reading becomes a crosshead motion.", align="justify")
    R.h3("Progressive cyclic")
    R.p("Cycles of increasing amplitude, each returning to a low load. Every unload "
        "separates the strain recovered on unloading (elastic plus delayed-elastic) from "
        "the strain that remains (plastic), so one specimen yields the onset and growth "
        "of permanent strain as a function of peak stress, and the unloading slope of "
        "each cycle gives a stiffness at that damage level.", align="justify")
    R.h3("Staircase to fracture")
    R.p("A staircase continued until the specimen breaks. It gives a modulus at each "
        "step and a fracture stress reached under near-static loading — a slower path to "
        "failure than a constant-rate pull, and therefore a lower apparent strength for a "
        "rate-sensitive polymer. Run on a specimen that has already been cycled, it "
        "measures residual strength, the quantity used in Section 4.10 to price fatigue "
        "damage.", align="justify")
    R.h3("The loop itself")
    R.p("The controller is a proportional controller on the load-cell (or DIC) error with "
        "a rate limit, running at the rig's control period. Its performance is governed "
        "by the delay in the sensing path — for force, the serial round-trip to the "
        "controller; for strain, the camera exposure plus the detection latency — and by "
        "the stiffness of the specimen, since a stiff specimen converts a small crosshead "
        "step into a large force step. Section 4.10 reports the loop's tuning history from "
        "45 N to about 6 N of overshoot.", align="justify")

    # ------------------------------------------------------------------ 2.7
    R.h2("The materials: PLA, PETG and TPU")
    R.p("Three fused-filament polymers were tested, chosen to span the property space: a "
        "stiff and brittle one, an intermediate one, and a very soft one. Their published "
        "ranges, as collected from datasheets and the literature, are the *bands* against "
        "which the rig's measurements are judged in Section 4.8; {{tab:bands}} collects "
        "them.", align="justify")
    R.tab([
        ("Material", "E (MPa)", "UTS (MPa)", "εf (%)", "Character", "Sources"),
        ("PLA (polylactic acid)", "2000–3500", "32–60", "2–8", "Stiff, brittle; sharp fracture",
         R.cite("prusament_pla", "addnorth_epla_tds", "tymrak2014", "chacon2017")),
        ("PETG (PET-glycol)", "1500–2100", "30–50", "5–25", "Ductile; necks and draws",
         R.cite("prusament_petg", "durgashyam2019", "hsueh2021")),
        ("TPU (thermoplastic polyurethane)", "12–30", "25–40", "400–700",
         "Elastomer; huge strain, low modulus", R.cite("tpu_tds_ultimaker", "tpu_tds_ninjaflex")),
    ], "Published property bands for the three printed polymers, as used for the literature "
       "comparison in Section 4.8. Bands are for printed specimens where the source gives "
       "them, otherwise for the filament datasheet.", col_widths_cm=(3.4, 2.0, 2.0, 1.6, 4.0, 3.0),
       font=9, label="bands")
    R.p("Printed parts are anisotropic and porous, so their properties depend on raster "
        "orientation, layer height, infill and print temperature as much as on the "
        "polymer [[tymrak2014, chacon2017, hohimer2017]]. Two of those variables were "
        "studied here: **infill density**, where a 50 % gyroid infill leaves a shell "
        "carrying most of the load and an interior that mostly adds compliance, so both "
        "strength and modulus fall by roughly the ratio of solid cross-section; and "
        "**moisture**, treated in the next section. PLA in particular is sensitive to both. "
        "The PLA used throughout was a single brand and spool where the comparison "
        "required it [[addnorth_pla_product, addnorth_epla_tds]]. How the rig's own "
        "numbers fall against these bands is a result, and is reported in Section 4.8.",
        align="justify")

    # ------------------------------------------------------------------ 2.8
    R.h2("Filament moisture and its effect on strength")
    R.p("PLA is hygroscopic: the filament absorbs water from the air, and the water "
        "matters twice. In the printer's hot end, absorbed water flashes to steam, "
        "producing bubbles, voids and a rougher extrusion; and during storage and "
        "printing the ester bonds of the polymer hydrolyse, lowering the molecular weight. "
        "Both mechanisms weaken the printed part, and both are functions of exposure time "
        "and relative humidity.", align="justify")
    R.p("The literature quantifies the effect. Hamid et al. [[hamid2022]] exposed PLA "
        "filament to ambient humidity and measured a tensile-strength loss of about 8.5 % "
        "after 24 hours and about 11 % after 150 hours, while filament stored under vacuum "
        "with desiccant showed no loss. Quader et al. [[quader2024]] conditioned PLA/PBS "
        "filament at controlled relative humidity and found the tensile properties held "
        "within 3.7 % of the dry value up to 65 % RH, but that three months at room "
        "conditions cost 24–36 % of the strength, accompanied by a 50 % rise in melt-flow "
        "index (a proxy for chain scission) and a rise in part porosity from 1.2 % to "
        "3.0 %. Absorption saturates at under 0.7 wt % after a week at 80 % RH — a small "
        "mass with a large effect. Manufacturers' guidance is consistent: store dry, and "
        "dry the spool before printing if it has been open for more than a day "
        "[[aco_humidity]].", align="justify")
    R.p("For this project the practical consequence is that **specimens printed from "
        "different spools, or from the same spool weeks apart, are not the same "
        "material**, and that a strength difference of several per cent between two "
        "batches is expected rather than surprising. This is the frame for the "
        "ultimate-strength gap in the laboratory comparison (Section 4.2), for the "
        "batch-to-batch spread in Section 4.8, and for the humidity study of Section 4.11.",
        align="justify")

    # ------------------------------------------------------------------ 2.9
    R.h2("Product carbon footprint of a development project")
    R.p("A product carbon footprint (PCF) is the sum of the greenhouse-gas emissions and "
        "removals attributable to a product or activity over a defined boundary, expressed "
        "in kilograms of CO₂ equivalent. It is a life-cycle assessment restricted to one "
        "impact category, climate change, and it is governed by ISO 14067 [[iso14067]], "
        "which builds on the general LCA standards ISO 14040 and 14044 "
        "[[iso14040, iso14044]] and is paralleled by the GHG Protocol's Product Standard "
        "[[ghg_product]]. The standards prescribe the same sequence of steps.", align="justify")
    R.numbered([
        "**Goal and scope.** State what is being assessed and why, and define the "
        "*functional unit* — the quantity the result is expressed per (here: one "
        "development project, and secondarily one recorded test).",
        "**System boundary.** Decide which life-cycle stages and which activities are "
        "inside the assessment. A cradle-to-grave study covers raw materials, "
        "manufacture, distribution, use and end of life; a *partial* footprint covers a "
        "declared subset, and ISO 14067 requires the exclusions and the cut-off rules to "
        "be stated.",
        "**Life-cycle inventory.** For every activity inside the boundary, quantify the "
        "flows — kilowatt-hours of electricity, kilograms of material, kilometres of "
        "transport — from measurement where possible and from documented estimates "
        "otherwise, and record the data quality of each.",
        "**Characterisation.** Convert each flow to emissions with an *emission factor* "
        "(kg CO₂e per unit of flow), and convert each greenhouse gas to CO₂ equivalent with "
        "its 100-year global warming potential from the IPCC [[ipcc_ar6]]. For "
        "electricity the factor is the grid mix of the place and time of use; a "
        "*location-based* factor uses the average grid, a *market-based* one the "
        "contracted supply.",
        "**Interpretation and reporting.** Sum the contributions, attribute them to "
        "activities (contribution analysis), assess uncertainty and sensitivity to the "
        "assumptions, and report the result with the boundary, the functional unit and the "
        "data sources so that it can be reproduced.",
    ])
    R.p("In its simplest form the calculation is", align="justify")
    R.eq("PCF = Σᵢ  Aᵢ · EFᵢ", "2.7")
    R.p("with Aᵢ the activity data of item i (for example, hours of use multiplied by power "
        "draw, giving kWh) and EFᵢ its emission factor. For an engineering development "
        "project the activities are hours of equipment use, and the dominant factor is the "
        "electricity mix: the Swedish grid, at about 0.04 kg CO₂e/kWh [[eea_grid]], is "
        "among the cleanest in Europe, and the same inventory on the European average "
        "would read several times higher.", align="justify")
    R.p("The boundary drawn here is the *development* of the rig and its evidence — a "
        "partial footprint in the sense of ISO 14067: the desk computer for the hours it "
        "was in use on the project, the 3D printer for the specimens and fixtures, the rig "
        "itself for the hours it ran, and the AI coding agent's share of data-centre "
        "energy. Materials (filament mass, the camera's embodied carbon) and travel are "
        "excluded, and the exclusions are stated. The AI term uses a published per-prompt "
        "energy figure [[google_ai_energy]] with a band to reflect its uncertainty; "
        "printer and computer power are taken from measured and community-reported "
        "figures [[prusa_forum_power, prusa_mk4s]]. Section 4.12 gives the inventory and "
        "the result; a car-kilometre equivalent [[eea_cars]] is used only as a scale for "
        "the reader.", align="justify")
