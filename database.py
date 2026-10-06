import sqlite3
import csv
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

def init_db():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    
    # Create table if not exists (matching HW specs)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS TemperatureForecasts (
        id INTEGER PRIMARY KEY,
        regionName TEXT,
        dataDate TEXT,
        mint REAL,
        maxt REAL,
        UNIQUE(regionName, dataDate)
    )
    ''')
    conn.commit()
    return conn

def populate_db(conn):
    if not os.path.exists("weather_data.csv"):
        print("Error: weather_data.csv not found.")
        return
        
    cursor = conn.cursor()
    count = 0
    with open("weather_data.csv", "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # 每次匯入都換成最新一週的預報，避免舊日期累積（表格必須剛好 7 天）
    cursor.execute("DELETE FROM TemperatureForecasts")
    for row in rows:
        cursor.execute('''
        INSERT INTO TemperatureForecasts (regionName, dataDate, mint, maxt)
        VALUES (?, ?, ?, ?)
        ''', (row["regionName"], row["dataDate"], float(row["mint"]), float(row["maxt"])))
        count += 1

    conn.commit()
    print(f"Stored {count} records into SQLite database data.db")

def verify_queries(conn):
    cursor = conn.cursor()
    print("-" * 40)
    print("Verification Query 1: SELECT DISTINCT regionName FROM TemperatureForecasts;")
    cursor.execute("SELECT DISTINCT regionName FROM TemperatureForecasts")
    regions = cursor.fetchall()
    for r in regions:
        print(f" - {r[0]}")
        
    print("-" * 40)
    print("Verification Query 2: SELECT * FROM TemperatureForecasts WHERE regionName = '中部地區' LIMIT 7;")
    cursor.execute("SELECT * FROM TemperatureForecasts WHERE regionName = '中部地區' ORDER BY dataDate LIMIT 7")
    rows = cursor.fetchall()
    print("id | regionName | dataDate | mint | maxt")
    for row in rows:
        print(" | ".join(str(x) for x in row))
    print("-" * 40)

if __name__ == "__main__":
    connection = init_db()
    populate_db(connection)
    verify_queries(connection)
    connection.close()
