import json
import math
import signal

import numpy as np
import open3d as o3d
import zmq


IPC_ADDRESS = "ipc:///tmp/apex_telemetry.ipc"


# ============================================================
# CONTROLLO INTERRUZIONE
# ============================================================

running = True


def handle_sigint(signum, frame):

    global running

    print(
        "\nCTRL+C ricevuto. "
        "Chiusura del visualizzatore..."
    )

    running = False


signal.signal(
    signal.SIGINT,
    handle_sigint
)


# ============================================================
# CARICAMENTO TRACCIATO
# ============================================================

with open("track_definition.json", "r") as f:
    track = json.load(f)

waypoints = track["waypoints"]

points = [
    [
        wp["x_m"],
        wp["y_m"],
        wp.get("z_m", 0.0)
    ]
    for wp in waypoints
]


# ============================================================
# ZERO MQ
# ============================================================

context = zmq.Context()

socket = context.socket(zmq.SUB)
socket.connect(IPC_ADDRESS)
socket.setsockopt_string(zmq.SUBSCRIBE, "")


# ============================================================
# OPEN3D
# ============================================================

vis = o3d.visualization.Visualizer()

vis.create_window(
    window_name="APEX 3D Telemetry",
    width=1280,
    height=800
)


# ============================================================
# TRACCIATO
# ============================================================

lines = [
    [i, i + 1]
    for i in range(len(points) - 1)
]

line_set = o3d.geometry.LineSet(
    points=o3d.utility.Vector3dVector(points),
    lines=o3d.utility.Vector2iVector(lines)
)

line_set.paint_uniform_color(
    [0.75, 0.75, 0.75]
)

vis.add_geometry(line_set)


# ============================================================
# WAYPOINT
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
# TERRENO
# ============================================================

min_x = min(p[0] for p in points)
max_x = max(p[0] for p in points)

min_y = min(p[1] for p in points)
max_y = max(p[1] for p in points)

margin = 8.0

ground_width = (max_x - min_x) + margin * 2
ground_depth = (max_y - min_y) + margin * 2

ground = o3d.geometry.TriangleMesh.create_box(
    width=ground_width,
    height=ground_depth,
    depth=0.05
)

ground.paint_uniform_color(
    [0.18, 0.22, 0.18]
)

ground.translate([
    min_x - margin,
    min_y - margin,
    -0.05
])

vis.add_geometry(ground)


# ============================================================
# PAESAGGIO
# ============================================================

def create_block(
    x,
    y,
    z,
    width,
    depth,
    height,
    color
):

    block = o3d.geometry.TriangleMesh.create_box(
        width=width,
        height=depth,
        depth=height
    )

    block.paint_uniform_color(color)

    block.translate([
        x - width / 2,
        y - depth / 2,
        z
    ])

    block.compute_vertex_normals()

    return block


landscape_objects = [

    create_block(
        min_x - 2.0,
        min_y + 4.0,
        0.0,
        2.0,
        2.0,
        1.5,
        [0.25, 0.30, 0.25]
    ),

    create_block(
        max_x + 2.0,
        min_y + 8.0,
        0.0,
        2.5,
        2.5,
        2.0,
        [0.30, 0.28, 0.20]
    ),

    create_block(
        min_x + 5.0,
        max_y + 3.0,
        0.0,
        3.0,
        2.0,
        1.0,
        [0.22, 0.28, 0.22]
    )
]

for obj in landscape_objects:
    vis.add_geometry(obj)


# ============================================================
# MACCHINA
# ============================================================

robot_parts = []


# ------------------------------------------------------------
# Corpo
# ------------------------------------------------------------

body = o3d.geometry.TriangleMesh.create_box(
    width=0.90,
    height=0.48,
    depth=0.18
)

body.paint_uniform_color(
    [0.12, 0.55, 0.18]
)

body.translate([
    -0.45,
    -0.24,
    0.20
])

body.compute_vertex_normals()

robot_parts.append(body)


# ------------------------------------------------------------
# Cabina
# ------------------------------------------------------------

cabin = o3d.geometry.TriangleMesh.create_box(
    width=0.45,
    height=0.38,
    depth=0.28
)

cabin.paint_uniform_color(
    [0.08, 0.16, 0.10]
)

cabin.translate([
    -0.20,
    -0.19,
    0.38
])

cabin.compute_vertex_normals()

robot_parts.append(cabin)


# ------------------------------------------------------------
# Cofano
# ------------------------------------------------------------

hood = o3d.geometry.TriangleMesh.create_box(
    width=0.30,
    height=0.44,
    depth=0.12
)

hood.paint_uniform_color(
    [0.16, 0.62, 0.20]
)

