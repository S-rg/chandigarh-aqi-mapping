#include <Arduino.h>
#include "SensorsConfig.h"
#include "Base.h"
#include "Sensors.h"
#include "Manager.h"

Manager manager;

void setup() {
	delay(1000);
	Serial.begin(115200);

	// Create and start sensors
	manager.createSensors();
	manager.beginSensors();

	Serial.println("Manager and sensors initialized\n");

	// Do a single poll and print results
	manager.poll_once();

	const int BUF = 16;
	RuntimeMeasurement out[BUF];
	uint16_t n = manager.getRecentMeasurements(out, BUF);

	for (uint16_t i = 0; i < n; ++i) {
		Serial.printf("Measurement[%u]: sensor=%u, measurement=%u, value=%.2f, ts=%lu\n",
					  i,
					  out[i].sensor_id,
					  out[i].measurement_id,
					  out[i].value,
					  out[i].timestamp);
	}
}

void loop() {
	// nothing here for now; everything done in setup for a single poll
	delay(1000);
}
