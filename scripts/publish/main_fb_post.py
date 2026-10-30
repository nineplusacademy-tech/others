"""페이스북 페이지 글(교육뉴스 월요일·메인 블로그 화요일) 자동 게시 오케스트레이터.

2026-10-30 신설(사용자 지시: 교육뉴스·메인 블로그 내용을 페이스북 페이지에도 올릴 것).
카드뉴스·릴스(main.py)와는 별개로, 네이버 블로그 글을 소개하는 짧은 글(삽화/대표이미지
1장 + 요약 + 원문 링크)을 올린다. 스레드와 같은 방식이다 — 네이버 글이 공개된 뒤에만 올리고,
아직이면 미뤘다가 다음 catch-up 실행에서 다시 시도한다. 두 경로 모두 여러 번 실행해도
중복 게시되지 않는다(게시 후 파일 삭제 / _status.json의 facebook_post 키).

- 교육뉴스: `queue/_edu_fb.md`(본문, `{{BLOG_URL}}` 포함) + 선택 `queue/_edu_fb.png`(이미지)
  + `queue/_edu_fb_link.json`(set_naver_url.py --edu가 기록). 게시 후 본문·이미지를 지우고, 주소 파일은
  인스타 캐러셀(`queue/_edu_ig/01~05.png` + `캡션.md`, 2026-10-30 추가)까지 끝난 뒤에 지운다.
- 메인 블로그: `queue/<주차폴더>/페이스북글.md`(프런트매터 `image:` 로 폴더 안 이미지 상대경로 선택)
  + `_status.json`의 `naver_blog_url`. 게시 후 `facebook_post` 키를 기록한다(ALL_STEPS에는 넣지 않아
  게시가 늦어도 큐 폴더 삭제 판단에 영향이 없다).
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import facebook
import instagram
from common import (
    DRY_RUN,
    QUEUE_DIR,
    fill_placeholders,
    find_queue_folder,
    load_status,
    naver_post_not_found,
    parse_frontmatter,
    save_status,
    step_done,
)

EDU_TEXT = QUEUE_DIR / "_edu_fb.md"
EDU_IMAGE = QUEUE_DIR / "_edu_fb.png"
EDU_LINK = QUEUE_DIR / "_edu_fb_link.json"
EDU_IG_DIR = QUEUE_DIR / "_edu_ig"  # 2026-10-30: 교육뉴스 인스타 캐러셀(01~05.png + 캡션.md)


def run_edu() -> None:
    if not EDU_TEXT.exists():
        print("교육뉴스 페이스북 글(_edu_fb.md)이 없음 — 건너뜀")
        return
    if not EDU_LINK.exists():
        print(
            "::warning::교육뉴스 페이스북 글은 있지만 네이버 URL(_edu_fb_link.json)이 기록되지 않아 "
            "게시하지 않았습니다 — 'python scripts/publish/set_naver_url.py --edu <URL>' 기록 후 "
            "publish-fb-post 워크플로를 수동 실행하세요."
        )
        return
    url = json.loads(EDU_LINK.read_text(encoding="utf-8")).get("url")
    if not url:
        raise RuntimeError("_edu_fb_link.json에 url이 없습니다.")
    if not DRY_RUN and naver_post_not_found(url):
        print(f"::warning::교육뉴스 네이버 블로그 글({url})이 아직 공개 전이라 페이스북 글을 미뤘습니다 — 다음 실행 때 다시 시도합니다.")
        return

    text = fill_placeholders(EDU_TEXT.read_text(encoding="utf-8").strip(), BLOG_URL=url)
    post_id = facebook.publish_post(text, EDU_IMAGE if EDU_IMAGE.exists() else None)
    if not DRY_RUN:
        for p in (EDU_TEXT, EDU_IMAGE):
            p.unlink(missing_ok=True)
    print(f"[edu-facebook-post] 발행 완료: {post_id}")


def run_edu_ig() -> None:
    """교육뉴스 인스타 캐러셀(팔로우·네이버 블로그 조회 유도) — 페이스북 글과 같은 주소 파일로 공개 여부를 확인한다."""
    caption_file = EDU_IG_DIR / "캡션.md"
    if not caption_file.exists():
        print("교육뉴스 인스타 캐러셀(_edu_ig/캡션.md)이 없음 — 건너뜀")
        return
    images = sorted(EDU_IG_DIR.glob("[0-9][0-9].png"))
    if not images:
        raise RuntimeError("_edu_ig/에 01~NN.png 이미지가 없습니다.")
    if not EDU_LINK.exists():
        print("::warning::교육뉴스 인스타 캐러셀은 있지만 네이버 URL(_edu_fb_link.json)이 기록되지 않아 게시하지 않았습니다.")
        return
    url = json.loads(EDU_LINK.read_text(encoding="utf-8")).get("url")
    if not url:
        raise RuntimeError("_edu_fb_link.json에 url이 없습니다.")
    if not DRY_RUN and naver_post_not_found(url):
        print(f"::warning::교육뉴스 네이버 블로그 글({url})이 아직 공개 전이라 인스타 캐러셀을 미뤘습니다 — 다음 실행 때 다시 시도합니다.")
        return

    caption = fill_placeholders(caption_file.read_text(encoding="utf-8").strip(), BLOG_URL=url)
    media_id = instagram.publish_carousel(images, caption)
    if not DRY_RUN:
        shutil.rmtree(EDU_IG_DIR, ignore_errors=True)
    print(f"[edu-instagram-carousel] 발행 완료: {media_id}")


def cleanup_edu_link() -> None:
    """페이스북 글·인스타 캐러셀이 모두 끝났으면 주소 파일을 지운다(다음 주 것과 섞이지 않게)."""
    if DRY_RUN or not EDU_LINK.exists():
        return
    if not EDU_TEXT.exists() and not EDU_IG_DIR.exists():
        EDU_LINK.unlink()


def run_main() -> None:
    folder = find_queue_folder()
    if folder is None:
        print("발행할 콘텐츠가 queue/ 에 없음 — 메인 블로그 페이스북 글 건너뜀")
        return
    fb_md = folder / "페이스북글.md"
    if not fb_md.exists():
        print(f"'{folder.name}'에 페이스북글.md가 없음 — 이번 주는 대상 아님(건너뜀)")
        return

    status = load_status(folder)
    if step_done(status, "facebook_post"):
        print(f"'{folder.name}' 페이스북 글은 이미 게시됨 — 건너뜀")
        return
    if not step_done(status, "blogger"):
        print(f"'{folder.name}' 블로그가 아직 발행되지 않아 페이스북 글을 미뤘습니다 — 다음 실행 때 다시 시도합니다.")
        return
    naver_url = status.get("naver_blog_url")
    if not naver_url:
        print(
            f"::warning::'{folder.name}'에 naver_blog_url이 없어 페이스북 글을 미뤘습니다 — "
            "'python scripts/publish/set_naver_url.py <URL>' 기록 후 다시 실행하세요."
        )
        return
    if not DRY_RUN and naver_post_not_found(naver_url):
        print(f"::warning::네이버 블로그 글({naver_url})이 아직 공개 전이라 페이스북 글을 미뤘습니다 — 다음 실행 때 다시 시도합니다.")
        return

    meta, body = parse_frontmatter(fb_md)
    text = fill_placeholders(body, BLOG_URL=naver_url)
    image = None
    if meta.get("image"):
        image = folder / str(meta["image"])
        if not image.exists():
            raise RuntimeError(f"페이스북글.md의 image({meta['image']}) 파일이 없습니다.")
    post_id = facebook.publish_post(text, image)
    if not DRY_RUN:
        status["facebook_post"] = {"done": True, "id": post_id}
        save_status(folder, status)
    print(f"[main-facebook-post] 발행 완료: {post_id}")


def main() -> None:
    errors: list[str] = []
    for fn in (run_edu, run_edu_ig, run_main):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 — 한쪽 실패가 다른 쪽을 막지 않게
            errors.append(f"{fn.__name__}: {exc}")
            print(f"페이스북 글 발행 중 오류 ({fn.__name__}): {exc}", file=sys.stderr)
    try:
        cleanup_edu_link()
    except Exception as exc:  # noqa: BLE001
        print(f"주소 파일 정리 중 오류: {exc}", file=sys.stderr)
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
