"""페이스북 페이지 게시글(사진) + 릴스 발행."""

from __future__ import annotations

import os
from pathlib import Path

import requests

from common import DRY_RUN, dry_run_log

GRAPH = "https://graph.facebook.com/v21.0"


def _page_id() -> str:
    return os.environ["FACEBOOK_PAGE_ID"]


def _page_token() -> str:
    return os.environ["FACEBOOK_PAGE_ACCESS_TOKEN"]


def publish_photo_post(image_path: Path, caption: str) -> str:
    """카드뉴스 표지 이미지 + 캡션(블로그 링크 포함)으로 페이지 게시글을 올린다."""
    if DRY_RUN:
        dry_run_log("Facebook 게시글", image=str(image_path), caption=caption)
        return "dryrun-facebook-post"

    url = f"{GRAPH}/{_page_id()}/photos"
    with open(image_path, "rb") as f:
        resp = requests.post(
            url,
            data={"caption": caption, "access_token": _page_token()},
            files={"source": f},
            timeout=120,
        )
    resp.raise_for_status()
    return resp.json()["id"]


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
    start.raise_for_status()
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
    upload_resp.raise_for_status()

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
    finish.raise_for_status()
    return video_id
