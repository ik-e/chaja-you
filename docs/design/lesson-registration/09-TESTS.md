# 수용 시험·검증·미확인 사항

> 정본에서 생성한 읽기 전용 검토 뷰. 기준 커밋 `197987047ea9a305072bba3fdff816c5c37b0157`. 설계 채택/구현/실서비스 승인 아님.

[검토 홈](README.md) · [AI 인덱스](MANIFEST.json) · [전체 이력](12-HISTORY.md)

## common-integration-v1.json

[고정 JSON 원본](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/common-integration-v1.json) · blob `9df34e576f8a7c63c7ee84d01893a77631ce0360`

### gate

- **ID** (`id`): GATE
- **required** (`required`): AT-01 · T5-08 · T5-11 · T6-01 · T6-02 · AT-02 · AT-03 · T5-01 · T5-02 · T5-12 · T5-03 · T5-07 · AT-04 · AT-05 · T5-06 · T5-13 · T5-05 · DV-01 · DV-02 · DV-03 · DV-04 · DV-05
- **tests** (`tests`)
  - **[0] AT-01**
    - **ID** (`id`): AT-01
    - **prior** (`prior`)
      - **source** (`source`): wbs-v0.5.json
      - **ID** (`id`): AT-01
    - **요구 참조** (`requirement_refs`): REQ-01 · REQ-03
    - **targets** (`targets`): I2 · H4 · H5
    - **scenario** (`scenario`): unstructured source with exact distinct 250/400/500k, 90/180/270min, month4, VAT unknown, invented free production/notice
    - **기대값** (`expected`): questions and no fabricated fact; no accepted start
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
  - **[1] T5-08**
    - **ID** (`id`): T5-08
    - **prior** (`prior`)
      - **source** (`source`): contract-v0.5.json
      - **ID** (`id`): T5-08
    - **요구 참조** (`requirement_refs`): REQ-01 · REQ-03 · REQ-11
    - **targets** (`targets`): I2 · H4 · H5
    - **scenario** (`scenario`): actual model raw source→facts/mapping, missing and conflicting price/VAT, unavailable model; 3 fixtures incl known/unknown/conflict
    - **기대값** (`expected`): linked source/answer facts; exact units/price/terms; unavailable ready=false; manual stub never AI pass
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `true`
  - **[2] T5-11**
    - **ID** (`id`): T5-11
    - **prior** (`prior`)
      - **source** (`source`): contract-v0.5.json
      - **ID** (`id`): T5-11
    - **요구 참조** (`requirement_refs`): REQ-01 · REQ-03
    - **targets** (`targets`): H1 · H2 · H3 · H4 · H8
    - **scenario** (`scenario`): immutable source create/reuse detail, exact persisted version, path/body injection and other owner
    - **기대값** (`expected`): source/asset identity preserved; server-only review; invalid/other owner denied
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
  - **[3] T6-01**
    - **ID** (`id`): T6-01
    - **prior** (`prior`)
      - **source** (`source`): trace-index-v0.6.json
      - **ID** (`id`): T6-01
    - **요구 참조** (`requirement_refs`): REQ-01 · REQ-10
    - **targets** (`targets`): H1 · H3 · STORE
    - **scenario** (`scenario`): synthetic allowed image, no rights, MIME/size mismatch, foreign reference, missing/extra multipart part
    - **기대값** (`expected`): only authorized valid assets stored/linked, byte hash matches, rejected no external effect
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
  - **[4] T6-02**
    - **ID** (`id`): T6-02
    - **prior** (`prior`)
      - **source** (`source`): trace-index-v0.6.json
      - **ID** (`id`): T6-02
    - **요구 참조** (`requirement_refs`): REQ-03 · REQ-05
    - **targets** (`targets`): H5 · I2 · H7 · STATE
    - **scenario** (`scenario`): valid prestart platform correction, current issue resolved field, stale edit, source fact conflict, source version change, postaccept edit
    - **기대값** (`expected`): normalized answer bound to field, new revision, old review unusable, shared source preserved, postaccept no mutation
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
  - **[5] AT-02**
    - **ID** (`id`): AT-02
    - **prior** (`prior`)
      - **source** (`source`): wbs-v0.5.json
      - **ID** (`id`): AT-02
    - **요구 참조** (`requirement_refs`): REQ-04 · REQ-10
    - **targets** (`targets`): H6 · I3 · I4 · VIEWER · RUNTIME
    - **scenario** (`scenario`): direct mock auth, same context handoff, viewer dispose, other session/old generation, cleanup
    - **기대값** (`expected`): exclusive control, job continues on disconnect, other session denied, no secrets, cleanup
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
  - **[6] AT-03**
    - **ID** (`id`): AT-03
    - **prior** (`prior`)
      - **source** (`source`): wbs-v0.5.json
      - **ID** (`id`): AT-03
    - **요구 참조** (`requirement_refs`): REQ-05 · REQ-10
    - **targets** (`targets`): H7 · I4 · STORE · RUNTIME
    - **scenario** (`scenario`): wrong account, forged approval, permission denied, stale binding, unregistered operation
    - **기대값** (`expected`): zero external mutation
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
  - **[7] T5-01**
    - **ID** (`id`): T5-01
    - **prior** (`prior`)
      - **source** (`source`): contract-v0.5.json
      - **ID** (`id`): T5-01
    - **요구 참조** (`requirement_refs`): REQ-05
    - **targets** (`targets`): H7 · STATE · STORE
    - **scenario** (`scenario`): missing/stale/forged digest or profile, exact current review
    - **기대값** (`expected`): only exact current scope accepted once; invalid cases zero effect
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
  - **[8] T5-02**
    - **ID** (`id`): T5-02
    - **prior** (`prior`)
      - **source** (`source`): contract-v0.5.json
      - **ID** (`id`): T5-02
    - **요구 참조** (`requirement_refs`): REQ-04 · REQ-05
    - **targets** (`targets`): H6 · I3
    - **scenario** (`scenario`): first auth without job/target/account, finish/target resolution, wrong account
    - **기대값** (`expected`): trusted identity before target, verified output includes connection, no fabricated job
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
  - **[9] T5-12**
    - **ID** (`id`): T5-12
    - **prior** (`prior`)
      - **source** (`source`): contract-v0.5.json
      - **ID** (`id`): T5-12
    - **요구 참조** (`requirement_refs`): REQ-05 · REQ-10
    - **targets** (`targets`): I4 · RUNTIME · STORE
    - **scenario** (`scenario`): duplicate operation, wrong binding, unknown action, old lease, error fence race; read steps
    - **기대값** (`expected`): only registered bound action; atomic admission; stale and postfence denied; unknown retained
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
  - **[10] T5-03**
    - **ID** (`id`): T5-03
    - **prior** (`prior`)
      - **source** (`source`): contract-v0.5.json
      - **ID** (`id`): T5-03
    - **요구 참조** (`requirement_refs`): REQ-03 · REQ-04 · REQ-09 · REQ-11
    - **targets** (`targets`): I1 · I2 · I3 · I4 · I5 · INTEGRATION
    - **scenario** (`scenario`): fake providers and then actual adapters conform; valid/invalid typed I/O; shared registry; third synthetic profile
    - **기대값** (`expected`): same contracts; no raw driver bypass; actual adapters required for product pass
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
  - **[11] T5-07**
    - **ID** (`id`): T5-07
    - **prior** (`prior`)
      - **source** (`source`): contract-v0.5.json
      - **ID** (`id`): T5-07
    - **요구 참조** (`requirement_refs`): REQ-02 · REQ-03 · REQ-05
    - **targets** (`targets`): I1 · H4 · H5 · H6 · H7
    - **scenario** (`scenario`): invalid/unsupported/blocked, missing input/auth, ambiguous/existing target
    - **기대값** (`expected`): distinct views/errors; no arbitrary fetch or unapproved start
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
  - **[12] AT-04**
    - **ID** (`id`): AT-04
    - **prior** (`prior`)
      - **source** (`source`): wbs-v0.5.json
      - **ID** (`id`): AT-04
    - **요구 참조** (`requirement_refs`): REQ-06 · REQ-08
    - **targets** (`targets`): I4 · I5 · H7 · H8
    - **scenario** (`scenario`): Kmong synthetic registered profile K1..K7 with exact tiers/values/approved image and independent receipt
    - **기대값** (`expected`): confirmed goal only on matching stored target/payload/image receipt; mock not live
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
  - **[13] AT-05**
    - **ID** (`id`): AT-05
    - **prior** (`prior`)
      - **source** (`source`): wbs-v0.5.json
      - **ID** (`id`): AT-05
    - **요구 참조** (`requirement_refs`): REQ-07 · REQ-08 · REQ-09
    - **targets** (`targets`): I4 · I5 · H7 · H8
    - **scenario** (`scenario`): Soomgo synthetic existing provider S1..S6, selected category/questions, independent saved configuration
    - **기대값** (`expected`): matching stored category and responses; no image/price invented; mock not publication
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
  - **[14] T5-06**
    - **ID** (`id`): T5-06
    - **prior** (`prior`)
      - **source** (`source`): contract-v0.5.json
      - **ID** (`id`): T5-06
    - **요구 참조** (`requirement_refs`): REQ-01 · REQ-06 · REQ-07 · REQ-09
    - **targets** (`targets`): H1 · H4 · H5 · H8 · H9 · STORE
    - **scenario** (`scenario`): one source across two platform requests, platform-local correction or new source version
    - **기대값** (`expected`): independent values/target/approval/results; historical source unchanged
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
  - **[15] T5-13**
    - **ID** (`id`): T5-13
    - **prior** (`prior`)
      - **source** (`source`): contract-v0.5.json
      - **ID** (`id`): T5-13
    - **요구 참조** (`requirement_refs`): REQ-06 · REQ-07 · REQ-09
    - **targets** (`targets`): I1 · I2 · I4 · I5
    - **scenario** (`scenario`): Kmong requires image; Soomgo service configuration has none; independent harness mapping
    - **기대값** (`expected`): platform-specific validation and evidence; no fake shared image or price
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
  - **[16] T5-05**
    - **ID** (`id`): T5-05
    - **prior** (`prior`)
      - **source** (`source`): contract-v0.5.json
      - **ID** (`id`): T5-05
    - **요구 참조** (`requirement_refs`): REQ-08 · REQ-10
    - **targets** (`targets`): H2 · H8 · H9 · UI · STATE
    - **scenario** (`scenario`): close/reconnect UI, owner/nonowner list/detail, active/terminal states
    - **기대값** (`expected`): job remains, owner sees persisted data; other owner 404; no GET mutation
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
  - **[17] DV-01**
    - **ID** (`id`): DV-01
    - **prior** (`prior`)
      - **source** (`source`): detail-gate-v1.json
      - **ID** (`id`): AT-06
    - **요구 참조** (`requirement_refs`): REQ-05 · REQ-08 · REQ-10
    - **targets** (`targets`): H7 · I4 · I5 · STORE · STATE · RUNTIME
    - **scenario** (`scenario`): attachment failure, response lost before/after effect, accepted worker crash; same key replay/conflicting payload/different key same intent
    - **기대값** (`expected`): error-only stop, no later effects; evidence absent/confirmed/unknown separated; no cancel/resume/rollback; identical key same registration
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
  - **[18] DV-02**
    - **ID** (`id`): DV-02
    - **prior** (`prior`)
      - **source** (`source`): detail-gate-v1.json
      - **ID** (`id`): T5-04
    - **요구 참조** (`requirement_refs`): REQ-04 · REQ-05 · REQ-10
    - **targets** (`targets`): H6 · I3 · I4 · RUNTIME · STATE
    - **scenario** (`scenario`): prestart reauth same/different account, same account other binding, stale generation; postaccept auth loss
    - **기대값** (`expected`): old review invalid before start; after accept stop/fence no rebind/resume, no mutation on stale
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
  - **[19] DV-03**
    - **ID** (`id`): DV-03
    - **prior** (`prior`)
      - **source** (`source`): detail-gate-v1.json
      - **ID** (`id`): T5-09
    - **요구 참조** (`requirement_refs`): REQ-06 · REQ-07 · REQ-08 · REQ-10
    - **targets** (`targets`): I5 · H8 · STATE
    - **scenario** (`scenario`): wrong target/payload/image/method, missing trusted evidence; live request
    - **기대값** (`expected`): goal proof only, otherwise stopped/not&#95;reached or unknown; live denied
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
  - **[20] DV-04**
    - **ID** (`id`): DV-04
    - **prior** (`prior`)
      - **source** (`source`): detail-gate-v1.json
      - **ID** (`id`): DV-04
    - **요구 참조** (`requirement_refs`): REQ-03 · REQ-05 · REQ-09
    - **targets** (`targets`): I1 · I4 · I5 · H7 · RUNTIME
    - **scenario** (`scenario`): profile digest changed, unknown step/operation, operation registry binding changed
    - **기대값** (`expected`): pinned profile throughout, prestart deny or error stop, no unapproved new action
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
  - **[21] DV-05**
    - **ID** (`id`): DV-05
    - **prior** (`prior`)
      - **source** (`source`): detail-gate-v1.json
      - **ID** (`id`): DV-05
    - **요구 참조** (`requirement_refs`): REQ-04 · REQ-08 · REQ-10
    - **targets** (`targets`): H6 · H8 · H9 · VIEWER · UI
    - **scenario** (`scenario`): owner reconnect after approval, viewer grant stale, nonowner lookup, UI closes
    - **기대값** (`expected`): stored approved values/result, stale input denied, job independent, no secret leakage
    - **observables** (`observables`): exact input/candidate/version · response/state and permitted external mutation count · trusted observation/evidence or explicit absence/unknown
    - **verdict** (`verdict`): pass iff all expected assertions observed; fail on violated assertion; incomplete if required observation absent
    - **실행** (`execution`): not&#95;run
    - **actual&#95;model&#95;required** (`actual_model_required`): `false`
