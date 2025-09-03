import sqlite3
from datetime import datetime, timedelta
import random
import logging
import os

# -----------------------------
# Logging setup
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

DB_FILE = "weather.db"

# -----------------------------
# Create DB and Tables
# -----------------------------
def init_db():
    db_exists = os.path.exists(DB_FILE)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if not db_exists:
        logging.info(f"Creating new database at {DB_FILE}")

    # Create locations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        lat REAL,
        lon REAL
    )
    """)
    logging.info("Created table: locations")

    # Create readings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS readings (
        id INTEGER PRIMARY KEY,
        location_id INTEGER,
        time TIMESTAMP,
        temp_c REAL,
        source TEXT,
        FOREIGN KEY(location_id) REFERENCES locations(id)
    )
    """)
    logging.info("Created table: readings")

    conn.commit()
    return conn

# -----------------------------
# Insert mock data
# -----------------------------
def insert_mock_data(conn):
    cursor = conn.cursor()

    # Define sample locations
    locations = [
        {"name": "New York", "lat": 40.7128, "lon": -74.0060},
        {"name": "San Francisco", "lat": 37.7749, "lon": -122.4194}
    ]

    for loc in locations:
        cursor.execute("INSERT INTO locations (name, lat, lon) VALUES (?, ?, ?)",
                       (loc["name"], loc["lat"], loc["lon"]))
        loc_id = cursor.lastrowid
        logging.info(f"Inserted location: {loc['name']} (id: {loc_id})")

        # Insert 7 days of mock readings
        for i in range(7):
            date = datetime.now() - timedelta(days=6-i)
            temp = round(random.uniform(10, 30), 1)
            cursor.execute(
                "INSERT INTO readings (location_id, time, temp_c, source) VALUES (?, ?, ?, ?)",
                (loc_id, date.isoformat(), temp, "mock")
            )
        logging.info(f"Inserted 7 days of mock readings for {loc['name']}")

    conn.commit()
    logging.info("Database initialization complete.")

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    conn = init_db()
    insert_mock_data(conn)
    conn.close()
    logging.info("Database connection closed.")

