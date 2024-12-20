import pygame
import sys
import random
import math
import os

# Inicializar Pygame
pygame.init()

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
        # Intentar poner la ventana al frente de manera segura
        current_thread = win32api.GetCurrentThreadId()
        foreground_thread = win32api.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[0]
        win32api.AttachThreadInput(current_thread, foreground_thread, True)
        win32gui.SetForegroundWindow(hwnd)
        win32api.AttachThreadInput(current_thread, foreground_thread, False)
    except Exception as e:
        print(f"No se pudo poner la ventana al frente: {e}")
else:
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME | pygame.SRCALPHA)

pygame.display.set_caption("Ninja Mouse")

# Colores (ajustados para mejor visibilidad con alpha)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
SALMON = (255, 160, 160)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 140, 0)
PURPLE = (160, 32, 240)
GOLD = (255, 215, 0)

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

def resource_path(relative_path):
    """ Obtener la ruta absoluta a los recursos, funciona para dev y para PyInstaller """
    try:
        # PyInstaller crea un directorio temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Modificar la sección de carga de fuentes:
font_paths = [
    resource_path(os.path.join("assets", "PressStart2P-Regular.ttf")),
]

GAME_FONT = None
SCORE_FONT = None

for font_path in font_paths:
    try:
        GAME_FONT = pygame.font.Font(font_path, 36)
        SCORE_FONT = pygame.font.Font(font_path, 48)
        print(f"Fuente cargada desde: {font_path}")
        break
    except Exception as e:
        print(f"No se pudo cargar la fuente desde {font_path}: {e}")
        continue

if not GAME_FONT or not SCORE_FONT:
    print("No se pudo cargar la fuente Press Start 2P, usando fuente por defecto")
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

