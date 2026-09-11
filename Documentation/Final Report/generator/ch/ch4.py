# -*- coding: utf-8 -*-
"""Chapter 4 — Analysis: results and discussion, ending with the RQ answers."""


def build(R):
    R.h1("Analysis")
    R.p("This chapter presents the results in the order of the validation logic: first the "
        "channel against a certified instrument, then the sources of the remaining "
        "differences, then the channel's noise, its predictability and the effect of gauge "
        "length, then what the channel measured about the materials, the closed-loop "
        "protocols, moisture and the project's carbon footprint. It ends with the answers "
        "to the three research questions.", align="justify")

    # ------------------------------------------------------------------ 4.1
    R.h2("The strain channel in operation")
    R.p("{{fig:ui_curve}} shows what the operator sees during a pull: the stress–strain "
        "curve forming in real time with strain from the camera and stress from the load "
        "cell. {{fig:pixels}} shows the quantity underneath it — the two marker blobs on "
        "the region of interest, the pixel grid of one marker's edge, and the "
        "pixel-to-strain rule applied to the centroids. Every run in this chapter was "
        "recorded this way, at ≈20 frames per second, and the strain record is the "
        "camera's, not the crosshead's.", align="justify")
    R.fig("ppd_ui_curve.png",
          "The stress–strain curve as the application draws it during a PLA pull: strain "
          "from the camera, stress from the load cell, updated every frame.", width_cm=15.0,
          label="ui_curve")
    R.fig("ppd_pixels.png",
          "The measurand at pixel level: the two marker blobs on the region of interest, "
          "the pixel grid of one marker's edge, and the pixel-to-strain rule applied to "
          "their centroids.", width_cm=16.0, label="pixels")

    # ------------------------------------------------------------------ 4.2
    R.h2("Validation against a certified video extensometer")
    R.p("The laboratory comparison was run as the two analyses defined in Section 3.11.3. "
        "**Analysis 1** is instrument against instrument: the XT-205's certified strain on "
        "the laboratory's specimen against the rig's DIC on a matched specimen, with E, "
        "σy, UTS and εf each computed twice and independently. **Analysis 2** is method "
        "against method on the same footage: the laboratory's own XT-205 video re-measured "
        "frame by frame by the rig's post-processor, so that the specimen, the machine and "
        "the pull drop out and only the two strain calculations remain. Analysis 1 says how "
        "close two machines land; Analysis 2 says whether the rig's software is a "
        "measurement.", align="justify")
    R.h3("Analysis 1 — two rigs, two specimens, one material (Test 2)")
    R.p("The decisive Analysis 1 comparison is the second laboratory session, with the "
        "45 mm gauge. Specimen S34 was pulled on the PPD-UTM DIC rig and a specimen from "
        "the same batch (XT205-S2) on the Zwick/Roell Z100 with the XT-205 extensometer, "
        "at 2 mm/min with a 300 N preload. {{tab:test2}} compares the four headline "
        "properties and {{fig:mot2_pair}} overlays the two curves on the same "
        "preload-frozen zero; {{fig:mot2_stress}} adds the second 45 mm specimen S33.",
        align="justify")
    R.tab([
        ("Property", "PPD-UTM DIC (S34)", "XT-205 (S2)", "Difference"),
        ("Ultimate tensile strength", "48.34 MPa", "44.62 MPa", "−7.7 %"),
        ("Yield strength (0.2 % offset)", "39.23 MPa", "39.61 MPa", "+1.0 %"),
        ("Elastic modulus", "3.45 GPa", "3.23 GPa", "−6.4 %"),
        ("Strain at fracture", "5.25 %", "5.21 %", "−0.8 %"),
    ], "Analysis 1, Test 2 (45 mm gauge): the rig against the laboratory on specimens from "
       "the same batch. Differences are laboratory relative to rig.",
       col_widths_cm=(5.0, 3.8, 3.4, 3.8), label="test2")
    R.fig("mot2cmp_pair.png",
          "Analysis 1: XT205-S2 on the laboratory machine against S34 on the rig, both PLA "
          "from the same batch, both on the preload-frozen zero. UTS 44.62 against "
          "48.34 MPa (−7.7 %), fracture at 5.21 against 5.25 % strain (−0.8 %).",
          width_cm=13.5, label="mot2_pair")
    R.fig("mot2cmp_stress.png",
          "Analysis 1 with both 45 mm rig specimens: S33 and S34 (DIC strain) and the "
          "laboratory's S2 (XT-205 strain) overlaid. Yield and fracture strain coincide; "
          "the UTS and the elastic slope differ by a few per cent.", width_cm=14.0,
          label="mot2_stress")
    R.p("Yield strength and fracture strain — the two properties that depend on the strain "
        "channel most directly — agree within one per cent, and the whole curve shape "
        "matches. The modulus and the UTS differ by six to eight per cent, and Section 4.3 "
        "takes those apart: they carry a pull-speed difference and ordinary specimen "
        "scatter. But Analysis 1 is still two machines on two specimens, so specimen "
        "scatter is inside the difference; Analysis 2 removes it.", align="justify")
    R.h3("Analysis 2 — same video, same specimen, two calculation methods")
    R.p("The laboratory provided the XT-205's video of its pull. The rig's post-processor "
        "measured that video — 3 153 frames from tare to fracture — with its own detection "
        "and its own pixel-to-strain rule, and the result was compared frame by frame "
        "with the XT-205's own strain record. {{tab:samefoot}} summarises the agreement; "
        "{{fig:pp_full}} shows the whole pull with the per-frame difference beneath it, "
        "{{fig:pp_agree}} plots the two strains against each other for every frame, and "
        "{{fig:pp_strain}} shows the two records against time.", align="justify")
    R.tab([
        ("Quantity", "Value"),
        ("Frames compared", "3 153"),
        ("Fracture strain, XT-205 / post-processor", "5.21 % / 5.22 % (+0.08 %)"),
        ("Scale factor (post-processor vs XT-205)", "0.99928"),
        ("Coefficient of determination R²", "0.9999964"),
        ("Constant offset", "−55 µε = 0.069 px on a 1 255 px reference"),
        ("Elastic slope, post-processor / XT-205", "3.21–3.24 GPa / 3.23 GPa"),
    ], "Analysis 2: the rig's algorithm on the XT-205's own frames against the XT-205's "
       "record.", col_widths_cm=(8.0, 8.0), label="samefoot")
    R.fig("mot2pp_full.png",
          "Analysis 2, the whole pull: DIC strain against time from the XT-205 (red) and "
          "from the post-processor on the same frames (blue, dashed) to fracture at 5.21 "
          "and 5.22 %; below, the per-frame difference around its constant −55 µε "
          "(−0.069 px on a 1 255 px span). The shaded band is the window used for rate and "
          "noise.", width_cm=16.0, label="pp_full")
    R.fig("mot2pp_agree.png",
          "Analysis 2: post-processor strain against XT-205 strain for every one of the "
          "3 153 frames: a line of slope 0.99928 with R² = 0.9999964 and an offset of "
          "−55 µε.", width_cm=13.0, label="pp_agree")
    R.p("The two calculations agree in scale to 0.07 % and in fracture strain to 0.08 %. "
        "The residual is a constant offset of −55 µε, which on a 1 255-pixel reference "
        "span is 0.069 of a pixel — the difference between two sub-pixel centroid "
        "conventions on the tare frame, not a measurement disagreement, and it vanishes "
        "from every slope. When the modulus is fitted to the post-processed strain it "
        "lands at 3.21 GPa with the fixed window and 3.24 GPa with the steepest run, "
        "against the laboratory machine's 3.23: the slope agrees, not only the endpoints. "
        "**This is the central result of the project: given the same frames, the rig's "
        "software measures what a certified extensometer measures.**", align="justify")
    R.fig("mot2pp_strain_pp.png",
          "Analysis 2: strain against time for the laboratory's pull, measured by the "
          "post-processor from the XT-205 video; the XT-205's own record lies on top of it "
          "to the width of the line.", width_cm=14.0, label="pp_strain")
    R.h3("Test 1 — the 80 mm gauge, and why Test 2 became necessary")
    R.p("The first laboratory session used the rig's standard 80 mm gauge, and it produced "
        "only a partial record. The XT-205 stands closer to the specimen than the rig's "
        "camera — 27.9 px/mm against 20.9 — and sees a field of 88 mm. With the markers "
        "80 mm apart, a marker reaches the edge of the XT-205's field after only about "
        "0.7 % strain ({{fig:pxmm_tradeoff}}), so the extensometer's strain record stops "
        "in the first seconds of the pull, before yield. Test 1 therefore yielded a noise "
        "and rate comparison over the elastic region rather than a full curve, and the "
        "second session was run with the 45 mm gauge, which keeps both markers in the "
        "XT-205's field to fracture. That is also why the rig's 45 mm specimens S33 and "
        "S34 exist, and why Section 4.5 checks that the shorter gauge does not change the "
        "properties.", align="justify")
    R.p("What Test 1 did measure is valuable in its own right: the noise floors and the "
        "strain rates of the two channels over the same elastic window, given in "
        "{{tab:test1}} and {{fig:mot_noise}}.", align="justify")
    R.tab([
        ("Quantity", "PPD-UTM DIC", "XT-205"),
        ("Strain noise, RMS (two runs)", "23.5 / 23.6 µε", "44.9 µε"),
        ("Median absolute residual", "12 µε", "13 / 17 µε"),
        ("95th-percentile residual", "116 µε", "45 µε"),
        ("Strain rate during the pull", "7.42 × 10⁻⁴ /s", "2.67 / 4.06 × 10⁻⁴ /s"),
        ("Rig runs agreeing with each other", "0.4 %", "—"),
    ], "Test 1 (80 mm gauge, elastic window only): noise and rate of the two strain "
       "channels.", col_widths_cm=(6.0, 5.0, 5.0), label="test1")
    R.fig("mot_noise.png",
          "Test 1 noise comparison: the rig's DIC residuals (RMS 23.5 µε) against the "
          "XT-205's (44.9 µε). The rig is quieter at the centre and has a longer tail.",
          width_cm=14.0, label="mot_noise")
    R.p("The rig's channel is quieter than the laboratory's in RMS and in the median, and "
        "noisier in the tail: its 95th-percentile residual is twice the XT-205's. The tail "
        "is the occasional frame where the threshold catches an edge pixel; it is the "
        "reason the fixed threshold replaced Otsu (Section 4.7). The rate row is the "
        "explanation for the UTS gap, treated next.", align="justify")

    R.h3("How far two specimens can be trusted")
    R.p("The whole external validation rests on one laboratory session and **n = 2** "
        "specimens pulled against the XT-205. That is too small a sample to trust the "
        "agreement to the precision the percentages suggest. With two specimens there is "
        "no distribution to speak of: a single unlucky print, a single grip that seated "
        "differently, or one specimen drawn from the tail of the batch would move the "
        "−7.7 % UTS difference or the −6.4 % modulus difference by more than the effects "
        "Section 4.3 attributes them to, and nothing in the data would separate the two "
        "explanations. Two specimens can show that a difference is small; they cannot "
        "establish how small, and they cannot bound how often it is small.", align="justify")
    R.p("Two things keep the conclusion standing in spite of that. Analysis 2 does not "
        "depend on the sample size at all — it is the same video of the same pull measured "
        "two ways, so specimen scatter is removed by construction, and the scale factor of "
        "0.99928 with R² = 0.9999964 is a statement about the two calculation methods "
        "rather than about two specimens. And the rig-side repeatability is separately "
        "characterised over many more runs (Section 4.6). What is missing is the third "
        "leg: repetition of the two-machine comparison itself.", align="justify")
    R.p("**More validation at the laboratory is therefore needed**, and it is the first "
        "thing this work asks of whoever continues it. A defensible campaign would take "
        "five to ten specimens from the same print batch through the XT-205 and the rig "
        "under one agreed pull rate and gauge length, so that the difference in each "
        "property could be reported as a mean with a confidence interval instead of a "
        "single number, and so that the rate and seating effects of Section 4.3 could be "
        "estimated from the data rather than argued from two curves. Repeating it on a "
        "second material would show whether the agreement is a property of the channel or "
        "of PLA. Until that exists, the honest reading of Section 4.2 is that the strain "
        "channel agreed with a certified instrument on the specimens tested, not that its "
        "agreement is established to a stated tolerance.", align="justify")

    # ------------------------------------------------------------------ 4.3
    R.h2("Where the remaining differences come from")
    R.p("The two properties that disagreed by more than a per cent in {{tab:test2}} — UTS "
        "at −7.7 % and modulus at −6.4 % — were each traced to causes that are not the "
        "strain measurement.", align="justify")
    R.h3("Pull rate")
    R.p("The rig pulled at 2.21 times the laboratory's strain rate (7.42 against 2.67–4.06 "
        "× 10⁻⁴ /s in Test 1; {{fig:mot_rate}}). The speed the operator enters is the "
        "crosshead's, in mm/s — 0.1 mm/s on the rig against 2 mm/min in the laboratory — "
        "and it is open-loop with respect to the specimen: nothing tracks whether the "
        "gauge is stretching at that rate. Polymers are strain-rate sensitive: a faster "
        "pull gives a higher apparent strength and a slightly higher modulus, because the "
        "chains have less time to relax. The rate effect moves the slope more than the "
        "UTS, and on its own predicts under 1 % of the stress gap; the open item on the "
        "roadmap — one pull at the laboratory's 2 mm/min — is the direct test.",
        align="justify")
    R.fig("mot_rate.png",
          "Strain rate against time for Test 1: the rig's crosshead schedule gives 2.21× "
          "the laboratory's rate at the gauge.", width_cm=14.0, label="mot_rate")
    R.h3("Grip seating and machine compliance")
    R.p("The DIC channel makes it possible to measure how much of the crosshead's motion "
        "reaches the gauge: on the rig, 19–29 % during the elastic region "
        "({{fig:share}}), the rest being the printed grips seating and the load train "
        "stretching. About half of the early crosshead travel, under 1 % strain, is eaten "
        "by slack in the grips before the gauge feels anything, and the four rig runs "
        "cluster at 21 % of travel reaching the gauge — a joint that either seats or does "
        "not. This has no effect on a DIC-measured modulus — that is the point of the "
        "channel — but it bends the toe of the curve, delays the moment at which the "
        "specimen is fully loaded, and the laboratory's grips seat differently from the "
        "rig's printed ones.", align="justify")
    R.fig("motpp_share.png",
          "Share of crosshead motion that reaches the gauge, measured by DIC: 19–29 % in "
          "the elastic region. A crosshead-based strain would be too large by a factor of "
          "three to five.", width_cm=13.0, label="share")
    R.h3("Specimen and batch")
    R.p("The two specimens of Analysis 1 were printed from the same spool but were "
        "different objects, printed at different times. How much that alone is worth can "
        "be read from the rig's own PLA record, where the same material was pulled as a "
        "pilot and then as a batch printed eight days later, and again two months later. "
        "{{tab:batches}} gives the individual specimens and {{tab:batchoff}} the offsets.",
        align="justify")
    R.tab([
        ("Specimen", "Printed / pulled", "UTS (MPa)", "E (GPa)", "σy (MPa)", "εf (%)"),
        ("S7 (pilot)", "June, day 0", "47.82", "3.003", "45.42", "2.98"),
        ("S8", "June, day 8", "44.83", "2.686", "42.99", "5.17"),
        ("S9", "June, day 8", "45.47", "3.075", "42.30", "7.44"),
        ("S10", "June, day 8", "46.82", "2.896", "44.39", "7.32"),
        ("S11", "June, day 8", "46.10", "2.886", "43.72", "5.00"),
        ("Batch mean S8–S11", "", "45.81", "2.886", "43.35", "6.23"),
        ("Batch CV S8–S11", "", "1.9 %", "2.1 %", "1.8 %", "21 %"),
        ("S12, S13, S24–S26 mean", "August (≈2 months)", "46.78", "3.207", "41.02", "5.67"),
    ], "The 100 % PLA specimens from one spool: the pilot, the batch printed eight days "
       "later, and the August series. Modulus values follow the analysis convention of "
       "Section 3.9.", col_widths_cm=(3.6, 3.2, 2.2, 2.0, 2.2, 2.0), font=9, label="batches")
    R.tab([
        ("Comparison", "UTS", "E", "σy", "εf"),
        ("Batch (day 8) vs pilot (day 0)", "−4.2 %", "−3.9 %", "−4.6 %", "+109 % (1.7–2.5×)"),
        ("Within the day-8 batch (CV, n = 4)", "1.9 %", "2.1 %", "1.8 %", "21 %"),
        ("Same-day pair S25 / S26", "2.2 %", "11.4 %", "4.7 %", "31.6 %"),
        ("August series vs pilot", "−2.2 %", "+6.8 %", "−9.7 %", "+90 %"),
        ("Analysis 1: laboratory vs rig", "−7.7 %", "−6.4 %", "+1.0 %", "−0.8 %"),
    ], "Offsets between batches and within batches, against the Analysis 1 gap.",
       col_widths_cm=(5.4, 2.2, 2.2, 2.2, 4.0), font=9, label="batchoff")
    R.p("Three things follow. Within one batch, strength repeats to about 2 % and modulus "
        "to about 2 % — that floor is ordinary print scatter, not moisture. Between the "
        "pilot and the batch printed eight days later off the same spool the strength "
        "fell 4.2 %, the modulus 3.9 %, and the fracture strain doubled — both arrows in "
        "the direction the moisture literature predicts (Section 4.11). And the Analysis 1 "
        "gap of −7.7 % in UTS is therefore about half explained by a batch offset of the "
        "size the rig has already seen on its own, with pull rate and grip seating "
        "supplying the rest; the strain channel is ruled out by Analysis 2. The modulus "
        "gap has the same structure plus the window sensitivity of Section 2.5: on the "
        "same frames the two fits agree, as {{fig:pp_slope}} shows.", align="justify")
    R.fig("mot2pp_slope_pp.png",
          "Elastic-slope fit on the post-processed strain from the laboratory's frames: "
          "3.21–3.24 GPa depending on the window, bracketing the laboratory's 3.23.",
          width_cm=13.0, label="pp_slope")

    # ------------------------------------------------------------------ 4.4
    R.h2("Noise floor and measurement uncertainty")
    R.p("The noise floor was measured with the crosshead stopped and the specimen at "
        "preload ({{fig:s13_noise}}). Over a 10 s window the standard deviation of the DIC "
        "strain is 11.9 µε on the black specimen S13 and 13.3–15.4 µε on the white S25 and "
        "S26; over a 900 s window it is 26 µε, because slow drift enters. All are below "
        "the 44.9 µε of the reference instrument in Test 1. The RMS moves with the window "
        "length, so specimens are always compared over the same window.", align="justify")
    R.fig("s13_noise.png",
          "The noise floor on three specimens over the last 10 s of a stationary hold: S13 "
          "(black) 11.9 µε, S25 and S26 (white) 15.4 and 13.3 µε — and the RMS against "
          "window length, which is why windows must be equal.", width_cm=16.0,
          label="s13_noise")
    R.p("Equation 2.5 predicts that the noise scales as 1/Px₀. This was tested by "
        "comparing the 80 mm gauge (1 675 px at 20.9 px/mm) with the 45 mm gauge (939 px), "
        "the two geometries of {{fig:gauge_geom}}: the prediction for the noise ratio was "
        "1.78, and the measured ratio was 1.78. The channel's noise is therefore centroid "
        "noise, and it can be lowered by putting more pixels across the gauge — a longer "
        "gauge, a tighter framing or a higher-resolution sensor — without any change to "
        "the software.", align="justify")
    R.fig("gauge_geometry.png",
          "The 1/Px₀ test: the same specimen geometry, section and pull rate, with the dots "
          "sprayed 80 mm apart (1 675 px) or 45 mm apart (939 px). The predicted noise ratio "
          "is 1.78; the measured ratio was 1.78.", width_cm=16.0, label="gauge_geom")
    R.p("Marker colour matters at the margin. On a black specimen with white markers the "
        "floor was 11.9 µε; on the white specimens with black markers, 13.3–15.4 µε. The "
        "difference is the grey-level margin: with gamma 0.5 lifting the dark tones, the "
        "white-on-black case has a slightly cleaner edge. Both are far below the "
        "specimen-to-specimen scatter in any property, so the practical uncertainty of a "
        "modulus on this rig is set by the specimen and the fit window, not by the camera; "
        "{{fig:est_noise}} traces how the strain noise propagates into a fitted modulus.",
        align="justify")
    R.fig("est_noise_method.png",
          "How the uncertainty of a fitted modulus is estimated from the strain noise and "
          "the fit window: at the measured floor, noise contributes well under one per "
          "cent, and the window choice dominates.", width_cm=13.0, label="est_noise")

    # ------------------------------------------------------------------ 4.5
    R.h2("Gauge length: 80 mm against 45 mm")
    R.p("The 45 mm gauge was introduced for the laboratory comparison (Section 4.2.3) and "
        "for TPU. It roughly halves the pixel span (939 against 1 675 px at the same "
        "framing), so by Equation 2.5 it nearly doubles the noise, and it moves the markers "
        "closer to the shoulders. Before the 45 mm results are used for anything, the "
        "question is whether the shorter marker spacing changes the properties. "
        "{{tab:gaugeoff}} answers it with the two matched pairs — S25 and S26 at 80 mm, "
        "S33 and S34 at 45 mm, same specimen geometry, same 80 mm² section, same 0.10 mm/s "
        "pull — and {{fig:gauge_pair}} and {{fig:gauge_scatter}} show the pairs to "
        "fracture and the strain difference at matched stress.", align="justify")
    R.tab([
        ("Quantity", "80 mm (S25, S26)", "45 mm (S33, S34)", "45 vs 80 mm", "Within-pair spread"),
        ("UTS (MPa)", "46.16 / 47.17 → 46.67", "47.09 / 48.34 → 47.72", "+2.2 %", "2.2 % / 2.6 %"),
        ("E (GPa)", "3.167 / 3.549 → 3.358", "3.174 / 3.451 → 3.313", "−1.3 %", "11.4 % / 8.4 %"),
        ("σy (MPa)", "39.82 / 41.75 → 40.79", "39.43 / 39.31 → 39.37", "−3.5 %", "4.7 % / 0.3 %"),
        ("εf (%)", "4.18 / 5.74 → 4.96", "2.95 / 5.25 → 4.10", "−17 %", "31.6 % / 56 %"),
        ("Noise floor (µε)", "≈12", "≈21", "1.78×", "as predicted by 1/Px₀"),
        ("Pixel span (px)", "1 675", "939", "0.56×", "—"),
    ], "The 80 mm and 45 mm pairs: the between-gauge offset of every property is no larger "
       "than the spread between two specimens of the same gauge. Pair values are given as "
       "specimen / specimen → mean.", col_widths_cm=(2.8, 3.6, 3.6, 2.2, 3.8), font=8.5,
       label="gaugeoff")
    R.fig("gauge_pair.png",
          "The 45 mm pair S33 and S34 to fracture, and their strain difference at matched "
          "stress: specimen scatter, not gauge, is the larger term.", width_cm=16.0,
          label="gauge_pair")
    R.fig("gauge_scatter.png",
          "The between-gauge difference in measured strain at matched stress is no larger "
          "than the scatter between two specimens of the same gauge.", width_cm=15.0,
          label="gauge_scatter")
    R.p("Strength moves by 2 %, modulus by 1 %, yield by 3.5 % — each inside the spread "
        "of the same-gauge pairs — and only the fracture strain, which is set by the "
        "specimen's largest defect, differs more, as it does between any two specimens. "
        "The noise rises by exactly the predicted factor. The gauge length therefore "
        "influences the values only to a very small extent: either gauge can be used, and "
        "the choice is a trade of noise against travel room — 80 mm for the lowest noise, "
        "45 mm when the markers must stay in a smaller field of view or a large strain "
        "must fit in the frame — not a source of bias.", align="justify")

    # ------------------------------------------------------------------ 4.6
    R.h2("Repeatability and DIC coverage")
    R.p("Two PLA specimens from the same batch, S25 and S26, pulled on consecutive runs "
        "with the same settings, give a direct repeatability check; {{tab:vc}} lists them "
        "with the other 100 % VC-series specimens and {{fig:s25s26}} overlays the pair.",
        align="justify")
    R.tab([
        ("Specimen", "UTS (MPa)", "E (GPa)", "σy (MPa)", "εf (%)"),
        ("S25", "46.16", "3.167", "39.82", "4.18"),
        ("S26", "47.17", "3.549", "41.75", "5.74"),
        ("S12", "47.78", "3.286", "41.99", "5.82"),
        ("S13", "46.33", "3.030", "42.07", "5.15"),
        ("S24", "46.47", "3.004", "39.46", "7.44"),
    ], "The 100 % PLA VC-series specimens: UTS repeats to a few per cent, fracture strain "
       "does not, which is the material rather than the channel.",
       col_widths_cm=(3.0, 3.2, 3.2, 3.2, 3.2), label="vc")
    R.fig("s25_s26_overlay.png",
          "S25 and S26 overlaid: the curves coincide to yield and diverge only in the "
          "post-yield region, where fracture is set by the specimen's largest defect.",
          width_cm=13.5, label="s25s26")
    R.p("Ultimate strength repeats to 2 %, yield to 5 %; the modulus spread of 12 % between "
        "S25 and S26 is the window sensitivity of a polymer without a sharp linear region. "
        "Across the six PLA runs the run-to-run scatter of the modulus is 16.0 % with a "
        "fixed 0.05–0.40 % window and 9.6 % with the steepest-straight-run rule, which is "
        "why that rule was adopted (Section 3.9). Fracture strain varies from 4 % to 7 % "
        "across the five specimens: fracture is nucleated by the largest print defect, and "
        "that is a property of the specimen. The fracture survey of Section 4.9 makes the "
        "same point from the other side.", align="justify")
    R.p("DIC coverage — the share of the run's frames on which both markers were found — "
        "was 27 % on S24 and 47 % on S13 in the early VC-series ({{fig:coverage}}), and "
        "rose to effectively 100 % once the fixed threshold replaced Otsu and the "
        "enclosure was in place. Coverage is reported in the HUD and stored with the run; "
        "a run with low coverage is not used for a fracture strain.", align="justify")
    R.fig("s13_coverage.png",
          "DIC coverage on specimen S13: the frames on which both markers were detected, "
          "against time. Gaps are frames the threshold lost; the strain record is not "
          "interpolated across them.", width_cm=13.5, label="coverage")

    # ------------------------------------------------------------------ 4.7
    R.h2("Otsu against a fixed threshold")
    R.p("The Otsu failure mode of Section 2.5 was measured on the rig's own recordings. "
        "The markers are a tiny class: painting them out of the frame moves Otsu's "
        "threshold by at most three grey levels on four specimens, against margins of 46–99 "
        "levels on either side of it ({{fig:otsu_setby}}). Otsu's cut is therefore set by "
        "the specimen body and the background, not by the markers it is supposed to find. "
        "On the black PLA specimen S13 it lands at 131 ({{fig:otsu_hist}}), where the "
        "bright grips bloom into the foreground along with the markers ({{fig:otsu_frame}}); "
        "the rig's fixed 149 sits in the histogram valley and the grips pull back. On "
        "white PLA Otsu (158) and the preset (150) are both in the valley and behave "
        "alike. On the translucent PETG specimen S29 the difference is decisive: Otsu "
        "found both markers on 48.5 % of the frames, the fixed threshold on 99.5 %; on S13 "
        "the two were equal at 99.8 %.", align="justify")
    R.fig("otsu_hist.png",
          "What Otsu sees: the grey-level histogram pooled over 120 frames of S13, with "
          "Otsu's 131 on the shoulder of the specimen peak and the rig's fixed 149 in the "
          "valley.", width_cm=13.0, label="otsu_hist")
    R.fig("otsu_frame.png",
          "The same S13 frame thresholded at Otsu's 131 and at the rig's 149: both find the "
          "two markers, but at 131 the bright grips bloom into the foreground.", width_cm=13.0,
          label="otsu_frame")
    R.fig("otsu_setby.png",
          "Otsu is set by the body, not the markers: painting the markers out moves the cut "
          "by 0–3 grey levels on S24, S25, S26 and S13, against margins of 46–99 levels to "
          "the nearest class on either side.", width_cm=15.0, label="otsu_setby")
    R.p("The consequence for practice is the material preset: the threshold is set once "
        "per material and polarity from the histogram valley, stored as a recipe (SF3), "
        "and Otsu is retained only as a starting point for a new material. The "
        "auto-calibration sweep (SF12) scores candidate thresholds by marker count and "
        "centroid stability and lands on the valley without the operator reading a "
        "histogram.", align="justify")

    # ------------------------------------------------------------------ 4.8
    R.h2("Three polymers against their published bands")
    R.p("The strongest test that the rig measures the material and not itself is to pull "
        "materials of very different character and check that each lands in its own "
        "published band, in the expected order. PLA, PETG and TPU do: {{tab:trio}} gives "
        "one representative specimen of each against the bands of {{tab:bands}}, "
        "{{fig:trio}} overlays the three curves and {{fig:trio_mod}} places the moduli in "
        "their bands.", align="justify")
    R.tab([
        ("Material (specimen)", "UTS (MPa)", "E (GPa)", "εf (%)", "Published band"),
        ("PLA (S25)", "46.16", "3.17", "4.13", "UTS 32–60 · E 2.0–3.5 · εf 2–8"),
        ("PETG (S30)", "41.75", "1.81", "7.81", "UTS 30–50 · E 1.5–2.1 · εf 5–25"),
        ("TPU (S37)", "2.60 (at 18.9 %, unbroken)", "0.024", "> 18.9", "UTS 25–40 · E 0.012–0.030 · εf 400–700"),
    ], "One representative specimen of each polymer against the published bands. TPU was "
       "not pulled to fracture: the 45 mm gauge reached the 30 mm travel backstop at 18.9 % "
       "strain.", col_widths_cm=(3.4, 3.4, 2.0, 2.2, 5.0), font=9, label="trio")
    R.fig("trio_curves.png",
          "PLA, PETG and TPU stress–strain on the same axes: stiff and brittle, ductile, "
          "and elastomeric, in the expected order and each within its band.", width_cm=14.5,
          label="trio")
    R.fig("trio_modulus.png",
          "The three moduli against their literature bands: PLA and PETG inside, TPU inside "
          "at the low end where the pull stopped at the travel limit.", width_cm=13.0,
          label="trio_mod")
    R.p("PLA is stiff and brittle, with a sharp fracture at 4–7 % strain. PETG yields, "
        "necks and draws: its modulus is 57 % of PLA's, its UTS 90 %, and its fracture "
        "strain twice, all inside the band. TPU is an elastomer: at 0.024 GPa its modulus "
        "is one hundred and thirtieth of PLA's, and it stretched to the rig's travel limit "
        "without a hint of failure. The TPU pull ({{fig:tpu}}) is the channel's best "
        "demonstration of range: the same two markers, tracked with the same code, gave a "
        "clean strain record at 19 % where the marker separation had grown by a fifth.",
        align="justify")
    R.fig("tpu_s37.png",
          "TPU specimen S37 on the 45 mm gauge: strain to 18.9 % at the travel backstop, "
          "with both markers tracked throughout.", width_cm=13.0, label="tpu")
    R.h3("Within-material scatter")
    R.p("Five 100 % PLA specimens pulled over two months have a UTS coefficient of "
        "variation of ≈2.5 %. The 50 % gyroid pair S27 and S28 ({{fig:s27s28}}) agree in "
        "UTS to 0.2 % (19.87 and 19.91 MPa), in fracture strain to 5 % (4.0 and 4.2 %), and "
        "in modulus to 3 % (1.22 and 1.26 GPa). The rig's repeatability on a well-printed "
        "pair is therefore better than 1 % in strength.", align="justify")
    R.fig("s27_s28_pair.png",
          "S27 and S28, the 50 % infill pair: UTS 19.87 and 19.91 MPa, the two curves "
          "indistinguishable to yield.", width_cm=13.0, label="s27s28")
    R.h3("The infill knockdown and the datasheet")
    R.p("Halving the infill to 50 % gyroid cut the UTS from ≈46 to ≈20 MPa and the modulus "
        "from ≈3.1 to ≈1.25 GPa, a knockdown factor of ≈2.4 in both ({{fig:knockdown}}). "
        "A solid shell around a 50 % interior does not carry half the load: the interior's "
        "contribution to stiffness is smaller than its volume fraction, and the knockdown "
        "of 2.4 rather than 2.0 is the expected result [[chacon2017]]. The two batches of "
        "100 % specimens differ by a factor of 1.05–1.24 in the same comparison, which is "
        "the batch effect of Section 4.3.4.", align="justify")
    R.fig("infill_knockdown.png",
          "UTS and modulus at 100 % and 50 % infill: a knockdown factor of ≈2.4 in both, "
          "against the factor of 2.0 that the volume fraction alone would give.",
          width_cm=13.0, label="knockdown")
    R.p("{{fig:lit}} puts the same numbers against the filament datasheet rather than the "
        "literature band. The 100 % PLA modulus lands on the datasheet's 2.87 GPa "
        "(k = 1.00 for the staircase top level, 0.90 for the V6 quintet) while the 100 % "
        "strength is 46 MPa against a datasheet 58 MPa — a printed part reaches the "
        "moulded stiffness but not the moulded strength, which is the usual finding for "
        "fused-filament PLA [[tymrak2014, chacon2017]]. The 50 % specimens sit at a "
        "knockdown of 2.7 in strength, consistent with the 2.4 in modulus above given "
        "their different batches.", align="justify")
    R.fig("sf9_literature.png",
          "The rig's PLA numbers against the filament datasheet: modulus on the datasheet "
          "value at 100 % infill, strength at about 80 % of it, and the 50 % infill "
          "knockdown k ≈ 2.7 in strength.", width_cm=14.0, label="lit")

    # ------------------------------------------------------------------ 4.9
    R.h2("Fracture behaviour")
    R.p("Because the channel records video, the position of every fracture relative to the "
        "markers is known. Twelve fractures were surveyed and placed on a normalised "
        "position axis along the gauge, 0 at the upper marker and 1 at the lower marker "
        "(the lower-grip side in the camera view); {{tab:fracpos}} gives the positions, "
        "{{fig:frac_map}} shows the fractured specimens and {{fig:frac_faces}} the "
        "fracture faces of the two brittle-versus-ductile cases.", align="justify")
    R.tab([
        ("Specimen", "S13", "S24", "S25", "S26", "S27", "S28", "S30", "S31", "S33", "S34"),
        ("Position", "0.15", "0.03", "0.45", "0.77", "0.42", "0.22", "0.95", "0.90", "−0.12", "0.71"),
    ], "Fracture position along the gauge, on a scale where 0 is the upper marker and 1 the "
       "lower one. A value between 0 and 1 means the specimen broke between the markers; "
       "S33's −0.12 means it broke *above* the upper marker, outside the pair. S12 and S32 "
       "are omitted: S12 parted outside the viewed gauge and S32's fracture was not on "
       "film.", font=9, label="fracpos")
    R.p("Every value but one lies between 0 and 1, which is the interval between the two "
        "markers. S33 is the exception at −0.12: its break sits above the upper marker, so "
        "both dots ended up on the lower fragment, and on this scale a break on the far "
        "side of the upper marker is negative by construction. It is not a sign error and "
        "not a different convention — it is the one specimen in the survey whose fracture "
        "fell outside the measured gauge, which is also why its fracture strain (2.95 %) is "
        "the lowest of the 45 mm pair: after the break the markers no longer straddle the "
        "failure.", align="justify")
    R.fig("frac_map.png",
          "Fracture position map for the surveyed specimens: no clustering at the markers "
          "or the grips, so the paint and the stencil do not nucleate fracture.",
          width_cm=13.0, label="frac_map")
    R.fig("report_frac_faces.png",
          "Fracture faces of PLA (brittle, flat) and PETG (ductile, drawn) specimens from "
          "the study; the character matches the stress–strain curves of Section 4.8. The PLA "
          "break is shown in the rig, moments after the auto-stop halted the crosshead.",
          width_cm=14.5, label="frac_faces")
    R.p("Fractures scatter across the gauge with no preference for the marker positions, "
        "which answers a practical worry: the paint does not weaken the specimen. The "
        "two PETG fractures near 0.9 are drawn necks that ran to the shoulder; S33 is the "
        "one specimen that broke outside the pair, which the survey records rather than "
        "hides. The brittle PLA faces are flat and perpendicular; the PETG faces are drawn "
        "and whitened.", align="justify")

    # ------------------------------------------------------------------ 4.10
    R.h2("Closed-loop protocols on the rig")
    R.p("The six advanced modes were tuned on a simulated spring plant and then on the rig, "
        "with 50 % infill PLA specimens S18–S23 as the plant. Each protocol is reported "
        "below in its own right; Appendix B lists the runs.", align="justify")
    R.h3("Staircase")
    R.p("The loop's history is a single number: the overshoot on arrival at a staircase "
        "step fell from 45.5, 46.8 and 52.6 N in the first session (T1) to 6.0, 4.8 and "
        "7.8 N after tuning (T3), with the rate-limited approach of T4 removing the last "
        "of it ({{fig:staircase}}). The holds themselves show the material: at each level "
        "the strain keeps creeping during the dwell, the short-term creep that the creep "
        "protocol then measures on its own.", align="justify")
    R.fig("sf9_staircase.png",
          "Staircase before and after tuning: overshoot at each step fell from ≈45–53 N to "
          "≈5–8 N.", width_cm=14.0, label="staircase")
    R.h3("Cyclic loading")
    R.p("The peak-tracking error fell from 71 N on the triangle test T5 to 15 N on the sine "
        "test T6.3, with the peaks converging from 528 to 500 N. The window then proved "
        "to matter more than the tracking: raising the unload floor to 400 N so that the "
        "mechanism no longer crosses its own backlash twice a cycle (T6.5 on S22, 400–"
        "1 100 N) gave six closed hysteresis loops ({{fig:hyst}}) whose area fell from "
        "14.2 to 10.9 kJ/m³ and whose unloading modulus fell from 1.49 to 1.43 GPa, both "
        "monotonically with cycle count at R² ≥ 0.99 and with the peaks held to ±3.4 N.",
        align="justify")
    R.fig("sf9_cyclic_hyst.png",
          "Cyclic loading on S22 between 400 and 1 100 N: six closed hysteresis loops, with "
          "the loop area (dissipated energy) and the unloading modulus both falling "
          "monotonically with cycle count.", width_cm=13.0, label="hyst")
    R.h3("Creep")
    R.p("Creep at 600 N (53 % of UTS) on S23 for 877 s ({{fig:creep}}) gave a net creep of "
        "+1 080 µε after a measured zero-load drift of +254 µε — from a separate 928 s "
        "baseline hold at +0.289 µε/s — was subtracted: 41 times the noise floor, with a "
        "Findley exponent of 0.48 and a decelerating primary shape, the discriminator "
        "fixed before the run for telling creep from drift. Holding the force took 172 µm "
        "of crosshead while the gauge extended 107 µm, so only 62 % of crosshead motion "
        "was specimen even in a hold.", align="justify")
    R.fig("sf9_creep.png",
          "Creep at 600 N on S23: raw DIC strain, the zero-load drift baseline measured in "
          "a separate run, and the net creep of +1 080 µε with its Findley fit.",
          width_cm=13.5, label="creep")
    R.h3("Stress relaxation")
    R.p("Relaxation is the protocol that uses the camera as the control sensor. On S18 the "
        "crosshead ramped the gauge to a target strain of 1.0 % and then froze while the "
        "loop held the DIC strain ({{fig:relax}}): the strain was held at 0.01011 with a "
        "standard deviation of 0.000024, 0.24 % of the held value, and the force decayed "
        "from 2 146 N at the start of the hold to 2 040 N after 81 s — 106 N or 4.9 % lost "
        "to relaxation, in the decelerating shape of Section 2.6.", align="justify")
    R.fig("sf9_relax.png",
          "Stress relaxation on S18: ramp to 1.0 % DIC strain, then a hold with the "
          "crosshead frozen — strain flat at 0.01011 ± 0.000024, force falling from 2 146 to "
          "2 040 N (−4.9 %) in 81 s.", width_cm=15.0, label="relax")
    R.h3("Progressive cyclic to fracture")
    R.p("T8 on S21 ran eight cycles of rising amplitude to fracture at 1 397 N, halted "
        "automatically 1.33 s after the load collapsed ({{fig:progcyc}}). Its result is "
        "the report's argument in one test: over cycles 4 to 8 the modulus measured by "
        "DIC fell from 2.32 to 1.73 GPa, a 26 % loss, while the stiffness read from the "
        "crosshead rose from 744 to 777 N/mm. The two are two springs in a row — the "
        "machine's compliance tightening as slack squeezes out while the specimen "
        "softens — and read from the crosshead alone the test says the material is getting "
        "stiffer ({{fig:stiffness}}). The hysteresis fraction fell to a minimum of 9.6 % at "
        "cycle 5 and then accelerated to 30 %, which marks the onset of damage.",
        align="justify")
    R.fig("sf9_prog_cyclic.png",
          "Progressive cyclic T8 on S21: eight rising cycles to fracture at 1 397 N; the "
          "DIC modulus falls 2.32 → 1.73 GPa while the crosshead stiffness rises; the "
          "dissipated fraction turns up at cycle 5.", width_cm=16.0, label="progcyc")
    R.fig("sf9_teach_stiffness.png",
          "Why the crosshead reads stiffer: the crosshead sees machine and specimen as two "
          "springs in a row; as the machine's coils tighten (1 095 → 1 411 N/mm) the "
          "specimen's loosen (2 325 → 1 727 N/mm), and the crosshead reading rises 4 %.",
          width_cm=16.0, label="stiffness")
    R.h3("Staircase to fracture")
    R.p("T7.2 on S18 stepped the load in eight dwells of at least five seconds to fracture "
        "at 1 388 N, halted 1.36 s later ({{fig:stairfrac}}). The force drop during each "
        "dwell is a per-level relaxation measurement, and its minimum — 1.6 % at level 4, "
        "694 N — marks the onset of yield from one specimen. The resulting strength, "
        "21.19 MPa, landed 0.9 % from the progressive-cyclic T8 (21.38 MPa) on a different "
        "specimen, which bounds protocol and specimen scatter together at n = 1 each. Run "
        "on S22 after sixteen cycles at 79 % of UTS (T7.3), the same protocol gave "
        "19.74 MPa — a residual-strength loss of 6.8 % against the same-protocol virgin "
        "run, many times the 0.9 % virgin spread, and the project's first fatigue number.",
        align="justify")
    R.fig("sf9_stair_fracture.png",
          "Staircase to fracture T7.2 on S18: eight dwells to fracture at 1 388 N, and the "
          "dwell force drop per level with its minimum at 694 N, the yield onset.",
          width_cm=16.0, label="stairfrac")
    R.h3("The one that failed, and what it taught")
    R.p("The first staircase-to-fracture attempt, T7 on the 100 % specimen S20, never "
        "fractured: the pull ground at about 2.6 kN for 118 s while the crosshead advanced "
        "only 192 µm, against the ≈3.7 kN a 100 % PLA specimen needs ({{fig:stall}}). The "
        "stall guard (SF7) proved it was a motor stall and not a fracture — the specimen "
        "came off intact — and the record of six 100 % specimens that did fracture at "
        "3.1–3.4 kN shows the ceiling is not a hard one: the drivetrain is rated far "
        "above it, so the cause is electrical (driver current or thermal derating) rather "
        "than mechanical. The guard and the hard backstops (SF15) date from this run.",
        align="justify")
    R.fig("sf9_t7_stall.png",
          "T7 on S20: the pull that never fractured — 118 s at ≈2.6 kN advancing 192 µm — "
          "against six 100 % specimens that did fracture at 3.1–3.4 kN; a stall, not a "
          "ceiling.", width_cm=16.0, label="stall")
    R.p("The loop's cost was also measured: the control path's share of the main thread "
        "fell from 700 to 285 ms per second of test after profiling, and the DIC delivery "
        "rate — frames with a strain per second, not frames grabbed — was 11.1, 8.9 and "
        "5.3 Hz on S26, S29 and S13 respectively before the ROI reduction, which is why "
        "the region of interest was cut to the gauge strip.", align="justify")

    # ------------------------------------------------------------------ 4.11
    R.h2("Humidity: the batch effect and the literature")
    R.p("The moisture question entered the project through the batch offsets of "
        "Section 4.3.4: the batch printed eight days after the pilot, off the same spool, "
        "was 4.2 % weaker and 1.7–2.5× more ductile, and the August series two months "
        "later kept the higher ductility. A spool that has been open takes up water, and a "
        "wetter filament prints a more ductile, slightly weaker part — the Hamid and "
        "Quader signatures of Section 2.8 [[hamid2022, quader2024]]: moisture sends UTS "
        "down and εf up, never one without the other, and both arrows here point the "
        "moisture way. The size is plausible too: about −4 % per extra week in room air "
        "sits between Quader's ≤3.7 % at ≤65 % RH for a week and Hamid's −8.5 % after 24 h "
        "in open humid air.", align="justify")
    R.p("What is deliberately not claimed: it is one pilot against one batch, not a trend; "
        "no humidity log exists for the print room and the spool's open-air hours were "
        "not recorded; same-day specimens still differ by about 2 %, which is ordinary "
        "print scatter and not humidity; and bed adhesion, first-layer quality and ambient "
        "temperature were not controlled either. The verdict is that humidity is a "
        "plausible, direction-consistent contributor to the batch gap and unprovable in "
        "hindsight. The decisive experiment is cheap: dry the spool (50 °C for 4 h, which "
        "recovers more than 90 % of the absorbed water), reprint two specimens and "
        "compare — if the strength rebounds toward the pilot, moisture is convicted. It "
        "is specified in Section 5.2.", align="justify")
    R.p("For the laboratory comparison the implication is direct: the −7.7 % UTS gap of "
        "{{tab:test2}} is the size of a batch effect the rig has already seen, and the two "
        "specimens were printed at different times. Moisture is the second candidate "
        "after pull rate, and the controlled experiment separates them.", align="justify")

    # ------------------------------------------------------------------ 4.12
    R.h2("Carbon footprint of the project")
    R.p("The inventory of Section 2.9, applied with Equation 2.7, gives {{tab:pcf}}; "
        "{{fig:pcf}} shows the same numbers by activity. The three electricity rows use "
        "the Swedish grid factor of 0.040 kg/kWh; the AI row uses a data-centre factor of "
        "≈0.38 kg/kWh, since the agent does not run on the Swedish grid.", align="justify")
    R.tab([
        ("Activity", "Basis", "Energy", "kg CO₂e"),
        ("Desk computer", "955 h × 60 W", "57.3 kWh", "2.29"),
        ("3D printer", "60 prints, ≈84 Wh each", "5.04 kWh", "0.20"),
        ("The rig", "7 h × 45 W", "0.315 kWh", "0.013"),
        ("AI coding agent", "195 h × 40 prompts/h × 0.24 Wh", "1.87 kWh (band 0.117–1.31 kg)", "0.71"),
        ("Total", "", "", "3.22 (2.62–3.82)"),
    ], "Product carbon footprint of the project's development. Electricity at the Swedish "
       "grid factor; the AI term at a data-centre factor with a published per-prompt "
       "energy, given with its band.", col_widths_cm=(3.2, 5.2, 4.4, 3.2), font=9, label="pcf")
    R.fig("pcf_bars.png",
          "The footprint by activity: the desk computer dominates, the rig is negligible, "
          "and the AI term is the uncertain one.", width_cm=13.0, label="pcf")
    R.p("Three readings. The whole project cost about 3.2 kg CO₂e, the equivalent of "
        "≈30 km in an average European car [[eea_cars]]; per recorded test it is 83 g. The "
        "rig itself — the machine that does the pulling — is 13 g per test, and the hours "
        "of thinking at the computer outweigh the hours of pulling by a factor of 239. And "
        "the AI term, even at the top of its band, is smaller than the desk computer: the "
        "agent's data-centre share of a prompt is less than the screen it is read on. The "
        "numbers are small because the Swedish grid is clean; on the European average "
        "factor [[eea_grid]] every row would be roughly six times larger and the ranking "
        "would not change.", align="justify")

    R.h3("The counterfactual: what if the code had been typed by hand?")
    R.p("The AI term is the one a reader is most likely to object to, so it is worth asking "
        "what it replaced. Only one term of the inventory changes under that question. The "
        "195 h of agent sessions are a subset of the 955 h of desk time; in a solo scenario "
        "those hours become the time a human would have needed to write the same 26 468 "
        "tested lines, the AI row goes to zero, and the printer, the rig and the rest of "
        "the desk time are untouched. The boundary is the same on both sides — grid "
        "electricity only, no metabolism, commuting or embodied hardware — so the two are "
        "comparable. The speed-up itself is the estimate of {{tab:ai}}, taken with the "
        "brackets Section 3.10 puts on it: ×6.7 is the ≈1 300 h figure, ×3 the floor that "
        "would still have made the project possible in the time, ×10 the pessimistic end. "
        "{{tab:pcfsolo}} and {{fig:pcfsolo}} give the result.", align="justify")
    R.tab([
        ("Scenario", "Development hours", "Implied rate", "Desk time", "PC", "kg CO₂e",
         "vs as-run"),
        ("As run, with the agent", "195 (measured)", "136 lines/h", "955 h", "57.3 kWh",
         "3.22", "—"),
        ("Solo, ×3 assumed", "585", "45 lines/h", "1 345 h", "80.7 kWh", "3.44",
         "+0.22 (1.07×)"),
        ("Solo, ×6.7 (the estimate)", "1 300", "20 lines/h", "2 060 h",
         "123.6 kWh", "5.16", "+1.94 (1.60×)"),
        ("Solo, ×10 assumed", "1 950", "14 lines/h", "2 710 h", "162.6 kWh", "6.72",
         "+3.50 (2.09×)"),
    ], "The counterfactual: the same code written without the agent. Every row keeps the "
       "printer, the rig and the non-development desk time of {{tab:pcf}}; only the "
       "development hours and the AI row change. The implied rate is the 26 468 development "
       "lines of {{tab:ai}} divided by the development hours — what each multiplier actually "
       "asserts about a person's sustained output.",
       col_widths_cm=(3.5, 2.3, 2.0, 1.9, 2.1, 1.6, 2.6), font=8.5, label="pcfsolo")
    R.fig("pcf_solo_bars.png",
          "The project as run against the same code typed by hand at the central ×6.7 "
          "estimate. Whiskers are the honest uncertainty on each side: the AI term's band "
          "above, the ×3–×10 speed-up bracket below.", width_cm=15.0, label="pcfsolo")
    R.p("At the central estimate the answer is about 5.2 kg against 3.2 kg — the AI-assisted "
        "route emitted roughly 1.9 kg less, a factor of 1.6, or 30 km of driving against "
        "48 km. The mechanism is the whole argument: the agent's own compute cost 0.71 kg "
        "and avoided 1 105 h of laptop time, which is 66.3 kWh and 2.7 kg, so every "
        "kilogram of AI compute displaced about 3.7 kg of desk electricity. The break-even "
        "is a speed-up of ×2.5: if a human could have written and tested those 26 468 lines "
        "in under ≈490 h — 54 tested lines an hour, sustained for the project — typing by "
        "hand would have been the cleaner choice.", align="justify")
    R.p("The implied-rate column is the reason the multiplier is stated as a bracket rather "
        "than a number. Only one side of it is measured: 195 h against 26 468 lines is "
        "136 lines an hour with the agent, from the session logs and an AST scan. The other "
        "side is an assumption about a person, and reading it as a rate makes that "
        "assumption checkable — ×6.7 asserts 20 tested lines an hour sustained across "
        "design, debugging, tests and rework; ×10 asserts 14; ×3 asserts 45, which is fast "
        "for tested code with hardware in the loop; and the break-even asserts 54, which is "
        "not credible for a project of this size. The comparison is therefore safe in its "
        "direction and soft in its magnitude. It should also be said that nothing in the "
        "repository measures the engineer's unassisted rate: every commit before the "
        "collaboration began belongs to the upstream project [[cenmir_utm]], so the solo "
        "figure could not have been calibrated from this work even in principle.",
        align="justify")
    R.p("The conclusion is not unconditional, and the corner that breaks it belongs in the "
        "report. If the AI term sits at the top of its band (1.31 kg, a location-based "
        "grid factor at the highest prompt intensity) **and** the solo speed-up were only "
        "×3, then hand-typing comes out lower — by 0.37 kg. The opposite corner, the AI "
        "term at its published market-based value against a ×10 speed-up, favours the "
        "agent by 4.09 kg. So the comparison is clear at the central estimates and "
        "ambiguous at the extremes, which is the same standing as the solo estimate it "
        "inherits. One asymmetry is deliberately excluded and would only widen the gap: "
        "1 112 extra hours at a desk also means more commuting, lighting and heating, none "
        "of which is inside this operational boundary.", align="justify")

    # ------------------------------------------------------------------ 4.13
    R.h2("Answers to the research questions")
    R.p("**RQ1 — Can a two-marker DIC channel on a low-cost industrial camera match a "
        "certified video extensometer, and to what agreement?** Yes. In Analysis 2, on the "
        "same frames, the rig's algorithm and the XT-205 agree in scale to 0.07 %, in "
        "fracture strain to 0.08 %, and in modulus within the fit-window spread, with a "
        "constant offset of 0.07 pixel that vanishes from every slope. In Analysis 1, on "
        "separate specimens on the two machines, yield strength and fracture strain agree "
        "within 1 %; the 6–8 % differences in UTS and modulus are attributable to pull "
        "rate, grip seating and specimen batch, not to the strain channel.", align="justify")
    R.p("**RQ2 — What sets the noise floor, and can it be predicted?** The floor is "
        "centroid noise, ≈12 µε over 10 s and 26 µε over 900 s, below the reference "
        "instrument's 45 µε. It scales as the inverse of the reference pixel span, "
        "predicted 1.78× and measured 1.78×, so it can be designed: more pixels across "
        "the gauge, lower noise. At this floor the uncertainty of a modulus from noise is "
        "under 1 %, and the fit window, not the camera, limits the modulus.", align="justify")
    R.p("**RQ3 — Does the rig reproduce the expected ordering and published property "
        "ranges across polymers of very different character?** Yes. PLA, PETG and TPU land "
        "inside their published bands and in the expected order across two decades of "
        "modulus; a matched pair repeats to 0.2 % in strength; the infill knockdown is the "
        "expected 2.4; fractures do not cluster at the markers; the gauge length changes "
        "the properties by less than the same-gauge scatter; and the share of crosshead "
        "motion that reaches the gauge — 19–29 % — is exactly the quantity a machine "
        "without an extensometer cannot know about itself.", align="justify")
