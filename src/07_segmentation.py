"""
07_segmentation.py — Phase 7: contractor segmentation & ACE Prospect Fit Score.

Defines theory-driven contractor segments and scores them on a transparent,
additive ACE Prospect Fit Score. Where contractor-level data (recipient panel)
is available, it ALSO scores individual recipients; otherwise it scores segments.

IMPORTANT: This is a PRIORITIZATION HEURISTIC, not a validated predictive model.
There is no ground-truth "bought outsourced BD" label, so the score encodes
domain judgment about WHO is most likely to need outsourced BD. Weights are
stated and a sensitivity check (equal vs domain weights) is emitted.

Outputs: outputs/tables/ace_prospect_fit_segments.csv
         outputs/tables/ace_prospect_fit_contractors.csv (if data allows)
         outputs/charts/segment_scores.png
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402

log = C.get_logger("segment")
ACE_BLUE = "#1f3a5f"

# --------------------------------------------------------------------------- #
# ACE Prospect Fit Score — documented formula
#   Score = sum_i  w_i * component_i        (each component normalized to 0..1)
#   Higher score = higher likely need for OUTSOURCED BD.
# Components (0..1, with direction):
#   market_growth        : growth of the firm's primary market           (+)
#   small_mid_size       : smaller firms score higher (inverted size)     (+)
#   new_entrant          : recently entered federal market                (+)
#   agency_concentration : revenue concentrated in one agency (diversify) (+)
#   tech_category        : operates in cyber/AI/cloud/software            (+)
#   vehicle_complexity   : exposure to/pursuit of IDIQ/GWAC/BPA           (+)
#   competitive_intensity: faces crowded markets (needs differentiation)  (+)
#   weak_internal_bd     : likely lacks mature internal BD team           (+)
# --------------------------------------------------------------------------- #
WEIGHTS = {
    "market_growth": 0.15,
    "small_mid_size": 0.15,
    "new_entrant": 0.15,
    "agency_concentration": 0.12,
    "tech_category": 0.15,
    "vehicle_complexity": 0.10,
    "competitive_intensity": 0.08,
    "weak_internal_bd": 0.10,
}

# Theory-driven segment definitions with prior component scores (0..1).
# These priors encode the hypotheses in research_plan.md §8 and are the
# transparent "judgment layer" of the heuristic.
SEGMENTS = [
    ("Commercial tech firm entering federal", dict(market_growth=.9, small_mid_size=.6,
        new_entrant=1.0, agency_concentration=.7, tech_category=1.0, vehicle_complexity=.5,
        competitive_intensity=.7, weak_internal_bd=1.0)),
    ("Small/mid contractor, single-agency concentrated", dict(market_growth=.6, small_mid_size=.9,
        new_entrant=.5, agency_concentration=1.0, tech_category=.5, vehicle_complexity=.5,
        competitive_intensity=.6, weak_internal_bd=.8)),
    ("Fast-growing cyber/AI/cloud SMB", dict(market_growth=1.0, small_mid_size=.8,
        new_entrant=.6, agency_concentration=.6, tech_category=1.0, vehicle_complexity=.6,
        competitive_intensity=.8, weak_internal_bd=.7)),
    ("Recent federal entrant (any sector)", dict(market_growth=.6, small_mid_size=.8,
        new_entrant=1.0, agency_concentration=.8, tech_category=.5, vehicle_complexity=.4,
        competitive_intensity=.6, weak_internal_bd=.9)),
    ("Firm chasing first GWAC/IDIQ", dict(market_growth=.7, small_mid_size=.7,
        new_entrant=.6, agency_concentration=.6, tech_category=.6, vehicle_complexity=1.0,
        competitive_intensity=.7, weak_internal_bd=.7)),
    ("Established large prime", dict(market_growth=.4, small_mid_size=.1,
        new_entrant=.1, agency_concentration=.3, tech_category=.5, vehicle_complexity=.4,
        competitive_intensity=.4, weak_internal_bd=.1)),
    ("Stable niche incumbent (single agency, mature)", dict(market_growth=.3, small_mid_size=.5,
        new_entrant=.1, agency_concentration=.7, tech_category=.3, vehicle_complexity=.3,
        competitive_intensity=.3, weak_internal_bd=.3)),
]


def score_row(components: dict, weights: dict) -> float:
    return sum(weights[k] * components.get(k, 0.0) for k in weights)


def score_segments() -> pd.DataFrame:
    rows = []
    equal_w = {k: 1 / len(WEIGHTS) for k in WEIGHTS}
    for name, comp in SEGMENTS:
        rows.append({
            "segment": name,
            "ace_prospect_fit_score": round(100 * score_row(comp, WEIGHTS), 1),
            "score_equal_weights": round(100 * score_row(comp, equal_w), 1),
            **{k: comp.get(k, 0.0) for k in WEIGHTS},
        })
    df = pd.DataFrame(rows).sort_values("ace_prospect_fit_score", ascending=False)
    df.to_csv(C.OUT_TABLES / "ace_prospect_fit_segments.csv", index=False)

    fig, ax = plt.subplots(figsize=(8.5, 5))
    d = df.iloc[::-1]
    ax.barh(d["segment"], d["ace_prospect_fit_score"], color=ACE_BLUE)
    ax.set_xlabel("ACE Prospect Fit Score (0-100)")
    ax.set_title("Contractor Segment Prioritization for Outsourced BD", fontweight="bold")
    for i, v in enumerate(d["ace_prospect_fit_score"]):
        ax.text(v + 1, i, f"{v:.0f}", va="center", fontsize=8)
    fig.savefig(C.OUT_CHARTS / "segment_scores.png", bbox_inches="tight")
    plt.close(fig)
    log.info("segment scores written (%d segments)", len(df))
    return df


def score_contractors() -> None:
    """Score individual recipients IF the recipient panel is available.
    Maps observable recipient features -> the score components (documented)."""
    p = C.DATA_PROCESSED / "agency_year.csv"  # placeholder check for pipeline run
    rec = C.DATA_INTERIM / "recipients_year.csv"
    techrec = C.DATA_INTERIM / "tech_recipients_year.csv"
    if not rec.exists():
        log.warning("contractor-level scoring skipped (no recipient panel)")
        return
    df = pd.read_csv(rec)
    if df.empty or "code" not in df.columns:
        return
    tech_codes = set()
    if techrec.exists():
        tdf = pd.read_csv(techrec)
        tech_codes = set(tdf["code"].dropna())

    # observable features per recipient
    g = df.groupby("code")
    feat = pd.DataFrame({
        "name": g["name"].first(),
        "years_active": g["fiscal_year"].nunique(),
        "total_amount": g["amount"].sum(),
        "first_year": g["fiscal_year"].min(),
        "last_year": g["fiscal_year"].max(),
    }).reset_index()
    feat["recent_growth"] = g["amount"].apply(
        lambda s: (s.sort_index().iloc[-1] / max(s.sort_index().iloc[0], 1) - 1)
        if len(s) > 1 else 0).values

    # map to 0..1 components
    size_rank = feat["total_amount"].rank(pct=True)
    feat["small_mid_size"] = 1 - size_rank                # smaller -> higher
    feat["new_entrant"] = (feat["first_year"] >= C.FY_END - 2).astype(float)
    feat["weak_internal_bd"] = feat["small_mid_size"]     # proxy: smaller -> weaker BD
    feat["tech_category"] = feat["code"].isin(tech_codes).astype(float)
    feat["market_growth"] = feat["recent_growth"].clip(0, 2) / 2
    feat["agency_concentration"] = 0.7  # not resolvable from this sample -> neutral-high prior
    feat["vehicle_complexity"] = 0.5
    feat["competitive_intensity"] = 0.6

    feat["ace_prospect_fit_score"] = feat.apply(
        lambda r: round(100 * score_row({k: r[k] for k in WEIGHTS}, WEIGHTS), 1), axis=1)
    out = feat.sort_values("ace_prospect_fit_score", ascending=False).head(200)
    out.to_csv(C.OUT_TABLES / "ace_prospect_fit_contractors.csv", index=False)
    log.info("contractor-level scores written (top %d)", len(out))


def main() -> None:
    log.info("=== Phase 7: segmentation & ACE Prospect Fit Score ===")
    score_segments()
    score_contractors()
    log.info("=== segmentation complete ===")


if __name__ == "__main__":
    main()
