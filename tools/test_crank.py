#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo de teste para o Crank (Mecânico)
Execute este arquivo para testar o sistema do Crank diretamente
"""

import pygame
import sys
import os

# Adicionar o diretório src ao path (ajustado para estar em tools/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import LARGURA, ALTURA, FPS
from core.crank import crank
from core.progresso import gerenciador_progresso

def main():
    """Função principal de teste"""
    pygame.init()
    
    # Criar tela
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Teste - Crank (Mecânico)")
    relogio = pygame.time.Clock()
    
    # Forçar aparecimento do Crank
    print("Forçando aparecimento do Crank...")
    
    # Garantir que os sprites estão carregados
    if not crank.sprites_carregados:
        print("Carregando sprites...")
        crank.carregar_sprites()
    
    print(f"Sprites carregados:")
    print(f"  normal: {crank.sprite_normal is not None}")
    print(f"  alegre: {crank.sprite_alegre is not None}")
    print(f"  bravo: {crank.sprite_bravo is not None}")
    print(f"  estressado: {crank.sprite_estressado is not None}")
    print(f"  duvida: {crank.sprite_duvida is not None}")
    print(f"  surpreso: {crank.sprite_surpreso is not None}")
    print(f"  triste: {crank.sprite_triste is not None}")
    print(f"  convencido: {crank.sprite_convencido is not None}")
    print(f"  incredulo: {crank.sprite_incredulo is not None}")
    
    print(f"\nHumor atual: {crank.humor_atual}")
    print(f"Saúde do carro: {crank.saude_carro * 100:.1f}%")
    
    # Simular diferentes cenários de corrida
    print("\n=== CENÁRIOS DE TESTE ===")
    print("1: Venceu sem colisões (muito feliz)")
    print("2: Venceu com poucas colisões (feliz)")
    print("3: Perdeu sem colisões (normal)")
    print("4: Perdeu com algumas colisões (bravo)")
    print("5: Muitas colisões (muito bravo)")
    print("6: Dano crítico (saúde < 20%)")
    print("7: Tutorial inicial (primeira vez na oficina)")
    print("8: Tutorial de upgrades (primeira vez na tela de upgrades)")
    print("9: Diálogo raro sobre compra alien - Golpe")
    print("0: Diálogo raro sobre compra alien - Melhoria boa")
    print("==================\n")
    
    # Simular primeira corrida
    print("Simulando corrida: Venceu sem colisões")
    crank.registrar_corrida(posicao=1, colisoes=0, venceu=True)
    crank.verificar_aparecer_pos_corrida()
    
    rodando = True
    dt = 0
    
    print("\n=== CONTROLES ===")
    print("ENTER/ESPAÇO: Avançar/Confirmar")
    print("ESC: Fechar diálogo")
    print("SETAS CIMA/BAIXO ou W/S: Navegar opções de resposta")
    print("1-6: Simular diferentes cenários de corrida")
    print("7: Tutorial inicial")
    print("8: Tutorial de upgrades")
    print("9: Diálogo raro - Golpe alien")
    print("0: Diálogo raro - Melhoria alien")
    print("\n=== SISTEMA DE RESPOSTAS ===")
    print("Quando o Crank está bravo, você pode escolher uma resposta:")
    print("  Opção 1 (Desculpa): Melhora o humor → Preços normais")
    print("  Opção 2 (Relativiza): Mantém ou piora um pouco → Preços +25%")
    print("  Opção 3 (Desafio): Piora muito → Preços +50%")
    print("==================\n")
    
    while rodando:
        dt = relogio.tick(FPS) / 1000.0
        
        eventos = list(pygame.event.get())
        
        for ev in eventos:
            if ev.type == pygame.QUIT:
                rodando = False
            elif ev.type == pygame.KEYDOWN:
                # Não processar eventos de fechar se o Crank precisa de resposta
                # O próprio Crank vai processar esses eventos
                if ev.key == pygame.K_1:
                    print("\nSimulando: Venceu sem colisões")
                    crank.registrar_corrida(posicao=1, colisoes=0, venceu=True)
                    crank.verificar_aparecer_pos_corrida()
                elif ev.key == pygame.K_2:
                    print("\nSimulando: Venceu com 2 colisões")
                    crank.registrar_corrida(posicao=1, colisoes=2, venceu=True)
                    crank.verificar_aparecer_pos_corrida()
                elif ev.key == pygame.K_3:
                    print("\nSimulando: Perdeu sem colisões")
                    crank.registrar_corrida(posicao=2, colisoes=0, venceu=False)
                    crank.verificar_aparecer_pos_corrida()
                elif ev.key == pygame.K_4:
                    print("\nSimulando: Perdeu com 4 colisões")
                    crank.registrar_corrida(posicao=3, colisoes=4, venceu=False)
                    crank.verificar_aparecer_pos_corrida()
                elif ev.key == pygame.K_5:
                    print("\nSimulando: Muitas colisões (7)")
                    crank.registrar_corrida(posicao=4, colisoes=7, venceu=False)
                    crank.verificar_aparecer_pos_corrida()
                elif ev.key == pygame.K_6:
                    print("\nSimulando: Dano crítico")
                    crank.saude_carro = 0.15  # 15% de saúde
                    crank.verificar_aparecer_dano_critico()
                elif ev.key == pygame.K_7:
                    print("\nSimulando: Tutorial inicial")
                    crank.tutorial_mostrado = False
                    crank.mostrar_tutorial()
                elif ev.key == pygame.K_8:
                    print("\nSimulando: Tutorial de upgrades")
                    crank.tutorial_upgrades_mostrado = False
                    crank.mostrar_tutorial_upgrades()
                elif ev.key == pygame.K_9:
                    print("\nSimulando: Diálogo raro - Golpe do mercador alien")
                    from core.progresso import gerenciador_progresso
                    gerenciador_progresso.registrar_compra_alien('golpe', 1, 'motor')
                    crank.verificar_aparecer_dialogo_alien()
                elif ev.key == pygame.K_0:
                    print("\nSimulando: Diálogo raro - Melhoria boa do mercador alien")
                    from core.progresso import gerenciador_progresso
                    gerenciador_progresso.registrar_compra_alien('upgrade_especial', 1, 'motor')
                    crank.verificar_aparecer_dialogo_alien()
        
        # Processar eventos do Crank
        if crank.ativo:
            resultado = crank.processar_eventos(eventos)
            if resultado == "fechado":
                print("Diálogo fechado!")
        
        # Desenhar fundo
        tela.fill((30, 50, 70))
        
        # Desenhar informações de debug (só quando Crank não está ativo)
        if not crank.ativo:
            fonte_debug = pygame.font.SysFont("consolas", 24, bold=True)
            texto_info = fonte_debug.render("TESTE DO CRANK (MECÂNICO)", True, (255, 200, 0))
            tela.blit(texto_info, (20, 20))
            
            fonte_info = pygame.font.SysFont("consolas", 18, bold=True)
            
            humor_texto = f"Humor: {crank.humor_atual} (Multiplicador: {crank.MULTIPLICADORES_PRECO.get(crank.humor_atual, 1.0):.2f}x)"
            texto_humor = fonte_info.render(humor_texto, True, (255, 215, 0))
            tela.blit(texto_humor, (20, 60))
            
            saude_texto = f"Saúde do carro: {crank.saude_carro * 100:.1f}%"
            texto_saude = fonte_info.render(saude_texto, True, (0, 255, 100))
            tela.blit(texto_saude, (20, 90))
            
            if crank.ultima_corrida['posicao'] is not None:
                corrida_texto = f"Última corrida: Posição {crank.ultima_corrida['posicao']}, {crank.ultima_corrida['colisoes']} colisões, Venceu: {crank.ultima_corrida['venceu']}"
                texto_corrida = fonte_info.render(corrida_texto, True, (200, 200, 255))
                tela.blit(texto_corrida, (20, 120))
            
            instrucoes = [
                "1-6: Simular diferentes cenários de corrida",
                "7: Tutorial inicial",
                "8: Tutorial de upgrades",
                "9: Diálogo raro - Golpe alien",
                "0: Diálogo raro - Melhoria alien"
            ]
            y_instrucoes = 160
            for instrucao in instrucoes:
                texto_inst = fonte_info.render(instrucao, True, (150, 150, 150))
                tela.blit(texto_inst, (20, y_instrucoes))
                y_instrucoes += 30
        
        # Desenhar Crank
        if crank.ativo:
            crank.desenhar_dialogo(tela, dt)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

