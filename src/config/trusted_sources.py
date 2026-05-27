"""
신뢰 소스 필터 도메인 정의
Claude 웹서치 결과 필터링에 사용
"""

# ── 국내 신뢰 소스 ────────────────────────────────────────
DOMESTIC_TRUSTED_DOMAINS: list[str] = [
    # 증권사 리포트
    "consensus.hankyung.com",   # 한경 컨센서스
    "finance.naver.com",        # 네이버 금융
    "securities.miraeasset.com",
    "www.kiwoom.com",

    # 경제지
    "mk.co.kr",                 # 매일경제
    "hankyung.com",             # 한국경제
    "sedaily.com",              # 서울경제
    "chosun.com",               # 조선일보 경제
    "joongang.co.kr",           # 중앙일보 경제

    # 공시
    "dart.fss.or.kr",           # DART (금융감독원)
    "kind.krx.co.kr",           # KRX 전자공시

    # 통계/연구
    "kostat.go.kr",             # 통계청
    "kiet.re.kr",               # 산업연구원
    "kisdi.re.kr",              # 정보통신정책연구원
    "kdb.co.kr",                # KDB미래전략연구소
]

# ── 해외 신뢰 소스 ────────────────────────────────────────
INTERNATIONAL_TRUSTED_DOMAINS: list[str] = [
    # 기술/산업 미디어
    "techcrunch.com",
    "coindesk.com",
    "wired.com",
    "theverge.com",

    # 금융/경제
    "bloomberg.com",
    "reuters.com",
    "ft.com",                   # Financial Times
    "wsj.com",                  # Wall Street Journal
    "economist.com",

    # 리서치/통계
    "statista.com",
    "idc.com",
    "gartner.com",
    "mckinsey.com",
    "bcg.com",
]

# ── 전체 합산 ────────────────────────────────────────────
ALL_TRUSTED_DOMAINS: list[str] = DOMESTIC_TRUSTED_DOMAINS + INTERNATIONAL_TRUSTED_DOMAINS


def is_trusted_source(url: str) -> bool:
    """URL이 신뢰 소스 필터에 해당하는지 확인"""
    return any(domain in url for domain in ALL_TRUSTED_DOMAINS)


def get_trusted_domains_str() -> str:
    """신뢰 소스 도메인 리스트를 시스템 프롬프트용 문자열로 반환"""
    domestic = "\n".join(f"  - {d}" for d in DOMESTIC_TRUSTED_DOMAINS)
    international = "\n".join(f"  - {d}" for d in INTERNATIONAL_TRUSTED_DOMAINS)
    return f"국내 신뢰 소스:\n{domestic}\n\n해외 신뢰 소스:\n{international}"
