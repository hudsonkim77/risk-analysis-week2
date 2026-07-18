import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import data as d
import common

common.apply_style()
common.back_home_button()

st.title("2. 신용등급별 리스크")
st.caption("협력사 최초 신용등급(AAA → CCC) 별 완수상태 분포")

common.stacked_status_bar(d.BY_GRADE)

common.chart_note(
    "AAA부터 CCC까지 등급이 낮아질수록 막대의 빨강(중도해지) 비중이 계단식으로 커집니다. "
    "중간 어딘가에서 갑자기 튀는 구간 없이 등급 순서 그대로 해지율이 늘어나는, 매우 깨끗한 선형 패턴입니다."
)

common.callout(
    "AAA(0%) → AA(15.4%) → A(36.4%) → BBB(37.5%) → BB(51.7%) → B(48.6%) → CCC(100%, 3건 중 3건)로 "
    "신용등급과 해지율이 거의 선형적으로 움직입니다. 협력사 선정 시 <b>최초 신용등급 BB 이하</b>는 "
    "별도 리스크 관리(계약 이행보증, 단계별 검수 강화)가 필요해 보입니다."
)
