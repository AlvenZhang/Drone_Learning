/*
 * ESP32测试5: I2C设备扫描器
 * 用于查找连接到I2C总线的设备（如陀螺仪MPU6050等）
 * 连接方式：
 * - SDA → GPIO21
 * - SCL → GPIO22
 */

#include <Wire.h>

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("ESP32 I2C Scanner");
  Serial.println("=================");

  // 初始化I2C
  Wire.begin();

  Serial.println("I2C pins:");
  Serial.println("  SDA → GPIO21");
  Serial.println("  SCL → GPIO22");
  Serial.println("");
  Serial.println("Scanning for I2C devices...");
}

void loop() {
  byte error, address;
  int deviceCount;

  Serial.println("");
  Serial.println("Scanning...");

  deviceCount = 0;

  // 扫描所有可能的I2C地址（1-127）
  for (address = 1; address < 127; address++) {
    // 尝试与地址通信
    Wire.beginTransmission(address);
    error = Wire.endTransmission();

    if (error == 0) {
      // 找到设备
      Serial.print("I2C device found at address 0x");
      if (address < 16) {
        Serial.print("0");
      }
      Serial.print(address, HEX);
      Serial.print(" (");
      Serial.print(address);
      Serial.print(")");

      // 打印常见设备的地址
      if (address == 0x68 || address == 0x69) {
        Serial.print(" → MPU6050/MPU6500 (Gyro/Accel)");
      } else if (address == 0x3C || address == 0x3D) {
        Serial.print(" → OLED Display");
      } else if (address == 0x50 || address == 0x51) {
        Serial.print(" → EEPROM");
      } else if (address == 0x76 || address == 0x77) {
        Serial.print(" → BME280/BMP280 (Pressure)");
      }

      Serial.println();
      deviceCount++;
    } else if (error == 4) {
      Serial.print("Unknown error at address 0x");
      if (address < 16) {
        Serial.print("0");
      }
      Serial.println(address, HEX);
    }
  }

  if (deviceCount == 0) {
    Serial.println("No I2C devices found");
    Serial.println("Check your wiring!");
  } else {
    Serial.print("Found ");
    Serial.print(deviceCount);
    Serial.println(" device(s)!");
  }

  Serial.println("");
  Serial.println("Waiting 5 seconds before next scan...");
  delay(5000);
}
