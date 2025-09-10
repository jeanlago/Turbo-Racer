import pygame
from config import (
    LARGURA, ALTURA,
    CAMINHO_MAPA,
    CORES_PISTA, TOLERANCIA_COR,
    HSV_S_MAX, HSV_V_MAX
)
from utils.cores import cor_proxima_de_alguma, asfalto_por_hsv

def carregar_pista():
    imagem = pygame.image.load(CAMINHO_MAPA).convert()
    if imagem.get_width() != LARGURA or imagem.get_height() != ALTURA:
        imagem = pygame.transform.smoothscale(imagem, (LARGURA, ALTURA))
    mascara = imagem.copy()
    return imagem, mascara

def eh_pixel_da_pista(superficie, x, y):
    if not (0 <= x < LARGURA and 0 <= y < ALTURA):
        return False
    rgb = superficie.get_at((x, y))[:3]
    return (
        cor_proxima_de_alguma(rgb, CORES_PISTA, TOLERANCIA_COR)
        or asfalto_por_hsv(rgb, HSV_S_MAX, HSV_V_MAX)
    )
