# DIY飞控：自己做飞行控制器！

用开发板自己写代码做飞控，这个很酷！

---

## 目录
1. [入门级方案](#入门级方案)
2. [进阶级方案](#进阶级方案)
3. [学习路径](#学习路径)
4. [软件框架](#软件框架)
5. [代码示例](#代码示例)

---

## 入门级方案 (最简单)

### Arduino + MPU6050

#### 硬件清单
| 部件 | 型号 | 价格 |
|------|------|------|
| 开发板 | Arduino Uno / Nano | ¥30-50 |
| 陀螺仪 | MPU6050模块 | ¥10-15 |
| 电调 | 普通4路电调或4个独立电调 | ¥100-150 |
| 接收机 | PWM接收机 (跟遥控配对) | ¥30-80 |
| 可选：气压计 | BMP280 | ¥5-8 |
| 可选：GPS | NEO-6M/7M | ¥30-50 |

**总计：约 ¥200-300**

#### 硬件连接图
```
Arduino Uno
  │
  ├─ I2C ──── MPU6050 (陀螺仪+加速度计)
  │
  ├─ PWM引脚 ── 4个电调
  │
  ├─ 中断/PCINT ── 接收机
  │
  └─ 可选：I2C ── BMP280 (气压计)
```

#### MPU6050接线
```
MPU6050    Arduino Uno
  VCC   →  3.3V 或 5V (看模块)
  GND   →  GND
  SDA   →  A4 (或 SDA引脚)
  SCL   →  A5 (或 SCL引脚)
  INT   →  D2 (可选，中断用)
```

---

## 进阶级方案 (性能更好)

### STM32 + 多传感器

#### 硬件清单
| 部件 | 推荐型号 | 价格 |
|------|---------|------|
| 开发板 | STM32F103C8T6 (Blue Pill) | ¥20-30 |
| 或 | STM32F407 | ¥50-80 |
| IMU | MPU6050 / MPU9250 / ICM-20602 | ¥15-30 |
| 气压计 | BMP280 / MS5611 | ¥5-15 |
| 磁力计 | HMC5883L / AK8963 | ¥5-10 |
| GPS | NEO-6M/7M/8M | ¥30-50 |
| 遥控接收机 | SBUS/PPM接收机 | ¥30-80 |

**总计：约 ¥200-400**

#### 为什么选STM32？
- ✅ 速度快！比Arduino快很多
- ✅ 外设丰富
- ✅ 开源飞控很多都用STM32
- ✅ 便宜！

---

## 专业级方案 (跟开源飞控差不多)

### 自己画PCB板
- 用 KiCad / Altium Designer 画
- 嘉立创打样 (5片板子约 ¥50)
- 自己焊接所有芯片和元件

---

## 学习路径 (循序渐进)

### 第一步：先玩传感器 (1-2周)
```
目标：能读出传感器数据

练习：
1. Arduino 读取 MPU6050 的原始数据
2. 用串口打印出来
3. 晃动板子，看数据变化
```

### 第二步：姿态解算 (2-3周)
```
目标：从原始数据算出 Roll/Pitch/Yaw

内容：
1. 简单的互补滤波
2. 卡尔曼滤波 (可选，稍难)
3. 或者用MPU6050的DMP (简单，但是不如自己写清楚)
```

### 第三步：遥控器读取 (1周)
```
目标：能读出遥控器的5个通道值

内容：
1. PPM信号读取
2. PWM信号读取
3. SBUS信号读取 (推荐，抗干扰好)
```

### 第四步：电调控制 (1周)
```
目标：Arduino输出PWM控制电机

内容：
1. 理解PWM信号 (50Hz, 1000-2000us)
2. 校准电调
3. 写代码控制电机转起来
⚠️ 先不要装桨！
```

### 第五步：简单的级联PID (2-3周)
```
目标：能保持飞机水平

步骤：
1. 先写姿态环 PID
2. 然后写角速度环 PID
3. 最后混合输出到四个电机
```

### 第六步：高度控制 (1-2周)
```
目标：定高悬停

内容：
1. 读取气压计数据
2. 计算高度
3. 高度PID控制
```

### 第七步：试飞调试 (持续)
```
目标：能飞起来！

注意：
⚠️ 找老手陪同
⚠️ 先在模拟器测试
⚠️ 用机架保护圈
```

---

## 软件框架 (可以直接用的)

### 1. Arduino 开源项目
- **MultiWii**：经典老项目，代码可读
- **BaseFlight**：MultiWii的优化版
- **CleanFlight**：现代一点
- **BetaFlight**：现在最火

### 2. STM32 开源项目
- **BetaFlight**：支持STM32F1/F3/F4/F7
- **PX4**：超级强大，但复杂
- **ArduPilot**：同样强大

### 3. 学习项目
- **Crazepony**：迷你四轴，代码简单
- **MiniFly**：另一个学习用的
- **Paparazzi**：开源

---

## 代码示例 (Arduino + MPU6050)

### 示例1：读取MPU6050原始数据
```cpp
#include <Wire.h>

#define MPU6050_ADDR 0x68

void setup() {
  Wire.begin();
  Serial.begin(115200);

  // 初始化MPU6050
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(0x6B); // PWR_MGMT_1
  Wire.write(0);    // 唤醒
  Wire.endTransmission(true);
}

void loop() {
  // 请求数据
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(0x3B); // 从0x3B开始
  Wire.endTransmission(false);
  Wire.requestFrom(MPU6050_ADDR, 14, true);

  // 读取14个字节
  int16_t ax = Wire.read() << 8 | Wire.read();
  int16_t ay = Wire.read() << 8 | Wire.read();
  int16_t az = Wire.read() << 8 | Wire.read();
  int16_t temp = Wire.read() << 8 | Wire.read();
  int16_t gx = Wire.read() << 8 | Wire.read();
  int16_t gy = Wire.read() << 8 | Wire.read();
  int16_t gz = Wire.read() << 8 | Wire.read();

  // 打印
  Serial.print("ax:"); Serial.print(ax);
  Serial.print(" ay:"); Serial.print(ay);
  Serial.print(" az:"); Serial.print(az);
  Serial.print(" gx:"); Serial.print(gx);
  Serial.print(" gy:"); Serial.print(gy);
  Serial.print(" gz:"); Serial.println(gz);

  delay(10);
}
```

### 示例2：简单的互补滤波
```cpp
// 变量
float roll = 0;
float pitch = 0;

// 参数
float alpha = 0.96; // 滤波系数
float dt = 0.01;   // 10ms

void update_attitude(float ax, float ay, float az,
                     float gx, float gy, float gz) {

  // 1. 用加速度计算姿态
  float roll_acc = atan2(ay, sqrt(ax*ax + az*az)) * 180/PI;
  float pitch_acc = atan2(-ax, sqrt(ay*ay + az*az)) * 180/PI;

  // 2. 用陀螺仪积分
  float roll_gyro = roll + gx * dt;
  float pitch_gyro = pitch + gy * dt;

  // 3. 互补滤波：两者融合
  roll = alpha * roll_gyro + (1 - alpha) * roll_acc;
  pitch = alpha * pitch_gyro + (1 - alpha) * pitch_acc;
}
```

### 示例3：电机混控 (X形)
```cpp
void motor_mixing(float thrust, float roll, float pitch, float yaw) {
  // 四个电机
  float m1 = thrust - roll + pitch + yaw;
  float m2 = thrust + roll + pitch - yaw;
  float m3 = thrust + roll - pitch + yaw;
  float m4 = thrust - roll - pitch - yaw;

  // 限幅
  m1 = constrain(m1, 1000, 2000);
  m2 = constrain(m2, 1000, 2000);
  m3 = constrain(m3, 1000, 2000);
  m4 = constrain(m4, 1000, 2000);

  // 输出到电调
  servo1.writeMicroseconds(m1);
  servo2.writeMicroseconds(m2);
  servo3.writeMicroseconds(m3);
  servo4.writeMicroseconds(m4);
}
```

---

## 推荐的学习资源

### 视频教程 (B站搜)
1. "MultiWii 飞控代码解读"
2. "MPU6050 姿态解算"
3. "Arduino 四轴飞控"
4. "STM32 四轴飞控开发"

### 开源代码
1. **MultiWii**：https://github.com/multiwii
2. **BetaFlight**：https://github.com/betaflight
3. **Crazepony**：https://github.com/Crazepony
4. **PX4**：https://github.com/PX4/PX4-Autopilot

### 书籍
- 《四旋翼无人飞行器设计》
- 《无人机设计与制作》

---

## 我的建议路线

### 方案A：Arduino入门 (简单，慢点)
1. Arduino Uno + MPU6050
2. 先读数据，再写姿态解算
3. 成功让电机转起来
4. 尝试悬停
5. 然后换STM32

### 方案B：直接玩开源飞控 (推荐！)
1. 买现成F3/F4飞控
2. 刷BetaFlight固件
3. 先飞起来
4. 再看源码，慢慢改
5. 理解了之后自己做

**推荐方案B！** 先有感性认识，再深入理论

---

## ⚠️ 注意事项

1. **安全第一**：自己写的飞控没经过大量测试，一定要小心
2. **先用模拟器**：先在仿真里跑通
3. **有人陪同**：第一次试飞一定要有经验的人在
4. **装保护圈**：新手必备

---

## 你想从哪开始？

- [ ] 先买Arduino + MPU6050玩传感器
- [ ] 直接研究BetaFlight源码
- [ ] 先不管这个，先把第一架飞机装起来飞了再说

你选哪个？
