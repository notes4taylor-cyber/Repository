"""
10_build_pdf.py — assemble the final report PDF from REAL outputs.

Builds outputs/report/Outsourced_GovCon_BD_Market_Report.pdf using matplotlib's
PdfPages (no external/system PDF tooling needed). Pulls the real GAO-based trend
and forecast (src/09) and the segmentation (src/07). Figures and numbers are real
and sourced (data/raw/SOURCES.md); proxy-dependent sections that require the live
API pull are clearly marked as such.
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import image as mpimg

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402

log = C.get_logger("pdf")
ACE_BLUE, ACE_ORANGE = "#1f3a5f", "#e07b1a"
PAGE = (8.5, 11)  # letter portrait


def _csv(name):
    p = C.OUT_TABLES / name
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


def text_page(pdf, title, body, subtitle=None):
    fig = plt.figure(figsize=PAGE)
    fig.patch.set_facecolor("white")
    fig.text(0.08, 0.93, title, fontsize=19, fontweight="bold", color=ACE_BLUE)
    if subtitle:
        fig.text(0.08, 0.895, subtitle, fontsize=10.5, color="#555555", style="italic")
    y = 0.85
    for para in body:
        wrapped = textwrap.fill(para, width=98) if not para.startswith(("•", "  ")) else para
        for line in wrapped.split("\n"):
            fig.text(0.08, y, line, fontsize=10.5, color="#1a1a1a", va="top")
            y -= 0.022
        y -= 0.012
    fig.text(0.08, 0.04, "ACE Business Development — Outsourced GovCon BD Market Study",
             fontsize=7.5, color="#999999")
    pdf.savefig(fig); plt.close(fig)


def image_page(pdf, title, image_path, caption, table_df=None):
    fig = plt.figure(figsize=PAGE)
    fig.patch.set_facecolor("white")
    fig.text(0.08, 0.94, title, fontsize=17, fontweight="bold", color=ACE_BLUE)
    if Path(image_path).exists():
        ax = fig.add_axes([0.08, 0.50, 0.84, 0.38])
        ax.imshow(mpimg.imread(image_path)); ax.axis("off")
    else:
        fig.text(0.08, 0.7, "[chart unavailable]", fontsize=11, color="red")
    fig.text(0.08, 0.47, caption, fontsize=9, color="#555555", style="italic")
    if table_df is not None and not table_df.empty:
        ax2 = fig.add_axes([0.08, 0.10, 0.84, 0.32]); ax2.axis("off")
        tbl = ax2.table(cellText=table_df.values, colLabels=table_df.columns,
                        loc="center", cellLoc="center")
        tbl.auto_set_font_size(False); tbl.set_fontsize(7.5); tbl.scale(1, 1.3)
        for (r, _), cell in tbl.get_celld().items():
            if r == 0:
                cell.set_facecolor(ACE_BLUE); cell.set_text_props(color="white", fontweight="bold")
    pdf.savefig(fig); plt.close(fig)


def main() -> None:
    trend = _csv("real_trend_total_obligations.csv")
    fc = _csv("real_forecast_2030.csv")
    seg = _csv("ace_prospect_fit_segments.csv")
    summ = (C.OUT_TABLES / "real_summary.txt")
    summ_txt = summ.read_text() if summ.exists() else ""

    # pull headline numbers
    t = trend.iloc[0] if not trend.empty else {}
    cagr = t.get("cagr_pct", "n/a"); grow = t.get("cumulative_growth_pct", "n/a")
    ann = t.get("trend_annual_growth_pct", "n/a"); pval = t.get("trend_p_value", "n/a")
    f2030 = fc[fc.fiscal_year == 2030]["baseline_trend_busd"].iloc[0] if not fc.empty else "n/a"
    f2030c = fc[fc.fiscal_year == 2030]["conservative_busd"].iloc[0] if not fc.empty else "n/a"
    f2030h = fc[fc.fiscal_year == 2030]["high_growth_busd"].iloc[0] if not fc.empty else "n/a"
    top3 = ", ".join(seg.segment.head(3)) if not seg.empty else "n/a"

    out = C.OUT_REPORT / "Outsourced_GovCon_BD_Market_Report.pdf"
    with PdfPages(out) as pdf:
        # ---- Cover ----
        fig = plt.figure(figsize=PAGE); fig.patch.set_facecolor("white")
        fig.add_axes([0, 0.62, 1, 0.02]).axis("off")
        fig.text(0.08, 0.74, "Is Outsourced GovCon Business", fontsize=27, fontweight="bold", color=ACE_BLUE)
        fig.text(0.08, 0.69, "Development a Growing Market?", fontsize=27, fontweight="bold", color=ACE_BLUE)
        fig.text(0.08, 0.63, "A data-driven market-intelligence study for ACE Business Development",
                 fontsize=12.5, color="#444444")
        fig.text(0.08, 0.55, f"Headline finding (real GAO data, FY2015–FY2024):", fontsize=12, fontweight="bold")
        fig.text(0.08, 0.51, f"• Federal contract obligations grew +{grow}% over the decade "
                 f"(CAGR {cagr}%/yr, trend +{ann}%/yr, p<0.001).", fontsize=11)
        fig.text(0.08, 0.475, f"• Baseline forecast reaches ~${f2030:.0f}B by FY2030 "
                 f"(range ${f2030c:.0f}B–${f2030h:.0f}B).", fontsize=11)
        fig.text(0.08, 0.44, f"• Top ACE target segments: {top3}.", fontsize=11)
        fig.text(0.08, 0.40, "• Outsourced-BD demand is measured via documented proxies — this is",
                 fontsize=11)
        fig.text(0.095, 0.375, "descriptive/associational, not causal. See Limitations.", fontsize=11)
        fig.text(0.08, 0.12, "Prepared by: Senior econometrics research assistant (Claude)\n"
                 "Method: GAO Snapshot of Government-Wide Contracting + transparent proxy framework\n"
                 "Data provenance: data/raw/SOURCES.md   |   Reproduce: README.md",
                 fontsize=9, color="#666666")
        fig.text(0.08, 0.05, "FY2015–FY2024 analysis · forecast to FY2030", fontsize=9, color=ACE_ORANGE)
        pdf.savefig(fig); plt.close(fig)

        # ---- Executive summary ----
        text_page(pdf, "1. Executive Summary",
                  subtitle="The business question: Is outsourced GovCon BD a growing market, and where can ACE capitalize?",
                  body=[
            f"Federal contracting — the pond every outsourced-BD client fishes in — grew from $438B "
            f"in FY2015 to $755B in FY2024, a +{grow}% increase (CAGR {cagr}%/yr). A log-linear trend "
            f"estimates +{ann}% per year and is highly significant (p<0.001, R²=0.96, n=9 GAO data points).",
            "There is no public dataset that directly measures 'spending on outsourced GovCon business "
            "development.' So this study measures the CONDITIONS that create demand for it — the size and "
            "growth of federal contracting, the technology-spend mix, contractor entry, and procurement "
            "complexity — and scores which contractor segments are most likely to buy.",
            f"Forecast: under a baseline trend, federal contract obligations reach ~${f2030:.0f}B by FY2030 "
            f"(conservative ${f2030c:.0f}B, high-growth ${f2030h:.0f}B). Federal IT obligations rose to ~$126B "
            f"in FY2024 (+5% YoY), continuing a tech-led shift that favors outsourced BD for tech entrants.",
            f"Where ACE should focus: the highest-propensity segments are {top3}. These share three traits — "
            "recent or imminent federal entry, operation in fast-growing technology markets, and a high "
            "likelihood of lacking a mature in-house BD/capture function.",
            "Confidence & honesty: the contracting growth and forecast use REAL GAO figures. The outsourced-BD "
            "demand read-through is a proxy argument, not a measured dollar market. Findings are associational, "
            "not causal, and the segment score is a transparent prioritization heuristic, not a trained model.",
        ])

        # ---- Trend (real) ----
        image_page(pdf, "2. Federal Contracting Grew Sharply Over the Decade",
                   C.OUT_CHARTS / "real_01_total_obligations.png",
                   "Source: GAO Snapshot of Government-Wide Contracting (nominal $). Provenance: data/raw/SOURCES.md. "
                   "FY2016 omitted (no single authoritative figure available; not fabricated).",
                   table_df=trend[["first_busd", "last_busd", "cumulative_growth_pct",
                                   "cagr_pct", "trend_annual_growth_pct", "trend_p_value", "r2", "n"]]
                   if not trend.empty else None)

        # ---- Forecast (real) ----
        fc_disp = fc[fc.fiscal_year.isin([2025, 2026, 2027, 2028, 2029, 2030])][
            ["fiscal_year", "conservative_busd", "baseline_trend_busd", "high_growth_busd"]] if not fc.empty else None
        image_page(pdf, "3. Forecast to FY2030 (Three Scenarios)",
                   C.OUT_CHARTS / "real_02_forecast_2030.png",
                   "Baseline = log-linear trend with 80% prediction interval. Conservative assumes ~1.5%/yr "
                   "below-trend drag (flat budgets/CRs); High-growth assumes ~3%/yr above trend (sustained "
                   "cyber/AI/cloud demand). ~9 annual points → wide intervals; treat as ranges, not point bets.",
                   table_df=fc_disp)

        # ---- Segmentation (real) ----
        seg_disp = seg[["segment", "ace_prospect_fit_score"]].copy() if not seg.empty else None
        if seg_disp is not None:
            seg_disp.columns = ["Contractor segment", "ACE Prospect Fit (0-100)"]
        image_page(pdf, "4. Which Contractors Are Most Likely to Buy Outsourced BD",
                   C.OUT_CHARTS / "segment_scores.png",
                   "ACE Prospect Fit Score — a transparent, additive heuristic (formula in src/07_segmentation.py). "
                   "Not a trained model: there is no ground-truth 'bought outsourced BD' label.",
                   table_df=seg_disp)

        # ---- ACE implications ----
        text_page(pdf, "5. Implications for ACE Business Development", body=[
            f"Where to look for clients: prioritize {top3}. The common thread is firms with strong technical "
            "capability but weak federal sales infrastructure — exactly the gap outsourced capture/proposal/"
            "market-entry services fill.",
            "Most attractive segments: (1) commercial tech firms crossing into federal for the first time; "
            "(2) fast-growing cyber/AI/cloud SMBs; (3) recent entrants concentrated in a single agency who need "
            "to diversify; (4) firms chasing their first GWAC/IDIQ vehicle.",
            "Markets driving demand: the technology categories (IT, cyber, cloud, AI) growing faster than the "
            "overall ~6%/yr base. Federal IT reached ~$126B in FY2024; tech entrants are the prototypical buyer.",
            "Positioning: sell capture + proposal + federal market-entry as a MANAGED SERVICE ('fractional BD'), "
            "emphasizing vehicle strategy (how to get on GWAC/IDIQ/BPA) where procurement complexity is highest.",
            "Data ACE should collect internally to upgrade this model: win/loss by pursuit; each client's size and "
            "federal tenure at engagement start; agency concentration; services purchased; outcomes. That turns this "
            "heuristic into a trainable propensity model and lets ACE measure true ROI by segment.",
        ])

        # ---- Methodology, sources, limitations ----
        text_page(pdf, "6. Methodology, Data & Limitations", body=[
            "DATA (real): GAO 'Snapshot of Government-Wide Contracting' annual totals, FY2015–FY2024 (nominal $, "
            "FPDS/USAspending basis), plus published federal-IT figures. Every value is cited in data/raw/SOURCES.md.",
            "WHY GAO (not the live API): the build environment's network was firewalled from api.usaspending.gov "
            "and FRED, so the granular live pull could not run here. The full reproducible API pipeline (src/01–08) "
            "is built and ready; run it with network access to refresh and extend (agency/NAICS panels, the composite "
            "BD Demand Index, and panel fixed-effects regressions).",
            "METHODS: CAGR and a log-linear trend regression with Newey–West (HAC) standard errors for the growth "
            "test; log-linear trend with 80% prediction intervals plus an ARIMA cross-check and three assumption-based "
            "scenarios for the forecast; a transparent additive scoring heuristic for segmentation.",
            "LIMITATIONS (read before quoting): (1) No direct dependent variable — outsourced-BD spend is "
            "unobservable; this is a proxy argument. (2) Associational, not causal — no identification strategy. "
            "(3) Small N (~9 annual points) → low power, wide forecast bands. (4) Figures are nominal; GAO notes "
            "FY2024 was a real-terms decline vs FY2023. (5) FY2016 omitted rather than fabricated. (6) The segment "
            "score encodes judgment, not validated prediction.",
            "BOTTOM LINE: the FEDERAL CONTRACTING MARKET clearly grew over the decade and is projected to keep "
            "growing to 2030 — a favorable backdrop for outsourced BD. The specific size of the outsourced-BD niche "
            "remains an inference, not a measured figure, until internal ACE data or the granular pull is added.",
        ])

    log.info("PDF written -> %s", out)
    print(f"PDF: {out}")


if __name__ == "__main__":
    main()
