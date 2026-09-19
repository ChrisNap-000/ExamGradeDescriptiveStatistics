"""Load and validate the uploaded exam workbook."""
from __future__ import annotations

import pandas as pd

REQUIRED_GRADING_COLUMNS = {"Student", "Exam A or B?"}
QUESTION_COLUMNS = list(range(1, 51))


class WorkbookValidationError(Exception):
    """Raised when the uploaded workbook doesn't match the expected shape."""


def _rename_question_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    for c in df.columns:
        s = str(c).strip()
        if s.isdigit() and 1 <= int(s) <= 50:
            rename[c] = int(s)
    return df.rename(columns=rename)


def load_grading_sheet(file, exam_number: int) -> pd.DataFrame:
    sheet_name = f"Exam {exam_number} Grading"
    try:
        # keep_default_na=False is required: pandas otherwise treats the
        # literal "NA" answers teachers fill in for blanks as real NaN.
        df = pd.read_excel(file, sheet_name=sheet_name, keep_default_na=False)
    except ValueError as exc:
        raise WorkbookValidationError(
            f"Sheet '{sheet_name}' was not found in the uploaded workbook."
        ) from exc

    df.columns = [str(c).strip() for c in df.columns]
    df = _rename_question_columns(df)

    missing = REQUIRED_GRADING_COLUMNS - set(df.columns)
    if missing:
        raise WorkbookValidationError(
            f"Sheet '{sheet_name}' is missing required column(s): {', '.join(sorted(missing))}"
        )

    missing_questions = [q for q in QUESTION_COLUMNS if q not in df.columns]
    if missing_questions:
        raise WorkbookValidationError(
            f"Sheet '{sheet_name}' is missing question column(s): {missing_questions}"
        )

    if "Total" in df.columns:
        df = df.drop(columns=["Total"])

    return df


def load_reference_sheet(file, exam_number: int) -> pd.DataFrame:
    """Load the "melted" reference sheet: one row per (question, option) pair
    rather than one row per question, since Exam A and Exam B shuffle
    answer-choice order as well as question order."""
    sheet_name = f"Exam {exam_number} Reference"
    try:
        df = pd.read_excel(file, sheet_name=sheet_name)
    except ValueError as exc:
        raise WorkbookValidationError(
            f"Sheet '{sheet_name}' was not found in the uploaded workbook."
        ) from exc

    df.columns = [str(c).strip() for c in df.columns]

    required = {"A - Question", "A - Option", "B - Question", "B - Option", "Correct"}
    missing = required - set(df.columns)
    if missing:
        raise WorkbookValidationError(
            f"Sheet '{sheet_name}' is missing required column(s): {', '.join(sorted(missing))}"
        )

    distinct_questions = df["A - Question"].nunique()
    if distinct_questions != 50:
        raise WorkbookValidationError(
            f"Sheet '{sheet_name}' should cover 50 questions (one per 'A - Question' value), "
            f"found {distinct_questions}."
        )

    # A question may have more than one row flagged correct (e.g. a question
    # thrown out for accepting multiple answers) - only zero is invalid.
    correct_counts = df.groupby("A - Question")["Correct"].sum()
    bad_questions = sorted(correct_counts[correct_counts < 1].index.tolist())
    if bad_questions:
        raise WorkbookValidationError(
            f"Sheet '{sheet_name}' should have at least one correct option per question; "
            f"question(s) with none flagged: {bad_questions}"
        )

    return df
