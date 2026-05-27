"""
경쟁사 에이전트
- 주요 경쟁사 현황, 점유율, 전략적 포지셔닝 조사
- 국내 상장사: DART API / 해외 기업: Claude 웹서치
"""
from dataclasses import dataclass, field
from src.agents.base import BaseAgentResult
from src.tools.router import route_company_data
from src.tools.web_search import search_with_claude
from src.tools.source_filter import calculate_score, format_score_badge


@dataclass
class CompetitorResult(BaseAgentResult):
    agent: str = "competitor"
    competitors: list[str] = field(default_factory=list)    # 주요 경쟁사 목록
    market_share: str = ""          # 시장 점유율 정보
    competitive_edge: str = ""      # 경쟁 우위 요소


def run_competitor_agent(
    company_name: str,
    industry: str,
    core_question: str,
    year: str = "2023",
) -> CompetitorResult:
    """
    경쟁사 에이전트 실행

    Args:
        company_name: 분석 대상 기업명
        industry: 산업명
        core_question: 핵심 질문
        year: 기준 연도

    Returns:
        CompetitorResult
    """
    result = CompetitorResult(
        company_name=company_name,
        industry=industry,
        year=year,
    )

    try:
        # 1. 듀얼 트랙 라우터로 기업 기본 데이터 수집
        router_result = route_company_data(
            company_name=company_name,
            industry=industry,
            core_question=core_question,
            year=year,
        )

        # 2. 경쟁사 특화 웹서치
        competitor_query = (
            f"{company_name} {industry} 경쟁사 시장점유율 competitive landscape "
            f"주요 플레이어 {year}"
        )
        context = f"기업: {company_name} | 핵심 질문: {core_question}"
        competitor_sr = search_with_claude(query=competitor_query, context=context)

        # 3. 포지셔닝 추가 조사
        positioning_query = (
            f"{company_name} vs 경쟁사 기술력 차별화 전략 {industry} {year}"
        )
        positioning_sr = search_with_claude(query=positioning_query, context=context)

        # 4. 출처 URL 통합
        all_urls = list(set(
            router_result.source_urls
            + [s["url"] for s in competitor_sr.sources]
            + [s["url"] for s in positioning_sr.sources]
        ))
        result.source_urls = all_urls

        # 5. 신뢰도 점수
        score = calculate_score(urls=all_urls, values_to_verify=None)
        result.score_badge = format_score_badge(score)
        result.score_total = score.total

        # 6. 요약 조립
        summary_parts = [
            f"[경쟁사 에이전트 — {company_name} vs 경쟁사]",
            "",
            "▶ 기업 기본 데이터:",
            router_result.summary,
            "",
            "▶ 경쟁사 현황:",
            competitor_sr.content[:600],
            "",
            "▶ 경쟁 포지셔닝:",
            positioning_sr.content[:400],
            "",
            f"신뢰도: {result.score_badge}",
        ]
        result.summary = "\n".join(summary_parts)

    except Exception as e:
        result.error = str(e)
        result.summary = f"[경쟁사 에이전트 오류] {e}"

    return result
