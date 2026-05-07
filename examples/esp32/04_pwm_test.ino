/*
 * ESP32测试4: PWM输出测试
 * PWM用于控制电机转速、LED亮度等（无人机必备！）
 * 连接方式：LED串联220Ω电阻到GPIO2，另一端到GND
 * 这个版本兼容性最好！
 */

#define LED_PIN 2       // LED连接到GPIO2

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("ESP32 PWM Test");
  Serial.println("==============");

  // 配置LED引脚
  pinMode(LED_PIN, OUTPUT);

  Serial.println("LED Pin: GPIO" + String(LED_PIN));
  Serial.println("PWM Resolution: 8 bits (0-255) - default");
  Serial.println("");
  Serial.println("LED will fade in and out...");
}

void loop() {
  // LED渐亮
  Serial.println("Fading IN...");
  for (int duty = 0; duty <= 255; duty += 5) {
    analogWrite(LED_PIN, duty);
    Serial.print("Duty: ");
    Serial.println(duty);
    delay(30);
  }

  // LED渐暗
  Serial.println("Fading OUT...");
  for (int duty = 255; duty >= 0; duty -= 5) {
    analogWrite(LED_PIN, duty);
    Serial.print("Duty: ");
    Serial.println(duty);
    delay(30);
  }
}
