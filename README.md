
# 🏎️ Forza Horizon 5 - Telemetry Dashboard Cluster

An ultra-low latency, web-based digital dashboard for **Forza Horizon 5**. Built using Python WebSockets to process game engine data frames at high speeds and project real-time metrics onto local networks.

## 🛠️ Key Core Modules
* **Live HUD Speedometer:** Responsive metrics mapped to current vehicle transmission states.
* **Bi-Axial G-Force Tracker:** Vector mapping calculation engine displaying real-time cornering, acceleration, and deceleration forces.
* **Client-Side Stopwatch Splitter:** Automatically launches tracking registers the moment the vehicle clears a dead standstill (2 MPH). 

## 🚀 Execution Instructions

### 1. Initialize Python Backend Service
Open your terminal inside the directory folder and prepare the dependencies:
```bash
pip install -r requirements.txt
python server.py
```

### 2. Configure Game Settings
1. Boot into **Forza Horizon 5** -> **Settings** -> **HUD and Gameplay**.
2. Scroll down to the bottom fields and update the following settings:
   * **Data Out:** `On`
   * **Data Out IP Address:** `127.0.0.1` (Use your PC's local IP network identifier if loading the dashboard page onto an iPad or Phone)
   * **Data Out IP Port:** `9994`

### 3. Open the Dashboard Page
Simply double-click the `index.html` file to launch it in any modern web browser.