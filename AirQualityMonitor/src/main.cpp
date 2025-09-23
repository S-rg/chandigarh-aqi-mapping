#include <Arduino.h>
#include <SensorBase.h>
#include <SO2Sensor.h>


// SO2 Sensor in active upload mode 
HardwareSerial& formalSerial = Serial1;
SO2 SO2Sensor(formalSerial, SerialSensor::HARDWARE_SERIAL, 9600, false);
// Initialize is called within the parent class contructor

void setup() {

}

void loop() {
  SO2Sensor.sendCommand(SO2::getValueCommand, SO2::commandSize);
  delay(1000);
  SO2Sensor.read(true);
  float tvoc_val = SO2Sensor.getValue();
  Serial.print(tvoc_val); Serial.println(" ppm");

  delay(100);
}
