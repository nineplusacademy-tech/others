# sns_analysis_team — 검색순위·SNS 인사이트 추적 로그

나인플러스학원 네이버 블로그(블로그탭·통합검색)·네이버 플레이스 검색순위를 매주
점검한 기록. **목표는 6개 학교(동성중·산남중·동수원중·유신고·창현고·광교고) 관련
키워드에서 블로그·플레이스 둘 다 상위권을 차지하는 것**이다.
[sns_analysis_team 스킬](../.claude/skills/sns_analysis_team/SKILL.md)이 매주 토요일
13:00 브리핑 시 갱신하며, 기존 행은 지우지 않고 아래에 이어 붙인다.

**"Meta(인스타·페이스북) 인사이트 자동 조회" 섹션(2026-09-12 신설)**은 검색순위와
무관한 참여도(reach·좋아요·댓글·저장·공유) 지표다 — `.github/workflows/insights.yml`이
매주 토요일 12:00 KST에 자동으로 append하며(`publishing-plan.md` §7), 사람이 직접
쓰는 순위 추이·실행 이력과는 성격이 다르니 섞어서 비교하지 않는다.

## 순위 추이

| 점검일 | 키워드 | 블로그탭 | 통합검색 | 플레이스 | 비고 |
|---|---|---|---|---|---|
| 2026-09-12 | 우만동 수학학원 | 1위 | 7위 | 미점검 | 기준선 |
| 2026-09-12 | 동수원중 수학학원 | 2위 | 4위 | 미점검 | 기준선 |
| 2026-09-12 | 수원 수학학원 | 8위 | 노출 안 됨(30위 밖) | 미점검 | 넓은 키워드, 경쟁 심함 — 기준선 |
| 2026-09-12 | 동성중수학학원 | 미점검 | 미점검 | 8위 | 기준선 |
| 2026-09-12 | 창현고수학학원 | 미점검 | 미점검 | 순위권 밖(10위 밖, 301개 중) | 사용자 실기기 확인으로 일치 검증됨. 기준선 |
| 2026-09-12 | 유신고수학학원 | 미점검 | 미점검 | 순위권 밖(10위 밖, 323개 중) | 사용자 실기기 확인으로 일치 검증됨. 기준선 |
| 2026-09-12 | 동성중수학학원 | 2위 | 4위 | (플레이스 8위, 상동) | 2회차 — 블로그 SERP 신규 점검 |
| 2026-09-12 | 우만동수학학원 | (블로그 1위, 상동) | (블로그 7위, 상동) | 7위(155개 중) | 2회차 — 플레이스 신규 점검 |
| 2026-09-12 | 동수원중수학학원 | (블로그 2위, 상동) | (블로그 4위, 상동) | 순위권 밖(10위 밖, 485개 중, 전부 광교·매탄 지역) | 2회차 — 플레이스 신규 점검. **블로그는 강한데 플레이스는 약함** |
| 2026-09-12 | 수원수학학원 | (블로그 8위, 상동) | (블로그 노출 안 됨, 상동) | 순위권 밖(10위 밖, 1749개 중) | 2회차 — 플레이스 신규 점검, 예상대로 광범위 키워드라 밖 |

## 실행 이력

### 2026-09-12 — 기준선(baseline) 진단

- **관측**: 방문수 최근 30일 968회(직전 30일 238회 대비 +306%)이지만 9/2 하루
  221회 스파이크가 전체의 23%를 차지하는 착시 — 그 하루를 빼면 최근 추세는 오히려
  8월 평시보다 낮음(9/10~9/12 일 5~8회). 체류시간 최근 30일 평균 134.3초, 직전
  30일(202.2초) 대비 -33.6%.
- **가능한 설명**: 창현고·유신고는 학교 자체는 우만동 소재지만 수원 2학군(수원
  남부) 평준화 배정 대상이라 광교신도시 학생도 다수 배정받음 — 광교 지역 학원들이
  이 키워드를 오래 공략해온 것으로 추정. 리뷰 수는 창현고·유신고 플레이스 상위
  10곳 대부분(19~173건)이 나인플러스(8건)보다 많았지만, 동성중 키워드에서는
  리뷰 수와 순위가 무관한 사례(리뷰 1건인데 2위)가 확인되어 **리뷰 수를 단독
  원인으로 볼 수 없음**.
- **추천**: 예비 풀에 "P23. 창현고·유신고 배정 학생 실제 후기" 소재를 추가 제안 →
  사용자 승인, `docs/blog-calendar.md` 홍보형(P) 잔여 목록에 반영 완료(2026-09-12).
  순서 확정(언제 실제로 편성할지)은 아직 미정 — 다음 홍보형 차례 브리핑에서
  기존 P16~P22와 함께 검토 예정.
- **데이터 한계**: 유입 검색어·인기글 표본이 하루 5~9건 수준으로 매우 작음. 블로그
  SERP(동성중)·플레이스(우만동·동수원중·수원)는 이번 회차에 점검하지 않음 — 다음
  실행 시 우선 점검 대상.

### 2026-09-12 (같은 날, 2회차) — 8주차 브리핑 대비 확장 점검

