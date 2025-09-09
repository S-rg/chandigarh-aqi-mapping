DEBUG = True

import serial
import mysql.connector
from dotenv import load_dotenv
import os
import sys

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

def get_int(byte1, byte2):
    return byte1 * 256 + byte2

def winsen_to_real_val(data):
    pm1 = get_int(data[2], data[3])
    pm25 = get_int(data[4], data[5])
    pm10 = get_int(data[6], data[7])
    co2 = get_int(data[8], data[9])
    voc = data[10]
    temp = get_int(data[11], data[12])
    humidity = get_int(data[13], data[14])
    ch2o = get_int(data[15], data[16])
    co = get_int(data[17], data[18])
    o3 = get_int(data[19], data[20])
    no2 = get_int(data[21], data[22])

    return (pm1, pm25, pm10, co2, voc, temp, humidity, ch2o, co, o3, no2)

try:
    cursor = conn.cursor()
    while True:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            data = data.decode('utf-8', errors='ignore')

            data = data.split()
            data = [int(x) for x in data]

            winsen1_raw = data[0:26]
            winsen2_raw = data[26:]

            winsen1 = winsen_to_real_val(winsen1_raw)
            winsen2 = winsen_to_real_val(winsen2_raw)

            if DEBUG:
                print("Raw Data:", data)
                print("Length: ", len(data))

                print("Winsen1 Raw:", winsen1_raw)
                print("Winsen2 Raw:", winsen2_raw)

                print("Winsen1:", winsen1)
                print("Winsen2:", winsen2)

            cursor.execute(
                "INSERT INTO winsen1 (pm1, pm25, pm10, co2, voc, temp, humidity, ch2o, co, o3, no2) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                winsen1
            )
            cursor.execute(
                "INSERT INTO winsen2 (pm1, pm25, pm10, co2, voc, temp, humidity, ch2o, co, o3, no2) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                winsen2
            )
            conn.commit()

            print("Data inserted into database")
            print("---------------------\n")

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    ser.close()
    conn.close()
    cursor.close()
