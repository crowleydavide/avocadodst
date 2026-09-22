import json
import unittest
from pathlib import Path

from appendix_router import select_appendices


ROOT = Path(__file__).resolve().parents[1]


class RouterTests(unittest.TestCase):
    def test_threshold_is_required(self):
        with self.assertRaises(ValueError):
            select_appendices({}, ROOT / "manifest.json")

    def test_k_and_cl_add_interaction(self):
        context = json.loads((ROOT / "example_report_context.json").read_text(encoding="utf-8"))
        ids = [x["appendix_id"] for x in select_appendices(context, ROOT / "manifest.json")]
        self.assertIn("K", ids)
        self.assertIn("CL", ids)
        self.assertIn("CTX-WATER", ids)
        self.assertIn("CTX-INTERACTIONS", ids)

    def test_extrapolated_opportunity_is_not_auto_attached(self):
        context = {
            "opportunity_threshold_pct": 10,
            "nutrients": {"N": {"opportunity_pct": 15, "reportable": True, "support_status": "validated", "stability": "stable", "extrapolation": True}},
        }
        ids = [x["appendix_id"] for x in select_appendices(context, ROOT / "manifest.json")]
        self.assertNotIn("N", ids)


if __name__ == "__main__":
    unittest.main()
