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

    # youtube.upload 권한은 업로드(videos.insert) 전용이라 channels.list 같은 조회
    # 호출엔 애초에 쓸 수 없다 (Google이 요구하는 별도 scope: youtube/youtube.readonly
    # 등). 그래서 여기선 채널 조회로 검증하지 않고, refresh 성공 자체로 client_id/
    # secret/refresh_token이 유효함을 확인한 것으로 충분하다고 본다. 실제 업로드
    # 권한(youtube.upload) 자체는 발행 워크플로가 처음 영상을 올릴 때 검증된다.
    return f"blog='{blog.get('name')}' ({blog.get('url')}) — OAuth 갱신 성공 (youtube.upload 범위는 업로드 시 검증됨)"


def _graph_get(base: str, node_id: str, fields: str, access_token: str) -> dict:
    """Graph API GET 호출. 실패 시 돌려준 error 객체를 그대로 예외 메시지에
    담는다 (토큰 값은 에러 응답에 echo되지 않으므로 안전)."""
    resp = requests.get(
        f"{base}/{node_id}",
        params={"fields": fields, "access_token": access_token},
        timeout=30,
    )
    if not resp.ok:
        try:
            detail = resp.json().get("error", resp.text)
        except ValueError:
            detail = resp.text
        raise RuntimeError(f"HTTP {resp.status_code} — {detail}")
    return resp.json()


def check_facebook_page() -> str:
    data = _graph_get(
        "https://graph.facebook.com/v21.0",
        os.environ["FACEBOOK_PAGE_ID"],
        "name,id",
        os.environ["FACEBOOK_PAGE_ACCESS_TOKEN"],
    )
    return f"page='{data.get('name')}' (id={data.get('id')})"


def check_instagram() -> str:
    # "Instagram 로그인이 포함된 API" 방식으로 발급된 토큰이라 graph.facebook.com이
    # 아니라 graph.instagram.com 이어야 한다 (Facebook 로그인 방식과는 다른 도메인).
    data = _graph_get(
        "https://graph.instagram.com",
        os.environ["INSTAGRAM_BUSINESS_ACCOUNT_ID"],
        "username,id",
        os.environ["INSTAGRAM_ACCESS_TOKEN"],
    )
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
