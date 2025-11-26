#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo de teste para a Akira (Mestra do Fluxo)
Execute este arquivo para testar o sistema da Akira diretamente
"""

import pygame
import sys
import os

# Adicionar o diretório src ao path (ajustado para estar em tools/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import LARGURA, ALTURA, FPS
from core.akira import akira

def main():
    """Função principal de teste"""
    pygame.init()
    
    # Criar tela
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Teste - Akira (Mestra do Fluxo)")
    relogio = pygame.time.Clock()
    
    # Garantir que os sprites estão carregados
    if not akira.sprites_carregados:
        print("Carregando sprites...")
        akira.carregar_sprites()
    
    print(f"Sprites carregados:")
    print(f"  neutro: {akira.sprite_neutro is not None}")
    print(f"  ensinando: {akira.sprite_ensinando is not None}")
    print(f"  focada: {akira.sprite_focada is not None}")
    print(f"  respeito: {akira.sprite_respeito is not None}")
    print(f"  decepcionada: {akira.sprite_decepcionada is not None}")
    print(f"  fundo pré-corrida: {akira.sprite_fundo_pre is not None}")
    print(f"  fundo fim de corrida: {akira.sprite_fundo_fim is not None}")
    
    print(f"\nEstado atual:")
    print(f"  Nome revelado: {akira.nome_revelado}")
    print(f"  Diálogos pré-corrida mostrados: {akira.dialogos_pre_corrida_mostrados}")
    print(f"  Ativo: {akira.ativo}")
    
    # Simular diferentes cenários
    print("\n=== CENÁRIOS DE TESTE ===")
    print("PRÉ-CORRIDA:")
    print("  1-9: Testar diálogo pré-corrida da pista 1-9")
    print("  R: Resetar diálogos pré-corrida mostrados")
    print("\nPÓS-CORRIDA:")
    print("  A: Boa colocação + Carro limpo (Vitória perfeita)")
    print("  B: Boa colocação + Carro destruído (Vitória bárbara)")
    print("  C: Má colocação + Carro limpo (Piloto cauteloso)")
    print("  D: Má colocação + Carro destruído (Desastre completo)")
    print("==================\n")
    
    rodando = True
    dt = 0
    
    print("\n=== CONTROLES ===")
    print("ENTER/ESPAÇO: Avançar diálogo")
    print("ESC: Fechar diálogo")
    print("CLIQUE DO MOUSE: Avançar diálogo")
    print("1-9: Testar diálogo pré-corrida da pista correspondente")
    print("R: Resetar diálogos pré-corrida")
    print("A-D: Testar diferentes cenários pós-corrida")
    print("==================\n")
    
    while rodando:
        dt = relogio.tick(FPS) / 1000.0
        
        eventos = list(pygame.event.get())
        
        for ev in eventos:
            if ev.type == pygame.QUIT:
                rodando = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1:
                    print("\n=== TESTANDO PRÉ-CORRIDA: PISTA 1 ===")
                    akira.dialogos_pre_corrida_mostrados = {}
                    akira.ativo = False
                    akira.verificar_aparecer_pre_corrida(1)
                elif ev.key == pygame.K_2:
                    print("\n=== TESTANDO PRÉ-CORRIDA: PISTA 2 ===")
                    akira.dialogos_pre_corrida_mostrados = {}
                    akira.ativo = False
                    akira.verificar_aparecer_pre_corrida(2)
                elif ev.key == pygame.K_3:
                    print("\n=== TESTANDO PRÉ-CORRIDA: PISTA 3 ===")
                    akira.dialogos_pre_corrida_mostrados = {}
                    akira.ativo = False
                    akira.verificar_aparecer_pre_corrida(3)
                elif ev.key == pygame.K_4:
                    print("\n=== TESTANDO PRÉ-CORRIDA: PISTA 4 ===")
                    akira.dialogos_pre_corrida_mostrados = {}
                    akira.ativo = False
                    akira.verificar_aparecer_pre_corrida(4)
                elif ev.key == pygame.K_5:
                    print("\n=== TESTANDO PRÉ-CORRIDA: PISTA 5 ===")
                    akira.dialogos_pre_corrida_mostrados = {}
                    akira.ativo = False
                    akira.verificar_aparecer_pre_corrida(5)
                elif ev.key == pygame.K_6:
                    print("\n=== TESTANDO PRÉ-CORRIDA: PISTA 6 ===")
                    akira.dialogos_pre_corrida_mostrados = {}
                    akira.ativo = False
                    akira.verificar_aparecer_pre_corrida(6)
                elif ev.key == pygame.K_7:
                    print("\n=== TESTANDO PRÉ-CORRIDA: PISTA 7 ===")
                    akira.dialogos_pre_corrida_mostrados = {}
                    akira.ativo = False
                    akira.verificar_aparecer_pre_corrida(7)
                elif ev.key == pygame.K_8:
                    print("\n=== TESTANDO PRÉ-CORRIDA: PISTA 8 ===")
                    akira.dialogos_pre_corrida_mostrados = {}
                    akira.ativo = False
                    akira.verificar_aparecer_pre_corrida(8)
                elif ev.key == pygame.K_9:
                    print("\n=== TESTANDO PRÉ-CORRIDA: PISTA 9 ===")
                    akira.dialogos_pre_corrida_mostrados = {}
                    akira.ativo = False
                    akira.verificar_aparecer_pre_corrida(9)
                elif ev.key == pygame.K_r:
                    print("\n=== RESETANDO DIÁLOGOS PRÉ-CORRIDA ===")
                    akira.dialogos_pre_corrida_mostrados = {}
                    akira.salvar_estado()
                    print("Diálogos pré-corrida resetados!")
                elif ev.key == pygame.K_a:
                    print("\n=== TESTANDO PÓS-CORRIDA: CENÁRIO A (Boa colocação + Carro limpo) ===")
                    akira.ativo = False
                    akira.verificar_aparecer_pos_corrida(posicao=1, colisoes=0, venceu=True)
                elif ev.key == pygame.K_b:
                    print("\n=== TESTANDO PÓS-CORRIDA: CENÁRIO B (Boa colocação + Carro destruído) ===")
                    akira.ativo = False
                    akira.verificar_aparecer_pos_corrida(posicao=1, colisoes=8, venceu=True)
                elif ev.key == pygame.K_c:
                    print("\n=== TESTANDO PÓS-CORRIDA: CENÁRIO C (Má colocação + Carro limpo) ===")
                    akira.ativo = False
                    akira.verificar_aparecer_pos_corrida(posicao=4, colisoes=1, venceu=False)
                elif ev.key == pygame.K_d:
                    print("\n=== TESTANDO PÓS-CORRIDA: CENÁRIO D (Má colocação + Carro destruído) ===")
                    akira.ativo = False
                    akira.verificar_aparecer_pos_corrida(posicao=5, colisoes=10, venceu=False)
        
        # Atualizar Akira
        if akira.ativo:
            akira.atualizar(dt)
        
        # Processar eventos da Akira
        if akira.ativo:
            akira.processar_eventos(eventos)
        
        # Desenhar fundo
        tela.fill((20, 30, 40))
        
        # Desenhar informações de debug (só quando Akira não está ativa)
        if not akira.ativo:
            fonte_debug = pygame.font.SysFont("consolas", 24, bold=True)
            texto_info = fonte_debug.render("TESTE DA AKIRA (MESTRA DO FLUXO)", True, (200, 100, 150))
            tela.blit(texto_info, (20, 20))
            
            fonte_info = pygame.font.SysFont("consolas", 18, bold=True)
            
            nome_texto = f"Nome revelado: {akira.nome_revelado}"
            texto_nome = fonte_info.render(nome_texto, True, (255, 255, 255))
            tela.blit(texto_nome, (20, 60))
            
            dialogos_texto = f"Diálogos pré-corrida mostrados: {len(akira.dialogos_pre_corrida_mostrados)} pistas"
            texto_dialogos = fonte_info.render(dialogos_texto, True, (200, 200, 255))
            tela.blit(texto_dialogos, (20, 90))
            
            if akira.ultima_corrida['posicao'] is not None:
                corrida_texto = f"Última corrida: Posição {akira.ultima_corrida['posicao']}, {akira.ultima_corrida['colisoes']} colisões, Venceu: {akira.ultima_corrida['venceu']}"
                texto_corrida = fonte_info.render(corrida_texto, True, (200, 255, 200))
                tela.blit(texto_corrida, (20, 120))
            
            if akira.modo_dialogo:
                modo_texto = f"Modo diálogo: {akira.modo_dialogo.upper()}"
                texto_modo = fonte_info.render(modo_texto, True, (255, 200, 0))
                tela.blit(texto_modo, (20, 150))
            
            instrucoes_pre = [
                "PRÉ-CORRIDA:",
                "1-9: Testar diálogo pré-corrida da pista correspondente",
                "R: Resetar diálogos pré-corrida"
            ]
            y_instrucoes = 200
            for instrucao in instrucoes_pre:
                texto_inst = fonte_info.render(instrucao, True, (150, 200, 255))
                tela.blit(texto_inst, (20, y_instrucoes))
                y_instrucoes += 30
            
            instrucoes_pos = [
                "PÓS-CORRIDA:",
                "A: Boa colocação + Carro limpo",
                "B: Boa colocação + Carro destruído",
                "C: Má colocação + Carro limpo",
                "D: Má colocação + Carro destruído"
            ]
            y_instrucoes = 290
            for instrucao in instrucoes_pos:
                texto_inst = fonte_info.render(instrucao, True, (255, 200, 150))
                tela.blit(texto_inst, (20, y_instrucoes))
                y_instrucoes += 30
        
        # Desenhar Akira
        if akira.ativo:
            akira.desenhar_dialogo(tela, dt)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()



