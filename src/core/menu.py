import os
import sys
import pygame
from enum import Enum

# Adicionar o diretório pai ao path para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import LARGURA, ALTURA, FPS, CAMINHO_MENU, CONFIGURACOES, MAPAS_DISPONIVEIS
import main
from core.musica import gerencIAdor_musica
from core.popup_musica import popup_musica
from core.game_modes import ModoJogo, TipoJogo

def scale_to_cover(img_surf, target_w, target_h):
    iw, ih = img_surf.get_size()
    scale = max(target_w/iw, target_h/ih)
    surf = pygame.transform.smoothscale(img_surf, (int(iw*scale), int(ih*scale)))
    x = (surf.get_width() - target_w) // 2
    y = (surf.get_height() - target_h) // 2
    return surf.subsurface((x, y, target_w, target_h)).copy()

def ponto_dentro_ret(mouse_x, mouse_y, rect: pygame.Rect) -> bool:
    return rect.collidepoint(mouse_x, mouse_y)

def verificar_clique_opcao(mouse_x, mouse_y, opcoes, caixa_x, caixa_y, caixa_largura, altura_item=50, offset_y=80, opcao_largura=None, scroll_offset=0):
    """Verifica se o mouse clicou em alguma opção e retorna o índice"""
    for i, (nome, chave) in enumerate(opcoes):
        if opcao_largura is None:
            # Layout padrão para submenus
            y = caixa_y + offset_y + i * altura_item - scroll_offset
            opcao_rect = pygame.Rect(caixa_x + 20, y - 5, caixa_largura - 40, altura_item)
        else:
            # Layout para menu de opções principal
            opcao_x = caixa_x + (caixa_largura - opcao_largura) // 2
            opcao_y_inicial = caixa_y + 20 + 48 + 10 + 40  # titulo_y + titulo_height + 10 + 40
            opcao_y = opcao_y_inicial + i * (altura_item + 15) - scroll_offset  # altura_item + espacamento
            opcao_rect = pygame.Rect(opcao_x, opcao_y, opcao_largura, altura_item)
        
        if opcao_rect.collidepoint(mouse_x, mouse_y):
            return i
    return -1

def desenhar_scrollbar(screen, scroll_offset, max_scroll, caixa_x, caixa_y, caixa_largura, caixa_altura):
    """Desenha uma barra de rolagem"""
    if max_scroll <= 0:
        return
    
    # Calcular posição e tamanho da barra
    scrollbar_width = 12
    scrollbar_x = caixa_x + caixa_largura - scrollbar_width - 5
    scrollbar_y = caixa_y + 80
    scrollbar_height = caixa_altura - 200  # Altura da área de opções (deixando espaço para o botão voltar)
    
    # Calcular posição do indicador
    scroll_ratio = scroll_offset / max_scroll if max_scroll > 0 else 0
    indicator_height = max(30, int(scrollbar_height * 0.3))  # 30% da altura da barra
    indicator_y = scrollbar_y + int(scroll_ratio * (scrollbar_height - indicator_height))
    
    # Desenhar fundo da barra (semi-transparente)
    scrollbar_bg = pygame.Surface((scrollbar_width, scrollbar_height), pygame.SRCALPHA)
    scrollbar_bg.fill((50, 50, 50, 150))
    screen.blit(scrollbar_bg, (scrollbar_x, scrollbar_y))
    
    # Desenhar indicador
    indicator_bg = pygame.Surface((scrollbar_width - 2, indicator_height), pygame.SRCALPHA)
    indicator_bg.fill((150, 150, 150, 200))
    screen.blit(indicator_bg, (scrollbar_x + 1, indicator_y))
    
    # Borda da barra
    pygame.draw.rect(screen, (255, 255, 255), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height), 1)

def render_text(text, size, color=(255,255,255), bold=True, pixel_style=True):
    pygame.font.init()
    
    if pixel_style:
        # Usar fonte pixel art para estilo retrô/synthwave
        try:
            # Tentar carregar fonte pixel art
            font = pygame.font.Font("assets/fonts/pixel_font.ttf", size)
        except:
            try:
                # Fallback para fonte pixel art do sistema
                font = pygame.font.Font("assets/fonts/retro_font.ttf", size)
            except:
                # Fallback final: usar fonte monospace com estilo pixel
                font = pygame.font.SysFont("consolas", size, bold=bold)
    else:
        font = pygame.font.SysFont("arIAl", size, bold=bold)
    
    # Renderizar texto com contorno para estilo pixel art
    if pixel_style and size >= 24:
        # CrIAr contorno preto para texto grande
        text_surface = font.render(text, True, color)
        outline_surface = font.render(text, True, (0, 0, 0))
        
        # CrIAr superfície maior para o contorno
        final_surface = pygame.Surface((text_surface.get_width() + 4, text_surface.get_height() + 4), pygame.SRCALPHA)
        
        # Desenhar contorno (4 posições)
        for dx in [-2, 0, 2]:
            for dy in [-2, 0, 2]:
                if dx != 0 or dy != 0:
                    final_surface.blit(outline_surface, (2 + dx, 2 + dy))
        
        # Desenhar texto principal
        final_surface.blit(text_surface, (2, 2))
        
        return final_surface
    else:
        return font.render(text, True, color)

class Escolha(Enum):
    JOGAR = 0
    SELECIONAR_CARROS = 1
    SELECIONAR_MAPAS = 2
    OPCOES = 3
    SAIR = 4

def menu_loop(screen) -> Escolha:
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)

    itens = ["JOGAR", "SELECIONAR CARROS", "SELECIONAR MAPAS", "OPÇÕES", "SAIR"]
    idx = 0
    clock = pygame.time.Clock()

    # posições dos botões (layout horizontal na parte inferior)
    base_y = int(ALTURA * 0.85)
    botao_largura = 230
    botao_altura = 60  
    espacamento = 20
    total_largura = len(itens) * botao_largura + (len(itens) - 1) * espacamento
    base_x = (LARGURA - total_largura) // 2  # Centralizar horizontalmente
    
    # Variáveis para animação de hover dos botões
    hover_animation = [0.0] * len(itens)  # Progresso da animação para cada botão
    hover_speed = 3.0  # Velocidade da animação de hover

    while True:
        dt = clock.tick(FPS) / 1000.0  # Converter para segundos
        
        # Atualizar música
        gerencIAdor_musica.verificar_fim_musica()
        popup_musica.atualizar(dt)
        
        # Verificar hover do pop-up
        mouse_x, mouse_y = pygame.mouse.get_pos()
        popup_musica.verificar_hover(mouse_x, mouse_y)
        
        # Atualizar animação de hover dos botões
        for i in range(len(itens)):
            tx = base_x + i * (botao_largura + espacamento)
            ty = base_y
            rect = pygame.Rect(tx, ty, botao_largura, botao_altura)
            is_hovering = rect.collidepoint(mouse_x, mouse_y)
            
            if is_hovering:
                # Aumentar progresso da animação
                hover_animation[i] = min(1.0, hover_animation[i] + hover_speed * dt)
            else:
                # Diminuir progresso da animação
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt)
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return Escolha.SAIR
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_LEFT, pygame.K_a):
                    idx = (idx - 1) % len(itens)
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    idx = (idx + 1) % len(itens)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return Escolha(idx)
                elif ev.key == pygame.K_ESCAPE:
                    return Escolha.SAIR
                elif ev.key == pygame.K_m:
                    # Próxima música
                    gerencIAdor_musica.proxima_musica()
                    if gerencIAdor_musica.musica_tocando:
                        popup_musica.mostrar(gerencIAdor_musica.obter_nome_musica_atual())
                elif ev.key == pygame.K_n:
                    # Música anterior
                    gerencIAdor_musica.musica_anterior()
                    if gerencIAdor_musica.musica_tocando:
                        popup_musica.mostrar(gerencIAdor_musica.obter_nome_musica_atual())
            if ev.type == pygame.MOUSEMOTION:
                mx, my = ev.pos
                # detecta hover do mouse nas opções (layout horizontal)
                for i in range(len(itens)):
                    tx = base_x + i * (botao_largura + espacamento)
                    ty = base_y
                    rect = pygame.Rect(tx, ty, botao_largura, botao_altura)
                    if rect.collidepoint(mx, my):
                        idx = i
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # Verificar clique no pop-up de música primeiro
                clique_popup = popup_musica.verificar_clique(ev.pos[0], ev.pos[1])
                if clique_popup == "anterior":
                    gerencIAdor_musica.musica_anterior()
                    if gerencIAdor_musica.musica_tocando:
                        popup_musica.mostrar(gerencIAdor_musica.obter_nome_musica_atual())
                elif clique_popup == "proximo":
                    gerencIAdor_musica.proxima_musica()
                    if gerencIAdor_musica.musica_tocando:
                        popup_musica.mostrar(gerencIAdor_musica.obter_nome_musica_atual())
                else:
                    # Se não clicou no popup, verificar se clicou em algum botão
                    mouse_x, mouse_y = ev.pos
                    for i, txt in enumerate(itens):
                        x = base_x + i * (botao_largura + espacamento)
                        y = base_y
                        botao_rect = pygame.Rect(x, y, botao_largura, botao_altura)
                        if botao_rect.collidepoint(mouse_x, mouse_y):
                            return Escolha(i)

        # desenha
        screen.blit(bg, (0, 0))

        # Botões do menu - layout horizontal na parte inferior
        for i, txt in enumerate(itens):
            sel = (i == idx)
            hover_progress = hover_animation[i]  # Progresso da animação de hover (0.0 a 1.0)
            
            # Posição do botão
            x = base_x + i * (botao_largura + espacamento)
            y = base_y
            
            # Cores base do botão
            if sel:
                # Botão selecionado (teclado)
                base_cor_fundo = (0, 150, 255, 120)  # Azul cIAno vibrante
                base_cor_borda = (0, 200, 255)  # Borda azul cIAno
                base_cor_texto = (255, 255, 255)  # Texto branco
            else:
                # Botão normal
                base_cor_fundo = (0, 0, 0, 150)  # Preto semi-transparente
                base_cor_borda = (255, 255, 255)  # Borda branca
                base_cor_texto = (255, 255, 255)  # Texto branco
            
            # Aplicar animação de hover
            if hover_progress > 0:
                # Cores de hover (azul cIAno vibrante)
                hover_cor_fundo = (0, 150, 255, 120)  # Azul cIAno
                hover_cor_borda = (0, 200, 255)  # Borda azul cIAno
                hover_cor_texto = (255, 255, 255)  # Texto branco
                
                # Interpolar entre cores base e hover
                cor_fundo = (
                    int(base_cor_fundo[0] + (hover_cor_fundo[0] - base_cor_fundo[0]) * hover_progress),
                    int(base_cor_fundo[1] + (hover_cor_fundo[1] - base_cor_fundo[1]) * hover_progress),
                    int(base_cor_fundo[2] + (hover_cor_fundo[2] - base_cor_fundo[2]) * hover_progress),
                    int(base_cor_fundo[3] + (hover_cor_fundo[3] - base_cor_fundo[3]) * hover_progress)
                )
                cor_borda = (
                    int(base_cor_borda[0] + (hover_cor_borda[0] - base_cor_borda[0]) * hover_progress),
                    int(base_cor_borda[1] + (hover_cor_borda[1] - base_cor_borda[1]) * hover_progress),
                    int(base_cor_borda[2] + (hover_cor_borda[2] - base_cor_borda[2]) * hover_progress)
                )
                cor_texto = (
                    int(base_cor_texto[0] + (hover_cor_texto[0] - base_cor_texto[0]) * hover_progress),
                    int(base_cor_texto[1] + (hover_cor_texto[1] - base_cor_texto[1]) * hover_progress),
                    int(base_cor_texto[2] + (hover_cor_texto[2] - base_cor_texto[2]) * hover_progress)
                )
            else:
                cor_fundo = base_cor_fundo
                cor_borda = base_cor_borda
                cor_texto = base_cor_texto
            
            # Efeito de escala suave no hover
            scale_factor = 1.0 + (hover_progress * 0.05)  # Aumenta até 5% no hover
            scaled_width = int(botao_largura * scale_factor)
            scaled_height = int(botao_altura * scale_factor)
            offset_x = (scaled_width - botao_largura) // 2
            offset_y = (scaled_height - botao_altura) // 2
            
            # Desenhar fundo do botão com escala
            botao_fundo = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
            botao_fundo.fill(cor_fundo)
            screen.blit(botao_fundo, (x - offset_x, y - offset_y))
            
            # Desenhar borda do botão com escala
            pygame.draw.rect(screen, cor_borda, (x - offset_x, y - offset_y, scaled_width, scaled_height), 3)
            
            # Desenhar texto do botão centralizado
            texto_surface = render_text(txt, 20, cor_texto, bold=True, pixel_style=True)
            texto_x = x + (botao_largura - texto_surface.get_width()) // 2
            texto_y = y + (botao_altura - texto_surface.get_height()) // 2
            screen.blit(texto_surface, (texto_x, texto_y))
            
            # Efeito de glow no hover
            if hover_progress > 0:
                glow_intensity = int(30 * hover_progress)
                glow_surface = pygame.Surface((scaled_width + 10, scaled_height + 10), pygame.SRCALPHA)
                glow_surface.fill((0, 200, 255, glow_intensity))  # Glow azul cIAno
                screen.blit(glow_surface, (x - offset_x - 5, y - offset_y - 5))
            
            if sel:
                # Efeito de brilho/glow sob o botão ativo (teclado)
                glow_surface = pygame.Surface((botao_largura + 10, botao_altura + 10), pygame.SRCALPHA)
                glow_surface.fill((0, 200, 255, 30))  # Glow azul cIAno suave
                screen.blit(glow_surface, (x - 5, y - 5))

        # Desenhar pop-up de música
        popup_musica.desenhar(screen)
        
        pygame.display.flip()