class Enemy:
    def __init__(self):
        # Dimensiones totales
        self.width = 60  # Largo total
        self.height = 20  # Ancho total
        self.head_size = 20  # Tamaño de la cabeza (cuadrada)
        
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
        self.speed = 2  # Velocidad reducida (antes era 3)
        self.rotation_speed = 4  # Velocidad de rotación aumentada (antes era 2)

    def move(self, target_x, target_y):
        # Calcular dirección hacia el mouse
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Calcular el ángulo objetivo hacia el mouse
        self.target_angle = math.degrees(math.atan2(dy, dx))
        
        # Ajustar el ángulo actual gradualmente hacia el ángulo objetivo
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
        body = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Dibujar el cuerpo con alpha
        pygame.draw.rect(body, (*SALMON, 200), (0, 0, self.width - self.head_size, self.height))
        
        # Dibujar la cabeza con alpha y forma más definida
        head_surface = pygame.Surface((self.head_size, self.height), pygame.SRCALPHA)
        
        # Dibujar la cabeza como un trapecio
        head_points = [
            (0, 0),  # Esquina superior izquierda
            (self.head_size, self.height * 0.15),  # Esquina superior derecha (más estrecha)
            (self.head_size, self.height * 0.85),  # Esquina inferior derecha (más estrecha)
            (0, self.height)  # Esquina inferior izquierda
        ]
        pygame.draw.polygon(head_surface, (*RED, 200), head_points)
        
        # Agregar la cabeza al cuerpo
        body.blit(head_surface, (self.width - self.head_size, 0))
        
        # Rotar superficie
        rotated = pygame.transform.rotate(body, -self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect)

    def check_body_collision(self, mouse_x, mouse_y):
        # Convertir coordenadas del mouse al espacio local del enemigo
        angle_rad = math.radians(self.angle)
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        
        # Rotar el punto del mouse al espacio local del rectángulo
        rotated_x = dx * math.cos(-angle_rad) - dy * math.sin(-angle_rad)
        rotated_y = dx * math.sin(-angle_rad) + dy * math.cos(-angle_rad)
        
        # Definir las zonas de colisión del cuerpo
        body_width = self.width - self.head_size
        
        # Zona principal del cuerpo (más ancha en el centro)
        in_body_x = rotated_x < 0 and abs(rotated_x) < body_width/2
        in_body_y = abs(rotated_y) < self.height/2
        
        # Zona de corte efectivo (más grande cuando el corte es perpendicular)
        cut_angle = abs(math.degrees(math.atan2(rotated_y, rotated_x)) % 180 - 90)
        cut_threshold = self.height * (1 + math.sin(math.radians(cut_angle)))
        
        return in_body_x and abs(rotated_y) < cut_threshold

    def check_head_collision(self, mouse_x, mouse_y):
        # Convertir coordenadas del mouse al espacio local del enemigo
        angle_rad = math.radians(self.angle)
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        
        # Rotar el punto del mouse al espacio local del rectángulo
        rotated_x = dx * math.cos(-angle_rad) - dy * math.sin(-angle_rad)
        rotated_y = dx * math.sin(-angle_rad) + dy * math.cos(-angle_rad)
        
        # Definir la zona de la cabeza con una forma más precisa y generosa
        head_start = (self.width - self.head_size)
        
        # Crear una zona de colisión más amplia en forma de trapecio
        head_width_base = self.height  # Base más ancha en la parte trasera de la cabeza
        head_width_tip = self.height * 0.7  # Más estrecho en la punta
        
        # Calcular el ancho de la zona de colisión en el punto actual
        progress = (rotated_x - head_start) / self.head_size
        if 0 <= progress <= 1:
            current_width = head_width_base * (1 - progress) + head_width_tip * progress
            # Zona de colisión más generosa cerca de la punta
            if progress > 0.7:  # Últimos 30% de la cabeza
                current_width *= 1.3  # 30% más ancha en la punta
            
            # Comprobar si el punto está dentro del trapecio
            return abs(rotated_y) < current_width/2
        
        return False

    def update(self, mouse_x, mouse_y):
        # Nuevo método para actualizar la posición y comprobar colisiones
        self.move(mouse_x, mouse_y)
        
        # Comprobar colisiones y devolver el resultado
        if self.check_head_collision(mouse_x, mouse_y):
            return "head_collision"
        elif self.check_body_collision(mouse_x, mouse_y):
            return "body_collision"
        return None

class MouseTrail:
    def __init__(self):
        self.positions = []  # Lista de posiciones anteriores del mouse
        self.max_length = 20  # Longitud base de la estela aumentada
        self.last_pos = None
        self.last_time = pygame.time.get_ticks()
        self.base_width = 8  # Ancho base de la estela

    def update(self, pos):
        current_time = pygame.time.get_ticks()
        speed = 0  # Inicializar speed con un valor por defecto
        
        if self.last_pos:
            dx = pos[0] - self.last_pos[0]
            dy = pos[1] - self.last_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            dt = current_time - self.last_time
            speed = distance / dt if dt > 0 else 0
            
            # Hacer la estela más reactiva a la velocidad
            self.max_length = int(20 + speed * 1.2)  # Más larga
        
        # Calcular el ancho basado en la velocidad
        width = min(self.base_width + speed * 0.3, 20)
        self.positions.append((pos, width))  # Guardar posición y ancho
        
        if len(self.positions) > self.max_length:
            self.positions.pop(0)
        
        self.last_pos = pos
        self.last_time = current_time

    def draw(self, surface):
        if len(self.positions) < 2:
            return
        
        # Dibujar la estela con degradado y ancho variable
        for i in range(len(self.positions) - 1):
            alpha = int(200 * (i / len(self.positions)))  # Más opaco
            color = (*BLUE, alpha)
            start_pos, start_width = self.positions[i]
            end_pos, end_width = self.positions[i + 1]
            
            # Dibujar línea gruesa usando múltiples líneas
            width = (start_width + end_width) / 2
            pygame.draw.line(surface, color, start_pos, end_pos, int(width))

