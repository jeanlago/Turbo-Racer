import pygame
import math
import os

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
        
        # Configurações do ponteiro (valores fixos otimizados)
        self.ponteiro_offset_x = 1
        self.ponteiro_offset_y = 23
        self.ponteiro_escala_atual = 0.07  # Reduzido de 0.1 para 0.07
        self.ponteiro_pivo_x = 180.69452265072886
        self.ponteiro_pivo_y = 1.2977856569646988
        self.ponteiro_angulo_inicial = 215
        self.pivo_sprite_x = 180.69452265072886
        self.pivo_sprite_y = 1.2977856569646988
        self.ponteiro_comprimento_relativo = 0.1
        self._ultimo_angulo_desenho = 0.0
        
        # Imagens (serão carregadas se existirem)
        self.imagem_velocimetro = None
        self.imagem_ponteiro = None
        self.imagem_fundo_hud = None
        self.imagem_nitro_cheio = None
        self.imagem_nitro_vazio = None
        
        # Carregar imagens se existirem
        self._carregar_imagens()
        
        # Configurações do velocímetro (canto inferior direito)
        self.velocimetro_centro = (1170, 630)
        self.velocimetro_raio = 80  # Reduzido de 150 para 100
        self.velocimetro_vmax = 250.0  # km/h para escala (ajustado para velocidade real do jogo)
        
        # Configurações do nitro (ao lado esquerdo do velocímetro)
        self.nitro_centro = (1080, 675)  # Posição mais à direita do velocímetro
        self.nitro_tamanho = (60, 60)   # Tamanho do ícone de nitro reduzido
        # Ângulos do mostrador (em graus). Usando arco completo do velocímetro
        # -135° a 135° = 270° de arco (3/4 de círculo)
        self.velocimetro_ang_min = -135.0
        self.velocimetro_ang_max = 135.0
        # Offset para alinhar a orientação do sprite do ponteiro
        # -90° para ponteiro que aponta para cima no sprite original
        self.ponteiro_offset_graus = -90.0
        # Comprimento relativo do ponteiro em relação ao raio do velocímetro
        self.ponteiro_comprimento_relativo = 0.85
        
        # Configurações do HUD (canto inferior esquerdo - minimapa)
        self.posicao_hud = (20, 510)  # Ajustado para ficar acima do velocímetro descido
        self.espacamento_linhas = 18  # Espaçamento compacto
        
    def _carregar_imagens(self):
        """Carrega imagens do HUD se existirem"""
        try:
            # Carregar velocímetro
            caminho_velocimetro = "assets/images/icons/velocimetro.png"
            if os.path.exists(caminho_velocimetro):
                self.imagem_velocimetro = pygame.image.load(caminho_velocimetro).convert_alpha()
                print("Velocímetro carregado com sucesso!")
            
            # Carregar ponteiro
            caminho_ponteiro = "assets/images/icons/ponteiro.png"
            if os.path.exists(caminho_ponteiro):
                self.imagem_ponteiro = pygame.image.load(caminho_ponteiro).convert_alpha()
                print("Ponteiro carregado com sucesso!")
            
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
    
    
    def _calcular_ponta_ponteiro(self, angulo_graus=None):
        """Calcula a posição da ponta do ponteiro para um ângulo específico"""
        if angulo_graus is None:
            angulo_graus = 0  # Ângulo base para edição
        
        comprimento_ponteiro = self.velocimetro_raio * self.ponteiro_comprimento_relativo
        import math
        angulo_rad = math.radians(angulo_graus)
        ponta_x = self.velocimetro_centro[0] + comprimento_ponteiro * math.cos(angulo_rad)
        ponta_y = self.velocimetro_centro[1] + comprimento_ponteiro * math.sin(angulo_rad)
        return ponta_x, ponta_y
    
    def _escala_atual_sprite(self):
        """Calcula a escala atual do sprite do ponteiro"""
        if not self.imagem_ponteiro:
            return 1.0
        # Usar uma escala fixa menor para manter o ponteiro no tamanho original do arquivo
        return 0.10  # Escala menor para ponteiro mais proporcional
    
    def _calcular_centro_ponteiro(self):
        """Calcula a posição do centro do ponteiro (bolinha vermelha)"""
        # centro = velocímetro + offset do ponteiro
        return (self.velocimetro_centro[0] + self.ponteiro_offset_x,
                self.velocimetro_centro[1] + self.ponteiro_offset_y)
    
    
    
    def _rotozoom_com_pivo(self, surf, ang_graus, escala, piv_rel_centro):
        """
        Gira/escala 'surf' em torno de um pivô (x,y) dado em coordenadas
        RELATIVAS AO CENTRO do sprite original. Retorna (rot, rect).
        """
        w, h = surf.get_width(), surf.get_height()
        # surface âncora grandinha p/ evitar crop
        anc_w, anc_h = int(w*3), int(h*3)
        ancora = pygame.Surface((anc_w, anc_h), pygame.SRCALPHA)

        # onde fica o centro da âncora
        cx, cy = anc_w // 2, anc_h // 2

        # pivô é relativo ao CENTRO do sprite.
        piv_x, piv_y = piv_rel_centro  # (ex.: -28.54, -33.38)

        # top-left do sprite dentro da âncora para que o PIVÔ caIA no centro da âncora
        tl_x = cx - (w/2 + piv_x)
        tl_y = cy - (h/2 + piv_y)

        ancora.blit(surf, (tl_x, tl_y))
        rot = pygame.transform.rotozoom(ancora, ang_graus, escala)
        rect = rot.get_rect()  # vamos só posicionar depois
        return rot, rect
    
    
    
    
    def desenhar_velocimetro(self, superficie, carro):
        """Desenha o velocímetro com ponteiro (pivô correto e rotação horárIA)."""
        if not carro:
            return

        # Velocidade (km/h) - ajustada para nova escala
        if hasattr(carro, 'velocidade_kmh'):
            velocidade_kmh = float(carro.velocidade_kmh)  # Usar valor já calculado
        else:
            velocidade_kmh = abs(float(getattr(carro, 'velocidade', 0.0))) * 1.0 * (200.0 / 650.0)  # escala automática

        # Fundo do velocímetro
        if self.imagem_velocimetro:
            w0 = self.imagem_velocimetro.get_width()
            h0 = self.imagem_velocimetro.get_height()
            esc = (self.velocimetro_raio * 2) / max(w0, h0)
            nw, nh = int(w0 * esc), int(h0 * esc)
            img = pygame.transform.smoothscale(self.imagem_velocimetro, (nw, nh))
            superficie.blit(img, (self.velocimetro_centro[0] - nw // 2,
                                  self.velocimetro_centro[1] - nh // 2))

        # Ponteiro do velocímetro
        if self.imagem_ponteiro:
            # Mapear velocidade para ângulo dentro do arco definido
            # 0 km/h = ângulo mínimo, velocidade máxima = ângulo máximo
            v = max(0.0, min(velocidade_kmh, self.velocimetro_vmax))
            t = v / self.velocimetro_vmax  # t vai de 0 a 1
            angulo_graus = self.velocimetro_ang_min + t * (self.velocimetro_ang_max - self.velocimetro_ang_min)
            
            # Calcular comprimento do ponteiro
            comprimento_ponteiro = self.velocimetro_raio * self.ponteiro_comprimento_relativo
            
            # Calcular posição da ponta do ponteiro baseada no ângulo (para rotação)
            import math
            angulo_rad = math.radians(angulo_graus)
            ponta_angulo_x = self.velocimetro_centro[0] + comprimento_ponteiro * math.cos(angulo_rad)
            ponta_angulo_y = self.velocimetro_centro[1] + comprimento_ponteiro * math.sin(angulo_rad)

            # Aplicar offset para orientação do sprite, ângulo inicial e converter para rotação do pygame
            # O pygame rota no sentido anti-horário, então invertemos o ângulo
            angulo_desenho = -(angulo_graus + self.ponteiro_offset_graus + self.ponteiro_angulo_inicial)

            # Escala usada no sprite
            esc = self._escala_atual_sprite()
            
            # Centro no MUNDO = bolinha vermelha já ajustada
            centro_ponteiro_x = self.velocimetro_centro[0] + self.ponteiro_offset_x
            centro_ponteiro_y = self.velocimetro_centro[1] + self.ponteiro_offset_y

            # atualize antes de chamar _desenhar_info...
            self._ultimo_angulo_desenho = angulo_desenho

            # gira/escala tendo o PIVÔ DO SPRITE = (pivo_sprite_x, pivo_sprite_y) (rel. ao centro do sprite)
            ponteiro_rot, rect_rot = self._rotozoom_com_pivo(
                self.imagem_ponteiro,
                angulo_desenho,
                esc,
                (self.pivo_sprite_x, self.pivo_sprite_y)
            )

            # agora é fácil: blita CENTRALIZANDO no ponto vermelho
            rect_rot.center = (int(centro_ponteiro_x), int(centro_ponteiro_y))
            superficie.blit(ponteiro_rot, rect_rot.topleft)

        # Texto de velocidade (debug/visual) - otimizado com cache
        if hasattr(carro, 'velocidade_kmh'):
            if not hasattr(self, '_fonte_vel_cache'):
                self._fonte_vel_cache = pygame.font.SysFont("consolas", 24, bold=True)
                self._fundo_vel_cache = None
                self._velocidade_texto_cache = None
            
            vel_int = int(velocidade_kmh)
            if self._velocidade_texto_cache != vel_int:
                txt = self._fonte_vel_cache.render(f"{vel_int} km/h", True, (255, 255, 255))
                self._fundo_vel_cache = pygame.Surface((txt.get_width() + 10, txt.get_height() + 5), pygame.SRCALPHA)
                self._fundo_vel_cache.fill((0, 0, 0, 150))
                self._texto_vel_cache = txt
                self._velocidade_texto_cache = vel_int
            
            tx = self.velocimetro_centro[0] - self._texto_vel_cache.get_width() // 2
            ty = self.velocimetro_centro[1] + self.velocimetro_raio + 20
            superficie.blit(self._fundo_vel_cache, (tx - 5, ty - 2))
            superficie.blit(self._texto_vel_cache, (tx, ty))
    
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
    
    def desenhar_nitro(self, superficie, carro):
        """Desenha o indicador de nitro ao lado esquerdo do velocímetro"""
        if not carro or not hasattr(carro, 'turbo_carga'):
            return
        
        # Obter informações do turbo (que é o nitro) do carro
        nitro_atual = getattr(carro, 'turbo_carga', 0.0)
        nitro_max = 100.0  # Turbo sempre vai de 0 a 100
        usando_nitro = getattr(carro, 'turbo_ativo', False)
        
        # Calcular porcentagem do nitro (0.0 a 1.0)
        porcentagem_nitro = nitro_atual / nitro_max if nitro_max > 0 else 0.0
        porcentagem_nitro = max(0.0, min(1.0, porcentagem_nitro))
        
        # Posição do nitro
        nitro_x = self.nitro_centro[0] - self.nitro_tamanho[0] // 2
        nitro_y = self.nitro_centro[1] - self.nitro_tamanho[1] // 2
        
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
    
    def desenhar_hud_completo(self, superficie, carro):
        """Desenha o HUD completo - versão limpa"""
        if not carro:
            return
        
        # Desenhar fundo do HUD se disponível
        if self.imagem_fundo_hud:
            superficie.blit(self.imagem_fundo_hud, (0, 0))
        
        # Desenhar velocímetro
        self.desenhar_velocimetro(superficie, carro)
        
        # Desenhar nitro
        self.desenhar_nitro(superficie, carro)
        
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
