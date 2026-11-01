cat << 'EOF' > server.py
import asyncio
import socket
import struct
import json
import websockets

# INCOMING NETWORK TRANSLATION
# BIND_IP "0.0.0.0" instructs the phone to listen to ALL network channels
BIND_IP = "0.0.0.0"
FORZA_PORT = 9994
WS_PORT = 8765

connected_clients = set()

async def broadcast_telemetry():
    # Force socket allocation to listen to external network ports
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((BIND_IP, FORZA_PORT))
    sock.setblocking(False)
    
    loop = asyncio.get_running_loop()
    print(f"==================================================")
    print(f" FORZA MATCH NETWORK RECEIVER ACTIVE             ")
    print(f"==================================================")
    print(f" Listening for PS5 UDP packets on Port: {FORZA_PORT}")
    print(f" WebSockets server ready on Port:       {WS_PORT}")
    print(f"==================================================")

    while True:
        try:
            data, addr = await loop.sock_recv(sock, 1024)
            
            # Diagnostic flag: lets you see if a packet arrives from your console
            print(f"[PACKET RECEIVED] Catching data frames from: {addr[0]}", end="\r")
            
            if not connected_clients:
                continue

            # Core Variables Unpacking
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

            if connected_clients:
                await asyncio.gather(*[client.send(payload) for client in connected_clients], return_exceptions=True)

        except Exception as e:
            await asyncio.sleep(0.001)

async def ws_handler(websocket):
    connected_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)

async def main():
    async with websockets.serve(ws_handler, BIND_IP, WS_PORT):
        await broadcast_telemetry()

if __name__ == "__main__":
    asyncio.run(main())
EOF