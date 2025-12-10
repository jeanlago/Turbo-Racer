"""Sistema de Celular - Interface para missões, progresso, mensagens e corridas"""
import pygame
import os
import math
import json
from config import DIR_PROJETO, LARGURA, ALTURA

CAMINHO_SPRITE_CELULAR = os.path.join(DIR_PROJETO, "assets", "images", "hud", "celular.png")
CAMINHO_TELA_CELULAR = os.path.join(DIR_PROJETO, "assets", "images", "ui", "tela_celular.png")
CAMINHO_CONFIG_CELULAR = os.path.join(DIR_PROJETO, "data", "celular_config.json")

class Celular:
    """Celular que aparece no canto inferior direito durante a campanha"""
    
    def __init__(self):
        self.sprite_original = None
        self.sprite_atual = None
        self.carregado = False
        
        self.largura_base = 80
        self.altura_base = 120
        self.pos_x = LARGURA - self.largura_base - 20
        self.pos_y = ALTURA - self.altura_base - 20
        
        self.visivel = False
        self.menu_aberto = False
        self.hover = False
        
        self.tempo_animacao = 0.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.escala = 1.0
        
        self.opcao_selecionada = 0
        self.menu_opcoes = [
            "Missões",
            "Progresso",
            "Mensagens",
            "Saldo",
            "Corridas"
        ]
        
        self.tela_atual = "menu"
        
        self.botao_pagar_divida_rect = None
        
        self.tela_celular_bg = None
        
        self.config = self.carregar_config()
        
        self.carregar_sprite()
        self.carregar_tela_celular()
    
    def carregar_sprite(self):
        """Carrega o sprite do celular"""
        try:
            if os.path.exists(CAMINHO_SPRITE_CELULAR):
                self.sprite_original = pygame.image.load(CAMINHO_SPRITE_CELULAR).convert_alpha()
                self.sprite_original = pygame.transform.scale(
                    self.sprite_original, 
                    (self.largura_base, self.altura_base)
                )
                self.sprite_atual = self.sprite_original.copy()
                self.carregado = True
                print(f"[CELULAR] Sprite carregado: {CAMINHO_SPRITE_CELULAR}")
            else:
                print(f"[CELULAR] ERRO: Sprite não encontrado: {CAMINHO_SPRITE_CELULAR}")
                self.sprite_original = pygame.Surface((self.largura_base, self.altura_base), pygame.SRCALPHA)
                pygame.draw.rect(self.sprite_original, (100, 100, 100), (0, 0, self.largura_base, self.altura_base))
                pygame.draw.rect(self.sprite_original, (200, 200, 200), (5, 5, self.largura_base-10, self.altura_base-10))
                self.sprite_atual = self.sprite_original.copy()
                self.carregado = True
        except Exception as e:
            print(f"[CELULAR] Erro ao carregar sprite: {e}")
            self.carregado = False
    
    def carregar_config(self):
        """Carrega as configurações do celular do arquivo JSON"""
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
                "barra_espacamento": 15
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
            if os.path.exists(CAMINHO_CONFIG_CELULAR):
                with open(CAMINHO_CONFIG_CELULAR, 'r', encoding='utf-8') as f:
                    config_carregada = json.load(f)
                    config = config_padrao.copy()
                    for key, value in config_carregada.items():
                        if isinstance(value, dict) and key in config:
                            config[key].update(value)
                        else:
                            config[key] = value
                    print(f"[CELULAR] Configurações carregadas de: {CAMINHO_CONFIG_CELULAR}")
                    return config
            else:
                print(f"[CELULAR] Arquivo de configuração não encontrado, usando padrões. Crie {CAMINHO_CONFIG_CELULAR} para personalizar.")
                return config_padrao
        except Exception as e:
            print(f"[CELULAR] Erro ao carregar configurações: {e}")
            return config_padrao
    
    def carregar_tela_celular(self):
        """Carrega o background da tela do celular"""
        try:
            if os.path.exists(CAMINHO_TELA_CELULAR):
                self.tela_celular_bg = pygame.image.load(CAMINHO_TELA_CELULAR).convert_alpha()
                print(f"[CELULAR] Background da tela carregado: {CAMINHO_TELA_CELULAR}")
            else:
                print(f"[CELULAR] AVISO: Background da tela não encontrado: {CAMINHO_TELA_CELULAR}")
                self.tela_celular_bg = None
        except Exception as e:
            print(f"[CELULAR] Erro ao carregar background da tela: {e}")
            self.tela_celular_bg = None
    
    def verificar_visibilidade(self, modo_arcade=False, em_corrida=False, cutscene_ativa=False):
        """Verifica se o celular deve estar visível"""
        self.visivel = not modo_arcade and not em_corrida and not cutscene_ativa
    
    def atualizar(self, dt, mouse_pos=None):
        """Atualiza o estado do celular"""
        if not self.visivel or not self.carregado:
            return
        
        rect_celular = pygame.Rect(
            self.pos_x + self.offset_x,
            self.pos_y + self.offset_y,
            self.largura_base * self.escala,
            self.altura_base * self.escala
        )
        
        hover_anterior = self.hover
        if mouse_pos:
            self.hover = rect_celular.collidepoint(mouse_pos)
        else:
            self.hover = False
        
        if self.hover:
            self.tempo_animacao += dt * 10.0
            self.offset_x = math.sin(self.tempo_animacao * 2.0) * 3.0
            self.escala = 1.0 + 0.1 * (1.0 + math.sin(self.tempo_animacao * 1.5)) / 2.0
        else:
            self.offset_x = self.offset_x * 0.9
            self.escala = 1.0 + (self.escala - 1.0) * 0.9
            if abs(self.offset_x) < 0.1:
                self.offset_x = 0.0
            if abs(self.escala - 1.0) < 0.01:
                self.escala = 1.0
                self.tempo_animacao = 0.0
        
        if self.sprite_original:
            nova_largura = int(self.largura_base * self.escala)
            nova_altura = int(self.altura_base * self.escala)
            self.sprite_atual = pygame.transform.scale(self.sprite_original, (nova_largura, nova_altura))
    
    def processar_clique(self, pos):
        """Processa clique no celular"""
        if not self.visivel or not self.carregado:
            return False
        
        rect_celular = pygame.Rect(
            self.pos_x + self.offset_x,
            self.pos_y + self.offset_y,
            self.largura_base * self.escala,
            self.altura_base * self.escala
        )
        
        if rect_celular.collidepoint(pos):
            print(f"[CELULAR] Celular clicado! Abrindo menu...")
            self.menu_aberto = True
            self.tela_atual = "menu"
            self.opcao_selecionada = 0
            print(f"[CELULAR] menu_aberto={self.menu_aberto}, tela_atual={self.tela_atual}, visivel={self.visivel}")
            return True
        
        return False
    
    def _processar_clique_menu(self, pos):
        """Processa clique dentro do menu"""
        menu_largura = 500
        menu_altura = 600
        menu_x = LARGURA // 2 - menu_largura // 2
        menu_y = ALTURA // 2 - menu_altura // 2
        
        menu_rect = pygame.Rect(menu_x, menu_y, menu_largura, menu_altura)
        if not menu_rect.collidepoint(pos):
            self.menu_aberto = False
            self.tela_atual = "menu"
            return "fechado"
        
        if self.tela_atual == "menu":
            return self._processar_clique_menu_opcoes(pos)
        
        return None
    
    def processar_eventos(self, eventos):
        """Processa eventos do celular"""
        if not self.visivel or not self.menu_aberto:
            return None
        
        for evento in eventos:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.menu_aberto = False
                    self.tela_atual = "menu"
                    return "fechado"
                elif evento.key == pygame.K_UP or evento.key == pygame.K_w:
                    self.opcao_selecionada = (self.opcao_selecionada - 1) % len(self.menu_opcoes)
                elif evento.key == pygame.K_DOWN or evento.key == pygame.K_s:
                    self.opcao_selecionada = (self.opcao_selecionada + 1) % len(self.menu_opcoes)
                elif evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                    return self._abrir_tela_selecionada()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    if self.botao_pagar_divida_rect and self.botao_pagar_divida_rect.collidepoint(evento.pos):
                        return self._processar_pagamento_divida()
                    
                    resultado = self._processar_clique_menu(evento.pos)
                    if resultado:
                        return resultado
        
        return None
    
    def _abrir_tela_selecionada(self):
        """Abre a tela selecionada no menu"""
        opcao = self.menu_opcoes[self.opcao_selecionada]
        if opcao == "Missões":
            self.tela_atual = "missoes"
        elif opcao == "Progresso":
            self.tela_atual = "progresso"
        elif opcao == "Mensagens":
            self.tela_atual = "mensagens"
        elif opcao == "Saldo":
            self.tela_atual = "saldo"
        elif opcao == "Corridas":
            self.tela_atual = "corridas"
        return "tela_aberta"
    
    def _processar_clique_menu_opcoes(self, pos):
        """Processa clique nas opções do menu"""
        menu_x = LARGURA // 2 - 200
        menu_y = ALTURA // 2 - 150
        opcao_altura = 40
        
        for i, opcao in enumerate(self.menu_opcoes):
            opcao_y = menu_y + 60 + (i * opcao_altura)
            opcao_rect = pygame.Rect(menu_x, opcao_y, 400, opcao_altura)
            if opcao_rect.collidepoint(pos):
                self.opcao_selecionada = i
                return self._abrir_tela_selecionada()
        
        return None
    
    def desenhar(self, tela):
        """Desenha o celular na tela"""
        if not self.visivel or not self.carregado:
            return
        
        if self.sprite_atual:
            tela.blit(
                self.sprite_atual,
                (self.pos_x + self.offset_x, self.pos_y + self.offset_y)
            )
        
        if self.menu_aberto:
            print(f"[CELULAR] Desenhando menu... menu_aberto={self.menu_aberto}, tela_atual={self.tela_atual}")
            self._desenhar_menu(tela)
    
    def _desenhar_menu(self, tela):
        """Desenha o menu do celular"""
        from core.menu import render_text
        
        config_menu = self.config.get("menu", {})
        menu_largura = config_menu.get("largura", 500)
        menu_altura = config_menu.get("altura", 600)
        
        menu_x_config = config_menu.get("x", "centro")
        menu_y_config = config_menu.get("y", "centro")
        
        if menu_x_config == "centro":
            menu_x = LARGURA // 2 - menu_largura // 2
        else:
            menu_x = menu_x_config
        
        if menu_y_config == "centro":
            menu_y = ALTURA // 2 - menu_altura // 2
        else:
            menu_y = menu_y_config
        
        menu_x += config_menu.get("offset_x", 0)
        menu_y += config_menu.get("offset_y", 0)
        
        overlay_opacidade = self.config.get("overlay", {}).get("opacidade", 180)
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, overlay_opacidade))
        tela.blit(overlay, (0, 0))
        
        if self.tela_celular_bg:
            bg_redimensionado = pygame.transform.scale(self.tela_celular_bg, (menu_largura, menu_altura))
            tela.blit(bg_redimensionado, (menu_x, menu_y))
        else:
            menu_bg = pygame.Surface((menu_largura, menu_altura), pygame.SRCALPHA)
            menu_bg.fill((30, 30, 40, 240))
            tela.blit(menu_bg, (menu_x, menu_y))
        
        config_titulo = self.config.get("titulo", {})
            titulo_x = menu_x + config_titulo.get("x", 20)
            titulo_y = menu_y + config_titulo.get("y", 20)
            titulo_tamanho = config_titulo.get("tamanho_fonte", 28)
            titulo_cor = tuple(config_titulo.get("cor", [255, 255, 255]))
            titulo_negrito = config_titulo.get("negrito", True)
            titulo = render_text("CELULAR", titulo_tamanho, titulo_cor, bold=titulo_negrito, pixel_style=True)
            tela.blit(titulo, (titulo_x, titulo_y))
        
        if self.tela_atual == "menu":
            self._desenhar_menu_principal(tela, menu_x, menu_y, menu_largura, menu_altura)
        elif self.tela_atual == "missoes":
            self._desenhar_tela_missoes(tela, menu_x, menu_y, menu_largura, menu_altura)
        elif self.tela_atual == "progresso":
            self._desenhar_tela_progresso(tela, menu_x, menu_y, menu_largura, menu_altura)
        elif self.tela_atual == "mensagens":
            self._desenhar_tela_mensagens(tela, menu_x, menu_y, menu_largura, menu_altura)
        elif self.tela_atual == "saldo":
            self._desenhar_tela_saldo(tela, menu_x, menu_y, menu_largura, menu_altura)
        elif self.tela_atual == "corridas":
            self._desenhar_tela_corridas(tela, menu_x, menu_y, menu_largura, menu_altura)
        
        config_voltar = self.config.get("voltar", {})
        voltar_x = menu_x + menu_largura + config_voltar.get("x_offset", -150)
        voltar_y = menu_y + menu_altura + config_voltar.get("y_offset", -30)
        voltar_tamanho = config_voltar.get("tamanho_fonte", 16)
        voltar_cor = tuple(config_voltar.get("cor", [200, 200, 200]))
        voltar_negrito = config_voltar.get("negrito", False)
        voltar_texto = render_text("ESC - Voltar", voltar_tamanho, voltar_cor, bold=voltar_negrito, pixel_style=True)
        tela.blit(voltar_texto, (voltar_x, voltar_y))
    
    def _processar_pagamento_divida(self):
        """Processa o pagamento da dívida do Barão"""
        from core.progresso import gerenciador_progresso
        from core.popup_musica import popup_musica
        
        if not gerenciador_progresso.barao_emprestimo_ativo:
            popup_musica.mostrar("Você não tem dívidas pendentes.", tipo="outra")
            return None
        
        valor_devido = gerenciador_progresso.barao_valor_devido
        dinheiro = gerenciador_progresso.dinheiro
        
        if dinheiro < valor_devido:
            falta = valor_devido - dinheiro
            popup_musica.mostrar(f"Você não tem dinheiro suficiente. Faltam ${falta:,}.", tipo="outra")
            return None
        
        # Processar pagamento
        gerenciador_progresso.remover_dinheiro(valor_devido)
        gerenciador_progresso.barao_emprestimo_ativo = False
        gerenciador_progresso.barao_valor_devido = 0
        gerenciador_progresso.barao_corridas_restantes = 0
        gerenciador_progresso.salvar()
        
        popup_musica.mostrar(f"Dívida de ${valor_devido:,} paga com sucesso! O Barão está satisfeito.", tipo="outra")
        
        # Limpar retângulo do botão
        self.botao_pagar_divida_rect = None
        
        return None
    
    def _desenhar_menu_principal(self, tela, x, y, largura, altura):
        """Desenha o menu principal"""
        from core.menu import render_text
        from core.progresso import gerenciador_progresso
        
        config_status = self.config.get("status", {})
        config_titulo_status = config_status.get("titulo", {})
        status_y = y + config_titulo_status.get("y_offset", 80)
        status_titulo_x = x + config_titulo_status.get("x", 20)
        status_titulo_tamanho = config_titulo_status.get("tamanho_fonte", 18)
        status_titulo_cor = tuple(config_titulo_status.get("cor", [255, 200, 0]))
        status_titulo_negrito = config_titulo_status.get("negrito", True)
        
        status_titulo = render_text("STATUS", status_titulo_tamanho, status_titulo_cor, bold=status_titulo_negrito, pixel_style=True)
        tela.blit(status_titulo, (status_titulo_x, status_y))
        
        try:
            from core.status_jogador import status_jogador
            popularidade = status_jogador.popularidade
            fome = status_jogador.fome
            sono = status_jogador.sono
            tedio = status_jogador.tedio
            dinheiro = gerenciador_progresso.dinheiro
            
            print(f"[CELULAR] Status: popularidade={popularidade}, fome={fome}, sono={sono}, tedio={tedio}, dinheiro={dinheiro}")
            
            config_status = self.config.get("status", {})
            barra_altura = config_status.get("barra_altura", 10)
            barra_largura_offset = config_status.get("barra_largura_offset", 60)
            barra_x_offset = config_status.get("barra_x_offset", 20)
            barra_y_offset_base = config_status.get("barra_y_offset_base", 42)
            texto_x_offset = config_status.get("texto_x_offset", 20)
            texto_y_offset_base = config_status.get("texto_y_offset_base", 25)
            
            pop_porcentagem = min(100, (popularidade / 500) * 100)
            pop_texto = render_text(f"Reputação: {popularidade:.0f}/500 ({pop_porcentagem:.1f}%)", 14, (255, 255, 0), bold=False, pixel_style=True)
            tela.blit(pop_texto, (x + texto_x_offset, status_y + texto_y_offset_base))
            
            pop_barra_x = x + barra_x_offset
            pop_barra_y = status_y + barra_y_offset_base
            pop_barra_largura = largura - barra_largura_offset
            pop_barra_altura = barra_altura
            pop_preenchimento = int(pop_barra_largura * (pop_porcentagem / 100))
            pygame.draw.rect(tela, (30, 30, 30), (pop_barra_x, pop_barra_y, pop_barra_largura, pop_barra_altura))
            pygame.draw.rect(tela, (255, 255, 0), (pop_barra_x, pop_barra_y, pop_preenchimento, pop_barra_altura))
            pygame.draw.rect(tela, (200, 200, 200), (pop_barra_x, pop_barra_y, pop_barra_largura, pop_barra_altura), 1)
            
            espacamento_linhas = config_status.get("espacamento_linhas", 25)
            cor_fome = (0, 255, 0) if fome > 50 else (255, 200, 0) if fome > 25 else (255, 0, 0)
            fome_texto = render_text(f"Fome: {fome:.0f}%", 14, cor_fome, bold=False, pixel_style=True)
            tela.blit(fome_texto, (x + texto_x_offset, status_y + texto_y_offset_base + espacamento_linhas))
            
            fome_barra_x = x + barra_x_offset
            fome_barra_y = status_y + barra_y_offset_base + espacamento_linhas
            fome_barra_largura = largura - barra_largura_offset
            fome_barra_altura = barra_altura
            fome_preenchimento = int(fome_barra_largura * (fome / 100))
            pygame.draw.rect(tela, (30, 30, 30), (fome_barra_x, fome_barra_y, fome_barra_largura, fome_barra_altura))
            pygame.draw.rect(tela, cor_fome, (fome_barra_x, fome_barra_y, fome_preenchimento, fome_barra_altura))
            pygame.draw.rect(tela, (200, 200, 200), (fome_barra_x, fome_barra_y, fome_barra_largura, fome_barra_altura), 1)
            
            cor_sono = (100, 150, 255) if sono > 50 else (255, 200, 0) if sono > 25 else (255, 0, 0)
            sono_texto = render_text(f"Sono: {sono:.0f}%", 14, cor_sono, bold=False, pixel_style=True)
            tela.blit(sono_texto, (x + texto_x_offset, status_y + texto_y_offset_base + espacamento_linhas * 2))
            
            sono_barra_x = x + barra_x_offset
            sono_barra_y = status_y + barra_y_offset_base + espacamento_linhas * 2
            sono_barra_largura = largura - barra_largura_offset
            sono_barra_altura = barra_altura
            sono_preenchimento = int(sono_barra_largura * (sono / 100))
            pygame.draw.rect(tela, (30, 30, 30), (sono_barra_x, sono_barra_y, sono_barra_largura, sono_barra_altura))
            pygame.draw.rect(tela, cor_sono, (sono_barra_x, sono_barra_y, sono_preenchimento, sono_barra_altura))
            pygame.draw.rect(tela, (200, 200, 200), (sono_barra_x, sono_barra_y, sono_barra_largura, sono_barra_altura), 1)
            
            tedio_texto = render_text(f"Tédio: {tedio:.0f}%", 14, (150, 150, 150), bold=False, pixel_style=True)
            tela.blit(tedio_texto, (x + texto_x_offset, status_y + texto_y_offset_base + espacamento_linhas * 3))
            
            tedio_barra_x = x + barra_x_offset
            tedio_barra_y = status_y + barra_y_offset_base + espacamento_linhas * 3
            tedio_barra_largura = largura - barra_largura_offset
            tedio_barra_altura = barra_altura
            tedio_preenchimento = int(tedio_barra_largura * (tedio / 100))
            pygame.draw.rect(tela, (30, 30, 30), (tedio_barra_x, tedio_barra_y, tedio_barra_largura, tedio_barra_altura))
            pygame.draw.rect(tela, (150, 150, 150), (tedio_barra_x, tedio_barra_y, tedio_preenchimento, tedio_barra_altura))
            pygame.draw.rect(tela, (200, 200, 200), (tedio_barra_x, tedio_barra_y, tedio_barra_largura, tedio_barra_altura), 1)
            
            dinheiro_texto = render_text(f"Dinheiro: ${dinheiro:,}", 14, (0, 255, 0), bold=False, pixel_style=True)
            tela.blit(dinheiro_texto, (x + 20, status_y + 157))
            
            divida_y = status_y + 180
            if gerenciador_progresso.barao_emprestimo_ativo:
                valor_devido = gerenciador_progresso.barao_valor_devido
                corridas_restantes = gerenciador_progresso.barao_corridas_restantes
                
                divida_titulo = render_text("DÍVIDA DO BARÃO", 16, (255, 100, 100), bold=True, pixel_style=True)
                tela.blit(divida_titulo, (x + 20, divida_y))
                
                valor_texto = render_text(f"Valor devido: ${valor_devido:,}", 14, (255, 200, 200), bold=False, pixel_style=True)
                tela.blit(valor_texto, (x + 20, divida_y + 25))
                
                if corridas_restantes > 0:
                    corridas_texto = render_text(f"Corridas restantes: {corridas_restantes}", 14, (255, 200, 200), bold=False, pixel_style=True)
                else:
                    corridas_texto = render_text("PRAZO VENCIDO!", 14, (255, 0, 0), bold=True, pixel_style=True)
                tela.blit(corridas_texto, (x + 20, divida_y + 45))
                
                if dinheiro >= valor_devido:
                    botao_pagar_y = divida_y + 70
                    botao_pagar_rect = pygame.Rect(x + 20, botao_pagar_y, largura - 40, 35)
                    
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    hover = botao_pagar_rect.collidepoint(mouse_x, mouse_y)
                    
                    cor_botao = (100, 200, 100) if hover else (80, 180, 80)
                    pygame.draw.rect(tela, cor_botao, botao_pagar_rect)
                    pygame.draw.rect(tela, (200, 200, 200), botao_pagar_rect, 2)
                    
                    botao_texto = render_text(f"PAGAR DÍVIDA (${valor_devido:,})", 14, (255, 255, 255), bold=True, pixel_style=True)
                    texto_x = botao_pagar_rect.centerx - botao_texto.get_width() // 2
                    texto_y = botao_pagar_rect.centery - botao_texto.get_height() // 2
                    tela.blit(botao_texto, (texto_x, texto_y))
                    
                    self.botao_pagar_divida_rect = botao_pagar_rect
                else:
                    falta = valor_devido - dinheiro
                    falta_texto = render_text(f"Faltam ${falta:,} para pagar", 12, (200, 100, 100), bold=False, pixel_style=True)
                    tela.blit(falta_texto, (x + 20, divida_y + 70))
                    self.botao_pagar_divida_rect = None
                
                inicio_y = divida_y + 110
            else:
                self.botao_pagar_divida_rect = None
                inicio_y = status_y + 180
        except Exception as e:
            print(f"[CELULAR] Erro ao obter status do jogador: {e}")
            import traceback
            traceback.print_exc()
            # Mostrar mensagem de erro
            erro_texto = render_text("Erro ao carregar status", 14, (255, 0, 0), bold=False, pixel_style=True)
            tela.blit(erro_texto, (x + 20, status_y + 25))
            self.botao_pagar_divida_rect = None
            inicio_y = status_y + 180
        
        config_menu_opcoes = self.config.get("menu_opcoes", {})
        opcao_altura = config_menu_opcoes.get("altura_opcao", 34)
        espacamento = config_menu_opcoes.get("espacamento", 4)
        opcao_x = x + config_menu_opcoes.get("x", 55)
        opcao_y_padding = config_menu_opcoes.get("y_padding", 5)
        if gerenciador_progresso.barao_emprestimo_ativo:
            inicio_y_opcoes = inicio_y + 20
        else:
            inicio_y_opcoes = inicio_y + 20
        
        altura_total_opcoes = len(self.menu_opcoes) * (opcao_altura + espacamento)
        altura_maxima_menu = altura - (inicio_y_opcoes - y) - 20
        
        if altura_total_opcoes > altura_maxima_menu:
            inicio_y_opcoes = y + altura - altura_total_opcoes - 20
        
        for i, opcao in enumerate(self.menu_opcoes):
            opcao_y = inicio_y_opcoes + (i * (opcao_altura + espacamento))
            
            if opcao_y + opcao_altura > y + altura:
                break
            
            if i == self.opcao_selecionada:
                destaque = pygame.Surface((largura - 40, opcao_altura - 5), pygame.SRCALPHA)
                destaque.fill((100, 150, 200, 100))
                tela.blit(destaque, (x + 20, opcao_y))
            
            cor = (255, 255, 255) if i == self.opcao_selecionada else (200, 200, 200)
            texto = render_text(opcao, 18, cor, bold=(i == self.opcao_selecionada), pixel_style=True)
            tela.blit(texto, (opcao_x, opcao_y + opcao_y_padding))
    
    def _desenhar_tela_missoes(self, tela, x, y, largura, altura):
        """Desenha a tela de missões"""
        from core.menu import render_text
        from core.missoes import gerenciador_missoes
        
        titulo = render_text("MISSÕES", 24, (255, 255, 0), bold=True, pixel_style=True)
        tela.blit(titulo, (x + 20, y + 60))
        
        missao = gerenciador_missoes.obter_missao_ativa()
        if missao:
            nome_missao = gerenciador_missoes.obter_nome_missao()
            nome = render_text(f"Nome: {nome_missao}", 18, (255, 255, 255), bold=True, pixel_style=True)
            tela.blit(nome, (x + 20, y + 100))
            
            objetivo = gerenciador_missoes.obter_objetivo_missao()
            objetivo_texto = render_text(f"Objetivo: {objetivo}", 16, (200, 200, 200), bold=False, pixel_style=True)
            palavras = objetivo.split()
            linha_atual = ""
            y_offset = 130
            for palavra in palavras:
                teste = linha_atual + (" " if linha_atual else "") + palavra
                teste_render = render_text(teste, 16, (200, 200, 200), bold=False, pixel_style=True)
                if teste_render.get_width() > largura - 60:
                    if linha_atual:
                        tela.blit(render_text(linha_atual, 16, (200, 200, 200), bold=False, pixel_style=True), (x + 20, y + y_offset))
                        y_offset += 25
                    linha_atual = palavra
                else:
                    linha_atual = teste
            if linha_atual:
                tela.blit(render_text(linha_atual, 16, (200, 200, 200), bold=False, pixel_style=True), (x + 20, y + y_offset))
        else:
            sem_missao = render_text("Nenhuma missão ativa", 18, (150, 150, 150), bold=False, pixel_style=True)
            tela.blit(sem_missao, (x + 20, y + 100))
    
    def _desenhar_tela_progresso(self, tela, x, y, largura, altura):
        """Desenha a tela de progresso da campanha"""
        from core.menu import render_text
        from core.missoes import gerenciador_missoes
        from core.progresso import gerenciador_progresso
        
        titulo = render_text("PROGRESSO DA CAMPANHA", 24, (255, 255, 0), bold=True, pixel_style=True)
        tela.blit(titulo, (x + 20, y + 60))
        
        total_missoes = len(gerenciador_missoes.missoes)
        missoes_completas = len(gerenciador_missoes.missoes_completas)
        porcentagem = (missoes_completas / total_missoes * 100) if total_missoes > 0 else 0
        
        barra_x = x + 20
        barra_y = y + 100
        barra_largura = largura - 40
        barra_altura = 25
        
        pygame.draw.rect(tela, (50, 50, 50), (barra_x, barra_y, barra_largura, barra_altura))
        preenchimento = int(barra_largura * (porcentagem / 100))
        pygame.draw.rect(tela, (0, 255, 0), (barra_x, barra_y, preenchimento, barra_altura))
        pygame.draw.rect(tela, (255, 255, 255), (barra_x, barra_y, barra_largura, barra_altura), 2)
        
        texto_progresso = render_text(f"{porcentagem:.1f}%", 18, (255, 255, 255), bold=True, pixel_style=True)
        tela.blit(texto_progresso, (barra_x + barra_largura // 2 - texto_progresso.get_width() // 2, barra_y + 3))
        
        stats_y = barra_y + barra_altura + 20
        stats_texto = render_text(f"Missões: {missoes_completas}/{total_missoes}", 16, (200, 200, 200), bold=False, pixel_style=True)
        tela.blit(stats_texto, (x + 20, stats_y))
        
        capitulo = gerenciador_progresso.obter_capitulo_atual()
        if capitulo:
            capitulo_texto = render_text(f"Capítulo: {capitulo.upper()}", 16, (200, 200, 200), bold=False, pixel_style=True)
            tela.blit(capitulo_texto, (x + 20, stats_y + 25))
        
        status_y = stats_y + 55
        status_titulo = render_text("STATUS DO JOGADOR", 20, (255, 200, 0), bold=True, pixel_style=True)
        tela.blit(status_titulo, (x + 20, status_y))
        
        try:
            from core.status_jogador import status_jogador
            popularidade = status_jogador.popularidade
            fome = status_jogador.fome
            sono = status_jogador.sono
            tedio = status_jogador.tedio
            dinheiro = gerenciador_progresso.dinheiro
            
            pop_porcentagem = min(100, (popularidade / 500) * 100)
            pop_texto = render_text(f"Reputação: {popularidade:.0f}/500 ({pop_porcentagem:.1f}%)", 16, (255, 255, 0), bold=False, pixel_style=True)
            tela.blit(pop_texto, (x + 20, status_y + 30))
            
            pop_barra_x = x + 20
            pop_barra_y = status_y + 50
            pop_barra_largura = largura - 40
            pop_barra_altura = 15
            pop_preenchimento = int(pop_barra_largura * (pop_porcentagem / 100))
            pygame.draw.rect(tela, (30, 30, 30), (pop_barra_x, pop_barra_y, pop_barra_largura, pop_barra_altura))
            pygame.draw.rect(tela, (255, 255, 0), (pop_barra_x, pop_barra_y, pop_preenchimento, pop_barra_altura))
            pygame.draw.rect(tela, (200, 200, 200), (pop_barra_x, pop_barra_y, pop_barra_largura, pop_barra_altura), 1)
            
            cor_fome = (0, 255, 0) if fome > 50 else (255, 200, 0) if fome > 25 else (255, 0, 0)
            fome_texto = render_text(f"Fome: {fome:.0f}%", 16, cor_fome, bold=False, pixel_style=True)
            tela.blit(fome_texto, (x + 20, status_y + 75))
            
            fome_barra_x = x + 20
            fome_barra_y = status_y + 95
            fome_barra_largura = largura - 40
            fome_barra_altura = 15
            fome_preenchimento = int(fome_barra_largura * (fome / 100))
            pygame.draw.rect(tela, (30, 30, 30), (fome_barra_x, fome_barra_y, fome_barra_largura, fome_barra_altura))
            pygame.draw.rect(tela, cor_fome, (fome_barra_x, fome_barra_y, fome_preenchimento, fome_barra_altura))
            pygame.draw.rect(tela, (200, 200, 200), (fome_barra_x, fome_barra_y, fome_barra_largura, fome_barra_altura), 1)
            
            # Sono (azul)
            cor_sono = (100, 150, 255) if sono > 50 else (255, 200, 0) if sono > 25 else (255, 0, 0)
            sono_texto = render_text(f"Sono: {sono:.0f}%", 16, cor_sono, bold=False, pixel_style=True)
            tela.blit(sono_texto, (x + 20, status_y + 120))
            
            # Barra de sono
            sono_barra_x = x + 20
            sono_barra_y = status_y + 140
            sono_barra_largura = largura - 40
            sono_barra_altura = 15
            sono_preenchimento = int(sono_barra_largura * (sono / 100))
            pygame.draw.rect(tela, (30, 30, 30), (sono_barra_x, sono_barra_y, sono_barra_largura, sono_barra_altura))
            pygame.draw.rect(tela, cor_sono, (sono_barra_x, sono_barra_y, sono_preenchimento, sono_barra_altura))
            pygame.draw.rect(tela, (200, 200, 200), (sono_barra_x, sono_barra_y, sono_barra_largura, sono_barra_altura), 1)
            
            # Tédio (cinza)
            tedio_texto = render_text(f"Tédio: {tedio:.0f}%", 16, (150, 150, 150), bold=False, pixel_style=True)
            tela.blit(tedio_texto, (x + 20, status_y + 165))
            
            # Barra de tédio
            tedio_barra_x = x + 20
            tedio_barra_y = status_y + 185
            tedio_barra_largura = largura - 40
            tedio_barra_altura = 15
            tedio_preenchimento = int(tedio_barra_largura * (tedio / 100))
            pygame.draw.rect(tela, (30, 30, 30), (tedio_barra_x, tedio_barra_y, tedio_barra_largura, tedio_barra_altura))
            pygame.draw.rect(tela, (150, 150, 150), (tedio_barra_x, tedio_barra_y, tedio_preenchimento, tedio_barra_altura))
            pygame.draw.rect(tela, (200, 200, 200), (tedio_barra_x, tedio_barra_y, tedio_barra_largura, tedio_barra_altura), 1)
            
            # Dinheiro (verde)
            dinheiro_texto = render_text(f"Dinheiro: ${dinheiro:,}", 16, (0, 255, 0), bold=False, pixel_style=True)
            tela.blit(dinheiro_texto, (x + 20, status_y + 210))
        except Exception as e:
            print(f"[CELULAR] Erro ao obter status do jogador na tela de progresso: {e}")
            import traceback
            traceback.print_exc()
            # Mostrar mensagem de erro
            erro_texto = render_text("Erro ao carregar status", 16, (255, 0, 0), bold=False, pixel_style=True)
            tela.blit(erro_texto, (x + 20, status_y + 30))
    
    def _desenhar_tela_mensagens(self, tela, x, y, largura, altura):
        """Desenha a tela de mensagens"""
        from core.menu import render_text
        
        # Título
        titulo = render_text("MENSAGENS", 24, (255, 255, 0), bold=True, pixel_style=True)
        tela.blit(titulo, (x + 20, y + 60))
        
        # Lista de NPCs disponíveis
        npcs = ["Barão", "Boris", "Crank", "Akira", "Fuligem", "Pixel"]
        npc_y = y + 100
        
        for i, npc in enumerate(npcs):
            npc_texto = render_text(f"→ {npc}", 18, (200, 200, 200), bold=False, pixel_style=True)
            tela.blit(npc_texto, (x + 40, npc_y + (i * 35)))
        
        # Mensagem de placeholder
        placeholder = render_text("(Em desenvolvimento)", 14, (150, 150, 150), bold=False, pixel_style=True)
        tela.blit(placeholder, (x + 20, y + altura - 80))
    
    def _desenhar_tela_saldo(self, tela, x, y, largura, altura):
        """Desenha a tela de saldo"""
        from core.menu import render_text
        from core.progresso import gerenciador_progresso
        
        # Título
        titulo = render_text("SALDO", 24, (255, 255, 0), bold=True, pixel_style=True)
        tela.blit(titulo, (x + 20, y + 60))
        
        # Saldo atual
        saldo = gerenciador_progresso.dinheiro
        saldo_texto = render_text(f"${saldo:,}", 32, (0, 255, 0), bold=True, pixel_style=True)
        tela.blit(saldo_texto, (x + 20, y + 120))
        
        # Formatação com separadores de milhar
        saldo_formatado = f"${saldo:,}".replace(",", ".")
        saldo_formatado_texto = render_text(saldo_formatado, 28, (0, 255, 0), bold=True, pixel_style=True)
        tela.blit(saldo_formatado_texto, (x + 20, y + 120))
    
    def _desenhar_tela_corridas(self, tela, x, y, largura, altura):
        """Desenha a tela de corridas disponíveis"""
        from core.menu import render_text
        from core.progresso import gerenciador_progresso
        
        # Título
        titulo = render_text("CORRIDAS DISPONÍVEIS", 24, (255, 255, 0), bold=True, pixel_style=True)
        tela.blit(titulo, (x + 20, y + 60))
        
        # Lista de corridas desbloqueadas
        corridas_desbloqueadas = gerenciador_progresso.corridas_desbloqueadas
        
        if corridas_desbloqueadas:
            corrida_y = y + 100
            for i, race_id in enumerate(list(corridas_desbloqueadas)[:5]):  # Mostrar até 5
                corrida_texto = render_text(f"→ {race_id}", 18, (200, 200, 200), bold=False, pixel_style=True)
                tela.blit(corrida_texto, (x + 40, corrida_y + (i * 35)))
        else:
            sem_corridas = render_text("Nenhuma corrida disponível", 18, (150, 150, 150), bold=False, pixel_style=True)
            tela.blit(sem_corridas, (x + 20, y + 100))
        
        # Mensagem de placeholder
        placeholder = render_text("(Clique para iniciar corrida)", 14, (150, 150, 150), bold=False, pixel_style=True)
        tela.blit(placeholder, (x + 20, y + altura - 80))

# Instância global
celular = Celular()

