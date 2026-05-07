#!/usr/bin/env python3
"""
Raw gyro data test - check if yaw (gz) has bias drift
"""

import sys
import time
import csv
from datetime import datetime

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("Error: Please install pyserial")
    sys.exit(1)


def list_ports():
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No ports found!")
        return []

    print(f"\nFound {len(ports)} ports:")
    for i, p in enumerate(ports):
        print(f"  [{i+1}] {p.device}")
    return ports


def select_port():
    ports = list_ports()
    if not ports:
        return None

    while True:
        try:
            choice = input("\nSelect port (1-{}): ".format(len(ports)))
            idx = int(choice) - 1
            if 0 <= idx < len(ports):
                return ports[idx].device
        except KeyboardInterrupt:
            break
        except:
            pass
    return None


def main():
    print("="*60)
    print("GYRO TEST - Raw Data Viewer")
    print("="*60)
    print("Displays raw gyro X/Y/Z in deg/s")
    print("Note: Keep sensor STILL to check bias")
    print("Press Ctrl+C to stop\n")

    port_name = select_port()
    if not port_name:
        return

    try:
        ser = serial.Serial(port_name, 115200, timeout=0.1)
        print(f"\nConnected to {port_name}")
        time.sleep(0.5)
        ser.reset_input_buffer()
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    # Save to CSV for later analysis
    save_csv = input("\nSave data to gyro_log.csv? (y/n): ").strip().lower() == 'y'
    csv_file = None
    csv_writer = None

    if save_csv:
        csv_file = open('gyro_log.csv', 'w', newline='')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['timestamp', 'ax', 'ay', 'az', 'gx', 'gy', 'gz'])

    print("\n" + "="*80)
    print(f"{'Time':<12} {'gx(deg/s)':>10} {'gy(deg/s)':>10} {'gz(deg/s)':>10}  |  {'acc_norm':>8}")
    print("="*80)

    line_count = 0
    start_time = time.time()

    try:
        while True:
            if ser.in_waiting > 0:
                line_bytes = ser.readline()
                line = line_bytes.decode('utf-8', errors='ignore').strip()
                data = line.split(',')

                if len(data) == 6:
                    ax = float(data[0])
                    ay = float(data[1])
                    az = float(data[2])
                    gx = float(data[3])
                    gy = float(data[4])
                    gz = float(data[5])

                    line_count += 1
                    elapsed = time.time() - start_time
                    fps = line_count / elapsed if elapsed > 0 else 0

                    # Calculate acc norm (should be ~1 when stationary)
                    acc_norm = (ax**2 + ay**2 + az**2)**0.5

                    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

                    print(f"{timestamp:<12} {gx:>+10.2f} {gy:>+10.2f} {gz:>+10.2f}  |  {acc_norm:>8.2f}",
                          end='\r')

                    if save_csv:
                        csv_writer.writerow([timestamp, ax, ay, az, gx, gy, gz])

            time.sleep(0.001)

    except KeyboardInterrupt:
        print("\n" + "="*80)
        print(f"\nStopped. Total lines: {line_count}")
        print(f"Average rate: {line_count/(time.time()-start_time):.1f} Hz")
    finally:
        if csv_file:
            csv_file.close()
            print("Data saved to gyro_log.csv")
        ser.close()


if __name__ == "__main__":
    main()
