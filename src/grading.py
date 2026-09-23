"""Score each student's exam and compute their Total."""
from __future__ import annotations

import pandas as pd

from .reference import AnswerKeys

QUESTION_COLUMNS = list(range(1, 51))
POINTS_PER_QUESTION = 2


def build_correctness_mask(grading_df: pd.DataFrame, keys: AnswerKeys) -> pd.DataFrame:
    """Boolean mask, same shape/index as the question columns: True where correct."""
    records = []
    for _, row in grading_df.iterrows():
        version = str(row["Exam A or B?"]).strip().upper()
        records.append({q: keys.is_correct(version, q, row[q]) for q in QUESTION_COLUMNS})
    return pd.DataFrame(records, index=grading_df.index, columns=QUESTION_COLUMNS)


def score_grading_sheet(grading_df: pd.DataFrame, keys: AnswerKeys) -> pd.DataFrame:
    df = grading_df.copy()
    mask = build_correctness_mask(df, keys)
    raw_total = (mask.sum(axis=1) * POINTS_PER_QUESTION).astype(int)
    curve = df.pop("Curve") if "Curve" in df.columns else 0
    df.insert(1, "Total Before Curve", raw_total)
    df.insert(2, "Curve", curve)
    df.insert(3, "Total", df["Total Before Curve"] + df["Curve"])
    return df
