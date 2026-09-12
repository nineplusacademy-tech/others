"""인스타그램·페이스북 게시물/계정 인사이트 조회 (읽기 전용, 아무것도 게시하지 않음).

발행에 쓰는 것과 같은 토큰(INSTAGRAM_ACCESS_TOKEN, FACEBOOK_PAGE_ACCESS_TOKEN)을
재사용해 Meta Graph API의 인사이트 엔드포인트를 조회한다.

queue/_status.json에 남는 게시물 ID에 의존하지 않는다 — main.py가 전 채널
발행을 완료하면 그 즉시 queue 폴더 자체를 삭제하므로(_finish()) 게시물 ID가
남지 않는다. 대신 계정의 "최근 미디어/게시물 목록"을 API로 직접 가져와 그
안에서 최근 N개를 조회한다.

Meta는 인사이트 메트릭 이름을 API 버전마다 바꾸거나 폐기하는 일이 잦다 —
이 스크립트는 메트릭 요청 하나가 실패해도 나머지는 계속 진행하고, 실패한
이유를 결과에 그대로 남긴다(조용히 누락시키거나 0으로 채우지 않는다). 처음
실제로 돌려보기 전까지는 이 토큰들이 인사이트 조회 권한
(instagram_manage_insights, read_insights 등)까지 가지고 있는지 확인된 바
없다 — 첫 실행 결과를 반드시 확인할 것.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

import requests

from common import raise_for_status_with_body

IG_GRAPH = "https://graph.instagram.com"
FB_GRAPH = "https://graph.facebook.com/v21.0"


def _ig_id() -> str:
    return os.environ["INSTAGRAM_BUSINESS_ACCOUNT_ID"]


def _ig_token() -> str:
    return os.environ["INSTAGRAM_ACCESS_TOKEN"]


def _fb_page_id() -> str:
    return os.environ["FACEBOOK_PAGE_ID"]


def _fb_token() -> str:
    return os.environ["FACEBOOK_PAGE_ACCESS_TOKEN"]


def _get(url: str, params: dict) -> dict:
    resp = requests.get(url, params=params, timeout=30)
    raise_for_status_with_body(resp)
    return resp.json()


def _latest_values(data: dict) -> dict:
    return {
        item["name"]: item.get("values", [{}])[-1].get("value")
        for item in data.get("data", [])
    }


# ---------- 인스타그램 ----------


def list_recent_instagram_media(limit: int = 5) -> list[dict]:
    data = _get(
        f"{IG_GRAPH}/{_ig_id()}/media",
        {
            "fields": "id,caption,timestamp,media_type,media_product_type,permalink",
            "limit": limit,
            "access_token": _ig_token(),
        },
    )
    return data.get("data", [])


def instagram_media_insights(media_id: str, media_product_type: str) -> dict:
    """media_product_type(FEED/REELS 등)에 따라 지원되는 메트릭이 다르다."""
    metrics = (
        "reach,likes,comments,saved,shares,plays"
        if media_product_type == "REELS"
        else "reach,likes,comments,saved,shares"
    )
    result: dict = {"requested": metrics}
    try:
        data = _get(
            f"{IG_GRAPH}/{media_id}/insights",
            {"metric": metrics, "access_token": _ig_token()},
        )
        result["values"] = _latest_values(data)
    except Exception as exc:  # noqa: BLE001 — 실패도 결과에 남기고 계속 진행
        result["error"] = str(exc)
    return result


def instagram_account_summary() -> dict:
    result: dict = {}
    try:
        result["profile"] = _get(
            f"{IG_GRAPH}/{_ig_id()}",
            {"fields": "followers_count,media_count", "access_token": _ig_token()},
        )
    except Exception as exc:  # noqa: BLE001
        result["profile_error"] = str(exc)

    try:
        insights = _get(
            f"{IG_GRAPH}/{_ig_id()}/insights",
            {
                "metric": "reach,profile_views,accounts_engaged",
                "period": "day",
                "access_token": _ig_token(),
            },
        )
        result["account_insights"] = _latest_values(insights)
    except Exception as exc:  # noqa: BLE001
        result["account_insights_error"] = str(exc)
    return result


# ---------- 페이스북 ----------


def list_recent_facebook_posts(limit: int = 5) -> list[dict]:
    data = _get(
        f"{FB_GRAPH}/{_fb_page_id()}/posts",
        {
            "fields": "id,message,created_time,permalink_url",
            "limit": limit,
            "access_token": _fb_token(),
        },
    )
    return data.get("data", [])


def list_recent_facebook_videos(limit: int = 5) -> list[dict]:
    """릴스는 /video_reels API로 올라가 /posts에는 안 잡힐 수 있어 /videos도 따로 본다."""
    data = _get(
        f"{FB_GRAPH}/{_fb_page_id()}/videos",
        {
            "fields": "id,description,created_time,permalink_url",
            "limit": limit,
            "access_token": _fb_token(),
        },
    )
    return data.get("data", [])


def facebook_post_insights(post_id: str) -> dict:
    metrics = "post_impressions,post_engaged_users,post_reactions_by_type_total"
    result: dict = {"requested": metrics}
    try:
        data = _get(
            f"{FB_GRAPH}/{post_id}/insights",
            {"metric": metrics, "access_token": _fb_token()},
        )
        result["values"] = _latest_values(data)
    except Exception as exc:  # noqa: BLE001
        result["error"] = str(exc)
    return result


def facebook_video_insights(video_id: str) -> dict:
    metrics = "total_video_views,total_video_impressions,total_video_avg_time_watched"
    result: dict = {"requested": metrics}
    try:
        data = _get(
            f"{FB_GRAPH}/{video_id}/video_insights",
            {"metric": metrics, "access_token": _fb_token()},
        )
        result["values"] = _latest_values(data)
    except Exception as exc:  # noqa: BLE001
        result["error"] = str(exc)
    return result


def facebook_page_summary() -> dict:
    result: dict = {}
    try:
        result["page"] = _get(
            f"{FB_GRAPH}/{_fb_page_id()}",
            {"fields": "fan_count", "access_token": _fb_token()},
        )
    except Exception as exc:  # noqa: BLE001
        result["page_error"] = str(exc)

    try:
        insights = _get(
            f"{FB_GRAPH}/{_fb_page_id()}/insights",
            {
                "metric": "page_impressions,page_engaged_users",
                "period": "week",
                "access_token": _fb_token(),
            },
        )
        result["page_insights"] = _latest_values(insights)
    except Exception as exc:  # noqa: BLE001
        result["page_insights_error"] = str(exc)
    return result


def build_report(limit: int = 5) -> dict:
    """계정 요약 + 최근 게시물별 인사이트를 한 번에 모은다.

    부분 실패로 전체를 죽이지 않는다 — 발행을 막지 않는 순수 조회용이므로
    인스타그램만 실패해도 페이스북 결과는 그대로 돌려준다.
    """
    report: dict = {"generated_at": datetime.now(timezone.utc).isoformat()}

    try:
        report["instagram_account"] = instagram_account_summary()
        media = list_recent_instagram_media(limit=limit)
        report["instagram_media"] = [
            {**m, "insights": instagram_media_insights(m["id"], m.get("media_product_type", ""))}
            for m in media
        ]
    except Exception as exc:  # noqa: BLE001
        report["instagram_error"] = str(exc)

    try:
        report["facebook_page"] = facebook_page_summary()
        posts = list_recent_facebook_posts(limit=limit)
        report["facebook_posts"] = [
            {**p, "insights": facebook_post_insights(p["id"])} for p in posts
        ]
        videos = list_recent_facebook_videos(limit=limit)
        report["facebook_videos"] = [
            {**v, "insights": facebook_video_insights(v["id"])} for v in videos
        ]
    except Exception as exc:  # noqa: BLE001
        report["facebook_error"] = str(exc)

    return report


if __name__ == "__main__":
    import json

    print(json.dumps(build_report(), ensure_ascii=False, indent=2))