hood.translate([
    0.20,
    -0.22,
    0.29
])

hood.compute_vertex_normals()

robot_parts.append(hood)


# ------------------------------------------------------------
# Paraurti
# ------------------------------------------------------------

bumper = o3d.geometry.TriangleMesh.create_box(
    width=0.08,
    height=0.50,
    depth=0.12
)

bumper.paint_uniform_color(
    [0.05, 0.05, 0.05]
)

bumper.translate([
    0.45,
    -0.25,
    0.17
])

bumper.compute_vertex_normals()

robot_parts.append(bumper)


# ============================================================
# RUOTE
# ============================================================

def create_wheel(x, y, z):

    wheel = o3d.geometry.TriangleMesh.create_cylinder(
        radius=0.13,
        height=0.08,
        resolution=20
    )

    wheel.paint_uniform_color(
        [0.03, 0.03, 0.03]
    )

    rotation = wheel.get_rotation_matrix_from_xyz(
        [math.pi / 2, 0.0, 0.0]
    )

    wheel.rotate(
        rotation,
        center=[0.0, 0.0, 0.0]
    )

    wheel.translate([
        x,
        y,
        z
    ])

    wheel.compute_vertex_normals()

    return wheel


wheel_positions = [
    [0.28,  0.29, 0.15],
    [0.28, -0.29, 0.15],
    [-0.30,  0.29, 0.15],
    [-0.30, -0.29, 0.15]
]

for pos in wheel_positions:

    wheel = create_wheel(
        pos[0],
        pos[1],
        pos[2]
    )

    robot_parts.append(wheel)


# ============================================================
# MODELLO COMPLETO
# ============================================================

robot = robot_parts[0]

for part in robot_parts[1:]:
    robot += part

robot.compute_vertex_normals()

vis.add_geometry(robot)


# ============================================================
# FRAME
# ============================================================

robot_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
    size=0.45,
    origin=[0.0, 0.0, 0.0]
)

vis.add_geometry(robot_frame)


# ============================================================
# TRAIETTORIA
# ============================================================

trajectory_points = []
trajectory_lines = []

trajectory = o3d.geometry.LineSet()

trajectory.paint_uniform_color(
    [0.1, 0.8, 1.0]
)

vis.add_geometry(trajectory)


# ============================================================
# STATO ROBOT
# ============================================================

robot_initialized = False

current_x = 0.0
current_y = 0.0
current_z = 0.0
current_yaw = 0.0


# ============================================================
# CAMERA
# ============================================================

camera_parameters = None


# ============================================================
# CAMERA FOLLOW
# ============================================================

def update_camera():

    global camera_parameters

    ctr = vis.get_view_control()

    # --------------------------------------------------------
    # PARAMETRI CAMERA
    #
    # La macchina guarda lungo il proprio asse +X.
    # --------------------------------------------------------

    forward = np.array([
        math.cos(current_yaw),
        math.sin(current_yaw),
        0.0
    ], dtype=float)

    world_up = np.array([
        0.0,
        0.0,
        1.0
    ], dtype=float)

    # --------------------------------------------------------
    # POSIZIONE CAMERA
    #
    # 2.2 m dietro
    # 0.9 m sopra
    # --------------------------------------------------------

    eye = np.array([
        current_x,
        current_y,
        current_z
    ], dtype=float)

    eye = (
        eye
        - forward * 2.2
        + world_up * 0.9
    )

    # --------------------------------------------------------
    # PUNTO OSSERVATO
    #
    # 1.0 m davanti alla macchina,
    # all'altezza del corpo.
    # --------------------------------------------------------

    target = np.array([
        current_x,
        current_y,
        current_z + 0.30
    ], dtype=float)

    target = target + forward * 1.0

    # --------------------------------------------------------
    # DIREZIONE DI VISTA
    # --------------------------------------------------------

    camera_forward = target - eye

    forward_length = np.linalg.norm(
        camera_forward
    )

    if forward_length < 1e-9:
        return

    camera_forward /= forward_length

    # --------------------------------------------------------
    # ASSE X CAMERA = DESTRA
    # --------------------------------------------------------

    camera_right = np.cross(
        camera_forward,
        world_up
    )

    right_length = np.linalg.norm(
        camera_right
    )

    if right_length < 1e-9:
        return

    camera_right /= right_length

    # --------------------------------------------------------
    # ASSE Y CAMERA = BASSO
    #
    # Convenzione pinhole:
    #
    # X = destra
    # Y = basso
    # Z = avanti
    #
    # Con:
    #
    # forward = +X mondo
    # world_up = +Z mondo
    #
    # il verso corretto di DOWN è:
    #
    # forward × right
    # --------------------------------------------------------

    camera_down = np.cross(
        camera_forward,
        camera_right
    )

    down_length = np.linalg.norm(
        camera_down
    )

    if down_length < 1e-9:
        return

    camera_down /= down_length

    # --------------------------------------------------------
    # MATRICE ROTAZIONE WORLD -> CAMERA
    # --------------------------------------------------------

    rotation = np.array([
        camera_right,
        camera_down,
        camera_forward
    ])

    # --------------------------------------------------------
    # EXTRINSIC
    #
    # X_camera = R * X_world + t
    #
    # t = -R * camera_position
    # --------------------------------------------------------

    extrinsic = np.eye(4)

    extrinsic[:3, :3] = rotation

    extrinsic[:3, 3] = -rotation @ eye

    # --------------------------------------------------------
    # INTRINSECI OPEN3D
    # --------------------------------------------------------

    if camera_parameters is None:

        camera_parameters = (
            ctr.convert_to_pinhole_camera_parameters()
        )

    camera_parameters.extrinsic = extrinsic

    # --------------------------------------------------------
    # APPLICA LA CAMERA
    # --------------------------------------------------------

    ctr.convert_from_pinhole_camera_parameters(
        camera_parameters,
        allow_arbitrary=True
    )


