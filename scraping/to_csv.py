from dotenv import load_dotenv
import os
import mysql.connector
import pandas as pd

load_dotenv("/home/studentiotlab/aqi-dashboard/.env")

def login():
    db = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")

    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=db
    )

    return conn

def export_to_csv(conn):
    query = "SELECT * FROM AqiInScrape"
    df = pd.read_sql(query, conn)
    df.to_csv("aqi_in_data.csv", index=False)

def main():
    conn = login()
    export_to_csv(conn)
    conn.close()

if __name__ == "__main__":
    main()
