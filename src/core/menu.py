import os
import sys
import pygame
from enum import Enum

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import LARGURA, ALTURA, FPS, CAMINHO_MENU, CONFIGURACOES, MAPAS_DISPONIVEIS
import main
from core.musica import gerenciador_musica
from core.popup_musica import popup_musica
from core.game_modes import ModoJogo, TipoJogo
from core.progresso import gerenciador_progresso

def scale_to_cover(img_surf, target_w, target_h):
    iw, ih = img_surf.get_size()
    scale = max(target_w/iw, target_h/ih)
    surf = pygame.transform.smoothscale(img_surf, (int(iw*scale), int(ih*scale)))
    x = (surf.get_width() - target_w) // 2
    y = (surf.get_height() - target_h) // 2
    return surf.subsurface((x, y, target_w, target_h)).copy()

def verificar_clique_opcao(mouse_x, mouse_y, opcoes, caixa_x, caixa_y, caixa_largura, altura_item=50, offset_y=80, opcao_largura=None, scroll_offset=0):
    """Verifica se o mouse clicou em alguma opção e retorna o índice"""
    for i, (nome, chave) in enumerate(opcoes):
        if opcao_largura is None:
            # Layout padrão para submenus
            y = caixa_y + offset_y + i * altura_item - scroll_offset
            opcao_rect = pygame.Rect(caixa_x + 20, y - 5, caixa_largura - 40, altura_item)
        else:
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
    
    scrollbar_width = 12
    scrollbar_x = caixa_x + caixa_largura - scrollbar_width - 5
    scrollbar_y = caixa_y + 80
    scrollbar_height = caixa_altura - 200  # Altura da área de opções (deixando espaço para o botão voltar)
    
    scroll_ratio = scroll_offset / max_scroll if max_scroll > 0 else 0
    indicator_height = max(30, int(scrollbar_height * 0.3))  # 30% da altura da barra
    indicator_y = scrollbar_y + int(scroll_ratio * (scrollbar_height - indicator_height))
    
    scrollbar_bg = pygame.Surface((scrollbar_width, scrollbar_height), pygame.SRCALPHA)
    scrollbar_bg.fill((50, 50, 50, 150))
    screen.blit(scrollbar_bg, (scrollbar_x, scrollbar_y))
    
    indicator_bg = pygame.Surface((scrollbar_width - 2, indicator_height), pygame.SRCALPHA)
    indicator_bg.fill((150, 150, 150, 200))
    screen.blit(indicator_bg, (scrollbar_x + 1, indicator_y))
    
    pygame.draw.rect(screen, (255, 255, 255), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height), 1)

_pixel_font_atlas = None
_pixel_font_chars = {}

def load_pixel_font_atlas():
    """Carrega o atlas de fonte pixel art"""
    global _pixel_font_atlas, _pixel_font_chars
    
    if _pixel_font_atlas is None:
        try:
            if not pygame.get_init():
                pygame.init()
            _pixel_font_atlas = pygame.image.load("assets/fonts/pixel_font_atlas.png").convert_alpha()
            
            char_width = 8
            char_height = 12
            chars_per_row = 10
            
            for ascii_code in range(32, 127):
                char = chr(ascii_code)
                char_index = ascii_code - 32
                
                row = char_index // chars_per_row
                col = char_index % chars_per_row
                
                x = col * char_width
                y = row * char_height
                
                char_surface = pygame.Surface((char_width, char_height), pygame.SRCALPHA)
                char_surface.blit(_pixel_font_atlas, (0, 0), (x, y, char_width, char_height))
                _pixel_font_chars[char] = char_surface
            
            special_chars = ['ç', 'Ç', 'ã', 'Ã', 'õ', 'Õ', 'á', 'Á', 'à', 'À', 'â', 'Â', 
                           'é', 'É', 'ê', 'Ê', 'í', 'Í', 'ó', 'Ó', 'ô', 'Ô', 'ú', 'Ú', 
                           'ü', 'Ü', 'ñ', 'Ñ']
            
            char_index = 95  # 127 - 32 = 95 (posição após ASCII 32-126)
            
            for char in special_chars:
                row = char_index // chars_per_row
                col = char_index % chars_per_row
                
                x = col * char_width
                y = row * char_height
                
                char_surface = pygame.Surface((char_width, char_height), pygame.SRCALPHA)
                char_surface.blit(_pixel_font_atlas, (0, 0), (x, y, char_width, char_height))
                _pixel_font_chars[char] = char_surface
                
                char_index += 1
                
        except Exception as e:
            print(f"Erro ao carregar atlas de fonte pixel art: {e}")
            _pixel_font_atlas = None

def render_pixel_text(text, size, color=(255,255,255)):
    """Renderiza texto usando fonte pixel art do atlas"""
    load_pixel_font_atlas()
    
    if _pixel_font_atlas is None:
        font = pygame.font.SysFont("consolas", size, bold=True)
        return font.render(text, True, color)
    
    base_size = 12  # Tamanho base dos caracteres no atlas
    scale = size / base_size
    
    char_width = int(8 * scale)
    char_height = int(12 * scale)
    
    text_width = len(text) * char_width
    text_height = char_height
    text_surface = pygame.Surface((text_width, text_height), pygame.SRCALPHA)
    
    for i, char in enumerate(text):
        if char in _pixel_font_chars:
            char_surface = _pixel_font_chars[char]
            
            if scale != 1.0:
                char_surface = pygame.transform.scale(char_surface, (char_width, char_height))
            
            char_colored = pygame.Surface(char_surface.get_size(), pygame.SRCALPHA)
            
            for x in range(char_surface.get_width()):
                for y in range(char_surface.get_height()):
                    pixel = char_surface.get_at((x, y))
                    if pixel[0] > 128:  # Se é um pixel branco (caractere)
                        char_colored.set_at((x, y), (*color, 255))
            
            x = i * char_width
            text_surface.blit(char_colored, (x, 0))
        else:
            font_fallback = pygame.font.SysFont("consolas", size, bold=True)
            char_surface = font_fallback.render(char, True, color)
            char_surface = pygame.transform.scale(char_surface, (char_width, char_height))
            x = i * char_width
            text_surface.blit(char_surface, (x, 0))
    
    return text_surface

def render_text(text, size, color=(255,255,255), bold=True, pixel_style=True):
    pygame.font.init()
    
    if pixel_style:
        pixel_fonts = [
            "assets/fonts/PixeloidSans.ttf",           # PixeloidSans (pixel art com acentos)
            "assets/fonts/ByteBounce.ttf",             # ByteBounce (pixel art com acentos)
            "assets/fonts/PressStart2P-Regular.ttf",  # Press Start 2P (clássica)
            "assets/fonts/04b_03.ttf",               # 04b_03 (pixel art clássica)
            "assets/fonts/04b_08.ttf",               # 04b_08 (pixel art moderna)
            "assets/fonts/pixel_font.ttf",           # Fonte customizada
            "assets/fonts/retro_font.ttf",           # Fonte retrô customizada
        ]
        
        # Se não encontrar fontes TTF, usar fontes do sistema com aparência pixel art
        if not any(os.path.exists(font_path) for font_path in pixel_fonts):
            # Usar fontes do sistema que suportam acentos
            system_fonts = [
                "consolas",      # Consolas (monospace, suporta acentos)
                "courier",       # Courier (monospace, suporta acentos)
                "lucida console", # Lucida Console (monospace, suporta acentos)
                "arial"          # Arial (fallback)
            ]
            
            for font_name in system_fonts:
                try:
                    font = pygame.font.SysFont(font_name, size, bold=bold)
                    # Aplicar efeito pixel art (escalar para baixo e depois para cima)
                    if size > 12:
                        # Criar superfície pequena para efeito pixel
                        small_size = max(8, size // 2)
                        small_font = pygame.font.SysFont(font_name, small_size, bold=bold)
                        small_surface = small_font.render(text, True, color)
                        # Escalar para o tamanho desejado
                        font = pygame.transform.scale(small_surface, (small_surface.get_width() * 2, small_surface.get_height() * 2))
                    break
                except:
                    continue
        
        font = None
        for font_path in pixel_fonts:
            try:
                font = pygame.font.Font(font_path, size)
                break
            except:
                continue
        
        # Se nenhuma fonte pixel art funcionar, usar fontes do sistema com suporte a acentos
        if font is None:
            # Tentar fontes que suportam acentos e têm aparência pixel art
            system_fonts = [
                "consolas",      # Consolas (monospace, suporta acentos)
                "courier",       # Courier (monospace, suporta acentos)
                "lucida console", # Lucida Console (monospace, suporta acentos)
                "monaco",        # Monaco (se disponível)
                "menlo",         # Menlo (se disponível)
                "arial"          # Arial (fallback)
            ]
            
            for font_name in system_fonts:
                try:
                    font = pygame.font.SysFont(font_name, size, bold=bold)
                    break
                except:
                    continue
    else:
        font = pygame.font.SysFont("arial", size, bold=bold)
    
    # Renderizar texto com contorno para estilo pixel art
    if pixel_style and size >= 16:
        # Criar contorno preto para texto pixel art
        text_surface = font.render(text, True, color)
        outline_surface = font.render(text, True, (0, 0, 0))
        
        # Criar superfície maior para o contorno
        outline_width = 2 if size < 32 else 3
        final_surface = pygame.Surface((text_surface.get_width() + outline_width * 2, text_surface.get_height() + outline_width * 2), pygame.SRCALPHA)
        
        # Desenhar contorno (8 posições para contorno mais suave)
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    final_surface.blit(outline_surface, (outline_width + dx, outline_width + dy))
        
        # Desenhar texto principal
        final_surface.blit(text_surface, (outline_width, outline_width))
        
        return final_surface
    else:
        return font.render(text, True, color)

class Escolha(Enum):
    SELECIONAR_CARROS = 0
    JOGAR = 1
    RECORDES = 2
    OPCOES = 3
    SAIR = 4

def splash_screen(screen) -> bool:
    """Tela de splash com 'Aperte qualquer botão para iniciar'"""
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)
    
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    
    fade_surface = pygame.Surface((LARGURA, ALTURA))
    fade_surface.fill((0, 0, 0))
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        gerenciador_musica.verificar_fim_musica()
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYDOWN or ev.type == pygame.MOUSEBUTTONDOWN:
                return True
        
        screen.blit(bg, (0, 0))
        
        elapsed = pygame.time.get_ticks() - start_time
        fade_alpha = max(0, 255 - int((elapsed / 2000.0) * 255))
        
        if fade_alpha > 0:
            fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0, 0))
        from core.i18n import t
        blink_time = (pygame.time.get_ticks() % 2000) / 2000.0
        if blink_time < 0.5:  # Pisca a cada 1 segundo
            texto_iniciar = render_text(t("menu.splash.pressione_qualquer_botao"), 24, (0, 200, 255), bold=True, pixel_style=True)
            texto_iniciar_x = (LARGURA - texto_iniciar.get_width()) // 2
            texto_iniciar_y = ALTURA // 2 + 50
            screen.blit(texto_iniciar, (texto_iniciar_x, texto_iniciar_y))
        
        pygame.display.flip()

