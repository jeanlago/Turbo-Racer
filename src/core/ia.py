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
    
    def __init__(self, checkpoints, nome="IA-Melhorada-V2", dificuldade="medio"):
        self.checkpoints = checkpoints if checkpoints else []
        self.nome = nome
        self.checkpoint_atual = 0
        self.chegou = False
        self.debug = False
        self.dificuldade = dificuldade
        
        # Debug: verificar se checkpoints foram recebidos
        if not self.checkpoints or len(self.checkpoints) == 0:
            print(f"AVISO: IA {self.nome} não recebeu checkpoints válidos!")
        else:
            print(f"IA {self.nome} inicializada com {len(self.checkpoints)} checkpoints")
        
        # Sistema de navegação melhorado
        self.pontos_navegacao = []
        self.ponto_navegacao_atual = 0
        self.atualizar_pontos_navegacao()
        
        # Controle de velocidade baseado na física e dificuldade
        self.velocidade_alvo = 3.0
        self.velocidade_maxima = 4.0
        self.velocidade_curva = 1.5
        
        # Parâmetros de dificuldade
        self._configurar_dificuldade()
        
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
    
    def _configurar_dificuldade(self):
        """Configura os parâmetros baseados na dificuldade"""
        if self.dificuldade == "facil":
            # IA FÁCIL - Medrosa, freia muito antes das curvas
            self.velocidade_maxima = 3.2
            self.velocidade_curva = 1.0
            self.distancia_freio_curva = 80  # Freia muito antes
            self.distancia_freio_checkpoint = 60  # Freia muito antes do checkpoint
            self.angulo_max_curva = 25  # Freia em curvas menos fechadas
            self.velocidade_max_curva = 1.5  # Velocidade máxima em curvas
            self.agressividade = 0.3  # Muito conservadora
            self.precisao_curva = 0.8  # Muito precisa
            self.tempo_reacao = 0.15  # Reação mais lenta
        elif self.dificuldade == "dificil":
            # IA DIFÍCIL - EXTREMAMENTE DIFÍCIL, QUASE IMPOSSÍVEL DE VENCER
            self.velocidade_maxima = 8.0  # Aumentado de 6.0 para 8.0 (EXTREMO)
            self.velocidade_curva = 4.5  # Aumentado de 3.0 para 4.5 (EXTREMO)
            self.distancia_freio_curva = 15  # Reduzido de 25 para 15 (freia MUITO menos)
            self.distancia_freio_checkpoint = 10  # Reduzido de 20 para 10 (freia MUITO menos)
            self.angulo_max_curva = 80  # Aumentado de 60 para 80 (freia MUITO menos)
            self.velocidade_max_curva = 6.0  # Aumentado de 4.0 para 6.0 (EXTREMO)
            self.agressividade = 1.0  # Máxima agressividade
            self.precisao_curva = 0.99  # Aumentado de 0.98 para 0.99 (quase perfeita)
            self.tempo_reacao = 0.01  # Reduzido de 0.03 para 0.01 (reação instantânea)
        else:  # medio
            # IA MÉDIA - Confiante, equilibrada, MAIS DIFÍCIL
            self.velocidade_maxima = 4.5  # Aumentado de 3.8 para 4.5
            self.velocidade_curva = 2.0  # Aumentado de 1.6 para 2.0
            self.distancia_freio_curva = 45  # Reduzido de 60 para 45 (freia menos)
            self.distancia_freio_checkpoint = 35  # Reduzido de 45 para 35 (freia menos)
            self.angulo_max_curva = 45  # Aumentado de 35 para 45 (freia menos)
            self.velocidade_max_curva = 2.8  # Aumentado de 2.2 para 2.8
            self.agressividade = 0.75  # Aumentado de 0.6 para 0.75 (mais agressiva)
            self.precisao_curva = 0.9  # Aumentado de 0.85 para 0.9 (mais precisa)
            self.tempo_reacao = 0.08  # Reduzido de 0.1 para 0.08 (mais rápida)
    
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
        
        # Normalizar (otimizado - calcular sqrt apenas uma vez)
        l1 = math.sqrt(l1_sq)
        l2 = math.sqrt(l2_sq)
        v1x, v1y = v1x/l1, v1y/l1
        v2x, v2y = v2x/l2, v2y/l2
        
        # Curvatura
        cross_product = v1x * v2y - v1y * v2x
        curvatura = abs(cross_product) / l1
        
        return curvatura
    
    def obter_pontos_lookahead(self, carro):
        """Obtém pontos à frente para antecipação (otimizado)"""
        if not self.pontos_navegacao:
            return []
        
        # Encontrar checkpoint mais próximo usando distância ao quadrado (já otimizado)
        distancia_min_sq = float('inf')
        indice_inicial = 0
        carro_x, carro_y = carro.x, carro.y  # Cache para evitar múltiplas leituras
        
        for i, (px, py) in enumerate(self.pontos_navegacao):
            dx = px - carro_x
            dy = py - carro_y
            dist_sq = dx*dx + dy*dy
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
        """Calcula velocidade alvo baseada na curvatura e dificuldade - otimizado"""
        pontos_lookahead = self.obter_pontos_lookahead(carro)
        
        if len(pontos_lookahead) < 3:
            return self.velocidade_maxima
        
        # Calcular curvatura média (otimizado - limitar iterações)
        num_calculos = min(len(pontos_lookahead) - 2, 3)  # Máximo 3 cálculos
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
        
        # Ajustar velocidade baseada na curvatura e dificuldade
        if curvatura_media > 0.15:  # Curva muito fechada
            return self.velocidade_curva
        elif curvatura_media > 0.08:  # Curva fechada
            return self.velocidade_curva * 1.2
        elif curvatura_media > 0.04:  # Curva média
            return self.velocidade_curva * 1.5
        elif curvatura_media > 0.02:  # Curva suave
            return self.velocidade_maxima * 0.8
        else:  # Reta
            return self.velocidade_maxima
        
        # IA DIFÍCIL: Velocidades EXTREMAMENTE agressivas
        if self.dificuldade == "dificil":
            if curvatura_media > 0.15:  # Curva muito fechada
                return self.velocidade_curva * 1.3  # MUITO mais rápido em curvas fechadas
            elif curvatura_media > 0.08:  # Curva fechada
                return self.velocidade_curva * 1.6  # MUITO mais rápido
            elif curvatura_media > 0.04:  # Curva média
                return self.velocidade_curva * 2.0  # EXTREMAMENTE mais rápido
            elif curvatura_media > 0.02:  # Curva suave
                return self.velocidade_maxima * 0.95  # Quase velocidade máxima
            else:  # Reta
                return self.velocidade_maxima * 1.1  # MUITO acima da velocidade máxima
    
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
        """Vetor unitário da direção lateral direita (com cache)"""
        fx, fy = self._vetor_frente(carro)
        return (fy, -fx)
    
    @classmethod
    def limpar_cache_trig(cls):
        """Limpa o cache de cálculos trigonométricos"""
        cls._trig_cache.clear()
    
    def controlar(self, carro, superficie_mascara, is_on_track, dt, superficie_pista_renderizada=None, corrida_iniciada=True):
        """Controla o carro com sistema inteligente baseado no jogo_antigo"""
        
        # Não controlar se a corrida ainda não iniciou
        if not corrida_iniciada:
            return
        
        if not self.checkpoints or len(self.checkpoints) == 0:
            # Se não há checkpoints, não fazer nada (mas não marcar como chegou)
            return
        
        # Calcular velocidade atual (otimizado - evitar sqrt quando possível)
        vel_sq = carro.vx*carro.vx + carro.vy*carro.vy
        velocidade_atual = math.sqrt(vel_sq) if vel_sq > 0.01 else 0.0
        
        # DETECÇÃO DE TRAVAMENTO (baseado no jogo_antigo) - otimizado
        # Verificar se o bot está na grama (pode estar lento mas não travado)
        na_grama = getattr(carro, 'na_grama', False)
        
        posicao_atual = (carro.x, carro.y)
        if self.ultima_posicao is not None:
            # Usar distância ao quadrado para evitar sqrt
            dx = posicao_atual[0] - self.ultima_posicao[0]
            dy = posicao_atual[1] - self.ultima_posicao[1]
            dist_movimento_sq = dx*dx + dy*dy
            
            # Se está na grama, ser mais tolerante com o movimento (grama reduz velocidade)
            # Na grama, o bot pode estar se movendo lentamente mas ainda progredindo
            if na_grama:
                # Na grama: considerar travado apenas se não se moveu quase nada
                limite_travamento_grama = 1.0  # 1.0^2 = 1.0 (muito mais tolerante)
                if dist_movimento_sq < limite_travamento_grama:
                    self.tempo_travado += dt
                else:
                    # Se está se movendo na grama, resetar travamento mais rapidamente
                    self.tempo_travado = max(0.0, self.tempo_travado - dt * 2.0)  # Reduzir travamento mais rápido
            else:
                # Na pista: usar limite normal
                if dist_movimento_sq < 9.0:  # 3.0^2 = 9.0
                    self.tempo_travado += dt
                else:
                    self.tempo_travado = 0.0
        self.ultima_posicao = posicao_atual
        
        # Se está na grama mas ainda tem velocidade, não considerar totalmente travado
        if na_grama and velocidade_atual > 0.5:
            # Reduzir o tempo de travamento se está se movendo (mesmo que lentamente)
            self.tempo_travado = max(0.0, self.tempo_travado - dt * 0.5)
        
        # DETECÇÃO DE COLISÃO
        # Se estamos usando tiles do GRIP, não usar detecção de colisão baseada em máscara
        # (o sistema GRIP não tem colisão hard, apenas redução de velocidade na grama)
        colidiu = False
        if superficie_mascara is not None and superficie_pista_renderizada is None:
            # Só detectar colisão se não estamos usando o sistema de tiles do GRIP
            colidiu = self.detectar_colisao(carro, superficie_mascara)
        
        if colidiu:
            if self.tempo_batido == 0.0:
                self.ultima_posicao_valida = (carro.x, carro.y)
            
            self.tempo_batido += dt
            
            # Recuperação simples: dar ré e tentar se reposicionar
            if self.tempo_batido > self.max_tempo_batido:
                # Dar ré por um tempo
                carro._step(False, False, False, True, False, superficie_mascara, dt, None, superficie_pista_renderizada)
                return
            else:
                # Parar e tentar se reposicionar
                carro._step(False, False, False, True, False, superficie_mascara, dt, None, superficie_pista_renderizada)
                return
        else:
            if self.tempo_batido > 0.0:
                self.tempo_batido = 0.0
        
        # NAVEGAÇÃO
        if not self.checkpoints or len(self.checkpoints) == 0:
            # Se não há checkpoints, não fazer nada
            return
        
        checkpoint_idx = self.checkpoint_atual % len(self.checkpoints)
        self.alvo_x = self.checkpoints[checkpoint_idx][0]
        self.alvo_y = self.checkpoints[checkpoint_idx][1]
        
        # Debug periódico (apenas a cada segundo para não spammar)
        if not hasattr(self, '_ultimo_debug_tempo'):
            self._ultimo_debug_tempo = 0.0
        if pygame.time.get_ticks() / 1000.0 - self._ultimo_debug_tempo > 2.0:  # A cada 2 segundos
            print(f"[IA {self.nome}] Checkpoint atual: {checkpoint_idx}/{len(self.checkpoints)}")
            print(f"[IA {self.nome}] Alvo: ({self.alvo_x:.1f}, {self.alvo_y:.1f})")
            print(f"[IA {self.nome}] Carro pos: ({carro.x:.1f}, {carro.y:.1f})")
            self._ultimo_debug_tempo = pygame.time.get_ticks() / 1000.0
        
        # DETECÇÃO DE CHECKPOINTS - usando retângulo (como no GRIP)
        # Verificar se o carro está dentro do retângulo do checkpoint
        checkpoint_idx = self.checkpoint_atual % len(self.checkpoints)
        if checkpoint_idx < len(self.checkpoints):
            cp = self.checkpoints[checkpoint_idx]
            # Suportar formato (x, y) ou (x, y, angulo)
            if len(cp) >= 3:
                cx, cy, angulo_salvo = cp[0], cp[1], cp[2]
                usar_angulo_salvo = True
            else:
                cx, cy = cp[0], cp[1]
                angulo_salvo = None
                usar_angulo_salvo = False
            
            CHECKPOINT_LARGURA = 300  # Largura dos tiles de pista
            CHECKPOINT_ESPESSURA = 1
            
            if usar_angulo_salvo:
                # Usar ângulo salvo (mesma lógica de _obter_retangulo_checkpoint)
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
                # Fallback: calcular baseado na direção
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
            
            # Expandir ligeiramente para melhor detecção
            checkpoint_rect = checkpoint_rect.inflate(10, 10)
            
            # Verificar se o carro está dentro do retângulo
            if checkpoint_rect.collidepoint(carro.x, carro.y):
                self.checkpoint_atual = (self.checkpoint_atual + 1) % len(self.checkpoints)
                self.tempo_travado = 0.0
                self.tentativas_recuperacao = 0
        
        # Atualizar alvo para o checkpoint atual (sempre, mesmo se não passou)
        checkpoint_idx = self.checkpoint_atual % len(self.checkpoints)
        self.alvo_x = self.checkpoints[checkpoint_idx][0]
        self.alvo_y = self.checkpoints[checkpoint_idx][1]
        
        # Calcular distâncIA e ângulo - otimizado
        dx = self.alvo_x - carro.x
        dy = self.alvo_y - carro.y
        distancia_sq = dx*dx + dy*dy
        distancia = math.sqrt(distancia_sq) if distancia_sq > 0.01 else 0.0
        
        # Calcular ângulo para o alvo (mesmo sistema do jogo_antigo)
        angulo_alvo = math.degrees(math.atan2(dy, -dx))  # -dx porque 0° aponta para -X
        diff_angulo = (angulo_alvo - carro.angulo + 180) % 360 - 180
        
        # LÓGICA DE RECUPERAÇÃO (baseada no jogo_antigo)
        # Só considerar travado se realmente parado (não apenas lento na grama)
        realmente_travado = self.tempo_travado > self.max_tempo_travado and velocidade_atual < 0.3
        
        # Debug: log quando está quase travado
        if self.tempo_travado > 2.0 and self.debug:
            print(f"IA {self.nome}: Quase travado - tempo: {self.tempo_travado:.1f}s, velocidade: {velocidade_atual:.2f}, na_grama: {na_grama}, checkpoint: {self.checkpoint_atual + 1}")
        
        if realmente_travado:
            print(f"IA {self.nome}: TRAVADO detectado - tempo: {self.tempo_travado:.1f}s, velocidade: {velocidade_atual:.2f}, checkpoint atual: {self.checkpoint_atual + 1}, tentativas: {self.tentativas_recuperacao}")
            if self.tentativas_recuperacao < self.max_tentativas_recuperacao:
                self.tentativas_recuperacao += 1
                
                # EstratégIA de recuperação: encontrar o checkpoint mais próximo ao invés de pular
                # Calcular distância para todos os checkpoints
                checkpoint_mais_proximo = self.checkpoint_atual
                distancia_minima = float('inf')
                
                for i, cp in enumerate(self.checkpoints):
                    cx, cy = cp[0], cp[1]
                    dist_sq = (carro.x - cx)**2 + (carro.y - cy)**2
                    if dist_sq < distancia_minima:
                        distancia_minima = dist_sq
                        checkpoint_mais_proximo = i
                
                # Se encontrou um checkpoint mais próximo, usar ele
                # Caso contrário, avançar para o próximo
                if checkpoint_mais_proximo != self.checkpoint_atual:
                    self.checkpoint_atual = checkpoint_mais_proximo
                    print(f"IA {self.nome}: Recuperação - mudou para checkpoint mais próximo: {checkpoint_mais_proximo + 1}")
                else:
                    # Avançar para o próximo checkpoint
                    self.checkpoint_atual = (self.checkpoint_atual + 1) % len(self.checkpoints)
                    print(f"IA {self.nome}: Recuperação - avançou para próximo checkpoint: {(self.checkpoint_atual % len(self.checkpoints)) + 1}")
                
                self.tempo_travado = 0.0
                
                # Atualizar alvo
                checkpoint_idx = self.checkpoint_atual % len(self.checkpoints)
                self.alvo_x = self.checkpoints[checkpoint_idx][0]
                self.alvo_y = self.checkpoints[checkpoint_idx][1]
                dx = self.alvo_x - carro.x
                dy = self.alvo_y - carro.y
            else:
                # Se esgotou tentativas, encontrar o checkpoint mais próximo ao invés de resetar para 0
                checkpoint_mais_proximo = 0
                distancia_minima = float('inf')
                
                for i, cp in enumerate(self.checkpoints):
                    cx, cy = cp[0], cp[1]
                    dist_sq = (carro.x - cx)**2 + (carro.y - cy)**2
                    if dist_sq < distancia_minima:
                        distancia_minima = dist_sq
                        checkpoint_mais_proximo = i
                
                # Usar o checkpoint mais próximo (não necessariamente o 0)
                self.checkpoint_atual = checkpoint_mais_proximo
                self.tentativas_recuperacao = 0
                self.tempo_travado = 0.0
                self.alvo_x = self.checkpoints[checkpoint_mais_proximo][0]
                self.alvo_y = self.checkpoints[checkpoint_mais_proximo][1]
                dx = self.alvo_x - carro.x
                dy = self.alvo_y - carro.y
                print(f"IA {self.nome}: Recuperação final - mudou para checkpoint mais próximo: {checkpoint_mais_proximo + 1} (não resetou para 0)")
        
        # SISTEMA INTELIGENTE DE CURVAS
        self.velocidade_alvo = self.calcular_velocidade_alvo(carro)
        self.atualizar_estado_curva(carro, dt)
        
        # CONTROLE DE VELOCIDADE baseado na dificuldade
        # Garantir que o bot sempre tente acelerar inicialmente
        acelerar = True
        frear_re = False
        
        # Remover verificação duplicada - já foi feita no início da função
        
        # 1. Frear se estiver muito próximo do checkpoint (baseado na dificuldade)
        if distancia < self.distancia_freio_checkpoint and velocidade_atual > 1.2:
            frear_re = True
            acelerar = False
        
        # 2. Frear se precisar fazer uma curva (baseado na dificuldade)
        if abs(diff_angulo) > self.angulo_max_curva and velocidade_atual > self.velocidade_max_curva:
            frear_re = True
            acelerar = False
        
        # 3. Frear se estiver indo muito rápido em relação à distâncIA (baseado na dificuldade)
        if distancia < self.distancia_freio_curva and velocidade_atual > self.velocidade_maxima * 0.8:
            frear_re = True
            acelerar = False
        
        # 4. Frear se estiver indo na direção errada (baseado na dificuldade)
        if abs(diff_angulo) > 80 and velocidade_atual > 0.8:
            frear_re = True
            acelerar = False
        
        # 5. Acelerar apenas se estiver alinhado e não muito próximo (baseado na dificuldade)
        if abs(diff_angulo) < 12 and distancia > self.distancia_freio_checkpoint and velocidade_atual < self.velocidade_maxima * 0.9:
            acelerar = True
            frear_re = False
        
        # 5b. IA DIFÍCIL: Acelerar EXTREMAMENTE agressivamente
        if self.dificuldade == "dificil":
            # IA difícil acelera com ângulos muito maiores
            if abs(diff_angulo) < 40 and distancia > self.distancia_freio_checkpoint and velocidade_atual < self.velocidade_maxima * 0.98:
                acelerar = True
                frear_re = False
            # IA difícil acelera mesmo em curvas moderadas
            if abs(diff_angulo) < 50 and self.curvatura_atual < 0.08 and velocidade_atual < self.velocidade_maxima * 0.9:
                acelerar = True
                frear_re = False
            # IA difícil acelera mesmo em curvas fechadas se estiver alinhada
            if abs(diff_angulo) < 25 and self.curvatura_atual < 0.12 and velocidade_atual < self.velocidade_maxima * 0.85:
                acelerar = True
                frear_re = False
            # IA difícil NUNCA para de acelerar em retas
            if abs(diff_angulo) < 15 and self.curvatura_atual < 0.03:
                acelerar = True
                frear_re = False
        
        # 6. Controle baseado no estado da curva (baseado na dificuldade)
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
        
        # Drift baseado na dificuldade
        turbo_pressed = False
        if self.dificuldade == "dificil":
            # IA difícil usa turbo CONSTANTEMENTE
            if abs(diff_angulo) > 15 and velocidade_atual > 1.0:  # MUITO mais agressiva
                turbo_pressed = True
            # IA difícil usa turbo para acelerar em retas também
            elif abs(diff_angulo) < 15 and velocidade_atual > 2.0 and velocidade_atual < self.velocidade_maxima * 0.9:
                turbo_pressed = True
            # IA difícil usa turbo em curvas suaves
            elif abs(diff_angulo) < 30 and self.curvatura_atual < 0.06 and velocidade_atual > 1.5:
                turbo_pressed = True
            # IA difícil usa turbo para manter velocidade em curvas
            elif abs(diff_angulo) < 45 and velocidade_atual > 2.5 and velocidade_atual < self.velocidade_maxima * 0.8:
                turbo_pressed = True
        elif self.dificuldade == "medio":
            # IA média faz drift mais frequentemente
            if abs(diff_angulo) > 30 and velocidade_atual > 2.0:  # Mais agressiva
                turbo_pressed = True
            # IA média usa turbo em retas ocasionalmente
            elif abs(diff_angulo) < 15 and velocidade_atual > 2.5 and velocidade_atual < self.velocidade_maxima * 0.8:
                turbo_pressed = True
        # IA fácil não faz drift (muito conservadora)
        
        # IA MÉDIA: Acelerar mais agressivamente
        if self.dificuldade == "medio":
            # IA média acelera mais frequentemente
            if abs(diff_angulo) < 25 and distancia > self.distancia_freio_checkpoint and velocidade_atual < self.velocidade_maxima * 0.85:
                acelerar = True
                frear_re = False
            # IA média acelera em curvas suaves
            if abs(diff_angulo) < 35 and self.curvatura_atual < 0.06 and velocidade_atual < self.velocidade_maxima * 0.75:
                acelerar = True
                frear_re = False
        
        # IA DIFÍCIL: Forçar aceleração constante (quase impossível de vencer)
        if self.dificuldade == "dificil":
            # IA difícil acelera SEMPRE, exceto em situações extremas
            if not (abs(diff_angulo) > 70 and velocidade_atual > 5.0):  # Só não acelera se estiver muito desalinhada E muito rápida
                acelerar = True
                frear_re = False
        
        # Debug: verificar controles antes de aplicar (apenas a cada 2 segundos)
        if pygame.time.get_ticks() / 1000.0 - self._ultimo_debug_tempo > 2.0:
            print(f"[IA {self.nome}] Controles: acelerar={acelerar}, frear={frear_re}, direita={direita}, esquerda={esquerda}, turbo={turbo_pressed}")
            print(f"[IA {self.nome}] Velocidade: {velocidade_atual:.2f}, diff_angulo: {diff_angulo:.1f}°, distancia: {distancia:.1f}")
        
        # Aplicar controles (usando sistema antigo que funciona)
        carro._step(acelerar, direita, esquerda, frear_re, turbo_pressed, superficie_mascara, dt, None, superficie_pista_renderizada)
        
        # Armazenar estado para debug
        self.estado_freio = frear_re
        self.estado_aceleracao = acelerar
        self.velocidade_atual = velocidade_atual
        self.distancia_atual = distancia
        self.diff_angulo_atual = diff_angulo
        
        # Debug (removido print para melhor performance)
    
    def desenhar_debug(self, superficie, camera=None, mostrar_todos_checkpoints=False):
        """Desenha debug visual da IA (otimizado)"""
        if not self.debug or not camera:
            return
        
        try:
            # Usar fontes pré-crIAdas para evitar recrIAção
            fonte_debug = pygame.font.SysFont("consolas", 16)
            fonte_debug_bold = pygame.font.SysFont("consolas", 16, bold=True)
            
            # Desenhar checkpoints
            for i, cp in enumerate(self.checkpoints):
                cx, cy = cp[0], cp[1] if len(cp) >= 2 else (cp[0], cp[1])
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
