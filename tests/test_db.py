# tests/test_db.py
import datetime as dt
import sqlite3

import pytest

from weather import db as wdb

def _table_exists(conn, name: str) -> bool:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (name,)
    )
    return cur.fetchone() is not None

def test_init_db_creates_tables(initialized_db):
    assert _table_exists(initialized_db, "locations")
    assert _table_exists(initialized_db, "weather_readings")

def test_insert_and_get_location(initialized_db):
    loc_id = wdb.insert_location(initialized_db, "Testville", 40.0, -86.0)
    assert isinstance(loc_id, int) and loc_id > 0

    row = wdb.get_location_by_name(initialized_db, "Testville")
    assert row is not None
    assert row["id"] == loc_id
    assert row["name"] == "Testville"
    assert row["lat"] == 40.0
    assert row["lon"] == -86.0

def test_upsert_weather_readings_inserts_and_dedupes(initialized_db, location_id, normalized_readings):
    inserted_1 = wdb.upsert_weather_readings(initialized_db, location_id, normalized_readings)
    assert inserted_1 == len(normalized_readings)

    # Insert same readings again -> should dedupe (0 new rows)
    inserted_2 = wdb.upsert_weather_readings(initialized_db, location_id, normalized_readings)
    assert inserted_2 == 0

    # Verify row count in table equals unique timestamps
    cur = initialized_db.execute("SELECT COUNT(*) AS c FROM weather_readings WHERE location_id = ?;", (location_id,))
    count = cur.fetchone()["c"]
    assert count == len(normalized_readings)

def test_fetch_readings_date_range(initialized_db, location_id, normalized_readings):
    # Insert readings across two days
    wdb.upsert_weather_readings(initialized_db, location_id, normalized_readings)

    start = dt.datetime(2024, 1, 1, 0, 30)
    end = dt.datetime(2024, 1, 1, 23, 59)

    rows = wdb.fetch_readings(initialized_db, location_id, start, end)
    # Expect only the 2024-01-01 01:00 record in this range
    assert len(rows) == 1
    r = rows[0]
    assert r["time"] == dt.datetime(2024, 1, 1, 1, 0)
    assert r["temp_c"] == 2.5

    # Verify results are sorted by time asc
    # (Insert another query for the full [1st..2nd day] range)
    rows_full = wdb.fetch_readings(
        initialized_db,
        location_id,
        dt.datetime(2024, 1, 1, 0, 0),
        dt.datetime(2024, 1, 2, 23, 59),
    )
    times = [r["time"] for r in rows_full]
    assert times == sorted(times)


def test_fetch_readings_returns_correct_types(initialized_db, location_id, normalized_readings):
    # Insert readings
    wdb.upsert_weather_readings(initialized_db, location_id, normalized_readings)

    rows = wdb.fetch_readings(
        initialized_db,
        location_id,
        dt.datetime(2024, 1, 1, 0, 0),
        dt.datetime(2024, 1, 2, 23, 59),
    )

    # Verify data types
    for r in rows:
        assert isinstance(r["time"], dt.datetime)
        if r["temp_c"] is not None:
            assert isinstance(r["temp_c"], float)
        assert isinstance(r["temp_c"], (float, type(None)))
