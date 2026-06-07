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
    
    if df.empty:
        raise ValueError("Temperature CSV is empty")
    
    # Debug: print original columns and first few rows
    print(f"Temperature CSV original columns: {list(df.columns)}")
    print(f"Temperature CSV shape: {df.shape}")
    print(f"First row: {df.iloc[0].to_dict() if len(df) > 0 else 'empty'}")
    
    # Normalize column names: strip whitespace and convert to lowercase
    df.columns = df.columns.str.strip().str.lower()
    print(f"Temperature CSV normalized columns: {list(df.columns)}")
    
    # Try to find date column
    date_col_name = None
    if "date" in df.columns:
        date_col_name = "date"
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    elif "year" in df.columns and "month" in df.columns:
        date_col_name = "date"
        df["date"] = pd.to_datetime(df.assign(day=1)[["year", "month", "day"]])
    elif "year" in df.columns:
        # Handle year-month strings like '1850-01' or just year
        print(f"Trying to parse 'year' column as date...")
        sample = df["year"].iloc[0] if len(df) > 0 else None
        print(f"Sample year value: {sample} (type: {type(sample)})")
        
        df["date"] = pd.to_datetime(df["year"], format="%Y-%m", errors="coerce")
        non_na_count = df["date"].notna().sum()
        print(f"Parsed {non_na_count}/{len(df)} rows with %Y-%m format")
        
        if df["date"].isna().all():
            # Try just year format
            print("Trying %Y format...")
            df["date"] = pd.to_datetime(df["year"], format="%Y", errors="coerce")
            non_na_count = df["date"].notna().sum()
            print(f"Parsed {non_na_count}/{len(df)} rows with %Y format")
        
        if df["date"].isna().all():
            raise ValueError("Could not parse any dates from 'year' column")
        
        date_col_name = "date"
    
    if date_col_name is None:
        raise ValueError(f"Temperature CSV missing date column. Columns: {list(df.columns)}")

    # Find value column (case-insensitive)
    value_col = None
    for col in ["mean", "value", "anomaly", "temp", "temperature"]:
        if col in df.columns:
            value_col = col
            break
    
    if value_col is None:
        raise ValueError(f"Temperature CSV missing value column. Columns: {list(df.columns)}")

    # Keep only valid rows
    cleaned = df[["date", value_col]].dropna()
    cleaned = cleaned.rename(columns={value_col: "temperature_anomaly"})
    cleaned = cleaned.sort_values("date").reset_index(drop=True)
    
    if len(cleaned) == 0:
        raise ValueError("No valid temperature records after parsing")
    
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
