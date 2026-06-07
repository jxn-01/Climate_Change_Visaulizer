import pathlib
import sys
import pandas as pd
import streamlit as st

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import scripts.fetch_data as fetch_data
import scripts.clean_data as clean_data
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_FILES = [
    PROCESSED_DIR / "temperature_monthly.parquet",
    PROCESSED_DIR / "owid_co2.parquet",
    PROCESSED_DIR / "sea_level.parquet",
]


def data_is_ready() -> bool:
    return all(path.exists() for path in PROCESSED_FILES)


def prepare_data() -> bool:
    try:
        fetch_data.main()
        clean_data.main()
        return data_is_ready()
    except Exception as exc:
        st.error(f"Failed to fetch or process data: {exc}")
        return False


def load_data() -> dict:
    data = {}
    temp_path = PROCESSED_DIR / "temperature_monthly.parquet"
    co2_path = PROCESSED_DIR / "owid_co2.parquet"
    sea_path = PROCESSED_DIR / "sea_level.parquet"

    if temp_path.exists():
        temp = pd.read_parquet(temp_path)
        temp["date"] = pd.to_datetime(temp["date"])
        data["temp"] = temp

    if co2_path.exists():
        co2 = pd.read_parquet(co2_path)
        data["co2"] = co2

    if sea_path.exists():
        sea = pd.read_parquet(sea_path)
        data["sea"] = sea

    return data


def get_year_range(data: dict) -> tuple[int, int]:
    years = []
    if "temp" in data and not data["temp"].empty:
        years.extend(data["temp"]["date"].dt.year.dropna().astype(int).tolist())
    if "co2" in data and "year" in data["co2"].columns:
        years.extend(data["co2"]["year"].dropna().astype(int).tolist())
    if "sea" in data and "year" in data["sea"].columns:
        years.extend(data["sea"]["year"].dropna().astype(int).tolist())

    if not years:
        return 1900, 2100

    return min(years), max(years)


def get_co2_countries(data: dict) -> list[str]:
    if "co2" not in data or data["co2"].empty:
        return []
    return sorted(data["co2"]["country"].dropna().unique().tolist())


def filter_data(data: dict, start_year: int, end_year: int) -> dict:
    filtered = {}
    if "temp" in data:
        temp = data["temp"]
        filtered["temp"] = temp if temp.empty else temp[(temp["date"].dt.year >= start_year) & (temp["date"].dt.year <= end_year)]
    if "co2" in data:
        co2 = data["co2"]
        filtered["co2"] = co2[(co2["year"] >= start_year) & (co2["year"] <= end_year)]
    if "sea" in data:
        sea = data["sea"]
        filtered["sea"] = sea[(sea["year"] >= start_year) & (sea["year"] <= end_year)]
    return filtered


def render_summary_cards(data: dict) -> None:
    temp_value = None
    co2_value = None
    sea_value = None

    if "temp" in data and not data["temp"].empty:
        temp_value = data["temp"]["temperature_anomaly"].iloc[-1]
    if "co2" in data and not data["co2"].empty:
        world = data["co2"][data["co2"]["country"] == "World"]
        if not world.empty and "co2" in world.columns:
            co2_value = world["co2"].iloc[-1]
    if "sea" in data and not data["sea"].empty:
        sea_value = data["sea"]["sea_level_mm"].iloc[-1]

    cols = st.columns(3)
    cols[0].metric("Latest temp anomaly", f"{temp_value:.2f} °C" if temp_value is not None else "N/A")
    cols[1].metric("Latest CO2 emissions", f"{co2_value:,.0f} Mt" if co2_value is not None else "N/A")
    cols[2].metric("Latest sea level", f"{sea_value:,.0f} mm" if sea_value is not None else "N/A")


