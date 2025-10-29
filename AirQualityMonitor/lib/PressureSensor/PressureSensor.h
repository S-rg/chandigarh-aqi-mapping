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
        AC1 = (int16_t)((readRegister8(0xaa) << 8) | readRegister8(0xab));
        AC2 = (int16_t)((readRegister8(0xac) << 8) | readRegister8(0xad));
        AC3 = (int16_t)((readRegister8(0xae) << 8) | readRegister8(0xaf));
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
    
    String getName() {
        return String("Bosch BMP180");
    }

    void printCalibrationData() {
        Serial.println("--- Calibration Data ---");
        Serial.print("AC1: "); Serial.println(AC1);
        Serial.print("AC2: "); Serial.println(AC2);
        Serial.print("AC3: "); Serial.println(AC3);
        Serial.print("AC4: "); Serial.println(AC4);
        Serial.print("AC5: "); Serial.println(AC5);
        Serial.print("AC6: "); Serial.println(AC6);
        Serial.print("B1:  "); Serial.println(B1_);
        Serial.print("B2:  "); Serial.println(B2);
        Serial.print("MB:  "); Serial.println(MB);
        Serial.print("MC:  "); Serial.println(MC);
        Serial.print("MD:  "); Serial.println(MD);
        Serial.print("OSS: "); Serial.println(oss);
        Serial.println("------------------------");
    }

    float readRawTemp(bool DEBUG = false) {
    return -1;
    }

    float readCompensatedTemp(bool DEBUG = false) {
        return -1;
    }

    float readRawPressure(bool DEBUG = false) {
        return -1;
    }

    float readCompensatedPressure(bool DEBUG = false) {
        return -1;
    }
};