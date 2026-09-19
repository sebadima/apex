import json
import math
import random

class InlineBrownNoiseGenerator:
    def __init__(self, seed: int, amplitude: float = 0.1):
        self.rng = random.Random(seed)
        self.amplitude = amplitude
        self.last_value = 0.0

    def get_sample(self) -> float:
        step = self.rng.uniform(-self.amplitude, self.amplitude)
        self.last_value += step
        # Limita il valore all'interno del range consentito
        self.last_value = max(-1.0, min(1.0, self.last_value))
        return self.last_value

    def check_obstacle_event(self, probability: float) -> bool:
        return self.rng.random() < probability

def run_simulation_isolated(seed: int) -> tuple[float, float]:
    with open("track_definition.json", "r") as f:
        track = json.load(f)

    noise = InlineBrownNoiseGenerator(seed=seed, amplitude=0.1)

    v_bat_oc = 8.2
    r_bat_int = 0.08
    m_kg = 1.5
    speed_m_s = 2.0
    dt = 0.02  # 50 Hz

    used_mah = 0.0
    used_wh = 0.0

    waypoints = track["waypoints"]
    num_wp = len(waypoints)

    x_curr = waypoints[0]["x_m"]
    y_curr = waypoints[0]["y_m"]

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

    return round(used_mah, 2), round(used_wh, 4)

def main():
    print("=== [DEBUG] Avvio script run_batch.py (Isolato) ===", flush=True)
    print("=== AVVIO TEST DI CONSUMO STOCASTICO (10 RUN) ===", flush=True)
    results = []

    for i in range(1, 11):
        seed = 1000 + (i * 37)
        print(f"[DEBUG] Preparazione run {i:02d}/10 con seed {seed}...", flush=True)
        
        try:
            print(f"[DEBUG] Chiamata a run_simulation_isolated({seed}) in corso...", flush=True)
            mah, wh = run_simulation_isolated(seed)
            print(f"[DEBUG] run_simulation_isolated({seed}) completata: {mah} mAh, {wh} Wh", flush=True)
        except Exception as e:
            print(f"[ERRORE CRITICO] Eccezione nella run {i} (seed {seed}): {e}", flush=True)
            raise e

        results.append((i, seed, mah, wh))
        print(
            f"Run {i:02d}/10 | Seed: {seed} -> Consumo: {mah} mAh | Energia: {wh} Wh",
            flush=True
        )

    print("\n=== [DEBUG] Calcolo statistiche finali in corso ===", flush=True)
    all_mah = [r[2] for r in results]
    min_mah = min(all_mah)
    max_mah = max(all_mah)
    avg_mah = round(sum(all_mah) / len(all_mah), 2)

    print("\n=== RIEPILOGO FINALE ===", flush=True)
    print(f"Consumo Minimo : {min_mah} mAh", flush=True)
    print(f"Consumo Massimo: {max_mah} mAh", flush=True)
    print(f"Consumo Medio  : {avg_mah} mAh", flush=True)
    print(
        f"Delta Variazione: {round(max_mah - min_mah, 2)} mAh (Dovuto a erba e"
        " stalli stocastici)",
        flush=True
    )
    print("=== [DEBUG] Esecuzione batch terminata correttamente ===", flush=True)

if __name__ == "__main__":
    main()