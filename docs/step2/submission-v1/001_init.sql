-- SUB-DESIGN-20261126-V1: provisional PostgreSQL 16 submission only.
BEGIN;
CREATE TABLE schema_migrations (version integer PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now());
-- OIDC 식별 사용자
CREATE TABLE app_users (
  user_id uuid PRIMARY KEY,
  issuer text NOT NULL,
  subject text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  deletion_requested_at timestamptz,
  UNIQUE (issuer,subject)
);

-- 서버 검증 서비스 세션(토큰 해시만)
CREATE TABLE app_sessions (
  session_hash text PRIMARY KEY,
  owner_id uuid NOT NULL REFERENCES app_users(user_id),
  csrf_hash text NOT NULL,
  expires_at timestamptz NOT NULL,
  revoked_at timestamptz,
  CHECK (length(session_hash)=64 AND length(csrf_hash)=64)
);

-- 7개 조사 플랫폼 레지스트리
CREATE TABLE platforms (
  platform_id text PRIMARY KEY,
  name text NOT NULL
);

-- 플랫폼별 객체·업무·규칙 버전 및 허용 근거
CREATE TABLE platform_profiles (
  profile_id uuid PRIMARY KEY,
  platform_id text NOT NULL REFERENCES platforms(platform_id),
  object_kind text NOT NULL,
  operation text NOT NULL CHECK (operation IN ('create','update','renew','status')),
  version text NOT NULL,
  rules_digest text NOT NULL,
  rules jsonb NOT NULL,
  policy_status text NOT NULL CHECK (policy_status IN ('allowed','prohibited','unknown')),
  policy_evidence jsonb NOT NULL DEFAULT '[]',
  mock_supported boolean NOT NULL DEFAULT false,
  UNIQUE (platform_id,object_kind,operation,version),
  UNIQUE (profile_id,platform_id,object_kind,operation)
);

-- 소유자별 재사용 원본 레슨
CREATE TABLE lessons (
  lesson_id uuid PRIMARY KEY,
  owner_id uuid NOT NULL REFERENCES app_users(user_id),
  title text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  deletion_requested_at timestamptz,
  UNIQUE (owner_id,lesson_id)
);

-- 원본 버전(불변) 및 공통 사실·출처
CREATE TABLE lesson_versions (
  version_id uuid PRIMARY KEY,
  owner_id uuid NOT NULL,
  lesson_id uuid NOT NULL,
  version_no bigint NOT NULL CHECK (version_no>=1),
  raw_text text NOT NULL,
  facts jsonb NOT NULL DEFAULT '[]',
  content_digest text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (owner_id,version_id),
  UNIQUE (owner_id,lesson_id,version_id),
  UNIQUE (lesson_id,version_no),
  FOREIGN KEY (owner_id,lesson_id) REFERENCES lessons(owner_id,lesson_id)
);

-- 첨부 bytes·사용 권리·digest
CREATE TABLE assets (
  asset_id uuid PRIMARY KEY,
  owner_id uuid NOT NULL REFERENCES app_users(user_id),
  digest text NOT NULL,
  mime text NOT NULL,
  content bytea NOT NULL,
  byte_count bigint NOT NULL CHECK (byte_count>=0),
  rights_confirmed boolean NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (owner_id,asset_id),
  CHECK (byte_count=octet_length(content))
);

-- 원본 버전별 순서가 있는 첨부 연결
CREATE TABLE version_assets (
  owner_id uuid NOT NULL,
  version_id uuid NOT NULL,
  asset_id uuid NOT NULL,
  position integer NOT NULL CHECK (position>=0),
  PRIMARY KEY (version_id,asset_id),
  UNIQUE (version_id,position),
  FOREIGN KEY (owner_id,version_id) REFERENCES lesson_versions(owner_id,version_id),
  FOREIGN KEY (owner_id,asset_id) REFERENCES assets(owner_id,asset_id)
);

-- 직접 인증한 외부 계정 식별만 저장(비밀 미저장)
CREATE TABLE external_accounts (
  account_id uuid PRIMARY KEY,
  owner_id uuid NOT NULL REFERENCES app_users(user_id),
  platform_id text NOT NULL REFERENCES platforms(platform_id),
  external_ref text NOT NULL,
  label text NOT NULL,
  verified_at timestamptz NOT NULL DEFAULT now(),
  unlinked_at timestamptz,
  UNIQUE (owner_id,account_id),
  UNIQUE (owner_id,account_id,platform_id),
  UNIQUE (owner_id,platform_id,external_ref)
);

