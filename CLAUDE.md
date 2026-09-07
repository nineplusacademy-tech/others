# 나인플러스학원 — 마케팅 자동화 프로젝트

학원 블로그/카드뉴스/숏츠/릴스 콘텐츠 제작과, 여러 SNS 채널 발행을 자동화하는 프로젝트입니다.

- 콘텐츠 제작 방법(원고 작성 규칙·이미지 규칙·카드뉴스/숏츠 스토리보드 규칙·캡션 규칙 등)은
  **[docs/content-playbook.md](docs/content-playbook.md)** 를 따른다. 이 문서가 콘텐츠 품질의 기준이며,
  여기 정리된 규칙과 어긋나는 방식으로 콘텐츠를 만들지 않는다.
- 자동 발행이 기술적으로 어떻게 구현됐는지(코드 위치·자격증명·API 세부사항)는
  **[docs/publishing-plan.md](docs/publishing-plan.md)** 를 따른다.
- **모든 게시물(블로그·교육뉴스)의 기획안(무슨 주제)·포스팅 일정(언제)·채널별
  자동/반자동 안내(어떻게)는 mainmanager 전담이며, 그 내용은
  [docs/mainmanager-plan.md](docs/mainmanager-plan.md)** 에 모아뒀다 — 절대 임의로
  바꾸지 않는다. 이번 주 블로그 주제 자체(22주 편집 일정·진행 상황)는
  [docs/blog-calendar.md](docs/blog-calendar.md)를 따른다.
- 실제 자동 발행 코드(GitHub Actions 워크플로/스크립트)는 이 저장소에 구현한다.
- "오늘 뭐 해야 하는지", "다음 기획안이 뭔지", 각 에이전트 상태 확인, 정규 사이클 밖의
  별도 작업 지시는 **[mainmanager](.claude/skills/mainmanager/SKILL.md)** 에게 시킨다.

## 콘텐츠 저장 원칙

원고·이미지·카드뉴스·숏츠 같은 실제 결과물은 **이 저장소에 평소 두지 않는다** — 로컬
컴퓨터에만 보관한다. 예외는 `queue/` 폴더뿐: 그 주 콘텐츠가 완성되어 발행 직전일 때만
잠깐 올라오고, 완전자동 4채널 발행에 성공하면 자동으로 삭제된다. 자세한 흐름은
`docs/publishing-plan.md`의 "콘텐츠 큐" 절 참고.

## 자격증명

실제 API 키/토큰 값은 이 저장소에 절대 커밋하지 않는다 — GitHub Actions Secrets로만 관리한다.
필요한 시크릿 이름 목록과 용도는 `docs/publishing-plan.md`의 "자격증명" 절 참고.

## 지침 자동 갱신 — 알고리즘-searching team

네이버·구글 검색 알고리즘과 AEO/GEO 동향을 조사해 `docs/content-playbook.md`를 최신
상태로 유지하는 전담 에이전트다. 4주(28일) 간격으로 자동 실행되며, 실행 이력은
`docs/algorithm-search-log.md`에 남는다. 스킬 정의:
[.claude/skills/algorithm-searching-team/SKILL.md](.claude/skills/algorithm-searching-team/SKILL.md).
지침 변경은 항상 PR로 올라오며 자동 머지되지 않는다 — 사용자가 검토 후 머지한다.

## 총괄 관리 — mainmanager

모든 게시물(블로그·교육뉴스)의 기획안·포스팅 일정·채널별 자동/반자동 안내와 확인을
전담하고(`docs/mainmanager-plan.md`), 다른 에이전트(algorithm-searching-team·
content-derivation-team·design_team·education-news-team)의 최근 상태를 취합해
보여줄 뿐 아니라 **조건이 갖춰지면 직접 해당 에이전트를 호출해 작업을 지시하고,
결과물이 규격·CTA 노출·과장광고 체크리스트 등 기준을 통과했는지 확인한 뒤에만 완료로
보고**한다(`mainmanager-plan.md` §8). 정규 기획안과 무관한 별도 작업 지시가 들어오면
기존 지침(content-playbook.md·publishing-plan.md) 그대로 다른 작업이 즉시 진행되도록
연결해주는 총괄 에이전트다. 매주 토요일 13:00 브리핑에서는 그 주 예정 주제를 제시해
"그대로 진행할지, 다른 주제를 찾아볼지" 확인받고, 블로그 원고가 완성되면 결과물을 보고한 뒤
사용자 승인이 있어야만 카드뉴스·숏츠 스토리보드 단계로 넘어간다. 또한
[docs/ad-marketing-knowledge.md](docs/ad-marketing-knowledge.md)(학원 광고법규·Meta
광고정책·SNS 브랜딩 트렌드)를 algorithm-searching-team과 같은 원칙(28일 주기·출처
기반)으로 학습·갱신하고 브리핑에 관련 인사이트를 반영한다(`mainmanager-plan.md` §9).
스킬 정의: [.claude/skills/mainmanager/SKILL.md](.claude/skills/mainmanager/SKILL.md).

## 카드뉴스·숏츠 제작 — content-derivation-team

