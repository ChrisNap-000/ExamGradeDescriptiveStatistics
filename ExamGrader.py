"""Exam Grade Descriptive Statistics - Streamlit app.

Upload one workbook containing a Grading/Reference sheet pair per exam
number (1-4). Tab 1 shows aggregate, masked statistics; Tab 2 shows the
unmasked student-level detail for the teacher's own reference.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts import difficulty_bar_chart, option_breakdown_chart, totals_boxplot, totals_histogram
from src.data_loader import WorkbookValidationError, load_grading_sheet, load_reference_sheet
from src.descriptive_stats import compute_kpis
from src.exam_document import missing_text_columns, render_answer_distributions
from src.grading import QUESTION_COLUMNS, build_correctness_mask, score_grading_sheet
from src.item_analysis import option_selection_breakdown, question_difficulty
from src.reference import build_answer_keys

st.set_page_config(page_title="Exam Grade Descriptive Statistics", page_icon="\U0001F4CA", layout="wide")

ACCENT = "#9E1B32"

KPI_CSS = f"""
<style>
.kpi-card {{
    background-color: #1a1a19;
    border: 1px solid #2c2c2a;
    border-left: 4px solid {ACCENT};
    border-radius: 10px;
    padding: 20px 10px;
    text-align: center;
}}
.kpi-label {{
    font-size: 1rem;
    font-weight: 600;
    color: #c3c2b7;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 8px;
}}
.kpi-value {{
    font-size: 3.2rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.1;
}}
</style>
"""

CORRECT_STYLE = "background-color: #0ca30c; color: #ffffff;"
INCORRECT_STYLE = "background-color: #d03b3b; color: #ffffff;"

st.markdown(KPI_CSS, unsafe_allow_html=True)
st.title("\U0001F4CA Exam Grade Descriptive Statistics")

uploaded_file = st.file_uploader("Upload exam workbook (.xlsx)", type=["xlsx"])
exam_number = st.selectbox("Which exam do you want to analyze?", options=[1, 2, 3, 4])

if uploaded_file is None:
    st.info("Upload a workbook to get started.")
    st.stop()

try:
    grading_df = load_grading_sheet(uploaded_file, exam_number)
    reference_df = load_reference_sheet(uploaded_file, exam_number)
except WorkbookValidationError as exc:
    st.error(str(exc))
    st.stop()

keys = build_answer_keys(reference_df)
graded_df = score_grading_sheet(grading_df, keys)

breakdown_df = option_selection_breakdown(graded_df, keys)

tab_stats, tab_detail, tab_distributions = st.tabs(
    ["\U0001F4C8 Class Statistics", "\U0001F9D1‍\U0001F393 Student Detail", "\U0001F4DD Answer Distributions"]
)

with tab_stats:
    st.caption("Aggregate statistics only — no student names appear on this tab.")

    curve = graded_df["Curve"]
    apply_curve = False
    if curve.any():
        apply_curve = st.toggle("Apply curve to statistics below", value=False)

    totals = graded_df["Total"] if apply_curve else graded_df["Total Before Curve"]

    kpis = compute_kpis(totals)
    kpi_cols = st.columns(len(kpis))
    for col, (label, value) in zip(kpi_cols, kpis.items()):
        col.markdown(
            f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    col_hist, col_box = st.columns(2)
    with col_hist:
        bin_size = st.number_input(
            "Bin size", min_value=1, max_value=50, value=2, step=1, key="grade_bin_size"
        )
        st.plotly_chart(totals_histogram(totals, bin_size), use_container_width=True)
    with col_box:
        st.container(height=70, border=False)
        st.plotly_chart(totals_boxplot(totals), use_container_width=True)

    st.subheader("Question Difficulty")
    st.caption(
        "Question numbers refer to Exam A's numbering. Since Exam A and Exam B "
        "shuffle the same 50 questions, results from both versions are combined "
        "into one bar per question. Hover a bar to see that question's number "
        "and correct answer on both versions."
    )
    difficulty_df = question_difficulty(graded_df, keys)
    st.plotly_chart(difficulty_bar_chart(difficulty_df), use_container_width=True)

    st.subheader("Answer Choice Breakdown")
    st.caption(
        "One stacked bar per question, ordered by Exam A's question number. "
        "Since Exam A and Exam B shuffle answer-choice order as well as "
        "question order, each segment is the same underlying option "
        "regardless of which letter it was labeled on either version's "
        "paper — the reference sheet's per-option mapping combines both "
        "versions into a single bar instead of splitting them. Hover a "
        "segment to see each version's own native letter and question "
        "number. The checkmark marks each question's correct option(s) — a "
        "question can have more than one accepted answer; \"No Answer\" "
        "(graded incorrect) covers blanks."
    )
    st.plotly_chart(option_breakdown_chart(breakdown_df), use_container_width=True)

with tab_detail:
    st.caption("Unmasked — for your own reference only. Green = correct, red = incorrect.")

    all_students = sorted(graded_df["Student"].astype(str).unique())
    # Keyed to the exam number + filename so switching exams/files doesn't leave a
    # stale student selection behind (which would error against the new roster).
    student_filter_key = f"student_filter_{exam_number}_{uploaded_file.name}"

    def _select_all_students() -> None:
        st.session_state[student_filter_key] = all_students

    def _clear_all_students() -> None:
        st.session_state[student_filter_key] = []

    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([4, 1, 1, 2])
    with filter_col1:
        selected_students = st.multiselect(
            "Filter by Student",
            options=all_students,
            default=all_students,
            key=student_filter_key,
        )
    with filter_col2:
        st.write("")
        st.button("Select All", on_click=_select_all_students, use_container_width=True)
    with filter_col3:
        st.write("")
        st.button("Clear All", on_click=_clear_all_students, use_container_width=True)
    with filter_col4:
        selected_version = st.selectbox("Filter by Exam Version", options=["All", "A", "B"])

    selected_versions = ["A", "B"] if selected_version == "All" else [selected_version]

    filtered_df = graded_df[
        graded_df["Student"].astype(str).isin(selected_students)
        & graded_df["Exam A or B?"].astype(str).str.upper().isin(selected_versions)
    ]

    display_cols = [
        "Student",
        "Total Before Curve",
        "Curve",
        "Total",
        "Exam A or B?",
    ] + QUESTION_COLUMNS
    display_df = filtered_df[display_cols]
    correctness_mask = build_correctness_mask(filtered_df, keys)

    def _highlight_correctness(data: pd.DataFrame) -> pd.DataFrame:
        styles = pd.DataFrame("", index=data.index, columns=data.columns)
        for q in QUESTION_COLUMNS:
            styles[q] = correctness_mask.loc[data.index, q].map(
                lambda correct: CORRECT_STYLE if correct else INCORRECT_STYLE
            )
        return styles

    styled_df = display_df.style.apply(_highlight_correctness, axis=None)

    row_height_px = 35
    table_height = row_height_px * (len(display_df) + 1) + 3
    st.dataframe(
        styled_df,
        height=table_height,
        use_container_width=True,
        column_config={
            "Student": None,
            "Total Before Curve": st.column_config.Column("Total"),
            "Total": st.column_config.Column("Total after Curve"),
        },
    )

with tab_distributions:
    st.caption("Aggregate statistics only — no student names appear on this tab.")

    missing_columns = missing_text_columns(reference_df)
    if missing_columns:
        st.info(
            "This tab needs the following column(s) on the "
            f"'Exam {exam_number} Reference' sheet: {', '.join(missing_columns)}."
        )
    else:
        distributions_md = render_answer_distributions(
            exam_number, len(graded_df), breakdown_df, reference_df
        )
        st.download_button(
            "Download as Markdown",
            data=distributions_md,
            file_name=f"Exam {exam_number} Answer Distributions.md",
            mime="text/markdown",
        )
        st.markdown(distributions_md)
