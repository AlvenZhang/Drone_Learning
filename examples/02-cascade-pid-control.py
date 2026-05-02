#!/usr/bin/env python3
"""
示例2: 级联 PID 控制 (Cascade PID Control)

更接近真实飞控的控制架构：
- 外环：位置 → 速度 → 期望姿态角
- 内环：姿态角 → 角速度 → 力矩
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.simulation import Simulator
from src.control.pid import PIDController


class CascadePIDController:
    """级联 PID 控制器"""

    def __init__(self, quadcopter):
        self.quadcopter = quadcopter

        # ========== 外环：位置控制 ==========
        # Z 轴 (高度) 控制
        self.pos_z_pid = PIDController(kp=1.2, ki=0.0, kd=0.8, output_min=-5.0, output_max=5.0)
        self.vel_z_pid = PIDController(kp=5.0, ki=0.1, kd=1.5, output_min=-10.0, output_max=10.0)

        # X, Y 水平位置控制
        self.pos_x_pid = PIDController(kp=1.0, ki=0.0, kd=0.5, output_min=-4.0, output_max=4.0)
        self.vel_x_pid = PIDController(kp=3.0, ki=0.05, kd=1.0, output_min=-0.4, output_max=0.4)

        self.pos_y_pid = PIDController(kp=1.0, ki=0.0, kd=0.5, output_min=-4.0, output_max=4.0)
        self.vel_y_pid = PIDController(kp=3.0, ki=0.05, kd=1.0, output_min=-0.4, output_max=0.4)

        # ========== 内环：姿态控制 ==========
        # 姿态角控制 (Roll, Pitch, Yaw) - 限制在 +/-30度
        self.roll_pid = PIDController(kp=8.0, ki=0.0, kd=2.0, output_min=-3.0, output_max=3.0)
        self.pitch_pid = PIDController(kp=8.0, ki=0.0, kd=2.0, output_min=-3.0, output_max=3.0)
        self.yaw_pid = PIDController(kp=5.0, ki=0.05, kd=0.8, output_min=-2.0, output_max=2.0)

        # 角速度控制 (Body rates)
        self.rate_roll_pid = PIDController(kp=15.0, ki=1.0, kd=0.8, output_min=-5.0, output_max=5.0)
        self.rate_pitch_pid = PIDController(kp=15.0, ki=1.0, kd=0.8, output_min=-5.0, output_max=5.0)
        self.rate_yaw_pid = PIDController(kp=8.0, ki=0.5, kd=0.3, output_min=-3.0, output_max=3.0)

        # 目标
        self.target_pos = np.array([0.0, 0.0, 5.0])  # 目标位置
        self.target_yaw = 0.0  # 目标航向

    def set_target(self, x, y, z, yaw=0.0):
        """设置目标位置和航向"""
        self.target_pos = np.array([x, y, z])
        self.target_yaw = yaw

    def reset(self):
        """重置所有 PID 控制器"""
        for pid in [self.pos_z_pid, self.vel_z_pid,
                    self.pos_x_pid, self.vel_x_pid,
                    self.pos_y_pid, self.vel_y_pid,
                    self.roll_pid, self.pitch_pid, self.yaw_pid,
                    self.rate_roll_pid, self.rate_pitch_pid, self.rate_yaw_pid]:
            pid.reset()

    def compute(self, dt):
        """
        计算控制量

        返回: thrust, tau_phi, tau_theta, tau_psi
        """
        # 获取当前状态
        pos = self.quadcopter.get_position()
        vel = self.quadcopter.get_velocity()
        att = self.quadcopter.get_attitude()  # phi, theta, psi
        rates = self.quadcopter.get_angular_rates()  # p, q, r

        # ========== 1. 高度控制 (Z轴) ==========
        # 位置误差 → 期望速度
        z_error = self.target_pos[2] - pos[2]
        target_vz = self.pos_z_pid.compute(z_error, dt)

        # 速度误差 → 期望推力增量
        vz_error = target_vz - vel[2]
        thrust_delta = self.vel_z_pid.compute(vz_error, dt)

        # 总推力 = 悬停推力 + 增量
        hover_thrust = self.quadcopter.mass * self.quadcopter.g
        thrust = hover_thrust + thrust_delta
        # 推力限幅
        thrust = np.clip(thrust, 0.2 * hover_thrust, 2.0 * hover_thrust)

        # ========== 2. 水平位置控制 (X, Y) ==========
        # X 轴
        x_error = self.target_pos[0] - pos[0]
        target_vx = self.pos_x_pid.compute(x_error, dt)
        vx_error = target_vx - vel[0]
        target_pitch = -self.vel_x_pid.compute(vx_error, dt)  # 负号：向前飞需要低头
        target_pitch = np.clip(target_pitch, -0.3, 0.3)  # 限幅 30度

        # Y 轴
        y_error = self.target_pos[1] - pos[1]
        target_vy = self.pos_y_pid.compute(y_error, dt)
        vy_error = target_vy - vel[1]
        target_roll = self.vel_y_pid.compute(vy_error, dt)  # 向右飞需要右滚
        target_roll = np.clip(target_roll, -0.3, 0.3)  # 限幅 30度

        # ========== 3. 姿态控制 ==========
        # 姿态角误差 → 期望角速度
        roll_error = target_roll - att[0]
        target_p = self.roll_pid.compute(roll_error, dt)

        pitch_error = target_pitch - att[1]
        target_q = self.pitch_pid.compute(pitch_error, dt)

        yaw_error = self.target_yaw - att[2]
        # 将角度误差归一化到 [-pi, pi]
        yaw_error = np.arctan2(np.sin(yaw_error), np.cos(yaw_error))
        target_r = self.yaw_pid.compute(yaw_error, dt)

        # ========== 4. 角速度控制 ==========
        # 角速度误差 → 力矩
        p_error = target_p - rates[0]
        tau_phi = self.rate_roll_pid.compute(p_error, dt)

        q_error = target_q - rates[1]
        tau_theta = self.rate_pitch_pid.compute(q_error, dt)

        r_error = target_r - rates[2]
        tau_psi = self.rate_yaw_pid.compute(r_error, dt)

        return thrust, tau_phi, tau_theta, tau_psi


def moving_trajectory(controller, t):
    """生成移动轨迹"""
    if t < 5.0:
        # 0-5s: 起飞到 5m
        controller.set_target(0, 0, 5)
    elif t < 15.0:
        # 5-15s: 飞一个小圆圈
        phase = 0.5 * (t - 5.0)
        radius = 2.0
        x = radius * np.cos(phase) - radius
        y = radius * np.sin(phase)
        controller.set_target(x, y, 5)
    else:
        # 15s+: 返回原点
        controller.set_target(0, 0, 5)


def main():
    print("Cascade PID Control Demo")
    print("=" * 50)

    # 创建仿真器
    sim = Simulator(dt=0.005)  # 5ms 控制周期，更接近真实飞控

    # 创建级联 PID 控制器
    controller = CascadePIDController(sim.quadcopter)

    # 定义控制回调
    last_t = 0.0
    def control_callback(quadcopter, t):
        nonlocal last_t
        dt = t - last_t
        if dt < 1e-6:
            dt = 1e-6
        last_t = t

        # 更新轨迹
        moving_trajectory(controller, t)

        # 计算控制量
        thrust, tau_phi, tau_theta, tau_psi = controller.compute(dt)

        # 混控
        return quadcopter.motor_mixing(thrust, tau_phi, tau_theta, tau_psi)

    # 运行仿真
    print("Running simulation...")
    sim.reset(position=np.array([0, 0, 0]))
    sim.run(duration=20.0, controller=control_callback)

    # 获取轨迹
    traj = sim.get_trajectory()

    print(f"\nSimulation complete! Duration: {traj['time'][-1]:.1f}s")
    final_pos = traj['position'][-1]
    print(f"Final position: x={final_pos[0]:.2f}m, "
          f"y={final_pos[1]:.2f}m, "
          f"z={final_pos[2]:.2f}m")

    # 绘制结果
    try:
        import matplotlib.pyplot as plt

        fig = plt.figure(figsize=(14, 10))

        # 1. 3D 轨迹
        ax1 = fig.add_subplot(2, 2, 1, projection='3d')
        ax1.plot(traj['position'][:, 0], traj['position'][:, 1], traj['position'][:, 2], label='Trajectory')
        ax1.scatter(0, 0, 5, c='red', marker='o', label='Target')
        ax1.set_xlabel('X (m)')
        ax1.set_ylabel('Y (m)')
        ax1.set_zlabel('Z (m)')
        ax1.set_title('3D Flight Path')
        ax1.legend()

        # 2. 位置追踪
        ax2 = fig.add_subplot(2, 2, 2)
        ax2.plot(traj['time'], traj['position'][:, 0], label='X')
        ax2.plot(traj['time'], traj['position'][:, 1], label='Y')
        ax2.plot(traj['time'], traj['position'][:, 2], label='Z')
        ax2.axhline(y=5, c='k', ls='--', label='Target Z')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Position (m)')
        ax2.set_title('Position vs Time')
        ax2.legend()
        ax2.grid(True)

        # 3. 姿态
        ax3 = fig.add_subplot(2, 2, 3)
        ax3.plot(traj['time'], np.rad2deg(traj['attitude'][:, 0]), label='Roll')
        ax3.plot(traj['time'], np.rad2deg(traj['attitude'][:, 1]), label='Pitch')
        ax3.plot(traj['time'], np.rad2deg(traj['attitude'][:, 2]), label='Yaw')
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Angle (deg)')
        ax3.set_title('Attitude vs Time')
        ax3.legend()
        ax3.grid(True)

        # 4. 电机转速
        ax4 = fig.add_subplot(2, 2, 4)
        motor_history = np.array(sim.history['motor_speeds'])
        for i in range(4):
            ax4.plot(traj['time'], motor_history[:, i], label=f'Motor {i+1}')
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Motor speed squared (a.u.)')
        ax4.set_title('Motor Commands')
        ax4.legend()
        ax4.grid(True)

        plt.tight_layout()
        plt.savefig('data/cascade_pid_demo.png', dpi=150)
        print(f"\nPlot saved to data/cascade_pid_demo.png")

    except ImportError:
        print("\nTip: install matplotlib to plot results")


if __name__ == '__main__':
    main()
