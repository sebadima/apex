import json
import sys
import time
import math
import zmq

from brown_noise import BrownNoiseGenerator


def run_simulation(seed: int, publish_ipc: bool = False) -> tuple[float, float]:
    with open("track_definition.json", "r") as f:
        track = json.load(f)

    socket = None

    if publish_ipc:
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        socket.bind("ipc:///tmp/apex_telemetry.ipc")

        # Lascia tempo al subscriber Open3D di collegarsi
        time.sleep(0.5)

    noise = BrownNoiseGenerator(seed=seed, amplitude=0.1)

    # Parametri robot
    v_bat_oc = 8.2
    r_bat_int = 0.08
    m_kg = 1.5
    speed_m_s = 2.0
    dt = 0.02

    used_mah = 0.0
    used_wh = 0.0

    waypoints = track["waypoints"]
    num_wp = len(waypoints)

    # Posizione iniziale 3D
    x_curr = waypoints[0]["x_m"]
    y_curr = waypoints[0]["y_m"]
    z_curr = waypoints[0].get("z_m", 0.0)

    yaw_curr = 0.0

    while True:

        for i in range(1, num_wp):

            wp_target = waypoints[i]

            x_target = wp_target["x_m"]
            y_target = wp_target["y_m"]
            z_target = wp_target.get("z_m", 0.0)

            # Differenza di posizione nello spazio 3D
            dx = x_target - x_curr
            dy = y_target - y_curr
            dz = z_target - z_curr

            dist = math.sqrt(
                dx * dx +
                dy * dy +
                dz * dz
            )

            if dist == 0:
                continue

            # Direzione 3D normalizzata
            dir_x = dx / dist
            dir_y = dy / dist
            dir_z = dz / dist

            # Orientamento sul piano XY
            yaw_curr = math.atan2(
                dir_y,
                dir_x
            )

            r_m = wp_target.get("radius_m", None)

            steps = int(
                dist /
                (speed_m_s * dt)
            )

            for _ in range(steps):

                # -------------------------------------------------
                # MODELLO CINEMATICO 3D
                # -------------------------------------------------

                x_curr += (
                    dir_x *
                    speed_m_s *
                    dt
                )

                y_curr += (
                    dir_y *
                    speed_m_s *
                    dt
                )

                z_curr += (
                    dir_z *
                    speed_m_s *
                    dt
                )

                # -------------------------------------------------
                # MODELLO DI DISTURBO / ATTRITO
                # -------------------------------------------------

                b_noise = (
                    noise.get_sample() *
                    wp_target["noise_amplitude"]
                )

                f_friction = (
                    wp_target["friction_base"] +
                    b_noise
                )

                # -------------------------------------------------
                # EFFETTO CURVA
                # -------------------------------------------------

                f_corner = 0.0

                if r_m and r_m > 0:

                    f_centripetal = (
                        m_kg *
                        (speed_m_s ** 2)
                    ) / r_m

                    f_corner = (
                        (0.5 / r_m) +
                        (f_centripetal * 0.05)
                    )

                # -------------------------------------------------
                # OSTACOLO CASUALE
                # -------------------------------------------------

                is_stuck = noise.check_obstacle_event(0.01)

                f_obstacle = (
                    2.0
                    if is_stuck
                    else 0.0
                )

                # -------------------------------------------------
                # FORZA TOTALE
                # -------------------------------------------------

                f_total = max(
                    0.05,
                    f_friction +
                    f_corner +
                    f_obstacle
                )

                # -------------------------------------------------
                # CORRENTE
                # -------------------------------------------------

                current_a = max(
                    0.2,
                    f_total * 7.5
                )

                # -------------------------------------------------
                # TENSIONE BATTERIA
                # -------------------------------------------------

                voltage_v = max(
                    5.0,
                    v_bat_oc -
                    (
                        current_a *
                        r_bat_int
                    )
                )

                # -------------------------------------------------
                # CONSUMO
                # -------------------------------------------------

                used_mah += (
                    current_a *
                    dt *
                    (1000.0 / 3600.0)
                )

                used_wh += (
                    voltage_v *
                    current_a *
                    (dt / 3600.0)
                )

                # -------------------------------------------------
                # TELEMETRIA ZERO MQ
                #
                # timestamp,
                # robot_id,
                # voltage,
                # current,
                # x,
                # y,
                # z,
                # yaw
                # -------------------------------------------------

                if socket:

                    ts = time.time_ns()

                    payload = (
                        f"{ts},"
                        f"APEX_01,"
                        f"{voltage_v:.2f},"
                        f"{current_a:.2f},"
                        f"{x_curr:.2f},"
                        f"{y_curr:.2f},"
                        f"{z_curr:.2f},"
                        f"{yaw_curr:.4f}"
                    )

                    socket.send_string(payload)

                    time.sleep(dt)

        # ---------------------------------------------------------
        # RICOMINCIA IL PERCORSO
        # ---------------------------------------------------------

        x_curr = waypoints[0]["x_m"]
        y_curr = waypoints[0]["y_m"]
        z_curr = waypoints[0].get("z_m", 0.0)

        if num_wp > 1:

            dx = (
                waypoints[1]["x_m"] -
                waypoints[0]["x_m"]
            )

            dy = (
                waypoints[1]["y_m"] -
                waypoints[0]["y_m"]
            )

            yaw_curr = math.atan2(
                dy,
                dx
            )


if __name__ == "__main__":

    run_seed = (
        int(sys.argv[1])
        if len(sys.argv) > 1
        else 42
    )

    mah, wh = run_simulation(
        run_seed,
        publish_ipc=True
    )

    print(
        f"SEED: {run_seed} | "
        f"Consumo: {mah} mAh | "
        f"Energia: {wh} Wh"
    )
