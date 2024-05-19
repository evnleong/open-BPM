import pydbus
from gi.repository import GLib
import serial
import sys
import time
import os

# Setup of device specific values
dev_id = os.environ.get("BP7000_MAC_ADDRESS")
adapter_path = "/org/bluez/hci0"
device_path = f"{adapter_path}/dev_{dev_id.replace(':', '_')}"
bp_reading_uuid = "00002a35-0000-1000-8000-00805f9b34fb"


# Some helper functions
def get_characteristic_path(device_path, uuid):
    """Find DBus path for UUID on a device"""
    mng_objs = mngr.GetManagedObjects()
    for path in mng_objs:
        chr_uuid = mng_objs[path].get("org.bluez.GattCharacteristic1", {}).get("UUID")
        if path.startswith(device_path) and chr_uuid == uuid:
            return path


# Enable eventloop for notifications
def temp_handler(iface, prop_changed, prop_removed):
    """Notify event handler for temperature"""
    if "Value" in prop_changed:
        ser = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
        ser.reset_input_buffer()
        print(f"Measurement Received: {(prop_changed['Value'])} \u00B0C")
        data = prop_changed["Value"]
        sys = data[1]
        dias = data[3]
        bpm = data[14]
        print(f"Sys: {sys} Dias: {dias} Pulse: {bpm}")
        ser.write(bytes(f" {sys},{dias},{bpm} \n ", encoding="utf-8"))


try:

    # Setup DBus informaton for adapter and remote device
    bus = pydbus.SystemBus()
    mngr = bus.get("org.bluez", "/")
    adapter = bus.get("org.bluez", adapter_path)
    device = bus.get("org.bluez", device_path)
    # Connect to device (needs to have already been paired via bluetoothctl)
    # Get a couple of characteristics on the device we are connected to
    temp_reading_path = get_characteristic_path(device._path, temp_reading_uuid)
    # temp_period_path = get_characteristic_path(device._path, temp_period_uuid)
    temp = bus.get("org.bluez", temp_reading_path)
    try:
        device.Connect()
    except:
        time.sleep(5)
        try:
            device.Connect()
        except:
            pass
    print("connected")
    time.sleep(2)
    ser = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
    ser.reset_input_buffer()
    ser.write(bytes("000 \n", encoding="utf-8"))
    ser.close()

    mainloop = GLib.MainLoop()
    temp.onPropertiesChanged = temp_handler
    temp.StartNotify()
    mainloop.run()
except KeyboardInterrupt:
    mainloop.quit()
    temp.StopNotify()
    device.Disconnect()
