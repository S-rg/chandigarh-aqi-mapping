from flask import Flask, render_template
from mysql.connector import connect, Error
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from utils import get_index_stats, get_node_stats


app = Flask(__name__)


@app.route("/")
def hello():
    stats = get_index_stats()
    print(stats)
    return render_template('index.html', stats=stats)

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
