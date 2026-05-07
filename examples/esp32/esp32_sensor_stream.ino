/*
 * ESP32 + BMI160 传感器数据流
 * 专门用于Python 3D可视化
 * 连接方式：
 * - VIN → 3.3V
 * - GND → GND
 * - SCL → GPIO22
 * - SDA → GPIO21
 */

#include <Wire.h>
#include <DFRobot_BMI160.h>

DFRobot_BMI160 bmi160;

int16_t accelData[3];  // 加速度计原始数据
int16_t gyroData[3];   // 陀螺仪原始数据

void setup() {
  Serial.begin(115200);
  delay(500);  // 简短等待

  Wire.begin();

  // 初始化BMI160
  int8_t rslt = bmi160.I2cInit(0x68);  // 先试0x68
  if (rslt != BMI160_OK) {
    rslt = bmi160.I2cInit(0x69);  // 再试0x69
  }

  if (rslt != BMI160_OK) {
    while (1);  // 初始化失败就停止
  }
}

void loop() {
  // 读取数据
  bmi160.getAccelData(accelData);
  bmi160.getGyroData(gyroData);

  // 转换为物理单位（不做校准，Python端处理）
  float ax = accelData[0] / 16384.0;
  float ay = accelData[1] / 16384.0;
  float az = accelData[2] / 16384.0;

  float gx = gyroData[0] / 16.4;
  float gy = gyroData[1] / 16.4;
  float gz = gyroData[2] / 16.4;

  // 发送CSV格式数据
  Serial.print(ax, 5); Serial.print(",");
  Serial.print(ay, 5); Serial.print(",");
  Serial.print(az, 5); Serial.print(",");
  Serial.print(gx, 3); Serial.print(",");
  Serial.print(gy, 3); Serial.print(",");
  Serial.println(gz, 3);

  delay(20);  // 50Hz刷新率
}
