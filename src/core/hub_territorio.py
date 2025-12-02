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
def obter_caminho_autodromo():
    return obter_caminho_sprite_dia_noite("autodromo_fora")

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
    elif "autódromo" in territorio_id_lower or "autodromo" in territorio_id_lower:
        caminho = obter_caminho_autodromo()
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
        # Verificar se é uma área especial (ex: oficina, autódromo)
        territorio_id_lower = territorio_id.lower()
        area_nome_lower = (area_nome or "").lower()
        
        if ("oficina" in territorio_id_lower or "garagem" in territorio_id_lower or 
            "crank" in territorio_id_lower or 
            "oficina" in area_nome_lower or "garagem" in area_nome_lower):
            # Redirecionar diretamente para a oficina
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
    
    # Lista de atividades (não usada mais - NPCs gerenciam suas próprias atividades)
    atividades = territorio.atividades
    
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
    
    # Verificar se é território da Akira (Montanha)
    from core.akira import akira
    mostrar_akira = False
    if territorio.npc_id and "akira" in territorio.npc_id.lower():
        # Verificar se a montanha está desbloqueada
        from core.mapa_locations import gerenciador_localizacoes
        if gerenciador_localizacoes.esta_desbloqueado("montanha"):
            # Carregar sprites se necessário
            if not akira.sprites_carregados:
                akira.carregar_sprites()
            
            # Se é primeira vez, mostrar apresentação
            if not akira.primeira_aparicao_mostrada:
                mostrar_akira = akira.verificar_aparecer_primeira_vez()
            else:
                # Já foi apresentado - ativar diálogo da Akira para oferecer corrida
                mostrar_akira = akira.ativar_dialogo_corrida()
        else:
            # Montanha ainda não desbloqueada
            mostrar_akira = False
    
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
                # Salvar progresso após fechar diálogo do Boris
                from core.progresso import gerenciador_progresso
                from core.missoes import gerenciador_missoes
                gerenciador_progresso.salvar()
                gerenciador_missoes.salvar()
                mostrar_boris = False
            elif resultado_boris == "abrir_loja":
                # Abrir loja do Boris (implementar depois)
                mostrar_boris = False
        
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
            elif resultado_pixel == "abrir_loja":
                # Abrir loja do Pixel (implementar depois)
                mostrar_pixel = False
        
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
        
        # Processar Akira se ativa
        if mostrar_akira and akira.ativo:
            # IMPORTANTE: Capturar o modo ANTES de processar eventos, pois fechar() reseta o modo
            modo_antes_processar = akira.modo_dialogo
            akira.atualizar(dt)
            resultado_akira = akira.processar_eventos(eventos)
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
            elif isinstance(resultado_akira, dict) and resultado_akira.get("corrida"):
                # Iniciar corrida da Akira
                pista = resultado_akira.get("pista", 3)
                # Definir flag de corrida campanha antes de retornar
                from core.progresso import gerenciador_progresso
                race_id = resultado_akira.get("race_id", "mountain_test")
                if race_id == "mountain_test":
                    gerenciador_progresso.ultima_corrida_campanha = "mountain_test"
                    gerenciador_progresso.salvar()
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
        
        # Processar eventos do celular (antes de outros eventos, mas apenas se nenhum NPC estiver ativo)
        celular_processou_evento = False
        try:
            from core.celular import celular
            from core.narrative_system import narrative_system
            
            # Verificar se deve mostrar celular (modo campanha, sem cutscenes, sem NPCs ativos)
            npc_ativo = (mostrar_boris and boris.ativo) or (mostrar_pixel and pixel.ativo) or \
                       (mostrar_fuligem and fuligem.ativo) or (mostrar_akira and akira.ativo)
            cutscene_ativa = narrative_system.active if hasattr(narrative_system, 'active') else False
            celular.verificar_visibilidade(modo_arcade=False, em_corrida=False, cutscene_ativa=cutscene_ativa or npc_ativo)
            
            # Processar eventos do celular apenas se nenhum NPC estiver ativo
            if not npc_ativo:
                for ev in eventos:
                    if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                        if celular.processar_clique(ev.pos):
                            # Celular foi clicado, processar eventos do menu
                            resultado_celular = celular.processar_eventos([ev])
                            if resultado_celular == "fechado":
                                celular.menu_aberto = False
                            celular_processou_evento = True
                            break  # Não processar outros eventos se o celular foi clicado
                    elif ev.type == pygame.KEYDOWN:
                        # Processar teclas do celular se o menu estiver aberto
                        if celular.menu_aberto:
                            resultado_celular = celular.processar_eventos([ev])
                            if resultado_celular == "fechado":
                                celular.menu_aberto = False
                            # Se ESC foi pressionado, não processar outros eventos
                            if ev.key == pygame.K_ESCAPE:
                                celular_processou_evento = True
                                break
        except Exception as e:
            print(f"[HUB_TERRITORIO] Erro ao processar celular: {e}")
            import traceback
            traceback.print_exc()
        
        # Processar eventos (apenas se Boris/Pixel/Fuligem/Akira não estiverem ativos, para evitar processamento duplo)
        # IMPORTANTE: Se Fuligem está ativo, não processar ESC aqui para evitar conflito
        if not (mostrar_boris and boris.ativo) and not (mostrar_pixel and pixel.ativo) and not (mostrar_fuligem and fuligem.ativo) and not (mostrar_akira and akira.ativo):
            # Se o celular processou um evento importante, pular processamento de outros eventos
            if celular_processou_evento and celular.menu_aberto:
                pass  # Não processar outros eventos se o menu do celular está aberto
            else:
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
        
        # Desenhar fundo apenas se nenhum NPC estiver ativo (NPCs desenham seus próprios fundos)
        # EXCEÇÃO: Akira em primeira_aparicao, sem_preparo e corrida precisam do fundo do território
        desenhar_fundo = True
        if (mostrar_boris and boris.ativo) or (mostrar_pixel and pixel.ativo) or (mostrar_fuligem and fuligem.ativo):
            desenhar_fundo = False
        elif mostrar_akira and akira.ativo:
            # Akira precisa do fundo do território para primeira_aparicao, sem_preparo e corrida
            # Apenas pre_corrida e fim_corrida têm seus próprios fundos
            if akira.modo_dialogo in ["pre_corrida", "fim_corrida"]:
                desenhar_fundo = False
        
        if desenhar_fundo and bg:
            screen.blit(bg, (0, 0))
        
        # Desenhar Akira se ativa (prioridade sobre outros NPCs)
        if mostrar_akira and akira.ativo:
            akira.desenhar_dialogo(screen, dt)
            pygame.display.flip()
            continue  # Pular o resto do desenho se Akira estiver ativa
        
        # Desenhar Boris se ativo
        if mostrar_boris and boris.ativo:
            boris.desenhar_dialogo(screen, dt)
            pygame.display.flip()
            continue  # Pular o resto do desenho se Boris estiver ativo
        
        # Desenhar Pixel se ativo
        if mostrar_pixel and pixel.ativo:
            # Garantir que os sprites estão carregados antes de desenhar
            if not pixel.sprites_carregados:
                pixel.carregar_sprites()
            pixel.desenhar_dialogo(screen, dt)
            pygame.display.flip()
            continue  # Pular o resto do desenho se Pixel estiver ativo
        
        # Desenhar Fuligem se ativo
        if mostrar_fuligem and fuligem.ativo:
            fuligem.desenhar_dialogo(screen, dt)
            pygame.display.flip()
            continue  # Pular o resto do desenho se Fuligem estiver ativo
        
        # Atualizar e desenhar celular (modo campanha, sem cutscenes, sem NPCs ativos)
        try:
            from core.celular import celular
            from core.narrative_system import narrative_system
            
            # Verificar se deve mostrar celular
            npc_ativo = (mostrar_boris and boris.ativo) or (mostrar_pixel and pixel.ativo) or \
                       (mostrar_fuligem and fuligem.ativo) or (mostrar_akira and akira.ativo)
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

