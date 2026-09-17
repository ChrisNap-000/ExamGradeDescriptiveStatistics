"""Unit tests for the grading, reference-mapping, and item-analysis logic.

These exercise the two trickiest correctness traps in this app: the pandas
"NA"-as-NaN gotcha (see data_loader.py), and the Exam-A<->Exam-B canonical
question mapping used for item analysis (see reference.py / item_analysis.py).
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import openpyxl
import pandas as pd
import pytest

from src.data_loader import load_grading_sheet, load_reference_sheet, WorkbookValidationError
from src.grading import build_correctness_mask, score_grading_sheet
from src.item_analysis import question_difficulty
from src.reference import build_answer_keys

EXAM_NUMBER = 1
SHIFT = 25  # self-inverse cyclic shift over 1..50, used to build a synthetic A<->B mapping


def _b_question(a_question: int) -> int:
    return ((a_question - 1 + SHIFT) % 50) + 1


def _reference_df() -> pd.DataFrame:
    rows = []
    for a_q in range(1, 51):
        b_q = _b_question(a_q)
        rows.append(
            {
                "A - Questions": a_q,
                f"Exam {EXAM_NUMBER}A Answer": "A",
                "B - Questions": b_q,
                f"Exam {EXAM_NUMBER}B Answer": "B",
            }
        )
    return pd.DataFrame(rows)


def _grading_df() -> pd.DataFrame:
    student_1 = {"Student": "Alice", "Exam A or B?": "A", **{q: "A" for q in range(1, 51)}}
    student_2 = {"Student": "Bob", "Exam A or B?": "B", **{q: "B" for q in range(1, 51)}}
    student_3 = {
        "Student": "Carol",
        "Exam A or B?": "A",
        **{q: "A" for q in range(1, 26)},
        **{q: "X" for q in range(26, 51)},
    }
    return pd.DataFrame([student_1, student_2, student_3])


def test_score_grading_sheet():
    keys = build_answer_keys(_reference_df(), EXAM_NUMBER)
    graded = score_grading_sheet(_grading_df(), keys)

    assert graded.set_index("Student")["Total"].to_dict() == {
        "Alice": 100,
        "Bob": 100,
        "Carol": 50,
    }


def test_build_answer_keys_mapping():
    keys = build_answer_keys(_reference_df(), EXAM_NUMBER)

    assert keys.key_a[1] == "A"
    assert keys.key_b[_b_question(1)] == "B"
    assert keys.a_to_b[1] == _b_question(1)
    assert keys.b_to_a[_b_question(1)] == 1
    assert keys.canonical_id("B", _b_question(7)) == 7


def test_build_correctness_mask():
    grading_df = _grading_df()
    keys = build_answer_keys(_reference_df(), EXAM_NUMBER)
    mask = build_correctness_mask(grading_df, keys)

    carol_index = grading_df.index[grading_df["Student"] == "Carol"][0]
    assert mask.loc[carol_index, list(range(1, 26))].all()
    assert not mask.loc[carol_index, list(range(26, 51))].any()


def test_question_difficulty_combines_versions_and_carries_tooltip_fields():
    keys = build_answer_keys(_reference_df(), EXAM_NUMBER)
    graded = score_grading_sheet(_grading_df(), keys)
    difficulty = question_difficulty(graded, keys)

    # sorted ascending by Exam A Question Number, not by Percent Correct
    assert difficulty["Exam A Question Number"].tolist() == list(range(1, 51))

    by_question = difficulty.set_index("Exam A Question Number")["Percent Correct"].to_dict()
    easy_questions = {q for q in range(1, 26)}
    hard_questions = {q for q in range(26, 51)}

    assert all(by_question[q] == pytest.approx(100.0) for q in easy_questions)
    assert all(by_question[q] == pytest.approx(200 / 3) for q in hard_questions)

    row_q1 = difficulty[difficulty["Exam A Question Number"] == 1].iloc[0]
    assert row_q1["Exam A Answer"] == "A"
    assert row_q1["Exam B Question Number"] == _b_question(1)
    assert row_q1["Exam B Answer"] == "B"


def test_load_grading_sheet_preserves_literal_na():
    """Blank answers are pre-filled by the teacher as the literal string "NA".

    pandas treats "NA" as a default missing-value token on read_excel, so
    without keep_default_na=False this would silently become NaN instead of
    the literal string the scoring logic compares against.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Exam {EXAM_NUMBER} Grading"

    header = ["Student", "Total", "Exam A or B?"] + list(range(1, 51))
    ws.append(header)

    row = ["Dana", 0, "A"] + ["A"] * 50
    row[header.index(1)] = "NA"  # blank answer to question 1
    ws.append(row)

    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir) / "workbook.xlsx"
        wb.save(path)

        df = load_grading_sheet(str(path), EXAM_NUMBER)

    assert df.loc[0, 1] == "NA"
    assert "Total" not in df.columns


def test_load_grading_sheet_works_without_total_column():
    """Total is optional in the source workbook, not required."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Exam {EXAM_NUMBER} Grading"

    header = ["Student", "Exam A or B?"] + list(range(1, 51))  # no Total column
    ws.append(header)
    ws.append(["Erin", "A"] + ["A"] * 50)

    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir) / "workbook.xlsx"
        wb.save(path)

        grading_df = load_grading_sheet(str(path), EXAM_NUMBER)

    assert "Total" not in grading_df.columns

    keys = build_answer_keys(_reference_df(), EXAM_NUMBER)
    graded = score_grading_sheet(grading_df, keys)
    assert graded.set_index("Student")["Total"].to_dict() == {"Erin": 100}


def test_load_grading_sheet_missing_sheet_raises():
    wb = openpyxl.Workbook()
    wb.active.title = "Some Other Sheet"

    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir) / "workbook.xlsx"
        wb.save(path)

        with pytest.raises(WorkbookValidationError):
            load_grading_sheet(str(path), EXAM_NUMBER)


def test_load_reference_sheet_wrong_row_count_raises():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Exam {EXAM_NUMBER} Reference"
    ws.append(["A - Questions", f"Exam {EXAM_NUMBER}A Answer", "B - Questions", f"Exam {EXAM_NUMBER}B Answer"])
    ws.append([1, "A", 1, "A"])  # only 1 row, should be 50

    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir) / "workbook.xlsx"
        wb.save(path)

        with pytest.raises(WorkbookValidationError):
            load_reference_sheet(str(path), EXAM_NUMBER)