def selecionar_mapas_loop(screen):
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)
    
    mapas = list(MAPAS_DISPONIVEIS.keys())
    indice = 0
    relogio = pygame.time.Clock()
    
    base_x = int(LARGURA * 0.10)
    base_y = int(ALTURA * 0.30)
    passo = 60
    
    while True:
        dt = relogio.tick(FPS) / 1000.0
        
        gerencIAdor_musica.verificar_fim_musica()
        popup_musica.atualizar(dt)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_UP:
                    indice = (indice - 1) % len(mapas)
                elif event.key == pygame.K_DOWN:
                    indice = (indice + 1) % len(mapas)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    mapa_selecionado = mapas[indice]
                    main.principal(mapa_selecionado=mapa_selecionado)
                    return None
                elif event.key == pygame.K_m:
                    # Próxima música
                    gerencIAdor_musica.proxima_musica()
                    if gerencIAdor_musica.musica_tocando:
                        popup_musica.mostrar(gerencIAdor_musica.obter_nome_musica_atual())
        
        screen.blit(bg, (0, 0))
        
        titulo = render_text("SELECIONAR MAPA", 56, (255, 100, 255), bold=True, pixel_style=True)
        titulo_x = (LARGURA - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, base_y - 100))
        
        for i, mapa_id in enumerate(mapas):
            mapa_info = MAPAS_DISPONIVEIS[mapa_id]
            nome_mapa = mapa_info["nome"]
            
            if i == indice:
                cor = (255, 100, 255)  # Magenta vibrante
                tamanho = 42
            else:
                cor = (100, 200, 255)  # Azul cIAno
                tamanho = 36
            
            texto = render_text(nome_mapa, tamanho, cor, bold=True, pixel_style=True)
            screen.blit(texto, (base_x, base_y + i * passo))
        
        # Instruções removidas
        
        popup_musica.desenhar(screen)
        
        pygame.display.flip()

