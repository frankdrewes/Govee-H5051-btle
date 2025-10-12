import sqlite3
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Path to your SQLite database
DB_PATH = "/databases/sensordata.sqlite"

# Connect to the database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Format timestamp for SQLite
cutoff = datetime.now() - timedelta(hours=4)
cutoff_sql = cutoff.strftime("%Y-%m-%d %H:%M:%S")

# Query last 4 hours of data
cursor.execute("""
    SELECT timestamp, temperature, humidity, battery, signal, sensor_id
    FROM data
    WHERE timestamp >= ?
    ORDER BY timestamp DESC
""", (cutoff_sql,))
rows = cursor.fetchall()
conn.close()

# Build Rich table
table = Table(title="Sensor Data (Last 4 Hours)", show_lines=True)
table.add_column("Time", style="cyan")
table.add_column("Temp (°C)", justify="right")
table.add_column("Temp (°F)", justify="right")
table.add_column("Humidity (%)", justify="right")
table.add_column("Battery (%)", justify="right")
table.add_column("Signal (dBm)", justify="right")
table.add_column("Sensor_ID", justify="right")

latest_timestamp = None

for ts, temp_c, hum, bat, sig, sensor_id in rows:
    temp_f = temp_c * 9 / 5 + 32
    table.add_row(ts, f"{temp_c:.2f}", f"{temp_f:.2f}", f"{hum:.2f}", str(bat), str(sig), f"{sensor_id}")
    if not latest_timestamp:
        latest_timestamp = ts  # First row is most recent due to DESC

# Display in panel
console = Console()
console.print(Panel(table, title="📡 BLE Telemetry Snapshot", border_style="green"))

# Show time since last event
if latest_timestamp:
    last_time = datetime.strptime(latest_timestamp, "%Y-%m-%d %H:%M:%S")
    delta = datetime.now() - last_time
    minutes = int(delta.total_seconds() // 60)
    seconds = int(delta.total_seconds() % 60)
    console.print(Text(f"⏱️ Last event was {minutes} min {seconds} sec ago", style="bold yellow"))
else:
    console.print(Text("⚠️ No data found in the last 4 hours.", style="bold red"))
    