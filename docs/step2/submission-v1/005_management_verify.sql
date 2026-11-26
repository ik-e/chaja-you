-- Submission-only PostgreSQL design test. Run after 001, 003, 002, 004.
-- All data synthetic; rollback at end. Not app/API or real platform validation.
BEGIN;
INSERT INTO platform_profiles(profile_id,platform_id,object_kind,operation,version,rules_digest,rules,policy_status,mock_supported)
 VALUES ('00000000-0000-4000-8000-000000000044','PL01','service_listing','status','mock-v1','aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa','{}','unknown',true);
INSERT INTO work_requests(request_id,owner_id,lesson_id,version_id,profile_id,platform_id,object_kind,operation,account_id,related_job_id,target_slot,revision,draft_status)
 VALUES ('00000000-0000-4000-8000-000000000066','00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000011','00000000-0000-4000-8000-000000000021','00000000-0000-4000-8000-000000000044','PL01','service_listing','status','00000000-0000-4000-8000-000000000051','00000000-0000-4000-8000-000000000081','lesson11-slot1',1,'ready');
INSERT INTO preparation_versions(owner_id,request_id,revision,ready,values_json) VALUES ('00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000066',1,true,'{}');
INSERT INTO approvals(approval_id,owner_id,request_id,revision,account_id,target_slot,review_digest,scope)
 VALUES ('00000000-0000-4000-8000-000000000076','00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000066',1,'00000000-0000-4000-8000-000000000051','lesson11-slot1','cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc','{"environment":"mock","information_approved":true,"scope_approved":true}');
INSERT INTO jobs(job_id,owner_id,request_id,revision,approval_id,request_key,request_digest,state)
 VALUES ('00000000-0000-4000-8000-000000000086','00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000066',1,'00000000-0000-4000-8000-000000000076','synthetic-readback','cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc','active');
DO $$
BEGIN
 BEGIN
   INSERT INTO effects(effect_id,owner_id,job_id,operation_id,effect_key,lease_epoch,state)
     VALUES ('00000000-0000-4000-8000-000000000096','00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000086','NO-CHANGE','forbidden',0,'admitted');
   RAISE EXCEPTION 'read-only status admitted mutation';
 EXCEPTION WHEN check_violation THEN NULL; END;
END $$;
INSERT INTO external_objects(object_id,owner_id,lesson_id,account_id,platform_id,object_kind,native_id)
 VALUES ('00000000-0000-4000-8000-000000000121','00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000011','00000000-0000-4000-8000-000000000051','PL01','service_listing','mock-listing-001');
INSERT INTO observations(observation_id,owner_id,job_id,object_id,method,outcome,reconciliation_verdict,native_status,snapshot,observed_at)
 VALUES ('00000000-0000-4000-8000-000000000286','00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000086','00000000-0000-4000-8000-000000000121','independent_readback','observed','confirmed','mock_received','{"amount_krw":250000}','2026-11-26T01:00:00Z');
INSERT INTO evidence(evidence_id,owner_id,job_id,observation_id,kind,payload_digest,record)
 VALUES ('00000000-0000-4000-8000-000000000186','00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000086','00000000-0000-4000-8000-000000000286','goal','cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc','{"synthetic":true,"matches_prior_scope":true}');
UPDATE jobs SET state='done',goal_verdict='confirmed',final_evidence_id='00000000-0000-4000-8000-000000000186',result_object_id='00000000-0000-4000-8000-000000000121',next_action='독립 확인 완료' WHERE job_id='00000000-0000-4000-8000-000000000086';
UPDATE effect_slots SET state='confirmed',object_id='00000000-0000-4000-8000-000000000121',reconciled_by_job_id='00000000-0000-4000-8000-000000000086'
 WHERE owner_id='00000000-0000-4000-8000-000000000001' AND account_id='00000000-0000-4000-8000-000000000051' AND slot_key='lesson11-slot1' AND job_id='00000000-0000-4000-8000-000000000081' AND state='unknown';
