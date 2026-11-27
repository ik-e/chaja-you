-- TASK-058 V5.3 synthetic DB guard candidate. Run only after db-physical-v5.3.sql.
-- Store-layer authorization, full typed payload validation and broker fencing are still required.
SET search_path TO chajayou_v53_mock, pg_catalog;

CREATE FUNCTION require_ok(ok boolean, message text) RETURNS void
LANGUAGE plpgsql SET search_path TO chajayou_v53_mock, pg_catalog AS $$
BEGIN
  IF ok IS DISTINCT FROM TRUE THEN
    RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = message;
  END IF;
END $$;

CREATE FUNCTION mutation_op(op text) RETURNS boolean
LANGUAGE sql IMMUTABLE AS $$
  SELECT op IN ('CREATE','UPDATE','RENEW','FIRST_OPEN_SCHEDULE','REPRESENTATIVE_SERVICE')
$$;

-- All trusted write entrypoints acquire the complete sorted key set BEFORE rows.
-- Exact canonical tuple comparison is still required: hash collisions only over-serialize.
CREATE FUNCTION lock_scopes(keys text[]) RETURNS void
LANGUAGE plpgsql SET search_path TO chajayou_v53_mock, pg_catalog AS $$
DECLARE k bigint;
BEGIN
  PERFORM require_ok(keys IS NOT NULL AND cardinality(keys)>0 AND array_position(keys,NULL::text) IS NULL,'invalid lock scope');
  FOR k IN SELECT DISTINCT hashtextextended(x,0) AS h FROM unnest(keys) x ORDER BY h
  LOOP
    PERFORM pg_advisory_xact_lock(k);
  END LOOP;
END $$;

CREATE FUNCTION target_owner(tid uuid) RETURNS uuid
LANGUAGE sql STABLE SET search_path TO chajayou_v53_mock, pg_catalog AS $$
  SELECT r.owner_id FROM work_targets t JOIN work_requests r ON r.id=t.request_id WHERE t.id=tid
$$;
CREATE FUNCTION object_owner(oid uuid) RETURNS uuid
LANGUAGE sql STABLE SET search_path TO chajayou_v53_mock, pg_catalog AS $$
  SELECT a.owner_id FROM platform_objects o JOIN platform_accounts a ON a.id=o.account_id WHERE o.id=oid
$$;
CREATE FUNCTION effect_owner(eid uuid) RETURNS uuid
LANGUAGE sql STABLE SET search_path TO chajayou_v53_mock, pg_catalog AS $$
  SELECT target_owner(e.target_id) FROM effects e WHERE e.id=eid
$$;
CREATE FUNCTION attempt_owner(aid uuid) RETURNS uuid
LANGUAGE sql STABLE SET search_path TO chajayou_v53_mock, pg_catalog AS $$
  SELECT a.owner_id FROM attempts t JOIN access_contexts a ON a.id=t.access_id WHERE t.id=aid
$$;

-- Identity/lineage anchors must not be rebound behind existing evidence.
CREATE FUNCTION immutable_anchor() RETURNS trigger
LANGUAGE plpgsql SET search_path TO chajayou_v53_mock, pg_catalog AS $$
BEGIN
  IF TG_TABLE_NAME='users' THEN
    PERFORM require_ok(ROW(OLD.id,OLD.issuer,OLD.subject) IS NOT DISTINCT FROM ROW(NEW.id,NEW.issuer,NEW.subject),'user identity immutable');
    PERFORM require_ok(OLD.state<>'retired' OR NEW.state='retired','retired user cannot reopen');
  ELSIF TG_TABLE_NAME='sources' THEN
    PERFORM require_ok(ROW(OLD.id,OLD.owner_id) IS NOT DISTINCT FROM ROW(NEW.id,NEW.owner_id),'source owner immutable');
    PERFORM require_ok(OLD.state<>'retired' OR NEW.state='retired','retired source cannot reopen');
    PERFORM require_ok(NEW.revision>=OLD.revision AND NEW.revision<=OLD.revision+1,'source revision must stay or increment once');
    PERFORM require_ok(NEW.content IS NOT DISTINCT FROM OLD.content OR NEW.revision=OLD.revision+1,'content change needs revision increment');
  ELSIF TG_TABLE_NAME='assets' THEN
    PERFORM require_ok(ROW(OLD.id,OLD.source_id,OLD.storage_key,OLD.digest,OLD.media_type,OLD.size_bytes,OLD.created_at) IS NOT DISTINCT FROM ROW(NEW.id,NEW.source_id,NEW.storage_key,NEW.digest,NEW.media_type,NEW.size_bytes,NEW.created_at),'asset bytes/identity immutable');
  ELSIF TG_TABLE_NAME='platform_accounts' THEN
    PERFORM require_ok(ROW(OLD.id,OLD.owner_id,OLD.environment,OLD.platform_key,OLD.identity_namespace,OLD.native_account_key) IS NOT DISTINCT FROM ROW(NEW.id,NEW.owner_id,NEW.environment,NEW.platform_key,NEW.identity_namespace,NEW.native_account_key),'account identity immutable');
    PERFORM require_ok(OLD.management_state<>'retired' OR NEW.management_state='retired','retired account cannot reopen');
  ELSIF TG_TABLE_NAME='platform_objects' THEN
    PERFORM require_ok(ROW(OLD.id,OLD.account_id,OLD.kind,OLD.identity_namespace,OLD.native_object_key) IS NOT DISTINCT FROM ROW(NEW.id,NEW.account_id,NEW.kind,NEW.identity_namespace,NEW.native_object_key),'object identity immutable');
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER users_immutable BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION immutable_anchor();
CREATE TRIGGER sources_immutable BEFORE UPDATE ON sources FOR EACH ROW EXECUTE FUNCTION immutable_anchor();
CREATE TRIGGER assets_immutable BEFORE UPDATE ON assets FOR EACH ROW EXECUTE FUNCTION immutable_anchor();
CREATE TRIGGER accounts_immutable BEFORE UPDATE ON platform_accounts FOR EACH ROW EXECUTE FUNCTION immutable_anchor();
CREATE TRIGGER objects_immutable BEFORE UPDATE ON platform_objects FOR EACH ROW EXECUTE FUNCTION immutable_anchor();

