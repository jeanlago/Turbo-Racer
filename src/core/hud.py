import pygame
import math
import os

# Importar render_text do menu para usar a mesma fonte
try:
    from core.menu import render_text
except ImportError:
    # Fallback caso não consiga importar
    def render_text(text, size, color=(255, 255, 255), bold=True, pixel_style=True):
        pygame.font.init()
        fonte = pygame.font.SysFont("consolas", size, bold=bold)
        return fonte.render(text, True, color)

class HUD:
    """
    Sistema de HUD para o jogo com velocímetro, ponteiro e informações do carro
    """
    
    def __init__(self):
        self.fonte_principal = pygame.font.SysFont("consolas", 24, bold=True)
        self.fonte_secundarIA = pygame.font.SysFont("consolas", 18)
        self.fonte_pequena = pygame.font.SysFont("consolas", 14)
        
        # Cores
        self.cor_principal = (255, 255, 255)
        self.cor_secundarIA = (200, 200, 200)
        self.cor_velocidade = (0, 255, 0)
        self.cor_rpm = (255, 165, 0)
        self.cor_marcha = (0, 255, 255)
        
        # Imagens (serão carregadas se existirem)
        self.imagem_fundo_hud = None
        self.imagem_nitro_cheio = None
        self.imagem_nitro_vazio = None
        
        # Carregar imagens se existirem
        self._carregar_imagens()
        
        # Configurações do novo velocímetro horizontal com PNGs
        self.velocimetro_posicao = (1000, 650)  # Posição do velocímetro (canto inferior direito, mais baixo)
        self.velocimetro_vmax = 180.0  # Velocidade máxima: 180 km/h
        self.velocimetro_largura = 250  # Largura desejada do velocímetro
        self.velocimetro_altura = 40  # Altura desejada do velocímetro
        
        # Imagens do velocímetro (colorido e sem cor)
        self.imagem_velocimetro_colorido = None
        self.imagem_velocimetro_sem_cor = None
        self._carregar_imagens_velocimetro()
        
        # Cache para animação suave
        self._velocidade_anterior = 0.0
        self._velocidade_alvo = 0.0
        
        # Configurações do nitro (ao lado do número do velocímetro)
        self.nitro_tamanho = (60, 60)   # Tamanho do ícone de nitro reduzido
        
        # Configurações do HUD (canto inferior esquerdo - minimapa)
        self.posicao_hud = (20, 510)  # Ajustado para ficar acima do velocímetro descido
        self.espacamento_linhas = 18  # Espaçamento compacto
        
    def _carregar_imagens(self):
        """Carrega imagens do HUD se existirem"""
        try:
            # Carregar fundo do HUD (se existir)
            caminho_fundo = "assets/images/icons/hud_fundo.png"
            if os.path.exists(caminho_fundo):
                self.imagem_fundo_hud = pygame.image.load(caminho_fundo).convert_alpha()
                print("Fundo do HUD carregado com sucesso!")
            
            # Carregar nitro (colorido)
            caminho_nitro_cheio = "assets/images/icons/nitro.png"
            if os.path.exists(caminho_nitro_cheio):
                self.imagem_nitro_cheio = pygame.image.load(caminho_nitro_cheio).convert_alpha()
                print("Nitro colorido carregado com sucesso!")
            
            # Carregar nitro vazio (preto e branco)
            caminho_nitro_vazio = "assets/images/icons/nitro_vazio.png"
            if os.path.exists(caminho_nitro_vazio):
                self.imagem_nitro_vazio = pygame.image.load(caminho_nitro_vazio).convert_alpha()
                print("Nitro vazio carregado com sucesso!")
                
        except Exception as e:
            print(f"Erro ao carregar imagens do HUD: {e}")
    
    def _carregar_imagens_velocimetro(self):
        """Carrega as 2 imagens do velocímetro (colorido e sem cor)"""
        try:
            # Tentar diferentes caminhos para a imagem colorida
            caminhos_colorido = [
                "assets/images/icons/velocimetro/velocimetro_colorido.png",
                "assets/images/icons/velocimetro_colorido.png",
                "assets/images/velocimetro/velocimetro_colorido.png",
                "assets/images/icons/velocimetro.png",
            ]
            
            for caminho in caminhos_colorido:
                if os.path.exists(caminho):
                    try:
                        img = pygame.image.load(caminho).convert_alpha()
                        # Redimensionar para o tamanho desejado
                        self.imagem_velocimetro_colorido = pygame.transform.scale(
                            img, (self.velocimetro_largura, self.velocimetro_altura)
                        )
                        print(f"Velocímetro colorido carregado e redimensionado: {caminho}")
                        break
                    except Exception as e:
                        print(f"Erro ao carregar {caminho}: {e}")
            
            # Tentar diferentes caminhos para a imagem sem cor (branco/preto)
            caminhos_sem_cor = [
                "assets/images/icons/velocimetro/velocimetro_sem_cor.png",
                "assets/images/icons/velocimetro_sem_cor.png",
                "assets/images/velocimetro/velocimetro_sem_cor.png",
                "assets/images/icons/velocimetro_branco.png",
                "assets/images/icons/velocimetro_vazio.png",
            ]
            
            for caminho in caminhos_sem_cor:
                if os.path.exists(caminho):
                    try:
                        img = pygame.image.load(caminho).convert_alpha()
                        # Redimensionar para o tamanho desejado
                        self.imagem_velocimetro_sem_cor = pygame.transform.scale(
                            img, (self.velocimetro_largura, self.velocimetro_altura)
                        )
                        print(f"Velocímetro sem cor carregado e redimensionado: {caminho}")
                        break
                    except Exception as e:
                        print(f"Erro ao carregar {caminho}: {e}")
            
            # Criar fallback se não encontrar as imagens
            if not self.imagem_velocimetro_colorido:
                print("Criando fallback para velocímetro colorido")
                self.imagem_velocimetro_colorido = pygame.Surface(
                    (self.velocimetro_largura, self.velocimetro_altura), pygame.SRCALPHA
                )
                self.imagem_velocimetro_colorido.fill((0, 255, 0, 200))
            
            if not self.imagem_velocimetro_sem_cor:
                print("Criando fallback para velocímetro sem cor")
                self.imagem_velocimetro_sem_cor = pygame.Surface(
                    (self.velocimetro_largura, self.velocimetro_altura), pygame.SRCALPHA
                )
                self.imagem_velocimetro_sem_cor.fill((200, 200, 200, 200))
                    
        except Exception as e:
            print(f"Erro ao carregar imagens do velocímetro: {e}")
    
    
    def _obter_cor_por_velocidade(self, velocidade_kmh):
        """Retorna a cor baseada na velocidade (muda a cada 10km/h até 180km/h)"""
        # Limitar velocidade a 180 km/h
        velocidade_kmh = min(velocidade_kmh, 180.0)
        
        # Calcular qual faixa de 10km estamos (0-9, 10-19, 20-29, etc.)
        faixa = int(velocidade_kmh // 10)
        
        # Definir cores para cada faixa de 10km (18 faixas de 0 a 180)
        # Gradiente de verde (baixo) -> amarelo -> laranja -> vermelho (alto)
        cores = [
            (0, 255, 0),      # 0-9: Verde
            (50, 255, 0),     # 10-19: Verde claro
            (100, 255, 0),    # 20-29: Verde amarelado
            (150, 255, 0),    # 30-39: Amarelo esverdeado
            (200, 255, 0),    # 40-49: Amarelo
            (255, 255, 0),    # 50-59: Amarelo puro
            (255, 220, 0),    # 60-69: Amarelo alaranjado
            (255, 180, 0),    # 70-79: Laranja claro
            (255, 140, 0),    # 80-89: Laranja
            (255, 100, 0),    # 90-99: Laranja escuro
            (255, 80, 0),     # 100-109: Vermelho alaranjado
            (255, 60, 0),     # 110-119: Vermelho laranja
            (255, 40, 0),     # 120-129: Vermelho
            (255, 20, 0),     # 130-139: Vermelho escuro
            (255, 0, 0),      # 140-149: Vermelho puro
            (220, 0, 0),      # 150-159: Vermelho muito escuro
            (180, 0, 0),      # 160-169: Vermelho quase preto
            (150, 0, 0),      # 170-180: Vermelho muito escuro
        ]
        
        # Garantir que não ultrapasse o índice
        faixa = min(faixa, len(cores) - 1)
        return cores[faixa]
    
    def desenhar_velocimetro(self, superficie, carro, dt=0.016):
        """Desenha o velocímetro horizontal com 2 PNGs (colorido e sem cor), similar ao nitro."""
        if not carro:
            return

        # Obter velocidade (km/h)
        if hasattr(carro, 'velocidade_kmh'):
            velocidade_kmh = float(carro.velocidade_kmh)
        else:
            velocidade_kmh = abs(float(getattr(carro, 'velocidade', 0.0))) * 1.0 * (200.0 / 650.0)

        # Limitar velocidade a 180 km/h
        velocidade_kmh = min(velocidade_kmh, self.velocimetro_vmax)
        velocidade_kmh = max(0.0, velocidade_kmh)

        # Animar suavemente a velocidade (similar ao nitro)
        velocidade_suavizada = velocidade_kmh
        if abs(velocidade_kmh - self._velocidade_alvo) > 0.1:
            # Interpolação suave
            velocidade_suavizada = self._velocidade_anterior + (velocidade_kmh - self._velocidade_anterior) * min(1.0, dt * 8.0)
            self._velocidade_anterior = velocidade_suavizada
        else:
            self._velocidade_anterior = velocidade_kmh
        
        self._velocidade_alvo = velocidade_kmh

        # Posição do velocímetro
        x, y = self.velocimetro_posicao

        # Desenhar número da velocidade usando a fonte do menu
        vel_texto = f"{int(velocidade_suavizada)}"
        texto_surface = render_text(vel_texto, 48, (255, 255, 255), bold=True, pixel_style=True)
        
        # Posicionar o número acima do velocímetro
        texto_x = x
        texto_y = y - texto_surface.get_height() - 10
        superficie.blit(texto_surface, (texto_x, texto_y))

        # Calcular porcentagem de velocidade (0.0 a 1.0)
        porcentagem_velocidade = velocidade_suavizada / self.velocimetro_vmax
        porcentagem_velocidade = max(0.0, min(1.0, porcentagem_velocidade))

        # Desenhar velocímetro similar ao nitro
        if self.imagem_velocimetro_colorido and self.imagem_velocimetro_sem_cor:
            # Obter tamanho das imagens
            largura = self.imagem_velocimetro_colorido.get_width()
            altura = self.imagem_velocimetro_colorido.get_height()
            
            # Criar superfície para o velocímetro
            velocimetro_surface = pygame.Surface((largura, altura), pygame.SRCALPHA)
            
            # Desenhar versão colorida como base
            velocimetro_surface.blit(self.imagem_velocimetro_colorido, (0, 0))
            
            # Calcular largura da área sem cor que "cobre" da direita para esquerda
            # (similar ao nitro que cobre de cima para baixo)
            largura_sem_cor = int(largura * (1.0 - porcentagem_velocidade))
            
            if largura_sem_cor > 0:
                # Criar uma superfície para a área sem cor
                area_sem_cor = pygame.Surface((largura_sem_cor, altura), pygame.SRCALPHA)
                
                # Desenhar a versão sem cor (branco/preto) na área
                # Cortar apenas a parte direita da imagem sem cor
                area_sem_cor.blit(self.imagem_velocimetro_sem_cor, (0, 0), 
                                 (largura - largura_sem_cor, 0, largura_sem_cor, altura))
                
                # Aplicar a área sem cor na parte direita do velocímetro
                velocimetro_surface.blit(area_sem_cor, (largura - largura_sem_cor, 0))
            
            # Desenhar o velocímetro na tela
            superficie.blit(velocimetro_surface, (x, y))
        else:
            # Fallback: desenhar barra simples
            barra_largura = 300
            barra_altura = 30
            largura_preenchida = int(barra_largura * porcentagem_velocidade)
            
            pygame.draw.rect(superficie, (40, 40, 40), (x, y, barra_largura, barra_altura))
            if largura_preenchida > 0:
                cor = self._obter_cor_por_velocidade(velocidade_suavizada)
                pygame.draw.rect(superficie, cor, (x, y, largura_preenchida, barra_altura))
    
    def desenhar_informacoes_carro(self, superficie, carro, posicao=(20, 200)):
        """Desenha informações detalhadas do carro"""
        if not carro:
            return
        
        y = posicao[1]
        
        # Nome do carro
        texto_nome = self.fonte_principal.render(f"{carro.nome}", True, self.cor_principal)
        superficie.blit(texto_nome, (posicao[0], y))
        y += self.espacamento_linhas
        
        # Velocidade
        velocidade_kmh = abs(carro.velocidade) * 1.0 * (200.0 / 650.0)  # escala automática
        texto_velocidade = self.fonte_secundarIA.render(f"Velocidade: {int(velocidade_kmh)} km/h", True, self.cor_velocidade)
        superficie.blit(texto_velocidade, (posicao[0], y))
        y += self.espacamento_linhas
        
        # RPM (se disponível)
        if hasattr(carro, 'rpm'):
            texto_rpm = self.fonte_secundarIA.render(f"RPM: {int(carro.rpm)}", True, self.cor_rpm)
            superficie.blit(texto_rpm, (posicao[0], y))
            y += self.espacamento_linhas
        
        # Marcha (se disponível)
        if hasattr(carro, 'marcha_atual'):
            marcha_texto = "R" if carro.marcha_atual == -1 else "N" if carro.marcha_atual == 0 else str(carro.marcha_atual)
            texto_marcha = self.fonte_secundarIA.render(f"Marcha: {marcha_texto}", True, self.cor_marcha)
            superficie.blit(texto_marcha, (posicao[0], y))
            y += self.espacamento_linhas
        
        # Turbo (se disponível)
        if hasattr(carro, 'turbo_carga'):
            texto_turbo = self.fonte_secundarIA.render(f"Turbo: {int(carro.turbo_carga)}%", True, self.cor_secundarIA)
            superficie.blit(texto_turbo, (posicao[0], y))
            y += self.espacamento_linhas
        
        # Drift (se ativo)
        if hasattr(carro, 'drift_ativado') and carro.drift_ativado:
            texto_drift = self.fonte_secundarIA.render("DRIFT ATIVO!", True, (255, 0, 255))
            superficie.blit(texto_drift, (posicao[0], y))
            y += self.espacamento_linhas
        
        # Freio de mão (se ativo)
        if hasattr(carro, 'freio_mao_ativo') and carro.freio_mao_ativo:
            texto_freio = self.fonte_secundarIA.render("FREIO DE MÃO!", True, (255, 100, 100))
            superficie.blit(texto_freio, (posicao[0], y))
            y += self.espacamento_linhas
    
    def desenhar_nitro(self, superficie, carro, posicao_nitro=None):
        """Desenha o indicador de nitro ao lado do número do velocímetro"""
        if not carro or not hasattr(carro, 'turbo_carga'):
            return
        
        # Obter informações do turbo (que é o nitro) do carro
        nitro_atual = getattr(carro, 'turbo_carga', 0.0)
        nitro_max = 100.0  # Turbo sempre vai de 0 a 100
        usando_nitro = getattr(carro, 'turbo_ativo', False)
        
        # Calcular porcentagem do nitro (0.0 a 1.0)
        porcentagem_nitro = nitro_atual / nitro_max if nitro_max > 0 else 0.0
        porcentagem_nitro = max(0.0, min(1.0, porcentagem_nitro))
        
        # Posição do nitro (se não fornecida, usar posição padrão)
        if posicao_nitro:
            nitro_x, nitro_y = posicao_nitro
        else:
            # Posição padrão (fallback)
            nitro_x = 1000 - self.nitro_tamanho[0] - 10
            nitro_y = 600
        
        # Desenhar nitro com efeito de "descida" do cinza
        if self.imagem_nitro_cheio and self.imagem_nitro_vazio:
            # Criar superfície para o nitro
            nitro_surface = pygame.Surface(self.nitro_tamanho, pygame.SRCALPHA)
            
            # Desenhar versão colorida como base
            nitro_cheio_escalado = pygame.transform.scale(self.imagem_nitro_cheio, self.nitro_tamanho)
            nitro_surface.blit(nitro_cheio_escalado, (0, 0))
            
            # Calcular altura da área cinza que "desce" conforme o nitro esvazia
            altura_cinza = int(self.nitro_tamanho[1] * (1.0 - porcentagem_nitro))
            
            if altura_cinza > 0:
                # Criar uma superfície para a área cinza
                area_cinza = pygame.Surface((self.nitro_tamanho[0], altura_cinza), pygame.SRCALPHA)
                
                # Desenhar a versão preto/branco na área cinza
                nitro_vazio_escalado = pygame.transform.scale(self.imagem_nitro_vazio, self.nitro_tamanho)
                # Cortar apenas a parte superior da imagem preto/branco
                area_cinza.blit(nitro_vazio_escalado, (0, 0), (0, 0, self.nitro_tamanho[0], altura_cinza))
                
                # Aplicar a área cinza na parte superior do nitro
                nitro_surface.blit(area_cinza, (0, 0))
            
            superficie.blit(nitro_surface, (nitro_x, nitro_y))
        else:
            # Fallback: desenhar círculos coloridos
            if porcentagem_nitro >= 1.0:
                pygame.draw.circle(superficie, (0, 255, 0), (nitro_x + 40, nitro_y + 40), 40)
            elif porcentagem_nitro > 0.0:
                pygame.draw.circle(superficie, (255, 255, 0), (nitro_x + 40, nitro_y + 40), 40)
            else:
                pygame.draw.circle(superficie, (128, 128, 128), (nitro_x + 40, nitro_y + 40), 40)
        
        # Borda removida conforme solicitado
        
        # Porcentagem removida para HUD mais limpo
    
    def desenhar_hud_completo(self, superficie, carro, dt=0.016):
        """Desenha o HUD completo - versão limpa"""
        if not carro:
            return
        
        # Desenhar fundo do HUD se disponível
        if self.imagem_fundo_hud:
            superficie.blit(self.imagem_fundo_hud, (0, 0))
        
        # Calcular posição do nitro antes de desenhar (precisa das informações do velocímetro)
        # Obter velocidade para calcular posição do número
        if hasattr(carro, 'velocidade_kmh'):
            velocidade_kmh = float(carro.velocidade_kmh)
        else:
            velocidade_kmh = abs(float(getattr(carro, 'velocidade', 0.0))) * 1.0 * (200.0 / 650.0)
        velocidade_kmh = min(velocidade_kmh, self.velocimetro_vmax)
        velocidade_kmh = max(0.0, velocidade_kmh)
        
        # Calcular posição do número do velocímetro
        x, y = self.velocimetro_posicao
        vel_texto = f"{int(velocidade_kmh)}"
        texto_surface = render_text(vel_texto, 48, (255, 255, 255), bold=True, pixel_style=True)
        texto_x = x
        texto_y = y - texto_surface.get_height() - 10
        
        # Calcular posição do nitro ao lado do número
        nitro_x = texto_x - self.nitro_tamanho[0] - 10
        nitro_y = texto_y + (texto_surface.get_height() - self.nitro_tamanho[1]) // 2
        
        # Desenhar velocímetro
        self.desenhar_velocimetro(superficie, carro, dt)
        
        # Desenhar nitro na posição calculada
        self.desenhar_nitro(superficie, carro, (nitro_x, nitro_y))
        
        # HUD limpo - apenas velocímetro e nitro
    
    def desenhar_minimapa(self, superficie, carro, checkpoints, camera, posicao=(50, 550)):
        """Desenha um minimapa simples"""
        if not carro or not checkpoints:
            return
        
        # Tamanho do minimapa circular (como na imagem)
        minimapa_raio = 60  # Raio do minimapa circular
        
        # Desenhar fundo circular do minimapa
        pygame.draw.circle(superficie, (0, 0, 0), (posicao[0] + minimapa_raio, posicao[1] + minimapa_raio), minimapa_raio)
        pygame.draw.circle(superficie, (100, 100, 100), (posicao[0] + minimapa_raio, posicao[1] + minimapa_raio), minimapa_raio, 2)
        
        # Calcular escala do minimapa
        if checkpoints:
            # Encontrar limites dos checkpoints
            min_x = min(cp[0] for cp in checkpoints)
            max_x = max(cp[0] for cp in checkpoints)
            min_y = min(cp[1] for cp in checkpoints)
            max_y = max(cp[1] for cp in checkpoints)
            
            # Adicionar margem
            margem = 50
            min_x -= margem
            max_x += margem
            min_y -= margem
            max_y += margem
            
            # Calcular escala para minimapa circular
            escala_x = (minimapa_raio * 2) / (max_x - min_x)
            escala_y = (minimapa_raio * 2) / (max_y - min_y)
            escala = min(escala_x, escala_y)
            
            # Centro do minimapa circular
            centro_x = posicao[0] + minimapa_raio
            centro_y = posicao[1] + minimapa_raio
            
            # Desenhar checkpoints
            for i, (cx, cy) in enumerate(checkpoints):
                x = centro_x + (cx - min_x) * escala - (max_x - min_x) * escala / 2
                y = centro_y + (cy - min_y) * escala - (max_y - min_y) * escala / 2
                
                # Verificar se está dentro do círculo
                distancia_centro = ((x - centro_x) ** 2 + (y - centro_y) ** 2) ** 0.5
                if distancia_centro <= minimapa_raio - 5:  # Margem de 5 pixels
                    cor = (0, 255, 0) if i < getattr(carro, 'checkpoint_atual', 0) else (255, 0, 0) if i == getattr(carro, 'checkpoint_atual', 0) else (128, 128, 128)
                    pygame.draw.circle(superficie, cor, (int(x), int(y)), 3)
            
            # Desenhar posição do carro no minimapa circular
            carro_x = centro_x + (carro.x - min_x) * escala - (max_x - min_x) * escala / 2
            carro_y = centro_y + (carro.y - min_y) * escala - (max_y - min_y) * escala / 2
            
            # Verificar se o carro está dentro do círculo
            distancia_carro = ((carro_x - centro_x) ** 2 + (carro_y - centro_y) ** 2) ** 0.5
            if distancia_carro <= minimapa_raio - 5:
                pygame.draw.circle(superficie, (0, 255, 255), (int(carro_x), int(carro_y)), 5)
                # Desenhar direção do carro
                angulo_rad = math.radians(carro.angulo)
                dir_x = carro_x + 10 * math.cos(angulo_rad)
                dir_y = carro_y + 10 * math.sin(angulo_rad)
                pygame.draw.line(superficie, (0, 255, 255), (carro_x, carro_y), (dir_x, dir_y), 2)
