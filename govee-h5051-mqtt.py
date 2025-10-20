#!/usr/bin/env python3

import socket
import sys
import time
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.table import Table
from rich.console import Console
import json
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
import asyncio

console = Console(force_terminal=True)

load_dotenv()  # Loads from .env by default

MQTT_SERVER = os.getenv("MQTT_SERVER")
MQTT_SERVER_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
LISTENER_DURATION =  int(os.getenv("LISTENER_DURATION",30))

MQTT_TOPIC =  "sensor/h5051"

# Flag to stop scanning once a value is found
found = asyncio.Event()



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
    
    # Signal that we're done
    log_to_mqtt(temperature,humidity,battery,signal)
    found.set() 
             
def log_to_mqtt(temperature,
            humidity,
            battery,
            signal
            ):

    print(f"Connecting to {MQTT_SERVER}:{MQTT_SERVER_PORT}")
    print(f"writing to MQTT topic {MQTT_TOPIC}")
    
    payload = {
        "temperature": f"{temperature:.1f}",
        "humidity": f"{humidity:.1f}",
        "battery": battery,
        "signal": signal,
                }
    
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME,MQTT_PASSWORD)
    client.connect(MQTT_SERVER,int(MQTT_SERVER_PORT), 60)
    mqtt_result= client.publish(MQTT_TOPIC, json.dumps(payload))
    
    if mqtt_result.is_published:
        print(f"MQTT #1 publish results -> {mqtt_result.rc}")
    
    print(f"MQTT publish done")


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
