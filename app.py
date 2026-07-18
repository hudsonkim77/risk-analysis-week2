"""단일 페이지 Streamlit 대시보드 (plotly.express 버전).

실행할 때마다 pipeline.build()가 raw_data/*.csv를 직접 읽어 조인·집계하며,
어떤 숫자도 하드코딩되어 있지 않다.
"""

import streamlit as st

import board_report
import pipeline
from charts_express import ALL_CHARTS

st.set_page_config(page_title="구매 협력사 성과·리스크 분석", page_icon="📊", layout="wide")

if "show_report" not in st.session_state:
    st.session_state.show_report = False

result = pipeline.build()
kpi = result["kpi"]

title_col, btn_col = st.columns([5, 2])
with title_col:
    st.title("구매 협력사 성과·리스크 분석")
with btn_col:
    st.write("")
    if st.session_state.show_report:
        if st.button("← 처음으로 돌아가기", use_container_width=True):
            st.session_state.show_report = False
            st.rerun()
    else:
        if st.button("📄 이사회 제출용 분석리포트", use_container_width=True, type="primary"):
            st.session_state.show_report = True
            st.rerun()

if st.session_state.show_report:
    board_report.render(result)
else:
    st.caption(
        "입찰공고 260건 · 비딩참여 1,193건 · 협력사 120개 · 프로젝트수행 260건 · 협력사평가이력 720건을 "
        "pandas로 조인·집계한 결과입니다. (합성 synthetic 데이터 기준)"
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("정상완료율", f"{kpi['normal_rate']}%")
    c2.metric("지연완료율", f"{kpi['delayed_rate']}%")
    c3.metric("중도해지율", f"{kpi['term_rate']}%")

    for title, chart_fn in ALL_CHARTS:
        st.subheader(title)
        fig = chart_fn(result)
        st.plotly_chart(fig, use_container_width=True)
