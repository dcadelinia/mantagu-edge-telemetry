/**
 * ManTAGU sole edge firmware sketch (ESP32 / Arduino-style).
 * Streams MANTAGU_DATA packets over Serial for the Python ingestion pipeline.
 * Copyright (c) 2026 Odynex Axis Logistics LLC.
 */

#include <Arduino.h>

static const int PIEZO_MATRIX_PIN = 34;
static const unsigned long CORE_SAMPLE_RATE_MS = 20; // 50 Hz

struct HapticTelemetryPacket {
  unsigned long timestamp;
  float acceleration_x;
  float acceleration_y;
  float acceleration_z;
  int surface_compliance;
  float micro_friction_index;
};

void setup() {
  Serial.begin(115200);
  pinMode(PIEZO_MATRIX_PIN, INPUT);
  randomSeed(analogRead(0));
  Serial.println("MANTAGU_BOOT:OK");
}

void loop() {
  static unsigned long last_sample_time = 0;
  unsigned long current_time = millis();

  if (current_time - last_sample_time >= CORE_SAMPLE_RATE_MS) {
    last_sample_time = current_time;

    int raw_compliance = analogRead(PIEZO_MATRIX_PIN);

    HapticTelemetryPacket frame;
    frame.timestamp = current_time;
    frame.acceleration_x = (float)random(-200, 200) / 100.0f;
    frame.acceleration_y = (float)random(-200, 200) / 100.0f;
    frame.acceleration_z = (float)random(800, 1200) / 100.0f;
    frame.surface_compliance = map(raw_compliance, 0, 1023, 0, 5000);
    frame.micro_friction_index = (float)random(15, 95) / 100.0f;

    Serial.print("MANTAGU_DATA:");
    Serial.print(frame.timestamp);
    Serial.print(",");
    Serial.print(frame.acceleration_x);
    Serial.print(",");
    Serial.print(frame.acceleration_y);
    Serial.print(",");
    Serial.print(frame.acceleration_z);
    Serial.print(",");
    Serial.print(frame.surface_compliance);
    Serial.print(",");
    Serial.println(frame.micro_friction_index);
  }
}
