from flask import Flask
from mysql.connector import connect, Error
import os
from dotenv import load_dotenv

app = Flask(__name__)

@app.route("/")
def hello():            
    return "WHEEEEEEEEEEEEEE SERVER WOOOOOOOOOOOOOOOO"

@app.route('/dotenvtest')
def dotenvtest():
    return os.getenv("DB_HOST", "NOPE")

load_dotenv()

def get_connection():
    return connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", ""),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "aqi_monitoring")
    )

@app.route("/winsen1")
def winsen1():
    connection = get_connection()
    try:
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
    connection = get_connection()

    try:
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
