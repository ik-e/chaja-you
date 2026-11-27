-- TASK-058 V5.3 candidate: disposable synthetic PostgreSQL only.
-- No application roles or product migration. Do not run against existing data.
CREATE SCHEMA chajayou_v53_mock;
SET search_path TO chajayou_v53_mock, pg_catalog;
REVOKE ALL ON SCHEMA chajayou_v53_mock FROM PUBLIC;

CREATE TABLE users (
  id uuid PRIMARY KEY,
  issuer text NOT NULL,
  subject text NOT NULL,
  state text NOT NULL,
  retired_at timestamptz,
  UNIQUE (issuer, subject),
  CHECK (length(btrim(issuer)) > 0),
  CHECK (length(btrim(subject)) > 0),
  CHECK (state IN ('active','restricted','retired')),
  CHECK ((state = 'retired') = (retired_at IS NOT NULL))
);

CREATE TABLE sources (
  id uuid PRIMARY KEY,
  owner_id uuid NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  content jsonb,
  revision integer NOT NULL,
  draft jsonb,
  state text NOT NULL,
  updated_at timestamptz NOT NULL,
  UNIQUE (owner_id, id),
  CHECK (revision >= 0),
  CHECK (state IN ('draft_only','managed','retired')),
  CHECK (state <> 'managed' OR content IS NOT NULL),
  CHECK (state <> 'draft_only' OR content IS NULL),
  CHECK (content IS NULL OR jsonb_typeof(content) = 'object'),
  CHECK (draft IS NULL OR jsonb_typeof(draft) = 'object')
);

CREATE TABLE assets (
  id uuid PRIMARY KEY,
  source_id uuid NOT NULL REFERENCES sources(id) ON DELETE RESTRICT,
  storage_key text NOT NULL,
  digest text NOT NULL,
  media_type text NOT NULL,
  size_bytes bigint NOT NULL,
  rights_state text NOT NULL,
  rights_detail jsonb NOT NULL,
  created_at timestamptz NOT NULL,
  CHECK (size_bytes >= 0),
  CHECK (length(btrim(storage_key)) > 0),
  CHECK (length(btrim(digest)) > 0),
  CHECK (rights_state IN ('allowed','unknown','revoked')),
  CHECK (rights_detail IS NULL OR jsonb_typeof(rights_detail) = 'object')
);

CREATE TABLE platform_accounts (
  id uuid PRIMARY KEY,
  owner_id uuid NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  platform_key text NOT NULL,
  environment text NOT NULL,
  identity_namespace text NOT NULL,
  native_account_key text NOT NULL,
  management_state text NOT NULL,
  UNIQUE (owner_id, environment, platform_key, identity_namespace, native_account_key),
  UNIQUE (owner_id, environment, platform_key, id),
  CHECK (environment = 'mock'),
  CHECK (management_state IN ('unlinked','linked','retired')),
  CHECK (length(btrim(platform_key)) > 0),
  CHECK (length(btrim(identity_namespace)) > 0),
  CHECK (length(btrim(native_account_key)) > 0)
);

CREATE TABLE platform_objects (
  id uuid PRIMARY KEY,
  account_id uuid NOT NULL REFERENCES platform_accounts(id) ON DELETE RESTRICT,
  parent_id uuid REFERENCES platform_objects(id) ON DELETE RESTRICT,
  kind text NOT NULL,
  identity_namespace text NOT NULL,
  native_object_key text NOT NULL,
  locator jsonb,
  source_id uuid REFERENCES sources(id) ON DELETE RESTRICT,
  UNIQUE (account_id, kind, identity_namespace, native_object_key),
  UNIQUE (account_id, id),
  FOREIGN KEY (account_id, parent_id) REFERENCES platform_objects(account_id, id) ON DELETE RESTRICT,
  CHECK (parent_id IS NULL OR parent_id <> id),
  CHECK (kind <> 'profile' OR source_id IS NULL),
  CHECK (length(btrim(native_object_key)) > 0),
  CHECK (length(btrim(identity_namespace)) > 0),
  CHECK (locator IS NULL OR jsonb_typeof(locator) = 'object')
);

