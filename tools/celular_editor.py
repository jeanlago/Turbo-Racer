#!/usr/bin/env python3
"""
Editor de Configuração do Celular - Turbo Racer
===============================================

Esta ferramenta permite editar visualmente as configurações do celular,
incluindo posições, tamanhos, cores e outros parâmetros.

Controles:
- Mouse: Clique para selecionar campos, arrastar sliders
- Teclado: Digite valores numéricos diretamente
- F5: Salvar configurações
- F6: Carregar configurações
- ESC: Sair

Autor: Turbo Racer Team
Versão: 1.0
"""

import sys
import os
import pygame
import json
from pathlib import Path

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import LARGURA, ALTURA, FPS, DIR_PROJETO

CAMINHO_CONFIG = os.path.join(DIR_PROJETO, "data", "celular_config.json")
CAMINHO_TELA_CELULAR = os.path.join(DIR_PROJETO, "assets", "images", "ui", "tela_celular.png")

class CelularEditor:
    def __init__(self):
        pygame.init()
        
        self.largura_tela = 1200
        self.altura_tela = 800
        
        self.screen = pygame.display.set_mode((self.largura_tela, self.altura_tela))
        pygame.display.set_caption("Editor de Celular - Turbo Racer")
        self.clock = pygame.time.Clock()
        
        self.fonte = pygame.font.Font(None, 24)
        self.fonte_pequena = pygame.font.Font(None, 18)
        self.fonte_grande = pygame.font.Font(None, 32)
        
        self.config = self.carregar_config()
        self.config_original = json.loads(json.dumps(self.config))  # Deep copy
        
        self.scroll_y = 0
        self.campo_selecionado = None
        self.campo_editando = None
        self.texto_editando = ""
        
        self.preview_ativo = True
        self.preview_x = 800
        self.preview_y = 50
        self.preview_largura = 400
        self.preview_altura = 600
        
        self.cor_fundo = (40, 40, 50)
        self.cor_painel = (60, 60, 70)
        self.cor_botao = (80, 120, 160)
        self.cor_botao_hover = (100, 140, 180)
        self.cor_texto = (255, 255, 255)
        self.cor_texto_secundario = (200, 200, 200)
        
        # Carregar imagem do celular
        self.tela_celular_bg = None
        self.carregar_tela_celular()
        
        self.campos = []
        self.preparar_campos()
        
    def carregar_tela_celular(self):
        """Carrega a imagem de background do celular"""
        try:
            if os.path.exists(CAMINHO_TELA_CELULAR):
                self.tela_celular_bg = pygame.image.load(CAMINHO_TELA_CELULAR).convert_alpha()
                print(f"[EDITOR] Background do celular carregado: {CAMINHO_TELA_CELULAR}")
            else:
                print(f"[EDITOR] AVISO: Background do celular não encontrado: {CAMINHO_TELA_CELULAR}")
                self.tela_celular_bg = None
        except Exception as e:
            print(f"[EDITOR] Erro ao carregar background do celular: {e}")
            self.tela_celular_bg = None
    
    def carregar_config(self):
        """Carrega a configuração do celular"""
        config_padrao = {
            "menu": {
                "largura": 500,
                "altura": 600,
                "x": "centro",
                "y": "centro",
                "offset_x": 0,
                "offset_y": 0
            },
            "hora": {
                "x": 20,
                "y": 20,
                "tamanho_fonte": 24,
                "cor": [255, 255, 255],
                "negrito": True
            },
            "dia": {
                "x": 20,
                "y": 50,
                "tamanho_fonte": 18,
                "cor": [200, 200, 200],
                "negrito": False
            },
            "status": {
                "titulo": {
                    "x": 20,
                    "y_offset": 80,
                    "tamanho_fonte": 18,
                    "cor": [255, 200, 0],
                    "negrito": True
                },
                "espacamento_linhas": 25,
                "barra_altura": 10,
                "barra_largura_offset": 60,
                "barra_espacamento": 15,
                "barra_x_offset": 20,
                "barra_y_offset_base": 42,
                "texto_x_offset": 20,
                "texto_y_offset_base": 25
            },
            "menu_opcoes": {
                "inicio_y_offset": 180,
                "altura_opcao": 35,
                "espacamento": 0,
                "x": 40,
                "y_padding": 8
            },
            "titulo": {
                "x": 20,
                "y": 20,
                "tamanho_fonte": 28,
                "cor": [255, 255, 255],
                "negrito": True
            },
            "voltar": {
                "x_offset": -150,
                "y_offset": -30,
                "tamanho_fonte": 16,
                "cor": [200, 200, 200],
                "negrito": False
            },
            "overlay": {
                "opacidade": 180
            },
            "borda": {
                "cor": [100, 150, 200],
                "espessura": 3
            }
        }
        
        try:
            if os.path.exists(CAMINHO_CONFIG):
                with open(CAMINHO_CONFIG, 'r', encoding='utf-8') as f:
                    config_carregada = json.load(f)
                    # Mesclar com padrão
                    config = config_padrao.copy()
                    for key, value in config_carregada.items():
                        if isinstance(value, dict) and key in config:
                            config[key].update(value)
                        else:
                            config[key] = value
                    return config
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
        
        return config_padrao
    
    def salvar_config(self):
        """Salva a configuração do celular"""
        try:
            os.makedirs(os.path.dirname(CAMINHO_CONFIG), exist_ok=True)
            with open(CAMINHO_CONFIG, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"Configuração salva em: {CAMINHO_CONFIG}")
            return True
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
            return False
    
    def preparar_campos(self):
        """Prepara a lista de campos editáveis"""
        self.campos = []
        y = 50
        
        # Menu
        self.campos.append({"tipo": "titulo", "texto": "MENU", "y": y})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["menu", "largura"], "label": "Largura", "y": y, "min": 200, "max": 1000})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["menu", "altura"], "label": "Altura", "y": y, "min": 200, "max": 1000})
        y += 30
        self.campos.append({"tipo": "texto", "caminho": ["menu", "x"], "label": "Posição X", "y": y, "opcoes": ["centro", "numero"]})
        y += 30
        self.campos.append({"tipo": "texto", "caminho": ["menu", "y"], "label": "Posição Y", "y": y, "opcoes": ["centro", "numero"]})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["menu", "offset_x"], "label": "Offset X", "y": y, "min": -500, "max": 500})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["menu", "offset_y"], "label": "Offset Y", "y": y, "min": -500, "max": 500})
        y += 50
        
        # Hora
        self.campos.append({"tipo": "titulo", "texto": "HORA", "y": y})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["hora", "x"], "label": "X", "y": y, "min": 0, "max": 500})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["hora", "y"], "label": "Y", "y": y, "min": 0, "max": 100})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["hora", "tamanho_fonte"], "label": "Tamanho Fonte", "y": y, "min": 10, "max": 50})
        y += 30
        self.campos.append({"tipo": "cor", "caminho": ["hora", "cor"], "label": "Cor", "y": y})
        y += 30
        self.campos.append({"tipo": "bool", "caminho": ["hora", "negrito"], "label": "Negrito", "y": y})
        y += 50
        
        # Dia
        self.campos.append({"tipo": "titulo", "texto": "DIA", "y": y})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["dia", "x"], "label": "X", "y": y, "min": 0, "max": 500})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["dia", "y"], "label": "Y", "y": y, "min": 0, "max": 100})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["dia", "tamanho_fonte"], "label": "Tamanho Fonte", "y": y, "min": 10, "max": 50})
        y += 30
        self.campos.append({"tipo": "cor", "caminho": ["dia", "cor"], "label": "Cor", "y": y})
        y += 30
        self.campos.append({"tipo": "bool", "caminho": ["dia", "negrito"], "label": "Negrito", "y": y})
        y += 50
        
        # Status
        self.campos.append({"tipo": "titulo", "texto": "STATUS", "y": y})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["status", "titulo", "x"], "label": "Título X", "y": y, "min": 0, "max": 500})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["status", "titulo", "y_offset"], "label": "Título Y Offset", "y": y, "min": 0, "max": 200})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["status", "espacamento_linhas"], "label": "Espaçamento Linhas", "y": y, "min": 10, "max": 50})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["status", "barra_altura"], "label": "Altura Barra", "y": y, "min": 5, "max": 30})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["status", "barra_largura_offset"], "label": "Largura Offset (redução)", "y": y, "min": 0, "max": 200})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["status", "barra_x_offset"], "label": "Barra X Offset", "y": y, "min": 0, "max": 200})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["status", "barra_y_offset_base"], "label": "Barra Y Offset Base", "y": y, "min": 0, "max": 200})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["status", "texto_x_offset"], "label": "Texto X Offset", "y": y, "min": 0, "max": 200})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["status", "texto_y_offset_base"], "label": "Texto Y Offset Base", "y": y, "min": 0, "max": 200})
        y += 50
        
        # Menu Opções
        self.campos.append({"tipo": "titulo", "texto": "MENU OPÇÕES", "y": y})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["menu_opcoes", "inicio_y_offset"], "label": "Início Y Offset", "y": y, "min": 0, "max": 400})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["menu_opcoes", "altura_opcao"], "label": "Altura Opção", "y": y, "min": 20, "max": 60})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["menu_opcoes", "espacamento"], "label": "Espaçamento", "y": y, "min": 0, "max": 20})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["menu_opcoes", "x"], "label": "X", "y": y, "min": 0, "max": 500})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["menu_opcoes", "y_padding"], "label": "Y Padding", "y": y, "min": 0, "max": 20})
        y += 50
        
        # Overlay
        self.campos.append({"tipo": "titulo", "texto": "OVERLAY", "y": y})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["overlay", "opacidade"], "label": "Opacidade", "y": y, "min": 0, "max": 255})
        y += 50
        
        # Borda
        self.campos.append({"tipo": "titulo", "texto": "BORDA", "y": y})
        y += 30
        self.campos.append({"tipo": "cor", "caminho": ["borda", "cor"], "label": "Cor", "y": y})
        y += 30
        self.campos.append({"tipo": "numero", "caminho": ["borda", "espessura"], "label": "Espessura", "y": y, "min": 1, "max": 10})
        y += 50
        
    def obter_valor(self, caminho):
        """Obtém um valor do config usando um caminho"""
        valor = self.config
        for chave in caminho:
            if isinstance(valor, dict) and chave in valor:
                valor = valor[chave]
            else:
                return None
        return valor
    
    def definir_valor(self, caminho, valor):
        """Define um valor no config usando um caminho"""
        obj = self.config
        for i, chave in enumerate(caminho[:-1]):
            if chave not in obj:
                obj[chave] = {}
            obj = obj[chave]
        obj[caminho[-1]] = valor
    
    def desenhar_campo(self, campo, y_real):
        """Desenha um campo editável"""
        x = 20
        largura_campo = 350
        
        if campo["tipo"] == "titulo":
            texto = self.fonte_grande.render(campo["texto"], True, self.cor_texto)
            self.screen.blit(texto, (x, y_real))
            return
        
        # Label
        label = self.fonte.render(campo["label"] + ":", True, self.cor_texto)
        self.screen.blit(label, (x, y_real))
        
        valor = self.obter_valor(campo["caminho"])
        if valor is None:
            valor = 0
        
        x_valor = x + 150
        largura_valor = 200
        
        # Destaque se selecionado
        if self.campo_selecionado == campo:
            pygame.draw.rect(self.screen, (100, 100, 120), 
                           (x_valor - 5, y_real - 2, largura_valor + 10, 26))
        
        if campo["tipo"] == "numero":
            if isinstance(valor, (int, float)):
                texto_valor = str(int(valor))
            else:
                texto_valor = str(valor)
            
            if self.campo_editando == campo:
                texto_valor = self.texto_editando
                # Cursor piscante
                if int(pygame.time.get_ticks() / 500) % 2:
                    texto_valor += "|"
            
            texto = self.fonte.render(texto_valor, True, self.cor_texto)
            self.screen.blit(texto, (x_valor, y_real))
            
            # Slider
            slider_x = x_valor + largura_valor + 10
            slider_y = y_real + 5
            slider_largura = 100
            slider_altura = 16
            
            if campo.get("min") is not None and campo.get("max") is not None:
                min_val = campo["min"]
                max_val = campo["max"]
                valor_normalizado = (valor - min_val) / (max_val - min_val) if max_val > min_val else 0
                valor_normalizado = max(0, min(1, valor_normalizado))
                
                pygame.draw.rect(self.screen, (50, 50, 60), 
                               (slider_x, slider_y, slider_largura, slider_altura))
                pygame.draw.rect(self.screen, (100, 150, 200), 
                               (slider_x, slider_y, int(slider_largura * valor_normalizado), slider_altura))
                pygame.draw.rect(self.screen, (200, 200, 200), 
                               (slider_x, slider_y, slider_largura, slider_altura), 1)
        
        elif campo["tipo"] == "bool":
            texto_valor = "Sim" if valor else "Não"
            cor_valor = (100, 255, 100) if valor else (255, 100, 100)
            texto = self.fonte.render(texto_valor, True, cor_valor)
            self.screen.blit(texto, (x_valor, y_real))
        
        elif campo["tipo"] == "cor":
            if isinstance(valor, list) and len(valor) >= 3:
                cor = tuple(valor[:3])
            else:
                cor = (255, 255, 255)
            
            # Quadrado de cor
            pygame.draw.rect(self.screen, cor, (x_valor, y_real, 50, 20))
            pygame.draw.rect(self.screen, (200, 200, 200), (x_valor, y_real, 50, 20), 1)
            
            # Valores RGB
            texto_rgb = f"R:{valor[0]} G:{valor[1]} B:{valor[2]}"
            texto = self.fonte_pequena.render(texto_rgb, True, self.cor_texto_secundario)
            self.screen.blit(texto, (x_valor + 60, y_real))
        
        elif campo["tipo"] == "texto":
            texto_valor = str(valor)
            if self.campo_editando == campo:
                texto_valor = self.texto_editando
                if int(pygame.time.get_ticks() / 500) % 2:
                    texto_valor += "|"
            
            texto = self.fonte.render(texto_valor, True, self.cor_texto)
            self.screen.blit(texto, (x_valor, y_real))
    
    def processar_clique_campo(self, campo, pos):
        """Processa clique em um campo"""
        if campo["tipo"] == "numero":
            # Verificar se clicou no slider
            x = 20
            x_valor = x + 150
            largura_valor = 200
            slider_x = x_valor + largura_valor + 10
            slider_y = campo["y"] - self.scroll_y + 5
            slider_largura = 100
            
            if slider_x <= pos[0] <= slider_x + slider_largura and slider_y <= pos[1] <= slider_y + 16:
                # Clicou no slider
                valor_normalizado = (pos[0] - slider_x) / slider_largura
                valor_normalizado = max(0, min(1, valor_normalizado))
                min_val = campo.get("min", 0)
                max_val = campo.get("max", 100)
                novo_valor = int(min_val + valor_normalizado * (max_val - min_val))
                self.definir_valor(campo["caminho"], novo_valor)
                return True
            
            # Clicou no campo de texto
            x_campo = x_valor
            y_campo = campo["y"] - self.scroll_y
            if x_campo <= pos[0] <= x_campo + largura_valor and y_campo <= pos[1] <= y_campo + 24:
                self.campo_editando = campo
                self.texto_editando = str(int(self.obter_valor(campo["caminho"]) or 0))
                return True
        
        elif campo["tipo"] == "bool":
            x = 20
            x_valor = x + 150
            largura_valor = 200
            x_campo = x_valor
            y_campo = campo["y"] - self.scroll_y
            if x_campo <= pos[0] <= x_campo + largura_valor and y_campo <= pos[1] <= y_campo + 24:
                valor_atual = self.obter_valor(campo["caminho"])
                self.definir_valor(campo["caminho"], not valor_atual)
                return True
        
        elif campo["tipo"] == "cor":
            x = 20
            x_valor = x + 150
            x_campo = x_valor
            y_campo = campo["y"] - self.scroll_y
            if x_campo <= pos[0] <= x_campo + 200 and y_campo <= pos[1] <= y_campo + 24:
                # Abrir editor de cor simples (ciclar R, G, B)
                valor_atual = self.obter_valor(campo["caminho"])
                if not isinstance(valor_atual, list) or len(valor_atual) < 3:
                    valor_atual = [255, 255, 255]
                
                # Incrementar componente baseado na posição do clique
                componente = (pos[0] - x_campo) // 70
                componente = max(0, min(2, componente))
                valor_atual[componente] = (valor_atual[componente] + 32) % 256
                self.definir_valor(campo["caminho"], valor_atual)
                return True
        
        elif campo["tipo"] == "texto":
            x = 20
            x_valor = x + 150
            largura_valor = 200
            x_campo = x_valor
            y_campo = campo["y"] - self.scroll_y
            if x_campo <= pos[0] <= x_campo + largura_valor and y_campo <= pos[1] <= y_campo + 24:
                self.campo_editando = campo
                self.texto_editando = str(self.obter_valor(campo["caminho"]) or "")
                return True
        
        return False
    
    def desenhar_preview(self):
        """Desenha um preview completo do celular com todos os elementos"""
        if not self.preview_ativo:
            return
        
        x = self.preview_x
        y = self.preview_y
        
        # Obter configurações
        config_menu = self.config.get("menu", {})
        menu_largura = config_menu.get("largura", 500)
        menu_altura = config_menu.get("altura", 600)
        
        # Escalar para caber no preview (usar escala 1:1 para melhor visualização)
        escala = min(self.preview_largura / menu_largura, (self.preview_altura - 40) / menu_altura) * 0.95
        menu_largura_preview = int(menu_largura * escala)
        menu_altura_preview = int(menu_altura * escala)
        
        # Fundo do preview
        pygame.draw.rect(self.screen, (20, 20, 30), 
                        (x, y, self.preview_largura, self.preview_altura))
        pygame.draw.rect(self.screen, (100, 100, 120), 
                        (x, y, self.preview_largura, self.preview_altura), 2)
        
        # Título do preview
        titulo = self.fonte.render("PREVIEW", True, self.cor_texto)
        self.screen.blit(titulo, (x + 10, y + 10))
        
        # Menu
        menu_x_preview = x + (self.preview_largura - menu_largura_preview) // 2
        menu_y_preview = y + 40
        
        # Overlay escuro
        overlay_opacidade = self.config.get("overlay", {}).get("opacidade", 180)
        overlay_preview = pygame.Surface((menu_largura_preview, menu_altura_preview), pygame.SRCALPHA)
        overlay_preview.fill((0, 0, 0, int(overlay_opacidade * 0.7)))
        self.screen.blit(overlay_preview, (menu_x_preview, menu_y_preview))
        
        # Background da tela do celular
        if self.tela_celular_bg:
            bg_redimensionado = pygame.transform.scale(self.tela_celular_bg, (menu_largura_preview, menu_altura_preview))
            self.screen.blit(bg_redimensionado, (menu_x_preview, menu_y_preview))
        else:
            # Fallback: fundo sólido
            menu_bg = pygame.Surface((menu_largura_preview, menu_altura_preview), pygame.SRCALPHA)
            menu_bg.fill((30, 30, 40, 240))
            self.screen.blit(menu_bg, (menu_x_preview, menu_y_preview))
        
        # Borda
        config_borda = self.config.get("borda", {})
        cor_borda = tuple(config_borda.get("cor", [100, 150, 200]))
        espessura_borda = config_borda.get("espessura", 3)
        pygame.draw.rect(self.screen, cor_borda, 
                        (menu_x_preview, menu_y_preview, menu_largura_preview, menu_altura_preview), 
                        max(1, int(espessura_borda * escala)))
        
        # Função auxiliar para renderizar texto
        def render_text_preview(texto, tamanho, cor, negrito=False):
            fonte = pygame.font.Font(None, max(8, int(tamanho * escala)))
            if negrito:
                fonte.set_bold(True)
            return fonte.render(str(texto), True, cor)
        
        # Hora
        config_hora = self.config.get("hora", {})
        hora_x = menu_x_preview + int(config_hora.get("x", 20) * escala)
        hora_y = menu_y_preview + int(config_hora.get("y", 20) * escala)
        hora_tamanho = config_hora.get("tamanho_fonte", 24)
        hora_cor = tuple(config_hora.get("cor", [255, 255, 255]))
        hora_negrito = config_hora.get("negrito", True)
        hora_texto = render_text_preview("14:30", hora_tamanho, hora_cor, hora_negrito)
        self.screen.blit(hora_texto, (hora_x, hora_y))
        
        # Dia
        config_dia = self.config.get("dia", {})
        dia_x = menu_x_preview + int(config_dia.get("x", 20) * escala)
        dia_y = menu_y_preview + int(config_dia.get("y", 50) * escala)
        dia_tamanho = config_dia.get("tamanho_fonte", 18)
        dia_cor = tuple(config_dia.get("cor", [200, 200, 200]))
        dia_negrito = config_dia.get("negrito", False)
        # Usar formato de data correto (DD/MM/YYYY)
        try:
            from datetime import date
            data_exemplo = date(1990, 12, 5)
            dia_formatado = data_exemplo.strftime("%d/%m/%Y")
        except:
            dia_formatado = "05/12/1990"
        dia_texto = render_text_preview(dia_formatado, dia_tamanho, dia_cor, dia_negrito)
        self.screen.blit(dia_texto, (dia_x, dia_y))
        
        # Status
        config_status = self.config.get("status", {})
        config_titulo_status = config_status.get("titulo", {})
        status_y_offset = config_titulo_status.get("y_offset", 80)
        status_y_preview = menu_y_preview + int(status_y_offset * escala)
        status_titulo_x = menu_x_preview + int(config_titulo_status.get("x", 20) * escala)
        status_titulo_tamanho = config_titulo_status.get("tamanho_fonte", 18)
        status_titulo_cor = tuple(config_titulo_status.get("cor", [255, 200, 0]))
        status_titulo_negrito = config_titulo_status.get("negrito", True)
        
        status_titulo = render_text_preview("STATUS", status_titulo_tamanho, status_titulo_cor, status_titulo_negrito)
        self.screen.blit(status_titulo, (status_titulo_x, status_y_preview))
        
        # Barras de status (valores simulados)
        espacamento_linhas = config_status.get("espacamento_linhas", 25)
        barra_altura = config_status.get("barra_altura", 10)
        barra_largura_offset = config_status.get("barra_largura_offset", 60)
        barra_espacamento = config_status.get("barra_espacamento", 15)
        barra_x_offset = config_status.get("barra_x_offset", 20)
        barra_y_offset_base = config_status.get("barra_y_offset_base", 42)
        texto_x_offset = config_status.get("texto_x_offset", 20)
        texto_y_offset_base = config_status.get("texto_y_offset_base", 25)
        
        status_valores = [
            ("Reputação", 75, (255, 255, 0)),  # 75%
            ("Fome", 60, (0, 255, 0)),        # 60%
            ("Sono", 45, (100, 150, 255)),     # 45%
            ("Tédio", 30, (255, 150, 0))       # 30%
        ]
        
        for i, (nome, valor, cor) in enumerate(status_valores):
            # Texto do status usando offset configurável
            texto_y = status_y_preview + int((texto_y_offset_base + espacamento_linhas * i) * escala)
            texto_x = menu_x_preview + int(texto_x_offset * escala)
            status_texto = render_text_preview(f"{nome}: {valor}%", 14, cor, False)
            self.screen.blit(status_texto, (texto_x, texto_y))
            
            # Barra de status usando offset configurável
            barra_y = status_y_preview + int((barra_y_offset_base + espacamento_linhas * i) * escala)
            barra_largura = menu_largura_preview - int(barra_largura_offset * escala)
            barra_x = menu_x_preview + int(barra_x_offset * escala)
            barra_altura_scaled = int(barra_altura * escala)
            
            # Fundo da barra
            pygame.draw.rect(self.screen, (30, 30, 30), 
                           (barra_x, barra_y, barra_largura, barra_altura_scaled))
            # Preenchimento da barra
            preenchimento = int(barra_largura * (valor / 100))
            pygame.draw.rect(self.screen, cor, 
                           (barra_x, barra_y, preenchimento, barra_altura_scaled))
            # Borda da barra
            pygame.draw.rect(self.screen, (200, 200, 200), 
                           (barra_x, barra_y, barra_largura, barra_altura_scaled), 1)
        
        # Menu de opções
        config_menu_opcoes = self.config.get("menu_opcoes", {})
        inicio_y_offset = config_menu_opcoes.get("inicio_y_offset", 180)
        altura_opcao = config_menu_opcoes.get("altura_opcao", 35)
        espacamento = config_menu_opcoes.get("espacamento", 0)
        opcao_x = menu_x_preview + int(config_menu_opcoes.get("x", 40) * escala)
        opcao_y_padding = int(config_menu_opcoes.get("y_padding", 8) * escala)
        
        opcoes = ["Missões", "Progresso", "Mensagens", "Saldo", "Corridas"]
        inicio_y_opcoes = menu_y_preview + int(inicio_y_offset * escala)
        
        for i, opcao in enumerate(opcoes):
            opcao_y = inicio_y_opcoes + int((altura_opcao + espacamento) * i * escala)
            
            # Destaque se selecionada (primeira opção)
            if i == 0:
                destaque_largura = menu_largura_preview - int(40 * escala)
                destaque_altura = int((altura_opcao - 5) * escala)
                destaque = pygame.Surface((destaque_largura, destaque_altura), pygame.SRCALPHA)
                destaque.fill((100, 150, 200, 100))
                self.screen.blit(destaque, (menu_x_preview + int(20 * escala), opcao_y))
            
            # Texto da opção
            cor_texto_opcao = (255, 255, 255) if i == 0 else (200, 200, 200)
            opcao_texto = render_text_preview(opcao, 18, cor_texto_opcao, i == 0)
            self.screen.blit(opcao_texto, (opcao_x, opcao_y + opcao_y_padding))
        
        # Botão voltar
        config_voltar = self.config.get("voltar", {})
        voltar_x = menu_x_preview + menu_largura_preview + int(config_voltar.get("x_offset", -150) * escala)
        voltar_y = menu_y_preview + menu_altura_preview + int(config_voltar.get("y_offset", -30) * escala)
        voltar_tamanho = config_voltar.get("tamanho_fonte", 16)
        voltar_cor = tuple(config_voltar.get("cor", [200, 200, 200]))
        voltar_negrito = config_voltar.get("negrito", False)
        voltar_texto = render_text_preview("ESC - Voltar", voltar_tamanho, voltar_cor, voltar_negrito)
        self.screen.blit(voltar_texto, (voltar_x, voltar_y))
    
    def desenhar_botoes(self):
        """Desenha os botões de ação"""
        y_botao = self.altura_tela - 50
        x_botao = 20
        largura_botao = 120
        altura_botao = 35
        
        # Botão Salvar
        mouse_pos = pygame.mouse.get_pos()
        hover_salvar = (x_botao <= mouse_pos[0] <= x_botao + largura_botao and 
                       y_botao <= mouse_pos[1] <= y_botao + altura_botao)
        
        cor_botao = self.cor_botao_hover if hover_salvar else self.cor_botao
        pygame.draw.rect(self.screen, cor_botao, (x_botao, y_botao, largura_botao, altura_botao))
        pygame.draw.rect(self.screen, (200, 200, 200), (x_botao, y_botao, largura_botao, altura_botao), 2)
        
        texto_salvar = self.fonte.render("Salvar (F5)", True, self.cor_texto)
        self.screen.blit(texto_salvar, (x_botao + 10, y_botao + 8))
        
        # Botão Carregar
        x_botao_carregar = x_botao + largura_botao + 10
        hover_carregar = (x_botao_carregar <= mouse_pos[0] <= x_botao_carregar + largura_botao and 
                         y_botao <= mouse_pos[1] <= y_botao + altura_botao)
        
        cor_botao = self.cor_botao_hover if hover_carregar else self.cor_botao
        pygame.draw.rect(self.screen, cor_botao, (x_botao_carregar, y_botao, largura_botao, altura_botao))
        pygame.draw.rect(self.screen, (200, 200, 200), (x_botao_carregar, y_botao, largura_botao, altura_botao), 2)
        
        texto_carregar = self.fonte.render("Carregar (F6)", True, self.cor_texto)
        self.screen.blit(texto_carregar, (x_botao_carregar + 10, y_botao + 8))
        
        # Botão Reset
        x_botao_reset = x_botao_carregar + largura_botao + 10
        hover_reset = (x_botao_reset <= mouse_pos[0] <= x_botao_reset + largura_botao and 
                      y_botao <= mouse_pos[1] <= y_botao + altura_botao)
        
        cor_botao = self.cor_botao_hover if hover_reset else self.cor_botao
        pygame.draw.rect(self.screen, cor_botao, (x_botao_reset, y_botao, largura_botao, altura_botao))
        pygame.draw.rect(self.screen, (200, 200, 200), (x_botao_reset, y_botao, largura_botao, altura_botao), 2)
        
        texto_reset = self.fonte.render("Reset", True, self.cor_texto)
        self.screen.blit(texto_reset, (x_botao_reset + 10, y_botao + 8))
        
        return {
            "salvar": (x_botao, y_botao, largura_botao, altura_botao),
            "carregar": (x_botao_carregar, y_botao, largura_botao, altura_botao),
            "reset": (x_botao_reset, y_botao, largura_botao, altura_botao)
        }
    
    def processar_eventos(self):
        """Processa eventos do editor"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return False
                elif evento.key == pygame.K_F5:
                    self.salvar_config()
                elif evento.key == pygame.K_F6:
                    self.config = self.carregar_config()
                    self.preparar_campos()
                elif evento.key == pygame.K_UP:
                    self.scroll_y = max(0, self.scroll_y - 20)
                elif evento.key == pygame.K_DOWN:
                    self.scroll_y += 20
                elif evento.key == pygame.K_RETURN:
                    if self.campo_editando:
                        # Aplicar valor editado
                        try:
                            if self.campo_editando["tipo"] == "numero":
                                valor = int(self.texto_editando)
                                if "min" in self.campo_editando:
                                    valor = max(self.campo_editando["min"], 
                                              min(self.campo_editando["max"], valor))
                                self.definir_valor(self.campo_editando["caminho"], valor)
                            elif self.campo_editando["tipo"] == "texto":
                                self.definir_valor(self.campo_editando["caminho"], self.texto_editando)
                        except ValueError:
                            pass
                        self.campo_editando = None
                        self.texto_editando = ""
                elif self.campo_editando:
                    if evento.key == pygame.K_BACKSPACE:
                        self.texto_editando = self.texto_editando[:-1]
                    else:
                        self.texto_editando += evento.unicode
            
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # Clique esquerdo
                    pos = evento.pos
                    
                    # Verificar botões
                    botoes = self.desenhar_botoes()
                    if (botoes["salvar"][0] <= pos[0] <= botoes["salvar"][0] + botoes["salvar"][2] and
                        botoes["salvar"][1] <= pos[1] <= botoes["salvar"][1] + botoes["salvar"][3]):
                        self.salvar_config()
                    elif (botoes["carregar"][0] <= pos[0] <= botoes["carregar"][0] + botoes["carregar"][2] and
                          botoes["carregar"][1] <= pos[1] <= botoes["carregar"][1] + botoes["carregar"][3]):
                        self.config = self.carregar_config()
                        self.preparar_campos()
                    elif (botoes["reset"][0] <= pos[0] <= botoes["reset"][0] + botoes["reset"][2] and
                          botoes["reset"][1] <= pos[1] <= botoes["reset"][1] + botoes["reset"][3]):
                        self.config = json.loads(json.dumps(self.config_original))
                        self.preparar_campos()
                    else:
                        # Verificar campos
                        for campo in self.campos:
                            if campo["tipo"] != "titulo":
                                y_real = campo["y"] - self.scroll_y
                                if 0 <= y_real <= self.altura_tela - 100:
                                    if self.processar_clique_campo(campo, pos):
                                        self.campo_selecionado = campo
                                        break
                
                elif evento.button == 4:  # Scroll up
                    self.scroll_y = max(0, self.scroll_y - 20)
                elif evento.button == 5:  # Scroll down
                    self.scroll_y += 20
        
        return True
    
    def executar(self):
        """Loop principal do editor"""
        rodando = True
        
        while rodando:
            rodando = self.processar_eventos()
            
            # Desenhar
            self.screen.fill(self.cor_fundo)
            
            # Painel esquerdo (campos)
            pygame.draw.rect(self.screen, self.cor_painel, (0, 0, 750, self.altura_tela))
            
            # Desenhar campos
            for campo in self.campos:
                y_real = campo["y"] - self.scroll_y
                if -50 <= y_real <= self.altura_tela - 50:
                    self.desenhar_campo(campo, y_real)
            
            # Desenhar preview
            self.desenhar_preview()
            
            # Desenhar botões
            self.desenhar_botoes()
            
            # Instruções
            instrucoes = [
                "F5: Salvar | F6: Carregar | ESC: Sair",
                "Clique nos campos para editar | Use sliders para ajustar valores"
            ]
            y_inst = self.altura_tela - 90
            for i, instrucao in enumerate(instrucoes):
                texto = self.fonte_pequena.render(instrucao, True, self.cor_texto_secundario)
                self.screen.blit(texto, (20, y_inst + i * 20))
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    editor = CelularEditor()
    editor.executar()

