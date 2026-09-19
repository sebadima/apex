import json
import math
import random
import time
import zmq

# 1. Caricamento tracciato per calcolo posizioni
with open("track_definition.json", "r") as f:
    track = json.load(f)

waypoints = track["waypoints"]
num_wp = len(waypoints)

# 2. Setup ZeroMQ Publisher
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("ipc:///tmp/apex_telemetry.ipc")

print("Apex Emulator attivo [50 Hz -> ipc:///tmp/apex_telemetry.ipc]")

base_voltage = 8.2
t = 0.0
wp_index = 0
progress = 0.0  # Avanzamento tra un waypoint e il successivo (0.0 -> 1.0)

try:
    while True:
        # Interpolazione posizione tra waypoint corrente e successivo
        p1 = waypoints[wp_index]
        p2 = waypoints[(wp_index + 1) % num_wp]

        x_pos = p1["x_m"] + (p2["x_m"] - p1["x_m"]) * progress
        y_pos = p1["y_m"] + (p2["y_m"] - p1["y_m"]) * progress

        progress += 0.01
        if progress >= 1.0:
            progress = 0.0
            wp_index = (wp_index + 1) % num_wp

        # Simulazione elettrica (tensione e corrente)
        current_a = round(abs(math.sin(t) * 2.8) + random.uniform(0.1, 0.5), 2)
        base_voltage -= 0.0002
        if base_voltage < 6.0:
            base_voltage = 8.2
        voltage_v = round(base_voltage - (current_a * 0.09), 2)

        ts = time.time_ns()

        # Formato 6 campi: ts, vehicle_id, voltage, current, pos_x, pos_y
        payload = f"{ts},APEX_01,{voltage_v},{current_a},{x_pos:.2f},{y_pos:.2f}"

        socket.send_string(payload)
        t += 0.05
        time.sleep(0.02)  # 50 Hz

except KeyboardInterrupt:
    print("\nEmulatore arrestato.")