#!/usr/bin/env python3
"""Check proposed 16-deliverable map consistency, not content truth or official submission."""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "docs" / "deliverables"
REG = json.loads((DIR / "registry.json").read_text(encoding="utf-8"))

def require(ok, msg):
    if not ok:
        raise SystemExit(f"deliverable registry invalid: {msg}")

def main():
    require(REG["id"] == "DELIVERABLE-REGISTRY-20261118", "registry ID")
    require(REG["status"] == "framework_draft_not_content_approval", "must not claim approval")
    require(len(REG["deliverables"]) == 16, "expected 16 official dashboard entries")
    domains = set(REG["accepted_work_domains"])
    require(len(domains) == 13, "expected 13 work information domains")
    sources = REG["source_registry"]
    source_ids = [s["id"] for s in sources]
    require(len(source_ids) == len(set(source_ids)), "source IDs must be unique")
    require(all(s.get("supports") and s.get("does_not_prove") for s in sources),
            "source evidence must include explicit limitations")
    entries = REG["deliverables"]
    ids = [e["id"] for e in entries]
    require(ids == [f"DLV-{n:02}" for n in range(1,17)], "DLV IDs/order")
    rows = [e["dashboard_row"] for e in entries]
    require(rows == list(range(26,42)), "one-to-one dashboard row mapping")
    for e in entries:
        date.fromisoformat(e["due"])
        require(e["kind"] and e["central_question"], f"{e['id']}: purpose missing")
        require(e["work_domains"] and set(e["work_domains"]) <= domains,
                f"{e['id']}: unknown work domain")
        require(e["review_evidence_checks"], f"{e['id']}: evidence checks missing")
        require(all(x in ids and x != e["id"] for x in e["related_deliverables"]),
                f"{e['id']}: invalid related deliverable")
        require(e["official_outline_status"] == "not_yet_verified",
                f"{e['id']}: official outline is not yet verified")
        require(e["template_design_status"] == "proposed_not_a_submitted_artifact",
                f"{e['id']}: proposal confused with submitted document")
        require(e["sample_status"] == (
            "observed_educational_example_not_mandatory" if e["dashboard_row"] <= 37
            else "not_in_observed_12_item_example"), f"{e['id']}: sample scope")
    for path in ["README.md","WORK-MODEL.md","QUALITY-GATES.md",
                 "PROJECTION-CONTRACT.md","SOURCES-AND-DECISIONS.md",
                 "WORKFLOW-EXAMPLES.md","work-record-template.json",
                 "submission-entry-template.json","official-outline-template.json"]:
        require((DIR / path).is_file(), f"missing {path}")
    for path in ["work-record-template.json","submission-entry-template.json",
                 "official-outline-template.json"]:
        template = json.loads((DIR / path).read_text(encoding="utf-8"))
        require(template["status"] == "template_only", f"{path}: not a real record")
    require((ROOT / REG["phase_intent_ref"]).is_file(), "missing Phase Intent")
    print(f"Validated {len(entries)} proposed deliverable mappings, "
          f"{len(domains)} work domains, {len(sources)} evidence sources. "
          "No claim of official outline verification or submission.")
if __name__ == "__main__":
    main()
