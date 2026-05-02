#!/usr/bin/env python3
"""
示例2: 简化版级联 PID 控制

先实现稳定的悬停，不添加太激进的运动
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.simulation import Simulator
from src.control.pid import PIDController


class SimpleCascadeController:
    """简化的级联 PID 控制器"""

    def __init__(self, quadcopter):
        self.quadcopter = quadcopter

        # 高度控制
        self.altitude_pid = PIDController(kp=3.0, ki=0.1, kd=2.0, output_min=-5.0, output_max=8.0)

        # 姿态角控制 (Roll, Pitch, Yaw) - 更保守的参数
        self.roll_pid = PIDController(kp=4.0, ki=0.0, kd=1.0, output_min=-1.5, output_max=1.5)
        self.pitch_pid = PIDController(kp=4.0, ki=0.0, kd=1.0, output_min=-1.5, output_max=1.5)
        self.yaw_pid = PIDController(kp=2.0, ki=0.0, kd=0.5, output_min=-1.0, output_max=1.0)

        # 角速度控制 - 降低增益
        self.rate_roll_pid = PIDController(kp=8.0, ki=0.5, kd=0.3, output_min=-2.0, output_max=2.0)
        self.rate_pitch_pid = PIDController(kp=8.0, ki=0.5, kd=0.3, output_min=-2.0, output_max=2.0)
        self.rate_yaw_pid = PIDController(kp=5.0, ki=0.3, kd=0.2, output_min=-1.5, output_max=1.5)

        self.target_z = 5.0
        self.target_yaw = 0.0

    def reset(self):
        for pid in [self.altitude_pid,
                    self.roll_pid, self.pitch_pid, self.yaw_pid,
                    self.rate_roll_pid, self.rate_pitch_pid, self.rate_yaw_pid]:
            pid.reset()

    def compute(self, dt):
        """计算控制量"""
        pos = self.quadcopter.get_position()
        vel = self.quadcopter.get_velocity()
        att = self.quadcopter.get_attitude()
        rates = self.quadcopter.get_angular_rates()

        # 1. 高度控制
        z_error = self.target_z - pos[2]
        vz_error = 0.0 - vel[2]
        thrust_delta = self.altitude_pid.compute(z_error, dt) + 1.5 * vz_error
        hover_thrust = self.quadcopter.mass * self.quadcopter.g
        thrust = hover_thrust + thrust_delta
        thrust = np.clip(thrust, 0.3 * hover_thrust, 1.8 * hover_thrust)

        # 2. 姿态控制 - 保持水平
        target_roll = 0.0
        target_pitch = 0.0

        # 姿态角 → 目标角速度
        roll_error = target_roll - att[0]
        target_p = self.roll_pid.compute(roll_error, dt)

        pitch_error = target_pitch - att[1]
        target_q = self.pitch_pid.compute(pitch_error, dt)

        yaw_error = self.target_yaw - att[2]
        yaw_error = np.arctan2(np.sin(yaw_error), np.cos(yaw_error))
        target_r = self.yaw_pid.compute(yaw_error, dt)

        # 3. 角速度 → 力矩
        p_error = target_p - rates[0]
        tau_phi = self.rate_roll_pid.compute(p_error, dt)

        q_error = target_q - rates[1]
        tau_theta = self.rate_pitch_pid.compute(q_error, dt)

        r_error = target_r - rates[2]
        tau_psi = self.rate_yaw_pid.compute(r_error, dt)

        return thrust, tau_phi, tau_theta, tau_psi


def main():
    print("Simple Cascade PID Demo (Hover Only)")
    print("=" * 50)

    sim = Simulator(dt=0.01)
    controller = SimpleCascadeController(sim.quadcopter)

    last_t = 0.0
    def control_callback(quadcopter, t):
        nonlocal last_t
        dt = max(t - last_t, 0.001)
        last_t = t
        thrust, tau_phi, tau_theta, tau_psi = controller.compute(dt)
        return quadcopter.motor_mixing(thrust, tau_phi, tau_theta, tau_psi)

    print("Running simulation...")
    sim.reset(position=np.array([0, 0, 0]))
    sim.run(duration=15.0, controller=control_callback)

    traj = sim.get_trajectory()
    print(f"\nFinal position: x={traj['position'][-1][0]:.3f}m, "
          f"y={traj['position'][-1][1]:.3f}m, "
          f"z={traj['position'][-1][2]:.3f}m")

    try:
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(3, 1, figsize=(12, 9))

        axes[0].plot(traj['time'], traj['position'][:, 2], label='Altitude')
        axes[0].axhline(5, c='r', ls='--', label='Target')
        axes[0].set_ylabel('Z (m)')
        axes[0].legend()
        axes[0].grid(True)

        axes[1].plot(traj['time'], np.rad2deg(traj['attitude'][:, 0]), label='Roll')
        axes[1].plot(traj['time'], np.rad2deg(traj['attitude'][:, 1]), label='Pitch')
        axes[1].plot(traj['time'], np.rad2deg(traj['attitude'][:, 2]), label='Yaw')
        axes[1].set_ylabel('Angle (deg)')
        axes[1].legend()
        axes[1].grid(True)

        axes[2].plot(traj['time'], np.array(sim.history['motor_speeds']))
        axes[2].set_xlabel('Time (s)')
        axes[2].set_ylabel('Motor commands')
        axes[2].grid(True)

        plt.tight_layout()
        plt.savefig('data/simple_cascade.png')
        print("\nPlot saved to data/simple_cascade.png")
    except ImportError:
        pass


if __name__ == '__main__':
    main()
