import pygame
import math

class DriftScoring:
    """
    Sistema de pontuação de drift simplificado e funcional
    """
    
    def __init__(self):
        # Parâmetros básicos
        self.SPEED_MIN = 5.0   # Velocidade mínima para drift (km/h) - reduzido
        self.ANGLE_MIN = 3.0   # Ângulo mínimo para drift (graus) - reduzido
        
        # Sistema de combo
        self.MULTIPLIERS = [1.0, 1.5, 2.0, 3.0, 5.0]  # x1, x1.5, x2, x3, x5
        self.current_multiplier = 0  # Índice do multiplicador atual
        self.combo_fill = 0.0  # 0.0 a 1.0 para preencher o próximo nível
        
        # Pontuação
        self.points = 0.0
        self.best_points = 0.0
        self.best_combo = 0
        
        # Controle de tempo
        self.drift_timer = 0.0  # Tempo atual de drift
        self.no_drift_timer = 0.0  # Tempo sem drift
        self.max_no_drift_time = 5.0  # 5 segundos de tolerância (aumentado)
        
        # Estado
        self.is_drifting = False
        self.last_drift_activated = False
        
        # Taxa de pontos base
        self.base_point_rate = 50.0  # Pontos por segundo no nível 1
        
        # Clipping zones (para compatibilidade)
        self.clipping_zones = []
        
    def update(self, dt, angle_deg, speed_kmh, car_x, car_y, drift_activated=False, drifting=False, collision_force=0.0):
        """
        Atualiza o sistema de pontuação
        
        Args:
            dt: Delta time
            angle_deg: Ângulo de drift em graus
            speed_kmh: Velocidade em km/h
            car_x, car_y: Posição do carro
            drift_activated: Se o drift foi ativado (espaço pressionado)
            drifting: Se está atualmente derrapando (ignorado)
            collision_force: Força da colisão (0-1)
        """
        
        # Detectar se está derrapando - baseado APENAS no drift_ativado + velocidade
        self.is_drifting = drift_activated and speed_kmh >= self.SPEED_MIN
        
        # Colisão forte reseta tudo
        if collision_force > 0.8:
            self._reset_combo()
            return
        
        if self.is_drifting:
            # Está derrapando
            self.drift_timer += dt
            self.no_drift_timer = 0.0
            
            # Calcular pontos baseados no ângulo e velocidade
            angle_factor = min(abs(angle_deg) / 30.0, 2.0)  # Máximo 2x por ângulo
            speed_factor = min(speed_kmh / 100.0, 1.5)  # Máximo 1.5x por velocidade
            
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
                # Decaimento mais rápido conforme multiplicador maior
                base_decay_rate = 0.4 * dt  # Base de 0.4 por segundo
                
                # Multiplicador de decaimento: quanto maior o multiplicador, mais rápido cai
                decay_multiplier = 1.0 + (self.current_multiplier * 0.3)  # +30% por nível
                decay_rate = base_decay_rate * decay_multiplier
                
                self.combo_fill = max(0.0, self.combo_fill - decay_rate)
                
                # Se o fill chegar a zero, diminuir o multiplicador gradualmente
                if self.combo_fill <= 0.0 and self.current_multiplier > 0:
                    self.current_multiplier -= 1
                    self.combo_fill = 0.7  # 70% do fill para o nível anterior (menos generoso)
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
        """Preenche a barra de combo"""
        # Taxa de preenchimento diminui conforme o multiplicador aumenta
        base_fill_rate = (angle_factor + speed_factor) * 0.6 * dt  # Reduzido de 0.8 para 0.6
        
        # Penalidade progressiva: quanto maior o multiplicador, mais lento para subir
        multiplier_penalty = 1.0 - (self.current_multiplier * 0.15)  # -15% por nível
        multiplier_penalty = max(0.3, multiplier_penalty)  # Mínimo de 30% da velocidade original
        
        fill_rate = base_fill_rate * multiplier_penalty
        self.combo_fill += fill_rate
        
        # Subir de nível se necessário
        while self.combo_fill >= 1.0 and self.current_multiplier < len(self.MULTIPLIERS) - 1:
            self.combo_fill -= 1.0
            self.current_multiplier += 1
            if self.current_multiplier > self.best_combo:
                self.best_combo = self.current_multiplier
        
        # Limitar o fill ao máximo de 1.0 quando estiver no nível máximo
        if self.current_multiplier >= len(self.MULTIPLIERS) - 1:
            self.combo_fill = min(self.combo_fill, 1.0)
    
    def _reset_combo(self):
        """Reseta o combo completamente"""
        self.current_multiplier = 0
        self.combo_fill = 0.0
        self.drift_timer = 0.0
        self.no_drift_timer = 0.0
    
    def draw_hud(self, surface, x, y, font):
        """Desenha o HUD do drift scoring"""
        # Pontuação
        text_points = font.render(f"Score: {int(self.points)}", True, (255, 255, 255))
        surface.blit(text_points, (x, y))
        y += text_points.get_height() + 5
        
        # Multiplicador atual
        mult_color = (255, 255, 0) if self.current_multiplier > 0 else (200, 200, 200)
        text_mult = font.render(f"Combo: x{self.MULTIPLIERS[self.current_multiplier]:.1f}", True, mult_color)
        surface.blit(text_mult, (x, y))
        y += text_mult.get_height() + 5
        
        # Barra de combo
        bar_width = 200
        bar_height = 15
        fill_width = int(bar_width * self.combo_fill)
        
        # Cor da barra
        if self.current_multiplier == len(self.MULTIPLIERS) - 1:  # Max combo
            bar_color = (255, 165, 0)  # Laranja
        elif self.current_multiplier > 0:
            bar_color = (0, 200, 255)  # Azul claro
        else:
            bar_color = (100, 100, 100)  # Cinza
        
        # Desenhar barra
        pygame.draw.rect(surface, (50, 50, 50), (x, y, bar_width, bar_height), 2)  # Borda
        pygame.draw.rect(surface, bar_color, (x, y, fill_width, bar_height))  # Preenchimento
        y += bar_height + 5
        
        # Tempo de drift
        text_drift_time = font.render(f"Drift Time: {self.drift_timer:.1f}s", True, (255, 255, 255))
        surface.blit(text_drift_time, (x, y))
        y += text_drift_time.get_height() + 5
        
        # Melhor combo e pontos
        text_best_combo = font.render(f"Best Combo: x{self.MULTIPLIERS[self.best_combo]:.1f}", True, (255, 255, 255))
        surface.blit(text_best_combo, (x, y))
        y += text_best_combo.get_height() + 5
        
        text_best_points = font.render(f"Best Score: {int(self.best_points)}", True, (255, 255, 255))
        surface.blit(text_best_points, (x, y))
        
        # Mostrar tolerância se aplicável
        if self.last_drift_activated and not self.is_drifting and self.no_drift_timer < self.max_no_drift_time:
            remaining_time = self.max_no_drift_time - self.no_drift_timer
            text_tolerance = font.render(f"Reset em: {remaining_time:.1f}s", True, (255, 200, 0))
            surface.blit(text_tolerance, (x, y + 20))
