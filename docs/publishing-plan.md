# 발행 자동화 계획

콘텐츠 제작 규칙은 [content-playbook.md](content-playbook.md)를 따르고, 이 문서는
"어느 채널을 어떻게 발행하는가"만 다룬다.

## 1. 채널별 자동화 수준

| # | 채널 | 자동화 수준 | 발행 콘텐츠 | 구현 방식 |
|---|---|---|---|---|
| 1 | 네이버 블로그 | 반자동 | 블로그 원고(`블로그용.txt`) | 원고 자동 준비 → 사람이 네이버 블로그에서 자체 예약발행 기능으로 목요일 09:00 예약 클릭 |
| 2 | 구글 블로그(Blogger) | **완전자동** | 블로그 원고(`구글블로그용.md`, HTML) | Blogger API v3 — GitHub Actions가 목요일 09:00 KST에 직접 게시 |
| 3 | 유튜브 커뮤니티 게시판 | 반자동 | `유튜브_게시물.md` | Data API가 커뮤니티 탭 글쓰기 미지원 — 사람이 목요일 직접 게시 |
| 4 | 페이스북 (게시글 · 릴스) | **완전자동** | 카드뉴스 표지+블로그 링크(게시글), 숏츠 9:16(릴스) | Meta Graph API(페이지 토큰) — GitHub Actions가 목요일 09:00 KST에 직접 게시 |
| 5 | 인스타그램 (캐러셀 · 릴스) | **완전자동** | 카드뉴스 9장(캐러셀), 숏츠 9:16(릴스) | Instagram Graph API — GitHub Actions가 목요일 09:00 KST에 직접 게시 |
| 6 | 스레드 | 반자동(당분간) | `스레드.md` | Threads API 앱 별도 구축 전까지 사람이 금요일 직접 게시 |
| 7 | 유튜브 쇼츠 | **완전자동** | 숏츠 9:16 mp4 | YouTube Data API v3 — GitHub Actions가 목요일 09:00 KST에 직접 업로드 |
| 8 | 네이버클립 | 반자동 | 숏츠 9:16 mp4 + `네이버클립_소개글.md` | 업로드 API 없음 — 사람이 토요일 직접 업로드 |
| - | 당근마켓 | 반자동 | 채널별 캡션 | 예약 기능 없음 — 사람이 금요일 직접 게시 |
| - | 카카오톡채널 | 반자동 | 채널별 캡션 | 사람이 금요일 직접 게시 |
| - | 네이버플레이스 | 반자동 | 채널별 캡션(제목40자/설명1000자) | 사람이 금요일 직접 게시 |

**완전자동 4채널(구글 블로그·페이스북·인스타그램·유튜브 쇼츠)** 은 이미 API 자격증명
발급이 끝났고, GitHub Actions에서 지정 시각에 직접 API를 호출해 발행한다. 사람이
Meta Business Suite나 유튜브 스튜디오에 로그인해서 예약 버튼을 누를 필요가 없다.

**반자동 채널**은 콘텐츠(원고/캡션/영상)까지만 자동으로 준비되고, 실제 게시 버튼
클릭은 항상 사람이 한다. 네이버 블로그처럼 그 플랫폼 자체에 예약발행 기능이 있으면
월요일에 사람이 한 번 예약해두는 것으로 목요일 발행이 이미 해결된다.

## 2. 주간 사이클 (자동화 반영판)

| 요일 | 할 일 |
|---|---|
| 월요일 오전 | 블로그 원고 작성 → 네이버 블로그는 사람이 자체 예약발행(목 09:00)으로 등록 |
| 월요일 11:00 | 카드뉴스·숏츠 스토리보드 + 스레드 초안 작성 (사용자 동의 후 진행) |
| 화~수요일 | 클로드코드/HyperFrames 렌더링 대기 |
| 목요일 09:00 KST | **GitHub Actions 자동 실행** → 구글 블로그·페이스북·인스타그램·유튜브 쇼츠 동시 발행. 네이버 블로그는 월요일에 걸어둔 예약이 같은 시각에 공개됨. 유튜브 커뮤니티는 사람이 이 시점에 직접 게시 |
| 금요일 | 당근마켓·카카오톡채널·네이버플레이스·스레드 — 사람이 직접 게시 |
| 토요일 | 네이버클립 — 사람이 직접 업로드 |

## 3. 콘텐츠 승인 흐름 (GitHub PR 기반)

