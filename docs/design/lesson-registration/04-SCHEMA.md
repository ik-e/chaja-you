# 공통 타입과 스키마 V4.1

> 정본에서 생성한 읽기 전용 검토 뷰. 기준 커밋 `197987047ea9a305072bba3fdff816c5c37b0157`. 설계 채택/구현/실서비스 승인 아님.

[검토 홈](README.md) · [AI 인덱스](MANIFEST.json) · [전체 이력](12-HISTORY.md)

## data-schema-v4.1.json

[고정 JSON 원본](https://github.com/ik-e/chaja-you/blob/197987047ea9a305072bba3fdff816c5c37b0157/docs/artifacts/design/lesson-registration-20261124/data-schema-v4.1.json) · blob `de6c147216ee68bae75a9d18f9127c327701fa5a`

### $schema

- https://json-schema.org/draft/2020-12/schema

### $id

- urn:chaja-you:lesson-registration:common-data:v4.1

### title

- Common data contract V4.1 — minimal integration baseline, mock only

### description

- Select an explicit $defs entry at the boundary. Platform schemas are independently registered and use common definitions; validating the document root alone is not a data check.

### $defs

#### Id

- **type** (`type`): string
- **minLength** (`minLength`): `1`
- **maxLength** (`maxLength`): `256`

#### Text

- **type** (`type`): string
- **minLength** (`minLength`): `1`

#### Revision

- **type** (`type`): integer
- **minimum** (`minimum`): `0`
- **maximum** (`maximum`): `9007199254740991`

#### Digest

- **type** (`type`): string
- **pattern** (`pattern`): ^&#91;a-f0-9&#93;{64}$

#### Timestamp

- **type** (`type`): string
- **format** (`format`): date-time

#### Environment

- **const** (`const`): mock

#### JobState

- **enum** (`enum`): active · stopping · done · stopped

#### GoalVerdict

- **enum** (`enum`): confirmed · not&#95;reached · unknown

#### ProfileRef

- **type** (`type`): object
- **properties** (`properties`)
  - **platform** (`platform`)
    - **$ref** (`$ref`): #/$defs/PlatformId
  - **object&#95;kind** (`object_kind`)
    - **$ref** (`$ref`): #/$defs/Id
  - **version** (`version`)
    - **$ref** (`$ref`): #/$defs/Id
  - **digest** (`digest`)
    - **$ref** (`$ref`): #/$defs/Digest
  - **environment** (`environment`)
    - **$ref** (`$ref`): #/$defs/Environment
- **required** (`required`): platform · object&#95;kind · version · digest · environment
- **additionalProperties** (`additionalProperties`): `false`

#### Value

- **anyOf** (`anyOf`)
  - **[0] **
    - **type** (`type`): null
  - **[1] **
    - **type** (`type`): boolean
  - **[2] **
    - **type** (`type`): integer
    - **minimum** (`minimum`): `-9007199254740991`
    - **maximum** (`maximum`): `9007199254740991`
  - **[3] **
    - **type** (`type`): string
  - **[4] **
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Value
    - **minItems** (`minItems`): `0`
  - **[5] **
    - **type** (`type`): object
    - **additionalProperties** (`additionalProperties`)
      - **$ref** (`$ref`): #/$defs/Value

#### Values

- **type** (`type`): object
- **additionalProperties** (`additionalProperties`)
  - **$ref** (`$ref`): #/$defs/Value

#### AssetInput

- **type** (`type`): object
- **properties** (`properties`)
  - **part&#95;name** (`part_name`)
    - **$ref** (`$ref`): #/$defs/Id
  - **rights&#95;confirmed** (`rights_confirmed`)
    - **type** (`type`): boolean
- **required** (`required`): part&#95;name · rights&#95;confirmed
- **additionalProperties** (`additionalProperties`): `false`

#### AssetRef

- **type** (`type`): object
- **properties** (`properties`)
  - **asset&#95;id** (`asset_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **digest** (`digest`)
    - **$ref** (`$ref`): #/$defs/Digest
  - **mime** (`mime`)
    - **enum** (`enum`): image/png · image/jpeg
  - **bytes** (`bytes`)
    - **type** (`type`): integer
    - **minimum** (`minimum`): `1`
  - **width** (`width`)
    - **type** (`type`): integer
    - **minimum** (`minimum`): `1`
  - **height** (`height`)
    - **type** (`type`): integer
    - **minimum** (`minimum`): `1`
  - **rights&#95;confirmed** (`rights_confirmed`)
    - **type** (`type`): boolean
- **required** (`required`): asset&#95;id · digest · mime · bytes · width · height · rights&#95;confirmed
- **additionalProperties** (`additionalProperties`): `false`

#### SourceInput

- **type** (`type`): object
- **properties** (`properties`)
  - **raw&#95;text** (`raw_text`)
    - **type** (`type`): string
    - **minLength** (`minLength`): `0`
  - **previous&#95;source&#95;id** (`previous_source_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **reuse&#95;asset&#95;ids** (`reuse_asset_ids`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Id
    - **minItems** (`minItems`): `0`
    - **uniqueItems** (`uniqueItems`): `true`
  - **new&#95;assets** (`new_assets`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/AssetInput
    - **minItems** (`minItems`): `0`
- **required** (`required`): raw&#95;text
- **additionalProperties** (`additionalProperties`): `false`

#### SourceView

- **type** (`type`): object
- **properties** (`properties`)
  - **source&#95;id** (`source_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **previous&#95;source&#95;id** (`previous_source_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **raw&#95;text** (`raw_text`)
    - **type** (`type`): string
    - **minLength** (`minLength`): `0`
  - **asset&#95;refs** (`asset_refs`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/AssetRef
    - **minItems** (`minItems`): `0`
  - **created&#95;at** (`created_at`)
    - **$ref** (`$ref`): #/$defs/Timestamp
- **required** (`required`): source&#95;id · raw&#95;text · asset&#95;refs · created&#95;at
- **additionalProperties** (`additionalProperties`): `false`

#### SourceSummary

- **type** (`type`): object
- **properties** (`properties`)
  - **source&#95;id** (`source_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **excerpt** (`excerpt`)
    - **type** (`type`): string
    - **minLength** (`minLength`): `0`
  - **created&#95;at** (`created_at`)
    - **$ref** (`$ref`): #/$defs/Timestamp
- **required** (`required`): source&#95;id · excerpt · created&#95;at
- **additionalProperties** (`additionalProperties`): `false`

#### SourceList

- **type** (`type`): object
- **properties** (`properties`)
  - **items** (`items`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/SourceSummary
    - **minItems** (`minItems`): `0`
  - **next&#95;cursor** (`next_cursor`)
    - **$ref** (`$ref`): #/$defs/Id
- **required** (`required`): items
- **additionalProperties** (`additionalProperties`): `false`

#### ListQuery

- **type** (`type`): object
- **properties** (`properties`)
  - **cursor** (`cursor`)
    - **$ref** (`$ref`): #/$defs/Id
  - **limit** (`limit`)
    - **type** (`type`): integer
    - **minimum** (`minimum`): `1`
    - **maximum** (`maximum`): `100`
- **required** (`required`): `[]`
- **additionalProperties** (`additionalProperties`): `false`

#### RegistrationInput

- **type** (`type`): object
- **properties** (`properties`)
  - **source&#95;id** (`source_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **selector** (`selector`)
    - **type** (`type`): string
    - **minLength** (`minLength`): `1`
    - **maxLength** (`maxLength`): `2048`
- **required** (`required`): source&#95;id · selector
- **additionalProperties** (`additionalProperties`): `false`

#### Issue

- **type** (`type`): object
- **properties** (`properties`)
  - **issue&#95;id** (`issue_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **field** (`field`)
    - **$ref** (`$ref`): #/$defs/Id
  - **code** (`code`)
    - **enum** (`enum`): missing · conflict · invalid · rule&#95;unverified · rights&#95;unknown · unsupported · permission&#95;denied · model&#95;unavailable
  - **message** (`message`)
    - **$ref** (`$ref`): #/$defs/Text
  - **blocking** (`blocking`)
    - **type** (`type`): boolean
- **required** (`required`): issue&#95;id · field · code · message · blocking
- **additionalProperties** (`additionalProperties`): `false`

#### Answer

- **type** (`type`): object
- **properties** (`properties`)
  - **issue&#95;id** (`issue_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **value** (`value`)
    - **$ref** (`$ref`): #/$defs/Value
- **required** (`required`): issue&#95;id · value
- **additionalProperties** (`additionalProperties`): `false`

#### PreparationEdit

- **type** (`type`): object
- **properties** (`properties`)
  - **expected&#95;revision** (`expected_revision`)
    - **$ref** (`$ref`): #/$defs/Revision
  - **source&#95;id** (`source_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **selector** (`selector`)
    - **type** (`type`): string
    - **minLength** (`minLength`): `1`
    - **maxLength** (`maxLength`): `2048`
  - **answers** (`answers`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Answer
    - **minItems** (`minItems`): `1`
  - **corrections** (`corrections`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/FieldCorrection
    - **minItems** (`minItems`): `1`
- **required** (`required`): expected&#95;revision
- **additionalProperties** (`additionalProperties`): `false`

#### Provenance

- **type** (`type`): object
- **properties** (`properties`)
  - **field** (`field`)
    - **$ref** (`$ref`): #/$defs/Id
  - **kind** (`kind`)
    - **enum** (`enum`): direct · wording · selection · derived · user&#95;choice
  - **fact&#95;refs** (`fact_refs`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Id
    - **minItems** (`minItems`): `1`
    - **uniqueItems** (`uniqueItems`): `true`
  - **note** (`note`)
    - **$ref** (`$ref`): #/$defs/Text
- **required** (`required`): field · kind · fact&#95;refs
- **additionalProperties** (`additionalProperties`): `false`

#### Preparation

- **type** (`type`): object
- **properties** (`properties`)
  - **ready** (`ready`)
    - **type** (`type`): boolean
  - **values** (`values`)
    - **$ref** (`$ref`): #/$defs/Values
  - **facts** (`facts`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Fact
    - **minItems** (`minItems`): `0`
  - **issues** (`issues`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Issue
    - **minItems** (`minItems`): `0`
  - **provenance** (`provenance`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Provenance
    - **minItems** (`minItems`): `0`
- **required** (`required`): ready · values · facts · issues · provenance
- **additionalProperties** (`additionalProperties`): `false`

#### AuthCommand

- **oneOf** (`oneOf`)
  - **[0] **
    - **type** (`type`): object
    - **properties** (`properties`)
      - **action** (`action`)
        - **const** (`const`): open
      - **expected&#95;revision** (`expected_revision`)
        - **$ref** (`$ref`): #/$defs/Revision
    - **required** (`required`): action · expected&#95;revision
    - **additionalProperties** (`additionalProperties`): `false`
  - **[1] **
    - **type** (`type`): object
    - **properties** (`properties`)
      - **action** (`action`)
        - **const** (`const`): finish
      - **expected&#95;revision** (`expected_revision`)
        - **$ref** (`$ref`): #/$defs/Revision
      - **generation** (`generation`)
        - **$ref** (`$ref`): #/$defs/Revision
    - **required** (`required`): action · expected&#95;revision · generation
    - **additionalProperties** (`additionalProperties`): `false`
  - **[2] **
    - **type** (`type`): object
    - **properties** (`properties`)
      - **action** (`action`)
        - **const** (`const`): close
      - **expected&#95;revision** (`expected_revision`)
        - **$ref** (`$ref`): #/$defs/Revision
      - **generation** (`generation`)
        - **$ref** (`$ref`): #/$defs/Revision
    - **required** (`required`): action · expected&#95;revision · generation
    - **additionalProperties** (`additionalProperties`): `false`
  - **[3] **
    - **type** (`type`): object
    - **properties** (`properties`)
      - **action** (`action`)
        - **const** (`const`): refresh
      - **expected&#95;revision** (`expected_revision`)
        - **$ref** (`$ref`): #/$defs/Revision
      - **generation** (`generation`)
        - **$ref** (`$ref`): #/$defs/Revision
    - **required** (`required`): action · expected&#95;revision · generation
    - **additionalProperties** (`additionalProperties`): `false`

#### AuthView

- **type** (`type`): object
- **properties** (`properties`)
  - **state** (`state`)
    - **enum** (`enum`): none · human · verifying · verified · closed
  - **generation** (`generation`)
    - **$ref** (`$ref`): #/$defs/Revision
  - **account&#95;label** (`account_label`)
    - **$ref** (`$ref`): #/$defs/Text
- **required** (`required`): state
- **additionalProperties** (`additionalProperties`): `false`

#### AuthGrant

- **type** (`type`): object
- **properties** (`properties`)
  - **generation** (`generation`)
    - **$ref** (`$ref`): #/$defs/Revision
  - **viewer&#95;grant** (`viewer_grant`)
    - **$ref** (`$ref`): #/$defs/Id
  - **expires&#95;at** (`expires_at`)
    - **$ref** (`$ref`): #/$defs/Timestamp
- **required** (`required`): generation · viewer&#95;grant · expires&#95;at
- **additionalProperties** (`additionalProperties`): `false`

#### TargetView

- **type** (`type`): object
- **properties** (`properties`)
  - **상태** (`status`)
    - **enum** (`enum`): new · existing · ambiguous
  - **account&#95;label** (`account_label`)
    - **$ref** (`$ref`): #/$defs/Text
  - **object&#95;kind** (`object_kind`)
    - **$ref** (`$ref`): #/$defs/Id
  - **target&#95;label** (`target_label`)
    - **$ref** (`$ref`): #/$defs/Text
  - **existing&#95;registration&#95;id** (`existing_registration_id`)
    - **$ref** (`$ref`): #/$defs/Id
- **required** (`required`): status · account&#95;label · object&#95;kind · target&#95;label
- **additionalProperties** (`additionalProperties`): `false`

#### ReviewView

- **type** (`type`): object
- **properties** (`properties`)
  - **digest** (`digest`)
    - **$ref** (`$ref`): #/$defs/Digest
  - **values** (`values`)
    - **$ref** (`$ref`): #/$defs/Values
  - **assets** (`assets`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/AssetRef
    - **minItems** (`minItems`): `0`
  - **profile&#95;ref** (`profile_ref`)
    - **$ref** (`$ref`): #/$defs/ProfileRef
  - **target** (`target`)
    - **$ref** (`$ref`): #/$defs/TargetView
  - **procedure** (`procedure`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Text
    - **minItems** (`minItems`): `1`
  - **goal** (`goal`)
    - **$ref** (`$ref`): #/$defs/Text
  - **notice** (`notice`)
    - **$ref** (`$ref`): #/$defs/Text
- **required** (`required`): digest · values · assets · profile&#95;ref · target · procedure · goal · notice
- **additionalProperties** (`additionalProperties`): `false`

#### StartInput

- **type** (`type`): object
- **properties** (`properties`)
  - **expected&#95;revision** (`expected_revision`)
    - **$ref** (`$ref`): #/$defs/Revision
  - **review&#95;digest** (`review_digest`)
    - **$ref** (`$ref`): #/$defs/Digest
  - **approved** (`approved`)
    - **const** (`const`): `true`
  - **request&#95;key** (`request_key`)
    - **type** (`type`): string
    - **minLength** (`minLength`): `1`
    - **maxLength** (`maxLength`): `128`
- **required** (`required`): expected&#95;revision · review&#95;digest · approved · request&#95;key
- **additionalProperties** (`additionalProperties`): `false`

#### StepView

- **type** (`type`): object
- **properties** (`properties`)
  - **step&#95;id** (`step_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **label** (`label`)
    - **$ref** (`$ref`): #/$defs/Text
  - **상태** (`status`)
    - **enum** (`enum`): pending · confirmed · absent · unknown · error
- **required** (`required`): step&#95;id · label · status
- **additionalProperties** (`additionalProperties`): `false`

#### Progress

- **type** (`type`): object
- **properties** (`properties`)
  - **step&#95;index** (`step_index`)
    - **type** (`type`): integer
    - **minimum** (`minimum`): `0`
  - **step&#95;count** (`step_count`)
    - **type** (`type`): integer
    - **minimum** (`minimum`): `1`
  - **confirmed&#95;steps** (`confirmed_steps`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/StepView
    - **minItems** (`minItems`): `0`
  - **current&#95;step** (`current_step`)
    - **$ref** (`$ref`): #/$defs/StepView
- **required** (`required`): step&#95;index · step&#95;count · confirmed&#95;steps
- **additionalProperties** (`additionalProperties`): `false`

#### Error

- **type** (`type`): object
- **properties** (`properties`)
  - **code** (`code`)
    - **enum** (`enum`): INVALID&#95;REQUEST · UNAUTHENTICATED · NOT&#95;FOUND · UNSUPPORTED&#95;TARGET · VALIDATION&#95;FAILED · MODEL&#95;UNAVAILABLE · AUTH&#95;REQUIRED · ACCOUNT&#95;MISMATCH · TARGET&#95;AMBIGUOUS · DUPLICATE&#95;RISK · PERMISSION&#95;DENIED · STALE&#95;REVISION · APPROVAL&#95;INVALID · IDEMPOTENCY&#95;CONFLICT · INVALID&#95;PHASE · RUNTIME&#95;ERROR · EFFECT&#95;UNKNOWN · EVIDENCE&#95;INSUFFICIENT · PROFILE&#95;CHANGED · CONNECTION&#95;MISMATCH · FACT&#95;CONFLICT
  - **message** (`message`)
    - **$ref** (`$ref`): #/$defs/Text
  - **issues** (`issues`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Issue
    - **minItems** (`minItems`): `0`
  - **current&#95;revision** (`current_revision`)
    - **$ref** (`$ref`): #/$defs/Revision
- **required** (`required`): code · message
- **additionalProperties** (`additionalProperties`): `false`

#### EffectSummary

- **type** (`type`): object
- **properties** (`properties`)
  - **step&#95;id** (`step_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **operation&#95;id** (`operation_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **verdict** (`verdict`)
    - **enum** (`enum`): confirmed · absent · unknown
  - **evidence&#95;refs** (`evidence_refs`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Id
    - **minItems** (`minItems`): `0`
- **required** (`required`): step&#95;id · operation&#95;id · verdict · evidence&#95;refs
- **additionalProperties** (`additionalProperties`): `false`

#### EvidenceView

- **type** (`type`): object
- **properties** (`properties`)
  - **evidence&#95;id** (`evidence_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **kind** (`kind`)
    - **enum** (`enum`): operation · goal · error
  - **method** (`method`)
    - **$ref** (`$ref`): #/$defs/EvidenceMethod
  - **target&#95;label** (`target_label`)
    - **$ref** (`$ref`): #/$defs/Text
  - **summary** (`summary`)
    - **$ref** (`$ref`): #/$defs/Text
  - **observed&#95;at** (`observed_at`)
    - **$ref** (`$ref`): #/$defs/Timestamp
  - **environment** (`environment`)
    - **$ref** (`$ref`): #/$defs/Environment
- **required** (`required`): evidence&#95;id · kind · method · target&#95;label · summary · observed&#95;at · environment
- **additionalProperties** (`additionalProperties`): `false`

#### Result

- **type** (`type`): object
- **properties** (`properties`)
  - **goal&#95;verdict** (`goal_verdict`)
    - **$ref** (`$ref`): #/$defs/GoalVerdict
  - **environment** (`environment`)
    - **$ref** (`$ref`): #/$defs/Environment
  - **effects** (`effects`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/EffectSummary
    - **minItems** (`minItems`): `0`
  - **evidence** (`evidence`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/EvidenceView
    - **minItems** (`minItems`): `0`
  - **error** (`error`)
    - **$ref** (`$ref`): #/$defs/Error
  - **next&#95;action** (`next_action`)
    - **$ref** (`$ref`): #/$defs/Text
- **required** (`required`): goal&#95;verdict · environment · effects · evidence · next&#95;action
- **additionalProperties** (`additionalProperties`): `false`

#### RegistrationView

- **type** (`type`): object
- **properties** (`properties`)
  - **registration&#95;id** (`registration_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **source&#95;id** (`source_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **revision** (`revision`)
    - **$ref** (`$ref`): #/$defs/Revision
  - **support** (`support`)
    - **enum** (`enum`): supported · unsupported · blocked
  - **profile&#95;ref** (`profile_ref`)
    - **$ref** (`$ref`): #/$defs/ProfileRef
  - **preparation** (`preparation`)
    - **$ref** (`$ref`): #/$defs/Preparation
  - **auth** (`auth`)
    - **$ref** (`$ref`): #/$defs/AuthView
  - **target** (`target`)
    - **$ref** (`$ref`): #/$defs/TargetView
  - **review** (`review`)
    - **$ref** (`$ref`): #/$defs/ReviewView
  - **job&#95;state** (`job_state`)
    - **anyOf** (`anyOf`)
      - **[0] **
        - **type** (`type`): null
      - **[1] **
        - **$ref** (`$ref`): #/$defs/JobState
  - **progress** (`progress`)
    - **$ref** (`$ref`): #/$defs/Progress
  - **result** (`result`)
    - **$ref** (`$ref`): #/$defs/Result
- **required** (`required`): registration&#95;id · source&#95;id · revision · support · preparation · auth · job&#95;state
- **additionalProperties** (`additionalProperties`): `false`

#### AuthResponse

- **type** (`type`): object
- **properties** (`properties`)
  - **registration** (`registration`)
    - **$ref** (`$ref`): #/$defs/RegistrationView
  - **grant** (`grant`)
    - **$ref** (`$ref`): #/$defs/AuthGrant
- **required** (`required`): registration
- **additionalProperties** (`additionalProperties`): `false`

#### RegistrationSummary

- **type** (`type`): object
- **properties** (`properties`)
  - **registration&#95;id** (`registration_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **source&#95;id** (`source_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **profile&#95;ref** (`profile_ref`)
    - **$ref** (`$ref`): #/$defs/ProfileRef
  - **job&#95;state** (`job_state`)
    - **anyOf** (`anyOf`)
      - **[0] **
        - **type** (`type`): null
      - **[1] **
        - **$ref** (`$ref`): #/$defs/JobState
  - **goal&#95;verdict** (`goal_verdict`)
    - **$ref** (`$ref`): #/$defs/GoalVerdict
- **required** (`required`): registration&#95;id · source&#95;id · job&#95;state
- **additionalProperties** (`additionalProperties`): `false`

#### RegistrationList

- **type** (`type`): object
- **properties** (`properties`)
  - **items** (`items`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/RegistrationSummary
    - **minItems** (`minItems`): `0`
  - **next&#95;cursor** (`next_cursor`)
    - **$ref** (`$ref`): #/$defs/Id
- **required** (`required`): items
- **additionalProperties** (`additionalProperties`): `false`

#### ProfileField

- **type** (`type`): object
- **properties** (`properties`)
  - **key** (`key`)
    - **$ref** (`$ref`): #/$defs/Id
  - **label** (`label`)
    - **$ref** (`$ref`): #/$defs/Text
  - **requirement** (`requirement`)
    - **enum** (`enum`): required · optional · conditional
  - **rule&#95;text** (`rule_text`)
    - **$ref** (`$ref`): #/$defs/Text
  - **source&#95;facts** (`source_facts`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Id
    - **minItems** (`minItems`): `0`
  - **evidence&#95;ids** (`evidence_ids`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Id
    - **minItems** (`minItems`): `1`
- **required** (`required`): key · label · requirement · rule&#95;text · source&#95;facts · evidence&#95;ids
- **additionalProperties** (`additionalProperties`): `false`

#### ProfileStep

- **type** (`type`): object
- **properties** (`properties`)
  - **step&#95;id** (`step_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **label** (`label`)
    - **$ref** (`$ref`): #/$defs/Text
  - **effect&#95;class** (`effect_class`)
    - **enum** (`enum`): read · potential&#95;effect
  - **bindings** (`bindings`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Id
    - **minItems** (`minItems`): `0`
    - **uniqueItems** (`uniqueItems`): `true`
  - **success&#95;evidence** (`success_evidence`)
    - **$ref** (`$ref`): #/$defs/Text
- **required** (`required`): step&#95;id · label · effect&#95;class · bindings · success&#95;evidence
- **additionalProperties** (`additionalProperties`): `false`

#### Profile

- **type** (`type`): object
- **properties** (`properties`)
  - **ref** (`ref`)
    - **$ref** (`$ref`): #/$defs/ProfileRef
  - **routes** (`routes`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Id
    - **minItems** (`minItems`): `1`
    - **uniqueItems** (`uniqueItems`): `true`
  - **fields** (`fields`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/ProfileField
    - **minItems** (`minItems`): `1`
  - **prohibitions** (`prohibitions`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Text
    - **minItems** (`minItems`): `1`
  - **steps** (`steps`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/ProfileStep
    - **minItems** (`minItems`): `1`
  - **goal** (`goal`)
    - **$ref** (`$ref`): #/$defs/ProfileGoal
  - **value&#95;contract&#95;ref** (`value_contract_ref`)
    - **$ref** (`$ref`): #/$defs/Id
  - **evidence&#95;ids** (`evidence_ids`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Id
    - **minItems** (`minItems`): `1`
- **required** (`required`): ref · routes · fields · prohibitions · steps · goal · value&#95;contract&#95;ref · evidence&#95;ids
- **additionalProperties** (`additionalProperties`): `false`

#### TargetIdentity

- **type** (`type`): object
- **properties** (`properties`)
  - **environment** (`environment`)
    - **$ref** (`$ref`): #/$defs/Environment
  - **platform** (`platform`)
    - **$ref** (`$ref`): #/$defs/PlatformId
  - **external&#95;account&#95;ref** (`external_account_ref`)
    - **$ref** (`$ref`): #/$defs/Id
  - **object&#95;kind** (`object_kind`)
    - **$ref** (`$ref`): #/$defs/Id
  - **slot&#95;ref** (`slot_ref`)
    - **$ref** (`$ref`): #/$defs/Id
- **required** (`required`): environment · platform · external&#95;account&#95;ref · object&#95;kind · slot&#95;ref
- **additionalProperties** (`additionalProperties`): `false`

#### TrustedTarget

- **type** (`type`): object
- **properties** (`properties`)
  - **identity** (`identity`)
    - **$ref** (`$ref`): #/$defs/TargetIdentity
  - **상태** (`status`)
    - **enum** (`enum`): new · existing · ambiguous
  - **evidence&#95;ref** (`evidence_ref`)
    - **$ref** (`$ref`): #/$defs/Id
  - **account&#95;label** (`account_label`)
    - **$ref** (`$ref`): #/$defs/Text
- **required** (`required`): identity · status · evidence&#95;ref · account&#95;label
- **additionalProperties** (`additionalProperties`): `false`

#### Scope

- **type** (`type`): object
- **properties** (`properties`)
  - **registration&#95;id** (`registration_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **source&#95;id** (`source_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **revision** (`revision`)
    - **$ref** (`$ref`): #/$defs/Revision
  - **profile&#95;ref** (`profile_ref`)
    - **$ref** (`$ref`): #/$defs/ProfileRef
  - **values** (`values`)
    - **$ref** (`$ref`): #/$defs/Values
  - **facts** (`facts`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Fact
    - **minItems** (`minItems`): `0`
  - **provenance** (`provenance`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Provenance
    - **minItems** (`minItems`): `0`
  - **assets** (`assets`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/AssetRef
    - **minItems** (`minItems`): `0`
  - **target** (`target`)
    - **$ref** (`$ref`): #/$defs/TargetIdentity
  - **connection** (`connection`)
    - **$ref** (`$ref`): #/$defs/ConnectionBinding
  - **procedure&#95;ids** (`procedure_ids`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Id
    - **minItems** (`minItems`): `1`
    - **uniqueItems** (`uniqueItems`): `true`
  - **goal&#95;kind** (`goal_kind`)
    - **$ref** (`$ref`): #/$defs/Id
- **required** (`required`): registration&#95;id · source&#95;id · revision · profile&#95;ref · values · facts · provenance · assets · target · connection · procedure&#95;ids · goal&#95;kind
- **additionalProperties** (`additionalProperties`): `false`

#### AcceptedScope

- **type** (`type`): object
- **properties** (`properties`)
  - **scope** (`scope`)
    - **$ref** (`$ref`): #/$defs/Scope
  - **review&#95;digest** (`review_digest`)
    - **$ref** (`$ref`): #/$defs/Digest
  - **accepted&#95;at** (`accepted_at`)
    - **$ref** (`$ref`): #/$defs/Timestamp
  - **owner&#95;ref** (`owner_ref`)
    - **$ref** (`$ref`): #/$defs/Id
  - **request&#95;key** (`request_key`)
    - **type** (`type`): string
    - **minLength** (`minLength`): `1`
    - **maxLength** (`maxLength`): `128`
- **required** (`required`): scope · review&#95;digest · accepted&#95;at · owner&#95;ref · request&#95;key
- **additionalProperties** (`additionalProperties`): `false`

#### ConnectionBinding

- **type** (`type`): object
- **properties** (`properties`)
  - **connection&#95;ref** (`connection_ref`)
    - **$ref** (`$ref`): #/$defs/Id
  - **verified&#95;generation** (`verified_generation`)
    - **$ref** (`$ref`): #/$defs/Revision
  - **account&#95;ref** (`account_ref`)
    - **$ref** (`$ref`): #/$defs/Id
- **required** (`required`): connection&#95;ref · verified&#95;generation · account&#95;ref
- **additionalProperties** (`additionalProperties`): `false`

#### Operation

- **type** (`type`): object
- **properties** (`properties`)
  - **operation&#95;id** (`operation_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **step&#95;id** (`step_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **action&#95;key** (`action_key`)
    - **$ref** (`$ref`): #/$defs/Id
  - **effect&#95;class** (`effect_class`)
    - **enum** (`enum`): read · potential&#95;effect
  - **binding&#95;digest** (`binding_digest`)
    - **$ref** (`$ref`): #/$defs/Digest
- **required** (`required`): operation&#95;id · step&#95;id · action&#95;key · effect&#95;class · binding&#95;digest
- **additionalProperties** (`additionalProperties`): `false`

#### Observation

- **type** (`type`): object
- **properties** (`properties`)
  - **operation&#95;id** (`operation_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **step&#95;id** (`step_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **target** (`target`)
    - **$ref** (`$ref`): #/$defs/TargetIdentity
  - **method** (`method`)
    - **$ref** (`$ref`): #/$defs/EvidenceMethod
  - **verdict** (`verdict`)
    - **enum** (`enum`): confirmed · absent · unknown
  - **evidence&#95;refs** (`evidence_refs`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Id
    - **minItems** (`minItems`): `0`
  - **observed&#95;at** (`observed_at`)
    - **$ref** (`$ref`): #/$defs/Timestamp
- **required** (`required`): operation&#95;id · step&#95;id · target · method · verdict · evidence&#95;refs · observed&#95;at
- **additionalProperties** (`additionalProperties`): `false`

#### GoalObservation

- **type** (`type`): object
- **properties** (`properties`)
  - **goal&#95;kind** (`goal_kind`)
    - **$ref** (`$ref`): #/$defs/Id
  - **target** (`target`)
    - **$ref** (`$ref`): #/$defs/TargetIdentity
  - **method** (`method`)
    - **$ref** (`$ref`): #/$defs/EvidenceMethod
  - **observed&#95;state** (`observed_state`)
    - **$ref** (`$ref`): #/$defs/Id
  - **payload&#95;digest** (`payload_digest`)
    - **$ref** (`$ref`): #/$defs/Digest
  - **external&#95;ref** (`external_ref`)
    - **$ref** (`$ref`): #/$defs/Id
  - **asset&#95;digests** (`asset_digests`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Digest
    - **minItems** (`minItems`): `0`
  - **evidence&#95;ref** (`evidence_ref`)
    - **$ref** (`$ref`): #/$defs/Id
  - **observed&#95;at** (`observed_at`)
    - **$ref** (`$ref`): #/$defs/Timestamp
  - **environment** (`environment`)
    - **$ref** (`$ref`): #/$defs/Environment
- **required** (`required`): goal&#95;kind · target · method · observed&#95;state · payload&#95;digest · external&#95;ref · asset&#95;digests · evidence&#95;ref · observed&#95;at · environment
- **additionalProperties** (`additionalProperties`): `false`

#### ExecutionReport

- **type** (`type`): object
- **properties** (`properties`)
  - **observations** (`observations`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Observation
    - **minItems** (`minItems`): `0`
  - **goal&#95;observation** (`goal_observation`)
    - **$ref** (`$ref`): #/$defs/GoalObservation
  - **error** (`error`)
    - **$ref** (`$ref`): #/$defs/Error
- **required** (`required`): observations
- **additionalProperties** (`additionalProperties`): `false`

#### ResolveOutput

- **oneOf** (`oneOf`)
  - **[0] **
    - **type** (`type`): object
    - **properties** (`properties`)
      - **상태** (`status`)
        - **const** (`const`): supported
      - **profile** (`profile`)
        - **$ref** (`$ref`): #/$defs/Profile
    - **required** (`required`): status · profile
    - **additionalProperties** (`additionalProperties`): `false`
  - **[1] **
    - **type** (`type`): object
    - **properties** (`properties`)
      - **상태** (`status`)
        - **enum** (`enum`): unsupported · blocked
      - **이유** (`reason`)
        - **$ref** (`$ref`): #/$defs/Text
    - **required** (`required`): status · reason
    - **additionalProperties** (`additionalProperties`): `false`

#### PrepareInput

- **type** (`type`): object
- **properties** (`properties`)
  - **source** (`source`)
    - **$ref** (`$ref`): #/$defs/SourceView
  - **profile** (`profile`)
    - **$ref** (`$ref`): #/$defs/Profile
  - **answers** (`answers`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/ResolvedAnswer
    - **minItems** (`minItems`): `0`
- **required** (`required`): source · profile · answers
- **additionalProperties** (`additionalProperties`): `false`

#### AuthInput

- **type** (`type`): object
- **properties** (`properties`)
  - **registration&#95;id** (`registration_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **profile&#95;ref** (`profile_ref`)
    - **$ref** (`$ref`): #/$defs/ProfileRef
  - **owner&#95;ref** (`owner_ref`)
    - **$ref** (`$ref`): #/$defs/Id
  - **command** (`command`)
    - **$ref** (`$ref`): #/$defs/AuthCommand
- **required** (`required`): registration&#95;id · profile&#95;ref · owner&#95;ref · command
- **additionalProperties** (`additionalProperties`): `false`

#### AuthOutput

- **oneOf** (`oneOf`)
  - **[0] **
    - **type** (`type`): object
    - **properties** (`properties`)
      - **auth** (`auth`)
        - **type** (`type`): object
        - **properties** (`properties`)
          - **state** (`state`)
            - **enum** (`enum`): none · human · verifying · closed
          - **generation** (`generation`)
            - **$ref** (`$ref`): #/$defs/Revision
        - **required** (`required`): state
        - **additionalProperties** (`additionalProperties`): `false`
      - **grant** (`grant`)
        - **$ref** (`$ref`): #/$defs/AuthGrant
    - **required** (`required`): auth
    - **additionalProperties** (`additionalProperties`): `false`
  - **[1] **
    - **type** (`type`): object
    - **properties** (`properties`)
      - **auth** (`auth`)
        - **type** (`type`): object
        - **properties** (`properties`)
          - **state** (`state`)
            - **const** (`const`): verified
          - **generation** (`generation`)
            - **$ref** (`$ref`): #/$defs/Revision
          - **account&#95;label** (`account_label`)
            - **$ref** (`$ref`): #/$defs/Text
        - **required** (`required`): state · generation · account&#95;label
        - **additionalProperties** (`additionalProperties`): `false`
      - **target** (`target`)
        - **$ref** (`$ref`): #/$defs/TrustedTarget
      - **connection** (`connection`)
        - **$ref** (`$ref`): #/$defs/ConnectionBinding
    - **required** (`required`): auth · target · connection
    - **additionalProperties** (`additionalProperties`): `false`

#### ExecuteInput

- **type** (`type`): object
- **properties** (`properties`)
  - **accepted** (`accepted`)
    - **$ref** (`$ref`): #/$defs/AcceptedScope
- **required** (`required`): accepted
- **additionalProperties** (`additionalProperties`): `false`

#### EvaluateInput

- **type** (`type`): object
- **properties** (`properties`)
  - **profile** (`profile`)
    - **$ref** (`$ref`): #/$defs/Profile
  - **accepted** (`accepted`)
    - **$ref** (`$ref`): #/$defs/AcceptedScope
  - **report** (`report`)
    - **$ref** (`$ref`): #/$defs/ExecutionReport
  - **evidence** (`evidence`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/EvidenceRecord
    - **minItems** (`minItems`): `0`
- **required** (`required`): profile · accepted · report · evidence
- **additionalProperties** (`additionalProperties`): `false`

#### PlatformId

- **type** (`type`): string
- **minLength** (`minLength`): `1`
- **maxLength** (`maxLength`): `128`

#### SourcePackage

- **type** (`type`): object
- **properties** (`properties`)
  - **package&#95;id** (`package_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **minutes&#95;per&#95;session** (`minutes_per_session`)
    - **type** (`type`): integer
    - **minimum** (`minimum`): `1`
    - **maximum** (`maximum`): `9007199254740991`
  - **sessions&#95;per&#95;period** (`sessions_per_period`)
    - **type** (`type`): integer
    - **minimum** (`minimum`): `1`
    - **maximum** (`maximum`): `9007199254740991`
  - **period** (`period`)
    - **$ref** (`$ref`): #/$defs/Id
  - **total&#95;price&#95;krw** (`total_price_krw`)
    - **type** (`type`): integer
    - **minimum** (`minimum`): `0`
    - **maximum** (`maximum`): `9007199254740991`
  - **vat&#95;basis** (`vat_basis`)
    - **enum** (`enum`): included · excluded · unknown
- **required** (`required`): package&#95;id · minutes&#95;per&#95;session · sessions&#95;per&#95;period · period · total&#95;price&#95;krw · vat&#95;basis
- **additionalProperties** (`additionalProperties`): `false`

#### FactOrigin

- **type** (`type`): object
- **properties** (`properties`)
  - **kind** (`kind`)
    - **enum** (`enum`): source · answer
  - **ref** (`ref`)
    - **$ref** (`$ref`): #/$defs/Id
  - **locator** (`locator`)
    - **$ref** (`$ref`): #/$defs/Text
- **required** (`required`): kind · ref · locator
- **additionalProperties** (`additionalProperties`): `false`

#### Fact

- **type** (`type`): object
- **properties** (`properties`)
  - **fact&#95;id** (`fact_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **path** (`path`)
    - **$ref** (`$ref`): #/$defs/Id
  - **value** (`value`)
    - **$ref** (`$ref`): #/$defs/Value
  - **origin** (`origin`)
    - **$ref** (`$ref`): #/$defs/FactOrigin
- **required** (`required`): fact&#95;id · path · value · origin
- **additionalProperties** (`additionalProperties`): `false`

#### EvidenceMethod

- **enum** (`enum`): independent&#95;readback · submission&#95;response · form&#95;read · runtime&#95;observation

#### ProfileGoal

- **type** (`type`): object
- **properties** (`properties`)
  - **kind** (`kind`)
    - **$ref** (`$ref`): #/$defs/Id
  - **methods** (`methods`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/EvidenceMethod
    - **minItems** (`minItems`): `1`
    - **uniqueItems** (`uniqueItems`): `true`
  - **requires&#95;asset&#95;digests** (`requires_asset_digests`)
    - **type** (`type`): boolean
  - **goal&#95;capable&#95;steps** (`goal_capable_steps`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Id
    - **minItems** (`minItems`): `1`
    - **uniqueItems** (`uniqueItems`): `true`
  - **observed&#95;state** (`observed_state`)
    - **$ref** (`$ref`): #/$defs/Id
- **required** (`required`): kind · methods · requires&#95;asset&#95;digests · goal&#95;capable&#95;steps · observed&#95;state
- **additionalProperties** (`additionalProperties`): `false`

#### EvidenceRecord

- **type** (`type`): object
- **properties** (`properties`)
  - **evidence&#95;id** (`evidence_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **registration&#95;id** (`registration_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **target** (`target`)
    - **$ref** (`$ref`): #/$defs/TargetIdentity
  - **kind** (`kind`)
    - **enum** (`enum`): operation · goal · error
  - **method** (`method`)
    - **$ref** (`$ref`): #/$defs/EvidenceMethod
  - **observed&#95;at** (`observed_at`)
    - **$ref** (`$ref`): #/$defs/Timestamp
  - **environment** (`environment`)
    - **$ref** (`$ref`): #/$defs/Environment
  - **operation&#95;id** (`operation_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **observed&#95;state** (`observed_state`)
    - **$ref** (`$ref`): #/$defs/Id
  - **payload&#95;digest** (`payload_digest`)
    - **$ref** (`$ref`): #/$defs/Digest
  - **asset&#95;digests** (`asset_digests`)
    - **type** (`type`): array
    - **items** (`items`)
      - **$ref** (`$ref`): #/$defs/Digest
    - **minItems** (`minItems`): `0`
  - **external&#95;ref** (`external_ref`)
    - **$ref** (`$ref`): #/$defs/Id
- **required** (`required`): evidence&#95;id · registration&#95;id · target · kind · method · observed&#95;at · environment
- **additionalProperties** (`additionalProperties`): `false`

#### FieldCorrection

- **type** (`type`): object
- **properties** (`properties`)
  - **field** (`field`)
    - **$ref** (`$ref`): #/$defs/Id
  - **value** (`value`)
    - **$ref** (`$ref`): #/$defs/Value
- **required** (`required`): field · value
- **additionalProperties** (`additionalProperties`): `false`

#### ResolvedAnswer

- **type** (`type`): object
- **properties** (`properties`)
  - **answer&#95;id** (`answer_id`)
    - **$ref** (`$ref`): #/$defs/Id
  - **field** (`field`)
    - **$ref** (`$ref`): #/$defs/Id
  - **value** (`value`)
    - **$ref** (`$ref`): #/$defs/Value
  - **origin&#95;issue&#95;id** (`origin_issue_id`)
    - **$ref** (`$ref`): #/$defs/Id
- **required** (`required`): answer&#95;id · field · value
- **additionalProperties** (`additionalProperties`): `false`

