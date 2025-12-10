"""
Hub do Território - Tela de ações após selecionar um território no mapa
Mostra o NPC local e lista de atividades disponíveis
"""

import pygame
import os
from typing import Optional, Dict, List
from config import LARGURA, ALTURA, FPS, DIR_PROJETO, obter_caminho_sprite_dia_noite
from core.territorios import obter_territorio, Territorio

def obter_caminho_fabrica():
    return obter_caminho_sprite_dia_noite("fosso")
def obter_caminho_iate_barao():
    return obter_caminho_sprite_dia_noite("iate_barao")
def obter_caminho_monte_akira():
    return obter_caminho_sprite_dia_noite("monte_akira")
def obter_caminho_torre_king():
    caminho_saguao = os.path.join(DIR_PROJETO, "assets", "images", "ui", "saguao_torre_rex.png")
    if os.path.exists(caminho_saguao):
        return caminho_saguao
    return obter_caminho_sprite_dia_noite("predio_rex")
def obter_caminho_bunker():
    return obter_caminho_sprite_dia_noite("bunker")
def obter_caminho_oficina():
    return obter_caminho_sprite_dia_noite("oficina")
def obter_caminho_autodromo():
    return obter_caminho_sprite_dia_noite("autodromo_fora")
def obter_caminho_beco_sucata():
    return obter_caminho_sprite_dia_noite("beco_de_sucata")
def obter_caminho_beco_neon():
    caminho_noite = os.path.join(DIR_PROJETO, "assets", "images", "ui", "beco_neon_noite.png")
    if os.path.exists(caminho_noite):
        return caminho_noite
    caminho_dia = os.path.join(DIR_PROJETO, "assets", "images", "ui", "beco_neon_dia.png")
    if os.path.exists(caminho_dia):
        return caminho_dia
    return caminho_noite

CAMINHO_FABRICA = obter_caminho_fabrica()
CAMINHO_IATE_BARAO = obter_caminho_iate_barao()
CAMINHO_MONTE_AKIRA = obter_caminho_monte_akira()
CAMINHO_TORRE_KING = obter_caminho_torre_king()
CAMINHO_BUNKER = obter_caminho_bunker()
CAMINHO_OFICINA = obter_caminho_oficina()

def obter_mapeamento_fundos():
    """Retorna o mapeamento de fundos com caminhos dinâmicos baseados em dia/noite"""
    return {
        # Barão - Iate
        "docas_barao": obter_caminho_iate_barao(),
        "iate_barao": obter_caminho_iate_barao(),
        "iate_do_barao": obter_caminho_iate_barao(),
        "iate_do_barão": obter_caminho_iate_barao(),
        "barao": obter_caminho_iate_barao(),
        "barão": obter_caminho_iate_barao(),
        
        # Boris - Fábrica
        "fabrica_boris": obter_caminho_fabrica(),
        "fabrica_do_boris": obter_caminho_fabrica(),
        "fábrica_do_boris": obter_caminho_fabrica(),
        "fabrica": obter_caminho_fabrica(),
        "fábrica": obter_caminho_fabrica(),
        "boris": obter_caminho_fabrica(),
        "fosso_ferrugem": obter_caminho_fabrica(),
        
        # Akira - Monte
        "templo_akira": obter_caminho_monte_akira(),
        "monte_akira": obter_caminho_monte_akira(),
        "monte": obter_caminho_monte_akira(),
        "montanha_akira": obter_caminho_monte_akira(),
        "akira": obter_caminho_monte_akira(),
        
        # Rex - Torre
        "torre_rex": obter_caminho_torre_king(),
        "torre_king": obter_caminho_torre_king(),
        "predio_do_rex": obter_caminho_torre_king(),
        "prédio_do_rex": obter_caminho_torre_king(),
        "predio_rex": obter_caminho_torre_king(),
        "prédio_rex": obter_caminho_torre_king(),
        "rex": obter_caminho_torre_king(),
        
        # Pixel - Bunker
        "bueiro_pixel": obter_caminho_bunker(),
        "pixel": obter_caminho_bunker(),
        "bunker": obter_caminho_bunker(),
        
        # Oficina/Garagem
        "oficina": obter_caminho_oficina(),
        "garagem": obter_caminho_oficina(),
        "crank": obter_caminho_oficina(),
        
        # Autódromo
        "autódromo": obter_caminho_autodromo(),
        "autodromo": obter_caminho_autodromo(),
        
        # Glub - Beco da Sucata
        "beco_da_sucata": obter_caminho_beco_sucata(),
        "beco_de_sucata": obter_caminho_beco_sucata(),
        "loja_glub": obter_caminho_beco_sucata(),
        "glub": obter_caminho_beco_sucata(),
        
        # Slick - Beco Neon
        "beco_neon": obter_caminho_beco_neon(),
        "slick": obter_caminho_beco_neon(),
    }

MAPEAMENTO_FUNDOS = obter_mapeamento_fundos()

def _get_render_text():
    """Importa e retorna a função render_text"""
    from core.menu import render_text
    return render_text

def obter_fundo_territorio(territorio_id: str, npc_id: str = None, sprite_fundo_area: str = None) -> Optional[str]:
    """Retorna o caminho do sprite de fundo para um território"""
    # Primeiro, usar sprite_fundo da área se fornecido
    if sprite_fundo_area:
        # Se for caminho relativo, converter para absoluto
        if not os.path.isabs(sprite_fundo_area):
            caminho_absoluto = os.path.join(DIR_PROJETO, sprite_fundo_area)
        else:
            caminho_absoluto = sprite_fundo_area
        
        if os.path.exists(caminho_absoluto):
            return caminho_absoluto
    
    # Atualizar mapeamento dinamicamente (para refletir mudanças dia/noite)
    mapeamento = obter_mapeamento_fundos()
    
    # Tentar pelo ID do território
    if territorio_id in mapeamento:
        caminho = mapeamento[territorio_id]
        if caminho and os.path.exists(caminho):
            return caminho
    
    # Tentar pelo NPC ID
    if npc_id and npc_id in mapeamento:
        caminho = mapeamento[npc_id]
        if caminho and os.path.exists(caminho):
            return caminho
    
    # Verificar se o ID contém palavras-chave (usando funções dinâmicas)
    territorio_id_lower = territorio_id.lower()
    if "oficina" in territorio_id_lower or "garagem" in territorio_id_lower or "crank" in territorio_id_lower:
        caminho = obter_caminho_oficina()
        if os.path.exists(caminho):
            return caminho
    elif "barao" in territorio_id_lower or "iate" in territorio_id_lower:
        caminho = obter_caminho_iate_barao()
        if os.path.exists(caminho):
            return caminho
    elif "boris" in territorio_id_lower or "fabrica" in territorio_id_lower or "fosso" in territorio_id_lower or "ferrugem" in territorio_id_lower:
        caminho = obter_caminho_fabrica()
        if os.path.exists(caminho):
            return caminho
    elif "glub" in territorio_id_lower or ("beco" in territorio_id_lower and "sucata" in territorio_id_lower):
        caminho = obter_caminho_beco_sucata()
        if os.path.exists(caminho):
            return caminho
    elif "slick" in territorio_id_lower or ("beco" in territorio_id_lower and "neon" in territorio_id_lower):
        caminho = obter_caminho_beco_neon()
        if os.path.exists(caminho):
            return caminho
    elif "akira" in territorio_id_lower or "monte" in territorio_id_lower or "templo" in territorio_id_lower:
        caminho = obter_caminho_monte_akira()
        if os.path.exists(caminho):
            return caminho
    elif "rex" in territorio_id_lower or "torre" in territorio_id_lower or "king" in territorio_id_lower:
        caminho = obter_caminho_torre_king()
        if os.path.exists(caminho):
            return caminho
    elif "pixel" in territorio_id_lower or "bueiro" in territorio_id_lower or "bunker" in territorio_id_lower:
        caminho = obter_caminho_bunker()
        if os.path.exists(caminho):
            return caminho
    elif "autódromo" in territorio_id_lower or "autodromo" in territorio_id_lower:
        caminho = obter_caminho_autodromo()
        if os.path.exists(caminho):
            return caminho
    
    return None

