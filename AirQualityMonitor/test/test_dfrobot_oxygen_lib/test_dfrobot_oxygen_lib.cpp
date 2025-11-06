#include <Arduino.h>
#include <unity.h>
#include "DFRobot_OxygenSensor.h"

// Create an instance of the sensor on Wire2 with address 0x73
extern TwoWire Wire2; // Use the predefined Wire2 instance for Teensy 4.1
DFRobot_OxygenSensor oxygenSensor(&Wire2);

void test_getOxygenData() {
    // Initialize the sensor
    bool initialized = oxygenSensor.begin(0x73);
    TEST_ASSERT_TRUE_MESSAGE(initialized, "Sensor initialization failed");

    // Get oxygen data with a collection number of n
    float oxygenReading = oxygenSensor.getOxygenData(1);
    float key = oxygenSensor.getKey();

    // Print the oxygen reading value
    Serial.print("Oxygen Reading: ");
    Serial.print(oxygenReading);
    Serial.print(" | Key: ");
    Serial.println(key);

    // Check if the reading is within a reasonable range (0-100%)
    TEST_ASSERT_TRUE_MESSAGE(oxygenReading >= 0 && oxygenReading <= 100, "Oxygen reading out of range");
    // Check if key is not equal to 20.9 / 120.0
    TEST_ASSERT_NOT_EQUAL_MESSAGE(key, 20.9f / 120.0f, "Key should not be equal to 20.9 / 120.0");
}

void setup() {
    // Initialize Serial for debugging
    Serial.begin(9600);
    while (!Serial) {
        ; // Wait for Serial to be ready
    }

    // Initialize Wire2
    Wire2.begin(); // Correct initialization for Wire2 on Teensy 4.1

    // Begin Unity testing
    UNITY_BEGIN();

    // Add the test case
    RUN_TEST(test_getOxygenData);

    // End Unity testing
    UNITY_END();
}

void loop() {
    // Empty loop
}

