# 나인플러스학원 — 마케팅 자동화 프로젝트

학원 블로그·카드뉴스·숏츠·릴스·교육뉴스 콘텐츠를 만들고 여러 SNS 채널에 발행하는 일을 자동화하는 프로젝트다.

## 먼저 볼 문서

**[docs/operations-overview.md](docs/operations-overview.md)** — 채널별 자동/반자동/수동, 한 주 흐름, 에이전트 역할, 핵심 규칙을 한 장에 모은 기준 문서다. 작업을 시작하기 전에 먼저 읽는다. 이 문서와 상세 문서가 어긋나면 이 문서를 먼저 고친 뒤 상세 문서를 맞춘다.

## 상세 문서

- 콘텐츠를 어떻게 만드는가(원고·이미지·카드뉴스·숏츠·캡션 규칙): [docs/content-playbook.md](docs/content-playbook.md) — 콘텐츠 품질의 기준이며 이 규칙과 어긋나게 만들지 않는다.
- 자동 발행이 어떻게 구현됐는가(코드 위치·자격증명·API): [docs/publishing-plan.md](docs/publishing-plan.md)
- 무엇을·언제·어떤 방식으로 낼지, 다음 주제, 브리핑 절차: [docs/mainmanager-plan.md](docs/mainmanager-plan.md) — 게시물 기획안·일정·채널별 방식은 mainmanager 전담이라 **임의로 바꾸지 않는다.** 이번 주 블로그 주제와 22주 일정은 [docs/blog-calendar.md](docs/blog-calendar.md).
- 교육뉴스(별개 파이프라인): [docs/education-news-publishing.md](docs/education-news-publishing.md), 이력 미러 [docs/education-news-log.md](docs/education-news-log.md)
- 기록: [docs/sns-analysis-log.md](docs/sns-analysis-log.md)(순위·SNS·광고), [docs/naver-blog-posts.md](docs/naver-blog-posts.md)(발행된 네이버 글 주소), [docs/algorithm-search-log.md](docs/algorithm-search-log.md)
- 참고: [docs/ad-marketing-knowledge.md](docs/ad-marketing-knowledge.md)(광고법규·브랜딩), [docs/local-hyperframes-setup.md](docs/local-hyperframes-setup.md)(로컬 렌더링 연결)

## 에이전트(스킬)

| 스킬 | 역할 |
|---|---|
| [mainmanager](.claude/skills/mainmanager/SKILL.md) | 일정·주제·상태 총괄, 다른 에이전트 호출과 결과 확인, 브리핑·현황판. "오늘 할 일", "다음 주제", 정규 사이클 밖의 별도 작업 지시는 여기로 보낸다 |
| [sns_analysis_team](.claude/skills/sns_analysis_team/SKILL.md) | 네이버 블로그·플레이스 검색순위와 Meta(인스타·페이스북·스레드·광고) 분석. 추천만 하고 계획 문서를 직접 고치지 않으며 광고 집행·예산은 건드리지 않는다 |
| [education-news-team](.claude/skills/education-news-team/SKILL.md) | 월요일 교육뉴스 원고·채널 파일·큐 등록 |
| [content-derivation-team](.claude/skills/content-derivation-team/SKILL.md) | 블로그 원고에서 카드뉴스·숏츠 스토리보드·캡션·스레드·페이스북 글을 쓰고 렌더링 |
| [design_team](.claude/skills/design_team/SKILL.md) | 정지 이미지 1장 단위 디자인(대표이미지·삽화 오버레이). 다중 장면·영상은 content-derivation-team |
| [algorithm-searching-team](.claude/skills/algorithm-searching-team/SKILL.md) | 네이버·구글 알고리즘과 AEO/GEO 동향을 28일마다 조사해 `content-playbook.md` 갱신을 PR로 제안(자동 머지 없음, 사용자가 검토 후 머지) |

## 저장·보안 원칙

- 원고·이미지·카드뉴스·숏츠 같은 결과물은 **저장소에 두지 않고 로컬에만 보관**한다. 예외는 `queue/`·`queue-edu/`뿐이며 그 주 콘텐츠가 완성되어 발행 직전일 때만 올라오고 발행에 성공하면 자동 삭제된다(`docs/publishing-plan.md` "콘텐츠 큐").
- `queue/`·`queue-edu/`를 수정하면 지시가 없어도 곧바로 commit+push하고 원격 기준으로 자동 발행을 확인한다. `git add`는 경로를 지정한다(`docs/handover/` 같은 미추적 폴더가 딸려 올라가지 않게).
- 실제 API 키·토큰 값은 저장소에 커밋하지 않고 GitHub Actions Secrets로만 관리한다(이름과 용도는 `docs/publishing-plan.md` "자격증명").
- 되돌리기 어려운 작업(히스토리 정리·force push, 광고비 집행, 계정·결제 설정)은 사용자의 명시적 승인 뒤에만 한다.
