# 실행·저장·인증·뷰어·UI

> 정본에서 생성한 읽기 전용 검토 뷰. 기준 커밋 `197987047ea9a305072bba3fdff816c5c37b0157`. 설계 채택/구현/실서비스 승인 아님.

[검토 홈](README.md) · [AI 인덱스](MANIFEST.json) · [전체 이력](12-HISTORY.md)

## common-integration-v1.json

[고정 JSON 원본](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/common-integration-v1.json) · blob `9df34e576f8a7c63c7ee84d01893a77631ce0360`

### state

- **owner** (`owner`): CO
- **states** (`states`): active · stopping · done · stopped
- **prestart** (`prestart`): job&#95;state=null; ready computed; auth separate view; review only ready + verified + target new + policy; approval atomic at start
- **transition&#95;contract** (`transition_contract`)
  - null · active · exact current scope approved &amp; atomically accepted
  - active · done · trusted goal confirmed and required effects resolved
  - active · stopping · system detected error/condition loss/worker loss
  - stopping · stopped · fence new admission; bounded in-flight observation or unknown; persist terminal result
- **invariants** (`invariants`): No user cancellation, modification, resume or rollback after start. · Auth/viewer close button prestart only; viewer dispose alone never stops. · CO changes job lifecycle; STORE transaction enforces state; EXEC records observations and requests error-stop; RESULT pure verdict; never reopen terminal. · Late trustworthy read-only evidence may refine goal verdict with new evidence, not reopen lifecycle; no rebind/resubmit. · At restart, accepted active job without current worker and unobserved admission: fence and stop, preserve uncertainty; do not auto-resume.
- **revision** (`revision`): Every material prestart scope mutation increments registration revision, invalidates prior review. Persist progress/result with monotonic revision; UI ignores older response. Refresh viewer grant fences old grant without silently changing verified binding. Exact key replay precedes stale check. Start key scoped owner+command, canonical request incl path id; no expiration during job/effect retention.

### storage

