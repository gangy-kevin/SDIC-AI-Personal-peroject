"""
재사용 UI 컴포넌트
"""
import streamlit as st


def render_header():
    st.title("🔍 SDIC 산업 분석 도구")
    st.caption("전략 컨설팅 선행조사 → KSF·가설 설계 자동화")
    st.divider()


def render_input_form():
    """사용자 입력 폼. 입력값 dict 반환"""
    with st.form("input_form"):
        st.subheader("📋 분석 정보 입력")

        company_name = st.text_input(
            "기업명",
            placeholder="예: LG디스플레이, Tesla",
        )
        industry = st.text_input(
            "산업",
            placeholder="예: 차량용 디스플레이, 전기차 배터리",
        )
        core_question = st.text_area(
            "핵심 질문",
            placeholder="예: LGD가 차량용 OLED 시장에서 중국 경쟁사 대비 지속 성장 가능한가?",
            height=90,
        )
        year = st.selectbox("기준 연도", ["2024", "2023", "2022"], index=1)

        submitted = st.form_submit_button("🚀 분석 시작", use_container_width=True)

    if submitted:
        return {
            "company_name": company_name.strip(),
            "industry": industry.strip(),
            "core_question": core_question.strip(),
            "year": year,
        }
    return None


def render_agent_results(aggregated: dict):
    """Step 1 — 4개 에이전트 결과 표시"""
    st.subheader("📊 Step 1 — 선행 조사 결과")

    agents = aggregated.get("agents", {})
    icons = {
        "market_size": "📈",
        "competitor":  "🏢",
        "regulation":  "⚖️",
        "trend":       "🌐",
    }
    labels = {
        "market_size": "시장규모",
        "competitor":  "경쟁사",
        "regulation":  "규제",
        "trend":       "트렌드",
    }

    # 신뢰도 요약 카드
    cols = st.columns(4)
    for i, (agent_type, data) in enumerate(agents.items()):
        with cols[i]:
            icon = icons.get(agent_type, "•")
            label = labels.get(agent_type, agent_type)
            badge = data.score_badge if data.score_badge else "—"
            status = "✅" if not data.error else "❌"
            st.metric(label=f"{icon} {label}", value=badge, delta=status)

    st.caption(
        f"총 출처 {len(aggregated.get('all_source_urls', []))}개 수집 · "
        f"평균 신뢰도 {aggregated.get('avg_score', 0)}점"
    )

    # 에이전트별 상세 요약 (접기/펼치기)
    for agent_type, data in agents.items():
        icon = icons.get(agent_type, "•")
        label = labels.get(agent_type, agent_type)
        with st.expander(f"{icon} {label} 상세 내용"):
            if data.error:
                st.error(f"오류: {data.error}")
            else:
                st.text(data.summary)


def render_supervisor_results(supervisor: dict):
    """Step 2 — Key Driver·KSF·가설 표시"""
    st.subheader("🧠 Step 2 — 분석 축 설계")

    if supervisor.get("error"):
        st.error(f"Supervisor 오류: {supervisor['error']}")
        return

    # Key Drivers
    st.markdown("#### 🔑 Key Driver")
    for i, kd in enumerate(supervisor.get("key_drivers", []), 1):
        st.info(f"**{i}.** {kd}")

    st.markdown("---")

    # KSF + 가설
    st.markdown("#### 📌 KSF · 가설")
    for i, ksf_item in enumerate(supervisor.get("ksfs", []), 1):
        with st.expander(f"KSF {i}: {ksf_item['ksf']}", expanded=True):
            st.caption(f"연결 Key Driver: {ksf_item.get('key_driver', '')}")
            for j, hyp in enumerate(ksf_item.get("hypotheses", []), 1):
                st.markdown(f"- **가설 {i}-{j}:** {hyp}")


def render_error(message: str):
    st.error(message)


def render_validation_warning(fields: list[str]):
    st.warning(f"다음 항목을 입력해주세요: {', '.join(fields)}")
