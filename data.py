"""구매(조달) 5개 CSV 조인 분석 결과.

원본: raw_data/구매_입찰공고.csv(260) / 구매_비딩참여.csv(1,193) / 구매_프로젝트수행.csv(260)
      / 구매_협력사.csv(120) / 구매_협력사평가이력.csv(720)
합성(synthetic) 데이터 기준.

pipeline.py(pandas)가 raw_data의 CSV를 직접 읽어 조인·집계·리스크 스코어링까지
전부 수행하고, 이 모듈은 그 결과를 앱 전역에서 쓰기 좋은 이름으로 노출만 한다.
"""

import pipeline

_result = pipeline.build()

# ---- 색상 (dataviz 팔레트: 상태 3색 + 카테고리컬 8색 중 일부) ----
STATUS_COLORS = {
    "정상완료": "#0ca30c",   # good
    "지연완료": "#fab219",   # warning
    "중도해지": "#d03b3b",   # critical
}
SIZE_COLORS = {
    "대기업": "#2a78d6",     # blue
    "중견기업": "#008300",   # green
    "중소기업": "#e87ba4",   # magenta
    "소상공인": "#eda100",   # yellow
}
TREND_COLORS = {
    "신용도점수": "#2a78d6",  # blue
    "품질점수": "#1baf7a",   # aqua
    "납기준수율": "#4a3aa7",  # violet
}
TIER_COLORS = {
    "Critical": "#d03b3b",
    "High": "#eb6834",
    "Medium": "#fab219",
    "Low": "#0ca30c",
}
TIER_ORDER = ["Critical", "High", "Medium", "Low"]

KPI = _result["kpi"]

BY_BID_RATIO = _result["by_bid_ratio"]
BY_GRADE = _result["by_grade"]
BY_SIZE = _result["by_size"]
BY_CAT = _result["by_cat"]
TREND = _result["trend"]
SCATTER = _result["scatter"]              # 프로젝트 1건 이상 수행한 협력사 전체
RISK_VENDORS = _result["risk_vendors"]    # 중도해지 이력 보유 상위 15개사
VENDOR_SCORES = _result["vendor_scores"]  # 리스크 스코어링 모델 산출 결과
WATCHLIST = _result["watchlist"]          # 실적+스코어 동시 검증된 상위 5개사 (7번 스코어보드)

MEDIAN_CREDIT = _result["median_credit"]

# ---- 리스크 스코어링 모델 메타데이터 (8번 리포트에서 사용) ----
SCORING_WEIGHTS = pipeline.SCORING_WEIGHTS
SCORING_RATE_TABLES = {
    "낙찰가율": {"< 0.85": 53.4, "0.85 ~ 0.95": 35.6, "0.95 ~ 1.05": 17.4, ">= 1.05 (관측치 없음, 외삽)": 10.0},
    "신용등급": {row["key"]: row["termRate"] for row in BY_GRADE},
    "기업규모": {row["key"]: row["termRate"] for row in BY_SIZE},
    "업종": {row["key"]: row["termRate"] for row in BY_CAT},
}
# 쿼타일 기반 등급 컷오프 (스코어 분포 25/50/75 percentile, pandas로 매번 재계산)
SCORING_CUTOFFS = _result["scoring_cutoffs"]
# 백테스트: 티어별 실제 평균 중도해지율 (모델이 실제로 구분력이 있는지 검증)
SCORING_BACKTEST = _result["scoring_backtest"]

# ---- 처음 페이지에 노출할 분석 항목 메타데이터 ----
ANALYSIS_ITEMS = [
    {
        "no": 1,
        "title": "저가 입찰의 위험",
        "subtitle": "낙찰가율 구간별 완수상태",
        "kind": "분석",
        "headline": "저가입찰(<0.85) 중도해지율 53.4% — 적정가 구간의 3배",
    },
    {
        "no": 2,
        "title": "신용등급별 리스크",
        "subtitle": "최초 신용등급 AAA~CCC 별 완수상태",
        "kind": "분석",
        "headline": "AAA 0% → CCC 100%, 등급과 해지율의 선형 관계",
    },
    {
        "no": 3,
        "title": "기업 규모별 리스크",
        "subtitle": "대기업/중견/중소/소상공인 별 완수상태",
        "kind": "분석",
        "headline": "소상공인 48.5% vs 대기업 0%",
    },
    {
        "no": 4,
        "title": "업종별 리스크",
        "subtitle": "전문분야(카테고리) 별 완수상태",
        "kind": "분석",
        "headline": "건설/설비 52.8%로 최다 리스크 업종",
    },
    {
        "no": 5,
        "title": "협력사 평가지표 추이",
        "subtitle": "2023H1~2025H2 반기별 평균 점수",
        "kind": "분석",
        "headline": "신용도점수 6개 반기 연속 하락 (63.5 → 58.8)",
    },
    {
        "no": 6,
        "title": "신용도 vs 중도해지율",
        "subtitle": "협력사 99개 산점도",
        "kind": "분석",
        "headline": "중앙값 미만 구간에 해지 사례 밀집",
    },
    {
        "no": 7,
        "title": "고위험 협력사 워치리스트",
        "subtitle": "리스크 스코어 상위 5개사 스코어카드",
        "kind": "분석",
        "headline": "물류/운송 3개사 포함 — 모델 예측과 실제 해지 이력이 겹치는 Top 5",
    },
    {
        "no": 8,
        "title": "협력사 리스크 스코어링 모델",
        "subtitle": "4개 요인 가중합산 → 99개사 등급화 + 백테스트",
        "kind": "제언",
        "headline": "Critical 등급 실제 해지율 59.4% vs Low 등급 17.4%",
    },
    {
        "no": 9,
        "title": "저가 입찰 제도 개선안",
        "subtitle": "이상저가 심사 · 차등 이행보증 · 가중평가 낙찰제",
        "kind": "제언",
        "headline": "최저가낙찰 구조를 바꾸지 않으면 해지율은 반복된다",
    },
    {
        "no": 10,
        "title": "리스크 관리 실행 로드맵",
        "subtitle": "90일 실행계획 · 거버넌스 · 재무적 임팩트",
        "kind": "제언",
        "headline": "40% → 2년 내 25% 목표, 단계별 실행안",
    },
]
