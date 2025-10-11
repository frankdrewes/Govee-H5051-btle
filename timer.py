from bleak import BleakScanner
import asyncio
import time

last_seen = {}

def detection_callback(device, adv_data):
    if "Govee" in (device.name or ""):
        mfg_data = adv_data.manufacturer_data.get(60552)  # Govee's manufacturer ID
        if mfg_data:
            now = time.time()
            delta = None

            print("Raw payload:", mfg_data.hex())
            print(f"Device Address: {device.address}")
            print(f"Name: {device.name}")
            print(f"Signal: {adv_data.rssi} dBm")
            
            if device.address in last_seen:
                delta = now - last_seen[device.address]
                print(f"⏱️ Time since last callback: {delta:.2f} seconds")
            else:
                print("⏱️ First time seeing this device.")

            last_seen[device.address] = now


async def main():
    scanner = BleakScanner(detection_callback)
    
    await scanner.start()
    await asyncio.sleep(600)
    await scanner.stop()

asyncio.run(main())