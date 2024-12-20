import pygame
from typing import Tuple, Optional

class UIElement:
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.is_visible = True
        self.background_color: Optional[Tuple[int, int, int]] = None
        self.border_color: Optional[Tuple[int, int, int]] = None
        self.border_width = 0
        
    def update(self, dt: float) -> None:
        """Actualiza el estado del elemento UI."""
        pass
        
    def draw(self, screen: pygame.Surface) -> None:
        """Dibuja el elemento UI en la pantalla."""
        if self.is_visible:
            if self.background_color is not None:
                pygame.draw.rect(screen, self.background_color, self.rect)
            if self.border_color is not None and self.border_width > 0:
                pygame.draw.rect(screen, self.border_color, self.rect, self.border_width)
                
    def set_position(self, x: float, y: float) -> None:
        """Establece la posición del elemento UI."""
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        
    def contains_point(self, point: Tuple[float, float]) -> bool:
        """Verifica si un punto está dentro del elemento UI."""
        return self.rect.collidepoint(point) 