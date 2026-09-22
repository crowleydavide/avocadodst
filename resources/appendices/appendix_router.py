from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class AttachmentDecision:
    appendix_id: str
    title: str
    file: str
    action_level: str
    reasons: list[str]
    missing_data: list[str]


def _load_manifest(manifest_path: Path | None = None) -> tuple[Path, dict[str, Any]]:
    root = Path(__file__).resolve().parent
    path = manifest_path or root / "manifest.json"
    return path.parent, json.loads(path.read_text(encoding="utf-8"))


def select_appendices(report_context: dict[str, Any], manifest_path: Path | None = None) -> list[dict[str, Any]]:
    """Return ordered appendix decisions for one generated DST report.

    This router selects explanatory attachments. It does not create a fertilizer,
    amendment, or irrigation recommendation.
    """
    base, manifest = _load_manifest(manifest_path)
    threshold = report_context.get("opportunity_threshold_pct")
    if threshold is None:
        raise ValueError("opportunity_threshold_pct must be supplied by the report program")

    nutrients = report_context.get("nutrients", {})
    available = set(report_context.get("available_data", []))
    field_flags = set(report_context.get("field_flags", []))
    interaction_flags = set(report_context.get("interaction_flags", []))
    all_flags = field_flags | interaction_flags
    include_research = bool(report_context.get("include_research_context", False))
    entries = {item["id"]: item for item in manifest["appendices"]}
    selected: dict[str, AttachmentDecision] = {}

    def add(item: dict[str, Any], level: str, reason: str, missing: list[str] | None = None) -> None:
        decision = selected.get(item["id"])
        if decision:
            if reason not in decision.reasons:
                decision.reasons.append(reason)
            decision.missing_data = sorted(set(decision.missing_data) | set(missing or []))
            return
        selected[item["id"]] = AttachmentDecision(
            appendix_id=item["id"], title=item["title"], file=str(base / item["file"]),
            action_level=level, reasons=[reason], missing_data=sorted(missing or []),
        )

    # Nutrient opportunity and direct diagnostic flags.
    for item in manifest["appendices"]:
        if item["kind"] != "nutrient":
            continue
        state = nutrients.get(item["id"], {})
        item_flags = set(item.get("diagnostic_flags", []))
        direct_flag = bool(state.get("flagged")) or bool(item_flags & all_flags)
        opportunity = state.get("opportunity_pct")
        opportunity_pass = (
            item["trigger_mode"] == "opportunity_or_flag"
            and opportunity is not None
            and float(opportunity) >= float(threshold)
            and bool(state.get("reportable", False))
        )
        if not (direct_flag or opportunity_pass):
            continue

        support = state.get("support_status", "unavailable")
        stability = state.get("stability", "unknown")
        extrapolation = bool(state.get("extrapolation", False))
        reliability_pass = support in {"validated", "operational"} and stability in {"stable", "mixed"} and not extrapolation
        research_only = support == "research_only" or stability == "unstable" or extrapolation
        if opportunity_pass and research_only and not direct_flag and not include_research:
            continue

        missing = [key for key in item.get("required_data_for_management", []) if key not in available]
        level = item["max_action_level"]
        reasons: list[str] = []
        if opportunity_pass:
            reasons.append(f"modeled opportunity {opportunity:g}% met the {float(threshold):g}% attachment threshold")
        if direct_flag:
            reasons.append("diagnostic or interaction flag matched")

        if research_only:
            level = "research_context"
            reasons.append("reliability gate limited this finding to research context")
        elif not reliability_pass or support == "provisional" or stability in {"mixed", "unknown"}:
            level = "diagnostic_only"
            reasons.append("reliability gate requires diagnostic wording")
        elif missing:
            level = "diagnostic_only"
            reasons.append("interpretation gate is missing field evidence")
        elif item["max_action_level"] != "management_context":
            level = "diagnostic_only"
            reasons.append("appendix safety policy caps automated wording at diagnostic only")

        add(item, level, "; ".join(reasons), missing)

    # Explicit field-context modules.
    for item in manifest["appendices"]:
        if item["kind"] == "context" and set(item.get("diagnostic_flags", [])) & all_flags:
            add(item, "diagnostic_context", "field or interaction flag matched")

    nutrient_ids = [key for key in selected if entries[key]["kind"] == "nutrient"]
    if len(nutrient_ids) >= 2 or interaction_flags:
        add(entries["CTX-INTERACTIONS"], "diagnostic_context", "multiple nutrients or an interaction flag was selected")
    if len(nutrient_ids) >= 3 or "conflicting_symptoms" in field_flags:
        add(entries["CTX-MATRIX"], "diagnostic_context", "multiple findings require a cross-check matrix")

    # Default companions and missing-data support.
    for nutrient_id in list(nutrient_ids):
        item = entries[nutrient_id]
        for companion_id in item.get("default_companions", []):
            add(entries[companion_id], "diagnostic_context", f"default companion for {item['title']}")
    if any(d.action_level in {"diagnostic_only", "research_context"} or d.missing_data for d in selected.values()):
        add(entries["CTX-FIELD-DATA"], "diagnostic_context", "diagnostic or provisional findings need additional field evidence")

    ordered = []
    for item in manifest["appendices"]:
        decision = selected.get(item["id"])
        if decision:
            ordered.append(asdict(decision))
    return ordered
