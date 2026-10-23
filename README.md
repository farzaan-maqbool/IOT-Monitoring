# Real-Time IoT Monitoring Dashboard (Simulated Sensors)

A portfolio-ready learning project that demonstrates MQTT messaging, a Flask backend, PostgreSQL persistence, and a live browser dashboard. It uses **simulated sensor readings**, so no physical Arduino or sensors are required.

## Architecture

`simulator.py` → MQTT broker (Mosquitto) → Flask MQTT subscriber → PostgreSQL → dashboard

## Requirements

- Python 3.10+
- Docker Desktop (recommended for running PostgreSQL and Mosquitto locally)
- A modern browser

## 1. Start PostgreSQL and MQTT

Open a terminal in this project folder and run:

```bash
docker compose up -d
```

This starts:
- PostgreSQL at `localhost:5432`
- Mosquitto MQTT broker at `localhost:1883`

Local development credentials:
- Database: `iot_monitoring`
- User: `iot_user`
- Password: `iot_password`

These are for local learning only. Do not expose this setup publicly or use these credentials in production.

## 2. Create a Python virtual environment

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, you can instead run:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```
Then use `.\.venv\Scripts\python.exe` instead of `python`.

## 3. Run the Flask dashboard

In terminal 1:

```powershell
python app.py
```

Open `http://127.0.0.1:5000` in your browser. On first start, the app creates the PostgreSQL table automatically.

## 4. Start the sensor simulator

Open a **second terminal**, activate the same virtual environment, and run:

```powershell
python simulator.py
```

The simulator publishes a temperature and humidity reading every 3 seconds. The dashboard should begin updating and storing readings.

Stop the simulator with `Ctrl+C`.

## 5. Check the API endpoints

- `GET /api/status` — MQTT/PostgreSQL connection status and count of stored readings
- `GET /api/readings?limit=100` — recent sensor readings
- `GET /api/alerts?temperature=35` — readings at or above a temperature threshold

## Optional: simulate another device

PowerShell:
```powershell
$env:DEVICE_ID="simulated-device-02"
python simulator.py
```

Use a second terminal to run another simulator. Both devices publish to the same topic but have different device IDs.

## Troubleshooting

- **Docker command not found:** Install and start Docker Desktop, then retry `docker compose up -d`.
- **MQTT unavailable:** Confirm the Mosquitto container is running with `docker compose ps`.
- **PostgreSQL unavailable:** Check `docker compose logs postgres` and confirm port 5432 is not already in use.
- **No readings:** Start `simulator.py` in a second terminal and watch the Flask terminal for messages.
- **Port conflict:** Change the host-side port in `docker-compose.yml` and update the local connection settings as needed.

## Security note

This project is configured for local development only: MQTT allows anonymous connections and the PostgreSQL credentials are intentionally simple. Before deploying publicly, configure MQTT authentication/TLS, strong database credentials, environment variables, and appropriate network restrictions.

## Suggested GitHub description

A real-time IoT monitoring dashboard using simulated temperature and humidity data, MQTT, Flask, PostgreSQL, and Chart.js.
