import pygame

class Camera:
    def __init__(self, largura_tela, altura_tela, largura_mundo, altura_mundo, alvo=None, zoom=1.6):
        self.largura_tela = largura_tela
        self.altura_tela = altura_tela
        self.largura_mundo = largura_mundo
        self.altura_mundo = altura_mundo
        self.alvo = alvo
        self.zoom = float(zoom)

        self.cx = largura_mundo / 2
        self.cy = altura_mundo / 2

        self.follow_rigidez = 18.0
        
        self._visao_cache = None
        self._visao_cache_key = None

    def set_alvo(self, alvo):
        self.alvo = alvo

    def atualizar(self, dt):
        if not self.alvo:
            return
        
        offset_x = getattr(self, 'offset_x', 0)
        offset_y = getattr(self, 'offset_y', 0)
        tx, ty = float(self.alvo.x) - offset_x, float(self.alvo.y) - offset_y
        dt_smooth = max(dt, 0.001)
        
        dist_x = abs(tx - self.cx)
        dist_y = abs(ty - self.cy)
        distancia = (dist_x**2 + dist_y**2)**0.5
        
        if distancia > 100:
            rigidez_ajustada = self.follow_rigidez * 1.5
        elif distancia > 50:
            rigidez_ajustada = self.follow_rigidez * 1.2
        else:
            rigidez_ajustada = self.follow_rigidez
        
        lerp = 1.0 - pow(0.001, rigidez_ajustada * dt_smooth)
        
        dx_raw = (tx - self.cx) * lerp
        dy_raw = (ty - self.cy) * lerp
        
        max_move_base = 400.0 * dt_smooth
        if distancia > 100:
            max_move = max_move_base * 1.5
        else:
            max_move = max_move_base
        
        if distancia > 80:
            dx = dx_raw
            dy = dy_raw
        else:
            if not hasattr(self, '_dx_smooth'):
                self._dx_smooth = 0.0
                self._dy_smooth = 0.0
            
            alpha = 0.5
            self._dx_smooth = alpha * dx_raw + (1.0 - alpha) * self._dx_smooth
            self._dy_smooth = alpha * dy_raw + (1.0 - alpha) * self._dy_smooth
            
            dx = self._dx_smooth
            dy = self._dy_smooth
        
        if abs(dx) > max_move:
            dx = max_move if dx > 0 else -max_move
        if abs(dy) > max_move:
            dy = max_move if dy > 0 else -max_move
        
        self.cx += dx
        self.cy += dy
        self._clamp_centro()
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
        cache_key = (int(self.cx), int(self.cy), int(self.zoom * 100))
        if self._visao_cache_key == cache_key and self._visao_cache is not None:
            return self._visao_cache
        
        vw = self.largura_tela / self.zoom
        vh = self.altura_tela  / self.zoom
        left = int(self.cx - vw / 2)
        top  = int(self.cy - vh / 2)
        left = max(0, min(self.largura_mundo - int(vw), left))
        top  = max(0, min(self.altura_mundo  - int(vh), top))
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
        return pygame.Rect(r.left + offset_x, r.top + offset_y, r.width, r.height)

    def mundo_para_tela(self, x, y):
        """Converte coordenadas do mundo para tela (aplica offset e zoom)."""
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
        
        offset_x = getattr(self, 'offset_x', 0)
        offset_y = getattr(self, 'offset_y', 0)
        x = x_camera + offset_x
        y = y_camera + offset_y
        return x, y

    def desenhar_fundo(self, superficie_tela, superficie_mundo):
        """Recorta a visão do mundo e escala para preencher a tela."""
        r_original = self.ret_visao_original()
        r_camera = self.ret_visao()
        
        mundo_w, mundo_h = superficie_mundo.get_size()
        
        escala_x = self.largura_tela / r_camera.width if r_camera.width > 0 else 1.0
        escala_y = self.altura_tela / r_camera.height if r_camera.height > 0 else 1.0
        
        superficie_tela.fill((0, 0, 0))
        
        clip_left = max(0, min(mundo_w, r_original.left))
        clip_top = max(0, min(mundo_h, r_original.top))
        clip_right = max(0, min(mundo_w, r_original.right))
        clip_bottom = max(0, min(mundo_h, r_original.bottom))
        
        clip_width = clip_right - clip_left
        clip_height = clip_bottom - clip_top
        
        if clip_width > 0 and clip_height > 0:
            try:
                recorte_original = superficie_mundo.subsurface(
                    (int(clip_left), int(clip_top), int(clip_width), int(clip_height))
                )
                
                recorte_escalado = pygame.transform.scale(
                    recorte_original,
                    (int(clip_width * escala_x), int(clip_height * escala_y))
                )
                
                offset_x_tela = 0
                offset_y_tela = 0
                
                if r_original.left < 0:
                    pixels_fora_x = -r_original.left
                    offset_x_tela = int(pixels_fora_x * escala_x)
                
                if r_original.top < 0:
                    pixels_fora_y = -r_original.top
                    offset_y_tela = int(pixels_fora_y * escala_y)
                
                superficie_tela.blit(recorte_escalado, (offset_x_tela, offset_y_tela))
                
            except (ValueError, pygame.error) as e:
                pass
    
    def esta_visivel(self, x_mundo, y_mundo, margem=0):
        """Verificar se um objeto está visível na tela (com margem)."""
        x_tela, y_tela = self.mundo_para_tela(x_mundo, y_mundo)
        return (-margem <= x_tela <= self.largura_tela + margem and 
                -margem <= y_tela <= self.altura_tela + margem)