CREATE FUNCTION guard_object() RETURNS trigger
LANGUAGE plpgsql SET search_path TO chajayou_v53_mock, pg_catalog AS $$
DECLARE own uuid; src_owner uuid; src_state text; cycle_found boolean;
BEGIN
  SELECT owner_id INTO own FROM platform_accounts WHERE id=NEW.account_id;
  IF NEW.source_id IS NOT NULL THEN
    SELECT owner_id,state INTO src_owner,src_state FROM sources WHERE id=NEW.source_id;
    PERFORM require_ok(src_owner=own,'object/source owner mismatch');
    -- Existing links may persist while a retire transaction explicitly unlinks them.
    IF TG_OP='INSERT' OR NEW.source_id IS DISTINCT FROM OLD.source_id THEN
      PERFORM require_ok(src_state='managed','source not linkable');
    END IF;
  END IF;
  IF NEW.parent_id IS NOT NULL THEN
    PERFORM require_ok(EXISTS(SELECT 1 FROM platform_objects p WHERE p.id=NEW.parent_id AND p.account_id=NEW.account_id),'object parent account mismatch');
    WITH RECURSIVE parents(id,parent_id) AS (
      SELECT p.id,p.parent_id FROM platform_objects p WHERE p.id=NEW.parent_id
      UNION
      SELECT p.id,p.parent_id FROM platform_objects p JOIN parents q ON p.id=q.parent_id
    ) SELECT EXISTS(SELECT 1 FROM parents WHERE id=NEW.id) INTO cycle_found;
    PERFORM require_ok(NOT cycle_found,'object parent cycle');
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER objects_guard BEFORE INSERT OR UPDATE ON platform_objects FOR EACH ROW EXECUTE FUNCTION guard_object();

CREATE FUNCTION guard_request() RETURNS trigger
LANGUAGE plpgsql SET search_path TO chajayou_v53_mock, pg_catalog AS $$
BEGIN
  IF TG_OP='UPDATE' THEN
    PERFORM require_ok(ROW(OLD.id,OLD.owner_id,OLD.environment,OLD.created_at) IS NOT DISTINCT FROM ROW(NEW.id,NEW.owner_id,NEW.environment,NEW.created_at),'request identity immutable');
    IF OLD.approval_state='frozen' THEN
      PERFORM require_ok(NEW IS NOT DISTINCT FROM OLD,'frozen request immutable');
    END IF;
    PERFORM require_ok(NEW.selection_revision>=OLD.selection_revision,'selection revision rollback');
    PERFORM require_ok(NEW.approval_state=OLD.approval_state OR
      (OLD.approval_state='none' AND NEW.approval_state='presented') OR
      (OLD.approval_state='presented' AND NEW.approval_state IN ('invalidated','frozen')) OR
      (OLD.approval_state='invalidated' AND NEW.approval_state='presented'),'illegal approval transition');
  ELSE
    PERFORM require_ok(NEW.approval_state='none','new request must start unapproved');
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER requests_guard BEFORE INSERT OR UPDATE ON work_requests FOR EACH ROW EXECUTE FUNCTION guard_request();

