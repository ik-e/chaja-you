"""Row-level reads/writes for sources, assets and registrations. Callers own the transaction."""

from __future__ import annotations

import json
import sqlite3

from .db import next_seq


def insert_asset(conn: sqlite3.Connection, owner_ref: str, asset: dict, blob: bytes, created_at: str) -> None:
    conn.execute(
        "INSERT INTO assets(asset_id, owner_ref, digest, mime, bytes, width, height, rights_confirmed, blob, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            asset["asset_id"], owner_ref, asset["digest"], asset["mime"], asset["bytes"],
            asset["width"], asset["height"], int(asset["rights_confirmed"]), blob, created_at,
        ),
    )


def owned_asset_refs(conn: sqlite3.Connection, owner_ref: str, asset_ids: list[str]) -> dict[str, dict]:
    if not asset_ids:
        return {}
    marks = ",".join("?" * len(asset_ids))
    rows = conn.execute(
        f"SELECT * FROM assets WHERE owner_ref=? AND asset_id IN ({marks})", (owner_ref, *asset_ids)
    ).fetchall()
    return {r["asset_id"]: _asset_ref(r) for r in rows}


def source_exists(conn: sqlite3.Connection, owner_ref: str, source_id: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sources WHERE owner_ref=? AND source_id=?", (owner_ref, source_id)
    ).fetchone()
    return row is not None


def insert_source(
    conn: sqlite3.Connection,
    owner_ref: str,
    source_id: str,
    previous_source_id: str | None,
    raw_text: str,
    asset_ids: list[str],
    created_at: str,
) -> None:
    conn.execute(
        "INSERT INTO sources(source_id, owner_ref, previous_source_id, raw_text, created_at, seq) VALUES (?,?,?,?,?,?)",
        (source_id, owner_ref, previous_source_id, raw_text, created_at, next_seq(conn, "sources")),
    )
    conn.executemany(
        "INSERT INTO source_assets(source_id, asset_id, ord) VALUES (?,?,?)",
        [(source_id, a, i) for i, a in enumerate(asset_ids)],
    )


def get_source(conn: sqlite3.Connection, owner_ref: str, source_id: str) -> dict | None:
    row = conn.execute(
        "SELECT * FROM sources WHERE owner_ref=? AND source_id=?", (owner_ref, source_id)
    ).fetchone()
    if row is None:
        return None
    assets = conn.execute(
        "SELECT a.* FROM source_assets sa JOIN assets a ON a.asset_id = sa.asset_id"
        " WHERE sa.source_id=? ORDER BY sa.ord",
        (source_id,),
    ).fetchall()
    view = {
        "source_id": row["source_id"],
        "raw_text": row["raw_text"],
        "asset_refs": [_asset_ref(a) for a in assets],
        "created_at": row["created_at"],
    }
    if row["previous_source_id"]:
        view["previous_source_id"] = row["previous_source_id"]
    return view


def list_sources(
    conn: sqlite3.Connection, owner_ref: str, after: tuple[str, str] | None, limit: int
) -> list[sqlite3.Row]:
    """Contract H2 order: created_at DESC, then source_id DESC. ``after`` is the last (created_at, source_id) seen."""
    if after is None:
        return conn.execute(
            "SELECT source_id, raw_text, created_at FROM sources WHERE owner_ref=?"
            " ORDER BY created_at DESC, source_id DESC LIMIT ?",
            (owner_ref, limit),
        ).fetchall()
    created_at, source_id = after
    return conn.execute(
        "SELECT source_id, raw_text, created_at FROM sources WHERE owner_ref=?"
        " AND (created_at < ? OR (created_at = ? AND source_id < ?))"
        " ORDER BY created_at DESC, source_id DESC LIMIT ?",
        (owner_ref, created_at, created_at, source_id, limit),
    ).fetchall()


def get_asset_blob(conn: sqlite3.Connection, owner_ref: str, asset_id: str) -> bytes | None:
    row = conn.execute(
        "SELECT blob FROM assets WHERE owner_ref=? AND asset_id=?", (owner_ref, asset_id)
    ).fetchone()
    return None if row is None else bytes(row["blob"])


