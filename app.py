"""구매 협력사 성과·리스크 분석 — 단일 페이지 아코디언 대시보드.

실행할 때마다 pipeline.build()가 raw_data/*.csv를 직접 읽어 조인·집계하며,
어떤 숫자도 하드코딩되어 있지 않다. 분석 항목 10개는 별도 페이지로 이동하지 않고
"열기"를 누르면 카드 바로 아래에서 펼쳐지고(sections.py), "닫기"를 누르면 접힌다.
"""

import streamlit as st

import common
import data as d
from sections import SECTION_FNS

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

common.apply_style()

st.title("구매 협력사 성과·리스크 분석")
st.caption(
    "입찰공고 260건 · 비딩참여 1,193건 · 협력사 120개 · 프로젝트수행 260건 · 협력사평가이력 720건을 "
    "조인해 분석한 결과입니다. (합성 synthetic 데이터 기준)"
)

k = d.KPI
cols = st.columns(6)
tiles = [
    ("입찰공고 / 협력사", f"{k['total_rfp']} / {k['total_vendors']}", None),
    ("평균 낙찰률", f"{k['overall_win_rate']}%", None),
    ("평균 계약금액", f"{k['avg_contract_amount_eok']}억", None),
    ("정상완료율", f"{k['normal_rate']}%", "#0ca30c"),
    ("지연완료율", f"{k['delayed_rate']}%", "#c98500"),
    ("중도해지율", f"{k['term_rate']}%", "#d03b3b"),
]
for c, (label, value, color) in zip(cols, tiles):
    with c:
        value_style = f"color:{color};" if color else ""
        st.markdown(
            f'<div class="kpi-card"><div class="label">{label}</div>'
            f'<div class="value" style="{value_style}">{value}</div></div>',
            unsafe_allow_html=True,
        )

st.write("")
st.subheader("분석 항목")
st.caption("항목의 '열기'를 누르면 그 자리에서 세부 내용이 펼쳐집니다. 파란 배지는 데이터 분석, 보라 배지는 제언·컨설팅 리포트입니다.")

for item in d.ANALYSIS_ITEMS:
    no = item["no"]
    state_key = f"open_{no}"
    if state_key not in st.session_state:
        st.session_state[state_key] = False
    is_open = st.session_state[state_key]

    with st.container(border=True):
        c1, c2 = st.columns([5, 1])
        with c1:
            badge_color = common.ACCENT[item["kind"]]
            st.markdown(
                f'<span class="kind-badge" style="background:{badge_color}1e;color:{badge_color};">'
                f'{item["kind"]}</span>'
                f'<span class="item-num">{no}</span>'
                f'<b>{item["title"]}</b>  ·  {item["subtitle"]}',
                unsafe_allow_html=True,
            )
            st.caption(item["headline"])
        with c2:
            label = "닫기 ✕" if is_open else "열기 →"
            if st.button(label, key=f"toggle_{no}", width="stretch"):
                st.session_state[state_key] = not is_open
                st.rerun()

        if is_open:
            st.divider()
            SECTION_FNS[no]()
