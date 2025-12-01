# src/core/mapa_cidade.py
"""
Tela do Mapa da Cidade - Point and Click Isométrico
Interface para navegação entre territórios
"""

import pygame
import os
from typing import Optional, Tuple
from config import LARGURA, ALTURA, FPS, DIR_PROJETO
from core.territorios import TERRITORIOS, Territorio, obter_territorios_desbloqueados, obter_territorio
from core.mapa_locations import gerenciador_localizacoes, EstadoLocalizacao

from config import obter_caminho_sprite_dia_noite
def obter_caminho_mapa_cidade():
    """Retorna o caminho do mapa da cidade baseado no ciclo dia/noite"""
    return obter_caminho_sprite_dia_noite("cidade")
CAMINHO_MAPA_CIDADE = obter_caminho_mapa_cidade()
CAMINHO_AREAS_MAPA = os.path.join(DIR_PROJETO, "data", "mapa_areas.json")
DIR_HOVER = os.path.join(DIR_PROJETO, "assets", "images", "hover", "mapa")

MAPEAMENTO_HOVER_SPRITES = {
    "bueiro": os.path.join(DIR_HOVER, "bueiro.png"),
    "pixel": os.path.join(DIR_HOVER, "bueiro.png"),
    "bunker": os.path.join(DIR_HOVER, "bueiro.png"),
    "iate": os.path.join(DIR_HOVER, "iate.png"),
    "barao": os.path.join(DIR_HOVER, "iate.png"),
    "barão": os.path.join(DIR_HOVER, "iate.png"),
    
    "fabrica": os.path.join(DIR_HOVER, "fabrica.png"),
    "fábrica": os.path.join(DIR_HOVER, "fabrica.png"),
    "boris": os.path.join(DIR_HOVER, "fabrica.png"),
    
    "predio": os.path.join(DIR_HOVER, "predio.png"),
    "prédio": os.path.join(DIR_HOVER, "predio.png"),
    "rex": os.path.join(DIR_HOVER, "predio.png"),
    
    "montanha": os.path.join(DIR_HOVER, "montanha.png"),
    "akira": os.path.join(DIR_HOVER, "montanha.png"),
    
    "oficina": os.path.join(DIR_HOVER, "oficina.png"),
    "autodromo": os.path.join(DIR_HOVER, "autodromo.png"),
    "autódromo": os.path.join(DIR_HOVER, "autodromo.png"),
}

ESCALAS_HOVER = {
    "bueiro": 2.0,
    "pixel": 2.0,
    "bunker": 2.0,
    "iate": 3.0,
    "barao": 3.0,
    "barão": 3.0,
    "fábrica": 4.0,
    "predio": 5.0,
    "prédio": 5.0,
    "rex": 5.0,
    "montanha": 4.0,
    "akira": 4.0,
    "oficina": 4.0,
    "autodromo": 3.0,
    "autódromo": 3.0,
}

def _get_render_text():
    """Importa e retorna a função render_text"""
    from core.menu import render_text
    return render_text

def carregar_areas_mapa():
    """Carrega áreas clicáveis do arquivo JSON"""
    areas = []
    if os.path.exists(CAMINHO_AREAS_MAPA):
        try:
            import json
            with open(CAMINHO_AREAS_MAPA, 'r', encoding='utf-8') as f:
                data = json.load(f)
                areas = data.get("areas", [])
                print(f"✓ Carregadas {len(areas)} áreas do mapa da cidade")
        except Exception as e:
            print(f"Erro ao carregar áreas do mapa: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"AVISO: Arquivo de áreas do mapa não encontrado: {CAMINHO_AREAS_MAPA}")
    return areas

def mostrar_pensamento_jogador(screen, mensagem: str, duracao: float = 3.0) -> bool:
    """
    Mostra uma mensagem de pensamento do jogador
    Retorna True se o jogador fechou a mensagem, False se ainda está mostrando
    """
    render_text = _get_render_text()
    clock = pygame.time.Clock()
    tempo_decorrido = 0.0
    
    palavras = mensagem.split(' ')
    linhas = []
    linha_atual = ""
    largura_max = 600
    
    for palavra in palavras:
        teste_linha = linha_atual + (" " if linha_atual else "") + palavra
        teste_render = render_text(teste_linha, 20, (255, 255, 255), bold=False, pixel_style=True)
        if teste_render.get_width() <= largura_max:
            linha_atual = teste_linha
        else:
            if linha_atual:
                linhas.append(linha_atual)
            linha_atual = palavra
    if linha_atual:
        linhas.append(linha_atual)
    
    altura_linha = 30
    padding = 30
    caixa_largura = largura_max + padding * 2
    caixa_altura = len(linhas) * altura_linha + padding * 2 + 50  # +50 para botão
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = ALTURA - caixa_altura - 100
    
    while tempo_decorrido < duracao:
        dt = clock.tick(FPS) / 1000.0
        tempo_decorrido += dt
        
        eventos = pygame.event.get()
        for ev in eventos:
            if ev.type == pygame.QUIT:
                return True
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    return True
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    return True
        
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 220))
        screen.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(screen, (150, 150, 150), (caixa_x, caixa_y, caixa_largura, caixa_altura), 2)
        
        y_texto = caixa_y + padding
        for linha in linhas:
            linha_render = render_text(linha, 20, (255, 255, 255), bold=False, pixel_style=True)
            screen.blit(linha_render, (caixa_x + padding, y_texto))
            y_texto += altura_linha
        
        instrucao = render_text("Pressione ESPAÇO ou clique para continuar", 14, (200, 200, 200), bold=False, pixel_style=True)
        instrucao_x = caixa_x + (caixa_largura - instrucao.get_width()) // 2
        screen.blit(instrucao, (instrucao_x, caixa_y + caixa_altura - 30))
        
        pygame.display.flip()
    
    return True

