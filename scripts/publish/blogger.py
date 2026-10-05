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
        # 2026-09-29 개선 — 재발 원인 진단을 위해 실제로 무엇이 돌아왔는지 로그에 남긴다
        # (그동안은 "안 붙었다"는 결론만 남고 실제 API 응답값이 안 보여 왜 안 붙는지
        # 알 수 없었다 — 9/29 10주차에서 라벨·검색설명이 4번 보정 후에도 전부 실패).
        fetched = service.posts().get(blogId=blog_id, postId=post_id).execute()
        actual_description = fetched.get("searchDescription")
        actual_labels = fetched.get("labels", [])
        log(
            f"[blogger] 확인: searchDescription={actual_description!r} "
            f"labels={actual_labels!r} (기대: description={search_description!r} labels={labels!r})"
        )
        # 2026-10-05: 검색설명은 보정 대상에서 뺐다 — Blogger API v3의 Post 리소스에는 애초에
        # searchDescription 필드가 없다(discovery 문서의 Post 속성: author·blog·content·
        # customMetaData·etag·id·images·kind·labels·location·published·readerComments·replies·
        # selfLink·status·title·titleLink·trashed·updated·url). insert/patch/update에 보내도
        # 서버가 조용히 무시하므로 몇 번을 재시도해도 반영되지 않는다(9/15·9/22·9/28·9/29·10/5
        # 반복 실사고의 진짜 원인). 그래서 라벨만 재시도 대상으로 두고, 검색설명은 끝에서
        # 붙여넣을 문구를 경고로 남겨 사람이 Blogger 관리 화면에서 넣게 한다.
        return (
            False,
            bool(labels) and set(actual_labels) != set(labels),
        )

    def _done() -> str:
        if search_description:
            log(
                f"::warning::[blogger] 검색설명은 Blogger API가 지원하지 않아 자동 입력되지 않습니다 — "
                f"{url} 글의 Blogger 관리 화면(게시물 설정 > 검색 설명)에 아래 문구를 붙여넣어 주세요: "
                f"{search_description}"
            )
        return url

    # 2026-09-24 개선 — 예전엔 대기 없이 patch만 2번 시도했는데(9/15·9/22 두 번 다 실패),
    # ①저장 반영에 시간이 걸릴 수 있어 매 시도 전에 점점 늘어나는 간격(2·5·10·20초)을 두고
    # ②patch를 2번 시도해도 안 되면 posts.update(PUT, 제목·본문·라벨·검색설명 전체)로
    # 방식을 바꿔 4번까지 시도한다. 그래도 안 되면 위 원칙대로 경고만 남긴다.
    # 2026-09-28 개선 — 이 루프 안의 모든 API 호출(_missing의 get 포함)을 try/except로
    # 감싼다. 감싸지 않았던 탓에 교육뉴스 9/28호에서 patch 단계의 일시적 HttpError 503
    # (Blogger 백엔드 일시 장애)이 그대로 위로 전파돼 "발행 실패"로 잘못 기록됐다 —
    # 글 자체(insert)는 이미 성공해 라이브였는데도 워크플로가 실패 처리되면서 큐 폴더가
    # 안 지워졌고, 다음 재시도가 같은 글을 다시 insert해 중복 게시할 뻔했다. 이 시점부터
    # 절대 예외를 던지지 않는다는 원칙(위 주석)을 코드로도 지키도록, 무엇이 됐든 실패하면
    # 즉시 루프를 멈추고 경고만 남긴 뒤 url을 반환한다.
    delays = (2, 5, 10, 20)
    for attempt, delay in enumerate(delays):
        time.sleep(delay)
        try:
            missing_description, missing_labels = _missing()
            if not missing_labels:
                return _done()
            if attempt < 2:
                patch_body: dict = {}
                if missing_description:
                    patch_body["searchDescription"] = search_description
                if missing_labels:
                    patch_body["labels"] = labels
                patch_result = service.posts().patch(blogId=blog_id, postId=post_id, body=patch_body).execute()
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
                patch_result = service.posts().update(blogId=blog_id, postId=post_id, body=full_body).execute()
            log(
                f"[blogger] 라벨·검색설명 보정 시도 {attempt + 1}/{len(delays)} "
                f"({'patch' if attempt < 2 else 'update'}) — 응답: "
                f"searchDescription={patch_result.get('searchDescription')!r} labels={patch_result.get('labels')!r}"
            )
        except Exception as exc:  # noqa: BLE001 — Blogger API의 일시적 오류(503 등)까지 포함
            log(
                f"::warning::[blogger] 게시는 됐지만({url}) 라벨·검색설명 보정 {attempt + 1}번째 시도 중 "
                f"오류가 나서 중단합니다: {exc}. 발행은 완료로 처리하고 계속 진행합니다 — "
                "Blogger 관리 화면에서 직접 채워주세요."
            )
            return _done()

    try:
        time.sleep(5)
        missing_description, missing_labels = _missing()
    except Exception as exc:  # noqa: BLE001
        log(f"::warning::[blogger] 최종 확인 중 오류(무시하고 계속): {exc}")
        return _done()

    if missing_labels:
        # "::warning::"는 GitHub Actions 워크플로 명령 문법 — 일반 로그에 묻히지 않고 실행
        # 화면 상단 Annotations에 노란 경고로 뜬다. 발행 자체는 성공(초록)이라 이게 없으면
        # 검색설명 누락을 놓치기 쉽다.
        log(
            f"::warning::[blogger] 게시는 됐지만({url}) 라벨이 {len(delays)}번 보정 후에도 "
            "반영되지 않았습니다. 발행은 완료로 처리하고 계속 진행합니다 — "
            "Blogger 관리 화면에서 직접 채워주세요."
        )

    return _done()
