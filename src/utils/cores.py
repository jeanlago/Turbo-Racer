import pygame

def cor_proxima_de_alguma(rgb, paleta, tol=0):
    r, g, b = rgb
    for pr, pg, pb in paleta:
        if abs(r - pr) <= tol and abs(g - pg) <= tol and abs(b - pb) <= tol:
            return True
    return False

def asfalto_por_hsv(rgb, s_max, v_max):
    c = pygame.Color(*rgb)
    h, s, v, _ = c.hsva
    return (s <= s_max and v <= v_max)