def mostrar_menu_casa_oficina(screen) -> Optional[str]:
    """Mostra menu de escolha entre casa e oficina"""
    render_text = _get_render_text()
    clock = pygame.time.Clock()
    opcao_selecionada = 0
    escolhido = False
    resultado = None
    
    from config import obter_caminho_sprite_dia_noite
    CAMINHO_CASA = obter_caminho_sprite_dia_noite("casa")
    CAMINHO_OFICINA = obter_caminho_sprite_dia_noite("oficina")
    
    sprite_casa = None
    sprite_oficina = None
    if os.path.exists(CAMINHO_CASA):
        try:
            sprite_casa = pygame.image.load(CAMINHO_CASA).convert_alpha()
        except Exception as e:
            print(f"Erro ao carregar sprite da casa: {e}")
    else:
        print(f"AVISO: Sprite da casa não encontrado: {CAMINHO_CASA}")
    
    if os.path.exists(CAMINHO_OFICINA):
        try:
            sprite_oficina = pygame.image.load(CAMINHO_OFICINA).convert_alpha()
        except Exception as e:
            print(f"Erro ao carregar sprite da oficina: {e}")
    else:
        print(f"AVISO: Sprite da oficina não encontrado: {CAMINHO_OFICINA}")
    
    while not escolhido:
        dt = clock.tick(FPS) / 1000.0
        
        eventos = pygame.event.get()
        for ev in eventos:
            if ev.type == pygame.QUIT:
                return None
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return None
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    opcao_selecionada = 0
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    opcao_selecionada = 1
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if opcao_selecionada == 0:
                        resultado = "casa"
                    else:
                        resultado = "oficina"
                    escolhido = True
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    mouse_x, mouse_y = ev.pos
                    caixa_largura = 800
                    caixa_altura = 400
                    caixa_x = (LARGURA - caixa_largura) // 2
                    caixa_y = (ALTURA - caixa_altura) // 2
                    
                    opcao_largura = 300
                    opcao_altura = 300
                    espacamento = 50
                    total_largura = opcao_largura * 2 + espacamento
                    inicio_x = caixa_x + (caixa_largura - total_largura) // 2
                    
                    casa_x = inicio_x
                    casa_y = caixa_y + 50
                    casa_rect = pygame.Rect(casa_x, casa_y, opcao_largura, opcao_altura)
                    if casa_rect.collidepoint(mouse_x, mouse_y):
                        resultado = "casa"
                        escolhido = True
                    
                    oficina_x = inicio_x + opcao_largura + espacamento
                    oficina_y = caixa_y + 50
                    oficina_rect = pygame.Rect(oficina_x, oficina_y, opcao_largura, opcao_altura)
                    if oficina_rect.collidepoint(mouse_x, mouse_y):
                        resultado = "oficina"
                        escolhido = True
        
        screen.fill((20, 20, 30))
        
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        caixa_largura = 800
        caixa_altura = 400
        caixa_x = (LARGURA - caixa_largura) // 2
        caixa_y = (ALTURA - caixa_altura) // 2
        
        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((30, 30, 40, 250))
        screen.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(screen, (150, 150, 150), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        titulo = render_text("Onde você quer ir?", 32, (255, 255, 255), bold=True, pixel_style=True)
        titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, caixa_y + 20))
        
        opcao_largura = 300
        opcao_altura = 300
        espacamento = 50
        total_largura = opcao_largura * 2 + espacamento
        inicio_x = caixa_x + (caixa_largura - total_largura) // 2
        
        casa_x = inicio_x
        casa_y = caixa_y + 80
        casa_rect = pygame.Rect(casa_x, casa_y, opcao_largura, opcao_altura)
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        casa_hover = casa_rect.collidepoint(mouse_x, mouse_y)
        if casa_hover:
            opcao_selecionada = 0
        
        if opcao_selecionada == 0:
            pygame.draw.rect(screen, (100, 150, 255), casa_rect, 4)
        else:
            pygame.draw.rect(screen, (80, 80, 80), casa_rect, 2)
        
        if sprite_casa:
            casa_sprite_w = min(opcao_largura - 20, sprite_casa.get_width())
            casa_sprite_h = int(sprite_casa.get_height() * (casa_sprite_w / sprite_casa.get_width()))
            casa_sprite_redim = pygame.transform.scale(sprite_casa, (casa_sprite_w, casa_sprite_h))
            casa_sprite_x = casa_x + (opcao_largura - casa_sprite_w) // 2
            casa_sprite_y = casa_y + 20
            screen.blit(casa_sprite_redim, (casa_sprite_x, casa_sprite_y))
        
        casa_texto = render_text("CASA", 24, (255, 255, 255), bold=True, pixel_style=True)
        casa_texto_x = casa_x + (opcao_largura - casa_texto.get_width()) // 2
        screen.blit(casa_texto, (casa_texto_x, casa_y + opcao_altura - 40))
        
        # Oficina (direita)
        oficina_x = inicio_x + opcao_largura + espacamento
        oficina_y = caixa_y + 80
        oficina_rect = pygame.Rect(oficina_x, oficina_y, opcao_largura, opcao_altura)
        
        # Verificar hover
        oficina_hover = oficina_rect.collidepoint(mouse_x, mouse_y)
        if oficina_hover:
            opcao_selecionada = 1
        
        # Desenhar opção oficina
        if opcao_selecionada == 1:
            pygame.draw.rect(screen, (100, 150, 255), oficina_rect, 4)
        else:
            pygame.draw.rect(screen, (80, 80, 80), oficina_rect, 2)
        
        if sprite_oficina:
            oficina_sprite_w = min(opcao_largura - 20, sprite_oficina.get_width())
            oficina_sprite_h = int(sprite_oficina.get_height() * (oficina_sprite_w / sprite_oficina.get_width()))
            oficina_sprite_redim = pygame.transform.scale(sprite_oficina, (oficina_sprite_w, oficina_sprite_h))
            oficina_sprite_x = oficina_x + (opcao_largura - oficina_sprite_w) // 2
            oficina_sprite_y = oficina_y + 20
            screen.blit(oficina_sprite_redim, (oficina_sprite_x, oficina_sprite_y))
        
        oficina_texto = render_text("OFICINA", 24, (255, 255, 255), bold=True, pixel_style=True)
        oficina_texto_x = oficina_x + (opcao_largura - oficina_texto.get_width()) // 2
        screen.blit(oficina_texto, (oficina_texto_x, oficina_y + opcao_altura - 40))
        
        instrucoes = render_text("Use SETAS ou clique para escolher | ESC para cancelar", 16, (150, 150, 150), bold=False, pixel_style=True)
        instrucoes_x = caixa_x + (caixa_largura - instrucoes.get_width()) // 2
        screen.blit(instrucoes, (instrucoes_x, caixa_y + caixa_altura - 30))
        
        pygame.display.flip()
    
    return resultado

