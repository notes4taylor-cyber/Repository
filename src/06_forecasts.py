"""
06_forecasts.py — Phase 8: forecasts through 2030 with scenarios.

Forecasts the composite BD Demand Index, real technology obligations, and the
new-entrant proxy to FY2030 using THREE compared methods:
  1) Log-linear trend (interpretable baseline)
  2) SARIMAX / ARIMA (statsmodels; auto_arima if pmdarima present)
  3) ML (GradientBoosting on lag features) — illustrative only

Validation: expanding-window backtest on the last 3 fiscal years (MAE/MAPE).
Scenarios: Conservative / Baseline / High-growth, with STATED assumptions.
Honesty: with ~10 annual points, intervals are wide; fan charts show this.

Outputs: outputs/charts/fan_*.png, outputs/tables/forecast_*.csv,
         outputs/tables/forecast_backtest.csv, outputs/tables/scenarios.csv
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402

warnings.filterwarnings("ignore")
log = C.get_logger("forecast")
FORECAST_TO = 2030
ACE_BLUE, ACE_ORANGE = "#1f3a5f", "#e07b1a"


def _load(name: str, where: Path) -> pd.DataFrame:
    p = where / name
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


# --------------------------------------------------------------------------- #
# Forecast methods
# --------------------------------------------------------------------------- #
def trend_forecast(years, y, future_years):
    """Log-linear (or level) trend with analytic prediction intervals."""
    import statsmodels.api as sm
    pos = (y > 0).all()
    yy = np.log(y) if pos else y
    t = np.asarray(years) - years[0]
    X = sm.add_constant(t)
    res = sm.OLS(yy, X).fit()
    ft = np.asarray(future_years) - years[0]
    Xf = sm.add_constant(ft, has_constant="add")
    pred = res.get_prediction(Xf).summary_frame(alpha=0.20)  # 80% interval
    mean, lo, hi = pred["mean"], pred["obs_ci_lower"], pred["obs_ci_upper"]
    if pos:
        mean, lo, hi = np.exp(mean), np.exp(lo), np.exp(hi)
    return np.asarray(mean), np.asarray(lo), np.asarray(hi)


def arima_forecast(y, h):
    import statsmodels.api as sm
    try:
        import pmdarima as pm
        m = pm.auto_arima(y, seasonal=False, suppress_warnings=True,
                          error_action="ignore", max_p=2, max_q=2, max_d=1)
        fc, ci = m.predict(n_periods=h, return_conf_int=True, alpha=0.20)
        return np.asarray(fc), ci[:, 0], ci[:, 1]
    except Exception:
        try:
            model = sm.tsa.SARIMAX(y, order=(1, 1, 0),
                                   enforce_stationarity=False).fit(disp=False)
            f = model.get_forecast(h)
            ci = f.conf_int(alpha=0.20)
            return np.asarray(f.predicted_mean), ci[:, 0], ci[:, 1]
        except Exception as e:  # noqa: BLE001
            log.warning("ARIMA failed: %s", e)
            return None, None, None


def ml_forecast(years, y, h):
    """GradientBoosting on lag-1/lag-2 features, recursive. Illustrative only."""
    from sklearn.ensemble import GradientBoostingRegressor
    if len(y) < 6:
        return None
    df = pd.DataFrame({"y": y})
    df["l1"] = df["y"].shift(1)
    df["l2"] = df["y"].shift(2)
    df["t"] = np.arange(len(df))
    tr = df.dropna()
    model = GradientBoostingRegressor(n_estimators=120, max_depth=2,
                                      learning_rate=0.05, random_state=0)
    model.fit(tr[["l1", "l2", "t"]], tr["y"])
    hist = list(y)
    preds = []
    for i in range(h):
        l1, l2, t = hist[-1], hist[-2], len(hist)
        p = float(model.predict([[l1, l2, t]])[0])
        preds.append(p)
        hist.append(p)
    return np.asarray(preds)


def backtest(years, y, holdout=3) -> dict:
    """Expanding-window backtest of the trend model on the last `holdout` years."""
    if len(y) <= holdout + 3:
        return {"mae": np.nan, "mape": np.nan, "note": "series too short"}
    errs, apes = [], []
    for cut in range(len(y) - holdout, len(y)):
        m, _, _ = trend_forecast(years[:cut], y[:cut], [years[cut]])
        pred, actual = m[0], y[cut]
        errs.append(abs(pred - actual))
        if actual != 0:
            apes.append(abs(pred - actual) / abs(actual))
    return {"mae": float(np.mean(errs)),
            "mape": float(np.mean(apes)) if apes else np.nan,
            "holdout_years": holdout}


# --------------------------------------------------------------------------- #
def forecast_series(years, y, name, scenario_mult):
    future = list(range(years[-1] + 1, FORECAST_TO + 1))
    allyears = list(years) + future
    t_mean, t_lo, t_hi = trend_forecast(years, y, future)
    a_mean, a_lo, a_hi = arima_forecast(y, len(future))
    ml = ml_forecast(years, y, len(future))
    bt = backtest(list(years), list(y))

    # scenarios: scale the trend central path by cumulative scenario multipliers
    rows = []
    for i, fy in enumerate(future):
        base = t_mean[i]
        rows.append({
            "variable": name, "fiscal_year": fy,
            "trend": base, "trend_lo80": t_lo[i], "trend_hi80": t_hi[i],
            "arima": (a_mean[i] if a_mean is not None else np.nan),
            "ml_gbm": (ml[i] if ml is not None else np.nan),
            "conservative": base * scenario_mult["cons"] ** (i + 1),
            "baseline": base * scenario_mult["base"] ** (i + 1),
            "high_growth": base * scenario_mult["high"] ** (i + 1),
        })
    fc = pd.DataFrame(rows)

    # fan chart
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.plot(years, y, "o-", color=ACE_BLUE, lw=2, label="History")
    ax.plot(future, t_mean, "--", color=ACE_ORANGE, lw=2, label="Trend forecast")
    ax.fill_between(future, t_lo, t_hi, color=ACE_ORANGE, alpha=0.18, label="80% interval")
    if a_mean is not None:
        ax.plot(future, a_mean, ":", color="#3c8d40", lw=1.8, label="ARIMA")
    ax.plot(future, fc["high_growth"], color="#c0392b", lw=1, alpha=.7, label="High-growth")
    ax.plot(future, fc["conservative"], color="#7f8c8d", lw=1, alpha=.7, label="Conservative")
    ax.set_title(f"Forecast to {FORECAST_TO}: {name}", fontweight="bold")
    ax.set_xlabel("Fiscal Year"); ax.legend(fontsize=8)
    fig.savefig(C.OUT_CHARTS / f"fan_{name}.png", bbox_inches="tight")
    plt.close(fig)
    return fc, bt


def main() -> None:
    log.info("=== Phase 8: forecasts to %d ===", FORECAST_TO)
    nat = _load("national_year.csv", C.DATA_PROCESSED)
    px = _load("proxies.csv", C.DATA_PROCESSED)
    if nat.empty:
        log.error("no processed data; run 01->03 first (needs network).")
        return

    targets = []
    if not px.empty and "BD_Demand_Index" in px.columns:
        m = px[["fiscal_year", "BD_Demand_Index"]].dropna()
        targets.append(("BD_Demand_Index", m["fiscal_year"].tolist(),
                        m["BD_Demand_Index"].tolist()))
    if "real_tech_naics" in nat.columns:
        m = nat[["fiscal_year", "real_tech_naics"]].dropna()
        targets.append(("real_tech_obligations", m["fiscal_year"].tolist(),
                        (m["real_tech_naics"] / 1e9).tolist()))
    if "new_entrants_proxy" in nat.columns:
        m = nat[["fiscal_year", "new_entrants_proxy"]].dropna()
        targets.append(("new_entrants", m["fiscal_year"].tolist(),
                        m["new_entrants_proxy"].tolist()))

    # Scenario annual multipliers (STATED ASSUMPTIONS — see report):
    #   conservative = below-trend (flat budgets, slower tech), baseline = on-trend,
    #   high = above-trend (sustained tech/cyber/AI demand + entrant surge).
    scen = {"cons": 0.985, "base": 1.0, "high": 1.03}

    all_fc, bt_rows = [], []
    for name, yrs, vals in targets:
        if len(vals) < 5:
            log.warning("skip %s (too few points)", name)
            continue
        fc, bt = forecast_series(yrs, vals, name, scen)
        all_fc.append(fc)
        bt_rows.append({"variable": name, **bt})

    if all_fc:
        pd.concat(all_fc, ignore_index=True).to_csv(
            C.OUT_TABLES / "forecasts_2030.csv", index=False)
        pd.DataFrame(bt_rows).to_csv(C.OUT_TABLES / "forecast_backtest.csv", index=False)
        # scenario assumptions table
        pd.DataFrame([
            {"scenario": "Conservative", "annual_mult": scen["cons"],
             "assumptions": "Flat/declining real budgets, CR drag, slower tech adoption"},
            {"scenario": "Baseline", "annual_mult": scen["base"],
             "assumptions": "Trend continuation of FY15-24 dynamics"},
            {"scenario": "High-growth", "annual_mult": scen["high"],
             "assumptions": "Sustained cyber/AI/cloud demand + entrant surge + vehicle proliferation"},
        ]).to_csv(C.OUT_TABLES / "scenarios.csv", index=False)
        log.info("forecasts written for %d targets", len(all_fc))
    log.info("=== forecasting complete ===")


if __name__ == "__main__":
    main()
