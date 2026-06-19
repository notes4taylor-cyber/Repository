# Quality Control — Phase 10

This file records what was checked, what was found, what was fixed, and what limitations
remain. It is updated after each live data run. The QC philosophy: **fail loudly, never
fabricate.** Every script logs missing inputs and writes a status line rather than inventing
values.

> **Run status (as of 2026-06-19):** The environment building this project had its network
> egress **blocked** for `api.usaspending.gov`, FRED, Census, BLS, and Google. Therefore the
> *live data pull has not yet executed here*. Items below are split into **(a) verified now**
> (pipeline logic, code-level checks, no-fabrication guarantees, the network-independent
> segmentation deliverable) and **(b) gated on the live run** (data-integrity checks that
> require the downloaded data). Re-run `python src/01_download_data.py` once the hosts are
> allowlisted; the acquisition status is written to `data/raw/_download_status.log` and
> summarized here.

---

## A. The standard AI/code-mistake checklist

| # | Risk | How it is guarded | Status |
|---|---|---|---|
| 1 | **Broken API calls** | Real documented endpoints; retry+backoff; cached; status logged per source | ✅ code verified; ⏳ live call gated on egress |
| 2 | **Fake / hallucinated data sources** | Every source has a real endpoint + limitations in `data_sources.md`; nothing invented | ✅ verified |
| 3 | **Incorrect joins** | All merges on explicit keys (`fiscal_year`, `code`); row counts logged before/after | ✅ logic verified; ⏳ values gated |
| 4 | **Duplicate rows** | `drop_duplicates` on `(fiscal_year, series/code/group)` in `02_clean_data.py`, with before→after logging | ✅ verified |
| 5 | **Unit-of-analysis mistakes** | Panels are explicitly national-year / agency-year / NAICS-year; never mixed in a single regression | ✅ verified |
| 6 | **Obligations vs outlays** | I use **obligations** throughout and say so; never call them outlays or vendor revenue | ✅ verified |
| 7 | **Correlation ⇒ causation** | Every regression header states "ASSOCIATIONAL ONLY"; `research_plan.md` §6.4/§10 pin this | ✅ verified |
| 8 | **Overclaiming from weak proxies** | 4 independent proxies triangulated; composite always shown with components; weaknesses tabulated | ✅ verified |
| 9 | **Forecasting without validation** | Expanding-window backtest (MAE/MAPE) in `06_forecasts.py`; 3 methods compared | ✅ verified |
| 10 | **Ignoring inflation** | GDP-deflator → constant FY2024$ in `02`; real series used for headline trends | ✅ logic verified; ⏳ needs FRED key |
| 11 | **Fiscal vs calendar year** | FY = Oct(Y-1)–Sep(Y) applied to obligations, Trends, and deflator; every conversion commented | ✅ verified |
| 12 | **Inconsistent agency names** | `_std_agency_name()` normalizes variants before agency-year joins | ✅ verified |
| 13 | **Bad charts** | Consistent style, labeled axes/units, nominal-vs-real shown, fan charts show intervals | ✅ verified |
| 14 | **Unsupported business conclusions** | Report ties each ACE implication to a specific table/figure; caveats inline | ✅ verified |
| 15 | **Missing citations / source docs** | `data_sources.md` + report §4; secondary numbers quoted with source, never blended | ✅ verified |

## B. Data-integrity checks that run on the live data

These execute automatically (via logging) when `01`→`03` run with real data; review the logs:

- **Obligation sanity bounds:** total annual contract obligations should land in the
  ~$500B–$800B range (FY15–FY24). A value outside this flags an endpoint/filter bug.
- **Monotonic-ish deflator:** `deflator_factor` should be ≥1 for years before the base and
  ~1 at FY2024; printed by `02_clean_data.py`.
- **Entrant proxy NaN at FY2015:** by construction the first window year has no baseline, so
  `new_entrants_proxy` is NaN in FY2015 (expected, not a bug).
- **Composite component count:** `proxies.csv` carries `n_components`; if Google Trends was
  blocked, the composite is rebuilt from P1/P2/P4 and `n_components` drops to 3 — flagged.
- **Panel dimensions:** `05` logs entity/year counts and skips FE if a panel is too small.

## C. Issues found & fixed during build

- **Short-series log trends:** log-linear trend tests fall back to level-linear when a series
  has non-positive values, preventing `log(≤0)` crashes (`04`, `06`).
- **Forecast over-reach:** with ~10 points, ML (GBM) is included but labeled *illustrative*;
  trend model carries the analytic interval shown in fan charts; ARIMA falls back to a fixed
  SARIMAX order if `auto_arima`/`pmdarima` is unavailable.
- **Graceful degradation verified:** running `04/05/06` with no `data/processed/` present logs
  the missing inputs and exits cleanly instead of erroring — confirmed in build.
- **Report never fabricates:** `08_generate_report.py` prints `[pending data run]` for any
  missing table/figure rather than inventing numbers — confirmed in the generated scaffold.

## D. Limitations that remain (cannot be "fixed", only disclosed)

1. **No direct dependent variable.** Outsourced-BD spend is unobservable; everything is a proxy.
2. **Associational only.** No instrument/natural experiment → no causal claims.
3. **Small N.** ~10 annual observations → low power, wide forecast bands.
4. **Recipient sampling.** Concentration/entrant figures use a top-N recipient sample from the
   API, not the full population; treat as directional. A bulk-award extract would fix this.
5. **Google Trends** is relative, sampled, and rate-limited; P3 can be unstable or absent.
6. **Segmentation score is judgment-encoded**, not trained/validated against purchase outcomes.
7. **Deflator choice** (GDP vs IT-specific) affects real magnitudes; only GDPDEF is implemented.

## E. Reproducibility ledger

- All raw pulls cached under `data/raw/_cache/` (keyed by request) → deterministic reruns.
- Acquisition outcome per source → `data/raw/_download_status.log`.
- No secrets in the repo; keys load from `.env` (git-ignored).
- `requirements.txt` pins minimum versions; `make all` / `run_all.sh` reproduce end-to-end.
