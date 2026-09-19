# 🧭 User Guide

## 1. 🚀 Launch the app

```bash
pip install -r requirements.txt
streamlit run ExamGrader.py
```

## 2. 📤 Upload your workbook

Drag in your `.xlsx` file. It needs the `Exam {n} Grading` /
`Exam {n} Reference` sheet pair for whichever exam number you're about to
select — see [DATA_FORMAT.md](DATA_FORMAT.md) if you're not sure your file is
shaped correctly.

## 3. 🔢 Pick an exam number

Choose 1, 2, 3, or 4. The app loads that exam's sheets and grades every student
in the `Grading` sheet immediately — 2 points per correct answer, both exam
versions handled automatically.

If the sheets for that exam number aren't in your workbook, or a required column
is missing, you'll get a clear error message instead of a crash — just fix the
workbook and re-upload.

## 4. 📈 Tab: Class Statistics *(masked)*

This tab is safe to project on a screen in front of students — **no name ever
appears here.**

- **KPI cards:** Mean, Median, Mode, Min, Max, Range, Std Dev of the class's total
  scores, shown as large cards for easy reading from across a room.
- **Histogram:** distribution of total scores across the class, x-axis fixed to
  0–100. Hover a bar to see `Grade: X` / `Occurrences: X`.
- **Boxplot:** spread and outliers in total scores, y-axis fixed to 0–100.
- **Question Difficulty:** a bar chart of % correct per question, ordered left to
  right by Exam A's question number, combining both A and B versions of that
  question into one bar. Hover a bar to see that question's number and correct
  answer on **both** versions, plus percent correct.
- **Answer Choice Breakdown:** a stacked bar chart of which answer option
  students picked, one bar per question (same left-to-right ordering),
  combining both A and B versions into one bar per underlying option via the
  Reference sheet's option mapping. The correct option's segment carries a
  checkmark. Hover a segment to see each version's own native letter and
  question number.

## 5. 🧑‍🎓 Tab: Student Detail *(unmasked)*

This tab is for your own records only — it shows real student names alongside
their computed total, which exam version they took, and every raw answer
(1–50), with each answer cell colored green (correct) or red (incorrect). Don't
share this tab's view the way you would the Class Statistics tab.

- **`Student` column is hidden by default.** Hover the table and use the column
  visibility icon in its toolbar to unhide it if you need it on screen.
- **Filter by Student:** a multiselect above the table, with **Select All** /
  **Clear All** buttons next to it for quickly resetting the list.
- **Filter by Exam Version:** a dropdown (`All` / `A` / `B`) to narrow the table
  to one exam version.
- The table is sized to show every filtered row at once — no internal scrolling.

## 6. 📝 Tab: Answer Distributions *(masked)*

The exam laid out like the paper copy: one block per question, ordered by Exam A's
question number, headed `Question N (Exam B: Question M)` so you can see where the
question landed on both versions. Under each question is a table of its answer
options (Exam A lettering) with the option's text, the **% of students** and the
**number of students** who chose it, combining both exam versions. The correct
answer(s) are **bold with a ✓**. A `No Answer` row (blanks) is added only for
questions that at least one student left blank. No student names appear here.

Use **Download as Markdown** to save the same content as a `.md` file. The layout
comes from `templates/answer_distributions.md`, so you can change the wording or
structure by editing that file. This tab needs the `Question Text` and
`Answer Text` columns on the Reference sheet; without them it shows a notice and
the other tabs keep working.

## 7. ✅ Sanity-checking a new workbook

Before trusting the numbers on a new exam file:

- Spot-check one student's `Total` against the KPI/detail table by hand.
- Confirm the `Question Difficulty` chart has exactly 50 bars.
- Confirm the Student Detail tab's `Total` column matches what you'd expect for
  a student you graded manually.
