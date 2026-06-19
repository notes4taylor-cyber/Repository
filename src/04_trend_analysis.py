"""
04_trend_analysis.py — Phase 5: descriptive trends, charts, CAGR & trend tests.

Produces business-readable charts in outputs/charts/ and trend tables in
outputs/tables/. Trend significance uses a log-linear OLS with Newey-West (HAC)
standard errors to account for serial correlation in short annual series.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.api as sm

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402

log = C.get_logger("trends")
plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight",
                     "axes.grid": True, "grid.alpha": 0.25, "font.size": 10})
ACE_BLUE, ACE_ORANGE = "#1f3a5f", "#e07b1a"


def _load(name: str, where: Path) -> pd.DataFrame:
    p = where / name
    if not p.exists():
        log.warning("missing %s", p)
        return pd.DataFrame()
    return pd.read_csv(p)


def cagr(series: pd.Series, years: pd.Series) -> float:
    s = series.dropna()
    if len(s) < 2:
        return np.nan
    n = years.iloc[-1] - years.iloc[0]
    if n <= 0 or s.iloc[0] <= 0 or s.iloc[-1] <= 0:
        return np.nan
    return (s.iloc[-1] / s.iloc[0]) ** (1 / n) - 1


def trend_test(df: pd.DataFrame, col: str) -> dict:
    """Log-linear trend regression with HAC SEs. Returns growth rate & p-value."""
    d = df[["fiscal_year", col]].dropna()
    if len(d) < 4 or (d[col] <= 0).any():
        # fall back to level-linear if logs are invalid
        if len(d) < 4:
            return {"variable": col, "annual_growth": np.nan, "p_value": np.nan, "n": len(d)}
        y = d[col].values
        logged = False
    else:
        y = np.log(d[col].values)
        logged = True
    t = d["fiscal_year"].values - d["fiscal_year"].min()
    X = sm.add_constant(t)
    model = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 1})
    slope = model.params[1]
    return {
        "variable": col,
        "annual_growth": (np.exp(slope) - 1) if logged else slope,
        "slope": slope,
        "p_value": model.pvalues[1],
        "r2": model.rsquared,
        "n": len(d),
        "spec": "log-linear" if logged else "level-linear",
    }


def plot_line(df, x, ys, title, ylabel, fname, pct=False):
    if df.empty or not any(c in df.columns for c in ys):
        log.warning("skip chart %s (no data)", fname)
        return
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = [ACE_BLUE, ACE_ORANGE, "#3c8d40", "#8e44ad", "#c0392b"]
    for i, c in enumerate([c for c in ys if c in df.columns]):
        ax.plot(df[x], df[c], marker="o", lw=2, color=colors[i % len(colors)], label=c)
    ax.set_title(title, fontweight="bold")
    ax.set_xlabel("Fiscal Year")
    ax.set_ylabel(ylabel)
    if pct:
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    if len([c for c in ys if c in df.columns]) > 1:
        ax.legend(fontsize=8)
    fig.savefig(C.OUT_CHARTS / fname)
    plt.close(fig)
    log.info("wrote chart %s", fname)


def main() -> None:
    log.info("=== Phase 5: trend analysis ===")
    nat = _load("national_year.csv", C.DATA_PROCESSED)
    px = _load("proxies.csv", C.DATA_PROCESSED)
    if nat.empty:
        log.error("no national_year.csv — run 01->03 first (needs network).")
        return

    # to $B for readability
    for c in ("real_total_contracts", "real_tech_naics", "total_contracts", "tech_naics"):
        if c in nat.columns:
            nat[c + "_B"] = nat[c] / 1e9

    # Charts
    plot_line(nat, "fiscal_year", ["total_contracts_B", "real_total_contracts_B"],
              "Federal Contract Obligations (nominal vs real FY24$)", "$ Billions",
              "01_federal_contracting.png")
    plot_line(nat, "fiscal_year", ["real_tech_naics_B"],
              "Federal IT/Cyber/Cloud/AI Contract Obligations (real FY24$)", "$ Billions",
              "02_tech_contracting.png")
    plot_line(nat, "fiscal_year", ["tech_share"],
              "Technology Share of Federal Contract Obligations", "Share", "03_tech_share.png", pct=True)
    plot_line(nat, "fiscal_year", ["new_entrants_proxy"],
              "New Federal Contractor Entry (proxy)", "New recipients (sample)",
              "04_new_entrants.png")
    plot_line(nat, "fiscal_year", ["idv_share", "tech_share"],
              "Procurement Complexity: IDV Obligation Share", "Share", "05_complexity.png", pct=True)
    plot_line(nat, "fiscal_year", ["trends_composite"],
              "Search Interest: GovCon BD/Capture/Proposal Consulting", "Google Trends index",
              "06_search_interest.png")
    if not px.empty:
        plot_line(px, "fiscal_year", ["P1_new_entrant", "P3_search", "P4_tech_entry"],
                  "Demand Proxies (indexed to FY%d=100)" % C.BASE_FY, "Index", "07_proxies.png")
        plot_line(px, "fiscal_year", ["BD_Demand_Index"],
                  "Composite BD Demand Index", "Index (FY%d=100)" % C.BASE_FY,
                  "08_bd_demand_index.png")

    # CAGR + trend-test tables
    trend_vars = [c for c in ["real_total_contracts", "real_tech_naics", "tech_share",
                              "idv_share", "new_entrants_proxy", "trends_composite",
                              "tech_vendor_count"] if c in nat.columns]
    cagr_rows = [{"variable": v, "CAGR_FY%d_FY%d" % (C.FY_START, C.FY_END):
                  cagr(nat[v], nat["fiscal_year"])} for v in trend_vars]
    pd.DataFrame(cagr_rows).to_csv(C.OUT_TABLES / "cagr_summary.csv", index=False)

    trend_rows = [trend_test(nat, v) for v in trend_vars]
    if not px.empty and "BD_Demand_Index" in px.columns:
        trend_rows.append(trend_test(px, "BD_Demand_Index"))
    tr = pd.DataFrame(trend_rows)
    tr.to_csv(C.OUT_TABLES / "trend_tests.csv", index=False)
    log.info("trend tables written; %d variables tested", len(tr))
    log.info("=== trend analysis complete ===")


if __name__ == "__main__":
    main()