def menu_loop(screen) -> Escolha:
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)

    from core.i18n import t
    itens = [t("menu.principal.selecionar_carros"), t("menu.principal.jogar"), t("menu.principal.recordes"), t("menu.principal.opcoes"), t("menu.principal.sair")]
    idx = 1
    clock = pygame.time.Clock()

    itens_completos = [t("menu.principal.selecionar_carros"), t("menu.principal.jogar"), t("menu.principal.recordes"), t("menu.principal.opcoes"), t("menu.principal.sair")]
    base_y = int(ALTURA * 0.85)
    
    jogar_largura = 280
    jogar_altura = 70
    botao_largura = 180
    botao_sel_carros_largura = 220
    botao_altura = 50
    espacamento = 15
    
    jogar_y = base_y + (botao_altura - jogar_altura) // 2
    jogar_x = (LARGURA - jogar_largura) // 2
    
    outros_posicoes = []
    outros_itens = [t("menu.principal.recordes"), t("menu.principal.selecionar_carros"), t("menu.principal.opcoes"), t("menu.principal.sair")]
    
    espaco_esquerda = jogar_x - espacamento
    espaco_direita = LARGURA - (jogar_x + jogar_largura) - espacamento
    
    outros_posicoes.append((jogar_x - espacamento - botao_sel_carros_largura - espacamento - botao_largura, base_y))
    outros_posicoes.append((jogar_x - espacamento - botao_sel_carros_largura, base_y))
    outros_posicoes.append((jogar_x + jogar_largura + espacamento, base_y))
    outros_posicoes.append((jogar_x + jogar_largura + espacamento + botao_largura + espacamento, base_y))
    
    hover_animation = [0.0] * len(itens)
    hover_speed = 8.0

    while True:
        dt = clock.tick(FPS) / 1000.0
        
        gerenciador_musica.verificar_fim_musica()
        popup_musica.atualizar(dt)
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        popup_musica.verificar_hover(mouse_x, mouse_y)
        
        for i in range(len(itens)):
            if i == 1:
                rect = pygame.Rect(jogar_x, jogar_y, jogar_largura, jogar_altura)
            else:
                if i == 0:
                    x, y = outros_posicoes[1]
                    largura = botao_sel_carros_largura
                elif i == 2:
                    x, y = outros_posicoes[0]
                    largura = botao_largura
                elif i == 3:
                    x, y = outros_posicoes[2]
                    largura = botao_largura
                else:
                    x, y = outros_posicoes[3]
                    largura = botao_largura
                rect = pygame.Rect(x, y, largura, botao_altura)
            
            is_hovering = rect.collidepoint(mouse_x, mouse_y)
            
            if is_hovering:
                hover_animation[i] = min(1.0, hover_animation[i] + hover_speed * dt)
            else:
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt)
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return Escolha.SAIR
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_LEFT, pygame.K_a):
                    # Navegação baseada na ordem visual: RECORDES (2), SELECIONAR CARROS (0), JOGAR (1), OPÇÕES (3), SAIR (4)
                    # Ordem visual da esquerda para direita: 2, 0, 1, 3, 4
                    # Mapeamento: idx -> esquerda
                    navegacao_esquerda = {
                        0: 2,     # SELECIONAR CARROS -> RECORDES
                        1: 0,     # JOGAR -> SELECIONAR CARROS
                        2: None,  # RECORDES -> não tem esquerda (primeiro)
                        3: 1,     # OPÇÕES -> JOGAR
                        4: 3      # SAIR -> OPÇÕES
                    }
                    novo_idx = navegacao_esquerda.get(idx)
                    if novo_idx is not None:
                        idx = novo_idx
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    # Mapeamento: idx -> direita
                    navegacao_direita = {
                        0: 1,     # SELECIONAR CARROS -> JOGAR
                        1: 3,     # JOGAR -> OPÇÕES
                        2: 0,     # RECORDES -> SELECIONAR CARROS
                        3: 4,     # OPÇÕES -> SAIR
                        4: None   # SAIR -> não tem direita (último)
                    }
                    novo_idx = navegacao_direita.get(idx)
                    if novo_idx is not None:
                        idx = novo_idx
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return Escolha(idx)
                elif ev.key == pygame.K_ESCAPE:
                    return Escolha.SAIR
                elif ev.key == pygame.K_m:
                    gerenciador_musica.proxima_musica()
                    if gerenciador_musica.musica_tocando:
                        popup_musica.mostrar(gerenciador_musica.obter_nome_musica_atual())
                elif ev.key == pygame.K_n:
                    gerenciador_musica.musica_anterior()
                    if gerenciador_musica.musica_tocando:
                        popup_musica.mostrar(gerenciador_musica.obter_nome_musica_atual())
            if ev.type == pygame.MOUSEMOTION:
                mx, my = ev.pos
                for i in range(len(itens)):
                    if i == 1:  # Botão JOGAR (segundo na nova ordem)
                        rect = pygame.Rect(jogar_x, jogar_y, jogar_largura, jogar_altura)
                    else:  # Outros botões
                        if i == 0:  # SELECIONAR CARROS
                            x, y = outros_posicoes[1]
                            largura = botao_sel_carros_largura
                        elif i == 2:  # RECORDES
                            x, y = outros_posicoes[0]
                            largura = botao_largura
                        elif i == 3:  # OPÇÕES
                            x, y = outros_posicoes[2]
                            largura = botao_largura
                        else:  # SAIR (i == 4)
                            x, y = outros_posicoes[3]
                            largura = botao_largura
                        rect = pygame.Rect(x, y, largura, botao_altura)
                    if rect.collidepoint(mx, my):
                        idx = i
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                clique_popup = popup_musica.verificar_clique(ev.pos[0], ev.pos[1])
                if clique_popup == "anterior":
                    gerenciador_musica.musica_anterior()
                    if gerenciador_musica.musica_tocando:
                        popup_musica.mostrar(gerenciador_musica.obter_nome_musica_atual())
                elif clique_popup == "proximo":
                    gerenciador_musica.proxima_musica()
                    if gerenciador_musica.musica_tocando:
                        popup_musica.mostrar(gerenciador_musica.obter_nome_musica_atual())
                else:
                    mouse_x, mouse_y = ev.pos
                    for i, txt in enumerate(itens):
                        if i == 1:  # Botão JOGAR (segundo na nova ordem)
                            botao_rect = pygame.Rect(jogar_x, jogar_y, jogar_largura, jogar_altura)
                        else:  # Outros botões
                            if i == 0:  # SELECIONAR CARROS
                                x, y = outros_posicoes[1]
                                largura = botao_sel_carros_largura
                            elif i == 2:  # RECORDES
                                x, y = outros_posicoes[0]
                                largura = botao_largura
                            elif i == 3:  # OPÇÕES
                                x, y = outros_posicoes[2]
                                largura = botao_largura
                            else:  # SAIR (i == 4)
                                x, y = outros_posicoes[3]
                                largura = botao_largura
                            botao_rect = pygame.Rect(x, y, largura, botao_altura)
                        if botao_rect.collidepoint(mouse_x, mouse_y):
                            return Escolha(i)

        # desenha
        screen.blit(bg, (0, 0))

        # Renderizar todos os botões na mesma linha
        for i, txt in enumerate(itens):
            sel = (i == idx)
            hover_progress = hover_animation[i]  # Progresso da animação de hover (0.0 a 1.0)
            
            # Posição e tamanho do botão
            if i == 1:  # Botão JOGAR (segundo na nova ordem)
                x, y = jogar_x, jogar_y
                largura, altura = jogar_largura, jogar_altura
                fonte_tamanho = 24  # Fonte maior para JOGAR
                borda_espessura = 4  # Borda mais espessa para JOGAR
            else:  # Outros botões
                if i == 0:  # SELECIONAR CARROS
                    x, y = outros_posicoes[1]
                    largura = botao_sel_carros_largura
                elif i == 2:  # RECORDES
                    x, y = outros_posicoes[0]
                    largura = botao_largura
                elif i == 3:  # OPÇÕES
                    x, y = outros_posicoes[2]
                    largura = botao_largura
                else:  # SAIR (i == 4)
                    x, y = outros_posicoes[3]
                    largura = botao_largura
                altura = botao_altura
                fonte_tamanho = 16  # Fonte menor para outros
                borda_espessura = 3  # Borda normal para outros
            
            # Cores base do botão
            if sel:
                # Botão selecionado (teclado)
                base_cor_fundo = (0, 150, 255, 120)  # Azul ciano vibrante
                base_cor_borda = (0, 200, 255)  # Borda azul ciano
                base_cor_texto = (255, 255, 255)  # Texto branco
            else:
                # Botão normal
                base_cor_fundo = (0, 0, 0, 150)  # Preto semi-transparente
                base_cor_borda = (255, 255, 255)  # Borda branca
                base_cor_texto = (255, 255, 255)  # Texto branco
            
            # Aplicar animação de hover
            if hover_progress > 0:
                # Cores de hover (azul ciano vibrante)
                hover_cor_fundo = (0, 150, 255, 120)  # Azul ciano
                hover_cor_borda = (0, 200, 255)  # Borda azul ciano
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
            scaled_width = int(largura * scale_factor)
            scaled_height = int(altura * scale_factor)
            offset_x = (scaled_width - largura) // 2
            offset_y = (scaled_height - altura) // 2
            
            # Desenhar fundo do botão com escala
            botao_fundo = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
            botao_fundo.fill(cor_fundo)
            screen.blit(botao_fundo, (x - offset_x, y - offset_y))
            
            # Desenhar borda do botão com escala
            pygame.draw.rect(screen, cor_borda, (x - offset_x, y - offset_y, scaled_width, scaled_height), borda_espessura)
            
            # Desenhar texto do botão centralizado
            texto_surface = render_text(txt, fonte_tamanho, cor_texto, bold=True, pixel_style=True)
            texto_x = x + (largura - texto_surface.get_width()) // 2
            texto_y = y + (altura - texto_surface.get_height()) // 2
            screen.blit(texto_surface, (texto_x, texto_y))
            
            # Efeito de glow no hover
            if hover_progress > 0:
                glow_intensity = int(30 * hover_progress)
                glow_surface = pygame.Surface((scaled_width + 10, scaled_height + 10), pygame.SRCALPHA)
                glow_surface.fill((0, 200, 255, glow_intensity))  # Glow azul ciano
                screen.blit(glow_surface, (x - offset_x - 5, y - offset_y - 5))
            
            if sel:
                # Efeito de brilho/glow sob o botão ativo (teclado)
                glow_surface = pygame.Surface((scaled_width + 20, scaled_height + 20), pygame.SRCALPHA)
                glow_surface.fill((0, 200, 255, 20))  # Glow sutil
                screen.blit(glow_surface, (x - offset_x - 10, y - offset_y - 10))

        # Desenhar pop-up de música
        popup_musica.desenhar(screen)
        
        pygame.display.flip()

def selecionar_mapas_loop(screen):
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)
    
    from config import obter_lista_mapas, obter_nome_mapa, recarregar_mapas
    mapas = obter_lista_mapas()
    indice = 0
    relogio = pygame.time.Clock()
    
    # Layout padronizado como o submenu JOGAR
    caixa_largura = 600
    caixa_altura = 400
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2
    
    # Animações de hover
    hover_animation_mapas = [0.0] * len(mapas)
    hover_speed = 8.0  # Velocidade aumentada
    
    while True:
        dt = relogio.tick(FPS) / 1000.0
        
        gerenciador_musica.verificar_fim_musica()
        popup_musica.atualizar(dt)
        
        # Verificar hover do pop-up
        mouse_x, mouse_y = pygame.mouse.get_pos()
        popup_musica.verificar_hover(mouse_x, mouse_y)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Verificar clique no pop-up de música primeiro
                clique_popup = popup_musica.verificar_clique(event.pos[0], event.pos[1])
                if clique_popup == "anterior":
                    gerenciador_musica.musica_anterior()
                    if gerenciador_musica.musica_tocando:
                        popup_musica.mostrar(gerenciador_musica.obter_nome_musica_atual())
                elif clique_popup == "proximo":
                    gerenciador_musica.proxima_musica()
                    if gerenciador_musica.musica_tocando:
                        popup_musica.mostrar(gerenciador_musica.obter_nome_musica_atual())
                else:
                    # Verificar clique nos mapas
                    mouse_x, mouse_y = event.pos
                    
                    for i, mapa_id in enumerate(mapas):
                        y = caixa_y + 120 + i * 50
                        rect = pygame.Rect(caixa_x + 50, y - 5, 500, 40)
                        if rect.collidepoint(mouse_x, mouse_y):
                            indice = i
                            mapa_selecionado = mapas[indice]
                            main.principal(mapa_selecionado=mapa_selecionado)
                            return None
                    
                    # Verificar clique no botão voltar
                    voltar_rect = pygame.Rect(caixa_x + 200, caixa_y + caixa_altura - 50, 200, 40)
                    if voltar_rect.collidepoint(mouse_x, mouse_y):
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
                    gerenciador_musica.proxima_musica()
                    if gerenciador_musica.musica_tocando:
                        popup_musica.mostrar(gerenciador_musica.obter_nome_musica_atual())
                elif event.key == pygame.K_r:
                    # Recarregar mapas
                    if recarregar_mapas():
                        mapas = obter_lista_mapas()
                        indice = 0
                        from core.i18n import t
                        popup_musica.mostrar(t("mensagens.mapas_recarregados"), tipo="outra")
                    else:
                        from core.i18n import t
                        popup_musica.mostrar(t("mensagens.nenhum_mapa_novo"), tipo="outra")
        
        screen.blit(bg, (0, 0))
        
        # Caixa principal (padrão do submenu JOGAR)
        pygame.draw.rect(screen, (0, 0, 0, 150), (caixa_x, caixa_y, caixa_largura, caixa_altura))
        pygame.draw.rect(screen, (255, 255, 255, 50), (caixa_x, caixa_y, caixa_largura, caixa_altura), 2)
        
        # Título
        from core.i18n import t
        titulo = render_text(t("menu.selecionar_mapa.titulo"), 32, (255, 255, 255), bold=True, pixel_style=True)
        titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, caixa_y + 20))
        
        # Lista de mapas
        for i, mapa_id in enumerate(mapas):
            nome_mapa = obter_nome_mapa(mapa_id)
            y = caixa_y + 120 + i * 50
            
            # Cores baseadas na seleção e hover
            if i == indice:
                cor_fundo = (0, 200, 255, 50)
                cor_texto = (0, 200, 255)
            else:
                cor_fundo = (0, 0, 0, 0)
                cor_texto = (255, 255, 255)
            
            # Aplicar hover
            hover_progress = hover_animation_mapas[i]
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
                opcao_fundo = pygame.Surface((500, 40), pygame.SRCALPHA)
                opcao_fundo.fill(cor_fundo)
                screen.blit(opcao_fundo, (caixa_x + 50, y - 5))
            
            # Desenhar texto
            texto = render_text(nome_mapa, 20, cor_texto, bold=True, pixel_style=True)
            screen.blit(texto, (caixa_x + 60, y))
        
        # Botão voltar
        voltar_rect = pygame.Rect(caixa_x + 200, caixa_y + caixa_altura - 50, 200, 40)
        voltar_hover = voltar_rect.collidepoint(mouse_x, mouse_y)
        if voltar_hover:
            pygame.draw.rect(screen, (0, 200, 255, 50), voltar_rect)
        from core.i18n import t
        voltar_texto = render_text(t("menu.selecionar_mapa.voltar"), 24, (0, 200, 255) if voltar_hover else (255, 255, 255), bold=True, pixel_style=True)
        screen.blit(voltar_texto, (caixa_x + 210, caixa_y + caixa_altura - 50))
        
        # Instruções
        from core.i18n import t
        instrucoes = [
            t("menu.selecionar_mapa.instrucao_navegar"),
            t("menu.selecionar_mapa.instrucao_atalhos")
        ]
        
        for j, instrucao in enumerate(instrucoes):
            texto_instrucao = render_text(instrucao, 16, (200, 200, 200), pixel_style=True)
            screen.blit(texto_instrucao, (caixa_x + 50, caixa_y + caixa_altura - 80 + j * 20))
        
        # Desenhar popup de música
        popup_musica.desenhar(screen)
        
        pygame.display.flip()

