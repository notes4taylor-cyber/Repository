# Is the Market for Outsourced GovCon Business Development Growing?

A reproducible, data-driven research project analyzing whether demand for **outsourced
business development, capture, proposal, and federal market-entry services** in U.S.
government contracting has grown over the last decade, what explains it, which contractor
segments are the best targets, and whether demand is likely to keep growing through 2030.

**Prepared for:** ACE Business Development.
**Honest framing:** there is no public dataset of "outsourced GovCon BD spending," so this
project builds and triangulates **four documented demand proxies**. All findings are
**descriptive / associational**, never causal, and every proxy and limitation is documented.

---

## What's in here

| Path | Contents |
|---|---|
| `research_plan.md` | **Phase 1** — research design, hypotheses, proxy logic, what can/can't be claimed |
| `data_sources.md` | **Phase 2** — every source, endpoint, variables, limitations, usage status |
| `src/01`–`08_*.py` | **Phases 3–9** — download → clean → features → trends → econometrics → forecast → segmentation → report |
| `src/config.py` | Shared paths, taxonomies, FRED series, resilient cached HTTP helper |
| `data/raw,interim,processed/` | Cached pulls → cleaned panels → analytical datasets |
| `outputs/charts,tables,report/` | Figures, regression/forecast tables, final Markdown report |
| `quality_control.md` | **Phase 10** — what was checked, found, fixed, and still limited |

## The pipeline

```
01_download_data.py    Pull USAspending / FRED / Census / BLS / Google Trends → data/raw/
02_clean_data.py       Validate, dedupe, deflate to constant FY2024$         → data/interim/
03_create_features.py  Build proxies P1–P4 + composite BD Demand Index       → data/processed/
04_trend_analysis.py   CAGR, log-linear trend tests (HAC SEs), charts        → outputs/
05_econometric_models  Pooled OLS + agency/NAICS panel fixed effects         → outputs/tables/
06_forecasts.py        Trend / ARIMA / GBM to 2030, backtest, scenarios      → outputs/
07_segmentation.py     Contractor segments + ACE Prospect Fit Score          → outputs/
08_generate_report.py  Assemble the business report                          → outputs/report/
```

Each script is rerun-safe: API responses are cached under `data/raw/_cache/`, and
data-dependent scripts **degrade gracefully** (logging what's missing) if a source is
unavailable — they never fabricate data.

---

## Prerequisites

1. **Python 3.10+** and packages: `pip install -r requirements.txt`
2. **Network egress** to the data APIs. In a sandboxed/remote environment you must allowlist:
   `api.usaspending.gov`, `api.stlouisfed.org`, `fred.stlouisfed.org`, `api.census.gov`,
   `api.bls.gov`, `trends.google.com`, `www.google.com`.
3. **API keys** in a local `.env` (git-ignored). USAspending needs **none**; others are optional:
   ```
   FRED_API_KEY=your_free_key        # https://fred.stlouisfed.org/docs/api/api_key.html
   CENSUS_API_KEY=optional
   BLS_API_KEY=optional
   ```
   Without a FRED key the pipeline runs in **nominal dollars** (flagged as a limitation).

## Run it

```bash
pip install -r requirements.txt
python src/01_download_data.py     # needs network; writes a status log
python src/02_clean_data.py
python src/03_create_features.py
python src/04_trend_analysis.py
python src/05_econometric_models.py
python src/06_forecasts.py
python src/07_segmentation.py       # runs without network (theory-driven score)
python src/08_generate_report.py
```

Or all at once:

```bash
make all          # see Makefile
# or
bash run_all.sh
```

Final report: `outputs/report/outsourced_govcon_bd_market_report.md`.

---

## Current status / reproducibility note

The analysis scripts and segmentation are complete and tested. The **live data pull
(`01_download_data.py`) requires the API hosts above to be reachable**; in the environment
where this was built, egress to those hosts was blocked, so the numeric trend/econometric/
forecast outputs regenerate as soon as the allowlist + FRED key are in place. The
segmentation deliverable (`outputs/tables/ace_prospect_fit_segments.csv`) and the report
scaffold are already generated. See `quality_control.md` for the exact run-status checklist.

## What this project does NOT claim

- No dollar figure for "outsourced BD market size" (unobservable).
- No causal effects (no identification strategy; panel FE reduces but doesn't remove confounding).
- No point-precise 2030 forecast (intervals are wide with ~10 annual points).
- The ACE Prospect Fit Score is a **transparent prioritization heuristic**, not a validated model.
