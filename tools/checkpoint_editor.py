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

# Adicionar o diretório src ao path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import LARGURA, ALTURA, FPS, MAPAS_DISPONIVEIS
from core.camera import Camera
from core.pista_tiles import PistaTiles
from core.laps_grip import carregar_checkpoints_grip

class CheckpointEditor:
    def __init__(self):
        pygame.init()
        
        # Configurações da tela
        self.screen = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Checkpoint Editor - Turbo Racer")
        
        # Clock para FPS
        self.clock = pygame.time.Clock()
        
        # Estado do editor
        self.modo_edicao = False
        self.checkpoints = []  # Formato: [x, y, angulo] ou [x, y] (angulo padrão 0)
        self.checkpoint_selecionado = -1
        self.checkpoint_em_arraste = -1
        self.arrastando_camera = False
        
        # Sistema de spawn points (posições onde os carros vão nascer)
        self.spawn_points = []  # Formato: [x, y] - posições de spawn dos carros
        self.spawn_selecionado = -1
        self.spawn_em_arraste = -1
        self.modo_spawn = False  # Modo para editar spawn points (Shift+F7)
        
        # Sistema de pistas GRIP
        self.usar_tiles_grip = True  # Sempre usar tiles do GRIP
        self.numero_pista = 1  # Pista do GRIP (1-9)
        self.pista_tiles = None
        self.surface_pista_completa = None  # Superfície completa do mapa (5000x5000)
        self.largura_pista = 5000
        self.altura_pista = 5000
        
        # Navegação entre mapas (pistas GRIP 1-9)
        self.mapas_disponiveis = list(range(1, 10))  # Pistas 1-9 do GRIP
        self.indice_mapa_atual = 0
        
        # Mapa atual
        self.mapa_atual = f"Pista_{self.numero_pista}"
        self.img_pista = None
        self.mask_pista = None
        self.mask_guias = None
        
        # Câmera (com zoom controlável) - ajustada para mapa grande
        # Zoom inicial calculado para mostrar o mapa inteiro na tela
        zoom_para_ver_tudo = min(LARGURA / self.largura_pista, ALTURA / self.altura_pista) * 0.9
        self.zoom_min = 0.3  # Zoom mínimo travado em 0.3x
        self.zoom_max = 2.0  # Zoom máximo para detalhes
        # Garantir que o zoom inicial respeite o mínimo
        zoom_inicial = max(self.zoom_min, zoom_para_ver_tudo)
        self.camera = Camera(LARGURA, ALTURA, self.largura_pista, self.altura_pista, zoom=zoom_inicial)
        # Centralizar câmera no centro do mapa
        self.camera.cx = self.largura_pista // 2
        self.camera.cy = self.altura_pista // 2
        
        # Fonte
        self.fonte = pygame.font.Font(None, 24)
        self.fonte_pequena = pygame.font.Font(None, 18)
        
        # Carregar mapa inicial
        self.carregar_mapa()
        self.carregar_checkpoints()
        
        # Estado da interface
        self.mostrar_ajuda = True
        self.huds_visiveis = True  # controla painel principal e ajuda
        self.ultimo_clique_tempo = 0
        self.debounce_tempo = 200  # ms

    def set_zoom(self, novo_zoom):
        """Define o zoom com clamp e quantização para evitar drift por arredondamento."""
        # Clamp
        clamped = max(self.zoom_min, min(self.zoom_max, float(novo_zoom)))
        # Quantizar para 1 casa (evita acumular floats como 0.30000000004)
        quantizado = round(clamped, 1)
        # Se não houver mudança, não faz nada
        if abs(quantizado - self.camera.zoom) < 1e-6:
            return False
        self.camera.zoom = quantizado
        return True
        
    def carregar_mapa(self):
        """Carrega o mapa atual usando sistema de tiles do GRIP"""
        try:
            # Usar sistema de tiles do GRIP
            self.pista_tiles = PistaTiles(largura=self.largura_pista, altura=self.altura_pista)
            self.surface_pista_completa = self.pista_tiles.construir_pista(self.numero_pista)
            
            # Criar imagens compatíveis para o sistema antigo (não usadas, mas mantidas para compatibilidade)
            self.img_pista = self.surface_pista_completa.copy()
            self.mask_pista = self.surface_pista_completa.copy()
            self.mask_guias = pygame.Surface((self.largura_pista, self.altura_pista), pygame.SRCALPHA)
            
            # Atualizar câmera para o tamanho correto do mapa
            self.camera.largura_pista = self.largura_pista
            self.camera.altura_pista = self.altura_pista
            # Centralizar câmera
            self.camera.cx = self.largura_pista // 2
            self.camera.cy = self.altura_pista // 2
            
            print(f"Pista GRIP {self.numero_pista} carregada: {self.largura_pista}x{self.altura_pista}")
            
            # Carregar checkpoints do GRIP
            self.carregar_checkpoints()
        except Exception as e:
            print(f"Erro ao carregar pista GRIP: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: criar superfície vazia
            self.surface_pista_completa = pygame.Surface((self.largura_pista, self.altura_pista))
            self.surface_pista_completa.fill((0, 200, 0))  # Verde = grama
            self.img_pista = self.surface_pista_completa.copy()
            self.mask_pista = self.img_pista.copy()
            self.mask_guias = pygame.Surface((self.largura_pista, self.altura_pista), pygame.SRCALPHA)
            # Carregar checkpoints mesmo com erro
            self.carregar_checkpoints()
    
    def obter_caminho_checkpoints_pista(self):
        """Retorna o caminho do arquivo JSON de checkpoints para a pista atual"""
        diretorio = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(diretorio, exist_ok=True)
        return os.path.join(diretorio, f"checkpoints_pista_{self.numero_pista}.json")
    
    def carregar_checkpoints(self):
        """Carrega checkpoints e spawn points do arquivo JSON (prioridade) ou do GRIP (fallback)"""
        try:
            # Primeiro, tentar carregar do arquivo JSON específico da pista
            arquivo = self.obter_caminho_checkpoints_pista()
            if os.path.exists(arquivo):
                with open(arquivo, 'r', encoding='utf-8') as f:
                    dados_carregados = json.load(f)
                
                # Verificar se é formato novo (com spawn_points) ou antigo (só checkpoints)
                if isinstance(dados_carregados, dict):
                    # Formato novo: {"checkpoints": [...], "spawn_points": [...]}
                    checkpoints_carregados = dados_carregados.get("checkpoints", [])
                    self.spawn_points = dados_carregados.get("spawn_points", [])
                else:
                    # Formato antigo: apenas lista de checkpoints
                    checkpoints_carregados = dados_carregados
                    self.spawn_points = []
                
                # Garantir que todos os checkpoints tenham ângulo (compatibilidade com versões antigas)
                self.checkpoints = []
                for cp in checkpoints_carregados:
                    if len(cp) == 2:
                        # Formato antigo [x, y] - adicionar ângulo 0
                        self.checkpoints.append([float(cp[0]), float(cp[1]), 0])
                    elif len(cp) == 3:
                        # Formato novo [x, y, angulo]
                        self.checkpoints.append([float(cp[0]), float(cp[1]), float(cp[2])])
                
                # Garantir que spawn_points sejam listas de [x, y]
                if self.spawn_points:
                    self.spawn_points = [[float(sp[0]), float(sp[1])] for sp in self.spawn_points if len(sp) >= 2]
                
                print(f"Carregados {len(self.checkpoints)} checkpoints do JSON para pista {self.numero_pista}")
                print(f"Carregados {len(self.spawn_points)} spawn points do JSON para pista {self.numero_pista}")
                return
            
            # Fallback: tentar carregar checkpoints do GRIP (fonte principal)
            checkpoints_grip = carregar_checkpoints_grip(self.numero_pista)
            if checkpoints_grip:
                # Converter tuplas para listas (formato JSON) - adicionar ângulo padrão 0
                self.checkpoints = []
                for cp in checkpoints_grip:
                    if len(cp) >= 3:
                        self.checkpoints.append([float(cp[0]), float(cp[1]), float(cp[2])])
                    else:
                        self.checkpoints.append([float(cp[0]), float(cp[1]), 0])
                # Spawn points do GRIP (se existirem) - tentar carregar do JSON da pista
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
                print(f"Carregados {len(self.checkpoints)} checkpoints do GRIP (laps_grip.py) para pista {self.numero_pista}")
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

        # Salvar automaticamente antes de trocar
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
        # carregar_mapa() já invoca carregar_checkpoints()
        print(f"Pista alterada para: GRIP Pista {self.numero_pista}")
        return True
    
    def salvar_checkpoints(self):
        """Salva checkpoints e spawn points no arquivo JSON específico da pista"""
        try:
            # Salvar em arquivo JSON específico da pista
            arquivo = self.obter_caminho_checkpoints_pista()
            os.makedirs(os.path.dirname(arquivo), exist_ok=True)
            
            # Salvar em formato: {"checkpoints": [...], "spawn_points": [...]}
            dados_para_salvar = {
                "checkpoints": self.checkpoints,
                "spawn_points": self.spawn_points,
                "numero_pista": self.numero_pista
            }
            
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_para_salvar, f, indent=2)
            
            print(f"Checkpoints salvos em JSON para pista {self.numero_pista}: {len(self.checkpoints)} checkpoints, {len(self.spawn_points)} spawn points")
            print(f"Arquivo: {arquivo}")
            print(f"NOTA: O jogo usa checkpoints de src/core/laps_grip.py, não do JSON.")
            print(f"Use F10 para exportar para laps_grip.py ou copie manualmente as coordenadas abaixo.\n")
            
            # Mostrar coordenadas para copiar para laps_grip.py
            print(f"=== COORDENADAS PARA PISTA {self.numero_pista} ===")
            print(f"Copie e cole no arquivo src/core/laps_grip.py:")
            print(f"    if numero_pista == {self.numero_pista}:")
            centro_x, centro_y = 2500, 2500
            for i, cp in enumerate(self.checkpoints):
                x, y = cp[0], cp[1]
                angulo = cp[2] if len(cp) > 2 else 0
                offset_x = x - centro_x
                offset_y = y - centro_y
                print(f"        checkpoint_{i+1} = (centro_x + {offset_x:.0f}, centro_y + {offset_y:.0f}, {angulo:.0f})  # Ângulo: {angulo:.0f}°")
            print(f"        checkpoints = [")
            for i in range(len(self.checkpoints)):
                print(f"            tuple(checkpoint_{i+1}),")
            print(f"        ]")
            print(f"==========================================\n")
            
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
            
            # Ler arquivo atual
            with open(caminho_laps_grip, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
            
            # Encontrar o bloco da pista atual
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
                # Se não encontrou fim, procurar pelo próximo if/elif ou final da função
                for i in range(inicio_bloco + 1, len(linhas)):
                    linha_stripped = linhas[i].strip()
                    if linha_stripped.startswith('elif numero_pista ==') or linha_stripped.startswith('else:'):
                        fim_bloco = i
                        break
                if fim_bloco is None:
                    fim_bloco = len(linhas) - 1
            
            # Gerar novo código para os checkpoints
            centro_x, centro_y = 2500, 2500
            novo_codigo = []
            novo_codigo.append(f"    if numero_pista == {self.numero_pista}:\n")
            
            # Adicionar checkpoints individuais (com ângulo)
            for i, cp in enumerate(self.checkpoints):
                x, y = cp[0], cp[1]
                angulo = cp[2] if len(cp) > 2 else 0
                offset_x = x - centro_x
                offset_y = y - centro_y
                # Incluir ângulo no checkpoint: (x, y, angulo)
                novo_codigo.append(f"        checkpoint_{i+1} = (centro_x + {offset_x:.0f}, centro_y + {offset_y:.0f}, {angulo:.0f})  # Ângulo: {angulo:.0f}°\n")
            
            # Adicionar lista de checkpoints
            novo_codigo.append("        # Checkpoints com ângulo: (x, y, angulo) ou (x, y) para cálculo automático\n")
            novo_codigo.append("        checkpoints = [\n")
            for i in range(len(self.checkpoints)):
                novo_codigo.append(f"            tuple(checkpoint_{i+1}),\n")
            novo_codigo.append("        ]\n")
            
            # Substituir o bloco
            novas_linhas = linhas[:inicio_bloco] + novo_codigo + linhas[fim_bloco:]
            
            # Salvar arquivo
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
            # Salvar checkpoints e spawn points atuais da pista anterior
            if self.checkpoints or self.spawn_points:
                self.salvar_checkpoints()
                print(f"Dados da pista {self.numero_pista} salvos antes de trocar")

            # Trocar para nova pista
            self.numero_pista = numero_pista
            self.indice_mapa_atual = numero_pista - 1
            self.mapa_atual = f"Pista_{numero_pista}"
            self.checkpoint_selecionado = -1
            self.checkpoint_em_arraste = -1
            self.spawn_selecionado = -1
            self.spawn_em_arraste = -1
            
            # Carregar mapa e checkpoints da nova pista
            self.carregar_mapa()
            # carregar_mapa() já invoca carregar_checkpoints()
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
        
        # Encontrar checkpoint mais próximo
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
            # Garantir que tem ângulo
            if len(cp) == 2:
                cp.append(0)
            # Rotacionar
            cp[2] = (cp[2] + incremento) % 360
            print(f"Checkpoint {indice + 1} rotacionado para {cp[2]:.0f}°")
    
    def mover_checkpoint(self, indice, novo_x, novo_y):
        """Move um checkpoint para uma nova posição"""
        if 0 <= indice < len(self.checkpoints):
            cp = self.checkpoints[indice]
            # Preservar ângulo se existir
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
        
        # Encontrar spawn point mais próximo
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
        
        # Ajustar raio baseado no zoom
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
    
    # Removidas funções alternativas de conversão; usaremos sempre as da câmera

    def desenhar(self):
        """Desenha a interface do editor"""
        # Limpar tela
        self.screen.fill((0, 0, 0))
        
        # Desenhar fundo da pista completa
        if self.surface_pista_completa:
            self.camera.desenhar_fundo(self.screen, self.surface_pista_completa)
        else:
            self.camera.desenhar_fundo(self.screen, self.img_pista)
        
        # Desenhar checkpoints
        if self.checkpoints:
            # Desenhar linhas que ligam os checkpoints
            for i in range(len(self.checkpoints)):
                if i < len(self.checkpoints) - 1:
                    # Linha para o próximo checkpoint (sem fechar o loop)
                    cp1 = self.checkpoints[i]
                    cp2 = self.checkpoints[i + 1]
                    x1, y1 = cp1[0], cp1[1]
                    x2, y2 = cp2[0], cp2[1]
                    
                    # Verificar se pelo menos um dos checkpoints está visível
                    if not (self.camera.esta_visivel(x1, y1, margem=50) or 
                           self.camera.esta_visivel(x2, y2, margem=50)):
                        continue
                        
                    screen_x1, screen_y1 = self.camera.mundo_para_tela(x1, y1)
                    screen_x2, screen_y2 = self.camera.mundo_para_tela(x2, y2)
                    
                    # Verificar se as coordenadas da tela são válidas
                    if not ((0 <= screen_x1 <= LARGURA and 0 <= screen_y1 <= ALTURA) or
                           (0 <= screen_x2 <= LARGURA and 0 <= screen_y2 <= ALTURA)):
                        continue
                    
                    # Cor da linha baseada na seleção
                    if i == self.checkpoint_selecionado or i + 1 == self.checkpoint_selecionado:
                        cor_linha = (255, 255, 0)  # Amarelo para selecionado
                    else:
                        cor_linha = (0, 200, 255)  # Azul para normal
                    
                    # Espessura da linha fixa (não escala com zoom)
                    espessura_linha = 3
                    pygame.draw.line(self.screen, cor_linha, 
                                   (int(screen_x1), int(screen_y1)), 
                                   (int(screen_x2), int(screen_y2)), espessura_linha)
            
            # Desenhar retângulos dos checkpoints (como no GRIP)
            for i, cp in enumerate(self.checkpoints):
                x, y = cp[0], cp[1]
                # Obter ângulo (padrão 0 se não existir)
                angulo = cp[2] if len(cp) > 2 else 0
                
                CHECKPOINT_LARGURA = 300  # Largura dos tiles de pista
                CHECKPOINT_ESPESSURA = 1
                
                # Criar retângulo base (horizontal por padrão)
                rect_base = pygame.Rect(
                    -CHECKPOINT_LARGURA // 2,
                    -CHECKPOINT_ESPESSURA // 2,
                    CHECKPOINT_LARGURA,
                    CHECKPOINT_ESPESSURA
                )
                
                # Criar superfície para o retângulo
                superficie_rect = pygame.Surface((CHECKPOINT_LARGURA, CHECKPOINT_ESPESSURA), pygame.SRCALPHA)
                
                # Cor baseada na seleção
                if i == self.checkpoint_selecionado:
                    cor = (255, 255, 0, 150)  # Amarelo transparente para selecionado
                    cor_borda = (255, 255, 0)  # Amarelo sólido para borda
                else:
                    cor = (0, 255, 255, 100)  # Ciano transparente para normal
                    cor_borda = (0, 255, 255)  # Ciano sólido para borda
                
                # Preencher retângulo
                superficie_rect.fill(cor)
                pygame.draw.rect(superficie_rect, cor_borda, rect_base, 3)
                
                # Rotacionar a superfície
                if angulo != 0:
                    superficie_rect = pygame.transform.rotate(superficie_rect, -angulo)
                
                # Converter posição do mundo para tela
                screen_x, screen_y = self.camera.mundo_para_tela(x, y)
                
                # Calcular posição para centralizar o retângulo rotacionado
                rect_rotacionado = superficie_rect.get_rect(center=(int(screen_x), int(screen_y)))
                
                # Verificar se está visível
                if not (rect_rotacionado.colliderect(pygame.Rect(0, 0, LARGURA, ALTURA))):
                    continue
                
                # Desenhar retângulo rotacionado
                self.screen.blit(superficie_rect, rect_rotacionado)
                
                # Número do checkpoint no centro
                texto = self.fonte.render(str(i + 1), True, (255, 255, 255))
                texto_rect = texto.get_rect(center=(int(screen_x), int(screen_y)))
                
                # Fundo semi-transparente para o texto
                fundo_texto = pygame.Surface((texto_rect.width + 8, texto_rect.height + 4), pygame.SRCALPHA)
                fundo_texto.fill((0, 0, 0, 200))
                self.screen.blit(fundo_texto, (texto_rect.x - 4, texto_rect.y - 2))
                self.screen.blit(texto, texto_rect)
                
                # Mostrar ângulo se selecionado
                if i == self.checkpoint_selecionado and angulo != 0:
                    texto_angulo = self.fonte_pequena.render(f"{angulo:.0f}°", True, (255, 255, 0))
                    texto_angulo_rect = texto_angulo.get_rect(center=(int(screen_x), int(screen_y) + 25))
                    fundo_angulo = pygame.Surface((texto_angulo_rect.width + 8, texto_angulo_rect.height + 4), pygame.SRCALPHA)
                    fundo_angulo.fill((0, 0, 0, 200))
                    self.screen.blit(fundo_angulo, (texto_angulo_rect.x - 4, texto_angulo_rect.y - 2))
                    self.screen.blit(texto_angulo, texto_angulo_rect)
        
        # Desenhar spawn points (em verde para diferenciar)
        if self.spawn_points:
            for i, sp in enumerate(self.spawn_points):
                x, y = sp[0], sp[1]
                
                # Converter posição do mundo para tela
                screen_x, screen_y = self.camera.mundo_para_tela(x, y)
                
                # Verificar se está visível
                if not (0 <= screen_x <= LARGURA and 0 <= screen_y <= ALTURA):
                    continue
                
                # Desenhar círculo para spawn point (verde)
                raio = 15
                if i == self.spawn_selecionado:
                    cor_spawn = (0, 255, 0)  # Verde brilhante para selecionado
                    pygame.draw.circle(self.screen, cor_spawn, (int(screen_x), int(screen_y)), raio + 3, 3)
                else:
                    cor_spawn = (0, 200, 0)  # Verde para normal
                
                pygame.draw.circle(self.screen, cor_spawn, (int(screen_x), int(screen_y)), raio)
                pygame.draw.circle(self.screen, (255, 255, 255), (int(screen_x), int(screen_y)), raio, 2)
                
                # Número do spawn point
                texto_spawn = self.fonte_pequena.render(f"S{i+1}", True, (255, 255, 255))
                texto_spawn_rect = texto_spawn.get_rect(center=(int(screen_x), int(screen_y)))
                fundo_spawn = pygame.Surface((texto_spawn_rect.width + 4, texto_spawn_rect.height + 2), pygame.SRCALPHA)
                fundo_spawn.fill((0, 0, 0, 200))
                self.screen.blit(fundo_spawn, (texto_spawn_rect.x - 2, texto_spawn_rect.y - 1))
                self.screen.blit(texto_spawn, texto_spawn_rect)
        
        # Desenhar interface
        if self.huds_visiveis:
            self.desenhar_interface()

        # Rótulo de pista no topo central
        self.desenhar_rotulo_mapa_topo()
        
        # Atualizar tela
        pygame.display.flip()
    
    def desenhar_interface(self):
        """Desenha a interface do editor"""
        # Fundo semi-transparente para interface (mais alto)
        interface_rect = pygame.Rect(10, 10, 400, 250)
        pygame.draw.rect(self.screen, (0, 0, 0, 150), interface_rect)
        pygame.draw.rect(self.screen, (255, 255, 255, 50), interface_rect, 2)
        
        y_offset = 20
        
        # Título
        titulo = self.fonte.render("CHECKPOINT EDITOR", True, (255, 255, 255))
        self.screen.blit(titulo, (20, y_offset))
        y_offset += 30
        
        # Pista atual
        mapa_texto = self.fonte_pequena.render(f"Pista GRIP: {self.numero_pista}", True, (200, 200, 200))
        self.screen.blit(mapa_texto, (20, y_offset))
        y_offset += 25
        
        # Modo de edição
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
        
        # Contadores
        contador_texto = self.fonte_pequena.render(f"Checkpoints: {len(self.checkpoints)}", True, (200, 200, 200))
        self.screen.blit(contador_texto, (20, y_offset))
        y_offset += 25
        
        # Contador de spawn points
        spawn_texto = self.fonte_pequena.render(f"Spawn Points: {len(self.spawn_points)}", True, (0, 255, 0) if self.spawn_points else (200, 200, 200))
        self.screen.blit(spawn_texto, (20, y_offset))
        y_offset += 25
        
        # Zoom atual
        zoom_texto = self.fonte_pequena.render(f"Zoom: {self.camera.zoom:.1f}x", True, (200, 200, 200))
        self.screen.blit(zoom_texto, (20, y_offset))
        y_offset += 25
        
        # Controles
        controles = [
            "F7: Toggle Checkpoint | Shift+F7: Toggle Spawn",
            "F5: Salvar JSON (backup) | F6: Carregar | F8: Limpar",
            "Shift+F8: Limpar Spawn | F9: Trocar Pista | F10: Exportar",
            "R: Rotacionar 90° | Q/E: Rotacionar ±15°",
            "H: Toggle Ajuda | +/-: Zoom | 0: Reset",
            "< >: Navegar Pistas | ESC: Sair"
        ]
        
        for controle in controles:
            controle_texto = self.fonte_pequena.render(controle, True, (150, 150, 150))
            self.screen.blit(controle_texto, (20, y_offset))
            y_offset += 20
        
        # Removido: botões de navegação e linha "< Mapa: ... >" na interface inferior
        
        # Ajuda detalhada
        if self.huds_visiveis and self.mostrar_ajuda:
            ajuda_rect = pygame.Rect(10, 270, 400, 120)
            pygame.draw.rect(self.screen, (0, 0, 0, 150), ajuda_rect)
            pygame.draw.rect(self.screen, (255, 255, 255, 50), ajuda_rect, 2)
            
            ajuda_textos = [
                "AJUDA:",
                "CHECKPOINTS:",
                "• F7: Ativar modo checkpoint",
                "• Clique: Adicionar | Direito: Remover",
                "• Arrastar: Mover | R/Q/E: Rotacionar",
                "",
                "SPAWN POINTS:",
                "• Shift+F7: Ativar modo spawn",
                "• Clique: Adicionar | Direito: Remover",
                "• Arrastar: Mover | Scroll: Zoom",
                "• Arrastar (sem edição): Mover câmera"
            ]
            
            y_ajuda = 280
            for texto in ajuda_textos:
                ajuda_texto = self.fonte_pequena.render(texto, True, (200, 200, 200))
                self.screen.blit(ajuda_texto, (20, y_ajuda))
                y_ajuda += 18
    
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
            
            # Processar eventos
            rodando = self.processar_eventos()
            
            # Desenhar
            self.desenhar()
        
        # Salvar antes de sair
        if self.checkpoints:
            self.salvar_checkpoints()
            print("Checkpoints salvos automaticamente!")
        
        pygame.quit()
        print("Editor fechado!")

    def desenhar_rotulo_mapa_topo(self):
        """Desenha o rótulo 'Pista GRIP X' no topo central da tela."""
        numero = self._obter_numero_mapa(self.mapa_atual)
        rotulo = self.fonte.render(f"Pista GRIP {numero}", True, (255, 255, 255))
        rect = rotulo.get_rect(center=(LARGURA // 2, 18))
        # Fundo discreto para legibilidade
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
