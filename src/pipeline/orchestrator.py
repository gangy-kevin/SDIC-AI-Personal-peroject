"""
Phase 2 멀티에이전트 오케스트레이터
LangGraph를 사용해 4개 에이전트를 병렬 실행하고 결과를 통합

파이프라인:
  START
    └─ [병렬] market_size_node / competitor_node / regulation_node / trend_node
    └─ aggregate_node  (4개 결과 통합)
  END
"""
from __future__ import annotations

import operator
from dataclasses import dataclass, field
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END

from src.agents.market_size import run_market_size_agent, MarketSizeResult
from src.agents.competitor import run_competitor_agent, CompetitorResult
from src.agents.regulation import run_regulation_agent, RegulationResult
from src.agents.trend import run_trend_agent, TrendResult


# ── 공유 상태 정의 ────────────────────────────────────────
class ResearchState(TypedDict):
    # 입력
    company_name: str
    industry: str
    core_question: str
    year: str

    # 각 에이전트 결과 (Annotated[list, operator.add] → 병렬 노드 결과를 리스트로 누적)
    agent_results: Annotated[list, operator.add]

    # 최종 통합 결과
    aggregated: dict


# ── 에이전트 노드 함수 ────────────────────────────────────

def market_size_node(state: ResearchState) -> dict:
    result = run_market_size_agent(
        company_name=state["company_name"],
        industry=state["industry"],
        core_question=state["core_question"],
        year=state["year"],
    )
    return {"agent_results": [{"type": "market_size", "data": result}]}


def competitor_node(state: ResearchState) -> dict:
    result = run_competitor_agent(
        company_name=state["company_name"],
        industry=state["industry"],
        core_question=state["core_question"],
        year=state["year"],
    )
    return {"agent_results": [{"type": "competitor", "data": result}]}


def regulation_node(state: ResearchState) -> dict:
    result = run_regulation_agent(
        company_name=state["company_name"],
        industry=state["industry"],
        core_question=state["core_question"],
        year=state["year"],
    )
    return {"agent_results": [{"type": "regulation", "data": result}]}


def trend_node(state: ResearchState) -> dict:
    result = run_trend_agent(
        company_name=state["company_name"],
        industry=state["industry"],
        core_question=state["core_question"],
        year=state["year"],
    )
    return {"agent_results": [{"type": "trend", "data": result}]}


# ── 통합 노드 ─────────────────────────────────────────────

def aggregate_node(state: ResearchState) -> dict:
    """4개 에이전트 결과를 하나의 딕셔너리로 통합"""
    aggregated: dict = {
        "company_name": state["company_name"],
        "industry": state["industry"],
        "core_question": state["core_question"],
        "year": state["year"],
        "agents": {},
        "combined_summary": "",
        "all_source_urls": [],
        "avg_score": 0,
        "errors": [],
    }

    all_urls: list[str] = []
    score_sum = 0
    score_count = 0
    summary_parts = [
        "=" * 60,
        f"  Phase 2 선행 조사 결과 — {state['company_name']} / {state['industry']}",
        f"  핵심 질문: {state['core_question']}",
        "=" * 60,
        "",
    ]

    for item in state.get("agent_results", []):
        agent_type = item["type"]
        data = item["data"]
        aggregated["agents"][agent_type] = data

        if data.error:
            aggregated["errors"].append(f"[{agent_type}] {data.error}")

        all_urls.extend(data.source_urls)
        if data.score_total > 0:
            score_sum += data.score_total
            score_count += 1

        summary_parts.append(data.summary)
        summary_parts.append("")

    # 평균 신뢰도
    aggregated["avg_score"] = score_sum // score_count if score_count else 0
    aggregated["all_source_urls"] = list(set(all_urls))

    # 전체 출처 수 및 점수 요약
    summary_parts += [
        "=" * 60,
        f"  📊 수집 출처 수: {len(aggregated['all_source_urls'])}개",
        f"  📈 평균 신뢰도: {aggregated['avg_score']}점",
        "=" * 60,
    ]
    aggregated["combined_summary"] = "\n".join(summary_parts)

    return {"aggregated": aggregated}


# ── 그래프 빌드 ───────────────────────────────────────────

def build_research_graph() -> StateGraph:
    """4개 에이전트 병렬 실행 그래프 생성"""
    builder = StateGraph(ResearchState)

    # 에이전트 노드 등록
    builder.add_node("market_size", market_size_node)
    builder.add_node("competitor", competitor_node)
    builder.add_node("regulation", regulation_node)
    builder.add_node("trend", trend_node)
    builder.add_node("aggregate", aggregate_node)

    # START → 4개 에이전트 병렬 실행
    builder.add_edge(START, "market_size")
    builder.add_edge(START, "competitor")
    builder.add_edge(START, "regulation")
    builder.add_edge(START, "trend")

    # 4개 에이전트 → 통합 노드
    builder.add_edge("market_size", "aggregate")
    builder.add_edge("competitor", "aggregate")
    builder.add_edge("regulation", "aggregate")
    builder.add_edge("trend", "aggregate")

    # 통합 → END
    builder.add_edge("aggregate", END)

    return builder.compile()


# ── 메인 실행 함수 ────────────────────────────────────────

def run_preliminary_research(
    company_name: str,
    industry: str,
    core_question: str,
    year: str = "2023",
) -> dict:
    """
    Phase 2 선행 조사 실행 진입점

    Args:
        company_name: 분석 대상 기업명
        industry: 산업명
        core_question: 핵심 질문
        year: 재무 데이터 기준 연도

    Returns:
        aggregated dict — agents / combined_summary / all_source_urls / avg_score
    """
    graph = build_research_graph()

    initial_state: ResearchState = {
        "company_name": company_name,
        "industry": industry,
        "core_question": core_question,
        "year": year,
        "agent_results": [],
        "aggregated": {},
    }

    final_state = graph.invoke(initial_state)
    return final_state["aggregated"]
