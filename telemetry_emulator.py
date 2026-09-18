import math
import random
import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("ipc:///tmp/apex_telemetry.ipc")

print("Apex Emulator attivo [50 Hz -> ipc:///tmp/apex_telemetry.ipc]")

base_voltage = 8.2
t = 0.0

try:
    while True:
        # Simula variazioni di carico dinamiche
        current_a = round(abs(math.sin(t) * 2.8) + random.uniform(0.1, 0.5), 2)
        
        # Simula la caduta di tensione sotto carico e scarica progressiva
        base_voltage -= 0.0005
        voltage_v = round(base_voltage - (current_a * 0.09), 2)

        ts = time.time_ns()
        payload = f"{ts},BAT_MONITOR,{voltage_v},{current_a}"

        socket.send_string(payload)
        t += 0.05
        time.sleep(0.02)

except KeyboardInterrupt:
    print("\nEmulatore arrestato.")
