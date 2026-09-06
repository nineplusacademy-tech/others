"""구글 블로그(Blogger) 게시글 자동 발행."""

from __future__ import annotations

import os

from googleapiclient.discovery import build

from google_auth import get_credentials


def publish(title: str, html_content: str, labels: list[str]) -> str:
    """블로그 글을 즉시 공개로 게시하고, 게시된 글의 URL을 반환한다."""
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

    result = (
        service.posts()
        .insert(blogId=os.environ["BLOGGER_BLOG_ID"], body=body, isDraft=False)
        .execute()
    )
    return result["url"]
