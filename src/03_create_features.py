"""
03_create_features.py — Phase 4 (part 2): feature engineering, proxies, index.

Builds the national fiscal-year analytical frame plus agency-year and NAICS-year
panels, then constructs the four demand proxies (P1-P4) and the composite
BD Demand Index exactly as specified in research_plan.md.

Outputs:
  data/processed/national_year.csv      (one row per fiscal year, all features)
  data/processed/agency_year.csv        (agency-year panel for econometrics)
  data/processed/naics_year.csv         (naics-year panel for econometrics)
  data/processed/proxies.csv            (P1-P4 + composite, normalized)

Index construction is fully documented inline and in the report. If an input is
missing (e.g., Google Trends blocked), the affected proxy is set to NaN and the
composite is rebuilt from the available components, with a flag recorded.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402

log = C.get_logger("features")


def _read_interim(name: str) -> pd.DataFrame:
    p = C.DATA_INTERIM / name
    if not p.exists():
        log.warning("missing interim file: %s", name)
        return pd.DataFrame()
    return pd.read_csv(p)


def _hhi(amounts: pd.Series) -> float:
    """Herfindahl–Hirschman index (0-1) over a recipient amount distribution.
    Computed on the top-N recipient SAMPLE -> a concentration *proxy*, not a
    population HHI; documented as such in quality_control.md."""
    total = amounts.sum()
    if total <= 0:
        return np.nan
    shares = amounts / total
    return float((shares ** 2).sum())


def _index_to_base(s: pd.Series) -> pd.Series:
    """Index a series to 100 at the base fiscal year."""
    base = s.loc[s.index == C.BASE_FY]
    base_val = float(base.iloc[0]) if len(base) and base.iloc[0] not in (0, np.nan) else np.nan
    return s / base_val * 100 if base_val and not np.isnan(base_val) else s * np.nan


def _zscore(s: pd.Series) -> pd.Series:
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0


def build_national_frame() -> pd.DataFrame:
    fy = pd.DataFrame({"fiscal_year": C.FISCAL_YEARS})

    # --- obligations + deflation ---
    ot = _read_interim("obligations_over_time.csv")
    deflator = _read_interim("deflator.csv")
    if not ot.empty:
        fy = fy.merge(ot, on="fiscal_year", how="left")
    if not deflator.empty:
        fy = fy.merge(deflator[["fiscal_year", "deflator_factor"]], on="fiscal_year", how="left")
    else:
        fy["deflator_factor"] = 1.0
    fy["deflator_factor"] = fy["deflator_factor"].fillna(1.0)

    for col in ("total_contracts", "idv_obligations", "tech_naics"):
        if col in fy.columns:
            fy[f"real_{col}"] = fy[col] * fy["deflator_factor"]

    # --- complexity: IDV obligation share + award counts ---
    if {"idv_obligations", "total_contracts"}.issubset(fy.columns):
        fy["idv_share"] = fy["idv_obligations"] / (fy["total_contracts"] + fy["idv_obligations"])
    counts = _read_interim("award_counts.csv")
    if not counts.empty:
        fy = fy.merge(counts, on="fiscal_year", how="left")
        if {"idv_vehicles", "definitive_contracts"}.issubset(fy.columns):
            fy["vehicle_count_ratio"] = fy["idv_vehicles"] / (
                fy["definitive_contracts"].replace(0, np.nan))

    # --- tech share ---
    if {"real_tech_naics", "real_total_contracts"}.issubset(fy.columns):
        fy["tech_share"] = fy["real_tech_naics"] / fy["real_total_contracts"]

    # --- concentration / fragmentation (recipient sample) ---
    rec = _read_interim("recipients_year.csv")
    if not rec.empty:
        hhi = rec.groupby("fiscal_year")["amount"].apply(_hhi).reset_index(name="recipient_hhi")
        fy = fy.merge(hhi, on="fiscal_year", how="left")

    # --- tech vendor count (distinct recipients in tech sample) ---
    techrec = _read_interim("tech_recipients_year.csv")
    if not techrec.empty:
        vc = techrec.groupby("fiscal_year")["code"].nunique().reset_index(name="tech_vendor_count")
        fy = fy.merge(vc, on="fiscal_year", how="left")

    # --- new-entrant proxy (recipient appearance across years; approximate) ---
    if not rec.empty:
        seen: set = set()
        entrants = []
        for y in C.FISCAL_YEARS:
            codes = set(rec.loc[rec["fiscal_year"] == y, "code"].dropna())
            new = codes - seen if seen else set()  # FY_START has no baseline -> NaN
            entrants.append({"fiscal_year": y,
                             "new_entrants_proxy": (len(new) if seen else np.nan)})
            seen |= codes
        fy = fy.merge(pd.DataFrame(entrants), on="fiscal_year", how="left")

    # --- Google Trends FY index (P3 raw) ---
    gt = _read_interim("google_trends_fy.csv")
    if not gt.empty:
        term_cols = [c for c in gt.columns if c != "fiscal_year"]
        gt["trends_composite"] = gt[term_cols].mean(axis=1)
        fy = fy.merge(gt[["fiscal_year", "trends_composite"]], on="fiscal_year", how="left")

    fy.to_csv(C.DATA_PROCESSED / "national_year.csv", index=False)
    log.info("national_year.csv: %d rows, %d cols", len(fy), fy.shape[1])
    return fy


def build_proxies(fy: pd.DataFrame) -> pd.DataFrame:
    """Construct P1-P4 and the composite BD Demand Index (documented in report)."""
    idx = fy.set_index("fiscal_year")
    px = pd.DataFrame(index=idx.index)

    # P1 New-entrant index (indexed to base=100)
    if "new_entrants_proxy" in idx:
        px["P1_new_entrant"] = _index_to_base(idx["new_entrants_proxy"])

    # P2 Procurement-complexity index: equal-weight z of idv_share, vehicle_count_ratio
    comp_parts = [c for c in ("idv_share", "vehicle_count_ratio") if c in idx]
    if comp_parts:
        px["P2_complexity"] = pd.concat([_zscore(idx[c]) for c in comp_parts], axis=1).mean(axis=1)

    # P3 Search-interest index (indexed to base=100)
    if "trends_composite" in idx:
        px["P3_search"] = _index_to_base(idx["trends_composite"])

    # P4 Tech-entry index: tech real obligations growth * vendor-count growth
    if {"real_tech_naics", "tech_vendor_count"}.issubset(idx.columns):
        spend_idx = _index_to_base(idx["real_tech_naics"])
        vend_idx = _index_to_base(idx["tech_vendor_count"])
        px["P4_tech_entry"] = (spend_idx * vend_idx) / 100.0  # combined index, base≈100
    elif "real_tech_naics" in idx:
        px["P4_tech_entry"] = _index_to_base(idx["real_tech_naics"])

    # --- Composite: z-score each available proxy, equal weight, re-index to 100 ---
    proxy_cols = [c for c in px.columns if c.startswith("P")]
    if proxy_cols:
        z = pd.concat([_zscore(px[c]) for c in proxy_cols], axis=1)
        z.columns = proxy_cols
        composite_z = z.mean(axis=1)
        # map z back to a readable 100-base index using base-year anchoring
        px["BD_Demand_Index_z"] = composite_z
        # readable version: scale so base year = 100, +1 sd = +25 pts (documented)
        px["BD_Demand_Index"] = 100 + 25 * (composite_z - composite_z.loc[C.BASE_FY])
        px["n_components"] = z.notna().sum(axis=1)

    px = px.reset_index()
    px.to_csv(C.DATA_PROCESSED / "proxies.csv", index=False)
    log.info("proxies.csv built with components: %s", proxy_cols)
    return px


def build_panels() -> None:
    """Agency-year and NAICS-year panels with real dollars and growth features."""
    deflator = _read_interim("deflator.csv")
    dmap = (deflator.set_index("fiscal_year")["deflator_factor"].to_dict()
            if not deflator.empty else {})

    for raw, out, key in (("agency_year.csv", "agency_year.csv", "agency"),
                          ("naics_year.csv", "naics_year.csv", "naics")):
        df = _read_interim(raw)
        if df.empty:
            continue
        df["deflator_factor"] = df["fiscal_year"].map(dmap).fillna(1.0)
        df["real_amount"] = df["amount"] * df["deflator_factor"]
        df = df.sort_values([key if key in df else "code", "fiscal_year"])
        entity = "code"
        df["real_amount_lag"] = df.groupby(entity)["real_amount"].shift(1)
        df["growth"] = (df["real_amount"] / df["real_amount_lag"] - 1)
        # market-level competition: vendors implied not available here; use #entities/yr
        df.to_csv(C.DATA_PROCESSED / out, index=False)
        log.info("panel %s: %d rows", out, len(df))


def main() -> None:
    log.info("=== Phase 4b: feature engineering & proxies ===")
    fy = build_national_frame()
    build_proxies(fy)
    build_panels()
    log.info("=== features complete -> data/processed/ ===")


if __name__ == "__main__":
    main()
