"""발행 전에 큐의 블로그 사진을 assets/blog-images/<주차>/ 로 복사한다.

구글 블로그 글은 사진을 raw.githubusercontent.com에서 계속 불러온다. queue/는 발행 뒤
삭제되고 히스토리 정리 대상이므로, 글이 가리키는 사본은 assets/에 남긴다(2026-11-26).
워크플로가 발행 전에 이 스크립트를 실행하고 결과를 커밋·푸시한다.
"""

from __future__ import annotations

import shutil

from common import BLOG_IMAGE_DIR, QUEUE_DIR

EXTENSIONS = {".png", ".jpg", ".jpeg"}


def main() -> None:
    for source in sorted(QUEUE_DIR.glob("*/블로그/*")):
        if source.suffix.lower() not in EXTENSIONS:
            continue
        target = BLOG_IMAGE_DIR / source.parent.parent.name / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        print(f"[blog-images] {source} -> {target}")


if __name__ == "__main__":
    main()
