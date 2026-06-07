# Climate Change Visualizer

A starter Python project for climate data analysis and visualization.

## What it includes

- `scripts/fetch_data.py`: downloads MVP climate data sources to `data/raw/`
- `scripts/clean_data.py`: normalizes raw CSVs and writes processed Parquet files to `data/processed/`
- `app/streamlit_app.py`: a minimal Streamlit app to preview processed data

## Data sources

- global temperature: `datasets/global-temp` monthly CSV
- atmospheric CO2: Our World in Data `owid-co2-data.csv`
- sea level: EPA sea-level dataset

## Features

- interactive Streamlit dashboard with year-range filtering and CO2 country selection
- static plot generation via `scripts/plot_static.py`
- analysis notebook with summary metrics and CO2/temperature correlation
- pytest coverage for download, cleaning, and dashboard helper logic

## Setup

1. Create and activate a Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Download raw data

```powershell
python scripts\fetch_data.py
```

3. Clean and process the raw files

```powershell
python scripts\clean_data.py
```

4. Run the demo app

```powershell
streamlit run app\streamlit_app.py
```

5. Generate static plots

```powershell
python scripts\plot_static.py
```

6. Open the analysis notebook

- Open `notebooks/analysis.ipynb` in Jupyter or VS Code

5. If the app does not find processed data, use the in-app button to download and process it automatically.

6. Run tests

```powershell
pip install -r requirements-dev.txt
pytest
```

## Deployment

- Streamlit Cloud: push this repo to GitHub, then create a new Streamlit app using `app/streamlit_app.py`.
- Heroku or other container hosts: use the included `Procfile` and `runtime.txt`.

## Project flow

- `fetch_data.py` downloads raw CSV files and saves them under `data/raw/`
- `clean_data.py` loads the raw files, normalizes dates and column names, and writes cleaned Parquet files for fast analysis
- `app/streamlit_app.py` loads processed data and renders simple charts for quick exploration
