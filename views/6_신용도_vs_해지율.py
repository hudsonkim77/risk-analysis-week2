import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import data as d
import common

common.apply_style()
common.back_home_button()

st.title("6. 신용도 vs 중도해지율")
st.caption("프로젝트 1건 이상 수행한 협력사 99개, 규모별 색상 구분")

common.scatter_credit_vs_term()

common.callout(
    f"평균 신용도점수가 <b>중앙값({d.MEDIAN_CREDIT}점) 미만</b>인 협력사군에 해지 사례가 집중돼 있습니다(좌상단 밀집). "
    "다만 고신용(80점 이상)에서도 해지가 발생해 신용도만으로는 완전히 설명되지 않으며, 낙찰가율과 함께 보는 "
    "복합 리스크 스코어링을 권장합니다.",
    good=True,
)
