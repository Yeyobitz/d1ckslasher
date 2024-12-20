import pygame
import os
from typing import Dict, Optional

class ResourceManager:
    def __init__(self):
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        
    def load_font(self, name: str, path: str, size: int) -> pygame.font.Font:
        """Carga una fuente y la almacena."""
        if name not in self.fonts:
            try:
                font = pygame.font.Font(path, size)
                self.fonts[name] = font
            except Exception as e:
                print(f"Error al cargar la fuente {path}: {e}")
                # Usar una fuente por defecto si falla la carga
                font = pygame.font.Font(None, size)
                self.fonts[name] = font
        return self.fonts[name]
        
    def load_image(self, name: str, path: str) -> Optional[pygame.Surface]:
        """Carga una imagen y la almacena."""
        if name not in self.images:
            try:
                image = pygame.image.load(path)
                self.images[name] = image
            except Exception as e:
                print(f"Error al cargar la imagen {path}: {e}")
                return None
        return self.images[name]
        
    def load_sound(self, name: str, path: str) -> Optional[pygame.mixer.Sound]:
        """Carga un sonido y lo almacena."""
        if name not in self.sounds:
            try:
                sound = pygame.mixer.Sound(path)
                self.sounds[name] = sound
            except Exception as e:
                print(f"Error al cargar el sonido {path}: {e}")
                return None
        return self.sounds[name]
        
    def get_font(self, name: str) -> Optional[pygame.font.Font]:
        """Retorna una fuente cargada."""
        return self.fonts.get(name)
        
    def get_image(self, name: str) -> Optional[pygame.Surface]:
        """Retorna una imagen cargada."""
        return self.images.get(name)
        
    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Retorna un sonido cargado."""
        return self.sounds.get(name) 