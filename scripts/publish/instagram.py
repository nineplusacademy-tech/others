"""인스타그램 캐러셀(카드뉴스) + 릴스 발행.

인스타그램 Graph API는 파일 직접 업로드를 지원하지 않고 반드시 공개적으로
접근 가능한 image_url/video_url을 요구한다 — 그래서 이 저장소를 퍼블릭으로
전환했고, common.raw_github_url()로 queue/ 안의 파일을 가리키는 raw.githubusercontent.com
주소를 만들어 넘긴다.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import requests

from common import DRY_RUN, dry_run_log, raw_github_url

GRAPH = "https://graph.instagram.com"
POLL_INTERVAL_SECONDS = 10
POLL_MAX_ATTEMPTS = 30  # 최대 5분 대기


def _ig_id() -> str:
    return os.environ["INSTAGRAM_BUSINESS_ACCOUNT_ID"]


def _token() -> str:
    return os.environ["INSTAGRAM_ACCESS_TOKEN"]


def _wait_until_finished(creation_id: str) -> None:
    for _ in range(POLL_MAX_ATTEMPTS):
        time.sleep(POLL_INTERVAL_SECONDS)
        resp = requests.get(
            f"{GRAPH}/{creation_id}",
            params={"fields": "status_code", "access_token": _token()},
            timeout=30,
        )
        resp.raise_for_status()
        status = resp.json().get("status_code")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"인스타그램 미디어 처리 실패 (creation_id={creation_id})")
    raise TimeoutError(f"인스타그램 미디어 처리 시간 초과 (creation_id={creation_id})")


def publish_carousel(image_paths: list[Path], caption: str) -> str:
    if DRY_RUN:
        dry_run_log(
            "Instagram 캐러셀",
            images=", ".join(str(p) for p in image_paths),
            caption=caption,
        )
        return "dryrun-instagram-carousel"

    ig_id = _ig_id()
    token = _token()

    child_ids = []
    for path in image_paths:
        resp = requests.post(
            f"{GRAPH}/{ig_id}/media",
            data={
                "image_url": raw_github_url(path),
                "is_carousel_item": "true",
                "access_token": token,
            },
            timeout=60,
        )
        resp.raise_for_status()
        child_ids.append(resp.json()["id"])

    container = requests.post(
        f"{GRAPH}/{ig_id}/media",
        data={
            "media_type": "CAROUSEL",
            "children": ",".join(child_ids),
            "caption": caption,
            "access_token": token,
        },
        timeout=60,
    )
    container.raise_for_status()
    creation_id = container.json()["id"]

    publish = requests.post(
        f"{GRAPH}/{ig_id}/media_publish",
        data={"creation_id": creation_id, "access_token": token},
        timeout=60,
    )
    publish.raise_for_status()
    return publish.json()["id"]


def publish_reel(video_path: Path, caption: str) -> str:
    if DRY_RUN:
        dry_run_log("Instagram 릴스", video=str(video_path), caption=caption)
        return "dryrun-instagram-reel"

    ig_id = _ig_id()
    token = _token()

    container = requests.post(
        f"{GRAPH}/{ig_id}/media",
        data={
            "media_type": "REELS",
            "video_url": raw_github_url(video_path),
            "caption": caption,
            "access_token": token,
        },
        timeout=60,
    )
    container.raise_for_status()
    creation_id = container.json()["id"]

    _wait_until_finished(creation_id)

    publish = requests.post(
        f"{GRAPH}/{ig_id}/media_publish",
        data={"creation_id": creation_id, "access_token": token},
        timeout=60,
    )
    publish.raise_for_status()
    return publish.json()["id"]


def refresh_access_token(current_token: str) -> dict:
    """60일짜리 인스타그램 토큰을 갱신한다. {access_token, expires_in} 반환.

    호출부는 반환된 access_token 값을 절대 print/log 하지 않아야 한다 —
    이 저장소는 퍼블릭이라 Actions 로그도 공개되고, 새로 발급된 토큰은
    아직 GitHub Secrets에 등록되지 않아 자동 마스킹 대상이 아니다.
    """
    resp = requests.get(
        "https://graph.instagram.com/refresh_access_token",
        params={"grant_type": "ig_refresh_token", "access_token": current_token},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()
