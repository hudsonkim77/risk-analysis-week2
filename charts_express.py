"""plotly.express 버전 차트 10종.

pipeline.build()가 raw_data/*.csv를 직접 읽어 조인·집계한 결과(dict)를 받아
각 리포트를 대표하는 차트 하나씩을 plotly.express로 그린다.
막대 형태 차트는 전부 px.bar를 사용하고, 모든 차트는 hover에 수치가
뜨도록 hover_data/hover_name을 명시했다.
"""

import pandas as pd
import plotly.express as px

STATUS_COLS = ["정상완료", "지연완료", "중도해지"]
STATUS_COLORS = {"정상완료": "#0ca30c", "지연완료": "#fab219", "중도해지": "#d03b3b"}
SIZE_COLORS = {"대기업": "#2a78d6", "중견기업": "#008300", "중소기업": "#e87ba4", "소상공인": "#eda100"}
TIER_COLORS = {"Critical": "#d03b3b", "High": "#eb6834", "Medium": "#fab219", "Low": "#0ca30c"}
TIER_ORDER = ["Critical", "High", "Medium", "Low"]


def _y_label(fig, text):
    """Plotly가 한글 y축 제목을 세로로 한 글자씩 쌓아 렌더링하는 문제를 피하기 위해
    회전된 axis title 대신 좌상단 가로 주석으로 대체한다."""
    fig.update_layout(yaxis_title=None)
    fig.add_annotation(
        text=text, x=0, y=1.1, xref="paper", yref="paper",
        showarrow=False, xanchor="left", font=dict(size=12, color="#898781"),
    )
    return fig


def _status_long(rows):
    """[{key,total,정상완료,지연완료,중도해지,termRate}, ...] -> long-form df (px.bar용)."""
    df = pd.DataFrame(rows)
    long = df.melt(id_vars=["key", "total", "termRate"], value_vars=STATUS_COLS,
                    var_name="완수상태", value_name="건수")
    long["비율(%)"] = (long["건수"] / long["total"] * 100).round(1)
    return long