def selecionar_carros_loop(screen):
    from config import CAMINHO_OFICINA, DIR_SPRITES, DIR_CAR_SELECTION
    bg_raw = pygame.image.load(CAMINHO_OFICINA).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)
    
    # Importar a lista de carros do main
    from main import CARROS_DISPONIVEIS
    
    carro_p1 = 0
    carro_p2 = 0
    fase_selecao = 1  # 1 = P1 selecionando, 2 = P2 selecionando, 3 = confirmando
    
    # Variáveis para transição
    transicao_ativa = False
    transicao_tempo = 0.0
    transicao_duracao = 0.8  # 800ms - mais lenta
    transicao_direcao = 1  # 1 = direita para esquerda, -1 = esquerda para direita
    carro_atual_pos = 0.0  # Posição X do carro atual (0 = centro)
    carro_proximo_pos = 1.0  # Posição X do próximo carro (1 = fora da tela direita)
    carro_anterior = None  # Carro que estava sendo exibido antes da transição
    
    # Carregar sprites dos carros para seleção (usando pasta car_selection)
    sprites_carros = {}
    for carro in CARROS_DISPONIVEIS:
        try:
            # Primeiro tenta carregar da pasta car_selection
            sprite_path = os.path.join(DIR_CAR_SELECTION, f"{carro['sprite_selecao']}.png")
            if not os.path.exists(sprite_path):
                # Se não existir, usa o sprite normal
                sprite_path = os.path.join(DIR_SPRITES, f"{carro['prefixo_cor']}.png")
            
            sprite = pygame.image.load(sprite_path).convert_alpha()
            # Usar tamanho e posição individuais para cada carro
            tamanho_oficina = carro.get('tamanho_oficina', (600, 300))  # Padrão se não especificado
            canvas_largura, canvas_altura = tamanho_oficina
            sprite_original = sprite
            
            # Calcular escala para manter proporção e ajustar ao tamanho individual
            escala_x = canvas_largura / sprite_original.get_width()
            escala_y = canvas_altura / sprite_original.get_height()
            escala = min(escala_x, escala_y)  # Usar a menor escala para manter proporção
            
            # Redimensionar mantendo proporção
            nova_largura = int(sprite_original.get_width() * escala)
            nova_altura = int(sprite_original.get_height() * escala)
            sprite_redimensionado = pygame.transform.scale(sprite_original, (nova_largura, nova_altura))
            
            # CrIAr canvas com tamanho individual
            sprite = pygame.Surface((canvas_largura, canvas_altura), pygame.SRCALPHA)
            
            # Centralizar horizontalmente e posicionar na parte inferior (encostado no chão)
            x_offset = (canvas_largura - nova_largura) // 2
            y_offset = canvas_altura - nova_altura - 5  # Posicionar mais baixo, quase no chão
            sprite.blit(sprite_redimensionado, (x_offset, y_offset))
            
            sprites_carros[carro['prefixo_cor']] = sprite
        except:
            # Se não conseguir carregar, crIAr um retângulo como fallback
            tamanho_oficina = carro.get('tamanho_oficina', (600, 300))
            sprite = pygame.Surface(tamanho_oficina, pygame.SRCALPHA)
            pygame.draw.rect(sprite, (100, 100, 100), (0, 0, tamanho_oficina[0], tamanho_oficina[1]))
            sprites_carros[carro['prefixo_cor']] = sprite
    
    def inicIAr_transicao(direcao, carro_atual_idx):
        """InicIA uma transição entre carros"""
        nonlocal transicao_ativa, transicao_tempo, transicao_direcao, carro_atual_pos, carro_proximo_pos, carro_anterior
        transicao_ativa = True
        transicao_tempo = 0.0
        transicao_direcao = direcao
        carro_anterior = carro_atual_idx  # Armazenar carro anterior
        carro_atual_pos = 0.0
        carro_proximo_pos = direcao  # 1 = direita, -1 = esquerda
    
    def atualizar_transicao(dt):
        """Atualiza a animação de transição"""
        nonlocal transicao_ativa, transicao_tempo, carro_atual_pos, carro_proximo_pos
        
        if not transicao_ativa:
            return
        
        transicao_tempo += dt
        
        if transicao_tempo >= transicao_duracao:
            # Transição completa
            transicao_ativa = False
            carro_atual_pos = 0.0
            carro_proximo_pos = 1.0
        else:
            # Interpolação suave (ease-in-out)
            progresso = transicao_tempo / transicao_duracao
            # Ease-in-out cubic para movimento mais natural
            if progresso < 0.5:
                progresso = 4 * progresso * progresso * progresso
            else:
                progresso = 1 - pow(-2 * progresso + 2, 3) / 2
            
            # Carro atual sai pela direção oposta
            carro_atual_pos = -transicao_direcao * progresso
            # Próximo carro entra pela direção oposta
            carro_proximo_pos = transicao_direcao * (1 - progresso)
    
    clock = pygame.time.Clock()
    
    while True:
        dt = clock.tick(FPS) / 1000.0  # Converter para segundos
        
        # Atualizar transição
        atualizar_transicao(dt)
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return None, None
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return None, None
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    if not transicao_ativa:  # Só permite navegação se não estiver em transição
                        if fase_selecao == 1:
                            inicIAr_transicao(-1, carro_p1)  # Esquerda para direita
                            carro_p1 = (carro_p1 - 1) % len(CARROS_DISPONIVEIS)
                        elif fase_selecao == 2:
                            inicIAr_transicao(-1, carro_p2)  # Esquerda para direita
                            carro_p2 = (carro_p2 - 1) % len(CARROS_DISPONIVEIS)
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    if not transicao_ativa:  # Só permite navegação se não estiver em transição
                        if fase_selecao == 1:
                            inicIAr_transicao(1, carro_p1)  # Direita para esquerda
                            carro_p1 = (carro_p1 + 1) % len(CARROS_DISPONIVEIS)
                        elif fase_selecao == 2:
                            inicIAr_transicao(1, carro_p2)  # Direita para esquerda
                            carro_p2 = (carro_p2 + 1) % len(CARROS_DISPONIVEIS)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if not transicao_ativa:  # Só permite confirmação se não estiver em transição
                        if fase_selecao == 1:
                            fase_selecao = 2  # P1 confirmou, vai para P2
                        elif fase_selecao == 2:
                            return carro_p1, carro_p2  # P2 confirmou, retorna seleções
        
        # Desenhar
        screen.blit(bg, (0, 0))
        
        # Overlay escuro sutil
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        screen.blit(overlay, (0, 0))
        
        # Título - estilo pixel art
        titulo = render_text("OFICINA", 48, (255, 100, 255), bold=True, pixel_style=True)
        titulo_x = (LARGURA - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, 20))
        
        if fase_selecao == 1:
            # FASE 1: Player 1 selecionando
            subtitulo = render_text("JOGADOR 1 - ESCOLHA SEU CARRO", 32, (100, 200, 255), bold=True, pixel_style=True)
            subtitulo_x = (LARGURA - subtitulo.get_width()) // 2
            screen.blit(subtitulo, (subtitulo_x, 50))
            
            # Instruções
            instrucoes = render_text("← → navegar | ENTER confirmar | ESC voltar", 20, (255, 255, 255), bold=True, pixel_style=True)
            instrucoes_x = (LARGURA - instrucoes.get_width()) // 2
            screen.blit(instrucoes, (instrucoes_x, 80))
            
            # Carro selecionado P1 - Grande e centralizado
            if transicao_ativa:
                # Durante transição: desenhar carro anterior saindo e novo carro entrando
                carro_anterior_obj = CARROS_DISPONIVEIS[carro_anterior]
                carro_atual_obj = CARROS_DISPONIVEIS[carro_p1]
                sprite_anterior = sprites_carros[carro_anterior_obj['prefixo_cor']]
                sprite_atual = sprites_carros[carro_atual_obj['prefixo_cor']]
                
                # Calcular posições usando posições individuais dos carros
                carro_anterior_obj = CARROS_DISPONIVEIS[carro_anterior]
                carro_atual_obj = CARROS_DISPONIVEIS[carro_p1]
                pos_anterior = carro_anterior_obj.get('posicao_oficina', (LARGURA//2 - 300, 380))
                pos_atual = carro_atual_obj.get('posicao_oficina', (LARGURA//2 - 300, 380))
                
                pos_x_anterior = pos_anterior[0] + int(carro_atual_pos * LARGURA)
                pos_x_atual = pos_atual[0] + int(carro_proximo_pos * LARGURA)
                
                # Desenhar carro anterior saindo
                screen.blit(sprite_anterior, (pos_x_anterior, pos_anterior[1]))
                # Desenhar novo carro entrando
                screen.blit(sprite_atual, (pos_x_atual, pos_atual[1]))
            else:
                # Sem transição: desenhar carro atual normalmente
                carro_atual = CARROS_DISPONIVEIS[carro_p1]
                sprite_atual = sprites_carros[carro_atual['prefixo_cor']]
                posicao = carro_atual.get('posicao_oficina', (LARGURA//2 - 300, 380))
                screen.blit(sprite_atual, posicao)
            
            # Nome do carro (abaixo do carro) - estilo pixel art
            nome_carro = render_text(carro_atual['nome'], 42, (255, 100, 255), bold=True, pixel_style=True)
            nome_x = (LARGURA - nome_carro.get_width()) // 2
            screen.blit(nome_carro, (nome_x, 700))
            
            # Informações do carro na lateral direita
            info_x = LARGURA - 350  # 350px da direita (mais largo)
            info_y = 200
            
            # Fundo semi-transparente para as informações
            info_bg = pygame.Surface((330, 450), pygame.SRCALPHA)
            info_bg.fill((0, 0, 0, 150))
            screen.blit(info_bg, (info_x, info_y))
            
            # Nome do carro (acima das especificações) - estilo pixel art
            nome_carro_info = render_text(carro_atual['nome'], 28, (255, 100, 255), bold=True, pixel_style=True)
            nome_x_info = info_x + (330 - nome_carro_info.get_width()) // 2
            screen.blit(nome_carro_info, (nome_x_info, info_y + 10))
            
            # Título das informações
            info_titulo = render_text("ESPECIFICAÇÕES", 20, (255, 255, 255), bold=True, pixel_style=True)
            screen.blit(info_titulo, (info_x + 10, info_y + 50))
            
            # Tipo de tração
            tracao_texto = f"TRAÇÃO: {carro_atual['tipo_tracao'].upper()}"
            tracao_color = (100, 255, 100) if carro_atual['tipo_tracao'] == 'awd' else (255, 255, 100)
            tracao_render = render_text(tracao_texto, 18, tracao_color, bold=True, pixel_style=True)
            screen.blit(tracao_render, (info_x + 10, info_y + 80))
            
            # Velocidade máxima (simulada baseada no tipo de tração)
            vel_max = {"front": 180, "rear": 200, "awd": 220}.get(carro_atual['tipo_tracao'], 190)
            vel_texto = f"VELOCIDADE: {vel_max} km/h"
            vel_render = render_text(vel_texto, 18, (100, 200, 255), bold=True, pixel_style=True)
            screen.blit(vel_render, (info_x + 10, info_y + 110))
            
            # Dirigibilidade (simulada)
            dir_valor = {"front": 85, "rear": 70, "awd": 95}.get(carro_atual['tipo_tracao'], 80)
            dir_texto = f"DIRIGIBILIDADE: {dir_valor}%"
            dir_render = render_text(dir_texto, 18, (255, 200, 100), bold=True, pixel_style=True)
            screen.blit(dir_render, (info_x + 10, info_y + 140))
            
            # Frenagem (simulada)
            fren_valor = {"front": 90, "rear": 75, "awd": 95}.get(carro_atual['tipo_tracao'], 85)
            fren_texto = f"FRENAGEM: {fren_valor}%"
            fren_render = render_text(fren_texto, 18, (255, 100, 100), bold=True, pixel_style=True)
            screen.blit(fren_render, (info_x + 10, info_y + 170))
            
            # Aceleração (simulada)
            acel_valor = {"front": 80, "rear": 90, "awd": 95}.get(carro_atual['tipo_tracao'], 85)
            acel_texto = f"ACELERAÇÃO: {acel_valor}%"
            acel_render = render_text(acel_texto, 18, (200, 100, 255), bold=True, pixel_style=True)
            screen.blit(acel_render, (info_x + 10, info_y + 200))
            
            # Estabilidade (simulada)
            est_valor = {"front": 85, "rear": 70, "awd": 95}.get(carro_atual['tipo_tracao'], 80)
            est_texto = f"ESTABILIDADE: {est_valor}%"
            est_render = render_text(est_texto, 18, (100, 255, 200), bold=True, pixel_style=True)
            screen.blit(est_render, (info_x + 10, info_y + 230))
            
            # Borda da caixa de informações
            pygame.draw.rect(screen, (255, 255, 255), (info_x, info_y, 330, 450), 2)
            
            # Botão confirmar - estilo pixel art
            botao = render_text("ENTER - CONFIRMAR CARRO", 28, (100, 255, 100), bold=True, pixel_style=True)
            botao_x = (LARGURA - botao.get_width()) // 2
            screen.blit(botao, (botao_x, 840))
            
        elif fase_selecao == 2:
            # FASE 2: Player 2 selecionando
            subtitulo = render_text("JOGADOR 2 - ESCOLHA SEU CARRO", 32, (100, 200, 255), bold=True, pixel_style=True)
            subtitulo_x = (LARGURA - subtitulo.get_width()) // 2
            screen.blit(subtitulo, (subtitulo_x, 50))
            
            # Mostrar carro do P1 já selecionado (pequeno, no canto)
            carro_p1_selecionado = CARROS_DISPONIVEIS[carro_p1]
            sprite_p1 = pygame.transform.scale(sprites_carros[carro_p1_selecionado['prefixo_cor']], (90, 45))
            screen.blit(render_text("P1:", 20, (255, 255, 255)), (50, 100))
            screen.blit(sprite_p1, (50, 120))
            screen.blit(render_text(carro_p1_selecionado['nome'], 16, (255, 255, 255)), (50, 175))
            
            # Instruções
            screen.blit(render_text("← → navegar | ENTER confirmar | ESC voltar", 18, (200, 200, 200)), (LARGURA//2 - 180, 60))
            
            # Carro selecionado P2 - Grande e centralizado
            if transicao_ativa:
                # Durante transição: desenhar carro anterior saindo e novo carro entrando
                carro_anterior_obj = CARROS_DISPONIVEIS[carro_anterior]
                carro_atual_obj = CARROS_DISPONIVEIS[carro_p2]
                sprite_anterior = sprites_carros[carro_anterior_obj['prefixo_cor']]
                sprite_atual = sprites_carros[carro_atual_obj['prefixo_cor']]
                
                # Calcular posições usando posições individuais dos carros
                carro_anterior_obj = CARROS_DISPONIVEIS[carro_anterior]
                carro_atual_obj = CARROS_DISPONIVEIS[carro_p2]
                pos_anterior = carro_anterior_obj.get('posicao_oficina', (LARGURA//2 - 300, 380))
                pos_atual = carro_atual_obj.get('posicao_oficina', (LARGURA//2 - 300, 380))
                
                pos_x_anterior = pos_anterior[0] + int(carro_atual_pos * LARGURA)
                pos_x_atual = pos_atual[0] + int(carro_proximo_pos * LARGURA)
                
                # Desenhar carro anterior saindo
                screen.blit(sprite_anterior, (pos_x_anterior, pos_anterior[1]))
                # Desenhar novo carro entrando
                screen.blit(sprite_atual, (pos_x_atual, pos_atual[1]))
            else:
                # Sem transição: desenhar carro atual normalmente
                carro_atual = CARROS_DISPONIVEIS[carro_p2]
                sprite_atual = sprites_carros[carro_atual['prefixo_cor']]
                posicao = carro_atual.get('posicao_oficina', (LARGURA//2 - 300, 380))
                screen.blit(sprite_atual, posicao)
            
            # Nome do carro (abaixo do carro) - estilo pixel art
            nome_carro = render_text(carro_atual['nome'], 42, (255, 100, 255), bold=True, pixel_style=True)
            nome_x = (LARGURA - nome_carro.get_width()) // 2
            screen.blit(nome_carro, (nome_x, 700))
            
            # Informações do carro na lateral direita
            info_x = LARGURA - 350  # 350px da direita (mais largo)
            info_y = 200
            
            # Fundo semi-transparente para as informações
            info_bg = pygame.Surface((330, 450), pygame.SRCALPHA)
            info_bg.fill((0, 0, 0, 150))
            screen.blit(info_bg, (info_x, info_y))
            
            # Nome do carro (acima das especificações) - estilo pixel art
            nome_carro_info = render_text(carro_atual['nome'], 28, (255, 100, 255), bold=True, pixel_style=True)
            nome_x_info = info_x + (330 - nome_carro_info.get_width()) // 2
            screen.blit(nome_carro_info, (nome_x_info, info_y + 10))
            
            # Título das informações
            info_titulo = render_text("ESPECIFICAÇÕES", 20, (255, 255, 255), bold=True, pixel_style=True)
            screen.blit(info_titulo, (info_x + 10, info_y + 50))
            
            # Tipo de tração
            tracao_texto = f"TRAÇÃO: {carro_atual['tipo_tracao'].upper()}"
            tracao_color = (100, 255, 100) if carro_atual['tipo_tracao'] == 'awd' else (255, 255, 100)
            tracao_render = render_text(tracao_texto, 18, tracao_color, bold=True, pixel_style=True)
            screen.blit(tracao_render, (info_x + 10, info_y + 80))
            
            # Velocidade máxima (simulada baseada no tipo de tração)
            vel_max = {"front": 180, "rear": 200, "awd": 220}.get(carro_atual['tipo_tracao'], 190)
            vel_texto = f"VELOCIDADE: {vel_max} km/h"
            vel_render = render_text(vel_texto, 18, (100, 200, 255), bold=True, pixel_style=True)
            screen.blit(vel_render, (info_x + 10, info_y + 110))
            
            # Dirigibilidade (simulada)
            dir_valor = {"front": 85, "rear": 70, "awd": 95}.get(carro_atual['tipo_tracao'], 80)
            dir_texto = f"DIRIGIBILIDADE: {dir_valor}%"
            dir_render = render_text(dir_texto, 18, (255, 200, 100), bold=True, pixel_style=True)
            screen.blit(dir_render, (info_x + 10, info_y + 140))
            
            # Frenagem (simulada)
            fren_valor = {"front": 90, "rear": 75, "awd": 95}.get(carro_atual['tipo_tracao'], 85)
            fren_texto = f"FRENAGEM: {fren_valor}%"
            fren_render = render_text(fren_texto, 18, (255, 100, 100), bold=True, pixel_style=True)
            screen.blit(fren_render, (info_x + 10, info_y + 170))
            
            # Aceleração (simulada)
            acel_valor = {"front": 80, "rear": 90, "awd": 95}.get(carro_atual['tipo_tracao'], 85)
            acel_texto = f"ACELERAÇÃO: {acel_valor}%"
            acel_render = render_text(acel_texto, 18, (200, 100, 255), bold=True, pixel_style=True)
            screen.blit(acel_render, (info_x + 10, info_y + 200))
            
            # Estabilidade (simulada)
            est_valor = {"front": 85, "rear": 70, "awd": 95}.get(carro_atual['tipo_tracao'], 80)
            est_texto = f"ESTABILIDADE: {est_valor}%"
            est_render = render_text(est_texto, 18, (100, 255, 200), bold=True, pixel_style=True)
            screen.blit(est_render, (info_x + 10, info_y + 230))
            
            # Borda da caixa de informações
            pygame.draw.rect(screen, (255, 255, 255), (info_x, info_y, 330, 450), 2)
            
            # Botão confirmar - estilo pixel art
            botao = render_text("ENTER - CONFIRMAR CARRO", 28, (100, 255, 100), bold=True, pixel_style=True)
            botao_x = (LARGURA - botao.get_width()) // 2
            screen.blit(botao, (botao_x, 840))
        
        pygame.display.flip()

def submenu_audio(screen):
    """Submenu de configurações de áudio"""
    from config import CONFIGURACOES, salvar_configuracoes
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)

    opcoes_audio = [
        ("MÚSICA HABILITADA", "musica_habilitada"),
        ("MÚSICA NO MENU", "musica_no_menu"),
        ("MÚSICA NO JOGO", "musica_no_jogo"),
        ("MÚSICA ALEATÓRIA", "musica_aleatorIA"),
        ("VOLUME MÚSICA", "volume_musica")
    ]
    opcao_voltar = ("VOLTAR", "voltar")

    opcao_atual = 0
    clock = pygame.time.Clock()

    caixa_largura = 500
    caixa_altura = 400
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2

    hover_animation = [0.0] * len(opcoes_audio)
    hover_speed = 3.0

    while True:
        dt = clock.tick(FPS)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mouse_in_caixa = (caixa_x <= mouse_x <= caixa_x + caixa_largura and
                                  caixa_y <= mouse_y <= caixa_y + caixa_altura)
                # voltar
                voltar_y = caixa_y + caixa_altura - 60
                voltar_rect = pygame.Rect(caixa_x + 20, voltar_y - 5, caixa_largura - 40, 50)
                if voltar_rect.collidepoint(mouse_x, mouse_y):
                    return True
                # clique em opções só vale dentro da caixa
                if mouse_in_caixa:
                    idx = verificar_clique_opcao(mouse_x, mouse_y, opcoes_audio,
                                                 caixa_x, caixa_y, caixa_largura, 50, 80, None, 0)
                    if idx >= 0:
                        opcao_atual = idx
                        chave = opcoes_audio[opcao_atual][1]
                        if chave in ["musica_habilitada", "musica_no_menu", "musica_no_jogo", "musica_aleatorIA"]:
                            CONFIGURACOES["audio"][chave] = not CONFIGURACOES["audio"][chave]
                            salvar_configuracoes()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return True
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    opcao_atual = (opcao_atual - 1) % len(opcoes_audio)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    opcao_atual = (opcao_atual + 1) % len(opcoes_audio)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    chave = opcoes_audio[opcao_atual][1]
                    if chave == "voltar":
                        return True
                    elif chave in ["musica_habilitada", "musica_no_menu", "musica_no_jogo", "musica_aleatorIA"]:
                        CONFIGURACOES["audio"][chave] = not CONFIGURACOES["audio"][chave]
                        salvar_configuracoes()
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    if opcoes_audio[opcao_atual][1] == "volume_musica":
                        CONFIGURACOES["audio"]["volume_musica"] = max(0.0, CONFIGURACOES["audio"]["volume_musica"] - 0.1)
                        salvar_configuracoes()
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    if opcoes_audio[opcao_atual][1] == "volume_musica":
                        CONFIGURACOES["audio"]["volume_musica"] = min(1.0, CONFIGURACOES["audio"]["volume_musica"] + 0.1)
                        salvar_configuracoes()

        # fundo/overlay/caixa
        screen.blit(bg, (0, 0))
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 150))
        screen.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)

        # --- HOVER CORRETO: só dentro da caixa ---
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_in_caixa = (caixa_x <= mouse_x <= caixa_x + caixa_largura and
                          caixa_y <= mouse_y <= caixa_y + caixa_altura)

        opcao_hover = -1
        if mouse_in_caixa:
            opcao_hover = verificar_clique_opcao(
                mouse_x, mouse_y, opcoes_audio,
                caixa_x, caixa_y, caixa_largura, 50, 80, None, 0
            )
        if opcao_hover >= 0:
            opcao_atual = opcao_hover

        for i in range(len(opcoes_audio)):
            if i == opcao_hover:
                hover_animation[i] = min(1.0, hover_animation[i] + hover_speed * dt)
            else:
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt)
        if not mouse_in_caixa:
            for i in range(len(opcoes_audio)):
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt * 1.5)

        # título
        titulo = render_text("CONFIGURAÇÕES DE ÁUDIO", 36, (255, 255, 255), bold=True, pixel_style=True)
        titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, caixa_y + 20))

        # opções
        for i, (nome, chave) in enumerate(opcoes_audio):
            y = caixa_y + 80 + i * 50

            # sem "duplo": selecionado ignora hover
            hover_progress = 0.0 if (i == opcao_atual) else hover_animation[i]

            if i == opcao_atual:
                base_cor_fundo = (0, 200, 255, 50)
                base_cor_texto = (255, 255, 255)
            else:
                base_cor_fundo = (0, 0, 0, 0)
                base_cor_texto = (255, 255, 255)

            if hover_progress > 0:
                hover_cor_fundo = (0, 200, 255, 30)
                hover_cor_texto = (0, 200, 255)
                cor_fundo = (
                    int(base_cor_fundo[0] + (hover_cor_fundo[0] - base_cor_fundo[0]) * hover_progress),
                    int(base_cor_fundo[1] + (hover_cor_fundo[1] - base_cor_fundo[1]) * hover_progress),
                    int(base_cor_fundo[2] + (hover_cor_fundo[2] - base_cor_fundo[2]) * hover_progress),
                    int(base_cor_fundo[3] + (hover_cor_fundo[3] - base_cor_fundo[3]) * hover_progress)
                )
                cor_texto = (
                    int(base_cor_texto[0] + (hover_cor_texto[0] - base_cor_texto[0]) * hover_progress),
                    int(base_cor_texto[1] + (hover_cor_texto[1] - base_cor_texto[1]) * hover_progress),
                    int(base_cor_texto[2] + (hover_cor_texto[2] - base_cor_texto[2]) * hover_progress)
                )
            else:
                cor_fundo = base_cor_fundo
                cor_texto = base_cor_texto

            if cor_fundo[3] > 0:
                opcao_fundo = pygame.Surface((caixa_largura - 40, 50), pygame.SRCALPHA)
                opcao_fundo.fill(cor_fundo)
                screen.blit(opcao_fundo, (caixa_x + 20, y - 5))

            if chave == "voltar":
                texto = render_text(nome, 24, cor_texto, bold=True, pixel_style=True)
            elif chave == "volume_musica":
                valor = f"{CONFIGURACOES['audio'][chave]:.1f}"
                texto = render_text(f"{nome}: {valor}", 20, cor_texto, bold=True, pixel_style=True)
            else:
                valor = "SIM" if CONFIGURACOES["audio"][chave] else "NÃO"
                texto = render_text(f"{nome}: {valor}", 20, cor_texto, bold=True, pixel_style=True)
            screen.blit(texto, (caixa_x + 30, y))

        # voltar
        voltar_y = caixa_y + caixa_altura - 60
        voltar_rect = pygame.Rect(caixa_x + 20, voltar_y - 5, caixa_largura - 40, 50)
        voltar_hover = voltar_rect.collidepoint(mouse_x, mouse_y)
        if voltar_hover:
            pygame.draw.rect(screen, (0, 200, 255, 50), voltar_rect)
        voltar_texto = render_text(opcao_voltar[0], 24, (0, 200, 255) if voltar_hover else (255, 255, 255), bold=True, pixel_style=True)
        screen.blit(voltar_texto, (caixa_x + 30, voltar_y))

        pygame.display.flip()

def submenu_controles(screen):
    """Submenu de configurações de controles"""
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)

    opcoes_controles = [
        ("JOGADOR 1 - ACELERAR", "W"),
        ("JOGADOR 1 - FREAR", "S"),
        ("JOGADOR 1 - ESQUERDA", "A"),
        ("JOGADOR 1 - DIREITA", "D"),
        ("JOGADOR 1 - TURBO", "SHIFT ESQUERDO"),
        ("JOGADOR 1 - FREIO DE MÃO", "SPACE"),
        ("JOGADOR 2 - ACELERAR", "↑"),
        ("JOGADOR 2 - FREAR", "↓"),
        ("JOGADOR 2 - ESQUERDA", "←"),
        ("JOGADOR 2 - DIREITA", "→"),
        ("JOGADOR 2 - TURBO", "CTRL DIREITO"),
        ("JOGADOR 2 - FREIO DE MÃO", "CTRL")
    ]
    opcao_voltar = ("VOLTAR", "voltar")

    opcao_atual = 0
    clock = pygame.time.Clock()

    caixa_largura = 600
    caixa_altura = 500
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2

    hover_animation = [0.0] * len(opcoes_controles)
    hover_speed = 3.0

    # scroll
    scroll_offset = 0
    altura_item = 45
    altura_total_opcoes = len(opcoes_controles) * altura_item
    altura_area_visivel = caixa_altura - 200
    max_scroll = max(0, altura_total_opcoes - altura_area_visivel)
    
    while True:
        dt = clock.tick(FPS)
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # botão voltar
                voltar_y = caixa_y + caixa_altura - 60
                voltar_rect = pygame.Rect(caixa_x + 20, voltar_y - 5, caixa_largura - 50, altura_item)
                if voltar_rect.collidepoint(mouse_x, mouse_y):
                    return True

                # clique nas opções (respeitando scroll)
                idx = verificar_clique_opcao(
                    mouse_x, mouse_y, opcoes_controles,
                    caixa_x, caixa_y, caixa_largura,
                    altura_item, 80, None, scroll_offset
                )
                if idx >= 0:
                    opcao_atual = idx

            elif ev.type == pygame.MOUSEWHEEL:
                scroll_offset = max(0, min(max_scroll, scroll_offset - ev.y * 30))

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return True
                elif ev.key == pygame.K_RETURN:
                    if opcao_atual >= len(opcoes_controles) - 1:
                        return True
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    opcao_atual = (opcao_atual - 1) % len(opcoes_controles)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    opcao_atual = (opcao_atual + 1) % len(opcoes_controles)
        
        # fundo/overlay/caixa
        screen.blit(bg, (0, 0))
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 150))
        screen.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)

        # --- HOVER CORRETO COM SCROLL ---
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_in_caixa = (caixa_x <= mouse_x <= caixa_x + caixa_largura and
                          caixa_y <= mouse_y <= caixa_y + caixa_altura)
        area_scroll_y = caixa_y + 80
        area_scroll_height = altura_area_visivel
        mouse_in_scroll_area = (area_scroll_y <= mouse_y <= area_scroll_y + area_scroll_height)

        opcao_hover = -1
        if mouse_in_caixa and mouse_in_scroll_area:
            opcao_hover = verificar_clique_opcao(
                mouse_x, mouse_y, opcoes_controles,
                caixa_x, caixa_y, caixa_largura,
                altura_item, 80, None, scroll_offset
            )
        if opcao_hover >= 0:
            opcao_atual = opcao_hover

        for i in range(len(opcoes_controles)):
            if i == opcao_hover:
                hover_animation[i] = min(1.0, hover_animation[i] + hover_speed * dt)
            else:
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt)
        if not mouse_in_caixa:
            for i in range(len(opcoes_controles)):
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt * 1.5)
        
        # título
        titulo = render_text("CONTROLES", 36, (255, 255, 255), bold=True, pixel_style=True)
        titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, caixa_y + 20))

        # opções (respeitando área visível)
        for i, (nome, tecla) in enumerate(opcoes_controles):
            y = caixa_y + 80 + i * altura_item - scroll_offset
            if y < caixa_y + 80 or y > caixa_y + caixa_altura - 80:
                continue

            hover_progress = 0.0 if (i == opcao_atual) else hover_animation[i]

            if i == opcao_atual:
                base_cor_fundo = (0, 200, 255, 50)
                base_cor_texto = (0, 200, 255)
            else:
                base_cor_fundo = (0, 0, 0, 0)
                base_cor_texto = (255, 255, 255)

            if hover_progress > 0:
                hover_cor_fundo = (0, 200, 255, 30)
                hover_cor_texto = (0, 200, 255)
                cor_fundo = (
                    int(base_cor_fundo[0] + (hover_cor_fundo[0] - base_cor_fundo[0]) * hover_progress),
                    int(base_cor_fundo[1] + (hover_cor_fundo[1] - base_cor_fundo[1]) * hover_progress),
                    int(base_cor_fundo[2] + (hover_cor_fundo[2] - base_cor_fundo[2]) * hover_progress),
                    int(base_cor_fundo[3] + (hover_cor_fundo[3] - base_cor_fundo[3]) * hover_progress)
                )
                cor_texto = (
                    int(base_cor_texto[0] + (hover_cor_texto[0] - base_cor_texto[0]) * hover_progress),
                    int(base_cor_texto[1] + (hover_cor_texto[1] - base_cor_texto[1]) * hover_progress),
                    int(base_cor_texto[2] + (hover_cor_texto[2] - base_cor_texto[2]) * hover_progress)
                )
            else:
                cor_fundo = base_cor_fundo
                cor_texto = base_cor_texto

            if cor_fundo[3] > 0:
                opcao_fundo = pygame.Surface((caixa_largura - 50, altura_item), pygame.SRCALPHA)
                opcao_fundo.fill(cor_fundo)
                screen.blit(opcao_fundo, (caixa_x + 20, y - 5))

            texto = render_text(f"{nome}: {tecla}", 20, cor_texto, bold=True, pixel_style=True)
            screen.blit(texto, (caixa_x + 30, y))

        # voltar
        voltar_y = caixa_y + caixa_altura - 60
        voltar_rect = pygame.Rect(caixa_x + 20, voltar_y - 5, caixa_largura - 50, altura_item)
        voltar_hover = voltar_rect.collidepoint(mouse_x, mouse_y)
        if voltar_hover:
            pygame.draw.rect(screen, (0, 200, 255, 50), voltar_rect)
        voltar_texto = render_text(opcao_voltar[0], 24, (0, 200, 255) if voltar_hover else (255, 255, 255), bold=True, pixel_style=True)
        screen.blit(voltar_texto, (caixa_x + 30, voltar_y))

        # scrollbar
        if max_scroll > 0:
            desenhar_scrollbar(screen, scroll_offset, max_scroll, caixa_x, caixa_y, caixa_largura, caixa_altura)

        pygame.display.flip()

