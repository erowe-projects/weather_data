import pytest
from plotly.graph_objects import Figure
from datetime import date

from weather.plots import plot_daily_stats, plot_weekly_high_low


# -----------------------------
# Test: plot_daily_stats
# -----------------------------
def test_plot_daily_stats_normal():
    daily_stats = [
        {"date": date(2025, 1, 1), "avg_temp_c": 20, "min_temp_c": 18, "max_temp_c": 22, "count": 3},
        {"date": date(2025, 1, 2), "avg_temp_c": 25, "min_temp_c": 23, "max_temp_c": 27, "count": 2},
    ]
    fig = plot_daily_stats(daily_stats)
    assert isinstance(fig, Figure)
    # Should have 3 traces: avg, min, max
    assert len(fig.data) == 3
    # Check trace names
    trace_names = [t.name for t in fig.data]
    assert set(trace_names) == {"Avg Temp", "Min Temp", "Max Temp"}


def test_plot_daily_stats_empty():
    fig = plot_daily_stats([])
    assert isinstance(fig, Figure)
    # No traces should exist
    assert len(fig.data) == 0


def test_plot_daily_stats_invalid_data():
    # Test with dicts missing required keys (like error dicts from get_daily_summary)
    invalid_stats = [
        {"error": "Invalid date format"},
        {"error": "Location not found"},
        {"date": date(2025, 1, 1)},  # Missing temp keys
        {"avg_temp_c": 20},  # Missing date and other keys
    ]
    fig = plot_daily_stats(invalid_stats)
    assert isinstance(fig, Figure)
    # Should have no traces since no valid data
    assert len(fig.data) == 0


def test_plot_daily_stats_mixed_valid_invalid():
    # Test with mix of valid and invalid data
    mixed_stats = [
        {"error": "Some error"},
        {"date": date(2025, 1, 1), "avg_temp_c": 20, "min_temp_c": 18, "max_temp_c": 22, "count": 3},
        {"error": "Another error"},
        {"date": date(2025, 1, 2), "avg_temp_c": 25, "min_temp_c": 23, "max_temp_c": 27, "count": 2},
    ]
    fig = plot_daily_stats(mixed_stats)
    assert isinstance(fig, Figure)
    # Should have 3 traces for the 2 valid entries
    assert len(fig.data) == 3
    # Check that only valid dates are plotted
    assert len(fig.data[0].x) == 2  # 2 valid dates


# -----------------------------
# Test: plot_weekly_high_low
# -----------------------------
def test_plot_weekly_high_low_normal():
    fig = plot_weekly_high_low(30, 15)
    assert isinstance(fig, Figure)
    # One trace: bar chart
    assert len(fig.data) == 1
    assert fig.data[0].type == "bar"
    # Check labels
    assert list(fig.data[0].x) == ["High", "Low"]
    assert list(fig.data[0].y) == [30, 15]


def test_plot_weekly_high_low_none_values():
    fig = plot_weekly_high_low(None, None)
    assert isinstance(fig, Figure)
    # No traces should exist
    assert len(fig.data) == 0
