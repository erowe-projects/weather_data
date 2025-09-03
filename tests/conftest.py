# tests/conftest.py
import datetime as dt
import sqlite3
import pytest

# --- Sample API payloads (Open-Meteo-like hourly structure) ---

@pytest.fixture
def sample_api_json():
    # Two days of hourly data (3 hours total for brevity)
    return {
        "latitude": 40.0,
        "longitude": -86.0,
        "generationtime_ms": 0.123,
        "utc_offset_seconds": 0,
        "timezone": "UTC",
        "timezone_abbreviation": "UTC",
        "hourly": {
            "time": [
                "2024-01-01T00:00",
                "2024-01-01T01:00",
                "2024-01-02T00:00",
            ],
            "temperature_2m": [1.0, 2.5, -0.5],
        },
    }

@pytest.fixture
def empty_api_json():
    return {
        "latitude": 40.0,
        "longitude": -86.0,
        "hourly": {"time": [], "temperature_2m": []},
    }

# --- Normalized readings derived from sample_api_json ---

@pytest.fixture
def normalized_readings():
    # Mirrors the transformation we expect from weather.api.fetch_hourly_weather
    return [
        {
            "time": dt.datetime(2024, 1, 1, 0, 0),
            "temp_c": 1.0,
            "lat": 40.0,
            "lon": -86.0,
            "source": "open-meteo",
        },
        {
            "time": dt.datetime(2024, 1, 1, 1, 0),
            "temp_c": 2.5,
            "lat": 40.0,
            "lon": -86.0,
            "source": "open-meteo",
        },
        {
            "time": dt.datetime(2024, 1, 2, 0, 0),
            "temp_c": -0.5,
            "lat": 40.0,
            "lon": -86.0,
            "source": "open-meteo",
        },
    ]

# --- SQLite fixtures ---

@pytest.fixture
def db_conn():
    # In-memory DB per test; pass connection into weather.db functions
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()

@pytest.fixture
def initialized_db(db_conn):
    # Import here (tests should fail until implementation exists)
    from weather import db as wdb
    wdb.init_db(db_conn)
    return db_conn

@pytest.fixture
def location_id(initialized_db):
    from weather import db as wdb
    return wdb.insert_location(initialized_db, name="Testville", lat=40.0, lon=-86.0)

