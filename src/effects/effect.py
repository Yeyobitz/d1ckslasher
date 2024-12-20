import pygame
from typing import Tuple

class Effect:
    def __init__(self, x: float, y: float, duration: float = 1.0):
        self.x = x
        self.y = y
        self.duration = duration
        self.timer = duration
        self.is_active = True
        
    def update(self, dt: float) -> None:
        """Actualiza el estado del efecto."""
        if self.is_active:
            self.timer -= dt
            if self.timer <= 0:
                self.is_active = False
                
    def draw(self, screen: pygame.Surface) -> None:
        """Dibuja el efecto en la pantalla."""
        pass  # Implementado por las clases hijas
        
    def get_progress(self) -> float:
        """Retorna el progreso de la animación (0.0 a 1.0)."""
        return 1.0 - (self.timer / self.duration) 