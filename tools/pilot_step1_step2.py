#!/usr/bin/env python3
"""Render/verify isolated 2026-11-18 pilot Markdown. Never change other project artifacts."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "docs/deliverables/pilots/2026-11-18"
MODEL = PILOT / "model.json"
ALLOWED = {
    "STEP1-기획서.md","STEP1-WBS.md",
    "STEP2-API-설계.md","STEP2-DB-스키마.md",
}

def render(doc, model):
    lines = [
        f"# {doc['title']}", "",
        f"> **{doc['status']}** · 적용 기준: 2026-11-18 · 문서 ID: `{doc['id']}`",
        ">", " >", 
        "> 이 문서는 기존 찾아you 기획의 **트랙 B 제출 대응용 잠정 시연본**입니다. 프로젝트 주제·기능·기술 채택 및 실제 구현·제출을 의미하지 않습니다.",
        "",
        f"- **기준:** {doc['basis']}",
        f"- **목차 근거:** {doc['outline_basis']}",
        f"- **생성 입력:** [파일럿 정본](model.json) · 기준 커밋 `{model['source_baseline_commit']}`",
        "- **Phase:** [PHASE-20261118-01](../../../human/phase-intents/PHASE-20261118-01.md)",
        "", "## 문서·근거 경계", "",
        "기존 기획/설계 원본을 변경하지 않고 동일 기준 데이터에서 생성한 **검토용 Markdown**입니다. 해당 커밋이 당시 참고 자료이며, 현재 제품의 승인/개발/제출 상태는 아닙니다.",
        "", "| 기준 원본 | 원본 고정 커밋 |", "| --- | --- |",
    ]
    for pin in doc["source_pins"]:
        from urllib.parse import quote
        p = pin["path"]
        lines.append(f"| [`{p}`](https://github.com/ik-e/chaja-you/blob/{pin['commit']}/{quote(p, safe='/')}) | `{pin['commit'][:12]}` |")
    lines.append("")
    for section in doc["sections"]:
        lines.extend([f"## {section['heading']}", "", section["body"].strip(), ""])
    lines.extend(["---", "",
        "**검토 상태:** 공식 수정본 필수 목차 직접 대조(G0) 미완료 · 기술/구현 승인 미완료 · 제출·접수 미완료", ""])
    return "\n".join(lines)

def verify_model(model):
    assert model["status"] == "draft_not_submitted"
    assert model["source_baseline_commit"] == "53b73584069042225298c97c6c5688f8b429f56b"
    assert len(model["documents"]) == 4
    assert [x["id"] for x in model["documents"]] == ["DLV-01","DLV-02","DLV-03","DLV-04"]
    assert set(d["file"] for d in model["documents"]) == ALLOWED
    for d in model["documents"]:
        assert len(d["sections"]) >= 3
        assert d["source_pins"] and all(x["commit"] == model["source_baseline_commit"] for x in d["source_pins"])
        assert "미제출" in d["status"] and not d.get("submitted_at")
        assert "미검증" in d["outline_basis"] or "미검증" in d["status"] or "미확정" in d["outline_basis"] or "대조" in d["outline_basis"]
    docs={d["id"]:d for d in model["documents"]}
    content=lambda x:"\n".join(s["body"] for s in docs[x]["sections"])
    proposal, wbs, api, db=(content(x) for x in ["DLV-01","DLV-02","DLV-03","DLV-04"])
    for fr in ["FR-01","FR-02","FR-03","FR-04"]:
        assert fr in proposal and fr in api, fr
    for field in ["domain","targets","criteria","discovery_rule","request_id","task_id","status"]:
        assert field in api and field in db,field
    for field in ["source_id","evidence_id","verdict_id","attempt_id"]:
        assert field in api and field in db,field
    for id in ["TASK-022","TASK-023","TASK-024","TASK-025","TASK-026","TASK-027"]:
        assert id in wbs,id
    assert "11/21" in wbs and "11/20" in wbs
    assert "미검증" in proposal and "미구현" in api and "미구현" in db
    # Show usage boundary and no false approval.
    for d in model["documents"]:
        assert "미제출" in d["status"]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    m=json.loads(MODEL.read_text(encoding="utf-8"))
    verify_model(m)
    mismatches=[]
    for d in m["documents"]:
        target=PILOT / d["file"]
        expected=render(d,m)
        if args.check:
            if not target.is_file() or target.read_text(encoding="utf-8") != expected:
                mismatches.append(d["file"])
        else:
            target.write_text(expected,encoding="utf-8")
    if mismatches:
        raise SystemExit("stale pilot projections: "+", ".join(mismatches))
    print("pilot: 4 isolated Step1/Step2 projections, links, state & API/DB cross-check PASS")
if __name__=="__main__":
    main()
