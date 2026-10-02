## Pilot Update 9.2.4b

UI-rendering hotfix for the Adviser nutrient-field graphics. Representative and exploratory Plotly charts now receive explicit, role-specific Streamlit keys, preventing an intermittent `StreamlitDuplicateElementId` when both views render the same historical context. No model, nutrient-field classification, threshold, gate, replacement, management, or report logic changed.

## Pilot Update 9.2.4a

Copy-only hotfix: the Guided Grower View now uses the same simple high-nutrient wording as the revised reports: **“This nutrient is high. No corrective application; replacement only if needed.”** No model, threshold, gate, replacement, or management logic changed.

# Avocado DST 2.0 — Phase 2 Pilot

This is a separate English pilot for testing nutrient-opportunity screening and automatic appendix attachment. It is intentionally separate from the existing Spanish production repository.

## Pilot Update 9.2.4

Pilot 9.2.4 is a communication, workflow, and direction-safety update. The frozen
Extra Trees model, 7.5 / 10 / 15 YP thresholds, nutrient-field shadow analysis,
replacement factors, and underlying uptake-gate policy are unchanged.

- Makes **nutrition-associated %YP** the first adviser result, alongside modeled
  kg/tree, gap to the high-yield reference, and the largest individual nutrient
  opportunity.
- Uses the plain directional labels **Low / In range / High** throughout the
  adviser workflow and grower/adviser reports.
- Separates diagnosis into **nutrient supply** versus **uptake conditions**, with
  an explicit prompt to review the most recent soil analysis and available
  nutrient measurements when reported.
- Makes opportunity interpretation direction-aware. Low values point upward,
  high values point downward, and in-range values do not imply a corrective move.
- Adds a high-side safeguard: a large modeled opportunity cannot be presented as
  a reason to apply more of a nutrient when the entered leaf value is High.
  Annual replacement remains possible only when independently justified.
- Simplifies the adviser gate language to **Ready / Review first / Do not
  proceed**, reduces repeated management text, and replaces calibration wording
  with **check response / follow-up plan** in reader-facing material.
- Uses **grove** in reader-facing labels while retaining existing batch-file
  schema fields for backward compatibility.
- Updates the Grower Summary and Adviser Supplement to the same terminology and
  hierarchy.


## Pilot Update 9

Pilot 9 adds a separate **Batch Grove Workspace** without changing the frozen
model, opportunity thresholds, uptake gates, or existing single-sample reports.

- Download a stable CSV template and upload CSV or Excel files containing up to
  500 leaf samples.
- Validate required headings, sample identity, duplicates, numeric values,
  negative values, possible percent/ppm unit errors, missing nutrients, and
  values outside the model's central development range.
- Use the development-set median for prediction when a nutrient is blank while
  leaving that nutrient explicitly unmeasured and unscored.
- Rank samples as Review first, Appendix candidate, Watchlist, or No model
  watchlist using the unchanged 15, 10, and 7.5 YP thresholds.
- Display grove-level metrics, recurring nutrient opportunities, a prioritized
  sample table, and an individual-sample drill-down.
- Download a prioritized batch CSV and a versioned batch audit JSON.

This first batch increment is prioritization only. Shared field context, batch
management plans, and combined batch PDFs are planned for Pilot 9.1. Users
continue in the single-sample workflow when they are ready to enter field
evidence, evaluate uptake conditions, build a management plan, or download the
existing grower and adviser reports.

## Pilot Update 8.4

Pilot 8.4 adds a replacement-reconciliation safeguard for potassium without
changing the frozen model, opportunity thresholds, removal factors, or the
existing element-specific source and uptake-condition rules.

- Harvested-fruit potassium removal remains visible as an accounting value.
- When entered leaf potassium is above the model-favorable scan zone and
  outside the central development range, the removal ledger is not
  automatically converted into an applied potassium planning amount. This
  avoids treating small stepwise curve differences as a high-potassium hold.
- The replacement share begins at zero for that case, and the grower view
  reports that the applied amount is pending balance review.
- Calcium and magnesium leaf patterns are carried into the potassium balance
  explanation when they reinforce the need to review cation balance.
- Adviser Detail View can release the calculation only through an explicit
  override accompanied by a written reason. The override and reason are saved
  in the PDF and JSON audit record.
- A reconciliation hold activates a caution pathway rather than presenting
  crop removal as a supported fertilizer rate.

## Pilot Update 8.3

Pilot 8.3 is a plain-language and visibility update. It does not change the
frozen model, opportunity thresholds, uptake rules, or replacement factors.

- The field-condition switch now states that it checks whether roots, water,
  chemistry, source, timing, safety, and follow-up support nutrient uptake.
