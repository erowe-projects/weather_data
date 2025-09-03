import datetime as dt
import sqlite3
from typing import List, Dict, Optional
from .logging_config import get_logger

logger = get_logger(__name__)

# Schema definitions for DRYness
TABLES = {
    "locations": """
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """,
    "weather_readings": """
        CREATE TABLE IF NOT EXISTS weather_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER NOT NULL,
            time TIMESTAMP NOT NULL,
            temp_c REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(location_id, time),
            FOREIGN KEY(location_id) REFERENCES locations(id)
        );
    """,
}


def init_db(conn: sqlite3.Connection) -> None:
    """
    Initialize database schema if not present.
    """
    cur = conn.cursor()
    for ddl in TABLES.values():
        cur.execute(ddl)
    conn.commit()
    conn.row_factory = sqlite3.Row
    logger.info("Database initialized with tables: %s", ", ".join(TABLES.keys()))


def insert_location(conn: sqlite3.Connection, name: str, lat: float, lon: float) -> int:
    """
    Insert or retrieve a location by name.
    """
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO locations(name, lat, lon) VALUES (?, ?, ?);",
        (name, lat, lon),
    )
    conn.commit()
    cur.execute("SELECT id FROM locations WHERE name = ?;", (name,))
    row = cur.fetchone()
    if row is None:
        raise RuntimeError("Failed to insert or retrieve location")
    logger.debug("Location %s mapped to ID %s", name, row[0])
    return row[0]


def get_location_by_name(conn: sqlite3.Connection, name: str) -> Optional[Dict]:
    """
    Fetch location by name.
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM locations WHERE name = ?;", (name,))
    row = cur.fetchone()
    return dict(row) if row else None


def upsert_weather_readings(
    conn: sqlite3.Connection, location_id: int, readings: List[Dict]
) -> int:
    """
    Insert weather readings, skipping duplicates.
    Returns number of new rows inserted.
    """
    inserted = 0
    cur = conn.cursor()
    for r in readings:
        try:
            cur.execute(
                "INSERT INTO weather_readings(location_id, time, temp_c) VALUES (?, ?, ?);",
                (location_id, r["time"], r["temp_c"]),
            )
            inserted += 1
        except sqlite3.IntegrityError:
            logger.debug("Skipping duplicate reading at %s", r["time"])
    conn.commit()
    logger.info("Inserted %d new readings", inserted)
    return inserted


def fetch_readings(
    conn: sqlite3.Connection,
    location_id: int,
    start: dt.datetime,
    end: dt.datetime,
) -> List[Dict]:
    """
    Fetch readings for a location within a time range.
    """
    cur = conn.cursor()
    cur.execute(
        """
        SELECT time, temp_c
        FROM weather_readings
        WHERE location_id = ? AND time BETWEEN ? AND ?
        ORDER BY time ASC;
        """,
        (location_id, start, end),
    )
    rows = cur.fetchall()
    results = []
    for r in rows:
        timestamp = (
            dt.datetime.fromisoformat(r["time"]) if isinstance(r["time"], str) else r["time"]
        )
        # Ensure temp_c is a float or None
        temp_c = r["temp_c"]
        if temp_c is not None:
            if isinstance(temp_c, bytes):
                import struct
                temp_c = struct.unpack('f', temp_c)[0]
            else:
                temp_c = float(temp_c)
        results.append({"time": timestamp, "temp_c": temp_c})
    return results
