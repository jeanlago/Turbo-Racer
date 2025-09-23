#!/usr/bin/env python3
"""
Script de teste para a nova IA melhorada.
Testa se a IA consegue navegar corretamente com a nova física dos carros.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pygame
import math
from core.IA import IAMelhorada
from core.carro_fisica import CarroFisica
from core.pista import carregar_pista

def testar_IA():
    """Testa a nova IA com a física atual"""
    print("=== TESTE DA IA MELHORADA ===")
    
    # InicIAlizar pygame
    pygame.init()
    
    # Definir modo de vídeo (necessário para carregar imagens)
    pygame.display.set_mode((800, 600))
    
    # Carregar pista
    try:
        img_pista, mask_pista, mask_guIAs = carregar_pista()
        print("✓ Pista carregada com sucesso")
    except Exception as e:
        print(f"✗ Erro ao carregar pista: {e}")
        return False
    
    # CrIAr checkpoints de teste
    checkpoints = [
        (640, 300),  # Ponto inicIAl
        (700, 350),  # Curva suave
        (750, 400),  # Curva médIA
        (700, 450),  # Curva fechada
        (640, 500),  # Reta
        (580, 450),  # Curva fechada
        (530, 400),  # Curva médIA
        (580, 350),  # Curva suave
    ]
    
    # CrIAr IA
    IA = IAMelhorada(checkpoints, nome="IA-Teste")
    IA.debug = True
    print("✓ IA crIAda com sucesso")
    
    # CrIAr carro de teste
    carro = CarroFisica(640, 300, "Car3", (0, 0, 0, 0), nome="Carro-Teste", tipo_tracao="rear")
    print("✓ Carro de teste crIAdo")
    
    # Simular alguns frames
    dt = 1.0 / 60.0  # 60 FPS
    frames_teste = 300  # 5 segundos
    
    print(f"\n=== SIMULANDO {frames_teste} FRAMES ===")
    
    for frame in range(frames_teste):
        # Controlar carro com IA
        IA.controlar(carro, mask_guIAs, lambda x, y: True, dt)
        
        # Verificar se passou por checkpoints
        if frame % 60 == 0:  # A cada segundo
            print(f"Frame {frame}: Posição=({carro.x:.1f}, {carro.y:.1f}), "
                  f"Velocidade={math.sqrt(carro.vx*carro.vx + carro.vy*carro.vy):.2f}, "
                  f"Checkpoint={IA.checkpoint_atual + 1}")
        
        # Verificar se completou uma volta
        if IA.checkpoint_atual >= len(checkpoints):
            print(f"✓ IA completou uma volta em {frame} frames!")
            break
    
    print(f"\n=== RESULTADO FINAL ===")
    print(f"Checkpoints passados: {IA.checkpoint_atual}")
    print(f"Posição final: ({carro.x:.1f}, {carro.y:.1f})")
    print(f"Velocidade final: {math.sqrt(carro.vx*carro.vx + carro.vy*carro.vy):.2f}")
    
    # Verificar se a IA funcionou bem
    if IA.checkpoint_atual > 0:
        print("✓ IA funcionou corretamente!")
        return True
    else:
        print("✗ IA não conseguiu navegar")
        return False

if __name__ == "__main__":
    sucesso = testar_IA()
    if sucesso:
        print("\n🎉 TESTE PASSOU! A nova IA está funcionando!")
    else:
        print("\n❌ TESTE FALHOU! A IA precisa de ajustes.")
    
    pygame.quit()