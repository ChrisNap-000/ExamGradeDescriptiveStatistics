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
        for q in QUESTION_COLUMNS:
            canonical_id = keys.canonical_id(version, q)
            total_counts[canonical_id] += 1
            if keys.is_correct(version, q, row[q]):
                correct_counts[canonical_id] += 1

    records = []
    for a_q in QUESTION_COLUMNS:
        b_q = keys.a_to_b[a_q]
        records.append(
            {
                "Exam A Question Number": a_q,
                "Exam A Answer": keys.correct_letters("A", a_q),
                "Exam B Question Number": b_q,
                "Exam B Answer": keys.correct_letters("B", b_q),
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
    """Per-question count of which underlying answer option students picked,
    combined across Exam A and Exam B.

    Exam A and Exam B shuffle answer-choice order as well as question order,
    so a raw letter alone doesn't identify an option across versions. The
    reference sheet maps each option pair explicitly (not just each question
    pair), so a student's selected letter is first translated to its
    canonical (Exam A) option identity via `keys.canonical_option` before
    being counted — letting both versions land in the same bucket instead of
    two separate per-version rows. Anything that doesn't map to a known
    option (a blank graded "NA", or stray data-entry noise) is bucketed as
    "NA" — a no-answer counts as incorrect either way.
    """
    counts: dict[tuple[int, str], int] = {}
    version_counts: dict[tuple[int, str, str], int] = {}
    totals: dict[int, int] = {}

    for _, row in graded_df.iterrows():
        version = str(row["Exam A or B?"]).strip().upper()
        for q in QUESTION_COLUMNS:
            a_q = keys.canonical_id(version, q)
            totals[a_q] = totals.get(a_q, 0) + 1
            letter = str(row[q]).strip().upper()
            option = keys.canonical_option(version, q, letter) or NO_ANSWER_OPTION
            counts[(a_q, option)] = counts.get((a_q, option), 0) + 1
            version_counts[(a_q, option, version)] = version_counts.get((a_q, option, version), 0) + 1

    records = []
    for a_q in QUESTION_COLUMNS:
        b_q = keys.a_to_b[a_q]
        total = totals.get(a_q, 0)
        correct_letters = keys.key_a.get(a_q, set())
        options = (*keys.canonical_options.get(a_q, KNOWN_OPTIONS), NO_ANSWER_OPTION)
        for option in options:
            count = counts.get((a_q, option), 0)
            is_na = option == NO_ANSWER_OPTION
            records.append(
                {
                    "Exam A Question Number": a_q,
                    "Exam B Question Number": b_q,
                    "Option": option,
                    "A Option": "" if is_na else option,
                    "B Option": "" if is_na else keys.b_option(a_q, option),
                    "Count": count,
                    "A Count": version_counts.get((a_q, option, "A"), 0),
                    "B Count": version_counts.get((a_q, option, "B"), 0),
                    "Total": total,
                    "Percent": count / total * 100 if total else 0.0,
                    "Is Correct": option in correct_letters,
                }
            )
    return pd.DataFrame(records)
