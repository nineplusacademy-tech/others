# -*- coding: utf-8 -*-
"""Gemini TTS 장면 음성 생성기 — 응답이 멈춰도(2026-11 15주차 반복 발생) 알아서 끊고 다시 시도한다.

http_options timeout이 먹지 않고 서비스가 가끔 응답 없이 멈추므로, 장면마다 별도 프로세스로 호출하고
제한 시간(기본 60초)이 지나면 프로세스를 강제 종료한 뒤 다시 시도한다(기본 6회, 사이에 짧게 쉼).

사용: python scripts/local/tts_scenes.py <출력 폴더> "scene01=문장" "scene02=문장" ...
  → <출력 폴더>/scene01.wav · .mp3 를 만들고 길이(초)를 출력한다. GEMINI_API_KEY 환경변수 필요(값은 출력하지 않음).
  옵션: --voice Charon --style "..." --timeout 60 --tries 6
"""
import argparse
import base64
import os
import subprocess
import sys
import time

STYLE = "차분하고 따뜻한 30~40대 남성 강사, 또박또박 자신감 있게"


def worker(out_base: str, name: str, text: str, voice: str, style: str) -> None:
    from google import genai  # 지연 import — 부모 프로세스는 라이브러리 없이도 동작

    c = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    i = c.interactions.create(
        model="gemini-3.8-flash-tts",
        input=[{"type": "user_input", "content": [{"type": "text", "text": text,
                                                   "annotations": [{"type": "speech_metadata", "style": style}]}]}],
        response_format={"type": "audio"},
        generation_config={"speech_config": [{"voice": voice}]},
    )
    d = os.path.dirname(os.path.join(out_base, name))
    os.makedirs(d, exist_ok=True)
    wav = os.path.join(out_base, name + ".wav")
    mp3 = os.path.join(out_base, name + ".mp3")
    with open(wav, "wb") as f:
        f.write(base64.b64decode(i.output_audio.data))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-ar", "44100", "-b:a", "192k", mp3], check=True)


def duration(path: str) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker(*sys.argv[2:7])
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("items", nargs="+", help='"scene01=문장" 형식')
    ap.add_argument("--voice", default="Charon")
    ap.add_argument("--style", default=STYLE)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--tries", type=int, default=6)
    a = ap.parse_args()
    if not os.environ.get("GEMINI_API_KEY"):
        sys.exit("GEMINI_API_KEY 환경변수가 없습니다.")
    failed = []
    for item in a.items:
        name, text = item.split("=", 1)
        ok = False
        for attempt in range(1, a.tries + 1):
            try:
                subprocess.run([sys.executable, os.path.abspath(__file__), "--worker", a.out, name, text, a.voice, a.style],
                               timeout=a.timeout, check=True)
                ok = True
                break
            except subprocess.TimeoutExpired:
                print(f"{name}: {attempt}/{a.tries} 응답 없음({a.timeout}초) — 끊고 다시 시도", flush=True)
            except subprocess.CalledProcessError as e:
                print(f"{name}: {attempt}/{a.tries} 오류(코드 {e.returncode}) — 다시 시도", flush=True)
            time.sleep(2)
        if ok:
            print(f"{name} {duration(os.path.join(a.out, name + '.mp3')):.2f}", flush=True)
        else:
            failed.append(name)
            print(f"{name}: 실패 — 나중에 다시 시도하세요", flush=True)
    if failed:
        sys.exit("실패한 장면: " + ", ".join(failed))


if __name__ == "__main__":
    main()
