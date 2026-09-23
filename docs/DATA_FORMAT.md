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
| `Curve` | ➖ | Optional — points to add to that student's score (e.g. `2`, or `-1`). Leave it out, or leave a cell blank, to apply no curve (defaults to `0`). Added on top of the computed raw score to produce the final `Total`. |
| `Exam A or B?` | ✅ | Literally `A` or `B` — which version this student took. |
| `1` … `50` | ✅ | One column per question number, header is just the number. Holds the student's letter answer (`A`/`B`/`C`/`D`), or the literal text `NA` for a blank. |

**Example:**

| Student | Total | Curve | Exam A or B? | 1 | 2 | 3 | … | 50 |
|---|---|---|---|---|---|---|---|---|
| Jordan P. | *(ignored)* | 2 | A | B | A | NA | … | C |
| Sam R. | *(ignored)* | 0 | B | D | B | A | … | D |

> ⚠️ Blank answers must be entered as the literal text `NA`, not left as an empty
> cell. The app scores `NA` as incorrect either way, but a truly empty cell can be
> read inconsistently by different spreadsheet tools — `NA` is unambiguous.

## 🗂️ `Exam {n} Reference`

One row per **(question, answer option)** pair — up to 5 rows per question
(options A–E), not one row per question. This sheet does two jobs at once:
it's the answer key for each version, **and** it maps each Exam A
question/option to the Exam B question/option that's actually the same
underlying question and the same underlying option (both are shuffled
between versions, not just question order).

| Column | Required? | Notes |
|---|---|---|
| `A - Question` | ✅ | The question number on Exam A. |
| `A - Option` | ✅ | The option letter on Exam A for this row. |
| `B - Question` | ✅ | The Exam B question number that is the *same question* as the Exam A one on this row. |
| `B - Option` | ✅ | The Exam B option letter that is the *same underlying option* as the Exam A one on this row. |
| `Correct` | ✅ | `1` if this row's option pair is an accepted correct answer for the question, otherwise `0`. At least one `1` per question — flag more than one row `1` for a question if you're accepting multiple answers (e.g. to fix a flawed question). |
| `Question Text` | ➖ | The question's wording, repeated on each of its option rows. Optional for the charts and grading, but required for the **Answer Distributions** tab (which shows a notice if it's missing). |
| `Answer Text` | ➖ | The wording of this row's option (the answer choice itself). Optional for the charts and grading, but required for the **Answer Distributions** tab. Text such as `None` or `N/A` is kept as-is. |

**Example** (for Exam 1): the first two rows say *"Exam A Question 1's option A
is the same underlying option as Exam B Question 26's option B, and it's the
correct answer. Exam A Question 1's option B is the same underlying option as
Exam B Question 26's option A, and it's a distractor."*

| A - Question | A - Option | B - Question | B - Option | Correct |
|---|---|---|---|---|
| 1 | A | 26 | B | 1 |
| 1 | B | 26 | A | 0 |
| 2 | A | 14 | C | 0 |
| 2 | B | 14 | A | 1 |
| … | … | … | … | … |

This mapping is what lets the app's **Question Difficulty** chart combine
results from both exam versions into one number per underlying question, and
what lets the **Answer Choice Breakdown** chart combine both versions'
responses into one stacked bar per question per underlying option — instead
of treating "Question 1, Option A" on Exam A and "Question 1, Option A" on
Exam B as if they were the same choice, when the versions may have shuffled
which letter each option is labeled.

## 🙅 What happens if something's off

If a required sheet is missing, a required column is missing, the Reference
sheet doesn't cover all 50 questions, or a question has no row flagged
`Correct = 1`, the app stops and tells you exactly what's wrong instead of
guessing.
