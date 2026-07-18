"""pandas 기반 데이터 파이프라인.

raw_data/*.csv (구매 5종 합성 데이터)를 읽어 조인·집계하고,
Streamlit 앱(data.py)이 그대로 쓸 수 있는 구조로 반환한다.
이전에는 PowerShell로 미리 집계한 JSON을 읽는 방식이었으나,
과제 요구사항에 맞춰 pandas 조인/집계 파이프라인으로 전면 교체했다.
"""

import os

import pandas as pd

_DIR = os.path.dirname(os.path.abspath(__file__))
_RAW = os.path.join(_DIR, "raw_data")

GRADE_ORDER = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC"]
STATUS_COLS = ["정상완료", "지연완료", "중도해지"]

SCORING_WEIGHTS = {"낙찰가율": 0.35, "신용등급": 0.30, "기업규모": 0.20, "업종": 0.15}


def _read(name):
    return pd.read_csv(os.path.join(_RAW, name), encoding="utf-8-sig")


def load_raw():
    return {
        "rfp": _read("구매_입찰공고.csv"),
        "bid": _read("구매_비딩참여.csv"),
        "proj": _read("구매_프로젝트수행.csv"),
        "vendor": _read("구매_협력사.csv"),
        "eval": _read("구매_협력사평가이력.csv"),
    }


def _status_breakdown(df, group_col):
    """group_col 기준 정상완료/지연완료/중도해지 건수·비율 집계."""
    g = df.groupby(group_col)["완수상태"].value_counts().unstack(fill_value=0)
    for col in STATUS_COLS:
        if col not in g.columns:
            g[col] = 0
    g = g[STATUS_COLS]
    g["total"] = g.sum(axis=1)
    g["termRate"] = (g["중도해지"] / g["total"] * 100).round(1)
    return g


