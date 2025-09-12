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

        # Suavização (follow “macio”)
        self.follow_rigidez = 8.0  # maior = segue mais “grudado”

    def set_alvo(self, alvo):
        self.alvo = alvo

    def atualizar(self, dt):
        if not self.alvo:
            return
        # segue o alvo com suavização exponencial simples
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
        return pygame.Rect(left, top, int(vw), int(vh))

    def mundo_para_tela(self, x, y):
        """Converte coordenadas do mundo para tela (aplica offset e zoom)."""
        r = self.ret_visao()
        sx = int((x - r.left) * self.zoom)
        sy = int((y - r.top ) * self.zoom)
        return sx, sy

    def desenhar_fundo(self, superficie_tela, superficie_mundo):
        """Recorta a visão do mundo e escala para preencher a tela."""
        r = self.ret_visao()
        recorte = superficie_mundo.subsurface(r).copy()
        ampliado = pygame.transform.scale(recorte, (self.largura_tela, self.altura_tela))
        superficie_tela.blit(ampliado, (0, 0))
