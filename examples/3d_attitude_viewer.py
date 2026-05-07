#!/usr/bin/env python3
"""
ESP32 + BMI160 3D Aircraft Attitude Visualization
IMPROVED VERSION:
- Landed detection (acceleration norm near 1G)
- EMA low-pass filtering for gyro rates
- Continuous gyro bias estimation (only when landed)
- Ultra-low accel correction weight when landed
- Pure gyro integration when moving
"""

import sys
import time
import numpy as np

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
        # Attitude angles
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0

        # Time tracking
        self.last_time = time.time()

        # Serial
        self.ser = None
        self.data_count = 0

        # Gyro bias (estimated continuously when landed)
        self.gyro_bias = np.array([0.0, 0.0, 0.0])

        # Level calibration offsets
        self.init_roll = 0.0
        self.init_pitch = 0.0

        # EMA filtered gyro rates (low-pass)
        self.rate_x = 0.0
        self.rate_y = 0.0
        self.rate_z = 0.0
        self.rate_alpha = 0.2  # ~35Hz cutoff

        # Bias tracking alpha (very slow EMA)
        self.bias_alpha = 0.001

        # Acceleration smoothing (light)
        self.ax_avg = 0.0
        self.ay_avg = 0.0
        self.az_avg = 0.0

        # State
        self.landed = False
        self.calibrated = False

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


def quick_calibrate(ser):
    """Quick initial calibration"""
    print("\n" + "="*60)
    print("INITIAL CALIBRATION - KEEP STILL!")
    print("="*60)
    time.sleep(1)

    print("Collecting data...")
    gx_list, gy_list, gz_list = [], [], []
    ax_list, ay_list, az_list = [], [], []

    for i in range(300):
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

    if len(ax_list) < 100:
        print(f"Not enough data! Got {len(ax_list)}")
        return False

    state.gyro_bias[0] = np.mean(gx_list)
    state.gyro_bias[1] = np.mean(gy_list)
    state.gyro_bias[2] = np.mean(gz_list)

    ax_avg = np.mean(ax_list)
    ay_avg = np.mean(ay_list)
    az_avg = np.mean(az_list)
    state.init_roll = np.arctan2(ay_avg, az_avg)
    state.init_pitch = np.arctan2(-ax_avg, np.sqrt(ay_avg**2 + az_avg**2))

    state.ax_avg = ax_avg
    state.ay_avg = ay_avg
    state.az_avg = az_avg

    print(f"Gyro bias (deg/s): X={state.gyro_bias[0]:.2f}, Y={state.gyro_bias[1]:.2f}, Z={state.gyro_bias[2]:.2f}")
    print(f"Initial level: Roll={np.degrees(state.init_roll):.1f}deg, Pitch={np.degrees(state.init_pitch):.1f}deg")
    state.calibrated = True
    return True


