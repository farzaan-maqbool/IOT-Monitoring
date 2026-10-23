# 🌐 Real-Time IoT Monitoring Dashboard

A real-time IoT monitoring system built with **Python, Flask, PostgreSQL, MQTT, and Docker**. The application simulates IoT sensor devices, collects temperature and humidity readings, stores telemetry in a PostgreSQL database, and visualizes the data through a web dashboard.

The project uses simulated sensor data, so **no physical Arduino or IoT hardware is required**.

## 🚀 Features

* **Real-Time Monitoring:** Displays temperature and humidity readings from simulated IoT devices.
* **MQTT Communication:** Uses the Mosquitto MQTT broker to publish and receive sensor telemetry.
* **PostgreSQL Database:** Stores sensor readings for historical tracking and analysis.
* **Interactive Dashboard:** Visualizes temperature and humidity history using charts.
* **Device Identification:** Associates sensor readings with individual simulated devices.
* **Temperature Alerts:** Highlights readings that meet or exceed a configurable temperature threshold.
* **REST API:** Provides endpoints to inspect system status, retrieve sensor readings, and query temperature alerts.
* **Docker Integration:** Runs PostgreSQL and the MQTT broker in containers.
* **Multi-Device Simulation:** Supports running multiple simulated devices.

## 🛠️ Tech Stack

| Technology        | Purpose                                          |
| ----------------- | ------------------------------------------------ |
| Python            | Application logic and sensor simulation          |
| Flask             | Web application and API                          |
| PostgreSQL        | Persistent storage for sensor readings           |
| MQTT              | Lightweight messaging protocol for IoT telemetry |
| Eclipse Mosquitto | MQTT message broker                              |
| Docker Compose    | Container management                             |
| HTML5             | Dashboard structure                              |
| CSS3              | Dashboard styling                                |
| JavaScript        | Dynamic dashboard interactions                   |
| Chart.js          | Temperature and humidity visualization           |
| Paho-MQTT         | MQTT communication in Python                     |
| psycopg2          | PostgreSQL connectivity                          |

## 🏗️ System Architecture

```text
+---------------------------+
|   Simulated IoT Sensors   |
| Temperature and Humidity  |
+-------------+-------------+
              |
              | MQTT Publish
              v
+---------------------------+
|   Mosquitto MQTT Broker   |
|         Docker            |
+-------------+-------------+
              |
              | MQTT Subscribe
              v
+---------------------------+
|     Flask Application     |
| Python Backend and API    |
+-------------+-------------+
              |
              | Store Readings
              v
+---------------------------+
|    PostgreSQL Database    |
|         Docker            |
+-------------+-------------+
              |
              v
+---------------------------+
|      Web Dashboard        |
| Charts, Metrics, Alerts   |
+---------------------------+
```

## 📋 Prerequisites

Install the following software before running the project:

