import sqlite3
import json
import os
from datetime import datetime
from ..schemas.temperature import StationTemperature

DB_PATH = "history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS historical_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT UNIQUE,
        data TEXT
    )
    ''')
    conn.commit()
    conn.close()

def save_snapshot(timestamp: str, stations: list[StationTemperature]):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Store the entire snapshot as JSON for easy retrieval
    data_json = json.dumps([s.model_dump(mode="json") for s in stations])
    
    try:
        cursor.execute("INSERT OR IGNORE INTO historical_data (timestamp, data) VALUES (?, ?)", (timestamp, data_json))
        conn.commit()
    except Exception as e:
        print(f"Failed to save snapshot: {e}")
    finally:
        conn.close()

def get_history_snapshots():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp FROM historical_data ORDER BY timestamp ASC")
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_snapshot(timestamp: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM historical_data WHERE timestamp = ?", (timestamp,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None
