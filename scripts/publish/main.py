"""예약 발행 오케스트레이터.

queue/ 아래 폴더 하나를 찾아, 완전자동 4채널(구글블로그·페이스북·인스타그램·
유튜브쇼츠)에 순서대로 발행한다. 각 단계 성공 여부를 _status.json에 기록해
재실행 시 이미 성공한 채널은 건너뛴다. 전부 성공하면 큐 폴더를 삭제한다.

이 파일은 python scripts/publish/main.py 로 저장소 루트에서 실행한다
(.github/workflows/publish.yml 참고). 실제로 Secrets/토큰 값을 print하지 않는다.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import blogger
import facebook
import instagram
import youtube
from common import (
    all_steps_done,
    fill_placeholders,
    find_queue_folder,
    load_status,
    parse_caption_sections,
    parse_frontmatter,
    save_status,
    step_done,
)


def run(folder: Path) -> None:
    status = load_status(folder)

    # 1. 구글 블로그
    if not step_done(status, "blogger"):
        meta, html = parse_frontmatter(folder / "블로그" / "구글블로그용.md")
        url = blogger.publish(meta.get("title", ""), html, meta.get("labels") or [])
        status["blogger"] = {"done": True, "url": url}
        save_status(folder, status)
        print(f"[blogger] 발행 완료: {url}")
    blog_url = status["blogger"]["url"]

    cardnews_captions = parse_caption_sections(folder / "카드뉴스" / "채널별_캡션.md")
    shorts_captions = parse_caption_sections(folder / "숏츠" / "채널별_캡션.md")

    # 2. 페이스북 게시글 (카드뉴스 표지 + 블로그 링크)
    if not step_done(status, "facebook_post"):
        cover = folder / "카드뉴스" / "01.png"
        caption = fill_placeholders(cardnews_captions.get("페이스북", ""), BLOG_URL=blog_url)
        post_id = facebook.publish_photo_post(cover, caption)
        status["facebook_post"] = {"done": True, "id": post_id}
        save_status(folder, status)
        print(f"[facebook_post] 발행 완료: {post_id}")

    # 3. 인스타그램 캐러셀 (카드뉴스 9장)
    if not step_done(status, "instagram_carousel"):
        images = sorted((folder / "카드뉴스").glob("*.png"))
        caption = fill_placeholders(cardnews_captions.get("인스타그램", ""), BLOG_URL=blog_url)
        media_id = instagram.publish_carousel(images, caption)
        status["instagram_carousel"] = {"done": True, "id": media_id}
        save_status(folder, status)
        print(f"[instagram_carousel] 발행 완료: {media_id}")

    video_path = folder / "숏츠" / "9x16.mp4"

    # 4. 페이스북 릴스
    if not step_done(status, "facebook_reel"):
        caption = fill_placeholders(shorts_captions.get("페이스북", ""), BLOG_URL=blog_url)
        video_id = facebook.publish_reel(video_path, caption)
        status["facebook_reel"] = {"done": True, "id": video_id}
        save_status(folder, status)
        print(f"[facebook_reel] 발행 완료: {video_id}")

    # 5. 인스타그램 릴스
    if not step_done(status, "instagram_reel"):
        caption = fill_placeholders(shorts_captions.get("인스타그램", ""), BLOG_URL=blog_url)
        media_id = instagram.publish_reel(video_path, caption)
        status["instagram_reel"] = {"done": True, "id": media_id}
        save_status(folder, status)
        print(f"[instagram_reel] 발행 완료: {media_id}")

    # 6. 유튜브 쇼츠
    if not step_done(status, "youtube_shorts"):
        yt_meta, yt_description = parse_frontmatter(folder / "숏츠" / "캡션_유튜브쇼츠.md")
        video_url = youtube.upload_shorts(video_path, yt_meta.get("title", ""), yt_description)
        status["youtube_shorts"] = {"done": True, "url": video_url}
        save_status(folder, status)
        print(f"[youtube_shorts] 발행 완료: {video_url}")

    if all_steps_done(status):
        shutil.rmtree(folder)
        print(f"'{folder.name}' 전 채널 발행 완료 — 큐에서 삭제")
    else:
        print(f"'{folder.name}' 일부 채널 미완료 — 다음 실행 때 나머지 재시도")


def main() -> None:
    folder = find_queue_folder()
    if folder is None:
        print("발행할 콘텐츠가 queue/ 에 없음 — 종료")
        return
    run(folder)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — 실패 원인을 그대로 Actions 로그에 남김
        print(f"발행 중 오류 발생: {exc}", file=sys.stderr)
        sys.exit(1)
