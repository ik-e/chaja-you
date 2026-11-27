"""D05 (R02/R03): H5 partial correction keeps the parent answer and never loses the previous state.

R03 rules under test:
- a leaf correction keeps existing ancestor answers (e.g. /packages) and sends both to I2;
- an existing answer is replaced only by the same field or an ancestor field;
- blocking ``unsupported`` on a corrected field (or its ancestor/descendant) -> VALIDATION_FAILED, nothing stored;
- a result that drops elements of a kept list answer -> RUNTIME_ERROR, nothing stored;
- blocking ``conflict`` on a corrected field -> FACT_CONFLICT, nothing stored;
- I2 failure during H5 -> MODEL_UNAVAILABLE, nothing stored (H4 still persists the issue);
- a result that arrives after another revision was stored is discarded (STALE_REVISION).
"""

import copy
import json
import unittest

from contracts.interfaces import PortFailure

from lesson_registration.app.coordinator import Coordinator
from lesson_registration.app.errors import AppError
from lesson_registration.app.store import Store

from support import TickClock, replay_cases, temp_db

A = "owner-a"
LEAF = "/packages/0/amount_vat_included_krw"


def _set(doc: dict, pointer: str, value) -> None:
    parts = pointer[1:].split("/")
    node = doc
    for p in parts[:-1]:
        node = node[int(p)] if isinstance(node, list) else node[p]
    last = parts[-1]
    if isinstance(node, list):
        node[int(last)] = value
    else:
        node[last] = value


class ApplyingPrep:
    """I2 fake following the R02 D05 rule: parent copy + leaf answers -> full result.

    A leaf answer without an ancestor answer is reported as blocking ``unsupported``.
    ``mutate`` lets a test damage the result; ``during`` runs inside the call (late-result races).
    """

    def __init__(self) -> None:
        self.base = replay_cases("kmong")["I2"]["output"]
        self.calls: list[dict] = []
        self.fail: BaseException | None = None
        self.mutate = None
        self.during = None

    def prepare(self, inp: dict) -> dict:
        self.calls.append(json.loads(json.dumps(inp)))
        if self.during is not None:
            hook, self.during = self.during, None
            hook()
        if self.fail is not None:
            err, self.fail = self.fail, None
            raise err
        out = copy.deepcopy(self.base)
        answers = sorted(inp["answers"], key=lambda a: a["field"].count("/"))
        fields = [a["field"] for a in answers]
        for a in answers:
            depth = a["field"].count("/")
            if depth > 1 and not any(a["field"].startswith(f + "/") for f in fields if f != a["field"]):
                out["ready"] = False
                out["issues"].append({"issue_id": f"unsupported-{a['field']}", "field": a["field"],
                                      "code": "unsupported", "message": "부모 답변 없음", "blocking": True})
                continue
            _set(out["values"], a["field"], copy.deepcopy(a["value"]))
        if self.mutate is not None:
            self.mutate(out)
        return out


