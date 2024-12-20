import pygame
from typing import List, Tuple
from .entity import Entity

class Player(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 20, 20)
        self.color = (0, 255, 0)  # Verde para el jugador
        self.trail: List[Tuple[float, float]] = []
        self.trail_length = 10
        self.trail_color = (0, 255, 0, 128)  # Verde semi-transparente
        self.combo = 0
        self.max_combo = 0
        self.score = 0
        self.is_invulnerable = False
        self.invulnerability_timer = 0
        self.invulnerability_duration = 1.0  # 1 segundo de invulnerabilidad
        
    def update(self, dt: float) -> None:
        """Actualiza la posición del jugador y su rastro."""
        # Actualizar la posición del jugador
        mouse_pos = pygame.mouse.get_pos()
        self.set_position(mouse_pos[0] - self.width / 2, mouse_pos[1] - self.height / 2)
        
        # Actualizar el rastro
        self.trail.append((self.x + self.width / 2, self.y + self.height / 2))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)
            
        # Actualizar invulnerabilidad
        if self.is_invulnerable:
            self.invulnerability_timer -= dt
            if self.invulnerability_timer <= 0:
                self.is_invulnerable = False
                
    def draw(self, screen: pygame.Surface) -> None:
        """Dibuja el jugador y su rastro."""
        if self.is_active:
            # Dibujar el rastro
            if len(self.trail) > 1:
                trail_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                pygame.draw.lines(trail_surface, self.trail_color, False, self.trail, 2)
                screen.blit(trail_surface, (0, 0))
            
            # Dibujar el jugador
            if not self.is_invulnerable or pygame.time.get_ticks() % 200 < 100:
                pygame.draw.rect(screen, self.color, self.rect)
                
    def add_score(self, points: int) -> None:
        """Añade puntos al score y actualiza el combo."""
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)
        multiplier = max(1, self.combo // 5)  # Cada 5 combos aumenta el multiplicador
        self.score += points * multiplier
        
    def reset_combo(self) -> None:
        """Reinicia el combo cuando el jugador es golpeado."""
        self.combo = 0
        
    def make_invulnerable(self) -> None:
        """Hace al jugador invulnerable por un tiempo."""
        self.is_invulnerable = True
        self.invulnerability_timer = self.invulnerability_duration 