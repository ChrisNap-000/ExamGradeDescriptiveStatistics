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
        key = keys.key_for(version)
        records.append({q: str(row[q]).strip().upper() == key.get(q) for q in QUESTION_COLUMNS})
    return pd.DataFrame(records, index=grading_df.index, columns=QUESTION_COLUMNS)


def score_grading_sheet(grading_df: pd.DataFrame, keys: AnswerKeys) -> pd.DataFrame:
    df = grading_df.copy()
    mask = build_correctness_mask(df, keys)
    df.insert(1, "Total", (mask.sum(axis=1) * POINTS_PER_QUESTION).astype(int))
    return df
