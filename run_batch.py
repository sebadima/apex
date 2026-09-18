from track_runner import run_simulation


def main():
    print("=== AVVIO TEST DI CONSUMO STOCASTICO (10 RUN) ===")
    results = []

    # Genera 10 run con 10 seed differenti
    for i in range(1, 11):
        seed = 1000 + (i * 37)  # Seed univoco per ogni run
        mah, wh = run_simulation(seed)
        results.append((i, seed, mah, wh))
        print(
            f"Run {i:02d}/10 | Seed: {seed} -> Consumo: {mah} mAh | Energia:"
            f" {wh} Wh"
        )

    print("\n=== RIEPILOGO FINALE ===")
    all_mah = [r[2] for r in results]
    min_mah = min(all_mah)
    max_mah = max(all_mah)
    avg_mah = round(sum(all_mah) / len(all_mah), 2)

    print(f"Consumo Minimo : {min_mah} mAh")
    print(f"Consumo Massimo: {max_mah} mAh")
    print(f"Consumo Medio  : {avg_mah} mAh")
    print(
        f"Delta Variazione: {round(max_mah - min_mah, 2)} mAh (Dovuto a erba e"
        " stalli stocastici)"
    )


if __name__ == "__main__":
    main()
