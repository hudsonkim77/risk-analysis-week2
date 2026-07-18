import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import data as d
import common

common.apply_style()
common.back_home_button()

st.title("4. 업종별 리스크")
st.caption("전문분야(카테고리) 별 완수상태 분포 · 해지율 높은 순")

common.stacked_status_bar(d.BY_CAT)

common.chart_note(
    "해지율이 높은 순으로 정렬했더니 건설/설비가 맨 위에서 빨강 비중이 가장 크고, 아래로 내려갈수록 초록이 늘어나는 "
    "뚜렷한 기울기가 나타납니다. 디자인/광고 같은 무형 서비스 업종이 가장 아래, 즉 가장 안전한 쪽에 위치합니다."
)

common.callout(
    "<b>건설/설비(52.8%)</b>가 가장 높은 중도해지율을 보이고, <b>디자인/광고(34.1%)</b>가 상대적으로 낮습니다. "
    "물리적 시공·자재 조달이 얽힌 업종일수록 외부 변수(원자재가, 현장 여건)에 취약해 해지율이 높게 나타나는 것으로 보입니다."
)
