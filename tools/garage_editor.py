#!/usr/bin/env python3
"""
Ferramenta de Edição de Garagem - Turbo Racer
=============================================

Esta ferramenta permite ajustar a posição, tamanho e escala dos carros na garagem/oficina.

Controles:
- F7: Ativar/Desativar modo de edição
- F5: Salvar configurações
- F6: Carregar configurações
- ESC: Sair
- Mouse: Clique para selecionar carro, arrastar para mover, arrastar cantos para redimensionar
- Setas: Navegar entre carros
- W/A/S/D: Ajustar posição (W=↑, S=↓, A=←, D=→)
- Q/E: Ajustar largura (Q=diminuir, E=aumentar)
- Z/X: Ajustar altura (Z=diminuir, X=aumentar)

Autor: Turbo Racer Team
Versão: 1.0
"""

import sys
import os
import pygame
import json
from pathlib import Path

# Adicionar o diretório src ao path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import LARGURA, ALTURA, FPS, CAMINHO_OFICINA, DIR_SPRITES, DIR_CAR_SELECTION

# Importar lista de carros do main.py
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from main import CARROS_DISPONIVEIS

class GarageEditor:
    def __init__(self):
        pygame.init()
        
        # Configurações da tela
        self.screen = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Garage Editor - Turbo Racer")
        
        # Clock para FPS
        self.clock = pygame.time.Clock()
        
        # Estado do editor
        self.modo_edicao = False
        self.carro_selecionado = 0
        self.arrastando = False
        self.arrastando_canto = None
        self.offset_arraste = (0, 0)
        
        # Carregar dados dos carros (cópia para edição)
        self.carros = []
        for carro in CARROS_DISPONIVEIS:
            self.carros.append({
                'nome': carro['nome'],
                'prefixo_cor': carro['prefixo_cor'],
                'sprite_selecao': carro.get('sprite_selecao', carro['prefixo_cor']),
                'posicao': list(carro.get('posicao', (570, 145))),
                'tamanho_oficina': list(carro.get('tamanho_oficina', (600, 300))),
                'posicao_oficina': list(carro.get('posicao_oficina', (LARGURA//2 - 300, 380))),
                'preco': carro.get('preco', 0),
                'tipo_tracao': carro.get('tipo_tracao', 'rear')
            })
        
        # Carregar imagem de fundo da oficina
        self.bg_oficina = None
        try:
            if os.path.exists(CAMINHO_OFICINA):
                self.bg_oficina = pygame.image.load(CAMINHO_OFICINA).convert()
                self.bg_oficina = pygame.transform.scale(self.bg_oficina, (LARGURA, ALTURA))
        except Exception as e:
            print(f"Erro ao carregar fundo da oficina: {e}")
        
        # Carregar sprites dos carros
        self.sprites_carros = {}
        self.carregar_sprites()
        
        # Fonte
        self.fonte = pygame.font.Font(None, 24)
        self.fonte_pequena = pygame.font.Font(None, 18)
        self.fonte_grande = pygame.font.Font(None, 36)
        
        # Estado da interface
        self.mostrar_ajuda = True
        self.velocidade_ajuste = 5  # Pixels por ajuste
        
    def carregar_sprites(self):
        """Carrega os sprites dos carros"""
        for carro in self.carros:
            try:
                # Primeiro tenta carregar da pasta car_selection
                sprite_path = os.path.join(DIR_CAR_SELECTION, f"{carro['sprite_selecao']}.png")
                if not os.path.exists(sprite_path):
                    # Se não existir, usa o sprite normal
                    sprite_path = os.path.join(DIR_SPRITES, f"{carro['prefixo_cor']}.png")
                
                sprite = pygame.image.load(sprite_path).convert_alpha()
                self.sprites_carros[carro['prefixo_cor']] = sprite
            except Exception as e:
                print(f"Erro ao carregar sprite de {carro['nome']}: {e}")
                # Criar sprite placeholder
                placeholder = pygame.Surface((100, 50), pygame.SRCALPHA)
                pygame.draw.rect(placeholder, (128, 128, 128), (0, 0, 100, 50))
                self.sprites_carros[carro['prefixo_cor']] = placeholder
    
    def processar_eventos(self):
        """Processa eventos do teclado e mouse"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_F7:
                    self.modo_edicao = not self.modo_edicao
                    print(f"Modo edição: {'ATIVADO' if self.modo_edicao else 'DESATIVADO'}")
                elif event.key == pygame.K_F5:
                    self.salvar_configuracoes()
                elif event.key == pygame.K_F6:
                    self.carregar_configuracoes()
                elif event.key == pygame.K_h:
                    self.mostrar_ajuda = not self.mostrar_ajuda
                elif event.key == pygame.K_LEFT:
                    self.carro_selecionado = (self.carro_selecionado - 1) % len(self.carros)
                    print(f"Carro selecionado: {self.carros[self.carro_selecionado]['nome']} ({self.carro_selecionado + 1}/{len(self.carros)})")
                elif event.key == pygame.K_RIGHT:
                    self.carro_selecionado = (self.carro_selecionado + 1) % len(self.carros)
                    print(f"Carro selecionado: {self.carros[self.carro_selecionado]['nome']} ({self.carro_selecionado + 1}/{len(self.carros)})")
                
                # Ajustes de posição (apenas em modo edição)
                if self.modo_edicao:
                    carro = self.carros[self.carro_selecionado]
                    if event.key == pygame.K_w:
                        carro['posicao_oficina'][1] -= self.velocidade_ajuste
                    elif event.key == pygame.K_s:
                        carro['posicao_oficina'][1] += self.velocidade_ajuste
                    elif event.key == pygame.K_a:
                        carro['posicao_oficina'][0] -= self.velocidade_ajuste
                    elif event.key == pygame.K_d:
                        carro['posicao_oficina'][0] += self.velocidade_ajuste
                    elif event.key == pygame.K_q:
                        carro['tamanho_oficina'][0] = max(100, carro['tamanho_oficina'][0] - self.velocidade_ajuste)
                    elif event.key == pygame.K_e:
                        carro['tamanho_oficina'][0] += self.velocidade_ajuste
                    elif event.key == pygame.K_z:
                        carro['tamanho_oficina'][1] = max(100, carro['tamanho_oficina'][1] - self.velocidade_ajuste)
                    elif event.key == pygame.K_x:
                        carro['tamanho_oficina'][1] += self.velocidade_ajuste
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo
                    mouse_x, mouse_y = event.pos
                    
                    # Verificar primeiro se clicou no carro selecionado (para mover/redimensionar)
                    carro_atual = self.carros[self.carro_selecionado]
                    rect_atual = pygame.Rect(
                        carro_atual['posicao_oficina'][0],
                        carro_atual['posicao_oficina'][1],
                        carro_atual['tamanho_oficina'][0],
                        carro_atual['tamanho_oficina'][1]
                    )
                    
                    # Se clicou no carro selecionado, verificar se é para mover ou redimensionar
                    if rect_atual.collidepoint(mouse_x, mouse_y):
                        # Verificar se clicou em um canto para redimensionar
                        canto = self.verificar_canto(rect_atual, mouse_x, mouse_y)
                        if canto and self.modo_edicao:
                            self.arrastando_canto = canto
                        elif self.modo_edicao:
                            # Iniciar arraste para mover
                            self.arrastando = True
                            self.offset_arraste = (
                                mouse_x - carro_atual['posicao_oficina'][0],
                                mouse_y - carro_atual['posicao_oficina'][1]
                            )
                        # Se não estiver em modo edição, não fazer nada (não mudar seleção)
                    else:
                        # Se não clicou no carro selecionado, verificar se clicou em outro carro
                        # (mas só se não estiver em modo edição, para evitar mudanças acidentais)
                        if not self.modo_edicao:
                            carro_idx = self.encontrar_carro_no_ponto(mouse_x, mouse_y)
                            if carro_idx is not None and carro_idx != self.carro_selecionado:
                                self.carro_selecionado = carro_idx
                                print(f"Carro selecionado: {self.carros[self.carro_selecionado]['nome']} ({self.carro_selecionado + 1}/{len(self.carros)})")
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.arrastando = False
                    self.arrastando_canto = None
            
            elif event.type == pygame.MOUSEMOTION:
                if self.arrastando and self.modo_edicao:
                    carro = self.carros[self.carro_selecionado]
                    carro['posicao_oficina'][0] = event.pos[0] - self.offset_arraste[0]
                    carro['posicao_oficina'][1] = event.pos[1] - self.offset_arraste[1]
                elif self.arrastando_canto and self.modo_edicao:
                    carro = self.carros[self.carro_selecionado]
                    rect = pygame.Rect(
                        carro['posicao_oficina'][0],
                        carro['posicao_oficina'][1],
                        carro['tamanho_oficina'][0],
                        carro['tamanho_oficina'][1]
                    )
                    if self.arrastando_canto == 'se':
                        # Canto superior esquerdo
                        nova_largura = rect.right - event.pos[0]
                        nova_altura = rect.bottom - event.pos[1]
                        if nova_largura > 50:
                            carro['tamanho_oficina'][0] = nova_largura
                            carro['posicao_oficina'][0] = event.pos[0]
                        if nova_altura > 50:
                            carro['tamanho_oficina'][1] = nova_altura
                            carro['posicao_oficina'][1] = event.pos[1]
                    elif self.arrastando_canto == 'sd':
                        # Canto superior direito
                        nova_largura = event.pos[0] - rect.left
                        nova_altura = rect.bottom - event.pos[1]
                        if nova_largura > 50:
                            carro['tamanho_oficina'][0] = nova_largura
                        if nova_altura > 50:
                            carro['tamanho_oficina'][1] = nova_altura
                            carro['posicao_oficina'][1] = event.pos[1]
                    elif self.arrastando_canto == 'ie':
                        # Canto inferior esquerdo
                        nova_largura = rect.right - event.pos[0]
                        nova_altura = event.pos[1] - rect.top
                        if nova_largura > 50:
                            carro['tamanho_oficina'][0] = nova_largura
                            carro['posicao_oficina'][0] = event.pos[0]
                        if nova_altura > 50:
                            carro['tamanho_oficina'][1] = nova_altura
                    elif self.arrastando_canto == 'id':
                        # Canto inferior direito
                        nova_largura = event.pos[0] - rect.left
                        nova_altura = event.pos[1] - rect.top
                        if nova_largura > 50:
                            carro['tamanho_oficina'][0] = nova_largura
                        if nova_altura > 50:
                            carro['tamanho_oficina'][1] = nova_altura
        
        return True
    
    def encontrar_carro_no_ponto(self, x, y):
        """Encontra qual carro está no ponto (x, y)"""
        for i, carro in enumerate(self.carros):
            rect = pygame.Rect(
                carro['posicao_oficina'][0],
                carro['posicao_oficina'][1],
                carro['tamanho_oficina'][0],
                carro['tamanho_oficina'][1]
            )
            if rect.collidepoint(x, y):
                return i
        return None
    
    def verificar_canto(self, rect, x, y, raio=10):
        """Verifica se o ponto está em um canto do retângulo"""
        cantos = {
            'se': (rect.left, rect.top),      # Superior esquerdo
            'sd': (rect.right, rect.top),      # Superior direito
            'ie': (rect.left, rect.bottom),    # Inferior esquerdo
            'id': (rect.right, rect.bottom)    # Inferior direito
        }
        for nome, (cx, cy) in cantos.items():
            if abs(x - cx) < raio and abs(y - cy) < raio:
                return nome
        return None
    
    def desenhar(self):
        """Desenha a tela"""
        # Fundo
        if self.bg_oficina:
            self.screen.blit(self.bg_oficina, (0, 0))
        else:
            self.screen.fill((40, 40, 40))
        
        # Desenhar apenas o carro selecionado (não todos empilhados)
        carro_selecionado_obj = self.carros[self.carro_selecionado]
        self.desenhar_carro(carro_selecionado_obj, True)
        
        # Desenhar interface
        self.desenhar_interface()
        
        pygame.display.flip()
    
    def desenhar_carro(self, carro, selecionado=False):
        """Desenha um carro na oficina"""
        x, y = carro['posicao_oficina']
        largura, altura = carro['tamanho_oficina']
        
        # Retângulo do canvas
        cor_borda = (0, 255, 0) if selecionado else (128, 128, 128)
        espessura = 3 if selecionado else 1
        
        # Fundo semi-transparente
        superficie_canvas = pygame.Surface((largura, altura), pygame.SRCALPHA)
        superficie_canvas.fill((0, 0, 0, 100))
        self.screen.blit(superficie_canvas, (x, y))
        
        # Borda
        pygame.draw.rect(self.screen, cor_borda, (x, y, largura, altura), espessura)
        
        # Desenhar sprite do carro
        if carro['prefixo_cor'] in self.sprites_carros:
            sprite_original = self.sprites_carros[carro['prefixo_cor']]
            
            # Calcular escala para manter proporção
            escala_x = largura / sprite_original.get_width()
            escala_y = altura / sprite_original.get_height()
            escala = min(escala_x, escala_y) * 0.9  # 90% para deixar margem
            
            # Redimensionar
            nova_largura = int(sprite_original.get_width() * escala)
            nova_altura = int(sprite_original.get_height() * escala)
            sprite_redimensionado = pygame.transform.scale(sprite_original, (nova_largura, nova_altura))
            
            # Centralizar e posicionar na parte inferior
            x_offset = (largura - nova_largura) // 2
            y_offset = altura - nova_altura - 5
            self.screen.blit(sprite_redimensionado, (x + x_offset, y + y_offset))
        
        # Desenhar cantos de redimensionamento (se selecionado)
        if selecionado and self.modo_edicao:
            raio = 8
            cantos = [
                (x, y),                    # Superior esquerdo
                (x + largura, y),          # Superior direito
                (x, y + altura),           # Inferior esquerdo
                (x + largura, y + altura)  # Inferior direito
            ]
            for cx, cy in cantos:
                pygame.draw.circle(self.screen, (255, 255, 0), (cx, cy), raio)
                pygame.draw.circle(self.screen, (0, 0, 0), (cx, cy), raio, 2)
        
        # Nome do carro
        texto = self.fonte_pequena.render(carro['nome'], True, (255, 255, 255))
        self.screen.blit(texto, (x + 5, y + 5))
    
    def desenhar_interface(self):
        """Desenha a interface do editor"""
        y_offset = 10
        
        # Título
        titulo = self.fonte_grande.render("GARAGE EDITOR", True, (255, 255, 255))
        self.screen.blit(titulo, (10, y_offset))
        y_offset += 40
        
        # Informações do carro selecionado
        carro = self.carros[self.carro_selecionado]
        info_lines = [
            f"Carro: {carro['nome']} ({self.carro_selecionado + 1}/{len(self.carros)})",
            f"Posição oficina: ({carro['posicao_oficina'][0]}, {carro['posicao_oficina'][1]})",
            f"Tamanho oficina: ({carro['tamanho_oficina'][0]}, {carro['tamanho_oficina'][1]})",
            f"Posição menu: ({carro['posicao'][0]}, {carro['posicao'][1]})",
        ]
        
        for line in info_lines:
            texto = self.fonte.render(line, True, (255, 255, 255))
            self.screen.blit(texto, (10, y_offset))
            y_offset += 25
        
        # Modo edição
        modo_texto = "MODO EDIÇÃO: ATIVADO" if self.modo_edicao else "MODO EDIÇÃO: DESATIVADO"
        cor_modo = (0, 255, 0) if self.modo_edicao else (255, 0, 0)
        texto_modo = self.fonte.render(modo_texto, True, cor_modo)
        self.screen.blit(texto_modo, (10, y_offset))
        y_offset += 30
        
        # Lista de carros (navegação)
        y_offset += 10
        texto_lista = self.fonte.render("LISTA DE CARROS (← → para navegar):", True, (200, 200, 200))
        self.screen.blit(texto_lista, (10, y_offset))
        y_offset += 25
        
        # Mostrar lista de carros com destaque para o selecionado
        max_carros_visiveis = min(8, len(self.carros))
        inicio_lista = max(0, self.carro_selecionado - 3)
        fim_lista = min(len(self.carros), inicio_lista + max_carros_visiveis)
        
        for i in range(inicio_lista, fim_lista):
            carro_item = self.carros[i]
            is_selected = (i == self.carro_selecionado)
            
            # Cor e fundo para o item selecionado
            if is_selected:
                # Fundo destacado
                fundo_rect = pygame.Rect(10, y_offset - 2, 400, 22)
                pygame.draw.rect(self.screen, (0, 100, 200), fundo_rect)
                cor_texto = (255, 255, 0)
            else:
                cor_texto = (200, 200, 200)
            
            texto_carro = self.fonte_pequena.render(
                f"{i+1}. {carro_item['nome']}", 
                True, 
                cor_texto
            )
            self.screen.blit(texto_carro, (15, y_offset))
            y_offset += 22
        
        # Ajuda
        if self.mostrar_ajuda:
            ajuda_lines = [
                "CONTROLES:",
                "F7 - Ativar/Desativar modo edição",
                "F5 - Salvar configurações",
                "F6 - Carregar configurações",
                "← → - Navegar entre carros",
                "W/A/S/D - Mover posição (modo edição)",
                "Q/E - Ajustar largura (modo edição)",
                "Z/X - Ajustar altura (modo edição)",
                "Mouse - Arrastar para mover, cantos para redimensionar",
                "H - Mostrar/Ocultar ajuda",
                "ESC - Sair"
            ]
            
            # Fundo semi-transparente para ajuda
            ajuda_surface = pygame.Surface((300, len(ajuda_lines) * 20 + 20), pygame.SRCALPHA)
            ajuda_surface.fill((0, 0, 0, 180))
            self.screen.blit(ajuda_surface, (LARGURA - 320, 10))
            
            y_ajuda = 20
            for line in ajuda_lines:
                texto = self.fonte_pequena.render(line, True, (255, 255, 255))
                self.screen.blit(texto, (LARGURA - 310, y_ajuda))
                y_ajuda += 20
    
    def salvar_configuracoes(self):
        """Salva as configurações em um arquivo JSON"""
        try:
            caminho_arquivo = os.path.join(os.path.dirname(__file__), '..', 'data', 'garage_config.json')
            os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
            
            dados = {
                'carros': []
            }
            
            for carro in self.carros:
                dados['carros'].append({
                    'prefixo_cor': carro['prefixo_cor'],
                    'posicao': carro['posicao'],
                    'tamanho_oficina': carro['tamanho_oficina'],
                    'posicao_oficina': carro['posicao_oficina']
                })
            
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
            
            print(f"Configurações salvas em: {caminho_arquivo}")
            
            # Também gerar código Python para copiar no main.py
            self.gerar_codigo_python()
            
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
    
    def carregar_configuracoes(self):
        """Carrega configurações de um arquivo JSON"""
        try:
            caminho_arquivo = os.path.join(os.path.dirname(__file__), '..', 'data', 'garage_config.json')
            
            if not os.path.exists(caminho_arquivo):
                print(f"Arquivo não encontrado: {caminho_arquivo}")
                return
            
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            # Criar dicionário por prefixo_cor para busca rápida
            carros_dict = {carro['prefixo_cor']: carro for carro in self.carros}
            
            # Atualizar carros com dados carregados
            for carro_data in dados.get('carros', []):
                prefixo = carro_data.get('prefixo_cor')
                if prefixo in carros_dict:
                    carro = carros_dict[prefixo]
                    if 'posicao' in carro_data:
                        carro['posicao'] = carro_data['posicao']
                    if 'tamanho_oficina' in carro_data:
                        carro['tamanho_oficina'] = carro_data['tamanho_oficina']
                    if 'posicao_oficina' in carro_data:
                        carro['posicao_oficina'] = carro_data['posicao_oficina']
            
            print(f"Configurações carregadas de: {caminho_arquivo}")
            
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
    
    def gerar_codigo_python(self):
        """Gera código Python para copiar no main.py"""
        print("\n" + "="*80)
        print("CÓDIGO PARA COPIAR NO main.py (CARROS_DISPONIVEIS):")
        print("="*80)
        
        for i, carro in enumerate(self.carros):
            # Encontrar carro original para manter outros campos
            carro_original = None
            for carro_orig in CARROS_DISPONIVEIS:
                if carro_orig['prefixo_cor'] == carro['prefixo_cor']:
                    carro_original = carro_orig
                    break
            
            if carro_original:
                linha = f'    {{"nome": "{carro_original["nome"]}", '
                linha += f'"prefixo_cor": "{carro["prefixo_cor"]}", '
                linha += f'"posicao": {tuple(carro["posicao"])}, '
                linha += f'"sprite_selecao": "{carro["sprite_selecao"]}", '
                linha += f'"tipo_tracao": "{carro["tipo_tracao"]}", '
                linha += f'"tamanho_oficina": {tuple(carro["tamanho_oficina"])}, '
                linha += f'"posicao_oficina": {tuple(carro["posicao_oficina"])}, '
                linha += f'"preco": {carro["preco"]}}},'
                print(linha)
        
        print("="*80 + "\n")
    
    def executar(self):
        """Loop principal do editor"""
        rodando = True
        while rodando:
            dt = self.clock.tick(FPS) / 1000.0
            rodando = self.processar_eventos()
            self.desenhar()
        
        pygame.quit()

if __name__ == "__main__":
    editor = GarageEditor()
    editor.executar()

