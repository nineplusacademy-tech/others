"""예약 발행 오케스트레이터.

queue/ 아래 폴더 하나를 찾아 6개 채널에 발행한다. 각 단계 성공 여부를
_status.json에 기록해 재실행 시 이미 성공한 채널은 건너뛴다. 전부 성공하면
큐 폴더를 삭제한다.

2026-09-09부로 발행이 **3단계 배치**로 나뉜다(`docs/mainmanager-plan.md` §1-1
참고 — 블로그로 검색 유입을 먼저 잡고, 카드뉴스와 릴스/쇼츠를 하루씩 띄워
같은 팔로워에게 같은 시각 두 게시물이 알고리즘 노출을 서로 갉아먹지 않게 하고,
카드뉴스(저장·정독)와 릴스(발견·확산)가 서로 다른 날 각자의 확산 곡선을
갖게 한다):

- `--phase blog` (화요일 10:00 KST): 구글 블로그만 발행하고 끝낸다. 다른 채널
  캡션이 이 URL을 참조하므로 반드시 먼저 끝나야 한다. 이 단계만으로는
  `_status.json`이 전부 완료되지 않으므로 큐 폴더는 삭제되지 않고 다음 배치를
  기다린다.
- `--phase cardnews` (수요일 20:00 KST): 블로그가 이미 끝나 있다고 가정하고
  (안 끝나 있으면 에러) 카드뉴스 캐러셀 2채널(FB 캐러셀·IG 캐러셀)을 동시에
  발행한다.
- `--phase social` (목요일 20:00 KST): 블로그가 이미 끝나 있다고 가정하고
  릴스/쇼츠 3채널(FB 릴스·IG 릴스·YT 쇼츠)을 스레드풀로 동시에 발행한다 —
  특히 인스타 릴스는 처리 완료까지 최대 5분 폴링이라, 순차 실행이면 그 대기
  시간이 전체 소요 시간에 그대로 더해진다. 동시 실행하면 전체 소요 시간이
  "3개 합산"이 아니라 "3개 중 가장 오래 걸리는 것" 기준으로 줄어든다.
- `--phase all`(기본값, 생략 시): 예전처럼 블로그+카드뉴스+릴스를 한 번에
  순서대로 전부 실행한다 — 수동 재시도나 dry-run 점검용.

6개 채널 전부 끝나면(세 배치 모두 성공하면) 큐 폴더를 삭제한다.

이 파일은 python scripts/publish/main.py [--phase blog|cardnews|social|all] 로
저장소 루트에서 실행한다(.github/workflows/publish.yml 참고). 실제로
Secrets/토큰 값을 print하지 않는다.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import blogger
import facebook
import instagram
import youtube
from common import (
    DRY_RUN,
    all_steps_done,
    fill_image_placeholders,
    fill_placeholders,
    find_queue_folder,
    load_status,
    log,
    parse_caption_sections,
    parse_frontmatter,
    save_status,
    step_done,
)

_status_lock = threading.Lock()


def _require_caption(caption: str, channel: str, section: str) -> str:
    """캡션이 빈 문자열이면 발행을 막고 즉시 에러를 낸다.

    2026-09-11 신설 — 채널별_캡션.md의 섹션명이 조회 키와 안 맞으면
    parse_caption_sections()가 조용히 빈 문자열을 반환해, 36주차 릴스가
    캡션 없이 그대로 게시된 실사고가 있었다. 원인 자체는 이미 고쳤지만
    (섹션명 뒤 괄호 정규화), 앞으로 같은 종류의 실수(섹션명 오타 등)가 다시
    생겨도 조용히 넘어가지 않고 여기서 확실히 막는다 — 캡션 없는 발행은
    항상 버그이지 정상 상태가 아니다.
    """
    if not caption or not caption.strip():
        raise RuntimeError(
            f"[{channel}] 캡션이 비어 있어 발행을 중단합니다 — "
            f"채널별_캡션.md의 '## {section}' 섹션을 확인하세요."
        )
    return caption


def _record(folder: Path, status: dict, key: str, result_field: str, value: str) -> None:
    """여러 스레드에서 동시에 상태를 기록해도 안전하게 (락으로 보호)."""
    with _status_lock:
        status[key] = {"done": True, result_field: value}
        if not DRY_RUN:
            save_status(folder, status)


def _finish(folder: Path, status: dict, errors: dict[str, Exception]) -> None:
    """이번 배치 실행 후 공통 마무리: 전부 끝났으면 큐 폴더 삭제, 아니면 안내."""
    if not all_steps_done(status):
        remaining = ", ".join(k for k in ["blogger", "facebook_carousel", "instagram_carousel",
                                           "facebook_reel", "instagram_reel", "youtube_shorts"]
                               if not step_done(status, k))
        print(f"'{folder.name}' 일부 채널 미완료(남은 단계: {remaining}) — 다음 배치/재실행 때 처리")
    elif DRY_RUN:
        print(f"[DRY RUN] '{folder.name}' 전 채널 시뮬레이션 완료 — 실제로는 아무것도 게시되거나 삭제되지 않음")
    else:
        shutil.rmtree(folder)
        print(f"'{folder.name}' 전 채널 발행 완료 — 큐에서 삭제")

    if errors:
        names = ", ".join(errors)
        raise RuntimeError(f"다음 채널 발행 실패: {names} (자세한 원인은 위 로그 참고)")


def _publish_blog(folder: Path, status: dict) -> None:
    if not step_done(status, "blogger"):
        meta, html = parse_frontmatter(folder / "블로그" / "구글블로그용.md")
        html = fill_image_placeholders(html, folder / "블로그")
        url = blogger.publish(
            meta.get("title", ""),
            html,
            meta.get("labels") or [],
            meta.get("search_description", ""),
        )
        _record(folder, status, "blogger", "url", url)
        log(f"[blogger] 발행 완료: {url}")
    else:
        log("[blogger] 이미 완료됨 — 건너뜀")


def run(folder: Path, phase: str = "all") -> None:
    # DRY_RUN에서는 실제 상태 파일을 읽거나 쓰지 않는다 — 진짜 실행 때 이 큐가
    # 처리된 것처럼 보이면 안 되고, 매번 처음부터 필요한 단계를 전부 시뮬레이션한다.
    status = {} if DRY_RUN else load_status(folder)

    # 1. 구글 블로그 — 다른 채널 캡션이 이 URL을 참조하므로 반드시 먼저 끝난다.
    if phase in ("all", "blog"):
        _publish_blog(folder, status)

    if phase == "blog":
        # 화요일 배치는 여기서 끝 — 소셜 채널은 목요일 배치(--phase social)가 처리한다.
        _finish(folder, status, {})
        return

    if not step_done(status, "blogger"):
        raise RuntimeError(
            "블로그가 아직 발행되지 않았습니다 — 먼저 --phase blog(화요일 배치)를 "
            "실행하거나 --phase all로 전체를 실행하세요."
        )
    # 캡션의 {{BLOG_URL}}은 원문으로 안내하는 자리이므로 실제 학원 블로그(네이버)를
    # 우선한다 — 구글 블로그는 완전자동 발행을 위한 SEO/AEO용 미러일 뿐, 독자가 아는
    # "블로그"는 네이버다. 네이버는 반자동(사람이 직접 예약)이라 자동화가 URL을 알
    # 방법이 없으므로, 사람이 발행 직후 set_naver_url.py로 _status.json에 적어둔
    # naver_blog_url을 읽는다. 아직 안 적혀 있으면 구글 블로그 URL로 대체하되 경고를
    # 남긴다 — 조용히 잘못된 링크로 나가지 않게 한다.
    naver_url = status.get("naver_blog_url")
    if naver_url:
        blog_url = naver_url
    else:
        blog_url = status["blogger"]["url"]
        log(
            "[경고] naver_blog_url이 _status.json에 없어 캡션의 {{BLOG_URL}}에 구글 "
            "블로그 주소를 대신 씁니다 — 네이버 블로그를 발행했다면 "
            "'python scripts/publish/set_naver_url.py <URL>'로 기록해주세요."
        )

    # 2026-09-08부로 카드뉴스·숏츠 모두 채널마다 CTA 문구가 달라(§7) 플랫폼별 파일을
    # 따로 렌더링한다 — 카드뉴스는 "카드뉴스/instagram/"·"카드뉴스/facebook/" 하위
    # 폴더, 숏츠는 "9x16_instagram.mp4"·"9x16_facebook.mp4"·"9x16_youtube.mp4"
    # 파일명으로 구분한다(content-playbook.md §11).
    tasks: dict[str, tuple] = {}

    if phase in ("all", "cardnews"):
        cardnews_captions = parse_caption_sections(folder / "카드뉴스" / "채널별_캡션.md")

        def _facebook_carousel() -> str:
            images = sorted((folder / "카드뉴스" / "facebook").glob("*.png"))
            caption = fill_placeholders(cardnews_captions.get("페이스북", ""), BLOG_URL=blog_url)
            caption = _require_caption(caption, "facebook_carousel", "페이스북")
            return facebook.publish_photo_carousel(images, caption)

        def _instagram_carousel() -> str:
            images = sorted((folder / "카드뉴스" / "instagram").glob("*.png"))
            caption = fill_placeholders(cardnews_captions.get("인스타그램", ""), BLOG_URL=blog_url)
            caption = _require_caption(caption, "instagram_carousel", "인스타그램")
            return instagram.publish_carousel(images, caption)

        tasks["facebook_carousel"] = (_facebook_carousel, "id")
        tasks["instagram_carousel"] = (_instagram_carousel, "id")

    if phase in ("all", "social"):
        shorts_captions = parse_caption_sections(folder / "숏츠" / "채널별_캡션.md")

        def _facebook_reel() -> str:
            video_path = folder / "숏츠" / "9x16_facebook.mp4"
            caption = fill_placeholders(shorts_captions.get("페이스북", ""), BLOG_URL=blog_url)
            caption = _require_caption(caption, "facebook_reel", "페이스북")
            return facebook.publish_reel(video_path, caption)

        def _instagram_reel() -> str:
            video_path = folder / "숏츠" / "9x16_instagram.mp4"
            caption = fill_placeholders(shorts_captions.get("인스타그램", ""), BLOG_URL=blog_url)
            caption = _require_caption(caption, "instagram_reel", "인스타그램")
            return instagram.publish_reel(video_path, caption)

        def _youtube_shorts() -> str:
            video_path = folder / "숏츠" / "9x16_youtube.mp4"
            yt_meta, yt_description = parse_frontmatter(folder / "숏츠" / "캡션_유튜브쇼츠.md")
            yt_description = _require_caption(yt_description, "youtube_shorts", "(캡션_유튜브쇼츠.md 본문)")
            return youtube.upload_shorts(video_path, yt_meta.get("title", ""), yt_description)

        tasks["facebook_reel"] = (_facebook_reel, "id")
        tasks["instagram_reel"] = (_instagram_reel, "id")
        tasks["youtube_shorts"] = (_youtube_shorts, "url")

    # 이번 배치에 속한 채널들은 서로 의존하지 않으므로 동시에 실행한다.
    pending = {key: fn_field for key, fn_field in tasks.items() if not step_done(status, key)}

    errors: dict[str, Exception] = {}
    if pending:
        with ThreadPoolExecutor(max_workers=len(pending)) as pool:
            future_to_key = {pool.submit(fn): (key, field) for key, (fn, field) in pending.items()}
            for future in as_completed(future_to_key):
                key, field = future_to_key[future]
                try:
                    result = future.result()
                    _record(folder, status, key, field, result)
                    log(f"[{key}] 발행 완료: {result}")
                except Exception as exc:  # noqa: BLE001 — 다른 채널 발행을 막지 않고 계속 진행
                    errors[key] = exc
                    log(f"[{key}] 발행 실패: {exc}")

    _finish(folder, status, errors)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase",
        choices=["all", "blog", "cardnews", "social"],
        default="all",
        help="blog=화요일 배치(구글블로그만), cardnews=수요일 배치(카드뉴스 캐러셀 "
             "2채널), social=목요일 배치(릴스·쇼츠 3채널), all=예전처럼 한 번에 "
             "전부(기본값)",
    )
    args = parser.parse_args()

    folder = find_queue_folder()
    if folder is None:
        print("발행할 콘텐츠가 queue/ 에 없음 — 종료")
        return
    run(folder, phase=args.phase)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — 실패 원인을 그대로 Actions 로그에 남김
        print(f"발행 중 오류 발생: {exc}", file=sys.stderr)
        sys.exit(1)
