import mysql.connector
import os
from dotenv import load_dotenv

def get_index_stats_dummy():
    import random
    # Dummy implementation for illustration purposes
    return {
        'avg_aqi': 40,
        'active_nodes': 3,
        'alerts': 0,
        'most_common_pollutant': 'PM2.5',
        'aqi_trend_path': generate_smooth_path([random.randint(10, 100) for _ in range(24)]),
        'aqi_time': [f"{str(h).zfill(2)}" for h in range(0, 25, 4)],
        'good': 70,
        'moderate': 20,
        'unhealthy': 5,
        'hazardous': 5,
        'worst1': {
            'name': 'Node A',
            'aqi': 80,
            'location': 'California, USA'
        },
        'worst2': {
            'name': 'Node B',
            'aqi': 75,
            'location': 'Texas, USA'
        },
        'worst3': {
            'name': 'Node C',
            'aqi': 70,
            'location': 'Florida, USA'
        },
        'worst4': {
            'name': 'Node D',
            'aqi': 65,
            'location': 'New York, USA'
        },
        'worst5': {
            'name': 'Node E',
            'aqi': 60,
            'location': 'Illinois, USA'
        }
    }

def get_node_stats(node_id):
    result = {}
    
    load_dotenv()
    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME')
    }

    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT node_id, sensor_id, measurement_id, measurement_name, unit FROM Sensor WHERE node_id = %s", (node_id,))
        sensors = cursor.fetchall()

        sensor_values = []
        for sensor in sensors:
            tbl_name = f"{sensor['node_id']}_{sensor['sensor_id']}_{sensor['measurement_id']}"
            cursor.execute(f"""
                SELECT value
                FROM {tbl_name}
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            value = row["value"] if row else None
            sensor_values.append({
                "name": sensor["measurement_name"].encode('latin1').decode('utf8'),
                "unit": sensor["unit"].encode('latin1').decode('utf8'),
                "value": value
            })

        result["measurements"] = sensor_values

        tbl_name = f"{node_id}_1_1"
        cursor.execute(f"""
            SELECT HOUR(timestamp) AS hr, AVG(value) AS avg_val
            FROM {tbl_name}
            WHERE timestamp >= NOW() - INTERVAL 24 HOUR
            GROUP BY hr
            ORDER BY hr
        """)
        rows = cursor.fetchall()

        hourly_aqi = [None] * 24
        hours_present = set()
        for row in rows:
            hr = row["hr"]
            hourly_aqi[hr] = row["avg_val"]
            hours_present.add(hr)

        last_val = None
        for i in range(24):
            if hourly_aqi[i] is None:
                hourly_aqi[i] = last_val
            else:
                last_val = hourly_aqi[i]

        first_hour = min(hours_present) if hours_present else 0
        aqi_time = [f"{str((first_hour + 4 * i) % 24).zfill(2)}" for i in range(6)]
        result["aqi_path"] = aqi_time

        result["aqi_trend_path"] = generate_smooth_path(hourly_aqi)

    except mysql.connector.Error as e:
        print("Database error:", e)
        result = {"error": str(e)}
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return result


def get_index_stats():
    load_dotenv()

    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME')
    }

    result = {
        'avg_aqi': None,
        'active_nodes': 0,
        'alerts': 0,
        'most_common_pollutant': None,
        'aqi_trend_path': [],
        'aqi_time': [],
        'good': 0,
        'moderate': 0,
        'unhealthy': 0,
        'hazardous': 0,
        'worst1': None,
        'worst2': None,
        'worst3': None,
        'worst4': None,
        'worst5': None,
    }

    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------------------
        # 1. Discover all node tables
        # -------------------------------------------------------------
        # cursor.execute("""
        #     SELECT table_name 
        #     FROM information_schema.tables
        #     WHERE table_schema = %s
        #     AND table_name LIKE '%%_1_1'
        # """, (db_config["database"],))
        # node_tables = [row["table_name"] for row in cursor.fetchall()]

        # if not node_tables:
        #     return {"error": "No node AQI tables found"}

        # -------------------------------------------------------------
        # 2. Load basic node metadata
        # -------------------------------------------------------------
        cursor.execute("SELECT node_id, location FROM Node")
        nodes = cursor.fetchall()
        node_locations = {n["node_id"]: n["location"] for n in nodes}

        node_ids = list(node_locations.keys())
        node_tables = [f"{nid}_1_1" for nid in node_ids]

        # -------------------------------------------------------------
        # 3. Compute avg AQI across all nodes
        # -------------------------------------------------------------
        # Get the most recent AQI value from each node table and compute their average
        latest_values = []
        for tbl in node_tables:
            cursor.execute(f"""
                SELECT value
                FROM {tbl}
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row and row["value"] is not None:
                latest_values.append(row["value"])
    
        avg_aqi = sum(latest_values) / len(latest_values) if latest_values else None

        # -------------------------------------------------------------
        # 4. Count active nodes (all nodes are active)
        # -------------------------------------------------------------
        
        active_nodes = len(node_tables)

        # -------------------------------------------------------------
        # 5. AQI Trend (past 24 hours) — hourly AVG across all nodes
        # -------------------------------------------------------------
        trend_sql_parts = []
        for tbl in node_tables:
            trend_sql_parts.append(
                f"SELECT HOUR(timestamp) AS hr, value FROM {tbl} "
                "WHERE timestamp >= NOW() - INTERVAL 24 HOUR"
            )
        trend_union = " UNION ALL ".join(trend_sql_parts)

        cursor.execute(f"""
            SELECT hr, AVG(value) AS avg_val
            FROM ({trend_union}) AS t
            GROUP BY hr
            ORDER BY hr
        """)

        trend_rows = cursor.fetchall()
        aqi_trend_values = [row["avg_val"] for row in trend_rows]

        # Pad to 24 entries if needed
        if len(aqi_trend_values) < 24:
            aqi_trend_values += [aqi_trend_values[-1]] * (24 - len(aqi_trend_values))

        aqi_trend_path = generate_smooth_path(aqi_trend_values)

        # -------------------------------------------------------------
        # 6. AQI Category Percentages
        # -------------------------------------------------------------
        union_sql = " UNION ALL ".join([
            f"SELECT value FROM {tbl} WHERE timestamp >= NOW() - INTERVAL 24 HOUR"
            for tbl in node_tables
        ])

        category_sql = f"""
            SELECT 
                SUM(CASE WHEN value < 50 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS good,
                SUM(CASE WHEN value BETWEEN 50 AND 100 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS moderate,
                SUM(CASE WHEN value BETWEEN 100 AND 200 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS unhealthy,
                SUM(CASE WHEN value > 200 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS hazardous
            FROM ({union_sql}) AS all_values
        """
        cursor.execute(category_sql)
        category_data = cursor.fetchone()

        # -------------------------------------------------------------
        # 7. Worst 5 nodes by latest AQI
        # -------------------------------------------------------------
        worst_list = []
        for node_id, tbl in zip(node_ids, node_tables):
            cursor.execute(f"""
                SELECT value, timestamp
                FROM {tbl}
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            if not row:
                continue
            worst_list.append({
                "node_id": node_id,
                "name": f"Node {node_id}",
                "aqi": row["value"],
                "location": node_locations.get(node_id, "Unknown")
            })

        worst_list = sorted(worst_list, key=lambda x: x["aqi"], reverse=True)
        worst_list = worst_list[:5]  # keep only top 5

        # -------------------------------------------------------------
        # 8. Assemble final result dictionary
        # -------------------------------------------------------------
        result = {
            'avg_aqi': round(avg_aqi, 2) if avg_aqi else None,
            'active_nodes': active_nodes,
            'alerts': 0,  # Optional: define alert threshold
            'most_common_pollutant': "PM2.5",  # Placeholder unless pollutant table exists
            'aqi_trend_path': aqi_trend_path,
            'aqi_time': [f"{str(h).zfill(2)}" for h in range(0, 25, 4)],
            'good': round(category_data["good"], 2),
            'moderate': round(category_data["moderate"], 2),
            'unhealthy': round(category_data["unhealthy"], 2),
            'hazardous': round(category_data["hazardous"], 2),
        }

        # Add worst1…worst5
        for i, w in enumerate(worst_list):
            result[f"worst{i+1}"] = {
                'name': w["name"],
                'aqi': w["aqi"],
                'location': w["location"]
            }

        if len(worst_list) < 5:
            for i in range(len(worst_list), 5):
                result[f"worst{i+1}"] = {
                    'name': None,
                    'aqi': None,
                    'location': None
                }

    except mysql.connector.Error as e:
        print("Database error:", e)
        return {"error": str(e)}

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return result


def generate_smooth_path(values, width=472, height=150):
    n = len(values)
    if n < 2:
        raise ValueError("Need at least 2 points")

    # Normalize Y values (invert SVG Y axis)
    max_val = max(values)
    scaled = [height - (v / max_val * height) for v in values]

    # Evenly spaced X values
    step = width / (n - 1)
    pts = [(i * step, scaled[i]) for i in range(n)]

    def catmull_rom_to_bezier(p0, p1, p2, p3):
        """
        Convert 4 Catmull-Rom points into 2 Bézier control points.
        """
        c1 = (p1[0] + (p2[0] - p0[0]) / 6,
              p1[1] + (p2[1] - p0[1]) / 6)

        c2 = (p2[0] - (p3[0] - p1[0]) / 6,
              p2[1] - (p3[1] - p1[1]) / 6)

        return c1, c2

    # Start
    d = [f"M{pts[0][0]},{pts[0][1]}"]

    # Build smooth curve
    for i in range(n - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1 = pts[i]
        p2 = pts[i + 1]
        p3 = pts[i + 2] if i + 2 < n else pts[i + 1]

        c1, c2 = catmull_rom_to_bezier(p0, p1, p2, p3)

        d.append(f"C{c1[0]},{c1[1]} {c2[0]},{c2[1]} {p2[0]},{p2[1]}")

    line_path = " ".join(d)

    # Area path (close shape)
    area_path = line_path + f" V{height} H0 Z"

    return area_path, line_path