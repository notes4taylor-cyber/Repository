"""
02_clean_data.py — Phase 4 (part 1): cleaning, validation, deflation.

Reads data/raw/*.csv, validates and de-duplicates, builds the fiscal-year GDP
deflator (constant FY2024 dollars), standardizes agency names, and writes tidy
panels to data/interim/. Every step logs row counts so unit-of-analysis and
join integrity are auditable (see quality_control.md).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402

log = C.get_logger("clean")


def _read(name: str) -> pd.DataFrame:
    p = C.DATA_RAW / name
    if not p.exists():
        log.warning("missing raw file: %s (downstream features will degrade)", name)
        return pd.DataFrame()
    df = pd.read_csv(p)
    log.info("loaded %s: %d rows", name, len(df))
    return df


# --------------------------------------------------------------------------- #
# Deflator: GDP deflator (quarterly) -> fiscal-year average -> factor to base FY
# --------------------------------------------------------------------------- #
def build_deflator() -> pd.DataFrame:
    fred = _read("fred_macro.csv")
    if fred.empty:
        log.warning("no FRED data; emitting NOMINAL passthrough deflator (factor=1)")
        df = pd.DataFrame({"fiscal_year": C.FISCAL_YEARS, "deflator_factor": 1.0,
                           "real_basis": "NOMINAL (no FRED deflator available)"})
        df.to_csv(C.DATA_INTERIM / "deflator.csv", index=False)
        return df

    gdpdef = fred[fred["series_id"] == "GDPDEF"].copy()
    gdpdef["date"] = pd.to_datetime(gdpdef["date"])
    gdpdef["value"] = pd.to_numeric(gdpdef["value"], errors="coerce")
    # Federal fiscal year Y = Oct (Y-1) .. Sep (Y): shift quarters by one quarter
    gdpdef["fiscal_year"] = gdpdef["date"].dt.year + (gdpdef["date"].dt.month >= 10).astype(int)
    fy_def = gdpdef.groupby("fiscal_year")["value"].mean().reset_index(name="gdpdef")
    base = fy_def.loc[fy_def["fiscal_year"] == C.REAL_DOLLAR_BASE_FY, "gdpdef"]
    base_val = float(base.iloc[0]) if len(base) else float(fy_def["gdpdef"].iloc[-1])
    fy_def["deflator_factor"] = base_val / fy_def["gdpdef"]   # multiply nominal -> real
    fy_def["real_basis"] = f"constant FY{C.REAL_DOLLAR_BASE_FY} $ (GDPDEF)"
    out = fy_def[["fiscal_year", "deflator_factor", "real_basis"]]
    out = out[out["fiscal_year"].isin(C.FISCAL_YEARS)]
    out.to_csv(C.DATA_INTERIM / "deflator.csv", index=False)
    log.info("deflator built (base FY%d)", C.REAL_DOLLAR_BASE_FY)
    return out


# --------------------------------------------------------------------------- #
# Panel cleaners
# --------------------------------------------------------------------------- #
def clean_obligations_over_time() -> pd.DataFrame:
    df = _read("usa_obligations_over_time.csv")
    if df.empty:
        return df
    df = df.drop_duplicates(["fiscal_year", "series"])
    df = df[df["fiscal_year"].isin(C.FISCAL_YEARS)]
    wide = df.pivot(index="fiscal_year", columns="series", values="obligations").reset_index()
    wide.to_csv(C.DATA_INTERIM / "obligations_over_time.csv", index=False)
    return wide


def _std_agency_name(name: str) -> str:
    if not isinstance(name, str):
        return name
    s = name.strip()
    # Normalize common variants so agency names join consistently across years
    repl = {
        "Dept Of": "Department of", "Dept. of": "Department of",
        "U.S.": "United States", "US ": "United States ",
    }
    for a, b in repl.items():
        s = s.replace(a, b)
    return " ".join(s.split())


def clean_category_panel(raw_name: str, out_name: str, key: str) -> pd.DataFrame:
    df = _read(raw_name)
    if df.empty:
        return df
    before = len(df)
    df = df.dropna(subset=["fiscal_year"])
    df["fiscal_year"] = df["fiscal_year"].astype(int)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    if "name" in df.columns and key == "agency":
        df["name"] = df["name"].map(_std_agency_name)
    # de-dup on (year, code)
    df = df.sort_values("amount", ascending=False).drop_duplicates(["fiscal_year", "code"])
    log.info("%s: %d -> %d rows after clean/dedup", raw_name, before, len(df))
    df.to_csv(C.DATA_INTERIM / out_name, index=False)
    return df


def clean_award_counts() -> pd.DataFrame:
    df = _read("usa_award_counts.csv")
    if df.empty:
        return df
    df = df.drop_duplicates(["fiscal_year", "group"])
    wide = df.pivot(index="fiscal_year", columns="group",
                    values="award_count").reset_index()
    wide.to_csv(C.DATA_INTERIM / "award_counts.csv", index=False)
    return wide


def clean_google_trends() -> pd.DataFrame:
    df = _read("google_trends.csv")
    if df.empty:
        return df
    date_col = df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])
    df["fiscal_year"] = df[date_col].dt.year + (df[date_col].dt.month >= 10).astype(int)
    term_cols = [c for c in df.columns if c not in (date_col, "fiscal_year")]
    for c in term_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    fy = df.groupby("fiscal_year")[term_cols].mean().reset_index()
    fy = fy[fy["fiscal_year"].isin(C.FISCAL_YEARS)]
    fy.to_csv(C.DATA_INTERIM / "google_trends_fy.csv", index=False)
    return fy


def main() -> None:
    log.info("=== Phase 4a: cleaning & deflation ===")
    build_deflator()
    clean_obligations_over_time()
    clean_category_panel("usa_by_agency_year.csv", "agency_year.csv", "agency")
    clean_category_panel("usa_by_naics_year.csv", "naics_year.csv", "naics")
    clean_category_panel("usa_by_psc_year.csv", "psc_year.csv", "psc")
    clean_category_panel("usa_recipients_top_year.csv", "recipients_year.csv", "recipient")
    clean_category_panel("usa_tech_recipients_top_year.csv", "tech_recipients_year.csv", "recipient")
    clean_award_counts()
    clean_google_trends()
    log.info("=== cleaning complete -> data/interim/ ===")


if __name__ == "__main__":
    main()
