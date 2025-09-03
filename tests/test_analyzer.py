# tests/test_analyzer.py
import datetime as dt
import math
import pytest

from weather import analyzer as wan

def test_compute_range_stats(normalized_readings):
    # temps: [1.0, 2.5, -0.5]
    avg, tmin, tmax, count = wan.compute_range_stats(normalized_readings)
    assert count == 3
    assert math.isclose(avg, (1.0 + 2.5 - 0.5) / 3, rel_tol=1e-9)
    assert tmin == -0.5
    assert tmax == 2.5

def test_compute_daily_stats_grouping(normalized_readings):
    daily = wan.compute_daily_stats(normalized_readings)
    # Expect two dates: 2024-01-01 (two readings), 2024-01-02 (one reading)
    # Convert to dict for easy asserts
    by_date = {d["date"]: d for d in daily}

    d1 = by_date[dt.date(2024, 1, 1)]
    assert d1["count"] == 2
    assert math.isclose(d1["avg_temp_c"], (1.0 + 2.5) / 2, rel_tol=1e-9)
    assert d1["min_temp_c"] == 1.0
    assert d1["max_temp_c"] == 2.5

    d2 = by_date[dt.date(2024, 1, 2)]
    assert d2["count"] == 1
    assert d2["avg_temp_c"] == -0.5
    assert d2["min_temp_c"] == -0.5
    assert d2["max_temp_c"] == -0.5

def test_analyzer_ignores_none_temps():
    readings = [
        {"time": dt.datetime(2024, 1, 1, 0), "temp_c": None},
        {"time": dt.datetime(2024, 1, 1, 1), "temp_c": 2.0},
        {"time": dt.datetime(2024, 1, 1, 2), "temp_c": None},
    ]
    avg, tmin, tmax, count = wan.compute_range_stats(readings)
    assert count == 1
    assert avg == 2.0 and tmin == 2.0 and tmax == 2.0

def test_weekly_high_low(normalized_readings):
    # Extend to 7 days for the “week” notion; we’ll duplicate pattern with shifts
    base = normalized_readings
    extended = []
    for i in range(7):
        for r in base:
            extended.append(
                {
                    **r,
                    "time": r["time"] + dt.timedelta(days=i),
                    # vary temps slightly
                    "temp_c": r["temp_c"] + i * 0.1,
                }
            )

    high, low = wan.weekly_high_low(extended)
    assert math.isclose(high, 2.5 + 0.6, rel_tol=1e-9)  # 2.5 + 6*0.1
    assert math.isclose(low, -0.5, rel_tol=1e-9)

