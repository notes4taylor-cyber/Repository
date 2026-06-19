"""
01_download_data.py — Phase 3 data acquisition.

Pulls every source documented in data_sources.md into data/raw/ as tidy CSVs,
logging each source as OK / EMPTY / FAILED. Designed to be RERUN-SAFE (responses
are cached) and to DEGRADE GRACEFULLY: if a host is blocked or a key is missing,
it records the failure and continues so the rest of the pipeline still runs.

Run:  python src/01_download_data.py
Requires network egress to: api.usaspending.gov, api.stlouisfed.org (FRED key),
api.census.gov, api.bls.gov, trends.google.com.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402

log = C.get_logger("download")


# --------------------------------------------------------------------------- #
# USAspending helpers
# --------------------------------------------------------------------------- #
def _fy_window(fy_start: int, fy_end: int) -> dict:
    """Return a USAspending time_period filter spanning the given fiscal years."""
    return {"start_date": f"{fy_start - 1}-10-01", "end_date": f"{fy_end}-09-30"}


def usa_spending_over_time(award_type_codes, naics_codes=None, psc_codes=None,
                           label="total") -> pd.DataFrame:
    """National obligations grouped by fiscal year for a filter set."""
    filters = {
        "time_period": [_fy_window(C.FY_START, C.FY_END)],
        "award_type_codes": award_type_codes,
    }
    if naics_codes:
        filters["naics_codes"] = naics_codes
    if psc_codes:
        filters["psc_codes"] = psc_codes
    body = {"group": "fiscal_year", "filters": filters}
    data = C.http_json(f"{C.USA_BASE}/search/spending_over_time/", "POST", body,
                       cache_name=f"usa_overtime_{label}")
    if not data or "results" not in data:
        return pd.DataFrame()
    rows = [{"fiscal_year": int(r["time_period"]["fiscal_year"]),
             "obligations": float(r["aggregated_amount"] or 0),
             "series": label}
            for r in data["results"]]
    return pd.DataFrame(rows)


def usa_category_by_year(category: str, extra_filters: dict | None = None,
                         limit: int = 100, label: str = "") -> pd.DataFrame:
    """Top-`limit` rows of a spending_by_category, looped over each fiscal year.

    category ∈ {naics, psc, awarding_agency, recipient}.
    """
    frames = []
    for fy in C.FISCAL_YEARS:
        filters = {
            "time_period": [_fy_window(fy, fy)],
            "award_type_codes": C.CONTRACT_AWARD_TYPE_CODES,
        }
        if extra_filters:
            filters.update(extra_filters)
        body = {"category": category, "filters": filters, "limit": limit, "page": 1}
        data = C.http_json(f"{C.USA_BASE}/search/spending_by_category/{category}/",
                           "POST", body, cache_name=f"usa_{category}_{label}_{fy}")
        if not data or "results" not in data:
            log.warning("no %s results for FY%d", category, fy)
            continue
        for r in data["results"]:
            frames.append({
                "fiscal_year": fy,
                "code": r.get("code"),
                "name": r.get("name"),
                "amount": float(r.get("amount") or 0),
            })
    return pd.DataFrame(frames)


def usa_award_counts_by_year() -> pd.DataFrame:
    """Award counts per fiscal year for definitive contracts vs IDVs (complexity)."""
    rows = []
    groups = {
        "definitive_contracts": C.CONTRACT_AWARD_TYPE_CODES,
        "idv_vehicles": C.IDV_AWARD_TYPE_CODES,
    }
    for fy in C.FISCAL_YEARS:
        for gname, codes in groups.items():
            body = {"filters": {"time_period": [_fy_window(fy, fy)],
                                "award_type_codes": codes}}
            data = C.http_json(f"{C.USA_BASE}/search/spending_by_award_count/",
                               "POST", body, cache_name=f"usa_count_{gname}_{fy}")
            count = 0
            if data and "results" in data:
                res = data["results"]
                count = sum(v for v in res.values() if isinstance(v, (int, float)))
            rows.append({"fiscal_year": fy, "group": gname, "award_count": count})
    return pd.DataFrame(rows)


def download_usaspending() -> None:
    src = "usaspending"
    try:
        # 1) Toptier agencies (panel skeleton)
        ag = C.http_json(f"{C.USA_BASE}/references/toptier_agencies/",
                         cache_name="usa_toptier_agencies")
        if ag and "results" in ag:
            pd.DataFrame(ag["results"]).to_csv(C.DATA_RAW / "usa_agencies.csv", index=False)

        # 2) Total contract obligations by FY (+ IDV obligations for complexity)
        total = usa_spending_over_time(C.CONTRACT_AWARD_TYPE_CODES, label="total_contracts")
        idv = usa_spending_over_time(C.IDV_AWARD_TYPE_CODES, label="idv_obligations")
        tech_naics = usa_spending_over_time(C.CONTRACT_AWARD_TYPE_CODES,
                                            naics_codes=list(C.TECH_NAICS.keys()),
                                            label="tech_naics")
        ot = pd.concat([total, idv, tech_naics], ignore_index=True)
        ot.to_csv(C.DATA_RAW / "usa_obligations_over_time.csv", index=False)

        # 3) By-category panels (looped per FY)
        usa_category_by_year("awarding_agency", label="agency").to_csv(
            C.DATA_RAW / "usa_by_agency_year.csv", index=False)
        usa_category_by_year("naics", label="naics").to_csv(
            C.DATA_RAW / "usa_by_naics_year.csv", index=False)
        usa_category_by_year("psc", label="psc").to_csv(
            C.DATA_RAW / "usa_by_psc_year.csv", index=False)

        # 4) Recipient sample (top 500) per FY — concentration + tech-vendor proxy
        usa_category_by_year("recipient", limit=500, label="recipient").to_csv(
            C.DATA_RAW / "usa_recipients_top_year.csv", index=False)
        usa_category_by_year("recipient", limit=500,
                             extra_filters={"naics_codes": list(C.TECH_NAICS.keys())},
                             label="tech_recipient").to_csv(
            C.DATA_RAW / "usa_tech_recipients_top_year.csv", index=False)

        # 5) Award counts (complexity)
        usa_award_counts_by_year().to_csv(
            C.DATA_RAW / "usa_award_counts.csv", index=False)

        C.write_status(src, "OK", "obligations, agency/naics/psc/recipient panels, counts")
        log.info("USAspending: OK")
    except Exception as e:  # noqa: BLE001
        C.write_status(src, "FAILED", str(e)[:200])
        log.error("USAspending FAILED: %s", e)


# --------------------------------------------------------------------------- #
# FRED
# --------------------------------------------------------------------------- #
def download_fred() -> None:
    src = "fred"
    if not C.FRED_API_KEY:
        C.write_status(src, "FAILED", "no FRED_API_KEY in env/.env")
        log.warning("FRED skipped: set FRED_API_KEY in .env (see data_sources.md)")
        return
    try:
        frames = []
        for sid in C.FRED_SERIES:
            params = {"series_id": sid, "api_key": C.FRED_API_KEY,
                      "file_type": "json", "observation_start": "2010-01-01"}
            data = C.http_json(C.FRED_BASE, params=params, cache_name=f"fred_{sid}")
            if not data or "observations" not in data:
                continue
            df = pd.DataFrame(data["observations"])[["date", "value"]]
            df["series_id"] = sid
            frames.append(df)
        if frames:
            pd.concat(frames, ignore_index=True).to_csv(
                C.DATA_RAW / "fred_macro.csv", index=False)
            C.write_status(src, "OK", ",".join(C.FRED_SERIES))
        else:
            C.write_status(src, "EMPTY", "no observations returned")
    except Exception as e:  # noqa: BLE001
        C.write_status(src, "FAILED", str(e)[:200])
        log.error("FRED FAILED: %s", e)


# --------------------------------------------------------------------------- #
# Census BDS (context)
# --------------------------------------------------------------------------- #
def download_census_bds() -> None:
    src = "census_bds"
    try:
        params = {"get": "YEAR,FIRM,ESTAB,JOB_CREATION,ESTABS_ENTRY",
                  "time": "from 2010 to 2022"}
        if C.CENSUS_API_KEY:
            params["key"] = C.CENSUS_API_KEY
        data = C.http_json(C.CENSUS_BDS, params=params, cache_name="census_bds")
        if data and len(data) > 1:
            pd.DataFrame(data[1:], columns=data[0]).to_csv(
                C.DATA_RAW / "census_bds.csv", index=False)
            C.write_status(src, "OK", "firm/estab births")
        else:
            C.write_status(src, "EMPTY", "no rows")
    except Exception as e:  # noqa: BLE001
        C.write_status(src, "FAILED", str(e)[:200])
        log.error("Census BDS FAILED: %s", e)


# --------------------------------------------------------------------------- #
# BLS (context) — NAICS 5416 management/technical consulting employment
# --------------------------------------------------------------------------- #
def download_bls() -> None:
    src = "bls"
    try:
        # CES series for Management & Technical Consulting Services employment
        series_id = "CEU6054160001"  # all employees, NAICS 54161-ish (thousands)
        body = {"seriesid": [series_id], "startyear": "2014", "endyear": "2024"}
        if C.BLS_API_KEY:
            body["registrationkey"] = C.BLS_API_KEY
        data = C.http_json(C.BLS_BASE, "POST", body, cache_name="bls_5416")
        rows = []
        if data and data.get("Results", {}).get("series"):
            for s in data["Results"]["series"]:
                for d in s.get("data", []):
                    rows.append({"series_id": s["seriesID"], "year": d["year"],
                                 "period": d["period"], "value": d["value"]})
        if rows:
            pd.DataFrame(rows).to_csv(C.DATA_RAW / "bls_consulting.csv", index=False)
            C.write_status(src, "OK", series_id)
        else:
            C.write_status(src, "EMPTY", "no series data (BLS often needs a key)")
    except Exception as e:  # noqa: BLE001
        C.write_status(src, "FAILED", str(e)[:200])
        log.error("BLS FAILED: %s", e)


# --------------------------------------------------------------------------- #
# Google Trends (P3) via pytrends
# --------------------------------------------------------------------------- #
def download_google_trends() -> None:
    src = "google_trends"
    try:
        from pytrends.request import TrendReq
    except ImportError:
        C.write_status(src, "FAILED", "pytrends not installed")
        log.warning("pytrends not installed; skipping Google Trends")
        return
    try:
        py = TrendReq(hl="en-US", tz=300, timeout=(10, 25))
        frames = []
        # Trends allows max 5 terms per request; split into batches.
        terms = C.TRENDS_TERMS
        for i in range(0, len(terms), 5):
            batch = terms[i:i + 5]
            py.build_payload(batch, timeframe="2015-01-01 2024-12-31", geo="US")
            df = py.interest_over_time()
            if not df.empty:
                if "isPartial" in df.columns:
                    df = df.drop(columns=["isPartial"])
                frames.append(df)
        if frames:
            out = pd.concat(frames, axis=1)
            out.to_csv(C.DATA_RAW / "google_trends.csv")
            C.write_status(src, "OK", ",".join(terms))
        else:
            C.write_status(src, "EMPTY", "no trends data")
    except Exception as e:  # noqa: BLE001
        C.write_status(src, "FAILED", str(e)[:200])
        log.error("Google Trends FAILED (often 429/blocked): %s", e)


# --------------------------------------------------------------------------- #
def main() -> None:
    (C.DATA_RAW / "_download_status.log").unlink(missing_ok=True)
    log.info("=== Phase 3: data acquisition (FY%d-FY%d) ===", C.FY_START, C.FY_END)
    download_usaspending()
    download_fred()
    download_census_bds()
    download_bls()
    download_google_trends()
    log.info("=== acquisition complete; status log: ===")
    status = (C.DATA_RAW / "_download_status.log")
    if status.exists():
        print(status.read_text())


if __name__ == "__main__":
    main()
