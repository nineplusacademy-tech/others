"""스레드 60일 액세스 토큰을 갱신하고 GitHub Secret에 다시 저장한다.

절대 토큰 값을 print/log하지 않는다 — 이 저장소는 퍼블릭이라 Actions 로그도
공개되고, 새로 발급된 토큰은 아직 Secrets에 등록되지 않아 GitHub의 자동
로그 마스킹 대상이 아니다.
"""

from __future__ import annotations

import os

import threads
from common import update_github_secret


def main() -> None:
    current_token = os.environ["THREADS_ACCESS_TOKEN"]
    result = threads.refresh_access_token(current_token)
    update_github_secret("THREADS_ACCESS_TOKEN", result["access_token"])
    print(f"THREADS_ACCESS_TOKEN 갱신 완료 (새 만료까지 약 {result.get('expires_in', 0) // 86400}일)")


if __name__ == "__main__":
    main()
