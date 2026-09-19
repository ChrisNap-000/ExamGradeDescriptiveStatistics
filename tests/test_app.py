"""End-to-end test of ExamGrader.py using Streamlit's headless AppTest runner.

This drives the real app script (file upload, both tabs, filters) the way a
user's browser would, without needing an actual browser.
"""
from __future__ import annotations

import io

import openpyxl
from streamlit.testing.v1 import AppTest

EXAM_NUMBER = 1


def _sample_workbook_bytes() -> bytes:
    wb = openpyxl.Workbook()
    grading_ws = wb.active
    grading_ws.title = f"Exam {EXAM_NUMBER} Grading"

    header = ["Student", "Total", "Exam A or B?"] + list(range(1, 51))
    grading_ws.append(header)

    # Alice (A): all correct. Bob (B): all correct. Carol (A): first 25 correct only.
    grading_ws.append(["Alice", 0, "A"] + ["A"] * 50)
    grading_ws.append(["Bob", 0, "B"] + ["B"] * 50)
    grading_ws.append(["Carol", 0, "A"] + ["A"] * 25 + ["X"] * 25)

    reference_ws = wb.create_sheet(f"Exam {EXAM_NUMBER} Reference")
    reference_ws.append(["A - Question", "A - Option", "B - Question", "B - Option", "Correct"])
    shift = 25
    for a_q in range(1, 51):
        b_q = ((a_q - 1 + shift) % 50) + 1
        reference_ws.append([a_q, "A", b_q, "B", 1])
        reference_ws.append([a_q, "B", b_q, "A", 0])

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _run_app_with_upload() -> AppTest:
    at = AppTest.from_file("ExamGrader.py")
    at.run()
    at.file_uploader[0].set_value(
        ("sample_workbook.xlsx", _sample_workbook_bytes(), "application/vnd.ms-excel")
    )
    at.run()
    return at


def test_app_runs_with_no_upload_yet():
    at = AppTest.from_file("ExamGrader.py")
    at.run()
    assert not at.exception


def test_app_runs_end_to_end_after_upload():
    at = _run_app_with_upload()
    assert not at.exception


def test_kpi_cards_render_expected_values():
    at = _run_app_with_upload()
    # Alice=100, Bob=100, Carol=50 -> mean 83.33, median 100
    rendered = "\n".join(m.value for m in at.markdown)
    assert "83.33" in rendered
    assert "kpi-value" in rendered


def test_student_detail_tab_has_no_names_leaking_into_stats_tab():
    at = _run_app_with_upload()
    stats_tab_markdown = "\n".join(m.value for m in at.tabs[0].markdown)
    assert "Alice" not in stats_tab_markdown
    assert "Bob" not in stats_tab_markdown
    assert "Carol" not in stats_tab_markdown


def test_student_detail_table_shows_all_students_by_default():
    at = _run_app_with_upload()
    detail_tab = at.tabs[1]
    assert len(detail_tab.dataframe) == 1
    table_df = detail_tab.dataframe[0].value
    assert set(table_df["Student"]) == {"Alice", "Bob", "Carol"}
    assert dict(zip(table_df["Student"], table_df["Total"])) == {
        "Alice": 100,
        "Bob": 100,
        "Carol": 50,
    }


def test_clear_all_students_button_empties_table():
    at = _run_app_with_upload()
    detail_tab = at.tabs[1]
    clear_button = next(b for b in detail_tab.button if b.label == "Clear All")
    clear_button.click().run()

    assert not at.exception
    table_df = at.tabs[1].dataframe[0].value
    assert len(table_df) == 0


def test_select_all_students_button_restores_full_table():
    at = _run_app_with_upload()
    detail_tab = at.tabs[1]
    next(b for b in detail_tab.button if b.label == "Clear All").click().run()
    next(b for b in at.tabs[1].button if b.label == "Select All").click().run()

    assert not at.exception
    table_df = at.tabs[1].dataframe[0].value
    assert set(table_df["Student"]) == {"Alice", "Bob", "Carol"}


def test_exam_version_dropdown_filters_table():
    at = _run_app_with_upload()
    detail_tab = at.tabs[1]
    version_dropdown = detail_tab.selectbox[0]
    assert version_dropdown.value == "All"

    version_dropdown.set_value("A").run()

    assert not at.exception
    table_df = at.tabs[1].dataframe[0].value
    assert set(table_df["Student"]) == {"Alice", "Carol"}
