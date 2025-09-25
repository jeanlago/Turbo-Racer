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
        # Marca permanente - nunca fica inativa
        # self.ativo sempre permanece True
    
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
        
        # Desenhar linha preta para marcas de pneu
        cor = (0, 0, 0)  # Preto para marcas de pneu
        pygame.draw.line(tela, cor, (int(x1), int(y1)), (int(x2), int(y2)), 3)  # Mais fina

class GerenciadorSkidmarks:
    """Gerencia todos os skidmarks do jogo"""
    
    def __init__(self):
        self.skidmarks = []
        self.max_skidmarks = 120  # Restaurado para manter marcas em todas as 4 rodas
        self.ultima_posicoes = {}  # Para conectar os skidmarks de cada pneu
    
    def adicionar_skidmark(self, x, y, angulo, intensidade=1.0, pneu_id="traseiro_esq"):
        """Adiciona um novo skidmark baseado na posição e ângulo"""
        import math
        
        # Só criar skidmark se a intensidade for significativa (handbrake sempre cria)
        if intensidade > 0.1:  # Threshold restaurado para manter marcas em todas as 4 rodas
            # Se temos uma posição anterior para este pneu, conectar com ela
            if pneu_id in self.ultima_posicoes:
                x_anterior, y_anterior = self.ultima_posicoes[pneu_id]
                # Verificar se a distância é significativa para evitar skidmarks muito próximos
                distancia = math.sqrt((x - x_anterior)**2 + (y - y_anterior)**2)
                if distancia > 2.0:  # Distância menor para marcas mais contínuas
                    # Criar skidmark conectando com a posição anterior
                    skidmark = Skidmark(x_anterior, y_anterior, x, y, duracao=5.0 * intensidade)
                    self.skidmarks.append(skidmark)
            
            # Atualizar posição anterior para este pneu
            self.ultima_posicoes[pneu_id] = (x, y)
        
        # Limitar número de skidmarks
        if len(self.skidmarks) > self.max_skidmarks:
            self.skidmarks.pop(0)
    
    def atualizar(self, dt):
        """Atualiza todos os skidmarks"""
        for skidmark in self.skidmarks:
            skidmark.atualizar(dt)
        # Não remover skidmarks - eles são permanentes
    
    def desenhar(self, tela, camera):
        """Desenha todos os skidmarks"""
        for skidmark in self.skidmarks:
            skidmark.desenhar(tela, camera)
    
    def limpar(self):
        """Remove todos os skidmarks"""
        self.skidmarks.clear()
        self.ultima_posicoes.clear()
    
    def parar_rastro(self):
        """Para o rastro contínuo (quando para de derrapar)"""
        self.ultima_posicoes.clear()