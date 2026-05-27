"""
URL fetch + 본문 추출 모듈
- URL에서 실제 본문 텍스트 추출
- 수치 존재 여부 검증 (할루시네이션 방지 핵심)
"""
import re
import httpx
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class FetchResult:
    url: str
    success: bool
    text: str          # 추출된 본문 텍스트
    title: str
    error: str = ""


def fetch_url(url: str, timeout: int = 15) -> FetchResult:
    """URL에서 본문 텍스트 추출"""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8",
    }
    try:
        with httpx.Client(follow_redirects=True, timeout=timeout) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")

        # 불필요한 태그 제거
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()

        title = soup.title.string.strip() if soup.title else ""
        text = soup.get_text(separator=" ", strip=True)
        # 연속 공백 정리
        text = re.sub(r"\s+", " ", text).strip()

        return FetchResult(url=url, success=True, text=text, title=title)

    except Exception as e:
        return FetchResult(url=url, success=False, text="", title="", error=str(e))


def verify_value_in_text(value: str, text: str) -> bool:
    """
    수치/키워드가 본문에 실제로 존재하는지 검증
    할루시네이션 방지 핵심 함수
    예) value="3조 2천억", text="...매출 3조 2천억원 기록..."
    """
    if not value or not text:
        return False
    # 숫자 정규화 후 검색
    normalized_value = re.sub(r"\s+", "", value)
    normalized_text = re.sub(r"\s+", "", text)
    return normalized_value in normalized_text


def extract_numbers_from_text(text: str) -> list[str]:
    """본문에서 수치 패턴 추출 (검증용)"""
    # 한국어 수치 패턴: 조, 억, 만 단위
    patterns = [
        r"\d+[,\d]*\.?\d*\s*(?:조|억|만|천)?\s*(?:원|달러|%|위안)?",
        r"\d+\.?\d*\s*(?:trillion|billion|million|%)",
    ]
    results = []
    for pattern in patterns:
        results.extend(re.findall(pattern, text))
    return list(set(results))