def build():
    raw = load_raw()
    rfp, bid, proj, vendor, eval_ = raw["rfp"], raw["bid"], raw["proj"], raw["vendor"], raw["eval"]

    # ---- 낙찰(winning) 비딩만 추려서 프로젝트에 조인: 프로젝트별 실제 낙찰가율 확보 ----
    won_bids = bid[bid["낙찰여부"] == "낙찰"][["공고ID", "협력사ID", "낙찰가율"]]
    proj_j = (
        proj.merge(rfp[["공고ID", "카테고리"]], on="공고ID", how="left")
        .merge(vendor[["협력사ID", "규모", "전문분야", "최초신용등급"]], on="협력사ID", how="left")
        .merge(won_bids, on=["공고ID", "협력사ID"], how="left")
        .rename(columns={"낙찰가율": "bidRatio", "규모": "size", "카테고리": "category",
                          "최초신용등급": "initialGrade"})
    )

    # ---- KPI ----
    status_counts = proj["완수상태"].value_counts()
    kpi = {
        "total_rfp": int(len(rfp)),
        "total_bids": int(len(bid)),
        "total_vendors": int(len(vendor)),
        "total_projects": int(len(proj)),
        "overall_win_rate": round((bid["낙찰여부"] == "낙찰").sum() / len(bid) * 100, 1),
        "avg_contract_amount_eok": round(proj["계약금액"].mean() / 1e8, 2),
        "normal_rate": round(status_counts.get("정상완료", 0) / len(proj) * 100, 1),
        "delayed_rate": round(status_counts.get("지연완료", 0) / len(proj) * 100, 1),
        "term_rate": round(status_counts.get("중도해지", 0) / len(proj) * 100, 1),
    }

    # ---- 규모 / 업종 / 신용등급 별 완수상태 ----
    by_size = _status_breakdown(proj_j, "size").reset_index().rename(columns={"size": "key"})
    by_size = by_size.sort_values("total", ascending=False)

    by_cat = _status_breakdown(proj_j, "category").reset_index().rename(columns={"category": "key"})
    by_cat = by_cat.sort_values("termRate", ascending=False)

    by_grade = _status_breakdown(proj_j, "initialGrade").reset_index().rename(columns={"initialGrade": "key"})
    by_grade["key"] = pd.Categorical(by_grade["key"], categories=GRADE_ORDER, ordered=True)
    by_grade = by_grade.sort_values("key").dropna(subset=["key"])
    by_grade["key"] = by_grade["key"].astype(str)

    # ---- 낙찰가율 구간별 완수상태 ----
    bins = [0, 0.85, 0.95, 1.05, 1.15, 999]
    labels = ["< 0.85 (저가입찰)", "0.85 ~ 0.95", "0.95 ~ 1.05", "1.05 ~ 1.15", ">= 1.15"]
    proj_j["bidBucket"] = pd.cut(proj_j["bidRatio"], bins=bins, labels=labels, right=False)
    by_bid_ratio = _status_breakdown(proj_j.dropna(subset=["bidBucket"]), "bidBucket")
    by_bid_ratio = by_bid_ratio[by_bid_ratio["total"] > 0].reset_index().rename(columns={"bidBucket": "key"})
    by_bid_ratio["key"] = by_bid_ratio["key"].astype(str)

    # ---- 평가지표 반기 추이 ----
    trend = (
        eval_.groupby("평가시기")[["신용도점수", "품질점수", "납기준수율"]]
        .mean().round(1).reset_index().rename(columns={"평가시기": "period"})
    )
    period_order = sorted(trend["period"].unique())
    trend["period"] = pd.Categorical(trend["period"], categories=period_order, ordered=True)
    trend = trend.sort_values("period")
    trend["period"] = trend["period"].astype(str)

    # ---- 벤더 롤업: 평가 평균, 프로젝트 통계, 입찰/낙찰 ----
    eval_avg = eval_.groupby("협력사ID")[["신용도점수", "품질점수", "납기준수율"]].mean().round(1)
    eval_avg.columns = ["avgCredit", "avgQuality", "avgDelivery"]

    proj_stats = proj_j.groupby("협력사ID").agg(
        projects=("완수상태", "count"),
        terminated=("완수상태", lambda s: (s == "중도해지").sum()),
    )
    proj_stats["termRate"] = (proj_stats["terminated"] / proj_stats["projects"] * 100).round(1)

    bid_ratio_by_vendor = proj_j.groupby("협력사ID")["bidRatio"].mean().round(3)

    bid_stats = bid.groupby("협력사ID").agg(bids=("입찰ID", "count"), wins=("낙찰여부", lambda s: (s == "낙찰").sum()))
    bid_stats["winRate"] = (bid_stats["wins"] / bid_stats["bids"] * 100).round(1)

    grade_2023h1 = eval_[eval_["평가시기"] == "2023H1"].set_index("협력사ID")["종합등급"]
    grade_2025h2 = eval_[eval_["평가시기"] == "2025H2"].set_index("협력사ID")["종합등급"]

    roll = (
        vendor.set_index("협력사ID")[["전문분야", "규모", "최초신용등급"]]
        .join(eval_avg).join(proj_stats).join(bid_stats)
    )
    roll["gradeStart"] = grade_2023h1
    roll["gradeEnd"] = grade_2025h2
    roll["avgBidRatio"] = bid_ratio_by_vendor
    roll = roll.rename(columns={"전문분야": "specialty", "규모": "size", "최초신용등급": "initialGrade"})
    roll[["projects", "terminated"]] = roll[["projects", "terminated"]].fillna(0).astype(int)

    active = roll[roll["projects"] > 0].copy()

    median_credit = round(active["avgCredit"].median(), 1)

    scatter = active.reset_index().rename(columns={"협력사ID": "id"})[
        ["id", "avgCredit", "termRate", "projects", "size"]
    ]

    risk_vendors = (
        active[active["terminated"] >= 1]
        .sort_values(["termRate", "projects"], ascending=[False, False])
        .head(15)
        .reset_index().rename(columns={"협력사ID": "id"})
    )

    # ---- 리스크 스코어링: 4개 요인을 각 구간의 "실측 해지율"로 환산해 가중합산 ----
    bid_rate_map = {
        "< 0.85 (저가입찰)": 53.4, "0.85 ~ 0.95": 35.6, "0.95 ~ 1.05": 17.4,
    }

    def bid_score(r):
        if pd.isna(r):
            return None
        if r < 0.85:
            return bid_rate_map["< 0.85 (저가입찰)"]
        if r < 0.95:
            return bid_rate_map["0.85 ~ 0.95"]
        if r < 1.05:
            return bid_rate_map["0.95 ~ 1.05"]
        return 10.0  # 관측치 없는 구간에 대한 보수적 외삽값

    grade_rate = dict(zip(by_grade["key"], by_grade["termRate"]))
    size_rate = dict(zip(by_size["key"], by_size["termRate"]))
    cat_rate = dict(zip(by_cat["key"], by_cat["termRate"]))

    scored = active[active["initialGrade"].isin(grade_rate)].copy()
    scored["riskScore"] = (
        SCORING_WEIGHTS["낙찰가율"] * scored["avgBidRatio"].apply(bid_score)
        + SCORING_WEIGHTS["신용등급"] * scored["initialGrade"].map(grade_rate)
        + SCORING_WEIGHTS["기업규모"] * scored["size"].map(size_rate)
        + SCORING_WEIGHTS["업종"] * scored["specialty"].map(cat_rate)
    ).round(1)
    scored = scored.dropna(subset=["riskScore"])

    q1, q2, q3 = scored["riskScore"].quantile([0.25, 0.5, 0.75]).round(1)

    def tier_of(score):
        if score >= q3:
            return "Critical"
        if score >= q2:
            return "High"
        if score >= q1:
            return "Medium"
        return "Low"

    scored["tier"] = scored["riskScore"].apply(tier_of)
    vendor_scores = scored.reset_index().rename(columns={"협력사ID": "id"})[
        ["id", "specialty", "size", "initialGrade", "avgCredit", "avgBidRatio",
         "projects", "terminated", "termRate", "riskScore", "tier"]
    ]

    backtest = (
        scored.groupby("tier").agg(n=("riskScore", "count"), actualTermRate=("termRate", "mean"))
        .round(1).reset_index()
    )
    tier_order = ["Critical", "High", "Medium", "Low"]
    backtest["tier"] = pd.Categorical(backtest["tier"], categories=tier_order, ordered=True)
    backtest = backtest.sort_values("tier").reset_index(drop=True)
    backtest["tier"] = backtest["tier"].astype(str)

    # ---- 워치리스트: 실제 해지 이력(projects>=2, terminated>=1)이 있는 협력사 중
    #      리스크 스코어 상위 5개사. 표본이 1건뿐인 "우연한 100% 해지"를 걸러내고,
    #      모델 스코어와 실제 이력이 함께 뒷받침되는 협력사만 남긴다. ----
    credible = scored[(scored["projects"] >= 2) & (scored["terminated"] >= 1)]
    watchlist = (
        credible.sort_values("riskScore", ascending=False)
        .head(5)
        .reset_index().rename(columns={"협력사ID": "id"})[
            ["id", "specialty", "size", "initialGrade", "avgCredit", "avgBidRatio",
             "projects", "terminated", "termRate", "riskScore", "tier"]
        ]
    )

    return {
        "kpi": kpi,
        "by_size": by_size.to_dict("records"),
        "by_cat": by_cat.to_dict("records"),
        "by_grade": by_grade.to_dict("records"),
        "by_bid_ratio": by_bid_ratio.to_dict("records"),
        "trend": trend.to_dict("records"),
        "scatter": scatter.to_dict("records"),
        "risk_vendors": risk_vendors.to_dict("records"),
        "vendor_scores": vendor_scores.to_dict("records"),
        "median_credit": median_credit,
        "scoring_cutoffs": {"q1": float(q1), "q2": float(q2), "q3": float(q3)},
        "scoring_backtest": backtest.to_dict("records"),
        "watchlist": watchlist.to_dict("records"),
    }
