"""
08_generate_report.py — Phase 9: assemble the industry report.

Reads the computed tables/charts and writes a business-readable Markdown report
to outputs/report/outsourced_govcon_bd_market_report.md. Numbers are pulled from
the generated CSVs so the report stays in sync with the data. Sections with
missing inputs are marked "[pending data run]" rather than fabricated.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402

log = C.get_logger("report")
REL_CHART = "../charts"   # report lives in outputs/report/


def _csv(name: str, where: Path = C.OUT_TABLES) -> pd.DataFrame:
    p = where / name
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


def _md_table(df: pd.DataFrame, max_rows: int = 12) -> str:
    if df.empty:
        return "_[pending data run — generated once the acquisition pipeline runs against live APIs]_\n"
    d = df.head(max_rows).copy()
    for c in d.columns:
        if d[c].dtype.kind in "fc":
            d[c] = d[c].map(lambda v: f"{v:,.3g}" if pd.notna(v) else "")
    return d.to_markdown(index=False) + "\n"


def _fig(fname: str, caption: str) -> str:
    if (C.OUT_CHARTS / fname).exists():
        return f"![{caption}]({REL_CHART}/{fname})\n\n*Figure: {caption}*\n"
    return f"_[chart {fname} pending data run]_\n"


def _pct(x) -> str:
    try:
        return f"{float(x)*100:.1f}%"
    except Exception:
        return "n/a"


def main() -> None:
    log.info("=== Phase 9: report generation ===")
    cagr = _csv("cagr_summary.csv")
    trend = _csv("trend_tests.csv")
    ols = _csv("ols_national.csv")
    seg = _csv("ace_prospect_fit_segments.csv")
    fc = _csv("forecasts_2030.csv")
    bt = _csv("forecast_backtest.csv")
    scen = _csv("scenarios.csv")

    top_segments = ", ".join(seg["segment"].head(3)) if not seg.empty else "[pending]"

    R = []
    R.append("# Outsourced GovCon Business Development — Market Intelligence Report\n")
    R.append("**Prepared for ACE Business Development**  ·  **Analysis window: FY2015–FY2024**  ·  "
             "**Forecast horizon: FY2030**\n")
    R.append("> Scope note: there is no public dataset that directly measures spending on "
             "outsourced GovCon business development. This report triangulates **four independent "
             "demand proxies** built from official procurement data, macro data, and search-interest "
             "data. All findings are **associational/descriptive**, not causal. Every proxy, "
             "assumption, and limitation is documented.\n")
    R.append("\n---\n")

    # 1. Executive summary
    R.append("## 1. Executive Summary\n")
    R.append("**The business question:** *Is outsourced GovCon business development a growing market, "
             "and where can ACE capitalize?*\n")
    R.append("**Short answer (evidence-graded):** The *observable conditions that create demand* for "
             "outsourced BD — federal technology spending, procurement complexity, contractor entry, "
             "and search interest in capture/proposal/BD consulting — are analyzed below over a decade "
             "and projected to 2030. The composite **BD Demand Index** summarizes the direction.\n")
    if not trend.empty and "BD_Demand_Index" in set(trend.get("variable", [])):
        row = trend[trend["variable"] == "BD_Demand_Index"].iloc[0]
        R.append(f"- **BD Demand Index trend:** ~{_pct(row.get('annual_growth'))} per year "
                 f"(p={row.get('p_value', float('nan')):.3f}, n={int(row.get('n', 0))}).\n")
    R.append(f"- **Highest-priority ACE target segments:** {top_segments}.\n")
    R.append("- **Caveat:** ~10 annual observations → low statistical power and wide forecast "
             "intervals. Treat 2030 figures as scenario ranges, not point predictions.\n")
    R.append(_fig("08_bd_demand_index.png", "Composite BD Demand Index, FY2015–FY2024"))

    # 2. Research questions
    R.append("\n## 2. Research Questions\n")
    R.append("1. Have the market conditions driving outsourced GovCon BD demand grown over 10 years?\n"
             "2. Which observable factors co-move with the BD-demand proxies?\n"
             "3. Which contractor segments are most likely to buy outsourced BD?\n"
             "4. Is demand likely to keep growing through 2030 (under stated assumptions)?\n")

    # 3. Methodology
    R.append("\n## 3. Methodology\n")
    R.append("Descriptive trend analysis (log-linear trends with Newey–West SEs), pooled OLS and "
             "two-way fixed-effects panel regressions (agency-year and NAICS-year, SEs clustered by "
             "entity), and three forecasting approaches (trend, ARIMA, gradient boosting) validated by "
             "expanding-window backtests. Full design in `research_plan.md`.\n")

    # 4. Data sources
    R.append("\n## 4. Data Sources\n")
    R.append("USAspending.gov API (primary; obligations, awards, NAICS/PSC, vehicles, recipients), "
             "FRED (deflator + macro controls), Census BDS and BLS (sector context), Google Trends "
             "(search interest). Detail, endpoints, and limitations in `data_sources.md`.\n")

    # 5. Proxy construction
    R.append("\n## 5. Proxy Construction\n")
    R.append("| Proxy | What it measures | Source | Key weakness |\n|---|---|---|---|\n"
             "| P1 New-entrant | First-time federal recipients/yr | USAspending | First-award ≠ first-attempt |\n"
             "| P2 Complexity | IDV obligation share, vehicle/order counts | USAspending | Complexity ≠ outsourcing |\n"
             "| P3 Search | Interest in BD/capture/proposal consulting | Google Trends | Relative, sampled, noisy |\n"
             "| P4 Tech-entry | Tech obligations × distinct vendors | USAspending | Taxonomy fuzziness |\n"
             "| **Composite BD Demand Index** | z-scored equal-weight of P1–P4 | derived | Can mask divergence |\n")
    R.append("\nComposite: each proxy is z-scored, averaged (equal weights by default), and re-expressed "
             "as an index (base FY2015 = 100; +1 sd ≈ +25 points). Components are always shown alongside "
             "the composite so divergence is visible.\n")
    R.append(_fig("07_proxies.png", "Demand proxies indexed to FY2015 = 100"))

    # 6. Trend analysis
    R.append("\n## 6. Trend Analysis\n")
    R.append("**Compound annual growth rates (FY2015→FY2024):**\n\n")
    R.append(_md_table(cagr))
    R.append("\n**Trend significance (log-linear, HAC SEs):**\n\n")
    R.append(_md_table(trend))
    R.append("\n")
    R.append(_fig("01_federal_contracting.png", "Federal contract obligations, nominal vs real"))
    R.append(_fig("02_tech_contracting.png", "Federal IT/cyber/cloud/AI obligations (real)"))
    R.append(_fig("05_complexity.png", "Procurement complexity: IDV obligation share"))
    R.append(_fig("04_new_entrants.png", "New federal contractor entry (proxy)"))
    R.append(_fig("06_search_interest.png", "Search interest in GovCon BD consulting"))

    # 7. Econometric results
    R.append("\n## 7. Econometric Results\n")
    R.append("**Pooled OLS — DV: BD Demand Index (standardized betas, HC3 SEs). Associational only:**\n\n")
    R.append(_md_table(ols))
    R.append("\nPanel fixed-effects results (agency-year, NAICS-year; entity+time FE, clustered SEs) "
             "are in `outputs/tables/panel_fe_agency.txt` and `panel_fe_naics.txt`. These absorb "
             "time-invariant entity differences and common shocks but **do not identify causal effects** "
             "— there is no exogenous variation or instrument. Read coefficients as conditional "
             "associations on a proxy outcome.\n")

    # 8. Forecast
    R.append("\n## 8. Forecast Through 2030\n")
    R.append("**Scenario assumptions:**\n\n")
    R.append(_md_table(scen))
    R.append("\n**Backtest accuracy (expanding window, last 3 FY):**\n\n")
    R.append(_md_table(bt))
    R.append("\n**Forecast table (selected):**\n\n")
    R.append(_md_table(fc, max_rows=18))
    R.append("\n")
    R.append(_fig("fan_BD_Demand_Index.png", "BD Demand Index forecast to 2030 with 80% interval"))
    R.append(_fig("fan_real_tech_obligations.png", "Real technology obligations forecast to 2030"))

    # 9. Segmentation
    R.append("\n## 9. Contractor Segmentation & ACE Prospect Fit Score\n")
    R.append("The **ACE Prospect Fit Score** (0–100) ranks segments by likely need for outsourced BD. "
             "It is a transparent additive heuristic — **not** a validated predictive model (no "
             "ground-truth purchase label exists). Formula and weights: see `src/07_segmentation.py`.\n\n")
    R.append(_md_table(seg))
    R.append("\n")
    R.append(_fig("segment_scores.png", "Contractor segment prioritization"))

    # 10. ACE implications
    R.append("\n## 10. Implications for ACE Business Development\n")
    R.append(f"**Where should ACE look for clients?** The highest-scoring segments are: "
             f"**{top_segments}**. These share three traits: recent/imminent federal entry, "
             "operation in fast-growing technology markets, and a high likelihood of lacking a mature "
             "internal BD/capture function.\n")
    R.append("- **Most attractive segments:** commercial tech firms crossing into federal; fast-growing "
             "cyber/AI/cloud SMBs; recent entrants concentrated in a single agency who need to diversify.\n"
             "- **Agencies / tech markets driving demand:** the technology-heavy buying centers and the "
             "NAICS/PSC tech categories with the fastest real-obligation and vendor-count growth (see "
             "Section 6 tables) are where outsourced-BD need concentrates.\n"
             "- **Positioning:** lead with *capture + proposal + federal market-entry as a managed service* "
             "for firms with strong technical product but weak federal sales infrastructure. Emphasize "
             "vehicle strategy (GWAC/IDIQ/BPA access) where complexity is rising.\n"
             "- **Internal data ACE should collect** to upgrade this model: win/loss by pursuit, client "
             "size and federal tenure at engagement start, agency-concentration of clients, services "
             "purchased, and outcomes. That converts this heuristic into a *trainable* propensity model.\n")

    # 11. Limitations
    R.append("\n## 11. Limitations\n")
    R.append("- **No direct dependent variable** — outsourced-BD spend is unobservable; all results "
             "concern proxies.\n- **Associational, not causal** — no identification strategy.\n"
             "- **Small N (~10 annual points)** — low power, wide intervals, ML overfitting risk.\n"
             "- **Obligations ≠ outlays ≠ vendor revenue**; fiscal vs calendar alignment handled but "
             "imperfect.\n- **Recipient dedup / top-N sampling** make entrant and concentration figures "
             "approximate.\n- **Google Trends** is relative and noisy.\n- **Segmentation score is "
             "judgment-encoded**, not validated. Full list in `research_plan.md` §9 and "
             "`quality_control.md`.\n")

    # 12. Next steps
    R.append("\n## 12. Recommended Next Steps\n")
    R.append("1. Acquire a true contractor-history extract (bulk USAspending) for exact first-award "
             "entrant detection and population-level concentration.\n"
             "2. Add a compliant job-postings feed (e.g., licensed Lightcast) for a labor-demand proxy.\n"
             "3. Collect ACE's internal win/loss + client-profile data to train and validate a real "
             "propensity model against the Prospect Fit heuristic.\n"
             "4. Refresh quarterly; widen to sub-award and B&P signals if obtainable.\n")

    R.append("\n---\n*Generated by `src/08_generate_report.py`. Reproduce with the pipeline in "
             "`README.md`. All figures regenerate from `data/processed/`.*\n")

    out = C.OUT_REPORT / "outsourced_govcon_bd_market_report.md"
    out.write_text("\n".join(R))
    log.info("report written -> %s", out)


if __name__ == "__main__":
    main()
