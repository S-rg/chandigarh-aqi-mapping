// TVOC.h
#pragma once
#include "SensorBase.h"

class TVOC : public SerialSensor {
private:
    bool isQAMode = false;
    float _lastValue = 0.0;

public:
    static const int commandSize = 9;
    // Send Commands
    static byte qaModeOnCommand[commandSize];
    static byte getValueCommand[commandSize];

    // Recieve Response
    static const int responseSize = 9;
    byte response[responseSize];

    TVOC(Stream& serialStream, serialType type, int baudRate)
        : SerialSensor(serialStream, type, baudRate) {
            Serial.println("Contructor TVOC started");
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
        // Conc values in 6th byte [HIGH] and 7th byte [LOW]
        uint16_t conc = (response[6] << 8) | response[7]; // Units: ppb
        _lastValue = static_cast<float>(conc);

        return true;
    }

    float getValue() override {
        return _lastValue;
    }

    String getName() {
        return String("ZE40A-TVOC");
    }
};

byte TVOC::qaModeOnCommand[TVOC::commandSize] = {0xff, 0x01, 0x78, 0x41, 0x00, 0x00, 0x00, 0x00, 0x46};
byte TVOC::getValueCommand[TVOC::commandSize] = {0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};