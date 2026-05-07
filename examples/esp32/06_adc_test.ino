/*
 * ESP32测试6: ADC模拟电压读取
 * 用于读取电池电压、模拟传感器等
 * 连接方式：电位器一端到3.3V，一端到GND，中间到GPIO34
 * 或者直接用杜邦线测试不同电压
 */

#define ADC_PIN 34  // ADC输入引脚（GPIO34是输入专用的）

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("ESP32 ADC Test");
  Serial.println("==============");

  Serial.println("ADC Pin: GPIO" + String(ADC_PIN));
  Serial.println("ADC Resolution: 12 bits (0-4095) - default");
  Serial.println("Voltage Reference: 3.3V");
  Serial.println("");
  Serial.println("Connect a voltage source (0-3.3V) to GPIO" + String(ADC_PIN));
}

void loop() {
  // 读取ADC值
  int adcValue = analogRead(ADC_PIN);

  // 转换为电压
  float voltage = (adcValue / 4095.0) * 3.3;

  // 打印结果
  Serial.print("ADC Value: ");
  Serial.print(adcValue);
  Serial.print("  Voltage: ");
  Serial.print(voltage, 3);
  Serial.println(" V");

  // 模拟电池电压检测
  if (voltage > 3.0) {
    Serial.println("  Battery: GOOD ✓");
  } else if (voltage > 2.5) {
    Serial.println("  Battery: LOW ⚠");
  } else {
    Serial.println("  Battery: CRITICAL !");
  }

  delay(500);  // 每500ms读取一次
}
