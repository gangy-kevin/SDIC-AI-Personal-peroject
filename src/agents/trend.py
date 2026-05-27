"""
트렌드 에이전트
- 산업 기술 트렌드, 소비자 변화, 거시 환경(PESTLE) 조사
"""
from dataclasses import dataclass
from src.agents.base import BaseAgentResult
from src.tools.web_search import search_with_claude
from src.tools.source_filter import calculate_score, format_score_badge


@dataclass
class TrendResult(BaseAgentResult):
    agent: str = "trend"
    tech_trends: str = ""           # 기술 트렌드
    consumer_trends: str = ""       # 소비자/수요 트렌드
    macro_trends: str = ""          # 거시 환경 트렌드 (PESTLE)


def run_trend_agent(
    company_name: str,
    industry: str,
    core_question: str,
    year: str = "2023",
) -> TrendResult:
    """
    트렌드 에이전트 실행

    Args:
        company_name: 분석 대상 기업명
        industry: 산업명
        core_question: 핵심 질문
        year: 기준 연도

    Returns:
        TrendResult
    """
    result = TrendResult(
        company_name=company_name,
        industry=industry,
        year=year,
    )

    try:
        context = f"기업: {company_name} | 핵심 질문: {core_question}"

        # 1. 기술 트렌드 조사
        tech_query = (
            f"{industry} 기술 트렌드 혁신 R&D 신기술 {year} "
            f"technology innovation emerging"
        )
        tech_sr = search_with_claude(query=tech_query, context=context)

        # 2. 소비자·수요 트렌드
        consumer_query = (
            f"{industry} 소비자 트렌드 수요 변화 고객 니즈 {year} "
            f"consumer demand market shift"
        )
        consumer_sr = search_with_claude(query=consumer_query, context=context)

        # 3. 거시환경 (경제·지정학·ESG)
        macro_query = (
            f"{industry} 거시경제 지정학 ESG 공급망 {year} "
            f"macro environment geopolitics supply chain"
        )
        macro_sr = search_with_claude(query=macro_query, context=context)

        # 4. 출처 URL 통합
        all_urls = list(set(
            [s["url"] for s in tech_sr.sources]
            + [s["url"] for s in consumer_sr.sources]
            + [s["url"] for s in macro_sr.sources]
        ))
        result.source_urls = all_urls

        # 5. 신뢰도 점수
        score = calculate_score(urls=all_urls, values_to_verify=None)
        result.score_badge = format_score_badge(score)
        result.score_total = score.total

        # 6. 결과 저장 및 요약 조립
        result.tech_trends = tech_sr.content[:400]
        result.consumer_trends = consumer_sr.content[:400]
        result.macro_trends = macro_sr.content[:300]

        summary_parts = [
            f"[트렌드 에이전트 — {industry}]",
            "",
            "▶ 기술 트렌드:",
            result.tech_trends,
            "",
            "▶ 소비자·수요 트렌드:",
            result.consumer_trends,
            "",
            "▶ 거시 환경 (ESG·지정학·공급망):",
            result.macro_trends,
            "",
            f"신뢰도: {result.score_badge}",
        ]
        result.summary = "\n".join(summary_parts)

    except Exception as e:
        result.error = str(e)
        result.summary = f"[트렌드 에이전트 오류] {e}"

    return result