def main():
    print("="*60)
    print("ESP32 + BMI160 3D Viewer (IMPROVED)")
    print("="*60)

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

    state.ser = ser

    # Quick initial calibration
    if not quick_calibrate(ser):
        print("Using default values...")
        state.gyro_bias = np.array([0.0, 0.0, 0.0])
        state.init_roll = 0.0
        state.init_pitch = 0.0

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
        ax_raw, ay_raw, az_raw = 0, 0, 1
        gx_raw, gy_raw, gz_raw = 0, 0, 0

        try:
            while ser.in_waiting > 0:
                line_bytes = ser.readline()
                line = line_bytes.decode('utf-8', errors='ignore').strip()
                data = line.split(',')
                if len(data) == 6:
                    # 加速度计原始值 (单位: g，即重力加速度的倍数)
                    # 静止平放时 ax≈0, ay≈0, az≈±1.0
                    ax_raw = float(data[0])  # X轴加速度: 前后方向
                    ay_raw = float(data[1])  # Y轴加速度: 左右方向
                    az_raw = float(data[2])  # Z轴加速度: 上下方向

                    # 陀螺仪原始值 (单位: deg/s，即度/秒)
                    # 静止时全部≈0，转动时变大，正负表示旋转方向
                    gx_raw = float(data[3])  # X轴角速度: 滚转速率 (roll rate)
                    gy_raw = float(data[4])  # Y轴角速度: 俯仰速率 (pitch rate)
                    gz_raw = float(data[5])  # Z轴角速度: 偏航速率 (yaw rate)
                    data_valid = True
                    state.data_count += 1
        except Exception as e:
            pass

        if data_valid:
            now = time.time()
            dt = now - state.last_time
            state.last_time = now

            # Step 1: EMA low-pass filter on gyro rates (remove vibration noise)
            state.rate_x += state.rate_alpha * (gx_raw - state.rate_x)
            state.rate_y += state.rate_alpha * (gy_raw - state.rate_y)
            state.rate_z += state.rate_alpha * (gz_raw - state.rate_z)

            # Step 2: Subtract bias
            gx = np.radians(state.rate_x - state.gyro_bias[0])
            gy = np.radians(state.rate_y - state.gyro_bias[1])
            gz = np.radians(state.rate_z - state.gyro_bias[2])

            # Step 3: Light smoothing on accelerometer
            state.ax_avg += 0.1 * (ax_raw - state.ax_avg)
            state.ay_avg += 0.1 * (ay_raw - state.ay_avg)
            state.az_avg += 0.1 * (az_raw - state.az_avg)

            # Step 4: Landed detection (accel norm near 1G)
            acc_norm = np.sqrt(state.ax_avg**2 + state.ay_avg**2 + state.az_avg**2)
            state.landed = abs(acc_norm - 1.0) < 0.1

            # Step 5: Pure gyro integration first
            state.roll += gx * dt
            state.pitch += gy * dt
            state.yaw += gz * dt

            # Step 6: When landed: update bias + ultra-light accel correction
            if state.landed:
                # Continuous gyro bias estimation (very slow EMA)
                state.gyro_bias[0] += state.bias_alpha * (state.rate_x - state.gyro_bias[0])
                state.gyro_bias[1] += state.bias_alpha * (state.rate_y - state.gyro_bias[1])
                state.gyro_bias[2] += state.bias_alpha * (state.rate_z - state.gyro_bias[2])

                # Calculate accel angles
                roll_a = np.arctan2(state.ay_avg, state.az_avg) - state.init_roll
                pitch_a = np.arctan2(-state.ax_avg, np.sqrt(state.ay_avg**2 + state.az_avg**2)) - state.init_pitch

                # Ultra-low weight correction towards accel angle (0.3%)
                acc_weight = 0.003
                state.roll += acc_weight * (roll_a - state.roll)
                state.pitch += acc_weight * (pitch_a - state.pitch)

        # Update aircraft
        for i, (points, _, _) in enumerate(model_lines):
            rotated = rotate_points(points, state.roll, state.pitch, state.yaw)
            aircraft_lines[i].set_data(rotated[:, 0], rotated[:, 1])
            aircraft_lines[i].set_3d_properties(rotated[:, 2])

        # Status text
        if not data_valid:
            status = "WAITING"
        elif state.landed:
            status = "LANDED"
        else:
            status = "MOVING"

        acc_norm = np.sqrt(state.ax_avg**2 + state.ay_avg**2 + state.az_avg**2)
        text_str = (
            f"Status: {status}\n"
            f"Data:   {state.data_count}\n"
            f"AccG:   {acc_norm:.2f}g\n\n"
            f"Roll:  {np.degrees(state.roll):+6.1f} deg\n"
            f"Pitch: {np.degrees(state.pitch):+6.1f} deg\n"
            f"Yaw:   {np.degrees(state.yaw):+6.1f} deg"
        )
        text_obj.set_text(text_str)

        return aircraft_lines + [text_obj]

    # 30毫秒调用一次update
    anim = animation.FuncAnimation(fig, update, interval=30, blit=False)
    print("\nVisualization started!")
    plt.show()


if __name__ == "__main__":
    main()
