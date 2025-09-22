from bleak import BleakScanner
import asyncio

#- Data array structure (expected length: 6 bytes):
#  Byte 0: Padding or reserved (0x00), not part of temperature
#  Byte 1-2: Temperature (little-endian, scaled by 100)
#  Byte 3-4: Humidity (little-endian, scaled by 100)
#  Byte 5: Battery (single byte, percentage, no scaling)
#- Temperature is stored in 2 bytes, little-endian, scaled by 100.
#- Humidity is also 2 bytes, little-endian, scaled by 100.
#- Battery is a single byte, no scaling.
def parse_govee_data(data):
    print(f"Data: {data} ")
    # Print raw bytes for inspection
    print("Raw bytes:", [hex(b) for b in data])
    
    # decoding temperature and humidity as little-endian 16-bit integers
    temp_raw = int.from_bytes(data[1:3], byteorder='little')     # skip first byte
    humidity_raw = int.from_bytes(data[3:5], byteorder='little') 
    battery = data[5]  # single byte

    # scaling
    temperature_c = temp_raw / 100
    temperature_f = temperature_c * 9 / 5 + 32
    humidity = humidity_raw / 100

    print(f"Decoded Temperature: {temperature_c:.2f} C / {temperature_f:.2f} F")
    print(f"Decoded Humidity: {humidity:.2f} %")
    print(f"Decoded Battery: {battery} %")

def detection_callback(device, adv_data):
    if "Govee" in (device.name or ""):
        mfg_data = adv_data.manufacturer_data.get(60552)  # Govee's manufacturer ID
        if mfg_data:
            parse_govee_data(mfg_data)
            print("Raw payload:", mfg_data.hex())

async def main():
    scanner = BleakScanner(detection_callback)
    
    await scanner.start()
    await asyncio.sleep(10)
    await scanner.stop()

asyncio.run(main())