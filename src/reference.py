"""Build per-version answer keys and the canonical A<->B option mapping.

The reference sheet is "melted": one row per (question, option) pair rather
than one row per question, since Exam A and Exam B shuffle answer-choice
order as well as question order. A row's `Correct` flag (0/1) marks an
option pair that counts as that question's right answer - a question can
have more than one row flagged correct (e.g. a question thrown out for
accepting multiple answers), so the accepted answer per question is a set,
not a single letter. Exam A's own lettering is used as the canonical option
identity, so a student's raw answer letter - on either version - can be
translated into "which underlying option did they pick" for combined item
analysis.
"""
from __future__ import annotations

import pandas as pd


class AnswerKeys:
    def __init__(
        self,
        key_a: dict[int, set[str]],
        key_b: dict[int, set[str]],
        a_to_b: dict[int, int],
        b_to_a: dict[int, int],
        option_map: dict[tuple[str, int, str], str],
        canonical_options: dict[int, list[str]],
        b_option_for: dict[tuple[int, str], str],
    ):
        self.key_a = key_a
        self.key_b = key_b
        self.a_to_b = a_to_b
        self.b_to_a = b_to_a
        self.canonical_options = canonical_options
        self._option_map = option_map
        self._b_option_for = b_option_for

    def key_for(self, version: str) -> dict[int, set[str]]:
        return self.key_a if version.strip().upper() == "A" else self.key_b

    def canonical_id(self, version: str, question_number: int) -> int:
        """The underlying (Exam-A-numbered) question identity for item analysis."""
        if version.strip().upper() == "A":
            return question_number
        return self.b_to_a[question_number]

    def is_correct(self, version: str, native_question_number: int, letter: str) -> bool:
        """Whether `letter` is one of the accepted answers for this version's
        native question number (a question may accept more than one)."""
        accepted = self.key_for(version).get(native_question_number, set())
        return str(letter).strip().upper() in accepted

    def correct_letters(self, version: str, native_question_number: int) -> str:
        """All accepted letters for this version's native question number,
        joined for display (e.g. "A" or "A / C" if more than one is accepted)."""
        accepted = self.key_for(version).get(native_question_number, set())
        return " / ".join(sorted(accepted))

    def canonical_option(self, version: str, native_question_number: int, letter: str) -> str | None:
        """Map a selected letter on the given version/question to its canonical
        (Exam A) option identity, or None if the letter isn't a recognized
        option for that question (a blank or stray data-entry value)."""
        return self._option_map.get((version.strip().upper(), native_question_number, letter.strip().upper()))

    def b_option(self, a_question: int, canonical_letter: str) -> str:
        """The Exam B sheet's own letter for a canonical (Exam A) option."""
        return self._b_option_for.get((a_question, canonical_letter), "")


def build_answer_keys(reference_df: pd.DataFrame) -> AnswerKeys:
    key_a: dict[int, set[str]] = {}
    key_b: dict[int, set[str]] = {}
    a_to_b: dict[int, int] = {}
    b_to_a: dict[int, int] = {}
    option_map: dict[tuple[str, int, str], str] = {}
    canonical_options: dict[int, list[str]] = {}
    b_option_for: dict[tuple[int, str], str] = {}

    for _, row in reference_df.iterrows():
        a_q = int(row["A - Question"])
        a_opt = str(row["A - Option"]).strip().upper()
        b_q = int(row["B - Question"])
        b_opt = str(row["B - Option"]).strip().upper()
        correct = int(row["Correct"]) == 1

        a_to_b[a_q] = b_q
        b_to_a[b_q] = a_q
        option_map[("A", a_q, a_opt)] = a_opt
        option_map[("B", b_q, b_opt)] = a_opt
        b_option_for[(a_q, a_opt)] = b_opt
        canonical_options.setdefault(a_q, []).append(a_opt)

        if correct:
            key_a.setdefault(a_q, set()).add(a_opt)
            key_b.setdefault(b_q, set()).add(b_opt)

    canonical_options = {q: sorted(opts) for q, opts in canonical_options.items()}
    return AnswerKeys(
        key_a=key_a,
        key_b=key_b,
        a_to_b=a_to_b,
        b_to_a=b_to_a,
        option_map=option_map,
        canonical_options=canonical_options,
        b_option_for=b_option_for,
    )
