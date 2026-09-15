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

    # Blogger API v3의 알려진 결함 — posts.insert에 searchDescription을 함께 보내도
    # 저장되지 않는 경우가 있다(2026-09-15 37주차 실사고로 확인, 구글 지원 포럼에도
    # 동일 사례 다수 보고됨). 게시 직후 patch로 한 번 더 명시적으로 설정해 확실히
    # 반영시킨다.
    if search_description:
        service.posts().patch(
            blogId=os.environ["BLOGGER_BLOG_ID"],
            postId=result["id"],
            body={"searchDescription": search_description},
        ).execute()

    return result["url"]
