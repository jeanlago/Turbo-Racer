import pygame, math, os

os.environ["SDL_AUDIODRIVER"] = "dummy"  # evita travar áudio em PCs sem saída de som
pygame.init()

# ---------- Tela ----------
WIDTH, HEIGHT = 1024, 768
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Corrida com Pista de Imagem")

clock = pygame.time.Clock()
FPS = 60

# ---------- Paths ----------
BASE_DIR = os.path.dirname(__file__)
SPRITE_DIR = os.path.join(BASE_DIR, "assets", "images", "car_sprites")   # red.png / blue.png (apontando para CIMA)
TRACK_IMAGE_PATH = os.path.join(BASE_DIR, "assets", "images", "maps", "Map_1.png")

# ---------- Pista / Cores ----------
# Paleta “permitida” (se usar uma pista com tons planos). Mantemos, mas também
# adicionamos um detector por HSV para asfalto escuro com pouca saturação.
TRACK_COLORS = [(31, 23, 38), (0, 0, 0), (240, 224, 0), (144, 105, 0)]
COLOR_TOLERANCE = 18  # tolerância de paleta (para antialiasing)

# Parámetros de detecção HSV para "asfalto"
HSV_S_MAX = 45   # pouca saturação
HSV_V_MAX = 55   # escuro

def color_close_to_any(rgb, palette, tol=0):
    r, g, b = rgb
    for pr, pg, pb in palette:
        if abs(r - pr) <= tol and abs(g - pg) <= tol and abs(b - pb) <= tol:
            return True
    return False

def is_asphalt_hsv(rgb):
    c = pygame.Color(*rgb)
    h, s, v, _ = c.hsva  # 0..360, 0..100, 0..100
    return (s <= HSV_S_MAX and v <= HSV_V_MAX)

def is_track_pixel(surface, x, y):
    if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
        return False
    rgb = surface.get_at((x, y))[:3]
    # Aceita se estiver próximo da paleta OU se passar no filtro de asfalto por HSV
    return color_close_to_any(rgb, TRACK_COLORS, COLOR_TOLERANCE) or is_asphalt_hsv(rgb)

# ---------- Carro ----------
class Car:
    def __init__(self, x, y, color_prefix, controls):
        """
        controls: (accelerate, right, left, brake_or_reverse)
        """
        self.x = float(x)
        self.y = float(y)
        self.angle = 0.0          # 0° = aponta para a direita; sprite aponta para CIMA -> usamos (angle - 90) no movimento
        self.speed = 0.0
        self.controls = controls

        path = os.path.join(SPRITE_DIR, f"{color_prefix}.png")
        self.sprite_base = pygame.image.load(path).convert_alpha()

        # Física
        self.MAX_SPEED_FWD = 6.0      # px/frame (≈ 360 px/s)
        self.MAX_SPEED_REV = -2.0
        self.ACCEL = 0.08             # aceleração pra frente
        self.BRAKE = 0.14              # freio/marcha-ré (aumenta módulo reduzindo rapidamente)
        self.FRICTION = 0.985          # atrito geral
        self.STEER_MAX = 3.0           # limite de giro por frame

    def draw(self, win):
        # Rotaciona sprite: -angle (horário positivo)
        rotated_sprite = pygame.transform.rotate(self.sprite_base, -self.angle)
        rect = rotated_sprite.get_rect(center=(self.x, self.y))
        win.blit(rotated_sprite, rect.topleft)

    def _move_forward_vector(self):
        # Sprite aponta para CIMA => direção de avanço é (angle - 90)
        rad = math.radians(self.angle - 90.0)
        return math.cos(rad), math.sin(rad)

    def update(self, keys, mask_surface):
        old_x, old_y = self.x, self.y

        # --- Aceleração / Freio ---
        if keys[self.controls[0]]:  # acelerar
            self.speed = min(self.speed + self.ACCEL, self.MAX_SPEED_FWD)
        elif keys[self.controls[3]]:  # freio/marcha-ré
            # Se estiver andando pra frente, freia forte; se já estiver quase parado, permite ré
            if self.speed > 0.2:
                self.speed = max(0.0, self.speed - self.BRAKE)
            else:
                self.speed = max(self.MAX_SPEED_REV, self.speed - (self.BRAKE * 0.5))
        else:
            # Atrito natural
            self.speed *= self.FRICTION
            if abs(self.speed) < 0.01:
                self.speed = 0.0

        # --- Direção (escala com a velocidade) ---
        # Quase não vira parado, vira mais quando está rápido.
        steer_factor = min(abs(self.speed) * 0.5, self.STEER_MAX)
        if keys[self.controls[1]]:  # right
            self.angle += steer_factor
        if keys[self.controls[2]]:  # left
            self.angle -= steer_factor

        # Mantém ângulo em [-180, 180] para evitar números grandes
        if self.angle > 180: self.angle -= 360
        if self.angle < -180: self.angle += 360

        # --- Movimento ---
        fx, fy = self._move_forward_vector()
        self.x += self.speed * fx
        self.y += self.speed * fy

        # --- Colisão: checa alguns pontos ao redor do centro (frente/lados/centro) ---
        cx, cy = int(self.x), int(self.y)
        collided = False
        sample_offsets = [(0, 0), (12, 0), (-12, 0), (0, 12), (0, -12)]
        # rotaciona offsets pro ângulo atual
        cos_a = math.cos(math.radians(self.angle - 90))
        sin_a = math.sin(math.radians(self.angle - 90))
        for ox, oy in sample_offsets:
            rx = int(cx + ox * cos_a - oy * sin_a)
            ry = int(cy + ox * sin_a + oy * cos_a)
            if not is_track_pixel(mask_surface, rx, ry):
                collided = True
                break

        if collided:
            # Reverte movimento e dá um recuo leve
            self.x, self.y = old_x, old_y
            self.speed = -abs(self.speed) * 0.4
            if self.speed < self.MAX_SPEED_REV:
                self.speed = self.MAX_SPEED_REV

        # Limites de tela
        self.x = max(0.0, min(WIDTH * 1.0, self.x))
        self.y = max(0.0, min(HEIGHT * 1.0, self.y))

# ---------- Setup carros ----------
# Controles: (acelera, direita, esquerda, freia/ré)
car1 = Car(570, 145, "red",  (pygame.K_w, pygame.K_d, pygame.K_a, pygame.K_s))
car2 = Car(570, 190, "blue", (pygame.K_UP, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_DOWN))

# ---------- Pista ----------
track_image = pygame.image.load(TRACK_IMAGE_PATH).convert()
if track_image.get_width() != WIDTH or track_image.get_height() != HEIGHT:
    track_image = pygame.transform.smoothscale(track_image, (WIDTH, HEIGHT))
mask_surface = track_image.copy()  # usamos a própria imagem como "máscara flexível" (HSV + paleta)

# ---------- Loop principal ----------
def main():
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()

        car1.update(keys, mask_surface)
        car2.update(keys, mask_surface)

        win.blit(track_image, (0, 0))
        car1.draw(win)
        car2.draw(win)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
