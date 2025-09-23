#!/usr/bin/env python3
"""
Teste simples para verificar se a IA funciona com física antiga.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pygame
from core.IA import IAMelhorada
from core.carro import Carro

def testar():
    print("=== TESTE SIMPLES ===")
    
    pygame.init()
    pygame.display.set_mode((800, 600))
    
    # Checkpoints simples
    checkpoints = [(100, 100), (200, 100), (200, 200), (100, 200)]
    
    # IA
    IA = IAMelhorada(checkpoints, nome="IA-Teste")
    
    # Carro com física antiga
    carro = Carro(100, 100, "Car3", (0, 0, 0, 0), nome="Carro-Teste")
    
    print(f"✓ IA: {IA.nome}")
    print(f"✓ Carro: {carro.nome}")
    
    # Testar alguns frames
    dt = 1.0 / 60.0
    for i in range(5):
        IA.controlar(carro, None, lambda x, y: True, dt)
        print(f"Frame {i}: Pos=({carro.x:.1f}, {carro.y:.1f}), Ângulo={carro.angulo:.1f}°")
    
    print("✅ Teste concluído!")
    pygame.quit()

if __name__ == "__main__":
    testar()
