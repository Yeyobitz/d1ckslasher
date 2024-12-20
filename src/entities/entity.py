import pygame
from typing import Tuple, Optional

class Entity:
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.is_active = True
        self.velocity = pygame.math.Vector2(0, 0)
        self.color = (255, 255, 255)  # Color por defecto: blanco
        
    def update(self, dt: float) -> None:
        """Actualiza la posición y estado de la entidad."""
        self.x += self.velocity.x * dt
        self.y += self.velocity.y * dt
        self.rect.x = self.x
        self.rect.y = self.y
        
    def draw(self, screen: pygame.Surface) -> None:
        """Dibuja la entidad en la pantalla."""
        if self.is_active:
            pygame.draw.rect(screen, self.color, self.rect)
            
    def get_position(self) -> Tuple[float, float]:
        """Retorna la posición actual de la entidad."""
        return (self.x, self.y)
        
    def set_position(self, x: float, y: float) -> None:
        """Establece la posición de la entidad."""
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        
    def collides_with(self, other: 'Entity') -> bool:
        """Verifica si hay colisión con otra entidad."""
        return self.is_active and other.is_active and self.rect.colliderect(other.rect) 