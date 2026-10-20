"""Render the exam-style "Answer Distributions" markdown from a template file."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .item_analysis import NO_ANSWER_OPTION

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
TEMPLATE_NAME = "answer_distributions.md"
TEXT_COLUMNS = ("Question Text", "Answer Text")
_BLANK_TEXT = "—"
QUESTION_MAP_ROWS = 10

# Streamlit treats $...$ as LaTeX, and | would split a table cell, so all of
# these are backslash-escaped (standard CommonMark, so any viewer shows them plainly).
_MD_ESCAPES = str.maketrans({char: "\\" + char for char in "\\|$*_`<"})


def md_escape(value: object) -> str:
    text = " ".join(str(value).split())
    return text.translate(_MD_ESCAPES)


def missing_text_columns(reference_df: pd.DataFrame) -> list[str]:
    return [column for column in TEXT_COLUMNS if column not in reference_df.columns]


def _clean(value: object) -> str:
    return "" if pd.isna(value) else str(value).strip()


def build_question_blocks(breakdown_df: pd.DataFrame, reference_df: pd.DataFrame) -> list[dict]:
    question_text: dict[int, str] = {}
    answer_text: dict[tuple[int, str], str] = {}
    for _, row in reference_df.iterrows():
        a_q = int(row["A - Question"])
        a_opt = str(row["A - Option"]).strip().upper()
        text = _clean(row["Question Text"])
        if text and a_q not in question_text:
            question_text[a_q] = text
        answer_text[(a_q, a_opt)] = _clean(row["Answer Text"])

    blocks = []
    for a_q, group in breakdown_df.groupby("Exam A Question Number", sort=True):
        options = []
        no_answer = {"percent": "0.0", "count": 0}
        for _, row in group.iterrows():
            percent = f"{row['Percent']:.1f}"
            if row["Option"] == NO_ANSWER_OPTION:
                no_answer = {"percent": percent, "count": int(row["Count"])}
                continue
            options.append(
                {
                    "letter": row["Option"],
                    "text": answer_text.get((int(a_q), row["Option"])) or _BLANK_TEXT,
                    "percent": percent,
                    "count": int(row["Count"]),
                    "is_correct": bool(row["Is Correct"]),
                }
            )
        blocks.append(
            {
                "a_number": int(a_q),
                "b_number": int(group["Exam B Question Number"].iloc[0]),
                "text": question_text.get(int(a_q)) or _BLANK_TEXT,
                "options": options,
                "no_answer": no_answer,
            }
        )
    return blocks


def build_question_map(breakdown_df: pd.DataFrame, rows_per_group: int = QUESTION_MAP_ROWS) -> list[list[dict]]:
    """Exam B question numbers in order, each with its Exam A question, laid out
    as table rows: consecutive runs of `rows_per_group` Exam B questions sit
    side by side (row 1 holds B1, B11, B21, ...) so the table stays short."""
    pairs = breakdown_df[["Exam B Question Number", "Exam A Question Number"]].drop_duplicates()
    ordered = [
        {"b_number": int(b_q), "a_number": int(a_q)}
        for b_q, a_q in sorted(pairs.itertuples(index=False, name=None))
    ]
    groups = [ordered[i:i + rows_per_group] for i in range(0, len(ordered), rows_per_group)]
    blank = {"b_number": "", "a_number": ""}
    return [
        [group[r] if r < len(group) else blank for group in groups]
        for r in range(min(rows_per_group, len(ordered)))
    ]


def render_answer_distributions(
    exam_number: int,
    total_students: int,
    breakdown_df: pd.DataFrame,
    reference_df: pd.DataFrame,
) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        undefined=StrictUndefined,
    )
    env.filters["md"] = md_escape
    return env.get_template(TEMPLATE_NAME).render(
        exam_number=exam_number,
        total_students=total_students,
        question_map=build_question_map(breakdown_df),
        questions=build_question_blocks(breakdown_df, reference_df),
    )
