# 🏎️ Forza Horizon 5 - Telemetry Dashboard Cluster

An ultra-low latency, web-based digital dashboard for **Forza Horizon 5**. This project acts as an asynchronous Python gateway that captures live UDP binary telemetry frames sent by the game engine and broadcasts them over WebSockets to a web-based dashboard on your local network.

## 🛠️ Key Core Modules
* **Live HUD Speedometer:** Real-time speed (MPH) and current transmission gear selectors.
* **Bi-Axial G-Force Tracker:** Vector mapping calculation engine displaying real-time cornering, acceleration, and deceleration vectors.
* **Client-Side Stopwatch Splitter:** Automatically launches tracking registers the moment the vehicle clears a dead standstill (2 MPH). Use the **Spacebar** to log and split sector laps manually.
* **Session Peak Memory:** Automatically tracks and retains your all-time records across a driving session, saving your **Top Speed**, **Max Lateral G-Force**, and **Highest Tire Temperature**.

---

## 🚀 Execution Instructions (Mobile Setup)

You can run your Python dashboard server directly on your mobile device (while playing the game on a console or PC) using terminal environments like **Termux** (Android) or **a-Shell / Pyto** (iOS).

### 1. Initialize the Environment
Open your mobile terminal emulator app and execute the setup environment stack:

```bash
# Update packages and pull tools (For Android/Termux)
pkg update && pkg install python git -y

# Clone your dashboard repository
git clone https://github.com
cd forza-horizon-dashboard

# Install required high-speed websocket dependencies
pip install -r requirements.txt

# Start your gateway telemetry server engine
python server.py
```

### 2. Configure Forza Horizon 5 Game Settings
1. Boot up the game on your Xbox console or PC and open **Settings** -> **HUD and Gameplay**.
2. Scroll to the very bottom to locate the telemetry server fields:
   * **Data Out:** `On`
   * **Data Out IP Address:** Enter your phone's current **Local Wi-Fi IP Address** (e.g., `192.168.1.XX`).
   * **Data Out IP Port:** `9994`

### 3. Open the Interface
Simply locate and open the `index.html` file using your mobile device's internal file explorer, or pull up your local loopback browser tab. The moment you press the accelerator in-game, the telemetry dials will light up instantly.