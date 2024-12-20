import pygame
import sys
import random
import math
import os

# Inicializar Pygame
pygame.init()
pygame.mixer.init()

def resource_path(relative_path):
    """ Obtener la ruta absoluta a los recursos, funciona para dev y para PyInstaller """
    try:
        # PyInstaller crea un directorio temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Colores (ajustados para mejor visibilidad con alpha)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
SALMON = (255, 160, 160)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 140, 0)
PURPLE = (160, 32, 240)
GOLD = (255, 215, 0)

# Sistema de sonido simplificado
SOUNDS = {}

def init_sounds():
    """Inicializar los sonidos del juego"""
    sound_files = {
        'slash': 'slash.wav',
        'hit': 'hit.wav',
        'powerup': 'powerup.wav',
        'shield_break': 'shield_break.wav',
        'berserker': 'berserker.wav',
        'matrix': 'matrix.wav',
        'golden': 'golden.wav',
        'game_over': 'game_over.wav',
        'combo': 'combo.wav'
    }
    
    for sound_name, filename in sound_files.items():
        try:
            sound_path = resource_path(os.path.join("assets", "sounds", filename))
            if os.path.exists(sound_path):
                SOUNDS[sound_name] = pygame.mixer.Sound(sound_path)
            else:
                print(f"Archivo de sonido no encontrado: {sound_path}")
        except Exception as e:
            print(f"Error al cargar sonido {filename}: {e}")

def play_sound(sound_name, volume=1.0):
    """Reproducir un sonido de forma segura"""
    if sound_name in SOUNDS and SOUNDS[sound_name]:
        try:
            SOUNDS[sound_name].set_volume(volume)
            SOUNDS[sound_name].play()
        except Exception as e:
            print(f"Error al reproducir sonido {sound_name}: {e}")

# Inicializar sonidos
init_sounds()

# Configurar la ventana transparente
info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h

# Configuración específica para Windows
if sys.platform == 'win32':
    # Importar las bibliotecas necesarias
    import win32gui # type: ignore
    import win32con # type: ignore
    import win32api # type: ignore
    import win32process # type: ignore
    from ctypes import windll, byref, c_int # type: ignore

    # Crear la ventana con el flag de layered
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
    hwnd = pygame.display.get_wm_info()["window"]

    # Configurar la ventana como layered y topmost
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                          ex_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST)

    # Hacer la ventana transparente pero interactiva
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0,0,0), 128, win32con.LWA_ALPHA)
    
    # Extender el frame en la ventana para efecto de transparencia
    margins = (0, 0, screen_width, screen_height)
    DwmExtendFrameIntoClientArea = windll.dwmapi.DwmExtendFrameIntoClientArea
    DwmExtendFrameIntoClientArea(hwnd, byref(c_int(margins[0])))

    try:
        # Simplificar la puesta al frente de la ventana
        win32gui.SetForegroundWindow(hwnd)
    except Exception as e:
        print(f"No se pudo poner la ventana al frente: {e}")
else:
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME | pygame.SRCALPHA)

pygame.display.set_caption("Ninja Mouse")

# Estilos de combo
COMBO_STYLES = {
    1: {
        'color': WHITE,
        'border_color': None,
        'glow': False,
        'scale': 1.0,
        'shake': False
    },
    2: {
        'color': BLUE,
        'border_color': WHITE,
        'glow': False,
        'scale': 1.2,
        'shake': False
    },
    3: {
        'color': ORANGE,
        'border_color': WHITE,
        'glow': True,
        'scale': 1.4,
        'shake': False
    },
    4: {
        'color': PURPLE,
        'border_color': BLACK,
        'glow': True,
        'scale': 1.6,
        'shake': True
    },
    5: {
        'color': GOLD,
        'border_color': WHITE,
        'glow': True,
        'scale': 2.0,
        'shake': True
    }
}

# Modificar la sección de carga de fuentes:
font_paths = [
    resource_path(os.path.join("assets", "PressStart2P-Regular.ttf")),
]

GAME_FONT = None
SCORE_FONT = None

# Cargar fuentes silenciosamente
try:
    GAME_FONT = pygame.font.Font(resource_path(os.path.join("assets", "PressStart2P-Regular.ttf")), 36)
    SCORE_FONT = pygame.font.Font(resource_path(os.path.join("assets", "PressStart2P-Regular.ttf")), 48)
except:
    GAME_FONT = pygame.font.Font(None, 36)
    SCORE_FONT = pygame.font.Font(None, 48)

