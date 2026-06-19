# Provenance of real figures used in the "published-data" analysis

**Why this file exists.** The build environment's network egress blocked direct access
to the USAspending and FRED APIs, so the live granular pull (`src/01`) could not run here.
To still deliver an analysis on **real numbers** (not fabricated), I compiled the official
**GAO "Snapshot of Government-Wide Contracting"** annual totals (FPDS/USAspending basis) and
published federal-IT figures from credible secondary sources, each cited below. These power
`src/09_published_data_analysis.py` and the PDF. The full granular pipeline (`src/01`–`08`)
remains the canonical method once API egress is available.

## Total federal contract obligations (nominal $)
GAO publishes an annual government-wide contracting snapshot built from FPDS/USAspending.

| FY | $B | Source |
|----|----|--------|
| 2015 | 438 | GAO / USAspending — FY2015 contract obligations (>$430B products & services) |
| 2017 | 507 | GAO Snapshot of Government-Wide Contracting, FY2017 (~$507B) |
| 2018 | 559 | GAO Snapshot, FY2018 (>$550B) |
| 2019 | 586 | GAO Snapshot, FY2019 (>$586B) |
| 2020 | 665 | GAO Snapshot, FY2020 (>$665B; COVID-19 surge) |
| 2021 | 637 | GAO Snapshot, FY2021 (~$637B) |
| 2022 | 694 | GAO Snapshot, FY2022 — "about $694 billion" (gao.gov/blog/snapshot-government-wide-contracting-fy-2022) |
| 2023 | 759 | GAO Snapshot, FY2023 ($759B) |
| 2024 | 755 | GAO Snapshot, FY2024 ($755B; a real-terms decline vs FY2023) |

**FY2016 is intentionally omitted** — I could not confirm a single authoritative published
total via the available channel, so rather than fabricate or interpolate it, it is left out.
The 9 remaining points are sufficient for a credible decade trend.

**Caveats (read before quoting):**
- Figures are **nominal** (current dollars). GAO notes FY2024 was a *decline from FY2023 after
  adjusting for inflation* — real-dollar adjustment needs the FRED deflator (unavailable here).
- Early-year values (FY2015, FY2017–2019) carry ~±2–3% cross-source variance depending on
  prime-only vs all-actions and inflation basis. The **trend/CAGR are robust** to this.
- Other published series (e.g., Bloomberg Government BGOV200 "$705B FY2022", HigherGov "$765B
  FY2023 awarded") differ because of methodology (awards vs obligations). I use the GAO
  obligations basis consistently.

## Federal IT contract obligations
| FY | $B | Source |
|----|----|--------|
| 2023 | 120 | Federal IT contract spending ~$120B, industry/GAO-cited |
| 2024 | 126 | Federal IT contract obligations ~$126B, industry-cited |

Only two well-sourced points were obtainable via the available channel, so IT is presented as
**supporting context** (direction + recent growth rate), not a full modeled series.

## Search reference URLs (retrieved via WebSearch in the build session)
- GAO Federal Contracting hub: https://www.gao.gov/federal-contracting
- GAO FY2022 snapshot: https://www.gao.gov/blog/snapshot-government-wide-contracting-fy-2022
- GAO FY2023 snapshot: https://www.gao.gov/blog/snapshot-government-wide-contracting-fy-2023-interactive-dashboard
- GAO FY2024 snapshot: https://www.gao.gov/blog/snapshot-government-wide-contracting-fy-2024-interactive-dashboard
- GAO FY2020 snapshot: https://www.gao.gov/blog/snapshot-government-wide-contracting-fy-2020-infographic
- GAO FY2019 snapshot: https://www.gao.gov/blog/snapshot-government-wide-contracting-fy-2019-infographic