CREATE FUNCTION guard_target() RETURNS trigger
LANGUAGE plpgsql SET search_path TO chajayou_v53_mock, pg_catalog AS $$
DECLARE r work_requests%ROWTYPE; a platform_accounts%ROWTYPE; old_owner uuid;
BEGIN
  IF TG_OP='DELETE' THEN
    SELECT * INTO r FROM work_requests WHERE id=OLD.request_id;
    PERFORM require_ok(r.approval_state<>'frozen' AND OLD.lifecycle='not_accepted','accepted or frozen target cannot be deleted');
    RETURN OLD;
  END IF;
  SELECT * INTO r FROM work_requests WHERE id=NEW.request_id;
  PERFORM require_ok(r.id IS NOT NULL,'target request absent');
  IF NEW.account_id IS NOT NULL THEN
    SELECT * INTO a FROM platform_accounts WHERE id=NEW.account_id;
    PERFORM require_ok(a.owner_id=r.owner_id AND a.platform_key=NEW.platform_key AND a.environment=r.environment,'target account mismatch');
  END IF;
  IF NEW.object_id IS NOT NULL THEN
    PERFORM require_ok(EXISTS(SELECT 1 FROM platform_objects o WHERE o.id=NEW.object_id AND o.account_id=NEW.account_id),'target object/account mismatch');
  END IF;
  IF NEW.prior_target_id IS NOT NULL THEN
    SELECT target_owner(NEW.prior_target_id) INTO old_owner;
    PERFORM require_ok(old_owner=r.owner_id,'prior target owner mismatch');
  END IF;
  IF TG_OP='INSERT' THEN
    PERFORM require_ok(r.approval_state<>'frozen' AND NEW.lifecycle='not_accepted','target cannot be added after freeze or preaccepted');
  ELSE
    PERFORM require_ok(ROW(OLD.id,OLD.request_id,OLD.platform_key,OLD.operation_key,OLD.prior_target_id) IS NOT DISTINCT FROM ROW(NEW.id,NEW.request_id,NEW.platform_key,NEW.operation_key,NEW.prior_target_id),'target identity immutable');
    IF r.approval_state='frozen' OR OLD.lifecycle<>'not_accepted' THEN
      PERFORM require_ok(ROW(OLD.account_id,OLD.object_id,OLD.prepared_source_revision,OLD.prep_generation,OLD.prep_state,OLD.profile_ref,OLD.plan) IS NOT DISTINCT FROM ROW(NEW.account_id,NEW.object_id,NEW.prepared_source_revision,NEW.prep_generation,NEW.prep_state,NEW.profile_ref,NEW.plan),'accepted or frozen plan immutable');
      PERFORM require_ok(OLD.lifecycle<>'not_accepted' OR NEW.lifecycle='not_accepted','frozen unaccepted disposition immutable');
    END IF;
    PERFORM require_ok(NEW.prep_generation>=OLD.prep_generation,'prep generation rollback');
    PERFORM require_ok(NEW.lifecycle=OLD.lifecycle OR
      (OLD.lifecycle='not_accepted' AND NEW.lifecycle='accepted') OR
      (OLD.lifecycle='accepted' AND NEW.lifecycle IN ('running','fencing')) OR
      (OLD.lifecycle='running' AND NEW.lifecycle IN ('fencing','ended')) OR
      (OLD.lifecycle='fencing' AND NEW.lifecycle='ended'),'illegal target lifecycle transition');
    PERFORM require_ok(OLD.lifecycle<>'ended' OR NEW.ended_at IS NOT DISTINCT FROM OLD.ended_at,'ended timestamp immutable');
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER targets_guard BEFORE INSERT OR UPDATE OR DELETE ON work_targets FOR EACH ROW EXECUTE FUNCTION guard_target();

