import os
import sys
import math
import pygame
from enum import Enum

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import LARGURA, ALTURA, FPS, CAMINHO_MENU, CONFIGURACOES, MAPAS_DISPONIVEIS
import main
from core.musica import gerenciador_musica
from core.popup_musica import popup_musica
from core.game_modes import ModoJogo, TipoJogo
from core.progresso import gerenciador_progresso
from core.gamepad_manager import gerenciador_gamepad

# Variável global para rastrear se o jogador tinha dinheiro suficiente antes (fora da oficina)
# Usado para mostrar notificação apenas quando há transição de "sem dinheiro" para "com dinheiro"
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

def desenhar_scrollbar(screen, scroll_offset, max_scroll, caixa_x, caixa_y, caixa_largura, caixa_altura, scroll_dragging=False):
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
                    # Verificar controles
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
            # Calcular proporção: manter altura de 35px (igual ao achievements) e ajustar largura proporcionalmente
            largura_original, altura_original = icon_concluida.get_size()
            altura_alvo = 35
            # Calcular largura proporcional
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
    
    # Calcular altura total necessária para todos os achievements
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
        # Verificar se o achievement está visível na área de scroll
        if y_atual + espacamento < area_scroll_y:
            y_atual += espacamento
            continue
        if y_atual > area_scroll_y + area_scroll_altura:
            break
        
        achievement_id = achievement['id']
        
        # Obter traduções
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
        
        # Calcular posição relativa na surface de scroll
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
        
        # Calcular posição e tamanho do thumb (indicador) da barra
        thumb_altura = max(30, int((altura_visivel / altura_total) * barra_altura))
        thumb_y = barra_y + int((_achievements_scroll_offset / scroll_max) * (barra_altura - thumb_altura)) if scroll_max > 0 else barra_y
        
        # Desenhar trilha da barra
        pygame.draw.rect(screen, (60, 60, 60), (barra_x, barra_y, barra_largura, barra_altura))
        pygame.draw.rect(screen, (100, 100, 100), (barra_x, barra_y, barra_largura, barra_altura), 1)
        
        # Desenhar thumb (indicador)
        cor_thumb = (180, 180, 180) if not _achievements_scroll_dragging else (220, 220, 220)
        pygame.draw.rect(screen, cor_thumb, (barra_x + 2, thumb_y, barra_largura - 4, thumb_altura))
        pygame.draw.rect(screen, (255, 255, 255), (barra_x + 2, thumb_y, barra_largura - 4, thumb_altura), 1)
    
    # Botão fechar
    fechar_rect = pygame.Rect(caixa_x + caixa_largura - 100, caixa_y + 20, 80, 40)
    mouse_x, mouse_y = pygame.mouse.get_pos()
    fechar_hover = fechar_rect.collidepoint(mouse_x, mouse_y)
    
    cor_fechar = (200, 50, 50) if fechar_hover else (150, 50, 50)
    pygame.draw.rect(screen, cor_fechar, fechar_rect)
    pygame.draw.rect(screen, (255, 255, 255), fechar_rect, 2)
    
    # Desenhar cursor do controle (caixa animada) para botão fechar
    if gerenciador_gamepad.obter_numero_controles() > 0:
        tamanho_cursor = 3 + int(2 * abs(math.sin(_achievements_animacao_cursor * math.pi)))
        cursor_rect = pygame.Rect(
            fechar_rect.x - tamanho_cursor,
            fechar_rect.y - tamanho_cursor,
            fechar_rect.width + tamanho_cursor * 2,
            fechar_rect.height + tamanho_cursor * 2
        )
        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
    
    fechar_texto = render_text("FECHAR", 18, (255, 255, 255), bold=True, pixel_style=True)
    fechar_x = fechar_rect.x + (fechar_rect.width - fechar_texto.get_width()) // 2
    fechar_y = fechar_rect.y + (fechar_rect.height - fechar_texto.get_height()) // 2
    screen.blit(fechar_texto, (fechar_x, fechar_y))
    
    # Instrução
    instrucao = render_text("ESC para fechar", 16, (150, 150, 150), bold=False, pixel_style=True)
    screen.blit(instrucao, (caixa_x + 20, caixa_y + caixa_altura - 30))

# Variáveis globais para animação do cursor nas telas
_estatisticas_animacao_cursor = 0.0
_desafios_animacao_cursor = 0.0

def desenhar_tela_estatisticas(screen, dt):
    """Desenha a tela de estatísticas detalhadas"""
    global _estatisticas_animacao_cursor
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
    
    titulo = render_text("ESTATÍSTICAS", 48, (100, 220, 255), bold=True, pixel_style=True)
    titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
    screen.blit(titulo, (titulo_x, caixa_y + 20))
    
    stats_gerais = gerenciador_estatisticas.obter_estatisticas_gerais()
    y_atual = caixa_y + 90
    
    secoes = [
        ("GERAIS", [
            ("Tempo Total Jogado", gerenciador_estatisticas.formatar_tempo(stats_gerais["tempo_total_jogado"])),
            ("Distância Total", gerenciador_estatisticas.formatar_distancia(stats_gerais["distancia_total"])),
            ("Corridas Completas", str(stats_gerais["corridas_completas"])),
            ("Corridas Vencidas", str(stats_gerais["corridas_vencidas"])),
            ("Voltas Completas", str(stats_gerais["voltas_completas"])),
            ("Colisões Totais", str(stats_gerais["colisoes_totais"])),
            ("Drifts Totais", str(stats_gerais["drifts_totais"])),
            ("Turbo Usado", str(stats_gerais["turbo_usado"])),
            ("Recordes Estabelecidos", str(stats_gerais["recordes_estabelecidos"])),
            ("Troféus Ganhos", str(stats_gerais["trofeus_ganhos"]))
        ])
    ]
    
    for secao_nome, itens in secoes:
        secao_titulo = render_text(secao_nome, 28, (150, 200, 255), bold=True, pixel_style=True)
        screen.blit(secao_titulo, (caixa_x + 30, y_atual))
        y_atual += 40
        
        for i, (nome, valor) in enumerate(itens):
            if y_atual > caixa_y + caixa_altura - 100:
                break
            nome_texto = render_text(nome, 18, (200, 200, 200), bold=False, pixel_style=True)
            valor_texto = render_text(str(valor), 18, (100, 220, 255), bold=True, pixel_style=True)
            screen.blit(nome_texto, (caixa_x + 50, y_atual))
            screen.blit(valor_texto, (caixa_x + caixa_largura - 250, y_atual))
            y_atual += 45
    
    botao_fechar_rect = pygame.Rect(caixa_x + caixa_largura - 120, caixa_y + 20, 100, 40)
    pygame.draw.rect(screen, (200, 50, 50), botao_fechar_rect)
    pygame.draw.rect(screen, (255, 100, 100), botao_fechar_rect, 2)
    fechar_texto = render_text("FECHAR", 18, (255, 255, 255), bold=True, pixel_style=True)
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
    
    titulo = render_text("DESAFIOS", 48, (100, 220, 255), bold=True, pixel_style=True)
    titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
    screen.blit(titulo, (titulo_x, caixa_y + 20))
    
    y_atual = caixa_y + 90
    
    desafios_diarios = gerenciador_desafios.obter_desafios_diarios()
    desafios_semanais = gerenciador_desafios.obter_desafios_semanais()
    
    if desafios_diarios:
        secao_titulo = render_text("DESAFIOS DIÁRIOS", 28, (150, 200, 255), bold=True, pixel_style=True)
        screen.blit(secao_titulo, (caixa_x + 30, y_atual))
        y_atual += 40
        
        for desafio in desafios_diarios:
            if y_atual > caixa_y + caixa_altura - 100:
                break
            progresso = gerenciador_desafios.obter_progresso(desafio["id"])
            porcentagem = min(100, int((progresso / desafio["objetivo"]) * 100))
            
            desc_texto = render_text(desafio["descricao"], 18, (200, 200, 200), bold=False, pixel_style=True)
            progresso_texto = render_text(f"{progresso}/{desafio['objetivo']} ({porcentagem}%)", 16, (100, 220, 255), bold=True, pixel_style=True)
            recompensa_texto = render_text(f"Recompensa: ${desafio['recompensa']}", 16, (150, 255, 150), bold=True, pixel_style=True)
            
            screen.blit(desc_texto, (caixa_x + 50, y_atual))
            screen.blit(progresso_texto, (caixa_x + 50, y_atual + 25))
            screen.blit(recompensa_texto, (caixa_x + caixa_largura - 250, y_atual))
            y_atual += 60
    
    if desafios_semanais:
        y_atual += 20
        secao_titulo = render_text("DESAFIOS SEMANAIS", 28, (200, 150, 255), bold=True, pixel_style=True)
        screen.blit(secao_titulo, (caixa_x + 30, y_atual))
        y_atual += 40
        
        for desafio in desafios_semanais:
            if y_atual > caixa_y + caixa_altura - 100:
                break
            progresso = gerenciador_desafios.obter_progresso(desafio["id"])
            porcentagem = min(100, int((progresso / desafio["objetivo"]) * 100))
            
            desc_texto = render_text(desafio["descricao"], 18, (200, 200, 200), bold=False, pixel_style=True)
            progresso_texto = render_text(f"{progresso}/{desafio['objetivo']} ({porcentagem}%)", 16, (100, 220, 255), bold=True, pixel_style=True)
            recompensa_texto = render_text(f"Recompensa: ${desafio['recompensa']}", 16, (200, 150, 255), bold=True, pixel_style=True)
            
            screen.blit(desc_texto, (caixa_x + 50, y_atual))
            screen.blit(progresso_texto, (caixa_x + 50, y_atual + 25))
            screen.blit(recompensa_texto, (caixa_x + caixa_largura - 250, y_atual))
            y_atual += 60
    
    botao_fechar_rect = pygame.Rect(caixa_x + caixa_largura - 120, caixa_y + 20, 100, 40)
    pygame.draw.rect(screen, (200, 50, 50), botao_fechar_rect)
    pygame.draw.rect(screen, (255, 100, 100), botao_fechar_rect, 2)
    fechar_texto = render_text("FECHAR", 18, (255, 255, 255), bold=True, pixel_style=True)
    fechar_x = botao_fechar_rect.x + (botao_fechar_rect.width - fechar_texto.get_width()) // 2
    fechar_y = botao_fechar_rect.y + (botao_fechar_rect.height - fechar_texto.get_height()) // 2
    screen.blit(fechar_texto, (fechar_x, fechar_y))
    
    return botao_fechar_rect

