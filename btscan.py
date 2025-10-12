#!/usr/bin/env python3

import sqlite3
import time
import struct
import asyncio
import os
from datetime import datetime
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
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
            A dictionary with the sensor data if the device is a Govee H5075, otherwise None.
    """
        
    if not data.local_name or not data.local_name.startswith('G'):
        return

    device_data = data.manufacturer_data
    if not device_data :
        return
    
    print(f"Name {device.name}")
    print(f"Device Address {device.address}")
    print(f"Signal {data.rssi}")
    print(f"Local Name {data.local_name}")
    print(f"Manufacturer_data {data.manufacturer_data}")
    print(f"Service_uuid {data.service_uuids}")
    print("\n \n \n")

    # Signal that we're done
    #found.set()   
    
async def main():
    clear_screen()
    scanner = BleakScanner(detection_callback)
    await scanner.start()

    # Countdown from 60 seconds
    with Progress(
        TextColumn("[cyan]Scanning for BLE devices..."),
        BarColumn(),
        TextColumn("[progress.remaining] {task.remaining} sec left"),
    ) as progress:
        task = progress.add_task("scan", total=600)
        for remaining in reversed(range(600)):
            if found.is_set():
                break
            await asyncio.sleep(1)
            progress.update(task, completed=600 - remaining)

    await scanner.stop()
    
    if not found.is_set() :
        print(f"Timeout without finding device")
        
asyncio.run(main())