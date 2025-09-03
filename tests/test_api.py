# tests/test_api.py
import datetime as dt
import numpy as np
import pytest
from unittest.mock import Mock

from weather import api as wapi

class MockHourly:
    def __init__(self, times, temps):
        self._times = times
        self._temps = temps

    def Time(self):
        return self._times[0] if self._times else 0

    def TimeEnd(self):
        return self._times[-1] + 3600 if self._times else 0

    def Interval(self):
        return 3600

    def Variables(self, index):
        return Mock(ValuesAsNumpy=lambda: np.array(self._temps))

class MockResponse:
    def __init__(self, lat, lon, times, temps):
        self._lat = lat
        self._lon = lon
        self._times = times
        self._temps = temps

    def Latitude(self):
        return self._lat

    def Longitude(self):
        return self._lon

    def Elevation(self):
        return 100

    def UtcOffsetSeconds(self):
        return 0

    def Hourly(self):
        return MockHourly(self._times, self._temps)

def test_fetch_hourly_weather_normalizes_response(monkeypatch, sample_api_json):
    # Mock openmeteo.weather_api
    times = [dt.datetime(2024, 1, 1, 0, 0).timestamp(), dt.datetime(2024, 1, 1, 1, 0).timestamp(), dt.datetime(2024, 1, 2, 0, 0).timestamp()]
    temps = [1.0, 2.5, -0.5]
    mock_response = MockResponse(40.0, -86.0, times, temps)
    mock_openmeteo = Mock()
    mock_openmeteo.weather_api.return_value = [mock_response]

    monkeypatch.setattr(wapi, "openmeteo", mock_openmeteo)

    start = dt.date(2024, 1, 1)
    end = dt.date(2024, 1, 2)

    readings = wapi.fetch_hourly_weather(
        lat=40.0, lon=-86.0, start_date=start, end_date=end
    )

    # Expect a list of normalized dicts
    assert isinstance(readings, list)
    assert len(readings) == 3

    r0 = readings[0]
    assert set(r0.keys()) == {"time", "temp_c", "lat", "lon", "source"}
    assert isinstance(r0["time"], dt.datetime)
    assert isinstance(r0["temp_c"], (int, float))
    assert r0["lat"] == 40.0
    assert r0["lon"] == -86.0
    assert r0["source"] == "open-meteo"

def test_fetch_hourly_weather_handles_http_error(monkeypatch):
    mock_openmeteo = Mock()
    mock_openmeteo.weather_api.side_effect = Exception("API error")

    monkeypatch.setattr(wapi, "openmeteo", mock_openmeteo)

    with pytest.raises(wapi.WeatherAPIError):
        wapi.fetch_hourly_weather(40.0, -86.0, dt.date(2024, 1, 1), dt.date(2024, 1, 2))

def test_fetch_hourly_weather_validates_date_range(monkeypatch):
    # Even if network is fine, invalid date range should raise before calling the API
    start = dt.date(2024, 1, 2)
    end = dt.date(2024, 1, 1)
    with pytest.raises(ValueError):
        wapi.fetch_hourly_weather(40.0, -86.0, start, end)

def test_fetch_hourly_weather_empty_data(monkeypatch):
    # Mock empty data
    mock_response = MockResponse(40.0, -86.0, [], [])
    mock_openmeteo = Mock()
    mock_openmeteo.weather_api.return_value = [mock_response]

    monkeypatch.setattr(wapi, "openmeteo", mock_openmeteo)

    readings = wapi.fetch_hourly_weather(
        lat=40.0, lon=-86.0, start_date=dt.date(2024, 1, 1), end_date=dt.date(2024, 1, 2)
    )
    assert readings == []  # explicit empty list is fine/expected
