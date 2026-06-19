.PHONY: all install download clean features trends econ forecast segment report fresh

all: download clean features trends econ forecast segment report

install:
	pip install -r requirements.txt

download:    ; python src/01_download_data.py
clean:       ; python src/02_clean_data.py
features:    ; python src/03_create_features.py
trends:      ; python src/04_trend_analysis.py
econ:        ; python src/05_econometric_models.py
forecast:    ; python src/06_forecasts.py
segment:     ; python src/07_segmentation.py
report:      ; python src/08_generate_report.py

# Re-run everything from cleaning onward (assumes data/raw already populated)
fresh: clean features trends econ forecast segment report
