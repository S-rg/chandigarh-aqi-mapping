import os
import requests
from dotenv import load_dotenv
import json
from datetime import datetime
import time
from logging_config import setup_logging
import logging

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def format_datetime(dt_str):
    try:
        parsed = datetime.strptime(dt_str, "%d %b %Y, %I:%M%p")
        return parsed.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return None

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

def get_row(location):
    row = {}

    row['lat'] = location['lat']
    row['lon'] = location['lon']
    row['locationId'] = location['locationId']
    row['city'] = location['city']
    row['state'] = location['state']
    row['country'] = location['country']
    row['last_updated'] = location['last_updated']

    for sensor in location['airquality']:
        key = f"{sensor['senDevId'].lower()}"
        row[key] = sensor['sensorData']

    return row


def data_to_sql(mass_data, logger):
    rows = []
    for location in mass_data["Locations"]:
        row = get_row(location)
        rows.append(row)

    config = {
        'host': os.getenv("DB_HOST", "localhost"),
        'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD", ""),
        'database': os.getenv("DB_NAME", "SMAQI")
    }

    try:
        import mysql.connector
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        for row in rows:
            insert_scraped_row(row, cursor)

        conn.commit()

    except mysql.connector.Error as e:
        logger.error(f"Failed to connect to the database: {str(e)}")
        return
    
    finally:
        cursor.close()
        conn.close()

    

def insert_scraped_row(row, cursor):
    query = """
        INSERT INTO AqiInScrape (
            lat, lon, locationId, city, state, country, last_updated,
            AQI_IN, AQI_US, CO_PPB, H_PERCENT, NO2_PPB, O3_PPB,
            PM10_UGM3, PM2_5_UGM3, SO2_PPB, T_C, PM1_UGM3, TVOC_PPM, Noise_DB
        )
        VALUES (
            %(lat)s, %(lon)s, %(locationId)s, %(city)s, %(state)s, %(country)s, %(last_updated)s,
            %(AQI_IN)s, %(AQI_US)s, %(CO_PPB)s, %(H_PERCENT)s, %(NO2_PPB)s, %(O3_PPB)s,
            %(PM10_UGM3)s, %(PM2_5_UGM3)s, %(SO2_PPB)s, %(T_C)s, %(PM1_UGM3)s, %(TVOC_PPM)s, %(Noise_DB)s
        );
    """
    cursor.execute(query, {
        'lat': row.get('lat'),
        'lon': row.get('lon'),
        'locationId': row.get('locationId'),
        'city': row.get('city'),
        'state': row.get('state'),
        'country': row.get('country'),
        'last_updated': format_datetime(row.get('last_updated')),
        'AQI_IN': row.get('aqi-in', None),
        'AQI_US': row.get('aqi', None),
        'CO_PPB': row.get('co', None),
        'H_PERCENT': row.get('h', None),
        'NO2_PPB': row.get('no2', None),
        'O3_PPB': row.get('o3', None),
        'PM10_UGM3': row.get('pm10', None),
        'PM2_5_UGM3': row.get('pm25', None),
        'SO2_PPB': row.get('so2', None),
        'T_C': row.get('t', None),
        'PM1_UGM3': row.get('pm1', None),
        'TVOC_PPM': row.get('tvoc', None),
        'Noise_DB': row.get('noise', None)
    })


def insert_sensor_data_api(node_id, sensor_id, measurement_id, data, logger):
    request_url = f"http://10.1.40.45/api/postdata/{node_id}/{sensor_id}/{measurement_id}"
    
    response = requests.post(request_url, json=data)
    logger.info(f"{node_id}_{sensor_id}_{measurement_id} response status: {response.status_code}, body: {response.text}")

def sensor_data_to_sql(sensors_data, logger):
    sensor_map = {
        "84530304be06c": "1",
        "48F6EE5481E0": "2",
        "48F6EE546F34": "3"
    }

    sensor_id_map = {
        1: (1,1),
        2: (2,1),
        3: (3,1),
        4: (3,2),
        5: (3,3),
        11: (4,1),
        12: (5,1),
        13: (6,1),
        18: (7,1),
        20: (8,1),
        21: (9,1),
        22: (10,1),
        23: (11,1),
        25: (12,1),
        26: (13,1),
        27: (14,1),
        71: (1,4),
        72: (1,5),
        73: (1,6),
        74: (1,7),
        75: (1,8),
        76: (1,9),
        78: (15,1)
    }

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for device in sensors_data['data']:
        node_id = sensor_map.get(device['serialNo'])

        for sensor in device['realtime']:
            if sensor['sensorid'] not in sensor_id_map:
                continue
            sensor_id, measurement_id = sensor_id_map[sensor['sensorid']]

            data = {
                'value': sensor['sensorvalue'],
                'timestamp': timestamp,
            }

            insert_sensor_data_api(node_id, sensor_id, measurement_id, data, logger)



    

def main(logger):
    load_dotenv("/home/studentiotlab/aqi-dashboard/.env")

    token = login()
    logger.info("Logged in successfully")
    sensors = get_sensors(token)
    logger.debug(f"Fetched {len(sensors['data'])} sensors")
    mass = request_mass(token)
    logger.info(f"Fetched mass data with {len(mass['Locations'])} locations")

    data_to_sql(mass, logger)
    logger.info("Data inserted into database successfully")

    sensor_data_to_sql(sensors, logger)

def alert_mail(body):
    msg = MIMEMultipart()
    
    sender = os.getenv("ALERT_SENDER")
    password = os.getenv("ALERT_PASSWORD")
    recipients = [email.strip() for email in os.getenv("ALERT_EMAIL").split(",")]

    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = "Alert: AQI Scraper Stopped"
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipients, msg.as_string())


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        main(logger)
    except Exception as e:
        logger.error(f"Error occurred: {e}", exc_info=True)
        alert_mail(str(e))
    except KeyboardInterrupt as e:
        logger.info("Script interrupted by user")
        alert_mail(str(e) + " \n\n\n Damn bro you stopped it yourself bro.")
    except requests.exceptions.ConnectionError:
        logger.error("Network error occurred, retrying in 5 minutes...")
    except requests.exceptions.Timeout:
        logger.error("Request timed out, retrying in 5 minutes...")