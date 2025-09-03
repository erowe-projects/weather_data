import datetime as dt
from .api import fetch_hourly_weather, WeatherAPIError
from .db import init_db, insert_location, upsert_weather_readings, fetch_readings
from .analyzer import compute_daily_stats, weekly_high_low
from .logging_config import get_logger
import sqlite3

logger = get_logger(__name__)

DB_PATH = "weather_demo.db"

# -----------------------------
# Database setup
# -----------------------------
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row
init_db(conn)

# -----------------------------
# Core functions for UI
# -----------------------------
def add_location_and_fetch_weather(
    name: str, lat: float, lon: float, start_date: str, end_date: str
) -> str:
    """
    Add a location to DB, fetch weather data, and persist it.
    Returns a summary string for UI.
    """
    try:
        start = dt.date.fromisoformat(start_date)
        end = dt.date.fromisoformat(end_date)
    except ValueError as e:
        return f"Invalid date format: {e}"

    try:
        loc_id = insert_location(conn, name, lat, lon)
        readings = fetch_hourly_weather(lat, lon, start, end)
        inserted = upsert_weather_readings(conn, loc_id, readings)
        return f"Inserted {inserted} readings for {name} from {start} to {end}"
    except WeatherAPIError as e:
        logger.error("Weather API failed: %s", e)
        return f"Weather API error: {e}"
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return f"Error: {e}"


def get_daily_summary(name: str, start_date: str, end_date: str) -> list[dict]:
    """
    Retrieve daily weather summary for a location.
    """
    try:
        start = dt.date.fromisoformat(start_date)
        end = dt.date.fromisoformat(end_date)
    except ValueError:
        return [{"error": "Invalid date format"}]

    loc = conn.execute("SELECT id FROM locations WHERE name = ?", (name,)).fetchone()
    if not loc:
        return [{"error": f"Location '{name}' not found"}]

    readings = fetch_readings(conn, loc["id"], dt.datetime.combine(start, dt.time()), dt.datetime.combine(end, dt.time()))
    return compute_daily_stats(readings)


def get_weekly_high_low(name: str, start_date: str, end_date: str) -> str:
    """
    Retrieve weekly high/low temperature summary.
    """
    try:
        start = dt.date.fromisoformat(start_date)
        end = dt.date.fromisoformat(end_date)
    except ValueError:
        return "Invalid date format"

    loc = conn.execute("SELECT id FROM locations WHERE name = ?", (name,)).fetchone()
    if not loc:
        return f"Location '{name}' not found"

    readings = fetch_readings(conn, loc["id"], dt.datetime.combine(start, dt.time()), dt.datetime.combine(end, dt.time()))
    high, low = weekly_high_low(readings)
    return f"Weekly High: {high}°C, Low: {low}°C" if high is not None else "No readings found"
