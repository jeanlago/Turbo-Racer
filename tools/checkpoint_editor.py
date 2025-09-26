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

from config import LARGURA, ALTURA, FPS, MAPAS_DISPONIVEIS, obter_caminho_checkpoints
from core.pista import carregar_pista
from core.camera import Camera

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
        self.checkpoints = []
        self.checkpoint_selecionado = -1
        self.checkpoint_em_arraste = -1
        self.arrastando_camera = False
        
        # Navegação entre mapas
        self.mapas_disponiveis = self.obter_mapas_disponiveis()
        self.indice_mapa_atual = 0
        
        # Mapa atual - usar o primeiro mapa disponível
        if self.mapas_disponiveis:
            self.mapa_atual = self.mapas_disponiveis[0]
        else:
            self.mapa_atual = "Mapa_1"
        self.img_pista = None
        self.mask_pista = None
        self.mask_guias = None
        
        # Câmera (com zoom controlável)
        self.camera = Camera(LARGURA, ALTURA, LARGURA, ALTURA, zoom=1.0)
        self.zoom_min = 1.0
        self.zoom_max = 3.0
        
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
        """Carrega o mapa atual"""
        try:
            # Configurar o mapa atual no config antes de carregar
            import config
            config.MAPA_ATUAL = self.mapa_atual
            config.atualizar_caminhos_mapa()
            
            self.img_pista, self.mask_pista, self.mask_guias = carregar_pista()
            
            # Garantir que a imagem está na resolução correta
            if self.img_pista.get_width() != LARGURA or self.img_pista.get_height() != ALTURA:
                self.img_pista = pygame.transform.smoothscale(self.img_pista, (LARGURA, ALTURA))
                self.mask_pista = pygame.transform.smoothscale(self.mask_pista, (LARGURA, ALTURA))
                self.mask_guias = pygame.transform.smoothscale(self.mask_guias, (LARGURA, ALTURA))
            
            print(f"Mapa carregado: {self.mapa_atual}")
            
            # Carregar checkpoints do mapa
            self.carregar_checkpoints()
        except Exception as e:
            print(f"Erro ao carregar mapa: {e}")
            self.img_pista = pygame.Surface((LARGURA, ALTURA))
            self.img_pista.fill((50, 50, 50))
            self.mask_pista = self.img_pista.copy()
            self.mask_guias = self.img_pista.copy()
            # Carregar checkpoints mesmo com erro no mapa
            self.carregar_checkpoints()
    
    def carregar_checkpoints(self):
        """Carrega checkpoints do arquivo"""
        try:
            # Tentar carregar do arquivo específico do mapa
            arquivo = obter_caminho_checkpoints()
            if os.path.exists(arquivo):
                with open(arquivo, 'r', encoding='utf-8') as f:
                    self.checkpoints = json.load(f)
                print(f"Carregados {len(self.checkpoints)} checkpoints de {arquivo}")
            else:
                # Não carregar checkpoints de outros mapas - deixar vazio
                self.checkpoints = []
                print(f"Nenhum arquivo de checkpoints encontrado para {self.mapa_atual}")
        except Exception as e:
            print(f"Erro ao carregar checkpoints: {e}")
            self.checkpoints = []
    
    def obter_mapas_disponiveis(self):
        """Obtém lista de mapas disponíveis"""
        mapas = []
        maps_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'maps')
        
        if os.path.exists(maps_dir):
            for arquivo in os.listdir(maps_dir):
                if arquivo.startswith('Mapa_') and arquivo.endswith('.png'):
                    nome_mapa = arquivo.replace('.png', '')
                    mapas.append(nome_mapa)
        
        return sorted(mapas)
    
    def trocar_mapa_direcional(self, direcao):
        """Troca para o mapa anterior ou próximo (navegação local do editor)."""
        if len(self.mapas_disponiveis) <= 1:
            return False

        # Salvar automaticamente antes de trocar
        if self.checkpoints:
            self.salvar_checkpoints()

        if direcao == "anterior":
            self.indice_mapa_atual = (self.indice_mapa_atual - 1) % len(self.mapas_disponiveis)
        else:  # "proximo"
            self.indice_mapa_atual = (self.indice_mapa_atual + 1) % len(self.mapas_disponiveis)

        self.mapa_atual = self.mapas_disponiveis[self.indice_mapa_atual]
        self.checkpoint_selecionado = -1
        self.checkpoint_em_arraste = -1
        self.carregar_mapa()
        # carregar_mapa() já invoca carregar_checkpoints()
        print(f"Mapa alterado para: {self.mapa_atual}")
        return True
    
    def salvar_checkpoints(self):
        """Salva checkpoints no arquivo"""
        try:
            arquivo = obter_caminho_checkpoints()
            os.makedirs(os.path.dirname(arquivo), exist_ok=True)
            
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(self.checkpoints, f, indent=2)
            print(f"Checkpoints salvos: {len(self.checkpoints)} pontos")
            return True
        except Exception as e:
            print(f"Erro ao salvar checkpoints: {e}")
            return False
    
    def trocar_mapa_por_id(self, novo_mapa):
        """Troca para um novo mapa usando o id presente em MAPAS_DISPONIVEIS (config)."""
        if novo_mapa in MAPAS_DISPONIVEIS:
            # Salvar checkpoints atuais
            if self.checkpoints:
                self.salvar_checkpoints()

            self.mapa_atual = novo_mapa
            self.checkpoint_selecionado = -1
            self.checkpoint_em_arraste = -1
            self.carregar_mapa()
            # carregar_mapa() já invoca carregar_checkpoints()
            print(f"Trocado para mapa: {MAPAS_DISPONIVEIS[novo_mapa]['nome']}")
            return True
        return False
    
    def adicionar_checkpoint(self, x, y):
        """Adiciona um checkpoint na posição especificada"""
        if not self.modo_edicao:
            return
        
        mundo_x, mundo_y = self.camera.tela_para_mundo(x, y)
        self.checkpoints.append([int(mundo_x), int(mundo_y)])
        print(f"Checkpoint adicionado: ({mundo_x:.0f}, {mundo_y:.0f})")
    
    def remover_checkpoint(self, x, y):
        """Remove o checkpoint mais próximo da posição especificada"""
        if not self.modo_edicao or not self.checkpoints:
            return
        
        mundo_x, mundo_y = self.camera.tela_para_mundo(x, y)
        
        # Encontrar checkpoint mais próximo
        melhor_indice = -1
        menor_distancia = float('inf')
        
        for i, (cx, cy) in enumerate(self.checkpoints):
            distancia = ((mundo_x - cx) ** 2 + (mundo_y - cy) ** 2) ** 0.5
            if distancia < menor_distancia:
                menor_distancia = distancia
                melhor_indice = i
        
        if melhor_indice >= 0 and menor_distancia < 30:  # 30 pixels de tolerância
            checkpoint_removido = self.checkpoints.pop(melhor_indice)
            print(f"Checkpoint removido: {checkpoint_removido}")
    
    def mover_checkpoint(self, indice, novo_x, novo_y):
        """Move um checkpoint para uma nova posição"""
        if 0 <= indice < len(self.checkpoints):
            self.checkpoints[indice] = [int(novo_x), int(novo_y)]
    
    def encontrar_checkpoint_proximo(self, x, y, raio_base=30):
        """Encontra o checkpoint mais próximo da posição especificada com raio baseado n-o zoom."""
        mundo_x, mundo_y = self.camera.tela_para_mundo(x, y)
        
        # Ajustar raio baseado no zoom
        raio = max(15, int(raio_base * self.camera.zoom))
        
        melhor_indice = -1
        menor_distancia = float('inf')
        
        for i, (cx, cy) in enumerate(self.checkpoints):
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
                    self.modo_edicao = not self.modo_edicao
                    print(f"Modo de edição: {'ATIVADO' if self.modo_edicao else 'DESATIVADO'}")
                elif event.key == pygame.K_F5:
                    if self.salvar_checkpoints():
                        print("Checkpoints salvos com sucesso!")
                elif event.key == pygame.K_F6:
                    self.carregar_checkpoints()
                    print("Checkpoints recarregados!")
                elif event.key == pygame.K_F8:
                    self.checkpoints = []
                    print("Todos os checkpoints removidos!")
                elif event.key == pygame.K_F9:
                    self.mostrar_selecao_mapa()
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
                    if self.modo_edicao:
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
                    if self.modo_edicao:
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
                    if self.checkpoint_em_arraste >= 0:
                        self.checkpoint_em_arraste = -1
                        print("Checkpoint solto")
                    elif self.arrastando_camera:
                        self.arrastando_camera = False
                        print("Câmera solta")
            
            elif event.type == pygame.MOUSEMOTION:
                if self.modo_edicao and self.checkpoint_em_arraste >= 0:
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
        
        # Desenhar fundo da pista
        self.camera.desenhar_fundo(self.screen, self.img_pista)
        
        # Desenhar checkpoints
        if self.checkpoints:
            # Desenhar linhas que ligam os checkpoints
            for i in range(len(self.checkpoints)):
                if i < len(self.checkpoints) - 1:
                    # Linha para o próximo checkpoint (sem fechar o loop)
                    x1, y1 = self.checkpoints[i]
                    x2, y2 = self.checkpoints[i + 1]
                    
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
            
            # Desenhar círculos dos checkpoints
            for i, (x, y) in enumerate(self.checkpoints):
                # Verificar se o checkpoint está visível na tela
                if not self.camera.esta_visivel(x, y, margem=50):
                    continue
                    
                screen_x, screen_y = self.camera.mundo_para_tela(x, y)
                
                # Verificar se as coordenadas da tela são válidas
                if not (0 <= screen_x <= LARGURA and 0 <= screen_y <= ALTURA):
                    continue
                
                # Cor baseada na seleção
                if i == self.checkpoint_selecionado:
                    cor = (255, 255, 0)  # Amarelo para selecionado
                else:
                    cor = (0, 255, 255)  # Ciano para normal
                
                # Desenhar círculo com tamanho fixo (não escala com zoom)
                pygame.draw.circle(self.screen, cor, (int(screen_x), int(screen_y)), 20, 4)
                pygame.draw.circle(self.screen, cor, (int(screen_x), int(screen_y)), 16)
                
                # Número do checkpoint com fonte fixa
                texto = self.fonte.render(str(i + 1), True, (255, 255, 255))
                texto_rect = texto.get_rect(center=(int(screen_x), int(screen_y)))
                self.screen.blit(texto, texto_rect)
        
        # Desenhar interface
        if self.huds_visiveis:
            self.desenhar_interface()

        # Rótulo de mapa no topo central
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
        
        # Mapa atual
        mapa_nome = MAPAS_DISPONIVEIS.get(self.mapa_atual, {}).get('nome', self.mapa_atual)
        mapa_texto = self.fonte_pequena.render(f"Mapa: {mapa_nome}", True, (200, 200, 200))
        self.screen.blit(mapa_texto, (20, y_offset))
        y_offset += 25
        
        # Modo de edição
        modo_cor = (0, 255, 0) if self.modo_edicao else (255, 0, 0)
        modo_texto = self.fonte_pequena.render(f"Modo Edição: {'ATIVO' if self.modo_edicao else 'INATIVO'}", True, modo_cor)
        self.screen.blit(modo_texto, (20, y_offset))
        y_offset += 25
        
        # Contadores
        contador_texto = self.fonte_pequena.render(f"Checkpoints: {len(self.checkpoints)}", True, (200, 200, 200))
        self.screen.blit(contador_texto, (20, y_offset))
        y_offset += 25
        
        # Zoom atual
        zoom_texto = self.fonte_pequena.render(f"Zoom: {self.camera.zoom:.1f}x", True, (200, 200, 200))
        self.screen.blit(zoom_texto, (20, y_offset))
        y_offset += 25
        
        # Controles
        controles = [
            "F7: Toggle Edição",
            "F5: Salvar | F6: Carregar | F8: Limpar",
            "F9: Trocar Mapa | H: Toggle Ajuda",
            "+/-: Zoom | 0: Reset Zoom | ESC: Sair",
            "< >: Navegar Mapas"
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
                "• Clique esquerdo: Adicionar checkpoint",
                "• Clique direito: Remover checkpoint",
                "• Arrastar: Mover checkpoint | Scroll: Zoom",
                "• Arrastar (sem edição): Mover câmera"
            ]
            
            y_ajuda = 280
            for texto in ajuda_textos:
                ajuda_texto = self.fonte_pequena.render(texto, True, (200, 200, 200))
                self.screen.blit(ajuda_texto, (20, y_ajuda))
                y_ajuda += 18
    
    def executar(self):
        """Loop principal do editor"""
        print("=== CHECKPOINT EDITOR - TURBO RACER ===")
        print("Pressione F7 para ativar o modo de edição")
        print("Pressione +/- para zoom, 0 para resetar zoom")
        print("Use scroll do mouse para zoom")
        print("Pressione < > ou , . para navegar entre mapas")
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
        """Desenha o rótulo 'Mapa X' no topo central da tela."""
        # Extrair número do nome do mapa; fallback para índice + 1
        numero = self._obter_numero_mapa(self.mapa_atual)
        rotulo = self.fonte.render(f"Mapa {numero}", True, (255, 255, 255))
        rect = rotulo.get_rect(center=(LARGURA // 2, 18))
        # Fundo discreto para legibilidade
        fundo = pygame.Surface((rect.width + 12, rect.height + 6), pygame.SRCALPHA)
        fundo.fill((0, 0, 0, 120))
        fundo_rect = fundo.get_rect(center=rect.center)
        self.screen.blit(fundo, fundo_rect)
        self.screen.blit(rotulo, rect)

    def _obter_numero_mapa(self, nome_mapa):
        """Tenta extrair o número do mapa a partir do nome (ex.: 'Mapa_2' -> 2)."""
        m = re.search(r"(\d+)$", str(nome_mapa))
        if m:
            try:
                return int(m.group(1))
            except ValueError:
                pass
        # Fallback: usar índice atual + 1
        try:
            return self.indice_mapa_atual + 1
        except Exception:
            return 1

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
