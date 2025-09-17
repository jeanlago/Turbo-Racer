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
        self.posicao_y = ALTURA - 120  # Posição fixa no canto inferior direito
        self.largura = 350
        self.altura = 100
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
        
        # Cores
        self.cor_fundo = (20, 20, 20)
        self.cor_borda = (100, 100, 100)
        self.cor_texto = (255, 255, 255)
        self.cor_botao = (255, 100, 100)
        
        # Superfície para o pop-up
        self.surface = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        
        # Botões de controle de música
        self.botao_anterior_rect = pygame.Rect(10, 60, 40, 30)
        self.botao_proximo_rect = pygame.Rect(60, 60, 40, 30)
        self.hover_anterior = False
        self.hover_proximo = False
    
    def carregar_disco(self):
        """Carrega o ícone de disco de vinil"""
        try:
            caminho_disco = os.path.join(DIR_PROJETO, "assets", "images", "icons", "vinil_disc.png")
            if os.path.exists(caminho_disco):
                # Carregar com transparência para manter fundo transparente
                self.disco_original = pygame.image.load(caminho_disco).convert_alpha()
                # Redimensionar para 30x30 pixels
                self.disco_original = pygame.transform.scale(self.disco_original, (30, 30))
            else:
                # Se não encontrar o arquivo, criar um disco de vinil simples
                self.criar_disco_simples()
        except Exception as e:
            print(f"Erro ao carregar disco de vinil: {e}")
            # Criar disco simples como fallback
            self.criar_disco_simples()
    
    def criar_disco_simples(self):
        """Cria um disco de vinil simples usando pygame"""
        # Criar superfície com transparência
        self.disco_original = pygame.Surface((30, 30), pygame.SRCALPHA)
        
        # Desenhar disco de vinil
        # Disco principal (preto)
        pygame.draw.circle(self.disco_original, (20, 20, 20), (15, 15), 15)
        
        # Anel externo (cinza escuro)
        pygame.draw.circle(self.disco_original, (60, 60, 60), (15, 15), 12)
        
        # Anel interno (preto)
        pygame.draw.circle(self.disco_original, (20, 20, 20), (15, 15), 10)
        
        # Linhas de vinil (cinza claro)
        for i in range(0, 360, 30):
            x1 = 15 + 8 * pygame.math.Vector2(1, 0).rotate(i).x
            y1 = 15 + 8 * pygame.math.Vector2(1, 0).rotate(i).y
            x2 = 15 + 12 * pygame.math.Vector2(1, 0).rotate(i).x
            y2 = 15 + 12 * pygame.math.Vector2(1, 0).rotate(i).y
            pygame.draw.line(self.disco_original, (100, 100, 100), (x1, y1), (x2, y2), 1)
        
        # Buraco central (preto)
        pygame.draw.circle(self.disco_original, (0, 0, 0), (15, 15), 3)
    
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
            fonte = pygame.font.SysFont("arial", 14, bold=True)
            texto_teste = fonte.render("♪ " + self.nome_musica, True, (255, 255, 255))
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
        
        # Posição final fixa
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
        
        if self.hover:
            # Verificar hover dos botões
            self.hover_anterior = self.botao_anterior_rect.collidepoint(
                mouse_x - self.posicao_x, 
                mouse_y - self.posicao_y
            )
            self.hover_proximo = self.botao_proximo_rect.collidepoint(
                mouse_x - self.posicao_x, 
                mouse_y - self.posicao_y
            )
        else:
            self.hover_anterior = False
            self.hover_proximo = False
        
        return self.hover
    
    def verificar_clique(self, mouse_x, mouse_y):
        """Verifica se o usuário clicou em algum botão"""
        if not self.ativo or not self.hover:
            return None
        
        # Verificar clique no botão anterior
        if self.botao_anterior_rect.collidepoint(
            mouse_x - self.posicao_x, 
            mouse_y - self.posicao_y
        ):
            return "anterior"
        
        # Verificar clique no botão próximo
        if self.botao_proximo_rect.collidepoint(
            mouse_x - self.posicao_x, 
            mouse_y - self.posicao_y
        ):
            return "proximo"
        
        return None
    
    def desenhar(self, tela):
        """Desenha o pop-up na tela"""
        if not self.ativo or self.alpha <= 0:
            return
        
        # Limpar superfície
        self.surface.fill((0, 0, 0, 0))
        
        # Desenhar fundo com bordas arredondadas
        pygame.draw.rect(self.surface, self.cor_fundo, (0, 0, self.largura, self.altura))
        pygame.draw.rect(self.surface, self.cor_borda, (0, 0, self.largura, self.altura), 2)
        
        # Desenhar disco de vinil rotativo
        if self.disco_rotacionado:
            # Centralizar o disco rotacionado
            disco_rect = self.disco_rotacionado.get_rect(center=(25, 25))
            self.surface.blit(self.disco_rotacionado, disco_rect)
        else:
            # Fallback: círculo simples se o disco não carregar
            pygame.draw.circle(self.surface, self.cor_texto, (25, 25), 15)
            pygame.draw.circle(self.surface, self.cor_fundo, (25, 25), 8)
        
        # Desenhar nome da música com animação deslizante
        fonte = pygame.font.SysFont("arial", 14, bold=True)
        texto_musica = fonte.render("♪ " + self.nome_musica, True, self.cor_texto)
        
        # Criar uma superfície de clipping para o texto (mais espaço)
        area_texto = pygame.Rect(50, 15, self.largura - 100, 20)
        clip_surface = pygame.Surface((area_texto.width, area_texto.height), pygame.SRCALPHA)
        
        # Desenhar o texto com offset (começa em 0, desliza para a esquerda)
        clip_surface.blit(texto_musica, (0 - self.texto_offset, 15 - area_texto.y))
        
        # Efeito de fade removido por enquanto para evitar problemas de cor
        
        # Aplicar o clipping
        self.surface.blit(clip_surface, (area_texto.x, area_texto.y))
        
        # Desenhar botão anterior
        cor_anterior = (255, 200, 100) if self.hover_anterior else (100, 150, 255)
        pygame.draw.rect(self.surface, cor_anterior, self.botao_anterior_rect)
        pygame.draw.rect(self.surface, self.cor_borda, self.botao_anterior_rect, 1)
        
        # Desenhar botão próximo
        cor_proximo = (255, 200, 100) if self.hover_proximo else (100, 150, 255)
        pygame.draw.rect(self.surface, cor_proximo, self.botao_proximo_rect)
        pygame.draw.rect(self.surface, self.cor_borda, self.botao_proximo_rect, 1)
        
        # Texto dos botões
        fonte_botao = pygame.font.SysFont("arial", 12, bold=True)
        texto_anterior = fonte_botao.render("<", True, self.cor_texto)
        texto_proximo = fonte_botao.render(">", True, self.cor_texto)
        
        # Centralizar o texto nos botões
        pos_x_anterior = self.botao_anterior_rect.x + (self.botao_anterior_rect.width - texto_anterior.get_width()) // 2
        pos_y_anterior = self.botao_anterior_rect.y + (self.botao_anterior_rect.height - texto_anterior.get_height()) // 2
        pos_x_proximo = self.botao_proximo_rect.x + (self.botao_proximo_rect.width - texto_proximo.get_width()) // 2
        pos_y_proximo = self.botao_proximo_rect.y + (self.botao_proximo_rect.height - texto_proximo.get_height()) // 2
        
        self.surface.blit(texto_anterior, (pos_x_anterior, pos_y_anterior))
        self.surface.blit(texto_proximo, (pos_x_proximo, pos_y_proximo))
        
        # Desenhar na tela principal com transparência
        if self.alpha < 255:
            # Criar uma cópia da superfície com alpha
            surface_alpha = self.surface.copy()
            surface_alpha.set_alpha(self.alpha)
            tela.blit(surface_alpha, (self.posicao_x, self.posicao_y))
        else:
            tela.blit(self.surface, (self.posicao_x, self.posicao_y))

# Instância global do pop-up
popup_musica = PopupMusica()
