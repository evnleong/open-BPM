# open-BPM

An open-source blood pressure monitoring BLE software kit built in Python to enable patients using OMRON branded blood pressure cuffs to transmit their data to their physician without internet access.

## diy-BPM 

The diy-BPM folder contains the source code used for the analog to digital signal processing of the data produced by the NXP MPX2050 pressure transducer used in our diy blood pressure monitor solution.

## BLE Intercept 

Inital testing of this software kit was done using a Raspberry Pi 3 and Pi 4 to connect to OMRON devices BP7450 (aka OMRON M7) and the OMRON EVOLV. More OMRON devices are likely to be supported, but have not been confirmed yet. Please open an issue if you have any success with your OMRON device! On the GATT Client side, any Linux device with a bluetooth adapter should work. 

### Setup 
1. Create pairing keys between your OMRON device and your computer using the instructions in the omblepy repository: [omblepy](https://github.com/userx14/omblepy?tab=readme-ov-file#omblepy). Device must be paired before running any of this repository's scripts. If you've already done this, skip to step 4. 
2. If creating pairing keys for a device for the first time, hold down the bluetooth connect button on the OMRON device until the OMRON device's pairing screen appears.
3. Run python3 ./omblepy.py -p -d <insert HEM-XXXT device number here> in terminal to search for your device, and select it's MAC address in the terminal window.
4. Once initial pair complete (depending on device this should be an OK symbol or some variant of a paired symbol), device should now be paired and visible on your device's bluetooth list. If not, connect to device using python3 ./omblepy.py -p <insert HEM-XXXT device number here> to pair.
6. Power on the OMRON device and take a blood pressure measurement.
7. Before blood pressure measurement concludes (or in the ~1 minute after the measurement is taken and before the OMRON device goes to sleep), run gatt.py or dbus.py to capture the most recent blood pressure measurement. 
8. Once BP measurement is complete, script will continually poll for BP info and recorded data should be printed to terminal.