def render_data_overview(data: dict, selected_co2_country: str | None) -> None:
    temp_count = len(data.get("temp", [])) if "temp" in data else 0
    co2_count = len(data.get("co2", [])) if "co2" in data else 0
    sea_count = len(data.get("sea", [])) if "sea" in data else 0

    st.markdown(
        f"**Data overview:** {temp_count} temperature rows, {co2_count} CO2 rows, {sea_count} sea level rows."
    )
    if selected_co2_country and "co2" in data:
        country_rows = len(data["co2"][data["co2"]["country"] == selected_co2_country])
        st.markdown(f"**Selected CO2 country:** {selected_co2_country} ({country_rows} rows)")


def main():
    st.set_page_config(page_title="Climate Change Visualizer", layout="wide")
    st.title("Climate Change Visualizer")
    st.markdown(
        "This demo loads processed climate data and renders interactive trend charts. "
        "Run `python scripts/fetch_data.py` and `python scripts/clean_data.py` first."
    )

    data = load_data()
    if not data:
        st.warning("Processed climate data is missing.")
        if st.button("Download and process data"):
            with st.spinner("Fetching and cleaning data..."):
                if prepare_data():
                    st.success("Data downloaded and processed successfully. Reloading...")
                    st.experimental_rerun()
                else:
                    st.error("Unable to prepare data. Check logs and network access.")
        else:
            st.info("If you have already run the pipeline locally, commit `data/processed/` to the repo or use the button above.")
        return

    st.sidebar.header("Filters")
    dataset_options = [
        "Temperature anomaly",
        "CO2 emissions",
        "Sea level"
    ]
    selected_datasets = st.sidebar.multiselect(
        "Select datasets to display",
        dataset_options,
        default=dataset_options,
    )

    min_year, max_year = get_year_range(data)
    year_range = st.sidebar.slider(
        "Select year range",
        min_value=int(min_year),
        max_value=int(max_year),
        value=(int(min_year), int(max_year)),
        step=1,
    )

    selected_co2_country = None
    if "co2" in data:
        countries = get_co2_countries(data)
        if countries:
            default_index = countries.index("World") if "World" in countries else 0
            selected_co2_country = st.sidebar.selectbox(
                "Select CO2 country",
                countries,
                index=default_index,
            )

    filtered = filter_data(data, year_range[0], year_range[1])

    st.sidebar.markdown("---")
    st.sidebar.write("Loaded files from `data/processed/`. Use the slider to focus on a time window.")

    render_summary_cards(filtered)
    render_data_overview(filtered, selected_co2_country)

    if "Temperature anomaly" in selected_datasets:
        if "temp" in filtered and not filtered["temp"].empty:
            st.subheader("Global Temperature Anomaly")
            temp = filtered["temp"].set_index("date")
            st.line_chart(temp["temperature_anomaly"])
        else:
            st.warning("No temperature data available for the selected year range.")

    if "CO2 emissions" in selected_datasets:
        if "co2" in filtered and not filtered["co2"].empty:
            if selected_co2_country:
                st.subheader(f"CO2 Emissions / CO2 per Capita — {selected_co2_country}")
                country_df = filtered["co2"][filtered["co2"]["country"] == selected_co2_country]
                if not country_df.empty:
                    cols = [col for col in ["co2", "co2_per_capita"] if col in country_df.columns]
                    st.line_chart(country_df.set_index("year")[cols])
                else:
                    st.warning(f"No CO2 rows found for {selected_co2_country} in the selected year range.")
            else:
                st.subheader("World CO2 Emissions / CO2 per Capita")
                world = filtered["co2"][filtered["co2"]["country"] == "World"]
                if not world.empty:
                    cols = [col for col in ["co2", "co2_per_capita"] if col in world.columns]
                    st.line_chart(world.set_index("year")[cols])
                else:
                    st.warning("World-level CO2 rows not found in the dataset.")
        else:
            st.warning("No CO2 data available for the selected year range.")

    if "Sea level" in selected_datasets:
        if "sea" in filtered and not filtered["sea"].empty:
            st.subheader("Sea Level")
            st.line_chart(filtered["sea"].set_index("year")["sea_level_mm"])
        else:
            st.warning("No sea level data available for the selected year range.")


if __name__ == "__main__":
    main()
