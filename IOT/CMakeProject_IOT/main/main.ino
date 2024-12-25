#include <WiFi.h>
#include <ESP32CAM.h>
#include <HTTPClient.h>

// Konfigurasi WiFi
const char* ssid = "red";
const char* password = "ganggangpb";

// Pin untuk Traffic Light dan Buzzer
int redPin = 33;
int yellowPin = 32;
int greenPin = 35;
int buzzerPin = 15;

void setup() {
  Serial.begin(115200);
  
  // Setup WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Setup Traffic Light Pins
  pinMode(redPin, OUTPUT);
  pinMode(yellowPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);

  // Setup Camera
  if (!camera.begin()) {
    Serial.println("Camera initialization failed");
    return;
  }
}

void loop() {
  // Ambil gambar dari kamera
  camera_fb_t *fb = camera.capture();
  if (fb) {
    // Kirim gambar ke server deep learning untuk deteksi wajah
    HTTPClient http;
    http.begin("http://localhost:5000/upload");
    http.addHeader("Content-Type", "application/octet-stream");
    int httpResponseCode = http.POST(fb->buf, fb->len);
    if (httpResponseCode == 200) {
      String response = http.getString();
      if (response == "recognized") {
        digitalWrite(greenPin, HIGH);  // Hijau: buka pintu
      } else {
        digitalWrite(redPin, HIGH);    // Merah: tutup pintu
        digitalWrite(buzzerPin, HIGH); // Buzzer aktif
      }
    }
    http.end();
  }
  delay(10000);  // Delay 10 detik sebelum mengambil gambar lagi
}