- The research switch now states that it reveals experimental findings that are
  not ready for management guidance; this currently applies mainly to sulfur.
- `Carry into maintenance plan` was replaced with `Include in annual
  replacement plan`, and the annual replacement section uses simpler labels.
- Guided Grower View now provides a collapsed table of measured nutrient
  movements below the 7.5-YP review threshold, so a changing nutrient is not
  mistaken for an unresponsive model merely because it has no action card.
- Both PDFs use compact nutrient cards. The download area and reports clearly
  distinguish the fixed two-page grower core from the full Adviser Supplement
  and its automatically selected technical guides.

## Pilot Update 8.2

The Guided Grower View and two-page Grower Action Summary now restore overall
yield-potential context. They show the current modeled yield position relative
to the high-yield reference, the remaining reference gap, the number of
nutrients at the watchlist, and the largest individual nutrient opportunity.
The display explicitly warns that one-at-a-time nutrient opportunities are not
additive and are not promised yield gains.

## Pilot Update 8.1

The Grower Action Summary is now an intentional two-page report. Page 1 provides
a grove and data snapshot, principal findings, and a prioritized action plan.
Page 2 provides simple direction markers for up to three nutrients, replacement
assumptions, information most likely to change the advice, and the follow-up
plan. Optional grove/block and leaf-sample identifiers can be entered without
blocking a leaf-only analysis.

## Pilot Update 8

The pilot now has two interfaces over the same frozen model, thresholds, uptake
gates, and appendix router:

- **Guided Grower View** is the default. It accepts leaf analysis alone, asks
  only the pH, salinity, root, water, timing, source, or follow-up questions
  triggered by the case, and produces short action cards.
- **Adviser Detail View** retains the complete opportunity table, curves,
  structured evidence matrix, gate reasons, appendix routing, audit record, and
  evaluator scorecard.

Opportunity interpretation is now direction-aware. When the entered value is
above the model-favorable zone, the grower wording explicitly states that the
curve is not evidence of deficiency and is not a reason to apply more. The
calibration checklist transfers into the management follow-up plan, and Guided
Grower View does not offer a maintenance application unless crop-removal or
another maintenance basis has been documented.

The download area now provides a concise Grower Action Summary and a separate
Adviser Supplement. The grower summary is designed to remain within one or two
pages; technical curves, gate details, selected appendices, and the complete
audit trail remain in the supplement and JSON.

## Pilot Update 7

The pilot now includes a separate annual harvest-removal and replacement budget
for nitrogen, phosphorus, potassium, and calcium. Expected crop removal is never
derived from, or multiplied by, the model opportunity curve. The budget exposes
the fruit-removal factor, intended replacement share, documented nutrient
credits, and recovery assumption. It does not calculate a provisional applied
elemental amount unless the evaluator deliberately enters a recovery estimate.

The same screen adds a calibration pathway requiring a comparison, application
record, harvest follow-up, and a leaf or root-zone check. Budget assumptions and
calibration status are preserved in the PDF and JSON audit record.

The opportunity-curve work introduced in Update 6 remains unchanged:

The pilot now displays and reports nutrient opportunity curves for measured
nutrients at or above the 7.5 YP-point watchlist threshold. Each curve shows:

- the entered leaf value and a zero reference for the current modeled profile;
- the change in modeled yield potential while one nutrient is scanned and all
  other entered nutrients are held fixed;
- a model-favorable scan zone containing the contiguous values around the scan
  maximum that retain at least 90% of the modeled opportunity; and
- the nutrient's evidence-support and stability classification.

The model-favorable zone is not presented as a tissue sufficiency range,
fertilizer target, treatment response, or rate recommendation. It is an
interpretive model association that must be read with the uptake gates and the
grower's management plan. The PDF includes no more than the three highest
eligible curves to keep the report concise. Research-only curves remain hidden
unless research context is explicitly enabled on screen.

The Update 5 Management Plan and Recommendation Builder remains unchanged. It
keeps nutrient need, uptake conditions, and the grower's proposed plan separate,
then produces constructive guidance:

The pilot now includes a Management Plan and Recommendation Builder after the
uptake-condition gates. It keeps nutrient need, uptake conditions, and the
grower's proposed plan separate, then produces constructive guidance:

- **Ready now** — a measured maintenance or corrective comparison can proceed
  under the documented conditions.
- **Prepare first** — fertilizer remains a conditional option while a marginal
  or missing condition is corrected or confirmed.
- **Improve conditions first** — preserve the nutrient objective, correct the
  closing root-zone, chemistry, source, or safety condition, and then reassess
  fertilizer.

The builder can record grower- or adviser-entered product, rate, timing, and
placement details, but the DST does not calculate or approve a fertilizer rate.
The plan and recommendations are included in the PDF and JSON audit record.

