#!/usr/bin/env python3
"""
Teste específico para verificar se o carro está virando corretamente.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pygame
import math
from core.carro_fisica import CarroFisica

def testar_carro_direcao():
    """Teste específico de direção do carro"""
    print("=== TESTE DE DIREÇÃO DO CARRO ===")
    
    # InicIAlizar pygame
    pygame.init()
    pygame.display.set_mode((800, 600))
    
    # CrIAr carro
    carro = CarroFisica(400, 300, "Car3", (0, 0, 0, 0), nome="Carro-Teste", tipo_tracao="rear")
    carro.angulo = 0  # Apontando para -X (esquerda)
    
    print(f"✓ Carro crIAdo: {carro.nome}")
    print(f"✓ Ângulo inicIAl: {carro.angulo}°")
    
    dt = 1.0 / 60.0
    
    # Teste 1: Virar para direita
    print("\n--- TESTE 1: Virar para direita ---")
    for i in range(10):
        carro.atualizar_com_ai(None, dt, False, True, False, False, False)
        print(f"  Frame {i}: Ângulo={carro.angulo:.1f}°")
    
    # Resetar carro
    carro.x = 400
    carro.y = 300
    carro.angulo = 0
    carro.vx = 0
    carro.vy = 0
    
    # Teste 2: Virar para esquerda
    print("\n--- TESTE 2: Virar para esquerda ---")
    for i in range(10):
        carro.atualizar_com_ai(None, dt, False, False, True, False, False)
        print(f"  Frame {i}: Ângulo={carro.angulo:.1f}°")
    
    # Resetar carro
    carro.x = 400
    carro.y = 300
    carro.angulo = 0
    carro.vx = 0
    carro.vy = 0
    
    # Teste 3: Acelerar e virar
    print("\n--- TESTE 3: Acelerar e virar para direita ---")
    for i in range(10):
        carro.atualizar_com_ai(None, dt, True, True, False, False, False)
        print(f"  Frame {i}: Ângulo={carro.angulo:.1f}°, Vel={math.sqrt(carro.vx*carro.vx + carro.vy*carro.vy):.2f}")
    
    print("\n✅ Teste de direção do carro concluído!")
    pygame.quit()

if __name__ == "__main__":
    testar_carro_direcao()
