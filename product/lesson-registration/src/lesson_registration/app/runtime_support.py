"""R03-owned internal providers for explicit R05 composition (mock only)."""
import json

from .errors import AppError
from .ids import digest, bytes_digest
from .store import repo, atomic


class RuntimeSupport:
    def __init__(self, store, knowledge):
        self.store, self.knowledge = store, knowledge

    def slot_resolver(self, registration_id, owner_ref, profile_id):
        with self.store.connect() as conn:
            reg = repo.get_registration(conn, owner_ref, registration_id)
            if reg is None:
                raise AppError("NOT_FOUND", "registration not found")
            profile = self.knowledge.get_profile(reg["profile"])
            if profile_id != profile["value_contract_ref"]:
                raise AppError("PROFILE_CHANGED", "profile does not match registration")
            source_id, seen = reg["source_id"], set()
            while True:
                if source_id in seen:
                    raise AppError("RUNTIME_ERROR", "invalid source lineage")
                seen.add(source_id)
                source = repo.get_source(conn, owner_ref, source_id)
                if source is None:
                    raise AppError("NOT_FOUND", "source not found")
                previous = source.get("previous_source_id")
                if not previous:
                    break
                source_id = previous
        return "slot-" + digest({"kind": "source-slot.v1", "owner": owner_ref,
                                 "root_source_id": source_id,
                                 "platform": profile["ref"]["platform"],
                                 "object_kind": profile["ref"]["object_kind"]})

    def read_approved_asset(self, context, asset_id):
        # One read snapshot binds job, owner, immutable approval and asset bytes.
        with self.store.connect() as conn:
            conn.execute("BEGIN")
            job = atomic.find_job(conn, context.registration_id)
            if job is None:
                raise AppError("NOT_FOUND", "accepted job not found")
            if job["state"] != "active" or not job["worker_lease"] or job["worker_lease"] != context.lease:
                raise AppError("PERMISSION_DENIED", "inactive or foreign worker")
            reg = repo.get_registration(conn, job["owner_ref"], context.registration_id)
            if reg is None:
                raise AppError("NOT_FOUND", "registration not found")
            scope = json.loads(job["accepted_scope_json"])["scope"]
            asset = next((a for a in scope["assets"] if a["asset_id"] == asset_id), None)
            if asset is None or not asset["rights_confirmed"]:
                raise AppError("PERMISSION_DENIED", "asset is not approved")
            raw = repo.get_asset_blob(conn, job["owner_ref"], asset_id)
            if raw is None or len(raw) != asset["bytes"] or bytes_digest(raw) != asset["digest"]:
                raise AppError("RUNTIME_ERROR", "approved asset integrity mismatch")
            return raw
