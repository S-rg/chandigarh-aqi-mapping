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
                "name": sensor["measurement_name"],
                "unit": sensor["unit"],
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
        result["aqi_time"] = aqi_time

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


def get_index_stats(interval_hours=24):
    if interval_hours not in [24, 168, 720]:
        interval_hours = 24
    """
    Get AQI statistics for the specified time interval.
    
    Args:
        interval_hours: Time interval in hours (24 for 1 day, 168 for 7 days, 720 for 30 days)
    
    Recommended indexes:
        CREATE INDEX idx_timestamp ON {node_table} (timestamp DESC);
        CREATE INDEX idx_timestamp_value ON {node_table} (timestamp, value);
    """
    load_dotenv()

    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME')
    }

    # Initialize result with all required keys including worst1-worst5
    result = {
        'avg_aqi': None,
        'active_nodes': 0,
        'alerts': 0,
        'most_common_pollutant': 'PM2.5',
        'aqi_trend_path': [],
        'aqi_time': [],
        'good': 0,
        'moderate': 0,
        'unhealthy': 0,
        'hazardous': 0,
        'worst1': {'name': None, 'aqi': None, 'location': None},
        'worst2': {'name': None, 'aqi': None, 'location': None},
        'worst3': {'name': None, 'aqi': None, 'location': None},
        'worst4': {'name': None, 'aqi': None, 'location': None},
        'worst5': {'name': None, 'aqi': None, 'location': None},
        'hours': interval_hours
    }

    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------------------
        # 1. Load node metadata
        # -------------------------------------------------------------
        cursor.execute("SELECT node_id, location FROM Node")
        nodes = cursor.fetchall()
        
        if not nodes:
            return result  # Return initialized result instead of error
            
        node_locations = {n["node_id"]: n["location"] for n in nodes}
        node_ids = list(node_locations.keys())
        node_tables = [f"{nid}_1_1" for nid in node_ids]

        result['active_nodes'] = len(node_tables)

        # -------------------------------------------------------------
        # 2. OPTIMIZED: Get latest value and interval data for each node
        # -------------------------------------------------------------
        latest_values = {}
        trend_data = []
        category_values = []

        for node_id, tbl in zip(node_ids, node_tables):
            try:
                # Get latest value
                cursor.execute(f"""
                    SELECT value, timestamp
                    FROM {tbl}
                    ORDER BY timestamp DESC
                    LIMIT 1
                """)
                latest_row = cursor.fetchone()
                
                if latest_row and latest_row["value"] is not None:
                    latest_values[node_id] = {
                        "value": latest_row["value"],
                        "timestamp": latest_row["timestamp"],
                        "location": node_locations.get(node_id, "Unknown")
                    }
                
                # Get interval data for trend and categories
                cursor.execute(f"""
                    SELECT value, timestamp
                    FROM {tbl}
                    WHERE timestamp >= NOW() - INTERVAL {interval_hours} HOUR
                    ORDER BY timestamp ASC
                """)
                
                interval_rows = cursor.fetchall()
                for row in interval_rows:
                    if row["value"] is not None:
                        trend_data.append({"timestamp": row["timestamp"], "value": row["value"]})
                        category_values.append(row["value"])
                        
            except mysql.connector.Error as e:
                print(f"Error querying table {tbl}: {e}")
                continue

        # -------------------------------------------------------------
        # 3. Calculate average AQI
        # -------------------------------------------------------------
        if latest_values:
            avg_aqi = sum(d["value"] for d in latest_values.values()) / len(latest_values)
            result['avg_aqi'] = round(avg_aqi, 2)

        # -------------------------------------------------------------
        # 4. Build AQI trend (hourly or daily based on interval)
        # -------------------------------------------------------------
        if trend_data:
            from collections import defaultdict
            from datetime import datetime, timedelta
            
            # Determine grouping (hourly for 24h, daily for longer periods)
            if interval_hours <= 24:
                # Hourly grouping
                hourly_avg = defaultdict(list)
                
                for item in trend_data:
                    hour = item["timestamp"].hour
                    hourly_avg[hour].append(item["value"])
                
                trend_values = []
                for h in range(24):
                    if h in hourly_avg:
                        trend_values.append(sum(hourly_avg[h]) / len(hourly_avg[h]))
                    elif trend_values:
                        trend_values.append(trend_values[-1])
                    else:
                        trend_values.append(0)
                
                result['aqi_time'] = [f"{str(h).zfill(2)}" for h in range(0, 25, 4)]
            
            else:
                # Daily grouping for 7 days or 30 days
                daily_avg = defaultdict(list)
                
                for item in trend_data:
                    day = item["timestamp"].date()
                    daily_avg[day].append(item["value"])
                
                # Calculate number of days
                num_days = min(interval_hours // 24, 30)
                trend_values = []
                
                end_date = datetime.now().date()
                for i in range(num_days):
                    day = end_date - timedelta(days=num_days - 1 - i)
                    if day in daily_avg:
                        trend_values.append(sum(daily_avg[day]) / len(daily_avg[day]))
                    elif trend_values:
                        trend_values.append(trend_values[-1])
                    else:
                        trend_values.append(0)
                
                # Time labels for days
                if num_days <= 7:
                    result['aqi_time'] = [f"Day {i+1}" for i in range(0, num_days, max(1, num_days // 6))]
                else:
                    result['aqi_time'] = [f"Day {i+1}" for i in range(0, num_days, max(1, num_days // 6))]
            
            result['aqi_trend_path'] = generate_smooth_path(trend_values)
        else:
            result['aqi_trend_path'] = generate_smooth_path([0] * 24)
            result['aqi_time'] = [f"{str(h).zfill(2)}" for h in range(0, 25, 4)]

        # -------------------------------------------------------------
        # 5. Calculate AQI category percentages
        # -------------------------------------------------------------
        if category_values:
            total = len(category_values)
            result['good'] = round(sum(1 for v in category_values if v < 50) * 100.0 / total, 2)
            result['moderate'] = round(sum(1 for v in category_values if 50 <= v <= 100) * 100.0 / total, 2)
            result['unhealthy'] = round(sum(1 for v in category_values if 100 < v <= 200) * 100.0 / total, 2)
            result['hazardous'] = round(sum(1 for v in category_values if v > 200) * 100.0 / total, 2)

        # -------------------------------------------------------------
        # 6. Worst 5 nodes by latest AQI
        # -------------------------------------------------------------
        worst_list = [
            {
                "node_id": node_id,
                "name": node_id,
                "aqi": data["value"],
                "location": data["location"]
            }
            for node_id, data in latest_values.items()
        ]
        
        worst_list.sort(key=lambda x: x["aqi"], reverse=True)
        worst_list = worst_list[:5]

        # IMPORTANT: Always populate all worst1-worst5 keys
        for i in range(5):
            if i < len(worst_list):
                result[f"worst{i+1}"] = {
                    'name': worst_list[i]["name"],
                    'aqi': worst_list[i]["aqi"],
                    'location': worst_list[i]["location"]
                }
            else:
                result[f"worst{i+1}"] = {
                    'name': None,
                    'aqi': None,
                    'location': None
                }

        # -------------------------------------------------------------
        # 7. Optional: Count alerts (AQI > threshold)
        # -------------------------------------------------------------
        result['alerts'] = sum(1 for v in latest_values.values() if v["value"] > 100)

    except mysql.connector.Error as e:
        print("Database error:", e)
        # Return the initialized result even on error
        return result

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return result


def generate_smooth_path(values, width=472, height=150):
    values = [v if v is not None else 0 for v in values]
    if sum(values) == 0:
        values = [1 for _ in values]
    n = len(values)
    if n < 2:
        raise ValueError("Need at least 2 points")

    # Normalize Y values (invert SVG Y axis)
    max_val = max(values)
    scaled = [height - (v / max_val * height + 0.000001) for v in values]

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