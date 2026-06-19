"""
config.py — shared configuration, paths, constants, and helpers.

Central place for: project paths, the analysis window, NAICS/PSC technology
taxonomies, FRED series IDs, Google Trends terms, and a resilient HTTP helper
with retry/backoff + on-disk caching so every pull is reproducible and auditable.

No data is downloaded on import. API keys are read from environment / .env only.
"""
from __future__ import annotations

import json
import logging
import os
import time
import hashlib
from pathlib import Path
from typing import Any, Optional

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_INTERIM = ROOT / "data" / "interim"
DATA_PROCESSED = ROOT / "data" / "processed"
OUT_CHARTS = ROOT / "outputs" / "charts"
OUT_TABLES = ROOT / "outputs" / "tables"
OUT_REPORT = ROOT / "outputs" / "report"

for _p in (DATA_RAW, DATA_INTERIM, DATA_PROCESSED, OUT_CHARTS, OUT_TABLES, OUT_REPORT):
    _p.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------- #
# Analysis window  (federal FISCAL years: Oct 1 (Y-1) .. Sep 30 (Y))
# --------------------------------------------------------------------------- #
FY_START = 2015
FY_END = 2024           # last fully-closed fiscal year as of the study
FISCAL_YEARS = list(range(FY_START, FY_END + 1))
BASE_FY = FY_START      # index normalization base for proxies/composite
REAL_DOLLAR_BASE_FY = FY_END   # constant-dollar reference year

# --------------------------------------------------------------------------- #
# Technology taxonomy for the "tech-entry" proxy (P4)
#   NAICS: IT / cyber / cloud / software / data
#   PSC:   D (IT & Telecom services) family + R425 etc.
#   These are intentionally explicit so reviewers can challenge them.
# --------------------------------------------------------------------------- #
TECH_NAICS = {
    "541511": "Custom Computer Programming Services",
    "541512": "Computer Systems Design Services",
    "541513": "Computer Facilities Management Services",
    "541519": "Other Computer Related Services (incl. cyber)",
    "518210": "Data Processing, Hosting & Related (cloud)",
    "513210": "Software Publishers",
    "541715": "R&D in Physical/Eng/Life Sciences (incl. AI R&D)",
}
# PSC: the 'D' product-service-code family = IT and Telecom
TECH_PSC_PREFIXES = ("D",)   # DA-DZ IT & Telecom services
TECH_KEYWORDS = ("cyber", "cloud", "artificial intelligence", "machine learning",
                 "software", "data analytics", "automation", "zero trust")

# Contract-vehicle / IDV types that signal procurement complexity (P2)
IDV_TYPES = {  # USAspending idv_type / type codes
    "IDIQ": "Indefinite Delivery / Indefinite Quantity",
    "GWAC": "Governmentwide Acquisition Contract",
    "BPA": "Blanket Purchase Agreement",
    "FSS": "Federal Supply Schedule",
    "BOA": "Basic Ordering Agreement",
}
# Contract award type codes (USAspending): A/B/C/D = procurement contracts
CONTRACT_AWARD_TYPE_CODES = ["A", "B", "C", "D"]
# IDV award type codes (vehicles + task/delivery orders live here)
IDV_AWARD_TYPE_CODES = ["IDV_A", "IDV_B", "IDV_B_A", "IDV_B_B", "IDV_B_C",
                        "IDV_C", "IDV_D", "IDV_E"]

# --------------------------------------------------------------------------- #
# FRED series (macro controls + deflator)
# --------------------------------------------------------------------------- #
FRED_SERIES = {
    "GDPDEF": "GDP implicit price deflator (real-dollar conversion)",
    "GDP": "Nominal Gross Domestic Product",
    "FGEXPND": "Federal Government current expenditures",
}

# --------------------------------------------------------------------------- #
# Google Trends terms (P3 search-interest proxy)
# --------------------------------------------------------------------------- #
TRENDS_TERMS = [
    "GovCon consultant",
    "capture consultant",
    "proposal consultant",
    "government contracting consultant",
    "federal business development consultant",
    "fractional BD",
]

# --------------------------------------------------------------------------- #
# API endpoints
# --------------------------------------------------------------------------- #
USA_BASE = "https://api.usaspending.gov/api/v2"
FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
CENSUS_BDS = "https://api.census.gov/data/timeseries/bds"
BLS_BASE = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

# --------------------------------------------------------------------------- #
# API keys (never hard-coded; loaded from env / .env)
# --------------------------------------------------------------------------- #
def _load_dotenv() -> None:
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


_load_dotenv()
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")
CENSUS_API_KEY = os.environ.get("CENSUS_API_KEY", "")
BLS_API_KEY = os.environ.get("BLS_API_KEY", "")

# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter(
            "%(asctime)s  %(levelname)-7s  %(name)s  %(message)s",
            datefmt="%H:%M:%S"))
        logger.addHandler(h)
        logger.setLevel(logging.INFO)
    return logger


log = get_logger("config")

# --------------------------------------------------------------------------- #
# Resilient HTTP with retry/backoff + on-disk JSON cache
# --------------------------------------------------------------------------- #
def _cache_key(method: str, url: str, payload: Optional[dict]) -> str:
    raw = f"{method}|{url}|{json.dumps(payload, sort_keys=True) if payload else ''}"
    return hashlib.sha1(raw.encode()).hexdigest()[:16]


def http_json(
    url: str,
    method: str = "GET",
    payload: Optional[dict] = None,
    params: Optional[dict] = None,
    *,
    max_retries: int = 4,
    timeout: int = 60,
    cache: bool = True,
    cache_name: Optional[str] = None,
) -> Optional[Any]:
    """GET/POST returning parsed JSON, with exponential backoff and caching.

    Returns the parsed JSON, or None on persistent failure (caller logs/handles).
    Caches successful responses under data/raw/_cache/ keyed by request.
    """
    import requests  # imported lazily so config import never requires network libs

    cache_dir = DATA_RAW / "_cache"
    cache_dir.mkdir(exist_ok=True)
    key = cache_name or _cache_key(method, url, payload or params)
    cache_file = cache_dir / f"{key}.json"

    if cache and cache_file.exists():
        try:
            return json.loads(cache_file.read_text())
        except json.JSONDecodeError:
            pass  # corrupt cache; refetch

    last_err = None
    for attempt in range(max_retries):
        try:
            if method.upper() == "POST":
                r = requests.post(url, json=payload, params=params, timeout=timeout,
                                  headers={"Content-Type": "application/json"})
            else:
                r = requests.get(url, params=params, timeout=timeout)
            if r.status_code == 429:  # rate limited
                wait = 2 ** (attempt + 1)
                log.warning("429 rate-limited on %s; sleeping %ds", url, wait)
                time.sleep(wait)
                continue
            r.raise_for_status()
            data = r.json()
            if cache:
                cache_file.write_text(json.dumps(data))
            return data
        except Exception as e:  # noqa: BLE001 — we want to retry on any transient error
            last_err = e
            wait = 2 ** attempt
            log.warning("attempt %d/%d failed for %s: %s (retry in %ds)",
                       attempt + 1, max_retries, url, str(e)[:160], wait)
            time.sleep(wait)
    log.error("PERSISTENT FAILURE for %s: %s", url, str(last_err)[:200])
    return None


def write_status(source: str, status: str, detail: str = "") -> None:
    """Append a one-line acquisition status to data/raw/_download_status.log."""
    f = DATA_RAW / "_download_status.log"
    with f.open("a") as fh:
        fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}\t{source}\t{status}\t{detail}\n")
