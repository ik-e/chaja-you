#!/usr/bin/env python3
"""Check the V4 lightweight slice example and re-use V3 structural/contract checks.

This is a design-artifact validator, not a test of any candidate product implementation.
Usage: python tools/check_ai_design_playbook.py
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from validate_planning_design_model import validate, validate_component

ROOT = Path("docs/deliverables")
PILOT = ROOT / "pilots/2026-11-19-planning-design-v2"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_slice(slice_data: dict, pilot: dict, comp: dict, domain: dict) -> list[str]:
    errors = []
    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    recs = {r["id"]: r for r in pilot.get("records", [])}
    components = {c["id"]: c for c in comp["example"]["components"]}
    units = {c["id"]: c for c in comp["example"]["containers"]}
    contracts = {c["id"]: c for c in comp["example"]["example_contracts"]}
    authority = slice_data["authority"]
    execution = slice_data["execution_plan"]
    results = slice_data["results"]
    require(authority["approval_state"] == "not_approved_for_product_implementation", "Unapproved product prematurely promoted")
    require(slice_data["status"] == "illustrative_only_not_approved", "Slice status must remain illustrative")
    require(execution["run_status"] == "not_run", "Synthetic test execution cannot be marked completed")
    require(results["execution_status"] == "not_run", "No actual execution record exists")
    require(results["measured_quality"] is None and execution["measured_time_minutes"] is None,
            "Pilot must not invent measurements")
    require(authority["candidate_ref"] == pilot["candidate_ref"], "Slice candidate source differs from pilot")
    for name in ("intent_ref", "phase_intent_ref", "candidate_ref", "approval_state"):
        require(bool(authority.get(name)), f"Missing authority field: {name}")
    for name in ("actor", "trigger", "desired_result", "requirement_ref", "quality_requirement_ref"):
        require(bool(slice_data["one_flow"].get(name)), f"Missing goal/flow field: {name}")
    for name in ("in_scope", "out_of_scope", "constraints"):
        require(bool(slice_data["boundaries"].get(name)), f"Missing scope field: {name}")
    for name in ("verification_refs", "examples"):
        require(bool(slice_data["acceptance"].get(name)), f"Missing acceptance field: {name}")
    for name in ("ai_may", "requires_human", "recheck_when"):
        require(bool(slice_data["decision_boundary"].get(name)), f"Missing authority boundary: {name}")

    for k in ("requirement_ref", "quality_requirement_ref"):
        ref = slice_data["one_flow"][k]
        require(ref in recs, f"Unknown slice requirement: {ref}")
    for ref in slice_data["acceptance"]["verification_refs"]:
        require(recs.get(ref, {}).get("type_id") == "IT-20", f"Unknown slice test: {ref}")
    for ref in slice_data["design_impact"]["runtime_units"]:
        require(ref in recs and recs[ref].get("type_id") == "IT-27", f"Unknown runtime info record: {ref}")
        require(ref.startswith("RU-") and ref[3:] in units, f"Unknown runtime component: {ref}")
    for ref in slice_data["design_impact"]["components"]:
        require(ref in recs and recs[ref].get("type_id") == "IT-13", f"Unknown component info record: {ref}")
        require(ref.startswith("CR-") and ref[3:] in components, f"Unknown executable component: {ref}")
    for ref in slice_data["design_impact"]["interfaces"]:
        require(ref in contracts, f"Unknown contract: {ref}")

    require(slice_data["design_impact"]["canonical_contract_ref"] == comp["canonical_domain_contract_ref"],
            "Slice shared contract ref mismatch")
    require(slice_data["design_impact"]["depth"] in {"S", "M", "H"}, "Invalid design depth")
    require(domain["enums"]["ObservationKind"] == ["observed","inferred","unknown"], "Unexpected sample observation enum")
    for example in slice_data["acceptance"]["examples"]:
        require(bool(example.get("input")) and bool(example.get("expected")), "Incomplete acceptance example")

    return errors


def main() -> int:
    model = load(ROOT / "planning-design-info-model.json")
    pilot = load(PILOT / "CAND-016-TRACE.json")
    comp = load(ROOT / "component-design-model.json")
    domain = load(PILOT / "DOMAIN-CONTRACT.json")
    example = load(PILOT / "AI-SLICE-EXAMPLE.json")
    prior_errors, prior_stats = validate(model, pilot)
    component_errors, component_stats = validate_component(model, pilot, comp, domain)
    errors = prior_errors + component_errors + check_slice(example, pilot, comp, domain)

    injected = [
        ("invented_execution", lambda x: x["execution_plan"].update(run_status="pass")),
        ("lost_requirement", lambda x: x["one_flow"].update(requirement_ref="EX-NONEXISTENT")),
        ("lost_component", lambda x: x["design_impact"].update(components=["CR-NONEXISTENT"])),
        ("unapproved_promotion", lambda x: x.update(status="adopted")),
        ("unknown_contract", lambda x: x["design_impact"].update(canonical_contract_ref="missing.json")),
    ]
    caught = []
    for name, mutate in injected:
        variant = copy.deepcopy(example)
        mutate(variant)
        caught.append({"case": name, "caught": bool(check_slice(variant, pilot, comp, domain))})
    if not all(x["caught"] for x in caught):
        errors.append("Regression mutation unexpectedly passed")
    result = {
        "status": "pass" if not errors else "fail",
        "type": "design_contract_structure_only",
        "legacy_model": prior_stats,
        "component": component_stats,
        "slice": {"id": example["id"], "mode": example["design_impact"]["depth"],
                  "execution": example["execution_plan"]["run_status"]},
        "regression_checks": caught,
        "errors": errors,
        "not_claimed": ["candidate adoption", "implemented product", "user validation", "measured productivity"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
