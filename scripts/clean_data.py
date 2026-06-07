import os
from pathlib import Path
import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def clean_temperature():
    raw_path = RAW_DIR / "temperature_monthly.csv"
    if not raw_path.exists():
        raise FileNotFoundError(f"Missing raw temperature file: {raw_path}")

    df = pd.read_csv(raw_path)
    
    # Debug: print columns for troubleshooting
    print(f"Temperature CSV columns: {list(df.columns)}")
    print(f"First row: {df.iloc[0].to_dict() if len(df) > 0 else 'empty'}")
    
    # Normalize column names to lowercase for comparison
    df.columns = df.columns.str.strip().str.lower()
    
    # Try different date column patterns
    date_col = None
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        date_col = "date"
    elif {"year", "month"}.issubset(df.columns):
        df["date"] = pd.to_datetime(df.assign(day=1)[["year", "month", "day"]])
        date_col = "date"
    elif "year" in df.columns:
        # Handle year-month strings like '1850-01' or just year
        df["date"] = pd.to_datetime(df["year"], format="%Y-%m", errors="coerce")
        if df["date"].isna().all():
            # Try just year format
            df["date"] = pd.to_datetime(df["year"], format="%Y", errors="coerce")
        if df["date"].isna().all():
            raise ValueError("Temperature CSV Year values could not be parsed.")
        date_col = "date"
    
    if date_col is None:
        raise ValueError(f"Temperature CSV does not contain a recognized date column. Found: {list(df.columns)}")

    # Identify the value column (case-insensitive)
    value_col = next(
        (col for col in df.columns if col in ["mean", "value", "anomaly"]),
        None,
    )
    if value_col is None:
        raise ValueError(f"Temperature CSV does not contain a recognized value column. Found: {list(df.columns)}")

    cleaned = df[["date", value_col]].rename(columns={value_col: "temperature_anomaly"})
    cleaned = cleaned.sort_values("date").reset_index(drop=True)
    out_path = PROCESSED_DIR / "temperature_monthly.parquet"
    cleaned.to_parquet(out_path)
    print(f"Wrote {out_path} ({len(cleaned)} rows)")


def clean_co2():
    raw_path = RAW_DIR / "owid-co2-data.csv"
    if not raw_path.exists():
        raise FileNotFoundError(f"Missing raw CO2 file: {raw_path}")

    df = pd.read_csv(raw_path)
    if "year" not in df.columns:
        raise ValueError("CO2 CSV must contain a year column.")

    df["year"] = df["year"].astype(int)
    cols = [col for col in ["country", "year", "co2", "co2_per_capita", "population"] if col in df.columns]
    cleaned = df[cols]
    out_path = PROCESSED_DIR / "owid_co2.parquet"
    cleaned.to_parquet(out_path)
    print(f"Wrote {out_path} ({len(cleaned)} rows)")


def clean_sea_level():
    raw_path = RAW_DIR / "epa-sea-level.csv"
    if not raw_path.exists():
        raise FileNotFoundError(f"Missing raw sea level file: {raw_path}")

    df = pd.read_csv(raw_path)
    if "Year" not in df.columns:
        raise ValueError("Sea level CSV must contain a Year column.")

    df["year"] = df["Year"].astype(int)
    sea_cols = [col for col in ["CSIRO Adjusted Sea Level", "Adjusted Sea Level", "Sea Level"] if col in df.columns]
    if not sea_cols:
        raise ValueError("Sea level CSV does not contain a recognized sea-level column.")

    cleaned = df[["year", sea_cols[0]]].rename(columns={sea_cols[0]: "sea_level_mm"})
    cleaned = cleaned.sort_values("year").reset_index(drop=True)
    out_path = PROCESSED_DIR / "sea_level.parquet"
    cleaned.to_parquet(out_path)
    print(f"Wrote {out_path} ({len(cleaned)} rows)")


def main():
    clean_temperature()
    clean_co2()
    clean_sea_level()


if __name__ == "__main__":
    main()
