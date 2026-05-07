#!/usr/bin/env python3
"""
Analyze gyro log
"""

import csv
import numpy as np

with open('gyro_log.csv', 'r') as f:
    reader = csv.DictReader(f)
    data = list(reader)

gx = [float(row['gx']) for row in data]
gy = [float(row['gy']) for row in data]
gz = [float(row['gz']) for row in data]

print("="*60)
print("GYRO DATA ANALYSIS")
print("="*60)
print(f"Total samples: {len(data)}")
print()
print(f"gx: min={min(gx):.1f}, max={max(gx):.1f}, mean={np.mean(gx):.1f}, std={np.std(gx):.1f}")
print(f"gy: min={min(gy):.1f}, max={max(gy):.1f}, mean={np.mean(gy):.1f}, std={np.std(gy):.1f}")
print(f"gz: min={min(gz):.1f}, max={max(gz):.1f}, mean={np.mean(gz):.1f}, std={np.std(gz):.1f}")
print()
print("="*60)
print("THESE VALUES SEEM TO BE RAW REGISTER COUNTS, NOT deg/s!")
print("="*60)
print()
print("If they were raw counts:")
print(f"  gx bias would be: {np.mean(gx)/16.4:.2f} deg/s")
print(f"  gy bias would be: {np.mean(gy)/16.4:.2f} deg/s")
print(f"  gz bias would be: {np.mean(gz)/16.4:.2f} deg/s")
print()
print("But wait — these values are too large!")
print("Maybe DFRobot_BMI160 library already converts to deg/s internally?")
print("Or maybe the sensor range is different?")
