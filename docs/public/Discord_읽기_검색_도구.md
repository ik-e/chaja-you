# Discord 읽기·검색 도구 사용법

`tools/discord_reader.py`는 Discord 봇이 접근할 수 있는 채널에서 메시지를 읽고 채널·기간·키워드로 검색하는 로컬 도구입니다. 메시지를 보내거나 수정·삭제하지 않습니다.

## 설정

1. Python 3.9 이상을 준비합니다.
2. 봇에 필요한 읽기 권한만 부여하고 Discord Developer Portal에서 Message Content Intent를 설정합니다.
3. 저장소 루트의 `.env.example`을 참고해 로컬 `.env`에 `DISCORD_BOT_TOKEN`을 설정합니다. 실제 토큰은 저장소·채팅·문서에 넣지 않습니다.

## 예시

```powershell
py tools/discord_reader.py --guild "서버 이름" --keyword "배포" --max-results 20
py tools/discord_reader.py --guild "서버 이름" --channel "개발" --keyword "API 오류" --after 2026-11-01 --before 2026-11-10
```

봇이 볼 수 있는 채널에 한해 검색할 수 있습니다. 첨부 파일 본문은 자동 검색하지 않으며, 검색 결과와 가져온 메시지는 참고 자료로 다룹니다. 다른 멤버의 대화나 첨부를 외부에 재배포하기 전에 동의와 공개 범위를 확인하세요.
