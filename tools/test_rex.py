#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo de teste para o Rex (Rival)
Execute este arquivo para testar o sistema do Rex diretamente
"""

import pygame
import sys
import os

# Adicionar o diretório src ao path (ajustado para estar em tools/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import LARGURA, ALTURA, FPS
from core.rex import rex
from core.progresso import gerenciador_progresso
from core.estatisticas import gerenciador_estatisticas

def main():
    """Função principal de teste"""
    pygame.init()
    
    # Criar tela
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Teste - Rex (Rival)")
    relogio = pygame.time.Clock()
    
    # Garantir que os sprites estão carregados
    if not rex.sprites_carregados:
        print("Carregando sprites...")
        rex.carregar_sprites()
    
    print(f"Sprites carregados:")
    print(f"  competitive (competitivo.png): {rex.sprite_competitive is not None}")
    print(f"  mocking (zombando.png): {rex.sprite_mocking is not None}")
    print(f"  angry (ameaça.png): {rex.sprite_angry is not None}")
    print(f"  challenging (campeao_1.png): {rex.sprite_challenging is not None}")
    print(f"  scheming (desdem.png): {rex.sprite_scheming is not None}")
    print(f"  fundo (pista_corrida.png): {rex.sprite_fundo is not None}")
    
    print(f"\nEstado atual:")
    print(f"  Primeira aparição mostrada: {rex.primeira_aparicao_mostrada}")
    print(f"  Ativo: {rex.ativo}")
    
    # Obter carro atual
    carro_p1_atual = gerenciador_progresso.obter_carro_atual(1)
    if carro_p1_atual is None:
        carro_p1_atual = 0
    
    from main import CARROS_DISPONIVEIS
    if 0 <= carro_p1_atual < len(CARROS_DISPONIVEIS):
        prefixo_cor = CARROS_DISPONIVEIS[carro_p1_atual]["prefixo_cor"]
        nome_carro = CARROS_DISPONIVEIS[carro_p1_atual]["nome"]
    else:
        prefixo_cor = "Car1"
        nome_carro = "Nissan 350Z"
    
    upgrades = gerenciador_progresso.obter_todos_upgrades(prefixo_cor)
    print(f"\nCarro atual: {nome_carro} ({prefixo_cor})")
    print(f"Upgrades: {upgrades}")
    
    # Verificar se é carro lixo ou decente
    carro_lixo = rex._verificar_carro_lixo(prefixo_cor)
    print(f"Tipo de carro: {'LIXO' if carro_lixo else 'DECENTE'}")
    
    # Simular primeira corrida completada
    print("\nSimulando primeira corrida completada...")
    gerenciador_estatisticas.estatisticas_gerais["corridas_completas"] = 1
    rex.primeira_aparicao_mostrada = False  # Resetar para testar
    
    # Forçar aparecimento do Rex
    print("Forçando aparecimento do Rex...")
    rex.verificar_aparecer()
    
    print(f"\nRoteiro selecionado: {rex.roteiro_tipo}")
    print(f"Fase do diálogo: {rex.fase_dialogo}")
    print(f"Parte do diálogo: {rex.parte_dialogo}")
    
    rodando = True
    dt = 0
    
    print("\n=== CONTROLES ===")
    print("ENTER/ESPAÇO: Avançar diálogo")
    print("ESC: Fechar diálogo")
    print("CLIQUE DO MOUSE: Avançar diálogo")
    print("1: Testar roteiro CARRO LIXO")
    print("2: Testar roteiro CARRO DECENTE")
    print("3: Resetar e aparecer novamente")
    print("==================\n")
    
    while rodando:
        dt = relogio.tick(FPS) / 1000.0
        
        eventos = list(pygame.event.get())
        
        for ev in eventos:
            if ev.type == pygame.QUIT:
                rodando = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1:
                    print("\n=== FORÇANDO ROTEIRO: CARRO LIXO ===")
                    # Resetar upgrades para simular carro lixo
                    gerenciador_progresso.upgrades[prefixo_cor] = {
                        'motor': 0,
                        'filtro_ar': 0,
                        'ecu': 0,
                        'transmissao': 0,
                        'rodas': 0,
                        'suspensao': 0,
                        'nitro': 0
                    }
                    gerenciador_progresso.salvar()
                    rex.primeira_aparicao_mostrada = False
                    rex.ativo = False
                    rex.verificar_aparecer()
                    print(f"Roteiro: {rex.roteiro_tipo}")
                elif ev.key == pygame.K_2:
                    print("\n=== FORÇANDO ROTEIRO: CARRO DECENTE ===")
                    # Aumentar upgrades para simular carro decente
                    gerenciador_progresso.upgrades[prefixo_cor] = {
                        'motor': 4,
                        'filtro_ar': 3,
                        'ecu': 4,
                        'transmissao': 3,
                        'rodas': 4,
                        'suspensao': 3,
                        'nitro': 4
                    }
                    gerenciador_progresso.salvar()
                    rex.primeira_aparicao_mostrada = False
                    rex.ativo = False
                    rex.verificar_aparecer()
                    print(f"Roteiro: {rex.roteiro_tipo}")
                elif ev.key == pygame.K_3:
                    print("\n=== RESETANDO ===")
                    rex.primeira_aparicao_mostrada = False
                    rex.ativo = False
                    gerenciador_estatisticas.estatisticas_gerais["corridas_completas"] = 1
                    rex.verificar_aparecer()
                    print(f"Roteiro: {rex.roteiro_tipo}")
        
        # Atualizar Rex
        if rex.ativo:
            rex.atualizar(dt)
        
        # Processar eventos do Rex
        if rex.ativo:
            rex.processar_eventos(eventos)
        
        # Desenhar fundo
        tela.fill((20, 30, 40))
        
        # Desenhar informações de debug (só quando Rex não está ativo)
        if not rex.ativo:
            fonte_debug = pygame.font.SysFont("consolas", 24, bold=True)
            texto_info = fonte_debug.render("TESTE DO REX (RIVAL)", True, (255, 200, 0))
            tela.blit(texto_info, (20, 20))
            
            fonte_info = pygame.font.SysFont("consolas", 18, bold=True)
            
            estado_texto = f"Primeira aparição mostrada: {rex.primeira_aparicao_mostrada}"
            texto_estado = fonte_info.render(estado_texto, True, (255, 255, 255))
            tela.blit(texto_estado, (20, 60))
            
            corridas_texto = f"Corridas completas: {gerenciador_estatisticas.estatisticas_gerais.get('corridas_completas', 0)}"
            texto_corridas = fonte_info.render(corridas_texto, True, (200, 200, 255))
            tela.blit(texto_corridas, (20, 90))
            
            carro_texto = f"Carro: {nome_carro} ({prefixo_cor})"
            texto_carro = fonte_info.render(carro_texto, True, (200, 255, 200))
            tela.blit(texto_carro, (20, 120))
            
            upgrades_texto = f"Upgrades: {upgrades}"
            texto_upgrades = fonte_info.render(upgrades_texto, True, (255, 200, 200))
            tela.blit(texto_upgrades, (20, 150))
            
            tipo_carro = "LIXO" if rex._verificar_carro_lixo(prefixo_cor) else "DECENTE"
            tipo_texto = f"Tipo de carro: {tipo_carro}"
            texto_tipo = fonte_info.render(tipo_texto, True, (255, 200, 0) if tipo_carro == "LIXO" else (0, 255, 100))
            tela.blit(texto_tipo, (20, 180))
            
            if rex.roteiro_tipo:
                roteiro_texto = f"Roteiro: {rex.roteiro_tipo.upper()}"
                texto_roteiro = fonte_info.render(roteiro_texto, True, (255, 150, 0))
                tela.blit(texto_roteiro, (20, 210))
            
            instrucoes = [
                "1: Testar roteiro CARRO LIXO",
                "2: Testar roteiro CARRO DECENTE",
                "3: Resetar e aparecer novamente"
            ]
            y_instrucoes = 250
            for instrucao in instrucoes:
                texto_inst = fonte_info.render(instrucao, True, (150, 150, 150))
                tela.blit(texto_inst, (20, y_instrucoes))
                y_instrucoes += 30
        
        # Desenhar Rex
        if rex.ativo:
            rex.desenhar_dialogo(tela, dt)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

