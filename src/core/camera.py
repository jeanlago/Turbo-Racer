# src/core/camera.py
import pygame

class Camera:
    def __init__(self, largura_tela, altura_tela, largura_mundo, altura_mundo, alvo=None, zoom=1.6):
        self.largura_tela = largura_tela
        self.altura_tela = altura_tela
        self.largura_mundo = largura_mundo
        self.altura_mundo = altura_mundo
        self.alvo = alvo  # objeto com .x e .y
        self.zoom = float(zoom)

        # Posição do centro da câmera no MUNDO
        self.cx = largura_mundo / 2
        self.cy = altura_mundo / 2

        # Suavização (follow "macio") - mais responsivo
        self.follow_rigidez = 20.0  # maior = segue mais "grudado" e responsivo

    def set_alvo(self, alvo):
        self.alvo = alvo

    def atualizar(self, dt):
        if not self.alvo:
            return
        # segue o alvo com suavização exponencIAl simples
        tx, ty = float(self.alvo.x), float(self.alvo.y)
        lerp = 1.0 - pow(0.001, self.follow_rigidez * dt)  # 0..1
        self.cx += (tx - self.cx) * lerp
        self.cy += (ty - self.cy) * lerp
        self._clamp_centro()

    def _clamp_centro(self):
        vw = self.largura_tela / self.zoom
        vh = self.altura_tela  / self.zoom
        half_w = vw / 2
        half_h = vh / 2
        self.cx = max(half_w, min(self.largura_mundo - half_w, self.cx))
        self.cy = max(half_h, min(self.altura_mundo  - half_h, self.cy))

    def ret_visao(self):
        """Retângulo da visão no MUNDO (não escalado)."""
        vw = self.largura_tela / self.zoom
        vh = self.altura_tela  / self.zoom
        left = int(self.cx - vw / 2)
        top  = int(self.cy - vh / 2)
        # garante que o rect está dentro do mundo
        left = max(0, min(self.largura_mundo - int(vw), left))
        top  = max(0, min(self.altura_mundo  - int(vh), top))
        # garante que as dimensões não excedem o mundo
        width = min(int(vw), self.largura_mundo - left)
        height = min(int(vh), self.altura_mundo - top)
        return pygame.Rect(left, top, width, height)

    def mundo_para_tela(self, x, y):
        """Converte coordenadas do mundo para tela (aplica offset e zoom)."""
        r = self.ret_visao()
        sx = int((x - r.left) * self.zoom)
        sy = int((y - r.top ) * self.zoom)
        return sx, sy
    
    def tela_para_mundo(self, sx, sy):
        """Converte coordenadas da tela para mundo (remove offset e zoom)."""
        r = self.ret_visao()
        x = (sx / self.zoom) + r.left
        y = (sy / self.zoom) + r.top
        return x, y

    def desenhar_fundo(self, superficie_tela, superficie_mundo):
        """Recorta a visão do mundo e escala para preencher a tela."""
        r = self.ret_visao()
        # Otimização: usar subsurface diretamente em vez de copy()
        recorte = superficie_mundo.subsurface(r)
        # Usar scale em vez de smoothscale para melhor performance
        amplIAdo = pygame.transform.scale(recorte, (self.largura_tela, self.altura_tela))
        superficie_tela.blit(amplIAdo, (0, 0))
    
    def esta_visivel(self, x_mundo, y_mundo, margem=0):
        """Verificar se um objeto está visível na tela (com margem)."""
        x_tela, y_tela = self.mundo_para_tela(x_mundo, y_mundo)
        return (-margem <= x_tela <= self.largura_tela + margem and 
                -margem <= y_tela <= self.altura_tela + margem)