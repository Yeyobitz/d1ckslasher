import pygame
from typing import Tuple, Optional
from .ui_element import UIElement

class Text(UIElement):
    def __init__(self, x: float, y: float, text: str, font: pygame.font.Font, color: Tuple[int, int, int] = (255, 255, 255)):
        self.text = text
        self.font = font
        self.color = color
        self._rendered_text = self.font.render(text, True, color)
        text_rect = self._rendered_text.get_rect()
        super().__init__(x, y, text_rect.width, text_rect.height)
        
    def set_text(self, text: str) -> None:
        """Actualiza el texto mostrado."""
        if text != self.text:
            self.text = text
            self._rendered_text = self.font.render(text, True, self.color)
            text_rect = self._rendered_text.get_rect()
            self.width = text_rect.width
            self.height = text_rect.height
            self.rect.width = text_rect.width
            self.rect.height = text_rect.height
            
    def draw(self, screen: pygame.Surface) -> None:
        """Dibuja el texto en la pantalla."""
        if self.is_visible:
            super().draw(screen)
            screen.blit(self._rendered_text, self.rect) 