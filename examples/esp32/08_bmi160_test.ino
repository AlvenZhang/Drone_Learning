/*
 * ESP32测试8: BMI160陀螺仪/加速度计测试
 * 连接方式：
 * - VIN → 3.3V (不要接5V！)
 * - GND → GND
 * - SCL → GPIO22
 * - SDA → GPIO21
 * - SA0 → GND (地址0x68) 或 3.3V (地址0x69)
 */

#include <Wire.h>

#define BMI160_ADDR 0x69

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("ESP32 BMI160 Test");
  Serial.println("=================");

  Wire.begin();

  initBMI160();
}

void loop() {
  uint8_t status = readReg(0x1B);
  uint8_t pmu = readReg(0x03);

  Serial.print("PMU:0x");
  Serial.print(pmu, HEX);
  Serial.print(" Status:0x");
  Serial.print(status, HEX);

  // 如果陀螺仪没就绪，尝试重新启动！
  if ((pmu & 0x0C) != 0x04) {
    Serial.print(" RESTART GYRO!");
    writeReg(0x7E, 0x15);
    delay(200);
  }

  // 读取数据
  uint8_t axl = readReg(0x12); uint8_t axh = readReg(0x13);
  uint8_t ayl = readReg(0x14); uint8_t ayh = readReg(0x15);
  uint8_t azl = readReg(0x16); uint8_t azh = readReg(0x17);

  int16_t accelX = (int16_t)(axh << 8 | axl);
  int16_t accelY = (int16_t)(ayh << 8 | ayl);
  int16_t accelZ = (int16_t)(azh << 8 | azl);

  float ax = accelX / 16384.0;
  float ay = accelY / 16384.0;
  float az = accelZ / 16384.0;

  Serial.print("  |  Accel(g): ");
  Serial.print(ax, 3); Serial.print(", ");
  Serial.print(ay, 3); Serial.print(", ");
  Serial.println(az, 3);

  delay(200);
}

void initBMI160() {
  Serial.println("Chip ID: 0x" + String(readReg(0x00), HEX));

  // 软复位
  writeReg(0x7E, 0xB6);
  delay(150);

  // 先启动陀螺仪，再启动加速度计！
  Serial.println("Starting gyroscope...");
  writeReg(0x7E, 0x15);
  delay(300);  // 更长的延迟！
  Serial.println("PMU after gyro: 0x" + String(readReg(0x03), HEX));

  Serial.println("Starting accelerometer...");
  writeReg(0x7E, 0x11);
  delay(150);
  Serial.println("PMU after accel: 0x" + String(readReg(0x03), HEX));

  // 配置
  writeReg(0x40, 0x23);  // Accel: ±2g, 100Hz
  writeReg(0x42, 0x23);  // Gyro: ±2000dps, 100Hz

  Serial.println("Done!");
}

uint8_t readReg(uint8_t reg) {
  Wire.beginTransmission(BMI160_ADDR);
  Wire.write(reg);
  Wire.endTransmission();
  Wire.requestFrom(BMI160_ADDR, 1);
  return Wire.read();
}

void writeReg(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(BMI160_ADDR);
  Wire.write(reg);
  Wire.write(val);
  Wire.endTransmission();
}
