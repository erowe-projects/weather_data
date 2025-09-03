import datetime as dt
import pytest
from unittest.mock import patch, MagicMock, ANY

from weather.ui_core import (
    add_location_and_fetch_weather,
    get_daily_summary,
    get_weekly_high_low,
    conn,
)

# -----------------------------
# Test: add_location_and_fetch_weather
# -----------------------------

@patch("weather.ui_core.insert_location")
@patch("weather.ui_core.fetch_hourly_weather")
@patch("weather.ui_core.upsert_weather_readings")
def test_add_location_success(mock_upsert, mock_fetch, mock_insert):
    # Arrange
    mock_insert.return_value = 1
    mock_fetch.return_value = [
        {"time": dt.datetime.now(), "temp_c": 20, "lat": 0, "lon": 0, "source": "test"}
    ]
    mock_upsert.return_value = 1

    # Act
    result = add_location_and_fetch_weather("TestCity", 0, 0, "2025-01-01", "2025-01-02")

    # Assert
    assert "Inserted 1 readings" in result
    mock_insert.assert_called_once_with(ANY, "TestCity", 0, 0)
    mock_fetch.assert_called_once()
    mock_upsert.assert_called_once()


@patch("weather.ui_core.insert_location", side_effect=Exception("DB fail"))
def test_add_location_failure(mock_insert):
    result = add_location_and_fetch_weather("TestCity", 0, 0, "2025-01-01", "2025-01-02")
    assert "Error: DB fail" in result


def test_add_location_invalid_date():
    result = add_location_and_fetch_weather("TestCity", 0, 0, "invalid-date", "2025-01-02")
    assert "Invalid date format" in result


# -----------------------------
# Test: get_daily_summary
# -----------------------------

@patch("weather.ui_core.fetch_readings")
def test_get_daily_summary_success(mock_fetch):
    mock_fetch.return_value = [
        {"time": dt.datetime(2025, 1, 1, 0, 0), "temp_c": 20},
        {"time": dt.datetime(2025, 1, 1, 1, 0), "temp_c": 22},
    ]
    # Patch DB call
    with patch("weather.ui_core.conn") as mock_conn:
        mock_conn.execute.return_value.fetchone.return_value = {"id": 1}
        result = get_daily_summary("TestCity", "2025-01-01", "2025-01-02")

    assert isinstance(result, list)
    assert all("avg_temp_c" in d for d in result)
    assert result[0]["avg_temp_c"] == 21.0


def test_get_daily_summary_invalid_date():
    result = get_daily_summary("TestCity", "bad-date", "2025-01-02")
    assert "error" in result[0]


def test_get_daily_summary_location_not_found():
    with patch("weather.ui_core.conn") as mock_conn:
        mock_conn.execute.return_value.fetchone.return_value = None
        result = get_daily_summary("MissingCity", "2025-01-01", "2025-01-02")
    assert "error" in result[0]


# -----------------------------
# Test: get_weekly_high_low
# -----------------------------

@patch("weather.ui_core.fetch_readings")
def test_get_weekly_high_low_success(mock_fetch):
    mock_fetch.return_value = [
        {"time": dt.datetime(2025, 1, 1), "temp_c": 20},
        {"time": dt.datetime(2025, 1, 2), "temp_c": 30},
    ]
    with patch("weather.ui_core.conn") as mock_conn:
        mock_conn.execute.return_value.fetchone.return_value = {"id": 1}
        result = get_weekly_high_low("TestCity", "2025-01-01", "2025-01-07")

    assert "Weekly High: 30" in result and "Low: 20" in result


def test_get_weekly_high_low_invalid_date():
    result = get_weekly_high_low("TestCity", "bad-date", "2025-01-07")
    assert "Invalid date format" in result


def test_get_weekly_high_low_location_not_found():
    with patch("weather.ui_core.conn") as mock_conn:
        mock_conn.execute.return_value.fetchone.return_value = None
        result = get_weekly_high_low("MissingCity", "2025-01-01", "2025-01-07")
    assert "not found" in result


# -----------------------------
# Test: plotting / visualization (to be added in UI)
# -----------------------------

@patch("weather.ui_core.compute_daily_stats")
def test_plotting_daily_stats(mock_compute):
    # Simulate daily stats for plotting
    mock_compute.return_value = [
        {"date": dt.date(2025, 1, 1), "avg_temp_c": 21, "min_temp_c": 20, "max_temp_c": 22, "count": 2},
        {"date": dt.date(2025, 1, 2), "avg_temp_c": 25, "min_temp_c": 23, "max_temp_c": 27, "count": 3},
    ]
    # We'll assume a function `plot_daily_stats(stats)` will exist
    from weather.plots import plot_daily_stats  # placeholder
    fig = plot_daily_stats(mock_compute.return_value)
    assert fig is not None  # returns a plotly/matplotlib figure object