def selecionar_carros_loop(screen):
    from config import CAMINHO_OFICINA, DIR_SPRITES, DIR_CAR_SELECTION
    bg_raw = pygame.image.load(CAMINHO_OFICINA).convert_alpha()
    # Usar scale simples (como no editor) para mostrar a imagem completa sem cortar
    bg = pygame.transform.scale(bg_raw, (LARGURA, ALTURA))
    
    # Importar a lista de carros do main
    from main import CARROS_DISPONIVEIS
    
    carro_p1 = 0
    carro_p2 = 0
    fase_selecao = 1  # 1 = P1 selecionando, 2 = P2 selecionando, 3 = confirmando
    
    # Variáveis para transição
    transicao_ativa = False
    transicao_tempo = 0.0
    transicao_duracao = 0.5  # 500ms - velocidade intermediária
    transicao_direcao = 1  # 1 = direita para esquerda, -1 = esquerda para direita
    carro_atual_pos = 0.0  # Posição X do carro atual (0 = centro)
    carro_proximo_pos = 1.0  # Posição X do próximo carro (1 = fora da tela direita)
    carro_anterior = None  # Carro que estava sendo exibido antes da transição
    
    # Carregar ícone de cadeado
    icone_cadeado = None
    caminho_cadeado = os.path.join("assets", "images", "icons", "Locked.png")
    if os.path.exists(caminho_cadeado):
        icone_cadeado = pygame.image.load(caminho_cadeado).convert_alpha()
        # Redimensionar para tamanho adequado
        icone_cadeado = pygame.transform.scale(icone_cadeado, (80, 80))
    
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
            
            # Criar canvas com tamanho individual
            sprite = pygame.Surface((canvas_largura, canvas_altura), pygame.SRCALPHA)
            
            # Centralizar horizontalmente e posicionar na parte inferior (encostado no chão)
            x_offset = (canvas_largura - nova_largura) // 2
            y_offset = canvas_altura - nova_altura - 5  # Posicionar mais baixo, quase no chão
            sprite.blit(sprite_redimensionado, (x_offset, y_offset))
            
            sprites_carros[carro['prefixo_cor']] = sprite
        except:
            # Se não conseguir carregar, criar um retângulo como fallback
            tamanho_oficina = carro.get('tamanho_oficina', (600, 300))
            sprite = pygame.Surface(tamanho_oficina, pygame.SRCALPHA)
            pygame.draw.rect(sprite, (100, 100, 100), (0, 0, tamanho_oficina[0], tamanho_oficina[1]))
            sprites_carros[carro['prefixo_cor']] = sprite
    
    def iniciar_transicao(direcao, carro_atual_idx):
        """Inicia uma transição entre carros"""
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
            # Interpolação suave (ease-out para mais responsividade)
            progresso = transicao_tempo / transicao_duracao
            # Ease-out cubic: começa rápido e termina suave
            progresso = 1 - pow(1 - progresso, 3)
            
            # Carro atual sai pela direção oposta
            carro_atual_pos = -transicao_direcao * progresso
            # Próximo carro entra pela direção oposta
            carro_proximo_pos = transicao_direcao * (1 - progresso)
    
    clock = pygame.time.Clock()
    
    while True:
        dt = clock.tick(FPS) / 1000.0  # Converter para segundos
        
        # Atualizar transição
        atualizar_transicao(dt)
        
        # Atualizar popup de música
        popup_musica.atualizar(dt)
        
        # Calcular posições dos botões antes de processar eventos
        botao_usar_rect_p1 = None
        botao_comprar_rect_p1 = None
        botao_usar_rect_p2 = None
        botao_comprar_rect_p2 = None
        
        # Calcular posições dos botões para P1
        if fase_selecao == 1:
            carro_atual_p1 = CARROS_DISPONIVEIS[carro_p1]
            esta_desbloqueado_p1 = gerenciador_progresso.esta_desbloqueado(carro_atual_p1['prefixo_cor'])
            info_x_p1 = LARGURA - 300
            info_y_p1 = 180
            info_altura_p1 = 380
            botao_y_p1 = info_y_p1 + info_altura_p1 + 20
            botao_largura_p1 = 130
            botao_altura_p1 = 45
            espacamento_botoes_p1 = 15
            info_largura_p1 = 280
            botoes_x_inicial_p1 = info_x_p1 + (info_largura_p1 - (botao_largura_p1 * 2 + espacamento_botoes_p1)) // 2
            
            if esta_desbloqueado_p1:
                botao_usar_rect_p1 = pygame.Rect(botoes_x_inicial_p1, botao_y_p1, botao_largura_p1, botao_altura_p1)
            else:
                botao_comprar_rect_p1 = pygame.Rect(botoes_x_inicial_p1, botao_y_p1, botao_largura_p1, botao_altura_p1)
        
        # Calcular posições dos botões para P2
        if fase_selecao == 2:
            carro_atual_p2 = CARROS_DISPONIVEIS[carro_p2]
            esta_desbloqueado_p2 = gerenciador_progresso.esta_desbloqueado(carro_atual_p2['prefixo_cor'])
            info_x_p2 = LARGURA - 300
            info_y_p2 = 180
            info_altura_p2 = 380
            botao_y_p2 = info_y_p2 + info_altura_p2 + 20
            botao_largura_p2 = 130
            botao_altura_p2 = 45
            espacamento_botoes_p2 = 15
            info_largura_p2 = 280
            botoes_x_inicial_p2 = info_x_p2 + (info_largura_p2 - (botao_largura_p2 * 2 + espacamento_botoes_p2)) // 2
            
            if esta_desbloqueado_p2:
                botao_usar_rect_p2 = pygame.Rect(botoes_x_inicial_p2, botao_y_p2, botao_largura_p2, botao_altura_p2)
            else:
                botao_comprar_rect_p2 = pygame.Rect(botoes_x_inicial_p2, botao_y_p2, botao_largura_p2, botao_altura_p2)
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return None, None
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # Verificar clique nos botões
                if not transicao_ativa:
                    mouse_x, mouse_y = ev.pos
                    
                    if fase_selecao == 1:
                        carro_atual = CARROS_DISPONIVEIS[carro_p1]
                        esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                        
                        if esta_desbloqueado:
                            # Verificar clique no botão USAR
                            if botao_usar_rect_p1 and botao_usar_rect_p1.collidepoint(mouse_x, mouse_y):
                                fase_selecao = 2  # P1 confirmou, vai para P2
                        else:
                            # Verificar clique no botão COMPRAR
                            if botao_comprar_rect_p1 and botao_comprar_rect_p1.collidepoint(mouse_x, mouse_y):
                                preco = carro_atual.get('preco', 0)
                                if gerenciador_progresso.comprar_carro(carro_atual['prefixo_cor'], preco):
                                    from core.i18n import t
                                    popup_musica.mostrar(t("mensagens.carro_comprado").format(carro_atual['nome']), tipo="outra")
                                else:
                                    from core.i18n import t
                                    popup_musica.mostrar(t("mensagens.dinheiro_insuficiente"), tipo="outra")
                    elif fase_selecao == 2:
                        carro_atual = CARROS_DISPONIVEIS[carro_p2]
                        esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                        
                        if esta_desbloqueado:
                            # Verificar clique no botão USAR
                            if botao_usar_rect_p2 and botao_usar_rect_p2.collidepoint(mouse_x, mouse_y):
                                return carro_p1, carro_p2  # P2 confirmou, retorna seleções
                        else:
                            # Verificar clique no botão COMPRAR
                            if botao_comprar_rect_p2 and botao_comprar_rect_p2.collidepoint(mouse_x, mouse_y):
                                preco = carro_atual.get('preco', 0)
                                if gerenciador_progresso.comprar_carro(carro_atual['prefixo_cor'], preco):
                                    from core.i18n import t
                                    popup_musica.mostrar(t("mensagens.carro_comprado").format(carro_atual['nome']), tipo="outra")
                                else:
                                    from core.i18n import t
                                    popup_musica.mostrar(t("mensagens.dinheiro_insuficiente"), tipo="outra")
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return None, None
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    if not transicao_ativa:  # Só permite navegação se não estiver em transição
                        if fase_selecao == 1:
                            iniciar_transicao(-1, carro_p1)  # Esquerda para direita
                            carro_p1 = (carro_p1 - 1) % len(CARROS_DISPONIVEIS)
                        elif fase_selecao == 2:
                            iniciar_transicao(-1, carro_p2)  # Esquerda para direita
                            carro_p2 = (carro_p2 - 1) % len(CARROS_DISPONIVEIS)
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    if not transicao_ativa:  # Só permite navegação se não estiver em transição
                        if fase_selecao == 1:
                            iniciar_transicao(1, carro_p1)  # Direita para esquerda
                            carro_p1 = (carro_p1 + 1) % len(CARROS_DISPONIVEIS)
                        elif fase_selecao == 2:
                            iniciar_transicao(1, carro_p2)  # Direita para esquerda
                            carro_p2 = (carro_p2 + 1) % len(CARROS_DISPONIVEIS)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if not transicao_ativa:  # Só permite confirmação se não estiver em transição
                        if fase_selecao == 1:
                            carro_atual = CARROS_DISPONIVEIS[carro_p1]
                            esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                            if esta_desbloqueado:
                                fase_selecao = 2  # P1 confirmou, vai para P2
                        elif fase_selecao == 2:
                            carro_atual = CARROS_DISPONIVEIS[carro_p2]
                            esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                            if esta_desbloqueado:
                                return carro_p1, carro_p2  # P2 confirmou, retorna seleções
                elif ev.key == pygame.K_b:
                    # Tentar comprar carro
                    if not transicao_ativa:
                        if fase_selecao == 1:
                            carro_atual = CARROS_DISPONIVEIS[carro_p1]
                        else:
                            carro_atual = CARROS_DISPONIVEIS[carro_p2]
                        esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                        if not esta_desbloqueado:
                            preco = carro_atual.get('preco', 0)
                            if gerenciador_progresso.comprar_carro(carro_atual['prefixo_cor'], preco):
                                popup_musica.mostrar(f"Carro {carro_atual['nome']} comprado!", tipo="outra")
                            else:
                                popup_musica.mostrar("Dinheiro insuficiente!", tipo="outra")
        
        # Desenhar
        screen.blit(bg, (0, 0))
        
        # Overlay escuro sutil
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        screen.blit(overlay, (0, 0))
        
        from core.i18n import t
        # Mostrar dinheiro no topo (dourado suave harmonizado)
        dinheiro_texto = t("menu.oficina.dinheiro").format(gerenciador_progresso.dinheiro)
        dinheiro_render = render_text(dinheiro_texto, 32, (255, 220, 100), bold=True, pixel_style=True)
        screen.blit(dinheiro_render, (20, 20))
        
        # Título - estilo pixel art (azul ciano harmonizado) - mais espaçado
        titulo = render_text(t("menu.oficina.titulo"), 48, (100, 220, 255), bold=True, pixel_style=True)
        titulo_x = (LARGURA - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, 30))
        
        if fase_selecao == 1:
            # FASE 1: Player 1 selecionando (azul claro harmonizado) - mais espaçado
            subtitulo = render_text(t("menu.oficina.jogador_1"), 32, (150, 220, 255), bold=True, pixel_style=True)
            subtitulo_x = (LARGURA - subtitulo.get_width()) // 2
            screen.blit(subtitulo, (subtitulo_x, 90))
            
            # Instruções - mais espaçado
            carro_atual = CARROS_DISPONIVEIS[carro_p1]
            esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
            if esta_desbloqueado:
                instrucoes = render_text(t("menu.oficina.navegar_confirmar"), 20, (255, 255, 255), bold=True, pixel_style=True)
            else:
                instrucoes = render_text(t("menu.oficina.navegar_comprar"), 20, (255, 255, 255), bold=True, pixel_style=True)
            instrucoes_x = (LARGURA - instrucoes.get_width()) // 2
            screen.blit(instrucoes, (instrucoes_x, 130))
            
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
                
                # Usar float para suavidade e depois converter para int apenas na renderização
                pos_x_anterior = pos_anterior[0] + carro_atual_pos * LARGURA
                pos_x_atual = pos_atual[0] + carro_proximo_pos * LARGURA
                
                # Desenhar carro anterior saindo (converter para int apenas na renderização)
                screen.blit(sprite_anterior, (int(pos_x_anterior), pos_anterior[1]))
                # Desenhar novo carro entrando
                screen.blit(sprite_atual, (int(pos_x_atual), pos_atual[1]))
                
                # Desenhar cadeado se o carro atual não estiver desbloqueado
                esta_desbloqueado_atual = gerenciador_progresso.esta_desbloqueado(carro_atual_obj['prefixo_cor'])
                if not esta_desbloqueado_atual and icone_cadeado:
                    cadeado_x = int(pos_x_atual) + (sprite_atual.get_width() - icone_cadeado.get_width()) // 2
                    cadeado_y = pos_atual[1] + (sprite_atual.get_height() - icone_cadeado.get_height()) // 2
                    screen.blit(icone_cadeado, (cadeado_x, cadeado_y))
            else:
                # Sem transição: desenhar carro atual normalmente
                carro_atual = CARROS_DISPONIVEIS[carro_p1]
                sprite_atual = sprites_carros[carro_atual['prefixo_cor']]
                posicao = carro_atual.get('posicao_oficina', (LARGURA//2 - 300, 380))
                screen.blit(sprite_atual, posicao)
                
                # Desenhar cadeado se o carro não estiver desbloqueado
                esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                if not esta_desbloqueado and icone_cadeado:
                    # Centralizar cadeado sobre o carro
                    cadeado_x = posicao[0] + (sprite_atual.get_width() - icone_cadeado.get_width()) // 2
                    cadeado_y = posicao[1] + (sprite_atual.get_height() - icone_cadeado.get_height()) // 2
                    screen.blit(icone_cadeado, (cadeado_x, cadeado_y))
            
            # Informações do carro na lateral direita - retângulo otimizado
            info_x = LARGURA - 300  # Largura reduzida
            info_y = 180  # Posição ajustada
            
            # Fundo semi-transparente para as informações - tamanho otimizado
            info_largura = 280
            info_altura = 380  # Altura reduzida
            info_bg = pygame.Surface((info_largura, info_altura), pygame.SRCALPHA)
            info_bg.fill((0, 0, 0, 150))
            screen.blit(info_bg, (info_x, info_y))
            
            # Nome do carro (acima das especificações) - estilo pixel art
            nome_carro_info = render_text(carro_atual['nome'], 24, (100, 220, 255), bold=True, pixel_style=True)
            nome_x_info = info_x + (info_largura - nome_carro_info.get_width()) // 2
            screen.blit(nome_carro_info, (nome_x_info, info_y + 15))
            
            # Título das informações - mais espaçado
            info_titulo = render_text(t("menu.oficina.especificacoes"), 18, (255, 255, 255), bold=True, pixel_style=True)
            screen.blit(info_titulo, (info_x + 15, info_y + 55))
            
            # Tipo de tração - espaçamento melhorado
            # Normalizar tipo de tração: converter português para inglês
            tipo_tracao_str = carro_atual['tipo_tracao'].lower() if isinstance(carro_atual['tipo_tracao'], str) else str(carro_atual['tipo_tracao']).lower()
            mapeamento_tracao = {
                "traseira": "rear",
                "frontal": "front",
                "integral": "awd",
                "rear": "rear",
                "front": "front",
                "awd": "awd"
            }
            tipo_tracao_normalizado = mapeamento_tracao.get(tipo_tracao_str, "rear")
            tracao_tipo = t(f"tipos_tracao.{tipo_tracao_normalizado}")
            tracao_texto = t("menu.oficina.tracao").format(tracao_tipo)
            tracao_color = (120, 240, 180) if carro_atual['tipo_tracao'] == 'awd' else (150, 220, 255)
            tracao_render = render_text(tracao_texto, 16, tracao_color, bold=True, pixel_style=True)
            screen.blit(tracao_render, (info_x + 15, info_y + 90))
            
            # Velocidade máxima (simulada baseada no tipo de tração) - azul claro harmonizado
            vel_max = {"front": 180, "rear": 200, "awd": 220}.get(carro_atual['tipo_tracao'], 190)
            vel_texto = t("menu.oficina.velocidade").format(vel_max)
            vel_render = render_text(vel_texto, 16, (120, 200, 255), bold=True, pixel_style=True)
            screen.blit(vel_render, (info_x + 15, info_y + 120))
            
            # Dirigibilidade (simulada) - azul ciano suave
            dir_valor = {"front": 85, "rear": 70, "awd": 95}.get(carro_atual['tipo_tracao'], 80)
            dir_texto = t("menu.oficina.dirigibilidade").format(dir_valor)
            dir_render = render_text(dir_texto, 16, (140, 210, 255), bold=True, pixel_style=True)
            screen.blit(dir_render, (info_x + 15, info_y + 150))
            
            # Frenagem (simulada) - azul ciano médio
            fren_valor = {"front": 90, "rear": 75, "awd": 95}.get(carro_atual['tipo_tracao'], 85)
            fren_texto = t("menu.oficina.frenagem").format(fren_valor)
            fren_render = render_text(fren_texto, 16, (130, 200, 255), bold=True, pixel_style=True)
            screen.blit(fren_render, (info_x + 15, info_y + 180))
            
            # Aceleração (simulada) - azul ciano claro
            acel_valor = {"front": 80, "rear": 90, "awd": 95}.get(carro_atual['tipo_tracao'], 85)
            acel_texto = t("menu.oficina.aceleracao").format(acel_valor)
            acel_render = render_text(acel_texto, 16, (160, 220, 255), bold=True, pixel_style=True)
            screen.blit(acel_render, (info_x + 15, info_y + 210))
            
            # Estabilidade (simulada) - azul ciano suave
            est_valor = {"front": 85, "rear": 70, "awd": 95}.get(carro_atual['tipo_tracao'], 80)
            est_texto = t("menu.oficina.estabilidade").format(est_valor)
            est_render = render_text(est_texto, 16, (150, 230, 255), bold=True, pixel_style=True)
            screen.blit(est_render, (info_x + 15, info_y + 240))
            
            # Status de desbloqueio e preço (harmonizado) - mais espaçado
            esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
            preco = carro_atual.get('preco', 0)
            
            if esta_desbloqueado:
                status_texto = t("menu.oficina.desbloqueado")
                status_color = (120, 240, 180)  # Verde-água harmonizado
            else:
                status_texto = t("menu.oficina.bloqueado_preco").format(preco)
                status_color = (255, 150, 120)  # Laranja suave harmonizado
            
            status_render = render_text(status_texto, 20, status_color, bold=True, pixel_style=True)
            screen.blit(status_render, (info_x + 15, info_y + 280))
            
            # Borda da caixa de informações (azul ciano harmonizado)
            pygame.draw.rect(screen, (100, 220, 255), (info_x, info_y, info_largura, info_altura), 2)
            
            # Botões abaixo do retângulo de especificações (usar variáveis já calculadas)
            if esta_desbloqueado:
                # Botão USAR (verde)
                if botao_usar_rect_p1:
                    pygame.draw.rect(screen, (50, 150, 100), botao_usar_rect_p1)
                    pygame.draw.rect(screen, (120, 240, 180), botao_usar_rect_p1, 2)
                    texto_usar = render_text(t("menu.oficina.usar"), 20, (255, 255, 255), bold=True, pixel_style=True)
                    texto_usar_x = botao_usar_rect_p1.x + (botao_usar_rect_p1.width - texto_usar.get_width()) // 2
                    texto_usar_y = botao_usar_rect_p1.y + (botao_usar_rect_p1.height - texto_usar.get_height()) // 2
                    screen.blit(texto_usar, (texto_usar_x, texto_usar_y))
            else:
                # Botão COMPRAR (amarelo/dourado se tiver dinheiro, vermelho se não)
                if botao_comprar_rect_p1:
                    if gerenciador_progresso.tem_dinheiro(preco):
                        pygame.draw.rect(screen, (150, 120, 50), botao_comprar_rect_p1)
                        pygame.draw.rect(screen, (255, 220, 100), botao_comprar_rect_p1, 2)
                        texto_comprar = render_text(t("menu.oficina.comprar"), 18, (255, 255, 255), bold=True, pixel_style=True)
                    else:
                        pygame.draw.rect(screen, (100, 50, 50), botao_comprar_rect_p1)
                        pygame.draw.rect(screen, (255, 150, 120), botao_comprar_rect_p1, 2)
                        texto_comprar = render_text("COMPRAR", 18, (200, 200, 200), bold=True, pixel_style=True)
                    
                    texto_comprar_x = botao_comprar_rect_p1.x + (botao_comprar_rect_p1.width - texto_comprar.get_width()) // 2
                    texto_comprar_y = botao_comprar_rect_p1.y + (botao_comprar_rect_p1.height - texto_comprar.get_height()) // 2
                    screen.blit(texto_comprar, (texto_comprar_x, texto_comprar_y))
            
        elif fase_selecao == 2:
            # FASE 2: Player 2 selecionando (azul claro harmonizado) - mais espaçado
            subtitulo = render_text(t("menu.oficina.jogador_2"), 32, (150, 220, 255), bold=True, pixel_style=True)
            subtitulo_x = (LARGURA - subtitulo.get_width()) // 2
            screen.blit(subtitulo, (subtitulo_x, 90))
            
            # Mostrar carro do P1 já selecionado (pequeno, no canto)
            carro_p1_selecionado = CARROS_DISPONIVEIS[carro_p1]
            sprite_p1 = pygame.transform.scale(sprites_carros[carro_p1_selecionado['prefixo_cor']], (90, 45))
            from core.i18n import t
            screen.blit(render_text(t("jogo.p1"), 20, (255, 255, 255), bold=True, pixel_style=True), (50, 100))
            screen.blit(sprite_p1, (50, 120))
            screen.blit(render_text(carro_p1_selecionado['nome'], 16, (255, 255, 255), bold=True, pixel_style=True), (50, 175))
            
            # Instruções - mais espaçado
            carro_atual = CARROS_DISPONIVEIS[carro_p2]
            esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
            if esta_desbloqueado:
                instrucoes = render_text("← → navegar | ENTER confirmar | ESC voltar", 20, (255, 255, 255), bold=True, pixel_style=True)
            else:
                instrucoes = render_text("← → navegar | B comprar | ESC voltar", 20, (255, 255, 255), bold=True, pixel_style=True)
            instrucoes_x = (LARGURA - instrucoes.get_width()) // 2
            screen.blit(instrucoes, (instrucoes_x, 130))
            
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
                
                # Usar float para suavidade e depois converter para int apenas na renderização
                pos_x_anterior = pos_anterior[0] + carro_atual_pos * LARGURA
                pos_x_atual = pos_atual[0] + carro_proximo_pos * LARGURA
                
                # Desenhar carro anterior saindo (converter para int apenas na renderização)
                screen.blit(sprite_anterior, (int(pos_x_anterior), pos_anterior[1]))
                # Desenhar novo carro entrando
                screen.blit(sprite_atual, (int(pos_x_atual), pos_atual[1]))
                
                # Desenhar cadeado se o carro atual não estiver desbloqueado (P2)
                esta_desbloqueado_atual = gerenciador_progresso.esta_desbloqueado(carro_atual_obj['prefixo_cor'])
                if not esta_desbloqueado_atual and icone_cadeado:
                    cadeado_x = int(pos_x_atual) + (sprite_atual.get_width() - icone_cadeado.get_width()) // 2
                    cadeado_y = pos_atual[1] + (sprite_atual.get_height() - icone_cadeado.get_height()) // 2
                    screen.blit(icone_cadeado, (cadeado_x, cadeado_y))
            else:
                # Sem transição: desenhar carro atual normalmente
                carro_atual = CARROS_DISPONIVEIS[carro_p2]
                sprite_atual = sprites_carros[carro_atual['prefixo_cor']]
                posicao = carro_atual.get('posicao_oficina', (LARGURA//2 - 300, 380))
                screen.blit(sprite_atual, posicao)
                
                # Desenhar cadeado se o carro não estiver desbloqueado (P2)
                esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                if not esta_desbloqueado and icone_cadeado:
                    cadeado_x = posicao[0] + (sprite_atual.get_width() - icone_cadeado.get_width()) // 2
                    cadeado_y = posicao[1] + (sprite_atual.get_height() - icone_cadeado.get_height()) // 2
                    screen.blit(icone_cadeado, (cadeado_x, cadeado_y))
            
            # Informações do carro na lateral direita - retângulo otimizado (P2)
            carro_atual = CARROS_DISPONIVEIS[carro_p2]  # Garantir que está definido
            info_x = LARGURA - 300  # Largura reduzida
            info_y = 180  # Posição ajustada
            
            # Fundo semi-transparente para as informações - tamanho otimizado
            info_largura = 280
            info_altura = 380  # Altura reduzida
            info_bg = pygame.Surface((info_largura, info_altura), pygame.SRCALPHA)
            info_bg.fill((0, 0, 0, 150))
            screen.blit(info_bg, (info_x, info_y))
            
            # Nome do carro (acima das especificações) - estilo pixel art (azul ciano harmonizado)
            nome_carro_info = render_text(carro_atual['nome'], 24, (100, 220, 255), bold=True, pixel_style=True)
            nome_x_info = info_x + (info_largura - nome_carro_info.get_width()) // 2
            screen.blit(nome_carro_info, (nome_x_info, info_y + 15))
            
            # Título das informações - mais espaçado
            from core.i18n import t
            info_titulo = render_text(t("menu.oficina.especificacoes"), 18, (255, 255, 255), bold=True, pixel_style=True)
            screen.blit(info_titulo, (info_x + 15, info_y + 55))
            
            # Tipo de tração (harmonizado - azul ciano com variações sutis) - espaçamento melhorado
            from core.i18n import t
            # Normalizar tipo de tração: converter português para inglês
            tipo_tracao_str = carro_atual['tipo_tracao'].lower() if isinstance(carro_atual['tipo_tracao'], str) else str(carro_atual['tipo_tracao']).lower()
            mapeamento_tracao = {
                "traseira": "rear",
                "frontal": "front",
                "integral": "awd",
                "rear": "rear",
                "front": "front",
                "awd": "awd"
            }
            tipo_tracao_normalizado = mapeamento_tracao.get(tipo_tracao_str, "rear")
            tipo_tracao_traduzido = t(f"tipos_tracao.{tipo_tracao_normalizado}")
            tracao_texto = t("menu.oficina.tracao").format(tipo_tracao_traduzido)
            tracao_color = (120, 240, 180) if carro_atual['tipo_tracao'] == 'awd' else (150, 220, 255)
            tracao_render = render_text(tracao_texto, 16, tracao_color, bold=True, pixel_style=True)
            screen.blit(tracao_render, (info_x + 15, info_y + 90))
            
            # Velocidade máxima (simulada baseada no tipo de tração) - azul claro harmonizado
            vel_max = {"front": 180, "rear": 200, "awd": 220}.get(carro_atual['tipo_tracao'], 190)
            vel_texto = t("menu.oficina.velocidade").format(vel_max)
            vel_render = render_text(vel_texto, 16, (120, 200, 255), bold=True, pixel_style=True)
            screen.blit(vel_render, (info_x + 15, info_y + 120))
            
            # Dirigibilidade (simulada) - azul ciano suave
            dir_valor = {"front": 85, "rear": 70, "awd": 95}.get(carro_atual['tipo_tracao'], 80)
            dir_texto = t("menu.oficina.dirigibilidade").format(dir_valor)
            dir_render = render_text(dir_texto, 16, (140, 210, 255), bold=True, pixel_style=True)
            screen.blit(dir_render, (info_x + 15, info_y + 150))
            
            # Frenagem (simulada) - azul ciano médio
            fren_valor = {"front": 90, "rear": 75, "awd": 95}.get(carro_atual['tipo_tracao'], 85)
            fren_texto = t("menu.oficina.frenagem").format(fren_valor)
            fren_render = render_text(fren_texto, 16, (130, 200, 255), bold=True, pixel_style=True)
            screen.blit(fren_render, (info_x + 15, info_y + 180))
            
            # Aceleração (simulada) - azul ciano claro
            acel_valor = {"front": 80, "rear": 90, "awd": 95}.get(carro_atual['tipo_tracao'], 85)
            acel_texto = t("menu.oficina.aceleracao").format(acel_valor)
            acel_render = render_text(acel_texto, 16, (160, 220, 255), bold=True, pixel_style=True)
            screen.blit(acel_render, (info_x + 15, info_y + 210))
            
            # Estabilidade (simulada) - azul ciano suave
            est_valor = {"front": 85, "rear": 70, "awd": 95}.get(carro_atual['tipo_tracao'], 80)
            est_texto = t("menu.oficina.estabilidade").format(est_valor)
            est_render = render_text(est_texto, 16, (150, 230, 255), bold=True, pixel_style=True)
            screen.blit(est_render, (info_x + 15, info_y + 240))
            
            # Status de desbloqueio e preço (P2) (harmonizado) - mais espaçado
            esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
            preco = carro_atual.get('preco', 0)
            
            if esta_desbloqueado:
                status_texto = t("menu.oficina.desbloqueado")
                status_color = (120, 240, 180)  # Verde-água harmonizado
            else:
                status_texto = t("menu.oficina.bloqueado_preco").format(preco)
                status_color = (255, 150, 120)  # Laranja suave harmonizado
            
            status_render = render_text(status_texto, 20, status_color, bold=True, pixel_style=True)
            screen.blit(status_render, (info_x + 15, info_y + 280))
            
            # Borda da caixa de informações (azul ciano harmonizado)
            pygame.draw.rect(screen, (100, 220, 255), (info_x, info_y, info_largura, info_altura), 2)
            
            # Botões abaixo do retângulo de especificações (P2) (usar variáveis já calculadas)
            if esta_desbloqueado:
                # Botão USAR (verde)
                if botao_usar_rect_p2:
                    pygame.draw.rect(screen, (50, 150, 100), botao_usar_rect_p2)
                    pygame.draw.rect(screen, (120, 240, 180), botao_usar_rect_p2, 2)
                    texto_usar = render_text(t("menu.oficina.usar"), 20, (255, 255, 255), bold=True, pixel_style=True)
                    texto_usar_x = botao_usar_rect_p2.x + (botao_usar_rect_p2.width - texto_usar.get_width()) // 2
                    texto_usar_y = botao_usar_rect_p2.y + (botao_usar_rect_p2.height - texto_usar.get_height()) // 2
                    screen.blit(texto_usar, (texto_usar_x, texto_usar_y))
            else:
                # Botão COMPRAR (amarelo/dourado se tiver dinheiro, vermelho se não)
                if botao_comprar_rect_p2:
                    if gerenciador_progresso.tem_dinheiro(preco):
                        pygame.draw.rect(screen, (150, 120, 50), botao_comprar_rect_p2)
                        pygame.draw.rect(screen, (255, 220, 100), botao_comprar_rect_p2, 2)
                        texto_comprar = render_text(t("menu.oficina.comprar"), 18, (255, 255, 255), bold=True, pixel_style=True)
                    else:
                        pygame.draw.rect(screen, (100, 50, 50), botao_comprar_rect_p2)
                        pygame.draw.rect(screen, (255, 150, 120), botao_comprar_rect_p2, 2)
                        texto_comprar = render_text("COMPRAR", 18, (200, 200, 200), bold=True, pixel_style=True)
                    
                    texto_comprar_x = botao_comprar_rect_p2.x + (botao_comprar_rect_p2.width - texto_comprar.get_width()) // 2
                    texto_comprar_y = botao_comprar_rect_p2.y + (botao_comprar_rect_p2.height - texto_comprar.get_height()) // 2
                    screen.blit(texto_comprar, (texto_comprar_x, texto_comprar_y))
        
        # Atualizar e desenhar popup de música
        popup_musica.atualizar(dt)
        popup_musica.desenhar(screen)
        
        pygame.display.flip()

def submenu_audio(screen):
    """Submenu de configurações de áudio"""
    from config import CONFIGURACOES, salvar_configuracoes
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)

    from core.i18n import t
    opcoes_audio = [
        (t("audio.musica_habilitada"), "musica_habilitada"),
        (t("audio.musica_no_menu"), "musica_no_menu"),
        (t("audio.musica_no_jogo"), "musica_no_jogo"),
        (t("audio.musica_aleatoria"), "musica_aleatoria"),
        (t("audio.volume_musica"), "volume_musica")
    ]
    opcao_voltar = (t("audio.voltar"), "voltar")

    opcao_atual = 0
    clock = pygame.time.Clock()

    caixa_largura = 500
    caixa_altura = 400
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2

    hover_animation = [0.0] * len(opcoes_audio)
    hover_speed = 8.0  # Velocidade aumentada

    while True:
        dt = clock.tick(FPS) / 1000.0  # Converter para segundos

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
                        if chave in ["musica_habilitada", "musica_no_menu", "musica_no_jogo", "musica_aleatoria"]:
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
                    elif chave in ["musica_habilitada", "musica_no_menu", "musica_no_jogo", "musica_aleatoria"]:
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
        from core.i18n import t
        titulo = render_text(t("audio.titulo"), 36, (255, 255, 255), bold=True, pixel_style=True)
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
                from core.i18n import t
                valor = t("jogo.sim") if CONFIGURACOES["audio"][chave] else t("jogo.nao")
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

    from core.i18n import t
    opcoes_controles = [
        (t("controles.jogador_1_acelerar"), "W"),
        (t("controles.jogador_1_frear"), "S"),
        (t("controles.jogador_1_esquerda"), "A"),
        (t("controles.jogador_1_direita"), "D"),
        (t("controles.jogador_1_turbo"), "SHIFT ESQUERDO"),
        (t("controles.jogador_1_freio_mao"), "SPACE"),
        (t("controles.jogador_2_acelerar"), "↑"),
        (t("controles.jogador_2_frear"), "↓"),
        (t("controles.jogador_2_esquerda"), "←"),
        (t("controles.jogador_2_direita"), "→"),
        (t("controles.jogador_2_turbo"), "CTRL DIREITO"),
        (t("controles.jogador_2_freio_mao"), "CTRL")
    ]
    opcao_voltar = (t("controles.voltar"), "voltar")

    opcao_atual = 0
    clock = pygame.time.Clock()

    caixa_largura = 600
    caixa_altura = 500
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2

    hover_animation = [0.0] * len(opcoes_controles)
    hover_speed = 8.0  # Velocidade aumentada

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
        from core.i18n import t
        titulo = render_text(t("menu.opcoes.controles"), 36, (255, 255, 255), bold=True, pixel_style=True)
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

    from core.i18n import t
    opcoes_video = [
        (t("video.resolucao"), "resolucao"),
        (t("video.tela_cheia"), "fullscreen"),
        (t("video.sem_bordas"), "tela_cheia_sem_bordas"),
        (t("video.qualidade_alta"), "qualidade_alta"),
        (t("video.vsync"), "vsync"),
        (t("video.fps_maximo"), "fps_max"),
        (t("video.mostrar_fps"), "mostrar_fps")
    ]
    opcao_voltar = (t("video.voltar"), "voltar")

    opcao_atual = 0
    clock = pygame.time.Clock()

    caixa_largura = 500
    caixa_altura = 400
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2

    hover_animation = [0.0] * len(opcoes_video)
    hover_speed = 8.0  # Velocidade aumentada

    # scroll
    scroll_offset = 0
    altura_item = 50
    altura_total_opcoes = len(opcoes_video) * altura_item
    altura_area_visivel = caixa_altura - 200
    max_scroll = max(0, altura_total_opcoes - altura_area_visivel)
    
    while True:
        dt = clock.tick(FPS) / 1000.0  # Converter para segundos

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
                        if chave in ["fullscreen", "tela_cheia_sem_bordas", "qualidade_alta", "vsync", "mostrar_fps"]:
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
                    elif chave in ["fullscreen", "tela_cheia_sem_bordas", "qualidade_alta", "vsync", "mostrar_fps"]:
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
        from core.i18n import t
        titulo = render_text(t("video.titulo"), 36, (255, 255, 255), bold=True, pixel_style=True)
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
                from core.i18n import t
                valor = t("jogo.sim") if CONFIGURACOES["video"][chave] else t("jogo.nao")
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
    from core.i18n import t
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)

    def recarregar_opcoes_idioma():
        """Recarrega as opções de idioma com as traduções atualizadas"""
        return [
            (t("menu.idioma.portugues"), "pt"),
            (t("menu.idioma.english"), "en"),
            (t("menu.idioma.espanol"), "es"),
            (t("menu.idioma.frances"), "fr")
        ]
    
    opcoes_idioma = recarregar_opcoes_idioma()
    opcao_voltar = (t("menu.idioma.voltar"), "voltar")

    opcao_atual = 0
    clock = pygame.time.Clock()

    caixa_largura = 400
    caixa_altura = 350
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2

    hover_animation = [0.0] * len(opcoes_idioma)
    hover_speed = 8.0  # Velocidade aumentada
    
    while True:
        dt = clock.tick(FPS) / 1000.0  # Converter para segundos
        
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
                        # Trocar idioma ao clicar
                        if opcoes_idioma[idx][1] != "voltar":
                            idioma_selecionado = opcoes_idioma[idx][1]
                            from core.i18n import definir_idioma
                            from config import CONFIGURACOES, salvar_configuracoes
                            if definir_idioma(idioma_selecionado):
                                CONFIGURACOES["idioma"]["idioma_atual"] = idioma_selecionado
                                salvar_configuracoes()
                                print(f"Idioma alterado para: {idioma_selecionado}")
                                # Forçar atualização imediata da interface
                                from core.i18n import atualizar_titulo_janela
                                atualizar_titulo_janela("menu")
                                # Recarregar opções de idioma para atualizar os textos
                                opcoes_idioma = recarregar_opcoes_idioma()
                                opcao_voltar = (t("menu.idioma.voltar"), "voltar")
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
                    # Trocar idioma
                    idioma_selecionado = opcoes_idioma[opcao_atual][1]
                    from core.i18n import definir_idioma
                    from config import CONFIGURACOES, salvar_configuracoes
                    if definir_idioma(idioma_selecionado):
                        CONFIGURACOES["idioma"]["idioma_atual"] = idioma_selecionado
                        salvar_configuracoes()
                        print(f"Idioma alterado para: {idioma_selecionado}")
                        # Forçar atualização imediata da interface
                        from core.i18n import atualizar_titulo_janela
                        atualizar_titulo_janela("menu")
                        # Recarregar opções de idioma para atualizar os textos
                        opcoes_idioma = recarregar_opcoes_idioma()
                        opcao_voltar = (t("menu.idioma.voltar"), "voltar")
        
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
        from core.i18n import t
        titulo = render_text(t("menu.opcoes.idioma"), 36, (255, 255, 255), bold=True, pixel_style=True)
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

    from core.i18n import t
    
    def recarregar_opcoes():
        """Recarrega as opções com as traduções atualizadas"""
        return [
            (t("menu.opcoes.volume"), "audio"),
            (t("menu.opcoes.controles"), "controles"),
            (t("menu.opcoes.graficos"), "video"),
            (t("menu.opcoes.idioma"), "idioma"),
            (t("menu.opcoes.voltar"), "voltar")
        ]
    
    opcoes_principais = recarregar_opcoes()

    opcao_atual = 0
    clock = pygame.time.Clock()

    # caixa
    caixa_largura = 400
    caixa_altura = 500
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2

    # animação hover (mantém estado entre frames)
    hover_animation = [0.0] * 5  # Tamanho fixo (sempre 5 opções)
    hover_speed = 8.0  # Velocidade aumentada

    while True:
        dt = clock.tick(FPS) / 1000.0  # Converter para segundos

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
                            # Recarregar opções após voltar do submenu de idioma
                            opcoes_principais = recarregar_opcoes()
                            continue

        # Recarregar opções a cada frame para garantir traduções atualizadas
        opcoes_principais = recarregar_opcoes()
        # Garantir que hover_animation tem o tamanho correto
        if len(hover_animation) != len(opcoes_principais):
            hover_animation = [0.0] * len(opcoes_principais)
        
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
        from core.i18n import t
        titulo = render_text(t("menu.opcoes.titulo"), 48, (255, 255, 255), bold=True, pixel_style=True)
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
    voltas_atual = 1  # Número de voltas selecionado
    dificuldade_ia_atual = "medio"  # Dificuldade da IA
    
    # Opções de modo de jogo
    from core.i18n import t
    opcoes_modo = [
        (t("modo_jogo.1_jogador"), ModoJogo.UM_JOGADOR),
        (t("modo_jogo.2_jogadores"), ModoJogo.DOIS_JOGADORES)
    ]
    
    # Opções de tipo de jogo
    opcoes_tipo = [
        (t("modo_jogo.corrida"), TipoJogo.CORRIDA),
        (t("modo_jogo.drift"), TipoJogo.DRIFT)
    ]
    
    # Opções de voltas (apenas para corrida) - máximo 3 voltas
    opcoes_voltas = [
        (t("voltas.1_volta"), 1),
        (t("voltas.2_voltas"), 2),
        (t("voltas.3_voltas"), 3)
    ]
    
    # Opções de dificuldade (IA para corrida, tempo para drift)
    opcoes_dificuldade = [
        (t("dificuldade.facil"), "facil"),
        (t("dificuldade.medio"), "medio"),
        (t("dificuldade.dificil"), "dificil")
    ]
    
    opcao_modo_atual = 0
    opcao_tipo_atual = 0
    opcao_voltas_atual = 0
    opcao_dificuldade_atual = 1  # Começar no MÉDIO
    clock = pygame.time.Clock()
    
    # Caixa principal (ajustada para layout horizontal das voltas e dificuldade)
    caixa_largura = 600
    caixa_altura = 580  # Aumentado de 500 para 580 para acomodar dificuldade
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2
    
    # Animações de hover
    hover_animation_modo = [0.0] * len(opcoes_modo)
    hover_animation_tipo = [0.0] * len(opcoes_tipo)
    hover_animation_voltas = [0.0] * len(opcoes_voltas)
    hover_animation_dificuldade = [0.0] * len(opcoes_dificuldade)
    hover_speed = 8.0  # Velocidade aumentada
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        
        # Atualizar música
        gerenciador_musica.verificar_fim_musica()
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
                    gerenciador_musica.musica_anterior()
                    if gerenciador_musica.musica_tocando:
                        popup_musica.mostrar(gerenciador_musica.obter_nome_musica_atual())
                elif clique_popup == "proximo":
                    gerenciador_musica.proxima_musica()
                    if gerenciador_musica.musica_tocando:
                        popup_musica.mostrar(gerenciador_musica.obter_nome_musica_atual())
                else:
                    # Verificar clique nas opções
                    mouse_x, mouse_y = ev.pos
                    
                    # Verificar clique em modo de jogo
                    for i, (nome, modo) in enumerate(opcoes_modo):
                        y = caixa_y + 120 + i * 50
                        rect = pygame.Rect(caixa_x + 50, y - 5, 200, 40)
                        if rect.collidepoint(mouse_x, mouse_y):
                            opcao_modo_atual = i
                            modo_jogo_atual = modo
                    
                    # Verificar clique em tipo de jogo
                    for i, (nome, tipo) in enumerate(opcoes_tipo):
                        y = caixa_y + 260 + i * 50
                        rect = pygame.Rect(caixa_x + 50, y - 5, 200, 40)
                        if rect.collidepoint(mouse_x, mouse_y):
                            opcao_tipo_atual = i
                            tipo_jogo_atual = tipo
                    
                    # Verificar clique em voltas (para corrida e drift) - layout horizontal
                    if tipo_jogo_atual in (TipoJogo.CORRIDA, TipoJogo.DRIFT):
                        for i, (nome, voltas) in enumerate(opcoes_voltas):
                            x = caixa_x + 50 + i * 180  # Espaçamento horizontal aumentado
                            y = caixa_y + 380
                            rect = pygame.Rect(x, y - 5, 140, 40)
                            if rect.collidepoint(mouse_x, mouse_y):
                                opcao_voltas_atual = i
                                voltas_atual = voltas
                    
                    # Verificar clique em dificuldade (1 e 2 jogadores)
                    if modo_jogo_atual == ModoJogo.UM_JOGADOR or modo_jogo_atual == ModoJogo.DOIS_JOGADORES:
                        for i, (nome, dificuldade) in enumerate(opcoes_dificuldade):
                            x = caixa_x + 50 + i * 180  # Espaçamento horizontal
                            y = caixa_y + 480
                            rect = pygame.Rect(x, y - 5, 140, 40)
                            if rect.collidepoint(mouse_x, mouse_y):
                                opcao_dificuldade_atual = i
                                dificuldade_ia_atual = dificuldade
                    
                    # Verificar clique no botão iniciar jogo (mesma hitbox aumentada)
                    iniciar_rect = pygame.Rect(caixa_x + 50, caixa_y + caixa_altura - 60, 200, 50)
                    if iniciar_rect.collidepoint(mouse_x, mouse_y):
                        # Abrir seleção de fase antes de iniciar o jogo
                        fase_selecionada = selecionar_fase_loop(screen)
                        if fase_selecionada is not None:
                            return (modo_jogo_atual, tipo_jogo_atual, voltas_atual, dificuldade_ia_atual, fase_selecionada)
                        # Se cancelou a seleção de fase, continuar no menu
                        continue
                    
                    # Verificar clique no botão voltar
                    voltar_rect = pygame.Rect(caixa_x + 270, caixa_y + caixa_altura - 40, 200, 40)
                    if voltar_rect.collidepoint(mouse_x, mouse_y):
                        return None
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return None
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    if opcao_modo_atual > 0:
                        opcao_modo_atual -= 1
                        modo_jogo_atual = opcoes_modo[opcao_modo_atual][1]
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    if opcao_modo_atual < len(opcoes_modo) - 1:
                        opcao_modo_atual += 1
                        modo_jogo_atual = opcoes_modo[opcao_modo_atual][1]
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    # Se estiver em voltas ou dificuldade, navegar neles primeiro
                    # Verificar se está focado em voltas (se voltas estão visíveis)
                    if tipo_jogo_atual in (TipoJogo.CORRIDA, TipoJogo.DRIFT):
                        if opcao_voltas_atual > 0:
                            opcao_voltas_atual -= 1
                            voltas_atual = opcoes_voltas[opcao_voltas_atual][1]
                        else:
                            # Se já está no primeiro, mudar tipo de jogo
                            if opcao_tipo_atual > 0:
                                opcao_tipo_atual -= 1
                                tipo_jogo_atual = opcoes_tipo[opcao_tipo_atual][1]
                    elif opcao_tipo_atual > 0:
                        opcao_tipo_atual -= 1
                        tipo_jogo_atual = opcoes_tipo[opcao_tipo_atual][1]
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    # Se estiver em voltas ou dificuldade, navegar neles primeiro
                    if tipo_jogo_atual in (TipoJogo.CORRIDA, TipoJogo.DRIFT):
                        if opcao_voltas_atual < len(opcoes_voltas) - 1:
                            opcao_voltas_atual += 1
                            voltas_atual = opcoes_voltas[opcao_voltas_atual][1]
                        else:
                            # Se já está no último, mudar tipo de jogo
                            if opcao_tipo_atual < len(opcoes_tipo) - 1:
                                opcao_tipo_atual += 1
                                tipo_jogo_atual = opcoes_tipo[opcao_tipo_atual][1]
                    elif opcao_tipo_atual < len(opcoes_tipo) - 1:
                        opcao_tipo_atual += 1
                        tipo_jogo_atual = opcoes_tipo[opcao_tipo_atual][1]
                elif ev.key == pygame.K_RETURN:
                    # Abrir seleção de fase antes de iniciar o jogo
                    fase_selecionada = selecionar_fase_loop(screen)
                    if fase_selecionada is not None:
                        return (modo_jogo_atual, tipo_jogo_atual, voltas_atual, dificuldade_ia_atual, fase_selecionada)
                    # Se cancelou a seleção de fase, continuar no menu
                    continue
                elif ev.key == pygame.K_m:
                    # Próxima música
                    gerenciador_musica.proxima_musica()
                    if gerenciador_musica.musica_tocando:
                        popup_musica.mostrar(gerenciador_musica.obter_nome_musica_atual())
                elif ev.key == pygame.K_n:
                    # Música anterior
                    gerenciador_musica.musica_anterior()
                    if gerenciador_musica.musica_tocando:
                        popup_musica.mostrar(gerenciador_musica.obter_nome_musica_atual())
        
        # Atualizar animações de hover
        for i in range(len(opcoes_modo)):
            y = caixa_y + 120 + i * 50
            rect = pygame.Rect(caixa_x + 50, y - 5, 200, 40)
            is_hovering = rect.collidepoint(mouse_x, mouse_y)
            
            if is_hovering:
                hover_animation_modo[i] = min(1.0, hover_animation_modo[i] + hover_speed * dt)
            else:
                hover_animation_modo[i] = max(0.0, hover_animation_modo[i] - hover_speed * dt)
        
        for i in range(len(opcoes_tipo)):
            y = caixa_y + 260 + i * 50
            rect = pygame.Rect(caixa_x + 50, y - 5, 200, 40)
            is_hovering = rect.collidepoint(mouse_x, mouse_y)
            
            if is_hovering:
                hover_animation_tipo[i] = min(1.0, hover_animation_tipo[i] + hover_speed * dt)
            else:
                hover_animation_tipo[i] = max(0.0, hover_animation_tipo[i] - hover_speed * dt)
        
        # Atualizar animações de hover para voltas (apenas se for corrida) - layout horizontal
        if tipo_jogo_atual == TipoJogo.CORRIDA:
            for i in range(len(opcoes_voltas)):
                x = caixa_x + 50 + i * 180  # Espaçamento horizontal aumentado
                y = caixa_y + 380
                rect = pygame.Rect(x, y - 5, 140, 40)
                is_hovering = rect.collidepoint(mouse_x, mouse_y)
                
                if is_hovering:
                    hover_animation_voltas[i] = min(1.0, hover_animation_voltas[i] + hover_speed * dt)
                else:
                    hover_animation_voltas[i] = max(0.0, hover_animation_voltas[i] - hover_speed * dt)
        
        # Atualizar animações de hover para dificuldade (1 jogador)
        if modo_jogo_atual == ModoJogo.UM_JOGADOR:
            for i in range(len(opcoes_dificuldade)):
                x = caixa_x + 50 + i * 180  # Espaçamento horizontal
                y = caixa_y + 480
                rect = pygame.Rect(x, y - 5, 140, 40)
                is_hovering = rect.collidepoint(mouse_x, mouse_y)
                
                if is_hovering:
                    hover_animation_dificuldade[i] = min(1.0, hover_animation_dificuldade[i] + hover_speed * dt)
                else:
                    hover_animation_dificuldade[i] = max(0.0, hover_animation_dificuldade[i] - hover_speed * dt)
        
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
        titulo = render_text(t("modo_jogo.titulo"), 36, (255, 255, 255), bold=True, pixel_style=True)
        titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, caixa_y + 20))
        
        # Modo de jogo
        from core.i18n import t
        modo_titulo = render_text(t("modo_jogo.numero_jogadores"), 24, (255, 255, 255), bold=True, pixel_style=True)
        screen.blit(modo_titulo, (caixa_x + 50, caixa_y + 80))
        
        for i, (nome, modo) in enumerate(opcoes_modo):
            y = caixa_y + 120 + i * 50
            
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
        from core.i18n import t
        tipo_titulo = render_text(t("jogo.tipo_jogo"), 24, (255, 255, 255), bold=True, pixel_style=True)
        screen.blit(tipo_titulo, (caixa_x + 50, caixa_y + 220))
        
        for i, (nome, tipo) in enumerate(opcoes_tipo):
            y = caixa_y + 260 + i * 50
            
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
        
        # Opções de voltas (para corrida e drift) - layout horizontal
        if tipo_jogo_atual in (TipoJogo.CORRIDA, TipoJogo.DRIFT):
            voltas_titulo = render_text(t("jogo.numero_voltas"), 24, (255, 255, 255), bold=True, pixel_style=True)
            screen.blit(voltas_titulo, (caixa_x + 50, caixa_y + 350))
            
            for i, (nome, voltas) in enumerate(opcoes_voltas):
                x = caixa_x + 50 + i * 180  # Espaçamento horizontal aumentado
                y = caixa_y + 390
                
                # Cores baseadas na seleção e hover
                if i == opcao_voltas_atual:
                    cor_fundo = (0, 200, 255, 50)
                    cor_texto = (0, 200, 255)
                else:
                    cor_fundo = (0, 0, 0, 0)
                    cor_texto = (255, 255, 255)
                
                # Aplicar hover
                hover_progress = hover_animation_voltas[i]
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
                    opcao_fundo = pygame.Surface((140, 40), pygame.SRCALPHA)
                    opcao_fundo.fill(cor_fundo)
                    screen.blit(opcao_fundo, (x, y - 5))
                
                # Desenhar texto centralizado
                texto = render_text(nome, 18, cor_texto, bold=True, pixel_style=True)
                texto_x = x + (140 - texto.get_width()) // 2  # Centralizar horizontalmente
                screen.blit(texto, (texto_x, y))
        
        # Opções de dificuldade (corrida = IA, drift = pontuação necessária)
        # Agora disponível para 1 e 2 jogadores (2 jogadores tem IA também)
        if modo_jogo_atual == ModoJogo.UM_JOGADOR or modo_jogo_atual == ModoJogo.DOIS_JOGADORES:
            # Título baseado no tipo de jogo
            if tipo_jogo_atual == TipoJogo.CORRIDA:
                titulo_dificuldade = t("dificuldade.dificuldade_ia")
            else:  # DRIFT
                titulo_dificuldade = t("dificuldade.dificuldade_pontuacao")
            dificuldade_titulo = render_text(titulo_dificuldade, 24, (255, 255, 255), bold=True, pixel_style=True)
            screen.blit(dificuldade_titulo, (caixa_x + 50, caixa_y + 440))
            
            for i, (nome, dificuldade) in enumerate(opcoes_dificuldade):
                x = caixa_x + 50 + i * 180  # Espaçamento horizontal
                y = caixa_y + 480
                
                # Cores baseadas na seleção e hover
                if i == opcao_dificuldade_atual:
                    cor_fundo = (0, 200, 255, 50)
                    cor_texto = (0, 200, 255)
                else:
                    cor_fundo = (0, 0, 0, 0)
                    cor_texto = (255, 255, 255)
                
                # Aplicar hover
                hover_progress = hover_animation_dificuldade[i]
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
                    opcao_fundo = pygame.Surface((140, 40), pygame.SRCALPHA)
                    opcao_fundo.fill(cor_fundo)
                    screen.blit(opcao_fundo, (x, y - 5))
                
                # Desenhar texto centralizado
                texto = render_text(nome, 18, cor_texto, bold=True, pixel_style=True)
                texto_x = x + (140 - texto.get_width()) // 2  # Centralizar horizontalmente
                screen.blit(texto, (texto_x, y))
        
        # Botão iniciar jogo (descido para não sobrepor dificuldade)
        # Aumentar hitbox para cima para melhorar detecção de clique
        iniciar_rect = pygame.Rect(caixa_x + 50, caixa_y + caixa_altura - 60, 200, 50)
        iniciar_hover = iniciar_rect.collidepoint(mouse_x, mouse_y)
        if iniciar_hover:
            pygame.draw.rect(screen, (0, 255, 0, 50), iniciar_rect)
        from core.i18n import t
        iniciar_texto = render_text(t("jogo.iniciar_jogo"), 24, (0, 255, 0) if iniciar_hover else (255, 255, 255), bold=True, pixel_style=True)
        screen.blit(iniciar_texto, (caixa_x + 60, caixa_y + caixa_altura - 53))
        
        # Botão voltar (descido para não sobrepor dificuldade)
        voltar_rect = pygame.Rect(caixa_x + 270, caixa_y + caixa_altura - 53, 200, 40)
        voltar_hover = voltar_rect.collidepoint(mouse_x, mouse_y)
        if voltar_hover:
            pygame.draw.rect(screen, (0, 200, 255, 50), voltar_rect)
        from core.i18n import t
        voltar_texto = render_text(t("menu.selecionar_mapa.voltar"), 24, (0, 200, 255) if voltar_hover else (255, 255, 255), bold=True, pixel_style=True)
        screen.blit(voltar_texto, (caixa_x + 280, caixa_y + caixa_altura - 53))
        
        
        # Desenhar popup de música
        popup_musica.desenhar(screen)
        
        pygame.display.flip()