- **environment** (`environment`): mock
- **execution&#95;kind** (`execution_kind`): integrated&#95;product
- **candidate&#95;fields** (`candidate_fields`): build&#95;sha · contract&#95;digest · fixture&#95;digest · environment
- **actual&#95;model&#95;test&#95;refs** (`actual_model_test_refs`): T5-08
- **completion** (`completion`): All required tests pass for exact candidate and execution&#95;kind; any fail fail, missing/inconclusive incomplete. Actual&#95;model flag for T5-08. No mock/live conflation. Existing independent T1~T6 unchanged; map evidence only after conformance, not substitute for integrated product gate.
- **final&#95;tests** (`final_tests`)
  - **[0] AT-07**
    - **ID** (`id`): AT-07
    - **요구 참조** (`requirement_refs`): REQ-02 · REQ-09 · REQ-10
    - **scenario** (`scenario`): 지원 홈/등록 URL, 미지원/내부망/redirect
    - **기대값** (`expected`): registry match, 무단 fetch 0, 적합 adapter
    - **stage** (`stage`): FINAL
    - **실행** (`execution`): not&#95;run
  - **[1] AT-08**
    - **ID** (`id`): AT-08
    - **요구 참조** (`requirement_refs`): REQ-04 · REQ-05 · REQ-08 · REQ-10
    - **scenario** (`scenario`): crash/error fence/old lease/concurrent control/isolation
    - **기대값** (`expected`): no subsequent admission, durable unknown, isolation/disposal; no user cancel/resume
    - **stage** (`stage`): FINAL
    - **실행** (`execution`): not&#95;run
  - **[2] AT-09**
    - **ID** (`id`): AT-09
    - **요구 참조** (`requirement_refs`): REQ-01 · REQ-03 · REQ-11
    - **scenario** (`scenario`): A/B/C 동일 목표 업무 비교
    - **기대값** (`expected`): 활동 시간·오류·개입·비용/대기 분리, 실패 포함
    - **stage** (`stage`): FINAL
    - **실행** (`execution`): not&#95;run
  - **[3] AT-10**
    - **ID** (`id`): AT-10
    - **요구 참조** (`requirement_refs`): REQ-02 · REQ-06 · REQ-07 · REQ-08 · REQ-09
    - **scenario** (`scenario`): 지원 URL 입력→최초 등록→결과
    - **기대값** (`expected`): 각 지원 플랫폼 목표/증거 일치; 미지원 차단; actual 권한 없으면 mock only
    - **stage** (`stage`): FINAL
    - **실행** (`execution`): not&#95;run
