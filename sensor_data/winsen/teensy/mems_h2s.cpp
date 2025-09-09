#include <Arduino.h>
#include <mems_h2s.h>

int get_raw_h2s(int pin) {
  return analogRead(pin);
}