CREATE TABLE work_requests (
  id uuid PRIMARY KEY,
  owner_id uuid NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  source_id uuid REFERENCES sources(id) ON DELETE RESTRICT,
  source_revision integer,
  environment text NOT NULL,
  selection_revision integer NOT NULL,
  approval_state text NOT NULL,
  approval jsonb,
  created_at timestamptz NOT NULL,
  accepted_at timestamptz,
  UNIQUE (owner_id, id),
  FOREIGN KEY (owner_id, source_id) REFERENCES sources(owner_id, id) ON DELETE RESTRICT,
  CHECK (environment = 'mock'),
  CHECK (selection_revision >= 0),
  CHECK (source_revision IS NULL OR source_revision >= 0),
  CHECK ((source_id IS NULL) = (source_revision IS NULL)),
  CHECK (approval_state IN ('none','presented','invalidated','frozen')),
  CHECK ((approval_state = 'frozen') = (accepted_at IS NOT NULL)),
  CHECK (approval_state <> 'frozen' OR approval IS NOT NULL),
  CHECK (accepted_at IS NULL OR accepted_at >= created_at),
  CHECK (approval IS NULL OR jsonb_typeof(approval) = 'object')
);

CREATE TABLE work_targets (
  id uuid PRIMARY KEY,
  request_id uuid NOT NULL REFERENCES work_requests(id) ON DELETE RESTRICT,
  platform_key text NOT NULL,
  operation_key text NOT NULL,
  account_id uuid REFERENCES platform_accounts(id) ON DELETE RESTRICT,
  object_id uuid REFERENCES platform_objects(id) ON DELETE RESTRICT,
  prior_target_id uuid REFERENCES work_targets(id) ON DELETE RESTRICT,
  prepared_source_revision integer,
  prep_generation integer NOT NULL,
  prep_state text NOT NULL,
  profile_ref text,
  plan jsonb NOT NULL,
  lifecycle text NOT NULL,
  ended_at timestamptz,
  CHECK (prep_generation >= 0),
  CHECK (prepared_source_revision IS NULL OR prepared_source_revision >= 0),
  CHECK (prior_target_id IS NULL OR prior_target_id <> id),
  CHECK (prep_state IN ('unprepared','preparing','issues','ready','held','excluded','stale','consumed')),
  CHECK (lifecycle IN ('not_accepted','accepted','running','fencing','ended')),
  CHECK ((lifecycle = 'ended') = (ended_at IS NOT NULL)),
  CHECK (prep_state <> 'consumed' OR lifecycle <> 'not_accepted'),
  CHECK (operation_key NOT IN ('CREATE','UPDATE','RENEW','FIRST_OPEN_SCHEDULE','REPRESENTATIVE_SERVICE') OR ((lifecycle <> 'not_accepted') = (prep_state = 'consumed'))),
  CHECK (plan IS NULL OR jsonb_typeof(plan) = 'object')
);

CREATE TABLE commands (
  id uuid PRIMARY KEY,
  owner_id uuid NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  kind text NOT NULL,
  request_key text NOT NULL,
  request_digest text NOT NULL,
  state text NOT NULL,
  receipt jsonb,
  created_at timestamptz NOT NULL,
  resolved_at timestamptz,
  source_id uuid REFERENCES sources(id) ON DELETE RESTRICT,
  work_request_id uuid REFERENCES work_requests(id) ON DELETE RESTRICT,
  scope jsonb NOT NULL,
  UNIQUE (owner_id, kind, request_key),
  UNIQUE (owner_id, id),
  FOREIGN KEY (owner_id, source_id) REFERENCES sources(owner_id, id) ON DELETE RESTRICT,
  FOREIGN KEY (owner_id, work_request_id) REFERENCES work_requests(owner_id, id) ON DELETE RESTRICT,
  CHECK (state IN ('reserved','committed','rejected','no_commit_proven')),
  CHECK (length(btrim(request_key)) > 0),
  CHECK (length(btrim(request_digest)) > 0),
  CHECK ((state = 'reserved') = (resolved_at IS NULL)),
  CHECK ((state = 'reserved') = (receipt IS NULL)),
  CHECK (resolved_at IS NULL OR resolved_at >= created_at),
  CHECK (kind <> 'SAVE_SOURCE' OR source_id IS NOT NULL),
  CHECK (receipt IS NULL OR jsonb_typeof(receipt) = 'object'),
  CHECK (scope IS NULL OR jsonb_typeof(scope) = 'object')
);