def menu_escolha_fabrica_boris(screen) -> Optional[str]:
    """Menu de escolha na fábrica do Boris: escolher entre Boris ou Glub"""
    from core.menu import render_text
    
    opcoes = [
        ("Fábrica do Boris", "boris"),
        ("Beco da Sucata", "glub")
    ]
    
    opcao_selecionada = 0
    clock = pygame.time.Clock()
    rodando = True
    
    # Carregar fundo da fábrica
    CAMINHO_FABRICA = obter_caminho_fabrica()
    if os.path.exists(CAMINHO_FABRICA):
        bg_raw = pygame.image.load(CAMINHO_FABRICA).convert()
        bg = pygame.transform.scale(bg_raw, (LARGURA, ALTURA))
    else:
        bg = pygame.Surface((LARGURA, ALTURA))
        bg.fill((30, 30, 30))
    
    while rodando:
        dt = clock.tick(FPS) / 1000.0
        
        eventos = pygame.event.get()
        for ev in eventos:
            if ev.type == pygame.QUIT:
                return None
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_UP or ev.key == pygame.K_w:
                    opcao_selecionada = (opcao_selecionada - 1) % len(opcoes)
                elif ev.key == pygame.K_DOWN or ev.key == pygame.K_s:
                    opcao_selecionada = (opcao_selecionada + 1) % len(opcoes)
                elif ev.key == pygame.K_RETURN or ev.key == pygame.K_SPACE:
                    escolha = opcoes[opcao_selecionada][1]
                    return escolha
                elif ev.key == pygame.K_ESCAPE:
                    return "voltar_mapa"
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    mouse_x, mouse_y = ev.pos
                    # Verificar clique nas opções
                    caixa_largura = 500
                    caixa_altura = 200
                    caixa_x = (LARGURA - caixa_largura) // 2
                    caixa_y = (ALTURA - caixa_altura) // 2
                    opcao_altura = 80
                    opcao_espacamento = 20
                    
                    for i, (nome, _) in enumerate(opcoes):
                        opcao_y = caixa_y + 60 + i * (opcao_altura + opcao_espacamento)
                        opcao_rect = pygame.Rect(caixa_x + 20, opcao_y, caixa_largura - 40, opcao_altura)
                        if opcao_rect.collidepoint(mouse_x, mouse_y):
                            escolha = opcoes[i][1]
                            return escolha
                    
                    # Verificar clique no botão voltar
                    voltar_rect = pygame.Rect(caixa_x + caixa_largura - 150, caixa_y + caixa_altura - 40, 130, 35)
                    if voltar_rect.collidepoint(mouse_x, mouse_y):
                        return "voltar_mapa"
        
        # Desenhar
        screen.blit(bg, (0, 0))
        
        # Caixa do menu
        caixa_largura = 500
        caixa_altura = 200
        caixa_x = (LARGURA - caixa_largura) // 2
        caixa_y = (ALTURA - caixa_altura) // 2
        
        overlay = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (caixa_x, caixa_y))
        pygame.draw.rect(screen, (200, 200, 200), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        # Título
        titulo = render_text("Onde você quer ir?", 24, (255, 255, 255), bold=True, pixel_style=True)
        screen.blit(titulo, (caixa_x + (caixa_largura - titulo.get_width()) // 2, caixa_y + 15))
        
        # Opções
        opcao_altura = 80
        opcao_espacamento = 20
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        for i, (nome, _) in enumerate(opcoes):
            opcao_y = caixa_y + 60 + i * (opcao_altura + opcao_espacamento)
            opcao_rect = pygame.Rect(caixa_x + 20, opcao_y, caixa_largura - 40, opcao_altura)
            
            hover = opcao_rect.collidepoint(mouse_x, mouse_y)
            selecionada = (i == opcao_selecionada)
            
            if selecionada or hover:
                cor_bg = (100, 100, 200)
                cor_texto = (255, 255, 255)
            else:
                cor_bg = (50, 50, 100)
                cor_texto = (200, 200, 200)
            
            overlay_opcao = pygame.Surface((opcao_rect.width, opcao_rect.height), pygame.SRCALPHA)
            overlay_opcao.fill(cor_bg)
            screen.blit(overlay_opcao, opcao_rect.topleft)
            pygame.draw.rect(screen, cor_texto, opcao_rect, 2)
            
            texto_opcao = render_text(nome, 20, cor_texto, bold=True, pixel_style=True)
            screen.blit(texto_opcao, (opcao_rect.x + (opcao_rect.width - texto_opcao.get_width()) // 2,
                                     opcao_rect.y + (opcao_rect.height - texto_opcao.get_height()) // 2))
        
        # Botão voltar
        voltar_rect = pygame.Rect(caixa_x + caixa_largura - 150, caixa_y + caixa_altura - 40, 130, 35)
        hover_voltar = voltar_rect.collidepoint(mouse_x, mouse_y)
        cor_voltar = (255, 100, 100) if hover_voltar else (200, 50, 50)
        pygame.draw.rect(screen, cor_voltar, voltar_rect)
        pygame.draw.rect(screen, (255, 255, 255), voltar_rect, 2)
        texto_voltar = render_text("Voltar", 16, (255, 255, 255), bold=True, pixel_style=True)
        screen.blit(texto_voltar, (voltar_rect.x + (voltar_rect.width - texto_voltar.get_width()) // 2,
                                  voltar_rect.y + (voltar_rect.height - texto_voltar.get_height()) // 2))
        
        pygame.display.flip()
    
    return None

def hub_territorio_loop(screen, territorio_id: str, area_nome: str = None, sprite_fundo: str = None) -> Optional[Dict]:
    """
    Loop principal do hub do território
    Retorna um dicionário com a atividade selecionada ou None se cancelado
    
    Formato retornado:
    {
        "atividade": "corrida_aposta",
        "tipo": "corrida",
        "parametros": {...}
    }
    """
    # Verificar gatilhos narrativos ao entrar no território
    from core.narrative_system import narrative_system
    from core.progresso import gerenciador_progresso
    
    # Garantir que current_chapter_id está definido
    if not narrative_system.current_chapter_id:
        capitulo_atual = gerenciador_progresso.obter_capitulo_atual()
        if capitulo_atual:
            narrative_system.current_chapter_id = capitulo_atual
            print(f"[HUB_TERRITORIO] current_chapter_id estava None, atualizado para {capitulo_atual}")
    
    # SEMPRE verificar gatilhos, mesmo sem current_chapter_id (para permitir cenas de capítulos futuros)
    # Se não houver current_chapter_id, tentar inferir do progresso
    if not narrative_system.current_chapter_id:
        capitulo_atual = gerenciador_progresso.obter_capitulo_atual()
        if capitulo_atual:
            narrative_system.current_chapter_id = capitulo_atual
            print(f"[HUB_TERRITORIO] current_chapter_id ainda None após tentativa, definindo como {capitulo_atual}")
    
    # Verificar gatilhos mesmo se current_chapter_id não estiver definido (para permitir cenas de qualquer capítulo)
    if True:  # Sempre verificar gatilhos
        # Mapear territorio_id para locationId do narrative
        location_map = {
            "fosso_ferrugem": "fosso_ferrugem",
            "fábrica_do_boris": "fosso_ferrugem",
            "fabrica_do_boris": "fosso_ferrugem",
            "bg_garagem": "bg_garagem",
            "oficina": "bg_garagem",
            "montanha": "montanha_santuario",
            "monte": "montanha_santuario",
            "templo_akira": "montanha_santuario",  # Mapear templo_akira para montanha_santuario
            "montanha_akira": "montanha_santuario",
            "akira": "montanha_santuario",
            "cinturao_industrial": "cinturao_industrial",
            "cinturão": "cinturao_industrial",
            "esconderijo_pixel": "esconderijo_pixel",
            "bg_beco_sucata": "bg_beco_sucata",
            "beco_da_sucata": "bg_beco_sucata",
            "beco_de_sucata": "bg_beco_sucata",
            "loja_glub": "bg_beco_sucata",
            "glub": "bg_beco_sucata",
            "bg_beco_neon": "bg_beco_neon",
            "beco_neon": "bg_beco_neon",
            "slick": "bg_beco_neon",
            "docas_barao": "iate_barao",
            "iate_barao": "iate_barao",
            "iate_do_barao": "iate_barao",
            "iate_do_barão": "iate_barao",
            "barao": "iate_barao",
            "barão": "iate_barao",
        }
        
        location_id = location_map.get(territorio_id.lower(), territorio_id.lower())
        context = {"locationId": location_id}
        
        # IMPORTANTE: Só verificar gatilhos se o locationId corresponder ao territorio_id
        # Isso evita que triggers de outras localizações sejam ativados incorretamente
        print(f"[HUB_TERRITORIO] Verificando gatilhos para territorio_id={territorio_id}, location_id={location_id}, current_chapter_id={narrative_system.current_chapter_id}")
        print(f"[HUB_TERRITORIO] Context passado: {context}")
        
        # Verificar se há cenas pendentes com gatilho enter_location
        gatilho_encontrado = narrative_system.verificar_gatilhos_pendentes(context)
        print(f"[HUB_TERRITORIO] Resultado verificar_gatilhos_pendentes: {gatilho_encontrado}, narrative_system.active={narrative_system.active}, current_scene_id={narrative_system.current_scene_id}")
        if gatilho_encontrado:
            # Se uma cena foi iniciada, ativar narrativa e retornar None para processar no loop principal
            print(f"[HUB_TERRITORIO] Gatilho encontrado e cena iniciada para location_id={location_id}, ativando narrativa...")
            narrative_system.active = True
            return None  # Retornar None para que o loop principal processe a narrativa
    
    # Se for a casa, usar sistema de point and click
    if territorio_id.lower() == "casa" or (area_nome and "casa" in area_nome.lower()):
        from core.casa import casa_loop
        return casa_loop(screen, sprite_fundo)
    
    territorio = obter_territorio(territorio_id)
    
    # Se não encontrar território, tentar criar um básico baseado no ID
    if not territorio:
        # Verificar se é uma área especial (ex: oficina, autódromo)
        territorio_id_lower = territorio_id.lower()
        area_nome_lower = (area_nome or "").lower()
        
        # Verificar se é oficina/garagem - mas ANTES de redirecionar, verificar se há cena narrativa pendente
        if ("oficina" in territorio_id_lower or "garagem" in territorio_id_lower or 
            "crank" in territorio_id_lower or 
            "oficina" in area_nome_lower or "garagem" in area_nome_lower):
            
            # Verificar se há uma cena narrativa pendente para a garagem (especialmente ch1_1_crank_garage_intro)
            if narrative_system.current_chapter_id:
                from core.missoes import gerenciador_missoes
                # Se a missão m1 está ativa e a cena ch1_1_crank_garage_intro não foi visitada, iniciar a cena
                if (gerenciador_missoes.missao_ativa_id == "m1_primeira_faisca" and 
                    "ch1_1_crank_garage_intro" not in narrative_system.scenes_visited):
                    print(f"[HUB_TERRITORIO] Missão m1 ativa e cena ch1_1_crank_garage_intro não visitada, iniciando cena...")
                    if narrative_system.iniciar_cena("ch1_1_crank_garage_intro"):
                        narrative_system.active = True
                        return "narrativa_ativa"
            
            # Se não há cena narrativa pendente, redirecionar para a oficina normalmente
            from core.menu import selecionar_carros_loop
            selecionar_carros_loop(screen)
            return "voltar_mapa"  # Voltar para o mapa após sair da oficina
        
        # Verificar se é o iate do Barão - iniciar cena narrativa
        if ("iate" in territorio_id_lower and "barao" in territorio_id_lower) or ("iate" in territorio_id_lower and "barão" in territorio_id_lower):
            from core.narrative_system import narrative_system
            from core.tempo_jogo import gerenciador_tempo
            
            # Verificar se é noite (18h-6h) e se tem dívida
            hora_atual = gerenciador_tempo.obter_hora()
            is_noite = hora_atual >= 18 or hora_atual < 6
            from core.progresso import gerenciador_progresso
            tem_divida = gerenciador_progresso.barao_emprestimo_ativo
            
            # Escolher cena baseado em hora e dívida
            if is_noite and tem_divida:
                cena_id = "ch4_8_iate_barao_cobranca"
            else:
                cena_id = "ch4_7_iate_barao_visita"
            
            # Tentar iniciar a cena narrativa
            if narrative_system.iniciar_cena(cena_id):
                narrative_system.active = True
                # Loop de narrativa
                clock_narrativa = pygame.time.Clock()
                while narrative_system.active:
                    dt = clock_narrativa.tick(FPS) / 1000.0
                    narrative_system.atualizar(dt)
                    
                    eventos = pygame.event.get()
                    for ev in eventos:
                        if ev.type == pygame.QUIT:
                            narrative_system.fechar()
                            return None
                    
                    resultado = narrative_system.processar_eventos(eventos)
                    if resultado == "fechado":
                        narrative_system.fechar()
                        break
                    
                    narrative_system.desenhar(screen)
                    pygame.display.flip()
            
            return "voltar_mapa"
        
        # Verificar se é o autódromo - abrir menu de corridas do Circuito da Coroa
        if ("autódromo" in territorio_id_lower or "autodromo" in territorio_id_lower or
            "autódromo" in area_nome_lower or "autodromo" in area_nome_lower):
            # Abrir menu de corridas do Circuito da Coroa
            from core.pc_corridas import autodromo_corridas_loop
            corrida_info = autodromo_corridas_loop(screen)
            # Se uma corrida foi selecionada, retornar para iniciar a corrida
            if corrida_info:
                return {
                    "atividade": "corrida_circuito_coroa",
                    "tipo": "corrida",
                    "parametros": corrida_info
                }
            return None  # Cancelado
        
        # Criar território temporário
        from core.territorios import Territorio, TipoTerritorio
        # Garantir que o nome do território está correto
        if not area_nome:
            # Se não foi passado area_nome, gerar a partir do territorio_id
            nome_territorio = territorio_id.replace("_", " ").title()
            # Corrigir nomes específicos
            if "beco" in territorio_id.lower() or "sucata" in territorio_id.lower():
                nome_territorio = "Beco da Sucata"
            elif "boris" in territorio_id.lower() or "fosso" in territorio_id.lower() or "ferrugem" in territorio_id.lower():
                nome_territorio = "Fábrica do Boris"
        else:
            nome_territorio = area_nome
        
        territorio = Territorio(
            id=territorio_id,
            nome=nome_territorio,
            descricao="Local da cidade",
            tipo=TipoTerritorio.TECNICA,
            npc_id=territorio_id,
            posicao_mapa=(0, 0),
            area_clicavel=(0, 0, 0, 0),
            atividades=[]
        )
    
    clock = pygame.time.Clock()
    render_text = _get_render_text()
    
    # Carregar fundo do território
    caminho_fundo = obter_fundo_territorio(territorio_id, territorio.npc_id, sprite_fundo)
    print(f"[HUB_TERRITORIO] Carregando fundo para territorio_id={territorio_id}, npc_id={territorio.npc_id}, sprite_fundo={sprite_fundo}, caminho={caminho_fundo}, existe={os.path.exists(caminho_fundo) if caminho_fundo else False}")
    
    # Se não encontrou o caminho, tentar diretamente com obter_caminho_beco_sucata para beco da sucata
    if not caminho_fundo and ("beco" in territorio_id.lower() or "sucata" in territorio_id.lower() or "glub" in territorio_id.lower()):
        caminho_fundo = obter_caminho_beco_sucata()
        print(f"[HUB_TERRITORIO] Tentando caminho direto para beco da sucata: {caminho_fundo}, existe={os.path.exists(caminho_fundo) if caminho_fundo else False}")
        
        # Se ainda não encontrou (arquivo noite não existe), tentar arquivo dia como fallback
        if not caminho_fundo or not os.path.exists(caminho_fundo):
            caminho_fundo_dia = os.path.join(DIR_PROJETO, "assets", "images", "ui", "beco_de_sucata_dia.png")
            if os.path.exists(caminho_fundo_dia):
                caminho_fundo = caminho_fundo_dia
                print(f"[HUB_TERRITORIO] Usando fallback dia para beco da sucata: {caminho_fundo}")
        
        # Se ainda não encontrou, tentar arquivo dia como fallback
        if not caminho_fundo or not os.path.exists(caminho_fundo):
            caminho_fundo_dia = os.path.join(DIR_PROJETO, "assets", "images", "ui", "beco_de_sucata_dia.png")
            if os.path.exists(caminho_fundo_dia):
                caminho_fundo = caminho_fundo_dia
                print(f"[HUB_TERRITORIO] Usando fallback dia para beco da sucata: {caminho_fundo}")
    
    if caminho_fundo and os.path.exists(caminho_fundo):
        try:
            bg_raw = pygame.image.load(caminho_fundo).convert_alpha()
            bg = pygame.transform.scale(bg_raw, (LARGURA, ALTURA))
        except Exception as e:
            print(f"Erro ao carregar fundo do território: {e}")
            bg = None
    elif territorio.imagem_fundo and os.path.exists(territorio.imagem_fundo):
        try:
            bg_raw = pygame.image.load(territorio.imagem_fundo).convert_alpha()
            bg = pygame.transform.scale(bg_raw, (LARGURA, ALTURA))
        except Exception as e:
            print(f"Erro ao carregar fundo do território: {e}")
            bg = None
    else:
        bg = None
    
    # Fallback: fundo baseado no tipo de território
    if bg is None:
        bg = pygame.Surface((LARGURA, ALTURA))
        cores_fundo = {
            "dinheiro_rapido": (30, 10, 10),      # Vermelho escuro
            "pecas_brutas": (30, 20, 10),         # Laranja escuro
            "tecnica": (10, 20, 30),             # Azul escuro
            "informacao": (20, 10, 30),           # Roxo escuro
            "progressao": (30, 30, 10)            # Amarelo escuro
        }
        cor_fundo = cores_fundo.get(territorio.tipo.value, (20, 20, 20))
        bg.fill(cor_fundo)
    
    # Carregar sprite do NPC (se existir)
    npc_sprite = None
    # Verificar se há NPC antes de construir o caminho
    if territorio.npc_id:
        caminho_npc = os.path.join(DIR_PROJETO, "assets", "images", "characters", territorio.npc_id)
        if os.path.exists(caminho_npc):
            # Tentar carregar sprite neutro
            sprite_neutro = os.path.join(caminho_npc, "neutro.png")
            if os.path.exists(sprite_neutro):
                try:
                    npc_sprite = pygame.image.load(sprite_neutro).convert_alpha()
                except:
                    pass
    
    # Lista de atividades (não usada mais - NPCs gerenciam suas próprias atividades)
    atividades = territorio.atividades
    
    # Animações
    tempo_animacao = 0.0
    
    # Verificar se é território do Boris
    from core.boris import boris
    from core.progresso import gerenciador_progresso
    mostrar_boris = False
    # Inicializar mostrar_glub antes de qualquer uso
    from core.glub import glub
    mostrar_glub = False
    
    # Verificar se é território do Boris (fábrica)
    # Verificar tanto pelo npc_id quanto pelo territorio_id (pode ser "fosso_ferrugem")
    is_territorio_boris = (territorio.npc_id and ("boris" in territorio.npc_id.lower() or "fosso" in territorio.npc_id.lower() or "ferrugem" in territorio.npc_id.lower())) or \
                         ("boris" in territorio_id.lower() or "fosso" in territorio_id.lower() or "ferrugem" in territorio_id.lower())
    if is_territorio_boris:
        # Recarregar estado do Boris para garantir que está atualizado
        boris.carregar_estado()
        
        # Garantir que os sprites do Boris estão carregados (incluindo o fundo)
        if not boris.sprites_carregados:
            boris.carregar_sprites()
        # Se o fundo ainda não foi carregado, carregar do território
        if not boris.sprite_fundo_redimensionado:
            # Tentar usar o bg que já foi carregado
            if bg:
                # Criar uma cópia do bg para o Boris
                boris.sprite_fundo_redimensionado = bg.copy()
                print(f"[HUB_TERRITORIO] Fundo do Boris definido do bg do território")
            else:
                # Se bg não existe, tentar carregar diretamente
                caminho_fundo_boris = obter_fundo_territorio(territorio_id, territorio.npc_id, sprite_fundo)
                if caminho_fundo_boris and os.path.exists(caminho_fundo_boris):
                    try:
                        boris.sprite_fundo = pygame.image.load(caminho_fundo_boris).convert_alpha()
                        boris.sprite_fundo_redimensionado = pygame.transform.scale(boris.sprite_fundo, (LARGURA, ALTURA))
                        print(f"[HUB_TERRITORIO] Fundo do Boris carregado diretamente: {caminho_fundo_boris}")
                    except Exception as e:
                        print(f"[HUB_TERRITORIO] Erro ao carregar fundo do Boris: {e}")
        # Sempre ativar o Boris quando entrar no território
        if not boris.primeira_aparicao_mostrada:
            # Primeira vez: mostrar cutscene de introdução
            mostrar_boris = boris.verificar_aparecer_primeira_vez()
        else:
            # Após a introdução: ativar diálogo/loja diretamente
            boris.ativar_loja_narrativa(on_close_scene_id=None)
            mostrar_boris = True
    
    # Verificar se é território do Slick (beco neon)
    territorio_id_lower = territorio_id.lower()
    slick_em_cooldown = False
    is_beco_neon = "neon" in territorio_id_lower or "slick" in territorio_id_lower
    mostrar_slick = False
    if is_beco_neon:
        # Slick só aparece quando desbloqueado pela narrativa
        from core.mapa_locations import gerenciador_localizacoes
        from core.tempo_jogo import gerenciador_tempo
        beco_neon_desbloqueado = gerenciador_localizacoes.esta_desbloqueado("beco_neon")
        
        if not beco_neon_desbloqueado:
            # Ainda não desbloqueado - mostrar mensagem
            slick_em_cooldown = True
            print(f"[SLICK] Beco Neon não desbloqueado, mostrando mensagem de cooldown")
        else:
            # Verificar se a primeira aparição do Slick já aconteceu (cena ch4_5_meet_slick)
            from core.narrative_system import narrative_system
            primeira_aparicao_aconteceu = "ch4_5_meet_slick" in narrative_system.scenes_visited
            
            if not primeira_aparicao_aconteceu:
                # Primeira aparição ainda não aconteceu - não mostrar mensagem, deixar aparecer na narrativa
                print(f"[SLICK] Primeira aparição ainda não aconteceu (cena ch4_5_meet_slick não visitada), permitindo aparecer na narrativa")
                slick_em_cooldown = False
            else:
                # Primeira aparição já aconteceu - verificar cooldown de 4 dias (similar ao Glub)
                data_atual = gerenciador_tempo.obter_data_atual()
                slick_ultima_aparicao_data = getattr(gerenciador_progresso, 'slick_ultima_aparicao_data', None)
                slick_primeira_aparicao_mostrada = getattr(gerenciador_progresso, 'slick_primeira_aparicao_mostrada', False)
                
                print(f"[SLICK] Primeira aparição já aconteceu. Data atual: {gerenciador_tempo.obter_data_formatada()}, Última aparição: {slick_ultima_aparicao_data}, Primeira aparição mostrada: {slick_primeira_aparicao_mostrada}")
                
                # Se slick_primeira_aparicao_mostrada == False, significa que ainda não visitou o Slick no território após a cena narrativa
                # Nesse caso, verificar se já passou tempo suficiente desde a cena narrativa para mostrar mensagem
                if not slick_primeira_aparicao_mostrada:
                    # Primeira vez após a cena narrativa - permitir aparecer na primeira vez (não mostrar mensagem)
                    print(f"[SLICK] Primeira vez após cena narrativa, permitindo aparecer (não mostrar mensagem)")
                    slick_em_cooldown = False
                else:
                    # Já visitou o Slick antes - verificar cooldown de 4 dias
                    if slick_ultima_aparicao_data is None:
                        # Se slick_ultima_aparicao_data ainda é None mas já mostrou primeira aparição, algo está errado
                        # Mas vamos tratar como se estivesse em cooldown para mostrar a mensagem
                        print(f"[SLICK] Primeira aparição já mostrada mas slick_ultima_aparicao_data é None, mostrando mensagem")
                        slick_em_cooldown = True
                    else:
                        from datetime import datetime
                        ultima_aparicao = datetime.strptime(slick_ultima_aparicao_data, "%Y-%m-%d").date()
                        dias_desde_ultima_aparicao = (data_atual - ultima_aparicao).days
                        print(f"[SLICK] Dias desde última aparição: {dias_desde_ultima_aparicao}")
                        
                        # Se não passaram 4 dias desde a última aparição, mostrar mensagem de cooldown
                        if dias_desde_ultima_aparicao < 4:
                            slick_em_cooldown = True
                            dias_restantes = 4 - dias_desde_ultima_aparicao
                            print(f"[SLICK] Em cooldown: {dias_desde_ultima_aparicao}/4 dias passados, faltam {dias_restantes} dias")
                        else:
                            # Pode aparecer - atualizar última aparição quando aparecer
                            # Isso será feito quando a loja for aberta (via narrativa ou diretamente)
                            print(f"[SLICK] Não está em cooldown, pode aparecer")
                            slick_em_cooldown = False
    
    # Verificar se é território do Glub (beco da sucata) - NÃO incluir beco_neon
    glub_em_cooldown = False
    mostrar_glub = False
    # IMPORTANTE: Só processar Glub se foi desbloqueado pela narrativa (cena ch4_4_meet_glub)
    glub_desbloqueado = getattr(gerenciador_progresso, 'glub_desbloqueado', False)
    if not is_beco_neon and glub_desbloqueado and ((territorio.npc_id and ("glub" in territorio.npc_id.lower() or ("beco" in territorio.npc_id.lower() and "sucata" in territorio.npc_id.lower()))) or \
       ("glub" in territorio_id_lower or ("beco" in territorio_id_lower and "sucata" in territorio_id_lower))):
        if not glub.sprites_carregados:
            glub.carregar_sprites()
        
        # Verificar se deve mostrar Glub (primeira aparição ou após cooldown)
        mostrar_glub = glub.verificar_aparecer_primeira_vez()
        if mostrar_glub:
            # A última aparição já é atualizada dentro de verificar_aparecer_primeira_vez()
            pass
        else:
            # Verificar se está em cooldown
            from core.tempo_jogo import gerenciador_tempo
            data_atual = gerenciador_tempo.obter_data_atual()
            ultima_aparicao_data = getattr(gerenciador_progresso, 'glub_ultima_aparicao_data', None)
            
            # Calcular dias desde última aparição
            dias_desde_ultima_aparicao = 999  # Valor alto se nunca apareceu
            if ultima_aparicao_data:
                from datetime import datetime
                ultima_aparicao = datetime.strptime(ultima_aparicao_data, "%Y-%m-%d").date()
                dias_desde_ultima_aparicao = (data_atual - ultima_aparicao).days
            
            # Se já foi apresentado e está em cooldown
            if glub.primeira_aparicao_feita and dias_desde_ultima_aparicao < 4:
                glub_em_cooldown = True
                dias_restantes = 4 - dias_desde_ultima_aparicao
                print(f"[GLUB] Em cooldown: {dias_desde_ultima_aparicao}/4 dias passados, faltam {dias_restantes} dias")
    
    # Verificar se é território do Pixel e mostrar primeira aparição
    from core.pixel import pixel
    mostrar_pixel = False
    if territorio.npc_id and "pixel" in territorio.npc_id.lower():
        mostrar_pixel = pixel.verificar_aparecer_primeira_vez()
    
    # Verificar se é território da Akira (Montanha)
    # IMPORTANTE: Só usar sistema antigo da Akira se não houver gatilho narrativo
    from core.akira import akira
    mostrar_akira = False
    if territorio.npc_id and "akira" in territorio.npc_id.lower():
        # Recarregar estado da Akira para garantir que está atualizado
        akira.carregar_estado()
        
        # Verificar se há gatilho narrativo primeiro (prioridade)
        from core.narrative_system import narrative_system
        from core.progresso import gerenciador_progresso
        location_id = location_map.get(territorio_id.lower(), territorio_id.lower())
        context_akira = {"locationId": location_id}
        gatilho_narrativo_akira = narrative_system.verificar_gatilhos_pendentes(context_akira)
        
        # Verificar se a primeira aparição já foi mostrada (via narrativa ou sistema antigo)
        primeira_aparicao_ja_mostrada = akira.primeira_aparicao_mostrada or (hasattr(gerenciador_progresso, 'akira_primeira_aparicao_mostrada') and gerenciador_progresso.akira_primeira_aparicao_mostrada)
        
        if not gatilho_narrativo_akira or primeira_aparicao_ja_mostrada:
            # Não há gatilho narrativo OU a primeira aparição já foi mostrada (via narrativa)
            # Usar sistema antigo da Akira para oferecer corrida
            # Verificar se a montanha está desbloqueada
            from core.mapa_locations import gerenciador_localizacoes
            if gerenciador_localizacoes.esta_desbloqueado("montanha"):
                # Carregar sprites se necessário
                if not akira.sprites_carregados:
                    akira.carregar_sprites()
                
                # Se é primeira vez, mostrar apresentação
                if not primeira_aparicao_ja_mostrada:
                    mostrar_akira = akira.verificar_aparecer_primeira_vez()
                else:
                    # Já foi apresentado (via narrativa ou sistema antigo) - ativar diálogo da Akira para oferecer corrida
                    mostrar_akira = akira.ativar_dialogo_corrida()
                    # Se ativar_dialogo_corrida retornou False (sem pneus), retornar ao mapa imediatamente
                    if not mostrar_akira:
                        print(f"[HUB_TERRITORIO] Akira não pode ativar diálogo (sem pneus), retornando ao mapa")
                        return "voltar_mapa"
            else:
                # Montanha ainda não desbloqueada
                mostrar_akira = False
        else:
            # Há gatilho narrativo E primeira aparição ainda não foi mostrada
            # Usar sistema de narrativa
            mostrar_akira = False
            print(f"[HUB_TERRITORIO] Gatilho narrativo detectado para Akira, usando sistema de narrativa")
    
    # Verificar se é território do Barão (Iate)
    from core.barao import barao
    mostrar_barao = False
    if territorio.npc_id and "barao" in territorio.npc_id.lower():
        # Carregar sprites se necessário
        if not barao.sprites_carregados:
            barao.carregar_sprites()
        
        # Verificar se o Barão já foi apresentado pela narrativa (ch2_2_barao_offer)
        from core.narrative_system import narrative_system
        barao_ja_apresentado = "ch2_2_barao_offer" in narrative_system.scenes_visited
        
        if barao_ja_apresentado:
            # Já foi apresentado pela narrativa - sempre ativar o Barão quando entrar no iate
            # O Barão decidirá qual diálogo mostrar baseado no estado do empréstimo
            if not barao.ativo:
                # Verificar qual diálogo deve ser mostrado
                if gerenciador_progresso.barao_emprestimo_ativo:
                    # Há empréstimo ativo - verificar se deve mostrar cobrança ou lembrete
                    if barao.verificar_aparecer_cobranca():
                        mostrar_barao = True
                    elif barao.verificar_aparecer_lembrete():
                        mostrar_barao = True
                    else:
                        # Mostrar diálogo padrão
                        barao.ativo = True
                        barao.fase_dialogo = "neutro"
                        barao.sprite_atual = barao.sprite_neutro
                        barao._iniciar_animacao_texto("Mrrr... O que você quer?")
                        mostrar_barao = True
                else:
                    # Não há empréstimo ativo - sempre mostrar diálogo de visita com oferta de empréstimo
                    if barao.ativar_dialogo_visita():
                        mostrar_barao = True
            else:
                # Barão já está ativo
                mostrar_barao = True
        else:
            # Ainda não foi apresentado - deixar a narrativa lidar com isso
            mostrar_barao = False
    
    # Verificar se é território do Glub
    # (mostrar_glub já foi inicializado acima)
    if territorio.npc_id and "glub" in territorio.npc_id.lower():
        if not glub.sprites_carregados:
            glub.carregar_sprites()
        if not glub.primeira_aparicao_feita:
            mostrar_glub = glub.verificar_aparecer_primeira_vez()
        else:
            glub.ativo = True
            glub.fase_dialogo = "loja"
            mostrar_glub = True
    
    # Verificar se é território do Fuligem (Cinturão Industrial)
    from core.fuligem import fuligem
    mostrar_fuligem = False
    if territorio.npc_id and "fuligem" in territorio.npc_id.lower():
        # Carregar sprites se necessário
        if not fuligem.sprites_carregados:
            fuligem.carregar_sprites()
        
        # Verificar se é noite (18h-6h)
        if not fuligem.verificar_horario_noite():
            # Não é noite, mostrar mensagem de bloqueio
            fuligem.ativo = True
            fuligem.fase_dialogo = "dia"
            fuligem.sprite_atual = fuligem.sprite_irritado or fuligem.sprite_neutro
            fuligem._iniciar_animacao_texto("Eles não fariam corridas assim de dia...")
            mostrar_fuligem = True
        elif not fuligem.primeira_aparicao_mostrada:
            # Primeira vez - mostrar apresentação
            mostrar_fuligem = fuligem.verificar_aparecer_primeira_vez()
        else:
            # Já foi apresentado - ativar menu de corridas
            mostrar_fuligem = fuligem.ativar_corrida()
    
    # Estado de pause
    hub_pausado = False
    opcao_pausa_selecionada = 0
    
    # Estado de feedback de salvamento
    mostrar_mensagem_salvo = False
    tempo_mensagem_salvo = 0.0
    
    # Estado de mensagem de cooldown do Glub
    mostrar_mensagem_cooldown_glub = glub_em_cooldown
    # Estado de mensagem de cooldown do Slick
    mostrar_mensagem_cooldown_slick = slick_em_cooldown
    print(f"[HUB_TERRITORIO] slick_em_cooldown={slick_em_cooldown}, mostrar_mensagem_cooldown_slick={mostrar_mensagem_cooldown_slick}, is_beco_neon={is_beco_neon}")
    
    # Rastrear estado dia/noite para recarregar backgrounds quando mudar
    from config import obter_estado_dia_noite
    estado_dia_noite_anterior = obter_estado_dia_noite()
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        tempo_animacao += dt
        
        # Atualizar tempo do jogo (1 minuto real = 1 hora do jogo)
        from core.tempo_jogo import gerenciador_tempo
        gerenciador_tempo.atualizar(dt)
        
        # Verificar se o estado dia/noite mudou e recarregar background se necessário
        estado_dia_noite_atual = obter_estado_dia_noite()
        if estado_dia_noite_atual != estado_dia_noite_anterior:
            estado_dia_noite_anterior = estado_dia_noite_atual
            # Recarregar fundo do território (pode ter mudado para noite)
            caminho_fundo = obter_fundo_territorio(territorio_id, territorio.npc_id if territorio else None, sprite_fundo)
            if caminho_fundo and os.path.exists(caminho_fundo):
                try:
                    bg_raw = pygame.image.load(caminho_fundo).convert_alpha()
                    bg = pygame.transform.scale(bg_raw, (LARGURA, ALTURA))
                    print(f"[HUB_TERRITORIO] Background recarregado para {estado_dia_noite_atual}")
                except Exception as e:
                    print(f"Erro ao recarregar fundo do território: {e}")
        
        # Atualizar mensagem de salvamento
        if mostrar_mensagem_salvo:
            tempo_mensagem_salvo += dt
            if tempo_mensagem_salvo >= 2.0:  # Mostrar por 2 segundos
                mostrar_mensagem_salvo = False
                tempo_mensagem_salvo = 0.0
        
        # Coletar eventos uma vez para todos os processamentos
        eventos = pygame.event.get()
        eventos_para_boris = []  # Eventos que não foram consumidos pelo pause/celular
        
        # Processar pause primeiro (mesmo quando NPCs estão ativos)
        pause_consumiu_evento = False
        for ev in eventos:
            evento_consumido = False
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    # Alternar pause (funciona mesmo com NPCs ativos)
                    hub_pausado = not hub_pausado
                    if hub_pausado:
                        opcao_pausa_selecionada = 0
                    evento_consumido = True
                    pause_consumiu_evento = True
                elif hub_pausado:
                    # Processar navegação no menu de pause
                    if ev.key in (pygame.K_UP, pygame.K_w):
                        opcao_pausa_selecionada = (opcao_pausa_selecionada - 1) % 4
                        evento_consumido = True
                    elif ev.key in (pygame.K_DOWN, pygame.K_s):
                        opcao_pausa_selecionada = (opcao_pausa_selecionada + 1) % 4
                        evento_consumido = True
                    elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        # Selecionar opção do pause
                        if opcao_pausa_selecionada == 0:
                            hub_pausado = False
                        elif opcao_pausa_selecionada == 1:
                            from core.progresso import gerenciador_progresso
                            gerenciador_progresso.salvar()
                            hub_pausado = False
                        elif opcao_pausa_selecionada == 2:
                            hub_pausado = False
                        elif opcao_pausa_selecionada == 3:
                            return "menu_principal"
                        evento_consumido = True
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and hub_pausado:
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
                
                for i, (nome, chave) in enumerate(opcoes_pausa):
                    y_opcao = offset_opcoes + i * 60
                    opcao_rect = pygame.Rect(caixa_x + 20, y_opcao - 5, caixa_largura - 40, 60)
                    if opcao_rect.collidepoint(mouse_x, mouse_y):
                        if i == 0:
                            hub_pausado = False
                        elif i == 1:
                            from core.progresso import gerenciador_progresso
                            gerenciador_progresso.salvar()
                            hub_pausado = False
                        elif i == 2:
                            hub_pausado = False
                        elif i == 3:
                            return "menu_principal"
                        evento_consumido = True
                        break
            
            # Se o evento não foi consumido pelo pause, adicionar à lista para o Boris
            if not evento_consumido:
                eventos_para_boris.append(ev)
        
        # Processar Boris se ativo (mas não se estiver pausado)
        if mostrar_boris and boris.ativo and not hub_pausado:
            boris.atualizar(dt)
            resultado_boris = boris.processar_eventos(eventos_para_boris)
            if resultado_boris == "fechado":
                # Salvar progresso após fechar diálogo do Boris
                from core.progresso import gerenciador_progresso
                from core.missoes import gerenciador_missoes
                gerenciador_progresso.salvar()
                gerenciador_missoes.salvar()
                mostrar_boris = False
                # Sempre voltar para o mapa após fechar o diálogo do Boris
                return "voltar_mapa"
            elif resultado_boris == "abrir_loja":
                # Abrir loja do Boris (implementar depois)
                mostrar_boris = False
                # Voltar para o mapa após fechar a loja
                return "voltar_mapa"
        
        # Processar Pixel se ativo
        if mostrar_pixel and pixel.ativo:
            pixel.atualizar(dt)
            resultado_pixel = pixel.processar_eventos(eventos)
            if resultado_pixel == "fechado":
                # Salvar progresso após fechar diálogo do Pixel
                from core.progresso import gerenciador_progresso
                from core.missoes import gerenciador_missoes
                gerenciador_progresso.salvar()
                gerenciador_missoes.salvar()
                mostrar_pixel = False
                # Retornar ao mapa da cidade após fechar o Pixel
                return "voltar_mapa"
            elif resultado_pixel == "abrir_loja":
                # Abrir menu de desbloqueios do Pixel
                pixel.ativar_menu_desbloqueios()
                mostrar_pixel = True  # Manter Pixel ativo para mostrar o menu
        
        # Processar Glub se ativo
        if mostrar_glub and glub.ativo:
            glub.atualizar(dt)
            resultado_glub = glub.processar_eventos(eventos)
            if resultado_glub == "fechado":
                # Salvar progresso após fechar diálogo do Glub
                from core.progresso import gerenciador_progresso
                from core.missoes import gerenciador_missoes
                gerenciador_progresso.salvar()
                gerenciador_missoes.salvar()
                mostrar_glub = False
                return "voltar_mapa"
        
        # Processar Fuligem se ativo
        if mostrar_fuligem and fuligem.ativo:
            fuligem.atualizar(dt)
            resultado_fuligem = fuligem.processar_eventos(eventos)
            if resultado_fuligem == "fechado":
                # Salvar progresso após fechar diálogo do Fuligem
                from core.progresso import gerenciador_progresso
                from core.missoes import gerenciador_missoes
                gerenciador_progresso.salvar()
                gerenciador_missoes.salvar()
                
                # Se acabou de completar a primeira aparição, ativar menu de corridas automaticamente
                if fuligem.primeira_aparicao_mostrada and fuligem.verificar_horario_noite():
                    mostrar_fuligem = fuligem.ativar_corrida()
                else:
                    mostrar_fuligem = False
            elif isinstance(resultado_fuligem, dict) and resultado_fuligem.get("corrida"):
                # Iniciar corrida do Cinturão Industrial
                pista = resultado_fuligem.get("pista")
                if pista:
                    # Retornar informação da corrida para ser processada
                    return {
                        "atividade": "corrida_cinturao",
                        "nome": f"Corrida Cinturão Industrial - Pista {pista}",
                        "territorio_id": territorio_id,
                        "npc_id": territorio.npc_id,
                        "pista": pista,
                        "preco": resultado_fuligem.get("preco", 800),
                        "recompensa": resultado_fuligem.get("recompensa", 0),
                        "indice": resultado_fuligem.get("indice", 0)
                    }
                mostrar_fuligem = False
        
        # Processar Barão se ativo
        if mostrar_barao and barao.ativo:
            barao.atualizar(dt)
            resultado_barao = barao.processar_eventos(eventos)
            if resultado_barao == "fechado":
                # Salvar progresso após fechar diálogo do Barão
                from core.progresso import gerenciador_progresso
                from core.missoes import gerenciador_missoes
                gerenciador_progresso.salvar()
                gerenciador_missoes.salvar()
                mostrar_barao = False
                # Retornar ao mapa após fechar o diálogo do Barão
                return "voltar_mapa"
        
        # Processar Akira se ativa
        if mostrar_akira and akira.ativo:
            # IMPORTANTE: Capturar o modo ANTES de processar eventos, pois fechar() reseta o modo
            modo_antes_processar = akira.modo_dialogo
            akira.atualizar(dt)
            resultado_akira = akira.processar_eventos(eventos)
            
            # PRIMEIRO: Verificar se a Akira retornou um dicionário com corrida (prioridade máxima)
            if isinstance(resultado_akira, dict) and resultado_akira.get("corrida"):
                # Iniciar corrida da Akira
                pista = resultado_akira.get("pista", 3)
                # Definir flag de corrida campanha antes de retornar
                from core.progresso import gerenciador_progresso
                race_id = resultado_akira.get("race_id", "mountain_test")
                # Aceitar tanto mountain_test quanto mountain_test_run
                if race_id in ["mountain_test", "mountain_test_run"]:
                    # Usar mountain_test_run para compatibilidade com a narrativa
                    gerenciador_progresso.ultima_corrida_campanha = "mountain_test_run"
                    gerenciador_progresso.salvar()
                    print(f"[HUB_TERRITORIO] Corrida da Akira aceita: race_id={race_id}, pista={pista}")
                return {
                    "atividade": resultado_akira.get("tipo", "desafio_touge"),
                    "nome": resultado_akira.get("nome", "Desafio de Montanha (Touge)"),
                    "territorio_id": territorio_id,
                    "npc_id": territorio.npc_id,
                    "pista": pista,
                    "race_id": race_id,
                    "voltas": resultado_akira.get("voltas", 1),
                    "dificuldade": resultado_akira.get("dificuldade", "medio"),
                    "sem_bots": resultado_akira.get("sem_bots", False)
                }
            
            # SEGUNDO: Verificar se a Akira fechou sem retornar "fechado" (pode acontecer quando fecha por falta de pneus)
            if not akira.ativo and mostrar_akira:
                print(f"[HUB_TERRITORIO] Akira fechou sem retornar 'fechado' (provavelmente sem pneus), retornando ao mapa")
                mostrar_akira = False
                # Se acabou de completar a primeira aparição, tentar ativar diálogo de corrida
                if akira.primeira_aparicao_mostrada and modo_antes_processar == "primeira_aparicao":
                    mostrar_akira = akira.ativar_dialogo_corrida()
                    if not mostrar_akira:
                        return "voltar_mapa"
                else:
                    return "voltar_mapa"
            
            # TERCEIRO: Verificar se retornou "fechado"
            if resultado_akira == "fechado":
                # Salvar progresso após fechar diálogo da Akira
                from core.progresso import gerenciador_progresso
                from core.missoes import gerenciador_missoes
                gerenciador_progresso.salvar()
                gerenciador_missoes.salvar()
                
                mostrar_akira = False
                
                # Se acabou de completar a primeira aparição E o modo não era "corrida" (ou seja, não estava no menu de corridas),
                # verificar se deve oferecer corrida (transição automática)
                if akira.primeira_aparicao_mostrada and modo_antes_processar != "corrida" and not akira.ativo:
                    # Tentar ativar diálogo de corrida novamente (transição automática após primeira aparição)
                    mostrar_akira = akira.ativar_dialogo_corrida()
                    if not mostrar_akira:
                        # Se não conseguiu ativar (sem pneus), voltar ao mapa
                        return "voltar_mapa"
                else:
                    # Akira fechou normalmente (jogador escolheu SAIR ou ESC do menu de corridas), voltar ao mapa
                    # NÃO reativar o diálogo se o jogador escolheu sair explicitamente
                    return "voltar_mapa"
        
        # Processar eventos do celular (sempre, mesmo com NPCs ativos, mas não quando pausado)
        celular_processou_evento = False
        try:
            from core.celular import celular
            from core.narrative_system import narrative_system
            
            # Verificar se deve mostrar celular (modo campanha, sem cutscenes)
            # NÃO mostrar celular quando há cutscene ativa ou NPCs ativos
            npc_ativo = (mostrar_boris and boris.ativo) or (mostrar_pixel and pixel.ativo) or \
                       (mostrar_fuligem and fuligem.ativo) or (mostrar_akira and akira.ativo) or \
                       (mostrar_barao and barao.ativo) or (mostrar_glub and glub.ativo)
            cutscene_ativa = narrative_system.active if hasattr(narrative_system, 'active') else False
            # NÃO mostrar celular quando há cutscene ativa ou NPCs ativos
            celular.verificar_visibilidade(modo_arcade=False, em_corrida=False, cutscene_ativa=cutscene_ativa or npc_ativo)
            
            # Processar eventos do celular sempre (mas não quando pausado)
            if not hub_pausado:
                for ev in eventos:
                    # Se o menu está aberto, processar todos os eventos do celular
                    if celular.menu_aberto:
                        resultado_celular = celular.processar_eventos([ev])
                        if resultado_celular == "fechado":
                            celular.menu_aberto = False
                        # Se o celular processou o evento, marcar como processado
                        if resultado_celular:
                            celular_processou_evento = True
                            # Se ESC foi pressionado, não processar outros eventos
                            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                                break
                    elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                        # Se o menu não está aberto, verificar se clicou no celular
                        if celular.processar_clique(ev.pos):
                            # Celular foi clicado, processar eventos do menu
                            resultado_celular = celular.processar_eventos([ev])
                            if resultado_celular == "fechado":
                                celular.menu_aberto = False
                                celular_processou_evento = True
                            break  # Não processar outros eventos se o celular foi clicado
        except Exception as e:
            print(f"[HUB_TERRITORIO] Erro ao processar celular: {e}")
            import traceback
            traceback.print_exc()
        
        # Processar eventos (apenas se Boris/Pixel/Fuligem/Akira/Glub não estiverem ativos, para evitar processamento duplo)
        # IMPORTANTE: Se Fuligem está ativo, não processar ESC aqui para evitar conflito
        if not (mostrar_boris and boris.ativo) and not (mostrar_pixel and pixel.ativo) and not (mostrar_fuligem and fuligem.ativo) and not (mostrar_akira and akira.ativo) and not (mostrar_glub and glub.ativo):
            # Se o celular processou um evento importante, pular processamento de outros eventos
            if celular_processou_evento and celular.menu_aberto:
                pass  # Não processar outros eventos se o menu do celular está aberto
            else:
                for ev in eventos:
                    if ev.type == pygame.QUIT:
                        return "menu_principal"  # Fechar jogo vai para menu principal
                    
                    if ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_ESCAPE:
                            # Se estiver mostrando mensagem de cooldown, ESC fecha e volta ao mapa
                            if mostrar_mensagem_cooldown_glub:
                                mostrar_mensagem_cooldown_glub = False
                                return "voltar_mapa"
                            # Alternar pause
                            hub_pausado = not hub_pausado
                            if hub_pausado:
                                opcao_pausa_selecionada = 0
                        elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                            # Se estiver mostrando mensagem de cooldown, ENTER/SPACE fecha e volta ao mapa
                            if mostrar_mensagem_cooldown_glub:
                                mostrar_mensagem_cooldown_glub = False
                                return "voltar_mapa"
                        elif hub_pausado:
                            # Processar navegação no menu de pause
                            if ev.key in (pygame.K_UP, pygame.K_w):
                                opcao_pausa_selecionada = (opcao_pausa_selecionada - 1) % 4
                            elif ev.key in (pygame.K_DOWN, pygame.K_s):
                                opcao_pausa_selecionada = (opcao_pausa_selecionada + 1) % 4
                    
                    if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                        mouse_x, mouse_y = ev.pos
                        if hub_pausado:
                            # Processar clique no menu de pause
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
                                            hub_pausado = False
                                        elif i == 1:
                                            # Salvar
                                            from core.progresso import gerenciador_progresso
                                            gerenciador_progresso.salvar()
                                            mostrar_mensagem_salvo = True
                                            tempo_mensagem_salvo = 0.0
                                            hub_pausado = False
                                    elif i == 2:
                                        # Opções (por enquanto, apenas continuar)
                                        hub_pausado = False
                                    elif i == 3:
                                        # Menu principal
                                        return "menu_principal"
                                    break
                            continue  # Não processar outros cliques quando pausado
                        
                        # Verificar clique no botão voltar (antes de verificar atividades)
                        voltar_largura = 120
                        voltar_altura = 40
                        voltar_x = LARGURA - voltar_largura - 20
                        voltar_y = 20
                        voltar_rect = pygame.Rect(voltar_x, voltar_y, voltar_largura, voltar_altura)
                        if voltar_rect.collidepoint(mouse_x, mouse_y):
                            return "voltar_mapa"  # Voltar para o mapa
        
        # Verificar mensagem de cooldown do Slick ANTES de desenhar qualquer coisa (prioridade máxima)
        if mostrar_mensagem_cooldown_slick:
            # Criar uma versão customizada que preserva o background
            render_text = _get_render_text()
            clock_cooldown = pygame.time.Clock()
            tempo_decorrido = 0.0
            mensagem = "Acho que ele não está por aqui hoje..."
            
            # Quebrar mensagem em linhas
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
            caixa_altura = len(linhas) * altura_linha + padding * 2 + 50
            caixa_x = (LARGURA - caixa_largura) // 2
            caixa_y = ALTURA - caixa_altura - 100
            
            fechou = False
            while not fechou:
                dt_cooldown = clock_cooldown.tick(FPS) / 1000.0
                tempo_decorrido += dt_cooldown
                
                eventos_cooldown = pygame.event.get()
                for ev in eventos_cooldown:
                    if ev.type == pygame.QUIT:
                        fechou = True
                    if ev.type == pygame.KEYDOWN:
                        if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                            fechou = True
                    if ev.type == pygame.MOUSEBUTTONDOWN:
                        if ev.button == 1:
                            fechou = True
                
                # Desenhar background primeiro
                if bg:
                    screen.blit(bg, (0, 0))
                
                # Overlay semi-transparente (mais claro para não esconder o background)
                overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 100))  # Mais transparente (100 ao invés de 150)
                screen.blit(overlay, (0, 0))
                
                # Caixa de mensagem
                caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
                caixa_fundo.fill((0, 0, 0, 220))
                screen.blit(caixa_fundo, (caixa_x, caixa_y))
                pygame.draw.rect(screen, (150, 150, 150), (caixa_x, caixa_y, caixa_largura, caixa_altura), 2)
                
                # Texto
                y_texto = caixa_y + padding
                for linha in linhas:
                    linha_render = render_text(linha, 20, (255, 255, 255), bold=False, pixel_style=True)
                    screen.blit(linha_render, (caixa_x + padding, y_texto))
                    y_texto += altura_linha
                
                instrucao = render_text("Pressione ESPAÇO ou clique para continuar", 14, (200, 200, 200), bold=False, pixel_style=True)
                instrucao_x = caixa_x + (caixa_largura - instrucao.get_width()) // 2
                screen.blit(instrucao, (instrucao_x, caixa_y + caixa_altura - 30))
                
                pygame.display.flip()
            
            mostrar_mensagem_cooldown_slick = False
            return "voltar_mapa"
        # Desenhar fundo apenas se nenhum NPC estiver ativo (NPCs desenham seus próprios fundos)
        # EXCEÇÃO: Akira em primeira_aparicao, sem_preparo e corrida precisam do fundo do território
        # EXCEÇÃO: Barão desenha seu próprio fundo (iate), então não desenhar fundo do território quando ele estiver ativo
        # EXCEÇÃO: Glub precisa do fundo do território (desenha overlay escuro por cima)
        # EXCEÇÃO: Boris precisa do fundo do território (fábrica) - ele desenha sobre o fundo
        desenhar_fundo = True
        if (mostrar_pixel and pixel.ativo) or (mostrar_fuligem and fuligem.ativo):
            desenhar_fundo = False
        # Boris precisa do fundo do território, então manter desenhar_fundo = True mesmo quando ativo
        # Mas garantir que o Boris carregue o fundo antes de desenhar
        if mostrar_boris and boris.ativo and not boris.sprite_fundo_redimensionado:
            # Carregar fundo do Boris se ainda não estiver carregado
            caminho_fundo_boris = obter_fundo_territorio(territorio_id, territorio.npc_id, sprite_fundo)
            if caminho_fundo_boris and os.path.exists(caminho_fundo_boris):
                try:
                    boris.sprite_fundo = pygame.image.load(caminho_fundo_boris).convert_alpha()
                    boris.sprite_fundo_redimensionado = pygame.transform.scale(boris.sprite_fundo, (LARGURA, ALTURA))
                    print(f"[HUB_TERRITORIO] Fundo do Boris carregado: {caminho_fundo_boris}")
                except Exception as e:
                    print(f"[HUB_TERRITORIO] Erro ao carregar fundo do Boris: {e}")
        elif mostrar_barao and barao.ativo:
            # Barão desenha seu próprio fundo (iate), então não desenhar fundo do território
            desenhar_fundo = False
        elif mostrar_akira and akira.ativo:
            # Akira precisa do fundo do território para primeira_aparicao, sem_preparo e corrida
            # Apenas pre_corrida e fim_corrida têm seus próprios fundos
            if akira.modo_dialogo in ["pre_corrida", "fim_corrida"]:
                desenhar_fundo = False
        # Glub precisa do fundo do território (desenha overlay escuro por cima), então manter desenhar_fundo = True
        # Boris também precisa do fundo do território
        # Sempre desenhar fundo se existir (exceto quando Pixel ou Fuligem estão ativos)
        if bg and not ((mostrar_pixel and pixel.ativo) or (mostrar_fuligem and fuligem.ativo)):
            screen.blit(bg, (0, 0))
        
        # Desenhar Akira se ativa (prioridade sobre outros NPCs)
        if mostrar_akira and akira.ativo:
            akira.desenhar_dialogo(screen, dt)
            pygame.display.flip()
            continue  # Pular o resto do desenho se Akira estiver ativa
        
        # Desenhar Barão se ativo
        if mostrar_barao and barao.ativo:
            barao.desenhar_dialogo(screen, dt)
            pygame.display.flip()
            continue  # Pular o resto do desenho se Barão estiver ativo
        
        # Verificar se o Barão foi fechado após aceitar/recusar (mas ainda está sendo desenhado)
        if not mostrar_barao and not barao.ativo and barao.fase_dialogo in ["aceito", "recusado"]:
            # Retornar ao mapa se o Barão foi fechado após aceitar ou recusar
            return "voltar_mapa"
        
        # Desenhar Boris se ativo (ele desenha sobre o fundo do território)
        if mostrar_boris and boris.ativo:
            # Garantir que o fundo do Boris está carregado
            if not boris.sprite_fundo_redimensionado:
                # Tentar usar o bg que já foi carregado
                if bg:
                    # Criar uma cópia do bg para o Boris
                    boris.sprite_fundo_redimensionado = bg.copy()
                    print(f"[HUB_TERRITORIO] Fundo do Boris definido do bg do território")
                else:
                    # Se bg não existe, tentar carregar diretamente
                    caminho_fundo_boris = obter_fundo_territorio(territorio_id, territorio.npc_id, sprite_fundo)
                    if caminho_fundo_boris and os.path.exists(caminho_fundo_boris):
                        try:
                            boris.sprite_fundo = pygame.image.load(caminho_fundo_boris).convert_alpha()
                            boris.sprite_fundo_redimensionado = pygame.transform.scale(boris.sprite_fundo, (LARGURA, ALTURA))
                            print(f"[HUB_TERRITORIO] Fundo do Boris carregado diretamente: {caminho_fundo_boris}")
                        except Exception as e:
                            print(f"[HUB_TERRITORIO] Erro ao carregar fundo do Boris: {e}")
            boris.desenhar_dialogo(screen, dt)
            
            # Desenhar celular mesmo quando Boris está ativo (mas não quando pausado)
            if not hub_pausado:
                try:
                    from core.celular import celular
                    mouse_pos = pygame.mouse.get_pos()
                    celular.atualizar(dt, mouse_pos)
                    celular.desenhar(screen)
                except Exception as e:
                    print(f"[HUB_TERRITORIO] Erro ao desenhar celular: {e}")
            
            # Desenhar menu de pause se estiver pausado (mesmo com Boris ativo)
            if hub_pausado:
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
                if not hasattr(hub_territorio_loop, '_hover_animation_pause_boris'):
                    hub_territorio_loop._hover_animation_pause_boris = [0.0] * len(opcoes_pausa)
                
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
                        hub_territorio_loop._hover_animation_pause_boris[i] = min(1.0, hub_territorio_loop._hover_animation_pause_boris[i] + hover_speed * dt)
                    else:
                        hub_territorio_loop._hover_animation_pause_boris[i] = max(0.0, hub_territorio_loop._hover_animation_pause_boris[i] - hover_speed * dt)
                
                if not mouse_in_caixa:
                    for i in range(len(opcoes_pausa)):
                        if i != opcao_pausa_selecionada:
                            hub_territorio_loop._hover_animation_pause_boris[i] = max(0.0, hub_territorio_loop._hover_animation_pause_boris[i] - hover_speed * dt * 1.5)
                
                # Desenhar opções
                import math
                for i, (nome, chave) in enumerate(opcoes_pausa):
                    y_opcao = offset_opcoes + i * 60
                    hover_progress = hub_territorio_loop._hover_animation_pause_boris[i]
                    
                    # Determinar cor baseado no estado
                    if i == opcao_pausa_selecionada:
                        cor = (255, 255, 255)
                        # Desenhar cursor do controle
                        cursor_rect = pygame.Rect(caixa_x + 20, y_opcao - 5, caixa_largura - 40, 60)
                        pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                        cursor_alpha = int(128 + 127 * abs(math.sin(tempo_animacao * 3.0 * math.pi)))
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
            continue  # Pular o resto do desenho se Boris estiver ativo
        
        # Desenhar Pixel se ativo
        if mostrar_pixel and pixel.ativo:
            # Garantir que os sprites estão carregados antes de desenhar
            if not pixel.sprites_carregados:
                pixel.carregar_sprites()
            # Garantir que o nome está revelado se já passou da primeira aparição
            pixel.carregar_estado()
            if pixel.primeira_aparicao_mostrada and not pixel.nome_revelado:
                pixel.nome_revelado = True
                pixel.salvar_estado()
            # Garantir que o sprite está definido
            if not pixel.sprite_atual:
                pixel.sprite_atual = pixel.sprite_neutro if pixel.sprite_neutro else pixel.sprite_digitando
            pixel.desenhar_dialogo(screen, dt)
            pygame.display.flip()
            continue  # Pular o resto do desenho se Pixel estiver ativo
        
        # Verificar se o Pixel foi fechado sem retornar "fechado" explicitamente
        if not pixel.ativo and mostrar_pixel:
            print(f"[HUB_TERRITORIO] Pixel fechou, retornando ao mapa")
            mostrar_pixel = False
            # Salvar progresso antes de voltar
            from core.progresso import gerenciador_progresso
            from core.missoes import gerenciador_missoes
            gerenciador_progresso.salvar()
            gerenciador_missoes.salvar()
            return "voltar_mapa"
        
        # Desenhar Fuligem se ativo
        if mostrar_fuligem and fuligem.ativo:
            fuligem.desenhar_dialogo(screen, dt)
            pygame.display.flip()
            continue  # Pular o resto do desenho se Fuligem estiver ativo
        
        # Desenhar mensagem de cooldown do Glub se necessário
        if mostrar_mensagem_cooldown_glub:
            # Criar uma versão customizada que preserva o background
            render_text = _get_render_text()
            clock_cooldown = pygame.time.Clock()
            tempo_decorrido = 0.0
            mensagem = "Acho que ele não está aqui hoje..."
            
            # Quebrar mensagem em linhas
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
            caixa_altura = len(linhas) * altura_linha + padding * 2 + 50
            caixa_x = (LARGURA - caixa_largura) // 2
            caixa_y = ALTURA - caixa_altura - 100
            
            fechou = False
            while not fechou:
                dt_cooldown = clock_cooldown.tick(FPS) / 1000.0
                tempo_decorrido += dt_cooldown
                
                eventos_cooldown = pygame.event.get()
                for ev in eventos_cooldown:
                    if ev.type == pygame.QUIT:
                        fechou = True
                    if ev.type == pygame.KEYDOWN:
                        if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                            fechou = True
                    if ev.type == pygame.MOUSEBUTTONDOWN:
                        if ev.button == 1:
                            fechou = True
                
                # Desenhar background primeiro
                if bg:
                    screen.blit(bg, (0, 0))
                
                # Overlay semi-transparente (mais claro para não esconder o background)
                overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 100))  # Mais transparente (100 ao invés de 150)
                screen.blit(overlay, (0, 0))
                
                # Caixa de mensagem
                caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
                caixa_fundo.fill((0, 0, 0, 220))
                screen.blit(caixa_fundo, (caixa_x, caixa_y))
                pygame.draw.rect(screen, (150, 150, 150), (caixa_x, caixa_y, caixa_largura, caixa_altura), 2)
                
                # Texto
                y_texto = caixa_y + padding
                for linha in linhas:
                    linha_render = render_text(linha, 20, (255, 255, 255), bold=False, pixel_style=True)
                    screen.blit(linha_render, (caixa_x + padding, y_texto))
                    y_texto += altura_linha
                
                instrucao = render_text("Pressione ESPAÇO ou clique para continuar", 14, (200, 200, 200), bold=False, pixel_style=True)
                instrucao_x = caixa_x + (caixa_largura - instrucao.get_width()) // 2
                screen.blit(instrucao, (instrucao_x, caixa_y + caixa_altura - 30))
                
                pygame.display.flip()
            
            mostrar_mensagem_cooldown_glub = False
            return "voltar_mapa"
        
        # Desenhar Glub se ativo
        if mostrar_glub and glub.ativo:
            glub.desenhar_dialogo(screen, dt)
            pygame.display.flip()
            continue  # Pular o resto do desenho se Glub estiver ativo
        
        # Atualizar e desenhar celular (modo campanha, sem cutscenes, sem NPCs ativos)
        try:
            from core.celular import celular
            from core.narrative_system import narrative_system
            
            # Verificar se deve mostrar celular
            npc_ativo = (mostrar_boris and boris.ativo) or (mostrar_pixel and pixel.ativo) or \
                       (mostrar_fuligem and fuligem.ativo) or (mostrar_akira and akira.ativo) or \
                       (mostrar_glub and glub.ativo)
            cutscene_ativa = narrative_system.active if hasattr(narrative_system, 'active') else False
            celular.verificar_visibilidade(modo_arcade=False, em_corrida=False, cutscene_ativa=cutscene_ativa or npc_ativo)
            
            # Atualizar celular
            mouse_pos = pygame.mouse.get_pos()
            celular.atualizar(dt, mouse_pos)
            
            # Desenhar celular
            celular.desenhar(screen)
        except Exception as e:
            print(f"[HUB_TERRITORIO] Erro ao desenhar celular: {e}")
            import traceback
            traceback.print_exc()
            pass
        
        # Desenhar menu de pause
        if hub_pausado:
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
            if not hasattr(hub_territorio_loop, '_hover_animation_pause'):
                hub_territorio_loop._hover_animation_pause = [0.0] * len(opcoes_pausa)
            
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
                    hub_territorio_loop._hover_animation_pause[i] = min(1.0, hub_territorio_loop._hover_animation_pause[i] + hover_speed * dt)
                else:
                    hub_territorio_loop._hover_animation_pause[i] = max(0.0, hub_territorio_loop._hover_animation_pause[i] - hover_speed * dt)
            
            if not mouse_in_caixa:
                for i in range(len(opcoes_pausa)):
                    if i != opcao_pausa_selecionada:
                        hub_territorio_loop._hover_animation_pause[i] = max(0.0, hub_territorio_loop._hover_animation_pause[i] - hover_speed * dt * 1.5)
            
            # Desenhar opções
            import math
            for i, (nome, chave) in enumerate(opcoes_pausa):
                y_opcao = offset_opcoes + i * 60
                hover_progress = hub_territorio_loop._hover_animation_pause[i]
                
                # Determinar cor baseado no estado
                if i == opcao_pausa_selecionada:
                    cor = (255, 255, 255)
                    # Desenhar cursor do controle
                    cursor_rect = pygame.Rect(caixa_x + 20, y_opcao - 5, caixa_largura - 40, 60)
                    pygame.draw.rect(screen, (0, 200, 255), cursor_rect, 3)
                    cursor_alpha = int(128 + 127 * abs(math.sin(tempo_animacao * 3.0 * math.pi)))
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
            continue  # Pular o resto do desenho quando pausado
        
        # Se nenhum NPC estiver ativo, apenas mostrar fundo (já desenhado acima)
        # NPCs gerenciam suas próprias atividades através de diálogos
        # Não desenhar overlay escuro nem botão voltar quando NPCs estão ativos
        
        # Desenhar mensagem de salvamento
        if mostrar_mensagem_salvo:
            mensagem = render_text("JOGO SALVO!", 36, (0, 255, 0), bold=True, pixel_style=True)
            mensagem_x = (LARGURA - mensagem.get_width()) // 2
            mensagem_y = 100
            
            # Fundo semi-transparente
            fundo_mensagem = pygame.Surface((mensagem.get_width() + 40, mensagem.get_height() + 20), pygame.SRCALPHA)
            fundo_mensagem.fill((0, 0, 0, 180))
            screen.blit(fundo_mensagem, (mensagem_x - 20, mensagem_y - 10))
            
            screen.blit(mensagem, (mensagem_x, mensagem_y))
        
        pygame.display.flip()

