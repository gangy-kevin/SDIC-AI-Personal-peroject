"""
시장규모 에이전트
- 대상 산업의 시장 규모, 성장률(CAGR), 주요 세그먼트 조사
- 국내 상장사: DART API / 해외 기업: Claude 웹서치
"""
from dataclasses import dataclass, field
from src.agents.base import BaseAgentResult
from src.tools.router import route_company_data
from src.tools.web_search import search_with_claude
from src.tools.source_filter import calculate_score, format_score_badge


@dataclass
class MarketSizeResult(BaseAgentResult):
    agent: str = "market_size"
    market_size: str = ""           # 시장 규모 수치
    cagr: str = ""                  # 연평균 성장률
    key_segments: list[str] = field(default_factory=list)   # 주요 세그먼트


def run_market_size_agent(
    company_name: str,
    industry: str,
    core_question: str,
    year: str = "2023",
) -> MarketSizeResult:
    """
    시장규모 에이전트 실행

    Args:
        company_name: 분석 대상 기업명
        industry: 산업명
        core_question: 핵심 질문
        year: 기준 연도

    Returns:
        MarketSizeResult
    """
    result = MarketSizeResult(
        company_name=company_name,
        industry=industry,
        year=year,
    )

    try:
        # 1. 듀얼 트랙 라우터로 기업 데이터 수집
        router_result = route_company_data(
            company_name=company_name,
            industry=industry,
            core_question=core_question,
            year=year,
        )

        # 2. 시장규모 특화 웹서치 (라우터 결과와 별도 추가 조사)
        market_query = (
            f"{industry} 시장규모 CAGR 성장률 {year} "
            f"글로벌 국내 세그먼트 전망"
        )
        context = f"기업: {company_name} | 핵심 질문: {core_question}"
        market_sr = search_with_claude(query=market_query, context=context)

        # 3. 출처 URL 통합
        all_urls = list(set(router_result.source_urls + [s["url"] for s in market_sr.sources]))
        result.source_urls = all_urls

        # 4. 신뢰도 점수
        score = calculate_score(urls=all_urls, values_to_verify=None)
        result.score_badge = format_score_badge(score)
        result.score_total = score.total

        # 5. 요약 조립
        summary_parts = [
            f"[시장규모 에이전트 — {industry}]",
            "",
            "▶ 기업 데이터:",
            router_result.summary,
            "",
            "▶ 시장 규모 조사:",
            market_sr.content[:800],
            "",
            f"신뢰도: {result.score_badge}",
        ]
        result.summary = "\n".join(summary_parts)

    except Exception as e:
        result.error = str(e)
        result.summary = f"[시장규모 에이전트 오류] {e}"

    return result
