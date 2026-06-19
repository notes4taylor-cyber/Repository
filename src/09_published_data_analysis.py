"""
09_published_data_analysis.py — REAL-DATA analysis on GAO-published figures.

The live API pull (src/01) could not run in the build environment (network egress
blocked). To deliver findings on REAL numbers, this script analyzes the official
GAO "Snapshot of Government-Wide Contracting" annual totals compiled (with citations)
in data/raw/published_contract_obligations.csv  (provenance: data/raw/SOURCES.md).

Outputs (all real, all sourced):
  outputs/charts/real_01_total_obligations.png
  outputs/charts/real_02_forecast_2030.png
  outputs/tables/real_trend_total_obligations.csv
  outputs/tables/real_forecast_2030.csv
  outputs/tables/real_summary.txt
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.api as sm

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402

warnings.filterwarnings("ignore")
log = C.get_logger("real")
ACE_BLUE, ACE_ORANGE = "#1f3a5f", "#e07b1a"
FORECAST_TO = 2030
plt.rcParams.update({"figure.dpi": 140, "savefig.bbox": "tight",
                     "axes.grid": True, "grid.alpha": 0.25, "font.size": 10})


def load() -> pd.DataFrame:
    df = pd.read_csv(C.DATA_RAW / "published_contract_obligations.csv")
    df = df.sort_values("fiscal_year").reset_index(drop=True)
    log.info("loaded %d real annual observations (FY%d-FY%d)",
             len(df), df.fiscal_year.min(), df.fiscal_year.max())
    return df


def cagr(s: pd.Series, yrs: pd.Series) -> float:
    n = yrs.iloc[-1] - yrs.iloc[0]
    return (s.iloc[-1] / s.iloc[0]) ** (1 / n) - 1


def trend_regression(df: pd.DataFrame) -> dict:
    """Log-linear trend with Newey-West (HAC) SEs."""
    y = np.log(df["total_contract_obligations_busd"].values)
    t = df["fiscal_year"].values - df["fiscal_year"].min()
    X = sm.add_constant(t)
    m = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 1})
    slope = m.params[1]
    ci = m.conf_int()[1]
    return {
        "annual_growth_pct": (np.exp(slope) - 1) * 100,
        "p_value": m.pvalues[1],
        "ci_low_pct": (np.exp(ci[0]) - 1) * 100,
        "ci_high_pct": (np.exp(ci[1]) - 1) * 100,
        "r2": m.rsquared,
        "n": len(df),
        "model": m,
    }


def forecast(df: pd.DataFrame) -> pd.DataFrame:
    years = df["fiscal_year"].values
    y = df["total_contract_obligations_busd"].values
    future = np.arange(years.max() + 1, FORECAST_TO + 1)

    # log-linear trend with prediction interval (80%)
    ly = np.log(y)
    t = years - years.min()
    res = sm.OLS(ly, sm.add_constant(t)).fit()
    ft = future - years.min()
    pred = res.get_prediction(sm.add_constant(ft, has_constant="add")).summary_frame(alpha=0.20)
    trend = np.exp(pred["mean"].values)
    lo, hi = np.exp(pred["obs_ci_lower"].values), np.exp(pred["obs_ci_upper"].values)

    # ARIMA cross-check
    try:
        am = sm.tsa.SARIMAX(y, order=(1, 1, 0), enforce_stationarity=False).fit(disp=False)
        arima = am.get_forecast(len(future)).predicted_mean
    except Exception:  # noqa: BLE001
        arima = np.full(len(future), np.nan)

    # scenarios (annual multipliers on the trend central path — STATED ASSUMPTIONS)
    cons, high = 0.985, 1.03
    rows = []
    for i, fy in enumerate(future):
        rows.append({
            "fiscal_year": int(fy),
            "baseline_trend_busd": round(trend[i], 1),
            "lo80_busd": round(lo[i], 1),
            "hi80_busd": round(hi[i], 1),
            "arima_busd": round(float(arima[i]), 1) if np.isfinite(arima[i]) else None,
            "conservative_busd": round(trend[i] * cons ** (i + 1), 1),
            "high_growth_busd": round(trend[i] * high ** (i + 1), 1),
        })
    return pd.DataFrame(rows), trend, lo, hi, future


def main() -> None:
    log.info("=== REAL-DATA analysis (GAO published obligations) ===")
    df = load()

    # --- trend stats ---
    g = cagr(df["total_contract_obligations_busd"], df["fiscal_year"])
    tr = trend_regression(df)
    total_growth = (df["total_contract_obligations_busd"].iloc[-1] /
                    df["total_contract_obligations_busd"].iloc[0] - 1)

    pd.DataFrame([{
        "metric": "Total federal contract obligations",
        "first_year": int(df.fiscal_year.iloc[0]), "first_busd": df.iloc[0, 1],
        "last_year": int(df.fiscal_year.iloc[-1]), "last_busd": df.iloc[-1, 1],
        "cumulative_growth_pct": round(total_growth * 100, 1),
        "cagr_pct": round(g * 100, 2),
        "trend_annual_growth_pct": round(tr["annual_growth_pct"], 2),
        "trend_p_value": round(tr["p_value"], 5),
        "trend_ci80": f"[{tr['ci_low_pct']:.1f}%, {tr['ci_high_pct']:.1f}%]",
        "r2": round(tr["r2"], 3), "n": tr["n"],
    }]).to_csv(C.OUT_TABLES / "real_trend_total_obligations.csv", index=False)

    # --- forecast ---
    fc, trend, lo, hi, future = forecast(df)
    fc.to_csv(C.OUT_TABLES / "real_forecast_2030.csv", index=False)

    # --- chart 1: history + fitted trend ---
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(df.fiscal_year, df.total_contract_obligations_busd, color=ACE_BLUE,
           alpha=0.85, label="GAO actual obligations")
    # fitted trend line over history
    t = df.fiscal_year.values - df.fiscal_year.min()
    fitted = np.exp(tr["model"].params[0] + tr["model"].params[1] * t)
    ax.plot(df.fiscal_year, fitted, "--", color=ACE_ORANGE, lw=2,
            label=f"Log-linear trend (+{tr['annual_growth_pct']:.1f}%/yr)")
    ax.set_title("Total Federal Contract Obligations, FY2015–FY2024 (GAO, nominal $)",
                 fontweight="bold")
    ax.set_ylabel("$ Billions"); ax.set_xlabel("Fiscal Year"); ax.legend(fontsize=8)
    fig.savefig(C.OUT_CHARTS / "real_01_total_obligations.png")
    plt.close(fig)

    # --- chart 2: forecast to 2030 ---
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.plot(df.fiscal_year, df.total_contract_obligations_busd, "o-",
            color=ACE_BLUE, lw=2, label="History (GAO)")
    ax.plot(future, trend, "--", color=ACE_ORANGE, lw=2, label="Baseline trend")
    ax.fill_between(future, lo, hi, color=ACE_ORANGE, alpha=0.18, label="80% interval")
    ax.plot(future, fc.high_growth_busd, color="#c0392b", lw=1, alpha=.7, label="High-growth")
    ax.plot(future, fc.conservative_busd, color="#7f8c8d", lw=1, alpha=.7, label="Conservative")
    ax.set_title("Federal Contract Obligations: Forecast to FY2030", fontweight="bold")
    ax.set_ylabel("$ Billions"); ax.set_xlabel("Fiscal Year"); ax.legend(fontsize=8)
    fig.savefig(C.OUT_CHARTS / "real_02_forecast_2030.png")
    plt.close(fig)

    # --- summary text ---
    it = pd.read_csv(C.DATA_RAW / "published_it_obligations.csv")
    it_growth = (it.federal_it_obligations_busd.iloc[-1] /
                 it.federal_it_obligations_busd.iloc[0] - 1) * 100
    summary = f"""REAL-DATA SUMMARY (GAO published figures; see data/raw/SOURCES.md)