- **실행** (`execution`): not&#95;run

## common-integration-validation-v1.json

[고정 JSON 원본](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/common-integration-validation-v1.json) · blob `f13c2a658e285408a5d9138c86724057a16e9102`

### source_commit

- 485290a694a05db514855741d8d249a669507a10

### inputs

- **common** (`common`): 9df34e576f8a7c63c7ee84d01893a77631ce0360
- **trace** (`trace`): 987018e3e41f15521de6ba2fef33867cea81a88d
- **schema** (`schema`): de6c147216ee68bae75a9d18f9127c327701fa5a
- **profiles** (`profiles`): b0b2044526f63f0244d920f85b2d9676b94bbe72
- **gate** (`gate`): 55c66d285183fb4a8a12041b883c12e7775d12f7
- **wbs** (`wbs`): 5203828cc220187ec53d1602579b9e12ab1cf5d0
- **shape** (`shape`): 1d49665ea105450c87b97a6a7cd6f72aec869321
- **data** (`data`): 2484c5df659962145af1ee2d94dd36d1f41e5f6f
- **closure** (`closure`): ec9e1b21c139b8f9115b1661596d0f385cba1b12
- **general** (`general`): bdb4c90b3f699432343a0c8a3c77f668dc050546

### checks

#### COMMON-01 type and route references

