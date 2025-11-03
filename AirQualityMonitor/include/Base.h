/*
Base Classes for
- Sensors
- Comms Interfaces
*/

/*
	TODO: change serialStream to a pointer so you can set it to nullptr in case of problems
	TODO: not return nullptr in I2C begin
*/

#pragma once
#include "DataTypes.h"
#include "SensorsConfig.h"
#include <HardwareSerial.h>
#include <SoftwareSerial.h>
#include <Wire.h>
#include <string>

class CommsInterface {
protected:
	SensorInfo* _cfg;
	CommsType _type;

public:
	CommsInterface(SensorInfo* cfg) : _cfg(cfg) {
		_type = _cfg->comms;
	}
	virtual ~CommsInterface() {}
	virtual CommsInterface* begin() = 0;
};

class SerialInterface : public CommsInterface {
private:
	Stream& _serialStream;
	int _baudRate;

public:
	SerialInterface(SensorInfo* cfg, Stream& serialStream) 
		: CommsInterface(cfg), _serialStream(serialStream) {
			_baudRate = _cfg->baud_rate;
		}

	CommsInterface* begin() {
		if (_type == COMM_HARDWARE_SERIAL) {
			HardwareSerial& hw = static_cast<HardwareSerial&>(_serialStream);
			hw.begin(_baudRate);
			_serialStream = hw;
			return this;
		}
		else if (_type == COMM_SOFTWARE_SERIAL) {
			_serialStream = SoftwareSerial(_cfg->rx_pin, _cfg->tx_pin);
			SoftwareSerial& sw = static_cast<SoftwareSerial&>(_serialStream);
			sw.begin(_baudRate);
			_serialStream = sw;
			return this;
		}
		return nullptr;
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
			Serial.print("[DEBUG] Reponse: ");
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
private:
	uint16_t _address;
	TwoWire& _wire;
	uint32_t _clockSpeed;

public:
	I2CInterface(SensorInfo* cfg, TwoWire& wire = Wire, uint32_t clockSpeed = 100000) // Hz
		: CommsInterface(cfg), _wire(wire), _clockSpeed(clockSpeed) {
			_address = _cfg->i2c_address;
		}

	CommsInterface* begin() override {
		_wire.begin();
		_wire.setClock(_clockSpeed);

		// Test communication by attempting to contact the device
		// _wire.beginTransmission(_address);
		// return (_wire.endTransmission() == 0);
		return nullptr;
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
		_wire.requestFrom(_address, static_cast<size_t>(1)); // There was a warning if i just did (uint_8), gpt did this fix
		return _wire.read();
	}
};

class SensorBase {
protected:
	SensorInfo* _cfg;
	CommsInterface* _comm;
	
	static uint32_t getCurrentTime();
	
public:
	uint32_t delayTime = 100; // ms
	
	SensorBase(SensorInfo* cfg, CommsInterface* comm) : _cfg(cfg), _comm(comm) {
	}

	virtual ~SensorBase() {
		delete _cfg;
		delete _comm;
	};

	virtual bool begin() = 0;

	virtual void read(uint8_t measurement_id, RuntimeMeasurement* buffer) = 0;
	/* If commsType for the sensors is Serial, call one set of functions
	If it is I2C, call another set of funcs for same measurements
	This is to provide functionality for 1 sensor having both comms*/

	virtual const SensorInfo* info() const = 0;
};

uint32_t SensorBase::getCurrentTime() {
	return (uint32_t)millis();
}