"""plotly.express 버전 차트 10종 — 다크모드 + 네온 글로우 테마.

pipeline.build()가 raw_data/*.csv를 직접 읽어 조인·집계한 결과(dict)를 받아
각 리포트를 대표하는 차트 하나씩을 그린다.
1~4·7번은 "리스크 리더보드"(정도 순 정렬 + 그린→옐로우→레드 그라데이션) 기법으로 통일해
3색 스택바보다 한눈에 위험도 서열이 들어오도록 했다.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

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
    """신용도점수 하락만 확대·강조하고, 안정적인 품질·납기는 흐린 점선으로 대비시킨다."""
    df = pd.DataFrame(result["trend"])
    periods = df["period"].tolist()
    credit = df["신용도점수"].tolist()
    quality = df["품질점수"].tolist()
    delivery = df["납기준수율"].tolist()
    all_vals = credit + quality + delivery
    delta = round(credit[-1] - credit[0], 1)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=periods, y=quality, mode="lines+markers", name="품질점수",
        line=dict(color="rgba(57,255,20,0.35)", width=1.6, dash="dot"),
        marker=dict(size=5, color="rgba(57,255,20,0.55)"),
        hovertemplate="%{x}<br>품질점수 %{y}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=periods, y=delivery, mode="lines+markers", name="납기준수율",
        line=dict(color="rgba(255,62,165,0.35)", width=1.6, dash="dot"),
        marker=dict(size=5, color="rgba(255,62,165,0.55)"),
        hovertemplate="%{x}<br>납기준수율 %{y}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=periods, y=credit, mode="lines+markers+text", name="신용도점수",
        line=dict(color="#FF3366", width=4), marker=dict(size=10, color="#FF3366"),
        text=[f"{v}" for v in credit], textposition="top center", textfont=dict(color="#FF3366", size=12),
        fill="tozeroy", fillcolor="rgba(255,51,102,0.12)",
        hovertemplate="%{x}<br>신용도점수 %{y}<extra></extra>",
    ))
    fig.add_annotation(
        x=periods[-1], y=max(all_vals) + 2, xref="x", yref="y", xanchor="right", yanchor="top",
        text=f"신용도점수만 {delta}pt 하락", showarrow=False, font=dict(size=13, color="#FF3366"),
        bgcolor="rgba(255,51,102,0.14)", borderpad=6,
    )
    fig.update_layout(xaxis_title=None, yaxis_range=[min(all_vals) - 3, max(all_vals) + 7])
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


def render_watchlist(result):
    """15개사 나열 대신, 실적+스코어가 동시에 검증된 상위 5개사를 실명(협력사ID) 카드로 렌더링.
    반환값 없이 st 요소를 직접 그리므로 app.py에서 st.plotly_chart 대신 호출한다."""
    for i, v in enumerate(result["watchlist"], start=1):
        color = TIER_COLORS[v["tier"]]
        with st.container(border=True):
            c1, c2 = st.columns([2.1, 3.9])
            with c1:
                st.markdown(
                    f'<div style="display:flex;align-items:center;">'
                    f'<span style="display:inline-flex;align-items:center;justify-content:center;width:30px;'
                    f'height:30px;border-radius:50%;font-weight:800;background:rgba(255,51,102,0.16);'
                    f'color:#FF3366;margin-right:10px;">{i}</span>'
                    f'<div><div style="font-size:1.15rem;font-weight:800;color:{TEXT_COLOR};">{v["id"]}</div>'
                    f'<div style="font-size:0.8rem;color:{LABEL_COLOR};">{v["specialty"]} · {v["size"]} · '
                    f'최초등급 {v["initialGrade"]}</div></div></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<span style="font-size:0.7rem;font-weight:800;padding:2px 9px;border-radius:999px;'
                    f'background:{color}29;color:{color};margin-top:9px;display:inline-block;">'
                    f'{v["tier"]} 등급 · 리스크스코어 {v["riskScore"]}</span>',
                    unsafe_allow_html=True,
                )
            with c2:
                stats = [
                    ("해지율", f'{v["termRate"]:.0f}%'),
                    ("진행PJ / 해지건수", f'{v["projects"]} / {v["terminated"]}'),
                    ("평균신용도", f'{v["avgCredit"]:.1f}'),
                    ("평균낙찰가율", f'{v["avgBidRatio"]:.2f}'),
                ]
                cols = st.columns(len(stats))
                for col, (label, val) in zip(cols, stats):
                    with col:
                        st.markdown(
                            f'<div style="text-align:center;"><div style="font-size:1.2rem;font-weight:800;'
                            f'color:{TEXT_COLOR};">{val}</div><div style="font-size:0.72rem;color:{LABEL_COLOR};'
                            f'margin-top:2px;">{label}</div></div>',
                            unsafe_allow_html=True,
                        )


def chart_8_scoring_backtest(result):
    """등급별 실제 해지율을 가로 리더보드 + 전체 평균 기준선으로 대비시켜 격차를 강조."""
    df = pd.DataFrame(result["scoring_backtest"])
    df["tier"] = pd.Categorical(df["tier"], categories=TIER_ORDER, ordered=True)
    df = df.sort_values("tier")
    overall = result["kpi"]["term_rate"]

    fig = px.bar(
        df, x="actualTermRate", y="tier", orientation="h", color="tier",
        color_discrete_map=TIER_COLORS,
        hover_data={"tier": True, "actualTermRate": ":.1f", "n": True},
        text=df.apply(lambda r: f"{r['actualTermRate']}%  (n={r['n']})", axis=1),
    )
    fig.update_traces(marker_line_width=0, textfont_color=TEXT_COLOR, textposition="outside")
    fig.add_vline(x=overall, line_dash="dash", line_color="rgba(234,255,224,0.55)",
                  annotation_text=f"전체 평균 {overall}%", annotation_font_color=LABEL_COLOR,
                  annotation_position="top")
    fig.update_layout(
        xaxis_title="실제 중도해지율 (%)", yaxis_title=None, showlegend=False,
        yaxis=dict(autorange="reversed", categoryorder="array", categoryarray=TIER_ORDER),
        xaxis_range=[0, 78], bargap=0.5,
    )
    _dark_style(fig, height=300, legend=False)
    return fig


def chart_9_bid_reform_impact(result):
    """현재→개선 시나리오를 워터폴로 그려 '얼마나 깎이는지'를 하나의 막대 흐름으로 시각화."""
    current = result["kpi"]["term_rate"]
    low_bid = next(r for r in result["by_bid_ratio"] if r["key"] == "< 0.85 (저가입찰)")
    projected_term = round(low_bid["total"] * 17.4 / 100)
    saved = low_bid["중도해지"] - projected_term
    new_total_term = round(result["kpi"]["total_projects"] * current / 100) - saved
    new_rate = round(new_total_term / result["kpi"]["total_projects"] * 100, 1)
    drop = round(new_rate - current, 1)

    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["absolute", "relative", "total"],
        x=["현재<br>전체 중도해지율", "저가입찰 구간 개선<br>효과", "개선 후<br>전체 중도해지율"],
        y=[current, drop, 0],
        text=[f"{current}%", f"{drop:+.1f}%p", f"{new_rate}%"],
        textposition="outside", textfont=dict(color=TEXT_COLOR, size=14),
        connector=dict(line=dict(color="rgba(234,255,224,0.35)", width=1.4)),
        increasing=dict(marker=dict(color="#FF3366")),
        decreasing=dict(marker=dict(color="#39FF14")),
        totals=dict(marker=dict(color="#00E5FF")),
        hovertemplate="%{x}<extra></extra>",
    ))
    fig.update_layout(showlegend=False, yaxis_range=[0, current + 14], waterfallgap=0.4)
    _dark_style(fig, height=340, legend=False)
    _y_label(fig, "전체 중도해지율 (%) →")
    return fig


def chart_10_roadmap_kpi(result):
    """0~50 고정축 대신 실제 목표 구간으로 확대하고, 신호등 색상으로 개선 흐름을 강조."""
    current = result["kpi"]["term_rate"]
    periods = ["현재 (관측치)", "1년 후 목표", "2년 후 목표"]
    targets = [current, 32.0, 25.0]
    gap = round(current - targets[-1], 1)
    ymin, ymax = min(targets) - 6, max(targets) + 10
    point_colors = ["#FF3366", "#FFEA00", "#39FF14"]

    fig = go.Figure(go.Scatter(
        x=periods, y=targets, mode="lines+markers+text",
        line=dict(color="rgba(234,255,224,0.45)", width=2.5, dash="dot"),
        marker=dict(color=point_colors, size=16, line=dict(width=2, color="rgba(255,255,255,0.7)")),
        text=[f"{t}%" for t in targets], textposition="top center", textfont=dict(color=TEXT_COLOR, size=13),
        fill="tozeroy", fillcolor="rgba(204,255,0,0.08)",
        hovertemplate="%{x}<br>%{y}%<extra></extra>",
    ))
    fig.add_annotation(
        x=periods[-1], y=ymax, xref="x", yref="y", xanchor="right", yanchor="top", showarrow=False,
        text=f"2년 내 목표 ▼ {gap}%p", font=dict(size=15, color="#39FF14"),
        bgcolor="rgba(57,255,20,0.12)", borderpad=6,
    )
    fig.update_layout(xaxis_title=None, yaxis_range=[ymin, ymax], showlegend=False)
    _dark_style(fig, height=340, legend=False)
    _y_label(fig, "중도해지율 (%) →")
    return fig


ALL_CHARTS = [
    ("1. 저가 입찰의 위험", chart_1_bid_ratio),
    ("2. 신용등급별 리스크", chart_2_grade),
    ("3. 기업 규모별 리스크", chart_3_size),
    ("4. 업종별 리스크", chart_4_category),
    ("5. 협력사 평가지표 추이", chart_5_trend),
    ("6. 신용도 vs 중도해지율", chart_6_scatter),
    ("7. 고위험 협력사 워치리스트 (리스크 스코어 상위 5개사)", None),  # render_watchlist가 직접 렌더링
    ("8. 협력사 리스크 스코어링 모델", chart_8_scoring_backtest),
    ("9. 저가 입찰 제도 개선안", chart_9_bid_reform_impact),
    ("10. 리스크 관리 실행 로드맵", chart_10_roadmap_kpi),
]

# 각 차트 하단에 붙는 회색 해석 캡션 (~200자 내외). app.py에서 st.caption으로 렌더링한다.
CHART_NOTES = {
    "1. 저가 입찰의 위험":
        "구간을 해지율 낮은 순으로 정렬한 가로 막대입니다. 색이 초록에서 빨강으로 바뀌는 지점을 보면 "
        "<0.85 구간이 막대 길이와 색 모두에서 압도적으로 위험하다는 게 바로 드러납니다.",
    "2. 신용등급별 리스크":
        "AAA~CCC를 해지율 낮은 순으로 정렬하니 그대로 신용등급 순서가 되어버립니다. 등급이 나빠질수록 "
        "막대가 길어지고 색이 빨갛게 변하는, 예외 없는 계단식 패턴입니다.",
    "3. 기업 규모별 리스크":
        "대기업·중견기업은 막대가 짧고 초록, 중소기업·소상공인은 막대가 길고 빨강에 가깝습니다. "
        "규모가 작을수록 위험도가 커진다는 것이 색과 길이로 이중으로 확인됩니다.",
    "4. 업종별 리스크":
        "건설/설비가 막대 길이와 빨강 색 모두에서 최상단을 차지하고, 디자인/광고가 가장 짧고 "
        "초록에 가까운 맨 아래에 위치합니다.",
    "5. 협력사 평가지표 추이":
        "신용도점수만 확대해 채워 그렸고, 품질·납기 두 지표는 점선으로 흐리게 남겨 대비시켰습니다. "
        "신용도점수만 6개 반기 내내 꺾이지 않고 하락합니다.",
    "6. 신용도 vs 중도해지율":
        "점 하나가 협력사 1곳입니다. 점선(중앙값) 왼쪽에 해지율 높은 점이 몰려 있고, 오른쪽은 대부분 "
        "해지율 0%에 가깝지만 예외도 섞여 있어 신용도만으로 완전히 설명되지는 않습니다.",
    "7. 고위험 협력사 워치리스트 (리스크 스코어 상위 5개사)":
        "표본 1건짜리 &#39;우연한 100% 해지&#39;는 제외하고, 5개사 모두 신용등급 BB 이하·낙찰가율 0.85 안팎이라는 "
        "공통점을 갖습니다. 8번 스코어링 모델이 예측한 순위와 실제 해지 이력이 정확히 겹칩니다.",
    "8. 협력사 리스크 스코어링 모델":
        "점선은 전체 평균 해지율(40.0%)입니다. Critical·High는 이 선보다 오른쪽, Medium·Low는 왼쪽에 위치해 "
        "네 등급이 평균 기준 위험군·안전군으로 뚜렷하게 나뉩니다.",
    "9. 저가 입찰 제도 개선안":
        "첫 막대(현재)에서 초록 막대(개선 효과)만큼 깎여 마지막 막대(개선 후)로 떨어지는 흐름입니다. "
        "저가입찰 구간 하나만 정상화해도 전체 해지율이 10%p 넘게 줄어들 수 있습니다.",
    "10. 리스크 관리 실행 로드맵":
        "점 색이 빨강→노랑→초록으로 바뀌는 것 자체가 목표입니다. 현재 40.0%에서 2년 후 25.0%까지 총 15.0%p를 "
        "낮추는 여정이며, 1년 차(32.0%)가 중간 점검 지점입니다.",
}
