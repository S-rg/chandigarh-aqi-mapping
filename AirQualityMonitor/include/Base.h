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

	// Reads a single byte from the serial stream, blocking until available
	int readByte() {
		while (_serialStream.available() == 0) {
			// Optionally add a timeout here if needed
		}
		return _serialStream.read();
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

			if (SENSORS_DEBUG) sweep_i2c(_wire);
		}

	static void sweep_i2c(TwoWire& wire) {
		wire.begin();

		char found[128] = {0};
		// Print which Wire instance is being used (if possible)
		#if defined(ARDUINO_TEENSY41) || defined(ARDUINO_TEENSY40) || defined(ARDUINO_TEENSY36) || defined(ARDUINO_TEENSY35) || defined(ARDUINO_TEENSY31) || defined(ARDUINO_TEENSY32) || defined(ARDUINO_TEENSY30)
			if (&wire == &Wire) {
				Serial.println("[DEBUG] Scanning I2C bus: Wire");
			} else if (&wire == &Wire1) {
				Serial.println("[DEBUG] Scanning I2C bus: Wire1");
			} else if (&wire == &Wire2) {
				Serial.println("[DEBUG] Scanning I2C bus: Wire2");
			} else {
				Serial.println("[DEBUG] Scanning I2C bus: Unknown Wire instance");
			}
		#else
			Serial.println("[DEBUG] Scanning I2C bus (Wire instance, name unknown on this platform)");
		#endif
		int count = 0;
		for (uint8_t address = 1; address < 127; address++) {
			wire.beginTransmission(address);
			uint8_t error = wire.endTransmission();
			if (error == 0) {
				found[address] = 1;
				count++;
			}
		}
		for (uint8_t row = 0; row < 8; row++) {
			for (uint8_t col = 0; col < 16; col++) {
				uint8_t addr = row * 16 + col;
				if (addr == 0 || addr >= 127) {
					Serial.print("   ");
					continue;
				}
				if (found[addr]) {
					Serial.printf("%02X ", addr);
				} else {
					Serial.print("-- ");
				}
			}
			Serial.println();
		}

		wire.end();
	}

	CommsInterface* begin() override {
		_wire.begin();
		_wire.setClock(_clockSpeed);

		// Test communication by attempting to contact the device
		_wire.beginTransmission(_address);
		uint8_t error = _wire.endTransmission();

		#if SENSORS_DEBUG == 1
			printf("[DEBUG] I2C device at 0x%X", _address);
			if (error == 0) {
				printf(" responded successfully.\n");
			} else {
				printf(" did not respond. Error code: %d\n", error);
			}
		#endif

		if (error == 0) {
			return this;
		}
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

	virtual const SensorInfo* info() const {
		if (_cfg != nullptr)
		{
			return _cfg;
		}
		return nullptr;
	};
};

uint32_t SensorBase::getCurrentTime() {
	return (uint32_t)millis();
}