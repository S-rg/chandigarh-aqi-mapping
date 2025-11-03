#pragma once
#include "Base.h"

class TVOCSensor : public SensorBase
{
public:
	static const int commandSize = 9;
	static const int responseSize = 9;

	TVOCSensor(SensorInfo *cfg, CommsInterface *comm) : SensorBase(cfg, comm) {
	}

	bool begin() override
	{
		_comm->begin();

		_startQAMode();

		return true;
	}

	const SensorInfo* info() const override
	{
		if (_cfg != nullptr)
		{
			return _cfg;
		}
		return nullptr;
	}

	void read(uint8_t measurement_id, RuntimeMeasurement *buffer) override
	{
		if (_cfg->comms == COMM_HARDWARE_SERIAL || _cfg->comms == COMM_SOFTWARE_SERIAL)
		{
			SerialInterface *commInterface = static_cast<SerialInterface *>(_comm);

			// The sensor manager can update the sensor_id and measurement_id field
			// of RuntimeMeasurement
			if (measurement_id == 1)
			{
				read_measurement_1(commInterface, buffer);
			}
		}
	}

	void read_measurement_1(SerialInterface *commInterface, RuntimeMeasurement *buffer)
	{
		commInterface->sendBuffer(getValueCommand, commandSize);
		delay(delayTime);

		byte responseBuffer[responseSize];
		commInterface->receiveBuffer(responseBuffer, responseSize);

		if (_verifyChecksum(responseBuffer) != true)
		{
			return;
		}

		// Process response and store in runtime measurement 'buffer'
		// Conc values in 6th byte [HIGH] and 7th byte [LOW]
		uint16_t conc = (responseBuffer[6] << 8) | responseBuffer[7]; // Units: ppb

		buffer->timestamp = SensorBase::getCurrentTime();
		buffer->value = static_cast<float>(conc);

		return;
	}

private:
	static byte qaModeOnCommand[commandSize];
	static byte getValueCommand[commandSize];

	void _startQAMode()
	{
		if (_cfg->comms == COMM_HARDWARE_SERIAL || _cfg->comms == COMM_SOFTWARE_SERIAL)
		{
			SerialInterface *commInterface = static_cast<SerialInterface *>(_comm);

			commInterface->sendBuffer(qaModeOnCommand, commandSize);
			delay(delayTime);
		}
	}

	uint8_t _verifyChecksum(byte *responseBuffer)
	{
		// TODO: Implement this
		return 1; // true
	}
};

class CH2OSensor : public SensorBase
{
	public:
	static const int commandSize = 9;
	static const int responseSize = 9;
	
	CH2OSensor(SensorInfo *cfg, CommsInterface *comm) : SensorBase(cfg, comm) {
	}
	
	bool begin() override
	{
		_comm->begin();
		_startQAMode();
		
		return true;
	}
	
	const SensorInfo* info() const override
	{
		if (_cfg != nullptr)
		{
			return _cfg;
		}
		return nullptr;
	}
	
	void read(uint8_t measurement_id, RuntimeMeasurement *buffer) override
	{
		if (_cfg->comms == COMM_HARDWARE_SERIAL || _cfg->comms == COMM_SOFTWARE_SERIAL)
		{
			SerialInterface *commInterface = static_cast<SerialInterface *>(_comm);
			
			if (measurement_id == 1)
			{
				read_measurement_1(commInterface, buffer);
			}
		}
	}
	
	void read_measurement_1(SerialInterface *commInterface, RuntimeMeasurement *buffer)
	{
		commInterface->sendBuffer(getValueCommand, commandSize);
		delay(delayTime);
		
		byte responseBuffer[responseSize];
		commInterface->receiveBuffer(responseBuffer, responseSize);
		
		if (_verifyChecksum(responseBuffer) != true)
		{
			return;
		}
		
		uint16_t conc = (responseBuffer[6] << 8) | responseBuffer[7];
		
		buffer->timestamp = SensorBase::getCurrentTime();
		buffer->value = static_cast<float>(conc);
		
		return;
	}
	
	private:
	static byte qaModeOnCommand[commandSize];
	static byte getValueCommand[commandSize];
	
	void _startQAMode()
	{
		if (_cfg->comms == COMM_HARDWARE_SERIAL || _cfg->comms == COMM_SOFTWARE_SERIAL)
		{
			SerialInterface *commInterface = static_cast<SerialInterface *>(_comm);
			
			commInterface->sendBuffer(qaModeOnCommand, commandSize);
			delay(delayTime);
		}
	}
	
	// active mode intentionally unsupported; always operate in QA mode
	
	uint8_t _verifyChecksum(byte *responseBuffer)
	{
		return 1; // placeholder
	}
};

class SO2Sensor : public SensorBase
{
public:
	static const int commandSize = 9;
	static const int responseSize = 9;

	SO2Sensor(SensorInfo *cfg, CommsInterface *comm) : SensorBase(cfg, comm) {
	}

	bool begin() override
	{
		_comm->begin();
		_startQAMode();

		return true;
	}

