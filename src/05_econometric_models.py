"""
05_econometric_models.py — Phase 6: regression analysis.

Estimates, in order of increasing rigor:
  (A) Pooled OLS of the BD Demand Index on national drivers (HC3 robust SEs).
  (B) Agency-year panel fixed-effects (entity + time FE) with SEs clustered by
      agency, modeling growth/complexity associations  [linearmodels.PanelOLS].
  (C) NAICS-year panel fixed-effects as a robustness check.

ALL results are ASSOCIATIONAL. The dependent variables are proxies; no causal
claim is made (see research_plan.md §6.4). Regression tables -> outputs/tables/.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402

log = C.get_logger("econ")


def _load(name: str) -> pd.DataFrame:
    p = C.DATA_PROCESSED / name
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


def _standardize(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        if c in out.columns:
            sd = out[c].std(ddof=0)
            out[c] = (out[c] - out[c].mean()) / sd if sd and sd > 0 else 0.0
    return out


# --------------------------------------------------------------------------- #
# (A) Pooled OLS — national time series
# --------------------------------------------------------------------------- #
def national_ols() -> None:
    nat = _load("national_year.csv")
    px = _load("proxies.csv")
    if nat.empty or px.empty or "BD_Demand_Index" not in px.columns:
        log.warning("national OLS skipped (missing data)")
        return
    df = nat.merge(px[["fiscal_year", "BD_Demand_Index"]], on="fiscal_year", how="inner")

    candidates = ["real_total_contracts", "real_tech_naics", "tech_share",
                  "idv_share", "new_entrants_proxy", "recipient_hhi"]
    rhs = [c for c in candidates if c in df.columns and df[c].notna().sum() >= 6]
    if not rhs:
        log.warning("no usable RHS variables for national OLS")
        return
    d = df[["BD_Demand_Index"] + rhs].dropna()
    if len(d) < len(rhs) + 2:
        # too few points for all regressors: keep the 2 strongest-variance ones
        rhs = rhs[:max(1, len(d) - 2)]
        d = df[["BD_Demand_Index"] + rhs].dropna()
    d = _standardize(d, rhs)  # standardized betas (comparable magnitudes)
    X = sm.add_constant(d[rhs])
    model = sm.OLS(d["BD_Demand_Index"], X).fit(cov_type="HC3")

    with open(C.OUT_TABLES / "ols_national.txt", "w") as f:
        f.write("Pooled OLS — DV: BD Demand Index (proxy). Standardized betas, HC3 SEs.\n")
        f.write("ASSOCIATIONAL ONLY — not causal. N=%d annual observations.\n\n" % len(d))
        f.write(str(model.summary()))
    # tidy CSV
    tidy = pd.DataFrame({"term": model.params.index, "beta": model.params.values,
                         "std_err": model.bse.values, "p_value": model.pvalues.values,
                         "ci_low": model.conf_int()[0].values,
                         "ci_high": model.conf_int()[1].values})
    tidy.to_csv(C.OUT_TABLES / "ols_national.csv", index=False)
    log.info("national OLS written (N=%d, k=%d)", len(d), len(rhs))


# --------------------------------------------------------------------------- #
# (B,C) Panel fixed effects
# --------------------------------------------------------------------------- #
def panel_fe(panel_file: str, entity: str, label: str) -> None:
    df = _load(panel_file)
    if df.empty:
        log.warning("%s FE skipped (no data)", label)
        return
    df = df.dropna(subset=["real_amount", "fiscal_year", "code"])
    df = df[np.isfinite(df.get("growth", pd.Series(dtype=float))).fillna(False) |
            df["growth"].isna()] if "growth" in df else df
    # DV: log real obligations; RHS: lagged growth + year structure via FE
    df["log_real"] = np.log(df["real_amount"].clip(lower=1))
    df = df.dropna(subset=["log_real"])
    if df["code"].nunique() < 5 or df["fiscal_year"].nunique() < 3:
        log.warning("%s FE skipped (insufficient panel dims)", label)
        return
    try:
        from linearmodels.panel import PanelOLS
        pdf = df.set_index(["code", "fiscal_year"])
        # entity + time fixed effects; cluster SEs by entity
        exog_cols = [c for c in ["real_amount_lag"] if c in df.columns]
        if not exog_cols:
            log.warning("%s FE: no exog; running pure two-way FE variance decomposition", label)
        exog = sm.add_constant(pdf[exog_cols]) if exog_cols else None
        mod = PanelOLS(pdf["log_real"], exog, entity_effects=True, time_effects=True,
                       drop_absorbed=True)
        res = mod.fit(cov_type="clustered", cluster_entity=True)
        with open(C.OUT_TABLES / f"panel_fe_{label}.txt", "w") as f:
            f.write(f"Panel FE — {label}. DV: log real obligations.\n")
            f.write("Entity + Time FE; SEs clustered by entity. ASSOCIATIONAL ONLY.\n\n")
            f.write(str(res.summary))
        log.info("%s FE written (entities=%d, years=%d)", label,
                 df["code"].nunique(), df["fiscal_year"].nunique())
    except ImportError:
        # statsmodels fallback: entity & year dummies (absorbing FE manually)
        log.warning("linearmodels missing; using statsmodels dummy FE for %s", label)
        d = pd.get_dummies(df, columns=["code", "fiscal_year"], drop_first=True)
        ycol = "log_real"
        xcols = [c for c in d.columns if c.startswith(("code_", "fiscal_year_"))
                 and c != ycol]
        if "real_amount_lag" in d:
            xcols = ["real_amount_lag"] + xcols
            d = d.dropna(subset=["real_amount_lag"])
        X = sm.add_constant(d[xcols].astype(float))
        res = sm.OLS(d[ycol], X).fit(cov_type="cluster",
                                     cov_kwds={"groups": df.loc[d.index, "code"]}
                                     if "code" in df else {})
        with open(C.OUT_TABLES / f"panel_fe_{label}.txt", "w") as f:
            f.write(f"Panel FE (dummy-variable) — {label}. DV: log real obligations.\n\n")
            f.write(str(res.summary()))
    except Exception as e:  # noqa: BLE001
        log.error("%s FE FAILED: %s", label, e)


def main() -> None:
    log.info("=== Phase 6: econometric models ===")
    national_ols()
    panel_fe("agency_year.csv", "agency", "agency")
    panel_fe("naics_year.csv", "naics", "naics")
    log.info("=== econometrics complete -> outputs/tables/ ===")


if __name__ == "__main__":
    main()
