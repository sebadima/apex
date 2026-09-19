import json
import open3d as o3d
import zmq

# 1. Caricamento tracciato
with open("track_definition.json", "r") as f:
    track = json.load(f)

wp_x = [wp["x_m"] for wp in track["waypoints"]]
wp_y = [wp["y_m"] for wp in track["waypoints"]]
points = [[x, y, 0.0] for x, y in zip(wp_x, wp_y)]

# 2. Setup ZeroMQ Subscriber non-bloccante
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("ipc:///tmp/apex_telemetry.ipc")
socket.setsockopt_string(zmq.SUBSCRIBE, "")

# 3. Setup Open3D Visualizer
vis = o3d.visualization.Visualizer()
vis.create_window(window_name="APEX 3D Telemetry", width=1024, height=768)

# Creazione geometria del tracciato (Linee)
lines = [[i, i + 1] for i in range(len(points) - 1)]
line_set = o3d.geometry.LineSet(
    points=o3d.utility.Vector3dVector(points),
    lines=o3d.utility.Vector2iVector(lines)
)
line_set.paint_uniform_color([1.0, 0.0, 0.0])
vis.add_geometry(line_set)

# Creazione mesh del mezzo (Dimensioni reali in metri: 0.4m x 0.2m x 0.1m)
vehicle = o3d.geometry.TriangleMesh.create_box(width=0.4, height=0.2, depth=0.1)
vehicle.paint_uniform_color([0.0, 1.0, 0.0])
# Sposta il pivot al centro geometrico del box
vehicle.translate([-0.2, -0.1, 0.0])
vis.add_geometry(vehicle)

# Adatta la visuale sull'intera geometria della pista
vis.reset_view_point(True)

print("Visualizzatore 3D Open3D attivo [In ascolto su IPC...]")

last_x = 0.0
last_y = 0.0

try:
    while True:
        if not vis.poll_events():
            break
        vis.update_renderer()

        try:
            raw_msg = socket.recv_string(flags=zmq.NOBLOCK)
        except zmq.Again:
            continue

        parts = raw_msg.split(",")
        if len(parts) >= 6:
            x_pos = float(parts[4])
            y_pos = float(parts[5])

            # Traslazione assoluta basata sullo spostamento dal punto precedente
            dx = x_pos - last_x
            dy = y_pos - last_y
            
            vehicle.translate([dx, dy, 0.0])
            vis.update_geometry(vehicle)

            last_x = x_pos
            last_y = y_pos

except KeyboardInterrupt:
    print("\nVisualizzatore 3D chiuso.")
finally:
    vis.destroy_window()