from flask import Flask, render_template, redirect, url_for, request
from mysql.connector import Error as MySQLError
import logging
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from utils import get_index_stats, get_node_stats, get_mock_stats, sanitize_stats


app = Flask(__name__)


# Load environment variables early so configuration flags are available.
load_dotenv()

# Environment-aware configuration for mock data usage.
# MOCK_DATA_ENABLED can be toggled via environment; by default it's enabled
# when running in debug/development mode.
default_mock_flag = "true" if app.debug or os.getenv("FLASK_ENV", "").lower() != "production" else "false"
app.config["MOCK_DATA_ENABLED"] = os.getenv("MOCK_DATA_ENABLED", default_mock_flag).lower() == "true"


# Configure logging with timestamps and levels for better observability.
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(formatter)
if not app.logger.handlers:
    app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)


@app.route("/")
def hello():
    hours = request.args.get("hours", default=24, type=int)
    app.logger.info("Handling dashboard request for last %s hours", hours)

    use_mock = app.config.get("MOCK_DATA_ENABLED", False) and (
        app.debug or os.getenv("FLASK_ENV", "").lower() != "production"
    )

    stats = None

    try:
        app.logger.info("Attempting to fetch index statistics from database")
        stats = get_index_stats(hours)
        app.logger.info("Successfully fetched index statistics from database")
    except MySQLError as db_err:
        app.logger.warning("Database error while fetching index stats: %s", db_err)
        if use_mock:
            app.logger.warning("Falling back to mock statistics due to database error")
            print("⚠️ Using mock data - database connection failed")
            stats = get_mock_stats(hours)
        else:
            # In production without mock data enabled, re-raise to fail fast.
            raise
    except Exception as exc:
        app.logger.error("Unexpected error while fetching index stats", exc_info=True)
        if use_mock:
            app.logger.warning("Falling back to mock statistics due to unexpected error")
            print("⚠️ Using mock data - database connection failed")
            stats = get_mock_stats(hours)
        else:
            raise

    # If we didn't hit an exception but the stats are None/partial or contain
    # None values, sanitize them before passing to the template. This also
    # covers the case where get_index_stats internally handled DB errors and
    # returned a partially-populated structure.
    stats = sanitize_stats(stats or {}, interval_hours=hours)

    return render_template("index.html", stats=stats)

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