def submenu_video(screen):
    """Submenu de configurações de vídeo"""
    from config import CONFIGURACOES, salvar_configuracoes
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)

    opcoes_video = [
        ("RESOLUÇÃO", "resolucao"),
        ("TELA CHEIA", "fullscreen"),
        ("SEM BORDAS", "tela_cheIA_sem_bordas"),
        ("QUALIDADE ALTA", "qualidade_alta"),
        ("VSYNC", "vsync"),
        ("FPS MÁXIMO", "fps_max"),
        ("MOSTRAR FPS", "mostrar_fps")
    ]
    opcao_voltar = ("VOLTAR", "voltar")

    opcao_atual = 0
    clock = pygame.time.Clock()

    caixa_largura = 500
    caixa_altura = 400
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2

    hover_animation = [0.0] * len(opcoes_video)
    hover_speed = 3.0

    # scroll
    scroll_offset = 0
    altura_item = 50
    altura_total_opcoes = len(opcoes_video) * altura_item
    altura_area_visivel = caixa_altura - 200
    max_scroll = max(0, altura_total_opcoes - altura_area_visivel)
    
    while True:
        dt = clock.tick(FPS)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mouse_in_caixa = (caixa_x <= mouse_x <= caixa_x + caixa_largura and
                                  caixa_y <= mouse_y <= caixa_y + caixa_altura)
                voltar_y = caixa_y + caixa_altura - 60
                voltar_rect = pygame.Rect(caixa_x + 20, voltar_y - 5, caixa_largura - 50, altura_item)
                if voltar_rect.collidepoint(mouse_x, mouse_y):
                    return True
                if mouse_in_caixa:
                    idx = verificar_clique_opcao(mouse_x, mouse_y, opcoes_video,
                                                 caixa_x, caixa_y, caixa_largura, altura_item, 80, None, scroll_offset)
                    if idx >= 0:
                        opcao_atual = idx
                        chave = opcoes_video[opcao_atual][1]
                        if chave in ["fullscreen", "tela_cheIA_sem_bordas", "qualidade_alta", "vsync", "mostrar_fps"]:
                            CONFIGURACOES["video"][chave] = not CONFIGURACOES["video"][chave]
                            salvar_configuracoes()
            elif ev.type == pygame.MOUSEWHEEL:
                scroll_offset = max(0, min(max_scroll, scroll_offset - ev.y * 30))
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return True
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    opcao_atual = (opcao_atual - 1) % len(opcoes_video)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    opcao_atual = (opcao_atual + 1) % len(opcoes_video)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    chave = opcoes_video[opcao_atual][1]
                    if chave == "voltar":
                        return True
                    elif chave in ["fullscreen", "tela_cheIA_sem_bordas", "qualidade_alta", "vsync", "mostrar_fps"]:
                        CONFIGURACOES["video"][chave] = not CONFIGURACOES["video"][chave]
                        salvar_configuracoes()
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    if opcoes_video[opcao_atual][1] == "resolucao":
                        resolucoes = [(1280, 720), (1920, 1080), (1366, 768), (1600, 900)]
                        try:
                            idx = resolucoes.index(CONFIGURACOES["video"]["resolucao"])
                            CONFIGURACOES["video"]["resolucao"] = resolucoes[(idx - 1) % len(resolucoes)]
                        except ValueError:
                            CONFIGURACOES["video"]["resolucao"] = resolucoes[0]
                        salvar_configuracoes()
                    elif opcoes_video[opcao_atual][1] == "fps_max":
                        fps_opcoes = [30, 60, 120, 144, 200, 300]
                        try:
                            idx = fps_opcoes.index(CONFIGURACOES["video"]["fps_max"])
                            CONFIGURACOES["video"]["fps_max"] = fps_opcoes[(idx - 1) % len(fps_opcoes)]
                        except ValueError:
                            CONFIGURACOES["video"]["fps_max"] = 60
                        salvar_configuracoes()
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    if opcoes_video[opcao_atual][1] == "resolucao":
                        resolucoes = [(1280, 720), (1920, 1080), (1366, 768), (1600, 900)]
                        try:
                            idx = resolucoes.index(CONFIGURACOES["video"]["resolucao"])
                            CONFIGURACOES["video"]["resolucao"] = resolucoes[(idx + 1) % len(resolucoes)]
                        except ValueError:
                            CONFIGURACOES["video"]["resolucao"] = resolucoes[0]
                        salvar_configuracoes()
                    elif opcoes_video[opcao_atual][1] == "fps_max":
                        fps_opcoes = [30, 60, 120, 144, 200, 300]
                        try:
                            idx = fps_opcoes.index(CONFIGURACOES["video"]["fps_max"])
                            CONFIGURACOES["video"]["fps_max"] = fps_opcoes[(idx + 1) % len(fps_opcoes)]
                        except ValueError:
                            CONFIGURACOES["video"]["fps_max"] = 60
                        salvar_configuracoes()

        # desenha fundo/caixa
        screen.blit(bg, (0, 0))
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 150))
        screen.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)

        # --- HOVER CORRETO COM SCROLL ---
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_in_caixa = (caixa_x <= mouse_x <= caixa_x + caixa_largura and
                          caixa_y <= mouse_y <= caixa_y + caixa_altura)
        area_scroll_y = caixa_y + 80
        area_scroll_height = altura_area_visivel
        mouse_in_scroll_area = (area_scroll_y <= mouse_y <= area_scroll_y + area_scroll_height)

        opcao_hover = -1
        if mouse_in_caixa and mouse_in_scroll_area:
            opcao_hover = verificar_clique_opcao(
                mouse_x, mouse_y, opcoes_video,
                caixa_x, caixa_y, caixa_largura, altura_item, 80, None, scroll_offset
            )
        if opcao_hover >= 0:
            opcao_atual = opcao_hover

        for i in range(len(opcoes_video)):
            if i == opcao_hover:
                hover_animation[i] = min(1.0, hover_animation[i] + hover_speed * dt)
            else:
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt)
        if not mouse_in_caixa:
            for i in range(len(opcoes_video)):
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt * 1.5)

        # título
        titulo = render_text("CONFIGURAÇÕES DE VÍDEO", 36, (255, 255, 255), bold=True, pixel_style=True)
        titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, caixa_y + 20))

        # opções (respeitando área visível)
        for i, (nome, chave) in enumerate(opcoes_video):
            y = caixa_y + 80 + i * altura_item - scroll_offset
            if y < caixa_y + 80 or y > caixa_y + caixa_altura - 80:
                continue

            hover_progress = 0.0 if (i == opcao_atual) else hover_animation[i]

            if i == opcao_atual:
                base_cor_fundo = (0, 200, 255, 50)
                base_cor_texto = (255, 255, 255)
            else:
                base_cor_fundo = (0, 0, 0, 0)
                base_cor_texto = (255, 255, 255)

            if hover_progress > 0:
                hover_cor_fundo = (0, 200, 255, 30)
                hover_cor_texto = (0, 200, 255)
                cor_fundo = (
                    int(base_cor_fundo[0] + (hover_cor_fundo[0] - base_cor_fundo[0]) * hover_progress),
                    int(base_cor_fundo[1] + (hover_cor_fundo[1] - base_cor_fundo[1]) * hover_progress),
                    int(base_cor_fundo[2] + (hover_cor_fundo[2] - base_cor_fundo[2]) * hover_progress),
                    int(base_cor_fundo[3] + (hover_cor_fundo[3] - base_cor_fundo[3]) * hover_progress)
                )
                cor_texto = (
                    int(base_cor_texto[0] + (hover_cor_texto[0] - base_cor_texto[0]) * hover_progress),
                    int(base_cor_texto[1] + (hover_cor_texto[1] - base_cor_texto[1]) * hover_progress),
                    int(base_cor_texto[2] + (hover_cor_texto[2] - base_cor_texto[2]) * hover_progress)
                )
            else:
                cor_fundo = base_cor_fundo
                cor_texto = base_cor_texto

            if cor_fundo[3] > 0:
                opcao_fundo = pygame.Surface((caixa_largura - 50, altura_item), pygame.SRCALPHA)
                opcao_fundo.fill(cor_fundo)
                screen.blit(opcao_fundo, (caixa_x + 20, y - 5))

            if chave == "voltar":
                texto = render_text(nome, 24, cor_texto, bold=True, pixel_style=True)
            elif chave == "resolucao":
                res = CONFIGURACOES["video"][chave]
                texto = render_text(f"{nome}: {res[0]}x{res[1]}", 20, cor_texto, bold=True, pixel_style=True)
            elif chave == "fps_max":
                fps = CONFIGURACOES["video"][chave]
                texto = render_text(f"{nome}: {fps}", 20, cor_texto, bold=True, pixel_style=True)
            else:
                valor = "SIM" if CONFIGURACOES["video"][chave] else "NÃO"
                texto = render_text(f"{nome}: {valor}", 20, cor_texto, bold=True, pixel_style=True)
            screen.blit(texto, (caixa_x + 30, y))

        # voltar
        voltar_y = caixa_y + caixa_altura - 60
        voltar_rect = pygame.Rect(caixa_x + 20, voltar_y - 5, caixa_largura - 50, altura_item)
        voltar_hover = voltar_rect.collidepoint(mouse_x, mouse_y)
        if voltar_hover:
            pygame.draw.rect(screen, (0, 200, 255, 50), voltar_rect)
        voltar_texto = render_text(opcao_voltar[0], 24, (0, 200, 255) if voltar_hover else (255, 255, 255), bold=True, pixel_style=True)
        screen.blit(voltar_texto, (caixa_x + 30, voltar_y))

        # scrollbar
        if max_scroll > 0:
            desenhar_scrollbar(screen, scroll_offset, max_scroll, caixa_x, caixa_y, caixa_largura, caixa_altura)

        pygame.display.flip()