def _stacked_status_bar(rows):
    long = _status_long(rows)
    fig = px.bar(
        long, x="비율(%)", y="key", color="완수상태", orientation="h",
        color_discrete_map=STATUS_COLORS,
        category_orders={"완수상태": STATUS_COLS},
        hover_data={"key": True, "완수상태": True, "건수": True, "비율(%)": ":.1f", "total": True},
    )
    fig.update_layout(
        barmode="stack", yaxis_title=None, xaxis_title="비중 (%)",
        legend_title_text="완수상태", height=120 + 55 * len(rows),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def chart_1_bid_ratio(result):
    return _stacked_status_bar(result["by_bid_ratio"])


def chart_2_grade(result):
    return _stacked_status_bar(result["by_grade"])


def chart_3_size(result):
    return _stacked_status_bar(result["by_size"])


def chart_4_category(result):
    return _stacked_status_bar(result["by_cat"])


def chart_5_trend(result):
    df = pd.DataFrame(result["trend"])
    long = df.melt(id_vars="period", value_vars=["신용도점수", "품질점수", "납기준수율"],
                    var_name="지표", value_name="점수")
    fig = px.line(
        long, x="period", y="점수", color="지표", markers=True,
        hover_data={"period": True, "지표": True, "점수": ":.1f"},
    )
    fig.update_layout(xaxis_title=None, yaxis_range=[0, 100],
                       margin=dict(l=10, r=10, t=50, b=10))
    _y_label(fig, "점수 →")
    return fig


def chart_6_scatter(result):
    df = pd.DataFrame(result["scatter"])
    fig = px.scatter(
        df, x="avgCredit", y="termRate", color="size",
        color_discrete_map=SIZE_COLORS,
        hover_name="id",
        hover_data={"avgCredit": ":.1f", "termRate": ":.1f", "projects": True, "size": True},
    )
    fig.add_vline(x=result["median_credit"], line_dash="dash", line_color="gray",
                  annotation_text=f"중앙값 {result['median_credit']}")
    fig.update_layout(xaxis_title="평균 신용도점수", margin=dict(l=10, r=10, t=50, b=10))
    _y_label(fig, "중도해지율 (%) →")
    return fig


def chart_7_watchlist(result):
    df = pd.DataFrame(result["risk_vendors"]).sort_values("termRate")
    fig = px.bar(
        df, x="termRate", y="id", orientation="h", color="specialty",
        hover_name="id",
        hover_data={"specialty": True, "size": True, "initialGrade": True,
                    "avgCredit": ":.1f", "termRate": ":.1f", "projects": True},
    )
    fig.update_layout(xaxis_title="중도해지율 (%)", yaxis_title=None,
                       legend_title_text="전문분야", height=480,
                       margin=dict(l=10, r=10, t=50, b=10))
    return fig


def chart_8_scoring_backtest(result):
    df = pd.DataFrame(result["scoring_backtest"])
    df["tier"] = pd.Categorical(df["tier"], categories=TIER_ORDER, ordered=True)
    df = df.sort_values("tier")
    fig = px.bar(
        df, x="tier", y="actualTermRate", color="tier",
        color_discrete_map=TIER_COLORS,
        hover_data={"tier": True, "actualTermRate": ":.1f", "n": True},
        text=df["actualTermRate"].map(lambda v: f"{v}%"),
    )
    fig.update_layout(xaxis_title=None, showlegend=False, margin=dict(l=10, r=10, t=50, b=10))
    _y_label(fig, "실제 중도해지율 (%) →")
    return fig


def chart_9_bid_reform_impact(result):
    current = result["kpi"]["term_rate"]
    low_bid = next(r for r in result["by_bid_ratio"] if r["key"] == "< 0.85 (저가입찰)")
    projected_term = round(low_bid["total"] * 17.4 / 100)
    saved = low_bid["중도해지"] - projected_term
    new_total_term = round(result["kpi"]["total_projects"] * current / 100) - saved
    new_rate = round(new_total_term / result["kpi"]["total_projects"] * 100, 1)

    df = pd.DataFrame({
        "시나리오": ["현재", "저가입찰 구간 개선 시"],
        "중도해지율": [current, new_rate],
    })
    fig = px.bar(
        df, x="시나리오", y="중도해지율", color="시나리오",
        color_discrete_map={"현재": "#d03b3b", "저가입찰 구간 개선 시": "#0ca30c"},
        hover_data={"시나리오": True, "중도해지율": ":.1f"},
        text=df["중도해지율"].map(lambda v: f"{v}%"),
    )
    fig.update_layout(xaxis_title=None, showlegend=False, margin=dict(l=10, r=10, t=50, b=10))
    _y_label(fig, "전체 중도해지율 (%) →")
    return fig


def chart_10_roadmap_kpi(result):
    df = pd.DataFrame({
        "시점": ["현재 (관측치)", "1년 후 목표", "2년 후 목표"],
        "중도해지율": [result["kpi"]["term_rate"], 32.0, 25.0],
    })
    fig = px.line(
        df, x="시점", y="중도해지율", markers=True,
        hover_data={"시점": True, "중도해지율": ":.1f"},
        text=df["중도해지율"].map(lambda v: f"{v}%"),
    )
    fig.update_traces(line_color="#d03b3b", marker=dict(color="#d03b3b", size=10), textposition="top center")
    fig.update_layout(xaxis_title=None, yaxis_range=[0, 50], margin=dict(l=10, r=10, t=50, b=10))
    _y_label(fig, "목표 중도해지율 (%) →")
    return fig


ALL_CHARTS = [
    ("1. 저가 입찰의 위험", chart_1_bid_ratio),
    ("2. 신용등급별 리스크", chart_2_grade),
    ("3. 기업 규모별 리스크", chart_3_size),
    ("4. 업종별 리스크", chart_4_category),
    ("5. 협력사 평가지표 추이", chart_5_trend),
    ("6. 신용도 vs 중도해지율", chart_6_scatter),
    ("7. 고위험 협력사 워치리스트", chart_7_watchlist),
    ("8. 협력사 리스크 스코어링 모델", chart_8_scoring_backtest),
    ("9. 저가 입찰 제도 개선안", chart_9_bid_reform_impact),
    ("10. 리스크 관리 실행 로드맵", chart_10_roadmap_kpi),
]