def selecionar_fase_loop(screen):
    """Menu de seleção de fase com minimapas"""
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)
    
    # Carregar e redimensionar minimapas das 9 pistas (fazer apenas uma vez)
    from core.pista_tiles import PistaTiles
    minimapas = {}
    minimapas_redimensionados = {}  # Cache das versões redimensionadas
    minimapa_tamanho_display = 110  # Tamanho final para exibição (minimapa_tamanho - 10)
    
    # Carregar imagens de troféus uma vez (cache)
    from core.progresso import gerenciador_progresso
    from config import CAMINHO_TROFEU_OURO, CAMINHO_TROFEU_PRATA, CAMINHO_TROFEU_BRONZE, CAMINHO_TROFEU_VAZIO
    trofeus_cache = {}
    try:
        trofeu_ouro = pygame.image.load(CAMINHO_TROFEU_OURO).convert_alpha()
        trofeu_prata = pygame.image.load(CAMINHO_TROFEU_PRATA).convert_alpha()
        trofeu_bronze = pygame.image.load(CAMINHO_TROFEU_BRONZE).convert_alpha()
        trofeu_vazio = pygame.image.load(CAMINHO_TROFEU_VAZIO).convert_alpha()
        tamanho_trofeu = (25, 25)
        trofeus_cache["ouro"] = pygame.transform.scale(trofeu_ouro, tamanho_trofeu)
        trofeus_cache["prata"] = pygame.transform.scale(trofeu_prata, tamanho_trofeu)
        trofeus_cache["bronze"] = pygame.transform.scale(trofeu_bronze, tamanho_trofeu)
        trofeus_cache["vazio"] = pygame.transform.scale(trofeu_vazio, tamanho_trofeu)
    except Exception as e:
        print(f"Erro ao carregar troféus: {e}")
        trofeus_cache = {}
    
    print("Carregando minimapas...")
    pista_temp = PistaTiles()  # Criar apenas uma instância
    for i in range(1, 10):
        try:
            minimapa = pista_temp.carregar_minimapa(i)
            if minimapa:
                minimapas[i] = minimapa
                # Redimensionar mantendo proporção para evitar distorção
                largura_original = minimapa.get_width()
                altura_original = minimapa.get_height()
                
                # Calcular escala para manter proporção
                escala_x = minimapa_tamanho_display / largura_original
                escala_y = minimapa_tamanho_display / altura_original
                escala = min(escala_x, escala_y)  # Usar menor escala para manter proporção
                
                # Calcular novo tamanho mantendo proporção
                nova_largura = int(largura_original * escala)
                nova_altura = int(altura_original * escala)
                
                # Redimensionar mantendo proporção
                minimapa_redimensionado = pygame.transform.smoothscale(
                    minimapa, 
                    (nova_largura, nova_altura)
                )
                
                # Criar superfície do tamanho final e centralizar a imagem
                minimapa_final = pygame.Surface((minimapa_tamanho_display, minimapa_tamanho_display), pygame.SRCALPHA)
                offset_x = (minimapa_tamanho_display - nova_largura) // 2
                offset_y = (minimapa_tamanho_display - nova_altura) // 2
                minimapa_final.blit(minimapa_redimensionado, (offset_x, offset_y))
                
                minimapas_redimensionados[i] = minimapa_final
        except Exception as e:
            print(f"Erro ao carregar minimapa {i}: {e}")
    print(f"Minimapas carregados: {len(minimapas_redimensionados)}")
    
    fase_selecionada = 1
    clock = pygame.time.Clock()
    
    # Layout
    caixa_largura = 700
    caixa_altura = 550
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2
    
    # Grid de minimapas (3x3) - diminuído e centralizado
    minimapa_tamanho = 120
    espacamento = 15
    # Calcular posição do grid para centralizar
    largura_total_grid = 3 * minimapa_tamanho + 2 * espacamento
    altura_total_grid = 3 * minimapa_tamanho + 2 * espacamento
    grid_x = caixa_x + (caixa_largura - largura_total_grid) // 2
    grid_y = caixa_y + 80
    colunas = 3
    
    # Animações de hover
    hover_animation = [0.0] * 9
    hover_speed = 8.0
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        
        gerenciador_musica.verificar_fim_musica()
        popup_musica.atualizar(dt)
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        popup_musica.verificar_hover(mouse_x, mouse_y)
        
        # Atualizar animações de hover
        for i in range(9):
            fase_num = i + 1
            col = i % colunas
            linha = i // colunas
            x = grid_x + col * (minimapa_tamanho + espacamento)
            y = grid_y + linha * (minimapa_tamanho + espacamento)
            rect = pygame.Rect(x, y, minimapa_tamanho, minimapa_tamanho)
            
            is_hovering = rect.collidepoint(mouse_x, mouse_y)
            if is_hovering:
                hover_animation[i] = min(1.0, hover_animation[i] + hover_speed * dt)
            else:
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt)
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return None
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # Verificar clique em minimapa
                for i in range(9):
                    fase_num = i + 1
                    col = i % colunas
                    linha = i // colunas
                    x = grid_x + col * (minimapa_tamanho + espacamento)
                    y = grid_y + linha * (minimapa_tamanho + espacamento)
                    rect = pygame.Rect(x, y, minimapa_tamanho, minimapa_tamanho)
                    
                    if rect.collidepoint(ev.pos[0], ev.pos[1]):
                        fase_selecionada = fase_num
                        return fase_selecionada
                
                # Verificar clique no botão voltar
                voltar_largura_temp = 120
                voltar_altura_temp = 40
                voltar_x_temp = caixa_x + (caixa_largura - voltar_largura_temp) // 2
                voltar_y_temp = caixa_y + caixa_altura - 50
                voltar_rect = pygame.Rect(voltar_x_temp, voltar_y_temp, voltar_largura_temp, voltar_altura_temp)
                if voltar_rect.collidepoint(ev.pos[0], ev.pos[1]):
                    return None
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return None
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    fase_selecionada = max(1, fase_selecionada - 1)
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    fase_selecionada = min(9, fase_selecionada + 1)
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    fase_selecionada = max(1, fase_selecionada - 3)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    fase_selecionada = min(9, fase_selecionada + 3)
                elif ev.key == pygame.K_RETURN or ev.key == pygame.K_SPACE:
                    return fase_selecionada
                elif ev.key == pygame.K_m:
                    gerenciador_musica.proxima_musica()
                    if gerenciador_musica.musica_tocando:
                        popup_musica.mostrar(gerenciador_musica.obter_nome_musica_atual())
        
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
        from core.i18n import t
        titulo = render_text(t("jogo.selecionar_fase"), 36, (255, 255, 255), bold=True, pixel_style=True)
        titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, caixa_y + 20))
        
        # Desenhar grid de minimapas
        for i in range(9):
            fase_num = i + 1
            col = i % colunas
            linha = i // colunas
            x = grid_x + col * (minimapa_tamanho + espacamento)
            y = grid_y + linha * (minimapa_tamanho + espacamento)
            
            # Cores baseadas na seleção e hover
            is_selected = (fase_num == fase_selecionada)
            hover_progress = hover_animation[i]
            
            if is_selected:
                cor_borda = (0, 200, 255)
                espessura_borda = 4
            else:
                cor_borda = (128, 128, 128)
                espessura_borda = 2
            
            # Aplicar hover
            if hover_progress > 0:
                cor_borda_hover = (0, 255, 0)
                cor_borda = (
                    int(cor_borda[0] + (cor_borda_hover[0] - cor_borda[0]) * hover_progress),
                    int(cor_borda[1] + (cor_borda_hover[1] - cor_borda[1]) * hover_progress),
                    int(cor_borda[2] + (cor_borda_hover[2] - cor_borda[2]) * hover_progress)
                )
            
            # Desenhar fundo do minimapa
            pygame.draw.rect(screen, (0, 0, 0), (x, y, minimapa_tamanho, minimapa_tamanho))
            pygame.draw.rect(screen, cor_borda, (x, y, minimapa_tamanho, minimapa_tamanho), espessura_borda)
            
            # Desenhar minimapa se disponível (usar versão já redimensionada do cache)
            if fase_num in minimapas_redimensionados:
                screen.blit(minimapas_redimensionados[fase_num], (x + 5, y + 5))
            else:
                # Fallback: desenhar número da fase
                texto_fase = render_text(t("jogo.fase_numero").format(fase_num), 24, (255, 255, 255), bold=True, pixel_style=True)
                texto_x = x + (minimapa_tamanho - texto_fase.get_width()) // 2
                texto_y = y + (minimapa_tamanho - texto_fase.get_height()) // 2
                screen.blit(texto_fase, (texto_x, texto_y))
            
            # Desenhar número da fase abaixo do minimapa
            texto_num = render_text(t("jogo.fase_numero").format(fase_num), 14, (255, 255, 255), bold=True, pixel_style=True)
            texto_num_x = x + (minimapa_tamanho - texto_num.get_width()) // 2
            screen.blit(texto_num, (texto_num_x, y + minimapa_tamanho + 3))
            
            # Desenhar troféu no canto superior direito do minimapa (usar cache)
            try:
                trofeu_tipo = gerenciador_progresso.obter_trofeu(fase_num)
                if trofeu_tipo in trofeus_cache:
                    trofeu_img = trofeus_cache[trofeu_tipo]
                else:
                    trofeu_img = trofeus_cache.get("vazio")
                
                if trofeu_img:
                    trofeu_x = x + minimapa_tamanho - 30
                    trofeu_y = y + 5
                    screen.blit(trofeu_img, (trofeu_x, trofeu_y))
            except:
                pass
        
        # Botão voltar (centralizado na parte inferior)
        voltar_largura = 120
        voltar_altura = 40
        voltar_x = caixa_x + (caixa_largura - voltar_largura) // 2
        voltar_y = caixa_y + caixa_altura - 50
        voltar_rect = pygame.Rect(voltar_x, voltar_y, voltar_largura, voltar_altura)
        voltar_hover = voltar_rect.collidepoint(mouse_x, mouse_y)
        if voltar_hover:
            pygame.draw.rect(screen, (0, 200, 255, 50), voltar_rect)
        voltar_texto = render_text("VOLTAR", 20, (0, 200, 255) if voltar_hover else (255, 255, 255), bold=True, pixel_style=True)
        voltar_texto_x = voltar_x + (voltar_largura - voltar_texto.get_width()) // 2
        voltar_texto_y = voltar_y + (voltar_altura - voltar_texto.get_height()) // 2
        screen.blit(voltar_texto, (voltar_texto_x, voltar_texto_y))
        
        # Desenhar popup de música
        popup_musica.desenhar(screen)
        
        pygame.display.flip()

