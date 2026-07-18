import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import data as d
import common

common.apply_style()
common.back_home_button()

st.title("9. 저가 입찰 제도 개선안")
st.caption("1번 분석(저가 입찰의 위험)에서 확인된 최대 리스크 요인에 대한 제도적 대응")

st.markdown(
    "낙찰가율 0.85 미만 구간의 중도해지율(53.4%)은 적정가 구간(17.4%)의 3배입니다. "
    "이는 개별 협력사의 일탈이 아니라 <b>&quot;최저가만으로 낙찰자를 정하는 현재 입찰 구조&quot;가 만들어내는 "
    "구조적 결과</b>로 해석하는 것이 맞습니다. 협력사 개별 관리(8번 스코어링)만으로는 신규 저가 입찰이 "
    "계속 유입되는 것을 막지 못하므로, 제도 자체를 바꾸는 3가지 방안을 제안합니다.",
    unsafe_allow_html=True,
)

st.markdown("### 제안 1 · 이상저가 심사제 도입")
st.markdown(
    "- 낙찰가율이 <b>0.85 미만</b>인 입찰 건은 낙찰 확정 전 <b>원가 소명자료 제출을 의무화</b>하고, "
    "구매팀·현업부서 합동 심사위원회의 사전 승인을 거치도록 합니다.\n"
    "- 소명이 불충분한 경우 차순위 적격 협력사로 낙찰자를 변경할 수 있는 근거 조항을 계약 특수조건에 명시합니다.\n"
    "- 공공조달의 &quot;저가심의/이상저가 판단 기준&quot;과 유사한 개념으로, 이미 여러 발주기관에서 운영 중인 "
    "제도적 선례가 있습니다.",
    unsafe_allow_html=True,
)

st.markdown("### 제안 2 · 낙찰가율 연동 차등 이행보증")
st.table(
    {
        "낙찰가율 구간": ["0.95 이상 (적정가)", "0.85 ~ 0.95", "0.85 미만 (저가입찰)"],
        "현재 관행": ["표준 이행보증 10%", "표준 이행보증 10%", "표준 이행보증 10%"],
        "제안": ["표준 이행보증 10% 유지", "이행보증 15%로 상향", "이행보증 30% + 이행보증보험 가입 의무"],
        "실제 해지율": ["17.4%", "35.6%", "53.4%"],
    }
)
st.caption("낙찰가율이 낮을수록 원가 압박이 커진다는 전제 하에, 위험도에 비례해 이행 담보 수준을 높이는 구조입니다.")

st.markdown("### 제안 3 · 최저가낙찰제 → 가중평가 낙찰제 전환")
st.markdown(
    "- 가격 단독 기준 대신 <b>가격 60% + 협력사 평가등급(신용도·품질·납기) 30% + 재무건전성 10%</b>의 "
    "가중합산 방식으로 낙찰자를 결정합니다.\n"
    "- 이미 확보된 &quot;협력사평가이력&quot; 데이터를 낙찰 심사에 그대로 활용할 수 있어 추가 데이터 구축 없이 "
    "즉시 적용 가능합니다.\n"
    "- 최초 신용등급 <b>BB 이하</b>는 원가 소명 없이도 자동으로 이상저가 심사 대상에 포함시켜 8번 스코어링 모델과 "
    "연계합니다.",
    unsafe_allow_html=True,
)

st.markdown("### 예상 임팩트 (일러스트레이션)")

current_total_term = 104
low_bid_n, low_bid_actual_term = 88, 47
low_bid_healthy_rate = 17.4
projected_low_bid_term = round(low_bid_n * low_bid_healthy_rate / 100)
saved = low_bid_actual_term - projected_low_bid_term
new_total_term = current_total_term - saved
new_rate = round(new_total_term / d.KPI["total_projects"] * 100, 1)

common.impact_scenario_chart(d.KPI["term_rate"], new_rate)

common.callout(
    f"저가입찰(&lt;0.85) 88건의 해지율이 적정가 구간 수준(17.4%)까지 낮아진다면, 해지 건수는 "
    f"{low_bid_actual_term}건 → {projected_low_bid_term}건(약 {saved}건 감소)이 되어 "
    f"전체 중도해지율은 <b>{d.KPI['term_rate']}% → 약 {new_rate}%</b>로 개선될 수 있다는 계산입니다. "
    "<br><br><b>주의:</b> 이는 상관관계에 기반한 산술적 시나리오이며 인과관계를 증명한 값이 아닙니다. "
    "저가입찰 협력사가 애초에 재무 여력이 약해 낮은 금액을 부를 수밖에 없었을 가능성(역인과)도 배제할 수 없으므로, "
    "제도 도입 후 실제 효과는 별도로 추적·검증해야 합니다."
)
