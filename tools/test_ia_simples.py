#!/usr/bin/env python3
"""
Teste simples para verificar se a nova IA está funcionando no jogo.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pygame
from core.IA import IAMelhorada
from core.carro_fisica import CarroFisica

def testar_IA_simples():
    """Teste básico da IA"""
    print("=== TESTE SIMPLES DA IA MELHORADA ===")
    
    # InicIAlizar pygame
    pygame.init()
    pygame.display.set_mode((800, 600))
    
    # CrIAr checkpoints simples
    checkpoints = [(100, 100), (200, 100), (200, 200), (100, 200)]
    
    # CrIAr IA
    IA = IAMelhorada(checkpoints, nome="IA-Teste")
    IA.debug = True
    
    # CrIAr carro
    carro = CarroFisica(100, 100, "Car3", (0, 0, 0, 0), nome="Carro-Teste", tipo_tracao="rear")
    
    print(f"✓ IA crIAda: {IA.nome}")
    print(f"✓ Carro crIAdo: {carro.nome}")
    print(f"✓ Checkpoints: {len(checkpoints)}")
    
    # Testar alguns controles
    dt = 1.0 / 60.0
    
    print("\n=== TESTANDO CONTROLES ===")
    
    # Simular controle da IA
    for i in range(10):
        # Simular teclas (todas False)
        teclas = [False] * 512
        
        # Controlar carro com IA
        IA.controlar(carro, None, lambda x, y: True, dt)
        
        print(f"Frame {i}: Pos=({carro.x:.1f}, {carro.y:.1f}), Vel={carro.velocidade:.2f}")
    
    print("\n✅ Teste concluído!")
    pygame.quit()

if __name__ == "__main__":
    testar_IA_simples()