-- 확인된 외부 게시 객체; 상태는 관측에서 파생
CREATE TABLE external_objects (
  object_id uuid PRIMARY KEY,
  owner_id uuid NOT NULL,
  lesson_id uuid NOT NULL,
  account_id uuid NOT NULL,
  platform_id text NOT NULL,
  object_kind text NOT NULL,
  native_id text NOT NULL,
  public_url text,
  linked_at timestamptz NOT NULL DEFAULT now(),
  unlinked_at timestamptz,
  UNIQUE (owner_id,object_id),
  UNIQUE (owner_id,object_id,lesson_id,account_id,platform_id,object_kind),
  UNIQUE (owner_id,account_id,object_kind,native_id),
  FOREIGN KEY (owner_id,lesson_id) REFERENCES lessons(owner_id,lesson_id),
  FOREIGN KEY (owner_id,account_id,platform_id) REFERENCES external_accounts(owner_id,account_id,platform_id)
);

-- 업무 초안. 한 외부 객체에 독립적인 복수 업무 요청 가능
CREATE TABLE work_requests (
  request_id uuid PRIMARY KEY,
  owner_id uuid NOT NULL,
  lesson_id uuid NOT NULL,
  version_id uuid NOT NULL,
  profile_id uuid NOT NULL,
  platform_id text NOT NULL,
  object_kind text NOT NULL,
  operation text NOT NULL CHECK (operation IN ('create','update','renew','status')),
  account_id uuid,
  object_id uuid,
  related_job_id uuid,
  before_snapshot jsonb,
  target_slot text NOT NULL,
  revision bigint NOT NULL CHECK (revision>=1),
  draft_status text NOT NULL CHECK (draft_status IN ('blocked','ready','rejected')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (owner_id,request_id),
  FOREIGN KEY (owner_id,lesson_id,version_id) REFERENCES lesson_versions(owner_id,lesson_id,version_id),
  FOREIGN KEY (profile_id,platform_id,object_kind,operation) REFERENCES platform_profiles(profile_id,platform_id,object_kind,operation),
  FOREIGN KEY (owner_id,account_id,platform_id) REFERENCES external_accounts(owner_id,account_id,platform_id),
  FOREIGN KEY (owner_id,object_id,lesson_id,account_id,platform_id,object_kind) REFERENCES external_objects(owner_id,object_id,lesson_id,account_id,platform_id,object_kind),
  CHECK (object_id IS NULL OR account_id IS NOT NULL),
  CHECK (operation<>'create' OR object_id IS NULL),
  CHECK (related_job_id IS NULL OR operation='status')
);

-- revision별 준비 결과·질문·확인 근거
CREATE TABLE preparation_versions (
  owner_id uuid NOT NULL,
  request_id uuid NOT NULL,
  revision bigint NOT NULL CHECK (revision>=1),
  ready boolean NOT NULL,
  values_json jsonb NOT NULL DEFAULT '{}',
  facts jsonb NOT NULL DEFAULT '[]',
  issues jsonb NOT NULL DEFAULT '[]',
  provenance jsonb NOT NULL DEFAULT '[]',
  answers jsonb NOT NULL DEFAULT '[]',
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (request_id,revision),
  UNIQUE (owner_id,request_id,revision),
  FOREIGN KEY (owner_id,request_id) REFERENCES work_requests(owner_id,request_id),
  CHECK (jsonb_typeof(values_json)='object' AND jsonb_typeof(issues)='array'),
  CHECK (NOT ready OR NOT jsonb_path_exists(issues, '$[*] ? (@.blocking == true)'))
);

-- 정보 및 실행 범위 승인 snapshot
CREATE TABLE approvals (
  approval_id uuid PRIMARY KEY,
  owner_id uuid NOT NULL,
  request_id uuid NOT NULL,
  revision bigint NOT NULL,
  account_id uuid NOT NULL,
  object_id uuid,
  target_slot text NOT NULL,
  review_digest text NOT NULL,
  scope jsonb NOT NULL,
  approved_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (owner_id,request_id,approval_id,revision),
  UNIQUE (request_id,revision),
  FOREIGN KEY (owner_id,request_id,revision) REFERENCES preparation_versions(owner_id,request_id,revision),
  FOREIGN KEY (owner_id,account_id) REFERENCES external_accounts(owner_id,account_id),
  FOREIGN KEY (owner_id,object_id) REFERENCES external_objects(owner_id,object_id)
);

-- 작업 상태의 유일한 저장 정본
CREATE TABLE jobs (
  job_id uuid PRIMARY KEY,
  owner_id uuid NOT NULL,
  request_id uuid NOT NULL UNIQUE,
  revision bigint NOT NULL,
  approval_id uuid NOT NULL,
  request_key text NOT NULL,
  request_digest text NOT NULL,
  state text NOT NULL CHECK (state IN ('active','stopping','done','stopped')),
  goal_verdict text CHECK (goal_verdict IN ('confirmed','not_reached','unknown')),
  final_evidence_id uuid,
  result_object_id uuid,
  next_action text,
  progress_json jsonb NOT NULL DEFAULT '{"step_index":0,"step_count":1,"confirmed_steps":[],"current_step":null}'::jsonb,
  error_json jsonb,
  lease_epoch bigint NOT NULL DEFAULT 0 CHECK (lease_epoch>=0),
  accepted_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (owner_id,job_id),
  UNIQUE (owner_id,request_key),
  FOREIGN KEY (owner_id,request_id,approval_id,revision) REFERENCES approvals(owner_id,request_id,approval_id,revision),
  CHECK ((state IN ('active','stopping') AND goal_verdict IS NULL AND final_evidence_id IS NULL AND next_action IS NULL) OR (state='done' AND goal_verdict IS NOT DISTINCT FROM 'confirmed' AND final_evidence_id IS NOT NULL AND next_action IS NOT NULL) OR (state='stopped' AND goal_verdict IS NOT NULL AND goal_verdict IN ('not_reached','unknown') AND next_action IS NOT NULL)),
  FOREIGN KEY (owner_id,result_object_id) REFERENCES external_objects(owner_id,object_id)
);

-- 계정별 안정 논리 슬롯 및 중복/미확인 효과 차단
CREATE TABLE effect_slots (
  owner_id uuid NOT NULL,
  account_id uuid NOT NULL,
  slot_key text NOT NULL,
  job_id uuid NOT NULL,
  object_id uuid,
  reconciled_by_job_id uuid,
  state text NOT NULL CHECK (state IN ('reserved','confirmed','unknown','absent')),
  PRIMARY KEY (owner_id,account_id,slot_key),
  FOREIGN KEY (owner_id,account_id) REFERENCES external_accounts(owner_id,account_id),
  FOREIGN KEY (owner_id,job_id) REFERENCES jobs(owner_id,job_id),
  FOREIGN KEY (owner_id,object_id) REFERENCES external_objects(owner_id,object_id),
  FOREIGN KEY (owner_id,reconciled_by_job_id) REFERENCES jobs(owner_id,job_id),
  CHECK ((state='confirmed') = (object_id IS NOT NULL))
);

-- 등록된 operation별 durable admission/효과 상태
CREATE TABLE effects (
  effect_id uuid PRIMARY KEY,
  owner_id uuid NOT NULL,
  job_id uuid NOT NULL,
  operation_id text NOT NULL,
  effect_key text NOT NULL,
  lease_epoch bigint NOT NULL CHECK (lease_epoch>=0),
  state text NOT NULL CHECK (state IN ('admitted','confirmed','absent','unknown')),
  admitted_at timestamptz NOT NULL DEFAULT now(),
  dispatched_at timestamptz,
  resolved_at timestamptz,
  UNIQUE (owner_id,job_id,effect_id),
  UNIQUE (job_id,effect_key),
  FOREIGN KEY (owner_id,job_id) REFERENCES jobs(owner_id,job_id)
);

-- 관측 성공과 실패를 별도 저장; 외부 상태/시간
CREATE TABLE observations (
  observation_id uuid PRIMARY KEY,
  owner_id uuid NOT NULL,
  job_id uuid NOT NULL,
  effect_id uuid,
  object_id uuid,
  method text NOT NULL CHECK (method IN ('independent_readback','submission_response','form_read','runtime_observation')),
  outcome text NOT NULL CHECK (outcome IN ('observed','unavailable')),
  reconciliation_verdict text CHECK (reconciliation_verdict IN ('confirmed','not_reached')),
  native_status text,
  snapshot jsonb NOT NULL DEFAULT '{}',
  observed_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (owner_id,job_id,observation_id),
  FOREIGN KEY (owner_id,job_id) REFERENCES jobs(owner_id,job_id),
  FOREIGN KEY (owner_id,job_id,effect_id) REFERENCES effects(owner_id,job_id,effect_id),
  FOREIGN KEY (owner_id,object_id) REFERENCES external_objects(owner_id,object_id),
  CHECK (outcome<>'unavailable' OR native_status IS NULL),
  CHECK (reconciliation_verdict IS NULL OR (method='independent_readback' AND outcome='observed' AND (reconciliation_verdict<>'confirmed' OR object_id IS NOT NULL)))
);

-- 작업·관측에 연결된 redacted 증거
CREATE TABLE evidence (
  evidence_id uuid PRIMARY KEY,
  owner_id uuid NOT NULL,
  job_id uuid NOT NULL,
  observation_id uuid NOT NULL,
  kind text NOT NULL CHECK (kind IN ('goal','operation','error')),
  payload_digest text NOT NULL,
  record jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (owner_id,job_id,evidence_id),
  FOREIGN KEY (owner_id,job_id,observation_id) REFERENCES observations(owner_id,job_id,observation_id)
);

ALTER TABLE work_requests ADD CONSTRAINT current_preparation_fk FOREIGN KEY (owner_id,request_id,revision) REFERENCES preparation_versions(owner_id,request_id,revision) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE work_requests ADD CONSTRAINT related_job_fk FOREIGN KEY (owner_id,related_job_id) REFERENCES jobs(owner_id,job_id);
ALTER TABLE jobs ADD CONSTRAINT final_evidence_fk FOREIGN KEY (owner_id,job_id,final_evidence_id) REFERENCES evidence(owner_id,job_id,evidence_id);

CREATE FUNCTION guard_job_transition() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF TG_OP='INSERT' THEN
   IF NEW.state<>'active' THEN RAISE EXCEPTION 'initial state' USING ERRCODE='23514'; END IF;
 ELSIF OLD.state IN ('done','stopped') THEN
   IF NEW IS DISTINCT FROM OLD THEN RAISE EXCEPTION 'terminal immutable' USING ERRCODE='23514'; END IF;
 ELSIF NEW.state<>OLD.state AND NOT ((OLD.state='active' AND NEW.state IN ('stopping','done')) OR (OLD.state='stopping' AND NEW.state='stopped')) THEN
   RAISE EXCEPTION 'invalid transition' USING ERRCODE='23514';
 END IF;
 IF NEW.state='done' AND NOT EXISTS (
   SELECT 1 FROM evidence e JOIN observations o ON (e.owner_id,e.job_id,e.observation_id)=(o.owner_id,o.job_id,o.observation_id)
   WHERE (e.owner_id,e.job_id,e.evidence_id)=(NEW.owner_id,NEW.job_id,NEW.final_evidence_id)
     AND e.kind='goal' AND o.method='independent_readback' AND o.outcome='observed'
     AND o.object_id IS NOT DISTINCT FROM NEW.result_object_id
 ) THEN RAISE EXCEPTION 'independent goal evidence required' USING ERRCODE='23514'; END IF;
 IF NEW.state='done' AND EXISTS (
   SELECT 1 FROM work_requests r WHERE r.owner_id=NEW.owner_id AND r.request_id=NEW.request_id
     AND ((r.operation<>'status' AND NEW.result_object_id IS NULL) OR
          (r.object_id IS NOT NULL AND r.object_id IS DISTINCT FROM NEW.result_object_id) OR
          (NEW.result_object_id IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM external_objects x WHERE x.owner_id=r.owner_id AND x.object_id=NEW.result_object_id
              AND (x.lesson_id,x.account_id,x.platform_id,x.object_kind)=(r.lesson_id,r.account_id,r.platform_id,r.object_kind)
          )))
 ) THEN RAISE EXCEPTION 'result object mismatch' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER job_transition BEFORE INSERT OR UPDATE ON jobs FOR EACH ROW EXECUTE FUNCTION guard_job_transition();
