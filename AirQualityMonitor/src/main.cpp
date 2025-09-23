#include <Arduino.h>
#include <SensorBase.h>
#include <FormaldehydeSensor.h>


// CH2O Sensor in active upload mode 
HardwareSerial& formalSerial = Serial1;
CH2O formalSensor(formalSerial, SerialSensor::HARDWARE_SERIAL, 9600, true);

void setup() {
  Serial.println("setup started");
  formalSensor.initialize();
}

void loop() {
  formalSensor.sendCommand(CH2O::getValueCommand, CH2O::commandSize);
  delay(1000);
  formalSensor.read(true);
  float tvoc_val = formalSensor.getValue();
  Serial.print(tvoc_val); Serial.println(" ppb");

  delay(100);
}
