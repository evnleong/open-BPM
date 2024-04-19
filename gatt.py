# Run script for initial connection/authentication to BP7450 and BP7600 -- not currently working (Linux only)
import pygatt
import logging
from binascii import hexlify
import time
from dotenv import load_dotenv
import os

adapter = pygatt.GATTToolBackend()

logging.basicConfig()
logging.getLogger("pygatt").setLevel(logging.DEBUG)

# DEVICE_MAC= os.environ.get("BP7450_MAC_ADDRESS")
DEVICE_MAC = os.environ.get("BP7000_MAC_ADDRESS")


def handle_value(handle, value):
    print("hello")


try:

    adapter.start()

    device = adapter.connect(DEVICE_MAC, timeout=20, auto_reconnect=False)
    print("hi")

    device.subscribe(
        "00002a35-0000-1000-8000-00805f9b34fb", callback=handle_value, indication=True
    )
    # attempt write request for auth
    device.char_write_handle(0x12, bytearray([0x02, 0x00]))
    time.sleep(5)
    while True:
        print("waiting")


finally:

    time.sleep(4)
    adapter.stop()
