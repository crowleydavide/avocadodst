# Phase 2 pilot correction ledger

This ledger is the durable change record for pilot findings that should not be
left only in conversation notes. It separates decision-engine changes from
reporting, interface, and cosmetic work.

## Pilot Update 9.2.4b - 2026-10-02

UI-rendering hotfix. The frozen model, opportunity thresholds, nutrient-field classifications,
replacement factors, uptake-gate policy, management logic, and report logic were not changed.

| ID | Finding | Resolution | Status |
|---|---|---|---|
| P2-0117 | In Adviser Detail View, a nutrient-field representative chart and the exploratory historical-context chart could occasionally render the same Plotly figure in one Streamlit run. With no explicit chart keys, Streamlit raised `StreamlitDuplicateElementId`. | Added explicit, role-specific Streamlit keys to representative and exploratory nutrient-field charts. The representative and exploratory views now remain distinct even when they use the same historical year. | Implemented; compile and regression checks passed |

## Pilot Update 9.2.4a - 2026-10-01

Copy-only hotfix. The frozen model, opportunity thresholds, nutrient-field results,
replacement factors, uptake-gate policy, and management logic were not changed.

| ID | Finding | Resolution | Status |
|---|---|---|---|
| P2-0116 | Guided Grower View still used the older high-side sentence, “not evidence of deficiency ... not a reason to apply more,” after the reports had adopted the simpler High wording. | Replaced only the displayed high-side sentence with: “This nutrient is high. No corrective application; replacement only if needed.” | Implemented; copy-only regression check |


## Pilot Update 9.2.4 - 2026-10-01

The frozen model, opportunity thresholds, nutrient-field shadow results,
replacement factors, and underlying uptake-gate policy were not changed.

| ID | Finding | Resolution | Status |
|---|---|---|---|
| P2-0110 | %YP was technically present but not prominent enough for growers and advisers who use the model to judge nutrition-associated harvest potential. | Elevated nutrition-associated %YP to the first headline result, with modeled kg/tree, gap to the high-yield reference, and largest individual nutrient opportunity. | Implemented; regression checks added |
| P2-0111 | Adviser Detail View exposed development-oriented terms and a dense model table before the most important interpretation. | Reorganized the adviser screen around %YP, a compact Current/Status/Opportunity/Model-support table, and an advanced-details expander. | Implemented |
| P2-0112 | The workflow emphasized uptake constraints but did not clearly show how an adviser should evaluate nutrient supply. | Added an explicit supply-versus-uptake sequence and a prompt to review soil analysis and available nutrient measurements as supporting evidence. | Implemented |
| P2-0113 | A high-side nutrient such as K could still generate corrective-application language when the one-at-a-time model opportunity pointed toward a lower leaf value. | Added direction status to gate and management context. High results now state: no corrective application; replacement only when independently justified. Corrective application is removed from the action menu for High results in both working views. | Implemented; high-K regression case added |
| P2-0114 | Open/Caution/Closed, calibration, and repeated gate language made the adviser workflow harder to scan. | Reader-facing states are now Ready/Review first/Do not proceed; calibration wording is replaced by check response/follow-up plan; management recommendations are condensed. | Implemented |
| P2-0115 | Grower and adviser reports used mixed orchard/grove terminology and older phrases such as modeled movement. | Standardized reader-facing grove terminology, modeled opportunity, Low/In range/High, annual replacement language, and the revised %YP hierarchy. | Implemented |


## Pilot Update 9 - 2026-09-27

The frozen model, opportunity thresholds, uptake-gate rules, appendix router,
replacement factors, and existing single-sample reports were not changed.

| ID | Finding | Resolution | Status |
|---|---|---|---|
| P2-0100 | Commercial growers and advisers may submit ten or more leaf samples at the same time; repeating the complete single-sample workflow is inefficient and obscures ranch-level priorities. | Added a separate Batch Orchard Workspace with a stable CSV template, CSV/Excel upload, validation, frozen-model processing, a prioritized block table, recurring-opportunity summary, and individual sample drill-down. | Implemented and regression tested |
| P2-0101 | Missing nutrients in a batch could be silently treated as measured values. | Blank values use the frozen development-set median for prediction but remain explicitly unmeasured, receive no opportunity score, and generate a visible data note. | Implemented and regression tested |
| P2-0102 | Batch uploads create new risks from duplicate identifiers, changed headings, nonnumeric values, negative values, and percent/ppm mistakes. | Added blocking schema and unit validation, duplicate-ID checks, non-blocking central-range notices, a 500-sample pilot limit, and a downloadable source-file audit hash. | Implemented and regression tested |
| P2-0103 | A batch summary could be mistaken for a ranch fertilizer prescription. | Pilot 9 is explicitly limited to prioritization. Uptake gates, shared field context, management plans, and reports remain in the single-sample workflow until the Pilot 9.1 design is tested. | Implemented |

