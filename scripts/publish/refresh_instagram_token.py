"""인스타그램 60일 액세스 토큰을 갱신하고 GitHub Secret에 다시 저장한다.

절대 토큰 값을 print/log 하지 않는다 — 이 저장소는 퍼블릭이라 Actions 로그도
공개되고, 새로 발급된 토큰은 아직 Secrets에 등록되지 않아 GitHub의 자동
로그 마스킹 대상이 아니다.

GH_PAT는 이 저장소의 Secrets를 쓸 수 있는 개인용 액세스 토큰이어야 한다
(기본 GITHUB_TOKEN은 Secrets API 쓰기 권한이 없음). Fine-grained PAT라면
이 저장소에 "Secrets: Read and write" 권한을 준 것으로 발급한다.
"""

from __future__ import annotations

import base64
import os

import requests
from nacl import encoding, public

import instagram

API = "https://api.github.com"


def _repo() -> str:
    return os.environ["GITHUB_REPOSITORY"]


def _gh_headers() -> dict:
    return {
        "Authorization": f"Bearer {os.environ['GH_PAT']}",
        "Accept": "application/vnd.github+json",
    }


def _encrypt(public_key_b64: str, value: str) -> str:
    pk = public.PublicKey(public_key_b64.encode("utf-8"), encoding.Base64Encoder())
    box = public.SealedBox(pk)
    return base64.b64encode(box.encrypt(value.encode("utf-8"))).decode("utf-8")


def update_secret(name: str, value: str) -> None:
    r = requests.get(
        f"{API}/repos/{_repo()}/actions/secrets/public-key",
        headers=_gh_headers(),
        timeout=30,
    )
    r.raise_for_status()
    key_info = r.json()

    encrypted = _encrypt(key_info["key"], value)

    r = requests.put(
        f"{API}/repos/{_repo()}/actions/secrets/{name}",
        headers=_gh_headers(),
        json={"encrypted_value": encrypted, "key_id": key_info["key_id"]},
        timeout=30,
    )
    r.raise_for_status()


def main() -> None:
    current_token = os.environ["INSTAGRAM_ACCESS_TOKEN"]
    result = instagram.refresh_access_token(current_token)
    update_secret("INSTAGRAM_ACCESS_TOKEN", result["access_token"])
    print(f"INSTAGRAM_ACCESS_TOKEN 갱신 완료 (새 만료까지 약 {result.get('expires_in', 0) // 86400}일)")


if __name__ == "__main__":
    main()
