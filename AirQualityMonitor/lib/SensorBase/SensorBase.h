#pragma once
#include <Arduino.h>
#include <HardwareSerial.h>
#include <SoftwareSerial.h>
#include <Wire.h>

class SensorBase {
public:
    virtual ~SensorBase() {}
    virtual bool initialize() = 0;
    virtual bool read() = 0;
    virtual bool processResponse() = 0;
    virtual float getValue() = 0;
    virtual String getName() = 0;
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

    void receiveBytes(byte response[], int responseSize) {
        int bytesRead = 0;
        
        while (_serialStream.available() > 0 && bytesRead < responseSize) {
            response[bytesRead] = _serialStream.read();
            bytesRead++;
        }
    }
};


class I2CSensor : public SensorBase {
public:
    uint8_t _address;
    TwoWire& _wire;
    uint32_t _clockSpeed;
    
    I2CSensor(uint8_t address, TwoWire& wire = Wire, uint32_t clockSpeed = 100000) 
        : _address(address), _wire(wire), _clockSpeed(clockSpeed) {
    }

    ~I2CSensor() override {}

    bool initialize() override {
        _wire.begin();
        _wire.setClock(_clockSpeed);
        
        // Test communication by attempting to contact the device
        _wire.beginTransmission(_address);
        return (_wire.endTransmission() == 0);
    }
};
