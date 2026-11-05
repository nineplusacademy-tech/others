#!/bin/bash
# HyperFrames 숏츠를 채널별로 동시에 렌더링한다(채널마다 index.html이 달라 프로젝트를 복사해 병렬 실행).
# 사용: bash scripts/local/render_channels_parallel.sh <프로젝트 폴더> <빌더 스크립트 이름> instagram facebook youtube none
#   프로젝트 폴더 = ...\숏츠\_원본프로젝트_916_instagram, 빌더 = 프로젝트의 _tools/ 안에 있는 build_wNN.py
#   (python _tools/<빌더> <채널> 로 index.html을 만든다).
#   결과: 프로젝트 상위 폴더에 9x16_<채널>.mp4 와 9x16_<채널>_small.mp4 (none은 naverclip). 작업 복사본은 끝나면 지운다.
set -u
PROJ="$(cd "$1" && pwd)"; BUILDER="$2"; shift 2
OUT="$(dirname "$PROJ")"
pids=()
for ch in "$@"; do
  name=$ch; [ "$ch" = "none" ] && name=naverclip
  W="$OUT/_render_$ch"
  rm -rf "$W"; cp -r "$PROJ" "$W"
  (
    cd "$W" && python -I -X utf8 "_tools/$BUILDER" "$ch" | head -1
    npx --yes hyperframes@0.8.97 render . -o "../9x16_${name}.mp4" --fps 30 --quiet 2>&1 | tail -1
    ffmpeg -y -loglevel error -i "../9x16_${name}.mp4" -c:v libx264 -preset slow -crf 24 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart "../9x16_${name}_small.mp4"
    echo "done $ch"
  ) > "$OUT/_render_$ch.log" 2>&1 &
  pids+=($!)
done
fail=0
for p in "${pids[@]}"; do wait "$p" || fail=1; done
for ch in "$@"; do tail -2 "$OUT/_render_$ch.log"; rm -rf "$OUT/_render_$ch" "$OUT/_render_$ch.log"; done
exit $fail
