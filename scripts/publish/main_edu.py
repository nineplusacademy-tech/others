"""교육뉴스 발행 오케스트레이터 (구글 블로그 채널만).

education-news-team은 이 저장소 스킬이며, 산출물은 평소 로컬
`클로드작업폴더/교육뉴스/`에만 보관한다(docs/education-news-log.md 참고). 8개
채널 중 공식 발행 API가 있는 채널은 구글 블로그(Blogger API)뿐이라, 이 스크립트는
그 한 채널만 자동 발행한다 — 나머지 7채널(밴드·네이버블로그·유튜브 커뮤니티·당근·
카카오톡채널·네이버플레이스)은 여전히 사람이 로컬 산출물을 보고 체크리스트대로
직접 게시한다.

메인 블로그 파이프라인과 같은 시각(화요일 10:00 KST)에 발행하도록 2026-09-08에
맞췄다(`docs/mainmanager-plan.md` §1-1). main.py와 달리 채널이 하나뿐이라
스레드풀 등 병렬화가 필요 없다. 큐 폴더 형식은 main.py의 queue/ 와 동일하게
`구글블로그용.md`(YAML 프런트매터 + HTML 본문)를 그대로 재사용한다.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import blogger
from common import DRY_RUN, parse_frontmatter

QUEUE_EDU_DIR = Path("queue-edu")


def find_queue_edu_folder() -> Path | None:
    """queue-edu/ 아래에서 처리할 폴더 하나를 찾는다."""
    if not QUEUE_EDU_DIR.exists():
        return None
    candidates = sorted(p for p in QUEUE_EDU_DIR.iterdir() if p.is_dir())
    return candidates[0] if candidates else None


def run(folder: Path) -> None:
    meta, html = parse_frontmatter(folder / "구글블로그용.md")
    url = blogger.publish(meta.get("title", ""), html, meta.get("labels") or ["교육뉴스"])
    print(f"[교육뉴스-blogger] 발행 완료: {url}")

    if DRY_RUN:
        print(f"[DRY RUN] '{folder.name}' 시뮬레이션 완료 — 큐 폴더는 삭제하지 않음")
        return

    shutil.rmtree(folder)
    print(f"'{folder.name}' 발행 완료 — 큐에서 삭제")


def main() -> None:
    folder = find_queue_edu_folder()
    if folder is None:
        print("발행할 교육뉴스가 queue-edu/ 에 없음 — 종료")
        return
    run(folder)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — 실패 원인을 그대로 Actions 로그에 남김
        print(f"교육뉴스 발행 중 오류 발생: {exc}", file=sys.stderr)
        sys.exit(1)
