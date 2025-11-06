import mysql.connector
from dotenv import load_dotenv
import os
from logging_config import setup_logging
import logging

def init_tables(cursor, logger):
    create_node_table(cursor, logger)
    create_sensor_table(cursor, logger)

def create_node_table(cursor, logger):
    create_table_query = """
    CREATE TABLE Node (
        node_id VARCHAR(50) PRIMARY KEY,
        location VARCHAR(255) NOT NULL,
        latitude DOUBLE NOT NULL,
        longitude DOUBLE NOT NULL
    );
    """
    cursor.execute(create_table_query)
    logger.info("Node table created successfully.")


def create_sensor_table(cursor, logger):
    create_table_query = """
    CREATE TABLE Sensor (
        node_id VARCHAR(50) NOT NULL,
        sensor_id INT NOT NULL,
        measurement_id INT NOT NULL,
        sensor_type VARCHAR(255),
        sensor_model VARCHAR(255),
        measurement_name VARCHAR(255),
        unit VARCHAR(50) NOT NULL,
        FOREIGN KEY (node_id) REFERENCES Node(node_id),
        PRIMARY KEY (node_id, sensor_id, measurement_id)
    );
    """
    cursor.execute(create_table_query)
    logger.info("Sensor table created successfully.")

def main():
    logger = logging.getLogger(__name__)
    DB_NAME = os.getenv("DB_NAME")

    config = {
        'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD", ""),
        'host': os.getenv("DB_HOST", "localhost")
    }

    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        logger.info("Connected to MySQL server.")

        cursor.execute(f"CREATE DATABASE {DB_NAME};") # Throws error 1007 if DB exists
        cursor.execute(f"USE {DB_NAME};")

        init_tables(cursor, logger)


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
    setup_logging()
    load_dotenv()
    main()