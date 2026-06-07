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
    if "Date" in df.columns:
        df["date"] = pd.to_datetime(df["Date"])
    elif {"Year", "Month"}.issubset(df.columns):
        df["date"] = pd.to_datetime(
            df.assign(DAY=1)[["Year", "Month", "DAY"]]
        )
    else:
        raise ValueError("Temperature CSV does not contain a recognized date column.")

    value_col = next(
        (col for col in ["Mean", "mean", "Value", "value"] if col in df.columns),
        None,
    )
    if value_col is None:
        raise ValueError("Temperature CSV does not contain a recognized value column.")

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
