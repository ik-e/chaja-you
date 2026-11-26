-- Run after 001, fixture, 002. Constraint tests only; not API authorization tests.
BEGIN;
DO $$
BEGIN
 IF (SELECT array_agg(version ORDER BY version) FROM schema_migrations) IS DISTINCT FROM ARRAY[1,2] THEN RAISE EXCEPTION 'migration versions'; END IF;
 IF (SELECT count(*) FROM lessons)<>2 OR (SELECT count(*) FROM jobs WHERE state='stopped' AND goal_verdict='unknown')<>1 OR (SELECT count(*) FROM evidence)<>1 THEN RAISE EXCEPTION 'fixture changed'; END IF;
 BEGIN
   INSERT INTO version_assets VALUES ('00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000021','00000000-0000-4000-8000-000000000999',1);
   RAISE EXCEPTION 'missing FK accepted';
 EXCEPTION WHEN foreign_key_violation THEN NULL; END;
 BEGIN
   INSERT INTO version_assets VALUES ('00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000021','00000000-0000-4000-8000-000000000032',1);
   RAISE EXCEPTION 'cross-owner FK accepted';
 EXCEPTION WHEN foreign_key_violation THEN NULL; END;
 BEGIN
   UPDATE jobs SET state='active',goal_verdict=NULL,next_action=NULL WHERE job_id='00000000-0000-4000-8000-000000000081';
   RAISE EXCEPTION 'terminal reopened';
 EXCEPTION WHEN check_violation THEN NULL; END;
 BEGIN
   INSERT INTO effects(effect_id,owner_id,job_id,operation_id,effect_key,lease_epoch,state) VALUES ('00000000-0000-4000-8000-000000000092','00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000081','K6','submit-2',0,'admitted');
   RAISE EXCEPTION 'terminal admission accepted';
 EXCEPTION WHEN check_violation THEN NULL; END;
 IF NOT EXISTS (SELECT 1 FROM request_status WHERE owner_id='00000000-0000-4000-8000-000000000001' AND request_id='00000000-0000-4000-8000-000000000061' AND job_state='stopped' AND goal_verdict='unknown') THEN RAISE EXCEPTION 'projection mismatch'; END IF;
 IF EXISTS (SELECT 1 FROM request_status WHERE owner_id='00000000-0000-4000-8000-000000000002' AND request_id='00000000-0000-4000-8000-000000000061') THEN RAISE EXCEPTION 'owner predicate mismatch'; END IF;
END $$;
ROLLBACK;
-- Application role/connection, SQL 23503 on blank DB, concurrent accept/admit,
-- evidence semantic match, digest and backup/secret canary require additional actual tests.
