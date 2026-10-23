const temperatureEl = document.getElementById("temperature");
const humidityEl = document.getElementById("humidity");
const deviceEl = document.getElementById("device");
const lastUpdatedEl = document.getElementById("lastUpdated");
const totalReadingsEl = document.getElementById("totalReadings");
const mqttStatusEl = document.getElementById("mqttStatus");
const mqttDot = document.getElementById("mqttDot");
const dbStatusEl = document.getElementById("dbStatus");
const readingsTable = document.getElementById("readingsTable");

const chartContext = document.getElementById("sensorChart").getContext("2d");
const sensorChart = new Chart(chartContext, {
  type: "line",
  data: {
    labels: [],
    datasets: [
      {
        label: "Temperature (°C)",
        data: [],
        borderColor: "#a78bfa",
        backgroundColor: "rgba(167,139,250,.12)",
        borderWidth: 2,
        tension: 0.3,
        fill: true,
        yAxisID: "y"
      },
      {
        label: "Humidity (%)",
        data: [],
        borderColor: "#38bdf8",
        backgroundColor: "rgba(56,189,248,.08)",
        borderWidth: 2,
        tension: 0.3,
        fill: false,
        yAxisID: "y1"
      }
    ]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: "index", intersect: false },
    plugins: {
      legend: { labels: { color: "#cbd5e1" } }
    },
    scales: {
      x: { ticks: { color: "#939bb0", maxTicksLimit: 8 }, grid: { color: "#252b3b" } },
      y: { position: "left", ticks: { color: "#a78bfa" }, grid: { color: "#252b3b" }, title: { display: true, text: "°C", color: "#a78bfa" } },
      y1: { position: "right", min: 0, max: 100, ticks: { color: "#38bdf8" }, grid: { drawOnChartArea: false }, title: { display: true, text: "%", color: "#38bdf8" } }
    }
  }
});

function formatTime(isoString) {
  return new Date(isoString).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

async function refreshDashboard() {
  try {
    const [readingsResponse, statusResponse] = await Promise.all([
      fetch("/api/readings?limit=60"),
      fetch("/api/status")
    ]);
    if (!readingsResponse.ok || !statusResponse.ok) throw new Error("API request failed");
    const readings = await readingsResponse.json();
    const status = await statusResponse.json();

    totalReadingsEl.textContent = status.total_readings;
    dbStatusEl.textContent = status.database_connected ? "PostgreSQL connected" : "PostgreSQL unavailable";
    mqttStatusEl.textContent = status.mqtt_connected ? "MQTT connected" : status.mqtt_message;
    mqttDot.className = `dot ${status.mqtt_connected ? "ok" : "bad"}`;

    if (!readings.length) {
      readingsTable.innerHTML = '<tr><td colspan="5">No readings yet. Start simulator.py in another terminal.</td></tr>';
      return;
    }

    const latest = readings[readings.length - 1];
    temperatureEl.textContent = Number(latest.temperature).toFixed(1);
    humidityEl.textContent = Number(latest.humidity).toFixed(1);
    deviceEl.textContent = latest.device_id;
    lastUpdatedEl.textContent = `Last reading: ${formatTime(latest.recorded_at)}`;

    sensorChart.data.labels = readings.map(item => formatTime(item.recorded_at));
    sensorChart.data.datasets[0].data = readings.map(item => Number(item.temperature));
    sensorChart.data.datasets[1].data = readings.map(item => Number(item.humidity));
    sensorChart.update("none");

    readingsTable.innerHTML = readings.slice().reverse().slice(0, 12).map(item => {
      const hot = Number(item.temperature) >= 35;
      return `<tr>
        <td>${formatTime(item.recorded_at)}</td>
        <td>${escapeHtml(item.device_id)}</td>
        <td>${Number(item.temperature).toFixed(1)} °C</td>
        <td>${Number(item.humidity).toFixed(1)}%</td>
        <td class="${hot ? "alert" : "normal"}">${hot ? "High temperature" : "Normal"}</td>
      </tr>`;
    }).join("");
  } catch (error) {
    mqttStatusEl.textContent = "Dashboard API unavailable";
    mqttDot.className = "dot bad";
    console.error(error);
  }
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[char]));
}

refreshDashboard();
setInterval(refreshDashboard, 3000);
