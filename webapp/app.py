from flask import Flask
from mysql.connector import connect, Error
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt


app = Flask(__name__)

import api_routes

@app.route("/")
def hello():            
    return "WHEEEEEEEEEEEEEE SERVER WOOOOOOOOOOOOOOOO"

load_dotenv()

if __name__ == "__main__":
    app.run()
