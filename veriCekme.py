import psutil
import json
import datetime
import time
import sqlite3
import threading
from fastapi import FastAPI
from contextlib import asynccontextmanager

def setup_database():
    conn = sqlite3.connect("system_info.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            cpu_percent REAL,
            cpu_cores INTEGER,
            cpu_threads INTEGER,
            memory_total INTEGER,
            memory_used INTEGER,
            memory_percent REAL,
            disk_total INTEGER,
            disk_used INTEGER,
            disk_percent REAL,
            uptime_seconds INTEGER
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(info):
    conn = sqlite3.connect("system_info.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO system_info (
            timestamp, cpu_percent, cpu_cores, cpu_threads,
            memory_total, memory_used, memory_percent,
            disk_total, disk_used, disk_percent,
            uptime_seconds
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        info["timestamp"],
        info["cpu_percent"],
        info["cpu_cores"],
        info["cpu_threads"],
        info["memory"]["total"],
        info["memory"]["used"],
        info["memory"]["percent"],
        info["disk"]["total"],
        info["disk"]["used"],
        info["disk"]["percent"],
        info["uptime_seconds"]
    ))
    conn.commit()
    conn.close()

def get_system_info():
    info = {
        "timestamp": datetime.datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_cores": psutil.cpu_count(logical=False),
        "cpu_threads": psutil.cpu_count(logical=True),
        "memory": {
            "total": psutil.virtual_memory().total,
            "used": psutil.virtual_memory().used,
            "percent": psutil.virtual_memory().percent
        },
        "disk": {
            "total": psutil.disk_usage('/').total,
            "used": psutil.disk_usage('/').used,
            "percent": psutil.disk_usage('/').percent
        },
        "uptime_seconds": int((datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())).total_seconds())
    }

    return info

def background_data_collector(interval_seconds=60):
    while True:
        info = get_system_info()
        save_to_db(info)
        time.sleep(interval_seconds)
        """
        run every 60 seconds with this function
        """

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_database()
    thread = threading.Thread(target=background_data_collector, daemon=True)
    thread.start()
    yield  

app = FastAPI(lifespan=lifespan)
"""
@asynccontextmanager,manage the functions when the FastAPI start
target = background_data_collector, taking the system informations constantly
daemon = True, stop the threading when applicaton closed
"""

@app.get("/data")
def get_data():
    return get_system_info()

@app.get("/logs")
def get_logs():
    conn = sqlite3.connect("system_info.db")
    conn.row_factory = sqlite3.Row
    """
    sqlite3.Row, changing the query resulto to row and each row like a dict
    example=>id": 1, "timestamp": "2025-04-13T12:34:56
    after we can reach every column names like a key
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM system_info ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    setup_database()
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
