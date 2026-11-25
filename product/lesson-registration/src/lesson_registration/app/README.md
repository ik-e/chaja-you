# R03 TASK-050 · 공통 앱/API

H1~H9·CO·KNOW·STORE·RESULT; 원자 수락/admit/observe/fence와 API; 별도 브라우저·PREP 구현 제외

PREP과 인증/실행은 공통 Providers로 명시 주입한다.

- HTTP factory: `lesson_registration.app.http.create_app(coordinator, ...)`
- 로컬 실행: `lesson_registration.app.service.serve(coordinator, ...)`
- [연동 실행 안내](../../../tests/modules/app/README.md)
- [상세 설계](../../../tests/modules/app/SPEC.md)

mock-only, DB당 단일 서버. 실제 UI/viewer/provider 연결 및 제품 gate는 별도 검증한다.
