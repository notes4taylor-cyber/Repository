#!/usr/bin/env bash
# Run the full pipeline in order. Data-dependent steps degrade gracefully if
# 01 could not reach the APIs (they log what's missing rather than failing hard).
set -u
cd "$(dirname "$0")"
echo ">>> Outsourced GovCon BD pipeline"
for step in 01_download_data 02_clean_data 03_create_features \
            04_trend_analysis 05_econometric_models 06_forecasts \
            07_segmentation 08_generate_report; do
  echo ">>> python src/${step}.py"
  python "src/${step}.py" || echo "!!! ${step} reported an issue (continuing)"
done
echo ">>> Done. Report: outputs/report/outsourced_govcon_bd_market_report.md"
