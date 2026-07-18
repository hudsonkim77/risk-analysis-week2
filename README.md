# 구매 협력사 성과·리스크 분석 (2주차)

구매(조달) 5종 합성(synthetic) CSV 데이터를 pandas로 조인·집계하고, Streamlit 멀티페이지 앱으로
분석 결과와 개선 제언을 제공하는 대시보드입니다.

- **데이터**: 입찰공고 260건 · 비딩참여 1,193건 · 프로젝트수행 260건 · 협력사 120개 · 협력사평가이력 720건
- **분석(1~7)**: 저가입찰, 신용등급, 기업규모, 업종별 리스크 / 평가지표 추이 / 신용도-해지율 상관 / 고위험 워치리스트
- **제언(8~10)**: 협력사 리스크 스코어링 모델 / 저가입찰 제도 개선안 / 실행 로드맵

## 구조

```
app.py              진입점 - st.navigation으로 페이지 라우팅
pipeline.py          pandas 데이터 파이프라인 (raw_data/*.csv → 조인·집계·리스크 스코어링)
data.py              pipeline 결과를 앱 전역 상수로 노출
common.py            공통 스타일, 차트, 표 컴포넌트
raw_data/            원본 CSV 5종
views/               페이지별 화면 (0_home ~ 10_실행_로드맵)
```

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 데이터 안내

`raw_data/`의 CSV는 합성(synthetic) 데이터이며 실제 기업·거래 정보가 아닙니다.
