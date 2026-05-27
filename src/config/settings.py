"""
전역 설정 및 환경변수 로드
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트 기준 .env 로드
ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(ROOT_DIR / ".env")


# ── API Keys ──────────────────────────────────────────────
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
DART_API_KEY: str = os.getenv("DART_API_KEY", "")

# ── Claude 모델 ───────────────────────────────────────────
CLAUDE_MODEL: str = "claude-haiku-4-5"

# ── 파이프라인 상수 ───────────────────────────────────────
MAX_LOOPBACK: int = 2           # 가설 재조사 최대 횟수
MAX_AGENTS: int = 4             # 선행조사 병렬 에이전트 수
KEY_DRIVER_COUNT: int = 3       # Key Driver 수
KSF_COUNT: int = 3              # KSF 수
HYPOTHESIS_PER_KSF: int = 3     # KSF별 가설 수

# ── 신뢰도 점수 가중치 ────────────────────────────────────
SCORE_WEIGHTS = {
    "has_url": 25,          # 출처 URL 존재 여부
    "body_match": 35,       # fetch 본문 일치 여부
    "trusted_source": 25,   # 신뢰 소스 필터 해당 여부
    "cross_source": 15,     # 교차 출처 수 (최대 2개 이상)
}

# ── SQLite 경로 ───────────────────────────────────────────
DB_PATH: Path = ROOT_DIR / "data" / "sessions.db"
DB_PATH.parent.mkdir(exist_ok=True)


def validate_keys() -> dict[str, bool]:
    """API 키 설정 여부 확인"""
    return {
        "anthropic": bool(ANTHROPIC_API_KEY),
        "dart": bool(DART_API_KEY),
    }
