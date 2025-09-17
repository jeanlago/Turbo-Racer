#!/usr/bin/env python3
import sys
import os
sys.path.append('src')

import pygame
import math
from config import LARGURA, ALTURA, CAMINHO_GUIAS
from core.pista import eh_pixel_transitavel, eh_pixel_da_pista
from core.checkpoint_manager import CheckpointManager

def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Debug IA Travada")
    
    # Carregar imagem de guias
    if os.path.exists(CAMINHO_GUIAS):
        surface_guides = pygame.image.load(CAMINHO_GUIAS).convert_alpha()
        if surface_guides.get_width() != LARGURA or surface_guides.get_height() != ALTURA:
            surface_guides = pygame.transform.smoothscale(surface_guides, (LARGURA, ALTURA))
    else:
        print("Arquivo de guias não encontrado!")
        return
    
    # Carregar checkpoints
    checkpoint_manager = CheckpointManager()
    checkpoints = checkpoint_manager.checkpoints
    
    if not checkpoints:
        print("Nenhum checkpoint encontrado!")
        return
    
    print(f"Analisando {len(checkpoints)} checkpoints...")
    
    # Analisar cada checkpoint
    for i, (cx, cy) in enumerate(checkpoints):
        print(f"\n--- Checkpoint {i+1}: ({cx:.1f}, {cy:.1f}) ---")
        
        # Verificar área ao redor do checkpoint
        raio = 50
        pontos_problema = []
        pontos_ok = []
        
        for dx in range(-raio, raio + 1, 5):
            for dy in range(-raio, raio + 1, 5):
                x = int(cx + dx)
                y = int(cy + dy)
                
                if 0 <= x < LARGURA and 0 <= y < ALTURA:
                    # Verificar se é transitável
                    transitavel = eh_pixel_transitavel(surface_guides, x, y)
                    pista = eh_pixel_da_pista(surface_guides, x, y)
                    
                    if not transitavel:
                        pontos_problema.append((x, y))
                    else:
                        pontos_ok.append((x, y))
        
        print(f"  Pontos transitáveis: {len(pontos_ok)}")
        print(f"  Pontos problemáticos: {len(pontos_problema)}")
        
        if pontos_problema:
            print(f"  ⚠️  Checkpoint {i+1} tem {len(pontos_problema)} pontos não transitáveis ao redor!")
            # Mostrar alguns exemplos
            for j, (px, py) in enumerate(pontos_problema[:5]):
                r, g, b, a = surface_guides.get_at((px, py))
                print(f"    Exemplo {j+1}: ({px}, {py}) = RGB({r}, {g}, {b})")
        else:
            print(f"  ✅ Checkpoint {i+1} está em área transitável")
    
    # Desenhar debug visual
    tela.fill((0, 0, 0))
    tela.blit(surface_guides, (0, 0))
    
    fonte = pygame.font.SysFont("consolas", 16)
    
    # Desenhar checkpoints
    for i, (cx, cy) in enumerate(checkpoints):
        # Verificar se checkpoint está em área transitável
        transitavel = eh_pixel_transitavel(surface_guides, int(cx), int(cy))
        pista = eh_pixel_da_pista(surface_guides, int(cx), int(cy))
        
        if not transitavel:
            cor = (255, 0, 0)  # Vermelho para problemático
            print(f"❌ Checkpoint {i+1} em área não transitável!")
        elif not pista:
            cor = (255, 165, 0)  # Laranja para transitável mas não pista
            print(f"⚠️  Checkpoint {i+1} transitável mas não é pista")
        else:
            cor = (0, 255, 0)  # Verde para OK
        
        # Desenhar círculo
        pygame.draw.circle(tela, cor, (int(cx), int(cy)), 20, 3)
        pygame.draw.circle(tela, cor, (int(cx), int(cy)), 10)
        
        # Número
        texto = fonte.render(str(i+1), True, (255, 255, 255))
        texto_rect = texto.get_rect(center=(int(cx), int(cy)))
        tela.blit(texto, texto_rect)
        
        # Status
        status = "OK" if transitavel and pista else "PROBLEMA"
        status_texto = fonte.render(status, True, cor)
        tela.blit(status_texto, (int(cx) - 30, int(cy) + 25))
    
    # Legenda
    legenda = [
        "VERDE: Checkpoint OK (transitável + pista)",
        "LARANJA: Transitável mas não é pista",
        "VERMELHO: Não transitável (PROBLEMA!)"
    ]
    
    for i, texto in enumerate(legenda):
        cor = (0, 255, 0) if i == 0 else (255, 165, 0) if i == 1 else (255, 0, 0)
        tela.blit(fonte.render(texto, True, cor), (10, 10 + i * 25))
    
    pygame.display.flip()
    
    # Aguardar fechamento
    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False
    
    pygame.quit()

if __name__ == "__main__":
    main()