def mapa_cidade_loop(screen) -> Optional[str]:
    """
    Loop principal da tela do mapa da cidade
    Retorna o ID do território selecionado ou None se cancelado
    """
    clock = pygame.time.Clock()
    
    ZOOM_MAPA = 1.25
    offset_x_zoom = (LARGURA * ZOOM_MAPA - LARGURA) // 2
    offset_y_zoom = (ALTURA * ZOOM_MAPA - ALTURA) // 2
    
    arrastando = False
    mouse_inicio_x = 0
    mouse_inicio_y = 0
    offset_inicio_x = offset_x_zoom
    offset_inicio_y = offset_y_zoom
    
    caminho_cidade = obter_caminho_mapa_cidade()
    if os.path.exists(caminho_cidade):
        try:
            bg_raw = pygame.image.load(caminho_cidade).convert_alpha()
            bg_largura_zoom = int(LARGURA * ZOOM_MAPA)
            bg_altura_zoom = int(ALTURA * ZOOM_MAPA)
            bg_zoom = pygame.transform.scale(bg_raw, (bg_largura_zoom, bg_altura_zoom))
            bg_zoom_ref = bg_zoom
            mapa_carregado = True
        except Exception as e:
            print(f"Erro ao carregar mapa da cidade: {e}")
            mapa_carregado = False
            bg_zoom_ref = None
    else:
        mapa_carregado = False
        bg_zoom_ref = None
    
    render_text = _get_render_text()
    
    areas_mapa = carregar_areas_mapa()
    if not areas_mapa:
        print(f"AVISO: Nenhuma área carregada do mapa! Verifique {CAMINHO_AREAS_MAPA}")
    else:
        print(f"✓ {len(areas_mapa)} áreas do mapa carregadas")
    
    from config import obter_caminho_hover_dia_noite
    hover_sprites = {}
    for key, caminho in MAPEAMENTO_HOVER_SPRITES.items():
        caminho_hover = obter_caminho_hover_dia_noite(caminho)
        if os.path.exists(caminho_hover):
            try:
                sprite = pygame.image.load(caminho_hover).convert_alpha()
                hover_sprites[key] = sprite
            except Exception as e:
                print(f"Erro ao carregar sprite de hover {key}: {e}")
    
    area_hover = None
    territorio_selecionado: Optional[str] = None
    
    tempo_animacao = 0.0
    import math
    
    mapa_pausado = False
    opcao_pausa_selecionada = 0
    
    mostrar_mensagem_salvo = False
    tempo_mensagem_salvo = 0.0
    
    from config import obter_estado_dia_noite
    estado_dia_noite_anterior = obter_estado_dia_noite()
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        tempo_animacao += dt
        
        from core.tempo_jogo import gerenciador_tempo
        gerenciador_tempo.atualizar(dt)
        
        estado_dia_noite_atual = obter_estado_dia_noite()
        if estado_dia_noite_atual != estado_dia_noite_anterior:
            estado_dia_noite_anterior = estado_dia_noite_atual
            # Recarregar todos os hovers
            hover_sprites = {}
            for key, caminho in MAPEAMENTO_HOVER_SPRITES.items():
                caminho_hover = obter_caminho_hover_dia_noite(caminho)
                if os.path.exists(caminho_hover):
                    try:
                        sprite = pygame.image.load(caminho_hover).convert_alpha()
                        hover_sprites[key] = sprite
                    except Exception as e:
                        print(f"Erro ao recarregar sprite de hover {key}: {e}")
        
        # Atualizar mensagem de salvamento
        if mostrar_mensagem_salvo:
            tempo_mensagem_salvo += dt
            if tempo_mensagem_salvo >= 2.0:  # Mostrar por 2 segundos
                mostrar_mensagem_salvo = False
                tempo_mensagem_salvo = 0.0
        
        # Processar eventos
        eventos = pygame.event.get()
        for ev in eventos:
            if ev.type == pygame.QUIT:
                return None
            
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    # Alternar pause
                    mapa_pausado = not mapa_pausado
                    if mapa_pausado:
                        opcao_pausa_selecionada = 0
                elif mapa_pausado:
                    # Processar navegação no menu de pause
                    if ev.key in (pygame.K_UP, pygame.K_w):
                        opcao_pausa_selecionada = (opcao_pausa_selecionada - 1) % 4
                    elif ev.key in (pygame.K_DOWN, pygame.K_s):
                        opcao_pausa_selecionada = (opcao_pausa_selecionada + 1) % 4
                    elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        # Selecionar opção
                        if opcao_pausa_selecionada == 0:
                            # Continuar
                            mapa_pausado = False
                        elif opcao_pausa_selecionada == 1:
                            # Salvar
                            from core.progresso import gerenciador_progresso
                            gerenciador_progresso.salvar()
                            mostrar_mensagem_salvo = True
                            tempo_mensagem_salvo = 0.0
                            mapa_pausado = False
                        elif opcao_pausa_selecionada == 2:
                            # Opções (por enquanto, apenas continuar)
                            mapa_pausado = False
                        elif opcao_pausa_selecionada == 3:
                            # Menu principal
                            return None
            
            if ev.type == pygame.MOUSEMOTION:
                if not mapa_pausado:
                    mouse_x, mouse_y = ev.pos
                    
                    # Se estiver arrastando, atualizar offset
                    if arrastando:
                        delta_x = mouse_x - mouse_inicio_x
                        delta_y = mouse_y - mouse_inicio_y
                        offset_x_zoom = offset_inicio_x - delta_x
                        offset_y_zoom = offset_inicio_y - delta_y
                        
                        # Limitar offsets para não sair dos limites do mapa
                        offset_max_x = (LARGURA * ZOOM_MAPA - LARGURA)
                        offset_max_y = (ALTURA * ZOOM_MAPA - ALTURA)
                        offset_x_zoom = max(0, min(offset_x_zoom, offset_max_x))
                        offset_y_zoom = max(0, min(offset_y_zoom, offset_max_y))
                    else:
                        # Verificar hover nas áreas
                        area_hover = None
                        
                        for area in areas_mapa:
                            territorio_id = area.get("territorio_id") or area.get("id")
                            estado = gerenciador_localizacoes.obter_estado(territorio_id)
                            
                            # Filtrar áreas invisíveis do hover
                            if estado == EstadoLocalizacao.INVISIVEL:
                                continue
                            
                            # Verificar se está desbloqueada (compatibilidade)
                            if not area.get("desbloqueada", True) and estado != EstadoLocalizacao.DESBLOQUEADO:
                                continue
                            
                            # Ajustar coordenadas para o zoom e offset do mapa (acompanhar o mapa)
                            x = int(area.get("x", 0) * ZOOM_MAPA) - offset_x_zoom
                            y = int(area.get("y", 0) * ZOOM_MAPA) - offset_y_zoom
                            largura = int(area.get("largura", 0) * ZOOM_MAPA)
                            altura = int(area.get("altura", 0) * ZOOM_MAPA)
                            # Validar valores antes de verificar hover
                            if largura > 0 and altura > 0:
                                if x <= mouse_x <= x + largura and y <= mouse_y <= y + altura:
                                    area_hover = area
                                    break
            
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if mapa_pausado:
                    # Processar clique no menu de pause
                    mouse_x, mouse_y = ev.pos
                    caixa_largura = 500
                    caixa_altura = 400
                    caixa_x = (LARGURA - caixa_largura) // 2
                    caixa_y = (ALTURA - caixa_altura) // 2
                    
                    opcoes_pausa = [
                        ("CONTINUAR", "continuar"),
                        ("SALVAR", "salvar"),
                        ("OPÇÕES", "opcoes"),
                        ("MENU PRINCIPAL", "menu")
                    ]
                    
                    altura_total_opcoes = len(opcoes_pausa) * 60
                    offset_opcoes = caixa_y + caixa_altura - altura_total_opcoes - 20
                    
                    if caixa_x <= mouse_x <= caixa_x + caixa_largura and caixa_y <= mouse_y <= caixa_y + caixa_altura:
                        for i, (nome, chave) in enumerate(opcoes_pausa):
                            y_opcao = offset_opcoes + i * 60
                            opcao_rect = pygame.Rect(caixa_x + 20, y_opcao - 5, caixa_largura - 40, 60)
                            if opcao_rect.collidepoint(mouse_x, mouse_y):
                                if i == 0:
                                    # Continuar
                                    mapa_pausado = False
                                elif i == 1:
                                    # Salvar
                                    from core.progresso import gerenciador_progresso
                                    gerenciador_progresso.salvar()
                                    mostrar_mensagem_salvo = True
                                    tempo_mensagem_salvo = 0.0
                                    mapa_pausado = False
                                elif i == 2:
                                    # Opções (por enquanto, apenas continuar)
                                    mapa_pausado = False
                                elif i == 3:
                                    # Menu principal
                                    return None
                                break
                else:
                    mouse_x, mouse_y = ev.pos
                    
                    # Verificar se clicou em uma área primeiro
                    clicou_em_area = False
                    for area in areas_mapa:
                        # Verificar estado de desbloqueio usando gerenciador de localizações
                        territorio_id = area.get("territorio_id") or area.get("id")
                        estado = gerenciador_localizacoes.obter_estado(territorio_id)
                        
                        # Filtrar áreas invisíveis
                        if estado == EstadoLocalizacao.INVISIVEL:
                            continue
                        
                        # Verificar se está desbloqueada (compatibilidade)
                        if not area.get("desbloqueada", True) and estado != EstadoLocalizacao.DESBLOQUEADO:
                            continue
                        
                        # Ajustar coordenadas para o zoom e offset do mapa (acompanhar o mapa)
                        x = int(area.get("x", 0) * ZOOM_MAPA) - offset_x_zoom
                        y = int(area.get("y", 0) * ZOOM_MAPA) - offset_y_zoom
                        largura = int(area.get("largura", 0) * ZOOM_MAPA)
                        altura = int(area.get("altura", 0) * ZOOM_MAPA)
                        # Validar valores antes de verificar clique
                        if largura > 0 and altura > 0:
                            if x <= mouse_x <= x + largura and y <= mouse_y <= y + altura:
                                    # Verificar se é oficina - mostrar opção de escolha
                                    area_id_lower = area.get("id", "").lower()
                                    area_nome_lower = (area.get("nome", "") or "").lower()
                                    
                                    if "oficina" in area_id_lower or "oficina" in area_nome_lower or "garagem" in area_id_lower:
                                        # Mostrar menu de escolha entre casa e oficina
                                        escolha = mostrar_menu_casa_oficina(screen)
                                        if escolha == "casa":
                                            # Ir para casa (hub com fundo da casa)
                                            return "casa"
                                        elif escolha == "oficina":
                                            # Ir para oficina diretamente
                                            return "oficina"
                                        elif escolha is None:
                                            # Cancelou, não fazer nada
                                            clicou_em_area = True
                                            break
                                    else:
                                        # Tentar encontrar território correspondente
                                        territorio_id = area.get("territorio_id") or area.get("id")
                                        
                                        # Verificar estado da localização
                                        estado = gerenciador_localizacoes.obter_estado(territorio_id)
                                        
                                        if estado == EstadoLocalizacao.INVISIVEL:
                                            # Localização invisível - não fazer nada
                                            clicou_em_area = True
                                            break
                                        elif estado == EstadoLocalizacao.BLOQUEADO_VISIVEL:
                                            # Localização bloqueada - mostrar pensamento
                                            mensagem = gerenciador_localizacoes.obter_mensagem_bloqueado(territorio_id)
                                            if mensagem:
                                                # Salvar estado atual da tela
                                                tela_atual = screen.copy()
                                                mostrar_pensamento_jogador(screen, mensagem)
                                                # Restaurar tela
                                                screen.blit(tela_atual, (0, 0))
                                            clicou_em_area = True
                                            break
                                        elif estado == EstadoLocalizacao.DESBLOQUEADO:
                                            # Localização desbloqueada - permitir acesso
                                            territorio = obter_territorio(territorio_id) if territorio_id else None
                                            if territorio:
                                                territorio_selecionado = territorio.id
                                            else:
                                                # Se não encontrar território, usar o ID da área
                                                territorio_selecionado = area.get("id")
                                            return territorio_selecionado
                    
                    # Se não clicou em área, iniciar arrasto
                    if not clicou_em_area:
                        arrastando = True
                        mouse_inicio_x = mouse_x
                        mouse_inicio_y = mouse_y
                        offset_inicio_x = offset_x_zoom
                        offset_inicio_y = offset_y_zoom
            
            if ev.type == pygame.MOUSEBUTTONUP:
                if ev.button == 1:  # Botão esquerdo
                    arrastando = False
        
        # Desenhar fundo (redesenhar a cada frame para suportar arrasto)
        if mapa_carregado and bg_zoom_ref:
            bg = pygame.Surface((LARGURA, ALTURA))
            bg.fill((20, 20, 30))  # Fundo escuro
            bg.blit(bg_zoom_ref, (-offset_x_zoom, -offset_y_zoom))
        else:
            # Fallback: fundo escuro com grid
            bg = pygame.Surface((LARGURA, ALTURA))
            bg.fill((20, 20, 30))
            # Desenhar grid simples
            for x in range(0, LARGURA, 50):
                pygame.draw.line(bg, (40, 40, 50), (x, 0), (x, ALTURA), 1)
            for y in range(0, ALTURA, 50):
                pygame.draw.line(bg, (40, 40, 50), (0, y), (LARGURA, y), 1)
        
        screen.blit(bg, (0, 0))
        
        # Desenhar relógio digital no canto superior direito
        from core.hud import HUD
        if not hasattr(mapa_cidade_loop, '_hud_instance'):
            mapa_cidade_loop._hud_instance = HUD()
        mapa_cidade_loop._hud_instance.desenhar_relogio_digital(screen)
        
        # Desenhar áreas do mapa
        for area in areas_mapa:
            territorio_id = area.get("territorio_id") or area.get("id")
            
            # Verificar estado da localização
            estado = gerenciador_localizacoes.obter_estado(territorio_id)
            
            # Filtrar áreas invisíveis
            if estado == EstadoLocalizacao.INVISIVEL:
                continue  # Não desenhar áreas invisíveis
            
            # Verificar se está desbloqueada (compatibilidade com sistema antigo)
            if not area.get("desbloqueada", True) and estado != EstadoLocalizacao.DESBLOQUEADO:
                continue
            
            # Ajustar coordenadas para o zoom e offset do mapa (acompanhar o mapa)
            x = int(area.get("x", 0) * ZOOM_MAPA) - offset_x_zoom
            y = int(area.get("y", 0) * ZOOM_MAPA) - offset_y_zoom
            largura = int(area.get("largura", 0) * ZOOM_MAPA)
            altura = int(area.get("altura", 0) * ZOOM_MAPA)
            largura = max(1, largura)
            altura = max(1, altura)
            nome = area.get("nome", "Área") or "Área"
            
            # Verificar se a área está visível na tela antes de desenhar
            # (não desenhar se estiver completamente fora da tela)
            if x + largura < 0 or x > LARGURA or y + altura < 0 or y > ALTURA:
                continue  # Pular esta área se estiver completamente fora da tela
            
            # Tentar encontrar território correspondente para obter cor
            territorio = obter_territorio(territorio_id) if territorio_id else None
            
            # Cor baseada no tipo do território ou padrão
            if territorio:
                cores_tipo = {
                    "dinheiro_rapido": (200, 50, 50),
                    "pecas_brutas": (200, 150, 50),
                    "tecnica": (50, 150, 200),
                    "informacao": (150, 50, 200),
                    "progressao": (200, 200, 50)
                }
                cor_base = cores_tipo.get(territorio.tipo.value, (150, 150, 150))
            else:
                cor_base = (100, 150, 200)  # Cor padrão azul
            
            # Ajustar cor baseado no estado
            if estado == EstadoLocalizacao.BLOQUEADO_VISIVEL:
                # Área bloqueada - esmaecer cor e adicionar tom cinza
                cor_base = tuple(int(c * 0.5) for c in cor_base)  # 50% mais escuro
                cor_base = tuple(min(255, c + 50) for c in cor_base)  # Adicionar tom cinza
            
            # Efeito de hover (comparar por ID para evitar problemas de referência)
            area_id_atual = area.get("territorio_id") or area.get("id")
            area_hover_id = area_hover.get("territorio_id") or area_hover.get("id") if area_hover else None
            if area_hover and area_id_atual == area_hover_id:
                # Brilho pulsante no hover (menos intenso se bloqueado)
                pulso = 0.8 + 0.2 * abs(math.sin(tempo_animacao * 3.0))
                if estado == EstadoLocalizacao.BLOQUEADO_VISIVEL:
                    pulso = 0.7 + 0.1 * abs(math.sin(tempo_animacao * 3.0))  # Menos intenso
                cor = tuple(min(255, int(c * pulso)) for c in cor_base)
                # Borda mais espessa
                pygame.draw.rect(screen, cor, (x - 2, y - 2, largura + 4, altura + 4), 3)
            else:
                cor = cor_base
            
            # Calcular área visível para clipping (se a área está parcialmente fora da tela)
            x_visivel = max(0, x)
            y_visivel = max(0, y)
            x_fim = min(x + largura, LARGURA)
            y_fim = min(y + altura, ALTURA)
            largura_visivel = x_fim - x_visivel
            altura_visivel = y_fim - y_visivel
            
            # Desenhar área clicável (retângulo semi-transparente) apenas na parte visível
            if largura_visivel > 0 and altura_visivel > 0:
                overlay = pygame.Surface((largura_visivel, altura_visivel), pygame.SRCALPHA)
                overlay.fill((*cor, 80))  # 80/255 de opacidade
                screen.blit(overlay, (x_visivel, y_visivel))
                
                # Borda (desenhar apenas as partes visíveis)
                if x_visivel == x and y_visivel == y:
                    # Área completamente visível, desenhar borda normal
                    pygame.draw.rect(screen, cor, (x, y, largura, altura), 2)
                else:
                    # Área parcialmente visível, desenhar apenas as bordas visíveis
                    if x_visivel > 0:
                        pygame.draw.line(screen, cor, (x_visivel, y_visivel), (x_visivel, y_fim), 2)  # Esquerda
                    if y_visivel > 0:
                        pygame.draw.line(screen, cor, (x_visivel, y_visivel), (x_fim, y_visivel), 2)  # Superior
                    if x_fim < LARGURA:
                        pygame.draw.line(screen, cor, (x_fim, y_visivel), (x_fim, y_fim), 2)  # Direita
                    if y_fim < ALTURA:
                        pygame.draw.line(screen, cor, (x_visivel, y_fim), (x_fim, y_fim), 2)  # Inferior
            
            # Nome da área (só desenhar se estiver visível)
            if x_visivel >= 0 and y_visivel >= 0 and x_visivel < LARGURA and y_visivel < ALTURA:
                nome_texto = render_text(nome, 16, cor, bold=True, pixel_style=True)
                nome_x = x + (largura - nome_texto.get_width()) // 2
                nome_y = y + 5
                # Só desenhar o nome se estiver dentro da área visível
                if nome_x >= 0 and nome_y >= 0 and nome_x + nome_texto.get_width() < LARGURA and nome_y + nome_texto.get_height() < ALTURA:
                    screen.blit(nome_texto, (nome_x, nome_y))
                
                # Desenhar cadeado se estiver bloqueado
                if estado == EstadoLocalizacao.BLOQUEADO_VISIVEL:
                    # Desenhar símbolo de cadeado simples (retângulo com linha)
                    cadeado_tamanho = 20
                    cadeado_x = x + largura - cadeado_tamanho - 5
                    cadeado_y = y + 5
                    # Corpo do cadeado (retângulo)
                    pygame.draw.rect(screen, (150, 150, 150), (cadeado_x, cadeado_y + 8, cadeado_tamanho, cadeado_tamanho - 8), 2)
                    # Arco do cadeado (semicírculo)
                    pygame.draw.arc(screen, (150, 150, 150), (cadeado_x - 3, cadeado_y, cadeado_tamanho + 6, 16), 0, 3.14, 2)
        
        # Tooltip no hover
        if area_hover:
            territorio_id = area_hover.get("territorio_id") or area_hover.get("id")
            territorio = obter_territorio(territorio_id) if territorio_id else None
            estado = gerenciador_localizacoes.obter_estado(territorio_id)
            
            # Dimensões padrão do tooltip
            tooltip_largura = 300
            tooltip_altura = 100
            
            # Ajustar altura se estiver bloqueado (para mostrar mensagem)
            if estado == EstadoLocalizacao.BLOQUEADO_VISIVEL:
                tooltip_altura = 120

            # Desenhar tooltip (garantir que não saia da tela)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            tooltip_x = mouse_x + 20
            tooltip_y = mouse_y + 20
            
            # Ajustar posição se tooltip sair da tela
            if tooltip_x + tooltip_largura > LARGURA:
                tooltip_x = mouse_x - tooltip_largura - 20
            if tooltip_y + tooltip_altura > ALTURA:
                tooltip_y = mouse_y - tooltip_altura - 20
            
            # Garantir que não fique negativo
            tooltip_x = max(10, min(tooltip_x, LARGURA - tooltip_largura - 10))
            tooltip_y = max(10, min(tooltip_y, ALTURA - tooltip_altura - 10))
            
            # Fundo do tooltip
            tooltip_fundo = pygame.Surface((tooltip_largura, tooltip_altura), pygame.SRCALPHA)
            tooltip_fundo.fill((0, 0, 0, 220))
            screen.blit(tooltip_fundo, (tooltip_x, tooltip_y))
            pygame.draw.rect(screen, (255, 255, 255), (tooltip_x, tooltip_y, tooltip_largura, tooltip_altura), 2)
            
            # Texto do tooltip
            nome_tooltip = render_text(area_hover.get("nome", "Área"), 18, (255, 255, 255), bold=True, pixel_style=True)
            screen.blit(nome_tooltip, (tooltip_x + 10, tooltip_y + 10))
            
            # Se estiver bloqueado, mostrar indicador
            if estado == EstadoLocalizacao.BLOQUEADO_VISIVEL:
                bloqueado_texto = render_text("BLOQUEADO", 14, (200, 100, 100), bold=True, pixel_style=True)
                screen.blit(bloqueado_texto, (tooltip_x + 10, tooltip_y + 30))
                y_texto = tooltip_y + 50
            else:
                y_texto = tooltip_y + 35
            
            # Descrição (se houver território)
            if territorio:
                desc_palavras = territorio.descricao.split(' ')
                linha_atual = ""
                for palavra in desc_palavras:
                    teste_linha = linha_atual + (" " if linha_atual else "") + palavra
                    teste_render = render_text(teste_linha, 14, (200, 200, 200), bold=False, pixel_style=True)
                    if teste_render.get_width() <= tooltip_largura - 20:
                        linha_atual = teste_linha
                    else:
                        if linha_atual:
                            linha_render = render_text(linha_atual, 14, (200, 200, 200), bold=False, pixel_style=True)
                            screen.blit(linha_render, (tooltip_x + 10, y_texto))
                            y_texto += 20
                        linha_atual = palavra
                if linha_atual:
                    linha_render = render_text(linha_atual, 14, (200, 200, 200), bold=False, pixel_style=True)
                    screen.blit(linha_render, (tooltip_x + 10, y_texto))
        
        # Efeito de escurecimento do resto da tela quando houver hover
        if area_hover:
            # Obter área do hover com validação (ajustar para zoom e offset do mapa)
            area_x = int(area_hover.get("x", 0) * ZOOM_MAPA) - offset_x_zoom
            area_y = int(area_hover.get("y", 0) * ZOOM_MAPA) - offset_y_zoom
            area_largura = int(area_hover.get("largura", 0) * ZOOM_MAPA)
            area_altura = int(area_hover.get("altura", 0) * ZOOM_MAPA)
            
            # Calcular área visível na tela
            area_x_visivel = max(0, area_x)
            area_y_visivel = max(0, area_y)
            area_x_fim = min(area_x + area_largura, LARGURA)
            area_y_fim = min(area_y + area_altura, ALTURA)
            area_largura_visivel = max(0, area_x_fim - area_x_visivel)
            area_altura_visivel = max(0, area_y_fim - area_y_visivel)
            
            # Criar overlay escuro
            overlay_escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay_escuro.fill((0, 0, 0, 180))  # Preto com 180/255 de opacidade
            
            # Desenhar o overlay escuro em partes, deixando a área do hover clara
            # Usar coordenadas visíveis calculadas
            # Parte superior
            if area_y_visivel > 0:
                try:
                    parte_superior = overlay_escuro.subsurface((0, 0, LARGURA, area_y_visivel))
                    screen.blit(parte_superior, (0, 0))
                except (ValueError, pygame.error):
                    pass  # Ignorar erro se coordenadas inválidas
            
            # Parte inferior
            y_inferior = area_y_visivel + area_altura_visivel
            altura_inferior = ALTURA - y_inferior
            if altura_inferior > 0 and y_inferior < ALTURA:
                try:
                    parte_inferior = overlay_escuro.subsurface((0, y_inferior, LARGURA, altura_inferior))
                    screen.blit(parte_inferior, (0, y_inferior))
                except (ValueError, pygame.error):
                    pass
            
            # Parte esquerda
            if area_x_visivel > 0 and area_altura_visivel > 0:
                try:
                    parte_esquerda = overlay_escuro.subsurface((0, area_y_visivel, area_x_visivel, area_altura_visivel))
                    screen.blit(parte_esquerda, (0, area_y_visivel))
                except (ValueError, pygame.error):
                    pass
            
            # Parte direita
            x_direita = area_x_visivel + area_largura_visivel
            largura_direita = LARGURA - x_direita
            if largura_direita > 0 and x_direita < LARGURA and area_altura_visivel > 0:
                try:
                    parte_direita = overlay_escuro.subsurface((x_direita, area_y_visivel, largura_direita, area_altura_visivel))
                    screen.blit(parte_direita, (x_direita, area_y_visivel))
                except (ValueError, pygame.error):
                    pass
        
        # Desenhar sprites de hover (DEPOIS do tooltip e do overlay escuro)
        if area_hover:
            area_id = area_hover.get("territorio_id") or area_hover.get("id")
            area_id_lower = (area_id or "").lower()
            area_nome_lower = (area_hover.get("nome", "") or "").lower()
            
            # Verificar se há sprite de hover para esta área
            hover_sprite = None
            hover_key = None
            
            # Tentar encontrar sprite de hover por ID ou nome
            # Verificar cada palavra-chave no mapeamento
            texto_completo = f"{area_id_lower} {area_nome_lower}"
            for key in hover_sprites.keys():
                key_lower = key.lower()
                # Verificar se a palavra-chave está em qualquer parte do ID ou nome
                if key_lower in texto_completo:
                    # Verificar se precisa recarregar (mudança dia/noite)
                    caminho_original = MAPEAMENTO_HOVER_SPRITES.get(key)
                    if caminho_original:
                        caminho_hover = obter_caminho_hover_dia_noite(caminho_original)
                        if os.path.exists(caminho_hover):
                            try:
                                hover_sprite = pygame.image.load(caminho_hover).convert_alpha()
                                hover_sprites[key] = hover_sprite  # Atualizar cache
                            except Exception as e:
                                print(f"Erro ao recarregar sprite de hover {key}: {e}")
                                hover_sprite = hover_sprites.get(key)  # Usar cache se falhar
                        else:
                            hover_sprite = hover_sprites.get(key)  # Usar cache se não existir
                    else:
                        hover_sprite = hover_sprites.get(key)  # Usar cache
                    hover_key = key
                    break
            
            # Desenhar sprite de hover com animação de salto
            if hover_sprite:
                # Ajustar coordenadas para o zoom e offset do mapa (acompanhar o mapa)
                area_x = int(area_hover.get("x", 0) * ZOOM_MAPA) - offset_x_zoom
                area_y = int(area_hover.get("y", 0) * ZOOM_MAPA) - offset_y_zoom
                area_largura = int(area_hover.get("largura", 0) * ZOOM_MAPA)
                area_altura = int(area_hover.get("altura", 0) * ZOOM_MAPA)
                
                # Animação de salto (movimento vertical) - mais suave
                # Reduzir velocidade de 4.0 para 2.0 para movimento mais suave
                offset_salto = -15 * abs(math.sin(tempo_animacao * 2.0))  # Salta até 15 pixels para cima
                
                # Calcular posição central da área
                centro_x = area_x + area_largura // 2
                centro_y = area_y + area_altura // 2
                
                # Redimensionar sprite
                sprite_w, sprite_h = hover_sprite.get_size()
                # Validar tamanhos antes de calcular escala
                if sprite_w > 0 and sprite_h > 0 and area_largura > 0 and area_altura > 0:
                    # Obter escala individual para este hover
                    # Tentar encontrar a escala correspondente usando o hover_key ou texto completo
                    multiplicador_escala = None
                    texto_busca = f"{area_id_lower} {area_nome_lower}"
                    
                    # Primeiro, tentar com a chave exata
                    if hover_key and hover_key in ESCALAS_HOVER:
                        multiplicador_escala = ESCALAS_HOVER[hover_key]
                    else:
                        # Se não encontrou, buscar por correspondência no texto completo
                        for escala_key in ESCALAS_HOVER.keys():
                            if escala_key.lower() in texto_busca:
                                multiplicador_escala = ESCALAS_HOVER[escala_key]
                                break
                    
                    # Se ainda não encontrou, usar padrão
                    if multiplicador_escala is None:
                        multiplicador_escala = 2.6
                    
                    # Calcular escala baseada no multiplicador
                    # O multiplicador agora representa o tamanho desejado em relação à área
                    # Exemplo: multiplicador_escala = 2.0 significa que o sprite será 2x maior que a área
                    # Calcular o tamanho desejado do sprite
                    tamanho_desejado_largura = area_largura * multiplicador_escala
                    tamanho_desejado_altura = area_altura * multiplicador_escala
                    
                    # Calcular a escala necessária para atingir esse tamanho
                    escala_largura = tamanho_desejado_largura / sprite_w if sprite_w > 0 else 1.0
                    escala_altura = tamanho_desejado_altura / sprite_h if sprite_h > 0 else 1.0
                    
                    # Usar a menor escala para manter proporção
                    escala = min(escala_largura, escala_altura)
                    
                    # Garantir um mínimo para visibilidade
                    escala = max(0.1, escala)
                else:
                    escala = 1.0
                sprite_redimensionado = pygame.transform.scale(
                    hover_sprite, 
                    (int(sprite_w * escala), int(sprite_h * escala))
                )
                
                # Posicionar sprite centralizado na área, com offset de salto
                sprite_x = centro_x - sprite_redimensionado.get_width() // 2
                sprite_y = centro_y - sprite_redimensionado.get_height() // 2 + int(offset_salto)
                
                # Desenhar sprite de hover (sobreposto a tudo)
                screen.blit(sprite_redimensionado, (sprite_x, sprite_y))
        
        # Instruções
        if not mapa_pausado:
            instrucoes = render_text("Clique em um território para viajar | ESC para pausar", 14, (150, 150, 150), bold=False, pixel_style=True)
            screen.blit(instrucoes, (10, ALTURA - 30))
        
        # Desenhar menu de pause
        if mapa_pausado:
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            caixa_largura = 500
            caixa_altura = 400
            caixa_x = (LARGURA - caixa_largura) // 2
            caixa_y = (ALTURA - caixa_altura) // 2
            
            caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
            caixa_fundo.fill((0, 0, 0, 200))
            screen.blit(caixa_fundo, (caixa_x, caixa_y))
            pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
            
            titulo_texto = render_text("JOGO PAUSADO", 48, (255, 255, 255), bold=True, pixel_style=True)
            titulo_x = caixa_x + (caixa_largura - titulo_texto.get_width()) // 2
            screen.blit(titulo_texto, (titulo_x, caixa_y + 20))
            
            opcoes_pausa = [
                ("CONTINUAR", "continuar"),
                ("SALVAR", "salvar"),
                ("OPÇÕES", "opcoes"),
                ("MENU PRINCIPAL", "menu")
            ]
            
            altura_total_opcoes = len(opcoes_pausa) * 60
            offset_opcoes = caixa_y + caixa_altura - altura_total_opcoes - 20
            
            # Animações de hover
            if not hasattr(mapa_cidade_loop, '_hover_animation_pause'):
                mapa_cidade_loop._hover_animation_pause = [0.0] * len(opcoes_pausa)
            
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_in_caixa = (caixa_x <= mouse_x <= caixa_x + caixa_largura and
                            caixa_y <= mouse_y <= caixa_y + caixa_altura)
            
            hover_speed = 8.0
            opcao_hover = -1
            if mouse_in_caixa:
                for i, (nome, chave) in enumerate(opcoes_pausa):
                    y_opcao = offset_opcoes + i * 60
                    opcao_rect = pygame.Rect(caixa_x + 20, y_opcao - 5, caixa_largura - 40, 60)
                    if opcao_rect.collidepoint(mouse_x, mouse_y):
                        opcao_hover = i
                        break
            
            for i in range(len(opcoes_pausa)):
                if i == opcao_hover or i == opcao_pausa_selecionada:
                    mapa_cidade_loop._hover_animation_pause[i] = min(1.0, mapa_cidade_loop._hover_animation_pause[i] + hover_speed * dt)
                else:
                    mapa_cidade_loop._hover_animation_pause[i] = max(0.0, mapa_cidade_loop._hover_animation_pause[i] - hover_speed * dt)
            
            if not mouse_in_caixa:
                for i in range(len(opcoes_pausa)):
                    if i != opcao_pausa_selecionada:
                        mapa_cidade_loop._hover_animation_pause[i] = max(0.0, mapa_cidade_loop._hover_animation_pause[i] - hover_speed * dt * 1.5)
            
            # Desenhar opções
            for i, (nome, chave) in enumerate(opcoes_pausa):
                y_opcao = offset_opcoes + i * 60
                hover_progress = mapa_cidade_loop._hover_animation_pause[i]
                
                # Determinar cor baseado no estado
                if i == opcao_pausa_selecionada:
                    cor = (255, 255, 255)
                    # Desenhar cursor do controle
                    cursor_rect = pygame.Rect(caixa_x + 20, y_opcao - 5, caixa_largura - 40, 60)
                    pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                    cursor_alpha = int(128 + 127 * abs(math.sin(tempo_animacao * 3.0)))
                    cursor_surface = pygame.Surface((cursor_rect.width, cursor_rect.height), pygame.SRCALPHA)
                    cursor_surface.fill((0, 200, 255, cursor_alpha // 4))
                    screen.blit(cursor_surface, cursor_rect.topleft)
                elif hover_progress > 0.1:
                    cor = (200, 200, 255)
                else:
                    cor = (150, 150, 150)
                
                # Desenhar efeito de hover se aplicável
                if hover_progress > 0 and i != opcao_pausa_selecionada:
                    hover_alpha = int(30 * hover_progress)
                    hover_rect = pygame.Rect(caixa_x + 20, y_opcao - 5, caixa_largura - 40, 60)
                    hover_surface = pygame.Surface((hover_rect.width, hover_rect.height), pygame.SRCALPHA)
                    hover_surface.fill((0, 200, 255, hover_alpha))
                    screen.blit(hover_surface, hover_rect.topleft)
                
                # Desenhar texto da opção
                opcao_texto = render_text(nome, 32, cor, bold=True, pixel_style=True)
                opcao_x = caixa_x + (caixa_largura - opcao_texto.get_width()) // 2
                screen.blit(opcao_texto, (opcao_x, y_opcao))
        
        # Desenhar mensagem de salvamento
        if mostrar_mensagem_salvo:
            render_text = _get_render_text()
            mensagem = render_text("JOGO SALVO!", 36, (0, 255, 0), bold=True, pixel_style=True)
            mensagem_x = (LARGURA - mensagem.get_width()) // 2
            mensagem_y = 100
            
            # Fundo semi-transparente
            fundo_mensagem = pygame.Surface((mensagem.get_width() + 40, mensagem.get_height() + 20), pygame.SRCALPHA)
            fundo_mensagem.fill((0, 0, 0, 180))
            screen.blit(fundo_mensagem, (mensagem_x - 20, mensagem_y - 10))
            
            screen.blit(mensagem, (mensagem_x, mensagem_y))
        
        # Desenhar missão ativa no canto superior direito (se houver)
        try:
            from core.hud import HUD
            if not hasattr(mapa_cidade_loop, '_hud_instance'):
                mapa_cidade_loop._hud_instance = HUD()
            mapa_cidade_loop._hud_instance.desenhar_missao_ativa(screen, posicao=(LARGURA - 20, 10), alinhar_direita=True)
        except:
            pass
            
        pygame.display.flip()

