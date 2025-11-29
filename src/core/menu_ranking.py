# src/core/menu_ranking.py
"""Tela de Ranking de Pilotos"""
import pygame
from config import LARGURA, ALTURA, FPS, CAMINHO_MENU
from core.menu import render_text, scale_to_cover, gerenciador_musica, popup_musica
from core.ranking import gerenciador_ranking
from core.i18n import t

def ranking_loop(screen):
    """Tela de ranking mostrando o Top 10 de pilotos"""
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)
    
    clock = pygame.time.Clock()
    
    caixa_largura = 900
    caixa_altura = 700
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2
    
    voltar_selecionado = True
    animacao_cursor = 0.0
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        
        animacao_cursor += dt * 3.0
        
        gerenciador_musica.verificar_fim_musica()
        popup_musica.atualizar(dt)
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        popup_musica.verificar_hover(mouse_x, mouse_y)
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            
            from core.gamepad_manager import gerenciador_gamepad
            controle_processado = False
            if gerenciador_gamepad.obter_numero_controles() > 0:
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
                resultado_controle = processar_eventos_controle_menu(ev, 0, 1, joystick_id=0, tempo_atual=tempo_atual)
                if resultado_controle:
                    controle_processado = True
                    acao = resultado_controle.get("acao")
                    if acao == "cancelar" or acao == "confirmar":
                        return True
            
            if controle_processado:
                continue
            
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                voltar_largura = 120
                voltar_altura = 40
                voltar_x = caixa_x + (caixa_largura - voltar_largura) // 2
                voltar_y = caixa_y + caixa_altura - 50
                voltar_rect = pygame.Rect(voltar_x, voltar_y, voltar_largura, voltar_altura)
                if voltar_rect.collidepoint(ev.pos[0], ev.pos[1]):
                    return True
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return True
        
        screen.blit(bg, (0, 0))
        
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        
        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 150))
        screen.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        titulo = render_text("HIERARQUIA", 36, (255, 220, 100), bold=True, pixel_style=True)
        titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, caixa_y + 20))
        
        y_cabecalho = caixa_y + 80
        x_pos = caixa_x + 50
        x_nome = caixa_x + 150
        x_vitorias = caixa_x + 500
        x_derrotas = caixa_x + 650
        
        cabecalho_pos = render_text("POS", 20, (255, 255, 255), bold=True, pixel_style=True)
        cabecalho_nome = render_text("PILOTO", 20, (255, 255, 255), bold=True, pixel_style=True)
        cabecalho_vitorias = render_text("VITÓRIAS", 20, (255, 255, 255), bold=True, pixel_style=True)
        cabecalho_derrotas = render_text("DERROTAS", 20, (255, 255, 255), bold=True, pixel_style=True)
        
        screen.blit(cabecalho_pos, (x_pos, y_cabecalho))
        screen.blit(cabecalho_nome, (x_nome, y_cabecalho))
        screen.blit(cabecalho_vitorias, (x_vitorias, y_cabecalho))
        screen.blit(cabecalho_derrotas, (x_derrotas, y_cabecalho))
        
        pygame.draw.line(screen, (128, 128, 128), 
                        (caixa_x + 30, y_cabecalho + 35), 
                        (caixa_x + caixa_largura - 30, y_cabecalho + 35), 2)
        
        ranking = gerenciador_ranking.obter_ranking()
        posicao_jogador = gerenciador_ranking.obter_posicao_jogador()
        from core.progresso import gerenciador_progresso
        
        y_atual = y_cabecalho + 50
        for piloto in ranking:
            pos = piloto['posicao']
            nome = piloto['nome']
            vitorias = piloto.get('vitorias', 0)
            derrotas = piloto.get('derrotas', 0)
            e_jogador = piloto.get('e_jogador', False) or nome == "JOGADOR" or nome == gerenciador_progresso.nome_jogador
            
            if pos == 1:
                cor_pos = (255, 215, 0)  # Ouro
                cor_nome = (255, 215, 0)
            elif pos == 2:
                cor_pos = (192, 192, 192)  # Prata
                cor_nome = (192, 192, 192)
            elif pos == 3:
                cor_pos = (205, 127, 50)  # Bronze
                cor_nome = (205, 127, 50)
            elif e_jogador:
                cor_pos = (255, 255, 100)  # Amarelo claro para jogador (mais visível)
                cor_nome = (255, 255, 100)
            else:
                cor_pos = (255, 255, 255)
                cor_nome = (255, 255, 255)
            
            texto_pos = render_text(f"{pos}º", 18, cor_pos, bold=False, pixel_style=True)
            screen.blit(texto_pos, (x_pos, y_atual))
            
            if e_jogador:
                nome_display = gerenciador_progresso.nome_jogador
            else:
                nome_display = nome
            texto_nome = render_text(nome_display, 18, cor_nome, bold=e_jogador, pixel_style=True)
            screen.blit(texto_nome, (x_nome, y_atual))
            
            texto_vitorias = render_text(str(vitorias), 18, (0, 255, 0), bold=False, pixel_style=True)
            screen.blit(texto_vitorias, (x_vitorias, y_atual))
            
            texto_derrotas = render_text(str(derrotas), 18, (255, 100, 100), bold=False, pixel_style=True)
            screen.blit(texto_derrotas, (x_derrotas, y_atual))
            
            if e_jogador:
                highlight_rect = pygame.Rect(caixa_x + 25, y_atual - 5, caixa_largura - 50, 30)
                highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
                highlight_surface.fill((255, 255, 100, 30))  # Amarelo claro com transparência
                screen.blit(highlight_surface, highlight_rect)
                pygame.draw.rect(screen, (255, 255, 100), highlight_rect, 2)
            
            y_atual += 40
        
        voltar_largura = 120
        voltar_altura = 40
        voltar_x = caixa_x + (caixa_largura - voltar_largura) // 2
        voltar_y = caixa_y + caixa_altura - 50
        voltar_rect = pygame.Rect(voltar_x, voltar_y, voltar_largura, voltar_altura)
        
        voltar_hover = voltar_rect.collidepoint(mouse_x, mouse_y)
        
        if voltar_hover:
            cor_voltar = (255, 80, 80)
            cor_borda = (255, 150, 150)
        elif voltar_selecionado:
            cor_voltar = (200, 50, 50)
            cor_borda = (255, 100, 100)
        else:
            cor_voltar = (150, 50, 50)
            cor_borda = (200, 80, 80)
        
        pygame.draw.rect(screen, cor_voltar, voltar_rect)
        pygame.draw.rect(screen, cor_borda, voltar_rect, 2)
        
        voltar_texto = render_text("VOLTAR", 18, (255, 255, 255), bold=True, pixel_style=True)
        voltar_texto_x = voltar_x + (voltar_largura - voltar_texto.get_width()) // 2
        voltar_texto_y = voltar_y + (voltar_altura - voltar_texto.get_height()) // 2
        screen.blit(voltar_texto, (voltar_texto_x, voltar_texto_y))
        
        popup_musica.desenhar(screen)
        pygame.display.flip()

