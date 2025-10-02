#pragma once
#include "SensorBase.h"

class SO2 : public SerialSensor {
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

    SO2(Stream& serialStream, serialType type, int baudRate, bool qaMode)
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

        return true;
    }

    bool turnActiveUploadModeOn() {
        sendCommand(activeUploadModeOnCommand, commandSize);
        delay(1000);
        isQAMode = false;

        return true;
    }

    bool read(bool DEBUG = false) override {
        receiveBytes(response, responseSize, DEBUG);

        processResponse();
        return true;
    }

    bool processResponse() {
        if (isQAMode) {
            uint16_t conc = (response[2] << 8) | response[3]; // Units: ppm
            _lastValue = static_cast<float>(conc);
            return true;
        }

        // Active Mode
        uint16_t conc = (response[2] << 8) | response[3]; // Units: ppm
        _lastValue = static_cast<float>(conc);
        return true;
    }

    float getValue() override {
        return _lastValue;
    }

    String getName() {
        return String("Winsen ZE03 SO2");
    }
};

byte SO2::qaModeOnCommand[SO2::commandSize] = {0xff, 0x01, 0x78, 0x04, 0x00, 0x00, 0x00, 0x00, 0x83};
byte SO2::activeUploadModeOnCommand[SO2::commandSize] = {0xff, 0x01, 0x78, 0x03, 0x00, 0x00, 0x00, 0x00, 0x84};
byte SO2::getValueCommand[SO2::commandSize] = {0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};