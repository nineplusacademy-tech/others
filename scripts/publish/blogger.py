"""구글 블로그(Blogger) 게시글 자동 발행."""

from __future__ import annotations

import os

from googleapiclient.discovery import build

from common import DRY_RUN, dry_run_log
from google_auth import get_credentials


def publish(title: str, html_content: str, labels: list[str], search_description: str = "") -> str:
    """블로그 글을 즉시 공개로 게시하고, 게시된 글의 URL을 반환한다."""
    if DRY_RUN:
        dry_run_log(
            "Blogger",
            title=title,
            labels=", ".join(labels),
            search_description=search_description,
            content=html_content,
        )
        return "https://dry-run.invalid/blogger-post"

    creds = get_credentials()
    service = build("blogger", "v3", credentials=creds)

    body = {
        "kind": "blogger#post",
        "blog": {"id": os.environ["BLOGGER_BLOG_ID"]},
        "title": title,
        "content": html_content,
    }
    if labels:
        body["labels"] = labels
    if search_description:
        body["searchDescription"] = search_description

    result = (
        service.posts()
        .insert(blogId=os.environ["BLOGGER_BLOG_ID"], body=body, isDraft=False)
        .execute()
    )
    post_id = result["id"]

    # Blogger API v3의 알려진 결함 — posts.insert에 searchDescription을(가끔 labels도)
    # 함께 보내도 저장되지 않는 경우가 있다(2026-09-15 37주차 실사고로 확인, 구글
    # 지원 포럼에도 동일 사례 다수 보고됨). 게시 직후 실제로 반영됐는지 다시 읽어
    # 확인하고, 빠진 필드만 patch로 최대 2회까지 재시도한다 — "보냈으니 됐겠지"로
    # 끝내지 않고 끝까지 확인해서, 여전히 안 붙으면 발행 자체를 에러로 멈춘다(조용히
    # 라벨·검색설명 없이 게시되지 않게).
    for attempt in range(2):
        fetched = service.posts().get(blogId=os.environ["BLOGGER_BLOG_ID"], postId=post_id).execute()
        missing_description = bool(search_description) and fetched.get("searchDescription") != search_description
        missing_labels = bool(labels) and set(fetched.get("labels", [])) != set(labels)
        if not missing_description and not missing_labels:
            break
        patch_body: dict = {}
        if missing_description:
            patch_body["searchDescription"] = search_description
        if missing_labels:
            patch_body["labels"] = labels
        service.posts().patch(
            blogId=os.environ["BLOGGER_BLOG_ID"], postId=post_id, body=patch_body
        ).execute()
    else:
        fetched = service.posts().get(blogId=os.environ["BLOGGER_BLOG_ID"], postId=post_id).execute()
        if (bool(search_description) and fetched.get("searchDescription") != search_description) or (
            bool(labels) and set(fetched.get("labels", [])) != set(labels)
        ):
            raise RuntimeError(
                f"[blogger] 게시는 됐지만({fetched.get('url')}) 라벨·검색설명이 2번 재시도 후에도 "
                "반영되지 않았습니다 — Blogger 관리 화면에서 직접 확인해주세요."
            )

    return result["url"]