-- Cross-row acceptance is checked against the FINAL transaction state.
-- TX02 updates targets/effects first, then freezes request; no partial commit allowed.
CREATE FUNCTION check_request_aggregate() RETURNS trigger
LANGUAGE plpgsql SET search_path TO chajayou_v53_mock, pg_catalog AS $$
DECLARE rid uuid; r work_requests%ROWTYPE; accepted uuid[]; declared uuid[];
BEGIN
  IF TG_TABLE_NAME='work_requests' THEN rid:=NEW.id; ELSE rid:=NEW.request_id; END IF;
  SELECT * INTO r FROM work_requests WHERE id=rid;
  IF NOT FOUND THEN RETURN NULL; END IF;
  IF r.approval_state='frozen' THEN
    PERFORM require_ok(jsonb_typeof(r.approval->'accepted_target_ids')='array','frozen approval missing accepted set');
    PERFORM require_ok(jsonb_typeof(r.approval->'target_plan_digests')='object','frozen approval missing digest map');
    SELECT coalesce(array_agg(t.id ORDER BY t.id),'{}'::uuid[]) INTO accepted
      FROM work_targets t WHERE t.request_id=rid AND t.lifecycle<>'not_accepted';
    SELECT coalesce(array_agg(x::uuid ORDER BY x::uuid),'{}'::uuid[]) INTO declared
      FROM jsonb_array_elements_text(r.approval->'accepted_target_ids') x;
    PERFORM require_ok(cardinality(accepted)>0 AND accepted=declared,'frozen accepted set mismatch');
    PERFORM require_ok((SELECT coalesce(array_agg(k::uuid ORDER BY k::uuid),'{}'::uuid[]) FROM jsonb_object_keys(r.approval->'target_plan_digests') k)=accepted,'frozen digest set mismatch');
    PERFORM require_ok((r.approval->>'actor_ref')::uuid=r.owner_id AND (r.approval->>'selection_revision')::integer=r.selection_revision,'frozen approval actor/revision mismatch');
    PERFORM require_ok(NOT EXISTS(SELECT 1 FROM work_targets t WHERE t.request_id=rid AND
      ((t.lifecycle<>'not_accepted' AND (NOT mutation_op(t.operation_key) OR t.prep_state<>'consumed' OR t.account_id IS NULL)) OR
       (t.lifecycle='not_accepted' AND t.prep_state NOT IN ('held','excluded')))),'frozen disposition mismatch');
  ELSE
    PERFORM require_ok(NOT EXISTS(SELECT 1 FROM work_targets t WHERE t.request_id=rid AND mutation_op(t.operation_key) AND t.lifecycle<>'not_accepted'),'write accepted without frozen approval');
  END IF;
  RETURN NULL;
END $$;
CREATE CONSTRAINT TRIGGER requests_aggregate AFTER INSERT OR UPDATE ON work_requests DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_request_aggregate();
CREATE CONSTRAINT TRIGGER targets_aggregate AFTER INSERT OR UPDATE ON work_targets DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_request_aggregate();

CREATE FUNCTION guard_command() RETURNS trigger
LANGUAGE plpgsql SET search_path TO chajayou_v53_mock, pg_catalog AS $$
BEGIN
  IF NEW.source_id IS NOT NULL AND NEW.work_request_id IS NOT NULL THEN
    PERFORM require_ok(EXISTS(SELECT 1 FROM work_requests r WHERE r.id=NEW.work_request_id AND r.source_id=NEW.source_id),'command source/request mismatch');
  END IF;
  IF TG_OP='INSERT' THEN
    PERFORM require_ok(NEW.state='reserved','command must start reserved');
  ELSE
    PERFORM require_ok(ROW(OLD.id,OLD.owner_id,OLD.kind,OLD.request_key,OLD.request_digest,OLD.created_at,OLD.source_id,OLD.work_request_id,OLD.scope) IS NOT DISTINCT FROM ROW(NEW.id,NEW.owner_id,NEW.kind,NEW.request_key,NEW.request_digest,NEW.created_at,NEW.source_id,NEW.work_request_id,NEW.scope),'command identity or intent immutable');
    PERFORM require_ok(OLD.state='reserved' OR NEW IS NOT DISTINCT FROM OLD,'final receipt immutable');
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER commands_guard BEFORE INSERT OR UPDATE ON commands FOR EACH ROW EXECUTE FUNCTION guard_command();

CREATE FUNCTION guard_access() RETURNS trigger
LANGUAGE plpgsql SET search_path TO chajayou_v53_mock, pg_catalog AS $$
DECLARE t work_targets%ROWTYPE; r work_requests%ROWTYPE; newest integer;
BEGIN
  IF NEW.target_id IS NOT NULL THEN
    SELECT * INTO t FROM work_targets WHERE id=NEW.target_id;
    SELECT * INTO r FROM work_requests WHERE id=t.request_id;
    PERFORM require_ok(r.owner_id=NEW.owner_id AND r.environment=NEW.environment AND t.platform_key=NEW.platform_key,'access target scope mismatch');
    IF t.account_id IS NOT NULL THEN
      PERFORM require_ok((NEW.expected_account_id IS NULL OR NEW.expected_account_id=t.account_id) AND
        (NEW.verified_account_id IS NULL OR NEW.verified_account_id=t.account_id),'access target account mismatch');
    END IF;
  END IF;
  IF TG_OP='INSERT' THEN
    SELECT max(generation) INTO newest FROM access_contexts WHERE owner_id=NEW.owner_id AND context_key=NEW.context_key;
    PERFORM require_ok(NEW.state='human' AND (newest IS NULL OR NEW.generation>newest),'new access generation must advance');
  ELSE
    PERFORM require_ok(ROW(OLD.id,OLD.owner_id,OLD.target_id,OLD.platform_key,OLD.expected_account_id,OLD.purpose,OLD.context_key,OLD.generation,OLD.environment) IS NOT DISTINCT FROM ROW(NEW.id,NEW.owner_id,NEW.target_id,NEW.platform_key,NEW.expected_account_id,NEW.purpose,NEW.context_key,NEW.generation,NEW.environment),'access identity immutable');
    PERFORM require_ok(NEW.state=OLD.state OR
      (OLD.state='human' AND NEW.state IN ('verifying','blocked')) OR
      (OLD.state='verifying' AND NEW.state IN ('verified','blocked')) OR
      (OLD.state='verified' AND NEW.state='blocked'),'illegal access transition');
    IF OLD.state IN ('verified','blocked') THEN
      PERFORM require_ok(ROW(OLD.verified_account_id,OLD.scope,OLD.expires_at) IS NOT DISTINCT FROM ROW(NEW.verified_account_id,NEW.scope,NEW.expires_at),'verified scope immutable; new generation required');
    END IF;
    PERFORM require_ok(OLD.state<>'blocked' OR OLD.blocked_at IS NOT DISTINCT FROM NEW.blocked_at,'blocked timestamp immutable');
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER access_guard BEFORE INSERT OR UPDATE ON access_contexts FOR EACH ROW EXECUTE FUNCTION guard_access();

