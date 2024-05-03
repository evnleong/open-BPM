# Python script for connection/authentication and data retreival from OMRON BP7450 and BP7600 -- Requires gattool (Linux only)
import pygatt
import logging
from binascii import hexlify
import time
from datetime import datetime
from dotenv import load_dotenv
import os
import csv

adapter = pygatt.GATTToolBackend()

logging.basicConfig()
logging.getLogger("pygatt").setLevel(logging.DEBUG)

# DEVICE_MAC= os.environ.get("BP7450_MAC_ADDRESS")
DEVICE_MAC = os.environ.get("BP7000_MAC_ADDRESS")


# Get BPM timestamp
current_time = datetime.now()


# Function for parsing hex values
def parse_bpm(input):
    if len(input) == 2:
        v = int(input, 16)
        print(current_time)
        return v
    elif len(input) == 36:
        # systolic val is hex at index 2&3
        sys = int(input[2:4], 16)
        # diastolic val is hex at index 6&8
        dias = int(input[6:8], 16)
        # bpm is hex at index 28 & 30
        bpm = int(input[28:30], 16)
        return f"Timestamp[{current_time}] \n Systolic Pressure = {sys} mmHg \n Diastolic Pressure = {dias} mmHg \n BPM = {bpm} beats/min"


def write_to_csv(hex):
    with open("log.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=" ")
        writer.writerow([hex, current_time])


def handle_value(handle, value):
    ascii = binascii.b2a_hex(value)
    write_to_csv(ascii)
    print(parse_bpm(ascii))


try:

    adapter.start()
    device = adapter.connect(DEVICE_MAC, timeout=8, auto_reconnect=True)
    device.subscribe(
        "00002a35-0000-1000-8000-00805f9b34fb",
        callback=handle_value,
        indication=True,
        wait_for_response=False,
    )

    device.char_write_handle(0x12, bytearray([0x02, 0x00]))
    device.char_write_handle(0x812, bytearray([1, 1, 1, 1, 1]))

    time.sleep(5)

    while True:
        print("Waiting")

except:
    adapter.stop()


finally:

    time.sleep(4)
    adapter.stop()
