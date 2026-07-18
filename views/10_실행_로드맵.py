import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import data as d
import common

common.apply_style()
common.back_home_button()

st.title("10. 리스크 관리 실행 로드맵")
st.caption("8·9번의 진단·제도개선을 실제 조직 운영에 붙이기 위한 단계별 실행안 · 거버넌스 · 재무적 임팩트")

st.markdown("### 단계별 실행 계획")
st.table(
    {
        "단계": ["Phase 1 · 0~30일 (즉시 실행)", "Phase 2 · 31~90일", "Phase 3 · 91~180일 이후"],
        "핵심 과제": [
            "고위험 워치리스트 15개사 모니터링 강화 · 신규 저가입찰(<0.85) 건 임원 사전승인 임시 적용",
            "가중평가 낙찰제·차등 이행보증 제도화(9번) · 리스크 스코어링 모델(8번) 전체 협력사 적용 및 자동화",
            "반기 협력사평가 프로세스에 스코어 반영 · 등급개선 인센티브(우수협력사 우선협상권) 도입 · 월간 대시보드 정례 보고",
        ],
    }
)

st.markdown("### 거버넌스")
st.table(
    {
        "구분": ["운영 주체", "모니터링 주기", "에스컬레이션 기준"],
        "내용": [
            "구매팀(1차 관리) + 리스크관리팀(스코어링 모델 운영) + 재무팀(이행보증·소명자료 심사) 협의체",
            "Critical 등급: 월간 / High: 분기 / Medium·Low: 반기(정기평가 주기와 동일)",
            "스코어 Critical 신규 진입 또는 진행 중 계약의 지연 징후 포착 시 48시간 내 구매담당 임원 보고",
        ],
    }
)

st.markdown("### KPI 목표 (일러스트레이션)")
periods = ["현재 (관측치)", "1년 후 목표", "2년 후 목표"]
targets = [d.KPI["term_rate"], 32.0, 25.0]
common.kpi_target_chart(periods, targets)
st.caption(
    "선행지표: 저가입찰(<0.85) 비중(현재 88/260=33.8%), 반기 평균 신용도점수(현재 58.8점, 하락 추세 반전 여부) · "
    "후행지표: 중도해지율, 지연완료율"
)

st.markdown("### 재무적 임팩트 (가정 기반 추정)")
terminated = 104
avg_amount = d.KPI["avg_contract_amount_eok"]
low, high = 0.15, 0.20
cost_low = round(terminated * avg_amount * low, 1)
cost_high = round(terminated * avg_amount * high, 1)
saved_low = round(32 * avg_amount * low, 1)
saved_high = round(32 * avg_amount * high, 1)

c1, c2 = st.columns(2)
with c1:
    st.markdown(
        f'<div class="kpi-card"><div class="label">관측 기간 중도해지 추정 손실</div>'
        f'<div class="value">{cost_low}~{cost_high}억</div>'
        f'<div style="font-size:0.78rem;opacity:0.6;margin-top:4px;">재입찰·지연 비용을 계약금액의 15~20%로 가정</div></div>',
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f'<div class="kpi-card"><div class="label">9번 제도개선 시나리오의 잠재 절감액</div>'
        f'<div class="value">{saved_low}~{saved_high}억</div>'
        f'<div style="font-size:0.78rem;opacity:0.6;margin-top:4px;">저가입찰 구간 해지 32건 감소 가정 기준</div></div>',
        unsafe_allow_html=True,
    )

common.callout(
    "위 금액은 실제 회계 데이터가 아니라 <b>계약금액 대비 15~20%라는 가정</b>을 적용한 추정치입니다. "
    "실제 재입찰 소요 비용, 지연에 따른 기회비용, 품질 저하 비용 등을 재무팀과 함께 실측해 이 가정을 "
    "교체하는 것을 다음 단계 과제로 제안합니다."
)
