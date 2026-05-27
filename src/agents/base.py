"""
에이전트 공통 베이스 dataclass
모든 에이전트 Result 클래스가 상속하는 공통 필드 정의
"""
from dataclasses import dataclass, field


@dataclass
class BaseAgentResult:
    agent: str = ""
    company_name: str = ""
    industry: str = ""
    year: str = ""
    summary: str = ""
    source_urls: list[str] = field(default_factory=list)
    score_badge: str = ""
    score_total: int = 0
    error: str = ""
