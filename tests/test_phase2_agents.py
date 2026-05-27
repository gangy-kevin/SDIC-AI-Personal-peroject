"""
Phase 2 멀티에이전트 선행조사 테스트
실행: .venv/bin/python tests/test_phase2_agents.py

데모 시나리오:
  산업: 차량용 디스플레이
  기업: LG디스플레이
  핵심 질문: LGD가 차량용 OLED 디스플레이 시장에서 중국 경쟁사 대비 지속 성장 가능한가?
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

COMPANY = "LG디스플레이"
INDUSTRY = "차량용 디스플레이"
QUESTION = "LGD가 차량용 OLED 디스플레이 시장에서 중국 경쟁사 대비 지속 성장 가능한가?"
YEAR = "2023"


def test_market_size_agent():
    print("\n" + "=" * 50)
    print("📊 시장규모 에이전트 테스트")
    print("=" * 50)
    from src.agents.market_size import run_market_size_agent

    t0 = time.time()
    result = run_market_size_agent(COMPANY, INDUSTRY, QUESTION, YEAR)
    elapsed = time.time() - t0

    print(f"  소요 시간: {elapsed:.1f}초")
    print(f"  에이전트: {result.agent}")
    print(f"  출처 수: {len(result.source_urls)}개")
    print(f"  신뢰도: {result.score_badge}")
    if result.error:
        print(f"  ⚠️ 오류: {result.error}")
    else:
        print(f"  요약 길이: {len(result.summary)}자")
        print(f"  요약 미리보기:\n  {result.summary[:200]}...")

    return not bool(result.error)


def test_competitor_agent():
    print("\n" + "=" * 50)
    print("🏢 경쟁사 에이전트 테스트")
    print("=" * 50)
    from src.agents.competitor import run_competitor_agent

    t0 = time.time()
    result = run_competitor_agent(COMPANY, INDUSTRY, QUESTION, YEAR)
    elapsed = time.time() - t0

    print(f"  소요 시간: {elapsed:.1f}초")
    print(f"  출처 수: {len(result.source_urls)}개")
    print(f"  신뢰도: {result.score_badge}")
    if result.error:
        print(f"  ⚠️ 오류: {result.error}")
    else:
        print(f"  요약 길이: {len(result.summary)}자")
        print(f"  요약 미리보기:\n  {result.summary[:200]}...")

    return not bool(result.error)


def test_regulation_agent():
    print("\n" + "=" * 50)
    print("⚖️  규제 에이전트 테스트")
    print("=" * 50)
    from src.agents.regulation import run_regulation_agent

    t0 = time.time()
    result = run_regulation_agent(COMPANY, INDUSTRY, QUESTION, YEAR)
    elapsed = time.time() - t0

    print(f"  소요 시간: {elapsed:.1f}초")
    print(f"  출처 수: {len(result.source_urls)}개")
    print(f"  신뢰도: {result.score_badge}")
    if result.error:
        print(f"  ⚠️ 오류: {result.error}")
    else:
        print(f"  요약 길이: {len(result.summary)}자")

    return not bool(result.error)


def test_trend_agent():
    print("\n" + "=" * 50)
    print("📈 트렌드 에이전트 테스트")
    print("=" * 50)
    from src.agents.trend import run_trend_agent

    t0 = time.time()
    result = run_trend_agent(COMPANY, INDUSTRY, QUESTION, YEAR)
    elapsed = time.time() - t0

    print(f"  소요 시간: {elapsed:.1f}초")
    print(f"  출처 수: {len(result.source_urls)}개")
    print(f"  신뢰도: {result.score_badge}")
    if result.error:
        print(f"  ⚠️ 오류: {result.error}")
    else:
        print(f"  요약 길이: {len(result.summary)}자")

    return not bool(result.error)


def test_orchestrator():
    print("\n" + "=" * 50)
    print("🔀 LangGraph 오케스트레이터 테스트 (4개 병렬)")
    print("=" * 50)
    from src.pipeline.orchestrator import run_preliminary_research

    print(f"  기업: {COMPANY}")
    print(f"  산업: {INDUSTRY}")
    print(f"  질문: {QUESTION[:50]}...")

    t0 = time.time()
    result = run_preliminary_research(COMPANY, INDUSTRY, QUESTION, YEAR)
    elapsed = time.time() - t0

    print(f"\n  ⏱️  전체 소요 시간: {elapsed:.1f}초")
    print(f"  수집 에이전트 수: {len(result.get('agents', {}))}개")
    print(f"  총 출처 수: {len(result.get('all_source_urls', []))}개")
    print(f"  평균 신뢰도: {result.get('avg_score', 0)}점")

    errors = result.get("errors", [])
    if errors:
        print(f"  ⚠️ 오류 ({len(errors)}건):")
        for e in errors:
            print(f"    - {e}")

    # 에이전트별 점수 요약
    print("\n  에이전트별 결과:")
    for agent_type, agent_data in result.get("agents", {}).items():
        icon = {"market_size": "📊", "competitor": "🏢", "regulation": "⚖️", "trend": "📈"}.get(agent_type, "•")
        status = "✅" if not agent_data.error else "❌"
        print(f"    {status} {icon} {agent_type}: {agent_data.score_badge}")

    # 전체 요약 출력
    print("\n" + "-" * 60)
    print(result.get("combined_summary", "")[:1000])
    print("-" * 60)

    return len(result.get("agents", {})) == 4


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  Phase 2 멀티에이전트 선행조사 테스트")
    print("=" * 50)

    results = {}

    # 개별 에이전트 테스트
    results["market_size"] = test_market_size_agent()
    results["competitor"] = test_competitor_agent()
    results["regulation"] = test_regulation_agent()
    results["trend"] = test_trend_agent()

    # 통합 오케스트레이터 테스트
    results["orchestrator"] = test_orchestrator()

    # 최종 결과
    print("\n" + "=" * 50)
    print("📋 Phase 2 최종 결과")
    print("=" * 50)
    for name, ok in results.items():
        print(f"  {'✅' if ok else '❌'} {name}")

    if all(results.values()):
        print("\n🎉 Phase 2 완료 — Phase 3(분석 축 설계)으로 진행 가능!")
    else:
        print("\n⚠️  일부 항목 확인 필요")
