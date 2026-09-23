# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
pip install -r requirements.txt
streamlit run ExamGrader.py                     # run the app locally
pytest tests/                                   # full suite
pytest tests/test_grading.py::test_score_grading_sheet   # single test
```

`tests/test_app.py::test_kpi_cards_render_expected_values` currently fails: it asserts `"83.33"`, but `compute_kpis` rounds to one decimal (`83.3`). Don't count it as a regression you caused.

There is no linter or build step. The app is deployed on Streamlit Community Cloud from this repo (link in README).

## What the app does

A Streamlit app for a teacher. They upload one `.xlsx` workbook, pick exam 1–4, and get stats for a 50-question exam given in two shuffled versions (A and B). Each exam number needs two sheets, `Exam {n} Grading` and `Exam {n} Reference`. `docs/DATA_FORMAT.md` is the authoritative spec for the workbook format. Update it when the expected input columns change.

## Architecture

`ExamGrader.py` is the Streamlit entry point. It runs top to bottom on every interaction: load, build keys, score, then render three tabs (Class Statistics, Student Detail, Answer Distributions). The logic lives in `src/`, and the entry point only handles layout.

Data flow:
1. `data_loader.py` reads and validates both sheets and raises `WorkbookValidationError` with a message the user can read. Question columns are renamed to the ints `1..50`. Any `Total` column in the upload is dropped, because the app always recomputes it. An optional `Curve` column is coerced to numeric and defaults to 0.
2. `reference.py` → `build_answer_keys()` returns an `AnswerKeys` object. The Reference sheet is **melted**: it has one row per (question, option) pair (`A - Question`, `A - Option`, `B - Question`, `B - Option`, `Correct`), because the two versions shuffle answer-choice order as well as question order. **Exam A's numbering and lettering is the canonical identity.** Every Exam B answer is translated back to its Exam A question and option, so item analysis combines both versions into a single row or bar per question. A question can have more than one correct option (for example, a thrown-out question), so each answer key is a `set` of letters.
3. `grading.py` → `score_grading_sheet()` scores 2 points per question and adds three columns: `Total Before Curve` (raw score), `Curve`, and `Total` (raw + curve). `build_correctness_mask()` is reused by the Student Detail tab to color cells.
4. `item_analysis.py` produces per-question difficulty and the option-selection breakdown, both keyed by the canonical Exam A question. Blank or unrecognized answers go into an `"NA"` bucket (`NO_ANSWER_OPTION`) and are never dropped.
5. `charts.py` builds Plotly figures and `descriptive_stats.py` computes the KPI values. Both take plain Series or DataFrames.
6. `exam_document.py` renders `templates/answer_distributions.md`, a Jinja2 template using `StrictUndefined`, into downloadable markdown. It only works if the Reference sheet has the optional `Question Text` and `Answer Text` columns. Text passed through the `md` filter is escaped because Streamlit treats `$…$` as LaTeX and `|` would break table cells.

## Conventions and gotchas

- **Read the Grading sheet with `keep_default_na=False`.** Teachers enter blank answers as the literal string `NA`, and pandas' default settings would turn that into NaN. The Reference sheet uses `keep_default_na=False, na_values=[""]` for the same reason, since answer text can legitimately be "None" or "N/A". A test covers this.
- **Privacy:** the Class Statistics and Answer Distributions tabs must never show student names. `test_app.py` checks this. On Student Detail, the `Student` column is hidden by default through `column_config={"Student": None}`.
- The curve is off by default on Class Statistics. A toggle switches the KPIs and charts between `Total Before Curve` and `Total`. Student Detail relabels its columns with `column_config`: `Total Before Curve` is shown as "Total" and `Total` as "Total after Curve". The underlying column names stay the same because other code depends on them.
- Theming is fixed dark, set in `.streamlit/config.toml`, with the brand accent Crimson `#9E1B32`. Chart colors are constants at the top of `charts.py`.
- `tests/test_app.py` drives the real script headlessly with `streamlit.testing.v1.AppTest` using workbooks built in memory with openpyxl. It must be run from the repo root so that `src` imports resolve. `*.xlsx` files are gitignored, so don't commit sample workbooks.
