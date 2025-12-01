# src/core/hub_territorio.py
"""
Hub do Território - Tela de ações após selecionar um território no mapa
Mostra o NPC local e lista de atividades disponíveis
"""

import pygame
import os
from typing import Optional, Dict, List
from config import LARGURA, ALTURA, FPS, DIR_PROJETO, obter_caminho_sprite_dia_noite
from core.territorios import obter_territorio, Territorio

# Mapeamento de territórios para sprites de fundo (usando sistema dia/noite)
def obter_caminho_fabrica():
    return obter_caminho_sprite_dia_noite("fabrica")
def obter_caminho_iate_barao():
    return obter_caminho_sprite_dia_noite("iate_barao")
def obter_caminho_monte_akira():
    return obter_caminho_sprite_dia_noite("monte_akira")
def obter_caminho_torre_king():
    return obter_caminho_sprite_dia_noite("predio_rex")
def obter_caminho_bunker():
    return obter_caminho_sprite_dia_noite("bunker")
def obter_caminho_oficina():
    return obter_caminho_sprite_dia_noite("oficina")

# Mantém compatibilidade com código existente
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
        
        # Akira - Monte
        "templo_akira": obter_caminho_monte_akira(),
        "monte_akira": obter_caminho_monte_akira(),
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
    elif "boris" in territorio_id_lower or "fabrica" in territorio_id_lower:
        caminho = obter_caminho_fabrica()
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
    # Se for a casa, usar sistema de point and click
    if territorio_id.lower() == "casa" or (area_nome and "casa" in area_nome.lower()):
        from core.casa import casa_loop
        return casa_loop(screen, sprite_fundo)
    
    territorio = obter_territorio(territorio_id)
    
    # Se não encontrar território, tentar criar um básico baseado no ID
    if not territorio:
        # Verificar se é uma área especial (ex: oficina)
        territorio_id_lower = territorio_id.lower()
        area_nome_lower = (area_nome or "").lower()
        
        if ("oficina" in territorio_id_lower or "garagem" in territorio_id_lower or 
            "crank" in territorio_id_lower or 
            "oficina" in area_nome_lower or "garagem" in area_nome_lower):
            # Redirecionar diretamente para a oficina
            from core.menu import selecionar_carros_loop
            selecionar_carros_loop(screen)
            return "voltar_mapa"  # Voltar para o mapa após sair da oficina
        
        # Criar território temporário
        from core.territorios import Territorio, TipoTerritorio
        territorio = Territorio(
            id=territorio_id,
            nome=area_nome or territorio_id.replace("_", " ").title(),
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
    
    # Lista de atividades
    atividades = territorio.atividades
    atividade_selecionada = 0
    
    # Animações
    tempo_animacao = 0.0
    
    # Verificar se é território do Boris e mostrar primeira aparição / loja
    from core.boris import boris
    from core.progresso import gerenciador_progresso
    mostrar_boris = False
    if territorio.npc_id and "boris" in territorio.npc_id.lower():
        # Verificar capítulo atual - no Capítulo 2+, não mostrar introdução
        capitulo_atual = gerenciador_progresso.obter_capitulo_atual()
        if capitulo_atual and capitulo_atual != "ch1":
            # No Capítulo 2 ou superior, sempre abrir a loja diretamente
            boris.ativar_loja_narrativa(on_close_scene_id=None)
            mostrar_boris = True
        elif not boris.primeira_aparicao_mostrada:
            # Se ainda não vimos a primeira aparição (Capítulo 1), tocar a cutscene normal
            mostrar_boris = boris.verificar_aparecer_primeira_vez()
        else:
            # Após a introdução, ao entrar na Fábrica do Boris já abrir direto a "loja"
            boris.ativar_loja_narrativa(on_close_scene_id=None)
            mostrar_boris = True
    
    # Verificar se é território do Pixel e mostrar primeira aparição
    from core.pixel import pixel
    mostrar_pixel = False
    if territorio.npc_id and "pixel" in territorio.npc_id.lower():
        mostrar_pixel = pixel.verificar_aparecer_primeira_vez()
    
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
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        tempo_animacao += dt
        
        # Atualizar tempo do jogo (1 minuto real = 1 hora do jogo)
        from core.tempo_jogo import gerenciador_tempo
        gerenciador_tempo.atualizar(dt)
        
        # Atualizar mensagem de salvamento
        if mostrar_mensagem_salvo:
            tempo_mensagem_salvo += dt
            if tempo_mensagem_salvo >= 2.0:  # Mostrar por 2 segundos
                mostrar_mensagem_salvo = False
                tempo_mensagem_salvo = 0.0
        
        # Coletar eventos uma vez para todos os processamentos
        eventos = pygame.event.get()
        
        # Processar Boris se ativo
        if mostrar_boris and boris.ativo:
            boris.atualizar(dt)
            resultado_boris = boris.processar_eventos(eventos)
            if resultado_boris == "fechado":
                mostrar_boris = False
            elif resultado_boris == "abrir_loja":
                # Abrir loja do Boris (implementar depois)
                mostrar_boris = False
        
        # Processar Pixel se ativo
        if mostrar_pixel and pixel.ativo:
            pixel.atualizar(dt)
            resultado_pixel = pixel.processar_eventos(eventos)
            if resultado_pixel == "fechado":
                mostrar_pixel = False
            elif resultado_pixel == "abrir_loja":
                # Abrir loja do Pixel (implementar depois)
                mostrar_pixel = False
        
        # Processar Fuligem se ativo
        if mostrar_fuligem and fuligem.ativo:
            fuligem.atualizar(dt)
            resultado_fuligem = fuligem.processar_eventos(eventos)
            if resultado_fuligem == "fechado":
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
                        "preco": resultado_fuligem.get("preco", 800)
                    }
                mostrar_fuligem = False
        
        # Processar eventos (apenas se Boris/Pixel/Fuligem não estiverem ativos, para evitar processamento duplo)
        if not (mostrar_boris and boris.ativo) and not (mostrar_pixel and pixel.ativo) and not (mostrar_fuligem and fuligem.ativo):
            for ev in eventos:
                if ev.type == pygame.QUIT:
                    return "menu_principal"  # Fechar jogo vai para menu principal
                
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        # Alternar pause
                        hub_pausado = not hub_pausado
                        if hub_pausado:
                            opcao_pausa_selecionada = 0
                    elif hub_pausado:
                        # Processar navegação no menu de pause
                        if ev.key in (pygame.K_UP, pygame.K_w):
                            opcao_pausa_selecionada = (opcao_pausa_selecionada - 1) % 4
                        elif ev.key in (pygame.K_DOWN, pygame.K_s):
                            opcao_pausa_selecionada = (opcao_pausa_selecionada + 1) % 4
                        elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                            # Selecionar opção
                            if opcao_pausa_selecionada == 0:
                                # Continuar
                                hub_pausado = False
                            elif opcao_pausa_selecionada == 1:
                                # Salvar
                                from core.progresso import gerenciador_progresso
                                gerenciador_progresso.salvar()
                                hub_pausado = False
                            elif opcao_pausa_selecionada == 2:
                                # Opções (por enquanto, apenas continuar)
                                hub_pausado = False
                            elif opcao_pausa_selecionada == 3:
                                # Menu principal
                                return "menu_principal"
                    elif ev.key in (pygame.K_UP, pygame.K_w):
                        atividade_selecionada = (atividade_selecionada - 1) % len(atividades) if atividades else 0
                    elif ev.key in (pygame.K_DOWN, pygame.K_s):
                        atividade_selecionada = (atividade_selecionada + 1) % len(atividades) if atividades else 0
                    elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if atividades and 0 <= atividade_selecionada < len(atividades):
                            atividade = atividades[atividade_selecionada]
                            return {
                                "atividade": atividade.get("tipo"),
                                "nome": atividade.get("nome"),
                                "territorio_id": territorio_id,
                                "npc_id": territorio.npc_id,
                                **atividade  # Incluir todos os parâmetros da atividade
                            }
                
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
                    
                    # Verificar clique nas atividades
                    caixa_x = LARGURA // 2 - 300
                    caixa_y = ALTURA // 2 - 200
                    atividade_altura = 60
                    
                    for i, atividade in enumerate(atividades):
                        atividade_y = caixa_y + 100 + i * (atividade_altura + 10)
                        atividade_rect = pygame.Rect(caixa_x + 20, atividade_y, 560, atividade_altura)
                        if atividade_rect.collidepoint(mouse_x, mouse_y):
                            return {
                                "atividade": atividade.get("tipo"),
                                "nome": atividade.get("nome"),
                                "territorio_id": territorio_id,
                                "npc_id": territorio.npc_id,
                                **atividade
                            }
        
        # Desenhar
        screen.blit(bg, (0, 0))
        
        # Desenhar Boris se ativo
        if mostrar_boris and boris.ativo:
            boris.desenhar_dialogo(screen, dt)
            pygame.display.flip()
            continue  # Pular o resto do desenho se Boris estiver ativo
        
        # Desenhar Pixel se ativo
        if mostrar_pixel and pixel.ativo:
            pixel.desenhar_dialogo(screen, dt)
            pygame.display.flip()
            continue  # Pular o resto do desenho se Pixel estiver ativo
        
        # Desenhar Fuligem se ativo
        if mostrar_fuligem and fuligem.ativo:
            fuligem.desenhar(screen)
            pygame.display.flip()
            continue  # Pular o resto do desenho se Fuligem estiver ativo
        
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
        
        # Overlay escuro
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Botão VOLTAR no canto superior direito
        voltar_largura = 120
        voltar_altura = 40
        voltar_x = LARGURA - voltar_largura - 20
        voltar_y = 20
        voltar_rect = pygame.Rect(voltar_x, voltar_y, voltar_largura, voltar_altura)
        
        # Verificar hover no botão voltar
        mouse_x, mouse_y = pygame.mouse.get_pos()
        voltar_hover = voltar_rect.collidepoint(mouse_x, mouse_y)
        
        # Desenhar botão voltar
        if voltar_hover:
            pygame.draw.rect(screen, (50, 50, 50), voltar_rect)
            pygame.draw.rect(screen, (255, 255, 255), voltar_rect, 2)
            cor_voltar = (255, 255, 255)
        else:
            pygame.draw.rect(screen, (30, 30, 30), voltar_rect)
            pygame.draw.rect(screen, (150, 150, 150), voltar_rect, 2)
            cor_voltar = (200, 200, 200)
        
        voltar_texto = render_text("VOLTAR", 24, cor_voltar, bold=True, pixel_style=True)
        voltar_texto_x = voltar_x + (voltar_largura - voltar_texto.get_width()) // 2
        voltar_texto_y = voltar_y + (voltar_altura - voltar_texto.get_height()) // 2
        screen.blit(voltar_texto, (voltar_texto_x, voltar_texto_y))
        
        # Desenhar NPC (se existir)
        if npc_sprite:
            # Redimensionar NPC
            npc_w = 300
            npc_h = int(npc_sprite.get_height() * (npc_w / npc_sprite.get_width()))
            npc_redimensionado = pygame.transform.scale(npc_sprite, (npc_w, npc_h))
            
            npc_x = 50
            npc_y = ALTURA - npc_h - 50
            screen.blit(npc_redimensionado, (npc_x, npc_y))
        
        # Caixa principal
        caixa_largura = 600
        caixa_altura = 400
        caixa_x = LARGURA // 2 - caixa_largura // 2
        caixa_y = ALTURA // 2 - caixa_altura // 2
        
        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 220))
        screen.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(screen, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        # Título
        titulo = render_text(territorio.nome, 32, (255, 255, 255), bold=True, pixel_style=True)
        titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, caixa_y + 20))
        
        # Descrição
        desc_texto = render_text(territorio.descricao, 16, (200, 200, 200), bold=False, pixel_style=True)
        desc_x = caixa_x + (caixa_largura - desc_texto.get_width()) // 2
        screen.blit(desc_texto, (desc_x, caixa_y + 60))
        
        # Lista de atividades
        if atividades:
            atividade_altura = 60
            atividade_y_inicial = caixa_y + 100
            
            for i, atividade in enumerate(atividades):
                atividade_y = atividade_y_inicial + i * (atividade_altura + 10)
                atividade_rect = pygame.Rect(caixa_x + 20, atividade_y, caixa_largura - 40, atividade_altura)
                
                # Destaque se selecionada
                if i == atividade_selecionada:
                    # Brilho pulsante
                    import math
                    pulso = 0.9 + 0.1 * abs(math.sin(tempo_animacao * 4.0))
                    cor_destaque = tuple(min(255, int(c * pulso)) for c in (100, 150, 200))
                    pygame.draw.rect(screen, cor_destaque, atividade_rect, 3)
                else:
                    pygame.draw.rect(screen, (100, 100, 100), atividade_rect, 1)
                
                # Nome da atividade
                nome_atividade = render_text(atividade.get("nome", "Atividade"), 20, (255, 255, 255), bold=True, pixel_style=True)
                screen.blit(nome_atividade, (atividade_rect.x + 10, atividade_rect.y + 10))
                
                # Informações adicionais (risco, recompensa, etc.)
                info_parts = []
                if "risco" in atividade:
                    info_parts.append(f"Risco: {atividade['risco'].upper()}")
                if "recompensa" in atividade:
                    info_parts.append(f"Recompensa: {atividade['recompensa'].upper()}")
                if "custo" in atividade:
                    info_parts.append(f"Custo: {atividade['custo'].upper()}")
                
                if info_parts:
                    info_texto = render_text(" | ".join(info_parts), 14, (150, 150, 150), bold=False, pixel_style=True)
                    screen.blit(info_texto, (atividade_rect.x + 10, atividade_rect.y + 35))
        # Removido: mensagem "Nenhuma atividade disponível"
        
        # Instruções
        instrucoes = render_text("Selecione uma atividade | ESC para voltar ao mapa", 14, (150, 150, 150), bold=False, pixel_style=True)
        screen.blit(instrucoes, (10, ALTURA - 30))
        
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