def submenu_idioma(screen):
    """Submenu de configurações de idioma"""
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)

    opcoes_idioma = [
        ("PORTUGUÊS", "pt"),
        ("ENGLISH", "en"),
        ("ESPAÑOL", "es"),
        ("FRANÇAIS", "fr")
    ]
    opcao_voltar = ("VOLTAR", "voltar")

    opcao_atual = 0
    clock = pygame.time.Clock()

    caixa_largura = 400
    caixa_altura = 350
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2

    hover_animation = [0.0] * len(opcoes_idioma)
    hover_speed = 3.0
    
    while True:
        dt = clock.tick(FPS)
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mouse_in_caixa = (caixa_x <= mouse_x <= caixa_x + caixa_largura and
                                  caixa_y <= mouse_y <= caixa_y + caixa_altura)
                voltar_y = caixa_y + caixa_altura - 60
                voltar_rect = pygame.Rect(caixa_x + 20, voltar_y - 5, caixa_largura - 40, 45)
                if voltar_rect.collidepoint(mouse_x, mouse_y):
                    return True
                if mouse_in_caixa:
                    idx = verificar_clique_opcao(mouse_x, mouse_y, opcoes_idioma,
                                                 caixa_x, caixa_y, caixa_largura, 45, 80, None, 0)
                    if idx >= 0:
                        opcao_atual = idx
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return True
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    opcao_atual = (opcao_atual - 1) % len(opcoes_idioma)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    opcao_atual = (opcao_atual + 1) % len(opcoes_idioma)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if opcoes_idioma[opcao_atual][1] == "voltar":
                        return True
                    # aqui entrarIA a troca de idioma
        
        # fundo/overlay/caixa
        screen.blit(bg, (0, 0))
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 150))
        screen.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)

        # --- HOVER CORRETO ---
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_in_caixa = (caixa_x <= mouse_x <= caixa_x + caixa_largura and
                          caixa_y <= mouse_y <= caixa_y + caixa_altura)

        opcao_hover = -1
        if mouse_in_caixa:
            opcao_hover = verificar_clique_opcao(
                mouse_x, mouse_y, opcoes_idioma,
                caixa_x, caixa_y, caixa_largura, 45, 80, None, 0
            )
        if opcao_hover >= 0:
            opcao_atual = opcao_hover

        for i in range(len(opcoes_idioma)):
            if i == opcao_hover:
                hover_animation[i] = min(1.0, hover_animation[i] + hover_speed * dt)
            else:
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt)
        if not mouse_in_caixa:
            for i in range(len(opcoes_idioma)):
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt * 1.5)
        
        # título
        titulo = render_text("IDIOMA", 36, (255, 255, 255), bold=True, pixel_style=True)
        titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, caixa_y + 20))

        # opções
        for i, (nome, codigo) in enumerate(opcoes_idioma):
            y = caixa_y + 80 + i * 45

            hover_progress = 0.0 if (i == opcao_atual) else hover_animation[i]

            if i == opcao_atual:
                base_cor_fundo = (0, 200, 255, 50)
                base_cor_texto = (0, 200, 255)
            else:
                base_cor_fundo = (0, 0, 0, 0)
                base_cor_texto = (255, 255, 255)

            if hover_progress > 0:
                hover_cor_fundo = (0, 200, 255, 30)
                hover_cor_texto = (0, 200, 255)
                cor_fundo = (
                    int(base_cor_fundo[0] + (hover_cor_fundo[0] - base_cor_fundo[0]) * hover_progress),
                    int(base_cor_fundo[1] + (hover_cor_fundo[1] - base_cor_fundo[1]) * hover_progress),
                    int(base_cor_fundo[2] + (hover_cor_fundo[2] - base_cor_fundo[2]) * hover_progress),
                    int(base_cor_fundo[3] + (hover_cor_fundo[3] - base_cor_fundo[3]) * hover_progress)
                )
                cor_texto = (
                    int(base_cor_texto[0] + (hover_cor_texto[0] - base_cor_texto[0]) * hover_progress),
                    int(base_cor_texto[1] + (hover_cor_texto[1] - base_cor_texto[1]) * hover_progress),
                    int(base_cor_texto[2] + (hover_cor_texto[2] - base_cor_texto[2]) * hover_progress)
                )
            else:
                cor_fundo = base_cor_fundo
                cor_texto = base_cor_texto

            if cor_fundo[3] > 0:
                opcao_fundo = pygame.Surface((caixa_largura - 40, 45), pygame.SRCALPHA)
                opcao_fundo.fill(cor_fundo)
                screen.blit(opcao_fundo, (caixa_x + 20, y - 5))

            texto = render_text(nome, 24, cor_texto, bold=True, pixel_style=True)
            screen.blit(texto, (caixa_x + 30, y))

        # voltar
        voltar_y = caixa_y + caixa_altura - 60
        voltar_rect = pygame.Rect(caixa_x + 20, voltar_y - 5, caixa_largura - 40, 45)
        voltar_hover = voltar_rect.collidepoint(mouse_x, mouse_y)
        if voltar_hover:
            pygame.draw.rect(screen, (0, 200, 255, 50), voltar_rect)
        voltar_texto = render_text(opcao_voltar[0], 24, (0, 200, 255) if voltar_hover else (255, 255, 255), bold=True, pixel_style=True)
        screen.blit(voltar_texto, (caixa_x + 30, voltar_y))

        pygame.display.flip()

