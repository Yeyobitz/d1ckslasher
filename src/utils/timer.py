import pygame

class Timer:
    def __init__(self, target_fps: int = 60):
        self.clock = pygame.time.Clock()
        self.target_fps = target_fps
        self.dt = 0
        self.fps = 0
        
    def tick(self) -> float:
        """Actualiza el tiempo y retorna el delta time."""
        self.dt = self.clock.tick(self.target_fps) / 1000.0  # Convertir a segundos
        self.fps = self.clock.get_fps()
        return self.dt
        
    def get_fps(self) -> float:
        """Retorna los FPS actuales."""
        return self.fps
        
    def get_dt(self) -> float:
        """Retorna el último delta time."""
        return self.dt 