	const SensorInfo* info() const override
	{
		if (_cfg != nullptr)
		{
			return _cfg;
		}
		return nullptr;
	}

	void read(uint8_t measurement_id, RuntimeMeasurement *buffer) override
	{
		if (_cfg->comms == COMM_HARDWARE_SERIAL || _cfg->comms == COMM_SOFTWARE_SERIAL)
		{
			SerialInterface *commInterface = static_cast<SerialInterface *>(_comm);

			if (measurement_id == 1)
			{
				read_measurement_1(commInterface, buffer);
			}
		}
	}

	void read_measurement_1(SerialInterface *commInterface, RuntimeMeasurement *buffer)
	{
		commInterface->sendBuffer(getValueCommand, commandSize);
		delay(delayTime);

		byte responseBuffer[responseSize];
		commInterface->receiveBuffer(responseBuffer, responseSize);

		if (_verifyChecksum(responseBuffer) != true)
		{
			return;
		}

		uint16_t conc = (responseBuffer[2] << 8) | responseBuffer[3]; // ppm

		buffer->timestamp = SensorBase::getCurrentTime();
		buffer->value = static_cast<float>(conc);

		return;
	}

private:
	static byte qaModeOnCommand[commandSize];
	static byte getValueCommand[commandSize];

	void _startQAMode()
	{
		if (_cfg->comms == COMM_HARDWARE_SERIAL || _cfg->comms == COMM_SOFTWARE_SERIAL)
		{
			SerialInterface *commInterface = static_cast<SerialInterface *>(_comm);

			commInterface->sendBuffer(qaModeOnCommand, commandSize);
			delay(delayTime);
		}
	}

	uint8_t _verifyChecksum(byte *responseBuffer)
	{
		return 1;
	}
};

class CO2Sensor : public SensorBase
{
public:
	static const int commandSize = 9;
	static const int responseSize = 9;

	CO2Sensor(SensorInfo *cfg, CommsInterface *comm) : SensorBase(cfg, comm) {
	}

	bool begin() override
	{
		_comm->begin();
		return true;
	}

	const SensorInfo* info() const override
	{
		if (_cfg != nullptr)
		{
			return _cfg;
		}
		return nullptr;
	}

	void read(uint8_t measurement_id, RuntimeMeasurement *buffer) override
	{
		if (_cfg->comms == COMM_HARDWARE_SERIAL || _cfg->comms == COMM_SOFTWARE_SERIAL)
		{
			SerialInterface *commInterface = static_cast<SerialInterface *>(_comm);

			if (measurement_id == 1)
			{
				read_measurement_1(commInterface, buffer);
			}
		}
	}

	void read_measurement_1(SerialInterface *commInterface, RuntimeMeasurement *buffer)
	{
		commInterface->sendBuffer(getValueCommand, commandSize);
		delay(delayTime);

		byte responseBuffer[responseSize];
		commInterface->receiveBuffer(responseBuffer, responseSize);

		if (_verifyChecksum(responseBuffer) != true)
		{
			return;
		}

		uint16_t conc = (responseBuffer[2] << 8) | responseBuffer[3]; // ppm

		buffer->timestamp = SensorBase::getCurrentTime();
		buffer->value = static_cast<float>(conc);

		return;
	}

private:
	static byte getValueCommand[commandSize];

	uint8_t _verifyChecksum(byte *responseBuffer)
	{
		return 1;
	}
};

class PMS7003Sensor : public SensorBase {
public:
	static const int responseSize = 32;
	static const int commandSize = 7;

	PMS7003Sensor(SensorInfo *cfg, CommsInterface *comm) : SensorBase(cfg, comm) {
	}

	bool begin() override {
		_comm->begin();
		_startQAMode();
		return true;
	}

	const SensorInfo* info() const override {
		if (_cfg != nullptr) return _cfg;
		return nullptr;
	}

	void read(uint8_t measurement_id, RuntimeMeasurement *buffer) override {
		if (_cfg->comms == COMM_HARDWARE_SERIAL || _cfg->comms == COMM_SOFTWARE_SERIAL) {
			SerialInterface *commInterface = static_cast<SerialInterface *>(_comm);

			commInterface->sendBuffer(getValueCommand, commandSize);
			delay(delayTime + 400);

			byte frame[responseSize];
			// Replace commInterface->receiveBuffer(frame, responseSize) with frame sync logic
			int frameIdx = 0;
			while (frameIdx < responseSize) {
				int b = commInterface->readByte();
				if (frameIdx == 0 && b != 0x42) continue;
				if (frameIdx == 1 && b != 0x4D) { frameIdx = 0; continue; }
				frame[frameIdx++] = b;
			}

			if (!_verifyChecksum(frame)) {
				if(SENSORS_DEBUG) {
					Serial.printf("[DEBUG] Checksum failed for PMS7003 with ID = %i\n", _cfg->sensor_id);
				}
			}

			switch (measurement_id) {
				case 1: read_measurement_1(frame, buffer); break;
				case 2: read_measurement_2(frame, buffer); break;
				case 3: read_measurement_3(frame, buffer); break;
				case 4: read_measurement_4(frame, buffer); break;
				case 5: read_measurement_5(frame, buffer); break;
				case 6: read_measurement_6(frame, buffer); break;
				case 7: read_measurement_7(frame, buffer); break;
				case 8: read_measurement_8(frame, buffer); break;
				case 9: read_measurement_9(frame, buffer); break;
				case 10: read_measurement_10(frame, buffer); break;
				case 11: read_measurement_11(frame, buffer); break;
				case 12: read_measurement_12(frame, buffer); break;
				default: break;
			}
		}
	}

