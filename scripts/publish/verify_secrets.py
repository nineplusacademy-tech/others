"""등록된 Secrets가 실제로 유효한지 읽기 전용으로 점검한다 (아무것도 게시하지 않음).

GitHub Actions에서 workflow_dispatch로 수동 실행해 결과를 로그로 확인하는 용도.
절대 토큰 값 자체는 print/log 하지 않는다 — 저장소가 퍼블릭이라 로그도 공개됨.
"""

from __future__ import annotations

import os
import sys

import requests

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, fn) -> None:
    try:
        detail = fn()
        RESULTS.append((name, True, detail))
    except Exception as exc:  # noqa: BLE001
        RESULTS.append((name, False, f"{type(exc).__name__}: {exc}"))


def check_google() -> str:
    from google_auth import get_credentials  # noqa: PLC0415
    from googleapiclient.discovery import build  # noqa: PLC0415

    creds = get_credentials()
    blogger = build("blogger", "v3", credentials=creds)
    blog = blogger.blogs().get(blogId=os.environ["BLOGGER_BLOG_ID"]).execute()

    youtube = build("youtube", "v3", credentials=creds)
    channels = youtube.channels().list(part="snippet", mine=True).execute()
    channel_name = channels["items"][0]["snippet"]["title"] if channels.get("items") else "?"

    return f"blog='{blog.get('name')}' ({blog.get('url')}), youtube channel='{channel_name}'"


def check_facebook_page() -> str:
    resp = requests.get(
        f"https://graph.facebook.com/v21.0/{os.environ['FACEBOOK_PAGE_ID']}",
        params={
            "fields": "name,id",
            "access_token": os.environ["FACEBOOK_PAGE_ACCESS_TOKEN"],
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return f"page='{data.get('name')}' (id={data.get('id')})"


def check_instagram() -> str:
    resp = requests.get(
        f"https://graph.facebook.com/v21.0/{os.environ['INSTAGRAM_BUSINESS_ACCOUNT_ID']}",
        params={
            "fields": "username,id",
            "access_token": os.environ["INSTAGRAM_ACCESS_TOKEN"],
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return f"account=@{data.get('username')} (id={data.get('id')})"


def check_gh_pat() -> str:
    resp = requests.get(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/actions/secrets/public-key",
        headers={
            "Authorization": f"Bearer {os.environ['GH_PAT']}",
            "Accept": "application/vnd.github+json",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return "Secrets API 읽기 성공 (write 권한은 실제 갱신 시 확인됨)"


def main() -> None:
    check("Google (Blogger + YouTube OAuth, BLOGGER_BLOG_ID)", check_google)
    check("Facebook 페이지 (FACEBOOK_PAGE_ID + FACEBOOK_PAGE_ACCESS_TOKEN)", check_facebook_page)
    check(
        "Instagram (INSTAGRAM_BUSINESS_ACCOUNT_ID + INSTAGRAM_ACCESS_TOKEN)",
        check_instagram,
    )
    check("GH_PAT (Secrets API 접근)", check_gh_pat)

    print("\n===== 자격증명 점검 결과 =====")
    all_ok = True
    for name, ok, detail in RESULTS:
        mark = "OK " if ok else "FAIL"
        print(f"[{mark}] {name} — {detail}")
        all_ok = all_ok and ok
    print("=============================\n")

    if not all_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
