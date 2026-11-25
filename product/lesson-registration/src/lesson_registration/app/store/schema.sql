-- r03-app STORE schema (SQLite). Sources/assets are immutable: no UPDATE/DELETE paths exist.
CREATE TABLE IF NOT EXISTS dispatch_permits (
    token TEXT PRIMARY KEY,
    registration_id TEXT NOT NULL,
    lease TEXT NOT NULL,
    operation_json TEXT NOT NULL,
    consumed INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sources (
    source_id          TEXT PRIMARY KEY,
    owner_ref          TEXT NOT NULL,
    previous_source_id TEXT REFERENCES sources(source_id),
    raw_text           TEXT NOT NULL,
    created_at         TEXT NOT NULL,
    seq                INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS sources_owner_order ON sources(owner_ref, created_at DESC, source_id DESC);

CREATE TABLE IF NOT EXISTS assets (
    asset_id         TEXT PRIMARY KEY,
    owner_ref        TEXT NOT NULL,
    digest           TEXT NOT NULL,
    mime             TEXT NOT NULL,
    bytes            INTEGER NOT NULL,
    width            INTEGER NOT NULL,
    height           INTEGER NOT NULL,
    rights_confirmed INTEGER NOT NULL,
    blob             BLOB NOT NULL,
    created_at       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS source_assets (
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    asset_id  TEXT NOT NULL REFERENCES assets(asset_id),
    ord       INTEGER NOT NULL,
    PRIMARY KEY (source_id, asset_id)
);

CREATE TABLE IF NOT EXISTS registrations (
    registration_id  TEXT PRIMARY KEY,
    owner_ref        TEXT NOT NULL,
    source_id        TEXT NOT NULL REFERENCES sources(source_id),
    selector         TEXT NOT NULL,
    support          TEXT NOT NULL,
    profile_json     TEXT,
    preparation_json TEXT NOT NULL,
    answers_json     TEXT NOT NULL,
    revision         INTEGER NOT NULL,
    auth_json        TEXT NOT NULL,
    target_json      TEXT,
    connection_json  TEXT,
    review_json      TEXT,
    job_state        TEXT,
    created_at       TEXT NOT NULL,
    updated_at       TEXT NOT NULL,
    seq              INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
    registration_id     TEXT PRIMARY KEY REFERENCES registrations(registration_id),
    owner_ref           TEXT NOT NULL,
    request_key         TEXT NOT NULL,
    request_digest      TEXT NOT NULL,
    accepted_scope_json TEXT NOT NULL,
    state               TEXT NOT NULL,
    result_json         TEXT,
    worker_lease        TEXT,
    accepted_at         TEXT NOT NULL,
    updated_at          TEXT NOT NULL,
    UNIQUE (owner_ref, request_key)
);

CREATE TABLE IF NOT EXISTS effects (
    effect_key      TEXT PRIMARY KEY,
    registration_id TEXT NOT NULL REFERENCES registrations(registration_id),
    operation_id    TEXT NOT NULL,
    step_id         TEXT NOT NULL,
    action_key      TEXT NOT NULL,
    effect_class    TEXT NOT NULL,
    binding_digest  TEXT NOT NULL,
    status          TEXT NOT NULL,
    admitted_at     TEXT NOT NULL,
    resolved_at     TEXT
);

CREATE TABLE IF NOT EXISTS observations (
    observation_id     TEXT PRIMARY KEY,
    registration_id    TEXT NOT NULL REFERENCES registrations(registration_id),
    operation_id       TEXT NOT NULL,
    verdict            TEXT NOT NULL,
    method             TEXT NOT NULL,
    evidence_refs_json TEXT NOT NULL,
    observed_at        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evidence (
    evidence_id     TEXT PRIMARY KEY,
    registration_id TEXT NOT NULL REFERENCES registrations(registration_id),
    record_json     TEXT NOT NULL,
    observed_at     TEXT NOT NULL
);