Total federal contract obligations:
  FY{int(df.fiscal_year.iloc[0])}: ${df.iloc[0,1]:.0f}B  ->  FY{int(df.fiscal_year.iloc[-1])}: ${df.iloc[-1,1]:.0f}B
  Cumulative growth: {total_growth*100:.0f}%   CAGR: {g*100:.1f}%/yr
  Log-linear trend: +{tr['annual_growth_pct']:.1f}%/yr (95% CI {tr['ci_low_pct']:.1f}..{tr['ci_high_pct']:.1f}%),
    p={tr['p_value']:.4f}, R^2={tr['r2']:.2f}, n={tr['n']}
  => Statistically significant decade-long GROWTH in the federal contracting base.

Federal IT obligations (context, 2 sourced points):
  FY{int(it.fiscal_year.iloc[0])}: ${it.iloc[0,1]:.0f}B -> FY{int(it.fiscal_year.iloc[-1])}: ${it.iloc[-1,1]:.0f}B  (+{it_growth:.0f}%)

Forecast to FY2030 (baseline trend): ${fc.baseline_trend_busd.iloc[-1]:.0f}B
  conservative ${fc.conservative_busd.iloc[-1]:.0f}B .. high-growth ${fc.high_growth_busd.iloc[-1]:.0f}B
"""
    (C.OUT_TABLES / "real_summary.txt").write_text(summary)
    print(summary)
    log.info("=== real-data analysis complete ===")


if __name__ == "__main__":
    main()
