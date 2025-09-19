from app import app
import os
from mysql.connector import connect, Error
from typing import List

def get_connection():
    return connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", ""),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "aqi_monitoring")
    )

def get_data(table: str, cols: List[str]):
    connection = get_connection()
    cols_str = ",".join(cols)
    try:
        cursor = connection.cursor(buffered=True)
        query = f"SELECT {cols_str} FROM {table} WHERE id > (SELECT MAX(id) - 1000 FROM {table});"
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
    data = get_data("tvoc_data", cols)
    return data


@app.route("/api/temp/<string:table>/<string:sensor>")
def get_sensor_data(table, sensor):
    allowed_tables = ["winsen1", "winsen2"]
    allowed_sensors = ["pm1", "pm25", "pm10", "co2", "voc", "temp", "humidity", "ch2o", "co", "o3", "no2"]

    if table not in allowed_tables or sensor not in allowed_sensors:
        return {"error": "Invalid table or sensor name"}, 400

    connection = get_connection()
    try:
        cursor = connection.cursor(buffered=True)
        query = f"SELECT {sensor}, timestamp FROM {table};"
        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
            return {"error": "No data found"}, 404

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
    

