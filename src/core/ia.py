import math
import pygame

class IA:
    _trig_cache = {}
    
    def __init__(self, checkpoints, nome="IA-Melhorada-V2", dificuldade="medio"):
        self.checkpoints = checkpoints if checkpoints else []
        self.nome = nome
        self.checkpoint_atual = 0
        self.chegou = False
        self.debug = False
        self.dificuldade = dificuldade
        
        if not self.checkpoints or len(self.checkpoints) == 0:
            print(f"AVISO: IA {self.nome} não recebeu checkpoints válidos!")
        else:
            print(f"IA {self.nome} inicializada com {len(self.checkpoints)} checkpoints")
        
        self.pontos_navegacao = []
        self.ponto_navegacao_atual = 0
        self.atualizar_pontos_navegacao()
        
        self.velocidade_alvo = 5.0
        self.velocidade_maxima = 7.5
        self.velocidade_curva = 4.0
        
        self._configurar_dificuldade()
        
        self.lookahead_distance = 120.0
        self.lookahead_points = 5
        
        self.estado_curva = "reta"
        self.tempo_na_curva = 0.0
        self.curvatura_atual = 0.0
        self.curvatura_futura = 0.0
        
        self.tempo_travado = 0.0
        self.max_tempo_travado = 3.0
        self.ultima_posicao = None
        self.tentativas_recuperacao = 0
        self.max_tentativas_recuperacao = 2
        
        self.tempo_batido = 0.0
        self.max_tempo_batido = 1.0
        self.ultima_posicao_valida = None
        
        if self.checkpoints:
            self.alvo_x = self.checkpoints[0][0]
            self.alvo_y = self.checkpoints[0][1]
        else:
            self.alvo_x = 640
            self.alvo_y = 360
    
    def _configurar_dificuldade(self):
        """Configura os parâmetros baseados na dificuldade"""
        if self.dificuldade == "facil":
            self.velocidade_maxima = 5.0
            self.velocidade_curva = 2.5
            self.distancia_freio_curva = 80
            self.distancia_freio_checkpoint = 60
            self.angulo_max_curva = 25
            self.velocidade_max_curva = 3.0
            self.agressividade = 0.3
            self.precisao_curva = 0.8
            self.tempo_reacao = 0.15
        elif self.dificuldade == "dificil":
            self.velocidade_maxima = 12.0
            self.velocidade_curva = 7.0
            self.distancia_freio_curva = 15
            self.distancia_freio_checkpoint = 10
            self.angulo_max_curva = 80
            self.velocidade_max_curva = 9.0
            self.agressividade = 1.0
            self.precisao_curva = 0.99
            self.tempo_reacao = 0.01
        else:
            self.velocidade_maxima = 7.5
            self.velocidade_curva = 4.0
            self.distancia_freio_curva = 45
            self.distancia_freio_checkpoint = 35
            self.angulo_max_curva = 45
            self.velocidade_max_curva = 5.5
            self.agressividade = 0.75
            self.precisao_curva = 0.9
            self.tempo_reacao = 0.08
    
    def atualizar_pontos_navegacao(self):
        """Atualiza os pontos de navegação baseados nos checkpoints"""
        self.pontos_navegacao = self.checkpoints.copy()
        self.ponto_navegacao_atual = 0
        if self.pontos_navegacao:
            self.alvo_x = self.pontos_navegacao[0][0]
            self.alvo_y = self.pontos_navegacao[0][1]
    
    def calcular_curvatura(self, p1, p2, p3):
        """Calcula curvatura entre três pontos"""
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        
        v1x, v1y = x2 - x1, y2 - y1
        v2x, v2y = x3 - x2, y3 - y2
        
        l1_sq = v1x*v1x + v1y*v1y
        l2_sq = v2x*v2x + v2y*v2y
        
        if l1_sq < 0.01 or l2_sq < 0.01:
            return 0.0
        
        l1 = math.sqrt(l1_sq)
        l2 = math.sqrt(l2_sq)
        v1x, v1y = v1x/l1, v1y/l1
        v2x, v2y = v2x/l2, v2y/l2
        
        cross_product = v1x * v2y - v1y * v2x
        curvatura = abs(cross_product) / l1
        
        return curvatura
    
    def obter_pontos_lookahead(self, carro):
        """Obtém pontos à frente para antecipação"""
        if not self.pontos_navegacao:
            return []
        
        distancia_min_sq = float('inf')
        indice_inicial = 0
        carro_x, carro_y = carro.x, carro.y
        
        for i, (px, py) in enumerate(self.pontos_navegacao):
            dx = px - carro_x
            dy = py - carro_y
            dist_sq = dx*dx + dy*dy
            if dist_sq < distancia_min_sq:
                distancia_min_sq = dist_sq
                indice_inicial = i
        
        pontos_lookahead = []
        for i in range(min(self.lookahead_points, len(self.pontos_navegacao))):
            indice = (indice_inicial + i) % len(self.pontos_navegacao)
            pontos_lookahead.append(self.pontos_navegacao[indice])
        
        return pontos_lookahead
    
    def calcular_velocidade_alvo(self, carro):
        """Calcula velocidade alvo baseada na curvatura e dificuldade"""
        pontos_lookahead = self.obter_pontos_lookahead(carro)
        
        if len(pontos_lookahead) < 3:
            return self.velocidade_maxima
        
        num_calculos = min(len(pontos_lookahead) - 2, 3)
        curvaturas = []
        step = max(1, (len(pontos_lookahead) - 2) // num_calculos)
        for i in range(0, len(pontos_lookahead) - 2, step):
            curv = self.calcular_curvatura(
                pontos_lookahead[i],
                pontos_lookahead[i+1],
                pontos_lookahead[i+2]
            )
            curvaturas.append(curv)
        
        curvatura_media = sum(curvaturas) / len(curvaturas) if curvaturas else 0.0
        self.curvatura_atual = curvatura_media
        
        if self.dificuldade == "dificil":
            if curvatura_media > 0.15:
                return self.velocidade_curva * 0.6
            elif curvatura_media > 0.12:
                return self.velocidade_curva * 0.8
            elif curvatura_media > 0.08:
                return self.velocidade_curva * 1.2
            elif curvatura_media > 0.04:
                return self.velocidade_curva * 1.5
            elif curvatura_media > 0.02:
                return self.velocidade_maxima * 0.95
            else:
                return self.velocidade_maxima * 1.1
        else:
            if curvatura_media > 0.15:
                return self.velocidade_curva * 0.5
            elif curvatura_media > 0.12:
                return self.velocidade_curva * 0.75
            elif curvatura_media > 0.08:
                return self.velocidade_curva * 1.0
            elif curvatura_media > 0.04:
                return self.velocidade_curva * 1.2
            elif curvatura_media > 0.02:
                return self.velocidade_maxima * 0.8
            else:
                return self.velocidade_maxima
    
    def atualizar_estado_curva(self, carro, dt):
        """Atualiza estado da curva baseado na curvatura"""
        curvatura = self.curvatura_atual
        
        if curvatura > 0.08:  # Curva fechada
            if self.estado_curva == "reta":
                self.estado_curva = "entrando_curva"
                self.tempo_na_curva = 0.0
            elif self.estado_curva == "entrando_curva":
                self.estado_curva = "curva"
        elif curvatura > 0.03:  # Curva suave
            if self.estado_curva == "reta":
                self.estado_curva = "entrando_curva"
                self.tempo_na_curva = 0.0
            elif self.estado_curva == "curva":
                self.estado_curva = "saindo_curva"
        else:  # Reta
            if self.estado_curva in ["curva", "saindo_curva"]:
                self.estado_curva = "reta"
                self.tempo_na_curva = 0.0
        
        if self.estado_curva in ["entrando_curva", "curva", "saindo_curva"]:
            self.tempo_na_curva += dt
    
    def detectar_colisao(self, carro, superficie_mascara):
        return False
    
    def _vetor_frente(self, carro):
        angulo_key = int(carro.angulo * 10) / 10
        if angulo_key not in self._trig_cache:
            rad = math.radians(angulo_key)
            self._trig_cache[angulo_key] = {
                'cos': math.cos(rad),
                'sin': math.sin(rad)
            }
        
        cos_val = self._trig_cache[angulo_key]['cos']
        sin_val = self._trig_cache[angulo_key]['sin']
        return (-cos_val, sin_val)
    
    def _vetor_direita(self, carro):
        """Vetor unitário da direção lateral direita"""
        fx, fy = self._vetor_frente(carro)
        return (fy, -fx)
    
    @classmethod
    def limpar_cache_trig(cls):
        """Limpa o cache de cálculos trigonométricos"""
        cls._trig_cache.clear()
    
    def controlar(self, carro, superficie_mascara, is_on_track, dt, superficie_pista_renderizada=None, corrida_iniciada=True):
        """Controla o carro com sistema inteligente"""
        
        if not corrida_iniciada:
            return
        
        if not self.checkpoints or len(self.checkpoints) == 0:
            return
        
        vel_sq = carro.vx*carro.vx + carro.vy*carro.vy
        velocidade_atual = math.sqrt(vel_sq) if vel_sq > 0.01 else 0.0
        
        na_grama = getattr(carro, 'na_grama', False)
        
        posicao_atual = (carro.x, carro.y)
        if self.ultima_posicao is not None:
            dx = posicao_atual[0] - self.ultima_posicao[0]
            dy = posicao_atual[1] - self.ultima_posicao[1]
            dist_movimento_sq = dx*dx + dy*dy
            
            if na_grama:
                limite_travamento_grama = 1.0
                if dist_movimento_sq < limite_travamento_grama:
                    self.tempo_travado += dt
                else:
                    self.tempo_travado = max(0.0, self.tempo_travado - dt * 2.0)
            else:
                if dist_movimento_sq < 9.0:
                    self.tempo_travado += dt
                else:
                    self.tempo_travado = 0.0
        self.ultima_posicao = posicao_atual
        
        if na_grama and velocidade_atual > 0.5:
            self.tempo_travado = max(0.0, self.tempo_travado - dt * 0.5)
        
        colidiu = False
        if superficie_mascara is not None and superficie_pista_renderizada is None:
            colidiu = self.detectar_colisao(carro, superficie_mascara)
        
        if colidiu:
            if self.tempo_batido == 0.0:
                self.ultima_posicao_valida = (carro.x, carro.y)
            
            self.tempo_batido += dt
            
            if self.tempo_batido > self.max_tempo_batido:
                carro._step(False, False, False, True, False, superficie_mascara, dt, None, superficie_pista_renderizada)
                return
            else:
                carro._step(False, False, False, True, False, superficie_mascara, dt, None, superficie_pista_renderizada)
                return
        else:
            if self.tempo_batido > 0.0:
                self.tempo_batido = 0.0
        
        if not self.checkpoints or len(self.checkpoints) == 0:
            return
        
        checkpoint_idx = self.checkpoint_atual % len(self.checkpoints)
        self.alvo_x = self.checkpoints[checkpoint_idx][0]
        self.alvo_y = self.checkpoints[checkpoint_idx][1]
        
        if not hasattr(self, '_ultimo_debug_tempo'):
            self._ultimo_debug_tempo = 0.0
        if pygame.time.get_ticks() / 1000.0 - self._ultimo_debug_tempo > 2.0:
            print(f"[IA {self.nome}] Checkpoint atual: {checkpoint_idx}/{len(self.checkpoints)}")
            print(f"[IA {self.nome}] Alvo: ({self.alvo_x:.1f}, {self.alvo_y:.1f})")
            print(f"[IA {self.nome}] Carro pos: ({carro.x:.1f}, {carro.y:.1f})")
            self._ultimo_debug_tempo = pygame.time.get_ticks() / 1000.0
        
        checkpoint_idx = self.checkpoint_atual % len(self.checkpoints)
        if checkpoint_idx < len(self.checkpoints):
            cp = self.checkpoints[checkpoint_idx]
            if len(cp) >= 3:
                cx, cy, angulo_salvo = cp[0], cp[1], cp[2]
                usar_angulo_salvo = True
            else:
                cx, cy = cp[0], cp[1]
                angulo_salvo = None
                usar_angulo_salvo = False
            
            CHECKPOINT_LARGURA = 300
            CHECKPOINT_ESPESSURA = 1
            
            if usar_angulo_salvo:
                angulo = angulo_salvo % 360
                rad = math.radians(angulo)
                cos_a = math.cos(rad)
                sin_a = math.sin(rad)
                
                w_half = CHECKPOINT_LARGURA // 2
                h_half = CHECKPOINT_ESPESSURA // 2
                vertices = [
                    (-w_half, -h_half),
                    (w_half, -h_half),
                    (w_half, h_half),
                    (-w_half, h_half)
                ]
                
                vertices_rot = []
                for vx, vy in vertices:
                    rx = vx * cos_a - vy * sin_a
                    ry = vx * sin_a + vy * cos_a
                    vertices_rot.append((rx, ry))
                
                xs = [v[0] for v in vertices_rot]
                ys = [v[1] for v in vertices_rot]
                min_x, max_x = min(xs), max(xs)
                min_y, max_y = min(ys), max(ys)
                
                checkpoint_rect = pygame.Rect(
                    cx + int(min_x),
                    cy + int(min_y),
                    int(max_x - min_x),
                    int(max_y - min_y)
                )
            else:
                if checkpoint_idx < len(self.checkpoints) - 1:
                    proximo_cp = self.checkpoints[checkpoint_idx + 1]
                    proximo_cx, proximo_cy = proximo_cp[0], proximo_cp[1]
                else:
                    proximo_cp = self.checkpoints[0]
                    proximo_cx, proximo_cy = proximo_cp[0], proximo_cp[1]
                
                dx_checkpoint = proximo_cx - cx
                dy_checkpoint = proximo_cy - cy
                
                if abs(dx_checkpoint) > abs(dy_checkpoint):
                    checkpoint_rect = pygame.Rect(
                        cx - 1,
                        cy - CHECKPOINT_LARGURA // 2,
                        2,
                        CHECKPOINT_LARGURA
                    )
                else:
                    checkpoint_rect = pygame.Rect(
                        cx - CHECKPOINT_LARGURA // 2,
                        cy - 1,
                        CHECKPOINT_LARGURA,
                        2
                    )
            
            checkpoint_rect = checkpoint_rect.inflate(10, 10)
            
            if checkpoint_rect.collidepoint(carro.x, carro.y):
                self.checkpoint_atual = (self.checkpoint_atual + 1) % len(self.checkpoints)
                self.tempo_travado = 0.0
                self.tentativas_recuperacao = 0
        
        checkpoint_idx = self.checkpoint_atual % len(self.checkpoints)
        self.alvo_x = self.checkpoints[checkpoint_idx][0]
        self.alvo_y = self.checkpoints[checkpoint_idx][1]
        
        dx = self.alvo_x - carro.x
        dy = self.alvo_y - carro.y
        distancia_sq = dx*dx + dy*dy
        distancia = math.sqrt(distancia_sq) if distancia_sq > 0.01 else 0.0
        
        angulo_alvo = math.degrees(math.atan2(dy, -dx))
        diff_angulo = (angulo_alvo - carro.angulo + 180) % 360 - 180
        
        curvatura_futura_max = 0.0
        if len(self.checkpoints) >= 3:
            checkpoint_idx = self.checkpoint_atual % len(self.checkpoints)
            for offset in range(1, min(4, len(self.checkpoints))):
                idx1 = (checkpoint_idx + offset - 1) % len(self.checkpoints)
                idx2 = (checkpoint_idx + offset) % len(self.checkpoints)
                idx3 = (checkpoint_idx + offset + 1) % len(self.checkpoints)
                
                cp1 = self.checkpoints[idx1]
                cp2 = self.checkpoints[idx2]
                cp3 = self.checkpoints[idx3]
                
                p1 = (cp1[0], cp1[1])
                p2 = (cp2[0], cp2[1])
                p3 = (cp3[0], cp3[1])
                
                curv_futura = self.calcular_curvatura(p1, p2, p3)
                curvatura_futura_max = max(curvatura_futura_max, curv_futura)
        
        self.curvatura_futura = curvatura_futura_max
        
        realmente_travado = self.tempo_travado > self.max_tempo_travado and velocidade_atual < 0.3
        
        if self.tempo_travado > 2.0 and self.debug:
            print(f"IA {self.nome}: Quase travado - tempo: {self.tempo_travado:.1f}s, velocidade: {velocidade_atual:.2f}, na_grama: {na_grama}, checkpoint: {self.checkpoint_atual + 1}")
        
        if realmente_travado:
            print(f"IA {self.nome}: TRAVADO detectado - tempo: {self.tempo_travado:.1f}s, velocidade: {velocidade_atual:.2f}, checkpoint atual: {self.checkpoint_atual + 1}, tentativas: {self.tentativas_recuperacao}")
            if self.tentativas_recuperacao < self.max_tentativas_recuperacao:
                self.tentativas_recuperacao += 1
                
                checkpoint_mais_proximo = self.checkpoint_atual
                distancia_minima = float('inf')
                
                for i, cp in enumerate(self.checkpoints):
                    cx, cy = cp[0], cp[1]
                    dist_sq = (carro.x - cx)**2 + (carro.y - cy)**2
                    if dist_sq < distancia_minima:
                        distancia_minima = dist_sq
                        checkpoint_mais_proximo = i
                
                if checkpoint_mais_proximo != self.checkpoint_atual:
                    self.checkpoint_atual = checkpoint_mais_proximo
                    print(f"IA {self.nome}: Recuperação - mudou para checkpoint mais próximo: {checkpoint_mais_proximo + 1}")
                else:
                    self.checkpoint_atual = (self.checkpoint_atual + 1) % len(self.checkpoints)
                    print(f"IA {self.nome}: Recuperação - avançou para próximo checkpoint: {(self.checkpoint_atual % len(self.checkpoints)) + 1}")
                
                self.tempo_travado = 0.0
                
                checkpoint_idx = self.checkpoint_atual % len(self.checkpoints)
                self.alvo_x = self.checkpoints[checkpoint_idx][0]
                self.alvo_y = self.checkpoints[checkpoint_idx][1]
                dx = self.alvo_x - carro.x
                dy = self.alvo_y - carro.y
            else:
                checkpoint_mais_proximo = 0
                distancia_minima = float('inf')
                
                for i, cp in enumerate(self.checkpoints):
                    cx, cy = cp[0], cp[1]
                    dist_sq = (carro.x - cx)**2 + (carro.y - cy)**2
                    if dist_sq < distancia_minima:
                        distancia_minima = dist_sq
                        checkpoint_mais_proximo = i
                
                self.checkpoint_atual = checkpoint_mais_proximo
                self.tentativas_recuperacao = 0
                self.tempo_travado = 0.0
                self.alvo_x = self.checkpoints[checkpoint_mais_proximo][0]
                self.alvo_y = self.checkpoints[checkpoint_mais_proximo][1]
                dx = self.alvo_x - carro.x
                dy = self.alvo_y - carro.y
                print(f"IA {self.nome}: Recuperação final - mudou para checkpoint mais próximo: {checkpoint_mais_proximo + 1} (não resetou para 0)")
        
        self.velocidade_alvo = self.calcular_velocidade_alvo(carro)
        self.atualizar_estado_curva(carro, dt)
        
        acelerar = True
        frear_re = False
        
        if na_grama:
            frear_re = True
            acelerar = False
        
        if self.curvatura_futura > 0.12:
            if distancia < self.distancia_freio_curva * 3.0:
                if velocidade_atual > self.velocidade_max_curva * 0.4:
                    frear_re = True
                    acelerar = False
            if velocidade_atual > self.velocidade_max_curva * 0.5:
                frear_re = True
                acelerar = False
        elif self.curvatura_futura > 0.08:
            if distancia < self.distancia_freio_curva * 2.5:
                if velocidade_atual > self.velocidade_max_curva * 0.5:
                    frear_re = True
                    acelerar = False
        elif self.curvatura_futura > 0.05:
            if distancia < self.distancia_freio_curva * 1.8:
                if velocidade_atual > self.velocidade_max_curva * 0.65:
                    frear_re = True
                    acelerar = False
        
        if abs(diff_angulo) > 45 and velocidade_atual > self.velocidade_max_curva * 0.9:
            frear_re = True
            acelerar = False
        elif abs(diff_angulo) > 35 and velocidade_atual > self.velocidade_max_curva * 1.0:
            frear_re = True
            acelerar = False
        elif abs(diff_angulo) > 30 and velocidade_atual > self.velocidade_max_curva * 1.1:
            frear_re = True
            acelerar = False
        
        if distancia < self.distancia_freio_checkpoint and velocidade_atual > 1.2:
            frear_re = True
            acelerar = False
        
        velocidade_max_curva_ajustada = self.velocidade_max_curva
        if self.curvatura_atual > 0.12:
            velocidade_max_curva_ajustada = self.velocidade_max_curva * 0.35
        elif self.curvatura_atual > 0.08:
            velocidade_max_curva_ajustada = self.velocidade_max_curva * 0.55
        elif self.curvatura_atual > 0.05:
            velocidade_max_curva_ajustada = self.velocidade_max_curva * 0.7
        elif self.curvatura_atual > 0.03:
            velocidade_max_curva_ajustada = self.velocidade_max_curva * 0.85
        
        if abs(diff_angulo) > self.angulo_max_curva and velocidade_atual > velocidade_max_curva_ajustada:
            frear_re = True
            acelerar = False
        
        if self.curvatura_atual > 0.12:
            velocidade_max_curva_fechada = self.velocidade_max_curva * 0.2
            if velocidade_atual > velocidade_max_curva_fechada:
                frear_re = True
                acelerar = False
        elif self.curvatura_atual > 0.08:
            velocidade_max_curva_fechada = self.velocidade_max_curva * 0.4
            if velocidade_atual > velocidade_max_curva_fechada:
                frear_re = True
                acelerar = False
        elif self.curvatura_atual > 0.05:
            velocidade_max_curva_fechada = self.velocidade_max_curva * 0.65
            if velocidade_atual > velocidade_max_curva_fechada and abs(diff_angulo) > 15:
                frear_re = True
                acelerar = False
        elif self.curvatura_atual > 0.03:
            if abs(diff_angulo) > 30 and velocidade_atual > self.velocidade_max_curva * 0.8:
                frear_re = True
                acelerar = False
        
        if distancia < self.distancia_freio_curva and velocidade_atual > self.velocidade_maxima * 0.8:
            frear_re = True
            acelerar = False
        
        if self.curvatura_atual > 0.10:
            distancia_freio_ajustada = self.distancia_freio_curva * 3.5
            if distancia < distancia_freio_ajustada and velocidade_atual > self.velocidade_maxima * 0.3:
                frear_re = True
                acelerar = False
        elif self.curvatura_atual > 0.08:
            distancia_freio_ajustada = self.distancia_freio_curva * 2.5
            if distancia < distancia_freio_ajustada and velocidade_atual > self.velocidade_maxima * 0.4:
                frear_re = True
                acelerar = False
        elif self.curvatura_atual > 0.05:
            distancia_freio_ajustada = self.distancia_freio_curva * 1.6
            if distancia < distancia_freio_ajustada and velocidade_atual > self.velocidade_maxima * 0.6 and abs(diff_angulo) > 25:
                frear_re = True
                acelerar = False
        
        if abs(diff_angulo) > 70 and velocidade_atual > 0.8:
            frear_re = True
            acelerar = False
        elif abs(diff_angulo) > 60 and velocidade_atual > self.velocidade_max_curva * 0.8:
            frear_re = True
            acelerar = False
        
        if abs(diff_angulo) < 12 and distancia > self.distancia_freio_checkpoint and velocidade_atual < self.velocidade_maxima * 0.9:
            acelerar = True
            frear_re = False
        
        if self.dificuldade == "dificil":
            if self.curvatura_atual <= 0.12:
                if abs(diff_angulo) < 40 and distancia > self.distancia_freio_checkpoint and velocidade_atual < self.velocidade_maxima * 0.98:
                    acelerar = True
                    frear_re = False
                if abs(diff_angulo) < 50 and self.curvatura_atual < 0.08 and velocidade_atual < self.velocidade_maxima * 0.9:
                    acelerar = True
                    frear_re = False
                if abs(diff_angulo) < 25 and self.curvatura_atual < 0.10 and velocidade_atual < self.velocidade_maxima * 0.85:
                    acelerar = True
                    frear_re = False
            if abs(diff_angulo) < 15 and self.curvatura_atual < 0.03:
                acelerar = True
                frear_re = False
        
        if self.estado_curva == "entrando_curva" and velocidade_atual > self.velocidade_alvo:
            frear_re = True
            acelerar = False
        elif self.estado_curva == "curva" and velocidade_atual > self.velocidade_alvo * 1.2:
            frear_re = True
            acelerar = False
        elif self.estado_curva == "curva" and self.curvatura_atual > 0.10:
            if velocidade_atual > self.velocidade_alvo * 0.7:
                frear_re = True
                acelerar = False
        elif self.estado_curva == "curva" and self.curvatura_atual > 0.08:
            if velocidade_atual > self.velocidade_alvo * 0.8:
                frear_re = True
                acelerar = False
        elif self.estado_curva == "curva" and self.curvatura_atual > 0.05:
            if velocidade_atual > self.velocidade_alvo * 0.9:
                frear_re = True
                acelerar = False
        elif self.estado_curva == "reta" and velocidade_atual < self.velocidade_alvo * 0.8:
            acelerar = True
            frear_re = False
        
        direita = diff_angulo < -2
        esquerda = diff_angulo > 2
        
        turbo_pressed = False
        if self.dificuldade == "dificil":
            if self.curvatura_atual > 0.12:
                turbo_pressed = False
            elif self.curvatura_atual > 0.08:
                if abs(diff_angulo) < 20 and velocidade_atual < self.velocidade_max_curva * 0.8:
                    turbo_pressed = True
            elif abs(diff_angulo) > 15 and velocidade_atual > 1.0:
                turbo_pressed = True
            elif abs(diff_angulo) < 15 and velocidade_atual > 2.0 and velocidade_atual < self.velocidade_maxima * 0.9:
                turbo_pressed = True
            elif abs(diff_angulo) < 30 and self.curvatura_atual < 0.06 and velocidade_atual > 1.5:
                turbo_pressed = True
            elif abs(diff_angulo) < 45 and self.curvatura_atual < 0.08 and velocidade_atual > 2.5 and velocidade_atual < self.velocidade_maxima * 0.8:
                turbo_pressed = True
        elif self.dificuldade == "medio":
            if abs(diff_angulo) > 30 and velocidade_atual > 2.0:
                turbo_pressed = True
            elif abs(diff_angulo) < 15 and velocidade_atual > 2.5 and velocidade_atual < self.velocidade_maxima * 0.8:
                turbo_pressed = True
        
        if self.dificuldade == "medio":
            if abs(diff_angulo) < 25 and distancia > self.distancia_freio_checkpoint and velocidade_atual < self.velocidade_maxima * 0.85:
                acelerar = True
                frear_re = False
            if abs(diff_angulo) < 35 and self.curvatura_atual < 0.06 and velocidade_atual < self.velocidade_maxima * 0.75:
                acelerar = True
                frear_re = False
        
        if self.dificuldade == "dificil":
            if self.curvatura_atual > 0.12:
                if abs(diff_angulo) < 15 and velocidade_atual < self.velocidade_max_curva * 0.6:
                    acelerar = True
                    frear_re = False
                else:
                    frear_re = True
                    acelerar = False
            elif self.curvatura_atual > 0.08:
                if abs(diff_angulo) < 25 and velocidade_atual < self.velocidade_max_curva * 0.75:
                    acelerar = True
                    frear_re = False
            elif not (abs(diff_angulo) > 70 and velocidade_atual > 5.0):
                acelerar = True
                frear_re = False
        
        if pygame.time.get_ticks() / 1000.0 - self._ultimo_debug_tempo > 2.0:
            print(f"[IA {self.nome}] Controles: acelerar={acelerar}, frear={frear_re}, direita={direita}, esquerda={esquerda}, turbo={turbo_pressed}")
            print(f"[IA {self.nome}] Velocidade: {velocidade_atual:.2f}, diff_angulo: {diff_angulo:.1f}°, distancia: {distancia:.1f}")
        
        carro._step(acelerar, direita, esquerda, frear_re, turbo_pressed, superficie_mascara, dt, None, superficie_pista_renderizada)
        
        self.estado_freio = frear_re
        self.estado_aceleracao = acelerar
        self.velocidade_atual = velocidade_atual
        self.distancia_atual = distancia
        self.diff_angulo_atual = diff_angulo
    
    def desenhar_debug(self, superficie, camera=None, mostrar_todos_checkpoints=False):
        """Desenha debug visual da IA"""
        if not self.debug or not camera:
            return
        
        try:
            fonte_debug = pygame.font.SysFont("consolas", 16)
            fonte_debug_bold = pygame.font.SysFont("consolas", 16, bold=True)
            
            for i, cp in enumerate(self.checkpoints):
                cx, cy = cp[0], cp[1] if len(cp) >= 2 else (cp[0], cp[1])
                screen_x, screen_y = camera.mundo_para_tela(cx, cy)
                
                if not mostrar_todos_checkpoints and i != self.checkpoint_atual:
                    continue
                
                if i == self.checkpoint_atual:
                    cor = (255, 0, 0)
                    raio = 20
                elif i < self.checkpoint_atual:
                    cor = (0, 255, 0)
                    raio = 12
                else:
                    cor = (128, 128, 128)
                    raio = 12
                
                pygame.draw.circle(superficie, cor, (int(screen_x), int(screen_y)), raio)
                
                texto = fonte_debug_bold.render(str(i+1), True, (255, 255, 255))
                texto_rect = texto.get_rect(center=(int(screen_x), int(screen_y)))
                superficie.blit(texto, texto_rect)
            
            if not self.chegou and self.checkpoints:
                checkpoint_display = (self.checkpoint_atual % len(self.checkpoints)) + 1
                
                texto = fonte_debug.render(f"Checkpoint {checkpoint_display}/{len(self.checkpoints)}", True, (255, 255, 255))
                superficie.blit(texto, (10, 10))
                
                checkpoint_idx = self.checkpoint_atual % len(self.checkpoints)
                alvo_x, alvo_y = self.checkpoints[checkpoint_idx]
                texto_alvo = fonte_debug.render(f"Alvo: ({alvo_x:.0f}, {alvo_y:.0f})", True, (255, 255, 255))
                superficie.blit(texto_alvo, (10, 30))
                
                # Informações adicionais
                if hasattr(self, 'velocidade_alvo'):
                    texto_vel = fonte_debug.render(f"Vel Alvo: {self.velocidade_alvo:.1f}", True, (255, 255, 255))
                    superficie.blit(texto_vel, (10, 50))
                
                if hasattr(self, 'curvatura_atual'):
                    texto_curv = fonte_debug.render(f"Curvatura: {self.curvatura_atual:.3f}", True, (255, 255, 255))
                    superficie.blit(texto_curv, (10, 70))
                
                if hasattr(self, 'estado_curva'):
                    cor_estado = (0, 255, 0) if self.estado_curva == "reta" else (255, 165, 0) if "curva" in self.estado_curva else (255, 255, 0)
                    texto_estado = fonte_debug.render(f"Estado: {self.estado_curva.upper()}", True, cor_estado)
                    superficie.blit(texto_estado, (10, 90))
                
                # Indicador de travamento
                if hasattr(self, 'tempo_travado') and self.tempo_travado > 0:
                    texto_travado = fonte_debug.render(f"TRAVADO: {self.tempo_travado:.1f}s", True, (255, 0, 255))
                    superficie.blit(texto_travado, (10, 110))
                
                if hasattr(self, 'tempo_batido') and self.tempo_batido > 0:
                    texto_batido = fonte_debug.render(f"BATIDO: {self.tempo_batido:.1f}s", True, (255, 0, 0))
                    superficie.blit(texto_batido, (10, 130))
            else:
                texto_chegou = fonte_debug.render("SEQUÊNCIA COMPLETA!", True, (0, 255, 0))
                superficie.blit(texto_chegou, (10, 10))
                
        except Exception as e:
            print(f"Erro ao desenhar debug da IA: {e}")
