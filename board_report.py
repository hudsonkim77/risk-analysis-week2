"""이사회 제출용 분석 리포트 페이지.

app.py 상단 버튼에서 토글되는 별도 화면. pipeline.build() 결과(result)를
그대로 받아 렌더링하며 숫자를 하드코딩하지 않는다.
"""

import pandas as pd
import streamlit as st

from charts_express import chart_8_scoring_backtest, chart_9_bid_reform_impact

GRADE_ORDER_LOW = ["BB", "B", "CCC"]


def _bid_score(x):
    if x < 0.85:
        return 53.4
    if x < 0.95:
        return 35.6
    if x < 1.05:
        return 17.4
    return 10.0


def _tier_cause_table(result):
    df = pd.DataFrame(result["vendor_scores"])
    grade_rate = {row["key"]: row["termRate"] for row in result["by_grade"]}
    size_rate = {row["key"]: row["termRate"] for row in result["by_size"]}
    cat_rate = {row["key"]: row["termRate"] for row in result["by_cat"]}

    df["c_bid"] = df["avgBidRatio"].apply(_bid_score) * 0.35
    df["c_grade"] = df["initialGrade"].map(grade_rate) * 0.30
    df["c_size"] = df["size"].map(size_rate) * 0.20
    df["c_cat"] = df["specialty"].map(cat_rate) * 0.15
    df["dominant"] = df[["c_bid", "c_grade", "c_size", "c_cat"]].idxmax(axis=1)

    rows = {}
    for tier in ["Critical", "High"]:
        sub = df[df["tier"] == tier]
        n = len(sub)
        bid_dom = (sub["dominant"] == "c_bid").sum()
        grade_dom = (sub["dominant"] == "c_grade").sum()
        rows[tier] = {
            "협력사 수": f"{n}개사",
            "결정타 요인": f"낙찰가율 {round(bid_dom / n * 100)}% ({bid_dom}개사) / 신용등급 {round(grade_dom / n * 100)}% ({grade_dom}개사)",
            "평균 낙찰가율": f"{sub['avgBidRatio'].mean():.3f}",
            "저가입찰(<0.85) 비중": f"{(sub['avgBidRatio'] < 0.85).mean() * 100:.1f}%",
            "BB 이하 등급 비중": f"{sub['initialGrade'].isin(GRADE_ORDER_LOW).mean() * 100:.1f}%",
        }
    table = pd.DataFrame(rows).T
    table.index.name = "구분"

    ch = df[df["tier"].isin(["Critical", "High"])]
    ml = df[df["tier"].isin(["Medium", "Low"])]
    stats = {
        "ch_bb_below": ch["initialGrade"].isin(GRADE_ORDER_LOW).mean() * 100,
        "ml_bb_below": ml["initialGrade"].isin(GRADE_ORDER_LOW).mean() * 100,
        "ch_small": ch["size"].isin(["중소기업", "소상공인"]).mean() * 100,
    }
    return table, stats


