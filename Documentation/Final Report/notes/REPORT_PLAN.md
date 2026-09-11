# Project report — approved plan (2026-09-09)

Reference conventions: EENX30 (Chalmers) report — cover · inner title · supervisor/copyright
page · one-page abstract with keywords · acknowledgments · acronyms · contents · chapters ·
numeric bibliography. W = Weekly deck slide feeding the section (393-slide deck).

## Decisions (his answers, 2026-09-09)
- Format: **Word (.docx) built by script, plus PDF** exported through Word.
- Length: up to ~100 pages — as much as the content sensibly supports.
- AI in the loop: **full section in the body** (3.9), plus disclosure in acknowledgments.
- Appendices: **data tables included** (S25/S26, S27/S28, MOT raw-data tables).
- PCF and humidity: **each gets a whole section** — Analysis 4.11 (humidity) and 4.12 (PCF),
  with primers in Theory 2.7/2.8.
- Affiliation: Department of Product Development, Production and Design, Jönköping
  University. Supervisors: Johan Jansson · Mirza Cenanovic. Cover picture: composed from the
  project's own imagery (report_cover.png). JU logo on the cover (ju_mark.png; higher-res
  official logo welcome).
- Research questions: **RQ1–RQ3 only** (RQ4 on closed-loop control removed); the protocol
  work stays as capability built — Theory 2.6 compact, Analysis 4.9 halved.
- Citations: numeric [n], bibliography harvested from every hyperlink/DOI in both decks and
  checked by hand.

## Front matter
Cover · inner title · supervisor & copyright page · Abstract (one page, keywords) ·
Acknowledgments · Acronyms · Contents · List of figures · List of tables

## Chapters
1 Introduction — 1.1 Background [W1–7, 364] · 1.2 Where DIC is used [W379] · 1.3 Problem and
objectives · 1.4 Research questions RQ1–RQ3 · 1.5 Scope and limitations · 1.6 Method of
work and outline
2 Theory — 2.1 Tensile testing [W186–189, 266–267] · 2.2 Ways to measure strain [W362–365] ·
2.3 DIC and the two-marker form [W245, 321–325] · 2.4 Image formation and segmentation
[W229–243, 386–388] · 2.5 Noise and uncertainty [W294, 326, 335–337] · 2.6 Closed-loop
protocols (compact) [W190–213] · 2.7 Materials and hygroscopic effects [W166, 299, 307,
369–371] · 2.8 Product carbon footprint method [W373–374]
3 Methodology — 3.1 The rig [W27–124, 382] · 3.2 Specimens [W61–62, 215, 360] · 3.3 Software
architecture [W390–393] · 3.4 The DIC pipeline [W241–259] · 3.5 Camera configuration and
auto-calibration [W227–232] · 3.6 Test automation and the 20 smart features [W174–225,
246–250, 361] · 3.7 Validation methodology [W125–170, 312, 327–351] · 3.8 Data handling and
the evidence pipeline [W226, 247, 393] · 3.9 AI in the loop [W380–385]
4 Analysis — 4.1 Bring-up and instrument checks [W17–60, 126–138] · 4.2 PLA to fracture
[W141–170, 282–290] · 4.3 Elastic modulus window [W265–267, 285, 309] · 4.4 Black vs white
and the delivery-rate investigation [W271–278, 387] · 4.5 Three polymers [W295–311, 320] ·
4.6 Marker spacing [W312–319] · 4.7 Cross-validation vs MOT XT-205 [W327–359] · 4.8 Noise
and uncertainty [W321–337] · 4.9 Closed-loop protocol results (halved) [W191–221, 338] ·
4.10 Fracture survey [W366–368] · 4.11 Humidity and the UTS spread [W369–372] · 4.12 Product
carbon footprint [W373–377] · 4.13 Discussion — RQ1–RQ3 answered
5 Conclusion and future work — 5.1 Overview · 5.2 Observations · 5.3 Open items [W389] ·
5.4 Future work [W378] · 5.5 Lessons
6 Bibliography
Appendices — A specimen register · B test campaign register · C smart-feature index ·
D data tables [W268–270, 287–289, 333–334] · E Python workflow · F PCF inventory and
arithmetic · G AI-in-the-loop details

## Build
documentation/report/build_report.py (python-docx) + chapter modules; PDF via Word COM with
TOC/fields updated; figures reused from documentation/figures/ (regenerated from raw runs).
Output: documentation/report/UTM_DIC_Report.docx / .pdf.
