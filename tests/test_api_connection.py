"""
API 연동 연결 테스트
실행: .venv/bin/python tests/test_api_connection.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.settings import ANTHROPIC_API_KEY, DART_API_KEY, CLAUDE_MODEL, validate_keys


def test_env_keys():
    """환경변수 로드 확인"""
    print("\n" + "="*50)
    print("🔑 API 키 설정 상태 확인")
    print("="*50)
    status = validate_keys()
    for name, ok in status.items():
        icon = "✅" if ok else "❌"
        print(f"  {icon} {name.upper()}_API_KEY: {'설정됨' if ok else '미설정 (.env 확인 필요)'}")
    print()
    return all(status.values())


def test_anthropic_connection():
    """Anthropic Claude API 연결 테스트"""
    print("🤖 Anthropic Claude API 연결 테스트")
    print("-"*50)
    if not ANTHROPIC_API_KEY:
        print("  ❌ ANTHROPIC_API_KEY 미설정 — 건너뜀\n")
        return False

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=50,
            messages=[{"role": "user", "content": "ping"}],
        )
        response = message.content[0].text
        print(f"  ✅ 연결 성공 | 모델: {CLAUDE_MODEL}")
        print(f"  응답: {response[:50]}\n")
        return True
    except Exception as e:
        print(f"  ❌ 연결 실패: {e}\n")
        return False


def test_dart_connection():
    """DART Open API 연결 테스트 (삼성전자 기업정보)"""
    print("📊 DART Open API 연결 테스트")
    print("-"*50)
    if not DART_API_KEY:
        print("  ❌ DART_API_KEY 미설정 — 건너뜀\n")
        return False

    try:
        import requests
        url = "https://opendart.fss.or.kr/api/company.json"
        params = {
            "crtfc_key": DART_API_KEY,
            "corp_code": "00126380",  # 삼성전자
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        if data.get("status") == "000":
            corp_name = data.get("corp_name", "")
            print(f"  ✅ 연결 성공 | 조회 기업: {corp_name}\n")
            return True
        else:
            print(f"  ❌ API 오류: {data.get('message', '')}\n")
            return False
    except Exception as e:
        print(f"  ❌ 연결 실패: {e}\n")
        return False


def test_imports():
    """핵심 라이브러리 import 확인"""
    print("📦 핵심 라이브러리 import 확인")
    print("-"*50)
    libraries = [
        ("anthropic", "Anthropic SDK"),
        ("langgraph", "LangGraph"),
        ("streamlit", "Streamlit"),
        ("httpx", "httpx"),
        ("sqlite_utils", "sqlite-utils"),
        ("pydantic", "Pydantic"),
        ("bs4", "BeautifulSoup4"),
        ("dotenv", "python-dotenv"),
    ]
    all_ok = True
    for module, name in libraries:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            all_ok = False
    print()
    return all_ok


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  환경 세팅 확인 테스트")
    print("="*50)

    results = {
        "imports": test_imports(),
        "env_keys": test_env_keys(),
        "anthropic": test_anthropic_connection(),
        "dart": test_dart_connection(),
    }

    print("="*50)
    print("📋 최종 결과")
    print("="*50)
    all_passed = all(results.values())
    for name, ok in results.items():
        icon = "✅" if ok else "⚠️ "
        print(f"  {icon} {name}")

    print()
    if all_passed:
        print("🎉 모든 테스트 통과 — 개발 시작 가능!")
    else:
        print("⚠️  일부 항목 확인 필요 (API 키가 없으면 연결 테스트는 건너뜁니다)")
    print()