-- Subsequent failed status attempt: keep last successful snapshot.
INSERT INTO work_requests(request_id,owner_id,lesson_id,version_id,profile_id,platform_id,object_kind,operation,account_id,object_id,target_slot,revision,draft_status)
 VALUES ('00000000-0000-4000-8000-000000000067','00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000011','00000000-0000-4000-8000-000000000021','00000000-0000-4000-8000-000000000044','PL01','service_listing','status','00000000-0000-4000-8000-000000000051','00000000-0000-4000-8000-000000000121','object121',1,'ready');
INSERT INTO preparation_versions(owner_id,request_id,revision,ready,values_json) VALUES ('00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000067',1,true,'{}');
INSERT INTO approvals(approval_id,owner_id,request_id,revision,account_id,object_id,target_slot,review_digest,scope)
 VALUES ('00000000-0000-4000-8000-000000000077','00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000067',1,'00000000-0000-4000-8000-000000000051','00000000-0000-4000-8000-000000000121','object121','cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc','{"environment":"mock"}');
INSERT INTO jobs(job_id,owner_id,request_id,revision,approval_id,request_key,request_digest,state)
 VALUES ('00000000-0000-4000-8000-000000000088','00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000067',1,'00000000-0000-4000-8000-000000000077','synthetic-failed-status','cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc','active');
INSERT INTO observations(observation_id,owner_id,job_id,object_id,method,outcome,observed_at)
 VALUES ('00000000-0000-4000-8000-000000000288','00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000088','00000000-0000-4000-8000-000000000121','independent_readback','unavailable','2026-11-26T02:00:00Z');
UPDATE jobs SET state='stopping' WHERE job_id='00000000-0000-4000-8000-000000000088';
UPDATE jobs SET state='stopped',goal_verdict='unknown',result_object_id='00000000-0000-4000-8000-000000000121',next_action='조회 실패' WHERE job_id='00000000-0000-4000-8000-000000000088';
DO $$
BEGIN
 IF NOT EXISTS (SELECT 1 FROM jobs WHERE job_id='00000000-0000-4000-8000-000000000081' AND state='stopped' AND goal_verdict='unknown' AND result_object_id IS NULL) THEN RAISE EXCEPTION 'prior job overwritten'; END IF;
 IF NOT EXISTS (SELECT 1 FROM job_reconciliation WHERE prior_job_id='00000000-0000-4000-8000-000000000081' AND status_job_id='00000000-0000-4000-8000-000000000086' AND verdict='confirmed' AND object_id='00000000-0000-4000-8000-000000000121' AND evidence_id='00000000-0000-4000-8000-000000000186') THEN RAISE EXCEPTION 'missing independent reconciliation'; END IF;
 IF NOT EXISTS (SELECT 1 FROM effect_slots WHERE owner_id='00000000-0000-4000-8000-000000000001' AND job_id='00000000-0000-4000-8000-000000000081' AND state='confirmed' AND object_id='00000000-0000-4000-8000-000000000121' AND reconciled_by_job_id='00000000-0000-4000-8000-000000000086') THEN RAISE EXCEPTION 'slot reconciliation mismatch'; END IF;
 IF EXISTS (SELECT 1 FROM effects WHERE job_id IN ('00000000-0000-4000-8000-000000000086','00000000-0000-4000-8000-000000000088')) THEN RAISE EXCEPTION 'status effect found'; END IF;
 IF NOT EXISTS (SELECT 1 FROM object_status WHERE object_id='00000000-0000-4000-8000-000000000121' AND native_status='mock_received' AND last_confirmed_snapshot->>'amount_krw'='250000' AND latest_attempt_outcome='unavailable' AND last_confirmed_at<latest_attempt_at) THEN RAISE EXCEPTION 'failed observation overwrote confirmed snapshot'; END IF;
 BEGIN
   INSERT INTO effect_slots(owner_id,account_id,slot_key,job_id,state) VALUES ('00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000051','lesson11-slot1','00000000-0000-4000-8000-000000000081','reserved');
   RAISE EXCEPTION 'duplicate slot accepted';
 EXCEPTION WHEN unique_violation THEN NULL; END;
END $$;
-- Force deferred current-preparation FK checks before rolling back.
SET CONSTRAINTS ALL IMMEDIATE;
ROLLBACK;
