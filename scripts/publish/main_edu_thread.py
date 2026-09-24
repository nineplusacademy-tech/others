"""스레드(교육뉴스) 목요일 10:00 자동 게시 오케스트레이터.

화요일 스레드(main_thread.py)가 메인 블로그를 소개한다면, 이쪽은 같은 스레드
계정으로 그 주 교육뉴스의 네이버 블로그 링크를 소개한다(`content-playbook.md` §9).
입력은 저장소 루트 `queue/` 아래 두 파일이다.

- `_edu_thread_link.json`: `set_naver_url.py --edu <URL>`이 기록한 네이버 URL
- `_edu_thread.md`: 스레드 본문(`{{BLOG_URL}}` 자리표시자 포함, 교육뉴스 방침상 CTA 없음)

둘 중 하나라도 없으면 게시하지 않고 종료한다(에러 아님 — 그 주는 사람이 처리).
게시에 성공하면 두 파일을 지워 다음 주 것과 섞이거나 중복 게시되지 않게 한다.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import threads
from common import DRY_RUN, QUEUE_DIR, fill_placeholders, naver_post_not_found

LINK_FILE = QUEUE_DIR / "_edu_thread_link.json"
TEXT_FILE = QUEUE_DIR / "_edu_thread.md"


def run() -> None:
    if not LINK_FILE.exists():
        print("교육뉴스 네이버 URL(_edu_thread_link.json)이 없음 — 종료")
        return
    if not TEXT_FILE.exists():
        print("교육뉴스 스레드 본문(_edu_thread.md)이 없음 — 종료")
        return

    url = json.loads(LINK_FILE.read_text(encoding="utf-8")).get("url")
    if not url:
        raise RuntimeError("_edu_thread_link.json에 url이 없습니다.")

    if not DRY_RUN and naver_post_not_found(url):
        print(f"::warning::교육뉴스 네이버 블로그 글({url})이 아직 공개 전이라 스레드를 미뤘습니다 — 다음 catch-up 실행 때 다시 시도합니다.")
        return

    text = fill_placeholders(TEXT_FILE.read_text(encoding="utf-8").strip(), BLOG_URL=url)
    result_id = threads.publish_text(text)

    if not DRY_RUN:
        LINK_FILE.unlink()
        TEXT_FILE.unlink()
    print(f"[edu-thread] 발행 완료: {result_id}")


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:  # noqa: BLE001 — 실패 원인을 그대로 Actions 로그에 남김
        print(f"교육뉴스 스레드 발행 중 오류 발생: {exc}", file=sys.stderr)
        sys.exit(1)
