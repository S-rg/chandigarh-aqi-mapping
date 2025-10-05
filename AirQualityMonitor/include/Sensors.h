#pragma once
#include "Base.h"

class TVOCSensor : public SensorBase
{
public:
	static const int commandSize = 9;
	static const int responseSize = 9;

	TVOCSensor(SensorInfo *cfg) : SensorBase(cfg) {}

	bool begin()
	{
		_comm->begin();
		_startQAMode();
	}

	const SensorInfo *info()
	{
		if (_cfg != nullptr)
		{
			return _cfg;
		}
		return nullptr;
	}

	void read(uint8_t measurement_id, RuntimeMeasurement *buffer)
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

	float read_measurement_1(SerialInterface *commInterface, RuntimeMeasurement *buffer)
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
		return 1; // true
	}
};