# Sensors

## Code Improvements
- [x] Add `DEBUG` mode in SerialSensor to see the raw output of sensor.
- [ ] In `SerialSensor` constructor, check the datatype of the `Stream` reference, instead of having the user put `HARDWARE` or `SOFTWARE` serial as an argument.
    - Too many human errors made due to this.


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

