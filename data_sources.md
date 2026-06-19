# Data Sources — Outsourced GovCon BD Market Study

**Status:** Phase 2 deliverable (documentation only; no data downloaded here).
**Convention:** "Used in final project?" is set to **Pending** until the acquisition script (`src/01_download_data.py`) successfully pulls the series; it is updated to **Yes/No/Failed** after the run, with the failure reason logged in `quality_control.md`. This keeps us honest: a source is only "used" once it actually returns data.

> ⚠️ **Environment note (2026-06-19):** This sandbox's network egress is allowlisted. At plan time, `api.usaspending.gov`, FRED, and Google were **blocked**. The acquisition scripts target the real endpoints below and run unmodified once these hosts are added to the environment's egress settings. Any source that cannot be reached at run time is recorded as **Failed** with the exact error, and an alternative is documented — never silently faked.

---

## 1. USAspending.gov API  — **PRIMARY SOURCE**

- **Base URL:** `https://api.usaspending.gov/api/v2/`
- **Auth:** None (public, no API key). Rate-limited; we add backoff + caching.
- **Docs:** https://api.usaspending.gov/docs/endpoints
- **Key endpoints used:**
  | Endpoint | Method | Pulls |
  |---|---|---|
  | `/references/toptier_agencies/` | GET | Agency list (for agency-year panel) |
  | `/search/spending_over_time/` | POST | Obligations by fiscal year (national + filtered) |
  | `/search/spending_by_category/{naics,psc,recipient,awarding_agency}/` | POST | Obligations & counts by NAICS, PSC, recipient, agency |
  | `/search/spending_by_award/` | POST | Award-level rows (entrant detection, vehicle/IDV flags) |
  | `/bulk_download/awards/` | POST | Bulk year files when paging is too large |
- **Variables:** obligations, award counts, recipient (UEI/name), NAICS, PSC, awarding/funding agency, award type (A/B/C/D = contracts), IDV type (IDIQ/GWAC/BPA), parent award, action date, fiscal year, set-aside / business-size flags.
- **Years available:** FY2008→present (we use **FY2015–FY2024**, the cleaner decade).
- **Why it matters:** Authoritative, reproducible federal procurement record. Source for obligations, contractor counts, new-entrant detection, complexity (vehicle shares, task orders), tech-category spend (NAICS/PSC), competition (vendors per market, HHI). It anchors **P1, P2, P4** and almost all RHS variables.
- **Limitations:** Obligations ≠ outlays ≠ vendor revenue. Recipient dedup imperfect (UEI/DUNS transition ~2022). Vehicle/PSC coding noise. Sub-award data is separate and patchier (not used as primary).
- **Used in final project?** **Pending → (set at run time).**

## 2. FRED — St. Louis Fed  — macro controls & deflation

- **Base URL:** `https://api.stlouisfed.org/fred/series/observations`
- **Auth:** **Free API key required** (`FRED_API_KEY`, set via `.env`). Register: https://fred.stlouisfed.org/docs/api/api_key.html
- **Series used:**
  | Series ID | Meaning | Use |
  |---|---|---|
  | `GDPDEF` | GDP implicit price deflator | Convert obligations to constant FY2024 $ |
  | `FGEXPND` | Federal Government current expenditures | Macro budget control |
  | `GDP` | Nominal GDP | Scale/control |
  | `A091RC1Q027SBEA` | Federal defense consumption (optional) | Defense-budget context |
- **Years:** Multi-decade; ample coverage.
- **Why it matters:** Real-dollar adjustment is mandatory for a credible 10-year trend; macro controls reduce omitted-variable bias in regressions.
- **Limitations:** Needs a key; quarterly→fiscal-year aggregation required; deflator choice (GDP vs IT-specific) affects real series — we test sensitivity.
- **Used in final project?** **Pending.** *If key/host unavailable:* fall back to BEA published deflator table (manual, cited) or report nominal-only with a flagged limitation.

## 3. U.S. Census — Business Dynamics Statistics (BDS)

- **Base URL:** `https://api.census.gov/data/timeseries/bds`
- **Auth:** Census API key recommended (`CENSUS_API_KEY`); works keyless at low volume.
- **Variables:** establishment/firm births & deaths, job creation, by year/sector/firm-age.
- **Years:** ~1978–2022 (release-dependent).
- **Why it matters:** Economy-wide firm-entry **base rate** — context to judge whether federal-contractor entry is a GovCon-specific story or just the broader business-formation cycle.
- **Limitations:** Not federal-contractor specific; ends a couple years short of present; sector codes ≠ federal NAICS mix.
- **Used in final project?** **Pending (context, secondary).**

## 4. BLS — Bureau of Labor Statistics

