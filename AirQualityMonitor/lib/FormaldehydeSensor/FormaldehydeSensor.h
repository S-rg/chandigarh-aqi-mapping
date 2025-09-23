#pragma once
#include "SensorBase.h"

class CH2O : public SerialSensor {
private:
    bool isQAMode = false;
    float _lastValue = 0.0;
    
public:
    // Send Commands
    static const int commandSize = 9;
    static byte qaModeOnCommand[commandSize];
    static byte getValueCommand[commandSize];
    static byte activeUploadModeOnCommand[commandSize];

    // Recieve Response
    static const int responseSize = 9;
    byte response[responseSize];

    CH2O(Stream& serialStream, serialType type, int baudRate, bool qaMode)
        : SerialSensor(serialStream, type, baudRate) {

            if (qaMode) {
                turnQAModeOn();
            } 
            else {
                turnActiveUploadModeOn();
            }
    }

    bool turnQAModeOn() {
        sendCommand(qaModeOnCommand, commandSize);
        delay(1000);
        isQAMode = true;
    }

    bool turnActiveUploadModeOn() {
        sendCommand(activeUploadModeOnCommand, commandSize);
        delay(1000);
        isQAMode = false;
    }

    bool read(bool DEBUG = false) override {
        receiveBytes(response, responseSize, DEBUG);

        processResponse();
        return true;
    }

    bool processResponse() {
        if (isQAMode) {
            // Conc values in 6th byte [HIGH] and 7th byte [LOW]
            uint16_t conc = (response[6] << 8) | response[7]; // Units: ppb
            _lastValue = static_cast<float>(conc);
            return true;
        }

        // Active Mode
        uint16_t conc = (response[4] << 8) | response[5];
        _lastValue = static_cast<float>(conc);
        return true;
    }

    float getValue() override {
        return _lastValue;
    }

    String getName() {
        return String("Dart Sensors WZ-S-K formaldehyde module");
    }
};

byte CH2O::qaModeOnCommand[CH2O::commandSize] = {0xff, 0x01, 0x78, 0x41, 0x00, 0x00, 0x00, 0x00, 0x46};
byte CH2O::activeUploadModeOnCommand[CH2O::commandSize] = {0xff, 0x01, 0x78, 0x40, 0x00, 0x00, 0x00, 0x00, 0x47};
byte CH2O::getValueCommand[CH2O::commandSize] = {0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};