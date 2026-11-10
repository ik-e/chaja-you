#!/usr/bin/env python3
"""Read-only Discord history reader with channel, date, and keyword filters.

Requires Python 3.9+. The bot token is read from DISCORD_BOT_TOKEN or a local
.env file next to this script / in the current directory. This tool only makes
GET requests to Discord; it cannot send, edit, delete, or react to messages.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://discord.com/api/v10"
UA = "DiscordBot (chaja-you-readonly, 1.0)"


def token() -> str:
    value = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
    if not value:
        for path in (Path(__file__).resolve().parent.parent / ".env", Path.cwd() / ".env"):
            if path.is_file():
                for line in path.read_text(encoding="utf-8-sig").splitlines():
                    if line.strip().startswith("DISCORD_BOT_TOKEN="):
                        value = line.split("=", 1)[1].strip().strip("\"'")
                        break
            if value:
                break
    if not value:
        raise SystemExit("DISCORD_BOT_TOKEN이 없습니다. 저장소 루트의 .env에 직접 설정하세요.")
    return value


def get(path: str, **params):
    url = API + path + (("?" + urllib.parse.urlencode(params)) if params else "")
    req = urllib.request.Request(url, headers={"Authorization": "Bot " + token(), "User-Agent": UA})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            if exc.code == 429 and attempt < 5:
                try:
                    delay = float(json.loads(detail).get("retry_after", 1))
                except (ValueError, TypeError):
                    delay = 1
                time.sleep(delay + 0.2)
                continue
            hints = {
                401: "봇 토큰을 확인하세요.",
                403: "봇에 채널 보기와 메시지 기록 읽기 권한이 있는지 확인하세요.",
                404: "서버 또는 채널 ID를 확인하세요.",
            }
            raise SystemExit(f"Discord API HTTP {exc.code}: {hints.get(exc.code, detail[:300])}")
    raise SystemExit("Discord API 요청 재시도 한도를 넘었습니다.")


def resolve_guild(name: str) -> dict:
    guilds = get("/users/@me/guilds")
    matches = [g for g in guilds if g["id"] == name or g["name"].casefold() == name.casefold()]
    if not matches:
        matches = [g for g in guilds if name.casefold() in g["name"].casefold()]
    if not matches:
        raise SystemExit(f"봇이 접근할 수 있는 서버를 찾지 못했습니다: {name}")
    if len(matches) > 1:
        raise SystemExit("서버 이름이 여러 개와 일치합니다. 서버 ID를 사용하세요: " + ", ".join(f"{g['name']} ({g['id']})" for g in matches))
    return matches[0]


def parse_date(value: str | None, end: bool = False) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise SystemExit(f"날짜 형식이 올바르지 않습니다: {value} (예: 2026-11-01 또는 2026-11-01T09:30:00+09:00)")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
    dt = dt.astimezone(timezone.utc)
    if end and len(value) == 10:
        from datetime import timedelta
        dt += timedelta(days=1)
    return dt


def message_time(message: dict) -> datetime:
    return datetime.fromisoformat(message["timestamp"].replace("Z", "+00:00")).astimezone(timezone.utc)


def channel_list(guild_id: str) -> list[dict]:
    return sorted((c for c in get(f"/guilds/{guild_id}/channels") if c.get("type") in (0, 5, 15, 16)), key=lambda c: c.get("position", 0))


def searchable_channels(guild_id: str, parents: list[dict]) -> list[dict]:
    """Return accessible parent channels plus active and public archived threads."""
    threads: dict[str, dict] = {}
    for thread in get(f"/guilds/{guild_id}/threads/active").get("threads", []):
        threads[thread["id"]] = thread
    for parent in parents:
        cursor = None
        # Bound discovery to 500 archived threads per parent. Message scanning
        # remains separately bounded by --max-scan.
        for _ in range(5):
            params = {"limit": 100}
            if cursor:
                params["before"] = cursor
            page = get(f"/channels/{parent['id']}/threads/archived/public", **params)
            batch = page.get("threads", [])
            for thread in batch:
                threads[thread["id"]] = thread
            if not page.get("has_more") or not batch:
                break
            cursor = batch[-1].get("thread_metadata", {}).get("archive_timestamp")
            if not cursor:
                break
    by_id = {c["id"]: c for c in parents}
    return parents + [
        {**t, "parent_name": by_id.get(t.get("parent_id"), {}).get("name", "알 수 없는 채널")}
        for t in threads.values()
    ]


def resolve_channels(channels: list[dict], requested: str | None) -> list[dict]:
    if not requested:
        return channels
    if requested.isdigit():
        found = [c for c in channels if c["id"] == requested]
    else:
        needle = requested.lstrip("#").casefold()
        found = [c for c in channels if c["name"].casefold() == needle]
        if not found:
            found = [c for c in channels if needle in c["name"].casefold()]
    if not found:
        raise SystemExit(f"텍스트 채널 또는 스레드를 찾지 못했습니다: {requested}")
    if len(found) > 1:
        raise SystemExit("채널/스레드 이름이 여러 개와 일치합니다. ID를 사용하세요: " + ", ".join(f"#{c['name']} ({c['id']})" for c in found))
    parent_ids = {c["id"] for c in found if c.get("type") in (0, 5, 15, 16)}
    if parent_ids:
        found.extend(c for c in channels if c.get("parent_id") in parent_ids)
    return found


def searchable_text(message: dict) -> str:
    parts = [message.get("content", "")]
    parts.extend(a.get("filename", "") for a in message.get("attachments", []))
    for embed in message.get("embeds", []):
        parts.extend((embed.get("title", ""), embed.get("description", "")))
    return " ".join(parts)


def search_channel(channel: dict, keyword: str, after: datetime | None, before: datetime | None,
                   scan_limit: int, result_limit: int) -> tuple[list[dict], int]:
    results: list[dict] = []
    scanned = 0
    cursor = None
    terms = [part.casefold() for part in keyword.split() if part]
    while scanned < scan_limit and len(results) < result_limit:
        count = min(100, scan_limit - scanned)
        params = {"limit": count}
        if cursor:
            params["before"] = cursor
        batch = get(f"/channels/{channel['id']}/messages", **params)
        if not batch:
            break
        for message in batch:
            scanned += 1
            timestamp = message_time(message)
            if after and timestamp < after:
                return results, scanned
            if before and timestamp >= before:
                continue
            haystack = searchable_text(message).casefold()
            if all(term in haystack for term in terms):
                results.append({"channel": channel["name"], "channel_id": channel["id"],
                                "parent_name": channel.get("parent_name"), **message})
                if len(results) >= result_limit:
                    break
        cursor = batch[-1]["id"]
        if len(batch) < count:
            break
    return results, scanned


def main() -> None:
    # Windows consoles may use cp949; Discord messages can contain characters
    # outside that encoding. Replace only unrepresentable output characters.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="Discord 메시지를 채널·기간·키워드로 읽기 전용 검색")
    parser.add_argument("--guild", required=True, help="서버 이름 또는 서버 ID")
    parser.add_argument("--channel", help="채널/스레드 이름 또는 ID. 생략하면 접근 가능한 텍스트 채널과 공개 스레드 전체")
    parser.add_argument("--keyword", "-k", required=True, help="검색어. 여러 단어는 모두 포함된 메시지만 반환")
    parser.add_argument("--after", help="시작 날짜/시각(포함), 예: 2026-11-01 또는 ISO 시각")
    parser.add_argument("--before", help="종료 날짜/시각(미포함), 예: 2026-11-10")
    parser.add_argument("--max-scan", type=int, default=2000, help="채널별 최대 확인 메시지 수 (기본 2000)")
    parser.add_argument("--max-results", type=int, default=30, help="최대 검색 결과 수 (기본 30)")
    parser.add_argument("--json", action="store_true", help="검색 결과 JSON 출력")
    args = parser.parse_args()
    if args.max_scan < 1 or args.max_results < 1:
        parser.error("--max-scan과 --max-results는 1 이상이어야 합니다.")
    if not args.keyword.strip():
        parser.error("--keyword는 비워 둘 수 없습니다.")
    guild = resolve_guild(args.guild)
    channels = resolve_channels(searchable_channels(guild["id"], channel_list(guild["id"])), args.channel)
    after, before = parse_date(args.after), parse_date(args.before, end=True)
    if after and before and after >= before:
        parser.error("--after는 --before보다 앞선 시각이어야 합니다.")
    all_results, scanned_total = [], 0
    per_channel_scan = args.max_scan if args.channel else max(1, args.max_scan // max(1, len(channels)))
    for channel in channels:
        found, scanned = search_channel(channel, args.keyword, after, before, per_channel_scan,
                                        args.max_results - len(all_results))
        all_results.extend(found)
        scanned_total += scanned
        if len(all_results) >= args.max_results:
            break
    if args.json:
        print(json.dumps({"guild": guild["name"], "keyword": args.keyword, "scanned": scanned_total,
                          "truncated": scanned_total >= args.max_scan, "results": all_results}, ensure_ascii=False, indent=2))
        return
    print(f"서버: {guild['name']} | 검색어: {args.keyword} | 확인 메시지: {scanned_total} | 결과: {len(all_results)}")
    if not all_results:
        print("조건에 맞는 메시지가 없습니다.")
        return
    for message in all_results:
        created = message_time(message).astimezone().strftime("%Y-%m-%d %H:%M %Z")
        author = message.get("author", {})
        display = author.get("global_name") or author.get("username", "알 수 없음")
        body = searchable_text(message).replace("\n", " ⏎ ").strip() or "(본문 없음)"
        url = f"https://discord.com/channels/{guild['id']}/{message['channel_id']}/{message['id']}"
        location = f"#{message['parent_name']} / 스레드: {message['channel']}" if message.get("parent_name") else f"#{message['channel']}"
        print(f"\n[{created}] {location} · {display}\n{body}\n{url}")
    if scanned_total >= args.max_scan:
        print("\n검색 범위가 --max-scan 한도에 도달했습니다. 기간을 좁히거나 한도를 높여 다시 검색하세요.")


if __name__ == "__main__":
    main()
