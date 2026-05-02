#!/usr/bin/env python3
"""
示例1: 悬停仿真
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.simulation import Simulator


def hover_controller(quadcopter, t):
    """悬停控制器"""
    # 获取当前高度 (ENU坐标系，z向上)
    z = quadcopter.get_position()[2]
    vz = quadcopter.get_velocity()[2]

    # 目标高度 5m
    z_target = 5.0

    # 简单的PD控制器
    kp = 5.0
    kd = 3.0

    # 误差计算：目标 - 当前
    error = z_target - z
    thrust = quadcopter.mass * quadcopter.g + kp * error + kd * (-vz)

    # 分配到四个电机
    motor_speeds_sq = np.ones(4) * thrust / 4.0

    return motor_speeds_sq


def main():
    print("Quadcopter Hover Simulation")
    print("=" * 40)

    # 创建仿真器
    sim = Simulator(dt=0.01)

    # 从地面开始
    sim.reset(position=np.array([0, 0, 0]))

    # 运行仿真
    print("Running simulation...")
    sim.run(duration=10.0, controller=hover_controller)

    # 获取轨迹
    traj = sim.get_trajectory()

    # 打印结果
    print(f"\nSimulation complete! Duration: {traj['time'][-1]:.2f}s")
    print(f"Final position: x={traj['position'][-1][0]:.3f}m, "
          f"y={traj['position'][-1][1]:.3f}m, "
          f"z={traj['position'][-1][2]:.3f}m")
    print(f"Target altitude: 5.0m")

    # 绘制轨迹
    try:
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(3, 1, figsize=(10, 8))

        # 位置
        axes[0].plot(traj['time'], traj['position'][:, 2], label='Altitude z')
        axes[0].axhline(y=5.0, color='r', linestyle='--', label='Target')
        axes[0].set_ylabel('Altitude (m)')
        axes[0].legend()
        axes[0].grid(True)

        # 速度
        axes[1].plot(traj['time'], traj['velocity'][:, 2], label='Vertical velocity vz')
        axes[1].set_ylabel('Velocity (m/s)')
        axes[1].legend()
        axes[1].grid(True)

        # 姿态
        axes[2].plot(traj['time'], np.rad2deg(traj['attitude'][:, 0]), label='Roll')
        axes[2].plot(traj['time'], np.rad2deg(traj['attitude'][:, 1]), label='Pitch')
        axes[2].plot(traj['time'], np.rad2deg(traj['attitude'][:, 2]), label='Yaw')
        axes[2].set_xlabel('Time (s)')
        axes[2].set_ylabel('Angle (deg)')
        axes[2].legend()
        axes[2].grid(True)

        plt.tight_layout()
        plt.savefig('data/hover_simulation.png')
        print(f"\nPlot saved to data/hover_simulation.png")

    except ImportError:
        print("\nTip: install matplotlib to plot results")
        print("Run: uv add matplotlib")


if __name__ == '__main__':
    main()
