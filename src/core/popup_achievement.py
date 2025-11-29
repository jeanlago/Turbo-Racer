import pygame
import os
import math
from config import LARGURA, ALTURA, DIR_PROJETO

class PopupAchievement:
    def __init__(self):
        self.ativo = False
        self.tempo_visivel = 0.0
        self.duracao_visivel = 4.0  # Duração menor que música
        self.velocidade_animacao = 200.0
        self.posicao_x = LARGURA
        self.posicao_y = 20
        self.largura = 400
        self.altura = 80
        self.alpha = 0
        self.hover = False
        self.texto_offset = 0
        self.texto_velocidade = 50
        self.texto_tempo = 0
        self.texto_pausa = 1.5
        self.texto_estado = "pausa"
        self.texto_largura_total = 0
        self.texto_largura_disponivel = 0
        self.texto_terminou_deslizar = False
        self.tempo_apos_deslizar = 0
        
        self.icone_achievement = None
        self.icone_concluido = None
        self.icone_carregado = False
        self.tempo_piscar = 0.0
        
        self.cor_fundo = (0, 0, 0)
        self.cor_borda = (255, 215, 0)  # Dourado para achievements
        self.cor_texto = (255, 255, 255)
        
        self.surface = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        self.nome_achievement = ""
        self.recompensa = 0
    
    def carregar_icones(self):
        """Carrega os ícones de achievement e concluído"""
        try:
            caminho_achievement = os.path.join(DIR_PROJETO, "assets", "images", "icons", "achievements.png")
            if os.path.exists(caminho_achievement):
                self.icone_achievement = pygame.image.load(caminho_achievement).convert_alpha()
                self.icone_achievement = pygame.transform.scale(self.icone_achievement, (40, 40))
            else:
                self.criar_icone_achievement_simples()
            
            caminhos_concluido = [
                os.path.join(DIR_PROJETO, "assets", "images", "icons", "concluido.png"),
                os.path.join(DIR_PROJETO, "assets", "images", "icons", "check.png"),
                os.path.join(DIR_PROJETO, "assets", "images", "icons", "checkmark.png"),
                os.path.join(DIR_PROJETO, "assets", "images", "icons", "done.png"),
            ]
            
            for caminho in caminhos_concluido:
                if os.path.exists(caminho):
                    self.icone_concluido = pygame.image.load(caminho).convert_alpha()
                    self.icone_concluido = pygame.transform.scale(self.icone_concluido, (30, 30))
                    break
            
            if self.icone_concluido is None:
                self.criar_icone_concluido_simples()
                
        except Exception as e:
            print(f"Erro ao carregar ícones de achievement: {e}")
            self.criar_icone_achievement_simples()
            self.criar_icone_concluido_simples()
    
    def criar_icone_achievement_simples(self):
        """Cria um ícone de achievement simples"""
        self.icone_achievement = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.icone_achievement, (255, 215, 0), (20, 20), 18, 3)
        pygame.draw.circle(self.icone_achievement, (255, 215, 0), (20, 20), 12, 2)
    
    def criar_icone_concluido_simples(self):
        """Cria um ícone de checkmark simples"""
        self.icone_concluido = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.line(self.icone_concluido, (0, 255, 0), (8, 15), (12, 20), 3)
        pygame.draw.line(self.icone_concluido, (0, 255, 0), (12, 20), (22, 8), 3)
    
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
    
    def mostrar(self, nome_achievement, recompensa=0):
        """Mostra o pop-up com o achievement desbloqueado
        
        Args:
            nome_achievement: Nome do achievement (pode ser chave de tradução ou texto direto)
            recompensa: Valor da recompensa em dinheiro
        """
        try:
            from core.i18n import t
            mapeamento_traducoes = {
                "Primeira Corrida": "achievements.primeira_corrida",
                "Velocista": "achievements.velocista",
                "Mestre do Drift": "achievements.drift_master",
                "Piloto Limpo": "achievements.sem_colisao",
                "Campeão": "achievements.trofeu_ouro",
                "Colecionador": "achievements.colecionador",
                "Perfeccionista": "achievements.perfeccionista",
                "Recordista": "achievements.recordista",
                "Tunado": "achievements.upgrade_completo",
                "Veterano": "achievements.veterano",
            }
            if nome_achievement in mapeamento_traducoes:
                nome_achievement = t(mapeamento_traducoes[nome_achievement])
        except:
            pass
        
        self.ativo = True
        self.tempo_visivel = 0.0
        self.nome_achievement = nome_achievement
        self.recompensa = recompensa
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
            self.carregar_icones()
            self.icone_carregado = True
        
        self.tempo_piscar += dt
        
        if hasattr(self, 'nome_achievement') and self.nome_achievement:
            nome_limpo = self.limpar_caracteres_especiais(self.nome_achievement)
            fonte = pygame.font.SysFont("arial", 16, bold=True)
            texto_teste = fonte.render(nome_limpo, True, (255, 255, 255))
            self.texto_largura_total = texto_teste.get_width()
            self.texto_largura_disponivel = self.largura - 120
            
            if self.texto_largura_total > self.texto_largura_disponivel:
                self.texto_tempo += dt
                max_offset = self.texto_largura_total - self.texto_largura_disponivel
                ciclo_tempo = 5.0
                tempo_ciclo = self.texto_tempo % ciclo_tempo
                
                if tempo_ciclo < 1.0:
                    self.texto_offset = 0
                elif tempo_ciclo < 2.5:
                    progresso = (tempo_ciclo - 1.0) / 1.5
                    self.texto_offset = int(progresso * max_offset)
                elif tempo_ciclo < 3.0:
                    self.texto_offset = max_offset
                elif tempo_ciclo < 4.5:
                    progresso = (tempo_ciclo - 3.0) / 1.5
                    self.texto_offset = int(max_offset - progresso * max_offset)
                else:
                    self.texto_offset = 0
            else:
                self.texto_offset = 0
        
        posicao_final = LARGURA - self.largura - 20
        
        if self.tempo_visivel < 0.8:
            progresso = self.tempo_visivel / 0.8
            self.posicao_x = int(LARGURA - progresso * (LARGURA - posicao_final))
            self.alpha = int(255 * progresso)
        elif self.tempo_visivel < self.duracao_visivel - 0.8:
            self.posicao_x = posicao_final
            self.alpha = 255
        else:
            progresso = (self.tempo_visivel - (self.duracao_visivel - 0.8)) / 0.8
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
    
    def desenhar(self, tela):
        """Desenha o pop-up na tela"""
        if not self.ativo or self.alpha <= 0:
            return
        
        self.surface = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 0))
        
        # Efeito de piscar dourado
        ciclo_piscar = (self.tempo_piscar * 3.0) % 2.0
        if ciclo_piscar < 1.0:
            intensidade = abs(ciclo_piscar - 0.5) * 2.0
            dourado = (255, 215, 0)
            cor_borda_atual = (
                int(self.cor_borda[0] * (1 - intensidade * 0.3) + dourado[0] * intensidade * 0.3),
                int(self.cor_borda[1] * (1 - intensidade * 0.3) + dourado[1] * intensidade * 0.3),
                int(self.cor_borda[2] * (1 - intensidade * 0.3) + dourado[2] * intensidade * 0.3)
            )
        else:
            cor_borda_atual = self.cor_borda
        
        pygame.draw.rect(self.surface, self.cor_fundo, (0, 0, self.largura, self.altura), border_radius=8)
        pygame.draw.rect(self.surface, cor_borda_atual, (0, 0, self.largura, self.altura), 3, border_radius=8)
        
        nome_limpo = self.limpar_caracteres_especiais(self.nome_achievement)
        fonte = pygame.font.SysFont("arial", 16, bold=True)
        texto_achievement = fonte.render(nome_limpo, True, self.cor_texto)
        
        texto_recompensa = ""
        if self.recompensa > 0:
            fonte_recompensa = pygame.font.SysFont("arial", 14, bold=True)
            texto_recompensa = fonte_recompensa.render(f"+${self.recompensa}", True, (255, 215, 0))
        
        texto_altura = texto_achievement.get_height()
        area_texto_y = (self.altura - texto_altura) // 2 - (8 if texto_recompensa else 0)
        area_texto = pygame.Rect(15, area_texto_y, self.largura - 30, texto_altura + 4)
        clip_surface = pygame.Surface((area_texto.width, area_texto.height), pygame.SRCALPHA)
        clip_surface.blit(texto_achievement, (0 - self.texto_offset, 0))
        self.surface.blit(clip_surface, (area_texto.x, area_texto.y))
        
        if texto_recompensa:
            recompensa_y = area_texto_y + texto_altura + 4
            self.surface.blit(texto_recompensa, (15, recompensa_y))
        
        if self.alpha < 255:
            surface_alpha = self.surface.copy()
            surface_alpha.set_alpha(self.alpha)
            tela.blit(surface_alpha, (self.posicao_x, self.posicao_y))
        else:
            tela.blit(self.surface, (self.posicao_x, self.posicao_y))

popup_achievement = PopupAchievement()

