#!/usr/bin/env python3
"""
测试基础稳定性：只用简单的高度控制 + 阻尼
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.simulation import Simulator


def basic_controller(quadcopter, t):
    """基础稳定控制器"""
    # 获取状态
    z = quadcopter.get_position()[2]
    vz = quadcopter.get_velocity()[2]
    phi, theta, psi = quadcopter.get_attitude()
    p, q, r = quadcopter.get_angular_rates()

    # 悬停推力
    hover_thrust = quadcopter.mass * quadcopter.g

    # 高度控制
    z_target = 3.0
    kp_z = 2.0
    kd_z = 1.5
    thrust = hover_thrust + kp_z * (z_target - z) + kd_z * (-vz)
    thrust = np.clip(thrust, 0.2 * hover_thrust, 1.5 * hover_thrust)

    # 姿态阻尼：简单的比例-微分控制来保持水平
    kp_att = 3.0
    kd_att = 0.8

    tau_phi = -kp_att * phi - kd_att * p
    tau_theta = -kp_att * theta - kd_att * q
    tau_psi = -0.5 * psi - 0.3 * r

    # 限幅
    tau_phi = np.clip(tau_phi, -1.0, 1.0)
    tau_theta = np.clip(tau_theta, -1.0, 1.0)
    tau_psi = np.clip(tau_psi, -0.5, 0.5)

    return quadcopter.motor_mixing(thrust, tau_phi, tau_theta, tau_psi)


def main():
    print("Basic Stability Test")
    print("=" * 40)

    sim = Simulator(dt=0.01)
    print("Running simulation...")
    sim.reset(position=np.array([0, 0, 0]))
    sim.run(duration=10.0, controller=basic_controller)

    traj = sim.get_trajectory()
    print(f"\nFinal position: x={traj['position'][-1][0]:.3f}m, "
          f"y={traj['position'][-1][1]:.3f}m, "
          f"z={traj['position'][-1][2]:.3f}m")

    try:
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))

        axes[0,0].plot(traj['time'], traj['position'][:, 2])
        axes[0,0].axhline(3, c='r', ls='--')
        axes[0,0].set_ylabel('Altitude (m)')
        axes[0,0].grid(True)

        axes[0,1].plot(traj['time'], np.rad2deg(traj['attitude'][:, 0]), label='Roll')
        axes[0,1].plot(traj['time'], np.rad2deg(traj['attitude'][:, 1]), label='Pitch')
        axes[0,1].set_ylabel('Angle (deg)')
        axes[0,1].legend()
        axes[0,1].grid(True)

        axes[1,0].plot(traj['time'], traj['velocity'][:, 2])
        axes[1,0].set_ylabel('Vz (m/s)')
        axes[1,0].grid(True)

        axes[1,1].plot(traj['time'], np.array(sim.history['motor_speeds']))
        axes[1,1].set_ylabel('Motor commands')
        axes[1,1].grid(True)

        plt.tight_layout()
        plt.savefig('data/basic_stability.png')
        print("\nPlot saved to data/basic_stability.png")
    except ImportError:
        pass


if __name__ == '__main__':
    main()
