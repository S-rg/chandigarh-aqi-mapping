/*
   ESP32 + Plantower PMS7003 (Active Mode)
   Using UART0 (default pins: U0RX = GPIO3, U0TX = GPIO1)
   Baudrate: 9600, 8N1
*/

#define PMS_FRAME_LENGTH 32
#define START1 0x42
#define START2 0x4D

// Buffer to store incoming data
uint8_t pmsData[PMS_FRAME_LENGTH];

void setup() {
  Serial.begin(9600);   // For debug monitor
  Serial5.begin(9600);
  Serial.println("PMS7003 Reader Initialized...");
}

void loop() {
  if (Serial5.available() >= PMS_FRAME_LENGTH) {
    // Look for frame header 0x42 0x4D
    if (Serial5.peek() == START1) {
      Serial5.readBytes(pmsData, PMS_FRAME_LENGTH);

      if (pmsData[0] == START1 && pmsData[1] == START2) {
        // Verify checksum
        uint16_t sum = 0;
        for (int i = 0; i < PMS_FRAME_LENGTH - 2; i++) {
          sum += pmsData[i];
        }
        uint16_t checksum = (pmsData[30] << 8) | pmsData[31];

        if (sum == checksum) {
          // Parse data (big-endian)
          uint16_t pm1_cf1   = (pmsData[4] << 8) | pmsData[5];
          uint16_t pm25_cf1  = (pmsData[6] << 8) | pmsData[7];
          uint16_t pm10_cf1  = (pmsData[8] << 8) | pmsData[9];

          uint16_t pm1_env   = (pmsData[10] << 8) | pmsData[11];
          uint16_t pm25_env  = (pmsData[12] << 8) | pmsData[13];
          uint16_t pm10_env  = (pmsData[14] << 8) | pmsData[15];

          // Print to Serial Monitor
          Serial.print("PM1.0 (CF=1): "); Serial.print(pm1_cf1);
          Serial.print(" | PM2.5 (CF=1): "); Serial.print(pm25_cf1);
          Serial.print(" | PM10 (CF=1): "); Serial.println(pm10_cf1);

          Serial.print("PM1.0 (Env): "); Serial.print(pm1_env);
          Serial.print(" | PM2.5 (Env): "); Serial.print(pm25_env);
          Serial.print(" | PM10 (Env): "); Serial.println(pm10_env);

          Serial.println("-------------------------");
        } else {
          Serial.println("Checksum mismatch!");
        }
      }
    } else {
      Serial5.read(); // discard one byte if no header match
    }
  }
}
