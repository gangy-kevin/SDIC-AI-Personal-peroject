"""
신뢰도 점수 산출 모듈
출처 URL 존재 + fetch 본문 일치 + 신뢰 소스 해당 + 교차 출처 수
→ 0~100 점수 산출
"""
from dataclasses import dataclass, field
from src.config.settings import SCORE_WEIGHTS
from src.config.trusted_sources import is_trusted_source
from src.tools.url_fetcher import fetch_url, verify_value_in_text


@dataclass
class SourceScore:
    total: int                          # 0~100 최종 점수
    has_url: bool                       # 출처 URL 존재
    body_match: bool                    # fetch 본문 일치
    trusted_source: bool                # 신뢰 소스 해당
    cross_source_count: int             # 교차 출처 수
    breakdown: dict = field(default_factory=dict)   # 항목별 점수
    grade: str = ""                     # A/B/C/D 등급


def _calc_grade(score: int) -> str:
    if score >= 80:
        return "A"
    elif score >= 60:
        return "B"
    elif score >= 40:
        return "C"
    else:
        return "D"


def calculate_score(
    urls: list[str],
    values_to_verify: list[str] | None = None,
) -> SourceScore:
    """
    출처 URL 리스트와 검증할 수치로 신뢰도 점수 산출

    Args:
        urls: 출처 URL 리스트
        values_to_verify: 본문 존재 여부 검증할 수치/키워드 리스트

    Returns:
        SourceScore (0~100점)
    """
    # 1. 출처 URL 존재 여부
    has_url = len(urls) > 0
    url_score = SCORE_WEIGHTS["has_url"] if has_url else 0

    # 2. 신뢰 소스 필터 해당 여부
    trusted = any(is_trusted_source(u) for u in urls)
    trusted_score = SCORE_WEIGHTS["trusted_source"] if trusted else 0

    # 3. 교차 출처 수 (2개 이상이면 만점)
    cross_count = len(set(urls))
    cross_score = SCORE_WEIGHTS["cross_source"] if cross_count >= 2 else int(
        SCORE_WEIGHTS["cross_source"] * cross_count / 2
    )

    # 4. fetch 본문 일치 여부
    body_match = False
    body_score = 0
    if has_url and values_to_verify:
        for url in urls[:3]:  # 최대 3개 URL만 fetch (비용 절감)
            fetch_result = fetch_url(url)
            if not fetch_result.success:
                continue
            for value in values_to_verify:
                if verify_value_in_text(value, fetch_result.text):
                    body_match = True
                    break
            if body_match:
                break
        body_score = SCORE_WEIGHTS["body_match"] if body_match else 0
    elif has_url and not values_to_verify:
        # 검증할 수치가 없으면 부분 점수 부여
        body_score = int(SCORE_WEIGHTS["body_match"] * 0.5)

    total = url_score + body_score + trusted_score + cross_score

    return SourceScore(
        total=min(total, 100),
        has_url=has_url,
        body_match=body_match,
        trusted_source=trusted,
        cross_source_count=cross_count,
        breakdown={
            "has_url": url_score,
            "body_match": body_score,
            "trusted_source": trusted_score,
            "cross_source": cross_score,
        },
        grade=_calc_grade(total),
    )


def format_score_badge(score: SourceScore) -> str:
    """신뢰도 점수를 UI 표시용 문자열로 변환"""
    grade_emoji = {"A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴"}.get(score.grade, "⚪")
    return f"{grade_emoji} {score.total}점 ({score.grade}등급)"
