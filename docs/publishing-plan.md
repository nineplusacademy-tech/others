# 발행 자동화 계획

콘텐츠 제작 규칙은 [content-playbook.md](content-playbook.md)를 따르고, 언제 무엇을
발행할지(주간 일정)·기획안·채널별 자동/반자동 요약 안내는
[mainmanager-plan.md](mainmanager-plan.md)를 따른다 — **이 문서는 자동화가 기술적으로
어떻게 구현됐는지(코드 위치·자격증명·API 세부사항)만 다룬다.**

## 1. 채널별 자동화 수준 (구현 상세 — 요약 안내는 mainmanager-plan.md §1 참고)

| # | 채널 | 자동화 수준 | 발행 콘텐츠 | 구현 방식 |
|---|---|---|---|---|
| 1 | 네이버 블로그 | 반자동 | 블로그 원고(`블로그용.txt`) | 원고 자동 준비 → 사람이 네이버 블로그에서 자체 예약발행 기능으로 **화요일 10:00** 예약 클릭 |
| 2 | 구글 블로그(Blogger) | **완전자동** | 블로그 원고(`구글블로그용.md`, HTML) | Blogger API v3 — GitHub Actions가 **화요일 10:00 KST**(`--phase blog`)에 직접 게시 |
| 3 | 유튜브 커뮤니티 게시판 | 반자동 | `유튜브_게시물.md` | Data API가 커뮤니티 탭 글쓰기 미지원 — 사람이 **목요일 20:00**(릴스·쇼츠와 동시) 직접 게시 |
| 4a | 페이스북 카드뉴스 (캐러셀) | **완전자동** | 카드뉴스 9장+블로그 링크(멀티포토 게시글) | Meta Graph API(페이지 토큰) — 사진 9장을 `published=false`로 각각 업로드 후 `/feed`에 `attached_media`로 묶어 게시(`facebook.publish_photo_carousel`, `_status.json` 키 `facebook_carousel`). 릴스와 API 흐름이 완전히 달라 별도 단계로 성공/실패를 추적한다. GitHub Actions가 **수요일 20:00 KST**(`--phase cardnews`)에 직접 게시 |
| 4b | 페이스북 릴스 | **완전자동** | 숏츠 9:16(`9x16_facebook.mp4`) | Meta Graph API(Resumable Upload, `facebook.publish_reel`, `_status.json` 키 `facebook_reel`) — **목요일 20:00 KST**(`--phase social`)에 직접 게시 |
| 5a | 인스타그램 카드뉴스 (캐러셀) | **완전자동** | 카드뉴스 9장(캐러셀) | Instagram Graph API(`instagram.publish_carousel`, `_status.json` 키 `instagram_carousel`) — **수요일 20:00 KST**(`--phase cardnews`)에 직접 게시 |
| 5b | 인스타그램 릴스 | **완전자동** | 숏츠 9:16(`9x16_instagram.mp4`) | Instagram Graph API(`instagram.publish_reel`, `_status.json` 키 `instagram_reel`) — **목요일 20:00 KST**(`--phase social`)에 직접 게시 |
| 6 | 스레드 | 반자동(당분간) | `스레드.md` | Threads API 앱 별도 구축 전까지 사람이 **화요일 12:30** 직접 게시 |
| 7 | 유튜브 쇼츠 | **완전자동** | 숏츠 9:16 mp4 | YouTube Data API v3 — **목요일 20:00 KST**(`--phase social`)에 직접 업로드 |
| 8 | 네이버클립 | 반자동 | 숏츠 9:16 mp4 + `네이버클립_소개글.md` | 업로드 API 없음 — 사람이 **목요일 20:00**(위와 동시) 직접 업로드 |
| - | 당근마켓 | 반자동 | 채널별 캡션 | 예약 기능 없음 — 사람이 **수요일 18:00** 직접 게시 |
| - | 카카오톡채널 | 반자동 | 채널별 캡션 | 사람이 **목요일 10:30**(야간 발송 제한 회피) 직접 게시 |
| - | 네이버플레이스 | 반자동 | 채널별 캡션(제목40자/설명1000자) | 사람이 **수요일 11:00** 직접 게시 |

