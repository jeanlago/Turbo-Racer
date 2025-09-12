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

    # 1) Limite especial (verde-lima) SEMPRE fora
    if _cor_proxima((r, g, b), (0, 255, 0), 45):
        return False

    # 2) Cinzas/brancos (baixa saturação) contam como pista
    if _is_grey_like((r, g, b)):
        return True

    # 3) Paleta explícita adicional
    for pr, pg, pb in CORES_PISTA:
        if _cor_proxima((r, g, b), (pr, pg, pb), TOLERANCIA_COR):
            return True

    return False


# ---------- carregamento ----------
def carregar_pista():
    pista = pygame.image.load(CAMINHO_MAPA).convert()
    if pista.get_width() != LARGURA or pista.get_height() != ALTURA:
        pista = pygame.transform.smoothscale(pista, (LARGURA, ALTURA))

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
    visited = [[False]*ALTURA for _ in range(LARGURA)]
    pontos = []
    for x in range(LARGURA):
        for y in range(ALTURA):
            if visited[x][y]: 
                continue
            r,g,b,a = surface.get_at((x,y))
            if a<=0: 
                continue
            if _cor_proxima((r,g,b), CHECKPOINT_COR, CHECKPOINT_TOL):
                fila = [(x,y)]
                visited[x][y] = True
                soma_x=soma_y=cont=0
                while fila:
                    cx,cy = fila.pop()
                    soma_x += cx; soma_y += cy; cont += 1
                    for nx,ny in ((cx+1,cy),(cx-1,cy),(cx,cy+1),(cx,cy-1)):
                        if 0<=nx<LARGURA and 0<=ny<ALTURA and not visited[nx][ny]:
                            r2,g2,b2,a2 = surface.get_at((nx,ny))
                            if a2>0 and _cor_proxima((r2,g2,b2), CHECKPOINT_COR, CHECKPOINT_TOL):
                                visited[nx][ny] = True
                                fila.append((nx,ny))
                if cont >= CHECKPOINT_MIN_PIXELS:
                    pontos.append((soma_x/cont, soma_y/cont))
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
    pts = [camera.mundo_para_tela(x, y) for (x,y) in pontos]
    pygame.draw.lines(superficie, cor, True, pts, 2)
    for (x,y) in pts[:: max(1, len(pts)//24) ]:
        pygame.draw.circle(superficie, (255,255,0), (int(x), int(y)), 3)
