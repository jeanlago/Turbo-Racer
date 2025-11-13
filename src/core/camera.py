# src/core/camera.py
import pygame

class Camera:
    def __init__(self, largura_tela, altura_tela, largura_mundo, altura_mundo, alvo=None, zoom=1.6):
        self.largura_tela = largura_tela
        self.altura_tela = altura_tela
        self.largura_mundo = largura_mundo
        self.altura_mundo = altura_mundo
        self.alvo = alvo  # objeto com .x e .y
        self.zoom = float(zoom)

        # Posição do centro da câmera no MUNDO
        self.cx = largura_mundo / 2
        self.cy = altura_mundo / 2

        # Suavização (follow "macio") - equilíbrio entre suavidade e responsividade
        self.follow_rigidez = 18.0  # Valor intermediário: suave mas ainda responsivo
        
        # Cache de visão para evitar recálculos
        self._visao_cache = None
        self._visao_cache_key = None

    def set_alvo(self, alvo):
        self.alvo = alvo

    def atualizar(self, dt):
        if not self.alvo:
            return
        # segue o alvo com suavização exponencial simples
        # Melhorar suavização para evitar tremulação, mas manter responsividade
        # Ajustar coordenadas do alvo se houver offset
        offset_x = getattr(self, 'offset_x', 0)
        offset_y = getattr(self, 'offset_y', 0)
        tx, ty = float(self.alvo.x) - offset_x, float(self.alvo.y) - offset_y
        # Usar dt mínimo para evitar saltos quando dt é muito pequeno
        dt_smooth = max(dt, 0.001)
        
        # Calcular distância do carro para ajustar responsividade
        dist_x = abs(tx - self.cx)
        dist_y = abs(ty - self.cy)
        distancia = (dist_x**2 + dist_y**2)**0.5
        
        # Ajustar rigidez dinamicamente: mais responsivo quando o carro está longe
        # Isso permite que a câmera acompanhe melhor em alta velocidade
        if distancia > 100:  # Se o carro está longe, aumentar responsividade
            rigidez_ajustada = self.follow_rigidez * 1.5
        elif distancia > 50:
            rigidez_ajustada = self.follow_rigidez * 1.2
        else:
            rigidez_ajustada = self.follow_rigidez
        
        # Suavização exponencial
        lerp = 1.0 - pow(0.001, rigidez_ajustada * dt_smooth)  # 0..1
        
        # Calcular movimento base
        dx_raw = (tx - self.cx) * lerp
        dy_raw = (ty - self.cy) * lerp
        
        # Limitar a velocidade de movimento da câmera, mas permitir mais movimento quando necessário
        # Aumentar limite quando o carro está se movendo rápido
        max_move_base = 400.0 * dt_smooth
        if distancia > 100:
            max_move = max_move_base * 1.5  # Permitir movimento mais rápido quando longe
        else:
            max_move = max_move_base
        
        # Aplicar suavização adicional apenas quando o carro está próximo (para evitar tremulação)
        # Quando está longe, usar movimento direto para acompanhar melhor
        if distancia > 80:
            # Quando longe, usar movimento mais direto (menos suavização)
            dx = dx_raw
            dy = dy_raw
        else:
            # Quando próximo, aplicar suavização adicional para evitar tremulação
            if not hasattr(self, '_dx_smooth'):
                self._dx_smooth = 0.0
                self._dy_smooth = 0.0
            
            # Filtro de suavização (média móvel exponencial) - menos agressivo
            alpha = 0.5  # Aumentado de 0.3 para 0.5 (mais responsivo)
            self._dx_smooth = alpha * dx_raw + (1.0 - alpha) * self._dx_smooth
            self._dy_smooth = alpha * dy_raw + (1.0 - alpha) * self._dy_smooth
            
            dx = self._dx_smooth
            dy = self._dy_smooth
        
        # Clampar movimento para evitar saltos grandes
        if abs(dx) > max_move:
            dx = max_move if dx > 0 else -max_move
        if abs(dy) > max_move:
            dy = max_move if dy > 0 else -max_move
        
        self.cx += dx
        self.cy += dy
        self._clamp_centro()
        # Invalidar cache quando a câmera se move
        self._visao_cache = None
        self._visao_cache_key = None

    def _clamp_centro(self):
        vw = self.largura_tela / self.zoom
        vh = self.altura_tela  / self.zoom
        half_w = vw / 2
        half_h = vh / 2
        self.cx = max(half_w, min(self.largura_mundo - half_w, self.cx))
        self.cy = max(half_h, min(self.altura_mundo  - half_h, self.cy))

    def ret_visao(self):
        """Retângulo da visão no MUNDO (não escalado) - com cache."""
        # Cache baseado em cx, cy e zoom
        cache_key = (int(self.cx), int(self.cy), int(self.zoom * 100))
        if self._visao_cache_key == cache_key and self._visao_cache is not None:
            return self._visao_cache
        
        vw = self.largura_tela / self.zoom
        vh = self.altura_tela  / self.zoom
        left = int(self.cx - vw / 2)
        top  = int(self.cy - vh / 2)
        # garante que o rect está dentro do mundo
        left = max(0, min(self.largura_mundo - int(vw), left))
        top  = max(0, min(self.altura_mundo  - int(vh), top))
        # garante que as dimensões não excedem o mundo
        width = min(int(vw), self.largura_mundo - left)
        height = min(int(vh), self.altura_mundo - top)
        
        self._visao_cache = pygame.Rect(left, top, width, height)
        self._visao_cache_key = cache_key
        return self._visao_cache
    
    def ret_visao_original(self):
        """Retorna o retângulo de visão no sistema de coordenadas original (considerando offset)."""
        r = self.ret_visao()
        offset_x = getattr(self, 'offset_x', 0)
        offset_y = getattr(self, 'offset_y', 0)
        # Converter do sistema da câmera para o sistema original
        return pygame.Rect(r.left + offset_x, r.top + offset_y, r.width, r.height)

    def mundo_para_tela(self, x, y):
        """Converte coordenadas do mundo para tela (aplica offset e zoom)."""
        # Converter coordenadas do mundo original para o sistema da câmera
        offset_x = getattr(self, 'offset_x', 0)
        offset_y = getattr(self, 'offset_y', 0)
        x_camera = x - offset_x
        y_camera = y - offset_y
        
        r = self.ret_visao()
        sx = int((x_camera - r.left) * self.zoom)
        sy = int((y_camera - r.top ) * self.zoom)
        return sx, sy
    
    def tela_para_mundo(self, sx, sy):
        """Converte coordenadas da tela para mundo (remove offset e zoom)."""
        r = self.ret_visao()
        x_camera = (sx / self.zoom) + r.left
        y_camera = (sy / self.zoom) + r.top
        
        # Converter do sistema da câmera para o mundo original
        offset_x = getattr(self, 'offset_x', 0)
        offset_y = getattr(self, 'offset_y', 0)
        x = x_camera + offset_x
        y = y_camera + offset_y
        return x, y

    def desenhar_fundo(self, superficie_tela, superficie_mundo):
        """Recorta a visão do mundo e escala para preencher a tela."""
        # Obter retângulo de visão no sistema original
        r_original = self.ret_visao_original()
        r_camera = self.ret_visao()
        
        # Obter dimensões da superfície original
        mundo_w, mundo_h = superficie_mundo.get_size()
        
        # Calcular escala para preencher a tela
        escala_x = self.largura_tela / r_camera.width if r_camera.width > 0 else 1.0
        escala_y = self.altura_tela / r_camera.height if r_camera.height > 0 else 1.0
        
        # Preencher a tela com preto primeiro (para áreas fora da pista)
        superficie_tela.fill((0, 0, 0))
        
        # Calcular a parte do retângulo que está dentro dos limites da superfície
        clip_left = max(0, min(mundo_w, r_original.left))
        clip_top = max(0, min(mundo_h, r_original.top))
        clip_right = max(0, min(mundo_w, r_original.right))
        clip_bottom = max(0, min(mundo_h, r_original.bottom))
        
        clip_width = clip_right - clip_left
        clip_height = clip_bottom - clip_top
        
        if clip_width > 0 and clip_height > 0:
            # Recortar a parte visível da superfície
            try:
                recorte_original = superficie_mundo.subsurface(
                    (int(clip_left), int(clip_top), int(clip_width), int(clip_height))
                )
                
                # Escalar o recorte para o tamanho da tela
                recorte_escalado = pygame.transform.scale(
                    recorte_original,
                    (int(clip_width * escala_x), int(clip_height * escala_y))
                )
                
                # Calcular onde desenhar na tela
                # Se o retângulo original está parcialmente fora, ajustar a posição
                offset_x_tela = 0
                offset_y_tela = 0
                
                # Se parte do retângulo está à esquerda da pista (r_original.left < 0),
                # a parte visível deve ser desenhada mais à direita na tela
                if r_original.left < 0:
                    # Calcular quanto está fora (em pixels do mundo)
                    pixels_fora_x = -r_original.left
                    # Converter para pixels da tela
                    offset_x_tela = int(pixels_fora_x * escala_x)
                
                # Mesmo para Y
                if r_original.top < 0:
                    pixels_fora_y = -r_original.top
                    offset_y_tela = int(pixels_fora_y * escala_y)
                
                # Se parte do retângulo está à direita ou abaixo da pista,
                # não precisa ajustar (já está na posição correta)
                
                # Desenhar o recorte na posição correta
                superficie_tela.blit(recorte_escalado, (offset_x_tela, offset_y_tela))
                
            except (ValueError, pygame.error) as e:
                # Se houver erro ao recortar, apenas não desenhar (já está preto)
                pass
    
    def esta_visivel(self, x_mundo, y_mundo, margem=0):
        """Verificar se um objeto está visível na tela (com margem)."""
        x_tela, y_tela = self.mundo_para_tela(x_mundo, y_mundo)
        return (-margem <= x_tela <= self.largura_tela + margem and 
                -margem <= y_tela <= self.altura_tela + margem)