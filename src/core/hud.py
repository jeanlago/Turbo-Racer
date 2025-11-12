import pygame
import math
import os
from config import DIR_ICONS, LARGURA, ALTURA

class HUD:
    """
    Sistema de HUD para o jogo com velocímetro, ponteiro e informações do carro
    """
    
    def __init__(self):
        self.imagem_retorne = None
        self.fonte_contra_mao = None
        # Carregar imagens do velocímetro e nitro
        self.velocimetro_sem_cor = None
        self.velocimetro_colorido = None
        self.nitro_vazio = None
        self.nitro = None
        self._carregar_imagens_hud()
    
    def _carregar_imagens_hud(self):
        """Carrega as imagens PNG do velocímetro e nitro"""
        try:
            caminho_velocimetro_sem_cor = os.path.join(DIR_ICONS, "velocimetro_sem_cor.png")
            caminho_velocimetro_colorido = os.path.join(DIR_ICONS, "velocimetro_colorido.png")
            caminho_nitro_vazio = os.path.join(DIR_ICONS, "nitro_vazio.png")
            caminho_nitro = os.path.join(DIR_ICONS, "nitro.png")
            
            if os.path.exists(caminho_velocimetro_sem_cor):
                self.velocimetro_sem_cor = pygame.image.load(caminho_velocimetro_sem_cor).convert_alpha()
                print(f"HUD: Carregado velocimetro_sem_cor: {caminho_velocimetro_sem_cor}")
            else:
                print(f"HUD: Arquivo não encontrado: {caminho_velocimetro_sem_cor}")
                
            if os.path.exists(caminho_velocimetro_colorido):
                self.velocimetro_colorido = pygame.image.load(caminho_velocimetro_colorido).convert_alpha()
                print(f"HUD: Carregado velocimetro_colorido: {caminho_velocimetro_colorido}")
            else:
                print(f"HUD: Arquivo não encontrado: {caminho_velocimetro_colorido}")
                
            if os.path.exists(caminho_nitro_vazio):
                self.nitro_vazio = pygame.image.load(caminho_nitro_vazio).convert_alpha()
                print(f"HUD: Carregado nitro_vazio: {caminho_nitro_vazio}")
            else:
                print(f"HUD: Arquivo não encontrado: {caminho_nitro_vazio}")
                
            if os.path.exists(caminho_nitro):
                self.nitro = pygame.image.load(caminho_nitro).convert_alpha()
                print(f"HUD: Carregado nitro: {caminho_nitro}")
            else:
                print(f"HUD: Arquivo não encontrado: {caminho_nitro}")
        except Exception as e:
            print(f"Erro ao carregar imagens do HUD: {e}")
    
    def desenhar_hud_completo(self, superficie, carro, dt=0.016, offset_x=0):
        """
        Desenha o HUD completo (velocímetro e nitro) no canto inferior direito
        velocimetro_sem_cor é sobreposto por velocimetro_colorido conforme acelera (máx 180 km/h)
        nitro_vazio é sobreposto por nitro conforme a carga (esvazia quando usa)
        offset_x: offset horizontal para posicionar o HUD (útil para split-screen)
        """
        if not carro:
            return
        
        # Criar fonte se não existir
        if not hasattr(self, 'fonte_velocimetro'):
            self.fonte_velocimetro = pygame.font.SysFont("consolas", 28, bold=True)
            self.fonte_velocimetro_pequena = pygame.font.SysFont("consolas", 16)
        
        # Obter velocidade do carro
        velocidade_kmh = getattr(carro, 'velocidade_kmh', 0.0)
        
        # Simular oscilação do velocímetro quando próximo do limite máximo
        # Adicionar pequena variação visual para simular o limite que o carro aguenta
        if not hasattr(self, '_tempo_oscilacao'):
            self._tempo_oscilacao = 0.0
        
        self._tempo_oscilacao += dt
        
        # Quando a velocidade está próxima ou acima de 180 km/h, adicionar oscilação
        if velocidade_kmh >= 170:  # Começar a oscilar quando próximo do máximo
            # Calcular quanto acima de 170 estamos (0 a ~30 km/h)
            excesso = min(velocidade_kmh - 170, 30.0)
            # Oscilação senoidal: varia entre -5 e +8 km/h quando no máximo
            amplitude = 3.0 + (excesso / 30.0) * 5.0  # Aumenta a amplitude conforme se aproxima do máximo
            frequencia = 2.5  # Velocidade da oscilação
            oscilacao = math.sin(self._tempo_oscilacao * frequencia) * amplitude
            # Adicionar oscilação ao valor mostrado (mas não deixar abaixo de 170)
            velocidade_kmh_mostrada = max(170, velocidade_kmh + oscilacao)
        else:
            velocidade_kmh_mostrada = velocidade_kmh
        
        # Posição do velocímetro (canto inferior direito)
        # Ajustar posição baseado no tamanho das imagens redimensionadas
        escala_velocimetro = 0.22  # Velocímetro um pouco menor (25%)
        escala_nitro = 0.05  # Nitro MUITO menor (12%)
        
        # Calcular largura efetiva da superfície (para split-screen)
        largura_efetiva = superficie.get_width()
        
        if self.velocimetro_sem_cor:
            # Calcular tamanho redimensionado
            altura_velocimetro = int(self.velocimetro_sem_cor.get_height() * escala_velocimetro)
            largura_velocimetro = int(self.velocimetro_sem_cor.get_width() * escala_velocimetro)
            pos_y = ALTURA - altura_velocimetro - 10  # 10px de margem do fundo
            # Posicionar no canto direito da superfície atual (considerando offset_x)
            pos_x_velocimetro = offset_x + largura_efetiva - largura_velocimetro - 10  # 10px de margem da direita
        else:
            pos_y = ALTURA - 70
            pos_x_velocimetro = offset_x + largura_efetiva - 200
            
        if self.nitro_vazio:
            # Redimensionar nitro também (20% do original - menor)
            largura_nitro_redimensionado = int(self.nitro_vazio.get_width() * escala_nitro)
            altura_nitro_redimensionado = int(self.nitro_vazio.get_height() * escala_nitro)
            # Posicionar nitro à esquerda do velocímetro
            pos_x_nitro = pos_x_velocimetro - largura_nitro_redimensionado - 10  # 10px de espaçamento à esquerda
            pos_y_nitro = pos_y  # Mesma altura Y
        else:
            pos_x_nitro = offset_x + largura_efetiva - 100
            pos_y_nitro = pos_y
        
        # Desenhar velocímetro
        if self.velocimetro_sem_cor and self.velocimetro_colorido:
            # Calcular porcentagem de velocidade (0-180 km/h)
            # Usar velocidade_kmh_mostrada que inclui a oscilação
            velocidade_max = 180.0
            porcentagem_velocidade = min(velocidade_kmh_mostrada / velocidade_max, 1.0)
            
            # Redimensionar imagens para um tamanho menor
            largura_original = self.velocimetro_sem_cor.get_width()
            altura_original = self.velocimetro_sem_cor.get_height()
            # Redimensionar para 25% do tamanho original
            escala = escala_velocimetro
            largura = int(largura_original * escala)
            altura = int(altura_original * escala)
            
            # Redimensionar imagens (cache para não redimensionar a cada frame)
            if not hasattr(self, '_velocimetro_sem_cor_redimensionado'):
                self._velocimetro_sem_cor_redimensionado = pygame.transform.scale(self.velocimetro_sem_cor, (largura, altura))
            if not hasattr(self, '_velocimetro_colorido_redimensionado'):
                self._velocimetro_colorido_redimensionado = pygame.transform.scale(self.velocimetro_colorido, (largura, altura))
            
            # Desenhar fundo (sem cor) - sempre completo
            superficie.blit(self._velocimetro_sem_cor_redimensionado, (pos_x_velocimetro, pos_y))
            
            # Desenhar parte colorida sobreposta (da esquerda para direita)
            largura_preenchida = int(largura * porcentagem_velocidade)
            if largura_preenchida > 0:
                superficie.blit(
                    self._velocimetro_colorido_redimensionado,
                    (pos_x_velocimetro, pos_y),
                    (0, 0, largura_preenchida, altura)
                )
            
            # Texto de velocidade (canto superior esquerdo, acima do começo do velocímetro)
            # Usar velocidade_kmh_mostrada que inclui a oscilação
            texto_velocidade = f"{int(velocidade_kmh_mostrada)}"
            texto_surf = self.fonte_velocimetro.render(texto_velocidade, True, (255, 255, 255))
            # Posicionar no canto superior esquerdo do velocímetro
            texto_rect = texto_surf.get_rect(topleft=(pos_x_velocimetro, pos_y - 30))
            superficie.blit(texto_surf, texto_rect)
            
            # Texto "km/h" (ao lado do número)
            texto_kmh = self.fonte_velocimetro_pequena.render("km/h", True, (200, 200, 200))
            texto_kmh_rect = texto_kmh.get_rect(topleft=(pos_x_velocimetro + texto_surf.get_width() + 5, pos_y - 28))
            superficie.blit(texto_kmh, texto_kmh_rect)
        else:
            # Debug: desenhar retângulo se imagens não carregaram
            if not hasattr(self, '_debug_mostrado'):
                print(f"DEBUG HUD: velocimetro_sem_cor={self.velocimetro_sem_cor is not None}, velocimetro_colorido={self.velocimetro_colorido is not None}")
                self._debug_mostrado = True
            # Fallback: desenhar retângulo simples
            pygame.draw.rect(superficie, (100, 100, 100), (pos_x_velocimetro, pos_y, 100, 50))
            # Usar velocidade_kmh_mostrada que inclui a oscilação
            texto_velocidade = f"{int(velocidade_kmh_mostrada)}"
            texto_surf = self.fonte_velocimetro.render(texto_velocidade, True, (255, 255, 255))
            superficie.blit(texto_surf, (pos_x_velocimetro + 10, pos_y + 10))
        
        # Desenhar nitro
        if hasattr(carro, 'turbo_carga') and self.nitro_vazio and self.nitro:
            # turbo_carga está em 0.0 a 100.0, converter para 0.0 a 1.0
            porcentagem_nitro = carro.turbo_carga / 100.0  # Converter de 0-100 para 0-1
            
            # Redimensionar nitro (12% do original - MUITO menor)
            largura_nitro_original = self.nitro_vazio.get_width()
            altura_nitro_original = self.nitro_vazio.get_height()
            # Usar escala_nitro já definida acima (0.12)
            largura_nitro = int(largura_nitro_original * escala_nitro)
            altura_nitro = int(altura_nitro_original * escala_nitro)
            
            # Cache das imagens redimensionadas
            if not hasattr(self, '_nitro_vazio_redimensionado'):
                self._nitro_vazio_redimensionado = pygame.transform.scale(self.nitro_vazio, (largura_nitro, altura_nitro))
            if not hasattr(self, '_nitro_redimensionado'):
                self._nitro_redimensionado = pygame.transform.scale(self.nitro, (largura_nitro, altura_nitro))
            
            # Desenhar fundo vazio (cinza) - sempre completo
            superficie.blit(self._nitro_vazio_redimensionado, (pos_x_nitro, pos_y_nitro))
            
            # Desenhar parte colorida de baixo para cima conforme recarrega
            # Quando porcentagem_nitro = 1.0, desenha tudo (totalmente colorido)
            # Quando porcentagem_nitro = 0.0, não desenha nada (totalmente cinza)
            altura_colorida = int(altura_nitro * porcentagem_nitro)
            if altura_colorida > 0:
                origem_y_colorida = altura_nitro - altura_colorida  # Começar de baixo
                superficie.blit(
                    self._nitro_redimensionado,
                    (pos_x_nitro, pos_y_nitro + origem_y_colorida),
                    (0, origem_y_colorida, largura_nitro, altura_colorida)
                )
    
    def desenhar_minimapa(self, superficie, carro, checkpoints, camera, posicao=(50, 550), imagem_minimapa=None, limites_pista=None, todos_carros=None):
        """
        Desenha um minimapa simples com imagem do GRIP se disponível
        limites_pista: (min_x, min_y, max_x, max_y) - limites da pista completa
        todos_carros: lista de todos os carros para mostrar no minimapa
        """
        if not carro:
            return
        
        if todos_carros is None:
            todos_carros = [carro]
        
        # Tamanho do minimapa (ajustado)
        minimapa_largura = 200
        minimapa_altura = 200
        minimapa_raio = 100  # Para minimapa circular
        
        # Se temos imagem do minimapa, usar ela
        if imagem_minimapa:
            # Redimensionar imagem do minimapa
            minimapa_redimensionado = pygame.transform.scale(imagem_minimapa, (minimapa_largura, minimapa_altura))
            superficie.blit(minimapa_redimensionado, posicao)
            
            # Remover borda do minimapa (apenas o circuito, sem contorno)
        else:
            # Desenhar fundo circular do minimapa (fallback)
            pygame.draw.circle(superficie, (0, 0, 0), 
                             (posicao[0] + minimapa_raio, posicao[1] + minimapa_raio), minimapa_raio)
            pygame.draw.circle(superficie, (100, 100, 100), 
                             (posicao[0] + minimapa_raio, posicao[1] + minimapa_raio), minimapa_raio, 2)
        
        # Calcular escala do minimapa baseado na pista completa ou checkpoints
        if limites_pista:
            # Usar limites da pista completa (mais preciso)
            # Usar os limites exatos sem adicionar margem - isso garante mapeamento preciso
            min_x, min_y, max_x, max_y = limites_pista
            # Não adicionar margem aqui - usar limites exatos para mapeamento preciso
        elif checkpoints:
            # Usar limites dos checkpoints como fallback
            min_x = min(cp[0] for cp in checkpoints)
            max_x = max(cp[0] for cp in checkpoints)
            min_y = min(cp[1] for cp in checkpoints)
            max_y = max(cp[1] for cp in checkpoints)
            
            # Adicionar margem
            margem = 500  # Margem maior para cobrir toda a pista
            min_x -= margem
            max_x += margem
            min_y -= margem
            max_y += margem
        else:
            # Sem limites conhecidos, usar posição do carro como centro
            min_x = carro.x - 1000
            max_x = carro.x + 1000
            min_y = carro.y - 1000
            max_y = carro.y + 1000
        
        # Calcular escala
        if imagem_minimapa:
            # Para minimapa retangular com imagem
            escala_x = minimapa_largura / (max_x - min_x)
            escala_y = minimapa_altura / (max_y - min_y)
            escala = min(escala_x, escala_y)
            centro_x = posicao[0] + minimapa_largura / 2
            centro_y = posicao[1] + minimapa_altura / 2
        else:
            # Para minimapa circular
            escala_x = (minimapa_raio * 2) / (max_x - min_x)
            escala_y = (minimapa_raio * 2) / (max_y - min_y)
            escala = min(escala_x, escala_y)
            centro_x = posicao[0] + minimapa_raio
            centro_y = posicao[1] + minimapa_raio
        
        # Desenhar checkpoints (sempre, mesmo com imagem do minimapa)
        if checkpoints:
            checkpoint_atual = getattr(carro, 'checkpoint_atual', 0)
            for i, cp in enumerate(checkpoints):
                # Suportar formato (x, y) ou (x, y, angulo)
                if len(cp) >= 3:
                    cx, cy = cp[0], cp[1]
                else:
                    cx, cy = cp[0], cp[1]
                
                # Normalizar posição do checkpoint
                if (max_x - min_x) > 0 and (max_y - min_y) > 0:
                    cp_normalizado_x = (cx - min_x) / (max_x - min_x)
                    cp_normalizado_y = (cy - min_y) / (max_y - min_y)
                    
                    if imagem_minimapa:
                        # Para minimapa retangular
                        cp_x = posicao[0] + cp_normalizado_x * minimapa_largura
                        cp_y = posicao[1] + cp_normalizado_y * minimapa_altura
                    else:
                        # Para minimapa circular
                        cp_x = centro_x + (cp_normalizado_x - 0.5) * (minimapa_raio * 2)
                        cp_y = centro_y + (cp_normalizado_y - 0.5) * (minimapa_raio * 2)
                    
                    # Verificar se está dentro dos limites do minimapa
                    if imagem_minimapa:
                        dentro = (posicao[0] <= cp_x <= posicao[0] + minimapa_largura and 
                                 posicao[1] <= cp_y <= posicao[1] + minimapa_altura)
                    else:
                        distancia_centro = ((cp_x - centro_x) ** 2 + (cp_y - centro_y) ** 2) ** 0.5
                        dentro = distancia_centro <= minimapa_raio - 5
                    
                    if dentro:
                        # Cor do checkpoint: verde se já passou, vermelho se é o próximo, cinza se ainda não passou
                        if i < checkpoint_atual:
                            cor = (0, 255, 0)  # Verde - já passou
                        elif i == checkpoint_atual:
                            cor = (255, 0, 0)  # Vermelho - próximo
                        else:
                            cor = (128, 128, 128)  # Cinza - ainda não passou
                        
                        pygame.draw.circle(superficie, cor, (int(cp_x), int(cp_y)), 4)
                        pygame.draw.circle(superficie, (255, 255, 255), (int(cp_x), int(cp_y)), 4, 1)
        
        # Normalizar posição do carro para a área da pista (0.0 a 1.0)
        if (max_x - min_x) > 0 and (max_y - min_y) > 0:
            # Clampar a posição do carro dentro dos limites antes de normalizar
            carro_x_clamped = max(min_x, min(max_x, carro.x))
            carro_y_clamped = max(min_y, min(max_y, carro.y))
            
            carro_normalizado_x = (carro_x_clamped - min_x) / (max_x - min_x)
            carro_normalizado_y = (carro_y_clamped - min_y) / (max_y - min_y)
            
            # Garantir que a normalização está entre 0 e 1
            carro_normalizado_x = max(0.0, min(1.0, carro_normalizado_x))
            carro_normalizado_y = max(0.0, min(1.0, carro_normalizado_y))
            
            # Mapear para o minimapa
            if imagem_minimapa:
                # Para minimapa retangular - mapear diretamente
                carro_x = posicao[0] + carro_normalizado_x * minimapa_largura
                carro_y = posicao[1] + carro_normalizado_y * minimapa_altura
            else:
                # Para minimapa circular
                carro_x = centro_x + (carro_normalizado_x - 0.5) * (minimapa_raio * 2)
                carro_y = centro_y + (carro_normalizado_y - 0.5) * (minimapa_raio * 2)
        else:
            # Fallback: usar cálculo antigo
            centro_pista_x = (min_x + max_x) / 2
            centro_pista_y = (min_y + max_y) / 2
            carro_rel_x = carro.x - centro_pista_x
            carro_rel_y = carro.y - centro_pista_y
            carro_x = centro_x + carro_rel_x * escala
            carro_y = centro_y + carro_rel_y * escala
        
        # Desenhar todos os carros no minimapa
        for idx, outro_carro in enumerate(todos_carros):
            if outro_carro is None:
                continue
            
            # Normalizar posição do carro para a área da pista (0.0 a 1.0)
            if (max_x - min_x) > 0 and (max_y - min_y) > 0:
                # Clampar a posição do carro dentro dos limites antes de normalizar
                outro_carro_x_clamped = max(min_x, min(max_x, outro_carro.x))
                outro_carro_y_clamped = max(min_y, min(max_y, outro_carro.y))
                
                outro_carro_normalizado_x = (outro_carro_x_clamped - min_x) / (max_x - min_x)
                outro_carro_normalizado_y = (outro_carro_y_clamped - min_y) / (max_y - min_y)
                
                # Garantir que a normalização está entre 0 e 1
                outro_carro_normalizado_x = max(0.0, min(1.0, outro_carro_normalizado_x))
                outro_carro_normalizado_y = max(0.0, min(1.0, outro_carro_normalizado_y))
                
                # Mapear para o minimapa
                if imagem_minimapa:
                    # Para minimapa retangular - mapear diretamente
                    outro_carro_x = posicao[0] + outro_carro_normalizado_x * minimapa_largura
                    outro_carro_y = posicao[1] + outro_carro_normalizado_y * minimapa_altura
                else:
                    # Para minimapa circular
                    outro_carro_x = centro_x + (outro_carro_normalizado_x - 0.5) * (minimapa_raio * 2)
                    outro_carro_y = centro_y + (outro_carro_normalizado_y - 0.5) * (minimapa_raio * 2)
            else:
                # Fallback
                centro_pista_x = (min_x + max_x) / 2
                centro_pista_y = (min_y + max_y) / 2
                outro_carro_rel_x = outro_carro.x - centro_pista_x
                outro_carro_rel_y = outro_carro.y - centro_pista_y
                outro_carro_x = centro_x + outro_carro_rel_x * escala
                outro_carro_y = centro_y + outro_carro_rel_y * escala
            
            # Verificar se o carro está dentro dos limites do minimapa
            if imagem_minimapa:
                # Para minimapa retangular - sempre mostrar, mas com margem maior
                # Usar margem maior para não cortar quando está perto das bordas
                margem_borda = 8
                outro_carro_x_visivel = max(posicao[0] + margem_borda, 
                                           min(posicao[0] + minimapa_largura - margem_borda, outro_carro_x))
                outro_carro_y_visivel = max(posicao[1] + margem_borda, 
                                           min(posicao[1] + minimapa_altura - margem_borda, outro_carro_y))
            else:
                # Para minimapa circular
                distancia_outro_carro = ((outro_carro_x - centro_x) ** 2 + (outro_carro_y - centro_y) ** 2) ** 0.5
                if distancia_outro_carro > minimapa_raio - 8:
                    # Se estiver fora, mostrar na borda do círculo
                    angulo = math.atan2(outro_carro_y - centro_y, outro_carro_x - centro_x)
                    outro_carro_x_visivel = centro_x + (minimapa_raio - 8) * math.cos(angulo)
                    outro_carro_y_visivel = centro_y + (minimapa_raio - 8) * math.sin(angulo)
                else:
                    outro_carro_x_visivel = outro_carro_x
                    outro_carro_y_visivel = outro_carro_y
            
            # Escolher cor baseado se é o carro principal ou outro
            if outro_carro == carro:
                # Carro principal - ciano
                cor_carro = (0, 255, 255)
                tamanho = 6
            else:
                # Outros carros - amarelo
                cor_carro = (255, 255, 0)
                tamanho = 5
            
            pygame.draw.circle(superficie, cor_carro, (int(outro_carro_x_visivel), int(outro_carro_y_visivel)), tamanho)
            pygame.draw.circle(superficie, (255, 255, 255), (int(outro_carro_x_visivel), int(outro_carro_y_visivel)), tamanho, 1)
            
            # Desenhar direção do carro
            angulo_rad = math.radians(outro_carro.angulo)
            dir_x = outro_carro_x_visivel + 12 * math.cos(angulo_rad)
            dir_y = outro_carro_y_visivel + 12 * math.sin(angulo_rad)
            pygame.draw.line(superficie, cor_carro, (int(outro_carro_x_visivel), int(outro_carro_y_visivel)), 
                           (int(dir_x), int(dir_y)), 2)
    
    def desenhar_posicao_voltas(self, superficie, corrida, carro, todos_carros, posicao=(10, 10), alinhar_direita=False):
        """
        Desenha a posição (1st, 2nd, etc) e voltas (1/2, 2/2, etc) no canto da tela
        estilo Mario Kart com blur/fundo por trás
        """
        if not carro or not corrida:
            return
        
        # Calcular posição atual do carro em tempo real
        def calcular_posicao_atual(carro_alvo, todos_carros):
            """Calcula a posição atual baseada no progresso (checkpoints + voltas)"""
            if not corrida.checkpoints:
                return None
            
            # Calcular progresso de cada carro
            progressos = []
            for c in todos_carros:
                if c not in corrida.proximo_checkpoint:
                    continue
                
                checkpoint_atual = corrida.proximo_checkpoint.get(c, 0)
                voltas_completas = corrida.voltas.get(c, 0)
                total_checkpoints = len(corrida.checkpoints)
                
                # Progresso total = voltas completas * total_checkpoints + checkpoint_atual
                progresso_total = voltas_completas * total_checkpoints + checkpoint_atual
                progressos.append((c, progresso_total))
            
            # Ordenar por progresso (maior = na frente)
            progressos.sort(key=lambda x: x[1], reverse=True)
            
            # Encontrar posição do carro alvo
            for pos, (c, _) in enumerate(progressos, start=1):
                if c == carro_alvo:
                    return pos
            
            return None
        
        posicao_atual = calcular_posicao_atual(carro, todos_carros)
        voltas_atual = corrida.voltas.get(carro, 0)
        voltas_objetivo = corrida.voltas_objetivo
        
        # Converter posição para texto (1st, 2nd, 3rd, 4th, etc)
        if posicao_atual:
            if posicao_atual == 1:
                texto_posicao = "1st"
            elif posicao_atual == 2:
                texto_posicao = "2nd"
            elif posicao_atual == 3:
                texto_posicao = "3rd"
            else:
                texto_posicao = f"{posicao_atual}th"
        else:
            texto_posicao = "?"
        
        # Texto de voltas
        texto_voltas = f"{voltas_atual}/{voltas_objetivo}"
        
        # Fontes menores ainda
        fonte_posicao = pygame.font.SysFont("Arial", 28, bold=True)
        fonte_voltas = pygame.font.SysFont("Arial", 20, bold=True)
        
        # Renderizar textos
        texto_pos_surf = fonte_posicao.render(texto_posicao, True, (255, 255, 255))
        texto_voltas_surf = fonte_voltas.render(texto_voltas, True, (255, 255, 255))
        
        # Calcular tamanho do fundo (com padding menor)
        padding = 8
        largura_fundo = max(texto_pos_surf.get_width(), texto_voltas_surf.get_width()) + padding * 2
        altura_fundo = texto_pos_surf.get_height() + texto_voltas_surf.get_height() + padding * 2 + 3
        
        # Ajustar posição se alinhar à direita
        if alinhar_direita:
            x_fundo = posicao[0] - largura_fundo
        else:
            x_fundo = posicao[0]
        
        # Criar superfície com blur/fundo semi-transparente
        fundo_surface = pygame.Surface((largura_fundo, altura_fundo), pygame.SRCALPHA)
        fundo_surface.fill((0, 0, 0, 180))  # Preto semi-transparente com blur
        
        # Desenhar fundo na superfície
        superficie.blit(fundo_surface, (x_fundo, posicao[1]))
        
        # Desenhar textos
        x_texto = x_fundo + padding
        y_posicao = posicao[1] + padding
        y_voltas = y_posicao + texto_pos_surf.get_height() + 5
        
        superficie.blit(texto_pos_surf, (x_texto, y_posicao))
        superficie.blit(texto_voltas_surf, (x_texto, y_voltas))
    
    def desenhar_tempos(self, superficie, corrida, carro, posicao=(20, 20)):
        """
        Desenha os tempos de checkpoint e tempo total (estilo GRIP)
        """
        if not carro or not corrida:
            return
        
        y_offset = posicao[1]
        linha_altura = 25
        
        # Tempo total
        if corrida.inicIAda:
            tempo_total = corrida.tempo_global
            minutos = int(tempo_total // 60)
            segundos = int(tempo_total % 60)
            centesimos = int((tempo_total % 1) * 100)
            texto_tempo = f"Tempo: {minutos:02d}:{segundos:02d}.{centesimos:02d}"
        else:
            texto_tempo = "Tempo: 00:00.00"
        
        # Tempo do checkpoint
        checkpoint_atual = getattr(carro, 'checkpoint_atual', 0)
        if checkpoint_atual in corrida.tempo_checkpoint.get(carro, {}):
            tempo_cp = corrida.tempo_checkpoint[carro][checkpoint_atual]
            segundos_cp = int(tempo_cp % 60)
            centesimos_cp = int((tempo_cp % 1) * 100)
            texto_checkpoint = f"Checkpoint: {segundos_cp}.{centesimos_cp:02d}"
        else:
            texto_checkpoint = "Checkpoint: 00.00"
        
        # Voltas
        voltas = corrida.voltas.get(carro, 0)
        voltas_objetivo = corrida.voltas_objetivo
        texto_voltas = f"Voltas: {voltas}/{voltas_objetivo}"
        
        # Criar fonte se não existir
        if not hasattr(self, 'fonte_tempos'):
            self.fonte_tempos = pygame.font.SysFont("consolas", 24)
        
        # Desenhar textos
        cor_tempo = (255, 255, 255)
        cor_voltas = (255, 255, 0)
        
        texto_surf = self.fonte_tempos.render(texto_tempo, True, cor_tempo)
        superficie.blit(texto_surf, (posicao[0], y_offset))
        y_offset += linha_altura
        
        texto_surf = self.fonte_tempos.render(texto_checkpoint, True, cor_tempo)
        superficie.blit(texto_surf, (posicao[0], y_offset))
        y_offset += linha_altura
        
        texto_surf = self.fonte_tempos.render(texto_voltas, True, cor_voltas)
        superficie.blit(texto_surf, (posicao[0], y_offset))
    
    def desenhar_aviso_contra_mao(self, superficie, carro, dt=0.016):
        """
        Desenha aviso de contra mão quando o jogador passa por checkpoint na direção errada
        """
        if not hasattr(carro, 'contra_mao') or not carro.contra_mao:
            return
        
        # Atualizar timer de contra mão
        if not hasattr(carro, 'contra_mao_tempo'):
            carro.contra_mao_tempo = 0.0
        carro.contra_mao_tempo += dt
        
        # Mostrar aviso por 3 segundos
        if carro.contra_mao_tempo > 3.0:
            carro.contra_mao = False
            return
        
        # Carregar imagem de retorne se ainda não foi carregada
        if self.imagem_retorne is None:
            caminho_retorne = os.path.join(DIR_ICONS, "retorne.png")
            if os.path.exists(caminho_retorne):
                try:
                    self.imagem_retorne = pygame.image.load(caminho_retorne).convert_alpha()
                except:
                    self.imagem_retorne = None
            else:
                self.imagem_retorne = None
        
        # Posição central da tela
        centro_x = superficie.get_width() // 2
        centro_y = superficie.get_height() // 2
        
        # Desenhar seta de retorne
        if self.imagem_retorne:
            # Redimensionar seta
            seta_tamanho = 100
            seta_redimensionada = pygame.transform.scale(self.imagem_retorne, (seta_tamanho, seta_tamanho))
            seta_rect = seta_redimensionada.get_rect(center=(centro_x, centro_y - 80))
            superficie.blit(seta_redimensionada, seta_rect)
        else:
            # Fallback: desenhar seta simples
            pontos_seta = [
                (centro_x, centro_y - 120),
                (centro_x - 40, centro_y - 80),
                (centro_x, centro_y - 40),
                (centro_x + 40, centro_y - 80)
            ]
            pygame.draw.polygon(superficie, (255, 0, 0), pontos_seta)
        
        # Desenhar texto "CONTRA MÃO"
        if self.fonte_contra_mao is None:
            self.fonte_contra_mao = pygame.font.SysFont("Arial", 56, bold=True)
        
        texto = self.fonte_contra_mao.render("CONTRA MÃO", True, (255, 0, 0))
        texto_sombra = self.fonte_contra_mao.render("CONTRA MÃO", True, (0, 0, 0))
        texto_rect = texto.get_rect(center=(centro_x, centro_y + 20))
        superficie.blit(texto_sombra, (texto_rect.x + 3, texto_rect.y + 3))
        superficie.blit(texto, texto_rect)
