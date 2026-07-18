"""단일 페이지 Streamlit 대시보드 (plotly.express 버전, 다크·네온 테마).

실행할 때마다 pipeline.build()가 raw_data/*.csv를 직접 읽어 조인·집계하며,
어떤 숫자도 하드코딩되어 있지 않다.
"""

import streamlit as st

import board_report
import pipeline
from charts_express import ALL_CHARTS

st.set_page_config(page_title="구매 협력사 성과·리스크 분석", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
    h1 {
        text-shadow: 0 0 6px rgba(204,255,0,0.55), 0 0 18px rgba(204,255,0,0.25);
    }
    [data-testid="stMetricValue"] {
        color: #CCFF00;
        text-shadow: 0 0 8px rgba(204,255,0,0.6), 0 0 20px rgba(204,255,0,0.25);
    }
    [data-testid="stMetricLabel"] { color: #9FE870; }
    h2, h3 {
        text-shadow: 0 0 4px rgba(204,255,0,0.3);
    }
    .stButton > button {
        border: 1px solid rgba(204,255,0,0.5);
        font-weight: 700;
        transition: box-shadow .15s ease, border-color .15s ease;
    }
    .stButton > button:hover {
        border-color: #CCFF00;
        box-shadow: 0 0 10px rgba(204,255,0,0.6), 0 0 24px rgba(204,255,0,0.25);
        color: #CCFF00;
    }
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        color: #06210f !important;
        font-weight: 800 !important;
        text-shadow: none;
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        color: #06210f !important;
    }
    div[data-testid="stMetric"] {
        background: rgba(204,255,0,0.05);
        border: 1px solid rgba(204,255,0,0.18);
        border-radius: 10px;
        padding: 10px 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
