"""
四旋翼无人机仿真模型
使用 ENU 坐标系（东-北-上）
"""
import numpy as np
from typing import Tuple


class Quadcopter:
    """四旋翼无人机类"""

    def __init__(self, mass=1.0, arm_length=0.25):
        """
        初始化四旋翼

        参数:
            mass: 无人机质量 (kg)
            arm_length: 机臂长度 (m)
        """
        self.mass = mass
        self.arm_length = arm_length

        # 状态向量 [x, y, z, vx, vy, vz, phi, theta, psi, p, q, r]
        # ENU 坐标系：x=东, y=北, z=上
        self.state = np.zeros(12)

        # 重力加速度 (向下，所以在 ENU 中是负 z 方向)
        self.g = 9.81

        # 转动惯量 (简化模型)
        self.Ixx = 0.01
        self.Iyy = 0.01
        self.Izz = 0.02

    def reset(self, position=None):
        """重置无人机状态"""
        self.state = np.zeros(12)
        if position is not None:
            self.state[0:3] = position

    def get_position(self) -> np.ndarray:
        """获取位置"""
        return self.state[0:3]

    def get_velocity(self) -> np.ndarray:
        """获取速度"""
        return self.state[3:6]

    def get_attitude(self) -> np.ndarray:
        """获取姿态 (phi, theta, psi)"""
        return self.state[6:9]

    def get_angular_rates(self) -> np.ndarray:
        """获取角速度"""
        return self.state[9:12]

    def motor_mixing(self, thrust, tau_phi, tau_theta, tau_psi) -> np.ndarray:
        """
        将期望的推力和力矩转换为四个电机的转速平方

        电机布局 (X形，机头沿y轴向前):
            1      2
             |    |
              --  y (北)
             |    |
            4      3
          x (东)

        参数:
            thrust: 总推力
            tau_phi: 滚转力矩
            tau_theta: 俯仰力矩
            tau_psi: 偏航力矩

        返回:
            四个电机的转速平方 [w1^2, w2^2, w3^2, w4^2]
        """
        l = self.arm_length
        kf = 1.0  # 推力系数
        km = 0.1  # 力矩系数

        # 混控矩阵 (X形布局)
        mixer = np.array([
            [1/(4*kf),  1/(4*kf*l),  1/(4*kf*l), -1/(4*km)],
            [1/(4*kf), -1/(4*kf*l),  1/(4*kf*l),  1/(4*km)],
            [1/(4*kf), -1/(4*kf*l), -1/(4*kf*l), -1/(4*km)],
            [1/(4*kf),  1/(4*kf*l), -1/(4*kf*l),  1/(4*km)]
        ])

        inputs = np.array([thrust, tau_phi, tau_theta, tau_psi])
        return mixer @ inputs

    def step(self, motor_speeds_sq: np.ndarray, dt: float):
        """
        执行一步仿真

        参数:
            motor_speeds_sq: 四个电机的转速平方
            dt: 时间步长 (s)
        """
        kf = 1.0  # 推力系数
        km = 0.1  # 力矩系数
        l = self.arm_length

        # 电机限幅：不能为负，也不能过大
        motor_min = 0.0
        motor_max = 2 * self.mass * self.g  # 最大总推力约为 2 倍重力
        motor_speeds_sq = np.clip(motor_speeds_sq, motor_min, motor_max / 4.0)

        # 计算每个电机的推力
        thrusts = kf * motor_speeds_sq

        # 总推力 (沿机体 z 轴向上)
        total_thrust = np.sum(thrusts)

        # 计算力矩
        tau_phi = l * (thrusts[0] + thrusts[3] - thrusts[1] - thrusts[2])
        tau_theta = l * (thrusts[0] + thrusts[1] - thrusts[2] - thrusts[3])
        tau_psi = km * (thrusts[0] + thrusts[2] - thrusts[1] - thrusts[3])

        # 获取当前状态
        x, y, z, vx, vy, vz, phi, theta, psi, p, q, r = self.state

        # 旋转矩阵（从机体坐标系到 ENU 地面坐标系）
        c_phi = np.cos(phi)
        s_phi = np.sin(phi)
        c_theta = np.cos(theta)
        s_theta = np.sin(theta)
        c_psi = np.cos(psi)
        s_psi = np.sin(psi)

        R = np.array([
            [c_theta*c_psi, s_phi*s_theta*c_psi - c_phi*s_psi, c_phi*s_theta*c_psi + s_phi*s_psi],
            [c_theta*s_psi, s_phi*s_theta*s_psi + c_phi*c_psi, c_phi*s_theta*s_psi - s_phi*c_psi],
            [-s_theta, s_phi*c_theta, c_phi*c_theta]
        ])

        # 机体坐标系下的推力向量 (向上为正 z)
        thrust_body = np.array([0, 0, total_thrust])

        # 转换到 ENU 地面坐标系
        thrust_world = R @ thrust_body

        # 平移动力学 (重力向下，即负 z 方向)
        ax = thrust_world[0] / self.mass
        ay = thrust_world[1] / self.mass
        az = thrust_world[2] / self.mass - self.g

        # 姿态运动学
        phi_dot = p + q*s_phi*np.tan(theta) + r*c_phi*np.tan(theta)
        theta_dot = q*c_phi - r*s_phi
        psi_dot = q*s_phi/np.cos(theta) + r*c_phi/np.cos(theta)

        # 旋转动力学
        p_dot = (tau_phi - q*r*(self.Izz - self.Iyy)) / self.Ixx
        q_dot = (tau_theta - p*r*(self.Ixx - self.Izz)) / self.Iyy
        r_dot = (tau_psi - p*q*(self.Iyy - self.Ixx)) / self.Izz

        # 状态导数
        state_dot = np.array([
            vx, vy, vz,
            ax, ay, az,
            phi_dot, theta_dot, psi_dot,
            p_dot, q_dot, r_dot
        ])

        # 欧拉积分
        self.state += state_dot * dt

        # 限制位置：地面碰撞检测 (z >= 0)
        if self.state[2] < 0:
            self.state[2] = 0   # z=0 是地面
            self.state[5] = 0   # 停止向下的速度
