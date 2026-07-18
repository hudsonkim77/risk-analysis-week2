import streamlit as st

st.set_page_config(page_title="구매 협력사 성과·리스크 분석", page_icon="📊", layout="wide")

pages = [
    st.Page("views/0_home.py", title="처음으로", icon="🏠", default=True),
    st.Page("views/1_저가입찰_리스크.py", title="저가 입찰 리스크", icon="📉"),
    st.Page("views/2_신용등급_리스크.py", title="신용등급별 리스크", icon="🏷️"),
    st.Page("views/3_기업규모_리스크.py", title="기업 규모별 리스크", icon="🏢"),
    st.Page("views/4_업종별_리스크.py", title="업종별 리스크", icon="🧭"),
    st.Page("views/5_평가지표_추이.py", title="평가지표 추이", icon="📈"),
    st.Page("views/6_신용도_vs_해지율.py", title="신용도 vs 해지율", icon="🔎"),
    st.Page("views/7_고위험_워치리스트.py", title="고위험 워치리스트", icon="⚠️"),
    st.Page("views/8_리스크_스코어링_모델.py", title="리스크 스코어링 모델", icon="🧮"),
    st.Page("views/9_입찰제도_개선안.py", title="입찰제도 개선안", icon="📝"),
    st.Page("views/10_실행_로드맵.py", title="실행 로드맵", icon="🗺️"),
]

nav = st.navigation(pages, position="hidden")
nav.run()
