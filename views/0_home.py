import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import data as d
import common

common.apply_style()

st.title("구매 협력사 성과 · 리스크 분석")
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
st.caption("항목을 클릭하면 해당 리포트로 이동합니다. 파란 배지는 데이터 분석, 보라 배지는 제언·컨설팅 리포트입니다.")

for item in d.ANALYSIS_ITEMS:
    with st.container(border=True):
        c1, c2 = st.columns([5, 1])
        with c1:
            badge_color = common.ACCENT[item["kind"]]
            st.markdown(
                f'<span class="kind-badge" style="background:{badge_color}1e;color:{badge_color};">'
                f'{item["kind"]}</span>'
                f'<span class="item-num">{item["no"]}</span>'
                f'<b>{item["title"]}</b>  ·  {item["subtitle"]}',
                unsafe_allow_html=True,
            )
            st.caption(item["headline"])
        with c2:
            st.page_link(item["page"], label="열기 →")
