import mysql.connector
from dotenv import load_dotenv
import os


def init_tables(cursor):
    create_node_table(cursor)
    create_sensor_table(cursor)

def create_node_table(cursor):
    create_table_query = """
    CREATE TABLE Node (
        node_id INT PRIMARY KEY,
        location VARCHAR(255) NOT NULL,
        latitude DOUBLE NOT NULL,
        longitude DOUBLE NOT NULL
    );
    """
    cursor.execute(create_table_query)
    print("Node table created successfully.")


def create_sensor_table(cursor):
    create_table_query = """
    CREATE TABLE Sensor (
        node_id INT NOT NULL,
        sensor_id INT NOT NULL,
        measurement_id INT NOT NULL,
        sensor_type VARCHAR(255) NOT NULL,
        sensor_model VARCHAR(255) NOT NULL,
        measurement_name VARCHAR(255) NOT NULL,
        unit VARCHAR(50) NOT NULL,
        FOREIGN KEY (node_id) REFERENCES Node(node_id),
        PRIMARY KEY (node_id, sensor_id, measurement_id)
    );
    """
    cursor.execute(create_table_query)
    print("Sensor table created successfully.")

def main():
    DB_NAME = os.getenv("DB_NAME")

    config = {
        'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD", ""),
        'host': os.getenv("DB_HOST", "localhost")
    }

    try:
        conn = mysql.connector.connect(**config)
        print("Connection established!")
        cursor = conn.cursor()
        print("Cursor created!")

        cursor.execute(f"CREATE DATABASE {DB_NAME};") # Throws error 1007 if DB exists
        print(f"Database {DB_NAME} created successfully.")
        cursor.execute(f"USE {DB_NAME};")

        init_tables(cursor)


    except mysql.connector.Error as err:
        if err.errno == 1007:  # Error code for "ER_DB_CREATE_EXISTS"
            raise RuntimeError(f"Database '{DB_NAME}' already exists.") from err
        else:
            raise

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    load_dotenv()
    main()