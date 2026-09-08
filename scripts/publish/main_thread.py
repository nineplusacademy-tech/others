"""스레드(메인 블로그) 화요일 12:30 자동 게시 오케스트레이터.

메인 블로그 파이프라인(queue/)과 같은 폴더를 보되, main.py(블로그·카드뉴스·
릴스/쇼츠 3단계)와는 별도로 화요일 12:30 KST에 독립 실행된다
(`docs/mainmanager-plan.md` §1-1). 카드뉴스 캐러셀 첨부 없이 텍스트(+ 네이버
블로그 링크)만 자동 게시한다 — 이미지를 첨부하기로 한 주는 당분간 사람이
그대로 수동 게시한다(`content-playbook.md` §9).

블로그(--phase blog, 10:00 KST)가 먼저 끝나 있어야 하고, 그 직후 사람이
`set_naver_url.py`로 기록한 네이버 블로그 URL이 있어야 한다 — 아직 없으면
(사람이 아직 네이버에 발행/기록하지 않은 상태) 에러로 멈춘다. `_status.json`의
"thread" 키로 중복 게시를 막지만, ALL_STEPS(main.py가 큐 폴더 삭제 여부를
판단하는 목록)에는 포함하지 않는다 — 스레드 게시가 늦어져도 기존 4채널
완료 후 큐 폴더가 정상적으로 삭제되게 하기 위함이다.
"""

from __future__ import annotations

import sys

import threads
from common import DRY_RUN, fill_placeholders, find_queue_folder, load_status, save_status, step_done


def run() -> None:
    folder = find_queue_folder()
    if folder is None:
        print("발행할 콘텐츠가 queue/ 에 없음 — 종료")
        return

    status = load_status(folder)

    if not step_done(status, "blogger"):
        raise RuntimeError(
            f"'{folder.name}' 블로그가 아직 발행되지 않았습니다 — "
            "먼저 화요일 10:00 블로그 배치(--phase blog)가 끝나야 합니다."
        )

    naver_url = status.get("naver_blog_url")
    if not naver_url:
        raise RuntimeError(
            f"'{folder.name}'에 naver_blog_url이 없습니다 — 네이버 블로그를 "
            "발행한 뒤 'python scripts/publish/set_naver_url.py <URL>'로 기록해주세요."
        )

    if step_done(status, "thread"):
        print(f"'{folder.name}' 스레드는 이미 게시됨 — 건너뜀")
        return

    thread_md = folder / "스레드.md"
    if not thread_md.exists():
        print(f"'{folder.name}'에 스레드.md가 없음 — 이번 주는 자동 게시 대상 아님(건너뜀)")
        return

    text = fill_placeholders(thread_md.read_text(encoding="utf-8").strip(), BLOG_URL=naver_url)
    result_id = threads.publish_text(text)

    if not DRY_RUN:
        status["thread"] = {"done": True, "id": result_id}
        save_status(folder, status)
    print(f"[thread] 발행 완료: {result_id}")


def main() -> None:
    run()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — 실패 원인을 그대로 Actions 로그에 남김
        print(f"스레드 발행 중 오류 발생: {exc}", file=sys.stderr)
        sys.exit(1)
