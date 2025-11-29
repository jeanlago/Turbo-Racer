# src/core/particulas.py
import math, random, pygame, os
from config import DIR_EFFECTS

class Particula:
    __slots__ = ("x","y","vx","vy","life","t","ang","scale0","scale1","alpha0","alpha1","tipo","tex_index")
    def __init__(self, x, y, vx, vy, life, ang, scale0, scale1, alpha0, alpha1, tipo="fumaca"):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = float(vx), float(vy)
        self.life = float(life)
        self.t = 0.0
        self.ang = float(ang)
        self.scale0, self.scale1 = float(scale0), float(scale1)
        self.alpha0, self.alpha1 = int(alpha0), int(alpha1)
        self.tipo = tipo
        self.tex_index = 0

    def alive(self): return self.t < self.life
    def update(self, dt):
        if not self.alive():
            return False
        self.t += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.tex_index = int((self.t * 0.05) % 12)
        return True
    def interp(self):
        k = max(0.0, min(1.0, self.t / self.life))
        scale = self.scale0 + (self.scale1 - self.scale0) * k
        fade_curve = 1.0 - (k * k)
        alpha = int(self.alpha0 * fade_curve)
        return scale, alpha

class EmissorColisao:
    """Emissor de partículas para colisões (faíscas)"""
    def __init__(self):
        self.ps = []
        self.max_particulas = 30
        self._frame_atual = 0
    
    def spawn(self, x, y, normal_x, normal_y, intensidade=1.0):
        """Cria partículas de faíscas na posição de colisão"""
        if len(self.ps) >= self.max_particulas:
            return
        
        num_particulas = int(5 * intensidade)
        for _ in range(min(num_particulas, 10)):
            if len(self.ps) >= self.max_particulas:
                break
            
            ang = math.atan2(normal_y, normal_x) + random.uniform(-math.pi/3, math.pi/3)
            v = random.uniform(100, 200) * intensidade
            vx = math.cos(ang) * v
            vy = math.sin(ang) * v
            life = random.uniform(0.3, 0.6)
            
            p = Particula(
                x, y, vx, vy, life,
                random.uniform(0, 360),
                0.5, 0.2, 255, 0,
                "faisca"
            )
            self.ps.append(p)
    
    def update(self, dt):
        for p in self.ps:
            p.update(dt)
        self.ps = [p for p in self.ps if p.alive()]
    
    def draw(self, surface, camera=None):
        for p in self.ps:
            if not p.alive():
                continue
            scale, alpha = p.interp()
            if camera:
                sx, sy = camera.mundo_para_tela(p.x, p.y)
            else:
                sx, sy = int(p.x), int(p.y)
            
            cor = (255, 200, 50, alpha)
            tamanho = int(3 * scale)
            if tamanho > 0:
                particula_surf = pygame.Surface((tamanho * 2, tamanho * 2), pygame.SRCALPHA)
                pygame.draw.circle(particula_surf, cor[:3], (tamanho, tamanho), tamanho)
                particula_surf.set_alpha(alpha)
                surface.blit(particula_surf, (sx - tamanho, sy - tamanho))