1. 콘텐츠 생성 워크플로가 그 주 원고·이미지·카드뉴스 스토리보드·숏츠 스토리보드·
   채널별 캡션을 담은 PR을 이 저장소에 올린다 (이미지는 PR 본문/커밋에 포함되어
   브라우저에서 바로 미리보기 가능).
2. 사용자가 PR을 열어 검토 — 이미지가 부적절하면 코멘트로 재생성 요청, 문구 수정
   등을 코멘트/직접 커밋으로 처리.
3. **PR을 머지하면 = 승인 완료.** 별도 대시보드나 로그인 없이 깃허브만으로 검토가
   끝난다.
4. 목요일 09:00 KST가 되면 예약 발행 워크플로가 머지된 콘텐츠 중 그 시각이 된 것만
   골라 완전자동 4채널에 발행한다.
5. 렌더링(카드뉴스 PNG, 숏츠 mp4)은 사용자가 별도 클로드코드/HyperFrames 프로젝트에서
   진행하므로, 렌더링 완료 파일이 돌아오면 그걸 다시 커밋해 PR을 갱신하거나 새 커밋으로
   추가한다.

## 4. 자격증명 (GitHub Actions Secrets로만 관리 — 이 저장소에 값 자체를 커밋하지 않음)

| Secret 이름(제안) | 용도 | 비고 |
|---|---|---|
| `GEMINI_API_KEY` | 블로그 이미지 자동 생성 | Google AI Studio 발급 |
| `GOOGLE_OAUTH_CLIENT_ID` | Blogger/YouTube 인증 | 웹 애플리케이션 타입 OAuth 클라이언트 |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Blogger/YouTube 인증 | 위 클라이언트의 시크릿 |
| `GOOGLE_OAUTH_REFRESH_TOKEN` | Blogger/YouTube 인증 | 만료 없음(프로덕션 게시 상태 확인됨) |
| `BLOGGER_BLOG_ID` | 어느 Blogger 블로그에 올릴지 | 첫 발행 전에 Blogger API로 조회해 채워넣기 |
| `META_APP_ID` / `META_APP_SECRET` | Instagram 토큰 자동 갱신용 | blogTOsns_nineplus 앱 |
| `FACEBOOK_PAGE_ID` | 페이스북 페이지 게시 대상 | 1265899359934473 (나인플러스수학학원) |
| `FACEBOOK_PAGE_ACCESS_TOKEN` | 페이스북 페이지 게시 | 만료 없음(Page 토큰) — 그래도 주기적으로 debug_token으로 유효성 점검 권장 |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | 인스타그램 게시 대상 | 27167215579620807 (nineplus_math) |
| `INSTAGRAM_ACCESS_TOKEN` | 인스타그램 게시 | 60일 만료 — 자동 갱신 로직 필요(아래 5절) |
| `YOUTUBE_CHANNEL_ID` | 업로드 대상 채널 확인용 | 선택사항, 업로드 자체엔 OAuth 토큰이면 충분 |

## 5. 인스타그램 토큰 자동 갱신

인스타그램 액세스 토큰은 60일 후 만료된다. 완전 무인 운영을 위해 발행 워크플로
실행 시마다(또는 별도 주간 스케줄) 다음을 수행하는 갱신 스텝을 둔다.

```
GET https://graph.instagram.com/refresh_access_token
    ?grant_type=ig_refresh_token
    &access_token={현재 INSTAGRAM_ACCESS_TOKEN}
```

응답으로 받은 새 토큰을 GitHub Secrets에 다시 저장해야 하는데, Actions는 자기
자신의 Secret을 직접 덮어쓸 수 없으므로 GitHub API(저장소 관리자 권한의 PAT 또는
GitHub App)를 통해 `INSTAGRAM_ACCESS_TOKEN` 시크릿을 갱신하는 별도 스텝이 필요하다.
(구현 시 `actions/github-script` + `libsodium` 암호화로 Secrets API 호출)

## 6. 스레드(Threads) — 향후 완전자동 전환 메모

Threads API는 같은 Meta 앱 안에서 Facebook 로그인/페이지 관리 이용 사례와 함께 쓸 수
없다(Meta 앱 생성 시 확인된 제약). 나중에 스레드 콘텐츠 전략이 확정되면:

1. 새 Meta 앱을 별도로 생성(예: `threads_nineplus`)
2. 이용 사례에서 "Threads API 액세스"만 선택
3. Threads 계정을 테스터로 연결해 액세스 토큰 발급
4. 같은 GitHub Actions 구조에 5번째 완전자동 채널로 추가

그 전까지는 [content-playbook.md](content-playbook.md) 9절 규칙대로 사람이 금요일에
직접 게시한다.
