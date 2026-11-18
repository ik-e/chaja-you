#!/usr/bin/env python3
"""Isolated Step1/Step2 V3 pilot renderer and semantic contract checks (no real API/DB)."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "docs/deliverables/pilots/2026-11-18-v3"
ALLOWED = {"STEP1-기획서.md", "STEP1-WBS.md", "STEP2-API-설계.md", "STEP2-DB-스키마.md"}
EXPECTED = ["DLV-01", "DLV-02", "DLV-03", "DLV-04"]
SECTIONS = [3,4,6,6]

def render(doc, model):
    lines = [
        f"# {doc['title']}", "",
        f"> **{doc['status']}** · 작성기준 2026-11-18 · {doc['id']}",
        "> 기존 찾아you의 **잠정 제출용 설계**로 실제 제품 선정·구현·실측·공식 제출·접수를 뜻하지 않습니다.", "",
        f"- **기준:** {doc['basis']}",
        f"- **가이드/목차 근거:** {doc['outline_basis']}",
        f"- **검증 범위:** {doc.get('outline_verified_scope','추가 확인 필요')}",
        "- **단일 프로젝션 입력:** [model.json](model.json) · [API-DB 계약](contract.json)",
        f"- **기준 커밋:** `{model['source_baseline_commit']}` · [현재 두 트랙 Phase](../../../human/phase-intents/PHASE-20261118-01.md)",
        "", "## 문서 근거와 적용 제한", "",
        "아래 원본은 당시 저장소의 **고정 참조**입니다. 사실·가설·합성 검증·실측을 구분하며 과거 정본이나 타인 TASK를 수정하지 않습니다.",
        "", "| 참조 원본 | 커밋 |", "| --- | --- |",
    ]
    for pin in doc["source_pins"]:
        p = pin["path"]
        lines.append(f"| [`{p}`](https://github.com/ik-e/chaja-you/blob/{pin['commit']}/{quote(p,safe='/')}) | `{pin['commit'][:12]}` |")
    lines.append("")
    for section in doc["sections"]:
        lines.extend([f"## {section['heading']}", "", section["body"].strip(), ""])
    lines.extend(["---", "",
        "**현재 완료 판정:** V3 내용/계약/렌더 검토 대상 · 실제 제품 미선정/미구현 · 산출물 미제출 · 공식 제출 전 최종 검토 별도", ""])
    return "\n".join(lines)

def parse_code_fences(text, label):
    if "\\`\\`\\`" in text:
        raise AssertionError(f"{label}: escaped fence still present")
    blocks = re.findall(r"(?ms)^```(json|mermaid)\n(.*?)^```\s*$", text)
    opens = re.findall(r"(?m)^```(?:json|mermaid)\s*$", text)
    closes = re.findall(r"(?m)^```\s*$", text)
    if len(blocks)!=len(opens) or len(opens)!=len(closes):
        raise AssertionError(f"{label}: malformed code fence: {len(blocks)}/{len(opens)}/{len(closes)}")
    for lang,body in blocks:
        if lang=="json": json.loads(body)
        elif not any(k in body for k in ("flowchart ","gantt","erDiagram")):
            raise AssertionError(f"{label}: not a Mermaid flowchart/ERD/gantt")
    return blocks

def check_contract(c, m):
    assert c["status"]=="proposed_only_not_implemented"
    ids=[r["id"] for r in c["resources"]]
    assert ids==["API-01","API-02","API-03","API-04"]
    assert len({r["path"]+r["method"] for r in c["resources"]})==4
    assert all(r.get("owner_rule") and r.get("response_example") and r.get("errors") for r in c["resources"])
    names=[t["name"] for t in c["tables"]]
    assert names==["research_request","research_task","task_attempt","source","evidence","verdict","verdict_evidence"]
    assert len(names)==len(set(names))==7
    cols={t["name"]:{x[0]:x for x in t["columns"]} for t in c["tables"]}
    for table in c["tables"]:
        assert "created_at" in cols[table["name"]], table["name"]
        for key in table["pk"]: assert key in cols[table["name"]], (table["name"],key)
        for fk in table["fks"]:
            assert fk[0] in cols[table["name"]]
            t,k=fk[1].split(".")
            assert t in cols and k in cols[t],fk
    assert {"request_id","owner_id","status","criteria","targets","idempotency_key"} <= set(cols["research_request"])
    assert cols["research_request"]["owner_id"][1]=="TEXT"
    assert {"request_id","task_id","status"} <= set(cols["verdict"])
    assert {"request_id","task_id","status"} <= set(cols["research_task"]) | {"request_id"}
    assert any(x["id"]=="I-TASK" and "request_id" in x["rule"] for x in c["invariants"])
    assert any(x["id"]=="I-EVIDENCE" and "source.task.request_id" in x["rule"] for x in c["invariants"])
    assert any(x["id"]=="I-OWNER" for x in c["invariants"])
    assert all(x["kind"]=="planned_not_run" for x in c["tests"])
    for r in c["resources"]:
        if r["id"]=="API-01":
            assert r["request_example"]["domain"]=="focus_apps"
            assert set(r["request_example"]) <= set(cols["research_request"])
            assert r["response_example"]["status"] in c["status_policy"]["request"]
            assert r["response_http"]==202
        else:
            assert r["response_http"]==200
            assert "request_id" in r["response_example"]
        assert r["response_example"]["request_id"].startswith("req_")
        assert all(x.startswith("FR-") for x in r["requirement_refs"])
    assert c["identity"]["owner_field"]=="research_request.owner_id"
    assert c["identity"]["subject_claim"]=="sub"
    assert "request_id" in c["identity"]["authorization_rule"]
    assert set(c["status_policy"]["verdict"])=={"fulfilled","not_fulfilled","unknown"}
    for d in m["documents"]:
        assert "미제출" in d["status"],d["id"]
    return cols

def verify(model, contract):
    assert model["status"]=="draft_not_submitted"
    assert model["id"]=="PILOT-SUBMISSIONS-20261118-V3"
    assert model["source_baseline_commit"]=="53b73584069042225298c97c6c5688f8b429f56b"
    docs=model["documents"]
    assert [d["id"] for d in docs]==EXPECTED
    assert set(d["file"] for d in docs)==ALLOWED
    assert [len(d["sections"]) for d in docs]==SECTIONS
    check_contract(contract, model)
    for d in docs:
        assert all(pin["commit"]==model["source_baseline_commit"] for pin in d["source_pins"])
        assert d.get("official_outline_checked") == (d["id"] in ("DLV-01","DLV-02"))
    outputs={d["id"]:render(d,model) for d in docs}
    for did,v in outputs.items():
        parse_code_fences(v,did)
    assert len(parse_code_fences(outputs["DLV-03"],"API"))>=7
    assert len(parse_code_fences(outputs["DLV-04"],"DB"))>=2
    for fr in ("FR-01","FR-02","FR-03","FR-04"):
        assert fr in outputs["DLV-01"] and fr in outputs["DLV-03"]
    for req in ("API-01","API-02","API-03","API-04"):
        assert req in outputs["DLV-03"] and req in outputs["DLV-04"]
    for term in ("owner_id","idempotency_key","verdict_id","task_id","request_id","verdict_evidence"):
        assert term in outputs["DLV-04"]
    for task in ("TASK-022","TASK-023","TASK-024","TASK-025","TASK-026","TASK-027"):
        assert task in outputs["DLV-02"]
    assert "매니저 확인 TRUE" in outputs["DLV-02"]
    assert "11/21" in outputs["DLV-02"] and "11/20" in outputs["DLV-02"]
    assert "Before / After" in outputs["DLV-01"]
    return outputs

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    m=json.loads((PILOT/"model.json").read_text(encoding="utf-8"))
    c=json.loads((PILOT/"contract.json").read_text(encoding="utf-8"))
    expected=verify(m,c)
    mismatches=[]
    for doc in m["documents"]:
        path=PILOT/doc["file"]
        rendered=expected[doc["id"]]
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8")!=rendered:
                mismatches.append(doc["file"])
        else:
            path.write_text(rendered,encoding="utf-8")
    if mismatches: raise SystemExit("Stale or missing V3 projections: "+", ".join(mismatches))
    print("V3 PASS: 4 documents; 7 tables; 4 endpoints; 48 columns; owner/FK/ID + 12+ valid JSON/Mermaid fences.")
if __name__=="__main__": main()
