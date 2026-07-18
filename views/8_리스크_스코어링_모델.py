import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import data as d
import common

common.apply_style()
common.back_home_button()

st.title("8. 협력사 리스크 스코어링 모델")
st.caption("1~7번 분석에서 확인된 4개 위험요인을 하나의 점수로 통합 — 99개사 대상 등급화 + 백테스트")

st.markdown("#### 모델 개요")
st.markdown(
    "협력사 1곳의 <b>중도해지 위험도</b>를 4개 요인의 가중합으로 산출합니다. 각 요인의 점수는 "
    "임의의 값이 아니라, <b>해당 구간에서 실제로 관측된 중도해지율</b>을 그대로 사용합니다 "
    "(예: 낙찰가율 0.85 미만 구간의 요인점수 = 그 구간의 실제 해지율인 53.4점). "
    "즉 &#39;이 협력사가 위험군에 속하는 정도&#39;를 과거 데이터의 실제 실패율로 직접 환산하는 방식입니다.",
    unsafe_allow_html=True,
)

common.weights_chart()

st.markdown(
    "<b>가중치 근거</b>: 낙찰가율(35%)과 신용등급(30%)은 구간별 해지율 격차가 가장 크고 표본도 충분해 "
    "가장 신뢰도 높은 신호로 판단했습니다. 기업규모(20%)는 격차는 크지만 대기업 표본이 6건으로 적어 "
    "다소 낮춰 반영했고, 업종(15%)은 상대적으로 격차가 작아 보조 신호로만 사용했습니다.",
    unsafe_allow_html=True,
)

st.markdown("#### 점수 분포 (99개사)")
common.score_distribution_chart()
st.caption("Q1(33.8) / 중앙값(38.5) / Q3(44.4) 4분위 컷오프로 Low·Medium·High·Critical 4개 등급을 나눴습니다.")

st.markdown("#### 백테스트 — 이 모델이 실제로 구분력이 있는가?")
common.backtest_chart()
common.callout(
    "등급을 <b>실제 중도해지율</b>과 대조한 결과, Critical(59.4%) → High(42.4%) → Medium(38.6%) → "
    "Low(17.4%) 순으로 단조 감소해 모델이 실제 리스크를 상당히 잘 구분해냄을 확인했습니다. "
    "다만 이 점수는 <b>모델을 만든 바로 그 데이터로 검증한 것</b>이라 표본 외 검증(다음 분기 신규 계약 대상)이 "
    "필요하며, High·Medium 구간의 차이(42.4% vs 38.6%)는 상대적으로 좁아 두 등급의 정책은 유사하게 가져가도 무방합니다.",
    good=True,
)

st.markdown("#### Critical 등급 협력사 (전체)")
common.critical_tier_table()

st.markdown("#### 등급별 권장 대응")
st.table(
    {
        "등급": ["Critical", "High", "Medium", "Low"],
        "권장 조치": [
            "신규 계약 전 임원 승인 필수 · 이행보증보험 의무화(계약금액 30% 이상) · 월간 모니터링",
            "계약이행보증금 상향(15~20%) · 착수 후 분기별 현장 점검",
            "표준 이행보증(10%) + 반기 정기평가로 관리",
            "표준 절차 유지, 우수 실적 시 우선협상 대상자 후보로 고려",
        ],
    }
)

common.callout(
    "이 모델은 상관관계 기반 휴리스틱 스코어카드로, <b>인과관계를 증명하지 않습니다</b>. "
    "예를 들어 낙찰가율이 낮은 협력사가 애초에 재무 여력이 약해 낮게 부를 수밖에 없었을 가능성도 있습니다. "
    "따라서 스코어는 &quot;누구를 먼저, 더 자세히 볼 것인가&quot;를 정하는 우선순위 도구로 쓰고, "
    "계약 거절의 단독 근거로 사용하지 않을 것을 권장합니다."
)
