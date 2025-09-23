import os, math, pygame
from config import (
    LARGURA, ALTURA, DIR_SPRITES,
    MODO_DRIFT, DRIFT_MIN_VEL, DRIFT_EMISSAO_QPS,
    VEL_MAX, ACEL_BASE,
    TURBO_FORCA_IMPULSO, TURBO_FATOR, TURBO_DURACAO_S, TURBO_COOLDOWN_S
)
from core.pista import eh_pixel_da_pista, eh_pixel_transitavel
from core.particulas import EmissorFumaca

# Mapear nomes ("K_LCTRL", etc.) -> constantes pygame.K_*
KEY_NAME_TO_CONST = {name: getattr(pygame, name) for name in dir(pygame) if name.startswith("K_")}

class CarroFisica:
    """
    Nova física de carros baseada no Absolute Drift:
    - Sistema de tração traseira/frontal configurável
    - Drift realista com derrapagem da traseira
    - Física de pneus com grip lateral e longitudinal
    - Sistema de peso e inércIA realista
    """
    
    # Tipos de tração
    TRACAO_TRASEIRA = "rear"
    TRACAO_FRONTAL = "front"
    TRACAO_INTEGRAL = "awd"
    
    def __init__(self, x, y, prefixo_cor, controles, turbo_key=None, nome=None, tipo_tracao=None):
        self.x = float(x)
        self.y = float(y)
        self.angulo = 0.0  # graus (0 aponta pra -x do sprite)
        
        # Velocidades no mundo
        self.vx = 0.0
        self.vy = 0.0
        
        # Compatibilidade com HUD/lógicas externas
        self.velocidade = 0.0
        
        # Configurações do carro
        self.controles = controles
        self.turbo_key = KEY_NAME_TO_CONST.get(turbo_key) if isinstance(turbo_key, str) else turbo_key
        self.nome = nome or f"Carro {prefixo_cor}"
        self.tipo_tracao = tipo_tracao or self.TRACAO_TRASEIRA  # Padrão: tração traseira
        
        # Carregar sprite
        self._carregar_sprite(prefixo_cor)
        
        # Física avançada
        self.massa = 1200.0  # kg
        self.centro_massa_y = 0.0  # posição do centro de massa (negativo = mais à frente)
        self.distancia_eixos = 2.5  # metros
        self.largura_trilha = 1.5  # metros
        
        # Pneus (frente e traseira)
        self.pneus = {
            'frente': {
                'grip_lateral': 1.2,
                'grip_longitudinal': 1.0,
                'atrito_rolamento': 0.98,
                'angulo_max': 30.0,  # graus
                'largura': 0.2
            },
            'traseira': {
                'grip_lateral': 1.0,
                'grip_longitudinal': 1.0,
                'atrito_rolamento': 0.98,
                'angulo_max': 0.0,  # pneus traseiros não viram
                'largura': 0.2
            }
        }
        
        # Física do carro
        self._configurar_fisica()
        
        # Constantes de física mais realistas
        self.VEL_MAX_FRENTE = VEL_MAX if 'VEL_MAX' in globals() else 8.0  # Aumentado de 6.0 para 8.0
        self.VEL_MAX_RE = -3.0  # Ré controlada (aumentado de -2.5)
        self.ACELERACAO = ACEL_BASE if 'ACEL_BASE' in globals() else 0.08  # Reduzido para 0.08 (mais realista)
        self.FREIO = 0.18  # Aumentado de 0.14 para 0.18
        self.ATRITO_LONG_NORMAL = 0.985  # Reduzido de 0.992 para 0.985 (mais inércIA)
        self.GIRO_MAX = 3.5  # Reduzido de 4.0 para 3.5 (mais realista)
        
        # Estado do carro
        self.drift_hold = False
        self.drift_ativado = False  # Drift ativado por clique
        self.drifting = False
        self.drift_intensidade = 0.0
        self._was_drifting = False
        self._drift_time = 0.0
        self._drift_timer = 0.0  # Timer para duração do drift
        self._drift_duracao = 1.5  # Duração do drift em segundos
        
        # Sistema de estabilização do drift
        self._drift_direcao = 0  # -1 = esquerda, 0 = neutro, 1 = direita
        self._drift_estabilizacao = 0.0  # Fator de estabilização (0.0 a 1.0)
        self._drift_tempo_direcao = 0.0  # Tempo na direção atual
        self._bateu = False  # Flag para detectar colisão
        self._velocidade_antes_colisao = 0.0  # Velocidade antes de bater
        
        # Sistema de freio de mão
        self.freio_mao_ativo = False
        self.freio_mao_timer = 0.0
        self.freio_mao_duracao = 0.0  # Duração do freio de mão
        self.freio_mao_som_tocado = False
        self.marca_pneu_ativa = False
        self.marca_pneu_timer = 0.0
        self.marca_pneu_duracao = 1.0  # Duração da marca de pneu
        
        # Sistema de velocímetro e marchas
        self.velocidade_kmh = 0.0  # Velocidade em km/h
        self.marcha_atual = 0  # Marcha atual (0 = neutro, -1 = ré, 1-6 = marchas)
        self.rpm = 0.0  # RPM do motor
        
        # Efeitos
        self.emissor = EmissorFumaca()
        
        # Turbo
        self.turbo_carga = 100.0
        self.turbo_ativo = False
        self._turbo_timer = 0.0
        self._turbo_cd = 0.0
        self._turbo_mul = 1.0
        
        # Forças aplicadas
        self.forca_motor = 0.0
        self.forca_freio = 0.0
        self.angulo_volante = 0.0
        
        # Velocidades angulares
        self.velocidade_angular = 0.0  # rad/s
        self.aceleracao_angular = 0.0  # rad/s²
        
    def _carregar_sprite(self, prefixo_cor):
        """Carrega e redimensiona o sprite do carro"""
        caminho_sprite = os.path.join(DIR_SPRITES, f"{prefixo_cor}.png")
        sprite_original = pygame.image.load(caminho_sprite).convert_alpha()
        
        # Redimensionar sprite mantendo proporção
        largura_original, altura_original = sprite_original.get_size()
        proporcao = largura_original / altura_original
        
        # Definir área máxima
        area_maxima = 48 * 48
        
        # Calcular dimensões baseadas na área máxima
        if proporcao >= 1.0:
            largura_desejada = int((area_maxima * proporcao) ** 0.5)
            altura_desejada = int(largura_desejada / proporcao)
        else:
            altura_desejada = int((area_maxima / proporcao) ** 0.5)
            largura_desejada = int(altura_desejada * proporcao)
        
        # Limitar tamanho máximo
        largura_desejada = min(largura_desejada, 64)
        altura_desejada = min(altura_desejada, 64)
        
        self.sprite_base = pygame.transform.scale(sprite_original, (largura_desejada, altura_desejada))
        
    def _configurar_fisica(self):
        """Configura parâmetros físicos baseados no tipo de tração"""
        if self.tipo_tracao == self.TRACAO_TRASEIRA:
            # Carro com tração traseira - mais propenso ao drift
            self.potencIA_motor = 300.0  # HP
            self.torque_maximo = 400.0  # Nm
            self.centro_massa_y = -0.2  # Centro de massa mais à frente
            self.pneus['traseira']['grip_lateral'] = 0.8  # Menos grip traseiro
            self.pneus['frente']['grip_lateral'] = 1.2  # Mais grip frontal
            
        elif self.tipo_tracao == self.TRACAO_FRONTAL:
            # Carro com tração frontal - mais estável, sem drift
            self.potencIA_motor = 250.0
            self.torque_maximo = 350.0
            self.centro_massa_y = 0.2  # Centro de massa mais atrás
            self.pneus['frente']['grip_lateral'] = 1.3  # Muito mais grip frontal
            self.pneus['traseira']['grip_lateral'] = 1.2  # Mais grip traseiro
            
        else:  # TRACAO_INTEGRAL
            # Carro com tração integral - equilibrado
            self.potencIA_motor = 350.0
            self.torque_maximo = 450.0
            self.centro_massa_y = 0.0  # Centro de massa central
            self.pneus['frente']['grip_lateral'] = 1.0
            self.pneus['traseira']['grip_lateral'] = 1.0
    
    def _vetor_frente(self):
        """Retorna vetor unitário da direção frontal do carro"""
        rad = math.radians(self.angulo)
        return (-math.cos(rad), math.sin(rad))
    
    def _vetor_direita(self):
        """Retorna vetor unitário da direção lateral direita do carro"""
        fx, fy = self._vetor_frente()
        return (fy, -fx)
    
    def _decomp_vel(self):
        """Decompõe velocidade em componentes longitudinal e lateral"""
        fx, fy = self._vetor_frente()
        rx, ry = self._vetor_direita()
        v_long = self.vx * fx + self.vy * fy
        v_lat = self.vx * rx + self.vy * ry
        return v_long, v_lat
    
    def _recomp_vel(self, v_long, v_lat):
        """Recompõe velocidade a partir de componentes longitudinal e lateral"""
        fx, fy = self._vetor_frente()
        rx, ry = self._vetor_direita()
        self.vx = fx * v_long + rx * v_lat
        self.vy = fy * v_long + ry * v_lat
    
    def _calcular_forcas_pneus(self, v_long, v_lat, angulo_volante, dt):
        """Calcula forças dos pneus baseadas na física real"""
        # Velocidade total
        v_total = math.hypot(v_long, v_lat)
        
        # Ângulo de deslizamento (slip angle)
        if v_total > 0.1:
            slip_angle = math.atan2(v_lat, abs(v_long))
        else:
            slip_angle = 0.0
        
        # Forças dos pneus dIAnteiros
        forca_frente_lat = self._calcular_forca_lateral_pneu('frente', slip_angle + angulo_volante, v_total)
        forca_frente_long = self._calcular_forca_longitudinal_pneu('frente', v_long, v_total)
        
        # Forças dos pneus traseiros
        forca_traseira_lat = self._calcular_forca_lateral_pneu('traseira', slip_angle, v_total)
        forca_traseira_long = self._calcular_forca_longitudinal_pneu('traseira', v_long, v_total)
        
        # Aplicar tipo de tração
        if self.tipo_tracao == self.TRACAO_TRASEIRA:
            forca_frente_long = 0.0  # Só traseira acelera
        elif self.tipo_tracao == self.TRACAO_FRONTAL:
            forca_traseira_long = 0.0  # Só dIAnteira acelera
        
        return (forca_frente_lat, forca_frente_long, 
                forca_traseira_lat, forca_traseira_long)
    
    def _calcular_forca_lateral_pneu(self, posicao, slip_angle, velocidade):
        """Calcula força lateral do pneu baseada no ângulo de deslizamento"""
        pneu = self.pneus[posicao]
        
        # Limitar ângulo de deslizamento
        slip_angle = max(-math.radians(pneu['angulo_max']), 
                        min(math.radians(pneu['angulo_max']), slip_angle))
        
        # Curva de força lateral (simplificada)
        # Para ângulos pequenos, força é proporcional ao ângulo
        # Para ângulos grandes, força satura
        if abs(slip_angle) < 0.1:  # Região linear
            forca = pneu['grip_lateral'] * 1000.0 * slip_angle
        else:  # Região saturada
            forca = pneu['grip_lateral'] * 1000.0 * 0.1 * math.copysign(1, slip_angle)
        
        # Reduzir força em baixas velocidades
        fator_velocidade = min(1.0, velocidade / 50.0)
        return forca * fator_velocidade
    
    def _calcular_forca_longitudinal_pneu(self, posicao, v_long, velocidade):
        """Calcula força longitudinal do pneu"""
        pneu = self.pneus[posicao]
        
        # Força de aceleração/freio
        if abs(v_long) < 0.1:
            return 0.0
        
        # Aplicar grip longitudinal
        forca = pneu['grip_longitudinal'] * self.forca_motor * 0.1
        
        # Reduzir força em baixas velocidades
        fator_velocidade = min(1.0, velocidade / 30.0)
        return forca * fator_velocidade
    
    def _aplicar_drift(self, v_long, v_lat, dt):
        """Aplica sistema de drift baseado no Absolute Drift"""
        if not self.drift_hold or abs(v_long) < 1.0:
            return v_long, v_lat
        
        # Reduzir grip lateral durante drift
        fator_drift = 0.4  # Reduzir grip para 40%
        
        # Aplicar redução de grip principalmente na traseira
        if self.tipo_tracao == self.TRACAO_TRASEIRA:
            # Drift clássico - traseira derrapa
            v_lat *= (1.0 - fator_drift * 0.8)  # Reduzir grip lateral mais
            # Adicionar derrapagem lateral mais pronuncIAda
            if abs(v_long) > 1.5:
                v_lat += math.copysign(1.0, v_lat) * dt
        elif self.tipo_tracao == self.TRACAO_FRONTAL:
            # Drift de tração frontal - mais sutil
            v_lat *= (1.0 - fator_drift * 0.4)
        else:  # TRACAO_INTEGRAL
            # Drift equilibrado
            v_lat *= (1.0 - fator_drift * 0.6)
        
        return v_long, v_lat
    
    def _atualizar_estabilizacao_drift(self, direita, esquerda, dt):
        """Atualiza a estabilização do drift para evitar mudanças bruscas de direção"""
        # Determinar direção atual do input
        nova_direcao = 0
        if direita and not esquerda:
            nova_direcao = 1
        elif esquerda and not direita:
            nova_direcao = -1
        
        # Se mudou de direção
        if nova_direcao != self._drift_direcao:
            if self._drift_direcao != 0:  # Se já estava em uma direção
                # Aumentar estabilização para dificultar mudança
                self._drift_estabilizacao = min(1.0, self._drift_estabilizacao + 0.3)
                self._drift_tempo_direcao = 0.0
            else:
                # Primeira direção, estabilização baixa
                self._drift_estabilizacao = 0.1
                self._drift_tempo_direcao = 0.0
            
            self._drift_direcao = nova_direcao
        else:
            # Mesma direção, aumentar tempo e reduzir estabilização gradualmente
            self._drift_tempo_direcao += dt
            if self._drift_tempo_direcao > 0.2:  # Após 0.2s na mesma direção
                self._drift_estabilizacao = max(0.0, self._drift_estabilizacao - 0.1 * dt)
        
        # Se não está virando, resetar estabilização
        if nova_direcao == 0:
            self._drift_estabilizacao = max(0.0, self._drift_estabilizacao - 0.2 * dt)
    
    def _atualizar_fisica(self, acelerar, direita, esquerda, frear, turbo_pressed, superficie_mascara, dt):
        """Atualiza física do carro"""
        x_ant, y_ant = self.x, self.y
        
        # Decompor velocidade atual
        v_long, v_lat = self._decomp_vel()
        
        # ACELERAÇÃO/FREIO - Sistema simplificado mas funcional
        if self.freio_mao_ativo:
            # Com freio de mão ativo, frear gradualmente
            v_long *= 0.7  # Frear mais agressivamente
            v_lat *= 0.6   # Reduzir deslizamento lateral mais
            # Aplicar freio adicional
            if v_long > 0:
                v_long = max(0.0, v_long - self.FREIO * 2.0)  # Freio mais forte
            elif v_long < 0:
                v_long = min(0.0, v_long + self.FREIO * 2.0)  # Freio mais forte
        elif acelerar and not self._bateu:
            # Aceleração progressiva baseada na velocidade atual (mais realista)
            velocidade_atual = abs(v_long)
            
            # Fator de aceleração que diminui conforme a velocidade aumenta (mais realista)
            if velocidade_atual < 1.0:
                fator_acel = 1.0  # Aceleração máxima em baixas velocidades
            elif velocidade_atual < 2.5:
                fator_acel = 0.7  # Aceleração reduzida em velocidades médIAs
            elif velocidade_atual < 4.0:
                fator_acel = 0.5  # Aceleração ainda menor em altas velocidades
            elif velocidade_atual < 5.5:
                fator_acel = 0.3  # Aceleração muito reduzida em velocidades altas
            else:
                fator_acel = 0.15  # Aceleração mínima em velocidades muito altas
            
            # Aplicar aceleração baseada no tipo de tração (reduzida)
            if self.tipo_tracao == self.TRACAO_TRASEIRA:
                v_long += self.ACELERACAO * fator_acel * 0.7  # Tração traseira (reduzida)
            elif self.tipo_tracao == self.TRACAO_FRONTAL:
                v_long += self.ACELERACAO * fator_acel * 0.6  # Tração frontal (reduzida)
            else:  # AWD
                v_long += self.ACELERACAO * fator_acel * 0.8  # Tração integral (reduzida)
        elif frear:
            if v_long > 0.2:
                # Freando para frente - reduzir velocidade positiva
                v_long = max(0.0, v_long - self.FREIO)
            else:
                # Ré - usar lógica do arquivo original que funcionava bem
                v_long = max(self.VEL_MAX_RE, v_long - (self.FREIO * 0.5))
        else:
            v_long *= self.ATRITO_LONG_NORMAL
        
        # TURBO - só funciona para frente, não para ré (mais realista)
        self.turbo_ativo = bool(turbo_pressed and self.turbo_carga > 0.0 and v_long >= 0)
        if self.turbo_ativo:
            # Multiplicador de velocidade mais realista baseado na velocidade atual
            velocidade_atual = abs(v_long)
            if velocidade_atual < 2.0:
                multiplicador_turbo = 1.15  # 15% de aumento em baixas velocidades
            elif velocidade_atual < 4.0:
                multiplicador_turbo = 1.12  # 12% de aumento em velocidades médIAs
            elif velocidade_atual < 6.0:
                multiplicador_turbo = 1.08  # 8% de aumento em altas velocidades
            else:
                multiplicador_turbo = 1.05  # 5% de aumento em velocidades muito altas
            
            v_long *= multiplicador_turbo
            self.turbo_carga = max(0.0, self.turbo_carga - 25.0 * dt)  # Consumo mais lento
        else:
            self.turbo_carga = min(100.0, self.turbo_carga + 12.0 * dt)  # Recarga mais lenta
        
        # DIREÇÃO - Sistema mais realista com resposta baseada na velocidade
        speed_mag = math.hypot(self.vx, self.vy)
        
        # Fator de giro que aumenta com a velocidade (mais realista)
        if speed_mag < 1.0:
            fator_giro = speed_mag * 0.5  # Giro mais lento em baixas velocidades
        elif speed_mag < 3.0:
            fator_giro = speed_mag * 0.4  # Giro moderado em velocidades médIAs
        else:
            fator_giro = min(speed_mag * 0.35, self.GIRO_MAX)  # Giro limitado em altas velocidades
        
        # Inverter controles quando estiver dando ré
        if v_long < 0:  # Dando ré
            if direita:
                self.angulo += fator_giro  # Invertido: direita vira para esquerda
            if esquerda:
                self.angulo -= fator_giro  # Invertido: esquerda vira para direita
        else:  # Para frente ou parado
            if direita:
                self.angulo -= fator_giro  # Normal: direita vira para direita
            if esquerda:
                self.angulo += fator_giro  # Normal: esquerda vira para esquerda
        
        # DRIFT - Sistema realista com derrapagem natural e estabilização (SÓ PARA FRENTE)
        if self.drift_ativado and v_long > 1.0 and not self._bateu:  # Só para frente
            # Atualizar timer do drift
            self._drift_timer += dt
            
            # Verificar se o drift ainda está ativo
            if self._drift_timer < self._drift_duracao:
                # Atualizar direção do drift e estabilização
                self._atualizar_estabilizacao_drift(direita, esquerda, dt)
                
                # Reduzir aceleração durante o drift (mais realista)
                if acelerar:
                    # Fator de redução de aceleração durante drift
                    fator_reducao_drift = 0.4  # Reduzir aceleração em 60% durante drift
                    velocidade_atual = abs(v_long)
                    
                    # Aplicar redução de aceleração baseada na velocidade
                    if velocidade_atual < 2.0:
                        fator_drift = fator_reducao_drift * 0.8  # Menos redução em baixas velocidades
                    elif velocidade_atual < 4.0:
                        fator_drift = fator_reducao_drift * 0.6  # Redução médIA
                    else:
                        fator_drift = fator_reducao_drift * 0.4  # Mais redução em altas velocidades
                    
                    # Aplicar aceleração reduzida durante drift
                    if self.tipo_tracao == self.TRACAO_TRASEIRA:
                        v_long += self.ACELERACAO * fator_drift * 0.5  # Muito reduzida
                    elif self.tipo_tracao == self.TRACAO_FRONTAL:
                        v_long += self.ACELERACAO * fator_drift * 0.4  # Muito reduzida
                    else:  # AWD
                        v_long += self.ACELERACAO * fator_drift * 0.6  # Reduzida
                
                # DRIFT REALISTA - reduzir grip e adicionar derrapagem natural
                if self.tipo_tracao == self.TRACAO_TRASEIRA:
                    # Drift clássico - traseira derrapa MUITO mais
                    v_lat *= 0.10  # Redução MUITO significativa de grip (90%)
                    
                    # Aplicar derrapagem com estabilização
                    derrapagem_base = 1.5
                    derrapagem_extra = 0.8
                    fator_velocidade = min(1.0, v_long / 3.0)
                    
                    # Calcular derrapagem baseada na direção estabilizada
                    if self._drift_direcao == 1:  # Direita
                        v_lat += derrapagem_base * (1.0 - self._drift_estabilizacao * 0.3)
                        v_lat += derrapagem_extra * fator_velocidade * (1.0 - self._drift_estabilizacao * 0.2)
                    elif self._drift_direcao == -1:  # Esquerda
                        v_lat -= derrapagem_base * (1.0 - self._drift_estabilizacao * 0.3)
                        v_lat -= derrapagem_extra * fator_velocidade * (1.0 - self._drift_estabilizacao * 0.2)
                    else:  # Neutro
                        v_lat += 0.4 * fator_velocidade  # Derrapagem neutra menor
                        
                else:  # AWD (tração frontal não pode fazer drift)
                    # Drift equilibrado com estabilização
                    v_lat *= 0.20  # Redução de grip (80%)
                    
                    derrapagem_base = 1.0
                    if self._drift_direcao == 1:  # Direita
                        v_lat += derrapagem_base * (1.0 - self._drift_estabilizacao * 0.2)
                    elif self._drift_direcao == -1:  # Esquerda
                        v_lat -= derrapagem_base * (1.0 - self._drift_estabilizacao * 0.2)
            else:
                # Drift expirou - desativar e resetar estabilização
                self.drift_ativado = False
                self._drift_timer = 0.0
                self._drift_direcao = 0
                self._drift_estabilizacao = 0.0
                self._drift_tempo_direcao = 0.0
        else:
            # Grip normal - estabilidade baseada no tipo de tração
            if self.tipo_tracao == self.TRACAO_FRONTAL:
                # Tração frontal - muito estável, não desliza
                v_lat *= 0.95  # Muito atrito lateral
            else:
                # Tração traseira e integral - estabilidade baseada no contraesterço
                v_lat *= 0.90  # Atrito lateral normal
                
                # SISTEMA DE CONTRAESTERÇO - só estabiliza com volante contrário
                if abs(v_lat) > 0.5:  # Se estiver deslizando
                    # Verificar se está fazendo contraesterço
                    contraesterco = False
                    if v_lat > 0 and esquerda:  # Deslizando para direita, volante à esquerda
                        contraesterco = True
                    elif v_lat < 0 and direita:  # Deslizando para esquerda, volante à direita
                        contraesterco = True
                    
                    if contraesterco:
                        # Contraesterço - estabiliza gradualmente
                        v_lat *= 0.85
                    else:
                        # Sem contraesterço - continua deslizando
                        v_lat *= 0.98
                else:
                    # Não está deslizando - estabilidade normal
                    v_lat *= 0.90
        
        # Limitar velocidade máxima (mais realista)
        if self.turbo_ativo:
            # Velocidade máxima com turbo baseada na velocidade atual
            velocidade_atual = abs(v_long)
            if velocidade_atual < 3.0:
                v_max = VEL_MAX * 1.2  # 20% de aumento em baixas velocidades
            elif velocidade_atual < 5.0:
                v_max = VEL_MAX * 1.15  # 15% de aumento em velocidades médIAs
            else:
                v_max = VEL_MAX * 1.1  # 10% de aumento em altas velocidades
        else:
            v_max = VEL_MAX
        
        if abs(v_long) > v_max:
            v_long = math.copysign(v_max, v_long)
        
        # Normalizar ângulo
        if self.angulo > 180:
            self.angulo -= 360
        if self.angulo < -180:
            self.angulo += 360
        
        # Recompor velocidade
        self._recomp_vel(v_long, v_lat)
        
        # Atualizar posição
        self.x += self.vx
        self.y += self.vy
        
        # Colisão com pista (só se tiver superfície válida)
        if superficie_mascara is not None and not self._verificar_colisao(superficie_mascara):
            # Salvar velocidade antes da colisão
            if not self._bateu:
                self._velocidade_antes_colisao = abs(self.velocidade)
            
            self.x, self.y = x_ant, y_ant
            self.vx *= -0.3  # Reduzir mais a velocidade
            self.vy *= -0.3
            
            # Parar completamente o deslizamento
            v_long, v_lat = self._decomp_vel()
            v_lat *= 0.1  # Praticamente parar o deslizamento
            self._recomp_vel(v_long, v_lat)
            
            # Marcar que bateu e desativar drift
            self._bateu = True
            self.drift_ativado = False
            self._drift_timer = 0.0
        else:
            # Se não bateu, resetar flag de colisão após um tempo
            if self._bateu and abs(self.velocidade) < 0.5:
                self._bateu = False
        
        # Limites da tela
        self.x = max(0.0, min(LARGURA, self.x))
        self.y = max(0.0, min(ALTURA, self.y))
        
        # Atualizar velocidade para HUD
        self.velocidade = v_long
        
        # Atualizar velocímetro e marchas
        self._atualizar_velocimetro(v_long, dt)
        
        # Atualizar freio de mão e marca de pneu
        self._atualizar_freio_mao(dt)
        
        # Atualizar estado de drift
        self._atualizar_estado_drift(v_long, v_lat, dt)
    
    def _verificar_colisao(self, superficie_mascara):
        """Verifica colisão com a pista (otimizado)"""
        fx, fy = self._vetor_frente()
        rx, ry = self._vetor_direita()
        
        # Reduzir pontos de verificação para melhor performance
        pontos_verificacao = [
            (0, 0),  # Centro
            (12, 0), (-12, 0),  # Frente/trás
            (0, 6), (0, -6),  # Lados
        ]
        
        for ox, oy in pontos_verificacao:
            px = int(self.x + ox * fx + oy * rx)
            py = int(self.y + ox * fy + oy * ry)
            if not eh_pixel_transitavel(superficie_mascara, px, py):
                return False
        return True
    
    def _atualizar_estado_drift(self, v_long, v_lat, dt):
        """Atualiza estado visual e efeitos do drift (otimizado)"""
        v_total = math.hypot(v_long, v_lat)
        
        # Determinar se está fazendo drift (mais sensível à derrapagem)
        self.drifting = (self.drift_ativado and 
                        abs(v_lat) > 0.6 and  # Reduzido de 0.8 para 0.6 (mais sensível)
                        v_total > DRIFT_MIN_VEL)
        
        # Intensidade do drift baseada na velocidade lateral (mais dramática)
        if self.drifting:
            self.drift_intensidade = min(1.0, abs(v_lat) / 3.0)  # Reduzido de 4.0 para 3.0
            self._drift_time += dt
            
            # Emitir partículas durante drift (otimizado)
            if v_total > DRIFT_MIN_VEL:
                fx, fy = self._vetor_frente()
                taxa = DRIFT_EMISSAO_QPS * self.drift_intensidade
                self.emissor.spawn(self.x, self.y, fx, fy, taxa, dt)
        else:
            self.drift_intensidade *= 0.85  # Decaimento mais rápido
            self._drift_time = 0.0
        
        # Atualizar emissor apenas se necessário
        if self.drifting or len(self.emissor.ps) > 0:
            self.emissor.update(dt)
        
        self._was_drifting = self.drifting
    
    def atualizar(self, teclas, superficie_mascara, dt):
        """Atualiza o carro com base nas teclas pressionadas"""
        acelerar = teclas[self.controles[0]]
        direita = teclas[self.controles[1]]
        esquerda = teclas[self.controles[2]]
        frear = teclas[self.controles[3]]
        
        turbo_pressed = False
        if self.turbo_key is not None:
            turbo_pressed = bool(teclas[self.turbo_key])
        
        self._atualizar_fisica(acelerar, direita, esquerda, frear, turbo_pressed, superficie_mascara, dt)
    
    def desenhar(self, superficie, camera=None):
        """Desenha o carro na tela"""
        if camera is None:
            sprite_rot = pygame.transform.rotate(self.sprite_base, self.angulo)
            rect = sprite_rot.get_rect(center=(self.x, self.y))
            superficie.blit(sprite_rot, rect.topleft)
            self.emissor.draw(superficie, camera)
            return
        
        sx, sy = camera.mundo_para_tela(self.x, self.y)
        sprite_rot = pygame.transform.rotozoom(self.sprite_base, self.angulo, camera.zoom)
        rect = sprite_rot.get_rect(center=(sx, sy))
        superficie.blit(sprite_rot, rect.topleft)
        self.emissor.draw(superficie, camera)
    
    def usar_turbo(self):
        """Usa turbo (modo burst)"""
        if self._turbo_cd > 0.0:
            return
        
        v_long, v_lat = self._decomp_vel()
        v_long += TURBO_FORCA_IMPULSO * 0.016
        self._recomp_vel(v_long, v_lat)
        self._turbo_timer = TURBO_DURACAO_S
        self._turbo_mul = TURBO_FATOR
        self._turbo_cd = TURBO_COOLDOWN_S
    
    def ativar_drift(self, teclas=None):
        """Ativa o drift por clique ou freio de mão - só funciona se estiver virando"""
        # IA não pode usar drift nem freio de mão
        if "IA" in self.nome:
            return
        
        # Tração frontal não pode fazer drift
        if self.tipo_tracao == self.TRACAO_FRONTAL:
            return
        
        # Se estiver parado ou quase parado, ativar freio de mão
        if abs(self.velocidade) < 0.5:
            self.freio_mao_ativo = True
            self.freio_mao_timer = 0.0
            self.freio_mao_duracao = 0.0  # Indefinido até soltar
            self.freio_mao_som_tocado = False
            print(f"{self.nome}: Freio de mão ativado!")
            return
        
        # Verificar se está virando (esquerda ou direita)
        if teclas is not None:
            acelerar = teclas[self.controles[0]]  # Tecla acelerar
            direita = teclas[self.controles[1]]  # Tecla direita
            esquerda = teclas[self.controles[2]]  # Tecla esquerda
            esta_virando = direita or esquerda
            esta_acelerando = acelerar
        else:
            # Se não tiver teclas, assumir que não está virando nem acelerando
            esta_virando = False
            esta_acelerando = False
        
        # Se estiver em movimento para frente, não tiver batido, estiver virando E acelerando
        if self.velocidade > 1.0 and not self._bateu and esta_virando and esta_acelerando:
            # Verificar se não está muito rápido (evitar saída de frente)
            if self.velocidade < 6.0:  # Velocidade máxima para drift (ajustada para nova VEL_MAX)
                self.drift_ativado = True
                self._drift_timer = 0.0
                print(f"{self.nome}: Drift ativado!")
            else:
                print(f"{self.nome}: Muito rápido para drift!")
        elif self.velocidade > 1.0 and not self._bateu and esta_virando and not esta_acelerando:
            # Se estiver virando mas não acelerando, apenas frear (não ativar drift)
            print(f"{self.nome}: Apenas freando (não está acelerando)")
        elif self.velocidade > 1.0 and not self._bateu and not esta_virando:
            # Se estiver em linha reta, apenas frear (não ativar drift)
            print(f"{self.nome}: Apenas freando (não está virando)")
        else:
            # Se estiver parado ou quase parado, apenas frear
            print(f"{self.nome}: Apenas freando (velocidade baixa)")
    
    def desativar_drift(self):
        """Desativa o drift ou freio de mão"""
        if self.freio_mao_ativo:
            # Desativar freio de mão e ativar marca de pneu
            self.freio_mao_ativo = False
            self.marca_pneu_ativa = True
            self.marca_pneu_timer = 0.0
            print(f"{self.nome}: Freio de mão desativado! Marca de pneu ativada!")
        elif self.drift_ativado and not self.freio_mao_ativo:
            # Desativar drift normal apenas se não estiver com freio de mão
            self.drift_ativado = False
            self._drift_timer = 0.0
    
    def atualizar_com_ai(self, superficie_mascara, dt, acelerar, direita, esquerda, frear, turbo_pressed):
        """Atualiza o carro com controles da IA"""
        self._atualizar_fisica(acelerar, direita, esquerda, frear, turbo_pressed, superficie_mascara, dt)
    
    def _atualizar_velocimetro(self, v_long, dt):
        """Atualiza velocímetro e sistema de marchas"""
        # Converter velocidade para km/h (pixels/frame para km/h)
        # Usar o mesmo fator do HUD original: 20.0
        self.velocidade_kmh = abs(v_long) * 20.0  # Conversão de pixels/frame para km/h
        
        # Calcular RPM baseado na velocidade
        if v_long > 0:
            # Marcha para frente
            self.rpm = min(8000, 1000 + (self.velocidade_kmh * 80))
            # Determinar marcha baseada na velocidade
            if self.velocidade_kmh < 10:
                self.marcha_atual = 1
            elif self.velocidade_kmh < 25:
                self.marcha_atual = 2
            elif self.velocidade_kmh < 40:
                self.marcha_atual = 3
            elif self.velocidade_kmh < 60:
                self.marcha_atual = 4
            elif self.velocidade_kmh < 80:
                self.marcha_atual = 5
            else:
                self.marcha_atual = 6
        elif v_long < 0:
            # Ré
            self.rpm = min(4000, 800 + (abs(self.velocidade_kmh) * 40))
            self.marcha_atual = -1
        else:
            # Neutro
            self.rpm = 800
            self.marcha_atual = 0
    
    def _atualizar_freio_mao(self, dt):
        """Atualiza sistema de freio de mão e marca de pneu"""
        # Atualizar freio de mão
        if self.freio_mao_ativo:
            self.freio_mao_timer += dt
            
            # Tocar som do freio de mão (apenas uma vez)
            if not self.freio_mao_som_tocado:
                print(f"🔊 {self.nome}: Som do freio de mão!")
                self.freio_mao_som_tocado = True
        
        # Atualizar marca de pneu
        if self.marca_pneu_ativa:
            self.marca_pneu_timer += dt
            
            # Desativar marca de pneu após duração
            if self.marca_pneu_timer >= self.marca_pneu_duracao:
                self.marca_pneu_ativa = False
                self.marca_pneu_timer = 0.0
                print(f"🛞 {self.nome}: Marca de pneu desativada!")
