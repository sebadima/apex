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
        time.sleep(0.5)

    noise = BrownNoiseGenerator(seed=seed, amplitude=0.1)

    v_bat_oc = 8.2
    r_bat_int = 0.08
    m_kg = 1.5
    speed_m_s = 2.0
    dt = 0.02

    used_mah = 0.0
    used_wh = 0.0

    waypoints = track["waypoints"]
    num_wp = len(waypoints)

    x_curr = waypoints[0]["x_m"]
    y_curr = waypoints[0]["y_m"]

    while True:
        for i in range(1, num_wp):
            wp_target = waypoints[i]
            x_target = wp_target["x_m"]
            y_target = wp_target["y_m"]
            
            dx = x_target - x_curr
            dy = y_target - y_curr
            dist = math.hypot(dx, dy)
            
            if dist == 0:
                continue
                
            dir_x = dx / dist
            dir_y = dy / dist
            
            r_m = wp_target.get("radius_m", None)
            steps = int(dist / (speed_m_s * dt))
            
            for _ in range(steps):
                x_curr += dir_x * speed_m_s * dt
                y_curr += dir_y * speed_m_s * dt

                b_noise = noise.get_sample() * wp_target["noise_amplitude"]
                f_friction = wp_target["friction_base"] + b_noise

                f_corner = 0.0
                if r_m and r_m > 0:
                    f_centripetal = (m_kg * (speed_m_s**2)) / r_m
                    f_corner = (0.5 / r_m) + (f_centripetal * 0.05)

                is_stuck = noise.check_obstacle_event(0.01)
                f_obstacle = 2.0 if is_stuck else 0.0

                f_total = max(0.05, f_friction + f_corner + f_obstacle)
                current_a = max(0.2, f_total * 7.5)
                voltage_v = max(5.0, v_bat_oc - (current_a * r_bat_int))

                used_mah += current_a * dt * (1000.0 / 3600.0)
                used_wh += (voltage_v * current_a) * (dt / 3600.0)

                if socket:
                    ts = time.time_ns()
                    payload = f"{ts},APEX_01,{voltage_v:.2f},{current_a:.2f},{x_curr:.2f},{y_curr:.2f}"
                    socket.send_string(payload)
                    time.sleep(dt)
                    
        # Reset al waypoint zero per marcia continua
        x_curr = waypoints[0]["x_m"]
        y_curr = waypoints[0]["y_m"]

    return round(used_mah, 2), round(used_wh, 4)

if __name__ == "__main__":
    run_seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    mah, wh = run_simulation(run_seed, publish_ipc=True)
    print(f"SEED: {run_seed} | Consumo: {mah} mAh | Energia: {wh} Wh")