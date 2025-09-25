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
        self.tex_index = 0  # Cada partícula tem seu próprio índice de textura

    def alive(self): return self.t < self.life
    def update(self, dt):
        self.t += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        # Atualizar índice de textura individual (animação mais lenta)
        self.tex_index = int((self.t * 0.05) % 12)  # 12 texturas disponíveis
    def interp(self):
        k = max(0.0, min(1.0, self.t / self.life))
        scale = self.scale0 + (self.scale1 - self.scale0) * k
        # Fade suave: começa com alpha0, vai até 0 no final
        # Usar curva suave para evitar piscada
        fade_curve = 1.0 - (k * k)  # Curva quadrática para fade mais suave
        alpha = int(self.alpha0 * fade_curve)
        return scale, alpha

class EmissorFumaca:
    def __init__(self):
        # Carregar texturas de fumaça
        self.tex_fumaca = []
        for i in range(12):  # pixels_00.png a pixels_11.png
            caminho = os.path.join(DIR_EFFECTS, "smoke", f"pixels_{i:02d}.png")
            if os.path.exists(caminho):
                try:
                    img = pygame.image.load(caminho).convert_alpha()
                    # Redimensionar para tamanho adequado
                    img = pygame.transform.scale(img, (16, 16))
                    self.tex_fumaca.append(img)
                except Exception as e:
                    pass  # Silenciar erros de carregamento
        
        if not self.tex_fumaca:
            # Fallback se não encontrar as texturas
            self.tex_fumaca = [pygame.Surface((16, 16), pygame.SRCALPHA)]
            self.tex_fumaca[0].fill((100, 100, 100, 128))
        
        self.ps = []
        self._accum = 0.0
        self.max_particulas = 80  # Equilibrado para boa performance e efeitos visuais
        self._particulas_por_frame = 2  # 2 partículas por frame para efeitos visuais
        self._frame_atual = 0

    def spawn(self, x, y, dirx, diry, taxa_qps, dt):
        # Limitar número de partículas para performance
        if len(self.ps) >= self.max_particulas:
            return
            
        # Reduzir taxa de spawn para boa performance
        self._accum += taxa_qps * dt * 0.4  # Reduzir para 40% da taxa original
        n = int(self._accum)
        if n <= 0: 
            return
        self._accum -= n
        
        # Limitar número de partículas criadas por frame
        n = min(n, self._particulas_por_frame)
        
        base_ang = math.atan2(diry, dirx) + math.pi
        for _ in range(n):
            # Verificar limite novamente dentro do loop
            if len(self.ps) >= self.max_particulas:
                break
                
            ang = base_ang + random.uniform(-0.05, 0.05)  # Dispersão ainda menor
            v = random.uniform(20, 35)  # Velocidade mais concentrada
            vx, vy = math.cos(ang)*v, math.sin(ang)*v
            # Adicionar movimento vertical para cima
            vy -= random.uniform(25, 40)  # Força para cima mais concentrada
            life = random.uniform(3.0, 4.5)  # Vida um pouco menor
            scale0 = random.uniform(1.5, 2.5)  # Tamanho menor inicial
            scale1 = scale0 * random.uniform(1.5, 2.0)  # Crescimento menor
            alpha0 = random.randint(120, 180)  # Menos opaco inicial
            p = Particula(x, y, vx, vy, life, random.uniform(0,360), scale0, scale1, alpha0, 0, "fumaca")
            self.ps.append(p)

    def update(self, dt):
        # Atualizar partículas e remover as que morreram
        for p in self.ps:
            p.update(dt)
        self.ps = [p for p in self.ps if p.alive()]
        self._frame_atual += 1

    def draw(self, surface, camera=None):
        # Otimização: pré-calcular zoom se houver câmera
        zoom = getattr(camera, "zoom", 1.0) if camera else 1.0
        
        for p in self.ps:
            scale, alpha = p.interp()
            x, y = p.x, p.y
            if camera:
                x, y = camera.mundo_para_tela(x, y)
            
            # Verificar se a partícula está dentro da tela
            if x < -50 or x > 1280 + 50 or y < -50 or y > 720 + 50:
                continue  # Pular partículas fora da tela
            
            # Usar textura de fumaça se disponível
            if self.tex_fumaca:
                # Usar índice individual de cada partícula (sem loop global)
                tex_index = p.tex_index % len(self.tex_fumaca)
                img = pygame.transform.rotozoom(self.tex_fumaca[tex_index], p.ang, scale * zoom)
                img.set_alpha(alpha)
                surface.blit(img, img.get_rect(center=(int(x), int(y))))
            else:
                # Fallback: círculos coloridos mais visíveis
                raio = max(8, int(scale * 20 * zoom))  # Raio maior e mínimo de 8 pixels
                # Círculo externo cinza
                pygame.draw.circle(surface, (150, 150, 150), (int(x), int(y)), raio)
                # Círculo interno branco para contraste
                pygame.draw.circle(surface, (255, 255, 255), (int(x), int(y)), max(2, raio // 2))
                # Ponto central para máxima visibilidade
                pygame.draw.circle(surface, (0, 0, 0), (int(x), int(y)), 1)

class EmissorNitro:
    def __init__(self):
        # Carregar texturas de nitro
        self.tex_nitro = []
        for i in range(4):  # pixels_00.png a pixels_03.png
            caminho = os.path.join(DIR_EFFECTS, "nitro", f"pixels_{i:02d}.png")
            if os.path.exists(caminho):
                try:
                    img = pygame.image.load(caminho).convert_alpha()
                    # Redimensionar para tamanho adequado
                    img = pygame.transform.scale(img, (16, 16))
                    self.tex_nitro.append(img)
                    print(f"Nitro carregado: {caminho}")
                except Exception as e:
                    print(f"Erro ao carregar nitro {caminho}: {e}")
        
        if not self.tex_nitro:
            # Fallback se não encontrar as texturas
            print("Criando fallback para nitro")
            self.tex_nitro = [pygame.Surface((16, 16), pygame.SRCALPHA)]
            self.tex_nitro[0].fill((0, 255, 255, 200))
        
        self.ps = []
        self._accum = 0.0
        self.max_particulas = 20  # Equilibrado para boa performance e efeitos visuais
        self._particulas_por_frame = 1  # 1 partícula por frame para nitro
        self._frame_atual = 0

    def spawn(self, x, y, dirx, diry, taxa_qps, dt):
        if len(self.ps) >= self.max_particulas:
            return
            
        self._accum += taxa_qps * dt
        n = int(self._accum)
        if n <= 0: return
        self._accum -= n
        
        n = min(n, self._particulas_por_frame)
        
        base_ang = math.atan2(diry, dirx)
        for _ in range(n):
            if len(self.ps) >= self.max_particulas:
                break
                
            ang = base_ang + random.uniform(-0.3, 0.3)  # Menos dispersão para nitro
            v = random.uniform(60, 150)  # Mais rápido que fumaça
            vx, vy = math.cos(ang)*v, math.sin(ang)*v
            life = random.uniform(0.3, 0.8)  # Vida um pouco mais longa
            scale0 = random.uniform(0.4, 0.7)  # Tamanho maior
            scale1 = scale0 * random.uniform(1.2, 2.0)  # Crescimento menor
            alpha0 = random.randint(200, 255)  # Muito opaco
            p = Particula(x, y, vx, vy, life, random.uniform(0,360), scale0, scale1, alpha0, 0, "nitro")
            self.ps.append(p)

    def update(self, dt):
        self.ps = [p for p in self.ps if p.alive() and p.update(dt)]
        self._frame_atual += 1

    def draw(self, surface, camera=None):
        zoom = getattr(camera, "zoom", 1.0) if camera else 1.0
        
        for p in self.ps:
            scale, alpha = p.interp()
            # Usar textura animada de nitro
            tex_index = int((self._frame_atual * 0.2) % len(self.tex_nitro))
            img = pygame.transform.rotozoom(self.tex_nitro[tex_index], p.ang, scale * zoom)
            img.set_alpha(alpha)
            x, y = p.x, p.y
            if camera:
                x, y = camera.mundo_para_tela(x, y)
            
            surface.blit(img, img.get_rect(center=(int(x), int(y))))
