import os
from datetime import datetime
import mysql.connector
from logging_config import setup_logging
import logging
import json

def format_datetime(dt_str):
    try:
        parsed = datetime.strptime(dt_str, "%d %b %Y, %I:%M%p")
        return parsed.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return None

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


def data_to_sql(mass_data, logger, i):
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
        logger.info(f"Batch insert completed {i}")
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


if __name__ == "__main__":
    files = []
    logger = setup_logging()
    data_dir = os.path.join(os.path.dirname(__file__), "data", "mass")
    for filename in os.listdir(data_dir):
        file_path = os.path.join(data_dir, filename)
        if os.path.isfile(file_path):
            files.append(file_path)
    
    for i, file_path in enumerate(files):
        with open(file_path, 'r') as f:
            mass_data = json.load(f)
            data_to_sql(mass_data, logger, i)

