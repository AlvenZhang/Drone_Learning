"""
无人机仿真器
"""
import numpy as np
from .quadcopter import Quadcopter


class Simulator:
    """仿真器类"""

    def __init__(self, dt=0.01):
        """
        初始化仿真器

        参数:
            dt: 仿真时间步长 (s)
        """
        self.dt = dt
        self.quadcopter = Quadcopter()
        self.time = 0.0

        # 记录历史数据
        self.history = {
            'time': [],
            'position': [],
            'velocity': [],
            'attitude': [],
            'motor_speeds': []
        }

    def reset(self, position=None):
        """重置仿真"""
        self.quadcopter.reset(position)
        self.time = 0.0
        self.history = {
            'time': [],
            'position': [],
            'velocity': [],
            'attitude': [],
            'motor_speeds': []
        }

    def record_state(self, motor_speeds=None):
        """记录当前状态"""
        self.history['time'].append(self.time)
        self.history['position'].append(self.quadcopter.get_position().copy())
        self.history['velocity'].append(self.quadcopter.get_velocity().copy())
        self.history['attitude'].append(self.quadcopter.get_attitude().copy())
        if motor_speeds is not None:
            self.history['motor_speeds'].append(motor_speeds.copy())

    def run(self, duration, controller=None):
        """
        运行仿真

        参数:
            duration: 仿真时长 (s)
            controller: 控制器函数，输入是无人机和时间，输出是电机转速平方
        """
        steps = int(duration / self.dt)

        for _ in range(steps):
            if controller:
                motor_speeds_sq = controller(self.quadcopter, self.time)
            else:
                # 默认：悬停
                hover_thrust = self.quadcopter.mass * self.quadcopter.g
                motor_speeds_sq = np.ones(4) * hover_thrust / 4.0

            self.record_state(motor_speeds_sq)
            self.quadcopter.step(motor_speeds_sq, self.dt)
            self.time += self.dt

        # 记录最终状态
        self.record_state(motor_speeds_sq)

    def get_trajectory(self):
        """获取飞行轨迹"""
        return {
            'time': np.array(self.history['time']),
            'position': np.array(self.history['position']),
            'velocity': np.array(self.history['velocity']),
            'attitude': np.array(self.history['attitude'])
        }
