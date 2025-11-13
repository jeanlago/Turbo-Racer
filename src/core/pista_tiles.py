"""
Sistema de pista usando tiles estilo GRIP
Carrega tiles de assets/pistas/ e monta a pista baseado em definições
"""
import pygame
import os
import json
from config import LARGURA, ALTURA

# Caminhos
DIR_PROJETO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIR_PISTAS = os.path.join(DIR_PROJETO, "assets", "images", "pistas")
DIR_LAPS = os.path.join(DIR_PROJETO, "data", "laps")

class GerenciadorTiles:
    """Gerencia o carregamento e acesso às tiles de pista"""
    
    def __init__(self):
        self.tiles = {}
        self.overhead_tile = None
        self._carregar_tiles()
    
    def _carregar_tiles(self):
        """Carrega todas as tiles de pista"""
        tiles_carregadas = 0
        
        # Tiles de curva (b-1-1, b-1-2, etc.)
        for b in range(1, 5):  # b-1 até b-4
            for c in range(1, 5):  # 1 até 4
                nome = f"b-{b}-{c}.png"
                caminho = os.path.join(DIR_PISTAS, nome)
                if os.path.exists(caminho):
                    chave = f"b-{b}-{c}"
                    self.tiles[chave] = pygame.image.load(caminho).convert_alpha()
                    tiles_carregadas += 1
                else:
                    print(f"AVISO: Tile não encontrada: {caminho}")
        
        # Tiles retas horizontais (st-h-3)
        for k in range(1, 5):
            nome = f"st-h-3-k{k}.png"
            caminho = os.path.join(DIR_PISTAS, nome)
            if os.path.exists(caminho):
                chave = f"st-h-3-k{k}"
                self.tiles[chave] = pygame.image.load(caminho).convert_alpha()
                tiles_carregadas += 1
            else:
                print(f"AVISO: Tile não encontrada: {caminho}")
        
        # Tile reta horizontal base
        nome = "st-h-3.png"
        caminho = os.path.join(DIR_PISTAS, nome)
        if os.path.exists(caminho):
            self.tiles["st-h-3"] = pygame.image.load(caminho).convert_alpha()
            tiles_carregadas += 1
        else:
            print(f"AVISO: Tile não encontrada: {caminho}")
        
        # Tile reta horizontal com listra (largada/chegada)
        nome = "st-h-3-ch.png"
        caminho = os.path.join(DIR_PISTAS, nome)
        if os.path.exists(caminho):
            self.tiles["st-h-3-ch"] = pygame.image.load(caminho).convert_alpha()
            tiles_carregadas += 1
            print(f"Tile de largada/chegada carregada: {caminho}")
        else:
            print(f"AVISO: Tile de largada/chegada não encontrada: {caminho}")
        
        # Tiles retas verticais (st-v-3)
        for k in range(1, 5):
            nome = f"st-v-3-k{k}.png"
            caminho = os.path.join(DIR_PISTAS, nome)
            if os.path.exists(caminho):
                chave = f"st-v-3-k{k}"
                self.tiles[chave] = pygame.image.load(caminho).convert_alpha()
                tiles_carregadas += 1
            else:
                print(f"AVISO: Tile não encontrada: {caminho}")
        
        # Tile reta vertical base
        nome = "st-v-3.png"
        caminho = os.path.join(DIR_PISTAS, nome)
        if os.path.exists(caminho):
            self.tiles["st-v-3"] = pygame.image.load(caminho).convert_alpha()
            tiles_carregadas += 1
        else:
            print(f"AVISO: Tile não encontrada: {caminho}")
        
        # Tile overhead (fundo)
        nome = "overhead_tile.png"
        caminho = os.path.join(DIR_PISTAS, nome)
        if os.path.exists(caminho):
            self.overhead_tile = pygame.image.load(caminho).convert_alpha()
            tiles_carregadas += 1
            print(f"Tile de fundo carregada: {caminho}")
        else:
            print(f"ERRO: Tile de fundo não encontrada: {caminho}")
        
        print(f"Total de tiles carregadas: {tiles_carregadas}")
        print(f"Tiles disponíveis: {list(self.tiles.keys())}")
    
    def obter_tile(self, nome):
        """Obtém uma tile pelo nome"""
        return self.tiles.get(nome)
    
    def obter_overhead(self):
        """Obtém a tile de fundo"""
        return self.overhead_tile

