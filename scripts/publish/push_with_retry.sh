#!/bin/bash
# 워크플로의 '결과 커밋' 단계용 push — 같은 시각에 다른 푸시(사람의 문서 푸시, 다른 워크플로)가 끼어들어도
# 최신 커밋 위에 다시 얹어 재시도한다(2026-11-05: 15주차 페이스북 글·스토리 실행이 푸시 충돌로 "실패"로 표시되고
# 사용한 큐 파일이 남아 중복 게시 위험이 생긴 일이 있었다).
# 이 커밋은 queue/ 와 상태 파일만 바꾸므로 -X theirs(재생 중인 우리 커밋 우선)로 충돌을 해결해도 안전하다.
BR=$(git rev-parse --abbrev-ref HEAD)
for i in 1 2 3 4 5; do
  if git push; then
    exit 0
  fi
  echo "::warning::push 실패($i/5) — 최신 커밋을 받아 다시 얹고 재시도합니다"
  git fetch origin "$BR" || true
  if ! git rebase -X theirs "origin/$BR"; then
    git rebase --abort || true
    echo "::error::자동 rebase 실패 — 수동 확인 필요"
    exit 1
  fi
  sleep $((i * 3))
done
echo "::error::push를 5번 시도했지만 실패했습니다"
exit 1
