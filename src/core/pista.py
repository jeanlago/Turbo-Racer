import pygame, os, math, json
from config import (
    LARGURA, ALTURA, CAMINHO_MAPA, CAMINHO_GUIAS, CAMINHO_WAYPOINTS_JSON,
    CORES_PISTA, TOLERANCIA_COR,
    HSV_S_MAX, HSV_V_MAX,
    CHECKPOINT_COR, CHECKPOINT_TOL, CHECKPOINT_MIN_PIXELS,
    WAYPOINTS_MAP_1
)

# ---------- helpers de cor ----------
def _cor_proxima(c, alvo, tol):
    return abs(c[0]-alvo[0])<=tol and abs(c[1]-alvo[1])<=tol and abs(c[2]-alvo[2])<=tol

def _is_grey_like(rgb):
    """
    Considera 'pista' qualquer cor de baixa saturação (cinza/branco),
    desde que não seja muito escura (valor baixo).
    """
    c = pygame.Color(*rgb)
    h, s, v, _ = c.hsva  # s e v em [0..100]
    return (s <= HSV_S_MAX) and (v <= HSV_V_MAX)

def eh_pixel_da_pista(surface, x, y):
    """True se é pista; False se é limite/fora."""
    if x < 0 or y < 0 or x >= surface.get_width() or y >= surface.get_height():
        return False

    r, g, b, _ = surface.get_at((x, y))

    # 1) Verde = fora da pista (limite)
    if _cor_proxima((r, g, b), (0, 255, 0), 50):
        return False

    # 2) Laranja = pista (área válida para carros) - incluindo tons próximos
    if _cor_proxima((r, g, b), (255, 165, 0), 50):  # Laranja padrão
        return True
    if _cor_proxima((r, g, b), (254, 168, 59), 50):  # Laranja da sua imagem
        return True
    if _cor_proxima((r, g, b), (254, 169, 59), 50):  # VarIAção do laranja
        return True
    
    # 3) Tons de laranja/amarelo também contam como pista
    if _cor_proxima((r, g, b), (255, 200, 0), 50):  # Amarelo-laranja
        return True
    if _cor_proxima((r, g, b), (255, 140, 0), 50):  # Laranja escuro
        return True

    # 4) Magenta = checkpoints (É pista válida para a IA seguir)
    # O magenta é o caminho que a IA deve seguir em loop
    if _cor_proxima((r, g, b), (255, 0, 255), 50):  # Magenta
        return True

    return False

# Cache para detecção de pista (otimização de performance)
_pixel_cache = {}
_cache_hits = 0
_cache_misses = 0