- **ID** (`id`): COMMON-01 type and route references
- **pass** (`pass`): `true`
- **detail** (`detail`)
  - **definitions** (`definitions`): `67`
  - **references** (`references`): `224`
  - **unresolved** (`unresolved`): `[]`
  - **unsupported&#95;keywords** (`unsupported_keywords`): `[]`
  - **route&#95;missing** (`route_missing`): `[]`
  - **port&#95;missing** (`port_missing`): `[]`
  - **duplicate&#95;routes** (`duplicate_routes`): `0`
  - **root&#95;has&#95;validation** (`root_has_validation`): `false`

#### COMMON-02 profile schema and bindings

- **ID** (`id`): COMMON-02 profile schema and bindings
- **pass** (`pass`): `true`
- **detail** (`detail`): `null`

#### COMMON-03 logical dependency DAG

- **ID** (`id`): COMMON-03 logical dependency DAG
- **pass** (`pass`): `true`
- **detail** (`detail`): `[]`

#### COMMON-04 error vocabulary

- **ID** (`id`): COMMON-04 error vocabulary
- **pass** (`pass`): `true`
- **detail** (`detail`): `null`

#### COMMON-05 decision IDs and original locators

- **ID** (`id`): COMMON-05 decision IDs and original locators
- **pass** (`pass`): `true`
- **detail** (`detail`): `null`

#### COMMON-06 IT-19 required fields and prior refs

- **ID** (`id`): COMMON-06 IT-19 required fields and prior refs
- **pass** (`pass`): `true`
- **detail** (`detail`): `null`

#### COMMON-07 decision projection

- **ID** (`id`): COMMON-07 decision projection
- **pass** (`pass`): `true`
- **detail** (`detail`): `null`

#### COMMON-08 requirement and interface coverage

- **ID** (`id`): COMMON-08 requirement and interface coverage
- **pass** (`pass`): `true`
- **detail** (`detail`): `null`

#### COMMON-09 original product gate inventory

- **ID** (`id`): COMMON-09 original product gate inventory
- **pass** (`pass`): `true`
- **detail** (`detail`): `null`

#### COMMON-10 current lifecycle boundary

- **ID** (`id`): COMMON-10 current lifecycle boundary
- **pass** (`pass`): `true`
- **detail** (`detail`): `null`

#### COMMON-11 mock and physical limits

- **ID** (`id`): COMMON-11 mock and physical limits
- **pass** (`pass`): `true`
- **detail** (`detail`): `null`

#### COMMON-12 V4 selected synthetic regression

- **ID** (`id`): COMMON-12 V4 selected synthetic regression
- **pass** (`pass`): `true`
- **detail** (`detail`)
  - **passed** (`passed`): `31`
  - **total** (`total`): `31`

#### COMMON-13 V4.1 field correction and normalized answer shapes

- **ID** (`id`): COMMON-13 V4.1 field correction and normalized answer shapes
- **pass** (`pass`): `true`
- **detail** (`detail`)
  - **[0] **
    - **type** (`type`): PreparationEdit
    - **기대값** (`expected`): `true`
    - **actual** (`actual`): `true`
  - **[1] **
    - **type** (`type`): PreparationEdit
    - **기대값** (`expected`): `false`
    - **actual** (`actual`): `false`
  - **[2] **
    - **type** (`type`): PreparationEdit
    - **기대값** (`expected`): `false`
    - **actual** (`actual`): `false`
  - **[3] **
    - **type** (`type`): ResolvedAnswer
    - **기대값** (`expected`): `true`
    - **actual** (`actual`): `true`
  - **[4] **
    - **type** (`type`): ResolvedAnswer
    - **기대값** (`expected`): `false`
    - **actual** (`actual`): `false`
  - **[5] **
    - **type** (`type`): ResolvedAnswer
    - **기대값** (`expected`): `true`
    - **actual** (`actual`): `true`
  - **[6] **
    - **type** (`type`): StartInput
    - **기대값** (`expected`): `true`
    - **actual** (`actual`): `true`

#### COMMON-14 gate evaluator counterexamples

