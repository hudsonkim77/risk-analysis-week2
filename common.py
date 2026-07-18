"""페이지 공통 유틸: 스타일, 재사용 차트/테이블 컴포넌트."""

import streamlit as st
import plotly.graph_objects as go

import data as d

FONT_FAMILY = "'Segoe UI', 'Pretendard', -apple-system, system-ui, sans-serif"

ACCENT = {"분석": "#2a78d6", "제언": "#7c5cd6"}


def apply_style():
    st.markdown(
        f"""
        <style>
        html, body, [class*="css"] {{ font-family: {FONT_FAMILY}; }}

        .block-container {{ padding-top: 3rem; padding-bottom: 4rem; max-width: 1000px; }}

        h1 {{ font-size: 1.7rem !important; font-weight: 800 !important; letter-spacing: -0.01em; }}
        h1 + div p {{ color: var(--text-color); opacity: 0.62; font-size: 0.92rem; margin-top: -0.3rem; }}
        h3 {{ font-size: 1.05rem !important; font-weight: 700 !important; margin-top: 1.6rem !important; }}
        h4 {{ font-size: 0.98rem !important; font-weight: 700 !important; opacity: 0.92; }}

        /* callouts */
        .callout {{
            font-size: 0.92rem; line-height: 1.75; padding: 0.85rem 1.05rem;
            border-radius: 10px; border-left: 4px solid #d03b3b;
            background: rgba(208,59,59,0.07); margin-top: 0.7rem;
        }}
        .callout.good {{ border-left-color: #0ca30c; background: rgba(12,163,12,0.07); }}

        /* KPI tiles */
        .kpi-card {{
            background: var(--secondary-background-color);
            border: 1px solid rgba(128,128,128,0.16); border-radius: 14px;
            padding: 1rem 1.1rem; text-align: left;
            transition: transform .15s ease, box-shadow .15s ease;
        }}
        .kpi-card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 22px rgba(0,0,0,0.10); }}
        .kpi-card .label {{ font-size: 0.76rem; opacity: 0.62; margin-bottom: 0.35rem; font-weight: 600; }}
        .kpi-card .value {{ font-size: 1.55rem; font-weight: 800; letter-spacing: -0.01em; }}

        /* bordered containers (home cards) get a hover lift */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 14px !important;
            transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 26px rgba(0,0,0,0.10);
            border-color: rgba(128,128,128,0.35) !important;
        }}

        .kind-badge {{
            font-size: 0.7rem; font-weight: 800; padding: 2px 9px; border-radius: 999px;
            margin-right: 7px; letter-spacing: 0.01em;
        }}
        .item-num {{
            display: inline-flex; align-items: center; justify-content: center;
            width: 22px; height: 22px; border-radius: 50%;
            background: rgba(128,128,128,0.14); font-size: 0.74rem; font-weight: 800;
            margin-right: 6px;
        }}

        a[data-testid="stPageLink"] {{
            border-radius: 8px !important;
        }}

        /* tables */
        [data-testid="stTable"] table, [data-testid="stDataFrame"] {{
            border-radius: 10px; overflow: hidden;
        }}

        /* per-chart gray interpretation note */
        .chart-note {{
            font-size: 0.85rem; line-height: 1.65; color: var(--text-color); opacity: 0.6;
            margin-top: 0.3rem; margin-bottom: 0.6rem;
        }}

        /* score card (7번 워치리스트) */
        .score-card-rank {{
            display: inline-flex; align-items: center; justify-content: center;
            width: 30px; height: 30px; border-radius: 50%; font-weight: 800; font-size: 0.95rem;
            background: rgba(208,59,59,0.12); color: #d03b3b; margin-right: 10px; flex: none;
        }}
        .score-card-id {{ font-size: 1.15rem; font-weight: 800; letter-spacing: -0.01em; }}
        .score-card-sub {{ font-size: 0.8rem; opacity: 0.62; margin-top: 1px; }}
        .score-stat {{ text-align: center; }}
        .score-stat .n {{ font-size: 1.2rem; font-weight: 800; }}
        .score-stat .l {{ font-size: 0.72rem; opacity: 0.6; margin-top: 2px; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def chart_note(text: str):
    """차트 바로 아래에 붙는 회색 해석 캡션 (~200자 내외)."""
    st.markdown(f'<div class="chart-note">{text}</div>', unsafe_allow_html=True)


def _styled(fig, height=360, legend=True):
    """Plotly 차트 전 페이지 공통 톤 적용: 폰트, 여백, 호버라벨, 격자선."""
    fig.update_layout(
        font=dict(family=FONT_FAMILY, size=13, color="#31333F"),
        height=height,
        margin=dict(l=10, r=16, t=18 if legend else 10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(
            bgcolor="rgba(30,30,30,0.92)", bordercolor="rgba(0,0,0,0)",
            font=dict(family=FONT_FAMILY, size=12.5, color="#ffffff"),
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=12)) if legend else dict(),
        showlegend=legend,
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.14)", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.14)", zeroline=False)
    return fig


def callout(text: str, good: bool = False):
    cls = "callout good" if good else "callout"
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)


def stacked_status_bar(rows, x_title=""):
    """rows: list of dict{key,total,정상완료,지연완료,중도해지,termRate}, 100% 가로 스택 바."""
    status_keys = ["정상완료", "지연완료", "중도해지"]
    keys = [r["key"] for r in rows]
    fig = go.Figure()
    for status in status_keys:
        pct = [r[status] / r["total"] * 100 for r in rows]
        counts = [r[status] for r in rows]
        fig.add_trace(
            go.Bar(
                y=keys,
                x=pct,
                name=status,
                orientation="h",
                marker=dict(color=d.STATUS_COLORS[status]),
                customdata=counts,
                hovertemplate="%{y} · " + status + "<br>%{customdata}건 (%{x:.1f}%)<extra></extra>",
            )
        )
    fig.update_layout(
        barmode="stack",
        bargap=0.28,
        xaxis=dict(title="비중 (%)", range=[0, 100], ticksuffix="%"),
        yaxis=dict(autorange="reversed", title=x_title),
    )
    _styled(fig, height=80 + 50 * len(rows))
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    cols = st.columns(len(rows))
    for c, r in zip(cols, rows):
        with c:
            st.metric(r["key"], f"{r['termRate']:.1f}%", help=f"전체 {r['total']}건 중 중도해지 {r['중도해지']}건")


def trend_line_chart():
    """신용도점수 하락만 확대해 강조하고, 안정적인 품질·납기는 보조 지표로 축소 배치."""
    periods = [t["period"] for t in d.TREND]
    credit = [t["신용도점수"] for t in d.TREND]
    start, end = credit[0], credit[-1]
    delta = round(end - start, 1)
    ymin, ymax = min(credit) - 3, max(credit) + 3

    fig = go.Figure(
        go.Scatter(
            x=periods, y=credit, mode="lines+markers+text",
            line=dict(color="#d03b3b", width=3.5), marker=dict(size=10, color="#d03b3b"),
            fill="tozeroy", fillcolor="rgba(208,59,59,0.10)",
            text=[f"{v}" for v in credit], textposition="top center",
            textfont=dict(size=12, color="#d03b3b"),
            hovertemplate="%{x}<br>신용도점수: %{y}<extra></extra>",
            showlegend=False,
        )
    )
    fig.add_annotation(
        x=periods[-1], y=end, ax=periods[0], ay=start,
        xref="x", yref="y", axref="x", ayref="y",
        text="", showarrow=True, arrowhead=0, arrowwidth=1.4,
        arrowcolor="rgba(208,59,59,0.45)",
    )
    fig.add_annotation(
        x=periods[-1], y=ymax, xref="x", yref="y", xanchor="right", yanchor="top",
        text=f"6개 반기 연속 하락 &nbsp;<b style='font-size:1.15em;color:#d03b3b;'>{delta}pt</b>",
        showarrow=False, font=dict(size=13, color="#d03b3b"),
        bgcolor="rgba(208,59,59,0.08)", borderpad=6,
    )
    fig.update_layout(
        yaxis=dict(title=None, range=[ymin, ymax]),
        annotations=fig.layout.annotations + (
            dict(
                text="신용도점수 →", x=0, y=1.16, xref="paper", yref="paper",
                showarrow=False, xanchor="left", font=dict(size=12, color="#898781"),
            ),
        ),
    )
    _styled(fig, height=320, legend=False)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": "hover"})

    st.write("")
    others = [("품질점수", "#1baf7a"), ("납기준수율", "#4a3aa7")]
    cols = st.columns(len(others))
    for col, (metric, color) in zip(cols, others):
        vals = [t[metric] for t in d.TREND]
        chg = round(vals[-1] - vals[0], 1)
        with col:
            st.metric(
                f"{metric} ({periods[0]} → {periods[-1]})",
                f"{vals[-1]}",
                delta=f"{chg:+.1f}pt",
                delta_color="off",
                help=f"{periods[0]} {vals[0]} → {periods[-1]} {vals[-1]}, 6개 반기 동안 큰 변동 없이 유지",
            )


def scatter_credit_vs_term():
    fig = go.Figure()
    for size, color in d.SIZE_COLORS.items():
        pts = [p for p in d.SCATTER if p["size"] == size]
        fig.add_trace(
            go.Scatter(
                x=[p["avgCredit"] for p in pts],
                y=[p["termRate"] for p in pts],
                mode="markers",
                name=size,
                marker=dict(size=9, color=color, line=dict(width=1, color="rgba(255,255,255,0.6)")),
                customdata=[[p["id"], p["projects"]] for p in pts],
                hovertemplate="%{customdata[0]} · 신용도 %{x} · 해지율 %{y}%<br>진행 PJ %{customdata[1]}건<extra></extra>",
            )
        )
    fig.add_vline(x=d.MEDIAN_CREDIT, line_dash="dash", line_color="rgba(128,128,128,0.6)",
                   annotation_text=f"중앙값 {d.MEDIAN_CREDIT}", annotation_position="top")
    fig.update_layout(
        xaxis=dict(title="평균 신용도점수 →", range=[15, 105]),
        yaxis=dict(title=None, range=[-5, 105]),
        annotations=[
            dict(
                text="중도해지율 (%) →", x=0, y=1.16, xref="paper", yref="paper",
                showarrow=False, xanchor="left", font=dict(size=12, color="#898781"),
            )
        ],
    )
    _styled(fig, height=460)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": "hover"})


def risk_table():
    import pandas as pd

    df = pd.DataFrame(d.RISK_VENDORS)
    df["등급변화"] = df["gradeStart"] + " → " + df["gradeEnd"]
    df = df.rename(columns={
        "id": "협력사ID", "specialty": "전문분야", "size": "규모", "initialGrade": "최초등급",
        "projects": "진행PJ", "termRate": "해지율(%)", "avgCredit": "평균신용도",
        "avgQuality": "평균품질", "avgDelivery": "평균납기", "winRate": "낙찰률(%)",
    })
    df = df[["협력사ID", "전문분야", "규모", "최초등급", "등급변화", "진행PJ", "해지율(%)",
             "평균신용도", "평균품질", "평균납기", "낙찰률(%)"]]
    st.dataframe(df, width="stretch", hide_index=True)


def scoreboard(vendors):
    """워치리스트 상위 N개사를 업체ID 중심의 스코어카드로 렌더링 (7번 페이지)."""
    for i, v in enumerate(vendors, start=1):
        with st.container(border=True):
            c1, c2 = st.columns([2.1, 3.9])
            with c1:
                st.markdown(
                    f'<div style="display:flex;align-items:center;">'
                    f'<span class="score-card-rank">{i}</span>'
                    f'<div><div class="score-card-id">{v["id"]}</div>'
                    f'<div class="score-card-sub">{v["specialty"]} · {v["size"]} · 최초등급 {v["initialGrade"]}</div></div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
                tier_color = d.TIER_COLORS[v["tier"]]
                st.markdown(
                    f'<span class="kind-badge" style="background:{tier_color}1e;color:{tier_color};'
                    f'margin-top:9px;display:inline-block;">{v["tier"]} 등급 · 리스크스코어 {v["riskScore"]}</span>',
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
                            f'<div class="score-stat"><div class="n">{val}</div><div class="l">{label}</div></div>',
                            unsafe_allow_html=True,
                        )


def weights_chart():
    items = list(d.SCORING_WEIGHTS.items())
    fig = go.Figure(
        go.Bar(
            x=[v * 100 for _, v in items],
            y=[k for k, _ in items],
            orientation="h",
            marker=dict(color=["#2a78d6", "#4a3aa7", "#1baf7a", "#eda100"]),
            text=[f"{v * 100:.0f}%" for _, v in items],
            textposition="outside",
            hovertemplate="%{y}: %{x:.0f}%<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis=dict(title="가중치 (%)", range=[0, 45]),
        yaxis=dict(autorange="reversed"),
        bargap=0.35,
    )
    _styled(fig, height=220, legend=False)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def score_distribution_chart():
    """점수 분포 히스토그램 — 구간을 등급 컷오프(Q1/중앙값/Q3)에 맞춰 4개 등급 색으로 직접 채색."""
    scores = [v["riskScore"] for v in d.VENDOR_SCORES]
    cutoffs = d.SCORING_CUTOFFS
    start, size, n_bins = 10, 2.5, 22
    edges = [start + i * size for i in range(n_bins + 1)]

    def tier_of(x):
        if x >= cutoffs["q3"]:
            return "Critical"
        if x >= cutoffs["q2"]:
            return "High"
        if x >= cutoffs["q1"]:
            return "Medium"
        return "Low"

    bins = []
    for i in range(len(edges) - 1):
        lo, hi = edges[i], edges[i + 1]
        cnt = sum(1 for s in scores if lo <= s < hi)
        bins.append(((lo + hi) / 2, cnt, tier_of((lo + hi) / 2)))

    fig = go.Figure()
    for tier in d.TIER_ORDER:
        xs = [c for c, cnt, t in bins if t == tier and cnt > 0]
        ys = [cnt for c, cnt, t in bins if t == tier and cnt > 0]
        if not xs:
            continue
        fig.add_trace(
            go.Bar(
                x=xs, y=ys, name=tier, width=size * 0.92,
                marker=dict(color=d.TIER_COLORS[tier]),
                hovertemplate="점수 %{x}<br>%{y}개사<extra></extra>",
            )
        )
    for label, x in [("Q1", cutoffs["q1"]), ("중앙값", cutoffs["q2"]), ("Q3", cutoffs["q3"])]:
        fig.add_vline(x=x, line_dash="dash", line_color="rgba(128,128,128,0.6)", annotation_text=f"{label} {x}")
    fig.update_layout(
        xaxis=dict(title="리스크 스코어 (0~100)"),
        yaxis=dict(title=None),
        bargap=0.08,
        annotations=[dict(text="협력사 수 →", x=0, y=1.12, xref="paper", yref="paper",
                           showarrow=False, xanchor="left", font=dict(size=12, color="#898781"))],
    )
    _styled(fig, height=320, legend=True)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": "hover"})


def backtest_chart():
    """등급별 실제 해지율을 가로 리더보드 + 전체 평균 기준선으로 대비시켜 격차를 강조."""
    rows = sorted(d.SCORING_BACKTEST, key=lambda r: d.TIER_ORDER.index(r["tier"]))
    avg = d.KPI["term_rate"]
    fig = go.Figure(
        go.Bar(
            y=[r["tier"] for r in rows],
            x=[r["actualTermRate"] for r in rows],
            orientation="h",
            marker=dict(color=[d.TIER_COLORS[r["tier"]] for r in rows]),
            text=[f"{r['actualTermRate']}%  (n={r['n']})" for r in rows],
            textposition="outside",
            textfont=dict(size=13.5),
            hovertemplate="%{y} 등급<br>실제 중도해지율 %{x}%<extra></extra>",
        )
    )
    fig.add_vline(
        x=avg, line_dash="dash", line_color="rgba(128,128,128,0.75)",
        annotation_text=f"전체 평균 {avg}%", annotation_position="top",
        annotation_font=dict(size=12, color="#898781"),
    )
    fig.update_layout(
        xaxis=dict(title="실제 중도해지율 (%)", range=[0, 78]),
        yaxis=dict(autorange="reversed", title=None),
        bargap=0.5,
    )
    _styled(fig, height=300, legend=False)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def impact_scenario_chart(current_rate, new_rate):
    """현재→개선 시나리오를 워터폴로 그려 '얼마나 깎이는지'를 하나의 막대 흐름으로 시각화."""
    drop = round(new_rate - current_rate, 1)
    fig = go.Figure(
        go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "total"],
            x=["현재<br>전체 중도해지율", "저가입찰 구간 개선<br>효과", "개선 후<br>전체 중도해지율"],
            y=[current_rate, drop, 0],
            text=[f"{current_rate}%", f"{drop:+.1f}%p", f"{new_rate}%"],
            textposition="outside",
            textfont=dict(size=14),
            connector=dict(line=dict(color="rgba(128,128,128,0.35)", width=1.4)),
            increasing=dict(marker=dict(color="#d03b3b")),
            decreasing=dict(marker=dict(color="#0ca30c")),
            totals=dict(marker=dict(color="#2a78d6")),
            hovertemplate="%{x}<extra></extra>",
        )
    )
    fig.update_layout(
        yaxis=dict(title=None, range=[0, current_rate + 14]),
        waterfallgap=0.4,
        annotations=[dict(text="전체 중도해지율 (%) →", x=0, y=1.12, xref="paper", yref="paper",
                           showarrow=False, xanchor="left", font=dict(size=12, color="#898781"))],
    )
    _styled(fig, height=340, legend=False)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def kpi_target_chart(periods, targets):
    """0~50 고정축 대신 실제 목표치 구간으로 확대하고, 신호등 색상으로 개선 흐름을 강조."""
    ymin, ymax = min(targets) - 6, max(targets) + 9
    point_colors = ["#d03b3b", "#eda100", "#0ca30c"][: len(targets)]
    total_drop = round(targets[-1] - targets[0], 1)

    fig = go.Figure(
        go.Scatter(
            x=periods, y=targets, mode="lines+markers+text",
            line=dict(color="rgba(128,128,128,0.5)", width=2.5, dash="dot"),
            marker=dict(size=16, color=point_colors, line=dict(width=2, color="white")),
            text=[f"{t}%" for t in targets], textposition="top center",
            textfont=dict(size=14, color="#31333F"),
            fill="tozeroy", fillcolor="rgba(128,128,128,0.07)",
            hovertemplate="%{x}<br>%{y}%<extra></extra>",
        )
    )
    fig.add_annotation(
        x=periods[-1], y=ymax, xref="x", yref="y", xanchor="right", yanchor="top",
        text=f"2년 내 목표 &nbsp;<b style='font-size:1.15em;color:#0ca30c;'>{total_drop:+.1f}%p</b>",
        showarrow=False, font=dict(size=13, color="#0ca30c"),
        bgcolor="rgba(12,163,12,0.08)", borderpad=6,
    )
    fig.update_layout(
        yaxis=dict(title=None, range=[ymin, ymax]),
        annotations=fig.layout.annotations + (
            dict(text="중도해지율 목표 (%) →", x=0, y=1.16, xref="paper", yref="paper",
                 showarrow=False, xanchor="left", font=dict(size=12, color="#898781")),
        ),
    )
    _styled(fig, height=300, legend=False)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def critical_tier_table(n=15):
    import pandas as pd

    rows = [v for v in d.VENDOR_SCORES if v["tier"] == "Critical"]
    rows = sorted(rows, key=lambda v: -v["riskScore"])[:n]
    df = pd.DataFrame(rows)
    df = df.rename(columns={
        "id": "협력사ID", "specialty": "전문분야", "size": "규모", "initialGrade": "최초등급",
        "avgCredit": "평균신용도", "avgBidRatio": "평균낙찰가율", "projects": "진행PJ",
        "terminated": "해지건수", "termRate": "실제해지율(%)", "riskScore": "리스크스코어", "tier": "등급",
    })
    df = df[["협력사ID", "전문분야", "규모", "최초등급", "평균신용도", "평균낙찰가율",
             "진행PJ", "해지건수", "실제해지율(%)", "리스크스코어"]]
    st.dataframe(df, width="stretch", hide_index=True)