def opcoes_loop(screen):
    """Tela de opções do jogo com design pixel art centralizado"""
    from config import CAMINHO_MENU, CONFIGURACOES, salvar_configuracoes
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)

    opcoes_principais = [
        ("VOLUME", "audio"),
        ("CONTROLES", "controles"),
        ("GRÁFICOS", "video"),
        ("IDIOMA", "idioma"),
        ("VOLTAR", "voltar")
    ]

    opcao_atual = 0
    clock = pygame.time.Clock()

    # caixa
    caixa_largura = 400
    caixa_altura = 500
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2

    # animação hover
    hover_animation = [0.0] * len(opcoes_principais)
    hover_speed = 3.0

    while True:
        dt = clock.tick(FPS)

        # eventos
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # clique só vale se estiver dentro da caixa
                mouse_in_caixa = (caixa_x <= mouse_x <= caixa_x + caixa_largura and
                                  caixa_y <= mouse_y <= caixa_y + caixa_altura)
                if mouse_in_caixa:
                    opcao_clicada = verificar_clique_opcao(
                        mouse_x, mouse_y, opcoes_principais,
                        caixa_x, caixa_y, caixa_largura,
                        altura_item=50, offset_y=80, opcao_largura=350, scroll_offset=0
                    )
                    if opcao_clicada >= 0:
                        opcao_atual = opcao_clicada
                        chave = opcoes_principais[opcao_atual][1]
                        if chave == "voltar":
                            return True
                        elif chave == "audio":
                            if not submenu_audio(screen):
                                return False
                        elif chave == "controles":
                            if not submenu_controles(screen):
                                return False
                        elif chave == "video":
                            if not submenu_video(screen):
                                return False
                        elif chave == "idioma":
                            if not submenu_idioma(screen):
                                return False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return True
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    opcao_atual = (opcao_atual - 1) % len(opcoes_principais)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    opcao_atual = (opcao_atual + 1) % len(opcoes_principais)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    chave = opcoes_principais[opcao_atual][1]
                    if chave == "voltar":
                        return True
                    elif chave == "audio":
                        if submenu_audio(screen):
                            continue
                    elif chave == "controles":
                        if submenu_controles(screen):
                            continue
                    elif chave == "video":
                        if submenu_video(screen):
                            continue
                    elif chave == "idioma":
                        if submenu_idioma(screen):
                            continue

        # desenha fundo/overlay/caixa
        screen.blit(bg, (0, 0))
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 50))
        screen.blit(overlay, (0, 0))

        caixa_largura = 400
        caixa_altura = 500
        caixa_x = (LARGURA - caixa_largura) // 2
        caixa_y = (ALTURA - caixa_altura) // 2

        # --- HOVER CORRETO: só dentro da caixa ---
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_in_caixa = (caixa_x <= mouse_x <= caixa_x + caixa_largura and
                          caixa_y <= mouse_y <= caixa_y + caixa_altura)

        opcao_hover = -1
        if mouse_in_caixa:
            opcao_hover = verificar_clique_opcao(
                mouse_x, mouse_y, opcoes_principais,
                caixa_x, caixa_y, caixa_largura,
                altura_item=50, offset_y=80, opcao_largura=350, scroll_offset=0
            )
        if opcao_hover >= 0:
            opcao_atual = opcao_hover

        # atualiza animações (apenas uma em hover)
        for i in range(len(opcoes_principais)):
            if i == opcao_hover:
                hover_animation[i] = min(1.0, hover_animation[i] + hover_speed * dt)
            else:
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt)
        if not mouse_in_caixa:
            for i in range(len(opcoes_principais)):
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt * 1.5)

        # caixa e borda
        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 150))
        screen.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)

        # título
        titulo = render_text("OPÇÕES", 48, (255, 255, 255), bold=True, pixel_style=True)
        titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
        titulo_y = caixa_y + 20
        screen.blit(titulo, (titulo_x, titulo_y))
        pygame.draw.line(screen, (255, 255, 255),
                         (caixa_x + 20, titulo_y + titulo.get_height() + 10),
                         (caixa_x + caixa_largura - 20, titulo_y + titulo.get_height() + 10), 2)

        # opções
        opcao_largura = 350
        opcao_altura = 50
        opcao_x = caixa_x + (caixa_largura - opcao_largura) // 2
        opcao_y_inicial = titulo_y + titulo.get_height() + 40
        espacamento = 15

        for i, (nome, categoria) in enumerate(opcoes_principais):
            opcao_y = opcao_y_inicial + i * (opcao_altura + espacamento)

            # não misturar hover com selecionado
            hover_progress = 0.0 if (i == opcao_atual) else hover_animation[i]

            if i == opcao_atual:
                base_cor_fundo = (0, 200, 255, 50)
                base_cor_texto = (0, 200, 255)
            else:
                base_cor_fundo = (0, 0, 0, 0)
                base_cor_texto = (255, 255, 255)

            if hover_progress > 0:
                hover_cor_fundo = (0, 200, 255, 30)
                hover_cor_texto = (0, 200, 255)
                cor_fundo = (
                    int(base_cor_fundo[0] + (hover_cor_fundo[0] - base_cor_fundo[0]) * hover_progress),
                    int(base_cor_fundo[1] + (hover_cor_fundo[1] - base_cor_fundo[1]) * hover_progress),
                    int(base_cor_fundo[2] + (hover_cor_fundo[2] - base_cor_fundo[2]) * hover_progress),
                    int(base_cor_fundo[3] + (hover_cor_fundo[3] - base_cor_fundo[3]) * hover_progress)
                )
                cor_texto = (
                    int(base_cor_texto[0] + (hover_cor_texto[0] - base_cor_texto[0]) * hover_progress),
                    int(base_cor_texto[1] + (hover_cor_texto[1] - base_cor_texto[1]) * hover_progress),
                    int(base_cor_texto[2] + (hover_cor_texto[2] - base_cor_texto[2]) * hover_progress)
                )
            else:
                cor_fundo = base_cor_fundo
                cor_texto = base_cor_texto

            if cor_fundo[3] > 0:
                opcao_fundo = pygame.Surface((opcao_largura, opcao_altura), pygame.SRCALPHA)
                opcao_fundo.fill(cor_fundo)
                screen.blit(opcao_fundo, (opcao_x, opcao_y))

            pygame.draw.rect(screen, (255, 255, 255), (opcao_x, opcao_y, opcao_largura, opcao_altura), 2)
            texto_opcao = render_text(nome, 32, cor_texto, bold=True, pixel_style=True)
            texto_x = opcao_x + (opcao_largura - texto_opcao.get_width()) // 2
            texto_y = opcao_y + (opcao_altura - texto_opcao.get_height()) // 2
            screen.blit(texto_opcao, (texto_x, texto_y))

        pygame.display.flip()

