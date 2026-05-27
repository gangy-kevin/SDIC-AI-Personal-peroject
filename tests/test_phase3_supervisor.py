"""
Phase 3 분석 축 설계 테스트 — Claude Supervisor
실행: .venv/bin/python tests/test_phase3_supervisor.py

테스트 전략:
  1. 가벼운 mock 요약으로 Supervisor 단독 테스트
  2. Phase 2 오케스트레이터와 연결한 풀파이프라인 테스트 (선택)
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

COMPANY  = "LG디스플레이"
INDUSTRY = "차량용 디스플레이"
QUESTION = "LGD가 차량용 OLED 디스플레이 시장에서 중국 경쟁사 대비 지속 성장 가능한가?"
YEAR     = "2023"

# Phase 2 결과를 시뮬레이션한 mock 요약 (API 비용 절감)
MOCK_RESEARCH_SUMMARY = """
[시장규모 에이전트]
- 차량용 디스플레이 글로벌 시장: 2023년 약 126억 달러, CAGR 7.8% 전망
- 차량용 OLED 출하량 2030년까지 연 40% 성장 예상
- 전기차·자율주행 확산이 핵심 성장 동인

[경쟁사 에이전트]
- LG디스플레이 (LGD): 차량용 OLED 1위, 2023년 자산총계 35.7조
- 중국 BOE, CSOT 등이 LCD 중심으로 점유율 확대 중
- 일본 JDI·Sharp 약세, 삼성디스플레이는 중소형 OLED 집중

[규제 에이전트]
- EU 탄소국경세(CBAM) 도입 → 저탄소 생산공정 요구 강화
- 미국 IRA: 북미 생산 부품 우대 → 해외 공급망 리스크
- 중국 디스플레이 보조금 정책 지속 (BOE 등 경쟁사 지원)

[트렌드 에이전트]
- 차량 내 디스플레이 대형화·곡면화 트렌드 가속
- OLED 기술 우위: 명암비·응답속도·경량화
- 중국 업체의 가격 경쟁 심화 (LCD 기준 30~40% 저가 공세)
"""


def test_supervisor_standalone():
    """mock 요약으로 Supervisor 단독 테스트"""
    print("\n" + "=" * 50)
    print("🧠 Supervisor 단독 테스트 (mock 데이터)")
    print("=" * 50)
    from src.agents.supervisor import run_supervisor

    t0 = time.time()
    result = run_supervisor(
        company_name=COMPANY,
        industry=INDUSTRY,
        core_question=QUESTION,
        research_summary=MOCK_RESEARCH_SUMMARY,
    )
    elapsed = time.time() - t0

    print(f"  소요 시간: {elapsed:.1f}초")

    if result.get("error"):
        print(f"  ❌ 오류: {result['error']}")
        return False

    key_drivers = result.get("key_drivers", [])
    ksfs = result.get("ksfs", [])

    print(f"  Key Driver 수: {len(key_drivers)}개")
    print(f"  KSF 수: {len(ksfs)}개")
    total_hyp = sum(len(k["hypotheses"]) for k in ksfs)
    print(f"  총 가설 수: {total_hyp}개")

    print("\n" + result.get("analysis_summary", ""))

    return len(key_drivers) == 3 and len(ksfs) == 3 and total_hyp == 9


def test_full_pipeline():
    """Phase 2 오케스트레이터 → Phase 3 Supervisor 풀파이프라인"""
    print("\n" + "=" * 50)
    print("🔗 풀파이프라인 테스트 (Phase 2 → Phase 3)")
    print("=" * 50)
    print("  ⚠️  실제 API 호출 — 약 3~5분 소요")

    from src.pipeline.orchestrator import run_preliminary_research
    from src.agents.supervisor import run_supervisor

    # Phase 2
    print("\n  [1/2] Phase 2 선행조사 실행 중...")
    t0 = time.time()
    research = run_preliminary_research(COMPANY, INDUSTRY, QUESTION, YEAR)
    print(f"  Phase 2 완료 ({time.time()-t0:.0f}초) — 평균 신뢰도 {research.get('avg_score')}점")

    # Phase 3
    print("\n  [2/2] Phase 3 Supervisor 실행 중...")
    t1 = time.time()
    result = run_supervisor(
        company_name=COMPANY,
        industry=INDUSTRY,
        core_question=QUESTION,
        research_summary=research.get("combined_summary", ""),
    )
    print(f"  Phase 3 완료 ({time.time()-t1:.0f}초)")

    if result.get("error"):
        print(f"  ❌ 오류: {result['error']}")
        return False

    ksfs = result.get("ksfs", [])
    total_hyp = sum(len(k["hypotheses"]) for k in ksfs)
    print(f"\n  총 가설 수: {total_hyp}개")
    print(result.get("analysis_summary", ""))

    return total_hyp == 9


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="풀파이프라인 테스트 실행")
    args = parser.parse_args()

    print("\n" + "=" * 50)
    print("  Phase 3 분석 축 설계 테스트")
    print("=" * 50)

    results = {}
    results["supervisor_standalone"] = test_supervisor_standalone()

    if args.full:
        results["full_pipeline"] = test_full_pipeline()

    print("\n" + "=" * 50)
    print("📋 Phase 3 최종 결과")
    print("=" * 50)
    for name, ok in results.items():
        print(f"  {'✅' if ok else '❌'} {name}")

    if all(results.values()):
        print("\n🎉 Phase 3 완료 — Phase 4(가설 검증)으로 진행 가능!")
    else:
        print("\n⚠️  일부 항목 확인 필요")
