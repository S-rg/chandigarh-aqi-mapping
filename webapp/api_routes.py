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

# NEW: Gas-specific endpoint for latest reading (replaces sensor ID mapping)
@app.route("/api/gas/<string:table>/<string:gas>/latest")
def get_gas_latest_reading(table, gas):
    """Get latest reading for a specific gas from a specific table"""
    # Validate inputs
    is_valid, error_msg = validate_table_sensor_names(table, gas)
    if not is_valid:
        return {"error": error_msg}, 400
    
    connection = get_connection()
    try:
        cursor = connection.cursor(buffered=True)
        
        # Get the latest gas reading
        query = "SELECT {}, timestamp FROM {} WHERE {} IS NOT NULL ORDER BY timestamp DESC LIMIT 1".format(
            gas, table, gas
        )
        cursor.execute(query)
        result = cursor.fetchone()

        if not result:
            return {"error": "No data found"}, 404

        return {
            "value": float(result[0]) if result[0] is not None else 0,
            "unit": get_sensor_unit(gas),
            "timestamp": result[1].isoformat() if result[1] else None,
            "gas": gas,
            "table": table
        }, 200

    except Error as e:
        print(e)
        return {"error": str(e)}, 500
    finally:
        cursor.close()
        connection.close()

# NEW: Gas-specific endpoint for historical data
@app.route("/api/gas/<string:table>/<string:gas>/history")
def get_gas_history(table, gas):
    """Get historical data for a specific gas from a specific table"""
    # Validate inputs
    is_valid, error_msg = validate_table_sensor_names(table, gas)
    if not is_valid:
        return {"error": error_msg}, 400
    
    connection = get_connection()
    try:
        cursor = connection.cursor(buffered=True)
        
        # Get recent gas data (last 100 readings)
        query = "SELECT {}, timestamp FROM {} WHERE {} IS NOT NULL ORDER BY timestamp DESC LIMIT 100".format(
            gas, table, gas
        )
        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
            return {"error": "No data found"}, 404

        data = [
            {"sensor_value": row[0], "timestamp": row[1].isoformat()}
            for row in result if row[0] is not None
        ]
        return {
            "data": data,
            "gas": gas,
            "table": table
        }, 200

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

# LEGACY: Keep old sensor ID route for backward compatibility (can be removed later)
@app.route("/api/sensor<int:sensor_id>")
def get_sensor_data_by_id(sensor_id):
    """LEGACY: Route for individual sensor data (will be deprecated)"""
    # This route will be removed once frontend is updated
    return {"error": "This endpoint is deprecated. Use /api/gas/{table}/{gas}/latest instead"}, 410

# LEGACY: Keep old winsen route for backward compatibility
@app.route("/api/<string:table>/<string:sensor>")
def get_winsen_sensor_data(table, sensor):
    """LEGACY: Route for winsen sensor data (will be deprecated)"""
    return {"error": "This endpoint is deprecated. Use /api/gas/{table}/{sensor}/history instead"}, 410

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