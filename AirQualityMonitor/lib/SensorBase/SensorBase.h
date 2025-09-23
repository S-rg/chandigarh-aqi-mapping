#pragma once
#include <Arduino.h>
#include <HardwareSerial.h>
#include <SoftwareSerial.h>
#include <Wire.h>

class SensorBase {
public:
    virtual ~SensorBase() {}
    virtual bool initialize() = 0;
    virtual bool read(bool DEBUG = false) { return false; }
    virtual bool processResponse() { return false; }
    virtual float getValue() { return -1.0; }
    virtual String getName() = 0;

// Utility Functions
// TODO: Implement I2C sweep function to check addrs
};


class SerialSensor: public SensorBase {
public:
    enum serialType {HARDWARE_SERIAL, SOFTWARE_SERIAL};

    Stream& _serialStream;
    serialType _serialType;
    int _baudRate;

    SerialSensor(Stream& serialStream, serialType type, int baudRate) 
        : _serialStream(serialStream), _serialType(type) {
            _baudRate = baudRate;
            this->initialize();
    }

    ~SerialSensor() override {}

    bool initialize() override {
        if (_serialType == HARDWARE_SERIAL) {
            HardwareSerial& hw = static_cast<HardwareSerial&>(_serialStream);
            hw.begin(_baudRate);
            _serialStream = hw;
        }
        else if (_serialType == SOFTWARE_SERIAL) {
            SoftwareSerial& sw = static_cast<SoftwareSerial&>(_serialStream);
            sw.begin(_baudRate);
            _serialStream = sw;
        }
        else return false;

        return true;
    }

    void sendCommand(byte command[], int commandSize) {
        _serialStream.write(command, commandSize);
    }

    void receiveBytes(byte response[], int responseSize, bool DEBUG = false) {
        int bytesRead = 0;
        
        while (_serialStream.available() > 0 && bytesRead < responseSize) {
            response[bytesRead] = _serialStream.read();
            bytesRead++;
        }

        if (DEBUG) {
            for (int i = 0; i < responseSize; i++) {
                Serial.print(response[i]); Serial.print(" ");
            }
            Serial.print("| ");
            for (int i = 0; i < responseSize; i++) {
                Serial.print(response[i], HEX); Serial.print(" ");
            }
            Serial.println();
        }
    }
};


class I2CSensor : public SensorBase {
public:
    uint8_t _address;
    TwoWire& _wire;
    uint32_t _clockSpeed;
    
    I2CSensor(uint8_t address, TwoWire& wire = Wire, uint32_t clockSpeed = 100000) // Hz 
        : _address(address), _wire(wire), _clockSpeed(clockSpeed) {
            this->initialize();
    }

    ~I2CSensor() override {}

    bool initialize() override {
        _wire.begin();
        _wire.setClock(_clockSpeed);
        
        // Test communication by attempting to contact the device
        _wire.beginTransmission(_address);
        return (_wire.endTransmission() == 0);
    }

    void writeRegister(uint8_t reg, uint8_t value) {
        _wire.beginTransmission(_address);
        _wire.write(reg);
        _wire.write(value);
        _wire.endTransmission();
    }

    uint8_t readRegister8(uint8_t reg) {
        _wire.beginTransmission(_address);
        _wire.write(reg);
        _wire.endTransmission(false);
        _wire.requestFrom(_address, (uint8_t)1);
        return _wire.read();
    }

    uint16_t readRegister16(uint8_t reg) {
        _wire.beginTransmission(_address);
        _wire.write(reg);
        _wire.endTransmission(false);
        _wire.requestFrom(_address, (uint8_t)2);
        uint16_t msb = _wire.read();
        uint16_t lsb = _wire.read();
        return (msb << 8) | lsb;
    }
};
