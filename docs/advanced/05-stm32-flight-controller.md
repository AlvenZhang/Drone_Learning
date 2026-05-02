# STM32飞控制作完全指南

用STM32做飞控，这是个很酷的项目！

---

## 目录
1. [硬件选择](#第一步硬件选择)
2. [开发环境搭建](#第二步开发环境搭建)
3. [传感器读取](#第三步传感器读取)
4. [姿态解算](#第四步姿态解算)
5. [遥控器接收](#第五步遥控器接收)
6. [电调控制](#第六步电调控制)
7. [PID控制](#第七步pid控制)
8. [完整代码框架](#完整代码框架)

---

## 第一步：硬件选择

### 推荐的STM32开发板
| 型号 | 价格 | 特点 | 推荐度 |
|------|------|------|-------|
| STM32F103C8T6 (Blue Pill) | ¥20-30 | 便宜，入门首选 | ⭐⭐⭐⭐⭐ |
| STM32F407 | ¥50-80 | 性能强，IO多 | ⭐⭐⭐⭐ |
| STM32F411 | ¥40-60 | 平衡之选 | ⭐⭐⭐⭐ |

### 推荐配置
```
最推荐：STM32F103C8T6 (Blue Pill)
原因：
- 超便宜！¥20多
- 资料超多！
- 初学者首选！
```

---

### 其他硬件清单

| 部件 | 型号 | 价格 |
|------|------|------|
| 开发板 | STM32F103C8T6 | ¥20-30 |
| IMU | MPU6050模块 | ¥10-15 |
| 可选气压计 | BMP280 | ¥5-8 |
| 可选磁力计 | HMC5883L | ¥5-10 |
| 可选GPS | NEO-6M/7M | ¥30-50 |
| 电调 | 4路PWM输入 | ¥100-150 |
| 接收机 | SBUS/PPM | ¥30-80 |

**总计：约 ¥200-350**

---

### 硬件连接图

```
STM32F103C8T6
  │
  ├─ I2C ──── MPU6050 (陀螺仪+加速度计)
  │   SDA: PB9 (或 PB7)
  │   SCL: PB8 (或 PB6)
  │
  ├─ I2C ──── BMP280 (气压计，可选)
  │   (共用I2C总线)
  │
  ├─ USART1 ── SBUS接收机
  │   TX: PA9
  │   RX: PA10
  │
  ├─ PWM输出 ── 4个电调
  │   PA0, PA1, PA2, PA3 (TIM2_CH1-4)
  │
  └─ USART2 ── 调试串口
      TX: PA2
      RX: PA3
```

---

## 第二步：开发环境搭建

### 方案A：Keil MDK (Windows推荐)
```
1. 下载安装 Keil MDK
2. 安装 STM32CubeMX
3. 下载 STM32F103的标准库
4. 安装 ST-Link驱动
```

### 方案B：STM32CubeIDE (跨平台，免费)
```
1. 下载 STM32CubeIDE
2. 安装
3. 可以直接在里面开发，不需要其他软件
```

### 方案C：VS Code + PlatformIO (现代选择) ⭐推荐！
```
1. 安装 VS Code
2. 安装 PlatformIO 插件
3. 搜索 STM32F103C8T6 板子
4. 创建项目，直接开始写！

优点：
- 免费！
- 跨平台
- 库管理方便
```

---

## 第三步：传感器读取 (MPU6050)

### MPU6050 寄存器说明
```
主要寄存器：
- 0x6B: PWR_MGMT_1 (电源管理)
- 0x1B: GYRO_CONFIG (陀螺仪配置)
- 0x1C: ACCEL_CONFIG (加速度计配置)
- 0x3B-0x48: 数据寄存器
```

### 代码示例：读取MPU6050原始数据

```c
#include "stm32f10x.h"
#include "i2c.h"

#define MPU6050_ADDR 0xD0

// 初始化MPU6050
void MPU6050_Init(void) {
    // 唤醒MPU6050
    I2C_WriteReg(MPU6050_ADDR, 0x6B, 0x00);

    // 设置陀螺仪量程：±500°/s
    I2C_WriteReg(MPU6050_ADDR, 0x1B, 0x08);

    // 设置加速度计量程：±2g
    I2C_WriteReg(MPU6050_ADDR, 0x1C, 0x00);
}

// 读取加速度和陀螺仪数据
void MPU6050_Read(int16_t *ax, int16_t *ay, int16_t *az,
                  int16_t *gx, int16_t *gy, int16_t *gz) {
    uint8_t data[14];

    // 从0x3B开始读14个字节
    I2C_ReadRegs(MPU6050_ADDR, 0x3B, data, 14);

    // 拼接成16位有符号整数
    *ax = (data[0] << 8) | data[1];
    *ay = (data[2] << 8) | data[3];
    *az = (data[4] << 8) | data[5];
    *gx = (data[8] << 8) | data[9];
    *gy = (data[10] << 8) | data[11];
    *gz = (data[12] << 8) | data[13];
}

// 简单的I2C写寄存器
void I2C_WriteReg(uint8_t addr, uint8_t reg, uint8_t data) {
    I2C_GenerateSTART(I2C1, ENABLE);
    while(!I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_MODE_SELECT));

    I2C_Send7bitAddress(I2C1, addr, I2C_Direction_Transmitter);
    while(!I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_TRANSMITTER_MODE_SELECTED));

    I2C_SendData(I2C1, reg);
    while(!I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_BYTE_TRANSMITTED));

    I2C_SendData(I2C1, data);
    while(!I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_BYTE_TRANSMITTED));

    I2C_GenerateSTOP(I2C1, ENABLE);
}
```

---

## 第四步：姿态解算

### 方案A：互补滤波 (简单，新手推荐)

```c
#include <math.h>

// 姿态角度
float roll = 0;
float pitch = 0;
float yaw = 0;

// 滤波参数
float alpha = 0.96;  // 陀螺仪权重
float dt = 0.001;    // 1ms

void Attitude_Update(float ax, float ay, float az,
                     float gx, float gy, float gz) {

    // 1. 用加速度计算角度
    float roll_acc = atan2(ay, sqrt(ax*ax + az*az)) * 180.0f / 3.1415926f;
    float pitch_acc = atan2(-ax, sqrt(ay*ay + az*az)) * 180.0f / 3.1415926f;

    // 2. 把角速度转换成°/s
    // MPU6050设置为±500°/s，灵敏度65.5 LSB/(°/s)
    float gx_deg = gx / 65.5f;
    float gy_deg = gy / 65.5f;
    float gz_deg = gz / 65.5f;

    // 3. 陀螺仪积分
    float roll_gyro = roll + gx_deg * dt;
    float pitch_gyro = pitch + gy_deg * dt;

    // 4. 互补滤波融合两者
    roll = alpha * roll_gyro + (1 - alpha) * roll_acc;
    pitch = alpha * pitch_gyro + (1 - alpha) * pitch_acc;
}
```

### 方案B：卡尔曼滤波 (更高级，可选)

稍微复杂一点，以后可以研究

---

## 第五步：遥控器接收

### 推荐用SBUS协议！
```
优点：
- 只需要一根线
- 抗干扰强
- 最多支持16通道

注意：
- SBUS是反相的串口信号
- 可能需要硬件反相，或者用软件处理
```

### SBUS代码示例

```c
// SBUS数据包结构
typedef struct {
    uint8_t header;        // 0x0F
    uint16_t channels[16]; // 16个通道
    uint8_t flags;         // 标志位
    uint8_t end;           // 0x00
} SBUS_Packet;

SBUS_Packet sbus;

// 串口中断接收
void USART1_IRQHandler(void) {
    static uint8_t rx_buf[25];
    static uint8_t rx_idx = 0;

    if(USART_GetITStatus(USART1, USART_IT_RXNE) != RESET) {
        uint8_t data = USART_ReceiveData(USART1);

        rx_buf[rx_idx++] = ~data; // SBUS是反相的

        if(rx_idx == 25 && rx_buf[0] == 0x0F) {
            // 解析SBUS
            sbus.channels[0]  = ((rx_buf[1]  | rx_buf[2]<<8) & 0x07FF);
            sbus.channels[1]  = ((rx_buf[2]>>3 | rx_buf[3]<<5) & 0x07FF);
            sbus.channels[2]  = ((rx_buf[3]>>6 | rx_buf[4]<<2 | rx_buf[5]<<10) & 0x07FF);
            sbus.channels[3]  = ((rx_buf[5]>>1 | rx_buf[6]<<7) & 0x07FF);
            sbus.channels[4]  = ((rx_buf[6]>>4 | rx_buf[7]<<4) & 0x07FF);
            sbus.channels[5]  = ((rx_buf[7]>>7 | rx_buf[8]<<1 | rx_buf[9]<<9) & 0x07FF);
            // ... 继续解析16个通道

            rx_idx = 0;
        }
        else if(rx_idx >= 25) {
            rx_idx = 0;
        }
    }
}

// 把SBUS值转成1000-2000us
uint16_t sbus_to_pwm(uint16_t sbus_val) {
    // SBUS范围是172-1811，转成1000-2000
    return (uint16_t)((sbus_val - 172) * 1000.0f / 1639.0f + 1000.0f);
}
```

---

## 第六步：电调控制 (PWM输出)

### 初始化PWM输出

```c
#include "stm32f10x.h"

void PWM_Init(void) {
    // 启用时钟
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM2, ENABLE);
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);

    // GPIO配置：PA0, PA1, PA2, PA3
    GPIO_InitTypeDef GPIO_InitStructure;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0 | GPIO_Pin_1 | GPIO_Pin_2 | GPIO_Pin_3;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);

    // 定时器配置
    TIM_TimeBaseInitTypeDef TIM_TimeBaseStructure;
    TIM_TimeBaseStructure.TIM_Period = 19999;  // 20000步
    TIM_TimeBaseStructure.TIM_Prescaler = 71;  // 72MHz / 72 = 1MHz
    TIM_TimeBaseStructure.TIM_ClockDivision = TIM_CKD_DIV1;
    TIM_TimeBaseStructure.TIM_CounterMode = TIM_CounterMode_Up;
    TIM_TimeBaseInit(TIM2, &TIM_TimeBaseStructure);

    // PWM模式配置
    TIM_OCInitTypeDef TIM_OCInitStructure;
    TIM_OCInitStructure.TIM_OCMode = TIM_OCMode_PWM1;
    TIM_OCInitStructure.TIM_OutputState = TIM_OutputState_Enable;
    TIM_OCInitStructure.TIM_Pulse = 1000;  // 初始1000us
    TIM_OCInitStructure.TIM_OCPolarity = TIM_OCPolarity_High;

    TIM_OC1Init(TIM2, &TIM_OCInitStructure);  // PA0
    TIM_OC2Init(TIM2, &TIM_OCInitStructure);  // PA1
    TIM_OC3Init(TIM2, &TIM_OCInitStructure);  // PA2
    TIM_OC4Init(TIM2, &TIM_OCInitStructure);  // PA3

    // 启动定时器
    TIM_Cmd(TIM2, ENABLE);
}

// 设置PWM脉宽
void PWM_SetPulse(uint8_t motor, uint16_t pulse) {
    switch(motor) {
        case 0: TIM_SetCompare1(TIM2, pulse); break;
        case 1: TIM_SetCompare2(TIM2, pulse); break;
        case 2: TIM_SetCompare3(TIM2, pulse); break;
        case 3: TIM_SetCompare4(TIM2, pulse); break;
    }
}
```

---

## 第七步：PID控制

### PID控制器结构

```c
typedef struct {
    float kp;
    float ki;
    float kd;
    float integral;
    float prev_error;
    float output_min;
    float output_max;
} PIDController;

// PID初始化
void PID_Init(PIDController *pid, float kp, float ki, float kd,
              float out_min, float out_max) {
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->integral = 0;
    pid->prev_error = 0;
    pid->output_min = out_min;
    pid->output_max = out_max;
}

// PID计算
float PID_Compute(PIDController *pid, float setpoint, float measured, float dt) {
    float error = setpoint - measured;
    float p = pid->kp * error;

    pid->integral += error * dt;
    float i = pid->ki * pid->integral;

    float d = pid->kd * (error - pid->prev_error) / dt;

    float output = p + i + d;
    pid->prev_error = error;

    // 限幅
    if(output > pid->output_max) output = pid->output_max;
    if(output < pid->output_min) output = pid->output_min;

    return output;
}
```

---

## 完整代码框架 (main函数)

```c
#include "stm32f10x.h"
#include "i2c.h"
#include "pwm.h"
#include "sbus.h"
#include "pid.h"

// PID控制器
PIDController pid_roll, pid_pitch, pid_yaw, pid_z;

// 主函数
int main(void) {
    // 1. 初始化所有外设
    MPU6050_Init();
    PWM_Init();
    SBUS_Init();
    // 其他初始化...

    // 2. 初始化PID
    PID_Init(&pid_roll,  4.0f, 0.5f, 0.1f, -500, 500);
    PID_Init(&pid_pitch, 4.0f, 0.5f, 0.1f, -500, 500);
    PID_Init(&pid_yaw,   3.0f, 0.3f, 0.1f, -500, 500);
    PID_Init(&pid_z,     5.0f, 0.5f, 1.0f, -300, 300);

    // 3. 主循环
    while(1) {
        uint32_t now = get_current_time();
        static uint32_t last_time = 0;

        if(now - last_time >= 1) { // 1ms循环
            last_time = now;
            float dt = 0.001f;

            // 读取传感器
            int16_t ax, ay, az, gx, gy, gz;
            MPU6050_Read(&ax, &ay, &az, &gx, &gy, &gz);

            // 姿态解算
            Attitude_Update(ax, ay, az, gx, gy, gz);

            // 读取遥控器
            uint16_t ch0 = sbus_to_pwm(sbus.channels[0]); // 油门
            uint16_t ch1 = sbus_to_pwm(sbus.channels[1]); // 横滚
            uint16_t ch2 = sbus_to_pwm(sbus.channels[2]); // 俯仰
            uint16_t ch3 = sbus_to_pwm(sbus.channels[3]); // 偏航

            // 计算目标角度 (摇杆量转角度)
            float target_roll = (ch1 - 1500) * 0.1f;
            float target_pitch = (ch2 - 1500) * 0.1f;
            float target_yaw = (ch3 - 1500) * 0.1f;

            // PID计算
            float out_roll = PID_Compute(&pid_roll, target_roll, roll, dt);
            float out_pitch = PID_Compute(&pid_pitch, target_pitch, pitch, dt);
            float out_yaw = PID_Compute(&pid_yaw, target_yaw, yaw, dt);

            // 油门
            float throttle = ch0;

            // 电机混控 (X形)
            float m1 = throttle - out_roll + out_pitch + out_yaw;
            float m2 = throttle + out_roll + out_pitch - out_yaw;
            float m3 = throttle + out_roll - out_pitch + out_yaw;
            float m4 = throttle - out_roll - out_pitch - out_yaw;

            // 限幅
            m1 = (m1 > 2000) ? 2000 : ((m1 < 1000) ? 1000 : m1);
            m2 = (m2 > 2000) ? 2000 : ((m2 < 1000) ? 1000 : m2);
            m3 = (m3 > 2000) ? 2000 : ((m3 < 1000) ? 1000 : m3);
            m4 = (m4 > 2000) ? 2000 : ((m4 < 1000) ? 1000 : m4);

            // 输出到电调
            PWM_SetPulse(0, (uint16_t)m1);
            PWM_SetPulse(1, (uint16_t)m2);
            PWM_SetPulse(2, (uint16_t)m3);
            PWM_SetPulse(3, (uint16_t)m4);
        }
    }
}
```

---

## 📚 学习资源

### 在线教程
- B站搜 "STM32 四轴飞控"
- 野火/原子的STM32教程

### 参考代码
- MultiWii (虽然是Arduino的，但原理一样)
- CleanFlight (STM32的，代码更好)
- 网上搜 "STM32F103 四轴"

---

## 💡 我的建议

### 学习顺序
1. ✅ 先买STM32F103+MPU6050
2. ✅ 先跑通LED、串口这些简单例子
3. ✅ 再读MPU6050数据
4. ✅ 再做姿态解算
5. ✅ 再调通PWM控制电机
6. ✅ 最后整合PID

### 不建议一开始就做真飞机！
- 先在实验台上调通所有功能
- 写好代码
- 确保没问题了再装到机架上
- 第一次试飞一定要有老司机陪同！

---

你想用STM32做吗？还是先买现成飞控玩着？
