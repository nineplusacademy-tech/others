"""insights.build_report()의 결과를 docs/sns-analysis-log.md에 마크다운으로
append한다. .github/workflows/insights.yml이 매주 토요일 12:00 KST에 실행하고
(콘텐츠 브리핑 13:00보다 먼저), 결과를 커밋한다. 기존 내용은 지우지 않고
파일 끝에 이어 붙인다 — sns-analysis-log.md의 "기존 행은 지우지 않는다" 원칙과
동일하다.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from insights import build_report

LOG_PATH = Path(__file__).resolve().parent.parent.parent / "docs" / "sns-analysis-log.md"


def _fmt_values(values: dict | None) -> str:
    if not values:
        return "(값 없음)"
    return ", ".join(f"{k}={v}" for k, v in values.items())


def _short_error(message: str, limit: int = 100) -> str:
    return message if len(message) <= limit else message[:limit] + "…"


def _fmt_insight_result(result: dict) -> str:
    """{"requested": [...], "values": {...}, "errors": {...}} 형태를 한 줄로 요약한다.

    메트릭별 개별 요청 결과라 값과 실패가 섞여 있을 수 있다 — 둘 다 보여준다
    (값이 하나도 없다고 전체가 실패한 게 아니고, 일부만 실패해도 나머지 값은
    그대로 살아있다).
    """
    parts = []
    values = result.get("values")
    if values:
        parts.append(_fmt_values(values))
    errors = result.get("errors")
    if errors:
        failed = ", ".join(f"{metric}({_short_error(msg)})" for metric, msg in errors.items())
        parts.append(f"실패: {failed}")
    if not parts:
        return "(값 없음)"
    return " | ".join(parts)


def format_section(report: dict) -> str:
    today = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
    lines = [f"\n### {today} — Meta(인스타·페이스북) 인사이트 자동 조회", ""]

    if "instagram_error" in report:
        lines.append(f"- 인스타그램 조회 실패: {report['instagram_error']}")
    else:
        acct = report.get("instagram_account", {})
        profile = acct.get("profile", {})
        if "profile_error" in acct:
            lines.append(f"- 인스타그램 계정 조회 실패: {acct['profile_error']}")
        else:
            lines.append(
                f"- 인스타그램 계정: 팔로워 {profile.get('followers_count', '?')}, "
                f"게시물 수 {profile.get('media_count', '?')}"
            )
        lines.append(f"  - 계정 인사이트: {_fmt_insight_result(acct.get('account_insights', {}))}")
        for m in report.get("instagram_media", []):
            insights = m.get("insights", {})
            status = _fmt_insight_result(insights)
            caption = (m.get("caption") or "").replace("\n", " ")[:30]
            lines.append(
                f"  - [{m.get('media_type')}] {m.get('timestamp', '')[:10]} "
                f"{caption!r} → {status} ({m.get('permalink', '')})"
            )

    if "facebook_error" in report:
        lines.append(f"- 페이스북 조회 실패: {report['facebook_error']}")
    else:
        page = report.get("facebook_page", {})
        page_info = page.get("page", {})
        if "page_error" in page:
            lines.append(f"- 페이스북 페이지 조회 실패: {page['page_error']}")
        else:
            lines.append(f"- 페이스북 페이지: 팔로워 {page_info.get('fan_count', '?')}")
        lines.append(f"  - 페이지 인사이트: {_fmt_insight_result(page.get('page_insights', {}))}")
        for p in report.get("facebook_posts", []):
            insights = p.get("insights", {})
            status = _fmt_insight_result(insights)
            message = (p.get("message") or "").replace("\n", " ")[:30]
            lines.append(
                f"  - [게시글] {p.get('created_time', '')[:10]} "
                f"{message!r} → {status} ({p.get('permalink_url', '')})"
            )
        for v in report.get("facebook_videos", []):
            insights = v.get("insights", {})
            status = _fmt_insight_result(insights)
            desc = (v.get("description") or "").replace("\n", " ")[:30]
            lines.append(
                f"  - [릴스/영상] {v.get('created_time', '')[:10]} "
                f"{desc!r} → {status} ({v.get('permalink_url', '')})"
            )

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    report = build_report(limit=5)
    section = format_section(report)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(section)
    print(section)


if __name__ == "__main__":
    main()
