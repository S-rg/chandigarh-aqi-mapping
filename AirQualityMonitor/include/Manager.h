#include "SensorsConfig.h"
#include "Base.h"
#include "Sensors.h"
#include "Factory.h"
#include <iostream>
#include <memory>
#include <cstring> // for memset

/**
 * @brief Manager Class to create and poll sensors.
 * Currently, when the buffer is filled above a threshold, the _pos 
 * counter is reset to zero and new data will be written to the start 
 * of the buffer.
 */

class Manager {
private:
    int MAX_MEASUREMENTS_COUNT;
    RuntimeMeasurement *_measurements;
    uint16_t _pos = 0; // current position in _measurements buffer;
    uint16_t _change_in_pos = 0; // how many positions _pos has moved;
    static uint32_t _totalWrites;
    uint16_t _lastPolledIndex = 0;

    SensorBase* _sensors[SENSOR_COUNT];

    // Factory instance managed by manager
    SensorFactory* _factory;

    float updatePos(int offset = 1) {
        // Calculate % buffer filled BEFORE incrementing _pos
        _totalWrites += (uint32_t)offset;
        uint32_t filledSlots = (_totalWrites >= (uint32_t)MAX_MEASUREMENTS_COUNT) ? (uint32_t)MAX_MEASUREMENTS_COUNT : _totalWrites;
        float percentFilled = (float)filledSlots * 100.0f / (float)MAX_MEASUREMENTS_COUNT;

        // Only increment _pos after checking threshold and possible reset
        _pos = (_pos + offset) % MAX_MEASUREMENTS_COUNT;
        if (SENSORS_DEBUG) {
            Serial.printf("[DEBUG] Updated _pos: %u, _totalWrites: %u\n", _pos, _totalWrites);
        }
        return percentFilled;
    }

public:
    Manager(int NUM_MEAS=10) : MAX_MEASUREMENTS_COUNT(NUM_MEAS) {
        _factory = new SensorFactory();
        _measurements = new RuntimeMeasurement[MAX_MEASUREMENTS_COUNT];
        _totalWrites = 0;
        initializeBuffer();
    }

    ~Manager() {
        delete _factory;
    }

    void initializeBuffer() {
        std::memset(_measurements, 0, sizeof(RuntimeMeasurement) * MAX_MEASUREMENTS_COUNT);
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

    RuntimeMeasurement* pollAllSensors() {
        uint16_t measurements_written = 0;
        _change_in_pos = 0;
        bool stop = false;
        uint16_t lastIndex = _pos; // fallback

        for (size_t i = 0; i < SENSOR_COUNT && !stop; ++i) {
            SensorBase* sensor = _sensors[i];
            if (sensor == nullptr) continue;

            const SensorInfo* info = sensor->info();
            if (info == nullptr || info->measurements == nullptr) {
                Serial.printf("[FATAL] info or info->measurements is nullptr for SensorCount = %i\n", i);
                continue;
            }
            
            if(SENSORS_DEBUG) {
                Serial.printf("[DEBUG] Reading Sensor %f\n", info->config_key);
            }

            for (uint8_t m = 0; m < info->measurement_count; ++m) {
                // Capture the slot we will write to BEFORE changing _pos
                uint16_t writeIndex = _pos;

                // Fill the measurement at writeIndex
                _measurements[writeIndex].sensor_id = info->sensor_id;
                _measurements[writeIndex].measurement_id = info->measurements[m].measurement_id;
                _measurements[writeIndex].timestamp = 0;
                _measurements[writeIndex].value = -1.0f;

                sensor->read(info->measurements[m].measurement_id, &_measurements[writeIndex]);

                ++measurements_written;

                float percent = updatePos(); // advances _pos and _totalWrites

                // remember this as the last written slot
                lastIndex = writeIndex;
                _lastPolledIndex = writeIndex;

                if (handleBufferThresholdFilled(percent, 0.90f)) {
                    // If you want to zero/clear the buffer when threshold reached, do it AFTER
                    // recording lastIndex/_lastPolledIndex, so printing stays correct.
                    _pos = 0;
                    _totalWrites = 0;
                    if (SENSORS_DEBUG) {
                        Serial.printf("Buffer filled: %f\n", percent);
                    }
                    stop = true;
                    break; // exit inner loop
                }
            }
        }

        _change_in_pos = measurements_written;
        return &_measurements[lastIndex];
    }



    bool handleBufferThresholdFilled(float percentFilled, float threshold = 70.0) {
        if (threshold < 1.0) threshold *= 100;
        if (percentFilled >= threshold) {
            if (SENSORS_DEBUG) {
                Serial.printf("Buffer threshold reached: %f\n", percentFilled);
            }
            return true;
        }
        return false;
    }


    // Always get the last valid measurement index safely
    uint16_t getLastValidIndex() const {
        return (_pos + MAX_MEASUREMENTS_COUNT - 1) % MAX_MEASUREMENTS_COUNT;
    }

    void printLastMeasurement() {
        if (MAX_MEASUREMENTS_COUNT == 0) return;
        uint16_t lastIndex = _lastPolledIndex;
        const RuntimeMeasurement &m = _measurements[lastIndex];

        Serial.printf("[MEAS-NODE-%s] Measurement[%u]: sensor=%u, measurement=%u, value=%.2f, ts=%lu\n",
                    NODE_ID,
                    lastIndex,
                    m.sensor_id,
                    m.measurement_id,
                    m.value,
                    m.timestamp);
    }

    void printLastPolledMeasurements() {
        if (MAX_MEASUREMENTS_COUNT == 0) return;
        uint16_t lastIndex = _lastPolledIndex;
        uint16_t count = _change_in_pos ? _change_in_pos : 1;
        for (uint16_t i = 0; i < count; ++i) {
            uint16_t idx = (lastIndex + MAX_MEASUREMENTS_COUNT - i) % MAX_MEASUREMENTS_COUNT;
            const RuntimeMeasurement &m = _measurements[idx];
            Serial.printf("[MEAS-NODE-%s] Measurement[%u]: sensor=%u, measurement=%u, value=%.2f, ts=%lu\n",
                        NODE_ID,
                        idx,
                        m.sensor_id,
                        m.measurement_id,
                        m.value,
                        m.timestamp);
        }
    }


    void printFullBuffer() {
        for (uint16_t i = 0; i < MAX_MEASUREMENTS_COUNT; i++) {
            const RuntimeMeasurement &m = _measurements[i];

            Serial.printf("[MEAS-NODE-%s] Measurement[%u]: sensor=%u, measurement=%u, value=%.2f, ts=%lu\n",
                        NODE_ID,
                        i,
                        m.sensor_id,
                        m.measurement_id,
                        m.value,
                        m.timestamp);
        }
    }

};

// Define the static member variable
uint32_t Manager::_totalWrites = 0;
