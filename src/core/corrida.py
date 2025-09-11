import pygame
from config import (
    COR_TEXTO, COR_SOMBRA,
    VOLTAS_OBJETIVO, LINHA_LARGADA, PONTOS_DE_CONTROLE,
    MODO_DRIFT, DRIFT_PONTOS_BASE, DRIFT_PONTOS_VEL_FACTOR,
    DRIFT_DECAY_POR_SEG, DRIFT_COMBO_MAX, DRIFT_COMBO_STEP
)


class GerenciadorCorrida:
    def __init__(self, fonte=None):
        self.fonte = fonte or pygame.font.SysFont("consolas", 26)
        self.fonte_grande = pygame.font.SysFont("consolas", 64, bold=True)

        # Semáforo 3-2-1-VAI
        self.contagem_regressiva = 3.0
        self.iniciada = False

        # Progresso/estado por carro
        self.proximo_checkpoint = {}   # carro -> idx próximo CP
        self.voltas = {}               # carro -> voltas
        self.finalizou = {}            # carro -> bool

        # Tempo
        self.tempo_global = 0.0        # tempo desde o "VAI!"
        self.tempo_final = {}          # carro -> tempo quando finalizou

        # Retângulos
        self.ret_largada = pygame.Rect(*LINHA_LARGADA)
        self.ret_checkpoints = [pygame.Rect(*r) for r in PONTOS_DE_CONTROLE]

    def registrar_carro(self, carro):
        self.proximo_checkpoint[carro] = 0
        self.voltas[carro] = 0
        self.finalizou[carro] = False
        self.tempo_final[carro] = None

    # --- Semáforo e tempo global ---
    def atualizar_contagem(self, dt):
        if self.iniciada:
            return
        self.contagem_regressiva -= dt
        if self.contagem_regressiva <= 0:
            self.iniciada = True

    def atualizar_tempo(self, dt):
        if self.iniciada and not self.todos_finalizados():
            self.tempo_global += dt

    def pode_controlar(self):
        return self.iniciada

    def desenhar_semaforo(self, tela, largura, altura):
        if self.iniciada:
            return
        val = max(0, int(self.contagem_regressiva) + 1)
        texto = "VAI!" if val <= 0 else str(val)
        superficie = self.fonte_grande.render(texto, True, (255, 255, 255))
        sombra = self.fonte_grande.render(texto, True, (0, 0, 0))
        rect = superficie.get_rect(center=(largura//2, altura//3))
        tela.blit(sombra, (rect.x+2, rect.y+2))
        tela.blit(superficie, rect)

    # --- Checkpoints/Voltas ---
    def atualizar_progresso_carro(self, carro):
        if self.finalizou[carro]:
            return

        idx_cp = self.proximo_checkpoint[carro]
        if idx_cp < len(self.ret_checkpoints):
            if self.ret_checkpoints[idx_cp].collidepoint(int(carro.x), int(carro.y)):
                self.proximo_checkpoint[carro] += 1

        if self.proximo_checkpoint[carro] == len(self.ret_checkpoints):
            if self.ret_largada.collidepoint(int(carro.x), int(carro.y)):
                self.voltas[carro] += 1
                self.proximo_checkpoint[carro] = 0
                if self.voltas[carro] >= VOLTAS_OBJETIVO:
                    self.finalizou[carro] = True
                    # registra tempo de chegada
                    if self.tempo_final[carro] is None:
                        self.tempo_final[carro] = self.tempo_global

    # --- HUD ---
    def _fmt_tempo(self, t):
        if t is None: return "--:--.--"
        mm = int(t // 60)
        ss = t % 60
        return f"{mm:02d}:{ss:05.2f}"

    def desenhar_hud(self, tela, carros):
        y = 8
        for i, carro in enumerate(carros, start=1):
            voltas = self.voltas.get(carro, 0)
            t_final = self.tempo_final.get(carro, None)
            t_txt = self._fmt_tempo(self.tempo_global if t_final is None else t_final)
            texto = f"P{i}  Voltas: {voltas}/{VOLTAS_OBJETIVO}  Turbo: {int(carro.turbo_carga)}%  Tempo: {t_txt}"
            sombra = self.fonte.render(texto, True, COR_SOMBRA)
            superficie = self.fonte.render(texto, True, COR_TEXTO)
            tela.blit(sombra, (10, y+2))
            tela.blit(superficie, (8, y))
            y += 28

    # --- Resultado ---
    def alguem_finalizou(self):
        return any(self.finalizou.values())

    def todos_finalizados(self):
        # opcional: termina quando todos terminam; para singleplayer isso não é obrigatório
        return all(self.finalizou.values()) if self.finalizou else False

    def indice_vencedor(self, carros):
        """Vence quem terminar primeiro; em caso de múltiplos, menor tempo_final."""
        candidatos = [(i+1, self.tempo_final.get(c)) for i, c in enumerate(carros)]
        candidatos = [(idx, t) for (idx, t) in candidatos if t is not None]
        if not candidatos:
            return None
        candidatos.sort(key=lambda x: x[1])
        return candidatos[0][0]

    def desenhar_podio(self, tela, largura, altura, carros):
        if not self.alguem_finalizou():
            return
        vencedor = self.indice_vencedor(carros)
        msg = f"VENCEDOR: P{vencedor}" if vencedor else "FIM!"
        fg = self.fonte_grande
        sombra = fg.render(msg, True, (0, 0, 0))
        texto  = fg.render(msg, True, (255, 215, 0))
        rect = texto.get_rect(center=(largura//2, altura//2))
        tela.blit(sombra, (rect.x+3, rect.y+3))
        tela.blit(texto, rect)

class GerenciadorDrift:
    def __init__(self, fonte=None):
        self.fonte = fonte or pygame.font.SysFont("consolas", 26)
        self.score = 0.0
        self.combo = 1.0
        self.chain_timer = 0.0  # tempo "vivo" de drift p/ manter o combo

    def atualizar(self, carro, dt):
        # pontos por “tick” enquanto estiver derrapando
        v = abs(carro.velocidade) * 60.0  # px/s
        if carro.drifting and carro.drift_intensidade > 0.05:
            ganho = (DRIFT_PONTOS_BASE + v * DRIFT_PONTOS_VEL_FACTOR) * self.combo * carro.drift_intensidade
            self.score += ganho * dt * 60.0
            # combo sobe com tempo em drift
            self.combo = min(DRIFT_COMBO_MAX, self.combo + DRIFT_COMBO_STEP * dt)
            self.chain_timer = 0.0
        else:
            # decai “cadeia” e pontuação "quente"
            self.chain_timer += dt
            self.score = max(0.0, self.score - DRIFT_DECAY_POR_SEG * dt)
            # combo cai devagar se ficar muito tempo sem drift
            if self.chain_timer > 1.2:
                self.combo = max(1.0, self.combo - 2.0 * dt)

    def desenhar_hud(self, tela, x=8, y=8):
        s = int(self.score)
        c = f"x{self.combo:.1f}" if self.combo > 1.01 else "x1"
        msg = f"DRIFT SCORE: {s}   COMBO: {c}"
        sombra = self.fonte.render(msg, True, COR_SOMBRA)
        texto  = self.fonte.render(msg, True, COR_TEXTO)
        tela.blit(sombra, (x+2, y+2))
        tela.blit(texto, (x, y))
