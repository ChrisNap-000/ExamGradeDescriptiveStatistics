"""Chart builders for exam totals and question difficulty.

Colors use the school brand palette's Crimson (`#9E1B32`) as the app's
accent color; every chart here encodes one series of magnitudes, so a
single accent hue is used throughout.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

ACCENT = "#9E1B32"
ACCENT_FILL = "rgba(158, 27, 50, 0.25)"
SURFACE = "#1a1a19"
GRIDLINE = "#2c2c2a"
AXIS_LINE = "#383835"
INK_PRIMARY = "#ffffff"
INK_SECONDARY = "#c3c2b7"

# Validated categorical palette (dark-surface steps), assigned in fixed order —
# see the dataviz skill's color-formula: identity color, never repainted by
# correctness. "NA" (no answer given) takes the muted ink instead of a sixth
# categorical hue, since it isn't really an answer option's identity.
_OPTION_COLORS = {
    "A": "#3987e5",
    "B": "#d95926",
    "C": "#199e70",
    "D": "#c98500",
    "E": "#d55181",
    "NA": "#898781",
}
_OPTION_TEXT_INK = {
    "A": "#ffffff",
    "B": "#ffffff",
    "C": "#ffffff",
    "D": "#ffffff",
    "E": "#ffffff",
    "NA": "#0b0b0b",
}
_OPTION_LABELS = {
    "A": "Option A",
    "B": "Option B",
    "C": "Option C",
    "D": "Option D",
    "E": "Option E",
    "NA": "No Answer",
}

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


def totals_histogram(totals: pd.Series, bin_size: float = 2) -> go.Figure:
    fig = go.Figure(
        go.Histogram(
            x=totals,
            marker_color=ACCENT,
            marker_line_width=0,
            xbins=dict(size=bin_size),
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
    number and correct answer on each version, plus percent correct and
    the raw count of students who answered correctly.
    """
    customdata = difficulty_df[
        [
            "Exam A Question Number",
            "Exam A Answer",
            "Exam B Question Number",
            "Exam B Answer",
            "Number Correct",
            "Number of Students",
        ]
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
                "Percent Correct: %{y:.1f}% (%{customdata[4]} of %{customdata[5]} students)"
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


def option_breakdown_chart(breakdown_df: pd.DataFrame) -> go.Figure:
    """Stacked bars of which underlying answer option students picked, per
    question, combined across Exam A and Exam B into a single bar.

    Exam A and Exam B shuffle answer-choice order as well as question order,
    so a raw letter alone doesn't identify an option across versions. The
    reference sheet now maps each option pair explicitly (not just each
    question pair), so each stacked segment here represents one underlying
    option regardless of which letter it was labeled on either version's
    paper — no more splitting into separate Exam A / Exam B rows. The hover
    tooltip still spells out each version's own native letter and native
    question number, since that's what the raw answer keys are numbered by.
    The correct option's segment carries a checkmark in addition to its
    normal option color, so correctness is never color-alone.
    """
    fig = go.Figure()

    df = breakdown_df[breakdown_df["Total"] > 0]
    for option in (*_OPTION_COLORS,):
        option_df = df[df["Option"] == option].sort_values(
            "Exam A Question Number", kind="mergesort"
        )
        if option_df.empty:
            continue

        is_na = option == "NA"
        correct_note = np.where(option_df["Is Correct"], "<br>✓ Correct answer", "")
        customdata = np.column_stack(
            [
                option_df["Count"],
                option_df["Total"],
                correct_note,
                option_df["A Option"],
                option_df["B Option"],
                option_df["Exam B Question Number"],
                option_df["A Count"],
                option_df["B Count"],
            ]
        )
        detail_lines = (
            ""
            if is_na
            else (
                "<br>Exam A Option %{customdata[3]}: %{customdata[6]} students"
                "<br>Exam B Question %{customdata[5]}, Option %{customdata[4]}: %{customdata[7]} students"
            )
        )
        fig.add_trace(
            go.Bar(
                x=option_df["Exam A Question Number"],
                y=option_df["Percent"],
                name=_OPTION_LABELS[option],
                marker_color=_OPTION_COLORS[option],
                marker_line_width=1,
                marker_line_color=SURFACE,
                text=["✓" if correct else "" for correct in option_df["Is Correct"]],
                textposition="inside",
                insidetextfont=dict(color=_OPTION_TEXT_INK[option]),
                constraintext="inside",
                customdata=customdata,
                hovertemplate=(
                    f"<b>{_OPTION_LABELS[option]}</b><br>Exam A Question %{{x}}"
                    f"{detail_lines}<br>"
                    "%{y:.1f}% (%{customdata[0]} of %{customdata[1]} students combined)"
                    f"%{{customdata[2]}}<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title="Answer Choice Breakdown, Combined Across Exam A and Exam B",
        xaxis_title="Exam A Question Number",
        legend_title_text="Answer Option",
        barmode="stack",
        bargap=0.15,
        **_LAYOUT_DEFAULTS,
    )
    fig.update_xaxes(dtick=5, **_AXIS_DEFAULTS)
    fig.update_yaxes(range=[0, 100], title_text="Percent of Students", **_AXIS_DEFAULTS)
    return fig