- **Base URL:** `https://api.bls.gov/publicAPI/v2/timeseries/data/`
- **Auth:** Optional key (`BLS_API_KEY`) raises limits; keyless works at low volume.
- **Series of interest:** employment/wages for **NAICS 5416** (Management/Scientific/Technical Consulting) and **5611** (Office admin / incl. proposal support) via QCEW/CES.
- **Years:** Multi-decade.
- **Why it matters:** Sector backdrop for the *consulting* labor market that outsourced BD lives in; a coarse labor-demand context for P3/P4.
- **Limitations:** NAICS 5416 is far broader than GovCon BD; cannot isolate "capture/proposal consultants." Context only.
- **Used in final project?** **Pending (context, secondary).**

## 5. Google Trends (via `pytrends`)

- **Endpoint:** unofficial Google Trends (`trends.google.com`) through `pytrends`.
- **Auth:** None; **heavily rate-limited (HTTP 429)**; may need `www.google.com` for cookies.
- **Terms (P3 search-interest proxy):** "GovCon consultant", "capture consultant", "proposal consultant", "government contracting consultant", "federal business development consultant", "fractional BD", "proposal writer government", "capture manager".
- **Variables:** relative search interest index (0–100), monthly, US.
- **Years:** 2004→present (we use 2015–present, aggregated to fiscal year).
- **Why it matters:** The most *direct* available attention signal for the service category — independent of procurement data.
- **Limitations:** **Relative**, sampled, re-normalized; low-volume terms noisy/unstable; not a spend measure; ToS-sensitive (read-only research use). Directional only.
- **Used in final project?** **Pending.** *If blocked/429:* document failure; substitute term-by-term published Trends screenshots only if citable, else mark P3 unavailable and rebuild composite from P1/P2/P4 with a noted caveat.

## 6. Job-posting data (capture/proposal/BD consultants)

- **Candidate sources:** USAJOBS API (federal jobs — *not* the right population), aggregators (ToS-restricted), Lightcast/Burning Glass (paid).
- **Auth/Access:** No compliant, free, historical source identified for *private-sector GovCon BD consultant* postings.
- **Why it matters:** Would be an excellent labor-demand proxy if available.
- **Limitations:** Scraping commercial job boards violates ToS; no clean public series.
- **Used in final project?** **No (documented gap).** We will *not* scrape ToS-restricted sites. Recorded as a recommended internal-data collection item for ACE instead.

## 7. SAM.gov / FPDS

- **SAM.gov:** Entity registration data; public extracts at https://sam.gov/data-services. Entity API requires an approved key; bulk extracts exist but are large and licensing-flagged.
- **FPDS:** Underlying contract-action feed (ATOM). USAspending is the cleaned, queryable superset, so **we use USAspending as the canonical front-end** and cite FPDS as the upstream.
- **Why it matters:** SAM registrations are a candidate entrant proxy.
- **Limitations:** SAM registration ≠ active contractor (many register and never bid); API access friction; PII/licensing care.
- **Used in final project?** **Pending/secondary** — USAspending first-award entry is the primary entrant proxy; SAM noted as an alternative/validation source.

## 8. Secondary industry context (NOT primary quantitative data)

- GAO reports, CRS reports (e.g., R44027 on tracking federal awards), GSA MAS sales summaries, Bloomberg Government / DAU / SIA commentary.
- **Role:** sanity-check magnitudes and frame narrative. **Citable, used as context only.** Any number lifted from these is quoted with a citation and never blended into a modeled series without a flag.

---

## Source-to-proxy crosswalk

| Proxy / variable | Primary source | Secondary/validation |
|---|---|---|
| P1 New-entrant index | USAspending (first prime award) | SAM.gov, Census BDS (base rate) |
| P2 Procurement-complexity index | USAspending (IDV flags, task orders, vehicle share) | GAO/CRS context |
| P3 Search-interest index | Google Trends | — (no clean substitute) |
| P4 Tech-entry index | USAspending (IT/cyber/cloud/AI NAICS+PSC × vendor count) | GSA MAS IT sales (context) |
| Real-dollar deflation | FRED `GDPDEF` | BEA published tables |
| Macro controls | FRED (`FGEXPND`, `GDP`) | — |
| Consulting-sector backdrop | BLS (NAICS 5416) | Census BDS |

---

## Reproducibility & keys

- API keys go in a local `.env` (git-ignored): `FRED_API_KEY=...`, optionally `CENSUS_API_KEY`, `BLS_API_KEY`. USAspending needs none.
- Every raw pull is cached to `data/raw/` with the request parameters and a fetch timestamp so results are reproducible and auditable.
- `src/01_download_data.py` logs each source as `OK`, `EMPTY`, or `FAILED(reason)`; `quality_control.md` summarizes the run.
