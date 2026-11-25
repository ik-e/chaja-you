"""CO: use cases behind H1~H9. Owns registration/job state transitions.

S1 implements the source use cases (H1~H3). ``owner_ref`` always comes from
the authenticated app context, never from request bodies.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from collections.abc import Callable

from contracts.interfaces import PortFailure, Providers

from . import contract
from .errors import AppError
from .ids import bytes_digest, digest, inspect_image, new_id
from .knowledge import Knowledge
from .ports import Clock, ExecutionPort, PreparationPort, SystemClock
from .result import NEXT_NOT_REACHED, NEXT_UNKNOWN, ResultEvaluator, evaluate
from .store import Store, tx
from .store import atomic, repo
from .store.coordinator_store import SqliteCoordinatorStore

REVIEW_NOTICE = "합성 시험 전용. 실행 후 수정·재개·취소 없음."

DEFAULT_LIMIT = 20
EXCERPT_CHARS = 40
MAX_ASSET_BYTES = 5 * 1024 * 1024  # provisional (SPEC §10): profile limit not yet confirmed


class Coordinator:
    """CO. Providers follow contracts.interfaces (Registry, PreparationPort, ExecutionPort, ResultPort).

    Pass ``providers=Providers(...)`` (IB-05 explicit injection), or the individual keyword
    arguments for module-level tests. No silent fake fallback: missing PREP/EXEC are reported.
    """

    def __init__(
        self,
        store: Store,
        *,
        providers: Providers | None = None,
        knowledge: Knowledge | None = None,
        prep: PreparationPort | None = None,
        exec_port: ExecutionPort | None = None,
        result: object | None = None,
        clock: Clock | None = None,
        on_accepted: Callable[[str], None] | None = None,
    ) -> None:
        if providers is not None:
            knowledge, prep, exec_port, result = (providers.registry, providers.preparation,
                                                  providers.execution, providers.result)
        self.store = store
        self.knowledge = knowledge or Knowledge()
        self.prep = prep
        self.exec = exec_port
        self.result = result or ResultEvaluator()
        self.clock = clock or SystemClock()
        self.on_accepted = on_accepted  # dispatch hook, called after the accept transaction commits
        self.coord_store = SqliteCoordinatorStore(store, self.clock, self._view)
        self._cursor_key = store.cursor_secret()

    # ---------- H1 ----------
    def create_source(
        self,
        owner_ref: str,
        source_input: dict,
        new_files: dict[str, bytes | tuple[bytes, str | None]] | None = None,
    ) -> dict:
        """H1. ``new_files`` maps part_name -> bytes, or (bytes, declared Content-Type) from multipart."""
        contract.validate("SourceInput", source_input)
        new_files = dict(new_files or {})
        declared = [a["part_name"] for a in source_input.get("new_assets", [])]
        if len(set(declared)) != len(declared):
            raise AppError("INVALID_REQUEST", "duplicate part_name")
        if set(declared) != set(new_files):
            raise AppError("INVALID_REQUEST", "multipart parts must match new_assets exactly")

        prepared: list[tuple[dict, bytes]] = []
        for spec in source_input.get("new_assets", []):
            part = new_files[spec["part_name"]]
            data, declared_mime = part if isinstance(part, tuple) else (part, None)
            if not isinstance(data, (bytes, bytearray)):
                raise AppError("INVALID_REQUEST", f"part {spec['part_name']} is not a file")
            data = bytes(data)
            if not spec["rights_confirmed"]:
                raise AppError("VALIDATION_FAILED", f"rights not confirmed for {spec['part_name']}")
            if not data or len(data) > MAX_ASSET_BYTES:
                raise AppError("VALIDATION_FAILED", f"asset size not allowed for {spec['part_name']}")
            info = inspect_image(data)
            if info is None:
                raise AppError("VALIDATION_FAILED", f"unsupported or corrupt image {spec['part_name']}")
            if declared_mime is not None and declared_mime.split(";")[0].strip().lower() != info["mime"]:
                raise AppError("VALIDATION_FAILED", f"declared type does not match the bytes of {spec['part_name']}")
            prepared.append(
                (
                    {
                        "asset_id": new_id("asset"),
                        "digest": bytes_digest(data),
                        "mime": info["mime"],
                        "bytes": len(data),
                        "width": info["width"],
                        "height": info["height"],
                        "rights_confirmed": True,
                    },
                    data,
                )
            )

        reuse_ids = source_input.get("reuse_asset_ids", [])
        if not source_input["raw_text"].strip() and not reuse_ids and not prepared:
            raise AppError("VALIDATION_FAILED", "raw_text or a rights-confirmed asset is required")

        now = self.clock.now()
        source_id = new_id("source")
        previous = source_input.get("previous_source_id")
        with self.store.connect() as conn, tx(conn):
            if previous is not None and not repo.source_exists(conn, owner_ref, previous):
                raise AppError("NOT_FOUND", "previous source not found")
            reused = repo.owned_asset_refs(conn, owner_ref, reuse_ids)
            if len(reused) != len(reuse_ids):
                raise AppError("NOT_FOUND", "asset not found")
            if not all(a["rights_confirmed"] for a in reused.values()):
                raise AppError("VALIDATION_FAILED", "reused asset lacks confirmed rights")
            for asset, data in prepared:
                repo.insert_asset(conn, owner_ref, asset, data, now)
            asset_ids = list(reuse_ids) + [a["asset_id"] for a, _ in prepared]
            repo.insert_source(conn, owner_ref, source_id, previous, source_input["raw_text"], asset_ids, now)
            view = repo.get_source(conn, owner_ref, source_id)
        contract.validate("SourceView", view)
        return view

    # ---------- H2 ----------
    def list_sources(self, owner_ref: str, query: dict | None = None) -> dict:
        query = query or {}
        contract.validate("ListQuery", query)
        limit = query.get("limit", DEFAULT_LIMIT)
        after = self._decode_cursor(owner_ref, "sources", query["cursor"]) if "cursor" in query else None
        with self.store.connect() as conn:
            rows = repo.list_sources(conn, owner_ref, after, limit + 1)
        items = [
            {"source_id": r["source_id"], "excerpt": r["raw_text"][:EXCERPT_CHARS], "created_at": r["created_at"]}
            for r in rows[:limit]
        ]
        out: dict = {"items": items}
        if len(rows) > limit:
            last = rows[limit - 1]
            out["next_cursor"] = self._encode_cursor(owner_ref, "sources", [last["created_at"], last["source_id"]])
        contract.validate("SourceList", out)
        return out

    # ---------- H3 ----------
    def get_source(self, owner_ref: str, source_id: str) -> dict:
        with self.store.connect() as conn:
            view = repo.get_source(conn, owner_ref, source_id)
        if view is None:
            raise AppError("NOT_FOUND", "source not found")
        return view

    # ---------- H4 ----------
    def create_registration(self, owner_ref: str, reg_input: dict) -> dict:
        contract.validate("RegistrationInput", reg_input)
        source = self.get_source(owner_ref, reg_input["source_id"])
        resolved = self.knowledge.resolve(reg_input["selector"])
        if resolved["status"] == "supported":
            profile = resolved["profile"]
            support = "supported"
            preparation = self._prepare(source, profile, [])
        else:
            profile = None
            support = resolved["status"]
            preparation = _blocked_preparation("unsupported", resolved["reason"])
        reg = {
            "registration_id": new_id("registration"),
            "source_id": source["source_id"],
            "selector": reg_input["selector"],
            "support": support,
            "profile": None if profile is None else profile["ref"],
            "preparation": preparation,
            "answers": [],
            "revision": 1,
            "auth": {"state": "none"},
            "target": None,
            "connection": None,
            "review": None,
            "job_state": None,
        }
        now = self.clock.now()
        with self.store.connect() as conn, tx(conn):
            if not repo.source_exists(conn, owner_ref, source["source_id"]):
                raise AppError("NOT_FOUND", "source not found")
            repo.insert_registration(conn, owner_ref, reg, now)
            stored = repo.get_registration(conn, owner_ref, reg["registration_id"])
        return self._view(stored)

    # ---------- H5 ----------
    def edit_registration(self, owner_ref: str, registration_id: str, edit: dict) -> dict:
        contract.validate("PreparationEdit", edit)
        changes = {k for k in ("source_id", "selector", "answers", "corrections") if k in edit}
        if not changes:
            raise AppError("INVALID_REQUEST", "nothing to edit")
        reg = self._load(owner_ref, registration_id)
        self._check_prestart(reg, edit["expected_revision"])
        if reg["auth"]["state"] in ("human", "verifying"):
            raise AppError("INVALID_PHASE", "close the authentication session first",
                           current_revision=reg["revision"])

        new = dict(reg)
        new_source_id = edit.get("source_id", reg["source_id"])
        new_selector = edit.get("selector", reg["selector"])
        target_changed = new_source_id != reg["source_id"] or new_selector != reg["selector"]
        has_values = bool({"answers", "corrections"} & changes)
        if target_changed and has_values:
            raise AppError("INVALID_REQUEST", "answers/corrections cannot accompany a source or selector change")
        # Branch 1: new source/selector, or an explicit re-prepare of the same source (no values).
        if target_changed or not has_values:
            source = self.get_source(owner_ref, new_source_id)
            resolved = self.knowledge.resolve(new_selector)
            new["source_id"], new["selector"] = new_source_id, new_selector
            if resolved["status"] == "supported":
                profile = resolved["profile"]
                if target_changed or reg["profile"] != profile["ref"]:
                    new["answers"] = []
                new["support"], new["profile"] = "supported", profile["ref"]
                new["preparation"] = self._prepare(source, profile, new["answers"])
            else:
                new["support"], new["profile"], new["answers"] = resolved["status"], None, []
                new["preparation"] = _blocked_preparation("unsupported", resolved["reason"])
        else:
            if reg["support"] != "supported":
                raise AppError("INVALID_PHASE", "unsupported target cannot be prepared",
                               current_revision=reg["revision"])
            profile = self.knowledge.get_profile(reg["profile"])  # PROFILE_CHANGED on drift
            source = self.get_source(owner_ref, reg["source_id"])
            resolved_answers = self._normalize(reg, profile, edit.get("answers", []), edit.get("corrections", []))
            new["answers"] = _merge_answers(reg["answers"], resolved_answers)
            new["preparation"] = self._prepare(source, profile, new["answers"])
            corrected = {a["field"] for a in resolved_answers if "origin_issue_id" not in a}
            if any(
                i["code"] == "conflict" and i["blocking"] and i["field"] in corrected
                for i in new["preparation"]["issues"]
            ):
                # PREP judged the correction to contradict a shared source fact: needs a new Source.
                raise AppError("FACT_CONFLICT", "source facts change only through a new Source version",
                               current_revision=reg["revision"])

        material = any(
            new[k] != reg[k] for k in ("source_id", "selector", "support", "profile", "answers", "preparation")
        )
        if not material:
            return self._view(reg)
        new["revision"] = reg["revision"] + 1
        new["review"] = None
        new["target"] = None
        new["connection"] = None
        if reg["auth"]["state"] == "verified":
            new["auth"] = {"state": "closed"}
        now = self.clock.now()
        with self.store.connect() as conn, tx(conn):
            if not repo.update_registration_if(conn, owner_ref, new, reg["revision"], now):
                current = repo.get_registration(conn, owner_ref, registration_id)
                self._check_prestart(current, reg["revision"])
                raise AppError("STALE_REVISION", "registration changed", current_revision=current["revision"])
            stored = repo.get_registration(conn, owner_ref, registration_id)
        return self._view(stored)

    # ---------- H6 ----------
    def authenticate(self, owner_ref: str, registration_id: str, command: dict) -> dict:
        contract.validate("AuthCommand", command)
        reg = self._load(owner_ref, registration_id)
        self._check_prestart(reg, command["expected_revision"])
        action = command["action"]
        auth = reg["auth"]
        cur = reg["revision"]
        if action == "open":
            if reg["support"] != "supported" or not reg["preparation"]["ready"]:
                raise AppError("INVALID_PHASE", "registration is not ready for authentication", current_revision=cur)
            if auth["state"] not in ("none", "closed"):
                raise AppError("INVALID_PHASE", "authentication already open", current_revision=cur)
        else:
            needs = ("human",) if action in ("finish", "refresh") else ("human", "verifying", "verified")
            if auth["state"] not in needs:
                raise AppError("INVALID_PHASE", f"cannot {action} from {auth['state']}", current_revision=cur)
            if command["generation"] != auth.get("generation"):
                raise AppError("STALE_REVISION", "authentication generation changed", current_revision=cur)
        if self.exec is None:
            raise AppError("RUNTIME_ERROR", "authentication runtime not connected")

        profile = self.knowledge.get_profile(reg["profile"])
        auth_input = {"registration_id": registration_id, "profile_ref": profile["ref"],
                      "owner_ref": owner_ref, "command": command}
        contract.validate("AuthInput", auth_input)

        new = dict(reg)
        grant = None
        failure: AppError | None = None
        try:
            out = self.exec.authenticate(json.loads(json.dumps(auth_input)))
            if not contract.is_valid("AuthOutput", out):
                raise AppError("RUNTIME_ERROR", "runtime returned an invalid authentication result")
        except (AppError, PortFailure) as exc:
            failure = _port_error(exc, allowed=("ACCOUNT_MISMATCH", "CONNECTION_MISMATCH", "PERMISSION_DENIED",
                                                "AUTH_REQUIRED"))
            out = None
        except Exception:
            failure = AppError("RUNTIME_ERROR", "authentication runtime failed; reload the registration")
            out = None

        if failure is not None or action == "close":
            # Fence: any failure or close ends the session with no verified binding.
            new["auth"] = {"state": "closed"}
            new["target"] = new["connection"] = new["review"] = None
        else:
            state = out["auth"]["state"]
            if state == "verified":
                failure = self._check_binding(out, profile, command)
                if failure is None:
                    target_view = {
                        "status": out["target"]["status"],
                        "account_label": out["target"]["account_label"],
                        "object_kind": out["target"]["identity"]["object_kind"],
                        "target_label": f"{profile['ref']['platform']} 신규 {profile['ref']['object_kind']}",
                    }
                    new["auth"] = {"state": "verified", "generation": out["auth"]["generation"],
                                   "account_label": out["auth"]["account_label"]}
                    new["target"] = {"trusted": out["target"], "view": target_view}
                    new["connection"] = out["connection"]
                    new["review"] = None  # computed below once the new revision is known
                else:
                    new["auth"] = {"state": "closed"}
                    new["target"] = new["connection"] = new["review"] = None
            else:
                if action == "finish" and state == "human":
                    failure = AppError("RUNTIME_ERROR", "runtime did not finish verification")
                new["auth"] = {k: v for k, v in out["auth"].items()}
                if state in ("closed", "none"):
                    new["target"] = new["connection"] = new["review"] = None
                grant = out.get("grant")
                if action in ("open", "refresh"):
                    if state != "human" or grant is None or grant["generation"] != out["auth"].get("generation"):
                        failure = AppError("RUNTIME_ERROR", "runtime returned no usable viewer grant")
                        new["auth"] = {"state": "closed"}
                        grant = None
                    elif action == "refresh" and grant["generation"] == auth.get("generation"):
                        failure = AppError("RUNTIME_ERROR", "refresh must rotate the viewer grant")
                        new["auth"] = {"state": "closed"}
                        grant = None
                else:
                    grant = None

        new["revision"] = cur + 1
        if failure is None and new["auth"]["state"] == "verified":
            new["review"] = self._review(owner_ref, new, profile)
        now = self.clock.now()
        with self.store.connect() as conn, tx(conn):
            if not repo.update_registration_if(conn, owner_ref, new, cur, now):
                latest = repo.get_registration(conn, owner_ref, registration_id)
                self._check_prestart(latest, cur)
                raise AppError("STALE_REVISION", "registration changed", current_revision=latest["revision"])
            stored = repo.get_registration(conn, owner_ref, registration_id)
        if failure is not None:
            failure.current_revision = stored["revision"]
            raise failure
        response = {"registration": self._view(stored)}
        if grant is not None:
            response["grant"] = grant
        contract.validate("AuthResponse", response)
        return response

    @staticmethod
    def _check_binding(out: dict, profile: dict, command: dict) -> AppError | None:
        identity = out["target"]["identity"]
        conn_b = out["connection"]
        ref = profile["ref"]
        if (identity["platform"], identity["object_kind"], identity["environment"]) != (
            ref["platform"], ref["object_kind"], ref["environment"]
        ):
            return AppError("CONNECTION_MISMATCH", "verified target is not this registration's platform object")
        if conn_b["account_ref"] != identity["external_account_ref"]:
            return AppError("ACCOUNT_MISMATCH", "verified account does not own the target")
        if conn_b["verified_generation"] != out["auth"]["generation"] or out["auth"]["generation"] != command["generation"]:
            return AppError("CONNECTION_MISMATCH", "connection generation does not match the finished session")
        return None

    def _review(self, owner_ref: str, reg: dict, profile: dict) -> dict | None:
        """Review exists only for ready + verified + new target + supported (common state.prestart)."""
        target = reg.get("target")
        if not (reg["support"] == "supported" and reg["preparation"]["ready"]
                and reg["auth"]["state"] == "verified" and target and target["trusted"]["status"] == "new"):
            return None
        source = self.get_source(owner_ref, reg["source_id"])
        body = {
            "values": reg["preparation"]["values"],
            "assets": source["asset_refs"],
            "profile_ref": profile["ref"],
            "target": target["view"],
            "procedure": [s["label"] for s in profile["steps"]],
            "goal": profile["goal"]["kind"],
            "notice": REVIEW_NOTICE,
        }
        # data-contract-v4: review digest binds the exact internal Scope (revision, verified connection,
        # target, values, assets...). The public view shows values and labels, never the connection.
        scope = _build_scope(reg, profile, source["asset_refs"])
        review = {"digest": digest(scope), **body}
        contract.validate("ReviewView", review)
        return review

    # ---------- H7 ----------
    def start(self, owner_ref: str, registration_id: str, start_input: dict) -> tuple[int, dict]:
        """Final approval + durable acceptance. Returns (202, view) first time, (200, view) on exact replay.

        Pre-checks give precise errors; CoordinatorStore.accept re-checks them atomically.
        """
        contract.validate("StartInput", start_input)
        reg = self._load(owner_ref, registration_id)
        with self.store.connect() as conn:
            prior = atomic.find_job_by_key(conn, owner_ref, start_input["request_key"])
        if prior is not None:  # exact-key replay precedes stale/phase checks; accept decides atomically
            return self._accept(owner_ref, registration_id, start_input, None)
        cur = reg["revision"]
        if reg["job_state"] is not None:
            raise AppError("IDEMPOTENCY_CONFLICT", "registration already accepted under another key",
                           current_revision=cur)
        if start_input["expected_revision"] != cur:
            raise AppError("STALE_REVISION", "registration changed", current_revision=cur)
        if reg["support"] != "supported":
            raise AppError("INVALID_PHASE", "unsupported target", current_revision=cur)
        profile = self.knowledge.get_profile(reg["profile"])
        if reg["auth"]["state"] != "verified" or not reg.get("connection"):
            raise AppError("AUTH_REQUIRED", "verified authentication required", current_revision=cur)
        status = reg["target"]["trusted"]["status"]
        if status == "ambiguous":
            raise AppError("TARGET_AMBIGUOUS", "target could not be identified safely", current_revision=cur)
        if status == "existing":
            raise AppError("DUPLICATE_RISK", "target already exists", current_revision=cur)
        if not reg["preparation"]["ready"] or reg.get("review") is None:
            raise AppError("INVALID_PHASE", "registration is not ready for approval", current_revision=cur)
        if start_input["review_digest"] != reg["review"]["digest"]:
            raise AppError("APPROVAL_INVALID", "approved review is not the current review", current_revision=cur)
        scope = _build_scope(reg, profile, reg["review"]["assets"])
        contract.validate("Scope", scope)
        if digest(scope) != reg["review"]["digest"]:
            raise AppError("APPROVAL_INVALID", "current scope no longer matches the reviewed scope",
                           current_revision=cur)
        return self._accept(owner_ref, registration_id, start_input, scope)

    def _accept(self, owner_ref: str, registration_id: str, start_input: dict, scope: dict | None) -> tuple[int, dict]:
        if scope is None:
            # Replay path: the stored scope is never rebuilt; accept returns the persisted view or a conflict.
            scope = {"revision": -1, "connection": None, "target": None}
        replayed, view = self.coord_store.accept_with_status(owner_ref, registration_id, start_input, scope)
        if replayed:
            return 200, view
        if self.on_accepted is not None:
            self.on_accepted(registration_id)  # dispatch only after commit
        return 202, view

    # ---------- S4: execution ----------
    def run_job(self, registration_id: str) -> str:
        """Dispatch an accepted job to I4 once, then judge and commit a terminal state.

        Never re-dispatches: a lost response or crash fences the job and keeps unknown effects.
        Returns the terminal state ("done"/"stopped") or the current state if not active.
        """
        with self.store.connect() as conn:
            job = atomic.find_job(conn, registration_id)
        if job is None:
            raise AppError("NOT_FOUND", "no accepted job")
        if job["state"] != "active":
            return job["state"]
        accepted = json.loads(job["accepted_scope_json"])
        runtime_error: dict | None = None
        goal_obs: dict | None = None
        if self.exec is None:
            runtime_error = {"code": "RUNTIME_ERROR", "message": "실행 모듈이 연결되지 않았습니다."}
        else:
            try:
                report = self.exec.execute({"accepted": json.loads(json.dumps(accepted))})
                if not contract.is_valid("ExecutionReport", report):
                    raise ValueError("invalid ExecutionReport")
                runtime_error = report.get("error")
                goal_obs = report.get("goal_observation")
            except PortFailure as exc:
                runtime_error = exc.error if contract.is_valid("Error", exc.error) else {
                    "code": "RUNTIME_ERROR", "message": "실행 모듈이 잘못된 오류를 반환했습니다."}
            except Exception:
                runtime_error = {"code": "EFFECT_UNKNOWN", "message": "실행 응답을 받지 못했습니다. 효과를 확인할 수 없습니다."}
        return self._conclude(registration_id, accepted, goal_obs, runtime_error)

    def recover(self) -> list[str]:
        """At startup: every active/stopping job has lost its worker. Fence and stop; never resume."""
        with self.store.connect() as conn:
            rows = conn.execute("SELECT registration_id, accepted_scope_json FROM jobs"
                                " WHERE state IN ('active','stopping')").fetchall()
        stopped = []
        for row in rows:
            err = {"code": "RUNTIME_ERROR", "message": "작업 실행기가 중단되어 작업을 멈췄습니다. 자동 재개하지 않습니다."}
            self._conclude(row["registration_id"], json.loads(row["accepted_scope_json"]), None, err)
            stopped.append(row["registration_id"])
        return stopped

    def _conclude(self, registration_id: str, accepted: dict, goal_obs: dict | None, error: dict | None) -> str:
        with self.store.connect() as conn:
            job = atomic.find_job(conn, registration_id)
        if job["state"] in ("done", "stopped"):
            return job["state"]
        if error is not None:
            self.coord_store.fence(registration_id, error)
        # Judge only on what STORE holds (trusted), outside any transaction.
        with self.store.connect() as conn:
            observations = atomic.stored_observations(conn, registration_id)
            evidence = atomic.stored_evidence(conn, registration_id)
            effects = atomic.effects_of(conn, registration_id)
        profile = self.knowledge.get_profile(accepted["scope"]["profile_ref"])
        report = {"observations": observations}
        if goal_obs is not None:
            report["goal_observation"] = goal_obs
        if error is not None:
            report["error"] = error
        evaluate_input = {"profile": profile, "accepted": accepted, "report": report, "evidence": evidence}
        contract.validate("EvaluateInput", evaluate_input)
        try:
            result = self.result.evaluate(evaluate_input)
            if not contract.is_valid("Result", result):
                raise ValueError("invalid Result")
        except Exception:
            result = evaluate({"profile": {}, "accepted": {}, "report": {}, "evidence": []})  # fail closed
        result = _merge_unresolved(result, effects)
        if not effects and goal_obs is None and result["goal_verdict"] == "unknown":
            # Nothing was ever admitted, and every mutation needs an admission first: no effect is possible.
            result["goal_verdict"] = "not_reached"
            result["next_action"] = NEXT_NOT_REACHED
            result["error"] = {"code": "RUNTIME_ERROR",
                               "message": (error or {}).get("message", "등록 단계가 실행되지 않았습니다.")}
        contract.validate("Result", result)
        return self.coord_store.finalize(registration_id, result)

    # ---------- H8 (basic persisted read; S5 adds progress/result) ----------
    def get_registration(self, owner_ref: str, registration_id: str) -> dict:
        return self._view(self._load(owner_ref, registration_id))

    # ---------- helpers ----------
    def _load(self, owner_ref: str, registration_id: str) -> dict:
        with self.store.connect() as conn:
            reg = repo.get_registration(conn, owner_ref, registration_id)
        if reg is None:
            raise AppError("NOT_FOUND", "registration not found")
        return reg

    @staticmethod
    def _check_prestart(reg: dict, expected_revision: int) -> None:
        if reg["job_state"] is not None:
            raise AppError("INVALID_PHASE", "registration already started", current_revision=reg["revision"])
        if expected_revision != reg["revision"]:
            raise AppError("STALE_REVISION", "registration changed", current_revision=reg["revision"])

    def _prepare(self, source: dict, profile: dict, answers: list[dict]) -> dict:
        """Call I2 outside any transaction. Port failure -> persisted model_unavailable issue."""
        if self.prep is None:
            return _blocked_preparation("model_unavailable", "준비 모듈이 연결되지 않았습니다.")
        inp = {"source": source, "profile": profile, "answers": answers}
        contract.validate("PrepareInput", inp)
        try:
            out = self.prep.prepare(json.loads(json.dumps(inp)))
        except (AppError, PortFailure) as exc:
            err = _port_error(exc, allowed=("MODEL_UNAVAILABLE", "VALIDATION_FAILED", "PROFILE_CHANGED"))
            if err.code == "MODEL_UNAVAILABLE":
                # contract H4: model unavailable is a persisted ready=false issue, not a rejection
                return _blocked_preparation("model_unavailable", "준비 모델을 사용할 수 없습니다. 다시 시도하세요.")
            raise err from None
        except Exception:
            return _blocked_preparation("model_unavailable", "준비 모듈 응답을 받지 못했습니다. 다시 시도하세요.")
        if not contract.is_valid("Preparation", out):
            raise AppError("RUNTIME_ERROR", "preparation module returned an invalid result")
        out = json.loads(json.dumps(out))
        out["ready"] = bool(out["ready"]) and not any(i["blocking"] for i in out["issues"])
        if out["ready"] and not contract.profile_values_valid(profile["value_contract_ref"], out["values"]):
            raise AppError("RUNTIME_ERROR", "preparation marked ready with values outside the profile schema")
        return out

    def _normalize(self, reg: dict, profile: dict, answers: list[dict], corrections: list[dict]) -> list[dict]:
        """Server-side mapping: current issue -> field; correction pointer -> profile field."""
        issues = {i["issue_id"]: i for i in reg["preparation"]["issues"]}
        field_keys = {f["key"] for f in profile["fields"]}
        out: list[dict] = []
        seen: set[str] = set()
        for a in answers:
            issue = issues.get(a["issue_id"])
            if issue is None:
                raise AppError("VALIDATION_FAILED", f"issue {a['issue_id']} is not current",
                               current_revision=reg["revision"])
            out.append({"answer_id": new_id("answer"), "field": issue["field"], "value": a["value"],
                        "origin_issue_id": issue["issue_id"]})
        for c in corrections:
            pointer = c["field"]
            head = pointer[1:].split("/")[0] if pointer.startswith("/") else ""
            if head not in field_keys:
                raise AppError("VALIDATION_FAILED", f"{pointer} is not a profile field pointer")
            out.append({"answer_id": new_id("answer"), "field": pointer, "value": c["value"]})
        for item in out:
            if item["field"] in seen or any(_pointer_overlaps(item["field"], s) for s in seen):
                raise AppError("INVALID_REQUEST", f"duplicate or overlapping field {item['field']}")
            seen.add(item["field"])
        for item in out:
            contract.validate("ResolvedAnswer", item)
        return out

    def _view(self, reg: dict) -> dict:
        view = {
            "registration_id": reg["registration_id"],
            "source_id": reg["source_id"],
            "revision": reg["revision"],
            "support": reg["support"],
            "preparation": reg["preparation"],
            "auth": reg["auth"],
            "job_state": reg["job_state"],
        }
        if reg.get("profile"):
            view["profile_ref"] = reg["profile"]
        if reg.get("target"):
            view["target"] = reg["target"]["view"] if "view" in reg["target"] else reg["target"]
        if reg.get("review") and reg["job_state"] is None:
            view["review"] = reg["review"]
        if reg["job_state"] is not None:
            progress, result = self._execution_view(reg["registration_id"], reg["job_state"])
            view["progress"] = progress
            if result is not None:
                view["result"] = result
        contract.validate("RegistrationView", view)
        return view

    def _execution_view(self, registration_id: str, job_state: str) -> tuple[dict, dict | None]:
        """Progress from persisted effects/observations (advisory); result mandatory once terminal."""
        with self.store.connect() as conn:
            job = atomic.find_job(conn, registration_id)
            effects = {r["step_id"]: r["status"] for r in atomic.effects_of(conn, registration_id)}
            observed: dict[str, str] = {}
            for o in atomic.stored_observations(conn, registration_id):
                prev = observed.get(o["step_id"])
                if prev != "confirmed":
                    observed[o["step_id"]] = o["verdict"]
        accepted = json.loads(job["accepted_scope_json"])
        profile = self.knowledge.get_profile(accepted["scope"]["profile_ref"])
        labels = {s["step_id"]: s["label"] for s in profile["steps"]}
        steps = []
        for step_id in accepted["scope"]["procedure_ids"]:
            status = effects.get(step_id) or observed.get(step_id) or "pending"
            if status == "reserved":
                status = "unknown" if job_state in ("stopping", "stopped") else "pending"
            steps.append({"step_id": step_id, "label": labels[step_id], "status": status})
        index = 0
        while index < len(steps) and steps[index]["status"] == "confirmed":
            index += 1
        progress = {"step_index": index, "step_count": len(steps),
                    "confirmed_steps": [s for s in steps if s["status"] == "confirmed"]}
        if index < len(steps):
            current = dict(steps[index])
            if job_state in ("stopping", "stopped") and current["status"] == "pending":
                current["status"] = "error"
            progress["current_step"] = current
        result = json.loads(job["result_json"]) if job["result_json"] else None
        if job_state in ("done", "stopped") and result is None:
            raise AppError("RUNTIME_ERROR", "terminal job without a persisted result")
        return progress, result

    # ---------- H9 ----------
    def list_registrations(self, owner_ref: str, query: dict | None = None) -> dict:
        query = query or {}
        contract.validate("ListQuery", query)
        limit = query.get("limit", DEFAULT_LIMIT)
        after = self._decode_cursor(owner_ref, "registrations", query["cursor"]) if "cursor" in query else None
        with self.store.connect() as conn:
            rows = repo.list_registrations(conn, owner_ref, after, limit + 1)
        items = []
        for r in rows[:limit]:
            item = {"registration_id": r["registration_id"], "source_id": r["source_id"], "job_state": r["job_state"]}
            if r["profile_json"]:
                item["profile_ref"] = json.loads(r["profile_json"])
            if r["result_json"]:
                item["goal_verdict"] = json.loads(r["result_json"])["goal_verdict"]
            items.append(item)
        out: dict = {"items": items}
        if len(rows) > limit:
            last = rows[limit - 1]
            out["next_cursor"] = self._encode_cursor(owner_ref, "registrations",
                                                     [last["created_at"], last["registration_id"]])
        contract.validate("RegistrationList", out)
        return out

    # ---------- cursor ----------
    def _sign(self, owner_ref: str, kind: str, body: str) -> str:
        msg = f"{owner_ref}\0{kind}\0{body}".encode()
        return hmac.new(self._cursor_key, msg, hashlib.sha256).hexdigest()[:32]

    def _encode_cursor(self, owner_ref: str, kind: str, position: list) -> str:
        body = base64.urlsafe_b64encode(json.dumps(position, separators=(",", ":")).encode()).decode().rstrip("=")
        return f"{body}.{self._sign(owner_ref, kind, body)}"

    def _decode_cursor(self, owner_ref: str, kind: str, cursor: str) -> tuple:
        body, _, sig = cursor.partition(".")
        if not sig or not hmac.compare_digest(sig, self._sign(owner_ref, kind, body)):
            raise AppError("INVALID_REQUEST", "invalid cursor")
        try:
            position = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        except (ValueError, json.JSONDecodeError):
            raise AppError("INVALID_REQUEST", "invalid cursor") from None
        if not (isinstance(position, list) and len(position) == 2 and all(isinstance(p, str) for p in position)):
            raise AppError("INVALID_REQUEST", "invalid cursor")
        return tuple(position)


def _blocked_preparation(code: str, message: str) -> dict:
    return {
        "ready": False,
        "values": {},
        "facts": [],
        "issues": [{"issue_id": f"{code}-1", "field": "/", "code": code, "message": message, "blocking": True}],
        "provenance": [],
    }


def _pointer_overlaps(a: str, b: str) -> bool:
    return a.startswith(b.rstrip("/") + "/") or b.startswith(a.rstrip("/") + "/")


def _merge_answers(existing: list[dict], incoming: list[dict]) -> list[dict]:
    """Latest answer per field wins; answers nested under a replaced field are dropped."""
    fields = [i["field"] for i in incoming]
    kept = [
        e for e in existing
        if e["field"] not in fields and not any(_pointer_overlaps(e["field"], f) for f in fields)
    ]
    return kept + incoming


def _merge_unresolved(result: dict, effects: list) -> dict:
    """CO rule: done only with no unresolved effect. STORE effects not proven become unknown in the result."""
    result = json.loads(json.dumps(result))
    listed = {e["operation_id"]: e for e in result["effects"]}
    unresolved = False
    for row in effects:
        status = row["status"]
        verdict = "unknown" if status in ("reserved", "unknown") else status
        if verdict == "unknown":
            unresolved = True
        if row["operation_id"] in listed:
            listed[row["operation_id"]]["verdict"] = verdict
        else:
            result["effects"].append({"step_id": row["step_id"], "operation_id": row["operation_id"],
                                      "verdict": verdict, "evidence_refs": []})
    if unresolved:
        if result["goal_verdict"] == "confirmed":
            result["goal_verdict"] = "unknown"
        if result["goal_verdict"] == "unknown":
            result["next_action"] = NEXT_UNKNOWN
            if "error" not in result or result["error"]["code"] not in ("EFFECT_UNKNOWN",):
                result["error"] = {"code": "EFFECT_UNKNOWN", "message": "효과 여부를 확인할 수 없는 단계가 있습니다."}
    return result


def _port_error(exc: Exception, *, allowed: tuple[str, ...]) -> AppError:
    """Map a provider failure (contracts PortFailure or AppError) to a safe typed AppError.

    Only codes the calling route may surface are kept; anything else becomes RUNTIME_ERROR.
    """
    if isinstance(exc, PortFailure):
        err = exc.error if isinstance(exc.error, dict) and contract.is_valid("Error", exc.error) else None
        code, message = (err["code"], err["message"]) if err else ("RUNTIME_ERROR", "provider failed")
    else:
        code, message = exc.code, exc.message
    if code not in allowed:
        return AppError("RUNTIME_ERROR", message)
    return AppError(code, message)


def _build_scope(reg: dict, profile: dict, assets: list[dict]) -> dict:
    """The exact internal Scope a review approves and H7 accepts (Scope $def)."""
    prep = reg["preparation"]
    return {
        "registration_id": reg["registration_id"],
        "source_id": reg["source_id"],
        "revision": reg["revision"],
        "profile_ref": profile["ref"],
        "values": prep["values"],
        "facts": prep["facts"],
        "provenance": prep["provenance"],
        "assets": assets,
        "target": reg["target"]["trusted"]["identity"],
        "connection": reg["connection"],
        "procedure_ids": [s["step_id"] for s in profile["steps"]],
        "goal_kind": profile["goal"]["kind"],
    }
