DB_NAME = "SMAQI"

import yaml
import sys
import mysql.connector

def initialize_node(node, cursor):
    query = f"""INSERT INTO Node (node_id, location, latitude, longitude) 
    VALUES ({node['id']}, '{node['location_name']}', {node['lat']}, {node['lon']});"""
    cursor.execute(query)

def insert_measurement(sensor_id, measurement_id, sensor_type, sensor_model, measurement_name, unit, node_id, cursor):
    query = f"""INSERT INTO Sensor (node_id, sensor_id, measurement_id, sensor_type, sensor_model, measurement_name, unit) 
    VALUES ({node_id}, {sensor_id}, {measurement_id}, '{sensor_type}', '{sensor_model}', {measurement_name}, '{unit}');"""
    cursor.execute(query)

def create_sensor_table(node_id, sensor_id, measurement_id, cursor):
    query = f"""CREATE TABLE {node_id}_{sensor_id}_{measurement_id} (
        id INT PRIMARY KEY AUTO_INCREMENT,
        value DOUBLE NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );"""
    cursor.execute(query)


def initialize_sensors(node, sensors, cursor):
    node_id = node['id']
    for sensor in sensors:
        sensor_id = sensor['id']
        sensor_type = sensor['type']
        sensor_model = sensor['part_name']
        for measurement in sensor['measurements']:
            measurement_id = measurement['measurement_id']
            measurement_name = measurement['name']
            unit = measurement['unit']
            insert_measurement(sensor_id, measurement_id, sensor_type, sensor_model, measurement_name, unit, node_id, cursor)
            create_sensor_table(node_id, sensor_id, measurement_id, cursor)

def main():
    if len(sys.argv) < 2:
        print("Usage: py create_tables.py <input_yaml_file>")
        sys.exit(1)

    input_yaml_file = sys.argv[1]
    with open(input_yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    username = input("Enter your MySQL username: ")
    password = input("Enter your MySQL password: ")
    host = input("Enter the MySQL host (default: localhost): ") or 'localhost'

    db_config = {
        'user': username,
        'password': password,
        'host': host
    }

    try:
        conn = mysql.connector.connect(**db_config)
        print("Connection established!")
        cursor = conn.cursor()
        print("Cursor created!")

        cursor.execute(f"USE {DB_NAME};")

        initialize_node(data['Node'], cursor)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()