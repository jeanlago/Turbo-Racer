#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo de teste para o Glub (Comprador de Peças Antigas)
Execute este arquivo para testar o sistema do Glub diretamente
"""

import pygame
import sys
import os
import random

# Adicionar o diretório src ao path (ajustado para estar em tools/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import LARGURA, ALTURA, FPS
from core.glub import glub
from core.progresso import gerenciador_progresso
from core.menu import render_text

def main():
    """Função principal de teste"""
    pygame.init()
    
    # Inicializar mixer de áudio para os sons
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        print("✓ Mixer de áudio inicializado")
    except:
        try:
            pygame.mixer.init()
            print("✓ Mixer de áudio inicializado (fallback)")
        except Exception as e:
            print(f"✗ Erro ao inicializar mixer: {e}")
    
    # Criar tela
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Teste - Glub (Comprador de Peças Antigas)")
    relogio = pygame.time.Clock()
    
    # Forçar aparecimento do Glub
    print("Forçando aparecimento do Glub...")
    
    # Garantir que os sprites estão carregados
    if not glub.sprites_carregados:
        print("Carregando sprites...")
        glub.carregar_sprites()
    
    print(f"Sprites carregados:")
    print(f"  encontro: {glub.sprite_encontro is not None}")
    print(f"  curioso: {glub.sprite_curioso is not None}")
    print(f"  oferta: {glub.sprite_oferta is not None}")
    print(f"  comprou: {glub.sprite_comprou is not None}")
    print(f"  triste: {glub.sprite_triste is not None}")
    print(f"  dormindo: {glub.sprite_dormindo is not None}")
    print(f"  chorando: {glub.sprite_chorando is not None}")
    print(f"  compro_feliz: {glub.sprite_compro_feliz is not None}")
    print(f"  sem_entender: {glub.sprite_sem_entender is not None}")
    
    print(f"\nSons carregados:")
    print(f"  som_compra: {glub.som_compra is not None}")
    
    # Simular uma compra de upgrade para gerar oferta
    tipo_upgrade_teste = "motor"
    nivel_antigo_teste = 2  # Simular que tinha nível 2 e comprou nível 3
    
    glub.gerar_oferta(tipo_upgrade_teste, nivel_antigo_teste)
    glub.ativo = True
    
    print(f"Oferta gerada: {glub.oferta_atual}")
    print(f"Tipo: {glub.oferta_atual['tipo_upgrade']}")
    print(f"Nível antigo: {glub.oferta_atual['nivel_antigo']}")
    print(f"Preço oferecido: ${glub.oferta_atual['preco']:,}")
    
    # Adicionar dinheiro para teste
    gerenciador_progresso.adicionar_dinheiro(50000)
    print(f"Dinheiro disponível: ${gerenciador_progresso.dinheiro:,}")
    
    rodando = True
    dt = 0
    
    print("\n=== CONTROLES ===")
    print("SETAS ESQUERDA/DIREITA: Navegar entre opções")
    print("ENTER/ESPAÇO: Confirmar seleção")
    print("ESC: Fechar/Recusar")
    print("Q: Forçar nova oferta")
    print("==================\n")
    
    while rodando:
        dt = relogio.tick(FPS) / 1000.0
        
        eventos = list(pygame.event.get())
        
        for ev in eventos:
            if ev.type == pygame.QUIT:
                rodando = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_q:
                    # Forçar nova oferta
                    print("\nGerando nova oferta...")
                    # Simular diferentes tipos de upgrade
                    tipos = ["motor", "filtro_ar", "ecu", "transmissao", "rodas", "suspensao", "nitro"]
                    tipo_upgrade_teste = random.choice(tipos)
                    nivel_antigo_teste = random.randint(1, 4)
                    
                    glub.gerar_oferta(tipo_upgrade_teste, nivel_antigo_teste)
                    glub.ativo = True
                    glub.fase_dialogo = "apresentacao"  # Resetar para fase inicial
                    print(f"Oferta gerada: {glub.oferta_atual}")
                    print(f"Tipo: {glub.oferta_atual['tipo_upgrade']}")
                    print(f"Nível antigo: {glub.oferta_atual['nivel_antigo']}")
                    print(f"Preço oferecido: ${glub.oferta_atual['preco']:,}")
                    print(f"Dinheiro disponível: ${gerenciador_progresso.dinheiro:,}\n")
        
        # Processar eventos do Glub
        if glub.ativo:
            resultado = glub.processar_eventos(eventos, prefixo_cor="Car1")
            if resultado:
                print(f"Resultado: {resultado}")
                if resultado == "vendido":
                    print("Peça vendida com sucesso!")
                    print(f"Dinheiro atual: ${gerenciador_progresso.dinheiro:,}")
                elif resultado == "recusado":
                    print("Oferta recusada!")
                elif resultado == "fechado":
                    print("Diálogo fechado!")
                    # Reativar para continuar testando
                    tipo_upgrade_teste = random.choice(["motor", "filtro_ar", "ecu", "transmissao", "rodas", "suspensao", "nitro"])
                    nivel_antigo_teste = random.randint(1, 4)
                    glub.gerar_oferta(tipo_upgrade_teste, nivel_antigo_teste)
                    glub.ativo = True
                    glub.fase_dialogo = "apresentacao"  # Resetar para fase inicial
        
        # Desenhar fundo (simulando jogo)
        tela.fill((30, 50, 70))  # Cor de fundo mais interessante
        
        # Desenhar informações de debug (só quando Glub não está ativo)
        if not glub.ativo:
            fonte_debug = pygame.font.SysFont("consolas", 24, bold=True)
            texto_info = fonte_debug.render("TESTE DO GLUB (COMPRADOR)", True, (255, 200, 0))
            tela.blit(texto_info, (20, 20))
            
            fonte_info = pygame.font.SysFont("consolas", 18, bold=True)
            
            dinheiro_texto = f"Dinheiro: ${gerenciador_progresso.dinheiro:,}"
            texto_dinheiro = fonte_info.render(dinheiro_texto, True, (255, 215, 0))
            tela.blit(texto_dinheiro, (20, 60))
            
            if glub.oferta_atual:
                oferta_texto = f"Oferta: {glub.oferta_atual['tipo_upgrade']} Nível {glub.oferta_atual['nivel_antigo']} - ${glub.oferta_atual['preco']:,}"
                texto_oferta = fonte_info.render(oferta_texto, True, (200, 200, 255))
                tela.blit(texto_oferta, (20, 90))
            
            fase_texto = f"Fase: {glub.fase_dialogo}"
            texto_fase = fonte_info.render(fase_texto, True, (255, 255, 255))
            tela.blit(texto_fase, (20, 120))
            
            instrucoes = [
                "Q: Forçar nova oferta",
                "SETAS: Navegar opções",
                "ENTER: Confirmar",
                "ESC: Fechar/Recusar"
            ]
            y_instrucoes = 160
            for instrucao in instrucoes:
                texto_inst = fonte_info.render(instrucao, True, (150, 150, 150))
                tela.blit(texto_inst, (20, y_instrucoes))
                y_instrucoes += 30
        
        # Desenhar Glub (com overlay escuro e diálogo estilo visual novel)
        if glub.ativo:
            glub.desenhar_dialogo(tela, dt)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

