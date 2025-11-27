from flask import Flask, render_template, redirect, url_for
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

@app.route('/node/<string:node_id>')
def node(node_id):
    return render_template('node.html', stats=get_node_stats(node_id), node_id=node_id)

@app.route('/map')
def map_redirect():
    return redirect(url_for('map_india'))

@app.route('/map/india')
def map_india():
    map_config = {
        "apiUrl": url_for('api.get_latest_aqi_data'),
        "defaultCenter": [27.7, 85.3],
        "defaultZoom": 11,
        "useClustering": True,
        "showNumericMarkers": False,
        "countLabel": "locations"
    }
    return render_template(
        'map.html',
        map_title="AQI Monitoring Map - India",
        map_subtitle="Real-time air quality data across India",
        map_config=map_config
    )

@app.route('/map/tricity')
def map_tricity():
    bbox = {
        "min_lat": 30.6,
        "max_lat": 30.8,
        "min_lon": 76.7,
        "max_lon": 76.9
    }
    map_config = {
        "apiUrl": url_for('api.get_latest_aqi_data', **bbox),
        "defaultCenter": [30.7, 76.8],
        "defaultZoom": 12,
        "useClustering": False,
        "showNumericMarkers": True,
        "regionLabel": "Tricity (Chandigarh, Mohali, Panchkula)",
        "filters": bbox,
        "countLabel": "Tricity nodes"
    }
    return render_template(
        'map.html',
        map_title="AQI Map - Tricity",
        map_subtitle="Focused view of sensors around Chandigarh, Mohali, and Panchkula",
        map_config=map_config
    )

from api_routes import api_bp
app.register_blueprint(api_bp)

load_dotenv()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
