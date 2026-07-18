import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import data as d
import common

common.apply_style()
common.back_home_button()

st.title("1. 저가 입찰의 위험")
st.caption("낙찰가율 = 낙찰금액 / 발주 예정가 — 구간별 완수상태 분포")

common.stacked_status_bar(d.BY_BID_RATIO)

common.chart_note(
    "막대를 왼쪽에서 오른쪽으로 보면 낙찰가율이 오를수록 빨강(중도해지)이 줄고 초록(정상완료)이 늘어나는 흐름이 보입니다. "
    "특히 &lt;0.85 구간만 빨강 비중이 절반을 넘어, 이 구간에서 완수 실패가 유독 몰려 있음을 한눈에 알 수 있습니다."
)

common.callout(
    "<b>낙찰가율 0.85 미만(저가 낙찰)</b> 프로젝트는 <b>중도해지율 53.4%</b>로, "
    "적정가 구간(0.95~1.05, 17.4%)의 <b>3배</b>에 달합니다. 예정가 대비 지나치게 낮은 금액으로 "
    "낙찰된 협력사가 실제 수행 단계에서 원가를 감당하지 못하고 이탈하는 &quot;승자의 저주&quot; 패턴으로 해석됩니다."
)
