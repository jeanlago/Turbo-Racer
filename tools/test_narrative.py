#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Narrativa por Capítulo
Permite testar cada capítulo da narrativa sem precisar reiniciar o save
"""

import pygame
import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import LARGURA, ALTURA, FPS
from core.narrative_system import narrative_system
from core.progresso import gerenciador_progresso

# Capítulos disponíveis
CAPITULOS = {
    "1": {
        "id": "ch1",
        "nome": "Capítulo 1 - Ferrugem e Primeira Corrida",
        "descricao": "Prologue → Crank → Teste → Boris → Primeira Corrida"
    },
    "2": {
        "id": "ch2",
        "nome": "Capítulo 2 - Contrato com o Barão",
        "descricao": "Barão → Empréstimo → Cinturão Industrial"
    },
    "3": {
        "id": "ch3",
        "nome": "Capítulo 3 - Fluxo da Montanha",
        "descricao": "Akira → Montanha → Teste de Fluxo"
    },
    "4": {
        "id": "ch4",
        "nome": "Capítulo 4 - Olhos nas Torres",
        "descricao": "Rex observa → Slick → Glub"
    },
    "5": {
        "id": "ch5",
        "nome": "Capítulo 5 - Jogo do Rei",
        "descricao": "Circuito da Coroa → Preparações → Corrida Final"
    }
}

def mostrar_menu_selecao(screen):
    """Mostra menu de seleção de capítulo"""
    pygame.init()
    clock = pygame.time.Clock()
    
    from core.menu import render_text
    
    selecionado = 0
    rodando = True
    
    while rodando:
        dt = clock.tick(FPS) / 1000.0
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return None
            
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP or evento.key == pygame.K_w:
                    selecionado = (selecionado - 1) % len(CAPITULOS)
                elif evento.key == pygame.K_DOWN or evento.key == pygame.K_s:
                    selecionado = (selecionado + 1) % len(CAPITULOS)
                elif evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                    # Retornar o ID do capítulo selecionado
                    capitulo_key = list(CAPITULOS.keys())[selecionado]
                    return CAPITULOS[capitulo_key]["id"]
                elif evento.key == pygame.K_ESCAPE:
                    return None
        
        # Desenhar
        screen.fill((20, 20, 30))
        
        # Título
        titulo = render_text("TESTE DE NARRATIVA POR CAPÍTULO", 32, (255, 255, 255), bold=True, pixel_style=True)
        screen.blit(titulo, ((LARGURA - titulo.get_width()) // 2, 50))
        
        # Instruções
        instrucoes = render_text("Use ↑↓ para navegar, ENTER para selecionar, ESC para sair", 18, (200, 200, 200), bold=False, pixel_style=True)
        screen.blit(instrucoes, ((LARGURA - instrucoes.get_width()) // 2, 100))
        
        # Lista de capítulos
        y_start = 180
        espacamento = 80
        
        for i, (key, capitulo) in enumerate(CAPITULOS.items()):
            y = y_start + i * espacamento
            
            # Cor baseada na seleção
            if i == selecionado:
                cor_nome = (255, 255, 100)
                cor_desc = (200, 200, 200)
                # Fundo destacado
                fundo = pygame.Surface((LARGURA - 200, 70), pygame.SRCALPHA)
                fundo.fill((100, 100, 150, 100))
                screen.blit(fundo, (100, y - 5))
            else:
                cor_nome = (150, 150, 150)
                cor_desc = (100, 100, 100)
            
            # Nome do capítulo
            nome_texto = render_text(f"{key}. {capitulo['nome']}", 24, cor_nome, bold=True, pixel_style=True)
            screen.blit(nome_texto, (120, y))
            
            # Descrição
            desc_texto = render_text(capitulo['descricao'], 16, cor_desc, bold=False, pixel_style=True)
            screen.blit(desc_texto, (120, y + 35))
        
        pygame.display.flip()
    
    return None

def preparar_capitulo(capitulo_id):
    """Prepara o progresso para o capítulo selecionado"""
    print(f"\n=== Preparando para {capitulo_id} ===")
    
    # Definir capítulo atual
    gerenciador_progresso.definir_capitulo_atual(capitulo_id)
    
    # Preparar progresso baseado no capítulo
    if capitulo_id == "ch1":
        # Capítulo 1: início do jogo
        gerenciador_progresso.dinheiro = 5000
        gerenciador_progresso.carros_desbloqueados = {"Car1"}
        gerenciador_progresso.carro_p1_atual = "Car1"
        # Resetar flags de NPCs
        gerenciador_progresso.crank_nome_revelado = False
        gerenciador_progresso.boris_nome_revelado = False
        gerenciador_progresso.pixel_nome_revelado = False
        print("✓ Progresso resetado para início do Capítulo 1")
    
    elif capitulo_id == "ch2":
        # Capítulo 2: após primeira corrida
        gerenciador_progresso.dinheiro = 8000
        gerenciador_progresso.carros_desbloqueados = {"Car1"}
        gerenciador_progresso.carro_p1_atual = "Car1"
        gerenciador_progresso.marcar_capitulo_completo("ch1")
        gerenciador_progresso.crank_nome_revelado = True
        gerenciador_progresso.boris_nome_revelado = True
        gerenciador_progresso.pixel_nome_revelado = True
        print("✓ Progresso configurado para início do Capítulo 2")
    
    elif capitulo_id == "ch3":
        # Capítulo 3: após Cinturão Industrial
        gerenciador_progresso.dinheiro = 15000
        gerenciador_progresso.carros_desbloqueados = {"Car1", "Car2"}
        gerenciador_progresso.carro_p1_atual = "Car1"
        gerenciador_progresso.marcar_capitulo_completo("ch1")
        gerenciador_progresso.marcar_capitulo_completo("ch2")
        gerenciador_progresso.crank_nome_revelado = True
        gerenciador_progresso.boris_nome_revelado = True
        gerenciador_progresso.pixel_nome_revelado = True
        gerenciador_progresso.akira_nome_revelado = False
        print("✓ Progresso configurado para início do Capítulo 3")
    
    elif capitulo_id == "ch4":
        # Capítulo 4: após montanha
        gerenciador_progresso.dinheiro = 25000
        gerenciador_progresso.carros_desbloqueados = {"Car1", "Car2", "Car3"}
        gerenciador_progresso.carro_p1_atual = "Car1"
        gerenciador_progresso.marcar_capitulo_completo("ch1")
        gerenciador_progresso.marcar_capitulo_completo("ch2")
        gerenciador_progresso.marcar_capitulo_completo("ch3")
        gerenciador_progresso.crank_nome_revelado = True
        gerenciador_progresso.boris_nome_revelado = True
        gerenciador_progresso.pixel_nome_revelado = True
        gerenciador_progresso.akira_nome_revelado = True
        print("✓ Progresso configurado para início do Capítulo 4")
    
    elif capitulo_id == "ch5":
        # Capítulo 5: antes do Circuito da Coroa
        gerenciador_progresso.dinheiro = 50000
        gerenciador_progresso.carros_desbloqueados = {"Car1", "Car2", "Car3", "Car4"}
        gerenciador_progresso.carro_p1_atual = "Car1"
        gerenciador_progresso.marcar_capitulo_completo("ch1")
        gerenciador_progresso.marcar_capitulo_completo("ch2")
        gerenciador_progresso.marcar_capitulo_completo("ch3")
        gerenciador_progresso.marcar_capitulo_completo("ch4")
        gerenciador_progresso.crank_nome_revelado = True
        gerenciador_progresso.boris_nome_revelado = True
        gerenciador_progresso.pixel_nome_revelado = True
        gerenciador_progresso.akira_nome_revelado = True
        gerenciador_progresso.rex_nome_revelado = True
        print("✓ Progresso configurado para início do Capítulo 5")
    
    # Salvar progresso
    gerenciador_progresso.salvar()
    print(f"✓ Progresso salvo\n")

def main():
    """Função principal de teste"""
    pygame.init()
    
    # Criar tela
    screen = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Teste de Narrativa por Capítulo")
    
    # Mostrar menu de seleção
    capitulo_id = mostrar_menu_selecao(screen)
    
    if not capitulo_id:
        print("Teste cancelado.")
        return
    
    # Preparar progresso para o capítulo
    preparar_capitulo(capitulo_id)
    
    # Iniciar narrativa
    print(f"Iniciando narrativa do {capitulo_id}...")
    narrative_system.iniciar_capitulo(capitulo_id)
    narrative_system.active = True
    
    # Loop principal
    clock = pygame.time.Clock()
    rodando = True
    
    while rodando:
        dt = clock.tick(FPS) / 1000.0
        
        # Processar eventos
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                rodando = False
                break
            
            resultado = narrative_system.processar_eventos(eventos)
            if resultado == "fechado":
                rodando = False
                break
        
        # Atualizar
        narrative_system.atualizar(dt)
        
        # Desenhar
        screen.fill((0, 0, 0))
        narrative_system.desenhar(screen)
        pygame.display.flip()
    
    pygame.quit()
    print("\nTeste finalizado.")

if __name__ == "__main__":
    main()