**완전자동 채널**은 이미 API 자격증명 발급이 끝났고, GitHub Actions에서 지정 시각에
직접 API를 호출해 발행한다. 사람이 Meta Business Suite나 유튜브 스튜디오에 로그인해서
예약 버튼을 누를 필요가 없다. **2026-09-09부로 발행이 3단계 배치로 나뉜다**: 구글
블로그(화 10:00) → 카드뉴스 캐러셀(수 20:00) → 릴스·쇼츠(목 20:00). 카드뉴스와
릴스/쇼츠를 애초에 같은 목요일에 함께 냈었는데, 같은 계정이 같은 팔로워에게 같은
시각 두 게시물을 내면 알고리즘 노출을 서로 갉아먹고 카드뉴스(저장·정독, 팔로워
대상)와 릴스(발견·확산, 비팔로워 대상)는 노출 경로 자체가 달라 따로 낼 이유가
분명하다는 판단으로 하루 갈랐다(2026-09-08 결정) — `scripts/publish/main.py`가
`--phase blog`/`--phase cardnews`/`--phase social` 인자로 어느 배치인지 구분한다
(§3-1 참고).

**반자동 채널**은 콘텐츠(원고/캡션/영상)까지만 자동으로 준비되고, 실제 게시 버튼
클릭은 항상 사람이 한다. 네이버 블로그처럼 그 플랫폼 자체에 예약발행 기능이 있으면
원고 완성 직후 사람이 한 번 예약해두는 것으로 화요일 발행이 이미 해결된다.

## 2. 콘텐츠 큐 — 로컬 보관 + 발행 직전만 깃허브 업로드

원고·이미지·카드뉴스·숏츠 같은 실제 결과물은 평소 **로컬 컴퓨터에만** 보관한다
(이 저장소에는 안 둠). 콘텐츠 작성은 사용자가 로컬에서 기존 방식(클로드코드 +
HyperFrames)대로 계속 진행하고, 이미 그 과정에서 검토·승인이 끝난 상태로 본다.

자동 발행이 실제로 동작하려면 GitHub Actions가 읽을 수 있는 곳에 파일이 있어야
하므로, **그 주 콘텐츠가 완성되면 발행 직전에만** 아래 큐 폴더에 업로드한다.

```
queue/<번호>_<주제요약>/
  블로그/구글블로그용.md            ← Blogger API가 그대로 게시
  카드뉴스/instagram/01.png ~ 09.png ← 인스타그램 캐러셀 전용(댓글'9'+더보기 CTA)
  카드뉴스/facebook/01.png ~ 09.png ← 페이스북 캐러셀 전용(더보기만 CTA, 2026-09-08 표지 1장→9장 캐러셀로 전환)
  카드뉴스/채널별_캡션.md           ← 인스타·페이스북 캡션 추출용
  숏츠/9x16_instagram.mp4          ← 인스타 릴스 전용
  숏츠/9x16_facebook.mp4           ← 페이스북 릴스 전용
  숏츠/9x16_youtube.mp4            ← 유튜브 쇼츠 전용
  숏츠/채널별_캡션.md               ← 릴스용 인스타·페이스북 캡션
  숏츠/캡션_유튜브쇼츠.md
  스레드.md                         ← (선택) 화요일 12:30 스레드 자동 게시용, §6 참고
  _status.json                      ← 발행 워크플로가 자동 생성/갱신 (직접 만들 필요 없음)
```

카드뉴스·숏츠 모두 **채널마다 온스크린 CTA 문구가 달라서**(§7 — 인스타는 댓글'9'+
더보기, 페이스북은 더보기만, 유튜브는 고정댓글) 2026-09-08부터 플랫폼별로 파일을
따로 렌더링한다. `scripts/publish/main.py`가 이 폴더/파일명 그대로 채널별 함수에서
읽으므로, `content-derivation-team`이 결과물을 저장할 때 반드시 이 구조를 따라야
발행이 실제로 채널별로 구분되어 나간다(`content-playbook.md` §11 참고).

### 각 파일의 정확한 형식 (`scripts/publish/`가 이 형식 그대로 읽는다)

**`블로그/구글블로그용.md`** — YAML 프런트매터 + HTML 본문. `title`·`labels`·
`search_description` 셋 다 프런트매터 안에 있어야 실제로 게시글에 반영된다 —
본문 상단에 HTML 주석(`<!-- 검색 설명: ... -->`)으로만 적어두면 파서가 읽지
않아 그대로 빈 채로 게시된다(2026-09-08 36주차 스터디플래너 실사고로 확인 —
검색 설명·라벨·제목이 전부 비어서 나갔다가 Blogger 대시보드에서 직접 수정).
`fill_image_placeholders()`가 본문의 `<img src="[사진 자리 N · 설명]">`도
같은 폴더의 실제 파일(공백 제거 매칭)로 자동 치환하므로, 이미지 파일도
`구글블로그용.md`와 같은 폴더에 함께 큐에 올려야 한다. `labels`는 블로그 상단
메뉴 카테고리(`교육뉴스`/`학습법`/`학원소식`/`합격후기`) 중 그 글에 맞는 것
**정확히 1개**만 넣는다 — SNS 해시태그처럼 여러 개 넣지 않는다(2026-09-08
확인, content-playbook.md §2-9 참고).

