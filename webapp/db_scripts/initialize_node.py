import yaml
import sys
from dotenv import load_dotenv
import os
import mysql.connector
from logging_config import setup_logging
import logging

def initialize_node(node, cursor, logger):
    query = """INSERT INTO Node (node_id, location, latitude, longitude) 
               VALUES (%s, %s, %s, %s);"""
    cursor.execute(query, (node['id'], node['location_name'], node['lat'], node['lon']))
    logger.info(f"Inserted Node {node['id']} into Node")
    

def insert_measurement(sensor_id, measurement_id, sensor_type, sensor_model, measurement_name, unit, node_id, cursor, logger):
    query = """INSERT INTO Sensor (node_id, sensor_id, measurement_id, sensor_type, sensor_model, measurement_name, unit) 
               VALUES (%s, %s, %s, %s, %s, %s, %s);"""
    cursor.execute(query, (node_id, sensor_id, measurement_id, sensor_type, sensor_model, measurement_name, unit))
    logger.info(f"Inserted Sensor {node_id}_{sensor_id}_{measurement_id} into Sensor")

def create_sensor_table(node_id, sensor_id, measurement_id, cursor, logger):
    query = f"""CREATE TABLE {node_id}_{sensor_id}_{measurement_id} (
        id INT PRIMARY KEY AUTO_INCREMENT,
        value DOUBLE NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );"""
    cursor.execute(query)
    logger.info(f"Created node {node_id}_{sensor_id}_{measurement_id} table")


def initialize_sensors(node, sensors, cursor, logger):
    node_id = node['id']
    for _, sensor in sensors.items():
        sensor_id = sensor['id']
        sensor_type = sensor['type']
        sensor_model = sensor['part_name'] if 'part_name' in sensor else None

        measurements = sensor['measurements']
        if isinstance(measurements, dict):
            measurements = [measurements]

        for measurement in measurements:
            measurement_id = measurement['measurement_id']
            measurement_name = measurement['name']
            unit = measurement['unit']
            insert_measurement(sensor_id, measurement_id, sensor_type, sensor_model, measurement_name, unit, node_id, cursor, logger)
            create_sensor_table(node_id, sensor_id, measurement_id, cursor, logger)

def main():
    logger = logging.getLogger(__name__)
    logger.info("Node Initialization Started")    

    if len(sys.argv) < 2:
        print("Usage: py create_tables.py <input_yaml_file>")
        sys.exit(1)

    input_yaml_file = sys.argv[1]
    with open(input_yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    db_config = {
        'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD", ""),
        'host': os.getenv("DB_HOST", "localhost")
    }

    DB_NAME = os.getenv("DB_NAME")

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        logger.info("Created Cursor")

        cursor.execute(f"USE {DB_NAME};")

        initialize_node(data['Node'], cursor, logger)
        initialize_sensors(data['Node'], data['Sensors'], cursor, logger)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        sys.exit(1)


if __name__ == "__main__":
    load_dotenv()
    setup_logging()
    main()