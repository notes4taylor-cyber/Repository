# Research Plan — Is the Market for Outsourced GovCon Business Development Growing?

**Prepared for:** ACE Business Development
**Analyst role:** Senior Python econometrics research assistant / GovCon market intelligence
**Status:** Phase 1 deliverable (written *before* any data download, per project protocol)
**Last updated:** 2026-06-19

---

## 0. The core measurement problem (read this first)

There is **no public dataset that directly measures "spending on outsourced GovCon business development (BD)."** Firms that buy capture, proposal, and federal market-entry help pay for it out of overhead/B&P budgets; it is not a reported line item in any federal or commercial dataset.

Therefore this project **cannot directly measure the dependent variable.** Everything that follows is an exercise in building **defensible, transparent proxies** for *demand* for these services and triangulating across several independent proxies. The single most important discipline in this project is to never let a proxy quietly become "the truth." Every proxy is named, justified, and its weaknesses documented.

This is a **descriptive + forecasting** study with **limited causal content**. We can credibly answer "has the *environment that creates demand* for outsourced BD grown?" We cannot credibly answer "did outsourced BD spending grow by X%?" because that number is not observable.

---

## 1. Refined research questions

| # | Original question | Refined, answerable version | Type |
|---|---|---|---|
| RQ1 | Has outsourced GovCon BD grown over 10 years? | Have the **observable market conditions that drive demand** for outsourced BD (contractor entry, procurement complexity, tech-spend growth, search/labor interest) grown over FY2015–FY2024? | Descriptive |
| RQ2 | What explains the growth? | Which observable factors **co-move with** our BD-demand proxies, and which have the largest standardized association in a regression? (association, not proof of cause) | Descriptive / associational |
| RQ3 | Which contractor segments are most likely to buy? | Which **definable contractor segments** score highest on a transparent, theory-driven propensity framework (ACE Prospect Fit Score)? | Descriptive / decision-support |
| RQ4 | Will demand keep growing through 2030? | Under stated assumptions, what do trend / ARIMA / ML models project for our proxies through 2030, and how wide is the uncertainty? | Forecast (conditional) |

---

## 2. Hypotheses

Stated as falsifiable directional hypotheses about the **proxies**, not about unobservable BD spend.

- **H1 (entry).** The number of new/active federal contractors and SAM-style entry has risen over the past decade. *More entrants → more buyers who lack internal BD infrastructure.*
- **H2 (complexity).** Procurement has become more complex (rising share of obligations through IDIQ/GWAC/BPA/task-order vehicles; more vehicles; more task orders). *Complexity raises the skill premium for capture/proposal expertise that small firms outsource.*
- **H3 (technology).** Federal IT/cyber/cloud/AI obligations have grown faster than total contract obligations. *Tech firms entering federal markets are a classic outsourced-BD buyer.*
- **H4 (attention).** Search interest and job-posting interest for GovCon BD / capture / proposal / fractional-BD roles have risen. *A direct, if noisy, signal of demand for the service category.*
- **H5 (composite).** A composite BD-Demand Index combining the above shows a statistically significant positive time trend over FY2015–FY2024.
- **H6 (forecast).** Central-case forecasts of the composite index continue rising through 2030, though with widening confidence intervals.
- **H7 (segmentation).** Demand propensity is concentrated in small/mid, recently-entered, single-agency-concentrated, tech-sector firms — i.e., the ACE Prospect Fit Score is not uniform across segments.

Each hypothesis can be **rejected** by the data (e.g., flat or declining trend, insignificant time coefficient, negative association). We will report rejections honestly.

---

## 3. Proposed data sources (detail in `data_sources.md`)

| Source | Role | Key? | Used for |
|---|---|---|---|
| **USAspending.gov API** | Primary | No key | Obligations, awards, contractor counts, NAICS/PSC, vehicle indicators, agency panels |
| **FRED (St. Louis Fed)** | Macro control | Free key | GDP, federal outlays deflator, IT-related price indices for real-dollar adjustment |
| **Census Business Dynamics Statistics (BDS)** | Context | Keyless OK | Firm entry/exit base rates (economy-wide context for entrant trends) |
| **BLS** | Labor context | Keyless OK | Management-consulting (NAICS 5416) employment/wages as a sector backdrop |
| **Google Trends (pytrends)** | Attention proxy | No key | Search-interest index for BD/capture/proposal/"fractional BD" terms |
| **Job postings** | Labor-demand proxy | — | Only if a compliant, accessible source exists; otherwise documented as a gap |
| **Industry reports (GSA, GAO, CRS, SIA, Bloomberg Gov secondary)** | Secondary context | — | Calibration & sanity checks, **never** the primary quantitative series unless downloadable + citable |

**Inflation:** all dollar series will be reported in both **nominal** and **real (constant FY2024 $)** using a FRED deflator. Headline conclusions use real dollars.

