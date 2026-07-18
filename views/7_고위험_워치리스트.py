import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import data as d
import common

common.apply_style()
common.back_home_button()

st.title("7. 고위험 협력사 워치리스트")
st.caption("리스크 스코어링 모델(8번) 상위 5개사 — 스코어와 실제 해지 이력이 동시에 뒷받침되는 협력사만 선정")

st.markdown(
    "해지 이력이 있는 협력사를 모두 나열하면 15개사 대부분이 &quot;진행 1건 중 1건 해지(=100%)&quot;로 "
    "찍혀 비슷비슷해 보이고, 정작 어떤 협력사를 먼저 봐야 하는지가 묻힙니다. 그래서 표본이 1건뿐인 우연한 사례는 "
    "제외하고, <b>프로젝트 2건 이상을 수행했고 그중 실제 해지가 있었던</b> 협력사 중 8번 모델의 리스크 스코어가 "
    "가장 높은 5개사만 실명(협력사ID)과 세부 지표를 함께 보여줍니다.",
    unsafe_allow_html=True,
)

st.write("")
common.scoreboard(d.WATCHLIST)

common.chart_note(
    "5개사 중 3곳이 물류/운송 업종이고 나머지도 모두 소상공인·중소기업입니다. 낙찰가율은 5곳 모두 0.85 안팎으로 낮고 "
    "최초 신용등급도 BB 이하 — 8번 스코어링 모델이 짚어낸 위험 신호가 실제 해지 이력과 정확히 겹칩니다."
)

common.callout(
    "1위 <b>V005</b>는 수행한 3개 프로젝트가 전부 중도해지된 최고위험 협력사(스코어 60.1)입니다. "
    "5개사 모두 신규 계약 전 임원 승인과 이행보증보험 가입을 우선 적용하고, 착수 후 30/60/90일 마일스톤 검수 등 "
    "조기 경보 체계를 이 5개사부터 시범 적용할 것을 제안합니다."
)

with st.expander("중도해지 이력 보유 협력사 전체 목록 보기 (15개사, 표본 1건 포함)"):
    st.caption("해지율 100%이지만 진행 프로젝트가 1건뿐인 협력사도 포함된 전체 목록입니다. 참고용으로만 활용하세요.")
    common.risk_table()
