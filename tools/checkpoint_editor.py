#!/usr/bin/env python3
"""
Ferramenta de Edição de Checkpoints - Turbo Racer
================================================

Esta ferramenta permite editar, criar e remover checkpoints de forma independente
do jogo principal. Útil para configurar novos mapas ou ajustar checkpoints existentes.

Controles:
- F7: Ativar/Desativar modo de edição
- F5: Salvar checkpoints
- F6: Carregar checkpoints
- F8: Limpar todos os checkpoints
- F9: Trocar mapa
- ESC: Sair
- Mouse: Clique para adicionar, arrastar para mover, clique direito para remover

Autor: Turbo Racer Team
Versão: 1.0
"""

import sys
import os
import pygame
import re
import json
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import LARGURA, ALTURA, FPS, MAPAS_DISPONIVEIS
from core.camera import Camera
from core.pista_tiles import PistaTiles
from core.laps_grip import carregar_checkpoints_grip

class CheckpointEditor:
    def __init__(self):
        pygame.init()
        
        try:
            info = pygame.display.Info()
            largura_editor = min(1920, info.current_w - 100)
            altura_editor = min(1080, info.current_h - 100)
        except:
            largura_editor = 1920
            altura_editor = 1080
        
        self.largura_tela = max(LARGURA, largura_editor)
        self.altura_tela = max(ALTURA, altura_editor)
        
        self.screen = pygame.display.set_mode((self.largura_tela, self.altura_tela))
        pygame.display.set_caption("Checkpoint Editor - Turbo Racer")
        self.clock = pygame.time.Clock()
        
        self.modo_edicao = False
        self.checkpoints = []
        self.checkpoint_selecionado = -1
        self.checkpoint_em_arraste = -1
        self.arrastando_camera = False
        
        self.spawn_points = []
        self.spawn_selecionado = -1
        self.spawn_em_arraste = -1
        self.modo_spawn = False
        
        self.usar_tiles_grip = True
        self.numero_pista = 1
        self.pista_tiles = None
        self.surface_pista_completa = None
        self.largura_pista = 5000
        self.altura_pista = 5000
        
        self.mapas_disponiveis = list(range(1, 10))
        self.indice_mapa_atual = 0
        
        self.mapa_atual = f"Pista_{self.numero_pista}"
        self.img_pista = None
        self.mask_pista = None
        self.mask_guias = None
        
        zoom_para_ver_tudo = min(self.largura_tela / self.largura_pista, self.altura_tela / self.altura_pista) * 0.9
        self.zoom_min = 0.4
        self.zoom_max = 2.0
        zoom_inicial = max(self.zoom_min, zoom_para_ver_tudo)
        self.camera = Camera(self.largura_tela, self.altura_tela, self.largura_pista, self.altura_pista, zoom=zoom_inicial)
        self.camera.cx = self.largura_pista // 2
        self.camera.cy = self.altura_pista // 2
        
        self.fonte = pygame.font.Font(None, 24)
        self.fonte_pequena = pygame.font.Font(None, 18)
        
        self.carregar_mapa()
        self.carregar_checkpoints()
        
        self.mostrar_ajuda = True
        self.huds_visiveis = True
        self.ultimo_clique_tempo = 0
        self.debounce_tempo = 200

    def set_zoom(self, novo_zoom):
        """Define o zoom com clamp e quantização"""
        clamped = max(self.zoom_min, min(self.zoom_max, float(novo_zoom)))
        quantizado = round(clamped, 1)
        if abs(quantizado - self.camera.zoom) < 1e-6:
            return False
        self.camera.zoom = quantizado
        return True
        
    def ajustar_camera_para_pista(self):
        """Ajusta a câmera para mostrar toda a pista baseado nos limites reais"""
        if not self.pista_tiles:
            return
        
        try:
            limites = self.pista_tiles.calcular_limites_reais_pista(self.numero_pista)
            min_x, min_y, max_x, max_y = limites
            
            largura_real = max_x - min_x
            altura_real = max_y - min_y
            
            margem = 200
            largura_real += margem * 2
            altura_real += margem * 2
            
            zoom_para_ver_tudo = min(self.largura_tela / largura_real, self.altura_tela / altura_real) * 0.85
            zoom_ajustado = max(self.zoom_min, min(self.zoom_max, zoom_para_ver_tudo))
            self.camera.zoom = zoom_ajustado
            
            margem_mundo_x = 1000
            margem_mundo_y_cima = 500
            margem_mundo_y_baixo = 2000
            min_x_expandido = min_x - margem_mundo_x
            min_y_expandido = min_y - margem_mundo_y_cima
            max_x_expandido = max_x + margem_mundo_x
            max_y_expandido = max_y + margem_mundo_y_baixo
            
            largura_mundo_necessaria = max_x_expandido - min_x_expandido
            altura_mundo_necessaria = max_y_expandido - min_y_expandido
            self.camera.largura_mundo = max(self.largura_pista, largura_mundo_necessaria)
            self.camera.altura_mundo = max(self.altura_pista, altura_mundo_necessaria)
            
            centro_x_real = (min_x + max_x) / 2
            centro_y_real = (min_y + max_y) / 2
            self.camera.cx = centro_x_real
            self.camera.cy = centro_y_real
            
            vw = self.camera.largura_tela / self.camera.zoom
            vh = self.camera.altura_tela / self.camera.zoom
            half_w = vw / 2
            half_h = vh / 2
            
            margem_clamp_x = 100
            margem_clamp_y_cima = 100
            margem_clamp_y_baixo = 800
            self.camera.cx = max(min_x - half_w + margem_clamp_x, min(max_x + half_w - margem_clamp_x, self.camera.cx))
            self.camera.cy = max(min_y - half_h + margem_clamp_y_cima, min(max_y + half_h - margem_clamp_y_baixo, self.camera.cy))
            
            print(f"Câmera ajustada: zoom={self.camera.zoom:.2f}, centro=({self.camera.cx:.0f}, {self.camera.cy:.0f}), limites=({min_x:.0f}, {min_y:.0f}, {max_x:.0f}, {max_y:.0f})")
            
        except Exception as e:
            print(f"Erro ao ajustar câmera: {e}")
            self.camera.cx = self.largura_pista // 2
            self.camera.cy = self.altura_pista // 2
    
    def carregar_mapa(self):
        """Carrega o mapa atual usando sistema de tiles do GRIP"""
        try:
            self.pista_tiles = PistaTiles(largura=self.largura_pista, altura=self.altura_pista)
            self.surface_pista_completa = self.pista_tiles.construir_pista(self.numero_pista)
            
            self.img_pista = self.surface_pista_completa.copy()
            self.mask_pista = self.surface_pista_completa.copy()
            self.mask_guias = pygame.Surface((self.largura_pista, self.altura_pista), pygame.SRCALPHA)
            
            self.camera.largura_mundo = self.largura_pista
            self.camera.altura_mundo = self.altura_pista
            
            print(f"Pista GRIP {self.numero_pista} carregada: {self.largura_pista}x{self.altura_pista}")
            
            self.ajustar_camera_para_pista()
            self.carregar_checkpoints()
        except Exception as e:
            print(f"Erro ao carregar pista GRIP: {e}")
            import traceback
            traceback.print_exc()
            self.surface_pista_completa = pygame.Surface((self.largura_pista, self.altura_pista))
            self.surface_pista_completa.fill((0, 200, 0))
            self.img_pista = self.surface_pista_completa.copy()
            self.mask_pista = self.img_pista.copy()
            self.mask_guias = pygame.Surface((self.largura_pista, self.altura_pista), pygame.SRCALPHA)
            self.carregar_checkpoints()
    
    def obter_caminho_checkpoints_pista(self):
        """Retorna o caminho do arquivo JSON de checkpoints para a pista atual"""
        diretorio = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(diretorio, exist_ok=True)
        return os.path.join(diretorio, f"checkpoints_pista_{self.numero_pista}.json")
    
    def carregar_checkpoints(self):
        """Carrega checkpoints e spawn points do arquivo JSON (prioridade) ou do GRIP (fallback)"""
        try:
            arquivo = self.obter_caminho_checkpoints_pista()
            if os.path.exists(arquivo):
                with open(arquivo, 'r', encoding='utf-8') as f:
                    dados_carregados = json.load(f)
                
                if isinstance(dados_carregados, dict):
                    checkpoints_carregados = dados_carregados.get("checkpoints", [])
                    self.spawn_points = dados_carregados.get("spawn_points", [])
                else:
                    checkpoints_carregados = dados_carregados
                    self.spawn_points = []
                
                self.checkpoints = []
                for cp in checkpoints_carregados:
                    if len(cp) == 2:
                        self.checkpoints.append([float(cp[0]), float(cp[1]), 0])
                    elif len(cp) == 3:
                        self.checkpoints.append([float(cp[0]), float(cp[1]), float(cp[2])])
                
                if self.spawn_points:
                    self.spawn_points = [[float(sp[0]), float(sp[1])] for sp in self.spawn_points if len(sp) >= 2]
                
                print(f"Carregados {len(self.checkpoints)} checkpoints do JSON para pista {self.numero_pista}")
                print(f"Carregados {len(self.spawn_points)} spawn points do JSON para pista {self.numero_pista}")
                return
            
            checkpoints_grip = carregar_checkpoints_grip(self.numero_pista)
            if checkpoints_grip:
                self.checkpoints = []
                for cp in checkpoints_grip:
                    if len(cp) >= 3:
                        self.checkpoints.append([float(cp[0]), float(cp[1]), float(cp[2])])
                    else:
                        self.checkpoints.append([float(cp[0]), float(cp[1]), 0])
                
                try:
                    arquivo_spawn = self.obter_caminho_checkpoints_pista()
                    if os.path.exists(arquivo_spawn):
                        with open(arquivo_spawn, 'r', encoding='utf-8') as f:
                            dados_spawn = json.load(f)
                        if isinstance(dados_spawn, dict):
                            spawn_grip = dados_spawn.get("spawn_points", [])
                            if spawn_grip:
                                self.spawn_points = [[float(sp[0]), float(sp[1])] for sp in spawn_grip if len(sp) >= 2]
                            else:
                                self.spawn_points = []
                        else:
                            self.spawn_points = []
                    else:
                        self.spawn_points = []
                except:
                    self.spawn_points = []
                print(f"Carregados {len(self.checkpoints)} checkpoints do GRIP para pista {self.numero_pista}")
                print(f"Carregados {len(self.spawn_points)} spawn points do GRIP para pista {self.numero_pista}")
            else:
                self.checkpoints = []
                self.spawn_points = []
                print(f"Nenhum checkpoint encontrado para pista {self.numero_pista}")
        except Exception as e:
            print(f"Erro ao carregar checkpoints: {e}")
            import traceback
            traceback.print_exc()
            self.checkpoints = []
            self.spawn_points = []
    
    def obter_mapas_disponiveis(self):
        """Obtém lista de pistas GRIP disponíveis (1-9)"""
        # Retornar lista de números de pistas do GRIP
        return list(range(1, 10))
    
    def trocar_mapa_direcional(self, direcao):
        """Troca para a pista anterior ou próxima do GRIP (1-9)."""
        if len(self.mapas_disponiveis) <= 1:
            return False

        if self.checkpoints:
            self.salvar_checkpoints()

        if direcao == "anterior":
            self.indice_mapa_atual = (self.indice_mapa_atual - 1) % len(self.mapas_disponiveis)
        else:  # "proximo"
            self.indice_mapa_atual = (self.indice_mapa_atual + 1) % len(self.mapas_disponiveis)

        self.numero_pista = self.mapas_disponiveis[self.indice_mapa_atual]
        self.mapa_atual = f"Pista_{self.numero_pista}"
        self.checkpoint_selecionado = -1
        self.checkpoint_em_arraste = -1
        self.carregar_mapa()
        print(f"Pista alterada para: GRIP Pista {self.numero_pista}")
        return True
    
    def salvar_checkpoints(self):
        """Salva checkpoints e spawn points no JSON e exporta para laps_grip.py"""
        try:
            arquivo = self.obter_caminho_checkpoints_pista()
            os.makedirs(os.path.dirname(arquivo), exist_ok=True)
            
            dados_para_salvar = {
                "checkpoints": self.checkpoints,
                "spawn_points": self.spawn_points,
                "numero_pista": self.numero_pista
            }
            
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_para_salvar, f, indent=2)
            
            print(f"Checkpoints salvos em JSON para pista {self.numero_pista}: {len(self.checkpoints)} checkpoints, {len(self.spawn_points)} spawn points")
            
            if self.exportar_para_laps_grip():
                print(f"Checkpoints exportados para laps_grip.py - serão usados no jogo!")
            else:
                print(f"AVISO: Não foi possível exportar para laps_grip.py. Use F10 para exportar manualmente.")
            
            return True
        except Exception as e:
            print(f"Erro ao salvar checkpoints: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def exportar_para_laps_grip(self):
        """Exporta checkpoints diretamente para o arquivo laps_grip.py"""
        try:
            caminho_laps_grip = os.path.join(os.path.dirname(__file__), '..', 'src', 'core', 'laps_grip.py')
            
            if not os.path.exists(caminho_laps_grip):
                print(f"Erro: Arquivo não encontrado: {caminho_laps_grip}")
                return False
            
            with open(caminho_laps_grip, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
            
            inicio_bloco = None
            fim_bloco = None
            for i, linha in enumerate(linhas):
                if f'if numero_pista == {self.numero_pista}:' in linha:
                    inicio_bloco = i
                elif inicio_bloco is not None and (linha.strip().startswith('elif numero_pista ==') or linha.strip().startswith('else:')):
                    fim_bloco = i
                    break
            
            if inicio_bloco is None:
                print(f"Erro: Não foi possível encontrar o bloco da pista {self.numero_pista} em laps_grip.py")
                return False
            
            if fim_bloco is None:
                for i in range(inicio_bloco + 1, len(linhas)):
                    linha_stripped = linhas[i].strip()
                    if linha_stripped.startswith('elif numero_pista ==') or linha_stripped.startswith('else:'):
                        fim_bloco = i
                        break
                if fim_bloco is None:
                    fim_bloco = len(linhas) - 1
            
            centro_x, centro_y = 2500, 2500
            novo_codigo = []
            novo_codigo.append(f"    if numero_pista == {self.numero_pista}:\n")
            
            for i, cp in enumerate(self.checkpoints):
                x, y = cp[0], cp[1]
                angulo = cp[2] if len(cp) > 2 else 0
                offset_x = x - centro_x
                offset_y = y - centro_y
                novo_codigo.append(f"        checkpoint_{i+1} = (centro_x + {offset_x:.0f}, centro_y + {offset_y:.0f}, {angulo:.0f})  # Ângulo: {angulo:.0f}°\n")
            
            novo_codigo.append("        # Checkpoints com ângulo: (x, y, angulo) ou (x, y) para cálculo automático\n")
            novo_codigo.append("        checkpoints = [\n")
            for i in range(len(self.checkpoints)):
                novo_codigo.append(f"            tuple(checkpoint_{i+1}),\n")
            novo_codigo.append("        ]\n")
            
            novas_linhas = linhas[:inicio_bloco] + novo_codigo + linhas[fim_bloco:]
            
            with open(caminho_laps_grip, 'w', encoding='utf-8') as f:
                f.writelines(novas_linhas)
            
            print(f"Checkpoints exportados para laps_grip.py (Pista {self.numero_pista})")
            return True
        except Exception as e:
            print(f"Erro ao exportar para laps_grip.py: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def trocar_mapa_por_id(self, numero_pista):
        """Troca para uma nova pista GRIP (1-9)."""
        if 1 <= numero_pista <= 9:
            if self.checkpoints or self.spawn_points:
                self.salvar_checkpoints()
                print(f"Dados da pista {self.numero_pista} salvos antes de trocar")

            self.numero_pista = numero_pista
            self.indice_mapa_atual = numero_pista - 1
            self.mapa_atual = f"Pista_{numero_pista}"
            self.checkpoint_selecionado = -1
            self.checkpoint_em_arraste = -1
            self.spawn_selecionado = -1
            self.spawn_em_arraste = -1
            
            self.carregar_mapa()
            print(f"Trocado para pista GRIP: {numero_pista}")
            return True
        return False
    
    def adicionar_checkpoint(self, x, y):
        """Adiciona um checkpoint na posição especificada"""
        if not self.modo_edicao:
            return
        
        mundo_x, mundo_y = self.camera.tela_para_mundo(x, y)
        # Formato: [x, y, angulo] - ângulo em graus (0 = horizontal, 90 = vertical)
        self.checkpoints.append([int(mundo_x), int(mundo_y), 0])
        print(f"Checkpoint adicionado: ({mundo_x:.0f}, {mundo_y:.0f}) com ângulo 0°")
    
    def remover_checkpoint(self, x, y):
        """Remove o checkpoint mais próximo da posição especificada"""
        if not self.modo_edicao or not self.checkpoints:
            return
        
        mundo_x, mundo_y = self.camera.tela_para_mundo(x, y)
        
        melhor_indice = -1
        menor_distancia = float('inf')
        
        for i, cp in enumerate(self.checkpoints):
            cx, cy = cp[0], cp[1]
            distancia = ((mundo_x - cx) ** 2 + (mundo_y - cy) ** 2) ** 0.5
            if distancia < menor_distancia:
                menor_distancia = distancia
                melhor_indice = i
        
        if melhor_indice >= 0 and menor_distancia < 30:  # 30 pixels de tolerância
            checkpoint_removido = self.checkpoints.pop(melhor_indice)
            print(f"Checkpoint removido: {checkpoint_removido}")
    
    def rotacionar_checkpoint(self, indice, incremento=90):
        """Rotaciona um checkpoint em incremento graus"""
        if 0 <= indice < len(self.checkpoints):
            cp = self.checkpoints[indice]
            if len(cp) == 2:
                cp.append(0)
            cp[2] = (cp[2] + incremento) % 360
            print(f"Checkpoint {indice + 1} rotacionado para {cp[2]:.0f}°")
    
    def mover_checkpoint(self, indice, novo_x, novo_y):
        """Move um checkpoint para uma nova posição"""
        if 0 <= indice < len(self.checkpoints):
            cp = self.checkpoints[indice]
            if len(cp) > 2:
                self.checkpoints[indice] = [int(novo_x), int(novo_y), cp[2]]
            else:
                self.checkpoints[indice] = [int(novo_x), int(novo_y), 0]
    
    def adicionar_spawn_point(self, x, y):
        """Adiciona um spawn point na posição especificada"""
        if not self.modo_spawn:
            return
        
        mundo_x, mundo_y = self.camera.tela_para_mundo(x, y)
        self.spawn_points.append([int(mundo_x), int(mundo_y)])
        print(f"Spawn point adicionado: ({mundo_x:.0f}, {mundo_y:.0f})")
    
    def remover_spawn_point(self, x, y):
        """Remove o spawn point mais próximo da posição especificada"""
        if not self.modo_spawn or not self.spawn_points:
            return
        
        mundo_x, mundo_y = self.camera.tela_para_mundo(x, y)
        
        melhor_indice = -1
        menor_distancia = float('inf')
        
        for i, sp in enumerate(self.spawn_points):
            sx, sy = sp[0], sp[1]
            distancia = ((mundo_x - sx) ** 2 + (mundo_y - sy) ** 2) ** 0.5
            if distancia < menor_distancia:
                menor_distancia = distancia
                melhor_indice = i
        
        if melhor_indice >= 0 and menor_distancia < 30:  # 30 pixels de tolerância
            spawn_removido = self.spawn_points.pop(melhor_indice)
            print(f"Spawn point removido: {spawn_removido}")
    
    def mover_spawn_point(self, indice, novo_x, novo_y):
        """Move um spawn point para uma nova posição"""
        if 0 <= indice < len(self.spawn_points):
            self.spawn_points[indice] = [int(novo_x), int(novo_y)]
    
    def encontrar_spawn_proximo(self, x, y, raio_base=30):
        """Encontra o spawn point mais próximo da posição especificada"""
        if not self.spawn_points:
            return -1
        
        mundo_x, mundo_y = self.camera.tela_para_mundo(x, y)
        raio = max(15, int(raio_base * self.camera.zoom))
        
        melhor_indice = -1
        menor_distancia = float('inf')
        
        for i, sp in enumerate(self.spawn_points):
            sx, sy = sp[0], sp[1]
            distancia = ((mundo_x - sx) ** 2 + (mundo_y - sy) ** 2) ** 0.5
            if distancia < menor_distancia:
                menor_distancia = distancia
                melhor_indice = i
        
        if melhor_indice >= 0 and menor_distancia < raio:
            return melhor_indice
        return -1
    
    def encontrar_checkpoint_proximo(self, x, y, raio_base=30):
        """Encontra o checkpoint mais próximo da posição especificada com raio baseado n-o zoom."""
        mundo_x, mundo_y = self.camera.tela_para_mundo(x, y)
        raio = max(15, int(raio_base * self.camera.zoom))
        
        melhor_indice = -1
        menor_distancia = float('inf')
        
        for i, cp in enumerate(self.checkpoints):
            cx, cy = cp[0], cp[1]
            distancia = ((mundo_x - cx) ** 2 + (mundo_y - cy) ** 2) ** 0.5
            if distancia < menor_distancia:
                menor_distancia = distancia
                melhor_indice = i
        
        if melhor_indice >= 0 and menor_distancia < raio:
            return melhor_indice
        return -1
    
    def processar_eventos(self):
        """Processa eventos do pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_F7:
                    # Shift+F7 para modo spawn, F7 normal para modo checkpoint
                    teclas = pygame.key.get_pressed()
                    if teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT]:
                        self.modo_spawn = not self.modo_spawn
                        self.modo_edicao = False  # Desativar modo checkpoint quando ativar spawn
                        print(f"Modo SPAWN: {'ATIVADO' if self.modo_spawn else 'DESATIVADO'}")
                    else:
                        self.modo_edicao = not self.modo_edicao
                        self.modo_spawn = False  # Desativar modo spawn quando ativar checkpoint
                        print(f"Modo de edição CHECKPOINT: {'ATIVADO' if self.modo_edicao else 'DESATIVADO'}")
                elif event.key == pygame.K_F5:
                    if self.salvar_checkpoints():
                        print("Checkpoints salvos em JSON (backup)!")
                elif event.key == pygame.K_F6:
                    self.carregar_checkpoints()
                    print("Checkpoints recarregados!")
                elif event.key == pygame.K_F8:
                    # Shift+F8 para limpar spawn points, F8 normal para checkpoints
                    teclas = pygame.key.get_pressed()
                    if teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT]:
                        self.spawn_points = []
                        print("Todos os spawn points removidos!")
                    else:
                        self.checkpoints = []
                        print("Todos os checkpoints removidos!")
                elif event.key == pygame.K_F9:
                    self.mostrar_selecao_mapa()
                elif event.key == pygame.K_F10:
                    # Exportar diretamente para laps_grip.py
                    if self.exportar_para_laps_grip():
                        print("Checkpoints exportados para laps_grip.py!")
                    else:
                        print("Erro ao exportar para laps_grip.py")
                elif event.key == pygame.K_r:
                    # Rotacionar checkpoint selecionado 90 graus
                    if self.modo_edicao and self.checkpoint_selecionado >= 0:
                        self.rotacionar_checkpoint(self.checkpoint_selecionado, 90)
                elif event.key == pygame.K_q:
                    # Rotacionar checkpoint selecionado -15 graus
                    if self.modo_edicao and self.checkpoint_selecionado >= 0:
                        self.rotacionar_checkpoint(self.checkpoint_selecionado, -15)
                elif event.key == pygame.K_e:
                    # Rotacionar checkpoint selecionado +15 graus
                    if self.modo_edicao and self.checkpoint_selecionado >= 0:
                        self.rotacionar_checkpoint(self.checkpoint_selecionado, 15)
                elif event.key == pygame.K_h:
                    # Alterna ambos HUDs (principal e ajuda)
                    self.huds_visiveis = not self.huds_visiveis
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    # Aumentar zoom
                    if self.camera.zoom >= self.zoom_max - 1e-6:
                        # No limite: ignorar
                        continue
                    if self.set_zoom(self.camera.zoom + 0.2):
                        print(f"Zoom: {self.camera.zoom:.1f}x")
                elif event.key == pygame.K_MINUS:
                    # Diminuir zoom
                    if self.camera.zoom <= self.zoom_min + 1e-6:
                        # No limite: ignorar
                        continue
                    if self.set_zoom(self.camera.zoom - 0.2):
                        print(f"Zoom: {self.camera.zoom:.1f}x")
                elif event.key == pygame.K_0:
                    # Resetar zoom
                    if self.set_zoom(1.0):
                        print("Zoom resetado para 1.0x")
                elif event.key == pygame.K_LEFT:
                    # Mapa anterior
                    self.trocar_mapa_direcional("anterior")
                elif event.key == pygame.K_RIGHT:
                    # Próximo mapa
                    self.trocar_mapa_direcional("proximo")
                elif event.key == 44:  # Tecla , (código ASCII)
                    # Mapa anterior
                    self.trocar_mapa_direcional("anterior")
                elif event.key == 46:  # Tecla . (código ASCII)
                    # Próximo mapa
                    self.trocar_mapa_direcional("proximo")
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clique esquerdo
                    if self.modo_spawn:
                        # Modo spawn: adicionar/mover spawn points
                        tempo_atual = pygame.time.get_ticks()
                        if tempo_atual - self.ultimo_clique_tempo >= self.debounce_tempo:
                            self.ultimo_clique_tempo = tempo_atual
                            
                            # Verificar se clicou em um spawn point existente
                            indice = self.encontrar_spawn_proximo(event.pos[0], event.pos[1], 30)
                            if indice >= 0:
                                self.spawn_em_arraste = indice
                                self.spawn_selecionado = indice
                                print(f"Spawn point {indice} selecionado para arrastar")
                            else:
                                # Adicionar novo spawn point
                                self.adicionar_spawn_point(event.pos[0], event.pos[1])
                    elif self.modo_edicao:
                        tempo_atual = pygame.time.get_ticks()
                        if tempo_atual - self.ultimo_clique_tempo >= self.debounce_tempo:
                            self.ultimo_clique_tempo = tempo_atual
                            
                            # Verificar se clicou em um checkpoint existente
                            indice = self.encontrar_checkpoint_proximo(event.pos[0], event.pos[1], 30)
                            if indice >= 0:
                                self.checkpoint_em_arraste = indice
                                self.checkpoint_selecionado = indice
                                print(f"Checkpoint {indice} selecionado para arrastar")
                            else:
                                # Adicionar novo checkpoint
                                self.adicionar_checkpoint(event.pos[0], event.pos[1])
                    else:
                        # Arrastar câmera
                        self.arrastando_camera = True
                
                elif event.button == 3:  # Clique direito
                    if self.modo_spawn:
                        self.remover_spawn_point(event.pos[0], event.pos[1])
                    elif self.modo_edicao:
                        self.remover_checkpoint(event.pos[0], event.pos[1])
                    else:
                        # Verificar clique nos botões de navegação
                        if len(self.mapas_disponiveis) > 1:
                            mouse_x, mouse_y = event.pos
                            
                            # Botão anterior
                            botao_anterior_rect = pygame.Rect(20, 270, 30, 25)
                            if botao_anterior_rect.collidepoint(mouse_x, mouse_y):
                                self.trocar_mapa_direcional("anterior")
                            
                            # Botão próximo
                            botao_proximo_rect = pygame.Rect(200, 270, 30, 25)
                            if botao_proximo_rect.collidepoint(mouse_x, mouse_y):
                                self.trocar_mapa_direcional("proximo")
            
            elif event.type == pygame.MOUSEWHEEL:
                # Zoom com scroll do mouse
                if event.y > 0:  # Scroll para cima - aumentar zoom
                    if self.camera.zoom < self.zoom_max - 1e-6:
                        if self.set_zoom(self.camera.zoom + 0.1):
                            print(f"Zoom: {self.camera.zoom:.1f}x")
                elif event.y < 0:  # Scroll para baixo - diminuir zoom
                    if self.camera.zoom > self.zoom_min + 1e-6:
                        if self.set_zoom(self.camera.zoom - 0.1):
                            print(f"Zoom: {self.camera.zoom:.1f}x")
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.spawn_em_arraste >= 0:
                        self.spawn_em_arraste = -1
                        print("Spawn point solto")
                    elif self.checkpoint_em_arraste >= 0:
                        self.checkpoint_em_arraste = -1
                        print("Checkpoint solto")
                    elif self.arrastando_camera:
                        self.arrastando_camera = False
                        print("Câmera solta")
            
            elif event.type == pygame.MOUSEMOTION:
                if self.modo_spawn and self.spawn_em_arraste >= 0:
                    # Arrastar spawn point
                    mundo_x, mundo_y = self.camera.tela_para_mundo(event.pos[0], event.pos[1])
                    self.mover_spawn_point(self.spawn_em_arraste, mundo_x, mundo_y)
                elif self.modo_edicao and self.checkpoint_em_arraste >= 0:
                    # Arrastar checkpoint
                    mundo_x, mundo_y = self.camera.tela_para_mundo(event.pos[0], event.pos[1])
                    self.mover_checkpoint(self.checkpoint_em_arraste, mundo_x, mundo_y)
                elif self.arrastando_camera and hasattr(event, 'rel') and (event.rel[0] != 0 or event.rel[1] != 0):
                    # Arrastar câmera
                    sensibilidade = 1.0 / self.camera.zoom
                    self.camera.cx -= event.rel[0] * sensibilidade
                    self.camera.cy -= event.rel[1] * sensibilidade
                    # Usar clamp baseado nos limites reais da pista, permitindo movimento livre
                    if self.pista_tiles:
                        try:
                            limites = self.pista_tiles.calcular_limites_reais_pista(self.numero_pista)
                            min_x, min_y, max_x, max_y = limites
                            vw = self.camera.largura_tela / self.camera.zoom
                            vh = self.camera.altura_tela / self.camera.zoom
                            half_w = vw / 2
                            half_h = vh / 2
                            # Margem positiva para permitir ver além das bordas da pista
                            # Margem maior para baixo para permitir ver mais da parte inferior
                            margem_clamp_x = 100  # Margem para esquerda/direita
                            margem_clamp_y_cima = 100  # Margem para cima
                            margem_clamp_y_baixo = 800  # Margem muito maior para baixo (permitir descer muito mais)
                            # Permitir movimento livre dentro dos limites expandidos
                            self.camera.cx = max(min_x - half_w + margem_clamp_x, min(max_x + half_w - margem_clamp_x, self.camera.cx))
                            # Permitir descer muito mais do que subir
                            self.camera.cy = max(min_y - half_h + margem_clamp_y_cima, min(max_y + half_h - margem_clamp_y_baixo, self.camera.cy))
                        except:
                            self.camera._clamp_centro()
                    else:
                        self.camera._clamp_centro()
        
        return True
    
    def mostrar_selecao_mapa(self):
        """Mostra menu de seleção de mapa"""
        print("\n=== SELECIONAR MAPA ===")
        for i, (mapa_id, info) in enumerate(MAPAS_DISPONIVEIS.items()):
            print(f"{i + 1}. {info['nome']} ({mapa_id})")
        
        try:
            escolha = input("Digite o número do mapa (ou Enter para cancelar): ").strip()
            if escolha:
                indice = int(escolha) - 1
                if 0 <= indice < len(MAPAS_DISPONIVEIS):
                    mapa_id = list(MAPAS_DISPONIVEIS.keys())[indice]
                    self.trocar_mapa_por_id(mapa_id)
        except (ValueError, IndexError):
            print("Escolha inválida!")
    
    def desenhar(self):
        """Desenha a interface do editor"""
        self.screen.fill((0, 0, 0))
        
        if self.surface_pista_completa:
            self.camera.desenhar_fundo(self.screen, self.surface_pista_completa)
        else:
            self.camera.desenhar_fundo(self.screen, self.img_pista)
        
        if self.checkpoints:
            for i in range(len(self.checkpoints)):
                if i < len(self.checkpoints) - 1:
                    cp1 = self.checkpoints[i]
                    cp2 = self.checkpoints[i + 1]
                    x1, y1 = cp1[0], cp1[1]
                    x2, y2 = cp2[0], cp2[1]
                    
                    if not (self.camera.esta_visivel(x1, y1, margem=50) or 
                           self.camera.esta_visivel(x2, y2, margem=50)):
                        continue
                        
                    screen_x1, screen_y1 = self.camera.mundo_para_tela(x1, y1)
                    screen_x2, screen_y2 = self.camera.mundo_para_tela(x2, y2)
                    
                    if not ((0 <= screen_x1 <= self.largura_tela and 0 <= screen_y1 <= self.altura_tela) or
                           (0 <= screen_x2 <= self.largura_tela and 0 <= screen_y2 <= self.altura_tela)):
                        continue
                    
                    if i == self.checkpoint_selecionado or i + 1 == self.checkpoint_selecionado:
                        cor_linha = (255, 255, 0)
                    else:
                        cor_linha = (0, 200, 255)
                    
                    pygame.draw.line(self.screen, cor_linha, 
                                   (int(screen_x1), int(screen_y1)), 
                                   (int(screen_x2), int(screen_y2)), 3)
            
            for i, cp in enumerate(self.checkpoints):
                x, y = cp[0], cp[1]
                angulo = cp[2] if len(cp) > 2 else 0
                
                CHECKPOINT_LARGURA = 300
                CHECKPOINT_ESPESSURA = 1
                
                rect_base = pygame.Rect(
                    -CHECKPOINT_LARGURA // 2,
                    -CHECKPOINT_ESPESSURA // 2,
                    CHECKPOINT_LARGURA,
                    CHECKPOINT_ESPESSURA
                )
                
                superficie_rect = pygame.Surface((CHECKPOINT_LARGURA, CHECKPOINT_ESPESSURA), pygame.SRCALPHA)
                
                if i == self.checkpoint_selecionado:
                    cor = (255, 255, 0, 150)
                    cor_borda = (255, 255, 0)
                else:
                    cor = (0, 255, 255, 100)
                    cor_borda = (0, 255, 255)
                
                superficie_rect.fill(cor)
                pygame.draw.rect(superficie_rect, cor_borda, rect_base, 3)
                
                if angulo != 0:
                    superficie_rect = pygame.transform.rotate(superficie_rect, -angulo)
                
                screen_x, screen_y = self.camera.mundo_para_tela(x, y)
                rect_rotacionado = superficie_rect.get_rect(center=(int(screen_x), int(screen_y)))
                
                if not (rect_rotacionado.colliderect(pygame.Rect(0, 0, self.largura_tela, self.altura_tela))):
                    continue
                
                self.screen.blit(superficie_rect, rect_rotacionado)
                
                texto = self.fonte.render(str(i + 1), True, (255, 255, 255))
                texto_rect = texto.get_rect(center=(int(screen_x), int(screen_y)))
                
                fundo_texto = pygame.Surface((texto_rect.width + 8, texto_rect.height + 4), pygame.SRCALPHA)
                fundo_texto.fill((0, 0, 0, 200))
                self.screen.blit(fundo_texto, (texto_rect.x - 4, texto_rect.y - 2))
                self.screen.blit(texto, texto_rect)
                
                if i == self.checkpoint_selecionado and angulo != 0:
                    texto_angulo = self.fonte_pequena.render(f"{angulo:.0f}°", True, (255, 255, 0))
                    texto_angulo_rect = texto_angulo.get_rect(center=(int(screen_x), int(screen_y) + 25))
                    fundo_angulo = pygame.Surface((texto_angulo_rect.width + 8, texto_angulo_rect.height + 4), pygame.SRCALPHA)
                    fundo_angulo.fill((0, 0, 0, 200))
                    self.screen.blit(fundo_angulo, (texto_angulo_rect.x - 4, texto_angulo_rect.y - 2))
                    self.screen.blit(texto_angulo, texto_angulo_rect)
        
        if self.spawn_points:
            for i, sp in enumerate(self.spawn_points):
                x, y = sp[0], sp[1]
                screen_x, screen_y = self.camera.mundo_para_tela(x, y)
                
                if not (0 <= screen_x <= self.largura_tela and 0 <= screen_y <= self.altura_tela):
                    continue
                
                raio = 15
                if i == self.spawn_selecionado:
                    cor_spawn = (0, 255, 0)
                    pygame.draw.circle(self.screen, cor_spawn, (int(screen_x), int(screen_y)), raio + 3, 3)
                else:
                    cor_spawn = (0, 200, 0)
                
                pygame.draw.circle(self.screen, cor_spawn, (int(screen_x), int(screen_y)), raio)
                pygame.draw.circle(self.screen, (255, 255, 255), (int(screen_x), int(screen_y)), raio, 2)
                
                texto_spawn = self.fonte_pequena.render(f"S{i+1}", True, (255, 255, 255))
                texto_spawn_rect = texto_spawn.get_rect(center=(int(screen_x), int(screen_y)))
                fundo_spawn = pygame.Surface((texto_spawn_rect.width + 4, texto_spawn_rect.height + 2), pygame.SRCALPHA)
                fundo_spawn.fill((0, 0, 0, 200))
                self.screen.blit(fundo_spawn, (texto_spawn_rect.x - 2, texto_spawn_rect.y - 1))
                self.screen.blit(texto_spawn, texto_spawn_rect)
        
        if self.huds_visiveis:
            self.desenhar_interface()

        self.desenhar_rotulo_mapa_topo()
        pygame.display.flip()
    
    def desenhar_interface(self):
        """Desenha a interface do editor"""
        altura_total = 390 if (self.huds_visiveis and self.mostrar_ajuda) else 200
        interface_rect = pygame.Rect(10, 10, 400, altura_total)
        pygame.draw.rect(self.screen, (0, 0, 0, 200), interface_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), interface_rect, 2)
        
        y_offset = 20
        
        titulo = self.fonte.render("CHECKPOINT EDITOR", True, (255, 255, 255))
        self.screen.blit(titulo, (20, y_offset))
        y_offset += 30
        
        mapa_texto = self.fonte_pequena.render(f"Pista GRIP: {self.numero_pista}", True, (200, 200, 200))
        self.screen.blit(mapa_texto, (20, y_offset))
        y_offset += 25
        
        if self.modo_spawn:
            modo_cor = (0, 255, 0)
            modo_texto = self.fonte_pequena.render("Modo SPAWN: ATIVO", True, modo_cor)
        elif self.modo_edicao:
            modo_cor = (0, 255, 0)
            modo_texto = self.fonte_pequena.render("Modo CHECKPOINT: ATIVO", True, modo_cor)
        else:
            modo_cor = (255, 0, 0)
            modo_texto = self.fonte_pequena.render("Modo Edição: INATIVO", True, modo_cor)
        self.screen.blit(modo_texto, (20, y_offset))
        y_offset += 25
        
        contador_texto = self.fonte_pequena.render(f"Checkpoints: {len(self.checkpoints)}", True, (200, 200, 200))
        self.screen.blit(contador_texto, (20, y_offset))
        y_offset += 25
        
        spawn_texto = self.fonte_pequena.render(f"Spawn Points: {len(self.spawn_points)}", True, (0, 255, 0) if self.spawn_points else (200, 200, 200))
        self.screen.blit(spawn_texto, (20, y_offset))
        y_offset += 25
        
        zoom_texto = self.fonte_pequena.render(f"Zoom: {self.camera.zoom:.1f}x", True, (200, 200, 200))
        self.screen.blit(zoom_texto, (20, y_offset))
        y_offset += 25
        
        controles = [
            "F7: Toggle Checkpoint | Shift+F7: Spawn",
            "F5: Salvar | F6: Carregar | F8: Limpar",
            "F9: Trocar Pista | F10: Exportar",
            "R: Rot 90° | Q/E: ±15° | H: Ajuda",
            "+/-: Zoom | 0: Reset | < >: Navegar"
        ]
        
        for controle in controles:
            controle_texto = self.fonte_pequena.render(controle, True, (150, 150, 150))
            self.screen.blit(controle_texto, (20, y_offset))
            y_offset += 20
        
        if self.huds_visiveis and self.mostrar_ajuda:
            y_offset += 5
            ajuda_textos = [
                "AJUDA:",
                "CHECKPOINTS: F7 | Clique: Add | Dir: Rem | Arrastar: Mover",
                "SPAWN: Shift+F7 | Clique: Add | Dir: Rem | Arrastar: Mover",
                "CÂMERA: Arrastar (sem edição) | Scroll: Zoom"
            ]
            
            for texto in ajuda_textos:
                ajuda_texto = self.fonte_pequena.render(texto, True, (200, 200, 200))
                self.screen.blit(ajuda_texto, (20, y_offset))
                y_offset += 18
    
    def executar(self):
        """Loop principal do editor"""
        print("=== CHECKPOINT EDITOR - TURBO RACER (GRIP) ===")
        print("Pressione F7 para ativar o modo de edição")
        print("Pressione +/- para zoom, 0 para resetar zoom")
        print("Use scroll do mouse para zoom")
        print("Pressione < > ou , . para navegar entre pistas GRIP (1-9)")
        print("Pressione F10 para exportar checkpoints para laps_grip.py")
        print("Pressione H para mostrar/ocultar ajuda")
        print("Pressione ESC para sair")
        
        rodando = True
        while rodando:
            dt = self.clock.tick(FPS) / 1000.0
            rodando = self.processar_eventos()
            self.desenhar()
        
        if self.checkpoints:
            self.salvar_checkpoints()
            print("Checkpoints salvos automaticamente!")
        
        pygame.quit()
        print("Editor fechado!")

    def desenhar_rotulo_mapa_topo(self):
        """Desenha o rótulo 'Pista GRIP X' no topo central da tela."""
        numero = self._obter_numero_mapa(self.mapa_atual)
        rotulo = self.fonte.render(f"Pista GRIP {numero}", True, (255, 255, 255))
        rect = rotulo.get_rect(center=(self.largura_tela // 2, 18))
        fundo = pygame.Surface((rect.width + 12, rect.height + 6), pygame.SRCALPHA)
        fundo.fill((0, 0, 0, 120))
        fundo_rect = fundo.get_rect(center=rect.center)
        self.screen.blit(fundo, fundo_rect)
        self.screen.blit(rotulo, rect)

    def _obter_numero_mapa(self, nome_mapa):
        """Retorna o número da pista GRIP atual."""
        return self.numero_pista

def main():
    """Função principal"""
    try:
        editor = CheckpointEditor()
        editor.executar()
    except KeyboardInterrupt:
        print("\nEditor interrompido pelo usuário!")
    except Exception as e:
        print(f"Erro no editor: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