def menu_loop(screen) -> Escolha:
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)

    from core.i18n import t
    itens = [t("menu.principal.selecionar_carros"), t("menu.principal.jogar"), t("menu.principal.recordes"), t("menu.principal.opcoes"), t("menu.principal.sair")]
    idx = 1
    # Variável para rastrear se está navegando nos ícones superiores
    # None = nas opções do menu (idx 0-4), -1 = estatísticas, -2 = conquistas, -3 = missão diária
    icone_selecionado = None
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
            # Calcular proporção para manter aspecto original (ícone vertical 233x850)
            largura_original, altura_original = icon_exclamacao_raw.get_size()
            # Usar tamanho adequado para notificação (mantendo proporção)
            altura_alvo = 24  # Tamanho maior para ficar mais visível
            escala = altura_alvo / altura_original
            largura_alvo = int(largura_original * escala)
            icon_exclamacao_cache = pygame.transform.smoothscale(icon_exclamacao_raw, (largura_alvo, altura_alvo))
        except Exception as e:
            print(f"Erro ao carregar ícone de exclamação: {e}")

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
                        # Navegação entre opções do menu
                        navegacao_esquerda = {
                            0: 2, 1: 0, 2: None, 3: 1, 4: 3
                        }
                        novo_idx = navegacao_esquerda.get(idx)
                        if novo_idx is not None:
                            idx = novo_idx
                elif acao == "direita" and resultado_hold.get("fonte") == "hold":
                    if icone_selecionado is not None:
                        if icone_selecionado == -1:
                            icone_selecionado = -2
                        elif icone_selecionado == -2:
                            icone_selecionado = -3
                    else:
                        # Navegação entre opções do menu
                        navegacao_direita = {
                            0: 1, 1: 3, 2: 0, 3: 4, 4: None
                        }
                        novo_idx = navegacao_direita.get(idx)
                        if novo_idx is not None:
                            idx = novo_idx
        
        # Verificação contínua do D-pad REMOVIDA
        # O D-pad agora é processado apenas via eventos JOYBUTTONDOWN
        # Isso garante comportamento "por clique" - uma ação por pressionamento
        
        for ev in pygame.event.get():
            # Declarar todas as variáveis globais no início do loop de eventos
            global _achievements_scroll_offset, _achievements_scroll_dragging, _achievements_scroll_drag_start_y, _achievements_scroll_drag_start_offset
            
            # Processar eventos de controle nas telas abertas PRIMEIRO
            if tela_achievements_aberta and gerenciador_gamepad.obter_numero_controles() > 0:
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
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
                    elif acao == "confirmar" or acao == "cancelar":
                        # Fechar tela
                        tela_achievements_aberta = False
                        from core.achievements import gerenciador_achievements
                        gerenciador_achievements.marcar_todos_como_visualizados()
                        _achievements_scroll_offset = 0.0
                        icone_selecionado = None
                        continue
            elif tela_estatisticas_aberta and gerenciador_gamepad.obter_numero_controles() > 0:
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
                resultado_controle = processar_eventos_controle_menu(ev, 0, 0, joystick_id=0, tempo_atual=tempo_atual)
                if resultado_controle:
                    acao = resultado_controle.get("acao")
                    if acao == "confirmar" or acao == "cancelar":
                        # Fechar tela
                        tela_estatisticas_aberta = False
                        icone_selecionado = None
                        continue
            elif tela_desafios_aberta and gerenciador_gamepad.obter_numero_controles() > 0:
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
                resultado_controle = processar_eventos_controle_menu(ev, 0, 0, joystick_id=0, tempo_atual=tempo_atual)
                if resultado_controle:
                    acao = resultado_controle.get("acao")
                    if acao == "confirmar" or acao == "cancelar":
                        # Fechar tela
                        tela_desafios_aberta = False
                        icone_selecionado = None
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
                            # Processar tanto D-pad quanto analógico nas opções do menu
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
                            # Processar tanto D-pad quanto analógico nas opções do menu
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
                            # Se está nas opções do menu, retornar a escolha
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
                            icone_selecionado = None
                        elif tela_desafios_aberta:
                            tela_desafios_aberta = False
                            icone_selecionado = None
                        else:
                            # Se não está em nenhuma tela, sair do jogo
                            return Escolha.SAIR
                    # Se processou evento de controle, pular processamento de teclado
                    continue
            
            if ev.type == pygame.QUIT:
                return Escolha.SAIR
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
                    # Verificar clique no botão fechar da tela de achievements
                    fechar_rect = pygame.Rect((LARGURA - 800) // 2 + 800 - 100, (ALTURA - 600) // 2 + 20, 80, 40)
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
                    botao_fechar_estat = desenhar_tela_estatisticas(screen, dt)
                    if botao_fechar_estat.collidepoint(mouse_x, mouse_y):
                        tela_estatisticas_aberta = False
                        icone_selecionado = None  # Resetar seleção ao fechar tela
                elif tela_desafios_aberta:
                    botao_fechar_desafios = desenhar_tela_desafios(screen, dt)
                    if botao_fechar_desafios.collidepoint(mouse_x, mouse_y):
                        tela_desafios_aberta = False
                        icone_selecionado = None  # Resetar seleção ao fechar tela
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                if tela_achievements_aberta:
                    _achievements_scroll_dragging = False
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
                        
                        # Verificar clique no botão
                        clique_no_botao = botao_rect.collidepoint(mouse_x, mouse_y)
                        
                        # Se for o botão da oficina (i == 0) e houver ícone de exclamação, verificar clique no ícone também
                        if i == 0 and mostrar_notificacao_oficina and icon_exclamacao_cache is not None:
                            # Calcular posição do ícone de exclamação (mesma lógica do desenho)
                            pulso = 1.0 + 0.15 * math.sin(tempo_animacao_exclamacao * 4.0)
                            vibracao_x = 1.0 * math.sin(tempo_animacao_exclamacao * 4.0)
                            icon_exclamacao_largura, icon_exclamacao_altura = icon_exclamacao_cache.get_size()
                            largura_animada = int(icon_exclamacao_largura * pulso)
                            altura_animada = int(icon_exclamacao_altura * pulso)
                            exclamacao_x = x + largura - largura_animada - 5 + int(vibracao_x)
                            exclamacao_y = y - 8
                            exclamacao_rect = pygame.Rect(exclamacao_x, exclamacao_y, largura_animada, altura_animada)
                            clique_no_icone = exclamacao_rect.collidepoint(mouse_x, mouse_y)
                            if clique_no_botao or clique_no_icone:
                                return Escolha(i)
                        elif clique_no_botao:
                            return Escolha(i)

        # desenha
        screen.blit(bg, (0, 0))
        
        # Verificar hover dos botões de ícones (os retângulos já foram definidos antes do loop)
        botao_estatisticas_hover = botao_estatisticas_rect.collidepoint(mouse_x, mouse_y)
        botao_achievements_hover = botao_achievements_rect.collidepoint(mouse_x, mouse_y)
        botao_missao_hover = botao_missao_rect.collidepoint(mouse_x, mouse_y)
        
        # Contar missões diárias concluídas e selecionar ícone apropriado
        from core.desafios import gerenciador_desafios
        missoes_concluidas = gerenciador_desafios.contar_missoes_diarias_concluidas()
        icon_missao_atual = icon_missao_cache.get(missoes_concluidas, None)
        
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
        for i, txt in enumerate(itens):
            sel = (i == idx and icone_selecionado is None)  # Só selecionar se não estiver nos ícones
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
            
            # Desenhar notificação (ícone de exclamação) se for o botão da oficina e houver dinheiro suficiente
            # E se houver transição de "sem dinheiro" para "com dinheiro" (ou já tinha dinheiro antes)
            if i == 0 and mostrar_notificacao_oficina and icon_exclamacao_cache is not None:
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
            desenhar_tela_estatisticas(screen, dt)
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

def calcular_especificacoes_carro(carro_info, upgrades):
    """Calcula as especificações reais do carro baseadas nos upgrades e multiplicador_base"""
    import math
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
    
    # Calcular valores base (simulando CarroFisica)
    # Velocidade máxima base: o multiplicador_base não escala linearmente a velocidade real
    # devido ao atrito e arrasto. Vamos usar uma escala muito mais conservadora.
    # Primeiro carro (multiplicador_base = 1.00): V_TOP = 400 px/s
    # Último carro (multiplicador_base = 3.89): V_TOP deve ser limitado
    # Escala muito reduzida: usar apenas 8% do aumento do multiplicador
    V_TOP_base = 400.0 * (1.0 + (multiplicador_base - 1.0) * 0.08)  # Escala muito reduzida
    # Aplicar upgrades de motor e transmissão (mesma lógica de aplicar_upgrades)
    # Motor aumenta V_TOP em +10% por nível (reduzido)
    V_TOP = V_TOP_base * (1.0 + nivel_motor * 0.10)
    # Transmissão aumenta V_TOP em +6% por nível (reduzido, multiplicativo)
    V_TOP *= (1.0 + nivel_transmissao * 0.06)
    
    # Força do motor base
    engine_force_base = 80000.0 * multiplicador_base
    # Aplicar upgrades
    mult_motor = 1.0 + (nivel_motor * 0.25)
    mult_filtro = 1.0 + (nivel_filtro_ar * 0.12)
    mult_ecu = 1.0 + (nivel_ecu * 0.10)
    mult_trans = 1.0 + (nivel_transmissao * 0.08)
    engine_force = engine_force_base * mult_motor * mult_filtro * mult_ecu * mult_trans
    
    # Grip base
    Cf_base = (35000.0 if tipo_tracao != "rear" else 34000.0) * multiplicador_base
    mult_rodas = 1.0 + (nivel_rodas * 0.18)
    Cf = Cf_base * mult_rodas
    
    # Estabilidade base
    stability_k_base = 0.043
    mult_rodas_stab = 1.0 + (nivel_rodas * 0.10)
    mult_susp_stab = 1.0 + (nivel_suspensao * 0.12)
    stability_k = stability_k_base * mult_rodas_stab * mult_susp_stab
    
    # Frenagem base
    brake_force_base = 5500.0 * multiplicador_base
    # Frenagem não tem upgrade direto, mas melhora com estabilidade
    
    # Calcular velocidade máxima real considerando atrito e arrasto
    # OBSERVAÇÃO: Velocidade base observada ~140 km/h para primeiro carro
    # Último carro (multiplicador_base = 3.89) com upgrades máximos: máximo 380 km/h
    # Cálculo baseado na velocidade real observada:
    # - Primeiro carro (multiplicador_base = 1.00): ~140 km/h base, ~220 km/h com upgrades máximos
    # - Último carro (multiplicador_base = 3.89): ~200 km/h base, ~380 km/h com upgrades máximos
    
    # Fator de eficiência base: varia com multiplicador_base
    # Primeiro carro: 14% de V_TOP (140 km/h)
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
    PXPS_TO_KMH = 1.0  # Mesma conversão do HUD
    vel_max_kmh = vel_max_pxps * ARCADE_SPEED_MULT * PXPS_TO_KMH
    
    # LIMITE HARD: garantir que nenhum carro ultrapasse 380 km/h
    vel_max_kmh = min(380.0, vel_max_kmh)
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
            for tipo_upgrade in upgrades_tipos:
                nivel_atual = gerenciador_progresso.obter_upgrade(prefixo_cor, tipo_upgrade)
                if nivel_atual < 5:
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
    for tipo_upgrade in upgrades_tipos:
        nivel_atual = gerenciador_progresso.obter_upgrade(prefixo_cor, tipo_upgrade)
        if nivel_atual < 5:  # Ainda há níveis disponíveis
            preco = gerenciador_progresso.calcular_preco_upgrade(tipo_upgrade, nivel_atual)
            if gerenciador_progresso.tem_dinheiro(preco):
                return True  # Encontrou pelo menos um upgrade disponível
    
    return False  # Não há upgrades disponíveis ou não tem dinheiro suficiente

def selecionar_carros_loop(screen):
    global _tinha_dinheiro_anterior
    from core.crank import crank
    
    # Verificar se deve mostrar tutorial do Crank (primeira vez na oficina)
    if not crank.tutorial_mostrado and not crank.ativo:
        crank.mostrar_tutorial()
    
    # Verificar se deve mostrar diálogo raro sobre compras do mercador alien (chance rara)
    if crank.tutorial_mostrado and not crank.ativo:
        crank.verificar_aparecer_dialogo_alien()
    
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
    
    from config import CAMINHO_OFICINA, DIR_SPRITES, DIR_CAR_SELECTION
    bg_raw = pygame.image.load(CAMINHO_OFICINA).convert_alpha()
    # Usar scale simples (como no editor) para mostrar a imagem completa sem cortar
    bg = pygame.transform.scale(bg_raw, (LARGURA, ALTURA))
    
    # Importar a lista de carros do main
    from main import CARROS_DISPONIVEIS
    
    carro_p1_atual_salvo = gerenciador_progresso.obter_carro_atual(1)
    if carro_p1_atual_salvo is not None and 0 <= carro_p1_atual_salvo < len(CARROS_DISPONIVEIS):
        carro_p1 = carro_p1_atual_salvo
    else:
        carros_desbloqueados = [i for i, carro in enumerate(CARROS_DISPONIVEIS) if gerenciador_progresso.esta_desbloqueado(carro['prefixo_cor'])]
        if carros_desbloqueados:
            carro_p1 = carros_desbloqueados[0]
        else:
            carro_p1 = 0
    
    carro_p2_atual_salvo = gerenciador_progresso.obter_carro_atual(2)
    if carro_p2_atual_salvo is not None and 0 <= carro_p2_atual_salvo < len(CARROS_DISPONIVEIS):
        carro_p2 = carro_p2_atual_salvo
    else:
        carro_p2 = 1 if len(CARROS_DISPONIVEIS) > 1 else 0
    
    fase_selecao = 1
    modo_dois_jogadores = False
    carro_atual_p1_prefixo = CARROS_DISPONIVEIS[carro_p1]['prefixo_cor']
    carro_atual_p2_prefixo = CARROS_DISPONIVEIS[carro_p2]['prefixo_cor']
    carro_selecionado_p1 = (gerenciador_progresso.obter_carro_atual(1) == carro_p1)
    carro_selecionado_p2 = (gerenciador_progresso.obter_carro_atual(2) == carro_p2)
    
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
    
    # Variáveis para cursor do controle (indicador visual)
    botao_selecionado_controle = None  # Qual botão está selecionado pelo controle
    animacao_cursor = 0.0  # Animação do cursor (0.0 a 1.0)
    velocidade_animacao_cursor = 3.0  # Velocidade da animação
    
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
                carro_atual_p1 = CARROS_DISPONIVEIS[carro_p1]
                esta_desbloqueado_p1 = gerenciador_progresso.esta_desbloqueado(carro_atual_p1['prefixo_cor'])
            info_x_p1 = LARGURA - 300
            info_y_p1 = 180
            info_altura_p1 = 320  # Ajustar altura para refletir o tamanho real das especificações
            botao_y_p1 = info_y_p1 + info_altura_p1 + 20
            botao_largura_p1 = 130
            botao_altura_p1 = 45
            espacamento_botoes_p1 = 10
            info_largura_p1 = 280
            botao_largura_p1 = 80  # Reduzir largura para caber botões
            num_botoes = 3  # Sempre 3 botões: COMPRAR/USAR, UPGRADE, VENDER
            # Mover botões mais para a esquerda
            largura_total_botoes = botao_largura_p1 * num_botoes + espacamento_botoes_p1 * (num_botoes - 1)
            offset_esquerda = -30  # Mover para a esquerda
            botoes_x_inicial_p1 = info_x_p1 + (info_largura_p1 - largura_total_botoes) // 2 + offset_esquerda
            # Garantir que não saia da caixa pela esquerda
            if botoes_x_inicial_p1 < info_x_p1:
                botoes_x_inicial_p1 = info_x_p1 + 5
            
            if esta_desbloqueado_p1:
                botao_usar_rect_p1 = pygame.Rect(botoes_x_inicial_p1, botao_y_p1, botao_largura_p1, botao_altura_p1)
                botao_upgrade_rect_p1 = pygame.Rect(botoes_x_inicial_p1 + botao_largura_p1 + espacamento_botoes_p1, botao_y_p1, botao_largura_p1, botao_altura_p1)
                botao_vender_rect_p1 = pygame.Rect(botoes_x_inicial_p1 + (botao_largura_p1 + espacamento_botoes_p1) * 2, botao_y_p1, botao_largura_p1, botao_altura_p1)
                # Botão "2 jogadores" removido (não aparece mais ao lado de vender)
                botao_dois_jogadores_rect_p1 = None
                
                # Botão "Concluído" sempre aparece abaixo dos outros botões (esticado para centralizar)
                botao_concluido_y_p1 = botao_y_p1 + botao_altura_p1 + 15
                # Esticar o botão para ficar centralizado abaixo dos 3 botões acima
                largura_total_botoes_acima = botao_largura_p1 * 3 + espacamento_botoes_p1 * 2
                botao_concluido_largura_p1 = largura_total_botoes_acima  # Mesma largura dos 3 botões acima
                # Centralizar o botão em relação aos 3 botões acima
                botao_concluido_x_p1 = botoes_x_inicial_p1  # Alinhar com o primeiro botão
                botao_concluido_rect_p1 = pygame.Rect(botao_concluido_x_p1, botao_concluido_y_p1, botao_concluido_largura_p1, botao_altura_p1)
            else:
                # Mesmo quando carro não é possuído, mostrar os 3 botões (COMPRAR, UPGRADE, VENDER)
                botao_comprar_rect_p1 = pygame.Rect(botoes_x_inicial_p1, botao_y_p1, botao_largura_p1, botao_altura_p1)
                botao_upgrade_rect_p1 = pygame.Rect(botoes_x_inicial_p1 + botao_largura_p1 + espacamento_botoes_p1, botao_y_p1, botao_largura_p1, botao_altura_p1)
                botao_vender_rect_p1 = pygame.Rect(botoes_x_inicial_p1 + (botao_largura_p1 + espacamento_botoes_p1) * 2, botao_y_p1, botao_largura_p1, botao_altura_p1)
                botao_dois_jogadores_rect_p1 = None
                # Botão "Concluído" sempre aparece, mesmo quando carro não é possuído (esticado para centralizar)
                botao_concluido_y_p1 = botao_y_p1 + botao_altura_p1 + 15
                # Esticar o botão para ficar centralizado abaixo dos 3 botões acima
                largura_total_botoes_acima = botao_largura_p1 * 3 + espacamento_botoes_p1 * 2
                botao_concluido_largura_p1 = largura_total_botoes_acima  # Mesma largura dos 3 botões acima
                # Centralizar o botão em relação aos 3 botões acima
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
            info_altura_p2 = 320  # Ajustar altura para refletir o tamanho real das especificações
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
            if resultado_crank == "fechado":
                crank.fechar()
            # Filtrar eventos de mouse e teclado que o Crank processa
            eventos = [ev for ev in eventos if not (ev.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN) and crank.ativo)]
        
        for ev in eventos:
            if ev.type == pygame.QUIT:
                return None, None
            
            # Processar eventos de controle ANTES de outros eventos
            if gerenciador_gamepad.obter_numero_controles() > 0:
                from core.menu_controles import processar_eventos_controle_menu
                tempo_atual = pygame.time.get_ticks()
                # Criar uma lista de opções para navegação (carros)
                num_carros = len(CARROS_DISPONIVEIS)
                carro_atual_idx = carro_p1 if fase_selecao == 1 else carro_p2
                
                # Passar 0 como num_opcoes para evitar que esquerda/direita do D-pad sejam processadas como navegação de carros
                # Apenas L1/R1 devem trocar carros
                # Para navegação de carros, passar 0 (apenas L1/R1)
                # Para navegação de opções (usar, upgrade, vender, concluído), passar número de opções
                # Determinar opções disponíveis baseado no estado do carro
                if fase_selecao == 1:
                    carro_atual = CARROS_DISPONIVEIS[carro_p1]
                    esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                else:
                    carro_atual = CARROS_DISPONIVEIS[carro_p2]
                    esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                
                # Opções disponíveis: 
                # Linha superior: voltar, dois_jogadores (2 opções)
                # Linha inferior: usar/comprar, upgrade, vender, concluído (4 opções)
                num_opcoes_botoes_superior = 2  # voltar, dois_jogadores
                num_opcoes_botoes_inferior = 4  # usar/comprar, upgrade, vender, concluído
                
                # Determinar em qual linha estamos
                linha_atual = "inferior"  # ou "superior"
                opcao_botao_atual = 0
                if botao_selecionado_controle:
                    if botao_selecionado_controle == "voltar":
                        linha_atual = "superior"
                        opcao_botao_atual = 0
                    elif botao_selecionado_controle == "dois_jogadores":
                        linha_atual = "superior"
                        opcao_botao_atual = 1
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
                
                # Processar eventos: uma chamada para cima/baixo (0 opções) e outra para esquerda/direita
                num_opcoes_horizontal = num_opcoes_botoes_superior if linha_atual == "superior" else num_opcoes_botoes_inferior
                resultado_controle_vertical = processar_eventos_controle_menu(ev, opcao_botao_atual, 0, joystick_id=0, tempo_atual=tempo_atual)
                resultado_controle_horizontal = processar_eventos_controle_menu(ev, opcao_botao_atual, num_opcoes_horizontal, joystick_id=0, tempo_atual=tempo_atual)
                
                # Priorizar resultado vertical (cima/baixo) se existir, senão usar horizontal (esquerda/direita)
                if resultado_controle_vertical and resultado_controle_vertical.get("acao") in ("cima", "baixo"):
                    resultado_controle = resultado_controle_vertical
                elif resultado_controle_horizontal and resultado_controle_horizontal.get("acao") in ("esquerda", "direita"):
                    resultado_controle = resultado_controle_horizontal
                else:
                    resultado_controle = resultado_controle_vertical or resultado_controle_horizontal
                controle_processado = False
                if resultado_controle:
                    controle_processado = True
                    acao = resultado_controle.get("acao")
                    # Processar ações de carro (L1/R1) - processar sempre, mesmo durante transição
                    if acao == "carro_anterior" or acao == "carro_proximo":
                        # Processar mesmo durante transição (permitir mudança rápida)
                        if acao == "carro_anterior":
                            # Navegar para carro anterior (L1) - ir para esquerda (carro anterior)
                            if fase_selecao == 1:
                                iniciar_transicao(-1, carro_p1)
                                carro_p1 = (carro_p1 - 1) % num_carros
                                carro_selecionado_p1 = (gerenciador_progresso.obter_carro_atual(1) == carro_p1)
                                botao_selecionado_controle = None
                            else:
                                iniciar_transicao(-1, carro_p2)
                                carro_p2 = (carro_p2 - 1) % num_carros
                                carro_selecionado_p2 = (gerenciador_progresso.obter_carro_atual(2) == carro_p2)
                                botao_selecionado_controle = None
                        elif acao == "carro_proximo":
                            # Navegar para próximo carro (R1) - ir para direita (próximo carro)
                            if fase_selecao == 1:
                                iniciar_transicao(1, carro_p1)
                                carro_p1 = (carro_p1 + 1) % num_carros
                                carro_selecionado_p1 = (gerenciador_progresso.obter_carro_atual(1) == carro_p1)
                                botao_selecionado_controle = None
                            else:
                                iniciar_transicao(1, carro_p2)
                                carro_p2 = (carro_p2 + 1) % num_carros
                                carro_selecionado_p2 = (gerenciador_progresso.obter_carro_atual(2) == carro_p2)
                                botao_selecionado_controle = None
                        continue
                    
                    if not transicao_ativa:
                        if acao == "cima" or acao == "baixo":
                            # Navegar entre botões (cima/baixo) - apenas setinhas
                            if resultado_controle.get("fonte") == "dpad":
                                if fase_selecao == 1:
                                    carro_atual = CARROS_DISPONIVEIS[carro_p1]
                                    esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                    if esta_desbloqueado:
                                        # Navegação vertical: qualquer botão (baixo) → concluído, concluído (baixo) → voltar
                                        if botao_selecionado_controle is None:
                                            botao_selecionado_controle = "usar"
                                        elif botao_selecionado_controle == "usar":
                                            botao_selecionado_controle = "concluido" if acao == "baixo" else "voltar"
                                        elif botao_selecionado_controle == "upgrade":
                                            botao_selecionado_controle = "concluido" if acao == "baixo" else "voltar"
                                        elif botao_selecionado_controle == "vender":
                                            botao_selecionado_controle = "concluido" if acao == "baixo" else "voltar"
                                        elif botao_selecionado_controle == "concluido":
                                            botao_selecionado_controle = "voltar" if acao == "baixo" else "usar"
                                        elif botao_selecionado_controle == "voltar":
                                            botao_selecionado_controle = "concluido" if acao == "baixo" else "concluido"
                                        elif botao_selecionado_controle == "dois_jogadores":
                                            botao_selecionado_controle = "concluido" if acao == "baixo" else "concluido"
                                    else:
                                        # Navegação vertical: qualquer botão (baixo) → concluído, concluído (baixo) → voltar
                                        if botao_selecionado_controle is None:
                                            botao_selecionado_controle = "comprar"
                                        elif botao_selecionado_controle == "comprar":
                                            botao_selecionado_controle = "concluido" if acao == "baixo" else "voltar"
                                        elif botao_selecionado_controle == "upgrade":
                                            botao_selecionado_controle = "concluido" if acao == "baixo" else "voltar"
                                        elif botao_selecionado_controle == "vender":
                                            botao_selecionado_controle = "concluido" if acao == "baixo" else "voltar"
                                        elif botao_selecionado_controle == "concluido":
                                            botao_selecionado_controle = "voltar" if acao == "baixo" else "comprar"
                                        elif botao_selecionado_controle == "voltar":
                                            botao_selecionado_controle = "concluido" if acao == "baixo" else "concluido"
                                        elif botao_selecionado_controle == "dois_jogadores":
                                            botao_selecionado_controle = "concluido" if acao == "baixo" else "concluido"
                                else:
                                    # Fase 2 (P2) - mesma lógica
                                    carro_atual = CARROS_DISPONIVEIS[carro_p2]
                                    esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                    if esta_desbloqueado:
                                        # Navegação vertical: qualquer botão (baixo) → concluído, concluído (baixo) → voltar
                                        if botao_selecionado_controle is None:
                                            botao_selecionado_controle = "usar"
                                        elif botao_selecionado_controle == "usar":
                                            botao_selecionado_controle = "concluido" if acao == "baixo" else "voltar"
                                        elif botao_selecionado_controle == "upgrade":
                                            botao_selecionado_controle = "concluido" if acao == "baixo" else "voltar"
                                        elif botao_selecionado_controle == "vender":
                                            botao_selecionado_controle = "concluido" if acao == "baixo" else "voltar"
                                        elif botao_selecionado_controle == "concluido":
                                            botao_selecionado_controle = "voltar" if acao == "baixo" else "usar"
                                        elif botao_selecionado_controle == "voltar":
                                            botao_selecionado_controle = "concluido" if acao == "baixo" else "concluido"
                                        elif botao_selecionado_controle == "dois_jogadores":
                                            botao_selecionado_controle = "concluido" if acao == "baixo" else "concluido"
                                    else:
                                        # Navegação vertical: qualquer botão (baixo) → concluído, concluído (baixo) → voltar
                                        if botao_selecionado_controle is None:
                                            botao_selecionado_controle = "comprar"
                                        elif botao_selecionado_controle == "comprar":
                                            botao_selecionado_controle = "concluido" if acao == "baixo" else "voltar"
                                        elif botao_selecionado_controle == "upgrade":
                                            botao_selecionado_controle = "concluido" if acao == "baixo" else "voltar"
                                        elif botao_selecionado_controle == "vender":
                                            botao_selecionado_controle = "concluido" if acao == "baixo" else "voltar"
                                        elif botao_selecionado_controle == "concluido":
                                            botao_selecionado_controle = "voltar" if acao == "baixo" else "comprar"
                                        elif botao_selecionado_controle == "voltar":
                                            botao_selecionado_controle = "concluido" if acao == "baixo" else "concluido"
                                        elif botao_selecionado_controle == "dois_jogadores":
                                            botao_selecionado_controle = "concluido" if acao == "baixo" else "concluido"
                        elif acao == "esquerda" or acao == "direita":
                            # Navegação horizontal entre opções
                            if resultado_controle.get("fonte") == "dpad":
                                # Determinar linha atual
                                linha_atual = "inferior"
                                if botao_selecionado_controle in ("voltar", "dois_jogadores"):
                                    linha_atual = "superior"
                                
                                if linha_atual == "superior":
                                    # Navegação horizontal na linha superior: voltar ↔ dois_jogadores
                                    if "opcao" in resultado_controle:
                                        opcao_idx = resultado_controle["opcao"]
                                    else:
                                        if botao_selecionado_controle == "voltar":
                                            opcao_idx = 0
                                        elif botao_selecionado_controle == "dois_jogadores":
                                            opcao_idx = 1
                                        else:
                                            opcao_idx = 0
                                        
                                        if acao == "esquerda":
                                            opcao_idx = (opcao_idx - 1) % 2
                                        else:  # direita
                                            opcao_idx = (opcao_idx + 1) % 2
                                    
                                    opcoes_superior = ["voltar", "dois_jogadores"]
                                    botao_selecionado_controle = opcoes_superior[opcao_idx]
                                else:
                                    # Navegação horizontal na linha inferior: usar/comprar ↔ upgrade ↔ vender ↔ concluído
                                    if fase_selecao == 1:
                                        carro_atual = CARROS_DISPONIVEIS[carro_p1]
                                        esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                    else:
                                        carro_atual = CARROS_DISPONIVEIS[carro_p2]
                                        esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                    
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
                                        
                                        if acao == "esquerda":
                                            opcao_idx = (opcao_idx - 1) % 4
                                        else:  # direita
                                            opcao_idx = (opcao_idx + 1) % 4
                                    
                                    # Mapear índice de volta para botão
                                    if esta_desbloqueado:
                                        opcoes = ["usar", "upgrade", "vender", "concluido"]
                                    else:
                                        opcoes = ["comprar", "upgrade", "vender", "concluido"]
                                    
                                    botao_selecionado_controle = opcoes[opcao_idx]
                        elif acao == "confirmar":
                            # Confirmar ação baseada no botão atual
                            if fase_selecao == 1:
                                carro_atual = CARROS_DISPONIVEIS[carro_p1]
                                esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                if esta_desbloqueado:
                                    # Verificar qual botão está selecionado
                                    if botao_selecionado_controle == "usar":
                                        if not carro_selecionado_p1:
                                            carro_selecionado_p1 = True
                                    elif botao_selecionado_controle == "upgrade":
                                        # Abrir tela de upgrades
                                        if botao_upgrade_rect_p1:
                                            pode_upgrade = (carro_atual['prefixo_cor'] == "Car1") or esta_desbloqueado
                                            if pode_upgrade and fundo_sem_textos:
                                                if tela_upgrades(screen, carro_atual['prefixo_cor'], carro_atual['nome'], fundo_sem_textos):
                                                    pass  # Volta para seleção de carros
                                            elif not pode_upgrade:
                                                from core.i18n import t
                                                popup_musica.mostrar(t("mensagens.comprar_carro_primeiro"), tipo="outra")
                                    elif botao_selecionado_controle == "vender":
                                        # Vender carro
                                        if botao_vender_rect_p1:
                                            pode_vender = gerenciador_progresso.contar_carros_desbloqueados() > 1
                                            if pode_vender:
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
                                    elif botao_selecionado_controle == "concluido":
                                        # Confirmar seleção
                                        if botao_concluido_rect_p1:
                                            if modo_dois_jogadores:
                                                if carro_selecionado_p1:
                                                    fase_selecao = 2
                                            else:
                                                if carro_selecionado_p1:
                                                    gerenciador_progresso.definir_carro_atual(carro_p1=carro_p1)
                                                    return carro_p1, carro_p2
                                    elif botao_selecionado_controle == "voltar":
                                        # Voltar para o menu
                                        if modo_dois_jogadores:
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
                                    elif botao_selecionado_controle == "dois_jogadores":
                                        # Alternar modo 2 jogadores
                                        if modo_dois_jogadores:
                                            # Voltar para modo single player
                                            modo_dois_jogadores = False
                                            carro_selecionado_p1 = False  # Resetar seleção
                                            carro_selecionado_p2 = False  # Resetar seleção
                                        else:
                                            # Ativar modo 2 jogadores (não seleciona carro automaticamente)
                                            modo_dois_jogadores = True
                                else:
                                    # Carro não desbloqueado
                                    if botao_selecionado_controle == "comprar":
                                        # Tentar comprar
                                        if botao_comprar_rect_p1:
                                            preco = carro_atual.get('preco', 0)
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
                                carro_atual = CARROS_DISPONIVEIS[carro_p2]
                                esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                                if esta_desbloqueado:
                                    # Verificar qual botão está selecionado
                                    if botao_selecionado_controle == "usar":
                                        if not carro_selecionado_p2:
                                            carro_selecionado_p2 = True
                                    elif botao_selecionado_controle == "upgrade":
                                        # Abrir tela de upgrades
                                        if botao_upgrade_rect_p2:
                                            tela_upgrades_aberta = True
                                            carro_upgrade_atual = carro_p2
                                    elif botao_selecionado_controle == "vender":
                                        # Vender carro
                                        if botao_vender_rect_p2:
                                            pode_vender = gerenciador_progresso.contar_carros_desbloqueados() > 1
                                            if pode_vender:
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
                                    elif botao_selecionado_controle == "concluido":
                                        # Confirmar seleção
                                        if botao_concluido_rect_p2:
                                            if carro_selecionado_p2:
                                                gerenciador_progresso.definir_carro_atual(carro_p1=carro_p1, carro_p2=carro_p2)
                                                return carro_p1, carro_p2
                                    elif botao_selecionado_controle == "voltar":
                                        # Voltar para o menu
                                        if carro_selecionado_p2:
                                            gerenciador_progresso.definir_carro_atual(carro_p1=carro_p1, carro_p2=carro_p2)
                                            return carro_p1, carro_p2
                                        else:
                                            return None, None
                                else:
                                    # Carro não desbloqueado
                                    if botao_selecionado_controle == "comprar":
                                        # Tentar comprar
                                        if botao_comprar_rect_p2:
                                            preco = carro_atual.get('preco', 0)
                                            if gerenciador_progresso.comprar_carro(carro_atual['prefixo_cor'], preco):
                                                from core.i18n import t
                                                popup_musica.mostrar(t("mensagens.carro_comprado").format(carro_atual['nome']), tipo="outra")
                                            else:
                                                from core.i18n import t
                                                popup_musica.mostrar(t("mensagens.dinheiro_insuficiente"), tipo="outra")
                                    elif botao_selecionado_controle == "upgrade":
                                        # Abrir tela de upgrades
                                        if botao_upgrade_rect_p2:
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
                # Verificar clique no botão "Voltar"
                if botao_voltar_rect.collidepoint(ev.pos[0], ev.pos[1]):
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
                
                # Verificar clique no botão "2 jogadores" / "1 jogador" (menu superior)
                if fase_selecao == 1 and botao_dois_jogadores_menu_rect.collidepoint(ev.pos[0], ev.pos[1]):
                    if modo_dois_jogadores:
                        # Voltar para modo single player
                        modo_dois_jogadores = False
                        carro_selecionado_p1 = False  # Resetar seleção
                        carro_selecionado_p2 = False  # Resetar seleção
                    else:
                        # Ativar modo 2 jogadores (não seleciona carro automaticamente)
                        modo_dois_jogadores = True
                    continue
                # Verificar clique nos botões
                if not transicao_ativa:
                    mouse_x, mouse_y = ev.pos
                    
                    if fase_selecao == 1:
                        carro_atual = CARROS_DISPONIVEIS[carro_p1]
                        esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                        
                        if esta_desbloqueado:
                            # Verificar clique no botão USAR (apenas seleciona o carro, se não estiver já selecionado)
                            if botao_usar_rect_p1 and botao_usar_rect_p1.collidepoint(mouse_x, mouse_y) and not carro_selecionado_p1:
                                carro_selecionado_p1 = True
                            # Verificar clique no botão "Concluído"
                            elif botao_concluido_rect_p1 and botao_concluido_rect_p1.collidepoint(mouse_x, mouse_y):
                                if modo_dois_jogadores:
                                    # P1 confirmou, vai para P2 (apenas se carro foi selecionado)
                                    if carro_selecionado_p1:
                                        fase_selecao = 2
                                else:
                                    if carro_selecionado_p1:
                                        gerenciador_progresso.definir_carro_atual(carro_p1=carro_p1)
                                        return carro_p1, carro_p2
                            # Botão "2 JOGADORES" lateral removido (não existe mais)
                            # Verificar clique no botão UPGRADE
                            elif botao_upgrade_rect_p1 and botao_upgrade_rect_p1.collidepoint(mouse_x, mouse_y):
                                # Verificar se carro está desbloqueado (Car1 sempre desbloqueado)
                                pode_upgrade = (carro_atual['prefixo_cor'] == "Car1") or esta_desbloqueado
                                if pode_upgrade and fundo_sem_textos:
                                    if tela_upgrades(screen, carro_atual['prefixo_cor'], carro_atual['nome'], fundo_sem_textos):
                                        pass  # Volta para seleção de carros
                                elif not pode_upgrade:
                                    from core.i18n import t
                                    popup_musica.mostrar(t("mensagens.comprar_carro_primeiro"), tipo="outra")
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
                        
                        if esta_desbloqueado:
                            # Verificar clique no botão USAR (apenas seleciona o carro, se não estiver já selecionado)
                            if botao_usar_rect_p2 and botao_usar_rect_p2.collidepoint(mouse_x, mouse_y) and not carro_selecionado_p2:
                                carro_selecionado_p2 = True
                            # Verificar clique no botão "Concluído"
                            elif botao_concluido_rect_p2 and botao_concluido_rect_p2.collidepoint(mouse_x, mouse_y):
                                if carro_selecionado_p2:
                                    gerenciador_progresso.definir_carro_atual(carro_p1=carro_p1, carro_p2=carro_p2)
                                    return carro_p1, carro_p2
                            # Verificar clique no botão UPGRADE
                            elif botao_upgrade_rect_p2 and botao_upgrade_rect_p2.collidepoint(mouse_x, mouse_y):
                                # Verificar se carro está desbloqueado (Car1 sempre desbloqueado)
                                pode_upgrade = (carro_atual['prefixo_cor'] == "Car1") or esta_desbloqueado
                                if pode_upgrade and fundo_sem_textos:
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
                    return None, None
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    if not transicao_ativa:  # Só permite navegação se não estiver em transição
                        if fase_selecao == 1:
                            iniciar_transicao(-1, carro_p1)
                            carro_p1 = (carro_p1 - 1) % len(CARROS_DISPONIVEIS)
                            carro_selecionado_p1 = (gerenciador_progresso.obter_carro_atual(1) == carro_p1)
                        elif fase_selecao == 2:
                            iniciar_transicao(-1, carro_p2)
                            carro_p2 = (carro_p2 - 1) % len(CARROS_DISPONIVEIS)
                            carro_selecionado_p2 = (gerenciador_progresso.obter_carro_atual(2) == carro_p2)
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    if not transicao_ativa:  # Só permite navegação se não estiver em transição
                        if fase_selecao == 1:
                            iniciar_transicao(1, carro_p1)
                            carro_p1 = (carro_p1 + 1) % len(CARROS_DISPONIVEIS)
                            carro_selecionado_p1 = (gerenciador_progresso.obter_carro_atual(1) == carro_p1)
                        elif fase_selecao == 2:
                            iniciar_transicao(1, carro_p2)
                            carro_p2 = (carro_p2 + 1) % len(CARROS_DISPONIVEIS)
                            carro_selecionado_p2 = (gerenciador_progresso.obter_carro_atual(2) == carro_p2)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if not transicao_ativa:  # Só permite confirmação se não estiver em transição
                        if fase_selecao == 1:
                            carro_atual = CARROS_DISPONIVEIS[carro_p1]
                            esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                            if esta_desbloqueado and carro_selecionado_p1:
                                fase_selecao = 2
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
        
        # Mostrar dinheiro abaixo dos botões (dourado suave harmonizado)
        dinheiro_texto = t("menu.oficina.dinheiro").format(gerenciador_progresso.dinheiro)
        dinheiro_render = render_text(dinheiro_texto, 32, (255, 220, 100), bold=True, pixel_style=True)
        screen.blit(dinheiro_render, (20, 70))  # Movido para baixo dos botões (20 + 40 altura botão + 10 espaçamento)
        
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
        texto_voltar = render_text("VOLTAR", 18, (255, 255, 255), bold=True, pixel_style=True)
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
            
            selecionado_controle_dois_jogadores = (botao_selecionado_controle == "dois_jogadores")
            cor_dois_jogadores_menu = (150, 100, 200) if botao_dois_jogadores_menu_hover else (120, 80, 180)
            pygame.draw.rect(screen, cor_dois_jogadores_menu, botao_dois_jogadores_menu_rect)
            pygame.draw.rect(screen, (200, 150, 255), botao_dois_jogadores_menu_rect, 2)
            # Desenhar cursor do controle (caixa animada)
            if selecionado_controle_dois_jogadores and gerenciador_gamepad.obter_numero_controles() > 0:
                tamanho_cursor = 3 + int(2 * abs(math.sin(animacao_cursor * math.pi)))
                cursor_rect = pygame.Rect(
                    botao_dois_jogadores_menu_rect.x - tamanho_cursor,
                    botao_dois_jogadores_menu_rect.y - tamanho_cursor,
                    botao_dois_jogadores_menu_rect.width + tamanho_cursor * 2,
                    botao_dois_jogadores_menu_rect.height + tamanho_cursor * 2
                )
                pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
            texto_dois_jogadores_menu = render_text(texto_botao, 16, (255, 255, 255), bold=True, pixel_style=True)
            texto_dois_jogadores_menu_x = botao_dois_jogadores_menu_rect.x + (botao_dois_jogadores_menu_rect.width - texto_dois_jogadores_menu.get_width()) // 2
            texto_dois_jogadores_menu_y = botao_dois_jogadores_menu_rect.y + (botao_dois_jogadores_menu_rect.height - texto_dois_jogadores_menu.get_height()) // 2
            screen.blit(texto_dois_jogadores_menu, (texto_dois_jogadores_menu_x, texto_dois_jogadores_menu_y))
        
        if fase_selecao == 1:
            # FASE 1: Player 1 selecionando - sem subtítulo de "JOGADOR 1" e sem instruções
            
            # Carro selecionado P1 - Grande e centralizado
            carro_atual = CARROS_DISPONIVEIS[carro_p1]
            
            if transicao_ativa:
                carro_anterior_obj = CARROS_DISPONIVEIS[carro_anterior]
                carro_atual_obj = CARROS_DISPONIVEIS[carro_p1]
                sprite_anterior = sprites_carros[carro_anterior_obj['prefixo_cor']]
                sprite_atual = sprites_carros[carro_atual_obj['prefixo_cor']]
                
                pos_anterior = carro_anterior_obj.get('posicao_oficina', (LARGURA//2 - 300, 380))
                pos_atual = carro_atual_obj.get('posicao_oficina', (LARGURA//2 - 300, 380))
                
                pos_x_anterior = pos_anterior[0] + carro_atual_pos * LARGURA
                pos_x_atual = pos_atual[0] + carro_proximo_pos * LARGURA
                
                screen.blit(sprite_anterior, (int(pos_x_anterior), pos_anterior[1]))
                screen.blit(sprite_atual, (int(pos_x_atual), pos_atual[1]))
                
                esta_desbloqueado_atual = gerenciador_progresso.esta_desbloqueado(carro_atual_obj['prefixo_cor'])
                if not esta_desbloqueado_atual and icone_cadeado:
                    cadeado_x = int(pos_x_atual) + (sprite_atual.get_width() - icone_cadeado.get_width()) // 2
                    cadeado_y = pos_atual[1] + (sprite_atual.get_height() - icone_cadeado.get_height()) // 2
                    screen.blit(icone_cadeado, (cadeado_x, cadeado_y))
            else:
                sprite_atual = sprites_carros[carro_atual['prefixo_cor']]
                posicao = carro_atual.get('posicao_oficina', (LARGURA//2 - 300, 380))
                screen.blit(sprite_atual, posicao)
                
                esta_desbloqueado = gerenciador_progresso.esta_desbloqueado(carro_atual['prefixo_cor'])
                if not esta_desbloqueado and icone_cadeado:
                    cadeado_x = posicao[0] + (sprite_atual.get_width() - icone_cadeado.get_width()) // 2
                    cadeado_y = posicao[1] + (sprite_atual.get_height() - icone_cadeado.get_height()) // 2
                    screen.blit(icone_cadeado, (cadeado_x, cadeado_y))
            
            # Informações do carro na lateral direita - retângulo otimizado
            info_x = LARGURA - 300  # Largura reduzida
            info_y = 180  # Posição ajustada
            
            # Fundo semi-transparente para as informações - tamanho otimizado
            info_largura = 280
            info_altura = 320  # Altura ajustada para refletir o tamanho real das especificações
            if not hasattr(selecionar_carros_loop, '_info_bg_cache'):
                info_bg = pygame.Surface((info_largura, info_altura), pygame.SRCALPHA)
                info_bg.fill((0, 0, 0, 150))
                selecionar_carros_loop._info_bg_cache = info_bg
            screen.blit(selecionar_carros_loop._info_bg_cache, (info_x, info_y))
            
            if not hasattr(selecionar_carros_loop, '_textos_cache_p1') or selecionar_carros_loop._carro_texto_cache_p1 != carro_p1:
                nome_carro_info = render_text(carro_atual['nome'], 24, (100, 220, 255), bold=True, pixel_style=True)
                info_titulo = render_text(t("menu.oficina.especificacoes"), 18, (255, 255, 255), bold=True, pixel_style=True)
                selecionar_carros_loop._textos_cache_p1 = (nome_carro_info, info_titulo)
                selecionar_carros_loop._carro_texto_cache_p1 = carro_p1
            else:
                nome_carro_info, info_titulo = selecionar_carros_loop._textos_cache_p1
            
            nome_x_info = info_x + (info_largura - nome_carro_info.get_width()) // 2
            screen.blit(nome_carro_info, (nome_x_info, info_y + 15))
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
                if botao_usar_rect_p1:
                    usar_hover_p1 = botao_usar_rect_p1.collidepoint(pygame.mouse.get_pos())
                    usar_selecionado = carro_selecionado_p1
                    # Verificar se está selecionado pelo controle
                    selecionado_controle = (botao_selecionado_controle == "usar")
                    if usar_selecionado:
                        cor_usar = (50, 140, 90) if usar_hover_p1 else (40, 120, 80)
                        cor_borda_usar = (100, 200, 150)
                        cor_texto_usar = (200, 200, 200)
                    else:
                        cor_usar = (70, 180, 120) if usar_hover_p1 else (50, 150, 100)
                        cor_borda_usar = (120, 240, 180)
                        cor_texto_usar = (255, 255, 255)
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
                    texto_usar = render_text(t("menu.oficina.usar"), 18, cor_texto_usar, bold=True, pixel_style=True)
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
                    
                    # Desenhar ícone de notificação se houver upgrades disponíveis
                    if icon_exclamacao_oficina is not None and verificar_upgrades_disponiveis(carro_atual['prefixo_cor']):
                        # Animação de vibração (tremer) ao invés de piscar
                        vibracao_x = 2.0 * math.sin(tempo_animacao_exclamacao_oficina * 8.0)  # Vibração mais rápida
                        vibracao_y = 2.0 * math.cos(tempo_animacao_exclamacao_oficina * 8.0)  # Vibração vertical também
                        # Tamanho fixo (sem pulso)
                        icon_largura, icon_altura = icon_exclamacao_oficina.get_size()
                        # Posicionar no canto superior direito do botão
                        exclamacao_x = botao_upgrade_rect_p1.x + botao_upgrade_rect_p1.width - icon_largura - 5 + int(vibracao_x)
                        exclamacao_y = botao_upgrade_rect_p1.y + 5 + int(vibracao_y)
                        screen.blit(icon_exclamacao_oficina, (exclamacao_x, exclamacao_y))
                
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
            sprite_p1 = pygame.transform.scale(sprite_p1_original, (nova_largura, nova_altura))
            from core.i18n import t
            screen.blit(render_text(t("jogo.p1"), 20, (255, 255, 255), bold=True, pixel_style=True), (50, 130))
            screen.blit(sprite_p1, (50, 155))
            screen.blit(render_text(carro_p1_selecionado['nome'], 16, (255, 255, 255), bold=True, pixel_style=True), (50, 155 + nova_altura + 10))
            
            # Instruções removidas conforme solicitado
            
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
            info_altura = 320  # Altura ajustada para refletir o tamanho real das especificações
            if not hasattr(selecionar_carros_loop, '_info_bg_cache'):
                info_bg = pygame.Surface((info_largura, info_altura), pygame.SRCALPHA)
                info_bg.fill((0, 0, 0, 150))
                selecionar_carros_loop._info_bg_cache = info_bg
            screen.blit(selecionar_carros_loop._info_bg_cache, (info_x, info_y))
            
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
                if botao_usar_rect_p2:
                    usar_hover_p2 = botao_usar_rect_p2.collidepoint(pygame.mouse.get_pos())
                    usar_selecionado = carro_selecionado_p2
                    # Verificar se está selecionado pelo controle
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
                    if icon_exclamacao_oficina is not None and verificar_upgrades_disponiveis(carro_atual['prefixo_cor']):
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
        
        # Desenhar Crank (se ativo) - tem prioridade máxima
        if crank.ativo:
            crank.desenhar_dialogo(screen, dt)
        
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

def tela_upgrades(screen, prefixo_cor, nome_carro, fundo_garagem=None):
    """Tela de upgrades para um carro específico - estilo Need for Speed 2015"""
    from core.i18n import t
    from core.progresso import gerenciador_progresso
    from core.glub import glub
    from core.crank import crank
    from config import DIR_PROJETO
    import os
    
    # Verificar se o carro está desbloqueado
    # Garantir que Car1 sempre está desbloqueado
    carro_desbloqueado = (prefixo_cor == "Car1") or gerenciador_progresso.esta_desbloqueado(prefixo_cor)
    if not carro_desbloqueado:
        popup_musica.mostrar(t("mensagens.comprar_carro_primeiro"), tipo="outra")
        return True  # Volta para seleção de carros
    
    # Verificar se deve mostrar tutorial de upgrades do Crank (primeira vez)
    if not crank.tutorial_upgrades_mostrado and not crank.ativo:
        crank.mostrar_tutorial_upgrades()
    
    # Verificar se o Crank deve aparecer por dano crítico (apenas na tela de upgrades)
    if not crank.ativo:
        crank.verificar_aparecer_dano_critico()
    
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
        
        # Processar Crank primeiro (se ativo) - tem prioridade máxima
        if crank.ativo:
            resultado_crank = crank.processar_eventos(eventos)
            if resultado_crank == "confirmado":
                # Upgrade confirmado, realizar a compra
                if crank.upgrade_pendente:
                    upgrade_info = crank.upgrade_pendente
                    if gerenciador_progresso.comprar_upgrade(upgrade_info['prefixo_cor'], upgrade_info['tipo'], upgrade_info['preco']):
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
                        upgrades_carro = gerenciador_progresso.obter_todos_upgrades(upgrade_info['prefixo_cor'])
                        todos_maximizados = all(nivel >= 5 for nivel in upgrades_carro.values() if isinstance(nivel, int))
                        if todos_maximizados:
                            gerenciador_achievements.atualizar_estatistica("upgrades_maximizados", incrementar=True)
                            gerenciador_achievements.verificar_achievements(gerenciador_progresso)
                        
                        nome_upgrade = upgrades_disponiveis[upgrade_atual][1]
                        popup_musica.mostrar(t("mensagens.upgrade_comprado").format(nome_carro, nome_upgrade), tipo="outra")
                        
                        # Verificar se o Glub deve aparecer
                        if not glub.ativo:
                            glub.verificar_aparecer(upgrade_info['tipo'], upgrade_info['nivel'], upgrade_info['prefixo_cor'])
                    else:
                        popup_musica.mostrar(t("mensagens.dinheiro_insuficiente"), tipo="outra")
                    crank.upgrade_pendente = None
                crank.fechar()
            elif resultado_crank == "cancelado":
                # Upgrade cancelado
                crank.upgrade_pendente = None
                crank.fechar()
            elif resultado_crank == "fechado":
                crank.fechar()
            # Filtrar eventos de mouse e teclado que o Crank processa
            eventos = [ev for ev in eventos if not (ev.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN) and crank.ativo)]
        
        # Processar Glub (se ativo e Crank não estiver ativo) - antes de outros eventos
        if glub.ativo and not crank.ativo:
            resultado_glub = glub.processar_eventos(eventos, prefixo_cor=prefixo_cor)
            if resultado_glub in ["vendido", "recusado", "fechado"]:
                if resultado_glub == "vendido":
                    popup_musica.mostrar("Peça vendida para o Glub!", tipo="outra")
                # Continuar processando eventos normalmente
        
        for ev in eventos:
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
                        if nivel_atual < 5:
                            # Verificar se pode comprar (bloqueio por dano crítico)
                            pode_comprar, motivo = crank.pode_comprar_upgrade(upgrade_atual_tipo)
                            if not pode_comprar and motivo == "dano_critico":
                                crank.bloquear_upgrade_dano_critico(upgrade_atual_tipo)
                            else:
                                preco_base = gerenciador_progresso.calcular_preco_upgrade(upgrade_atual_tipo, nivel_atual)
                                # Aplicar multiplicador do humor do Crank
                                preco = crank.calcular_preco_com_humor(preco_base)
                                nivel_antigo = nivel_atual  # Salvar nível antigo antes de comprar
                                if gerenciador_progresso.comprar_upgrade(prefixo_cor, upgrade_atual_tipo, preco):
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
                        return True
                    continue
            
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return True
                elif ev.key in (pygame.K_LEFT, pygame.K_a) and not transicao_ativa:
                    iniciar_transicao(-1, upgrade_atual)
                    upgrade_atual = (upgrade_atual - 1) % len(upgrades_disponiveis)
                elif ev.key in (pygame.K_RIGHT, pygame.K_d) and not transicao_ativa:
                    iniciar_transicao(1, upgrade_atual)
                    upgrade_atual = (upgrade_atual + 1) % len(upgrades_disponiveis)
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # Verificar clique no upgrade atual
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
                    nivel_atual = gerenciador_progresso.obter_upgrade(prefixo_cor, upgrade_atual_tipo)
                    if nivel_atual < 5:
                        # Verificar se pode comprar (bloqueio por dano crítico)
                        pode_comprar, motivo = crank.pode_comprar_upgrade(upgrade_atual_tipo)
                        if not pode_comprar and motivo == "dano_critico":
                            crank.bloquear_upgrade_dano_critico(upgrade_atual_tipo)
                        else:
                            preco_base = gerenciador_progresso.calcular_preco_upgrade(upgrade_atual_tipo, nivel_atual)
                            # Aplicar multiplicador do humor do Crank
                            preco = crank.calcular_preco_com_humor(preco_base)
                            nivel_antigo = nivel_atual  # Salvar nível antigo antes de comprar
                            
                            # Verificar se precisa de confirmação
                            from config import CONFIGURACOES
                            precisa_confirmacao = CONFIGURACOES.get("jogo", {}).get("confirmar_upgrade", True)
                            
                            if precisa_confirmacao and not crank.ativo:
                                # Mostrar diálogo de confirmação
                                crank.mostrar_confirmacao_upgrade(upgrade_atual_tipo, preco, nivel_atual, prefixo_cor)
                            elif gerenciador_progresso.comprar_upgrade(prefixo_cor, upgrade_atual_tipo, preco):
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
                
                voltar_rect = pygame.Rect(LARGURA // 2 - 100, ALTURA - 80, 200, 50)
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
        
        # Título no topo
        titulo = render_text(t("menu.upgrades.titulo").format(nome_carro), 48, (100, 220, 255), bold=True, pixel_style=True)
        titulo_x = (LARGURA - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, 30))
        
        # Dinheiro no topo
        dinheiro_texto = t("menu.oficina.dinheiro").format(gerenciador_progresso.dinheiro)
        dinheiro_render = render_text(dinheiro_texto, 32, (255, 220, 100), bold=True, pixel_style=True)
        screen.blit(dinheiro_render, (20, 20))
        
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
                # Aplicar multiplicador do humor do Crank
                preco = crank.calcular_preco_com_humor(preco_base)
                pode_comprar = nivel_atual < 5 and gerenciador_progresso.tem_dinheiro(preco)
                
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
        
        # Botão voltar
        voltar_rect = pygame.Rect(LARGURA // 2 - 100, ALTURA - 80, 200, 50)
        voltar_hover = voltar_rect.collidepoint(mouse_x, mouse_y)
        cor_voltar = (100, 150, 200) if voltar_hover else (80, 120, 180)
        pygame.draw.rect(screen, cor_voltar, voltar_rect)
        pygame.draw.rect(screen, (100, 220, 255), voltar_rect, 2)
        voltar_texto = render_text(t("menu.upgrades.voltar"), 22, (255, 255, 255), bold=True, pixel_style=True)
        voltar_texto_x = voltar_rect.x + (voltar_rect.width - voltar_texto.get_width()) // 2
        voltar_texto_y = voltar_rect.y + (voltar_rect.height - voltar_texto.get_height()) // 2
        screen.blit(voltar_texto, (voltar_texto_x, voltar_texto_y))
        
        popup_musica.atualizar(dt)
        popup_musica.desenhar(screen)
        
        # Desenhar Crank (se ativo) - tem prioridade máxima
        if crank.ativo:
            crank.desenhar_dialogo(screen, dt)
        # Desenhar Glub (se ativo e Crank não estiver ativo)
        elif glub.ativo:
            glub.desenhar_dialogo(screen, dt)
        
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
                        chave = opcoes_idioma[opcao_atual][1]
                        CONFIGURACOES["idioma"] = chave
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
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)

    from core.i18n import t
    opcoes_jogo = [
        (t("jogo.confirmar_upgrade"), "confirmar_upgrade")
    ]
    opcao_voltar = (t("jogo.voltar"), "voltar")

    opcao_atual = 0
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
                        chave = opcoes_jogo[opcao_atual][1]
                        if chave == "confirmar_upgrade":
                            if "jogo" not in CONFIGURACOES:
                                CONFIGURACOES["jogo"] = {}
                            CONFIGURACOES["jogo"][chave] = not CONFIGURACOES["jogo"].get(chave, True)
                            salvar_configuracoes()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return True
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    opcao_atual = (opcao_atual - 1) % len(opcoes_jogo)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    opcao_atual = (opcao_atual + 1) % len(opcoes_jogo)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    chave = opcoes_jogo[opcao_atual][1]
                    if chave == "confirmar_upgrade":
                        if "jogo" not in CONFIGURACOES:
                            CONFIGURACOES["jogo"] = {}
                        CONFIGURACOES["jogo"][chave] = not CONFIGURACOES["jogo"].get(chave, True)
                        salvar_configuracoes()

        # Atualizar animações hover
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_in_caixa = (caixa_x <= mouse_x <= caixa_x + caixa_largura and
                          caixa_y <= mouse_y <= caixa_y + caixa_altura)
        
        for i in range(len(opcoes_jogo)):
            if i == opcao_atual:
                hover_animation[i] = 0.0
            else:
                y_opcao = caixa_y + 80 + i * 50
                opcao_rect = pygame.Rect(caixa_x + 20, y_opcao - 5, caixa_largura - 40, 50)
                if opcao_rect.collidepoint(mouse_x, mouse_y) and mouse_in_caixa:
                    hover_animation[i] = min(1.0, hover_animation[i] + dt * hover_speed)
                else:
                    hover_animation[i] = max(0.0, hover_animation[i] - dt * hover_speed)

        screen.blit(bg, (0, 0))

        # Caixa de opções
        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((20, 20, 20, 240))
        screen.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(screen, (100, 220, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 2)

        # Título
        titulo = render_text(t("menu.opcoes.jogo"), 36, (100, 220, 255), bold=True, pixel_style=True)
        titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
        titulo_y = caixa_y + 20
        screen.blit(titulo, (titulo_x, titulo_y))

        # Opções
        for i, (nome, chave) in enumerate(opcoes_jogo):
            y_opcao = caixa_y + 80 + i * 50
            opcao_rect = pygame.Rect(caixa_x + 20, y_opcao - 5, caixa_largura - 40, 50)
            
            hover_progress = hover_animation[i] if i != opcao_atual else 0.0
            
            if i == opcao_atual:
                cor_fundo = (0, 200, 255, 50)
                cor_texto = (0, 200, 255)
            else:
                cor_fundo = (0, 0, 0, int(30 * hover_progress))
                cor_texto = (255, 255, 255) if hover_progress == 0 else (0, 200, 255)
            
            if cor_fundo[3] > 0:
                opcao_fundo = pygame.Surface((opcao_rect.width, opcao_rect.height), pygame.SRCALPHA)
                opcao_fundo.fill(cor_fundo)
                screen.blit(opcao_fundo, opcao_rect.topleft)
            
            pygame.draw.rect(screen, (100, 220, 255), opcao_rect, 2)
            
            # Valor da opção (ON/OFF)
            valor = CONFIGURACOES.get("jogo", {}).get(chave, True)
            valor_texto = "ON" if valor else "OFF"
            texto_valor = render_text(valor_texto, 24, cor_texto, bold=True, pixel_style=True)
            valor_x = opcao_rect.right - texto_valor.get_width() - 20
            valor_y = y_opcao + (50 - texto_valor.get_height()) // 2
            screen.blit(texto_valor, (valor_x, valor_y))
            
            # Nome da opção
            texto_opcao = render_text(nome, 24, cor_texto, bold=True, pixel_style=True)
            texto_x = opcao_rect.x + 20
            texto_y = y_opcao + (50 - texto_opcao.get_height()) // 2
            screen.blit(texto_opcao, (texto_x, texto_y))

        # Botão voltar
        voltar_y = caixa_y + caixa_altura - 60
        voltar_rect = pygame.Rect(caixa_x + 20, voltar_y - 5, caixa_largura - 40, 50)
        voltar_hover = voltar_rect.collidepoint(mouse_x, mouse_y)
        cor_voltar = (100, 150, 200) if voltar_hover else (80, 120, 180)
        pygame.draw.rect(screen, cor_voltar, voltar_rect)
        pygame.draw.rect(screen, (100, 220, 255), voltar_rect, 2)
        voltar_texto = render_text(t("jogo.voltar"), 22, (255, 255, 255), bold=True, pixel_style=True)
        voltar_texto_x = voltar_rect.x + (voltar_rect.width - voltar_texto.get_width()) // 2
        voltar_texto_y = voltar_rect.y + (voltar_rect.height - voltar_texto.get_height()) // 2
        screen.blit(voltar_texto, (voltar_texto_x, voltar_texto_y))

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
        (t("modo_jogo.ghost"), TipoJogo.GHOST)
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
        
        # Verificar hover do pop-up
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
                x = grid_x + col * (minimapa_tamanho + espacamento)
                y = grid_y + linha * (minimapa_tamanho + espacamento)
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
            x = grid_x + col * (minimapa_tamanho + espacamento)
            y = grid_y + linha * (minimapa_tamanho + espacamento)
            
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
    import math
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
        resultado_menu = menu_loop(screen)
        if isinstance(resultado_menu, tuple) and len(resultado_menu) == 2:
            escolha, nova_tela = resultado_menu
            screen = nova_tela
        else:
            escolha = resultado_menu
        
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
                
                # Verificar se modo 2 jogadores e se os carros foram escolhidos
                if modo_jogo == ModoJogo.DOIS_JOGADORES:
                    # Redirecionar para a oficina para escolher carros
                    resultado_carros = selecionar_carros_loop(screen)
                    if resultado_carros[0] is None or resultado_carros[1] is None:
                        # Cancelou a seleção, continuar no menu
                        continue
                    # Atualizar carros selecionados
                    carro_p1, carro_p2 = resultado_carros
                
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
