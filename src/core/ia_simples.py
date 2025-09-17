import math
import pygame

class IASimples:
    """IA simples que segue uma sequência de checkpoints"""
    
    def __init__(self, checkpoints, nome="IA"):
        self.checkpoints = checkpoints
        self.nome = nome
        self.checkpoint_atual = 0
        self.chegou = False
        self.debug = False
        self.tempo_travado = 0.0  # Tempo que está tentando alcançar o mesmo checkpoint
        self.max_tempo_travado = 5.0  # Máximo de 5 segundos no mesmo checkpoint
        self.ultima_posicao = None  # Para detectar se está travado
        self.tentativas_recuperacao = 0
        self.max_tentativas_recuperacao = 3
        
        if self.checkpoints:
            self.alvo_x = self.checkpoints[0][0]
            self.alvo_y = self.checkpoints[0][1]
        else:
            self.alvo_x = 640
            self.alvo_y = 360
        
    def controlar(self, carro, superficie_mascara, is_on_track, dt):
        """Controla o carro para seguir a sequência de checkpoints em loop"""
        
        # Se não há checkpoints, parar
        if not self.checkpoints:
            self.chegou = True
            return
        
        # Atualizar alvo atual (usar módulo para fazer loop)
        checkpoint_idx = self.checkpoint_atual % len(self.checkpoints)
        self.alvo_x = self.checkpoints[checkpoint_idx][0]
        self.alvo_y = self.checkpoints[checkpoint_idx][1]
        
        # Calcular distância até o checkpoint atual
        dx = self.alvo_x - carro.x
        dy = self.alvo_y - carro.y
        distancia = math.sqrt(dx*dx + dy*dy)
        
        # Detectar se está travado (mesma posição por muito tempo)
        posicao_atual = (carro.x, carro.y)
        if self.ultima_posicao is not None:
            dist_movimento = math.sqrt((posicao_atual[0] - self.ultima_posicao[0])**2 + 
                                     (posicao_atual[1] - self.ultima_posicao[1])**2)
            if dist_movimento < 5.0:  # Movimento mínimo
                self.tempo_travado += dt
            else:
                self.tempo_travado = 0.0
        self.ultima_posicao = posicao_atual
        
        # Se chegou perto do checkpoint atual (raio de 40 pixels), ir para o próximo
        if distancia < 40:
            self.checkpoint_atual += 1
            self.tempo_travado = 0.0  # Reset tempo travado
            self.tentativas_recuperacao = 0  # Reset tentativas
            print(f"{self.nome} chegou ao checkpoint {self.checkpoint_atual}! (Loop: {self.checkpoint_atual // len(self.checkpoints) + 1})")
            
            # Atualizar para o próximo checkpoint (loop automático)
            checkpoint_idx = self.checkpoint_atual % len(self.checkpoints)
            self.alvo_x = self.checkpoints[checkpoint_idx][0]
            self.alvo_y = self.checkpoints[checkpoint_idx][1]
            dx = self.alvo_x - carro.x
            dy = self.alvo_y - carro.y
        
        # LÓGICA DE RECUPERAÇÃO - se está travado há muito tempo
        elif self.tempo_travado > self.max_tempo_travado:
            if self.tentativas_recuperacao < self.max_tentativas_recuperacao:
                self.tentativas_recuperacao += 1
                print(f"{self.nome} travado! Tentativa de recuperação {self.tentativas_recuperacao}/{self.max_tentativas_recuperacao}")
                
                # Estratégia de recuperação: pular para o próximo checkpoint
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
        
        # Calcular ângulo para o alvo (considerando que 0° do carro aponta para -X)
        angulo_alvo = math.degrees(math.atan2(dy, -dx))  # -dx porque 0° aponta para -X
        diff_angulo = (angulo_alvo - carro.angulo + 180) % 360 - 180
        
        # Calcular velocidade atual
        velocidade_atual = math.sqrt(carro.vx*carro.vx + carro.vy*carro.vy)
        
        # LÓGICA DE FREIO INTELIGENTE
        acelerar = True
        frear_re = False
        
        # 1. Frear se estiver muito próximo do checkpoint (para não passar direto)
        if distancia < 60 and velocidade_atual > 1.5:
            frear_re = True
            acelerar = False
        
        # 2. Frear se precisar fazer uma curva muito fechada
        if abs(diff_angulo) > 45 and velocidade_atual > 2.0:
            frear_re = True
            acelerar = False
        
        # 3. Frear se estiver indo muito rápido em relação à distância
        if distancia < 80 and velocidade_atual > 3.0:
            frear_re = True
            acelerar = False
        
        # 4. Frear se estiver indo na direção errada (diferença de ângulo muito grande)
        if abs(diff_angulo) > 90 and velocidade_atual > 1.0:
            frear_re = True
            acelerar = False
        
        # 5. Acelerar apenas se estiver alinhado e não muito próximo
        if abs(diff_angulo) < 15 and distancia > 50 and velocidade_atual < 4.0:
            acelerar = True
            frear_re = False
        
        # Controles de direção (mais suaves)
        direita = diff_angulo < -3  # Virar para a direita se o alvo está à esquerda
        esquerda = diff_angulo > 3  # Virar para a esquerda se o alvo está à direita
        turbo_pressed = False
        
        # Aplicar controles
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
            print(f"{self.nome}: CP {self.checkpoint_atual+1}/{len(self.checkpoints)}, Dist={distancia:.1f}, Vel={velocidade_atual:.1f}, Diff={diff_angulo:.1f}, {status}")
    
    def desenhar_debug(self, superficie, camera=None):
        """Desenha debug visual da IA"""
        if not self.debug or not camera:
            return
        
        try:
            # Desenhar todos os checkpoints
            for i, (cx, cy) in enumerate(self.checkpoints):
                screen_x, screen_y = camera.mundo_para_tela(cx, cy)
                
                # Cor diferente para o checkpoint atual
                if i == self.checkpoint_atual:
                    cor = (255, 0, 0)  # Vermelho para o atual
                    raio = 15
                elif i < self.checkpoint_atual:
                    cor = (0, 255, 0)  # Verde para os já passados
                    raio = 8
                else:
                    cor = (128, 128, 128)  # Cinza para os futuros
                    raio = 8
                
                pygame.draw.circle(superficie, cor, (int(screen_x), int(screen_y)), raio)
                
                # Número do checkpoint
                fonte = pygame.font.SysFont("consolas", 12)
                texto = fonte.render(str(i+1), True, (255, 255, 255))
                texto_rect = texto.get_rect(center=(int(screen_x), int(screen_y)))
                superficie.blit(texto, texto_rect)
            
            # Texto de debug
            fonte = pygame.font.SysFont("consolas", 16)
            if not self.chegou and self.checkpoints:
                # Calcular loop atual
                loop_atual = self.checkpoint_atual // len(self.checkpoints) + 1
                checkpoint_display = (self.checkpoint_atual % len(self.checkpoints)) + 1
                
                texto = fonte.render(f"Checkpoint {checkpoint_display}/{len(self.checkpoints)} (Loop {loop_atual})", True, (255, 255, 255))
                superficie.blit(texto, (10, 10))
                
                checkpoint_idx = self.checkpoint_atual % len(self.checkpoints)
                alvo_x, alvo_y = self.checkpoints[checkpoint_idx]
                texto_alvo = fonte.render(f"Alvo: ({alvo_x:.0f}, {alvo_y:.0f})", True, (255, 255, 255))
                superficie.blit(texto_alvo, (10, 30))
                
                # Usar valores armazenados
                if hasattr(self, 'distancia_atual'):
                    texto_dist = fonte.render(f"Distância: {self.distancia_atual:.1f}", True, (255, 255, 255))
                    superficie.blit(texto_dist, (10, 50))
                
                if hasattr(self, 'velocidade_atual'):
                    texto_vel = fonte.render(f"Velocidade: {self.velocidade_atual:.1f}", True, (255, 255, 255))
                    superficie.blit(texto_vel, (10, 70))
                
                # Indicador de freio
                if hasattr(self, 'estado_freio'):
                    if self.estado_freio:
                        texto_freio = fonte.render("FREANDO!", True, (255, 0, 0))
                        superficie.blit(texto_freio, (10, 90))
                    elif hasattr(self, 'estado_aceleracao') and self.estado_aceleracao:
                        texto_acel = fonte.render("ACELERANDO", True, (0, 255, 0))
                        superficie.blit(texto_acel, (10, 90))
                    else:
                        texto_neutro = fonte.render("NEUTRO", True, (255, 255, 0))
                        superficie.blit(texto_neutro, (10, 90))
                
                # Indicador de recuperação
                if hasattr(self, 'tempo_travado') and self.tempo_travado > 0:
                    texto_travado = fonte.render(f"TRAVADO: {self.tempo_travado:.1f}s", True, (255, 165, 0))
                    superficie.blit(texto_travado, (10, 110))
                
                if hasattr(self, 'tentativas_recuperacao') and self.tentativas_recuperacao > 0:
                    texto_recuperacao = fonte.render(f"RECUPERAÇÃO: {self.tentativas_recuperacao}/{self.max_tentativas_recuperacao}", True, (255, 100, 100))
                    superficie.blit(texto_recuperacao, (10, 130))
            else:
                texto_chegou = fonte.render("SEQUÊNCIA COMPLETA!", True, (0, 255, 0))
                superficie.blit(texto_chegou, (10, 10))
                
        except Exception as e:
            print(f"Erro ao desenhar debug da IA: {e}")
