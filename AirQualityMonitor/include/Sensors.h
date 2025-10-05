#pragma once
#include "Base.h"

class TVOCSensor : public SensorBase
{
public:
	static const int commandSize = 9;
	static const int responseSize = 9;

	TVOCSensor(SensorInfo *cfg) : SensorBase(cfg) {}

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
			return -1;
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

byte TVOCSensor::qaModeOnCommand[TVOCSensor::commandSize] = {0xff, 0x01, 0x78, 0x41, 0x00, 0x00, 0x00, 0x00, 0x46};
byte TVOCSensor::getValueCommand[TVOCSensor::commandSize] = {0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};