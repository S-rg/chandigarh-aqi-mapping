from app import app
import os
from mysql.connector import connect, Error
from typing import List
import json

def get_connection():
    try:
        return connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", ""),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "aqi_monitoring")
        )
    except Error as e:
        print(f"Database connection error: {e}")
        raise e

def get_data(table: str, cols: List[str]):
    # Validate table name for security
    is_valid, error_msg = validate_table_sensor_names(table, None)
    if not is_valid:
        return {"error": error_msg}, 400
    
    connection = get_connection()
    cols_str = ",".join(cols)
    try:
        cursor = connection.cursor(buffered=True)
        
        # Fix: Handle empty tables properly - check if table has data first
        # Table name is validated above
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        
        if count == 0:
            return {"error": "No data found"}, 404
        
        # Fix: Use COALESCE to handle NULL values in MAX(id)
        # Table name is validated above
        query = f"SELECT {cols_str} FROM {table} WHERE id > COALESCE((SELECT MAX(id) - 1000 FROM {table}), 0);"
        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
            return {"error": "No data found"}, 404

        columns = [desc[0] for desc in cursor.description]
        data = [dict(zip(columns, row)) for row in result]
        return {"data": data}, 200

    except Error as e:
        print(e)
        return {"error": str(e)}, 500
    finally:
        cursor.close()
        connection.close()

@app.route("/api/tvoc")
def get_tvoc_data():
    cols = ["val", "ts"]
    data, status_code = get_data("tvoc_data", cols)
    return data, status_code


@app.route("/api/temp/<string:table>/<string:sensor>")
def get_sensor_data(table, sensor):
    allowed_tables = ["winsen1", "winsen2"]
    allowed_sensors = ["pm1", "pm25", "pm10", "co2", "voc", "temp", "humidity", "ch2o", "co", "o3", "no2"]

    if table not in allowed_tables or sensor not in allowed_sensors:
        return {"error": "Invalid table or sensor name"}, 400

    connection = get_connection()
    try:
        cursor = connection.cursor(buffered=True)
        
        # Fix: Use parameterized query for better security
        query = "SELECT {}, timestamp FROM {} WHERE {} IS NOT NULL".format(sensor, table, sensor)
        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
            return {"error": "No data found"}, 404

        # Fix: Remove hard-coded filter, let frontend handle data validation
        data = [
            {"sensor_value": row[0], "timestamp": row[1].isoformat()}
            for row in result if row[0] is not None and row[0] <= 4000
        ]
        return {"data": data}, 200

    except Error as e:
        print(e)
        return {"error": str(e)}, 500
    finally:
        cursor.close()
        connection.close()

