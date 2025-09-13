from __future__ import annotations

import pandas as pd
import plotly.express as px


def line_dual_axis(df_left: pd.DataFrame, x: str, y_left: str, y_right: str, title: str = ""):
    fig = px.line(df_left, x=x, y=y_left, title=title)
    if y_right in df_left.columns:
        fig2 = px.line(df_left, x=x, y=y_right)
        for tr in fig2.data:
            tr.yaxis = "y2"
            fig.add_trace(tr)
        fig.update_layout(
            yaxis2=dict(overlaying="y", side="right", showgrid=False), legend=dict(orientation="h")
        )
    fig.update_layout(margin=dict(l=10, r=10, t=60, b=10))
    return fig


def line_simple(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str = ""):
    fig = px.line(df, x=x, y=y, color=color, title=title)
    fig.update_layout(margin=dict(l=10, r=10, t=60, b=10))
    return fig


def stacked_bar(df: pd.DataFrame, x: str, y: str, color: str, title: str = ""):
    fig = px.bar(df, x=x, y=y, color=color, title=title)
    fig.update_layout(barmode="stack", margin=dict(l=10, r=10, t=60, b=10))
    return fig


def treemap(df: pd.DataFrame, path: list[str], values: str, color: str | None = None, title: str = ""):
    fig = px.treemap(df, path=path, values=values, color=color, title=title)
    fig.update_layout(margin=dict(l=10, r=10, t=60, b=10))
    return fig


def scatter_bubble(df: pd.DataFrame, x: str, y: str, size: str, color: str, hover_name: str | None = None, title: str = ""):
    fig = px.scatter(df, x=x, y=y, size=size, color=color, hover_name=hover_name, title=title)
    fig.update_layout(margin=dict(l=10, r=10, t=60, b=10))
    return fig


def pareto_chart(df: pd.DataFrame, value_col: str, label_col: str, title: str = ""):
    d = df.sort_values(value_col, ascending=False).reset_index(drop=True)
    d["cum_share"] = d[value_col].cumsum() / max(d[value_col].sum(), 1e-9)
    d["rank"] = d.index + 1
    fig = px.bar(d, x="rank", y=value_col, hover_data=[label_col], title=title)
    fig2 = px.line(d, x="rank", y="cum_share")
    for tr in fig2.data:
        tr.yaxis = "y2"
        fig.add_trace(tr)
    fig.update_layout(
        yaxis2=dict(overlaying="y", side="right", range=[0, 1], showgrid=False),
        margin=dict(l=10, r=10, t=60, b=10),
    )
    return fig

