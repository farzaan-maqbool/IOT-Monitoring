import json
import os
import threading
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://iot_user:iot_password@localhost:5432/iot_monitoring"
)
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "iot/sensor/data")

mqtt_client = None
mqtt_status = {"connected": False, "message": "Connecting to MQTT broker..."}


def get_db_connection():
    return psycopg2.connect(DATABASE_URL, connect_timeout=5)


def init_db():
    """Create the readings table if it does not already exist."""
    last_error = None
    for _ in range(20):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS sensor_readings (
                            id BIGSERIAL PRIMARY KEY,
                            device_id VARCHAR(100) NOT NULL,
                            temperature DOUBLE PRECISION NOT NULL,
                            humidity DOUBLE PRECISION NOT NULL,
                            recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        );
                    """)
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_sensor_readings_recorded_at
                        ON sensor_readings (recorded_at DESC);
                    """)
            return
        except Exception as exc:
            last_error = exc
            import time
            time.sleep(2)
    raise RuntimeError(f"Could not initialize PostgreSQL: {last_error}")


def save_reading(payload):
    device_id = str(payload.get("device_id", "simulated-device-01"))[:100]
    temperature = float(payload["temperature"])
    humidity = float(payload["humidity"])

    # Reject malformed or unrealistic values rather than storing them.
    if not (-50 <= temperature <= 100):
        raise ValueError("temperature must be between -50 and 100 °C")
    if not (0 <= humidity <= 100):
        raise ValueError("humidity must be between 0 and 100 %")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sensor_readings (device_id, temperature, humidity)
                VALUES (%s, %s, %s)
                """,
                (device_id, temperature, humidity),
            )


def on_connect(client, userdata, flags, reason_code, properties=None):
    connected = getattr(reason_code, "is_failure", None)
    is_failure = connected if connected is not None else (int(reason_code) != 0)
    if not is_failure:
        mqtt_status.update(connected=True, message="Connected")
        client.subscribe(MQTT_TOPIC, qos=0)
        print(f"MQTT connected; subscribed to {MQTT_TOPIC}")
    else:
        mqtt_status.update(connected=False, message=f"Connection failed: {reason_code}")
        print(f"MQTT connection failed: {reason_code}")


def on_disconnect(client, userdata, disconnect_flags=None, reason_code=None, properties=None):
    mqtt_status.update(connected=False, message="Disconnected")
    print("MQTT disconnected")


def on_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))
        save_reading(payload)
        print(f"Saved reading from {payload.get('device_id', 'unknown device')}")
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"Ignored invalid MQTT message: {exc}")
    except Exception as exc:
        print(f"Could not save MQTT message: {exc}")


def start_mqtt():
    global mqtt_client
    try:
        # Callback API VERSION2 is supported by paho-mqtt 2.x.
        mqtt_client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id="iot-monitoring-dashboard",
        )
        mqtt_client.on_connect = on_connect
        mqtt_client.on_disconnect = on_disconnect
        mqtt_client.on_message = on_message
        mqtt_client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
        mqtt_client.loop_start()
    except Exception as exc:
        mqtt_status.update(connected=False, message=f"MQTT unavailable: {exc}")
        print(f"Could not start MQTT client: {exc}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/readings")
def api_readings():
    limit = request.args.get("limit", default=100, type=int)
    limit = max(1, min(limit or 100, 500))
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, device_id, temperature, humidity, recorded_at
                FROM sensor_readings
                ORDER BY recorded_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()

    readings = []
    for row in reversed(rows):
        readings.append({
            "id": row["id"],
            "device_id": row["device_id"],
            "temperature": row["temperature"],
            "humidity": row["humidity"],
            "recorded_at": row["recorded_at"].isoformat(),
        })
    return jsonify(readings)


@app.route("/api/status")
def api_status():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM sensor_readings")
                count = cur.fetchone()[0]
        db_ok = True
    except Exception:
        count = 0
        db_ok = False

    return jsonify({
        "mqtt_connected": mqtt_status["connected"],
        "mqtt_message": mqtt_status["message"],
        "database_connected": db_ok,
        "total_readings": count,
    })


@app.route("/api/alerts")
def api_alerts():
    threshold = request.args.get("temperature", default=35.0, type=float)
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, device_id, temperature, humidity, recorded_at
                FROM sensor_readings
                WHERE temperature >= %s
                ORDER BY recorded_at DESC
                LIMIT 50
                """,
                (threshold,),
            )
            rows = cur.fetchall()
    return jsonify([
        {
            "id": row["id"],
            "device_id": row["device_id"],
            "temperature": row["temperature"],
            "humidity": row["humidity"],
            "recorded_at": row["recorded_at"].isoformat(),
        }
        for row in rows
    ])


if __name__ == "__main__":
    init_db()
    threading.Thread(target=start_mqtt, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