---

## 4. Proxy variables for outsourced GovCon BD demand

We construct **four independent demand proxies**, then a **composite**. Independence matters: if four methodologically unrelated proxies all rise, the conclusion is far more robust than any one.

| Proxy | Construction | Direction of inference | Primary weakness |
|---|---|---|---|
| **P1 — New-entrant index** | Count of contractors receiving their first federal prime award in year *t* (or first appearance in USAspending recipient universe). | New entrants disproportionately lack internal BD → outsource. | First-award ≠ first-attempt; recipient dedup is imperfect; doesn't see firms that *tried and failed* to win (the purest BD buyers). |
| **P2 — Procurement-complexity index** | Composite of: share of obligations via IDIQ/GWAC/BPA/task-order; # active vehicles; # task orders; vendors-per-NAICS dispersion. | More complexity → higher capture/proposal skill premium → outsource. | Complexity rising doesn't *prove* outsourcing rises; vehicle coding in FPDS/USAspending is noisy. |
| **P3 — Search-interest index** | Google Trends composite for "GovCon consultant", "capture consultant", "proposal consultant", "government contracting consultant", "federal business development consultant", "fractional BD". | Direct attention signal for the service category. | Google Trends is *relative* (0–100), reweighted/normalized, sample-based; low-volume terms are noisy; not a spend measure. |
| **P4 — Tech-entry index** | Growth in IT/cyber/cloud/AI obligations × growth in *number of distinct vendors* in those PSC/NAICS codes. | Tech firms entering federal markets are prototypical outsourced-BD buyers. | PSC/NAICS tech taxonomy is fuzzy; spend growth ≠ new buyers without the vendor-count term. |
| **Composite — BD Demand Index** | z-score normalize each of P1–P4 to a common base year, then weight (default: equal; sensitivity to PCA-derived weights). | Triangulated demand signal. | A composite can mask divergence; we always show components alongside it. |

**Explanatory (RHS) variables** (for RQ2 regressions): total real obligations, real IT obligations, # unique contractors, # new contractors, # awards, avg award size, # agencies buying in a category, vehicle-share, contractor concentration (HHI) / fragmentation, vendors-per-NAICS, tech-category dummies, Google Trends index, macro controls (GDP, federal outlays).

---

## 5. Unit of analysis

We deliberately build **multiple panels** because each RQ wants a different grain:

| Unit | Source feasibility | Used for |
|---|---|---|
| **Year (national)** | High | RQ1 trends, RQ4 forecasts, composite index time series |
| **Agency-year** | High (USAspending toptier agency) | RQ2 panel FE regressions (agency + year FE) |
| **NAICS-year** | High | RQ2 robustness; competition/fragmentation by market |
| **PSC-year** | High | Tech-category analysis (P4), service vs product |
| **Segment-year** | Derived | RQ3 segmentation, scenario forecasts |
| **Contractor-year** | Medium (volume/dedup cost) | RQ3 individual scoring *if* extraction is tractable; otherwise segment-level |

**Primary panels:** national-year (trends/forecast) + agency-year and NAICS-year (econometrics). Contractor-level scoring is a stretch goal gated on data volume.

---

## 6. Empirical strategy

### 6.1 Trend analysis (Phase 5)
- Levels and YoY growth for every series, nominal vs real.
- Log-linear trend regressions: `log(y_t) = α + β·t + ε` → β ≈ average annual growth rate, with HAC (Newey–West) SEs for serial correlation.
- CAGR tables FY2015→FY2024.

### 6.2 Cross-sectional / pooled OLS (Phase 6)
- `BD_proxy = β0 + β1·real_obligations + β2·new_contractors + β3·complexity + β4·tech_share + β5·competition + controls + ε`
- Report standardized (beta) coefficients so magnitudes are comparable; robust (HC3) SEs.

### 6.3 Panel fixed effects (the workhorse for RQ2)
- `y_{it} = α_i + γ_t + β·X_{it} + ε_{it}` on agency-year and NAICS-year panels.
- **Entity FE** absorb time-invariant agency/market differences; **year FE** absorb common shocks (budget cycles, CRs, shutdowns, COVID).
- **Clustered SEs** at the agency / NAICS level (`linearmodels.PanelOLS`, cluster_entity=True).
- This identifies *within-agency over-time* associations, which is much stronger than raw cross-section — but still **associational**, not causal (no exogenous shock / instrument).

### 6.4 What we explicitly will NOT claim
- No claim that any X **causes** outsourced BD spending. We have no randomization, no natural experiment, no instrument that plausibly satisfies exclusion. Panel FE reduces confounding; it does not eliminate it.
- The dependent variable is a **proxy**, so even a clean coefficient is "effect on the proxy," not "effect on true BD spend."

---

## 7. Forecasting strategy (Phase 8)

