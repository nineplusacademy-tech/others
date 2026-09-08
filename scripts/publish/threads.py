"""스레드(Threads) 텍스트 게시 + 액세스 토큰 갱신.

Threads API는 인스타그램/페이스북과 별도의 Meta 앱(`threads_nineplus`)과
별도의 그래프 API 호스트(graph.threads.net)를 쓴다(publishing-plan.md §6).
카드뉴스 캐러셀 첨부 없이 텍스트(+ 블로그 링크) 게시만 자동화한다 — 이미지를
첨부하는 주는 당분간 사람이 그대로 수동 게시한다(content-playbook.md §9).
"""

from __future__ import annotations

import os
import time

import requests

from common import DRY_RUN, dry_run_log

GRAPH = "https://graph.threads.net/v1.0"
POLL_INTERVAL_SECONDS = 3
POLL_MAX_ATTEMPTS = 20  # 최대 1분 대기


def _user_id() -> str:
    return os.environ["THREADS_USER_ID"]


def _token() -> str:
    return os.environ["THREADS_ACCESS_TOKEN"]


def _wait_until_finished(creation_id: str, token: str) -> None:
    for _ in range(POLL_MAX_ATTEMPTS):
        resp = requests.get(
            f"{GRAPH}/{creation_id}",
            params={"fields": "status", "access_token": token},
            timeout=30,
        )
        resp.raise_for_status()
        status = resp.json().get("status")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"스레드 게시물 처리 실패 (creation_id={creation_id})")
        time.sleep(POLL_INTERVAL_SECONDS)
    raise TimeoutError(f"스레드 게시물 처리 시간 초과 (creation_id={creation_id})")


def publish_text(text: str) -> str:
    """텍스트(+ 링크) 스레드 게시물을 올린다. 게시된 글의 id를 반환한다."""
    if DRY_RUN:
        dry_run_log("Threads 텍스트 게시", text=text)
        return "dryrun-threads-text"

    user_id = _user_id()
    token = _token()

    container = requests.post(
        f"{GRAPH}/{user_id}/threads",
        data={"media_type": "TEXT", "text": text, "access_token": token},
        timeout=60,
    )
    container.raise_for_status()
    creation_id = container.json()["id"]

    _wait_until_finished(creation_id, token)

    publish = requests.post(
        f"{GRAPH}/{user_id}/threads_publish",
        data={"creation_id": creation_id, "access_token": token},
        timeout=60,
    )
    publish.raise_for_status()
    return publish.json()["id"]


def refresh_access_token(current_token: str) -> dict:
    """60일짜리 스레드 장기 토큰을 갱신한다. {access_token, expires_in} 반환.

    호출부는 반환된 access_token 값을 절대 print/log하지 않아야 한다 —
    이 저장소는 퍼블릭이라 Actions 로그도 공개되고, 새로 발급된 토큰은
    아직 GitHub Secrets에 등록되지 않아 자동 마스킹 대상이 아니다.
    """
    resp = requests.get(
        f"{GRAPH}/refresh_access_token",
        params={"grant_type": "th_refresh_token", "access_token": current_token},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()
