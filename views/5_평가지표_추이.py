import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import data as d
import common

common.apply_style()
common.back_home_button()

st.title("5. 협력사 평가지표 추이")
st.caption("2023H1 ~ 2025H2, 전체 협력사 반기 평균 점수")

common.trend_line_chart()

common.callout(
    "평균 신용도점수가 2023H1 63.5점에서 2025H2 58.8점으로 <b>6개 반기 연속 하락</b>했습니다. "
    "품질·납기준수율은 71~76점대에서 큰 변동 없이 유지되어, 협력사 풀 전반의 재무 건전성이 서서히 약화되는 "
    "추세로 읽힙니다."
)
