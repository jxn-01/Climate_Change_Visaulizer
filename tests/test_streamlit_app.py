import pandas as pd

from app import streamlit_app as app


def test_get_year_range_with_data():
    data = {
        "temp": pd.DataFrame({"date": pd.to_datetime(["2000-01-01", "2010-01-01"]), "temperature_anomaly": [0.1, 0.2]}),
        "co2": pd.DataFrame({"year": [1990, 2005]}),
        "sea": pd.DataFrame({"year": [1985, 2020]}),
    }

    assert app.get_year_range(data) == (1985, 2020)


def test_get_year_range_empty():
    assert app.get_year_range({}) == (1900, 2100)


def test_get_co2_countries_returns_sorted_list():
    data = {
        "co2": pd.DataFrame({"country": ["Brazil", "World", "China", None]})
    }

    assert app.get_co2_countries(data) == ["Brazil", "China", "World"]


def test_filter_data_limits_by_year():
    data = {
        "temp": pd.DataFrame({"date": pd.to_datetime(["2000-01-01", "2010-01-01"]), "temperature_anomaly": [0.1, 0.2]}),
        "co2": pd.DataFrame({"year": [2000, 2010], "country": ["World", "World"], "co2": [30000, 32000]}),
        "sea": pd.DataFrame({"year": [2000, 2010], "sea_level_mm": [10, 12]}),
    }

    filtered = app.filter_data(data, 2005, 2015)
    assert len(filtered["temp"]) == 1
    assert filtered["temp"]["temperature_anomaly"].iloc[0] == 0.2
    assert len(filtered["co2"]) == 1
    assert filtered["co2"]["year"].iloc[0] == 2010
    assert len(filtered["sea"]) == 1
    assert filtered["sea"]["year"].iloc[0] == 2010


def test_render_summary_cards(monkeypatch):
    class DummyColumn:
        def __init__(self):
            self.calls = []

        def metric(self, label, value):
            self.calls.append((label, value))

    cols = [DummyColumn() for _ in range(3)]
    monkeypatch.setattr(app.st, "columns", lambda count: cols)

    data = {
        "temp": pd.DataFrame({"date": pd.to_datetime(["2020-01-01"]), "temperature_anomaly": [0.5]}),
        "co2": pd.DataFrame({"country": ["World"], "year": [2020], "co2": [36000], "co2_per_capita": [4.5]}),
        "sea": pd.DataFrame({"year": [2020], "sea_level_mm": [80]}),
    }

    app.render_summary_cards(data)

    assert cols[0].calls[0][0] == "Latest temp anomaly"
    assert "0.50" in cols[0].calls[0][1]
    assert cols[1].calls[0][0] == "Latest CO2 emissions"
    assert "36,000" in cols[1].calls[0][1]
    assert cols[2].calls[0][0] == "Latest sea level"
    assert "80" in cols[2].calls[0][1]
