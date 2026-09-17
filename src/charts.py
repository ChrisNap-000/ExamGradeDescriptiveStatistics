"""Chart builders for exam totals and question difficulty.

Colors use the school brand palette's Crimson (`#9E1B32`) as the app's
accent color; every chart here encodes one series of magnitudes, so a
single accent hue is used throughout.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

ACCENT = "#9E1B32"
ACCENT_FILL = "rgba(158, 27, 50, 0.25)"
SURFACE = "#1a1a19"
GRIDLINE = "#2c2c2a"
AXIS_LINE = "#383835"
INK_PRIMARY = "#ffffff"
INK_SECONDARY = "#c3c2b7"

_LAYOUT_DEFAULTS = dict(
    plot_bgcolor=SURFACE,
    paper_bgcolor=SURFACE,
    font=dict(color=INK_PRIMARY, size=14),
    title_font=dict(size=20, color=INK_PRIMARY),
    margin=dict(l=60, r=25, t=60, b=55),
)

_AXIS_DEFAULTS = dict(
    gridcolor=GRIDLINE,
    linecolor=AXIS_LINE,
    title_font=dict(size=16, color=INK_SECONDARY),
    tickfont=dict(size=13, color=INK_SECONDARY),
)


def totals_histogram(totals: pd.Series) -> go.Figure:
    fig = go.Figure(
        go.Histogram(
            x=totals,
            marker_color=ACCENT,
            marker_line_width=0,
            xbins=dict(size=2),
            hovertemplate="Grade: %{x}<br>Occurrences: %{y}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Distribution of Exam Totals",
        xaxis_title="Total Score",
        yaxis_title="Number of Students",
        bargap=0.05,
        **_LAYOUT_DEFAULTS,
    )
    fig.update_xaxes(range=[0, 100], **_AXIS_DEFAULTS)
    fig.update_yaxes(**_AXIS_DEFAULTS)
    return fig


def totals_boxplot(totals: pd.Series) -> go.Figure:
    fig = go.Figure(
        go.Box(
            y=totals,
            name="Total Score",
            marker_color=ACCENT,
            line_color=ACCENT,
            fillcolor=ACCENT_FILL,
            boxmean=True,
        )
    )
    fig.update_layout(
        title="Spread of Exam Totals",
        yaxis_title="Total Score",
        showlegend=False,
        **_LAYOUT_DEFAULTS,
    )
    fig.update_xaxes(**_AXIS_DEFAULTS)
    fig.update_yaxes(range=[0, 100], **_AXIS_DEFAULTS)
    return fig


def difficulty_bar_chart(difficulty_df: pd.DataFrame) -> go.Figure:
    """Bars ordered left-to-right by Exam A question number.

    The hover tooltip carries the full picture for that question: its
    number and correct answer on each version, plus percent correct.
    """
    customdata = difficulty_df[
        ["Exam A Question Number", "Exam A Answer", "Exam B Question Number", "Exam B Answer"]
    ].to_numpy()

    fig = go.Figure(
        go.Bar(
            x=difficulty_df["Exam A Question Number"],
            y=difficulty_df["Percent Correct"],
            marker_color=ACCENT,
            marker_line_width=0,
            customdata=customdata,
            hovertemplate=(
                "<b>Exam A Question %{customdata[0]}</b> (Answer: %{customdata[1]})<br>"
                "Exam B Question %{customdata[2]} (Answer: %{customdata[3]})<br>"
                "Percent Correct: %{y:.1f}%"
                "<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title="Question Difficulty, Ordered by Exam A Question Number",
        xaxis_title="Exam A Question Number",
        yaxis_title="Percent Correct",
        **_LAYOUT_DEFAULTS,
    )
    fig.update_xaxes(dtick=5, **_AXIS_DEFAULTS)
    fig.update_yaxes(range=[0, 100], **_AXIS_DEFAULTS)
    return fig