- **관측**: 미점검이었던 4개 키워드를 마저 확인. **블로그(블로그탭·통합검색)는
  6개 키워드 전부 1~8위로 강세**인데, **플레이스는 동성중(8위)·우만동(7위) 둘만
  순위권이고 동수원중·창현고·유신고 3곳은 전부 10위 밖**으로 확인됨 — 플랫폼별
  격차가 뚜렷함. 특히 동수원중은 블로그 2위(강함)인데 플레이스는 485개 중 10위
  밖(약함)이라는 정반대 결과가 나와, 두 검색 영역이 서로 다른 신호로 움직인다는 걸
  보여줌. 동수원중 플레이스 상위 10곳도 창현고·유신고 때와 마찬가지로 전부
  광교·매탄 지역 학원.
- **가능한 설명**: 표본은 3개뿐이지만, "학교 자체는 우만동 인근이어도 그 학교
  학군이 광교·매탄까지 넓게 걸쳐 있으면 플레이스에서 광교 학원들에 밀린다"는
  패턴이 창현고·유신고에 이어 동수원중에서도 반복됨 — 다만 동수원중이 실제로
  그런 배정 구조인지는 아직 별도 확인 안 됨(추가 확인 필요).
- **추천**: **8주차(9/15) 예정 주제 P8("6등급이 3등급 된 비결")은 그대로 진행을
  추천** — 플레이스 약점과 직접 충돌하지 않고, 실제 학생 후기 콘텐츠(P23류)는
  섭외가 필요해 오늘 바로 대체하기엔 촉박함. 대신 **다음 홍보형 차례(10주차,
  9/29)에 P23을 우선 배치하고, 대상 범위를 창현고·유신고뿐 아니라 동수원중까지
  넓히는 걸 검토**하자고 제안 — 플레이스 약점 3곳을 한 콘텐츠로 같이 겨냥할 수
  있음. 최종 확정은 사용자 승인 필요(범위 확대 여부 포함).
- **데이터 한계**: 동수원중의 실제 학군 배정 구조(창현고·유신고처럼 광교 학생도
  다니는지)는 아직 확인 안 됨 — 확인되면 이 추천의 근거가 더 명확해짐.

### 2026-09-12 — Meta(인스타·페이스북) 인사이트 자동 조회

