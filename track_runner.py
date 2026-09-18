import json
import sys
from brown_noise import BrownNoiseGenerator


def run_simulation(seed: int) -> tuple[float, float]:
    with open("track_definition.json", "r") as f:
        track = json.load(f)

    noise = BrownNoiseGenerator(seed=seed, amplitude=0.1)

    v_bat_oc = 8.2
    r_bat_int = 0.08
    m_kg = 1.5
    speed_m_s = 2.0
    dt = 0.02  # 50 Hz

    used_mah = 0.0
    used_wh = 0.0

    for wp in track["waypoints"]:
        r_m = wp.get("radius_m", None)

        for _ in range(100):
            b_noise = noise.get_sample() * wp["noise_amplitude"]
            f_friction = wp["friction_base"] + b_noise

            f_corner = 0.0
            if r_m and r_m > 0:
                f_centripetal = (m_kg * (speed_m_s**2)) / r_m
                f_corner = (0.5 / r_m) + (f_centripetal * 0.05)

            is_stuck = noise.check_obstacle_event(0.01)
            f_obstacle = 2.0 if is_stuck else 0.0

            f_total = max(0.05, f_friction + f_corner + f_obstacle)
            current_a = max(0.2, f_total * 7.5)
            voltage_v = max(5.0, v_bat_oc - (current_a * r_bat_int))

            # Integrazione consumi
            used_mah += current_a * dt * (1000.0 / 3600.0)
            used_wh += (voltage_v * current_a) * (dt / 3600.0)

    return round(used_mah, 2), round(used_wh, 4)


if __name__ == "__main__":
    run_seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    mah, wh = run_simulation(run_seed)
    print(f"SEED: {run_seed} | Consumo: {mah} mAh | Energia: {wh} Wh")
