
This directory is intended for PlatformIO Test Runner and project tests.

Unit Testing is a software testing method by which individual units of
source code, sets of one or more MCU program modules together with associated
control data, usage procedures, and operating procedures, are tested to
determine whether they are fit for use. Unit testing finds problems early
in the development cycle.

More information about PlatformIO Unit Testing:
- https://docs.platformio.org/en/latest/advanced/unit-testing/index.html

# Running the tests
`pio test -e main_app -f test_arithmetic`
Where `-e` is for environment name and `-f` is for filter PATTERN

## Test_BMP180
Tried to use the sparkfun BMP180 library to get the values from the sensor. The idea was to make sure my code in the main library wasn't the problem and that something else could also be at play.

- The library did not work as intented and the sensor always failed to initialize.
- For some reason, this make the teensy reboot again and again and fail the unit test.


## Test_Arithmetic
To try and understand how to use tests and verify that the environment / teensy isn't the problem for the above result.