def _asset_ref(r: sqlite3.Row) -> dict:
    return {
        "asset_id": r["asset_id"],
        "digest": r["digest"],
        "mime": r["mime"],
        "bytes": r["bytes"],
        "width": r["width"],
        "height": r["height"],
        "rights_confirmed": bool(r["rights_confirmed"]),
    }


# ---------- registrations ----------
_REG_JSON = ("profile", "preparation", "answers", "auth", "target", "connection", "review")


def insert_registration(conn: sqlite3.Connection, owner_ref: str, reg: dict, now: str) -> None:
    conn.execute(
        "INSERT INTO registrations(registration_id, owner_ref, source_id, selector, support, profile_json,"
        " preparation_json, answers_json, revision, auth_json, target_json, connection_json, review_json,"
        " job_state, created_at, updated_at, seq) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            reg["registration_id"], owner_ref, reg["source_id"], reg["selector"], reg["support"],
            _dump(reg.get("profile")), _dump(reg["preparation"]), _dump(reg["answers"]), reg["revision"],
            _dump(reg["auth"]), _dump(reg.get("target")), _dump(reg.get("connection")),
            _dump(reg.get("review")), reg.get("job_state"), now, now, next_seq(conn, "registrations"),
        ),
    )


def get_registration(conn: sqlite3.Connection, owner_ref: str, registration_id: str) -> dict | None:
    row = conn.execute(
        "SELECT * FROM registrations WHERE owner_ref=? AND registration_id=?", (owner_ref, registration_id)
    ).fetchone()
    return None if row is None else _reg(row)


def update_registration_if(
    conn: sqlite3.Connection, owner_ref: str, reg: dict, expected_revision: int, now: str
) -> bool:
    """Compare-and-set on (revision, job_state IS NULL). Returns False if another writer won."""
    cur = conn.execute(
        "UPDATE registrations SET source_id=?, selector=?, support=?, profile_json=?, preparation_json=?,"
        " answers_json=?, revision=?, auth_json=?, target_json=?, connection_json=?, review_json=?, updated_at=?"
        " WHERE owner_ref=? AND registration_id=? AND revision=? AND job_state IS NULL",
        (
            reg["source_id"], reg["selector"], reg["support"], _dump(reg.get("profile")),
            _dump(reg["preparation"]), _dump(reg["answers"]), reg["revision"], _dump(reg["auth"]),
            _dump(reg.get("target")), _dump(reg.get("connection")), _dump(reg.get("review")), now,
            owner_ref, reg["registration_id"], expected_revision,
        ),
    )
    return cur.rowcount == 1


def _dump(value) -> str | None:
    return None if value is None else json.dumps(value, ensure_ascii=False, sort_keys=True)


def _reg(row: sqlite3.Row) -> dict:
    out = {
        "registration_id": row["registration_id"],
        "owner_ref": row["owner_ref"],
        "source_id": row["source_id"],
        "selector": row["selector"],
        "support": row["support"],
        "revision": row["revision"],
        "job_state": row["job_state"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }
    for key in _REG_JSON:
        raw = row[f"{key}_json"]
        out[key] = None if raw is None else json.loads(raw)
    return out


def list_registrations(
    conn: sqlite3.Connection, owner_ref: str, after: tuple[str, str] | None, limit: int
) -> list[sqlite3.Row]:
    """H9 order: creation DESC, then registration_id DESC (same convention as H2)."""
    base = (
        "SELECT r.registration_id, r.source_id, r.profile_json, r.job_state, r.created_at, j.result_json"
        " FROM registrations r LEFT JOIN jobs j ON j.registration_id = r.registration_id WHERE r.owner_ref=?"
    )
    if after is None:
        return conn.execute(base + " ORDER BY r.created_at DESC, r.registration_id DESC LIMIT ?",
                            (owner_ref, limit)).fetchall()
    created_at, rid = after
    return conn.execute(
        base + " AND (r.created_at < ? OR (r.created_at = ? AND r.registration_id < ?))"
        " ORDER BY r.created_at DESC, r.registration_id DESC LIMIT ?",
        (owner_ref, created_at, created_at, rid, limit),
    ).fetchall()
