#!/usr/bin/env python3
"""
Teste da IA melhorada com a física antiga (Carro) para comparar.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pygame
import math
from core.IA import IAMelhorada
from core.carro import Carro  # Física antiga

def testar_IA_fisica_antiga():
    """Teste da IA com física antiga"""
    print("=== TESTE IA MELHORADA COM FÍSICA ANTIGA ===")
    
    # InicIAlizar pygame
    pygame.init()
    pygame.display.set_mode((800, 600))
    
    # CrIAr checkpoints em formato de quadrado
    checkpoints = [
        (400, 300),  # Centro
        (500, 300),  # Direita
        (500, 400),  # Baixo-direita
        (400, 400),  # Baixo
        (300, 400),  # Baixo-esquerda
        (300, 300),  # Esquerda
        (300, 200),  # Cima-esquerda
        (400, 200),  # Cima
        (500, 200),  # Cima-direita
    ]
    
    # CrIAr IA
    IA = IAMelhorada(checkpoints, nome="IA-Física-Antiga")
    IA.debug = True
    
    # CrIAr carro com física antiga
    carro = Carro(400, 300, "Car3", (0, 0, 0, 0), nome="Carro-Física-Antiga")
    carro.angulo = 0  # Apontando para -X (esquerda)
    
    print(f"✓ IA crIAda: {IA.nome}")
    print(f"✓ Carro crIAdo: {carro.nome} (física antiga)")
    print(f"✓ Ângulo inicIAl: {carro.angulo}°")
    
    dt = 1.0 / 60.0
    
    # Testar cada direção
    for i, (cx, cy) in enumerate(checkpoints[1:], 1):
        print(f"\n--- TESTE {i}: Checkpoint ({cx}, {cy}) ---")
        
        # Posicionar carro no centro
        carro.x = 400
        carro.y = 300
        carro.angulo = 0
        carro.vx = 0
        carro.vy = 0
        
        # Atualizar alvo da IA
        IA.checkpoint_atual = i - 1
        IA.alvo_x = cx
        IA.alvo_y = cy
        
        # Calcular direção esperada
        dx = cx - carro.x
        dy = cy - carro.y
        angulo_esperado = math.degrees(math.atan2(dy, -dx))
        print(f"Ângulo esperado para ({cx}, {cy}): {angulo_esperado:.1f}°")
        
        # Simular alguns frames
        for frame in range(10):
            # Controlar carro com IA (usando método da física antiga)
            IA.controlar(carro, None, lambda x, y: True, dt)
            
            # Calcular ângulo atual
            angulo_atual = carro.angulo
            diff_angulo = (angulo_esperado - angulo_atual + 180) % 360 - 180
            
            print(f"  Frame {frame}: Pos=({carro.x:.1f}, {carro.y:.1f}), "
                  f"Ângulo={angulo_atual:.1f}°, Diff={diff_angulo:.1f}°")
            
            # Verificar se está virando na direção correta
            if abs(diff_angulo) < 30:  # Dentro de 30 graus
                print(f"  ✅ Virando corretamente!")
                break
            elif frame == 9:
                print(f"  ❌ Não virou corretamente")
    
    print("\n✅ Teste com física antiga concluído!")
    pygame.quit()

if __name__ == "__main__":
    testar_IA_fisica_antiga()
