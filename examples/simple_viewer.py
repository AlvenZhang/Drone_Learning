#!/usr/bin/env python3
"""
Simple 3D viewer - based on serial_test.py which works!
"""

import sys
import time
import numpy as np
from collections import deque

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("Error: Please install pyserial")
    sys.exit(1)

try:
    import matplotlib.pyplot as plt
    from matplotlib import animation
    from mpl_toolkits.mplot3d import Axes3D
except ImportError:
    print("Error: matplotlib not found")
    sys.exit(1)


class State:
    def __init__(self):
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.last_time = time.time()
        self.ser = None
        self.data_count = 0
        self.gyro_bias = np.array([0.0, 0.0, 0.0])
        self.init_roll = 0.0
        self.init_pitch = 0.0
        # Sliding window for gyro smoothing
        self.gx_buf = deque(maxlen=100)
        self.gy_buf = deque(maxlen=100)
        self.gz_buf = deque(maxlen=100)
        self.ax_buf = deque(maxlen=20)
        self.ay_buf = deque(maxlen=20)
        self.az_buf = deque(maxlen=20)

state = State()


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


def rotate_points(points, roll, pitch, yaw):
    cos_r = np.cos(roll)
    sin_r = np.sin(roll)
    cos_p = np.cos(pitch)
    sin_p = np.sin(pitch)
    cos_y = np.cos(yaw)
    sin_y = np.sin(yaw)
    Rx = np.array([[1,0,0],[0,cos_r,-sin_r],[0,sin_r,cos_r]])
    Ry = np.array([[cos_p,0,sin_p],[0,1,0],[-sin_p,0,cos_p]])
    Rz = np.array([[cos_y,-sin_y,0],[sin_y,cos_y,0],[0,0,1]])
    R = Rz @ Ry @ Rx
    return (R @ points.T).T


def make_aircraft():
    lines = []
    fus = np.array([[-1.2,0,0], [-0.8,0,0], [0.8,0,0], [1.0,0,0]])
    lines.append((fus, '#FF4444', 2.5))
    wing = np.array([[-0.4,-1.1,0], [-0.4,0,0], [-0.4,1.1,0]])
    lines.append((wing, '#4444FF', 2.5))
    vtail = np.array([[0.9,0,0], [0.9,0,0.4]])
    lines.append((vtail, '#44FF44', 2))
    htail = np.array([[0.9,-0.4,0], [0.9,0,0], [0.9,0.4,0]])
    lines.append((htail, '#44FF44', 2))
    return lines


