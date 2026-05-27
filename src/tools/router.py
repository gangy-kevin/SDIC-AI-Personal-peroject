"""
듀얼 트랙 데이터 라우터
- 분석 대상 기업의 국적에 따라 데이터 수집 경로 자동 분기
- 국내 상장사 → DART API
- 해외 기업   → Claude 웹서치 + 신뢰 소스 필터
"""
from dataclasses import dataclass, field
from src.tools.dart_api import collect_dart_data
from src.tools.web_search import search_with_claude, SearchResult


# 국내 주요 기업 키워드 (빠른 판별용)
DOMESTIC_KEYWORDS = [
    "삼성", "현대", "LG", "SK", "롯데", "포스코", "한화", "GS", "CJ", "카카오",
    "네이버", "기아", "셀트리온", "크래프톤", "하이닉스", "두산", "한국전력",
    "KB", "신한", "우리", "하나", "NH", "KT", "LGU+", "SKT",
]

# 해외 주요 기업 키워드
INTERNATIONAL_KEYWORDS = [
    "Apple", "Google", "Tesla", "Amazon", "Microsoft", "Meta", "NVIDIA",
    "BYD", "CATL", "Toyota", "Samsung SDI", "TSMC", "Intel", "Qualcomm",
    "BMW", "Mercedes", "Volkswagen", "Sony", "Panasonic",
]


@dataclass
class RouterResult:
    company_name: str
    is_domestic: bool
    track: str                          # "dart" | "web_search"
    dart_data: dict = field(default_factory=dict)
    web_results: list[SearchResult] = field(default_factory=list)
    summary: str = ""                   # 수집 결과 요약 텍스트
    source_urls: list[str] = field(default_factory=list)


def detect_domestic(company_name: str) -> bool:
    """기업명 기반 국내/해외 판별"""
    # 국내 키워드 포함 여부
    for kw in DOMESTIC_KEYWORDS:
        if kw in company_name:
            return True
    # 해외 키워드 포함 시 해외로 판별
    for kw in INTERNATIONAL_KEYWORDS:
        if kw.lower() in company_name.lower():
            return False
    # 한글 포함 → 국내 추정
    has_korean = any("가" <= c <= "힣" for c in company_name)
    return has_korean


def route_company_data(
    company_name: str,
    industry: str,
    core_question: str,
    year: str = "2023",
) -> RouterResult:
    """
    기업명에 따라 데이터 수집 경로 자동 결정 후 실행

    Args:
        company_name: 분석 대상 기업명
        industry: 산업명
        core_question: 핵심 질문
        year: 재무 데이터 기준 연도

    Returns:
        RouterResult (수집된 데이터 + 경로 정보)
    """
    is_domestic = detect_domestic(company_name)
    track = "dart" if is_domestic else "web_search"

    result = RouterResult(
        company_name=company_name,
        is_domestic=is_domestic,
        track=track,
    )

    context = f"산업: {industry} | 핵심 질문: {core_question}"

    if is_domestic:
        # ── 국내 상장사: DART API ──────────────────────────
        dart_data = collect_dart_data(company_name, year)
        result.dart_data = dart_data
        result.source_urls = dart_data.get("source_urls", [])

        # DART 데이터를 텍스트 요약으로 변환
        summary_parts = [f"[DART 공시 데이터 — {company_name}]"]

        if dart_data.get("company_info"):
            info = dart_data["company_info"]
            summary_parts.append(f"산업코드: {info.industry} | CEO: {info.ceo_name}")

        if dart_data.get("financials"):
            fin = dart_data["financials"]
            summary_parts.append(f"\n재무 현황 ({fin.year}년 연결기준):")
            for item in fin.account_items:
                amount_int = int(item["amount"]) if item["amount"].lstrip("-").isdigit() else 0
                amount_str = f"{amount_int:,}원" if amount_int else item["amount"]
                summary_parts.append(f"  - {item['account']}: {amount_str}")
            summary_parts.append(f"  출처: {fin.source_url}")

        if dart_data.get("disclosures"):
            summary_parts.append("\n최근 공시:")
            for d in dart_data["disclosures"]:
                summary_parts.append(f"  - [{d.date}] {d.title} ({d.url})")

        if dart_data.get("error"):
            summary_parts.append(f"\n⚠️ DART 조회 오류: {dart_data['error']}")
            # DART 실패 시 웹서치로 폴백
            fallback = search_with_claude(
                query=f"{company_name} 재무현황 매출 영업이익 {year}",
                context=context,
            )
            result.web_results.append(fallback)
            result.source_urls += [s["url"] for s in fallback.sources]
            summary_parts.append("\n[웹서치 폴백 결과]")
            summary_parts.append(fallback.content[:500])

        result.summary = "\n".join(summary_parts)

    else:
        # ── 해외 기업: Claude 웹서치 ──────────────────────
        queries = [
            f"{company_name} revenue market share financial results {year}",
            f"{company_name} {industry} competitive position strategy",
        ]
        for q in queries:
            sr = search_with_claude(query=q, context=context)
            result.web_results.append(sr)
            result.source_urls += [s["url"] for s in sr.sources]

        combined = "\n\n".join(r.content for r in result.web_results)
        result.summary = f"[웹서치 데이터 — {company_name}]\n{combined[:1500]}"

    return result
