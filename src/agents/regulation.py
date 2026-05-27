"""
규제 에이전트
- 산업 관련 국내외 규제 동향, 정책 변화, 인증 요건 조사
"""
from dataclasses import dataclass
from src.agents.base import BaseAgentResult
from src.tools.web_search import search_with_claude
from src.tools.source_filter import calculate_score, format_score_badge


@dataclass
class RegulationResult(BaseAgentResult):
    agent: str = "regulation"
    domestic_regulations: str = ""      # 국내 규제 현황
    international_regulations: str = "" # 해외 규제 현황
    upcoming_changes: str = ""          # 예정된 규제 변화


def run_regulation_agent(
    company_name: str,
    industry: str,
    core_question: str,
    year: str = "2023",
) -> RegulationResult:
    """
    규제 에이전트 실행

    Args:
        company_name: 분석 대상 기업명
        industry: 산업명
        core_question: 핵심 질문
        year: 기준 연도

    Returns:
        RegulationResult
    """
    result = RegulationResult(
        company_name=company_name,
        industry=industry,
        year=year,
    )

    try:
        context = f"기업: {company_name} | 핵심 질문: {core_question}"

        # 1. 국내 규제 조사
        domestic_query = (
            f"{industry} 국내 규제 정책 법령 인증 요건 {year} "
            f"산업통상자원부 환경부 금융위원회"
        )
        domestic_sr = search_with_claude(query=domestic_query, context=context)

        # 2. 해외 규제 조사 (EU, 미국, 중국 등 주요 시장)
        international_query = (
            f"{industry} international regulation policy EU US China "
            f"compliance certification {year}"
        )
        international_sr = search_with_claude(
            query=international_query, context=context
        )

        # 3. 향후 규제 변화 전망
        upcoming_query = (
            f"{industry} 규제 변화 전망 {int(year)+1} {int(year)+2} "
            f"policy roadmap upcoming regulation"
        )
        upcoming_sr = search_with_claude(query=upcoming_query, context=context)

        # 4. 출처 URL 통합
        all_urls = list(set(
            [s["url"] for s in domestic_sr.sources]
            + [s["url"] for s in international_sr.sources]
            + [s["url"] for s in upcoming_sr.sources]
        ))
        result.source_urls = all_urls

        # 5. 신뢰도 점수
        score = calculate_score(urls=all_urls, values_to_verify=None)
        result.score_badge = format_score_badge(score)
        result.score_total = score.total

        # 6. 요약 조립
        result.domestic_regulations = domestic_sr.content[:400]
        result.international_regulations = international_sr.content[:400]
        result.upcoming_changes = upcoming_sr.content[:300]

        summary_parts = [
            f"[규제 에이전트 — {industry}]",
            "",
            "▶ 국내 규제 현황:",
            result.domestic_regulations,
            "",
            "▶ 해외 규제 현황:",
            result.international_regulations,
            "",
            "▶ 향후 규제 변화 전망:",
            result.upcoming_changes,
            "",
            f"신뢰도: {result.score_badge}",
        ]
        result.summary = "\n".join(summary_parts)

    except Exception as e:
        result.error = str(e)
        result.summary = f"[규제 에이전트 오류] {e}"

    return result