* [Python 3.10 or later](https://www.python.org/downloads/)
* [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* [Visual Studio Code](https://code.visualstudio.com/) (recommended)
* A modern web browser

No physical sensors or Arduino board are required.

## 📁 Project Structure

```text
IOT-Monitoring/
│
├── app.py                 # Flask application and backend
├── simulator.py           # Simulated IoT sensor publisher
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # PostgreSQL and MQTT services
├── mosquitto.conf         # Mosquitto broker configuration
├── .env.example           # Example environment configuration
├── .gitignore             # Files excluded from Git
├── README.md              # Project documentation
│
├── static/
│   ├── app.js             # Dashboard JavaScript
│   └── style.css          # Dashboard styling
│
└── templates/
    └── index.html         # Dashboard interface
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/farzaan-maqbool/IOT-Monitoring.git
```

Navigate into the project directory:

```bash
cd IOT-Monitoring
```

### 2. Start PostgreSQL and Mosquitto

Make sure Docker Desktop is running.

Run:

```bash
docker compose up -d
```

This starts the PostgreSQL database and Mosquitto MQTT broker configured in `docker-compose.yml`.

Verify the containers:

```bash
docker compose ps
```

### 3. Create a Python virtual environment

On Windows PowerShell:

```powershell
py -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use the virtual environment's Python executable directly instead.

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure environment variables

If the application requires a `.env` file, create one using `.env.example` as a template.

For example:

```powershell
Copy-Item .env.example .env
```

Review the environment variables and ensure the database name, username, password, host, and MQTT settings match your Docker Compose configuration.

**Security:** Never commit `.env` or real passwords to GitHub. Use strong credentials for any deployment beyond local development.

### 6. Start the Flask dashboard

In the first terminal, run:

```bash
python app.py
```

Once Flask starts, open:

**http://127.0.0.1:5000**

Keep this terminal running.

### 7. Start the sensor simulator

Open a second terminal in the project directory.

Activate the virtual environment if necessary:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run the simulator:

```bash
python simulator.py
```

The simulator publishes temperature and humidity readings to the MQTT topic:

```text
iot/sensor/data
```

The Flask application receives the readings and stores them in PostgreSQL.

The dashboard should begin displaying sensor telemetry when the services are configured correctly.

## 📊 Dashboard

The dashboard provides an overview of the latest sensor data, including:

* Latest temperature in degrees Celsius.
* Latest relative humidity percentage.
* Reporting device identifier.
* Number of stored readings.
* Temperature and humidity history chart.
* MQTT and PostgreSQL connection status.
* Temperature threshold information.

## 🔌 API Endpoints

The application provides the following endpoints:

| Method | Endpoint                     | Description                                                        |
| ------ | ---------------------------- | ------------------------------------------------------------------ |
| GET    | `/api/status`                | Returns MQTT/PostgreSQL connection status and stored reading count |
| GET    | `/api/readings?limit=100`    | Retrieves recent sensor readings                                   |
| GET    | `/api/alerts?temperature=35` | Retrieves readings at or above the specified temperature threshold |

Example requests:

```text
http://127.0.0.1:5000/api/status
```

```text
http://127.0.0.1:5000/api/readings?limit=100
```

```text
http://127.0.0.1:5000/api/alerts?temperature=35
```

These endpoints are intended for local development and testing.

## 🧪 Simulating Multiple Devices

You can simulate a second device by opening another terminal and setting a different device ID.

In PowerShell:

```powershell
$env:DEVICE_ID="simulated-device-02"
python simulator.py
```

The second simulator publishes to the same MQTT topic with a different device identifier.

Check the simulator output and dashboard to verify that the device is reporting data.

## 🐳 Docker Commands

Start the services:

```bash
docker compose up -d
```

View running services:

```bash
docker compose ps
```

View PostgreSQL logs:

```bash
docker compose logs postgres
```

View Mosquitto logs:

```bash
docker compose logs mosquitto
```

Stop the containers:

```bash
docker compose down
```

The exact service names depend on the `docker-compose.yml` configuration.

## 🛠️ Troubleshooting

### Docker command not found

Start Docker Desktop and wait until the engine is running. Then retry:

```bash
docker --version
```

### MQTT connection failure

Check that the Mosquitto container is running:

```bash
docker compose ps
```

Inspect its logs:

```bash
docker compose logs mosquitto
```

Confirm that the application and simulator use the correct MQTT host and port.

### PostgreSQL connection failure

Check the database logs:

```bash
docker compose logs postgres
```

Verify the database name, username, password, port, and host in the application's configuration.

### No sensor readings appear

1. Confirm Docker services are running.
2. Keep `python app.py` running.
3. Start `python simulator.py` in a second terminal.
4. Confirm the MQTT topic is `iot/sensor/data`.
5. Inspect both terminal outputs for connection errors.

### Port conflicts

If ports `5432`, `1883`, or `5000` are already in use, resolve the conflict or update the appropriate port configuration and connection settings.

## 🔐 Security Notes

This project is intended for local learning and development.

* Do not expose the development Flask server publicly.
* Do not commit passwords, API keys, or `.env` files.
* Configure MQTT authentication and TLS before exposing a broker to an untrusted network.
* Use strong PostgreSQL credentials outside local development.
* Restrict database and broker access using appropriate network controls.

## 🎯 Learning Outcomes

This project demonstrates practical experience with:

* IoT messaging using MQTT.
* Python backend development with Flask.
* PostgreSQL database integration.
* Real-time telemetry processing.
* Data visualization using JavaScript charts.
* Docker-based local development.
* REST API design and testing.
* Simulated sensor systems and multi-device communication.

## 🔮 Future Improvements

Potential extensions include:

* Connecting real ESP32 or Arduino sensors.
* Adding user authentication and role-based access control.
* Implementing WebSocket-based dashboard updates.
* Adding configurable alert notifications.
* Supporting more sensor types.
* Deploying the application to a cloud platform.
* Adding automated tests and CI/CD workflows.

## 👨‍💻 Author

**Farzaan Maqbool**

Computer Science and Engineering Student

GitHub: [farzaan-maqbool](https://github.com/farzaan-maqbool)

---

*Built as a hands-on project to explore IoT communication, backend development, database integration, and containerization.*
