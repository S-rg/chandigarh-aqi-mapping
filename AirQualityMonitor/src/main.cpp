#include <Arduino.h>
#include <SensorBase.h>
#include <TVOCSensor.h>
#include <FormaldehydeSensor.h>


SoftwareSerial tvocSerial(0, 1);
TVOC tvocSensor(tvocSerial, SerialSensor::SOFTWARE_SERIAL, 9600);

SoftwareSerial formalSerial(2, 3);
CH2O formalSensor(formalSerial, SerialSensor::SOFTWARE_SERIAL, 9600);

void setup() {
  Serial.println("setup started");
  tvocSensor.initialize();
}

void loop() {
  tvocSensor.sendCommand(TVOC::getValueCommand, TVOC::commandSize);
  delay(100);
  tvocSensor.read();
  float tvoc_val = tvocSensor.getValue();
  Serial.print(tvoc_val); Serial.println(" ppb");

  delay(100);

  formalSensor.sendCommand(CH2O::getValueCommand, CH2O::commandSize);
  delay(10);
  formalSensor.read();
  float val = formalSensor.getValue();
  for (int i = 0; i < 9; i++) {
    Serial.print(formalSensor.response[i], HEX);
    Serial.print(" ");
  }
  Serial.println();
  Serial.print(val); Serial.println(" µg/m^3");  

  delay(3000);
}
