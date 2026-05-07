# Drone Learning

无人机学习项目 - 包含 ESP32 + BMI160 3D 姿态可视化、传感器驱动修复、飞控级姿态估计算法。

---

## 📦 最新项目：ESP32 + BMI160 3D 姿态可视化

从传感器原始数据到 3D 飞机模型的完整实时姿态解算项目，包含 DFRobot_BMI160 库的坑修复。

### 🎯 效果展示

- 静止时完全不抖动（LANDED 状态检测）
- 运动时纯陀螺积分快速跟随
- 放下后缓慢收敛到水平
- 刷新率 30+ fps

### ✨ 核心特性

1. **飞控级姿态估计算法**
   - EMA 低通滤波去除振动噪声
   - 静止（LANDED）状态自动检测
   - 连续陀螺仪零偏估计
   - 静止时超低权重（0.3%）加速度计修正

2. **修复了官方库的重大 BUG** ⚠️
   - DFRobot_BMI160 库 `getAccelData()` 和 `getGyroData()` 输出写反了
   - 这个坑踩过的人很多，文档完全不对

3. **完整的调试工具链**
   - 串口数据采集与分析脚本
   - 原始数据验证工具
   - 简化版可视化程序

### 🚀 快速开始

#### 硬件接线
```
BMI160    ESP32
VIN   →  3.3V
GND   →  GND
SCL   →  GPIO22
SDA   →  GPIO21
```

#### 软件运行

```bash
# 1. 上传 Arduino 固件
examples/esp32/esp32_sensor_stream.ino

# 2. 安装依赖
uv sync

# 3. 运行 3D 可视化
uv run python examples/3d_attitude_viewer.py

# 4. 选择串口号，等待校准完成
```

### 📁 项目结构

```
examples/
├── 3d_attitude_viewer.py  ✨ 主力程序（飞控级算法）
├── simple_viewer.py        简化版，快速验证
├── save_and_analyze.py     数据采集 + 自动分析
├── serial_test.py          串口调试工具
└── esp32/                  ESP32 固件
    ├── esp32_sensor_stream.ino  ← 推荐用这个
    └── 08_bmi160_test.ino       基础测试
```

### 🔧 关键技术点

#### 1. DFRobot_BMI160 库的 BUG

**坑了无数人的地方：**

| 函数名 | 你以为返回 | 实际返回 |
|--------|-----------|----------|
| `getAccelData()` | 加速度 (mg) | **陀螺仪原始计数** |
| `getGyroData()` | 陀螺仪 (mdeg/s) | **加速度计原始计数** |

**正确转换：**
```cpp
bmi160.getAccelData(gyroRaw);   // 读出来的其实是陀螺
bmi160.getGyroData(accelRaw);    // 读出来的其实是加速度

float gx = gyroRaw[0] / 16.4;    // 原始计数 → deg/s
float ax = accelRaw[0] / 16384.0; // 原始计数 → g
```

#### 2. 姿态算法原理

```
陀螺仪原始值 → EMA 滤波 → 减零偏 → 积分 → 姿态
                                             ↑
                          静止时 0.3% 权重 ← 加速度计
```

**为什么不直接用普通互补滤波？**
- 普通互补滤波每帧混入 5~10% 加速度计，静止时会抖
- 我们只在确认静止时才用极慢的速度修正，完全不抖

### 📝 数据格式

串口输出 CSV 格式：
```
ax, ay, az, gx, gy, gz
```

| 字段 | 单位 | 说明 |
|------|------|------|
| ax/ay/az | g | 三轴加速度，静止时模长≈1.0 |
| gx/gy/gz | deg/s | 三轴角速度，静止时≈0 |

---

## 📚 学习目录

```
├── docs/              # 学习资料
│   ├── basics/       # 基础知识
│   ├── advanced/     # 高级主题
│   └── projects/     # 项目案例
├── src/              # 源代码
│   ├── simulation/   # 仿真模块
│   ├── control/      # 控制算法
│   └── utils/        # 工具函数
├── tests/            # 测试代码
└── data/             # 数据文件
```

查看 `docs/basics/` 目录下的基础知识开始学习。
