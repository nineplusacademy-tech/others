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
열리면 성공이다. `content-derivation-team` 스킬을 실행하기 전 이 확인을 먼저
해본다 — 정션이 깨져 있으면(예: `claude_pro` 폴더 위치를 옮긴 경우) 위 명령을 다시
실행해서 다시 연결한다.

## 유지 관리

- `claude_pro`에서 HyperFrames가 업데이트되면(버전 갱신 등) 정션은 항상 최신 파일을
  그대로 가리키므로 이 저장소 쪽에서 따로 손볼 게 없다.
- `claude_pro` 폴더 자체를 다른 위치로 옮기면 정션이 깨진다 — 위 "정션 만들기"
  단계를 새 경로로 다시 실행한다.
- 이 저장소를 다른 컴퓨터에 새로 클론하면 정션은 그 컴퓨터에서 다시 만들어야
  한다(정션은 git으로 커밋되는 대상이 아니다 — `.claude/skills/hyperframes*`는
  `.gitignore`에 등록돼 있다).