	void read_measurement_1(byte *frame, RuntimeMeasurement *buffer) { set_uint16_value(frame, 4, buffer); }
	void read_measurement_2(byte *frame, RuntimeMeasurement *buffer) { set_uint16_value(frame, 6, buffer); }
	void read_measurement_3(byte *frame, RuntimeMeasurement *buffer) { set_uint16_value(frame, 8, buffer); }
	void read_measurement_4(byte *frame, RuntimeMeasurement *buffer) { set_uint16_value(frame, 10, buffer); }
	void read_measurement_5(byte *frame, RuntimeMeasurement *buffer) { set_uint16_value(frame, 12, buffer); }
	void read_measurement_6(byte *frame, RuntimeMeasurement *buffer) { set_uint16_value(frame, 14, buffer); }
	void read_measurement_7(byte *frame, RuntimeMeasurement *buffer) { set_uint16_value(frame, 16, buffer); }
	void read_measurement_8(byte *frame, RuntimeMeasurement *buffer) { set_uint16_value(frame, 18, buffer); }
	void read_measurement_9(byte *frame, RuntimeMeasurement *buffer) { set_uint16_value(frame, 20, buffer); }
	void read_measurement_10(byte *frame, RuntimeMeasurement *buffer) { set_uint16_value(frame, 22, buffer); }
	void read_measurement_11(byte *frame, RuntimeMeasurement *buffer) { set_uint16_value(frame, 24, buffer); }
	void read_measurement_12(byte *frame, RuntimeMeasurement *buffer) { set_uint16_value(frame, 26, buffer); }

private:
	static byte qaModeOnCommand[commandSize];
	static byte getValueCommand[commandSize];
	void set_uint16_value(byte *frame, int idx, RuntimeMeasurement *buffer) {
		uint16_t val = (static_cast<uint16_t>(frame[idx]) << 8) | static_cast<uint16_t>(frame[idx+1]);
		buffer->timestamp = SensorBase::getCurrentTime();
		buffer->value = static_cast<float>(val);
	}

	bool _verifyChecksum(byte *frame) {
		uint16_t frameLen = (static_cast<uint16_t>(frame[2]) << 8) | static_cast<uint16_t>(frame[3]);
		int expectedLen = frameLen + 4; // header+len + data + checksum
		if (expectedLen + 0 != responseSize) return false;

		uint16_t sum = 0;
		for (int i = 0; i < responseSize - 2; ++i) sum += frame[i];
		uint16_t checksum = (static_cast<uint16_t>(frame[responseSize-2]) << 8) | static_cast<uint16_t>(frame[responseSize-1]);
		return sum == checksum;
	}

	void _startQAMode() {
		if (_cfg->comms == COMM_HARDWARE_SERIAL || _cfg->comms == COMM_SOFTWARE_SERIAL) {
			SerialInterface *commInterface = static_cast<SerialInterface *>(_comm);
			commInterface->sendBuffer(qaModeOnCommand, commandSize);
			delay(delayTime);
		}
	}
};


byte TVOCSensor::qaModeOnCommand[TVOCSensor::commandSize] = {0xff, 0x01, 0x78, 0x41, 0x00, 0x00, 0x00, 0x00, 0x46};
byte TVOCSensor::getValueCommand[TVOCSensor::commandSize] = {0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};

byte CH2OSensor::qaModeOnCommand[CH2OSensor::commandSize] = {0xff, 0x01, 0x78, 0x41, 0x00, 0x00, 0x00, 0x00, 0x46};
byte CH2OSensor::getValueCommand[CH2OSensor::commandSize] = {0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};

byte SO2Sensor::qaModeOnCommand[SO2Sensor::commandSize] = {0xff, 0x01, 0x78, 0x04, 0x00, 0x00, 0x00, 0x00, 0x83};
byte SO2Sensor::getValueCommand[SO2Sensor::commandSize] = {0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};

byte CO2Sensor::getValueCommand[CO2Sensor::commandSize] = {0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};

byte PMS7003Sensor::qaModeOnCommand[PMS7003Sensor::commandSize] = {0x42, 0x4d, 0x00, 0x04, 0xe1, 0x00, 0x01}; // passive read command example
byte PMS7003Sensor::getValueCommand[PMS7003Sensor::commandSize] = {0x42, 0x4d, 0x00, 0x04, 0xe2, 0x00, 0x01}; // read data command example