CREATE FUNCTION guard_attempt() RETURNS trigger
LANGUAGE plpgsql SET search_path TO chajayou_v53_mock, pg_catalog AS $$
DECLARE a access_contexts%ROWTYPE; t work_targets%ROWTYPE; r work_requests%ROWTYPE;
BEGIN
  SELECT * INTO a FROM access_contexts WHERE id=NEW.access_id;
  IF NEW.target_id IS NOT NULL THEN
    SELECT * INTO t FROM work_targets WHERE id=NEW.target_id;
    SELECT * INTO r FROM work_requests WHERE id=t.request_id;
    PERFORM require_ok(r.owner_id=a.owner_id AND r.environment=a.environment AND t.platform_key=a.platform_key,'attempt target/access mismatch');
    PERFORM require_ok(a.target_id IS NULL OR a.target_id=t.id,'attempt wrong access target');
    PERFORM require_ok(t.account_id IS NULL OR a.verified_account_id=t.account_id,'attempt target account mismatch');
  END IF;
  IF NEW.object_id IS NOT NULL THEN
    PERFORM require_ok(EXISTS(SELECT 1 FROM platform_objects o WHERE o.id=NEW.object_id AND o.account_id=a.verified_account_id),'attempt object/account mismatch');
  END IF;
  IF TG_OP='INSERT' THEN
    PERFORM require_ok((NEW.kind='read' AND NEW.state='pending') OR (NEW.kind='write' AND NEW.state='reserved'),'attempt initial state');
  ELSE
    PERFORM require_ok(ROW(OLD.id,OLD.target_id,OLD.access_id,OLD.object_id,OLD.kind,OLD.purpose_key,OLD.scope,OLD.sequence_no,OLD.requested_at) IS NOT DISTINCT FROM ROW(NEW.id,NEW.target_id,NEW.access_id,NEW.object_id,NEW.kind,NEW.purpose_key,NEW.scope,NEW.sequence_no,NEW.requested_at),'attempt intent immutable');
    PERFORM require_ok(NEW.state=OLD.state OR
      (OLD.kind='read' AND ((OLD.state='pending' AND NEW.state IN ('running','unavailable')) OR (OLD.state='running' AND NEW.state IN ('observed','unavailable')))) OR
      (OLD.kind='write' AND ((OLD.state='reserved' AND NEW.state IN ('started','sealed')) OR (OLD.state='started' AND NEW.state='sealed'))),'illegal attempt transition');
    PERFORM require_ok(OLD.started_at IS NULL OR NEW.started_at IS NOT DISTINCT FROM OLD.started_at,'attempt start immutable');
    PERFORM require_ok(OLD.finished_at IS NULL OR NEW IS NOT DISTINCT FROM OLD,'terminal attempt immutable');
  END IF;
  IF TG_OP='INSERT' OR (NEW.state IN ('started','running') AND NEW.state IS DISTINCT FROM OLD.state) THEN
    PERFORM require_ok(a.state='verified' AND a.expires_at>clock_timestamp() AND NOT EXISTS(
      SELECT 1 FROM access_contexts q WHERE q.owner_id=a.owner_id AND q.context_key=a.context_key AND q.generation>a.generation),'attempt access not current');
    IF NEW.kind='write' THEN
      PERFORM require_ok(mutation_op(t.operation_key) AND t.lifecycle='running' AND r.approval_state='frozen' AND a.target_id=t.id AND a.verified_account_id=t.account_id,'write not accepted/running');
      PERFORM require_ok(EXISTS(SELECT 1 FROM platform_accounts p JOIN users u ON u.id=p.owner_id WHERE p.id=a.verified_account_id AND p.management_state='linked' AND u.state='active'),'write account not actively linked');
    END IF;
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER attempts_guard BEFORE INSERT OR UPDATE ON attempts FOR EACH ROW EXECUTE FUNCTION guard_attempt();