```markdown
---
title: 포스트 제목
labels: [학습법]
search_description: 검색 결과에 노출될 요약(150자 내외)
---
<h2>소제목</h2>
<p>본문...</p>
<img src="[사진 자리 1 · 대표이미지]" alt="...">
<!-- 위 예시처럼 본문 중간의 이미지 자리는 같은 폴더의 실제 파일명(대표이미지.png 등,
     공백 제거 매칭)으로 자동 치환된다 -->
```

**`카드뉴스/채널별_캡션.md`, `숏츠/채널별_캡션.md`** — `## 채널명` 으로 구분. 스크립트는
`## 인스타그램`, `## 페이스북` 두 섹션만 읽고 나머지(당근마켓 등)는 사람이 반자동
게시할 때 참고하는 용도로 그대로 둔다. 페이스북 섹션에 `{{BLOG_URL}}`이라고 써두면
실제 발행 시 그 자리에 **네이버 블로그** 글 주소가 자동으로 채워진다 — 독자가 실제로
아는 "원문"은 네이버 블로그이지 구글 블로그(SEO/AEO용 미러)가 아니기 때문이다
(2026-09-09 정정, 아래 참고). 네이버 URL이 `_status.json`에 아직 안 적혀 있으면
구글 블로그 주소로 대신 채우고 경고를 남긴다.

```markdown
## 인스타그램
캡션 텍스트...

## 페이스북
캡션 텍스트... 전체 글 보기 👉 {{BLOG_URL}}

## 당근마켓
(사람이 금요일에 참고해서 직접 게시)
```

**`숏츠/캡션_유튜브쇼츠.md`** — YAML 프런트매터(제목) + 본문(설명)

```markdown
---
title: 영상 제목(100자 이내)
---
영상 설명(최대 5,000자)...
```

**`스레드.md`** — 프런트매터 없이 게시물 본문 그대로(500자 이내, `content-playbook.md`
§9). `{{BLOG_URL}}` 자리는 발행 시 네이버 블로그 URL로 채워진다. 파일이 없으면
그 주는 자동 게시 대상이 아니라는 뜻으로 조용히 건너뛴다 — 카드뉴스 캐러셀을
첨부하기로 한 주는 아직 자동화 대상이 아니라 사람이 그대로 수동 게시한다.

**흐름:**

1. 로컬에서 그 주 콘텐츠(구글블로그용.md, 카드뉴스 PNG 9장, 숏츠 mp4, 캡션 파일들)가
   완성되면, 사용자가 `queue/<번호>_<주제요약>/`에 그대로 복사해 이 저장소에 커밋·푸시
   한다(로컬 원본은 그대로 둔 채 복사만 — 결과물은 로컬과 깃허브 양쪽에 잠시 존재).
2. **화요일 10:00 KST**, 예약 발행 워크플로가 `--phase blog`로 실행돼 `queue/` 아래
   폴더를 찾아 구글 블로그만 먼저 게시한다(2026-09-08부터 — 다른 채널 캡션이 이
   블로그 URL을 참조하므로 항상 먼저 끝나야 한다). 이 시점엔 아직 6채널이 다 끝난
   게 아니므로 큐 폴더는 삭제되지 않는다.
2-1. **같은 날, 네이버 블로그가 예약 발행되고 나면(반자동, §1 표)** 사람이
   `python scripts/publish/set_naver_url.py <네이버 블로그 글 URL>`을 저장소
   루트에서 실행해 실제 글 주소를 `_status.json`의 `naver_blog_url`에 기록해둔다
   (2026-09-09 신설, `naver_blog_url`은 완료 판정에 쓰는 `ALL_STEPS`에는 포함되지
   않는 부가 필드). 카드뉴스·릴스 캡션과 화요일 스레드의 `{{BLOG_URL}}`은 이 값을
   우선해서 쓴다 — 독자가 실제로 아는 "원문"은 네이버 블로그이지, 완전자동 SEO/AEO
   미러인 구글 블로그가 아니기 때문이다. 이 단계를 잊으면 수요일 배치가 구글 블로그
   주소로 대신 채우고 경고 로그를 남긴다(발행이 막히지는 않지만, 캡션의 원문 링크가
   독자가 모르는 주소로 나간다).
   같은 날 **교육뉴스 네이버 블로그**가 발행되면(별개 파이프라인, 반자동)
   `python scripts/publish/set_naver_url.py --edu <URL>`로 `queue/_edu_thread_link.json`에
   따로 기록해둔다(2026-09-09 신설) — 목요일 스레드(교육뉴스 원문 링크 게시,
   `content-playbook.md` §9)가 이 파일을 읽는다. `queue-edu/`는 구글 블로그 발행
   성공 즉시 삭제되는 구조라 그 안에는 목요일까지 상태를 못 들고 있어서, 큐 폴더와
   무관한 별도 파일에 보관한다.
