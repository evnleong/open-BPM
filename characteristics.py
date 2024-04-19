# Use for retrieving all BLE characteristics and services via Bleak for a BLE device (Windows)
import asyncio
from bleak import BleakClient
from dotenv import load_dotenv
import os

# Bluetooth MAC address of the Omron 10-Series cuff (BP7450) (HEM-7342T-Z)
# OMRON_ADDRESS = os.environ.get( "BP7450_MAC_ADDRESS")

# Bluetooth MAC address of the 10 Series cuff (BP7000) (HEM-7600T-Z)
OMRON_ADDRESS = os.environ.get("BP7000_MAC_ADDRESS")


# Get all Characteristics and Services for OMRON 10 Series
async def main(address):
    async with BleakClient(address) as client:
        try:
            services = await client.get_services()
            print("Descriptors: ")
            for descriptor in services.descriptors.values():
                print(f"\t {descriptor}")
            # print(services.descriptors)

            print("")
            print("Characteristics: ")
            for characteristic in services.characteristics.values():
                print(f"\t {characteristic}")
            # print(services.characteristics)

            print("")
            print("Services")
            for service in services.services.values():
                print(f"\t {service}")
            # print(services.services)
        finally:
            print("disconnecting")
            await client.disconnect()


asyncio.run(main(OMRON_ADDRESS))
