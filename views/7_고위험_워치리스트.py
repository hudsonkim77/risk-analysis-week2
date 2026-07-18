import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import data as d
import common

common.apply_style()
common.back_home_button()

st.title("7. 고위험 협력사 워치리스트")
st.caption("진행 프로젝트 전건 중도해지 이력 보유, 해지율 높은 순 상위 15개사")

common.risk_table()

common.callout(
    "15개사 모두 진행한 프로젝트가 <b>전건 중도해지</b>로 종결되었습니다. 초기 계약 시 이행보증 보험 가입, "
    "착수 후 30/60/90일 단위 마일스톤 검수 등 조기 경보 체계를 우선 적용할 대상입니다."
)