2-2. **같은 날 12:30 KST**, 별도 워크플로(`publish-thread.yml`)가 `queue/` 폴더에
   `스레드.md`가 있으면 `naver_blog_url`을 채워 넣어 자동 게시한다(§6). 성공 여부는
   `_status.json`의 `thread` 키에 기록하지만, 이 키는 `ALL_STEPS`(6채널 완료 판정)에
   포함되지 않는다 — 스레드 게시가 지연되거나 실패해도 기존 6채널 완료 후 큐 폴더
   삭제에 영향을 주지 않는다.
3. **수요일 20:00 KST**, 같은 워크플로가 `--phase cardnews`로 실행돼 카드뉴스
   캐러셀 2채널(페이스북·인스타그램)에 게시한다(2026-09-09부터 — 릴스와 같은 날
   같은 시각에 내면 같은 팔로워에게 알고리즘 노출이 서로 갉아먹혀서 하루 뺐다).
4. **목요일 20:00 KST**, 같은 워크플로가 `--phase social`로 실행돼 릴스·쇼츠
   3채널(페이스북·인스타그램·유튜브 쇼츠)에 동시에 게시한다.
5. **6채널 모두 게시에 성공하면**, 그 시점 워크플로가 `queue/<번호>_<주제요약>/`
   폴더를 삭제하는 커밋을 자동으로 만들어 푸시한다 — 깃허브에는 다시 남지 않고,
   로컬 원본만 계속 보관된다.
6. 하나라도 게시에 실패하면 그 채널만 재시도 대상으로 표시하고, **큐 폴더는 삭제하지
   않는다**(성공한 채널까지 기록해두고, 실패한 채널만 다음 실행에서 재시도 — 중복
   게시 방지를 위해 채널별 성공 여부를 큐 폴더 안에 작은 상태 파일로 같이 커밋해둔다).
7. 반자동 채널(네이버 블로그·유튜브 커뮤니티·네이버클립·당근·카카오톡채널·
   네이버플레이스·스레드)은 이 큐와 무관하게, 사용자가 로컬 원본을 보면서 각 플랫폼에
   직접 게시한다(요일·시각은 §1 표 참고).

이렇게 하면 이 저장소에는 평소 일정표(`blog-calendar.md`)·진행현황·자동화 코드만
남고, 실제 콘텐츠 파일은 발행 성공 즉시 사라져 "결과물은 로컬에만 보관"이라는
원칙이 유지된다.

**저장소가 퍼블릭인 이유**: 인스타그램 Graph API는 파일 직접 업로드를 지원하지
않고 반드시 공개 URL(`image_url`/`video_url`)을 요구한다. 그래서 이 저장소를
퍼블릭으로 전환해, `queue/` 안의 이미지·영상을 `raw.githubusercontent.com` 주소로
인스타그램이 바로 읽어갈 수 있게 했다(`scripts/publish/common.py`의
`raw_github_url()`). 발행 성공 즉시 파일이 삭제되므로 노출 기간은 짧다. **이
저장소에는 절대 실제 자격증명 값을 커밋하지 않는다** — 퍼블릭이라 더더욱 중요하다.

## 3. 실제 구현 위치

- `scripts/publish/main.py` — 오케스트레이터. `queue/` 폴더 하나를 찾아 6단계
  (Blogger → 페이스북 캐러셀 → 인스타 캐러셀 → 페이스북 릴스 → 인스타 릴스 →
  유튜브 쇼츠) 순서로 발행하고, 단계별 성공 여부를 `_status.json`에 기록해
  재실행 시 이미 끝난 단계는 건너뛴다. 전부 끝나면 큐 폴더를 삭제한다. `--phase`
  인자로 이번 실행이 블로그 단계까지만인지, 카드뉴스 2채널까지인지, 릴스·쇼츠
  3채널까지인지, 한 번에 전부인지 고른다(§3-1).