- **ID** (`id`): COMMON-14 gate evaluator counterexamples
- **pass** (`pass`): `true`
- **detail** (`detail`)
  - **[0] same&#95;candidate&#95;all&#95;pass**
    - **ID** (`id`): same&#95;candidate&#95;all&#95;pass
    - **기대값** (`expected`): pass
    - **actual** (`actual`): pass
  - **[1] missing&#95;case**
    - **ID** (`id`): missing&#95;case
    - **기대값** (`expected`): incomplete
    - **actual** (`actual`): incomplete
  - **[2] wrong&#95;candidate**
    - **ID** (`id`): wrong&#95;candidate
    - **기대값** (`expected`): incomplete
    - **actual** (`actual`): incomplete
  - **[3] failure&#95;not&#95;hidden**
    - **ID** (`id`): failure&#95;not&#95;hidden
    - **기대값** (`expected`): fail
    - **actual** (`actual`): fail
  - **[4] manual&#95;stub&#95;not&#95;ai**
    - **ID** (`id`): manual&#95;stub&#95;not&#95;ai
    - **기대값** (`expected`): incomplete
    - **actual** (`actual`): incomplete
  - **[5] independent&#95;harness&#95;not&#95;integrated**
    - **ID** (`id`): independent&#95;harness&#95;not&#95;integrated
    - **기대값** (`expected`): incomplete
    - **actual** (`actual`): incomplete

### regression

#### K-valid

- **ID** (`id`): K-valid
- **기대값** (`expected`): `true`
- **actual** (`actual`): `true`
- **pass** (`pass`): `true`
- **errors** (`errors`): `[]`

#### S-valid

- **ID** (`id`): S-valid
- **기대값** (`expected`): `true`
- **actual** (`actual`): `true`
- **pass** (`pass`): `true`
- **errors** (`errors`): `[]`

#### K-region-required

- **ID** (`id`): K-region-required
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): offline region missing

#### K-image-rights

- **ID** (`id`): K-image-rights
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): asset rights or scope mismatch

#### K-package-fields

- **ID** (`id`): K-package-fields
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): $.packages&#91;0&#93;.work&#95;days required · $.packages&#91;1&#93;.work&#95;days required · $.packages&#91;2&#93;.work&#95;days required

#### K-package-tiers

- **ID** (`id`): K-package-tiers
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): tier mismatch

#### K-option

- **ID** (`id`): K-option
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): unknown option minutes&#95;per&#95;session · unknown option minutes&#95;per&#95;session · unknown option minutes&#95;per&#95;session

#### S-no-image

- **ID** (`id`): S-no-image
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): $.main&#95;images additional

#### S-no-invalid-option

- **ID** (`id`): S-no-invalid-option
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): $.daw&#91;0&#93; enum

#### PREP-valid

- **ID** (`id`): PREP-valid
- **기대값** (`expected`): `true`
- **actual** (`actual`): `true`
- **pass** (`pass`): `true`
- **errors** (`errors`): `[]`

#### PREP-VAT-unknown

- **ID** (`id`): PREP-VAT-unknown
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): commercial mismatch or VAT unknown 0 · incorrect ready

#### PREP-price-changed

- **ID** (`id`): PREP-price-changed
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): commercial mismatch or VAT unknown 0 · incorrect ready

#### PREP-work-days-invented

- **ID** (`id`): PREP-work-days-invented
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): missing package option evidence 0 · missing package option evidence 1 · missing package option evidence 2 · incorrect ready

#### PREP-conflict-ready

- **ID** (`id`): PREP-conflict-ready
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): incorrect ready

#### PREP-unlinked-fact

- **ID** (`id`): PREP-unlinked-fact
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): invalid mapping · incorrect ready

#### AUTH-valid

- **ID** (`id`): AUTH-valid
- **기대값** (`expected`): `true`
- **actual** (`actual`): `true`
- **pass** (`pass`): `true`
- **errors** (`errors`): `[]`

#### AUTH-no-connection

- **ID** (`id`): AUTH-no-connection
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): $ oneOf

#### AUTH-other-connection-same-account

- **ID** (`id`): AUTH-other-connection-same-account
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): connection/target/generation mismatch

#### AUTH-stale-generation

- **ID** (`id`): AUTH-stale-generation
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): connection/target/generation mismatch

#### AUTH-execute-single-pinned-scope

- **ID** (`id`): AUTH-execute-single-pinned-scope
- **기대값** (`expected`): `true`
- **actual** (`actual`): `true`
- **pass** (`pass`): `true`
- **errors** (`errors`): `[]`

#### AUTH-execute-override-denied

- **ID** (`id`): AUTH-execute-override-denied
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): $.connection additional

#### GOAL-valid

- **ID** (`id`): GOAL-valid
- **기대값** (`expected`): `true`
- **actual** (`actual`): `true`
- **pass** (`pass`): `true`
- **errors** (`errors`): `[]`

#### GOAL-submission-only

- **ID** (`id`): GOAL-submission-only
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): goal mismatch · unlinked goal evidence

#### GOAL-wrong-target

- **ID** (`id`): GOAL-wrong-target
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): goal mismatch · unlinked goal evidence

#### GOAL-no-trusted-evidence

- **ID** (`id`): GOAL-no-trusted-evidence
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): unlinked goal evidence

#### GOAL-wrong-asset

- **ID** (`id`): GOAL-wrong-asset
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): asset proof mismatch · unlinked goal evidence

#### GOAL-unresolved-effect

- **ID** (`id`): GOAL-unresolved-effect
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): error or unresolved effect · step not proven K6

#### GOAL-missing-step

- **ID** (`id`): GOAL-missing-step
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): step not proven K1

#### EXT-open-platform-id

- **ID** (`id`): EXT-open-platform-id
- **기대값** (`expected`): `true`
- **actual** (`actual`): `true`
- **pass** (`pass`): `true`
- **errors** (`errors`): `[]`

