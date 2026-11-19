#!/usr/bin/env python3
"""Dependency/type/traceability validation for the R01 planning-design design-only V4 proposal.
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
COMPONENT = "docs/deliverables/component-design-model.json"
DOMAIN = "docs/deliverables/pilots/2026-11-19-planning-design-v2/DOMAIN-CONTRACT.json"
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


    # Strict causal prerequisites must be acyclic. Impact/review links are explicitly reversible.
    causal_relations = {"derived_from", "constrains", "satisfies"}
    causal_next = {t: [] for t in type_ids}
    for edge in model.get("type_edges", []):
        if edge["relation"] in causal_relations and edge["from_type"] in causal_next:
            causal_next[edge["from_type"]].append(edge["to_type"])
    active, complete = set(), set()
    def visit_type(t: str, chain: list[str]) -> None:
        if t in active:
            errors.append("Information prerequisite cycle: " + " -> ".join(chain+[t]))
            return
        if t in complete:
            return
        active.add(t)
        for to in causal_next.get(t, []):
            visit_type(to, chain+[t])
        active.remove(t)
        complete.add(t)
    for t in type_ids:
        visit_type(t, [])
    # Only strict prerequisites need chronological ordering. Conditional
    # baseline_reconcile relations can cross parallel detail-design stages.
    def predecessors(stage_id: str) -> set[str]:
        seen = set()
        todo = list(stage_map.get(stage_id,{}).get("blocking_on",[]))
        while todo:
            at = todo.pop()
            if at not in seen:
                seen.add(at)
                todo.extend(stage_map.get(at,{}).get("blocking_on", []))
        return seen
    for edge in model.get("type_edges", []):
        if edge["relation"] not in causal_relations or edge.get("contract_phase") == "baseline_reconcile":
            continue
        prior = type_map.get(edge["from_type"])
        later = type_map.get(edge["to_type"])
        if prior and later:
            from_stage, to_stage = prior["first_defined_at"], later["first_defined_at"]
            check(from_stage == to_stage or from_stage in predecessors(to_stage),
                  f"{edge['id']}: prerequisite {from_stage} not established before {to_stage}", errors)

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
        if rec["status"] == "adopted" and rec["type_id"] in {"IT-06", "IT-19", "IT-25"}:
            check(bool(fields.get("authority_ref")), f"{rec['id']}: adoption without human authority", errors)
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

    # Requirements must have planned checks; only observed executions justify verified_by.
    verified_sources = {e["from"] for e in pilot.get("edges", []) if e["relation"] in {"planned_check_by", "verified_by"}}
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

    # Design-stage verification/test planning is first-class, not a final gate.
    for stage in stages:
        plan = stage.get("verification_design", {})
        check(bool(plan.get("question")), f"{stage['id']}: missing verification question", errors)
        check(bool(plan.get("planned_methods")), f"{stage['id']}: missing planned method", errors)
        check(plan.get("test_plan_type_ref") == "IT-20", f"{stage['id']}: wrong test-plan type", errors)
        check(plan.get("execution_result") == "not_run",
              f"{stage['id']}: design plan falsely asserts execution", errors)
    for level in model.get("progressive_design_layers", []):
        plan = level.get("verification_design", {})
        check(bool(plan.get("objective") and plan.get("what_to_define")),
              f"{level['id']}: missing level verification/test design", errors)
        check(plan.get("design_record_type") == "IT-20",
              f"{level['id']}: missing IT-20 planning reference", errors)
        check(plan.get("execution_result") == "not_run",
              f"{level['id']}: verification design confused with execution", errors)
    check(model.get("design_scope", {}).get("primary", "").startswith("제품 기획"),
          "Model scope is not focused on product planning and system design", errors)
    check(bool(model.get("verification_concepts", {}).get("test_design"))
          and bool(model.get("verification_concepts", {}).get("test_execution")),
          "Missing test design vs execution distinction", errors)

    allowed_kinds = set(next((x.get("allowed_values", []) for x in type_map.get("IT-20", {}).get("fields", [])
                              if x["key"]=="verification_kind"), []))
    for s in stages:
        plan = s.get("verification_design", {})
        check(plan.get("kind") in allowed_kinds,
              f"{s['id']}: unrecognized verification_kind", errors)
        check(plan.get("plan_maturity") in {"question","validation_method","acceptance_criteria","detailed_test_case"},
              f"{s['id']}: invalid plan maturity", errors)
    for rec in records:
        if rec.get("type_id") != "IT-20":
            continue
        fields = rec.get("fields", {})
        if "verification_kind" in fields:
            check(fields["verification_kind"] in allowed_kinds,
                  f"{rec['id']}: invalid verification kind", errors)
        check(fields.get("run_ref") is None, f"{rec['id']}: simulated check falsely points to an execution", errors)
        maturity = fields.get("plan_maturity")
        if maturity == "detailed_test_case":
            check(bool(fields.get("case_conditions") and fields.get("expected") and fields.get("verdict_boundary")),
                  f"{rec['id']}: incomplete detailed test plan", errors)
            boundary = fields.get("verdict_boundary","")
            check("pass:" in boundary and "fail:" in boundary and "unknown:" in boundary,
                  f"{rec['id']}: pass/fail/unknown criteria must be explicit", errors)
            check("not_run" not in boundary,
                  f"{rec['id']}: verdict boundary confused with execution status", errors)
        if maturity:
            check(fields.get("design_level") in {f"L{i}" for i in range(7)},
                  f"{rec['id']}: invalid design level", errors)
    check(model.get("refinement_policy", {}).get("decision_graph") is not None,
          "Missing elastic refinement policy", errors)

    type20 = type_map.get("IT-20", {})
    required_test_fields = {"subject_refs","case_conditions","expected","method",
                            "verdict_boundary","verification_kind","design_level"}
    actual_fields = {f["key"] for f in type20.get("fields", [])}
    check(required_test_fields <= actual_fields, "Missing verification/test planning fields", errors)

    for typ in types:
        first = stage_map.get(typ.get("first_defined_at"))
        check(bool(first) and typ["id"] in first.get("output_types", []),
              f"{typ['id']}: first production stage missing", errors)
    for layer in model.get("progressive_design_layers", []):
        for sid in layer.get("stage_ids", []):
            check(sid in stage_map, f"{layer['id']}: unknown stage {sid}", errors)
        for prop in ("decide_now","defer_now","minimum_input","completion_for_next"):
            check(bool(layer.get(prop)), f"{layer['id']}: missing {prop}", errors)

    stats = {"stages":len(stages),"information_types":len(types),
             "typed_fields":sum(len(t["fields"]) for t in types),
             "typed_edges":len(model.get("type_edges",[])),
             "pilot_records":len(records),"pilot_edges":len(edge_ids),"projection_preview_edges":len(projection_edges),"trace_nodes":len(trace),
             "change_impact_targets":len(change.get("expected_impact",[]))}
    return errors, stats


def validate_component(model, pilot, component, domain):
    errors = []
    recs = {r["id"]: r for r in pilot.get("records", [])}
    ex = component.get("example", {})
    comps = ex.get("components", [])
    runtime = {c["id"] for c in ex.get("containers", [])}
    kind_ids = {c["key"] for c in component.get("categories", [])}
    comp_ids = {c["id"] for c in comps}
    known = comp_ids | runtime | {a["id"] for a in ex.get("system",{}).get("actors",[])} | {a["id"] for a in ex.get("system",{}).get("external",[])}
    check(len(comp_ids)==len(comps), "Duplicate component IDs", errors)
    for c in comps:
        cid = c["id"]
        check(c.get("kind") in kind_ids, f"{cid}: undefined component kind", errors)
        check(c.get("parent_container") in runtime, f"{cid}: missing runtime unit", errors)
        check(c.get("phase") == "draft_hypothesis", f"{cid}: proposed component prematurely adopted", errors)
        src = recs.get(c.get("source_info_ref"))
        check(src is not None and src.get("type_id") == "IT-13", f"{cid}: no independent IT-13 record", errors)
        if src:
            check(src["fields"].get("component") == cid, f"{cid}: mismatched ID", errors)
            check(src["fields"].get("parent_runtime_unit_ref") == "RU-"+c["parent_container"], f"{cid}: mismatched runtime", errors)
            check(src["fields"].get("verification_refs") == c.get("verification_refs"), f"{cid}: mismatched tests", errors)
        for dep in c.get("depends_on", []):
            check(dep in known, f"{cid}: missing dependency {dep}", errors)
        check(len(c.get("requirement_contributions", [])) == len(c.get("requirements", [])),
              f"{cid}: unclear requirement responsibility", errors)
        for contrib in c.get("requirement_contributions", []):
            check(contrib.get("requirement_ref") in c.get("requirements", []) and bool(contrib.get("contribution")),
                  f"{cid}: invalid requirement contribution", errors)
        for req in c.get("requirements", []):
            check(req in recs and recs[req].get("type_id") in {"IT-09", "IT-10"},
                  f"{cid}: unknown requirement {req}", errors)
        for req in c.get("requirements", []):
            matching = [k for k in c.get("requirement_contributions", []) if k.get("requirement_ref")==req]
            check(len(matching) == 1, f"{cid}: required contribution must be unique", errors)
        for test_id in c.get("verification_refs", []):
            test = recs.get(test_id, {})
            subjects = set(test.get("fields", {}).get("subject_refs", []))
            check(bool(subjects.intersection(c.get("requirements", []))),
                  f"{cid}: planned test {test_id} does not cover any of its requirements", errors)
        for test in c.get("verification_refs", []):
            check(test in recs and recs[test].get("type_id") == "IT-20",
                  f"{cid}: unknown verification {test}", errors)
    for conn in ex.get("connections", []):
        check(conn.get("from") in known and conn.get("to") in known,
              f"{conn.get('id')}: invalid component connection", errors)
    for unit in runtime:
        check(recs.get("RU-"+unit,{}).get("type_id") == "IT-27",
              f"{unit}: missing distinct logical runtime record", errors)
    enums = domain.get("enums", {})
    states = enums.get("CaseStatus", [])
    kinds = enums.get("ObservationKind", [])
    error_codes = enums.get("ErrorCode", [])
    wf = recs.get("EX-WF",{}).get("fields",{})
    api = recs.get("EX-API",{}).get("fields",{})
    ui = recs.get("EX-UI",{}).get("fields",{})
    check(wf.get("states") == states, "CaseStatus differs from workflow", errors)
    check(all(s in states for s in wf.get("terminal_states",[])), "Unknown terminal state", errors)
    check(api.get("output_schema",{}).get("status")=="|".join(states), "CaseStatus differs from API", errors)
    check(api.get("output_schema",{}).get("evidence_kind")=="|".join(kinds), "ObservationKind differs from API", errors)
    check(api.get("errors")==error_codes, "ErrorCode differs from API", errors)
    for state in states:
        check(any(state in v for v in ui.get("presentation_states",[])), f"UI missing {state}", errors)
    shared = component.get("canonical_domain_contract_ref")
    for rid in ("EX-WF","EX-API","EX-UI","EX-DATA"):
        check(recs.get(rid,{}).get("fields",{}).get("canonical_contract_ref")==shared,
              f"{rid}: inconsistent canonical contract ref", errors)
    case = next((d for d in ex.get("logical_data_entities",[]) if d["name"]=="Case"),None)
    check(bool(case) and "case_status: "+"|".join(states) in case.get("fields",[]),
          "Case status differs from canonical contract", errors)
    for ci in ex.get("example_contracts",[]):
        for error in ci.get("errors",[]):
            check(error in error_codes, f"{ci['id']}: invalid API error {error}", errors)
    return errors, {"components":len(comps),"logical_runtime_units":len(runtime),
                    "shared_states":len(states),"shared_errors":len(error_codes)}

def main() -> int:
    model_path = Path(sys.argv[1]) if len(sys.argv)>1 else Path(MODEL)
    pilot_path = Path(sys.argv[2]) if len(sys.argv)>2 else Path(PILOT)
    component_path = Path(sys.argv[3]) if len(sys.argv)>3 else Path(COMPONENT)
    domain_path = Path(sys.argv[4]) if len(sys.argv)>4 else Path(DOMAIN)
    try:
        model = json.loads(model_path.read_text(encoding="utf-8"))
        pilot = json.loads(pilot_path.read_text(encoding="utf-8"))
        component = json.loads(component_path.read_text(encoding="utf-8"))
        domain = json.loads(domain_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print(json.dumps({"status":"error", "reason":str(error)},ensure_ascii=False))
        return 2
    errors, stats = validate(model,pilot)
    more_errors, component_stats = validate_component(model,pilot,component,domain)
    errors.extend(more_errors)
    stats.update(component_stats)
    print(json.dumps({"status":"pass" if not errors else "fail","stats":stats,"errors":errors},ensure_ascii=False,indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