- `scripts/publish/{blogger,facebook,instagram,youtube}.py` — 채널별 API 호출.
- `.github/workflows/publish.yml` — cron 3개(화요일 01:00 UTC=10:00 KST →
  `--phase blog`, 수요일 11:00 UTC=20:00 KST → `--phase cardnews`, 목요일
  11:00 UTC=20:00 KST → `--phase social`) + `workflow_dispatch`로 phase를 골라
  수동 테스트 가능. 실행 후 `_status.json` 변경이나 큐 폴더 삭제를 항상 커밋·
  푸시한다(중간에 실패해도 `if: always()`로 상태는 저장됨).
- `scripts/publish/refresh_instagram_token.py` + `.github/workflows/refresh-instagram-token.yml`
  — 매달 1일·15일에 인스타그램 토큰을 갱신하고 GitHub Secret에 자동으로 다시
  저장(아래 5절).
- `scripts/publish/set_naver_url.py` — 네이버 블로그(반자동)가 실제로 발행된 뒤
  사람이 직접 실행해 그 글 주소를 기록하는 1회성 CLI(2026-09-09 신설, §2 흐름
  2-1번). 인자 없이 실행하면 메인 블로그용(`_status.json`의 `naver_blog_url`),
  `--edu` 플래그를 주면 교육뉴스용(`queue/_edu_thread_link.json`, 목요일 스레드가
  읽음)으로 기록한다.
- `scripts/publish/main_thread.py` + `.github/workflows/publish-thread.yml` — 화요일
  12:30 KST(03:30 UTC)에 `queue/`의 `스레드.md`를 텍스트로 자동 게시(§6, 2026-09-09
  구현). `scripts/publish/threads.py`가 실제 그래프 API 호출을 담당한다.
- `scripts/publish/refresh_threads_token.py` + `.github/workflows/refresh-threads-token.yml`
  — 매달 2일·16일에 스레드 토큰을 갱신하고 GitHub Secret에 자동으로 다시 저장(§6).

### 3-1. 3단계 배치(`--phase`) 동작 방식 (2026-09-08 신설, 2026-09-09 카드뉴스 분리)

`main.py`가 매번 6채널을 전부 발행하던 것을, 화요일/수요일/목요일 세 번의 워크플로
실행에 걸쳐 나눠 처리하도록 바꿨다 — 배경은 §1의 "발행 요일을 정한 근거"
(`mainmanager-plan.md` §1-1)와 동일: 블로그 원문을 먼저 내보내 검색 유입을 잡고,
수요일 저녁 카드뉴스(저장·정독, 팔로워 대상)로 재환기한 뒤, 목요일 저녁 릴스·쇼츠
(발견·확산, 비팔로워 대상)로 다시 환기한다 — 카드뉴스와 릴스를 같은 날 같은 시각에
내면 같은 팔로워에게 알고리즘 노출이 서로 갉아먹혀 하루씩 갈랐다(2026-09-08 결정).

- `--phase blog`(화요일): 구글 블로그 단계만 실행하고 끝난다. `_status.json`에
  `blogger`만 기록되므로 `all_steps_done()`이 아직 `False`다 — 큐 폴더는 삭제되지
  않고 다음 배치를 기다린다.
- `--phase cardnews`(수요일): 블로그가 이미 끝나 있어야 한다 — 안 끝나 있으면 에러를
  내고 멈춘다. `_status.json`의 `naver_blog_url`(사람이 §2 흐름 2-1번으로 미리
  기록해둔 값)을 읽어 캡션의 `{{BLOG_URL}}`을 채우고, 그게 없으면 `blogger.url`
  (구글 블로그)로 대신 채우며 경고를 남긴다. 카드뉴스 캐러셀 2채널(페이스북·
  인스타그램)을 동시에 발행한다.
- `--phase social`(목요일): 블로그가 이미 끝나 있어야 한다(카드뉴스 완료 여부는
  확인하지 않는다 — 서로 독립적인 배치). 릴스·쇼츠 3채널(페이스북·인스타그램·
  유튜브 쇼츠)을 스레드풀로 동시에 발행하고, 이 시점까지 6단계가 전부 끝나 있으면
  큐 폴더를 삭제한다.
- `--phase all`(기본값): 예전처럼 한 번에 전부 — 수동 재시도나 dry-run 점검용으로
  남겨뒀다.
- 세 워크플로 실행은 `_status.json`이라는 같은 상태 파일을 통해 이어진다 — 화요일
  실행이 커밋해둔 `_status.json`을 수요일·목요일 실행이 그대로 읽어 이어서 처리하는
  구조라, 재시도·부분 실패 로직(§2의 6~7번)이 그대로 세 배치에도 적용된다.

