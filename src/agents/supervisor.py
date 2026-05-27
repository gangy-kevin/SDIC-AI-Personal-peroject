"""
Claude Supervisor — 분석 축 설계 에이전트 (Phase 3)

Phase 2 선행조사 결과를 입력받아:
  1. Key Driver 3개 도출
  2. KSF 3개 정의 (Key Driver 기반)
  3. 가설 3개 수립 (KSF별)
  총 9개 가설 → Phase 4 검증 대상

출력 구조:
  {
    "key_drivers": [str, str, str],
    "ksfs": [
      {
        "ksf": str,
        "key_driver": str,       # 연결된 Key Driver
        "hypotheses": [str, str, str],
      }, ...
    ],
    "analysis_summary": str,     # 전체 구조 요약
  }
"""
import json
import re
import anthropic
from src.config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL


# ── 시스템 프롬프트 ───────────────────────────────────────

SUPERVISOR_SYSTEM = """당신은 전략 컨설팅 분석 전문가(Supervisor)입니다.

선행조사 데이터를 바탕으로 아래 분석 축을 설계하세요.

## 설계 규칙

### Key Driver (3개)
- 해당 산업의 경쟁 우위를 결정짓는 핵심 동인
- 시장·기술·규제·소비자 트렌드를 종합해 도출
- 구체적이고 측정 가능한 형태로 기술

### KSF — Key Success Factor (3개)
- 각 Key Driver에서 1개씩 도출
- "~을 확보/달성/구축해야 한다" 형태로 기술
- 기업이 실제로 행동할 수 있는 수준으로 구체화

### 가설 (KSF별 3개, 총 9개)
- KSF가 달성 가능한지 검증할 수 있는 Yes/No 형태
- 반드시 검증 가능한 수치·사례·근거가 존재해야 함
- "~하다면 KSF 달성 가능하다" 또는 "~인가?" 형태

## 출력 형식 (반드시 JSON만 출력)

```json
{
  "key_drivers": [
    "Key Driver 1 내용",
    "Key Driver 2 내용",
    "Key Driver 3 내용"
  ],
  "ksfs": [
    {
      "ksf": "KSF 1 내용",
      "key_driver": "연결된 Key Driver 내용",
      "hypotheses": [
        "가설 1-1",
        "가설 1-2",
        "가설 1-3"
      ]
    },
    {
      "ksf": "KSF 2 내용",
      "key_driver": "연결된 Key Driver 내용",
      "hypotheses": [
        "가설 2-1",
        "가설 2-2",
        "가설 2-3"
      ]
    },
    {
      "ksf": "KSF 3 내용",
      "key_driver": "연결된 Key Driver 내용",
      "hypotheses": [
        "가설 3-1",
        "가설 3-2",
        "가설 3-3"
      ]
    }
  ]
}
```

JSON 외 다른 텍스트는 절대 출력하지 마세요."""


def _build_user_prompt(
    company_name: str,
    industry: str,
    core_question: str,
    research_summary: str,
) -> str:
    return f"""## 분석 대상
- 기업: {company_name}
- 산업: {industry}
- 핵심 질문: {core_question}

## 선행조사 결과 요약
{research_summary}

위 선행조사 결과를 바탕으로 Key Driver 3개, KSF 3개, 가설 9개를 JSON 형식으로 설계하세요."""


def _parse_supervisor_response(raw: str) -> dict:
    """Claude 응답에서 JSON 추출 및 파싱"""
    # 코드블록 제거
    cleaned = re.sub(r"```json\s*|\s*```", "", raw).strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # JSON 블록만 추출 시도
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            data = json.loads(match.group())
        else:
            raise ValueError(f"JSON 파싱 실패: {cleaned[:200]}")

    # 구조 검증
    assert "key_drivers" in data and len(data["key_drivers"]) == 3
    assert "ksfs" in data and len(data["ksfs"]) == 3
    for ksf_item in data["ksfs"]:
        assert "ksf" in ksf_item
        assert "hypotheses" in ksf_item and len(ksf_item["hypotheses"]) == 3

    return data


def _format_analysis_summary(data: dict, company_name: str, industry: str) -> str:
    """분석 축 구조를 사람이 읽기 좋은 텍스트로 변환"""
    lines = [
        "=" * 60,
        f"  분석 축 설계 — {company_name} / {industry}",
        "=" * 60,
        "",
    ]

    for i, kd in enumerate(data["key_drivers"], 1):
        lines.append(f"🔑 Key Driver {i}: {kd}")
    lines.append("")

    for i, ksf_item in enumerate(data["ksfs"], 1):
        lines.append(f"📌 KSF {i}: {ksf_item['ksf']}")
        lines.append(f"   └─ 연결 Driver: {ksf_item['key_driver']}")
        for j, hyp in enumerate(ksf_item["hypotheses"], 1):
            lines.append(f"   가설 {i}-{j}: {hyp}")
        lines.append("")

    total_hyp = sum(len(k["hypotheses"]) for k in data["ksfs"])
    lines.append(f"총 {total_hyp}개 가설 → Phase 4 검증 대상")

    return "\n".join(lines)


# ── 메인 실행 함수 ────────────────────────────────────────

def run_supervisor(
    company_name: str,
    industry: str,
    core_question: str,
    research_summary: str,
) -> dict:
    """
    Phase 3 Supervisor 실행

    Args:
        company_name: 분석 대상 기업명
        industry: 산업명
        core_question: 핵심 질문
        research_summary: Phase 2 선행조사 통합 요약 텍스트

    Returns:
        {
          "key_drivers": [...],
          "ksfs": [{ksf, key_driver, hypotheses}, ...],
          "analysis_summary": str,
          "error": str | None,
        }
    """
    result = {
        "key_drivers": [],
        "ksfs": [],
        "analysis_summary": "",
        "error": None,
    }

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        user_prompt = _build_user_prompt(
            company_name=company_name,
            industry=industry,
            core_question=core_question,
            research_summary=research_summary[:3000],  # 토큰 절감
        )

        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2000,
            system=SUPERVISOR_SYSTEM,
            messages=[{"role": "user", "content": user_prompt}],
        )

        raw_text = response.content[0].text
        data = _parse_supervisor_response(raw_text)

        result["key_drivers"] = data["key_drivers"]
        result["ksfs"] = data["ksfs"]
        result["analysis_summary"] = _format_analysis_summary(
            data, company_name, industry
        )

    except Exception as e:
        result["error"] = str(e)
        result["analysis_summary"] = f"[Supervisor 오류] {e}"

    return result
