from flask import Flask, render_template
from mysql.connector import connect, Error
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt


app = Flask(__name__)

import api_routes

@app.route("/")
def hello():            
    return "WHEEEEEEEEEEEEEE SERVER WOOOOOOOOOOOOOOOO"

@app.route('/winsen')
def winsen():
    return render_template('winsen_plot.html')

load_dotenv()

if __name__ == "__main__":
    app.run()
