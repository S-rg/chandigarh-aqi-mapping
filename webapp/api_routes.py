from app import app
import os
from mysql.connector import connect, Error

def get_connection():
    return connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", ""),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "aqi_monitoring")
    )

@app.route("/api/<string:table>/<string:sensor>")
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

        data = [{"sensor_value": row[0], "timestamp": row[1].isoformat()} for row in result]
        return {"data": data}, 200

    except Error as e:
        print(e)
        return {"error": str(e)}, 500
    finally:
        cursor.close()
        connection.close()
    

