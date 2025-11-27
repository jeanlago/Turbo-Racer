#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Pista com Tiles de Noite
Visualiza como a pista fica usando as tiles da pasta noite
"""

import pygame
import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import LARGURA, ALTURA, FPS, DIR_PROJETO

# Caminho para tiles de noite
DIR_PISTAS_NOITE = os.path.join(DIR_PROJETO, "assets", "images", "pistas", "noite")

class GerenciadorTilesNoite:
    """Gerencia o carregamento e acesso às tiles de pista de noite"""
    
    def __init__(self):
        self.tiles = {}
        self.overhead_tile = None
        self._carregar_tiles()
    
    def _carregar_tiles(self):
        """Carrega todas as tiles de pista da pasta noite"""
        tiles_carregadas = 0
        
        # Tiles de curva (b-1-1, b-1-2, etc.)
        for b in range(1, 5):  # b-1 até b-4
            for c in range(1, 5):  # 1 até 4
                nome = f"b-{b}-{c}.png"
                caminho = os.path.join(DIR_PISTAS_NOITE, nome)
                if os.path.exists(caminho):
                    chave = f"b-{b}-{c}"
                    self.tiles[chave] = pygame.image.load(caminho).convert_alpha()
                    tiles_carregadas += 1
                else:
                    print(f"AVISO: Tile não encontrada: {caminho}")
        
        # Tiles retas horizontais (st-h-3)
        for k in range(1, 5):
            nome = f"st-h-3-k{k}.png"
            caminho = os.path.join(DIR_PISTAS_NOITE, nome)
            if os.path.exists(caminho):
                chave = f"st-h-3-k{k}"
                self.tiles[chave] = pygame.image.load(caminho).convert_alpha()
                tiles_carregadas += 1
            else:
                print(f"AVISO: Tile não encontrada: {caminho}")
        
        # Tile reta horizontal base
        nome = "st-h-3.png"
        caminho = os.path.join(DIR_PISTAS_NOITE, nome)
        if os.path.exists(caminho):
            self.tiles["st-h-3"] = pygame.image.load(caminho).convert_alpha()
            tiles_carregadas += 1
        else:
            print(f"AVISO: Tile não encontrada: {caminho}")
        
        # Tile reta horizontal com listra (largada/chegada)
        nome = "st-h-3-ch.png"
        caminho = os.path.join(DIR_PISTAS_NOITE, nome)
        if os.path.exists(caminho):
            self.tiles["st-h-3-ch"] = pygame.image.load(caminho).convert_alpha()
            tiles_carregadas += 1
            print(f"Tile de largada/chegada carregada: {caminho}")
        else:
            print(f"AVISO: Tile de largada/chegada não encontrada: {caminho}")
        
        # Tiles retas verticais (st-v-3)
        for k in range(1, 5):
            nome = f"st-v-3-k{k}.png"
            caminho = os.path.join(DIR_PISTAS_NOITE, nome)
            if os.path.exists(caminho):
                chave = f"st-v-3-k{k}"
                self.tiles[chave] = pygame.image.load(caminho).convert_alpha()
                tiles_carregadas += 1
            else:
                print(f"AVISO: Tile não encontrada: {caminho}")
        
        # Tile reta vertical base
        nome = "st-v-3.png"
        caminho = os.path.join(DIR_PISTAS_NOITE, nome)
        if os.path.exists(caminho):
            self.tiles["st-v-3"] = pygame.image.load(caminho).convert_alpha()
            tiles_carregadas += 1
        else:
            print(f"AVISO: Tile não encontrada: {caminho}")
        
        # Tile overhead (fundo) - nome pode ter espaço e hífen
        # Tentar diferentes variações do nome
        nomes_overhead = [
            "overhead_tile - noite.png",
            "overhead_tile-noite.png",
            "overhead_tile_noite.png",
            "overhead_tile.png"
        ]
        
        for nome in nomes_overhead:
            caminho = os.path.join(DIR_PISTAS_NOITE, nome)
            if os.path.exists(caminho):
                self.overhead_tile = pygame.image.load(caminho).convert_alpha()
                tiles_carregadas += 1
                print(f"Tile de fundo carregada: {caminho}")
                break
        
        if self.overhead_tile is None:
            print(f"ERRO: Tile de fundo não encontrada na pasta {DIR_PISTAS_NOITE}")
            print(f"Tentou: {nomes_overhead}")
        
        print(f"Total de tiles carregadas: {tiles_carregadas}")
        print(f"Tiles disponíveis: {list(self.tiles.keys())}")
    
    def obter_tile(self, nome_tile):
        """Obtém uma tile pelo nome"""
        return self.tiles.get(nome_tile)
    
    def obter_overhead(self):
        """Obtém a tile de fundo"""
        return self.overhead_tile

class PistaTilesNoite:
    """Versão modificada de PistaTiles que usa tiles de noite"""
    
    def __init__(self, largura=5000, altura=5000):
        self.largura = largura
        self.altura = altura
        self.gerenciador_tiles = GerenciadorTilesNoite()
        self.surface_pista = None
        self.definicao_pista = None
        self.posicao_inicial = (0, 0)
    
    def construir_pista(self, numero_pista, posicao_centro=(2500, 2500)):
        """Constrói a pista usando as tiles de noite"""
        # Importar a classe original para usar a definição
        from core.pista_tiles import PistaTiles
        
        # Criar instância temporária para obter a definição
        pista_temp = PistaTiles(self.largura, self.altura)
        definicao = pista_temp.carregar_definicao_pista(numero_pista)
        
        if not definicao:
            print(f"Erro: Definição da pista {numero_pista} não encontrada")
            return None
        
        self.definicao_pista = definicao
        
        # Criar superfície para a pista
        self.surface_pista = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        
        # Obter tile de fundo
        overhead = self.gerenciador_tiles.obter_overhead()
        if overhead:
            # Preencher toda a superfície com tiles de fundo
            tile_w, tile_h = overhead.get_size()
            for x in range(0, self.largura, tile_w):
                for y in range(0, self.altura, tile_h):
                    self.surface_pista.blit(overhead, (x, y))
        
        # Desenhar tiles da pista
        for tile_info in definicao:
            if len(tile_info) >= 3:
                nome_tile, offset_x, offset_y = tile_info[0], tile_info[1], tile_info[2]
                
                # Obter tile
                tile = self.gerenciador_tiles.obter_tile(nome_tile)
                if tile:
                    # Calcular posição absoluta
                    x = posicao_centro[0] + offset_x
                    y = posicao_centro[1] + offset_y
                    self.surface_pista.blit(tile, (x, y))
                else:
                    print(f"AVISO: Tile '{nome_tile}' não encontrada nas tiles de noite")
        
        print(f"Pista {numero_pista} construída com tiles de noite ({self.surface_pista.get_width()}x{self.surface_pista.get_height()})")
        return self.surface_pista

def main():
    """Função principal de teste"""
    pygame.init()
    
    # Criar tela
    screen = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Teste - Pista de Noite")
    
    clock = pygame.time.Clock()
    
    # Criar pista com tiles de noite
    pista_noite = PistaTilesNoite(largura=5000, altura=5000)
    
    # Selecionar pista (padrão: pista 1)
    numero_pista = 1
    
    print(f"\n=== TESTE DE PISTA DE NOITE ===")
    print(f"Construindo pista {numero_pista} com tiles de noite...")
    superficie_pista = pista_noite.construir_pista(numero_pista)
    
    if not superficie_pista:
        print("Erro ao construir pista!")
        return
    
    # Câmera para navegar pela pista
    camera_x = 0
    camera_y = 0
    velocidade_camera = 5
    
    rodando = True
    
    print("\nControles:")
    print("  WASD ou Setas - Mover câmera")
    print("  1-9 - Trocar pista")
    print("  R - Recarregar pista atual")
    print("  ESC - Sair")
    
    while rodando:
        dt = clock.tick(FPS) / 1000.0
        
        # Processar eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False
                elif evento.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, 
                                    pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                    numero_pista = int(evento.unicode)
                    print(f"\nTrocando para pista {numero_pista}...")
                    superficie_pista = pista_noite.construir_pista(numero_pista)
                elif evento.key == pygame.K_r:
                    print(f"\nRecarregando pista {numero_pista}...")
                    superficie_pista = pista_noite.construir_pista(numero_pista)
        
        # Mover câmera
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            camera_y -= velocidade_camera
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            camera_y += velocidade_camera
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            camera_x -= velocidade_camera
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            camera_x += velocidade_camera
        
        # Limitar câmera aos limites da pista
        if superficie_pista:
            camera_x = max(0, min(camera_x, superficie_pista.get_width() - LARGURA))
            camera_y = max(0, min(camera_y, superficie_pista.get_height() - ALTURA))
        
        # Desenhar
        screen.fill((0, 0, 0))
        
        if superficie_pista:
            # Desenhar porção visível da pista
            screen.blit(superficie_pista, (-camera_x, -camera_y))
        
        # Desenhar informações
        fonte = pygame.font.SysFont("consolas", 20)
        info_texto = fonte.render(f"Pista: {numero_pista} | Camera: ({camera_x}, {camera_y}) | WASD/Setas: Mover | 1-9: Trocar | R: Recarregar", 
                                 True, (255, 255, 255))
        screen.blit(info_texto, (10, 10))
        
        pygame.display.flip()
    
    pygame.quit()
    print("\nTeste finalizado.")

if __name__ == "__main__":
    main()

