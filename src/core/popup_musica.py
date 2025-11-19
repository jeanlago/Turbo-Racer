import pygame
import os
import math
from config import LARGURA, ALTURA, DIR_PROJETO

class PopupMusica:
    def __init__(self):
        self.ativo = False
        self.tempo_visivel = 0.0
        self.duracao_visivel = 15.0
        self.velocidade_animacao = 200.0
        self.posicao_x = LARGURA
        self.posicao_y = 20
        self.largura = 340
        self.altura = 70
        self.alpha = 0
        self.hover = False
        self.texto_offset = 0
        self.texto_velocidade = 50
        self.texto_tempo = 0
        self.texto_pausa = 2.0
        self.texto_estado = "pausa"
        self.texto_largura_total = 0
        self.texto_largura_disponivel = 0
        self.texto_terminou_deslizar = False
        self.tempo_apos_deslizar = 0
        
        self.tipo_notificacao = "musica"
        self.icone_notificacao = None
        self.disco_original = None
        self.disco_rotacionado = None
        self.angulo_disco = 0
        self.icone_carregado = False
        self.tempo_piscar = 0.0
        
        self.cor_fundo = (0, 0, 0)
        self.cor_borda = (255, 255, 255)
        self.cor_texto = (255, 255, 255)
        self.cor_botao = (255, 255, 255)
        
        self.surface = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
    
    def carregar_icone_notificacao(self):
        """Carrega o ícone de notificação"""
        try:
            caminhos_tentados = [
                os.path.join(DIR_PROJETO, "assets", "images", "icons", "notificacao.png"),
                "assets/images/icons/notificacao.png",
                "assets/images/icons/notification.png",
            ]
            
            for caminho in caminhos_tentados:
                if os.path.exists(caminho):
                    self.icone_notificacao = pygame.image.load(caminho).convert_alpha()
                    self.icone_notificacao = pygame.transform.scale(self.icone_notificacao, (35, 35))
                    print(f"Ícone de notificação carregado: {caminho}")
                    return
            
            self.criar_icone_simples()
        except Exception as e:
            print(f"Erro ao carregar ícone de notificação: {e}")
            self.criar_icone_simples()
    
    def carregar_disco_vinil(self):
        """Carrega o ícone de disco de vinil para notificações de música"""
        try:
            caminho_disco = os.path.join(DIR_PROJETO, "assets", "images", "icons", "vinil_disc.png")
            if os.path.exists(caminho_disco):
                self.disco_original = pygame.image.load(caminho_disco).convert_alpha()
                self.disco_original = pygame.transform.scale(self.disco_original, (35, 35))
                print(f"Disco de vinil carregado: {caminho_disco}")
            else:
                self.criar_disco_simples()
        except Exception as e:
            print(f"Erro ao carregar disco de vinil: {e}")
            self.criar_disco_simples()
    
    def criar_icone_simples(self):
        """Cria um ícone de notificação simples usando pygame"""
        self.icone_notificacao = pygame.Surface((35, 35), pygame.SRCALPHA)
        pygame.draw.circle(self.icone_notificacao, (255, 255, 255), (17, 14), 9, 2)
        pygame.draw.circle(self.icone_notificacao, (255, 0, 0), (24, 9), 5)
    
    def criar_disco_simples(self):
        """Cria um ícone de disco de vinil simples usando pygame"""
        self.disco_original = pygame.Surface((35, 35), pygame.SRCALPHA)
        pygame.draw.circle(self.disco_original, (255, 255, 255), (17, 17), 16, 2)
        pygame.draw.circle(self.disco_original, (255, 255, 255), (17, 17), 7, 2)
        for i in range(8):
            angulo = i * 45
            x1 = 17 + 7 * math.cos(math.radians(angulo))
            y1 = 17 + 7 * math.sin(math.radians(angulo))
            x2 = 17 + 16 * math.cos(math.radians(angulo))
            y2 = 17 + 16 * math.sin(math.radians(angulo))
            pygame.draw.line(self.disco_original, (255, 255, 255), (x1, y1), (x2, y2), 1)
    
    def limpar_caracteres_especiais(self, texto):
        """Remove ou substitui caracteres que causam quadradinhos"""
        if not texto:
            return texto
        
        substituicoes = {
            'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
            'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
            'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
            'ç': 'c', 'ñ': 'n',
            'Á': 'A', 'À': 'A', 'Ã': 'A', 'Â': 'A', 'Ä': 'A',
            'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
            'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
            'Ó': 'O', 'Ò': 'O', 'Õ': 'O', 'Ô': 'O', 'Ö': 'O',
            'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',
            'Ç': 'C', 'Ñ': 'N',
            '♪': '', '♫': '', '♬': '', '♭': '', '♯': '',
            '–': '-', '—': '-', '…': '...', '•': '*',
            '"': '"', '"': '"', ''': "'", ''': "'",
            '«': '"', '»': '"', '‹': "'", '›': "'"
        }
        
        texto_limpo = texto
        for char_problema, char_substituto in substituicoes.items():
            texto_limpo = texto_limpo.replace(char_problema, char_substituto)
        
        texto_final = ""
        for char in texto_limpo:
            codigo = ord(char)
            if codigo < 128:
                texto_final += char
            elif 192 <= codigo <= 255:
                try:
                    teste = pygame.font.SysFont("arial", 16).render(char, True, (255, 255, 255))
                    texto_final += char
                except:
                    texto_final += '?'
            else:
                texto_final += '?'
        
        return texto_final
    
    def mostrar(self, texto, tipo="musica"):
        """Mostra o pop-up com o texto e tipo de notificação
        
        Args:
            texto: Texto a ser exibido
            tipo: "musica" para notificações de música (disco de vinil) ou "outra" para outras notificações (ícone piscando)
        """
        self.ativo = True
        self.tempo_visivel = 0.0
        self.nome_musica = texto
        self.tipo_notificacao = tipo
        self.posicao_x = LARGURA
        self.alpha = 0
        self.tempo_piscar = 0.0
        self.texto_offset = 0
        self.texto_tempo = 0
        self.texto_estado = "pausa"
        self.texto_terminou_deslizar = False
        self.tempo_apos_deslizar = 0
    
    def esconder(self):
        """Esconde o pop-up"""
        self.ativo = False
    
    def atualizar(self, dt):
        """Atualiza a animação do pop-up"""
        if not self.ativo:
            return
        
        self.tempo_visivel += dt
        
        if not self.icone_carregado:
            self.carregar_icone_notificacao()
            self.carregar_disco_vinil()
            self.icone_carregado = True
        
        if self.tipo_notificacao == "musica" and self.disco_original:
            self.angulo_disco += 90 * dt
            if self.angulo_disco >= 360:
                self.angulo_disco = 0
            self.disco_rotacionado = pygame.transform.rotate(self.disco_original, self.angulo_disco)
        
        if self.tipo_notificacao == "outra":
            self.tempo_piscar += dt
        
        if hasattr(self, 'nome_musica') and self.nome_musica:
            nome_limpo = self.limpar_caracteres_especiais(self.nome_musica)
            fonte = pygame.font.SysFont("arial", 16, bold=True)
            texto_teste = fonte.render("♪ " + nome_limpo, True, (255, 255, 255))
            self.texto_largura_total = texto_teste.get_width()
            self.texto_largura_disponivel = self.largura - 100
            
            if self.texto_largura_total > self.texto_largura_disponivel:
                self.texto_tempo += dt
                max_offset = self.texto_largura_total - self.texto_largura_disponivel
                ciclo_tempo = 6.0
                tempo_ciclo = self.texto_tempo % ciclo_tempo
                
                if tempo_ciclo < 1.0:
                    self.texto_offset = 0
                elif tempo_ciclo < 3.0:
                    progresso = (tempo_ciclo - 1.0) / 2.0
                    self.texto_offset = int(progresso * max_offset)
                elif tempo_ciclo < 4.0:
                    self.texto_offset = max_offset
                elif tempo_ciclo < 5.5:
                    progresso = (tempo_ciclo - 4.0) / 1.5
                    self.texto_offset = int(max_offset - progresso * max_offset)
                else:
                    self.texto_offset = 0
            else:
                self.texto_offset = 0
        
        posicao_final = LARGURA - self.largura - 20
        
        if self.tempo_visivel < 1.0:
            progresso = self.tempo_visivel / 1.0
            self.posicao_x = int(LARGURA - progresso * (LARGURA - posicao_final))
            self.alpha = int(255 * progresso)
        elif self.tempo_visivel < self.duracao_visivel - 1.0:
            self.posicao_x = posicao_final
            self.alpha = 255
        else:
            progresso = (self.tempo_visivel - (self.duracao_visivel - 1.0)) / 1.0
            self.posicao_x = int(posicao_final + progresso * (LARGURA - posicao_final))
            self.alpha = int(255 * (1 - progresso))
            
            if progresso >= 1.0:
                self.ativo = False
                self.posicao_x = LARGURA
                self.alpha = 0
    
    def verificar_hover(self, mouse_x, mouse_y):
        """Verifica se o mouse está sobre o pop-up"""
        if not self.ativo:
            self.hover = False
            return False
        
        popup_rect = pygame.Rect(self.posicao_x, self.posicao_y, self.largura, self.altura)
        self.hover = popup_rect.collidepoint(mouse_x, mouse_y)
        return self.hover
    
    def verificar_clique(self, mouse_x, mouse_y):
        """Verifica se o usuário clicou no popup"""
        if not self.ativo or not self.hover:
            return None
        return None
    
    def desenhar(self, tela):
        """Desenha o pop-up na tela"""
        if not self.ativo or self.alpha <= 0:
            return
        
        self.surface = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 0))
        
        cor_borda_atual = self.cor_borda
        if self.tipo_notificacao == "outra":
            ciclo_piscar = (self.tempo_piscar * 2.0) % 2.0
            if ciclo_piscar < 1.0:
                intensidade = abs(ciclo_piscar - 0.5) * 2.0
                laranja = (255, 165, 0)
                cor_borda_atual = (
                    int(self.cor_borda[0] * (1 - intensidade) + laranja[0] * intensidade),
                    int(self.cor_borda[1] * (1 - intensidade) + laranja[1] * intensidade),
                    int(self.cor_borda[2] * (1 - intensidade) + laranja[2] * intensidade)
                )
        
        pygame.draw.rect(self.surface, self.cor_fundo, (0, 0, self.largura, self.altura), border_radius=8)
        pygame.draw.rect(self.surface, cor_borda_atual, (0, 0, self.largura, self.altura), 2, border_radius=8)
        
        if self.tipo_notificacao == "musica":
            if self.disco_rotacionado:
                disco_rect = self.disco_rotacionado.get_rect(center=(28, self.altura // 2))
                self.surface.blit(self.disco_rotacionado, disco_rect)
            elif self.disco_original:
                disco_rect = self.disco_original.get_rect(center=(28, self.altura // 2))
                self.surface.blit(self.disco_original, disco_rect)
            else:
                pygame.draw.circle(self.surface, self.cor_texto, (28, self.altura // 2), 8)
        else:
            if self.icone_notificacao:
                if self.tipo_notificacao == "outra":
                    ciclo_piscar = (self.tempo_piscar * 2.0) % 2.0
                    if ciclo_piscar < 1.0:
                        intensidade = abs(ciclo_piscar - 0.5) * 2.0
                        icone_piscar = self.icone_notificacao.copy()
                        overlay = pygame.Surface(icone_piscar.get_size(), pygame.SRCALPHA)
                        overlay.fill((255, 165, 0))
                        overlay.set_alpha(int(128 * intensidade))
                        icone_piscar.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
                        icone_rect = icone_piscar.get_rect(center=(28, self.altura // 2))
                        self.surface.blit(icone_piscar, icone_rect)
                    else:
                        icone_rect = self.icone_notificacao.get_rect(center=(28, self.altura // 2))
                        self.surface.blit(self.icone_notificacao, icone_rect)
                else:
                    icone_rect = self.icone_notificacao.get_rect(center=(28, self.altura // 2))
                    self.surface.blit(self.icone_notificacao, icone_rect)
            else:
                pygame.draw.circle(self.surface, self.cor_texto, (28, self.altura // 2), 8)
        
        nome_limpo = self.limpar_caracteres_especiais(self.nome_musica)
        fonte = pygame.font.SysFont("arial", 16, bold=True)
        prefixo = "♪ " if self.tipo_notificacao == "musica" else ""
        texto_musica = fonte.render(prefixo + nome_limpo, True, self.cor_texto)
        
        texto_altura = texto_musica.get_height()
        area_texto_y = (self.altura - texto_altura) // 2
        area_texto = pygame.Rect(50, area_texto_y, self.largura - 100, texto_altura + 4)
        clip_surface = pygame.Surface((area_texto.width, area_texto.height), pygame.SRCALPHA)
        clip_surface.blit(texto_musica, (0 - self.texto_offset, 0))
        self.surface.blit(clip_surface, (area_texto.x, area_texto.y))
        
        if self.alpha < 255:
            surface_alpha = self.surface.copy()
            surface_alpha.set_alpha(self.alpha)
            tela.blit(surface_alpha, (self.posicao_x, self.posicao_y))
        else:
            tela.blit(self.surface, (self.posicao_x, self.posicao_y))

# Instância global do pop-up
popup_musica = PopupMusica()
