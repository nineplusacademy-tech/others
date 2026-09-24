"""구글 블로그(Blogger) 게시글 자동 발행."""

from __future__ import annotations

import os
import time

from googleapiclient.discovery import build

from common import DRY_RUN, dry_run_log, log
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
    # 함께 보내도 저장되지 않는 경우가 있다(2026-09-15 37주차, 2026-09-22 9주차·
    # 교육뉴스 실사고로 확인, 구글 지원 포럼에도 동일 사례 다수 보고됨). 게시 직후
    # 실제로 반영됐는지 다시 읽어 확인하고, 빠진 필드만 patch로 최대 2회까지
    # 재시도한다.
    #
    # 2026-09-22 변경: 글 자체는 이미 공개(insert)됐으므로, 이 시점부터는 절대
    # 예외를 던지지 않는다 — 예전엔 2회 재시도 후에도 안 붙으면 RuntimeError를
    # 던졌는데, 그러면 main.py/main_edu.py가 "발행 실패"로 처리해 _status.json에
    # blogger 완료를 기록하지 못했고, 다음 배치(수/목)나 재실행이 이미 라이브인
    # 글을 다시 insert해서 중복 게시를 만들 위험이 있었다(9/22 실제 확인). 라벨·
    # 검색설명 미반영은 Blogger 관리 화면에서 사람이 손으로 채워도 되는 사소한
    # 문제이지, 발행 자체를 막을 이유가 아니다 — 안 붙으면 경고만 남기고 URL을
    # 그대로 반환한다.
    url = result["url"]
    blog_id = os.environ["BLOGGER_BLOG_ID"]

    def _missing() -> tuple[bool, bool]:
        fetched = service.posts().get(blogId=blog_id, postId=post_id).execute()
        return (
            bool(search_description) and fetched.get("searchDescription") != search_description,
            bool(labels) and set(fetched.get("labels", [])) != set(labels),
        )

    # 2026-09-24 개선 — 예전엔 대기 없이 patch만 2번 시도했는데(9/15·9/22 두 번 다 실패),
    # ①저장 반영에 시간이 걸릴 수 있어 매 시도 전에 점점 늘어나는 간격(2·5·10·20초)을 두고
    # ②patch를 2번 시도해도 안 되면 posts.update(PUT, 제목·본문·라벨·검색설명 전체)로
    # 방식을 바꿔 4번까지 시도한다. 그래도 안 되면 위 원칙대로 경고만 남긴다.
    delays = (2, 5, 10, 20)
    for attempt, delay in enumerate(delays):
        time.sleep(delay)
        missing_description, missing_labels = _missing()
        if not missing_description and not missing_labels:
            return url
        if attempt < 2:
            patch_body: dict = {}
            if missing_description:
                patch_body["searchDescription"] = search_description
            if missing_labels:
                patch_body["labels"] = labels
            service.posts().patch(blogId=blog_id, postId=post_id, body=patch_body).execute()
        else:
            full_body = {
                "id": post_id,
                "blog": {"id": blog_id},
                "title": title,
                "content": html_content,
            }
            if labels:
                full_body["labels"] = labels
            if search_description:
                full_body["searchDescription"] = search_description
            service.posts().update(blogId=blog_id, postId=post_id, body=full_body).execute()
        log(f"[blogger] 라벨·검색설명 보정 시도 {attempt + 1}/{len(delays)} ({'patch' if attempt < 2 else 'update'})")

    time.sleep(5)
    missing_description, missing_labels = _missing()
    if missing_description or missing_labels:
        # "::warning::"는 GitHub Actions 워크플로 명령 문법 — 일반 로그에 묻히지 않고 실행
        # 화면 상단 Annotations에 노란 경고로 뜬다. 발행 자체는 성공(초록)이라 이게 없으면
        # 검색설명 누락을 놓치기 쉽다.
        log(
            f"::warning::[blogger] 게시는 됐지만({url}) 라벨·검색설명이 {len(delays)}번 보정 후에도 "
            "반영되지 않았습니다. 발행은 완료로 처리하고 계속 진행합니다 — "
            "Blogger 관리 화면에서 직접 채워주세요."
        )

    return url
