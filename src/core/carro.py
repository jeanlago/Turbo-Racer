import os, math, pygame
from config import LARGURA, ALTURA, DIR_SPRITES
from core.pista import eh_pixel_da_pista

class Carro:
    def __init__(self, x, y, prefixo_cor, controles):
        self.x = float(x)
        self.y = float(y)
        self.angulo = 0.0
        self.velocidade = 0.0
        self.controles = controles

        caminho_sprite = os.path.join(DIR_SPRITES, f"{prefixo_cor}.png")
        self.sprite_base = pygame.image.load(caminho_sprite).convert_alpha()

        self.VEL_MAX_FRENTE = 6.0
        self.VEL_MAX_RE = -2.0
        self.ACELERACAO = 0.08
        self.FREIO = 0.14
        self.ATRITO = 0.985
        self.GIRO_MAX = 3.0

    def desenhar(self, superficie):
        sprite_rot = pygame.transform.rotate(self.sprite_base, (self.angulo))
        rect = sprite_rot.get_rect(center=(self.x, self.y))
        superficie.blit(sprite_rot, rect.topleft)

    def _vetor_frente(self):
        rad = math.radians(self.angulo)
        return (-math.cos(rad), math.sin(rad))

    def atualizar(self, teclas, superficie_mascara):
        x_ant, y_ant = self.x, self.y

        if teclas[self.controles[0]]:
            self.velocidade = min(self.velocidade + self.ACELERACAO, self.VEL_MAX_FRENTE)
        elif teclas[self.controles[3]]:
            if self.velocidade > 0.2:
                self.velocidade = max(0.0, self.velocidade - self.FREIO)
            else:
                self.velocidade = max(self.VEL_MAX_RE, self.velocidade - (self.FREIO * 0.5))
        else:
            self.velocidade *= self.ATRITO
            if abs(self.velocidade) < 0.01:
                self.velocidade = 0.0

        fator_giro = min(abs(self.velocidade) * 0.5, self.GIRO_MAX)
        if teclas[self.controles[1]]:
            self.angulo -= fator_giro
        if teclas[self.controles[2]]:
            self.angulo += fator_giro

        if self.angulo > 180: self.angulo -= 360
        if self.angulo < -180: self.angulo += 360

        fx, fy = self._vetor_frente()
        self.x += self.velocidade * fx
        self.y += self.velocidade * fy

        cx, cy = int(self.x), int(self.y)
        houve_colisao = False
        amostras_local = [(0, 0), (12, 0), (-12, 0), (0, 12), (0, -12)]
        dir_frente_x, dir_frente_y = fx, fy
        dir_direita_x, dir_direita_y = (fy, -fx)

        for ox, oy in amostras_local:
            px = int(cx + ox * dir_frente_x + oy * dir_direita_x)
            py = int(cy + ox * dir_frente_y + oy * dir_direita_y)
            if not eh_pixel_da_pista(superficie_mascara, px, py):
                houve_colisao = True
                break

        if houve_colisao:
            self.x, self.y = x_ant, y_ant
            self.velocidade = -abs(self.velocidade) * 0.4
            if self.velocidade < self.VEL_MAX_RE:
                self.velocidade = self.VEL_MAX_RE

        self.x = max(0.0, min(LARGURA * 1.0, self.x))
        self.y = max(0.0, min(ALTURA * 1.0, self.y))