class ScreenShake:
    def __init__(self):
        self.duration = 0
        self.intensity = 0
        
    def start(self, duration, intensity):
        self.duration = duration
        self.intensity = intensity
        
    def get_offset(self):
        if self.duration <= 0:
            return 0, 0
        
        self.duration -= 1
        dx = random.randint(-self.intensity, self.intensity)
        dy = random.randint(-self.intensity, self.intensity)
        return dx, dy

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
    
    def draw(self, surface):
        # Dibujar un corazón usando pygame
        radius = self.size // 4
        
        # Crear los círculos que forman el corazón
        pygame.draw.circle(surface, RED, (self.x - radius, self.y), radius)
        pygame.draw.circle(surface, RED, (self.x + radius, self.y), radius)
        
        # Crear el triángulo que forma la punta del corazón
        points = [
            (self.x - self.size//2, self.y),
            (self.x + self.size//2, self.y),
            (self.x, self.y + self.size//2)
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

class Game:
    def __init__(self):
        self.score = 0
        self.lives = 3
        self.enemies = []
        self.spawn_timer = 0
        self.spawn_delay = 60
        self.game_over = False
        self.mouse_trail = MouseTrail()
        self.effects = []
        self.screen_shake = ScreenShake()
        self.paused = False
        self.lost_focus = False
        
        # Sistema de combos
        self.combo_count = 0
        self.combo_multiplier = 1
        self.combo_thresholds = {
            10: 2,   # 10 penes = x2
            20: 3,   # 20 penes = x3
            40: 4,   # 40 penes = x4
            100: 5   # 100 penes = x5
        }
        
        # Crear los corazones centrados en la parte inferior
        heart_spacing = 50
        total_width = heart_spacing * 2
        start_x = (screen_width - total_width) // 2
        self.hearts = [
            Heart(start_x + i * heart_spacing, screen_height - 50)
            for i in range(3)
        ]

    def toggle_pause(self):
        self.paused = not self.paused

    def draw_pause_menu(self, surface):
        # Crear una capa semi-transparente negra
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))
        
        # Renderizar texto de PAUSA con efecto
        pause_text = render_combo_text(
            "PAUSED",
            GOLD,
            WHITE,
            True,
            1.5
        )
        pause_rect = pause_text.get_rect(center=(screen_width//2, screen_height//2 - 50))
        surface.blit(pause_text, pause_rect)
        
        # Instrucciones
        if self.lost_focus:
            resume_text = GAME_FONT.render("Click to resume", True, WHITE)
        else:
            resume_text = GAME_FONT.render("Press P to resume", True, WHITE)
        resume_rect = resume_text.get_rect(center=(screen_width//2, screen_height//2 + 50))
        surface.blit(resume_text, resume_rect)

    def update_combo(self):
        # Actualizar multiplicador basado en el combo actual
        for threshold, multiplier in sorted(self.combo_thresholds.items(), reverse=True):
            if self.combo_count >= threshold:
                if self.combo_multiplier != multiplier:
                    self.combo_multiplier = multiplier
                    # Efecto visual cuando se alcanza un nuevo multiplicador
                    self.effects.append(ParticleEffect(
                        screen_width//2, 50,  # Posición arriba del score
                        COMBO_STYLES[multiplier]['color'],  # Color del combo
                        30  # Más partículas para celebrar
                    ))
                break

    def reset_combo(self):
        self.combo_count = 0
        self.combo_multiplier = 1

    def spawn_enemy(self):
        if self.spawn_timer <= 0:
            self.enemies.append(Enemy())
            self.spawn_timer = self.spawn_delay

    def update(self):
        self.spawn_timer -= 1
        self.spawn_enemy()

        mouse_x, mouse_y = pygame.mouse.get_pos()

        for enemy in self.enemies[:]:
            collision_result = enemy.update(mouse_x, mouse_y)
            
            if collision_result == "body_collision":
                self.enemies.remove(enemy)
                # Aumentar score con multiplicador
                self.score += 1000 * self.combo_multiplier
                # Incrementar combo
                self.combo_count += 1
                self.update_combo()
                
                # Efecto de corte
                slash_angle = enemy.angle + random.uniform(-30, 30)
                self.effects.append(SlashEffect(
                    enemy.x, enemy.y,
                    slash_angle,
                    BLUE,
                    20
                ))
                
                # Partículas de corte
                self.effects.append(ParticleEffect(
                    enemy.x, enemy.y,
                    BLUE,
                    15
                ))
            
            elif collision_result == "head_collision":
                self.enemies.remove(enemy)
                self.lives -= 1
                # Resetear combo al ser golpeado
                self.reset_combo()
                
                # Efecto de daño con partículas rojas
                self.effects.append(ParticleEffect(
                    mouse_x, mouse_y,
                    RED,
                    20
                ))
                
                # Vibración de pantalla más intensa
                self.screen_shake.start(45, 15)  # Más duración e intensidad
                
                if self.lives <= 0:
                    self.game_over = True

        self.mouse_trail.update((mouse_x, mouse_y))
        self.effects = [effect for effect in self.effects if effect.update()]

    def draw(self, surface):
        # Crear superficie temporal con alpha
        temp_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        temp_surface.fill((0,0,0,0))
        
        # Dibujar todos los elementos del juego normalmente
        for enemy in self.enemies:
            enemy.draw(temp_surface)
        
        # Dibujar puntuación centrada arriba
        score_text = SCORE_FONT.render(f'{self.score:08d}', True, WHITE)
        score_rect = score_text.get_rect(midtop=(screen_width//2, 20))
        temp_surface.blit(score_text, score_rect)
        
        # Obtener el estilo del combo actual
        style = COMBO_STYLES[self.combo_multiplier]
        
        # Renderizar el multiplicador con efectos
        combo_text = render_combo_text(
            f'x{self.combo_multiplier}{"!" * (self.combo_multiplier-1)}',
            style['color'],
            style['border_color'],
            style['glow'],
            style['scale']
        )
        
        # Posicionar el multiplicador
        combo_rect = combo_text.get_rect(midtop=(screen_width//2, 70))
        
        # Agregar shake si corresponde
        if style['shake']:
            shake_offset = (
                random.randint(-2, 2),
                random.randint(-2, 2)
            )
            combo_rect.x += shake_offset[0]
            combo_rect.y += shake_offset[1]
        
        temp_surface.blit(combo_text, combo_rect)
        
        # Renderizar el contador de combo
        count_style = style.copy()
        count_style['scale'] *= 0.7
        combo_count_text = render_combo_text(
            f'{self.combo_count}',
            style['color'],
            style['border_color'],
            style['glow'],
            count_style['scale']
        )
        combo_count_rect = combo_count_text.get_rect(midtop=(screen_width//2, combo_rect.bottom + 10))
        temp_surface.blit(combo_count_text, combo_count_rect)
        
        # Dibujar corazones
        for i in range(self.lives):
            self.hearts[i].draw(temp_surface)
        
        if self.game_over:
            game_over_text = GAME_FONT.render('GAME OVER', True, RED)
            text_rect = game_over_text.get_rect(center=(screen_width//2, screen_height//2))
            temp_surface.blit(game_over_text, text_rect)
            
            restart_text = GAME_FONT.render('PRESS R TO RESTART', True, WHITE)
            restart_rect = restart_text.get_rect(center=(screen_width//2, screen_height//2 + 50))
            temp_surface.blit(restart_text, restart_rect)
        
        # Dibujar efectos
        self.mouse_trail.draw(temp_surface)
        for effect in self.effects:
            effect.draw(temp_surface)
        
        # Aplicar vibración de pantalla
        shake_offset = self.screen_shake.get_offset()
        surface.fill(BLACK)
        surface.blit(temp_surface, shake_offset)
        
        # Dibujar menú de pausa si está pausado
        if self.paused:
            self.draw_pause_menu(surface)

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