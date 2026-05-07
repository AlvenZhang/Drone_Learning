/*
 * ESP32测试2: WiFi扫描
 * 测试ESP32的WiFi功能，扫描附近的WiFi网络
 */

#include <WiFi.h>

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("ESP32 WiFi Scan Test");
  Serial.println("====================");

  // 设置为WiFi站点模式
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);

  Serial.println("Scanning WiFi networks...");
}

void loop() {
  // 扫描WiFi网络
  int n = WiFi.scanNetworks();

  Serial.println("");
  if (n == 0) {
    Serial.println("No WiFi networks found");
  } else {
    Serial.print(n);
    Serial.println(" WiFi networks found:");

    for (int i = 0; i < n; ++i) {
      // 打印WiFi名称、信号强度、加密类型
      Serial.print(i + 1);
      Serial.print(": ");
      Serial.print(WiFi.SSID(i));
      Serial.print(" (");
      Serial.print(WiFi.RSSI(i));
      Serial.print(" dBm) ");
      Serial.println(WiFi.encryptionType(i) == WIFI_AUTH_OPEN ? "Open" : "Encrypted");
      delay(10);
    }
  }

  Serial.println("");
  Serial.println("Waiting 5 seconds before next scan...");
  delay(5000);
}
