"""plotly.express 버전 차트 10종 — 다크모드 + 네온 글로우 테마.

pipeline.build()가 raw_data/*.csv를 직접 읽어 조인·집계한 결과(dict)를 받아
각 리포트를 대표하는 차트 하나씩을 그린다.
1~4·7번은 "리스크 리더보드"(정도 순 정렬 + 그린→옐로우→레드 그라데이션) 기법으로 통일해
3색 스택바보다 한눈에 위험도 서열이 들어오도록 했다.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

STATUS_COLS = ["정상완료", "지연완료", "중도해지"]
STATUS_COLORS = {"정상완료": "#39FF14", "지연완료": "#FFEA00", "중도해지": "#FF3366"}
SIZE_COLORS = {"대기업": "#00E5FF", "중견기업": "#39FF14", "중소기업": "#FF3EA5", "소상공인": "#FFEA00"}
TIER_COLORS = {"Critical": "#FF3366", "High": "#FF9500", "Medium": "#FFEA00", "Low": "#39FF14"}
TIER_ORDER = ["Critical", "High", "Medium", "Low"]

RISK_SCALE = [[0, "#39FF14"], [0.5, "#FFEA00"], [1, "#FF3366"]]

TEXT_COLOR = "#EAFFE0"
LABEL_COLOR = "#9FE870"
GRID_COLOR = "rgba(204,255,0,0.10)"


def _dark_style(fig, height=360, legend=True):
    """모든 차트 공통 다크+네온 톤: 투명 배경, 밝은 텍스트, 은은한 라임 그리드."""
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR, size=13),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(color=TEXT_COLOR)) if legend else dict(),
        showlegend=legend,
        hoverlabel=dict(bgcolor="#141a12", bordercolor="#CCFF00", font=dict(color="#EAFFE0", size=12.5)),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID_COLOR, zeroline=False, color=TEXT_COLOR,
                      linecolor="rgba(204,255,0,0.25)")
    fig.update_yaxes(showgrid=True, gridcolor=GRID_COLOR, zeroline=False, color=TEXT_COLOR,
                      linecolor="rgba(204,255,0,0.25)")
    return fig


def _y_label(fig, text):
    """Plotly가 한글 y축 제목을 세로로 한 글자씩 쌓아 렌더링하는 문제를 피하기 위해
    회전된 axis title 대신 좌상단 가로 주석으로 대체한다."""
    fig.update_layout(yaxis_title=None)
    fig.add_annotation(
        text=text, x=0, y=1.1, xref="paper", yref="paper",
        showarrow=False, xanchor="left", font=dict(size=12, color=LABEL_COLOR),
    )
    return fig


def _risk_leaderboard(rows, height=None):
    """termRate 내림차순(고위험이 위로) 가로 막대, 그린→옐로우→레드 연속 색상.
    hover에 정상완료/지연완료/중도해지/total 전체 내역을 보여준다."""
    df = pd.DataFrame(rows).sort_values("termRate", ascending=True)
    fig = px.bar(
        df, x="termRate", y="key", orientation="h",
        color="termRate", color_continuous_scale=RISK_SCALE, range_color=[0, 100],
        text=df["termRate"].map(lambda v: f"{v:.1f}%"),
        hover_data={"key": True, "termRate": ":.1f", "정상완료": True, "지연완료": True,
                    "중도해지": True, "total": True},
    )
    fig.update_traces(marker_line_width=0, textposition="outside", textfont=dict(color=TEXT_COLOR, size=13))
    fig.update_layout(xaxis_title="중도해지율 (%)", yaxis_title=None, xaxis_range=[0, 108],
                       coloraxis_showscale=False)
    _dark_style(fig, height=height or (110 + 55 * len(rows)), legend=False)
    return fig


def chart_1_bid_ratio(result):
    return _risk_leaderboard(result["by_bid_ratio"])


def chart_2_grade(result):
    return _risk_leaderboard(result["by_grade"])


def chart_3_size(result):
    return _risk_leaderboard(result["by_size"])


def chart_4_category(result):
    return _risk_leaderboard(result["by_cat"])


def chart_5_trend(result):
    df = pd.DataFrame(result["trend"])
    long = df.melt(id_vars="period", value_vars=["신용도점수", "품질점수", "납기준수율"],
                    var_name="지표", value_name="점수")
    fig = px.line(
        long, x="period", y="점수", color="지표", markers=True,
        color_discrete_map={"신용도점수": "#00E5FF", "품질점수": "#39FF14", "납기준수율": "#FF3EA5"},
        hover_data={"period": True, "지표": True, "점수": ":.1f"},
    )
    fig.update_traces(line_width=3, marker=dict(size=8, line=dict(width=1, color="rgba(255,255,255,0.5)")))
    fig.update_layout(xaxis_title=None, yaxis_range=[0, 100])
    _dark_style(fig, height=380)
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
    fig.update_traces(marker=dict(size=10, line=dict(width=1, color="rgba(255,255,255,0.35)")))
    fig.add_vline(x=result["median_credit"], line_dash="dash", line_color="#CCFF00",
                  annotation_text=f"중앙값 {result['median_credit']}",
                  annotation_font_color=LABEL_COLOR)
    fig.update_layout(xaxis_title="평균 신용도점수")
    _dark_style(fig, height=460)
    _y_label(fig, "중도해지율 (%) →")
    return fig


def chart_7_watchlist(result):
    df = pd.DataFrame(result["risk_vendors"]).sort_values("termRate", ascending=True)
    fig = px.bar(
        df, x="termRate", y="id", orientation="h",
        color="termRate", color_continuous_scale=RISK_SCALE, range_color=[0, 100],
        text=df["termRate"].map(lambda v: f"{v:.0f}%"),
        hover_name="id",
        hover_data={"specialty": True, "size": True, "initialGrade": True,
                    "avgCredit": ":.1f", "termRate": ":.1f", "projects": True},
    )
    fig.update_traces(marker_line_width=0, textposition="outside", textfont=dict(color=TEXT_COLOR, size=12))
    fig.update_layout(xaxis_title="중도해지율 (%)", yaxis_title=None, xaxis_range=[0, 112],
                      coloraxis_showscale=False)
    _dark_style(fig, height=480, legend=False)
    return fig


def chart_8_scoring_backtest(result):
    df = pd.DataFrame(result["scoring_backtest"])
    df["tier"] = pd.Categorical(df["tier"], categories=TIER_ORDER, ordered=True)
    df = df.sort_values("tier")
    overall = result["kpi"]["term_rate"]

    fig = px.bar(
        df, x="tier", y="actualTermRate", color="tier",
        color_discrete_map=TIER_COLORS,
        hover_data={"tier": True, "actualTermRate": ":.1f", "n": True},
        text=df["actualTermRate"].map(lambda v: f"{v}%"),
    )
    fig.update_traces(marker_line_width=0, textfont_color=TEXT_COLOR, textposition="outside")
    fig.add_hline(y=overall, line_dash="dash", line_color="rgba(234,255,224,0.55)",
                  annotation_text=f"전체 평균 {overall}%", annotation_font_color=LABEL_COLOR,
                  annotation_position="top left")
    fig.update_layout(xaxis_title=None, showlegend=False, yaxis_range=[0, 72])
    _dark_style(fig, height=340, legend=False)
    _y_label(fig, "실제 중도해지율 (%) →")
    return fig


def chart_9_bid_reform_impact(result):
    current = result["kpi"]["term_rate"]
    low_bid = next(r for r in result["by_bid_ratio"] if r["key"] == "< 0.85 (저가입찰)")
    projected_term = round(low_bid["total"] * 17.4 / 100)
    saved = low_bid["중도해지"] - projected_term
    new_total_term = round(result["kpi"]["total_projects"] * current / 100) - saved
    new_rate = round(new_total_term / result["kpi"]["total_projects"] * 100, 1)
    gap = round(current - new_rate, 1)

    df = pd.DataFrame({
        "시나리오": ["현재", "저가입찰 구간 개선 시"],
        "중도해지율": [current, new_rate],
    })
    fig = px.bar(
        df, x="시나리오", y="중도해지율", color="시나리오",
        color_discrete_map={"현재": "#FF3366", "저가입찰 구간 개선 시": "#39FF14"},
        hover_data={"시나리오": True, "중도해지율": ":.1f"},
        text=df["중도해지율"].map(lambda v: f"{v}%"),
    )
    fig.update_traces(marker_line_width=0, textfont_color=TEXT_COLOR, textposition="outside")
    fig.add_annotation(
        x=0.5, y=max(current, new_rate) + 9, xref="x", yref="y", showarrow=False,
        text=f"▼ {gap}%p 개선", font=dict(size=16, color="#CCFF00"),
    )
    fig.add_shape(type="line", x0=0, x1=1, y0=current + 3, y1=new_rate + 3,
                  xref="x", yref="y", line=dict(color="#CCFF00", width=2, dash="dot"))
    fig.update_layout(xaxis_title=None, showlegend=False, yaxis_range=[0, max(current, new_rate) + 18])
    _dark_style(fig, height=340, legend=False)
    _y_label(fig, "전체 중도해지율 (%) →")
    return fig


def chart_10_roadmap_kpi(result):
    current = result["kpi"]["term_rate"]
    periods = ["현재 (관측치)", "1년 후 목표", "2년 후 목표"]
    targets = [current, 32.0, 25.0]
    gap = round(current - targets[-1], 1)

    fig = go.Figure()
    # 현재 수준 기준선 (개선 안 하면 그대로일 수준)
    fig.add_trace(go.Scatter(
        x=periods, y=[current] * 3, mode="lines", line=dict(color="rgba(234,255,224,0.35)", width=2, dash="dot"),
        name="현재 수준 유지 시", hoverinfo="skip",
    ))
    # 목표 트래젝토리 + 기준선까지 음영 채우기(격차 시각화)
    fig.add_trace(go.Scatter(
        x=periods, y=targets, mode="lines+markers+text",
        line=dict(color="#CCFF00", width=4),
        marker=dict(color="#CCFF00", size=12, line=dict(width=1.5, color="rgba(255,255,255,0.6)")),
        text=[f"{t}%" for t in targets], textposition="bottom center", textfont=dict(color=TEXT_COLOR, size=13),
        fill="tonexty", fillcolor="rgba(204,255,0,0.14)",
        name="목표 로드맵", hovertemplate="%{x}<br>%{y}%<extra></extra>",
    ))
    fig.add_annotation(
        x=periods[-1], y=targets[-1] - 7, showarrow=False,
        text=f"◀ 총 {gap}%p 개선", font=dict(size=17, color="#CCFF00"),
    )
    fig.update_layout(xaxis_title=None, yaxis_range=[0, 50], legend=dict(orientation="h", y=1.15, x=0))
    _dark_style(fig, height=340)
    _y_label(fig, "중도해지율 (%) →")
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
