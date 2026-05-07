/*
 * ESP32测试3: GPIO输入输出测试
 * 测试数字引脚的输入和输出功能
 * 连接方式：
 * - LED串联220Ω电阻到GPIO4，另一端到GND
 * - 按键一端连GPIO5，另一端连GND
 */

#define LED_PIN 4      // LED连接到GPIO4
#define BUTTON_PIN 5   // 按键连接到GPIO5

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("ESP32 GPIO Test");
  Serial.println("===============");

  // 配置LED引脚为输出
  pinMode(LED_PIN, OUTPUT);

  // 配置按键引脚为输入，启用内部上拉电阻
  // 这样按键按下时是LOW，松开时是HIGH
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  Serial.println("LED_PIN: " + String(LED_PIN) + " (OUTPUT)");
  Serial.println("BUTTON_PIN: " + String(BUTTON_PIN) + " (INPUT_PULLUP)");
  Serial.println("Press the button to control the LED!");
}

void loop() {
  // 读取按键状态
  int buttonState = digitalRead(BUTTON_PIN);

  if (buttonState == LOW) {
    // 按键按下
    Serial.println("Button PRESSED - LED ON");
    digitalWrite(LED_PIN, HIGH);
  } else {
    // 按键松开
    Serial.println("Button RELEASED - LED OFF");
    digitalWrite(LED_PIN, LOW);
  }

  delay(100);  // 延时100ms，避免串口刷屏太快
}
