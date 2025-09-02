from flask import Flask
from mysql.connector import connect, Error




app = Flask(__name__)

@app.route("/")
def hello():            
    return "WHEEEEEEEEEEEEEE SERVER WOOOOOOOOOOOOOOOO"

@app.route("/winsen1")
def winsen1():
    try:
        connection = connect(
            host="localhost",
            user="",
            password="",
            database="aqi_monitoring"
        )

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM winsen1 ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            columns = [desc[0] for desc in cursor.description]
            return "<br>".join([f"{col}: {val}" for col, val in zip(columns, result)])
        else:
            return "No data found."

    except Error as e:
        return f"Error connecting to database: {e}"
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route("/winsen2")
def winsen2():
    try:
        connection = connect(
            host="localhost",
            user="",
            password="",
            database="aqi_monitoring"
        )

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM winsen2 ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            columns = [desc[0] for desc in cursor.description]
            return "<br>".join([f"{col}: {val}" for col, val in zip(columns, result)])
        else:
            return "No data found."

    except Error as e:
        return f"Error connecting to database: {e}"
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()




if __name__ == "__main__":
    app.run()