- 인스타그램 계정: 팔로워 99, 게시물 수 63
  - 계정 인사이트: reach=2
  - [VIDEO] 2026-09-10 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 계획 채우' → 400 Bad Request for url: https://graph.instagram.com/18407674150083499/insights?metric=reach%2Clikes%2Ccomments%2Csaved%2Cshares%2Cplays&access_token=IGAAg2hFBn2CdBZAGE0cnc5M3ZA2TUpialo1LXAxTFBLMjdfRzNOYkJFSUdrVmp6ampIRDBmaFBYTVNTc0VQRU1xX29CZADZAHZAlZAjeG1JY1ZAIZAHRyUUUwcXRKbGxGeTRJblZAieWY1ZATh2VF9jUzZA3QnNHLWJCOHI3NkFVREVhVGxNNAZDZD — 응답 본문: {'error': {'message': 'metric[5] must be one of the following values: impressions, shares, comments, likes, saved, replies, total_interactions, navigation, follows, profile_visits, profile_activity, reach, ig_reels_video_view_total_time, ig_reels_avg_watch_time, views, thread_replies, reposts, quotes, thread_shares, threads_views, threads_media_clicks, reels_skip_rate, threads_reposts, facebook_views, crossposted_views, total_views, total_likes, total_comments, link_clicks', 'type': 'IGApiException', 'code': 100, 'fbtrace_id': 'A50MlTVcfqgcsv4x5wyeuA5'}} (https://www.instagram.com/reel/DdHGfMflGvP/)
  - [CAROUSEL_ALBUM] 2026-09-09 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 🤔  다들' → reach=27, likes=0, comments=1, saved=0, shares=0 (https://www.instagram.com/p/DdEOirDlpNC/)
  - [VIDEO] 2026-09-04 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → 400 Bad Request for url: https://graph.instagram.com/17998244126796206/insights?metric=reach%2Clikes%2Ccomments%2Csaved%2Cshares%2Cplays&access_token=IGAAg2hFBn2CdBZAGE0cnc5M3ZA2TUpialo1LXAxTFBLMjdfRzNOYkJFSUdrVmp6ampIRDBmaFBYTVNTc0VQRU1xX29CZADZAHZAlZAjeG1JY1ZAIZAHRyUUUwcXRKbGxGeTRJblZAieWY1ZATh2VF9jUzZA3QnNHLWJCOHI3NkFVREVhVGxNNAZDZD — 응답 본문: {'error': {'message': 'metric[5] must be one of the following values: impressions, shares, comments, likes, saved, replies, total_interactions, navigation, follows, profile_visits, profile_activity, reach, ig_reels_video_view_total_time, ig_reels_avg_watch_time, views, thread_replies, reposts, quotes, thread_shares, threads_views, threads_media_clicks, reels_skip_rate, threads_reposts, facebook_views, crossposted_views, total_views, total_likes, total_comments, link_clicks', 'type': 'IGApiException', 'code': 100, 'fbtrace_id': 'AUS8BiaF_HAxJTx04elhk2b'}} (https://www.instagram.com/reel/Dc2KE6niQEJ/)
  - [CAROUSEL_ALBUM] 2026-09-03 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → reach=28, likes=2, comments=0, saved=1, shares=1 (https://www.instagram.com/p/Dc0Gfnun9nA/)
  - [VIDEO] 2026-08-31 '"필기는 했는데 시험만 보면 기억이 안 나요" 🙋\u200d♂️' → 400 Bad Request for url: https://graph.instagram.com/17987610351057463/insights?metric=reach%2Clikes%2Ccomments%2Csaved%2Cshares%2Cplays&access_token=IGAAg2hFBn2CdBZAGE0cnc5M3ZA2TUpialo1LXAxTFBLMjdfRzNOYkJFSUdrVmp6ampIRDBmaFBYTVNTc0VQRU1xX29CZADZAHZAlZAjeG1JY1ZAIZAHRyUUUwcXRKbGxGeTRJblZAieWY1ZATh2VF9jUzZA3QnNHLWJCOHI3NkFVREVhVGxNNAZDZD — 응답 본문: {'error': {'message': 'metric[5] must be one of the following values: impressions, shares, comments, likes, saved, replies, total_interactions, navigation, follows, profile_visits, profile_activity, reach, ig_reels_video_view_total_time, ig_reels_avg_watch_time, views, thread_replies, reposts, quotes, thread_shares, threads_views, threads_media_clicks, reels_skip_rate, threads_reposts, facebook_views, crossposted_views, total_views, total_likes, total_comments, link_clicks', 'type': 'IGApiException', 'code': 100, 'fbtrace_id': 'AsJjB0NxagNDtDeRrXRqlRW'}} (https://www.instagram.com/reel/Dcs-l6uDXin/)
- 페이스북 페이지: 팔로워 13
  - 페이지 인사이트 조회 실패: 400 Bad Request for url: https://graph.facebook.com/v21.0/1265899359934473/insights?metric=page_impressions%2Cpage_engaged_users&period=week&access_token=EAAPQQCo8q38BSZAvMFidS4rSSNeeTVt0hoFEixoOqxfJPPt39kY0bjASj8lLQmabT71I2WUQHbFQOwIeojJgVWhnxRQAKcqQWZBCOW8P4S0E6M3mFL2ACmUBfpFE3983Gje0ZBqdLqpnrodcTJbKBLtawMcjbKQpYDJ01Y55BAe8qyQgLv82bn74wzn50A9JnVz — 응답 본문: {'error': {'message': '(#100) The value must be a valid insights metric', 'type': 'OAuthException', 'code': 100, 'fbtrace_id': 'ATDYBAykX-bFFmP_Hu0Ud6e'}}
  - [게시글] 2026-09-10 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 계획 채우' → 400 Bad Request for url: https://graph.facebook.com/v21.0/1265899359934473_122114755119424939/insights?metric=post_impressions%2Cpost_engaged_users%2Cpost_reactions_by_type_total&access_token=EAAPQQCo8q38BSZAvMFidS4rSSNeeTVt0hoFEixoOqxfJPPt39kY0bjASj8lLQmabT71I2WUQHbFQOwIeojJgVWhnxRQAKcqQWZBCOW8P4S0E6M3mFL2ACmUBfpFE3983Gje0ZBqdLqpnrodcTJbKBLtawMcjbKQpYDJ01Y55BAe8qyQgLv82bn74wzn50A9JnVz — 응답 본문: {'error': {'message': '(#100) The value must be a valid insights metric', 'type': 'OAuthException', 'code': 100, 'fbtrace_id': 'AN-CJ3YMJwh8zqa4cJMlfAP'}} (https://www.facebook.com/reel/1423279913202551/)
  - [게시글] 2026-09-09 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 🤔  계획' → 400 Bad Request for url: https://graph.facebook.com/v21.0/1265899359934473_122114524905424939/insights?metric=post_impressions%2Cpost_engaged_users%2Cpost_reactions_by_type_total&access_token=EAAPQQCo8q38BSZAvMFidS4rSSNeeTVt0hoFEixoOqxfJPPt39kY0bjASj8lLQmabT71I2WUQHbFQOwIeojJgVWhnxRQAKcqQWZBCOW8P4S0E6M3mFL2ACmUBfpFE3983Gje0ZBqdLqpnrodcTJbKBLtawMcjbKQpYDJ01Y55BAe8qyQgLv82bn74wzn50A9JnVz — 응답 본문: {'error': {'message': '(#100) The value must be a valid insights metric', 'type': 'OAuthException', 'code': 100, 'fbtrace_id': 'A1mSqHRiVNkEsFbBgcgX91Y'}} (https://www.facebook.com/122115070323424939/posts/122114524905424939)
  - [게시글] 2026-09-04 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → 400 Bad Request for url: https://graph.facebook.com/v21.0/1265899359934473_122113287171424939/insights?metric=post_impressions%2Cpost_engaged_users%2Cpost_reactions_by_type_total&access_token=EAAPQQCo8q38BSZAvMFidS4rSSNeeTVt0hoFEixoOqxfJPPt39kY0bjASj8lLQmabT71I2WUQHbFQOwIeojJgVWhnxRQAKcqQWZBCOW8P4S0E6M3mFL2ACmUBfpFE3983Gje0ZBqdLqpnrodcTJbKBLtawMcjbKQpYDJ01Y55BAe8qyQgLv82bn74wzn50A9JnVz — 응답 본문: {'error': {'message': '(#100) The value must be a valid insights metric', 'type': 'OAuthException', 'code': 100, 'fbtrace_id': 'AO6MC3lb2kYS7xqU-v_c4Qo'}} (https://www.facebook.com/reel/2534315827035432/)
  - [게시글] 2026-09-03 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → 400 Bad Request for url: https://graph.facebook.com/v21.0/1265899359934473_122113120029424939/insights?metric=post_impressions%2Cpost_engaged_users%2Cpost_reactions_by_type_total&access_token=EAAPQQCo8q38BSZAvMFidS4rSSNeeTVt0hoFEixoOqxfJPPt39kY0bjASj8lLQmabT71I2WUQHbFQOwIeojJgVWhnxRQAKcqQWZBCOW8P4S0E6M3mFL2ACmUBfpFE3983Gje0ZBqdLqpnrodcTJbKBLtawMcjbKQpYDJ01Y55BAe8qyQgLv82bn74wzn50A9JnVz — 응답 본문: {'error': {'message': '(#100) The value must be a valid insights metric', 'type': 'OAuthException', 'code': 100, 'fbtrace_id': 'AgCX3z2rt9HPipdNvjbXunK'}} (https://www.facebook.com/122115070323424939/posts/122113120029424939)
  - [게시글] 2026-08-31 '같은 수업을 들어도 성적이 갈리는 이유, "노트 정리 ' → 400 Bad Request for url: https://graph.facebook.com/v21.0/1265899359934473_122112527043424939/insights?metric=post_impressions%2Cpost_engaged_users%2Cpost_reactions_by_type_total&access_token=EAAPQQCo8q38BSZAvMFidS4rSSNeeTVt0hoFEixoOqxfJPPt39kY0bjASj8lLQmabT71I2WUQHbFQOwIeojJgVWhnxRQAKcqQWZBCOW8P4S0E6M3mFL2ACmUBfpFE3983Gje0ZBqdLqpnrodcTJbKBLtawMcjbKQpYDJ01Y55BAe8qyQgLv82bn74wzn50A9JnVz — 응답 본문: {'error': {'message': '(#100) The value must be a valid insights metric', 'type': 'OAuthException', 'code': 100, 'fbtrace_id': 'A9aSHrxwVyBY6_FRwfBLELS'}} (https://www.facebook.com/reel/1478134887701342/)
  - [릴스/영상] 2026-09-10 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 계획 채우' → 403 Forbidden for url: https://graph.facebook.com/v21.0/1423279913202551/video_insights?metric=total_video_views%2Ctotal_video_impressions%2Ctotal_video_avg_time_watched&access_token=EAAPQQCo8q38BSZAvMFidS4rSSNeeTVt0hoFEixoOqxfJPPt39kY0bjASj8lLQmabT71I2WUQHbFQOwIeojJgVWhnxRQAKcqQWZBCOW8P4S0E6M3mFL2ACmUBfpFE3983Gje0ZBqdLqpnrodcTJbKBLtawMcjbKQpYDJ01Y55BAe8qyQgLv82bn74wzn50A9JnVz — 응답 본문: {'error': {'message': '(#200) read_insights permission missing (https://developers.facebook.com/docs/permissions/reference/read_insights)', 'type': 'OAuthException', 'code': 200, 'fbtrace_id': 'AO5mRCvEh4xmkXUZ8IUCvfO'}} (/reel/1423279913202551/)
  - [릴스/영상] 2026-09-04 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → 403 Forbidden for url: https://graph.facebook.com/v21.0/2534315827035432/video_insights?metric=total_video_views%2Ctotal_video_impressions%2Ctotal_video_avg_time_watched&access_token=EAAPQQCo8q38BSZAvMFidS4rSSNeeTVt0hoFEixoOqxfJPPt39kY0bjASj8lLQmabT71I2WUQHbFQOwIeojJgVWhnxRQAKcqQWZBCOW8P4S0E6M3mFL2ACmUBfpFE3983Gje0ZBqdLqpnrodcTJbKBLtawMcjbKQpYDJ01Y55BAe8qyQgLv82bn74wzn50A9JnVz — 응답 본문: {'error': {'message': '(#200) read_insights permission missing (https://developers.facebook.com/docs/permissions/reference/read_insights)', 'type': 'OAuthException', 'code': 200, 'fbtrace_id': 'A4oKtFzCViDPfoPRdc9CHS8'}} (/reel/2534315827035432/)
  - [릴스/영상] 2026-09-01 '' → 403 Forbidden for url: https://graph.facebook.com/v21.0/1785021425985952/video_insights?metric=total_video_views%2Ctotal_video_impressions%2Ctotal_video_avg_time_watched&access_token=EAAPQQCo8q38BSZAvMFidS4rSSNeeTVt0hoFEixoOqxfJPPt39kY0bjASj8lLQmabT71I2WUQHbFQOwIeojJgVWhnxRQAKcqQWZBCOW8P4S0E6M3mFL2ACmUBfpFE3983Gje0ZBqdLqpnrodcTJbKBLtawMcjbKQpYDJ01Y55BAe8qyQgLv82bn74wzn50A9JnVz — 응답 본문: {'error': {'message': '(#200) read_insights permission missing (https://developers.facebook.com/docs/permissions/reference/read_insights)', 'type': 'OAuthException', 'code': 200, 'fbtrace_id': 'AXd-B0gNnKIHxU7_iGDcWiu'}} (/122115070323424939/videos/1785021425985952)
  - [릴스/영상] 2026-08-31 '' → 403 Forbidden for url: https://graph.facebook.com/v21.0/4729289450632589/video_insights?metric=total_video_views%2Ctotal_video_impressions%2Ctotal_video_avg_time_watched&access_token=EAAPQQCo8q38BSZAvMFidS4rSSNeeTVt0hoFEixoOqxfJPPt39kY0bjASj8lLQmabT71I2WUQHbFQOwIeojJgVWhnxRQAKcqQWZBCOW8P4S0E6M3mFL2ACmUBfpFE3983Gje0ZBqdLqpnrodcTJbKBLtawMcjbKQpYDJ01Y55BAe8qyQgLv82bn74wzn50A9JnVz — 응답 본문: {'error': {'message': '(#200) read_insights permission missing (https://developers.facebook.com/docs/permissions/reference/read_insights)', 'type': 'OAuthException', 'code': 200, 'fbtrace_id': 'AwygFKF9KqIQ21yBHycqktL'}} (/122115070323424939/videos/4729289450632589)
  - [릴스/영상] 2026-08-31 '' → 403 Forbidden for url: https://graph.facebook.com/v21.0/1732426651206801/video_insights?metric=total_video_views%2Ctotal_video_impressions%2Ctotal_video_avg_time_watched&access_token=EAAPQQCo8q38BSZAvMFidS4rSSNeeTVt0hoFEixoOqxfJPPt39kY0bjASj8lLQmabT71I2WUQHbFQOwIeojJgVWhnxRQAKcqQWZBCOW8P4S0E6M3mFL2ACmUBfpFE3983Gje0ZBqdLqpnrodcTJbKBLtawMcjbKQpYDJ01Y55BAe8qyQgLv82bn74wzn50A9JnVz — 응답 본문: {'error': {'message': '(#200) read_insights permission missing (https://developers.facebook.com/docs/permissions/reference/read_insights)', 'type': 'OAuthException', 'code': 200, 'fbtrace_id': 'A2fEyZ6Etw2pWBRofPzEfDO'}} (/122115070323424939/videos/1732426651206801)

### 2026-09-12 — Meta(인스타·페이스북) 인사이트 자동 조회

- 인스타그램 계정: 팔로워 99, 게시물 수 63
  - 계정 인사이트: reach=0
  - [VIDEO] 2026-09-10 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 계획 채우' → reach=30, likes=1, comments=0, saved=1, shares=0, views=39 (https://www.instagram.com/reel/DdHGfMflGvP/)
  - [CAROUSEL_ALBUM] 2026-09-09 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 🤔  다들' → reach=27, likes=0, comments=1, saved=0, shares=0 (https://www.instagram.com/p/DdEOirDlpNC/)
  - [VIDEO] 2026-09-04 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → reach=149, likes=2, comments=1, saved=1, shares=0, views=170 (https://www.instagram.com/reel/Dc2KE6niQEJ/)
  - [CAROUSEL_ALBUM] 2026-09-03 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → reach=28, likes=2, comments=0, saved=1, shares=1 (https://www.instagram.com/p/Dc0Gfnun9nA/)
  - [VIDEO] 2026-08-31 '"필기는 했는데 시험만 보면 기억이 안 나요" 🙋\u200d♂️' → reach=133, likes=3, comments=1, saved=2, shares=0, views=193 (https://www.instagram.com/reel/Dcs-l6uDXin/)
- 페이스북 페이지: 팔로워 13
  - 페이지 인사이트: 실패: page_engaged_users(400 Bad Request for url: https://graph.facebook.com/v21.0/1265899359934473/insights?metric=page_enga…)
  - [게시글] 2026-09-10 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 계획 채우' → 실패: post_engaged_users(400 Bad Request for url: https://graph.facebook.com/v21.0/1265899359934473_122114755119424939/insigh…) (https://www.facebook.com/reel/1423279913202551/)
  - [게시글] 2026-09-09 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 🤔  계획' → 실패: post_engaged_users(400 Bad Request for url: https://graph.facebook.com/v21.0/1265899359934473_122114524905424939/insigh…) (https://www.facebook.com/122115070323424939/posts/122114524905424939)
  - [게시글] 2026-09-04 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → 실패: post_engaged_users(400 Bad Request for url: https://graph.facebook.com/v21.0/1265899359934473_122113287171424939/insigh…) (https://www.facebook.com/reel/2534315827035432/)
  - [게시글] 2026-09-03 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → 실패: post_engaged_users(400 Bad Request for url: https://graph.facebook.com/v21.0/1265899359934473_122113120029424939/insigh…) (https://www.facebook.com/122115070323424939/posts/122113120029424939)
  - [게시글] 2026-08-31 '같은 수업을 들어도 성적이 갈리는 이유, "노트 정리 ' → 실패: post_engaged_users(400 Bad Request for url: https://graph.facebook.com/v21.0/1265899359934473_122112527043424939/insigh…) (https://www.facebook.com/reel/1478134887701342/)
  - [릴스/영상] 2026-09-10 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 계획 채우' → 실패: total_video_views(403 Forbidden for url: https://graph.facebook.com/v21.0/1423279913202551/video_insights?metric=total…), total_video_impressions(403 Forbidden for url: https://graph.facebook.com/v21.0/1423279913202551/video_insights?metric=total…), total_video_avg_time_watched(403 Forbidden for url: https://graph.facebook.com/v21.0/1423279913202551/video_insights?metric=total…) (/reel/1423279913202551/)
  - [릴스/영상] 2026-09-04 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → 실패: total_video_views(403 Forbidden for url: https://graph.facebook.com/v21.0/2534315827035432/video_insights?metric=total…), total_video_impressions(403 Forbidden for url: https://graph.facebook.com/v21.0/2534315827035432/video_insights?metric=total…), total_video_avg_time_watched(403 Forbidden for url: https://graph.facebook.com/v21.0/2534315827035432/video_insights?metric=total…) (/reel/2534315827035432/)
  - [릴스/영상] 2026-09-01 '' → 실패: total_video_views(403 Forbidden for url: https://graph.facebook.com/v21.0/1785021425985952/video_insights?metric=total…), total_video_impressions(403 Forbidden for url: https://graph.facebook.com/v21.0/1785021425985952/video_insights?metric=total…), total_video_avg_time_watched(403 Forbidden for url: https://graph.facebook.com/v21.0/1785021425985952/video_insights?metric=total…) (/122115070323424939/videos/1785021425985952)
  - [릴스/영상] 2026-08-31 '' → 실패: total_video_views(403 Forbidden for url: https://graph.facebook.com/v21.0/4729289450632589/video_insights?metric=total…), total_video_impressions(403 Forbidden for url: https://graph.facebook.com/v21.0/4729289450632589/video_insights?metric=total…), total_video_avg_time_watched(403 Forbidden for url: https://graph.facebook.com/v21.0/4729289450632589/video_insights?metric=total…) (/122115070323424939/videos/4729289450632589)
  - [릴스/영상] 2026-08-31 '' → 실패: total_video_views(403 Forbidden for url: https://graph.facebook.com/v21.0/1732426651206801/video_insights?metric=total…), total_video_impressions(403 Forbidden for url: https://graph.facebook.com/v21.0/1732426651206801/video_insights?metric=total…), total_video_avg_time_watched(403 Forbidden for url: https://graph.facebook.com/v21.0/1732426651206801/video_insights?metric=total…) (/122115070323424939/videos/1732426651206801)

### 2026-09-12 — Meta(인스타·페이스북) 인사이트 자동 조회

- 인스타그램 계정: 팔로워 99, 게시물 수 63
  - 계정 인사이트: reach=0
  - [VIDEO] 2026-09-10 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 계획 채우' → reach=30, likes=1, comments=0, saved=1, shares=0, views=39 (https://www.instagram.com/reel/DdHGfMflGvP/)
  - [CAROUSEL_ALBUM] 2026-09-09 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 🤔  다들' → reach=27, likes=0, comments=1, saved=0, shares=0 (https://www.instagram.com/p/DdEOirDlpNC/)
  - [VIDEO] 2026-09-04 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → reach=149, likes=2, comments=1, saved=1, shares=0, views=170 (https://www.instagram.com/reel/Dc2KE6niQEJ/)
  - [CAROUSEL_ALBUM] 2026-09-03 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → reach=28, likes=2, comments=0, saved=1, shares=1 (https://www.instagram.com/p/Dc0Gfnun9nA/)
  - [VIDEO] 2026-08-31 '"필기는 했는데 시험만 보면 기억이 안 나요" 🙋\u200d♂️' → reach=133, likes=3, comments=1, saved=2, shares=0, views=193 (https://www.instagram.com/reel/Dcs-l6uDXin/)
- 페이스북 페이지: 팔로워 13
  - 페이지 인사이트: (값 없음)
  - [게시글] 2026-09-10 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 계획 채우' → (값 없음) (https://www.facebook.com/reel/1423279913202551/)
  - [게시글] 2026-09-09 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 🤔  계획' → (값 없음) (https://www.facebook.com/122115070323424939/posts/122114524905424939)
  - [게시글] 2026-09-04 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → (값 없음) (https://www.facebook.com/reel/2534315827035432/)
  - [게시글] 2026-09-03 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → (값 없음) (https://www.facebook.com/122115070323424939/posts/122113120029424939)
  - [게시글] 2026-08-31 '같은 수업을 들어도 성적이 갈리는 이유, "노트 정리 ' → (값 없음) (https://www.facebook.com/reel/1478134887701342/)
  - [릴스/영상] 2026-09-10 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 계획 채우' → 실패: total_video_views(403 Forbidden for url: https://graph.facebook.com/v21.0/1423279913202551/video_insights?metric=total…), total_video_impressions(403 Forbidden for url: https://graph.facebook.com/v21.0/1423279913202551/video_insights?metric=total…), total_video_avg_time_watched(403 Forbidden for url: https://graph.facebook.com/v21.0/1423279913202551/video_insights?metric=total…) (/reel/1423279913202551/)
  - [릴스/영상] 2026-09-04 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → 실패: total_video_views(403 Forbidden for url: https://graph.facebook.com/v21.0/2534315827035432/video_insights?metric=total…), total_video_impressions(403 Forbidden for url: https://graph.facebook.com/v21.0/2534315827035432/video_insights?metric=total…), total_video_avg_time_watched(403 Forbidden for url: https://graph.facebook.com/v21.0/2534315827035432/video_insights?metric=total…) (/reel/2534315827035432/)
  - [릴스/영상] 2026-09-01 '' → 실패: total_video_views(403 Forbidden for url: https://graph.facebook.com/v21.0/1785021425985952/video_insights?metric=total…), total_video_impressions(403 Forbidden for url: https://graph.facebook.com/v21.0/1785021425985952/video_insights?metric=total…), total_video_avg_time_watched(403 Forbidden for url: https://graph.facebook.com/v21.0/1785021425985952/video_insights?metric=total…) (/122115070323424939/videos/1785021425985952)
  - [릴스/영상] 2026-08-31 '' → 실패: total_video_views(403 Forbidden for url: https://graph.facebook.com/v21.0/4729289450632589/video_insights?metric=total…), total_video_impressions(403 Forbidden for url: https://graph.facebook.com/v21.0/4729289450632589/video_insights?metric=total…), total_video_avg_time_watched(403 Forbidden for url: https://graph.facebook.com/v21.0/4729289450632589/video_insights?metric=total…) (/122115070323424939/videos/4729289450632589)
  - [릴스/영상] 2026-08-31 '' → 실패: total_video_views(403 Forbidden for url: https://graph.facebook.com/v21.0/1732426651206801/video_insights?metric=total…), total_video_impressions(403 Forbidden for url: https://graph.facebook.com/v21.0/1732426651206801/video_insights?metric=total…), total_video_avg_time_watched(403 Forbidden for url: https://graph.facebook.com/v21.0/1732426651206801/video_insights?metric=total…) (/122115070323424939/videos/1732426651206801)

### 2026-09-12 — Meta(인스타·페이스북) 인사이트 자동 조회

- 인스타그램 계정: 팔로워 99, 게시물 수 63
  - 계정 인사이트: reach=0
  - [VIDEO] 2026-09-10 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 계획 채우' → reach=30, likes=1, comments=0, saved=1, shares=0, views=39 (https://www.instagram.com/reel/DdHGfMflGvP/)
  - [CAROUSEL_ALBUM] 2026-09-09 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 🤔  다들' → reach=27, likes=0, comments=1, saved=0, shares=0 (https://www.instagram.com/p/DdEOirDlpNC/)
  - [VIDEO] 2026-09-04 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → reach=149, likes=2, comments=1, saved=1, shares=0, views=170 (https://www.instagram.com/reel/Dc2KE6niQEJ/)
  - [CAROUSEL_ALBUM] 2026-09-03 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → reach=28, likes=2, comments=0, saved=1, shares=1 (https://www.instagram.com/p/Dc0Gfnun9nA/)
  - [VIDEO] 2026-08-31 '"필기는 했는데 시험만 보면 기억이 안 나요" 🙋\u200d♂️' → reach=133, likes=3, comments=1, saved=2, shares=0, views=193 (https://www.instagram.com/reel/Dcs-l6uDXin/)
- 페이스북 페이지: 팔로워 13
  - 페이지 인사이트: page_follows=13, page_media_view=99
  - [게시글] 2026-09-10 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 계획 채우' → post_media_view=13, post_reactions_by_type_total={} (https://www.facebook.com/reel/1423279913202551/)
  - [게시글] 2026-09-09 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 🤔  계획' → post_media_view=16, post_reactions_by_type_total={} (https://www.facebook.com/122115070323424939/posts/122114524905424939)
  - [게시글] 2026-09-04 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → post_media_view=196, post_reactions_by_type_total={} (https://www.facebook.com/reel/2534315827035432/)
  - [게시글] 2026-09-03 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → post_media_view=6, post_reactions_by_type_total={'like': 1} (https://www.facebook.com/122115070323424939/posts/122113120029424939)
  - [게시글] 2026-08-31 '같은 수업을 들어도 성적이 갈리는 이유, "노트 정리 ' → post_media_view=230, post_reactions_by_type_total={'like': 1} (https://www.facebook.com/reel/1478134887701342/)
  - [릴스/영상] 2026-09-10 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 계획 채우' → (값 없음) (/reel/1423279913202551/)
  - [릴스/영상] 2026-09-04 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → (값 없음) (/reel/2534315827035432/)
  - [릴스/영상] 2026-09-01 '' → total_video_views=0, total_video_impressions=0, total_video_avg_time_watched=0 (/122115070323424939/videos/1785021425985952)
  - [릴스/영상] 2026-08-31 '' → total_video_views=0, total_video_impressions=0, total_video_avg_time_watched=0 (/122115070323424939/videos/4729289450632589)
  - [릴스/영상] 2026-08-31 '' → total_video_views=0, total_video_impressions=0, total_video_avg_time_watched=0 (/122115070323424939/videos/1732426651206801)

### 2026-09-12 — Meta(인스타·페이스북) 인사이트 자동 조회

- 인스타그램 계정: 팔로워 99, 게시물 수 63
  - 계정 인사이트: reach=0, accounts_engaged=None
  - [VIDEO] 2026-09-10 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 계획 채우' → reach=30, likes=1, comments=0, saved=1, shares=0, views=39 (https://www.instagram.com/reel/DdHGfMflGvP/)
  - [CAROUSEL_ALBUM] 2026-09-09 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 🤔  다들' → reach=27, likes=0, comments=1, saved=0, shares=0 (https://www.instagram.com/p/DdEOirDlpNC/)
  - [VIDEO] 2026-09-04 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → reach=149, likes=2, comments=1, saved=1, shares=0, views=170 (https://www.instagram.com/reel/Dc2KE6niQEJ/)
  - [CAROUSEL_ALBUM] 2026-09-03 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → reach=28, likes=2, comments=0, saved=1, shares=1 (https://www.instagram.com/p/Dc0Gfnun9nA/)
  - [VIDEO] 2026-08-31 '"필기는 했는데 시험만 보면 기억이 안 나요" 🙋\u200d♂️' → reach=133, likes=3, comments=1, saved=2, shares=0, views=193 (https://www.instagram.com/reel/Dcs-l6uDXin/)
- 페이스북 페이지: 팔로워 13
  - 페이지 인사이트: page_follows=13, page_media_view=99
  - [게시글] 2026-09-10 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 계획 채우' → post_media_view=13, post_reactions_by_type_total={} (https://www.facebook.com/reel/1423279913202551/)
  - [게시글] 2026-09-09 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 🤔  계획' → post_media_view=16, post_reactions_by_type_total={} (https://www.facebook.com/122115070323424939/posts/122114524905424939)
  - [게시글] 2026-09-04 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → post_media_view=196, post_reactions_by_type_total={} (https://www.facebook.com/reel/2534315827035432/)
  - [게시글] 2026-09-03 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → post_media_view=6, post_reactions_by_type_total={'like': 1} (https://www.facebook.com/122115070323424939/posts/122113120029424939)
  - [게시글] 2026-08-31 '같은 수업을 들어도 성적이 갈리는 이유, "노트 정리 ' → post_media_view=230, post_reactions_by_type_total={'like': 1} (https://www.facebook.com/reel/1478134887701342/)
  - [릴스/영상] 2026-09-10 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 계획 채우' → (값 없음) (/reel/1423279913202551/)
  - [릴스/영상] 2026-09-04 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → blue_reels_play_count=185 (/reel/2534315827035432/)
  - [릴스/영상] 2026-09-01 '' → total_video_views=0, total_video_impressions=0, total_video_avg_time_watched=0 (/122115070323424939/videos/1785021425985952)
  - [릴스/영상] 2026-08-31 '' → total_video_views=0, total_video_impressions=0, total_video_avg_time_watched=0 (/122115070323424939/videos/4729289450632589)
  - [릴스/영상] 2026-08-31 '' → total_video_views=0, total_video_impressions=0, total_video_avg_time_watched=0 (/122115070323424939/videos/1732426651206801)

### 2026-09-12 — Meta(인스타·페이스북) 인사이트 자동 조회

- 인스타그램 계정: 팔로워 99, 게시물 수 63
  - 계정 인사이트: reach=0, accounts_engaged=0
  - [VIDEO] 2026-09-10 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 계획 채우' → reach=30, likes=1, comments=0, saved=1, shares=0, views=39 (https://www.instagram.com/reel/DdHGfMflGvP/)
  - [CAROUSEL_ALBUM] 2026-09-09 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 🤔  다들' → reach=27, likes=0, comments=1, saved=0, shares=0 (https://www.instagram.com/p/DdEOirDlpNC/)
  - [VIDEO] 2026-09-04 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → reach=149, likes=2, comments=1, saved=1, shares=0, views=170 (https://www.instagram.com/reel/Dc2KE6niQEJ/)
  - [CAROUSEL_ALBUM] 2026-09-03 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → reach=28, likes=2, comments=0, saved=1, shares=1 (https://www.instagram.com/p/Dc0Gfnun9nA/)
  - [VIDEO] 2026-08-31 '"필기는 했는데 시험만 보면 기억이 안 나요" 🙋\u200d♂️' → reach=133, likes=3, comments=1, saved=2, shares=0, views=193 (https://www.instagram.com/reel/Dcs-l6uDXin/)
- 페이스북 페이지: 팔로워 13
  - 페이지 인사이트: page_follows=13, page_media_view=99
  - [게시글] 2026-09-10 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 계획 채우' → post_media_view=13, post_reactions_by_type_total={} (https://www.facebook.com/reel/1423279913202551/)
  - [게시글] 2026-09-09 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 🤔  계획' → post_media_view=16, post_reactions_by_type_total={} (https://www.facebook.com/122115070323424939/posts/122114524905424939)
  - [게시글] 2026-09-04 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → post_media_view=196, post_reactions_by_type_total={} (https://www.facebook.com/reel/2534315827035432/)
  - [게시글] 2026-09-03 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → post_media_view=6, post_reactions_by_type_total={'like': 1} (https://www.facebook.com/122115070323424939/posts/122113120029424939)
  - [게시글] 2026-08-31 '같은 수업을 들어도 성적이 갈리는 이유, "노트 정리 ' → post_media_view=230, post_reactions_by_type_total={'like': 1} (https://www.facebook.com/reel/1478134887701342/)
  - [릴스/영상] 2026-09-10 '스터디플래너, 왜 항상 작심삼일로 끝날까요? 계획 채우' → (값 없음) (/reel/1423279913202551/)
  - [릴스/영상] 2026-09-04 '우리 아이 수시 원서, 마감일까지 정확히 알고 계신가요' → blue_reels_play_count=185 (/reel/2534315827035432/)
  - [릴스/영상] 2026-09-01 '' → total_video_views=0, total_video_impressions=0, total_video_avg_time_watched=0 (/122115070323424939/videos/1785021425985952)
  - [릴스/영상] 2026-08-31 '' → total_video_views=0, total_video_impressions=0, total_video_avg_time_watched=0 (/122115070323424939/videos/4729289450632589)
  - [릴스/영상] 2026-08-31 '' → total_video_views=0, total_video_impressions=0, total_video_avg_time_watched=0 (/122115070323424939/videos/1732426651206801)
