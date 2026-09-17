"""Descriptive statistics for a series of exam totals."""
from __future__ import annotations

import pandas as pd


def compute_kpis(totals: pd.Series) -> dict[str, str]:
    modes = totals.mode()
    mode_display = ", ".join(str(m) for m in modes.tolist())

    return {
        "Mean": f"{totals.mean():.2f}",
        "Median": f"{totals.median():.2f}",
        "Mode": mode_display,
        "Min": f"{totals.min():.0f}",
        "Max": f"{totals.max():.0f}",
        "Range": f"{totals.max() - totals.min():.0f}",
        "Std Dev": f"{totals.std(ddof=1):.2f}",
    }
