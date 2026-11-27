\set ON_ERROR_STOP on
-- Run ONLY on a fresh disposable database after V5.3 DDL and guards.
BEGIN;
SET search_path TO chajayou_v53_mock, pg_catalog;
CREATE FUNCTION pg_temp.reject(label text, stmt text) RETURNS void LANGUAGE plpgsql AS $$
BEGIN
  BEGIN
    EXECUTE stmt;
    SET CONSTRAINTS ALL IMMEDIATE;
  EXCEPTION WHEN check_violation OR foreign_key_violation OR unique_violation THEN
    RAISE NOTICE 'PASS rejected %', label;
    RETURN;
  END;
  RAISE EXCEPTION 'FAIL accepted invalid operation: %',label;
END $$;
INSERT INTO users VALUES
('00000000-0000-4000-8000-000000000001','mock','A','active',NULL),
('00000000-0000-4000-8000-000000000002','mock','B','active',NULL);
INSERT INTO sources VALUES
('00000000-0000-4000-8000-000000000011','00000000-0000-4000-8000-000000000001','{}',1,NULL,'managed',now()),
('00000000-0000-4000-8000-000000000012','00000000-0000-4000-8000-000000000002','{}',1,NULL,'managed',now());
INSERT INTO platform_accounts VALUES
('00000000-0000-4000-8000-000000000021','00000000-0000-4000-8000-000000000001','PL01','mock','test','acct','linked'),
('00000000-0000-4000-8000-000000000022','00000000-0000-4000-8000-000000000002','PL01','mock','test','acct','unlinked');
SELECT pg_temp.reject('T08 duplicate active link',$q$UPDATE platform_accounts SET management_state='linked' WHERE id='00000000-0000-4000-8000-000000000022'$q$);
SELECT pg_temp.reject('T23 wrong source owner',$q$INSERT INTO platform_objects(id,account_id,kind,identity_namespace,native_object_key,source_id) VALUES ('00000000-0000-4000-8000-000000000031','00000000-0000-4000-8000-000000000021','product','test','obj','00000000-0000-4000-8000-000000000012')$q$);
INSERT INTO platform_objects(id,account_id,kind,identity_namespace,native_object_key,source_id) VALUES
('00000000-0000-4000-8000-000000000031','00000000-0000-4000-8000-000000000021','product','test','obj','00000000-0000-4000-8000-000000000011');
INSERT INTO work_requests(id,owner_id,source_id,source_revision,environment,selection_revision,approval_state,created_at) VALUES
('00000000-0000-4000-8000-000000000041','00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000011',1,'mock',1,'none',now());
INSERT INTO work_targets(id,request_id,platform_key,operation_key,account_id,object_id,prepared_source_revision,prep_generation,prep_state,plan,lifecycle) VALUES
('00000000-0000-4000-8000-000000000051','00000000-0000-4000-8000-000000000041','PL01','UPDATE','00000000-0000-4000-8000-000000000021','00000000-0000-4000-8000-000000000031',1,1,'ready','{}','not_accepted');
SET CONSTRAINTS ALL IMMEDIATE;
SET CONSTRAINTS ALL DEFERRED;
SELECT pg_temp.reject('T24 unapproved write',$q$UPDATE work_targets SET prep_state='consumed',lifecycle='accepted' WHERE id='00000000-0000-4000-8000-000000000051'$q$);
SET CONSTRAINTS ALL DEFERRED;
UPDATE work_requests SET approval_state='presented' WHERE id='00000000-0000-4000-8000-000000000041';
UPDATE work_targets SET prep_state='consumed',lifecycle='accepted' WHERE id='00000000-0000-4000-8000-000000000051';
UPDATE work_requests SET approval_state='frozen',accepted_at=now(),approval='{"actor_ref":"00000000-0000-4000-8000-000000000001","selection_revision":1,"accepted_target_ids":["00000000-0000-4000-8000-000000000051"],"target_plan_digests":{"00000000-0000-4000-8000-000000000051":"synthetic-not-a-real-digest"}}' WHERE id='00000000-0000-4000-8000-000000000041';
SET CONSTRAINTS ALL IMMEDIATE;
SELECT pg_temp.reject('T24 frozen plan change',$q$UPDATE work_targets SET plan='{"changed":true}' WHERE id='00000000-0000-4000-8000-000000000051'$q$);
SELECT pg_temp.reject('T24 frozen target deletion',$q$DELETE FROM work_targets WHERE id='00000000-0000-4000-8000-000000000051'$q$);
SELECT pg_temp.reject('T23 other owner history',$q$INSERT INTO history(id,owner_id,kind,object_id,recorded_at,payload,proof_ids) VALUES ('00000000-0000-4000-8000-000000000061','00000000-0000-4000-8000-000000000002','audit','00000000-0000-4000-8000-000000000031',now(),'{}','{}')$q$);
SELECT pg_temp.reject('T18 missing proof',$q$INSERT INTO history(id,owner_id,kind,recorded_at,payload,proof_ids) VALUES ('00000000-0000-4000-8000-000000000062','00000000-0000-4000-8000-000000000001','audit',now(),'{}',ARRAY['00000000-0000-4000-8000-000000000099'::uuid])$q$);
SELECT pg_temp.reject('T02 revision guard',$q$UPDATE sources SET content='{"changed":true}' WHERE id='00000000-0000-4000-8000-000000000011'$q$);
DO $$ BEGIN RAISE NOTICE 'PASS synthetic row/trigger smoke assertions; NOT full T01-T30'; END $$;
ROLLBACK;
