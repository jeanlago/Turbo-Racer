#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste interativo para o NPC Barão (Agiota)
Permite testar os diferentes diálogos e situações do Barão
"""

import sys
import os

# Adicionar o diretório src ao path (ajustado para estar em tools/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pygame
from config import LARGURA, ALTURA
from core.barao import barao
from core.progresso import gerenciador_progresso

def main():
    """Função principal do teste"""
    pygame.init()
    
    # Configurar tela
    screen = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Teste do Barão - Agiota")
    
    clock = pygame.time.Clock()
    dt = 0.0
    
    # Carregar sprites do Barão
    barao.carregar_sprites()
    
    # Estado do teste
    print("=" * 60)
    print("TESTE DO BARÃO - AGIOTA")
    print("=" * 60)
    print("\nControles:")
    print("  O - Oferecer empréstimo (quando jogador está sem dinheiro)")
    print("  L - Mostrar lembrete (quando empréstimo está ativo)")
    print("  C - Mostrar cobrança (quando prazo acabou)")
    print("  P - Simular pagamento (quando jogador tem dinheiro)")
    print("  D - Simular calote (quando jogador não tem dinheiro)")
    print("  A - Aceitar empréstimo (quando na tela de aceitar/recusar)")
    print("  R - Recusar empréstimo (quando na tela de aceitar/recusar)")
    print("  ESPAÇO - Avançar diálogo")
    print("  ESC - Fechar diálogo")
    print("  Q - Sair do teste")
    print("\nEstado atual:")
    print(f"  Dinheiro: ${gerenciador_progresso.dinheiro:,}")
    print(f"  Empréstimo ativo: {gerenciador_progresso.barao_emprestimo_ativo}")
    print(f"  Valor devido: ${gerenciador_progresso.barao_valor_devido:,}")
    print(f"  Corridas restantes: {gerenciador_progresso.barao_corridas_restantes}")
    print("=" * 60)
    
    rodando = True
    
    while rodando:
        dt = clock.tick(60) / 1000.0
        
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_q:
                    rodando = False
                elif evento.key == pygame.K_o:
                    # Simular condições para oferta
                    gerenciador_progresso.dinheiro = 300  # Pouco dinheiro
                    gerenciador_progresso.barao_emprestimo_ativo = False
                    from core.crank import crank
                    if hasattr(crank, 'saude_carro'):
                        crank.saude_carro = 0.2  # Carro quebrado
                    barao.verificar_aparecer_oferta()
                    print("\n[O] Oferta de empréstimo ativada")
                elif evento.key == pygame.K_l:
                    # Simular condições para lembrete
                    gerenciador_progresso.barao_emprestimo_ativo = True
                    gerenciador_progresso.barao_corridas_restantes = 2
                    gerenciador_progresso.barao_valor_devido = 7500
                    barao.verificar_aparecer_lembrete()
                    print("\n[L] Lembrete ativado")
                elif evento.key == pygame.K_c:
                    # Simular condições para cobrança
                    gerenciador_progresso.barao_emprestimo_ativo = True
                    gerenciador_progresso.barao_corridas_restantes = 0
                    gerenciador_progresso.barao_valor_devido = 7500
                    gerenciador_progresso.dinheiro = 8000  # Tem dinheiro
                    barao.verificar_aparecer_cobranca()
                    print("\n[C] Cobrança ativada (jogador tem dinheiro)")
                elif evento.key == pygame.K_p:
                    # Simular pagamento
                    gerenciador_progresso.barao_emprestimo_ativo = True
                    gerenciador_progresso.barao_corridas_restantes = 0
                    gerenciador_progresso.barao_valor_devido = 7500
                    gerenciador_progresso.dinheiro = 10000  # Tem dinheiro suficiente
                    barao.verificar_aparecer_cobranca()
                    print("\n[P] Pagamento ativado")
                elif evento.key == pygame.K_d:
                    # Simular calote
                    gerenciador_progresso.barao_emprestimo_ativo = True
                    gerenciador_progresso.barao_corridas_restantes = 0
                    gerenciador_progresso.barao_valor_devido = 7500
                    gerenciador_progresso.dinheiro = 100  # Não tem dinheiro
                    barao.verificar_aparecer_cobranca()
                    print("\n[D] Calote ativado (jogador não tem dinheiro)")
                elif evento.key == pygame.K_a:
                    # Aceitar empréstimo
                    if barao.fase_dialogo == "aceitar_recusar":
                        barao.aceitar_emprestimo()
                        print("\n[A] Empréstimo aceito!")
                        print(f"  Dinheiro atual: ${gerenciador_progresso.dinheiro:,}")
                        print(f"  Valor devido: ${gerenciador_progresso.barao_valor_devido:,}")
                        print(f"  Corridas restantes: {gerenciador_progresso.barao_corridas_restantes}")
                elif evento.key == pygame.K_r:
                    # Recusar empréstimo
                    if barao.fase_dialogo == "aceitar_recusar":
                        barao.recusar_emprestimo()
                        print("\n[R] Empréstimo recusado!")
                elif evento.key == pygame.K_SPACE:
                    # Avançar diálogo
                    if barao.ativo:
                        if len(barao.texto_exibido) < len(barao.texto_completo):
                            barao._completar_animacao_texto()
                        else:
                            barao._avancar_dialogo()
                elif evento.key == pygame.K_ESCAPE:
                    # Fechar diálogo
                    if barao.ativo and barao.fase_dialogo != "aceitar_recusar":
                        barao.fechar()
                        print("\n[ESC] Diálogo fechado")
        
        # Atualizar Barão
        barao.atualizar(dt)
        
        # Processar eventos do Barão
        if barao.ativo:
            barao.processar_eventos(eventos)
        
        # Desenhar
        screen.fill((20, 20, 30))  # Fundo escuro
        
        # Desenhar informações de debug
        font = pygame.font.Font(None, 24)
        debug_info = [
            f"Estado: {'ATIVO' if barao.ativo else 'INATIVO'}",
            f"Fase: {barao.fase_dialogo}",
            f"Parte: {barao.parte_dialogo}",
            f"Dinheiro: ${gerenciador_progresso.dinheiro:,}",
            f"Empréstimo ativo: {gerenciador_progresso.barao_emprestimo_ativo}",
            f"Valor devido: ${gerenciador_progresso.barao_valor_devido:,}",
            f"Corridas restantes: {gerenciador_progresso.barao_corridas_restantes}",
            "",
            "Controles:",
            "O - Oferta | L - Lembrete | C - Cobrança",
            "P - Pagamento | D - Calote",
            "A - Aceitar | R - Recusar",
            "ESPAÇO - Avançar | ESC - Fechar | Q - Sair"
        ]
        
        y_offset = 10
        for info in debug_info:
            if info:
                text = font.render(info, True, (255, 255, 255))
                screen.blit(text, (10, y_offset))
            y_offset += 25
        
        # Desenhar diálogo do Barão
        if barao.ativo:
            barao.desenhar_dialogo(screen, dt)
        
        pygame.display.flip()
    
    pygame.quit()
    print("\nTeste finalizado!")

if __name__ == "__main__":
    main()

