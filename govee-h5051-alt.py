from bleak import BleakScanner
import asyncio

# Flag to stop scanning once a value is found
found = asyncio.Event()


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
            temp_f = temp_c * 9 / 5 + 32
            humidity = humidity_raw / 100

            print(f"Temperature: {temp_c:.2f} C / {temp_f:.2f} F")
            print(f"Humidity: {humidity:.2f} %")
            print(f"Battery: {battery} %")

            # Signal that we're done
            found.set()

async def main():
    scanner = BleakScanner(detection_callback)
    await scanner.start()
    try:
        await asyncio.wait_for(found.wait(), timeout=15)  # Wait up to 15 seconds
    except asyncio.TimeoutError:
        print("No Govee packet received within timeout.")
    await scanner.stop()


asyncio.run(main())