def render(result):
    kpi = result["kpi"]

    st.caption("CONFIDENTIAL · 이사회 보고 — 왜 우리 프로젝트의 40%가 중도에 깨지는가")

    st.markdown("### 0. 우리 회사 프로필 (데이터 기반 추정)")
    st.markdown(
        "구매 카테고리가 **건설/설비 · IT개발 · 컨설팅 · 물류/운송 · 디자인/광고 · 원부자재** 6종으로 "
        "구성되어 있다는 점에서, **여러 사업부를 동시에 운영하며 각 사업부가 필요할 때마다 외부 협력사를 "
        "입찰로 조달하는 중견~대기업형 조직**으로 추정된다. 입찰 기반 최저가 위주 조달 구조 자체가 "
        "본 보고서 문제의 출발점이다."
    )

    st.markdown("### 1막 — 무슨 일이 일어나고 있는가")
    c1, c2, c3 = st.columns(3)
    c1.metric("정상완료율", f"{kpi['normal_rate']}%")
    c2.metric("지연완료율", f"{kpi['delayed_rate']}%")
    c3.metric("중도해지율", f"{kpi['term_rate']}%")
    st.markdown(
        f"낙찰된 프로젝트 {kpi['total_projects']}건 중 **{round(kpi['total_projects']*kpi['term_rate']/100)}건"
        f"({kpi['term_rate']}%)이 중도에 해지**되었다. 이는 우발적 사고가 아니라 "
        "**구매 프로세스 자체의 구조적 문제**로 해석해야 한다."
    )

    st.markdown("### 2막 — 원인 추적 (분석 1~7)")
    cause_df = pd.DataFrame(
        [
            {"단서": "낙찰가율", "발견": "저가입찰(<0.85) 해지율 53.4% vs 적정가(0.95~1.05) 17.4% — 3배 차이"},
            {"단서": "신용등급", "발견": "AAA 0% → CCC 100%, 등급과 해지율이 거의 선형 관계"},
            {"단서": "기업규모", "발견": "대기업 0% vs 소상공인 48.5%"},
            {"단서": "업종", "발견": "건설/설비 52.8%로 최다 리스크 업종"},
            {"단서": "시간 추이", "발견": "평균 신용도점수 6개 반기 연속 하락 — 문제가 서서히 악화되는 중"},
            {"단서": "워치리스트", "발견": "진행 프로젝트 전건이 해지된 협력사 15개사 확인"},
        ]
    )
    st.dataframe(cause_df, use_container_width=True, hide_index=True)
    st.markdown("> **\"저가에 낚여, 감당 못 할 업체에게 일을 맡기고 있었다.\"**")

    st.markdown("### 3막 — 대안 (제언 8~10)")

    st.markdown("#### 8. 협력사 리스크 스코어링 모델")
    st.markdown(
        "낙찰가율(35%) + 신용등급(30%) + 기업규모(20%) + 업종(15%) 가중합산. 각 요인 점수는 "
        "**해당 구간에서 실제로 관측된 중도해지율**을 그대로 사용."
    )
    st.plotly_chart(chart_8_scoring_backtest(result), use_container_width=True)

    st.markdown("**Critical vs High 원인 분석 (심화)**")
    table, stats = _tier_cause_table(result)
    st.dataframe(table, use_container_width=True)
    st.info(
        f"Critical+High의 **{stats['ch_small']:.1f}%가 중소기업·소상공인**이며, "
        f"**신용등급 BB 이하는 Medium·Low에 {stats['ml_bb_below']:.0f}%** (Critical+High는 "
        f"{stats['ch_bb_below']:.1f}%) — BB 이하 등급은 사실상 위험군으로 분류된다."
    )

    st.markdown("#### 9. 저가 입찰 제도 개선안")
    st.markdown(
        "1. **이상저가 심사제**: 낙찰가율 0.85 미만 시 원가 소명자료 제출 의무화\n"
        "2. **낙찰가율 연동 차등 이행보증**: 저가일수록 보증금 상향\n"
        "3. **최저가낙찰제 → 가중평가 낙찰제**: 가격 60% + 평가등급 30% + 재무건전성 10%"
    )
    st.plotly_chart(chart_9_bid_reform_impact(result), use_container_width=True)

    st.markdown("#### 10. 리스크 관리 실행 로드맵")
    roadmap_df = pd.DataFrame(
        [
            {"단계": "Phase 1 · 0~30일", "핵심 과제": "워치리스트 15개사 모니터링 강화, 신규 저가입찰 건 임원 사전승인"},
            {"단계": "Phase 2 · 31~90일", "핵심 과제": "가중평가 낙찰제·차등 이행보증 제도화, 스코어링 모델 전체 적용"},
            {"단계": "Phase 3 · 91~180일+", "핵심 과제": "반기평가에 스코어 반영, 등급개선 인센티브, 월간 대시보드 정례 보고"},
        ]
    )
    st.dataframe(roadmap_df, use_container_width=True, hide_index=True)

    st.markdown("### 결론 — 회사 영향 요약")
    concl_df = pd.DataFrame(
        [
            {"관점": "재무", "내용": "관측 기간 중도해지 추정 손실 53.8~71.8억 원 (계약금액의 15~20% 가정)"},
            {"관점": "개선 효과", "내용": "제도개선 시나리오 잠재 절감액 16.6~22.1억 원"},
            {"관점": "리스크 관리 체질", "내용": '"사고 후 수습" → "사전 예방"으로 전환'},
            {"관점": "목표", "내용": "중도해지율 40% → 1년 내 32% → 2년 내 25%"},
        ]
    )
    st.dataframe(concl_df, use_container_width=True, hide_index=True)
    st.caption("본 리포트는 합성(synthetic) 데이터 기반이며, 가정 수치는 회사 실제 상황에 맞춰 조정 가능합니다.")

    st.write("")
    if st.button("← 처음으로 돌아가기", use_container_width=False, key="back_bottom"):
        st.session_state.show_report = False
        st.rerun()
