import pygame
from typing import Tuple
from .entity import Entity

class Enemy(Entity):
    def __init__(self, x: float, y: float, target_pos: Tuple[float, float], speed: float = 300):
        # El cuerpo es más grande que la cabeza
        body_width = 40
        body_height = 60
        super().__init__(x, y, body_width, body_height)
        
        # Crear la cabeza como un rectángulo más pequeño en la parte superior
        self.head_width = 30
        self.head_height = 20
        self.head_rect = pygame.Rect(
            x + (body_width - self.head_width) / 2,
            y - self.head_height,
            self.head_width,
            self.head_height
        )
        
        # Colores
        self.body_color = (255, 0, 0)  # Rojo para el cuerpo
        self.head_color = (200, 0, 0)  # Rojo más oscuro para la cabeza
        
        # Movimiento
        self.speed = speed
        self.target_pos = target_pos
        self._update_velocity()
        
    def _update_velocity(self) -> None:
        """Actualiza la velocidad basada en la posición objetivo."""
        direction = pygame.math.Vector2(
            self.target_pos[0] - self.x,
            self.target_pos[1] - self.y
        )
        if direction.length() > 0:
            direction = direction.normalize()
            self.velocity = direction * self.speed
            
    def update(self, dt: float) -> None:
        """Actualiza la posición del enemigo y su cabeza."""
        super().update(dt)
        # Actualizar la posición de la cabeza
        self.head_rect.x = self.x + (self.width - self.head_width) / 2
        self.head_rect.y = self.y - self.head_height
        
    def draw(self, screen: pygame.Surface) -> None:
        """Dibuja el enemigo con su cuerpo y cabeza."""
        if self.is_active:
            # Dibujar el cuerpo
            pygame.draw.rect(screen, self.body_color, self.rect)
            # Dibujar la cabeza
            pygame.draw.rect(screen, self.head_color, self.head_rect)
            
    def set_target(self, target_pos: Tuple[float, float]) -> None:
        """Actualiza la posición objetivo y recalcula la velocidad."""
        self.target_pos = target_pos
        self._update_velocity()
        
    def head_collides_with(self, other: Entity) -> bool:
        """Verifica si hay colisión con la cabeza del enemigo."""
        return self.is_active and other.is_active and self.head_rect.colliderect(other.rect) 