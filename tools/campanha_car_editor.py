#!/usr/bin/env python3
"""
Ferramenta de Edição de Carros da Campanha - Turbo Racer
=========================================================

Esta ferramenta permite ajustar tamanho, escala e posição dos carros da campanha na oficina.

Controles:
- F7: Ativar/Desativar modo de edição
- F5: Salvar configurações
- F6: Carregar configurações
- ESC: Sair
- Mouse: Clique para selecionar estágio/cor, arrastar para ajustar
- Setas: Navegar entre estágios/cores
- W/A/S/D: Ajustar posição Y offset (W=↑, S=↓)
- Q/E: Ajustar largura (Q=diminuir, E=aumentar)
- Z/X: Ajustar altura (Z=diminuir, X=aumentar)
- R/T: Ajustar escala (R=diminuir, T=aumentar)
- Tab: Alternar entre Estágios e Cores Finais

Autor: Turbo Racer Team
Versão: 1.0
"""

import sys
import os
import pygame
import json
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import LARGURA, ALTURA, FPS, obter_caminho_sprite_dia_noite

DIR_CAR_SELECTION_CAMPANHA = os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'car_selection', 'campanha')
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'campanha_car_config.json')

class CampanhaCarEditor:
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Campanha Car Editor - Turbo Racer")
        
        self.clock = pygame.time.Clock()
        
        self.modo_edicao = False
        self.aba_atual = "estagios"  # "estagios" ou "cores"
        self.item_selecionado = 0
        
        self.config = self.carregar_config()
        
        # Carregar background da oficina
        self.bg_oficina = None
        try:
            caminho_oficina = obter_caminho_sprite_dia_noite("oficina")
            if caminho_oficina and os.path.exists(caminho_oficina):
                self.bg_oficina = pygame.image.load(caminho_oficina).convert()
                self.bg_oficina = pygame.transform.scale(self.bg_oficina, (LARGURA, ALTURA))
                print(f"[EDITOR] Background carregado: {caminho_oficina}")
        except Exception as e:
            print(f"Erro ao carregar fundo da oficina: {e}")
        
        self.sprites_carros = {}
        self.carregar_sprites()
        
        self.fonte = pygame.font.Font(None, 24)
        self.fonte_pequena = pygame.font.Font(None, 18)
        self.fonte_grande = pygame.font.Font(None, 36)
        
        self.mostrar_ajuda = True
        self.velocidade_ajuste = 5
        self.velocidade_escala = 0.05
        
    def carregar_config(self):
        """Carrega a configuração do arquivo JSON"""
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar config: {e}")
        
        # Configuração padrão
        return {
            "estagios": [
                {
                    "estagio": 0,
                    "nome_sprite": "Car1_campanha_inicial",
                    "tamanho_oficina": [600, 300],
                    "escala": 0.7,
                    "y_offset": -50,
                    "descricao": "Carro inicial - quebrado"
                },
                {
                    "estagio": 1,
                    "nome_sprite": "Car1_lataria",
                    "tamanho_oficina": [600, 300],
                    "escala": 1.0,
                    "y_offset": -10,
                    "descricao": "Lataria reparada"
                },
                {
                    "estagio": 2,
                    "nome_sprite": "Car1_pneus_drift",
                    "tamanho_oficina": [600, 300],
                    "escala": 1.0,
                    "y_offset": -10,
                    "descricao": "Pneus de drift instalados"
                },
                {
                    "estagio": 3,
                    "nome_sprite": "Car1_bodykit",
                    "tamanho_oficina": [600, 300],
                    "escala": 1.0,
                    "y_offset": -10,
                    "descricao": "Bodykit completo"
                }
            ],
            "cores_finais": [
                {
                    "cor": "azul",
                    "nome_sprite": "Car1_final_azul",
                    "tamanho_oficina": [600, 300],
                    "escala": 1.0,
                    "y_offset": -10,
                    "descricao": "Versão final azul"
                },
                {
                    "cor": "branco",
                    "nome_sprite": "Car1_final_branco",
                    "tamanho_oficina": [600, 300],
                    "escala": 1.0,
                    "y_offset": -10,
                    "descricao": "Versão final branca"
                },
                {
                    "cor": "preto",
                    "nome_sprite": "Car1_final_preto",
                    "tamanho_oficina": [600, 300],
                    "escala": 1.0,
                    "y_offset": -10,
                    "descricao": "Versão final preta"
                },
                {
                    "cor": "verde",
                    "nome_sprite": "Car1_final_verde",
                    "tamanho_oficina": [600, 300],
                    "escala": 1.0,
                    "y_offset": -10,
                    "descricao": "Versão final verde"
                }
            ]
        }
    
    def carregar_sprites(self):
        """Carrega os sprites dos carros da campanha"""
        # Carregar estágios
        for estagio in self.config["estagios"]:
            try:
                sprite_path = os.path.join(DIR_CAR_SELECTION_CAMPANHA, f"{estagio['nome_sprite']}.png")
                if os.path.exists(sprite_path):
                    sprite = pygame.image.load(sprite_path).convert_alpha()
                    self.sprites_carros[estagio['nome_sprite']] = sprite
                else:
                    print(f"AVISO: Sprite não encontrado: {sprite_path}")
            except Exception as e:
                print(f"Erro ao carregar sprite {estagio['nome_sprite']}: {e}")
        
        # Carregar cores finais
        for cor in self.config["cores_finais"]:
            try:
                sprite_path = os.path.join(DIR_CAR_SELECTION_CAMPANHA, f"{cor['nome_sprite']}.png")
                if os.path.exists(sprite_path):
                    sprite = pygame.image.load(sprite_path).convert_alpha()
                    self.sprites_carros[cor['nome_sprite']] = sprite
                else:
                    print(f"AVISO: Sprite não encontrado: {sprite_path}")
            except Exception as e:
                print(f"Erro ao carregar sprite {cor['nome_sprite']}: {e}")
    
    def obter_item_atual(self):
        """Retorna o item atual (estágio ou cor)"""
        if self.aba_atual == "estagios":
            return self.config["estagios"][self.item_selecionado]
        else:
            return self.config["cores_finais"][self.item_selecionado]
    
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
                elif event.key == pygame.K_TAB:
                    self.aba_atual = "cores" if self.aba_atual == "estagios" else "estagios"
                    self.item_selecionado = 0
                    print(f"Aba: {self.aba_atual.upper()}")
                elif event.key == pygame.K_LEFT:
                    lista = self.config["estagios"] if self.aba_atual == "estagios" else self.config["cores_finais"]
                    self.item_selecionado = (self.item_selecionado - 1) % len(lista)
                    item = self.obter_item_atual()
                    print(f"Item selecionado: {item.get('descricao', item.get('nome_sprite', 'N/A'))}")
                elif event.key == pygame.K_RIGHT:
                    lista = self.config["estagios"] if self.aba_atual == "estagios" else self.config["cores_finais"]
                    self.item_selecionado = (self.item_selecionado + 1) % len(lista)
                    item = self.obter_item_atual()
                    print(f"Item selecionado: {item.get('descricao', item.get('nome_sprite', 'N/A'))}")
                
                if self.modo_edicao:
                    item = self.obter_item_atual()
                    if event.key == pygame.K_w:
                        item['y_offset'] -= self.velocidade_ajuste
                    elif event.key == pygame.K_s:
                        item['y_offset'] += self.velocidade_ajuste
                    elif event.key == pygame.K_q:
                        item['tamanho_oficina'][0] = max(100, item['tamanho_oficina'][0] - self.velocidade_ajuste)
                    elif event.key == pygame.K_e:
                        item['tamanho_oficina'][0] += self.velocidade_ajuste
                    elif event.key == pygame.K_z:
                        item['tamanho_oficina'][1] = max(100, item['tamanho_oficina'][1] - self.velocidade_ajuste)
                    elif event.key == pygame.K_x:
                        item['tamanho_oficina'][1] += self.velocidade_ajuste
                    elif event.key == pygame.K_r:
                        item['escala'] = max(0.1, item['escala'] - self.velocidade_escala)
                    elif event.key == pygame.K_t:
                        item['escala'] += self.velocidade_escala
        
        return True
    
    def desenhar(self):
        """Desenha a tela"""
        if self.bg_oficina:
            self.screen.blit(self.bg_oficina, (0, 0))
        else:
            self.screen.fill((40, 40, 40))
        
        # Desenhar carro atual
        item = self.obter_item_atual()
        self.desenhar_carro(item, True)
        
        self.desenhar_interface()
        
        pygame.display.flip()
    
    def desenhar_carro(self, item, selecionado=False):
        """Desenha um carro na oficina usando a mesma lógica do jogo"""
        nome_sprite = item['nome_sprite']
        
        if nome_sprite not in self.sprites_carros:
            return
        
        sprite_original = self.sprites_carros[nome_sprite]
        tamanho_oficina = item['tamanho_oficina']
        escala_config = item['escala']
        y_offset = item['y_offset']
        
        # REPLICAR A LÓGICA DO JOGO:
        # 1. Calcular tamanho do canvas
        canvas_largura = int(tamanho_oficina[0] * escala_config)
        canvas_altura = int(tamanho_oficina[1] * escala_config)
        
        # 2. Calcular escala do sprite baseado no canvas
        sprite_original_w, sprite_original_h = sprite_original.get_size()
        escala_x = canvas_largura / sprite_original_w if sprite_original_w > 0 else 1.0
        escala_y = canvas_altura / sprite_original_h if sprite_original_h > 0 else 1.0
        escala = min(escala_x, escala_y)  # Usar a menor escala para manter proporção
        
        # 3. Redimensionar sprite
        nova_largura = int(sprite_original_w * escala)
        nova_altura = int(sprite_original_h * escala)
        sprite_redimensionado = pygame.transform.scale(sprite_original, (nova_largura, nova_altura))
        
        # 4. Criar canvas
        canvas = pygame.Surface((canvas_largura, canvas_altura), pygame.SRCALPHA)
        
        # 5. Posicionar sprite no canvas
        x_offset_canvas = (canvas_largura - nova_largura) // 2
        y_offset_canvas = canvas_altura - nova_altura + y_offset
        canvas.blit(sprite_redimensionado, (x_offset_canvas, y_offset_canvas))
        
        # 6. Posicionar canvas na tela (centralizado)
        canvas_x = (LARGURA - canvas_largura) // 2
        canvas_y = (ALTURA - canvas_altura) // 2
        
        # Desenhar canvas
        self.screen.blit(canvas, (canvas_x, canvas_y))
        
        # Desenhar borda se selecionado
        if selecionado:
            cor_borda = (0, 255, 0) if self.modo_edicao else (255, 255, 0)
            espessura = 3 if self.modo_edicao else 2
            pygame.draw.rect(self.screen, cor_borda, (canvas_x, canvas_y, canvas_largura, canvas_altura), espessura)
    
    def desenhar_interface(self):
        """Desenha a interface do editor"""
        y_offset = 10
        
        # Título
        titulo = self.fonte_grande.render("CAMPANHA CAR EDITOR", True, (255, 255, 255))
        self.screen.blit(titulo, (10, y_offset))
        y_offset += 40
        
        # Aba atual
        aba_texto = f"ABA: {self.aba_atual.upper()}"
        texto_aba = self.fonte.render(aba_texto, True, (200, 200, 255))
        self.screen.blit(texto_aba, (10, y_offset))
        y_offset += 30
        
        # Informações do item selecionado
        item = self.obter_item_atual()
        lista = self.config["estagios"] if self.aba_atual == "estagios" else self.config["cores_finais"]
        
        info_lines = [
            f"Item: {item.get('descricao', item.get('nome_sprite', 'N/A'))} ({self.item_selecionado + 1}/{len(lista)})",
            f"Sprite: {item['nome_sprite']}",
            f"Tamanho oficina: [{item['tamanho_oficina'][0]}, {item['tamanho_oficina'][1]}]",
            f"Escala: {item['escala']:.2f}",
            f"Y Offset: {item['y_offset']}",
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
        
        # Lista de itens (navegação)
        y_offset += 10
        texto_lista = self.fonte.render(f"LISTA DE {self.aba_atual.upper()} (← → para navegar):", True, (200, 200, 200))
        self.screen.blit(texto_lista, (10, y_offset))
        y_offset += 25
        
        # Mostrar lista de itens com destaque para o selecionado
        max_itens_visiveis = min(8, len(lista))
        inicio_lista = max(0, self.item_selecionado - 3)
        fim_lista = min(len(lista), inicio_lista + max_itens_visiveis)
        
        for i in range(inicio_lista, fim_lista):
            item_lista = lista[i]
            is_selected = (i == self.item_selecionado)
            
            # Cor e fundo para o item selecionado
            if is_selected:
                # Fundo destacado
                fundo_rect = pygame.Rect(10, y_offset - 2, 500, 22)
                pygame.draw.rect(self.screen, (0, 100, 200), fundo_rect)
                cor_texto = (255, 255, 0)
            else:
                cor_texto = (200, 200, 200)
            
            descricao = item_lista.get('descricao', item_lista.get('nome_sprite', 'N/A'))
            texto_item = self.fonte_pequena.render(
                f"{i+1}. {descricao}", 
                True, 
                cor_texto
            )
            self.screen.blit(texto_item, (15, y_offset))
            y_offset += 22
        
        # Ajuda
        if self.mostrar_ajuda:
            ajuda_lines = [
                "CONTROLES:",
                "F7 - Ativar/Desativar modo edição",
                "F5 - Salvar configurações",
                "F6 - Carregar configurações",
                "TAB - Alternar Estágios/Cores",
                "← → - Navegar entre itens",
                "W/S - Ajustar Y Offset (modo edição)",
                "Q/E - Ajustar largura (modo edição)",
                "Z/X - Ajustar altura (modo edição)",
                "R/T - Ajustar escala (modo edição)",
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
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            print(f"Configurações salvas em: {CONFIG_PATH}")
            
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
    
    def carregar_configuracoes(self):
        """Carrega configurações de um arquivo JSON"""
        try:
            if not os.path.exists(CONFIG_PATH):
                print(f"Arquivo não encontrado: {CONFIG_PATH}")
                return
            
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            # Recarregar sprites
            self.sprites_carros = {}
            self.carregar_sprites()
            
            print(f"Configurações carregadas de: {CONFIG_PATH}")
            
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
    
    def executar(self):
        """Loop principal do editor"""
        rodando = True
        while rodando:
            dt = self.clock.tick(FPS) / 1000.0
            rodando = self.processar_eventos()
            self.desenhar()
        
        pygame.quit()

if __name__ == "__main__":
    editor = CampanhaCarEditor()
    editor.executar()
