# blueZ based script for connecting to OMRON BP7600 (works) and BP7450 (work in progress) and retrieving BP data (Linux only)
from bluepy import btle
import binascii
import time
from datetime import datetime
from dotenv import load_dotenv
import os

# Global variables

DEVICE_MAC_ADDRESS = os.environ.get("BP7450_MAC_ADDRESS")  # OMRON BT7450
# DEVICE_MAC_ADDRESS = os.environ.get("BP7000_MAC_ADDRESS") #OMRON EVOLV BT7600
BLESERVICE_UUID = "00001810-0000-1000-8000-00805f9b34fb"  # from SIG protocol


# Global decoder function for received hex array to decimal
def parse_bpm(input):
    current_time = datetime.now()
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


# Creating Delegate class
class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        ascii = binascii.b2a_hex(data)
        print("A notification was received: %s" % binascii.b2a_hex(data))
        print(parse_bpm(ascii))


# Attempt connection twice
for i in range(2):
    try:
        p = btle.Peripheral(DEVICE_MAC_ADDRESS)
        p.setDelegate(MyDelegate())

        # Setup to turn notifications on, e.g.
        svc = p.getServiceByUUID(BLESERVICE_UUID)
        ch = svc.getCharacteristics()[0]
        print("Connected!")
        print(f"Subscribed to handle {ch.valHandle}")

        while True:
            if p.waitForNotifications(1.0):
                # handleNotification() was called
                continue
            print("Waiting for response...")

    # If BT device disconnects, attempt reconnection.
    except btle.BTLEDisconnectError:
        print("Bluetooth device disconnected. Attempting Reconnection in 5 seconds...")
        time.sleep(5)  # Wait for a few seconds before attempting to reconnect
        print("Attempting reconnection")
        continue