class PartialEdit(unittest.TestCase):
    def setUp(self):
        self.path = temp_db(self)
        self.prep = ApplyingPrep()
        self.co = Coordinator(Store(self.path), prep=self.prep, clock=TickClock())
        src = self.co.create_source(A, {"raw_text": "합성 원본"})
        self.v1 = self.co.create_registration(A, {"source_id": src["source_id"], "selector": "kmong"})
        self.rid = self.v1["registration_id"]
        self.packages = copy.deepcopy(self.v1["preparation"]["values"]["packages"])
        self.v2 = self.edit(1, [{"field": "/packages", "value": self.packages}])

    def edit(self, rev, corrections):
        return self.co.edit_registration(A, self.rid, {"expected_revision": rev, "corrections": corrections})

    def stored(self):
        return self.co.get_registration(A, self.rid)

    def assertRejectedUnchanged(self, code, rev, corrections):
        before = self.stored()
        with self.assertRaises(AppError) as ctx:
            self.edit(rev, corrections)
        self.assertEqual(ctx.exception.code, code, ctx.exception.message)
        self.assertEqual(ctx.exception.current_revision, before["revision"])
        self.assertEqual(self.stored(), before)
        return ctx.exception

    def test_leaf_correction_keeps_parent_and_siblings(self):
        v3 = self.edit(2, [{"field": LEAF, "value": 260000}])
        sent = {a["field"]: a["value"] for a in self.prep.calls[-1]["answers"]}
        self.assertEqual(sent["/packages"], self.packages)
        self.assertEqual(sent[LEAF], 260000)
        got = v3["preparation"]["values"]["packages"]
        self.assertEqual(len(got), 3)
        self.assertEqual(got[0]["amount_vat_included_krw"], 260000)
        self.assertEqual({k: v for k, v in got[0].items() if k != "amount_vat_included_krw"},
                         {k: v for k, v in self.packages[0].items() if k != "amount_vat_included_krw"})
        self.assertEqual(got[1:], self.packages[1:])
        self.assertEqual(v3["revision"], 3)
        self.assertEqual(self.stored(), v3)

    def test_second_leaf_correction_replaces_only_the_same_leaf(self):
        self.edit(2, [{"field": LEAF, "value": 260000}])
        self.edit(3, [{"field": "/packages/1/sessions", "value": 6}])
        self.edit(4, [{"field": LEAF, "value": 270000}])
        sent = {a["field"]: a["value"] for a in self.prep.calls[-1]["answers"]}
        self.assertEqual(sent, {"/packages": self.packages, "/packages/1/sessions": 6, LEAF: 270000})

    def test_parent_correction_drops_old_leaf_answers(self):
        self.edit(2, [{"field": LEAF, "value": 260000}])
        replaced = copy.deepcopy(self.packages)
        replaced[2]["sessions"] = 8
        self.edit(3, [{"field": "/packages", "value": replaced}])
        sent = {a["field"]: a["value"] for a in self.prep.calls[-1]["answers"]}
        self.assertEqual(sent, {"/packages": replaced})

    def test_leaf_without_parent_is_rejected_and_state_kept(self):
        fresh = self.co.create_registration(A, {"source_id": self.v1["source_id"], "selector": "kmong"})
        self.rid = fresh["registration_id"]
        self.assertRejectedUnchanged("VALIDATION_FAILED", 1, [{"field": LEAF, "value": 260000}])

    def test_dropped_package_is_rejected_and_state_kept(self):
        def drop(ready):
            def mutate(out):
                out["values"]["packages"].pop()
                out["ready"] = ready
            return mutate
        for ready in (True, False):  # True: profile schema catches it; False: D05 list check catches it
            with self.subTest(ready=ready):
                self.prep.mutate = drop(ready)
                self.assertRejectedUnchanged("RUNTIME_ERROR", 2, [{"field": LEAF, "value": 260000}])

    def test_conflict_on_leaf_is_fact_conflict_and_state_kept(self):
        def conflict(out):
            out["ready"] = False
            out["issues"].append({"issue_id": "conflict-1", "field": LEAF, "code": "conflict",
                                  "message": "원본 가격과 다름", "blocking": True})
        self.prep.mutate = conflict
        self.assertRejectedUnchanged("FACT_CONFLICT", 2, [{"field": LEAF, "value": 999000}])

    def test_model_unavailable_during_edit_keeps_previous_state(self):
        for failure in (TimeoutError("model timeout"),
                        PortFailure({"code": "MODEL_UNAVAILABLE", "message": "model down"})):
            with self.subTest(failure=type(failure).__name__):
                self.prep.fail = failure
                self.assertRejectedUnchanged("MODEL_UNAVAILABLE", 2, [{"field": LEAF, "value": 260000}])
        self.assertTrue(self.stored()["preparation"]["ready"])

    def test_model_unavailable_on_reprepare_keeps_previous_state(self):
        self.prep.fail = TimeoutError()
        before = self.stored()
        with self.assertRaises(AppError) as ctx:
            self.co.edit_registration(A, self.rid, {"expected_revision": 2, "source_id": self.v1["source_id"]})
        self.assertEqual(ctx.exception.code, "MODEL_UNAVAILABLE")
        self.assertEqual(self.stored(), before)

    def test_late_result_after_newer_revision_is_discarded(self):
        def newer_edit():
            self.edit(2, [{"field": "/packages/2/sessions", "value": 6}])
        self.prep.during = newer_edit
        with self.assertRaises(AppError) as ctx:
            self.edit(2, [{"field": LEAF, "value": 260000}])
        self.assertEqual(ctx.exception.code, "STALE_REVISION")
        self.assertEqual(ctx.exception.current_revision, 3)
        now = self.stored()
        self.assertEqual(now["revision"], 3)
        self.assertEqual(now["preparation"]["values"]["packages"][2]["sessions"], 6)
        self.assertEqual(now["preparation"]["values"]["packages"][0]["amount_vat_included_krw"],
                         self.packages[0]["amount_vat_included_krw"])


if __name__ == "__main__":
    unittest.main()
