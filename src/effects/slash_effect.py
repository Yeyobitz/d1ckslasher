import pygame
import math
from typing import Tuple
from .effect import Effect

class SlashEffect(Effect):
    def __init__(self, x: float, y: float, color: Tuple[int, int, int] = (255, 255, 255)):
        super().__init__(x, y, duration=0.3)
        self.color = color
        self.size = 40
        self.line_width = 3
        
    def draw(self, screen: pygame.Surface) -> None:
        """Dibuja el efecto de corte."""
        if self.is_active:
            progress = self.get_progress()
            # El efecto crece y se desvanece
            current_size = self.size * min(progress * 2, 1.0)
            alpha = int(255 * (1.0 - progress))
            
            # Crear una superficie con alpha para el desvanecimiento
            surface = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
            
            # Dibujar las líneas del corte
            color_with_alpha = (*self.color, alpha)
            angle = progress * math.pi  # Rotación basada en el progreso
            
            # Línea principal
            start_pos = (
                current_size + math.cos(angle) * current_size,
                current_size + math.sin(angle) * current_size
            )
            end_pos = (
                current_size + math.cos(angle + math.pi) * current_size,
                current_size + math.sin(angle + math.pi) * current_size
            )
            pygame.draw.line(surface, color_with_alpha, start_pos, end_pos, self.line_width)
            
            # Líneas cruzadas
            cross_angle = math.pi / 4  # 45 grados
            for offset in [-cross_angle, cross_angle]:
                start_pos = (
                    current_size + math.cos(angle + offset) * current_size * 0.7,
                    current_size + math.sin(angle + offset) * current_size * 0.7
                )
                end_pos = (
                    current_size + math.cos(angle + offset + math.pi) * current_size * 0.7,
                    current_size + math.sin(angle + offset + math.pi) * current_size * 0.7
                )
                pygame.draw.line(surface, color_with_alpha, start_pos, end_pos, self.line_width)
            
            # Dibujar la superficie en la pantalla
            screen.blit(surface, (self.x - current_size, self.y - current_size)) 