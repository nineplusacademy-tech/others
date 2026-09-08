"""네이버 블로그 글 URL을 기록한다 — 메인 블로그용 또는 교육뉴스용.

네이버 블로그는 반자동(사람이 직접 예약/발행)이라 자동화 파이프라인이 그
URL을 알 방법이 없다. 카드뉴스·숏츠 캡션의 {{BLOG_URL}}과, 화/목 주 2회로 늘어난
스레드(Threads) 게시물은 원문으로 안내하는 자리이고, 독자가 실제로 아는
"블로그"는 구글 블로그(완전자동 SEO/AEO 미러)가 아니라 네이버 블로그이므로,
사람이 네이버 블로그를 예약/발행한 직후 이 스크립트로 실제 URL을 기록해둔다.

**메인 블로그용** (기본, 인자 1개): `queue/` 아래 처리 중인 큐 폴더의
`_status.json`에 `naver_blog_url`로 기록한다 — main.py가 수요일(카드뉴스)·
목요일(릴스·쇼츠) 배치에서 캡션의 {{BLOG_URL}}을 채울 때 이 값을 우선해서
읽는다. 화요일 스레드(원문 링크만 게시하는 주)에도 이 값을 그대로 쓴다.

**교육뉴스용** (`--edu` 플래그): 교육뉴스는 `queue-edu/<날짜>_<주제>/`가 구글
블로그 발행 성공 즉시 삭제되는 구조라(education-news-publishing.md 참고) 그
안에 목요일까지 상태를 들고 있을 곳이 없다. 그래서 저장소 루트의
`queue/_edu_thread_link.json`에 별도로 적어둔다 — 목요일 스레드(교육뉴스
링크 게시)가 이 파일을 읽고, 다 쓰면 삭제한다.

기록해두지 않으면 main.py가 경고를 남기고 구글 블로그 주소로 대체한다(메인
블로그 쪽 한정 — 조용히 잘못된 링크로 나가는 것을 막기 위함일 뿐 정상 동작은
아니다). 교육뉴스 쪽은 기록이 없으면 목요일 스레드를 사람이 직접 채워야 한다.

사용법 (저장소 루트에서):
  python scripts/publish/set_naver_url.py <네이버 블로그 글 URL>          # 메인 블로그
  python scripts/publish/set_naver_url.py --edu <네이버 블로그 글 URL>    # 교육뉴스
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

from common import QUEUE_DIR, find_queue_folder, load_status, save_status

EDU_LINK_FILE = QUEUE_DIR / "_edu_thread_link.json"


def _usage_and_exit() -> None:
    print(
        "사용법: python scripts/publish/set_naver_url.py [--edu] <네이버 블로그 글 URL>\n"
        "예(메인 블로그): python scripts/publish/set_naver_url.py https://blog.naver.com/math20335/224404199642\n"
        "예(교육뉴스):     python scripts/publish/set_naver_url.py --edu https://blog.naver.com/math20335/224404199999",
        file=sys.stderr,
    )
    sys.exit(1)


def main() -> None:
    args = sys.argv[1:]
    is_edu = "--edu" in args
    if is_edu:
        args.remove("--edu")

    if len(args) != 1 or not args[0].startswith("https://blog.naver.com/"):
        _usage_and_exit()

    url = args[0]

    if is_edu:
        QUEUE_DIR.mkdir(exist_ok=True)
        EDU_LINK_FILE.write_text(
            json.dumps({"url": url, "recorded_at": date.today().isoformat()}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"교육뉴스 스레드용 URL 기록 완료 ({EDU_LINK_FILE}): {url}")
        print("목요일 스레드 게시 후에는 이 파일을 지워도 됩니다(다음 주 화요일에 다시 기록됨).")
        return

    folder = find_queue_folder()
    if folder is None:
        print("큐(queue/)에 처리할 폴더가 없습니다.", file=sys.stderr)
        sys.exit(1)

    status = load_status(folder)
    status["naver_blog_url"] = url
    save_status(folder, status)
    print(f"'{folder.name}' 큐에 네이버 블로그 URL 기록 완료: {url}")


if __name__ == "__main__":
    main()
