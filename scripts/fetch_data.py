import os
import requests
from pathlib import Path

DATA_FILES = {
    "temperature_monthly": {
        "url": "https://raw.githubusercontent.com/datasets/global-temp/master/data/monthly.csv",
        "filename": "temperature_monthly.csv",
    },
    "co2_owid": {
        "url": "https://github.com/owid/co2-data/raw/master/owid-co2-data.csv",
        "filename": "owid-co2-data.csv",
    },
    "sea_level": {
        "url": "https://raw.githubusercontent.com/datasets/sea-level-rise/master/data/epa-sea-level.csv",
        "filename": "epa-sea-level.csv",
    },
}

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def download_file(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url} -> {path}")
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    with open(path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print(f"Saved {path} ({path.stat().st_size} bytes)")


def main() -> None:
    for name, info in DATA_FILES.items():
        target_path = RAW_DIR / info["filename"]
        try:
            download_file(info["url"], target_path)
        except Exception as exc:
            print(f"Failed to download {name}: {exc}")


if __name__ == "__main__":
    main()
