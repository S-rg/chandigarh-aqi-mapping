#pragma once
#include "DataTypes.h"
#include "SensorsConfig.h"
#include <HardwareSerial.h>
#include <SoftwareSerial.h>
#include <Wire.h>

class CommsInterface {
protected:
	SensorInfo* _cfg;
	CommsType _type;

public:
	CommsInterface(SensorInfo* cfg) : _cfg(cfg) {
		_type = _cfg->comms;
	}
	virtual ~CommsInterface() {}
	virtual void begin() = 0;
};

class SerialInterface : public CommsInterface {
private:
	Stream& _serialStream;
	int _baudRate;

public:
	SerialInterface(SensorInfo* cfg, Stream& serialStream, int baudRate) 
		: CommsInterface(cfg), _serialStream(serialStream), _baudRate(baudRate) {}

	void begin() {
		if (_type == COMM_HARDWARE_SERIAL) {
			HardwareSerial& hw = static_cast<HardwareSerial&>(_serialStream);
			hw.begin(_baudRate);
			_serialStream = hw;
		}
		else if (_type == COMM_SOFTWARE_SERIAL) {
			SoftwareSerial& sw = static_cast<SoftwareSerial&>(_serialStream);
			sw.begin(_baudRate);
			_serialStream = sw;
		}
	}

	void sendBuffer(byte* buffer, int bufferSize) {
		_serialStream.write(buffer, bufferSize);
	}

	void receiveBuffer(byte* buffer, int bufferSize) {
		int bytesRead = 0;

		while (_serialStream.available() > 0 && bytesRead < bufferSize) {
			buffer[bytesRead] = _serialStream.read();
			bytesRead++;
		}

		#if SENSORS_DEBUG == 1 
			for (int i = 0; i < bufferSize; i++) {
				Serial.print(buffer[i]); Serial.print(" ");
			}
			Serial.print("| ");
			for (int i = 0; i < bufferSize; i++) {
				Serial.print(buffer[i], HEX); Serial.print(" ");
			}
			Serial.println();
		#endif
	}
};

class I2CInterface : public CommsInterface {
	uint8_t _address;
	TwoWire& _wire;
	uint32_t _clockSpeed;

	I2CInterface(SensorInfo* cfg, uint8_t address, TwoWire& wire = Wire, uint32_t clockSpeed = 100000) // Hz
		: CommsInterface(cfg), _address(address), _wire(wire), _clockSpeed(clockSpeed) {}

	void begin() override {
		_wire.begin();
		_wire.setClock(_clockSpeed);

		// Test communication by attempting to contact the device
		// _wire.beginTransmission(_address);
		// return (_wire.endTransmission() == 0);
	}
	
	void writeRegister(uint8_t reg, uint8_t value) {
		_wire.beginTransmission(_address);
		_wire.write(reg);
		_wire.write(value);
		_wire.endTransmission();
	}

	uint8_t readRegister(uint8_t reg) {
		_wire.beginTransmission(_address);
		_wire.write(reg);
		_wire.endTransmission(false);
		_wire.requestFrom(_address, (uint8_t)1);
		return _wire.read();
	}
};

class ParserInterface {
	// TODO: Make this
};

class SensorBase {
public:
	virtual ~SensorBase() = default;

	virtual bool begin() = 0;

	// Read available measurements; write up to outcap measurements into out array.
	// Return number of measurements written.
	virtual size_t read(RuntimeMeasurement* out, size_t outcap) = 0;

	virtual const SensorInfo* info() const = 0;
};
