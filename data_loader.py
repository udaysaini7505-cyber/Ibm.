"""
data_loader.py
--------------
Handles loading, cleaning, and enriching the online food delivery dataset.
"""

import pandas as pd
import numpy as np
import os

# ── Income ordering for categorical sorting ──────────────────────────────────
INCOME_ORDER = [
    "No Income",
    "Below Rs.10000",
    "10001 to 25000",
    "25001 to 50000",
    "More than 50000",
]

EDU_ORDER = [
    "Uneducated",
    "School",
    "Graduate",
    "Post Graduate",
    "Ph.D",
]


def load_data(filepath: str) -> pd.DataFrame:
    """Load the CSV and return a cleaned, enriched DataFrame."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at: {filepath}")

    df = pd.read_csv(filepath)

    # ── 1. Drop fully empty / unnamed columns (trailing comma artefact) ───
    df = df.dropna(axis=1, how="all")
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

    # ── 2. Standardise column names ───────────────────────────────────────
    df.columns = df.columns.str.strip()

    # ── 3. Strip whitespace from string columns ────────────────────────────
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].str.strip()

    # ── 4. Drop exact duplicate rows ──────────────────────────────────────
    n_before = len(df)
    df = df.drop_duplicates()
    n_after = len(df)

    # ── 5. Fix known data-entry issues ────────────────────────────────────
    # Standardise "Negative " → "Negative"
    if "Feedback" in df.columns:
        df["Feedback"] = df["Feedback"].str.strip()

    # Standardise "Self Employeed" typo → "Self Employed"
    if "Occupation" in df.columns:
        df["Occupation"] = df["Occupation"].replace("Self Employeed", "Self Employed")

    # ── 6. Handle missing values ──────────────────────────────────────────
    df = df.dropna(subset=["Age", "Gender", "Output", "Feedback"])

    # Fill rare NaN in non-critical cols with "Unknown"
    for col in ["Marital Status", "Occupation", "Monthly Income",
                "Educational Qualifications", "Customer Type"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    # ── 7. Enforce correct dtypes ─────────────────────────────────────────
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
    df["Family size"] = pd.to_numeric(df["Family size"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["Pin code"] = df["Pin code"].astype(str).str.strip()

    # ── 8. Ordered categoricals for proper chart sorting ──────────────────
    df["Monthly Income"] = pd.Categorical(
        df["Monthly Income"], categories=INCOME_ORDER, ordered=True
    )
    df["Educational Qualifications"] = pd.Categorical(
        df["Educational Qualifications"], categories=EDU_ORDER, ordered=True
    )

    # ── 9. Derived / enriched columns ────────────────────────────────────
    df["Age Group"] = pd.cut(
        df["Age"],
        bins=[0, 20, 25, 30, 40, 100],
        labels=["≤20", "21–25", "26–30", "31–40", "40+"],
        right=True,
    )

    df["Orders Online"] = df["Output"].map({"Yes": 1, "No": 0})
    df["Positive Feedback"] = df["Feedback"].map({"Positive": 1, "Negative": 0})

    # Metadata about cleaning stored as attrs (survives copy)
    df.attrs["duplicates_removed"] = n_before - n_after
    df.attrs["total_rows"] = len(df)

    return df


# ── Summarisation helpers ─────────────────────────────────────────────────────

def pct_series(series: pd.Series) -> pd.DataFrame:
    """Count + percentage for a value_counts series."""
    counts = series.value_counts()
    pct = (counts / counts.sum() * 100).round(1)
    return pd.DataFrame({"Count": counts, "Percentage (%)": pct}).reset_index().rename(
        columns={"index": series.name}
    )


def crosstab_pct(df: pd.DataFrame, row: str, col: str) -> pd.DataFrame:
    """Cross-tabulation with row-wise percentage."""
    ct = pd.crosstab(df[row], df[col])
    ct_pct = ct.div(ct.sum(axis=1), axis=0).mul(100).round(1)
    return ct, ct_pct


def summary_stats(df: pd.DataFrame) -> dict:
    """High-level KPI summary dict."""
    total = len(df)
    orders_yes = (df["Output"] == "Yes").sum()
    positive_fb = (df["Feedback"] == "Positive").sum()
    return {
        "total_customers": total,
        "order_online_count": int(orders_yes),
        "order_online_pct": round(orders_yes / total * 100, 1),
        "positive_feedback_count": int(positive_fb),
        "positive_feedback_pct": round(positive_fb / total * 100, 1),
        "avg_age": round(df["Age"].mean(), 1),
        "avg_family_size": round(df["Family size"].mean(skipna=True), 1),
        "duplicates_removed": df.attrs.get("duplicates_removed", 0),
    }
