# -*- coding: utf-8 -*-
"""스토리용 세이프존 파일 자동 생성(2026-11-05 사용자 확인 방식: 82% 축소 + 블러 배경).

휴대폰에서 스토리 양옆이 잘리고 상하단을 인스타 UI가 가리는 문제를 피하려고, 완성된 카드·숏츠를 82%로
줄여 블러 배경 1080x1920 한가운데에 넣는다.
- 카드뉴스: <주차>/카드뉴스/instagram|facebook/*.png -> 카드뉴스/instagram_story|facebook_story/*.png
- 숏츠: <주차>/숏츠/9x16_<채널>_small.mp4(없으면 9x16_<채널>.mp4) -> 9x16_<채널>_story1.mp4(59초 초과면 story2도)
  스토리 영상은 60초 제한이라 59초를 넘으면 가운데 근처의 말 쉼(무음)에서 둘로 나눈다. --split 로 시각을 직접 줄 수도 있다.
사용: python scripts/local/make_story_assets.py <주차 폴더> [--channels instagram facebook] [--split 43.17]
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

MAX_STORY = 59.0


def run(cmd):
    subprocess.run(cmd, check=True)


def duration(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def pick_split(video: Path, total: float) -> float:
    """두 조각이 모두 59초 이하가 되는 범위 안에서, 영상 한가운데에 가장 가까운 말 쉼(무음) 지점을 고른다."""
    lo, hi = max(total - MAX_STORY, 5.0), min(MAX_STORY, total - 5.0)
    if lo > hi:
        sys.exit(f"{video.name}: 총 {total:.1f}초는 두 조각(각 59초 이하)으로 나눌 수 없습니다 - 영상을 줄여 주세요.")
    txt = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(video), "-af", "silencedetect=noise=-38dB:d=0.25", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", txt)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", txt)]
    mids = [(a + b) / 2 for a, b in zip(starts, ends) if lo <= (a + b) / 2 <= hi]
    if not mids:
        return round(min(max(total / 2, lo), hi), 2)
    return round(min(mids, key=lambda m: abs(m - total / 2)), 2)


VIDEO_FILTER = ("[0:v]split[a][b];[a]scale=1080:1920,boxblur=40:6,eq=brightness=-0.18[bg];[b]scale=886:1574[fg];"
                "[bg][fg]overlay=(W-w)/2:262,format=yuv420p[v]")
IMAGE_FILTER = ("[0:v]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                "boxblur=40:6,eq=brightness=-0.18[bg];[b]scale=886:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2")


def make_cards(week: Path, ch: str) -> None:
    src = week / "카드뉴스" / ch
    if not src.is_dir():
        return
    dst = week / "카드뉴스" / f"{ch}_story"
    dst.mkdir(exist_ok=True)
    for png in sorted(src.glob("*.png")):
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(png), "-filter_complex", IMAGE_FILTER, "-frames:v", "1", str(dst / png.name)])
    print(f"[{ch}] 카드 스토리 {len(list(dst.glob('*.png')))}장 -> {dst}")


def make_video(week: Path, ch: str, split: float | None) -> None:
    shorts = week / "숏츠"
    src = shorts / f"9x16_{ch}_small.mp4"
    if not src.exists():
        src = shorts / f"9x16_{ch}.mp4"
    if not src.exists():
        return
    full = shorts / f"9x16_{ch}_story_full.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-filter_complex", VIDEO_FILTER, "-map", "[v]", "-map", "0:a",
         "-c:v", "libx264", "-crf", "23", "-preset", "medium", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(full)])
    total = duration(full)
    enc = ["-c:v", "libx264", "-crf", "23", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart"]
    if total <= MAX_STORY:
        full.replace(shorts / f"9x16_{ch}_story1.mp4")
        print(f"[{ch}] 영상 스토리 1조각({total:.1f}초)")
        return
    at = split if split else pick_split(src, total)
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(full), "-t", str(at), *enc, str(shorts / f"9x16_{ch}_story1.mp4")])
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(at), "-i", str(full), *enc, str(shorts / f"9x16_{ch}_story2.mp4")])
    full.unlink()  # 발행 스크립트가 9x16_<채널>_story*.mp4 를 전부 올리므로 _story_full은 지운다
    print(f"[{ch}] 영상 스토리 2조각: {at}초에서 분할(총 {total:.1f}초)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("week", type=Path)
    ap.add_argument("--channels", nargs="+", default=["instagram", "facebook"])
    ap.add_argument("--split", type=float, default=None)
    ap.add_argument("--only", choices=["cards", "video", "all"], default="all")
    a = ap.parse_args()
    for ch in a.channels:
        if a.only in ("cards", "all"):
            make_cards(a.week, ch)
        if a.only in ("video", "all"):
            make_video(a.week, ch, a.split)


if __name__ == "__main__":
    main()