def eh_pixel_transitavel(surface, x, y):
    """True se é área transitável (não colide); False se é parede/limite."""
    global _cache_hits, _cache_misses
    
    if x < 0 or y < 0 or x >= surface.get_width() or y >= surface.get_height():
        return False

    # Verificar cache primeiro
    cache_key = (x, y)
    if cache_key in _pixel_cache:
        _cache_hits += 1
        return _pixel_cache[cache_key]
    
    _cache_misses += 1
    r, g, b, _ = surface.get_at((x, y))

    # 1) Verde = fora da pista (limite) - NÃO transitável
    if _cor_proxima((r, g, b), (0, 255, 0), 50):
        return False

    # 2) Laranja = pista (área válida para carros) - transitável
    if _cor_proxima((r, g, b), (255, 165, 0), 50):  # Laranja padrão
        return True
    if _cor_proxima((r, g, b), (254, 168, 59), 50):  # Laranja da sua imagem
        return True
    if _cor_proxima((r, g, b), (254, 169, 59), 50):  # VarIAção do laranja
        return True
    
    # 3) Tons de laranja/amarelo também contam como transitável
    if _cor_proxima((r, g, b), (255, 200, 0), 50):  # Amarelo-laranja
        return True
    if _cor_proxima((r, g, b), (255, 140, 0), 50):  # Laranja escuro
        return True

    # 4) Magenta = checkpoints (transitável para carros)
    # O magenta é transitável para carros e pode ser usado como pista
    if _cor_proxima((r, g, b), (255, 0, 255), 50):  # Magenta padrão
        return True
    if _cor_proxima((r, g, b), (254, 0, 254), 50):  # Magenta da sua imagem
        return True
    if _cor_proxima((r, g, b), (254, 0, 253), 50):  # VarIAção do magenta
        return True
    if _cor_proxima((r, g, b), (254, 0, 252), 50):  # VarIAção do magenta
        return True
    if _cor_proxima((r, g, b), (253, 0, 252), 50):  # VarIAção do magenta
        return True
    if _cor_proxima((r, g, b), (254, 9, 241), 50):  # VarIAção do magenta
        return True
    if _cor_proxima((r, g, b), (254, 6, 244), 50):  # VarIAção do magenta
        return True
    # Adicionar mais varIAções de magenta para garantir cobertura total
    if _cor_proxima((r, g, b), (255, 0, 254), 50):  # Magenta claro
        return True
    if _cor_proxima((r, g, b), (254, 0, 255), 50):  # Magenta alternativo
        return True
    if _cor_proxima((r, g, b), (253, 0, 255), 50):  # Magenta alternativo
        return True
    
    # 5) Tons de rosa/magenta que não estavam sendo detectados
    if _cor_proxima((r, g, b), (254, 65, 175), 50):  # Rosa-magenta
        return True
    if _cor_proxima((r, g, b), (254, 55, 188), 50):  # Rosa-magenta
        return True
    if _cor_proxima((r, g, b), (254, 48, 195), 50):  # Rosa-magenta
        return True
    if _cor_proxima((r, g, b), (254, 41, 204), 50):  # Rosa-magenta
        return True
    if _cor_proxima((r, g, b), (254, 34, 211), 50):  # Rosa-magenta
        return True
    if _cor_proxima((r, g, b), (254, 30, 218), 50):  # Rosa-magenta
        return True
    if _cor_proxima((r, g, b), (254, 28, 217), 50):  # Rosa-magenta
        return True
    if _cor_proxima((r, g, b), (254, 28, 220), 50):  # Rosa-magenta
        return True
    if _cor_proxima((r, g, b), (254, 26, 222), 50):  # Rosa-magenta
        return True
    if _cor_proxima((r, g, b), (254, 23, 225), 50):  # Rosa-magenta
        resultado = True
    else:
        resultado = False
    
    # Armazenar no cache (limitar tamanho do cache)
    if len(_pixel_cache) < 10000:  # Limite de 10k entradas
        _pixel_cache[cache_key] = resultado
    
    return resultado

def limpar_cache_pista():
    """Limpa o cache de detecção de pista"""
    global _pixel_cache, _cache_hits, _cache_misses
    _pixel_cache.clear()
    _cache_hits = 0
    _cache_misses = 0

def obter_estatisticas_cache():
    """Retorna estatísticas do cache de detecção de pista"""
    total = _cache_hits + _cache_misses
    hit_rate = (_cache_hits / total * 100) if total > 0 else 0
    return {
        'hits': _cache_hits,
        'misses': _cache_misses,
        'total': total,
        'hit_rate': hit_rate,
        'cache_size': len(_pixel_cache)
    }

# ---------- carregamento ----------
def carregar_pista():
    from config import CONFIGURACOES, CAMINHO_MAPA, CAMINHO_GUIAS
    pista = pygame.image.load(CAMINHO_MAPA).convert()
    
    # Aplicar configurações de qualidade
    qualidade_alta = CONFIGURACOES["video"]["qualidade_alta"]
    
    if pista.get_width() != LARGURA or pista.get_height() != ALTURA:
        if qualidade_alta:
            pista = pygame.transform.smoothscale(pista, (LARGURA, ALTURA))
        else:
            # Usar scale normal para melhor performance
            pista = pygame.transform.scale(pista, (LARGURA, ALTURA))

    mascara_pista = pista.copy()

    if os.path.exists(CAMINHO_GUIAS):
        guides = pygame.image.load(CAMINHO_GUIAS).convert_alpha()
        if guides.get_width() != LARGURA or guides.get_height() != ALTURA:
            guides = pygame.transform.smoothscale(guides, (LARGURA, ALTURA))
    else:
        guides = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)

    return pista, mascara_pista, guides

