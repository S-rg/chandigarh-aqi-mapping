#include "SensorsConfig.h"
#include "Base.h"
#include "Sensors.h"
#include "Factory.h"
#include <iostream>
#include <memory>

class Manager {
private:
    static const int MEASUREMENTS_COUNT = 10;
    RuntimeMeasurement _measurements[MEASUREMENTS_COUNT];
    uint16_t _pos = 0; // current posiiton in _measurements buffer; 

    SensorBase* _sensors[SENSOR_COUNT];

    // Factory instance managed by manager
    SensorFactory* _factory;

    void updatePos(int offset = 1) {
        _pos = (_pos + 1) % MEASUREMENTS_COUNT;
    }

public:
    Manager() {
        _factory = new SensorFactory();
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

    RuntimeMeasurement* poll_once() {
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
        uint16_t lastIndex = (_pos + MEASUREMENTS_COUNT - 1) % MEASUREMENTS_COUNT;
        return &_measurements[lastIndex];
    }

    // Copies up to max measurements into outBuf and returns the number copied.
    // Measurements are returned in chronological order (oldest first).
    uint16_t getRecentMeasurements(RuntimeMeasurement* outBuf, uint16_t max) {
        if (outBuf == nullptr || max == 0) return 0;

        // Determine how many measurements are actually available.
        uint16_t available = MEASUREMENTS_COUNT; // ring buffer is full/rotating; caller should manage freshness
        uint16_t toCopy = (max < available) ? max : available;

        // Compute start index (oldest)
        uint16_t start = (_pos + MEASUREMENTS_COUNT - available) % MEASUREMENTS_COUNT;

        for (uint16_t i = 0; i < toCopy; ++i) {
            outBuf[i] = _measurements[(start + i) % MEASUREMENTS_COUNT];
        }
        return toCopy;
    }
};