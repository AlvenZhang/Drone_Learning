/*
 * ESP32测试7: 舵机控制测试（PWM）
 * 舵机也是PWM控制的一种，和电机控制类似
 * 连接方式：
 * - 舵机信号线 → GPIO18
 * - 舵机VCC → 5V（注意：有些小舵机可以用3.3V）
 * - 舵机GND → GND
 */

#include <ESP32Servo.h>

#define SERVO_PIN 18  // 舵机信号线连接到GPIO18

Servo myServo;  // 创建舵机对象

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("ESP32 Servo Test");
  Serial.println("================");

  // 绑定舵机到引脚
  myServo.attach(SERVO_PIN);

  Serial.println("Servo connected to GPIO" + String(SERVO_PIN));
  Serial.println("Servo will move from 0° to 180°");
  Serial.println("");
}

void loop() {
  // 从0度转到180度
  Serial.println("Moving from 0° to 180°...");
  for (int angle = 0; angle <= 180; angle += 10) {
    myServo.write(angle);
    Serial.print("Angle: ");
    Serial.print(angle);
    Serial.println("°");
    delay(200);
  }

  delay(500);

  // 从180度转回到0度
  Serial.println("Moving from 180° to 0°...");
  for (int angle = 180; angle >= 0; angle -= 10) {
    myServo.write(angle);
    Serial.print("Angle: ");
    Serial.print(angle);
    Serial.println("°");
    delay(200);
  }

  delay(1000);
}
