#include <Arduino.h>
#include <unity.h>
#include "DFRobot_MultiGasSensor.h"

#define I2C1 Wire1
// DFRobot_GAS_I2C so2Sensor(&I2C1, 0x74);
DFRobot_GAS_HardWareUart so2Sensor(&Serial1);

void test_so2_sensor_readings() {
    Serial.println("[TEST] Starting SO2 sensor test...");

    bool isAvailable = so2Sensor.begin();
    Serial.print("[DEBUG] Sensor begin() returned: ");
    Serial.println(isAvailable);
    TEST_ASSERT_TRUE_MESSAGE(isAvailable, "SO2 Sensor is not available on the I2C bus");

    // bool dataAvailable = so2Sensor.dataIsAvailable();
    // Serial.print("[DEBUG] dataIsAvailable() = ");
    // Serial.println(dataAvailable);
    // TEST_ASSERT_TRUE_MESSAGE(dataAvailable, "No data available from the SO2 sensor");

    float concentration = so2Sensor.readGasConcentrationPPM();
    Serial.print("[DEBUG] Concentration = ");
    Serial.println(concentration);
    TEST_ASSERT_TRUE_MESSAGE(concentration >= 0, "Invalid SO2 concentration reading");
}

void setup() {
    Serial.begin(115200);
    delay(2000); // Give time for host to connect
    I2C1.begin();

    UNITY_BEGIN();
    RUN_TEST(test_so2_sensor_readings);
    UNITY_END();
}

void loop() {}
