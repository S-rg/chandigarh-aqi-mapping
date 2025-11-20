from flask import Flask, render_template
from mysql.connector import connect, Error
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt


app = Flask(__name__)


@app.route("/")
def hello():            
    return render_template('index.html')

@app.route('/winsen')
def winsen():
    return render_template('winsen_plot.html')

@app.route('/plot/<string:node_id>')
def plot(node_id):
    return render_template('plot.html', node_id=node_id)

@app.route('/map')
def map_page():
    return render_template('map.html')

from api_routes import api_bp
app.register_blueprint(api_bp)

load_dotenv()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
