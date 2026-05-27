"""
Claude 웹서치 모듈
- Anthropic Claude API의 web_search 도구 활용
- 신뢰 소스 필터 적용
- URL fetch 본문 대조 검증 포함
"""
import anthropic
from dataclasses import dataclass, field
from src.config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL
from src.config.trusted_sources import is_trusted_source, get_trusted_domains_str
from src.tools.url_fetcher import fetch_url, verify_value_in_text


@dataclass
class SearchResult:
    query: str
    content: str                        # Claude가 합성한 답변
    sources: list[dict] = field(default_factory=list)   # [{url, title, trusted}]
    trusted_count: int = 0
    verified_values: list[str] = field(default_factory=list)  # 본문 검증 통과한 수치들


def search_with_claude(
    query: str,
    context: str = "",
    require_trusted: bool = True,
    max_results: int = 5,
) -> SearchResult:
    """
    Claude 웹서치 실행
    - query: 검색 질문
    - context: 추가 컨텍스트 (KSF, 분석 목적 등)
    - require_trusted: 신뢰 소스 필터 적용 여부
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    trusted_domains = get_trusted_domains_str()

    system_prompt = f"""당신은 전략 컨설팅 리서치 전문가입니다.

다음 규칙을 반드시 준수하세요:
1. 수치를 인용할 때는 해당 수치가 실제로 출처 본문에 존재하는지 반드시 확인하세요.
2. 확인되지 않은 수치는 절대 인용하지 마세요.
3. 가능하면 아래 신뢰 소스에서 정보를 수집하세요:
{trusted_domains}
4. 각 주장에는 반드시 출처 URL을 명시하세요.
5. 2년 이내(2023년 이후) 데이터를 우선 사용하세요.

응답 형식:
- 핵심 내용을 명확하게 정리
- 수치는 [출처: URL] 형식으로 출처 명시
- 불확실한 정보는 "확인 필요" 표시"""

    user_message = query
    if context:
        user_message = f"분석 맥락: {context}\n\n검색 질문: {query}"

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2000,
            system=system_prompt,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": user_message}],
        )

        # 응답 텍스트 추출
        content_text = ""
        sources = []

        for block in response.content:
            if block.type == "text":
                content_text += block.text
            elif hasattr(block, "type") and block.type == "tool_result":
                # 웹서치 결과에서 URL 추출
                pass

        # tool_use 결과에서 소스 URL 추출
        for block in response.content:
            if hasattr(block, "input") and isinstance(getattr(block, "input", None), dict):
                url = block.input.get("url", "")
                if url:
                    trusted = is_trusted_source(url)
                    sources.append({"url": url, "title": "", "trusted": trusted})

        trusted_count = sum(1 for s in sources if s["trusted"])

        return SearchResult(
            query=query,
            content=content_text,
            sources=sources,
            trusted_count=trusted_count,
        )

    except Exception as e:
        return SearchResult(
            query=query,
            content=f"검색 오류: {str(e)}",
            sources=[],
            trusted_count=0,
        )


def search_and_verify(
    query: str,
    values_to_verify: list[str] | None = None,
    context: str = "",
) -> SearchResult:
    """
    웹서치 + URL fetch 본문 대조 검증
    - values_to_verify: 본문 존재 여부를 검증할 수치 리스트
    """
    result = search_with_claude(query=query, context=context)

    if not values_to_verify or not result.sources:
        return result

    # 각 소스 URL fetch 후 수치 존재 검증
    verified = []
    for value in values_to_verify:
        for source in result.sources:
            url = source.get("url", "")
            if not url:
                continue
            fetch_result = fetch_url(url)
            if fetch_result.success and verify_value_in_text(value, fetch_result.text):
                verified.append(value)
                break

    result.verified_values = verified
    return result