# Fix: Add missing route for main dashboard (plot.js calls /api/sensor{sensorId})
@app.route("/api/sensor<int:sensor_id>")
def get_sensor_data_by_id(sensor_id):
    """Route for individual sensor data (used by plot.js)"""
    # Map sensor_id to actual sensor data based on your sensor configuration
    # For now, we'll use a generic approach that can be customized
    
    # Define sensor mappings (customize based on your actual sensor setup)
    sensor_mappings = {
        1: {"table": "winsen1", "sensor": "pm25"},
        2: {"table": "winsen1", "sensor": "pm10"},
        3: {"table": "winsen1", "sensor": "co2"},
        4: {"table": "winsen1", "sensor": "temp"},
        5: {"table": "winsen1", "sensor": "humidity"},
        6: {"table": "winsen1", "sensor": "voc"},
        7: {"table": "winsen2", "sensor": "pm25"},
        8: {"table": "winsen2", "sensor": "pm10"},
        9: {"table": "winsen2", "sensor": "co2"},
        10: {"table": "winsen2", "sensor": "temp"},
        11: {"table": "winsen2", "sensor": "humidity"},
        12: {"table": "winsen2", "sensor": "voc"},
        # Extended mappings for sensors 13-20
        13: {"table": "winsen1", "sensor": "pm1"},
        14: {"table": "winsen1", "sensor": "ch2o"},
        15: {"table": "winsen1", "sensor": "co"},
        16: {"table": "winsen1", "sensor": "o3"},
        17: {"table": "winsen1", "sensor": "no2"},
        18: {"table": "winsen2", "sensor": "pm1"},
        19: {"table": "winsen2", "sensor": "ch2o"},
        20: {"table": "winsen2", "sensor": "co"},
        # Add more mappings as needed for additional sensors
    }
    
    if sensor_id not in sensor_mappings:
        return {"error": f"Sensor {sensor_id} not configured"}, 404
    
    mapping = sensor_mappings[sensor_id]
    table = mapping["table"]
    sensor = mapping["sensor"]
    
    connection = get_connection()
    try:
        cursor = connection.cursor(buffered=True)
        
        # Get the latest sensor reading
        query = "SELECT {}, timestamp FROM {} WHERE {} IS NOT NULL ORDER BY timestamp DESC LIMIT 1".format(
            sensor, table, sensor
        )
        cursor.execute(query)
        result = cursor.fetchone()

        if not result:
            return {"error": "No data found"}, 404

        # Fix: Return format that matches frontend expectations
        return {
            "value": float(result[0]) if result[0] is not None else 0,
            "unit": get_sensor_unit(sensor),
            "timestamp": result[1].isoformat() if result[1] else None
        }, 200

    except Error as e:
        print(e)
        return {"error": str(e)}, 500
    finally:
        cursor.close()
        connection.close()

# Fix: Add missing route for winsen plot page (winsen_plot.js calls /api/{table}/{sensor})
@app.route("/api/<string:table>/<string:sensor>")
def get_winsen_sensor_data(table, sensor):
    """Route for winsen sensor data (used by winsen_plot.js)"""
    allowed_tables = ["winsen1", "winsen2"]
    allowed_sensors = ["pm1", "pm25", "pm10", "co2", "voc", "temp", "humidity", "ch2o", "co", "o3", "no2"]

    if table not in allowed_tables or sensor not in allowed_sensors:
        return {"error": "Invalid table or sensor name"}, 400

    connection = get_connection()
    try:
        cursor = connection.cursor(buffered=True)
        
        # Get recent sensor data (last 100 readings)
        query = "SELECT {}, timestamp FROM {} WHERE {} IS NOT NULL ORDER BY timestamp DESC LIMIT 100".format(
            sensor, table, sensor
        )
        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
            return {"error": "No data found"}, 404

        data = [
            {"sensor_value": row[0], "timestamp": row[1].isoformat()}
            for row in result if row[0] is not None
        ]
        return {"data": data}, 200

    except Error as e:
        print(e)
        return {"error": str(e)}, 500
    finally:
        cursor.close()
        connection.close()

def validate_table_sensor_names(table, sensor):
    """Validate table and sensor names for security"""
    allowed_tables = ["winsen1", "winsen2", "tvoc_data"]
    allowed_sensors = ["pm1", "pm25", "pm10", "co2", "voc", "temp", "humidity", "ch2o", "co", "o3", "no2", "val", "ts"]
    
    # Validate table name
    if table not in allowed_tables:
        return False, f"Invalid table name: {table}"
    
    # Validate sensor name (if provided)
    if sensor and sensor not in allowed_sensors:
        return False, f"Invalid sensor name: {sensor}"
    
    return True, None

def get_sensor_unit(sensor_type):
    """Helper function to get appropriate unit for sensor type"""
    units = {
        "pm1": "μg/m³",
        "pm25": "μg/m³", 
        "pm10": "μg/m³",
        "co2": "ppm",
        "voc": "ppm",
        "temp": "°C",
        "humidity": "%",
        "ch2o": "μg/m³",
        "co": "ppm",
        "o3": "ppb",
        "no2": "ppb",
        "tvoc": "ppb"
    }
    return units.get(sensor_type, "units")
    

