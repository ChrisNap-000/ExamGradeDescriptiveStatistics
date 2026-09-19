"""Tests for the exam-style Answer Distributions markdown rendering."""
from __future__ import annotations

import re

import pandas as pd

from src.exam_document import md_escape, missing_text_columns, render_answer_distributions
from src.item_analysis import option_selection_breakdown
from src.reference import build_answer_keys

SHIFT = 25


def _b_question(a_question: int) -> int:
    return ((a_question - 1 + SHIFT) % 50) + 1


def _reference_df(extra_correct_a_q: int | None = None) -> pd.DataFrame:
    """Two options per question (A correct, B distractor); question 3 has 4
    options and question 4 has 5, so option counts vary. Optionally flags
    Exam A option B as also correct for one question."""
    rows = []
    for a_q in range(1, 51):
        b_q = _b_question(a_q)
        n_options = {3: 4, 4: 5}.get(a_q, 2)
        for i in range(n_options):
            letter = "ABCDE"[i]
            b_letter = "ABCDE"[(i + 1) % n_options]
            correct = 1 if i == 0 or (a_q == extra_correct_a_q and i == 1) else 0
            rows.append(
                {
                    "A - Question": a_q,
                    "A - Option": letter,
                    "B - Question": b_q,
                    "B - Option": b_letter,
                    "Correct": correct,
                    "Question Text": f"Question text {a_q}",
                    "Answer Text": f"Answer {letter} for {a_q}",
                }
            )
    return pd.DataFrame(rows)


def _render(reference_df: pd.DataFrame, students: list[dict] | None = None) -> str:
    keys = build_answer_keys(reference_df)
    if students is None:
        students = [
            {"Student": "Alice", "Exam A or B?": "A", **{q: "A" for q in range(1, 51)}},
            {"Student": "Carol", "Exam A or B?": "A", **{q: "X" for q in range(1, 51)}},
        ]
    graded = pd.DataFrame(students)
    breakdown = option_selection_breakdown(graded, keys)
    return render_answer_distributions(1, len(graded), breakdown, reference_df)


def test_renders_one_section_per_question_in_exam_a_order():
    md = _render(_reference_df())

    numbers = [int(n) for n in re.findall(r"^### Question (\d+) ", md, flags=re.MULTILINE)]
    assert numbers == list(range(1, 51))
    assert "# Exam 1 - Answer Distributions" in md
    assert "2 students" in md


def test_heading_shows_exam_a_and_exam_b_question_numbers():
    md = _render(_reference_df())

    assert f"### Question 1 (Exam B: Question {_b_question(1)})" in md
    assert "Question text 1" in md


def test_correct_option_is_bold_with_checkmark_and_others_are_plain():
    md = _render(_reference_df())

    # Alice picked A (correct) on every question; Carol's "X" is No Answer.
    assert "| **A** | **Answer A for 1 ✓** | **50.0%** | **1** |" in md
    assert "| B | Answer B for 1 | 0.0% | 0 |" in md
    assert "| No Answer | | 50.0% | 1 |" in md


def test_no_answer_row_only_shown_when_someone_left_the_question_blank():
    students = [
        {"Student": "Alice", "Exam A or B?": "A", **{q: "A" for q in range(1, 51)}},
        # Dave answers everything except question 1.
        {"Student": "Dave", "Exam A or B?": "A", 1: "X", **{q: "A" for q in range(2, 51)}},
    ]
    md = _render(_reference_df(), students)

    def section(number: int) -> str:
        return md.split(f"### Question {number} ")[1].split("### Question")[0]

    assert "| No Answer | | 50.0% | 1 |" in section(1)
    assert "No Answer" not in section(2)
    assert md.count("No Answer") == 1
    assert "| **A** | **Answer A for 2 ✓** | **100.0%** | **2** |" in section(2)


def test_tables_end_with_a_blank_line_so_no_blank_row_is_absorbed():
    """A non-pipe line directly under a table row (like the &nbsp; spacer) is
    parsed as one more table row, showing up as an empty record."""
    fully_answered = [{"Student": "Alice", "Exam A or B?": "A", **{q: "A" for q in range(1, 51)}}]
    for md in (_render(_reference_df()), _render(_reference_df(), fully_answered)):
        lines = md.splitlines()
        table_ends = [
            i for i, line in enumerate(lines)
            if line.startswith("|") and not (i + 1 < len(lines) and lines[i + 1].startswith("|"))
        ]
        assert len(table_ends) == 50
        assert all(i + 1 >= len(lines) or lines[i + 1] == "" for i in table_ends)


def test_multiple_correct_answers_are_all_bold():
    md = _render(_reference_df(extra_correct_a_q=1))

    assert "| **A** | **Answer A for 1 ✓**" in md
    assert "| **B** | **Answer B for 1 ✓**" in md


def test_options_listed_in_exam_a_letter_order_and_only_real_options():
    md = _render(_reference_df())

    def section(number: int) -> str:
        return md.split(f"### Question {number} ")[1].split("### Question")[0]

    assert re.findall(r"^\| \**([A-E])\**", section(5), flags=re.MULTILINE) == ["A", "B"]
    assert re.findall(r"^\| \**([A-E])\**", section(3), flags=re.MULTILINE) == ["A", "B", "C", "D"]
    assert re.findall(r"^\| \**([A-E])\**", section(4), flags=re.MULTILINE) == ["A", "B", "C", "D", "E"]


def test_percentages_including_no_answer_sum_to_100():
    md = _render(_reference_df())
    section = md.split("### Question 1 ")[1].split("### Question")[0]

    percents = [float(p) for p in re.findall(r"(\d+\.\d)%", section)]
    assert sum(percents) == 100.0


def test_text_is_escaped_so_it_cannot_break_the_table_or_render_as_math():
    reference_df = _reference_df()
    reference_df.loc[
        (reference_df["A - Question"] == 1) & (reference_df["A - Option"] == "A"), "Answer Text"
    ] = "Costs $5 | $10\nper *unit*"
    reference_df.loc[reference_df["A - Question"] == 1, "Question Text"] = "Line one\nline two_x"

    md = _render(reference_df)

    assert r"Costs \$5 \| \$10 per \*unit\*" in md
    assert r"Line one line two\_x" in md


def test_blank_text_falls_back_to_a_placeholder_instead_of_broken_bold():
    reference_df = _reference_df()
    reference_df.loc[
        (reference_df["A - Question"] == 1) & (reference_df["A - Option"] == "A"), "Answer Text"
    ] = ""

    md = _render(reference_df)

    assert "| **A** | **— ✓** |" in md


def test_missing_text_columns_detected():
    reference_df = _reference_df()

    assert missing_text_columns(reference_df) == []
    assert missing_text_columns(reference_df.drop(columns=["Answer Text"])) == ["Answer Text"]
    assert missing_text_columns(
        reference_df.drop(columns=["Question Text", "Answer Text"])
    ) == ["Question Text", "Answer Text"]


def test_md_escape_collapses_whitespace_and_escapes_specials():
    assert md_escape("a\n  b") == "a b"
    assert md_escape("x|y $z `c` <t>") == r"x\|y \$z \`c\` \<t>"
