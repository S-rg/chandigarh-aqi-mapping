#include <Arduino.h>
#include <SensorBase.h>
#include <PressureSensor.h>


// BMP180 
BMP180 pressureSensor(Wire);

void setup() {

}

void loop() {
  float rT = pressureSensor.readRawTemp();
  float cT = pressureSensor.readCompensatedTemp();

  float rP = pressureSensor.readRawPressure();
  float cP = pressureSensor.readCompensatedPressure();

  Serial.print("Raw Temp: ");
  Serial.print(rT);
  Serial.print(" | Compensated Temp: ");
  Serial.print(cT);
  Serial.println(" °C");

  Serial.print("Raw Pressure: ");
  Serial.print(rP);
  Serial.print(" | Compensated Pressure: ");
  Serial.print(cP);
  Serial.println(" Pa");

  delay(100);
}
