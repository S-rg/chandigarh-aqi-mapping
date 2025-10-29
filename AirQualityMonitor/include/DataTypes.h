#pragma once
#include <cstdint>
#include <cstddef>


typedef enum {
  COMM_HARDWARE_SERIAL = 0,
  COMM_SOFTWARE_SERIAL = 1,
  COMM_I2C = 2,
  COMM_UNKNOWN = 3
} CommsType;



struct RuntimeMeasurement {
    uint16_t sensor_id;
    uint8_t measurement_id;
    float value;
    uint32_t timestamp;  
};