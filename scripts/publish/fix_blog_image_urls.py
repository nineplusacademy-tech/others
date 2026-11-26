"""게시된 구글 블로그 글의 사진 주소를 queue/ 커밋 주소에서 assets/ 보존본으로 바꾼다.

기본은 미리보기(아무것도 바꾸지 않음)다. --apply 를 붙여야 글을 수정하고, --limit 으로
처음 몇 개만 수정해 볼 수 있다. 본문(content)의 사진 주소만 바꾼다.

미리보기는 자격증명 없이 공개 피드로 동작한다.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import quote, unquote

REPO = "nineplusacademy-tech/others"
BRANCH = "claude/academy-marketing-automation-lquj1w"
FEED = "https://nineplus-academy.blogspot.com/feeds/posts/default?alt=json&max-results=150"
OLD = re.compile(
    r"https://raw\.githubusercontent\.com/" + re.escape(REPO) + r"/[0-9a-f]{40}/queue/[^\"'<>\s]+"
)


def new_url(old: str) -> str:
    parts = unquote(old).split("/")
    i = parts.index("queue")
    preserved = Path("assets/blog-images") / parts[i + 1] / parts[-1]
    if not preserved.exists():
        raise FileNotFoundError(f"보존본 없음: {preserved}")
    encoded = "/".join(quote(segment) for segment in preserved.as_posix().split("/"))
    return f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{encoded}"


def rewrite(html: str) -> tuple[str, int]:
    return OLD.subn(lambda m: new_url(m.group(0)), html)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="수정할 글 수(0=전부)")
    args = parser.parse_args()

    if not args.apply:
        entries = json.load(urllib.request.urlopen(FEED, timeout=60))["feed"]["entry"]
        posts = [
            (e["published"]["$t"][:10], e["title"]["$t"], e.get("content", {}).get("$t", ""))
            for e in entries
        ]
        service = blog_id = None
    else:
        from googleapiclient.discovery import build

        from google_auth import get_credentials

        service = build("blogger", "v3", credentials=get_credentials())
        blog_id = os.environ["BLOGGER_BLOG_ID"]
        posts, token = [], None
        while True:
            page = service.posts().list(
                blogId=blog_id, maxResults=50, pageToken=token, fetchBodies=True, status="LIVE"
            ).execute()
            posts += [(p["published"][:10], p["title"], p.get("content", ""), p["id"]) for p in page.get("items", [])]
            token = page.get("nextPageToken")
            if not token:
                break

    changed = total = 0
    for post in posts:
        date, title, html = post[:3]
        updated, count = rewrite(html)
        if not count:
            continue
        if args.limit and changed >= args.limit:
            break
        if args.apply:
            service.posts().patch(blogId=blog_id, postId=post[3], body={"content": updated}).execute()
        changed += 1
        total += count
        print(f"{'수정' if args.apply else '대상'} {date} 사진 {count}개 · {title}")
    print(f"글 {changed}개, 사진 {total}개 ({'수정 완료' if args.apply else '미리보기 — 변경 없음'})")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
