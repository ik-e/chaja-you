-- Existing PostgreSQL v1 -> v2; non-destructive additive migration.
BEGIN;
ALTER TABLE observations ADD COLUMN failure_code text CHECK (failure_code IN ('AUTH_REQUIRED','RUNTIME_ERROR','EFFECT_UNKNOWN','PERMISSION_DENIED','MODEL_UNAVAILABLE'));
CREATE INDEX observations_job_idx ON observations(owner_id,job_id,observed_at DESC);
INSERT INTO schema_migrations(version) VALUES (2);
COMMIT;
