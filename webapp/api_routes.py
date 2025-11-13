from app import app
import os
from mysql.connector import connect, Error
from typing import List
from flask import request, render_template

def get_connection():
    return connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", ""),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "SMAQI")
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

@app.route("/api/get_all_nodes")
def get_all_nodes():
    connection = get_connection()
    cursor = connection.cursor(buffered=True)

    cursor.execute("SELECT DISTINCT node_id FROM Node;")

    result = cursor.fetchall()
    return {"nodes": [row[0] for row in result]}, 200

@app.route("/api/node/<string:node_id>")
def get_all_sensors(node_id):
    connection = get_connection()
    cursor = connection.cursor(buffered=True)

    cursor.execute(f"""SELECT sensor_id FROM Sensor WHERE node_id = {node_id};""")

    result = cursor.fetchall()
    return {"sensors": [row[0] for row in result]}, 200

@app.route("/api/sensor/<string:node_id>/<int:sensor_id>")
def get_all_measurements(node_id, sensor_id):
    connection = get_connection()
    cursor = connection.cursor(buffered=True)

    cursor.execute(f"""SELECT measurement_id FROM Sensor WHERE node_id = {node_id} AND sensor_id = {sensor_id};""")

    result = cursor.fetchall()
    return {"measurements": [row[0] for row in result]}, 200

@app.route("/api/measurement/<string:node_id>/<int:sensor_id>/<int:measurement_id>")
def get_measurement_data(node_id, sensor_id, measurement_id):
    connection = get_connection()
    cursor = connection.cursor(buffered=True)

    cursor.execute(f"""SELECT timestamp, value FROM {node_id}_{sensor_id}_{measurement_id};""")

    result = cursor.fetchall()
    data = [{"timestamp": row[0].isoformat(), "value": row[1]} for row in result]
    return {"data": data}, 200


@app.route("/api/postdata/<string:node_id>/<int:sensor_id>/<int:measurement_id>", methods=["POST"])
def post_data(node_id, sensor_id, measurement_id):
    try:
        data = request.get_json()
        if not data or "timestamp" not in data or "value" not in data:
            return {"error": "Invalid data"}, 400

        timestamp = data["timestamp"]
        value = data["value"]

        connection = get_connection()
        cursor = connection.cursor()

        query = f"""
            INSERT INTO {node_id}_{sensor_id}_{measurement_id} (timestamp, value)
            VALUES (%s, %s);
        """
        cursor.execute(query, (timestamp, value))
        connection.commit()

        return {"message": "Data inserted successfully"}, 200

    except Error as e:
        print(e)
        return {"error": str(e)}, 500

    finally:
        cursor.close()
        connection.close()


@app.route("/api/get_sensor_mapping/<string:node_id>")
def get_sensor_mapping(node_id):
    query = f"""
        SELECT sensor_id, measurement_id, measurement_name, unit, sensor_type FROM Sensor WHERE node_id = %s;
    """

    connection = get_connection()
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute(query, (node_id,))
        result = cursor.fetchall()

        if not result:
            return {"error": "No data found"}, 404

        mapping = {
            f"{row[0]},{row[1]}": [row[2], row[3], row[4]]
            for row in result
        }
        return {"mapping": mapping}, 200
    
    except Error as e:
        print(e)
        return {"error": str(e)}, 500
    
    finally:
        cursor.close()
        connection.close()