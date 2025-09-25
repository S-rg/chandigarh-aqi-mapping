#include <Arduino.h>
#include <Wire.h>
#include <unity.h>

#define BMP180_ADDR 0x77

uint16_t read16(uint8_t addr, uint8_t reg);

void test_wire_init(void) {
    Wire.begin();
}

void test_read_calibration(void) {
    Wire.begin();
    uint16_t val = read16(BMP180_ADDR, 0xAA);
    
    // Calibration coefficients are not all 0 or 2^16
    TEST_ASSERT_NOT_EQUAL(val, 0x0000);
    TEST_ASSERT_NOT_EQUAL(val, 0xFFFF);
}

// --- UNITY ENTRYPOINT ---
void setup() {
    delay(2000);
    Serial.begin(9600);
    UNITY_BEGIN();

    RUN_TEST(test_wire_init);
    RUN_TEST(test_read_calibration);

    UNITY_END();
}

void loop() {
    // not used
}

// Utility function
uint16_t read16(uint8_t addr, uint8_t reg) {
    Wire.beginTransmission(addr);
    Wire.write(reg);
    TEST_ASSERT_EQUAL(Wire.endTransmission(), 0);

    Wire.requestFrom(addr, (uint8_t)2);
    TEST_ASSERT_EQUAL(Wire.available(), 2);

    uint8_t msb = Wire.read();
    uint8_t lsb = Wire.read();
    return (uint16_t)(msb << 8 | lsb);
}
