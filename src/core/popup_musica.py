import pygame
import os
from config import LARGURA, ALTURA, DIR_PROJETO

class PopupMusica:
    def __init__(self):
        self.ativo = False
        self.tempo_visivel = 0.0
        self.duracao_visivel = 15.0  # 15 segundos - muito mais tempo
        self.velocidade_animacao = 200.0  # pixels por segundo - mais lenta
        self.posicao_x = LARGURA  # Começa fora da tela (direita)
        self.posicao_y = 20  # Posição fixa no canto superior direito
        self.largura = 350
        self.altura = 70
        self.alpha = 0
        self.hover = False  # Para controlar se o mouse está sobre o pop-up
        self.texto_offset = 0  # Offset para animação do texto
        self.texto_velocidade = 50  # Pixels por segundo
        self.texto_tempo = 0  # Timer para o texto
        self.texto_pausa = 2.0  # Segundos de pausa antes de deslizar novamente
        self.texto_estado = "pausa"  # "pausa", "deslizando"
        self.texto_largura_total = 0
        self.texto_largura_disponivel = 0
        self.texto_terminou_deslizar = False  # Flag para saber quando terminou de deslizar
        self.tempo_apos_deslizar = 0  # Timer após terminar de deslizar
        
        # Carregar ícone de disco de vinil
        self.disco_original = None
        self.disco_rotacionado = None
        self.angulo_disco = 0
        self.disco_carregado = False
        
        # Cores (estilo cyberpunk/retro)
        self.cor_fundo = (0, 0, 0)  # Preto
        self.cor_borda = (255, 255, 255)  # Branco
        self.cor_texto = (255, 255, 255)  # Branco
        self.cor_botao = (255, 255, 255)  # Branco para os botões
        
        # Superfície para o pop-up
        self.surface = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        
        # Botões removidos - apenas ícone e texto
    
    def carregar_disco(self):
        """Carrega o ícone de disco de vinil"""
        try:
            caminho_disco = os.path.join(DIR_PROJETO, "assets", "images", "icons", "vinil_disc.png")
            if os.path.exists(caminho_disco):
                # Carregar com transparêncIA para manter fundo transparente
                self.disco_original = pygame.image.load(caminho_disco).convert_alpha()
                # Redimensionar para 30x30 pixels
                self.disco_original = pygame.transform.scale(self.disco_original, (30, 30))
            else:
                # Se não encontrar o arquivo, crIAr um disco de vinil simples
                self.crIAr_disco_simples()
        except Exception as e:
            print(f"Erro ao carregar disco de vinil: {e}")
            # CrIAr disco simples como fallback
            self.crIAr_disco_simples()
    
    def crIAr_disco_simples(self):
        """CrIA um ícone de som/ondas simples usando pygame"""
        # CrIAr superfície com transparêncIA
        self.disco_original = pygame.Surface((30, 30), pygame.SRCALPHA)
        
        # Desenhar ícone de som/ondas (estilo da imagem)
        # Ponto central
        pygame.draw.circle(self.disco_original, (255, 255, 255), (15, 15), 3)
        
        # Ondas de som (linhas horizontais com espinhos)
        for i in range(3):
            y = 15 + (i - 1) * 8  # -8, 0, 8
            # Linha horizontal
            pygame.draw.line(self.disco_original, (255, 255, 255), (8, y), (22, y), 2)
            # Espinhos para cima e para baixo
            for x in range(8, 23, 3):
                pygame.draw.line(self.disco_original, (255, 255, 255), (x, y), (x, y - 3), 1)
                pygame.draw.line(self.disco_original, (255, 255, 255), (x, y), (x, y + 3), 1)
    
    def limpar_caracteres_especIAis(self, texto):
        """Remove ou substitui caracteres que causam quadradinhos"""
        if not texto:
            return texto
        
        # Dicionário de substituições para caracteres problemáticos
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
        
        # Aplicar substituições
        texto_limpo = texto
        for char_problema, char_substituto in substituicoes.items():
            texto_limpo = texto_limpo.replace(char_problema, char_substituto)
        
        # Remover caracteres não-ASCII restantes que podem causar problemas
        # Mas manter alguns caracteres comuns que funcionam bem
        texto_final = ""
        for char in texto_limpo:
            codigo = ord(char)
            if codigo < 128:  # ASCII básico
                texto_final += char
            elif 192 <= codigo <= 255:  # Latin-1 suplementar (acentos comuns)
                # Tentar manter acentos comuns que funcionam
                try:
                    # Testar se o caractere pode ser renderizado
                    teste = pygame.font.SysFont("arIAl", 16).render(char, True, (255, 255, 255))
                    texto_final += char
                except:
                    texto_final += '?'
            else:
                texto_final += '?'  # Substituir por ? se não for reconhecido
        
        return texto_final
    
    def mostrar(self, nome_musica):
        """Mostra o pop-up com o nome da música"""
        self.ativo = True
        self.tempo_visivel = 0.0
        self.nome_musica = nome_musica
        self.posicao_x = LARGURA  # Começa fora da tela (direita)
        self.alpha = 0
        # Resetar estado de animação
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
        
        # Contar o tempo de esconder sempre (não pausar no hover)
        self.tempo_visivel += dt
        
        # Carregar disco se ainda não foi carregado
        if not self.disco_carregado:
            self.carregar_disco()
            self.disco_carregado = True
        
        # Rotacionar disco de vinil
        if self.disco_original:
            self.angulo_disco += 90 * dt  # 90 graus por segundo
            if self.angulo_disco >= 360:
                self.angulo_disco = 0
            self.disco_rotacionado = pygame.transform.rotate(self.disco_original, self.angulo_disco)
        
        # Atualizar animação do texto deslizante
        if hasattr(self, 'nome_musica') and self.nome_musica:
            # Limpar caracteres problemáticos do nome da música
            nome_limpo = self.limpar_caracteres_especIAis(self.nome_musica)
            
            # Usar fonte do sistema com tamanho maior
            fonte = pygame.font.SysFont("arIAl", 16, bold=True)
            texto_teste = fonte.render("♪ " + nome_limpo, True, (255, 255, 255))
            self.texto_largura_total = texto_teste.get_width()
            self.texto_largura_disponivel = self.largura - 120  # Espaço disponível para o texto
            
            if self.texto_largura_total > self.texto_largura_disponivel:
                # Texto é muito longo, animar deslizamento simples
                self.texto_tempo += dt
                max_offset = self.texto_largura_total - self.texto_largura_disponivel
                
                # Deslizar continuamente com pausa e retorno
                ciclo_tempo = 6.0  # 6 segundos por ciclo completo
                tempo_ciclo = self.texto_tempo % ciclo_tempo
                
                if tempo_ciclo < 1.0:  # Pausa inicial
                    self.texto_offset = 0
                elif tempo_ciclo < 3.0:  # Deslizamento para a direita
                    progresso = (tempo_ciclo - 1.0) / 2.0
                    self.texto_offset = int(progresso * max_offset)
                elif tempo_ciclo < 4.0:  # Pausa no final
                    self.texto_offset = max_offset
                elif tempo_ciclo < 5.5:  # Retorno para a esquerda
                    progresso = (tempo_ciclo - 4.0) / 1.5
                    self.texto_offset = int(max_offset - progresso * max_offset)
                else:  # Pausa final
                    self.texto_offset = 0
            else:
                # Texto cabe, não animar
                self.texto_offset = 0
        
        # Posição final fixa (canto superior direito)
        posicao_final = LARGURA - self.largura - 20
        
        if self.tempo_visivel < 1.0:  # Animação de entrada
            # Interpolação linear simples da direita para dentro
            progresso = self.tempo_visivel / 1.0
            self.posicao_x = int(LARGURA - progresso * (LARGURA - posicao_final))
            self.alpha = int(255 * progresso)
        elif self.tempo_visivel < self.duracao_visivel - 1.0:  # Fica visível
            self.posicao_x = posicao_final
            self.alpha = 255
        else:  # Animação de saída
            # Interpolação linear simples da posição atual para fora
            progresso = (self.tempo_visivel - (self.duracao_visivel - 1.0)) / 1.0
            self.posicao_x = int(posicao_final + progresso * (LARGURA - posicao_final))
            self.alpha = int(255 * (1 - progresso))
            
            if progresso >= 1.0:
                self.ativo = False
                # Resetar posição para próxima ativação
                self.posicao_x = LARGURA
                self.alpha = 0
    
    def verificar_hover(self, mouse_x, mouse_y):
        """Verifica se o mouse está sobre o pop-up"""
        if not self.ativo:
            self.hover = False
            return False
        
        # Verificar se o mouse está sobre o pop-up
        popup_rect = pygame.Rect(self.posicao_x, self.posicao_y, self.largura, self.altura)
        self.hover = popup_rect.collidepoint(mouse_x, mouse_y)
        
        # Hover dos botões removido
        
        return self.hover
    
    def verificar_clique(self, mouse_x, mouse_y):
        """Verifica se o usuário clicou no popup (sem botões visuais)"""
        if not self.ativo or not self.hover:
            return None
        
        # Sem botões visuais - apenas hover
        return None
    
    def desenhar(self, tela):
        """Desenha o pop-up na tela"""
        if not self.ativo or self.alpha <= 0:
            return
        
        
        # Limpar superfície
        self.surface.fill((0, 0, 0, 0))
        
        # Desenhar fundo com bordas arredondadas (estilo da imagem)
        pygame.draw.rect(self.surface, self.cor_fundo, (0, 0, self.largura, self.altura), border_radius=8)
        pygame.draw.rect(self.surface, self.cor_borda, (0, 0, self.largura, self.altura), 2, border_radius=8)
        
        # Desenhar disco de vinil rotativo
        if self.disco_rotacionado:
            # Centralizar o disco rotacionado
            disco_rect = self.disco_rotacionado.get_rect(center=(25, 35))
            self.surface.blit(self.disco_rotacionado, disco_rect)
        elif self.disco_original:
            # Fallback: disco original se não estiver rotacionado
            disco_rect = self.disco_original.get_rect(center=(25, 35))
            self.surface.blit(self.disco_original, disco_rect)
        else:
            # Fallback: ícone simples se não carregar
            pygame.draw.circle(self.surface, self.cor_texto, (25, 35), 8)
        
        # Desenhar nome da música com animação deslizante
        # Limpar caracteres problemáticos do nome da música
        nome_limpo = self.limpar_caracteres_especIAis(self.nome_musica)
        
        # Usar fonte do sistema com tamanho maior
        fonte = pygame.font.SysFont("arIAl", 16, bold=True)
        texto_musica = fonte.render("♪ " + nome_limpo, True, self.cor_texto)
        
        # CrIAr uma superfície de clipping para o texto (mais espaço)
        area_texto = pygame.Rect(50, 25, self.largura - 100, 20)
        clip_surface = pygame.Surface((area_texto.width, area_texto.height), pygame.SRCALPHA)
        
        # Desenhar o texto com offset (começa em 0, desliza para a esquerda)
        clip_surface.blit(texto_musica, (0 - self.texto_offset, 0))
        
        # Efeito de fade removido por enquanto para evitar problemas de cor
        
        # Aplicar o clipping
        self.surface.blit(clip_surface, (area_texto.x, area_texto.y))
        
        # Desenhar na tela principal com transparêncIA
        if self.alpha < 255:
            # CrIAr uma cópIA da superfície com alpha
            surface_alpha = self.surface.copy()
            surface_alpha.set_alpha(self.alpha)
            tela.blit(surface_alpha, (self.posicao_x, self.posicao_y))
        else:
            tela.blit(self.surface, (self.posicao_x, self.posicao_y))

# InstâncIA global do pop-up
popup_musica = PopupMusica()
