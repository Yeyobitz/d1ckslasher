import pygame
from typing import Tuple, Optional, Callable
from .ui_element import UIElement
from .text import Text

class Button(UIElement):
    def __init__(self, x: float, y: float, width: float, height: float,
                 text: str, font: pygame.font.Font,
                 normal_color: Tuple[int, int, int] = (100, 100, 100),
                 hover_color: Tuple[int, int, int] = (150, 150, 150),
                 text_color: Tuple[int, int, int] = (255, 255, 255),
                 on_click: Optional[Callable[[], None]] = None):
        super().__init__(x, y, width, height)
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.background_color = normal_color
        self.on_click = on_click
        self.is_hovered = False
        
        # Crear el texto centrado
        self.text = Text(0, 0, text, font, text_color)
        self._center_text()
        
    def _center_text(self) -> None:
        """Centra el texto en el botón."""
        text_x = self.x + (self.width - self.text.width) / 2
        text_y = self.y + (self.height - self.text.height) / 2
        self.text.set_position(text_x, text_y)
        
    def update(self, dt: float) -> None:
        """Actualiza el estado del botón."""
        mouse_pos = pygame.mouse.get_pos()
        was_hovered = self.is_hovered
        self.is_hovered = self.contains_point(mouse_pos)
        
        # Actualizar color basado en el estado
        self.background_color = self.hover_color if self.is_hovered else self.normal_color
        
        # Manejar clic
        if self.is_hovered and pygame.mouse.get_pressed()[0] and self.on_click:
            self.on_click()
            
    def set_position(self, x: float, y: float) -> None:
        """Actualiza la posición del botón y su texto."""
        super().set_position(x, y)
        self._center_text()
        
    def draw(self, screen: pygame.Surface) -> None:
        """Dibuja el botón y su texto."""
        if self.is_visible:
            super().draw(screen)
            self.text.draw(screen) 