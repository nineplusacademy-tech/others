"""여러 발행 스크립트가 공유하는 작은 헬퍼들.

절대 시크릿(토큰) 값을 print/log 하지 않는다 — 이 저장소는 퍼블릭이라
GitHub Actions 로그도 공개되며, 새로 발급받은(아직 Secrets에 등록되지 않은)
토큰은 GitHub의 자동 마스킹 대상이 아니다.
"""

from __future__ import annotations

import json
import os
import re
import threading
from pathlib import Path

import requests
import yaml

QUEUE_DIR = Path("queue")

DRY_RUN = os.environ.get("DRY_RUN", "").lower() == "true"

# main.py가 여러 채널을 스레드풀로 동시 실행하므로, 여러 줄짜리 출력이
# 서로 다른 스레드의 print와 섞여 로그가 깨지지 않도록 공유 락으로 감싼다.
_print_lock = threading.Lock()


def dry_run_log(channel: str, **details: str) -> None:
    """DRY_RUN일 때 실제 API 호출 대신 '이렇게 게시될 것입니다'를 출력한다."""
    lines = [f"[DRY RUN] {channel} — 실제로 게시하지 않음. 아래 내용으로 게시될 예정:"]
    for key, value in details.items():
        preview = value if len(value) <= 200 else value[:200] + "…"
        lines.append(f"    {key}: {preview}")
    with _print_lock:
        print("\n".join(lines))


def log(message: str) -> None:
    """여러 스레드가 동시에 출력해도 줄이 섞이지 않게 락으로 감싸서 print한다."""
    with _print_lock:
        print(message)

