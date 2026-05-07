#!/usr/bin/env python3
"""
Test serial communication only - no GUI
"""
import time
import serial

port_name = "/dev/cu.usbserial-0001"
print(f"Connecting to {port_name}...")

try:
    ser = serial.Serial(port_name, 115200, timeout=0.1)
    # DTR/RTS control for CP210x chips
    ser.dtr = True
    ser.rts = True
    print(f"Connected!")
    time.sleep(0.5)
    ser.reset_input_buffer()
except Exception as e:
    print(f"Failed to connect: {e}")
    exit(1)

print("\nReading serial data for 5 seconds...\n")
count = 0
start_time = time.time()

while time.time() - start_time < 5:
    if ser.in_waiting > 0:
        line_bytes = ser.readline()
        line = line_bytes.decode('utf-8', errors='ignore').strip()
        if line:
            count += 1
            if count <= 10:
                print(f"[{count}] {line}")
            elif count == 11:
                print("... (more data)")
    else:
        time.sleep(0.001)

print(f"\nTotal lines received: {count}")
print(f"Rate: {count/5:.1f} lines/sec")
