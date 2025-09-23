import pygame
from config import (
    COR_TEXTO, COR_SOMBRA,
    VOLTAS_OBJETIVO, LINHA_LARGADA, PONTOS_DE_CONTROLE,
    MODO_DRIFT, DRIFT_PONTOS_BASE, DRIFT_PONTOS_VEL_FACTOR,
    DRIFT_DECAY_POR_SEG, DRIFT_COMBO_MAX, DRIFT_COMBO_STEP
)


class GerencIAdorCorrida:
    def __init__(self, fonte=None, checkpoints=None, voltas_objetivo=1):
        self.fonte = fonte or pygame.font.SysFont("consolas", 26)
        self.fonte_grande = pygame.font.SysFont("consolas", 64, bold=True)

        # Semáforo 3-2-1-VAI
        self.contagem_regressiva = 3.0
        self.inicIAda = False

        # Progresso/estado por carro
        self.proximo_checkpoint = {}   # carro -> idx próximo CP
        self.voltas = {}               # carro -> voltas
        self.finalizou = {}            # carro -> bool

        # Tempo
        self.tempo_global = 0.0        # tempo desde o "VAI!"
        self.tempo_final = {}          # carro -> tempo quando finalizou

        # Sistema de checkpoints dinâmico
        self.checkpoints = checkpoints or []
        self.voltas_objetivo = voltas_objetivo
        self.total_checkpoints_necessarios = len(self.checkpoints) * self.voltas_objetivo
        
        # Retângulos (mantidos para compatibilidade)
        self.ret_largada = pygame.Rect(*LINHA_LARGADA)
        self.ret_checkpoints = [pygame.Rect(*r) for r in PONTOS_DE_CONTROLE]

    def registrar_carro(self, carro):
        self.proximo_checkpoint[carro] = 0
        self.voltas[carro] = 0
        self.finalizou[carro] = False
        self.tempo_final[carro] = None

    # --- Semáforo e tempo global ---
    def atualizar_contagem(self, dt):
        if self.inicIAda:
            return
        self.contagem_regressiva -= dt
        if self.contagem_regressiva <= 0:
            self.inicIAda = True

    def atualizar_tempo(self, dt):
        if self.inicIAda and not self.todos_finalizados():
            self.tempo_global += dt

    def pode_controlar(self):
        return self.inicIAda

    def desenhar_semaforo(self, tela, largura, altura):
        if self.inicIAda:
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

        # Sistema de checkpoints dinâmico
        if self.checkpoints:
            # Verificar se passou pelo checkpoint atual
            idx_cp = self.proximo_checkpoint[carro] % len(self.checkpoints)
            if idx_cp < len(self.checkpoints):
                cx, cy = self.checkpoints[idx_cp]
                dist = ((carro.x - cx) ** 2 + (carro.y - cy) ** 2) ** 0.5
                
                # Detecção de checkpoint com múltiplos métodos
                passou_checkpoint = False
                
                # Método 1: Distância direta
                if dist < 60:
                    passou_checkpoint = True
                
                # Método 2: Projeção (passou "através" do checkpoint)
                if not passou_checkpoint and idx_cp < len(self.checkpoints) - 1:
                    proximo_cx, proximo_cy = self.checkpoints[idx_cp + 1]
                    vetor_checkpoint = (proximo_cx - cx, proximo_cy - cy)
                    vetor_carro = (carro.x - cx, carro.y - cy)
                    
                    produto_escalar = vetor_checkpoint[0] * vetor_carro[0] + vetor_checkpoint[1] * vetor_carro[1]
                    if produto_escalar > 0 and dist < 80:
                        passou_checkpoint = True
                
                # Método 3: Velocidade e direção
                if not passou_checkpoint and hasattr(carro, 'vx') and hasattr(carro, 'vy'):
                    velocidade = (carro.vx*carro.vx + carro.vy*carro.vy) ** 0.5
                    if velocidade > 0.5:  # Se estiver se movendo
                        direcao_movimento = (carro.vx, carro.vy)
                        proximo_cx, proximo_cy = self.checkpoints[(idx_cp + 1) % len(self.checkpoints)]
                        direcao_checkpoint = (proximo_cx - carro.x, proximo_cy - carro.y)
                        
                        if ((direcao_movimento[0]**2 + direcao_movimento[1]**2) ** 0.5 > 0.1 and
                            (direcao_checkpoint[0]**2 + direcao_checkpoint[1]**2) ** 0.5 > 0.1):
                            
                            norm_mov = (direcao_movimento[0]**2 + direcao_movimento[1]**2) ** 0.5
                            norm_check = (direcao_checkpoint[0]**2 + direcao_checkpoint[1]**2) ** 0.5
                            
                            cos_angulo = (direcao_movimento[0] * direcao_checkpoint[0] + 
                                         direcao_movimento[1] * direcao_checkpoint[1]) / (norm_mov * norm_check)
                            
                            if cos_angulo > 0.5 and dist < 80:  # Movendo na direção do próximo checkpoint
                                passou_checkpoint = True
                
                if passou_checkpoint:
                    self.proximo_checkpoint[carro] += 1
                    print(f"Carro {getattr(carro, 'nome', 'Desconhecido')} passou pelo checkpoint {self.proximo_checkpoint[carro]}!")
                    
                    # Verificar se completou uma volta
                    checkpoints_por_volta = len(self.checkpoints)
                    if self.proximo_checkpoint[carro] % checkpoints_por_volta == 0:
                        self.voltas[carro] += 1
                        print(f"Carro {getattr(carro, 'nome', 'Desconhecido')} completou a volta {self.voltas[carro]}!")
                    
                    # Verificar se terminou a corrida
                    if self.proximo_checkpoint[carro] >= self.total_checkpoints_necessarios:
                        self.finalizou[carro] = True
                        if self.tempo_final[carro] is None:
                            self.tempo_final[carro] = self.tempo_global
                        print(f"Carro {getattr(carro, 'nome', 'Desconhecido')} terminou a corrida!")
        else:
            # Sistema antigo para compatibilidade
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
            checkpoints_completados = self.proximo_checkpoint.get(carro, 0)
            t_final = self.tempo_final.get(carro, None)
            t_txt = self._fmt_tempo(self.tempo_global if t_final is None else t_final)
            nome_carro = getattr(carro, 'nome', f'P{i}')
            
            # Mostrar progresso baseado no sistema de checkpoints
            if self.checkpoints:
                voltas_objetivo = self.voltas_objetivo
                checkpoints_por_volta = len(self.checkpoints)
                checkpoint_atual = checkpoints_completados % checkpoints_por_volta
                texto = f"{nome_carro}  Voltas: {voltas}/{voltas_objetivo}  CP: {checkpoint_atual}/{checkpoints_por_volta}  Turbo: {int(carro.turbo_carga)}%  Tempo: {t_txt}"
            else:
                texto = f"{nome_carro}  Voltas: {voltas}/{VOLTAS_OBJETIVO}  Turbo: {int(carro.turbo_carga)}%  Tempo: {t_txt}"
            
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

class GerencIAdorDrift:
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
            # decai “cadeIA” e pontuação "quente"
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