CREATE FUNCTION guard_effect() RETURNS trigger
LANGUAGE plpgsql SET search_path TO chajayou_v53_mock, pg_catalog AS $$
DECLARE t work_targets%ROWTYPE; r work_requests%ROWTYPE; p effects%ROWTYPE; a attempts%ROWTYPE;
BEGIN
  SELECT * INTO t FROM work_targets WHERE id=NEW.target_id;
  SELECT * INTO r FROM work_requests WHERE id=t.request_id;
  PERFORM require_ok(mutation_op(t.operation_key) AND t.lifecycle<>'not_accepted','effect needs accepted mutation target');
  IF NEW.attempt_id IS NOT NULL THEN
    SELECT * INTO a FROM attempts WHERE id=NEW.attempt_id;
    PERFORM require_ok(a.target_id=t.id AND a.kind='write','effect attempt mismatch');
  END IF;
  IF NEW.object_id IS NOT NULL THEN
    PERFORM require_ok(EXISTS(SELECT 1 FROM platform_objects o WHERE o.id=NEW.object_id AND o.account_id=t.account_id),'effect object account mismatch');
  END IF;
  IF NEW.prior_effect_id IS NOT NULL THEN
    SELECT * INTO p FROM effects WHERE id=NEW.prior_effect_id;
    PERFORM require_ok(effect_owner(p.id)=r.owner_id,'prior effect owner mismatch');
  END IF;
  IF TG_OP='INSERT' THEN
    PERFORM require_ok(NEW.state='not_attempted' AND NEW.attempt_id IS NULL,'effect initial state');
  ELSE
    PERFORM require_ok(ROW(OLD.id,OLD.target_id,OLD.prior_effect_id,OLD.rule_key,OLD.logical_effect_key,OLD.intent_digest,OLD.root_key,OLD.scope_path,OLD.required) IS NOT DISTINCT FROM ROW(NEW.id,NEW.target_id,NEW.prior_effect_id,NEW.rule_key,NEW.logical_effect_key,NEW.intent_digest,NEW.root_key,NEW.scope_path,NEW.required),'effect intent immutable');
    PERFORM require_ok(OLD.attempt_id IS NULL OR NEW.attempt_id IS NOT DISTINCT FROM OLD.attempt_id,'effect attempt cannot be replaced');
    PERFORM require_ok(OLD.object_id IS NULL OR NEW.object_id IS NOT DISTINCT FROM OLD.object_id,'effect object cannot be rebound');
    PERFORM require_ok(NEW.updated_at>=OLD.updated_at,'effect time rollback');
    PERFORM require_ok(NEW.state=OLD.state OR
      (OLD.state='not_attempted' AND NEW.state='reserved') OR
      (OLD.state='reserved' AND NEW.state IN ('in_flight','none_confirmed','unknown')) OR
      (OLD.state='in_flight' AND NEW.state IN ('confirmed','none_confirmed','unknown')) OR
      (OLD.state='unknown' AND NEW.state IN ('confirmed','none_confirmed')),'illegal effect transition');
    IF NEW.state='reserved' AND OLD.state<>'reserved' THEN
      PERFORM require_ok(t.lifecycle='running' AND r.approval_state='frozen' AND a.state='reserved','reserve outside running target');
    END IF;
    IF NEW.state='in_flight' AND OLD.state<>'in_flight' THEN
      PERFORM require_ok(t.lifecycle='running' AND a.state='started','effect start without one-shot attempt start');
    END IF;
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER effects_guard BEFORE INSERT OR UPDATE ON effects FOR EACH ROW EXECUTE FUNCTION guard_effect();

