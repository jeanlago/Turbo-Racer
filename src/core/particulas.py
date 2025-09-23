# src/core/particulas.py
import math, random, pygame
from config import CAMINHO_FUMACA

class Particula:
    __slots__ = ("x","y","vx","vy","life","t","ang","scale0","scale1","alpha0","alpha1")
    def __init__(self, x, y, vx, vy, life, ang, scale0, scale1, alpha0, alpha1):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = float(vx), float(vy)
        self.life = float(life)
        self.t = 0.0
        self.ang = float(ang)
        self.scale0, self.scale1 = float(scale0), float(scale1)
        self.alpha0, self.alpha1 = int(alpha0), int(alpha1)

    def alive(self): return self.t < self.life
    def update(self, dt):
        self.t += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
    def interp(self):
        k = max(0.0, min(1.0, self.t / self.life))
        scale = self.scale0 + (self.scale1 - self.scale0) * k
        alpha = int(self.alpha0 + (self.alpha1 - self.alpha0) * k)
        return scale, alpha

class EmissorFumaca:
    def __init__(self):
        self.tex = pygame.image.load(CAMINHO_FUMACA).convert_alpha()
        self.ps = []
        self._accum = 0.0
        self.max_particulas = 50  # Reduzido ainda mais para melhor performance
        self._particulas_por_frame = 2  # Máximo de partículas crIAdas por frame

    def spawn(self, x, y, dirx, diry, taxa_qps, dt):
        # Limitar número de partículas para performance
        if len(self.ps) >= self.max_particulas:
            return
            
        self._accum += taxa_qps * dt
        n = int(self._accum)
        if n <= 0: return
        self._accum -= n
        
        # Limitar número de partículas crIAdas por frame
        n = min(n, self._particulas_por_frame)
        
        base_ang = math.atan2(diry, dirx) + math.pi
        for _ in range(n):
            # Verificar limite novamente dentro do loop
            if len(self.ps) >= self.max_particulas:
                break
                
            ang = base_ang + random.uniform(-0.6, 0.6)
            v = random.uniform(20, 80)
            vx, vy = math.cos(ang)*v, math.sin(ang)*v
            life = random.uniform(0.35, 0.8)
            scale0 = random.uniform(0.25, 0.45)
            scale1 = scale0 * random.uniform(2.0, 3.2)
            alpha0 = random.randint(160, 220)
            p = Particula(x, y, vx, vy, life, random.uniform(0,360), scale0, scale1, alpha0, 0)
            self.ps.append(p)

    def update(self, dt):
        # Otimização: usar list comprehension mais eficiente
        self.ps = [p for p in self.ps if p.alive() and p.update(dt)]

    def draw(self, surface, camera=None):
        # Otimização: pré-calcular zoom se houver câmera
        zoom = getattr(camera, "zoom", 1.0) if camera else 1.0
        
        for p in self.ps:
            scale, alpha = p.interp()
            img = pygame.transform.rotozoom(self.tex, p.ang, scale * zoom)
            img.set_alpha(alpha)
            x, y = p.x, p.y
            if camera:
                x, y = camera.mundo_para_tela(x, y)
            surface.blit(img, img.get_rect(center=(int(x), int(y))))