def modo_jogo_loop(screen):
    """Menu de seleção de modo de jogo"""
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)
    
    # Configurações atuais (podem ser salvas em CONFIGURACOES)
    modo_jogo_atual = ModoJogo.UM_JOGADOR
    tipo_jogo_atual = TipoJogo.CORRIDA
    
    # Opções de modo de jogo
    opcoes_modo = [
        ("1 JOGADOR", ModoJogo.UM_JOGADOR),
        ("2 JOGADORES", ModoJogo.DOIS_JOGADORES)
    ]
    
    # Opções de tipo de jogo
    opcoes_tipo = [
        ("CORRIDA", TipoJogo.CORRIDA),
        ("DRIFT", TipoJogo.DRIFT)
    ]
    
    opcao_modo_atual = 0
    opcao_tipo_atual = 0
    clock = pygame.time.Clock()
    
    # Caixa principal
    caixa_largura = 500
    caixa_altura = 450
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2
    
    # Animações de hover
    hover_animation_modo = [0.0] * len(opcoes_modo)
    hover_animation_tipo = [0.0] * len(opcoes_tipo)
    hover_speed = 3.0
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        
        # Atualizar música
        gerencIAdor_musica.verificar_fim_musica()
        popup_musica.atualizar(dt)
        
        # Verificar hover do pop-up
        mouse_x, mouse_y = pygame.mouse.get_pos()
        popup_musica.verificar_hover(mouse_x, mouse_y)
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # Verificar clique no pop-up de música primeiro
                clique_popup = popup_musica.verificar_clique(ev.pos[0], ev.pos[1])
                if clique_popup == "anterior":
                    gerencIAdor_musica.musica_anterior()
                    if gerencIAdor_musica.musica_tocando:
                        popup_musica.mostrar(gerencIAdor_musica.obter_nome_musica_atual())
                elif clique_popup == "proximo":
                    gerencIAdor_musica.proxima_musica()
                    if gerencIAdor_musica.musica_tocando:
                        popup_musica.mostrar(gerencIAdor_musica.obter_nome_musica_atual())
                else:
                    # Verificar clique nas opções
                    mouse_x, mouse_y = ev.pos
                    
                    # Verificar clique em modo de jogo
                    for i, (nome, modo) in enumerate(opcoes_modo):
                        y = caixa_y + 100 + i * 50
                        rect = pygame.Rect(caixa_x + 50, y - 5, 200, 40)
                        if rect.collidepoint(mouse_x, mouse_y):
                            opcao_modo_atual = i
                            modo_jogo_atual = modo
                    
                    # Verificar clique em tipo de jogo
                    for i, (nome, tipo) in enumerate(opcoes_tipo):
                        y = caixa_y + 250 + i * 50
                        rect = pygame.Rect(caixa_x + 50, y - 5, 200, 40)
                        if rect.collidepoint(mouse_x, mouse_y):
                            opcao_tipo_atual = i
                            tipo_jogo_atual = tipo
                    
                    # Verificar clique no botão iniciar jogo
                    iniciar_rect = pygame.Rect(caixa_x + 50, caixa_y + caixa_altura - 100, 200, 40)
                    if iniciar_rect.collidepoint(mouse_x, mouse_y):
                        return (modo_jogo_atual, tipo_jogo_atual)
                    
                    # Verificar clique no botão voltar
                    voltar_rect = pygame.Rect(caixa_x + 270, caixa_y + caixa_altura - 100, 200, 40)
                    if voltar_rect.collidepoint(mouse_x, mouse_y):
                        return None
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return True
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    if opcao_modo_atual > 0:
                        opcao_modo_atual -= 1
                        modo_jogo_atual = opcoes_modo[opcao_modo_atual][1]
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    if opcao_modo_atual < len(opcoes_modo) - 1:
                        opcao_modo_atual += 1
                        modo_jogo_atual = opcoes_modo[opcao_modo_atual][1]
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    if opcao_tipo_atual > 0:
                        opcao_tipo_atual -= 1
                        tipo_jogo_atual = opcoes_tipo[opcao_tipo_atual][1]
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    if opcao_tipo_atual < len(opcoes_tipo) - 1:
                        opcao_tipo_atual += 1
                        tipo_jogo_atual = opcoes_tipo[opcao_tipo_atual][1]
                elif ev.key == pygame.K_RETURN:
                    return (modo_jogo_atual, tipo_jogo_atual)
                elif ev.key == pygame.K_m:
                    # Próxima música
                    gerencIAdor_musica.proxima_musica()
                    if gerencIAdor_musica.musica_tocando:
                        popup_musica.mostrar(gerencIAdor_musica.obter_nome_musica_atual())
                elif ev.key == pygame.K_n:
                    # Música anterior
                    gerencIAdor_musica.musica_anterior()
                    if gerencIAdor_musica.musica_tocando:
                        popup_musica.mostrar(gerencIAdor_musica.obter_nome_musica_atual())
        
        # Atualizar animações de hover
        for i in range(len(opcoes_modo)):
            y = caixa_y + 100 + i * 50
            rect = pygame.Rect(caixa_x + 50, y - 5, 200, 40)
            is_hovering = rect.collidepoint(mouse_x, mouse_y)
            
            if is_hovering:
                hover_animation_modo[i] = min(1.0, hover_animation_modo[i] + hover_speed * dt)
            else:
                hover_animation_modo[i] = max(0.0, hover_animation_modo[i] - hover_speed * dt)
        
        for i in range(len(opcoes_tipo)):
            y = caixa_y + 250 + i * 50
            rect = pygame.Rect(caixa_x + 50, y - 5, 200, 40)
            is_hovering = rect.collidepoint(mouse_x, mouse_y)
            
            if is_hovering:
                hover_animation_tipo[i] = min(1.0, hover_animation_tipo[i] + hover_speed * dt)
            else:
                hover_animation_tipo[i] = max(0.0, hover_animation_tipo[i] - hover_speed * dt)
        
        # Desenhar
        screen.blit(bg, (0, 0))
        
        # Overlay
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        
        # Caixa principal
        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 150))
        screen.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        # Título
        titulo = render_text("MODO DE JOGO", 36, (255, 255, 255), bold=True, pixel_style=True)
        titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, caixa_y + 20))
        
        # Modo de jogo
        modo_titulo = render_text("NÚMERO DE JOGADORES:", 24, (255, 255, 255), bold=True, pixel_style=True)
        screen.blit(modo_titulo, (caixa_x + 50, caixa_y + 70))
        
        for i, (nome, modo) in enumerate(opcoes_modo):
            y = caixa_y + 100 + i * 50
            
            # Cores baseadas na seleção e hover
            if i == opcao_modo_atual:
                cor_fundo = (0, 200, 255, 50)
                cor_texto = (0, 200, 255)
            else:
                cor_fundo = (0, 0, 0, 0)
                cor_texto = (255, 255, 255)
            
            # Aplicar hover
            hover_progress = hover_animation_modo[i]
            if hover_progress > 0:
                hover_cor_fundo = (0, 200, 255, 30)
                hover_cor_texto = (0, 200, 255)
                cor_fundo = (
                    int(cor_fundo[0] + (hover_cor_fundo[0] - cor_fundo[0]) * hover_progress),
                    int(cor_fundo[1] + (hover_cor_fundo[1] - cor_fundo[1]) * hover_progress),
                    int(cor_fundo[2] + (hover_cor_fundo[2] - cor_fundo[2]) * hover_progress),
                    int(cor_fundo[3] + (hover_cor_fundo[3] - cor_fundo[3]) * hover_progress)
                )
                cor_texto = (
                    int(cor_texto[0] + (hover_cor_texto[0] - cor_texto[0]) * hover_progress),
                    int(cor_texto[1] + (hover_cor_texto[1] - cor_texto[1]) * hover_progress),
                    int(cor_texto[2] + (hover_cor_texto[2] - cor_texto[2]) * hover_progress)
                )
            
            # Desenhar fundo
            if cor_fundo[3] > 0:
                opcao_fundo = pygame.Surface((200, 40), pygame.SRCALPHA)
                opcao_fundo.fill(cor_fundo)
                screen.blit(opcao_fundo, (caixa_x + 50, y - 5))
            
            # Desenhar texto
            texto = render_text(nome, 20, cor_texto, bold=True, pixel_style=True)
            screen.blit(texto, (caixa_x + 60, y))
        
        # Tipo de jogo
        tipo_titulo = render_text("TIPO DE JOGO:", 24, (255, 255, 255), bold=True, pixel_style=True)
        screen.blit(tipo_titulo, (caixa_x + 50, caixa_y + 220))
        
        for i, (nome, tipo) in enumerate(opcoes_tipo):
            y = caixa_y + 250 + i * 50
            
            # Cores baseadas na seleção e hover
            if i == opcao_tipo_atual:
                cor_fundo = (0, 200, 255, 50)
                cor_texto = (0, 200, 255)
            else:
                cor_fundo = (0, 0, 0, 0)
                cor_texto = (255, 255, 255)
            
            # Aplicar hover
            hover_progress = hover_animation_tipo[i]
            if hover_progress > 0:
                hover_cor_fundo = (0, 200, 255, 30)
                hover_cor_texto = (0, 200, 255)
                cor_fundo = (
                    int(cor_fundo[0] + (hover_cor_fundo[0] - cor_fundo[0]) * hover_progress),
                    int(cor_fundo[1] + (hover_cor_fundo[1] - cor_fundo[1]) * hover_progress),
                    int(cor_fundo[2] + (hover_cor_fundo[2] - cor_fundo[2]) * hover_progress),
                    int(cor_fundo[3] + (hover_cor_fundo[3] - cor_fundo[3]) * hover_progress)
                )
                cor_texto = (
                    int(cor_texto[0] + (hover_cor_texto[0] - cor_texto[0]) * hover_progress),
                    int(cor_texto[1] + (hover_cor_texto[1] - cor_texto[1]) * hover_progress),
                    int(cor_texto[2] + (hover_cor_texto[2] - cor_texto[2]) * hover_progress)
                )
            
            # Desenhar fundo
            if cor_fundo[3] > 0:
                opcao_fundo = pygame.Surface((200, 40), pygame.SRCALPHA)
                opcao_fundo.fill(cor_fundo)
                screen.blit(opcao_fundo, (caixa_x + 50, y - 5))
            
            # Desenhar texto
            texto = render_text(nome, 20, cor_texto, bold=True, pixel_style=True)
            screen.blit(texto, (caixa_x + 60, y))
        
        # Botão iniciar jogo
        iniciar_rect = pygame.Rect(caixa_x + 50, caixa_y + caixa_altura - 100, 200, 40)
        iniciar_hover = iniciar_rect.collidepoint(mouse_x, mouse_y)
        if iniciar_hover:
            pygame.draw.rect(screen, (0, 255, 0, 50), iniciar_rect)
        iniciar_texto = render_text("INICIAR JOGO", 24, (0, 255, 0) if iniciar_hover else (255, 255, 255), bold=True, pixel_style=True)
        screen.blit(iniciar_texto, (caixa_x + 60, caixa_y + caixa_altura - 90))
        
        # Botão voltar
        voltar_rect = pygame.Rect(caixa_x + 270, caixa_y + caixa_altura - 100, 200, 40)
        voltar_hover = voltar_rect.collidepoint(mouse_x, mouse_y)
        if voltar_hover:
            pygame.draw.rect(screen, (0, 200, 255, 50), voltar_rect)
        voltar_texto = render_text("VOLTAR", 24, (0, 200, 255) if voltar_hover else (255, 255, 255), bold=True, pixel_style=True)
        screen.blit(voltar_texto, (caixa_x + 280, caixa_y + caixa_altura - 90))
        
        # Desenhar popup de música
        popup_musica.desenhar(screen)
        
        pygame.display.flip()

