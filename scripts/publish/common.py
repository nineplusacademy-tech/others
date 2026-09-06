"""여러 발행 스크립트가 공유하는 작은 헬퍼들.

절대 시크릿(토큰) 값을 print/log 하지 않는다 — 이 저장소는 퍼블릭이라
GitHub Actions 로그도 공개되며, 새로 발급받은(아직 Secrets에 등록되지 않은)
토큰은 GitHub의 자동 마스킹 대상이 아니다.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import yaml

QUEUE_DIR = Path("queue")

DRY_RUN = os.environ.get("DRY_RUN", "").lower() == "true"


def dry_run_log(channel: str, **details: str) -> None:
    """DRY_RUN일 때 실제 API 호출 대신 '이렇게 게시될 것입니다'를 출력한다."""
    print(f"[DRY RUN] {channel} — 실제로 게시하지 않음. 아래 내용으로 게시될 예정:")
    for key, value in details.items():
        preview = value if len(value) <= 200 else value[:200] + "…"
        print(f"    {key}: {preview}")

# main.py가 각 채널 성공 여부를 기록할 때 쓰는 키 전체 목록.
ALL_STEPS = [
    "blogger",
    "facebook_post",
    "instagram_carousel",
    "facebook_reel",
    "instagram_reel",
    "youtube_shorts",
]


def find_queue_folder() -> Path | None:
    """queue/ 아래에서 처리할 폴더 하나를 찾는다 (.gitkeep 등 파일은 무시)."""
    if not QUEUE_DIR.exists():
        return None
    candidates = sorted(p for p in QUEUE_DIR.iterdir() if p.is_dir())
    return candidates[0] if candidates else None


def status_path(folder: Path) -> Path:
    return folder / "_status.json"


def load_status(folder: Path) -> dict:
    p = status_path(folder)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def save_status(folder: Path, status: dict) -> None:
    status_path(folder).write_text(
        json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def step_done(status: dict, key: str) -> bool:
    return bool(status.get(key, {}).get("done"))


def all_steps_done(status: dict) -> bool:
    return all(step_done(status, k) for k in ALL_STEPS)


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    """`---\\nYAML\\n---\\n본문` 형식을 (메타, 본문)으로 분리한다."""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            meta = yaml.safe_load(parts[1]) or {}
            return meta, parts[2].strip()
    return {}, text.strip()


def parse_caption_sections(path: Path) -> dict[str, str]:
    """`## 채널명` 으로 구분된 캡션 파일을 {채널명: 캡션텍스트} 로 파싱한다."""
    sections: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current = line[3:].strip()
            buf = []
        else:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return sections


def fill_placeholders(text: str, **values: str) -> str:
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def raw_github_url(rel_path: Path) -> str:
    """queue/ 안의 파일을 인스타그램 API가 읽을 수 있는 공개 URL로 바꾼다.

    저장소가 퍼블릭이어야 동작한다 (raw.githubusercontent.com).
    """
    import os

    repo = os.environ["GITHUB_REPOSITORY"]  # "owner/repo"
    sha = os.environ["GITHUB_SHA"]
    return f"https://raw.githubusercontent.com/{repo}/{sha}/{rel_path.as_posix()}"
