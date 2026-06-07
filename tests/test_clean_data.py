import pandas as pd
import pytest

import scripts.clean_data as clean_data


@pytest.fixture(autouse=True)
def temp_dirs(tmp_path, monkeypatch):
    raw_dir = tmp_path / "data" / "raw"
    processed_dir = tmp_path / "data" / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(clean_data, "RAW_DIR", raw_dir)
    monkeypatch.setattr(clean_data, "PROCESSED_DIR", processed_dir)
    return raw_dir, processed_dir


def test_clean_temperature_writes_parquet(temp_dirs):
    raw_dir, processed_dir = temp_dirs
    raw_dir.mkdir(parents=True, exist_ok=True)
    temperature_csv = raw_dir / "temperature_monthly.csv"
    temperature_csv.write_text("Date,Mean\n2020-01-01,0.50\n2020-02-01,0.60\n", encoding="utf-8")

    clean_data.clean_temperature()

    output = processed_dir / "temperature_monthly.parquet"
    assert output.exists()
    df = pd.read_parquet(output)
    assert list(df.columns) == ["date", "temperature_anomaly"]
    assert len(df) == 2
    assert df.iloc[0]["temperature_anomaly"] == 0.50


def test_clean_co2_writes_parquet(temp_dirs):
    raw_dir, processed_dir = temp_dirs
    raw_dir.mkdir(parents=True, exist_ok=True)
    co2_csv = raw_dir / "owid-co2-data.csv"
    co2_csv.write_text(
        "country,year,co2,co2_per_capita,population\nWorld,2019,36000,4.8,7700000000\nWorld,2020,36200,4.7,7800000000\n",
        encoding="utf-8",
    )

    clean_data.clean_co2()

    output = processed_dir / "owid_co2.parquet"
    assert output.exists()
    df = pd.read_parquet(output)
    assert list(df.columns) == ["country", "year", "co2", "co2_per_capita", "population"]
    assert len(df) == 2
    assert df.loc[df["year"] == 2020, "co2"].iloc[0] == 36200


def test_clean_sea_level_writes_parquet(temp_dirs):
    raw_dir, processed_dir = temp_dirs
    raw_dir.mkdir(parents=True, exist_ok=True)
    sea_csv = raw_dir / "epa-sea-level.csv"
    sea_csv.write_text(
        "Year,CSIRO Adjusted Sea Level\n2010,50.1\n2011,51.2\n",
        encoding="utf-8",
    )

    clean_data.clean_sea_level()

    output = processed_dir / "sea_level.parquet"
    assert output.exists()
    df = pd.read_parquet(output)
    assert list(df.columns) == ["year", "sea_level_mm"]
    assert len(df) == 2
    assert df.loc[df["year"] == 2011, "sea_level_mm"].iloc[0] == 51.2
