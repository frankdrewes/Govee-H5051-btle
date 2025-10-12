# Govee H5051 BLE Scanner & Logger

This Python script scans for **Govee H5051 BLE sensors**, decodes their advertisement payloads, and logs temperature, humidity, battery level, and signal strength into a local SQLite database. It also displays real-time telemetry using [Rich](https://github.com/Textualize/rich) for a clean terminal UI.

---

## 🔍 Features

- Detects BLE devices with names starting with `Govee_H5051_`
- Filters for Govee's manufacturer ID (`60552`)
- Decodes:
  - Temperature (°C)
  - Humidity (%)
  - Battery level (%)
  - Signal strength (RSSI)
- Displays telemetry in a styled Rich table
- Logs data into a local SQLite database
- Stops scanning once a valid device is found or after 60 seconds

---

## 🧰 Requirements

- Python 3.7+
- [Bleak](https://pypi.org/project/bleak/)
- [Rich](https://pypi.org/project/rich/)

Install dependencies:


pip install bleak rich 





# Govee H5051 BLE Scanner

This script uses Bleak to passively scan Bluetooth Low Energy (BLE) advertising packets from Govee H5051 temperature/humidity sensors. It decodes the raw manufacturer data into human-readable temperature (°C/°F), humidity (%), and battery level (%).

 ## Requirements
- Python 3.7+
- Bleak (pip install bleak)
- A Linux or Windows PC with BLE support (e.g. Raspberry Pi, laptop, USB BLE dongle)

 ## How It Works
- BLE Scanning: Uses BleakScanner to listen for BLE advertisements.
- Device Filtering: Filters for devices with "Govee" in their name.
- Manufacturer Data Extraction: Pulls data from manufacturer ID 60552 (0xEC88), which this device uses.
- Payload Decoding: Parses -  the 6-byte payload into:
- Temperature (°C and °F)
- Humidity (%)
- Battery level (%)

## Payload Format
The Govee H5051 broadcasts a 6-byte manufacturer data payload:
 - Byte 0: Padding or reserved (0x00), not part of temperature
 - Byte 1-2: Temperature (little-endian, scaled by 100)
 - Byte 3-4: Humidity (little-endian, scaled by 100)
 - Byte 5: Battery (single byte, percentage, no scaling)

## Sample Output
  - Raw bytes: ['0x0', '0x28', '0xb', '0xab', '0x11', '0x64']
  - Decoded Temperature: 28.56 C / 83.41 F
  - Decoded Humidity: 45.23 %
  - Decoded Battery: 100 %
  - Raw payload: 00280bab1164
  - Device name
  - device MAC address
  - Signal Strength (RSSI)


## Notes:
- This script assumes passive BLE scanning only—no active connections or GATT reads.
- Govee’s manufacturer ID (60552) is hardcoded; adjust if using other models.
- BLE advertising intervals vary; multiple packets may be received per device.

The -alt version collects a single value within a timeout period

## govee-h5051-logger.py
 - Logs data to sqlite3 database

## status.py
 - Shows the most recent data logged
 