- **unit** (`unit`): STORE logical single durable authority, not DB schema; CO owner job transitions; gateway may record admission/observation through shared transactional operations; no callbacks while atomic lock
- **operations** (`operations`)
  - **[0] S-ACCEPT**
    - **ID** (`id`): S-ACCEPT
    - **call** (`call`): accept(owner, registration&#95;id, StartInput, internal Scope) -&gt; RegistrationView or Error
    - **atomic** (`atomic`): authenticate owner, lookup key/hash, compare revision/review/scope/profile/connection/permission and semantic target/effect guard; write immutable scope, key, active job together before dispatch; key conflict/duplicate no new job
  - **[1] S-ADMIT**
    - **ID** (`id`): S-ADMIT
    - **call** (`call`): admit(scoped execution context, Operation) -&gt; one-shot dispatch permit or typed Error
    - **atomic** (`atomic`): compare active state/current lease+permission+profile+target+binding and registry allowed operation; reserve stable logical effect key before external potential mutation. Reads scoped and cannot execute unknown mutating commands. Exclusive one dispatch; confirmed/pending/unknown duplicate deny. Permit never user-visible.
  - **[2] S-OBSERVE**
    - **ID** (`id`): S-OBSERVE
    - **call** (`call`): record scoped Observation + trusted EvidenceRecord&#91;&#93; -&gt; durable observation or Error
    - **atomic** (`atomic`): match admitted operation/lease/registration/target; preserve proof/unknown; dedupe observation IDs, retain prior effects; actual observation only
  - **[3] S-FENCE**
    - **ID** (`id`): S-FENCE
    - **call** (`call`): fence(registration&#95;id, typed Error) -&gt; stopping; finalize(registration&#95;id, Result) -&gt; stopped or done
    - **atomic** (`atomic`): serialize fence with S-ADMIT; no later admissions; pending operation not proven absent becomes unknown, bounded in-flight resolution; CO persists result and terminal state; done only confirmed; no terminal reopen
- **effect&#95;key** (`effect_key`): (environment, platform, external&#95;account&#95;ref, object&#95;kind, stable slot&#95;ref, stable logical&#95;operation&#95;id). Version/request/worker change cannot bypass existing effect. Mock listing slot uses server source lineage + verified account/platform/object and existing effect check; service configuration target includes category. Distinct actual lesson intent requires distinct legitimate slot and evidence; ambiguous cross-source existing/duplicate =&gt; block. Real stable target policy per verified profile. Physical uniqueness/CAS/transaction implementation delegated.

### runtime

- **boundary** (`boundary`): EXEC owns auth/runtime facade and platform adapters; RUNTIME gateway is shared internal boundary, not sixth business role or new HTTP API; VIEWER client is runtime-provided UI adapter
- **calls** (`calls`)
  - **[0] RT-01**
    - **ID** (`id`): RT-01
    - **signature** (`signature`): withVerifiedConnection(AcceptedScope) -&gt; scoped execution context or Error
    - **rule** (`rule`): runtime lookup exact connection&#95;ref/verified&#95;generation/account, acquire exclusive worker lease; no raw driver or credential to adapter; CO-authorized only
  - **[1] RT-02**
    - **ID** (`id`): RT-02
    - **signature** (`signature`): listOperations(scoped context) -&gt; Operation&#91;&#93;
    - **rule** (`rule`): derive stable logical operations from pinned profile, adapter registered operation definitions and accepted values; binding&#95;digest over exact immutable bound values, no ad hoc actions; platform-specific manifest/driver is delegated, registration checks before integration
  - **[2] RT-03**
    - **ID** (`id`): RT-03
    - **signature** (`signature`): perform(scoped context, Operation) -&gt; Observation or typed Error
    - **rule** (`rule`): match registry operation identity/step/effect class/binding&#95;digest; actual args from immutable scope/trusted config, never caller free arguments; effect admission durable before browser command; record real observation and evidence; unknown class treated potentially mutating, unexpected action error-stop
  - **[3] RT-04**
    - **ID** (`id`): RT-04
    - **signature** (`signature`): observeGoal(scoped context) -&gt; GoalObservation or typed Error
    - **rule** (`rule`): scoped registered read-only operation, actual normalized readback/payload digest and trusted evidence; no copy from input; only profile-required method, after fence no new effects; optional late read observation separate from run; no resume
- **viewer** (`viewer`)
  - **ID** (`id`): VIEWER
  - **input** (`input`): AuthGrant (current generation + opaque short-lived grant + expiry)
  - **client&#95;contract** (`client_contract`): runtime provides mount(container, grant) -&gt; dispose() and ready/error/disconnected events; caller only displays allowed authentication viewer and separately invokes H6 finish/close; dispose is UI detach, not job cancellation. Mount rejects expired/stale/foreign grant. Grant protected by service identity, not logged/URL leaked; no raw driver or credentials in UI API.
  - **deferred** (`deferred`): Actual frontend framework/client adapter package path, transport, endpoints, TTL and timeout numbers chosen 11/27 based on evidence; same-origin or secured allowed origin/owner binding verified.

### ui

- **ID** (`id`): UI
- **layout** (`layout`): screen count/layout/design system delegated
- **surfaces** (`surfaces`)
  - source · H1 H2 H3 · raw text/assets, reuse; owner errors; create immutable version on correction
  - prepare · H4 H5 H8 · support, issues/questions, values/source; user answer/correction, reprepare; no start before ready
  - auth · H6 H8 · open/refresh/finish/close prestart; runtime viewer mount; display verified account/target; existing/ambiguous blocked
  - review · H5 H7 H8 · show exact values/assets/provenance/target/profile goal/steps, notice no user rollback/cancel/change after start; approve once with current revision/digest/key; same request key retained across transport retry
  - progress&#95;result · H8 H9 · active/stopping/done/stopped, goal verdict/evidence/next&#95;action, reconnect; no cancel/edit/resume; distinguish mock from actual and unknown from failure
- **presentation** (`presentation`): loading, blocked/unsupported, required questions, stale response recovery via H8, owner errors, unknown explicit; no UI inference of success; HTTP response revision monotonic

