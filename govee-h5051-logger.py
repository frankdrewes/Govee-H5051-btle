#!/usr/bin/env python3

import sqlite3
import time
import struct
from datetime import datetime
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
import asyncio
import os
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich.console import Console

console = Console()

# Flag to stop scanning once a value is found
found = asyncio.Event()

DB_PATH = "/databases/sensordata.sqlite"  

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
   
def detection_callback(device: BLEDevice, data: AdvertisementData):
    """
        Summary:
            Called when an update is received from the bluetooth device.
        Parameters:
            BLEDevice: 
                The BLE device.
            AdvertisementData: 
                The advertisement data.
        Returns:
            A dictionary with the sensor data if the device is a Govee H5051, otherwise None.
    """
    
    if not data.local_name or not data.local_name.startswith('Govee_H5051_'):
        return
    
    device_data = data.manufacturer_data.get(60552) # Govee's manufacturer ID
    if not device_data :
        return
    
    temperature, humidity, battery = decode_data(device_data)
    signal = data.rssi
    sensor_id=device.name

    table = Table(show_header=False,  title="H5051 BLE Sensor Telemetry")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    table.add_row("Name", device.name)
    table.add_row("Device Address", device.address)
    table.add_row("Sensor ID", sensor_id)
    table.add_row("Temperature", f"{temperature:.2f} °C")
    table.add_row("Humidity", f"{humidity:.2f} %")
    table.add_row("Battery", f"{battery} %")
    table.add_row("Signal", f"{signal} dBm")
    console.print(table)
             
    log_to_sqlite(temperature, humidity, battery, signal, sensor_id)

    # Signal that we're done
    found.set() 

def decode_data(device_data):
    """ 
    summary_ 
    Decode temperature, humidity and battery from Govee H5051 advertisement packet.
    Returns temperature in Celsius, relative humidity in percent and battery in percent
    """
    # Temperature
    temp_raw = int.from_bytes(device_data[1:3], byteorder='little')
    temperature = temp_raw / 100
    # Humidity
    humidity_raw = int.from_bytes(device_data[3:5], byteorder='little')
    humidity = humidity_raw / 100
    # Battery
    battery = device_data[5]
    return temperature,humidity,battery
            
def log_to_sqlite(temperature, humidity,battery,signal,sensor_id):
    print(f"writing to DB @ {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            temperature REAL,
            humidity REAL,
            battery INTEGER,
            signal INTEGER,
            sensor_id TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO data (
            timestamp,
            temperature,
            humidity,
            battery,
            signal,
            sensor_id ) 
            VALUES (?, ?, ?, ?, ?, ?) """, 
            (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            temperature,
            humidity,
            battery,
            signal,
            sensor_id
            ) 
                )
    conn.commit()
    conn.close()
    print(f"DB update done")

async def main():
    clear_screen()
    scanner = BleakScanner(detection_callback)
    await scanner.start()

    # Countdown from 60 seconds
    with Progress(
        TextColumn("[cyan]Scanning for Govee H5051 BLE devices..."),
        BarColumn(),
        TextColumn("[progress.remaining] {task.remaining} sec left"),
    ) as progress:
        task = progress.add_task("scan", total=60)
        for remaining in reversed(range(60)):
            if found.is_set():
                break
            await asyncio.sleep(1)
            progress.update(task, completed= 60 - remaining)

    await scanner.stop()
    
    if not found.is_set() :
        print(f"Timeout without finding device")
            
asyncio.run(main())
