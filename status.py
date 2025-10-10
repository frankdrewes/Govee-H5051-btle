import sqlite3
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Path to your SQLite database
DB_PATH = "/databases/govee5051.sqlite"  

# Connect to the database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Calculate cutoff timestamp
cutoff = datetime.now() - timedelta(hours=4)
cutoff_iso = cutoff.isoformat()

# Query last 4 hours of data
cursor.execute("""
    SELECT timestamp, temperature, humidity, battery, signal, sensor_id
    FROM data
    WHERE timestamp >= ?
    ORDER BY timestamp DESC
""", (cutoff_iso,))
rows = cursor.fetchall()
conn.close()

# Build Rich table
table = Table(title="Sensor Data (Last 4 Hours)", show_lines=True)
table.add_column("Time", style="cyan")
table.add_column("Temp (°C)", justify="right")
table.add_column("Humidity (%)", justify="right")
table.add_column("Battery (%)", justify="right")
table.add_column("Signal (dBm)", justify="right")
table.add_column("Sensor ID", style="magenta")

for ts, temp, hum, bat, sig, sid in rows:
    table.add_row(ts, f"{temp:.2f}", f"{hum:.2f}", str(bat), str(sig), sid)

# Display in panel
console = Console()
console.print(Panel(table, title="📡 BLE Telemetry Snapshot", border_style="green"))