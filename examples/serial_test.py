#!/usr/bin/env python3
"""
ESP32串口通信测试程序
用于测试ESP32和Python之间的串口连接
"""

import sys
import time
import glob
from datetime import datetime

# 尝试导入pyserial
try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("错误: 请先安装pyserial库！")
    print("运行: uv add pyserial")
    sys.exit(1)


def list_serial_ports():
    """列出所有可用的串口"""
    ports = serial.tools.list_ports.comports()

    if not ports:
        print("没有找到可用的串口！")
        print("请检查:")
        print("  1. ESP32是否连接？")
        print("  2. USB数据线是否连接？")
        return []

    print(f"\n找到 {len(ports)} 个可用串口:")
    for i, port in enumerate(ports):
        print(f"  [{i+1}] {port.device}")
        print(f"      描述: {port.description}")
        print(f"      硬件: {port.hwid}")

    return ports


def select_serial_port():
    """让用户选择串口"""
    ports = list_serial_ports()
    if not ports:
        return None

    while True:
        try:
            choice = input("\n请选择串口号 (1-{}), 或按q退出: ".format(len(ports)))

            if choice.lower() == 'q':
                return None

            idx = int(choice) - 1
            if 0 <= idx < len(ports):
                return ports[idx].device
            else:
                print(f"请输入1到{len(ports)}之间的数字！")
        except ValueError:
            print("请输入数字！")
        except KeyboardInterrupt:
            print("\n用户取消")
            return None


def read_serial_data(port_name):
    """从串口读取数据"""
    try:
        ser = serial.Serial(
            port=port_name,
            baudrate=115200,
            timeout=0.1
        )
        print(f"\n成功连接到 {port_name}")
        print("按 Ctrl+C 停止...\n")

        # 等待串口稳定
        time.sleep(0.5)

        # 清空输入缓冲区
        ser.reset_input_buffer()

        # 统计数据
        start_time = time.time()
        line_count = 0

        while True:
            # 检查是否有数据
            if ser.in_waiting > 0:
                # 读取一行
                try:
                    line_bytes = ser.readline()
                    line = line_bytes.decode('utf-8').strip()

                    if line:
                        # 解析CSV
                        data = line.split(',')

                        if len(data) == 6:
                            # 成功解析
                            try:
                                ax = float(data[0])
                                ay = float(data[1])
                                az = float(data[2])
                                gx = float(data[3])
                                gy = float(data[4])
                                gz = float(data[5])

                                line_count += 1

                                # 计算刷新率
                                elapsed = time.time() - start_time
                                if elapsed > 0:
                                    fps = line_count / elapsed
                                else:
                                    fps = 0

                                # 打印格式化的数据
                                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                                print(f"[{timestamp}] Accel: {ax:+.3f}, {ay:+.3f}, {az:+.3f} | "
                                      f"Gyro: {gx:+.1f}, {gy:+.1f}, {gz:+.1f} | "
                                      f"FPS: {fps:.1f}", end='\r')

                            except ValueError:
                                print(f"解析失败: {line}")
                        else:
                            print(f"数据格式错误: {line}")

                except UnicodeDecodeError:
                    print(f"解码错误: {line_bytes}")
                except Exception as e:
                    print(f"读取错误: {e}")

            # 简短延时，避免CPU占用过高
            time.sleep(0.001)

    except serial.SerialException as e:
        print(f"\n串口错误: {e}")
    except KeyboardInterrupt:
        print("\n\n用户停止")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print(f"串口已关闭，共收到 {line_count} 条数据")


def main():
    print("="*60)
    print("ESP32 串口测试程序")
    print("="*60)

    port_name = select_serial_port()
    if port_name:
        read_serial_data(port_name)


if __name__ == "__main__":
    main()