# ============================================================
# AGGIORNAMENTO ROBOT
# ============================================================

def update_robot(
    x,
    y,
    z,
    yaw
):

    global current_x
    global current_y
    global current_z
    global current_yaw

    dx = x - current_x
    dy = y - current_y
    dz = z - current_z

    dyaw = yaw - current_yaw

    while dyaw > math.pi:
        dyaw -= 2.0 * math.pi

    while dyaw < -math.pi:
        dyaw += 2.0 * math.pi


    # --------------------------------------------------------
    # ROTAZIONE
    # --------------------------------------------------------

    if abs(dyaw) > 0.000001:

        rotation = robot.get_rotation_matrix_from_axis_angle(
            [0.0, 0.0, dyaw]
        )

        robot.rotate(
            rotation,
            center=[
                current_x,
                current_y,
                current_z
            ]
        )

        robot_frame.rotate(
            rotation,
            center=[
                current_x,
                current_y,
                current_z
            ]
        )


    # --------------------------------------------------------
    # TRASLAZIONE 3D
    # --------------------------------------------------------

    robot.translate([
        dx,
        dy,
        dz
    ])

    robot_frame.translate([
        dx,
        dy,
        dz
    ])


    # --------------------------------------------------------
    # TRAIETTORIA
    # --------------------------------------------------------

    trajectory_points.append([
        x,
        y,
        z + 0.02
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
    # OPEN3D
    # --------------------------------------------------------

    vis.update_geometry(robot)
    vis.update_geometry(robot_frame)
    vis.update_geometry(trajectory)


    # --------------------------------------------------------
    # STATO
    # --------------------------------------------------------

    current_x = x
    current_y = y
    current_z = z
    current_yaw = yaw


    # --------------------------------------------------------
    # CAMERA
    # --------------------------------------------------------

    update_camera()


# ============================================================
# AVVIO
# ============================================================

print(
    "Visualizzatore 3D Open3D attivo "
    "[In ascolto su IPC...]"
)


# ============================================================
# LOOP
# ============================================================

try:

    while running:

        if not vis.poll_events():
            break

        try:

            raw_msg = socket.recv_string(
                flags=zmq.NOBLOCK
            )

        except zmq.Again:

            vis.update_renderer()
            continue


        parts = raw_msg.split(",")

        if len(parts) >= 8:

            try:

                x_pos = float(parts[4])
                y_pos = float(parts[5])
                z_pos = float(parts[6])
                yaw = float(parts[7])

            except ValueError:

                continue


            # ------------------------------------------------
            # PRIMO MESSAGGIO
            # ------------------------------------------------

            if not robot_initialized:

                robot.translate([
                    x_pos,
                    y_pos,
                    z_pos
                ])

                robot_frame.translate([
                    x_pos,
                    y_pos,
                    z_pos
                ])

                current_x = x_pos
                current_y = y_pos
                current_z = z_pos
                current_yaw = yaw

                robot_initialized = True

                trajectory_points.append([
                    x_pos,
                    y_pos,
                    z_pos + 0.02
                ])

                update_camera()


            else:

                update_robot(
                    x_pos,
                    y_pos,
                    z_pos,
                    yaw
                )


        vis.update_renderer()


except KeyboardInterrupt:

    print(
        "\nVisualizzatore 3D chiuso."
    )


finally:

    socket.close()
    context.term()
    vis.destroy_window()
