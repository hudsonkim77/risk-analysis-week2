"""페이지 공통 유틸: 스타일, 뒤로가기 링크, 재사용 차트 컴포넌트."""

import streamlit as st
import plotly.graph_objects as go

import data as d

HOME_PATH = "views/0_home.py"


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
        </style>
        """,
        unsafe_allow_html=True,
    )


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


def back_home_button():
    st.page_link(HOME_PATH, label="처음으로", icon="🏠")
    st.write("")


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
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    cols = st.columns(len(rows))
    for c, r in zip(cols, rows):
        with c:
            st.metric(r["key"], f"{r['termRate']:.1f}%", help=f"전체 {r['total']}건 중 중도해지 {r['중도해지']}건")


def trend_line_chart():
    periods = [t["period"] for t in d.TREND]
    fig = go.Figure()
    for metric, color in d.TREND_COLORS.items():
        ys = [t[metric] for t in d.TREND]
        fig.add_trace(
            go.Scatter(
                x=periods, y=ys, mode="lines+markers", name=metric,
                line=dict(color=color, width=2), marker=dict(size=7, color=color),
                hovertemplate="%{x}<br>" + metric + ": %{y}<extra></extra>",
            )
        )
    fig.update_layout(
        yaxis=dict(title=None, range=[0, 100]),
        annotations=[
            dict(
                text="점수 →", x=0, y=1.16, xref="paper", yref="paper",
                showarrow=False, xanchor="left", font=dict(size=12, color="#898781"),
            )
        ],
    )
    _styled(fig, height=380)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": "hover"})


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
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": "hover"})


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
    st.dataframe(df, use_container_width=True, hide_index=True)


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
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def score_distribution_chart():
    scores = [v["riskScore"] for v in d.VENDOR_SCORES]
    fig = go.Figure(
        go.Histogram(
            x=scores, xbins=dict(start=10, end=65, size=2.5),
            marker=dict(color="#2a78d6"),
            hovertemplate="점수 %{x}<br>%{y}개사<extra></extra>",
        )
    )
    cutoffs = d.SCORING_CUTOFFS
    for label, x in [("Q1", cutoffs["q1"]), ("중앙값", cutoffs["q2"]), ("Q3", cutoffs["q3"])]:
        fig.add_vline(x=x, line_dash="dash", line_color="rgba(128,128,128,0.6)", annotation_text=f"{label} {x}")
    fig.update_layout(
        xaxis=dict(title="리스크 스코어 (0~100)"),
        yaxis=dict(title=None),
        bargap=0.08,
        annotations=[dict(text="협력사 수 →", x=0, y=1.12, xref="paper", yref="paper",
                           showarrow=False, xanchor="left", font=dict(size=12, color="#898781"))],
    )
    _styled(fig, height=320, legend=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": "hover"})


def backtest_chart():
    rows = d.SCORING_BACKTEST
    fig = go.Figure(
        go.Bar(
            x=[r["tier"] for r in rows],
            y=[r["actualTermRate"] for r in rows],
            marker=dict(color=[d.TIER_COLORS[r["tier"]] for r in rows]),
            text=[f"{r['actualTermRate']}%<br>(n={r['n']})" for r in rows],
            textposition="outside",
            hovertemplate="%{x} 등급<br>실제 중도해지율 %{y}%<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis=dict(title="", categoryorder="array", categoryarray=d.TIER_ORDER),
        yaxis=dict(title=None, range=[0, 75]),
        bargap=0.35,
        annotations=[dict(text="실제 중도해지율 (%) →", x=0, y=1.12, xref="paper", yref="paper",
                           showarrow=False, xanchor="left", font=dict(size=12, color="#898781"))],
    )
    _styled(fig, height=340, legend=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def impact_scenario_chart(current_rate, new_rate):
    fig = go.Figure(
        go.Bar(
            x=["현재", "저가입찰 구간이<br>적정가 구간 수준으로 개선될 경우"],
            y=[current_rate, new_rate],
            marker=dict(color=["#d03b3b", "#0ca30c"]),
            text=[f"{current_rate}%", f"{new_rate}%"],
            textposition="outside",
            hovertemplate="%{x}<br>전체 중도해지율 %{y}%<extra></extra>",
        )
    )
    fig.update_layout(
        yaxis=dict(title=None, range=[0, 50]),
        bargap=0.5,
        annotations=[dict(text="전체 중도해지율 (%) →", x=0, y=1.12, xref="paper", yref="paper",
                           showarrow=False, xanchor="left", font=dict(size=12, color="#898781"))],
    )
    _styled(fig, height=320, legend=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def kpi_target_chart(periods, targets):
    fig = go.Figure(
        go.Scatter(
            x=periods, y=targets, mode="lines+markers+text",
            line=dict(color="#d03b3b", width=2.5), marker=dict(size=10, color="#d03b3b"),
            text=[f"{t}%" for t in targets], textposition="top center",
            hovertemplate="%{x}<br>%{y}%<extra></extra>",
        )
    )
    fig.update_layout(
        yaxis=dict(title=None, range=[0, 50]),
        annotations=[dict(text="중도해지율 목표 (%) →", x=0, y=1.12, xref="paper", yref="paper",
                           showarrow=False, xanchor="left", font=dict(size=12, color="#898781"))],
    )
    _styled(fig, height=300, legend=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


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
    st.dataframe(df, use_container_width=True, hide_index=True)
