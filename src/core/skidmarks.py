import pygame

class Skidmark:
    """Representa um segmento de linha de skidmark"""
    
    def __init__(self, x1, y1, x2, y2, duracao=4.0, alpha=255):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.duracao = duracao
        self.tempo_vida = 0.0
        self.alpha = alpha
        self.ativo = True
    
    def atualizar(self, dt):
        """Atualiza o skidmark"""
        self.tempo_vida += dt
        if self.tempo_vida >= self.duracao:
            self.ativo = False
        else:
            # Fade out gradual
            progresso = self.tempo_vida / self.duracao
            self.alpha = int(255 * (1.0 - progresso))
    
    def desenhar(self, tela, camera):
        """Desenha o skidmark"""
        if not self.ativo:
            return
        
        # Converter coordenadas do mundo para tela
        if camera:
            x1, y1 = camera.mundo_para_tela(self.x1, self.y1)
            x2, y2 = camera.mundo_para_tela(self.x2, self.y2)
        else:
            x1, y1 = self.x1, self.y1
            x2, y2 = self.x2, self.y2
        
        # Desenhar linha
        cor = (100, 100, 100, self.alpha)
        pygame.draw.line(tela, cor, (int(x1), int(y1)), (int(x2), int(y2)), 3)

class GerenciadorSkidmarks:
    """Gerencia todos os skidmarks do jogo"""
    
    def __init__(self):
        self.skidmarks = []
        self.max_skidmarks = 100
    
    def adicionar_skidmark(self, x, y, angulo, intensidade=1.0):
        """Adiciona um novo skidmark baseado na posição e ângulo"""
        import math
        # Calcular posição final baseada no ângulo e intensidade
        comprimento = 10 * intensidade
        x2 = x + math.cos(angulo) * comprimento
        y2 = y + math.sin(angulo) * comprimento
        
        skidmark = Skidmark(x, y, x2, y2, duracao=4.0 * intensidade)
        self.skidmarks.append(skidmark)
        
        # Limitar número de skidmarks
        if len(self.skidmarks) > self.max_skidmarks:
            self.skidmarks.pop(0)
    
    def atualizar(self, dt):
        """Atualiza todos os skidmarks"""
        for skidmark in self.skidmarks[:]:
            skidmark.atualizar(dt)
            if not skidmark.ativo:
                self.skidmarks.remove(skidmark)
    
    def desenhar(self, tela, camera):
        """Desenha todos os skidmarks"""
        for skidmark in self.skidmarks:
            skidmark.desenhar(tela, camera)
    
    def limpar(self):
        """Remove todos os skidmarks"""
        self.skidmarks.clear()