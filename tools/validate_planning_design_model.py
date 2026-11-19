#!/usr/bin/env python3
"""Dependency/type/traceability validation for the R01 planning-design V2 proposal.
No network access; never accepts sample evidence as real-world product proof.
Usage: python tools/validate_planning_design_model.py [model_json] [pilot_json]
"""
from __future__ import annotations
import json
import sys
from collections import deque
from pathlib import Path

MODEL = "docs/deliverables/planning-design-info-model.json"
PILOT = "docs/deliverables/pilots/2026-11-19-planning-design-v2/CAND-016-TRACE.json"
ALLOWED_STATUS = {"draft_hypothesis", "proposed", "provisional", "adopted", "deferred", "rejected", "not_applicable"}
SCHEMA_TYPES = {"string", "string[]", "object", "ref", "ref[]", "enum"}

def check(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)

def check_type(value, type_name: str) -> bool:
    if value is None:
        return True  # Missing/unknown explicitly allowed for proposals
    if type_name in {"string", "ref", "enum"}:
        return isinstance(value, str)
    if type_name in {"string[]", "ref[]"}:
        return isinstance(value, list) and all(isinstance(x, str) for x in value)
    if type_name == "object":
        return isinstance(value, dict)
    return False

def validate(model: dict, pilot: dict) -> tuple[list[str], dict]:
    errors: list[str] = []
    stages = model.get("decision_stages", [])
    types = model.get("information_types", [])
    stage_ids = [s["id"] for s in stages]
    type_ids = [t["id"] for t in types]
    stage_map = {s["id"]: s for s in stages}
    type_map = {t["id"]: t for t in types}
    check(len(set(stage_ids)) == len(stage_ids), "Duplicate decision stage IDs", errors)
    check(len(set(type_ids)) == len(type_ids), "Duplicate information type IDs", errors)

    domains = set(model.get("compatibility", {}).get("accepted_work_domains", [
        "problem", "requirements", "task", "interface", "data", "workflow",
        "architecture", "risk", "test", "run", "deployment", "decision", "submission"
    ]))
    for s in stages:
        for d in s.get("blocking_on", []):
            check(d in stage_map, f"{s['id']}: missing prerequisite stage {d}", errors)
        for output in s.get("output_types", []):
            check(output in type_map, f"{s['id']}: missing output type {output}", errors)

    indegree = {id: 0 for id in stage_map}
    consumers = {id: [] for id in stage_map}
    for s in stages:
        for prior in s.get("blocking_on", []):
            if prior in stage_map:
                indegree[s["id"]] += 1
                consumers[prior].append(s["id"])
    queue = deque(k for k, v in indegree.items() if v == 0)
    count = 0
    while queue:
        curr = queue.popleft()
        count += 1
        for nxt in consumers[curr]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    check(count == len(stages), "Decision graph contains a cycle", errors)

    permitted_relations = {r["id"] for r in model.get("relationship_types", [])}
    allowed_edges = set()
    for edge in model.get("type_edges", []):
        a, b, relation = edge["from_type"], edge["to_type"], edge["relation"]
        check(a in type_map and b in type_map, f"Unknown type edge endpoint: {edge['id']}", errors)
        check(relation in permitted_relations, f"Unknown relation type: {relation}", errors)
        check((a,b,relation) not in allowed_edges, f"Duplicate typed edge: {a},{b},{relation}", errors)
        allowed_edges.add((a,b,relation))

    for t in types:
        check(t.get("first_defined_at") in stage_map, f"{t['id']}: missing first stage", errors)
        check(t.get("work_domain") in domains, f"{t['id']}: unknown work domain", errors)
        field_keys = [f["key"] for f in t.get("fields", [])]
        check(len(set(field_keys)) == len(field_keys), f"{t['id']}: duplicate field keys", errors)
        for f in t.get("fields", []):
            check(f.get("value_type") in SCHEMA_TYPES, f"{t['id']}.{f['key']}: field type invalid", errors)
            check(isinstance(f.get("required_for_baseline"), bool), f"{t['id']}.{f['key']}: baseline flag absent", errors)

    records = pilot.get("records", [])
    instance_ids = [r["id"] for r in records]
    record_map = {r["id"]: r for r in records}
    check(len(set(instance_ids)) == len(instance_ids), "Pilot duplicate record IDs", errors)
    check(pilot.get("no_product_adoption") is True, "Pilot adoption flag is missing", errors)
    check(pilot.get("no_real_world_test_run") is True, "Pilot run disclaimer is missing", errors)
    for rec in records:
        typ = type_map.get(rec.get("type_id"))
        if typ is None:
            errors.append(f"{rec['id']}: unknown information type")
            continue
        check(rec.get("status") in ALLOWED_STATUS, f"{rec['id']}: invalid status", errors)
        if pilot.get("no_product_adoption"):
            check(rec.get("status") != "adopted", f"{rec['id']}: candidate silently adopted", errors)
        fields = rec.get("fields", {})
        check(isinstance(fields, dict), f"{rec['id']}: fields must be object", errors)
        if not isinstance(fields, dict):
            continue
        spec = {f["key"]: f for f in typ["fields"]}
        for key, value in fields.items():
            f = spec.get(key)
            check(f is not None, f"{rec['id']}.{key}: unknown field", errors)
            if f:
                check(check_type(value, f["value_type"]), f"{rec['id']}.{key}: incorrect field type, want {f['value_type']}", errors)
                if f.get("allowed_values") and value is not None:
                    check(value in f["allowed_values"], f"{rec['id']}.{key}: enum value invalid", errors)
        if rec["status"] in {"adopted", "provisional"}:
            for f in typ["fields"]:
                if f["required_for_baseline"]:
                    check(f["key"] in fields and fields[f["key"]] not in (None, "", [], {}),
                        f"{rec['id']}.{f['key']}: baseline mandatory field missing", errors)
        check(isinstance(rec.get("source_refs"), list), f"{rec['id']}: source_refs missing", errors)

    edge_ids = []
    forward = {}
    for edge in pilot.get("edges", []):
        edge_ids.append(edge["id"])
        a, b, rel = edge["from"], edge["to"], edge["relation"]
        check(a in record_map and b in record_map, f"{edge['id']}: unknown instance endpoint", errors)
        check(rel in permitted_relations, f"{edge['id']}: unknown relation", errors)
        if a in record_map and b in record_map and rel != "impacts":
            key = (record_map[a]["type_id"], record_map[b]["type_id"], rel)
            check(key in allowed_edges, f"{edge['id']}: not allowed by type relation graph {key}", errors)
        forward.setdefault(a, []).append((b, rel))
    check(len(edge_ids) == len(set(edge_ids)), "Pilot duplicate edge IDs", errors)

    # Every example FR/NFR needs an explicit verification relationship, even before a run.
    verified_sources = {e["from"] for e in pilot.get("edges", []) if e["relation"] == "verified_by"}
    for rec in records:
        if rec.get("type_id") in {"IT-09", "IT-10"} and rec.get("status") != "not_applicable":
            check(rec["id"] in verified_sources, f"Requirement lacks verification link: {rec['id']}", errors)

    projection_ids = {d["id"] for d in model.get("projection_examples", [])}
    projection_edges = pilot.get("projection_edges", [])
    check(len({e["id"] for e in projection_edges}) == len(projection_edges),
          "Duplicate projection edge IDs", errors)
    for e in projection_edges:
        check(e.get("relation") == "materialized_in", f"Wrong projection relation: {e['id']}", errors)
        check(e.get("from") in record_map, f"Unknown projection source: {e['id']}", errors)
        check(e.get("to") in projection_ids, f"Unknown projection target: {e['id']}", errors)
        check(e.get("status") == "preview_only", f"Pilot must not claim submitted DLV: {e['id']}", errors)

    assertions = pilot.get("assertions", {})
    trace = assertions.get("minimum_trace", [])
    for id in trace:
        check(id in record_map, f"Trace includes non-existing record {id}", errors)
    # Each adjacent pair in the declared trace must have some path, not necessarily a direct edge.
    def reaches(start: str, target: str) -> bool:
        todo = deque([start])
        visited = set()
        while todo:
            at = todo.popleft()
            if at == target:
                return True
            if at in visited:
                continue
            visited.add(at)
            todo.extend(to for to, kind in forward.get(at, []) if kind != "impacts")
        return False
    for a,b in zip(trace,trace[1:]):
        check(reaches(a,b), f"No causal trace path {a} -> {b}", errors)

    change = assertions.get("change_case", {})
    changed = change.get("changed_record")
    if changed:
        check(changed in record_map, f"Change case references unknown record {changed}", errors)
        direct_impact = {to for to, rel in forward.get(changed, []) if rel == "impacts"}
        for expected in change.get("expected_impact", []):
            check(expected in direct_impact, f"Expected impact {changed} -> {expected} not linked", errors)
        check(change.get("action") == "review_candidates_only_not_automatic_invalidation",
              "Change impact must be review-only", errors)
    check(assertions.get("run_status") == "not_run", "Pilot must not invent test executions", errors)
    check("EX-CHOICE" in record_map and record_map["EX-CHOICE"].get("status") == "deferred",
          "Non-adopted product choice must remain deferred", errors)
    stats = {"stages":len(stages),"information_types":len(types),
             "typed_fields":sum(len(t["fields"]) for t in types),
             "typed_edges":len(model.get("type_edges",[])),
             "pilot_records":len(records),"pilot_edges":len(edge_ids),"projection_preview_edges":len(projection_edges),"trace_nodes":len(trace),
             "change_impact_targets":len(change.get("expected_impact",[]))}
    return errors, stats

def main() -> int:
    model_path = Path(sys.argv[1]) if len(sys.argv)>1 else Path(MODEL)
    pilot_path = Path(sys.argv[2]) if len(sys.argv)>2 else Path(PILOT)
    try:
        model = json.loads(model_path.read_text(encoding="utf-8"))
        pilot = json.loads(pilot_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print(json.dumps({"status":"error", "reason":str(error)},ensure_ascii=False))
        return 2
    errors, stats = validate(model,pilot)
    print(json.dumps({"status":"pass" if not errors else "fail","stats":stats,"errors":errors},ensure_ascii=False,indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
