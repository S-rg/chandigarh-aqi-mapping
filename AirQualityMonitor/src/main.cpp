#include <Arduino.h>
#include "SensorsConfig.h"
#include "Base.h"
#include "Sensors.h"

const SensorInfo *tvoc_cfg = &sensors_config[0];
SensorBase *tvoc;
RuntimeMeasurement measurement;

void setup()
{
	delay(1000);
	// Create a TVOC Sensor
	tvoc = new TVOCSensor((SensorInfo *)tvoc_cfg);
	Serial.printf("Created sensor: %s (%s)\n",
				  tvoc_cfg->part_name, tvoc_cfg->type);

	// // Init sensor
	tvoc->begin();
	// delay(200);

	// measurement.sensor_id = SENSOR_ID_TVOCSENSOR;
	// measurement.measurement_id = MEAS_TVOCSENSOR_TVOC;
	Serial.printf("Hello This is a test\n");
}

void loop()
{
	tvoc->read(1, &measurement);
	Serial.printf("Measurement from sensor %u: value=%.2f, timestamp=%lu\n",
                measurement.sensor_id,
                measurement.value,
                measurement.timestamp);
	delay(1000);
}
