#include <Arduino.h>
#include "SensorsConfig.h"
#include "Base.h"
#include "Sensors.h"
#include "Manager.h"

Manager manager(15);

void setup() {
	delay(1000);

	// Create and start sensors
	manager.createSensors();
	manager.beginSensors();

	Serial.println("[INFO] Manager and sensors initialized\n");
}

void loop() {

	// Do a single poll and print results
	manager.pollAllSensors();
	manager.printLastPolledMeasurements();

	delay(SAMPLING_RATE);
}
