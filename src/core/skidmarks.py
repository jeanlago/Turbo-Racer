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
        
        # Desenhar linha - marrom se estiver na grama, preto se estiver na pista
        if self.na_grama:
            cor = (139, 69, 19)  # Marrom para marcas na grama
        else:
            cor = (0, 0, 0)  # Preto para marcas na pista
        pygame.draw.line(tela, cor, (int(x1), int(y1)), (int(x2), int(y2)), 3)  # Mais fina

class GerenciadorSkidmarks:
    """Gerencia todos os skidmarks do jogo"""
    
    def __init__(self):
        self.skidmarks = []
        self.max_skidmarks = 120  # Restaurado para manter marcas em todas as 4 rodas
        self.ultima_posicoes = {}  # Para conectar os skidmarks de cada pneu
    
    def adicionar_skidmark(self, x, y, angulo, intensidade=1.0, pneu_id="traseiro_esq", na_grama=False):
        """Adiciona um novo skidmark baseado na posição e ângulo"""
        import math
        
        # Só criar skidmark se a intensidade for significativa (handbrake sempre cria) - mais permissivo
        if intensidade > 0.05:  # Threshold mais baixo para detectar mais ângulos
            # Se temos uma posição anterior para este pneu, conectar com ela
            if pneu_id in self.ultima_posicoes:
                x_anterior, y_anterior, na_grama_anterior = self.ultima_posicoes[pneu_id]
                # Verificar se a distância é significativa para evitar skidmarks muito próximos
                distancia = math.sqrt((x - x_anterior)**2 + (y - y_anterior)**2)
                # Limitar distância máxima para evitar linhas imensas ao trocar de tile
                # Se a distância for muito grande, provavelmente houve teleporte ou mudança de tile
                if distancia > 2.0 and distancia < 100.0:  # Distância mínima e máxima
                    # Criar skidmark conectando com a posição anterior
                    # Usar na_grama da posição anterior para manter consistência
                    skidmark = Skidmark(x_anterior, y_anterior, x, y, duracao=5.0 * intensidade, na_grama=na_grama_anterior)
                    self.skidmarks.append(skidmark)
                elif distancia >= 100.0:
                    # Se a distância for muito grande, limpar a posição anterior
                    # Isso evita criar linhas imensas quando há teleporte ou mudança de tile
                    del self.ultima_posicoes[pneu_id]
            
            # Atualizar posição anterior para este pneu (incluindo flag de grama)
            self.ultima_posicoes[pneu_id] = (x, y, na_grama)
        
        # Limitar número de skidmarks
        if len(self.skidmarks) > self.max_skidmarks:
            self.skidmarks.pop(0)
    
    def atualizar(self, dt):
        """Atualiza todos os skidmarks"""
        for skidmark in self.skidmarks:
            skidmark.atualizar(dt)
        # Não remover skidmarks - eles são permanentes
    
    def desenhar(self, tela, camera):
        """Desenha todos os skidmarks - otimizado"""
        # Filtrar apenas skidmarks visíveis
        if camera:
            visao = camera.ret_visao()
            margem = 50  # Margem para garantir que skidmarks próximos sejam desenhados
            for skidmark in self.skidmarks:
                # Verificar se pelo menos um ponto está visível
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