# main.py가 각 채널 성공 여부를 기록할 때 쓰는 키 전체 목록.
ALL_STEPS = [
    "blogger",
    "facebook_carousel",
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


_AUTHOR_NOTE_RE = re.compile(r"\[※.*?\]", re.DOTALL)
_SECTION_SUFFIX_RE = re.compile(r"\s*\([^)]*\)\s*$")


def parse_caption_sections(path: Path) -> dict[str, str]:
    """`## 채널명` 으로 구분된 캡션 파일을 {채널명: 캡션텍스트} 로 파싱한다.

    각 섹션 끝의 `[※ 글자수: ...]` 같은 작성자용 메모(발행에는 포함되면 안 됨)를
    제거한다 — content-playbook.md에 공식화되지 않은 채 content-derivation-team이
    관행적으로 남기던 메모라 이 파서가 몰랐고, 2026-09-09 카드뉴스 발행 때 그대로
    페이스북·인스타그램 캡션에 게시된 걸 확인해 여기서 걸러내도록 고쳤다.

    채널명 뒤에 붙는 `(릴스)` 같은 설명용 괄호는 키에서 제거한다 — 카드뉴스
    캡션 파일은 "## 인스타그램"으로, 숏츠 캡션 파일은 "## 인스타그램(릴스)"로
    적혀 있어서 호출부의 `.get("인스타그램", ...)` 조회가 숏츠 쪽에서만
    조용히 빈 문자열로 빠지던 실사고(2026-09-11, 36주차 릴스 캡션 전부 누락)를
    이 정규화로 막는다.
    """
    sections: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []

    def _finish(name: str) -> None:
        text = _AUTHOR_NOTE_RE.sub("", "\n".join(buf)).strip()
        sections[name] = text

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if current is not None:
                _finish(current)
            current = _SECTION_SUFFIX_RE.sub("", line[3:].strip())
            buf = []
        else:
            buf.append(line)
    if current is not None:
        _finish(current)
    return sections


def fill_placeholders(text: str, **values: str) -> str:
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def raise_for_status_with_body(resp: requests.Response) -> None:
    """`resp.raise_for_status()`와 같지만, Meta Graph API가 돌려준 실제 오류 메시지
    (JSON 본문)까지 예외 메시지에 포함한다.

    `raise_for_status()`만 쓰면 HTTP 상태 코드(예: "400 Bad Request")만 로그에 남고
    Meta가 알려주는 구체적인 원인(예: 만료된 토큰, 권한 부족, 잘못된 파라미터)이
    사라져 Actions 로그만 보고는 원인을 알 수 없다(2026-09-09 카드뉴스 발행 실패
    때 겪은 문제).
    """
    if resp.ok:
        return
    try:
        body = resp.json()
    except ValueError:
        body = resp.text
    raise requests.HTTPError(
        f"{resp.status_code} {resp.reason} for url: {resp.url} — 응답 본문: {body}",
        response=resp,
    )


def update_github_secret(name: str, value: str) -> None:
    """이 저장소의 GitHub Actions Secret 값을 새로 갱신한다 (토큰 자동 갱신용).

    GH_PAT 환경변수(이 저장소에 "Secrets: Read and write" 권한을 준 fine-grained
    PAT)가 필요하다 — 기본 GITHUB_TOKEN은 Secrets API 쓰기 권한이 없다. 절대
    value를 print/log하지 않는다 — 이 저장소는 퍼블릭이라 Actions 로그도
    공개되고, 새로 발급된 토큰은 아직 Secrets에 등록되지 않아 GitHub의 자동
    마스킹 대상이 아니다.
    """
    import base64

    import requests
    from nacl import encoding, public

    repo = os.environ["GITHUB_REPOSITORY"]
    headers = {
        "Authorization": f"Bearer {os.environ['GH_PAT']}",
        "Accept": "application/vnd.github+json",
    }

    key_resp = requests.get(
        f"https://api.github.com/repos/{repo}/actions/secrets/public-key",
        headers=headers,
        timeout=30,
    )
    key_resp.raise_for_status()
    key_info = key_resp.json()

    pk = public.PublicKey(key_info["key"].encode("utf-8"), encoding.Base64Encoder())
    encrypted = base64.b64encode(public.SealedBox(pk).encrypt(value.encode("utf-8"))).decode("utf-8")

    put_resp = requests.put(
        f"https://api.github.com/repos/{repo}/actions/secrets/{name}",
        headers=headers,
        json={"encrypted_value": encrypted, "key_id": key_info["key_id"]},
        timeout=30,
    )
    put_resp.raise_for_status()


def raw_github_url(rel_path: Path) -> str:
    """queue/ 안의 파일을 인스타그램 API가 읽을 수 있는 공개 URL로 바꾼다.

    저장소가 퍼블릭이어야 동작한다 (raw.githubusercontent.com). GITHUB_SHA로
    커밋을 고정하므로, 나중에 큐 폴더가 삭제되는 커밋이 생겨도 이 URL이 가리키는
    특정 커밋의 blob은 계속 살아있어 링크가 깨지지 않는다(히스토리를 재작성하지
    않는 한).

    경로 세그먼트(주제 폴더명 등 한글 포함)는 반드시 percent-encode해야 한다 —
    curl/브라우저는 인코딩 안 된 UTF-8 경로도 관대하게 처리하지만, 인스타그램의
    media fetcher는 엄격한 RFC 3986 URI를 요구해 raw 한글 경로를 그대로 주면
    "Media download has failed"로 조용히 실패한다(2026-09-09 카드뉴스 발행
    실사고에서 확인).
    """
    import os
    from urllib.parse import quote

    repo = os.environ["GITHUB_REPOSITORY"]  # "owner/repo"
    sha = os.environ["GITHUB_SHA"]
    encoded_path = "/".join(quote(segment) for segment in rel_path.as_posix().split("/"))
    return f"https://raw.githubusercontent.com/{repo}/{sha}/{encoded_path}"


_IMG_PLACEHOLDER_RE = re.compile(r'<img\s+src="\[사진 자리 \d+\s*·\s*([^\]]+)\]"')


def fill_image_placeholders(html: str, blog_folder: Path) -> str:
    """`<img src="[사진 자리 N · 설명]">`을 실제 이미지의 공개 URL로 치환한다.

    content-playbook.md §2 규칙 9번(`[📷 사진 자리 N · 대표이미지/본문이미지 N — 비율]`)의
    HTML 버전 표기를 그대로 파싱한다. "설명"에서 공백을 제거한 이름
    (예: "대표이미지", "본문이미지 1" → "본문이미지1")과 같은 파일명(.png/.jpg/.jpeg)을
    같은 폴더에서 찾아 raw_github_url로 바꾼다. 매칭되는 파일이 없으면 원본을 그대로
    두고 어떤 자리가 비어있는지 stderr에 남긴다 — 발행을 막지는 않되 눈에 띄게 한다.
    """
    import sys

    def _replace(match: re.Match) -> str:
        label = re.sub(r"\s+", "", match.group(1))
        for ext in (".png", ".jpg", ".jpeg"):
            candidate = blog_folder / f"{label}{ext}"
            if candidate.exists():
                # blog_folder는 이미 저장소 루트 기준 상대경로(queue/.../블로그)이므로
                # 추가 변환 없이 그대로 raw_github_url에 넘긴다.
                return f'<img src="{raw_github_url(candidate)}"'
        print(f"[blogger] 경고: '{label}'에 매칭되는 이미지 파일을 {blog_folder}에서 찾지 못함 — 원본 플레이스홀더 유지", file=sys.stderr)
        return match.group(0)

    return _IMG_PLACEHOLDER_RE.sub(_replace, html)
