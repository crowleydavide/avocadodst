# Avocado DST 2.0 Modular Appendix Library

Version 2026.09.22

This package is ready to place in the existing **Avocado DST** GitHub repository at:

```text
resources/appendices/
```

The Streamlit report program should read `manifest.json`, call `select_appendices()` in
`appendix_router.py`, and merge the returned PDF files into the generated report.

## Recommended access pattern

Keep the PDFs, manifest, gate policy, and router in the same GitHub repository as `app.py`,
`yield_model.joblib`, and `model_metadata.json`. The deployed Streamlit app will receive the
files automatically with each GitHub commit and can read them from a repository-relative path.
No public URL, database, or external storage service is required.

If the repository is public, the appendix PDFs are also public. Use a private repository or a
protected storage service if the content should remain restricted.

## Integration

```python
from pathlib import Path
from resources.appendices.appendix_router import select_appendices

APPENDIX_ROOT = Path(__file__).resolve().parent / "resources" / "appendices"
decisions = select_appendices(report_context, APPENDIX_ROOT / "manifest.json")

for decision in decisions:
    pdf_path = Path(decision["file"])
    # Append pdf_path to the generated report in the returned order.
```

`report_context` must supply `opportunity_threshold_pct`. The library intentionally does not
choose that scientific or business threshold. See `gating_policy.json` and
`example_report_context.json` for the complete input contract.

## Gate sequence

1. **Opportunity gate** - the nutrient opportunity reaches the report program's configured threshold.
2. **Reliability gate** - the response is reportable, sufficiently supported, stable enough, and not extrapolated.
3. **Interpretation gate** - the field data needed to discuss management are present.
4. **Safety gate** - B, Cl, Mn, S, Fe, and Zn remain diagnostic unless a separately reviewed rule permits stronger language.
5. **Interaction gate** - multiple nutrient findings or a named interaction add the interaction appendix.

A selected appendix explains a finding; it does not by itself authorize a fertilizer, amendment,
microbial product, leaching, or irrigation recommendation.

## Contents

- `pdfs/` - 11 element modules and 7 supporting context modules
- `manifest.json` - authoritative module metadata and trigger definitions
- `appendix_index.csv` - human-readable index
- `gating_policy.json` - machine-readable gate contract
- `appendix_router.py` - dependency-free selection logic
- `example_report_context.json` - illustrative input only; its threshold is not a recommendation
- `tests/test_appendix_router.py` - basic routing checks
- `SHA256SUMS.txt` - package integrity list

## Updating content

Keep the appendix ID and filename stable when replacing a PDF. Increase `library_version`, update
the affected metadata, regenerate `SHA256SUMS.txt`, and test the router before deployment.
