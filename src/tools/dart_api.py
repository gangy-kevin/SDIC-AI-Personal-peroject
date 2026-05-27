"""
금융감독원 DART Open API 연동 모듈
- 기업 기본정보 조회
- 사업보고서 / 재무제표 수집
- 공시 목록 조회
"""
import io
import zipfile
import xml.etree.ElementTree as ET
import requests
from dataclasses import dataclass, field
from src.config.settings import DART_API_KEY


DART_BASE = "https://opendart.fss.or.kr/api"

# corp_code 캐시 (세션 내 반복 다운로드 방지)
_CORP_CODE_CACHE: dict[str, str] = {}


def _load_corp_code_map() -> dict[str, str]:
    """
    DART 전체 기업코드 목록 다운로드 및 파싱
    반환: {기업명: corp_code}
    """
    global _CORP_CODE_CACHE
    if _CORP_CODE_CACHE:
        return _CORP_CODE_CACHE

    resp = requests.get(
        f"{DART_BASE}/corpCode.xml",
        params={"crtfc_key": DART_API_KEY},
        timeout=30,
    )
    resp.raise_for_status()

    # zip 파일 → XML 파싱
    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
        xml_filename = z.namelist()[0]
        xml_content = z.read(xml_filename)

    root = ET.fromstring(xml_content)
    corp_map = {}
    for item in root.findall("list"):
        name = item.findtext("corp_name", "").strip()
        code = item.findtext("corp_code", "").strip()
        stock = item.findtext("stock_code", "").strip()
        if name and code and stock:   # 상장사만 (stock_code 있는 것)
            corp_map[name] = code

    _CORP_CODE_CACHE = corp_map
    return corp_map


@dataclass
class CompanyInfo:
    corp_code: str
    corp_name: str
    stock_code: str
    industry: str
    ceo_name: str
    address: str


@dataclass
class FinancialData:
    corp_name: str
    year: str
    account_items: list[dict] = field(default_factory=list)  # [{account, amount, unit}]
    source_url: str = "https://dart.fss.or.kr"


@dataclass
class Disclosure:
    title: str
    date: str
    url: str
    corp_name: str


# ── 기업 검색 ─────────────────────────────────────────────

def search_corp_code(company_name: str) -> str | None:
    """
    기업명으로 DART corp_code 검색
    전체 기업코드 목록(zip)을 다운로드 후 파싱하여 매칭
    """
    try:
        corp_map = _load_corp_code_map()

        # 정확히 일치하는 기업명 우선
        if company_name in corp_map:
            return corp_map[company_name]

        # 부분 일치 검색 (예: "LG디스플레이" → "엘지디스플레이(주)" 등)
        company_name_clean = company_name.replace(" ", "").replace("(주)", "").replace("주식회사", "")
        for name, code in corp_map.items():
            name_clean = name.replace(" ", "").replace("(주)", "").replace("주식회사", "")
            if company_name_clean in name_clean or name_clean in company_name_clean:
                return code

    except Exception:
        pass
    return None


def get_company_info(corp_code: str) -> CompanyInfo | None:
    """DART corp_code로 기업 기본정보 조회"""
    try:
        resp = requests.get(
            f"{DART_BASE}/company.json",
            params={"crtfc_key": DART_API_KEY, "corp_code": corp_code},
            timeout=10,
        )
        d = resp.json()
        if d.get("status") != "000":
            return None
        return CompanyInfo(
            corp_code=corp_code,
            corp_name=d.get("corp_name", ""),
            stock_code=d.get("stock_code", ""),
            industry=d.get("induty_code", ""),
            ceo_name=d.get("ceo_nm", ""),
            address=d.get("adres", ""),
        )
    except Exception:
        return None


# ── 재무제표 ──────────────────────────────────────────────

def get_financial_statements(corp_code: str, year: str = "2023") -> FinancialData | None:
    """
    단일회사 주요 재무지표 조회
    - 매출액, 영업이익, 당기순이익, 자산총계 등
    """
    try:
        resp = requests.get(
            f"{DART_BASE}/fnlttSinglAcntAll.json",
            params={
                "crtfc_key": DART_API_KEY,
                "corp_code": corp_code,
                "bsns_year": year,
                "reprt_code": "11011",  # 사업보고서
                "fs_div": "CFS",        # 연결재무제표
            },
            timeout=15,
        )
        data = resp.json()
        if data.get("status") != "000":
            return None

        # 핵심 계정과목만 추출
        key_accounts = {"매출액", "영업이익", "당기순이익", "자산총계", "부채총계", "자본총계"}
        items = []
        for item in data.get("list", []):
            account = item.get("account_nm", "")
            if account in key_accounts:
                amount = item.get("thstrm_amount", "0").replace(",", "")
                items.append({
                    "account": account,
                    "amount": amount,
                    "unit": "원",
                })

        corp_name = data["list"][0].get("corp_name", "") if data.get("list") else ""
        return FinancialData(
            corp_name=corp_name,
            year=year,
            account_items=items,
            source_url=f"https://dart.fss.or.kr/corp/search.do?textCrpCik={corp_code}",
        )
    except Exception:
        return None


# ── 공시 목록 ─────────────────────────────────────────────

def get_recent_disclosures(corp_code: str, limit: int = 5) -> list[Disclosure]:
    """최근 공시 목록 조회"""
    try:
        resp = requests.get(
            f"{DART_BASE}/list.json",
            params={
                "crtfc_key": DART_API_KEY,
                "corp_code": corp_code,
                "pblntf_ty": "A",   # 정기공시
                "page_count": limit,
            },
            timeout=10,
        )
        data = resp.json()
        if data.get("status") != "000":
            return []

        results = []
        for item in data.get("list", [])[:limit]:
            rcept_no = item.get("rcept_no", "")
            results.append(Disclosure(
                title=item.get("report_nm", ""),
                date=item.get("rcept_dt", ""),
                url=f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}",
                corp_name=item.get("corp_name", ""),
            ))
        return results
    except Exception:
        return []


# ── 통합 조회 (파이프라인용) ──────────────────────────────

def collect_dart_data(company_name: str, year: str = "2023") -> dict:
    """
    기업명 입력 → 전체 DART 데이터 수집
    파이프라인에서 호출하는 메인 함수
    """
    result = {
        "company_name": company_name,
        "corp_code": None,
        "company_info": None,
        "financials": None,
        "disclosures": [],
        "source_urls": [],
        "error": None,
    }

    # 1. corp_code 조회
    corp_code = search_corp_code(company_name)
    if not corp_code:
        result["error"] = f"DART에서 '{company_name}' 기업코드를 찾을 수 없습니다."
        return result
    result["corp_code"] = corp_code

    # 2. 기업 기본정보
    info = get_company_info(corp_code)
    if info:
        result["company_info"] = info
        result["source_urls"].append(
            f"https://dart.fss.or.kr/corp/search.do?textCrpCik={corp_code}"
        )

    # 3. 재무제표
    financials = get_financial_statements(corp_code, year)
    if financials:
        result["financials"] = financials
        result["source_urls"].append(financials.source_url)

    # 4. 최근 공시
    disclosures = get_recent_disclosures(corp_code, limit=3)
    result["disclosures"] = disclosures
    for d in disclosures:
        result["source_urls"].append(d.url)

    return result