# ---------- checkpoints ----------
def extrair_checkpoints(surface):
    """Encontra uma sequêncIA de checkpoints ao longo do caminho magenta"""
    pontos = []
    
    def eh_magenta(r, g, b):
        """Verifica se a cor é magenta (incluindo varIAções)"""
        # Magenta padrão
        if _cor_proxima((r, g, b), (255, 0, 255), CHECKPOINT_TOL):
            return True
        if _cor_proxima((r, g, b), (254, 0, 254), CHECKPOINT_TOL):
            return True
        if _cor_proxima((r, g, b), (254, 0, 253), CHECKPOINT_TOL):
            return True
        if _cor_proxima((r, g, b), (254, 0, 252), CHECKPOINT_TOL):
            return True
        if _cor_proxima((r, g, b), (253, 0, 252), CHECKPOINT_TOL):
            return True
        if _cor_proxima((r, g, b), (254, 9, 241), CHECKPOINT_TOL):
            return True
        if _cor_proxima((r, g, b), (254, 6, 244), CHECKPOINT_TOL):
            return True
        # Tons de rosa/magenta
        if _cor_proxima((r, g, b), (254, 65, 175), CHECKPOINT_TOL):
            return True
        if _cor_proxima((r, g, b), (254, 55, 188), CHECKPOINT_TOL):
            return True
        if _cor_proxima((r, g, b), (254, 48, 195), CHECKPOINT_TOL):
            return True
        if _cor_proxima((r, g, b), (254, 41, 204), CHECKPOINT_TOL):
            return True
        if _cor_proxima((r, g, b), (254, 34, 211), CHECKPOINT_TOL):
            return True
        if _cor_proxima((r, g, b), (254, 30, 218), CHECKPOINT_TOL):
            return True
        if _cor_proxima((r, g, b), (254, 28, 217), CHECKPOINT_TOL):
            return True
        if _cor_proxima((r, g, b), (254, 28, 220), CHECKPOINT_TOL):
            return True
        if _cor_proxima((r, g, b), (254, 26, 222), CHECKPOINT_TOL):
            return True
        if _cor_proxima((r, g, b), (254, 23, 225), CHECKPOINT_TOL):
            return True
        return False
    
    # Encontrar pixels magenta com amostragem
    pixels_magenta = []
    step = 4
    for x in range(0, LARGURA, step):
        for y in range(0, ALTURA, step):
            r,g,b,a = surface.get_at((x,y))
            if a > 0 and eh_magenta(r, g, b):
                pixels_magenta.append((x, y))
    
    if not pixels_magenta:
        print("Nenhum pixel magenta encontrado")
        return pontos
    
    print(f"Encontrados {len(pixels_magenta)} pixels magenta")
    
    # Ordenar pixels para crIAr um caminho sequencIAl
    # Primeiro, encontrar o pixel mais próximo do início (canto superior esquerdo)
    if pixels_magenta:
        # Encontrar ponto de partida (mais próximo do canto superior esquerdo)
        inicio = min(pixels_magenta, key=lambda p: p[0] + p[1])
        pontos_ordenados = [inicio]
        pixels_restantes = [p for p in pixels_magenta if p != inicio]
        
        # Construir caminho sequencIAl (algoritmo do vizinho mais próximo)
        while pixels_restantes:
            ultimo_ponto = pontos_ordenados[-1]
            # Encontrar o pixel mais próximo do último ponto
            proximo = min(pixels_restantes, key=lambda p: 
                (p[0] - ultimo_ponto[0])**2 + (p[1] - ultimo_ponto[1])**2)
            pontos_ordenados.append(proximo)
            pixels_restantes.remove(proximo)
        
        # Dividir o caminho em segmentos para crIAr checkpoints
        segmento_size = max(20, len(pontos_ordenados) // 8)  # 8 checkpoints máximo
        for i in range(0, len(pontos_ordenados), segmento_size):
            segmento = pontos_ordenados[i:i+segmento_size]
            if len(segmento) >= 5:  # Mínimo de 5 pixels por checkpoint
                # Calcular centro do segmento
                centro_x = sum(p[0] for p in segmento) / len(segmento)
                centro_y = sum(p[1] for p in segmento) / len(segmento)
                pontos.append((centro_x, centro_y))
        
        print(f"CrIAdos {len(pontos)} checkpoints sequencIAis")
        for i, (x, y) in enumerate(pontos):
            print(f"  Checkpoint {i+1}: ({x:.1f}, {y:.1f})")
    
    return pontos

def _angulo(b, c, centro):
    return math.atan2(b[1]-centro[1], b[0]-centro[0])

def ordenar_checkpoints(pontos, sentido="horario"):
    if not pontos:
        return []
    cx = sum(p[0] for p in pontos)/len(pontos)
    cy = sum(p[1] for p in pontos)/len(pontos)
    pontos = sorted(pontos, key=lambda p: _angulo((0,0), p, (cx,cy)))
    if sentido == "horario":
        pontos = pontos[::-1]
    return pontos

# ---------- utilidades de rota ----------
def _interpolar(a, b, passo):
    ax,ay = a; bx,by = b
    dx,dy = bx-ax, by-ay
    dist = math.hypot(dx,dy)
    if dist < 1e-6:
        return []
    n = max(1, int(dist // passo))
    pts = []
    for i in range(1, n+1):
        t = i / n
        pts.append((ax + dx*t, ay + dy*t))
    return pts

def densificar(points, passo=28):
    if not points:
        return []
    out = [points[0]]
    for i in range(len(points)):
        a = points[i]
        b = points[(i+1) % len(points)]
        out.extend(_interpolar(a,b, passo))
    return out

def suavizar_chaikin(points, iters=2):
    if not points:
        return []
    pts = list(points)
    for _ in range(iters):
        novo = []
        for i in range(len(pts)):
            ax, ay = pts[i]
            bx, by = pts[(i+1)%len(pts)]
            qx, qy = ax*0.75 + bx*0.25, ay*0.75 + by*0.25
            rx, ry = ax*0.25 + bx*0.75, ay*0.25 + by*0.75
            novo.extend([(qx,qy), (rx,ry)])
        pts = novo
    return pts

# ---------- I/O de waypoints ----------
def salvar_waypoints(points, caminho_json=CAMINHO_WAYPOINTS_JSON):
    os.makedirs(os.path.dirname(caminho_json), exist_ok=True)
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump([ [float(x), float(y)] for (x,y) in points], f, ensure_ascii=False, indent=2)

def carregar_waypoints(caminho_json=CAMINHO_WAYPOINTS_JSON):
    if not os.path.exists(caminho_json):
        return None
    with open(caminho_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [(float(x), float(y)) for x,y in data]

# ---------- rota para Pure Pursuit ----------
def gerar_rota_pp(surface_guides):
    # 1) se existir JSON gravado, usamos
    gravados = carregar_waypoints()
    if gravados:
        base = gravados
    else:
        # 2) senão, tenta checkpoints magenta
        cps = extrair_checkpoints(surface_guides)
        if cps:
            cps = ordenar_checkpoints(cps, "horario")
            base = cps
        else:
            # 3) senão, fallback estático
            base = WAYPOINTS_MAP_1

    suave = suavizar_chaikin(base, iters=2)
    denso = densificar(suave, passo=26)
    return denso

# ---------- debug visual da rota ----------
def desenhar_rota_debug(superficie, camera, pontos, cor=(120,200,255)):
    if not pontos or not camera:
        return
    
    try:
        pts = []
        for (x, y) in pontos:
            try:
                sx, sy = camera.mundo_para_tela(x, y)
                # Verificar se as coordenadas são válidas
                if not (isinstance(sx, (int, float)) and isinstance(sy, (int, float))):
                    continue
                pts.append((sx, sy))
            except Exception as e:
                print(f"Erro ao converter coordenada ({x}, {y}): {e}")
                continue
        
        if len(pts) > 1:
            pygame.draw.lines(superficie, cor, True, pts, 2)
            for (x,y) in pts[:: max(1, len(pts)//24) ]:
                pygame.draw.circle(superficie, (255,255,0), (int(x), int(y)), 3)
    except Exception as e:
        print(f"Erro ao desenhar rota debug: {e}")

# Cache para checkpoints
_checkpoints_cache = None

def limpar_cache_checkpoints():
    """Limpa o cache de checkpoints quando o mapa é trocado"""
    global _checkpoints_cache
    _checkpoints_cache = None

# ---------- desenhar checkpoints ----------
def desenhar_checkpoints(superficie, camera, checkpoints=None):
    """Desenha os checkpoints com uma linha branca no chão"""
    global _checkpoints_cache
    
    if not camera:
        return
    
    # Usar checkpoints fornecidos ou usar cache
    if checkpoints is None:
        if _checkpoints_cache is None:
            # Carregar checkpoints da superfície de guias apenas uma vez
            if os.path.exists(CAMINHO_GUIAS):
                try:
                    surface_guides = pygame.image.load(CAMINHO_GUIAS).convert_alpha()
                    if surface_guides.get_width() != LARGURA or surface_guides.get_height() != ALTURA:
                        surface_guides = pygame.transform.smoothscale(surface_guides, (LARGURA, ALTURA))
                    checkpoints = extrair_checkpoints(surface_guides)
                    if checkpoints:
                        checkpoints = ordenar_checkpoints(checkpoints, "horario")
                        _checkpoints_cache = checkpoints
                except Exception as e:
                    print(f"Erro ao carregar checkpoints: {e}")
                    _checkpoints_cache = []
            else:
                _checkpoints_cache = []
        else:
            checkpoints = _checkpoints_cache
    
    if not checkpoints:
        return
    
    # Desenhar linha branca conectando os checkpoints
    try:
        pts = [camera.mundo_para_tela(x, y) for (x, y) in checkpoints]
        if len(pts) > 1:
            # Linha branca grossa no chão
            pygame.draw.lines(superficie, (255, 255, 255), False, pts, 4)
            
            # Círculos brancos nos pontos de checkpoint
            for (x, y) in pts:
                pygame.draw.circle(superficie, (255, 255, 255), (int(x), int(y)), 8)
                # Borda preta para contraste
                pygame.draw.circle(superficie, (0, 0, 0), (int(x), int(y)), 8, 2)
    except Exception as e:
        print(f"Erro ao desenhar checkpoints: {e}")

def encontrar_linha_amarela(surface):
    """Encontra a linha amarela de largada no mapa"""
    pixels_amarelos = []
    
    def eh_amarelo(r, g, b):
        """Verifica se a cor é amarela (incluindo varIAções)"""
        # Amarelo puro
        if _cor_proxima((r, g, b), (255, 255, 0), 30):
            return True
        # Amarelo dourado
        if _cor_proxima((r, g, b), (255, 215, 0), 30):
            return True
        # Amarelo claro
        if _cor_proxima((r, g, b), (255, 255, 100), 30):
            return True
        # Amarelo escuro
        if _cor_proxima((r, g, b), (255, 200, 0), 30):
            return True
        # Amarelo-laranja
        if _cor_proxima((r, g, b), (255, 180, 0), 30):
            return True
        return False
    
    # Procurar pixels amarelos com amostragem
    step = 2
    for x in range(0, LARGURA, step):
        for y in range(0, ALTURA, step):
            r, g, b, a = surface.get_at((x, y))
            if a > 0 and eh_amarelo(r, g, b):
                pixels_amarelos.append((x, y))
    
    if not pixels_amarelos:
        print("Nenhuma linha amarela encontrada")
        return None
    
    print(f"Encontrados {len(pixels_amarelos)} pixels amarelos")
    
    # Encontrar a linha amarela (assumindo que é horizontal)
    # Agrupar por Y e encontrar a linha com mais pixels
    linhas_y = {}
    for x, y in pixels_amarelos:
        if y not in linhas_y:
            linhas_y[y] = []
        linhas_y[y].append(x)
    
    # Encontrar a linha com mais pixels (linha principal)
    linha_principal_y = max(linhas_y.keys(), key=lambda y: len(linhas_y[y]))
    pixels_linha = linhas_y[linha_principal_y]
    
    # Calcular centro da linha
    centro_x = sum(pixels_linha) / len(pixels_linha)
    centro_y = linha_principal_y
    
    print(f"Linha amarela encontrada em Y={centro_y}, centro X={centro_x:.1f}")
    
    return (centro_x, centro_y)

def calcular_posicoes_iniciais(surface):
    """Calcula posições inicIAis atrás da linha amarela"""
    linha_amarela = encontrar_linha_amarela(surface)
    
    if not linha_amarela:
        # Fallback para posições centralizadas
        print("Usando posições de fallback")
        centro_x = LARGURA // 2
        centro_y = ALTURA // 2
        return {
            'p1': (centro_x - 30, centro_y - 20),
            'p2': (centro_x + 30, centro_y - 20),
            'IA': (centro_x, centro_y + 10)
        }
    
    linha_x, linha_y = linha_amarela
    
    # Posicionar carros atrás da linha (Y maior = mais para baixo)
    offset_y = 40  # DistâncIA atrás da linha
    offset_lateral = 30  # DistâncIA entre carros
    
    posicoes = {
        'p1': (linha_x - offset_lateral, linha_y + offset_y),
        'p2': (linha_x + offset_lateral, linha_y + offset_y),
        'IA': (linha_x, linha_y + offset_y + 20)  # IA um pouco mais atrás
    }
    
    print(f"Posições calculadas atrás da linha amarela:")
    print(f"  P1: {posicoes['p1']}")
    print(f"  P2: {posicoes['p2']}")
    print(f"  IA: {posicoes['IA']}")
    
    return posicoes
