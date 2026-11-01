cat << 'EOF' > server.py
import asyncio
import socket
import struct
import json
import websockets
import webbrowser
import threading
import time

FORZA_IP = "0.0.0.0"
FORZA_PORT = 9994
WS_IP = "0.0.0.0"
WS_PORT = 8765

connected_clients = set()

# Automated Mobile Browser Open Loop
def auto_launch_browser():
    time.sleep(1.5) # Let the network ports bind safely first
    print("\n[LAUNCHER] Automatically spinning up your visual interface web page...")
    webbrowser.open("file:///storage/emulated/0/forza-horizon-dashboard/index.html")

async def broadcast_telemetry():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((FORZA_IP, FORZA_PORT))
    sock.setblocking(False)
    
    loop = asyncio.get_running_loop()
    print(f"==================================================")
    print(f" FORZA TELEMETRY GATEWAY SERVER RUNNING           ")
    print(f"==================================================")
    print(f" Listening for Game UDP Stream on Port: {FORZA_PORT}")
    print(f" Broadcasting WebSockets on Port:       {WS_PORT}")
    print(f"==================================================")

    while True:
        try:
            data, _ = await loop.sock_recv(sock, 1024)
            if not connected_clients:
                await asyncio.sleep(0.01)
                continue

            rpm = struct.unpack_from('<f', data, 16)
            max_rpm = struct.unpack_from('<f', data, 8)
            idle_rpm = struct.unpack_from('<f', data, 12)
            speed_ms = struct.unpack_from('<f', data, 244)
            gear = struct.unpack_from('<B', data, 319)

            accel_x = struct.unpack_from('<f', data, 36)
            accel_z = struct.unpack_from('<f', data, 44)
            g_lat = accel_x / 9.80665
            g_long = accel_z / 9.80665

            speed_mph = int(speed_ms * 2.23694)
            gear_display = "R" if gear == 0 else str(gear)

            payload = json.dumps({
                "speed": speed_mph,
                "gear": gear_display,
                "rpm": int(rpm),
                "maxRpm": int(max_rpm),
                "idleRpm": int(idle_rpm),
                "gforce": { "lat": round(g_lat, 2), "long": round(g_long, 2) }
            })

            await asyncio.gather(*[client.send(payload) for client in connected_clients], return_exceptions=True)

        except Exception:
            await asyncio.sleep(0.001)

async def ws_handler(websocket):
    connected_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)

async def main():
    # Spin up browser trigger in an isolated thread so it doesn't block the network
    threading.Thread(target=auto_launch_browser, daemon=True).start()
    
    async with websockets.serve(ws_handler, WS_IP, WS_PORT):
        await broadcast_telemetry()

if __name__ == "__main__":
    asyncio.run(main())
EOF