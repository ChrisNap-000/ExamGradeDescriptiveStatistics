"""Build per-version answer keys and the canonical A<->B question mapping."""
from __future__ import annotations

import pandas as pd


class AnswerKeys:
    def __init__(
        self,
        key_a: dict[int, str],
        key_b: dict[int, str],
        a_to_b: dict[int, int],
        b_to_a: dict[int, int],
    ):
        self.key_a = key_a
        self.key_b = key_b
        self.a_to_b = a_to_b
        self.b_to_a = b_to_a

    def key_for(self, version: str) -> dict[int, str]:
        return self.key_a if version.strip().upper() == "A" else self.key_b

    def canonical_id(self, version: str, question_number: int) -> int:
        """The underlying (Exam-A-numbered) question identity for item analysis."""
        if version.strip().upper() == "A":
            return question_number
        return self.b_to_a[question_number]


def build_answer_keys(reference_df: pd.DataFrame, exam_number: int) -> AnswerKeys:
    a_ans_col = f"Exam {exam_number}A Answer"
    b_ans_col = f"Exam {exam_number}B Answer"

    key_a: dict[int, str] = {}
    key_b: dict[int, str] = {}
    a_to_b: dict[int, int] = {}
    b_to_a: dict[int, int] = {}

    for _, row in reference_df.iterrows():
        a_q = int(row["A - Questions"])
        b_q = int(row["B - Questions"])
        key_a[a_q] = str(row[a_ans_col]).strip().upper()
        key_b[b_q] = str(row[b_ans_col]).strip().upper()
        a_to_b[a_q] = b_q
        b_to_a[b_q] = a_q

    return AnswerKeys(key_a=key_a, key_b=key_b, a_to_b=a_to_b, b_to_a=b_to_a)
