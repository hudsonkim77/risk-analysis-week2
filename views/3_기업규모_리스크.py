import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import data as d
import common

common.apply_style()
common.back_home_button()

st.title("3. 기업 규모별 리스크")
st.caption("협력사 규모(대기업/중견/중소/소상공인) 별 완수상태 분포")

common.stacked_status_bar(d.BY_SIZE)

common.chart_note(
    "대기업·중견기업 막대는 초록(정상완료)이 대부분이지만, 중소기업·소상공인 막대로 내려갈수록 빨강(중도해지) 구간이 "
    "눈에 띄게 두꺼워집니다. 회사 규모가 작을수록 완수 실패 위험이 뚜렷하게 커지는 그림입니다."
)

common.callout(
    "대기업(0%)·중견기업(21.1%)에 비해 <b>소상공인(48.5%), 중소기업(42.7%)</b>의 중도해지율이 "
    "2배 이상 높습니다. 다만 전체 프로젝트의 83%(216/260건)가 중소기업·소상공인에 배분되어 있어, "
    "회사 규모만으로 배제하기보다 등급·낙찰가율과 함께 보는 것이 합리적입니다."
)
