import os
import sys
import math
import json
import pygame
from enum import Enum

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import LARGURA, ALTURA, FPS, CAMINHO_MENU, CONFIGURACOES, MAPAS_DISPONIVEIS, DIR_PROJETO, obter_caminho_sprite_dia_noite
import main
from core.musica import gerenciador_musica
from core.popup_musica import popup_musica
from core.game_modes import ModoJogo, TipoJogo
from core.progresso import gerenciador_progresso
from core.gamepad_manager import gerenciador_gamepad
from core.casa import casa_loop

_tinha_dinheiro_anterior = None

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

def desenhar_scrollbar(screen, scroll_offset, max_scroll, caixa_x, caixa_y, caixa_largura, caixa_altura, scroll_dragging=False):
    """Desenha uma barra de rolagem"""
    if max_scroll <= 0:
        return
    
    scrollbar_width = 12
    scrollbar_x = caixa_x + caixa_largura - scrollbar_width - 5
    scrollbar_y = caixa_y + 80
    scrollbar_height = caixa_altura - 200
    
    scroll_ratio = scroll_offset / max_scroll if max_scroll > 0 else 0
    indicator_height = max(30, int(scrollbar_height * 0.3))
    indicator_y = scrollbar_y + int(scroll_ratio * (scrollbar_height - indicator_height))
    
    scrollbar_bg = pygame.Surface((scrollbar_width, scrollbar_height), pygame.SRCALPHA)
    scrollbar_bg.fill((50, 50, 50, 150))
    screen.blit(scrollbar_bg, (scrollbar_x, scrollbar_y))
    
    indicator_color = (180, 180, 180, 200) if not scroll_dragging else (220, 220, 220, 200)
    indicator_bg = pygame.Surface((scrollbar_width - 2, indicator_height), pygame.SRCALPHA)
    indicator_bg.fill(indicator_color)
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
            
            char_index = 95
            
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
    
    base_size = 12
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
                    if pixel[0] > 128:
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
        
        if not any(os.path.exists(font_path) for font_path in pixel_fonts):
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
        # Usar fonte padrão do sistema que suporta acentos (não pixel art)
        system_fonts = [
            "arial",           # Arial (fallback padrão)
            "segoe ui",        # Segoe UI (Windows moderno)
            "tahoma",          # Tahoma (Windows)
            "verdana",         # Verdana (legível)
            "helvetica",       # Helvetica (macOS)
            "sans-serif"       # Genérico
        ]
        
        font = None
        for font_name in system_fonts:
            try:
                font = pygame.font.SysFont(font_name, size, bold=bold)
                # Testar se a fonte funciona renderizando um caractere
                test_surface = font.render("A", True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    break
            except:
                continue
        
        # Fallback final
        if font is None:
            font = pygame.font.Font(None, size)
    
    # Renderizar texto com contorno para estilo pixel art
    if pixel_style and size >= 14:
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
    OPCOES = 0
    JOGAR = 1
    SAIR = 2

def splash_screen(screen) -> bool:
    """Tela de splash com 'Aperte qualquer botão para iniciar'"""
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)
    
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    
    fade_surface = pygame.Surface((LARGURA, ALTURA))
    fade_surface.fill((0, 0, 0))
    
    while True:
        try:
            dt = clock.tick(FPS) / 1000.0
            try:
                gerenciador_musica.verificar_fim_musica()
            except Exception as e:
                print(f"Erro em verificar_fim_musica: {e}")
                import traceback
                traceback.print_exc()
            
            try:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        return False
                    if gerenciador_gamepad.obter_numero_controles() > 0:
                        if ev.type == pygame.JOYBUTTONDOWN:
                            return True
                        elif ev.type == pygame.JOYHATMOTION:
                            hat_x, hat_y = ev.value
                            if hat_x != 0 or hat_y != 0:
                                return True
                    if ev.type == pygame.KEYDOWN or ev.type == pygame.MOUSEBUTTONDOWN:
                        return True
            except (SystemError, KeyError) as e:
                print(f"Erro ao obter eventos do pygame: {e}")
                import traceback
                traceback.print_exc()
                # Tentar continuar mesmo com erro
                pass
        except Exception as e:
            print(f"Erro inesperado na splash screen: {e}")
            import traceback
            traceback.print_exc()
            # Tentar continuar
            pass
        
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

# Cache de ícones e textos para a tela de achievements (evita lag)
_achievements_cache = {
    'icon_achievements': None,
    'icon_conquista_concluida': None,
    'icon_achievements_escuro': None,
    'carregado': False
}

def _carregar_cache_achievements():
    """Carrega os ícones uma vez e armazena em cache"""
    if _achievements_cache['carregado']:
        return
    
    from config import DIR_ICONS
    import os
    
    # Carregar ícone de achievements
    caminho_achievements = os.path.join(DIR_ICONS, "achievements.png")
    if os.path.exists(caminho_achievements):
        try:
            icon_achievements = pygame.image.load(caminho_achievements).convert_alpha()
            _achievements_cache['icon_achievements'] = pygame.transform.scale(icon_achievements, (35, 35))
            # Criar versão escura para achievements não desbloqueados
            icon_escuro = icon_achievements.copy()
            icon_escuro.set_alpha(150)
            _achievements_cache['icon_achievements_escuro'] = pygame.transform.scale(icon_escuro, (35, 35))
        except:
            pass
    
    # Carregar ícone de conquista concluída (mesma altura do ícone normal, mantendo proporção)
    caminho_conquista_concluida = os.path.join(DIR_ICONS, "conquista_concluida.png")
    if os.path.exists(caminho_conquista_concluida):
        try:
            icon_concluida = pygame.image.load(caminho_conquista_concluida).convert_alpha()
            largura_original, altura_original = icon_concluida.get_size()
            altura_alvo = 35
            escala = altura_alvo / altura_original
            largura_alvo = int(largura_original * escala)
            # Usar smoothscale para melhor qualidade
            _achievements_cache['icon_conquista_concluida'] = pygame.transform.smoothscale(icon_concluida, (largura_alvo, altura_alvo))
        except:
            pass
    
    _achievements_cache['carregado'] = True

# Variável global para controlar o scroll dos achievements
_achievements_scroll_offset = 0.0
_achievements_scroll_dragging = False
_achievements_scroll_drag_start_y = 0
_achievements_scroll_drag_start_offset = 0.0
_achievements_animacao_cursor = 0.0

def desenhar_tela_achievements(screen, dt):
    """Desenha a tela de achievements/conquistas no menu"""
    global _achievements_scroll_offset, _achievements_scroll_dragging, _achievements_scroll_drag_start_y, _achievements_scroll_drag_start_offset, _achievements_animacao_cursor
    from core.achievements import gerenciador_achievements, ACHIEVEMENTS
    from core.i18n import t
    
    # Atualizar animação do cursor do controle
    _achievements_animacao_cursor += dt * 3.0
    if _achievements_animacao_cursor >= 1.0:
        _achievements_animacao_cursor = 0.0
    
    # Carregar cache de ícones (apenas uma vez)
    _carregar_cache_achievements()
    
    # Overlay escuro
    overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    # Caixa principal
    caixa_largura = 800
    caixa_altura = 600
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2
    
    caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
    caixa_fundo.fill((0, 0, 0, 240))
    screen.blit(caixa_fundo, (caixa_x, caixa_y))
    pygame.draw.rect(screen, (255, 215, 0), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
    
    # Título (traduzido) - cachear se não mudou
    titulo_texto = t("achievements.titulo")
    titulo = render_text(titulo_texto, 48, (255, 215, 0), bold=True, pixel_style=True)
    titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
    screen.blit(titulo, (titulo_x, caixa_y + 20))
    
    # Progresso total (traduzido)
    total = gerenciador_achievements.contar_total()
    desbloqueados = gerenciador_achievements.contar_desbloqueados()
    progresso_texto_str = f"{desbloqueados}/{total} {t('achievements.desbloqueados')}"
    progresso_texto = render_text(progresso_texto_str, 24, (200, 200, 200), bold=True, pixel_style=True)
    progresso_x = caixa_x + (caixa_largura - progresso_texto.get_width()) // 2
    screen.blit(progresso_texto, (progresso_x, caixa_y + 80))
    
    # Área de scroll para achievements
    area_scroll_y = caixa_y + 120
    area_scroll_altura = caixa_altura - 200  # Altura disponível para achievements (deixando espaço para título, progresso e botão fechar)
    area_scroll_x = caixa_x + 20
    area_scroll_largura = caixa_largura - 60  # Largura menos margens e espaço para barra de rolagem
    
    # Lista de achievements
    y_inicio = area_scroll_y
    y_atual = y_inicio - _achievements_scroll_offset
    espacamento = 70  # Aumentado para acomodar texto maior
    
    achievements = gerenciador_achievements.obter_todos_achievements()
    altura_total = len(achievements) * espacamento
    altura_visivel = area_scroll_altura
    
    # Limitar scroll offset
    scroll_max = max(0, altura_total - altura_visivel)
    _achievements_scroll_offset = max(0, min(_achievements_scroll_offset, scroll_max))
    
    # Mapeamento de IDs para chaves de tradução
    traducoes_achievements = {
        "primeira_corrida": ("primeira_corrida", "primeira_corrida_desc"),
        "velocista": ("velocista", "velocista_desc"),
        "velocista_pro": ("velocista_pro", "velocista_pro_desc"),
        "velocidade_extrema": ("velocidade_extrema", "velocidade_extrema_desc"),
        "drift_master": ("drift_master", "drift_master_desc"),
        "drift_expert": ("drift_expert", "drift_expert_desc"),
        "drift_legend": ("drift_legend", "drift_legend_desc"),
        "sem_colisao": ("sem_colisao", "sem_colisao_desc"),
        "sem_colisao_mestre": ("sem_colisao_mestre", "sem_colisao_mestre_desc"),
        "trofeu_ouro": ("trofeu_ouro", "trofeu_ouro_desc"),
        "colecionador": ("colecionador", "colecionador_desc"),
        "colecionador_pro": ("colecionador_pro", "colecionador_pro_desc"),
        "perfeccionista": ("perfeccionista", "perfeccionista_desc"),
        "perfeccionista_mestre": ("perfeccionista_mestre", "perfeccionista_mestre_desc"),
        "sem_erros_perfeito": ("sem_erros_perfeito", "sem_erros_perfeito_desc"),
        "recordista": ("recordista", "recordista_desc"),
        "recordista_pro": ("recordista_pro", "recordista_pro_desc"),
        "upgrade_completo": ("upgrade_completo", "upgrade_completo_desc"),
        "upgrade_mestre": ("upgrade_mestre", "upgrade_mestre_desc"),
        "veterano": ("veterano", "veterano_desc"),
        "lenda": ("lenda", "lenda_desc"),
        "piloto_estrella": ("piloto_estrella", "piloto_estrella_desc"),
    }
    
    # Criar surface para clipping (máscara de recorte)
    scroll_surface = pygame.Surface((area_scroll_largura, area_scroll_altura), pygame.SRCALPHA)
    scroll_surface.fill((0, 0, 0, 0))  # Transparente
    
    for achievement in achievements:
        if y_atual + espacamento < area_scroll_y:
            y_atual += espacamento
            continue
        if y_atual > area_scroll_y + area_scroll_altura:
            break
        
        achievement_id = achievement['id']
        
        if achievement_id in traducoes_achievements:
            chave_nome, chave_desc = traducoes_achievements[achievement_id]
            nome_traduzido = t(f"achievements.{chave_nome}")
            desc_traduzida = t(f"achievements.{chave_desc}")
        else:
            nome_traduzido = achievement['nome']
            desc_traduzida = achievement['descricao']
        
        # Cor baseado no status (verde quando desbloqueado)
        if achievement['desbloqueado']:
            cor_fundo = (50, 150, 50, 180)  # Verde mais intenso
            cor_texto = (255, 255, 255)
            cor_icone = (255, 215, 0)
        else:
            cor_fundo = (30, 30, 30, 150)
            cor_texto = (150, 150, 150)
            cor_icone = (100, 100, 100)
        
        y_relativo = y_atual - area_scroll_y
        
        # Fundo do achievement (aumentado para acomodar texto maior)
        achievement_rect = pygame.Rect(0, y_relativo, area_scroll_largura, 60)
        achievement_surface = pygame.Surface((achievement_rect.width, achievement_rect.height), pygame.SRCALPHA)
        achievement_surface.fill(cor_fundo)
        scroll_surface.blit(achievement_surface, achievement_rect.topleft)
        pygame.draw.rect(scroll_surface, cor_texto, achievement_rect, 2)
        
        # Ícone do achievement - usar conquista_concluida.png se desbloqueado, achievements.png se não
        if achievement['desbloqueado']:
            # Usar ícone de conquista concluída quando desbloqueado
            if _achievements_cache['icon_conquista_concluida']:
                icon_concluida = _achievements_cache['icon_conquista_concluida']
                # Centralizar o ícone (pode ter tamanho diferente devido à proporção)
                icon_largura, icon_altura = icon_concluida.get_size()
                icon_x = 5  # Posição X relativa
                icon_y = y_relativo + (60 - icon_altura) // 2  # Centralizar verticalmente
                scroll_surface.blit(icon_concluida, (icon_x, icon_y))
            texto_x = 50  # Mesma posição do texto
        else:
            # Usar ícone de achievements quando não desbloqueado
            if _achievements_cache['icon_achievements_escuro']:
                icon_x = 5
                icon_y = y_relativo + 12  # Centralizado para ícone 35x35
                scroll_surface.blit(_achievements_cache['icon_achievements_escuro'], (icon_x, icon_y))
            texto_x = 50
        
        # Nome e descrição (traduzidos) - usar render_text com tamanhos maiores
        nome_texto = render_text(nome_traduzido, 22, cor_texto, bold=True, pixel_style=True)
        scroll_surface.blit(nome_texto, (texto_x, y_relativo + 6))
        
        desc_texto = render_text(desc_traduzida, 18, cor_texto, bold=False, pixel_style=True)
        scroll_surface.blit(desc_texto, (texto_x, y_relativo + 32))
        
        # Recompensa
        if achievement['desbloqueado']:
            recompensa_texto = render_text(f"+${achievement['recompensa']}", 18, (255, 215, 0), bold=True, pixel_style=True)
            scroll_surface.blit(recompensa_texto, (area_scroll_largura - 120, y_relativo + 15))
        
        y_atual += espacamento
    
    # Desenhar a surface de scroll na tela
    screen.blit(scroll_surface, (area_scroll_x, area_scroll_y))
    
    # Desenhar barra de rolagem (se necessário)
    if altura_total > altura_visivel:
        barra_largura = 12
        barra_x = caixa_x + caixa_largura - 30
        barra_y = area_scroll_y
        barra_altura = area_scroll_altura
        
        thumb_altura = max(30, int((altura_visivel / altura_total) * barra_altura))
        thumb_y = barra_y + int((_achievements_scroll_offset / scroll_max) * (barra_altura - thumb_altura)) if scroll_max > 0 else barra_y
        
        # Desenhar trilha da barra
        pygame.draw.rect(screen, (60, 60, 60), (barra_x, barra_y, barra_largura, barra_altura))
        pygame.draw.rect(screen, (100, 100, 100), (barra_x, barra_y, barra_largura, barra_altura), 1)
        
        # Desenhar thumb (indicador)
        cor_thumb = (180, 180, 180) if not _achievements_scroll_dragging else (220, 220, 220)
        pygame.draw.rect(screen, cor_thumb, (barra_x + 2, thumb_y, barra_largura - 4, thumb_altura))
        pygame.draw.rect(screen, (255, 255, 255), (barra_x + 2, thumb_y, barra_largura - 4, thumb_altura), 1)
    
    # Botão fechar (padronizado com estatísticas e desafios)
    botao_fechar_rect = pygame.Rect(caixa_x + caixa_largura - 120, caixa_y + 20, 100, 40)
    mouse_x, mouse_y = pygame.mouse.get_pos()
    fechar_hover = botao_fechar_rect.collidepoint(mouse_x, mouse_y)
    
    from core.gamepad_manager import gerenciador_gamepad
    fechar_selecionado = getattr(desenhar_tela_achievements, '_fechar_selecionado', False)
    
    # Cores do botão baseadas no hover ou seleção (mesmo estilo das outras telas)
    cor_fundo = (255, 80, 80) if (fechar_hover or fechar_selecionado) else (200, 50, 50)
    cor_borda = (255, 150, 150) if (fechar_hover or fechar_selecionado) else (255, 100, 100)
    
    pygame.draw.rect(screen, cor_fundo, botao_fechar_rect)
    pygame.draw.rect(screen, cor_borda, botao_fechar_rect, 2)
    
    # Desenhar cursor do controle se selecionado
    if fechar_selecionado and gerenciador_gamepad.obter_numero_controles() > 0:
        tamanho_cursor = 3 + int(2 * abs(math.sin(_achievements_animacao_cursor * math.pi)))
        cursor_rect = pygame.Rect(
            botao_fechar_rect.x - tamanho_cursor,
            botao_fechar_rect.y - tamanho_cursor,
            botao_fechar_rect.width + tamanho_cursor * 2,
            botao_fechar_rect.height + tamanho_cursor * 2
        )
        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
    
    fechar_texto = render_text(t("menu.fechar"), 18, (255, 255, 255), bold=True, pixel_style=True)
    fechar_x = botao_fechar_rect.x + (botao_fechar_rect.width - fechar_texto.get_width()) // 2
    fechar_y = botao_fechar_rect.y + (botao_fechar_rect.height - fechar_texto.get_height()) // 2
    screen.blit(fechar_texto, (fechar_x, fechar_y))
    
    # Instrução (traduzida)
    instrucao = render_text(t("menu.esc_para_fechar"), 16, (150, 150, 150), bold=False, pixel_style=True)
    screen.blit(instrucao, (caixa_x + 20, caixa_y + caixa_altura - 30))

# Variáveis globais para animação do cursor nas telas
_estatisticas_animacao_cursor = 0.0
_estatisticas_scroll_offset = 0.0
_estatisticas_scroll_dragging = False
_estatisticas_scroll_drag_start_y = 0
_estatisticas_scroll_drag_start_offset = 0
_estatisticas_altura_total = 0
_desafios_animacao_cursor = 0.0

def _traduzir_descricao_desafio(desafio):
    """Traduz a descrição de um desafio baseado no tipo e objetivo"""
    from core.i18n import t
    tipo = desafio.get("tipo", "")
    objetivo = desafio.get("objetivo", 0)
    
    if tipo == "completar_corridas":
        return t("desafios.descricao.completar_corridas").format(objetivo=objetivo)
    elif tipo == "vencer_corridas":
        return t("desafios.descricao.vencer_corridas").format(objetivo=objetivo)
    elif tipo == "completar_voltas":
        return t("desafios.descricao.completar_voltas").format(objetivo=objetivo)
    elif tipo == "usar_turbo":
        return t("desafios.descricao.usar_turbo").format(objetivo=objetivo)
    elif tipo == "estabelecer_recorde":
        return t("desafios.descricao.estabelecer_recorde").format(objetivo=objetivo)
    else:
        # Fallback: usar descrição original se não houver tradução
        return desafio.get("descricao", "")

def desenhar_tela_estatisticas(screen, dt, mouse_x=None, mouse_y=None):
    """Desenha a tela de estatísticas detalhadas"""
    global _estatisticas_animacao_cursor, _estatisticas_scroll_offset, _estatisticas_altura_total
    from core.i18n import t
    from core.estatisticas import gerenciador_estatisticas
    
    # Atualizar animação do cursor do controle
    _estatisticas_animacao_cursor += dt * 3.0
    if _estatisticas_animacao_cursor >= 1.0:
        _estatisticas_animacao_cursor = 0.0
    
    overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    caixa_largura = 800
    caixa_altura = 600
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2
    
    caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
    caixa_fundo.fill((0, 0, 0, 240))
    screen.blit(caixa_fundo, (caixa_x, caixa_y))
    pygame.draw.rect(screen, (100, 150, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
    
    titulo = render_text(t("estatisticas.titulo"), 48, (100, 220, 255), bold=True, pixel_style=True)
    titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
    screen.blit(titulo, (titulo_x, caixa_y + 20))
    
    stats_gerais = gerenciador_estatisticas.obter_estatisticas_gerais()
    
    # Adicionar seção de recordes (tempos e scores)
    from core.progresso import gerenciador_progresso
    
    def formatar_tempo_estat(tempo):
        """Formata tempo em segundos para MM:SS.CC"""
        if tempo is None:
            return "--:--.--"
        minutos = int(tempo // 60)
        segundos = int(tempo % 60)
        centesimos = int((tempo % 1) * 100)
        return f"{minutos:02d}:{segundos:02d}.{centesimos:02d}"
    
    def formatar_score_estat(score):
        """Formata score para exibição"""
        if score is None:
            return "--"
        score_int = int(score)
        if score_int >= 1000:
            return f"{score_int:,}".replace(",", ".")
        return str(score_int)
    
    # Coletar melhores tempos de corrida das estatísticas (não dos recordes)
    recordes_corrida_texto = []
    for pista_num in range(1, 10):
        # Usar melhor_tempo das estatísticas por pista (mais preciso)
        stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(pista_num)
        melhor_tempo = stats_pista.get("melhor_tempo")
        # Se não houver nas estatísticas, tentar obter do recorde como fallback
        if melhor_tempo is None:
            melhor_tempo = gerenciador_progresso.obter_recorde(pista_num)
        if melhor_tempo is not None:
            recordes_corrida_texto.append(t("estatisticas.pista_tempo").format(pista=pista_num, tempo=formatar_tempo_estat(melhor_tempo)))
    
    # Coletar recordes de drift (buscar todas as chaves no formato "pista_voltas")
    recordes_drift_texto = []
    recordes_drift_dict = gerenciador_progresso.recordes_drift
    for chave, pontuacao in recordes_drift_dict.items():
        # Chave pode ser "1_1", "2_3", etc. (pista_voltas)
        try:
            pista_num = int(chave.split('_')[0])
            recordes_drift_texto.append(t("estatisticas.pista_score").format(pista=pista_num, score=formatar_score_estat(pontuacao)))
        except (ValueError, IndexError):
            # Se a chave não estiver no formato esperado, pular
            continue
    
    # Coletar melhores tempos do modo relógio (GHOST)
    # No modo GHOST, o tempo é salvo como recorde de corrida
    recordes_relogio_texto = []
    for pista_num in range(1, 10):
        # Tentar obter do recorde primeiro (modo GHOST salva como recorde)
        melhor_tempo = gerenciador_progresso.obter_recorde(pista_num)
        # Se não houver recorde, verificar nas estatísticas
        if melhor_tempo is None:
            stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(pista_num)
            melhor_tempo = stats_pista.get("melhor_tempo")
        if melhor_tempo is not None:
            recordes_relogio_texto.append(t("estatisticas.pista_tempo").format(pista=pista_num, tempo=formatar_tempo_estat(melhor_tempo)))
    
    secoes = [
        (t("estatisticas.gerais"), [
            (t("estatisticas.tempo_total_jogado"), gerenciador_estatisticas.formatar_tempo(stats_gerais["tempo_total_jogado"])),
            (t("estatisticas.distancia_total"), gerenciador_estatisticas.formatar_distancia(stats_gerais["distancia_total"])),
            (t("estatisticas.corridas_completas"), str(stats_gerais["corridas_completas"])),
            (t("estatisticas.corridas_vencidas"), str(stats_gerais["corridas_vencidas"])),
            (t("estatisticas.voltas_completas"), str(stats_gerais["voltas_completas"])),
            (t("estatisticas.colisoes_totais"), str(stats_gerais["colisoes_totais"])),
            (t("estatisticas.drifts_totais"), str(stats_gerais["drifts_totais"])),
            (t("estatisticas.turbo_usado"), str(stats_gerais["turbo_usado"])),
            (t("estatisticas.recordes_estabelecidos"), str(stats_gerais["recordes_estabelecidos"])),
            (t("estatisticas.trofeus_ganhos"), str(stats_gerais["trofeus_ganhos"]))
        ])
    ]
    
    # Adicionar seção de recordes de corrida se houver
    if recordes_corrida_texto:
        secoes.append((t("estatisticas.melhores_tempos_corrida"), recordes_corrida_texto))
    
    # Adicionar seção de recordes de drift se houver
    if recordes_drift_texto:
        secoes.append((t("estatisticas.melhores_scores_drift"), recordes_drift_texto))
    
    # Adicionar seção de recordes de relógio (GHOST) se houver
    if recordes_relogio_texto:
        secoes.append((t("estatisticas.melhores_tempos_relogio"), recordes_relogio_texto))
    
    # Criar superfície com scroll para conteúdo
    # Aumentar altura da área de conteúdo para evitar corte
    area_conteudo_altura = caixa_altura - 120  # Reduzir margem superior/inferior
    conteudo_surface = pygame.Surface((caixa_largura - 60, max(area_conteudo_altura, 1000)), pygame.SRCALPHA)  # Superfície maior para scroll
    conteudo_surface.fill((0, 0, 0, 0))
    
    scroll_y = 0
    y_conteudo = 0
    
    for secao_nome, itens in secoes:
        secao_titulo = render_text(secao_nome, 28, (150, 200, 255), bold=True, pixel_style=True)
        conteudo_surface.blit(secao_titulo, (30, y_conteudo))
        y_conteudo += 40
        
        for item in itens:
            if isinstance(item, tuple):
                nome, valor = item
                nome_texto = render_text(nome, 18, (200, 200, 200), bold=False, pixel_style=True)
                valor_texto = render_text(str(valor), 18, (100, 220, 255), bold=True, pixel_style=True)
                conteudo_surface.blit(nome_texto, (50, y_conteudo))
                conteudo_surface.blit(valor_texto, (caixa_largura - 310, y_conteudo))
            else:
                # Item simples (string)
                item_texto = render_text(str(item), 16, (200, 200, 200), bold=False, pixel_style=True)
                conteudo_surface.blit(item_texto, (50, y_conteudo))
            y_conteudo += 35
        
        y_conteudo += 10  # Espaço entre seções
    
    altura_total_conteudo = y_conteudo
    _estatisticas_altura_total = altura_total_conteudo  # Armazenar para uso no scroll
    scroll_max = max(0, altura_total_conteudo - area_conteudo_altura)
    _estatisticas_scroll_offset = max(0, min(_estatisticas_scroll_offset, scroll_max))
    
    # Criar área de clipping para o conteúdo (ajustar posição Y para mais espaço)
    clip_rect = pygame.Rect(caixa_x + 30, caixa_y + 70, caixa_largura - 60, area_conteudo_altura)
    screen.set_clip(clip_rect)
    
    # Desenhar conteúdo com scroll
    screen.blit(conteudo_surface, (caixa_x + 30, caixa_y + 70 - _estatisticas_scroll_offset))
    
    # Remover clipping
    screen.set_clip(None)
    
    # Desenhar barra de scroll se necessário
    if scroll_max > 0:
        desenhar_scrollbar(screen, _estatisticas_scroll_offset, scroll_max, caixa_x, caixa_y, caixa_largura, caixa_altura, _estatisticas_scroll_dragging)
    
    botao_fechar_rect = pygame.Rect(caixa_x + caixa_largura - 120, caixa_y + 20, 100, 40)
    fechar_hover = False
    if mouse_x is not None and mouse_y is not None:
        fechar_hover = botao_fechar_rect.collidepoint(mouse_x, mouse_y)
    
    from core.gamepad_manager import gerenciador_gamepad
    fechar_selecionado = getattr(desenhar_tela_estatisticas, '_fechar_selecionado', False)
    
    # Cores do botão baseadas no hover ou seleção
    cor_fundo = (255, 80, 80) if (fechar_hover or fechar_selecionado) else (200, 50, 50)
    cor_borda = (255, 150, 150) if (fechar_hover or fechar_selecionado) else (255, 100, 100)
    
    pygame.draw.rect(screen, cor_fundo, botao_fechar_rect)
    pygame.draw.rect(screen, cor_borda, botao_fechar_rect, 2)
    
    # Desenhar cursor do controle se selecionado
    if fechar_selecionado and gerenciador_gamepad.obter_numero_controles() > 0:
        tamanho_cursor = 3 + int(2 * abs(math.sin(_estatisticas_animacao_cursor * math.pi)))
        cursor_rect = pygame.Rect(
            botao_fechar_rect.x - tamanho_cursor,
            botao_fechar_rect.y - tamanho_cursor,
            botao_fechar_rect.width + tamanho_cursor * 2,
            botao_fechar_rect.height + tamanho_cursor * 2
        )
        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
    
    fechar_texto = render_text(t("menu.fechar"), 18, (255, 255, 255), bold=True, pixel_style=True)
    fechar_x = botao_fechar_rect.x + (botao_fechar_rect.width - fechar_texto.get_width()) // 2
    fechar_y = botao_fechar_rect.y + (botao_fechar_rect.height - fechar_texto.get_height()) // 2
    screen.blit(fechar_texto, (fechar_x, fechar_y))
    
    return botao_fechar_rect

def desenhar_tela_desafios(screen, dt):
    """Desenha a tela de desafios/missões"""
    global _desafios_animacao_cursor
    from core.i18n import t
    from core.desafios import gerenciador_desafios
    
    # Atualizar animação do cursor do controle
    _desafios_animacao_cursor += dt * 3.0
    if _desafios_animacao_cursor >= 1.0:
        _desafios_animacao_cursor = 0.0
    
    overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    caixa_largura = 900
    caixa_altura = 700
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2
    
    caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
    caixa_fundo.fill((20, 20, 30, 240))
    screen.blit(caixa_fundo, (caixa_x, caixa_y))
    pygame.draw.rect(screen, (100, 150, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
    
    titulo = render_text(t("desafios.titulo"), 48, (100, 220, 255), bold=True, pixel_style=True)
    titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
    screen.blit(titulo, (titulo_x, caixa_y + 20))
    
    y_atual = caixa_y + 90
    
    desafios_diarios = gerenciador_desafios.obter_desafios_diarios()
    desafios_semanais = gerenciador_desafios.obter_desafios_semanais()
    
    if desafios_diarios:
        secao_titulo = render_text(t("desafios.diarios"), 28, (150, 200, 255), bold=True, pixel_style=True)
        screen.blit(secao_titulo, (caixa_x + 30, y_atual))
        y_atual += 40
        
        for desafio in desafios_diarios:
            if y_atual > caixa_y + caixa_altura - 100:
                break
            progresso = gerenciador_desafios.obter_progresso(desafio["id"])
            # Garantir que o progresso não exceda o objetivo
            progresso = min(progresso, desafio["objetivo"])
            porcentagem = min(100, int((progresso / desafio["objetivo"]) * 100))
            esta_completo = gerenciador_desafios.esta_completado(desafio["id"])
            
            # Cores diferentes para desafios completados
            if esta_completo:
                cor_desc = (150, 255, 150)  # Verde para completado
                cor_progresso = (100, 255, 100)  # Verde mais claro
                status_texto = render_text(t("desafios.concluido"), 14, (100, 255, 100), bold=True, pixel_style=True)
            else:
                cor_desc = (200, 200, 200)  # Cinza normal
                cor_progresso = (100, 220, 255)  # Azul normal
                status_texto = None
            
            # Traduzir descrição do desafio
            descricao_traduzida = _traduzir_descricao_desafio(desafio)
            desc_texto = render_text(descricao_traduzida, 18, cor_desc, bold=False, pixel_style=True)
            progresso_texto = render_text(f"{progresso}/{desafio['objetivo']} ({porcentagem}%)", 16, cor_progresso, bold=True, pixel_style=True)
            recompensa_texto = render_text(t("desafios.recompensa").format(recompensa=desafio['recompensa']), 16, (150, 255, 150), bold=True, pixel_style=True)
            
            screen.blit(desc_texto, (caixa_x + 50, y_atual))
            screen.blit(progresso_texto, (caixa_x + 50, y_atual + 25))
            if status_texto:
                screen.blit(status_texto, (caixa_x + 50 + desc_texto.get_width() + 10, y_atual))
            screen.blit(recompensa_texto, (caixa_x + caixa_largura - 250, y_atual))
            y_atual += 60
    
    if desafios_semanais:
        y_atual += 20
        secao_titulo = render_text(t("desafios.semanais"), 28, (200, 150, 255), bold=True, pixel_style=True)
        screen.blit(secao_titulo, (caixa_x + 30, y_atual))
        y_atual += 40
        
        for desafio in desafios_semanais:
            if y_atual > caixa_y + caixa_altura - 100:
                break
            progresso = gerenciador_desafios.obter_progresso(desafio["id"])
            # Garantir que o progresso não exceda o objetivo
            progresso = min(progresso, desafio["objetivo"])
            porcentagem = min(100, int((progresso / desafio["objetivo"]) * 100))
            esta_completo = gerenciador_desafios.esta_completado(desafio["id"])
            
            # Cores diferentes para desafios completados
            if esta_completo:
                cor_desc = (200, 150, 255)  # Roxo claro para completado
                cor_progresso = (180, 120, 255)  # Roxo mais claro
                status_texto = render_text(t("desafios.concluido"), 14, (180, 120, 255), bold=True, pixel_style=True)
            else:
                cor_desc = (200, 200, 200)  # Cinza normal
                cor_progresso = (100, 220, 255)  # Azul normal
                status_texto = None
            
            # Traduzir descrição do desafio
            descricao_traduzida = _traduzir_descricao_desafio(desafio)
            desc_texto = render_text(descricao_traduzida, 18, cor_desc, bold=False, pixel_style=True)
            progresso_texto = render_text(f"{progresso}/{desafio['objetivo']} ({porcentagem}%)", 16, cor_progresso, bold=True, pixel_style=True)
            recompensa_texto = render_text(t("desafios.recompensa").format(recompensa=desafio['recompensa']), 16, (200, 150, 255), bold=True, pixel_style=True)
            
            screen.blit(desc_texto, (caixa_x + 50, y_atual))
            screen.blit(progresso_texto, (caixa_x + 50, y_atual + 25))
            if status_texto:
                screen.blit(status_texto, (caixa_x + 50 + desc_texto.get_width() + 10, y_atual))
            screen.blit(recompensa_texto, (caixa_x + caixa_largura - 250, y_atual))
            y_atual += 60
    
    botao_fechar_rect = pygame.Rect(caixa_x + caixa_largura - 120, caixa_y + 20, 100, 40)
    mouse_x, mouse_y = pygame.mouse.get_pos()
    fechar_hover = botao_fechar_rect.collidepoint(mouse_x, mouse_y)
    
    from core.gamepad_manager import gerenciador_gamepad
    fechar_selecionado = getattr(desenhar_tela_desafios, '_fechar_selecionado', False)
    
    # Cores do botão baseadas no hover ou seleção
    cor_fundo = (255, 80, 80) if (fechar_hover or fechar_selecionado) else (200, 50, 50)
    cor_borda = (255, 150, 150) if (fechar_hover or fechar_selecionado) else (255, 100, 100)
    
    pygame.draw.rect(screen, cor_fundo, botao_fechar_rect)
    pygame.draw.rect(screen, cor_borda, botao_fechar_rect, 2)
    
    # Desenhar cursor do controle se selecionado
    if fechar_selecionado and gerenciador_gamepad.obter_numero_controles() > 0:
        tamanho_cursor = 3 + int(2 * abs(math.sin(_desafios_animacao_cursor * math.pi)))
        cursor_rect = pygame.Rect(
            botao_fechar_rect.x - tamanho_cursor,
            botao_fechar_rect.y - tamanho_cursor,
            botao_fechar_rect.width + tamanho_cursor * 2,
            botao_fechar_rect.height + tamanho_cursor * 2
        )
        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
    
    fechar_texto = render_text(t("menu.fechar"), 18, (255, 255, 255), bold=True, pixel_style=True)
    fechar_x = botao_fechar_rect.x + (botao_fechar_rect.width - fechar_texto.get_width()) // 2
    fechar_y = botao_fechar_rect.y + (botao_fechar_rect.height - fechar_texto.get_height()) // 2
    screen.blit(fechar_texto, (fechar_x, fechar_y))
    
    return botao_fechar_rect

def menu_loop(screen) -> Escolha:
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)

    from core.i18n import t
    # Apenas 3 botões: OPCOES (esquerda), JOGAR (centro), SAIR (direita)
    itens = [t("menu.principal.opcoes"), t("menu.principal.jogar"), t("menu.principal.sair")]
    idx = 1  # Começar no JOGAR (centro)
    # Variável para rastrear se está navegando nos ícones superiores
    # None = nas opções do menu (idx 0-2), -1 = estatísticas, -2 = conquistas, -3 = missão diária
    icone_selecionado = None
    clock = pygame.time.Clock()

    base_y = int(ALTURA * 0.85)
    
    jogar_largura = 280
    jogar_altura = 70
    botao_largura = 180
    botao_altura = 50
    espacamento = 15
    
    jogar_y = base_y + (botao_altura - jogar_altura) // 2
    jogar_x = (LARGURA - jogar_largura) // 2
    
    # Posições: OPCOES (esquerda), JOGAR (centro), SAIR (direita)
    opcoes_x = jogar_x - espacamento - botao_largura
    opcoes_y = base_y
    sair_x = jogar_x + jogar_largura + espacamento
    sair_y = base_y
    
    hover_animation = [0.0] * len(itens)
    hover_speed = 8.0
    
    # Variável para controlar se a tela de achievements está aberta
    tela_achievements_aberta = False
    tela_estatisticas_aberta = False
    tela_desafios_aberta = False
    
    # Variável para animação do ícone de exclamação
    tempo_animacao_exclamacao = 0.0
    
    # Animação do cursor do controle
    animacao_cursor = 0.0
    velocidade_animacao_cursor = 3.0
    
    # Definir retângulos dos botões de ícones (antes do loop para evitar erro)
    botao_achievements_tamanho = 50
    botao_estatisticas_rect = pygame.Rect(10, 10, botao_achievements_tamanho, botao_achievements_tamanho)
    botao_achievements_rect = pygame.Rect(70, 10, botao_achievements_tamanho, botao_achievements_tamanho)
    botao_missao_rect = pygame.Rect(130, 10, botao_achievements_tamanho, botao_achievements_tamanho)
    
    # Carregar ícone de achievements uma vez (cache) - evita lag
    icon_achievements_cache = None
    icon_exclamacao_cache = None
    icon_estatisticas_cache = None
    icon_missao_cache = None  # Cache para ícone de missão diária
    from config import DIR_ICONS
    caminho_icon_achievements = os.path.join(DIR_ICONS, "achievements.png")
    if os.path.exists(caminho_icon_achievements):
        try:
            icon_achievements_raw = pygame.image.load(caminho_icon_achievements).convert_alpha()
            # Redimensionar mantendo proporção para 50x50 pixels (tamanho do botão)
            largura_original, altura_original = icon_achievements_raw.get_size()
            if largura_original > 0 and altura_original > 0:
                proporcao = min(50 / largura_original, 50 / altura_original)
                nova_largura = int(largura_original * proporcao)
                nova_altura = int(altura_original * proporcao)
                icon_achievements_cache = pygame.transform.smoothscale(icon_achievements_raw, (nova_largura, nova_altura))
            else:
                icon_achievements_cache = pygame.transform.scale(icon_achievements_raw, (50, 50))
        except Exception as e:
            print(f"Erro ao carregar ícone de achievements: {e}")
    
    caminho_icon_estatisticas = os.path.join(DIR_ICONS, "estatistica.png")
    if os.path.exists(caminho_icon_estatisticas):
        try:
            icon_estatisticas_raw = pygame.image.load(caminho_icon_estatisticas).convert_alpha()
            largura_original, altura_original = icon_estatisticas_raw.get_size()
            if largura_original > 0 and altura_original > 0:
                proporcao = min(50 / largura_original, 50 / altura_original)
                nova_largura = int(largura_original * proporcao)
                nova_altura = int(altura_original * proporcao)
                icon_estatisticas_cache = pygame.transform.smoothscale(icon_estatisticas_raw, (nova_largura, nova_altura))
            else:
                icon_estatisticas_cache = pygame.transform.scale(icon_estatisticas_raw, (50, 50))
        except Exception as e:
            print(f"Erro ao carregar ícone de estatísticas: {e}")
    
    # Carregar ícones de missão diária (missao0.png, missao1.png, missao2.png, missao3.png)
    icon_missao_cache = {}  # Dicionário para armazenar os 4 ícones
    for i in range(4):
        caminho_icon_missao = os.path.join(DIR_ICONS, f"missao{i}.png")
        if os.path.exists(caminho_icon_missao):
            try:
                icon_missao_raw = pygame.image.load(caminho_icon_missao).convert_alpha()
                icon_missao_cache[i] = pygame.transform.scale(icon_missao_raw, (50, 50))
            except Exception as e:
                print(f"Erro ao carregar ícone de missão {i}: {e}")
    
    # Carregar ícone de exclamação para notificações
    caminho_exclamacao = os.path.join(DIR_ICONS, "Exclamacao.png")
    if os.path.exists(caminho_exclamacao):
        try:
            icon_exclamacao_raw = pygame.image.load(caminho_exclamacao).convert_alpha()
            largura_original, altura_original = icon_exclamacao_raw.get_size()
            # Usar tamanho adequado para notificação (mantendo proporção)
            altura_alvo = 24  # Tamanho maior para ficar mais visível
            escala = altura_alvo / altura_original
            largura_alvo = int(largura_original * escala)
            icon_exclamacao_cache = pygame.transform.smoothscale(icon_exclamacao_raw, (largura_alvo, altura_alvo))
        except Exception as e:
            print(f"Erro ao carregar ícone de exclamação: {e}")

    # Inicializar variável de notificação da oficina
    mostrar_notificacao_oficina = False
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        
        gerenciador_musica.verificar_fim_musica()
        popup_musica.atualizar(dt)
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        popup_musica.verificar_hover(mouse_x, mouse_y)
        
        for i in range(len(itens)):
            if i == 1:  # JOGAR (centro)
                rect = pygame.Rect(jogar_x, jogar_y, jogar_largura, jogar_altura)
            elif i == 0:  # OPCOES (esquerda)
                rect = pygame.Rect(opcoes_x, opcoes_y, botao_largura, botao_altura)
            else:  # SAIR (direita, i == 2)
                rect = pygame.Rect(sair_x, sair_y, botao_largura, botao_altura)
            
            is_hovering = rect.collidepoint(mouse_x, mouse_y)
            
            if is_hovering:
                hover_animation[i] = min(1.0, hover_animation[i] + hover_speed * dt)
            else:
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt)
        
        # Atualizar animação do cursor do controle
        animacao_cursor += dt * velocidade_animacao_cursor
        if animacao_cursor >= 1.0:
            animacao_cursor = 0.0
        
        # Processar navegação contínua quando botão está sendo mantido pressionado
        if gerenciador_gamepad.obter_numero_controles() > 0:
            from core.menu_controles import processar_navegacao_hold
            tempo_atual = pygame.time.get_ticks()
            resultado_hold = processar_navegacao_hold(joystick_id=0, tempo_atual=tempo_atual)
            if resultado_hold:
                acao = resultado_hold.get("acao")
                if acao == "cima" and resultado_hold.get("fonte") == "hold":
                    if icone_selecionado is None:
                        icone_selecionado = -1
                elif acao == "baixo" and resultado_hold.get("fonte") == "hold":
                    if icone_selecionado is not None:
                        icone_selecionado = None
                elif acao == "esquerda" and resultado_hold.get("fonte") == "hold":
                    if icone_selecionado is not None:
                        if icone_selecionado == -2:
                            icone_selecionado = -1
                        elif icone_selecionado == -3:
                            icone_selecionado = -2
                    else:
                        # Navegação entre opções do menu: 0=Opções (esquerda), 1=JOGAR (centro), 2=Sair (direita)
                        # Esquerda: circular para a esquerda (0→2, 1→0, 2→1)
                        if idx == 0:  # Opções → Sair
                            idx = 2
                        elif idx == 1:  # JOGAR → Opções
                            idx = 0
                        elif idx == 2:  # Sair → JOGAR
                            idx = 1
                elif acao == "direita" and resultado_hold.get("fonte") == "hold":
                    if icone_selecionado is not None:
                        if icone_selecionado == -1:
                            icone_selecionado = -2
                        elif icone_selecionado == -2:
                            icone_selecionado = -3
                    else:
                        # Navegação entre opções do menu: 0=Opções (esquerda), 1=JOGAR (centro), 2=Sair (direita)
                        # Direita: circular para a direita (0→1, 1→2, 2→0)
                        if idx == 0:  # Opções → JOGAR
                            idx = 1
                        elif idx == 1:  # JOGAR → Sair
                            idx = 2
                        elif idx == 2:  # Sair → Opções
                            idx = 0
        
        # Verificação contínua do D-pad REMOVIDA
        # O D-pad agora é processado apenas via eventos JOYBUTTONDOWN
        # Isso garante comportamento "por clique" - uma ação por pressionamento
        
        for ev in pygame.event.get():
            # Declarar todas as variáveis globais no início do loop de eventos
            global _achievements_scroll_offset, _achievements_scroll_dragging, _achievements_scroll_drag_start_y, _achievements_scroll_drag_start_offset
            global _estatisticas_scroll_offset, _estatisticas_scroll_dragging, _estatisticas_scroll_drag_start_y, _estatisticas_scroll_drag_start_offset
            
            # Processar eventos de controle nas telas abertas PRIMEIRO
            if tela_achievements_aberta and gerenciador_gamepad.obter_numero_controles() > 0:
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
                # Sempre resetar para True quando a tela está aberta (garantir que aparece ao reabrir)
                desenhar_tela_achievements._fechar_selecionado = True
                resultado_controle = processar_eventos_controle_menu(ev, 0, 0, joystick_id=0, tempo_atual=tempo_atual)
                if resultado_controle:
                    acao = resultado_controle.get("acao")
                    if acao == "cima":
                        # Scroll para cima
                        scroll_speed = 50.0
                        _achievements_scroll_offset -= scroll_speed
                        from core.achievements import gerenciador_achievements
                        achievements = gerenciador_achievements.obter_todos_achievements()
                        altura_total = len(achievements) * 70
                        area_scroll_altura = 400
                        scroll_max = max(0, altura_total - area_scroll_altura)
                        _achievements_scroll_offset = max(0, min(_achievements_scroll_offset, scroll_max))
                        continue
                    elif acao == "baixo":
                        # Scroll para baixo
                        scroll_speed = 50.0
                        _achievements_scroll_offset += scroll_speed
                        from core.achievements import gerenciador_achievements
                        achievements = gerenciador_achievements.obter_todos_achievements()
                        altura_total = len(achievements) * 70
                        area_scroll_altura = 400
                        scroll_max = max(0, altura_total - area_scroll_altura)
                        _achievements_scroll_offset = max(0, min(_achievements_scroll_offset, scroll_max))
                        continue
                    elif acao == "confirmar":
                        # Fechar tela se botão fechar está selecionado
                        if desenhar_tela_achievements._fechar_selecionado:
                            tela_achievements_aberta = False
                            from core.achievements import gerenciador_achievements
                            gerenciador_achievements.marcar_todos_como_visualizados()
                            _achievements_scroll_offset = 0.0
                            icone_selecionado = None
                            desenhar_tela_achievements._fechar_selecionado = False
                        continue
                    elif acao == "cancelar":
                        # Fechar tela
                        tela_achievements_aberta = False
                        from core.achievements import gerenciador_achievements
                        gerenciador_achievements.marcar_todos_como_visualizados()
                        _achievements_scroll_offset = 0.0
                        icone_selecionado = None
                        desenhar_tela_achievements._fechar_selecionado = False
                        continue
            elif tela_achievements_aberta and gerenciador_gamepad.obter_numero_controles() > 0:
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
                # Sempre resetar para True quando a tela está aberta (garantir que aparece ao reabrir)
                desenhar_tela_achievements._fechar_selecionado = True
                resultado_controle = processar_eventos_controle_menu(ev, 0, 0, joystick_id=0, tempo_atual=tempo_atual)
                if resultado_controle:
                    acao = resultado_controle.get("acao")
                    if acao == "cima":
                        # Scroll para cima
                        scroll_speed = 50.0
                        _achievements_scroll_offset -= scroll_speed
                        from core.achievements import gerenciador_achievements
                        achievements = gerenciador_achievements.obter_todos_achievements()
                        altura_total = len(achievements) * 70
                        area_scroll_altura = 400
                        scroll_max = max(0, altura_total - area_scroll_altura)
                        _achievements_scroll_offset = max(0, min(_achievements_scroll_offset, scroll_max))
                        continue
                    elif acao == "baixo":
                        # Scroll para baixo
                        scroll_speed = 50.0
                        _achievements_scroll_offset += scroll_speed
                        from core.achievements import gerenciador_achievements
                        achievements = gerenciador_achievements.obter_todos_achievements()
                        altura_total = len(achievements) * 70
                        area_scroll_altura = 400
                        scroll_max = max(0, altura_total - area_scroll_altura)
                        _achievements_scroll_offset = max(0, min(_achievements_scroll_offset, scroll_max))
                        continue
                    elif acao == "confirmar":
                        # Fechar tela se botão fechar está selecionado
                        if desenhar_tela_achievements._fechar_selecionado:
                            tela_achievements_aberta = False
                            from core.achievements import gerenciador_achievements
                            gerenciador_achievements.marcar_todos_como_visualizados()
                            _achievements_scroll_offset = 0.0
                            icone_selecionado = None
                            desenhar_tela_achievements._fechar_selecionado = False
                        continue
                    elif acao == "cancelar":
                        # Fechar tela
                        tela_achievements_aberta = False
                        from core.achievements import gerenciador_achievements
                        gerenciador_achievements.marcar_todos_como_visualizados()
                        _achievements_scroll_offset = 0.0
                        icone_selecionado = None
                        desenhar_tela_achievements._fechar_selecionado = False
                        continue
            elif tela_estatisticas_aberta and gerenciador_gamepad.obter_numero_controles() > 0:
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
                # Sempre resetar para True quando a tela está aberta (garantir que aparece ao reabrir)
                desenhar_tela_estatisticas._fechar_selecionado = True
                resultado_controle = processar_eventos_controle_menu(ev, 0, 0, joystick_id=0, tempo_atual=tempo_atual)
                if resultado_controle:
                    acao = resultado_controle.get("acao")
                    if acao == "cima":
                        # Scroll para cima
                        scroll_speed = 50.0
                        _estatisticas_scroll_offset -= scroll_speed
                        caixa_altura = 600
                        area_conteudo_altura = caixa_altura - 150
                        altura_total = 800  # Valor aproximado, será recalculado no desenho
                        scroll_max = max(0, altura_total - area_conteudo_altura)
                        _estatisticas_scroll_offset = max(0, min(_estatisticas_scroll_offset, scroll_max))
                        continue
                    elif acao == "baixo":
                        # Scroll para baixo
                        scroll_speed = 50.0
                        _estatisticas_scroll_offset += scroll_speed
                        caixa_altura = 600
                        area_conteudo_altura = caixa_altura - 150
                        altura_total = 800  # Valor aproximado, será recalculado no desenho
                        scroll_max = max(0, altura_total - area_conteudo_altura)
                        _estatisticas_scroll_offset = max(0, min(_estatisticas_scroll_offset, scroll_max))
                        continue
                    elif acao == "confirmar":
                        # Fechar tela se botão fechar está selecionado
                        if desenhar_tela_estatisticas._fechar_selecionado:
                            tela_estatisticas_aberta = False
                            _estatisticas_scroll_offset = 0.0
                            icone_selecionado = None
                            desenhar_tela_estatisticas._fechar_selecionado = False
                        continue
                    elif acao == "cancelar":
                        # Fechar tela
                        tela_estatisticas_aberta = False
                        _estatisticas_scroll_offset = 0.0
                        icone_selecionado = None
                        desenhar_tela_estatisticas._fechar_selecionado = False
                        continue
            elif tela_desafios_aberta and gerenciador_gamepad.obter_numero_controles() > 0:
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
                # Sempre resetar para True quando a tela está aberta (garantir que aparece ao reabrir)
                desenhar_tela_desafios._fechar_selecionado = True
                resultado_controle = processar_eventos_controle_menu(ev, 0, 0, joystick_id=0, tempo_atual=tempo_atual)
                if resultado_controle:
                    acao = resultado_controle.get("acao")
                    if acao == "confirmar":
                        # Fechar tela se botão fechar está selecionado
                        if desenhar_tela_desafios._fechar_selecionado:
                            tela_desafios_aberta = False
                            icone_selecionado = None
                            desenhar_tela_desafios._fechar_selecionado = False
                        continue
                    elif acao == "cancelar":
                        # Fechar tela
                        tela_desafios_aberta = False
                        icone_selecionado = None
                        desenhar_tela_desafios._fechar_selecionado = False
                        continue
            
            # Processar eventos de controle ANTES de outros eventos (para o menu principal)
            if gerenciador_gamepad.obter_numero_controles() > 0:
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
                resultado_controle = processar_eventos_controle_menu(ev, idx, len(itens), joystick_id=0, tempo_atual=tempo_atual)
                if resultado_controle:
                    acao = resultado_controle.get("acao")
                    # No menu principal, ignorar cima/baixo do analógico (só usar esquerda/direita)
                    # Ignorar cima/baixo do analógico, mas aceitar do D-pad
                    if acao == "cima" and resultado_controle.get("fonte") == "dpad":
                        # Se está nas opções do menu, ir para os ícones superiores
                        if icone_selecionado is None:
                            icone_selecionado = -1  # Começar no primeiro ícone (estatísticas)
                        # Se já está nos ícones, navegar entre eles (não fazer nada, já está no topo)
                    elif acao == "baixo" and resultado_controle.get("fonte") == "dpad":
                        # Se está nos ícones, voltar para as opções do menu
                        if icone_selecionado is not None:
                            icone_selecionado = None
                            # Manter o idx atual (ou voltar para o primeiro)
                        elif "opcao" in resultado_controle:
                            idx = resultado_controle["opcao"]
                    elif acao == "esquerda":
                        # Se está nos ícones, navegar entre eles
                        if icone_selecionado is not None:
                            if icone_selecionado == -1:  # Estatísticas (primeiro, não tem esquerda)
                                pass
                            elif icone_selecionado == -2:  # Conquistas -> Estatísticas
                                icone_selecionado = -1
                            elif icone_selecionado == -3:  # Missão Diária -> Conquistas
                                icone_selecionado = -2
                        else:
                            # Navegação entre opções do menu: 0=Opções (esquerda), 1=JOGAR (centro), 2=Sair (direita)
                            # Esquerda: circular para a esquerda (0→2, 1→0, 2→1)
                            if idx == 0:  # Opções → Sair
                                idx = 2
                            elif idx == 1:  # JOGAR → Opções
                                idx = 0
                            elif idx == 2:  # Sair → JOGAR
                                idx = 1
                    elif acao == "direita":
                        # Se está nos ícones, navegar entre eles
                        if icone_selecionado is not None:
                            if icone_selecionado == -1:  # Estatísticas -> Conquistas
                                icone_selecionado = -2
                            elif icone_selecionado == -2:  # Conquistas -> Missão Diária
                                icone_selecionado = -3
                            elif icone_selecionado == -3:  # Missão Diária (último, não tem direita)
                                pass
                        else:
                            # Navegação entre opções do menu: 0=Opções (esquerda), 1=JOGAR (centro), 2=Sair (direita)
                            # Direita: circular para a direita (0→1, 1→2, 2→0)
                            if idx == 0:  # Opções → JOGAR
                                idx = 1
                            elif idx == 1:  # JOGAR → Sair
                                idx = 2
                            elif idx == 2:  # Sair → Opções
                                idx = 0
                    elif acao == "confirmar":
                        # Se está nos ícones, abrir a tela correspondente
                        if icone_selecionado == -1:  # Estatísticas
                            tela_estatisticas_aberta = True
                            icone_selecionado = None  # Resetar seleção ao abrir tela
                        elif icone_selecionado == -2:  # Conquistas
                            tela_achievements_aberta = True
                            from core.achievements import gerenciador_achievements
                            gerenciador_achievements.marcar_todos_como_visualizados()
                            _achievements_scroll_offset = 0.0
                            icone_selecionado = None  # Resetar seleção ao abrir tela
                        elif icone_selecionado == -3:  # Missão Diária
                            tela_desafios_aberta = True
                            icone_selecionado = None  # Resetar seleção ao abrir tela
                        else:
                            # Se for SAIR (idx == 2), mostrar confirmação antes de sair
                            if idx == 2:
                                confirmado = mostrar_dialogo_confirmacao_fechar(screen, bg)
                                if confirmado:
                                    return Escolha.SAIR
                                # Se não confirmou, continuar no menu
                                continue
                            # OPCOES (idx == 0) e JOGAR (idx == 1) não têm bloqueios
                            return Escolha(idx)
                    elif acao == "cancelar":
                        # Se está nas telas de achievements, estatísticas ou desafios, fechar a tela
                        if tela_achievements_aberta:
                            tela_achievements_aberta = False
                            from core.achievements import gerenciador_achievements
                            gerenciador_achievements.marcar_todos_como_visualizados()
                            _achievements_scroll_offset = 0.0
                            icone_selecionado = None
                        elif tela_estatisticas_aberta:
                            tela_estatisticas_aberta = False
                            _estatisticas_scroll_offset = 0.0
                            icone_selecionado = None
                        elif tela_desafios_aberta:
                            tela_desafios_aberta = False
                            icone_selecionado = None
                        else:
                            # Se não está em nenhuma tela, mostrar confirmação antes de sair
                            confirmado = mostrar_dialogo_confirmacao_fechar(screen, bg)
                            if confirmado:
                                return Escolha.SAIR
                            # Se não confirmou, continuar no menu
                            continue
                    # Se processou evento de controle, pular processamento de teclado
                    continue
            
            if ev.type == pygame.QUIT:
                # Mostrar diálogo modal de confirmação antes de fechar
                confirmado = mostrar_dialogo_confirmacao_fechar(screen, bg)
                if confirmado:
                    return Escolha.SAIR
                # Se não confirmou, continuar no menu
                continue
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # Verificar clique no botão de achievements
                if not tela_achievements_aberta and not tela_estatisticas_aberta and not tela_desafios_aberta and botao_achievements_rect.collidepoint(mouse_x, mouse_y):
                    tela_achievements_aberta = True
                    from core.achievements import gerenciador_achievements
                    gerenciador_achievements.marcar_todos_como_visualizados()
                    _achievements_scroll_offset = 0.0
                elif not tela_achievements_aberta and not tela_estatisticas_aberta and not tela_desafios_aberta and botao_estatisticas_rect.collidepoint(mouse_x, mouse_y):
                    tela_estatisticas_aberta = True
                elif not tela_achievements_aberta and not tela_estatisticas_aberta and not tela_desafios_aberta and botao_missao_rect.collidepoint(mouse_x, mouse_y):
                    tela_desafios_aberta = True
                elif tela_achievements_aberta:
                    # Verificar clique no botão fechar da tela de achievements (padronizado)
                    fechar_rect = pygame.Rect((LARGURA - 800) // 2 + 800 - 120, (ALTURA - 600) // 2 + 20, 100, 40)
                    if fechar_rect.collidepoint(mouse_x, mouse_y):
                        tela_achievements_aberta = False
                        # Marcar todos os achievements como visualizados quando fechar a tela
                        from core.achievements import gerenciador_achievements
                        gerenciador_achievements.marcar_todos_como_visualizados()
                        _achievements_scroll_offset = 0.0
                        icone_selecionado = None  # Resetar seleção ao fechar tela
                    else:
                        # Verificar clique na barra de rolagem
                        caixa_x = (LARGURA - 800) // 2
                        caixa_y = (ALTURA - 600) // 2
                        area_scroll_y = caixa_y + 120
                        area_scroll_altura = 400  # caixa_altura (600) - 200 (título + progresso + botão fechar)
                        barra_largura = 12
                        barra_x = caixa_x + 800 - 30
                        barra_y = area_scroll_y
                        barra_altura = area_scroll_altura
                        
                        # Verificar se clicou na área da barra
                        if barra_x <= mouse_x <= barra_x + barra_largura and barra_y <= mouse_y <= barra_y + barra_altura:
                            _achievements_scroll_dragging = True
                            _achievements_scroll_drag_start_y = mouse_y
                            _achievements_scroll_drag_start_offset = _achievements_scroll_offset
                elif tela_estatisticas_aberta:
                    botao_fechar_estat = desenhar_tela_estatisticas(screen, dt, mouse_x, mouse_y)
                    if botao_fechar_estat.collidepoint(mouse_x, mouse_y):
                        tela_estatisticas_aberta = False
                        _estatisticas_scroll_offset = 0.0
                        icone_selecionado = None  # Resetar seleção ao fechar tela
                    else:
                        # Verificar clique na barra de rolagem
                        caixa_x = (LARGURA - 800) // 2
                        caixa_y = (ALTURA - 600) // 2
                        area_scroll_y = caixa_y + 80
                        area_scroll_altura = 600 - 150
                        barra_largura = 12
                        barra_x = caixa_x + 800 - 30
                        barra_y = area_scroll_y
                        barra_altura = area_scroll_altura
                        
                        # Verificar se clicou na área da barra
                        if barra_x <= mouse_x <= barra_x + barra_largura and barra_y <= mouse_y <= barra_y + barra_altura:
                            _estatisticas_scroll_dragging = True
                            _estatisticas_scroll_drag_start_y = mouse_y
                            _estatisticas_scroll_drag_start_offset = _estatisticas_scroll_offset
                elif tela_desafios_aberta:
                    botao_fechar_desafios = desenhar_tela_desafios(screen, dt)
                    if botao_fechar_desafios.collidepoint(mouse_x, mouse_y):
                        tela_desafios_aberta = False
                        icone_selecionado = None  # Resetar seleção ao fechar tela
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                if tela_achievements_aberta:
                    _achievements_scroll_dragging = False
                elif tela_estatisticas_aberta:
                    _estatisticas_scroll_dragging = False
            elif ev.type == pygame.MOUSEMOTION:
                if tela_achievements_aberta:
                    if _achievements_scroll_dragging:
                        caixa_x = (LARGURA - 800) // 2
                        caixa_y = (ALTURA - 600) // 2
                        area_scroll_y = caixa_y + 120
                        area_scroll_altura = 400  # caixa_altura (600) - 200 (título + progresso + botão fechar)
                        barra_altura = area_scroll_altura
                        
                        # Calcular novo offset baseado no movimento do mouse
                        delta_y = mouse_y - _achievements_scroll_drag_start_y
                        from core.achievements import gerenciador_achievements
                        achievements = gerenciador_achievements.obter_todos_achievements()
                        altura_total = len(achievements) * 70
                        scroll_max = max(0, altura_total - area_scroll_altura)
                        
                        if scroll_max > 0:
                            # Converter movimento do mouse em scroll
                            scroll_ratio = delta_y / barra_altura
                            new_offset = _achievements_scroll_drag_start_offset + (scroll_ratio * scroll_max)
                            _achievements_scroll_offset = max(0, min(new_offset, scroll_max))
                elif tela_estatisticas_aberta:
                    if _estatisticas_scroll_dragging:
                        caixa_x = (LARGURA - 800) // 2
                        caixa_y = (ALTURA - 600) // 2
                        area_scroll_y = caixa_y + 80
                        area_scroll_altura = 600 - 150
                        barra_altura = area_scroll_altura
                        
                        # Calcular novo offset baseado no movimento do mouse
                        delta_y = mouse_y - _estatisticas_scroll_drag_start_y
                        altura_total = 800  # Valor aproximado, será recalculado no desenho
                        scroll_max = max(0, altura_total - area_scroll_altura)
                        
                        if scroll_max > 0:
                            # Converter movimento do mouse em scroll
                            scroll_ratio = delta_y / barra_altura
                            new_offset = _estatisticas_scroll_drag_start_offset + (scroll_ratio * scroll_max)
                            _estatisticas_scroll_offset = max(0, min(new_offset, scroll_max))
            elif ev.type == pygame.MOUSEWHEEL:
                if tela_achievements_aberta:
                    # Scroll com roda do mouse
                    caixa_x = (LARGURA - 800) // 2
                    caixa_y = (ALTURA - 600) // 2
                    area_scroll_y = caixa_y + 120
                    area_scroll_altura = 400  # caixa_altura (600) - 200 (título + progresso + botão fechar)
                    
                    # Verificar se o mouse está sobre a área de achievements
                    if caixa_x <= mouse_x <= caixa_x + 800 and area_scroll_y <= mouse_y <= area_scroll_y + area_scroll_altura:
                        scroll_speed = 50.0  # Velocidade de scroll
                        _achievements_scroll_offset -= ev.y * scroll_speed
                        
                        # Limitar scroll
                        from core.achievements import gerenciador_achievements
                        achievements = gerenciador_achievements.obter_todos_achievements()
                        altura_total = len(achievements) * 70
                        scroll_max = max(0, altura_total - area_scroll_altura)
                        _achievements_scroll_offset = max(0, min(_achievements_scroll_offset, scroll_max))
                elif tela_estatisticas_aberta:
                    # Scroll com roda do mouse
                    caixa_x = (LARGURA - 800) // 2
                    caixa_y = (ALTURA - 600) // 2
                    area_scroll_y = caixa_y + 80
                    area_scroll_altura = 600 - 150
                    
                    # Verificar se o mouse está sobre a área de estatísticas
                    if caixa_x <= mouse_x <= caixa_x + 800 and area_scroll_y <= mouse_y <= area_scroll_y + area_scroll_altura:
                        scroll_speed = 50.0  # Velocidade de scroll
                        _estatisticas_scroll_offset -= ev.y * scroll_speed
                        
                        # Limitar scroll usando altura total calculada na função de desenho
                        scroll_max = max(0, _estatisticas_altura_total - area_scroll_altura)
                        _estatisticas_scroll_offset = max(0, min(_estatisticas_scroll_offset, scroll_max))
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    if tela_achievements_aberta:
                        tela_achievements_aberta = False
                        # Marcar todos os achievements como visualizados quando fechar a tela
                        from core.achievements import gerenciador_achievements
                        gerenciador_achievements.marcar_todos_como_visualizados()
                        # Resetar scroll quando fechar
                        _achievements_scroll_offset = 0.0
                        icone_selecionado = None  # Resetar seleção ao fechar tela
                        continue
                    elif tela_estatisticas_aberta:
                        tela_estatisticas_aberta = False
                        _estatisticas_scroll_offset = 0.0
                        icone_selecionado = None  # Resetar seleção ao fechar tela
                        continue
                    elif tela_desafios_aberta:
                        tela_desafios_aberta = False
                        icone_selecionado = None  # Resetar seleção ao fechar tela
                        continue
                # Não processar outras teclas se as telas estiverem abertas
                if tela_achievements_aberta or tela_estatisticas_aberta or tela_desafios_aberta:
                    continue
                
                if ev.key in (pygame.K_LEFT, pygame.K_a):
                    # Navegação: OPCOES (0) <- JOGAR (1) <- SAIR (2)
                    # Ordem visual: OPCOES (esquerda), JOGAR (centro), SAIR (direita)
                    navegacao_esquerda = {
                        0: None,  # OPCOES -> não tem esquerda (primeiro)
                        1: 0,     # JOGAR -> OPCOES
                        2: 1      # SAIR -> JOGAR
                    }
                    novo_idx = navegacao_esquerda.get(idx)
                    if novo_idx is not None:
                        idx = novo_idx
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    # Navegação: OPCOES (0) -> JOGAR (1) -> SAIR (2)
                    navegacao_direita = {
                        0: 1,     # OPCOES -> JOGAR
                        1: 2,     # JOGAR -> SAIR
                        2: None   # SAIR -> não tem direita (último)
                    }
                    novo_idx = navegacao_direita.get(idx)
                    if novo_idx is not None:
                        idx = novo_idx
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    # Se for SAIR (idx == 2), mostrar confirmação antes de sair
                    if idx == 2:
                        confirmado = mostrar_dialogo_confirmacao_fechar(screen, bg)
                        if confirmado:
                            return Escolha.SAIR
                        # Se não confirmou, continuar no menu
                        continue
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
                    if i == 1:  # JOGAR (centro)
                        rect = pygame.Rect(jogar_x, jogar_y, jogar_largura, jogar_altura)
                    elif i == 0:  # OPCOES (esquerda)
                        rect = pygame.Rect(opcoes_x, opcoes_y, botao_largura, botao_altura)
                    else:  # SAIR (direita, i == 2)
                        rect = pygame.Rect(sair_x, sair_y, botao_largura, botao_altura)
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
                        if i == 1:  # JOGAR (centro)
                            botao_rect = pygame.Rect(jogar_x, jogar_y, jogar_largura, jogar_altura)
                        elif i == 0:  # OPCOES (esquerda)
                            botao_rect = pygame.Rect(opcoes_x, opcoes_y, botao_largura, botao_altura)
                        else:  # SAIR (direita, i == 2)
                            botao_rect = pygame.Rect(sair_x, sair_y, botao_largura, botao_altura)
                        
                        # Verificar clique no botão
                        clique_no_botao = botao_rect.collidepoint(mouse_x, mouse_y)
                        
                        # Verificar clique no botão
                        if clique_no_botao:
                            # Se for SAIR (i == 2), mostrar confirmação antes de sair
                            if i == 2:
                                confirmado = mostrar_dialogo_confirmacao_fechar(screen, bg)
                                if confirmado:
                                    return Escolha.SAIR
                                # Se não confirmou, continuar no menu
                                continue
                            # OPCOES (i == 0) e JOGAR (i == 1) não têm bloqueios
                            return Escolha(i)

        # desenha
        screen.blit(bg, (0, 0))
        
        botao_estatisticas_hover = botao_estatisticas_rect.collidepoint(mouse_x, mouse_y)
        botao_achievements_hover = botao_achievements_rect.collidepoint(mouse_x, mouse_y)
        botao_missao_hover = botao_missao_rect.collidepoint(mouse_x, mouse_y)
        
        # Contar missões diárias concluídas e selecionar ícone apropriado
        from core.desafios import gerenciador_desafios
        # Recarregar desafios para garantir que está atualizado
        gerenciador_desafios.gerenciador_progresso.carregar()
        missoes_concluidas = gerenciador_desafios.contar_missoes_diarias_concluidas()
        # Garantir que o valor está entre 0 e 3
        missoes_concluidas = max(0, min(3, int(missoes_concluidas)))
        # Selecionar ícone - garantir que sempre encontre o ícone correto
        if missoes_concluidas in icon_missao_cache:
            icon_missao_atual = icon_missao_cache[missoes_concluidas]
        else:
            # Fallback: usar o primeiro ícone disponível ou None
            icon_missao_atual = icon_missao_cache.get(0, None) if icon_missao_cache else None
        
        # Desenhar apenas o ícone de achievements (sem caixa de contorno)
        if not tela_achievements_aberta:
            # Verificar se há achievements não visualizados
            from core.achievements import gerenciador_achievements
            tem_notificacao = gerenciador_achievements.tem_achievements_nao_visualizados()
            
            # Verificar se há dinheiro suficiente para notificação na oficina
            tem_dinheiro_suficiente = verificar_dinheiro_suficiente()
            
            # Rastrear transição de "sem dinheiro" para "com dinheiro"
            global _tinha_dinheiro_anterior
            
            # Se é a primeira vez, inicializar com False (assumindo que não tinha dinheiro antes)
            # Isso garante que se o jogador ganhar dinheiro, a transição será detectada
            if _tinha_dinheiro_anterior is None:
                _tinha_dinheiro_anterior = False
            
            # Verificar se houve transição de "sem dinheiro" para "com dinheiro"
            # Isso acontece quando: estado anterior era False (sem dinheiro) e estado atual é True (com dinheiro)
            transicao_sem_para_com = (not _tinha_dinheiro_anterior) and tem_dinheiro_suficiente
            
            # Mostrar notificação apenas se houver transição de "sem dinheiro" para "com dinheiro"
            mostrar_notificacao_oficina = transicao_sem_para_com
            
            # Atualizar estado anterior:
            # - Se não tem dinheiro agora, sempre atualizar para False (para detectar transição futura)
            # - Se tem dinheiro agora e houve transição, manter False para manter a notificação visível
            # - Se tem dinheiro agora e não houve transição (já tinha antes), atualizar para True
            if not tem_dinheiro_suficiente:
                _tinha_dinheiro_anterior = False
            elif transicao_sem_para_com:
                # Se houve transição, manter False para manter a notificação visível
                # A notificação será "consumida" quando o jogador entrar na oficina
                pass  # Manter _tinha_dinheiro_anterior como False
            else:
                # Se não houve transição (já tinha dinheiro antes), atualizar o estado
                _tinha_dinheiro_anterior = True
            
            # Atualizar animação do ícone de exclamação (achievements ou oficina)
            if tem_notificacao or mostrar_notificacao_oficina:
                tempo_animacao_exclamacao += dt
            
            if icon_achievements_cache is not None:
                # Aplicar leve transparência no hover para feedback visual
                if botao_achievements_hover:
                    icon_temp = icon_achievements_cache.copy()
                    icon_temp.set_alpha(200)
                    screen.blit(icon_temp, botao_achievements_rect.topleft)
                else:
                    screen.blit(icon_achievements_cache, botao_achievements_rect.topleft)
                
                # Desenhar ícone de exclamação se houver notificação (com animação)
                if tem_notificacao and icon_exclamacao_cache is not None:
                    # Animação de pulso (crescer e diminuir)
                    pulso = 1.0 + 0.15 * math.sin(tempo_animacao_exclamacao * 4.0)  # Pulsa 4 vezes por segundo
                    # Vibração horizontal sincronizada com o pulso (vibra para os lados conforme cresce/diminui)
                    vibracao_x = 1.0 * math.sin(tempo_animacao_exclamacao * 4.0)  # Mesma frequência do pulso
                    
                    # Calcular tamanho animado
                    icon_exclamacao_largura, icon_exclamacao_altura = icon_exclamacao_cache.get_size()
                    largura_animada = int(icon_exclamacao_largura * pulso)
                    altura_animada = int(icon_exclamacao_altura * pulso)
                    
                    # Redimensionar ícone com animação
                    icon_exclamacao_animado = pygame.transform.smoothscale(icon_exclamacao_cache, (largura_animada, altura_animada))
                    
                    # Posicionar no canto superior direito do botão (vibração apenas horizontal)
                    exclamacao_x = botao_achievements_rect.x + botao_achievements_tamanho - largura_animada - 2 + int(vibracao_x)
                    exclamacao_y = botao_achievements_rect.y + 2  # Sem vibração vertical
                    screen.blit(icon_exclamacao_animado, (exclamacao_x, exclamacao_y))
            # Removido: emoji de fallback (conforme solicitado pelo usuário)
            
            # Desenhar cursor do controle (caixa animada) para conquistas
            if gerenciador_gamepad.obter_numero_controles() > 0 and icone_selecionado == -2:
                tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                cursor_rect = pygame.Rect(
                    botao_achievements_rect.x - tamanho_cursor,
                    botao_achievements_rect.y - tamanho_cursor,
                    botao_achievements_rect.width + tamanho_cursor * 2,
                    botao_achievements_rect.height + tamanho_cursor * 2
                )
                pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
        
        # Desenhar botão de Estatísticas
        if not tela_estatisticas_aberta:
            if icon_estatisticas_cache is not None:
                icon_largura, icon_altura = icon_estatisticas_cache.get_size()
                icon_x = botao_estatisticas_rect.x + (botao_estatisticas_rect.width - icon_largura) // 2
                icon_y = botao_estatisticas_rect.y + (botao_estatisticas_rect.height - icon_altura) // 2
                if botao_estatisticas_hover:
                    icon_temp = icon_estatisticas_cache.copy()
                    icon_temp.set_alpha(220)
                    screen.blit(icon_temp, (icon_x, icon_y))
                else:
                    screen.blit(icon_estatisticas_cache, (icon_x, icon_y))
                
                # Desenhar cursor do controle (caixa animada) para estatísticas
                if gerenciador_gamepad.obter_numero_controles() > 0 and icone_selecionado == -1:
                    tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                    cursor_rect = pygame.Rect(
                        botao_estatisticas_rect.x - tamanho_cursor,
                        botao_estatisticas_rect.y - tamanho_cursor,
                        botao_estatisticas_rect.width + tamanho_cursor * 2,
                        botao_estatisticas_rect.height + tamanho_cursor * 2
                    )
                    pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
        
        # Desenhar botão de Missão Diária
        if not tela_desafios_aberta and icon_missao_atual is not None:
            if botao_missao_hover:
                icon_temp = icon_missao_atual.copy()
                icon_temp.set_alpha(200)
                screen.blit(icon_temp, botao_missao_rect.topleft)
            else:
                screen.blit(icon_missao_atual, botao_missao_rect.topleft)
            
            # Desenhar cursor do controle (caixa animada) para missão diária
            if gerenciador_gamepad.obter_numero_controles() > 0 and icone_selecionado == -3:
                tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                cursor_rect = pygame.Rect(
                    botao_missao_rect.x - tamanho_cursor,
                    botao_missao_rect.y - tamanho_cursor,
                    botao_missao_rect.width + tamanho_cursor * 2,
                    botao_missao_rect.height + tamanho_cursor * 2
                )
                pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)

        # Atualizar animação do cursor do controle
        animacao_cursor += dt * velocidade_animacao_cursor
        if animacao_cursor >= 1.0:
            animacao_cursor = 0.0
        
        # Renderizar todos os botões na mesma linha
        from core.progresso import gerenciador_progresso
        for i, txt in enumerate(itens):
            sel = (i == idx and icone_selecionado is None)  # Só selecionar se não estiver nos ícones
            hover_progress = hover_animation[i]  # Progresso da animação de hover (0.0 a 1.0)
            
            # Posição e tamanho do botão
            if i == 1:  # JOGAR (centro)
                x, y = jogar_x, jogar_y
                largura, altura = jogar_largura, jogar_altura
                fonte_tamanho = 24  # Fonte maior para JOGAR
                borda_espessura = 4  # Borda mais espessa para JOGAR
            elif i == 0:  # OPCOES (esquerda)
                x, y = opcoes_x, opcoes_y
                largura, altura = botao_largura, botao_altura
                fonte_tamanho = 16
                borda_espessura = 3
            else:  # SAIR (direita, i == 2)
                x, y = sair_x, sair_y
                largura, altura = botao_largura, botao_altura
                fonte_tamanho = 16
                borda_espessura = 3
            
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
            
            # Removido: notificação da oficina (botão removido)
            if False:  # Placeholder
                # Animação de pulso (crescer e diminuir)
                pulso = 1.0 + 0.15 * math.sin(tempo_animacao_exclamacao * 4.0)  # Pulsa 4 vezes por segundo
                # Vibração horizontal sincronizada com o pulso
                vibracao_x = 1.0 * math.sin(tempo_animacao_exclamacao * 4.0)  # Mesma frequência do pulso
                
                # Calcular tamanho animado
                icon_exclamacao_largura, icon_exclamacao_altura = icon_exclamacao_cache.get_size()
                largura_animada = int(icon_exclamacao_largura * pulso)
                altura_animada = int(icon_exclamacao_altura * pulso)
                
                # Redimensionar ícone com animação
                icon_exclamacao_animado = pygame.transform.smoothscale(icon_exclamacao_cache, (largura_animada, altura_animada))
                
                # Posicionar no canto superior direito do botão (vibração apenas horizontal) - subido um pouco
                exclamacao_x = x + largura - largura_animada - 5 + int(vibracao_x)
                exclamacao_y = y - 8  # Subido 8 pixels do topo do botão
                screen.blit(icon_exclamacao_animado, (exclamacao_x, exclamacao_y))
            
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

        # Desenhar tela de achievements, estatísticas ou desafios se estiverem abertas
        if tela_achievements_aberta:
            desenhar_tela_achievements(screen, dt)
        elif tela_estatisticas_aberta:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            desenhar_tela_estatisticas(screen, dt, mouse_x, mouse_y)
        elif tela_desafios_aberta:
            desenhar_tela_desafios(screen, dt)
        else:
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
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        popup_musica.verificar_hover(mouse_x, mouse_y)
        
        # Processar eventos de controle
        if gerenciador_gamepad.obter_numero_controles() > 0:
            from core.menu_controles import processar_eventos_controle_menu
            for ev in pygame.event.get(pygame.JOYHATMOTION):
                tempo_atual = pygame.time.get_ticks()
                resultado_controle = processar_eventos_controle_menu(ev, indice, len(mapas), joystick_id=0, tempo_atual=tempo_atual)
                if resultado_controle:
                    acao = resultado_controle.get("acao")
                    if acao == "cima" and "opcao" in resultado_controle:
                        indice = resultado_controle["opcao"]
                    elif acao == "baixo" and "opcao" in resultado_controle:
                        indice = resultado_controle["opcao"]
                    elif acao == "confirmar":
                        mapa_selecionado = mapas[indice]
                        main.principal(mapa_selecionado=mapa_selecionado)
                        return None
                    elif acao == "cancelar":
                        return None
        
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

def calcular_especificacoes_carro(carro_info, upgrades):
    """Calcula as especificações reais do carro baseadas nos upgrades e multiplicador_base"""
    from core.progresso import gerenciador_progresso
    
    multiplicador_base = carro_info.get('multiplicador_base', 1.0)
    tipo_tracao_str = carro_info.get('tipo_tracao', 'rear').lower()
    
    # Normalizar tipo de tração
    mapeamento_tracao = {
        "traseira": "rear",
        "frontal": "front",
        "integral": "awd",
        "rear": "rear",
        "front": "front",
        "awd": "awd"
    }
    tipo_tracao = mapeamento_tracao.get(tipo_tracao_str, "rear")
    
    # Obter níveis de upgrades
    nivel_motor = upgrades.get('motor', 0)
    nivel_filtro_ar = upgrades.get('filtro_ar', 0)
    nivel_ecu = upgrades.get('ecu', 0)
    nivel_transmissao = upgrades.get('transmissao', 0)
    nivel_rodas = upgrades.get('rodas', 0)
    nivel_suspensao = upgrades.get('suspensao', 0)
    
    # Verificar upgrades especiais do Slick
    slick_upgrades = getattr(gerenciador_progresso, 'slick_upgrades_comprados', [])
    tem_slick_motor = any('slick_motor' in uid for uid in slick_upgrades)
    tem_slick_filtro = any('slick_filtro_ar' in uid for uid in slick_upgrades)
    tem_slick_ecu = any('slick_ecu' in uid for uid in slick_upgrades)
    tem_slick_trans = any('slick_transmissao' in uid for uid in slick_upgrades)
    tem_slick_rodas = any('slick_rodas' in uid for uid in slick_upgrades)
    tem_slick_susp = any('slick_suspensao' in uid for uid in slick_upgrades)
    
    # Calcular valores base (simulando CarroFisica)
    # Velocidade máxima base: o multiplicador_base não escala linearmente a velocidade real
    # devido ao atrito e arrasto. Vamos usar uma escala muito mais conservadora.
    # Primeiro carro (multiplicador_base = 1.00): V_TOP = 400 px/s
    # Último carro (multiplicador_base = 3.89): V_TOP deve ser limitado
    # Escala muito reduzida: usar apenas 8% do aumento do multiplicador
    V_TOP_base = 400.0 * (1.0 + (multiplicador_base - 1.0) * 0.08)  # Escala muito reduzida
    # Aplicar upgrades de motor e transmissão (mesma lógica de aplicar_upgrades)
    # Motor aumenta V_TOP em +10% por nível (reduzido)
    v_top_motor = 1.0 + nivel_motor * 0.10
    if tem_slick_motor:
        v_top_motor *= 1.3  # +30% velocidade
    V_TOP = V_TOP_base * v_top_motor
    # Transmissão aumenta V_TOP em +6% por nível (reduzido, multiplicativo)
    v_top_trans = 1.0 + nivel_transmissao * 0.06
    if tem_slick_trans:
        v_top_trans *= 1.3  # +30% velocidade
    V_TOP *= v_top_trans
    
    # Força do motor base
    engine_force_base = 80000.0 * multiplicador_base
    # Aplicar upgrades
    mult_motor = 1.0 + (nivel_motor * 0.25)
    if tem_slick_motor:
        mult_motor *= 1.5  # +50% força
    mult_filtro = 1.0 + (nivel_filtro_ar * 0.12)
    if tem_slick_filtro:
        mult_filtro *= 1.4  # +40% força
    mult_ecu = 1.0 + (nivel_ecu * 0.10)
    if tem_slick_ecu:
        mult_ecu *= 1.35  # +35% aceleração
    mult_trans = 1.0 + (nivel_transmissao * 0.08)
    if tem_slick_trans:
        mult_trans *= 1.25  # +25% força
    engine_force = engine_force_base * mult_motor * mult_filtro * mult_ecu * mult_trans
    
    # Grip base
    Cf_base = (35000.0 if tipo_tracao != "rear" else 34000.0) * multiplicador_base
    mult_rodas = 1.0 + (nivel_rodas * 0.18)
    if tem_slick_rodas:
        mult_rodas *= 1.5  # +50% grip
    Cf = Cf_base * mult_rodas
    
    # Estabilidade base
    stability_k_base = 0.043
    mult_rodas_stab = 1.0 + (nivel_rodas * 0.10)
    if tem_slick_rodas:
        mult_rodas_stab *= 1.3  # +30% estabilidade
    mult_susp_stab = 1.0 + (nivel_suspensao * 0.12)
    if tem_slick_susp:
        mult_susp_stab *= 1.4  # +40% estabilidade
    stability_k = stability_k_base * mult_rodas_stab * mult_susp_stab
    
    # Frenagem base
    brake_force_base = 5500.0 * multiplicador_base
    # Frenagem não tem upgrade direto, mas melhora com estabilidade
    
    # Fator de eficiência base: varia com multiplicador_base
    # Último carro: eficiência reduzida para compensar V_TOP maior
    # Quanto maior o multiplicador_base, menor a eficiência para manter velocidades realistas
    eficiencia_base_primeiro = 0.14  # 14% para primeiro carro (~140 km/h)
    # Reduzir eficiência para carros com multiplicador_base maior
    eficiencia_base = eficiencia_base_primeiro - (multiplicador_base - 1.0) * 0.005  # Redução suave
    fator_eficiencia_base = max(0.12, eficiencia_base)  # Mínimo 12% base
    
    # Melhorias de upgrades aumentam a eficiência, mas de forma muito conservadora
    # para não ultrapassar 380 km/h no último carro
    # Motor: aumenta V_TOP e força (+0.4% por nível)
    # Filtro de ar: reduz arrasto diretamente (+0.3% por nível)
    # ECU: melhora resposta e aceleração (+0.2% por nível)
    # Transmissão: aumenta V_TOP e melhora eficiência (+0.4% por nível)
    bonus_motor = nivel_motor * 0.004  # +0.4% por nível (muito reduzido)
    bonus_filtro = nivel_filtro_ar * 0.003  # +0.3% por nível (muito reduzido)
    bonus_ecu = nivel_ecu * 0.002  # +0.2% por nível (muito reduzido)
    bonus_trans = nivel_transmissao * 0.004  # +0.4% por nível (muito reduzido)
    fator_eficiencia = fator_eficiencia_base + bonus_motor + bonus_filtro + bonus_ecu + bonus_trans
    # Limitar eficiência máxima para evitar valores absurdos
    # A eficiência máxima diminui com multiplicador_base para manter velocidades realistas
    # Primeiro carro: eficiência máx ~0.20 (20%)
    # Último carro: eficiência máx ~0.155 (15.5%) para não ultrapassar 380 km/h
    eficiencia_max_base = 0.20
    eficiencia_max = eficiencia_max_base - (multiplicador_base - 1.0) * 0.015  # Redução maior com multiplicador
    eficiencia_max = max(0.155, eficiencia_max)  # Mínimo 15.5%
    fator_eficiencia = min(eficiencia_max, fator_eficiencia)
    
    # Velocidade real = V_TOP * fator_eficiencia (considerando atrito)
    # V_TOP já foi aumentado pelos upgrades de motor e transmissão acima
    vel_max_pxps = V_TOP * fator_eficiencia
    
    # Converter para km/h (mesma fórmula do HUD: v_long * ARCADE_SPEED_MULT * PXPS_TO_KMH)
    ARCADE_SPEED_MULT = 2.5
    PXPS_TO_KMH = 0.26  # Ajustado para que ~500 px/s = ~325 km/h
    vel_max_kmh = vel_max_pxps * ARCADE_SPEED_MULT * PXPS_TO_KMH
    
    # Aplicar mesmo multiplicador do velocímetro (5.0x) para exibição nas especificações
    vel_max_kmh = vel_max_kmh * 5.0
    
    # LIMITE HARD: garantir que nenhum carro ultrapasse 500 km/h (ajustado para o multiplicador)
    vel_max_kmh = min(500.0, vel_max_kmh)
    vel_max = int(vel_max_kmh)
    
    # Aceleração: baseada na força do motor (0-100)
    acel_base = {"front": 80, "rear": 90, "awd": 95}.get(tipo_tracao, 85)
    acel_mult = (engine_force / (80000.0 * multiplicador_base)) - 1.0  # Multiplicador extra
    acel_valor = min(100, int(acel_base + (acel_mult * 50)))  # Aumenta até 50 pontos
    
    # Dirigibilidade: baseada no grip e tipo de tração
    dir_base = {"front": 85, "rear": 70, "awd": 95}.get(tipo_tracao, 80)
    dir_mult = (Cf / ((35000.0 if tipo_tracao != "rear" else 34000.0) * multiplicador_base)) - 1.0
    dir_valor = min(100, int(dir_base + (dir_mult * 30)))  # Aumenta até 30 pontos
    
    # Frenagem: baseada no brake_force e estabilidade
    fren_base = {"front": 90, "rear": 75, "awd": 95}.get(tipo_tracao, 85)
    fren_mult = (stability_k / 0.043) - 1.0
    fren_valor = min(100, int(fren_base + (fren_mult * 20)))  # Aumenta até 20 pontos
    
    # Estabilidade: baseada em stability_k
    est_base = {"front": 85, "rear": 70, "awd": 95}.get(tipo_tracao, 80)
    est_mult = (stability_k / 0.043) - 1.0
    est_valor = min(100, int(est_base + (est_mult * 25)))  # Aumenta até 25 pontos
    
    return {
        'velocidade': vel_max,
        'aceleracao': acel_valor,
        'dirigibilidade': dir_valor,
        'frenagem': fren_valor,
        'estabilidade': est_valor
    }

def verificar_dinheiro_suficiente():
    """Verifica se há dinheiro suficiente para comprar algum carro ou upgrade"""
    from core.progresso import gerenciador_progresso
    from main import CARROS_DISPONIVEIS
    
    # Verificar se há dinheiro suficiente para comprar algum carro bloqueado
    for carro in CARROS_DISPONIVEIS:
        if not gerenciador_progresso.esta_desbloqueado(carro['prefixo_cor']):
            preco = carro.get('preco', 0)
            if gerenciador_progresso.tem_dinheiro(preco):
                return True
    
    # Verificar se há dinheiro suficiente para comprar algum upgrade
    for carro in CARROS_DISPONIVEIS:
        prefixo_cor = carro['prefixo_cor']
        if prefixo_cor == "Car1" or gerenciador_progresso.esta_desbloqueado(prefixo_cor):
            upgrades_tipos = ['motor', 'filtro_ar', 'ecu', 'transmissao', 'rodas', 'suspensao', 'nitro']
            nivel_maximo = gerenciador_progresso.obter_nivel_maximo_upgrade()
            for tipo_upgrade in upgrades_tipos:
                nivel_atual = gerenciador_progresso.obter_upgrade(prefixo_cor, tipo_upgrade)
                if nivel_atual < nivel_maximo:
                    preco = gerenciador_progresso.calcular_preco_upgrade(tipo_upgrade, nivel_atual)
                    if gerenciador_progresso.tem_dinheiro(preco):
                        return True
    
    return False

def verificar_upgrades_disponiveis(prefixo_cor):
    """Verifica se há upgrades disponíveis para um carro específico"""
    from core.progresso import gerenciador_progresso
    
    # Verificar se o carro está desbloqueado (Car1 sempre está)
    if prefixo_cor != "Car1" and not gerenciador_progresso.esta_desbloqueado(prefixo_cor):
        return False
    
    # Verificar se há algum upgrade disponível E se o jogador tem dinheiro suficiente
    upgrades_tipos = ['motor', 'filtro_ar', 'ecu', 'transmissao', 'rodas', 'suspensao', 'nitro']
    nivel_maximo = gerenciador_progresso.obter_nivel_maximo_upgrade()
    for tipo_upgrade in upgrades_tipos:
        nivel_atual = gerenciador_progresso.obter_upgrade(prefixo_cor, tipo_upgrade)
        if nivel_atual < nivel_maximo:  # Ainda há níveis disponíveis
            preco = gerenciador_progresso.calcular_preco_upgrade(tipo_upgrade, nivel_atual)
            if gerenciador_progresso.tem_dinheiro(preco):
                return True  # Encontrou pelo menos um upgrade disponível
    
    return False  # Não há upgrades disponíveis ou não tem dinheiro suficiente

def _mostrar_selecao_cores(screen, fundo_base):
    """Mostra tela de seleção de cores para o carro da campanha (estilo Slick/Pixel)"""
    from config import LARGURA, ALTURA, FPS, DIR_PROJETO, obter_caminho_sprite_dia_noite
    from core.progresso import gerenciador_progresso
    import os
    import json
    
    clock = pygame.time.Clock()
    
    # Carregar configuração de cores
    CAMINHO_CAMPANHA_CAR_CONFIG = os.path.join(DIR_PROJETO, "data", "campanha_car_config.json")
    cores_disponiveis = []
    try:
        if os.path.exists(CAMINHO_CAMPANHA_CAR_CONFIG):
            with open(CAMINHO_CAMPANHA_CAR_CONFIG, 'r', encoding='utf-8') as f:
                config = json.load(f)
                cores_disponiveis = config.get("cores_finais", [])
    except Exception as e:
        print(f"Erro ao carregar cores: {e}")
    
    # Se não carregou do JSON, usar cores padrão com preços
    if not cores_disponiveis:
        cores_disponiveis = [
            {"cor": "azul", "nome_sprite": "Car1_final_azul", "descricao": "Versão final azul", "preco": 5000},
            {"cor": "branco", "nome_sprite": "Car1_final_branco", "descricao": "Versão final branca", "preco": 5000},
            {"cor": "preto", "nome_sprite": "Car1_final_preto", "descricao": "Versão final preta", "preco": 5000},
            {"cor": "verde", "nome_sprite": "Car1_final_verde", "descricao": "Versão final verde", "preco": 5000}
        ]
    else:
        # Adicionar preços padrão se não existirem no JSON
        precos_padrao = {"azul": 5000, "branco": 5000, "preto": 5000, "verde": 5000}
        for cor_data in cores_disponiveis:
            if "preco" not in cor_data:
                cor_data["preco"] = precos_padrao.get(cor_data.get("cor", ""), 5000)
    
    opcao_selecionada = 0
    rodando = True
    cor_escolhida = None
    
    # Carregar background da oficina
    bg_oficina = None
    try:
        caminho_oficina = obter_caminho_sprite_dia_noite("oficina")
        if caminho_oficina and os.path.exists(caminho_oficina):
            bg_oficina = pygame.image.load(caminho_oficina).convert()
            bg_oficina = pygame.transform.scale(bg_oficina, (LARGURA, ALTURA))
    except Exception as e:
        print(f"Erro ao carregar background: {e}")
    
    # Carregar previews dos carros
    DIR_CAR_SELECTION_CAMPANHA = os.path.join(DIR_PROJETO, "assets", "images", "car_selection", "campanha")
    previews_carros = {}
    for cor_data in cores_disponiveis:
        sprite_path = os.path.join(DIR_CAR_SELECTION_CAMPANHA, f"{cor_data['nome_sprite']}.png")
        if os.path.exists(sprite_path):
            try:
                sprite = pygame.image.load(sprite_path).convert_alpha()
                # Redimensionar para preview pequeno
                preview_w = 150
                preview_h = 100
                sprite_w, sprite_h = sprite.get_size()
                escala = min(preview_w / sprite_w, preview_h / sprite_h) if sprite_w > 0 and sprite_h > 0 else 1.0
                nova_w = int(sprite_w * escala)
                nova_h = int(sprite_h * escala)
                preview = pygame.transform.scale(sprite, (nova_w, nova_h))
                previews_carros[cor_data['cor']] = preview
            except Exception as e:
                print(f"Erro ao carregar preview de {cor_data['cor']}: {e}")
    
    while rodando:
        dt = clock.tick(FPS) / 1000.0
        
        eventos = pygame.event.get()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Área do menu (centro da tela - padrão Pixel/Slick)
        menu_largura = 800
        menu_altura = 500
        menu_x = (LARGURA - menu_largura) // 2
        menu_y = (ALTURA - menu_altura) // 2
        
        y_inicio = menu_y + 100
        altura_item = 80
        espacamento = 10
        
        for i, cor_data in enumerate(cores_disponiveis):
            item_y = y_inicio + i * (altura_item + espacamento)
            item_rect = pygame.Rect(menu_x + 20, item_y, menu_largura - 40, altura_item)
            
            if item_rect.collidepoint(mouse_x, mouse_y):
                opcao_selecionada = i
        
        voltar_y = menu_y + menu_altura - 50
        voltar_rect = pygame.Rect(menu_x + menu_largura - 150, voltar_y, 130, 35)
        if voltar_rect.collidepoint(mouse_x, mouse_y):
            opcao_selecionada = len(cores_disponiveis)
        
        for ev in eventos:
            if ev.type == pygame.QUIT:
                return None
            
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # Verificar clique em cores
                for i, cor_data in enumerate(cores_disponiveis):
                    item_y = y_inicio + i * (altura_item + espacamento)
                    item_rect = pygame.Rect(menu_x + 20, item_y, menu_largura - 40, altura_item)
                    
                    if item_rect.collidepoint(mouse_x, mouse_y):
                        # Verificar se já tem essa cor aplicada
                        if gerenciador_progresso.carro_campanha_cor_final == cor_data['cor']:
                            # Já tem essa cor, não precisa comprar novamente
                            cor_escolhida = cor_data['cor']
                            rodando = False
                            break
                        
                        # Verificar dinheiro
                        preco = cor_data.get('preco', 5000)
                        if gerenciador_progresso.tem_dinheiro(preco):
                            # Remover dinheiro e aplicar cor
                            gerenciador_progresso.remover_dinheiro(preco)
                            gerenciador_progresso.salvar()
                            cor_escolhida = cor_data['cor']
                            rodando = False
                            break
                        else:
                            # Mostrar mensagem de dinheiro insuficiente
                            from core.musica import popup_musica
                            popup_musica.mostrar("Dinheiro insuficiente!", tipo="outra")
                        break
                
                # Verificar clique no botão "Voltar"
                if voltar_rect.collidepoint(mouse_x, mouse_y):
                    rodando = False
                    return None
            
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return None
                
                if ev.key in (pygame.K_UP, pygame.K_w):
                    if opcao_selecionada > 0:
                        opcao_selecionada -= 1
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    if opcao_selecionada < len(cores_disponiveis):
                        opcao_selecionada += 1
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if opcao_selecionada < len(cores_disponiveis):
                        cor_data = cores_disponiveis[opcao_selecionada]
                        # Verificar se já tem essa cor aplicada
                        if gerenciador_progresso.carro_campanha_cor_final == cor_data['cor']:
                            # Já tem essa cor, não precisa comprar novamente
                            cor_escolhida = cor_data['cor']
                            rodando = False
                        else:
                            # Verificar dinheiro
                            preco = cor_data.get('preco', 5000)
                            if gerenciador_progresso.tem_dinheiro(preco):
                                # Remover dinheiro e aplicar cor
                                gerenciador_progresso.remover_dinheiro(preco)
                                gerenciador_progresso.salvar()
                                cor_escolhida = cor_data['cor']
                                rodando = False
                            else:
                                # Mostrar mensagem de dinheiro insuficiente
                                from core.musica import popup_musica
                                popup_musica.mostrar("Dinheiro insuficiente!", tipo="outra")
                    elif opcao_selecionada == len(cores_disponiveis):
                        return None
        
        # Desenhar background
        if fundo_base:
            screen.blit(fundo_base, (0, 0))
        elif bg_oficina:
            screen.blit(bg_oficina, (0, 0))
        else:
            screen.fill((20, 20, 30))
        
        # Overlay escuro para melhorar legibilidade do menu
        overlay_escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay_escuro.fill((0, 0, 0, 150))
        screen.blit(overlay_escuro, (0, 0))
        
        # Fundo do menu
        overlay_menu = pygame.Surface((menu_largura, menu_altura), pygame.SRCALPHA)
        overlay_menu.fill((0, 0, 0, 240))
        screen.blit(overlay_menu, (menu_x, menu_y))
        
        # Borda amarela (tema loja/diálogo)
        pygame.draw.rect(screen, (255, 200, 0), (menu_x, menu_y, menu_largura, menu_altura), 3)
        
        # Título
        titulo = render_text("ESCOLHER COR DO CARRO", 28, (255, 200, 0), bold=True, pixel_style=True)
        screen.blit(titulo, (menu_x + (menu_largura - titulo.get_width()) // 2, menu_y + 20))
        
        # Dinheiro
        dinheiro_texto = render_text(f"Créditos: ${gerenciador_progresso.dinheiro:,}", 20, (255, 255, 100), bold=True, pixel_style=True)
        screen.blit(dinheiro_texto, (menu_x + 20, menu_y + 60))
        
        # Desenhar cores disponíveis
        for i, cor_data in enumerate(cores_disponiveis):
            item_y = y_inicio + i * (altura_item + espacamento)
            item_rect = pygame.Rect(menu_x + 20, item_y, menu_largura - 40, altura_item)
            
            hover = item_rect.collidepoint(mouse_x, mouse_y) or i == opcao_selecionada
            ja_aplicada = gerenciador_progresso.carro_campanha_cor_final == cor_data['cor']
            preco = cor_data.get('preco', 5000)
            tem_dinheiro = gerenciador_progresso.tem_dinheiro(preco) or ja_aplicada
            
            if ja_aplicada:
                cor_fundo = (20, 50, 20, 200) if hover else (10, 30, 10, 200)
                cor_borda = (0, 255, 0) if hover else (0, 200, 0)
            elif tem_dinheiro:
                cor_fundo = (50, 50, 20, 200) if hover else (30, 30, 10, 200)
                cor_borda = (255, 200, 0) if hover else (200, 150, 0)
            else:
                cor_fundo = (30, 20, 20, 200) if hover else (20, 10, 10, 200)
                cor_borda = (200, 100, 100) if hover else (150, 80, 80)
            
            # Fundo do item
            overlay_item = pygame.Surface((item_rect.width, item_rect.height), pygame.SRCALPHA)
            overlay_item.fill(cor_fundo)
            screen.blit(overlay_item, item_rect.topleft)
            
            # Borda do item
            pygame.draw.rect(screen, cor_borda, item_rect, 2)
            
            # Preview do carro (se disponível)
            if cor_data['cor'] in previews_carros:
                preview = previews_carros[cor_data['cor']]
                preview_x = item_rect.x + 10
                preview_y = item_rect.y + (item_rect.height - preview.get_height()) // 2
                screen.blit(preview, (preview_x, preview_y))
            
            # Nome da cor
            nome_cor = cor_data['cor'].upper()
            preco = cor_data.get('preco', 5000)
            
            # Verificar se já tem essa cor aplicada
            ja_aplicada = gerenciador_progresso.carro_campanha_cor_final == cor_data['cor']
            
            if ja_aplicada:
                nome_texto = render_text(f"{nome_cor} [APLICADA]", 20, (0, 255, 0), bold=True, pixel_style=True)
            else:
                nome_texto = render_text(nome_cor, 20, (255, 255, 255), bold=True, pixel_style=True)
            
            preview_w = previews_carros[cor_data['cor']].get_width() if cor_data['cor'] in previews_carros else 0
            nome_x = item_rect.x + preview_w + 30
            nome_y = item_rect.y + 15
            screen.blit(nome_texto, (nome_x, nome_y))
            
            # Preço (só mostrar se não estiver aplicada)
            if not ja_aplicada:
                preco_texto = render_text(f"${preco:,}", 18, (255, 255, 0), bold=True, pixel_style=True)
                preco_x = item_rect.right - preco_texto.get_width() - 10
                preco_y = item_rect.y + 15
                screen.blit(preco_texto, (preco_x, preco_y))
                
                # Verificar se tem dinheiro suficiente
                if not gerenciador_progresso.tem_dinheiro(preco):
                    # Mostrar texto "Dinheiro insuficiente" em vermelho
                    falta_texto = render_text("Dinheiro insuficiente", 14, (255, 100, 100), bold=False, pixel_style=True)
                    falta_x = item_rect.right - falta_texto.get_width() - 10
                    falta_y = item_rect.y + 40
                    screen.blit(falta_texto, (falta_x, falta_y))
        
        # Botão "Voltar"
        voltar_hover = voltar_rect.collidepoint(mouse_x, mouse_y) or opcao_selecionada == len(cores_disponiveis)
        cor_voltar = (100, 100, 100, 200) if voltar_hover else (80, 80, 80, 200)
        cor_borda_voltar = (150, 150, 150) if voltar_hover else (120, 120, 120)
        
        overlay_voltar = pygame.Surface((voltar_rect.width, voltar_rect.height), pygame.SRCALPHA)
        overlay_voltar.fill(cor_voltar)
        screen.blit(overlay_voltar, voltar_rect.topleft)
        pygame.draw.rect(screen, cor_borda_voltar, voltar_rect, 2)
        
        from core.i18n import t
        texto_voltar = render_text(t("menu.oficina.voltar"), 18, (255, 255, 255), bold=True, pixel_style=True)
        texto_voltar_x = voltar_rect.x + (voltar_rect.width - texto_voltar.get_width()) // 2
        texto_voltar_y = voltar_rect.y + (voltar_rect.height - texto_voltar.get_height()) // 2
        screen.blit(texto_voltar, (texto_voltar_x, texto_voltar_y))
        
        pygame.display.flip()
    
    return cor_escolhida

def _executar_transicao_melhoria(screen, fundo_base):
    """Executa transição de tela escura com som de oficina ao melhorar carro"""
    from config import LARGURA, ALTURA, DIR_PROJETO
    import time
    
    # Duração da transição (em segundos)
    duracao_escurecer = 0.5
    duracao_oficina = 1.5  # Tempo com tela preta e som de oficina
    duracao_clarear = 0.5
    
    clock = pygame.time.Clock()
    
    # Carregar som de oficina
    som_oficina = None
    try:
        if pygame.mixer.get_init():
            som_oficina_path = os.path.join(DIR_PROJETO, "assets", "sounds", "purchase", "caixa.mp3")
            if os.path.exists(som_oficina_path):
                som_oficina = pygame.mixer.Sound(som_oficina_path)
    except:
        pass
    
    # Fase 1: Escurecer
    tempo_inicio = time.time()
    while True:
        dt = clock.tick(60) / 1000.0
        tempo_decorrido = time.time() - tempo_inicio
        
        if tempo_decorrido < duracao_escurecer:
            # Escurecer gradualmente
            alpha = int(255 * (tempo_decorrido / duracao_escurecer))
            overlay = pygame.Surface((LARGURA, ALTURA))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(alpha)
            screen.blit(fundo_base, (0, 0))
            screen.blit(overlay, (0, 0))
        elif tempo_decorrido < duracao_escurecer + duracao_oficina:
            # Tela preta com som de oficina
            if som_oficina and tempo_decorrido - duracao_escurecer < 0.1:
                # Tocar som apenas uma vez no início desta fase
                som_oficina.play()
            overlay = pygame.Surface((LARGURA, ALTURA))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(255)
            screen.blit(overlay, (0, 0))
        elif tempo_decorrido < duracao_escurecer + duracao_oficina + duracao_clarear:
            # Clarear gradualmente
            tempo_clarear = tempo_decorrido - (duracao_escurecer + duracao_oficina)
            alpha = int(255 * (1.0 - tempo_clarear / duracao_clarear))
            overlay = pygame.Surface((LARGURA, ALTURA))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(alpha)
            screen.blit(fundo_base, (0, 0))
            screen.blit(overlay, (0, 0))
        else:
            break
        
        pygame.display.flip()
        
        # Processar eventos para não travar
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return

def selecionar_carros_loop(screen, modo_arcade=False, modo_jogo=None):
    from core.menu_controles import processar_eventos_controle_menu
    global _tinha_dinheiro_anterior
    # Importar gerenciador_progresso no início da função
    from core.progresso import gerenciador_progresso
    from core.crank import crank
    from core.barao import barao
    
    # Função auxiliar para converter obter_carro_atual para índice numérico
    def obter_carro_idx_seguro(jogador):
        """Converte o valor de obter_carro_atual para um índice numérico, tratando strings e prefixos"""
        from main import CARROS_DISPONIVEIS
        valor = gerenciador_progresso.obter_carro_atual(jogador)
        if valor is None:
            return None
        try:
            # Se for string que não é numérica (ex: 'Car1'), tentar encontrar o índice
            if isinstance(valor, str) and not valor.isdigit():
                # É um prefixo_cor, encontrar o índice correspondente
                return next((i for i, carro in enumerate(CARROS_DISPONIVEIS) if carro['prefixo_cor'] == valor), None)
            else:
                return int(valor)
        except (ValueError, TypeError):
            return None
    
    # Verificar se deve mostrar tutorial do Crank (primeira vez na oficina) - não no modo arcade
    if not modo_arcade:
        if not crank.tutorial_mostrado and not crank.ativo:
            crank.mostrar_tutorial()
        
        # Verificar se deve mostrar diálogo raro sobre compras do mercador alien (chance rara)
        if crank.tutorial_mostrado and not crank.ativo:
            crank.verificar_aparecer_dialogo_alien()
        
        # Verificar se Barão deve aparecer para oferecer empréstimo (sem dinheiro, carro quebrado)
        if not barao.ativo and not crank.ativo:
            barao.verificar_aparecer_oferta()
    
    # Ao entrar na oficina, se havia uma notificação ativa (transição detectada),
    # "consumir" a notificação atualizando o estado anterior para True
    # Isso faz a notificação desaparecer, mas permite que apareça novamente se houver nova transição
    if _tinha_dinheiro_anterior is not None:
        # Verificar o estado atual de dinheiro
        tem_dinheiro_atual = verificar_dinheiro_suficiente()
        # Se havia uma notificação (estado anterior era False) e agora tem dinheiro, consumir a notificação
        if not _tinha_dinheiro_anterior and tem_dinheiro_atual:
            _tinha_dinheiro_anterior = True  # Consumir a notificação
        # Se não tem dinheiro, atualizar o estado para False para detectar transição futura
        elif not tem_dinheiro_atual:
            _tinha_dinheiro_anterior = False
    
    from config import DIR_SPRITES, DIR_CAR_SELECTION, obter_caminho_sprite_dia_noite, LARGURA, ALTURA, DIR_UI
    import os
    # No modo arcade, sempre usar fundo de noite
    if modo_arcade:
        # Forçar fundo de noite no modo arcade
        caminho_oficina_noite = os.path.join(DIR_UI, "oficina_noite.png")
        if os.path.exists(caminho_oficina_noite):
            CAMINHO_OFICINA = caminho_oficina_noite
        else:
            # Fallback: usar função obter_caminho_sprite_dia_noite mas forçando noite
            # Temporariamente definir estado como noite
            from config import definir_estado_dia_noite, obter_estado_dia_noite
            estado_anterior = obter_estado_dia_noite()
            definir_estado_dia_noite("noite")
            CAMINHO_OFICINA = obter_caminho_sprite_dia_noite("oficina")
            # Restaurar estado anterior
            definir_estado_dia_noite(estado_anterior)
    else:
        # Usar sistema de ciclo dia/noite para carregar sprite correto
        CAMINHO_OFICINA = obter_caminho_sprite_dia_noite("oficina")
    
    if os.path.exists(CAMINHO_OFICINA):
        bg_raw = pygame.image.load(CAMINHO_OFICINA).convert_alpha()
    else:
        # Se nenhum arquivo existir, criar uma superfície preta como fallback
        bg_raw = pygame.Surface((LARGURA, ALTURA))
        bg_raw.fill((20, 20, 30))
    # Usar scale simples (como no editor) para mostrar a imagem completa sem cortar
    bg = pygame.transform.scale(bg_raw, (LARGURA, ALTURA))
    
    # Importar a lista de carros do main
    from main import CARROS_DISPONIVEIS
    
    # No modo campanha, filtrar para mostrar apenas Car1
    if not modo_arcade:
        CARROS_DISPONIVEIS_FILTRADOS = [carro for carro in CARROS_DISPONIVEIS if carro['prefixo_cor'] == 'Car1']
    else:
        CARROS_DISPONIVEIS_FILTRADOS = CARROS_DISPONIVEIS
    
    carro_p1_atual_salvo = gerenciador_progresso.obter_carro_atual(1)
    # Converter para int se necessário (pode vir como string do JSON)
    try:
        carro_p1_atual_salvo = int(carro_p1_atual_salvo) if carro_p1_atual_salvo is not None else None
    except (ValueError, TypeError):
        carro_p1_atual_salvo = None
    
    # Encontrar índice do Car1 na lista filtrada
    if not modo_arcade:
        carro_p1 = 0  # Sempre usar Car1 no modo campanha
    else:
        if carro_p1_atual_salvo is not None and 0 <= carro_p1_atual_salvo < len(CARROS_DISPONIVEIS):
            # Sempre usar o carro salvo, mesmo que não esteja desbloqueado (pode ter sido vendido)
            carro_p1 = carro_p1_atual_salvo
        else:
            carros_desbloqueados = [i for i, carro in enumerate(CARROS_DISPONIVEIS) if gerenciador_progresso.esta_desbloqueado(carro['prefixo_cor'])]
            if carros_desbloqueados:
                carro_p1 = carros_desbloqueados[0]
            else:
                carro_p1 = 0
    
    carro_p2_atual_salvo = gerenciador_progresso.obter_carro_atual(2)
    # Converter para int se necessário (pode vir como string do JSON)
    try:
        carro_p2_atual_salvo = int(carro_p2_atual_salvo) if carro_p2_atual_salvo is not None else None
    except (ValueError, TypeError):
        carro_p2_atual_salvo = None
    
    if carro_p2_atual_salvo is not None and 0 <= carro_p2_atual_salvo < len(CARROS_DISPONIVEIS):
        carro_p2 = carro_p2_atual_salvo
    else:
        carro_p2 = 1 if len(CARROS_DISPONIVEIS) > 1 else 0
    
    fase_selecao = 1
    # Determinar modo dois jogadores baseado no modo_jogo passado (se não for passado, usar False)
    from core.game_modes import ModoJogo
    if modo_jogo is None:
        modo_dois_jogadores = False
    else:
        modo_dois_jogadores = (modo_jogo == ModoJogo.DOIS_JOGADORES)
    carro_atual_p1_prefixo = CARROS_DISPONIVEIS_FILTRADOS[carro_p1]['prefixo_cor'] if not modo_arcade else CARROS_DISPONIVEIS[carro_p1]['prefixo_cor']
    carro_atual_p2_prefixo = CARROS_DISPONIVEIS[carro_p2]['prefixo_cor']
    # Verificar se os carros estão selecionados (com conversão segura)
    carro_selecionado_p1 = (obter_carro_idx_seguro(1) == carro_p1)
    carro_selecionado_p2 = (obter_carro_idx_seguro(2) == carro_p2)
    
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
    from config import DIR_ICONS
    caminho_cadeado = os.path.join(DIR_ICONS, "Locked.png")
    if os.path.exists(caminho_cadeado):
        icone_cadeado = pygame.image.load(caminho_cadeado).convert_alpha()
        # Redimensionar para tamanho adequado
        icone_cadeado = pygame.transform.scale(icone_cadeado, (80, 80))
    
    # Carregar ícone de exclamação para notificações
    icon_exclamacao_oficina = None
    caminho_exclamacao = os.path.join(DIR_ICONS, "Exclamacao.png")
    if os.path.exists(caminho_exclamacao):
        icon_exclamacao_raw = pygame.image.load(caminho_exclamacao).convert_alpha()
        # Redimensionar mantendo proporção - usar altura como referência
        icon_exclamacao_largura_original, icon_exclamacao_altura_original = icon_exclamacao_raw.get_size()
        altura_desejada = 20
        # Calcular largura mantendo proporção
        escala = altura_desejada / icon_exclamacao_altura_original
        largura_desejada = int(icon_exclamacao_largura_original * escala)
        icon_exclamacao_oficina = pygame.transform.smoothscale(icon_exclamacao_raw, (largura_desejada, altura_desejada))
    
    # Variável para animação do ícone de exclamação na oficina
    tempo_animacao_exclamacao_oficina = 0.0
    
    # Carregar configuração dos carros da campanha
    CAMINHO_CAMPANHA_CAR_CONFIG = os.path.join(DIR_PROJETO, "data", "campanha_car_config.json")
    config_campanha = None
    try:
        if os.path.exists(CAMINHO_CAMPANHA_CAR_CONFIG):
            with open(CAMINHO_CAMPANHA_CAR_CONFIG, 'r', encoding='utf-8') as f:
                config_campanha = json.load(f)
    except Exception as e:
        print(f"Erro ao carregar config de carros da campanha: {e}")
    
    # Função auxiliar para obter sprite do carro baseado no estágio da campanha
    def obter_sprite_carro_campanha(prefixo_cor):
        """Retorna o sprite do carro baseado no estágio da campanha"""
        if modo_arcade:
            # No modo arcade, usar sprite normal
            return None
        
        # Verificar se é o Car1 (carro da campanha)
        if prefixo_cor != "Car1":
            return None
        
        estagio = gerenciador_progresso.carro_campanha_estagio
        cor_final = gerenciador_progresso.carro_campanha_cor_final
        
        # Se tem cor final, usar sprite final com cor
        if cor_final:
            sprite_nome = f"Car1_final_{cor_final}"
        else:
            # Sequência de estágios: 0=inicial, 1=lataria, 2=pneus_drift, 3=bodykit
            estagios = [
                "Car1_campanha_inicial",
                "Car1_lataria",
                "Car1_pneus_drift",
                "Car1_bodykit"
            ]
            if 0 <= estagio < len(estagios):
                sprite_nome = estagios[estagio]
            else:
                sprite_nome = estagios[-1]  # Usar último estágio se estagio for maior
        
        # Tentar carregar da pasta campanha
        DIR_CAR_SELECTION_CAMPANHA = os.path.join(DIR_CAR_SELECTION, "campanha")
        sprite_path = os.path.join(DIR_CAR_SELECTION_CAMPANHA, f"{sprite_nome}.png")
        if os.path.exists(sprite_path):
            return sprite_path
        return None
    
    # Função auxiliar para obter configuração do estágio/cor do carro
    def obter_config_carro_campanha():
        """Retorna a configuração do carro baseado no estágio/cor atual"""
        if not config_campanha or modo_arcade:
            return None
        
        estagio = gerenciador_progresso.carro_campanha_estagio
        cor_final = gerenciador_progresso.carro_campanha_cor_final
        
        if cor_final:
            # Buscar configuração da cor final
            for cor_config in config_campanha.get("cores_finais", []):
                if cor_config.get("cor") == cor_final:
                    return cor_config
        else:
            # Buscar configuração do estágio
            for estagio_config in config_campanha.get("estagios", []):
                if estagio_config.get("estagio") == estagio:
                    return estagio_config
        
        return None
    
    # Carregar sprites dos carros para seleção (usando pasta car_selection)
    sprites_carros = {}
    sprites_carros_escurecidos = {}  # Cache de sprites escurecidos
    carros_para_carregar = CARROS_DISPONIVEIS_FILTRADOS if not modo_arcade else CARROS_DISPONIVEIS
    for carro in carros_para_carregar:
        try:
            # Verificar se é carro da campanha e obter sprite apropriado
            sprite_path_campanha = obter_sprite_carro_campanha(carro['prefixo_cor'])
            if sprite_path_campanha:
                sprite_path = sprite_path_campanha
            else:
                # Primeiro tenta carregar da pasta car_selection
                sprite_path = os.path.join(DIR_CAR_SELECTION, f"{carro['sprite_selecao']}.png")
                if not os.path.exists(sprite_path):
                    # Se não existir, usa o sprite normal
                    sprite_path = os.path.join(DIR_SPRITES, f"{carro['prefixo_cor']}.png")
            
            sprite = pygame.image.load(sprite_path).convert_alpha()
            
            # Obter configuração do carro da campanha se disponível
            config_carro = obter_config_carro_campanha() if not modo_arcade and carro['prefixo_cor'] == 'Car1' else None
            
            if config_carro:
                # Usar configuração do arquivo JSON
                tamanho_oficina = config_carro.get('tamanho_oficina', [600, 300])
                escala_config = config_carro.get('escala', 1.0)
                canvas_largura = int(tamanho_oficina[0] * escala_config)
                canvas_altura = int(tamanho_oficina[1] * escala_config)
                print(f"[CAMPANHA CAR] Usando config: tamanho={tamanho_oficina}, escala={escala_config}, y_offset={config_carro.get('y_offset', -10)}")
            else:
                # Usar tamanho padrão do carro
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
            # Ajustar y_offset usando configuração ou padrão
            if config_carro:
                y_offset = canvas_altura - nova_altura + config_carro.get('y_offset', -10)
            else:
                y_offset = canvas_altura - nova_altura - 10  # Posicionar no chão
            sprite.blit(sprite_redimensionado, (x_offset, y_offset))
            
            sprites_carros[carro['prefixo_cor']] = sprite
            
            # Pré-processar versão escurecida para cache
            sprite_escurecido = sprite.copy()
            overlay_preto = pygame.Surface(sprite_escurecido.get_size(), pygame.SRCALPHA)
            overlay_preto.fill((0, 0, 0, 240))  # Preto quase opaco
            sprite_escurecido.blit(overlay_preto, (0, 0), special_flags=pygame.BLEND_MULT)
            sprites_carros_escurecidos[carro['prefixo_cor']] = sprite_escurecido
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
    
    # Variáveis para cursor do controle (indicador visual)
    botao_selecionado_controle = None  # Qual botão está selecionado pelo controle
    animacao_cursor = 0.0  # Animação do cursor (0.0 a 1.0)
    velocidade_animacao_cursor = 3.0  # Velocidade da animação
    
    # Estado de pause
    oficina_pausada = False
    opcao_pausa_selecionada = 0
    
    # Estado de feedback de salvamento
    mostrar_mensagem_salvo = False
    tempo_mensagem_salvo = 0.0
    
    while True:
        dt = clock.tick(FPS) / 1000.0  # Converter para segundos
        
        atualizar_transicao(dt)
        tempo_animacao_exclamacao_oficina += dt
        popup_musica.atualizar(dt)
        
        # Atualizar animação do cursor do controle
        animacao_cursor += dt * velocidade_animacao_cursor
        if animacao_cursor >= 1.0:
            animacao_cursor = 0.0
        
        screen.blit(bg, (0, 0))
        
        if not hasattr(selecionar_carros_loop, '_overlay_cache'):
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 80))
            selecionar_carros_loop._overlay_cache = overlay
        screen.blit(selecionar_carros_loop._overlay_cache, (0, 0))
        
        fundo_sem_textos = screen.copy()
        
        # Calcular posições dos botões antes de processar eventos
        botao_usar_rect_p1 = None
        botao_comprar_rect_p1 = None
        botao_upgrade_rect_p1 = None
        botao_vender_rect_p1 = None
        botao_melhorar_rect_p1 = None  # Botão para melhorar carro no modo campanha
        botao_escolher_cor_rect_p1 = None  # Botão para escolher cor do carro no modo campanha
        botao_dois_jogadores_rect_p1 = None
        botao_concluido_rect_p1 = None
        botao_usar_rect_p2 = None
        botao_comprar_rect_p2 = None
        botao_upgrade_rect_p2 = None
        botao_vender_rect_p2 = None
        botao_concluido_rect_p2 = None
        tela_upgrades_aberta = False
        carro_upgrade_atual = None
        
        # Calcular posições dos botões para P1
        if fase_selecao == 1:
            # Durante a transição, usar o estado do carro anterior para manter os botões consistentes
            if transicao_ativa and carro_anterior is not None:
                carro_anterior_obj = CARROS_DISPONIVEIS[carro_anterior]
                esta_desbloqueado_p1 = gerenciador_progresso.esta_desbloqueado(carro_anterior_obj['prefixo_cor'])
                carro_atual_p1 = carro_anterior_obj
            else:
                carro_atual_p1 = CARROS_DISPONIVEIS_FILTRADOS[carro_p1] if not modo_arcade else CARROS_DISPONIVEIS[carro_p1]
                esta_desbloqueado_p1 = gerenciador_progresso.esta_desbloqueado(carro_atual_p1['prefixo_cor'])
            info_x_p1 = LARGURA - 300
            info_y_p1 = 150  # Subir a posição da caixa
            # Verificar se tem upgrades do Slick para ajustar altura do retângulo (só no modo campanha)
            if not modo_arcade:
                slick_upgrades_check = getattr(gerenciador_progresso, 'slick_upgrades_comprados', [])
                if slick_upgrades_check:
                    # Se tiver upgrades do Slick, aumentar altura moderadamente
                    info_altura_p1 = 420  # Altura aumentada moderadamente para acomodar upgrades do Slick
                else:
                    # Sem upgrades do Slick, usar altura padrão
                    info_altura_p1 = 360
            else:
                # Modo arcade: sempre usar altura padrão
                info_altura_p1 = 360
            botao_y_p1 = info_y_p1 + info_altura_p1 + 20
            botao_largura_p1 = 130
            botao_altura_p1 = 45
            espacamento_botoes_p1 = 10
            info_largura_p1 = 280
            botao_largura_p1 = 80  # Reduzir largura para caber botões
            # No modo campanha, adicionar botão MELHORAR se o carro não estiver no estágio máximo
            mostrar_botao_melhorar = (not modo_arcade and carro_atual_p1['prefixo_cor'] == 'Car1' and 
                                      gerenciador_progresso.carro_campanha_estagio < 3 and 
                                      gerenciador_progresso.carro_campanha_cor_final is None)
            # Botão ESCOLHER COR aparece quando estágio = 3 E cores foram desbloqueadas pelo Pixel
            cores_desbloqueadas = hasattr(gerenciador_progresso, 'pixel_cores_especiais_desbloqueadas') and \
                                  "todas" in getattr(gerenciador_progresso, 'pixel_cores_especiais_desbloqueadas', set())
            mostrar_botao_escolher_cor = (not modo_arcade and carro_atual_p1['prefixo_cor'] == 'Car1' and 
                                          gerenciador_progresso.carro_campanha_estagio >= 3 and cores_desbloqueadas)
            num_botoes = 4 if (mostrar_botao_melhorar or mostrar_botao_escolher_cor) else 3  # 4 botões se tiver MELHORAR ou ESCOLHER COR, senão 3
            # Posicionar botões mais para a direita na caixa de especificações
            largura_total_botoes = botao_largura_p1 * num_botoes + espacamento_botoes_p1 * (num_botoes - 1)
            offset_direita = 40  # Mover bastante para a direita
            botoes_x_inicial_p1 = info_x_p1 + (info_largura_p1 - largura_total_botoes) // 2 + offset_direita
            # Garantir que não saia da caixa pela direita
            if botoes_x_inicial_p1 + largura_total_botoes > info_x_p1 + info_largura_p1:
                botoes_x_inicial_p1 = info_x_p1 + info_largura_p1 - largura_total_botoes - 5
            
            if esta_desbloqueado_p1:
                botao_usar_rect_p1 = pygame.Rect(botoes_x_inicial_p1, botao_y_p1, botao_largura_p1, botao_altura_p1)
                botao_upgrade_rect_p1 = pygame.Rect(botoes_x_inicial_p1 + botao_largura_p1 + espacamento_botoes_p1, botao_y_p1, botao_largura_p1, botao_altura_p1)
                if mostrar_botao_melhorar:
                    botao_melhorar_rect_p1 = pygame.Rect(botoes_x_inicial_p1 + (botao_largura_p1 + espacamento_botoes_p1) * 2, botao_y_p1, botao_largura_p1, botao_altura_p1)
                    botao_vender_rect_p1 = pygame.Rect(botoes_x_inicial_p1 + (botao_largura_p1 + espacamento_botoes_p1) * 3, botao_y_p1, botao_largura_p1, botao_altura_p1)
                    botao_escolher_cor_rect_p1 = None
                elif mostrar_botao_escolher_cor:
                    botao_melhorar_rect_p1 = None
                    botao_escolher_cor_rect_p1 = pygame.Rect(botoes_x_inicial_p1 + (botao_largura_p1 + espacamento_botoes_p1) * 2, botao_y_p1, botao_largura_p1, botao_altura_p1)
                    botao_vender_rect_p1 = pygame.Rect(botoes_x_inicial_p1 + (botao_largura_p1 + espacamento_botoes_p1) * 3, botao_y_p1, botao_largura_p1, botao_altura_p1)
                else:
                    botao_melhorar_rect_p1 = None
                    botao_escolher_cor_rect_p1 = None
                    botao_vender_rect_p1 = pygame.Rect(botoes_x_inicial_p1 + (botao_largura_p1 + espacamento_botoes_p1) * 2, botao_y_p1, botao_largura_p1, botao_altura_p1)
                # Botão "2 jogadores" removido (não aparece mais ao lado de vender)
                botao_dois_jogadores_rect_p1 = None
                
                # Botão "Concluído" sempre aparece abaixo dos outros botões (esticado para centralizar)
                botao_concluido_y_p1 = botao_y_p1 + botao_altura_p1 + 15
                # Esticar o botão para ficar centralizado abaixo dos botões acima
                largura_total_botoes_acima = botao_largura_p1 * num_botoes + espacamento_botoes_p1 * (num_botoes - 1)
                botao_concluido_largura_p1 = largura_total_botoes_acima  # Mesma largura dos botões acima
                # Centralizar o botão em relação aos botões acima
                botao_concluido_x_p1 = botoes_x_inicial_p1  # Alinhar com o primeiro botão
                botao_concluido_rect_p1 = pygame.Rect(botao_concluido_x_p1, botao_concluido_y_p1, botao_concluido_largura_p1, botao_altura_p1)
            else:
                # Mesmo quando carro não é possuído, mostrar os botões (COMPRAR, UPGRADE, VENDER, e MELHORAR se aplicável)
                botao_comprar_rect_p1 = pygame.Rect(botoes_x_inicial_p1, botao_y_p1, botao_largura_p1, botao_altura_p1)
                botao_upgrade_rect_p1 = pygame.Rect(botoes_x_inicial_p1 + botao_largura_p1 + espacamento_botoes_p1, botao_y_p1, botao_largura_p1, botao_altura_p1)
                if mostrar_botao_melhorar:
                    botao_melhorar_rect_p1 = pygame.Rect(botoes_x_inicial_p1 + (botao_largura_p1 + espacamento_botoes_p1) * 2, botao_y_p1, botao_largura_p1, botao_altura_p1)
                    botao_vender_rect_p1 = pygame.Rect(botoes_x_inicial_p1 + (botao_largura_p1 + espacamento_botoes_p1) * 3, botao_y_p1, botao_largura_p1, botao_altura_p1)
                    botao_escolher_cor_rect_p1 = None
                elif mostrar_botao_escolher_cor:
                    botao_melhorar_rect_p1 = None
                    botao_escolher_cor_rect_p1 = pygame.Rect(botoes_x_inicial_p1 + (botao_largura_p1 + espacamento_botoes_p1) * 2, botao_y_p1, botao_largura_p1, botao_altura_p1)
                    botao_vender_rect_p1 = pygame.Rect(botoes_x_inicial_p1 + (botao_largura_p1 + espacamento_botoes_p1) * 3, botao_y_p1, botao_largura_p1, botao_altura_p1)
                else:
                    botao_melhorar_rect_p1 = None
                    botao_escolher_cor_rect_p1 = None
                    botao_vender_rect_p1 = pygame.Rect(botoes_x_inicial_p1 + (botao_largura_p1 + espacamento_botoes_p1) * 2, botao_y_p1, botao_largura_p1, botao_altura_p1)
                botao_dois_jogadores_rect_p1 = None
                # Botão "Concluído" sempre aparece, mesmo quando carro não é possuído (esticado para centralizar)
                botao_concluido_y_p1 = botao_y_p1 + botao_altura_p1 + 15
                # Esticar o botão para ficar centralizado abaixo dos botões acima
                largura_total_botoes_acima = botao_largura_p1 * num_botoes + espacamento_botoes_p1 * (num_botoes - 1)
                botao_concluido_largura_p1 = largura_total_botoes_acima  # Mesma largura dos botões acima
                # Centralizar o botão em relação aos botões acima
                botao_concluido_x_p1 = botoes_x_inicial_p1  # Alinhar com o primeiro botão
                botao_concluido_rect_p1 = pygame.Rect(botao_concluido_x_p1, botao_concluido_y_p1, botao_concluido_largura_p1, botao_altura_p1)
        
        # Calcular posições dos botões para P2
        if fase_selecao == 2:
            # Durante a transição, usar o estado do carro anterior para manter os botões consistentes
            if transicao_ativa and carro_anterior is not None:
                carro_anterior_obj = CARROS_DISPONIVEIS[carro_anterior]
                esta_desbloqueado_p2 = gerenciador_progresso.esta_desbloqueado(carro_anterior_obj['prefixo_cor'])
                carro_atual_p2 = carro_anterior_obj
            else:
                carro_atual_p2 = CARROS_DISPONIVEIS[carro_p2]
                esta_desbloqueado_p2 = gerenciador_progresso.esta_desbloqueado(carro_atual_p2['prefixo_cor'])
            info_x_p2 = LARGURA - 300
            info_y_p2 = 180
            info_altura_p2 = 360  # Altura aumentada para acomodar o texto de dano
            botao_y_p2 = info_y_p2 + info_altura_p2 + 20
            botao_largura_p2 = 85  # Reduzir largura para caber 3 botões
            botao_altura_p2 = 45
            espacamento_botoes_p2 = 10
            info_largura_p2 = 280
            num_botoes_p2 = 3  # Sempre 3 botões: COMPRAR/USAR, UPGRADE, VENDER
            # Mover botões mais para a esquerda
            largura_total_botoes_p2 = botao_largura_p2 * num_botoes_p2 + espacamento_botoes_p2 * (num_botoes_p2 - 1)
            offset_esquerda = -30  # Mover para a esquerda
            botoes_x_inicial_p2 = info_x_p2 + (info_largura_p2 - largura_total_botoes_p2) // 2 + offset_esquerda
            # Garantir que não saia da caixa pela esquerda
            if botoes_x_inicial_p2 < info_x_p2:
                botoes_x_inicial_p2 = info_x_p2 + 5
            
            if esta_desbloqueado_p2:
                botao_usar_rect_p2 = pygame.Rect(botoes_x_inicial_p2, botao_y_p2, botao_largura_p2, botao_altura_p2)
                botao_upgrade_rect_p2 = pygame.Rect(botoes_x_inicial_p2 + botao_largura_p2 + espacamento_botoes_p2, botao_y_p2, botao_largura_p2, botao_altura_p2)
                botao_vender_rect_p2 = pygame.Rect(botoes_x_inicial_p2 + (botao_largura_p2 + espacamento_botoes_p2) * 2, botao_y_p2, botao_largura_p2, botao_altura_p2)
                
                # Botão "Concluído" sempre aparece abaixo dos outros botões (esticado para centralizar)
                botao_concluido_y_p2 = botao_y_p2 + botao_altura_p2 + 15
                # Esticar o botão para ficar centralizado abaixo dos 3 botões acima
                largura_total_botoes_acima_p2 = botao_largura_p2 * 3 + espacamento_botoes_p2 * 2
                botao_concluido_largura_p2 = largura_total_botoes_acima_p2  # Mesma largura dos 3 botões acima
                # Centralizar o botão em relação aos 3 botões acima
                botao_concluido_x_p2 = botoes_x_inicial_p2  # Alinhar com o primeiro botão
                botao_concluido_rect_p2 = pygame.Rect(botao_concluido_x_p2, botao_concluido_y_p2, botao_concluido_largura_p2, botao_altura_p2)
            else:
                # Mesmo quando carro não é possuído, mostrar os 3 botões (COMPRAR, UPGRADE, VENDER)
                botao_comprar_rect_p2 = pygame.Rect(botoes_x_inicial_p2, botao_y_p2, botao_largura_p2, botao_altura_p2)
                botao_upgrade_rect_p2 = pygame.Rect(botoes_x_inicial_p2 + botao_largura_p2 + espacamento_botoes_p2, botao_y_p2, botao_largura_p2, botao_altura_p2)
                botao_vender_rect_p2 = pygame.Rect(botoes_x_inicial_p2 + (botao_largura_p2 + espacamento_botoes_p2) * 2, botao_y_p2, botao_largura_p2, botao_altura_p2)
                # Botão "Concluído" sempre aparece, mesmo quando carro não é possuído (esticado para centralizar)
                botao_concluido_y_p2 = botao_y_p2 + botao_altura_p2 + 15
                # Esticar o botão para ficar centralizado abaixo dos 3 botões acima
                largura_total_botoes_acima_p2 = botao_largura_p2 * 3 + espacamento_botoes_p2 * 2
                botao_concluido_largura_p2 = largura_total_botoes_acima_p2  # Mesma largura dos 3 botões acima
                # Centralizar o botão em relação aos 3 botões acima
                botao_concluido_x_p2 = botoes_x_inicial_p2  # Alinhar com o primeiro botão
                botao_concluido_rect_p2 = pygame.Rect(botao_concluido_x_p2, botao_concluido_y_p2, botao_concluido_largura_p2, botao_altura_p2)
        
        eventos = list(pygame.event.get())
        
        # Processar Crank primeiro (se ativo) - tem prioridade máxima
        if crank.ativo:
            resultado_crank = crank.processar_eventos(eventos)
            
            # Processar Barão se ativo
            from core.barao import barao
            if barao.ativo:
                barao.processar_eventos(eventos)
            if resultado_crank == "fechado":
                crank.fechar()
            # NÃO filtrar eventos aqui - o Crank processa os eventos dele, mas os outros eventos
            # devem continuar sendo processados normalmente
            # O Crank só intercepta eventos quando está ativo e processando, mas não bloqueia
            # eventos futuros que não foram processados por ele
        
        # Inicializar cursor do controle se houver controle conectado e ainda não foi inicializado
        if gerenciador_gamepad.obter_numero_controles() > 0 and botao_selecionado_controle is None:
            if fase_selecao == 1:
                carro_atual_temp = CARROS_DISPONIVEIS_FILTRADOS[carro_p1] if not modo_arcade else CARROS_DISPONIVEIS[carro_p1]
                esta_desbloqueado_temp = gerenciador_progresso.esta_desbloqueado(carro_atual_temp['prefixo_cor'])
            else:
                carro_atual_temp = CARROS_DISPONIVEIS[carro_p2]
                esta_desbloqueado_temp = gerenciador_progresso.esta_desbloqueado(carro_atual_temp['prefixo_cor'])
            if esta_desbloqueado_temp:
                botao_selecionado_controle = "usar"
            else:
                botao_selecionado_controle = "comprar"
        
        for ev in eventos:
            if ev.type == pygame.QUIT:
                # Mostrar diálogo modal de confirmação antes de fechar
                confirmado = mostrar_dialogo_confirmacao_fechar(screen, fundo_sem_textos if 'fundo_sem_textos' in locals() else bg)
                if confirmado:
                    return None, None
                # Se não confirmou, continuar na oficina
                continue
            
            # Processar eventos de controle ANTES de outros eventos
            # Verificar se há controles conectados e se o evento é de controle
            controle_processado = False  # Inicializar variável
            if gerenciador_gamepad.obter_numero_controles() > 0:
                # Verificar se é um evento de controle - processar TODOS os eventos de controle
                if ev.type in (pygame.JOYBUTTONDOWN, pygame.JOYHATMOTION, pygame.JOYAXISMOTION):
                    # Criar uma lista de opções para navegação (carros)
                    num_carros = len(CARROS_DISPONIVEIS_FILTRADOS) if not modo_arcade else len(CARROS_DISPONIVEIS)
                    carro_atual_idx = carro_p1 if fase_selecao == 1 else carro_p2
                
                # Definir tempo_atual para uso posterior (fora do bloco condicional para estar sempre disponível)
                tempo_atual = pygame.time.get_ticks()
                
                # Passar 0 como num_opcoes para evitar que esquerda/direita do D-pad sejam processadas como navegação de carros
                # Apenas L1/R1 devem trocar carros
                # Para navegação de carros, passar 0 (apenas L1/R1)
                # Para navegação de opções (usar, upgrade, vender, concluído), passar número de opções
                # Determinar opções disponíveis baseado no estado do carro
                if fase_selecao == 1:
                    carro_atual = CARROS_DISPONIVEIS_FILTRADOS[carro_p1] if not modo_arcade else CARROS_DISPONIVEIS[carro_p1]
                    esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                else:
                    carro_atual = CARROS_DISPONIVEIS[carro_p2]
                    esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                
                # Opções disponíveis: 
                # Linha superior: voltar (1 opção)
                # Linha inferior: usar/comprar, upgrade, vender, concluído (4 opções)
                # Setas: seta_esquerda, seta_direita (2 opções especiais)
                num_opcoes_botoes_superior = 1  # voltar (botão dois_jogadores removido)
                num_opcoes_botoes_inferior = 4  # usar/comprar, upgrade, vender, concluído
                
                # Verificar se há setas disponíveis
                num_carros_disponiveis = len(CARROS_DISPONIVEIS_FILTRADOS) if not modo_arcade else len(CARROS_DISPONIVEIS)
                tem_seta_esquerda = carro_p1 > 0 if fase_selecao == 1 else carro_p2 > 0
                tem_seta_direita = (carro_p1 < num_carros_disponiveis - 1) if fase_selecao == 1 else (carro_p2 < len(CARROS_DISPONIVEIS) - 1)
                
                # Determinar em qual linha estamos
                linha_atual = "inferior"  # ou "superior" ou "setas"
                opcao_botao_atual = 0
                # Inicializar botao_selecionado_controle se ainda não foi definido (primeira vez usando controle)
                if botao_selecionado_controle is None:
                    if esta_desbloqueado:
                        botao_selecionado_controle = "usar"
                    else:
                        botao_selecionado_controle = "comprar"
                if botao_selecionado_controle:
                    if botao_selecionado_controle == "voltar":
                        linha_atual = "superior"
                        opcao_botao_atual = 0
                    elif botao_selecionado_controle == "seta_esquerda":
                        linha_atual = "setas"
                        opcao_botao_atual = 0
                    elif botao_selecionado_controle == "seta_direita":
                        linha_atual = "setas"
                        opcao_botao_atual = 1
                    # Botão "dois_jogadores" removido
                    elif botao_selecionado_controle == "usar" or botao_selecionado_controle == "comprar":
                        linha_atual = "inferior"
                        opcao_botao_atual = 0
                    elif botao_selecionado_controle == "upgrade":
                        linha_atual = "inferior"
                        opcao_botao_atual = 1
                    elif botao_selecionado_controle == "vender":
                        linha_atual = "inferior"
                        opcao_botao_atual = 2
                    elif botao_selecionado_controle == "concluido":
                        linha_atual = "inferior"
                        opcao_botao_atual = 3
                
                # Processar eventos de controle - processar apenas UMA vez e verificar todas as ações
                resultado_controle = None
                num_opcoes_horizontal = num_opcoes_botoes_superior if linha_atual == "superior" else num_opcoes_botoes_inferior
                
                # Se estiver na linha de setas, usar 2 opções (seta_esquerda, seta_direita)
                if linha_atual == "setas":
                    num_opcoes_horizontal = 2
                
                # Processar o evento uma vez com num_opcoes_horizontal para capturar todas as ações possíveis
                resultado_controle_temp = processar_eventos_controle_menu(ev, opcao_botao_atual, num_opcoes_horizontal, joystick_id=0, tempo_atual=tempo_atual)
                
                if resultado_controle_temp:
                    acao_temp = resultado_controle_temp.get("acao")
                    # Verificar se é L1/R1 (carro_anterior/carro_proximo) - prioridade máxima
                    if acao_temp in ("carro_anterior", "carro_proximo"):
                        resultado_controle = resultado_controle_temp
                    # Verificar se é D-pad (cima/baixo/esquerda/direita)
                    elif acao_temp in ("cima", "baixo", "esquerda", "direita"):
                        resultado_controle = resultado_controle_temp
                    # Outras ações (confirmar, cancelar, etc.)
                    else:
                        resultado_controle = resultado_controle_temp
                    
                controle_processado = False
                if resultado_controle:
                    controle_processado = True
                    acao = resultado_controle.get("acao")
                    # Processar ações de carro (L1/R1) - funciona em ambos os modos
                    if acao == "carro_anterior" or acao == "carro_proximo":
                        # Processar mesmo durante transição (permitir mudança rápida)
                        if acao == "carro_anterior":
                            # Navegar para carro anterior (L1) - ir para esquerda (carro anterior)
                            if fase_selecao == 1:
                                # Usar num_carros correto baseado no modo
                                num_carros_disponiveis = len(CARROS_DISPONIVEIS_FILTRADOS) if not modo_arcade else len(CARROS_DISPONIVEIS)
                                # Permitir comportamento circular: se estiver no primeiro, vai para o último
                                iniciar_transicao(-1, carro_p1)
                                carro_p1 = (carro_p1 - 1) % num_carros_disponiveis
                                carro_selecionado_p1 = (obter_carro_idx_seguro(1) == carro_p1)
                                # Sempre inicializar o botão selecionado quando navegar entre carros
                                carro_atual = CARROS_DISPONIVEIS_FILTRADOS[carro_p1] if not modo_arcade else CARROS_DISPONIVEIS[carro_p1]
                                esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                botao_selecionado_controle = "usar" if esta_desbloqueado else "comprar"
                            else:
                                # Permitir comportamento circular: se estiver no primeiro, vai para o último
                                iniciar_transicao(-1, carro_p2)
                                carro_p2 = (carro_p2 - 1) % num_carros
                                carro_selecionado_p2 = (obter_carro_idx_seguro(2) == carro_p2)
                                # Sempre inicializar o botão selecionado quando navegar entre carros
                                carro_atual = CARROS_DISPONIVEIS[carro_p2]
                                esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                botao_selecionado_controle = "usar" if esta_desbloqueado else "comprar"
                        elif acao == "carro_proximo":
                            # Navegar para próximo carro (R1) - ir para direita (próximo carro)
                            if fase_selecao == 1:
                                num_carros_disponiveis = len(CARROS_DISPONIVEIS_FILTRADOS) if not modo_arcade else len(CARROS_DISPONIVEIS)
                                # Permitir comportamento circular: se estiver no último, vai para o primeiro
                                iniciar_transicao(1, carro_p1)
                                carro_p1 = (carro_p1 + 1) % num_carros_disponiveis
                                carro_selecionado_p1 = (obter_carro_idx_seguro(1) == carro_p1)
                                # Sempre inicializar o botão selecionado quando navegar entre carros
                                carro_atual = CARROS_DISPONIVEIS_FILTRADOS[carro_p1] if not modo_arcade else CARROS_DISPONIVEIS[carro_p1]
                                esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                botao_selecionado_controle = "usar" if esta_desbloqueado else "comprar"
                            else:
                                # Permitir comportamento circular: se estiver no último, vai para o primeiro
                                iniciar_transicao(1, carro_p2)
                                carro_p2 = (carro_p2 + 1) % num_carros
                                carro_selecionado_p2 = (obter_carro_idx_seguro(2) == carro_p2)
                                # Sempre inicializar o botão selecionado quando navegar entre carros
                                carro_atual = CARROS_DISPONIVEIS[carro_p2]
                                esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                botao_selecionado_controle = "usar" if esta_desbloqueado else "comprar"
                        continue
                    
                    if not transicao_ativa:
                        if acao == "cima" or acao == "baixo":
                            # Navegar entre botões (cima/baixo) - funciona com D-pad e analógico
                            if fase_selecao == 1:
                                carro_atual = CARROS_DISPONIVEIS[carro_p1]
                                esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                num_carros_disponiveis = len(CARROS_DISPONIVEIS_FILTRADOS) if not modo_arcade else len(CARROS_DISPONIVEIS)
                                tem_seta_esquerda = carro_p1 > 0
                                tem_seta_direita = carro_p1 < num_carros_disponiveis - 1
                                
                                # Se estiver nas setas, pode ir para baixo para os botões ou para cima para voltar
                                if botao_selecionado_controle in ("seta_esquerda", "seta_direita"):
                                    if acao == "baixo":
                                        # Ir para o primeiro botão inferior
                                        botao_selecionado_controle = "usar" if esta_desbloqueado else "comprar"
                                    elif acao == "cima":
                                        # Ir para o botão voltar (que fica acima das setas)
                                        botao_selecionado_controle = "voltar"
                                elif esta_desbloqueado:
                                    # Navegação vertical: qualquer botão (baixo) → concluído, concluído (baixo) → voltar
                                    # Se pressionar cima no primeiro botão e houver setas, ir para setas
                                    if botao_selecionado_controle is None:
                                        botao_selecionado_controle = "usar"
                                    elif botao_selecionado_controle == "usar":
                                        if acao == "cima":
                                            if tem_seta_esquerda or tem_seta_direita:
                                                # Ir para seta esquerda se disponível, senão direita
                                                botao_selecionado_controle = "seta_esquerda" if tem_seta_esquerda else "seta_direita"
                                            else:
                                                # Se não há setas, ir para voltar
                                                botao_selecionado_controle = "voltar"
                                        else:  # acao == "baixo"
                                            botao_selecionado_controle = "concluido"
                                    elif botao_selecionado_controle == "upgrade":
                                        if acao == "cima":
                                            if tem_seta_esquerda or tem_seta_direita:
                                                botao_selecionado_controle = "seta_esquerda" if tem_seta_esquerda else "seta_direita"
                                            else:
                                                # Se não há setas, ir para voltar
                                                botao_selecionado_controle = "voltar"
                                        else:  # acao == "baixo"
                                            botao_selecionado_controle = "concluido"
                                    elif botao_selecionado_controle == "vender":
                                        if acao == "cima":
                                            if tem_seta_esquerda or tem_seta_direita:
                                                botao_selecionado_controle = "seta_esquerda" if tem_seta_esquerda else "seta_direita"
                                            else:
                                                # Se não há setas, ir para voltar
                                                botao_selecionado_controle = "voltar"
                                        else:  # acao == "baixo"
                                            botao_selecionado_controle = "concluido"
                                    elif botao_selecionado_controle == "concluido":
                                        if acao == "baixo":
                                            botao_selecionado_controle = "voltar"
                                        else:  # acao == "cima"
                                            botao_selecionado_controle = "usar"
                                    elif botao_selecionado_controle == "voltar":
                                        if acao == "baixo":
                                            # Se houver setas, ir para elas, senão ir para concluido
                                            if tem_seta_esquerda or tem_seta_direita:
                                                botao_selecionado_controle = "seta_esquerda" if tem_seta_esquerda else "seta_direita"
                                            else:
                                                botao_selecionado_controle = "concluido"
                                        else:  # acao == "cima"
                                            # Voltar está no topo, então não fazer nada ou ir para concluido
                                            botao_selecionado_controle = "concluido"
                                    # Botão "dois_jogadores" removido
                                else:
                                    # Navegação vertical: qualquer botão (baixo) → concluído, concluído (baixo) → voltar
                                    # Se pressionar cima no primeiro botão e houver setas, ir para setas
                                    if botao_selecionado_controle is None:
                                        botao_selecionado_controle = "comprar"
                                    elif botao_selecionado_controle == "comprar":
                                        if acao == "cima":
                                            if tem_seta_esquerda or tem_seta_direita:
                                                botao_selecionado_controle = "seta_esquerda" if tem_seta_esquerda else "seta_direita"
                                            else:
                                                # Se não há setas, ir para voltar
                                                botao_selecionado_controle = "voltar"
                                        else:  # acao == "baixo"
                                            botao_selecionado_controle = "concluido"
                                    elif botao_selecionado_controle == "upgrade":
                                        if acao == "cima":
                                            if tem_seta_esquerda or tem_seta_direita:
                                                botao_selecionado_controle = "seta_esquerda" if tem_seta_esquerda else "seta_direita"
                                            else:
                                                # Se não há setas, ir para voltar
                                                botao_selecionado_controle = "voltar"
                                        else:  # acao == "baixo"
                                            botao_selecionado_controle = "concluido"
                                    elif botao_selecionado_controle == "vender":
                                        if acao == "cima":
                                            if tem_seta_esquerda or tem_seta_direita:
                                                botao_selecionado_controle = "seta_esquerda" if tem_seta_esquerda else "seta_direita"
                                            else:
                                                # Se não há setas, ir para voltar
                                                botao_selecionado_controle = "voltar"
                                        else:  # acao == "baixo"
                                            botao_selecionado_controle = "concluido"
                                    elif botao_selecionado_controle == "concluido":
                                        if acao == "baixo":
                                            botao_selecionado_controle = "voltar"
                                        else:  # acao == "cima"
                                            botao_selecionado_controle = "comprar"
                                    elif botao_selecionado_controle == "voltar":
                                        if acao == "baixo":
                                            # Se houver setas, ir para elas, senão ir para concluido
                                            if tem_seta_esquerda or tem_seta_direita:
                                                botao_selecionado_controle = "seta_esquerda" if tem_seta_esquerda else "seta_direita"
                                            else:
                                                botao_selecionado_controle = "concluido"
                                        else:  # acao == "cima"
                                            # Voltar está no topo, então não fazer nada ou ir para concluido
                                            botao_selecionado_controle = "concluido"
                                    # Botão "dois_jogadores" removido
                            else:
                                # Fase 2 (P2) - mesma lógica
                                carro_atual = CARROS_DISPONIVEIS[carro_p2]
                                esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                tem_seta_esquerda = carro_p2 > 0
                                tem_seta_direita = carro_p2 < len(CARROS_DISPONIVEIS) - 1
                                
                                # Se estiver nas setas, pode ir para baixo para os botões ou para cima para voltar
                                if botao_selecionado_controle in ("seta_esquerda", "seta_direita"):
                                    if acao == "baixo":
                                        # Ir para o primeiro botão inferior
                                        botao_selecionado_controle = "usar" if esta_desbloqueado else "comprar"
                                    elif acao == "cima":
                                        # Ir para o botão voltar (que fica acima das setas)
                                        botao_selecionado_controle = "voltar"
                                elif esta_desbloqueado:
                                    # Navegação vertical: qualquer botão (baixo) → concluído, concluído (baixo) → voltar
                                    # Se pressionar cima no primeiro botão e houver setas, ir para setas
                                    if botao_selecionado_controle is None:
                                        botao_selecionado_controle = "usar"
                                    elif botao_selecionado_controle == "usar":
                                        if acao == "cima":
                                            if tem_seta_esquerda or tem_seta_direita:
                                                botao_selecionado_controle = "seta_esquerda" if tem_seta_esquerda else "seta_direita"
                                            else:
                                                # Se não há setas, ir para voltar
                                                botao_selecionado_controle = "voltar"
                                        else:  # acao == "baixo"
                                            botao_selecionado_controle = "concluido"
                                    elif botao_selecionado_controle == "upgrade":
                                        if acao == "cima":
                                            if tem_seta_esquerda or tem_seta_direita:
                                                botao_selecionado_controle = "seta_esquerda" if tem_seta_esquerda else "seta_direita"
                                            else:
                                                # Se não há setas, ir para voltar
                                                botao_selecionado_controle = "voltar"
                                        else:  # acao == "baixo"
                                            botao_selecionado_controle = "concluido"
                                    elif botao_selecionado_controle == "vender":
                                        if acao == "cima":
                                            if tem_seta_esquerda or tem_seta_direita:
                                                botao_selecionado_controle = "seta_esquerda" if tem_seta_esquerda else "seta_direita"
                                            else:
                                                # Se não há setas, ir para voltar
                                                botao_selecionado_controle = "voltar"
                                        else:  # acao == "baixo"
                                            botao_selecionado_controle = "concluido"
                                    elif botao_selecionado_controle == "concluido":
                                        if acao == "baixo":
                                            botao_selecionado_controle = "voltar"
                                        else:  # acao == "cima"
                                            botao_selecionado_controle = "usar"
                                    elif botao_selecionado_controle == "voltar":
                                        if acao == "baixo":
                                            # Se houver setas, ir para elas, senão ir para concluido
                                            if tem_seta_esquerda or tem_seta_direita:
                                                botao_selecionado_controle = "seta_esquerda" if tem_seta_esquerda else "seta_direita"
                                            else:
                                                botao_selecionado_controle = "concluido"
                                        else:  # acao == "cima"
                                            # Voltar está no topo, então não fazer nada ou ir para concluido
                                            botao_selecionado_controle = "concluido"
                                    # Botão "dois_jogadores" removido
                                else:
                                    # Navegação vertical: qualquer botão (baixo) → concluído, concluído (baixo) → voltar
                                    # Se pressionar cima no primeiro botão e houver setas, ir para setas
                                    if botao_selecionado_controle is None:
                                        botao_selecionado_controle = "comprar"
                                    elif botao_selecionado_controle == "comprar":
                                        if acao == "cima":
                                            if tem_seta_esquerda or tem_seta_direita:
                                                botao_selecionado_controle = "seta_esquerda" if tem_seta_esquerda else "seta_direita"
                                            else:
                                                # Se não há setas, ir para voltar
                                                botao_selecionado_controle = "voltar"
                                        else:  # acao == "baixo"
                                            botao_selecionado_controle = "concluido"
                                    elif botao_selecionado_controle == "upgrade":
                                        if acao == "cima":
                                            if tem_seta_esquerda or tem_seta_direita:
                                                botao_selecionado_controle = "seta_esquerda" if tem_seta_esquerda else "seta_direita"
                                            else:
                                                # Se não há setas, ir para voltar
                                                botao_selecionado_controle = "voltar"
                                        else:  # acao == "baixo"
                                            botao_selecionado_controle = "concluido"
                                    elif botao_selecionado_controle == "vender":
                                        if acao == "cima":
                                            if tem_seta_esquerda or tem_seta_direita:
                                                botao_selecionado_controle = "seta_esquerda" if tem_seta_esquerda else "seta_direita"
                                            else:
                                                # Se não há setas, ir para voltar
                                                botao_selecionado_controle = "voltar"
                                        else:  # acao == "baixo"
                                            botao_selecionado_controle = "concluido"
                                    elif botao_selecionado_controle == "concluido":
                                        if acao == "baixo":
                                            botao_selecionado_controle = "voltar"
                                        else:  # acao == "cima"
                                            botao_selecionado_controle = "comprar"
                                    elif botao_selecionado_controle == "voltar":
                                        if acao == "baixo":
                                            # Se houver setas, ir para elas, senão ir para concluido
                                            if tem_seta_esquerda or tem_seta_direita:
                                                botao_selecionado_controle = "seta_esquerda" if tem_seta_esquerda else "seta_direita"
                                            else:
                                                botao_selecionado_controle = "concluido"
                                        else:  # acao == "cima"
                                            # Voltar está no topo, então não fazer nada ou ir para concluido
                                            botao_selecionado_controle = "concluido"
                                    # Botão "dois_jogadores" removido
                        elif acao == "esquerda" or acao == "direita":
                            # Navegação horizontal entre opções (funciona com D-pad e analógico)
                            # Determinar linha atual
                            linha_atual_temp = "inferior"
                            if botao_selecionado_controle == "voltar":
                                linha_atual_temp = "superior"
                            elif botao_selecionado_controle in ("seta_esquerda", "seta_direita"):
                                linha_atual_temp = "setas"
                            
                            if linha_atual_temp == "superior":
                                # Navegação horizontal na linha superior: apenas voltar (botão dois_jogadores removido)
                                opcao_idx = 0
                                opcoes_superior = ["voltar"]  # Botão dois_jogadores removido
                                botao_selecionado_controle = opcoes_superior[0]  # Apenas voltar
                            elif linha_atual_temp == "setas":
                                # Navegação horizontal entre setas: seta_esquerda ↔ seta_direita
                                if fase_selecao == 1:
                                    num_carros_disponiveis = len(CARROS_DISPONIVEIS_FILTRADOS) if not modo_arcade else len(CARROS_DISPONIVEIS)
                                    tem_seta_esquerda = carro_p1 > 0
                                    tem_seta_direita = carro_p1 < num_carros_disponiveis - 1
                                else:
                                    tem_seta_esquerda = carro_p2 > 0
                                    tem_seta_direita = carro_p2 < len(CARROS_DISPONIVEIS) - 1
                                
                                # Determinar índice atual
                                if botao_selecionado_controle == "seta_esquerda":
                                    seta_idx = 0
                                elif botao_selecionado_controle == "seta_direita":
                                    seta_idx = 1
                                else:
                                    seta_idx = 0
                                
                                # Navegar entre setas
                                if acao == "esquerda":
                                    seta_idx = (seta_idx - 1) % 2
                                else:  # direita
                                    seta_idx = (seta_idx + 1) % 2
                                
                                # Mapear índice de volta para seta (só se a seta estiver disponível)
                                if seta_idx == 0 and tem_seta_esquerda:
                                    botao_selecionado_controle = "seta_esquerda"
                                elif seta_idx == 1 and tem_seta_direita:
                                    botao_selecionado_controle = "seta_direita"
                                elif seta_idx == 0 and not tem_seta_esquerda and tem_seta_direita:
                                    botao_selecionado_controle = "seta_direita"
                                elif seta_idx == 1 and not tem_seta_direita and tem_seta_esquerda:
                                    botao_selecionado_controle = "seta_esquerda"
                                else:
                                    # Se nenhuma seta disponível, voltar para botões inferiores
                                    if fase_selecao == 1:
                                        carro_atual = CARROS_DISPONIVEIS[carro_p1]
                                        esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                    else:
                                        carro_atual = CARROS_DISPONIVEIS[carro_p2]
                                        esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                    botao_selecionado_controle = "usar" if esta_desbloqueado else "comprar"
                            else:
                                # Navegação horizontal na linha inferior: usar/comprar ↔ upgrade ↔ vender ↔ concluído
                                # Mas também pode navegar para as setas se pressionar esquerda no primeiro botão ou direita no último
                                if fase_selecao == 1:
                                    carro_atual = CARROS_DISPONIVEIS[carro_p1]
                                    esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                    num_carros_disponiveis = len(CARROS_DISPONIVEIS_FILTRADOS) if not modo_arcade else len(CARROS_DISPONIVEIS)
                                    tem_seta_esquerda = carro_p1 > 0
                                    tem_seta_direita = carro_p1 < num_carros_disponiveis - 1
                                else:
                                    carro_atual = CARROS_DISPONIVEIS[carro_p2]
                                    esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                    tem_seta_esquerda = carro_p2 > 0
                                    tem_seta_direita = carro_p2 < len(CARROS_DISPONIVEIS) - 1
                                
                                # Mapear índice para botão
                                if "opcao" in resultado_controle:
                                    opcao_idx = resultado_controle["opcao"]
                                else:
                                    # Calcular manualmente
                                    if botao_selecionado_controle:
                                        if botao_selecionado_controle == "usar" or botao_selecionado_controle == "comprar":
                                            opcao_idx = 0
                                        elif botao_selecionado_controle == "upgrade":
                                            opcao_idx = 1
                                        elif botao_selecionado_controle == "vender":
                                            opcao_idx = 2
                                        elif botao_selecionado_controle == "concluido":
                                            opcao_idx = 3
                                        else:
                                            opcao_idx = 0
                                    else:
                                        opcao_idx = 0
                                    
                                    # Verificar se pode navegar para setas
                                    if acao == "esquerda":
                                        if opcao_idx == 0 and tem_seta_esquerda:
                                            # Ir para seta esquerda
                                            botao_selecionado_controle = "seta_esquerda"
                                        else:
                                            opcao_idx = (opcao_idx - 1) % 4
                                    else:  # direita
                                        if opcao_idx == 3 and tem_seta_direita:
                                            # Ir para seta direita
                                            botao_selecionado_controle = "seta_direita"
                                        else:
                                            opcao_idx = (opcao_idx + 1) % 4
                                
                                # Se ainda não mudou para seta, mapear índice de volta para botão
                                if botao_selecionado_controle not in ("seta_esquerda", "seta_direita"):
                                    if esta_desbloqueado:
                                        opcoes = ["usar", "upgrade", "vender", "concluido"]
                                    else:
                                        opcoes = ["comprar", "upgrade", "vender", "concluido"]
                                    
                                    botao_selecionado_controle = opcoes[opcao_idx]
                        elif acao == "confirmar":
                            # Confirmar ação baseada no botão atual
                            if fase_selecao == 1:
                                # Verificar se está nas setas primeiro
                                if botao_selecionado_controle == "seta_esquerda":
                                    # Trocar para carro anterior
                                    if carro_p1 > 0 and not transicao_ativa:
                                        num_carros_disponiveis = len(CARROS_DISPONIVEIS_FILTRADOS) if not modo_arcade else len(CARROS_DISPONIVEIS)
                                        iniciar_transicao(-1, carro_p1)
                                        carro_p1 = (carro_p1 - 1) % num_carros_disponiveis
                                        carro_selecionado_p1 = (obter_carro_idx_seguro(1) == carro_p1)
                                        # Manter cursor na seta após trocar
                                        carro_atual = CARROS_DISPONIVEIS_FILTRADOS[carro_p1] if not modo_arcade else CARROS_DISPONIVEIS[carro_p1]
                                        esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                        # Se não há mais seta esquerda, ir para seta direita ou botão usar
                                        if carro_p1 == 0:
                                            num_carros_disponiveis = len(CARROS_DISPONIVEIS_FILTRADOS) if not modo_arcade else len(CARROS_DISPONIVEIS)
                                            if carro_p1 < num_carros_disponiveis - 1:
                                                botao_selecionado_controle = "seta_direita"
                                            else:
                                                botao_selecionado_controle = "usar" if esta_desbloqueado else "comprar"
                                elif botao_selecionado_controle == "seta_direita":
                                    # Trocar para próximo carro
                                    if not transicao_ativa:
                                        num_carros_disponiveis = len(CARROS_DISPONIVEIS_FILTRADOS) if not modo_arcade else len(CARROS_DISPONIVEIS)
                                        if carro_p1 < num_carros_disponiveis - 1:
                                            iniciar_transicao(1, carro_p1)
                                            carro_p1 = (carro_p1 + 1) % num_carros_disponiveis
                                            carro_selecionado_p1 = (obter_carro_idx_seguro(1) == carro_p1)
                                            # Manter cursor na seta após trocar
                                            carro_atual = CARROS_DISPONIVEIS_FILTRADOS[carro_p1] if not modo_arcade else CARROS_DISPONIVEIS[carro_p1]
                                            esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                            # Se não há mais seta direita, ir para seta esquerda ou botão usar
                                            if carro_p1 == num_carros_disponiveis - 1:
                                                if carro_p1 > 0:
                                                    botao_selecionado_controle = "seta_esquerda"
                                                else:
                                                    botao_selecionado_controle = "usar" if esta_desbloqueado else "comprar"
                                
                                carro_atual = CARROS_DISPONIVEIS[carro_p1]
                                esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                if esta_desbloqueado:
                                    # Verificar qual botão está selecionado
                                    if botao_selecionado_controle == "usar":
                                        if not carro_selecionado_p1:
                                            carro_selecionado_p1 = True
                                            gerenciador_progresso.definir_carro_atual(carro_p1=carro_p1)
                                            from core.i18n import t
                                            popup_musica.mostrar("Carro selecionado!", tipo="outra")
                                    elif botao_selecionado_controle == "upgrade":
                                        # Abrir tela de upgrades
                                        if botao_upgrade_rect_p1:
                                            pode_upgrade = (carro_atual['prefixo_cor'] == "Car1") or esta_desbloqueado
                                            if pode_upgrade and fundo_sem_textos:
                                                # Marcar que visitou a tela de upgrades para este carro
                                                gerenciador_progresso.marcar_upgrades_visitado(carro_atual['prefixo_cor'])
                                                if tela_upgrades(screen, carro_atual['prefixo_cor'], carro_atual['nome'], fundo_sem_textos):
                                                    pass  # Volta para seleção de carros
                                            elif not pode_upgrade:
                                                from core.i18n import t
                                                popup_musica.mostrar(t("mensagens.comprar_carro_primeiro"), tipo="outra")
                                    elif botao_selecionado_controle == "vender":
                                        # Vender carro - mostrar confirmação primeiro
                                        if botao_vender_rect_p1:
                                            pode_vender = gerenciador_progresso.contar_carros_desbloqueados() > 1
                                            if pode_vender:
                                                preco_venda = int(carro_atual.get('preco', 0) * 0.5)  # 50% do preço original
                                                # Mostrar diálogo de confirmação
                                                fundo_para_confirmacao = fundo_sem_textos if 'fundo_sem_textos' in locals() else bg
                                                confirmado = mostrar_dialogo_confirmacao_venda_carro(screen, fundo_para_confirmacao, carro_atual['nome'], preco_venda)
                                                if confirmado:
                                                    if gerenciador_progresso.vender_carro(carro_atual['prefixo_cor'], preco_venda):
                                                        from core.i18n import t
                                                        popup_musica.mostrar(t("mensagens.carro_vendido").format(carro_atual['nome']), tipo="outra")
                                                    else:
                                                        from core.i18n import t
                                                        popup_musica.mostrar(t("mensagens.erro_vender_carro"), tipo="outra")
                                            else:
                                                from core.i18n import t
                                                popup_musica.mostrar(t("mensagens.nao_pode_vender_unico_carro"), tipo="outra")
                                    elif botao_selecionado_controle == "concluido":
                                        # Confirmar seleção
                                        if botao_concluido_rect_p1:
                                            # Verificar se o carro está desbloqueado antes de permitir concluir
                                            if not esta_desbloqueado and carro_atual['prefixo_cor'] != "Car1":
                                                from core.i18n import t
                                                popup_musica.mostrar(t("mensagens.comprar_carro_primeiro"), tipo="outra")
                                            elif modo_dois_jogadores:
                                                if carro_selecionado_p1:
                                                    fase_selecao = 2
                                            else:
                                                if carro_selecionado_p1:
                                                    gerenciador_progresso.definir_carro_atual(carro_p1=carro_p1)
                                                    return carro_p1, carro_p2
                                    elif botao_selecionado_controle == "voltar":
                                        # Voltar para o menu ou seleção de mapas (no modo arcade)
                                        if modo_arcade:
                                            # No modo arcade, sempre voltar para seleção de mapas
                                            return None, None
                                        elif modo_dois_jogadores:
                                            if fase_selecao == 1 and carro_selecionado_p1:
                                                fase_selecao = 2  # Vai para P2
                                            elif fase_selecao == 2 and carro_selecionado_p2:
                                                gerenciador_progresso.definir_carro_atual(carro_p1=carro_p1, carro_p2=carro_p2)
                                                return carro_p1, carro_p2
                                            elif fase_selecao == 1:
                                                return None, None
                                            else:
                                                return None, None
                                        else:
                                            if carro_selecionado_p1:
                                                gerenciador_progresso.definir_carro_atual(carro_p1=carro_p1)
                                                return carro_p1, carro_p2
                                            else:
                                                return None, None
                                    # Botão "dois_jogadores" removido - o modo é definido antes de entrar na oficina
                                else:
                                    # Carro não desbloqueado
                                    if botao_selecionado_controle == "comprar":
                                        # Tentar comprar - mostrar confirmação primeiro
                                        if botao_comprar_rect_p1:
                                            preco = carro_atual.get('preco', 0)
                                            # Mostrar diálogo de confirmação
                                            fundo_para_confirmacao = fundo_sem_textos if 'fundo_sem_textos' in locals() else bg
                                            confirmado = mostrar_dialogo_confirmacao_compra_carro(screen, fundo_para_confirmacao, carro_atual['nome'], preco)
                                            if confirmado:
                                                if gerenciador_progresso.comprar_carro(carro_atual['prefixo_cor'], preco):
                                                    from core.i18n import t
                                                    popup_musica.mostrar(t("mensagens.carro_comprado").format(carro_atual['nome']), tipo="outra")
                                                else:
                                                    from core.i18n import t
                                                    popup_musica.mostrar(t("mensagens.dinheiro_insuficiente"), tipo="outra")
                                    elif botao_selecionado_controle == "upgrade":
                                        # Abrir tela de upgrades (mesmo que não desbloqueado, pode mostrar)
                                        if botao_upgrade_rect_p1:
                                            pode_upgrade = (carro_atual['prefixo_cor'] == "Car1") or esta_desbloqueado
                                            if pode_upgrade and fundo_sem_textos:
                                                # Marcar que visitou a tela de upgrades para este carro
                                                gerenciador_progresso.marcar_upgrades_visitado(carro_atual['prefixo_cor'])
                                                if tela_upgrades(screen, carro_atual['prefixo_cor'], carro_atual['nome'], fundo_sem_textos):
                                                    pass  # Volta para seleção de carros
                                            elif not pode_upgrade:
                                                from core.i18n import t
                                                popup_musica.mostrar(t("mensagens.comprar_carro_primeiro"), tipo="outra")
                                    elif botao_selecionado_controle == "vender":
                                        # Vender carro (não aplicável se não desbloqueado)
                                        pass
                                    elif botao_selecionado_controle == "concluido":
                                        # Confirmar seleção (não aplicável se não desbloqueado)
                                        pass
                            else:
                                # Fase 2 (P2)
                                # Verificar se está nas setas primeiro
                                if botao_selecionado_controle == "seta_esquerda":
                                    # Trocar para carro anterior
                                    if carro_p2 > 0 and not transicao_ativa:
                                        iniciar_transicao(-1, carro_p2)
                                        carro_p2 = (carro_p2 - 1) % num_carros
                                        carro_selecionado_p2 = (obter_carro_idx_seguro(2) == carro_p2)
                                        # Manter cursor na seta após trocar
                                        carro_atual = CARROS_DISPONIVEIS[carro_p2]
                                        esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                        # Se não há mais seta esquerda, ir para seta direita ou botão usar
                                        if carro_p2 == 0:
                                            if carro_p2 < len(CARROS_DISPONIVEIS) - 1:
                                                botao_selecionado_controle = "seta_direita"
                                            else:
                                                botao_selecionado_controle = "usar" if esta_desbloqueado else "comprar"
                                elif botao_selecionado_controle == "seta_direita":
                                    # Trocar para próximo carro
                                    if not transicao_ativa:
                                        if carro_p2 < len(CARROS_DISPONIVEIS) - 1:
                                            iniciar_transicao(1, carro_p2)
                                            carro_p2 = (carro_p2 + 1) % num_carros
                                            carro_selecionado_p2 = (obter_carro_idx_seguro(2) == carro_p2)
                                            # Manter cursor na seta após trocar
                                            carro_atual = CARROS_DISPONIVEIS[carro_p2]
                                            esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                            # Se não há mais seta direita, ir para seta esquerda ou botão usar
                                            if carro_p2 == len(CARROS_DISPONIVEIS) - 1:
                                                if carro_p2 > 0:
                                                    botao_selecionado_controle = "seta_esquerda"
                                                else:
                                                    botao_selecionado_controle = "usar" if esta_desbloqueado else "comprar"
                                
                                carro_atual = CARROS_DISPONIVEIS[carro_p2]
                                esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                if esta_desbloqueado:
                                    # Verificar qual botão está selecionado
                                    if botao_selecionado_controle == "usar":
                                        if not carro_selecionado_p2:
                                            carro_selecionado_p2 = True
                                            from core.i18n import t
                                            popup_musica.mostrar("Carro selecionado!", tipo="outra")
                                    elif botao_selecionado_controle == "upgrade":
                                        # Abrir tela de upgrades
                                        if botao_upgrade_rect_p2:
                                            # Marcar que visitou a tela de upgrades para este carro
                                            gerenciador_progresso.marcar_upgrades_visitado(carro_atual['prefixo_cor'])
                                            tela_upgrades_aberta = True
                                            carro_upgrade_atual = carro_p2
                                    elif botao_selecionado_controle == "vender":
                                        # Vender carro - mostrar confirmação primeiro
                                        if botao_vender_rect_p2:
                                            pode_vender = gerenciador_progresso.contar_carros_desbloqueados() > 1
                                            if pode_vender:
                                                preco_venda = int(carro_atual.get('preco', 0) * 0.5)  # 50% do preço original
                                                # Mostrar diálogo de confirmação
                                                fundo_para_confirmacao = fundo_sem_textos if 'fundo_sem_textos' in locals() else bg
                                                confirmado = mostrar_dialogo_confirmacao_venda_carro(screen, fundo_para_confirmacao, carro_atual['nome'], preco_venda)
                                                if confirmado:
                                                    if gerenciador_progresso.vender_carro(carro_atual['prefixo_cor'], preco_venda):
                                                        from core.i18n import t
                                                        popup_musica.mostrar(t("mensagens.carro_vendido").format(carro_atual['nome']), tipo="outra")
                                                    else:
                                                        from core.i18n import t
                                                        popup_musica.mostrar(t("mensagens.erro_vender_carro"), tipo="outra")
                                            else:
                                                from core.i18n import t
                                                popup_musica.mostrar(t("mensagens.nao_pode_vender_unico_carro"), tipo="outra")
                                    elif botao_selecionado_controle == "concluido":
                                        # Confirmar seleção
                                        if botao_concluido_rect_p2:
                                            # Verificar se o carro está desbloqueado antes de permitir concluir
                                            carro_atual_p2 = CARROS_DISPONIVEIS[carro_p2]
                                            esta_desbloqueado_p2 = gerenciador_progresso.esta_desbloqueado(carro_atual_p2['prefixo_cor'])
                                            if not esta_desbloqueado_p2 and carro_atual_p2['prefixo_cor'] != "Car1":
                                                from core.i18n import t
                                                popup_musica.mostrar(t("mensagens.comprar_carro_primeiro"), tipo="outra")
                                            elif carro_selecionado_p2:
                                                gerenciador_progresso.definir_carro_atual(carro_p1=carro_p1, carro_p2=carro_p2)
                                                return carro_p1, carro_p2
                                    elif botao_selecionado_controle == "voltar":
                                        # Voltar para o menu ou seleção de mapas (no modo arcade)
                                        if modo_arcade:
                                            # No modo arcade, sempre voltar para seleção de mapas
                                            return None, None
                                        elif carro_selecionado_p2:
                                            gerenciador_progresso.definir_carro_atual(carro_p1=carro_p1, carro_p2=carro_p2)
                                            return carro_p1, carro_p2
                                        else:
                                            return None, None
                                else:
                                    # Carro não desbloqueado
                                    if botao_selecionado_controle == "comprar":
                                        # Tentar comprar - mostrar confirmação primeiro
                                        if botao_comprar_rect_p2:
                                            preco = carro_atual.get('preco', 0)
                                            # Mostrar diálogo de confirmação
                                            fundo_para_confirmacao = fundo_sem_textos if 'fundo_sem_textos' in locals() else bg
                                            confirmado = mostrar_dialogo_confirmacao_compra_carro(screen, fundo_para_confirmacao, carro_atual['nome'], preco)
                                            if confirmado:
                                                if gerenciador_progresso.comprar_carro(carro_atual['prefixo_cor'], preco):
                                                    from core.i18n import t
                                                    popup_musica.mostrar(t("mensagens.carro_comprado").format(carro_atual['nome']), tipo="outra")
                                                else:
                                                    from core.i18n import t
                                                    popup_musica.mostrar(t("mensagens.dinheiro_insuficiente"), tipo="outra")
                                    elif botao_selecionado_controle == "upgrade":
                                        # Abrir tela de upgrades
                                        if botao_upgrade_rect_p2:
                                            # Marcar que visitou a tela de upgrades para este carro
                                            gerenciador_progresso.marcar_upgrades_visitado(carro_atual['prefixo_cor'])
                                            tela_upgrades_aberta = True
                                            carro_upgrade_atual = carro_p2
                                    elif botao_selecionado_controle == "vender":
                                        # Vender carro (não aplicável se não desbloqueado)
                                        pass
                                    elif botao_selecionado_controle == "concluido":
                                        # Confirmar seleção (não aplicável se não desbloqueado)
                                        pass
                        elif acao == "cancelar":
                            # Voltar
                            if botao_voltar_rect:
                                # No modo arcade, sempre cancelar e voltar à seleção de pistas
                                if modo_arcade:
                                    return None, None
                                
                                if modo_dois_jogadores:
                                    if fase_selecao == 1 and carro_selecionado_p1:
                                        fase_selecao = 2
                                    elif fase_selecao == 2 and carro_selecionado_p2:
                                        gerenciador_progresso.definir_carro_atual(carro_p1=carro_p1, carro_p2=carro_p2)
                                        return carro_p1, carro_p2
                                    elif fase_selecao == 1:
                                        return None, None
                                    else:
                                        return None, None
                                else:
                                    if carro_selecionado_p1:
                                        gerenciador_progresso.definir_carro_atual(carro_p1=carro_p1)
                                        return carro_p1, carro_p2
                                    else:
                                        return None, None
                
                # Se processou evento de controle, não processar mouse/teclado para esse evento
                if controle_processado:
                    continue
            
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if oficina_pausada:
                    # Processar clique no menu de pause
                    mouse_x, mouse_y = ev.pos
                    caixa_largura = 500
                    caixa_altura = 400
                    caixa_x = (LARGURA - caixa_largura) // 2
                    caixa_y = (ALTURA - caixa_altura) // 2
                    
                    from core.i18n import t
                    opcoes_pausa = [
                        (t("pause.continuar"), "continuar"),
                        (t("pause.salvar"), "salvar"),
                        (t("pause.opcoes"), "opcoes"),
                        (t("pause.menu_principal"), "menu")
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
                                    oficina_pausada = False
                                elif i == 1:
                                    # Salvar
                                    from core.progresso import gerenciador_progresso
                                    gerenciador_progresso.salvar()
                                    oficina_pausada = False
                                elif i == 2:
                                    # Opções (por enquanto, apenas continuar)
                                    oficina_pausada = False
                                elif i == 3:
                                    # Menu principal
                                    return None, None
                                break
                    continue  # Não processar outros cliques quando pausado
                
                # Verificar clique no botão "Voltar"
                if botao_voltar_rect.collidepoint(ev.pos[0], ev.pos[1]):
                    # No modo arcade, sempre cancelar e voltar à seleção de pistas
                    if modo_arcade:
                        return None, None
                    
                    # Se estiver no modo 2 jogadores, verificar se ambos selecionaram
                    if modo_dois_jogadores:
                        if fase_selecao == 1 and carro_selecionado_p1:
                            fase_selecao = 2  # Vai para P2
                            continue
                        elif fase_selecao == 2 and carro_selecionado_p2:
                            gerenciador_progresso.definir_carro_atual(carro_p1=carro_p1, carro_p2=carro_p2)
                            return carro_p1, carro_p2
                        elif fase_selecao == 1:
                            return None, None
                        else:
                            return None, None
                    else:
                        if carro_selecionado_p1:
                            gerenciador_progresso.definir_carro_atual(carro_p1=carro_p1)
                            return carro_p1, carro_p2
                        else:
                            return None, None
                
                # Botão "2 jogadores" removido - o modo é definido antes de entrar na oficina
                # Verificar clique nos botões
                if not transicao_ativa:
                    mouse_x, mouse_y = ev.pos
                    
                    if fase_selecao == 1:
                        carro_atual = CARROS_DISPONIVEIS_FILTRADOS[carro_p1] if not modo_arcade else CARROS_DISPONIVEIS[carro_p1]
                        esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                        
                        # Verificar clique nas setas de navegação (apenas no modo arcade)
                        if not modo_arcade:
                            # No modo campanha, não há navegação entre carros
                            pass
                        elif seta_esquerda_rect_p1 and seta_esquerda_rect_p1.collidepoint(mouse_x, mouse_y) and carro_p1 > 0 and not transicao_ativa:
                            iniciar_transicao(-1, carro_p1)
                            carro_p1 = (carro_p1 - 1) % len(CARROS_DISPONIVEIS)
                            carro_selecionado_p1 = (obter_carro_idx_seguro(1) == carro_p1)
                            continue
                        elif seta_direita_rect_p1 and seta_direita_rect_p1.collidepoint(mouse_x, mouse_y) and not transicao_ativa:
                            iniciar_transicao(1, carro_p1)
                            carro_p1 = (carro_p1 + 1) % len(CARROS_DISPONIVEIS)
                            carro_selecionado_p1 = (obter_carro_idx_seguro(1) == carro_p1)
                            continue
                        
                        if esta_desbloqueado:
                            # Verificar clique no botão USAR/REPARAR
                            if botao_usar_rect_p1 and botao_usar_rect_p1.collidepoint(mouse_x, mouse_y):
                                # Verificar se o carro atual está selecionado
                                carro_atual_p1 = obter_carro_idx_seguro(1)
                                carro_atual_idx = carro_p1 if carro_atual_p1 is None else carro_atual_p1
                                if carro_atual_idx == carro_p1:
                                    # Carro já está selecionado - reparar apenas se necessário
                                    from core.crank import crank
                                    saude_carro = crank.saude_carro if hasattr(crank, 'saude_carro') else 1.0
                                    if saude_carro < 1.0:
                                        custo_reparo = int((1.0 - saude_carro) * 2000)
                                        if crank.reparar_carro(custo_reparo):
                                            popup_musica.mostrar(t("mensagens.carro_reparado").format(custo_reparo), tipo="outra")
                                        # Se não tem dinheiro, não mostrar mensagem (carro já está selecionado)
                                    # Se o carro não precisa de reparo, não fazer nada
                                else:
                                    # Selecionar o carro
                                    carro_selecionado_p1 = True
                                    gerenciador_progresso.definir_carro_atual(carro_p1=carro_p1)
                                    from core.i18n import t
                                    popup_musica.mostrar("Carro selecionado!", tipo="outra")
                            # Verificar clique no botão "Concluído"
                            elif botao_concluido_rect_p1 and botao_concluido_rect_p1.collidepoint(mouse_x, mouse_y):
                                # Verificar se o carro está desbloqueado antes de permitir concluir
                                if not esta_desbloqueado and carro_atual['prefixo_cor'] != "Car1":
                                    from core.i18n import t
                                    popup_musica.mostrar(t("mensagens.comprar_carro_primeiro"), tipo="outra")
                                else:
                                    # Sempre salvar o carro atual antes de retornar
                                    gerenciador_progresso.definir_carro_atual(carro_p1=carro_p1)
                                    if modo_dois_jogadores:
                                        # P1 confirmou, vai para P2
                                        fase_selecao = 2
                                    else:
                                        return carro_p1, carro_p2
                            # Botão "2 JOGADORES" lateral removido (não existe mais)
                            # Verificar clique no botão UPGRADE
                            elif botao_upgrade_rect_p1 and botao_upgrade_rect_p1.collidepoint(mouse_x, mouse_y):
                                # Verificar se carro está desbloqueado (Car1 sempre desbloqueado)
                                pode_upgrade = (carro_atual['prefixo_cor'] == "Car1") or esta_desbloqueado
                                if pode_upgrade and fundo_sem_textos:
                                    # Marcar que visitou a tela de upgrades para este carro
                                    gerenciador_progresso.marcar_upgrades_visitado(carro_atual['prefixo_cor'])
                                    if tela_upgrades(screen, carro_atual['prefixo_cor'], carro_atual['nome'], fundo_sem_textos):
                                        pass  # Volta para seleção de carros
                                elif not pode_upgrade:
                                    from core.i18n import t
                                    popup_musica.mostrar(t("mensagens.comprar_carro_primeiro"), tipo="outra")
                            # Verificar clique no botão ESCOLHER COR (modo campanha)
                            elif botao_escolher_cor_rect_p1 and botao_escolher_cor_rect_p1.collidepoint(mouse_x, mouse_y):
                                # Mostrar tela de seleção de cores
                                cor_escolhida = _mostrar_selecao_cores(screen, fundo_sem_textos)
                                if cor_escolhida:
                                    gerenciador_progresso.carro_campanha_cor_final = cor_escolhida
                                    gerenciador_progresso.salvar()
                                    
                                    # Recarregar sprite do carro com a cor escolhida
                                    sprite_path_campanha = obter_sprite_carro_campanha(carro_atual['prefixo_cor'])
                                    if sprite_path_campanha and os.path.exists(sprite_path_campanha):
                                        sprite = pygame.image.load(sprite_path_campanha).convert_alpha()
                                        
                                        # Obter configuração do carro da campanha
                                        config_carro = obter_config_carro_campanha() if not modo_arcade and carro_atual['prefixo_cor'] == 'Car1' else None
                                        
                                        if config_carro:
                                            tamanho_oficina = config_carro.get('tamanho_oficina', [600, 300])
                                            escala_config = config_carro.get('escala', 1.0)
                                            canvas_largura = int(tamanho_oficina[0] * escala_config)
                                            canvas_altura = int(tamanho_oficina[1] * escala_config)
                                        else:
                                            tamanho_oficina = carro_atual.get('tamanho_oficina', (600, 300))
                                            canvas_largura, canvas_altura = tamanho_oficina
                                        
                                        # Calcular escala para manter proporção
                                        sprite_original = sprite
                                        escala_x = canvas_largura / sprite_original.get_width() if sprite_original.get_width() > 0 else 1.0
                                        escala_y = canvas_altura / sprite_original.get_height() if sprite_original.get_height() > 0 else 1.0
                                        escala = min(escala_x, escala_y)
                                        
                                        # Redimensionar mantendo proporção
                                        nova_largura = int(sprite_original.get_width() * escala)
                                        nova_altura = int(sprite_original.get_height() * escala)
                                        sprite_redimensionado = pygame.transform.scale(sprite_original, (nova_largura, nova_altura))
                                        
                                        # Criar canvas
                                        sprite = pygame.Surface((canvas_largura, canvas_altura), pygame.SRCALPHA)
                                        
                                        # Posicionar sprite no canvas
                                        x_offset = (canvas_largura - nova_largura) // 2
                                        if config_carro:
                                            y_offset = canvas_altura - nova_altura + config_carro.get('y_offset', -10)
                                        else:
                                            y_offset = canvas_altura - nova_altura - 10
                                        sprite.blit(sprite_redimensionado, (x_offset, y_offset))
                                        sprites_carros[carro_atual['prefixo_cor']] = sprite
                                        
                                        # Pré-processar versão escurecida
                                        sprite_escurecido = sprite.copy()
                                        overlay_preto = pygame.Surface(sprite_escurecido.get_size(), pygame.SRCALPHA)
                                        overlay_preto.fill((0, 0, 0, 240))
                                        sprite_escurecido.blit(overlay_preto, (0, 0), special_flags=pygame.BLEND_MULT)
                                        sprites_carros_escurecidos[carro_atual['prefixo_cor']] = sprite_escurecido
                                    
                                    from core.i18n import t
                                    popup_musica.mostrar(f"Cor {cor_escolhida.upper()} aplicada!", tipo="outra")
                            
                            # Verificar clique no botão MELHORAR (modo campanha)
                            elif botao_melhorar_rect_p1 and botao_melhorar_rect_p1.collidepoint(mouse_x, mouse_y):
                                estagio_atual = gerenciador_progresso.carro_campanha_estagio
                                custo_melhoria = [5000, 10000, 15000][estagio_atual] if estagio_atual < 3 else 0
                                
                                if gerenciador_progresso.tem_dinheiro(custo_melhoria) and estagio_atual < 3:
                                    # Processar melhoria com transição
                                    gerenciador_progresso.dinheiro -= custo_melhoria
                                    gerenciador_progresso.carro_campanha_estagio += 1
                                    gerenciador_progresso.salvar()
                                    
                                    # Executar transição de melhoria
                                    _executar_transicao_melhoria(screen, fundo_sem_textos)
                                    
                                    # Recarregar sprite do carro (forçar recarregamento)
                                    sprite_path_campanha = obter_sprite_carro_campanha(carro_atual['prefixo_cor'])
                                    if sprite_path_campanha and os.path.exists(sprite_path_campanha):
                                        sprite = pygame.image.load(sprite_path_campanha).convert_alpha()
                                        
                                        # Obter configuração do carro da campanha (usar a mesma lógica do carregamento inicial)
                                        config_carro = obter_config_carro_campanha() if not modo_arcade and carro_atual['prefixo_cor'] == 'Car1' else None
                                        
                                        if config_carro:
                                            # Usar configuração do arquivo JSON (mesma lógica do carregamento inicial)
                                            tamanho_oficina = config_carro.get('tamanho_oficina', [600, 300])
                                            escala_config = config_carro.get('escala', 1.0)
                                            canvas_largura = int(tamanho_oficina[0] * escala_config)
                                            canvas_altura = int(tamanho_oficina[1] * escala_config)
                                        else:
                                            # Usar tamanho padrão do carro
                                            tamanho_oficina = carro_atual.get('tamanho_oficina', (600, 300))
                                            canvas_largura, canvas_altura = tamanho_oficina
                                        
                                        # Calcular escala para manter proporção
                                        sprite_original = sprite
                                        escala_x = canvas_largura / sprite_original.get_width() if sprite_original.get_width() > 0 else 1.0
                                        escala_y = canvas_altura / sprite_original.get_height() if sprite_original.get_height() > 0 else 1.0
                                        escala = min(escala_x, escala_y)  # Usar a menor escala para manter proporção
                                        
                                        # Redimensionar mantendo proporção
                                        nova_largura = int(sprite_original.get_width() * escala)
                                        nova_altura = int(sprite_original.get_height() * escala)
                                        sprite_redimensionado = pygame.transform.scale(sprite_original, (nova_largura, nova_altura))
                                        
                                        # Criar canvas com tamanho individual
                                        sprite = pygame.Surface((canvas_largura, canvas_altura), pygame.SRCALPHA)
                                        
                                        # Centralizar horizontalmente e posicionar na parte inferior (encostado no chão)
                                        x_offset = (canvas_largura - nova_largura) // 2
                                        # Ajustar y_offset usando configuração ou padrão
                                        if config_carro:
                                            y_offset = canvas_altura - nova_altura + config_carro.get('y_offset', -10)
                                        else:
                                            y_offset = canvas_altura - nova_altura - 10  # Posicionar no chão
                                        sprite.blit(sprite_redimensionado, (x_offset, y_offset))
                                        sprites_carros[carro_atual['prefixo_cor']] = sprite
                                        
                                        # Pré-processar versão escurecida
                                        sprite_escurecido = sprite.copy()
                                        overlay_preto = pygame.Surface(sprite_escurecido.get_size(), pygame.SRCALPHA)
                                        overlay_preto.fill((0, 0, 0, 240))
                                        sprite_escurecido.blit(overlay_preto, (0, 0), special_flags=pygame.BLEND_MULT)
                                        sprites_carros_escurecidos[carro_atual['prefixo_cor']] = sprite_escurecido
                                    
                                    from core.i18n import t
                                    popup_musica.mostrar(f"Cor {cor_escolhida.upper()} aplicada!", tipo="outra")
                                else:
                                    from core.i18n import t
                                    popup_musica.mostrar(t("mensagens.dinheiro_insuficiente"), tipo="outra")
                            # Verificar clique no botão VENDER
                            elif botao_vender_rect_p1 and botao_vender_rect_p1.collidepoint(mouse_x, mouse_y):
                                if gerenciador_progresso.contar_carros_desbloqueados() > 1:
                                    preco_venda = int(carro_atual.get('preco', 0) * 0.5)  # 50% do preço original
                                    if gerenciador_progresso.vender_carro(carro_atual['prefixo_cor'], preco_venda):
                                        from core.i18n import t
                                        popup_musica.mostrar(t("mensagens.carro_vendido").format(carro_atual['nome']), tipo="outra")
                                    else:
                                        from core.i18n import t
                                        popup_musica.mostrar(t("mensagens.erro_vender_carro"), tipo="outra")
                                else:
                                    from core.i18n import t
                                    popup_musica.mostrar(t("mensagens.nao_pode_vender_unico_carro"), tipo="outra")
                        else:
                            # Verificar clique no botão COMPRAR
                            if botao_comprar_rect_p1 and botao_comprar_rect_p1.collidepoint(mouse_x, mouse_y):
                                preco = carro_atual.get('preco', 0)
                                # Mostrar diálogo de confirmação
                                fundo_para_confirmacao = fundo_sem_textos if 'fundo_sem_textos' in locals() else bg
                                confirmado = mostrar_dialogo_confirmacao_compra_carro(screen, fundo_para_confirmacao, carro_atual['nome'], preco)
                                if confirmado:
                                    if gerenciador_progresso.comprar_carro(carro_atual['prefixo_cor'], preco):
                                        from core.i18n import t
                                        popup_musica.mostrar(t("mensagens.carro_comprado").format(carro_atual['nome']), tipo="outra")
                                    else:
                                        from core.i18n import t
                                        popup_musica.mostrar(t("mensagens.dinheiro_insuficiente"), tipo="outra")
                            # Verificar clique no botão UPGRADE (desabilitado se não comprado)
                            elif botao_upgrade_rect_p1 and botao_upgrade_rect_p1.collidepoint(mouse_x, mouse_y):
                                # Botão está desabilitado visualmente, não faz nada
                                pass
                    elif fase_selecao == 2:
                        carro_atual = CARROS_DISPONIVEIS[carro_p2]
                        esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                        
                        # Verificar clique nas setas de navegação P2
                        if seta_esquerda_rect_p2 and seta_esquerda_rect_p2.collidepoint(mouse_x, mouse_y) and carro_p2 > 0 and not transicao_ativa:
                            iniciar_transicao(-1, carro_p2)
                            carro_p2 = (carro_p2 - 1) % len(CARROS_DISPONIVEIS)
                            carro_selecionado_p2 = (obter_carro_idx_seguro(2) == carro_p2)
                            continue
                        
                        if seta_direita_rect_p2 and seta_direita_rect_p2.collidepoint(mouse_x, mouse_y) and not transicao_ativa:
                            iniciar_transicao(1, carro_p2)
                            carro_p2 = (carro_p2 + 1) % len(CARROS_DISPONIVEIS)
                            carro_selecionado_p2 = (obter_carro_idx_seguro(2) == carro_p2)
                            continue
                        
                        if esta_desbloqueado:
                            # Verificar clique no botão USAR (apenas seleciona o carro, se não estiver já selecionado)
                            if botao_usar_rect_p2 and botao_usar_rect_p2.collidepoint(mouse_x, mouse_y):
                                if not carro_selecionado_p2:
                                    carro_selecionado_p2 = True
                                    from core.i18n import t
                                    popup_musica.mostrar("Carro selecionado!", tipo="outra")
                                else:
                                    # Carro já está selecionado
                                    from core.i18n import t
                                    popup_musica.mostrar("Carro já selecionado!", tipo="outra")
                            # Verificar clique no botão "Concluído"
                            elif botao_concluido_rect_p2 and botao_concluido_rect_p2.collidepoint(mouse_x, mouse_y):
                                # Verificar se o carro está desbloqueado antes de permitir concluir
                                carro_atual_p2 = CARROS_DISPONIVEIS[carro_p2]
                                esta_desbloqueado_p2 = gerenciador_progresso.esta_desbloqueado(carro_atual_p2['prefixo_cor'])
                                if not esta_desbloqueado_p2 and carro_atual_p2['prefixo_cor'] != "Car1":
                                    from core.i18n import t
                                    popup_musica.mostrar(t("mensagens.comprar_carro_primeiro"), tipo="outra")
                                elif carro_selecionado_p2:
                                    gerenciador_progresso.definir_carro_atual(carro_p1=carro_p1, carro_p2=carro_p2)
                                    return carro_p1, carro_p2
                            # Verificar clique no botão UPGRADE
                            elif botao_upgrade_rect_p2 and botao_upgrade_rect_p2.collidepoint(mouse_x, mouse_y):
                                # Verificar se carro está desbloqueado (Car1 sempre desbloqueado)
                                pode_upgrade = (carro_atual['prefixo_cor'] == "Car1") or esta_desbloqueado
                                if pode_upgrade and fundo_sem_textos:
                                    # Marcar que visitou a tela de upgrades para este carro
                                    gerenciador_progresso.marcar_upgrades_visitado(carro_atual['prefixo_cor'])
                                    if tela_upgrades(screen, carro_atual['prefixo_cor'], carro_atual['nome'], fundo_sem_textos):
                                        pass  # Volta para seleção de carros
                                elif not pode_upgrade:
                                    from core.i18n import t
                                    popup_musica.mostrar(t("mensagens.comprar_carro_primeiro"), tipo="outra")
                            # Verificar clique no botão VENDER
                            elif botao_vender_rect_p2 and botao_vender_rect_p2.collidepoint(mouse_x, mouse_y):
                                if gerenciador_progresso.contar_carros_desbloqueados() > 1:
                                    preco_venda = int(carro_atual.get('preco', 0) * 0.5)  # 50% do preço original
                                    if gerenciador_progresso.vender_carro(carro_atual['prefixo_cor'], preco_venda):
                                        from core.i18n import t
                                        popup_musica.mostrar(t("mensagens.carro_vendido").format(carro_atual['nome']), tipo="outra")
                                    else:
                                        from core.i18n import t
                                        popup_musica.mostrar(t("mensagens.erro_vender_carro"), tipo="outra")
                                else:
                                    from core.i18n import t
                                    popup_musica.mostrar(t("mensagens.nao_pode_vender_unico_carro"), tipo="outra")
                        else:
                            # Verificar clique no botão COMPRAR
                            if botao_comprar_rect_p2 and botao_comprar_rect_p2.collidepoint(mouse_x, mouse_y):
                                preco = carro_atual.get('preco', 0)
                                # Mostrar diálogo de confirmação
                                fundo_para_confirmacao = fundo_sem_textos if 'fundo_sem_textos' in locals() else bg
                                confirmado = mostrar_dialogo_confirmacao_compra_carro(screen, fundo_para_confirmacao, carro_atual['nome'], preco)
                                if confirmado:
                                    if gerenciador_progresso.comprar_carro(carro_atual['prefixo_cor'], preco):
                                        from core.i18n import t
                                        popup_musica.mostrar(t("mensagens.carro_comprado").format(carro_atual['nome']), tipo="outra")
                                    else:
                                        from core.i18n import t
                                        popup_musica.mostrar(t("mensagens.dinheiro_insuficiente"), tipo="outra")
                            # Verificar clique no botão UPGRADE (desabilitado se não comprado)
                            elif botao_upgrade_rect_p2 and botao_upgrade_rect_p2.collidepoint(mouse_x, mouse_y):
                                # Botão está desabilitado visualmente, não faz nada
                                pass
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    # Alternar pause
                    oficina_pausada = not oficina_pausada
                    if oficina_pausada:
                        opcao_pausa_selecionada = 0
                elif oficina_pausada:
                    # Processar navegação no menu de pause
                    if ev.key in (pygame.K_UP, pygame.K_w):
                        opcao_pausa_selecionada = (opcao_pausa_selecionada - 1) % 4
                    elif ev.key in (pygame.K_DOWN, pygame.K_s):
                        opcao_pausa_selecionada = (opcao_pausa_selecionada + 1) % 4
                    elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        # Selecionar opção
                        if opcao_pausa_selecionada == 0:
                            # Continuar
                            oficina_pausada = False
                        elif opcao_pausa_selecionada == 1:
                            # Salvar
                            from core.progresso import gerenciador_progresso
                            gerenciador_progresso.salvar()
                            mostrar_mensagem_salvo = True
                            tempo_mensagem_salvo = 0.0
                            oficina_pausada = False
                        elif opcao_pausa_selecionada == 2:
                            # Opções (por enquanto, apenas continuar)
                            oficina_pausada = False
                        elif opcao_pausa_selecionada == 3:
                            # Menu principal
                            return None, None
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    # No modo campanha, não permitir navegação entre carros
                    if modo_arcade and not transicao_ativa:  # Só permite navegação se não estiver em transição e estiver no modo arcade
                        if fase_selecao == 1:
                            iniciar_transicao(-1, carro_p1)
                            carro_p1 = (carro_p1 - 1) % len(CARROS_DISPONIVEIS)
                            carro_selecionado_p1 = (obter_carro_idx_seguro(1) == carro_p1)
                        elif fase_selecao == 2:
                            iniciar_transicao(-1, carro_p2)
                            carro_p2 = (carro_p2 - 1) % len(CARROS_DISPONIVEIS)
                            carro_selecionado_p2 = (obter_carro_idx_seguro(2) == carro_p2)
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    # No modo campanha, não permitir navegação entre carros
                    if modo_arcade and not transicao_ativa:  # Só permite navegação se não estiver em transição e estiver no modo arcade
                        if fase_selecao == 1:
                            iniciar_transicao(1, carro_p1)
                            carro_p1 = (carro_p1 + 1) % len(CARROS_DISPONIVEIS)
                            carro_selecionado_p1 = (obter_carro_idx_seguro(1) == carro_p1)
                        elif fase_selecao == 2:
                            iniciar_transicao(1, carro_p2)
                            carro_p2 = (carro_p2 + 1) % len(CARROS_DISPONIVEIS)
                            carro_selecionado_p2 = (obter_carro_idx_seguro(2) == carro_p2)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if not transicao_ativa:  # Só permite confirmação se não estiver em transição
                        if fase_selecao == 1:
                            carro_atual = CARROS_DISPONIVEIS_FILTRADOS[carro_p1] if not modo_arcade else CARROS_DISPONIVEIS[carro_p1]
                            esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                            if esta_desbloqueado and carro_selecionado_p1:
                                # Só avança para fase 2 se for modo 2 jogadores
                                if modo_dois_jogadores:
                                    fase_selecao = 2
                                else:
                                    # Modo 1 jogador: confirma e retorna
                                    gerenciador_progresso.definir_carro_atual(carro_p1=carro_p1, carro_p2=carro_p2)
                                    return carro_p1, carro_p2
                        elif fase_selecao == 2:
                            carro_atual = CARROS_DISPONIVEIS[carro_p2]
                            esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                            if esta_desbloqueado and carro_selecionado_p2:
                                gerenciador_progresso.definir_carro_atual(carro_p1=carro_p1, carro_p2=carro_p2)
                                return carro_p1, carro_p2
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
        
        from core.i18n import t
        
        # Título - estilo pixel art (azul ciano harmonizado) - mais espaçado
        titulo = render_text(t("menu.oficina.titulo"), 48, (100, 220, 255), bold=True, pixel_style=True)
        titulo_x = (LARGURA - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, 30))
        
        # Subtítulo indicando qual jogador está escolhendo (modo 2 jogadores)
        if modo_dois_jogadores:
            if fase_selecao == 1:
                subtitulo_texto = t("menu.oficina.jogador_1")
            else:
                subtitulo_texto = t("menu.oficina.jogador_2")
            subtitulo = render_text(subtitulo_texto, 32, (150, 220, 255), bold=True, pixel_style=True)
            subtitulo_x = (LARGURA - subtitulo.get_width()) // 2
            screen.blit(subtitulo, (subtitulo_x, 85))
        
        # Mostrar dinheiro no canto superior direito (dourado suave harmonizado)
        dinheiro_texto = t("menu.oficina.dinheiro").format(gerenciador_progresso.dinheiro)
        dinheiro_render = render_text(dinheiro_texto, 32, (255, 220, 100), bold=True, pixel_style=True)
        dinheiro_x = LARGURA - dinheiro_render.get_width() - 20
        screen.blit(dinheiro_render, (dinheiro_x, 20))
        
        # Botões "Voltar" e "2 jogadores" acima do dinheiro
        botao_voltar_largura = 120
        botao_voltar_altura = 40
        botao_voltar_x = 20
        botao_voltar_y = 20
        botao_voltar_rect = pygame.Rect(botao_voltar_x, botao_voltar_y, botao_voltar_largura, botao_voltar_altura)
        botao_voltar_hover = botao_voltar_rect.collidepoint(pygame.mouse.get_pos())
        
        botao_dois_jogadores_largura = 150
        botao_dois_jogadores_altura = 40
        botao_dois_jogadores_x = botao_voltar_x + botao_voltar_largura + 10
        botao_dois_jogadores_y = 20
        botao_dois_jogadores_menu_rect = pygame.Rect(botao_dois_jogadores_x, botao_dois_jogadores_y, botao_dois_jogadores_largura, botao_dois_jogadores_altura)
        botao_dois_jogadores_menu_hover = botao_dois_jogadores_menu_rect.collidepoint(pygame.mouse.get_pos())
        
        # Desenhar botão "Voltar"
        selecionado_controle_voltar = (botao_selecionado_controle == "voltar")
        cor_voltar = (100, 150, 200) if botao_voltar_hover else (80, 120, 180)
        pygame.draw.rect(screen, cor_voltar, botao_voltar_rect)
        pygame.draw.rect(screen, (150, 200, 255), botao_voltar_rect, 2)
        # Desenhar cursor do controle (caixa animada)
        if selecionado_controle_voltar and gerenciador_gamepad.obter_numero_controles() > 0:
            tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
            cursor_rect = pygame.Rect(
                botao_voltar_rect.x - tamanho_cursor,
                botao_voltar_rect.y - tamanho_cursor,
                botao_voltar_rect.width + tamanho_cursor * 2,
                botao_voltar_rect.height + tamanho_cursor * 2
            )
            pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
        from core.i18n import t
        texto_voltar = render_text(t("menu.oficina.voltar"), 18, (255, 255, 255), bold=True, pixel_style=True)
        texto_voltar_x = botao_voltar_rect.x + (botao_voltar_rect.width - texto_voltar.get_width()) // 2
        texto_voltar_y = botao_voltar_rect.y + (botao_voltar_rect.height - texto_voltar.get_height()) // 2
        screen.blit(texto_voltar, (texto_voltar_x, texto_voltar_y))
        
        # Desenhar botão "2 jogadores" / "1 jogador" (apenas na fase 1)
        if fase_selecao == 1:
            if modo_dois_jogadores:
                # Mostrar botão "1 jogador" quando estiver no modo 2 jogadores
                texto_botao = "1 JOGADOR"
            else:
                # Mostrar botão "2 jogadores" quando estiver no modo single player
                texto_botao = t("menu.oficina.dois_jogadores")
            
            # Botão "2 jogadores" removido - o modo é definido antes de entrar na oficina
        
        if fase_selecao == 1:
            # FASE 1: Player 1 selecionando - sem subtítulo de "JOGADOR 1" e sem instruções
            
            # Carro selecionado P1 - Grande e centralizado
            # Garantir que carro_p1 seja válido no modo campanha
            if not modo_arcade:
                carro_p1 = 0  # Sempre usar índice 0 no modo campanha
                if carro_p1 >= len(CARROS_DISPONIVEIS_FILTRADOS):
                    carro_p1 = 0
            carro_atual = CARROS_DISPONIVEIS_FILTRADOS[carro_p1] if not modo_arcade else CARROS_DISPONIVEIS[carro_p1]
            
            if transicao_ativa:
                carro_anterior_obj = CARROS_DISPONIVEIS_FILTRADOS[carro_anterior] if not modo_arcade else CARROS_DISPONIVEIS[carro_anterior]
                carro_atual_obj = CARROS_DISPONIVEIS_FILTRADOS[carro_p1] if not modo_arcade else CARROS_DISPONIVEIS[carro_p1]
                sprite_anterior = sprites_carros.get(carro_anterior_obj['prefixo_cor'])
                sprite_atual = sprites_carros.get(carro_atual_obj['prefixo_cor'])
                if sprite_anterior is None or sprite_atual is None:
                    # Fallback se sprite não encontrado
                    sprite_anterior = sprite_atual = sprites_carros.get('Car1', pygame.Surface((100, 100)))
                
                # Para carros da campanha, centralizar o canvas como no editor
                config_anterior = obter_config_carro_campanha() if not modo_arcade and carro_anterior_obj['prefixo_cor'] == 'Car1' else None
                config_atual = obter_config_carro_campanha() if not modo_arcade and carro_atual_obj['prefixo_cor'] == 'Car1' else None
                
                if config_anterior:
                    canvas_largura_ant = sprite_anterior.get_width()
                    canvas_altura_ant = sprite_anterior.get_height()
                    pos_anterior = ((LARGURA - canvas_largura_ant) // 2, (ALTURA - canvas_altura_ant) // 2)
                else:
                    pos_anterior = carro_anterior_obj.get('posicao_oficina', (LARGURA//2 - 300, 380))
                
                if config_atual:
                    canvas_largura_atual = sprite_atual.get_width()
                    canvas_altura_atual = sprite_atual.get_height()
                    pos_atual = ((LARGURA - canvas_largura_atual) // 2, (ALTURA - canvas_altura_atual) // 2)
                else:
                    pos_atual = carro_atual_obj.get('posicao_oficina', (LARGURA//2 - 300, 380))
                
                pos_x_anterior = pos_anterior[0] + carro_atual_pos * LARGURA
                pos_x_atual = pos_atual[0] + carro_proximo_pos * LARGURA
                
                esta_desbloqueado_anterior = gerenciador_progresso.esta_desbloqueado(carro_anterior_obj['prefixo_cor'])
                esta_desbloqueado_atual = gerenciador_progresso.esta_desbloqueado(carro_atual_obj['prefixo_cor'])
                
                sprite_anterior_desenhar = sprites_carros_escurecidos.get(carro_anterior_obj['prefixo_cor'], sprite_anterior) if not esta_desbloqueado_anterior else sprite_anterior
                sprite_atual_desenhar = sprites_carros_escurecidos.get(carro_atual_obj['prefixo_cor'], sprite_atual) if not esta_desbloqueado_atual else sprite_atual
                
                screen.blit(sprite_anterior_desenhar, (int(pos_x_anterior), pos_anterior[1]))
                screen.blit(sprite_atual_desenhar, (int(pos_x_atual), pos_atual[1]))
                
                if not esta_desbloqueado_atual and icone_cadeado:
                    cadeado_x = int(pos_x_atual) + (sprite_atual.get_width() - icone_cadeado.get_width()) // 2
                    cadeado_y = pos_atual[1] + (sprite_atual.get_height() - icone_cadeado.get_height()) // 2
                    screen.blit(icone_cadeado, (cadeado_x, cadeado_y))
            else:
                sprite_atual = sprites_carros.get(carro_atual['prefixo_cor'])
                if sprite_atual is None:
                    # Fallback se sprite não encontrado
                    sprite_atual = sprites_carros.get('Car1', pygame.Surface((100, 100)))
                
                # Para carros da campanha, centralizar o canvas como no editor
                config_carro = obter_config_carro_campanha() if not modo_arcade and carro_atual['prefixo_cor'] == 'Car1' else None
                if config_carro:
                    # Centralizar canvas na tela (como no editor)
                    canvas_largura = sprite_atual.get_width()
                    canvas_altura = sprite_atual.get_height()
                    posicao = ((LARGURA - canvas_largura) // 2, (ALTURA - canvas_altura) // 2)
                else:
                    posicao = carro_atual.get('posicao_oficina', (LARGURA//2 - 300, 380))
                
                esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                sprite_atual_desenhar = sprites_carros_escurecidos.get(carro_atual['prefixo_cor'], sprite_atual) if not esta_desbloqueado else sprite_atual
                
                screen.blit(sprite_atual_desenhar, posicao)
                
                if not esta_desbloqueado and icone_cadeado:
                    cadeado_x = posicao[0] + (sprite_atual.get_width() - icone_cadeado.get_width()) // 2
                    cadeado_y = posicao[1] + (sprite_atual.get_height() - icone_cadeado.get_height()) // 2
                    screen.blit(icone_cadeado, (cadeado_x, cadeado_y))
            
            # Indicadores de navegação (setas) para carros P1 - desenhar DEPOIS do carro para ficar na frente
            # No modo campanha, não mostrar setas (só tem Car1)
            seta_esquerda_rect_p1 = None
            seta_direita_rect_p1 = None
            # Mostrar setas em ambos os modos (arcade e campanha)
            if len(CARROS_DISPONIVEIS_FILTRADOS if not modo_arcade else CARROS_DISPONIVEIS) > 1:
                num_carros_disponiveis = len(CARROS_DISPONIVEIS_FILTRADOS) if not modo_arcade else len(CARROS_DISPONIVEIS)
                # Seta esquerda (se não estiver no primeiro carro) - mesma altura da seta direita
                if carro_p1 > 0:
                    seta_esquerda_temp = render_text("◄", 48, (150, 220, 255), bold=True, pixel_style=True)
                    seta_esquerda_x = 20
                    seta_esquerda_y = 100  # Mesma altura da seta direita
                    seta_esquerda_rect_p1 = pygame.Rect(seta_esquerda_x, seta_esquerda_y, seta_esquerda_temp.get_width(), seta_esquerda_temp.get_height())
                    seta_esquerda_hover = seta_esquerda_rect_p1.collidepoint(pygame.mouse.get_pos())
                    seta_esquerda_selecionada = (botao_selecionado_controle == "seta_esquerda")
                    cor_seta_esquerda = (200, 255, 255) if (seta_esquerda_hover or seta_esquerda_selecionada) else (150, 220, 255)
                    escala_seta = 1.3 if (seta_esquerda_hover or seta_esquerda_selecionada) else 1.0
                    tamanho_seta = int(48 * escala_seta)
                    seta_esquerda = render_text("◄", tamanho_seta, cor_seta_esquerda, bold=True, pixel_style=True)
                    # Ajustar posição para centralizar quando crescer
                    offset_x = (seta_esquerda.get_width() - seta_esquerda_temp.get_width()) // 2
                    offset_y = (seta_esquerda.get_height() - seta_esquerda_temp.get_height()) // 2
                    screen.blit(seta_esquerda, (seta_esquerda_x - offset_x, seta_esquerda_y - offset_y))
                    # Desenhar cursor do controle se selecionado
                    if seta_esquerda_selecionada and gerenciador_gamepad.obter_numero_controles() > 0:
                        tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                        cursor_rect = pygame.Rect(
                            seta_esquerda_rect_p1.x - tamanho_cursor,
                            seta_esquerda_rect_p1.y - tamanho_cursor,
                            seta_esquerda_rect_p1.width + tamanho_cursor * 2,
                            seta_esquerda_rect_p1.height + tamanho_cursor * 2
                        )
                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                
                # Seta direita (se não estiver no último carro) - posicionada acima dos botões
                if carro_p1 < num_carros_disponiveis - 1:
                    seta_direita_temp = render_text("►", 48, (150, 220, 255), bold=True, pixel_style=True)
                    seta_direita_x = LARGURA - 20 - seta_direita_temp.get_width()
                    seta_direita_y = 100  # Posicionada acima dos botões de confirmação
                    seta_direita_rect_p1 = pygame.Rect(seta_direita_x, seta_direita_y, seta_direita_temp.get_width(), seta_direita_temp.get_height())
                    seta_direita_hover = seta_direita_rect_p1.collidepoint(pygame.mouse.get_pos())
                    seta_direita_selecionada = (botao_selecionado_controle == "seta_direita")
                    cor_seta_direita = (200, 255, 255) if (seta_direita_hover or seta_direita_selecionada) else (150, 220, 255)
                    escala_seta = 1.3 if (seta_direita_hover or seta_direita_selecionada) else 1.0
                    tamanho_seta = int(48 * escala_seta)
                    seta_direita = render_text("►", tamanho_seta, cor_seta_direita, bold=True, pixel_style=True)
                    # Ajustar posição para centralizar quando crescer
                    offset_x = (seta_direita.get_width() - seta_direita_temp.get_width()) // 2
                    offset_y = (seta_direita.get_height() - seta_direita_temp.get_height()) // 2
                    screen.blit(seta_direita, (seta_direita_x - offset_x, seta_direita_y - offset_y))
                    # Desenhar cursor do controle se selecionado
                    if seta_direita_selecionada and gerenciador_gamepad.obter_numero_controles() > 0:
                        tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                        cursor_rect = pygame.Rect(
                            seta_direita_rect_p1.x - tamanho_cursor,
                            seta_direita_rect_p1.y - tamanho_cursor,
                            seta_direita_rect_p1.width + tamanho_cursor * 2,
                            seta_direita_rect_p1.height + tamanho_cursor * 2
                        )
                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
            
            # Informações do carro na lateral direita - retângulo otimizado
            info_x = LARGURA - 300  # Largura reduzida
            info_y = 150  # Posição ajustada (subida)
            
            # Fundo semi-transparente para as informações - tamanho otimizado
            info_largura = 280
            info_altura = info_altura_p1  # Usar a mesma altura definida para P1 (500)
            # Recriar cache se a altura mudou
            if not hasattr(selecionar_carros_loop, '_info_bg_cache') or \
               selecionar_carros_loop._info_bg_cache.get_height() != info_altura:
                info_bg = pygame.Surface((info_largura, info_altura), pygame.SRCALPHA)
                info_bg.fill((0, 0, 0, 150))
                selecionar_carros_loop._info_bg_cache = info_bg
            screen.blit(selecionar_carros_loop._info_bg_cache, (info_x, info_y))
            
            esta_desbloqueado_p1 = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
            nome_carro_display = "???" if not esta_desbloqueado_p1 else carro_atual['nome']
            
            if not hasattr(selecionar_carros_loop, '_textos_cache_p1') or selecionar_carros_loop._carro_texto_cache_p1 != carro_p1 or selecionar_carros_loop._desbloqueado_cache_p1 != esta_desbloqueado_p1:
                nome_carro_info = render_text(nome_carro_display, 24, (100, 220, 255), bold=True, pixel_style=True)
                info_titulo = render_text(t("menu.oficina.especificacoes"), 18, (255, 255, 255), bold=True, pixel_style=True)
                selecionar_carros_loop._textos_cache_p1 = (nome_carro_info, info_titulo)
                selecionar_carros_loop._carro_texto_cache_p1 = carro_p1
                selecionar_carros_loop._desbloqueado_cache_p1 = esta_desbloqueado_p1
            else:
                nome_carro_info, info_titulo = selecionar_carros_loop._textos_cache_p1
            
            # Verificar se tem upgrades do Slick para ajustar posição vertical (só no modo campanha)
            if not modo_arcade:
                slick_upgrades_pos = getattr(gerenciador_progresso, 'slick_upgrades_comprados', [])
                offset_y_slick = -10 if slick_upgrades_pos else 0  # Subir conteúdo levemente se tiver upgrades do Slick
            else:
                offset_y_slick = 0  # Modo arcade: sem offset
            
            nome_x_info = info_x + (info_largura - nome_carro_info.get_width()) // 2
            screen.blit(nome_carro_info, (nome_x_info, info_y + 15 + offset_y_slick))
            screen.blit(info_titulo, (info_x + 15, info_y + 55 + offset_y_slick))
            
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
            screen.blit(tracao_render, (info_x + 15, info_y + 90 + offset_y_slick))
            
            if not hasattr(selecionar_carros_loop, '_especs_cache') or selecionar_carros_loop._carro_cache_p1 != carro_p1:
                upgrades_carro = gerenciador_progresso.obter_todos_upgrades(carro_atual['prefixo_cor'])
                especs = calcular_especificacoes_carro(carro_atual, upgrades_carro)
                selecionar_carros_loop._especs_cache = especs
                selecionar_carros_loop._carro_cache_p1 = carro_p1
            else:
                especs = selecionar_carros_loop._especs_cache
            
            vel_max = int(especs['velocidade'])
            vel_texto = t("menu.oficina.velocidade").format(vel_max)
            vel_render = render_text(vel_texto, 16, (120, 200, 255), bold=True, pixel_style=True)
            screen.blit(vel_render, (info_x + 15, info_y + 120 + offset_y_slick))
            
            dir_valor = especs['dirigibilidade']
            dir_texto = t("menu.oficina.dirigibilidade").format(dir_valor)
            dir_render = render_text(dir_texto, 16, (140, 210, 255), bold=True, pixel_style=True)
            screen.blit(dir_render, (info_x + 15, info_y + 150 + offset_y_slick))
            
            fren_valor = especs['frenagem']
            fren_texto = t("menu.oficina.frenagem").format(fren_valor)
            fren_render = render_text(fren_texto, 16, (130, 200, 255), bold=True, pixel_style=True)
            screen.blit(fren_render, (info_x + 15, info_y + 180 + offset_y_slick))
            
            acel_valor = especs['aceleracao']
            acel_texto = t("menu.oficina.aceleracao").format(acel_valor)
            acel_render = render_text(acel_texto, 16, (160, 220, 255), bold=True, pixel_style=True)
            screen.blit(acel_render, (info_x + 15, info_y + 210 + offset_y_slick))
            
            est_valor = especs['estabilidade']
            est_texto = t("menu.oficina.estabilidade").format(est_valor)
            est_render = render_text(est_texto, 16, (150, 230, 255), bold=True, pixel_style=True)
            screen.blit(est_render, (info_x + 15, info_y + 240 + offset_y_slick))
            
            # Porcentagem de danos (P1) - sempre exibir se o carro visualizado é o equipado (exceto no modo arcade)
            if not modo_arcade:
                from core.crank import crank
                # Verificar se o carro atual está selecionado para mostrar o dano correto
                carro_atual_p1_idx = obter_carro_idx_seguro(1)
                
                # Verificar se este é o carro atual do jogador (o carro visualizado é o equipado)
                if carro_atual_p1_idx is not None and carro_atual_p1_idx == carro_p1:
                    saude_carro = crank.saude_carro if hasattr(crank, 'saude_carro') else 1.0
                    dano_percent = int((1.0 - saude_carro) * 100)
                    # Sempre exibir a saúde do carro, mesmo se não houver dano
                    if dano_percent > 0:
                        dano_texto = t("menu.oficina.dano").format(dano_percent)
                        cor_dano = (255, 150, 120) if dano_percent >= 50 else (255, 200, 120) if dano_percent >= 20 else (255, 220, 150)
                    else:
                        dano_texto = t("menu.oficina.dano").format(0)
                        cor_dano = (120, 240, 180)  # Verde para indicar que está saudável
                    dano_render = render_text(dano_texto, 16, cor_dano, bold=True, pixel_style=True)
                    screen.blit(dano_render, (info_x + 15, info_y + 270 + offset_y_slick))
                    y_slick = info_y + 300 + offset_y_slick
            else:
                y_slick = info_y + 270 + offset_y_slick
            
            # Mostrar upgrades do Slick se houver (só no modo campanha)
            if not modo_arcade:
                slick_upgrades = getattr(gerenciador_progresso, 'slick_upgrades_comprados', [])
                if slick_upgrades:
                    # Usar mesmo tamanho de fonte das outras especificações
                    slick_titulo = render_text("UPGRADES SLICK:", 16, (0, 255, 100), bold=True, pixel_style=True)
                    screen.blit(slick_titulo, (info_x + 15, y_slick))
                    
                    nomes_slick = {
                        'motor': 'Motor Experimental',
                        'filtro_ar': 'Filtro Quântico',
                        'ecu': 'ECU Alienígena',
                        'transmissao': 'Transmissão Dimensional',
                        'rodas': 'Rodas de Plasma',
                        'suspensao': 'Suspensão Antigravidade',
                        'nitro': 'Nitro Hiperespacial'
                    }
                    
                    y_slick += 25  # Espaçamento após título (igual às outras especificações)
                    max_y_slick = info_y + info_altura_p1 - 20  # Limitar dentro da caixa de especificações
                    for uid in slick_upgrades:
                        if y_slick > max_y_slick:  # Parar se ultrapassar o limite
                            break
                        for tipo, nome in nomes_slick.items():
                            if f'slick_{tipo}' in uid:
                                slick_item = render_text(f"• {nome}", 16, (0, 255, 150), bold=False, pixel_style=True)
                                screen.blit(slick_item, (info_x + 20, y_slick))
                                y_slick += 20  # Espaçamento entre itens (igual às outras especificações)
                                break
            
            esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
            preco = carro_atual.get('preco', 0)
            
            # Só exibir status se o carro estiver bloqueado
            if not esta_desbloqueado:
                status_texto = t("menu.oficina.bloqueado_preco").format(preco)
                status_color = (255, 150, 120)  # Laranja suave harmonizado
                status_render = render_text(status_texto, 20, status_color, bold=True, pixel_style=True)
                screen.blit(status_render, (info_x + 15, info_y + 300))
            
            # Borda da caixa de informações (azul ciano harmonizado)
            pygame.draw.rect(screen, (100, 220, 255), (info_x, info_y, info_largura, info_altura), 2)
            
            # Botões abaixo do retângulo de especificações (usar variáveis já calculadas)
            if esta_desbloqueado:
                if botao_usar_rect_p1:
                    usar_hover_p1 = botao_usar_rect_p1.collidepoint(pygame.mouse.get_pos())
                    usar_selecionado = carro_selecionado_p1
                    # Verificar se o carro atual está selecionado
                    carro_atual_p1 = obter_carro_idx_seguro(1)
                    carro_atual_idx = carro_p1 if carro_atual_p1 is None else carro_atual_p1
                    # Garantir comparação de inteiros
                    carro_esta_selecionado = (carro_atual_idx == carro_p1)
                    
                    selecionado_controle = (botao_selecionado_controle == "usar")
                    
                    # Se o carro está selecionado, mostrar botão REPARAR (apenas no modo campanha)
                    if carro_esta_selecionado and not modo_arcade:
                        from core.crank import crank
                        saude_carro = crank.saude_carro if hasattr(crank, 'saude_carro') else 1.0
                        if saude_carro < 1.0:
                            custo_reparo = int((1.0 - saude_carro) * 2000)
                            pode_reparar = gerenciador_progresso.tem_dinheiro(custo_reparo)
                            cor_usar = (150, 200, 150) if (usar_hover_p1 and pode_reparar) else (100, 150, 100) if pode_reparar else (150, 100, 100)
                            cor_borda_usar = (100, 220, 255)
                            cor_texto_usar = (255, 255, 255)  # Branco para destacar
                            # Se estiver em hover, mostrar o preço; senão, mostrar "Reparar"
                            if usar_hover_p1:
                                texto_botao = f"${custo_reparo}"
                            else:
                                texto_botao = t("menu.reparar")
                        else:
                            cor_usar = (50, 140, 90) if usar_hover_p1 else (40, 120, 80)
                            cor_borda_usar = (100, 200, 150)
                            cor_texto_usar = (255, 255, 255)  # Branco em vez de cinza para não parecer apagado
                            texto_botao = t("menu.oficina.usar")  # Carro já está selecionado e sem dano
                    elif carro_esta_selecionado and modo_arcade:
                        # No modo arcade, sempre mostrar "USAR" mesmo se o carro já está selecionado
                        cor_usar = (50, 140, 90) if usar_hover_p1 else (40, 120, 80)
                        cor_borda_usar = (100, 200, 150)
                        cor_texto_usar = (255, 255, 255)
                        texto_botao = t("menu.oficina.usar")
                    else:
                        # Carro não está selecionado - mostrar botão "USAR" com cores mais brilhantes
                        if usar_selecionado:
                            cor_usar = (80, 200, 120) if usar_hover_p1 else (60, 180, 100)
                            cor_borda_usar = (120, 240, 180)
                            cor_texto_usar = (255, 255, 255)
                        else:
                            cor_usar = (100, 220, 150) if usar_hover_p1 else (80, 200, 130)
                            cor_borda_usar = (140, 255, 200)
                            cor_texto_usar = (255, 255, 255)
                        texto_botao = t("menu.oficina.usar")
                    
                    pygame.draw.rect(screen, cor_usar, botao_usar_rect_p1)
                    pygame.draw.rect(screen, cor_borda_usar, botao_usar_rect_p1, 2)
                    # Desenhar cursor do controle (caixa animada)
                    if selecionado_controle and gerenciador_gamepad.obter_numero_controles() > 0:
                        # Calcular tamanho da caixa animada (cresce e diminui)
                        tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                        cursor_rect = pygame.Rect(
                            botao_usar_rect_p1.x - tamanho_cursor,
                            botao_usar_rect_p1.y - tamanho_cursor,
                            botao_usar_rect_p1.width + tamanho_cursor * 2,
                            botao_usar_rect_p1.height + tamanho_cursor * 2
                        )
                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                    # Ajustar tamanho da fonte do botão Reparar
                    # Verificar se é botão de reparar (texto é "Reparar" ou começa com "$")
                    is_reparar = (texto_botao == t("menu.reparar") or texto_botao.startswith("$"))
                    # Se estiver mostrando o preço (hover), usar fonte maior; senão, fonte menor
                    if texto_botao.startswith("$"):
                        tamanho_fonte = 16  # Fonte maior para o preço
                    elif is_reparar:
                        tamanho_fonte = 14  # Fonte menor para "Reparar"
                    else:
                        tamanho_fonte = 18  # Fonte normal para outros botões
                    texto_usar = render_text(texto_botao, tamanho_fonte, cor_texto_usar, bold=True, pixel_style=True)
                    texto_usar_x = botao_usar_rect_p1.x + (botao_usar_rect_p1.width - texto_usar.get_width()) // 2
                    texto_usar_y = botao_usar_rect_p1.y + (botao_usar_rect_p1.height - texto_usar.get_height()) // 2
                    screen.blit(texto_usar, (texto_usar_x, texto_usar_y))
                
                # Botão UPGRADE (azul ciano) - sempre traduzido
                if botao_upgrade_rect_p1:
                    upgrade_hover_p1 = botao_upgrade_rect_p1.collidepoint(pygame.mouse.get_pos())
                    selecionado_controle = (botao_selecionado_controle == "upgrade")
                    cor_upgrade = (80, 150, 200) if upgrade_hover_p1 else (60, 120, 180)
                    pygame.draw.rect(screen, cor_upgrade, botao_upgrade_rect_p1)
                    pygame.draw.rect(screen, (100, 220, 255), botao_upgrade_rect_p1, 2)
                    # Desenhar cursor do controle (caixa animada)
                    if selecionado_controle and gerenciador_gamepad.obter_numero_controles() > 0:
                        tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                        cursor_rect = pygame.Rect(
                            botao_upgrade_rect_p1.x - tamanho_cursor,
                            botao_upgrade_rect_p1.y - tamanho_cursor,
                            botao_upgrade_rect_p1.width + tamanho_cursor * 2,
                            botao_upgrade_rect_p1.height + tamanho_cursor * 2
                        )
                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                    texto_upgrade = render_text(t("menu.oficina.upgrade"), 14, (255, 255, 255), bold=True, pixel_style=True)
                    texto_upgrade_x = botao_upgrade_rect_p1.x + (botao_upgrade_rect_p1.width - texto_upgrade.get_width()) // 2
                    texto_upgrade_y = botao_upgrade_rect_p1.y + (botao_upgrade_rect_p1.height - texto_upgrade.get_height()) // 2
                    screen.blit(texto_upgrade, (texto_upgrade_x, texto_upgrade_y))
                    
                    # Desenhar ícone de notificação se houver upgrades disponíveis E ainda não visitou a tela
                    upgrades_disponiveis_e_nao_visitado = (
                        verificar_upgrades_disponiveis(carro_atual['prefixo_cor']) and
                        not gerenciador_progresso.upgrades_ja_visitado(carro_atual['prefixo_cor'])
                    )
                    if icon_exclamacao_oficina is not None and upgrades_disponiveis_e_nao_visitado:
                        # Animação de vibração (tremer) ao invés de piscar
                        vibracao_x = 2.0 * math.sin(tempo_animacao_exclamacao_oficina * 8.0)  # Vibração mais rápida
                        vibracao_y = 2.0 * math.cos(tempo_animacao_exclamacao_oficina * 8.0)  # Vibração vertical também
                        # Tamanho fixo (sem pulso)
                        icon_largura, icon_altura = icon_exclamacao_oficina.get_size()
                        # Posicionar no canto superior direito do botão
                        exclamacao_x = botao_upgrade_rect_p1.x + botao_upgrade_rect_p1.width - icon_largura - 5 + int(vibracao_x)
                        exclamacao_y = botao_upgrade_rect_p1.y + 5 + int(vibracao_y)
                        screen.blit(icon_exclamacao_oficina, (exclamacao_x, exclamacao_y))
                
                # Botão MELHORAR CARRO (dourado/amarelo) - só aparece no modo campanha
                if botao_melhorar_rect_p1:
                    melhorar_hover_p1 = botao_melhorar_rect_p1.collidepoint(pygame.mouse.get_pos())
                    selecionado_controle = (botao_selecionado_controle == "melhorar")
                    # Custo baseado no estágio atual
                    estagio_atual = gerenciador_progresso.carro_campanha_estagio
                    custo_melhoria = [5000, 10000, 15000][estagio_atual] if estagio_atual < 3 else 0
                    pode_melhorar = gerenciador_progresso.tem_dinheiro(custo_melhoria)
                    
                    if pode_melhorar:
                        cor_melhorar = (200, 180, 50) if melhorar_hover_p1 else (180, 160, 40)
                        cor_borda_melhorar = (255, 220, 100)
                        cor_texto_melhorar = (255, 255, 255)
                    else:
                        cor_melhorar = (100, 90, 40) if melhorar_hover_p1 else (80, 70, 30)
                        cor_borda_melhorar = (120, 100, 50)
                        cor_texto_melhorar = (150, 150, 150)
                    
                    pygame.draw.rect(screen, cor_melhorar, botao_melhorar_rect_p1)
                    pygame.draw.rect(screen, cor_borda_melhorar, botao_melhorar_rect_p1, 2)
                    # Desenhar cursor do controle (caixa animada)
                    if selecionado_controle and gerenciador_gamepad.obter_numero_controles() > 0:
                        tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                        cursor_rect = pygame.Rect(
                            botao_melhorar_rect_p1.x - tamanho_cursor,
                            botao_melhorar_rect_p1.y - tamanho_cursor,
                            botao_melhorar_rect_p1.width + tamanho_cursor * 2,
                            botao_melhorar_rect_p1.height + tamanho_cursor * 2
                        )
                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                    
                    # Mostrar preço no hover, senão mostrar "MELHORAR"
                    if melhorar_hover_p1:
                        texto_melhorar = render_text(f"${custo_melhoria}", 14, cor_texto_melhorar, bold=True, pixel_style=True)
                    else:
                        texto_melhorar = render_text("MELHORAR", 12, cor_texto_melhorar, bold=True, pixel_style=True)
                    texto_melhorar_x = botao_melhorar_rect_p1.x + (botao_melhorar_rect_p1.width - texto_melhorar.get_width()) // 2
                    texto_melhorar_y = botao_melhorar_rect_p1.y + (botao_melhorar_rect_p1.height - texto_melhorar.get_height()) // 2
                    screen.blit(texto_melhorar, (texto_melhorar_x, texto_melhorar_y))
                
                # Botão ESCOLHER COR (roxo/azul) - só aparece no modo campanha quando estágio >= 3
                if botao_escolher_cor_rect_p1:
                    escolher_cor_hover_p1 = botao_escolher_cor_rect_p1.collidepoint(pygame.mouse.get_pos())
                    selecionado_controle = (botao_selecionado_controle == "escolher_cor")
                    cor_escolher_cor = (150, 100, 200) if escolher_cor_hover_p1 else (120, 80, 180)
                    cor_borda_escolher_cor = (200, 150, 255)
                    cor_texto_escolher_cor = (255, 255, 255)  # Branco para garantir contraste
                    
                    pygame.draw.rect(screen, cor_escolher_cor, botao_escolher_cor_rect_p1)
                    pygame.draw.rect(screen, cor_borda_escolher_cor, botao_escolher_cor_rect_p1, 2)
                    # Desenhar cursor do controle (caixa animada)
                    if selecionado_controle and gerenciador_gamepad.obter_numero_controles() > 0:
                        tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                        cursor_rect = pygame.Rect(
                            botao_escolher_cor_rect_p1.x - tamanho_cursor,
                            botao_escolher_cor_rect_p1.y - tamanho_cursor,
                            botao_escolher_cor_rect_p1.width + tamanho_cursor * 2,
                            botao_escolher_cor_rect_p1.height + tamanho_cursor * 2
                        )
                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                    
                    # Renderizar texto "COR" com tamanho adequado
                    texto_escolher_cor = render_text("COR", 16, cor_texto_escolher_cor, bold=True, pixel_style=True)
                    if texto_escolher_cor:
                        texto_escolher_cor_x = botao_escolher_cor_rect_p1.x + (botao_escolher_cor_rect_p1.width - texto_escolher_cor.get_width()) // 2
                        texto_escolher_cor_y = botao_escolher_cor_rect_p1.y + (botao_escolher_cor_rect_p1.height - texto_escolher_cor.get_height()) // 2
                        screen.blit(texto_escolher_cor, (texto_escolher_cor_x, texto_escolher_cor_y))
                
                # Botão VENDER (vermelho) - sempre vermelho quando carro é possuído
                if botao_vender_rect_p1:
                    pode_vender = gerenciador_progresso.contar_carros_desbloqueados() > 1
                    vender_hover_p1 = botao_vender_rect_p1.collidepoint(pygame.mouse.get_pos())
                    selecionado_controle = (botao_selecionado_controle == "vender")
                    # Sempre vermelho quando pode vender, vermelho escuro quando não pode
                    if pode_vender:
                        cor_vender = (200, 100, 100) if vender_hover_p1 else (150, 80, 80)
                        cor_borda_vender = (255, 150, 150)
                        cor_texto_vender = (255, 255, 255)
                    else:
                        cor_vender = (150, 80, 80)  # Vermelho escuro quando não pode vender
                        cor_borda_vender = (200, 100, 100)
                        cor_texto_vender = (255, 255, 255)
                    pygame.draw.rect(screen, cor_vender, botao_vender_rect_p1)
                    pygame.draw.rect(screen, cor_borda_vender, botao_vender_rect_p1, 2)
                    # Desenhar cursor do controle (caixa animada)
                    if selecionado_controle and gerenciador_gamepad.obter_numero_controles() > 0:
                        tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                        cursor_rect = pygame.Rect(
                            botao_vender_rect_p1.x - tamanho_cursor,
                            botao_vender_rect_p1.y - tamanho_cursor,
                            botao_vender_rect_p1.width + tamanho_cursor * 2,
                            botao_vender_rect_p1.height + tamanho_cursor * 2
                        )
                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                    texto_vender = render_text(t("menu.oficina.vender"), 16, cor_texto_vender, bold=True, pixel_style=True)
                    texto_vender_x = botao_vender_rect_p1.x + (botao_vender_rect_p1.width - texto_vender.get_width()) // 2
                    texto_vender_y = botao_vender_rect_p1.y + (botao_vender_rect_p1.height - texto_vender.get_height()) // 2
                    screen.blit(texto_vender, (texto_vender_x, texto_vender_y))
                
                # Botão "Concluído" (verde) - sempre aparece
                if botao_concluido_rect_p1:
                    concluido_hover_p1 = botao_concluido_rect_p1.collidepoint(pygame.mouse.get_pos())
                    selecionado_controle = (botao_selecionado_controle == "concluido")
                    cor_concluido = (50, 200, 100) if concluido_hover_p1 else (40, 180, 80)
                    pygame.draw.rect(screen, cor_concluido, botao_concluido_rect_p1)
                    pygame.draw.rect(screen, (100, 255, 150), botao_concluido_rect_p1, 2)
                    # Desenhar cursor do controle (caixa animada)
                    if selecionado_controle and gerenciador_gamepad.obter_numero_controles() > 0:
                        tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                        cursor_rect = pygame.Rect(
                            botao_concluido_rect_p1.x - tamanho_cursor,
                            botao_concluido_rect_p1.y - tamanho_cursor,
                            botao_concluido_rect_p1.width + tamanho_cursor * 2,
                            botao_concluido_rect_p1.height + tamanho_cursor * 2
                        )
                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                    texto_concluido = render_text(t("menu.oficina.concluido"), 18, (255, 255, 255), bold=True, pixel_style=True)
                    texto_concluido_x = botao_concluido_rect_p1.x + (botao_concluido_rect_p1.width - texto_concluido.get_width()) // 2
                    texto_concluido_y = botao_concluido_rect_p1.y + (botao_concluido_rect_p1.height - texto_concluido.get_height()) // 2
                    screen.blit(texto_concluido, (texto_concluido_x, texto_concluido_y))
            else:
                if botao_comprar_rect_p1:
                    comprar_hover_p1 = botao_comprar_rect_p1.collidepoint(pygame.mouse.get_pos())
                    selecionado_controle = (botao_selecionado_controle == "comprar")
                    if gerenciador_progresso.tem_dinheiro(preco):
                        cor_comprar = (180, 150, 70) if comprar_hover_p1 else (150, 120, 50)
                        cor_borda_comprar = (255, 220, 100)
                        cor_texto_comprar = (255, 255, 255)
                    else:
                        cor_comprar = (50, 70, 90) if comprar_hover_p1 else (40, 60, 80)
                        cor_borda_comprar = (60, 80, 100)
                        cor_texto_comprar = (100, 100, 100)
                    pygame.draw.rect(screen, cor_comprar, botao_comprar_rect_p1)
                    pygame.draw.rect(screen, cor_borda_comprar, botao_comprar_rect_p1, 2)
                    # Desenhar cursor do controle (caixa animada)
                    if selecionado_controle and gerenciador_gamepad.obter_numero_controles() > 0:
                        tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                        cursor_rect = pygame.Rect(
                            botao_comprar_rect_p1.x - tamanho_cursor,
                            botao_comprar_rect_p1.y - tamanho_cursor,
                            botao_comprar_rect_p1.width + tamanho_cursor * 2,
                            botao_comprar_rect_p1.height + tamanho_cursor * 2
                        )
                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                    texto_comprar = render_text(t("menu.oficina.comprar"), 14, cor_texto_comprar, bold=True, pixel_style=True)
                    texto_comprar_x = botao_comprar_rect_p1.x + (botao_comprar_rect_p1.width - texto_comprar.get_width()) // 2
                    texto_comprar_y = botao_comprar_rect_p1.y + (botao_comprar_rect_p1.height - texto_comprar.get_height()) // 2
                    screen.blit(texto_comprar, (texto_comprar_x, texto_comprar_y))
                    
                    # NÃO desenhar ícone de exclamação na oficina (conforme solicitado pelo usuário)
                    # O ícone só aparece no menu principal quando há transição de "sem dinheiro" para "com dinheiro"
                
                if botao_upgrade_rect_p1:
                    upgrade_hover_p1 = botao_upgrade_rect_p1.collidepoint(pygame.mouse.get_pos())
                    selecionado_controle = (botao_selecionado_controle == "upgrade")
                    cor_upgrade = (50, 70, 90) if upgrade_hover_p1 else (40, 60, 80)
                    cor_borda = (60, 80, 100)
                    cor_texto = (100, 100, 100)
                    pygame.draw.rect(screen, cor_upgrade, botao_upgrade_rect_p1)
                    pygame.draw.rect(screen, cor_borda, botao_upgrade_rect_p1, 2)
                    # Desenhar cursor do controle (caixa animada)
                    if selecionado_controle and gerenciador_gamepad.obter_numero_controles() > 0:
                        tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                        cursor_rect = pygame.Rect(
                            botao_upgrade_rect_p1.x - tamanho_cursor,
                            botao_upgrade_rect_p1.y - tamanho_cursor,
                            botao_upgrade_rect_p1.width + tamanho_cursor * 2,
                            botao_upgrade_rect_p1.height + tamanho_cursor * 2
                        )
                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                    texto_upgrade = render_text(t("menu.oficina.upgrade"), 14, cor_texto, bold=True, pixel_style=True)
                    texto_upgrade_x = botao_upgrade_rect_p1.x + (botao_upgrade_rect_p1.width - texto_upgrade.get_width()) // 2
                    texto_upgrade_y = botao_upgrade_rect_p1.y + (botao_upgrade_rect_p1.height - texto_upgrade.get_height()) // 2
                    screen.blit(texto_upgrade, (texto_upgrade_x, texto_upgrade_y))
                
                if botao_vender_rect_p1:
                    vender_hover_p1 = botao_vender_rect_p1.collidepoint(pygame.mouse.get_pos())
                    selecionado_controle = (botao_selecionado_controle == "vender")
                    cor_vender = (100, 50, 50) if vender_hover_p1 else (80, 40, 40)
                    cor_borda_vender = (100, 50, 50)
                    cor_texto_vender = (150, 100, 100)
                    pygame.draw.rect(screen, cor_vender, botao_vender_rect_p1)
                    pygame.draw.rect(screen, cor_borda_vender, botao_vender_rect_p1, 2)
                    # Desenhar cursor do controle (caixa animada)
                    if selecionado_controle and gerenciador_gamepad.obter_numero_controles() > 0:
                        tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                        cursor_rect = pygame.Rect(
                            botao_vender_rect_p1.x - tamanho_cursor,
                            botao_vender_rect_p1.y - tamanho_cursor,
                            botao_vender_rect_p1.width + tamanho_cursor * 2,
                            botao_vender_rect_p1.height + tamanho_cursor * 2
                        )
                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                    texto_vender = render_text(t("menu.oficina.vender"), 16, cor_texto_vender, bold=True, pixel_style=True)
                    texto_vender_x = botao_vender_rect_p1.x + (botao_vender_rect_p1.width - texto_vender.get_width()) // 2
                    texto_vender_y = botao_vender_rect_p1.y + (botao_vender_rect_p1.height - texto_vender.get_height()) // 2
                    screen.blit(texto_vender, (texto_vender_x, texto_vender_y))
                
                # Botão "Concluído" sempre aparece (mesmo quando carro não é possuído)
                if botao_concluido_rect_p1:
                    concluido_hover_p1 = botao_concluido_rect_p1.collidepoint(pygame.mouse.get_pos())
                    selecionado_controle = (botao_selecionado_controle == "concluido")
                    cor_concluido = (50, 200, 100) if concluido_hover_p1 else (40, 180, 80)
                    pygame.draw.rect(screen, cor_concluido, botao_concluido_rect_p1)
                    pygame.draw.rect(screen, (100, 255, 150), botao_concluido_rect_p1, 2)
                    # Desenhar cursor do controle (caixa animada)
                    if selecionado_controle and gerenciador_gamepad.obter_numero_controles() > 0:
                        tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                        cursor_rect = pygame.Rect(
                            botao_concluido_rect_p1.x - tamanho_cursor,
                            botao_concluido_rect_p1.y - tamanho_cursor,
                            botao_concluido_rect_p1.width + tamanho_cursor * 2,
                            botao_concluido_rect_p1.height + tamanho_cursor * 2
                        )
                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                    texto_concluido = render_text(t("menu.oficina.concluido"), 18, (255, 255, 255), bold=True, pixel_style=True)
                    texto_concluido_x = botao_concluido_rect_p1.x + (botao_concluido_rect_p1.width - texto_concluido.get_width()) // 2
                    texto_concluido_y = botao_concluido_rect_p1.y + (botao_concluido_rect_p1.height - texto_concluido.get_height()) // 2
                    screen.blit(texto_concluido, (texto_concluido_x, texto_concluido_y))
            
        elif fase_selecao == 2:
            # FASE 2: Player 2 selecionando - sem subtítulo de "JOGADOR 2"
            
            # Mostrar carro do P1 já selecionado (pequeno, no canto)
            carro_p1_selecionado = CARROS_DISPONIVEIS[carro_p1]
            sprite_p1_original = sprites_carros[carro_p1_selecionado['prefixo_cor']]
            # Calcular escala mantendo proporção
            largura_desejada = 120
            altura_desejada = 60
            largura_original, altura_original = sprite_p1_original.get_size()
            escala_x = largura_desejada / largura_original
            escala_y = altura_desejada / altura_original
            escala = min(escala_x, escala_y)  # Usar a menor escala para manter proporção
            nova_largura = int(largura_original * escala)
            nova_altura = int(altura_original * escala)
            sprite_p1_temp = pygame.transform.scale(sprite_p1_original, (nova_largura, nova_altura))
            
            esta_desbloqueado_p1_selecionado = gerenciador_progresso.esta_desbloqueado(carro_p1_selecionado['prefixo_cor'])
            sprite_p1 = escurecer_sprite(sprite_p1_temp) if not esta_desbloqueado_p1_selecionado else sprite_p1_temp
            nome_p1_display = "???" if not esta_desbloqueado_p1_selecionado else carro_p1_selecionado['nome']
            
            from core.i18n import t
            screen.blit(render_text(t("jogo.p1"), 20, (255, 255, 255), bold=True, pixel_style=True), (50, 200))  # Descido para alinhar com a imagem
            screen.blit(sprite_p1, (50, 210))  # Descido mais para não ficar por cima
            screen.blit(render_text(nome_p1_display, 16, (255, 255, 255), bold=True, pixel_style=True), (50, 210 + nova_altura + 10))
            
            # Instruções removidas conforme solicitado
            
            # Indicadores de navegação (setas) para carros P2
            seta_esquerda_rect_p2 = None
            seta_direita_rect_p2 = None
            if len(CARROS_DISPONIVEIS) > 1:
                # Seta esquerda (se não estiver no primeiro carro) - mesma altura da seta direita
                if carro_p2 > 0:
                    seta_esquerda_temp = render_text("◄", 48, (150, 220, 255), bold=True, pixel_style=True)
                    seta_esquerda_x = 20
                    seta_esquerda_y = 100  # Mesma altura da seta direita
                    seta_esquerda_rect_p2 = pygame.Rect(seta_esquerda_x, seta_esquerda_y, seta_esquerda_temp.get_width(), seta_esquerda_temp.get_height())
                    seta_esquerda_hover = seta_esquerda_rect_p2.collidepoint(pygame.mouse.get_pos())
                    seta_esquerda_selecionada = (botao_selecionado_controle == "seta_esquerda")
                    cor_seta_esquerda = (200, 255, 255) if (seta_esquerda_hover or seta_esquerda_selecionada) else (150, 220, 255)
                    escala_seta = 1.3 if (seta_esquerda_hover or seta_esquerda_selecionada) else 1.0
                    tamanho_seta = int(48 * escala_seta)
                    seta_esquerda = render_text("◄", tamanho_seta, cor_seta_esquerda, bold=True, pixel_style=True)
                    # Ajustar posição para centralizar quando crescer
                    offset_x = (seta_esquerda.get_width() - seta_esquerda_temp.get_width()) // 2
                    offset_y = (seta_esquerda.get_height() - seta_esquerda_temp.get_height()) // 2
                    screen.blit(seta_esquerda, (seta_esquerda_x - offset_x, seta_esquerda_y - offset_y))
                    # Desenhar cursor do controle se selecionado
                    if seta_esquerda_selecionada and gerenciador_gamepad.obter_numero_controles() > 0:
                        tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                        cursor_rect = pygame.Rect(
                            seta_esquerda_rect_p2.x - tamanho_cursor,
                            seta_esquerda_rect_p2.y - tamanho_cursor,
                            seta_esquerda_rect_p2.width + tamanho_cursor * 2,
                            seta_esquerda_rect_p2.height + tamanho_cursor * 2
                        )
                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                
                # Seta direita (se não estiver no último carro) - posicionada acima dos botões
                if carro_p2 < len(CARROS_DISPONIVEIS) - 1:
                    seta_direita_temp = render_text("►", 48, (150, 220, 255), bold=True, pixel_style=True)
                    seta_direita_x = LARGURA - 20 - seta_direita_temp.get_width()
                    seta_direita_y = 100  # Posicionada acima dos botões de confirmação
                    seta_direita_rect_p2 = pygame.Rect(seta_direita_x, seta_direita_y, seta_direita_temp.get_width(), seta_direita_temp.get_height())
                    seta_direita_hover = seta_direita_rect_p2.collidepoint(pygame.mouse.get_pos())
                    seta_direita_selecionada = (botao_selecionado_controle == "seta_direita")
                    cor_seta_direita = (200, 255, 255) if (seta_direita_hover or seta_direita_selecionada) else (150, 220, 255)
                    escala_seta = 1.3 if (seta_direita_hover or seta_direita_selecionada) else 1.0
                    tamanho_seta = int(48 * escala_seta)
                    seta_direita = render_text("►", tamanho_seta, cor_seta_direita, bold=True, pixel_style=True)
                    # Ajustar posição para centralizar quando crescer
                    offset_x = (seta_direita.get_width() - seta_direita_temp.get_width()) // 2
                    offset_y = (seta_direita.get_height() - seta_direita_temp.get_height()) // 2
                    screen.blit(seta_direita, (seta_direita_x - offset_x, seta_direita_y - offset_y))
                    # Desenhar cursor do controle se selecionado
                    if seta_direita_selecionada and gerenciador_gamepad.obter_numero_controles() > 0:
                        tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                        cursor_rect = pygame.Rect(
                            seta_direita_rect_p2.x - tamanho_cursor,
                            seta_direita_rect_p2.y - tamanho_cursor,
                            seta_direita_rect_p2.width + tamanho_cursor * 2,
                            seta_direita_rect_p2.height + tamanho_cursor * 2
                        )
                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
            
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
                
                esta_desbloqueado_anterior = gerenciador_progresso.esta_desbloqueado(carro_anterior_obj['prefixo_cor'])
                esta_desbloqueado_atual = gerenciador_progresso.esta_desbloqueado(carro_atual_obj['prefixo_cor'])
                
                sprite_anterior_desenhar = sprites_carros_escurecidos.get(carro_anterior_obj['prefixo_cor'], sprite_anterior) if not esta_desbloqueado_anterior else sprite_anterior
                sprite_atual_desenhar = sprites_carros_escurecidos.get(carro_atual_obj['prefixo_cor'], sprite_atual) if not esta_desbloqueado_atual else sprite_atual
                
                # Desenhar carro anterior saindo (converter para int apenas na renderização)
                screen.blit(sprite_anterior_desenhar, (int(pos_x_anterior), pos_anterior[1]))
                # Desenhar novo carro entrando
                screen.blit(sprite_atual_desenhar, (int(pos_x_atual), pos_atual[1]))
                
                # Desenhar cadeado se o carro atual não estiver desbloqueado (P2)
                if not esta_desbloqueado_atual and icone_cadeado:
                    cadeado_x = int(pos_x_atual) + (sprite_atual.get_width() - icone_cadeado.get_width()) // 2
                    cadeado_y = pos_atual[1] + (sprite_atual.get_height() - icone_cadeado.get_height()) // 2
                    screen.blit(icone_cadeado, (cadeado_x, cadeado_y))
            else:
                # Sem transição: desenhar carro atual normalmente
                carro_atual = CARROS_DISPONIVEIS[carro_p2]
                sprite_atual = sprites_carros[carro_atual['prefixo_cor']]
                posicao = carro_atual.get('posicao_oficina', (LARGURA//2 - 300, 380))
                
                # Desenhar cadeado se o carro não estiver desbloqueado (P2)
                esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                sprite_atual_desenhar = sprites_carros_escurecidos.get(carro_atual['prefixo_cor'], sprite_atual) if not esta_desbloqueado else sprite_atual
                
                screen.blit(sprite_atual_desenhar, posicao)
                
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
            info_altura = 360  # Altura aumentada para acomodar o texto de dano
            if not hasattr(selecionar_carros_loop, '_info_bg_cache'):
                info_bg = pygame.Surface((info_largura, info_altura), pygame.SRCALPHA)
                info_bg.fill((0, 0, 0, 150))
                selecionar_carros_loop._info_bg_cache = info_bg
            screen.blit(selecionar_carros_loop._info_bg_cache, (info_x, info_y))
            
            # Nome do carro (acima das especificações) - estilo pixel art (azul ciano harmonizado)
            esta_desbloqueado_p2 = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
            nome_carro_display = "???" if not esta_desbloqueado_p2 else carro_atual['nome']
            nome_carro_info = render_text(nome_carro_display, 24, (100, 220, 255), bold=True, pixel_style=True)
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
            
            if not hasattr(selecionar_carros_loop, '_especs_cache_p2') or selecionar_carros_loop._carro_cache_p2 != carro_p2:
                upgrades_carro = gerenciador_progresso.obter_todos_upgrades(carro_atual['prefixo_cor'])
                especs = calcular_especificacoes_carro(carro_atual, upgrades_carro)
                selecionar_carros_loop._especs_cache_p2 = especs
                selecionar_carros_loop._carro_cache_p2 = carro_p2
            else:
                especs = selecionar_carros_loop._especs_cache_p2
            
            vel_max = int(especs['velocidade'])
            vel_texto = t("menu.oficina.velocidade").format(vel_max)
            vel_render = render_text(vel_texto, 16, (120, 200, 255), bold=True, pixel_style=True)
            screen.blit(vel_render, (info_x + 15, info_y + 120))
            
            dir_valor = especs['dirigibilidade']
            dir_texto = t("menu.oficina.dirigibilidade").format(dir_valor)
            dir_render = render_text(dir_texto, 16, (140, 210, 255), bold=True, pixel_style=True)
            screen.blit(dir_render, (info_x + 15, info_y + 150))
            
            fren_valor = especs['frenagem']
            fren_texto = t("menu.oficina.frenagem").format(fren_valor)
            fren_render = render_text(fren_texto, 16, (130, 200, 255), bold=True, pixel_style=True)
            screen.blit(fren_render, (info_x + 15, info_y + 180))
            
            acel_valor = especs['aceleracao']
            acel_texto = t("menu.oficina.aceleracao").format(acel_valor)
            acel_render = render_text(acel_texto, 16, (160, 220, 255), bold=True, pixel_style=True)
            screen.blit(acel_render, (info_x + 15, info_y + 210))
            
            est_valor = especs['estabilidade']
            est_texto = t("menu.oficina.estabilidade").format(est_valor)
            est_render = render_text(est_texto, 16, (150, 230, 255), bold=True, pixel_style=True)
            screen.blit(est_render, (info_x + 15, info_y + 240))
            
            esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
            preco = carro_atual.get('preco', 0)
            
            # Só exibir status se o carro estiver bloqueado
            if not esta_desbloqueado:
                status_texto = t("menu.oficina.bloqueado_preco").format(preco)
                status_color = (255, 150, 120)  # Laranja suave harmonizado
                status_render = render_text(status_texto, 20, status_color, bold=True, pixel_style=True)
                screen.blit(status_render, (info_x + 15, info_y + 300))
            
            # Borda da caixa de informações (azul ciano harmonizado)
            pygame.draw.rect(screen, (100, 220, 255), (info_x, info_y, info_largura, info_altura), 2)
            
            # Botões abaixo do retângulo de especificações (P2) (usar variáveis já calculadas)
            if esta_desbloqueado:
                if botao_usar_rect_p2:
                    usar_hover_p2 = botao_usar_rect_p2.collidepoint(pygame.mouse.get_pos())
                    usar_selecionado = carro_selecionado_p2
                    selecionado_controle = (botao_selecionado_controle == "usar")
                    if usar_selecionado:
                        cor_usar = (50, 140, 90) if usar_hover_p2 else (40, 120, 80)
                        cor_borda_usar = (100, 200, 150)
                        cor_texto_usar = (200, 200, 200)
                    else:
                        cor_usar = (70, 180, 120) if usar_hover_p2 else (50, 150, 100)
                        cor_borda_usar = (120, 240, 180)
                        cor_texto_usar = (255, 255, 255)
                    pygame.draw.rect(screen, cor_usar, botao_usar_rect_p2)
                    pygame.draw.rect(screen, cor_borda_usar, botao_usar_rect_p2, 2)
                    # Desenhar cursor do controle (caixa animada)
                    if selecionado_controle and gerenciador_gamepad.obter_numero_controles() > 0:
                        tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                        cursor_rect = pygame.Rect(
                            botao_usar_rect_p2.x - tamanho_cursor,
                            botao_usar_rect_p2.y - tamanho_cursor,
                            botao_usar_rect_p2.width + tamanho_cursor * 2,
                            botao_usar_rect_p2.height + tamanho_cursor * 2
                        )
                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                    texto_usar = render_text(t("menu.oficina.usar"), 18, cor_texto_usar, bold=True, pixel_style=True)
                    texto_usar_x = botao_usar_rect_p2.x + (botao_usar_rect_p2.width - texto_usar.get_width()) // 2
                    texto_usar_y = botao_usar_rect_p2.y + (botao_usar_rect_p2.height - texto_usar.get_height()) // 2
                    screen.blit(texto_usar, (texto_usar_x, texto_usar_y))
                
                # Botão UPGRADE (azul ciano)
                if botao_upgrade_rect_p2:
                    upgrade_hover_p2 = botao_upgrade_rect_p2.collidepoint(pygame.mouse.get_pos())
                    selecionado_controle = (botao_selecionado_controle == "upgrade")
                    cor_upgrade = (80, 150, 200) if upgrade_hover_p2 else (60, 120, 180)
                    pygame.draw.rect(screen, cor_upgrade, botao_upgrade_rect_p2)
                    pygame.draw.rect(screen, (100, 220, 255), botao_upgrade_rect_p2, 2)
                    # Desenhar cursor do controle (caixa animada)
                    if selecionado_controle and gerenciador_gamepad.obter_numero_controles() > 0:
                        tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                        cursor_rect = pygame.Rect(
                            botao_upgrade_rect_p2.x - tamanho_cursor,
                            botao_upgrade_rect_p2.y - tamanho_cursor,
                            botao_upgrade_rect_p2.width + tamanho_cursor * 2,
                            botao_upgrade_rect_p2.height + tamanho_cursor * 2
                        )
                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                    texto_upgrade = render_text(t("menu.oficina.upgrade"), 14, (255, 255, 255), bold=True, pixel_style=True)
                    texto_upgrade_x = botao_upgrade_rect_p2.x + (botao_upgrade_rect_p2.width - texto_upgrade.get_width()) // 2
                    texto_upgrade_y = botao_upgrade_rect_p2.y + (botao_upgrade_rect_p2.height - texto_upgrade.get_height()) // 2
                    screen.blit(texto_upgrade, (texto_upgrade_x, texto_upgrade_y))
                    
                    # Desenhar ícone de notificação se houver upgrades disponíveis
                    upgrades_disponiveis_e_nao_visitado_p2 = (
                        verificar_upgrades_disponiveis(carro_atual['prefixo_cor']) and
                        not gerenciador_progresso.upgrades_ja_visitado(carro_atual['prefixo_cor'])
                    )
                    if icon_exclamacao_oficina is not None and upgrades_disponiveis_e_nao_visitado_p2:
                        # Animação de vibração (tremer) ao invés de piscar
                        vibracao_x = 2.0 * math.sin(tempo_animacao_exclamacao_oficina * 8.0)  # Vibração mais rápida
                        vibracao_y = 2.0 * math.cos(tempo_animacao_exclamacao_oficina * 8.0)  # Vibração vertical também
                        # Tamanho fixo (sem pulso)
                        icon_largura, icon_altura = icon_exclamacao_oficina.get_size()
                        # Posicionar no canto superior direito do botão
                        exclamacao_x = botao_upgrade_rect_p2.x + botao_upgrade_rect_p2.width - icon_largura - 5 + int(vibracao_x)
                        exclamacao_y = botao_upgrade_rect_p2.y + 5 + int(vibracao_y)
                        screen.blit(icon_exclamacao_oficina, (exclamacao_x, exclamacao_y))
                
                # Botão VENDER (vermelho) - P2 - sempre vermelho quando carro é possuído
                if botao_vender_rect_p2:
                    pode_vender = gerenciador_progresso.contar_carros_desbloqueados() > 1
                    vender_hover_p2 = botao_vender_rect_p2.collidepoint(pygame.mouse.get_pos())
                    selecionado_controle = (botao_selecionado_controle == "vender")
                    # Sempre vermelho quando pode vender, vermelho escuro quando não pode
                    if pode_vender:
                        cor_vender = (200, 100, 100) if vender_hover_p2 else (150, 80, 80)
                        cor_borda_vender = (255, 150, 150)
                        cor_texto_vender = (255, 255, 255)
                    else:
                        cor_vender = (150, 80, 80)  # Vermelho escuro quando não pode vender
                        cor_borda_vender = (200, 100, 100)
                        cor_texto_vender = (255, 255, 255)
                    pygame.draw.rect(screen, cor_vender, botao_vender_rect_p2)
                    pygame.draw.rect(screen, cor_borda_vender, botao_vender_rect_p2, 2)
                    # Desenhar cursor do controle (caixa animada)
                    if selecionado_controle and gerenciador_gamepad.obter_numero_controles() > 0:
                        tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                        cursor_rect = pygame.Rect(
                            botao_vender_rect_p2.x - tamanho_cursor,
                            botao_vender_rect_p2.y - tamanho_cursor,
                            botao_vender_rect_p2.width + tamanho_cursor * 2,
                            botao_vender_rect_p2.height + tamanho_cursor * 2
                        )
                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                    texto_vender = render_text(t("menu.oficina.vender"), 16, cor_texto_vender, bold=True, pixel_style=True)
                    texto_vender_x = botao_vender_rect_p2.x + (botao_vender_rect_p2.width - texto_vender.get_width()) // 2
                    texto_vender_y = botao_vender_rect_p2.y + (botao_vender_rect_p2.height - texto_vender.get_height()) // 2
                    screen.blit(texto_vender, (texto_vender_x, texto_vender_y))
                
                # Botão "Concluído" (verde) - sempre aparece
                if botao_concluido_rect_p2:
                    concluido_hover_p2 = botao_concluido_rect_p2.collidepoint(pygame.mouse.get_pos())
                    selecionado_controle = (botao_selecionado_controle == "concluido")
                    cor_concluido = (50, 200, 100) if concluido_hover_p2 else (40, 180, 80)
                    pygame.draw.rect(screen, cor_concluido, botao_concluido_rect_p2)
                    pygame.draw.rect(screen, (100, 255, 150), botao_concluido_rect_p2, 2)
                    # Desenhar cursor do controle (caixa animada)
                    if selecionado_controle and gerenciador_gamepad.obter_numero_controles() > 0:
                        tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                        cursor_rect = pygame.Rect(
                            botao_concluido_rect_p2.x - tamanho_cursor,
                            botao_concluido_rect_p2.y - tamanho_cursor,
                            botao_concluido_rect_p2.width + tamanho_cursor * 2,
                            botao_concluido_rect_p2.height + tamanho_cursor * 2
                        )
                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                    texto_concluido = render_text(t("menu.oficina.concluido"), 18, (255, 255, 255), bold=True, pixel_style=True)
                    texto_concluido_x = botao_concluido_rect_p2.x + (botao_concluido_rect_p2.width - texto_concluido.get_width()) // 2
                    texto_concluido_y = botao_concluido_rect_p2.y + (botao_concluido_rect_p2.height - texto_concluido.get_height()) // 2
                    screen.blit(texto_concluido, (texto_concluido_x, texto_concluido_y))
            else:
                if botao_comprar_rect_p2:
                    comprar_hover_p2 = botao_comprar_rect_p2.collidepoint(pygame.mouse.get_pos())
                    selecionado_controle = (botao_selecionado_controle == "comprar")
                    if gerenciador_progresso.tem_dinheiro(preco):
                        cor_comprar = (180, 150, 70) if comprar_hover_p2 else (150, 120, 50)
                        cor_borda_comprar = (255, 220, 100)
                        cor_texto_comprar = (255, 255, 255)
                    else:
                        cor_comprar = (50, 70, 90) if comprar_hover_p2 else (40, 60, 80)
                        cor_borda_comprar = (60, 80, 100)
                        cor_texto_comprar = (100, 100, 100)
                    pygame.draw.rect(screen, cor_comprar, botao_comprar_rect_p2)
                    pygame.draw.rect(screen, cor_borda_comprar, botao_comprar_rect_p2, 2)
                    # Desenhar cursor do controle (caixa animada)
                    if selecionado_controle and gerenciador_gamepad.obter_numero_controles() > 0:
                        tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                        cursor_rect = pygame.Rect(
                            botao_comprar_rect_p2.x - tamanho_cursor,
                            botao_comprar_rect_p2.y - tamanho_cursor,
                            botao_comprar_rect_p2.width + tamanho_cursor * 2,
                            botao_comprar_rect_p2.height + tamanho_cursor * 2
                        )
                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                    texto_comprar = render_text(t("menu.oficina.comprar"), 14, cor_texto_comprar, bold=True, pixel_style=True)
                    texto_comprar_x = botao_comprar_rect_p2.x + (botao_comprar_rect_p2.width - texto_comprar.get_width()) // 2
                    texto_comprar_y = botao_comprar_rect_p2.y + (botao_comprar_rect_p2.height - texto_comprar.get_height()) // 2
                    screen.blit(texto_comprar, (texto_comprar_x, texto_comprar_y))
                    
                    # NÃO desenhar ícone de exclamação na oficina (conforme solicitado pelo usuário)
                    # O ícone só aparece no menu principal quando há transição de "sem dinheiro" para "com dinheiro"
                
                if botao_upgrade_rect_p2:
                    upgrade_hover_p2 = botao_upgrade_rect_p2.collidepoint(pygame.mouse.get_pos())
                    cor_upgrade = (50, 70, 90) if upgrade_hover_p2 else (40, 60, 80)
                    cor_borda = (60, 80, 100)
                    cor_texto = (100, 100, 100)
                    pygame.draw.rect(screen, cor_upgrade, botao_upgrade_rect_p2)
                    pygame.draw.rect(screen, cor_borda, botao_upgrade_rect_p2, 2)
                    texto_upgrade = render_text(t("menu.oficina.upgrade"), 14, cor_texto, bold=True, pixel_style=True)
                    texto_upgrade_x = botao_upgrade_rect_p2.x + (botao_upgrade_rect_p2.width - texto_upgrade.get_width()) // 2
                    texto_upgrade_y = botao_upgrade_rect_p2.y + (botao_upgrade_rect_p2.height - texto_upgrade.get_height()) // 2
                    screen.blit(texto_upgrade, (texto_upgrade_x, texto_upgrade_y))
                
                if botao_vender_rect_p2:
                    vender_hover_p2 = botao_vender_rect_p2.collidepoint(pygame.mouse.get_pos())
                    cor_vender = (100, 50, 50) if vender_hover_p2 else (80, 40, 40)
                    cor_borda_vender = (100, 50, 50)
                    cor_texto_vender = (150, 100, 100)
                    pygame.draw.rect(screen, cor_vender, botao_vender_rect_p2)
                    pygame.draw.rect(screen, cor_borda_vender, botao_vender_rect_p2, 2)
                    texto_vender = render_text(t("menu.oficina.vender"), 16, cor_texto_vender, bold=True, pixel_style=True)
                    texto_vender_x = botao_vender_rect_p2.x + (botao_vender_rect_p2.width - texto_vender.get_width()) // 2
                    texto_vender_y = botao_vender_rect_p2.y + (botao_vender_rect_p2.height - texto_vender.get_height()) // 2
                    screen.blit(texto_vender, (texto_vender_x, texto_vender_y))
                
                # Botão "Concluído" sempre aparece (mesmo quando carro não é possuído)
                if botao_concluido_rect_p2:
                    concluido_hover_p2 = botao_concluido_rect_p2.collidepoint(pygame.mouse.get_pos())
                    cor_concluido = (50, 200, 100) if concluido_hover_p2 else (40, 180, 80)
                    pygame.draw.rect(screen, cor_concluido, botao_concluido_rect_p2)
                    pygame.draw.rect(screen, (100, 255, 150), botao_concluido_rect_p2, 2)
                    texto_concluido = render_text(t("menu.oficina.concluido"), 18, (255, 255, 255), bold=True, pixel_style=True)
                    texto_concluido_x = botao_concluido_rect_p2.x + (botao_concluido_rect_p2.width - texto_concluido.get_width()) // 2
                    texto_concluido_y = botao_concluido_rect_p2.y + (botao_concluido_rect_p2.height - texto_concluido.get_height()) // 2
                    screen.blit(texto_concluido, (texto_concluido_x, texto_concluido_y))
        
        # Atualizar e desenhar popup de música
        popup_musica.atualizar(dt)
        popup_musica.desenhar(screen)
        
        # Desenhar Crank (se ativo) - tem prioridade máxima - não no modo arcade
        if not modo_arcade and crank.ativo:
            crank.desenhar_dialogo(screen, dt)
            
            # Desenhar Barão se ativo
            from core.barao import barao
            if barao.ativo:
                barao.desenhar_dialogo(screen, dt)
        
        # Desenhar menu de pause
        if oficina_pausada:
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
            
            from core.i18n import t
            titulo_texto = render_text(t("pause.titulo"), 48, (255, 255, 255), bold=True, pixel_style=True)
            titulo_x = caixa_x + (caixa_largura - titulo_texto.get_width()) // 2
            screen.blit(titulo_texto, (titulo_x, caixa_y + 20))
            
            from core.i18n import t
            opcoes_pausa = [
                (t("pause.continuar"), "continuar"),
                (t("pause.salvar"), "salvar"),
                (t("pause.opcoes"), "opcoes"),
                (t("pause.menu_principal"), "menu")
            ]
            
            altura_total_opcoes = len(opcoes_pausa) * 60
            offset_opcoes = caixa_y + caixa_altura - altura_total_opcoes - 20
            
            # Animações de hover
            if not hasattr(selecionar_carros_loop, '_hover_animation_pause'):
                selecionar_carros_loop._hover_animation_pause = [0.0] * len(opcoes_pausa)
            
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
                    selecionar_carros_loop._hover_animation_pause[i] = min(1.0, selecionar_carros_loop._hover_animation_pause[i] + hover_speed * dt)
                else:
                    selecionar_carros_loop._hover_animation_pause[i] = max(0.0, selecionar_carros_loop._hover_animation_pause[i] - hover_speed * dt)
            
            if not mouse_in_caixa:
                for i in range(len(opcoes_pausa)):
                    if i != opcao_pausa_selecionada:
                        selecionar_carros_loop._hover_animation_pause[i] = max(0.0, selecionar_carros_loop._hover_animation_pause[i] - hover_speed * dt * 1.5)
            
            # Desenhar opções
            for i, (nome, chave) in enumerate(opcoes_pausa):
                y_opcao = offset_opcoes + i * 60
                hover_progress = selecionar_carros_loop._hover_animation_pause[i]
                
                # Determinar cor baseado no estado
                if i == opcao_pausa_selecionada:
                    cor = (255, 255, 255)
                    # Desenhar cursor do controle
                    cursor_rect = pygame.Rect(caixa_x + 20, y_opcao - 5, caixa_largura - 40, 60)
                    pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                    cursor_alpha = int(128 + 127 * abs(math.sin(animacao_cursor * math.pi)))
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
        
        pygame.display.flip()

def aplicar_blur(surface, fator=4):
    """Aplica um efeito de blur simples escalando para baixo e depois para cima"""
    largura = surface.get_width()
    altura = surface.get_height()
    # Reduzir para 1/4 do tamanho
    pequena = pygame.transform.scale(surface, (max(1, largura // fator), max(1, altura // fator)))
    # Voltar para o tamanho original (cria o efeito de blur)
    blur = pygame.transform.scale(pequena, (largura, altura))
    return blur

# Cache global para sprites escurecidos
_sprite_escurecido_cache = {}

def escurecer_sprite(surface, fator=0.05):
    """Escurece um sprite quase completamente (quase preto) usando cache para performance"""
    # Usar id da superfície como chave (rápido e eficiente)
    surface_id = id(surface)
    cache_key = (surface_id, fator)
    
    # Verificar cache
    if cache_key in _sprite_escurecido_cache:
        return _sprite_escurecido_cache[cache_key]
    
    # Criar uma superfície preta com a mesma forma e aplicar alpha blending
    # Usar BLEND_MULT para escurecer mantendo a forma
    sprite_escurecido = surface.copy()
    overlay_preto = pygame.Surface(sprite_escurecido.get_size(), pygame.SRCALPHA)
    overlay_preto.fill((0, 0, 0, 240))  # Preto quase opaco (240/255 = 94% opaco)
    sprite_escurecido.blit(overlay_preto, (0, 0), special_flags=pygame.BLEND_MULT)
    
    # Armazenar no cache
    _sprite_escurecido_cache[cache_key] = sprite_escurecido
    
    # Limitar tamanho do cache (manter apenas os últimos 30)
    if len(_sprite_escurecido_cache) > 30:
        # Remover o mais antigo (primeiro item)
        chave_antiga = next(iter(_sprite_escurecido_cache))
        del _sprite_escurecido_cache[chave_antiga]
    
    return sprite_escurecido

def tela_upgrades(screen, prefixo_cor, nome_carro, fundo_garagem=None):
    """Tela de upgrades para um carro específico - estilo Need for Speed 2015"""
    from core.i18n import t
    from core.progresso import gerenciador_progresso
    from core.glub import glub
    from core.gamepad_manager import gerenciador_gamepad
    # Crank removido da tela de upgrades
    from config import DIR_PROJETO, LARGURA, ALTURA
    import os
    
    from core.narrative_system import narrative_system
    narrativa_estava_ativa = narrative_system.active
    narrative_current_scene = narrative_system.current_scene_id
    narrative_current_line = narrative_system.current_line_index
    if narrativa_estava_ativa:
        print("[TELA_UPGRADES] Narrativa estava ativa, fechando temporariamente para permitir interação com upgrades")
        # Fechar completamente a narrativa para evitar interceptação de eventos
        narrative_system.fechar()
        narrative_system.active = False
        narrative_system.current_scene_id = None
    
    # Verificar se o carro está desbloqueado
    # Garantir que Car1 sempre está desbloqueado
    carro_desbloqueado = (prefixo_cor == "Car1") or gerenciador_progresso.esta_desbloqueado(prefixo_cor)
    if not carro_desbloqueado:
        popup_musica.mostrar(t("mensagens.comprar_carro_primeiro"), tipo="outra")
        return True  # Volta para seleção de carros
    
    # Crank removido da tela de upgrades - não mostrar tutorial ou diálogos
    
    # Capturar fundo atual se não foi fornecido
    if fundo_garagem is None:
        fundo_garagem = screen.copy()
    
    upgrades_disponiveis = [
        ('motor', t("menu.upgrades.motor"), 'motor.png'),
        ('filtro_ar', t("menu.upgrades.filtro_ar"), 'filtro_de_ar.png'),
        ('ecu', t("menu.upgrades.ecu"), 'ecu.png'),
        ('transmissao', t("menu.upgrades.transmissao"), 'transmissão.png'),
        ('rodas', t("menu.upgrades.rodas"), 'rodas.png'),
        ('suspensao', t("menu.upgrades.suspensao"), 'suspensao.png'),
        ('nitro', t("menu.upgrades.nitro"), 'nitro.png')
    ]
    
    # Carregar ícones grandes
    icones_upgrades = {}
    icones_upgrades_grandes = {}
    from config import DIR_ICONS
    dir_icons = DIR_ICONS
    tamanho_icon_grande = 200  # Ícones grandes para estilo NFS
    for tipo, nome, arquivo_icon in upgrades_disponiveis:
        caminho_icon = os.path.join(dir_icons, arquivo_icon)
        if os.path.exists(caminho_icon):
            try:
                icon = pygame.image.load(caminho_icon).convert_alpha()
                icones_upgrades[tipo] = pygame.transform.scale(icon, (50, 50))
                icones_upgrades_grandes[tipo] = pygame.transform.scale(icon, (tamanho_icon_grande, tamanho_icon_grande))
            except:
                icones_upgrades[tipo] = None
                icones_upgrades_grandes[tipo] = None
        else:
            icones_upgrades[tipo] = None
            icones_upgrades_grandes[tipo] = None
    
    descricoes_upgrades = {
        'motor': t("menu.upgrades.desc_motor"),
        'filtro_ar': t("menu.upgrades.desc_filtro_ar"),
        'ecu': t("menu.upgrades.desc_ecu"),
        'transmissao': t("menu.upgrades.desc_transmissao"),
        'rodas': t("menu.upgrades.desc_rodas"),
        'suspensao': t("menu.upgrades.desc_suspensao"),
        'nitro': t("menu.upgrades.desc_nitro")
    }
    
    melhorias_upgrades = {
        'motor': t("menu.upgrades.melhorias_motor"),
        'filtro_ar': t("menu.upgrades.melhorias_filtro_ar"),
        'ecu': t("menu.upgrades.melhorias_ecu"),
        'transmissao': t("menu.upgrades.melhorias_transmissao"),
        'rodas': t("menu.upgrades.melhorias_rodas"),
        'suspensao': t("menu.upgrades.melhorias_suspensao"),
        'nitro': t("menu.upgrades.melhorias_nitro")
    }
    
    clock = pygame.time.Clock()
    upgrade_hover = None
    tooltip_timer = 0.0
    
    # Criar instância única do HUD (fora do loop para evitar recriação a cada frame)
    try:
        from core.hud import HUD
        hud_instance = HUD()
    except Exception:
        hud_instance = None
    
    # Índice do upgrade atual (navegação como na garagem)
    upgrade_atual = 0
    
    # Animação do cursor do controle
    animacao_cursor = 0.0
    velocidade_animacao_cursor = 3.0
    
    # Variáveis para transição entre upgrades
    transicao_ativa = False
    transicao_tempo = 0.0
    transicao_duracao = 0.3
    transicao_direcao = 1  # 1 = direita, -1 = esquerda
    upgrade_atual_pos = 0.0
    upgrade_proximo_pos = 1.0
    upgrade_anterior_idx = None
    
    def iniciar_transicao(direcao, upgrade_idx):
        """Inicia uma transição entre upgrades"""
        nonlocal transicao_ativa, transicao_tempo, transicao_direcao, upgrade_atual_pos, upgrade_proximo_pos, upgrade_anterior_idx
        transicao_ativa = True
        transicao_tempo = 0.0
        transicao_direcao = direcao
        upgrade_anterior_idx = upgrade_idx
        upgrade_atual_pos = 0.0
        upgrade_proximo_pos = direcao
    
    def atualizar_transicao(dt):
        """Atualiza a animação de transição"""
        nonlocal transicao_ativa, transicao_tempo, upgrade_atual_pos, upgrade_proximo_pos
        
        if not transicao_ativa:
            return
        
        transicao_tempo += dt
        
        if transicao_tempo >= transicao_duracao:
            transicao_ativa = False
            upgrade_atual_pos = 0.0
            upgrade_proximo_pos = 1.0
        else:
            progresso = transicao_tempo / transicao_duracao
            progresso = 1 - pow(1 - progresso, 3)  # Ease-out cubic
            
            upgrade_atual_pos = -transicao_direcao * progresso
            upgrade_proximo_pos = transicao_direcao * (1 - progresso)
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        
        # Atualizar transição
        atualizar_transicao(dt)
        
        # Atualizar animação do cursor do controle
        animacao_cursor += dt * velocidade_animacao_cursor
        if animacao_cursor >= 1.0:
            animacao_cursor = 0.0
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        upgrade_hover = None
        
        eventos = list(pygame.event.get())
        
        if narrative_system.active:
            print("[TELA_UPGRADES] Narrativa ainda está ativa durante loop, desativando completamente")
            narrative_system.fechar()
            narrative_system.active = False
            narrative_system.current_scene_id = None
        
        # Crank removido da tela de upgrades - upgrades são comprados diretamente
        
        # Processar Glub (se ativo) - antes de outros eventos
        if glub.ativo:
            resultado_glub = glub.processar_eventos(eventos, prefixo_cor=prefixo_cor)
            if resultado_glub in ["vendido", "recusado", "fechado"]:
                if resultado_glub == "vendido":
                    popup_musica.mostrar("Peça vendida para o Glub!", tipo="outra")
                # Continuar processando eventos normalmente
                # Filtrar eventos já processados pelo Glub (APENAS se o Glub estiver ativo)
                if glub.ativo:
                    eventos = [ev for ev in eventos if not (ev.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN))]
                    print(f"[TELA_UPGRADES] Eventos filtrados pelo Glub, restantes: {len(eventos)}")
        
        print(f"[TELA_UPGRADES] Total de eventos antes do loop: {len(eventos)}, tipos: {[ev.type for ev in eventos]}")
        
        # Definir rects das setas ANTES do loop de eventos (para que os cliques funcionem)
        seta_esquerda_rect = None
        seta_direita_rect = None
        if len(upgrades_disponiveis) > 1:
            if upgrade_atual > 0:
                seta_esquerda_temp = render_text("◄", 48, (150, 220, 255), bold=True, pixel_style=True)
                seta_esquerda_x = 50
                seta_esquerda_y = ALTURA // 2 - seta_esquerda_temp.get_height() // 2
                seta_esquerda_rect = pygame.Rect(seta_esquerda_x, seta_esquerda_y, seta_esquerda_temp.get_width(), seta_esquerda_temp.get_height())
            if upgrade_atual < len(upgrades_disponiveis) - 1:
                seta_direita_temp = render_text("►", 48, (150, 220, 255), bold=True, pixel_style=True)
                seta_direita_x = LARGURA - 50 - seta_direita_temp.get_width()
                seta_direita_y = ALTURA // 2 - seta_direita_temp.get_height() // 2
                seta_direita_rect = pygame.Rect(seta_direita_x, seta_direita_y, seta_direita_temp.get_width(), seta_direita_temp.get_height())
        
        for ev in eventos:
            print(f"[TELA_UPGRADES] Processando evento: type={ev.type}, button={ev.button if hasattr(ev, 'button') else 'N/A'}")
            if ev.type == pygame.QUIT:
                return False
            
            # Processar eventos de controle (mas não bloquear mouse)
            # Apenas processar eventos de controle, não eventos de mouse/teclado
            # Isso permite que mouse e controle funcionem independentemente
            if gerenciador_gamepad.obter_numero_controles() > 0 and ev.type in (pygame.JOYHATMOTION, pygame.JOYBUTTONDOWN, pygame.JOYAXISMOTION):
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
                # Para navegação horizontal (esquerda/direita), passar número de upgrades
                resultado_controle = processar_eventos_controle_menu(ev, upgrade_atual, len(upgrades_disponiveis), joystick_id=0, tempo_atual=tempo_atual)
                if resultado_controle:
                    acao = resultado_controle.get("acao")
                    if acao == "esquerda" and "opcao" in resultado_controle and not transicao_ativa:
                        nova_opcao = resultado_controle["opcao"]
                        if nova_opcao != upgrade_atual:
                            iniciar_transicao(-1, upgrade_atual)
                            upgrade_atual = nova_opcao
                    elif acao == "direita" and "opcao" in resultado_controle and not transicao_ativa:
                        nova_opcao = resultado_controle["opcao"]
                        if nova_opcao != upgrade_atual:
                            iniciar_transicao(1, upgrade_atual)
                            upgrade_atual = nova_opcao
                    elif acao == "confirmar":
                        # Comprar upgrade (mesma lógica do clique do mouse)
                        upgrade_atual_tipo = upgrades_disponiveis[upgrade_atual][0]
                        nivel_atual = gerenciador_progresso.obter_upgrade(prefixo_cor, upgrade_atual_tipo)
                        nivel_maximo = gerenciador_progresso.obter_nivel_maximo_upgrade()
                        if nivel_atual < nivel_maximo:
                            # Verificar fome antes de fazer upgrade
                            try:
                                from core.status_jogador import status_jogador
                                pode_fazer, mensagem = status_jogador.pode_fazer_upgrade()
                                if not pode_fazer:
                                    popup_musica.mostrar(mensagem, tipo="outra")
                                    continue
                            except Exception as e:
                                print(f"Erro ao verificar status do jogador: {e}")
                            
                            # Obter nome do upgrade e preço
                            nome_upgrade = None
                            for tipo, nome, _ in upgrades_disponiveis:
                                if tipo == upgrade_atual_tipo:
                                    nome_upgrade = nome
                                    break
                            
                            # Crank removido - calcular preço diretamente
                            preco_base = gerenciador_progresso.calcular_preco_upgrade(upgrade_atual_tipo, nivel_atual)
                            preco = preco_base
                            nivel_antigo = nivel_atual  # Salvar nível antigo antes de comprar
                            
                            # Verificar se precisa de confirmação
                            from config import CONFIGURACOES
                            precisa_confirmacao = CONFIGURACOES.get("jogo", {}).get("confirmar_upgrade", True)
                            
                            if precisa_confirmacao:
                                # Confirmação simples inline (estilo Boris) - sem Crank
                                confirmacao_ativa = True
                                opcao_confirmacao = 0  # 0 = COMPRAR, 1 = CANCELAR
                                
                                # Loop de confirmação
                                while confirmacao_ativa:
                                    dt_confirmacao = clock.tick(FPS) / 1000.0
                                    
                                    # Desenhar fundo com blur
                                    fundo_blur = aplicar_blur(fundo_garagem, fator=4)
                                    screen.blit(fundo_blur, (0, 0))
                                    overlay_transparente = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                                    overlay_transparente.fill((0, 0, 0, 100))
                                    screen.blit(overlay_transparente, (0, 0))
                                    
                                    # Desenhar caixa de confirmação (estilo Boris)
                                    caixa_largura = 500
                                    caixa_altura = 180
                                    caixa_x = (LARGURA - caixa_largura) // 2
                                    caixa_y = ALTURA - caixa_altura - 260
                                    
                                    overlay = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
                                    overlay.fill((0, 0, 0, 220))
                                    screen.blit(overlay, (caixa_x, caixa_y))
                                    pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 2)
                                    
                                    titulo = render_text(t("confirmacao.compra.titulo"), 22, (255, 255, 0), bold=True, pixel_style=True)
                                    screen.blit(titulo, (caixa_x + (caixa_largura - titulo.get_width()) // 2, caixa_y + 10))
                                    
                                    if nome_upgrade:
                                        desc = render_text(f"{nome_upgrade.upper()} nível {nivel_atual + 1}", 18, (220, 220, 220), bold=False, pixel_style=True)
                                        preco_txt = render_text(t("confirmacao.compra.preco").format(preco=preco), 18, (180, 255, 180), bold=False, pixel_style=True)
                                        screen.blit(desc, (caixa_x + 20, caixa_y + 45))
                                        screen.blit(preco_txt, (caixa_x + 20, caixa_y + 70))
                                    
                                    # Opções
                                    from core.i18n import t
                                    opcoes = [t("confirmacao.upgrade.comprar_peca"), t("confirmacao.upgrade.sair")]
                                    mouse_x_confirm, mouse_y_confirm = pygame.mouse.get_pos()
                                    
                                    # Animação do cursor do controle
                                    if not hasattr(tela_upgrades, '_animacao_cursor_confirm'):
                                        tela_upgrades._animacao_cursor_confirm = 0.0
                                    tela_upgrades._animacao_cursor_confirm += dt_confirmacao * 3.0
                                    if tela_upgrades._animacao_cursor_confirm >= 1.0:
                                        tela_upgrades._animacao_cursor_confirm = 0.0
                                    
                                    for i, texto_opcao in enumerate(opcoes):
                                        cor = (0, 200, 255) if i == opcao_confirmacao else (200, 200, 200)
                                        txt = render_text(texto_opcao, 20, cor, bold=True, pixel_style=True)
                                        y = caixa_y + 105 + i * 30
                                        rect_opcao = pygame.Rect(caixa_x + 40, y, caixa_largura - 80, 30)
                                        
                                        if rect_opcao.collidepoint(mouse_x_confirm, mouse_y_confirm):
                                            cor = (0, 200, 255)
                                            opcao_confirmacao = i
                                        
                                        screen.blit(txt, (caixa_x + 40, y))
                                        
                                        # Desenhar cursor do controle se selecionado
                                        if i == opcao_confirmacao and gerenciador_gamepad.obter_numero_controles() > 0:
                                            tamanho_cursor = 3 + int(2 * abs(math.sin(tela_upgrades._animacao_cursor_confirm * math.pi)))
                                            cursor_rect = pygame.Rect(
                                                rect_opcao.x - tamanho_cursor,
                                                rect_opcao.y - tamanho_cursor,
                                                rect_opcao.width + tamanho_cursor * 2,
                                                rect_opcao.height + tamanho_cursor * 2
                                            )
                                            pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                                    
                                    pygame.display.flip()
                                    
                                    # Processar eventos
                                    for ev_confirm in pygame.event.get():
                                        if ev_confirm.type == pygame.QUIT:
                                            return None
                                        
                                        # Processar controle primeiro
                                        controle_processado_confirm = False
                                        if gerenciador_gamepad.obter_numero_controles() > 0:
                                            tempo_atual_confirm = pygame.time.get_ticks()
                                            resultado_controle_confirm = processar_eventos_controle_menu(ev_confirm, opcao_confirmacao, len(opcoes), joystick_id=0, tempo_atual=tempo_atual_confirm)
                                            if resultado_controle_confirm:
                                                acao_confirm = resultado_controle_confirm.get("acao")
                                                if acao_confirm == "cima":
                                                    opcao_confirmacao = (opcao_confirmacao - 1) % len(opcoes)
                                                    controle_processado_confirm = True
                                                elif acao_confirm == "baixo":
                                                    opcao_confirmacao = (opcao_confirmacao + 1) % len(opcoes)
                                                    controle_processado_confirm = True
                                                elif acao_confirm == "confirmar":
                                                    if opcao_confirmacao == 0:  # COMPRAR
                                                        confirmacao_ativa = False
                                                    else:  # SAIR
                                                        confirmacao_ativa = False
                                                        continue  # Não comprar, apenas sair da confirmação
                                                elif acao_confirm == "cancelar":
                                                    confirmacao_ativa = False
                                                    continue  # Não comprar
                                        
                                        if not controle_processado_confirm:
                                            if ev_confirm.type == pygame.KEYDOWN:
                                                if ev_confirm.key in (pygame.K_UP, pygame.K_w):
                                                    opcao_confirmacao = (opcao_confirmacao - 1) % len(opcoes)
                                                elif ev_confirm.key in (pygame.K_DOWN, pygame.K_s):
                                                    opcao_confirmacao = (opcao_confirmacao + 1) % len(opcoes)
                                                elif ev_confirm.key in (pygame.K_RETURN, pygame.K_SPACE):
                                                    if opcao_confirmacao == 0:  # COMPRAR
                                                        confirmacao_ativa = False
                                                    else:  # SAIR
                                                        confirmacao_ativa = False
                                                        continue  # Não comprar
                                                elif ev_confirm.key == pygame.K_ESCAPE:
                                                    confirmacao_ativa = False
                                                    continue  # Não comprar
                                            elif ev_confirm.type == pygame.MOUSEBUTTONDOWN and ev_confirm.button == 1:
                                                mouse_x_confirm, mouse_y_confirm = pygame.mouse.get_pos()
                                                for i, texto_opcao in enumerate(opcoes):
                                                    rect_opcao = pygame.Rect(caixa_x + 40, caixa_y + 105 + i * 30, caixa_largura - 80, 30)
                                                    if rect_opcao.collidepoint(mouse_x_confirm, mouse_y_confirm):
                                                        if i == 0:  # COMPRAR
                                                            confirmacao_ativa = False
                                                        else:  # SAIR
                                                            confirmacao_ativa = False
                                                            continue  # Não comprar
                                
                                # Se cancelou, não comprar
                                if opcao_confirmacao != 0:
                                    continue
                            
                            if gerenciador_progresso.comprar_upgrade(prefixo_cor, upgrade_atual_tipo, preco):
                                # Obter nível novo após compra
                                nivel_novo = gerenciador_progresso.obter_upgrade(prefixo_cor, upgrade_atual_tipo)
                                
                                # Crank removido - não verificar reação
                                
                                # Verificar se todos os upgrades estão maximizados
                                from core.achievements import gerenciador_achievements
                                upgrades_carro = gerenciador_progresso.obter_todos_upgrades(prefixo_cor)
                                todos_maximizados = all(nivel >= 5 for nivel in upgrades_carro.values() if isinstance(nivel, int))
                                if todos_maximizados:
                                    gerenciador_achievements.atualizar_estatistica("upgrades_maximizados", incrementar=True)
                                    gerenciador_achievements.verificar_achievements(gerenciador_progresso)
                                nome_upgrade = upgrades_disponiveis[upgrade_atual][1]
                                popup_musica.mostrar(t("mensagens.upgrade_comprado").format(nome_carro, nome_upgrade), tipo="outra")
                                
                                # Verificar se o Glub deve aparecer (após compra bem-sucedida)
                                if not glub.ativo:
                                    glub.verificar_aparecer(upgrade_atual_tipo, nivel_antigo, prefixo_cor)
                            else:
                                popup_musica.mostrar(t("mensagens.dinheiro_insuficiente"), tipo="outra")
                    elif acao == "cancelar":
                        # Verificar se está no modo de instalação do primeiro upgrade
                        try:
                            from core.missoes import gerenciador_missoes
                            if gerenciador_missoes.missao_ativa_id == "m5_cirurgia_na_garagem":
                                if not gerenciador_missoes.esta_completa("m5_cirurgia_na_garagem"):
                                    # Avisar o jogador que precisa instalar o upgrade
                                    popup_musica.mostrar("Você precisa instalar o upgrade antes de sair!", tipo="outra")
                                    continue  # Não sair, continuar na tela de upgrades
                        except Exception as e:
                            pass  # Se houver erro, permitir sair normalmente
                        return True
                    continue
            
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    # Verificar se está no modo de instalação do primeiro upgrade
                    try:
                        from core.missoes import gerenciador_missoes
                        if gerenciador_missoes.missao_ativa_id == "m5_cirurgia_na_garagem":
                            if not gerenciador_missoes.esta_completa("m5_cirurgia_na_garagem"):
                                # Avisar o jogador que precisa instalar o upgrade
                                popup_musica.mostrar("Você precisa instalar o upgrade antes de sair!", tipo="outra")
                                continue  # Não sair, continuar na tela de upgrades
                    except Exception as e:
                        pass  # Se houver erro, permitir sair normalmente
                    return True
                elif ev.key in (pygame.K_LEFT, pygame.K_a) and not transicao_ativa:
                    iniciar_transicao(-1, upgrade_atual)
                    upgrade_atual = (upgrade_atual - 1) % len(upgrades_disponiveis)
                elif ev.key in (pygame.K_RIGHT, pygame.K_d) and not transicao_ativa:
                    iniciar_transicao(1, upgrade_atual)
                    upgrade_atual = (upgrade_atual + 1) % len(upgrades_disponiveis)
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                print(f"[TELA_UPGRADES] Clique detectado: mouse_x={mouse_x}, mouse_y={mouse_y}, narrative_active={narrative_system.active}, glub_active={glub.ativo}")
                
                if narrative_system.active:
                    print("[TELA_UPGRADES] Narrativa ainda está ativa durante clique, desativando completamente")
                    narrative_system.fechar()
                    narrative_system.active = False
                    narrative_system.current_scene_id = None
                
                # Crank removido - não verificar se está ativo
                
                # Não processar cliques se o Glub estiver ativo
                if glub.ativo:
                    print("[TELA_UPGRADES] Glub está ativo, ignorando clique")
                    continue
                
                # Verificar clique nas setas de navegação (rects já foram definidos antes do loop)
                if seta_esquerda_rect and seta_esquerda_rect.collidepoint(mouse_x, mouse_y) and upgrade_atual > 0 and not transicao_ativa:
                    print(f"[TELA_UPGRADES] Clique na seta esquerda detectado")
                    iniciar_transicao(-1, upgrade_atual)
                    upgrade_atual = upgrade_atual - 1
                    continue
                
                if seta_direita_rect and seta_direita_rect.collidepoint(mouse_x, mouse_y) and upgrade_atual < len(upgrades_disponiveis) - 1 and not transicao_ativa:
                    print(f"[TELA_UPGRADES] Clique na seta direita detectado")
                    iniciar_transicao(1, upgrade_atual)
                    upgrade_atual = upgrade_atual + 1
                    continue
                
                # Verificar clique no upgrade atual (apenas se não estiver em transição)
                if transicao_ativa:
                    continue
                
                upgrade_atual_tipo = upgrades_disponiveis[upgrade_atual][0]
                icon_center_x = LARGURA // 2
                icon_center_y = ALTURA // 2  # Centralizado verticalmente
                # Hitbox inclui o quadrado com blur (maior que o ícone)
                hitbox_tamanho = tamanho_icon_grande + 40  # Tamanho do quadrado com blur
                icon_rect = pygame.Rect(
                    icon_center_x - hitbox_tamanho // 2,
                    icon_center_y - hitbox_tamanho // 2,
                    hitbox_tamanho,
                    hitbox_tamanho
                )
                
                print(f"[TELA_UPGRADES] Verificando colisão: mouse=({mouse_x}, {mouse_y}), icon_rect={icon_rect}, collidepoint={icon_rect.collidepoint(mouse_x, mouse_y)}")
                if icon_rect.collidepoint(mouse_x, mouse_y):
                    print(f"[TELA_UPGRADES] Clique no ícone do upgrade {upgrade_atual_tipo} detectado")
                    nivel_atual = gerenciador_progresso.obter_upgrade(prefixo_cor, upgrade_atual_tipo)
                    nivel_maximo = gerenciador_progresso.obter_nivel_maximo_upgrade()
                    if nivel_atual < nivel_maximo:
                        # Verificar fome antes de fazer upgrade
                        try:
                            from core.status_jogador import status_jogador
                            pode_fazer, mensagem = status_jogador.pode_fazer_upgrade()
                            if not pode_fazer:
                                popup_musica.mostrar(mensagem, tipo="outra")
                                continue
                        except Exception as e:
                            print(f"Erro ao verificar status do jogador: {e}")
                        
                        # Obter nome do upgrade e preço
                        nome_upgrade = None
                        for tipo, nome, _ in upgrades_disponiveis:
                            if tipo == upgrade_atual_tipo:
                                nome_upgrade = nome
                                break
                        
                        preco_base = gerenciador_progresso.calcular_preco_upgrade(upgrade_atual_tipo, nivel_atual)
                        # Crank removido - usar preço base diretamente
                        preco = preco_base
                        nivel_antigo = nivel_atual  # Salvar nível antigo antes de comprar
                        
                        # Verificar se precisa de confirmação
                        from config import CONFIGURACOES
                        precisa_confirmacao = CONFIGURACOES.get("jogo", {}).get("confirmar_upgrade", True)
                        
                        if precisa_confirmacao:
                            # Confirmação simples inline (estilo Boris) - sem Crank
                            confirmacao_ativa = True
                            opcao_confirmacao = 0  # 0 = COMPRAR, 1 = CANCELAR
                            
                            # Loop de confirmação
                            while confirmacao_ativa:
                                dt_confirmacao = clock.tick(FPS) / 1000.0
                                
                                # Desenhar fundo com blur
                                fundo_blur = aplicar_blur(fundo_garagem, fator=4)
                                screen.blit(fundo_blur, (0, 0))
                                overlay_transparente = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                                overlay_transparente.fill((0, 0, 0, 100))
                                screen.blit(overlay_transparente, (0, 0))
                                
                                # Desenhar caixa de confirmação (estilo Boris)
                                caixa_largura = 500
                                caixa_altura = 180
                                caixa_x = (LARGURA - caixa_largura) // 2
                                caixa_y = ALTURA - caixa_altura - 260
                                
                                overlay = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
                                overlay.fill((0, 0, 0, 220))
                                screen.blit(overlay, (caixa_x, caixa_y))
                                pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 2)
                                
                                titulo = render_text("CONFIRMAÇÃO DE COMPRA", 22, (255, 255, 0), bold=True, pixel_style=True)
                                screen.blit(titulo, (caixa_x + (caixa_largura - titulo.get_width()) // 2, caixa_y + 10))
                                
                                if nome_upgrade:
                                    desc = render_text(f"{nome_upgrade.upper()} nível {nivel_atual + 1}", 18, (220, 220, 220), bold=False, pixel_style=True)
                                    from core.i18n import t
                                    preco_txt = render_text(t("confirmacao.compra.preco").format(preco=preco), 18, (180, 255, 180), bold=False, pixel_style=True)
                                    screen.blit(desc, (caixa_x + 20, caixa_y + 45))
                                    screen.blit(preco_txt, (caixa_x + 20, caixa_y + 70))
                                
                                # Opções
                                opcoes = ["COMPRAR PEÇA", "SAIR"]
                                mouse_x_confirm, mouse_y_confirm = pygame.mouse.get_pos()
                                
                                # Animação do cursor do controle
                                if not hasattr(tela_upgrades, '_animacao_cursor_confirm'):
                                    tela_upgrades._animacao_cursor_confirm = 0.0
                                tela_upgrades._animacao_cursor_confirm += dt_confirmacao * 3.0
                                if tela_upgrades._animacao_cursor_confirm >= 1.0:
                                    tela_upgrades._animacao_cursor_confirm = 0.0
                                
                                for i, texto_opcao in enumerate(opcoes):
                                    cor = (0, 200, 255) if i == opcao_confirmacao else (200, 200, 200)
                                    txt = render_text(texto_opcao, 20, cor, bold=True, pixel_style=True)
                                    y = caixa_y + 105 + i * 30
                                    rect_opcao = pygame.Rect(caixa_x + 40, y, caixa_largura - 80, 30)
                                    
                                    if rect_opcao.collidepoint(mouse_x_confirm, mouse_y_confirm):
                                        cor = (0, 200, 255)
                                        opcao_confirmacao = i
                                    
                                    screen.blit(txt, (caixa_x + 40, y))
                                    
                                    # Desenhar cursor do controle se selecionado
                                    from core.gamepad_manager import gerenciador_gamepad
                                    if i == opcao_confirmacao and gerenciador_gamepad.obter_numero_controles() > 0:
                                        tamanho_cursor = 3 + int(2 * abs(math.sin(tela_upgrades._animacao_cursor_confirm * math.pi)))
                                        cursor_rect = pygame.Rect(
                                            rect_opcao.x - tamanho_cursor,
                                            rect_opcao.y - tamanho_cursor,
                                            rect_opcao.width + tamanho_cursor * 2,
                                            rect_opcao.height + tamanho_cursor * 2
                                        )
                                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                                
                                pygame.display.flip()
                                
                                # Processar eventos
                                for ev_confirm in pygame.event.get():
                                    if ev_confirm.type == pygame.QUIT:
                                        return None
                                    
                                    # Processar controle primeiro
                                    from core.gamepad_manager import gerenciador_gamepad
                                    controle_processado_confirm = False
                                    if gerenciador_gamepad.obter_numero_controles() > 0:
                                        from core.menu_controles import processar_eventos_controle_menu
                                        tempo_atual_confirm = pygame.time.get_ticks()
                                        resultado_controle_confirm = processar_eventos_controle_menu(ev_confirm, opcao_confirmacao, len(opcoes), joystick_id=0, tempo_atual=tempo_atual_confirm)
                                        if resultado_controle_confirm:
                                            acao_confirm = resultado_controle_confirm.get("acao")
                                            if acao_confirm == "cima":
                                                opcao_confirmacao = (opcao_confirmacao - 1) % len(opcoes)
                                                controle_processado_confirm = True
                                            elif acao_confirm == "baixo":
                                                opcao_confirmacao = (opcao_confirmacao + 1) % len(opcoes)
                                                controle_processado_confirm = True
                                            elif acao_confirm == "confirmar":
                                                if opcao_confirmacao == 0:  # COMPRAR
                                                    confirmacao_ativa = False
                                                    break
                                                else:  # SAIR
                                                    confirmacao_ativa = False
                                                    opcao_confirmacao = -1  # Cancelado
                                                    break
                                            elif acao_confirm == "cancelar":
                                                confirmacao_ativa = False
                                                opcao_confirmacao = -1  # Cancelado
                                                break
                                    
                                    if controle_processado_confirm:
                                        continue
                                    
                                    elif ev_confirm.type == pygame.KEYDOWN:
                                        if ev_confirm.key in (pygame.K_UP, pygame.K_w):
                                            opcao_confirmacao = (opcao_confirmacao - 1) % len(opcoes)
                                        elif ev_confirm.key in (pygame.K_DOWN, pygame.K_s):
                                            opcao_confirmacao = (opcao_confirmacao + 1) % len(opcoes)
                                        elif ev_confirm.key in (pygame.K_RETURN, pygame.K_SPACE):
                                            if opcao_confirmacao == 0:  # COMPRAR
                                                confirmacao_ativa = False
                                                break
                                            else:  # SAIR
                                                confirmacao_ativa = False
                                                opcao_confirmacao = -1  # Cancelado
                                                break
                                        elif ev_confirm.key == pygame.K_ESCAPE:
                                            confirmacao_ativa = False
                                            opcao_confirmacao = -1  # Cancelado
                                            break
                                    elif ev_confirm.type == pygame.MOUSEBUTTONDOWN and ev_confirm.button == 1:
                                        mouse_x_confirm, mouse_y_confirm = ev_confirm.pos
                                        for i, texto_opcao in enumerate(opcoes):
                                            rect_opcao = pygame.Rect(caixa_x + 40, caixa_y + 105 + i * 30, caixa_largura - 80, 30)
                                            if rect_opcao.collidepoint(mouse_x_confirm, mouse_y_confirm):
                                                if i == 0:  # COMPRAR
                                                    confirmacao_ativa = False
                                                    break
                                                else:  # SAIR
                                                    confirmacao_ativa = False
                                                    opcao_confirmacao = -1  # Cancelado
                                                    break
                                        
                                        if not confirmacao_ativa:
                                            break
                            
                            if opcao_confirmacao != 0:  # Cancelado
                                continue  # Usuário cancelou
                        
                        # Comprar upgrade
                        if gerenciador_progresso.comprar_upgrade(prefixo_cor, upgrade_atual_tipo, preco):
                            # Obter nível novo após compra
                            nivel_novo = gerenciador_progresso.obter_upgrade(prefixo_cor, upgrade_atual_tipo)
                            
                            # Completar missão m5_cirurgia_na_garagem se estiver ativa (instalar peça na garagem)
                            try:
                                from core.missoes import gerenciador_missoes
                                if gerenciador_missoes.missao_ativa_id == "m5_cirurgia_na_garagem":
                                    gerenciador_missoes.completar_missao("m5_cirurgia_na_garagem")
                                    print("[GARAGEM] Missão 'Cirurgia na Garagem' completada após instalar upgrade!")
                            except Exception as e:
                                print(f"[GARAGEM] Erro ao completar missão: {e}")
                            
                            # Crank removido - não verificar reação
                            
                            # Tocar som de compra
                            try:
                                som_compra_path = os.path.join(DIR_PROJETO, "assets", "sounds", "purchase", "caixa.mp3")
                                if os.path.exists(som_compra_path):
                                    som_compra = pygame.mixer.Sound(som_compra_path)
                                    som_compra.play()
                            except Exception as e:
                                print(f"Erro ao tocar som de compra: {e}")
                            
                            # Verificar se todos os upgrades estão maximizados
                            from core.achievements import gerenciador_achievements
                            upgrades_carro = gerenciador_progresso.obter_todos_upgrades(prefixo_cor)
                            todos_maximizados = all(nivel >= 5 for nivel in upgrades_carro.values() if isinstance(nivel, int))
                            if todos_maximizados:
                                gerenciador_achievements.atualizar_estatistica("upgrades_maximizados", incrementar=True)
                                gerenciador_achievements.verificar_achievements(gerenciador_progresso)
                            nome_upgrade = upgrades_disponiveis[upgrade_atual][1]
                            popup_musica.mostrar(t("mensagens.upgrade_comprado").format(nome_carro, nome_upgrade), tipo="outra")
                            
                            # Verificar se o Glub deve aparecer (após compra bem-sucedida)
                            if not glub.ativo:
                                glub.verificar_aparecer(upgrade_atual_tipo, nivel_antigo, prefixo_cor)
                        else:
                            popup_musica.mostrar(t("mensagens.dinheiro_insuficiente"), tipo="outra")
                
                # Botão voltar (acima do dinheiro, no canto superior direito)
                voltar_rect = pygame.Rect(LARGURA - 150, 20, 130, 40)
                if voltar_rect.collidepoint(mouse_x, mouse_y):
                    return True
        
        # Detectar hover no upgrade atual
        upgrade_atual_tipo = upgrades_disponiveis[upgrade_atual][0]
        icon_center_x = LARGURA // 2
        icon_center_y = ALTURA // 2  # Centralizado verticalmente
        # Hitbox inclui o quadrado com blur (maior que o ícone)
        hitbox_tamanho = tamanho_icon_grande + 40  # Tamanho do quadrado com blur
        icon_rect = pygame.Rect(
            icon_center_x - hitbox_tamanho // 2,
            icon_center_y - hitbox_tamanho // 2,
            hitbox_tamanho,
            hitbox_tamanho
        )
        
        if icon_rect.collidepoint(mouse_x, mouse_y):
            upgrade_hover = upgrade_atual_tipo
            tooltip_timer += dt
        else:
            tooltip_timer = 0.0
        
        # Desenhar fundo com blur (garagem visível por trás)
        fundo_blur = aplicar_blur(fundo_garagem, fator=4)
        screen.blit(fundo_blur, (0, 0))
        
        # Overlay transparente para escurecer um pouco o fundo
        overlay_transparente = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay_transparente.fill((0, 0, 0, 100))  # Preto semi-transparente
        screen.blit(overlay_transparente, (0, 0))
        
        # Dinheiro no topo
        dinheiro_texto = t("menu.oficina.dinheiro").format(gerenciador_progresso.dinheiro)
        dinheiro_render = render_text(dinheiro_texto, 32, (255, 220, 100), bold=True, pixel_style=True)
        screen.blit(dinheiro_render, (20, 20))
        
        # Título no topo (abaixo do dinheiro)
        titulo = render_text(t("menu.upgrades.titulo").format(nome_carro), 48, (100, 220, 255), bold=True, pixel_style=True)
        titulo_x = (LARGURA - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, 80))
        
        # Desenhar upgrade atual (com transição se necessário)
        if transicao_ativa:
            # Desenhar upgrade anterior saindo
            upgrade_anterior_tipo = upgrades_disponiveis[upgrade_anterior_idx][0]
            icon_anterior = icones_upgrades_grandes.get(upgrade_anterior_tipo)
            if icon_anterior:
                x_anterior = int(LARGURA // 2 + upgrade_atual_pos * LARGURA - tamanho_icon_grande // 2)
                y_anterior = ALTURA // 2 - tamanho_icon_grande // 2  # Centralizado
                
                # Quadrado com blur preto atrás do ícone anterior
                quadrado_tamanho = tamanho_icon_grande + 40
                quadrado_surface = pygame.Surface((quadrado_tamanho, quadrado_tamanho), pygame.SRCALPHA)
                quadrado_surface.fill((0, 0, 0, 200))
                quadrado_blur = aplicar_blur(quadrado_surface, fator=2)
                screen.blit(quadrado_blur, (x_anterior - 20, y_anterior - 20))
                # Borda arredondada no quadrado anterior
                pygame.draw.rect(screen, (100, 220, 255), (x_anterior - 20, y_anterior - 20, quadrado_tamanho, quadrado_tamanho), 3, border_radius=15)
                
                screen.blit(icon_anterior, (x_anterior, y_anterior))
            
            # Desenhar upgrade atual entrando
            upgrade_atual_tipo = upgrades_disponiveis[upgrade_atual][0]
            icon_atual = icones_upgrades_grandes.get(upgrade_atual_tipo)
            if icon_atual:
                x_atual = int(LARGURA // 2 + upgrade_proximo_pos * LARGURA - tamanho_icon_grande // 2)
                y_atual = ALTURA // 2 - tamanho_icon_grande // 2  # Centralizado
                
                # Quadrado com blur preto atrás do ícone atual
                quadrado_tamanho = tamanho_icon_grande + 40
                quadrado_surface = pygame.Surface((quadrado_tamanho, quadrado_tamanho), pygame.SRCALPHA)
                quadrado_surface.fill((0, 0, 0, 200))
                quadrado_blur = aplicar_blur(quadrado_surface, fator=2)
                screen.blit(quadrado_blur, (x_atual - 20, y_atual - 20))
                # Borda arredondada no quadrado
                pygame.draw.rect(screen, (100, 220, 255), (x_atual - 20, y_atual - 20, quadrado_tamanho, quadrado_tamanho), 3, border_radius=15)
                
                # Desenhar cursor do controle (caixa animada) ao redor do upgrade atual durante transição
                if gerenciador_gamepad.obter_numero_controles() > 0:
                    tamanho_cursor = 5 + int(3 * abs(math.sin(animacao_cursor * math.pi)))
                    cursor_rect = pygame.Rect(
                        x_atual - 20 - tamanho_cursor,
                        y_atual - 20 - tamanho_cursor,
                        quadrado_tamanho + tamanho_cursor * 2,
                        quadrado_tamanho + tamanho_cursor * 2
                    )
                    pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 4, border_radius=15 + tamanho_cursor)
                
                screen.blit(icon_atual, (x_atual, y_atual))
            
            # Durante transição, não mostrar informações (apenas ícones)
        else:
            # Desenhar upgrade atual normalmente
            upgrade_atual_tipo = upgrades_disponiveis[upgrade_atual][0]
            icon_grande = icones_upgrades_grandes.get(upgrade_atual_tipo)
            
            if icon_grande:
                icon_center_x = LARGURA // 2
                icon_center_y = ALTURA // 2  # Centralizado verticalmente
                
                # Quadrado com blur preto atrás do ícone (destaque)
                quadrado_tamanho = tamanho_icon_grande + 40
                quadrado_surface = pygame.Surface((quadrado_tamanho, quadrado_tamanho), pygame.SRCALPHA)
                quadrado_surface.fill((0, 0, 0, 200))
                quadrado_blur = aplicar_blur(quadrado_surface, fator=2)
                
                # Ajustar tamanho do quadrado se hover
                if upgrade_hover == upgrade_atual_tipo:
                    escala_hover = 1.2
                    quadrado_tamanho_hover = int(quadrado_tamanho * escala_hover)
                    quadrado_surface_hover = pygame.Surface((quadrado_tamanho_hover, quadrado_tamanho_hover), pygame.SRCALPHA)
                    quadrado_surface_hover.fill((0, 0, 0, 200))
                    quadrado_blur_hover = aplicar_blur(quadrado_surface_hover, fator=2)
                    quadrado_x = int(icon_center_x - tamanho_icon_grande * escala_hover // 2 - 20)
                    quadrado_y = int(icon_center_y - tamanho_icon_grande * escala_hover // 2 - 20)
                    screen.blit(quadrado_blur_hover, (quadrado_x, quadrado_y))
                    # Borda arredondada no quadrado hover
                    pygame.draw.rect(screen, (100, 220, 255), (quadrado_x, quadrado_y, quadrado_tamanho_hover, quadrado_tamanho_hover), 3, border_radius=15)
                else:
                    quadrado_x = int(icon_center_x - tamanho_icon_grande // 2 - 20)
                    quadrado_y = int(icon_center_y - tamanho_icon_grande // 2 - 20)
                    screen.blit(quadrado_blur, (quadrado_x, quadrado_y))
                    # Borda arredondada no quadrado
                    pygame.draw.rect(screen, (100, 220, 255), (quadrado_x, quadrado_y, quadrado_tamanho, quadrado_tamanho), 3, border_radius=15)
                
                # Desenhar cursor do controle (caixa animada) ao redor do upgrade atual
                if gerenciador_gamepad.obter_numero_controles() > 0:
                    tamanho_cursor = 5 + int(3 * abs(math.sin(animacao_cursor * math.pi)))
                    cursor_rect = pygame.Rect(
                        quadrado_x - tamanho_cursor,
                        quadrado_y - tamanho_cursor,
                        quadrado_tamanho + tamanho_cursor * 2,
                        quadrado_tamanho + tamanho_cursor * 2
                    )
                    pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 4, border_radius=15 + tamanho_cursor)
                
                # Efeito de hover (aumentar tamanho)
                if upgrade_hover == upgrade_atual_tipo:
                    escala_hover = 1.2
                    icon_grande_hover = pygame.transform.scale(
                        icon_grande,
                        (int(tamanho_icon_grande * escala_hover), int(tamanho_icon_grande * escala_hover))
                    )
                    x_hover = int(icon_center_x - tamanho_icon_grande * escala_hover // 2)
                    y_hover = int(icon_center_y - tamanho_icon_grande * escala_hover // 2)
                    screen.blit(icon_grande_hover, (x_hover, y_hover))
                else:
                    x = int(icon_center_x - tamanho_icon_grande // 2)
                    y = int(icon_center_y - tamanho_icon_grande // 2)
                    screen.blit(icon_grande, (x, y))
                
                # Informações do upgrade abaixo do ícone
                nivel_atual = gerenciador_progresso.obter_upgrade(prefixo_cor, upgrade_atual_tipo)
                preco_base = gerenciador_progresso.calcular_preco_upgrade(upgrade_atual_tipo, nivel_atual)
                # Crank removido - usar preço base diretamente
                preco = preco_base
                nivel_maximo = gerenciador_progresso.obter_nivel_maximo_upgrade()
                pode_comprar = nivel_atual < nivel_maximo and gerenciador_progresso.tem_dinheiro(preco)
                
                # Nome do upgrade (afastado do ícone)
                nome = upgrades_disponiveis[upgrade_atual][1]
                nome_render = render_text(nome, 32, (255, 255, 255), bold=True, pixel_style=True)
                nome_x = int(icon_center_x - nome_render.get_width() // 2)
                nome_y = icon_center_y + tamanho_icon_grande // 2 + 80  # Mais afastado do ícone
                screen.blit(nome_render, (nome_x, nome_y))
                
                # Nível atual
                nivel_texto = t("menu.upgrades.nivel").format(nivel_atual, 5)
                nivel_render = render_text(nivel_texto, 24, (150, 220, 255), bold=True, pixel_style=True)
                nivel_x = int(icon_center_x - nivel_render.get_width() // 2)
                nivel_y = nome_y + 35
                screen.blit(nivel_render, (nivel_x, nivel_y))
                
                # Preço ou "MAX"
                if nivel_atual >= 5:
                    preco_texto = t("menu.upgrades.maximo")
                    preco_color = (150, 255, 150)
                else:
                    preco_texto = t("menu.upgrades.preco").format(preco)
                    preco_color = (255, 220, 100) if pode_comprar else (200, 100, 100)
                preco_render = render_text(preco_texto, 24, preco_color, bold=True, pixel_style=True)
                preco_x = int(icon_center_x - preco_render.get_width() // 2)
                preco_y = nivel_y + 30
                screen.blit(preco_render, (preco_x, preco_y))
        
        # Tooltip
        if upgrade_hover and tooltip_timer > 0.3:
            tooltip_x = mouse_x + 20
            tooltip_y = mouse_y - 10
            tooltip_largura = 380
            tooltip_padding = 10
            largura_texto_max = tooltip_largura - tooltip_padding * 2
            
            # Quebrar texto da descrição em linhas
            desc_texto = descricoes_upgrades[upgrade_hover]
            melhorias_texto = melhorias_upgrades[upgrade_hover]
            
            # Função auxiliar para quebrar texto
            def quebrar_texto(texto, largura_max, fonte_tamanho):
                palavras = texto.split()
                linhas = []
                linha_atual = ""
                fonte_teste = pygame.font.SysFont("consolas", fonte_tamanho, bold=True)
                
                for palavra in palavras:
                    teste = linha_atual + (" " if linha_atual else "") + palavra
                    largura_teste = fonte_teste.size(teste)[0]
                    if largura_teste <= largura_max:
                        linha_atual = teste
                    else:
                        if linha_atual:
                            linhas.append(linha_atual)
                        linha_atual = palavra
                if linha_atual:
                    linhas.append(linha_atual)
                return linhas
            
            # Quebrar descrição e melhorias
            desc_linhas = quebrar_texto(desc_texto, largura_texto_max, 16)
            melhorias_linhas = []
            for linha in melhorias_texto.split('\n'):
                melhorias_linhas.extend(quebrar_texto(linha, largura_texto_max, 14))
            
            # Calcular altura necessária
            altura_linha_desc = 20
            altura_linha_melhorias = 18
            espacamento = 5
            tooltip_altura = 10 + len(desc_linhas) * altura_linha_desc + espacamento + len(melhorias_linhas) * altura_linha_melhorias + 10
            
            # Ajustar posição se sair da tela
            if tooltip_x + tooltip_largura > LARGURA:
                tooltip_x = mouse_x - tooltip_largura - 20
            if tooltip_x < 0:
                tooltip_x = 10
            if tooltip_y + tooltip_altura > ALTURA:
                tooltip_y = ALTURA - tooltip_altura - 10
            if tooltip_y < 0:
                tooltip_y = 10
            
            # Desenhar fundo do tooltip
            tooltip_bg = pygame.Surface((tooltip_largura, tooltip_altura), pygame.SRCALPHA)
            tooltip_bg.fill((0, 0, 0, 240))
            screen.blit(tooltip_bg, (tooltip_x, tooltip_y))
            pygame.draw.rect(screen, (100, 220, 255), (tooltip_x, tooltip_y, tooltip_largura, tooltip_altura), 2, border_radius=8)
            
            # Desenhar descrição (linha por linha)
            y_offset = tooltip_padding
            for linha in desc_linhas:
                desc_render = render_text(linha, 16, (255, 255, 255), bold=True, pixel_style=True)
                screen.blit(desc_render, (tooltip_x + tooltip_padding, tooltip_y + y_offset))
                y_offset += altura_linha_desc
            
            # Espaçamento entre descrição e melhorias
            y_offset += espacamento
            
            # Desenhar melhorias (linha por linha)
            for linha in melhorias_linhas:
                melhorias_render = render_text(linha, 14, (150, 220, 255), bold=True, pixel_style=True)
                screen.blit(melhorias_render, (tooltip_x + tooltip_padding, tooltip_y + y_offset))
                y_offset += altura_linha_melhorias
        
        # Indicadores de navegação (setas) para upgrades
        seta_esquerda_rect = None
        seta_direita_rect = None
        if len(upgrades_disponiveis) > 1:
            # Seta esquerda (se não estiver no primeiro upgrade)
            if upgrade_atual > 0:
                seta_esquerda_temp = render_text("◄", 48, (150, 220, 255), bold=True, pixel_style=True)
                seta_esquerda_x = 50
                seta_esquerda_y = ALTURA // 2 - seta_esquerda_temp.get_height() // 2
                seta_esquerda_rect = pygame.Rect(seta_esquerda_x, seta_esquerda_y, seta_esquerda_temp.get_width(), seta_esquerda_temp.get_height())
                seta_esquerda_hover = seta_esquerda_rect.collidepoint(mouse_x, mouse_y)
                cor_seta_esquerda = (200, 255, 255) if seta_esquerda_hover else (150, 220, 255)
                escala_seta = 1.3 if seta_esquerda_hover else 1.0
                tamanho_seta = int(48 * escala_seta)
                seta_esquerda = render_text("◄", tamanho_seta, cor_seta_esquerda, bold=True, pixel_style=True)
                # Ajustar posição para centralizar quando crescer
                offset_x = (seta_esquerda.get_width() - seta_esquerda_temp.get_width()) // 2
                offset_y = (seta_esquerda.get_height() - seta_esquerda_temp.get_height()) // 2
                screen.blit(seta_esquerda, (seta_esquerda_x - offset_x, seta_esquerda_y - offset_y))
            
            # Seta direita (se não estiver no último upgrade)
            if upgrade_atual < len(upgrades_disponiveis) - 1:
                seta_direita_temp = render_text("►", 48, (150, 220, 255), bold=True, pixel_style=True)
                seta_direita_x = LARGURA - 50 - seta_direita_temp.get_width()
                seta_direita_y = ALTURA // 2 - seta_direita_temp.get_height() // 2
                seta_direita_rect = pygame.Rect(seta_direita_x, seta_direita_y, seta_direita_temp.get_width(), seta_direita_temp.get_height())
                seta_direita_hover = seta_direita_rect.collidepoint(mouse_x, mouse_y)
                cor_seta_direita = (200, 255, 255) if seta_direita_hover else (150, 220, 255)
                escala_seta = 1.3 if seta_direita_hover else 1.0
                tamanho_seta = int(48 * escala_seta)
                seta_direita = render_text("►", tamanho_seta, cor_seta_direita, bold=True, pixel_style=True)
                # Ajustar posição para centralizar quando crescer
                offset_x = (seta_direita.get_width() - seta_direita_temp.get_width()) // 2
                offset_y = (seta_direita.get_height() - seta_direita_temp.get_height()) // 2
                screen.blit(seta_direita, (seta_direita_x - offset_x, seta_direita_y - offset_y))
        
        popup_musica.atualizar(dt)
        popup_musica.desenhar(screen)
        
        # Desenhar rastreador de missão no canto superior direito (apenas em modo campanha)
        try:
            from core.missoes import gerenciador_missoes
            from config import LARGURA
            if hud_instance is not None:
                hud_instance.desenhar_missao_ativa(screen, posicao=(LARGURA - 20, 10), alinhar_direita=True)
        except Exception as e:
            pass  # Silenciosamente falhar se o sistema de missões não estiver disponível
        
        # Crank removido da tela de upgrades - não desenhar
        # Desenhar Glub (se ativo e Crank não estiver ativo) - APENAS no modo arcade, não na campanha
        # O Glub só deve aparecer na narrativa, não na oficina do modo campanha
        # elif glub.ativo:
        #     glub.desenhar_dialogo(screen, dt)
        
        pygame.display.flip()
    
    # Restaurar estado da narrativa se estava ativa antes de entrar na tela de upgrades
    if narrativa_estava_ativa:
        print("[TELA_UPGRADES] Restaurando estado da narrativa após sair da tela de upgrades")
        narrative_system.active = narrativa_estava_ativa

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
    
    # Variáveis para barra deslizante de volume
    volume_dragging = False
    volume_bar_width = 200
    volume_bar_height = 8
    volume_indicator_size = 16

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
                
                # Verificar clique na barra de volume
                volume_idx = -1
                for i, (nome, chave) in enumerate(opcoes_audio):
                    if chave == "volume_musica":
                        volume_idx = i
                        break
                
                if volume_idx >= 0:
                    y_volume = caixa_y + 80 + volume_idx * 50
                    volume_bar_x = caixa_x + 250
                    volume_bar_y = y_volume + 10
                    volume_bar_rect = pygame.Rect(volume_bar_x, volume_bar_y - volume_bar_height // 2, volume_bar_width, volume_bar_height)
                    
                    # Verificar se clicou na barra ou no indicador
                    volume_value = CONFIGURACOES["audio"]["volume_musica"]
                    indicator_x = volume_bar_x + int(volume_value * volume_bar_width) - volume_indicator_size // 2
                    indicator_rect = pygame.Rect(indicator_x, volume_bar_y - volume_indicator_size // 2, volume_indicator_size, volume_indicator_size)
                    
                    if volume_bar_rect.collidepoint(mouse_x, mouse_y) or indicator_rect.collidepoint(mouse_x, mouse_y):
                        volume_dragging = True
                        # Atualizar volume baseado na posição do clique
                        relative_x = mouse_x - volume_bar_x
                        new_volume = max(0.0, min(1.0, relative_x / volume_bar_width))
                        CONFIGURACOES["audio"]["volume_musica"] = new_volume
                        salvar_configuracoes()
                        # Atualizar volume no gerenciador de música
                        try:
                            from core.musica import gerenciador_musica
                            gerenciador_musica.definir_volume(new_volume)
                        except:
                            pass
                    else:
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
                else:
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
            
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                volume_dragging = False
            
            elif ev.type == pygame.MOUSEMOTION:
                if volume_dragging:
                    mouse_x = ev.pos[0]
                    volume_idx = -1
                    for i, (nome, chave) in enumerate(opcoes_audio):
                        if chave == "volume_musica":
                            volume_idx = i
                            break
                    
                    if volume_idx >= 0:
                        y_volume = caixa_y + 80 + volume_idx * 50
                        volume_bar_x = caixa_x + 250
                        relative_x = mouse_x - volume_bar_x
                        new_volume = max(0.0, min(1.0, relative_x / volume_bar_width))
                        CONFIGURACOES["audio"]["volume_musica"] = new_volume
                        salvar_configuracoes()
                        # Atualizar volume no gerenciador de música
                        try:
                            from core.musica import gerenciador_musica
                            gerenciador_musica.definir_volume(new_volume)
                        except:
                            pass
            # Processar eventos de controle
            if gerenciador_gamepad.obter_numero_controles() > 0:
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
                resultado_controle = processar_eventos_controle_menu(ev, opcao_atual, len(opcoes_audio), joystick_id=0, tempo_atual=tempo_atual)
                if resultado_controle:
                    acao = resultado_controle.get("acao")
                    if acao == "cima" and "opcao" in resultado_controle:
                        opcao_atual = resultado_controle["opcao"]
                    elif acao == "baixo" and "opcao" in resultado_controle:
                        opcao_atual = resultado_controle["opcao"]
                    elif acao == "esquerda":
                        # Ajustar volume para baixo se estiver na opção de volume
                        chave = opcoes_audio[opcao_atual][1]
                        if chave == "volume_musica":
                            CONFIGURACOES["audio"]["volume_musica"] = max(0.0, CONFIGURACOES["audio"]["volume_musica"] - 0.1)
                            salvar_configuracoes()
                            try:
                                from core.musica import gerenciador_musica
                                gerenciador_musica.definir_volume(CONFIGURACOES["audio"]["volume_musica"])
                            except:
                                pass
                    elif acao == "direita":
                        # Ajustar volume para cima se estiver na opção de volume
                        chave = opcoes_audio[opcao_atual][1]
                        if chave == "volume_musica":
                            CONFIGURACOES["audio"]["volume_musica"] = min(1.0, CONFIGURACOES["audio"]["volume_musica"] + 0.1)
                            salvar_configuracoes()
                            try:
                                from core.musica import gerenciador_musica
                                gerenciador_musica.definir_volume(CONFIGURACOES["audio"]["volume_musica"])
                            except:
                                pass
                    elif acao == "confirmar":
                        # Processar ação da opção atual
                        chave = opcoes_audio[opcao_atual][1]
                        if chave in ["musica_habilitada", "musica_no_menu", "musica_no_jogo", "musica_aleatoria"]:
                            CONFIGURACOES["audio"][chave] = not CONFIGURACOES["audio"][chave]
                            salvar_configuracoes()
                        elif chave == "voltar":
                            return True
                    elif acao == "cancelar":
                        return True
                    continue
            
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
                        try:
                            from core.musica import gerenciador_musica
                            gerenciador_musica.definir_volume(CONFIGURACOES["audio"]["volume_musica"])
                        except:
                            pass
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    if opcoes_audio[opcao_atual][1] == "volume_musica":
                        CONFIGURACOES["audio"]["volume_musica"] = min(1.0, CONFIGURACOES["audio"]["volume_musica"] + 0.1)
                        salvar_configuracoes()
                        try:
                            from core.musica import gerenciador_musica
                            gerenciador_musica.definir_volume(CONFIGURACOES["audio"]["volume_musica"])
                        except:
                            pass

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
                screen.blit(texto, (caixa_x + 30, y))
            elif chave == "volume_musica":
                texto = render_text(f"{nome}:", 20, cor_texto, bold=True, pixel_style=True)
                screen.blit(texto, (caixa_x + 30, y))
                
                # Desenhar barra deslizante de volume
                volume_bar_x = caixa_x + 250
                volume_bar_y = y + 10
                volume_value = CONFIGURACOES["audio"]["volume_musica"]
                
                # Barra de fundo
                pygame.draw.rect(screen, (50, 50, 50), (volume_bar_x, volume_bar_y - volume_bar_height // 2, volume_bar_width, volume_bar_height))
                pygame.draw.rect(screen, (100, 100, 100), (volume_bar_x, volume_bar_y - volume_bar_height // 2, volume_bar_width, volume_bar_height), 1)
                
                # Barra preenchida (indicando volume atual)
                filled_width = int(volume_value * volume_bar_width)
                if filled_width > 0:
                    pygame.draw.rect(screen, (0, 200, 255), (volume_bar_x, volume_bar_y - volume_bar_height // 2, filled_width, volume_bar_height))
                
                # Indicador (bolinha)
                indicator_x = volume_bar_x + int(volume_value * volume_bar_width) - volume_indicator_size // 2
                indicator_color = (220, 220, 220) if volume_dragging else (180, 180, 180)
                pygame.draw.circle(screen, indicator_color, (indicator_x + volume_indicator_size // 2, volume_bar_y), volume_indicator_size // 2)
                pygame.draw.circle(screen, (255, 255, 255), (indicator_x + volume_indicator_size // 2, volume_bar_y), volume_indicator_size // 2, 2)
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
    scroll_dragging = False
    scroll_drag_start_y = 0
    scroll_drag_start_offset = 0.0
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

                # Verificar clique na scrollbar
                if max_scroll > 0:
                    scrollbar_width = 12
                    scrollbar_x = caixa_x + caixa_largura - scrollbar_width - 5
                    scrollbar_y = caixa_y + 80
                    scrollbar_height = altura_area_visivel
                    scrollbar_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
                    if scrollbar_rect.collidepoint(mouse_x, mouse_y):
                        scroll_dragging = True
                        scroll_drag_start_y = mouse_y
                        scroll_drag_start_offset = scroll_offset
                    else:
                        # clique nas opções (respeitando scroll)
                        idx = verificar_clique_opcao(
                            mouse_x, mouse_y, opcoes_controles,
                            caixa_x, caixa_y, caixa_largura,
                            altura_item, 80, None, scroll_offset
                        )
                        if idx >= 0:
                            opcao_atual = idx
                else:
                    # clique nas opções (respeitando scroll)
                    idx = verificar_clique_opcao(
                        mouse_x, mouse_y, opcoes_controles,
                        caixa_x, caixa_y, caixa_largura,
                        altura_item, 80, None, scroll_offset
                    )
                    if idx >= 0:
                        opcao_atual = idx

            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                scroll_dragging = False

            elif ev.type == pygame.MOUSEMOTION:
                if scroll_dragging and max_scroll > 0:
                    mouse_y = ev.pos[1]
                    delta_y = mouse_y - scroll_drag_start_y
                    scrollbar_height = altura_area_visivel
                    indicator_height = max(30, int(scrollbar_height * 0.3))
                    scroll_max = scrollbar_height - indicator_height
                    if scroll_max > 0:
                        scroll_ratio = delta_y / scroll_max
                        new_offset = scroll_drag_start_offset + (scroll_ratio * max_scroll)
                        scroll_offset = max(0, min(max_scroll, new_offset))

            elif ev.type == pygame.MOUSEWHEEL:
                scroll_offset = max(0, min(max_scroll, scroll_offset - ev.y * 30))

            # Processar eventos de controle
            if gerenciador_gamepad.obter_numero_controles() > 0:
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
                resultado_controle = processar_eventos_controle_menu(ev, opcao_atual, len(opcoes_controles), joystick_id=0, tempo_atual=tempo_atual)
                if resultado_controle:
                    acao = resultado_controle.get("acao")
                    if acao == "cima" and "opcao" in resultado_controle:
                        nova_opcao = resultado_controle["opcao"]
                        if nova_opcao != opcao_atual:
                            opcao_atual = nova_opcao
                            # Ajustar scroll para seguir a opção selecionada
                            altura_total_opcoes = len(opcoes_controles) * altura_item
                            altura_area_visivel = caixa_altura - 200
                            max_scroll = max(0, altura_total_opcoes - altura_area_visivel)
                            # Calcular posição Y da opção na lista (sem scroll)
                            opcao_y_lista = opcao_atual * altura_item
                            # Área visível: de 0 até altura_area_visivel (sem sobrepor o botão voltar)
                            topo_area_visivel = 0
                            fundo_area_visivel = altura_area_visivel
                            # Calcular posição Y da opção na tela (considerando scroll atual)
                            opcao_y_tela = opcao_y_lista - scroll_offset
                            # Ajustar scroll se necessário
                            if opcao_y_tela < topo_area_visivel:
                                # Opção está acima da área visível - aumentar scroll para que ela apareça
                                scroll_offset = opcao_y_lista - topo_area_visivel
                            elif opcao_y_tela + altura_item > fundo_area_visivel:
                                # Opção está abaixo da área visível - diminuir scroll para que ela apareça
                                scroll_offset = opcao_y_lista + altura_item - fundo_area_visivel
                            # Garantir que scroll está dentro dos limites
                            scroll_offset = max(0, min(max_scroll, scroll_offset))
                    elif acao == "baixo" and "opcao" in resultado_controle:
                        nova_opcao = resultado_controle["opcao"]
                        if nova_opcao != opcao_atual:
                            opcao_atual = nova_opcao
                            # Ajustar scroll para seguir a opção selecionada
                            altura_total_opcoes = len(opcoes_controles) * altura_item
                            altura_area_visivel = caixa_altura - 200
                            max_scroll = max(0, altura_total_opcoes - altura_area_visivel)
                            # Calcular posição Y da opção na lista (sem scroll)
                            opcao_y_lista = opcao_atual * altura_item
                            # Área visível: de 0 até altura_area_visivel (sem sobrepor o botão voltar)
                            topo_area_visivel = 0
                            fundo_area_visivel = altura_area_visivel
                            # Calcular posição Y da opção na tela (considerando scroll atual)
                            opcao_y_tela = opcao_y_lista - scroll_offset
                            # Ajustar scroll se necessário
                            if opcao_y_tela < topo_area_visivel:
                                # Opção está acima da área visível - aumentar scroll para que ela apareça
                                scroll_offset = opcao_y_lista - topo_area_visivel
                            elif opcao_y_tela + altura_item > fundo_area_visivel:
                                # Opção está abaixo da área visível - diminuir scroll para que ela apareça
                                scroll_offset = opcao_y_lista + altura_item - fundo_area_visivel
                            # Garantir que scroll está dentro dos limites
                            scroll_offset = max(0, min(max_scroll, scroll_offset))
                    elif acao == "confirmar":
                        if opcao_atual >= len(opcoes_controles) - 1:
                            return True
                    elif acao == "cancelar":
                        return True
            
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
            desenhar_scrollbar(screen, scroll_offset, max_scroll, caixa_x, caixa_y, caixa_largura, caixa_altura, scroll_dragging)

        pygame.display.flip()

def mostrar_dialogo_confirmacao_compra_carro(screen, bg, nome_carro, preco):
    """Mostra diálogo modal de confirmação para comprar um carro"""
    from config import LARGURA, ALTURA, FPS
    from core.i18n import t
    from core.gamepad_manager import gerenciador_gamepad
    from core.menu_controles import processar_eventos_controle_menu
    
    clock = pygame.time.Clock()
    opcao_selecionada = 0  # 0 = COMPRAR, 1 = CANCELAR
    
    # Variáveis para os botões
    caixa_largura = 500
    caixa_altura = 180
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = ALTURA - caixa_altura - 260
    
    animacao_cursor = 0.0
    
    # Aplicar blur no fundo
    try:
        # aplicar_blur está no mesmo arquivo, então podemos chamá-la diretamente
        fundo_blur = aplicar_blur(bg, fator=4)
    except:
        fundo_blur = bg
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        animacao_cursor += dt * 3.0
        if animacao_cursor >= 1.0:
            animacao_cursor = 0.0
        
        # Desenhar fundo com blur
        screen.blit(fundo_blur, (0, 0))
        overlay_transparente = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay_transparente.fill((0, 0, 0, 100))
        screen.blit(overlay_transparente, (0, 0))
        
        # Desenhar caixa de confirmação
        overlay = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (caixa_x, caixa_y))
        pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 2)
        
        titulo = render_text("CONFIRMAÇÃO DE COMPRA", 22, (255, 255, 0), bold=True, pixel_style=True)
        screen.blit(titulo, (caixa_x + (caixa_largura - titulo.get_width()) // 2, caixa_y + 10))
        
        from core.i18n import t
        desc = render_text(f"{nome_carro.upper()}", 18, (220, 220, 220), bold=False, pixel_style=True)
        preco_txt = render_text(t("confirmacao.compra.preco").format(preco=preco), 18, (180, 255, 180), bold=False, pixel_style=True)
        screen.blit(desc, (caixa_x + 20, caixa_y + 45))
        screen.blit(preco_txt, (caixa_x + 20, caixa_y + 70))
        
        # Opções
        from core.i18n import t
        opcoes = [t("confirmacao.compra.comprar_carro"), t("menu.cancelar")]
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        for i, texto_opcao in enumerate(opcoes):
            cor = (0, 200, 255) if i == opcao_selecionada else (200, 200, 200)
            txt = render_text(texto_opcao, 20, cor, bold=True, pixel_style=True)
            y = caixa_y + 105 + i * 30
            rect_opcao = pygame.Rect(caixa_x + 40, y, caixa_largura - 80, 30)
            
            if rect_opcao.collidepoint(mouse_x, mouse_y):
                cor = (0, 200, 255)
                opcao_selecionada = i
            
            screen.blit(txt, (caixa_x + 40, y))
            
            # Desenhar cursor do controle se selecionado
            if i == opcao_selecionada and gerenciador_gamepad.obter_numero_controles() > 0:
                tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                cursor_rect = pygame.Rect(
                    rect_opcao.x - tamanho_cursor,
                    rect_opcao.y - tamanho_cursor,
                    rect_opcao.width + tamanho_cursor * 2,
                    rect_opcao.height + tamanho_cursor * 2
                )
                pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
        
        pygame.display.flip()
        
        # Processar eventos
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            
            # Processar controle primeiro
            controle_processado = False
            if gerenciador_gamepad.obter_numero_controles() > 0:
                tempo_atual = pygame.time.get_ticks()
                resultado_controle = processar_eventos_controle_menu(ev, opcao_selecionada, len(opcoes), joystick_id=0, tempo_atual=tempo_atual)
                if resultado_controle:
                    acao = resultado_controle.get("acao")
                    if acao == "cima":
                        opcao_selecionada = (opcao_selecionada - 1) % len(opcoes)
                        controle_processado = True
                    elif acao == "baixo":
                        opcao_selecionada = (opcao_selecionada + 1) % len(opcoes)
                        controle_processado = True
                    elif acao == "confirmar":
                        if opcao_selecionada == 0:  # COMPRAR
                            return True
                        else:  # CANCELAR
                            return False
                    elif acao == "cancelar":
                        return False
            
            if not controle_processado:
                if ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_UP, pygame.K_w):
                        opcao_selecionada = (opcao_selecionada - 1) % len(opcoes)
                    elif ev.key in (pygame.K_DOWN, pygame.K_s):
                        opcao_selecionada = (opcao_selecionada + 1) % len(opcoes)
                    elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        return opcao_selecionada == 0  # COMPRAR = True, CANCELAR = False
                    elif ev.key == pygame.K_ESCAPE:
                        return False  # Cancelar
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for i, texto_opcao in enumerate(opcoes):
                        rect_opcao = pygame.Rect(caixa_x + 40, caixa_y + 105 + i * 30, caixa_largura - 80, 30)
                        if rect_opcao.collidepoint(mouse_x, mouse_y):
                            return i == 0  # COMPRAR = True, CANCELAR = False

def mostrar_dialogo_confirmacao_venda_carro(screen, bg, nome_carro, preco_venda):
    """Mostra diálogo modal de confirmação para vender um carro"""
    from config import LARGURA, ALTURA, FPS
    from core.i18n import t
    from core.gamepad_manager import gerenciador_gamepad
    from core.menu_controles import processar_eventos_controle_menu
    
    clock = pygame.time.Clock()
    opcao_selecionada = 0  # 0 = VENDER, 1 = CANCELAR
    
    # Variáveis para os botões
    caixa_largura = 500
    caixa_altura = 180
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = ALTURA - caixa_altura - 260
    
    animacao_cursor = 0.0
    
    # Aplicar blur no fundo
    try:
        # aplicar_blur está no mesmo arquivo, então podemos chamá-la diretamente
        fundo_blur = aplicar_blur(bg, fator=4)
    except:
        fundo_blur = bg
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        animacao_cursor += dt * 3.0
        if animacao_cursor >= 1.0:
            animacao_cursor = 0.0
        
        # Desenhar fundo com blur
        screen.blit(fundo_blur, (0, 0))
        overlay_transparente = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay_transparente.fill((0, 0, 0, 100))
        screen.blit(overlay_transparente, (0, 0))
        
        # Desenhar caixa de confirmação
        overlay = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (caixa_x, caixa_y))
        pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 2)
        
        titulo = render_text(t("confirmacao.venda.titulo"), 22, (255, 200, 0), bold=True, pixel_style=True)
        screen.blit(titulo, (caixa_x + (caixa_largura - titulo.get_width()) // 2, caixa_y + 10))
        
        desc = render_text(f"{nome_carro.upper()}", 18, (220, 220, 220), bold=False, pixel_style=True)
        from core.i18n import t
        preco_txt = render_text(t("confirmacao.venda.valor_venda").format(preco_venda=preco_venda), 18, (255, 180, 180), bold=False, pixel_style=True)
        screen.blit(desc, (caixa_x + 20, caixa_y + 45))
        screen.blit(preco_txt, (caixa_x + 20, caixa_y + 70))
        
        # Opções
        from core.i18n import t
        opcoes = [t("confirmacao.venda.vender_carro"), t("menu.cancelar")]
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        for i, texto_opcao in enumerate(opcoes):
            cor = (255, 150, 150) if i == opcao_selecionada else (200, 200, 200)
            txt = render_text(texto_opcao, 20, cor, bold=True, pixel_style=True)
            y = caixa_y + 105 + i * 30
            rect_opcao = pygame.Rect(caixa_x + 40, y, caixa_largura - 80, 30)
            
            if rect_opcao.collidepoint(mouse_x, mouse_y):
                cor = (255, 150, 150)
                opcao_selecionada = i
            
            screen.blit(txt, (caixa_x + 40, y))
            
            # Desenhar cursor do controle se selecionado
            if i == opcao_selecionada and gerenciador_gamepad.obter_numero_controles() > 0:
                tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                cursor_rect = pygame.Rect(
                    rect_opcao.x - tamanho_cursor,
                    rect_opcao.y - tamanho_cursor,
                    rect_opcao.width + tamanho_cursor * 2,
                    rect_opcao.height + tamanho_cursor * 2
                )
                pygame.draw.rect(screen, (255, 150, 150), cursor_rect, 3)
        
        pygame.display.flip()
        
        # Processar eventos
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            
            # Processar controle primeiro
            controle_processado = False
            if gerenciador_gamepad.obter_numero_controles() > 0:
                tempo_atual = pygame.time.get_ticks()
                resultado_controle = processar_eventos_controle_menu(ev, opcao_selecionada, len(opcoes), joystick_id=0, tempo_atual=tempo_atual)
                if resultado_controle:
                    acao = resultado_controle.get("acao")
                    if acao == "cima":
                        opcao_selecionada = (opcao_selecionada - 1) % len(opcoes)
                        controle_processado = True
                    elif acao == "baixo":
                        opcao_selecionada = (opcao_selecionada + 1) % len(opcoes)
                        controle_processado = True
                    elif acao == "confirmar":
                        if opcao_selecionada == 0:  # VENDER
                            return True
                        else:  # CANCELAR
                            return False
                    elif acao == "cancelar":
                        return False
            
            if not controle_processado:
                if ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_UP, pygame.K_w):
                        opcao_selecionada = (opcao_selecionada - 1) % len(opcoes)
                    elif ev.key in (pygame.K_DOWN, pygame.K_s):
                        opcao_selecionada = (opcao_selecionada + 1) % len(opcoes)
                    elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        return opcao_selecionada == 0  # VENDER = True, CANCELAR = False
                    elif ev.key == pygame.K_ESCAPE:
                        return False  # Cancelar
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for i, texto_opcao in enumerate(opcoes):
                        rect_opcao = pygame.Rect(caixa_x + 40, caixa_y + 105 + i * 30, caixa_largura - 80, 30)
                        if rect_opcao.collidepoint(mouse_x, mouse_y):
                            return i == 0  # VENDER = True, CANCELAR = False

def mostrar_dialogo_confirmacao_fechar(screen, bg):
    """Mostra diálogo modal de confirmação para fechar o jogo"""
    from config import LARGURA, ALTURA, FPS
    from core.i18n import t
    
    clock = pygame.time.Clock()
    opcao_selecionada = 0  # 0 = SIM, 1 = NÃO
    
    # Variáveis para os botões
    caixa_largura = 600
    caixa_altura = 220
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2
    
    botao_sim_rect = pygame.Rect(caixa_x + 50, caixa_y + caixa_altura - 70, 180, 50)
    botao_nao_rect = pygame.Rect(caixa_x + caixa_largura - 230, caixa_y + caixa_altura - 70, 180, 50)
    
    animacao_cursor = 0.0
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        animacao_cursor += dt * 3.0
        if animacao_cursor >= 1.0:
            animacao_cursor = 0.0
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False  # Não fechar se clicar no X durante confirmação
            elif ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_LEFT, pygame.K_a):
                    opcao_selecionada = (opcao_selecionada - 1) % 2
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    opcao_selecionada = (opcao_selecionada + 1) % 2
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return opcao_selecionada == 0  # SIM = True, NÃO = False
                elif ev.key == pygame.K_ESCAPE:
                    return False  # Cancelar
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if botao_sim_rect.collidepoint(mouse_x, mouse_y):
                    return True
                elif botao_nao_rect.collidepoint(mouse_x, mouse_y):
                    return False
            
            # Processar controle
            from core.gamepad_manager import gerenciador_gamepad
            if gerenciador_gamepad.obter_numero_controles() > 0:
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
                resultado_controle = processar_eventos_controle_menu(ev, opcao_selecionada, 2, joystick_id=0, tempo_atual=tempo_atual)
                if resultado_controle:
                    acao = resultado_controle.get("acao")
                    if acao == "esquerda":
                        opcao_selecionada = (opcao_selecionada - 1) % 2
                    elif acao == "direita":
                        opcao_selecionada = (opcao_selecionada + 1) % 2
                    elif acao == "confirmar":
                        return opcao_selecionada == 0  # SIM = True, NÃO = False
                    elif acao == "cancelar":
                        return False  # Cancelar
        
        # Desenhar
        screen.blit(bg, (0, 0))
        
        # Overlay escuro
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Caixa do diálogo
        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 200))
        screen.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        # Texto principal - reduzir tamanho da fonte para caber na caixa
        from core.i18n import t
        texto_pergunta = render_text(t("confirmacao.fechar.pergunta"), 20, (255, 255, 255), bold=True, pixel_style=True)
        texto_pergunta_x = caixa_x + (caixa_largura - texto_pergunta.get_width()) // 2
        screen.blit(texto_pergunta, (texto_pergunta_x, caixa_y + 30))
        
        # Botões
        mouse_x, mouse_y = pygame.mouse.get_pos()
        sim_hover = botao_sim_rect.collidepoint(mouse_x, mouse_y)
        nao_hover = botao_nao_rect.collidepoint(mouse_x, mouse_y)
        
        cor_sim = (100, 255, 100) if (opcao_selecionada == 0 or sim_hover) else (80, 200, 80)
        cor_nao = (255, 100, 100) if (opcao_selecionada == 1 or nao_hover) else (200, 80, 80)
        
        pygame.draw.rect(screen, cor_sim, botao_sim_rect)
        pygame.draw.rect(screen, (150, 255, 150), botao_sim_rect, 2)
        pygame.draw.rect(screen, cor_nao, botao_nao_rect)
        pygame.draw.rect(screen, (255, 150, 150), botao_nao_rect, 2)
        
        # Desenhar cursor do controle se selecionado
        from core.gamepad_manager import gerenciador_gamepad
        if gerenciador_gamepad.obter_numero_controles() > 0:
            tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
            if opcao_selecionada == 0:
                cursor_rect = pygame.Rect(
                    botao_sim_rect.x - tamanho_cursor,
                    botao_sim_rect.y - tamanho_cursor,
                    botao_sim_rect.width + tamanho_cursor * 2,
                    botao_sim_rect.height + tamanho_cursor * 2
                )
                pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
            else:
                cursor_rect = pygame.Rect(
                    botao_nao_rect.x - tamanho_cursor,
                    botao_nao_rect.y - tamanho_cursor,
                    botao_nao_rect.width + tamanho_cursor * 2,
                    botao_nao_rect.height + tamanho_cursor * 2
                )
                pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
        
        texto_sim = render_text(t("confirmacao.fechar.sim"), 22, (255, 255, 255), bold=True, pixel_style=True)
        texto_sim_x = botao_sim_rect.x + (botao_sim_rect.width - texto_sim.get_width()) // 2
        texto_sim_y = botao_sim_rect.y + (botao_sim_rect.height - texto_sim.get_height()) // 2
        screen.blit(texto_sim, (texto_sim_x, texto_sim_y))
        
        texto_nao = render_text(t("confirmacao.fechar.nao"), 22, (255, 255, 255), bold=True, pixel_style=True)
        texto_nao_x = botao_nao_rect.x + (botao_nao_rect.width - texto_nao.get_width()) // 2
        texto_nao_y = botao_nao_rect.y + (botao_nao_rect.height - texto_nao.get_height()) // 2
        screen.blit(texto_nao, (texto_nao_x, texto_nao_y))
        
        pygame.display.flip()

def mostrar_dialogo_confirmacao_resolucao(screen_ref, bg, nova_resolucao, resolucao_anterior):
    """Mostra diálogo de confirmação para mudança de resolução com timer de 30 segundos"""
    from config import CONFIGURACOES, salvar_configuracoes
    from core.i18n import t
    
    print(f"DEBUG: Mostrando diálogo de confirmação. Nova resolução: {nova_resolucao}, Anterior: {resolucao_anterior}")
    
    # Aplicar nova resolução temporariamente
    fullscreen = CONFIGURACOES["video"]["fullscreen"]
    tela_cheia_sem_bordas = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
    display_flags = 0
    if fullscreen:
        display_flags |= pygame.FULLSCREEN
    elif tela_cheia_sem_bordas:
        display_flags |= pygame.NOFRAME
    
    # Criar nova tela com a nova resolução
    screen = pygame.display.set_mode(nova_resolucao, display_flags)
    nova_largura, nova_altura = nova_resolucao
    
    # Recarregar background com nova resolução
    bg_novo = scale_to_cover(pygame.image.load(CAMINHO_MENU).convert_alpha(), nova_largura, nova_altura)
    
    clock = pygame.time.Clock()
    tempo_inicial = pygame.time.get_ticks()
    tempo_limite = 30000  # 30 segundos em milissegundos
    confirmado = False
    
    # Variáveis para os botões
    caixa_largura = 700
    caixa_altura = 350
    caixa_x = (nova_largura - caixa_largura) // 2
    caixa_y = (nova_altura - caixa_altura) // 2
    
    botao_manter_rect = pygame.Rect(caixa_x + 50, caixa_y + caixa_altura - 80, 200, 50)
    botao_reverter_rect = pygame.Rect(caixa_x + caixa_largura - 250, caixa_y + caixa_altura - 80, 200, 50)
    
    print(f"DEBUG: Diálogo iniciado. Caixa em ({caixa_x}, {caixa_y}), tamanho ({caixa_largura}, {caixa_altura})")
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        tempo_atual = pygame.time.get_ticks()
        tempo_decorrido = tempo_atual - tempo_inicial
        tempo_restante = max(0, (tempo_limite - tempo_decorrido) // 1000)
        
        # Se o timer expirou, reverter
        if tempo_decorrido >= tempo_limite:
            return False
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if botao_manter_rect.collidepoint(mouse_x, mouse_y):
                    confirmado = True
                    return True
                elif botao_reverter_rect.collidepoint(mouse_x, mouse_y):
                    return False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN or ev.key == pygame.K_SPACE:
                    confirmado = True
                    return True
                elif ev.key == pygame.K_ESCAPE:
                    return False
        
        # Desenhar
        screen.blit(bg_novo, (0, 0))
        
        # Overlay escuro
        overlay = pygame.Surface((nova_largura, nova_altura), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Caixa do diálogo
        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 200))
        screen.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        # Texto principal
        texto_pergunta = render_text(t("video.confirmar_resolucao"), 26, (255, 255, 255), bold=True, pixel_style=True)
        texto_pergunta_x = caixa_x + (caixa_largura - texto_pergunta.get_width()) // 2
        screen.blit(texto_pergunta, (texto_pergunta_x, caixa_y + 50))
        
        # Informação da resolução
        texto_resolucao = render_text(f"{nova_resolucao[0]}x{nova_resolucao[1]}", 24, (0, 200, 255), bold=True, pixel_style=True)
        texto_resolucao_x = caixa_x + (caixa_largura - texto_resolucao.get_width()) // 2
        screen.blit(texto_resolucao, (texto_resolucao_x, caixa_y + 120))
        
        # Timer
        texto_timer = render_text(t("video.tempo_restante").format(tempo_restante), 22, (255, 200, 0), bold=True, pixel_style=True)
        texto_timer_x = caixa_x + (caixa_largura - texto_timer.get_width()) // 2
        screen.blit(texto_timer, (texto_timer_x, caixa_y + 180))
        
        # Botões
        mouse_x, mouse_y = pygame.mouse.get_pos()
        manter_hover = botao_manter_rect.collidepoint(mouse_x, mouse_y)
        reverter_hover = botao_reverter_rect.collidepoint(mouse_x, mouse_y)
        
        # Botão Manter
        cor_manter = (0, 200, 255) if manter_hover else (100, 150, 200)
        pygame.draw.rect(screen, cor_manter, botao_manter_rect)
        pygame.draw.rect(screen, (255, 255, 255), botao_manter_rect, 2)
        texto_manter = render_text(t("video.manter"), 22, (255, 255, 255), bold=True, pixel_style=True)
        texto_manter_x = botao_manter_rect.centerx - texto_manter.get_width() // 2
        texto_manter_y = botao_manter_rect.centery - texto_manter.get_height() // 2
        screen.blit(texto_manter, (texto_manter_x, texto_manter_y))
        
        # Botão Reverter
        cor_reverter = (255, 100, 100) if reverter_hover else (200, 100, 100)
        pygame.draw.rect(screen, cor_reverter, botao_reverter_rect)
        pygame.draw.rect(screen, (255, 255, 255), botao_reverter_rect, 2)
        texto_reverter = render_text(t("video.reverter"), 22, (255, 255, 255), bold=True, pixel_style=True)
        texto_reverter_x = botao_reverter_rect.centerx - texto_reverter.get_width() // 2
        texto_reverter_y = botao_reverter_rect.centery - texto_reverter.get_height() // 2
        screen.blit(texto_reverter, (texto_reverter_x, texto_reverter_y))
        
        pygame.display.flip()

def submenu_video(screen_ref):
    """Submenu de configurações de vídeo"""
    from config import CONFIGURACOES, salvar_configuracoes
    screen = screen_ref
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    # Usar resolução atual do screen ao invés de LARGURA e ALTURA globais
    largura_atual, altura_atual = screen.get_size()
    bg = scale_to_cover(bg_raw, largura_atual, altura_atual)

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
    caixa_x = (largura_atual - caixa_largura) // 2
    caixa_y = (altura_atual - caixa_altura) // 2

    hover_animation = [0.0] * len(opcoes_video)
    hover_speed = 8.0  # Velocidade aumentada

    # scroll
    scroll_offset = 0
    scroll_dragging = False
    scroll_drag_start_y = 0
    scroll_drag_start_offset = 0.0
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
                    print("DEBUG: Clique no botão voltar")
                    return True
                
                # Verificar clique na scrollbar
                if max_scroll > 0:
                    scrollbar_width = 12
                    scrollbar_x = caixa_x + caixa_largura - scrollbar_width - 5
                    scrollbar_y = caixa_y + 80
                    scrollbar_height = altura_area_visivel
                    scrollbar_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
                    if scrollbar_rect.collidepoint(mouse_x, mouse_y):
                        scroll_dragging = True
                        scroll_drag_start_y = mouse_y
                        scroll_drag_start_offset = scroll_offset
                    elif mouse_in_caixa:
                        idx = verificar_clique_opcao(mouse_x, mouse_y, opcoes_video,
                                                     caixa_x, caixa_y, caixa_largura, altura_item, 80, None, scroll_offset)
                        if idx >= 0:
                            opcao_atual = idx
                            chave = opcoes_video[opcao_atual][1]
                            if chave == "resolucao":
                                # Alterar resolução ao clicar (ciclar para próxima)
                                resolucoes = [(1280, 720), (1920, 1080), (1366, 768), (1600, 900)]
                                resolucao_atual = CONFIGURACOES["video"]["resolucao"]
                                try:
                                    idx_res = resolucoes.index(resolucao_atual)
                                    nova_resolucao = resolucoes[(idx_res + 1) % len(resolucoes)]
                                except ValueError:
                                    nova_resolucao = resolucoes[0]
                                
                                CONFIGURACOES["video"]["resolucao"] = nova_resolucao
                                salvar_configuracoes()
                                # Recarregar background com nova resolução
                                bg = scale_to_cover(bg_raw, nova_resolucao[0], nova_resolucao[1])
                                # Atualizar screen e retornar
                                fullscreen = CONFIGURACOES["video"]["fullscreen"]
                                tela_cheia_sem_bordas = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
                                display_flags = 0
                                if fullscreen:
                                    display_flags |= pygame.FULLSCREEN
                                elif tela_cheia_sem_bordas:
                                    display_flags |= pygame.NOFRAME
                                screen = pygame.display.set_mode(nova_resolucao, display_flags)
                                return (True, screen)
                            elif chave in ["fullscreen", "tela_cheia_sem_bordas"]:
                                # Salvar estado anterior
                                fullscreen_anterior = CONFIGURACOES["video"]["fullscreen"]
                                tela_cheia_sem_bordas_anterior = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
                                
                                # Alterar estado temporariamente
                                CONFIGURACOES["video"][chave] = not CONFIGURACOES["video"][chave]
                                
                                # Aplicar mudança temporariamente e mostrar diálogo de confirmação
                                resolucao = CONFIGURACOES["video"]["resolucao"]
                                fullscreen = CONFIGURACOES["video"]["fullscreen"]
                                tela_cheia_sem_bordas = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
                                display_flags = 0
                                if fullscreen:
                                    display_flags |= pygame.FULLSCREEN
                                elif tela_cheia_sem_bordas:
                                    display_flags |= pygame.NOFRAME
                                
                                resultado_confirmacao = mostrar_dialogo_confirmacao_resolucao(screen, bg, resolucao, resolucao)
                                
                                if resultado_confirmacao:
                                    # Usuário confirmou, manter nova configuração
                                    salvar_configuracoes()
                                    screen = pygame.display.set_mode(resolucao, display_flags)
                                    return (True, screen)
                                else:
                                    # Usuário não confirmou ou timer expirou, reverter
                                    CONFIGURACOES["video"]["fullscreen"] = fullscreen_anterior
                                    CONFIGURACOES["video"]["tela_cheia_sem_bordas"] = tela_cheia_sem_bordas_anterior
                                    salvar_configuracoes()
                                    # Aplicar configuração anterior
                                    display_flags = 0
                                    if fullscreen_anterior:
                                        display_flags |= pygame.FULLSCREEN
                                    elif tela_cheia_sem_bordas_anterior:
                                        display_flags |= pygame.NOFRAME
                                    screen = pygame.display.set_mode(resolucao, display_flags)
                                    return (True, screen)
                            elif chave in ["qualidade_alta", "vsync", "mostrar_fps"]:
                                CONFIGURACOES["video"][chave] = not CONFIGURACOES["video"][chave]
                                salvar_configuracoes()
                elif mouse_in_caixa:
                    idx = verificar_clique_opcao(mouse_x, mouse_y, opcoes_video,
                                                 caixa_x, caixa_y, caixa_largura, altura_item, 80, None, scroll_offset)
                    if idx >= 0:
                        opcao_atual = idx
                        chave = opcoes_video[opcao_atual][1]
                        if chave == "resolucao":
                            # Alterar resolução ao clicar (ciclar para próxima)
                            resolucoes = [(1280, 720), (1920, 1080), (1366, 768), (1600, 900)]
                            resolucao_atual = CONFIGURACOES["video"]["resolucao"]
                            try:
                                idx_res = resolucoes.index(resolucao_atual)
                                nova_resolucao = resolucoes[(idx_res + 1) % len(resolucoes)]
                            except ValueError:
                                nova_resolucao = resolucoes[0]
                            
                            CONFIGURACOES["video"]["resolucao"] = nova_resolucao
                            salvar_configuracoes()
                            # Recarregar background com nova resolução
                            bg = scale_to_cover(bg_raw, nova_resolucao[0], nova_resolucao[1])
                            # Atualizar variáveis de tamanho
                            largura_atual, altura_atual = nova_resolucao
                            caixa_x = (largura_atual - caixa_largura) // 2
                            caixa_y = (altura_atual - caixa_altura) // 2
                            # Atualizar screen e retornar
                            fullscreen = CONFIGURACOES["video"]["fullscreen"]
                            tela_cheia_sem_bordas = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
                            display_flags = 0
                            if fullscreen:
                                display_flags |= pygame.FULLSCREEN
                            elif tela_cheia_sem_bordas:
                                display_flags |= pygame.NOFRAME
                            screen = pygame.display.set_mode(nova_resolucao, display_flags)
                            return (True, screen)
                        elif chave in ["fullscreen", "tela_cheia_sem_bordas"]:
                            # Salvar estado anterior
                            fullscreen_anterior = CONFIGURACOES["video"]["fullscreen"]
                            tela_cheia_sem_bordas_anterior = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
                            
                            # Alterar estado temporariamente
                            CONFIGURACOES["video"][chave] = not CONFIGURACOES["video"][chave]
                            
                            # Aplicar mudança temporariamente e mostrar diálogo de confirmação
                            resolucao = CONFIGURACOES["video"]["resolucao"]
                            fullscreen = CONFIGURACOES["video"]["fullscreen"]
                            tela_cheia_sem_bordas = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
                            display_flags = 0
                            if fullscreen:
                                display_flags |= pygame.FULLSCREEN
                            elif tela_cheia_sem_bordas:
                                display_flags |= pygame.NOFRAME
                            
                            resultado_confirmacao = mostrar_dialogo_confirmacao_resolucao(screen, bg, resolucao, resolucao)
                            
                            if resultado_confirmacao:
                                # Usuário confirmou, manter nova configuração
                                salvar_configuracoes()
                                screen = pygame.display.set_mode(resolucao, display_flags)
                                return (True, screen)
                            else:
                                # Usuário não confirmou ou timer expirou, reverter
                                CONFIGURACOES["video"]["fullscreen"] = fullscreen_anterior
                                CONFIGURACOES["video"]["tela_cheia_sem_bordas"] = tela_cheia_sem_bordas_anterior
                                salvar_configuracoes()
                                # Aplicar configuração anterior
                                display_flags = 0
                                if fullscreen_anterior:
                                    display_flags |= pygame.FULLSCREEN
                                elif tela_cheia_sem_bordas_anterior:
                                    display_flags |= pygame.NOFRAME
                                screen = pygame.display.set_mode(resolucao, display_flags)
                                return (True, screen)
                        elif chave in ["qualidade_alta", "vsync", "mostrar_fps"]:
                            CONFIGURACOES["video"][chave] = not CONFIGURACOES["video"][chave]
                            salvar_configuracoes()

            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                scroll_dragging = False

            elif ev.type == pygame.MOUSEMOTION:
                if scroll_dragging and max_scroll > 0:
                    mouse_y = ev.pos[1]
                    delta_y = mouse_y - scroll_drag_start_y
                    scrollbar_height = altura_area_visivel
                    indicator_height = max(30, int(scrollbar_height * 0.3))
                    scroll_max = scrollbar_height - indicator_height
                    if scroll_max > 0:
                        scroll_ratio = delta_y / scroll_max
                        new_offset = scroll_drag_start_offset + (scroll_ratio * max_scroll)
                        scroll_offset = max(0, min(max_scroll, new_offset))

            elif ev.type == pygame.MOUSEWHEEL:
                scroll_offset = max(0, min(max_scroll, scroll_offset - ev.y * 30))
            # Processar eventos de controle
            if gerenciador_gamepad.obter_numero_controles() > 0:
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
                resultado_controle = processar_eventos_controle_menu(ev, opcao_atual, len(opcoes_video), joystick_id=0, tempo_atual=tempo_atual)
                if resultado_controle:
                    acao = resultado_controle.get("acao")
                    if acao == "cima" and "opcao" in resultado_controle:
                        nova_opcao = resultado_controle["opcao"]
                        if nova_opcao != opcao_atual:
                            opcao_atual = nova_opcao
                            # Ajustar scroll para seguir a opção selecionada
                            altura_total_opcoes = len(opcoes_video) * altura_item
                            altura_area_visivel = caixa_altura - 200
                            max_scroll = max(0, altura_total_opcoes - altura_area_visivel)
                            # Calcular posição Y da opção na lista (sem scroll)
                            opcao_y_lista = opcao_atual * altura_item
                            # Área visível: de 0 até altura_area_visivel (sem sobrepor o botão voltar)
                            topo_area_visivel = 0
                            fundo_area_visivel = altura_area_visivel
                            # Calcular posição Y da opção na tela (considerando scroll atual)
                            opcao_y_tela = opcao_y_lista - scroll_offset
                            # Ajustar scroll se necessário
                            if opcao_y_tela < topo_area_visivel:
                                # Opção está acima da área visível - aumentar scroll para que ela apareça
                                scroll_offset = opcao_y_lista - topo_area_visivel
                            elif opcao_y_tela + altura_item > fundo_area_visivel:
                                # Opção está abaixo da área visível - diminuir scroll para que ela apareça
                                scroll_offset = opcao_y_lista + altura_item - fundo_area_visivel
                            # Garantir que scroll está dentro dos limites
                            scroll_offset = max(0, min(max_scroll, scroll_offset))
                    elif acao == "baixo" and "opcao" in resultado_controle:
                        nova_opcao = resultado_controle["opcao"]
                        if nova_opcao != opcao_atual:
                            opcao_atual = nova_opcao
                            # Ajustar scroll para seguir a opção selecionada
                            altura_total_opcoes = len(opcoes_video) * altura_item
                            altura_area_visivel = caixa_altura - 200
                            max_scroll = max(0, altura_total_opcoes - altura_area_visivel)
                            # Calcular posição Y da opção na lista (sem scroll)
                            opcao_y_lista = opcao_atual * altura_item
                            # Área visível: de 0 até altura_area_visivel (sem sobrepor o botão voltar)
                            topo_area_visivel = 0
                            fundo_area_visivel = altura_area_visivel
                            # Calcular posição Y da opção na tela (considerando scroll atual)
                            opcao_y_tela = opcao_y_lista - scroll_offset
                            # Ajustar scroll se necessário
                            if opcao_y_tela < topo_area_visivel:
                                # Opção está acima da área visível - aumentar scroll para que ela apareça
                                scroll_offset = opcao_y_lista - topo_area_visivel
                            elif opcao_y_tela + altura_item > fundo_area_visivel:
                                # Opção está abaixo da área visível - diminuir scroll para que ela apareça
                                scroll_offset = opcao_y_lista + altura_item - fundo_area_visivel
                            # Garantir que scroll está dentro dos limites
                            scroll_offset = max(0, min(max_scroll, scroll_offset))
                    elif acao == "confirmar":
                        # Processar ação da opção atual (similar ao ENTER)
                        chave = opcoes_video[opcao_atual][1]
                        if chave == "voltar":
                            return True
                    elif acao == "cancelar":
                        return True
                    continue
            
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
                    elif chave == "resolucao":
                        # Alterar resolução ao pressionar ENTER/SPACE (ciclar para próxima)
                        resolucoes = [(1280, 720), (1920, 1080), (1366, 768), (1600, 900)]
                        resolucao_atual = CONFIGURACOES["video"]["resolucao"]
                        try:
                            idx_res = resolucoes.index(resolucao_atual)
                            nova_resolucao = resolucoes[(idx_res + 1) % len(resolucoes)]
                        except ValueError:
                            nova_resolucao = resolucoes[0]
                        
                        CONFIGURACOES["video"]["resolucao"] = nova_resolucao
                        salvar_configuracoes()
                        # Recarregar background com nova resolução
                        bg = scale_to_cover(bg_raw, nova_resolucao[0], nova_resolucao[1])
                        # Atualizar variáveis de tamanho
                        largura_atual, altura_atual = nova_resolucao
                        caixa_x = (largura_atual - caixa_largura) // 2
                        caixa_y = (altura_atual - caixa_altura) // 2
                        # Atualizar screen e retornar
                        fullscreen = CONFIGURACOES["video"]["fullscreen"]
                        tela_cheia_sem_bordas = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
                        display_flags = 0
                        if fullscreen:
                            display_flags |= pygame.FULLSCREEN
                        elif tela_cheia_sem_bordas:
                            display_flags |= pygame.NOFRAME
                        screen = pygame.display.set_mode(nova_resolucao, display_flags)
                        return (True, screen)
                    elif chave in ["fullscreen", "tela_cheia_sem_bordas"]:
                        # Salvar estado anterior
                        fullscreen_anterior = CONFIGURACOES["video"]["fullscreen"]
                        tela_cheia_sem_bordas_anterior = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
                        
                        # Alterar estado temporariamente
                        CONFIGURACOES["video"][chave] = not CONFIGURACOES["video"][chave]
                        
                        # Aplicar mudança temporariamente e mostrar diálogo de confirmação
                        resolucao = CONFIGURACOES["video"]["resolucao"]
                        fullscreen = CONFIGURACOES["video"]["fullscreen"]
                        tela_cheia_sem_bordas = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
                        display_flags = 0
                        if fullscreen:
                            display_flags |= pygame.FULLSCREEN
                        elif tela_cheia_sem_bordas:
                            display_flags |= pygame.NOFRAME
                        
                        resultado_confirmacao = mostrar_dialogo_confirmacao_resolucao(screen, bg, resolucao, resolucao)
                        
                        if resultado_confirmacao:
                            # Usuário confirmou, manter nova configuração
                            salvar_configuracoes()
                            screen = pygame.display.set_mode(resolucao, display_flags)
                            return (True, screen)
                        else:
                            # Usuário não confirmou ou timer expirou, reverter
                            CONFIGURACOES["video"]["fullscreen"] = fullscreen_anterior
                            CONFIGURACOES["video"]["tela_cheia_sem_bordas"] = tela_cheia_sem_bordas_anterior
                            salvar_configuracoes()
                            # Aplicar configuração anterior
                            display_flags = 0
                            if fullscreen_anterior:
                                display_flags |= pygame.FULLSCREEN
                            elif tela_cheia_sem_bordas_anterior:
                                display_flags |= pygame.NOFRAME
                            screen = pygame.display.set_mode(resolucao, display_flags)
                            return (True, screen)
                    elif chave in ["fullscreen", "tela_cheia_sem_bordas", "qualidade_alta", "vsync", "mostrar_fps"]:
                        CONFIGURACOES["video"][chave] = not CONFIGURACOES["video"][chave]
                        salvar_configuracoes()
                        
                        if chave in ["fullscreen", "tela_cheia_sem_bordas"]:
                            resolucao = CONFIGURACOES["video"]["resolucao"]
                            fullscreen = CONFIGURACOES["video"]["fullscreen"]
                            tela_cheia_sem_bordas = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
                            display_flags = 0
                            if fullscreen:
                                display_flags |= pygame.FULLSCREEN
                            elif tela_cheia_sem_bordas:
                                display_flags |= pygame.NOFRAME
                            nova_tela = pygame.display.set_mode(resolucao, display_flags)
                            screen = nova_tela
                            return (True, nova_tela)
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    if opcoes_video[opcao_atual][1] == "resolucao":
                        resolucoes = [(1280, 720), (1920, 1080), (1366, 768), (1600, 900)]
                        resolucao_atual = CONFIGURACOES["video"]["resolucao"]
                        try:
                            idx = resolucoes.index(resolucao_atual)
                            nova_resolucao = resolucoes[(idx - 1) % len(resolucoes)]
                        except ValueError:
                            nova_resolucao = resolucoes[0]
                        
                        CONFIGURACOES["video"]["resolucao"] = nova_resolucao
                        salvar_configuracoes()
                        # Recarregar background com nova resolução
                        bg = scale_to_cover(bg_raw, nova_resolucao[0], nova_resolucao[1])
                        # Atualizar variáveis de tamanho
                        largura_atual, altura_atual = nova_resolucao
                        caixa_x = (largura_atual - caixa_largura) // 2
                        caixa_y = (altura_atual - caixa_altura) // 2
                        # Atualizar screen e retornar
                        fullscreen = CONFIGURACOES["video"]["fullscreen"]
                        tela_cheia_sem_bordas = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
                        display_flags = 0
                        if fullscreen:
                            display_flags |= pygame.FULLSCREEN
                        elif tela_cheia_sem_bordas:
                            display_flags |= pygame.NOFRAME
                        screen = pygame.display.set_mode(nova_resolucao, display_flags)
                        return (True, screen)
                    elif opcoes_video[opcao_atual][1] in ["fullscreen", "tela_cheia_sem_bordas"]:
                        chave = opcoes_video[opcao_atual][1]
                        # Salvar estado anterior
                        fullscreen_anterior = CONFIGURACOES["video"]["fullscreen"]
                        tela_cheia_sem_bordas_anterior = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
                        resolucao_anterior = CONFIGURACOES["video"]["resolucao"]  # Salvar resolução anterior
                        
                        # Alterar estado temporariamente
                        CONFIGURACOES["video"][chave] = not CONFIGURACOES["video"][chave]
                        
                        # Aplicar mudança temporariamente e mostrar diálogo de confirmação
                        resolucao = CONFIGURACOES["video"]["resolucao"]
                        fullscreen = CONFIGURACOES["video"]["fullscreen"]
                        tela_cheia_sem_bordas = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
                        display_flags = 0
                        if fullscreen:
                            display_flags |= pygame.FULLSCREEN
                        elif tela_cheia_sem_bordas:
                            display_flags |= pygame.NOFRAME
                        
                        resultado_confirmacao = mostrar_dialogo_confirmacao_resolucao(screen, bg, resolucao, resolucao_anterior)
                        
                        if resultado_confirmacao:
                            # Usuário confirmou, manter nova configuração
                            salvar_configuracoes()
                            # Recarregar background com resolução atual
                            bg = scale_to_cover(bg_raw, resolucao[0], resolucao[1])
                        else:
                            # Usuário não confirmou ou timer expirou, reverter
                            CONFIGURACOES["video"][chave] = not CONFIGURACOES["video"][chave]  # Reverter mudança
                            CONFIGURACOES["video"]["resolucao"] = resolucao_anterior  # type: ignore
                            salvar_configuracoes()
                            # Recarregar background com resolução anterior
                            bg = scale_to_cover(bg_raw, resolucao_anterior[0], resolucao_anterior[1])  # type: ignore
                            # Aplicar resolução anterior
                            fullscreen = CONFIGURACOES["video"]["fullscreen"]
                            tela_cheia_sem_bordas = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
                            display_flags = 0
                            if fullscreen:
                                display_flags |= pygame.FULLSCREEN
                            elif tela_cheia_sem_bordas:
                                display_flags |= pygame.NOFRAME
                            screen = pygame.display.set_mode(resolucao_anterior, display_flags)  # type: ignore
                            return (True, screen)
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
                        resolucao_atual = CONFIGURACOES["video"]["resolucao"]
                        try:
                            idx = resolucoes.index(resolucao_atual)
                            nova_resolucao = resolucoes[(idx + 1) % len(resolucoes)]
                        except ValueError:
                            nova_resolucao = resolucoes[0]
                        
                        CONFIGURACOES["video"]["resolucao"] = nova_resolucao
                        salvar_configuracoes()
                        # Recarregar background com nova resolução
                        bg = scale_to_cover(bg_raw, nova_resolucao[0], nova_resolucao[1])
                        # Atualizar variáveis de tamanho
                        largura_atual, altura_atual = nova_resolucao
                        caixa_x = (largura_atual - caixa_largura) // 2
                        caixa_y = (altura_atual - caixa_altura) // 2
                        # Atualizar screen e retornar
                        fullscreen = CONFIGURACOES["video"]["fullscreen"]
                        tela_cheia_sem_bordas = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
                        display_flags = 0
                        if fullscreen:
                            display_flags |= pygame.FULLSCREEN
                        elif tela_cheia_sem_bordas:
                            display_flags |= pygame.NOFRAME
                        screen = pygame.display.set_mode(nova_resolucao, display_flags)
                        return (True, screen)
                    elif opcoes_video[opcao_atual][1] in ["fullscreen", "tela_cheia_sem_bordas"]:
                        chave = opcoes_video[opcao_atual][1]
                        # Salvar estado anterior
                        fullscreen_anterior = CONFIGURACOES["video"]["fullscreen"]
                        tela_cheia_sem_bordas_anterior = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
                        
                        # Alterar estado temporariamente
                        CONFIGURACOES["video"][chave] = not CONFIGURACOES["video"][chave]
                        
                        # Aplicar mudança temporariamente e mostrar diálogo de confirmação
                        resolucao = CONFIGURACOES["video"]["resolucao"]
                        fullscreen = CONFIGURACOES["video"]["fullscreen"]
                        tela_cheia_sem_bordas = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
                        display_flags = 0
                        if fullscreen:
                            display_flags |= pygame.FULLSCREEN
                        elif tela_cheia_sem_bordas:
                            display_flags |= pygame.NOFRAME
                        
                        resultado_confirmacao = mostrar_dialogo_confirmacao_resolucao(screen, bg, resolucao, resolucao)
                        
                        if resultado_confirmacao:
                            # Usuário confirmou, manter nova configuração
                            salvar_configuracoes()
                            screen = pygame.display.set_mode(resolucao, display_flags)
                            return (True, screen)
                        else:
                            # Usuário não confirmou ou timer expirou, reverter
                            CONFIGURACOES["video"]["fullscreen"] = fullscreen_anterior
                            CONFIGURACOES["video"]["tela_cheia_sem_bordas"] = tela_cheia_sem_bordas_anterior
                            salvar_configuracoes()
                            # Aplicar configuração anterior
                            display_flags = 0
                            if fullscreen_anterior:
                                display_flags |= pygame.FULLSCREEN
                            elif tela_cheia_sem_bordas_anterior:
                                display_flags |= pygame.NOFRAME
                            screen = pygame.display.set_mode(resolucao, display_flags)
                            return (True, screen)
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
            # Verificar se está dentro da área visível (acima do botão voltar)
            if y < caixa_y + 80 or y + altura_item > caixa_y + caixa_altura - 80:
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
            desenhar_scrollbar(screen, scroll_offset, max_scroll, caixa_x, caixa_y, caixa_largura, caixa_altura, scroll_dragging)

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
            # Processar eventos de controle
            if gerenciador_gamepad.obter_numero_controles() > 0:
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
                resultado_controle = processar_eventos_controle_menu(ev, opcao_atual, len(opcoes_idioma), joystick_id=0, tempo_atual=tempo_atual)
                if resultado_controle:
                    acao = resultado_controle.get("acao")
                    if acao == "cima" and "opcao" in resultado_controle:
                        opcao_atual = resultado_controle["opcao"]
                    elif acao == "baixo" and "opcao" in resultado_controle:
                        opcao_atual = resultado_controle["opcao"]
                    elif acao == "confirmar":
                        # Selecionar idioma
                        from config import CONFIGURACOES, salvar_configuracoes
                        chave = opcoes_idioma[opcao_atual][1]
                        if "idioma" not in CONFIGURACOES:
                            CONFIGURACOES["idioma"] = {}
                        CONFIGURACOES["idioma"]["idioma_atual"] = chave
                        salvar_configuracoes()
                        from core.i18n import inicializar_idioma
                        inicializar_idioma()
                    elif acao == "cancelar":
                        return True
                    continue
            
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
            (t("menu.opcoes.jogo"), "jogo"),
            (t("menu.opcoes.idioma"), "idioma"),
            (t("menu.opcoes.voltar"), "voltar")
        ]
    
    opcoes_principais = recarregar_opcoes()

    opcao_atual = 0
    clock = pygame.time.Clock()

    # caixa
    caixa_largura = 500
    caixa_altura = 600
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
            
            # Processar eventos de controle ANTES de outros eventos
            controle_processado = False
            if gerenciador_gamepad.obter_numero_controles() > 0:
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
                resultado_controle = processar_eventos_controle_menu(ev, opcao_atual, len(opcoes_principais), joystick_id=0, tempo_atual=tempo_atual)
                if resultado_controle:
                    controle_processado = True
                    acao = resultado_controle.get("acao")
                    if acao == "cima" and "opcao" in resultado_controle:
                        opcao_atual = resultado_controle["opcao"]
                    elif acao == "baixo" and "opcao" in resultado_controle:
                        opcao_atual = resultado_controle["opcao"]
                    elif acao == "confirmar":
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
                            resultado = submenu_video(screen)
                            if isinstance(resultado, tuple) and len(resultado) == 2:
                                voltar, nova_tela = resultado
                                screen = nova_tela
                                if not voltar:
                                    return False
                            elif not resultado:
                                return False
                        elif chave == "jogo":
                            if not submenu_jogo(screen):
                                return False
                        elif chave == "idioma":
                            if not submenu_idioma(screen):
                                return False
                    elif acao == "cancelar":
                        return True
            
            # Se processou evento de controle, não processar mouse/teclado para esse evento
            if controle_processado:
                continue
            
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # clique só vale se estiver dentro da caixa
                mouse_in_caixa = (caixa_x <= mouse_x <= caixa_x + caixa_largura and
                                  caixa_y <= mouse_y <= caixa_y + caixa_altura)
                if mouse_in_caixa:
                    opcao_clicada = verificar_clique_opcao(
                        mouse_x, mouse_y, opcoes_principais,
                        caixa_x, caixa_y, caixa_largura,
                        altura_item=50, offset_y=80, opcao_largura=450, scroll_offset=0
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
                            resultado = submenu_video(screen)
                            if isinstance(resultado, tuple) and len(resultado) == 2:
                                voltar, nova_tela = resultado
                                screen = nova_tela
                                if not voltar:
                                    return False
                            elif not resultado:
                                return False
                        elif chave == "jogo":
                            if not submenu_jogo(screen):
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
                        resultado = submenu_video(screen)
                        if isinstance(resultado, tuple) and len(resultado) == 2:
                            voltar, nova_tela = resultado
                            screen = nova_tela
                            if voltar:
                                continue
                        elif resultado:
                            continue
                    elif chave == "jogo":
                        if not submenu_jogo(screen):
                            return False
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

        caixa_largura = 500
        caixa_altura = 600
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
                altura_item=50, offset_y=80, opcao_largura=450, scroll_offset=0
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
        opcao_largura = 450
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

def submenu_jogo(screen):
    """Submenu de configurações de jogo"""
    from config import CONFIGURACOES, salvar_configuracoes
    from core.gamepad_manager import gerenciador_gamepad
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)

    from core.i18n import t
    opcoes_jogo = [
        (t("jogo.confirmar_upgrade"), "confirmar_upgrade")
    ]
    opcao_voltar = (t("jogo.voltar"), "voltar")

    opcao_atual = 0
    voltar_selecionado = False
    clock = pygame.time.Clock()

    caixa_largura = 500
    caixa_altura = 400
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2

    hover_animation = [0.0] * len(opcoes_jogo)
    hover_speed = 8.0

    while True:
        dt = clock.tick(FPS) / 1000.0

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
                    idx = verificar_clique_opcao(mouse_x, mouse_y, opcoes_jogo,
                                                 caixa_x, caixa_y, caixa_largura, 50, 80, None, 0)
                    if idx >= 0:
                        opcao_atual = idx
                        voltar_selecionado = False
                        chave = opcoes_jogo[opcao_atual][1]
                        if chave == "confirmar_upgrade":
                            if "jogo" not in CONFIGURACOES:
                                CONFIGURACOES["jogo"] = {}
                            CONFIGURACOES["jogo"][chave] = not CONFIGURACOES["jogo"].get(chave, True)
                            salvar_configuracoes()
            # Processar eventos de controle
            if gerenciador_gamepad.obter_numero_controles() > 0:
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
                resultado_controle = processar_eventos_controle_menu(ev, opcao_atual, len(opcoes_jogo), joystick_id=0, tempo_atual=tempo_atual)
                if resultado_controle:
                    acao = resultado_controle.get("acao")
                    if acao == "cima" and "opcao" in resultado_controle:
                        opcao_atual = resultado_controle["opcao"]
                        voltar_selecionado = False
                    elif acao == "baixo" and "opcao" in resultado_controle:
                        opcao_atual = resultado_controle["opcao"]
                        voltar_selecionado = False
                    elif acao == "baixo" and opcao_atual == len(opcoes_jogo) - 1:
                        voltar_selecionado = True
                    elif acao == "cima" and voltar_selecionado:
                        voltar_selecionado = False
                        opcao_atual = len(opcoes_jogo) - 1
                    elif acao == "confirmar":
                        if voltar_selecionado:
                            return True
                        else:
                            chave = opcoes_jogo[opcao_atual][1]
                            if chave == "confirmar_upgrade":
                                if "jogo" not in CONFIGURACOES:
                                    CONFIGURACOES["jogo"] = {}
                                CONFIGURACOES["jogo"][chave] = not CONFIGURACOES["jogo"].get(chave, True)
                                salvar_configuracoes()
                    elif acao == "cancelar":
                        return True
                    continue
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return True
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    if voltar_selecionado:
                        voltar_selecionado = False
                        opcao_atual = len(opcoes_jogo) - 1
                    else:
                        opcao_atual = (opcao_atual - 1) % len(opcoes_jogo)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    if opcao_atual == len(opcoes_jogo) - 1:
                        voltar_selecionado = True
                    else:
                        opcao_atual = (opcao_atual + 1) % len(opcoes_jogo)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if voltar_selecionado:
                        return True
                    else:
                        chave = opcoes_jogo[opcao_atual][1]
                        if chave == "confirmar_upgrade":
                            if "jogo" not in CONFIGURACOES:
                                CONFIGURACOES["jogo"] = {}
                            CONFIGURACOES["jogo"][chave] = not CONFIGURACOES["jogo"].get(chave, True)
                            salvar_configuracoes()

        # Atualizar animações hover (mesmo estilo do submenu_video)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_in_caixa = (caixa_x <= mouse_x <= caixa_x + caixa_largura and
                          caixa_y <= mouse_y <= caixa_y + caixa_altura)
        
        altura_item = 50
        opcao_hover = -1
        if mouse_in_caixa:
            opcao_hover = verificar_clique_opcao(
                mouse_x, mouse_y, opcoes_jogo,
                caixa_x, caixa_y, caixa_largura, altura_item, 80, None, 0
            )
        if opcao_hover >= 0:
            opcao_atual = opcao_hover
            voltar_selecionado = False

        for i in range(len(opcoes_jogo)):
            if i == opcao_hover:
                hover_animation[i] = min(1.0, hover_animation[i] + hover_speed * dt)
            else:
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt)
        if not mouse_in_caixa:
            for i in range(len(opcoes_jogo)):
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt * 1.5)

        screen.blit(bg, (0, 0))
        
        # Overlay escuro
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        # Caixa de opções (mesmo estilo do submenu_video - fundo preto translúcido e borda branca)
        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 150))
        screen.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)

        # Título (mesmo estilo do submenu_video)
        titulo = render_text(t("menu.opcoes.jogo"), 36, (255, 255, 255), bold=True, pixel_style=True)
        titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, caixa_y + 20))

        # Opções (mesmo estilo do submenu_video)
        altura_item = 50
        for i, (nome, chave) in enumerate(opcoes_jogo):
            y = caixa_y + 80 + i * altura_item
            
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
            
            # Formato "nome: valor" (mesmo estilo do submenu_video)
            valor = CONFIGURACOES.get("jogo", {}).get(chave, True)
            valor_texto = t("jogo.sim") if valor else t("jogo.nao")
            texto = render_text(f"{nome}: {valor_texto}", 20, cor_texto, bold=True, pixel_style=True)
            screen.blit(texto, (caixa_x + 30, y))

        # Botão voltar (mesmo estilo do submenu_video)
        altura_item = 50
        voltar_y = caixa_y + caixa_altura - 60
        voltar_rect = pygame.Rect(caixa_x + 20, voltar_y - 5, caixa_largura - 50, altura_item)
        voltar_hover = voltar_rect.collidepoint(mouse_x, mouse_y) or voltar_selecionado
        if voltar_hover:
            pygame.draw.rect(screen, (0, 200, 255, 50), voltar_rect)
        voltar_texto = render_text(opcao_voltar[0], 24, (0, 200, 255) if voltar_hover else (255, 255, 255), bold=True, pixel_style=True)
        screen.blit(voltar_texto, (caixa_x + 30, voltar_y))

        pygame.display.flip()

def selecao_modo_principal_loop(screen):
    """Menu de seleção entre Campanha e Arcade"""
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)
    
    from core.i18n import t
    opcoes = [
        ("CAMPANHA", "campanha"),
        ("ARCADE", "arcade")
    ]
    
    opcao_selecionada = 0
    clock = pygame.time.Clock()
    
    # Caixa principal
    caixa_largura = 500
    caixa_altura = 300
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2
    
    hover_animation = [0.0] * len(opcoes)
    hover_speed = 8.0
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        
        gerenciador_musica.verificar_fim_musica()
        popup_musica.atualizar(dt)
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        popup_musica.verificar_hover(mouse_x, mouse_y)
        
        # Processar eventos
        eventos = pygame.event.get()
        for ev in eventos:
            if ev.type == pygame.QUIT:
                return None
            
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return None
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    opcao_selecionada = (opcao_selecionada - 1) % len(opcoes)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    opcao_selecionada = (opcao_selecionada + 1) % len(opcoes)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return opcoes[opcao_selecionada][1]  # Retorna "campanha" ou "arcade"
            
            if ev.type == pygame.MOUSEMOTION:
                for i, (nome, _) in enumerate(opcoes):
                    y = caixa_y + 120 + i * 80
                    rect = pygame.Rect(caixa_x + 50, y, caixa_largura - 100, 60)
                    if rect.collidepoint(mouse_x, mouse_y):
                        opcao_selecionada = i
            
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mouse_x, mouse_y = ev.pos
                for i, (nome, _) in enumerate(opcoes):
                    y = caixa_y + 120 + i * 80
                    rect = pygame.Rect(caixa_x + 50, y, caixa_largura - 100, 60)
                    if rect.collidepoint(mouse_x, mouse_y):
                        return opcoes[i][1]
        
        # Atualizar animações de hover
        for i, (nome, _) in enumerate(opcoes):
            y = caixa_y + 120 + i * 80
            rect = pygame.Rect(caixa_x + 50, y, caixa_largura - 100, 60)
            is_hovering = rect.collidepoint(mouse_x, mouse_y) or (i == opcao_selecionada)
            
            if is_hovering:
                hover_animation[i] = min(1.0, hover_animation[i] + hover_speed * dt)
            else:
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt)
        
        # Desenhar
        screen.blit(bg, (0, 0))
        
        # Overlay escuro
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Caixa principal
        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 220))
        screen.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        # Título
        titulo = render_text("SELECIONAR MODO", 32, (255, 255, 255), bold=True, pixel_style=True)
        titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, caixa_y + 20))
        
        # Opções
        for i, (nome, valor) in enumerate(opcoes):
            y = caixa_y + 120 + i * 80
            rect = pygame.Rect(caixa_x + 50, y, caixa_largura - 100, 60)
            
            hover_progress = hover_animation[i]
            sel = (i == opcao_selecionada)
            
            # Cores
            if sel:
                cor_fundo = (0, 150, 255, 120)
                cor_borda = (0, 200, 255)
                cor_texto = (255, 255, 255)
            else:
                cor_fundo = (0, 0, 0, 150)
                cor_borda = (255, 255, 255)
                cor_texto = (255, 255, 255)
            
            # Aplicar hover
            if hover_progress > 0:
                hover_cor_fundo = (0, 150, 255, 120)
                hover_cor_borda = (0, 200, 255)
                cor_fundo = (
                    int(cor_fundo[0] + (hover_cor_fundo[0] - cor_fundo[0]) * hover_progress),
                    int(cor_fundo[1] + (hover_cor_fundo[1] - cor_fundo[1]) * hover_progress),
                    int(cor_fundo[2] + (hover_cor_fundo[2] - cor_fundo[2]) * hover_progress),
                    int(cor_fundo[3] + (hover_cor_fundo[3] - cor_fundo[3]) * hover_progress)
                )
                cor_borda = (
                    int(cor_borda[0] + (hover_cor_borda[0] - cor_borda[0]) * hover_progress),
                    int(cor_borda[1] + (hover_cor_borda[1] - cor_borda[1]) * hover_progress),
                    int(cor_borda[2] + (hover_cor_borda[2] - cor_borda[2]) * hover_progress)
                )
            
            # Desenhar botão
            botao_fundo = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            botao_fundo.fill(cor_fundo)
            screen.blit(botao_fundo, rect.topleft)
            pygame.draw.rect(screen, cor_borda, rect, 3)
            
            # Texto
            texto = render_text(nome, 24, cor_texto, bold=True, pixel_style=True)
            texto_x = rect.x + (rect.width - texto.get_width()) // 2
            texto_y = rect.y + (rect.height - texto.get_height()) // 2
            screen.blit(texto, (texto_x, texto_y))
        
        # Instruções
        instrucoes = render_text("ESC para voltar", 14, (150, 150, 150), bold=False, pixel_style=True)
        screen.blit(instrucoes, (10, ALTURA - 30))
        
        popup_musica.desenhar(screen)
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
    
    # Opções de tipo de jogo (layout horizontal: corrida à esquerda, ghost à direita)
    opcoes_tipo = [
        (t("modo_jogo.corrida"), TipoJogo.CORRIDA),
        (t("modo_jogo.drift"), TipoJogo.DRIFT),
        (t("modo_jogo.relogio"), TipoJogo.GHOST)
    ]
    
    # Importar gerenciador de ghosts para verificar disponibilidade
    from core.ghost import gerenciador_ghosts
    
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
    
    # Variáveis para cursor do controle (indicador visual)
    # Navegação: cima/baixo navega entre linhas, esquerda/direita navega dentro da linha
    # Estrutura: linhas de opções, cada linha pode ter múltiplas opções horizontais
    # Formato: {y_pos: [(secao, indice, x, y), ...]}
    linhas_opcoes = {
        caixa_y + 120: [("modo", 0, caixa_x + 50, caixa_y + 120)],  # 1 Jogador
        caixa_y + 170: [("modo", 1, caixa_x + 50, caixa_y + 170)],  # 2 Jogadores
        caixa_y + 260: [("tipo", 0, caixa_x + 50, caixa_y + 260), ("tipo", 2, caixa_x + 270, caixa_y + 260)],  # Corrida, Ghost (horizontal)
        caixa_y + 310: [("tipo", 1, caixa_x + 50, caixa_y + 310)],  # Drift
        caixa_y + 390: [("voltas", 0, caixa_x + 50, caixa_y + 390), ("voltas", 1, caixa_x + 230, caixa_y + 390), ("voltas", 2, caixa_x + 410, caixa_y + 390)],  # 1, 2, 3 voltas (horizontal)
        caixa_y + 480: [("dificuldade", 0, caixa_x + 50, caixa_y + 480), ("dificuldade", 1, caixa_x + 230, caixa_y + 480), ("dificuldade", 2, caixa_x + 410, caixa_y + 480)],  # Fácil, Médio, Difícil (horizontal)
        caixa_y + caixa_altura - 60: [("iniciar", 0, caixa_x + 50, caixa_y + caixa_altura - 60), ("voltar", 0, caixa_x + 270, caixa_y + caixa_altura - 53)]  # Iniciar, Voltar (horizontal)
    }
    
    # Lista ordenada de linhas Y para navegação vertical
    linhas_y_ordenadas = sorted(linhas_opcoes.keys())
    
    # Estado de navegação: linha atual e opção horizontal atual
    linha_atual_idx = 0  # Índice na lista de linhas Y
    opcao_horizontal_atual = 0  # Índice da opção dentro da linha atual
    animacao_cursor = 0.0  # Animação do cursor (0.0 a 1.0)
    velocidade_animacao_cursor = 3.0  # Velocidade da animação
    
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
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        popup_musica.verificar_hover(mouse_x, mouse_y)
        
        # Atualizar animação do cursor
        animacao_cursor += dt * velocidade_animacao_cursor
        
        # Processar navegação contínua quando botão está sendo mantido pressionado
        if gerenciador_gamepad.obter_numero_controles() > 0:
            from core.menu_controles import processar_navegacao_hold
            tempo_atual = pygame.time.get_ticks()
            resultado_hold = processar_navegacao_hold(joystick_id=0, tempo_atual=tempo_atual)
            if resultado_hold:
                acao = resultado_hold.get("acao")
                linha_y_atual = linhas_y_ordenadas[linha_atual_idx]
                opcoes_na_linha = linhas_opcoes[linha_y_atual]
                num_opcoes_horizontal = len(opcoes_na_linha)
                
                if acao == "cima" and resultado_hold.get("fonte") == "hold":
                    if linha_atual_idx > 0:
                        linha_atual_idx -= 1
                        linha_y_atual = linhas_y_ordenadas[linha_atual_idx]
                        opcoes_na_linha = linhas_opcoes[linha_y_atual]
                        opcao_horizontal_atual = min(opcao_horizontal_atual, len(opcoes_na_linha) - 1)
                elif acao == "baixo" and resultado_hold.get("fonte") == "hold":
                    if linha_atual_idx < len(linhas_y_ordenadas) - 1:
                        linha_atual_idx += 1
                        linha_y_atual = linhas_y_ordenadas[linha_atual_idx]
                        opcoes_na_linha = linhas_opcoes[linha_y_atual]
                        opcao_horizontal_atual = min(opcao_horizontal_atual, len(opcoes_na_linha) - 1)
                elif acao == "esquerda" and resultado_hold.get("fonte") == "hold":
                    opcao_horizontal_atual = max(0, opcao_horizontal_atual - 1)
                elif acao == "direita" and resultado_hold.get("fonte") == "hold":
                    opcao_horizontal_atual = min(len(opcoes_na_linha) - 1, opcao_horizontal_atual + 1)
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            
            # Processar eventos de controle ANTES de outros eventos
            controle_processado = False
            if gerenciador_gamepad.obter_numero_controles() > 0:
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
                
                # Obter linha atual e opções horizontais
                linha_y_atual = linhas_y_ordenadas[linha_atual_idx]
                opcoes_na_linha = linhas_opcoes[linha_y_atual]
                num_opcoes_horizontal = len(opcoes_na_linha)
                
                # Processar eventos: para cima/baixo, passar 0 opções (navegação entre linhas)
                # Para esquerda/direita, passar número de opções horizontais
                # Chamar duas vezes: uma para cima/baixo (0 opções) e outra para esquerda/direita (num_opcoes_horizontal)
                resultado_controle_vertical = processar_eventos_controle_menu(ev, opcao_horizontal_atual, 0, joystick_id=0, tempo_atual=tempo_atual)
                resultado_controle_horizontal = processar_eventos_controle_menu(ev, opcao_horizontal_atual, num_opcoes_horizontal, joystick_id=0, tempo_atual=tempo_atual)
                
                # Priorizar resultado vertical (cima/baixo) se existir, senão usar horizontal (esquerda/direita)
                # Para esquerda/direita, sempre usar resultado_horizontal (que tem num_opcoes correto)
                if resultado_controle_vertical and resultado_controle_vertical.get("acao") in ("cima", "baixo"):
                    resultado_controle = resultado_controle_vertical
                elif resultado_controle_horizontal and resultado_controle_horizontal.get("acao") in ("esquerda", "direita"):
                    resultado_controle = resultado_controle_horizontal
                else:
                    resultado_controle = resultado_controle_vertical or resultado_controle_horizontal
                
                if resultado_controle:
                    controle_processado = True
                    acao = resultado_controle.get("acao")
                    if acao == "cima":
                        # Navegar para linha anterior
                        if linha_atual_idx > 0:
                            linha_atual_idx -= 1
                            linha_y_atual = linhas_y_ordenadas[linha_atual_idx]
                            opcoes_na_linha = linhas_opcoes[linha_y_atual]
                            # Ajustar opção horizontal para não ultrapassar
                            opcao_horizontal_atual = min(opcao_horizontal_atual, len(opcoes_na_linha) - 1)
                    elif acao == "baixo":
                        # Navegar para próxima linha
                        if linha_atual_idx < len(linhas_y_ordenadas) - 1:
                            linha_atual_idx += 1
                            linha_y_atual = linhas_y_ordenadas[linha_atual_idx]
                            opcoes_na_linha = linhas_opcoes[linha_y_atual]
                            # Ajustar opção horizontal para não ultrapassar
                            opcao_horizontal_atual = min(opcao_horizontal_atual, len(opcoes_na_linha) - 1)
                    elif acao == "esquerda":
                        # Navegar para opção anterior na linha horizontal
                        if "opcao" in resultado_controle:
                            opcao_horizontal_atual = max(0, resultado_controle["opcao"])
                        else:
                            # Se não tem opção, calcular manualmente
                            opcao_horizontal_atual = max(0, opcao_horizontal_atual - 1)
                    elif acao == "direita":
                        # Navegar para próxima opção na linha horizontal
                        if "opcao" in resultado_controle:
                            opcao_horizontal_atual = min(len(opcoes_na_linha) - 1, resultado_controle["opcao"])
                        else:
                            # Se não tem opção, calcular manualmente
                            opcao_horizontal_atual = min(len(opcoes_na_linha) - 1, opcao_horizontal_atual + 1)
                    elif acao == "confirmar":
                        # Selecionar a opção atual ou iniciar jogo
                        linha_y_atual = linhas_y_ordenadas[linha_atual_idx]
                        opcoes_na_linha = linhas_opcoes[linha_y_atual]
                        if opcao_horizontal_atual < len(opcoes_na_linha):
                            secao, indice, _, _ = opcoes_na_linha[opcao_horizontal_atual]
                            if secao == "modo":
                                opcao_modo_atual = indice
                                modo_jogo_atual = opcoes_modo[opcao_modo_atual][1]
                            elif secao == "tipo":
                                opcao_tipo_atual = indice
                                tipo_jogo_atual = opcoes_tipo[opcao_tipo_atual][1]
                            elif secao == "voltas":
                                if tipo_jogo_atual in (TipoJogo.CORRIDA, TipoJogo.DRIFT, TipoJogo.GHOST):
                                    opcao_voltas_atual = indice
                                    voltas_atual = opcoes_voltas[opcao_voltas_atual][1]
                            elif secao == "dificuldade":
                                if modo_jogo_atual == ModoJogo.UM_JOGADOR or modo_jogo_atual == ModoJogo.DOIS_JOGADORES:
                                    opcao_dificuldade_atual = indice
                                    dificuldade_ia_atual = opcoes_dificuldade[opcao_dificuldade_atual][1]
                            elif secao == "iniciar":
                                # Abrir seleção de fase antes de iniciar o jogo (não seleciona, apenas inicia)
                                fase_selecionada = selecionar_fase_loop(screen)
                                if fase_selecionada is not None:
                                    return (modo_jogo_atual, tipo_jogo_atual, voltas_atual, dificuldade_ia_atual, fase_selecionada)
                                # Se cancelou a seleção de fase, continuar no menu
                                continue
                            elif secao == "voltar":
                                # Voltar ao menu principal
                                return None
                    elif acao == "cancelar":
                        # Voltar
                        return None
            
            # Se processou evento de controle, não processar mouse/teclado para esse evento
            if controle_processado:
                continue
            
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
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
                    
                    # Verificar clique em tipo de jogo (layout horizontal: corrida à esquerda, ghost à direita)
                    for i, (nome, tipo) in enumerate(opcoes_tipo):
                        if i == 0:  # CORRIDA - à esquerda
                            x = caixa_x + 50
                            y = caixa_y + 260
                        elif i == 1:  # DRIFT - no meio
                            x = caixa_x + 50
                            y = caixa_y + 260 + 50
                        else:  # GHOST - à direita (horizontalmente)
                            x = caixa_x + 270
                            y = caixa_y + 260
                        rect = pygame.Rect(x, y - 5, 200, 40)
                        if rect.collidepoint(mouse_x, mouse_y):
                            # Verificar se é ghost e se há ghost disponível
                            if tipo == TipoJogo.GHOST:
                                # Verificar se há ghost disponível (precisa selecionar fase primeiro ou verificar todas)
                                # Por enquanto, permitir seleção (verificação será feita ao iniciar)
                                pass
                            opcao_tipo_atual = i
                            tipo_jogo_atual = tipo
                    
                    # Verificar clique em voltas (para corrida, drift e ghost) - layout horizontal
                    if tipo_jogo_atual in (TipoJogo.CORRIDA, TipoJogo.DRIFT, TipoJogo.GHOST):
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
                    if tipo_jogo_atual in (TipoJogo.CORRIDA, TipoJogo.DRIFT, TipoJogo.GHOST):
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
                    if tipo_jogo_atual in (TipoJogo.CORRIDA, TipoJogo.DRIFT, TipoJogo.GHOST):
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
        
        # Atualizar animações de hover para tipos de jogo (layout horizontal)
        for i in range(len(opcoes_tipo)):
            if i == 0:  # CORRIDA - à esquerda
                x = caixa_x + 50
                y = caixa_y + 260
            elif i == 1:  # DRIFT - no meio (abaixo de corrida)
                x = caixa_x + 50
                y = caixa_y + 260 + 50
            else:  # GHOST - à direita (horizontalmente ao lado de corrida)
                x = caixa_x + 270
                y = caixa_y + 260
            rect = pygame.Rect(x, y - 5, 200, 40)
            is_hovering = rect.collidepoint(mouse_x, mouse_y)
            
            if is_hovering:
                hover_animation_tipo[i] = min(1.0, hover_animation_tipo[i] + hover_speed * dt)
            else:
                hover_animation_tipo[i] = max(0.0, hover_animation_tipo[i] - hover_speed * dt)
        
        # Atualizar animações de hover para voltas (para corrida, drift e ghost) - layout horizontal
        if tipo_jogo_atual in (TipoJogo.CORRIDA, TipoJogo.DRIFT, TipoJogo.GHOST):
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
            
            # Desenhar cursor do controle (caixa animada) para modo
            # Verificar se esta opção está sendo navegada (não selecionada)
            cursor_na_opcao = False
            if linha_atual_idx < len(linhas_y_ordenadas):
                linha_y_atual = linhas_y_ordenadas[linha_atual_idx]
                opcoes_na_linha = linhas_opcoes[linha_y_atual]
                if opcao_horizontal_atual < len(opcoes_na_linha):
                    secao_cursor, indice_cursor, _, _ = opcoes_na_linha[opcao_horizontal_atual]
                    if secao_cursor == "modo" and indice_cursor == i:
                        cursor_na_opcao = True
            if cursor_na_opcao and gerenciador_gamepad.obter_numero_controles() > 0:
                tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                cursor_rect = pygame.Rect(
                    caixa_x + 50 - tamanho_cursor,
                    y - 5 - tamanho_cursor,
                    200 + tamanho_cursor * 2,
                    40 + tamanho_cursor * 2
                )
                pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
            
            # Desenhar texto
            texto = render_text(nome, 20, cor_texto, bold=True, pixel_style=True)
            screen.blit(texto, (caixa_x + 60, y))
        
        # Tipo de jogo
        from core.i18n import t
        tipo_titulo = render_text(t("jogo.tipo_jogo"), 24, (255, 255, 255), bold=True, pixel_style=True)
        screen.blit(tipo_titulo, (caixa_x + 50, caixa_y + 220))
        
        for i, (nome, tipo) in enumerate(opcoes_tipo):
            # Layout horizontal: corrida à esquerda, ghost à direita
            if i == 0:  # CORRIDA - à esquerda
                x = caixa_x + 50
                y = caixa_y + 260
            elif i == 1:  # DRIFT - no meio (abaixo de corrida)
                x = caixa_x + 50
                y = caixa_y + 260 + 50
            else:  # GHOST - à direita (horizontalmente ao lado de corrida)
                x = caixa_x + 270
                y = caixa_y + 260
            
            # Verificar se ghost está disponível (para desabilitar visualmente)
            ghost_disponivel = True
            if tipo == TipoJogo.GHOST:
                # Verificar se há ghost para pelo menos uma pista
                # Por enquanto, sempre permitir (verificação será feita ao iniciar)
                ghost_disponivel = True
            
            # Cores baseadas na seleção e hover
            if i == opcao_tipo_atual:
                cor_fundo = (0, 200, 255, 50)
                cor_texto = (0, 200, 255)
            else:
                cor_fundo = (0, 0, 0, 0)
                cor_texto = (255, 255, 255) if ghost_disponivel else (100, 100, 100)
            
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
                screen.blit(opcao_fundo, (x, y - 5))
            
            # Desenhar cursor do controle (caixa animada) para tipo
            # Verificar se esta opção está sendo navegada (não selecionada)
            cursor_na_opcao = False
            if linha_atual_idx < len(linhas_y_ordenadas):
                linha_y_atual = linhas_y_ordenadas[linha_atual_idx]
                opcoes_na_linha = linhas_opcoes[linha_y_atual]
                if opcao_horizontal_atual < len(opcoes_na_linha):
                    secao_cursor, indice_cursor, _, _ = opcoes_na_linha[opcao_horizontal_atual]
                    if secao_cursor == "tipo" and indice_cursor == i:
                        cursor_na_opcao = True
            if cursor_na_opcao and gerenciador_gamepad.obter_numero_controles() > 0:
                tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                cursor_rect = pygame.Rect(
                    x - tamanho_cursor,
                    y - 5 - tamanho_cursor,
                    200 + tamanho_cursor * 2,
                    40 + tamanho_cursor * 2
                )
                pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
            
            # Desenhar texto
            texto = render_text(nome, 20, cor_texto, bold=True, pixel_style=True)
            screen.blit(texto, (x + 10, y))
        
        # Opções de voltas (para corrida, drift e relógio) - layout horizontal
        if tipo_jogo_atual in (TipoJogo.CORRIDA, TipoJogo.DRIFT, TipoJogo.GHOST):
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
                
                # Desenhar cursor do controle (caixa animada) para voltas
                # Verificar se esta opção está sendo navegada (não selecionada)
                cursor_na_opcao = False
                if linha_atual_idx < len(linhas_y_ordenadas):
                    linha_y_atual = linhas_y_ordenadas[linha_atual_idx]
                    opcoes_na_linha = linhas_opcoes[linha_y_atual]
                    if opcao_horizontal_atual < len(opcoes_na_linha):
                        secao_cursor, indice_cursor, _, _ = opcoes_na_linha[opcao_horizontal_atual]
                        if secao_cursor == "voltas" and indice_cursor == i:
                            cursor_na_opcao = True
                if cursor_na_opcao and gerenciador_gamepad.obter_numero_controles() > 0:
                    tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                    cursor_rect = pygame.Rect(
                        x - tamanho_cursor,
                        y - 5 - tamanho_cursor,
                        140 + tamanho_cursor * 2,
                        40 + tamanho_cursor * 2
                    )
                    pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                
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
            elif tipo_jogo_atual == TipoJogo.GHOST:
                titulo_dificuldade = t("dificuldade.dificuldade_tempo")
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
                
                # Desenhar cursor do controle (caixa animada) para dificuldade
                # Verificar se esta opção está sendo navegada (não selecionada)
                cursor_na_opcao = False
                if linha_atual_idx < len(linhas_y_ordenadas):
                    linha_y_atual = linhas_y_ordenadas[linha_atual_idx]
                    opcoes_na_linha = linhas_opcoes[linha_y_atual]
                    if opcao_horizontal_atual < len(opcoes_na_linha):
                        secao_cursor, indice_cursor, _, _ = opcoes_na_linha[opcao_horizontal_atual]
                        if secao_cursor == "dificuldade" and indice_cursor == i:
                            cursor_na_opcao = True
                if cursor_na_opcao and gerenciador_gamepad.obter_numero_controles() > 0:
                    tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                    cursor_rect = pygame.Rect(
                        x - tamanho_cursor,
                        y - 5 - tamanho_cursor,
                        140 + tamanho_cursor * 2,
                        40 + tamanho_cursor * 2
                    )
                    pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                
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
        voltar_texto = render_text(t("menu.selecionar_mapa.voltar"), 24, (0, 200, 255) if voltar_hover else (255, 255, 255), bold=True, pixel_style=True)
        screen.blit(voltar_texto, (caixa_x + 280, caixa_y + caixa_altura - 53))
        
        # Desenhar cursor do controle (caixa animada) para botão iniciar e voltar
        if linha_atual_idx < len(linhas_y_ordenadas):
            linha_y_atual = linhas_y_ordenadas[linha_atual_idx]
            opcoes_na_linha = linhas_opcoes[linha_y_atual]
            if opcao_horizontal_atual < len(opcoes_na_linha):
                secao_cursor, indice_cursor, x_cursor, y_cursor = opcoes_na_linha[opcao_horizontal_atual]
                if secao_cursor in ("iniciar", "voltar") and gerenciador_gamepad.obter_numero_controles() > 0:
                    tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                    if secao_cursor == "iniciar":
                        cursor_largura = 200
                        cursor_altura = 50
                    else:  # voltar
                        cursor_largura = 200
                        cursor_altura = 40
                    cursor_rect = pygame.Rect(
                        x_cursor - tamanho_cursor,
                        y_cursor - tamanho_cursor,
                        cursor_largura + tamanho_cursor * 2,
                        cursor_altura + tamanho_cursor * 2
                    )
                    pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
        
        
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
    
    # Variáveis para cursor do controle (indicador visual)
    animacao_cursor = 0.0  # Animação do cursor (0.0 a 1.0)
    velocidade_animacao_cursor = 3.0  # Velocidade da animação
    
    # Variável para rastrear se o botão voltar está selecionado
    voltar_selecionado = False
    
    # Layout
    caixa_largura = 700
    caixa_altura = 600  # Aumentada para acomodar textos abaixo dos minimapas
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2
    
    # Grid de minimapas (3x3) - diminuído e centralizado
    minimapa_tamanho = 120
    espacamento_horizontal = 15
    espacamento_vertical = 25  # Espaçamento vertical para acomodar texto abaixo (reduzido para dar espaço ao botão voltar)
    altura_texto = 20  # Altura aproximada do texto "Stage X"
    # Calcular posição do grid para centralizar
    largura_total_grid = 3 * minimapa_tamanho + 2 * espacamento_horizontal
    altura_total_grid = 3 * (minimapa_tamanho + altura_texto) + 2 * espacamento_vertical
    grid_x = caixa_x + (caixa_largura - largura_total_grid) // 2
    grid_y = caixa_y + 70  # Movido um pouco para cima para dar espaço aos textos
    colunas = 3
    
    # Animações de hover
    hover_animation = [0.0] * 9
    hover_speed = 8.0
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        
        gerenciador_musica.verificar_fim_musica()
        popup_musica.atualizar(dt)
        
        # Atualizar animação do cursor do controle
        animacao_cursor += dt * velocidade_animacao_cursor
        if animacao_cursor >= 1.0:
            animacao_cursor = 0.0
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        popup_musica.verificar_hover(mouse_x, mouse_y)
        
        # Atualizar animações de hover (apenas se o botão voltar não estiver selecionado)
        if not voltar_selecionado:
            for i in range(9):
                fase_num = i + 1
                col = i % colunas
                linha = i // colunas
                x = grid_x + col * (minimapa_tamanho + espacamento_horizontal)
                y = grid_y + linha * (minimapa_tamanho + altura_texto + espacamento_vertical)
                rect = pygame.Rect(x, y, minimapa_tamanho, minimapa_tamanho)
                
                is_hovering = rect.collidepoint(mouse_x, mouse_y)
                if is_hovering:
                    hover_animation[i] = min(1.0, hover_animation[i] + hover_speed * dt)
                else:
                    hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt)
        else:
            # Se o botão voltar está selecionado, desativar todos os hovers dos mapas
            for i in range(9):
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt * 2)
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return None
            
            # Processar eventos de controle ANTES de outros eventos
            controle_processado = False
            if gerenciador_gamepad.obter_numero_controles() > 0:
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
                
                # Grid navigation (3x3)
                # Calcular posição atual no grid
                fase_idx = fase_selecionada - 1  # Converter para índice 0-8
                linha_atual = fase_idx // colunas
                col_atual = fase_idx % colunas
                
                # Processar o evento baseado no tipo de ação
                # Para D-pad: botão 11=cima, 12=baixo, 13=esquerda, 14=direita
                # Para analógico: eixo 1=vertical, eixo 0=horizontal
                resultado_final = None
                
                if ev.type == pygame.JOYBUTTONDOWN:
                    if ev.button == 11:  # D-pad Up
                        if voltar_selecionado:
                            # Se voltar está selecionado, voltar para a última linha do grid
                            voltar_selecionado = False
                            fase_selecionada = 7  # Última linha, primeira coluna
                            controle_processado = True
                        else:
                            resultado_final = processar_eventos_controle_menu(ev, linha_atual, 0, joystick_id=0, tempo_atual=tempo_atual)
                    elif ev.button == 12:  # D-pad Down
                        if voltar_selecionado:
                            # Já está no voltar, não fazer nada
                            controle_processado = True
                        else:
                            resultado_final = processar_eventos_controle_menu(ev, linha_atual, 0, joystick_id=0, tempo_atual=tempo_atual)
                    elif ev.button == 13:  # D-pad Left
                        if not voltar_selecionado:
                            resultado_final = processar_eventos_controle_menu(ev, col_atual, colunas, joystick_id=0, tempo_atual=tempo_atual)
                    elif ev.button == 14:  # D-pad Right
                        if not voltar_selecionado:
                            resultado_final = processar_eventos_controle_menu(ev, col_atual, colunas, joystick_id=0, tempo_atual=tempo_atual)
                    elif ev.button == 0:  # X - confirmar
                        if voltar_selecionado:
                            return None  # Voltar
                        else:
                            return fase_selecionada
                    elif ev.button == 1:  # Circle - cancelar
                        return None
                elif ev.type == pygame.JOYAXISMOTION:
                    if ev.axis == 1:  # Eixo vertical
                        if voltar_selecionado:
                            # Se voltar está selecionado, processar movimento para voltar ao grid
                            valor = ev.value
                            if valor < -0.7:  # Movimento para cima
                                voltar_selecionado = False
                                fase_selecionada = 7  # Última linha, primeira coluna
                                controle_processado = True
                        else:
                            resultado_final = processar_eventos_controle_menu(ev, linha_atual, 0, joystick_id=0, tempo_atual=tempo_atual)
                    elif ev.axis == 0:  # Eixo horizontal
                        if not voltar_selecionado:
                            resultado_final = processar_eventos_controle_menu(ev, col_atual, colunas, joystick_id=0, tempo_atual=tempo_atual)
                
                # Processar o resultado final
                if resultado_final:
                    controle_processado = True
                    acao = resultado_final.get("acao")
                    
                    if acao == "cima":
                        # Mover para linha acima
                        nova_linha = max(0, linha_atual - 1)
                        fase_selecionada = nova_linha * colunas + col_atual + 1
                        voltar_selecionado = False
                    elif acao == "baixo":
                        # Mover para linha abaixo
                        nova_linha = min(2, linha_atual + 1)  # Máximo 2 linhas (0, 1, 2)
                        if nova_linha == 2 and linha_atual == 2:
                            # Se já está na última linha e pressionou baixo novamente, ir para voltar
                            voltar_selecionado = True
                        else:
                            fase_selecionada = nova_linha * colunas + col_atual + 1
                            voltar_selecionado = False
                    elif acao == "esquerda":
                        # Mover para coluna à esquerda
                        if "opcao" in resultado_final:
                            nova_col = resultado_final["opcao"]
                        else:
                            nova_col = max(0, col_atual - 1)
                        fase_selecionada = linha_atual * colunas + nova_col + 1
                        voltar_selecionado = False
                    elif acao == "direita":
                        # Mover para coluna à direita
                        if "opcao" in resultado_final:
                            nova_col = resultado_final["opcao"]
                        else:
                            nova_col = min(colunas - 1, col_atual + 1)
                        fase_selecionada = linha_atual * colunas + nova_col + 1
                        voltar_selecionado = False
                    elif acao == "confirmar":
                        if voltar_selecionado:
                            return None
                        else:
                            return fase_selecionada
                    elif acao == "cancelar":
                        return None
                
            
            # Se processou evento de controle, não processar mouse/teclado para esse evento
            if controle_processado:
                continue
            
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # Verificar clique em minimapa
                for i in range(9):
                    fase_num = i + 1
                    col = i % colunas
                    linha = i // colunas
                    x = grid_x + col * (minimapa_tamanho + espacamento_horizontal)
                    y = grid_y + linha * (minimapa_tamanho + altura_texto + espacamento_vertical)
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
                # Grid navigation (3x3)
                fase_idx = fase_selecionada - 1  # Converter para índice 0-8
                linha_atual = fase_idx // colunas
                col_atual = fase_idx % colunas
                
                if ev.key in (pygame.K_LEFT, pygame.K_a):
                    # Mover para coluna à esquerda
                    nova_col = max(0, col_atual - 1)
                    fase_selecionada = linha_atual * colunas + nova_col + 1
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    # Mover para coluna à direita
                    nova_col = min(colunas - 1, col_atual + 1)
                    fase_selecionada = linha_atual * colunas + nova_col + 1
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    # Mover para linha acima
                    nova_linha = max(0, linha_atual - 1)
                    fase_selecionada = nova_linha * colunas + col_atual + 1
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    # Mover para linha abaixo
                    nova_linha = min(2, linha_atual + 1)  # Máximo 2 linhas (0, 1, 2)
                    fase_selecionada = nova_linha * colunas + col_atual + 1
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
            x = grid_x + col * (minimapa_tamanho + espacamento_horizontal)
            y = grid_y + linha * (minimapa_tamanho + altura_texto + espacamento_vertical)
            
            # Cores baseadas na seleção e hover
            # Se o botão voltar está selecionado, não mostrar nenhum mapa como selecionado
            is_selected = (fase_num == fase_selecionada) and not voltar_selecionado
            hover_progress = hover_animation[i] if not voltar_selecionado else 0.0
            
            if is_selected:
                cor_borda = (0, 200, 255)
                espessura_borda = 4
            else:
                cor_borda = (128, 128, 128)
                espessura_borda = 2
            
            # Aplicar hover apenas se o botão voltar não estiver selecionado
            if hover_progress > 0 and not voltar_selecionado:
                cor_borda_hover = (0, 255, 0)
                cor_borda = (
                    int(cor_borda[0] + (cor_borda_hover[0] - cor_borda[0]) * hover_progress),
                    int(cor_borda[1] + (cor_borda_hover[1] - cor_borda[1]) * hover_progress),
                    int(cor_borda[2] + (cor_borda_hover[2] - cor_borda[2]) * hover_progress)
                )
            
            # Desenhar fundo do minimapa
            pygame.draw.rect(screen, (0, 0, 0), (x, y, minimapa_tamanho, minimapa_tamanho))
            pygame.draw.rect(screen, cor_borda, (x, y, minimapa_tamanho, minimapa_tamanho), espessura_borda)
            
            # Desenhar cursor do controle (caixa animada) para fase selecionada
            if is_selected and gerenciador_gamepad.obter_numero_controles() > 0:
                tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                cursor_rect = pygame.Rect(
                    x - tamanho_cursor,
                    y - tamanho_cursor,
                    minimapa_tamanho + tamanho_cursor * 2,
                    minimapa_tamanho + tamanho_cursor * 2
                )
                pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
            
            # Desenhar minimapa se disponível (usar versão já redimensionada do cache)
            if fase_num in minimapas_redimensionados:
                screen.blit(minimapas_redimensionados[fase_num], (x + 5, y + 5))
            else:
                # Fallback: desenhar número da fase
                texto_fase = render_text(t("jogo.fase_numero").format(fase_num), 24, (255, 255, 255), bold=True, pixel_style=True)
                texto_x = x + (minimapa_tamanho - texto_fase.get_width()) // 2
                texto_y = y + (minimapa_tamanho - texto_fase.get_height()) // 2
                screen.blit(texto_fase, (texto_x, texto_y))
            
            # Desenhar número da fase abaixo do minimapa (com mais espaçamento vertical)
            texto_num = render_text(t("jogo.fase_numero").format(fase_num), 14, (255, 255, 255), bold=True, pixel_style=True)
            texto_num_x = x + (minimapa_tamanho - texto_num.get_width()) // 2
            screen.blit(texto_num, (texto_num_x, y + minimapa_tamanho + 10))
            
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
        # Desenhar cursor do controle (caixa animada) para botão voltar APENAS se estiver selecionado
        if voltar_selecionado and gerenciador_gamepad.obter_numero_controles() > 0:
            tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
            cursor_rect = pygame.Rect(
                voltar_rect.x - tamanho_cursor,
                voltar_rect.y - tamanho_cursor,
                voltar_rect.width + tamanho_cursor * 2,
                voltar_rect.height + tamanho_cursor * 2
            )
            pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
        voltar_texto = render_text("VOLTAR", 20, (0, 200, 255) if (voltar_hover or voltar_selecionado) else (255, 255, 255), bold=True, pixel_style=True)
        voltar_texto_x = voltar_x + (voltar_largura - voltar_texto.get_width()) // 2
        voltar_texto_y = voltar_y + (voltar_altura - voltar_texto.get_height()) // 2
        screen.blit(voltar_texto, (voltar_texto_x, voltar_texto_y))
        
        # Desenhar popup de música
        popup_musica.desenhar(screen)
        
        pygame.display.flip()

def recordes_loop(screen):
    """Tela de recordes mostrando melhores tempos por pista (corrida e drift)"""
    from core.progresso import gerenciador_progresso
    from config import CAMINHO_TROFEU_OURO, CAMINHO_TROFEU_PRATA, CAMINHO_TROFEU_BRONZE, CAMINHO_TROFEU_VAZIO, DIR_ICONS
    
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
    
    # Carregar ícone de recorde vazio
    recorde_vazio = None
    caminho_recorde_vazio = os.path.join(DIR_ICONS, "recorde_vazio.png")
    if os.path.exists(caminho_recorde_vazio):
        try:
            recorde_vazio_raw = pygame.image.load(caminho_recorde_vazio).convert_alpha()
            recorde_vazio = pygame.transform.scale(recorde_vazio_raw, (40, 40))
        except:
            pass
    
    clock = pygame.time.Clock()
    
    # Layout - três seções lado a lado
    caixa_largura = 1200
    caixa_altura = 650
    caixa_x = (LARGURA - caixa_largura) // 2
    caixa_y = (ALTURA - caixa_altura) // 2
    
    # Estado de seleção (cursor começa no botão voltar)
    voltar_selecionado = True
    animacao_cursor = 0.0
    
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
        
        # Atualizar animação do cursor
        animacao_cursor += dt * 3.0
        
        gerenciador_musica.verificar_fim_musica()
        popup_musica.atualizar(dt)
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        popup_musica.verificar_hover(mouse_x, mouse_y)
        
        # Verificar estado contínuo do controle para "hold"
        if gerenciador_gamepad.obter_numero_controles() > 0:
            from core.menu_controles import obter_estado_controle_menu
            estado_controle = obter_estado_controle_menu(joystick_id=0)
            tempo_atual = pygame.time.get_ticks()
            
            # Processar navegação contínua quando botão está sendo mantido pressionado
            if voltar_selecionado:
                # Se está no botão voltar, qualquer ação de navegação não faz nada (só confirmar/cancelar)
                pass
            else:
                # Se não está no botão voltar, navegação não faz sentido (só tem um botão)
                pass
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            
            # Processar eventos de controle
            controle_processado = False
            if gerenciador_gamepad.obter_numero_controles() > 0:
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
                resultado_controle = processar_eventos_controle_menu(ev, 0, 1, joystick_id=0, tempo_atual=tempo_atual)
                if resultado_controle:
                    controle_processado = True
                    acao = resultado_controle.get("acao")
                    if acao == "cancelar":
                        return True
                    elif acao == "confirmar":
                        # Voltar (mesma lógica do clique)
                        return True
                    elif acao in ("cima", "baixo", "esquerda", "direita"):
                        # Navegação não faz sentido na tela de recordes (só tem um botão)
                        # Mas manter o cursor no botão voltar
                        voltar_selecionado = True
            
            # Se processou evento de controle, não processar mouse/teclado para esse evento
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
        
        # Criar superfície para conteúdo com scroll
        conteudo_surface = pygame.Surface((caixa_largura, caixa_altura - 100), pygame.SRCALPHA)
        conteudo_surface.fill((0, 0, 0, 0))
        
        # === SEÇÃO CORRIDA ===
        from core.i18n import t
        y_secao_corrida = 20
        titulo_corrida = fonte_secao.render(t("recordes.corrida"), True, (0, 200, 255))
        conteudo_surface.blit(titulo_corrida, (30, y_secao_corrida))
        
        y_inicial_corrida = y_secao_corrida + 35
        x_pista = 30
        x_trofeu = 150
        x_tempo = 220
        
        # Cabeçalhos corrida
        cabecalho_pista = fonte_cabecalho.render(t("recordes.pista"), True, (255, 255, 255))
        cabecalho_trofeu = fonte_cabecalho.render(t("recordes.trofeu"), True, (255, 255, 255))
        cabecalho_tempo = fonte_cabecalho.render(t("recordes.melhor_tempo"), True, (255, 255, 255))
        
        conteudo_surface.blit(cabecalho_pista, (x_pista, y_inicial_corrida))
        conteudo_surface.blit(cabecalho_trofeu, (x_trofeu, y_inicial_corrida))
        conteudo_surface.blit(cabecalho_tempo, (x_tempo, y_inicial_corrida))
        
        # Linha separadora
        pygame.draw.line(conteudo_surface, (128, 128, 128), 
                        (20, y_inicial_corrida + 30), 
                        (caixa_largura // 3 - 20, y_inicial_corrida + 30), 2)
        
        # Listar recordes de corrida das 9 pistas
        y_atual = y_inicial_corrida + 45
        for pista_num in range(1, 10):
            # Nome da pista
            texto_pista = fonte_item.render(t("recordes.pista_numero").format(pista_num), True, (255, 255, 255))
            conteudo_surface.blit(texto_pista, (x_pista, y_atual))
            
            # Troféu (sempre mostrar, vazio se não ganhou)
            trofeu_tipo = gerenciador_progresso.obter_trofeu(pista_num)
            recorde = gerenciador_progresso.obter_recorde(pista_num)
            
            # Se não tem recorde, mostrar ícone de recorde vazio
            if recorde is None:
                if recorde_vazio:
                    conteudo_surface.blit(recorde_vazio, (x_trofeu, y_atual - 5))
                elif trofeu_vazio:
                    conteudo_surface.blit(trofeu_vazio, (x_trofeu, y_atual - 5))
            elif trofeu_tipo == "ouro" and trofeu_ouro:
                conteudo_surface.blit(trofeu_ouro, (x_trofeu, y_atual - 5))
            elif trofeu_tipo == "prata" and trofeu_prata:
                conteudo_surface.blit(trofeu_prata, (x_trofeu, y_atual - 5))
            elif trofeu_tipo == "bronze" and trofeu_bronze:
                conteudo_surface.blit(trofeu_bronze, (x_trofeu, y_atual - 5))
            else:
                if trofeu_vazio:
                    conteudo_surface.blit(trofeu_vazio, (x_trofeu, y_atual - 5))
            
            # Tempo
            texto_tempo = fonte_item.render(formatar_tempo(recorde), True, 
                                          (0, 255, 0) if recorde else (128, 128, 128))
            conteudo_surface.blit(texto_tempo, (x_tempo, y_atual))
            
            y_atual += 45
        
        # === SEÇÃO DRIFT ===
        y_secao_drift = 20
        x_drift = caixa_largura // 3 + 30
        titulo_drift = fonte_secao.render(t("recordes.drift"), True, (255, 200, 0))
        conteudo_surface.blit(titulo_drift, (x_drift, y_secao_drift))
        
        y_inicial_drift = y_secao_drift + 35
        x_pista_drift = x_drift
        x_trofeu_drift = x_drift + 120
        x_score_drift = x_drift + 200
        
        # Cabeçalhos drift
        cabecalho_pista_drift = fonte_cabecalho.render(t("recordes.pista"), True, (255, 255, 255))
        cabecalho_trofeu_drift = fonte_cabecalho.render(t("recordes.trofeu"), True, (255, 255, 255))
        cabecalho_score = fonte_cabecalho.render(t("jogo.melhor_score"), True, (255, 255, 255))
        
        conteudo_surface.blit(cabecalho_pista_drift, (x_pista_drift, y_inicial_drift))
        conteudo_surface.blit(cabecalho_trofeu_drift, (x_trofeu_drift, y_inicial_drift))
        conteudo_surface.blit(cabecalho_score, (x_score_drift, y_inicial_drift))
        
        # Linha separadora
        pygame.draw.line(conteudo_surface, (128, 128, 128), 
                        (x_drift - 10, y_inicial_drift + 30), 
                        (caixa_largura // 3 * 2 - 20, y_inicial_drift + 30), 2)
        
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
            conteudo_surface.blit(texto_pista, (x_pista_drift, y_atual_drift))
            
            # Troféu baseado na pontuação
            recorde_drift = gerenciador_progresso.obter_recorde_drift(pista_num)
            trofeu_tipo_drift = obter_trofeu_por_pontuacao(recorde_drift)
            
            # Se não tem recorde, mostrar ícone de recorde vazio
            if recorde_drift is None:
                if recorde_vazio:
                    conteudo_surface.blit(recorde_vazio, (x_trofeu_drift, y_atual_drift - 5))
                elif trofeu_vazio:
                    conteudo_surface.blit(trofeu_vazio, (x_trofeu_drift, y_atual_drift - 5))
            elif trofeu_tipo_drift == "ouro" and trofeu_ouro:
                conteudo_surface.blit(trofeu_ouro, (x_trofeu_drift, y_atual_drift - 5))
            elif trofeu_tipo_drift == "prata" and trofeu_prata:
                conteudo_surface.blit(trofeu_prata, (x_trofeu_drift, y_atual_drift - 5))
            elif trofeu_tipo_drift == "bronze" and trofeu_bronze:
                conteudo_surface.blit(trofeu_bronze, (x_trofeu_drift, y_atual_drift - 5))
            else:
                # Sempre mostrar troféu vazio se não ganhou troféu
                if trofeu_vazio:
                    conteudo_surface.blit(trofeu_vazio, (x_trofeu_drift, y_atual_drift - 5))
            
            # Score
            texto_score = fonte_item.render(formatar_score(recorde_drift), True, 
                                          (255, 200, 0) if recorde_drift else (128, 128, 128))
            conteudo_surface.blit(texto_score, (x_score_drift, y_atual_drift))
            
            y_atual_drift += 45
        
        # === SEÇÃO RELÓGIO ===
        from core.ghost import GerenciadorGhosts
        gerenciador_ghosts = GerenciadorGhosts()
        
        y_secao_relogio = 20
        x_relogio = caixa_largura // 3 * 2 + 30
        titulo_relogio = fonte_secao.render(t("recordes.relogio"), True, (100, 255, 100))
        conteudo_surface.blit(titulo_relogio, (x_relogio, y_secao_relogio))
        
        y_inicial_relogio = y_secao_relogio + 35
        x_pista_relogio = x_relogio
        x_trofeu_relogio = x_relogio + 120
        x_tempo_relogio = x_relogio + 200
        
        # Cabeçalhos relógio
        cabecalho_pista_relogio = fonte_cabecalho.render(t("recordes.pista"), True, (255, 255, 255))
        cabecalho_trofeu_relogio = fonte_cabecalho.render(t("recordes.trofeu"), True, (255, 255, 255))
        cabecalho_tempo_relogio = fonte_cabecalho.render(t("recordes.melhor_tempo"), True, (255, 255, 255))
        
        conteudo_surface.blit(cabecalho_pista_relogio, (x_pista_relogio, y_inicial_relogio))
        conteudo_surface.blit(cabecalho_trofeu_relogio, (x_trofeu_relogio, y_inicial_relogio))
        conteudo_surface.blit(cabecalho_tempo_relogio, (x_tempo_relogio, y_inicial_relogio))
        
        # Linha separadora
        pygame.draw.line(conteudo_surface, (128, 128, 128), 
                        (x_relogio - 10, y_inicial_relogio + 30), 
                        (caixa_largura - 20, y_inicial_relogio + 30), 2)
        
        # Listar recordes de relógio das 9 pistas
        y_atual_relogio = y_inicial_relogio + 45
        for pista_num in range(1, 10):
            # Nome da pista
            texto_pista = fonte_item.render(t("recordes.pista_numero").format(pista_num), True, (255, 255, 255))
            conteudo_surface.blit(texto_pista, (x_pista_relogio, y_atual_relogio))
            
            # Verificar se há ghost (que indica que há um recorde)
            ghost = gerenciador_ghosts.obter_ghost(pista_num)
            if ghost and len(ghost) > 0:
                # Calcular tempo do ghost (último frame tem o tempo)
                tempo_ghost = ghost[-1][0] if ghost else None
                
                # Troféu baseado no tempo (usar mesmo sistema de troféus de corrida)
                trofeu_tipo = gerenciador_progresso.obter_trofeu(pista_num)
                
                # Se não tem tempo de ghost, mostrar ícone de recorde vazio
                if tempo_ghost is None:
                    if recorde_vazio:
                        conteudo_surface.blit(recorde_vazio, (x_trofeu_relogio, y_atual_relogio - 5))
                    elif trofeu_vazio:
                        conteudo_surface.blit(trofeu_vazio, (x_trofeu_relogio, y_atual_relogio - 5))
                elif trofeu_tipo == "ouro" and trofeu_ouro:
                    conteudo_surface.blit(trofeu_ouro, (x_trofeu_relogio, y_atual_relogio - 5))
                elif trofeu_tipo == "prata" and trofeu_prata:
                    conteudo_surface.blit(trofeu_prata, (x_trofeu_relogio, y_atual_relogio - 5))
                elif trofeu_tipo == "bronze" and trofeu_bronze:
                    conteudo_surface.blit(trofeu_bronze, (x_trofeu_relogio, y_atual_relogio - 5))
                else:
                    if trofeu_vazio:
                        conteudo_surface.blit(trofeu_vazio, (x_trofeu_relogio, y_atual_relogio - 5))
                
                # Tempo
                texto_tempo = fonte_item.render(formatar_tempo(tempo_ghost), True, (100, 255, 100))
                conteudo_surface.blit(texto_tempo, (x_tempo_relogio, y_atual_relogio))
            else:
                # Sem recorde
                if recorde_vazio:
                    conteudo_surface.blit(recorde_vazio, (x_trofeu_relogio, y_atual_relogio - 5))
                elif trofeu_vazio:
                    conteudo_surface.blit(trofeu_vazio, (x_trofeu_relogio, y_atual_relogio - 5))
                texto_tempo = fonte_item.render(formatar_tempo(None), True, (128, 128, 128))
                conteudo_surface.blit(texto_tempo, (x_tempo_relogio, y_atual_relogio))
            
            y_atual_relogio += 45
        
        # Blitar conteúdo
        screen.blit(conteudo_surface, (caixa_x, caixa_y + 100))
        
        # Botão voltar
        voltar_largura = 120
        voltar_altura = 40
        voltar_x = caixa_x + (caixa_largura - voltar_largura) // 2
        voltar_y = caixa_y + caixa_altura - 50
        voltar_rect = pygame.Rect(voltar_x, voltar_y, voltar_largura, voltar_altura)
        voltar_hover = voltar_rect.collidepoint(mouse_x, mouse_y)
        if voltar_hover:
            pygame.draw.rect(screen, (0, 200, 255, 50), voltar_rect)
        # Desenhar cursor do controle (caixa animada) para botão voltar se estiver selecionado
        if voltar_selecionado and gerenciador_gamepad.obter_numero_controles() > 0:
            tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
            cursor_rect = pygame.Rect(
                voltar_rect.x - tamanho_cursor,
                voltar_rect.y - tamanho_cursor,
                voltar_rect.width + tamanho_cursor * 2,
                voltar_rect.height + tamanho_cursor * 2
            )
            pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
        voltar_texto = render_text("VOLTAR", 20, (0, 200, 255) if (voltar_hover or voltar_selecionado) else (255, 255, 255), bold=True, pixel_style=True)
        voltar_texto_x = voltar_x + (voltar_largura - voltar_texto.get_width()) // 2
        voltar_texto_y = voltar_y + (voltar_altura - voltar_texto.get_height()) // 2
        screen.blit(voltar_texto, (voltar_texto_x, voltar_texto_y))
        
        # Desenhar popup de música
        popup_musica.desenhar(screen)
        
        pygame.display.flip()

def _verificar_corrida_completa(numero_pista):
    """Verifica se uma corrida foi completada baseado nas estatísticas"""
    from core.estatisticas import gerenciador_estatisticas
    gerenciador_estatisticas.carregar()
    stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(numero_pista)
    if stats_pista:
        melhor_tempo = stats_pista.get("melhor_tempo")
        melhor_posicao = stats_pista.get("melhor_posicao")
        corridas_completas = stats_pista.get("corridas_completas", 0)
        resultado = melhor_tempo is not None and melhor_posicao is not None
        print(f"[VERIFICAR_CORRIDA] Pista {numero_pista}: tempo={melhor_tempo}, posicao={melhor_posicao}, completas={corridas_completas}, resultado={resultado}")
        return resultado
    print(f"[VERIFICAR_CORRIDA] Pista {numero_pista}: stats_pista é None ou vazio")
    return False

def _iniciar_narrativa_pos_training_01(narrative_system, gerenciador_progresso):
    """Inicia a narrativa pós-training_01 com base nas estatísticas"""
    from core.estatisticas import gerenciador_estatisticas
    from core.missoes import gerenciador_missoes
    
    # Verificar se a flag já foi limpa - se sim, não processar novamente
    if not hasattr(gerenciador_progresso, 'ultima_corrida_campanha') or gerenciador_progresso.ultima_corrida_campanha != "training_01":
        print(f"[INICIAR_NARRATIVA] Flag ultima_corrida_campanha não é 'training_01' (é {getattr(gerenciador_progresso, 'ultima_corrida_campanha', None)}). Pulando.")
        return
    
    # Se a narrativa já está ativa com a cena de resultado, não reiniciar
    if narrative_system.active and narrative_system.current_scene_id in ["ch1_1c_crank_test_result", "ch1_6_post_first_race_and_pixel", "ch1_6_post_race", "ch1_7_pixel_voice_intro"]:
        print(f"[INICIAR_NARRATIVA] Narrativa já está ativa com a cena {narrative_system.current_scene_id}. Pulando reinicialização.")
        # Limpar flag mesmo assim para evitar loop
        gerenciador_progresso.ultima_corrida_campanha = None
        gerenciador_progresso.salvar()
        return
    
    # Se a cena ch1_6_post_race ou ch1_7_pixel_voice_intro já foi visitada, não reiniciar
    if "ch1_6_post_race" in narrative_system.scenes_visited or "ch1_7_pixel_voice_intro" in narrative_system.scenes_visited:
        print(f"[INICIAR_NARRATIVA] Cena pós-corrida já foi visitada. Limpando flag e pulando.")
        gerenciador_progresso.ultima_corrida_campanha = None
        gerenciador_progresso.salvar()
        return
    
    # Garantir que a cena anterior não seja reiniciada
    if "ch1_1b_crank_test_briefing" not in narrative_system.scenes_visited:
        narrative_system.scenes_visited.add("ch1_1b_crank_test_briefing")
        print(f"[INICIAR_NARRATIVA] Cena ch1_1b_crank_test_briefing marcada como visitada para evitar loop")
    
    print(f"[INICIAR_NARRATIVA] Iniciando narrativa pós-training_01...")
    
    # Obter posição para lastRaceResult
    gerenciador_estatisticas.carregar()
    stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(1)
    melhor_posicao = stats_pista.get("melhor_posicao", 1) if stats_pista else 1
    melhor_tempo = stats_pista.get("melhor_tempo") if stats_pista else None
    print(f"[INICIAR_NARRATIVA] Estatísticas pista 1: melhor_posicao={melhor_posicao}, melhor_tempo={melhor_tempo}")
    
    # Configurar narrativa
    if not narrative_system.current_chapter_id:
        narrative_system.current_chapter_id = "ch1"
    narrative_system.variables["lastRaceResult"] = "win" if melhor_posicao == 1 else "lose"
    print(f"[INICIAR_NARRATIVA] lastRaceResult definido como: {narrative_system.variables['lastRaceResult']}")
    
    # Garantir que ch1_0_prologue está marcada como visitada para evitar reiniciar
    if "ch1_0_prologue" not in narrative_system.scenes_visited:
        narrative_system.scenes_visited.add("ch1_0_prologue")
        print(f"[INICIAR_NARRATIVA] Cena ch1_0_prologue marcada como visitada para evitar reiniciar")
    
    # Tentar usar o sistema de triggers primeiro
    context = {
        "raceId": "training_01",
        "raceResult": narrative_system.variables["lastRaceResult"]
    }
    if narrative_system.verificar_gatilhos_pendentes(context):
        print(f"[INICIAR_NARRATIVA] Gatilho encontrado e cena iniciada via verificar_gatilhos_pendentes")
        narrative_system.active = True
        # Salvar missões antes de limpar flag
        from core.missoes import gerenciador_missoes
        gerenciador_missoes.salvar()
        # Limpar flag
        if hasattr(gerenciador_progresso, 'ultima_corrida_campanha'):
            gerenciador_progresso.ultima_corrida_campanha = None
            gerenciador_progresso.salvar()
            print(f"[INICIAR_NARRATIVA] Flag ultima_corrida_campanha limpa")
        return
    
    # Fallback: tentar iniciar ch1_6_post_race (cena correta após training_01 iniciada por ch1_5_race_briefing)
    # Se não funcionar, tentar ch1_1c_crank_test_result (cena antiga)
    cena_fallback = "ch1_6_post_race"
    if cena_fallback not in narrative_system.scenes_visited:
        resultado = narrative_system._iniciar_cena_sem_transicao(cena_fallback)
        if resultado:
            # Se retornou um trigger (dicionário), não ativar narrativa aqui - o trigger será processado
            if isinstance(resultado, dict) and "trigger" in resultado:
                print(f"[INICIAR_NARRATIVA] Trigger retornado: {resultado}")
                # Não definir active=True aqui, o trigger será processado pelo loop principal
                return
            narrative_system.active = True
            narrative_system.current_line_index = 0
            print(f"[INICIAR_NARRATIVA] Cena {cena_fallback} iniciada. active={narrative_system.active}, scene_id={narrative_system.current_scene_id}")
        else:
            # Se não conseguiu iniciar ch1_6_post_race, tentar ch1_1c_crank_test_result
            resultado = narrative_system._iniciar_cena_sem_transicao("ch1_1c_crank_test_result")
            if isinstance(resultado, dict) and "trigger" in resultado:
                print(f"[INICIAR_NARRATIVA] Trigger retornado: {resultado}")
                return
            narrative_system.active = True
            narrative_system.current_line_index = 0
            print(f"[INICIAR_NARRATIVA] Cena ch1_1c_crank_test_result iniciada (fallback). active={narrative_system.active}, scene_id={narrative_system.current_scene_id}")
    else:
        print(f"[INICIAR_NARRATIVA] Cena {cena_fallback} já foi visitada, não reiniciando")
    
    # Salvar missões antes de limpar flag
    from core.missoes import gerenciador_missoes
    gerenciador_missoes.salvar()
    
    # Limpar flag
    if hasattr(gerenciador_progresso, 'ultima_corrida_campanha'):
        gerenciador_progresso.ultima_corrida_campanha = None
        gerenciador_progresso.salvar()
        print(f"[INICIAR_NARRATIVA] Flag ultima_corrida_campanha limpa")

def _verificar_e_iniciar_narrativa_training_01(narrative_system, gerenciador_progresso):
    """Verifica se training_01 foi completada e inicia narrativa se necessário"""
    from core.missoes import gerenciador_missoes
    
    # Se a narrativa já está ativa, não reiniciar
    if narrative_system.active:
        return False
    
    # Se as cenas pós-corrida já foram visitadas, não verificar novamente
    if "ch1_6_post_race" in narrative_system.scenes_visited or "ch1_7_pixel_voice_intro" in narrative_system.scenes_visited:
        # Limpar flag se ainda estiver definida para evitar loop
        if hasattr(gerenciador_progresso, 'ultima_corrida_campanha') and gerenciador_progresso.ultima_corrida_campanha:
            gerenciador_progresso.ultima_corrida_campanha = None
            gerenciador_progresso.salvar()
        return False
    
    # Se Pixel já foi visto, não verificar novamente
    if gerenciador_progresso.pixel_primeira_aparicao_mostrada:
        # Limpar flag se ainda estiver definida para evitar loop
        if hasattr(gerenciador_progresso, 'ultima_corrida_campanha') and gerenciador_progresso.ultima_corrida_campanha:
            gerenciador_progresso.ultima_corrida_campanha = None
            gerenciador_progresso.salvar()
        return False
    
    if hasattr(gerenciador_progresso, 'ultima_corrida_campanha'):
        if gerenciador_progresso.ultima_corrida_campanha and gerenciador_progresso.ultima_corrida_campanha != "training_01":
            # Limpar flag de corrida desconhecida para evitar loop
            print(f"[VERIFICAR_TRAINING_01] Flag ultima_corrida_campanha é '{gerenciador_progresso.ultima_corrida_campanha}', não 'training_01'. Limpando para evitar loop.")
            gerenciador_progresso.ultima_corrida_campanha = None
            gerenciador_progresso.salvar()
            return False
    
    # Verificar se já completou a corrida
    corrida_completa = _verificar_corrida_completa(1)
    missao_completa = gerenciador_missoes.esta_completa("m6_batismo_de_pista")
    
    # Se completou mas Pixel ainda não foi visto E a flag é 'training_01'
    if (corrida_completa or missao_completa) and not gerenciador_progresso.pixel_primeira_aparicao_mostrada:
        # Verificar novamente se a flag é 'training_01' antes de processar
        if hasattr(gerenciador_progresso, 'ultima_corrida_campanha') and gerenciador_progresso.ultima_corrida_campanha == "training_01":
            _iniciar_narrativa_pos_training_01(narrative_system, gerenciador_progresso)
            return True
        else:
            # Se a flag não é 'training_01', limpar e não processar
            if hasattr(gerenciador_progresso, 'ultima_corrida_campanha') and gerenciador_progresso.ultima_corrida_campanha:
                print(f"[VERIFICAR_TRAINING_01] Corrida completa mas flag não é 'training_01' (é '{gerenciador_progresso.ultima_corrida_campanha}'). Limpando.")
                gerenciador_progresso.ultima_corrida_campanha = None
                gerenciador_progresso.salvar()
    return False

def run():
    from config import CONFIGURACOES, carregar_configuracoes
    
    # Verificar se m14_tres_mundos deve ser completada logo no início (reputação >= 500)
    try:
        from core.status_jogador import status_jogador
        from core.missoes import gerenciador_missoes
        # Garantir que o status está carregado
        status_jogador.carregar()
        popularidade_atual = status_jogador.popularidade
        print(f"[RUN] Verificando reputação no início do jogo: {popularidade_atual:.1f}/500, missao_ativa={gerenciador_missoes.missao_ativa_id}, m14_completa={'m14_tres_mundos' in gerenciador_missoes.missoes_completas}")
        if popularidade_atual >= 500.0:
            if gerenciador_missoes.missao_ativa_id == "m14_tres_mundos":
                if "m14_tres_mundos" not in gerenciador_missoes.missoes_completas:
                    print(f"[RUN] Reputação já está em 500! Completando missão m14_tres_mundos no início do jogo...")
                    gerenciador_missoes.completar_missao("m14_tres_mundos")
                    gerenciador_missoes.salvar()
    except Exception as e:
        print(f"[RUN] Erro ao verificar reputação para m14_tres_mundos no início: {e}")
        import traceback
        traceback.print_exc()
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
        resultado_menu = menu_loop(screen)
        if isinstance(resultado_menu, tuple) and len(resultado_menu) == 2:
            escolha, nova_tela = resultado_menu
            screen = nova_tela
        else:
            escolha = resultado_menu
        
        if escolha == Escolha.JOGAR:
            # Ir direto para o modo arcade (campanha removida)
            # Abrir tela de seleção de modo de jogo (Arcade)
            resultado_modo = modo_jogo_loop(screen)
            if resultado_modo is None:
                continue  # Cancelou, voltar ao menu
            
            if isinstance(resultado_modo, tuple):  # Se não cancelou e é uma tupla
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
                
                # Sempre permitir seleção de carro no modo arcade (após selecionar a pista)
                # A função está definida no mesmo módulo, então podemos chamá-la diretamente
                resultado_selecao = selecionar_carros_loop(screen, modo_arcade=True, modo_jogo=modo_jogo)
                # Verificar se cancelou (None ou (None, None)) - voltar ao menu
                if resultado_selecao is None or (isinstance(resultado_selecao, tuple) and len(resultado_selecao) == 2 and resultado_selecao[0] is None and resultado_selecao[1] is None):
                    continue  # Cancelou, voltar ao menu
                
                if isinstance(resultado_selecao, tuple):
                    carro_p1, carro_p2 = resultado_selecao
                    # Verificar se ambos são None (cancelamento)
                    if carro_p1 is None and carro_p2 is None:
                        continue  # Cancelou, voltar ao menu
                else:
                    carro_p1 = resultado_selecao
                    carro_p2 = 0
                
                # Parar música do menu se não deve tocar no jogo
                if not CONFIGURACOES["audio"]["musica_no_jogo"]:
                    gerenciador_musica.parar_musica()
                
                # Iniciar jogo no modo arcade
                import main
                main.principal(
                    carro_selecionado_p1=carro_p1,
                    carro_selecionado_p2=carro_p2,
                    modo_jogo=modo_jogo,
                    tipo_jogo=tipo_jogo,
                    voltas=voltas,
                    dificuldade_ia=dificuldade_ia,
                    modo_arcade=True,
                    mapa_selecionado=fase_selecionada
                )
                
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
            
            # Pular todo o código de campanha abaixo
            continue
            
            # CÓDIGO DE CAMPANHA REMOVIDO - COMEÇA AQUI:
            if False:  # Nunca executar
                # Loop de campanha - inicia com narrativa e alterna com gameplay
                from core.mapa_cidade import mapa_cidade_loop
                from core.hub_territorio import hub_territorio_loop
                from core.mapa_cidade import carregar_areas_mapa
                from core.narrative_system import narrative_system
                from core.progresso import gerenciador_progresso
                from core.missoes import gerenciador_missoes
                
                # Verificar se m14_tres_mundos deve ser completada ao iniciar campanha (reputação >= 500)
                try:
                    from core.status_jogador import status_jogador
                    # Garantir que o status está carregado
                    status_jogador.carregar()
                    popularidade_atual = status_jogador.popularidade
                    print(f"[CAMPANHA] Verificando reputação ao iniciar campanha: {popularidade_atual:.1f}/500, missao_ativa={gerenciador_missoes.missao_ativa_id}")
                    if popularidade_atual >= 500.0:
                        if gerenciador_missoes.missao_ativa_id == "m14_tres_mundos":
                            if "m14_tres_mundos" not in gerenciador_missoes.missoes_completas:
                                print(f"[CAMPANHA] Reputação já está em 500! Completando missão m14_tres_mundos ao iniciar campanha...")
                                gerenciador_missoes.completar_missao("m14_tres_mundos")
                                gerenciador_missoes.salvar()
                except Exception as e:
                    print(f"[CAMPANHA] Erro ao verificar reputação para m14_tres_mundos ao iniciar campanha: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Função auxiliar para executar loop de narrativa
                def executar_narrativa():
                    """Executa o loop de narrativa até encontrar um trigger ou terminar"""
                    if narrative_system.current_scene_id and not narrative_system.active:
                        print(f"[EXECUTAR_NARRATIVA] Cena {narrative_system.current_scene_id} existe mas narrativa não está ativa. Ativando...")
                        narrative_system.active = True
                    
                    # Verificar se há um trigger pendente antes de iniciar o loop
                    # Isso pode acontecer se uma cena já foi vista e retornou um trigger
                    if narrative_system.active and narrative_system.current_scene_id:
                        scene = narrative_system._obter_cena_atual()
                        if scene:
                            # Verificar se a cena já foi vista e tem um trigger
                            from core.progresso import gerenciador_progresso
                            cena_para_flag = {
                                "ch1_2_meet_boris": ("boris_primeira_aparicao_mostrada", "boris"),
                                "ch1_7_pixel_intro": ("pixel_primeira_aparicao_mostrada", "pixel"),
                                "ch1_7_pixel_voice_intro": ("pixel_primeira_aparicao_mostrada", "pixel"),  # Cena real do Pixel
                                "ch1_1_crank_garage_intro": ("crank_tutorial_mostrado", "crank"),
                            }
                            scene_id = narrative_system.current_scene_id
                            if scene_id in cena_para_flag:
                                flag_name, _ = cena_para_flag[scene_id]
                                flag_value = getattr(gerenciador_progresso, flag_name, False)
                                if flag_value and scene.get("gameplayTrigger"):
                                    # Cena já vista e tem trigger, processar diretamente
                                    trigger = scene.get("gameplayTrigger")
                                    print(f"[EXECUTAR_NARRATIVA] Cena {scene_id} já vista, processando trigger diretamente: {trigger}")
                                    narrative_system.fechar()
                                    return {
                                        "trigger": trigger.get("trigger"),
                                        "params": trigger.get("params", {})
                                    }
                    
                    clock_narrativa = pygame.time.Clock()
                    while narrative_system.active:
                        dt = clock_narrativa.tick(FPS) / 1000.0
                        
                        # Desativar NPCs quando a narrativa está ativa para evitar sobreposição
                        from core.pixel import pixel
                        from core.crank import crank
                        from core.akira import akira
                        pixel.ativo = False
                        crank.ativo = False
                        # Não desativar Akira completamente pois ela pode ser usada na narrativa
                        # Mas garantir que não está desenhando seu próprio diálogo
                        if akira.ativo and akira.modo_dialogo not in ["pre_corrida", "fim_corrida"]:
                            akira.ativo = False
                        
                        # Atualizar tempo do jogo (1 minuto real = 1 hora do jogo)
                        # MAS pausar durante time-skip ou transição de cena (fade escuro) para não avançar o tempo durante transições
                        from core.tempo_jogo import gerenciador_tempo
                        if not narrative_system.time_skip_active and not narrative_system.scene_transition_active:
                            gerenciador_tempo.atualizar(dt)
                        
                        # Processar eventos
                        eventos = pygame.event.get()
                        for ev in eventos:
                            if ev.type == pygame.QUIT:
                                narrative_system.fechar()
                                return None
                        
                        # Processar eventos da narrativa
                        resultado = narrative_system.processar_eventos(eventos)
                        if resultado == "fechado":
                            narrative_system.fechar()
                            break
                        elif resultado and isinstance(resultado, dict):
                            # Se retornou um trigger (de uma escolha), retornar o dicionário para ser processado no loop principal
                            print(f"[EXECUTAR_NARRATIVA] Trigger de escolha detectado, retornando: {resultado}")
                            print(f"[EXECUTAR_NARRATIVA] Tipo do trigger: {resultado.get('trigger')}, params: {resultado.get('params')}")
                            # NÃO fechar a narrativa aqui - deixar o loop principal processar o trigger primeiro
                            # narrative_system.fechar()
                            return resultado
                        
                        # Verificar se há trigger na cena atual (quando o texto termina)
                        # Usar método público se existir, senão usar privado
                        try:
                            scene = narrative_system._obter_cena_atual()
                        except:
                            scene = None
                        if scene:
                            lines = scene.get("lines", [])
                            if not narrative_system.choices_visible:
                                scene_trigger = scene.get("gameplayTrigger")
                                print(f"[EXECUTAR_NARRATIVA] Verificando scene_trigger: scene_id={narrative_system.current_scene_id}, has_trigger={scene_trigger is not None}, line_index={narrative_system.current_line_index}, total_lines={len(lines)}, choices_visible={narrative_system.choices_visible}")
                                if scene_trigger and narrative_system.current_scene_id:
                                    if narrative_system.current_line_index >= len(lines):
                                        if narrative_system.current_scene_id == "ch1_3_boris_deal":
                                            print(f"[EXECUTAR_NARRATIVA] ✓ Cena ch1_3_boris_deal: Todas as {len(lines)} linhas foram exibidas antes de abrir a loja!")
                                            for i, line in enumerate(lines):
                                                print(f"  Linha {i}: {line.get('speaker', '')} - {line.get('text', '')[:60]}...")
                                        # Extrair o tipo do trigger e todos os outros campos como params
                                        trigger_type = scene_trigger.get("trigger")
                                        params = {k: v for k, v in scene_trigger.items() if k != "trigger"}
                                        trigger = {
                                            "trigger": trigger_type,
                                            "params": params
                                        }
                                        print(f"[EXECUTAR_NARRATIVA] Trigger detectado diretamente da cena {narrative_system.current_scene_id}: {trigger}")
                                        # Verificar se o trigger já foi processado (evitar loop infinito)
                                        # Usar um atributo da função para rastrear triggers processados
                                        if not hasattr(executar_narrativa, '_triggers_processados'):
                                            executar_narrativa._triggers_processados = set()
                                        
                                        trigger_key = f"{narrative_system.current_scene_id}_{trigger.get('trigger')}"
                                        if trigger_key in executar_narrativa._triggers_processados:
                                            print(f"[EXECUTAR_NARRATIVA] Trigger já processado, ignorando: {trigger_key}")
                                            # Marcar a cena como visitada e desativar narrativa para evitar loop
                                            if narrative_system.current_scene_id:
                                                narrative_system.scenes_visited.add(narrative_system.current_scene_id)
                                            narrative_system.active = False
                                            narrative_system.current_scene_id = None
                                            return None
                                        
                                        # Marcar trigger como processado
                                        executar_narrativa._triggers_processados.add(trigger_key)
                                        
                                        if trigger.get('trigger') in ['open_shop', 'openShop', 'open_shop_interface']:
                                            shop_id = trigger.get('params', {}).get('shopId', '')
                                            print(f"[EXECUTAR_NARRATIVA] Processando trigger open_shop: shop_id={shop_id}")
                                            # Limpar current_scene_id antes de retornar o trigger
                                            narrative_system.current_scene_id = None
                                            narrative_system.active = False
                                            return trigger
                                        else:
                                            print(f"[EXECUTAR_NARRATIVA] Processando trigger: {trigger.get('trigger')}")
                                            narrative_system.current_scene_id = None
                                            narrative_system.active = False
                                            return trigger
                            
                            # Se terminou todas as linhas e não há escolhas, verificar trigger (método antigo como fallback)
                            if (narrative_system.current_line_index >= len(lines) and 
                                not narrative_system.choices_visible):
                                print(f"[EXECUTAR_NARRATIVA] Verificando trigger: line_index={narrative_system.current_line_index}, total_lines={len(lines)}, choices_visible={narrative_system.choices_visible}, scene_id={narrative_system.current_scene_id}")
                                trigger = narrative_system.obter_trigger_atual()
                                print(f"[EXECUTAR_NARRATIVA] obter_trigger_atual retornou: {trigger}")
                                if trigger:
                                    print(f"[EXECUTAR_NARRATIVA] Trigger detectado na cena {narrative_system.current_scene_id}: {trigger}")
                                    print(f"[EXECUTAR_NARRATIVA] line_index={narrative_system.current_line_index}, total_lines={len(lines)}, choices_visible={narrative_system.choices_visible}")
                                    
                                    # Verificar se o trigger já foi processado (evitar loop infinito)
                                    if not hasattr(executar_narrativa, '_triggers_processados'):
                                        executar_narrativa._triggers_processados = set()
                                    
                                    trigger_key = f"{narrative_system.current_scene_id}_{trigger.get('trigger')}"
                                    if trigger_key in executar_narrativa._triggers_processados:
                                        print(f"[EXECUTAR_NARRATIVA] Trigger já processado, ignorando: {trigger_key}")
                                        # Marcar a cena como visitada e desativar narrativa para evitar loop
                                        if narrative_system.current_scene_id:
                                            narrative_system.scenes_visited.add(narrative_system.current_scene_id)
                                        narrative_system.active = False
                                        narrative_system.current_scene_id = None
                                        return None
                                    
                                    # Marcar trigger como processado
                                    executar_narrativa._triggers_processados.add(trigger_key)
                                    
                                    if trigger.get('trigger') in ['open_shop', 'openShop', 'open_shop_interface']:
                                        shop_id = trigger.get('params', {}).get('shopId', '')
                                        print(f"[EXECUTAR_NARRATIVA] Processando trigger open_shop: shop_id={shop_id}")
                                        narrative_system.fechar()
                                        return trigger
                                    else:
                                        print(f"[EXECUTAR_NARRATIVA] Processando trigger: {trigger.get('trigger')}")
                                        narrative_system.fechar()
                                        return trigger
                                else:
                                    # Debug: verificar por que não há trigger
                                    if narrative_system.current_scene_id == "ch2_8_boris_unlock_offer":
                                        print(f"[DEBUG] Cena ch2_8_boris_unlock_offer terminou mas não há trigger! Verificando cena...")
                                        scene_trigger = scene.get("gameplayTrigger")
                                        print(f"[DEBUG] gameplayTrigger na cena: {scene_trigger}")
                        
                        # Atualizar narrativa
                        narrative_system.atualizar(dt)
                        
                        # Verificar novamente se terminou todas as linhas após atualizar
                        # (pode ter avançado durante a atualização ou processamento de eventos)
                        scene = narrative_system._obter_cena_atual()
                        if scene:
                            lines = scene.get("lines", [])
                            if (narrative_system.current_line_index >= len(lines) and 
                                not narrative_system.choices_visible):
                                trigger = narrative_system.obter_trigger_atual()
                                if trigger:
                                    print(f"[EXECUTAR_NARRATIVA] Trigger detectado após atualizar (cena {narrative_system.current_scene_id}): {trigger}")
                                    if trigger.get('trigger') in ['open_shop', 'openShop', 'open_shop_interface']:
                                        shop_id = trigger.get('params', {}).get('shopId', '')
                                        on_close_scene_id = trigger.get('params', {}).get('onCloseSceneId', '')
                                        trigger_key = f"{shop_id}_{on_close_scene_id}"
                                        if hasattr(processar_trigger, '_loja_processada') and trigger_key in processar_trigger._loja_processada:
                                            print(f"[EXECUTAR_NARRATIVA] Trigger já processado, ignorando: {trigger_key}")
                                            pass
                                        else:
                                            print(f"[EXECUTAR_NARRATIVA] Processando trigger open_shop após atualizar: shop_id={shop_id}")
                                            narrative_system.fechar()
                                            return trigger
                                    else:
                                        print(f"[EXECUTAR_NARRATIVA] Processando trigger após atualizar: {trigger.get('trigger')}")
                                        narrative_system.fechar()
                                        return trigger
                        
                        # Verificar se a transição de cena acabou e há um trigger na nova cena
                        if not narrative_system.scene_transition_active and narrative_system.current_scene_id:
                            scene = narrative_system._obter_cena_atual()
                            if scene:
                                lines = scene.get("lines", [])
                                # Se terminou todas as linhas e não há escolhas, verificar trigger
                                if (narrative_system.current_line_index >= len(lines) and 
                                    not narrative_system.choices_visible):
                                    trigger = narrative_system.obter_trigger_atual()
                                    if trigger:
                                        print(f"[EXECUTAR_NARRATIVA] Trigger detectado após transição: {trigger}")
                                        # Verificar se o trigger já foi processado (evitar loop infinito)
                                        if trigger.get('trigger') in ['open_shop', 'openShop', 'open_shop_interface']:
                                            shop_id = trigger.get('params', {}).get('shopId', '')
                                            on_close_scene_id = trigger.get('params', {}).get('onCloseSceneId', '')
                                            trigger_key = f"{shop_id}_{on_close_scene_id}"
                                            if hasattr(processar_trigger, '_loja_processada') and trigger_key in processar_trigger._loja_processada:
                                                print(f"[EXECUTAR_NARRATIVA] Trigger já processado após transição, ignorando: {trigger_key}")
                                                pass
                                            else:
                                                narrative_system.fechar()
                                                return trigger
                                        else:
                                            narrative_system.fechar()
                                            return trigger
                        
                        # Desenhar
                        screen.fill((0, 0, 0))
                        narrative_system.desenhar(screen)
                        pygame.display.flip()
                    
                    # Verificar se o jogo terminou (após créditos)
                    if narrative_system.game_ended:
                        print(f"[EXECUTAR_NARRATIVA] Jogo terminou (game_ended=True), retornando None para voltar ao menu")
                        return None
                    
                    # Se saiu do loop sem trigger, verificar se há trigger na última cena
                    trigger = narrative_system.obter_trigger_atual()
                    print(f"[EXECUTAR_NARRATIVA] Verificando trigger ao sair do loop: {trigger}")
                    # Verificar se o trigger já foi processado (evitar loop infinito)
                    if trigger and trigger.get('trigger') in ['open_shop', 'openShop', 'open_shop_interface']:
                        shop_id = trigger.get('params', {}).get('shopId', '')
                        on_close_scene_id = trigger.get('params', {}).get('onCloseSceneId', '')
                        trigger_key = f"{shop_id}_{on_close_scene_id}"
                        if hasattr(processar_trigger, '_loja_processada') and trigger_key in processar_trigger._loja_processada:
                            print(f"[EXECUTAR_NARRATIVA] Trigger já processado, ignorando: {trigger_key}")
                            return None  # Não retornar trigger já processado
                    return trigger
                
                # Função para processar triggers
                def processar_trigger(trigger_info):
                    """Processa um trigger e retorna o próximo estado"""
                    # Importar narrative_system no início para estar disponível em todo o escopo
                    from core.narrative_system import narrative_system
                    
                    if not trigger_info:
                        print(f"[PROCESSAR_TRIGGER] trigger_info é None ou vazio")
                        return None
                    
                    # Verificar se trigger_info é uma string (erro) ou dicionário
                    if isinstance(trigger_info, str):
                        print(f"[PROCESSAR_TRIGGER] ERRO: trigger_info é uma string: {trigger_info}")
                        return None
                    
                    if not isinstance(trigger_info, dict):
                        print(f"[PROCESSAR_TRIGGER] ERRO: trigger_info não é um dicionário: {type(trigger_info)}")
                        return None
                    
                    trigger_type = trigger_info.get("trigger")
                    params = trigger_info.get("params", {})
                    print(f"[PROCESSAR_TRIGGER] Processando trigger: type={trigger_type}, params={params}")
                    
                    if trigger_type == "goto_map":
                        # Verificar se há focusRace (pista de treino)
                        focus_race = params.get("focusRace")
                        objective_text = params.get("objectiveText", "")
                        skip_menu = params.get("skipMenu", False)
                        # Garantir que skip_menu é um booleano (pode vir como string do JSON)
                        if isinstance(skip_menu, str):
                            skip_menu = skip_menu.lower() in ("true", "1", "yes")
                        print(f"[PROCESSAR_TRIGGER] goto_map: focus_race={focus_race}, skip_menu={skip_menu}, type(skip_menu)={type(skip_menu)}")
                        
                        # Verificar condições
                        print(f"[PROCESSAR_TRIGGER] Verificando condições: focus_race == 'training_01' = {focus_race == 'training_01'}, not skip_menu = {not skip_menu}, skip_menu = {skip_menu}")
                        
                        if focus_race == "training_01" and not skip_menu:
                            # Mostrar menu "Ir para a pista de treino" ou "Sair"
                            
                            # Importar dependências necessárias
                            from config import LARGURA, ALTURA, FPS, DIR_PROJETO
                            import sys
                            import os
                            from core.popup_musica import popup_musica
                            
                            # Obter render_text
                            render_text_func = getattr(sys.modules[__name__], 'render_text')
                            
                            # Carregar fundo da garagem
                            fundo_garagem_path = os.path.join(DIR_PROJETO, "assets", "images", "ui", "garage_bg.png")
                            if os.path.exists(fundo_garagem_path):
                                fundo_garagem = pygame.image.load(fundo_garagem_path).convert()
                                fundo_garagem = pygame.transform.scale(fundo_garagem, (LARGURA, ALTURA))
                            else:
                                fundo_garagem = pygame.Surface((LARGURA, ALTURA))
                                fundo_garagem.fill((20, 20, 20))
                            
                            # Menu simples
                            clock_menu = pygame.time.Clock()
                            opcao_selecionada = 0  # 0 = Ir para pista, 1 = Sair
                            rodando_menu = True
                            
                            while rodando_menu:
                                dt = clock_menu.tick(FPS) / 1000.0
                                
                                # Atualizar tempo do jogo
                                from core.tempo_jogo import gerenciador_tempo
                                gerenciador_tempo.atualizar(dt)
                                
                                # Verificar se deve sair do loop antes de processar eventos
                                if not rodando_menu:
                                    break
                                
                                eventos = pygame.event.get()
                                for ev in eventos:
                                    if ev.type == pygame.QUIT:
                                        import sys
                                        pygame.quit()
                                        sys.exit()
                                    
                                    if ev.type == pygame.KEYDOWN:
                                        if ev.key in (pygame.K_UP, pygame.K_w):
                                            opcao_selecionada = (opcao_selecionada - 1) % 2
                                        elif ev.key in (pygame.K_DOWN, pygame.K_s):
                                            opcao_selecionada = (opcao_selecionada + 1) % 2
                                        elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                                            if opcao_selecionada == 0:
                                                # Ir para a pista de treino - iniciar corrida diretamente
                                                rodando_menu = False
                                                
                                                # Iniciar corrida training_01 diretamente
                                                import json
                                                import os
                                                from config import DIR_PROJETO
                                                
                                                caminho_races = os.path.join(DIR_PROJETO, "data", "races.json")
                                                race_config = None
                                                
                                                if os.path.exists(caminho_races):
                                                    try:
                                                        with open(caminho_races, 'r', encoding='utf-8') as f:
                                                            races_data = json.load(f)
                                                            for race in races_data.get("races", []):
                                                                if race.get("id") == "training_01":
                                                                    race_config = race
                                                                    break
                                                    except Exception as e:
                                                        print(f"Erro ao carregar corrida training_01: {e}")
                                                
                                                if race_config:
                                                    # Verificar tédio antes de iniciar corrida
                                                    try:
                                                        from core.status_jogador import status_jogador
                                                        pode_correr, mensagem = status_jogador.pode_correr()
                                                        if not pode_correr:
                                                            from core.popup_musica import popup_musica
                                                            popup_musica.mostrar(mensagem, tipo="outra")
                                                            return "mapa"
                                                    except Exception as e:
                                                        print(f"Erro ao verificar status do jogador: {e}")
                                                    
                                                    # Obter parâmetros da corrida
                                                    track = race_config.get("track", 1)
                                                    # Garantir que training_01 sempre usa a pista 1 (fase 1 do arcade)
                                                    if focus_race == "training_01":
                                                        track = 1
                                                        print(f"[PISTA TREINO] Forçando pista 1 para training_01 (fase 1 do arcade)")
                                                    laps = race_config.get("laps", 1)
                                                    difficulty = race_config.get("difficulty", "facil")
                                                    tipo = race_config.get("tipo", "corrida")
                                                    sem_bots = race_config.get("sem_bots", False)
                                                    
                                                    # Obter carro atual do jogador
                                                    from core.progresso import gerenciador_progresso
                                                    carro_p1_idx = 0
                                                    if gerenciador_progresso.carro_p1_atual:
                                                        from config import CARROS_DISPONIVEIS
                                                        for i, carro in enumerate(CARROS_DISPONIVEIS):
                                                            if carro.get("prefixo_cor") == gerenciador_progresso.carro_p1_atual:
                                                                carro_p1_idx = i
                                                                break
                                                    
                                                    # Converter tipo para enum
                                                    from main import TipoJogo, ModoJogo
                                                    tipo_jogo = TipoJogo.CORRIDA if tipo == "corrida" else TipoJogo.DRIFT
                                                    
                                                    # Armazenar race_id para verificar após a corrida
                                                    gerenciador_progresso.ultima_corrida_campanha = "training_01"
                                                    gerenciador_progresso.salvar()
                                                    
                                                    # Modo de teste: marcar corrida como concluída automaticamente
                                                    from config import MODO_TESTE_CORRIDAS
                                                    if MODO_TESTE_CORRIDAS:
                                                        print(f"[MODO TESTE] Corrida training_01 marcada como concluída automaticamente")
                                                        from core.estatisticas import gerenciador_estatisticas
                                                        gerenciador_estatisticas.carregar()
                                                        # Registrar corrida como concluída (posição 1, tempo fictício)
                                                        gerenciador_estatisticas.registrar_corrida_completa(
                                                            numero_pista=track,
                                                            posicao_final=1,
                                                            tempo_final=60.0  # Tempo fictício
                                                        )
                                                        gerenciador_estatisticas.salvar()
                                                        
                                                        # Limpar flag e salvar
                                                        gerenciador_progresso.ultima_corrida_campanha = None
                                                        gerenciador_progresso.salvar()
                                                        
                                                        # Iniciar narrativa pós-corrida
                                                        _iniciar_narrativa_pos_training_01(narrative_system, gerenciador_progresso)
                                                        return "narrativa"
                                                    else:
                                                        # Iniciar corrida normalmente
                                                        import main
                                                        print(f"[PISTA TREINO] Chamando main.principal com mapa_selecionado={track}, race_id=training_01")
                                                        main.principal(
                                                            carro_selecionado_p1=carro_p1_idx,
                                                            carro_selecionado_p2=0,
                                                            mapa_selecionado=track,
                                                            modo_jogo=ModoJogo.UM_JOGADOR,
                                                            tipo_jogo=tipo_jogo,
                                                            voltas=laps,
                                                            dificuldade_ia=difficulty,
                                                            modo_arcade=False,
                                                            sem_bots=sem_bots,
                                                            race_id="training_01"
                                                        )
                                                    
                                                    # Verificar se training_01 foi completada
                                                    foi_training_01 = (hasattr(gerenciador_progresso, 'ultima_corrida_campanha') and 
                                                                      gerenciador_progresso.ultima_corrida_campanha == "training_01")
                                                    
                                                    # Verificar se as cenas pós-corrida já foram visitadas antes de verificar a corrida
                                                    if "ch1_6_post_race" in narrative_system.scenes_visited or "ch1_7_pixel_voice_intro" in narrative_system.scenes_visited:
                                                        # Se já foram visitadas, limpar a flag para evitar verificações futuras
                                                        if foi_training_01:
                                                            gerenciador_progresso.ultima_corrida_campanha = None
                                                            gerenciador_progresso.salvar()
                                                    elif foi_training_01 and _verificar_corrida_completa(1):
                                                        _iniciar_narrativa_pos_training_01(narrative_system, gerenciador_progresso)
                                                        return "narrativa"
                                                    
                                                    return "mapa"
                                                else:
                                                    return "mapa"
                                            else:
                                                # Sair sem ir para a pista
                                                rodando_menu = False
                                                return "mapa"
                                        elif ev.key == pygame.K_ESCAPE:
                                            rodando_menu = False
                                            return "mapa"
                                    
                                    elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                                        mouse_x, mouse_y = pygame.mouse.get_pos()
                                        
                                        # Verificar clique nos botões
                                        caixa_largura = 500
                                        caixa_altura = 180
                                        caixa_x = (LARGURA - caixa_largura) // 2
                                        caixa_y = ALTURA - caixa_altura - 260
                                        botao_y_base = caixa_y + 105
                                        botao_altura = 30
                                        
                                        rect_ir_pista = pygame.Rect(caixa_x + 40, botao_y_base, caixa_largura - 80, botao_altura)
                                        rect_sair = pygame.Rect(caixa_x + 40, botao_y_base + 30, caixa_largura - 80, botao_altura)
                                        
                                        if rect_ir_pista.collidepoint(mouse_x, mouse_y):
                                            # Ir para a pista de treino - iniciar corrida diretamente
                                            rodando_menu = False
                                            
                                            # Iniciar corrida training_01 diretamente
                                            import json
                                            import os
                                            from config import DIR_PROJETO
                                            
                                            caminho_races = os.path.join(DIR_PROJETO, "data", "races.json")
                                            race_config = None
                                            
                                            if os.path.exists(caminho_races):
                                                try:
                                                    with open(caminho_races, 'r', encoding='utf-8') as f:
                                                        races_data = json.load(f)
                                                        for race in races_data.get("races", []):
                                                            if race.get("id") == "training_01":
                                                                race_config = race
                                                                break
                                                except Exception as e:
                                                    print(f"Erro ao carregar corrida training_01: {e}")
                                            
                                            if race_config:
                                                # Verificar tédio antes de iniciar corrida
                                                try:
                                                    from core.status_jogador import status_jogador
                                                    pode_correr, mensagem = status_jogador.pode_correr()
                                                    if not pode_correr:
                                                        from core.popup_musica import popup_musica
                                                        popup_musica.mostrar(mensagem, tipo="outra")
                                                        return "mapa"
                                                except Exception as e:
                                                    print(f"Erro ao verificar status do jogador: {e}")
                                                
                                                # Obter parâmetros da corrida
                                                track = race_config.get("track", 1)
                                                # Garantir que training_01 sempre usa a pista 1 (fase 1 do arcade)
                                                if race_id == "training_01":
                                                    track = 1
                                                    print(f"[PISTA TREINO] Forçando pista 1 para training_01 (fase 1 do arcade)")
                                                laps = race_config.get("laps", 1)
                                                difficulty = race_config.get("difficulty", "facil")
                                                tipo = race_config.get("tipo", "corrida")
                                                sem_bots = race_config.get("sem_bots", False)
                                                
                                                # Obter carro atual do jogador
                                                from core.progresso import gerenciador_progresso
                                                carro_p1_idx = 0
                                                if gerenciador_progresso.carro_p1_atual:
                                                    from config import CARROS_DISPONIVEIS
                                                    for i, carro in enumerate(CARROS_DISPONIVEIS):
                                                        if carro.get("prefixo_cor") == gerenciador_progresso.carro_p1_atual:
                                                            carro_p1_idx = i
                                                            break
                                                
                                                # Converter tipo para enum
                                                from main import TipoJogo, ModoJogo
                                                tipo_jogo = TipoJogo.CORRIDA if tipo == "corrida" else TipoJogo.DRIFT
                                                
                                                # Armazenar race_id para verificar após a corrida
                                                gerenciador_progresso.ultima_corrida_campanha = "training_01"
                                                gerenciador_progresso.salvar()
                                                
                                                # Log final antes de iniciar corrida
                                                print(f"[PISTA TREINO] Iniciando corrida training_01 (menu): track={track}, laps={laps}, difficulty={difficulty}, sem_bots={sem_bots}")
                                                
                                                # Iniciar corrida
                                                import main
                                                print(f"[PISTA TREINO] Chamando main.principal com mapa_selecionado={track}, race_id=training_01")
                                                main.principal(
                                                    carro_selecionado_p1=carro_p1_idx,
                                                    carro_selecionado_p2=0,
                                                    mapa_selecionado=track,
                                                    modo_jogo=ModoJogo.UM_JOGADOR,
                                                    tipo_jogo=tipo_jogo,
                                                    voltas=laps,
                                                    dificuldade_ia=difficulty,
                                                    modo_arcade=False,
                                                    sem_bots=sem_bots,
                                                    race_id="training_01"
                                                )
                                                
                                                # Verificar se training_01 foi completada
                                                foi_training_01 = (hasattr(gerenciador_progresso, 'ultima_corrida_campanha') and 
                                                                  gerenciador_progresso.ultima_corrida_campanha == "training_01")
                                                
                                                # Verificar se as cenas pós-corrida já foram visitadas antes de verificar a corrida
                                                if "ch1_6_post_race" in narrative_system.scenes_visited or "ch1_7_pixel_voice_intro" in narrative_system.scenes_visited:
                                                    # Se já foram visitadas, limpar a flag para evitar verificações futuras
                                                    if foi_training_01:
                                                        gerenciador_progresso.ultima_corrida_campanha = None
                                                        gerenciador_progresso.salvar()
                                                elif foi_training_01 and _verificar_corrida_completa(1):
                                                    _iniciar_narrativa_pos_training_01(narrative_system, gerenciador_progresso)
                                                    return "narrativa"
                                                
                                                return "mapa"
                                            else:
                                                return "mapa"
                                        elif rect_sair.collidepoint(mouse_x, mouse_y):
                                            rodando_menu = False
                                            return "mapa"
                                
                                # Verificar se deve sair antes de desenhar
                                if not rodando_menu:
                                    break
                                
                                # Desenhar fundo
                                screen.blit(fundo_garagem, (0, 0))
                                
                                # Overlay escuro
                                overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                                overlay.fill((0, 0, 0, 200))
                                screen.blit(overlay, (0, 0))
                                
                                # Caixa de menu (similar ao Boris)
                                caixa_largura = 500
                                caixa_altura = 180
                                caixa_x = (LARGURA - caixa_largura) // 2
                                caixa_y = ALTURA - caixa_altura - 260
                                
                                overlay_caixa = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
                                overlay_caixa.fill((0, 0, 0, 220))
                                screen.blit(overlay_caixa, (caixa_x, caixa_y))
                                pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 2)
                                
                                # Título
                                titulo = render_text_func("PISTA DE TREINO", 22, (255, 255, 0), bold=True, pixel_style=True)
                                screen.blit(titulo, (caixa_x + (caixa_largura - titulo.get_width()) // 2, caixa_y + 10))
                                
                                # Descrição
                                desc = render_text_func(objective_text if objective_text else "Circuito de Treino disponível", 18, (220, 220, 220), bold=False, pixel_style=True)
                                screen.blit(desc, (caixa_x + 20, caixa_y + 45))
                                
                                # Opções
                                opcoes = ["IR PARA A PISTA", "SAIR"]
                                for i, texto_opcao in enumerate(opcoes):
                                    cor = (0, 200, 255) if i == opcao_selecionada else (200, 200, 200)
                                    txt = render_text_func(texto_opcao, 20, cor, bold=True, pixel_style=True)
                                    y = caixa_y + 105 + i * 30
                                    screen.blit(txt, (caixa_x + 40, y))
                                
                                pygame.display.flip()
                            
                            # Após sair do loop, se escolheu ir para a pista, continuar para o mapa
                            # Armazenar focusRace para o mapa processar depois
                            if focus_race:
                                try:
                                    from core.progresso import gerenciador_progresso
                                    if not hasattr(gerenciador_progresso, 'focus_race_temp'):
                                        gerenciador_progresso.focus_race_temp = None
                                    gerenciador_progresso.focus_race_temp = focus_race
                                    print(f"[PISTA TREINO] Menu terminou, indo para o mapa com foco na pista: {focus_race}")
                                except Exception as e:
                                    print(f"[PISTA TREINO] Erro ao armazenar focus_race: {e}")
                            
                            return "mapa"
                        elif focus_race == "training_01" and skip_menu:
                            # Se skipMenu é True, iniciar corrida diretamente sem mostrar menu
                            print(f"[PROCESSAR_TRIGGER] Verificando elif: focus_race == 'training_01' = {focus_race == 'training_01'}, skip_menu = {skip_menu}, type(skip_menu)={type(skip_menu)}")
                            print(f"[PROCESSAR_TRIGGER] Entrando no bloco skipMenu=True para training_01")
                            print(f"[PISTA TREINO] skipMenu=True, iniciando corrida training_01 diretamente...")
                            
                            # Marcar a cena atual como visitada ANTES de fechar a narrativa
                            cena_atual = narrative_system.current_scene_id
                            if cena_atual == "ch1_1b_crank_test_briefing":
                                if "ch1_1b_crank_test_briefing" not in narrative_system.scenes_visited:
                                    narrative_system.scenes_visited.add("ch1_1b_crank_test_briefing")
                                    print(f"[PISTA TREINO] Cena ch1_1b_crank_test_briefing marcada como visitada")
                            
                            # Fechar narrativa antes de iniciar a corrida para evitar reiniciar
                            if narrative_system.active:
                                print(f"[PISTA TREINO] Fechando narrativa antes de iniciar corrida (cena atual: {cena_atual})")
                                narrative_system.fechar()
                                # Garantir que a narrativa está realmente fechada e limpar current_scene_id
                                narrative_system.active = False
                                # Limpar current_scene_id para evitar reiniciar a cena
                                narrative_system.current_scene_id = None
                                narrative_system.current_line_index = 0
                                print(f"[PISTA TREINO] Narrativa fechada e current_scene_id limpo")
                            
                            # Carregar configuração da corrida
                            import json
                            import os
                            from config import DIR_PROJETO
                            
                            caminho_races = os.path.join(DIR_PROJETO, "data", "races.json")
                            race_config = None
                            
                            if os.path.exists(caminho_races):
                                try:
                                    with open(caminho_races, 'r', encoding='utf-8') as f:
                                        races_data = json.load(f)
                                        for race in races_data.get("races", []):
                                            if race.get("id") == "training_01":
                                                race_config = race
                                                break
                                except Exception as e:
                                    print(f"Erro ao carregar corrida training_01: {e}")
                            
                            if race_config:
                                # Verificar tédio antes de iniciar corrida
                                try:
                                    from core.status_jogador import status_jogador
                                    pode_correr, mensagem = status_jogador.pode_correr()
                                    if not pode_correr:
                                        from core.popup_musica import popup_musica
                                        popup_musica.mostrar(mensagem, tipo="outra")
                                        return "mapa"
                                except Exception as e:
                                    print(f"Erro ao verificar status do jogador: {e}")
                                
                                # Obter parâmetros da corrida
                                track = race_config.get("track", 1)
                                # Garantir que training_01 sempre usa a pista 1 (fase 1 do arcade)
                                if focus_race == "training_01":
                                    track = 1
                                    print(f"[PISTA TREINO] Forçando pista 1 para training_01 (fase 1 do arcade)")
                                laps = race_config.get("laps", 1)
                                difficulty = race_config.get("difficulty", "facil")
                                tipo = race_config.get("tipo", "corrida")
                                sem_bots = race_config.get("sem_bots", False)
                                
                                # Obter carro atual do jogador
                                from core.progresso import gerenciador_progresso
                                carro_p1_idx = 0
                                if gerenciador_progresso.carro_p1_atual:
                                    from config import CARROS_DISPONIVEIS
                                    for i, carro in enumerate(CARROS_DISPONIVEIS):
                                        if carro.get("prefixo_cor") == gerenciador_progresso.carro_p1_atual:
                                            carro_p1_idx = i
                                            break
                                
                                # Converter tipo para enum
                                from main import TipoJogo, ModoJogo
                                tipo_jogo = TipoJogo.CORRIDA if tipo == "corrida" else TipoJogo.DRIFT
                                
                                # Armazenar race_id para verificar após a corrida
                                gerenciador_progresso.ultima_corrida_campanha = "training_01"
                                gerenciador_progresso.salvar()
                                
                                # Log final antes de iniciar corrida
                                print(f"[PISTA TREINO] Iniciando corrida training_01: track={track}, laps={laps}, difficulty={difficulty}, sem_bots={sem_bots}")
                                
                                # Modo de teste: marcar corrida como concluída automaticamente
                                from config import MODO_TESTE_CORRIDAS
                                if MODO_TESTE_CORRIDAS:
                                    print(f"[MODO TESTE] Corrida training_01 marcada como concluída automaticamente")
                                    from core.estatisticas import gerenciador_estatisticas
                                    gerenciador_estatisticas.carregar()
                                    # Registrar corrida como concluída (posição 1, tempo fictício)
                                    gerenciador_estatisticas.registrar_corrida_completa(
                                        numero_pista=track,
                                        posicao_final=1,
                                        tempo_final=60.0  # Tempo fictício
                                    )
                                    gerenciador_estatisticas.salvar()
                                    
                                    # Limpar flag e salvar
                                    gerenciador_progresso.ultima_corrida_campanha = None
                                    gerenciador_progresso.salvar()
                                    
                                    # Iniciar narrativa pós-corrida
                                    _iniciar_narrativa_pos_training_01(narrative_system, gerenciador_progresso)
                                    return "narrativa"
                                else:
                                    # Iniciar corrida normalmente
                                    import main
                                    print(f"[PISTA TREINO] Chamando main.principal com mapa_selecionado={track}, race_id=training_01")
                                    main.principal(
                                        carro_selecionado_p1=carro_p1_idx,
                                        carro_selecionado_p2=0,
                                        mapa_selecionado=track,
                                        modo_jogo=ModoJogo.UM_JOGADOR,
                                        tipo_jogo=tipo_jogo,
                                        voltas=laps,
                                        dificuldade_ia=difficulty,
                                        modo_arcade=False,
                                        sem_bots=sem_bots,
                                        race_id="training_01"
                                    )
                                    
                                    # Verificar se training_01 foi completada
                                    foi_training_01 = (hasattr(gerenciador_progresso, 'ultima_corrida_campanha') and 
                                                      gerenciador_progresso.ultima_corrida_campanha == "training_01")
                                    
                                    # Verificar se as cenas pós-corrida já foram visitadas antes de verificar a corrida
                                    if "ch1_6_post_race" in narrative_system.scenes_visited or "ch1_7_pixel_voice_intro" in narrative_system.scenes_visited:
                                        # Se já foram visitadas, limpar a flag para evitar verificações futuras
                                        if foi_training_01:
                                            gerenciador_progresso.ultima_corrida_campanha = None
                                            gerenciador_progresso.salvar()
                                    elif foi_training_01 and _verificar_corrida_completa(1):
                                        _iniciar_narrativa_pos_training_01(narrative_system, gerenciador_progresso)
                                        return "narrativa"
                                    
                                    return "mapa"
                            else:
                                print(f"[PISTA TREINO] Erro: configuração da corrida training_01 não encontrada")
                                return "mapa"
                        
                        # Verificar se acabamos de completar a cena de introdução do Pixel
                        if narrative_system.current_scene_id == "ch1_7_pixel_voice_intro" or narrative_system.current_scene_id == "ch1_7_pixel_intro":
                            print(f"[PIXEL INTRO] Cena de introdução do Pixel completada ({narrative_system.current_scene_id}), marcando primeira aparição")
                            from core.pixel import pixel
                            from core.progresso import gerenciador_progresso
                            # Marcar que o Pixel foi apresentado
                            pixel.primeira_aparicao_mostrada = True
                            pixel.nome_revelado = True
                            pixel.salvar_estado()
                            print(f"[PIXEL INTRO] Pixel marcado como apresentado: primeira_aparicao={pixel.primeira_aparicao_mostrada}, nome_revelado={pixel.nome_revelado}")
                            
                            # Completar missão m7_olhos_no_painel
                            from core.missoes import gerenciador_missoes
                            if "m7_olhos_no_painel" not in gerenciador_missoes.missoes_completas:
                                gerenciador_missoes.completar_por_cena(narrative_system.current_scene_id)
                                gerenciador_missoes.salvar()
                                print(f"[PIXEL INTRO] Missão m7_olhos_no_painel completada pela cena {narrative_system.current_scene_id}")
                            else:
                                print(f"[PIXEL INTRO] Missão m7_olhos_no_painel já estava completa")
                            
                            # Marcar capítulo 1 como completo e iniciar capítulo 2
                            if not gerenciador_progresso.capitulo_foi_completo("ch1"):
                                print(f"[CAPÍTULO 1] Marcando capítulo 1 como completo")
                                gerenciador_progresso.marcar_capitulo_completo("ch1")
                                gerenciador_progresso.definir_capitulo_atual("ch2")
                                gerenciador_progresso.salvar()
                                
                                # Iniciar capítulo 2
                                print(f"[CAPÍTULO 2] Iniciando capítulo 2")
                                if narrative_system.iniciar_capitulo("ch2"):
                                    narrative_system.active = True
                                    narrative_system.current_line_index = 0
                                    # Retornar "narrativa" para que o loop principal continue processando a narrativa
                                    return "narrativa"
                        
                        # Voltar para o mapa normalmente (sem menu especial ou se não é training_01)
                        print(f"[PROCESSAR_TRIGGER] goto_map: Nenhuma condição especial atendida, retornando 'mapa'. focus_race={focus_race}, skip_menu={skip_menu}")
                        return "mapa"
                    
                    elif trigger_type in ["check_tire_and_offer_race", "start_race_setup"]:
                        print(f"[PROCESSAR_TRIGGER] Trigger {trigger_type} detectado! Verificando pneu nível 1...")
                        # Verificar pneu nível 1 antes de oferecer corrida
                        race_id = params.get("raceId")
                        on_result_scene_id = params.get("onResultSceneId")
                        print(f"[PROCESSAR_TRIGGER] race_id={race_id}, on_result_scene_id={on_result_scene_id}")
                        
                        from core.progresso import gerenciador_progresso
                        # Obter carro atual
                        carro_atual = gerenciador_progresso.obter_carro_atual(1)
                        if not carro_atual:
                            carro_atual = "Car1"
                        print(f"[PROCESSAR_TRIGGER] carro_atual inicial: {carro_atual}, tipo: {type(carro_atual)}")
                        
                        # Garantir que carro_atual é string (prefixo_cor)
                        if isinstance(carro_atual, int):
                            from config import CARROS_DISPONIVEIS
                            if 0 <= carro_atual < len(CARROS_DISPONIVEIS):
                                carro_atual = CARROS_DISPONIVEIS[carro_atual].get("prefixo_cor", "Car1")
                            else:
                                carro_atual = "Car1"
                            print(f"[PROCESSAR_TRIGGER] carro_atual convertido: {carro_atual}")
                        
                        nivel_pneu = gerenciador_progresso.obter_upgrade(carro_atual, "rodas")
                        print(f"[PROCESSAR_TRIGGER] Nível de pneu verificado: {nivel_pneu} (carro: {carro_atual})")
                        
                        # Se não tem pneus nível 1, redirecionar para o mapa
                        if nivel_pneu < 1:
                            print(f"[PROCESSAR_TRIGGER] Jogador não tem pneu nível 1 (nível atual: {nivel_pneu}), redirecionando para o mapa")
                            from core.popup_musica import popup_musica
                            popup_musica.mostrar("Você precisa de pneus nível 1 para correr na montanha. Compre com Boris ou Crank.", tipo="outra")
                            # Fechar narrativa e voltar para o mapa
                            narrative_system.fechar()
                            narrative_system.active = False
                            narrative_system.current_scene_id = None
                            print(f"[PROCESSAR_TRIGGER] Narrativa fechada, retornando 'mapa'")
                            return "mapa"
                        
                        # Se tem pneus nível 1, fechar narrativa e voltar para o território
                        # O sistema antigo da Akira vai oferecer a corrida automaticamente
                        print(f"[PROCESSAR_TRIGGER] Jogador tem pneu nível 1 (nível: {nivel_pneu}), fechando narrativa e voltando para o território")
                        # Fechar narrativa
                        narrative_system.fechar()
                        narrative_system.active = False
                        narrative_system.current_scene_id = None
                        
                        # Garantir que a primeira aparição da Akira foi marcada como mostrada
                        from core.akira import akira
                        from core.progresso import gerenciador_progresso
                        akira.primeira_aparicao_mostrada = True
                        akira.nome_revelado = True
                        gerenciador_progresso.akira_primeira_aparicao_mostrada = True
                        gerenciador_progresso.akira_nome_revelado = True
                        gerenciador_progresso.salvar()
                        
                        # Voltar para o mapa - o jogador pode voltar ao território da Akira para aceitar a corrida
                        print(f"[PROCESSAR_TRIGGER] Voltando para o mapa - jogador pode voltar ao território da Akira")
                        return "mapa"
                    
                    elif trigger_type == "start_race":
                        # Iniciar uma corrida específica
                        race_id = params.get("raceId")
                        on_result_scene_id = params.get("onResultSceneId")
                        
                        if race_id:
                            # Carregar definição da corrida
                            import json
                            import os
                            from config import DIR_PROJETO
                            
                            caminho_races = os.path.join(DIR_PROJETO, "data", "races.json")
                            race_config = None
                            
                            if os.path.exists(caminho_races):
                                try:
                                    with open(caminho_races, 'r', encoding='utf-8') as f:
                                        races_data = json.load(f)
                                        for race in races_data.get("races", []):
                                            if race.get("id") == race_id:
                                                race_config = race
                                                break
                                except Exception as e:
                                    print(f"Erro ao carregar corrida {race_id}: {e}")
                            
                            if race_config:
                                # Verificar tédio antes de iniciar corrida
                                try:
                                    from core.status_jogador import status_jogador
                                    pode_correr, mensagem = status_jogador.pode_correr()
                                    if not pode_correr:
                                        from core.popup_musica import popup_musica
                                        popup_musica.mostrar(mensagem, tipo="outra")
                                        # Não iniciar corrida, voltar para o mapa
                                        return "mapa"
                                except Exception as e:
                                    print(f"Erro ao verificar status do jogador: {e}")
                                
                                # Verificar se é a corrida da montanha e se o jogador tem pneu nível 1
                                if race_id == "mountain_test_run":
                                    from core.progresso import gerenciador_progresso
                                    # Obter carro atual
                                    carro_atual = gerenciador_progresso.obter_carro_atual(1)
                                    if not carro_atual:
                                        carro_atual = "Car1"
                                    
                                    # Garantir que carro_atual é string (prefixo_cor)
                                    if isinstance(carro_atual, int):
                                        from config import CARROS_DISPONIVEIS
                                        if 0 <= carro_atual < len(CARROS_DISPONIVEIS):
                                            carro_atual = CARROS_DISPONIVEIS[carro_atual].get("prefixo_cor", "Car1")
                                        else:
                                            carro_atual = "Car1"
                                    
                                    nivel_pneu = gerenciador_progresso.obter_upgrade(carro_atual, "rodas")
                                    
                                    # Se não tem pneus nível 1, redirecionar para o mapa
                                    if nivel_pneu < 1:
                                        print(f"[PROCESSAR_TRIGGER] Jogador não tem pneu nível 1 (nível atual: {nivel_pneu}), redirecionando para o mapa")
                                        from core.popup_musica import popup_musica
                                        popup_musica.mostrar("Você precisa de pneus nível 1 para correr na montanha. Compre com Boris ou Crank.", tipo="outra")
                                        # Fechar narrativa e voltar para o mapa
                                        narrative_system.fechar()
                                        narrative_system.active = False
                                        narrative_system.current_scene_id = None
                                        return "mapa"
                                
                                # Obter parâmetros da corrida
                                track = race_config.get("track", 1)
                                # Garantir que training_01 sempre usa a pista 1 (fase 1 do arcade)
                                if race_id == "training_01":
                                    track = 1
                                    print(f"[PISTA TREINO] Forçando pista 1 para training_01 (fase 1 do arcade)")
                                laps = race_config.get("laps", 1)
                                difficulty = race_config.get("difficulty", "medio")
                                tipo = race_config.get("tipo", "corrida")
                                sem_bots = race_config.get("sem_bots", False)  # Verificar se a corrida não deve ter bots
                                
                                # Obter carro atual do jogador
                                from core.progresso import gerenciador_progresso
                                carro_p1_idx = 0  # Padrão
                                if gerenciador_progresso.carro_p1_atual:
                                    # Tentar encontrar índice do carro atual
                                    from config import CARROS_DISPONIVEIS
                                    for i, carro in enumerate(CARROS_DISPONIVEIS):
                                        if carro.get("prefixo_cor") == gerenciador_progresso.carro_p1_atual:
                                            carro_p1_idx = i
                                            break
                                
                                # Converter tipo para enum
                                from main import TipoJogo, ModoJogo
                                tipo_jogo = TipoJogo.CORRIDA if tipo == "corrida" else TipoJogo.DRIFT
                                
                                # Definir flag de corrida da campanha ANTES de iniciar a corrida
                                # Isso permite que o jogo saiba qual cena narrativa iniciar após a corrida
                                if race_id:
                                    gerenciador_progresso.ultima_corrida_campanha = race_id
                                    gerenciador_progresso.salvar()
                                    print(f"[PROCESSAR_TRIGGER] Flag ultima_corrida_campanha definida como '{race_id}' antes de iniciar corrida")
                                
                                # Marcar a cena atual como visitada antes de iniciar a corrida
                                # Isso evita que a cena seja reiniciada após a corrida
                                if narrative_system.current_scene_id:
                                    narrative_system.scenes_visited.add(narrative_system.current_scene_id)
                                    print(f"[PROCESSAR_TRIGGER] Cena {narrative_system.current_scene_id} marcada como visitada antes de iniciar corrida")
                                    # Salvar flags da cena atual
                                    narrative_system._salvar_flags_cena_atual()
                                
                                # Fechar narrativa antes de iniciar corrida
                                narrative_system.fechar()
                                
                                # Iniciar corrida
                                import main
                                # Passar flag para indicar que não deve ter bots (será processado no main.py)
                                modo_arcade = False  # Sempre modo campanha para corridas da narrativa
                                print(f"[PROCESSAR_TRIGGER] Chamando main.principal com race_id={race_id}")
                                main.principal(
                                    carro_selecionado_p1=carro_p1_idx,
                                    carro_selecionado_p2=0,
                                    mapa_selecionado=track,
                                    modo_jogo=ModoJogo.UM_JOGADOR,
                                    tipo_jogo=tipo_jogo,
                                    voltas=laps,
                                    dificuldade_ia=difficulty,
                                    modo_arcade=modo_arcade,
                                    sem_bots=sem_bots,  # Passar flag para não criar bots
                                    race_id=race_id
                                )
                                
                                # Após a corrida, continuar narrativa se houver próxima cena
                                if on_result_scene_id:
                                    narrative_system.iniciar_cena(on_result_scene_id)
                                    narrative_system.active = True
                                    return "narrativa"
                            else:
                                print(f"Corrida {race_id} não encontrada em races.json")
                        
                        return "mapa"
                    
                    elif trigger_type in ["open_shop", "openShop", "open_shop_interface"]:
                        # Abrir loja (integrado à narrativa da CAMPANHA)
                        shop_id = params.get("shopId")
                        on_close_scene_id = params.get("onCloseSceneId") or params.get("onCloseSceneId")
                        
                        # Verificar se a loja já foi processada (evitar loop infinito)
                        if not hasattr(processar_trigger, '_loja_processada'):
                            processar_trigger._loja_processada = set()
                        
                        trigger_key = f"{shop_id}_{on_close_scene_id}"
                        if trigger_key in processar_trigger._loja_processada:
                            print(f"[BORIS SHOP] Trigger já processado, ignorando: {trigger_key}")
                            # Se já foi processado, apenas continuar para a próxima cena
                            # Retornar None para que o loop principal processe a narrativa normalmente
                            if on_close_scene_id:
                                narrative_system.iniciar_cena(on_close_scene_id)
                                narrative_system.active = True
                                return None  # Deixar o loop principal processar a narrativa
                            return "mapa"
                        
                        # Marcar como processado ANTES de entrar na loja
                        processar_trigger._loja_processada.add(trigger_key)
                        print(f"[BORIS SHOP] Processando trigger: {trigger_key}")
                        
                        # Limpar current_scene_id após obter o trigger, mas antes de processar
                        # Isso evita que a cena seja reiniciada
                        if narrative_system.current_scene_id:
                            cena_anterior = narrative_system.current_scene_id
                            narrative_system.current_scene_id = None
                            narrative_system.active = False
                            print(f"[BORIS SHOP] current_scene_id limpo ({cena_anterior}) antes de abrir loja")
                        
                        # Implementação específica para a loja do Boris no fluxo da campanha:
                        # após a fala "Seguinte: tenho peças feias, baratas e fortes..."
                        # o jogador entra em uma tela simples de compra com o Boris,
                        # depois a narrativa continua para a próxima cena (garagem).
                        if shop_id == "boris_unlock_cinturao":
                            # Tela especial para desbloquear o Cinturão Industrial
                            from core.boris import boris
                            from core.menu import render_text
                            from config import FPS, LARGURA, ALTURA
                            from core.progresso import gerenciador_progresso
                            from core.mapa_locations import gerenciador_localizacoes
                            
                            # Ativar o Boris para usar o mesmo estilo da tela da peça
                            boris.ativar_loja_simples()
                            
                            preco_unlock = params.get("preco", 10000)
                            opcao_selecionada = 0  # 0 = Pagar, 1 = Sair
                            mensagem_status = ""
                            mensagem_tempo = 0.0
                            compra_concluida = False
                            
                            clock_boris = pygame.time.Clock()
                            rodando_boris = True
                            saiu_da_loja = False
                            
                            print(f"[BORIS UNLOCK] Iniciando tela de desbloqueio do Cinturão Industrial (preço: {preco_unlock})")
                            
                            while rodando_boris and boris.ativo and not saiu_da_loja:
                                dt = clock_boris.tick(FPS) / 1000.0
                                
                                from core.tempo_jogo import gerenciador_tempo
                                gerenciador_tempo.atualizar(dt)
                                
                                eventos = pygame.event.get()
                                for ev in eventos:
                                    if ev.type == pygame.QUIT:
                                        import sys
                                        pygame.quit()
                                        sys.exit()
                                    
                                    if ev.type == pygame.KEYDOWN:
                                        if compra_concluida:
                                            if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                                                saiu_da_loja = True
                                                rodando_boris = False
                                                boris.fechar()
                                                # Iniciar cena de confirmação
                                                narrative_system._iniciar_cena_sem_transicao("ch2_9_cinturao_unlocked")
                                                narrative_system.active = True
                                                return "narrativa"
                                        
                                        if ev.key in (pygame.K_UP, pygame.K_w):
                                            opcao_selecionada = (opcao_selecionada - 1) % 2
                                        elif ev.key in (pygame.K_DOWN, pygame.K_s):
                                            opcao_selecionada = (opcao_selecionada + 1) % 2
                                        elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                                            if opcao_selecionada == 0:  # Pagar
                                                if gerenciador_progresso.tem_dinheiro(preco_unlock):
                                                    gerenciador_progresso.remover_dinheiro(preco_unlock)
                                                    
                                                    # Desbloquear o Cinturão Industrial imediatamente
                                                    gerenciador_localizacoes.processar_efeito_narrativa("unlockRaceSet:cinturao_industrial")
                                                    
                                                    # Atualizar objetivo da missão m10_portoes_do_cinturao
                                                    from core.missoes import gerenciador_missoes
                                                    if gerenciador_missoes.missao_ativa_id == "m10_portoes_do_cinturao":
                                                        gerenciador_missoes.atualizar_objetivo_missao("m10_portoes_do_cinturao", "Corra no Cinturão Industrial")
                                                        print(f"[BORIS UNLOCK] Objetivo da missão m10_portoes_do_cinturao atualizado para 'Corra no Cinturão Industrial'")
                                                    
                                                    # Salvar todos os gerenciadores
                                                    gerenciador_progresso.salvar()
                                                    gerenciador_localizacoes.salvar()
                                                    gerenciador_missoes.salvar()
                                                    
                                                    # Forçar flush do sistema de arquivos
                                                    import sys
                                                    sys.stdout.flush()
                                                    
                                                    mensagem_status = f"Pagamento de ${preco_unlock:,} realizado!"
                                                    compra_concluida = True
                                                    print(f"[BORIS UNLOCK] Cinturão Industrial desbloqueado por ${preco_unlock:,}")
                                                    print(f"[BORIS UNLOCK] Progresso salvo - Dinheiro restante: ${gerenciador_progresso.dinheiro:,}")
                                                else:
                                                    mensagem_status = f"Você não tem dinheiro suficiente! Precisa de ${preco_unlock:,}"
                                                    mensagem_tempo = 0.0
                                            else:  # Sair
                                                saiu_da_loja = True
                                                rodando_boris = False
                                                boris.fechar()
                                                return "mapa"
                                        elif ev.key == pygame.K_ESCAPE:
                                            saiu_da_loja = True
                                            rodando_boris = False
                                            boris.fechar()
                                            return "mapa"
                                    # Suporte a controles (gamepad)
                                    elif ev.type in (pygame.JOYBUTTONDOWN, pygame.JOYHATMOTION, pygame.JOYAXISMOTION):
                                        from core.gamepad_manager import gerenciador_gamepad
                                        if gerenciador_gamepad.obter_numero_controles() > 0:
                                            from core.menu_controles import processar_eventos_controle_menu
                                            tempo_atual = pygame.time.get_ticks()
                                            resultado_controle = processar_eventos_controle_menu(ev, opcao_selecionada, 2, joystick_id=0, tempo_atual=tempo_atual)
                                            if resultado_controle:
                                                acao = resultado_controle.get("acao")
                                                if compra_concluida and acao in ("confirmar", "cancelar"):
                                                    saiu_da_loja = True
                                                    rodando_boris = False
                                                    boris.fechar()
                                                    narrative_system._iniciar_cena_sem_transicao("ch2_9_cinturao_unlocked")
                                                    narrative_system.active = True
                                                    return "narrativa"
                                                elif acao == "cima":
                                                    opcao_selecionada = (opcao_selecionada - 1) % 2
                                                elif acao == "baixo":
                                                    opcao_selecionada = (opcao_selecionada + 1) % 2
                                                elif acao == "confirmar":
                                                    if opcao_selecionada == 0:  # Pagar
                                                        if gerenciador_progresso.tem_dinheiro(preco_unlock):
                                                            gerenciador_progresso.remover_dinheiro(preco_unlock)
                                                            gerenciador_progresso.salvar()
                                                            gerenciador_localizacoes.processar_efeito_narrativa("unlockRaceSet:cinturao_industrial")
                                                            gerenciador_localizacoes.salvar()
                                                            mensagem_status = f"Pagamento de ${preco_unlock:,} realizado!"
                                                            compra_concluida = True
                                                            print(f"[BORIS UNLOCK] Cinturão Industrial desbloqueado por ${preco_unlock:,}")
                                                        else:
                                                            mensagem_status = f"Você não tem dinheiro suficiente! Precisa de ${preco_unlock:,}"
                                                            mensagem_tempo = 0.0
                                                    else:  # Sair
                                                        saiu_da_loja = True
                                                        rodando_boris = False
                                                        boris.fechar()
                                                        return "mapa"
                                                elif acao == "cancelar":
                                                    saiu_da_loja = True
                                                    rodando_boris = False
                                                    boris.fechar()
                                                    return "mapa"
                                    # Suporte a clique do mouse nos botões
                                    elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                                        mouse_x, mouse_y = ev.pos
                                        # Calcular retângulos dos botões com mesma lógica do desenho
                                        caixa_largura = 500
                                        caixa_altura = 180
                                        caixa_x = (LARGURA - caixa_largura) // 2
                                        caixa_y = ALTURA - caixa_altura - 260
                                        botao_y_base = caixa_y + 105
                                        botao_altura = 30
                                        # Botão 0 = PAGAR
                                        rect_pagar = pygame.Rect(caixa_x + 40, botao_y_base, caixa_largura - 80, botao_altura)
                                        rect_sair = pygame.Rect(caixa_x + 40, botao_y_base + 30, caixa_largura - 80, botao_altura)
                                        
                                        if rect_pagar.collidepoint(mouse_x, mouse_y):
                                            opcao_selecionada = 0
                                            if not compra_concluida:
                                                if gerenciador_progresso.tem_dinheiro(preco_unlock):
                                                    gerenciador_progresso.remover_dinheiro(preco_unlock)
                                                    gerenciador_progresso.salvar()
                                                    gerenciador_localizacoes.processar_efeito_narrativa("unlockRaceSet:cinturao_industrial")
                                                    gerenciador_localizacoes.salvar()
                                                    mensagem_status = f"Pagamento de ${preco_unlock:,} realizado!"
                                                    compra_concluida = True
                                                    print(f"[BORIS UNLOCK] Cinturão Industrial desbloqueado por ${preco_unlock:,}")
                                                else:
                                                    mensagem_status = f"Você não tem dinheiro suficiente! Precisa de ${preco_unlock:,}"
                                                    mensagem_tempo = 0.0
                                        elif rect_sair.collidepoint(mouse_x, mouse_y):
                                            opcao_selecionada = 1
                                            saiu_da_loja = True
                                            rodando_boris = False
                                            boris.fechar()
                                            return "mapa"
                                
                                boris.atualizar(dt)
                                
                                # Desenhar Boris + UI de loja (mesmo estilo da tela da peça)
                                screen.fill((0, 0, 0))
                                boris.desenhar_dialogo(screen, dt)
                                
                                # Overlay de opções de compra (mesmo estilo da tela da peça)
                                caixa_largura = 500
                                caixa_altura = 180
                                caixa_x = (LARGURA - caixa_largura) // 2
                                caixa_y = ALTURA - caixa_altura - 260
                                
                                overlay = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
                                overlay.fill((0, 0, 0, 220))
                                screen.blit(overlay, (caixa_x, caixa_y))
                                pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 2)
                                
                                titulo = render_text("OFERTA DO BORIS", 22, (255, 255, 0), bold=True, pixel_style=True)
                                screen.blit(titulo, (caixa_x + (caixa_largura - titulo.get_width()) // 2, caixa_y + 10))
                                
                                desc = render_text("Acesso ao Cinturão Industrial", 18, (220, 220, 220), bold=False, pixel_style=True)
                                preco_txt = render_text(f"Preço: ${preco_unlock:,}", 18, (180, 255, 180), bold=False, pixel_style=True)
                                screen.blit(desc, (caixa_x + 20, caixa_y + 45))
                                screen.blit(preco_txt, (caixa_x + 20, caixa_y + 70))
                                
                                # Opções
                                if not compra_concluida:
                                    opcoes = [f"PAGAR ${preco_unlock:,}", "SAIR"]
                                    for i, texto_opcao in enumerate(opcoes):
                                        cor = (0, 200, 255) if i == opcao_selecionada else (200, 200, 200)
                                        txt = render_text(texto_opcao, 20, cor, bold=True, pixel_style=True)
                                        y = caixa_y + 105 + i * 30
                                        screen.blit(txt, (caixa_x + 40, y))
                                
                                # Mensagem de status (ex: dinheiro insuficiente)
                                if mensagem_status:
                                    mensagem_tempo += dt
                                    if mensagem_tempo < 4.0:
                                        msg_txt = render_text(mensagem_status, 16, (255, 180, 180), bold=False, pixel_style=True)
                                        screen.blit(msg_txt, (caixa_x + 40, caixa_y + caixa_altura - 30))
                                    else:
                                        mensagem_status = ""
                                        mensagem_tempo = 0.0
                                
                                pygame.display.flip()
                            
                            # Se saiu da loja sem comprar, retornar para o mapa
                            # Se comprou, já retornou "narrativa" dentro do loop
                            if not compra_concluida:
                                return "mapa"
                            # Se comprou, não deveria chegar aqui, mas por segurança:
                            return "narrativa"
                        
                        elif shop_id == "slick_alien":
                            # Loja do Slick - upgrades experimentais e especiais (padrão Pixel)
                            from core.menu import render_text
                            from config import FPS, LARGURA, ALTURA
                            from core.progresso import gerenciador_progresso
                            from core.narrative_system import narrative_system
                            
                            clock_slick = pygame.time.Clock()
                            
                            # Obter on_close_scene_id dos parâmetros
                            on_close_scene_id = params.get("onCloseSceneId")
                            
                            # Carregar upgrades já comprados do progresso
                            if not hasattr(gerenciador_progresso, 'slick_upgrades_comprados'):
                                gerenciador_progresso.slick_upgrades_comprados = []
                            
                            # Gerar upgrades especiais do Slick (muito bons e caros, sem depender de nível)
                            tipos_upgrade = ['motor', 'filtro_ar', 'ecu', 'transmissao', 'rodas', 'suspensao', 'nitro']
                            upgrades_disponiveis = []
                            
                            # Gerar 3-4 upgrades aleatórios especiais
                            import random
                            num_upgrades = random.randint(3, 4)
                            tipos_selecionados = random.sample(tipos_upgrade, min(num_upgrades, len(tipos_upgrade)))
                            
                            # Preços base muito altos para upgrades especiais do Slick
                            precos_base_especiais = {
                                'motor': 15000,
                                'filtro_ar': 12000,
                                'ecu': 14000,
                                'transmissao': 13000,
                                'rodas': 11000,
                                'suspensao': 12000,
                                'nitro': 16000
                            }
                            
                            for tipo in tipos_selecionados:
                                preco_base = precos_base_especiais.get(tipo, 13000)
                                # Variação de preço: ±20%
                                preco_final = int(preco_base * random.uniform(0.8, 1.2))
                                
                                # Criar ID único para este upgrade (sem nível)
                                upgrade_id = f"slick_{tipo}_{preco_final}"
                                
                                upgrades_disponiveis.append({
                                    'id': upgrade_id,
                                    'tipo': tipo,
                                    'preco': preco_final,
                                    'ja_comprado': upgrade_id in gerenciador_progresso.slick_upgrades_comprados,
                                    'nome': {
                                        'motor': 'Motor Experimental Alienígena',
                                        'filtro_ar': 'Filtro de Ar Quântico',
                                        'ecu': 'ECU Alienígena Avançada',
                                        'transmissao': 'Transmissão Dimensional',
                                        'rodas': 'Rodas de Plasma',
                                        'suspensao': 'Suspensão Antigravidade',
                                        'nitro': 'Nitro Hiperespacial'
                                    }.get(tipo, 'Upgrade Experimental'),
                                    'descricao': {
                                        'motor': 'Motor experimental alienígena que aumenta drasticamente potência e velocidade máxima (+50% força, +30% velocidade)',
                                        'filtro_ar': 'Filtro quântico que melhora drasticamente respiração do motor e reduz arrasto (+40% força, -15% arrasto)',
                                        'ecu': 'ECU alienígena com processamento avançado que otimiza tudo (+35% aceleração, +25% direção)',
                                        'transmissao': 'Transmissão dimensional para trocas instantâneas (+30% velocidade, +25% força)',
                                        'rodas': 'Rodas de plasma com aderência superior (+50% grip, +30% estabilidade)',
                                        'suspensao': 'Suspensão antigravidade para estabilidade máxima (+40% estabilidade, +30% controle)',
                                        'nitro': 'Nitro hiperespacial com carga dupla (+60% força nitro, +40% duração, -30% cooldown)'
                                    }.get(tipo, 'Upgrade experimental alienígena com bônus extraordinários')
                                })
                            
                            opcao_selecionada = 0
                            rodando_slick = True
                            saiu_da_loja = False
                            
                            print(f"[SLICK SHOP] Iniciando loja do Slick com {len(upgrades_disponiveis)} upgrades disponíveis")
                            
                            # Atualizar última aparição do Slick (cooldown de 4 dias)
                            from core.tempo_jogo import gerenciador_tempo
                            data_atual = gerenciador_tempo.obter_data_atual()
                            gerenciador_progresso.slick_ultima_aparicao_data = data_atual.strftime("%Y-%m-%d")
                            gerenciador_progresso.slick_primeira_aparicao_mostrada = True
                            gerenciador_progresso.salvar()
                            print(f"[SLICK] Última aparição atualizada para {gerenciador_tempo.obter_data_formatada()}, primeira aparição marcada como mostrada")
                            
                            # Carregar background e sprite do Slick
                            from core.hub_territorio import obter_caminho_beco_neon
                            import os
                            bg_slick = None
                            sprite_slick = None
                            
                            caminho_bg = obter_caminho_beco_neon()
                            if caminho_bg and os.path.exists(caminho_bg):
                                try:
                                    bg_slick = pygame.image.load(caminho_bg).convert()
                                    bg_slick = pygame.transform.scale(bg_slick, (LARGURA, ALTURA))
                                except Exception as e:
                                    print(f"[SLICK SHOP] Erro ao carregar background: {e}")
                            
                            # Tentar carregar sprite do Slick
                            try:
                                slick_dir = os.path.join(DIR_PROJETO, "assets", "images", "characters", "slick")
                                sprite_slick_path = os.path.join(slick_dir, "sorriso_teatral.png")
                                if not os.path.exists(sprite_slick_path):
                                    sprite_slick_path = os.path.join(slick_dir, "neutro.png")
                                if os.path.exists(sprite_slick_path):
                                    sprite_slick = pygame.image.load(sprite_slick_path).convert_alpha()
                                    # Redimensionar sprite do Slick (grande, como na cutscene)
                                    sprite_original_w = sprite_slick.get_width()
                                    sprite_original_h = sprite_slick.get_height()
                                    if sprite_original_w > 0 and sprite_original_h > 0:
                                        sprite_altura_max = 900
                                        sprite_largura_max = 800
                                        escala_w = sprite_largura_max / sprite_original_w if sprite_original_w > 0 else 1.0
                                        escala_h = sprite_altura_max / sprite_original_h if sprite_original_h > 0 else 1.0
                                        escala = min(escala_w, escala_h, 1.0)
                                        sprite_w = int(sprite_original_w * escala)
                                        sprite_h = int(sprite_original_h * escala)
                                        sprite_slick = pygame.transform.scale(sprite_slick, (sprite_w, sprite_h))
                            except Exception as e:
                                print(f"[SLICK SHOP] Erro ao carregar sprite do Slick: {e}")
                            
                            # Função auxiliar para processar compra
                            def processar_compra_slick(upgrade):
                                """Processa a compra de um upgrade especial do Slick"""
                                if upgrade['ja_comprado']:
                                    return False, "Este upgrade já foi comprado!"
                                
                                if not gerenciador_progresso.tem_dinheiro(upgrade['preco']):
                                    return False, "Dinheiro insuficiente!"
                                
                                # Remover dinheiro
                                gerenciador_progresso.remover_dinheiro(upgrade['preco'])
                                
                                # Marcar como comprado (upgrades do Slick são aplicados automaticamente, não dependem de nível)
                                upgrade['ja_comprado'] = True
                                if upgrade['id'] not in gerenciador_progresso.slick_upgrades_comprados:
                                    gerenciador_progresso.slick_upgrades_comprados.append(upgrade['id'])
                                gerenciador_progresso.salvar()
                                
                                return True, f"Upgrade {upgrade['nome']} adquirido! Os bônus serão aplicados automaticamente."
                            
                            while rodando_slick and not saiu_da_loja:
                                dt = clock_slick.tick(FPS) / 1000.0
                                
                                from core.tempo_jogo import gerenciador_tempo
                                gerenciador_tempo.atualizar(dt)
                                
                                eventos = pygame.event.get()
                                
                                # Área do menu (centro da tela - padrão Pixel)
                                menu_largura = 800
                                menu_altura = 500
                                menu_x = (LARGURA - menu_largura) // 2
                                menu_y = (ALTURA - menu_altura) // 2
                                
                                mouse_x, mouse_y = pygame.mouse.get_pos()
                                
                                y_inicio = menu_y + 100
                                altura_item = 80
                                espacamento = 10
                                
                                for i, upgrade in enumerate(upgrades_disponiveis):
                                    item_y = y_inicio + i * (altura_item + espacamento)
                                    item_rect = pygame.Rect(menu_x + 20, item_y, menu_largura - 40, altura_item)
                                    
                                    if item_rect.collidepoint(mouse_x, mouse_y):
                                        opcao_selecionada = i
                                
                                voltar_y = menu_y + menu_altura - 50
                                voltar_rect = pygame.Rect(menu_x + menu_largura - 150, voltar_y, 130, 35)
                                if voltar_rect.collidepoint(mouse_x, mouse_y):
                                    opcao_selecionada = len(upgrades_disponiveis)
                                
                                for ev in eventos:
                                    if ev.type == pygame.QUIT:
                                        import sys
                                        pygame.quit()
                                        sys.exit()
                                    
                                    if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                                        # Verificar clique em itens
                                        for i, upgrade in enumerate(upgrades_disponiveis):
                                            item_y = y_inicio + i * (altura_item + espacamento)
                                            item_rect = pygame.Rect(menu_x + 20, item_y, menu_largura - 40, altura_item)
                                            
                                            if item_rect.collidepoint(mouse_x, mouse_y):
                                                if not upgrade['ja_comprado']:
                                                    sucesso, mensagem = processar_compra_slick(upgrade)
                                                    print(f"[SLICK SHOP] {mensagem}")
                                                break
                                        
                                        # Verificar clique no botão "Voltar"
                                        if voltar_rect.collidepoint(mouse_x, mouse_y):
                                            saiu_da_loja = True
                                            rodando_slick = False
                                            # Iniciar cena para contar ao Pixel
                                            if on_close_scene_id:
                                                narrative_system.iniciar_cena(on_close_scene_id)
                                                narrative_system.active = True
                                                return None
                                            return "mapa"
                                    
                                    if ev.type == pygame.KEYDOWN:
                                        if ev.key == pygame.K_ESCAPE:
                                            saiu_da_loja = True
                                            rodando_slick = False
                                            # Iniciar cena para contar ao Pixel
                                            if on_close_scene_id:
                                                narrative_system.iniciar_cena(on_close_scene_id)
                                                narrative_system.active = True
                                                return None
                                            return "mapa"
                                        
                                        if ev.key in (pygame.K_UP, pygame.K_w):
                                            if opcao_selecionada > 0:
                                                opcao_selecionada -= 1
                                        elif ev.key in (pygame.K_DOWN, pygame.K_s):
                                            if opcao_selecionada < len(upgrades_disponiveis):
                                                opcao_selecionada += 1
                                        elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                                            if opcao_selecionada < len(upgrades_disponiveis):
                                                upgrade = upgrades_disponiveis[opcao_selecionada]
                                                if not upgrade['ja_comprado']:
                                                    sucesso, mensagem = processar_compra_slick(upgrade)
                                                    print(f"[SLICK SHOP] {mensagem}")
                                            elif opcao_selecionada == len(upgrades_disponiveis):
                                                saiu_da_loja = True
                                                rodando_slick = False
                                                # Iniciar cena para contar ao Pixel
                                                if on_close_scene_id:
                                                    narrative_system.iniciar_cena(on_close_scene_id)
                                                    narrative_system.active = True
                                                    return None
                                                return "mapa"
                                
                                # Desenhar background do beco neon
                                if bg_slick:
                                    screen.blit(bg_slick, (0, 0))
                                else:
                                    screen.fill((20, 20, 30))
                                
                                # Desenhar sprite do Slick (atrás do menu)
                                if sprite_slick:
                                    sprite_x = LARGURA // 2 - sprite_slick.get_width() // 2
                                    sprite_y = ALTURA - sprite_slick.get_height() - 100
                                    screen.blit(sprite_slick, (sprite_x, sprite_y))
                                
                                # Overlay escuro para melhorar legibilidade do menu
                                overlay_escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                                overlay_escuro.fill((0, 0, 0, 150))
                                screen.blit(overlay_escuro, (0, 0))
                                
                                # Fundo do menu
                                overlay_menu = pygame.Surface((menu_largura, menu_altura), pygame.SRCALPHA)
                                overlay_menu.fill((0, 0, 0, 240))
                                screen.blit(overlay_menu, (menu_x, menu_y))
                                
                                # Borda verde (tema tecnológico - padrão Pixel)
                                pygame.draw.rect(screen, (0, 255, 0), (menu_x, menu_y, menu_largura, menu_altura), 3)
                                
                                # Título
                                titulo = render_text("UPGRADES EXPERIMENTAIS", 28, (0, 255, 100), bold=True, pixel_style=True)
                                screen.blit(titulo, (menu_x + (menu_largura - titulo.get_width()) // 2, menu_y + 20))
                                
                                # Dinheiro
                                dinheiro_texto = render_text(f"Créditos: ${gerenciador_progresso.dinheiro:,}", 20, (255, 255, 100), bold=True, pixel_style=True)
                                screen.blit(dinheiro_texto, (menu_x + 20, menu_y + 60))
                                
                                # Desenhar upgrades
                                for i, upgrade in enumerate(upgrades_disponiveis):
                                    item_y = y_inicio + i * (altura_item + espacamento)
                                    item_rect = pygame.Rect(menu_x + 20, item_y, menu_largura - 40, altura_item)
                                    
                                    hover = item_rect.collidepoint(mouse_x, mouse_y) or i == opcao_selecionada
                                    cor_fundo = (20, 50, 20, 200) if hover else (10, 30, 10, 200)
                                    cor_borda = (0, 255, 0) if hover else (0, 200, 0)
                                    
                                    # Fundo do item
                                    overlay_item = pygame.Surface((item_rect.width, item_rect.height), pygame.SRCALPHA)
                                    overlay_item.fill(cor_fundo)
                                    screen.blit(overlay_item, item_rect.topleft)
                                    pygame.draw.rect(screen, cor_borda, item_rect, 2)
                                    
                                    # Nome do upgrade
                                    nome = upgrade['nome']
                                    if upgrade['ja_comprado']:
                                        nome += " [VENDIDO]"
                                    nome_texto = render_text(nome, 20, (0, 255, 150) if not upgrade['ja_comprado'] else (150, 150, 150), bold=True, pixel_style=True)
                                    screen.blit(nome_texto, (item_rect.x + 10, item_rect.y + 10))
                                    
                                    # Descrição
                                    desc_curta = upgrade['descricao'][:80] + "..." if len(upgrade['descricao']) > 80 else upgrade['descricao']
                                    desc_texto = render_text(desc_curta, 14, (200, 255, 200), bold=False, pixel_style=True)
                                    screen.blit(desc_texto, (item_rect.x + 10, item_rect.y + 35))
                                    
                                    # Preço (só mostrar se não foi comprado)
                                    if not upgrade['ja_comprado']:
                                        preco_texto = render_text(f"${upgrade['preco']:,}", 18, (255, 255, 0), bold=True, pixel_style=True)
                                        screen.blit(preco_texto, (item_rect.right - preco_texto.get_width() - 10, item_rect.y + 10))
                                
                                # Botão Voltar (padrão Pixel)
                                hover_voltar = voltar_rect.collidepoint(mouse_x, mouse_y) or opcao_selecionada == len(upgrades_disponiveis)
                                cor_voltar = (0, 255, 0) if hover_voltar else (0, 200, 0)
                                pygame.draw.rect(screen, (0, 0, 0), voltar_rect)
                                pygame.draw.rect(screen, cor_voltar, voltar_rect, 2)
                                voltar_texto = render_text("VOLTAR", 16, cor_voltar, bold=True, pixel_style=True)
                                screen.blit(voltar_texto, (voltar_rect.x + (voltar_rect.width - voltar_texto.get_width()) // 2, voltar_rect.y + 8))
                                
                                pygame.display.flip()
                            
                            # Iniciar cena para contar ao Pixel ao sair
                            if on_close_scene_id:
                                narrative_system.iniciar_cena(on_close_scene_id)
                                narrative_system.active = True
                                return None
                            return "mapa"
                        
                        elif shop_id == "boris_basic":
                            from core.boris import boris
                            from core.menu import render_text
                            from config import FPS, LARGURA, ALTURA
                            
                            # Para a CAMPANHA: já mostramos a cena de história antes.
                            # Aqui queremos ir DIRETO para a tela de compra, sem repetir
                            # uma nova fala de saudação. Por isso usamos ativar_loja_simples
                            # e começamos na fase "shop".
                            boris.ativar_loja_simples()
                            
                            clock_boris = pygame.time.Clock()
                            fase = "shop"  # pular o modo "dialogo" para não repetir saudação
                            
                            # Dados da peça principal que o jogador deve comprar
                            # Primeira compra do motor na campanha: preço fixo de 2000
                            from core.progresso import gerenciador_progresso
                            from core.missoes import gerenciador_missoes
                            # Verificar se é a primeira compra (missão m4 ainda não completada)
                            if "m4_coracao_de_sucata" not in gerenciador_missoes.missoes_completas:
                                # Primeira compra: preço fixo de 2000
                                peca_info = {
                                    'tipo': 'motor',
                                    'preco_base': 2000,
                                    'preco_final': 2000,
                                    'preco_tipo': 'otimo'
                                }
                            else:
                                # Compras subsequentes: usar cálculo normal com preço base de 2500
                                preco_base_motor = 2500
                                peca_info = boris.calcular_preco_peça("motor", preco_base=preco_base_motor)
                            opcao_selecionada = 0  # 0 = Comprar peça, 1 = Sair
                            mensagem_status = ""
                            mensagem_tempo = 0.0
                            compra_concluida = False  # Após compra bem-sucedida, usar ENTER/ESQ para sair
                            
                            rodando_boris = True
                            print("[BORIS SHOP] Iniciando loop da loja do Boris")
                            # Flag para garantir que não reinicie o loop após sair
                            saiu_da_loja = False
                            while rodando_boris and boris.ativo and not saiu_da_loja:
                                dt = clock_boris.tick(FPS) / 1000.0
                                
                                # Atualizar tempo do jogo
                                from core.tempo_jogo import gerenciador_tempo
                                gerenciador_tempo.atualizar(dt)
                                
                                eventos = pygame.event.get()
                                for ev in eventos:
                                    if ev.type == pygame.QUIT:
                                        # Fechar o jogo completamente se o jogador clicar no X da janela
                                        import sys
                                        pygame.quit()
                                        sys.exit()
                                
                                if fase == "shop":
                                    # Tela simples de compra: duas opções (Comprar / Sair)
                                    for ev in eventos:
                                        # Suporte a teclado
                                        if ev.type == pygame.KEYDOWN:
                                            # Se a compra já foi concluída, qualquer ENTER/ESPAÇO/ESC sai da loja
                                            if compra_concluida:
                                                if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                                                    saiu_da_loja = True
                                                    rodando_boris = False
                                                    boris.fechar()
                                                    print("[BORIS SHOP] Saindo após compra (ENTER/ESC)")
                                                    # Voltar imediatamente para a narrativa/garagem
                                                    if on_close_scene_id:
                                                        print(f"[BORIS SHOP] Iniciando cena: {on_close_scene_id}")
                                                        narrative_system.iniciar_cena(on_close_scene_id)
                                                        narrative_system.active = True
                                                        return None  # Deixar o loop principal processar a narrativa
                                                    print("[BORIS SHOP] Retornando para mapa")
                                                    return "mapa"
                                            
                                            if ev.key in (pygame.K_UP, pygame.K_w):
                                                opcao_selecionada = (opcao_selecionada - 1) % 2
                                            elif ev.key in (pygame.K_DOWN, pygame.K_s):
                                                opcao_selecionada = (opcao_selecionada + 1) % 2
                                            elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                                                if opcao_selecionada == 0 and peca_info is not None:
                                                    sucesso, msg = boris.processar_compra(peca_info)
                                                    mensagem_status = msg
                                                    mensagem_tempo = 0.0
                                                    if sucesso:
                                                        # Compra feita; marcar como concluída e encerrar imediatamente a loja
                                                        compra_concluida = True
                                                        saiu_da_loja = True
                                                        rodando_boris = False
                                                        boris.fechar()
                                                        print("[BORIS SHOP] Compra concluída, saindo da loja...")
                                                        if on_close_scene_id:
                                                            print(f"[BORIS SHOP] Iniciando cena: {on_close_scene_id}")
                                                            narrative_system.iniciar_cena(on_close_scene_id)
                                                            narrative_system.active = True
                                                            return "narrativa"
                                                        print("[BORIS SHOP] Retornando para mapa")
                                                        return "mapa"
                                                else:
                                                    # Sair da loja sem comprar - resetar flag para reiniciar a cena
                                                    saiu_da_loja = True
                                                    rodando_boris = False
                                                    boris.fechar()
                                                    print("[BORIS SHOP] Saindo sem comprar (opção SAIR) - resetando flag para reiniciar cena")
                                                    # Resetar flag para que a cena seja reiniciada quando voltar
                                                    from core.progresso import gerenciador_progresso
                                                    gerenciador_progresso.boris_primeira_aparicao_mostrada = False
                                                    boris.primeira_aparicao_mostrada = False
                                                    gerenciador_progresso.salvar()
                                                    boris.salvar_estado()
                                                    print("[BORIS SHOP] Flag resetada, cena será reiniciada na próxima visita")
                                                    # Limpar trigger processado para permitir reiniciar
                                                    if hasattr(processar_trigger, '_loja_processada'):
                                                        trigger_key = f"{shop_id}_{on_close_scene_id}"
                                                        processar_trigger._loja_processada.discard(trigger_key)
                                                        print(f"[BORIS SHOP] Trigger removido do cache: {trigger_key}")
                                                    return "mapa"
                                        # Suporte a ESC direto
                                        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                                            saiu_da_loja = True
                                            rodando_boris = False
                                            boris.fechar()
                                            print("[BORIS SHOP] Saindo com ESC - resetando flag para reiniciar cena")
                                            # Resetar flag para que a cena seja reiniciada quando voltar
                                            from core.progresso import gerenciador_progresso
                                            gerenciador_progresso.boris_primeira_aparicao_mostrada = False
                                            boris.primeira_aparicao_mostrada = False
                                            gerenciador_progresso.salvar()
                                            boris.salvar_estado()
                                            print("[BORIS SHOP] Flag resetada, cena será reiniciada na próxima visita")
                                            # Limpar trigger processado para permitir reiniciar
                                            if hasattr(processar_trigger, '_loja_processada'):
                                                trigger_key = f"{shop_id}_{on_close_scene_id}"
                                                processar_trigger._loja_processada.discard(trigger_key)
                                                print(f"[BORIS SHOP] Trigger removido do cache: {trigger_key}")
                                            return "mapa"
                                        # Suporte a controles (gamepad)
                                        elif ev.type in (pygame.JOYBUTTONDOWN, pygame.JOYHATMOTION, pygame.JOYAXISMOTION):
                                            from core.gamepad_manager import gerenciador_gamepad
                                            if gerenciador_gamepad.obter_numero_controles() > 0:
                                                from core.menu_controles import processar_eventos_controle_menu
                                                tempo_atual = pygame.time.get_ticks()
                                                resultado_controle = processar_eventos_controle_menu(ev, opcao_selecionada, 2, joystick_id=0, tempo_atual=tempo_atual)
                                                if resultado_controle:
                                                    acao = resultado_controle.get("acao")
                                                    if compra_concluida and acao in ("confirmar", "cancelar"):
                                                        saiu_da_loja = True
                                                        rodando_boris = False
                                                        boris.fechar()
                                                        print("[BORIS SHOP] Saindo após compra (gamepad)")
                                                        if on_close_scene_id:
                                                            print(f"[BORIS SHOP] Iniciando cena: {on_close_scene_id}")
                                                            narrative_system.iniciar_cena(on_close_scene_id)
                                                            narrative_system.active = True
                                                            return "narrativa"
                                                        print("[BORIS SHOP] Retornando para mapa")
                                                        return "mapa"
                                                    elif acao == "cima":
                                                        opcao_selecionada = (opcao_selecionada - 1) % 2
                                                    elif acao == "baixo":
                                                        opcao_selecionada = (opcao_selecionada + 1) % 2
                                                    elif acao == "confirmar":
                                                        if opcao_selecionada == 0 and peca_info is not None:
                                                            sucesso, msg = boris.processar_compra(peca_info)
                                                            mensagem_status = msg
                                                            mensagem_tempo = 0.0
                                                            if sucesso:
                                                                compra_concluida = True
                                                                saiu_da_loja = True
                                                                rodando_boris = False
                                                                boris.fechar()
                                                                print("[BORIS SHOP] Compra concluída (gamepad)")
                                                                if on_close_scene_id:
                                                                    print(f"[BORIS SHOP] Iniciando cena: {on_close_scene_id}")
                                                                    narrative_system.iniciar_cena(on_close_scene_id)
                                                                    narrative_system.active = True
                                                                    return "narrativa"
                                                                print("[BORIS SHOP] Retornando para mapa")
                                                                return "mapa"
                                                        else:
                                                            saiu_da_loja = True
                                                            rodando_boris = False
                                                            boris.fechar()
                                                            print("[BORIS SHOP] Saindo sem comprar (gamepad)")
                                                            if on_close_scene_id:
                                                                print(f"[BORIS SHOP] Iniciando cena: {on_close_scene_id}")
                                                                narrative_system.iniciar_cena(on_close_scene_id)
                                                                narrative_system.active = True
                                                                return "narrativa"
                                                            print("[BORIS SHOP] Retornando para mapa")
                                                            return "mapa"
                                                    elif acao == "cancelar":
                                                        saiu_da_loja = True
                                                        rodando_boris = False
                                                        boris.fechar()
                                                        print("[BORIS SHOP] Saindo com cancelar (gamepad)")
                                                        if on_close_scene_id:
                                                            print(f"[BORIS SHOP] Iniciando cena: {on_close_scene_id}")
                                                            narrative_system.iniciar_cena(on_close_scene_id)
                                                            narrative_system.active = True
                                                            return "narrativa"
                                                        print("[BORIS SHOP] Retornando para mapa")
                                                        return "mapa"
                                        # Suporte a clique do mouse nos botões
                                        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                                            mouse_x, mouse_y = ev.pos
                                            # Calcular retângulos dos botões com mesma lógica do desenho
                                            caixa_largura = 500
                                            caixa_altura = 180
                                            caixa_x = (LARGURA - caixa_largura) // 2
                                            caixa_y = ALTURA - caixa_altura - 260
                                            botao_y_base = caixa_y + 105
                                            botao_altura = 30
                                            # Botão 0 = COMPRAR PEÇA
                                            rect_comprar = pygame.Rect(caixa_x + 40, botao_y_base, caixa_largura - 80, botao_altura)
                                            rect_sair = pygame.Rect(caixa_x + 40, botao_y_base + 30, caixa_largura - 80, botao_altura)
                                            
                                            if rect_comprar.collidepoint(mouse_x, mouse_y):
                                                opcao_selecionada = 0
                                                if not compra_concluida and peca_info is not None:
                                                    sucesso, msg = boris.processar_compra(peca_info)
                                                    mensagem_status = msg
                                                    mensagem_tempo = 0.0
                                                    if sucesso:
                                                        compra_concluida = True
                                                        saiu_da_loja = True
                                                        rodando_boris = False
                                                        boris.fechar()
                                                        print("[BORIS SHOP] Compra concluída, saindo da loja...")
                                                        if on_close_scene_id:
                                                            print(f"[BORIS SHOP] Iniciando cena: {on_close_scene_id}")
                                                            narrative_system.iniciar_cena(on_close_scene_id)
                                                            narrative_system.active = True
                                                            return "narrativa"
                                                        print("[BORIS SHOP] Retornando para mapa")
                                                        return "mapa"
                                            elif rect_sair.collidepoint(mouse_x, mouse_y):
                                                opcao_selecionada = 1
                                                # Sair imediatamente
                                                saiu_da_loja = True
                                                print("[BORIS SHOP] Botão SAIR clicado, saindo da loja...")
                                                rodando_boris = False
                                                boris.fechar()
                                                if on_close_scene_id:
                                                    print(f"[BORIS SHOP] Iniciando cena: {on_close_scene_id}")
                                                    narrative_system.iniciar_cena(on_close_scene_id)
                                                    narrative_system.active = True
                                                    return "narrativa"
                                                print("[BORIS SHOP] Retornando para mapa")
                                                return "mapa"
                                    
                                    boris.atualizar(dt)
                                    
                                    # Desenhar Boris + UI de loja
                                    screen.fill((0, 0, 0))
                                    boris.desenhar_dialogo(screen, dt)
                                    
                                    # Overlay de opções de compra
                                    caixa_largura = 500
                                    caixa_altura = 180
                                    caixa_x = (LARGURA - caixa_largura) // 2
                                    caixa_y = ALTURA - caixa_altura - 260
                                    
                                    overlay = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
                                    overlay.fill((0, 0, 0, 220))
                                    screen.blit(overlay, (caixa_x, caixa_y))
                                    pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 2)
                                    
                                    titulo = render_text("OFERTA DO BORIS", 22, (255, 255, 0), bold=True, pixel_style=True)
                                    screen.blit(titulo, (caixa_x + (caixa_largura - titulo.get_width()) // 2, caixa_y + 10))
                                    
                                    if peca_info is not None:
                                        desc = render_text("MOTOR reforçado para melhorar seu carro", 18, (220, 220, 220), bold=False, pixel_style=True)
                                        preco_txt = render_text(f"Preço: ${peca_info['preco_final']:,}", 18, (180, 255, 180), bold=False, pixel_style=True)
                                        screen.blit(desc, (caixa_x + 20, caixa_y + 45))
                                        screen.blit(preco_txt, (caixa_x + 20, caixa_y + 70))
                                    
                                    # Opções
                                    from core.i18n import t
                                    opcoes = [t("confirmacao.upgrade.comprar_peca"), t("confirmacao.upgrade.sair")]
                                    for i, texto_opcao in enumerate(opcoes):
                                        cor = (0, 200, 255) if i == opcao_selecionada else (200, 200, 200)
                                        txt = render_text(texto_opcao, 20, cor, bold=True, pixel_style=True)
                                        y = caixa_y + 105 + i * 30
                                        screen.blit(txt, (caixa_x + 40, y))
                                    
                                    # Mensagem de status (ex: dinheiro insuficiente)
                                    if mensagem_status:
                                        mensagem_tempo += dt
                                        if mensagem_tempo < 4.0:
                                            msg_txt = render_text(mensagem_status, 16, (255, 180, 180), bold=False, pixel_style=True)
                                            screen.blit(msg_txt, (caixa_x + 40, caixa_y + caixa_altura - 30))
                                        else:
                                            mensagem_status = ""
                                            mensagem_tempo = 0.0
                                    
                                    pygame.display.flip()
                            
                            # Se o loop terminou sem retornos antecipados (fallback),
                            # garantir que a narrativa continue corretamente.
                            print(f"[BORIS SHOP] Loop terminou. rodando_boris={rodando_boris}, boris.ativo={boris.ativo}")
                            if on_close_scene_id:
                                print(f"[BORIS SHOP] Fallback: Iniciando cena: {on_close_scene_id}")
                                narrative_system.iniciar_cena(on_close_scene_id)
                                narrative_system.active = True
                                return None  # Deixar o loop principal processar a narrativa
                            print("[BORIS SHOP] Fallback: Retornando para mapa")
                            return "mapa"
                        
                        # Outras lojas (não implementadas ainda)
                        if on_close_scene_id:
                            narrative_system.iniciar_cena(on_close_scene_id)
                            narrative_system.active = True
                            return None  # Deixar o loop principal processar a narrativa
                        
                        return "mapa"
                    
                    elif trigger_type == "open_garage":
                        # Abrir garagem/upgrades
                        mode = params.get("mode")
                        on_confirm_scene_id = params.get("onConfirmSceneId")
                        
                        # Verificar se deve forçar instalação do primeiro upgrade
                        if mode == "install_first_upgrade":
                            # Verificar estado da missão antes de abrir a garagem
                            from core.missoes import gerenciador_missoes
                            from core.progresso import gerenciador_progresso
                            from core.popup_musica import popup_musica
                            from main import CARROS_DISPONIVEIS
                            from core.i18n import t
                            from config import DIR_PROJETO, FPS, LARGURA, ALTURA
                            import os
                            import sys
                            # Garantir que render_text está acessível (está no mesmo módulo)
                            menu_module = sys.modules[__name__]
                            render_text_func = getattr(menu_module, 'render_text')
                            missao_instalacao_id = "m5_cirurgia_na_garagem"
                            upgrade_instalado = gerenciador_missoes.esta_completa(missao_instalacao_id)
                            
                            # Se já foi instalado, pular direto para a próxima cena
                            if upgrade_instalado and on_confirm_scene_id:
                                narrative_system.iniciar_cena(on_confirm_scene_id)
                                narrative_system.active = True
                                return "narrativa"
                            
                            # Menu simples para instalar peça (similar ao menu do Boris)
                            carro1 = CARROS_DISPONIVEIS[0]
                            prefixo_cor = carro1['prefixo_cor']
                            tipo_upgrade = "motor"  # O Boris sempre vende motor na primeira compra
                            
                            # Capturar fundo atual
                            fundo_garagem = screen.copy()
                            
                            # Menu simples de instalação
                            clock_instalacao = pygame.time.Clock()
                            opcao_selecionada = 0  # 0 = Instalar peça, 1 = Sair
                            rodando_menu = True
                            upgrade_instalado_no_loop = False  # Flag para rastrear se foi instalado
                            
                            while rodando_menu:
                                dt = clock_instalacao.tick(FPS) / 1000.0
                                
                                # Atualizar tempo do jogo
                                from core.tempo_jogo import gerenciador_tempo
                                gerenciador_tempo.atualizar(dt)
                                
                                # Verificar se deve sair do loop antes de processar eventos
                                if not rodando_menu:
                                    print("[INSTALAR PEÇA] Saindo do loop (verificação inicial)...")
                                    break
                                
                                eventos = pygame.event.get()
                                for ev in eventos:
                                    if ev.type == pygame.QUIT:
                                        import sys
                                        pygame.quit()
                                        sys.exit()
                                    
                                    if ev.type == pygame.KEYDOWN:
                                        if ev.key in (pygame.K_UP, pygame.K_w):
                                            opcao_selecionada = (opcao_selecionada - 1) % 2
                                        elif ev.key in (pygame.K_DOWN, pygame.K_s):
                                            opcao_selecionada = (opcao_selecionada + 1) % 2
                                        elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                                            print(f"[INSTALAR PEÇA] Tecla pressionada, opcao_selecionada={opcao_selecionada}")
                                            if opcao_selecionada == 0:
                                                # Instalar peça automaticamente
                                                print(f"[INSTALAR PEÇA] Tentando instalar upgrade: prefixo={prefixo_cor}, tipo={tipo_upgrade}")
                                                nivel_atual = gerenciador_progresso.obter_upgrade(prefixo_cor, tipo_upgrade)
                                                print(f"[INSTALAR PEÇA] Nível atual: {nivel_atual}")
                                                
                                                # Instalar upgrade de graça (já foi comprado do Boris)
                                                if prefixo_cor not in gerenciador_progresso.upgrades:
                                                    gerenciador_progresso.upgrades[prefixo_cor] = {}
                                                
                                                # Se o nível atual for 0 (padrão), instalar para nível 1
                                                # Se já tiver algum nível, incrementar (mas não passar de 5)
                                                novo_nivel = min(nivel_atual + 1, 5)
                                                gerenciador_progresso.upgrades[prefixo_cor][tipo_upgrade] = novo_nivel
                                                gerenciador_progresso.salvar()
                                                print(f"[INSTALAR PEÇA] Upgrade instalado: {nivel_atual} -> {novo_nivel}")
                                                
                                                # Completar missão m5_cirurgia_na_garagem
                                                try:
                                                    if gerenciador_missoes.missao_ativa_id == missao_instalacao_id:
                                                        gerenciador_missoes.completar_missao(missao_instalacao_id)
                                                        print("[GARAGEM] Missão 'Cirurgia na Garagem' completada após instalar upgrade!")
                                                except Exception as e:
                                                    print(f"[GARAGEM] Erro ao completar missão: {e}")
                                                
                                                # Tocar som de compra
                                                try:
                                                    if pygame.mixer.get_init():
                                                        som_compra_path = os.path.join(DIR_PROJETO, "assets", "sounds", "purchase", "caixa.mp3")
                                                        if os.path.exists(som_compra_path):
                                                            som_compra = pygame.mixer.Sound(som_compra_path)
                                                            som_compra.play()
                                                except Exception as e:
                                                    print(f"Erro ao tocar som de compra: {e}")
                                                
                                                # Marcar que upgrade foi instalado
                                                upgrade_instalado_no_loop = True
                                                
                                                # Continuar para a próxima cena ANTES de sair do loop
                                                if on_confirm_scene_id:
                                                    # Iniciar cena sem transição para garantir que está pronta
                                                    if narrative_system._iniciar_cena_sem_transicao(on_confirm_scene_id):
                                                        narrative_system.active = True
                                                        narrative_system.current_line_index = 0  # Resetar linha atual
                                                        print(f"[INSTALAR PEÇA] Upgrade instalado, cena iniciada: {on_confirm_scene_id}")
                                                    else:
                                                        print(f"[INSTALAR PEÇA] ERRO: Falha ao iniciar cena {on_confirm_scene_id}")
                                                
                                                # Mostrar mensagem de sucesso (não bloqueia)
                                                try:
                                                    nome_upgrade = t("menu.upgrades.motor")
                                                    popup_musica.mostrar(t("mensagens.upgrade_comprado").format(carro1['nome'], nome_upgrade), tipo="outra")
                                                except:
                                                    pass
                                                
                                                # Sair imediatamente do loop
                                                print(f"[INSTALAR PEÇA] Saindo do loop após instalação (teclado)")
                                                rodando_menu = False
                                                break
                                            else:
                                                # Sair sem instalar
                                                rodando_menu = False
                                                return "mapa"
                                        elif ev.key == pygame.K_ESCAPE:
                                            rodando_menu = False
                                            return "mapa"
                                    
                                    elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                                        mouse_x, mouse_y = pygame.mouse.get_pos()
                                        
                                        # Verificar clique nos botões
                                        caixa_largura = 500
                                        caixa_altura = 180
                                        caixa_x = (LARGURA - caixa_largura) // 2
                                        caixa_y = ALTURA - caixa_altura - 260
                                        botao_y_base = caixa_y + 105
                                        botao_altura = 30
                                        
                                        rect_instalar = pygame.Rect(caixa_x + 40, botao_y_base, caixa_largura - 80, botao_altura)
                                        rect_sair = pygame.Rect(caixa_x + 40, botao_y_base + 30, caixa_largura - 80, botao_altura)
                                        
                                        if rect_instalar.collidepoint(mouse_x, mouse_y):
                                            # Instalar peça
                                            print(f"[INSTALAR PEÇA] Clique no botão INSTALAR, prefixo={prefixo_cor}, tipo={tipo_upgrade}")
                                            nivel_atual = gerenciador_progresso.obter_upgrade(prefixo_cor, tipo_upgrade)
                                            print(f"[INSTALAR PEÇA] Nível atual: {nivel_atual}")
                                            
                                            # Instalar upgrade de graça (já foi comprado do Boris)
                                            if prefixo_cor not in gerenciador_progresso.upgrades:
                                                gerenciador_progresso.upgrades[prefixo_cor] = {}
                                            
                                            # Se o nível atual for 0 (padrão), instalar para nível 1
                                            # Se já tiver algum nível, incrementar (mas não passar de 5)
                                            novo_nivel = min(nivel_atual + 1, 5)
                                            gerenciador_progresso.upgrades[prefixo_cor][tipo_upgrade] = novo_nivel
                                            gerenciador_progresso.salvar()
                                            print(f"[INSTALAR PEÇA] Upgrade instalado: {nivel_atual} -> {novo_nivel}")
                                            
                                            # Completar missão
                                            try:
                                                if gerenciador_missoes.missao_ativa_id == missao_instalacao_id:
                                                    gerenciador_missoes.completar_missao(missao_instalacao_id)
                                                    print("[GARAGEM] Missão 'Cirurgia na Garagem' completada após instalar upgrade!")
                                            except Exception as e:
                                                print(f"[GARAGEM] Erro ao completar missão: {e}")
                                            
                                            # Tocar som
                                            try:
                                                if pygame.mixer.get_init():
                                                    som_compra_path = os.path.join(DIR_PROJETO, "assets", "sounds", "purchase", "caixa.mp3")
                                                    if os.path.exists(som_compra_path):
                                                        som_compra = pygame.mixer.Sound(som_compra_path)
                                                        som_compra.play()
                                            except Exception as e:
                                                print(f"Erro ao tocar som de compra: {e}")
                                            
                                            # Marcar que upgrade foi instalado
                                            upgrade_instalado_no_loop = True
                                            
                                            # Continuar para a próxima cena ANTES de sair do loop
                                            if on_confirm_scene_id:
                                                # Iniciar cena sem transição para garantir que está pronta
                                                if narrative_system._iniciar_cena_sem_transicao(on_confirm_scene_id):
                                                    narrative_system.active = True
                                                    narrative_system.current_line_index = 0  # Resetar linha atual
                                                    print(f"[INSTALAR PEÇA] Upgrade instalado (mouse), cena iniciada: {on_confirm_scene_id}")
                                                else:
                                                    print(f"[INSTALAR PEÇA] ERRO: Falha ao iniciar cena {on_confirm_scene_id}")
                                            
                                            # Mensagem (não bloqueia)
                                            try:
                                                nome_upgrade = t("menu.upgrades.motor")
                                                popup_musica.mostrar(t("mensagens.upgrade_comprado").format(carro1['nome'], nome_upgrade), tipo="outra")
                                            except:
                                                pass
                                            
                                            # Sair imediatamente do loop
                                            print(f"[INSTALAR PEÇA] Saindo do loop após instalação (mouse)")
                                            rodando_menu = False
                                            break
                                        elif rect_sair.collidepoint(mouse_x, mouse_y):
                                            rodando_menu = False
                                            break
                                
                                # Verificar se deve sair antes de desenhar
                                if not rodando_menu:
                                    print("[INSTALAR PEÇA] Saindo do loop de instalação...")
                                    break
                                
                                # Desenhar fundo
                                screen.blit(fundo_garagem, (0, 0))
                                
                                # Overlay escuro
                                overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                                overlay.fill((0, 0, 0, 200))
                                screen.blit(overlay, (0, 0))
                                
                                # Caixa de menu (similar ao Boris)
                                caixa_largura = 500
                                caixa_altura = 180
                                caixa_x = (LARGURA - caixa_largura) // 2
                                caixa_y = ALTURA - caixa_altura - 260
                                
                                overlay_caixa = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
                                overlay_caixa.fill((0, 0, 0, 220))
                                screen.blit(overlay_caixa, (caixa_x, caixa_y))
                                pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 2)
                                
                                # Título
                                titulo = render_text_func("INSTALAR PEÇA", 22, (255, 255, 0), bold=True, pixel_style=True)
                                screen.blit(titulo, (caixa_x + (caixa_largura - titulo.get_width()) // 2, caixa_y + 10))
                                
                                # Descrição
                                nome_upgrade = t("menu.upgrades.motor")
                                desc = render_text_func(f"{nome_upgrade} comprado do Boris", 18, (220, 220, 220), bold=False, pixel_style=True)
                                screen.blit(desc, (caixa_x + 20, caixa_y + 45))
                                
                                # Opções
                                opcoes = ["INSTALAR PEÇA", "SAIR"]
                                for i, texto_opcao in enumerate(opcoes):
                                    cor = (0, 200, 255) if i == opcao_selecionada else (200, 200, 200)
                                    txt = render_text_func(texto_opcao, 20, cor, bold=True, pixel_style=True)
                                    y = caixa_y + 105 + i * 30
                                    screen.blit(txt, (caixa_x + 40, y))
                                
                                pygame.display.flip()
                            
                            # Após sair do loop, retornar para continuar a narrativa
                            print(f"[INSTALAR PEÇA] Loop terminou. upgrade_instalado={upgrade_instalado_no_loop}, on_confirm_scene_id={on_confirm_scene_id}")
                            
                            # Se o upgrade foi instalado e há próxima cena, continuar narrativa
                            if upgrade_instalado_no_loop and on_confirm_scene_id:
                                print(f"[INSTALAR PEÇA] Garantindo que a narrativa está ativa para {on_confirm_scene_id}")
                                # Garantir que a narrativa está ativa e a cena foi iniciada
                                # Usar _iniciar_cena_sem_transicao para iniciar imediatamente sem fade
                                if not narrative_system.active or narrative_system.current_scene_id != on_confirm_scene_id:
                                    print(f"[INSTALAR PEÇA] Iniciando cena {on_confirm_scene_id} diretamente (active={narrative_system.active}, current_scene={narrative_system.current_scene_id})")
                                    # Iniciar cena sem transição para garantir que está pronta imediatamente
                                    if narrative_system._iniciar_cena_sem_transicao(on_confirm_scene_id):
                                        narrative_system.active = True
                                        narrative_system.current_line_index = 0  # Resetar linha atual
                                        print(f"[INSTALAR PEÇA] Cena iniciada com sucesso. active={narrative_system.active}, current_scene={narrative_system.current_scene_id}")
                                    else:
                                        print(f"[INSTALAR PEÇA] ERRO: Falha ao iniciar cena {on_confirm_scene_id}")
                                        return "mapa"
                                else:
                                    print(f"[INSTALAR PEÇA] Narrativa já está ativa com a cena correta")
                                print(f"[INSTALAR PEÇA] Retornando 'narrativa' para continuar para {on_confirm_scene_id}")
                                return "narrativa"
                            
                            print("[INSTALAR PEÇA] Retornando 'mapa'")
                            return "mapa"
                        else:
                            # Modo normal: apenas abrir garagem
                            selecionar_carros_loop(screen)
                            # Após fechar garagem, continuar narrativa se houver próxima cena
                            if on_confirm_scene_id:
                                narrative_system.iniciar_cena(on_confirm_scene_id)
                                narrative_system.active = True
                                return "narrativa"
                            return "mapa"
                    
                    elif trigger_type == "enable_feature":
                        # Habilitar recurso do jogo
                        feature_id = params.get("featureId")
                        on_next_scene_id = params.get("onNextSceneId")
                        # TODO: Implementar habilitação de recursos
                        if on_next_scene_id:
                            narrative_system.iniciar_cena(on_next_scene_id)
                            narrative_system.active = True
                            return "narrativa"
                        return "mapa"
                    
                    return None
                
                # Inicializar territorio_id como None no início do loop
                territorio_id = None
                
                # Verificar qual capítulo deve ser mostrado baseado no progresso
                capitulo_atual = gerenciador_progresso.obter_capitulo_atual()
                
                # limpar a cena para evitar que fique preso nos créditos
                if narrative_system.current_scene_id == "ch5_10_creditos" and not narrative_system.active:
                    print(f"[LOOP PRINCIPAL] Cena de créditos detectada mas narrativa não está ativa. Limpando...")
                    narrative_system.current_scene_id = None
                    narrative_system.current_chapter_id = None
                
                # Se o Capítulo 1 foi completado mas ainda está marcado como ch1, avançar para ch2
                if capitulo_atual == "ch1" and gerenciador_progresso.capitulo_foi_completo("ch1"):
                    print(f"[LOOP PRINCIPAL] Capítulo 1 completo, avançando para Capítulo 2")
                    gerenciador_progresso.definir_capitulo_atual("ch2")
                    gerenciador_progresso.salvar()
                    capitulo_atual = "ch2"
                    # Atualizar o current_chapter_id do narrative_system também
                    narrative_system.current_chapter_id = "ch2"
                
                # Se o Capítulo 2 foi completado mas ainda está marcado como ch2, avançar para ch3
                # Capítulo 2 está completo quando a missão m10_portoes_do_cinturao é completada
                if capitulo_atual == "ch2" and not gerenciador_progresso.capitulo_foi_completo("ch2"):
                    from core.missoes import gerenciador_missoes
                    if gerenciador_missoes.esta_completa("m10_portoes_do_cinturao"):
                        print(f"[LOOP PRINCIPAL] Capítulo 2 completo (missão m10 completada), avançando para Capítulo 3")
                        gerenciador_progresso.marcar_capitulo_completo("ch2")
                        gerenciador_progresso.definir_capitulo_atual("ch3")
                        gerenciador_progresso.salvar()
                        capitulo_atual = "ch3"
                
                # Se o Capítulo 2 foi completado mas ainda está marcado como ch2, avançar para ch3
                if capitulo_atual == "ch2" and gerenciador_progresso.capitulo_foi_completo("ch2"):
                    print(f"[LOOP PRINCIPAL] Capítulo 2 completo, avançando para Capítulo 3")
                    gerenciador_progresso.definir_capitulo_atual("ch3")
                    gerenciador_progresso.salvar()
                    capitulo_atual = "ch3"
                
                # Validar se o capítulo atual está correto baseado no progresso real
                from core.missoes import gerenciador_missoes
                gerenciador_missoes.carregar()
                
                # Determinar qual capítulo o jogador deveria estar baseado nas missões completas
                missoes_ch1 = ["m1_primeira_faisca", "m2_teste_de_sobrevivencia", "m3_rota_da_ferrugem", 
                               "m4_coracao_de_sucata", "m5_cirurgia_na_garagem", "m6_batismo_de_pista", "m7_olhos_no_painel"]
                missoes_ch2 = ["m8_oferta_envenenada", "m9a_peso_da_divida", "m10_portoes_do_cinturao", "m10b_corridas_cinturao"]
                missoes_ch3 = ["m11_chamado_da_montanha", "m12_fantasma_do_circuito", "m13_teste_de_fluxo", "m14_tres_mundos"]
                
                ch1_completas = sum(1 for m in missoes_ch1 if m in gerenciador_missoes.missoes_completas)
                ch2_completas = sum(1 for m in missoes_ch2 if m in gerenciador_missoes.missoes_completas)
                ch3_completas = sum(1 for m in missoes_ch3 if m in gerenciador_missoes.missoes_completas)
                
                # Determinar capítulo esperado baseado no progresso
                if ch1_completas < len(missoes_ch1):
                    capitulo_esperado = "ch1"
                elif ch2_completas < len(missoes_ch2):
                    capitulo_esperado = "ch2"
                elif ch3_completas < len(missoes_ch3):
                    capitulo_esperado = "ch3"
                else:
                    capitulo_esperado = "ch4"
                
                # Se o capítulo atual está muito mais avançado que o esperado, corrigir
                if capitulo_atual:
                    capitulo_atual_num = int(capitulo_atual.replace("ch", "")) if capitulo_atual.startswith("ch") else 0
                    capitulo_esperado_num = int(capitulo_esperado.replace("ch", "")) if capitulo_esperado.startswith("ch") else 0
                    
                    if capitulo_atual_num > capitulo_esperado_num + 1:
                        print(f"[LOOP PRINCIPAL] Capítulo atual ({capitulo_atual}) está muito mais avançado que o esperado ({capitulo_esperado}) baseado no progresso. Corrigindo...")
                        gerenciador_progresso.definir_capitulo_atual(capitulo_esperado)
                        capitulo_atual = capitulo_esperado
                        narrative_system.current_chapter_id = capitulo_esperado
                        narrative_system.current_scene_id = None
                        narrative_system.active = False
                        print(f"[LOOP PRINCIPAL] Capítulo corrigido para {capitulo_esperado} baseado no progresso real (ch1: {ch1_completas}/{len(missoes_ch1)}, ch2: {ch2_completas}/{len(missoes_ch2)}, ch3: {ch3_completas}/{len(missoes_ch3)})")
                
                if capitulo_atual is None:
                    # Primeira vez - iniciar Capítulo 1
                    # Mas primeiro verificar se já completamos o capítulo 1 (pode ter sido completado mas não salvo)
                    if gerenciador_progresso.capitulo_foi_completo("ch1"):
                        print(f"[LOOP PRINCIPAL] Capítulo 1 já foi completado, avançando para Capítulo 2")
                        gerenciador_progresso.definir_capitulo_atual("ch2")
                        gerenciador_progresso.salvar()
                        capitulo_atual = "ch2"
                        narrative_system.current_chapter_id = "ch2"
                    else:
                        # Primeira vez - iniciar Capítulo 1
                        print(f"[LOOP PRINCIPAL] Primeira vez - tentando iniciar Capítulo 1")
                        print(f"[LOOP PRINCIPAL] Cenas visitadas antes de iniciar: {narrative_system.scenes_visited}")
                        print(f"[LOOP PRINCIPAL] current_scene_id antes de iniciar: {narrative_system.current_scene_id}")
                        print(f"[LOOP PRINCIPAL] active antes de iniciar: {narrative_system.active}")
                        
                        if "ch1_0_prologue" in narrative_system.scenes_visited:
                            print(f"[LOOP PRINCIPAL] AVISO: ch1_0_prologue já está marcada como visitada em um novo save! Removendo...")
                            narrative_system.scenes_visited.discard("ch1_0_prologue")
                        
                        # FORÇAR: Garantir que o capítulo está definido
                        narrative_system.current_chapter_id = "ch1"
                        
                        # Tentar iniciar o capítulo
                        if narrative_system.iniciar_capitulo("ch1"):
                            print(f"[LOOP PRINCIPAL] iniciar_capitulo('ch1') retornou True")
                            print(f"[LOOP PRINCIPAL] current_scene_id após iniciar: {narrative_system.current_scene_id}")
                            print(f"[LOOP PRINCIPAL] active após iniciar: {narrative_system.active}")
                            
                            # Verificar se uma cena foi realmente iniciada
                            if narrative_system.current_scene_id:
                                print(f"[LOOP PRINCIPAL] Cena {narrative_system.current_scene_id} foi iniciada, executando narrativa...")
                                narrative_system.active = True
                                trigger_resultado = executar_narrativa()
                                
                                # Marcar que o Capítulo 1 foi iniciado
                                gerenciador_progresso.definir_capitulo_atual("ch1")
                                gerenciador_progresso.salvar()
                                
                                # Se houve trigger, processar
                                if trigger_resultado:
                                    # Processar trigger será feito no loop principal abaixo
                                    pass
                            else:
                                print(f"[LOOP PRINCIPAL] ERRO: iniciar_capitulo('ch1') retornou True mas não iniciou uma cena!")
                                print(f"[LOOP PRINCIPAL] Tentando iniciar ch1_0_prologue manualmente...")
                                # Tentar iniciar a primeira cena manualmente
                                if "ch1_0_prologue" in narrative_system.scenes_visited:
                                    narrative_system.scenes_visited.discard("ch1_0_prologue")
                                    print(f"[LOOP PRINCIPAL] Removendo ch1_0_prologue de scenes_visited para permitir reinício")
                                
                                resultado = narrative_system._iniciar_cena_sem_transicao("ch1_0_prologue")
                                print(f"[LOOP PRINCIPAL] _iniciar_cena_sem_transicao('ch1_0_prologue') retornou: {resultado}")
                                print(f"[LOOP PRINCIPAL] current_scene_id após iniciar manualmente: {narrative_system.current_scene_id}")
                                
                                if narrative_system.current_scene_id:
                                    print(f"[LOOP PRINCIPAL] Cena iniciada com sucesso, executando narrativa...")
                                    narrative_system.active = True
                                    gerenciador_progresso.definir_capitulo_atual("ch1")
                                    gerenciador_progresso.salvar()
                                    # Executar a narrativa
                                    trigger_resultado = executar_narrativa()
                                    if trigger_resultado:
                                        # Processar trigger será feito no loop principal abaixo
                                        pass
                                else:
                                    print(f"[LOOP PRINCIPAL] ERRO CRÍTICO: Não foi possível iniciar a primeira cena do Capítulo 1!")
                                    print(f"[LOOP PRINCIPAL] Tentando forçar ativação da narrativa...")
                                    # Última tentativa: forçar ativação
                                    narrative_system.current_chapter_id = "ch1"
                                    narrative_system.current_scene_id = "ch1_0_prologue"
                                    narrative_system.active = True
                                    narrative_system.current_line_index = 0
                                    # Recarregar a cena
                                    narrative_system._iniciar_cena_sem_transicao("ch1_0_prologue")
                                    if narrative_system.current_scene_id:
                                        print(f"[LOOP PRINCIPAL] Forçou ativação com sucesso, executando narrativa...")
                                        trigger_resultado = executar_narrativa()
                                        if trigger_resultado:
                                            # Processar trigger será feito no loop principal abaixo
                                            pass
                                    else:
                                        print(f"[LOOP PRINCIPAL] ERRO: Mesmo forçando não funcionou! Indo para o mapa como fallback.")
                                        # Se não conseguiu iniciar, ir para o mapa como fallback
                                        # Garantir que a narrativa está fechada
                                        narrative_system.fechar()
                                        # Salvar progresso
                                        gerenciador_progresso.definir_capitulo_atual("ch1")
                                        gerenciador_progresso.salvar()
                                        from core.missoes import gerenciador_missoes
                                        from core.mapa_locations import gerenciador_localizacoes
                                        gerenciador_missoes.salvar()
                                        gerenciador_localizacoes.salvar()
                                        # Ir para o mapa
                                        territorio_id = mapa_cidade_loop(screen)
                                        if territorio_id is None:
                                            break
                                        continue
                        else:
                            print(f"[LOOP PRINCIPAL] ERRO: iniciar_capitulo('ch1') retornou False!")
                            # Tentar iniciar manualmente mesmo assim
                            print(f"[LOOP PRINCIPAL] Tentando iniciar ch1_0_prologue manualmente como fallback...")
                            if "ch1_0_prologue" in narrative_system.scenes_visited:
                                narrative_system.scenes_visited.discard("ch1_0_prologue")
                            
                            resultado = narrative_system._iniciar_cena_sem_transicao("ch1_0_prologue")
                            if resultado and narrative_system.current_scene_id:
                                print(f"[LOOP PRINCIPAL] Cena iniciada manualmente com sucesso, executando narrativa...")
                                narrative_system.active = True
                                narrative_system.current_chapter_id = "ch1"
                                gerenciador_progresso.definir_capitulo_atual("ch1")
                                gerenciador_progresso.salvar()
                                trigger_resultado = executar_narrativa()
                                if trigger_resultado:
                                    # Processar trigger será feito no loop principal abaixo
                                    pass
                            else:
                                print(f"[LOOP PRINCIPAL] ERRO: Não foi possível iniciar a primeira cena do Capítulo 1! Indo para o mapa como fallback.")
                                # Se não conseguiu iniciar, ir para o mapa como fallback
                                narrative_system.fechar()
                                gerenciador_progresso.definir_capitulo_atual("ch1")
                                gerenciador_progresso.salvar()
                                from core.missoes import gerenciador_missoes
                                from core.mapa_locations import gerenciador_localizacoes
                                gerenciador_missoes.salvar()
                                gerenciador_localizacoes.salvar()
                                # Ir para o mapa
                                territorio_id = mapa_cidade_loop(screen)
                                if territorio_id is None:
                                    break
                                continue
                elif capitulo_atual == "ch2" and not narrative_system.active:
                    # Se estamos no Capítulo 2 mas a narrativa não está ativa
                    # Verificar se há uma cena salva - se sim, não reiniciar o capítulo
                    if narrative_system.current_scene_id and narrative_system.current_chapter_id == "ch2":
                        # Há uma cena salva - verificar se já foi visitada
                        if narrative_system.current_scene_id in narrative_system.scenes_visited:
                            print(f"[LOOP PRINCIPAL] Cena {narrative_system.current_scene_id} já foi visitada, não reiniciando")
                            narrative_system.current_scene_id = None
                            narrative_system.active = False
                            # Verificar se já passamos da oferta do barão
                            if gerenciador_progresso.barao_nome_revelado:
                                print(f"[LOOP PRINCIPAL] Capítulo 2: Barão já foi visto, não reiniciando capítulo")
                            else:
                                # Cena visitada mas barão não foi visto - pode ser um bug, mas não reiniciar
                                print(f"[LOOP PRINCIPAL] Capítulo 2: Cena visitada mas barão não visto - pode ser inconsistência, não reiniciando")
                        else:
                            # Há uma cena salva que não foi visitada - continuar de onde parou
                            print(f"[LOOP PRINCIPAL] Capítulo 2: Continuando cena salva {narrative_system.current_scene_id}")
                            narrative_system.active = True
                    else:
                        # Não há cena salva - verificar se já passamos da oferta do barão
                        from core.progresso import gerenciador_progresso
                        if gerenciador_progresso.barao_nome_revelado:
                            # Já passamos pela oferta do barão, não reiniciar o capítulo
                            print(f"[LOOP PRINCIPAL] Capítulo 2: Barão já foi visto, não reiniciando capítulo")
                        else:
                            # Não há cena salva e barão não foi visto - iniciar capítulo normalmente
                            print(f"[LOOP PRINCIPAL] Iniciando Capítulo 2")
                            if narrative_system.iniciar_capitulo("ch2"):
                                # Verificar se uma cena foi realmente iniciada
                                if narrative_system.current_scene_id:
                                    narrative_system.active = True
                                    narrative_system.current_line_index = 0
                                    print(f"[LOOP PRINCIPAL] Capítulo 2 iniciado: scene_id={narrative_system.current_scene_id}")
                                else:
                                    print(f"[LOOP PRINCIPAL] Capítulo 2 iniciado mas não há cena imediata (aguardando gatilhos). Indo para o mapa.")
                                    narrative_system.fechar()
                                    # Salvar progresso
                                    gerenciador_progresso.salvar()
                                    from core.missoes import gerenciador_missoes
                                    from core.mapa_locations import gerenciador_localizacoes
                                    gerenciador_missoes.salvar()
                                    gerenciador_localizacoes.salvar()
                                    # Ir para o mapa
                                    territorio_id = mapa_cidade_loop(screen)
                                    if territorio_id is None:
                                        break
                                    continue
                
                elif capitulo_atual == "ch3" and not narrative_system.active:
                    # Verificar se as missões do capítulo 2 foram completadas antes de iniciar ch3
                    from core.missoes import gerenciador_missoes
                    missoes_ch2_necessarias = ["m8_oferta_envenenada", "m9a_peso_da_divida", "m10_portoes_do_cinturao", "m10b_corridas_cinturao"]
                    missoes_ch2_completas = [m for m in missoes_ch2_necessarias if m in gerenciador_missoes.missoes_completas]
                    
                    # Verificar também se a flag cinturaoUnlocked está definida
                    from core.progresso import gerenciador_progresso
                    cinturao_unlocked = getattr(gerenciador_progresso, 'cinturaoUnlocked', False) or narrative_system.flags.get("cinturaoUnlocked", False)
                    
                    if len(missoes_ch2_completas) < len(missoes_ch2_necessarias) or not cinturao_unlocked:
                        # Missões do capítulo 2 não foram completadas ou Cinturão não foi desbloqueado - voltar para ch2
                        print(f"[LOOP PRINCIPAL] Capítulo 3 detectado mas condições não atendidas. Missões ch2: {len(missoes_ch2_completas)}/{len(missoes_ch2_necessarias)}, cinturaoUnlocked: {cinturao_unlocked}. Ajustando para ch2...")
                        gerenciador_progresso.definir_capitulo_atual("ch2")
                        capitulo_atual = "ch2"
                        # Limpar cena do capítulo 3 se houver
                        if narrative_system.current_chapter_id == "ch3":
                            narrative_system.current_chapter_id = "ch2"
                            narrative_system.current_scene_id = None
                            narrative_system.active = False
                            print(f"[LOOP PRINCIPAL] Cena do capítulo 3 limpa")
                    else:
                        # Se estamos no Capítulo 3 mas a narrativa não está ativa
                        # Verificar se há uma cena salva - se sim, não reiniciar o capítulo
                        if narrative_system.current_scene_id and narrative_system.current_chapter_id == "ch3":
                            # Verificar se a cena salva é válida (não deve ser ch3_2_pixel_route se ainda não correu no Cinturão)
                            if narrative_system.current_scene_id == "ch3_2_pixel_route":
                                # Esta cena só deve aparecer após correr no Cinturão - limpar e voltar para ch2
                                print(f"[LOOP PRINCIPAL] Cena ch3_2_pixel_route detectada prematuramente. Voltando para ch2...")
                                gerenciador_progresso.definir_capitulo_atual("ch2")
                                capitulo_atual = "ch2"
                                narrative_system.current_chapter_id = "ch2"
                                narrative_system.current_scene_id = None
                                narrative_system.active = False
                            else:
                                # Há uma cena salva válida - não reiniciar, apenas continuar de onde parou
                                print(f"[LOOP PRINCIPAL] Capítulo 3: Continuando cena salva {narrative_system.current_scene_id}")
                        else:
                            # Não há cena salva - iniciar capítulo normalmente
                            print(f"[LOOP PRINCIPAL] Iniciando Capítulo 3")
                            if narrative_system.iniciar_capitulo("ch3"):
                                # Verificar se uma cena foi realmente iniciada
                                if narrative_system.current_scene_id:
                                    narrative_system.active = True
                                    narrative_system.current_line_index = 0
                                    print(f"[LOOP PRINCIPAL] Capítulo 3 iniciado: scene_id={narrative_system.current_scene_id}")
                                else:
                                    print(f"[LOOP PRINCIPAL] Capítulo 3 iniciado mas não há cena imediata (aguardando gatilhos). Indo para o mapa.")
                                    narrative_system.fechar()
                                    # Salvar progresso
                                    gerenciador_progresso.salvar()
                                    from core.missoes import gerenciador_missoes
                                    from core.mapa_locations import gerenciador_localizacoes
                                    gerenciador_missoes.salvar()
                                    gerenciador_localizacoes.salvar()
                                    # Ir para o mapa
                                    territorio_id = mapa_cidade_loop(screen)
                                    if territorio_id is None:
                                        break
                                    continue
                
                elif capitulo_atual == "ch4" and not narrative_system.active:
                    # Se estamos no Capítulo 4 mas a narrativa não está ativa
                    # Verificar se há uma cena salva - se sim, não reiniciar o capítulo
                    if narrative_system.current_scene_id and narrative_system.current_chapter_id == "ch4":
                        # Há uma cena salva - não reiniciar, apenas continuar de onde parou
                        print(f"[LOOP PRINCIPAL] Capítulo 4: Continuando cena salva {narrative_system.current_scene_id}")
                    else:
                        # Não há cena salva - iniciar capítulo normalmente
                        print(f"[LOOP PRINCIPAL] Iniciando Capítulo 4")
                        if narrative_system.iniciar_capitulo("ch4"):
                            narrative_system.active = True
                            narrative_system.current_line_index = 0
                            print(f"[LOOP PRINCIPAL] Capítulo 4 iniciado: scene_id={narrative_system.current_scene_id}")
                
                elif capitulo_atual == "ch5" and not narrative_system.active:
                    # Verificar se o jogador realmente completou o Capítulo 4 antes de iniciar o 5
                    from core.progresso import gerenciador_progresso
                    from core.missoes import gerenciador_missoes
                    
                    # Verificar se o Capítulo 4 foi completado (missões m15, m16, m17 completas)
                    ch4_completo = (
                        gerenciador_missoes.esta_completa("m15_ruido_nos_servidores") and
                        gerenciador_missoes.esta_completa("m16_contatos_estranhos") and
                        gerenciador_missoes.esta_completa("m17_convite_da_coroa")
                    )
                    
                    if ch4_completo:
                        # Se estamos no Capítulo 5 mas a narrativa não está ativa, iniciar
                        print(f"[LOOP PRINCIPAL] Iniciando Capítulo 5 (Capítulo 4 completo)")
                        if narrative_system.iniciar_capitulo("ch5"):
                            narrative_system.active = True
                            narrative_system.current_line_index = 0
                            print(f"[LOOP PRINCIPAL] Capítulo 5 iniciado: scene_id={narrative_system.current_scene_id}")
                    else:
                        # Se o Capítulo 4 não foi completado, reverter para o Capítulo 4
                        print(f"[LOOP PRINCIPAL] Capítulo 5 detectado mas Capítulo 4 não completo. Revertendo para Capítulo 4...")
                        gerenciador_progresso.definir_capitulo_atual("ch4")
                        gerenciador_progresso.salvar()
                        capitulo_atual = "ch4"
                
                # Loop principal de campanha - alterna entre narrativa e gameplay
                while True:
                    # Verificar se training_01 foi completada e iniciar narrativa se necessário
                    if _verificar_e_iniciar_narrativa_training_01(narrative_system, gerenciador_progresso):
                        continue
                    
                    # Verificar se a corrida da Akira (mountain_test_run) foi completada mas as cenas pós-corrida ainda não foram mostradas
                    # Não verificar apenas por estatísticas, pois isso pode ativar a cena incorretamente
                    from core.estatisticas import gerenciador_estatisticas
                    from core.missoes import gerenciador_missoes
                    
                    # Verificar se realmente acabou de completar a corrida da montanha
                    acabou_de_completar = (hasattr(gerenciador_progresso, 'ultima_corrida_campanha') and 
                                          gerenciador_progresso.ultima_corrida_campanha in ["mountain_test", "mountain_test_run"])
                    
                    # Só verificar se realmente acabou de completar a corrida
                    # NÃO verificar apenas por estatísticas antigas, pois isso ativa a cena incorretamente quando o jogador apenas entra/sai de locais
                    if acabou_de_completar:
                        gerenciador_estatisticas.carregar()
                        stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(3)
                        melhor_tempo = stats_pista.get("melhor_tempo", None) if stats_pista else None
                        melhor_posicao = stats_pista.get("melhor_posicao", None) if stats_pista else None
                        missao_m13_completa = "m13_teste_de_fluxo" in gerenciador_missoes.missoes_completas
                        
                        # Verificar se o capítulo 4 foi iniciado (indica que ch3_6 foi realmente completada)
                        capitulo_atual = gerenciador_progresso.obter_capitulo_atual()
                        ch4_iniciado = capitulo_atual == "ch4" or "ch4_1_pixel_warning" in narrative_system.scenes_visited
                        
                        # Se a corrida foi completada mas o capítulo 4 não foi iniciado, as cenas pós-corrida não foram realmente mostradas
                        corrida_completa = (melhor_tempo is not None and melhor_posicao is not None) or missao_m13_completa
                        
                        # Só processar se realmente acabou de completar a corrida (não apenas por estatísticas antigas)
                        # Isso evita que a cena seja ativada incorretamente quando o jogador apenas entra/sai de locais
                        if acabou_de_completar and not ch4_iniciado:
                            # Se todas as cenas estão marcadas como visitadas mas o capítulo 4 não foi iniciado,
                            # significa que foram marcadas incorretamente - remover todas e reiniciar
                            if "ch3_4_test_result" in narrative_system.scenes_visited and \
                               "ch3_5_crank_debrief" in narrative_system.scenes_visited and \
                               "ch3_6_pixel_wrap_up" in narrative_system.scenes_visited:
                                print(f"[LOOP PRINCIPAL] Cenas pós-corrida marcadas como visitadas mas capítulo 4 não iniciado. Removendo de visited e reiniciando sequência...")
                                narrative_system.scenes_visited.discard("ch3_4_test_result")
                                narrative_system.scenes_visited.discard("ch3_5_crank_debrief")
                                narrative_system.scenes_visited.discard("ch3_6_pixel_wrap_up")
                                # Salvar mudanças
                                gerenciador_progresso.salvar()
                            
                            # Verificar se ch3_4 ainda não foi visitada (após possível remoção)
                            if "ch3_4_test_result" not in narrative_system.scenes_visited:
                                print(f"[LOOP PRINCIPAL] Detectada corrida da Akira completada mas cena ch3_4_test_result não foi visitada. Iniciando narrativa...")
                                
                                # Determinar resultado do teste
                                if melhor_posicao is not None:
                                    resultado_teste = "good" if melhor_posicao <= 2 else "bad"
                                else:
                                    resultado_teste = "good"  # Default se não houver estatísticas
                                
                                narrative_system.variables["mountainTest"] = resultado_teste
                                narrative_system.variables["racePerformance"] = resultado_teste
                                
                                # Determinar resultado da corrida
                                if melhor_posicao is not None:
                                    resultado = "win" if melhor_posicao <= 2 else "lose"
                                else:
                                    resultado = "win"  # Default
                                
                                narrative_system.variables["lastRaceResult"] = resultado
                                
                                # Verificar gatilhos de race_finished
                                context = {
                                    "raceId": "mountain_test_run",
                                    "raceResult": resultado
                                }
                                if narrative_system.verificar_gatilhos_pendentes(context):
                                    narrative_system.active = True
                                    print(f"[LOOP PRINCIPAL] Narrativa ch3_4_test_result iniciada via verificar_gatilhos_pendentes")
                                    # Limpar flag após iniciar narrativa
                                    if hasattr(gerenciador_progresso, 'ultima_corrida_campanha'):
                                        gerenciador_progresso.ultima_corrida_campanha = None
                                        gerenciador_progresso.salvar()
                                    continue  # Voltar para o início do loop para executar narrativa
                                else:
                                    # Fallback: iniciar cena diretamente
                                    print(f"[LOOP PRINCIPAL] Gatilho não encontrado, iniciando cena ch3_4_test_result diretamente")
                                    narrative_system._iniciar_cena_sem_transicao("ch3_4_test_result")
                                    narrative_system.active = True
                                    # Limpar flag após iniciar narrativa
                                    if hasattr(gerenciador_progresso, 'ultima_corrida_campanha'):
                                        gerenciador_progresso.ultima_corrida_campanha = None
                                        gerenciador_progresso.salvar()
                                    continue
                    
                    if not narrative_system.active and not narrative_system.current_scene_id:
                        # Verificar se é um novo save (nenhuma missão completa)
                        from core.missoes import gerenciador_missoes
                        gerenciador_missoes.carregar()
                        if len(gerenciador_missoes.missoes_completas) == 0:
                            capitulo_atual = gerenciador_progresso.obter_capitulo_atual()
                            if not capitulo_atual or capitulo_atual == "ch1":
                                print(f"[LOOP PRINCIPAL] NOVO SAVE DETECTADO: Tentando iniciar Capítulo 1 antes de ir para o mapa")
                                # Garantir que o capítulo está definido
                                if not capitulo_atual:
                                    gerenciador_progresso.definir_capitulo_atual("ch1")
                                    gerenciador_progresso.salvar()
                                
                                # Remover ch1_0_prologue de scenes_visited se estiver lá
                                if "ch1_0_prologue" in narrative_system.scenes_visited:
                                    narrative_system.scenes_visited.discard("ch1_0_prologue")
                                    print(f"[LOOP PRINCIPAL] Removendo ch1_0_prologue de scenes_visited para permitir início")
                                
                                # Tentar iniciar o capítulo
                                narrative_system.current_chapter_id = "ch1"
                                if narrative_system.iniciar_capitulo("ch1"):
                                    if narrative_system.current_scene_id:
                                        print(f"[LOOP PRINCIPAL] Capítulo 1 iniciado com sucesso! Cena: {narrative_system.current_scene_id}")
                                        narrative_system.active = True
                                        # Continuar no loop para executar a narrativa
                                        continue
                                    else:
                                        print(f"[LOOP PRINCIPAL] iniciar_capitulo retornou True mas não iniciou cena, tentando iniciar ch1_0_prologue manualmente")
                                        resultado = narrative_system._iniciar_cena_sem_transicao("ch1_0_prologue")
                                        if resultado and narrative_system.current_scene_id:
                                            print(f"[LOOP PRINCIPAL] ch1_0_prologue iniciada manualmente com sucesso!")
                                            narrative_system.active = True
                                            continue
                                        else:
                                            print(f"[LOOP PRINCIPAL] Falha ao iniciar ch1_0_prologue manualmente")
                                else:
                                    print(f"[LOOP PRINCIPAL] iniciar_capitulo('ch1') retornou False")
                    
                    # Isso garante que corridas como garage_test sejam processadas imediatamente após retornar
                    gerenciador_progresso.carregar()
                    
                    # Verificar se foi garage_test (corrida de teste da garagem)
                    if hasattr(gerenciador_progresso, 'ultima_corrida_campanha') and gerenciador_progresso.ultima_corrida_campanha == "garage_test":
                        print(f"[LOOP PRINCIPAL] Detectada corrida garage_test pendente (ANTES de processar narrativa), verificando se foi completada...")
                        
                        # Verificar se a corrida foi completada
                        from core.estatisticas import gerenciador_estatisticas
                        gerenciador_estatisticas.carregar()
                        
                        # Verificar estatísticas da pista 1 (pista de teste)
                        stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(1)
                        melhor_tempo = stats_pista.get("melhor_tempo", None) if stats_pista else None
                        melhor_posicao = stats_pista.get("melhor_posicao", None) if stats_pista else None
                        print(f"[LOOP PRINCIPAL] Estatísticas pista 1 (garage_test): melhor_tempo={melhor_tempo}, melhor_posicao={melhor_posicao}")
                        
                        # Se completou a corrida, verificar gatilhos narrativos
                        if melhor_tempo is not None and melhor_posicao is not None:
                            print(f"[LOOP PRINCIPAL] Corrida garage_test completada! Verificando gatilhos narrativos...")
                            
                            # Limpar flag imediatamente para evitar loop
                            gerenciador_progresso.ultima_corrida_campanha = None
                            gerenciador_progresso.salvar()
                            
                            if "ch1_4b_housing_offer" not in narrative_system.scenes_visited:
                                narrative_system.scenes_visited.add("ch1_4b_housing_offer")
                                print(f"[LOOP PRINCIPAL] Marcando ch1_4b_housing_offer como visitada para evitar reativação")
                            
                            # Determinar resultado da corrida
                            resultado = "win" if melhor_posicao == 1 else "lose"
                            narrative_system.variables["lastRaceResult"] = resultado
                            
                            # Verificar gatilhos de race_finished
                            context = {
                                "raceId": "garage_test",
                                "raceResult": resultado
                            }
                            print(f"[LOOP PRINCIPAL] Verificando gatilhos pendentes com context: {context}")
                            gatilho_encontrado = narrative_system.verificar_gatilhos_pendentes(context)
                            print(f"[LOOP PRINCIPAL] verificar_gatilhos_pendentes retornou: {gatilho_encontrado}")
                            
                            if gatilho_encontrado:
                                print(f"[LOOP PRINCIPAL] Gatilho encontrado! Ativando narrativa...")
                                narrative_system.active = True
                                continue  # Voltar para o início do loop para executar narrativa
                            else:
                                print(f"[LOOP PRINCIPAL] Nenhum gatilho encontrado para garage_test. Tentando iniciar ch1_1c_crank_test_result manualmente...")
                                # Tentar iniciar a cena manualmente
                                if "ch1_1c_crank_test_result" in narrative_system.scenes_visited:
                                    print(f"[LOOP PRINCIPAL] Removendo ch1_1c_crank_test_result de scenes_visited para permitir reinício...")
                                    narrative_system.scenes_visited.discard("ch1_1c_crank_test_result")
                                
                                if "ch1_1c_crank_test_result" in narrative_system.scenes_visited:
                                    print(f"[LOOP PRINCIPAL] Removendo ch1_1c_crank_test_result de scenes_visited para permitir reinício...")
                                    narrative_system.scenes_visited.discard("ch1_1c_crank_test_result")
                                
                                resultado = narrative_system._iniciar_cena_sem_transicao("ch1_1c_crank_test_result")
                                print(f"[LOOP PRINCIPAL] _iniciar_cena_sem_transicao retornou: {resultado}, current_scene_id={narrative_system.current_scene_id}")
                                if resultado and narrative_system.current_scene_id:
                                    narrative_system.active = True
                                    print(f"[LOOP PRINCIPAL] Cena ch1_1c_crank_test_result iniciada com sucesso! Continuando narrativa...")
                                    from core.missoes import gerenciador_missoes
                                    gerenciador_missoes.carregar()
                                    if "m3_rota_da_ferrugem" not in gerenciador_missoes.missoes_completas:
                                        # Marcar a cena como visitada temporariamente para permitir ativação
                                        narrative_system.scenes_visited.add("ch1_1c_crank_test_result")
                                        # Tentar ativar m3
                                        missao_ativada = gerenciador_missoes.ativar_por_cena("ch1_1c_crank_test_result")
                                        if missao_ativada:
                                            print(f"[LOOP PRINCIPAL] Missão {missao_ativada} ativada após iniciar ch1_1c_crank_test_result")
                                            gerenciador_missoes.salvar()
                                        else:
                                            print(f"[LOOP PRINCIPAL] Nenhuma missão foi ativada após iniciar ch1_1c_crank_test_result")
                                    continue
                                else:
                                    # Se não conseguiu iniciar a cena, verificar se já foi visitada
                                    print(f"[LOOP PRINCIPAL] Não conseguiu iniciar ch1_1c_crank_test_result. Verificando se a cena já foi visitada...")
                                    if "ch1_1c_crank_test_result" in narrative_system.scenes_visited:
                                        print(f"[LOOP PRINCIPAL] Cena ch1_1c_crank_test_result já foi visitada. Completando missão m2 e continuando...")
                                        # Completar missão m2 se ainda não foi completada
                                        from core.missoes import gerenciador_missoes
                                        if "m2_teste_de_sobrevivencia" not in gerenciador_missoes.missoes_completas:
                                            gerenciador_missoes.completar_missao("m2_teste_de_sobrevivencia")
                                            gerenciador_missoes.salvar()
                                        # Continuar para o mapa normalmente
                                    else:
                                        print(f"[LOOP PRINCIPAL] ERRO: Não conseguiu iniciar ch1_1c_crank_test_result e a cena não foi visitada!")
                        else:
                            print(f"[LOOP PRINCIPAL] Corrida garage_test ainda não completada. Continuando normalmente...")
                    
                    # Verificar se há narrativa ativa OU se há uma cena ativa (mesmo que active=False temporariamente)
                    # (pode acontecer que a narrativa foi fechada mas o trigger ainda precisa ser processado)
                    if not narrative_system.active and not narrative_system.current_scene_id:
                        # Não há narrativa ativa e não há cena - ir direto para o mapa da cidade
                        print(f"[LOOP PRINCIPAL] Não há narrativa ativa, indo para o mapa da cidade")
                        # Salvar progresso antes de ir para o mapa
                        gerenciador_progresso.salvar()
                        from core.missoes import gerenciador_missoes
                        from core.mapa_locations import gerenciador_localizacoes
                        gerenciador_missoes.salvar()
                        gerenciador_localizacoes.salvar()
                        # Ir para o mapa
                        territorio_id = mapa_cidade_loop(screen)
                        if territorio_id is None:
                            # Se o mapa retornou None, voltar ao menu principal
                            break
                        # NÃO fazer continue aqui - deixar o código continuar para processar o territorio_id abaixo
                        # O código abaixo vai processar o territorio_id retornado do mapa
                        print(f"[LOOP PRINCIPAL] Mapa retornou territorio_id={territorio_id}, processando...")
                    
                    # Se há narrativa ativa, processar narrativa primeiro
                    if narrative_system.active or narrative_system.current_scene_id:
                        # Verificar se a narrativa foi fechada para iniciar uma corrida (current_scene_id None indica isso)
                        if narrative_system.current_scene_id is None and narrative_system.active:
                            print(f"[LOOP PRINCIPAL] Narrativa está ativa mas current_scene_id é None, fechando narrativa")
                            narrative_system.fechar()
                            continue
                        
                        # Se há uma cena ativa mas a narrativa não está marcada como ativa, ativar
                        if narrative_system.current_scene_id and not narrative_system.active:
                            scene_id = narrative_system.current_scene_id
                            
                            # Verificar se é ch1_4b_housing_offer e se garage_test já foi completada
                            if scene_id == "ch1_4b_housing_offer":
                                from core.estatisticas import gerenciador_estatisticas
                                gerenciador_estatisticas.carregar()
                                stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(1)
                                melhor_tempo = stats_pista.get("melhor_tempo", None) if stats_pista else None
                                melhor_posicao = stats_pista.get("melhor_posicao", None) if stats_pista else None
                                
                                # Se a corrida já foi completada, não reativar a cena
                                if melhor_tempo is not None and melhor_posicao is not None:
                                    print(f"[LOOP PRINCIPAL] ch1_4b_housing_offer detectada mas garage_test já foi completada. Não reativando cena.")
                                    # Limpar a cena e ir para o mapa ou próxima cena
                                    narrative_system.current_scene_id = None
                                    narrative_system.active = False
                                    # Tentar iniciar ch1_1c_crank_test_result se ainda não foi visitada
                                    if "ch1_1c_crank_test_result" not in narrative_system.scenes_visited:
                                        resultado = narrative_system._iniciar_cena_sem_transicao("ch1_1c_crank_test_result")
                                        if resultado:
                                            narrative_system.active = True
                                            continue
                                    # Se já foi visitada, ir para o mapa
                                    continue
                            
                            print(f"[LOOP PRINCIPAL] Cena {narrative_system.current_scene_id} ativa mas narrative_system.active=False, ativando...")
                            # Recarregar sprites e background da cena atual
                            # Encontrar a cena no JSON
                            scene = None
                            for ch in narrative_system.narrative_data.get("chapters", []):
                                if ch.get("id") == narrative_system.current_chapter_id:
                                    for sc in ch.get("scenes", []):
                                        if sc.get("id") == scene_id:
                                            scene = sc
                                            break
                                    if scene:
                                        break
                            
                            if scene:
                                # Recarregar background
                                bg_name = scene.get("bg")
                                if bg_name:
                                    narrative_system._carregar_background(bg_name)
                                
                                # Recarregar sprites
                                sprites_config = scene.get("sprites", [])
                                print(f"[LOOP PRINCIPAL] Recarregando sprites da cena {scene_id}: {sprites_config}")
                                narrative_system._carregar_sprites_cena(sprites_config)
                            
                            narrative_system.active = True
                        
                        # Verificar se o jogo terminou antes de executar narrativa
                        if narrative_system.game_ended:
                            print(f"[LOOP PRINCIPAL] Jogo terminou (game_ended=True), retornando ao menu principal")
                            narrative_system.game_ended = False  # Resetar flag
                            break  # Sair do loop de campanha e voltar ao menu principal
                        
                        trigger_resultado = executar_narrativa()
                        print(f"[LOOP PRINCIPAL] executar_narrativa retornou: {trigger_resultado}, type={type(trigger_resultado)}")
                        
                        # Verificar se o jogo terminou após executar narrativa
                        if narrative_system.game_ended:
                            print(f"[LOOP PRINCIPAL] Jogo terminou após executar_narrativa, retornando ao menu principal")
                            narrative_system.game_ended = False  # Resetar flag
                            break  # Sair do loop de campanha e voltar ao menu principal
                        
                        if trigger_resultado:
                            print(f"[LOOP PRINCIPAL] Trigger retornado de executar_narrativa: {trigger_resultado}")
                            # Fechar narrativa antes de processar trigger (se ainda não foi fechada)
                            if narrative_system.active:
                                print(f"[LOOP PRINCIPAL] Fechando narrativa antes de processar trigger")
                                narrative_system.fechar()
                            # Processar trigger
                            proximo_estado = processar_trigger(trigger_resultado)
                            print(f"[LOOP PRINCIPAL] Próximo estado após processar_trigger: {proximo_estado}")
                            if proximo_estado == "narrativa":
                                # Continuar narrativa (já foi iniciada no processar_trigger)
                                print(f"[LOOP PRINCIPAL] Continuando narrativa (active={narrative_system.active}, scene={narrative_system.current_scene_id})")
                                continue
                            elif proximo_estado == "mapa":
                                # Antes de ir para o mapa, verificar se há corrida da campanha pendente
                                # Forçar recarregamento do progresso para garantir dados atualizados
                                gerenciador_progresso.carregar()
                                
                                # Verificar se foi corrida do cinturão
                                if hasattr(gerenciador_progresso, 'ultima_corrida_campanha') and gerenciador_progresso.ultima_corrida_campanha and gerenciador_progresso.ultima_corrida_campanha.startswith("cinturao_pista_"):
                                    print(f"[LOOP PRINCIPAL] Detectada corrida do cinturão pendente, verificando se foi completada...")
                                    pista_num = int(gerenciador_progresso.ultima_corrida_campanha.split("_")[-1])
                                    
                                    from core.estatisticas import gerenciador_estatisticas
                                    gerenciador_estatisticas.carregar()
                                    stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(pista_num)
                                    melhor_tempo = stats_pista.get("melhor_tempo", None) if stats_pista else None
                                    melhor_posicao = stats_pista.get("melhor_posicao", None) if stats_pista else None
                                    
                                    if melhor_tempo is not None and melhor_posicao is not None:
                                        print(f"[LOOP PRINCIPAL] Corrida do cinturão completada! Limpando flag...")
                                        gerenciador_progresso.ultima_corrida_campanha = None
                                        gerenciador_progresso.salvar()
                                
                                # Verificar se foi garage_test (corrida de teste da garagem)
                                if hasattr(gerenciador_progresso, 'ultima_corrida_campanha') and gerenciador_progresso.ultima_corrida_campanha == "garage_test":
                                    print(f"[LOOP PRINCIPAL] Detectada corrida garage_test pendente, verificando se foi completada...")
                                    
                                    # Verificar se a corrida foi completada
                                    from core.estatisticas import gerenciador_estatisticas
                                    gerenciador_estatisticas.carregar()
                                    
                                    # Verificar estatísticas da pista 1 (pista de teste)
                                    stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(1)
                                    melhor_tempo = stats_pista.get("melhor_tempo", None) if stats_pista else None
                                    melhor_posicao = stats_pista.get("melhor_posicao", None) if stats_pista else None
                                    print(f"[LOOP PRINCIPAL] Estatísticas pista 1 (garage_test): melhor_tempo={melhor_tempo}, melhor_posicao={melhor_posicao}")
                                    
                                    # Se completou a corrida, verificar gatilhos narrativos
                                    if melhor_tempo is not None and melhor_posicao is not None:
                                        print(f"[LOOP PRINCIPAL] Corrida garage_test completada! Verificando gatilhos narrativos...")
                                        
                                        # Limpar flag imediatamente para evitar loop
                                        gerenciador_progresso.ultima_corrida_campanha = None
                                        gerenciador_progresso.salvar()
                                        
                                        # Determinar resultado da corrida
                                        resultado = "win" if melhor_posicao == 1 else "lose"
                                        narrative_system.variables["lastRaceResult"] = resultado
                                        
                                        # Verificar gatilhos de race_finished
                                        context = {
                                            "raceId": "garage_test",
                                            "raceResult": resultado
                                        }
                                        if narrative_system.verificar_gatilhos_pendentes(context):
                                            narrative_system.active = True
                                            continue  # Voltar para o início do loop para executar narrativa
                                        else:
                                            print(f"[LOOP PRINCIPAL] Nenhum gatilho encontrado para garage_test. Tentando iniciar ch1_1c_crank_test_result manualmente...")
                                            # Tentar iniciar a cena manualmente
                                            resultado = narrative_system._iniciar_cena_sem_transicao("ch1_1c_crank_test_result")
                                            if resultado:
                                                narrative_system.active = True
                                                continue
                                            else:
                                                # Se não conseguiu iniciar a cena, verificar se já foi visitada
                                                print(f"[LOOP PRINCIPAL] Não conseguiu iniciar ch1_1c_crank_test_result. Verificando se a cena já foi visitada...")
                                                if "ch1_1c_crank_test_result" in narrative_system.scenes_visited:
                                                    print(f"[LOOP PRINCIPAL] Cena ch1_1c_crank_test_result já foi visitada. Completando missão m2 e continuando...")
                                                    # Completar missão m2 se ainda não foi completada
                                                    from core.missoes import gerenciador_missoes
                                                    if "m2_teste_de_sobrevivencia" not in gerenciador_missoes.missoes_completas:
                                                        gerenciador_missoes.completar_missao("m2_teste_de_sobrevivencia")
                                                        gerenciador_missoes.salvar()
                                                    # Continuar para o mapa normalmente
                                                else:
                                                    print(f"[LOOP PRINCIPAL] ERRO: Não conseguiu iniciar ch1_1c_crank_test_result e a cena não foi visitada!")
                                    else:
                                        print(f"[LOOP PRINCIPAL] Corrida garage_test ainda não completada. Continuando para o mapa...")
                                
                                if hasattr(gerenciador_progresso, 'ultima_corrida_campanha') and gerenciador_progresso.ultima_corrida_campanha == "training_01":
                                    # Verificar se as cenas pós-corrida já foram visitadas para evitar loop
                                    if "ch1_6_post_race" in narrative_system.scenes_visited or "ch1_7_pixel_voice_intro" in narrative_system.scenes_visited:
                                        print(f"[LOOP PRINCIPAL] Cenas pós-corrida já foram visitadas. Limpando flag training_01 para evitar loop.")
                                        gerenciador_progresso.ultima_corrida_campanha = None
                                        gerenciador_progresso.salvar()
                                        continue
                                    
                                    print(f"[LOOP PRINCIPAL] Detectada corrida training_01 pendente, verificando se foi completada...")
                                    
                                    # Verificar se a corrida foi completada
                                    from core.estatisticas import gerenciador_estatisticas
                                    # Recarregar estatísticas também
                                    gerenciador_estatisticas.carregar()
                                    
                                    # Verificar também as estatísticas da pista 1 diretamente
                                    stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(1)
                                    melhor_tempo = stats_pista.get("melhor_tempo", None) if stats_pista else None
                                    melhor_posicao = stats_pista.get("melhor_posicao", None) if stats_pista else None
                                    print(f"[LOOP PRINCIPAL] Estatísticas pista 1: melhor_tempo={melhor_tempo}, melhor_posicao={melhor_posicao}")
                                    
                                    # Se completou a corrida, verificar gatilhos narrativos
                                    if melhor_tempo is not None and melhor_posicao is not None:
                                        print(f"[LOOP PRINCIPAL] Corrida training_01 completada! Verificando gatilhos narrativos...")
                                        
                                        # Determinar resultado da corrida
                                        resultado = "win" if melhor_posicao == 1 else "lose"
                                        narrative_system.variables["lastRaceResult"] = resultado
                                        
                                        # Verificar gatilhos de race_finished
                                        context = {
                                            "raceId": "training_01",
                                            "raceResult": resultado
                                        }
                                        if narrative_system.verificar_gatilhos_pendentes(context):
                                            print(f"[LOOP PRINCIPAL] Gatilho encontrado para training_01, ativando narrativa...")
                                            narrative_system.active = True
                                            gerenciador_progresso.ultima_corrida_campanha = None
                                            gerenciador_progresso.salvar()
                                            continue
                                        else:
                                            # Fallback para sistema antigo se não houver gatilho
                                            print(f"[LOOP PRINCIPAL] Nenhum gatilho encontrado, usando fallback _iniciar_narrativa_pos_training_01...")
                                            _iniciar_narrativa_pos_training_01(narrative_system, gerenciador_progresso)
                                            # Verificar se a narrativa foi ativada
                                            if narrative_system.active:
                                                print(f"[LOOP PRINCIPAL] Narrativa ativada pelo fallback, continuando...")
                                                continue
                                            else:
                                                print(f"[LOOP PRINCIPAL] AVISO: Fallback não ativou a narrativa! Tentando iniciar cena diretamente...")
                                                # Tentar iniciar a cena diretamente
                                                resultado = narrative_system._iniciar_cena_sem_transicao("ch1_6_post_race")
                                                if resultado:
                                                    narrative_system.active = True
                                                    gerenciador_progresso.ultima_corrida_campanha = None
                                                    gerenciador_progresso.salvar()
                                                    continue
                                                else:
                                                    print(f"[LOOP PRINCIPAL] ERRO: Não foi possível iniciar a cena ch1_6_post_race!")
                                            continue
                                    else:
                                        print(f"[LOOP PRINCIPAL] Corrida training_01 ainda não completada. Continuando para o mapa...")
                                
                                # Verificar se foi mountain_test ou mountain_test_run
                                if hasattr(gerenciador_progresso, 'ultima_corrida_campanha') and gerenciador_progresso.ultima_corrida_campanha in ["mountain_test", "mountain_test_run"]:
                                    print(f"[LOOP PRINCIPAL] Detectada corrida mountain_test pendente, verificando se foi completada...")
                                    
                                    # Verificar se a corrida foi completada
                                    from core.estatisticas import gerenciador_estatisticas
                                    gerenciador_estatisticas.carregar()
                                    
                                    # Verificar estatísticas da pista 3 (montanha)
                                    stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(3)
                                    melhor_tempo = stats_pista.get("melhor_tempo", None) if stats_pista else None
                                    melhor_posicao = stats_pista.get("melhor_posicao", None) if stats_pista else None
                                    print(f"[LOOP PRINCIPAL] Estatísticas pista 3 (montanha): melhor_tempo={melhor_tempo}, melhor_posicao={melhor_posicao}")
                                    
                                    # Se completou a corrida, verificar gatilhos narrativos
                                    if melhor_tempo is not None and melhor_posicao is not None:
                                        print(f"[LOOP PRINCIPAL] Mountain test completado! Verificando gatilhos narrativos...")
                                        from core.missoes import gerenciador_missoes
                                        
                                        # Completar missão m13_teste_de_fluxo
                                        if gerenciador_missoes.missao_ativa_id == "m13_teste_de_fluxo":
                                            gerenciador_missoes.completar_missao("m13_teste_de_fluxo")
                                            gerenciador_missoes.salvar()
                                        
                                        # Determinar resultado do teste (baseado em posição)
                                        # mountainTest=good se posição <= 2
                                        resultado_teste = "good" if melhor_posicao <= 2 else "bad"
                                        narrative_system.variables["mountainTest"] = resultado_teste
                                        narrative_system.variables["racePerformance"] = resultado_teste
                                        
                                        # Determinar resultado da corrida
                                        resultado = "win" if melhor_posicao <= 2 else "lose"
                                        narrative_system.variables["lastRaceResult"] = resultado
                                        
                                        # Verificar gatilhos de race_finished
                                        context = {
                                            "raceId": "mountain_test_run",
                                            "raceResult": resultado
                                        }
                                        if narrative_system.verificar_gatilhos_pendentes(context):
                                            narrative_system.active = True
                                            gerenciador_progresso.ultima_corrida_campanha = None
                                            gerenciador_progresso.salvar()
                                            continue  # Voltar para o início do loop para executar narrativa
                                    else:
                                        print(f"[LOOP PRINCIPAL] Mountain test ainda não completado. Continuando para o mapa...")
                                
                                # Verificar se foi corrida do Circuito da Coroa
                                if hasattr(gerenciador_progresso, 'ultima_corrida_campanha') and gerenciador_progresso.ultima_corrida_campanha and gerenciador_progresso.ultima_corrida_campanha.startswith("crown_"):
                                    print(f"[LOOP PRINCIPAL] Detectada corrida do Circuito da Coroa pendente: {gerenciador_progresso.ultima_corrida_campanha}")
                                    
                                    # Verificar se a corrida foi completada
                                    from core.estatisticas import gerenciador_estatisticas
                                    gerenciador_estatisticas.carregar()
                                    
                                    # Mapear race_id para número da pista
                                    race_id = gerenciador_progresso.ultima_corrida_campanha
                                    pista_map = {
                                        "crown_stage1": 8,  # Autódromo
                                        "crown_stage2": 8,  # Autódromo
                                        "crown_stage3": 8,  # Autódromo
                                        "crown_final": 8   # Autódromo
                                    }
                                    
                                    pista = pista_map.get(race_id)
                                    if pista:
                                        stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(pista)
                                        melhor_tempo = stats_pista.get("melhor_tempo", None) if stats_pista else None
                                        melhor_posicao = stats_pista.get("melhor_posicao", None) if stats_pista else None
                                        print(f"[LOOP PRINCIPAL] Estatísticas pista {pista} ({race_id}): melhor_tempo={melhor_tempo}, melhor_posicao={melhor_posicao}")
                                        
                                        # A flag ultima_corrida_campanha é definida no início da corrida em main.py
                                        # e deve permanecer definida até aqui para indicar que a corrida foi completada
                                        # Se a flag ainda está definida (igual ao race_id), significa que a corrida foi completada nesta sessão
                                        
                                        # Verificar se a corrida foi realmente completada: 
                                        # 1. Deve ter melhor_tempo e melhor_posicao (corrida foi completada alguma vez)
                                        # 2. A flag ultima_corrida_campanha deve estar definida e igual ao race_id (corrida foi iniciada e completada nesta sessão)
                                        
                                        # Se completou a corrida NESTA SESSÃO, verificar gatilhos narrativos
                                        # A flag ultima_corrida_campanha permanece definida até aqui para indicar que a corrida foi completada
                                        if melhor_tempo is not None and melhor_posicao is not None:
                                            # Verificar se a flag ainda está definida e igual ao race_id - se sim, a corrida foi completada nesta sessão
                                            if gerenciador_progresso.ultima_corrida_campanha == race_id:
                                                # Flag ainda está definida, significa que a corrida foi completada nesta sessão
                                                print(f"[LOOP PRINCIPAL] Corrida {race_id} completada nesta sessão! Verificando gatilhos narrativos...")
                                                
                                                # Determinar resultado (win se posição <= 2, lose caso contrário)
                                                resultado = "win" if melhor_posicao <= 2 else "lose"
                                                narrative_system.variables["lastRaceResult"] = resultado
                                                
                                                # Verificar gatilhos de race_finished
                                                context = {
                                                    "raceId": race_id,
                                                    "raceResult": resultado
                                                }
                                                if narrative_system.verificar_gatilhos_pendentes(context):
                                                    narrative_system.active = True
                                                    gerenciador_progresso.ultima_corrida_campanha = None
                                                    gerenciador_progresso.salvar()
                                                    continue  # Voltar para o início do loop para executar narrativa
                                                else:
                                                    # Não há gatilhos pendentes, limpar flag e continuar para o mapa
                                                    print(f"[LOOP PRINCIPAL] Nenhum gatilho narrativo encontrado para {race_id}. Continuando para o mapa...")
                                                    gerenciador_progresso.ultima_corrida_campanha = None
                                                    gerenciador_progresso.salvar()
                                            else:
                                                # Flag não está definida ou é diferente - corrida não foi completada nesta sessão ou já foi processada
                                                print(f"[LOOP PRINCIPAL] Corrida {race_id} não foi completada nesta sessão ou já foi processada (flag: {gerenciador_progresso.ultima_corrida_campanha}). Continuando para o mapa...")
                                                if gerenciador_progresso.ultima_corrida_campanha == race_id:
                                                    # Limpar flag se ainda estiver definida (caso de erro)
                                                    gerenciador_progresso.ultima_corrida_campanha = None
                                                    gerenciador_progresso.salvar()
                                    else:
                                        print(f"[LOOP PRINCIPAL] Pista não encontrada para {race_id}. Continuando para o mapa...")
                                
                                # Salvar progresso antes de ir para o mapa
                                gerenciador_progresso.salvar()
                                from core.missoes import gerenciador_missoes
                                from core.mapa_locations import gerenciador_localizacoes
                                gerenciador_missoes.salvar()
                                gerenciador_localizacoes.salvar()
                                
                                # Ir para o mapa
                            elif proximo_estado is None:
                                continue
                    
                    # Loop do mapa e gameplay
                    # Só chamar mapa_cidade_loop se territorio_id ainda não foi definido
                    # (pode ter sido definido anteriormente, por exemplo, na linha 12409)
                    if territorio_id is None:
                        territorio_id = mapa_cidade_loop(screen)
                        if territorio_id is None:
                            # Se o mapa retornou None, voltar ao menu principal
                            break
                    
                    # Verificar se há corrida da campanha completada antes de processar território
                    # Isso garante que a narrativa seja iniciada mesmo se o jogador voltar do mapa
                    # Mas só se a narrativa não estiver já ativa
                    if not narrative_system.active:
                        gerenciador_progresso.carregar()
                        from core.missoes import gerenciador_missoes
                        
                        # Verificar e registrar corridas do Cinturão já completadas (baseado em estatísticas)
                        from core.estatisticas import gerenciador_estatisticas
                        gerenciador_estatisticas.carregar()
                        
                        # Verificar se o Cinturão está desbloqueado (corrigir flag se necessário)
                        cinturao_unlocked_narrative = getattr(gerenciador_progresso, 'locations_unlocked_by_narrative', {}).get("cinturao_industrial", False)
                        if cinturao_unlocked_narrative and not getattr(gerenciador_progresso, 'cinturaoUnlocked', False):
                            print(f"[LOOP PRINCIPAL] Cinturão desbloqueado pela narrativa mas flag cinturaoUnlocked está False, corrigindo...")
                            gerenciador_progresso.cinturaoUnlocked = True
                            narrative_system.flags["cinturaoUnlocked"] = True
                        
                        # Verificar se há corridas nas pistas 4, 5 ou 6 que foram completadas mas não registradas
                        if not hasattr(gerenciador_progresso, 'corridas_cinturao_completas'):
                            gerenciador_progresso.corridas_cinturao_completas = set()
                        if isinstance(gerenciador_progresso.corridas_cinturao_completas, list):
                            gerenciador_progresso.corridas_cinturao_completas = set(gerenciador_progresso.corridas_cinturao_completas)
                        
                        # Verificar estatísticas das pistas 4, 5 e 6
                        for pista_num in [4, 5, 6]:
                            stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(pista_num)
                            if stats_pista and stats_pista.get("corridas_completas", 0) > 0:
                                # Se a pista tem corridas completas mas não está registrada, adicionar
                                if pista_num not in gerenciador_progresso.corridas_cinturao_completas:
                                    print(f"[LOOP PRINCIPAL] Detectada corrida do Cinturão já completada na pista {pista_num} (baseado em estatísticas), registrando...")
                                    gerenciador_progresso.corridas_cinturao_completas.add(pista_num)
                        
                        # Se completou 3 corridas mas a missão não foi completada, completar agora
                        if len(gerenciador_progresso.corridas_cinturao_completas) >= 3:
                            if "m10b_corridas_cinturao" not in gerenciador_missoes.missoes_completas:
                                print(f"[LOOP PRINCIPAL] Detectadas {len(gerenciador_progresso.corridas_cinturao_completas)} corridas do Cinturão completadas, completando missão m10b_corridas_cinturao...")
                                gerenciador_missoes.completar_missao("m10b_corridas_cinturao")
                                gerenciador_missoes.salvar()
                                
                                # Atualizar capítulo para ch3
                                capitulo_atual = gerenciador_progresso.obter_capitulo_atual()
                                if capitulo_atual != "ch3":
                                    print(f"[LOOP PRINCIPAL] Atualizando capítulo de {capitulo_atual} para ch3 após completar m10b_corridas_cinturao")
                                    gerenciador_progresso.definir_capitulo_atual("ch3")
                                    narrative_system.current_chapter_id = "ch3"
                                    gerenciador_progresso.salvar()
                        
                        # Verificar se a missão m14_tres_mundos deve ser completada (reputação >= 500)
                        try:
                            from core.status_jogador import status_jogador
                            if status_jogador.popularidade >= 500.0:
                                if gerenciador_missoes.missao_ativa_id == "m14_tres_mundos":
                                    if "m14_tres_mundos" not in gerenciador_missoes.missoes_completas:
                                        print(f"[LOOP PRINCIPAL] Reputação chegou a 500! Completando missão m14_tres_mundos...")
                                        gerenciador_missoes.completar_missao("m14_tres_mundos")
                                        gerenciador_missoes.salvar()
                        except Exception as e:
                            print(f"[LOOP PRINCIPAL] Erro ao verificar reputação para m14_tres_mundos: {e}")
                        
                        # Salvar progresso após verificar/registrar corridas
                        if len(gerenciador_progresso.corridas_cinturao_completas) > 0 or cinturao_unlocked_narrative:
                            gerenciador_progresso.salvar()
                        
                        # Verificar se m10b_corridas_cinturao foi completada e se há gatilhos pendentes
                        if "m10b_corridas_cinturao" in gerenciador_missoes.missoes_completas:
                            # Verificar se o capítulo foi atualizado para ch3
                            capitulo_atual = gerenciador_progresso.obter_capitulo_atual()
                            if capitulo_atual != "ch3":
                                print(f"[LOOP PRINCIPAL] m10b_corridas_cinturao completa mas capítulo ainda é {capitulo_atual}, atualizando para ch3...")
                                gerenciador_progresso.definir_capitulo_atual("ch3")
                                narrative_system.current_chapter_id = "ch3"
                                gerenciador_progresso.salvar()
                            
                            # Verificar gatilhos pendentes para ch3_1_crank_briefing (entrar na oficina)
                            # Mas só se a cena ainda não foi visitada
                            if "ch3_1_crank_briefing" not in narrative_system.scenes_visited:
                                print(f"[LOOP PRINCIPAL] m10b_corridas_cinturao completa, verificando gatilhos para ch3_1_crank_briefing...")
                                # Não forçar a cena aqui, apenas garantir que o capítulo está correto
                                # A cena será ativada quando o jogador entrar na oficina
                        
                        if hasattr(gerenciador_progresso, 'ultima_corrida_campanha') and gerenciador_progresso.ultima_corrida_campanha == "training_01":
                            from core.estatisticas import gerenciador_estatisticas
                            gerenciador_estatisticas.carregar()
                            stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(1)
                            melhor_tempo = stats_pista.get("melhor_tempo", None) if stats_pista else None
                            melhor_posicao = stats_pista.get("melhor_posicao", None) if stats_pista else None
                            
                            if melhor_tempo is not None and melhor_posicao is not None:
                                print(f"[LOOP PRINCIPAL] Corrida training_01 detectada como completa após retornar do mapa. Iniciando narrativa...")
                                _iniciar_narrativa_pos_training_01(narrative_system, gerenciador_progresso)
                                continue  # Voltar para o início do loop para executar narrativa
                        
                        # Verificar mountain_test também
                        if hasattr(gerenciador_progresso, 'ultima_corrida_campanha') and gerenciador_progresso.ultima_corrida_campanha == "mountain_test":
                            from core.estatisticas import gerenciador_estatisticas
                            gerenciador_estatisticas.carregar()
                            stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(3)
                            melhor_tempo = stats_pista.get("melhor_tempo", None) if stats_pista else None
                            melhor_posicao = stats_pista.get("melhor_posicao", None) if stats_pista else None
                            
                            if melhor_tempo is not None and melhor_posicao is not None:
                                print(f"[LOOP PRINCIPAL] Mountain test detectado como completo após retornar do mapa. Iniciando narrativa...")
                                from core.missoes import gerenciador_missoes
                                
                                # Completar missão m13_teste_de_fluxo
                                if gerenciador_missoes.missao_ativa_id == "m13_teste_de_fluxo":
                                    gerenciador_missoes.completar_missao("m13_teste_de_fluxo")
                                    gerenciador_missoes.salvar()
                                
                                # Determinar resultado do teste
                                resultado_teste = "good" if melhor_posicao <= 2 else "bad"
                                narrative_system.variables["mountainTest"] = resultado_teste
                                narrative_system.variables["racePerformance"] = resultado_teste
                                
                                # Determinar resultado da corrida
                                resultado = "win" if melhor_posicao <= 2 else "lose"
                                narrative_system.variables["lastRaceResult"] = resultado
                                
                                # Verificar gatilhos de race_finished (mountain_test_run no novo sistema)
                                # Também verificar mountain_test para compatibilidade
                                context = {
                                    "raceId": "mountain_test_run",
                                    "raceResult": resultado
                                }
                                gatilho_encontrado = narrative_system.verificar_gatilhos_pendentes(context)
                                
                                # Se não encontrou com mountain_test_run, tentar mountain_test
                                if not gatilho_encontrado:
                                    context["raceId"] = "mountain_test"
                                    gatilho_encontrado = narrative_system.verificar_gatilhos_pendentes(context)
                                
                                if gatilho_encontrado:
                                    narrative_system.active = True
                                    gerenciador_progresso.ultima_corrida_campanha = None
                                    gerenciador_progresso.salvar()
                                    continue  # Voltar para o início do loop para executar narrativa
                                else:
                                    # Fallback: usar cena antiga se não houver gatilho
                                    narrative_system._iniciar_cena_sem_transicao("ch3_6_test_result")
                                    narrative_system.active = True
                                    gerenciador_progresso.ultima_corrida_campanha = None
                                    gerenciador_progresso.salvar()
                                    continue
                    
                    # Processar território selecionado (se houver um territorio_id retornado do mapa)
                    if territorio_id:
                        print(f"[LOOP PRINCIPAL] Processando territorio_id={territorio_id}")
                    
                    if territorio_id == "oficina":
                        # Verificar gatilhos narrativos ANTES de entrar na oficina
                        from core.narrative_system import narrative_system
                        from core.missoes import gerenciador_missoes
                        
                        print(f"[MENU] Entrando na oficina. current_chapter_id={narrative_system.current_chapter_id}, missão m4 completa={'m4_coracao_de_sucata' in gerenciador_missoes.missoes_completas}")
                        
                        # SEMPRE verificar gatilhos primeiro, mesmo sem current_chapter_id
                        location_map = {
                            "oficina": "bg_garagem",
                            "bg_garagem": "bg_garagem",
                        }
                        location_id = location_map.get(territorio_id.lower(), territorio_id.lower())
                        context = {"locationId": location_id}
                        
                        print(f"[MENU] Verificando gatilhos antes de entrar na oficina: location_id={location_id}, context={context}")
                        
                        # Verificar se há cenas pendentes com gatilho enter_location
                        # Se current_chapter_id for None, tentar inferir do progresso
                        if not narrative_system.current_chapter_id:
                            capitulo_atual = gerenciador_progresso.obter_capitulo_atual()
                            if capitulo_atual:
                                narrative_system.current_chapter_id = capitulo_atual
                                print(f"[MENU] current_chapter_id estava None, atualizado para {capitulo_atual} baseado no progresso")
                        
                        # Se a missão m14b_voltar_oficina_pixel está ativa, garantir que estamos no capítulo 4
                        from core.missoes import gerenciador_missoes
                        if gerenciador_missoes.missao_ativa_id == "m14b_voltar_oficina_pixel":
                            if narrative_system.current_chapter_id != "ch4":
                                print(f"[MENU] Missão m14b_voltar_oficina_pixel ativa mas capítulo é {narrative_system.current_chapter_id}, atualizando para ch4...")
                                narrative_system.current_chapter_id = "ch4"
                                gerenciador_progresso.definir_capitulo_atual("ch4")
                                gerenciador_progresso.salvar()
                        
                        gatilho_encontrado = False
                        if narrative_system.current_chapter_id:
                            print(f"[MENU] Verificando gatilhos com current_chapter_id={narrative_system.current_chapter_id}, location_id={location_id}")
                            # Verificar flags e missões antes de verificar gatilhos
                            from core.progresso import gerenciador_progresso
                            cinturao_unlocked = getattr(gerenciador_progresso, 'cinturaoUnlocked', False) or narrative_system.flags.get("cinturaoUnlocked", False)
                            m10b_completa = "m10b_corridas_cinturao" in gerenciador_missoes.missoes_completas
                            print(f"[MENU] Verificando condições para ch3_1_crank_briefing: cinturaoUnlocked={cinturao_unlocked}, m10b_completa={m10b_completa}")
                            gatilho_encontrado = narrative_system.verificar_gatilhos_pendentes(context)
                        else:
                            print(f"[MENU] current_chapter_id é None, não é possível verificar gatilhos")
                        
                        print(f"[MENU] Resultado da verificação de gatilhos: {gatilho_encontrado}, current_scene_id={narrative_system.current_scene_id}, active={narrative_system.active}")
                        
                        # Se há gatilho OU se há uma cena ativa, executar narrativa PRIMEIRO
                        if gatilho_encontrado or narrative_system.current_scene_id or narrative_system.active:
                            print(f"[MENU] Gatilho encontrado ou narrativa ativa ao entrar na oficina, iniciando/continuando narrativa")
                            # Se a narrativa não está ativa mas há um gatilho, ativar
                            if not narrative_system.active and gatilho_encontrado:
                                narrative_system.active = True
                            
                            # Executar narrativa (isso vai processar a cena e desenhar na tela)
                            trigger_resultado = executar_narrativa()
                            print(f"[MENU] executar_narrativa retornou: {trigger_resultado}")
                            
                            # Verificar se o jogo terminou (após créditos)
                            if narrative_system.game_ended:
                                print(f"[MENU] Jogo terminou (game_ended=True), retornando ao menu principal")
                                narrative_system.game_ended = False  # Resetar flag
                                break  # Sair do loop de campanha e voltar ao menu principal
                            
                            if trigger_resultado:
                                proximo_estado = processar_trigger(trigger_resultado)
                                if proximo_estado == "narrativa":
                                    continue  # Continuar no loop principal para processar narrativa
                                elif proximo_estado == "mapa":
                                    continue  # Voltar para o mapa
                            
                            # Se a narrativa ainda está ativa após executar_narrativa, continuar processando
                            if narrative_system.active or narrative_system.current_scene_id:
                                print(f"[MENU] Narrativa ainda ativa após executar_narrativa, continuando no loop principal")
                                continue  # Continuar no loop principal para processar narrativa
                        
                        # Se não há gatilho narrativo E não há narrativa ativa, ir diretamente para a oficina
                        print(f"[MENU] Nenhum gatilho encontrado e narrativa não está ativa, indo para selecionar_carros_loop")
                        selecionar_carros_loop(screen)
                        continue  # Voltar para o loop do mapa após sair da oficina
                    elif territorio_id == "casa":
                        # Ir para a casa (hub com fundo da casa)
                        resultado_casa = casa_loop(screen)
                        # Se casa_loop retornou None após iniciar narrativa, verificar se narrativa está ativa
                        if resultado_casa is None:
                            # Verificar se narrativa foi iniciada (pode ter sido iniciada após corrida)
                            if narrative_system.active:
                                continue  # Voltar para o início do loop para executar narrativa
                        # Continuar normalmente se não houver narrativa ativa
                        areas_mapa = carregar_areas_mapa()
                        area_info = None
                        for area in areas_mapa:
                            if area.get("id") == "oficina" or area.get("id") == "casa":
                                area_info = area
                                break
                        
                        # Abrir hub da casa
                        # Salvar antes de entrar no hub
                        gerenciador_progresso.salvar()
                        atividade = hub_territorio_loop(
                            screen, 
                            "casa", 
                            area_nome="Casa",
                            sprite_fundo=obter_caminho_sprite_dia_noite("casa") if os.path.exists(obter_caminho_sprite_dia_noite("casa")) else None
                        )
                        
                        # Se retornou None e narrativa está ativa, continuar narrativa
                        if atividade is None and narrative_system.active:
                            continue  # Voltar para o início do loop para executar narrativa
                        
                        # Se retornou "voltar_mapa", voltar para o mapa ao invés do menu
                        if atividade == "voltar_mapa":
                            continue  # Voltar para o loop do mapa
                        
                        # Se retornou "menu_principal", voltar para o menu principal
                        if atividade == "menu_principal":
                            break  # Sair do loop de campanha e voltar ao menu principal
                        
                        # Se retornou None, também voltar para o mapa (compatibilidade)
                        if atividade is None:
                            continue  # Voltar para o mapa se cancelado
                        
                        continue
                    elif territorio_id:
                        # Verificar se deve iniciar narrativa específica (ex: Boris no fosso_ferrugem)
                        print(f"[MENU] Entrando no bloco elif territorio_id: territorio_id={territorio_id}")
                        territorio_id_lower = territorio_id.lower()
                        # Verificar se é Torre Rex - mostrar menu de escolha
                        is_torre_rex = ("torres_rex" in territorio_id_lower or "torre" in territorio_id_lower or 
                            "rex" in territorio_id_lower or "prédio" in territorio_id_lower or "predio" in territorio_id_lower)
                        
                        if is_torre_rex:
                            from core.mapa_cidade import mostrar_menu_torre_rex_beco_neon
                            
                            print(f"[MENU] Torre Rex detectada, mostrando menu de escolha...")
                            # Sempre mostrar menu de escolha
                            escolha_torre = mostrar_menu_torre_rex_beco_neon(screen)
                            if escolha_torre is None:
                                # Cancelou, voltar para o mapa
                                print(f"[MENU] Menu cancelado, voltando para o mapa")
                                continue
                            elif escolha_torre == "torre_rex":
                                # Ir para Torre Rex
                                print(f"[MENU] Escolhido: Torre Rex")
                                territorio_id = "torres_rex"
                            elif escolha_torre == "beco_neon":
                                # Ir para Beco Neon
                                print(f"[MENU] Escolhido: Beco Neon")
                                territorio_id = "beco_neon"
                        
                        is_boris_territory = ("fosso_ferrugem" in territorio_id_lower or "fábrica_do_boris" in territorio_id_lower or 
                            "fabrica_do_boris" in territorio_id_lower or "fabrica_boris" in territorio_id_lower or "boris" in territorio_id_lower)
                        
                        print(f"[MENU] Verificando território do Boris: is_boris_territory={is_boris_territory}, territorio_id_lower={territorio_id_lower}")
                        
                        # Se o territorio_id já é "fabrica_boris" ou "beco_da_sucata", significa que o menu já foi mostrado no mapa
                        # Não mostrar o menu novamente, apenas processar o território
                        menu_ja_mostrado = (territorio_id == "fabrica_boris" or territorio_id == "beco_da_sucata")
                        
                        print(f"[MENU] menu_ja_mostrado={menu_ja_mostrado}")
                        
                        # SEMPRE verificar se é território do Boris e se precisa iniciar a cena (mesmo se o menu já foi mostrado)
                        if is_boris_territory:
                            # Verificar capítulo atual
                            capitulo_atual = gerenciador_progresso.obter_capitulo_atual()
                            print(f"[MENU] Território do Boris detectado: {territorio_id}, capítulo: {capitulo_atual}, menu_ja_mostrado={menu_ja_mostrado}")
                            
                            # Verificar se estamos no capítulo 1
                            if capitulo_atual == "ch1":
                                # Garantir que o capítulo está definido no sistema de narrativa
                                if not narrative_system.current_chapter_id:
                                    narrative_system.current_chapter_id = "ch1"
                                    print(f"[NARRATIVA] Definindo current_chapter_id como ch1")
                                
                                # Verificar se a cena ch1_2_meet_boris já foi visitada
                                if "ch1_2_meet_boris" not in narrative_system.scenes_visited:
                                    # Iniciar cena do Boris SEM transição para garantir que a cena seja iniciada imediatamente
                                    print(f"[NARRATIVA] Clicou no fosso_ferrugem/fabrica_boris, iniciando cena ch1_2_meet_boris")
                                    # Garantir que o capítulo está definido
                                    if not narrative_system.current_chapter_id:
                                        narrative_system.current_chapter_id = "ch1"
                                    # Usar _iniciar_cena_sem_transicao para iniciar imediatamente
                                    resultado_iniciar = narrative_system._iniciar_cena_sem_transicao("ch1_2_meet_boris")
                                    if resultado_iniciar:
                                        print(f"[NARRATIVA] Cena ch1_2_meet_boris iniciada. current_scene_id={narrative_system.current_scene_id}")
                                        narrative_system.flags["metBoris"] = True
                                        narrative_system.active = True
                                        narrative_system.current_line_index = 0  # Garantir que começa do início
                                        trigger_resultado = executar_narrativa()
                                        if trigger_resultado:
                                            proximo_estado = processar_trigger(trigger_resultado)
                                            if proximo_estado == "narrativa":
                                                continue
                                            elif proximo_estado == "mapa":
                                                continue
                                        continue  # Voltar para o loop principal
                                    else:
                                        print(f"[NARRATIVA] Falha ao iniciar cena ch1_2_meet_boris, continuando normalmente...")
                                # Se a cena já foi vista, continuar normalmente para o hub do território
                                # (o hub_territorio.py já vai abrir a loja automaticamente)
                                print(f"[NARRATIVA] Cena do Boris já foi vista, continuando para o hub do território")
                            
                            # Se não é capítulo 1 E o menu ainda não foi mostrado, mostrar menu de escolha entre Boris e Glub ANTES de entrar
                            elif capitulo_atual and capitulo_atual != "ch1" and not menu_ja_mostrado:
                                from core.boris import boris
                                from core.mapa_cidade import mostrar_menu_fabrica_boris_glub
                                
                                print(f"[MENU] Capítulo {capitulo_atual} detectado, verificando se Boris foi apresentado...")
                                print(f"[MENU] boris.primeira_aparicao_mostrada = {boris.primeira_aparicao_mostrada}")
                                
                                # Verificar se Boris já foi apresentado (sempre mostrar menu após ch1)
                                if boris.primeira_aparicao_mostrada or capitulo_atual in ["ch2", "ch3", "ch4"]:
                                    print(f"[MENU] Mostrando menu de escolha entre Boris e Glub...")
                                    # Mostrar menu de escolha
                                    escolha_fabrica = mostrar_menu_fabrica_boris_glub(screen)
                                    if escolha_fabrica is None:
                                        # Cancelou, voltar para o mapa
                                        print(f"[MENU] Menu cancelado, voltando para o mapa")
                                        continue
                                    elif escolha_fabrica == "boris":
                                        # Ir para fábrica do Boris
                                        print(f"[MENU] Escolhido: Boris")
                                        territorio_id = "fosso_ferrugem"
                                    elif escolha_fabrica == "glub":
                                        # Ir para beco da sucata (Glub)
                                        print(f"[MENU] Escolhido: Glub")
                                        territorio_id = "beco_da_sucata"
                                else:
                                    print(f"[MENU] Boris ainda não foi apresentado, indo direto para o hub")
                        
                        # Mapear territorio_id se necessário (quando o menu já foi mostrado no mapa)
                        if territorio_id == "fabrica_boris":
                            # O menu já foi mostrado no mapa e escolheu Boris
                            territorio_id_hub = "fabrica_boris"
                        elif territorio_id == "beco_da_sucata":
                            # O menu já foi mostrado no mapa e escolheu Glub
                            territorio_id_hub = "beco_da_sucata"
                        else:
                            # Mapear outros IDs se necessário
                            territorio_id_hub = territorio_id
                        
                        # Carregar informações da área
                        areas_mapa = carregar_areas_mapa()
                        area_info = None
                        for area in areas_mapa:
                            # Procurar por ID da área, territorio_id, ou por mapeamento especial
                            area_id = area.get("id", "").lower()
                            area_territorio_id = area.get("territorio_id", "").lower()
                            territorio_id_lower = territorio_id.lower()
                            
                            if (area.get("id") == territorio_id or 
                                area.get("territorio_id") == territorio_id or
                                (territorio_id == "fabrica_boris" and ("fábrica" in area_id or "fabrica" in area_id or "boris" in area_id or "fosso" in area_territorio_id or "ferrugem" in area_territorio_id)) or
                                (territorio_id == "beco_da_sucata" and ("beco" in area_id or "sucata" in area_id))):
                                area_info = area
                                break
                        
                        # Abrir hub do território
                        print(f"[MENU] Abrindo hub do território: {territorio_id_hub} (área encontrada: {area_info.get('nome') if area_info else 'Nenhuma'})")
                        atividade = hub_territorio_loop(
                            screen, 
                            territorio_id_hub, 
                            area_nome=area_info.get("nome") if area_info else None,
                            sprite_fundo=area_info.get("sprite_fundo") if area_info else None
                        )
                        
                        # Se retornou "voltar_mapa", voltar para o mapa ao invés do menu
                        if atividade == "voltar_mapa":
                            # Salvar progresso ao voltar do hub para o mapa
                            gerenciador_progresso.salvar()
                            from core.missoes import gerenciador_missoes
                            from core.mapa_locations import gerenciador_localizacoes
                            gerenciador_missoes.salvar()
                            gerenciador_localizacoes.salvar()
                            continue  # Voltar para o loop do mapa
                        
                        # Se retornou "menu_principal", voltar para o menu principal
                        if atividade == "menu_principal":
                            # Salvar antes de sair
                            gerenciador_progresso.salvar()
                            from core.missoes import gerenciador_missoes
                            from core.mapa_locations import gerenciador_localizacoes
                            gerenciador_missoes.salvar()
                            gerenciador_localizacoes.salvar()
                            break  # Sair do loop de campanha e voltar ao menu principal
                        
                        # Se retornou "narrativa_ativa", processar narrativa
                        if atividade == "narrativa_ativa":
                            print(f"[MENU] Narrativa foi ativada ao entrar no território, continuando no loop para processar narrativa")
                            continue  # Voltar para o início do loop para executar narrativa
                        
                        # Se retornou None, verificar se narrativa foi iniciada
                        if atividade is None:
                            # Verificar se narrativa foi iniciada (pode ter sido iniciada após entrar no território)
                            if narrative_system.active:
                                print(f"[MENU] Narrativa foi iniciada ao entrar no território, continuando no loop para processar narrativa")
                                continue  # Voltar para o início do loop para executar narrativa
                            # Se não há narrativa ativa, voltar para o mapa (não para o menu)
                            # Salvar progresso ao voltar do hub para o mapa
                            print(f"[MENU] Hub do território retornou None sem narrativa ativa, voltando para o mapa")
                            gerenciador_progresso.salvar()
                            from core.missoes import gerenciador_missoes
                            from core.mapa_locations import gerenciador_localizacoes
                            gerenciador_missoes.salvar()
                            gerenciador_localizacoes.salvar()
                            continue  # Voltar para o mapa se cancelado (não para o menu)
                        
                        # Processar atividade selecionada
                        if isinstance(atividade, dict):
                            atividade_tipo = atividade.get("atividade")
                            print(f"[MENU] Processando atividade: tipo={atividade_tipo}, atividade completa={atividade}")
                            
                            # Processar corrida do Cinturão Industrial
                            if atividade_tipo == "corrida_cinturao":
                                pista = atividade.get("pista")
                                if pista:
                                    # Definir flag para verificar após a corrida
                                    gerenciador_progresso.ultima_corrida_campanha = f"cinturao_pista_{pista}"
                                    gerenciador_progresso.salvar()
                                    
                                    # Obter carro atual do jogador
                                    carro_p1_idx = 0
                                    if gerenciador_progresso.carro_p1_atual:
                                        from config import CARROS_DISPONIVEIS
                                        for i, carro in enumerate(CARROS_DISPONIVEIS):
                                            if carro.get("prefixo_cor") == gerenciador_progresso.carro_p1_atual:
                                                carro_p1_idx = i
                                                break
                                    
                                    # Modo de teste: marcar corrida como concluída automaticamente
                                    from config import MODO_TESTE_CORRIDAS
                                    if MODO_TESTE_CORRIDAS:
                                        print(f"[MODO TESTE] Corrida do Cinturão (pista {pista}) marcada como concluída automaticamente")
                                        from core.estatisticas import gerenciador_estatisticas
                                        gerenciador_estatisticas.carregar()
                                        # Registrar corrida como concluída (posição 1, tempo fictício)
                                        gerenciador_estatisticas.registrar_corrida_completa(
                                            numero_pista=pista,
                                            posicao_final=1,
                                            tempo_final=60.0  # Tempo fictício
                                        )
                                        gerenciador_estatisticas.salvar()
                                        
                                        # Obter informações da corrida (recompensa, índice)
                                        recompensa = atividade.get("recompensa", 0)
                                        indice_corrida = atividade.get("indice", 0)
                                        
                                        # Dar recompensa de dinheiro
                                        if recompensa > 0:
                                            gerenciador_progresso.adicionar_dinheiro(recompensa)
                                            print(f"[CINTURÃO] Recompensa de ${recompensa:,} adicionada!")
                                        
                                        # Desbloquear próxima corrida
                                        from core.fuligem import fuligem
                                        if indice_corrida == 0:  # Completou corrida 1, desbloquear corrida 2
                                            fuligem.desbloquear_corrida(1)
                                        elif indice_corrida == 1:  # Completou corrida 2, desbloquear corrida 3
                                            fuligem.desbloquear_corrida(2)
                                        
                                        # Avançar 8 horas no jogo
                                        from core.tempo_jogo import gerenciador_tempo
                                        gerenciador_tempo.avancar_horas(8.0)
                                        gerenciador_tempo.salvar()
                                        
                                        # Limpar flag e salvar
                                        gerenciador_progresso.ultima_corrida_campanha = None
                                        gerenciador_progresso.salvar()
                                        
                                        continue  # Voltar para o mapa após a corrida
                                    else:
                                        # Iniciar corrida normalmente
                                        from main import TipoJogo, ModoJogo
                                        import main
                                        
                                        # Obter informações da corrida (recompensa, índice)
                                        recompensa = atividade.get("recompensa", 0)
                                        indice_corrida = atividade.get("indice", 0)
                                        
                                        main.principal(
                                            carro_selecionado_p1=carro_p1_idx,
                                            carro_selecionado_p2=0,
                                            mapa_selecionado=pista,
                                            modo_jogo=ModoJogo.UM_JOGADOR,
                                            tipo_jogo=TipoJogo.CORRIDA,
                                            voltas=1,
                                            dificuldade_ia="alta",
                                            modo_arcade=False,
                                            sem_bots=False  # Corridas do Cinturão têm bots
                                        )
                                    
                                    # Após a corrida retornar, verificar se foi corrida do cinturão
                                    # Garantir que o progresso está salvo
                                    gerenciador_progresso.carregar()
                                    if hasattr(gerenciador_progresso, 'ultima_corrida_campanha') and gerenciador_progresso.ultima_corrida_campanha and gerenciador_progresso.ultima_corrida_campanha.startswith("cinturao_pista_"):
                                        from core.estatisticas import gerenciador_estatisticas
                                        gerenciador_estatisticas.carregar()
                                        stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(pista)
                                        melhor_tempo = stats_pista.get("melhor_tempo", None) if stats_pista else None
                                        melhor_posicao = stats_pista.get("melhor_posicao", None) if stats_pista else None
                                        
                                        if melhor_tempo is not None and melhor_posicao is not None:
                                            print(f"[CINTURÃO] Corrida completada na pista {pista}: posição={melhor_posicao}, tempo={melhor_tempo}")
                                            
                                            # Dar recompensa de dinheiro
                                            if recompensa > 0:
                                                gerenciador_progresso.adicionar_dinheiro(recompensa)
                                                print(f"[CINTURÃO] Recompensa de ${recompensa:,} adicionada!")
                                            
                                            # Desbloquear próxima corrida
                                            from core.fuligem import fuligem
                                            if indice_corrida == 0:  # Completou corrida 1, desbloquear corrida 2
                                                fuligem.desbloquear_corrida(1)
                                            elif indice_corrida == 1:  # Completou corrida 2, desbloquear corrida 3
                                                fuligem.desbloquear_corrida(2)
                                            
                                            # Avançar 8 horas no jogo
                                            from core.tempo_jogo import gerenciador_tempo
                                            gerenciador_tempo.avancar_horas(8.0)
                                            gerenciador_tempo.salvar()
                                            print(f"[CINTURÃO] 8 horas avançadas no jogo após completar corrida")
                                            
                                            # Limpar flag e salvar
                                            gerenciador_progresso.ultima_corrida_campanha = None
                                            gerenciador_progresso.salvar()
                                            
                            # Se houver uma cena narrativa pós-corrida, iniciá-la
                            # Por enquanto, apenas garantir que o salvamento está correto
                            # TODO: Adicionar cena narrativa ch2_10_post_cinturao_race quando disponível
                                    
                                    continue  # Voltar para o mapa após a corrida
                            
                            # Processar corrida do Circuito da Coroa (Autódromo)
                            elif atividade_tipo == "corrida_circuito_coroa":
                                parametros = atividade.get("parametros", {})
                                pista = parametros.get("pista")
                                voltas = parametros.get("voltas", 2)
                                dificuldade = parametros.get("dificuldade", "dificil")
                                race_id = parametros.get("race_id")
                                sem_bots = parametros.get("sem_bots", False)
                                
                                if pista and race_id:
                                    # Definir flag para verificar após a corrida
                                    gerenciador_progresso.ultima_corrida_campanha = race_id
                                    gerenciador_progresso.salvar()
                                    print(f"[AUTÓDROMO] Iniciando corrida {race_id} na pista {pista}")
                                    
                                    # Obter carro atual do jogador
                                    carro_p1_idx = 0
                                    if gerenciador_progresso.carro_p1_atual:
                                        from config import CARROS_DISPONIVEIS
                                        for i, carro in enumerate(CARROS_DISPONIVEIS):
                                            if carro.get("prefixo_cor") == gerenciador_progresso.carro_p1_atual:
                                                carro_p1_idx = i
                                                break
                                    
                                    # Modo de teste: marcar corrida como concluída automaticamente
                                    from config import MODO_TESTE_CORRIDAS
                                    if MODO_TESTE_CORRIDAS:
                                        print(f"[MODO TESTE] Corrida {race_id} marcada como concluída automaticamente")
                                        from core.estatisticas import gerenciador_estatisticas
                                        gerenciador_estatisticas.carregar()
                                        # Registrar corrida como concluída (posição 1, tempo fictício)
                                        gerenciador_estatisticas.registrar_corrida_completa(
                                            numero_pista=pista,
                                            posicao_final=1,
                                            tempo_final=60.0  # Tempo fictício
                                        )
                                        gerenciador_estatisticas.salvar()
                                        
                                        # Desbloquear corrida se necessário
                                        if not hasattr(gerenciador_progresso, 'corridas_desbloqueadas'):
                                            gerenciador_progresso.corridas_desbloqueadas = set()
                                        if isinstance(gerenciador_progresso.corridas_desbloqueadas, list):
                                            gerenciador_progresso.corridas_desbloqueadas = set(gerenciador_progresso.corridas_desbloqueadas)
                                        gerenciador_progresso.corridas_desbloqueadas.add(race_id)
                                        
                                        # Limpar flag e salvar
                                        gerenciador_progresso.ultima_corrida_campanha = None
                                        gerenciador_progresso.salvar()
                                        
                                        # Verificar se há cena narrativa pós-corrida
                                        cena_map = {
                                            "crown_stage1": "ch5_5_stage1_post",
                                            "crown_stage2": "ch5_6_stage2_post",
                                            "crown_stage3": "ch5_5_stage3_post",
                                            "crown_final": "ch5_7_post_final"
                                        }
                                        
                                        proxima_cena = cena_map.get(race_id)
                                        if proxima_cena:
                                            # Iniciar cena pós-corrida
                                            narrative_system._iniciar_cena_sem_transicao(proxima_cena)
                                            narrative_system.active = True
                                            gerenciador_progresso.ultima_corrida_campanha = None
                                            gerenciador_progresso.salvar()
                                            continue  # Voltar para o início do loop para executar narrativa
                                        else:
                                            continue  # Voltar para o mapa
                                    else:
                                        # Iniciar corrida normalmente
                                        from main import TipoJogo, ModoJogo
                                        import main
                                        
                                        main.principal(
                                            carro_selecionado_p1=carro_p1_idx,
                                            carro_selecionado_p2=0,
                                            mapa_selecionado=pista,
                                            modo_jogo=ModoJogo.UM_JOGADOR,
                                            tipo_jogo=TipoJogo.CORRIDA,
                                            voltas=voltas,
                                            dificuldade_ia=dificuldade,
                                            modo_arcade=False,
                                            sem_bots=sem_bots,
                                            race_id=race_id
                                        )
                                    
                                    # Após a corrida retornar, verificar se foi corrida do Circuito da Coroa
                                    gerenciador_progresso.carregar()
                                    if hasattr(gerenciador_progresso, 'ultima_corrida_campanha') and gerenciador_progresso.ultima_corrida_campanha and gerenciador_progresso.ultima_corrida_campanha.startswith("crown_"):
                                        from core.estatisticas import gerenciador_estatisticas
                                        gerenciador_estatisticas.carregar()
                                        stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(pista)
                                        melhor_tempo = stats_pista.get("melhor_tempo", None) if stats_pista else None
                                        melhor_posicao = stats_pista.get("melhor_posicao", None) if stats_pista else None
                                        
                                        if melhor_tempo is not None and melhor_posicao is not None:
                                            print(f"[AUTÓDROMO] Corrida {race_id} completada: posição={melhor_posicao}, tempo={melhor_tempo}")
                                            
                                            # Garantir que o capítulo 5 está ativo
                                            if not narrative_system.current_chapter_id or narrative_system.current_chapter_id != "ch5":
                                                print(f"[AUTÓDROMO] Definindo current_chapter_id para ch5 (atual: {narrative_system.current_chapter_id})")
                                                narrative_system.current_chapter_id = "ch5"
                                            
                                            # Determinar resultado (win se posição <= 2, lose caso contrário)
                                            resultado = "win" if melhor_posicao <= 2 else "lose"
                                            narrative_system.variables["lastRaceResult"] = resultado
                                            print(f"[AUTÓDROMO] Resultado da corrida: {resultado}, current_chapter_id: {narrative_system.current_chapter_id}")
                                            
                                            # Desbloquear próxima corrida sequencialmente
                                            if not hasattr(gerenciador_progresso, 'corridas_desbloqueadas'):
                                                gerenciador_progresso.corridas_desbloqueadas = set()
                                            if isinstance(gerenciador_progresso.corridas_desbloqueadas, list):
                                                gerenciador_progresso.corridas_desbloqueadas = set(gerenciador_progresso.corridas_desbloqueadas)
                                            
                                            # Inicializar rastreamento de vitórias se não existir
                                            if not hasattr(gerenciador_progresso, 'crown_stages_won'):
                                                gerenciador_progresso.crown_stages_won = set()
                                            if isinstance(gerenciador_progresso.crown_stages_won, list):
                                                gerenciador_progresso.crown_stages_won = set(gerenciador_progresso.crown_stages_won)
                                            
                                            # Desbloquear próxima etapa sequencialmente e rastrear vitórias
                                            if race_id == "crown_stage1":
                                                # Adicionar vitória se venceu (posição 1)
                                                if melhor_posicao == 1:
                                                    gerenciador_progresso.crown_stages_won.add("crown_stage1")
                                                    print(f"[AUTÓDROMO] Vitória na Etapa 1 registrada!")
                                                # Desbloquear etapa 2 após completar etapa 1 (independente de vitória)
                                                gerenciador_progresso.corridas_desbloqueadas.add("crown_stage2")
                                                gerenciador_progresso.salvar()
                                                print(f"[AUTÓDROMO] Etapa 2 desbloqueada após completar Etapa 1")
                                            elif race_id == "crown_stage2":
                                                # Adicionar vitória se venceu (posição 1)
                                                if melhor_posicao == 1:
                                                    gerenciador_progresso.crown_stages_won.add("crown_stage2")
                                                    print(f"[AUTÓDROMO] Vitória na Etapa 2 registrada!")
                                                # Desbloquear etapa 3 após completar etapa 2 (independente de vitória)
                                                gerenciador_progresso.corridas_desbloqueadas.add("crown_stage3")
                                                gerenciador_progresso.salvar()
                                                print(f"[AUTÓDROMO] Etapa 3 desbloqueada após completar Etapa 2")
                                            elif race_id == "crown_stage3":
                                                # Adicionar vitória se venceu (posição 1)
                                                if melhor_posicao == 1:
                                                    gerenciador_progresso.crown_stages_won.add("crown_stage3")
                                                    print(f"[AUTÓDROMO] Vitória na Etapa 3 registrada!")
                                                
                                                # Verificar se venceu todas as 3 etapas (posição 1 em todas)
                                                venceu_todas = (
                                                    "crown_stage1" in gerenciador_progresso.crown_stages_won and
                                                    "crown_stage2" in gerenciador_progresso.crown_stages_won and
                                                    "crown_stage3" in gerenciador_progresso.crown_stages_won
                                                )
                                                
                                                if venceu_todas:
                                                    gerenciador_progresso.corridas_desbloqueadas.add("crown_final")
                                                    gerenciador_progresso.salvar()
                                                    print(f"[AUTÓDROMO] Corrida final desbloqueada após vencer todas as 3 etapas!")
                                                    
                                                    # Ativar missão m19 quando todas as 3 etapas são completadas
                                                    try:
                                                        from core.missoes import gerenciador_missoes
                                                        # Forçar ativação mesmo que tenha activateOnSceneId
                                                        if gerenciador_missoes.ativar_missao("m19_jogo_do_rei", forcar_ativacao=True):
                                                            gerenciador_missoes.salvar()
                                                            print(f"[AUTÓDROMO] Missão m19_jogo_do_rei ativada após completar todas as 3 etapas!")
                                                        else:
                                                            print(f"[AUTÓDROMO] Não foi possível ativar missão m19_jogo_do_rei (já ativa ou completada?)")
                                                    except Exception as e:
                                                        print(f"[AUTÓDROMO] Erro ao ativar missão m19: {e}")
                                                        import traceback
                                                        traceback.print_exc()
                                                else:
                                                    gerenciador_progresso.salvar()
                                                    print(f"[AUTÓDROMO] Corrida final não desbloqueada. Vitórias registradas: {gerenciador_progresso.crown_stages_won}")
                                            
                                            # Verificar gatilhos de race_finished usando o sistema de triggers
                                            context = {
                                                "raceId": race_id,
                                                "raceResult": resultado
                                            }
                                            
                                            print(f"[AUTÓDROMO] Verificando gatilhos para raceId={race_id}, raceResult={resultado}")
                                            
                                            # Mapear corrida para cena pós-corrida
                                            cena_map = {
                                                "crown_stage1": "ch5_5_stage1_post",
                                                "crown_stage2": "ch5_6_stage2_post",
                                                "crown_stage3": "ch5_5_stage3_post",
                                                "crown_final": "ch5_7_post_final"
                                            }
                                            cena_id = cena_map.get(race_id)
                                            
                                            # Remover cena da lista de visitadas se já foi visitada (para permitir reativação)
                                            if cena_id and cena_id in narrative_system.scenes_visited:
                                                print(f"[AUTÓDROMO] Cena {cena_id} já foi visitada. Removendo da lista para permitir reativação...")
                                                narrative_system.scenes_visited.discard(cena_id)
                                            
                                            # Verificar gatilhos
                                            if narrative_system.verificar_gatilhos_pendentes(context):
                                                print(f"[AUTÓDROMO] Gatilho encontrado para corrida {race_id}, iniciando narrativa...")
                                                narrative_system.active = True
                                                gerenciador_progresso.ultima_corrida_campanha = None
                                                gerenciador_progresso.salvar()
                                                continue  # Voltar para o início do loop para executar narrativa
                                            else:
                                                print(f"[AUTÓDROMO] Nenhum gatilho encontrado para corrida {race_id}.")
                                                # Se não encontrou gatilho mas há uma cena mapeada, tentar iniciar diretamente
                                                if cena_id:
                                                    print(f"[AUTÓDROMO] Tentando iniciar cena {cena_id} diretamente...")
                                                    if narrative_system._iniciar_cena_sem_transicao(cena_id):
                                                        narrative_system.active = True
                                                        gerenciador_progresso.ultima_corrida_campanha = None
                                                        gerenciador_progresso.salvar()
                                                        continue
                                            
                                            # Limpar flag mesmo se não houver gatilho
                                            gerenciador_progresso.ultima_corrida_campanha = None
                                            gerenciador_progresso.salvar()
                                    
                                    continue  # Voltar para o mapa após a corrida
                            
                            # Processar corrida da Akira (Desafio de Montanha)
                            elif atividade_tipo == "desafio_touge":
                                print(f"[AKIRA] Processando corrida da Akira (desafio_touge)")
                                pista = atividade.get("pista", 3)
                                race_id = atividade.get("race_id", "mountain_test_run")
                                voltas = atividade.get("voltas", 1)
                                dificuldade = atividade.get("dificuldade", "medio")
                                sem_bots = atividade.get("sem_bots", False)
                                print(f"[AKIRA] Parâmetros da corrida: pista={pista}, race_id={race_id}, voltas={voltas}, dificuldade={dificuldade}, sem_bots={sem_bots}")
                                
                                # A flag já foi definida no hub_territorio, mas garantir que está salva
                                if race_id in ["mountain_test", "mountain_test_run"]:
                                    gerenciador_progresso.ultima_corrida_campanha = "mountain_test_run"
                                    gerenciador_progresso.salvar()
                                    print(f"[AKIRA] Flag de corrida definida: {gerenciador_progresso.ultima_corrida_campanha}")
                                
                                # Obter carro atual do jogador
                                carro_p1_idx = 0
                                if gerenciador_progresso.carro_p1_atual:
                                    from config import CARROS_DISPONIVEIS
                                    for i, carro in enumerate(CARROS_DISPONIVEIS):
                                        if carro.get("prefixo_cor") == gerenciador_progresso.carro_p1_atual:
                                            carro_p1_idx = i
                                            break
                                
                                # Modo de teste: marcar corrida como concluída automaticamente
                                from config import MODO_TESTE_CORRIDAS
                                if MODO_TESTE_CORRIDAS:
                                    print(f"[MODO TESTE] Corrida {race_id} marcada como concluída automaticamente")
                                    from core.estatisticas import gerenciador_estatisticas
                                    gerenciador_estatisticas.carregar()
                                    # Registrar corrida como concluída (posição 1, tempo fictício)
                                    gerenciador_estatisticas.registrar_corrida_completa(
                                        numero_pista=pista,
                                        posicao_final=1,
                                        tempo_final=60.0  # Tempo fictício
                                    )
                                    gerenciador_estatisticas.salvar()
                                    
                                    # Limpar flag e salvar
                                    gerenciador_progresso.ultima_corrida_campanha = None
                                    gerenciador_progresso.salvar()
                                    
                                    # Verificar se há cena narrativa pós-corrida
                                    if race_id in ["mountain_test", "mountain_test_run"]:
                                        # Iniciar cena pós-corrida da montanha
                                        narrative_system._iniciar_cena_sem_transicao("ch3_4_test_result")
                                        narrative_system.active = True
                                        gerenciador_progresso.ultima_corrida_campanha = None
                                        gerenciador_progresso.salvar()
                                        continue  # Voltar para o início do loop para executar narrativa
                                    
                                    continue  # Voltar para o mapa
                                else:
                                    # Iniciar corrida normalmente
                                    print(f"[AKIRA] Iniciando corrida: pista={pista}, race_id={race_id}, voltas={voltas}, dificuldade={dificuldade}")
                                    from main import TipoJogo, ModoJogo
                                    import main
                                    
                                    main.principal(
                                        carro_selecionado_p1=carro_p1_idx,
                                        carro_selecionado_p2=0,
                                        mapa_selecionado=pista,
                                        modo_jogo=ModoJogo.UM_JOGADOR,
                                        tipo_jogo=TipoJogo.CORRIDA,
                                        voltas=voltas,
                                        dificuldade_ia=dificuldade,
                                        modo_arcade=False,
                                        sem_bots=sem_bots
                                    )
                                    print(f"[AKIRA] Corrida retornou, verificando se foi completada...")
                                
                                # Após a corrida retornar, verificar se foi mountain_test ou mountain_test_run
                                gerenciador_progresso.carregar()
                                if hasattr(gerenciador_progresso, 'ultima_corrida_campanha') and gerenciador_progresso.ultima_corrida_campanha in ["mountain_test", "mountain_test_run"]:
                                    from core.estatisticas import gerenciador_estatisticas
                                    gerenciador_estatisticas.carregar()
                                    stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(pista)
                                    melhor_tempo = stats_pista.get("melhor_tempo", None) if stats_pista else None
                                    melhor_posicao = stats_pista.get("melhor_posicao", None) if stats_pista else None
                                    
                                    if melhor_tempo is not None and melhor_posicao is not None:
                                        print(f"[MONTANHA] Corrida completada na pista {pista}: posição={melhor_posicao}, tempo={melhor_tempo}")
                                        
                                        # Completar missão m13_teste_de_fluxo se estiver ativa
                                        from core.missoes import gerenciador_missoes
                                        if gerenciador_missoes.missao_ativa_id == "m13_teste_de_fluxo":
                                            gerenciador_missoes.completar_missao("m13_teste_de_fluxo")
                                            gerenciador_missoes.salvar()
                                        
                                        # Determinar resultado do teste (good se posição <= 2, bad caso contrário)
                                        resultado_teste = "good" if melhor_posicao <= 2 else "bad"
                                        narrative_system.variables["mountainTest"] = resultado_teste
                                        
                                        # Limpar flag e salvar
                                        gerenciador_progresso.ultima_corrida_campanha = None
                                        
                                        # Verificar se já completou todas as cenas do capítulo 3
                                        # Se sim, iniciar capítulo 4 após a narrativa pós-corrida
                                        capitulo_3_completo = gerenciador_progresso.capitulo_foi_completo("ch3")
                                        
                                        # Iniciar narrativa pós-teste (ch3_4_test_result)
                                        narrative_system._iniciar_cena_sem_transicao("ch3_4_test_result")
                                        narrative_system.active = True
                                        print(f"[MONTANHA] Narrativa ch3_4_test_result iniciada com resultado: {resultado_teste}")
                                        
                                        # Se o capítulo 3 já estava completo (todas as cenas foram vistas),
                                        # marcar para iniciar o capítulo 4 após a narrativa pós-corrida
                                        if capitulo_3_completo:
                                            # Definir flag para iniciar capítulo 4 após narrativa
                                            gerenciador_progresso.iniciar_capitulo_4_apos_narrativa = True
                                        
                                        gerenciador_progresso.salvar()
                                
                                continue  # Voltar para o mapa após a corrida (ou iniciar narrativa)
                            
                            # Outras atividades podem ser processadas aqui
                        
                        continue  # Voltar para o loop do mapa
            # Código de arcade removido - agora está no início do bloco Escolha.JOGAR
        # Removido: SELECIONAR_CARROS (oficina agora acessível via Campanha)
        if False:  # Placeholder
            # Abre tela de seleção de carros
            resultado = selecionar_carros_loop(screen)
            if resultado[0] is not None and resultado[1] is not None:
                carro_p1, carro_p2 = resultado
        # Removido: RECORDES (hierarquia removida do menu principal)
        if False:  # Placeholder
            # Abre tela de ranking (substituiu recordes)
            from core.menu_ranking import ranking_loop
            ranking_loop(screen)
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