## Pilot Update 8.4 - 2026-09-27

The frozen model, opportunity thresholds, nutrient-removal factors, and
existing element-specific uptake and source rules were not changed. A new
replacement-reconciliation state was added ahead of those rules.

| ID | Finding | Resolution | Status |
|---|---|---|---|
| P2-0097 | A grower could select full potassium replacement even when the entered leaf K value was above the central development range and model-favorable zone, and lower K values were associated with the stronger modeled profile. | Added a potassium replacement-reconciliation check. Harvest removal remains visible, but the applied amount is blocked and the replacement share begins at zero while the high-side leaf pattern is under review. Values inside the central range are not blocked merely because of a small stepwise curve difference. | Implemented and regression tested |
| P2-0098 | A mass-balance hold needed to preserve fertilizer as an evidence-based option rather than becoming an absolute prohibition. | Adviser Detail View can release the potassium calculation only after an explicit override and written reason. The override is preserved in reports and the JSON audit record. | Implemented and AppTest checked |
| P2-0099 | A blocked potassium calculation could otherwise disappear from the management workflow. | Added a `replacement_review` caution pathway, positive grower wording, and potassium balance-review notes in both PDF formats. | Implemented; both report formats visually verified |

## Pilot Update 8.3 - 2026-09-27

The frozen model, opportunity thresholds, uptake-gate rules, and replacement
factors were not changed.

| ID | Finding | Resolution | Status |
|---|---|---|---|
| P2-0094 | A nutrient such as potassium could appear unresponsive when its modeled movement changed but remained below the 7.5-YP card and curve threshold. | Added a collapsed grower table containing all measured, non-research nutrient movements below the review threshold; the adviser table continues to show every measured result. | Implemented and regression tested |
| P2-0095 | Terms such as `shadow gates`, `research context`, and `carry into maintenance plan` were not clear to an average grower. | Replaced them with plain-language labels describing field-condition support, experimental findings, and inclusion in the annual replacement plan; simplified the replacement inputs and report headings. | Implemented and AppTest checked |
| P2-0096 | Nutrient cards and attached technical guides were difficult to locate or distinguish between the grower and adviser reports. | Added compact nutrient cards to both report summaries, listed the selected guide titles at download, and labeled the Grower Summary as a fixed two-page core while retaining full selected guides in the Adviser Supplement. | Implemented; report rendering and appendix assembly verified |

## Pilot Update 8.2 - 2026-09-25

The frozen model, opportunity thresholds, uptake-gate rules, and replacement
factors were not changed.

| ID | Finding | Resolution | Status |
|---|---|---|---|
| P2-0092 | The two-page grower report improved action guidance but no longer gave the grower an immediate sense of the overall distance from the high-yield reference. | Added the overall modeled yield position, absolute model estimate, and YP-point gap to the high-yield reference on both the Guided Grower View and page 1 of the Grower Action Summary. | Implemented, regression tested, and visually checked |
| P2-0093 | Multiple nutrient findings needed a concise prioritization signal without implying that their individual opportunities could be combined into a promised gain. | Added the number of nutrients at the watchlist and the largest individual opportunity, with explicit wording that one-at-a-time nutrient opportunities must not be added together. | Implemented, regression tested, and visually checked |

## Pilot Update 8.1 - 2026-09-25

The frozen model, opportunity thresholds, uptake-gate rules, and replacement
factors were not changed.

| ID | Finding | Resolution | Status |
|---|---|---|---|
| P2-0088 | The first concise Grower Action Summary was clear but visually and informationally sparse. | Expanded it into an intentional two-page report: page 1 contains the orchard/data snapshot, findings, and prioritized action plan; page 2 contains direction markers, replacement assumptions, information that could change the advice, and follow-up. | Implemented and visually checked |
| P2-0089 | A grower report needed basic case identification without adding another technical data-entry burden. | Added optional orchard/block name and leaf-sample date fields; leaving them blank does not block analysis. | Implemented and regression tested |
| P2-0090 | Growers needed a visual indication of direction without being asked to interpret the full response curve. | Added simple current-value markers for up to three reviewed nutrients; the green zone is explicitly labeled as an association rather than a sufficiency range or target. | Implemented and visually checked |
| P2-0091 | Missing data needed to be explained by consequence rather than listed as a negative deficiency. | Added a positive `What could change this advice?` section explaining why pH, salinity, feeder roots, or water/aeration would improve the decision. | Implemented and regression tested |

