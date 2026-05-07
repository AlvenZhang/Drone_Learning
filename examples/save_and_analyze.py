#!/usr/bin/env python3
"""
Save serial data and analyze
"""
import time
import serial
import csv
import numpy as np

port_name = "/dev/cu.usbserial-0001"
print(f"Connecting to {port_name}...")

try:
    ser = serial.Serial(port=port_name, baudrate=115200, timeout=0.1)
    print(f"Connected!")
    time.sleep(0.5)
    ser.reset_input_buffer()
except Exception as e:
    print(f"Failed to connect: {e}")
    exit(1)

print("\nCollecting data for 5 seconds...\n")

data_list = []
start_time = time.time()
count = 0

while time.time() - start_time < 5:
    if ser.in_waiting > 0:
        line_bytes = ser.readline()
        line = line_bytes.decode('utf-8', errors='ignore').strip()
        if line:
            try:
                parts = line.split(',')
                if len(parts) == 6:
                    ax = float(parts[0])
                    ay = float(parts[1])
                    az = float(parts[2])
                    gx = float(parts[3])
                    gy = float(parts[4])
                    gz = float(parts[5])
                    data_list.append((ax, ay, az, gx, gy, gz))
                    count += 1
                    if count <= 10:
                        print(f"[{count}] ax={ax:.3f}, ay={ay:.3f}, az={az:.3f}, gx={gx:.2f}, gy={gy:.2f}, gz={gz:.2f}")
                    elif count == 11:
                        print("... (more data)")
            except:
                pass
    else:
        time.sleep(0.001)

ser.close()

# Save to CSV
with open('/Users/alven/code/Drone_Learning/sensor_data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ax', 'ay', 'az', 'gx', 'gy', 'gz'])
    writer.writerows(data_list)

# Analysis
print("\n" + "="*60)
print("DATA ANALYSIS")
print("="*60)
print(f"Total samples: {len(data_list)}")
print(f"Sample rate: {len(data_list)/5:.1f} Hz")

if len(data_list) > 0:
    data = np.array(data_list)
    ax, ay, az = data[:, 0], data[:, 1], data[:, 2]
    gx, gy, gz = data[:, 3], data[:, 4], data[:, 5]

    print("\nAccelerometer (g):")
    print(f"  ax: mean={np.mean(ax):.3f}, std={np.std(ax):.3f}, min={np.min(ax):.3f}, max={np.max(ax):.3f}")
    print(f"  ay: mean={np.mean(ay):.3f}, std={np.std(ay):.3f}, min={np.min(ay):.3f}, max={np.max(ay):.3f}")
    print(f"  az: mean={np.mean(az):.3f}, std={np.std(az):.3f}, min={np.min(az):.3f}, max={np.max(az):.3f}")

    acc_norm = np.sqrt(ax**2 + ay**2 + az**2)
    print(f"  norm: mean={np.mean(acc_norm):.3f}g (should be ~1.0g when stationary)")

    print("\nGyro (deg/s):")
    print(f"  gx: mean={np.mean(gx):.2f}, std={np.std(gx):.2f}, min={np.min(gx):.2f}, max={np.max(gx):.2f}")
    print(f"  gy: mean={np.mean(gy):.2f}, std={np.std(gy):.2f}, min={np.min(gy):.2f}, max={np.max(gy):.2f}")
    print(f"  gz: mean={np.mean(gz):.2f}, std={np.std(gz):.2f}, min={np.min(gz):.2f}, max={np.max(gz):.2f}")

    print("\n" + "="*60)
    if np.mean(acc_norm) > 0.8 and np.mean(acc_norm) < 1.2:
        print("✅ Accelerometer values LOOK CORRECT (norm ~ 1.0g)")
    else:
        print("❌ Accelerometer values may be wrong")

    if np.abs(np.mean(gx)) < 5 and np.abs(np.mean(gy)) < 5 and np.abs(np.mean(gz)) < 5:
        print("✅ Gyro bias looks reasonable (< 5 deg/s when stationary)")
    else:
        print("⚠️  Gyro bias seems high (should be near 0 when stationary)")
    print("="*60)
else:
    print("\n❌ No data received!")
    print("Please check:")
    print("  1. ESP32 is powered on")
    print("  2. Arduino Serial Monitor is CLOSED")
    print("  3. Correct sketch is uploaded to ESP32")