def recordes_loop(screen):
    """Tela de recordes mostrando melhores tempos por pista (corrida e drift)"""
    from core.progresso import gerenciador_progresso
    from config import CAMINHO_TROFEU_OURO, CAMINHO_TROFEU_PRATA, CAMINHO_TROFEU_BRONZE, CAMINHO_TROFEU_VAZIO
    
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)
    
    # Carregar imagens de troféus
    try:
        trofeu_ouro = pygame.image.load(CAMINHO_TROFEU_OURO).convert_alpha()
        trofeu_prata = pygame.image.load(CAMINHO_TROFEU_PRATA).convert_alpha()
        trofeu_bronze = pygame.image.load(CAMINHO_TROFEU_BRONZE).convert_alpha()
        trofeu_vazio = pygame.image.load(CAMINHO_TROFEU_VAZIO).convert_alpha()
        tamanho_trofeu = (40, 40)
        trofeu_ouro = pygame.transform.scale(trofeu_ouro, tamanho_trofeu)
        trofeu_prata = pygame.transform.scale(trofeu_prata, tamanho_trofeu)
        trofeu_bronze = pygame.transform.scale(trofeu_bronze, tamanho_trofeu)
        trofeu_vazio = pygame.transform.scale(trofeu_vazio, tamanho_trofeu)
    except:
        trofeu_ouro = trofeu_prata = trofeu_bronze = trofeu_vazio = None
    
    clock = pygame.time.Clock()
    
    # Layout - aumentar altura para duas seções
    caixa_largura = 900
    caixa_altura = 650
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2
    
    def formatar_tempo(tempo):
        """Formata tempo em segundos para MM:SS.CC"""
        if tempo is None:
            return "--:--.--"
        minutos = int(tempo // 60)
        segundos = int(tempo % 60)
        centesimos = int((tempo % 1) * 100)
        return f"{minutos:02d}:{segundos:02d}.{centesimos:02d}"
    
    def formatar_score(score):
        """Formata score para exibição"""
        if score is None:
            return "--"
        score_int = int(score)
        # Formatar com separador de milhares (ponto)
        if score_int >= 1000:
            return f"{score_int:,}".replace(",", ".")
        return str(score_int)
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        
        gerenciador_musica.verificar_fim_musica()
        popup_musica.atualizar(dt)
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        popup_musica.verificar_hover(mouse_x, mouse_y)
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
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
        from core.i18n import t
        titulo = render_text(t("jogo.recordes"), 36, (255, 255, 255), bold=True, pixel_style=True)
        titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, caixa_y + 20))
        
        # Fonte
        fonte_cabecalho = pygame.font.SysFont("consolas", 18, bold=True)
        fonte_item = pygame.font.SysFont("consolas", 16)
        fonte_secao = pygame.font.SysFont("consolas", 20, bold=True)
        
        # === SEÇÃO CORRIDA ===
        from core.i18n import t
        y_secao_corrida = caixa_y + 70
        titulo_corrida = fonte_secao.render(t("recordes.corrida"), True, (0, 200, 255))
        screen.blit(titulo_corrida, (caixa_x + 30, y_secao_corrida))
        
        y_inicial_corrida = y_secao_corrida + 35
        x_pista = caixa_x + 30
        x_trofeu = caixa_x + 150
        x_tempo = caixa_x + 220
        
        # Cabeçalhos corrida
        cabecalho_pista = fonte_cabecalho.render(t("recordes.pista"), True, (255, 255, 255))
        cabecalho_trofeu = fonte_cabecalho.render(t("recordes.trofeu"), True, (255, 255, 255))
        cabecalho_tempo = fonte_cabecalho.render(t("recordes.melhor_tempo"), True, (255, 255, 255))
        
        screen.blit(cabecalho_pista, (x_pista, y_inicial_corrida))
        screen.blit(cabecalho_trofeu, (x_trofeu, y_inicial_corrida))
        screen.blit(cabecalho_tempo, (x_tempo, y_inicial_corrida))
        
        # Linha separadora
        pygame.draw.line(screen, (128, 128, 128), 
                        (caixa_x + 20, y_inicial_corrida + 30), 
                        (caixa_x + caixa_largura // 2 - 20, y_inicial_corrida + 30), 2)
        
        # Listar recordes de corrida das 9 pistas
        y_atual = y_inicial_corrida + 45
        for pista_num in range(1, 10):
            # Nome da pista
            texto_pista = fonte_item.render(t("recordes.pista_numero").format(pista_num), True, (255, 255, 255))
            screen.blit(texto_pista, (x_pista, y_atual))
            
            # Troféu (sempre mostrar, vazio se não ganhou)
            trofeu_tipo = gerenciador_progresso.obter_trofeu(pista_num)
            if trofeu_tipo == "ouro" and trofeu_ouro:
                screen.blit(trofeu_ouro, (x_trofeu, y_atual - 5))
            elif trofeu_tipo == "prata" and trofeu_prata:
                screen.blit(trofeu_prata, (x_trofeu, y_atual - 5))
            elif trofeu_tipo == "bronze" and trofeu_bronze:
                screen.blit(trofeu_bronze, (x_trofeu, y_atual - 5))
            else:
                if trofeu_vazio:
                    screen.blit(trofeu_vazio, (x_trofeu, y_atual - 5))
            
            # Tempo
            recorde = gerenciador_progresso.obter_recorde(pista_num)
            texto_tempo = fonte_item.render(formatar_tempo(recorde), True, 
                                          (0, 255, 0) if recorde else (128, 128, 128))
            screen.blit(texto_tempo, (x_tempo, y_atual))
            
            y_atual += 35
        
        # === SEÇÃO DRIFT ===
        y_secao_drift = caixa_y + 70
        x_drift = caixa_x + caixa_largura // 2 + 30
        titulo_drift = fonte_secao.render(t("recordes.drift"), True, (255, 200, 0))
        screen.blit(titulo_drift, (x_drift, y_secao_drift))
        
        y_inicial_drift = y_secao_drift + 35
        x_pista_drift = x_drift
        x_trofeu_drift = x_drift + 120
        x_score_drift = x_drift + 200
        
        # Cabeçalhos drift
        cabecalho_pista_drift = fonte_cabecalho.render(t("recordes.pista"), True, (255, 255, 255))
        cabecalho_trofeu_drift = fonte_cabecalho.render(t("recordes.trofeu"), True, (255, 255, 255))
        cabecalho_score = fonte_cabecalho.render(t("jogo.melhor_score"), True, (255, 255, 255))
        
        screen.blit(cabecalho_pista_drift, (x_pista_drift, y_inicial_drift))
        screen.blit(cabecalho_trofeu_drift, (x_trofeu_drift, y_inicial_drift))
        screen.blit(cabecalho_score, (x_score_drift, y_inicial_drift))
        
        # Linha separadora
        pygame.draw.line(screen, (128, 128, 128), 
                        (x_drift - 10, y_inicial_drift + 30), 
                        (caixa_x + caixa_largura - 20, y_inicial_drift + 30), 2)
        
        # Função para determinar troféu por pontuação
        def obter_trofeu_por_pontuacao(pontuacao):
            """Retorna o tipo de troféu baseado na pontuação de drift"""
            if pontuacao is None:
                return None
            if pontuacao >= 50000:  # Alta pontuação = ouro
                return "ouro"
            elif pontuacao >= 20000:  # Média pontuação = prata
                return "prata"
            elif pontuacao >= 5000:  # Baixa pontuação = bronze
                return "bronze"
            else:
                return None
        
        # Listar recordes de drift das 9 pistas
        y_atual_drift = y_inicial_drift + 45
        for pista_num in range(1, 10):
            # Nome da pista
            texto_pista = fonte_item.render(t("recordes.pista_numero").format(pista_num), True, (255, 255, 255))
            screen.blit(texto_pista, (x_pista_drift, y_atual_drift))
            
            # Troféu baseado na pontuação
            recorde_drift = gerenciador_progresso.obter_recorde_drift(pista_num)
            trofeu_tipo_drift = obter_trofeu_por_pontuacao(recorde_drift)
            if trofeu_tipo_drift == "ouro" and trofeu_ouro:
                screen.blit(trofeu_ouro, (x_trofeu_drift, y_atual_drift - 5))
            elif trofeu_tipo_drift == "prata" and trofeu_prata:
                screen.blit(trofeu_prata, (x_trofeu_drift, y_atual_drift - 5))
            elif trofeu_tipo_drift == "bronze" and trofeu_bronze:
                screen.blit(trofeu_bronze, (x_trofeu_drift, y_atual_drift - 5))
            else:
                # Sempre mostrar troféu vazio se não ganhou troféu
                if trofeu_vazio:
                    screen.blit(trofeu_vazio, (x_trofeu_drift, y_atual_drift - 5))
            
            # Score
            texto_score = fonte_item.render(formatar_score(recorde_drift), True, 
                                          (255, 200, 0) if recorde_drift else (128, 128, 128))
            screen.blit(texto_score, (x_score_drift, y_atual_drift))
            
            y_atual_drift += 35
        
        # Botão voltar
        voltar_largura = 120
        voltar_altura = 40
        voltar_x = caixa_x + (caixa_largura - voltar_largura) // 2
        voltar_y = caixa_y + caixa_altura - 50
        voltar_rect = pygame.Rect(voltar_x, voltar_y, voltar_largura, voltar_altura)
        voltar_hover = voltar_rect.collidepoint(mouse_x, mouse_y)
        if voltar_hover:
            pygame.draw.rect(screen, (0, 200, 255, 50), voltar_rect)
        voltar_texto = render_text("VOLTAR", 20, (0, 200, 255) if voltar_hover else (255, 255, 255), bold=True, pixel_style=True)
        voltar_texto_x = voltar_x + (voltar_largura - voltar_texto.get_width()) // 2
        voltar_texto_y = voltar_y + (voltar_altura - voltar_texto.get_height()) // 2
        screen.blit(voltar_texto, (voltar_texto_x, voltar_texto_y))
        
        # Desenhar popup de música
        popup_musica.desenhar(screen)
        
        pygame.display.flip()

def run():
    from config import CONFIGURACOES, carregar_configuracoes
    pygame.init()
    from core.i18n import inicializar_idioma, t, atualizar_titulo_janela
    inicializar_idioma()
    atualizar_titulo_janela("menu")
    
    # Recarregar configurações para garantir que estão atualizadas
    carregar_configuracoes()
    
    # Aplicar configurações de vídeo
    resolucao = CONFIGURACOES["video"]["resolucao"]
    fullscreen = CONFIGURACOES["video"]["fullscreen"]
    tela_cheia_sem_bordas = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
    qualidade_alta = CONFIGURACOES["video"]["qualidade_alta"]
    
    # Configurar flags de display
    display_flags = 0
    if fullscreen:
        display_flags |= pygame.FULLSCREEN
    elif tela_cheia_sem_bordas:
        display_flags |= pygame.NOFRAME
    
    # Configurar qualidade
    if qualidade_alta:
        # Habilitar suavização para melhor qualidade
        pass
    
    screen = pygame.display.set_mode(resolucao, display_flags)
    
    # Loop principal que mantém a janela aberta
    carro_p1, carro_p2 = 0, 1  # Valores padrão
    
    # Iniciar música no menu se habilitada
    if CONFIGURACOES["audio"]["musica_habilitada"] and CONFIGURACOES["audio"]["musica_no_menu"]:
        gerenciador_musica.definir_volume(CONFIGURACOES["audio"]["volume_musica"])
        if not gerenciador_musica.musica_tocando:
            if CONFIGURACOES["audio"]["musica_aleatoria"]:
                gerenciador_musica.musica_aleatoria()
            else:
                gerenciador_musica.tocar_musica()
            if gerenciador_musica.musica_tocando:
                popup_musica.mostrar(gerenciador_musica.obter_nome_musica_atual())
    
    # Mostrar tela de splash primeiro
    if not splash_screen(screen):
        return  # Usuário fechou a janela na splash screen
    
    while True:
        escolha = menu_loop(screen)
        
        if escolha == Escolha.JOGAR:
            # Abrir tela de seleção de modo de jogo primeiro
            resultado_modo = modo_jogo_loop(screen)
            if resultado_modo is not None and isinstance(resultado_modo, tuple):  # Se não cancelou e é uma tupla
                if len(resultado_modo) == 5:  # Novo formato com voltas, dificuldade e fase
                    modo_jogo, tipo_jogo, voltas, dificuldade_ia, fase_selecionada = resultado_modo
                elif len(resultado_modo) == 4:  # Formato com voltas e dificuldade (sem fase)
                    modo_jogo, tipo_jogo, voltas, dificuldade_ia = resultado_modo
                    fase_selecionada = 1  # Padrão: fase 1
                else:  # Formato antigo (compatibilidade)
                    modo_jogo, tipo_jogo = resultado_modo
                    voltas = 1  # Padrão
                    dificuldade_ia = "medio"  # Padrão
                    fase_selecionada = 1  # Padrão
                
                # Parar música do menu se não deve tocar no jogo
                if not CONFIGURACOES["audio"]["musica_no_jogo"]:
                    gerenciador_musica.parar_musica()
                # inicia seu jogo original com carros selecionados e modos
                main.principal(carro_p1, carro_p2, mapa_selecionado=fase_selecionada, modo_jogo=modo_jogo, tipo_jogo=tipo_jogo, voltas=voltas, dificuldade_ia=dificuldade_ia)
                # Após o jogo, volta para o menu (não fecha a janela)
                # Reiniciar música do menu se habilitada
                if CONFIGURACOES["audio"]["musica_habilitada"] and CONFIGURACOES["audio"]["musica_no_menu"]:
                    if not gerenciador_musica.musica_tocando:
                        if CONFIGURACOES["audio"]["musica_aleatoria"]:
                            gerenciador_musica.musica_aleatoria()
                        else:
                            gerenciador_musica.tocar_musica()
                        if gerenciador_musica.musica_tocando:
                            popup_musica.mostrar(gerenciador_musica.obter_nome_musica_atual())
        elif escolha == Escolha.SELECIONAR_CARROS:
            # Abre tela de seleção de carros
            resultado = selecionar_carros_loop(screen)
            if resultado[0] is not None and resultado[1] is not None:
                carro_p1, carro_p2 = resultado
        elif escolha == Escolha.RECORDES:
            # Abre tela de recordes
            recordes_loop(screen)
        elif escolha == Escolha.OPCOES:
            # Abre tela de opções
            opcoes_loop(screen)
            # Atualizar configurações de música após sair das opções
            gerenciador_musica.definir_volume(CONFIGURACOES["audio"]["volume_musica"])
            if not CONFIGURACOES["audio"]["musica_habilitada"]:
                gerenciador_musica.parar_musica()
            elif CONFIGURACOES["audio"]["musica_habilitada"] and CONFIGURACOES["audio"]["musica_no_menu"] and not gerenciador_musica.musica_tocando:
                if CONFIGURACOES["audio"]["musica_aleatoria"]:
                    gerenciador_musica.musica_aleatoria()
                else:
                    gerenciador_musica.tocar_musica()
                if gerenciador_musica.musica_tocando:
                    popup_musica.mostrar(gerenciador_musica.obter_nome_musica_atual())
        elif escolha == Escolha.SAIR:
            break
    
    pygame.quit()


if __name__ == "__main__":
    run()