CREATE FUNCTION guard_history() RETURNS trigger
LANGUAGE plpgsql SET search_path TO chajayou_v53_mock, pg_catalog AS $$
DECLARE eid_target uuid; at_kind text; at_target uuid; at_object uuid;
BEGIN
  PERFORM require_ok(NEW.kind IN ('identity','management_binding','management','rights','quota','relation','response','observation','effect_judgment','target_result','goal','error','cleanup','metric','evidence','audit'),'unknown history kind');
  PERFORM require_ok(NEW.target_id IS NULL OR target_owner(NEW.target_id)=NEW.owner_id,'history target owner mismatch');
  PERFORM require_ok(NEW.effect_id IS NULL OR effect_owner(NEW.effect_id)=NEW.owner_id,'history effect owner mismatch');
  PERFORM require_ok(NEW.attempt_id IS NULL OR attempt_owner(NEW.attempt_id)=NEW.owner_id,'history attempt owner mismatch');
  PERFORM require_ok(NEW.object_id IS NULL OR object_owner(NEW.object_id)=NEW.owner_id,'history object owner mismatch');
  PERFORM require_ok(NEW.related_object_id IS NULL OR object_owner(NEW.related_object_id)=NEW.owner_id,'history related object owner mismatch');
  PERFORM require_ok(NEW.account_id IS NULL OR EXISTS(SELECT 1 FROM platform_accounts p WHERE p.id=NEW.account_id AND p.owner_id=NEW.owner_id),'history account owner mismatch');
  PERFORM require_ok(NEW.access_id IS NULL OR EXISTS(SELECT 1 FROM access_contexts a WHERE a.id=NEW.access_id AND a.owner_id=NEW.owner_id),'history access owner mismatch');
  IF NEW.effect_id IS NOT NULL THEN
    SELECT target_id INTO eid_target FROM effects WHERE id=NEW.effect_id;
    PERFORM require_ok(NEW.target_id IS NULL OR NEW.target_id=eid_target,'history target/effect mismatch');
  END IF;
  IF NEW.attempt_id IS NOT NULL THEN
    SELECT kind,target_id,object_id INTO at_kind,at_target,at_object FROM attempts WHERE id=NEW.attempt_id;
    PERFORM require_ok(NEW.access_id IS NULL OR EXISTS(SELECT 1 FROM attempts a WHERE a.id=NEW.attempt_id AND a.access_id=NEW.access_id),'history attempt/access mismatch');
    PERFORM require_ok(at_object IS NULL OR NEW.object_id IS NULL OR at_object=NEW.object_id,'history attempt/object mismatch');
    -- A later read request may have its own target; effect scope is validated separately.
    PERFORM require_ok(at_kind<>'write' OR NEW.target_id IS NULL OR NEW.target_id=at_target,'history write attempt/target mismatch');
    IF at_kind='write' AND NEW.effect_id IS NOT NULL THEN
      PERFORM require_ok(EXISTS(SELECT 1 FROM effects e WHERE e.id=NEW.effect_id AND e.attempt_id=NEW.attempt_id),'history write attempt/effect mismatch');
    END IF;
  END IF;
  IF NEW.account_id IS NOT NULL AND NEW.object_id IS NOT NULL THEN
    PERFORM require_ok(EXISTS(SELECT 1 FROM platform_objects o WHERE o.id=NEW.object_id AND o.account_id=NEW.account_id),'history object/account mismatch');
  END IF;
  PERFORM require_ok(cardinality(NEW.proof_ids)=(SELECT count(DISTINCT p) FROM unnest(NEW.proof_ids) p),'duplicate proof ids');
  PERFORM require_ok(NOT EXISTS(SELECT 1 FROM unnest(NEW.proof_ids) p WHERE NOT EXISTS(SELECT 1 FROM history h WHERE h.id=p AND h.owner_id=NEW.owner_id)),'missing or other-owner proof');
  IF NEW.kind='management_binding' THEN
    PERFORM require_ok(NEW.object_id IS NOT NULL AND NEW.source_id IS NOT NULL AND NEW.version_no IS NOT NULL AND (NEW.command_id IS NOT NULL OR (NEW.target_id IS NOT NULL AND NEW.effect_id IS NOT NULL)),'binding event missing exact refs');
    PERFORM require_ok(NEW.payload->>'binding_action' IN ('link','unlink'),'binding action missing');
  ELSIF NEW.kind='quota' THEN
    PERFORM require_ok(NEW.account_id IS NOT NULL AND NEW.observed_at IS NOT NULL,'quota scope missing');
  ELSIF NEW.kind='relation' THEN
    PERFORM require_ok(NEW.object_id IS NOT NULL AND (NEW.related_object_id IS NOT NULL OR NEW.target_id IS NOT NULL),'relation scope missing');
  ELSIF NEW.kind='response' THEN
    PERFORM require_ok(NEW.attempt_id IS NOT NULL,'response needs attempt');
  ELSIF NEW.kind='observation' THEN
    PERFORM require_ok(NEW.attempt_id IS NOT NULL AND at_kind='read' AND NEW.observed_at IS NOT NULL,'observation needs read attempt/time');
    IF NEW.payload->>'eligibility'='eligible' THEN
      PERFORM require_ok(EXISTS(SELECT 1 FROM attempts a WHERE a.id=NEW.attempt_id AND a.state='observed'),'eligible observation needs observed read');
    END IF;
  ELSIF NEW.kind='effect_judgment' THEN
    PERFORM require_ok(NEW.effect_id IS NOT NULL AND NEW.version_no IS NOT NULL AND cardinality(NEW.proof_ids)>0,'effect judgment missing refs');
  ELSIF NEW.kind='target_result' THEN
    PERFORM require_ok(NEW.target_id IS NOT NULL AND NEW.version_no IS NOT NULL,'target result missing refs');
  ELSIF NEW.kind='goal' THEN
    PERFORM require_ok(NEW.object_id IS NOT NULL AND NEW.version_no IS NOT NULL,'goal needs exact object');
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER history_guard BEFORE INSERT ON history FOR EACH ROW EXECUTE FUNCTION guard_history();
CREATE FUNCTION block_history_mutation() RETURNS trigger
LANGUAGE plpgsql SET search_path TO chajayou_v53_mock, pg_catalog AS $$
BEGIN
  RAISE EXCEPTION USING ERRCODE='23514', MESSAGE='history append only; retention maintenance not enabled';