## What the pilot does

- Loads the frozen Phase 1 Extra Trees model.
- Accepts the 12 leaf nutrient inputs used by the model.
- Scans each measured nutrient across the central development range while holding the other inputs fixed.
- Displays auditable nutrient opportunity curves beginning at the 7.5 YP-point watchlist threshold.
- Calculates model opportunity in yield-potential (YP) points.
- Uses the provisional Phase 2 bands: below 7.5, watchlist at 7.5–<10, appendix candidate at 10–<15, and high priority at 15 or more.
- Applies reliability, model-range, field-evidence, safety, and interaction gates.
- Runs a separate uptake-condition shadow layer without changing the frozen model or the opportunity score.
- Keeps three reasons for action separate: maintenance replacement, corrective model opportunity, and independent laboratory or adviser evidence.
- Calculates transparent N, P, K, and Ca harvest removal independently of the model opportunity curve.
- Requires an explicit nutrient-recovery assumption before showing any provisional applied elemental amount.
- Subtracts only grower- or adviser-entered nutrient credits and records every assumption in the audit JSON.
- Reports Open, Caution, Closed, or Not Triggered outcomes and states whether fertilizer is reasonable, conditional, or inappropriate under the documented conditions.
- Treats missing critical information as Caution rather than automatic rejection, and preserves a supported nutrient need when a proposed source is closed.
- Allows an independently supported laboratory or adviser concern to call up a diagnostic-only nutrient appendix even when modeled opportunity is below the threshold.
- Builds a concise Grower Action Summary and a separate Adviser Supplement containing technical detail and selected appendices.
- Provides a JSON audit record for every routing decision.
- Carries structured pH, root, water, salinity, chloride, and bicarbonate evidence into appendix routing so entered information is not labeled missing.
- Prints the specific limiting gate reason and next action in the downloadable PDF and uses YP-point units consistently.
- Records the grower's proposed nutrient and field-management plan and converts gate findings into Ready now, Prepare first, or Improve conditions first recommendations.

## Important interpretation rule

A model opportunity identifies a topic to investigate. It is not proof of deficiency, a promised treatment response, or a fertilizer-rate recommendation. Irrigation, salinity, compaction, drainage, oxygen, root health, organic matter, pH, and nutrient interactions may be the better place to intervene.

The uptake gates are fertilizer-neutral. When need, source compatibility, roots, water, timing, safety, and calibration are documented, an Open result explicitly identifies fertilizer as a reasonable option. Closed applies to the proposed action under the present conditions; it does not erase crop-removal replacement or other supported nutrient need.

## Model audit facts

- Development records: 2,169
- Locked-test records: 1,085
- Locked-test R²: 0.5101
- Locked-test RMSE: 43.88 kg/tree
- Locked-test MAE: 30.37 kg/tree
- Yield reference: 174.882 kg/tree
- Frozen model: 300-tree Extra Trees pipeline

The model file is compressed with `joblib` to remain below GitHub's browser-upload size limit. Compression does not change its predictions.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

On Windows, activate with `.venv\Scripts\activate`.

## Repository layout

```text
app.py                  Streamlit user interface
batch_workspace.py      Pilot 9 multi-sample upload, validation, prioritization, and audit
dst_core.py             model scan, opportunity bands, and routing context
opportunity_curves.py   curve selection, model-favorable zone, and interpretation
grower_guidance.py      guided questions, pathway-safe actions, and plain-language findings
interface_views.py      progressive grower and full adviser screen components
grower_report.py        concise one-to-two-page grower PDF
uptake_gates.py         shadow-mode uptake decisions and element-specific hard stops
uptake_gate_policy.json versioned gate principle, outcomes, and safeguards
report_builder.py       merged pilot report and appendix attachment
pilot_config.json       versioned threshold and reliability settings
model_metadata.json     locked Phase 1 validation and scan ranges
yield_model.joblib      frozen Phase 1 model
resources/appendices/   modular appendix library and router
tests/                  automated pilot checks
test_outputs/           generated representative-case results
PHASE2_CORRECTION_LEDGER.md durable pilot findings and resolution status
```

## Representative-case test

The balanced synthetic suites document fertilizer-positive, conditional,
closed, not-triggered, and constructive management outcomes. Run them from the
repository root:

```bash
python scripts/run_representative_cases.py
python scripts/run_management_recommendation_cases.py
pytest -q
```

The runner writes JSON, CSV, and Markdown results under `test_outputs/`. These are logic tests, not fertilizer-rate recommendations.

## Change control

Do not change the 10-point gate merely to alter one report. Re-run the locked threshold analysis, document the evidence, update the policy version, and review the result before changing the pilot configuration. Do not replace the production repository until the Phase 2 pilot review is complete.
