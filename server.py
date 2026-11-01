import asyncio
import socket
import json
import websockets
import http.server
import socketserver
import threading
from forza_packet import ForzaTelemetryPacket  # Importing your brand new parsing model file!

BIND_IP = "0.0.0.0"
FORZA_PORT = 9994
WS_PORT = 8765
HTTP_PORT = 8000

connected_clients = set()

# Host your index.html interface file on port 8000
def launch_web_server():
    class QuietHTTPHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args): return

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((BIND_IP, HTTP_PORT), QuietHTTPHandler) as httpd:
        print(f" Interface serving live on:            http://localhost:{HTTP_PORT}")
        httpd.serve_forever()

async def broadcast_telemetry():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((BIND_IP, FORZA_PORT))
    sock.setblocking(False)
    
    loop = asyncio.get_running_loop()
    print("==================================================")
    print(" DYNAMIC TELEMETRY ENGINE MODULE GENERATION ACTIVE")
    print("==================================================")
    print(f" Intercepting incoming packet streams on Port: {FORZA_PORT}")

    while True:
        try:
            raw_bytes, addr = await loop.sock_recv(sock, 1024)
            
            # Pass the raw network buffer data right into your parsing model
            packet = ForzaTelemetryPacket(raw_bytes)
            
            # Diagnostic tracking flag visible inside Termux
            print(f"[PACKET PARSED] Speed: {packet.speed_mph} MPH | Gear: {packet.gear_display} | RPM: {int(packet.current_engine_rpm)}", end="\r")

            if not connected_clients:
                await asyncio.sleep(0.01)
                continue

            # Convert the model state into a clean dictionary map and compile to JSON string
            payload = json.dumps(packet.to_dict())

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
    threading.Thread(target=launch_web_server, daemon=True).start()
    async with websockets.serve(ws_handler, BIND_IP, WS_PORT):
        await broadcast_telemetry()

if __name__ == "__main__":
    asyncio.run(main())