# -*- coding: utf-8 -*-
"""로컬 결과물 백업 도구(2026-11-16, ChatGPT 자문 001 반영) — 아직 백업 위치가 정해지지 않아 실행하지 않는다.

`C:\\Users\\user\\Desktop\\claude_pro\\클로드작업폴더`(원고·이미지·카드뉴스·숏츠·캡션)를 사용자가 정한 위치로 복사한다.
- **삭제하지 않는다**: robocopy `/E /XO`(하위 폴더 포함, 대상이 더 새것이면 건너뜀)만 쓰고 `/MIR`·`/PURGE`는 쓰지 않는다.
  실수로 지운 파일이 백업에서 같이 사라지지 않게 하기 위해서다.
- **버전 보존**은 백업 위치가 담당한다(OneDrive·구글 드라이브처럼 파일 버전 기록이 있는 곳을 권장).
- 제외: 임시 렌더링 폴더(`_render_*`, `.hf-transaction*`), 작업 복사본 로그, node_modules, 캐시.
- 비밀값·개인정보: 이 폴더에는 API 키나 개인정보를 두지 않는 것이 원칙이다. 백업 대상을 넓히지 않는다(`--dry-run`으로 목록 확인).

사용: python scripts/local/backup_work.py --dest "D:\\백업\\나인플러스" [--dry-run]
"""
import argparse
import os
import subprocess
import sys

SRC = r"C:\Users\user\Desktop\claude_pro\클로드작업폴더"
EXCLUDE_DIRS = ["node_modules", "__pycache__", ".git", "_render_*", ".*.hf-transaction*", "*.hf-transaction*", "Claude outputs"]
EXCLUDE_FILES = ["_render_*.log", "_build_*.log", "*.tmp"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", required=True, help="백업 대상 폴더(없으면 만든다)")
    ap.add_argument("--dry-run", action="store_true", help="복사하지 않고 목록만 확인")
    a = ap.parse_args()
    if not os.path.isdir(SRC):
        print("원본 폴더가 없습니다:", SRC)
        return 2
    dest = os.path.join(a.dest, os.path.basename(SRC))
    cmd = ["robocopy", SRC, dest, "/E", "/XO", "/R:1", "/W:1", "/NP", "/NFL", "/NDL", "/XD", *EXCLUDE_DIRS, "/XF", *EXCLUDE_FILES]
    if a.dry_run:
        cmd.append("/L")
    print("실행:", " ".join(cmd))
    r = subprocess.run(cmd)
    # robocopy 종료 코드 0~7은 성공(복사됨/건너뜀 포함), 8 이상이 실패
    return 0 if r.returncode < 8 else r.returncode


if __name__ == "__main__":
    sys.exit(main())
