import pygame
import os
import math
from config import LARGURA, ALTURA

COR_PISTA_CINZA_MIN = 88
COR_PISTA_CINZA_MAX = 91
COR_PISTA_ESPECIAL = 165
COR_BRANCO = 255
COR_GRAMA_VERDE = (0, 200, 0)

TOLERANCIA_COR = 10

def _cor_proxima(cor, alvo, tol):
    r, g, b = cor[0], cor[1], cor[2]
    ar, ag, ab = alvo[0], alvo[1], alvo[2]
    return abs(r - ar) <= tol and abs(g - ag) <= tol and abs(b - ab) <= tol

def eh_pixel_transitavel_grip(surface, x, y):
    return True

def eh_pixel_grama_grip(surface, x, y):
    if x < 0 or y < 0 or x >= surface.get_width() or y >= surface.get_height():
        return False
    
    try:
        cor = surface.get_at((int(x), int(y)))
        r, g, b = cor[0], cor[1], cor[2]
    except (IndexError, ValueError):
        return False
    
    if (COR_PISTA_CINZA_MIN <= r <= COR_PISTA_CINZA_MAX) or \
       (r == COR_PISTA_ESPECIAL) or \
       (r == COR_BRANCO):
        return False
    
    if g > r + 30 and g > b + 30:
        return True
    
    if abs(r - g) < 10 and abs(g - b) < 10:
        return False
    
    return True

def verificar_colisao_grip(surface, x, y, raio=15):
    return False

def verificar_na_grama_grip(surface, x, y, raio=15):
    if eh_pixel_grama_grip(surface, x, y):
        return True
    pontos_verificacao = []
    num_pontos = 8
    for i in range(num_pontos):
        angulo = (2 * math.pi * i) / num_pontos
        px = x + raio * math.cos(angulo)
        py = y + raio * math.sin(angulo)
        pontos_verificacao.append((px, py))
    
    grama_count = 0
    for px, py in pontos_verificacao:
        if eh_pixel_grama_grip(surface, px, py):
            grama_count += 1
    
    return grama_count > len(pontos_verificacao) * 0.3