class PistaTiles:
    """
    Gerencia a construção e renderização de pistas usando tiles
    """
    def __init__(self, largura=5000, altura=5000):
        """
        Inicializa o gerenciador de pista
        largura e altura definem o tamanho total da superfície da pista
        """
        self.largura = largura
        self.altura = altura
        self.gerenciador_tiles = GerenciadorTiles()
        self.surface_pista = None
        self.definicao_pista = None
        self.posicao_inicial = (0, 0)  # Posição inicial do jogador
        
    def carregar_definicao_pista(self, numero_pista):
        """
        Carrega a definição de uma pista (hardcoded por enquanto, como no GRIP)
        Retorna uma lista de tuplas: (nome_tile, offset_x, offset_y)
        """
        # Por enquanto, vamos usar as definições do GRIP
        # Futuramente pode ser carregado de JSON
        definicoes = {
            1: self._definicao_pista_1,
            2: self._definicao_pista_2,
            3: self._definicao_pista_3,
            4: self._definicao_pista_4,
            5: self._definicao_pista_5,
            6: self._definicao_pista_6,
            7: self._definicao_pista_7,
            8: self._definicao_pista_8,
            9: self._definicao_pista_9,
        }
        
        if numero_pista in definicoes:
            return definicoes[numero_pista]()
        return []
    
    def _definicao_pista_1(self):
        """Definição da pista 1 (baseada no GRIP)"""
        # Posição inicial relativa ao centro da pista
        # A tile "st-h-3-ch" (linha de largada/chegada) está em (0, -100) relativa ao centro
        # No GRIP, a linha de largada está em (position[0]+50, position[1]-100)
        # Mas a tile horizontal está centrada em (0, -100)
        # Para centralizar os carros na largura da pista, vamos usar a posição do GRIP ajustada
        # A linha de largada no GRIP é vertical em x+50, mas a tile é horizontal
        # Vamos posicionar no centro da tile horizontal, que está em (0, -100)
        # Mas precisamos ajustar o Y para ficar mais centralizado na altura da pista
        # A tile está em y=-100, mas podemos ajustar um pouco para centralizar melhor
        # No GRIP, a linha de largada está em (position[0]+50, position[1]-100)
        # A tile st-h-3-ch está em (0, -100) relativa ao centro
        # Vamos usar a posição do GRIP (x+50) mas ajustar Y para centralizar melhor na altura da pista
        # Isso coloca os carros na linha de largada, mas mais centralizados verticalmente
        self.posicao_inicial_relativa = (50, -50)  # Relativo ao centro (2500, 2500) - alinhado com linha de largada do GRIP, mais centralizado
        
        return [
            ("st-h-3-k2", -1000, -115),
            ("st-h-3", -700, -100),
            ("st-h-3", -400, -100),
            ("st-h-3", -100, -100),
            ("st-h-3-ch", 0, -100),  # Tile de largada/chegada com listra branca
            ("st-h-3-k4", 300, -100),
            ("b-4-1", 600, -100),
            ("b-3-1", 600, 300),
            ("st-h-3-k3", 300, 385),
            ("st-h-3", 0, 400),
            ("st-h-3", -300, 400),
            ("st-h-3-k1", -600, 400),
            ("b-1-2", -1100, 400),
            ("b-2-2", -1100, 900),
            ("st-h-3-k2", -600, 1085),
            ("st-h-3", -300, 1100),
            ("st-h-3", 0, 1100),
            ("st-h-3", 300, 1100),
            ("st-h-3", 600, 1100),
            ("st-h-3-k3", 900, 1085),
            ("b-3-4", 1200, 700),
            ("st-v-3-k3", 1585, 400),
            ("st-v-3-k4", 1585, 100),
            ("b-4-1", 1500, -300),
            ("b-2-1", 1100, -400),
            ("b-4-4", 700, -1100),
            ("b-1-1", 300, -1100),
            ("b-3-1", 200, -700),
            ("st-h-3-k3", -100, -615),
            ("st-h-3-k2", -100, -615),
            ("b-2-2", -600, -800),
            ("b-4-1", -700, -1200),
            ("st-h-3-k4", -1000, -1200),
            ("st-h-3-k1", -1000, -1200),
            ("b-1-4", -1700, -1200),
            ("b-2-4", -1700, -500),
        ]
    
    def _definicao_pista_2(self):
        """Definição da pista 2"""
        centro_x, centro_y = LARGURA // 2, ALTURA // 2
        self.posicao_inicial = (centro_x + 50, centro_y - 50)
        
        return [
            ("st-h-3-k4", -100, -100),
            ("b-4-1", 200, -100),
            ("b-3-2", 100, 300),
            ("b-1-1", -300, 500),
            ("b-2-2", -300, 900),
            ("st-h-3-k2", 200, 1085),
            ("st-h-3-k3", 500, 1085),
            ("b-3-1", 800, 1000),
            ("st-v-3-k3", 885, 700),
            ("st-v-3", 900, 400),
            ("st-v-3", 900, 100),
            ("st-v-3-k4", 885, -200),
            ("b-4-2", 700, -700),
            ("b-2-1", 300, -800),
            ("b-4-2", 100, -1300),
            ("b-1-1", -300, -1300),
            ("b-3-2", -500, -900),
            ("st-h-3-k3", -800, -715),
            ("st-h-3", -1100, -700),
            ("st-h-3-k1", -1400, -700),
            ("b-1-1", -1800, -700),
            ("st-v-3-k1", -1800, -300),
            ("st-v-3-k2", -1800, 0),
            ("b-2-2", -1800, 300),
            ("st-h-3-k2", -1300, 485),
            ("b-3-1", -1000, 400),
            ("b-1-2", -900, -100),
            ("st-h-3-k1", -400, -100),
        ]
    
    def _definicao_pista_3(self):
        """Definição da pista 3"""
        centro_x, centro_y = LARGURA // 2, ALTURA // 2
        self.posicao_inicial = (centro_x + 50, centro_y - 50)
        
        return [
            ("st-h-3-k1", -900, -100),
            ("st-h-3", -600, -100),
            ("st-h-3", -300, -100),
            ("st-h-3", 0, -100),
            ("st-h-3-k4", 200, -100),
            ("b-4-1", 500, -100),
            ("b-3-1", 500, 300),
            ("b-1-1", 100, 400),
            ("b-2-1", 100, 800),
            ("st-h-3-k2", 500, 885),
            ("b-3-1", 800, 800),
            ("b-1-1", 900, 400),
            ("b-4-1", 1300, 400),
            ("st-v-3-k4", 1385, 800),
            ("st-v-3-k3", 1385, 900),
            ("b-3-4", 1000, 1200),
            ("st-h-3-k3", 700, 1585),
            ("st-h-3-k2", 400, 1585),
            ("b-2-1", 0, 1500),
            ("b-4-1", -100, 1100),
            ("b-1-1", -500, 1100),
            ("b-3-1", -600, 1500),
            ("b-2-2", -1100, 1400),
            ("b-1-2", -1100, 900),
            ("b-3-1", -600, 800),
            ("b-4-1", -600, 400),
            ("st-h-3-k4", -900, 400),
            ("st-h-3-k2", -900, 385),
            ("b-2-1", -1300, 300),
            ("b-1-1", -1300, -100),
        ]
    
    def _definicao_pista_4(self):
        """Definição da pista 4"""
        centro_x, centro_y = LARGURA // 2, ALTURA // 2
        self.posicao_inicial = (centro_x + 50, centro_y - 50)
        
        return [
            ("st-h-3-k1", -100, -100),
            ("st-h-3", 100, -100),
            ("st-h-3", 400, -100),
            ("st-h-3", 700, -100),
            ("st-h-3", 1000, -100),
            ("st-h-3-k4", 1200, -100),
            ("b-4-1", 1500, -100),
            ("b-2-2", 1600, 300),
            ("b-3-2", 2100, 300),
            ("b-1-1", 2300, -100),
            ("b-4-3", 2700, -100),
            ("st-v-3-k4", 2985, 500),
            ("b-3-3", 2700, 800),
            ("st-h-3-k3", 2400, 1085),
            ("st-h-3", 2100, 1100),
            ("st-h-3-k2", 1800, 1085),
            ("b-2-2", 1300, 900),
            ("b-4-2", 1100, 400),
            ("b-1-1", 700, 400),
            ("st-v-3-k1", 700, 800),
            ("b-2-2", 700, 1100),
            ("b-4-1", 1200, 1300),
            ("b-3-3", 1000, 1700),
            ("b-2-1", 600, 1900),
            ("b-4-1", 500, 1500),
            ("b-2-1", 100, 1400),
            ("st-v-3-k2", 100, 1100),
            ("b-4-1", 0, 700),
            ("b-2-3", -600, 400),
            ("b-1-2", -600, -100),
        ]
    
    def _definicao_pista_5(self):
        """Definição da pista 5"""
        centro_x, centro_y = LARGURA // 2, ALTURA // 2
        self.posicao_inicial = (centro_x + 50, centro_y - 50)
        
        return [
            ("b-1-1", -1300, -100),
            ("st-h-3-k1", -900, -100),
            ("st-h-3", -600, -100),
            ("st-h-3", -300, -100),
            ("st-h-3", 0, -100),
            ("st-h-3", 300, -100),
            ("st-h-3", 600, -100),
            ("st-h-3-k4", 900, -100),
            ("b-4-4", 1200, -100),
            ("st-v-3-k4", 1585, 600),
            ("b-3-1", 1500, 900),
            ("b-2-1", 1100, 900),
            ("b-4-1", 1000, 500),
            ("st-h-3-k4", 700, 500),
            ("st-h-3-k1", 400, 500),
            ("b-1-1", 0, 500),
            ("b-2-1", 0, 900),
            ("b-4-1", 400, 1000),
            ("st-v-3-k4", 485, 1400),
            ("b-3-3", 200, 1700),
            ("st-h-3-k3", -100, 1985),
            ("st-h-3", -300, 2000),
            ("st-h-3-k2", -600, 1985),
            ("b-2-1", -1000, 1900),
            ("b-1-1", -1000, 1500),
            ("b-3-1", -600, 1400),
            ("st-v-3-k3", -515, 1100),
            ("st-v-3-k4", -515, 800),
            ("b-4-1", -600, 400),
            ("st-h-3-k4", -900, 400),
            ("st-h-3-k2", -900, 385),
            ("b-2-1", -1300, 300),
            ("b-1-1", -1300, -100),
        ]
    
    def _definicao_pista_6(self):
        """Definição da pista 6"""
        centro_x, centro_y = LARGURA // 2, ALTURA // 2
        self.posicao_inicial = (centro_x + 50, centro_y - 50)
        
        return [
            ("b-1-2", -1800, -100),
            ("st-h-3-k1", -1300, -100),
            ("st-h-3", -1200, -100),
            ("st-h-3", -900, -100),
            ("st-h-3", -600, -100),
            ("st-h-3", -300, -100),
            ("st-h-3", 0, -100),
            ("st-h-3", 300, -100),
            ("st-h-3-k4", 600, -100),
            ("b-4-2", 900, -100),
            ("st-v-3-k4", 1085, 400),
            ("st-v-3", 1100, 700),
            ("st-v-3", 1100, 1000),
            ("st-v-3", 1100, 1300),
            ("st-v-3", 1100, 1600),
            ("st-v-3-k3", 1085, 1900),
            ("b-3-4", 700, 2200),
            ("b-2-2", 200, 2400),
            ("st-v-3-k2", 200, 2100),
            ("st-v-3", 200, 1800),
            ("st-v-3-k4", 185, 1500),
            ("b-4-4", -200, 800),
            ("st-h-3-k4", -500, 800),
            ("st-h-3", -800, 800),
            ("st-h-3-k2", -1100, 785),
            ("b-2-4", -1800, 400),
        ]
    
    def _definicao_pista_7(self):
        """Definição da pista 7"""
        centro_x, centro_y = LARGURA // 2, ALTURA // 2
        self.posicao_inicial = (centro_x + 50, centro_y - 50)
        
        return [
            ("b-1-1", -700, -100),
            ("st-h-3-k1", -300, -100),
            ("st-h-3-k4", 0, -100),
            ("b-4-1", 300, -100),
            ("b-3-2", 200, 300),
            ("b-1-1", -200, 500),
            ("b-2-3", -200, 900),
            ("b-3-4", 400, 800),
            ("st-v-3-k3", 785, 500),
            ("st-v-3-k1", 800, 400),
            ("b-1-4", 800, -300),
            ("b-3-4", 1500, -700),
            ("b-4-4", 1500, -1400),
            ("b-1-3", 900, -1400),
            ("b-3-2", 700, -800),
            ("b-2-1", 300, -700),
            ("b-4-3", 0, -1300),
            ("b-1-4", -700, -1300),
            ("b-3-4", -1100, -600),
            ("b-1-1", -1500, -200),
            ("b-2-3", -1500, 200),
            ("b-3-2", -900, 300),
            ("b-1-1", -700, -100),
        ]
    
    def _definicao_pista_8(self):
        """Definição da pista 8"""
        centro_x, centro_y = LARGURA // 2, ALTURA // 2
        self.posicao_inicial = (centro_x + 50, centro_y - 50)
        
        return [
            ("b-1-4", -1200, -100),
            ("st-h-3-k1", -500, -100),
            ("st-h-3", -200, -100),
            ("st-h-3-k3", 100, -115),
            ("b-3-1", 400, -200),
            ("b-1-4", 500, -900),
            ("b-4-4", 1200, -900),
            ("b-3-4", 1200, -200),
            ("b-1-1", 800, 200),
            ("st-v-3-k1", 800, 600),
            ("st-v-3-k2", 800, 600),
            ("b-2-1", 800, 900),
            ("b-3-2", 1200, 800),
            ("b-1-1", 1400, 400),
            ("st-h-3-k1", 1800, 400),
            ("st-h-3", 2100, 400),
            ("st-h-3-k3", 2400, 385),
            ("b-3-3", 2700, 100),
            ("b-1-1", 3000, -300),
            ("b-4-4", 3400, -300),
            ("b-3-4", 3400, 400),
            ("b-1-4", 2700, 800),
            ("b-3-3", 2400, 1500),
            ("st-h-3-k3", 2100, 1785),
            ("st-h-3", 1800, 1800),
            ("st-h-3", 1500, 1800),
            ("st-h-3", 1200, 1800),
            ("st-h-3-k2", 900, 1785),
            ("b-2-1", 500, 1700),
            ("b-4-1", 400, 1300),
            ("st-h-3-k4", 100, 1300),
            ("st-h-3", -200, 1300),
            ("st-h-3-k2", -500, 1285),
            ("b-2-4", -1200, 900),
            ("st-v-3-k2", -1200, 600),
            ("st-v-3-k1", -1200, 600),
        ]
    
    def _definicao_pista_9(self):
        """Definição da pista 9"""
        centro_x, centro_y = LARGURA // 2, ALTURA // 2
        self.posicao_inicial = (centro_x + 50, centro_y - 50)
        
        return [
            ("b-1-1", -800, -100),
            ("st-h-3-k1", -400, -100),
            ("st-h-3", -100, -100),
            ("st-h-3-k3", 200, -115),
            ("b-3-1", 500, -200),
            ("b-1-1", 600, -600),
            ("b-4-4", 1000, -600),
            ("st-v-3-k4", 1385, 100),
            ("st-v-3-k3", 1385, 100),
            ("b-3-4", 1000, 400),
            ("b-2-1", 600, 700),
            ("b-4-1", 500, 300),
            ("b-1-3", -100, 300),
            ("b-2-3", -100, 900),
            ("b-4-2", 500, 1200),
            ("st-v-3-k4", 685, 1700),
            ("st-v-3-k2", 700, 1700),
            ("b-2-2", 700, 2000),
            ("b-4-1", 1200, 2200),
            ("b-3-2", 1100, 2600),
            ("st-h-3-k3", 800, 2785),
            ("st-h-3", 500, 2800),
            ("st-h-3-k2", 200, 2785),
            ("b-2-4", -500, 2400),
            ("st-v-3-k2", -500, 2100),
            ("st-v-3", -500, 1800),
            ("st-v-3-k4", -515, 1600),
            ("b-4-2", -700, 1100),
            ("b-2-3", -1300, 800),
            ("b-1-1", -1300, 400),
            ("b-3-1", -900, 300),
        ]
    
    def construir_pista(self, numero_pista, posicao_centro=None):
        """
        Constrói uma superfície grande para a pista (estilo GRIP)
        No GRIP, a pista é desenhada dinamicamente, mas precisamos de uma superfície
        para verificação de colisão
        """
        if posicao_centro is None:
            posicao_centro = (self.largura // 2, self.altura // 2)
        
        # Carregar definição da pista primeiro para calcular limites reais
        self.definicao_pista = self.carregar_definicao_pista(numero_pista)
        print(f"Definição da pista {numero_pista} carregada: {len(self.definicao_pista)} tiles")
        
        # Calcular limites reais das tiles para expandir a superfície se necessário
        centro_x, centro_y = posicao_centro
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        
        for nome_tile, offset_x, offset_y in self.definicao_pista:
            tile = self.gerenciador_tiles.obter_tile(nome_tile)
            if tile:
                tile_w, tile_h = tile.get_size()
                x = centro_x + offset_x
                y = centro_y + offset_y
                min_x = min(min_x, x)
                max_x = max(max_x, x + tile_w)
                min_y = min(min_y, y)
                max_y = max(max_y, y + tile_h)
        
        # Adicionar margem de segurança
        margem = 500
        min_x = min(0, min_x - margem)
        max_x = max(self.largura, max_x + margem)
        min_y = min(0, min_y - margem)
        max_y = max(self.altura, max_y + margem)
        
        # Calcular dimensões expandidas
        largura_expandida = int(max_x - min_x)
        altura_expandida = int(max_y - min_y)
        
        # Limitar tamanho máximo para evitar problemas de memória (pygame tem limite de ~32767 pixels)
        tamanho_maximo = 30000
        if largura_expandida > tamanho_maximo or altura_expandida > tamanho_maximo:
            print(f"AVISO: Pista muito grande ({largura_expandida}x{altura_expandida}), limitando a {tamanho_maximo}")
            largura_expandida = min(largura_expandida, tamanho_maximo)
            altura_expandida = min(altura_expandida, tamanho_maximo)
        
        # Atualizar dimensões da superfície
        self.largura = largura_expandida
        self.altura = altura_expandida
        
        # Ajustar centro para o novo sistema de coordenadas
        offset_x_superficie = -min_x
        offset_y_superficie = -min_y
        centro_x_ajustado = centro_x + offset_x_superficie
        centro_y_ajustado = centro_y + offset_y_superficie
        
        # Armazenar offset para uso externo
        self.offset_x_superficie = offset_x_superficie
        self.offset_y_superficie = offset_y_superficie
        
        print(f"Superfície expandida: {largura_expandida}x{altura_expandida} (original: {self.largura}x{self.altura})")
        print(f"Limites das tiles: min_x={min_x:.0f}, max_x={max_x:.0f}, min_y={min_y:.0f}, max_y={max_y:.0f}")
        print(f"Offset da superfície: ({offset_x_superficie:.0f}, {offset_y_superficie:.0f})")
        
        # Criar superfície expandida para a pista
        self.surface_pista = pygame.Surface((largura_expandida, altura_expandida))
        
        # Preencher com fundo verde usando overhead_tile repetida (estilo GRIP)
        overhead = self.gerenciador_tiles.obter_overhead()
        if overhead:
            tile_w, tile_h = overhead.get_size()
            print(f"Desenhando fundo com tile {tile_w}x{tile_h}")
            # Preencher toda a superfície expandida com tiles de fundo
            for y in range(0, altura_expandida + tile_h, tile_h):
                for x in range(0, largura_expandida + tile_w, tile_w):
                    self.surface_pista.blit(overhead, (x, y))
            print(f"Fundo verde desenhado em superfície {largura_expandida}x{altura_expandida}")
        else:
            # Fallback: preencher com verde sólido
            print("AVISO: Usando verde sólido (overhead_tile não encontrada)")
            self.surface_pista.fill((0, 200, 0))
        
        # Renderizar todas as tiles da pista no novo sistema de coordenadas
        tiles_desenhadas = 0
        tiles_fora_limites = 0
        
        for nome_tile, offset_x, offset_y in self.definicao_pista:
            tile = self.gerenciador_tiles.obter_tile(nome_tile)
            if tile:
                # Calcular posição absoluta na superfície expandida
                # Ajustar para o novo sistema de coordenadas
                x = centro_x_ajustado + offset_x
                y = centro_y_ajustado + offset_y
                
                # Verificar se está dentro dos limites da superfície expandida
                if 0 <= x < largura_expandida and 0 <= y < altura_expandida:
                    self.surface_pista.blit(tile, (int(x), int(y)))
                    tiles_desenhadas += 1
                else:
                    tiles_fora_limites += 1
                    print(f"AVISO: Tile {nome_tile} fora dos limites expandidos: ({x}, {y})")
            else:
                print(f"ERRO: Tile não encontrada: {nome_tile}")
        
        print(f"Tiles da pista desenhadas: {tiles_desenhadas}/{len(self.definicao_pista)} (fora dos limites: {tiles_fora_limites})")
        print(f"Centro da pista: ({centro_x}, {centro_y})")
        if self.definicao_pista:
            print(f"Primeira tile em: ({centro_x + self.definicao_pista[0][1]}, {centro_y + self.definicao_pista[0][2]})")
        
        # Após construir a pista, tentar encontrar o centro real na largada
        # Isso garante que a posição inicial seja calculada corretamente
        print("Tentando encontrar centro real da pista na largada...")
        centro_largada = self.encontrar_centro_pista_na_largada()
        if centro_largada:
            print(f"Centro encontrado! Atualizando posição inicial para: {centro_largada}")
            self.posicao_inicial_relativa = centro_largada
        
        return self.surface_pista
    
    def desenhar_pista_dinamica(self, surface_destino, posicao_jogador):
        """
        Desenha a pista dinamicamente baseada na posição do jogador (estilo GRIP)
        posicao_jogador: (x, y) - posição atual do jogador no mundo
        """
        # Desenhar fundo verde usando overhead_tile repetida
        overhead = self.gerenciador_tiles.obter_overhead()
        if overhead:
            tile_w, tile_h = overhead.get_size()
            # Calcular offset do fundo baseado na posição (estilo GRIP)
            bg_x = int(posicao_jogador[0]) % tile_w
            bg_y = int(posicao_jogador[1]) % tile_h
            
            # Desenhar tiles de fundo cobrindo toda a tela visível
            for y in range(-tile_h, surface_destino.get_height() + tile_h, tile_h):
                for x in range(-tile_w, surface_destino.get_width() + tile_w, tile_w):
                    surface_destino.blit(overhead, (x - bg_x, y - bg_y))
        else:
            # Fallback: preencher com verde
            surface_destino.fill((0, 200, 0))
        
        # Desenhar tiles da pista baseadas na posição do jogador
        if self.definicao_pista:
            px, py = posicao_jogador
            for nome_tile, offset_x, offset_y in self.definicao_pista:
                tile = self.gerenciador_tiles.obter_tile(nome_tile)
                if tile:
                    # Calcular posição relativa ao jogador (estilo GRIP)
                    x = px + offset_x
                    y = py + offset_y
                    # Converter para coordenadas de tela
                    # No GRIP, position[0] e position[1] são a posição do jogador
                    # e as tiles são desenhadas relativas a essa posição
                    screen_x = x - px + surface_destino.get_width() // 2
                    screen_y = y - py + surface_destino.get_height() // 2
                    surface_destino.blit(tile, (screen_x, screen_y))
    
    def desenhar_pista(self, surface_destino, camera=None, posicao_centro=None):
        """
        Desenha a pista na superfície de destino
        camera: objeto Camera para culling
        posicao_centro: (x, y) - posição do centro (atualizada dinamicamente)
        """
        if self.surface_pista is None:
            return
        
        if camera is None:
            # Desenhar toda a pista (não recomendado para pistas grandes)
            surface_destino.blit(self.surface_pista, (0, 0))
        else:
            # Desenhar apenas a parte visível
            # Por enquanto, desenhamos toda a pista
            # TODO: Implementar culling baseado na câmera
            surface_destino.blit(self.surface_pista, (0, 0))
    
    def encontrar_centro_tile_largada(self):
        """Encontra o centro da tile st-h-3-ch (linha de largada)"""
        # Obter a tile st-h-3-ch
        tile = self.gerenciador_tiles.obter_tile("st-h-3-ch")
        if tile is None:
            print("AVISO: Tile st-h-3-ch não encontrada")
            return None
        
        # Obter dimensões da tile
        tile_w, tile_h = tile.get_size()
        print(f"Tile st-h-3-ch: {tile_w}x{tile_h} pixels")
        
        # A tile está posicionada em (0, -100) relativa ao centro
        # O canto superior esquerdo da tile está em (centro_x + 0, centro_y - 100)
        # O CENTRO da tile está em (centro_x + tile_w/2, centro_y - 100 + tile_h/2)
        centro_x, centro_y = 2500, 2500
        
        # Centro da tile em coordenadas absolutas
        tile_center_x = centro_x + (tile_w // 2)
        tile_center_y = centro_y - 100 + (tile_h // 2)
        
        # Retornar relativo ao centro da superfície
        offset_x = tile_center_x - centro_x
        offset_y = tile_center_y - centro_y
        
        print(f"Centro da tile st-h-3-ch: ({tile_center_x}, {tile_center_y}) (relativo: ({offset_x}, {offset_y}))")
        return (offset_x, offset_y)
    
    def encontrar_centro_pista_na_largada(self):
        """Encontra o centro real da pista na linha de largada, verificando a tile st-h-3-ch"""
        # Primeiro, tentar usar o centro geométrico da tile
        centro_tile = self.encontrar_centro_tile_largada()
        if centro_tile:
            return centro_tile
        
        # Fallback: procurar o centro da pista verificando pixels
        if self.surface_pista is None:
            return None
        
        try:
            from core.pista_grip import eh_pixel_grama_grip
        except:
            return None
        
        # A tile st-h-3-ch está em (0, -100) relativa ao centro
        centro_x, centro_y = 2500, 2500
        tile_y = centro_y - 100
        
        # Procurar o centro horizontal da pista nessa linha Y
        pontos_pista = []
        
        # Verificar uma faixa de Y ao redor da linha de largada
        for y_offset in range(-10, 11, 1):
            y = int(tile_y + y_offset)
            if 0 <= y < self.surface_pista.get_height():
                for x in range(0, self.surface_pista.get_width(), 2):
                    try:
                        if not eh_pixel_grama_grip(self.surface_pista, x, y):
                            pontos_pista.append(x)
                    except:
                        continue
        
        if pontos_pista:
            pontos_pista.sort()
            if len(pontos_pista) > 10:
                inicio = len(pontos_pista) // 10
                fim = len(pontos_pista) - inicio
                pontos_centrais = pontos_pista[inicio:fim]
                if pontos_centrais:
                    min_x = pontos_centrais[0]
                    max_x = pontos_centrais[-1]
                else:
                    min_x = pontos_pista[0]
                    max_x = pontos_pista[-1]
            else:
                min_x = pontos_pista[0]
                max_x = pontos_pista[-1]
            
            centro_real_x = (min_x + max_x) // 2
            offset_x = centro_real_x - centro_x
            print(f"Centro real da pista na largada (fallback): X={centro_real_x} (relativo: {offset_x}), largura={max_x - min_x}")
            return (offset_x, -100)
        
        print("AVISO: Não foi possível encontrar o centro da pista na largada")
        return None
    
    def obter_posicao_inicial(self):
        """Retorna a posição inicial do jogador (relativa ao centro)"""
        # Tentar encontrar o centro real da pista na linha de largada
        centro_real = self.encontrar_centro_pista_na_largada()
        if centro_real:
            print(f"Centro real da pista na largada encontrado: {centro_real}")
            return centro_real
        
        # Retorna posição relativa ao centro da pista
        if hasattr(self, 'posicao_inicial_relativa'):
            return self.posicao_inicial_relativa
        # Fallback: posição padrão (alinhado com linha de largada do GRIP, mais centralizado na pista)
        return (50, -50)
    
    def verificar_se_na_pista(self, x, y):
        """Verifica se uma posição (absoluta) está na pista"""
        if self.surface_pista is None:
            return False
        
        if x < 0 or y < 0 or x >= self.surface_pista.get_width() or y >= self.surface_pista.get_height():
            return False
        
        try:
            from core.pista_grip import eh_pixel_grama_grip
            # Se não está na grama, está na pista
            return not eh_pixel_grama_grip(self.surface_pista, x, y)
        except:
            return True
    
    def obter_surface_pista(self):
        """Retorna a superfície renderizada da pista"""
        return self.surface_pista
    
    def carregar_minimapa(self, numero_pista):
        """
        Carrega o minimapa da pista
        Retorna a imagem do minimapa ou None se não encontrado
        """
        nome_arquivo = f"track{numero_pista}.png"
        caminho_arquivo = os.path.join(DIR_PISTAS, nome_arquivo)
        
        if os.path.exists(caminho_arquivo):
            try:
                minimapa = pygame.image.load(caminho_arquivo).convert_alpha()
                print(f"Minimapa carregado: {nome_arquivo} ({minimapa.get_width()}x{minimapa.get_height()})")
                return minimapa
            except Exception as e:
                print(f"Erro ao carregar minimapa: {e}")
                return None
        else:
            print(f"Minimapa não encontrado: {caminho_arquivo}")
            return None
    
    def calcular_limites_reais_pista(self, numero_pista):
        """
        Calcula os limites reais da pista baseado nas tiles
        Retorna (min_x, min_y, max_x, max_y) em coordenadas absolutas
        """
        if not hasattr(self, 'definicao_pista') or not self.definicao_pista:
            # Se não tem definição, retornar limites padrão
            return (0, 0, 5000, 5000)
        
        centro_x, centro_y = 2500, 2500
        
        # Encontrar limites das tiles
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        
        for nome_tile, offset_x, offset_y in self.definicao_pista:
            tile = self.gerenciador_tiles.obter_tile(nome_tile)
            if tile:
                tile_w, tile_h = tile.get_size()
                x = centro_x + offset_x
                y = centro_y + offset_y
                
                min_x = min(min_x, x)
                max_x = max(max_x, x + tile_w)
                min_y = min(min_y, y)
                max_y = max(max_y, y + tile_h)
        
        # Retornar limites exatos sem margem - isso garante mapeamento preciso no minimapa
        # A margem será adicionada apenas na visualização do minimapa se necessário
        return (min_x, min_y, max_x, max_y)

