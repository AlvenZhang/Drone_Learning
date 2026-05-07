/*
 * ESP32测试1: LED闪烁
 * 最简单的测试程序，检查ESP32是否正常工作
 */

// ESP32开发板通常有一个板载LED连接到GPIO2
#define LED_PIN 2

void setup() {
  // 初始化串口通信（用于调试）
  Serial.begin(115200);
  delay(1000);
  Serial.println("ESP32 LED Blink Test");
  Serial.println("===================");

  // 配置LED引脚为输出
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  Serial.println("LED ON");
  digitalWrite(LED_PIN, HIGH);  // 点亮LED
  delay(500);                   // 等待500ms

  Serial.println("LED OFF");
  digitalWrite(LED_PIN, LOW);   // 熄灭LED
  delay(500);                   // 等待500ms
}