#### EXT-separate-profile

- **ID** (`id`): EXT-separate-profile
- **기대값** (`expected`): `true`
- **actual** (`actual`): `true`
- **pass** (`pass`): `true`
- **errors** (`errors`): `[]`

#### EXT-mock-only

- **ID** (`id`): EXT-mock-only
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): $.environment const

### shapes

- **[0] **
  - **type** (`type`): PreparationEdit
  - **기대값** (`expected`): `true`
  - **actual** (`actual`): `true`
- **[1] **
  - **type** (`type`): PreparationEdit
  - **기대값** (`expected`): `false`
  - **actual** (`actual`): `false`
- **[2] **
  - **type** (`type`): PreparationEdit
  - **기대값** (`expected`): `false`
  - **actual** (`actual`): `false`
- **[3] **
  - **type** (`type`): ResolvedAnswer
  - **기대값** (`expected`): `true`
  - **actual** (`actual`): `true`
- **[4] **
  - **type** (`type`): ResolvedAnswer
  - **기대값** (`expected`): `false`
  - **actual** (`actual`): `false`
- **[5] **
  - **type** (`type`): ResolvedAnswer
  - **기대값** (`expected`): `true`
  - **actual** (`actual`): `true`
- **[6] **
  - **type** (`type`): StartInput
  - **기대값** (`expected`): `true`
  - **actual** (`actual`): `true`

### gate_cases

#### same&#95;candidate&#95;all&#95;pass

- **ID** (`id`): same&#95;candidate&#95;all&#95;pass
- **기대값** (`expected`): pass
- **actual** (`actual`): pass

#### missing&#95;case

- **ID** (`id`): missing&#95;case
- **기대값** (`expected`): incomplete
- **actual** (`actual`): incomplete

#### wrong&#95;candidate

- **ID** (`id`): wrong&#95;candidate
- **기대값** (`expected`): incomplete
- **actual** (`actual`): incomplete

#### failure&#95;not&#95;hidden

- **ID** (`id`): failure&#95;not&#95;hidden
- **기대값** (`expected`): fail
- **actual** (`actual`): fail

#### manual&#95;stub&#95;not&#95;ai

- **ID** (`id`): manual&#95;stub&#95;not&#95;ai
- **기대값** (`expected`): incomplete
- **actual** (`actual`): incomplete

#### independent&#95;harness&#95;not&#95;integrated

- **ID** (`id`): independent&#95;harness&#95;not&#95;integrated
- **기대값** (`expected`): incomplete
- **actual** (`actual`): incomplete

### pass

- `true`

### mutations

#### drop&#95;test

- **ID** (`id`): drop&#95;test
- **detected** (`detected`): `true`
- **failed** (`failed`): COMMON-06 IT-19 required fields and prior refs · COMMON-08 requirement and interface coverage · COMMON-09 original product gate inventory

#### unknown&#95;prior

- **ID** (`id`): unknown&#95;prior
- **detected** (`detected`): `true`
- **failed** (`failed`): COMMON-06 IT-19 required fields and prior refs · COMMON-07 decision projection

#### unknown&#95;source

- **ID** (`id`): unknown&#95;source
- **detected** (`detected`): `true`
- **failed** (`failed`): COMMON-06 IT-19 required fields and prior refs · COMMON-07 decision projection

#### cycle&#95;dependency

- **ID** (`id`): cycle&#95;dependency
- **detected** (`detected`): `true`
- **failed** (`failed`): COMMON-03 logical dependency DAG

#### reintroduce&#95;resume

- **ID** (`id`): reintroduce&#95;resume
- **detected** (`detected`): `true`
- **failed** (`failed`): COMMON-08 requirement and interface coverage · COMMON-10 current lifecycle boundary

#### unmapped&#95;work

- **ID** (`id`): unmapped&#95;work
- **detected** (`detected`): `true`
- **failed** (`failed`): COMMON-07 decision projection

### limits

- Executed JS subset schema checker and existing logical composition/gate validators in code mode; not an independent standards-complete JSON Schema validator or a GitHub Actions run.
- 31 V4 synthetic regression checks passed on V4.1 types; 7 additional shape checks do not prove full H5 normalization/corrections behavior.
- Synthetic gate evaluator inputs are not actual product results. Product 22 tests still not run.
- Source blob and original locator verification are separate checks; no physical DB/HTTP/runtime or actual model tests.

## data-contract-validation-v4.json

[고정 JSON 원본](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/data-contract-validation-v4.json) · blob `0710bcf3676e23712e5d02d749e74d8cf47f9a6e`

### source_commit

- 1e865d32d5624c4c73c06f07aaa0347e8b0a7ca9

### source_blobs

- **[0] **
  - **path** (`path`): data-schema-v4.json
  - **sha** (`sha`): 772b29eed0ac4dbf60229f833a0064cb8ad65c14
- **[1] **
  - **path** (`path`): platform-profiles-v2.json
  - **sha** (`sha`): b0b2044526f63f0244d920f85b2d9676b94bbe72
- **[2] **
  - **path** (`path`): data-contract-v4.json
  - **sha** (`sha`): a5989cbe586237432a5dbb7081c0f80b2bc98d99
- **[3] **
  - **path** (`path`): validate-interface-review-v3.mjs
  - **sha** (`sha`): 1d49665ea105450c87b97a6a7cd6f72aec869321
- **[4] **
  - **path** (`path`): logical-behavior-v5.json
  - **sha** (`sha`): 2c13b86a44b10f7877678509819e97d1d1b72c17
