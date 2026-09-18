import math
import pygame

# Inizializzazione Pygame
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Micro-Framework RobotDaZero - Simulatore")
clock = pygame.time.Clock()

class MezzoSimulato:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.theta = 0.0  # Orientamento in radianti
        self.v = 50.0     # Velocità lineare
        self.w = 1.0      # Velocità angolare
        self.dim = 20     # Dimensione visiva sul canvas

    def aggiorna(self, dt):
        self.x += self.v * math.cos(self.theta) * dt
        self.y += self.v * math.sin(self.theta) * dt
        self.theta += self.w * dt

    def disegna(self, surface):
        pos = (int(self.x), int(self.y))
        pygame.draw.circle(surface, (74, 85, 104), pos, self.dim)
        
        end_x = self.x + (self.dim + 10) * math.cos(self.theta)
        end_y = self.y + (self.dim + 10) * math.sin(self.theta)
        pygame.draw.line(surface, (255, 103, 25), pos, (int(end_x), int(end_y)), 3)

# Istanza del mezzo
veicolo = MezzoSimulato(id=1, x=640, y=360)

# Loop principale
running = True
while running:
    dt = clock.tick(60) / 1000.0  # Delta time in secondi

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    veicolo.aggiorna(dt)

    screen.fill((15, 23, 42))
    veicolo.disegna(screen)

    pygame.display.flip()

pygame.quit()