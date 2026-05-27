"""
Phase 1 데이터 수집 레이어 테스트
실행: .venv/bin/python tests/test_phase1_tools.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_url_fetcher():
    print("\n" + "="*50)
    print("🌐 URL Fetcher 테스트")
    print("="*50)
    from src.tools.url_fetcher import fetch_url, verify_value_in_text

    result = fetch_url("https://www.hankyung.com")
    print(f"  URL: https://www.hankyung.com")
    print(f"  성공: {result.success}")
    print(f"  제목: {result.title[:40] if result.title else '없음'}")
    print(f"  본문 길이: {len(result.text)} 자")

    # 수치 검증 테스트
    sample_text = "2023년 매출액은 3조 2천억원을 기록했다."
    ok = verify_value_in_text("3조2천억원", sample_text)
    print(f"  수치 검증 ('3조2천억원' 존재): {ok}")
    return result.success


def test_dart_api():
    print("\n" + "="*50)
    print("📊 DART API 테스트 (LG디스플레이)")
    print("="*50)
    from src.tools.dart_api import collect_dart_data

    data = collect_dart_data("LG디스플레이", "2022")
    print(f"  기업명: {data['company_name']}")
    print(f"  corp_code: {data['corp_code']}")

    if data.get("company_info"):
        info = data["company_info"]
        print(f"  CEO: {info.ceo_name}")
        print(f"  주소: {info.address[:30]}")

    if data.get("financials"):
        fin = data["financials"]
        print(f"  재무({fin.year}년):")
        for item in fin.account_items[:3]:
            amount = int(item['amount']) if item['amount'].lstrip('-').isdigit() else 0
            print(f"    {item['account']}: {amount:,}원")

    if data.get("disclosures"):
        print(f"  최근 공시: {data['disclosures'][0].title}")

    if data.get("error"):
        print(f"  ⚠️ 오류: {data['error']}")

    return data.get("corp_code") is not None


def test_source_filter():
    print("\n" + "="*50)
    print("🔢 신뢰도 점수 산출 테스트")
    print("="*50)
    from src.tools.source_filter import calculate_score, format_score_badge

    # 신뢰 소스 URL로 테스트
    urls = ["https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20230101"]
    score = calculate_score(urls=urls, values_to_verify=None)
    badge = format_score_badge(score)
    print(f"  URL 1개 (DART): {badge}")
    print(f"  항목별: {score.breakdown}")

    # 복수 URL
    urls2 = ["https://dart.fss.or.kr/test", "https://mk.co.kr/test"]
    score2 = calculate_score(urls=urls2)
    print(f"  URL 2개 (DART+매경): {format_score_badge(score2)}")
    return True


def test_router():
    print("\n" + "="*50)
    print("🔀 듀얼 트랙 라우터 테스트")
    print("="*50)
    from src.tools.router import detect_domestic

    test_cases = [
        ("LG디스플레이", True),
        ("삼성전자", True),
        ("Tesla", False),
        ("BYD", False),
        ("현대자동차", True),
    ]
    all_ok = True
    for name, expected in test_cases:
        result = detect_domestic(name)
        ok = result == expected
        icon = "✅" if ok else "❌"
        track = "DART" if result else "웹서치"
        print(f"  {icon} {name} → {track} ({'예상일치' if ok else '예상불일치'})")
        if not ok:
            all_ok = False
    return all_ok


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  Phase 1 데이터 수집 레이어 테스트")
    print("="*50)

    results = {
        "url_fetcher": test_url_fetcher(),
        "dart_api": test_dart_api(),
        "source_filter": test_source_filter(),
        "router": test_router(),
    }

    print("\n" + "="*50)
    print("📋 Phase 1 최종 결과")
    print("="*50)
    for name, ok in results.items():
        print(f"  {'✅' if ok else '❌'} {name}")

    if all(results.values()):
        print("\n🎉 Phase 1 완료 — Phase 2(멀티에이전트)로 진행 가능!")
    else:
        print("\n⚠️  일부 항목 확인 필요")