## 4. 자격증명 (GitHub Actions Secrets로만 관리 — 이 저장소에 값 자체를 커밋하지 않음)

| Secret 이름 | 용도 | 비고 |
|---|---|---|
| `GOOGLE_OAUTH_CLIENT_ID` | Blogger/YouTube 인증 | 웹 애플리케이션 타입 OAuth 클라이언트 |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Blogger/YouTube 인증 | 위 클라이언트의 시크릿 |
| `GOOGLE_OAUTH_REFRESH_TOKEN` | Blogger/YouTube 인증 | 만료 없음(프로덕션 게시 상태 확인됨) |
| `BLOGGER_BLOG_ID` | 어느 Blogger 블로그에 올릴지 | Blogger API `blogs.getByUrl` 등으로 조회해서 채워넣기 |
| `FACEBOOK_PAGE_ID` | 페이스북 페이지 게시 대상 | 1265899359934473 (나인플러스수학학원) |
| `FACEBOOK_PAGE_ACCESS_TOKEN` | 페이스북 카드뉴스 캐러셀·릴스 + (2026-09-12부) `insights.yml` 인사이트 조회 | 만료 없음(Page 토큰) — 그래도 가끔 debug_token으로 유효성 점검 권장 |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | 인스타그램 게시 대상 | 27167215579620807 (nineplus_math) |
| `INSTAGRAM_ACCESS_TOKEN` | 인스타그램 캐러셀·릴스 + (2026-09-12부) `insights.yml` 인사이트 조회 | 60일 만료 — `refresh-instagram-token.yml`이 자동 갱신. 인사이트 조회 권한(`instagram_manage_insights` 등)까지 있는지는 §7 참고 |
| `GH_PAT` | 인스타그램·스레드 토큰 자동 갱신 시 이 저장소의 Secret을 다시 쓰기 위함 | 이 저장소에 "Secrets: Read and write" 권한을 준 fine-grained PAT. 기본 `GITHUB_TOKEN`은 Secrets API 쓰기 권한이 없어서 별도 PAT 필요 |
| `THREADS_USER_ID` | 스레드 게시 대상 계정 | 17841469176062079 (nineplus_math) — 공개 식별자라 값 자체는 민감하지 않음 |
| `THREADS_ACCESS_TOKEN` | 스레드 텍스트 게시 | 60일 만료 — `refresh-threads-token.yml`이 자동 갱신 |

`GEMINI_API_KEY`(블로그 이미지 생성)는 콘텐츠 작성이 로컬에서 이뤄지므로 이
저장소의 Secrets에는 필요 없다 — 로컬 작업 환경에만 보관한다.

## 5. 인스타그램 토큰 자동 갱신 (구현됨)

인스타그램 액세스 토큰은 60일 후 만료된다. `refresh-instagram-token.yml`이 매달
1일·15일에 자동으로:

1. `scripts/publish/instagram.py`의 `refresh_access_token()`으로 새 토큰 발급
   (`GET https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=...`)
2. `scripts/publish/refresh_instagram_token.py`가 GitHub Secrets API를 호출해
   `INSTAGRAM_ACCESS_TOKEN` Secret 값을 새 토큰으로 덮어씀 (libsodium sealed box로
   암호화해서 전송 — `PyNaCl` 사용)

새로 발급된 토큰 값은 어떤 경우에도 print/log 하지 않는다 — 저장소가 퍼블릭이라
Actions 로그도 공개되고, 아직 Secret에 등록 전인 값은 GitHub의 자동 로그 마스킹
대상이 아니기 때문이다.

### 5-1. 스레드 토큰 자동 갱신 (구현됨, 2026-09-09)

스레드 장기 액세스 토큰도 60일 후 만료된다. `refresh-threads-token.yml`이 매달
2일·16일(인스타그램 갱신과 하루 띄움)에 자동으로:

1. `scripts/publish/threads.py`의 `refresh_access_token()`으로 새 토큰 발급
   (`GET https://graph.threads.net/v1.0/refresh_access_token?grant_type=th_refresh_token&access_token=...`)
2. `scripts/publish/refresh_threads_token.py`가 `common.update_github_secret()`으로
   `THREADS_ACCESS_TOKEN` Secret 값을 새 토큰으로 덮어씀(인스타그램과 같은
   libsodium sealed box 암호화 로직을 `common.py`로 공유)

## 6. 스레드(Threads) 완전자동 게시 (구현됨, 2026-09-09)

