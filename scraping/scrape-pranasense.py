import os
import requests
from dotenv import load_dotenv
import json
from datetime import datetime
import time

def login():
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    if not email or not password:
        raise ValueError("EMAIL and PASSWORD environment variables must be set")
    
    url = "https://airquality.aqi.in/api/v1/login"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "email": email,
        "password": password
    }

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    response = response.json()

    token = response.get("token")
    if not token:
        raise ValueError("Login failed, no token received")

    return token

def get_sensors(token):
    url = "https://airquality.aqi.in/api/v1/GetAllUserDevices"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()

def options_request(url):
    response = requests.options(url)
    response.raise_for_status()
    return response.headers

def request_mass(token):
    url = "https://airquality.aqi.in/api/v1/getNearestMapLocation"

    headers = {
        "Authorization": f"Bearer {token}",
        "lat": "25.159189634046733",
        "long": "78.24462890625001",
        "distance": "4000",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        "Type": "1"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    load_dotenv()

    token = login()
    # print("Logged in successfully: ", token)
    sensors = get_sensors(token)
    # print("Retrieved sensors: ", sensors)
    mass = request_mass(token)
    # print("Retrieved mass data: ", mass)
    print(len(mass["Locations"]))

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    sensor_dir = os.path.join("data", "sensor")
    mass_dir = os.path.join("data", "mass")
    os.makedirs(sensor_dir, exist_ok=True)
    os.makedirs(mass_dir, exist_ok=True)

    sensor_path = os.path.join(sensor_dir, f"{timestamp}.json")
    mass_path = os.path.join(mass_dir, f"{timestamp}.json")

    with open(sensor_path, "w", encoding="utf-8") as f:
        json.dump(sensors, f, ensure_ascii=False, indent=2)

    with open(mass_path, "w", encoding="utf-8") as f:
        json.dump(mass, f, ensure_ascii=False, indent=2)

    print(f"Saved sensors to {sensor_path}")
    print(f"Saved mass to {mass_path}")
    

if __name__ == "__main__":
    while True:
        main()
        time.sleep(600)