def main():
    print("="*60)
    print("ESP32 + BMI160 3D Viewer (SIMPLE VERSION)")
    print("="*60)

    port_name = select_port()
    if not port_name:
        return

    try:
        ser = serial.Serial(port=port_name, baudrate=115200, timeout=0.1)
        print(f"\nConnected to {port_name}")
        time.sleep(0.5)
        ser.reset_input_buffer()
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    state.ser = ser

    # Calibration - SIMPLE VERSION
    print("\n" + "="*60)
    print("QUICK CALIBRATION - Keep STILL!")
    print("="*60)

    time.sleep(1)

    print("Collecting calibration data...")
    gx_list, gy_list, gz_list = [], [], []
    ax_list, ay_list, az_list = [], [], []

    for i in range(200):
        if ser.in_waiting > 0:
            line_bytes = ser.readline()
            line = line_bytes.decode('utf-8', errors='ignore').strip()
            data = line.split(',')
            if len(data) == 6:
                gx_list.append(float(data[3]))
                gy_list.append(float(data[4]))
                gz_list.append(float(data[5]))
                ax_list.append(float(data[0]))
                ay_list.append(float(data[1]))
                az_list.append(float(data[2]))
        time.sleep(0.005)

    if len(ax_list) < 50:
        print("Not enough data for calibration!")
    else:
        state.gyro_bias[0] = np.mean(gx_list)
        state.gyro_bias[1] = np.mean(gy_list)
        state.gyro_bias[2] = np.mean(gz_list)
        ax_avg = np.mean(ax_list)
        ay_avg = np.mean(ay_list)
        az_avg = np.mean(az_list)
        state.init_roll = np.arctan2(ay_avg, az_avg)
        state.init_pitch = np.arctan2(-ax_avg, np.sqrt(ay_avg**2 + az_avg**2))
        print(f"Gyro bias (deg/s): X={state.gyro_bias[0]:.2f}, Y={state.gyro_bias[1]:.2f}, Z={state.gyro_bias[2]:.2f}")
        print(f"Initial level: Roll={np.degrees(state.init_roll):.1f}deg, Pitch={np.degrees(state.init_pitch):.1f}deg")

    # Setup plot
    fig = plt.figure(figsize=(10, 8), facecolor='black')
    ax = fig.add_subplot(111, projection='3d', facecolor='black')
    ax.set_title('ESP32 + BMI160 3D Attitude Viewer', fontsize=14, color='white')
    ax.set_xlabel('X', color='white'), ax.set_ylabel('Y', color='white'), ax.set_zlabel('Z', color='white')
    ax.tick_params(colors='white')
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.set_xlim(-1.5,1.5), ax.set_ylim(-1.5,1.5), ax.set_zlim(-1.5,1.5)
    ax.set_aspect('equal')
    ax.view_init(elev=25, azim=-55)

    model_lines = make_aircraft()
    aircraft_lines = []
    for points, color, lw in model_lines:
        line, = ax.plot([], [], [], color=color, linewidth=lw)
        aircraft_lines.append(line)

    text_obj = ax.text2D(0.02, 0.98, '', transform=ax.transAxes, fontfamily='monospace',
                       verticalalignment='top', color='white')

    # Axis lines
    ax.plot([0,0.5], [0,0], [0,0], '#FF0000', linewidth=1)
    ax.plot([0,0], [0,0.5], [0,0], '#00FF00', linewidth=1)
    ax.plot([0,0], [0,0], [0,0.5], '#0000FF', linewidth=1)

    state.last_time = time.time()

    def update(frame):
        data_valid = False
        ax_val, ay_val, az_val = 0, 0, 1
        gx_val, gy_val, gz_val = 0, 0, 0

        try:
            # 最多读10行，防止因为某一行不完整导致整帧丢了
            read_attempts = 0
            while (ser.in_waiting > 0 or read_attempts < 3) and read_attempts < 10:
                read_attempts += 1
                line_bytes = ser.readline()
                if len(line_bytes) == 0:
                    continue  # 空行跳过

                line = line_bytes.decode('utf-8', errors='ignore').strip()
                data = line.split(',')
                if len(data) == 6:
                    ax_val = float(data[0])
                    ay_val = float(data[1])
                    az_val = float(data[2])
                    gx_val = np.radians(float(data[3]) - state.gyro_bias[0])
                    gy_val = np.radians(float(data[4]) - state.gyro_bias[1])
                    gz_val = np.radians(float(data[5]) - state.gyro_bias[2])

                    state.gx_buf.append(gx_val)
                    state.gy_buf.append(gy_val)
                    state.gz_buf.append(gz_val)
                    state.ax_buf.append(ax_val)
                    state.ay_buf.append(ay_val)
                    state.az_buf.append(az_val)

                    data_valid = True
                    state.data_count += 1
        except Exception as e:
            print(f"[DEBUG] Serial error: {e}")

        if data_valid:
            now = time.time()
            dt = now - state.last_time
            state.last_time = now

            gx_val = np.mean(state.gx_buf)
            gy_val = np.mean(state.gy_buf)
            gz_val = np.mean(state.gz_buf)
            ax_val = np.mean(state.ax_buf)
            ay_val = np.mean(state.ay_buf)
            az_val = np.mean(state.az_buf)

            dead_zone = np.radians(2.0)
            if abs(gx_val) < dead_zone:
                gx_val = 0.0
            if abs(gy_val) < dead_zone:
                gy_val = 0.0
            if abs(gz_val) < dead_zone:
                gz_val = 0.0

            roll_a = np.arctan2(ay_val, az_val)
            pitch_a = np.arctan2(-ax_val, np.sqrt(ay_val**2 + az_val**2))

            roll_g = state.roll + gx_val * dt
            pitch_g = state.pitch + gy_val * dt

            gyro_mag = abs(gx_val) + abs(gy_val) + abs(gz_val)
            alpha = 0.8 if gyro_mag < np.radians(2.0) else 0.97

            roll_raw = alpha * roll_g + (1 - alpha) * roll_a
            pitch_raw = alpha * pitch_g + (1 - alpha) * pitch_a

            state.roll = roll_raw - state.init_roll
            state.pitch = pitch_raw - state.init_pitch
            state.yaw = 0.0

        for i, (points, _, _) in enumerate(model_lines):
            rotated = rotate_points(points, state.roll, state.pitch, state.yaw)
            aircraft_lines[i].set_data(rotated[:, 0], rotated[:, 1])
            aircraft_lines[i].set_3d_properties(rotated[:, 2])

        status = "OK" if data_valid else "WAITING"
        text_str = f"Status: {status}\nData: {state.data_count}\n\nRoll: {np.degrees(state.roll):+6.1f} deg\nPitch: {np.degrees(state.pitch):+6.1f} deg\nYaw: {np.degrees(state.yaw):+6.1f} deg"
        text_obj.set_text(text_str)

        return aircraft_lines + [text_obj]

    anim = animation.FuncAnimation(fig, update, interval=30, blit=False)
    print("\nVisualization started!")
    plt.show()


if __name__ == "__main__":
    main()