Threads API는 같은 Meta 앱 안에서 Facebook 로그인/페이지 관리 이용 사례와 함께 쓸 수
없어(Meta 앱 생성 시 확인된 제약) 별도 Meta 앱 `threads_nineplus`를 새로 만들고,
"Threads API 액세스" 이용 사례만 선택해 `nineplus_math` 계정을 테스터로 연결한 뒤
장기 액세스 토큰을 발급받았다.

- **화요일 12:30 KST**, `.github/workflows/publish-thread.yml`이 `main.py`의 3단계
  배치와는 독립적으로 실행돼 `scripts/publish/main_thread.py`가 `queue/`의
  `스레드.md`를 텍스트 게시물로 올린다(`scripts/publish/threads.py`,
  `graph.threads.net/v1.0`).
- **카드뉴스 캐러셀 첨부는 아직 자동화 대상이 아니다** — 이미지 첨부를 하기로 한
  주는 `content-playbook.md` §9 그대로 사람이 직접 게시한다. `스레드.md`가 큐에
  없으면(카드뉴스 첨부 주 등) 조용히 건너뛴다.
- **목요일 교육뉴스 스레드는 여전히 반자동이다** — 별개 파이프라인(`queue-edu/`)이라
  이 자동화 대상이 아니고, 예약 작업 `edu-thread-reminder`가 초안을 제시하면 사람이
  같은 `threads_nineplus` 앱/토큰이 아니라 직접 앱에서 게시한다.

## 7. SNS 인사이트 조회 (읽기 전용, 신설 2026-09-12)

`sns_analysis_team`이 네이버 블로그·플레이스뿐 아니라 인스타그램·페이스북 성과도
같이 참고할 수 있도록, 발행에 쓰는 것과 동일한 Meta 토큰(`INSTAGRAM_ACCESS_TOKEN`·
`FACEBOOK_PAGE_ACCESS_TOKEN`)으로 **게시 없이 조회만** 하는 별도 파이프라인이다.

- `scripts/publish/insights.py`: Graph API 인사이트 엔드포인트를 호출하는 함수
  모음(계정 요약, 최근 게시물별 reach·좋아요·댓글·저장·공유, 릴스 재생수 등).
- `scripts/publish/append_insights_log.py`: 위 결과를 마크다운으로 정리해
  `docs/sns-analysis-log.md` 끝에 append(기존 내용은 지우지 않음).
- `.github/workflows/insights.yml`: **매주 토요일 12:00 KST**(콘텐츠 브리핑
  13:00보다 먼저) 자동 실행 + `workflow_dispatch`로 수동 실행 가능. 조회만 하므로
  실패해도 발행 파이프라인에 영향 없음.

메트릭은 **하나씩 개별 요청**한다(콤마로 묶으면 그중 하나라도 무효한 메트릭이 있을
때 Graph API가 요청 전체를 400으로 거부해 멀쩡한 값까지 못 받아온다 — 2026-09-12
첫 실행에서 실제로 겪음). 특정 메트릭이 실패해도 스크립트가 나머지는 계속 진행하고
실패 사유를 그대로 남기도록 만들어져 있다 — "값이 0"과 "조회 실패"를 구분해서
읽어야 한다.

queue/_status.json에 남는 게시물 ID는 재사용하지 않는다 — 전 채널 발행이
끝나면 `main.py`가 큐 폴더를 즉시 삭제하므로 ID가 남아있지 않다. 대신 계정의
"최근 미디어/게시물 목록"을 API로 직접 가져와 최근 N개를 조회하는 방식이다.

**2026-09-12 첫 실행 결과 및 후속 조치**:

- 인스타그램 캐러셀·페이스북 게시글 일부는 정상 조회됨(예: reach=27, likes=0
  같은 실제 값을 받아옴) — 토큰 자체의 기본 인사이트 조회 권한은 있는 것으로
  확인.
- **메트릭 이름 문제(코드로 수정 완료)**: 인스타그램 릴스의 `plays`,
  페이스북 페이지의 `page_impressions`·`page_fans`, 게시물의 `post_impressions`가
  전부 "invalid metric" 오류를 냈다 — Meta가 2025-11-15부로 조회수 계열 메트릭을
  전부 `views`(인스타그램) 또는 `page_follows`·`page_media_view`·`post_media_view`
  (페이스북)로 통합했기 때문(Meta 개발자 블로그 2025-08-15 공지). `insights.py`를
  새 메트릭 이름으로 수정 완료 — 다음 토요일(12:00 KST) 자동 실행에서 확인 예정.
