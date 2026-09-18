"""Per-question difficulty, combined across exam A and B via the reference mapping."""
from __future__ import annotations

import pandas as pd

from .grading import QUESTION_COLUMNS
from .reference import AnswerKeys

KNOWN_OPTIONS = ("A", "B", "C", "D", "E")
NO_ANSWER_OPTION = "NA"


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
                "Number Correct": correct_counts[a_q],
                "Number of Students": total_counts[a_q],
            }
        )
    return pd.DataFrame(records).sort_values(
        "Exam A Question Number", kind="mergesort"
    ).reset_index(drop=True)


def option_selection_breakdown(graded_df: pd.DataFrame, keys: AnswerKeys) -> pd.DataFrame:
    """Per-question, per-version count of which answer option students picked.

    Kept separate per exam version (never merged into one row) because Exam A
    and Exam B shuffle answer choices, so option "C" on one version isn't
    necessarily the same underlying distractor as option "C" on the other.
    Anything other than A-E (a blank graded "NA", or stray data-entry noise)
    is bucketed as "NA" — a no-answer counts as incorrect either way.
    """
    counts: dict[tuple[int, str, str], int] = {}
    totals: dict[tuple[int, str], int] = {}

    for _, row in graded_df.iterrows():
        version = str(row["Exam A or B?"]).strip().upper()
        for q in QUESTION_COLUMNS:
            canonical_id = keys.canonical_id(version, q)
            totals[(canonical_id, version)] = totals.get((canonical_id, version), 0) + 1
            letter = str(row[q]).strip().upper()
            option = letter if letter in KNOWN_OPTIONS else NO_ANSWER_OPTION
            count_key = (canonical_id, version, option)
            counts[count_key] = counts.get(count_key, 0) + 1

    records = []
    for a_q in QUESTION_COLUMNS:
        b_q = keys.a_to_b[a_q]
        for version, native_q in (("A", a_q), ("B", b_q)):
            total = totals.get((a_q, version), 0)
            correct_letter = keys.key_for(version).get(native_q)
            for option in (*KNOWN_OPTIONS, NO_ANSWER_OPTION):
                count = counts.get((a_q, version, option), 0)
                records.append(
                    {
                        "Exam A Question Number": a_q,
                        "Native Question Number": native_q,
                        "Version": version,
                        "Option": option,
                        "Count": count,
                        "Total": total,
                        "Percent": count / total * 100 if total else 0.0,
                        "Is Correct": option == correct_letter,
                    }
                )
    return pd.DataFrame(records)