END $$;
CREATE TRIGGER history_append_only BEFORE UPDATE OR DELETE ON history FOR EACH ROW EXECUTE FUNCTION block_history_mutation();

-- Final effect state must have evidence recorded atomically.
-- These are minimum DB checks, not a proof of actual external semantics.
CREATE FUNCTION check_effect_final() RETURNS trigger
LANGUAGE plpgsql SET search_path TO chajayou_v53_mock, pg_catalog AS $$
DECLARE e effects%ROWTYPE; t work_targets%ROWTYPE; r work_requests%ROWTYPE;
BEGIN
  SELECT * INTO e FROM effects WHERE id=NEW.id;
  IF NOT FOUND THEN RETURN NULL; END IF;
  SELECT * INTO t FROM work_targets WHERE id=e.target_id;
  SELECT * INTO r FROM work_requests WHERE id=t.request_id;
  PERFORM require_ok(r.approval_state='frozen' AND mutation_op(t.operation_key) AND t.lifecycle<>'not_accepted','effect outside frozen mutation');
  IF e.state='confirmed' THEN
    PERFORM require_ok(EXISTS(
      SELECT 1 FROM history j JOIN history h ON h.id=ANY(j.proof_ids)
        JOIN attempts a ON a.id=h.attempt_id JOIN access_contexts ac ON ac.id=a.access_id
      WHERE j.kind='effect_judgment' AND j.effect_id=e.id AND j.payload->>'effect_verdict'='confirmed'
        AND h.kind='observation' AND h.effect_id=e.id AND h.payload->>'eligibility'='eligible'
        AND h.owner_id=r.owner_id AND h.object_id IS NOT DISTINCT FROM e.object_id
        AND a.kind='read' AND a.state='observed' AND ac.verified_account_id=t.account_id
    ),'confirmed effect lacks exact independent observation');
  ELSIF e.state='none_confirmed' THEN
    PERFORM require_ok(EXISTS(SELECT 1 FROM history j JOIN history h ON h.id=ANY(j.proof_ids)
      WHERE j.kind='effect_judgment' AND j.effect_id=e.id AND j.payload->>'effect_verdict'='none_confirmed'
        AND h.effect_id=e.id AND h.kind IN ('observation','evidence') AND h.owner_id=r.owner_id),'none-confirmed effect lacks proof');
  END IF;
  RETURN NULL;
END $$;
CREATE CONSTRAINT TRIGGER effects_final AFTER INSERT OR UPDATE ON effects DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_effect_final();

-- A started write must have reserved effects atomically advanced to in_flight.
CREATE FUNCTION check_attempt_final() RETURNS trigger
LANGUAGE plpgsql SET search_path TO chajayou_v53_mock, pg_catalog AS $$
DECLARE a attempts%ROWTYPE;
BEGIN
  SELECT * INTO a FROM attempts WHERE id=NEW.id;
  IF NOT FOUND OR a.kind<>'write' THEN RETURN NULL; END IF;
  IF a.state='reserved' THEN
    PERFORM require_ok(EXISTS(SELECT 1 FROM effects e WHERE e.attempt_id=a.id AND e.state='reserved'),'write reservation missing effects');
    PERFORM require_ok(NOT EXISTS(SELECT 1 FROM effects e WHERE e.attempt_id=a.id AND e.state<>'reserved'),'mixed reservation state');
  ELSIF a.state='started' THEN
    PERFORM require_ok(EXISTS(SELECT 1 FROM effects e WHERE e.attempt_id=a.id),'started write missing effects');
    PERFORM require_ok(NOT EXISTS(SELECT 1 FROM effects e WHERE e.attempt_id=a.id AND e.state IN ('not_attempted','reserved')),'start did not advance reserved effects');
  ELSIF a.state='sealed' THEN
    PERFORM require_ok(NOT EXISTS(SELECT 1 FROM effects e WHERE e.attempt_id=a.id AND e.state IN ('reserved','in_flight')),'sealed write has unresolved active effects');
  END IF;
  RETURN NULL;
END $$;
CREATE CONSTRAINT TRIGGER attempts_final AFTER INSERT OR UPDATE ON attempts DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_attempt_final();

-- No PUBLIC access. Product roles, read isolation and trusted write entrypoints
-- are deliberately NOT provisioned by this mock-only candidate.
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA chajayou_v53_mock FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA chajayou_v53_mock FROM PUBLIC;
