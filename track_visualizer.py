import json
import matplotlib.pyplot as plt
import zmq

# 1. Caricamento mappa per disegnare il tracciato di sfondo
with open("track_definition.json", "r") as f:
    track = json.load(f)

wp_x = [wp["x_m"] for wp in track["waypoints"]]
wp_y = [wp["y_m"] for wp in track["waypoints"]]

# 2. Setup ZeroMQ Subscriber
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("ipc:///tmp/apex_telemetry.ipc")
socket.setsockopt_string(zmq.SUBSCRIBE, "")

# 3. Setup Grafico Matplotlib
plt.ion()
fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(wp_x, wp_y, "r--", label="Tracciato Master", alpha=0.6)
ax.scatter(wp_x, wp_y, c="blue", marker="o", label="Waypoints")
(vehicle_dot,) = ax.plot([], [], "go", markersize=12, label="Mezzo APEX")

ax.set_title(f"Monitoraggio Posizione: {track['track_name']}")
ax.set_xlabel("X (metri)")
ax.set_ylabel("Y (metri)")
ax.grid(True)
ax.legend()

print("Visualizzatore Percorso attivo [In ascolto su IPC...]")

try:
    while True:
        raw_msg = socket.recv_string()
        parts = raw_msg.split(",")

        # Formato payload: timestamp, vehicle_id, voltage, current, pos_x, pos_y
        if len(parts) >= 6:
            v_bat = float(parts[2])
            x_pos = float(parts[4])
            y_pos = float(parts[5])

            # Aggiorna la posizione del pallino sulla mappa
            vehicle_dot.set_data([x_pos], [y_pos])

            # Se la tensione scende sotto la soglia di warning, cambia colore in arancione/rosso
            if v_bat <= 6.6:
                vehicle_dot.set_color("red")
            elif v_bat <= 7.0:
                vehicle_dot.set_color("orange")
            else:
                vehicle_dot.set_color("green")

            fig.canvas.draw()
            fig.canvas.flush_events()

except KeyboardInterrupt:
    print("\nVisualizzatore chiuso.")
