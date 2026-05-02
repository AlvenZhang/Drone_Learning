"""
PID控制器
"""


class PIDController:
    """PID控制器"""

    def __init__(self, kp, ki, kd, output_min=None, output_max=None):
        """
        初始化PID控制器

        参数:
            kp: 比例系数
            ki: 积分系数
            kd: 微分系数
            output_min: 输出最小值
            output_max: 输出最大值
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_min = output_min
        self.output_max = output_max

        self.integral = 0.0
        self.last_error = 0.0

    def reset(self):
        """重置控制器状态"""
        self.integral = 0.0
        self.last_error = 0.0

    def compute(self, error, dt):
        """
        计算PID输出

        参数:
            error: 误差 (目标值 - 当前值)
            dt: 时间步长

        返回:
            PID输出
        """
        # 比例项
        p_term = self.kp * error

        # 积分项
        self.integral += error * dt
        i_term = self.ki * self.integral

        # 微分项
        d_term = self.kd * (error - self.last_error) / dt if dt > 0 else 0.0

        # 总输出
        output = p_term + i_term + d_term

        # 限幅
        if self.output_min is not None:
            output = max(output, self.output_min)
        if self.output_max is not None:
            output = min(output, self.output_max)

        # 保存误差
        self.last_error = error

        return output