def render_combo_text(text, color, border_color=None, glow=False, scale=1.0):
    # Renderizar el texto principal
    base_size = 36
    scaled_size = int(base_size * scale)
    temp_font = pygame.font.Font(font_paths[0] if font_paths else None, scaled_size)
    
    # Si hay glow, crear el efecto de resplandor
    if glow:
        glow_surfaces = []
        for offset in range(5, 0, -1):
            glow_color = color[0], color[1], color[2], 50
            glow_text = temp_font.render(text, True, glow_color)
            glow_surface = pygame.Surface(
                (glow_text.get_width() + offset*4, 
                 glow_text.get_height() + offset*4),
                pygame.SRCALPHA
            )
            glow_surface.blit(glow_text, (offset*2, offset*2))
            glow_surfaces.append(glow_surface)
    
    # Si hay borde, renderizar el texto con borde
    if border_color:
        border_surface = pygame.Surface(
            (scaled_size * len(text) * 1.2, scaled_size * 1.5),
            pygame.SRCALPHA
        )
        
        for dx, dy in [(-2,0), (2,0), (0,-2), (0,2)]:
            border_text = temp_font.render(text, True, border_color)
            border_surface.blit(border_text, 
                              (border_surface.get_width()//2 - border_text.get_width()//2 + dx,
                               border_surface.get_height()//2 - border_text.get_height()//2 + dy))
    
    # Renderizar el texto principal
    main_text = temp_font.render(text, True, color)
    
    # Combinar todas las superficies
    final_surface = pygame.Surface(
        (scaled_size * len(text) * 1.2, scaled_size * 1.5),
        pygame.SRCALPHA
    )
    
    if glow:
        for glow_surface in glow_surfaces:
            final_surface.blit(glow_surface, 
                             (final_surface.get_width()//2 - glow_surface.get_width()//2,
                              final_surface.get_height()//2 - glow_surface.get_height()//2))
    
    if border_color:
        final_surface.blit(border_surface, (0,0))
    
    final_surface.blit(main_text,
                      (final_surface.get_width()//2 - main_text.get_width()//2,
                       final_surface.get_height()//2 - main_text.get_height()//2))
    
    return final_surface

class BaseEnemy:
    def __init__(self):
        # Dimensiones base
        self.width = 60
        self.height = 20
        self.head_size = 20
        self.head_base_width = self.height * 1.5
        self.head_tip_width = self.height * 0.8
        
        # Posición inicial aleatoria en los bordes
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.x = random.randint(0, screen_width)
            self.y = -self.height
        elif side == 'bottom':
            self.x = random.randint(0, screen_width)
            self.y = screen_height
        elif side == 'left':
            self.x = -self.width
            self.y = random.randint(0, screen_height)
        else:
            self.x = screen_width
            self.y = random.randint(0, screen_height)
        
        self.angle = 0
        self.target_angle = 0
        self.speed = 2
        self.rotation_speed = 4
        self.color_body = SALMON
        self.color_head = RED
        self.alpha = 200

    def get_head_tip_position(self):
        """Obtener la posición de la punta"""
        angle_rad = math.radians(self.angle)
        tip_x = self.x + math.cos(angle_rad) * self.width/2
        tip_y = self.y + math.sin(angle_rad) * self.width/2
        return tip_x, tip_y

    def move(self, target_x, target_y):
        # Calcular dirección hacia el objetivo
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Calcular el ángulo objetivo
        self.target_angle = math.degrees(math.atan2(dy, dx))
        
        # Ajustar el ángulo gradualmente
        angle_diff = (self.target_angle - self.angle) % 360
        if angle_diff > 180:
            angle_diff -= 360
        
        if abs(angle_diff) > self.rotation_speed:
            if angle_diff > 0:
                self.angle += self.rotation_speed
            else:
                self.angle -= self.rotation_speed
        else:
            self.angle = self.target_angle
        
        self.angle = self.angle % 360
        
        if distance != 0:
            self.x += (dx/distance) * self.speed
            self.y += (dy/distance) * self.speed

    def draw(self, surface):
        # Crear superficie para el cuerpo con alpha
        total_height = max(self.height, self.head_base_width)
        body = pygame.Surface((self.width, total_height), pygame.SRCALPHA)
        
        # Dibujar el cuerpo
        body_y = (total_height - self.height) // 2
        pygame.draw.rect(body, (*self.color_body, self.alpha), 
                        (0, body_y, self.width - self.head_size, self.height))
        
        # Dibujar la cabeza
        head_surface = pygame.Surface((self.head_size, total_height), pygame.SRCALPHA)
        head_points = [
            (0, (total_height - self.head_base_width) // 2),
            (self.head_size, (total_height - self.head_tip_width) // 2),
            (self.head_size, (total_height + self.head_tip_width) // 2),
            (0, (total_height + self.head_base_width) // 2)
        ]
        pygame.draw.polygon(head_surface, (*self.color_head, self.alpha), head_points)
        
        # Agregar la cabeza al cuerpo
        body.blit(head_surface, (self.width - self.head_size, 0))
        
        # Rotar y dibujar
        rotated = pygame.transform.rotate(body, -self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect)
        
        # DEBUG: Dibujar áreas de colisión
        # self.draw_collision_areas(surface)

    def draw_collision_areas(self, surface):
        # Dibujar área de colisión de la cabeza
        tip_x, tip_y = self.get_head_tip_position()
        pygame.draw.circle(surface, WHITE, (int(tip_x), int(tip_y)), 
                         int(self.head_tip_width/2), 1)
        
        # Dibujar área de colisión del cuerpo
        angle_rad = math.radians(self.angle)
        body_points = [
            (-self.width/2, -self.height/2),
            (self.width/2 - self.head_size, -self.height/2),
            (self.width/2 - self.head_size, self.height/2),
            (-self.width/2, self.height/2)
        ]
        
        rotated_points = []
        for x, y in body_points:
            rx = x * math.cos(angle_rad) - y * math.sin(angle_rad)
            ry = x * math.sin(angle_rad) + y * math.cos(angle_rad)
            rotated_points.append((self.x + rx, self.y + ry))
        
        if len(rotated_points) >= 4:
            pygame.draw.lines(surface, WHITE, True, rotated_points, 1)

    def check_head_collision(self, mouse_x, mouse_y):
        tip_x, tip_y = self.get_head_tip_position()
        dx = mouse_x - tip_x
        dy = mouse_y - tip_y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < self.head_tip_width/2

    def check_body_collision(self, mouse_x, mouse_y):
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        angle_rad = math.radians(-self.angle)
        rotated_x = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
        rotated_y = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
        
        body_left = -self.width/2
        body_right = self.width/2 - self.head_size
        body_top = -self.height/2
        body_bottom = self.height/2
        
        return (body_left < rotated_x < body_right and 
                body_top < rotated_y < body_bottom)

    def update(self, mouse_x, mouse_y):
        self.move(mouse_x, mouse_y)
        if self.check_head_collision(mouse_x, mouse_y):
            return "head_collision"
        elif self.check_body_collision(mouse_x, mouse_y):
            return "body_collision"
        return None

class NormalEnemy(BaseEnemy):
    """Enemigo básico que persigue al jugador"""
    def __init__(self):
        super().__init__()

class SplitEnemy(BaseEnemy):
    """Enemigo que se divide en dos al ser cortado"""
    def __init__(self, size=1.0, x=None, y=None):
        super().__init__()
        # Ajustar tamaño según el nivel de división
        self.width *= size
        self.height *= size
        self.head_size *= size
        self.head_base_width *= size
        self.head_tip_width *= size
        self.speed = 2 + (1 - size)  # Más pequeño = más rápido
        
        # Si se especifica posición, usarla (para las divisiones)
        if x is not None and y is not None:
            self.x = x
            self.y = y
        
        self.size = size
        self.color_body = (255, 180, 180)  # Un poco más rosado
        self.color_head = (255, 50, 50)    # Rojo más brillante

    def split(self):
        """Retorna dos enemigos más pequeños"""
        if self.size > 0.3:  # No dividir si es muy pequeño
            new_size = self.size * 0.7
            angle1 = self.angle + 45
            angle2 = self.angle - 45
            dist = 20 * self.size
            
            # Calcular posiciones para los nuevos enemigos
            x1 = self.x + math.cos(math.radians(angle1)) * dist
            y1 = self.y + math.sin(math.radians(angle1)) * dist
            x2 = self.x + math.cos(math.radians(angle2)) * dist
            y2 = self.y + math.sin(math.radians(angle2)) * dist
            
            return [
                SplitEnemy(new_size, x1, y1),
                SplitEnemy(new_size, x2, y2)
            ]
        return []

class ShooterEnemy(BaseEnemy):
    """Enemigo que dispara proyectiles"""
    def __init__(self):
        super().__init__()
        self.shoot_delay = 120  # 2 segundos a 60 FPS
        self.shoot_timer = random.randint(0, self.shoot_delay)
        self.color_body = (255, 200, 150)  # Naranja claro
        self.color_head = (255, 100, 0)    # Naranja oscuro
        self.projectiles = []
        self.speed = 1.5  # Más lento que el normal

    def update(self, mouse_x, mouse_y):
        result = super().update(mouse_x, mouse_y)
        
        # Actualizar temporizador de disparo
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot()
            self.shoot_timer = self.shoot_delay
        
        # Actualizar proyectiles
        for proj in self.projectiles[:]:
            proj.update()
            if not proj.active:
                self.projectiles.remove(proj)
        
        return result

    def shoot(self):
        """Dispara un proyectil hacia el jugador"""
        tip_x, tip_y = self.get_head_tip_position()
        self.projectiles.append(Projectile(tip_x, tip_y, self.angle))

    def draw(self, surface):
        super().draw(surface)
        # Dibujar proyectiles
        for proj in self.projectiles:
            proj.draw(surface)

class Projectile:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 5
        self.radius = 5
        self.active = True
        self.color = (255, 100, 0)  # Naranja
        
    def check_collision(self, mouse_x, mouse_y):
        """Comprobar si la bala colisiona con el mouse"""
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < self.radius * 2  # Radio un poco más grande para mejor jugabilidad
        
    def update(self):
        # Mover en la dirección del ángulo
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed
        
        # Desactivar si sale de la pantalla
        if (self.x < -50 or self.x > screen_width + 50 or
            self.y < -50 or self.y > screen_height + 50):
            self.active = False
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, 
                         (int(self.x), int(self.y)), self.radius)

class FastEnemy(BaseEnemy):
    """Enemigo que persigue al jugador más rápido"""
    def __init__(self):
        super().__init__()
        self.speed = 4  # Doble de velocidad
        self.color_body = (200, 160, 255)  # Púrpura claro
        self.color_head = (160, 32, 240)   # Púrpura
        self.rotation_speed = 6  # Más ágil

    def move(self, target_x, target_y):
        super().move(target_x, target_y)
        # Movimiento serpenteante
        self.angle += math.sin(pygame.time.get_ticks() * 0.005) * 2

# Reemplazar la clase Enemy existente con NormalEnemy
Enemy = NormalEnemy

class MouseTrail:
    def __init__(self):
        self.positions = []  # Lista de posiciones anteriores del mouse
        self.max_length = 15  # Reducido de 20 a 15 para menos rastro
        self.last_pos = None
        self.last_time = pygame.time.get_ticks()
        self.base_width = 6  # Reducido de 8 a 6
        self.collision_radius = 2
        self.collision_glow = 6
        self.smoothing_factor = 0.5  # Factor de suavizado

    def update(self, pos):
        current_time = pygame.time.get_ticks()
        
        if self.last_pos:
            # Aplicar suavizado al movimiento
            smoothed_x = self.last_pos[0] + (pos[0] - self.last_pos[0]) * self.smoothing_factor
            smoothed_y = self.last_pos[1] + (pos[1] - self.last_pos[1]) * self.smoothing_factor
            smoothed_pos = (smoothed_x, smoothed_y)
            
            dx = smoothed_pos[0] - self.last_pos[0]
            dy = smoothed_pos[1] - self.last_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            dt = current_time - self.last_time
            speed = distance / dt if dt > 0 else 0
            
            # Hacer la estela más reactiva a la velocidad pero con límites
            self.max_length = min(15 + int(speed * 0.8), 20)
            width = min(self.base_width + speed * 0.2, 15)
        else:
            smoothed_pos = pos
            width = self.base_width
        
        self.positions.append((smoothed_pos, width))
        
        if len(self.positions) > self.max_length:
            self.positions.pop(0)
        
        self.last_pos = smoothed_pos
        self.last_time = current_time

    def draw(self, surface):
        if len(self.positions) < 2:
            return
        
        # Dibujar la estela con degradado y ancho variable
        for i in range(len(self.positions) - 1):
            alpha = int(150 * (i / len(self.positions)))  # Reducido de 200 a 150
            color = (*BLUE, alpha)
            start_pos, start_width = self.positions[i]
            end_pos, end_width = self.positions[i + 1]
            
            width = (start_width + end_width) / 2
            pygame.draw.line(surface, color, start_pos, end_pos, int(width))
        
        # Dibujar el punto de colisión
        if self.positions:
            current_pos = self.positions[-1][0]
            # Dibujar brillo exterior más sutil
            glow_color = (*BLUE, 80)  # Reducido de 100 a 80
            pygame.draw.circle(surface, glow_color, current_pos, self.collision_glow)
            # Dibujar punto central
            pygame.draw.circle(surface, BLUE, current_pos, self.collision_radius)

class ScreenShake:
    def __init__(self):
        self.duration = 0
        self.intensity = 0
        self.offset_x = 0
        self.offset_y = 0
        
    def start(self, duration, intensity):
        self.duration = duration
        self.intensity = intensity
        
    def get_offset(self):
        if self.duration <= 0:
            return (0, 0)
        
        # Reducir la intensidad gradualmente
        current_intensity = self.intensity * (self.duration / self.duration)
        self.duration -= 1
        
        if self.duration <= 0:
            return (0, 0)
            
        # Usar seno y coseno para un movimiento más suave
        time = pygame.time.get_ticks() / 50.0  # Reducir la velocidad de vibración
        self.offset_x = math.sin(time) * current_intensity
        self.offset_y = math.cos(time) * current_intensity
        
        return (int(self.offset_x), int(self.offset_y))

class Effect:
    def __init__(self, x, y, color, size, duration):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.alive = True

    def update(self):
        current_time = pygame.time.get_ticks()
        progress = (current_time - self.start_time) / self.duration
        if progress >= 1:
            self.alive = False
        return self.alive

class HitEffect(Effect):
    def draw(self, surface):
        current_time = pygame.time.get_ticks()
        progress = (current_time - self.start_time) / self.duration
        size = self.size * (1 + progress)
        alpha = int(255 * (1 - progress))
        # Crear el color con alpha correctamente
        r, g, b = self.color  # Desempaquetar el color RGB
        color = (r, g, b)  # Crear nuevo color con alpha
        
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(size))

class Heart:
    def __init__(self, x, y, size=30):
        self.x = x
        self.y = y
        self.size = size
        self.pulse = random.uniform(0, 2 * math.pi)  # Fase aleatoria para que no pulsen todos igual
        self.glow_intensity = random.uniform(0, math.pi)  # Para el efecto de brillo
    
    def draw(self, surface):
        # Efecto de pulsación suave
        self.pulse = (self.pulse + 0.05) % (2 * math.pi)
        self.glow_intensity = (self.glow_intensity + 0.03) % (2 * math.pi)
        pulse_scale = 1.0 + math.sin(self.pulse) * 0.1
        current_size = self.size * pulse_scale
        
        # Efecto de brillo
        glow_alpha = int(128 + math.sin(self.glow_intensity) * 64)
        glow_color = (*RED, glow_alpha)
        glow_size = current_size * 1.2
        
        # Dibujar el brillo
        glow_radius = glow_size // 4
        pygame.draw.circle(surface, glow_color, (int(self.x - glow_radius), int(self.y)), int(glow_radius))
        pygame.draw.circle(surface, glow_color, (int(self.x + glow_radius), int(self.y)), int(glow_radius))
        
        glow_points = [
            (self.x - glow_size//2, self.y),
            (self.x + glow_size//2, self.y),
            (self.x, self.y + glow_size//2)
        ]
        pygame.draw.polygon(surface, glow_color, glow_points)
        
        # Dibujar el corazón principal
        radius = current_size // 4
        
        # Círculos del corazón
        pygame.draw.circle(surface, RED, (int(self.x - radius), int(self.y)), int(radius))
        pygame.draw.circle(surface, RED, (int(self.x + radius), int(self.y)), int(radius))
        
        # Triángulo de la punta
        points = [
            (self.x - current_size//2, self.y),
            (self.x + current_size//2, self.y),
            (self.x, self.y + current_size//2)
        ]
        pygame.draw.polygon(surface, RED, points)

class SlashEffect(Effect):
    def __init__(self, x, y, angle, color, size):
        super().__init__(x, y, color, size, 300)  # 300ms de duración
        self.angle = angle
        self.width = size * 3  # Largo del corte
        
    def draw(self, surface):
        progress = (pygame.time.get_ticks() - self.start_time) / self.duration
        if progress >= 1:
            return
        
        # Calcular puntos del corte
        angle_rad = math.radians(self.angle)
        dx = math.cos(angle_rad) * self.width
        dy = math.sin(angle_rad) * self.width
        
        start_x = self.x - dx/2
        start_y = self.y - dy/2
        end_x = self.x + dx/2
        end_y = self.y + dy/2
        
        # Efecto de desvanecimiento
        alpha = int(255 * (1 - progress))
        color = (*self.color, alpha)
        
        # Dibujar línea principal
        width = int(self.size * (1 - progress))
        pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), width)
        
        # Dibujar destellos en los extremos
        pygame.draw.circle(surface, color, (int(start_x), int(start_y)), width//2)
        pygame.draw.circle(surface, color, (int(end_x), int(end_y)), width//2)

class ParticleEffect(Effect):
    def __init__(self, x, y, color, count=10):
        super().__init__(x, y, color, 5, 1000)  # 1 segundo de duración
        self.particles = []
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 8)
            self.particles.append({
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': random.uniform(2, 6)
            })
    
    def draw(self, surface):
        progress = (pygame.time.get_ticks() - self.start_time) / self.duration
        if progress >= 1:
            return
            
        alpha = int(255 * (1 - progress))
        color = (*self.color, alpha)
        
        for particle in self.particles:
            # Actualizar posición
            particle['dx'] *= 0.95  # Fricción
            particle['dy'] *= 0.95
            particle['dy'] += 0.2  # Gravedad
            
            x = self.x + particle['dx'] * progress * 60
            y = self.y + particle['dy'] * progress * 60
            size = particle['size'] * (1 - progress)
            
            pygame.draw.circle(surface, color, (int(x), int(y)), int(size))

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.active = False
        self.collected = False
        self.start_time = 0
        self.duration = 0
        self.float_offset = 0
        self.float_speed = 0.1
        self.effect_text = ""  # Texto que describe el efecto
        
    def collect(self):
        self.collected = True
        self.active = True
        self.start_time = pygame.time.get_ticks()
        
    def update(self):
        if not self.collected:
            # Efecto de flotación
            self.float_offset = math.sin(pygame.time.get_ticks() * self.float_speed) * 5
            return True
            
        if not self.active:
            return False
            
        # Verificar si el powerup sigue activo
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            self.active = False
            return False
        return True
        
    def draw(self, surface):
        if self.collected:
            return
            
        # Posición con efecto de flotación
        y_pos = self.y + self.float_offset
        
        # Dibujar orbe base con brillo
        glow_radius = self.radius + 5 + abs(self.float_offset/2)
        glow_color = (*self.color, 100)  # Color con alpha para el brillo
        pygame.draw.circle(surface, glow_color, (int(self.x), int(y_pos)), glow_radius)
        pygame.draw.circle(surface, self.color, (int(self.x), int(y_pos)), self.radius)
        
        # Dibujar texto descriptivo
        text = GAME_FONT.render(self.effect_text, True, WHITE)
        text_rect = text.get_rect(center=(self.x, y_pos - self.radius - 20))
        surface.blit(text, text_rect)

class GoldenPenePowerUp(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = GOLD
        self.duration = 15000  # 10 segundos
        self.score_multiplier = 2
        self.effect_text = "x2 SCORE"
        self.glow_intensity = 0  # Para el efecto pulsante
        
    def update(self):
        if not self.collected:
            # Efecto de flotación
            self.float_offset = math.sin(pygame.time.get_ticks() * self.float_speed) * 5
            return True
            
        if not self.active:
            return False
            
        # Actualizar el efecto pulsante
        self.glow_intensity = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 255
            
        # Verificar si el powerup sigue activo
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            self.active = False
            return False
        return True

    def apply_effect(self, game):
        game.score_multiplier *= self.score_multiplier
        # Efecto visual dorado explosivo en espiral
        for i in range(12):  # 12 anillos en espiral
            angle = i * 30  # Distribuir en 360 grados
            distance = i * 20  # Incrementar distancia
            x = screen_width//2 + math.cos(math.radians(angle)) * distance
            y = screen_height//2 + math.sin(math.radians(angle)) * distance
            game.effects.append(ParticleEffect(
                x, y,
                GOLD,
                30
            ))
        # Efecto de texto flotante
        game.effects.append(FloatingTextEffect(
            screen_width//2,
            screen_height//2,
            "¡SCORE x2!",
            GOLD,
            2000,  # 2 segundos
            scale=2.0
        ))

    def remove_effect(self, game):
        game.score_multiplier //= self.score_multiplier
        # Efecto de desvanecimiento
        game.effects.append(FloatingTextEffect(
            screen_width//2,
            screen_height//2,
            "Score Normal",
            GOLD,
            1000,
            scale=1.0
        ))

class ShieldPowerUp(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = BLUE
        self.duration = 15000  # 15 segundos
        self.shield_active = False
        self.effect_text = "SHIELD"
        
    def apply_effect(self, game):
        self.shield_active = True
        game.has_shield = True
        # Efecto de escudo expandiéndose
        for radius in range(10, 100, 10):
            game.effects.append(ExpandingRingEffect(
                game.mouse_trail.positions[-1][0][0],
                game.mouse_trail.positions[-1][0][1],
                BLUE,
                radius,
                500  # 0.5 segundos
            ))
        # Efecto de texto flotante
        game.effects.append(FloatingTextEffect(
            game.mouse_trail.positions[-1][0][0],
            game.mouse_trail.positions[-1][0][1],
            "¡ESCUDO ACTIVADO!",
            BLUE,
            1500
        ))

    def remove_effect(self, game):
        self.shield_active = False
        game.has_shield = False
        # Efecto de escudo rompiéndose
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for _ in range(10):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 5)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            game.effects.append(ParticleEffect(
                mouse_x,
                mouse_y,
                BLUE,
                10
            ))

class SlowMotionPowerUp(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = (0, 255, 0)  # Verde Matrix
        self.duration = 10000  # 5 segundos
        self.slow_factor = 0.5
        self.effect_text = "SLOW-MO"
        
    def apply_effect(self, game):
        for enemy in game.enemies:
            enemy.speed *= self.slow_factor
        # Efecto matrix en cascada
        for i in range(20):  # 20 columnas de código matrix
            x = random.randint(0, screen_width)
            game.effects.append(MatrixRainEffect(
                x, 0,
                self.color,
                3000,  # 3 segundos
                screen_height
            ))
        # Efecto de texto flotante
        game.effects.append(FloatingTextEffect(
            screen_width//2,
            screen_height//2,
            "¡MATRIX MODE!",
            self.color,
            1500,
            wave=True
        ))

    def remove_effect(self, game):
        for enemy in game.enemies:
            enemy.speed /= self.slow_factor
        # Efecto de velocidad normal
        game.effects.append(FloatingTextEffect(
            screen_width//2,
            screen_height//2,
            "¡Velocidad Normal!",
            self.color,
            1000,
            wave=True
        ))

class BerserkerPowerUp(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = RED
        self.duration = 10000  # 3 segundos
        self.effect_text = "BERSERKER"
        
    def apply_effect(self, game):
        game.berserker_mode = True
        game.mouse_trail.color = RED
        game.mouse_trail.width = 10
        # Efecto de explosión en anillo
        for angle in range(0, 360, 10):  # 36 líneas de fuego
            game.effects.append(SlashEffect(
                game.mouse_trail.positions[-1][0][0],
                game.mouse_trail.positions[-1][0][1],
                angle,
                RED,
                40
            ))
        # Ondas de choque
        for radius in range(20, 200, 40):
            game.effects.append(ShockwaveEffect(
                game.mouse_trail.positions[-1][0][0],
                game.mouse_trail.positions[-1][0][1],
                RED,
                radius,
                1000  # 1 segundo
            ))
        # Efecto de texto flotante
        game.effects.append(FloatingTextEffect(
            game.mouse_trail.positions[-1][0][0],
            game.mouse_trail.positions[-1][0][1],
            "¡BERSERKER MODE!",
            RED,
            1500,
            shake=True
        ))

    def remove_effect(self, game):
        game.berserker_mode = False
        game.mouse_trail.color = BLUE
        game.mouse_trail.width = 5
        # Efecto de desactivación
        mouse_x, mouse_y = pygame.mouse.get_pos()
        game.effects.append(ShockwaveEffect(
            mouse_x,
            mouse_y,
            RED,
            100,
            500
        ))

# Nuevos efectos
class FloatingTextEffect(Effect):
    def __init__(self, x, y, text, color, duration, scale=1.0, wave=False, shake=False):
        super().__init__(x, y, color, 0, duration)
        self.text = text
        self.scale = scale
        self.wave = wave
        self.shake = shake
        
    def draw(self, surface):
        progress = (pygame.time.get_ticks() - self.start_time) / self.duration
        if progress >= 1:
            return
            
        # Calcular posición
        y_offset = -50 * progress  # Subir
        x_offset = 0
        
        if self.wave:
            x_offset = math.sin(progress * 10) * 20
        if self.shake:
            x_offset += random.randint(-3, 3)
            y_offset += random.randint(-3, 3)
            
        # Calcular alpha y escala
        alpha = int(255 * (1 - progress))
        current_scale = self.scale * (1 + math.sin(progress * math.pi) * 0.3)
        
        # Renderizar texto con efectos
        text = render_combo_text(
            self.text,
            (*self.color, alpha),
            None,
            True,
            current_scale
        )
        
        # Posicionar y dibujar
        rect = text.get_rect(center=(self.x + x_offset, self.y + y_offset))
        surface.blit(text, rect)

class ExpandingRingEffect(Effect):
    def __init__(self, x, y, color, max_radius, duration):
        super().__init__(x, y, color, max_radius, duration)
        
    def draw(self, surface):
        progress = (pygame.time.get_ticks() - self.start_time) / self.duration
        if progress >= 1:
            return
            
        radius = self.size * progress
        alpha = int(255 * (1 - progress))
        pygame.draw.circle(surface, (*self.color, alpha), (int(self.x), int(self.y)), int(radius), 2)

class ShockwaveEffect(Effect):
    def __init__(self, x, y, color, radius, duration):
        super().__init__(x, y, color, radius, duration)
        
    def draw(self, surface):
        progress = (pygame.time.get_ticks() - self.start_time) / self.duration
        if progress >= 1:
            return
            
        radius = self.size * progress
        thickness = int(10 * (1 - progress))
        alpha = int(255 * (1 - progress))
        
        pygame.draw.circle(surface, (*self.color, alpha), (int(self.x), int(self.y)), int(radius), thickness)

class MatrixRainEffect(Effect):
    def __init__(self, x, y, color, duration, height):
        super().__init__(x, y, color, 0, duration)
        self.height = height
        self.chars = []
        for i in range(0, height, 20):
            self.chars.append({
                'y': y - i,
                'char': random.choice('01'),
                'alpha': random.randint(50, 255)
            })
        
    def draw(self, surface):
        progress = (pygame.time.get_ticks() - self.start_time) / self.duration
        if progress >= 1:
            return
            
        for char in self.chars:
            char['y'] += 5
            if random.random() < 0.1:
                char['char'] = random.choice('01')
            
            text = GAME_FONT.render(char['char'], True, (*self.color, char['alpha']))
            surface.blit(text, (self.x, char['y']))

class Game:
    def __init__(self):
        self.score = 0
        self._lives = 5  # Variable privada para las vidas
        self.enemies = []
        self.spawn_timer = 0
        self.spawn_delay = 60
        self.game_over = False
        self.mouse_trail = MouseTrail()
        self.effects = []
        self.screen_shake = ScreenShake()
        self.paused = False
        self.lost_focus = False
        
        # Sistema de sonido simplificado
        self.sound_enabled = True
        try:
            music_path = resource_path(os.path.join("assets", "music", "background.mp3"))
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
            else:
                print("Archivo de música no encontrado")
                self.sound_enabled = False
        except Exception as e:
            print(f"Error al cargar la música: {e}")
            self.sound_enabled = False
        
        # Sistema de powerups
        self.powerups = []
        self.active_powerups = []
        self.powerup_spawn_timer = 0
        self.powerup_spawn_delay = 1800
        self.score_multiplier = 1
        self.has_shield = False
        self.berserker_mode = False
        
        # Sistema de combos
        self.combo_count = 0
        self.combo_multiplier = 1
        self.combo_thresholds = {
            10: 2,
            20: 3,
            40: 4,
            100: 5
        }
        
        # Crear los corazones iniciales
        self.hearts = []
        self.create_hearts()

    @property
    def lives(self):
        return self._lives

    @lives.setter
    def lives(self, value):
        old_lives = self._lives
        self._lives = value
        if old_lives != value:  # Solo actualizar si cambió el número de vidas
            self.create_hearts()

    def create_hearts(self):
        """Crea los corazones que representan las vidas del jugador"""
        self.hearts = []
        heart_spacing = 50  # Aumentado para más espacio entre corazones
        heart_size = 35    # Tamaño ligeramente más grande
        
        # Si hay más de 5 vidas, mostrar un contador
        if self._lives > 5:
            # Crear un corazón centrado
            x = screen_width // 2 - heart_spacing  # Un poco a la izquierda del centro
            y = screen_height - 60  # Un poco más arriba del borde inferior
            self.hearts.append(Heart(x, y, heart_size))
            self.show_lives_counter = True
        else:
            # Crear hasta 5 corazones
            total_width = min(self._lives, 5) * heart_spacing
            start_x = (screen_width - total_width) // 2  # Centrar horizontalmente
            y = screen_height - 60  # Un poco más arriba del borde inferior
            
            for i in range(self._lives):
                x = start_x + (i * heart_spacing)
                self.hearts.append(Heart(x, y, heart_size))
            self.show_lives_counter = False

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        if self.sound_enabled:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

    def update(self):
        if self.game_over or self.paused:
            return

        self.spawn_timer -= 1
        self.spawn_enemy()
        self.update_powerups()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.check_powerup_collision(mouse_x, mouse_y)

        # Comprobar colisiones con balas
        for enemy in self.enemies:
            if isinstance(enemy, ShooterEnemy):
                for projectile in enemy.projectiles[:]:
                    if projectile.check_collision(mouse_x, mouse_y):
                        if self.has_shield:
                            if self.sound_enabled:
                                play_sound('shield_break')
                            self.has_shield = False
                            self.effects.append(ParticleEffect(
                                mouse_x, mouse_y,
                                BLUE,
                                30
                            ))
                            for powerup in self.active_powerups[:]:
                                if isinstance(powerup, ShieldPowerUp):
                                    powerup.remove_effect(self)
                                    self.active_powerups.remove(powerup)
                                    break
                        else:
                            if self.sound_enabled:
                                play_sound('hit')
                            self.lives -= 1
                            self.reset_combo()
                            self.effects.append(ParticleEffect(
                                mouse_x, mouse_y,
                                (255, 100, 0),  # Color naranja para las balas
                                20
                            ))
                            self.screen_shake.start(20, 5)
                            if self.lives <= 0:
                                if self.sound_enabled:
                                    play_sound('game_over')
                                self.game_over = True
                        projectile.active = False
                        enemy.projectiles.remove(projectile)

        for enemy in self.enemies[:]:
            collision_result = enemy.update(mouse_x, mouse_y)
            
            if collision_result == "body_collision" or (self.berserker_mode and collision_result):
                if self.sound_enabled:
                    play_sound('slash')
                self.enemies.remove(enemy)
                self.score += 1000 * self.combo_multiplier * self.score_multiplier
                self.combo_count += 1
                self.update_combo()
                
                slash_angle = enemy.angle + random.uniform(-30, 30)
                slash_color = RED if self.berserker_mode else BLUE
                self.effects.append(SlashEffect(
                    enemy.x, enemy.y,
                    slash_angle,
                    slash_color,
                    20
                ))
                self.effects.append(ParticleEffect(
                    enemy.x, enemy.y,
                    slash_color,
                    15
                ))
            
            elif collision_result == "head_collision":
                if self.has_shield:
                    if self.sound_enabled:
                        play_sound('shield_break')
                    self.has_shield = False
                    self.effects.append(ParticleEffect(
                        mouse_x, mouse_y,
                        BLUE,
                        30
                    ))
                    for powerup in self.active_powerups[:]:
                        if isinstance(powerup, ShieldPowerUp):
                            powerup.remove_effect(self)
                            self.active_powerups.remove(powerup)
                            break
                else:
                    if self.sound_enabled:
                        play_sound('hit')
                    self.enemies.remove(enemy)
                    self.lives -= 1
                    self.reset_combo()
                    self.effects.append(ParticleEffect(
                        mouse_x, mouse_y,
                        RED,
                        20
                    ))
                    self.screen_shake.start(20, 5)
                    if self.lives <= 0:
                        if self.sound_enabled:
                            play_sound('game_over')
                        self.game_over = True

        self.mouse_trail.update((mouse_x, mouse_y))
        self.effects = [effect for effect in self.effects if effect.update()]

    def draw(self, surface):
        # Crear superficie temporal con alpha
        temp_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        temp_surface.fill((0, 0, 0, 0))  # Limpiar con transparencia

        # Dibujar la estela del ratón
        self.mouse_trail.draw(temp_surface)

        # Dibujar enemigos
        for enemy in self.enemies:
            enemy.draw(temp_surface)

        # Dibujar powerups
        for powerup in self.powerups:
            powerup.draw(temp_surface)

        # Dibujar efectos
        for effect in self.effects:
            effect.draw(temp_surface)

        # Dibujar corazones y contador de vidas
        for heart in self.hearts:
            heart.draw(temp_surface)
        
        # Si hay más de 5 vidas, mostrar el contador
        if hasattr(self, 'show_lives_counter') and self.show_lives_counter:
            lives_text = render_combo_text(
                f'x{self.lives}',
                RED,
                WHITE,  # Agregar borde blanco
                True,   # Con brillo
                1.2     # Un poco más grande
            )
            lives_rect = lives_text.get_rect(midleft=(screen_width//2 + 10, screen_height - 60))
            temp_surface.blit(lives_text, lives_rect)

        # Dibujar puntuación con efecto dorado si está activo
        golden_active = False
        for powerup in self.active_powerups:
            if isinstance(powerup, GoldenPenePowerUp):
                golden_active = True
                break

        if golden_active:
            # Usar render_combo_text para el efecto dorado
            score_text = render_combo_text(
                f'{self.score:08d}',
                GOLD,
                None,  # sin borde
                True,  # con glow
                1.0 + abs(math.sin(pygame.time.get_ticks() * 0.003)) * 0.2  # escala pulsante
            )
        else:
            score_text = SCORE_FONT.render(f'{self.score:08d}', True, WHITE)
        
        score_rect = score_text.get_rect(midtop=(screen_width//2, 20))
        temp_surface.blit(score_text, score_rect)

        # Dibujar combo solo si es mayor a 0
        if self.combo_count > 0:
            combo_style = COMBO_STYLES.get(self.combo_multiplier, COMBO_STYLES[1])
            combo_text = render_combo_text(
                f'x{self.combo_multiplier}',
                combo_style['color'],
                combo_style['border_color'],
                combo_style['glow'],
                combo_style['scale']
            )
            combo_rect = combo_text.get_rect(midtop=(screen_width//2, score_rect.bottom + 10))
            
            if combo_style['shake']:
                combo_rect.x += random.randint(-2, 2)
                combo_rect.y += random.randint(-2, 2)
            
            temp_surface.blit(combo_text, combo_rect)
            
            # Dibujar contador de combo debajo
            count_style = combo_style.copy()
            count_style['scale'] *= 0.7
            combo_count_text = render_combo_text(
                str(self.combo_count),
                combo_style['color'],
                combo_style['border_color'],
                combo_style['glow'],
                count_style['scale']
            )
            count_rect = combo_count_text.get_rect(midtop=(screen_width//2, combo_rect.bottom + 5))
            temp_surface.blit(combo_count_text, count_rect)

        # Dibujar mensaje de pausa
        if self.paused:
            # Crear una capa semi-transparente negra
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            temp_surface.blit(overlay, (0, 0))
            
            # Renderizar texto de PAUSA con efecto
            pause_text = render_combo_text(
                "PAUSED",
                GOLD,
                WHITE,
                True,
                1.5
            )
            pause_rect = pause_text.get_rect(center=(screen_width//2, screen_height//2))
            temp_surface.blit(pause_text, pause_rect)

        # Dibujar mensaje de game over
        if self.game_over:
            # Crear una capa semi-transparente negra
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 192))  # Más oscuro que la pausa
            temp_surface.blit(overlay, (0, 0))
            
            # Renderizar GAME OVER con efecto
            game_over_text = render_combo_text(
                "GAME OVER",
                RED,
                None,
                True,
                2.0
            )
            restart_text = render_combo_text(
                "Presiona R para reiniciar",
                WHITE,
                None,
                True,
                1.0
            )
            
            game_over_rect = game_over_text.get_rect(center=(screen_width//2, screen_height//2 - 50))
            restart_rect = restart_text.get_rect(center=(screen_width//2, screen_height//2 + 50))
            
            temp_surface.blit(game_over_text, game_over_rect)
            temp_surface.blit(restart_text, restart_rect)

        # Aplicar screen shake solo si está activo
        shake_offset = self.screen_shake.get_offset()
        if shake_offset != (0, 0):
            surface.fill((0, 0, 0, 0))  # Limpiar la superficie principal
            surface.blit(temp_surface, shake_offset)
        else:
            surface.fill((0, 0, 0, 0))
            surface.blit(temp_surface, (0, 0))

    def update_combo(self):
        """Actualiza el multiplicador de combo basado en el contador actual"""
        old_multiplier = self.combo_multiplier
        for threshold, multiplier in sorted(self.combo_thresholds.items()):
            if self.combo_count >= threshold:
                self.combo_multiplier = multiplier
        
        if self.combo_multiplier > old_multiplier:
            if self.sound_enabled:
                play_sound('combo')
            # Efecto visual para el nuevo multiplicador
            self.effects.append(FloatingTextEffect(
                screen_width//2,
                screen_height//2,
                f"¡COMBO x{self.combo_multiplier}!",
                GOLD,
                1500,
                scale=1.5,
                shake=True
            ))

    def reset_combo(self):
        """Reinicia el contador y multiplicador de combo"""
        self.combo_count = 0
        self.combo_multiplier = 1

    def spawn_enemy(self):
        """Genera nuevos enemigos basados en el temporizador"""
        if self.spawn_timer <= 0:
            # Probabilidades de spawn para cada tipo de enemigo
            enemy_types = [
                (NormalEnemy, 0.4),
                (SplitEnemy, 0.2),
                (ShooterEnemy, 0.2),
                (FastEnemy, 0.2)
            ]
            
            # Seleccionar tipo de enemigo basado en probabilidades
            total_prob = sum(prob for _, prob in enemy_types)
            r = random.uniform(0, total_prob)
            cumulative = 0
            selected_type = None
            
            for enemy_type, prob in enemy_types:
                cumulative += prob
                if r <= cumulative:
                    selected_type = enemy_type
                    break
            
            if selected_type:
                self.enemies.append(selected_type())
            
            # Reducir el delay de spawn gradualmente
            self.spawn_delay = max(30, self.spawn_delay - 0.1)
            self.spawn_timer = self.spawn_delay

    def update_powerups(self):
        """Actualiza el sistema de powerups"""
        # Actualizar temporizador de spawn
        self.powerup_spawn_timer -= 1
        if self.powerup_spawn_timer <= 0:
            # Probabilidades de spawn para cada tipo de powerup
            powerup_types = [
                (ShieldPowerUp, 0.3),
                (SlowMotionPowerUp, 0.3),
                (BerserkerPowerUp, 0.2),
                (GoldenPenePowerUp, 0.2)
            ]
            
            # Seleccionar tipo de powerup
            total_prob = sum(prob for _, prob in powerup_types)
            r = random.uniform(0, total_prob)
            cumulative = 0
            selected_type = None
            
            for powerup_type, prob in powerup_types:
                cumulative += prob
                if r <= cumulative:
                    selected_type = powerup_type
                    break
            
            if selected_type:
                # Generar en una posición aleatoria dentro de la pantalla
                x = random.randint(100, screen_width - 100)
                y = random.randint(100, screen_height - 100)
                self.powerups.append(selected_type(x, y))
            
            self.powerup_spawn_timer = self.powerup_spawn_delay
        
        # Actualizar powerups activos
        for powerup in self.active_powerups[:]:
            if not powerup.update():
                powerup.remove_effect(self)
                self.active_powerups.remove(powerup)
        
        # Actualizar powerups en el campo
        for powerup in self.powerups[:]:
            if not powerup.update():
                self.powerups.remove(powerup)

    def check_powerup_collision(self, mouse_x, mouse_y):
        """Comprueba si el jugador recoge algún powerup"""
        for powerup in self.powerups[:]:
            dx = mouse_x - powerup.x
            dy = mouse_y - powerup.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < powerup.radius:
                if self.sound_enabled:
                    play_sound('powerup')
                powerup.collect()
                powerup.apply_effect(self)
                self.active_powerups.append(powerup)
                self.powerups.remove(powerup)

    def toggle_pause(self):
        """Alterna el estado de pausa del juego"""
        self.paused = not self.paused
        if self.paused:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()

def main():
    clock = pygame.time.Clock()
    game = Game()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if sys.platform == 'win32':
                    win32gui.ReleaseCapture()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if sys.platform == 'win32':
                        win32gui.ReleaseCapture()
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r and game.game_over:
                    game = Game()
                elif event.key == pygame.K_p and not game.game_over:
                    game.toggle_pause()
                elif event.key == pygame.K_m:  # Tecla M para mutear/desmutear
                    game.toggle_sound()
            elif event.type == pygame.ACTIVEEVENT:
                if event.state == 2:  # Estado de foco de ventana
                    if not event.gain:  # Perdió el foco
                        game.paused = True
                        game.lost_focus = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game.paused and game.lost_focus:
                    game.paused = False
                    game.lost_focus = False

        if not game.game_over and not game.paused:
            game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()