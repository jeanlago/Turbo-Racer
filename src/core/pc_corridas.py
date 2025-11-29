# src/core/pc_corridas.py
"""
Sistema de Corridas no PC
Tela para selecionar e iniciar corridas no modo campanha
"""

import os
import pygame
from typing import Optional
from config import LARGURA, ALTURA, DIR_PROJETO, FPS

def _get_render_text():
    from core.menu import render_text
    return render_text

NOMES_PISTAS = {
    1: "Pista Principal",
    2: "Circuito Urbano",
    3: "Montanha Akira",
    4: "Pista Industrial",
    5: "Circuito Velocidade",
    6: "Pista Técnica",
    7: "Circuito Desafio",
    8: "Pista Elite",
    9: "Circuito da Coroa"
}

def pc_corridas_loop(screen) -> Optional[dict]:
    """
    Loop principal da tela de corridas no PC
    Retorna um dicionário com informações da corrida selecionada ou None se cancelado
    
    Formato retornado:
    {
        "pista": 1,  # Número da pista (1-9)
        "voltas": 1,
        "dificuldade": "medio"
    }
    """
    from core.pista_tiles import PistaTiles
    from core.progresso import gerenciador_progresso
    from core.missoes import gerenciador_missoes
    
    clock = pygame.time.Clock()
    render_text = _get_render_text()
    
    todas_missoes = gerenciador_missoes.obter_todas_missoes()
    
    missao_selecionada_idx = 0
    missao_hover_idx = None
    
    missao_ativa = gerenciador_missoes.obter_missao_ativa()
    if missao_ativa:
        for i, missao in enumerate(todas_missoes):
            if missao["id"] == missao_ativa["id"]:
                missao_selecionada_idx = i
                break
    
    def eh_missao_corrida(missao):
        if not missao:
            return False
        objetivo = missao.get("objetivo", "").lower()
        palavras_corrida = ["corrida", "corra", "circuito", "pista", "race", "teste de fluxo"]
        return any(palavra in objetivo for palavra in palavras_corrida)
    
    pista_selecionada = 1
    voltas_selecionadas = 1
    dificuldade_selecionada = "medio"
    dificuldades = ["facil", "medio", "dificil"]
    dificuldade_idx = 1
    
    pista_tiles = PistaTiles()
    minimapa_selecionado = None
    
    from config import DIR_UI
    caminho_tela_pc = os.path.join(DIR_UI, "tela_pc.png")
    if os.path.exists(caminho_tela_pc):
        bg_raw = pygame.image.load(caminho_tela_pc).convert_alpha()
        bg = pygame.transform.scale(bg_raw, (LARGURA, ALTURA))
    else:
        bg = pygame.Surface((LARGURA, ALTURA))
        bg.fill((20, 20, 30))
    
    running = True
    
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    missao_selecionada_idx = max(0, missao_selecionada_idx - 1)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    missao_selecionada_idx = min(len(todas_missoes) - 1, missao_selecionada_idx + 1)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if missao_selecionada_idx < len(todas_missoes):
                        missao_atual = todas_missoes[missao_selecionada_idx]
                        if eh_missao_corrida(missao_atual):
                            voltas_selecionadas = max(1, voltas_selecionadas - 1)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if missao_selecionada_idx < len(todas_missoes):
                        missao_atual = todas_missoes[missao_selecionada_idx]
                        if eh_missao_corrida(missao_atual):
                            voltas_selecionadas = min(10, voltas_selecionadas + 1)
                elif event.key == pygame.K_TAB:
                    if missao_selecionada_idx < len(todas_missoes):
                        missao_atual = todas_missoes[missao_selecionada_idx]
                        if eh_missao_corrida(missao_atual):
                            dificuldade_idx = (dificuldade_idx + 1) % len(dificuldades)
                            dificuldade_selecionada = dificuldades[dificuldade_idx]
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if missao_selecionada_idx < len(todas_missoes):
                        missao_atual = todas_missoes[missao_selecionada_idx]
                        if eh_missao_corrida(missao_atual):
                            return {
                                "pista": pista_selecionada,
                                "voltas": voltas_selecionadas,
                                "dificuldade": dificuldade_selecionada
                            }
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    
                    painel_esq_x = 50
                    painel_esq_y = 100
                    painel_esq_largura = 500
                    espacamento_missoes = 55
                    altura_item_missao = 45
                    y_inicio = painel_esq_y + 50
                    
                    for i, missao in enumerate(todas_missoes):
                        y_missao = y_inicio + i * espacamento_missoes
                        if (painel_esq_x + 15 <= mouse_x <= painel_esq_x + painel_esq_largura - 15 and
                            y_missao <= mouse_y <= y_missao + altura_item_missao):
                            missao_selecionada_idx = i
                            break
                    
                    btn_iniciar_x = LARGURA // 2 - 120
                    btn_iniciar_y = ALTURA - 80
                    btn_iniciar_largura = 240
                    btn_iniciar_altura = 40
                    if (btn_iniciar_x <= mouse_x <= btn_iniciar_x + btn_iniciar_largura and
                        btn_iniciar_y <= mouse_y <= btn_iniciar_y + btn_iniciar_altura):
                        if missao_selecionada_idx < len(todas_missoes):
                            missao_atual = todas_missoes[missao_selecionada_idx]
                            if eh_missao_corrida(missao_atual):
                                return {
                                    "pista": pista_selecionada,
                                    "voltas": voltas_selecionadas,
                                    "dificuldade": dificuldade_selecionada
                                }
            
            elif event.type == pygame.MOUSEMOTION:
                pass
        
        screen.blit(bg, (0, 0))
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        painel_esq_x = 50
        painel_esq_y = 100
        painel_esq_largura = 500
        espacamento_missoes = 55
        altura_item_missao = 45
        y_inicio = painel_esq_y + 50
        
        missao_hover_idx = None
        for i, missao in enumerate(todas_missoes):
            y_missao = y_inicio + i * espacamento_missoes
            if (painel_esq_x + 15 <= mouse_x <= painel_esq_x + painel_esq_largura - 15 and
                y_missao <= mouse_y <= y_missao + altura_item_missao):
                missao_hover_idx = i
                break
        
        titulo = render_text("MISSÕES", 28, (255, 255, 255), bold=True, pixel_style=True)
        titulo_x = (LARGURA - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, 30))
        
        painel_esq_altura = 500
        pygame.draw.rect(screen, (255, 255, 0), (painel_esq_x, painel_esq_y, painel_esq_largura, painel_esq_altura), 3)
        
        painel_esq_titulo = render_text("MISSÕES", 20, (255, 255, 0), bold=True, pixel_style=True)
        screen.blit(painel_esq_titulo, (painel_esq_x + 15, painel_esq_y + 15))
        
        espacamento_missoes = 55
        altura_item_missao = 45
        y_inicio = painel_esq_y + 50
        for i, missao in enumerate(todas_missoes):
            y_missao = y_inicio + i * espacamento_missoes
            
            esta_completa = gerenciador_missoes.esta_completa(missao["id"])
            
            if i == missao_selecionada_idx:
                cor_fundo = (100, 150, 255, 200)
                cor_texto = (255, 255, 255)
                bold = True
            elif i == missao_hover_idx:
                cor_fundo = (80, 80, 80, 200)
                cor_texto = (200, 200, 255)
                bold = False
            else:
                cor_fundo = (40, 40, 40, 150)
                cor_texto = (180, 180, 180)
                bold = False
            
            if esta_completa:
                cor_texto = (150, 255, 150) if i != missao_selecionada_idx else (200, 255, 200)
            
            item_bg = pygame.Surface((painel_esq_largura - 30, altura_item_missao), pygame.SRCALPHA)
            item_bg.fill(cor_fundo)
            screen.blit(item_bg, (painel_esq_x + 15, y_missao))
            
            nome_missao = missao.get("nome", "Missão sem nome")
            if esta_completa:
                nome_missao = "✓ " + nome_missao
            nome_texto = render_text(nome_missao, 20, cor_texto, bold=bold, pixel_style=True)
            texto_y = y_missao + (altura_item_missao - nome_texto.get_height()) // 2
            screen.blit(nome_texto, (painel_esq_x + 20, texto_y))
        
        if missao_selecionada_idx < len(todas_missoes):
            missao_selecionada_atual = todas_missoes[missao_selecionada_idx]
            missao_eh_corrida = eh_missao_corrida(missao_selecionada_atual)
            
            if missao_eh_corrida and minimapa_selecionado is None:
                minimapa_selecionado = pista_tiles.carregar_minimapa(pista_selecionada)
        else:
            missao_selecionada_atual = None
            missao_eh_corrida = False
        
        painel_x = 600
        painel_y = 100
        painel_largura = 600
        painel_altura = 450
        
        pygame.draw.rect(screen, (255, 255, 0), (painel_x, painel_y, painel_largura, painel_altura), 3)
        
        painel_titulo = render_text("OBJETIVO DA MISSÃO", 12, (255, 255, 0), bold=True, pixel_style=True)
        screen.blit(painel_titulo, (painel_x + 20, painel_y + 20))
        
        if missao_selecionada_atual:
            objetivo = missao_selecionada_atual.get("objetivo", "Nenhum objetivo definido")
            palavras = objetivo.split()
            linhas = []
            linha_atual = ""
            y_texto = painel_y + 80
            
            for palavra in palavras:
                teste_linha = linha_atual + (" " if linha_atual else "") + palavra
                teste_texto = render_text(teste_linha, 35, (255, 255, 255), bold=False, pixel_style=True)
                if teste_texto.get_width() > painel_largura - 40:
                    if linha_atual:
                        linhas.append(linha_atual)
                        linha_atual = palavra
                    else:
                        linhas.append(palavra)
                        linha_atual = ""
                else:
                    linha_atual = teste_linha
            
            if linha_atual:
                linhas.append(linha_atual)
            
            num_linhas_objetivo = len(linhas[:15])
            for i, linha in enumerate(linhas[:15]):
                linha_texto = render_text(linha, 35, (255, 255, 255), bold=False, pixel_style=True)
                screen.blit(linha_texto, (painel_x + 20, y_texto + i * 42))
            
            if missao_eh_corrida:
                nome_circuito = NOMES_PISTAS.get(pista_selecionada, f"Pista {pista_selecionada}")
                y_circuito = y_texto + (num_linhas_objetivo * 42) + 20
                circuito_label = render_text("Circuito:", 30, (255, 255, 0), bold=True, pixel_style=True)
                screen.blit(circuito_label, (painel_x + 20, y_circuito))
                circuito_nome = render_text(nome_circuito, 35, (255, 255, 255), bold=True, pixel_style=True)
                screen.blit(circuito_nome, (painel_x + 20, y_circuito + 40))
        else:
            objetivo_texto = render_text("Nenhum objetivo definido", 150, (150, 150, 150), bold=False, pixel_style=True)
            screen.blit(objetivo_texto, (painel_x + 20, painel_y + 60))
        
        btn_iniciar_x = LARGURA // 2 - 120
        btn_iniciar_y = ALTURA - 80
        btn_iniciar_largura = 240
        btn_iniciar_altura = 40
        
        btn_bg = pygame.Surface((btn_iniciar_largura, btn_iniciar_altura), pygame.SRCALPHA)
        btn_bg.fill((0, 150, 0, 200))
        pygame.draw.rect(btn_bg, (255, 255, 255), (0, 0, btn_iniciar_largura, btn_iniciar_altura), 2)
        screen.blit(btn_bg, (btn_iniciar_x, btn_iniciar_y))
        
        btn_texto = render_text("INICIAR (ENTER)", 14, (255, 255, 255), bold=True, pixel_style=True)
        btn_texto_x = btn_iniciar_x + (btn_iniciar_largura - btn_texto.get_width()) // 2
        btn_texto_y = btn_iniciar_y + (btn_iniciar_altura - btn_texto.get_height()) // 2
        screen.blit(btn_texto, (btn_texto_x, btn_texto_y))
        
        if missao_selecionada_atual and missao_eh_corrida:
            instrucoes = render_text("↑↓ navegar | ← → voltas | TAB dificuldade | ENTER iniciar | ESC voltar", 12, (150, 150, 150), bold=False, pixel_style=True)
        else:
            instrucoes = render_text("↑↓ navegar | Clique selecionar | ESC voltar", 12, (150, 150, 150), bold=False, pixel_style=True)
        screen.blit(instrucoes, (10, ALTURA - 25))
        
        pygame.display.flip()
    
    return None