class EmissorFumaca:
    def __init__(self):
        self.tex_fumaca = []
        for i in range(12):
            caminho = os.path.join(DIR_EFFECTS, "smoke", f"pixels_{i:02d}.png")
            if os.path.exists(caminho):
                try:
                    img = pygame.image.load(caminho).convert_alpha()
                    img = pygame.transform.scale(img, (16, 16))
                    self.tex_fumaca.append(img)
                except Exception as e:
                    pass
        
        if not self.tex_fumaca:
            self.tex_fumaca = [pygame.Surface((16, 16), pygame.SRCALPHA)]
            self.tex_fumaca[0].fill((100, 100, 100, 128))
        
        self.ps = []
        self._accum = 0.0
        self.max_particulas = 80
        self._particulas_por_frame = 2
        self._frame_atual = 0

    def spawn(self, x, y, dirx, diry, taxa_qps, dt):
        if len(self.ps) >= self.max_particulas:
            return
            
        self._accum += taxa_qps * dt * 0.4
        n = int(self._accum)
        if n <= 0: 
            return
        self._accum -= n
        
        n = min(n, self._particulas_por_frame)
        
        base_ang = math.atan2(diry, dirx) + math.pi
        for _ in range(n):
            if len(self.ps) >= self.max_particulas:
                break
                
            ang = base_ang + random.uniform(-0.05, 0.05)
            v = random.uniform(20, 35)
            vx, vy = math.cos(ang)*v, math.sin(ang)*v
            vy -= random.uniform(25, 40)
            life = random.uniform(3.0, 4.5)
            scale0 = random.uniform(1.5, 2.5)
            scale1 = scale0 * random.uniform(1.5, 2.0)
            alpha0 = random.randint(120, 180)
            p = Particula(x, y, vx, vy, life, random.uniform(0,360), scale0, scale1, alpha0, 0, "fumaca")
            self.ps.append(p)

    def update(self, dt):
        for p in self.ps:
            p.update(dt)
        self.ps = [p for p in self.ps if p.alive()]
        self._frame_atual += 1

    def draw(self, surface, camera=None):
        zoom = getattr(camera, "zoom", 1.0) if camera else 1.0
        largura_tela = surface.get_width()
        altura_tela = surface.get_height()
        margem = 50
        
        for p in self.ps:
            scale, alpha = p.interp()
            x, y = p.x, p.y
            if camera:
                x, y = camera.mundo_para_tela(x, y)
            
            if x < -margem or x > largura_tela + margem or y < -margem or y > altura_tela + margem:
                continue
            
            if self.tex_fumaca:
                tex_index = p.tex_index % len(self.tex_fumaca)
                if not hasattr(self, '_transform_cache'):
                    self._transform_cache = {}
                    self._cache_size_limit = 50
                
                cache_key = (tex_index, int(p.ang), int(scale * zoom * 10))
                if cache_key not in self._transform_cache:
                    if len(self._transform_cache) > self._cache_size_limit:
                        oldest_key = next(iter(self._transform_cache))
                        del self._transform_cache[oldest_key]
                    img = pygame.transform.rotozoom(self.tex_fumaca[tex_index], p.ang, scale * zoom)
                    self._transform_cache[cache_key] = img
                else:
                    img = self._transform_cache[cache_key]
                
                img.set_alpha(alpha)
                surface.blit(img, img.get_rect(center=(int(x), int(y))))
            else:
                raio = max(8, int(scale * 20 * zoom))
                pygame.draw.circle(surface, (150, 150, 150), (int(x), int(y)), raio)
                pygame.draw.circle(surface, (255, 255, 255), (int(x), int(y)), max(2, raio // 2))
                pygame.draw.circle(surface, (0, 0, 0), (int(x), int(y)), 1)

class EmissorNitro:
    def __init__(self):
        self.tex_nitro = []
        for i in range(4):
            caminho = os.path.join(DIR_EFFECTS, "nitro", f"pixels_{i:02d}.png")
            if os.path.exists(caminho):
                try:
                    img = pygame.image.load(caminho).convert_alpha()
                    img = pygame.transform.scale(img, (16, 16))
                    self.tex_nitro.append(img)
                    print(f"Nitro carregado: {caminho}")
                except Exception as e:
                    print(f"Erro ao carregar nitro {caminho}: {e}")
        
        if not self.tex_nitro:
            print("Criando fallback para nitro")
            self.tex_nitro = [pygame.Surface((16, 16), pygame.SRCALPHA)]
            self.tex_nitro[0].fill((0, 255, 255, 200))
        
        self.ps = []
        self._accum = 0.0
        self.max_particulas = 30
        self._particulas_por_frame = 2
        self._frame_atual = 0

    def spawn(self, x, y, dirx, diry, taxa_qps, dt):
        if len(self.ps) >= self.max_particulas:
            self.ps = self.ps[-self.max_particulas//2:]
            
        self._accum += taxa_qps * dt
        n = int(self._accum)
        
        if n <= 0 and self._accum > 0.01:
            n = 1
            self._accum = 0.0
        
        if n > 0:
            self._accum -= n
            n = min(n, self._particulas_por_frame * 3)
            
            base_ang = math.atan2(diry, dirx)
            for _ in range(n):
                if len(self.ps) >= self.max_particulas:
                    break
                    
                ang = base_ang + random.uniform(-0.2, 0.2)
                v = random.uniform(100, 200)
                vx, vy = math.cos(ang)*v, math.sin(ang)*v
                life = random.uniform(0.3, 0.7)
                scale0 = random.uniform(0.6, 1.0)
                scale1 = scale0 * random.uniform(1.5, 2.5)
                alpha0 = random.randint(220, 255)
                p = Particula(x, y, vx, vy, life, random.uniform(0,360), scale0, scale1, alpha0, 0, "nitro")
                self.ps.append(p)

    def update(self, dt):
        self.ps = [p for p in self.ps if p.update(dt)]
        self._frame_atual += 1

    def draw(self, surface, camera=None):
        zoom = getattr(camera, "zoom", 1.0) if camera else 1.0
        largura_tela = surface.get_width()
        altura_tela = surface.get_height()
        margem = 50
        
        for p in self.ps:
            scale, alpha = p.interp()
            x, y = p.x, p.y
            if camera:
                x, y = camera.mundo_para_tela(x, y)
            
            if x < -margem or x > largura_tela + margem or y < -margem or y > altura_tela + margem:
                continue
            
            tex_index = int((self._frame_atual * 0.2) % len(self.tex_nitro))
            img = pygame.transform.rotozoom(self.tex_nitro[tex_index], p.ang, scale * zoom)
            img.set_alpha(alpha)
            surface.blit(img, img.get_rect(center=(int(x), int(y))))
