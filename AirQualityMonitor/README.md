# Sensors

## Common Mistakes

- ~~ Not initializaing your comms method [wire / stream] ~~
  - Fixed with new design

## TODO
- [ ] Make PMSensor Measurement ID consistent with Arnav's db config id he has used. 
- [x] Fix: Config file's sensor table should have an i2c address for each sensor.
- [x] FUNC: The switch cases for Serial1,2,3... and Wire1,2,3..
- [x] FUNC: Sensor Factory
- [x] FUNC: Sensor Manager
- ~~[ ] FUNC: Make the config generator add the lookup table for String name to class to create for usage inside sensor factory~~
  - [x] simply hardcode this inside sensor factory
- [x] FIX: Config generator does not take into account multiple measurements [see PM sensor config in header]
  - Problem was with the yaml having repeated keys `measurement_id`, to fix there needed to be a `-` before the key, so they appear as a list or something, like: `- measurement_id` when having multiple measurements. 
- [x] Redo the whole library with better anstraction for units, multiple measurements, etc.
  - Check out [this GPT chat](https://chatgpt.com/share/68deb952-05b4-8005-9f38-077af74053e9).
  - [x] Decide on dynamic or static arrays to store Measurements (per sensor basis)
- [x] Figure out if we using the `Manager` object's buffer to store readings, or having an external buffer which the manager refers to
  - Just using a buffer which is part of Manager object and the object only manages it.
- [x] Handle buffer being full in the manager
  - [ ] Handle this in a smarter way than ignoring as it is right now
- [x] Print last updated measuremt buffer's `RuntimeMeasurement` object
- [ ] Print all `RuntimeMeasurement` objects of the last poll of one sensor
- [x] Other printing stuff
- [x] Confirm the checksums for the sensors
- [ ] Add debug stuff everywhere
  - [x] Added it in places, where i needed to debug stuff.

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

## Reference Tables:

### Measurement ID reference

#### TVOCSensor
| Measurement ID | Measurement name | Unit |
|---:|---|---|
| 1 | tvoc | ppb |

#### CH2OSensor (Formaldehyde)
| Measurement ID | Measurement name | Unit |
|---:|---|---|
| 1 | formaldehyde (CH2O) | ppb |

#### SO2Sensor
| Measurement ID | Measurement name | Unit |
|---:|---|---|
| 1 | so2 | ppm |

#### CO2Sensor
| Measurement ID | Measurement name | Unit |
|---:|---|---|
| 1 | co2 | ppm |

#### PMS7003Sensor (Plantower PMS7003)
| Measurement ID | Measurement name | Unit |
|---:|---|---|
| 1 | PM1.0 (standard, CF=1) | µg/m³ |
| 2 | PM2.5 (standard, CF=1) | µg/m³ |
| 3 | PM10 (standard, CF=1) | µg/m³ |
| 4 | PM1.0 (atmospheric) | µg/m³ |
| 5 | PM2.5 (atmospheric) | µg/m³ |
| 6 | PM10 (atmospheric) | µg/m³ |
| 7 | Particle count ≥ 0.3 µm | particles / 0.1 L |
| 8 | Particle count ≥ 0.5 µm | particles / 0.1 L |
| 9 | Particle count ≥ 1.0 µm | particles / 0.1 L |
| 10 | Particle count ≥ 2.5 µm | particles / 0.1 L |
| 11 | Particle count ≥ 5.0 µm | particles / 0.1 L |
| 12 | Particle count ≥ 10 µm | particles / 0.1 L |

#### Oxygen Sensor (DFRobotOxygen with Winsen MEO2)
| Measurement ID | Measurement name | Unit | Min-Max
|---:|---|---|---|
| 1 | O2 | %Vol | 0% - 25% |


### Sensors
All Tasks and TODOs at the top
- [x] Add `DEBUG` mode in SerialSensor to see the raw output of sensor.
- [x] In `SerialSensor` constructor, check the datatype of the `Stream` reference, instead of having the user put `HARDWARE` or `SOFTWARE` serial as an argument.
  - Too many human errors made due to this.

- ~~[ ] Macros to control what sensors are active in main, so no need to comment, uncomment, etc.~~
- [x] Handle proper serial reading with checksum and frame start byte check
- [x] Create proper `I2CSensor` class.
  - All I2C sensors have libraries, but need to integrate into current convention.
- [x] Extend the base class so that `read()` can be implemented into `readTemp()`, `readPressure()`, etc.

### Sensor Manager

#### Functionality

- Send read write commands to all the sensors.
- Implement polling mechanisms depening on controller (parallel / sequential)
- Ability to handle commands like "Switch TVOC to QA Mode"

### Database

- [x] Figure out proper schema for database
- [x] Handle multiple sensors of same kind
  - Would be done using the same config file

### Casing

- Airflow?
- 3D Printed?
- Sealing / Weather-Proofing?
- Cleaning?

  - Air flushing

## PMSensor
- **Comms:** Serial
- **Problems:**
  - The manager did not recieve the frame in order and needed to be changed such that it waits to get the correct starting bytes.
  - Even after that, the checksum fails half the time.

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

# Installation

1. Install PlatformIO
2. Install Python Dependencies inside of PlatformIO's interpreter
  - `~/.platformio/penv/bin/pip install -r requirements.txt`