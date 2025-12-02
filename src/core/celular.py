"""Sistema de Celular - Interface para missões, progresso, mensagens e corridas"""
import pygame
import os
import math
from config import DIR_PROJETO, LARGURA, ALTURA

CAMINHO_SPRITE_CELULAR = os.path.join(DIR_PROJETO, "assets", "images", "hud", "celular.png")

class Celular:
    """Celular que aparece no canto inferior direito durante a campanha"""
    
    def __init__(self):
        self.sprite_original = None
        self.sprite_atual = None
        self.carregado = False
        
        # Posição e tamanho
        self.largura_base = 80
        self.altura_base = 120
        self.pos_x = LARGURA - self.largura_base - 20
        self.pos_y = ALTURA - self.altura_base - 20
        
        # Estado
        self.visivel = False
        self.menu_aberto = False
        self.hover = False
        
        # Animações
        self.tempo_animacao = 0.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.escala = 1.0
        
        # Menu
        self.opcao_selecionada = 0
        self.menu_opcoes = [
            "Missões",
            "Progresso",
            "Mensagens",
            "Saldo",
            "Corridas"
        ]
        
        # Estado do menu
        self.tela_atual = "menu"  # menu, missoes, progresso, mensagens, saldo, corridas
        
        self.carregar_sprite()
    
    def carregar_sprite(self):
        """Carrega o sprite do celular"""
        try:
            if os.path.exists(CAMINHO_SPRITE_CELULAR):
                self.sprite_original = pygame.image.load(CAMINHO_SPRITE_CELULAR).convert_alpha()
                # Redimensionar para tamanho base
                self.sprite_original = pygame.transform.scale(
                    self.sprite_original, 
                    (self.largura_base, self.altura_base)
                )
                self.sprite_atual = self.sprite_original.copy()
                self.carregado = True
                print(f"[CELULAR] Sprite carregado: {CAMINHO_SPRITE_CELULAR}")
            else:
                print(f"[CELULAR] ERRO: Sprite não encontrado: {CAMINHO_SPRITE_CELULAR}")
                # Criar sprite placeholder
                self.sprite_original = pygame.Surface((self.largura_base, self.altura_base), pygame.SRCALPHA)
                pygame.draw.rect(self.sprite_original, (100, 100, 100), (0, 0, self.largura_base, self.altura_base))
                pygame.draw.rect(self.sprite_original, (200, 200, 200), (5, 5, self.largura_base-10, self.altura_base-10))
                self.sprite_atual = self.sprite_original.copy()
                self.carregado = True
        except Exception as e:
            print(f"[CELULAR] Erro ao carregar sprite: {e}")
            self.carregado = False
    
    def verificar_visibilidade(self, modo_arcade=False, em_corrida=False, cutscene_ativa=False):
        """Verifica se o celular deve estar visível"""
        # Só aparece em modo campanha, fora de corridas e cutscenes
        self.visivel = not modo_arcade and not em_corrida and not cutscene_ativa
    
    def atualizar(self, dt, mouse_pos=None):
        """Atualiza o estado do celular"""
        if not self.visivel or not self.carregado:
            return
        
        # Verificar hover
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
        
        # Animações de hover
        if self.hover:
            self.tempo_animacao += dt * 10.0  # Velocidade da animação
            # Vibração lateral (sinusoidal)
            self.offset_x = math.sin(self.tempo_animacao * 2.0) * 3.0
            # Aumento de tamanho
            self.escala = 1.0 + 0.1 * (1.0 + math.sin(self.tempo_animacao * 1.5)) / 2.0
        else:
            # Retornar ao estado normal
            self.offset_x = self.offset_x * 0.9  # Suavizar
            self.escala = 1.0 + (self.escala - 1.0) * 0.9  # Suavizar
            if abs(self.offset_x) < 0.1:
                self.offset_x = 0.0
            if abs(self.escala - 1.0) < 0.01:
                self.escala = 1.0
                self.tempo_animacao = 0.0
        
        # Atualizar sprite com escala
        if self.sprite_original:
            nova_largura = int(self.largura_base * self.escala)
            nova_altura = int(self.altura_base * self.escala)
            self.sprite_atual = pygame.transform.scale(self.sprite_original, (nova_largura, nova_altura))
    
    def processar_clique(self, pos):
        """Processa clique no celular"""
        if not self.visivel or not self.carregado:
            return False
        
        # Se o menu está aberto, processar clique no menu primeiro
        if self.menu_aberto:
            return self._processar_clique_menu(pos)
        
        # Se o menu não está aberto, verificar clique no celular
        rect_celular = pygame.Rect(
            self.pos_x + self.offset_x,
            self.pos_y + self.offset_y,
            self.largura_base * self.escala,
            self.altura_base * self.escala
        )
        
        if rect_celular.collidepoint(pos):
            self.menu_aberto = True
            self.tela_atual = "menu"
            self.opcao_selecionada = 0
            return True
        
        return False
    
    def _processar_clique_menu(self, pos):
        """Processa clique dentro do menu"""
        # Se clicou fora do menu, fechar
        menu_largura = 500
        menu_altura = 400
        menu_x = LARGURA // 2 - menu_largura // 2
        menu_y = ALTURA // 2 - menu_altura // 2
        
        menu_rect = pygame.Rect(menu_x, menu_y, menu_largura, menu_altura)
        if not menu_rect.collidepoint(pos):
            # Clicou fora do menu, fechar
            self.menu_aberto = False
            self.tela_atual = "menu"
            return True
        
        # Processar clique nas opções do menu
        if self.tela_atual == "menu":
            return self._processar_clique_menu_opcoes(pos)
        
        return False
    
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
                    # Verificar clique nas opções do menu
                    resultado = self._processar_clique_menu_opcoes(evento.pos)
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
        # Calcular posições das opções
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
        
        # Desenhar celular
        if self.sprite_atual:
            tela.blit(
                self.sprite_atual,
                (self.pos_x + self.offset_x, self.pos_y + self.offset_y)
            )
        
        # Desenhar menu se aberto
        if self.menu_aberto:
            self._desenhar_menu(tela)
    
    def _desenhar_menu(self, tela):
        """Desenha o menu do celular"""
        from core.menu import render_text
        
        # Fundo semi-transparente
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        tela.blit(overlay, (0, 0))
        
        # Fundo do menu
        menu_largura = 500
        menu_altura = 400
        menu_x = LARGURA // 2 - menu_largura // 2
        menu_y = ALTURA // 2 - menu_altura // 2
        
        menu_bg = pygame.Surface((menu_largura, menu_altura), pygame.SRCALPHA)
        menu_bg.fill((30, 30, 40, 240))
        tela.blit(menu_bg, (menu_x, menu_y))
        pygame.draw.rect(tela, (100, 150, 200), (menu_x, menu_y, menu_largura, menu_altura), 3)
        
        # Título
        titulo = render_text("CELULAR", 28, (255, 255, 255), bold=True, pixel_style=True)
        tela.blit(titulo, (menu_x + 20, menu_y + 20))
        
        # Desenhar tela atual
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
        
        # Botão voltar
        voltar_texto = render_text("ESC - Voltar", 16, (200, 200, 200), bold=False, pixel_style=True)
        tela.blit(voltar_texto, (menu_x + menu_largura - 150, menu_y + menu_altura - 30))
    
    def _desenhar_menu_principal(self, tela, x, y, largura, altura):
        """Desenha o menu principal"""
        from core.menu import render_text
        
        opcao_altura = 40
        inicio_y = y + 80
        
        for i, opcao in enumerate(self.menu_opcoes):
            opcao_y = inicio_y + (i * opcao_altura)
            
            # Destaque se selecionada
            if i == self.opcao_selecionada:
                destaque = pygame.Surface((largura - 40, opcao_altura - 5), pygame.SRCALPHA)
                destaque.fill((100, 150, 200, 100))
                tela.blit(destaque, (x + 20, opcao_y))
            
            # Texto da opção
            cor = (255, 255, 255) if i == self.opcao_selecionada else (200, 200, 200)
            texto = render_text(opcao, 20, cor, bold=(i == self.opcao_selecionada), pixel_style=True)
            tela.blit(texto, (x + 40, opcao_y + 10))
    
    def _desenhar_tela_missoes(self, tela, x, y, largura, altura):
        """Desenha a tela de missões"""
        from core.menu import render_text
        from core.missoes import gerenciador_missoes
        
        # Título
        titulo = render_text("MISSÕES", 24, (255, 255, 0), bold=True, pixel_style=True)
        tela.blit(titulo, (x + 20, y + 60))
        
        # Missão ativa
        missao = gerenciador_missoes.obter_missao_ativa()
        if missao:
            # Usar o método que retorna o nome detalhado se disponível
            nome_missao = gerenciador_missoes.obter_nome_missao()
            nome = render_text(f"Nome: {nome_missao}", 18, (255, 255, 255), bold=True, pixel_style=True)
            tela.blit(nome, (x + 20, y + 100))
            
            # Usar o método que retorna a descrição detalhada se disponível
            objetivo = gerenciador_missoes.obter_objetivo_missao()
            objetivo_texto = render_text(f"Objetivo: {objetivo}", 16, (200, 200, 200), bold=False, pixel_style=True)
            # Quebrar em linhas se necessário
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
        
        # Título
        titulo = render_text("PROGRESSO DA CAMPANHA", 24, (255, 255, 0), bold=True, pixel_style=True)
        tela.blit(titulo, (x + 20, y + 60))
        
        # Calcular progresso
        total_missoes = len(gerenciador_missoes.missoes)
        missoes_completas = len(gerenciador_missoes.missoes_completas)
        porcentagem = (missoes_completas / total_missoes * 100) if total_missoes > 0 else 0
        
        # Barra de progresso
        barra_x = x + 20
        barra_y = y + 120
        barra_largura = largura - 40
        barra_altura = 30
        
        # Fundo da barra
        pygame.draw.rect(tela, (50, 50, 50), (barra_x, barra_y, barra_largura, barra_altura))
        # Preenchimento
        preenchimento = int(barra_largura * (porcentagem / 100))
        pygame.draw.rect(tela, (0, 255, 0), (barra_x, barra_y, preenchimento, barra_altura))
        # Borda
        pygame.draw.rect(tela, (255, 255, 255), (barra_x, barra_y, barra_largura, barra_altura), 2)
        
        # Texto de porcentagem
        texto_progresso = render_text(f"{porcentagem:.1f}%", 20, (255, 255, 255), bold=True, pixel_style=True)
        tela.blit(texto_progresso, (barra_x + barra_largura // 2 - texto_progresso.get_width() // 2, barra_y + 5))
        
        # Estatísticas
        stats_y = barra_y + barra_altura + 30
        stats_texto = render_text(f"Missões Completas: {missoes_completas}/{total_missoes}", 16, (200, 200, 200), bold=False, pixel_style=True)
        tela.blit(stats_texto, (x + 20, stats_y))
        
        # Capítulo atual
        capitulo = gerenciador_progresso.obter_capitulo_atual()
        if capitulo:
            capitulo_texto = render_text(f"Capítulo: {capitulo.upper()}", 16, (200, 200, 200), bold=False, pixel_style=True)
            tela.blit(capitulo_texto, (x + 20, stats_y + 30))
    
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

