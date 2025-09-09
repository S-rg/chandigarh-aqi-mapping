#include <Arduino.h>

const bool DEBUG = false;

byte GET_DATA_COMMAND[9] = {0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};
const int RESPONSE_SIZE = 26;

byte* get_data(HardwareSerial &serial_, byte response[RESPONSE_SIZE]) {
  serial_.write(GET_DATA_COMMAND, 9);

  delay(100);

  for (int i = 0; i < RESPONSE_SIZE; i++) { response[i] = serial_.read(); }

  return response;
}

int get_int(byte first, byte second) {
  return (int) first * 256 + (int) second;
}


void setup() {
  Serial.begin(9600);
  Serial3.begin(9600);
  Serial5.begin(9600);
}

void debug_print(byte* response) {
  int pm1 = get_int(response[2], response[3]);
  int pm25 = get_int(response[4], response[5]);
  int pm10 = get_int(response[6], response[7]);
  int co2 = get_int(response[8], response[9]);
  int voc = (int) response[10];
  int temp = get_int(response[11], response[12]);
  int humidity = get_int(response[13], response[14]);
  int ch2o = get_int(response[15], response[16]);
  int co = get_int(response[17], response[18]);
  int o3 = get_int(response[19], response[20]);
  int no2 = get_int(response[21], response[22]);

  Serial.print("PM1: ");       Serial.println(pm1);
  Serial.print("PM2.5: ");     Serial.println(pm25);
  Serial.print("PM10: ");      Serial.println(pm10);
  Serial.print("CO2: ");       Serial.println(co2);
  Serial.print("VOC: ");       Serial.println(voc);
  Serial.print("Temp: ");      Serial.println(temp);
  Serial.print("Humidity: ");  Serial.println(humidity);
  Serial.print("CH2O: ");      Serial.println(ch2o);
  Serial.print("CO: ");        Serial.println(co);
  Serial.print("O3: ");        Serial.println(o3);ho
  Serial.print("NO2: ");       Serial.println(no2);
  Serial.println("===================");
}

void send_responses(byte response1[], byte response2[]) {
  for (int i = 0; i < RESPONSE_SIZE; i++) {
    Serial.print(response1[i]);
    Serial.print(" ");
  }

  for (int i = 0; i < RESPONSE_SIZE; i++) {
    Serial.print(response2[i]);
    Serial.print(" ");
  }

  Serial.println();
}


void loop() {
  byte response1[RESPONSE_SIZE];
  byte response2[RESPONSE_SIZE];

  get_data(Serial3, response1);
  get_data(Serial5, response2);

  if (DEBUG) {debug_print(response1); debug_print(response2);}
  else {
    send_responses(response1, response2);
  }

  delay(800);
}
