import pygame
import random
import math
from typing import List, Tuple
from .effect import Effect

class Particle:
    def __init__(self, x: float, y: float, velocity: Tuple[float, float], color: Tuple[int, int, int], size: float):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.color = color
        self.size = size
        self.alpha = 255
        
    def update(self, dt: float) -> None:
        """Actualiza la posición y estado de la partícula."""
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt
        self.alpha = max(0, self.alpha - 500 * dt)  # Desvanecer
        self.size = max(0, self.size - 10 * dt)  # Encoger

class ParticleEffect(Effect):
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], particle_count: int = 20):
        super().__init__(x, y, duration=0.5)
        self.particles: List[Particle] = []
        self.color = color
        
        # Crear partículas iniciales
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 300)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            size = random.uniform(2, 6)
            
            particle = Particle(x, y, velocity, color, size)
            self.particles.append(particle)
            
    def update(self, dt: float) -> None:
        """Actualiza todas las partículas."""
        super().update(dt)
        if self.is_active:
            for particle in self.particles:
                particle.update(dt)
                
    def draw(self, screen: pygame.Surface) -> None:
        """Dibuja todas las partículas."""
        if self.is_active:
            surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            
            for particle in self.particles:
                if particle.alpha > 0 and particle.size > 0:
                    color_with_alpha = (*self.color, int(particle.alpha))
                    pygame.draw.circle(
                        surface,
                        color_with_alpha,
                        (int(particle.x), int(particle.y)),
                        particle.size
                    )
                    
            screen.blit(surface, (0, 0)) 