- **[5] **
  - **path** (`path`): validate-logical-v5.mjs
  - **sha** (`sha`): 660dd54af6cf7d2db72da25d724b728b00f1c550

### audit

- **definitions** (`definitions`): `65`
- **references** (`references`): `217`
- **unresolved** (`unresolved`): `[]`
- **unsupported&#95;keywords** (`unsupported_keywords`): `[]`
- **route&#95;missing** (`route_missing`): `[]`
- **port&#95;missing** (`port_missing`): `[]`
- **duplicate&#95;routes** (`duplicate_routes`): `0`
- **root&#95;has&#95;validation** (`root_has_validation`): `false`

### profileAudits

#### kmong.service&#95;listing.mock.v2

- **ID** (`id`): kmong.service&#95;listing.mock.v2
- **errors** (`errors`): `[]`
- **definitions** (`definitions`): `68`
- **references** (`references`): `225`
- **unresolved** (`unresolved`): `[]`
- **unsupported&#95;keywords** (`unsupported_keywords`): `[]`
- **route&#95;missing** (`route_missing`): `[]`
- **port&#95;missing** (`port_missing`): `[]`
- **duplicate&#95;routes** (`duplicate_routes`): `0`
- **root&#95;has&#95;validation** (`root_has_validation`): `false`

#### soomgo.service&#95;configuration.mock.v2

- **ID** (`id`): soomgo.service&#95;configuration.mock.v2
- **errors** (`errors`): `[]`
- **definitions** (`definitions`): `66`
- **references** (`references`): `217`
- **unresolved** (`unresolved`): `[]`
- **unsupported&#95;keywords** (`unsupported_keywords`): `[]`
- **route&#95;missing** (`route_missing`): `[]`
- **port&#95;missing** (`port_missing`): `[]`
- **duplicate&#95;routes** (`duplicate_routes`): `0`
- **root&#95;has&#95;validation** (`root_has_validation`): `false`

### cases

#### K-valid

- **ID** (`id`): K-valid
- **기대값** (`expected`): `true`
- **actual** (`actual`): `true`
- **pass** (`pass`): `true`
- **errors** (`errors`): `[]`

#### S-valid

- **ID** (`id`): S-valid
- **기대값** (`expected`): `true`
- **actual** (`actual`): `true`
- **pass** (`pass`): `true`
- **errors** (`errors`): `[]`

#### K-region-required

- **ID** (`id`): K-region-required
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): offline region missing

#### K-image-rights

- **ID** (`id`): K-image-rights
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): asset rights or scope mismatch

#### K-package-fields

- **ID** (`id`): K-package-fields
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): $.packages&#91;0&#93;.work&#95;days required · $.packages&#91;1&#93;.work&#95;days required · $.packages&#91;2&#93;.work&#95;days required

#### K-package-tiers

- **ID** (`id`): K-package-tiers
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): tier mismatch

#### K-option

- **ID** (`id`): K-option
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): unknown option minutes&#95;per&#95;session · unknown option minutes&#95;per&#95;session · unknown option minutes&#95;per&#95;session

#### S-no-image

- **ID** (`id`): S-no-image
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): $.main&#95;images additional

#### S-no-invalid-option

- **ID** (`id`): S-no-invalid-option
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): $.daw&#91;0&#93; enum

#### PREP-valid

- **ID** (`id`): PREP-valid
- **기대값** (`expected`): `true`
- **actual** (`actual`): `true`
- **pass** (`pass`): `true`
- **errors** (`errors`): `[]`

#### PREP-VAT-unknown

- **ID** (`id`): PREP-VAT-unknown
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): commercial mismatch or VAT unknown 0 · incorrect ready

#### PREP-price-changed

- **ID** (`id`): PREP-price-changed
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): commercial mismatch or VAT unknown 0 · incorrect ready

#### PREP-work-days-invented

- **ID** (`id`): PREP-work-days-invented
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): missing package option evidence 0 · missing package option evidence 1 · missing package option evidence 2 · incorrect ready

#### PREP-conflict-ready

- **ID** (`id`): PREP-conflict-ready
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): incorrect ready

#### PREP-unlinked-fact

- **ID** (`id`): PREP-unlinked-fact
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): invalid mapping · incorrect ready

#### AUTH-valid

- **ID** (`id`): AUTH-valid
- **기대값** (`expected`): `true`
- **actual** (`actual`): `true`
- **pass** (`pass`): `true`
- **errors** (`errors`): `[]`

#### AUTH-no-connection

- **ID** (`id`): AUTH-no-connection
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): $ oneOf

#### AUTH-other-connection-same-account

- **ID** (`id`): AUTH-other-connection-same-account
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): connection/target/generation mismatch

#### AUTH-stale-generation

- **ID** (`id`): AUTH-stale-generation
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): connection/target/generation mismatch

#### AUTH-execute-single-pinned-scope

- **ID** (`id`): AUTH-execute-single-pinned-scope
- **기대값** (`expected`): `true`
- **actual** (`actual`): `true`
- **pass** (`pass`): `true`
- **errors** (`errors`): `[]`

#### AUTH-execute-override-denied

- **ID** (`id`): AUTH-execute-override-denied
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): $.connection additional

#### GOAL-valid

- **ID** (`id`): GOAL-valid
- **기대값** (`expected`): `true`
- **actual** (`actual`): `true`
- **pass** (`pass`): `true`
- **errors** (`errors`): `[]`

#### GOAL-submission-only

- **ID** (`id`): GOAL-submission-only
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): goal mismatch · unlinked goal evidence

#### GOAL-wrong-target

