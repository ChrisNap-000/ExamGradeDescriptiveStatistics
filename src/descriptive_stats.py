"""Descriptive statistics for a series of exam totals."""
from __future__ import annotations

import pandas as pd


def _format_number(value: float) -> str:
    rounded = round(value, 1)
    if rounded == int(rounded):
        return f"{int(rounded)}"
    return f"{rounded:.1f}"


def compute_kpis(totals: pd.Series) -> dict[str, str]:
    modes = totals.mode()
    mode_display = ", ".join(_format_number(m) for m in modes.tolist())

    return {
        "Mean": _format_number(totals.mean()),
        "Median": _format_number(totals.median()),
        "Mode": mode_display,
        "Min": _format_number(totals.min()),
        "Max": _format_number(totals.max()),
        "Range": _format_number(totals.max() - totals.min()),
        "Std Dev": _format_number(totals.std(ddof=1)),
    }
