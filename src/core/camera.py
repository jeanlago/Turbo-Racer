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
        tx, ty = float(self.alvo.x), float(self.alvo.y)
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

    def mundo_para_tela(self, x, y):
        """Converte coordenadas do mundo para tela (aplica offset e zoom)."""
        r = self.ret_visao()
        sx = int((x - r.left) * self.zoom)
        sy = int((y - r.top ) * self.zoom)
        return sx, sy
    
    def tela_para_mundo(self, sx, sy):
        """Converte coordenadas da tela para mundo (remove offset e zoom)."""
        r = self.ret_visao()
        x = (sx / self.zoom) + r.left
        y = (sy / self.zoom) + r.top
        return x, y

    def desenhar_fundo(self, superficie_tela, superficie_mundo):
        """Recorta a visão do mundo e escala para preencher a tela."""
        r = self.ret_visao()
        # Otimização: usar subsurface diretamente em vez de copy()
        recorte = superficie_mundo.subsurface(r)
        # Usar scale em vez de smoothscale para melhor performance
        amplIAdo = pygame.transform.scale(recorte, (self.largura_tela, self.altura_tela))
        superficie_tela.blit(amplIAdo, (0, 0))
    
    def esta_visivel(self, x_mundo, y_mundo, margem=0):
        """Verificar se um objeto está visível na tela (com margem)."""
        x_tela, y_tela = self.mundo_para_tela(x_mundo, y_mundo)
        return (-margem <= x_tela <= self.largura_tela + margem and 
                -margem <= y_tela <= self.altura_tela + margem)