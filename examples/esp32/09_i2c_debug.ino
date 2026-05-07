/*
 * ESP32 I2C调试工具
 * 读取并显示I2C设备的所有寄存器
 */

#include <Wire.h>

#define I2C_ADDR 0x69  // 改成你的设备地址

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("ESP32 I2C Debug Tool");
  Serial.println("=====================");

  Wire.begin();

  // 读取前128个寄存器
  Serial.print("Reading registers from 0x00 to 0x7F at address 0x");
  Serial.println(I2C_ADDR, HEX);
  Serial.println();

  Serial.println("Register dump:");
  Serial.println("-------------");

  for (uint8_t reg = 0; reg < 0x80; reg++) {
    Wire.beginTransmission(I2C_ADDR);
    Wire.write(reg);
    Wire.endTransmission();

    Wire.requestFrom(I2C_ADDR, 1);
    if (Wire.available()) {
      uint8_t val = Wire.read();

      // 每行显示16个寄存器
      if (reg % 16 == 0) {
        Serial.println();
        Serial.print("0x");
        if (reg < 0x10) Serial.print("0");
        Serial.print(reg, HEX);
        Serial.print(": ");
      }

      if (val < 0x10) Serial.print("0");
      Serial.print(val, HEX);
      Serial.print(" ");
    }
    delay(1);
  }

  Serial.println();
  Serial.println();
  Serial.println("Done! Now trying simple read test...");
  Serial.println();
}

void loop() {
  // 简单读取前20个寄存器，看看有没有变化
  Serial.println("Reading registers 0x00-0x1F...");

  for (uint8_t reg = 0; reg < 0x20; reg++) {
    Wire.beginTransmission(I2C_ADDR);
    Wire.write(reg);
    Wire.endTransmission();

    Wire.requestFrom(I2C_ADDR, 1);
    if (Wire.available()) {
      uint8_t val = Wire.read();

      Serial.print("0x");
      if (reg < 0x10) Serial.print("0");
      Serial.print(reg, HEX);
      Serial.print(" = 0x");
      if (val < 0x10) Serial.print("0");
      Serial.print(val, HEX);

      if (reg == 0x00) {
        Serial.print("  <-- CHIP ID");
      }
      Serial.println();
    }
  }

  Serial.println();
  Serial.println("----------------------------------------");
  Serial.println();
  delay(2000);
}
