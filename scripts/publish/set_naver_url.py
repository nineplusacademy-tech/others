"""네이버 블로그 글 URL을 큐의 _status.json에 기록한다.

네이버 블로그는 반자동(사람이 직접 예약/발행)이라 자동화 파이프라인이 그
URL을 알 방법이 없다. 카드뉴스·숏츠 캡션의 {{BLOG_URL}}은 원문으로 안내하는
자리이고, 독자가 실제로 아는 "블로그"는 구글 블로그(완전자동 SEO/AEO 미러)가
아니라 네이버 블로그이므로, 사람이 네이버 블로그를 예약/발행한 직후 이
스크립트로 실제 URL을 큐에 적어둔다 — main.py가 수요일(카드뉴스)·목요일
(릴스·쇼츠) 배치에서 {{BLOG_URL}}을 채울 때 이 값을 우선해서 읽는다.

기록해두지 않으면 main.py가 경고를 남기고 구글 블로그 주소로 대체한다(조용히
잘못된 링크로 나가는 것을 막기 위함일 뿐, 정상 동작은 아니다).

사용법 (저장소 루트에서): python scripts/publish/set_naver_url.py <네이버 블로그 글 URL>
"""

from __future__ import annotations

import sys

from common import find_queue_folder, load_status, save_status


def main() -> None:
    if len(sys.argv) != 2 or not sys.argv[1].startswith("https://blog.naver.com/"):
        print(
            "사용법: python scripts/publish/set_naver_url.py <네이버 블로그 글 URL>\n"
            "예: python scripts/publish/set_naver_url.py https://blog.naver.com/math20335/224404199642",
            file=sys.stderr,
        )
        sys.exit(1)

    url = sys.argv[1]
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