CREATE FUNCTION guard_admission() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE s text; ep bigint;
BEGIN
 SELECT state,lease_epoch INTO s,ep FROM jobs WHERE owner_id=NEW.owner_id AND job_id=NEW.job_id FOR UPDATE;
 IF NOT FOUND OR s<>'active' OR ep<>NEW.lease_epoch OR NEW.state<>'admitted' OR NEW.dispatched_at IS NOT NULL
   OR EXISTS (SELECT 1 FROM jobs j JOIN work_requests r ON (r.owner_id,r.request_id)=(j.owner_id,j.request_id)
              WHERE j.owner_id=NEW.owner_id AND j.job_id=NEW.job_id AND r.operation='status')
 THEN RAISE EXCEPTION 'admission forbidden' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER effect_admission BEFORE INSERT ON effects FOR EACH ROW EXECUTE FUNCTION guard_admission();

CREATE VIEW request_status AS SELECT r.owner_id,r.request_id,r.revision,r.draft_status,j.job_id,j.state AS job_state,j.goal_verdict
 FROM work_requests r LEFT JOIN jobs j ON j.owner_id=r.owner_id AND j.request_id=r.request_id;
CREATE VIEW object_status AS SELECT x.owner_id,x.object_id,x.lesson_id,x.platform_id,x.object_kind,x.native_id,x.public_url,x.unlinked_at,
 ok.native_status,ok.observed_at AS last_confirmed_at,ok.snapshot AS last_confirmed_snapshot,attempt.outcome AS latest_attempt_outcome,attempt.observed_at AS latest_attempt_at
 FROM external_objects x
 LEFT JOIN LATERAL (SELECT o.native_status,o.observed_at,o.snapshot FROM observations o WHERE o.owner_id=x.owner_id AND o.object_id=x.object_id AND o.outcome='observed' AND o.method='independent_readback' ORDER BY o.observed_at DESC,o.observation_id DESC LIMIT 1) ok ON true
 LEFT JOIN LATERAL (SELECT o.outcome,o.observed_at FROM observations o WHERE o.owner_id=x.owner_id AND o.object_id=x.object_id ORDER BY o.observed_at DESC,o.observation_id DESC LIMIT 1) attempt ON true;
