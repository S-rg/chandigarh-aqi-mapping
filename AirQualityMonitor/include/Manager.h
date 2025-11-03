#include "SensorsConfig.h"
#include "Base.h"
#include "Sensors.h"
#include "Factory.h"
#include <iostream>
#include <memory>

class Manager {
private:
    int MAX_MEASUREMENTS_COUNT;
    RuntimeMeasurement *_measurements;
    uint16_t _pos = 0; // current posiiton in _measurements buffer; 

    SensorBase* _sensors[SENSOR_COUNT];

    // Factory instance managed by manager
    SensorFactory* _factory;

    float updatePos(int offset = 1) {
        _pos = (_pos + 1) % MAX_MEASUREMENTS_COUNT;

        // Calculate % buffer filled
        static uint32_t totalWrites = 0;
        totalWrites += (uint32_t)offset;
        uint32_t filledSlots = (totalWrites >= (uint32_t)MAX_MEASUREMENTS_COUNT) ? (uint32_t)MAX_MEASUREMENTS_COUNT : totalWrites;
        return (float)filledSlots * 100.0f / (float)MAX_MEASUREMENTS_COUNT;
    }

public:
    Manager(int NUM_MEAS=10) : MAX_MEASUREMENTS_COUNT(NUM_MEAS) {
        _factory = new SensorFactory();
        _measurements = new RuntimeMeasurement[MAX_MEASUREMENTS_COUNT];
    }

    ~Manager() {
        delete _factory;
    }

    void createSensors() {
        for (int i = 0; i < SENSOR_COUNT; i++) {
            _sensors[i] = _factory->createSensor((SensorInfo*)&sensors_config[i]);
        }
    }

    void beginSensors() {
        for (size_t i = 0; i < SENSOR_COUNT; ++i) {
            SensorBase* sensor = _sensors[i];
            if (sensor == nullptr) continue;
            sensor->begin();
        }
    }

    RuntimeMeasurement* poll_all_sensors() {
        for (size_t i = 0; i < SENSOR_COUNT; ++i) {
            SensorBase* sensor = _sensors[i];
            if (sensor == nullptr) continue;

            const SensorInfo* info = sensor->info();
            if (info == nullptr || info->measurements == nullptr) continue;

            // Iterate measurements using the provided measurement_count
            for (uint8_t m = 0; m < info->measurement_count; ++m) {
                const MeasurementInfo& measurement_info = info->measurements[m];
                _measurements[_pos].measurement_id = measurement_info.measurement_id;
                // initialize timestamp/value before reading
                _measurements[_pos].timestamp = 0;
                _measurements[_pos].value = 0.0f;

                // ask the sensor to populate this measurement
                sensor->read(measurement_info.measurement_id, &_measurements[_pos]);

                updatePos(1);
            }
        }

        // Return pointer to the most-recent measurement slot (previous position)
        // Compute last written index
        uint16_t lastIndex = (_pos + MAX_MEASUREMENTS_COUNT - 1) % MAX_MEASUREMENTS_COUNT;
        return &_measurements[lastIndex];
    }

    
};