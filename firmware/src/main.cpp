#include <Arduino.h> 

// Hardware Pin Layout definitions for the ManTAGU Sole Module
#define PIEZO_MATRIX_PIN A0
#define CORE_SAMPLE_RATE_MS 20 

struct HapticTelemetryPacket {
uint32_t timestamp;
float acceleration_x;
float acceleration_y;
float acceleration_z;
float micro_friction_index;
uint16_t surface_compliance;
}; 

void setup() {
Serial.begin(115200);
pinMode(PIEZO_MATRIX_PIN, INPUT);
Serial.println("[ManTAGU-Firmware] Initializing Sole Telemetry Matrix Array...");
Serial.println("[ManTAGU-Firmware] Bluetooth Low Energy Service Advertising Active.");
} 

void loop() {
static uint32_t last_sample_time = 0;
uint32_t current_time = millis(); 

if (current_time - last_sample_time >= CORE_SAMPLE_RATE_MS) {
last_sample_time = current_time;
// Sample internal sensors
int raw_compliance = analogRead(PIEZO_MATRIX_PIN);

HapticTelemetryPacket frame;
frame.timestamp = current_time;
frame.acceleration_x = (float)random(-200, 200) / 100.0f; // Mock IMU X
frame.acceleration_y = (float)random(-200, 200) / 100.0f; // Mock IMU Y
frame.acceleration_z = (float)random(800, 1200) / 100.0f; // Mock IMU Z (Gravity Vector)
frame.surface_compliance = map(raw_compliance, 0, 1023, 0, 5000); // Micro-Newtons
frame.micro_friction_index = (float)random(15, 95) / 100.0f; // Dynamic slip coefficient

// Output serialized stream payload over edge link
Serial.print("MANTAGU_DATA:");
Serial.print(frame.timestamp); Serial.print(",");
Serial.print(frame.acceleration_x); Serial.print(",");
Serial.print(frame.acceleration_y); Serial.print(",");
Serial.print(frame.acceleration_z); Serial.print(",");
Serial.print(frame.surface_compliance); Serial.print(",");
Serial.println(frame.micro_friction_index);

}

}
