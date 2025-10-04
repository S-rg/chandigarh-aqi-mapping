#pragma once
#include "DataTypes.h"
#include "SensorsConfig.h" 
#include <HardwareSerial.h>
#include <SoftwareSerial.h>
#include <Wire.h>

class CommsInterface {
private:
	SensorInfo* _cfg;
	CommsType _type;

public:
	CommsInterface(SensorInfo* cfg) : _cfg(cfg) {
		_type = _cfg->comms;
	}
    virtual ~CommsInterface() {}
	virtual void begin() = 0;
};

// TODO:comms interfaces, oarser interfaces, then the sesnor factory can cast commsInterface* into correct child and initialize

class SensorBase {
public:

  virtual ~SensorBase() = default;

  virtual bool begin() = 0;

  // Read available measurements; write up to outcap measurements into out array.
  // Return number of measurements written.
  virtual size_t read(RuntimeMeasurement* out, size_t outcap) = 0;

  virtual const SensorInfo* info() const = 0;
};