CREATE TABLE access_contexts (
  id uuid PRIMARY KEY,
  owner_id uuid NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  target_id uuid REFERENCES work_targets(id) ON DELETE RESTRICT,
  platform_key text NOT NULL,
  expected_account_id uuid REFERENCES platform_accounts(id) ON DELETE RESTRICT,
  verified_account_id uuid REFERENCES platform_accounts(id) ON DELETE RESTRICT,
  purpose text NOT NULL,
  state text NOT NULL,
  scope jsonb NOT NULL,
  expires_at timestamptz NOT NULL,
  blocked_at timestamptz,
  cleanup jsonb NOT NULL,
  context_key text NOT NULL,
  generation integer NOT NULL,
  environment text NOT NULL,
  UNIQUE (owner_id, context_key, generation),
  FOREIGN KEY (owner_id, environment, platform_key, expected_account_id) REFERENCES platform_accounts(owner_id, environment, platform_key, id) ON DELETE RESTRICT,
  FOREIGN KEY (owner_id, environment, platform_key, verified_account_id) REFERENCES platform_accounts(owner_id, environment, platform_key, id) ON DELETE RESTRICT,
  CHECK (environment = 'mock'),
  CHECK (generation >= 0),
  CHECK (state IN ('human','verifying','verified','blocked')),
  CHECK ((state = 'blocked') = (blocked_at IS NOT NULL)),
  CHECK (state <> 'verified' OR (verified_account_id IS NOT NULL AND (expected_account_id IS NULL OR expected_account_id = verified_account_id))),
  CHECK (scope IS NULL OR jsonb_typeof(scope) = 'object'),
  CHECK (cleanup IS NULL OR jsonb_typeof(cleanup) = 'object')
);

CREATE TABLE attempts (
  id uuid PRIMARY KEY,
  target_id uuid REFERENCES work_targets(id) ON DELETE RESTRICT,
  access_id uuid NOT NULL REFERENCES access_contexts(id) ON DELETE RESTRICT,
  object_id uuid REFERENCES platform_objects(id) ON DELETE RESTRICT,
  kind text NOT NULL,
  purpose_key text NOT NULL,
  scope jsonb NOT NULL,
  sequence_no bigint,
  state text NOT NULL,
  requested_at timestamptz NOT NULL,
  started_at timestamptz,
  finished_at timestamptz,
  failure_reason text,
  CHECK (kind IN ('read','write')),
  CHECK ((kind = 'read' AND state IN ('pending','running','observed','unavailable') AND sequence_no IS NOT NULL) OR (kind = 'write' AND state IN ('reserved','started','sealed') AND target_id IS NOT NULL)),
  CHECK (sequence_no IS NULL OR sequence_no >= 0),
  CHECK (started_at IS NULL OR started_at >= requested_at),
  CHECK (finished_at IS NULL OR finished_at >= requested_at),
  CHECK (started_at IS NULL OR finished_at IS NULL OR finished_at >= started_at),
  CHECK ((state IN ('sealed','observed','unavailable')) = (finished_at IS NOT NULL)),
  CHECK (state NOT IN ('started','running','observed') OR started_at IS NOT NULL),
  CHECK (state NOT IN ('reserved','pending') OR started_at IS NULL),
  CHECK (scope IS NULL OR jsonb_typeof(scope) = 'object')
);

CREATE TABLE effects (
  id uuid PRIMARY KEY,
  target_id uuid NOT NULL REFERENCES work_targets(id) ON DELETE RESTRICT,
  attempt_id uuid REFERENCES attempts(id) ON DELETE RESTRICT,
  prior_effect_id uuid REFERENCES effects(id) ON DELETE RESTRICT,
  rule_key text NOT NULL,
  logical_effect_key text NOT NULL,
  intent_digest text NOT NULL,
  root_key text NOT NULL,
  scope_path text NOT NULL,
  object_id uuid REFERENCES platform_objects(id) ON DELETE RESTRICT,
  required boolean NOT NULL,
  state text NOT NULL,
  disputed boolean NOT NULL,
  updated_at timestamptz NOT NULL,
  claims jsonb NOT NULL,
  UNIQUE (target_id, logical_effect_key),
  CHECK (state IN ('not_attempted','reserved','in_flight','confirmed','none_confirmed','unknown')),
  CHECK (prior_effect_id IS NULL OR prior_effect_id <> id),
  CHECK ((state = 'not_attempted') = (attempt_id IS NULL)),
  CHECK (claims IS NULL OR jsonb_typeof(claims) = 'array')
);

