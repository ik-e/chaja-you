#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PGHOST="${PGHOST:-127.0.0.1}" PGPORT="${PGPORT:-5432}" PGUSER="${PGUSER:-postgres}"
echo "candidate=${GITHUB_SHA:-local} utc=$(date -u +%FT%TZ)"
psql -X -v ON_ERROR_STOP=1 -d postgres -c 'SELECT version()'
psql -X -v ON_ERROR_STOP=1 -d postgres -c 'CREATE ROLE submission_app NOLOGIN'
for db in submission_empty submission_seed; do
  createdb "$db"
  psql -X -v ON_ERROR_STOP=1 -d "$db" -f 001_init.sql
  if [[ "$db" == submission_seed ]]; then
    psql -X -v ON_ERROR_STOP=1 -d "$db" -f 003_fixture_v1.sql
    psql -X -At -d "$db" -c "SELECT md5(string_agg(row_to_json(x)::text, ',' ORDER BY x.job_id)) FROM jobs x" > /tmp/submission_before
  fi
  psql -X -v ON_ERROR_STOP=1 -d "$db" -f 002_observation.sql
  psql -X -v ON_ERROR_STOP=1 -d "$db" -c 'GRANT USAGE ON SCHEMA public TO submission_app; GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA public TO submission_app'
  psql -X -v ON_ERROR_STOP=1 -d "$db" <<'SQL'
SET ROLE submission_app;
SELECT current_user, array_agg(version ORDER BY version) FROM schema_migrations;
DO $$
BEGIN
 BEGIN
  INSERT INTO lessons(lesson_id,owner_id,title) VALUES ('00000000-0000-4000-8000-000000009001','00000000-0000-4000-8000-000000009002','invalid owner');
  RAISE EXCEPTION 'FK did not reject';
 EXCEPTION WHEN foreign_key_violation THEN RAISE NOTICE 'expected SQLSTATE 23503: %', SQLSTATE; END;
END $$;
RESET ROLE;
SQL
  echo "$db initialization and role FK PASS"
done
psql -X -At -d submission_seed -c "SELECT md5(string_agg(row_to_json(x)::text, ',' ORDER BY x.job_id)) FROM jobs x" >/tmp/submission_after
diff /tmp/submission_before /tmp/submission_after
psql -X -v ON_ERROR_STOP=1 -d submission_seed -c 'SELECT (SELECT count(*) FROM lessons) AS lessons,(SELECT count(*) FROM jobs) AS jobs,(SELECT count(*) FROM evidence) AS evidence'
psql -X -v ON_ERROR_STOP=1 -d submission_seed -f 004_verify.sql
psql -X -v ON_ERROR_STOP=1 -d submission_seed -f 005_management_verify.sql
echo 'PG-01 PG-02 PG-07 SQL checks PASS; app HTTP/actual effect/backup not tested'
