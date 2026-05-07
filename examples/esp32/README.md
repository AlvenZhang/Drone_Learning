# ESP32 测试程序

这些是ESP32的基础测试程序，用于验证你的ESP32开发板是否正常工作。

## 硬件准备

- ESP32开发板
- USB数据线
- 电脑（Windows/Mac/Linux）

## 软件准备

1. 安装Arduino IDE: https://www.arduino.cc/en/software
2. 在Arduino IDE中添加ESP32支持：
   - 打开Arduino IDE
   - 文件 → 首选项 → 附加开发板管理器网址
   - 添加: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
3. 工具 → 开发板 → 开发板管理器 → 搜索"ESP32" → 安装"ESP32 by Espressif Systems"

## 使用步骤

1. 用USB线连接ESP32到电脑
2. 打开Arduino IDE
3. 工具 → 开发板 → ESP32 Arduino → 选择你的ESP32型号（通常选"ESP32 Dev Module"）
4. 工具 → 端口 → 选择ESP32的串口
5. 打开一个.ino文件
6. 点击"上传"按钮（→）
7. 等待编译和上传完成
8. 工具 → 串口监视器 → 设置波特率为115200，查看输出

## 测试顺序

### 1. 01_blink.ino
- 最简单的测试
- 验证ESP32能否正常烧录程序
- 板载LED应该每隔0.5秒闪烁一次
- 串口监视器会显示"LED ON"/"LED OFF"

### 2. 02_wifi_scan.ino
- 测试ESP32的WiFi功能
- 会扫描附近的WiFi网络并打印出来
- 串口监视器会显示找到的WiFi列表

### 3. 03_gpio_test.ino
- 测试数字输入输出
- 需要外接LED和按键
- LED: GPIO4, 按键: GPIO5
- 按下按键LED点亮，松开熄灭

### 4. 04_pwm_test.ino ⭐ 重要
- 测试PWM输出（无人机控制电机必备！）
- LED会渐亮渐暗
- PWM可以控制电机转速、舵机角度等

### 5. 05_i2c_scanner.ino ⭐ 重要
- 扫描I2C总线上的设备
- 用来找陀螺仪（MPU6050等）的地址
- MPU6050通常在0x68或0x69
- 接线: SDA→GPIO21, SCL→GPIO22

### 6. 06_adc_test.ino
- 测试模拟电压读取
- 用来测电池电压等
- 输入范围: 0-3.3V
- 接线: 输入→GPIO34

### 7. 07_servo_test.ino
- 测试舵机控制
- 需要安装ESP32Servo库（Arduino IDE库管理器搜索安装）
- 舵机信号线→GPIO18
- 舵机会在0°-180°之间来回转动

### 8. 08_bmi160_test.ino ⭐ 无人机必备
- 测试BMI160陀螺仪/加速度计
- 接线: VIN→3.3V, GND→GND, SCL→GPIO22, SDA→GPIO21
- 会实时显示加速度和陀螺仪数据
- 晃动ESP32看数据变化！

## 常见问题

**Q: 找不到串口？**
- 检查USB线是否是数据线（有些只能充电）
- 检查是否安装了CP2102/CH340驱动
- 尝试换一个USB口

**Q: 上传失败？**
- 检查开发板型号是否选对
- 按住ESP32的BOOT按钮，然后点击上传，看到"Connecting..."时松开

**Q: 串口监视器乱码？**
- 检查波特率是否设置为115200
