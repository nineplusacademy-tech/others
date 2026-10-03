# 로컬 HyperFrames 연결 설정 (최초 1회)

`content-derivation-team` 스킬(카드뉴스·숏츠 스토리보드 작성 + 렌더링)은 별도 로컬
프로젝트 `claude_pro`에 이미 설치돼 있는 HyperFrames 스킬 7개를 그대로 사용한다 —
**파일을 복사하지 않고, 윈도우 디렉터리 정션(junction)으로 경로만 연결**한다. 이렇게
하면 `claude_pro`는 손대지 않고 그대로 두면서, 이 저장소를 로컬에서 열었을 때도
같은 세션에서 HyperFrames를 바로 쓸 수 있다.

## 사전 조건

- 이 저장소(`nineplusacademy-tech/others`)를 로컬 컴퓨터에 클론해뒀을 것
- `claude_pro` 프로젝트가 로컬에 있고, 그 안에 다음 7개 폴더가 있을 것(스크린샷
  기준 위치: `바탕 화면\claude_pro\.claude\skills\`):
  `hyperframes`, `hyperframes-animation`, `hyperframes-cli`, `hyperframes-core`,
  `hyperframes-creative`, `hyperframes-keyframes`, `hyperframes-registry`

## 정션 만들기 (PowerShell)

이 저장소를 로컬에 클론한 폴더에서 PowerShell을 열고, 아래에서 `<CLAUDE_PRO 경로>`를
실제 `claude_pro` 경로로 바꿔서 실행한다(예: `C:\Users\본인계정\Desktop\claude_pro`):

```powershell
$hyperframesRoot = "<CLAUDE_PRO 경로>\.claude\skills"
$targets = @(
  "hyperframes",
  "hyperframes-animation",
  "hyperframes-cli",
  "hyperframes-core",
  "hyperframes-creative",
  "hyperframes-keyframes",
  "hyperframes-registry"
)
foreach ($name in $targets) {
  New-Item -ItemType Junction `
    -Path ".claude\skills\$name" `
    -Target "$hyperframesRoot\$name"
}
```

(관리자 권한 없이 실행 가능 — 디렉터리 정션은 일반 사용자 권한으로 만들 수 있다.)

cmd.exe를 쓴다면 동일한 작업을 아래처럼 할 수도 있다(폴더마다 반복):

```cmd
mklink /J ".claude\skills\hyperframes" "<CLAUDE_PRO 경로>\.claude\skills\hyperframes"
```

## 확인

```powershell
Get-ChildItem .claude\skills | Where-Object { $_.Name -like "hyperframes*" }
```

7개 폴더가 모두 보이고(속성이 정션으로 표시됨), 각각 안에 `SKILL.md`가 실제로
열리면 정션 자체는 성공이다. **단, 정션 안쪽까지 파고드는 폴더 목록 검색(Glob 등)은
정션을 따라 들어가지 않을 수 있다** — 그래서 `.claude/skills/`를 나열했을 때
`hyperframes*`가 안 보여도, 실제 파일을 직접 읽거나(`Read`) `/hyperframes` 스킬을
직접 호출하면 정상 작동하는 경우가 많다(2026-09-06 실제 확인됨). 가장 확실한
검증은 목록 검색이 아니라 **`/hyperframes` 스킬을 실제로 호출**해보는 것이다 —
호출됐을 때 8개 도메인 스킬(`-core`·`-animation`·`-audio`·`-cli`·`-creative`·
`-keyframes`·`-registry`)이 다 인식되면 성공.

**참고**: 이 컴퓨터에서는 확인해보니 HyperFrames가 `claude_pro` 프로젝트에만 있는
게 아니라 **사용자 계정 레벨**(`C:\Users\<계정명>\.claude\skills\hyperframes` 등)에도
이미 설치돼 있었다 — 이 경우 정션 없이도 이 저장소를 포함한 이 컴퓨터의 모든 로컬
프로젝트에서 HyperFrames가 자동으로 인식된다. 위 정션 설정은 그래도 안전장치로
남겨둔다 — 사용자 레벨 설치가 없는 다른 컴퓨터에서 작업하거나, 나중에 그 설치가
사라지는 경우에 대비한 대체 경로다.

## 나레이션(TTS) 생성 — HeyGen CLI는 이 PC에서 윈도우 네이티브 미지원 (2026-10-02 신설)

HyperFrames 숏츠의 내레이션은 원래 HeyGen CLI(`heygen voice speech create`,
원장님 클론 목소리 `5a123c0779304a2b99fa98d2c1be9e17`)로 생성하는 게 기본 경로지만,
**HeyGen CLI는 Windows 네이티브를 지원하지 않는다**(공식 문서: macOS/Linux만 지원,
Windows는 WSL 권장). 10주차에서 처음 이 문제를 만나 해결한 기록:

1. **WSL 설치**: 이 PC에는 이제 WSL(Ubuntu, 사용자명 `nineplus-aca`)이 설치돼 있다 —
   `wsl -d Ubuntu`로 열면 된다. `~/.local/bin`에 PATH를 추가해야 `heygen` 명령이
   인식된다(`export PATH="$HOME/.local/bin:$PATH"`, `~/.bashrc`에도 추가됨).
   WSL 설치 직후 `heygen auth login --oauth`의 브라우저 자동 실행이 막히면(WSL엔
   GUI 브라우저가 없음) 터미널에 출력되는 인증 URL을 윈도우 브라우저에 직접 열어
   로그인하면 된다 — 단, 이게 `ERR_CONNECTION_REFUSED`로 실패하면 `C:\Users\<계정>\.wslconfig`에
   `[wsl2]\nnetworkingMode=mirrored`를 추가하고 PowerShell에서 `wsl --shutdown` 후
   재시도한다(WSL2 NAT 모드에서 localhost 포트가 윈도우로 자동 전달 안 되는 경우가
   있음).
2. **무료 음성 생성 크레딧 소진**: 10주차 시점 기준 HeyGen 무료 플랜의 월간 음성
   생성 할당량이 거의 소진된 상태였다(`heygen user me get`으로 `Plan: free` 확인
   가능). 이 경우 당장 쓸 수 있는 대안:
   - **네이버 클로바더빙**(clovadubbing.naver.com) — 공개 API는 없어 웹사이트에서
     직접 문장별로 생성·다운로드해야 하지만, 무료이고 음질이 자연스럽다. 10주차는
     이 방식으로 전환해 완료했다.
   - **Edge-TTS**(`pip install edge-tts`) — 완전 무료·무제한·API 키 불필요, 한국어
     음성 3종(`ko-KR-InJoonNeural`·`ko-KR-HyunsuMultilingualNeural`·
     `ko-KR-SunHiNeural`) 지원하지만 합성 음성 티가 나서(AI스러움) 사용자가 거부한
     적 있다 — 급할 때 임시 대안 정도로만 쓴다.
   - **HeyGen API 직접 호출**(`POST https://api.heygen.com/v3/voices/speech`,
     `X-Api-Key` 헤더) — CLI의 무료 OAuth 경로가 아니라 유료 API 크레딧을 쓰는
     경로라 사용자 승인 후에만 진행한다.
   - `npx hyperframes tts`(로컬 Kokoro) — **한국어를 지원하지 않는다**(en/es/fr/hi/
     it/pt-br/ja/zh만 있음). 한국어 프로젝트에는 쓸 수 없다.
   - **Gemini TTS(2026-10-03 발견, 미검증 — 숏츠 작업 때 사용자에게 먼저 물어본다)**:
     `gemini-3.8-flash-tts`, 한국어 지원·무료 구간·말투 지시·AI Studio 음성 복제(본인
     10~30초 + 한국어 동의 문장 녹음). 생성 도구는 로컬
     `공용자료/참고자료/gemini_tts.py`(`GEMINI_API_KEY` 환경변수 필요, 컴퓨터마다 따로
     설정). 음질·복제 유사도는 아직 확인 전이라, 숏츠 나레이션 단계에서 사용 여부·키 설정·
     목소리(기본/복제)를 사용자에게 먼저 확인한다.
3. 다음 주차부터는 ①HeyGen 무료 할당량이 갱신됐는지 먼저 `heygen user me get`으로
   확인 → 남아있으면 CLI로 바로 생성, 소진됐으면 처음부터 클로바더빙으로 안내한다.

## 유지 관리

- `claude_pro`에서 HyperFrames가 업데이트되면(버전 갱신 등) 정션은 항상 최신 파일을
  그대로 가리키므로 이 저장소 쪽에서 따로 손볼 게 없다.
- `claude_pro` 폴더 자체를 다른 위치로 옮기면 정션이 깨진다 — 위 "정션 만들기"
  단계를 새 경로로 다시 실행한다.
- 이 저장소를 다른 컴퓨터에 새로 클론하면 정션은 그 컴퓨터에서 다시 만들어야
  한다(정션은 git으로 커밋되는 대상이 아니다 — `.claude/skills/hyperframes*`는
  `.gitignore`에 등록돼 있다).
