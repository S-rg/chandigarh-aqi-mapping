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

    // Recieve Response
    static const int responseSize = 9;
    byte response[responseSize];

    CH2O(Stream& serialStream, serialType type, int baudRate)
        : SerialSensor(serialStream, type, baudRate) {

            if (!isQAMode) {
                // Switch to QA mode by sending the command
                sendCommand(qaModeOnCommand, commandSize);
                isQAMode = true;
            }
    }

    bool read() override {
        receiveBytes(response, commandSize);

        processResponse();
        return true;
    }

    bool processResponse() {
        // Conc values in 2th byte [HIGH] and 3th byte [LOW]
        uint16_t conc = (response[6] << 8) | response[7]; // Units: µg / m^3
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
byte CH2O::getValueCommand[CH2O::commandSize] = {0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};