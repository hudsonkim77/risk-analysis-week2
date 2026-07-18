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

common.chart_note(
    "점 하나가 협력사 1곳입니다. 점선(중앙값) 왼쪽에 해지율 높은 점들이 몰려 있고, 점선 오른쪽은 해지율 0%에 가까운 "
    "점이 대부분입니다. 다만 오른쪽에도 해지율이 튄 점이 몇 개 섞여 있어 신용도 하나로 완전히 나뉘진 않습니다."
)

common.callout(
    f"평균 신용도점수가 <b>중앙값({d.MEDIAN_CREDIT}점) 미만</b>인 협력사군에 해지 사례가 집중돼 있습니다(좌상단 밀집). "
    "다만 고신용(80점 이상)에서도 해지가 발생해 신용도만으로는 완전히 설명되지 않으며, 낙찰가율과 함께 보는 "
    "복합 리스크 스코어링을 권장합니다.",
    good=True,
)
