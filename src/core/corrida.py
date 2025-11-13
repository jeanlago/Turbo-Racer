import pygame
from config import (
    COR_TEXTO, COR_SOMBRA,
    VOLTAS_OBJETIVO, LINHA_LARGADA, PONTOS_DE_CONTROLE,
    MODO_DRIFT, DRIFT_PONTOS_BASE, DRIFT_PONTOS_VEL_FACTOR,
    DRIFT_DECAY_POR_SEG, DRIFT_COMBO_MAX, DRIFT_COMBO_STEP
)


class GerenciadorCorrida:
    def __init__(self, fonte=None, checkpoints=None, voltas_objetivo=1):
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
        
        # Tempos por checkpoint (estilo GRIP)
        self.tempo_checkpoint = {}     # carro -> {idx_checkpoint: tempo}
        self.tempo_secao = {}          # carro -> {secao: tempo} - para seções do GRIP
        self.ultimo_checkpoint_tempo = {}  # carro -> tempo do último checkpoint

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
        self.tempo_checkpoint[carro] = {}
        self.tempo_secao[carro] = {}
        self.ultimo_checkpoint_tempo[carro] = 0.0
        # Inicializar checkpoint_atual no carro para o HUD
        carro.checkpoint_atual = 0

    # --- Semáforo e tempo global ---
    def atualizar_contagem(self, dt):
        if self.iniciada:
            return
        self.contagem_regressiva -= dt
        if self.contagem_regressiva <= 0:
            self.iniciada = True

    def atualizar_tempo(self, dt, jogo_pausado=False):
        # Parar o tempo quando pausado ou quando todos finalizaram
        if self.iniciada and not jogo_pausado and not self.todos_finalizados():
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
    def _obter_retangulo_checkpoint(self, idx_cp):
        """
        Retorna um pygame.Rect representando o checkpoint retangular.
        O checkpoint tem 300px de largura/altura (tamanho dos tiles de pista).
        Se o checkpoint tiver ângulo salvo, usa ele. Senão, calcula baseado na direção.
        """
        if not self.checkpoints or idx_cp >= len(self.checkpoints):
            return None
        
        cp = self.checkpoints[idx_cp]
        # Suportar formato (x, y) ou (x, y, angulo)
        if len(cp) >= 3:
            cx, cy, angulo_salvo = cp[0], cp[1], cp[2]
            usar_angulo_salvo = True
        else:
            cx, cy = cp[0], cp[1]
            angulo_salvo = None
            usar_angulo_salvo = False
        
        CHECKPOINT_LARGURA = 300  # Largura dos tiles de pista (GRIP)
        CHECKPOINT_ESPESSURA = 4  # Espessura para detecção (mais generosa)
        
        # Se tiver ângulo salvo, usar ele
        if usar_angulo_salvo:
            # Normalizar ângulo para 0-360
            angulo = angulo_salvo % 360
            
            # Criar retângulo base (horizontal)
            rect_base = pygame.Rect(
                -CHECKPOINT_LARGURA // 2,
                -CHECKPOINT_ESPESSURA // 2,
                CHECKPOINT_LARGURA,
                CHECKPOINT_ESPESSURA
            )
            
            # Rotacionar o retângulo usando transformação
            # Para obter as dimensões finais, precisamos calcular os vértices rotacionados
            import math
            rad = math.radians(angulo)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)
            
            # Vértices do retângulo base
            w_half = CHECKPOINT_LARGURA // 2
            h_half = CHECKPOINT_ESPESSURA // 2
            vertices = [
                (-w_half, -h_half),
                (w_half, -h_half),
                (w_half, h_half),
                (-w_half, h_half)
            ]
            
            # Rotacionar vértices
            vertices_rot = []
            for vx, vy in vertices:
                rx = vx * cos_a - vy * sin_a
                ry = vx * sin_a + vy * cos_a
                vertices_rot.append((rx, ry))
            
            # Encontrar bounding box
            xs = [v[0] for v in vertices_rot]
            ys = [v[1] for v in vertices_rot]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            
            # Retornar retângulo centralizado
            return pygame.Rect(
                cx + int(min_x),
                cy + int(min_y),
                int(max_x - min_x),
                int(max_y - min_y)
            )
        else:
            # Fallback: calcular baseado na direção do movimento (comportamento antigo)
            if idx_cp < len(self.checkpoints) - 1:
                proximo_cp = self.checkpoints[idx_cp + 1]
                proximo_cx, proximo_cy = proximo_cp[0], proximo_cp[1]
            else:
                proximo_cp = self.checkpoints[0]
                proximo_cx, proximo_cy = proximo_cp[0], proximo_cp[1]
            
            dx = proximo_cx - cx
            dy = proximo_cy - cy
            
            # Se movimento é mais horizontal que vertical, o checkpoint deve ser VERTICAL (perpendicular)
            # Se movimento é mais vertical que horizontal, o checkpoint deve ser HORIZONTAL (perpendicular)
            if abs(dx) > abs(dy):
                # Movimento horizontal -> Checkpoint VERTICAL (1px de largura, 300px de altura)
                # Centralizado horizontalmente em cx
                return pygame.Rect(
                    cx - CHECKPOINT_ESPESSURA // 2,
                    cy - CHECKPOINT_LARGURA // 2,
                    CHECKPOINT_ESPESSURA,
                    CHECKPOINT_LARGURA
                )
            else:
                # Movimento vertical -> Checkpoint HORIZONTAL (300px de largura, 1px de altura)
                # Centralizado verticalmente em cy
                return pygame.Rect(
                    cx - CHECKPOINT_LARGURA // 2,
                    cy - CHECKPOINT_ESPESSURA // 2,
                    CHECKPOINT_LARGURA,
                    CHECKPOINT_ESPESSURA
                )
    
    def atualizar_progresso_carro(self, carro):
        if self.finalizou[carro]:
            return

        # Sistema de checkpoints dinâmico
        if self.checkpoints:
            # Verificar se passou pelo checkpoint atual
            idx_cp = self.proximo_checkpoint[carro] % len(self.checkpoints)
            if idx_cp < len(self.checkpoints):
                # Suportar formato (x, y) ou (x, y, angulo)
                cp = self.checkpoints[idx_cp]
                if len(cp) >= 3:
                    cx, cy = cp[0], cp[1]
                else:
                    cx, cy = cp[0], cp[1]
                
                # Obter retângulo do checkpoint
                checkpoint_rect = self._obter_retangulo_checkpoint(idx_cp)
                
                # Detecção de checkpoint com múltiplos métodos
                passou_checkpoint = False
                contra_mao = False
                
                # Verificar se o carro está dentro do retângulo do checkpoint
                if checkpoint_rect:
                    # Expandir o retângulo do checkpoint para considerar o tamanho do carro
                    # O carro tem aproximadamente 30-40px de largura, então expandimos 25px em cada direção
                    rect_expandido = checkpoint_rect.inflate(50, 50)  # 25px de cada lado = 50px total
                    # Verificar se o centro do carro está dentro do retângulo expandido
                    # Isso garante que mesmo que o carro passe pela borda, ainda será detectado
                    passou_checkpoint = rect_expandido.collidepoint(carro.x, carro.y)
                
                # Verificar direção do movimento
                if hasattr(carro, 'vx') and hasattr(carro, 'vy'):
                    velocidade = (carro.vx*carro.vx + carro.vy*carro.vy) ** 0.5
                    if velocidade > 0.1:  # Se estiver se movendo
                        # Calcular direção do movimento
                        direcao_movimento = (carro.vx, carro.vy)
                        
                        # Calcular direção esperada (do checkpoint atual para o próximo)
                        if idx_cp < len(self.checkpoints) - 1:
                            proximo_cp = self.checkpoints[idx_cp + 1]
                            proximo_cx, proximo_cy = proximo_cp[0], proximo_cp[1]
                        else:
                            # Se for o último checkpoint, direção para o primeiro
                            proximo_cp = self.checkpoints[0]
                            proximo_cx, proximo_cy = proximo_cp[0], proximo_cp[1]
                        
                        direcao_esperada = (proximo_cx - cx, proximo_cy - cy)
                        
                        # Normalizar vetores
                        norm_mov = (direcao_movimento[0]**2 + direcao_movimento[1]**2) ** 0.5
                        norm_esperada = (direcao_esperada[0]**2 + direcao_esperada[1]**2) ** 0.5
                        
                        if norm_mov > 0.1 and norm_esperada > 0.1:
                            # Calcular produto escalar para determinar direção
                            produto_escalar = (direcao_movimento[0] * direcao_esperada[0] + 
                                              direcao_movimento[1] * direcao_esperada[1]) / (norm_mov * norm_esperada)
                            
                            # Se produto escalar negativo, está indo na direção errada
                            if produto_escalar < -0.3 and passou_checkpoint:
                                contra_mao = True
                                # Armazenar flag de contra mão no carro
                                if not hasattr(carro, 'contra_mao'):
                                    carro.contra_mao = False
                                carro.contra_mao = True
                                carro.contra_mao_checkpoint = idx_cp
                                carro.contra_mao_tempo = 0.0  # Timer para mostrar aviso
                                return  # Não passar checkpoint se estiver contra mão
                            else:
                                # Se não está contra mão, limpar flag
                                if hasattr(carro, 'contra_mao'):
                                    carro.contra_mao = False
                
                if passou_checkpoint and not contra_mao:
                    # Limpar flag de contra mão se passou corretamente
                    if hasattr(carro, 'contra_mao'):
                        carro.contra_mao = False
                    
                    # Registrar tempo do checkpoint
                    tempo_atual = self.tempo_global
                    idx_cp = self.proximo_checkpoint[carro]
                    self.tempo_checkpoint[carro][idx_cp] = tempo_atual
                    
                    # Calcular tempo desde o último checkpoint
                    tempo_entre_checkpoints = tempo_atual - self.ultimo_checkpoint_tempo[carro]
                    self.ultimo_checkpoint_tempo[carro] = tempo_atual
                    
                    print(f"Carro {getattr(carro, 'nome', 'Desconhecido')} passou pelo checkpoint {idx_cp + 1}! Tempo: {tempo_atual:.2f}s (desde último: {tempo_entre_checkpoints:.2f}s)")
                    
                    self.proximo_checkpoint[carro] += 1
                    # Atualizar checkpoint_atual no carro para o HUD
                    carro.checkpoint_atual = self.proximo_checkpoint[carro] % len(self.checkpoints)
                    
                    # Verificar se completou uma volta
                    checkpoints_por_volta = len(self.checkpoints)
                    if self.proximo_checkpoint[carro] % checkpoints_por_volta == 0:
                        self.voltas[carro] += 1
                        # Registrar tempo da volta completa
                        if self.voltas[carro] > 0:
                            self.tempo_secao[carro][f'volta_{self.voltas[carro]}'] = tempo_atual
                        print(f"Carro {getattr(carro, 'nome', 'Desconhecido')} completou a volta {self.voltas[carro]}! Tempo: {tempo_atual:.2f}s")
                    
                    # Verificar se terminou a corrida
                    if self.proximo_checkpoint[carro] >= self.total_checkpoints_necessarios:
                        self.finalizou[carro] = True
                        if self.tempo_final[carro] is None:
                            self.tempo_final[carro] = self.tempo_global
                        print(f"Carro {getattr(carro, 'nome', 'Desconhecido')} terminou a corrida! Tempo total: {self.tempo_final[carro]:.2f}s")
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

