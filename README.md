# System Information Collector

A FastAPI-based system information collector and logger for Raspberry Pi (or other devices), storing data in an SQLite database.

## Features

- **System Information:** Collects CPU usage, memory usage, disk usage, uptime, and more.
- **Database:** Information is stored in an SQLite database.
- **Web API:** 
  - `/data`: Returns real-time system information.
  - `/logs`: Returns historical system information from the database.
- **Background Data Collection:** Continuously collects system information and stores it in the database.
- **Deployment:** Developed using FastAPI and can be run using `uvicorn`.

## Requirements

- Python 3.x
- `psutil` - For collecting system information.
- `FastAPI` - For building the web API.
- `sqlite3` - For managing the database.
- `uvicorn` - To run the FastAPI application.

### Install Dependencies

To install the required dependencies, you can use `pip`:

```bash
pip install psutil fastapi uvicorn
```

Usage
Running the Application:

To run the FastAPI application, use uvicorn:

```bash
uvicorn your_script_name:app --reload
```

Replace your_script_name with the name of the file containing your FastAPI application (without the .py extension).

Accessing the Data:

Visit http://127.0.0.1:8000/data to view the real-time system information.

Visit http://127.0.0.1:8000/logs to view historical system data stored in the SQLite database.

How It Works

Database Setup: The application creates an SQLite database named system_info.db. The setup_database() function is called on startup to ensure that the required table exists.

System Information Collection: The get_system_info() function collects the system's current information, including CPU usage, memory, disk usage, and uptime.

Data Storage: The save_to_db(info) function stores the collected information in the database. This is done in the background by the background_data_collector() function, which runs in a separate thread, collecting data every 60 seconds.

Running as a Service (Optional)
If you want this application to start automatically on boot on a Raspberry Pi or any Linux machine, you can create a systemd service. This ensures that the application will start every time the system boots up.


Create a systemd service file (e.g., system_info_collector.service):

```bash
[Unit]
Description=System Information Collector Service

[Service]
ExecStart=/usr/bin/uvicorn your_script_name:app --host 0.0.0.0 --port 8000
WorkingDirectory=/path/to/your/app
User=pi
Restart=always

[Install]
WantedBy=multi-user.target
```
2)Enable and start the service:

```bash
sudo systemctl enable system_info_collector.service
sudo systemctl start system_info_collector.service
```