-- Reconciliation is a new read-only status job, never an UPDATE of the previous terminal job.
CREATE VIEW job_reconciliation AS
 SELECT DISTINCT ON (r.owner_id,r.related_job_id)
 r.owner_id,r.related_job_id AS prior_job_id,j.job_id AS status_job_id,
 o.reconciliation_verdict AS verdict,o.object_id,e.evidence_id,o.observed_at
 FROM work_requests r JOIN jobs j ON (r.owner_id,r.request_id)=(j.owner_id,j.request_id)
 JOIN jobs prior ON (prior.owner_id,prior.job_id)=(r.owner_id,r.related_job_id)
 JOIN work_requests pr ON (pr.owner_id,pr.request_id)=(prior.owner_id,prior.request_id)
 JOIN evidence e ON (e.owner_id,e.job_id,e.evidence_id)=(j.owner_id,j.job_id,j.final_evidence_id)
 JOIN observations o ON (o.owner_id,o.job_id,o.observation_id)=(e.owner_id,e.job_id,e.observation_id)
 WHERE r.operation='status' AND j.state='done' AND prior.state='stopped' AND prior.goal_verdict='unknown'
 AND pr.operation IN ('create','update','renew')
 AND (r.lesson_id,r.account_id,r.platform_id,r.object_kind,r.target_slot)=(pr.lesson_id,pr.account_id,pr.platform_id,pr.object_kind,pr.target_slot)
 AND (pr.object_id IS NULL OR o.object_id=pr.object_id)
 AND o.reconciliation_verdict IS NOT NULL AND o.method='independent_readback' AND o.outcome='observed'
 ORDER BY r.owner_id,r.related_job_id,o.observed_at DESC,o.observation_id DESC;

CREATE INDEX lessons_owner_idx ON lessons(owner_id,created_at DESC,lesson_id);
CREATE INDEX requests_owner_idx ON work_requests(owner_id,created_at DESC,request_id);
CREATE INDEX jobs_owner_idx ON jobs(owner_id,accepted_at DESC,job_id);
CREATE INDEX observations_object_idx ON observations(owner_id,object_id,observed_at DESC);
CREATE INDEX evidence_job_idx ON evidence(owner_id,job_id,created_at);
INSERT INTO platforms VALUES ('PL01','크몽'),('PL02','탈잉'),('PL03','숨고'),('PL04','프람피'),('PL05','뮬'),('PL06','힙합플레이야'),('PL07','힙합LE');
INSERT INTO schema_migrations(version) VALUES (1);
COMMIT;
