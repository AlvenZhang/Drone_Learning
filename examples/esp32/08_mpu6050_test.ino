/*
 * ESP32测试8: MPU6050陀螺仪/加速度计测试
 * 连接方式：
 * - VCC → 3.3V 或 5V（看模块，大部分可以3.3V）
 * - GND → GND
 * - SCL → GPIO22
 * - SDA → GPIO21
 * - AD0 → GND(0x68) 或 3.3V(0x69)
 */

#include <Wire.h>

// MPU6050 I2C地址
#define MPU6050_ADDR 0x69  // 根据你的实际地址改

// MPU6050寄存器定义
#define MPU6050_REG_PWR_MGMT_1 0x6B
#define MPU6050_REG_WHO_AM_I 0x75
#define MPU6050_REG_ACCEL_XOUT_H 0x3B
#define MPU6050_REG_GYRO_XOUT_H 0x43
#define MPU6050_REG_ACCEL_CONFIG 0x1C
#define MPU6050_REG_GYRO_CONFIG 0x1B

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("ESP32 MPU6050 Test");
  Serial.println("==================");

  // 初始化I2C
  Wire.begin();

  // 初始化MPU6050
  Serial.println("Initializing MPU6050...");
  if (initMPU6050()) {
    Serial.println("MPU6050 initialized successfully!");
  } else {
    Serial.println("MPU6050 initialization failed!");
    while (1);  // 停止程序
  }
}

void loop() {
  int16_t accelX, accelY, accelZ;
  int16_t gyroX, gyroY, gyroZ;
  int16_t temp;

  // 读取数据
  if (readMPU6050(&accelX, &accelY, &accelZ, &gyroX, &gyroY, &gyroZ, &temp)) {
    // 转换为物理单位
    float accelX_g = accelX / 16384.0;  // ±2g范围
    float accelY_g = accelY / 16384.0;
    float accelZ_g = accelZ / 16384.0;

    float gyroX_dps = gyroX / 131.0;  // ±250dps范围
    float gyroY_dps = gyroY / 131.0;
    float gyroZ_dps = gyroZ / 131.0;

    float temp_C = temp / 340.0 + 36.53;

    // 打印数据
    Serial.println("--------------------------------------------------");
    Serial.print("Accel (g): X=");
    Serial.print(accelX_g, 3);
    Serial.print("  Y=");
    Serial.print(accelY_g, 3);
    Serial.print("  Z=");
    Serial.println(accelZ_g, 3);

    Serial.print("Gyro  (dps): X=");
    Serial.print(gyroX_dps, 2);
    Serial.print("  Y=");
    Serial.print(gyroY_dps, 2);
    Serial.print("  Z=");
    Serial.println(gyroZ_dps, 2);

    Serial.print("Temp (C): ");
    Serial.println(temp_C, 1);
    Serial.println("--------------------------------------------------");
  }

  delay(100);  // 每100ms读取一次
}

// 写入寄存器
void writeReg(uint8_t reg, uint8_t data) {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(reg);
  Wire.write(data);
  Wire.endTransmission();
}

// 读取寄存器
uint8_t readReg(uint8_t reg) {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(reg);
  Wire.endTransmission();

  Wire.requestFrom(MPU6050_ADDR, 1);
  return Wire.read();
}

// 初始化MPU6050
bool initMPU6050() {
  // 读取WHO_AM_I寄存器，MPU6050应该是0x68-0x73之间（通常0x68或0x72）
  uint8_t whoAmI = readReg(MPU6050_REG_WHO_AM_I);
  Serial.print("WHO_AM_I: 0x");
  Serial.print(whoAmI, HEX);
  Serial.println();

  // 唤醒MPU6050（它默认是休眠状态）
  writeReg(MPU6050_REG_PWR_MGMT_1, 0x00);
  delay(100);

  // 配置加速度计范围 ±2g
  writeReg(MPU6050_REG_ACCEL_CONFIG, 0x00);

  // 配置陀螺仪范围 ±250dps
  writeReg(MPU6050_REG_GYRO_CONFIG, 0x00);

  delay(100);
  return true;
}

// 读取MPU6050数据
bool readMPU6050(int16_t *accelX, int16_t *accelY, int16_t *accelZ,
                 int16_t *gyroX, int16_t *gyroY, int16_t *gyroZ,
                 int16_t *temp) {
  // 从ACCEL_XOUT_H开始读取14个字节
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(MPU6050_REG_ACCEL_XOUT_H);
  Wire.endTransmission();

  Wire.requestFrom(MPU6050_ADDR, 14);
  if (Wire.available() == 14) {
    *accelX = (int16_t)(Wire.read() << 8 | Wire.read());
    *accelY = (int16_t)(Wire.read() << 8 | Wire.read());
    *accelZ = (int16_t)(Wire.read() << 8 | Wire.read());
    *temp = (int16_t)(Wire.read() << 8 | Wire.read());
    *gyroX = (int16_t)(Wire.read() << 8 | Wire.read());
    *gyroY = (int16_t)(Wire.read() << 8 | Wire.read());
    *gyroZ = (int16_t)(Wire.read() << 8 | Wire.read());
    return true;
  }

  return false;
}