## Pilot Update 8 - 2026-09-25

The frozen model, opportunity thresholds, uptake-gate rules, and replacement
factors were not changed.

| ID | Finding | Resolution | Status |
|---|---|---|---|
| P2-0081 | The complete technical workflow was too formidable for a grower who may have only an annual leaf analysis. | Added a default Guided Grower View with progressive questions and retained the complete Adviser Detail View over the same engine. | Implemented and regression tested |
| P2-0082 | A high entered nutrient value could be mistaken for a deficiency opportunity even when the stronger modeled profile was associated with lower values. | Added direction-aware interpretation: higher association, within-zone, or lower association. Lower-association wording explicitly states that the curve is not evidence of deficiency and is not a reason to apply more. | Implemented and regression tested |
| P2-0083 | Calculated replacement amounts could be hidden to the right in a wide table. | Added prominent per-nutrient cards showing harvest removal, provisional elemental amount, and whole-block element in the Guided Grower View. | Implemented and AppTest checked |
| P2-0084 | The calibration pathway could be assessed as Ready while the management-plan follow-up list remained empty. | Calibration selections now transfer automatically into the management-plan follow-up choices. | Implemented and regression tested |
| P2-0085 | A maintenance application could be selected without a documented crop-removal or maintenance pathway. | Guided choices now omit unsupported maintenance actions; the adviser workflow retains flexibility but emits an explicit pathway warning. | Implemented and regression tested |
| P2-0086 | Growers and advisers need reports at different levels of detail. | Added a concise one-page Grower Action Summary and renamed the full technical report the Adviser Supplement; both remain downloadable with the audit JSON. | Implemented, rendered, and visually checked |
| P2-0087 | Technical gate names and appendix routing crowded the grower workflow. | Guided mode shows only plain-language action cards and a count of technical modules; complete gates, curves, router reasons, and evaluator scorecard remain in Adviser Detail View. | Implemented and AppTest checked |

## Pilot Update 7 - 2026-09-25

The frozen model, opportunity thresholds, and uptake-gate rules were not changed.

| ID | Finding | Resolution | Status |
|---|---|---|---|
| P2-0071 | Annual crop-removal replacement needed to remain distinct from corrective model opportunity. | Added a separate N, P, K, and Ca harvest-removal budget that never uses the model curve to set a rate. | Implemented and regression tested |
| P2-0072 | A calculated rate could hide uncertain fertilizer recovery. | No provisional applied elemental amount is shown unless the evaluator explicitly enters a recovery estimate. | Implemented and regression tested |
| P2-0073 | Nutrient credits and partial replacement choices needed to be visible. | Added editable removal factors, intended replacement share, and documented nutrient credits, all preserved in PDF and JSON. | Implemented and regression tested |
| P2-0074 | Rate calibration needed a defined learning loop. | Added comparison, application-record, harvest, leaf, and root-zone follow-up checks with Ready, Limited, or Unknown status. | Implemented and regression tested |
| P2-0075 | David Crowley and Eddie Grangetto needed a consistent evaluation process. | Added a two-evaluator guide, representative-case list, scorecard, required comments, and wider-pilot go/no-go conditions. | Implemented |

## Pilot Update 4 - 2026-09-24

The frozen model and uptake-gate decision rules were not changed.

| ID | Finding | Resolution | Status |
|---|---|---|---|
| P2-0041 | The PDF showed only the overall fertilizer position and omitted the specific limiting reason and next action. | The uptake summary now prints the non-open gate reasons, missing critical evidence, fertilizer position, and primary next action. | Implemented and regression tested |
| P2-0042 | Structured pH and root evidence was retained in JSON but was not passed into appendix routing, so entered information could be called missing. | `build_available_data()` now merges documented pH, root activity, water/aeration, bicarbonate, salinity, and chloride status into the report evidence record. | Implemented and regression tested |
| P2-0043 | One appendix explanation displayed model opportunity and threshold as percentages rather than YP points. | The report-context contract now uses `opportunity_yp` and `opportunity_threshold_yp`; the router prints YP-point language and retains backward compatibility for earlier audit records. | Implemented and regression tested |

## Pilot Update 5 - 2026-09-24

The frozen model, uptake-gate decision rules, and provisional 10 YP-point
appendix gate were not changed.

