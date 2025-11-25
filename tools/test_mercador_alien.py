#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo de teste para o Mercador Alien
Execute este arquivo para testar o sistema do mercador alien diretamente
"""

import pygame
import sys
import os

# Adicionar o diretório src ao path (ajustado para estar em tools/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import LARGURA, ALTURA, FPS
from core.mercador_alien import mercador_alien
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
    pygame.display.set_caption("Teste - Mercador Alien (Slick)")
    relogio = pygame.time.Clock()
    
    # Forçar aparecimento do mercador
    print("Forçando aparecimento do mercador alien...")
    
    # Garantir que os sprites estão carregados
    if not mercador_alien.sprites_carregados:
        print("Carregando sprites...")
        mercador_alien.carregar_sprites()
    
    print(f"Sprites carregados:")
    print(f"  cumprimento: {mercador_alien.sprite_cumprimento is not None}")
    print(f"  oferta: {mercador_alien.sprite_oferta is not None}")
    print(f"  golpe: {mercador_alien.sprite_golpe is not None}")
    print(f"  vendeu: {mercador_alien.sprite_vendeu is not None}")
    
    print(f"\nSons carregados:")
    print(f"  som_compra: {mercador_alien.som_compra is not None}")
    print(f"  som_fail: {mercador_alien.som_fail is not None}")
    
    mercador_alien.gerar_oferta()
    mercador_alien.ativo = True
    mercador_alien.contexto_atual = "corrida"  # Simular contexto de corrida
    if mercador_alien.sprite_cumprimento:
        mercador_alien.sprite_atual = mercador_alien.sprite_cumprimento
    else:
        print("ERRO: Sprite cumprimento não carregado!")
    mercador_alien.texto_atual = mercador_alien.obter_texto_cumprimento()
    
    print(f"Oferta gerada: {mercador_alien.oferta_atual}")
    print(f"Tipo: {mercador_alien.oferta_atual['tipo']}")
    print(f"Preço: ${mercador_alien.oferta_atual['preco']:,}")
    print(f"Upgrade: {mercador_alien.oferta_atual['tipo_upgrade']}")
    
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
                    mercador_alien.gerar_oferta()
                    mercador_alien.ativo = True
                    mercador_alien.contexto_atual = "corrida"  # Simular contexto de corrida
                    if mercador_alien.sprite_cumprimento:
                        mercador_alien.sprite_atual = mercador_alien.sprite_cumprimento
                    mercador_alien.texto_atual = mercador_alien.obter_texto_cumprimento()
                    mercador_alien.fase_dialogo = "apresentacao"  # Resetar para fase inicial
                    print(f"Oferta gerada: {mercador_alien.oferta_atual}")
                    print(f"Tipo: {mercador_alien.oferta_atual['tipo']}")
                    print(f"Preço: ${mercador_alien.oferta_atual['preco']:,}")
                    print(f"Upgrade: {mercador_alien.oferta_atual['tipo_upgrade']}")
                    print(f"Dinheiro disponível: ${gerenciador_progresso.dinheiro:,}\n")
        
        # Processar eventos do mercador
        if mercador_alien.ativo:
            resultado = mercador_alien.processar_eventos(eventos, prefixo_cor="Car1")
            if resultado:
                print(f"Resultado: {resultado}")
                if resultado == "comprado":
                    print("Compra realizada com sucesso!")
                    print(f"Dinheiro restante: ${gerenciador_progresso.dinheiro:,}")
                    # Mostrar upgrades do Car1
                    upgrades = gerenciador_progresso.obter_todos_upgrades("Car1")
                    print(f"Upgrades do Car1: {upgrades}")
                elif resultado == "recusado":
                    print("Oferta recusada!")
                elif resultado == "fechado":
                    print("Diálogo fechado!")
                    # Reativar para continuar testando
                    mercador_alien.gerar_oferta()
                    mercador_alien.ativo = True
                    mercador_alien.contexto_atual = "corrida"  # Simular contexto de corrida
                    if mercador_alien.sprite_cumprimento:
                        mercador_alien.sprite_atual = mercador_alien.sprite_cumprimento
                    mercador_alien.texto_atual = mercador_alien.obter_texto_cumprimento()
                    mercador_alien.fase_dialogo = "apresentacao"  # Resetar para fase inicial
        
        # Desenhar fundo (simulando jogo)
        tela.fill((30, 50, 70))  # Cor de fundo mais interessante
        
        # Desenhar informações de debug (só quando mercador não está ativo)
        if not mercador_alien.ativo:
            fonte_debug = pygame.font.SysFont("consolas", 24, bold=True)
            texto_info = fonte_debug.render("TESTE DO MERCADOR ALIEN (SLICK)", True, (255, 200, 0))
            tela.blit(texto_info, (20, 20))
            
            fonte_info = pygame.font.SysFont("consolas", 18, bold=True)
            
            dinheiro_texto = f"Dinheiro: ${gerenciador_progresso.dinheiro:,}"
            texto_dinheiro = fonte_info.render(dinheiro_texto, True, (255, 215, 0))
            tela.blit(texto_dinheiro, (20, 60))
            
            if mercador_alien.oferta_atual:
                oferta_texto = f"Oferta: {mercador_alien.oferta_atual['tipo']} - ${mercador_alien.oferta_atual['preco']:,}"
                texto_oferta = fonte_info.render(oferta_texto, True, (200, 200, 255))
                tela.blit(texto_oferta, (20, 90))
                
                upgrade_texto = f"Upgrade: {mercador_alien.oferta_atual.get('tipo_upgrade', 'N/A')}"
                texto_upgrade = fonte_info.render(upgrade_texto, True, (200, 255, 200))
                tela.blit(texto_upgrade, (20, 120))
            
            fase_texto = f"Fase: {mercador_alien.fase_dialogo}"
            texto_fase = fonte_info.render(fase_texto, True, (255, 255, 255))
            tela.blit(texto_fase, (20, 150))
            
            contexto_texto = f"Contexto: {mercador_alien.contexto_atual}"
            texto_contexto = fonte_info.render(contexto_texto, True, (255, 200, 200))
            tela.blit(texto_contexto, (20, 180))
            
            instrucoes = [
                "Q: Forçar nova oferta",
                "SETAS: Navegar opções",
                "ENTER: Confirmar",
                "ESC: Fechar/Recusar"
            ]
            y_instrucoes = 220
            for instrucao in instrucoes:
                texto_inst = fonte_info.render(instrucao, True, (150, 150, 150))
                tela.blit(texto_inst, (20, y_instrucoes))
                y_instrucoes += 30
        
        # Desenhar mercador (com overlay escuro e diálogo estilo visual novel)
        if mercador_alien.ativo:
            mercador_alien.desenhar_dialogo(tela, dt)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