CREATE TABLE history (
  id uuid PRIMARY KEY,
  owner_id uuid NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  kind text NOT NULL,
  target_id uuid REFERENCES work_targets(id) ON DELETE RESTRICT,
  attempt_id uuid REFERENCES attempts(id) ON DELETE RESTRICT,
  effect_id uuid REFERENCES effects(id) ON DELETE RESTRICT,
  object_id uuid REFERENCES platform_objects(id) ON DELETE RESTRICT,
  access_id uuid REFERENCES access_contexts(id) ON DELETE RESTRICT,
  command_id uuid REFERENCES commands(id) ON DELETE RESTRICT,
  version_no integer,
  observed_at timestamptz,
  recorded_at timestamptz NOT NULL,
  payload jsonb NOT NULL,
  proof_ids uuid[] NOT NULL,
  source_id uuid REFERENCES sources(id) ON DELETE RESTRICT,
  account_id uuid REFERENCES platform_accounts(id) ON DELETE RESTRICT,
  related_object_id uuid REFERENCES platform_objects(id) ON DELETE RESTRICT,
  FOREIGN KEY (owner_id, source_id) REFERENCES sources(owner_id, id) ON DELETE RESTRICT,
  FOREIGN KEY (owner_id, command_id) REFERENCES commands(owner_id, id) ON DELETE RESTRICT,
  CHECK (version_no IS NULL OR version_no >= 0),
  CHECK (array_position(proof_ids, NULL::uuid) IS NULL),
  CHECK (NOT (id = ANY(proof_ids))),
  CHECK (related_object_id IS NULL OR (object_id IS NOT NULL AND related_object_id <> object_id)),
  CHECK (payload IS NULL OR jsonb_typeof(payload) = 'object')
);

-- Proposed indexes; measure EXPLAIN before product adoption.
CREATE UNIQUE INDEX uq_platform_linked_owner ON platform_accounts (environment, platform_key, identity_namespace, native_account_key) WHERE management_state = 'linked';
CREATE UNIQUE INDEX uq_access_current_generation ON access_contexts(owner_id, context_key) WHERE state <> 'blocked';
CREATE UNIQUE INDEX uq_binding_version ON history(object_id, version_no) WHERE kind = 'management_binding';
CREATE INDEX ix_platform_canonical ON platform_accounts (environment, platform_key, identity_namespace, native_account_key);
CREATE INDEX ix_sources_owner_updated ON sources (owner_id, updated_at DESC, id);
CREATE INDEX ix_assets_source ON assets (source_id);
CREATE INDEX ix_objects_source ON platform_objects (source_id);
CREATE INDEX ix_objects_parent ON platform_objects (parent_id);
CREATE INDEX ix_requests_owner_created ON work_requests (owner_id, created_at DESC, id);
CREATE INDEX ix_requests_source ON work_requests (source_id);
CREATE INDEX ix_targets_request_lifecycle ON work_targets (request_id, lifecycle);
CREATE INDEX ix_targets_account ON work_targets (account_id);
CREATE INDEX ix_targets_object ON work_targets (object_id);
CREATE INDEX ix_targets_prior ON work_targets (prior_target_id);
CREATE INDEX ix_commands_source_pending ON commands (source_id, state) WHERE state = 'reserved';
CREATE INDEX ix_commands_request ON commands (work_request_id);
CREATE INDEX ix_access_target ON access_contexts (target_id);
CREATE INDEX ix_access_expected ON access_contexts (expected_account_id);
CREATE INDEX ix_access_verified ON access_contexts (verified_account_id);
CREATE INDEX ix_attempts_target ON attempts (target_id);
CREATE INDEX ix_attempts_access_sequence ON attempts (access_id, object_id, purpose_key, sequence_no);
CREATE INDEX ix_attempts_object ON attempts (object_id);
CREATE INDEX ix_effects_target_state ON effects (target_id, state);
CREATE INDEX ix_effects_unresolved ON effects (root_key, scope_path) WHERE state IN ('reserved','in_flight','unknown') OR disputed;
CREATE INDEX ix_effects_attempt ON effects (attempt_id);
CREATE INDEX ix_effects_object ON effects (object_id);
CREATE INDEX ix_effects_prior ON effects (prior_effect_id);
CREATE INDEX ix_history_object_kind_version ON history (object_id, kind, version_no DESC);
CREATE INDEX ix_history_account_kind_time ON history (account_id, kind, observed_at DESC, recorded_at DESC);
CREATE INDEX ix_history_source_kind_time ON history (source_id, kind, recorded_at DESC);
CREATE INDEX ix_history_target_kind_version ON history (target_id, kind, version_no DESC);
CREATE INDEX ix_history_effect_kind_version ON history (effect_id, kind, version_no DESC);
CREATE INDEX ix_history_attempt ON history (attempt_id);
CREATE INDEX ix_history_access ON history (access_id);
CREATE INDEX ix_history_command ON history (command_id);
CREATE INDEX ix_history_related_object ON history (related_object_id);
REVOKE ALL ON ALL TABLES IN SCHEMA chajayou_v53_mock FROM PUBLIC;
-- Load db-guards-v5.3.sql in the same fresh synthetic database after this file.
-- Row constraints alone do not implement the guarded store, authorization, native evidence or broker protocol.
