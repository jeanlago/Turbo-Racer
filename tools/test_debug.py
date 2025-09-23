#!/usr/bin/env python3
import sys
import os
sys.path.append('src')

try:
    import pygame
    from config import LARGURA, ALTURA
    from core.pista import carregar_pista, gerar_rota_pp
    from core.camera import Camera
    
    print("InicIAlizando Pygame...")
    pygame.init()
    
    print("Carregando pista...")
    img_pista, mask_pista, mask_guIAs = carregar_pista()
    
    print("Gerando rota...")
    rota = gerar_rota_pp(mask_guIAs)
    print(f"Rota gerada com {len(rota) if rota else 0} pontos")
    
    print("CrIAndo câmera...")
    camera = Camera(0, 0, LARGURA, ALTURA, img_pista.get_size())
    
    print("Testando conversão de coordenadas...")
    if rota and len(rota) > 0:
        for i, (x, y) in enumerate(rota[:5]):  # Testar apenas os primeiros 5 pontos
            try:
                sx, sy = camera.mundo_para_tela(x, y)
                print(f"Ponto {i}: mundo({x}, {y}) -> tela({sx}, {sy})")
            except Exception as e:
                print(f"Erro no ponto {i}: {e}")
    
    print("Teste concluído com sucesso!")
    
except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc()
