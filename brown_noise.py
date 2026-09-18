import random


class BrownNoiseGenerator:

    def __init__(self, seed: int, amplitude: float = 0.1):
        self.rng = random.Random(seed)
        self.amplitude = amplitude
        self.current_value = 0.0

    def get_sample(self) -> float:
        step = self.rng.gauss(0, self.amplitude)
        self.current_value = (self.current_value * 0.92) + step
        return self.current_value

    def check_obstacle_event(self, probability: float) -> bool:
        return self.rng.random() < probability
