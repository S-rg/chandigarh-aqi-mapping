#pragma once
#include "SensorBase.h"

// Winsen MH-Z19C CO2 Sensor
// Operates on QA mode by default
class CO2 : public SerialSensor {
private:
    float _lastValue = 0.0;

public:
    // Send Commands
    static const int commandSize = 9;
    static byte getValueCommand[commandSize];

    // Recieve Response
    static const int responseSize = 9;
    byte response[responseSize];

    CO2(Stream& serialStream, serialType type, int baudRate)
        : SerialSensor(serialStream, type, baudRate) {
    }

    bool read(bool DEBUG = false) override {
        receiveBytes(response, commandSize, DEBUG);

        processResponse();
        return true;
    }

    bool processResponse() {
        // Conc values in 2th byte [HIGH] and 3th byte [LOW]
        uint16_t conc = (response[2] << 8) | response[3]; // Units: ppm
        _lastValue = static_cast<float>(conc);

        return true;
    }

    float getValue() override {
        return _lastValue;
    }

    String getName() override {
        return String("Winsen MH-Z19C CO2 Sensor");
    }
};

byte CO2::getValueCommand[CO2::commandSize] = {0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};