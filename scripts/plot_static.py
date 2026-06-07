import pathlib
import pandas as pd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "plots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    temperature = pd.read_parquet(PROCESSED_DIR / "temperature_monthly.parquet")
    temperature["date"] = pd.to_datetime(temperature["date"])

    return {
        "temperature": temperature,
        "co2": pd.read_parquet(PROCESSED_DIR / "owid_co2.parquet"),
        "sea_level": pd.read_parquet(PROCESSED_DIR / "sea_level.parquet"),
    }


def save_fig(fig, name: str) -> None:
    out_path = OUTPUT_DIR / name
    fig.savefig(out_path, dpi=150)
    print(f"Wrote {out_path}")


def plot_temperature(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["date"], df["temperature_anomaly"], color="tab:red", linewidth=1)
    ax.set_title("Global Temperature Anomaly")
    ax.set_xlabel("Date")
    ax.set_ylabel("Temperature anomaly (°C)")
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_locator(mdates.YearLocator(10))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.autofmt_xdate()
    fig.tight_layout()
    save_fig(fig, "temperature_anomaly.png")


def plot_co2(df: pd.DataFrame) -> None:
    world = df[df["country"] == "World"].sort_values("year")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(world["year"], world["co2"], marker="o", label="CO2 emissions (Mt)")
    if "co2_per_capita" in world.columns:
        ax.plot(world["year"], world["co2_per_capita"], marker="o", label="CO2 per capita (t)")
    ax.set_title("World CO2 Emissions")
    ax.set_xlabel("Year")
    ax.set_ylabel("CO2 emissions / intensity")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    save_fig(fig, "co2_world.png")


def plot_sea_level(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["year"], df["sea_level_mm"], color="tab:blue", marker="o")
    ax.set_title("Global Sea Level Change")
    ax.set_xlabel("Year")
    ax.set_ylabel("Sea level anomaly (mm)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    save_fig(fig, "sea_level.png")


def plot_combined_trends(temperature: pd.DataFrame, co2: pd.DataFrame) -> None:
    world_co2 = co2[co2["country"] == "World"].sort_values("year")
    annual_temp = (
        temperature.set_index("date")["temperature_anomaly"]
        .resample("Y")
        .mean()
        .rename("temperature_anomaly")
        .reset_index()
    )
    annual_temp["year"] = annual_temp["date"].dt.year
    merged = pd.merge(annual_temp, world_co2[["year", "co2"]], on="year", how="inner")

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(merged["year"], merged["temperature_anomaly"], color="tab:red", marker="o", label="Temperature anomaly")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Temperature anomaly (°C)", color="tab:red")
    ax1.tick_params(axis="y", labelcolor="tab:red")
    ax1.grid(alpha=0.2)

    ax2 = ax1.twinx()
    ax2.plot(merged["year"], merged["co2"], color="tab:green", marker="s", label="CO2 emissions")
    ax2.set_ylabel("CO2 emissions (Mt)", color="tab:green")
    ax2.tick_params(axis="y", labelcolor="tab:green")

    fig.suptitle("Annual temperature anomaly and CO2 emissions")
    fig.tight_layout()
    save_fig(fig, "combined_temperature_co2.png")


def main() -> None:
    data = load_data()
    plot_temperature(data["temperature"])
    plot_co2(data["co2"])
    plot_sea_level(data["sea_level"])
    plot_combined_trends(data["temperature"], data["co2"])


if __name__ == "__main__":
    main()
