import json
import math

import open3d as o3d
import zmq


IPC_ADDRESS = "ipc:///tmp/apex_telemetry.ipc"


# ============================================================
# Caricamento tracciato
# ============================================================

with open("track_definition.json", "r") as f:
    track = json.load(f)

waypoints = track["waypoints"]

points = [
    [wp["x_m"], wp["y_m"], 0.0]
    for wp in waypoints
]


# ============================================================
# ZeroMQ SUB
# ============================================================

context = zmq.Context()

socket = context.socket(zmq.SUB)
socket.connect(IPC_ADDRESS)
socket.setsockopt_string(zmq.SUBSCRIBE, "")


# ============================================================
# Open3D
# ============================================================

vis = o3d.visualization.Visualizer()

vis.create_window(
    window_name="APEX 3D Telemetry",
    width=1280,
    height=800
)


# ============================================================
# Tracciato
# ============================================================

lines = [
    [i, i + 1]
    for i in range(len(points) - 1)
]

line_set = o3d.geometry.LineSet(
    points=o3d.utility.Vector3dVector(points),
    lines=o3d.utility.Vector2iVector(lines)
)

line_set.paint_uniform_color([0.75, 0.75, 0.75])

vis.add_geometry(line_set)


# ============================================================
# Waypoints
# ============================================================

waypoint_cloud = o3d.geometry.PointCloud()

waypoint_cloud.points = o3d.utility.Vector3dVector(
    points
)

waypoint_cloud.paint_uniform_color(
    [1.0, 0.5, 0.0]
)

vis.add_geometry(waypoint_cloud)


# ============================================================
# Robot
# ============================================================

# Corpo principale
body = o3d.geometry.TriangleMesh.create_box(
    width=0.40,
    height=0.20,
    depth=0.10
)

body.paint_uniform_color(
    [0.15, 0.65, 0.20]
)

# Il centro del robot deve coincidere con (0, 0, 0)
body.translate([
    -0.20,
    -0.10,
    0.05
])


# ------------------------------------------------------------
# Parte superiore / cabina
# ------------------------------------------------------------

cabin = o3d.geometry.TriangleMesh.create_box(
    width=0.20,
    height=0.14,
    depth=0.10
)

cabin.paint_uniform_color(
    [0.10, 0.30, 0.12]
)

cabin.translate([
    -0.10,
    -0.07,
    0.15
])


# ------------------------------------------------------------
# Indicatore anteriore
# ------------------------------------------------------------

nose = o3d.geometry.TriangleMesh.create_box(
    width=0.08,
    height=0.12,
    depth=0.06
)

nose.paint_uniform_color(
    [1.0, 0.25, 0.05]
)

nose.translate([
    0.20,
    -0.06,
    0.02
])


# ------------------------------------------------------------
# Uniamo i triangoli delle tre parti
# ------------------------------------------------------------

robot = body + cabin + nose

robot.compute_vertex_normals()

vis.add_geometry(robot)


# ============================================================
# Frame del robot
# ============================================================

robot_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
    size=0.35,
    origin=[0.0, 0.0, 0.0]
)

vis.add_geometry(robot_frame)


# ============================================================
# Traiettoria percorsa
# ============================================================

trajectory_points = []

trajectory_lines = []

trajectory = o3d.geometry.LineSet()

vis.add_geometry(trajectory)


# ============================================================
# Stato iniziale
# ============================================================

robot_initialized = False

current_x = 0.0
current_y = 0.0
current_yaw = 0.0


# ============================================================
# Funzione aggiornamento robot
# ============================================================

def update_robot(x, y, yaw):

    global current_x
    global current_y
    global current_yaw

    # --------------------------------------------------------
    # Trasformazione rispetto alla posizione precedente
    # --------------------------------------------------------

    dx = x - current_x
    dy = y - current_y

    dyaw = yaw - current_yaw

    # --------------------------------------------------------
    # Rotazione attorno al centro
    # --------------------------------------------------------

    if abs(dyaw) > 0.000001:

        rotation = robot.get_rotation_matrix_from_axis_angle(
            [0.0, 0.0, dyaw]
        )

        robot.rotate(
            rotation,
            center=[current_x, current_y, 0.05]
        )

    # --------------------------------------------------------
    # Traslazione
    # --------------------------------------------------------

    robot.translate([
        dx,
        dy,
        0.0
    ])

    # --------------------------------------------------------
    # Frame del robot
    # --------------------------------------------------------

    if abs(dyaw) > 0.000001:

        robot_frame.rotate(
            rotation,
            center=[
                current_x,
                current_y,
                0.0
            ]
        )

    robot_frame.translate([
        dx,
        dy,
        0.0
    ])

    # --------------------------------------------------------
    # Traiettoria
    # --------------------------------------------------------

    trajectory_points.append([
        x,
        y,
        0.012
    ])

    if len(trajectory_points) >= 2:

        i = len(trajectory_points) - 1

        trajectory_lines.append([
            i - 1,
            i
        ])

    trajectory.points = o3d.utility.Vector3dVector(
        trajectory_points
    )

    trajectory.lines = o3d.utility.Vector2iVector(
        trajectory_lines
    )

    trajectory.paint_uniform_color(
        [0.1, 0.8, 1.0]
    )

    # --------------------------------------------------------
    # Aggiornamento geometrie
    # --------------------------------------------------------

    vis.update_geometry(robot)
    vis.update_geometry(robot_frame)
    vis.update_geometry(trajectory)

    # --------------------------------------------------------
    # Stato
    # --------------------------------------------------------

    current_x = x
    current_y = y
    current_yaw = yaw


# ============================================================
# Visualizzazione iniziale
# ============================================================

vis.reset_view_point(True)

print(
    "Visualizzatore 3D Open3D attivo "
    "[In ascolto su IPC...]"
)


# ============================================================
# Loop
# ============================================================

try:

    while True:

        if not vis.poll_events():
            break

        # ----------------------------------------------------
        # Ricezione ZeroMQ
        # ----------------------------------------------------

        try:

            raw_msg = socket.recv_string(
                flags=zmq.NOBLOCK
            )

        except zmq.Again:

            vis.update_renderer()
            continue

        # ----------------------------------------------------
        # Parsing
        # ----------------------------------------------------

        parts = raw_msg.split(",")

        if len(parts) >= 7:

            try:

                x_pos = float(parts[4])
                y_pos = float(parts[5])
                yaw = float(parts[6])

            except ValueError:

                continue

            # ------------------------------------------------
            # Primo messaggio
            # ------------------------------------------------

            if not robot_initialized:

                # Spostiamo direttamente il robot
                # nella posizione iniziale.

                robot.translate([
                    x_pos,
                    y_pos,
                    0.0
                ])

                robot_frame.translate([
                    x_pos,
                    y_pos,
                    0.0
                ])

                current_x = x_pos
                current_y = y_pos
                current_yaw = yaw

                robot_initialized = True

                trajectory_points.append([
                    x_pos,
                    y_pos,
                    0.012
                ])

            else:

                update_robot(
                    x_pos,
                    y_pos,
                    yaw
                )

        vis.update_renderer()


except KeyboardInterrupt:

    print("\nVisualizzatore 3D chiuso.")


finally:

    socket.close()
    context.term()
    vis.destroy_window()
