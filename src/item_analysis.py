"""Per-question difficulty, combined across exam A and B via the reference mapping."""
from __future__ import annotations

import pandas as pd

from .grading import QUESTION_COLUMNS
from .reference import AnswerKeys


def question_difficulty(graded_df: pd.DataFrame, keys: AnswerKeys) -> pd.DataFrame:
    correct_counts = {q: 0 for q in QUESTION_COLUMNS}
    total_counts = {q: 0 for q in QUESTION_COLUMNS}

    for _, row in graded_df.iterrows():
        version = str(row["Exam A or B?"]).strip().upper()
        key = keys.key_for(version)
        for q in QUESTION_COLUMNS:
            canonical_id = keys.canonical_id(version, q)
            total_counts[canonical_id] += 1
            if str(row[q]).strip().upper() == key.get(q):
                correct_counts[canonical_id] += 1

    records = []
    for a_q in QUESTION_COLUMNS:
        b_q = keys.a_to_b[a_q]
        records.append(
            {
                "Exam A Question Number": a_q,
                "Exam A Answer": keys.key_a.get(a_q, ""),
                "Exam B Question Number": b_q,
                "Exam B Answer": keys.key_b.get(b_q, ""),
                "Percent Correct": (
                    correct_counts[a_q] / total_counts[a_q] * 100 if total_counts[a_q] else 0.0
                ),
            }
        )
    return pd.DataFrame(records).sort_values(
        "Exam A Question Number", kind="mergesort"
    ).reset_index(drop=True)
