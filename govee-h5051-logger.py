#!/usr/bin/env python3

import sqlite3
import time
from datetime import datetime
from bleak import BleakScanner
import asyncio

# Flag to stop scanning once a value is found
found = asyncio.Event()

DB_PATH = "/databases/govee5051.sqlite"  


   
def detection_callback(device, adv_data):
    if "Govee" in (device.name or ""):
        mfg_data = adv_data.manufacturer_data.get(60552)  # Govee's manufacturer ID
        # mfg_data = adv_data.manufacturer_data.get(35052)  # Govee's manufacturer ID
        if mfg_data:
            # Decode and print
            temp_raw = int.from_bytes(mfg_data[1:3], byteorder='little')
            humidity_raw = int.from_bytes(mfg_data[3:5], byteorder='little')
            battery = mfg_data[5]

            temp_c = temp_raw / 100
            humidity = humidity_raw / 100
            signal = adv_data.rssi
            sensor_id=device.name

            print("-------------------------------------")
            print(f"Name: {device.name}")
            print(f"Device Address: {device.address}")
            print("-------------------------------------")
            print(f"Temperature: {temp_c:.2f} C ")
            print(f"Humidity: {humidity:.2f} %")
            print(f"Battery: {battery} %")
            print(f"Signal: {signal} dBm")
            print("-------------------------------------")
             
            log_to_sqlite(temp_c, humidity, battery, signal, sensor_id)

            # Signal that we're done
            found.set()   
            
def log_to_sqlite(temp,humidity,battery,signal,sensor_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO data (timestamp, temp, humidity, battery, signal, sensor_id) VALUES (?, ?, ?, ?, ?, ?)",
                   (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), temp, humidity, battery, signal, sensor_id))

    conn.commit()
    conn.close()

async def main():
    scanner = BleakScanner(detection_callback)
    await scanner.start()
    try:
        await asyncio.wait_for(found.wait(), timeout=15)  # Wait up to 15 seconds
    except asyncio.TimeoutError:
        print("No Govee packet received within timeout.")
    await scanner.stop()
        
asyncio.run(main())