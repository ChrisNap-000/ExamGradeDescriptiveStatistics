# 📊 Exam Grade Descriptive Statistics

## [Exam Grader App](https://examgradedescriptivestatistics-6hjxforidkvcbx3fyfnzpi.streamlit.app)

A Streamlit app that turns one exam workbook into instant descriptive statistics —
without ever putting a student's name on screen when you don't want it to.

You give two versions of the same 50-question exam (**A** and **B**) — same
questions, shuffled order, shuffled answer choices, to cut down on cheating. This
app grades both versions correctly using a single answer-key sheet, then shows you
the numbers that matter.

## ✨ What it does

- 📤 **One upload.** Drop in a single `.xlsx` workbook — the app reads the grading
  data and the answer key straight out of it.
- 🔢 **Pick an exam.** Choose exam 1–4 and the app looks up the matching sheets.
- 🧮 **Grades both versions correctly.** Handles the A↔B question shuffle for you —
  2 points per correct answer, 50 questions, done.
- 🙈 **Masked class view.** Large, prominent KPI cards (mean, median, mode, min, max,
  range, standard deviation), a fixed-scale (0–100) histogram and boxplot, and a
  per-question difficulty chart ordered by question number with a detailed hover
  tooltip — **no student names, ever, on this tab.**
- 🧑‍🎓 **Unmasked detail view.** A second tab with the full student-level table
  (name, total, version, every raw answer), filterable by student and exam version,
  with each answer color-coded correct/incorrect. The `Student` column is hidden by
  default (unhide it anytime from the table's column toolbar) for extra privacy.
- 🎨 **School-branded dark theme.** Fixed dark theme using your Crimson accent color.

## 🚀 Quick start

```bash
pip install -r requirements.txt
streamlit run ExamGrader.py
```

Then open the local URL Streamlit prints, upload your workbook, and pick an exam
number.

## 📁 Project layout

```
ExamGrader.py            Streamlit entrypoint
.streamlit/
  config.toml             Fixed dark theme + brand accent color
src/
  data_loader.py         Reads + validates the uploaded workbook
  reference.py             Builds the per-version answer keys + A↔B question map
  grading.py                 Scores students, computes Total + correctness mask
  item_analysis.py            Per-question difficulty, combined across A & B
  descriptive_stats.py         Mean / median / mode / min / max / range / std dev
  charts.py                     Histogram, boxplot, difficulty bar chart
  exam_document.py               Fills the Answer Distributions markdown template
templates/
  answer_distributions.md  Markdown template for the exam-style Answer Distributions tab
tests/
  test_grading.py          Unit tests for the grading + mapping logic
  test_app.py                End-to-end tests that drive the real app headlessly
docs/
  DATA_FORMAT.md          Exact workbook structure your file needs to follow
  USER_GUIDE.md             Walkthrough of the app's three tabs
```

## 📚 More docs

- 📐 [Data format spec](docs/DATA_FORMAT.md) — what your workbook needs to look like
- 🧭 [User guide](docs/USER_GUIDE.md) — how to use the app once it's running

## ✅ Running the tests

```bash
pytest tests/
```