- **미해결 — 사용자 조치 필요**: 페이스북 **영상(릴스) 인사이트**만
  `(#200) read_insights permission missing`으로 403이 남 — 메트릭 이름 문제가
  아니라 `FACEBOOK_PAGE_ACCESS_TOKEN` 자체에 `read_insights` 권한이 아예 없다는
  뜻이라 코드로 고칠 수 없다. Meta for Developers(개발자 앱 설정) 또는 Graph API
  Explorer에서 해당 권한을 추가해 토큰을 재발급하고, `FACEBOOK_PAGE_ACCESS_TOKEN`
  Secret 값을 갱신해야 한다 — 페이지 게시글 인사이트·인스타그램 인사이트는 이미
  정상 작동하므로 급하지 않다면 페이스북 릴스 조회수만 계속 비어 있는 채로 둬도
  다른 기능에는 영향 없다.

**2026-09-12 두 번째 실행 결과 및 후속 조치**: 인스타그램은 릴스·캐러셀 전부
reach·likes·comments·saved·shares·views가 정상 조회됨(예: 릴스 reach=149,
views=170) — 완전히 해결. 페이스북 페이지/게시물 쪽은 두 가지 문제가 더
있었다:

1. **`page_engaged_users`가 400 에러** — Meta 공식 "폐기된 메트릭" 문서
   확인 결과 이 메트릭은 **2024-03-14부로 이미 폐기**됐고 명시된 대체
   메트릭이 없다. 목록에서 제외했다.
2. **`page_follows`·`page_media_view`·`post_media_view`가 에러 없이 값도
   없이 빈 응답만 왔다** — 원인은 메트릭 이름이 아니라 **메트릭마다 지원하는
   `period`가 다른데 전부 같은 period(`week`)로 묶어 요청**했기 때문(Meta
   공식 문서 확인, 2026-09-12): `page_follows`는 **day만**,
   `page_media_view`는 day/week/days_28, `post_media_view`는 **lifetime만**
   지원한다. `_fetch_metrics_one_by_one()`이 메트릭마다 다른 파라미터를 줄 수
   있도록 `(메트릭, 전용 파라미터)` 튜플을 받게 고치고, 각 메트릭에 맞는
   period를 지정했다. `post_engaged_users`도 Meta 공식 참조 문서에 더 이상
   등재돼 있지 않고 실제로 400을 내서 제외했다(대체 메트릭 미확인 —
   `post_reactions_by_type_total`은 그대로 유지).

**2026-09-12 세 번째 실행 — `read_insights` 권한 추가 후**: 사용자가
Meta for Developers(`blogTOsns_nineplus` 앱)에서 `read_insights` 권한을
추가하고, Graph API Explorer로 만료 없는 새 페이지 토큰을 발급해
`FACEBOOK_PAGE_ACCESS_TOKEN` Secret을 갱신했다. 그 결과:

- **페이스북 페이지/게시물 인사이트가 전부 정상 조회됨** —
  `page_follows=13`, `page_media_view=99`, 게시물별 `post_media_view`
  (6~230 사이 실제 값), `post_reactions_by_type_total` 정상. `read_insights`
  권한 누락이 페이지/게시물 인사이트가 에러 없이 빈 값만 나오던 진짜
  원인이었다 — period 문제와 권한 문제가 동시에 있었던 것.
- **페이스북 일반 영상 인사이트는 정상**(`total_video_views` 등, 값 0이지만
  실제 조회 성공 — 오래된 홍보 안 된 영상이라 0인 게 타당함).
- **페이스북 릴스(Reels)만 여전히 빈 응답** — 원인은 릴스가 일반 영상과
  다른 전용 재생수 메트릭(`blue_reels_play_count`)을 쓰기 때문(Meta
  개발자 블로그 2022-12-15 공지). `total_video_views` 등 일반 영상
  메트릭을 릴스에 물으면 에러 없이 빈 응답만 온다. `insights.py`에
  `blue_reels_play_count`를 추가해 둘 다 시도하도록 수정 — 다음 실행에서
  확인 예정.
- **인스타그램 계정 인사이트도 재점검**: `profile_views`는
  2025-01-08부로 폐기됐고(Graph API v21+), `accounts_engaged`는
  `metric_type=total_value` 파라미터가 있어야 값이 온다(없으면 에러 없이
  빈 응답) — `profile_views`는 제거하고 `accounts_engaged`에 해당
  파라미터를 추가했다.

다음 토요일(12:00 KST) 자동 실행 또는 수동 실행에서 위 두 가지(릴스
재생수·계정 참여 지표)가 정상 조회되는지 확인 예정.
