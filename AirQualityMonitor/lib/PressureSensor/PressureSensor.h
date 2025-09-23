#pragma once
#include <SensorBase.h>

class BMP180: public I2CSensor {
private:
    const uint8_t CONTROL_REGISTER = 0xf4;
    const uint8_t TEMP_MEASURE_CMD = 0x2e;
    const uint8_t PRESSURE_MEASURE_CMD = 0x34;

    // Calibration Data
    int16_t AC1, AC2, AC3;
    uint16_t AC4, AC5, AC6;
    int16_t B1_, B2, MB, MC, MD;

    uint8_t oss; // Oversampling setting

    // Private method to read calibration data
    void readCalibrationData() {
        AC1 = (int16_t)this->readRegister16(0xaa);
        AC2 = (int16_t)this->readRegister16(0xac);
        AC3 = (int16_t)this->readRegister16(0xae);
        AC4 = this->readRegister16(0xb0);
        AC5 = this->readRegister16(0xb2);
        AC6 = this->readRegister16(0xb4);
        B1_ = (int16_t)this->readRegister16(0xb6);
        B2 = (int16_t)this->readRegister16(0xb8);
        MB = (int16_t)this->readRegister16(0xba);
        MC = (int16_t)this->readRegister16(0xbc);
        MD = (int16_t)this->readRegister16(0xbe);
    }

public:
    BMP180(TwoWire& wire = Wire, uint8_t address = 0x77, uint32_t clockSpeed = 100000) 
        : I2CSensor(address, wire, clockSpeed) {
            readCalibrationData();
        }

    float readRawTemp(bool DEBUG = false) {
        this->writeRegister(CONTROL_REGISTER, TEMP_MEASURE_CMD);
        delay(5);
        uint16_t ut = (this->readRegister16(0xf6));
        if (DEBUG) Serial.println(ut);
        return (float)ut;
    }

    float readCompensatedTemp(bool DEBUG = false) {
        int32_t ut = (int32_t)readRawTemp();

        int32_t X1 = ((ut - AC6) * AC5) >> 15;
        int32_t X2 = ((int32_t)MC << 11) / (X1 + MD);
        int32_t B5 = X1 + X2;
        float t = (B5 + 8) >> 4;
        t /= 10.0;
        if (DEBUG) Serial.println(t);
        return t;
    }

    float readRawPressure(bool DEBUG = false) {
        this->writeRegister(CONTROL_REGISTER, PRESSURE_MEASURE_CMD);
        delay(5);
        uint32_t up = 0;
        up = ((uint32_t)this->readRegister8(0xf6) << 16) | ((uint32_t)this->readRegister8(0xf7) << 8) | (uint32_t)this->readRegister8(0xf8);
        up >>= (8 - 0);
        if (DEBUG) Serial.println(up);
        return (float)up;
    }

    float readCompensatedPressure(bool DEBUG = false) {
        int32_t ut = (int32_t)readRawTemp();
        int32_t up = (int32_t)readRawPressure();
        
        int32_t X1 = ((ut - AC6) * AC5) >> 15;
        int32_t X2 = ((int32_t)MC << 11) / (X1 + MD);
        int32_t B5 = X1 + X2;
        int32_t B6 = B5 - 4000;
        X1 = (B2 * (B6 * B6 >> 12)) >> 11;
        X2 = (AC2 * B6) >> 11;
        int32_t X3 = X1 + X2;
        int32_t B3 = (((((int32_t)AC1) * 4 + X3) << 0) + 2) >> 2;
        X1 = (AC3 * B6) >> 13;
        X2 = (B1_ * ((B6 * B6) >> 12)) >> 16;
        X3 = ((X1 + X2) + 2) >> 2;
        uint32_t B4 = (AC4 * (uint32_t)(X3 + 32768)) >> 15;
        uint32_t B7 = ((uint32_t)up - B3) * (50000 >> 0);
        int32_t p;
        if (B7 < 0x80000000) p = (B7 << 1) / B4;
        else p = (B7 / B4) << 1;
        X1 = (p >> 8) * (p >> 8);
        X1 = (X1 * 3038) >> 16;
        X2 = (-7357 * p) >> 16;
        p = p + ((X1 + X2 + 3791) >> 4);
        if (DEBUG) Serial.println(p);
        return (float)p;
    }

    String getName() {
        return String("Bosch BMP180");
    }
};