"""
신뢰 소스 필터 도메인 정의
Claude 웹서치 결과 필터링에 사용

접근성 기준: URL fetch 본문 추출 가능한 무료 공개 소스만 포함
유료 페이월 소스 제외: bloomberg.com / ft.com / wsj.com / economist.com / gartner.com / idc.com
"""

# ── 국내 신뢰 소스 ────────────────────────────────────────
DOMESTIC_TRUSTED_DOMAINS: list[str] = [
    # 증권사 리포트 / 금융 포털
    "consensus.hankyung.com",   # 한경 컨센서스 (증권사 리포트 무료)
    "finance.naver.com",        # 네이버 금융 (기업 재무·공시 무료)
    "securities.miraeasset.com", # 미래에셋 리서치 (무료 공개)
    "www.kiwoom.com",           # 키움증권 리서치 (무료 공개)
    "invest.koreaherald.com",   # 코리아헤럴드 투자 (무료)

    # 경제지
    "mk.co.kr",                 # 매일경제 (무료)
    "hankyung.com",             # 한국경제 (무료)
    "sedaily.com",              # 서울경제 (무료)
    "chosun.com",               # 조선일보 (무료)
    "joongang.co.kr",           # 중앙일보 (무료)
    "donga.com",                # 동아일보 경제 (무료)
    "biz.chosun.com",           # 조선비즈 (무료)
    "news.mt.co.kr",            # 머니투데이 (무료)
    "thebell.co.kr",            # 더벨 (일부 무료)

    # 공시 / 정부
    "dart.fss.or.kr",           # DART 금융감독원 (전면 무료)
    "kind.krx.co.kr",           # KRX 전자공시 (전면 무료)
    "fss.or.kr",                # 금융감독원 (전면 무료)
    "moef.go.kr",               # 기획재정부 (전면 무료)
    "motie.go.kr",              # 산업통상자원부 (전면 무료)
    "mss.go.kr",                # 중소벤처기업부 (전면 무료)

    # 통계 / 연구기관
    "kostat.go.kr",             # 통계청 (전면 무료)
    "kiet.re.kr",               # 산업연구원 KIET (전면 무료)
    "kisdi.re.kr",              # 정보통신정책연구원 (전면 무료)
    "kdb.co.kr",                # KDB미래전략연구소 (무료)
    "kiep.go.kr",               # 대외경제정책연구원 (전면 무료)
    "kdi.re.kr",                # KDI 한국개발연구원 (전면 무료)
    "nipa.kr",                  # 정보통신산업진흥원 (전면 무료)
    "kcern.or.kr",              # 한국경제연구원 (무료)
]

# ── 해외 신뢰 소스 ────────────────────────────────────────
INTERNATIONAL_TRUSTED_DOMAINS: list[str] = [
    # 뉴스통신 / 경제 미디어 (전면 무료)
    "reuters.com",              # 로이터 통신 (전면 무료)
    "apnews.com",               # AP 통신 (전면 무료, 편향 없는 팩트)
    "cnbc.com",                 # CNBC 경제방송 (전면 무료)
    "marketwatch.com",          # 마켓워치 (전면 무료, WSJ 계열이나 본문 무료)
    "businessinsider.com",      # 비즈니스인사이더 (대부분 무료)

    # 기술 / 산업 미디어 (전면 무료)
    "techcrunch.com",           # 테크크런치 (테크·스타트업·VC, 전면 무료)
    "coindesk.com",             # 코인데스크 (블록체인·핀테크, 전면 무료)
    "theverge.com",             # 더버지 (테크·소비자전자, 전면 무료)
    "arstechnica.com",          # 아스테크니카 (기술 심층분석, 전면 무료)
    "venturebeat.com",          # 벤처비트 (AI·테크 트렌드, 전면 무료)
    "wired.com",                # 와이어드 (테크·비즈니스, 대부분 무료)

    # 글로벌 기관 / 싱크탱크 (전면 무료)
    "weforum.org",              # 세계경제포럼 WEF (다보스, 전면 무료)
    "oecd.org",                 # OECD (정책·통계 리포트, 전면 무료)
    "imf.org",                  # IMF (거시경제·금융 리포트, 전면 무료)
    "worldbank.org",            # 세계은행 (개발도상국·산업 데이터, 전면 무료)
    "bis.org",                  # BIS 국제결제은행 (금융안정 리포트, 전면 무료)
    "iea.org",                  # IEA 국제에너지기구 (에너지 산업, 전면 무료)

    # 컨설팅 펌 공개 인사이트 (무료 공개)
    "mckinsey.com",             # 맥킨지 인사이트 (산업별 리포트 무료 공개)
    "bcg.com",                  # BCG 인사이트 (전략 리포트 무료 공개)
    "deloitte.com",             # 딜로이트 인사이트 (전면 무료)
    "pwc.com",                  # PwC 리서치 (전면 무료)
    "ey.com",                   # EY 인사이트 (전면 무료)
    "kpmg.com",                 # KPMG 인사이트 (전면 무료)
    "accenture.com",            # 액센추어 리서치 (전면 무료)

    # 학술 / 통계 포털 (일부 무료)
    "statista.com",             # 스타티스타 (기본 통계 무료, 상세 유료)
    "hbr.org",                  # HBR 하버드비즈니스리뷰 (월 5편 무료)
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
