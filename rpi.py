import serial
import re
import requests

def extract_numbers(input_string):
    match = re.search(r"sensor=(\d+), measurement=(\d+), value=([\d.]+), ts=(\d+)", line)
    if match:
        sensor = int(match.group(1))
        measurement = int(match.group(2))
        value = float(match.group(3))
        ts = int(match.group(4))

        return sensor, measurement, value, ts

if __name__ == "__main__":
    node_id = "A01"
    port = '/dev/ttyUSB0'
    baudrate = 9600
    timeout = 1
    ser = serial.Serial(port, baudrate, timeout=timeout)

    try:
        while True:
            line = ser.readline().decode('utf-8').strip()

            if line:
                sensor, measurement, value, ts = extract_numbers(line)
                url = f"http://10.1.40.45/api/postdata/{node_id}/{sensor}/{measurement}"
                data = {
                    "value": value,
                    "ts": None
                }
                response = requests.post(url, json=data)
                

    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        ser.close()