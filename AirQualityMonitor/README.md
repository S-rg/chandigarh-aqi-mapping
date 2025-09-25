# Sensors

## Common Mistakes
- Not initializaing your comms method [wire / stream]

## TODO

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