mainmanager 승인 게이트 통과 후, 그 주 블로그 원고에서 소재를 뽑아 카드뉴스·숏츠
스토리보드+채널별 캡션+스레드 초안을 작성하고, 다시 사용자 승인을 받은 뒤 로컬
HyperFrames(`/hyperframes`, general-video 컴패니언 모드)로 실제 렌더링까지 진행하는
전담 에이전트다. 발행 자체는 담당하지 않는다(그건 `publishing-plan.md`의 큐
메커니즘). HyperFrames는 별도 로컬 프로젝트 `claude_pro`에 있으며, 이 저장소에는
파일을 복사하지 않고 윈도우 디렉터리 정션으로 경로만 연결한다 — 최초 1회 설정은
**[docs/local-hyperframes-setup.md](docs/local-hyperframes-setup.md)** 참고. 스킬 정의:
[.claude/skills/content-derivation-team/SKILL.md](.claude/skills/content-derivation-team/SKILL.md).

## 이미지 디자인 실행 — design_team

블로그 대표이미지·본문이미지처럼 **정지 이미지 1장 단위**의 실제 오버레이/디자인
제작을 전담하는 에이전트다. 로컬 Python/Pillow 스크립트·Canva·Figma·AI 이미지 생성
도구 중 작업 성격에 맞는 걸 매번 스스로 판단해서 고르고, 색상·레이아웃 등은
`content-playbook.md` §3 규칙을 그대로 따른다. 카드뉴스·숏츠 스토리보드 작성과
HyperFrames 렌더링(다중 씬·영상)은 이 스킬이 아니라 content-derivation-team 소관이다
— 정지 이미지냐 다중 씬/영상이냐로 구분한다. 채팅에 붙여넣은 사진은 파일로 추출할
수 없으므로, 실제 사진 원본은 항상 사용자가 로컬 경로에 저장해줘야 작업이
시작된다. 스킬 정의:
[.claude/skills/design_team/SKILL.md](.claude/skills/design_team/SKILL.md).

## 주간 교육뉴스 — education-news-team (이 저장소와 별개의 파이프라인)

이 프로젝트의 블로그/카드뉴스/숏츠 콘텐츠와는 완전히 별개로, 매주 네이버 밴드
회원(중고생 학부모·학생)용 중고등 교육/입시/내신/수능 뉴스 큐레이션을 만들어 발행한다.
주제 확정·원고 작성은 토요일 13:00에 시작하고, 구글 블로그 자동 발행은 월요일
12:00 KST에 이뤄진다(§ 아래).

- 담당은 **이 저장소의 스킬 `education-news-team`**
  ([.claude/skills/education-news-team/SKILL.md](.claude/skills/education-news-team/SKILL.md))이며,
  mainmanager의 지시(확정된 주제 또는 후보 조사 요청)를 받아 동작한다
  (`docs/mainmanager-plan.md` §8-1). 2026-09-08부로 이전에 쓰던 계정 레벨 스킬
  `education-news-weekly`는 더 이상 사용하지 않는다.
- 산출물(마크다운/밴드용/구글블로그 HTML 마스터본 3종 + 채널별 배포본 5종 + 업로드
  체크리스트 1종 + 삽화 1장, 총 10개 파일)은 **이 저장소가 아니라 로컬
  `클로드작업폴더/교육뉴스/` 아래에만** 보관한다 — 위 "콘텐츠 저장 원칙"과 동일하게
  실제 결과물은 로컬에만 둔다. 전 채널(카카오톡채널 포함) CTA·법정고시사항 없이
  해시태그로만 블로그 유입을 간접 유도하는 순수 정보성 방침을 따른다
  (`docs/education-news-publishing.md`).
- 발행 채널은 네이버 밴드·네이버 블로그·구글 블로그·유튜브(커뮤니티 게시물+동영상
  설명란)·당근마켓 비즈프로필·네이버플레이스·카카오톡채널, 총 8개다. 이 중 **구글
  블로그만 완전자동(API)** 이고 — 자세한 흐름은
  **[docs/education-news-publishing.md](docs/education-news-publishing.md)** 참고 —
  나머지 7채널은 여전히 사람이 체크리스트를 보고 직접 업로드한다(반자동). 두 자동화
  모두 `docs/mainmanager-plan.md` §1의 메인 콘텐츠 완전자동 4채널 시스템과는 별개의
  파이프라인이다.
- 주제 이력·다음 호 후보(원본은 로컬 `클로드작업폴더/교육뉴스/발행이력.md`)는
  **[docs/education-news-log.md](docs/education-news-log.md)** 에 스냅샷으로 미러링해
  둔다 — 이 저장소(원격/클라우드 세션 포함)는 로컬 파일에 접근할 수 없으므로, 사용자가
  로컬 발행이력.md를 갱신할 때마다 이 문서도 함께 최신화한다. 항상 로컬 발행이력.md가
  최종 원본이고 이 문서는 마지막 동기화 시점 스냅샷이라는 점에 유의한다.
- mainmanager는 토요일 13:00 브리핑에서 주제를 확정하고, 월요일 이후 스케줄 확인 시
  이 발행 여부도 함께 확인한다.