def run():
    from config import CONFIGURACOES, carregar_configuracoes
    pygame.init()
    pygame.display.set_caption("Turbo Racer — Menu")
    
    # Recarregar configurações para garantir que estão atualizadas
    carregar_configuracoes()
    
    # Aplicar configurações de vídeo
    resolucao = CONFIGURACOES["video"]["resolucao"]
    fullscreen = CONFIGURACOES["video"]["fullscreen"]
    tela_cheIA_sem_bordas = CONFIGURACOES["video"]["tela_cheIA_sem_bordas"]
    qualidade_alta = CONFIGURACOES["video"]["qualidade_alta"]
    
    # Configurar flags de display
    display_flags = 0
    if fullscreen:
        display_flags |= pygame.FULLSCREEN
    elif tela_cheIA_sem_bordas:
        display_flags |= pygame.NOFRAME
    
    # Configurar qualidade
    if qualidade_alta:
        # Habilitar suavização para melhor qualidade
        pass
    
    screen = pygame.display.set_mode(resolucao, display_flags)
    
    # Loop principal que mantém a janela aberta
    carro_p1, carro_p2 = 0, 1  # Valores padrão
    
    # InicIAr música no menu se habilitada
    if CONFIGURACOES["audio"]["musica_habilitada"] and CONFIGURACOES["audio"]["musica_no_menu"]:
        gerencIAdor_musica.definir_volume(CONFIGURACOES["audio"]["volume_musica"])
        if not gerencIAdor_musica.musica_tocando:
            if CONFIGURACOES["audio"]["musica_aleatorIA"]:
                gerencIAdor_musica.musica_aleatorIA()
            else:
                gerencIAdor_musica.tocar_musica()
            if gerencIAdor_musica.musica_tocando:
                popup_musica.mostrar(gerencIAdor_musica.obter_nome_musica_atual())
    
    while True:
        escolha = menu_loop(screen)
        
        if escolha == Escolha.JOGAR:
            # Abrir tela de seleção de modo de jogo primeiro
            resultado_modo = modo_jogo_loop(screen)
            if resultado_modo:  # Se não cancelou
                modo_jogo, tipo_jogo = resultado_modo
                # Parar música do menu se não deve tocar no jogo
                if not CONFIGURACOES["audio"]["musica_no_jogo"]:
                    gerencIAdor_musica.parar_musica()
                # inicIA seu jogo original com carros selecionados e modos
                main.principal(carro_p1, carro_p2, modo_jogo=modo_jogo, tipo_jogo=tipo_jogo)
                # Após o jogo, volta para o menu (não fecha a janela)
                # ReinicIAr música do menu se habilitada
                if CONFIGURACOES["audio"]["musica_habilitada"] and CONFIGURACOES["audio"]["musica_no_menu"]:
                    if not gerencIAdor_musica.musica_tocando:
                        if CONFIGURACOES["audio"]["musica_aleatorIA"]:
                            gerencIAdor_musica.musica_aleatorIA()
                        else:
                            gerencIAdor_musica.tocar_musica()
                        if gerencIAdor_musica.musica_tocando:
                            popup_musica.mostrar(gerencIAdor_musica.obter_nome_musica_atual())
        elif escolha == Escolha.SELECIONAR_CARROS:
            # Abre tela de seleção de carros
            resultado = selecionar_carros_loop(screen)
            if resultado[0] is not None and resultado[1] is not None:
                carro_p1, carro_p2 = resultado
        elif escolha == Escolha.SELECIONAR_MAPAS:
            # Abre tela de seleção de mapas
            selecionar_mapas_loop(screen)
        elif escolha == Escolha.OPCOES:
            # Abre tela de opções
            opcoes_loop(screen)
            # Atualizar configurações de música após sair das opções
            gerencIAdor_musica.definir_volume(CONFIGURACOES["audio"]["volume_musica"])
            if not CONFIGURACOES["audio"]["musica_habilitada"]:
                gerencIAdor_musica.parar_musica()
            elif CONFIGURACOES["audio"]["musica_habilitada"] and CONFIGURACOES["audio"]["musica_no_menu"] and not gerencIAdor_musica.musica_tocando:
                if CONFIGURACOES["audio"]["musica_aleatorIA"]:
                    gerencIAdor_musica.musica_aleatorIA()
                else:
                    gerencIAdor_musica.tocar_musica()
                if gerencIAdor_musica.musica_tocando:
                    popup_musica.mostrar(gerencIAdor_musica.obter_nome_musica_atual())
        elif escolha == Escolha.SAIR:
            break
    
    pygame.quit()

if __name__ == "__main__":
    run()
