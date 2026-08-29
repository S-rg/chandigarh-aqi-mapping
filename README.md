# Chandigarh AQI Mapping

High-resolution air quality mapping of the Tricity region (Chandigarh, Mohali, Panchkula), built by deploying a network of low-cost, custom IoT air quality nodes alongside industry-grade reference monitors. This repo is part of the **ILGC Project** at the Dixon IoT Lab, Plaksha University, under the broader *Digital Terrascope* initiative for smart-city IoT and analytics.

National monitoring stations (CPCB) are too sparse to capture hyperlocal pollution variation across a campus, neighborhood, or traffic corridor, and standard AQI only reflects the single worst pollutant, ignoring gases like NO2 and CO. This project addresses that by building affordable multi-sensor nodes, calibrating them against certified reference monitors, and surfacing the combined data (custom nodes + reference monitors + scraped public data) on a live map.

## Repo layout

```
AirQualityMonitor/   Teensy 4.1 firmware for the custom air quality nodes (PlatformIO)
configs/             YAML sensor configs, one per deployed node
scraping/            Scraper for public AQI data (aqi.in) across India
webapp/              Flask web app ("Tricity Watch") — REST API + live map/plot UI
rpi.py               Gateway script: reads node serial output and posts it to the API
temp_data_dumper.py  One-off loader for bulk-dumping scraped JSON into the database
logging_config.py    Shared logging setup
```

This repo covers node firmware, ingestion, storage, and the live web map.

## How it fits together

1. **Custom nodes** (`AirQualityMonitor/`) — a Teensy 4.1 runs a config-driven sensor library (particulate matter, TVOC, CO, SO2, O2, temperature/pressure, etc.). Each node is described entirely by a YAML file in `configs/`, which a build-time script (`AirQualityMonitor/scripts/generate_config_header.py`) turns into a generated header — adding or changing sensors on a node means editing YAML, not code.
2. **Gateway** (`rpi.py`) — a Raspberry Pi reads the node's serial output and POSTs each reading to the webapp's REST API (`/api/postdata/<node_id>/<sensor_id>/<measurement_id>`).
3. **Reference monitors** — two industry-grade monitors (Aurrasure, Prana Air) are collocated with the custom nodes to generate calibration curves via collocation-based calibration.
4. **Scraping** (`scraping/`) — pulls sub-hourly public AQI data for locations across India, which is stored alongside the project's own sensor data for direct comparison.
5. **Web platform** (`webapp/`) — a Flask app, *Tricity Watch*, that exposes the REST API and serves a live map (`/map/tricity`, `/map/india`) and per-node plots of all node and scraped data, backed by a MySQL database.

## Running it

**Node firmware** (`AirQualityMonitor/`) is a [PlatformIO](https://platformio.org/) project targeting the Teensy 4.1:

```
cd AirQualityMonitor
pio run              # build
pio run -t upload    # flash to a connected Teensy 4.1
```

See `AirQualityMonitor/README.md` for the sensor library's internal design notes.

**Web app** (`webapp/`) needs a MySQL database and a `.env` with `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` set. Initialize the schema with the scripts in `webapp/db_scripts/`, then:

```
cd webapp
python app.py
```

## Team

Arnav Kapoor, Mihir Narula, Suraj Dayma - mentored by Professor Srikant Srinivasan, Dixon IoT Lab, Plaksha University.
