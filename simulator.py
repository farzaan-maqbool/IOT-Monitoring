"""Publish simulated sensor readings to the MQTT broker."""
import json
import os
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "iot/sensor/data")
DEVICE_ID = os.getenv("DEVICE_ID", "simulated-device-01")
INTERVAL_SECONDS = float(os.getenv("INTERVAL_SECONDS", "3"))


def main():
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"sensor-simulator-{DEVICE_ID}",
    )
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_start()
    temperature = 24.0
    humidity = 55.0
    print(f"Publishing simulated readings to {MQTT_HOST}:{MQTT_PORT} topic {MQTT_TOPIC}")
    try:
        while True:
            temperature = max(-5, min(45, temperature + random.uniform(-1.2, 1.2)))
            humidity = max(20, min(90, humidity + random.uniform(-3, 3)))
            payload = {
                "device_id": DEVICE_ID,
                "temperature": round(temperature, 2),
                "humidity": round(humidity, 2),
                "simulated_at": datetime.now(timezone.utc).isoformat(),
            }
            info = client.publish(MQTT_TOPIC, json.dumps(payload), qos=0)
            info.wait_for_publish()
            print(payload)
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nSimulator stopped.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