- **Targets:** composite BD Demand Index; real IT/cyber/cloud/AI obligations; new-entrant index.
- **Models (compared, not cherry-picked):**
  1. Log-linear trend (interpretable baseline).
  2. ARIMA/SARIMAX (or `auto_arima`) for time-series structure.
  3. ML (RandomForest / GradientBoosting) on engineered features — used cautiously; with ~10 annual points these are **illustrative**, validated only via rolling/expanding-window backtests, and never presented as precise.
- **Validation:** expanding-window backtest, hold out last 2–3 years, report MAE/MAPE. With ~10 annual observations we will be explicit that statistical power is low and intervals are wide.
- **Scenarios (Phase 8):** Conservative / Baseline / High-growth, each driven by *stated* assumptions about budget growth, tech-spend share, and entrant rates — not just mechanical extrapolation. Scenario assumptions are tabulated so a reader can disagree with the inputs.
- **Horizon honesty:** 2030 is ~6 years out from a ~10-point annual series. We present **fan charts** with widening bands and refuse point-precision.

---

## 8. Contractor segmentation & ACE Prospect Fit Score (Phase 7)

Theory-driven, transparent, additive score (documented formula in `src/07_segmentation.py` and the report). Components (each normalized 0–1, weighted, weights stated and sensitivity-tested):
market growth · contractor size (inverted — smaller scores higher) · new-entrant status · agency-concentration (need to diversify) · tech-category growth · vehicle complexity exposure · competitive intensity · likelihood of lacking a mature internal BD team.
The score **ranks segments** (and individual contractors if contractor-level data is tractable). It is a **prioritization heuristic, not a validated predictive model** — there is no ground-truth "bought outsourced BD" label to train/test against. This limitation is stated wherever the score appears.

---

## 9. Risks & limitations (the honest list)

1. **No direct DV.** The thing we care about is unobservable; all conclusions are about proxies. *This is the dominant limitation.*
2. **Proxy validity.** Each proxy can move for reasons unrelated to outsourced-BD demand (e.g., search interest rises because of news, not buying intent).
3. **Google Trends** is relative, sampled, and unstable for low-volume queries; treat as directional only.
4. **Small N for time series.** ~10 annual points → low power, wide forecast intervals, ML overfitting risk.
5. **Obligations ≠ outlays ≠ outsourced-BD revenue.** We use obligations for activity; we will never call them spending received or conflate with outlays.
6. **Fiscal vs calendar year.** Federal data is fiscal year (Oct–Sep); Google Trends/BLS are calendar. We align to fiscal year and flag every join.
7. **Recipient deduplication.** UEI/DUNS transitions, name variants, and parent/child rollups make "number of contractors" and "new entrants" approximate.
8. **Vehicle/PSC/NAICS coding noise** in source data affects complexity and tech proxies.
9. **Survivorship / selection.** The purest BD buyers (firms that *tried and failed* to win) are largely invisible in award data.
10. **Causality.** Associational only; no identification strategy supports causal claims.
11. **Segmentation has no ground truth**, so the Prospect Fit Score is judgment-encoded, not empirically validated.

---

## 10. Causal vs descriptive — what each deliverable can support

| Claim type | Supported? | By what |
|---|---|---|
| "Conditions driving outsourced-BD demand grew FY15–FY24" | ✅ Descriptive | Multi-proxy trends + trend regressions |
| "Proxy X is statistically associated with proxy Y, within agency over time" | ✅ Associational | Panel FE with clustered SEs |
| "Factor X **caused** more outsourced BD spending" | ❌ Not supported | No identification strategy |
| "Outsourced BD spending grew by N%" | ❌ Not supported | DV unobservable |
| "Demand is *likely* to keep growing to 2030 under stated assumptions" | ⚠️ Conditional | Scenario forecasts w/ wide intervals |
| "Segment A is a higher-priority ACE target than Segment B" | ✅ Decision-support | Transparent scoring heuristic (not validated prediction) |

---

## 11. What we must not overclaim (pinned reminders)

- Don't convert a rising proxy into a dollar market size.
- Don't read a panel coefficient as a causal effect.
- Don't present a 2030 point forecast without its interval and assumptions.
- Don't let the composite index hide divergence among its components.
- Don't treat the Prospect Fit Score as a trained/validated model.
- Cite every external number; mark every proxy; document every join and every data failure (in `quality_control.md`).

---

## 12. Execution order (gates)

1. ✅ **Phase 1 — this plan** (no data).
2. **Phase 2 — `data_sources.md`** (no data download; documentation only).
3. **Phase 3 — acquisition** (`src/01_download_data.py`) — *gated on network egress to the APIs.*
4. Phases 4–10 as scripted in `src/02`–`src/08`, then `quality_control.md` and the final report.

> **Protocol honored:** no data download occurs until this plan and `data_sources.md` are written and the data APIs are reachable.
