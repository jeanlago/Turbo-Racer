import math
import pygame

class IA:
    """
    IA melhorada baseada no sistema do jogo_antigo mas com melhorias:
    - Sistema de recuperação mais robusto
    - Detecção de colisão melhorada
    - Controle de velocidade mais inteligente
    - Sistema de lookahead para curvas
    - Otimizações de performance
    """
    
    # Cache para cálculos trigonométricos (otimização)
    _trig_cache = {}
    
    def __init__(self, checkpoints, nome="IA-Melhorada-V2"):
        self.checkpoints = checkpoints
        self.nome = nome
        self.checkpoint_atual = 0
        self.chegou = False
        self.debug = False
        
        # Sistema de navegação melhorado
        self.pontos_navegacao = []
        self.ponto_navegacao_atual = 0
        self.atualizar_pontos_navegacao()
        
        # Controle de velocidade baseado na física
        self.velocidade_alvo = 3.0
        self.velocidade_maxima = 4.0
        self.velocidade_curva = 1.5
        
        # Sistema de lookahead para antecipação
        self.lookahead_distance = 80.0
        self.lookahead_points = 2
        
        # Estado da IA
        self.estado_curva = "reta"
        self.tempo_na_curva = 0.0
        self.curvatura_atual = 0.0
        
        # Sistema de recuperação melhorado (baseado no jogo_antigo)
        self.tempo_travado = 0.0
        self.max_tempo_travado = 3.0  # Reduzido de 5.0 para 3.0
        self.ultima_posicao = None
        self.tentativas_recuperacao = 0
        self.max_tentativas_recuperacao = 2  # Reduzido de 3 para 2
        
        # Sistema de colisão
        self.tempo_batido = 0.0
        self.max_tempo_batido = 1.0
        self.ultima_posicao_valida = None
        
        if self.checkpoints:
            self.alvo_x = self.checkpoints[0][0]
            self.alvo_y = self.checkpoints[0][1]
        else:
            self.alvo_x = 640
            self.alvo_y = 360
    
    def atualizar_pontos_navegacao(self):
        """Atualiza os pontos de navegação baseados nos checkpoints"""
        self.pontos_navegacao = self.checkpoints.copy()
        self.ponto_navegacao_atual = 0
        if self.pontos_navegacao:
            self.alvo_x = self.pontos_navegacao[0][0]
            self.alvo_y = self.pontos_navegacao[0][1]
    
    def calcular_curvatura(self, p1, p2, p3):
        """Calcula curvatura entre três pontos (otimizado)"""
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        
        # Vetores
        v1x, v1y = x2 - x1, y2 - y1
        v2x, v2y = x3 - x2, y3 - y2
        
        # Comprimentos ao quadrado (evitar sqrt quando possível)
        l1_sq = v1x*v1x + v1y*v1y
        l2_sq = v2x*v2x + v2y*v2y
        
        if l1_sq < 0.01 or l2_sq < 0.01:  # 0.1^2 = 0.01
            return 0.0
        
        # Normalizar
        l1 = math.sqrt(l1_sq)
        v1x, v1y = v1x/l1, v1y/l1
        v2x, v2y = v2x/math.sqrt(l2_sq), v2y/math.sqrt(l2_sq)
        
        # Curvatura
        cross_product = v1x * v2y - v1y * v2x
        curvatura = abs(cross_product) / l1
        
        return curvatura
    
    def obter_pontos_lookahead(self, carro):
        """Obtém pontos à frente para antecipação (otimizado)"""
        if not self.pontos_navegacao:
            return []
        
        # Encontrar checkpoint mais próximo usando distância ao quadrado
        distancia_min_sq = float('inf')
        indice_inicial = 0
        
        for i, (px, py) in enumerate(self.pontos_navegacao):
            dist_sq = (px - carro.x)**2 + (py - carro.y)**2
            if dist_sq < distancia_min_sq:
                distancia_min_sq = dist_sq
                indice_inicial = i
        
        # Pegar pontos à frente (limitado para performance)
        pontos_lookahead = []
        for i in range(min(self.lookahead_points, len(self.pontos_navegacao))):
            indice = (indice_inicial + i) % len(self.pontos_navegacao)
            pontos_lookahead.append(self.pontos_navegacao[indice])
        
        return pontos_lookahead
    
    def calcular_velocidade_alvo(self, carro):
        """Calcula velocidade alvo baseada na curvatura"""
        pontos_lookahead = self.obter_pontos_lookahead(carro)
        
        if len(pontos_lookahead) < 3:
            return self.velocidade_maxima
        
        # Calcular curvatura média
        curvaturas = []
        for i in range(len(pontos_lookahead) - 2):
            curv = self.calcular_curvatura(
                pontos_lookahead[i],
                pontos_lookahead[i+1],
                pontos_lookahead[i+2]
            )
            curvaturas.append(curv)
        
        curvatura_media = sum(curvaturas) / len(curvaturas) if curvaturas else 0.0
        self.curvatura_atual = curvatura_media
        
        # Ajustar velocidade baseada na curvatura
        if curvatura_media > 0.15:  # Curva muito fechada
            return 1.0
        elif curvatura_media > 0.08:  # Curva fechada
            return 1.5
        elif curvatura_media > 0.04:  # Curva média
            return 2.5
        elif curvatura_media > 0.02:  # Curva suave
            return 3.2
        else:  # Reta
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
        """Detecta colisão com a pista (otimizado)"""
        from core.pista import eh_pixel_transitavel
        
        fx, fy = self._vetor_frente(carro)
        rx, ry = self._vetor_direita(carro)
        
        # Reduzir ainda mais pontos de verificação para melhor performance
        pontos_verificacao = [
            (0, 0), (6, 0), (-6, 0)  # Apenas centro e frente/trás
        ]
        
        for ox, oy in pontos_verificacao:
            px = int(carro.x + ox * fx + oy * rx)
            py = int(carro.y + ox * fy + oy * ry)
            if not eh_pixel_transitavel(superficie_mascara, px, py):
                return True
        return False
    
    def _vetor_frente(self, carro):
        """Vetor unitário da direção frontal (com cache)"""
        # Usar cache para evitar recálculos
        angulo_key = int(carro.angulo * 10) / 10  # Arredondar para 1 casa decimal
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
        """Vetor unitário da direção lateral direita (com cache)"""
        fx, fy = self._vetor_frente(carro)
        return (fy, -fx)
    
    @classmethod
    def limpar_cache_trig(cls):
        """Limpa o cache de cálculos trigonométricos"""
        cls._trig_cache.clear()
    
    def controlar(self, carro, superficie_mascara, is_on_track, dt):
        """Controla o carro com sistema inteligente baseado no jogo_antigo"""
        
        if not self.checkpoints:
            self.chegou = True
            return
        
        # Calcular velocidade atual
        velocidade_atual = math.sqrt(carro.vx*carro.vx + carro.vy*carro.vy)
        
        # DETECÇÃO DE TRAVAMENTO (baseado no jogo_antigo)
        posicao_atual = (carro.x, carro.y)
        if self.ultima_posicao is not None:
            dist_movimento = math.sqrt((posicao_atual[0] - self.ultima_posicao[0])**2 + 
                                     (posicao_atual[1] - self.ultima_posicao[1])**2)
            if dist_movimento < 3.0:  # Movimento mínimo reduzido
                self.tempo_travado += dt
            else:
                self.tempo_travado = 0.0
        self.ultima_posicao = posicao_atual
        
        # DETECÇÃO DE COLISÃO
        colidiu = False
        if superficie_mascara is not None:
            colidiu = self.detectar_colisao(carro, superficie_mascara)
        
        if colidiu:
            if self.tempo_batido == 0.0:
                self.ultima_posicao_valida = (carro.x, carro.y)
                print(f"{self.nome} BATEU! Iniciando recuperação...")
            
            self.tempo_batido += dt
            
            if self.tempo_batido > self.max_tempo_batido:
                print(f"{self.nome} tentando dar ré...")
                carro.atualizar_com_ai(superficie_mascara, dt, self.checkpoints, 50)
                return
            else:
                carro.atualizar_com_ai(superficie_mascara, dt, self.checkpoints, 50)
                return
        else:
            if self.tempo_batido > 0.0:
                print(f"{self.nome} se recuperou da colisão!")
            self.tempo_batido = 0.0
        
        # NAVEGAÇÃO
        checkpoint_idx = self.checkpoint_atual % len(self.checkpoints)
        self.alvo_x = self.checkpoints[checkpoint_idx][0]
        self.alvo_y = self.checkpoints[checkpoint_idx][1]
        
        # Calcular distâncIA e ângulo
        dx = self.alvo_x - carro.x
        dy = self.alvo_y - carro.y
        distancia = math.sqrt(dx*dx + dy*dy)
        
        # Calcular ângulo para o alvo (mesmo sistema do jogo_antigo)
        angulo_alvo = math.degrees(math.atan2(dy, -dx))  # -dx porque 0° aponta para -X
        diff_angulo = (angulo_alvo - carro.angulo + 180) % 360 - 180
        
        # DETECÇÃO DE CHECKPOINTS (baseado no jogo_antigo)
        if distancia < 60:  # Raio aumentado para detecção mais rápida
            self.checkpoint_atual += 1
            self.tempo_travado = 0.0
            self.tentativas_recuperacao = 0
            print(f"{self.nome} chegou ao checkpoint {self.checkpoint_atual}! (Loop: {self.checkpoint_atual // len(self.checkpoints) + 1})")
            
            # Atualizar para o próximo checkpoint
            checkpoint_idx = self.checkpoint_atual % len(self.checkpoints)
            self.alvo_x = self.checkpoints[checkpoint_idx][0]
            self.alvo_y = self.checkpoints[checkpoint_idx][1]
            dx = self.alvo_x - carro.x
            dy = self.alvo_y - carro.y
        
        # LÓGICA DE RECUPERAÇÃO (baseada no jogo_antigo)
        elif self.tempo_travado > self.max_tempo_travado:
            if self.tentativas_recuperacao < self.max_tentativas_recuperacao:
                self.tentativas_recuperacao += 1
                print(f"{self.nome} travado! Tentativa de recuperação {self.tentativas_recuperacao}/{self.max_tentativas_recuperacao}")
                
                # EstratégIA de recuperação: pular para o próximo checkpoint
                self.checkpoint_atual += 1
                self.tempo_travado = 0.0
                
                # Atualizar alvo
                checkpoint_idx = self.checkpoint_atual % len(self.checkpoints)
                self.alvo_x = self.checkpoints[checkpoint_idx][0]
                self.alvo_y = self.checkpoints[checkpoint_idx][1]
                dx = self.alvo_x - carro.x
                dy = self.alvo_y - carro.y
            else:
                # Se esgotou tentativas, resetar para o início
                print(f"{self.nome} esgotou tentativas! Resetando para checkpoint inicial.")
                self.checkpoint_atual = 0
                self.tentativas_recuperacao = 0
                self.tempo_travado = 0.0
                self.alvo_x = self.checkpoints[0][0]
                self.alvo_y = self.checkpoints[0][1]
                dx = self.alvo_x - carro.x
                dy = self.alvo_y - carro.y
        
        # SISTEMA INTELIGENTE DE CURVAS
        self.velocidade_alvo = self.calcular_velocidade_alvo(carro)
        self.atualizar_estado_curva(carro, dt)
        
        # CONTROLE DE VELOCIDADE (baseado no jogo_antigo mas melhorado)
        acelerar = True
        frear_re = False
        
        # 1. Frear se estiver muito próximo do checkpoint
        if distancia < 50 and velocidade_atual > 1.2:
            frear_re = True
            acelerar = False
        
        # 2. Frear se precisar fazer uma curva muito fechada
        if abs(diff_angulo) > 40 and velocidade_atual > 1.8:
            frear_re = True
            acelerar = False
        
        # 3. Frear se estiver indo muito rápido em relação à distâncIA
        if distancia < 70 and velocidade_atual > 2.8:
            frear_re = True
            acelerar = False
        
        # 4. Frear se estiver indo na direção errada
        if abs(diff_angulo) > 80 and velocidade_atual > 0.8:
            frear_re = True
            acelerar = False
        
        # 5. Acelerar apenas se estiver alinhado e não muito próximo
        if abs(diff_angulo) < 12 and distancia > 45 and velocidade_atual < 3.8:
            acelerar = True
            frear_re = False
        
        # 6. Controle baseado no estado da curva
        if self.estado_curva == "entrando_curva" and velocidade_atual > self.velocidade_alvo:
            frear_re = True
            acelerar = False
        elif self.estado_curva == "curva" and velocidade_atual > self.velocidade_alvo * 1.2:
            frear_re = True
            acelerar = False
        elif self.estado_curva == "reta" and velocidade_atual < self.velocidade_alvo * 0.8:
            acelerar = True
            frear_re = False
        
        # Controles de direção (mais suaves que o jogo_antigo)
        direita = diff_angulo < -2  # Zona morta reduzida
        esquerda = diff_angulo > 2
        turbo_pressed = False
        
        # Aplicar controles (usando sistema antigo que funciona)
        carro._step(acelerar, direita, esquerda, frear_re, turbo_pressed, superficie_mascara, dt)
        
        # Armazenar estado para debug
        self.estado_freio = frear_re
        self.estado_aceleracao = acelerar
        self.velocidade_atual = velocidade_atual
        self.distancia_atual = distancia
        self.diff_angulo_atual = diff_angulo
        
        # Debug
        if self.debug:
            status = "FREANDO" if frear_re else ("ACELERANDO" if acelerar else "NEUTRO")
            print(f"{self.nome}: CP {self.checkpoint_atual+1}/{len(self.checkpoints)}, Dist={distancia:.1f}, Vel={velocidade_atual:.1f}, VelAlvo={self.velocidade_alvo:.1f}, Curv={self.curvatura_atual:.3f}, Estado={self.estado_curva}, {status}")
    
    def desenhar_debug(self, superficie, camera=None, mostrar_todos_checkpoints=False):
        """Desenha debug visual da IA (otimizado)"""
        if not self.debug or not camera:
            return
        
        try:
            # Usar fontes pré-crIAdas para evitar recrIAção
            fonte_debug = pygame.font.SysFont("consolas", 16)
            fonte_debug_bold = pygame.font.SysFont("consolas", 16, bold=True)
            
            # Desenhar checkpoints
            for i, (cx, cy) in enumerate(self.checkpoints):
                screen_x, screen_y = camera.mundo_para_tela(cx, cy)
                
                # Mostrar apenas o próximo checkpoint por padrão, ou todos se solicitado
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
                
                # Número do checkpoint
                texto = fonte_debug_bold.render(str(i+1), True, (255, 255, 255))
                texto_rect = texto.get_rect(center=(int(screen_x), int(screen_y)))
                superficie.blit(texto, texto_rect)
            
            # Texto de debug - usar fonte já crIAda
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
