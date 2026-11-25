"""RESULT: I5 evaluate(EvaluateInput) -> Result. Pure: no I/O, no browser commands.

Fail closed: insufficient or mismatched evidence never yields ``confirmed``.
Payload digest rule (to agree with R05): canonical SHA-256 of the accepted
``scope.values``; asset digests must equal the accepted asset digests as a set.
"""

from __future__ import annotations

from .ids import digest

NEXT_CONFIRMED = "모의 등록이 확인되었습니다."
NEXT_NOT_REACHED = "등록 목표에 도달하지 못했습니다. 승인 내용과 결과를 확인한 뒤 새 등록 요청으로 진행하세요."
NEXT_UNKNOWN = "결과를 확인할 수 없습니다. 자동 재제출하지 않습니다. 플랫폼에서 직접 등록 여부를 확인하세요."


def payload_digest(values: dict) -> str:
    return digest(values)


def evaluate(inp: dict) -> dict:
    try:
        return _evaluate(inp)
    except Exception:  # evaluator error -> fail closed
        return {
            "goal_verdict": "unknown",
            "environment": "mock",
            "effects": [],
            "evidence": [],
            "error": {"code": "EVIDENCE_INSUFFICIENT", "message": "결과 판정 중 오류가 발생했습니다."},
            "next_action": NEXT_UNKNOWN,
        }


def _evaluate(inp: dict) -> dict:
    profile = inp["profile"]
    scope = inp["accepted"]["scope"]
    report = inp["report"]
    records = {e["evidence_id"]: e for e in inp["evidence"]}
    target_label = f"{scope['target']['platform']} {scope['target']['object_kind']}"

    effects = [
        {"step_id": o["step_id"], "operation_id": o["operation_id"], "verdict": o["verdict"],
         "evidence_refs": [r for r in o["evidence_refs"] if r in records]}
        for o in report["observations"]
    ]
    evidence_views = [
        {"evidence_id": e["evidence_id"], "kind": e["kind"], "method": e["method"], "target_label": target_label,
         "summary": _summary(e), "observed_at": e["observed_at"], "environment": e["environment"]}
        for e in inp["evidence"]
    ]

    verdict, reason = _goal(profile, scope, report.get("goal_observation"), records)
    if any(e["verdict"] == "unknown" for e in effects) and verdict == "confirmed":
        verdict, reason = "unknown", "EFFECT_UNKNOWN"

    result = {
        "goal_verdict": verdict,
        "environment": "mock",
        "effects": effects,
        "evidence": evidence_views,
        "next_action": {"confirmed": NEXT_CONFIRMED, "not_reached": NEXT_NOT_REACHED}.get(verdict, NEXT_UNKNOWN),
    }
    error = report.get("error")
    if error is not None:
        result["error"] = error
    elif verdict != "confirmed":
        code = reason if reason in ("EFFECT_UNKNOWN", "EVIDENCE_INSUFFICIENT") else "EVIDENCE_INSUFFICIENT"
        result["error"] = {"code": code, "message": _MESSAGES.get(reason, "확인 근거가 부족합니다.")}
    return result


_MESSAGES = {
    "no_goal": "목표 관측 근거가 없습니다.",
    "untrusted": "목표 관측이 저장된 증거와 일치하지 않습니다.",
    "method": "프로필이 요구하는 확인 방법이 아닙니다.",
    "target": "관측 대상이 승인된 대상과 다릅니다.",
    "payload": "관측된 값이 승인된 값과 다릅니다.",
    "assets": "관측된 첨부가 승인된 첨부와 다릅니다.",
    "state": "목표 상태에 도달하지 않았습니다.",
    "EFFECT_UNKNOWN": "효과 여부를 확인할 수 없는 단계가 있습니다.",
}


def _goal(profile: dict, scope: dict, goal: dict | None, records: dict) -> tuple[str, str]:
    goal_rule = profile["goal"]
    if goal is None:
        return "unknown", "no_goal"
    record = records.get(goal["evidence_ref"])
    if (
        record is None
        or record["kind"] != "goal"
        or record.get("payload_digest") != goal["payload_digest"]
        or sorted(record.get("asset_digests", [])) != sorted(goal["asset_digests"])
        or record.get("observed_state") != goal["observed_state"]
        or record["target"] != goal["target"]
    ):
        return "unknown", "untrusted"
    if goal["method"] not in goal_rule["methods"] or goal["goal_kind"] != goal_rule["kind"]:
        return "unknown", "method"
    if goal["target"] != scope["target"]:
        return "not_reached", "target"
    if goal["payload_digest"] != payload_digest(scope["values"]):
        return "not_reached", "payload"
    if goal_rule["requires_asset_digests"] and sorted(goal["asset_digests"]) != sorted(a["digest"] for a in scope["assets"]):
        return "not_reached", "assets"
    if goal["observed_state"] != goal_rule["observed_state"]:
        return "not_reached", "state"
    return "confirmed", "ok"


def _summary(record: dict) -> str:
    if record["kind"] == "goal":
        return f"목표 관측: {record.get('observed_state', '-')} ({record['method']})"
    if record["kind"] == "operation":
        return f"단계 관측: {record.get('operation_id', '-')}"
    return "오류 관측"
