# 📐 Workbook Data Format

Your uploaded file must be a single `.xlsx` workbook. For each exam number `n`
(1, 2, 3, or 4) that you want to analyze, the workbook needs **two sheets**, named
exactly:

- `Exam {n} Grading`
- `Exam {n} Reference`

You only need the sheets for the exam numbers you actually want to look at — you
don't need all four.

## 🗂️ `Exam {n} Grading`

One row per student.

| Column | Required? | Notes |
|---|---|---|
| `Student` | ✅ | Student's name. Only ever shown on the unmasked Student Detail tab. |
| `Total` | ➖ | Optional — leave it out entirely, or include it and it'll be ignored. The app always recomputes this itself. |
| `Exam A or B?` | ✅ | Literally `A` or `B` — which version this student took. |
| `1` … `50` | ✅ | One column per question number, header is just the number. Holds the student's letter answer (`A`/`B`/`C`/`D`), or the literal text `NA` for a blank. |

**Example:**

| Student | Total | Exam A or B? | 1 | 2 | 3 | … | 50 |
|---|---|---|---|---|---|---|---|
| Jordan P. | *(ignored)* | A | B | A | NA | … | C |
| Sam R. | *(ignored)* | B | D | B | A | … | D |

> ⚠️ Blank answers must be entered as the literal text `NA`, not left as an empty
> cell. The app scores `NA` as incorrect either way, but a truly empty cell can be
> read inconsistently by different spreadsheet tools — `NA` is unambiguous.

## 🗂️ `Exam {n} Reference`

Exactly 50 rows — one per question. This sheet does two jobs at once: it's the
answer key for each version, **and** it maps each Exam A question to the Exam B
question that's actually the same underlying question (just reordered).

| Column | Required? | Notes |
|---|---|---|
| `A - Questions` | ✅ | The question number on Exam A. |
| `Exam {n}A Answer` | ✅ | The correct letter for that question on Exam A. Header includes the exam number, e.g. `Exam 2A Answer` for Exam 2. |
| `B - Questions` | ✅ | The Exam B question number that is the *same question* as the Exam A one on this row. |
| `Exam {n}B Answer` | ✅ | The correct letter for that same question on Exam B. |

**Example** (for Exam 1): the first row `1, A, 26, B` means *"Exam A Question 1 is
the same question as Exam B Question 26. The correct answer is A on the Exam A
version, and B on the Exam B version."*

| A - Questions | Exam 1A Answer | B - Questions | Exam 1B Answer |
|---|---|---|---|
| 1 | A | 26 | B |
| 2 | C | 14 | A |
| … | … | … | … |

This mapping is what lets the app's **Question Difficulty** chart combine results
from both exam versions into one number per underlying question, instead of
treating "Question 1" on Exam A and "Question 1" on Exam B as if they were
different questions.

## 🙅 What happens if something's off

If a required sheet is missing, a required column is missing, or the Reference
sheet doesn't have exactly 50 rows, the app stops and tells you exactly what's
wrong instead of guessing.
