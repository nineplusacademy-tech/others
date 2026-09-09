"""페이스북 페이지 게시글(사진) + 릴스 발행."""

from __future__ import annotations

import os
from pathlib import Path

import requests

from common import DRY_RUN, dry_run_log, raise_for_status_with_body

GRAPH = "https://graph.facebook.com/v21.0"


def _page_id() -> str:
    return os.environ["FACEBOOK_PAGE_ID"]


def _page_token() -> str:
    return os.environ["FACEBOOK_PAGE_ACCESS_TOKEN"]


def publish_photo_carousel(image_paths: list[Path], caption: str) -> str:
    """카드뉴스 9장 + 캡션(블로그 링크 포함)으로 멀티포토(캐러셀) 페이지 게시글을 올린다.

    Graph API는 인스타그램 캐러셀과 달리 별도 컨테이너 타입이 없다 — 사진을
    각각 비공개(published=false)로 업로드해 photo_id만 받은 뒤, /feed에
    attached_media로 묶어 게시글 하나로 발행하는 2단계 방식이다.
    """
    if DRY_RUN:
        dry_run_log("Facebook 캐러셀 게시글", images=[str(p) for p in image_paths], caption=caption)
        return "dryrun-facebook-carousel"

    token = _page_token()
    page_id = _page_id()

    media_fbids = []
    for image_path in image_paths:
        with open(image_path, "rb") as f:
            resp = requests.post(
                f"{GRAPH}/{page_id}/photos",
                data={"published": "false", "access_token": token},
                files={"source": f},
                timeout=120,
            )
        raise_for_status_with_body(resp)
        media_fbids.append(resp.json()["id"])

    attached_media = [{"media_fbid": fbid} for fbid in media_fbids]
    feed_resp = requests.post(
        f"{GRAPH}/{page_id}/feed",
        json={
            "message": caption,
            "attached_media": attached_media,
            "access_token": token,
        },
        timeout=120,
    )
    raise_for_status_with_body(feed_resp)
    return feed_resp.json()["id"]


def publish_reel(video_path: Path, caption: str) -> str:
    """숏츠 영상을 페이스북 릴스로 업로드한다 (Resumable Upload API 3단계)."""
    if DRY_RUN:
        dry_run_log("Facebook 릴스", video=str(video_path), caption=caption)
        return "dryrun-facebook-reel"

    token = _page_token()
    page_id = _page_id()

    start = requests.post(
        f"{GRAPH}/{page_id}/video_reels",
        data={"upload_phase": "start", "access_token": token},
        timeout=60,
    )
    raise_for_status_with_body(start)
    start_data = start.json()
    video_id = start_data["video_id"]
    upload_url = start_data["upload_url"]

    file_size = os.path.getsize(video_path)
    with open(video_path, "rb") as f:
        video_bytes = f.read()

    upload_resp = requests.post(
        upload_url,
        headers={
            "Authorization": f"OAuth {token}",
            "offset": "0",
            "file_size": str(file_size),
        },
        data=video_bytes,
        timeout=600,
    )
    raise_for_status_with_body(upload_resp)

    finish = requests.post(
        f"{GRAPH}/{page_id}/video_reels",
        data={
            "upload_phase": "finish",
            "video_id": video_id,
            "video_state": "PUBLISHED",
            "description": caption,
            "access_token": token,
        },
        timeout=60,
    )
    raise_for_status_with_body(finish)
    return video_id
