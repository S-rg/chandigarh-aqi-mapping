# Sensors

## Common Mistakes

- Not initializaing your comms method [wire / stream]

## TODO
- [ ] FIX: Config generator does not take into account multiple measurements [see PM sensor config in header]
- [x] Redo the whole library with better anstraction for units, multiple measurements, etc.
  - Check out [this GPT chat](https://chatgpt.com/share/68deb952-05b4-8005-9f38-077af74053e9).
  - [x] Decide on dynamic or static arrays to store Measurements (per sensor basis)


## Library Design
Initial Plan:
- Inside of each sensor class have an array of `Measurement` which is a struct containing the values, units, timestamp, etc.
- `SensorManager` polls all the sensors to update their measurements, reads them into a buffer and based on some logic, offloads that buffer.
- Problems with this design:
  - Too much redunduncy and memory overhead.
  - Things like units, number of measurements, etc. can be statically defined.

### **DESIGN PHILOSOPHY**
- For a given sensor, constants like comms interface, pin numbers, measurement properties (how many #?, units, measurement name, etc.) would be defined in a yaml config file.
- A config loader would go through the config to initialize the sensors.
- `SensorManager` polls all the sensors, and adds a `Measurement` inside of a static buffer. This measurement only includes the `sensorID`, `measurementID`, `measurementValue`, `timeStamp`.
- For the actual `Sensor` itself, it would have a `CommsInterface` and `ParserInterface`.
- Benefits:
  - Effectively half the memory overhead as last approach.
  - Config file to activate and disable sensors / change parameters
  - Only one way to get data (through `SensorManager`)
- Downsides:
  - The code would be slightly harder to read
  - Having to create a config, config loader, and manager to interface with even a single sensor.

#### Notes:
- The `measurement_id` for each unit of each measurement of a sensor should remain constant.

### Sensors

- [x] Add `DEBUG` mode in SerialSensor to see the raw output of sensor.
- [ ] In `SerialSensor` constructor, check the datatype of the `Stream` reference, instead of having the user put `HARDWARE` or `SOFTWARE` serial as an argument.

  - Too many human errors made due to this.

- [ ] Macros to control what sensors are active in main, so no need to comment, uncomment, etc.
- [ ] Handle proper serial reading with checksum and frame start byte check
- [ ] Create proper `I2CSensor` class.

  - All I2C sensors have libraries, but need to integrate into current convention.

- [ ] Extend the base class so that `read()` can be implemented into `readTemp()`, `readPressure()`, etc.

### Sensor Manager

#### Functionality

- Send read write commands to all the sensors.
- Implement polling mechanisms depening on controller (parallel / sequential)
- Ability to handle commands like "Switch TVOC to QA Mode"

### Database

- [ ] Figure out proper schema for database
- [ ] Handle multiple sensors of same kind

### Casing

- Airflow?
- 3D Printed?
- Sealing / Weather-Proofing?
- Cleaning?

  - Air flushing


## TVOC

- **Comms:** Serial
- **Problems:** None

## CH2O

- **Comms:** Serial
- **Problems:**

  - The sensor was not actually set to QA mode.

    - This was happening because the `Serial.begin()` command was being called after the qaModeOnCommand was sent in the Sensor's constructor.

      - This was fixed by called `sensor.initialize()` in the parent class constructor.

    - Also added a delay after setting switching the mode of the sensor





## O2

- **Comms:** I2C
- Has library, but needs integration with our commands

## Pressure Sensor

- I2C
- All values showing up as max or very high + comp. temp as -48 •C
- Upon checking further, all the calibration values were either 65k or -1. The problem is the data fetching with the sensor.
- Tried unit tests to find what the problem was, still do not know or understand why no data is coming through.