| ID | Finding | Resolution | Status |
|---|---|---|---|
| P2-0051 | Gate results were technically useful but did not provide a positive place for the grower to describe an intended fertilizer and field-management plan. | Added a Management Plan Builder that records the grower's goal, nutrient action, optional product/rate/timing details, supporting field actions, follow-up, and notes. | Implemented and regression tested |
| P2-0052 | Open, Caution, and Closed findings could read mainly as restrictions. | Added constructive reader-facing paths: Ready now, Prepare first, and Improve conditions first. Each path states what supports action, where fertilizer fits, conditions for success, and how to verify response. | Implemented and regression tested |
| P2-0053 | Grower-entered application details needed a clear boundary from DST-generated advice. | The interface, report, and audit label product/rate/timing details as grower- or adviser-entered; the DST does not calculate or approve a fertilizer rate. | Implemented and regression tested |
| P2-0054 | The Selected report modules heading could be separated from its table. | The heading and table now move together, while management-plan content uses the previously unused summary-page space. | Implemented and visually checked |

### Pilot Update 5 acceptance - 2026-09-24

- Streamlit confirmed policy `2026.09.24-pilot.5` after a clean reboot.
- A Zinc caution case correctly produced the constructive `Prepare first` path.
- The grower plan, fertilizer role, conditions for success, and follow-up checks
  transferred into the downloaded report.
- The report downloaded without an application error and all seven pages rendered
  without clipping, overlap, or unreadable text.

## Pilot Update 6 - 2026-09-24

The frozen model, uptake-gate decision rules, 7.5 YP-point watchlist, and
provisional 10 YP-point appendix gate were not changed.

| ID | Finding | Resolution | Status |
|---|---|---|---|
| P2-0061 | The management layer needed a representative acceptance matrix beyond individual unit checks. | Added six end-to-end cases balanced across two Ready now, two Prepare first, and two Improve conditions first outcomes. Cases cover Zn, Fe, K maintenance, Ca delivery, Ca with gypsum, and B safety. | Implemented; six of six matched expected outcomes |
| P2-0062 | Reports showed only the opportunity number and best scanned value, making the shape of the locked-model association difficult to evaluate. | Added auditable one-at-a-time opportunity curves on screen and in the PDF for nutrients at or above the watchlist threshold. | Implemented and regression tested |
| P2-0063 | A single best scanned value could be mistaken for a precise agronomic target. | Added a contiguous model-favorable scan zone retaining at least 90% of the modeled opportunity, with explicit language that it is not a sufficiency range, fertilizer target, treatment response, or rate calculation. | Implemented and regression tested |
| P2-0064 | Curve interpretation needed to remain subordinate to field feasibility and fertilizer-neutral management logic. | Curves retain the existing evidence classification and are presented alongside—not in place of—the uptake gate and management recommendation. | Implemented and visually checked |
| P2-0065 | The first deployed Streamlit curve displayed the blue response line and numeric zone but omitted the green zone overlay and orange entered-value marker that appeared in the PDF. | Replaced the simple on-screen line chart with a layered chart containing the green zone, orange entered-value line and point, zero reference, blue curve, and green scan-maximum point. | Implemented as visual hotfix 6.1; model and decision logic unchanged |
| P2-0066 | Exact scan-grid endpoints displayed unnecessary decimal precision and the model-favorable zone could be truncated in the large Streamlit metric. | Added unit-aware reader-facing rounding and widened the zone column. Ppm zones use one decimal; percentage values use two decimals, or three below 0.5%. Full precision remains in the audit JSON. | Implemented as visual hotfix 6.2; calculations unchanged |

## Deferred refinements

| ID | Item | Priority | Planned treatment |
|---|---|---|---|
| P2-D001 | The summary report can leave unused space on its final summary page. | Low | Resolved in Update 5 by using the space for management-plan content and keeping headings with their tables. |
| P2-D002 | Grower-facing recommendations should lead with supported actions and conditions for success rather than negative bullet lists. | Design priority | Resolved in Update 5 with the separate Management Plan and Recommendation Builder. |
| P2-D003 | In the downloaded Update 5 report, the `Important limits` heading is orphaned at the bottom of summary page 2 while its paragraph moves to page 3, leaving excess blank space. | Low | Resolved in Update 6 by keeping the heading with its first paragraph. |

## Change-control rule

- Do not change the frozen prediction model through this ledger.
- Do not change the provisional 10 YP-point appendix gate without the planned threshold review.
- Record every newly discovered issue with a stable ID, scope, decision, and validation result.
- Keep reporting and interface corrections separate from nutrient gate-policy changes.
