import psutilFeatures
import json
import datetime
import time
import sqlite3
import threading
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Veritabanı oluşturma
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

# Verileri kaydetme
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

# Sistem bilgisi alma
def get_system_info():
    info = {
        "timestamp": datetime.datetime.now().isoformat(),
        "cpu_percent": psutilFeatures.cpu_percent(interval=1),
        "cpu_cores": psutilFeatures.cpu_count(logical=False),
        "cpu_threads": psutilFeatures.cpu_count(logical=True),
        "memory": {
            "total": psutilFeatures.virtual_memory().total,
            "used": psutilFeatures.virtual_memory().used,
            "percent": psutilFeatures.virtual_memory().percent
        },
        "disk": {
            "total": psutilFeatures.disk_usage('/').total,
            "used": psutilFeatures.disk_usage('/').used,
            "percent": psutilFeatures.disk_usage('/').percent
        },
        "uptime_seconds": int((datetime.datetime.now() - datetime.datetime.fromtimestamp(psutilFeatures.boot_time())).total_seconds())
    }

    return info

# Arka planda çalışan veri toplayıcı
def background_data_collector(interval_seconds=60):
    while True:
        info = get_system_info()
        save_to_db(info)
        time.sleep(interval_seconds)

# Lifespan ile başlatma
@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_database()
    thread = threading.Thread(target=background_data_collector, daemon=True)
    thread.start()
    yield  # uygulama çalıştığı sürece burası bekler

app = FastAPI(lifespan=lifespan)

# Anlık veri alma
@app.get("/data")
def get_data():
    return get_system_info()

# Veritabanındaki geçmiş verileri alma
@app.get("/logs")
def get_logs():
    conn = sqlite3.connect("system_info.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM system_info ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Geliştirme ortamında direkt çalıştırmak için
if __name__ == "__main__":
    setup_database()
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