- **ID** (`id`): GOAL-wrong-target
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): goal mismatch · unlinked goal evidence

#### GOAL-no-trusted-evidence

- **ID** (`id`): GOAL-no-trusted-evidence
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): unlinked goal evidence

#### GOAL-wrong-asset

- **ID** (`id`): GOAL-wrong-asset
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): asset proof mismatch · unlinked goal evidence

#### GOAL-unresolved-effect

- **ID** (`id`): GOAL-unresolved-effect
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): error or unresolved effect · step not proven K6

#### GOAL-missing-step

- **ID** (`id`): GOAL-missing-step
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): step not proven K1

#### EXT-open-platform-id

- **ID** (`id`): EXT-open-platform-id
- **기대값** (`expected`): `true`
- **actual** (`actual`): `true`
- **pass** (`pass`): `true`
- **errors** (`errors`): `[]`

#### EXT-separate-profile

- **ID** (`id`): EXT-separate-profile
- **기대값** (`expected`): `true`
- **actual** (`actual`): `true`
- **pass** (`pass`): `true`
- **errors** (`errors`): `[]`

#### EXT-mock-only

- **ID** (`id`): EXT-mock-only
- **기대값** (`expected`): `false`
- **actual** (`actual`): `false`
- **pass** (`pass`): `true`
- **errors** (`errors`): $.environment const

### logic

- **[0] **
  - **N** (`N`): `4`
  - **states** (`states`): `53`
  - **edges** (`edges`): `134`
  - **violations** (`violations`): `0`
  - **unused** (`unused`): `[]`
  - **no&#95;outcome** (`no_outcome`): `0`
- **[1] **
  - **N** (`N`): `5`
  - **states** (`states`): `61`
  - **edges** (`edges`): `142`
  - **violations** (`violations`): `0`
  - **unused** (`unused`): `[]`
  - **no&#95;outcome** (`no_outcome`): `0`
- **[2] **
  - **N** (`N`): `6`
  - **states** (`states`): `69`
  - **edges** (`edges`): `150`
  - **violations** (`violations`): `0`
  - **unused** (`unused`): `[]`
  - **no&#95;outcome** (`no_outcome`): `0`
- **[3] **
  - **N** (`N`): `7`
  - **states** (`states`): `77`
  - **edges** (`edges`): `158`
  - **violations** (`violations`): `0`
  - **unused** (`unused`): `[]`
  - **no&#95;outcome** (`no_outcome`): `0`

### limitations

- Subset JS shape checker, not standard JSON Schema engine.
- Semantic sample checks use synthetic fixtures, trusted origin/evidence lists and expected payload digest supplied by test. Not actual extraction/provenance proof, digest generation, registry selection, database concurrency, runtime permission/session enforcement or real browser execution.
- Third platform synthetic sample demonstrates shape/profile extension only, not actual adapter support.
- Logical model remains abstract, N=6/7 also examined; actual runtime tests not run.

## logical-validation-v5.json

[고정 JSON 원본](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/logical-validation-v5.json) · blob `230505b72eb301175b09c5d1262ca828544e5b71`

### results

- **[0] **
  - **N** (`N`): `4`
  - **states** (`states`): `53`
  - **edges** (`edges`): `134`
  - **unused** (`unused`): `[]`
  - **violations** (`violations`): `[]`
  - **no&#95;outcome** (`no_outcome`): `0`
  - **normal&#95;path** (`normal_path`): source&#95;select · select&#95;supported · prepare&#95;ready · auth&#95;open · auth&#95;finish · target&#95;new · make&#95;review · accept · worker · admit · operation&#95;proven · admit · operation&#95;proven · admit · operation&#95;proven · admit · operation&#95;proven · goal&#95;proven
  - **unknown&#95;stop&#95;path** (`unknown_stop_path`): source&#95;select · select&#95;supported · prepare&#95;ready · auth&#95;open · auth&#95;finish · target&#95;new · make&#95;review · accept · worker · admit · error&#95;detected · finish&#95;stop&#95;pending
- **[1] **
  - **N** (`N`): `5`
  - **states** (`states`): `61`
  - **edges** (`edges`): `142`
  - **unused** (`unused`): `[]`
  - **violations** (`violations`): `[]`
  - **no&#95;outcome** (`no_outcome`): `0`
  - **normal&#95;path** (`normal_path`): source&#95;select · select&#95;supported · prepare&#95;ready · auth&#95;open · auth&#95;finish · target&#95;new · make&#95;review · accept · worker · admit · operation&#95;proven · admit · operation&#95;proven · admit · operation&#95;proven · admit · operation&#95;proven · admit · operation&#95;proven · goal&#95;proven
  - **unknown&#95;stop&#95;path** (`unknown_stop_path`): source&#95;select · select&#95;supported · prepare&#95;ready · auth&#95;open · auth&#95;finish · target&#95;new · make&#95;review · accept · worker · admit · error&#95;detected · finish&#95;stop&#95;pending

### mutations

- **[0] **
  - **name** (`name`): user cancel
  - **detected** (`detected`): `true`
- **[1] **
  - **name** (`name`): remove review reset
  - **detected** (`detected`): `true`
- **[2] **
  - **name** (`name`): lost pending effect
  - **detected** (`detected`): `true`
- **[3] **
  - **name** (`name`): reopen stopped
  - **detected** (`detected`): `true`
- **[4] **
  - **name** (`name`): unreviewed start
  - **detected** (`detected`): `true`
- **[5] **
  - **name** (`name`): duplicate attempt
  - **detected** (`detected`): `true`

### scope

- finite abstract model, trusted event assumptions; product not run

