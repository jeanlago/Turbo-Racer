import pygame
import math

class DriftScoring:
    """
    Sistema de pontuação de drift simplificado e funcional
    """
    
    def __init__(self):
        # Parâmetros básicos
        self.SPEED_MIN = 8.0   # Velocidade mínima para drift (km/h) - otimizado para permitir drift normal
        self.ANGLE_MIN = 0.5   # Ângulo mínimo para drift (graus)
        
        # Sistema de combo estilo CarX Drift Racing
        self.MULTIPLIERS = [1.0, 2.0, 3.0, 4.0, 5.0]  # x1, x2, x3, x4, x5
        self.current_multiplier = 0  # Índice do multiplicador atual
        self.combo_fill = 0.0  # 0.0 a 1.0 para preencher o próximo nível
        self.multiplier_progress = 0.0  # Progresso dentro do multiplicador atual (0.0 a 1.0)
        
        # Pontuação
        self.points = 0.0
        self.best_points = 0.0
        self.best_combo = 0
        
        # Controle de tempo estilo CarX (mais generoso)
        self.drift_timer = 0.0  # Tempo atual de drift
        self.no_drift_timer = 0.0  # Tempo sem drift
        self.max_no_drift_time = 4.0  # 4 segundos de tolerância (mais generoso)
        
        # Estado
        self.is_drifting = False
        self.last_drift_activated = False
        
        # Taxa de pontos base (aumentada significativamente)
        self.base_point_rate = 10000.0  # Pontos por segundo no nível 1 - aumentado para 10000
        
        # Clipping zones (para compatibilidade)
        self.clipping_zones = []
        
    def update(self, dt, angle_deg, speed_kmh, car_x, car_y, drift_activated=False, drifting=False, collision_force=0.0, has_skidmarks=False, na_grama=False):
        """
        Atualiza o sistema de pontuação baseado em skidmarks
        
        Args:
            dt: Delta time
            angle_deg: Ângulo de drift em graus
            speed_kmh: Velocidade em km/h
            car_x, car_y: Posição do carro
            drift_activated: Se o drift foi ativado (espaço pressionado) - IGNORADO
            drifting: Se está atualmente derrapando (baseado nas marcas de pneu)
            collision_force: Força da colisão (0-1)
            has_skidmarks: Se há skidmarks sendo criados (base para pontuação)
            na_grama: Se está na grama (estilo GRIP - não conta pontuação)
        """
        
        # Se está na grama, não conta pontuação (estilo GRIP)
        if na_grama:
            # Resetar combo se estiver na grama
            if self.is_drifting:
                self._reset_combo()
            return
        
        # Detectar se está derrapando - baseado em skidmarks + velocidade + ângulo
        # Exige velocidade mínima para evitar ganhar pontos apenas fazendo "zerinho"
        self.is_drifting = has_skidmarks and speed_kmh >= self.SPEED_MIN and angle_deg >= self.ANGLE_MIN
        
        # Mecânicas de perda de combo estilo CarX
        # Colisão forte reseta tudo
        if collision_force > 0.8:
            self._reset_combo()
            return
        
        # Verificar se saiu da pista (velocidade muito baixa por muito tempo)
        if speed_kmh < 2.0 and self.no_drift_timer > 2.0:
            self._reset_combo()
            return
        
        # Verificar se parou o drift por muito tempo (mais generoso)
        if not has_skidmarks and self.no_drift_timer > 3.0:
            self._reset_combo()
            return
        
        if self.is_drifting:
            # Está derrapando
            self.drift_timer += dt
            self.no_drift_timer = 0.0
            
            # Calcular pontos baseados no ângulo e velocidade (mais generoso)
            angle_factor = min(abs(angle_deg) / 20.0, 3.0)  # Máximo 3x por ângulo (mais generoso)
            speed_factor = min(speed_kmh / 80.0, 2.0)  # Máximo 2x por velocidade (mais generoso)
            
            # Taxa de pontos base
            base_rate = self.base_point_rate * angle_factor * speed_factor
            
            # Aplicar multiplicador atual
            multiplier = self.MULTIPLIERS[self.current_multiplier]
            points_gained = base_rate * multiplier * dt
            self.points += points_gained
            
            # Atualizar estatísticas
            if self.current_multiplier > self.best_combo:
                self.best_combo = self.current_multiplier
            if self.points > self.best_points:
                self.best_points = self.points
            
            # Preencher combo
            self._fill_combo(dt, angle_factor, speed_factor)
            
        else:
            # Não está derrapando - sempre usar tolerância de tempo
            self.drift_timer = 0.0
            self.no_drift_timer += dt
            
            if self.no_drift_timer < self.max_no_drift_time:
                # Decaimento do progresso do multiplicador atual (muito mais lento)
                base_decay_rate = 0.1 * dt  # Base de 0.1 por segundo (muito mais lento)
                
                # Multiplicador de decaimento: quanto maior o multiplicador, mais rápido cai
                decay_multiplier = 1.0 + (self.current_multiplier * 0.15)  # +15% por nível (menos agressivo)
                decay_rate = base_decay_rate * decay_multiplier
                
                self.multiplier_progress = max(0.0, self.multiplier_progress - decay_rate)
                
                # Se o progresso chegar a zero, diminuir o multiplicador
                if self.multiplier_progress <= 0.0 and self.current_multiplier > 0:
                    self.current_multiplier -= 1
                    self.multiplier_progress = 0.7  # 70% do progresso para o nível anterior (mais generoso)
            else:
                # Passou da tolerância - resetar combo
                self._reset_combo()
        
        self.last_drift_activated = drift_activated
    
    def add_clipping_zone(self, x, y, radius, zone_type="any"):
        """Adiciona uma zona de clipping (para compatibilidade)"""
        self.clipping_zones.append({
            'x': x,
            'y': y,
            'radius': radius,
            'type': zone_type
        })
    
    def _fill_combo(self, dt, angle_factor, speed_factor):
        """Preenche o combo estilo CarX - progresso contínuo dentro do multiplicador"""
        # Taxa de preenchimento baseada na qualidade do drift
        base_fill_rate = (angle_factor + speed_factor) * 0.8 * dt
        
        # Penalidade progressiva: quanto maior o multiplicador, mais difícil de subir
        multiplier_penalty = 1.0 - (self.current_multiplier * 0.15)  # -15% por nível
        multiplier_penalty = max(0.3, multiplier_penalty)  # Mínimo de 30% da velocidade original
        
        fill_rate = base_fill_rate * multiplier_penalty
        self.multiplier_progress += fill_rate
        
        # Subir de nível quando o progresso chegar a 1.0
        if self.multiplier_progress >= 1.0 and self.current_multiplier < len(self.MULTIPLIERS) - 1:
            self.multiplier_progress = 0.0
            self.current_multiplier += 1
            if self.current_multiplier > self.best_combo:
                self.best_combo = self.current_multiplier
        
        # Limitar o progresso ao máximo de 1.0 quando estiver no nível máximo
        if self.current_multiplier >= len(self.MULTIPLIERS) - 1:
            self.multiplier_progress = min(self.multiplier_progress, 1.0)
    
    def _reset_combo(self):
        """Reseta o combo completamente"""
        self.current_multiplier = 0
        self.combo_fill = 0.0
        self.multiplier_progress = 0.0
        self.drift_timer = 0.0
        self.no_drift_timer = 0.0
    
    def draw_hud(self, surface, x, y, font, mostrar_score_texto=True):
        """Desenha o HUD do drift scoring estilo CarX"""
        # Pontuação
        if mostrar_score_texto:
            text_points = font.render(f"Score: {int(self.points)}", True, (255, 255, 255))
        else:
            text_points = font.render(f"{int(self.points):,}".replace(",", "."), True, (255, 255, 255))
        surface.blit(text_points, (x, y))
        y += text_points.get_height() + 8
        
        # Multiplicador estilo CarX (ex: 3.2x, 3.4x, 3.6x)
        if self.current_multiplier > 0:
            # Calcular multiplicador com progresso (ex: 3.0 + 0.2 = 3.2x)
            current_mult = self.MULTIPLIERS[self.current_multiplier] + (self.multiplier_progress * 0.2)
            mult_text = f"x{current_mult:.1f}"
            
            # Cores baseadas no nível do multiplicador
            if self.current_multiplier == len(self.MULTIPLIERS) - 1:  # Max combo (5x)
                mult_color = (255, 100, 0)  # Laranja vibrante
            elif self.current_multiplier >= 3:  # 4x+
                mult_color = (255, 200, 0)  # Amarelo dourado
            elif self.current_multiplier >= 2:  # 3x+
                mult_color = (0, 255, 100)  # Verde
            else:  # 2x
                mult_color = (0, 200, 255)  # Azul
        else:
            mult_text = "x1.0"
            mult_color = (200, 200, 200)  # Cinza
        
        # Fonte maior para o multiplicador
        font_mult = pygame.font.Font(None, 32)
        text_mult = font_mult.render(mult_text, True, mult_color)
        surface.blit(text_mult, (x, y))
        y += text_mult.get_height() + 8
        
        # Barra de progresso do multiplicador atual
        if self.current_multiplier > 0 and self.current_multiplier < len(self.MULTIPLIERS) - 1:
            bar_width = 180
            bar_height = 8
            fill_width = int(bar_width * self.multiplier_progress)
            
            # Cor da barra baseada no multiplicador
            if self.current_multiplier >= 3:
                bar_color = (255, 200, 0)  # Amarelo dourado
            elif self.current_multiplier >= 2:
                bar_color = (0, 255, 100)  # Verde
            else:
                bar_color = (0, 200, 255)  # Azul
            
            # Desenhar barra
            pygame.draw.rect(surface, (50, 50, 50), (x, y, bar_width, bar_height), 1)  # Borda
            pygame.draw.rect(surface, bar_color, (x, y, fill_width, bar_height))  # Preenchimento
