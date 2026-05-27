"""
SDIC 산업 분석 도구 — Streamlit 메인 앱
실행: .venv/bin/streamlit run src/ui/app.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from src.ui.components import (
    render_header,
    render_input_form,
    render_agent_results,
    render_supervisor_results,
    render_error,
    render_validation_warning,
)
from src.pipeline.orchestrator import run_preliminary_research
from src.agents.supervisor import run_supervisor

# ── 페이지 설정 ───────────────────────────────────────────
st.set_page_config(
    page_title="SDIC 산업 분석",
    page_icon="🔍",
    layout="wide",
)


# ── 메인 ─────────────────────────────────────────────────
def main():
    render_header()

    # 입력 폼
    inputs = render_input_form()

    if inputs is None:
        st.info("기업명·산업·핵심 질문을 입력하고 분석을 시작하세요.")
        return

    # 입력값 검증
    missing = [k for k, v in inputs.items() if k != "year" and not v]
    if missing:
        labels = {"company_name": "기업명", "industry": "산업", "core_question": "핵심 질문"}
        render_validation_warning([labels[m] for m in missing])
        return

    # ── Step 1: 선행 조사 ────────────────────────────────
    with st.spinner("🔄 Step 1 — 4개 에이전트 선행 조사 중... (1~3분 소요)"):
        try:
            aggregated = run_preliminary_research(
                company_name=inputs["company_name"],
                industry=inputs["industry"],
                core_question=inputs["core_question"],
                year=inputs["year"],
            )
        except Exception as e:
            render_error(f"선행 조사 중 오류 발생: {e}")
            return

    render_agent_results(aggregated)
    st.divider()

    # ── Step 2: 분석 축 설계 ─────────────────────────────
    with st.spinner("🧠 Step 2 — Key Driver·KSF·가설 설계 중..."):
        try:
            supervisor = run_supervisor(
                company_name=inputs["company_name"],
                industry=inputs["industry"],
                core_question=inputs["core_question"],
                research_summary=aggregated.get("combined_summary", ""),
            )
        except Exception as e:
            render_error(f"분석 축 설계 중 오류 발생: {e}")
            return

    render_supervisor_results(supervisor)
    st.divider()

    # ── 완료 메시지 ──────────────────────────────────────
    total_hyp = sum(len(k["hypotheses"]) for k in supervisor.get("ksfs", []))
    st.success(
        f"✅ 분석 완료 — "
        f"Key Driver {len(supervisor.get('key_drivers', []))}개 · "
        f"KSF {len(supervisor.get('ksfs', []))}개 · "
        f"가설 {total_hyp}개 도출"
    )
    st.caption("⚠️ Step 3(가설 검증) · Step 4(So What) · Step 5(세션 저장)은 개발 중입니다.")


if __name__ == "__main__":
    main()
