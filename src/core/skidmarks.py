import pygame

class Skidmark:
    """Representa um segmento de linha de skidmark"""
    
    def __init__(self, x1, y1, x2, y2, duracao=4.0, alpha=255, na_grama=False):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.duracao = duracao
        self.tempo_vida = 0.0
        self.alpha = alpha
        self.ativo = True
        self.na_grama = na_grama  # Flag para indicar se foi criado na grama
    
    def atualizar(self, dt):
        """Atualiza o skidmark"""
        self.tempo_vida += dt
    
    def desenhar(self, tela, camera):
        """Desenha o skidmark"""
        if not self.ativo:
            return
        
        if camera:
            x1, y1 = camera.mundo_para_tela(self.x1, self.y1)
            x2, y2 = camera.mundo_para_tela(self.x2, self.y2)
        else:
            x1, y1 = self.x1, self.y1
            x2, y2 = self.x2, self.y2
        
        if self.na_grama:
            cor = (139, 69, 19)
        else:
            cor = (0, 0, 0)
        pygame.draw.line(tela, cor, (int(x1), int(y1)), (int(x2), int(y2)), 3)

class GerenciadorSkidmarks:
    """Gerencia todos os skidmarks do jogo"""
    
    def __init__(self):
        self.skidmarks = []
        self.max_skidmarks = 120
        self.ultima_posicoes = {}
    
    def adicionar_skidmark(self, x, y, angulo, intensidade=1.0, pneu_id="traseiro_esq", na_grama=False):
        """Adiciona um novo skidmark baseado na posição e ângulo"""
        import math
        
        if intensidade > 0.05:
            if pneu_id in self.ultima_posicoes:
                x_anterior, y_anterior, na_grama_anterior = self.ultima_posicoes[pneu_id]
                distancia = math.sqrt((x - x_anterior)**2 + (y - y_anterior)**2)
                if distancia > 2.0 and distancia < 100.0:
                    skidmark = Skidmark(x_anterior, y_anterior, x, y, duracao=5.0 * intensidade, na_grama=na_grama_anterior)
                    self.skidmarks.append(skidmark)
                elif distancia >= 100.0:
                    del self.ultima_posicoes[pneu_id]
            
            self.ultima_posicoes[pneu_id] = (x, y, na_grama)
        
        if len(self.skidmarks) > self.max_skidmarks:
            self.skidmarks.pop(0)
    
    def atualizar(self, dt):
        """Atualiza todos os skidmarks"""
        for skidmark in self.skidmarks:
            skidmark.atualizar(dt)
    
    def desenhar(self, tela, camera):
        """Desenha todos os skidmarks - otimizado"""
        if camera:
            visao = camera.ret_visao()
            margem = 50
            for skidmark in self.skidmarks:
                if (visao.left - margem <= skidmark.x1 <= visao.right + margem and
                    visao.top - margem <= skidmark.y1 <= visao.bottom + margem) or \
                   (visao.left - margem <= skidmark.x2 <= visao.right + margem and
                    visao.top - margem <= skidmark.y2 <= visao.bottom + margem):
                    skidmark.desenhar(tela, camera)
        else:
            for skidmark in self.skidmarks:
                skidmark.desenhar(tela, camera)
    
    def limpar(self):
        """Remove todos os skidmarks"""
        self.skidmarks.clear()
        self.ultima_posicoes.clear()
    
    def parar_rastro(self):
        """Para o rastro contínuo (quando para de derrapar)"""
        self.ultima_posicoes.clear()