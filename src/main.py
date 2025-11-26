import os
import math
import random
import pygame
from config import (
    LARGURA, ALTURA, TURBO_P1, TURBO_P2,
    USAR_IA_NO_CARRO_2, CONFIGURACOES,
    obter_lista_mapas, CAMINHO_TROFEU_OURO, CAMINHO_TROFEU_PRATA, CAMINHO_TROFEU_BRONZE, CAMINHO_TROFEU_VAZIO
)
from core.checkpoint_manager import CheckpointManager
from core.carro_fisica import CarroFisica
from core.corrida import GerenciadorCorrida
from core.camera import Camera
from core.ia import IA
from core.musica import gerenciador_musica
from core.hud import HUD
from core.game_modes import ModoJogo, TipoJogo
from core.drift_scoring import DriftScoring
from core.progresso import gerenciador_progresso
from core.ghost import GhostRecorder, GhostPlayer, gerenciador_ghosts
from core.achievements import gerenciador_achievements
from core.popup_achievement import popup_achievement
from core.estatisticas import gerenciador_estatisticas
from core.desafios import gerenciador_desafios
from core.gamepad_manager import gerenciador_gamepad
from core.mercador_alien import mercador_alien
from core.crank import crank
from core.rex import rex
from core.glub import glub
from core.akira import akira
from core.ranking import gerenciador_ranking
from config import CAMINHO_MENU

# Lista de nomes para os bots
NOMES_BOTS = [
    "SPEED DEMON", "NITRO RIDER", "TURBO BLAZE", "VELOCITY", "THUNDER",
    "SHADOW RACER", "PHANTOM", "NIGHT RIDER", "STORM", "LIGHTNING",
    "FIREBALL", "BLAZE RUNNER", "SKY ROCKET", "WIND RIDER", "FLASH",
    "RAPID FIRE", "QUICK SILVER", "SONIC", "BOLT", "JET STREAM",
    "ROCKET MAN", "SPEEDSTER", "RACER X", "FAST LANE", "HIGHWAY STAR",
    "ROAD WARRIOR", "DRIFT KING", "CORNER MASTER", "TRACK BEAST", "PIT VIPER"
]

def carregar_configuracoes_garagem():
    try:
        from config import DIR_PROJETO
        caminho_garage_config = os.path.join(DIR_PROJETO, 'data', 'garage_config.json')
        if os.path.exists(caminho_garage_config):
            import json
            with open(caminho_garage_config, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            carros_dict = {carro['prefixo_cor']: carro for carro in dados.get('carros', [])}
            
            for carro in CARROS_DISPONIVEIS:
                prefixo = carro['prefixo_cor']
                if prefixo in carros_dict:
                    carro_config = carros_dict[prefixo]
                    carro['posicao'] = tuple(carro_config.get('posicao', carro['posicao']))
                    carro['tamanho_oficina'] = tuple(carro_config.get('tamanho_oficina', carro['tamanho_oficina']))
                    carro['posicao_oficina'] = tuple(carro_config.get('posicao_oficina', carro['posicao_oficina']))
            
            print(f"Configurações da garagem carregadas de: {caminho_garage_config}")
    except Exception as e:
        print(f"Erro ao carregar configurações da garagem: {e}")

CARROS_DISPONIVEIS = [
    {"nome": "Nissan 350Z", "prefixo_cor": "Car1", "posicao": (570, 145), "sprite_selecao": "Car1", "tipo_tracao": "Traseira", "tamanho_oficina": (850, 550), "posicao_oficina": (203, 183), "preco": 0, "multiplicador_base": 1.00},
    {"nome": "BMW M3 95' ", "prefixo_cor": "Car2", "posicao": (570, 190), "sprite_selecao": "Car2", "tipo_tracao": "Traseira", "tamanho_oficina": (770, 415), "posicao_oficina": (233, 298), "preco": 28000, "multiplicador_base": 1.12},
    {"nome": "Chevrolet Camaro", "prefixo_cor": "Car3", "posicao": (560, 210), "sprite_selecao": "Car3", "tipo_tracao": "Traseira", "tamanho_oficina": (720, 470), "posicao_oficina": (263, 281), "preco": 38000, "multiplicador_base": 1.25},
    {"nome": "Toyota Supra", "prefixo_cor": "Car4", "posicao": (570, 190), "sprite_selecao": "Car4", "tipo_tracao": "Traseira", "tamanho_oficina": (755, 400), "posicao_oficina": (242, 326), "preco": 48000, "multiplicador_base": 1.40},
    {"nome": "Toyota Trueno", "prefixo_cor": "Car5", "posicao": (590, 175), "sprite_selecao": "Car5", "tipo_tracao": "Traseira", "tamanho_oficina": (740, 495), "posicao_oficina": (231, 240), "preco": 32000, "multiplicador_base": 1.57},
    {"nome": "Nissan Skyline", "prefixo_cor": "Car6", "posicao": (550, 200), "sprite_selecao": "Car6", "tipo_tracao": "Frontal", "tamanho_oficina": (730, 400), "posicao_oficina": (244, 329), "preco": 65000, "multiplicador_base": 1.76},
    {"nome": "Nissan Silvia S13", "prefixo_cor": "Car7", "posicao": (600, 185), "sprite_selecao": "Car7", "tipo_tracao": "Traseira", "tamanho_oficina": (855, 470), "posicao_oficina": (179, 318), "preco": 42000, "multiplicador_base": 1.97},
    {"nome": "Mazda RX-7", "prefixo_cor": "Car8", "posicao": (540, 220), "sprite_selecao": "Car8", "tipo_tracao": "Traseira", "tamanho_oficina": (805, 505), "posicao_oficina": (197, 240), "preco": 52000, "multiplicador_base": 2.21},
    {"nome": "Toyota Celica", "prefixo_cor": "Car9", "posicao": (610, 195), "sprite_selecao": "Car9", "tipo_tracao": "Traseira", "tamanho_oficina": (730, 425), "posicao_oficina": (240, 308), "preco": 38000, "multiplicador_base": 2.47},
    {"nome": "Volkswagem Fusca", "prefixo_cor": "Car10", "posicao": (530, 240), "sprite_selecao": "Car10", "tipo_tracao": "Frontal", "tamanho_oficina": (720, 485), "posicao_oficina": (242, 230), "preco": 18000, "multiplicador_base": 2.77},
    {"nome": "Mitsubishi Lancer", "prefixo_cor": "Car11", "posicao": (620, 205), "sprite_selecao": "Car11", "tipo_tracao": "Traseira", "tamanho_oficina": (955, 705), "posicao_oficina": (147, 86), "preco": 47000, "multiplicador_base": 3.10},
    {"nome": "Porsche 911 77'", "prefixo_cor": "Car12", "posicao": (520, 260), "sprite_selecao": "Car12", "tipo_tracao": "Traseira", "tamanho_oficina": (935, 675), "posicao_oficina": (153, 196), "preco": 90000, "multiplicador_base": 3.47},
    {"nome": "Audi Quattro S1", "prefixo_cor": "Car13", "posicao": (520, 260), "sprite_selecao": "Car13", "tipo_tracao": "AWD", "tamanho_oficina": (935, 675), "posicao_oficina": (153, 196), "preco": 100000, "multiplicador_base": 3.89}
]

carregar_configuracoes_garagem()

def principal(carro_selecionado_p1=0, carro_selecionado_p2=1, mapa_selecionado=None, modo_jogo=ModoJogo.UM_JOGADOR, tipo_jogo=TipoJogo.CORRIDA, voltas=1, dificuldade_ia="medio"):
    if hasattr(principal, '_recompensa_drift_calculada'):
        delattr(principal, '_recompensa_drift_calculada')
    
    pygame.init()

    from config import carregar_configuracoes
    carregar_configuracoes()

    resolucao = CONFIGURACOES["video"]["resolucao"]
    fullscreen = CONFIGURACOES["video"]["fullscreen"]
    tela_cheia_sem_bordas = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
    qualidade_alta = CONFIGURACOES["video"]["qualidade_alta"]
    vsync = CONFIGURACOES["video"]["vsync"]
    fps_max = max(CONFIGURACOES["video"]["fps_max"], 200)

    flags_display = 0
    if fullscreen:
        flags_display |= pygame.FULLSCREEN
    elif tela_cheia_sem_bordas:
        flags_display |= pygame.NOFRAME

    tela = pygame.display.set_mode(resolucao, flags_display)
    if vsync:
        pygame.display.set_mode(resolucao, flags_display | pygame.DOUBLEBUF)

    from core.i18n import inicializar_idioma, atualizar_titulo_janela
    inicializar_idioma()
    atualizar_titulo_janela("jogo")
    relogio = pygame.time.Clock()

    if CONFIGURACOES["video"]["mostrar_fps"]:
        pygame.font.init()
        fonte_fps = pygame.font.Font(None, 36)

    def aplicar_qualidade_imagem(imagem):
        if not qualidade_alta:
            largura, altura = imagem.get_size()
            nova_largura = max(largura // 3, 1)
            nova_altura = max(altura // 3, 1)
            imagem_redimensionada = pygame.transform.scale(imagem, (nova_largura, nova_altura))
            return pygame.transform.scale(imagem_redimensionada, (largura, altura))
        return imagem

    from config import MAPA_ATUAL
    mapas_disponiveis = obter_lista_mapas()
    mapa_atual = mapa_selecionado if mapa_selecionado and mapa_selecionado in mapas_disponiveis else MAPA_ATUAL

    if mapa_atual != MAPA_ATUAL:
        import config
        config.MAPA_ATUAL = mapa_atual
        config.atualizar_caminhos_mapa()

    from core.pista_tiles import PistaTiles
    numero_pista = mapa_selecionado if mapa_selecionado is not None else 1
    
    pista_tiles = PistaTiles(largura=5000, altura=5000)
    superficie_pista_renderizada = pista_tiles.construir_pista(numero_pista, posicao_centro=(2500, 2500))
    print(f"Pista {numero_pista} construída usando tiles estilo GRIP ({superficie_pista_renderizada.get_width()}x{superficie_pista_renderizada.get_height()})")
    
    offset_x_superficie = getattr(pista_tiles, 'offset_x_superficie', 0)
    offset_y_superficie = getattr(pista_tiles, 'offset_y_superficie', 0)
    
    img_pista = superficie_pista_renderizada.copy()
    mask_pista = superficie_pista_renderizada.copy()
    from core.laps_grip import carregar_checkpoints_grip, carregar_spawn_points
    checkpoints_grip = carregar_checkpoints_grip(numero_pista, superficie_pista=superficie_pista_renderizada)
    
    if checkpoints_grip:
        checkpoints = checkpoints_grip
        print(f"Checkpoints do GRIP carregados: {len(checkpoints)}")
    else:
        pos_inicial_tiles = pista_tiles.obter_posicao_inicial()
        centro_x, centro_y = 2500, 2500
        checkpoints = [(centro_x + pos_inicial_tiles[0], centro_y + pos_inicial_tiles[1])]
        print(f"Usando checkpoint padrão baseado em tiles: {checkpoints[0]}")
    
    minimapa_imagem = pista_tiles.carregar_minimapa(numero_pista)
    
    checkpoint_manager = CheckpointManager(mapa_atual, checkpoints_iniciais=checkpoints, numero_pista=numero_pista)
    
    if checkpoint_manager.checkpoints:
        checkpoints = []
        # Aplicar ajuste ao centro da pista também aos checkpoints do checkpoint_manager
        from core.laps_grip import ajustar_checkpoint_centro_pista
        for cp in checkpoint_manager.checkpoints:
            if len(cp) >= 3:
                x, y, angulo = float(cp[0]), float(cp[1]), float(cp[2])
            elif len(cp) >= 2:
                x, y = float(cp[0]), float(cp[1])
                angulo = None
            
            # Ajustar para o centro da pista
            novo_x, novo_y = ajustar_checkpoint_centro_pista(x, y, angulo, superficie_pista_renderizada)
            
            if len(cp) >= 3:
                checkpoints.append((float(novo_x), float(novo_y), float(angulo)))
            else:
                checkpoints.append((float(novo_x), float(novo_y), 0))
        print(f"Usando {len(checkpoints)} checkpoints do checkpoint_manager (ajustados ao centro da pista)")
    
    largura_atual, altura_atual = resolucao
    largura_pista, altura_pista = superficie_pista_renderizada.get_size()
    
    camera = Camera(largura_atual, altura_atual, largura_pista, altura_pista, zoom=1.8)
    camera.cx = 2500 + offset_x_superficie
    camera.cy = 2500 + offset_y_superficie
    camera.offset_x = -offset_x_superficie
    camera.offset_y = -offset_y_superficie
    
    print(f"Superfície da pista: {largura_pista:.0f}x{altura_pista:.0f}")
    print(f"Posição inicial da câmera: ({camera.cx:.0f}, {camera.cy:.0f})")

    modo_drift_atual = CONFIGURACOES["jogo"]["modo_drift"]
    mostrar_fps = CONFIGURACOES["video"]["mostrar_fps"]
    mostrar_debug = CONFIGURACOES["jogo"]["mostrar_debug"]

    fonte = pygame.font.SysFont("consolas", 26)
    fonte_small = pygame.font.SysFont("consolas", 18)
    fonte_checkpoint = pygame.font.SysFont("consolas", 18, bold=True)
    fonte_debug = pygame.font.SysFont("consolas", 16)
    fonte_debug_bold = pygame.font.SysFont("consolas", 16, bold=True)
    
    try:
        trofeu_ouro = pygame.image.load(CAMINHO_TROFEU_OURO).convert_alpha()
        trofeu_prata = pygame.image.load(CAMINHO_TROFEU_PRATA).convert_alpha()
        trofeu_bronze = pygame.image.load(CAMINHO_TROFEU_BRONZE).convert_alpha()
        trofeu_vazio = pygame.image.load(CAMINHO_TROFEU_VAZIO).convert_alpha()
        tamanho_trofeu = (160, 160)
        trofeu_ouro = pygame.transform.scale(trofeu_ouro, tamanho_trofeu)
        trofeu_prata = pygame.transform.scale(trofeu_prata, tamanho_trofeu)
        trofeu_bronze = pygame.transform.scale(trofeu_bronze, tamanho_trofeu)
        trofeu_vazio = pygame.transform.scale(trofeu_vazio, tamanho_trofeu)
    except Exception as e:
        print(f"Erro ao carregar troféus: {e}")
        trofeu_ouro = trofeu_prata = trofeu_bronze = trofeu_vazio = None

    voltas_objetivo = voltas
    print(f"Checkpoints para corrida: {len(checkpoints)} checkpoints")
    if checkpoints:
        print(f"Checkpoints: {checkpoints}")
    
    corrida = GerenciadorCorrida(fonte, checkpoints, voltas_objetivo)
    
    print(f"Checkpoints na corrida: {len(corrida.checkpoints)} checkpoints")
    if corrida.checkpoints:
        print(f"Checkpoints na corrida: {corrida.checkpoints}")
    
    def obter_posicao_jogador(carro_jogador, todos_carros):
        if not corrida.finalizou.get(carro_jogador, False):
            return None
        
        candidatos = []
        for i, carro in enumerate(todos_carros):
            if corrida.finalizou.get(carro, False):
                tempo = corrida.tempo_final.get(carro)
                if tempo is not None:
                    candidatos.append((i+1, tempo, carro))
        
        if not candidatos:
            return None
        
        candidatos.sort(key=lambda x: x[1])  # Ordenar por tempo
        
        for pos, (idx, tempo, carro) in enumerate(candidatos, start=1):
            if carro == carro_jogador:
                return pos
        return None
    
    def obter_trofeu_por_posicao(posicao):
        if posicao == 1:
            return trofeu_ouro
        elif posicao == 2:
            return trofeu_prata
        elif posicao == 3:
            return trofeu_bronze
        else:
            return trofeu_vazio
    
    def obter_pontuacoes_alvo(num_checkpoints, voltas=1, dificuldade="medio"):
        fator_base = 25000.0 / 19.0
        pontuacao_base_ouro = fator_base * num_checkpoints
        pontuacao_ouro = pontuacao_base_ouro * voltas
        
        if dificuldade == "facil":
            pontuacao_ouro = pontuacao_ouro * 0.6
        elif dificuldade == "dificil":
            pontuacao_ouro = pontuacao_ouro * 1.5
        
        pontuacao_prata = pontuacao_ouro * 0.4
        pontuacao_bronze = pontuacao_ouro * 0.1
        
        return {
            'ouro': pontuacao_ouro,
            'prata': pontuacao_prata,
            'bronze': pontuacao_bronze
        }
    
    def obter_tempos_alvo(numero_pista, voltas=1, dificuldade="medio"):
        tempo_base_por_volta = 32.0
        recorde_pista = gerenciador_progresso.obter_recorde(numero_pista)
        if recorde_pista is not None:
            tempo_base_por_volta = recorde_pista / voltas * 1.1
        
        tempo_base_total = tempo_base_por_volta * voltas
        
        if dificuldade == "facil":
            multiplicador = 1.4
        elif dificuldade == "dificil":
            multiplicador = 0.75
        else:
            multiplicador = 1.0
        
        tempo_ouro = tempo_base_total * multiplicador
        tempo_prata = tempo_ouro * 1.15
        tempo_bronze = tempo_ouro * 1.35
        
        return {
            'ouro': tempo_ouro,
            'prata': tempo_prata,
            'bronze': tempo_bronze
        }
    
    def obter_trofeu_por_tempo(tempo, tempos_alvo=None):
        if tempos_alvo is None or tempo is None:
            return trofeu_vazio
        
        if tempo <= tempos_alvo['ouro']:
            return trofeu_ouro
        elif tempo <= tempos_alvo['prata']:
            return trofeu_prata
        elif tempo <= tempos_alvo['bronze']:
            return trofeu_bronze
        else:
            return trofeu_vazio
    
    def obter_trofeu_por_pontuacao(pontuacao, pontuacoes_alvo=None):
        if pontuacoes_alvo:
            if pontuacao >= pontuacoes_alvo['ouro']:
                return trofeu_ouro
            elif pontuacao >= pontuacoes_alvo['prata']:
                return trofeu_prata
            elif pontuacao >= pontuacoes_alvo['bronze']:
                return trofeu_bronze
            else:
                return trofeu_vazio
        else:
            if pontuacao >= 50000:
                return trofeu_ouro
            elif pontuacao >= 20000:
                return trofeu_prata
            elif pontuacao >= 5000:
                return trofeu_bronze
            else:
                return trofeu_vazio
    
    def processar_tela_fim_jogo(ev, estado, lado=None):
        from core.menu import verificar_clique_opcao
        
        if estado is None:
            return None
        
        titulo, subtitulo, trofeu, posicao, pontuacao, recompensa, opcao_atual, hover_animation = estado
        # Verificar se está em modo 2 jogadores e se o outro jogador ainda não terminou
        mostrar_espectador = False
        if modo_jogo == ModoJogo.DOIS_JOGADORES:
            # Verificar se ambos os carros finalizaram a corrida (não apenas se os estados existem)
            # Isso evita mostrar opção de assistir quando um jogador já terminou mas virou espectador
            carro1_finalizou = corrida.finalizou.get(carro1, False) if carro1 is not None else False
            carro2_finalizou = corrida.finalizou.get(carro2, False) if carro2 is not None else False
            
            if lado == 'esquerdo' and not carro2_finalizou:
                # Player 1 terminou, mas player 2 ainda não
                mostrar_espectador = True
            elif lado == 'direito' and not carro1_finalizou:
                # Player 2 terminou, mas player 1 ainda não
                mostrar_espectador = True
        
        # Se o outro jogador ainda não terminou, mostrar apenas opção de assistir
        if mostrar_espectador:
            opcoes = [
                ("ASSISTIR JOGADOR", "espectador")
            ]
        else:
            # Ambos terminaram ou modo 1 jogador - mostrar todas as opções
            opcoes = [
                ("REINICIAR JOGO", "reiniciar"),
                ("TROCAR CARRO", "trocar_carro"),
                ("MENU PRINCIPAL", "menu")
            ]
        
        caixa_largura = 500
        caixa_altura = 650
        if lado == 'esquerdo':
            caixa_x = 20
            caixa_y = (ALTURA - caixa_altura) // 2
        elif lado == 'direito':
            caixa_x = LARGURA - caixa_largura - 20
            caixa_y = (ALTURA - caixa_altura) // 2
        else:
            caixa_x = (LARGURA - caixa_largura) // 2
            caixa_y = (ALTURA - caixa_altura) // 2
        
        altura_total_opcoes = len(opcoes) * 60
        offset_opcoes = caixa_y + caixa_altura - altura_total_opcoes - 20
        if ev.type == pygame.QUIT:
            return "sair"
        from core.gamepad_manager import gerenciador_gamepad
        if gerenciador_gamepad.obter_numero_controles() > 0:
            from core.menu_controles import processar_eventos_controle_menu
            tempo_atual = pygame.time.get_ticks()
            resultado_controle = processar_eventos_controle_menu(ev, estado[6], len(opcoes), joystick_id=0, tempo_atual=tempo_atual)
            if resultado_controle:
                acao = resultado_controle.get("acao")
                if acao == "cima" and "opcao" in resultado_controle:
                    estado[6] = resultado_controle["opcao"]
                elif acao == "baixo" and "opcao" in resultado_controle:
                    estado[6] = resultado_controle["opcao"]
                elif acao == "confirmar":
                    chave = opcoes[estado[6]][1]
                    return chave
                elif acao == "cancelar":
                    return "menu"
                else:
                    return None
        
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            mouse_x, mouse_y = ev.pos
            if lado == 'esquerdo' and mouse_x >= LARGURA // 2:
                return None
            elif lado == 'direito' and mouse_x < LARGURA // 2:
                return None
            
            mouse_in_caixa = (caixa_x <= mouse_x <= caixa_x + caixa_largura and
                              caixa_y <= mouse_y <= caixa_y + caixa_altura)
            if mouse_in_caixa:
                for i, (nome, chave) in enumerate(opcoes):
                    y_opcao = offset_opcoes + i * 60
                    opcao_rect = pygame.Rect(caixa_x + 20, y_opcao - 5, caixa_largura - 40, 60)
                    if opcao_rect.collidepoint(mouse_x, mouse_y):
                        return chave
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                return "menu"
            elif ev.key in (pygame.K_UP, pygame.K_w):
                estado[6] = (estado[6] - 1) % len(opcoes)  # opcao_atual
            elif ev.key in (pygame.K_DOWN, pygame.K_s):
                estado[6] = (estado[6] + 1) % len(opcoes)  # opcao_atual
            elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                chave = opcoes[estado[6]][1]
                return chave
        
        return None
    
    def desenhar_tela_fim_jogo(tela, estado, dt, lado=None):
        if estado is None:
            return
        
        from core.menu import render_text, verificar_clique_opcao
        
        titulo, subtitulo, trofeu, posicao, pontuacao, recompensa, opcao_atual, hover_animation = estado
        # Verificar se está em modo 2 jogadores e se o outro jogador ainda não terminou
        mostrar_espectador = False
        if modo_jogo == ModoJogo.DOIS_JOGADORES:
            # Verificar se ambos os carros finalizaram a corrida (não apenas se os estados existem)
            # Isso evita mostrar opção de assistir quando um jogador já terminou mas virou espectador
            carro1_finalizou = corrida.finalizou.get(carro1, False) if carro1 is not None else False
            carro2_finalizou = corrida.finalizou.get(carro2, False) if carro2 is not None else False
            
            if lado == 'esquerdo' and not carro2_finalizou:
                # Player 1 terminou, mas player 2 ainda não
                mostrar_espectador = True
            elif lado == 'direito' and not carro1_finalizou:
                # Player 2 terminou, mas player 1 ainda não
                mostrar_espectador = True
        
        # Se o outro jogador ainda não terminou, mostrar apenas opção de assistir
        if mostrar_espectador:
            opcoes = [
                ("ASSISTIR JOGADOR", "espectador")
            ]
        else:
            # Ambos terminaram ou modo 1 jogador - mostrar todas as opções
            opcoes = [
                ("REINICIAR JOGO", "reiniciar"),
                ("TROCAR CARRO", "trocar_carro"),
                ("MENU PRINCIPAL", "menu")
            ]
        
        caixa_largura = 500
        caixa_altura = 650
        if lado == 'esquerdo':
            caixa_x = 20
            caixa_y = (ALTURA - caixa_altura) // 2
        elif lado == 'direito':
            caixa_x = LARGURA - caixa_largura - 20
            caixa_y = (ALTURA - caixa_altura) // 2
        else:
            caixa_x = (LARGURA - caixa_largura) // 2
            caixa_y = (ALTURA - caixa_altura) // 2
        
        altura_total_opcoes = len(opcoes) * 60
        offset_opcoes = caixa_y + caixa_altura - altura_total_opcoes - 20
        
        if lado is None:
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            tela.blit(overlay, (0, 0))
        elif lado == 'esquerdo':
            metade_largura = LARGURA // 2
            overlay = pygame.Surface((metade_largura, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            tela.blit(overlay, (0, 0))
        elif lado == 'direito':
            metade_largura = LARGURA // 2
            overlay = pygame.Surface((metade_largura, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            tela.blit(overlay, (metade_largura, 0))
        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 200))
        tela.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(tela, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_in_caixa = (caixa_x <= mouse_x <= caixa_x + caixa_largura and
                          caixa_y <= mouse_y <= caixa_y + caixa_altura)
        
        hover_speed = 8.0
        opcao_hover = -1
        if mouse_in_caixa:
            for i, (nome, chave) in enumerate(opcoes):
                y_opcao = offset_opcoes + i * 60
                opcao_rect = pygame.Rect(caixa_x + 20, y_opcao - 5, caixa_largura - 40, 60)
                if opcao_rect.collidepoint(mouse_x, mouse_y):
                    opcao_hover = i
                    break
        if opcao_hover >= 0:
            opcao_atual = opcao_hover
            estado[6] = opcao_atual
        
        while len(hover_animation) < len(opcoes):
            hover_animation.append(0.0)
        if len(hover_animation) > len(opcoes):
            hover_animation = hover_animation[:len(opcoes)]
        
        for i in range(len(opcoes)):
            if i == opcao_hover:
                hover_animation[i] = min(1.0, hover_animation[i] + hover_speed * dt)
            else:
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt)
        if not mouse_in_caixa:
            for i in range(len(opcoes)):
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt * 1.5)
        
        titulo_texto = render_text(titulo, 40, (255, 255, 255), bold=True, pixel_style=True)
        titulo_x = caixa_x + (caixa_largura - titulo_texto.get_width()) // 2
        tela.blit(titulo_texto, (titulo_x, caixa_y + 20))
        
        if subtitulo:
            subtitulo_texto = render_text(subtitulo, 32, (200, 200, 200), bold=True, pixel_style=True)
            subtitulo_x = caixa_x + (caixa_largura - subtitulo_texto.get_width()) // 2
            tela.blit(subtitulo_texto, (subtitulo_x, caixa_y + 95))
        
        y_info = caixa_y + 180
        if trofeu is not None:
            trofeu_rect = trofeu.get_rect(center=(caixa_x + caixa_largura // 2, y_info + 60))
            tela.blit(trofeu, trofeu_rect)
            y_info += 150
        
        if posicao:
            pos_texto = render_text(f"{posicao}º LUGAR", 36, (255, 215, 0), bold=True, pixel_style=True)
            pos_x = caixa_x + (caixa_largura - pos_texto.get_width()) // 2
            tela.blit(pos_texto, (pos_x, y_info))
            y_info += 60
        
        if pontuacao is not None:
            pont_texto = render_text(f"Pontuação: {int(pontuacao)}", 28, (255, 255, 0), bold=True, pixel_style=True)
            pont_x = caixa_x + (caixa_largura - pont_texto.get_width()) // 2
            tela.blit(pont_texto, (pont_x, y_info))
            y_info += 50
        
        if recompensa is not None and recompensa > 0:
            rec_texto = render_text(f"+${recompensa}", 24, (100, 255, 100), bold=True, pixel_style=True)
            rec_x = caixa_x + (caixa_largura - rec_texto.get_width()) // 2
            tela.blit(rec_texto, (rec_x, y_info))
            y_info += 50
        
        # Atualizar animação do cursor do controle
        from core.gamepad_manager import gerenciador_gamepad
        if not hasattr(desenhar_tela_fim_jogo, '_animacao_cursor'):
            desenhar_tela_fim_jogo._animacao_cursor = 0.0
        velocidade_animacao_cursor = 3.0
        desenhar_tela_fim_jogo._animacao_cursor += dt * velocidade_animacao_cursor
        if desenhar_tela_fim_jogo._animacao_cursor >= 1.0:
            desenhar_tela_fim_jogo._animacao_cursor = 0.0
        
        for i, (nome, chave) in enumerate(opcoes):
            y = offset_opcoes + i * 60
            
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
                opcao_fundo = pygame.Surface((caixa_largura - 40, 60), pygame.SRCALPHA)
                opcao_fundo.fill(cor_fundo)
                tela.blit(opcao_fundo, (caixa_x + 20, y - 5))
            
            if i == opcao_atual and gerenciador_gamepad.obter_numero_controles() > 0:
                import math
                tamanho_cursor = 3 + int(2 * abs(math.sin(desenhar_tela_fim_jogo._animacao_cursor * math.pi)))
                opcao_rect = pygame.Rect(caixa_x + 20, y - 5, caixa_largura - 40, 60)
                cursor_rect = pygame.Rect(
                    opcao_rect.x - tamanho_cursor,
                    opcao_rect.y - tamanho_cursor,
                    opcao_rect.width + tamanho_cursor * 2,
                    opcao_rect.height + tamanho_cursor * 2
                )
                pygame.draw.rect(tela, (0, 200, 255), cursor_rect, 3)
            
            texto = render_text(nome, 24, cor_texto, bold=True, pixel_style=True)
            tela.blit(texto, (caixa_x + 30, y))
    
    def processar_tela_resultados_finais(ev, estado_resultados):
        """Processa eventos da tela de resultados finais quando ambos jogadores terminaram"""
        if estado_resultados is None:
            return None
        
        opcoes = estado_resultados.get("opcoes", [])
        opcao_atual = estado_resultados.get("opcao_atual", 0)
        
        caixa_largura = 1200
        caixa_altura = 650
        caixa_x = (LARGURA - caixa_largura) // 2
        caixa_y = (ALTURA - caixa_altura) // 2
        
        if ev.type == pygame.QUIT:
            return "sair"
        
        from core.gamepad_manager import gerenciador_gamepad
        if gerenciador_gamepad.obter_numero_controles() > 0:
            from core.menu_controles import processar_eventos_controle_menu
            tempo_atual = pygame.time.get_ticks()
            resultado_controle = processar_eventos_controle_menu(ev, opcao_atual, len(opcoes), joystick_id=0, tempo_atual=tempo_atual)
            if resultado_controle:
                acao = resultado_controle.get("acao")
                if acao == "esquerda":
                    if "opcao" in resultado_controle:
                        estado_resultados["opcao_atual"] = resultado_controle["opcao"]
                    else:
                        estado_resultados["opcao_atual"] = (opcao_atual - 1) % len(opcoes)
                    return None
                elif acao == "direita":
                    if "opcao" in resultado_controle:
                        estado_resultados["opcao_atual"] = resultado_controle["opcao"]
                    else:
                        estado_resultados["opcao_atual"] = (opcao_atual + 1) % len(opcoes)
                    return None
                elif acao == "confirmar":
                    chave = opcoes[opcao_atual][1]
                    return chave
                elif acao == "cancelar":
                    return "menu"
                return None
        
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            mouse_x, mouse_y = ev.pos
            base_y = int(ALTURA * 0.85)
            botao_largura = 180
            botao_altura = 50
            espacamento = 15
            
            for i, (nome, chave) in enumerate(opcoes):
                if i == 0:
                    x = (LARGURA - botao_largura) // 2 - botao_largura - espacamento
                elif i == 1:
                    x = (LARGURA - botao_largura) // 2
                else:
                    x = (LARGURA - botao_largura) // 2 + botao_largura + espacamento
                
                botao_rect = pygame.Rect(x, base_y, botao_largura, botao_altura)
                if botao_rect.collidepoint(mouse_x, mouse_y):
                    return chave
        
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                return "menu"
            elif ev.key in (pygame.K_LEFT, pygame.K_a):
                estado_resultados["opcao_atual"] = (opcao_atual - 1) % len(opcoes)
            elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                estado_resultados["opcao_atual"] = (opcao_atual + 1) % len(opcoes)
            elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                chave = opcoes[opcao_atual][1]
                return chave
        
        return None
    
    def desenhar_tela_resultados_finais(tela, estado_resultados, dt):
        """Desenha tela de resultados finais quando ambos jogadores terminaram"""
        if estado_resultados is None:
            return
        
        from core.menu import render_text
        from core.gamepad_manager import gerenciador_gamepad
        import math
        
        resultados = estado_resultados.get("resultados", [])
        opcoes = estado_resultados.get("opcoes", [])
        opcao_atual = estado_resultados.get("opcao_atual", 0)
        
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        tela.blit(overlay, (0, 0))
        
        caixa_largura = 1200
        caixa_altura = 650
        caixa_x = (LARGURA - caixa_largura) // 2
        caixa_y = (ALTURA - caixa_altura) // 2
        
        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 200))
        tela.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(tela, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        titulo = render_text("RESULTADOS FINAIS", 40, (255, 255, 255), bold=True, pixel_style=True)
        titulo_x = caixa_x + (caixa_largura - titulo.get_width()) // 2
        tela.blit(titulo, (titulo_x, caixa_y + 20))
        
        fonte_cabecalho = pygame.font.SysFont("consolas", 18, bold=True)
        fonte_item = pygame.font.SysFont("consolas", 16)
        
        x_pos = caixa_x + 30
        x_nome = x_pos + 60
        x_tempo = x_nome + 200
        x_trofeu = x_tempo + 150
        x_dinheiro = x_trofeu + 80
        y_cabecalho = caixa_y + 80
        
        cabecalho_pos = fonte_cabecalho.render("POS", True, (255, 255, 255))
        cabecalho_nome = fonte_cabecalho.render("NOME", True, (255, 255, 255))
        cabecalho_tempo = fonte_cabecalho.render("TEMPO", True, (255, 255, 255))
        cabecalho_trofeu = fonte_cabecalho.render("TROFÉU", True, (255, 255, 255))
        cabecalho_dinheiro = fonte_cabecalho.render("DINHEIRO", True, (255, 255, 255))
        
        tela.blit(cabecalho_pos, (x_pos, y_cabecalho))
        tela.blit(cabecalho_nome, (x_nome, y_cabecalho))
        tela.blit(cabecalho_tempo, (x_tempo, y_cabecalho))
        tela.blit(cabecalho_trofeu, (x_trofeu, y_cabecalho))
        tela.blit(cabecalho_dinheiro, (x_dinheiro, y_cabecalho))
        
        pygame.draw.line(tela, (128, 128, 128), (caixa_x + 20, y_cabecalho + 30), (caixa_x + caixa_largura - 20, y_cabecalho + 30), 2)
        
        y_atual = y_cabecalho + 45
        for resultado in resultados:
            pos = resultado.get("posicao", 0)
            nome = resultado.get("nome", "")
            tempo = resultado.get("tempo", None)
            trofeu = resultado.get("trofeu", None)
            dinheiro = resultado.get("dinheiro", 0)
            
            cor_pos = (255, 215, 0) if pos == 1 else (192, 192, 192) if pos == 2 else (205, 127, 50) if pos == 3 else (255, 255, 255)
            texto_pos = fonte_item.render(f"{pos}º", True, cor_pos)
            tela.blit(texto_pos, (x_pos, y_atual))
            
            texto_nome = fonte_item.render(nome, True, (255, 255, 255))
            tela.blit(texto_nome, (x_nome, y_atual))
            
            if tempo is not None:
                mm = int(tempo // 60)
                ss = tempo % 60
                tempo_str = f"{mm:02d}:{ss:05.2f}"
                texto_tempo = fonte_item.render(tempo_str, True, (0, 255, 0))
            else:
                texto_tempo = fonte_item.render("--:--.--", True, (128, 128, 128))
            tela.blit(texto_tempo, (x_tempo, y_atual))
            
            if trofeu:
                trofeu_pequeno = pygame.transform.scale(trofeu, (25, 25))
                trofeu_rect = trofeu_pequeno.get_rect(center=(x_trofeu + 20, y_atual + 10))
                tela.blit(trofeu_pequeno, trofeu_rect)
            
            texto_dinheiro = fonte_item.render(f"${dinheiro}", True, (100, 255, 100))
            tela.blit(texto_dinheiro, (x_dinheiro, y_atual))
            
            y_atual += 40
        
        base_y = int(ALTURA * 0.85)
        botao_largura = 180
        botao_altura = 50
        espacamento = 15
        
        if not hasattr(desenhar_tela_resultados_finais, '_animacao_cursor'):
            desenhar_tela_resultados_finais._animacao_cursor = 0.0
        velocidade_animacao_cursor = 3.0
        desenhar_tela_resultados_finais._animacao_cursor += dt * velocidade_animacao_cursor
        if desenhar_tela_resultados_finais._animacao_cursor >= 1.0:
            desenhar_tela_resultados_finais._animacao_cursor = 0.0
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        for i, (nome, chave) in enumerate(opcoes):
            if i == 0:
                x = (LARGURA - botao_largura) // 2 - botao_largura - espacamento
            elif i == 1:
                x = (LARGURA - botao_largura) // 2
            else:
                x = (LARGURA - botao_largura) // 2 + botao_largura + espacamento
            
            botao_rect = pygame.Rect(x, base_y, botao_largura, botao_altura)
            botao_hover = botao_rect.collidepoint(mouse_x, mouse_y)
            
            if i == opcao_atual:
                cor_fundo = (0, 200, 255, 50)
                cor_texto = (0, 200, 255)
            elif botao_hover:
                cor_fundo = (0, 200, 255, 30)
                cor_texto = (0, 200, 255)
            else:
                cor_fundo = (0, 0, 0, 0)
                cor_texto = (255, 255, 255)
            
            if cor_fundo[3] > 0:
                botao_fundo = pygame.Surface((botao_largura, botao_altura), pygame.SRCALPHA)
                botao_fundo.fill(cor_fundo)
                tela.blit(botao_fundo, (x, base_y))
            
            # Cursor do controle
            if i == opcao_atual and gerenciador_gamepad.obter_numero_controles() > 0:
                tamanho_cursor = 3 + int(2 * abs(math.sin(desenhar_tela_resultados_finais._animacao_cursor * math.pi)))
                cursor_rect = pygame.Rect(
                    botao_rect.x - tamanho_cursor,
                    botao_rect.y - tamanho_cursor,
                    botao_rect.width + tamanho_cursor * 2,
                    botao_rect.height + tamanho_cursor * 2
                )
                pygame.draw.rect(tela, (0, 200, 255), cursor_rect, 3)
            
            texto = render_text(nome, 20, cor_texto, bold=True, pixel_style=True)
            texto_x = x + (botao_largura - texto.get_width()) // 2
            texto_y = base_y + (botao_altura - texto.get_height()) // 2
            tela.blit(texto, (texto_x, texto_y))
    
    # Validar índices de carros antes de acessar
    # Usar variável local para evitar conflito com imports dentro da função
    carros_disponiveis = CARROS_DISPONIVEIS
    
    if carro_selecionado_p1 is None or carro_selecionado_p1 < 0 or carro_selecionado_p1 >= len(carros_disponiveis):
        carro_selecionado_p1 = 0
    if carro_selecionado_p2 is None or carro_selecionado_p2 < 0 or carro_selecionado_p2 >= len(carros_disponiveis):
        carro_selecionado_p2 = 1 if len(carros_disponiveis) > 1 else 0
    
    carro_p1 = carros_disponiveis[carro_selecionado_p1]
    carro_p2 = carros_disponiveis[carro_selecionado_p2]

    if pista_tiles is not None:
        pos_inicial_tiles = pista_tiles.obter_posicao_inicial()
        centro_x, centro_y = 2500, 2500
        pos_inicial_p1 = (centro_x + pos_inicial_tiles[0], centro_y + pos_inicial_tiles[1])
        
        if superficie_pista_renderizada is not None:
            if not pista_tiles.verificar_se_na_pista(pos_inicial_p1[0], pos_inicial_p1[1]):
                print(f"AVISO: Posição inicial {pos_inicial_p1} está na grama! Tentando ajustar...")
                for offset_x in range(-50, 51, 10):
                    for offset_y in range(-50, 51, 10):
                        test_x = pos_inicial_p1[0] + offset_x
                        test_y = pos_inicial_p1[1] + offset_y
                        if pista_tiles.verificar_se_na_pista(test_x, test_y):
                            pos_inicial_p1 = (test_x, test_y)
                            print(f"Posição ajustada para: {pos_inicial_p1}")
                            break
                    else:
                        continue
                    break
        
        spawn_points_editor = carregar_spawn_points(numero_pista)
        
        if spawn_points_editor and len(spawn_points_editor) > 0:
            print(f"Carregados {len(spawn_points_editor)} spawn points do editor")
            
            num_ias_1_jogador = 3
            num_ias_2_jogadores = 2
            
            spawn_disponiveis = list(spawn_points_editor)
            random.shuffle(spawn_disponiveis)
            
            if modo_jogo == ModoJogo.DOIS_JOGADORES:
                if len(spawn_disponiveis) >= 2:
                    pos_inicial_p1 = spawn_disponiveis.pop(0)
                    pos_inicial_p2 = spawn_disponiveis.pop(0)
                else:
                    pos_base = spawn_disponiveis[0]
                    offset_lateral = 50
                    pos_inicial_p1 = (pos_base[0] - offset_lateral, pos_base[1])
                    pos_inicial_p2 = (pos_base[0] + offset_lateral, pos_base[1])
                    spawn_disponiveis = []
                
                num_ias = num_ias_2_jogadores
                posicoes_ia = []
                for i in range(num_ias):
                    if len(spawn_disponiveis) > 0:
                        posicoes_ia.append(spawn_disponiveis.pop(0))
                    else:
                        pos_base_x, pos_base_y = pos_inicial_p2
                        offset_lateral = 50 * (i + 1)
                        posicoes_ia.append((pos_base_x + offset_lateral, pos_base_y))
                
                pos_inicial_IA = None
            else:
                if len(spawn_disponiveis) >= 1:
                    pos_inicial_p1 = spawn_disponiveis.pop(0)
                    pos_inicial_p2 = None
                else:
                    pos_inicial_p1 = spawn_points_editor[0]
                    pos_inicial_p2 = None
                    spawn_disponiveis = []
                
                num_ias = num_ias_1_jogador
                posicoes_ia = []
                for i in range(num_ias):
                    if len(spawn_disponiveis) > 0:
                        posicoes_ia.append(spawn_disponiveis.pop(0))
                    else:
                        pos_base_x, pos_base_y = pos_inicial_p1
                        offset_lateral = 50 * (i + 1)
                        posicoes_ia.append((pos_base_x + offset_lateral, pos_base_y))
                
                pos_inicial_IA = None
            
            print(f"Spawn points selecionados aleatoriamente:")
            print(f"  P1: {pos_inicial_p1}")
            if pos_inicial_p2:
                print(f"  P2: {pos_inicial_p2}")
            for i, pos_ia in enumerate(posicoes_ia):
                print(f"  IA-{i+1}: {pos_ia}")
        else:
            offset_lateral = 50
            pos_base_x, pos_base_y = pos_inicial_p1
            
            num_ias_1_jogador = 3
            num_ias_2_jogadores = 2
            
            if modo_jogo == ModoJogo.DOIS_JOGADORES:
                pos_inicial_p1 = (pos_base_x - offset_lateral, pos_base_y)
                pos_inicial_p2 = (pos_base_x + offset_lateral, pos_base_y)
                posicoes_ia = [
                    (pos_base_x + offset_lateral * 2, pos_base_y),
                    (pos_base_x + offset_lateral * 3, pos_base_y)
                ]
                pos_inicial_IA = None
            else:
                pos_inicial_p1 = (pos_base_x, pos_base_y)
                pos_inicial_p2 = None
                posicoes_ia = [
                    (pos_base_x - offset_lateral, pos_base_y),
                    (pos_base_x + offset_lateral, pos_base_y),
                    (pos_base_x + offset_lateral * 2, pos_base_y)
                ]
                pos_inicial_IA = None
        
        print(f"Posição inicial P1 (tiles): {pos_inicial_p1}")
        if pos_inicial_p2:
            print(f"Posição inicial P2 (tiles): {pos_inicial_p2}")
        if 'posicoes_ia' in locals():
            for i, pos in enumerate(posicoes_ia):
                print(f"Posição inicial IA-{i+1} (tiles): {pos}")

    carros = []

    upgrades_p1 = gerenciador_progresso.obter_todos_upgrades(carro_p1["prefixo_cor"])
    multiplicador_p1 = carro_p1.get("multiplicador_base", 1.0)
    carro1 = CarroFisica(
        pos_inicial_p1[0], pos_inicial_p1[1],
        carro_p1["prefixo_cor"],
        (pygame.K_w, pygame.K_d, pygame.K_a, pygame.K_s),
        turbo_key=TURBO_P1,
        nome=carro_p1["nome"],
        tipo_tracao=carro_p1.get("tipo_tracao", CarroFisica.TRACAO_TRASEIRA),
        upgrades=upgrades_p1,
        multiplicador_base=multiplicador_p1
    )
    carros.append(carro1)
    
    camera.cx = carro1.x
    camera.cy = carro1.y
    print(f"Câmera inicializada na posição do carro: ({camera.cx}, {camera.cy})")

    carro2 = None
    if modo_jogo == ModoJogo.DOIS_JOGADORES and pos_inicial_p2 is not None:
        upgrades_p2 = gerenciador_progresso.obter_todos_upgrades(carro_p2["prefixo_cor"])
        multiplicador_p2 = carro_p2.get("multiplicador_base", 1.0)
        carro2 = CarroFisica(
            pos_inicial_p2[0], pos_inicial_p2[1],
            carro_p2["prefixo_cor"],
            (pygame.K_UP, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_DOWN),
            turbo_key=TURBO_P2,
            nome=carro_p2["nome"],
            tipo_tracao=carro_p2.get("tipo_tracao", CarroFisica.TRACAO_TRASEIRA),
            upgrades=upgrades_p2,
            multiplicador_base=multiplicador_p2
        )
        carros.append(carro2)

    carros_ia = []
    if tipo_jogo != TipoJogo.DRIFT and tipo_jogo != TipoJogo.GHOST:
        if modo_jogo == ModoJogo.DOIS_JOGADORES:
            num_ias = 2
        else:
            num_ias = 3
        
        carros_disponiveis_ia = CARROS_DISPONIVEIS.copy()
        if carro_p1 in carros_disponiveis_ia:
            carros_disponiveis_ia.remove(carro_p1)
        if modo_jogo == ModoJogo.DOIS_JOGADORES and carro_p2 in carros_disponiveis_ia:
            carros_disponiveis_ia.remove(carro_p2)
        
        carros_selecionados_ia = random.sample(carros_disponiveis_ia, min(num_ias, len(carros_disponiveis_ia)))
        
        # Selecionar nomes aleatórios únicos para os bots
        nomes_disponiveis = NOMES_BOTS.copy()
        random.shuffle(nomes_disponiveis)
        
        for i, (pos_ia, carro_data) in enumerate(zip(posicoes_ia, carros_selecionados_ia)):
            upgrades_ia = gerenciador_progresso.obter_todos_upgrades(carro_data["prefixo_cor"])
            multiplicador_ia = carro_data.get("multiplicador_base", 1.0)
            
            # Atribuir nome aleatório ao bot
            nome_bot = nomes_disponiveis[i] if i < len(nomes_disponiveis) else f"BOT-{i+1}"
            
            carro_ia = CarroFisica(
                pos_ia[0], pos_ia[1],
                carro_data["prefixo_cor"],
                (0, 0, 0, 0),
                turbo_key=pygame.K_t,
                nome=nome_bot,
                tipo_tracao=carro_data.get("tipo_tracao", CarroFisica.TRACAO_TRASEIRA),
                upgrades=upgrades_ia,
                multiplicador_base=multiplicador_ia
            )
            carro_ia.eh_bot = True
            carro_ia.skidmarks.max_skidmarks = 80
            carros_ia.append(carro_ia)
            carros.append(carro_ia)
            print(f"{nome_bot} usando carro: {carro_data['nome']} ({carro_data['prefixo_cor']})")

    for c in carros:
        corrida.registrar_carro(c)
    
    ghost_recorder_p1 = GhostRecorder(intervalo_gravacao=0.05)
    ghost_player_p1 = None
    
    principal._colisoes_na_corrida = 0
    from core.particulas import EmissorColisao
    principal._emissor_colisao = EmissorColisao()
    
    if (tipo_jogo == TipoJogo.GHOST or tipo_jogo == TipoJogo.DRIFT) and modo_jogo == ModoJogo.UM_JOGADOR:
        frames_ghost = gerenciador_ghosts.obter_ghost(numero_pista)
        if frames_ghost:
            ghost_player_p1 = GhostPlayer(frames_ghost)
            print(f"Ghost carregado para pista {numero_pista} ({len(frames_ghost)} frames)")
        elif tipo_jogo == TipoJogo.GHOST:
            print(f"AVISO: Modo Ghost selecionado mas não há ghost disponível para pista {numero_pista}")

    camera.set_alvo(carro1)

    hud = HUD()
    mostrar_hud = True

    drift_scoring = DriftScoring()
    drift_scoring_p2 = DriftScoring() if (modo_jogo == ModoJogo.DOIS_JOGADORES and tipo_jogo == TipoJogo.DRIFT) else None
    mostrar_drift_hud = tipo_jogo == TipoJogo.DRIFT

    camera_p1 = None
    camera_p2 = None
    if modo_jogo == ModoJogo.DOIS_JOGADORES and carro2 is not None:
        metade_largura = LARGURA // 2
        camera_p1 = Camera(metade_largura, ALTURA, largura_pista, altura_pista, zoom=1.6)
        camera_p2 = Camera(metade_largura, ALTURA, largura_pista, altura_pista, zoom=1.6)
        camera_p1.cx = 2500 + offset_x_superficie
        camera_p1.cy = 2500 + offset_y_superficie
        camera_p2.cx = 2500 + offset_x_superficie
        camera_p2.cy = 2500 + offset_y_superficie
        camera_p1.offset_x = -offset_x_superficie
        camera_p1.offset_y = -offset_y_superficie
        camera_p2.offset_x = -offset_x_superficie
        camera_p2.offset_y = -offset_y_superficie

    checkpoints_ia = []
    if checkpoints:
        for cp in checkpoints:
            if isinstance(cp, (list, tuple)) and len(cp) >= 2:
                checkpoints_ia.append((float(cp[0]), float(cp[1])))
    
    print(f"Checkpoints passados para IA: {len(checkpoints_ia)}")
    if checkpoints_ia:
        print(f"Primeiro checkpoint da IA: {checkpoints_ia[0]}")
    
    instancias_ia = []
    personalidades_usadas = []
    for i, carro_ia in enumerate(carros_ia):
        personalidades_disponiveis = IA.PERSONALIDADES.copy()
        if len(personalidades_usadas) >= len(IA.PERSONALIDADES):
            personalidades_usadas = []
        
        personalidade = random.choice(personalidades_disponiveis)
        personalidades_usadas.append(personalidade)
        
        instancia_ia = IA(checkpoints_ia, nome=carro_ia.nome, dificuldade=dificuldade_ia, personalidade=personalidade)
        instancias_ia.append(instancia_ia)
        print(f"Criada {instancia_ia.nome} com {len(checkpoints_ia)} checkpoints - Personalidade: {personalidade}")
    
    IA2 = instancias_ia[0] if len(instancias_ia) > 0 else None
    IA3 = instancias_ia[1] if len(instancias_ia) > 1 else None
    IA4 = instancias_ia[2] if len(instancias_ia) > 2 else None
    debug_IA = True

    jogo_pausado = False
    jogo_terminado = False
    pontuacao_final = 0
    tela_fim_mostrada = False
    acao_fim_jogo = None
    estado_fim_jogo = None
    
    tela_fim_mostrada_p1 = False
    tela_fim_mostrada_p2 = False
    estado_fim_jogo_p1 = None
    estado_fim_jogo_p2 = None
    estado_resultados_finais = None
    pontuacao_final_p1 = 0
    pontuacao_final_p2 = 0
    p1_espectador = False
    p2_espectador = False
    
    opcao_pausa_selecionada = 0
    opcoes_pausa = ["Continuar", "Reiniciar", "Voltar ao Menu"]

    arrastando_checkpoint = False
    checkpoint_em_arraste = -1
    arrastando_camera = False
    ultimo_clique_tempo = 0
    debounce_tempo = 200

    if CONFIGURACOES["audio"]["musica_habilitada"] and CONFIGURACOES["audio"]["musica_no_jogo"]:
        gerenciador_musica.definir_volume(CONFIGURACOES["audio"]["volume_musica"])
        if not gerenciador_musica.musica_tocando:
            if CONFIGURACOES["audio"]["musica_aleatoria"]:
                gerenciador_musica.musica_aleatoria()
            else:
                gerenciador_musica.tocar_musica()

    rodando = True
    alguem_venceu = False
    dt_fixo = 1.0 / 120.0
    acumulador_dt = 0.0
    max_dt = 0.1

    while rodando:
        dt = relogio.tick(fps_max) / 1000.0
        dt = min(dt, max_dt)
        acumulador_dt += dt
        
        if corrida.iniciada and not jogo_pausado:
            gerenciador_estatisticas.registrar_tempo_jogado(dt)

        gerenciador_musica.verificar_fim_musica()
        
        # Processar navegação contínua (hold) para telas de fim de jogo e resultados finais
        from core.gamepad_manager import gerenciador_gamepad
        if gerenciador_gamepad.obter_numero_controles() > 0:
            from core.menu_controles import processar_navegacao_hold
            tempo_atual = pygame.time.get_ticks()
            resultado_hold = processar_navegacao_hold(joystick_id=0, tempo_atual=tempo_atual)
            if resultado_hold:
                acao = resultado_hold.get("acao")
                # Navegação contínua para tela de resultados finais (apenas para hold, eventos individuais são processados no loop de eventos)
                # Esta parte só processa quando o botão está sendo mantido pressionado
                if estado_resultados_finais is not None and resultado_hold.get("fonte") == "hold":
                    opcoes = estado_resultados_finais.get("opcoes", [])
                    if acao == "esquerda":
                        estado_resultados_finais["opcao_atual"] = (estado_resultados_finais["opcao_atual"] - 1) % len(opcoes)
                    elif acao == "direita":
                        estado_resultados_finais["opcao_atual"] = (estado_resultados_finais["opcao_atual"] + 1) % len(opcoes)
                # Navegação contínua para telas de fim de jogo no modo 2 jogadores
                elif modo_jogo == ModoJogo.DOIS_JOGADORES:
                    if estado_fim_jogo_p1 is not None:
                        # Calcular opções disponíveis para player 1
                        # Se o outro jogador ainda não terminou, mostrar apenas "ASSISTIR JOGADOR"
                        if estado_fim_jogo_p2 is None:
                            opcoes_p1 = [
                                ("ASSISTIR JOGADOR", "espectador")
                            ]
                        else:
                            # Ambos terminaram - mostrar todas as opções
                            opcoes_p1 = [
                                ("REINICIAR JOGO", "reiniciar"),
                                ("TROCAR CARRO", "trocar_carro"),
                                ("MENU PRINCIPAL", "menu")
                            ]
                        
                        if acao == "cima":
                            estado_fim_jogo_p1[6] = (estado_fim_jogo_p1[6] - 1) % len(opcoes_p1)
                        elif acao == "baixo":
                            estado_fim_jogo_p1[6] = (estado_fim_jogo_p1[6] + 1) % len(opcoes_p1)
                    if estado_fim_jogo_p2 is not None:
                        # Calcular opções disponíveis para player 2
                        # Se o outro jogador ainda não terminou, mostrar apenas "ASSISTIR JOGADOR"
                        if estado_fim_jogo_p1 is None:
                            opcoes_p2 = [
                                ("ASSISTIR JOGADOR", "espectador")
                            ]
                        else:
                            # Ambos terminaram - mostrar todas as opções
                            opcoes_p2 = [
                                ("REINICIAR JOGO", "reiniciar"),
                                ("TROCAR CARRO", "trocar_carro"),
                                ("MENU PRINCIPAL", "menu")
                            ]
                        
                        if acao == "cima":
                            estado_fim_jogo_p2[6] = (estado_fim_jogo_p2[6] - 1) % len(opcoes_p2)
                        elif acao == "baixo":
                            estado_fim_jogo_p2[6] = (estado_fim_jogo_p2[6] + 1) % len(opcoes_p2)
                # Navegação contínua para tela de resultados finais no modo singleplayer
                elif modo_jogo != ModoJogo.DOIS_JOGADORES and estado_resultados_finais is not None:
                    opcoes = estado_resultados_finais.get("opcoes", [])
                    if acao == "esquerda":
                        estado_resultados_finais["opcao_atual"] = (estado_resultados_finais["opcao_atual"] - 1) % len(opcoes)
                    elif acao == "direita":
                        estado_resultados_finais["opcao_atual"] = (estado_resultados_finais["opcao_atual"] + 1) % len(opcoes)

        eventos = list(pygame.event.get())
        
        # Atualizar Rex (se ativo e modo 1 jogador)
        if rex.ativo and modo_jogo == ModoJogo.UM_JOGADOR:
            rex.atualizar(dt)
        
        # Atualizar Akira (se ativa e modo 1 jogador)
        if akira.ativo and modo_jogo == ModoJogo.UM_JOGADOR:
            akira.atualizar(dt)
        
        # Processar Akira primeiro (se ativa, modo 1 jogador, NÃO estiver em corrida e não estiver na tela de fim de jogo ou resultados finais) - tem prioridade sobre todos
        if akira.ativo and modo_jogo == ModoJogo.UM_JOGADOR and not corrida.iniciada and estado_fim_jogo is None and estado_fim_jogo_p1 is None and estado_fim_jogo_p2 is None and estado_resultados_finais is None:
            akira.processar_eventos(eventos)
        
        # Processar Rex (se ativo, modo 1 jogador, NÃO estiver em corrida, Akira não estiver ativa e não estiver na tela de fim de jogo ou resultados finais) - tem prioridade sobre Crank
        if rex.ativo and modo_jogo == ModoJogo.UM_JOGADOR and not corrida.iniciada and not akira.ativo and estado_fim_jogo is None and estado_fim_jogo_p1 is None and estado_fim_jogo_p2 is None and estado_resultados_finais is None:
            rex.processar_eventos(eventos)
        
        # Processar Crank (se ativo, modo 1 jogador, NÃO estiver em corrida, Akira/Rex não estiverem ativos e não estiver na tela de fim de jogo ou resultados finais) - tem prioridade sobre mercador alien
        if crank.ativo and modo_jogo == ModoJogo.UM_JOGADOR and not corrida.iniciada and not akira.ativo and not rex.ativo and estado_fim_jogo is None and estado_fim_jogo_p1 is None and estado_fim_jogo_p2 is None and estado_resultados_finais is None:
            resultado_crank = crank.processar_eventos(eventos)
            if resultado_crank == "fechado":
                crank.fechar()
        
        # Processar mercador alien (se ativo, modo 1 jogador, NÃO estiver em corrida, Akira/Rex/Crank não estiverem ativos e não estiver na tela de fim de jogo ou resultados finais)
        if mercador_alien.ativo and modo_jogo == ModoJogo.UM_JOGADOR and not corrida.iniciada and not akira.ativo and not rex.ativo and not crank.ativo and estado_fim_jogo is None and estado_fim_jogo_p1 is None and estado_fim_jogo_p2 is None and estado_resultados_finais is None:
            resultado_mercador = mercador_alien.processar_eventos(eventos, prefixo_cor=carro_p1["prefixo_cor"])
            if resultado_mercador in ["comprado", "recusado", "fechado", "erro"]:
                if resultado_mercador == "comprado":
                    from core.popup_musica import popup_musica
                    popup_musica.mostrar("Compra realizada com sucesso!", tipo="outra")
                elif resultado_mercador == "recusado":
                    mercador_alien.fechar()
                elif resultado_mercador == "fechado":
                    mercador_alien.fechar()
                # Continuar processando eventos normalmente
        
        for ev in eventos:
            if modo_jogo == ModoJogo.DOIS_JOGADORES:
                evento_processado = False
                
                # Processar eventos da tela de resultados finais PRIMEIRO (se estiver ativa)
                if estado_resultados_finais is not None:
                    acao_resultados = processar_tela_resultados_finais(ev, estado_resultados_finais)
                    # Se processou evento de controle, marcar como processado e continuar
                    if gerenciador_gamepad.obter_numero_controles() > 0 and ev.type in (pygame.JOYHATMOTION, pygame.JOYBUTTONDOWN, pygame.JOYAXISMOTION):
                        evento_processado = True
                        # Se foi apenas navegação (retornou None), continuar sem processar outros eventos
                        if acao_resultados is None:
                            continue
                    if acao_resultados:
                        evento_processado = True
                        if acao_resultados == "reiniciar":
                            return principal(carro_selecionado_p1, carro_selecionado_p2, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                        elif acao_resultados == "trocar_carro":
                            from core.menu import selecionar_carros_loop
                            resultado = selecionar_carros_loop(tela)
                            if resultado and len(resultado) == 2:
                                carro_p1_idx, carro_p2_idx = resultado
                                if carro_p1_idx is not None and carro_p2_idx is not None:
                                    if 0 <= carro_p1_idx < len(CARROS_DISPONIVEIS) and 0 <= carro_p2_idx < len(CARROS_DISPONIVEIS):
                                        return principal(carro_p1_idx, carro_p2_idx, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                            estado_resultados_finais = None
                            estado_fim_jogo_p1 = None
                            estado_fim_jogo_p2 = None
                            continue
                        elif acao_resultados == "menu" or acao_resultados == "sair":
                            rodando = False
                            return
                    # Se processou evento de resultados finais (mouse/teclado), não processar outros eventos
                    elif ev.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                        evento_processado = True
                        continue
                    # Se processou qualquer evento na tela de resultados finais, não processar outros
                    if evento_processado:
                        continue
                
                if estado_fim_jogo_p1 is not None:
                    if hasattr(ev, 'pos') and ev.pos[0] >= LARGURA // 2:
                        pass
                    else:
                        acao = processar_tela_fim_jogo(ev, estado_fim_jogo_p1, lado='esquerdo')
                        if acao:
                            evento_processado = True
                            if acao == "reiniciar":
                                return principal(carro_selecionado_p1, carro_selecionado_p2, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                            elif acao == "trocar_carro":
                                from core.menu import selecionar_carros_loop
                                resultado = selecionar_carros_loop(tela)
                                if resultado and len(resultado) == 2:
                                    carro_p1_idx, carro_p2_idx = resultado
                                    if carro_p1_idx is not None and carro_p2_idx is not None:
                                        if 0 <= carro_p1_idx < len(CARROS_DISPONIVEIS) and 0 <= carro_p2_idx < len(CARROS_DISPONIVEIS):
                                            return principal(carro_p1_idx, carro_p2_idx, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                                estado_fim_jogo_p1 = None
                                # Após fechar tela de fim de jogo P1, verificar se Rex deve aparecer (primeira corrida, só se P2 também terminou e modo 1 jogador)
                                if modo_jogo == ModoJogo.UM_JOGADOR and estado_fim_jogo_p2 is None and not rex.ativo and not crank.ativo and not mercador_alien.ativo:
                                    rex.verificar_aparecer()
                                # Verificar se o Crank deve aparecer (após o Rex, modo 1 jogador)
                                if modo_jogo == ModoJogo.UM_JOGADOR and estado_fim_jogo_p2 is None and not rex.ativo and not crank.ativo:
                                    crank.verificar_aparecer_pos_corrida()
                                # Verificar se o mercador alien deve aparecer (após o Crank, modo 1 jogador)
                                if modo_jogo == ModoJogo.UM_JOGADOR and estado_fim_jogo_p2 is None and not rex.ativo and not mercador_alien.ativo and not crank.ativo:
                                    mercador_alien.verificar_aparecer(contexto="corrida")
                                continue
                            elif acao == "espectador":
                                p1_espectador = True
                                estado_fim_jogo_p1 = None
                                # Após fechar tela de fim de jogo P1, verificar se Rex deve aparecer (primeira corrida, só se P2 também terminou e modo 1 jogador)
                                if modo_jogo == ModoJogo.UM_JOGADOR and estado_fim_jogo_p2 is None and not rex.ativo and not crank.ativo and not mercador_alien.ativo:
                                    rex.verificar_aparecer()
                                # Verificar se o Crank deve aparecer (após o Rex, modo 1 jogador)
                                if modo_jogo == ModoJogo.UM_JOGADOR and estado_fim_jogo_p2 is None and not rex.ativo and not crank.ativo:
                                    crank.verificar_aparecer_pos_corrida()
                                # Verificar se o mercador alien deve aparecer (após o Crank, modo 1 jogador)
                                if modo_jogo == ModoJogo.UM_JOGADOR and estado_fim_jogo_p2 is None and not rex.ativo and not mercador_alien.ativo and not crank.ativo:
                                    mercador_alien.verificar_aparecer(contexto="corrida")
                                continue
                            elif acao == "menu" or acao == "sair":
                                rodando = False
                                return
                        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                            if estado_fim_jogo_p1 is None:
                                jogo_pausado = not jogo_pausado
                                opcao_pausa_selecionada = 0
                                evento_processado = True
                        elif ev.type == pygame.JOYBUTTONDOWN and ev.button == 6:
                            if estado_fim_jogo_p1 is None:
                                jogo_pausado = not jogo_pausado
                                opcao_pausa_selecionada = 0
                                evento_processado = True
                
                if estado_fim_jogo_p2 is not None and not evento_processado:
                    if hasattr(ev, 'pos') and ev.pos[0] < LARGURA // 2:
                        pass
                    else:
                        acao = processar_tela_fim_jogo(ev, estado_fim_jogo_p2, lado='direito')
                        if acao:
                            evento_processado = True
                            if acao == "reiniciar":
                                return principal(carro_selecionado_p1, carro_selecionado_p2, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                            elif acao == "trocar_carro":
                                from core.menu import selecionar_carros_loop
                                resultado = selecionar_carros_loop(tela)
                                if resultado and len(resultado) == 2:
                                    carro_p1_idx, carro_p2_idx = resultado
                                    # Validar índices antes de retornar
                                    if carro_p1_idx is not None and carro_p2_idx is not None:
                                        # Usar CARROS_DISPONIVEIS do escopo global
                                        if 0 <= carro_p1_idx < len(CARROS_DISPONIVEIS) and 0 <= carro_p2_idx < len(CARROS_DISPONIVEIS):
                                            return principal(carro_p1_idx, carro_p2_idx, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                                estado_fim_jogo_p2 = None
                                continue
                            elif acao == "espectador":
                                # Player 2 vira espectador do player 1
                                p2_espectador = True
                                estado_fim_jogo_p2 = None
                                # Não verificar Crank aqui pois P1 ainda não terminou
                                continue
                            elif acao == "menu" or acao == "sair":
                                rodando = False
                                return
                        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                            # Se não há tela de fim de jogo, pausar o jogo
                            if estado_fim_jogo_p2 is None:
                                jogo_pausado = not jogo_pausado
                                opcao_pausa_selecionada = 0
                                evento_processado = True
                        elif ev.type == pygame.JOYBUTTONDOWN and ev.button == 6:
                            # Botão Options/Start do PS5 - pausar o jogo (mesma lógica do ESC)
                            # PS5: botão 6 = Options/Start
                            if estado_fim_jogo_p2 is None:
                                jogo_pausado = not jogo_pausado
                                opcao_pausa_selecionada = 0
                                evento_processado = True
                
                # Verificar se ambos terminaram para mostrar tela de resultados finais
                # Verificar se ambos os carros finalizaram (não apenas se os estados existem)
                # Isso garante que mesmo se um jogador virou espectador, quando ambos terminarem, vai para resultados finais
                carro1_finalizou = corrida.finalizou.get(carro1, False) if carro1 is not None else False
                carro2_finalizou = corrida.finalizou.get(carro2, False) if carro2 is not None else False
                ambos_finalizaram = carro1_finalizou and carro2_finalizou
                
                if ambos_finalizaram and estado_resultados_finais is None:
                    # Coletar informações de todos os carros
                    todos_carros = [c for c in carros if c is not None]
                    resultados = []
                    
                    for carro in todos_carros:
                        posicao = obter_posicao_jogador(carro, todos_carros)
                        tempo = corrida.tempo_final.get(carro)
                        recompensa = 0
                        trofeu = None
                        
                        # Determinar nome
                        if carro == carro1:
                            nome = "JOGADOR 1"
                            # Se estado_fim_jogo_p1 existe, usar dele, senão calcular recompensa baseado na posição
                            if estado_fim_jogo_p1 is not None:
                                recompensa = estado_fim_jogo_p1[5]  # recompensa_dinheiro_p1
                                trofeu = estado_fim_jogo_p1[2]  # trofeu_p1
                            else:
                                # Player 1 virou espectador, calcular recompensa baseado na posição
                                if posicao == 1:
                                    recompensa = 600 if dificuldade_ia == "facil" else 1500 if dificuldade_ia == "medio" else 3000
                                elif posicao == 2:
                                    recompensa = 300 if dificuldade_ia == "facil" else 750 if dificuldade_ia == "medio" else 1500
                                elif posicao == 3:
                                    recompensa = 150 if dificuldade_ia == "facil" else 400 if dificuldade_ia == "medio" else 800
                                else:
                                    recompensa = 100 if dificuldade_ia == "facil" else 200 if dificuldade_ia == "medio" else 400
                                trofeu = obter_trofeu_por_posicao(posicao) if posicao else trofeu_vazio
                        elif carro == carro2:
                            nome = "JOGADOR 2"
                            # Se estado_fim_jogo_p2 existe, usar dele, senão calcular recompensa baseado na posição
                            if estado_fim_jogo_p2 is not None:
                                recompensa = estado_fim_jogo_p2[5]  # recompensa_dinheiro_p2
                                trofeu = estado_fim_jogo_p2[2]  # trofeu_p2
                            else:
                                # Player 2 virou espectador, calcular recompensa baseado na posição
                                if posicao == 1:
                                    recompensa = 600 if dificuldade_ia == "facil" else 1500 if dificuldade_ia == "medio" else 3000
                                elif posicao == 2:
                                    recompensa = 300 if dificuldade_ia == "facil" else 750 if dificuldade_ia == "medio" else 1500
                                elif posicao == 3:
                                    recompensa = 150 if dificuldade_ia == "facil" else 400 if dificuldade_ia == "medio" else 800
                                else:
                                    recompensa = 100 if dificuldade_ia == "facil" else 200 if dificuldade_ia == "medio" else 400
                                trofeu = obter_trofeu_por_posicao(posicao) if posicao else trofeu_vazio
                        else:
                            nome = carro.nome if hasattr(carro, 'nome') else "IA"
                            # Calcular recompensa para bots baseado na posição
                            if posicao == 1:
                                recompensa = 600 if dificuldade_ia == "facil" else 1500 if dificuldade_ia == "medio" else 3000
                            elif posicao == 2:
                                recompensa = 300 if dificuldade_ia == "facil" else 750 if dificuldade_ia == "medio" else 1500
                            elif posicao == 3:
                                recompensa = 150 if dificuldade_ia == "facil" else 400 if dificuldade_ia == "medio" else 800
                            else:
                                recompensa = 100 if dificuldade_ia == "facil" else 200 if dificuldade_ia == "medio" else 400
                            trofeu = obter_trofeu_por_posicao(posicao) if posicao else trofeu_vazio
                        
                        resultados.append({
                            "posicao": posicao,
                            "nome": nome,
                            "tempo": tempo,
                            "trofeu": trofeu,
                            "dinheiro": recompensa
                        })
                    
                    # Ordenar por posição
                    resultados.sort(key=lambda x: x["posicao"] if x["posicao"] else 999)
                    
                    estado_resultados_finais = {
                        "resultados": resultados,
                        "opcoes": [
                            ("TROCAR CARRO", "trocar_carro"),
                            ("REINICIAR JOGO", "reiniciar"),
                            ("MENU PRINCIPAL", "menu")
                        ],
                        "opcao_atual": 0
                    }
                    # Limpar estados das telas individuais para evitar sobreposição
                    estado_fim_jogo_p1 = None
                    estado_fim_jogo_p2 = None
                
                if evento_processado:
                    continue
            else:
                # Modo singleplayer - processar tela de resultados finais
                if estado_resultados_finais is not None:
                    acao = processar_tela_resultados_finais(ev, estado_resultados_finais)
                    if acao:
                        if acao == "reiniciar":
                            return principal(carro_selecionado_p1, carro_selecionado_p2, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                        elif acao == "trocar_carro":
                            from core.menu import selecionar_carros_loop
                            resultado = selecionar_carros_loop(tela)
                            if resultado and len(resultado) == 2:
                                carro_p1_idx, carro_p2_idx = resultado
                                # Validar índices antes de retornar
                                if carro_p1_idx is not None and carro_p2_idx is not None:
                                    if 0 <= carro_p1_idx < len(CARROS_DISPONIVEIS) and 0 <= carro_p2_idx < len(CARROS_DISPONIVEIS):
                                        return principal(carro_p1_idx, carro_p2_idx, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                            estado_resultados_finais = None
                            # Após fechar tela de resultados finais, verificar se Rex deve aparecer (primeira corrida, modo 1 jogador)
                            if modo_jogo == ModoJogo.UM_JOGADOR and not rex.ativo and not crank.ativo and not mercador_alien.ativo:
                                rex.verificar_aparecer()
                            # Verificar se o Crank deve aparecer (após o Rex, modo 1 jogador)
                            if modo_jogo == ModoJogo.UM_JOGADOR and not rex.ativo and not crank.ativo:
                                crank.verificar_aparecer_pos_corrida()
                            # Verificar se o mercador alien deve aparecer (após o Crank, modo 1 jogador)
                            if modo_jogo == ModoJogo.UM_JOGADOR and not rex.ativo and not mercador_alien.ativo and not crank.ativo:
                                mercador_alien.verificar_aparecer(contexto="corrida")
                            continue
                        elif acao == "menu" or acao == "sair":
                            gerenciador_estatisticas.finalizar_sessao()
                            rodando = False
                            return
                    continue
                elif estado_fim_jogo is not None:
                    # Fallback para tela individual (caso ainda exista algum código que use)
                    acao = processar_tela_fim_jogo(ev, estado_fim_jogo)
                    if acao:
                        if acao == "reiniciar":
                            return principal(carro_selecionado_p1, carro_selecionado_p2, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                        elif acao == "trocar_carro":
                            from core.menu import selecionar_carros_loop
                            resultado = selecionar_carros_loop(tela)
                            if resultado and len(resultado) == 2:
                                carro_p1_idx, carro_p2_idx = resultado
                                # Validar índices antes de retornar
                                if carro_p1_idx is not None and carro_p2_idx is not None:
                                    if 0 <= carro_p1_idx < len(CARROS_DISPONIVEIS) and 0 <= carro_p2_idx < len(CARROS_DISPONIVEIS):
                                        return principal(carro_p1_idx, carro_p2_idx, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                            estado_fim_jogo = None
                            # Após fechar tela de fim de jogo, verificar se Rex deve aparecer (primeira corrida, modo 1 jogador)
                            if modo_jogo == ModoJogo.UM_JOGADOR and not rex.ativo and not crank.ativo and not mercador_alien.ativo:
                                rex.verificar_aparecer()
                            # Verificar se o Crank deve aparecer (após o Rex, modo 1 jogador)
                            if modo_jogo == ModoJogo.UM_JOGADOR and not rex.ativo and not crank.ativo:
                                crank.verificar_aparecer_pos_corrida()
                            # Verificar se o mercador alien deve aparecer (após o Crank, modo 1 jogador)
                            if modo_jogo == ModoJogo.UM_JOGADOR and not rex.ativo and not mercador_alien.ativo and not crank.ativo:
                                mercador_alien.verificar_aparecer(contexto="corrida")
                            continue
                        elif acao == "menu" or acao == "sair":
                            gerenciador_estatisticas.finalizar_sessao()
                            rodando = False
                            return
                    continue
            
            if ev.type == pygame.QUIT:
                rodando = False

            # Processar cliques do mouse no menu de pausa ANTES de outros eventos
            if jogo_pausado and ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                caixa_largura = 500
                caixa_altura = 400
                caixa_x = (LARGURA - caixa_largura) // 2
                caixa_y = (ALTURA - caixa_altura) // 2
                mouse_x, mouse_y = ev.pos
                mouse_in_caixa = (caixa_x <= mouse_x <= caixa_x + caixa_largura and
                                caixa_y <= mouse_y <= caixa_y + caixa_altura)
                if mouse_in_caixa:
                    opcoes_pausa_formatadas = [
                        ("CONTINUAR", "continuar"),
                        ("REINICIAR JOGO", "reiniciar"),
                        ("MENU PRINCIPAL", "menu")
                    ]
                    altura_total_opcoes = len(opcoes_pausa_formatadas) * 60
                    offset_opcoes = caixa_y + caixa_altura - altura_total_opcoes - 20
                    for i, (nome, chave) in enumerate(opcoes_pausa_formatadas):
                        y_opcao = offset_opcoes + i * 60
                        opcao_rect = pygame.Rect(caixa_x + 20, y_opcao - 5, caixa_largura - 40, 60)
                        if opcao_rect.collidepoint(mouse_x, mouse_y):
                            if i == 0:
                                jogo_pausado = False
                            elif i == 1:
                                return principal(carro_selecionado_p1, carro_selecionado_p2, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                            elif i == 2:
                                gerenciador_estatisticas.finalizar_sessao()
                                return
                            break
                # Marcar evento como processado para não ser processado novamente
                continue

            # Processar eventos de controle no menu de pausa ANTES de outros eventos
            if jogo_pausado:
                opcoes_pausa_formatadas = [
                    ("CONTINUAR", "continuar"),
                    ("REINICIAR JOGO", "reiniciar"),
                    ("MENU PRINCIPAL", "menu")
                ]
                controle_processado_pausa = False
                if gerenciador_gamepad.obter_numero_controles() > 0:
                    from core.menu_controles import processar_eventos_controle_menu
                    tempo_atual = pygame.time.get_ticks()
                    resultado_controle = processar_eventos_controle_menu(ev, opcao_pausa_selecionada, len(opcoes_pausa_formatadas), joystick_id=0, tempo_atual=tempo_atual)
                    if resultado_controle:
                        controle_processado_pausa = True
                        acao = resultado_controle.get("acao")
                        if acao == "cima" and "opcao" in resultado_controle:
                            opcao_pausa_selecionada = resultado_controle["opcao"]
                        elif acao == "baixo" and "opcao" in resultado_controle:
                            opcao_pausa_selecionada = resultado_controle["opcao"]
                        elif acao == "confirmar":
                            chave = opcoes_pausa_formatadas[opcao_pausa_selecionada][1]
                            if chave == "continuar":
                                jogo_pausado = False
                            elif chave == "reiniciar":
                                return principal(carro_selecionado_p1, carro_selecionado_p2, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                            elif chave == "menu":
                                gerenciador_estatisticas.finalizar_sessao()
                                return
                        elif acao == "cancelar":
                            # Circle/B para continuar (despausar)
                            jogo_pausado = False
                
                # Se processou evento de controle, não processar outros eventos
                if controle_processado_pausa:
                    continue

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    if modo_jogo == ModoJogo.DOIS_JOGADORES:
                        # No modo 2 jogadores, verificar se há tela de fim de jogo
                        if estado_fim_jogo_p1 is not None or estado_fim_jogo_p2 is not None:
                            # Se há tela de fim de jogo, não fazer nada aqui (já foi processado acima)
                            pass
                        else:
                            # Se não há tela de fim de jogo, pausar o jogo
                            jogo_pausado = not jogo_pausado
                            opcao_pausa_selecionada = 0
                    else:
                        # Modo 1 jogador
                        if estado_fim_jogo is not None:
                            return
                        elif not jogo_terminado:
                            jogo_pausado = not jogo_pausado
                            opcao_pausa_selecionada = 0
            elif ev.type == pygame.JOYBUTTONDOWN:
                from core.gamepad_manager import gerenciador_gamepad
                if ev.button == 6:
                    if modo_jogo == ModoJogo.DOIS_JOGADORES:
                        if estado_fim_jogo_p1 is not None or estado_fim_jogo_p2 is not None:
                            pass
                        else:
                            jogo_pausado = not jogo_pausado
                            opcao_pausa_selecionada = 0
                    else:
                        if estado_fim_jogo is not None:
                            pass
                        elif not jogo_terminado:
                            jogo_pausado = not jogo_pausado
                            opcao_pausa_selecionada = 0
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_F1:
                    debug_IA = not debug_IA
                    IA2.debug = IA3.debug = debug_IA
                elif ev.key == pygame.K_h:
                    mostrar_hud = not mostrar_hud
                elif ev.key == pygame.K_1:
                    dificuldade_ia = "facil"
                elif ev.key == pygame.K_2:
                    dificuldade_ia = "medio"
                elif ev.key == pygame.K_3:
                    dificuldade_ia = "dificil"
                
                if ev.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    if IA2:
                        IA2.dificuldade = dificuldade_ia
                        IA2._configurar_dificuldade()
                    if IA3:
                        IA3.dificuldade = dificuldade_ia
                        IA3._configurar_dificuldade()

                if ev.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                    pass

                # Se o jogo está pausado, processar apenas eventos de pausa
                if jogo_pausado:
                    opcoes_pausa_formatadas = [
                        ("CONTINUAR", "continuar"),
                        ("REINICIAR JOGO", "reiniciar"),
                        ("MENU PRINCIPAL", "menu")
                    ]
                    # Processar eventos de controle no menu de pausa
                    controle_processado_pausa = False
                    if gerenciador_gamepad.obter_numero_controles() > 0:
                        from core.menu_controles import processar_eventos_controle_menu
                        tempo_atual = pygame.time.get_ticks()
                        resultado_controle = processar_eventos_controle_menu(ev, opcao_pausa_selecionada, len(opcoes_pausa_formatadas), joystick_id=0, tempo_atual=tempo_atual)
                        if resultado_controle:
                            controle_processado_pausa = True
                            acao = resultado_controle.get("acao")
                            if acao == "cima" and "opcao" in resultado_controle:
                                opcao_pausa_selecionada = resultado_controle["opcao"]
                            elif acao == "baixo" and "opcao" in resultado_controle:
                                opcao_pausa_selecionada = resultado_controle["opcao"]
                            elif acao == "confirmar":
                                chave = opcoes_pausa_formatadas[opcao_pausa_selecionada][1]
                                if chave == "continuar":
                                    jogo_pausado = False
                                elif chave == "reiniciar":
                                    return principal(carro_selecionado_p1, carro_selecionado_p2, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                                elif chave == "menu":
                                    gerenciador_estatisticas.finalizar_sessao()
                                    return
                            elif acao == "cancelar":
                                # Circle/B para continuar (despausar)
                                jogo_pausado = False
                    
                    # Se processou evento de controle, não processar teclado
                    if controle_processado_pausa:
                        continue
                    
                    # Processar teclado para navegação no menu de pausa
                    if ev.key == pygame.K_UP or ev.key == pygame.K_w:
                        opcao_pausa_selecionada = (opcao_pausa_selecionada - 1) % len(opcoes_pausa_formatadas)
                    elif ev.key == pygame.K_DOWN or ev.key == pygame.K_s:
                        opcao_pausa_selecionada = (opcao_pausa_selecionada + 1) % len(opcoes_pausa_formatadas)
                    elif ev.key == pygame.K_RETURN or ev.key == pygame.K_SPACE:
                        chave = opcoes_pausa_formatadas[opcao_pausa_selecionada][1]
                        if chave == "continuar":
                            jogo_pausado = False
                        elif chave == "reiniciar":
                            return principal(carro_selecionado_p1, carro_selecionado_p2, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                        elif chave == "menu":
                            gerenciador_estatisticas.finalizar_sessao()
                            return
                    elif ev.key == pygame.K_ESCAPE:
                        # ESC também despausa
                        jogo_pausado = False
                    # Não processar outras teclas quando pausado
                    continue
                elif ev.key == pygame.K_SPACE:
                    carro1.ativar_drift()
                elif ev.key in (pygame.K_LSHIFT, pygame.K_RSHIFT) and carro2 is not None:
                    carro2.drift_hold = True

            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # Cliques do mouse no menu de pausa já foram processados acima
                # Se não está pausado, continuar processando normalmente abaixo
                if jogo_pausado:
                    continue

            elif ev.type == pygame.KEYUP:
                if ev.key == pygame.K_SPACE:
                    carro1.desativar_drift()
                if ev.key in (pygame.K_LSHIFT, pygame.K_RSHIFT) and carro2 is not None:
                    carro2.drift_hold = False

            elif ev.type == pygame.MOUSEBUTTONDOWN:
                # Se já processamos o mouse quando pausado acima, não processar aqui
                if jogo_pausado:
                    continue
                if ev.button == 1 and checkpoint_manager.modo_edicao:
                    tempo_atual = pygame.time.get_ticks()
                    if tempo_atual - ultimo_clique_tempo >= debounce_tempo:
                        ultimo_clique_tempo = tempo_atual
                        mundo_x, mundo_y = camera.tela_para_mundo(ev.pos[0], ev.pos[1])
                        indice = checkpoint_manager.encontrar_checkpoint_proximo(mundo_x, mundo_y, 30)
                        if indice >= 0:
                            arrastando_checkpoint = True
                            checkpoint_em_arraste = indice
                            checkpoint_manager.checkpoint_selecionado = indice
                            checkpoint_manager.checkpoint_em_arraste = indice
                        else:
                            mods = pygame.key.get_mods()
                            if mods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL | pygame.KMOD_CTRL):
                                checkpoint_manager.adicionar_checkpoint_na_posicao(ev.pos[0], ev.pos[1], camera)
                            else:
                                arrastando_camera = True
                                checkpoint_manager.checkpoint_selecionado = -1

            elif ev.type == pygame.MOUSEBUTTONUP:
                if ev.button == 1:
                    if arrastando_checkpoint:
                        arrastando_checkpoint = False
                        checkpoint_em_arraste = -1
                        checkpoint_manager.checkpoint_em_arraste = -1
                    elif arrastando_camera:
                        arrastando_camera = False

            elif ev.type == pygame.MOUSEMOTION and checkpoint_manager.modo_edicao:
                if arrastando_checkpoint and checkpoint_em_arraste >= 0:
                    mundo_x, mundo_y = camera.tela_para_mundo(ev.pos[0], ev.pos[1])
                    checkpoint_manager.mover_checkpoint(checkpoint_em_arraste, mundo_x, mundo_y)
                elif arrastando_camera and hasattr(ev, 'rel') and (ev.rel[0] != 0 or ev.rel[1] != 0):
                    sensibilidade = 1.0 / camera.zoom
                    camera.cx -= ev.rel[0] * sensibilidade
                    camera.cy -= ev.rel[1] * sensibilidade

        teclas = pygame.key.get_pressed()

        checkpoint_manager.processar_teclado(teclas)
        checkpoint_manager.processar_teclas_f(teclas)

        if not corrida.iniciada:
            # Verificar se há NPCs ativos (cutscenes) - não iniciar corrida durante cutscenes
            npcs_ativos = (akira.ativo or rex.ativo or crank.ativo or mercador_alien.ativo or glub.ativo)
            
            # Verificar se Akira deve aparecer pré-corrida (modo 1 jogador, primeira vez na pista)
            if modo_jogo == ModoJogo.UM_JOGADOR and tipo_jogo == TipoJogo.CORRIDA and not npcs_ativos:
                numero_pista = mapa_selecionado if mapa_selecionado is not None else 1
                akira.verificar_aparecer_pre_corrida(numero_pista)
                npcs_ativos = akira.ativo  # Atualizar após verificar
            
            corrida.atualizar_contagem(dt, npcs_ativos=npcs_ativos)
        corrida.atualizar_tempo(dt, jogo_pausado)

        if tipo_jogo == TipoJogo.DRIFT and corrida.iniciada:
            if not tela_fim_mostrada_p1 and corrida.finalizou.get(carro1, False):
                pontuacao_final_p1 = drift_scoring.points
                tela_fim_mostrada_p1 = True
                num_checkpoints = len(checkpoints) if checkpoints else 19
                pontuacoes_alvo = obter_pontuacoes_alvo(num_checkpoints, voltas_objetivo, dificuldade_ia)
                trofeu_drift_p1 = obter_trofeu_por_pontuacao(pontuacao_final_p1, pontuacoes_alvo)
                
                if not hasattr(principal, '_recompensa_drift_p1_calculada'):
                    # Recompensas de drift baseadas na dificuldade (como Need for Speed)
                    if dificuldade_ia == "facil":
                        recompensa_drift_p1 = int(pontuacao_final_p1 / 150)
                    elif dificuldade_ia == "medio":
                        recompensa_drift_p1 = int(pontuacao_final_p1 / 120)
                    else:  # dificil
                        recompensa_drift_p1 = int(pontuacao_final_p1 / 100)
                    gerenciador_progresso.adicionar_dinheiro(recompensa_drift_p1)
                    numero_pista = mapa_selecionado if mapa_selecionado is not None else 1
                    chave_recorde = f"{numero_pista}_{voltas_objetivo}"
                    if gerenciador_progresso.registrar_recorde_drift(chave_recorde, pontuacao_final_p1):
                        print(f"Novo recorde de drift na pista {numero_pista} ({voltas_objetivo} voltas): {pontuacao_final_p1:.0f} pontos")
                    voltas_completas = corrida.voltas.get(carro1, 0)
                    gerenciador_achievements.atualizar_estatistica("voltas_drift", voltas_completas)
                    achievements_desbloqueados = gerenciador_achievements.verificar_achievements(gerenciador_progresso)
                    from core.i18n import t
                    for ach in achievements_desbloqueados:
                        nome_traduzido = t(f"achievements.{ach['id']}")
                        popup_achievement.mostrar(nome_traduzido, ach['recompensa'])
                    principal._recompensa_drift_p1_calculada = recompensa_drift_p1
                else:
                    recompensa_drift_p1 = principal._recompensa_drift_p1_calculada
                
                estado_fim_jogo_p1 = [
                    "DRIFT FINALIZADO!",
                    "TODOS OS CHECKPOINTS COLETADOS!",
                    trofeu_drift_p1,
                    None,
                    pontuacao_final_p1,
                    recompensa_drift_p1,
                    0,
                    [0.0, 0.0, 0.0, 0.0]  # 4 opções possíveis (incluindo "ASSISTIR JOGADOR")
                ]
            
            if modo_jogo == ModoJogo.DOIS_JOGADORES and carro2 is not None and drift_scoring_p2 is not None:
                if not tela_fim_mostrada_p2 and corrida.finalizou.get(carro2, False):
                    if estado_fim_jogo_p1 is not None:
                        # Apenas marcar como terminado e calcular dados necessários para resultados finais
                        pontuacao_final_p2 = drift_scoring_p2.points
                        tela_fim_mostrada_p2 = True
                        num_checkpoints = len(checkpoints) if checkpoints else 19
                        pontuacoes_alvo = obter_pontuacoes_alvo(num_checkpoints, voltas_objetivo, dificuldade_ia)
                        trofeu_drift_p2 = obter_trofeu_por_pontuacao(pontuacao_final_p2, pontuacoes_alvo)
                        
                        if not hasattr(principal, '_recompensa_drift_p2_calculada'):
                            # Recompensas de drift baseadas na dificuldade (como Need for Speed)
                            if dificuldade_ia == "facil":
                                recompensa_drift_p2 = int(pontuacao_final_p2 / 150)
                            elif dificuldade_ia == "medio":
                                recompensa_drift_p2 = int(pontuacao_final_p2 / 120)
                            else:  # dificil
                                recompensa_drift_p2 = int(pontuacao_final_p2 / 100)
                            gerenciador_progresso.adicionar_dinheiro(recompensa_drift_p2)
                            numero_pista = mapa_selecionado if mapa_selecionado is not None else 1
                            chave_recorde = f"{numero_pista}_{voltas_objetivo}"
                            if gerenciador_progresso.registrar_recorde_drift(chave_recorde, pontuacao_final_p2):
                                print(f"Novo recorde de drift na pista {numero_pista} ({voltas_objetivo} voltas): {pontuacao_final_p2:.0f} pontos")
                            principal._recompensa_drift_p2_calculada = recompensa_drift_p2
                        else:
                            recompensa_drift_p2 = principal._recompensa_drift_p2_calculada
                        
                        estado_fim_jogo_p2 = [
                            "DRIFT FINALIZADO!",
                            "TODOS OS CHECKPOINTS COLETADOS!",
                            trofeu_drift_p2,
                            None,
                            pontuacao_final_p2,
                            recompensa_drift_p2,
                            0,
                            [0.0]
                        ]
                    else:
                        pontuacao_final_p2 = drift_scoring_p2.points
                        tela_fim_mostrada_p2 = True
                        num_checkpoints = len(checkpoints) if checkpoints else 19
                        pontuacoes_alvo = obter_pontuacoes_alvo(num_checkpoints, voltas_objetivo, dificuldade_ia)
                        trofeu_drift_p2 = obter_trofeu_por_pontuacao(pontuacao_final_p2, pontuacoes_alvo)
                        
                        if not hasattr(principal, '_recompensa_drift_p2_calculada'):
                            # Recompensas de drift baseadas na dificuldade (como Need for Speed)
                            if dificuldade_ia == "facil":
                                recompensa_drift_p2 = int(pontuacao_final_p2 / 150)
                            elif dificuldade_ia == "medio":
                                recompensa_drift_p2 = int(pontuacao_final_p2 / 120)
                            else:  # dificil
                                recompensa_drift_p2 = int(pontuacao_final_p2 / 100)
                            gerenciador_progresso.adicionar_dinheiro(recompensa_drift_p2)
                            numero_pista = mapa_selecionado if mapa_selecionado is not None else 1
                            chave_recorde = f"{numero_pista}_{voltas_objetivo}"
                            if gerenciador_progresso.registrar_recorde_drift(chave_recorde, pontuacao_final_p2):
                                print(f"Novo recorde de drift na pista {numero_pista} ({voltas_objetivo} voltas): {pontuacao_final_p2:.0f} pontos")
                            principal._recompensa_drift_p2_calculada = recompensa_drift_p2
                        else:
                            recompensa_drift_p2 = principal._recompensa_drift_p2_calculada
                        
                        estado_fim_jogo_p2 = [
                            "DRIFT FINALIZADO!",
                            "TODOS OS CHECKPOINTS COLETADOS!",
                            trofeu_drift_p2,
                            None,
                            pontuacao_final_p2,
                            recompensa_drift_p2,
                            0,
                            [0.0, 0.0, 0.0, 0.0]  # 4 opções possíveis (incluindo "ASSISTIR JOGADOR")
                        ]
            
            if modo_jogo != ModoJogo.DOIS_JOGADORES:
                if corrida.finalizou.get(carro1, False):
                    jogo_terminado = True
                    pontuacao_final = drift_scoring.points

        if tipo_jogo == TipoJogo.GHOST and corrida.iniciada:
            if modo_jogo == ModoJogo.DOIS_JOGADORES:
                if not tela_fim_mostrada_p1 and corrida.finalizou.get(carro1, False):
                    vencedor_p1 = None
                    recompensa_dinheiro_p1 = 0
                    posicao_jogador_p1 = None
                    
                    todos_carros = [c for c in carros if c is not None]
                    posicao_jogador_p1 = obter_posicao_jogador(carro1, todos_carros)
                    
                    if posicao_jogador_p1 == 1:
                        vencedor_p1 = "JOGADOR 1 VENCEU!"
                        if dificuldade_ia == "facil":
                            recompensa_dinheiro_p1 = 600
                        elif dificuldade_ia == "medio":
                            recompensa_dinheiro_p1 = 1500
                        else:  # dificil
                            recompensa_dinheiro_p1 = 3000
                    elif posicao_jogador_p1 == 2:
                        vencedor_p1 = "CORRIDA FINALIZADA!"
                        if dificuldade_ia == "facil":
                            recompensa_dinheiro_p1 = 300
                        elif dificuldade_ia == "medio":
                            recompensa_dinheiro_p1 = 750
                        else:  # dificil
                            recompensa_dinheiro_p1 = 1500
                    elif posicao_jogador_p1 == 3:
                        vencedor_p1 = "CORRIDA FINALIZADA!"
                        if dificuldade_ia == "facil":
                            recompensa_dinheiro_p1 = 150
                        elif dificuldade_ia == "medio":
                            recompensa_dinheiro_p1 = 400
                        else:  # dificil
                            recompensa_dinheiro_p1 = 800
                    else:
                        vencedor_p1 = "CORRIDA FINALIZADA!"
                        if dificuldade_ia == "facil":
                            recompensa_dinheiro_p1 = 100
                        elif dificuldade_ia == "medio":
                            recompensa_dinheiro_p1 = 200
                        else:  # dificil
                            recompensa_dinheiro_p1 = 400
                    
                    if not hasattr(principal, '_recompensa_corrida_p1_calculada'):
                        gerenciador_progresso.adicionar_dinheiro(recompensa_dinheiro_p1)
                        principal._recompensa_corrida_p1_calculada = recompensa_dinheiro_p1
                    else:
                        recompensa_dinheiro_p1 = principal._recompensa_corrida_p1_calculada
                    
                    tela_fim_mostrada_p1 = True
                    trofeu_p1 = obter_trofeu_por_posicao(posicao_jogador_p1) if posicao_jogador_p1 else trofeu_vazio
                    
                    if posicao_jogador_p1 is not None:
                        tempo_final_p1 = corrida.tempo_final.get(carro1)
                        if tempo_final_p1 is not None:
                            numero_pista = mapa_selecionado if mapa_selecionado is not None else 1
                            
                            # Verificar recorde ANTES de registrar (para comparar com o ghost)
                            recorde_antes = gerenciador_progresso.obter_recorde(numero_pista)
                            
                            novo_recorde = gerenciador_progresso.registrar_recorde(numero_pista, tempo_final_p1)
                            if novo_recorde:
                                print(f"Novo recorde na pista {numero_pista}: {tempo_final_p1:.2f}s")
                                # Atualizar estatística de recordes
                                gerenciador_achievements.atualizar_estatistica("recordes_estabelecidos", incrementar=True)
                            
                            if tipo_jogo == TipoJogo.GHOST:
                                if ghost_recorder_p1 and ghost_recorder_p1.gravando:
                                    salvar_ghost = False
                                    if recorde_antes is None or tempo_final_p1 < recorde_antes:
                                        salvar_ghost = True
                                    
                                    if salvar_ghost:
                                        ghost_recorder_p1.parar_gravacao()
                                        frames_gravados = ghost_recorder_p1.obter_dados()
                                        if frames_gravados and len(frames_gravados) > 0:
                                            # Verificação adicional no método salvar_ghost
                                            gerenciador_ghosts.salvar_ghost(numero_pista, frames_gravados, tempo_final_p1, "GHOST")
                                    else:
                                        # Não é melhor volta, limpar frames para economizar memória
                                        if ghost_recorder_p1 and ghost_recorder_p1.gravando:
                                            ghost_recorder_p1.parar_gravacao()
                                            ghost_recorder_p1.limpar()
                            
                            if posicao_jogador_p1 == 1:
                                gerenciador_progresso.registrar_trofeu(numero_pista, "ouro")
                                if not gerenciador_achievements.esta_desbloqueado("trofeu_ouro"):
                                    if gerenciador_achievements.desbloquear("trofeu_ouro", gerenciador_progresso):
                                        from core.achievements import ACHIEVEMENTS
                                        from core.i18n import t
                                        ach_trofeu = ACHIEVEMENTS["trofeu_ouro"]
                                        nome_traduzido = t("achievements.trofeu_ouro")
                                        popup_achievement.mostrar(nome_traduzido, ach_trofeu['recompensa'])
                            elif posicao_jogador_p1 == 2:
                                gerenciador_progresso.registrar_trofeu(numero_pista, "prata")
                            elif posicao_jogador_p1 == 3:
                                gerenciador_progresso.registrar_trofeu(numero_pista, "bronze")
                            
                            gerenciador_achievements.atualizar_estatistica("corridas_completas", incrementar=True)
                            achievements_desbloqueados = gerenciador_achievements.verificar_achievements(gerenciador_progresso)
                            
                            numero_pista = mapa_selecionado if mapa_selecionado is not None else 1
                            gerenciador_estatisticas.registrar_corrida_completa(numero_pista, posicao_jogador_p1, tempo_final_p1)
                            
                            # Registrar no ranking
                            if posicao_jogador_p1 == 1:
                                gerenciador_ranking.registrar_vitoria_jogador()
                            else:
                                gerenciador_ranking.registrar_derrota_jogador()
                            
                            # Verificar se Akira deve aparecer pós-corrida (modo 1 jogador) - ANTES do Rex
                            if modo_jogo == ModoJogo.UM_JOGADOR:
                                colisoes_na_corrida = getattr(principal, '_colisoes_na_corrida', 0)
                                akira.verificar_aparecer_pos_corrida(posicao_jogador_p1, colisoes_na_corrida, posicao_jogador_p1 == 1)
                            
                            # Verificar se Rex deve aparecer (primeira corrida, modo 1 jogador) - DEPOIS de registrar a corrida
                            if modo_jogo == ModoJogo.UM_JOGADOR:
                                rex.verificar_aparecer()
                            if novo_recorde:
                                gerenciador_estatisticas.registrar_recorde(numero_pista)
                                gerenciador_desafios.atualizar_progresso("estabelecer_recorde", 1, gerenciador_progresso)
                            if posicao_jogador_p1 in [1, 2, 3]:
                                gerenciador_estatisticas.registrar_trofeu()
                            
                            gerenciador_desafios.atualizar_progresso("completar_corridas", 1, gerenciador_progresso)
                            if posicao_jogador_p1 == 1:
                                gerenciador_desafios.atualizar_progresso("vencer_corridas", 1, gerenciador_progresso)
                            
                            colisoes_na_corrida = getattr(principal, '_colisoes_na_corrida', 0)
                            if colisoes_na_corrida == 0:
                                gerenciador_desafios.atualizar_progresso("completar_sem_colisao", 1, gerenciador_progresso)
                            principal._colisoes_na_corrida = 0
                            from core.i18n import t
                            for ach in achievements_desbloqueados:
                                nome_traduzido = t(f"achievements.{ach['id']}")
                                popup_achievement.mostrar(nome_traduzido, ach['recompensa'])
                    
                    tempo_final_formatado_p1 = None
                    if posicao_jogador_p1 is not None:
                        tempo_final_p1 = corrida.tempo_final.get(carro1)
                        if tempo_final_p1 is not None:
                            mm = int(tempo_final_p1 // 60)
                            ss = tempo_final_p1 % 60
                            tempo_final_formatado_p1 = f"Tempo: {mm:02d}:{ss:05.2f}"
                    
                    estado_fim_jogo_p1 = [
                        vencedor_p1,
                        tempo_final_formatado_p1 or "",  # Mostrar tempo ao invés de "CORRIDA FINALIZADA!" duplicado
                        trofeu_p1,
                        posicao_jogador_p1,
                        None,
                        recompensa_dinheiro_p1,
                        0,
                        [0.0, 0.0, 0.0, 0.0]  # 4 opções possíveis (incluindo "ASSISTIR JOGADOR")
                    ]
                
                if carro2 is not None and not tela_fim_mostrada_p2 and corrida.finalizou.get(carro2, False):
                    if estado_fim_jogo_p1 is not None:
                        # Apenas marcar como terminado e calcular dados necessários para resultados finais
                        tela_fim_mostrada_p2 = True
                        todos_carros = [c for c in carros if c is not None]
                        posicao_jogador_p2 = obter_posicao_jogador(carro2, todos_carros)
                        
                        # Calcular recompensa
                        if posicao_jogador_p2 == 1:
                            if dificuldade_ia == "facil":
                                recompensa_dinheiro_p2 = 600
                            elif dificuldade_ia == "medio":
                                recompensa_dinheiro_p2 = 1500
                            else:  # dificil
                                recompensa_dinheiro_p2 = 3000
                        elif posicao_jogador_p2 == 2:
                            if dificuldade_ia == "facil":
                                recompensa_dinheiro_p2 = 300
                            elif dificuldade_ia == "medio":
                                recompensa_dinheiro_p2 = 750
                            else:  # dificil
                                recompensa_dinheiro_p2 = 1500
                        elif posicao_jogador_p2 == 3:
                            if dificuldade_ia == "facil":
                                recompensa_dinheiro_p2 = 150
                            elif dificuldade_ia == "medio":
                                recompensa_dinheiro_p2 = 400
                            else:  # dificil
                                recompensa_dinheiro_p2 = 800
                        else:
                            if dificuldade_ia == "facil":
                                recompensa_dinheiro_p2 = 100
                            elif dificuldade_ia == "medio":
                                recompensa_dinheiro_p2 = 200
                            else:  # dificil
                                recompensa_dinheiro_p2 = 400
                        
                        if not hasattr(principal, '_recompensa_corrida_p2_calculada'):
                            gerenciador_progresso.adicionar_dinheiro(recompensa_dinheiro_p2)
                            principal._recompensa_corrida_p2_calculada = recompensa_dinheiro_p2
                        else:
                            recompensa_dinheiro_p2 = principal._recompensa_corrida_p2_calculada
                        
                        trofeu_p2 = obter_trofeu_por_posicao(posicao_jogador_p2) if posicao_jogador_p2 else trofeu_vazio
                        
                        if posicao_jogador_p2 is not None:
                            tempo_final_p2 = corrida.tempo_final.get(carro2)
                            if tempo_final_p2 is not None:
                                numero_pista = mapa_selecionado if mapa_selecionado is not None else 1
                                
                                if gerenciador_progresso.registrar_recorde(numero_pista, tempo_final_p2):
                                    print(f"Novo recorde na pista {numero_pista}: {tempo_final_p2:.2f}s")
                                
                                if posicao_jogador_p2 == 1:
                                    gerenciador_progresso.registrar_trofeu(numero_pista, "ouro")
                                elif posicao_jogador_p2 == 2:
                                    gerenciador_progresso.registrar_trofeu(numero_pista, "prata")
                                elif posicao_jogador_p2 == 3:
                                    gerenciador_progresso.registrar_trofeu(numero_pista, "bronze")
                        
                        estado_fim_jogo_p2 = [
                            "CORRIDA FINALIZADA!",
                            "",
                            trofeu_p2,
                            posicao_jogador_p2,
                            None,
                            recompensa_dinheiro_p2,
                            0,
                            [0.0]
                        ]
                        # Criar tela de resultados finais imediatamente (não esperar próximo ciclo do loop de eventos)
                        # Duplicar a lógica de criação da tela de resultados finais aqui
                        # Verificar se ambos os carros finalizaram (não apenas se os estados existem)
                        carro1_finalizou = corrida.finalizou.get(carro1, False) if carro1 is not None else False
                        carro2_finalizou = corrida.finalizou.get(carro2, False) if carro2 is not None else False
                        ambos_finalizaram = carro1_finalizou and carro2_finalizou
                        
                        if ambos_finalizaram and estado_resultados_finais is None:
                            todos_carros = [c for c in carros if c is not None]
                            resultados = []
                            
                            for carro in todos_carros:
                                posicao = obter_posicao_jogador(carro, todos_carros)
                                tempo = corrida.tempo_final.get(carro)
                                recompensa = 0
                                trofeu = None
                                
                                if carro == carro1:
                                    nome = "JOGADOR 1"
                                    # Se estado_fim_jogo_p1 existe, usar dele, senão calcular recompensa baseado na posição
                                    if estado_fim_jogo_p1 is not None:
                                        recompensa = estado_fim_jogo_p1[5]
                                        trofeu = estado_fim_jogo_p1[2]
                                    else:
                                        # Player 1 virou espectador, calcular recompensa baseado na posição
                                        if posicao == 1:
                                            recompensa = 600 if dificuldade_ia == "facil" else 1500 if dificuldade_ia == "medio" else 3000
                                        elif posicao == 2:
                                            recompensa = 300 if dificuldade_ia == "facil" else 750 if dificuldade_ia == "medio" else 1500
                                        elif posicao == 3:
                                            recompensa = 150 if dificuldade_ia == "facil" else 400 if dificuldade_ia == "medio" else 800
                                        else:
                                            recompensa = 100 if dificuldade_ia == "facil" else 200 if dificuldade_ia == "medio" else 400
                                        trofeu = obter_trofeu_por_posicao(posicao) if posicao else trofeu_vazio
                                elif carro == carro2:
                                    nome = "JOGADOR 2"
                                    # Se estado_fim_jogo_p2 existe, usar dele, senão calcular recompensa baseado na posição
                                    if estado_fim_jogo_p2 is not None:
                                        recompensa = estado_fim_jogo_p2[5]
                                        trofeu = estado_fim_jogo_p2[2]
                                    else:
                                        # Player 2 virou espectador, calcular recompensa baseado na posição
                                        if posicao == 1:
                                            recompensa = 600 if dificuldade_ia == "facil" else 1500 if dificuldade_ia == "medio" else 3000
                                        elif posicao == 2:
                                            recompensa = 300 if dificuldade_ia == "facil" else 750 if dificuldade_ia == "medio" else 1500
                                        elif posicao == 3:
                                            recompensa = 150 if dificuldade_ia == "facil" else 400 if dificuldade_ia == "medio" else 800
                                        else:
                                            recompensa = 100 if dificuldade_ia == "facil" else 200 if dificuldade_ia == "medio" else 400
                                        trofeu = obter_trofeu_por_posicao(posicao) if posicao else trofeu_vazio
                                else:
                                    nome = carro.nome if hasattr(carro, 'nome') else "IA"
                                    if posicao == 1:
                                        recompensa = 600 if dificuldade_ia == "facil" else 1500 if dificuldade_ia == "medio" else 3000
                                    elif posicao == 2:
                                        recompensa = 300 if dificuldade_ia == "facil" else 750 if dificuldade_ia == "medio" else 1500
                                    elif posicao == 3:
                                        recompensa = 150 if dificuldade_ia == "facil" else 400 if dificuldade_ia == "medio" else 800
                                    else:
                                        recompensa = 100 if dificuldade_ia == "facil" else 200 if dificuldade_ia == "medio" else 400
                                    trofeu = obter_trofeu_por_posicao(posicao) if posicao else trofeu_vazio
                                
                                resultados.append({
                                    "posicao": posicao,
                                    "nome": nome,
                                    "tempo": tempo,
                                    "trofeu": trofeu,
                                    "dinheiro": recompensa
                                })
                            
                            resultados.sort(key=lambda x: x["posicao"] if x["posicao"] else 999)
                            
                            estado_resultados_finais = {
                                "resultados": resultados,
                                "opcoes": [
                                    ("TROCAR CARRO", "trocar_carro"),
                                    ("REINICIAR JOGO", "reiniciar"),
                                    ("MENU PRINCIPAL", "menu")
                                ],
                                "opcao_atual": 0
                            }
                            estado_fim_jogo_p1 = None
                            estado_fim_jogo_p2 = None
                    else:
                        vencedor_p2 = None
                        recompensa_dinheiro_p2 = 0
                        posicao_jogador_p2 = None
                        
                        todos_carros = [c for c in carros if c is not None]
                        posicao_jogador_p2 = obter_posicao_jogador(carro2, todos_carros)
                        
                        if posicao_jogador_p2 == 1:
                            vencedor_p2 = "JOGADOR 2 VENCEU!"
                            if dificuldade_ia == "facil":
                                recompensa_dinheiro_p2 = 600
                            elif dificuldade_ia == "medio":
                                recompensa_dinheiro_p2 = 1500
                            else:  # dificil
                                recompensa_dinheiro_p2 = 3000
                        elif posicao_jogador_p2 == 2:
                            vencedor_p2 = "CORRIDA FINALIZADA!"
                            if dificuldade_ia == "facil":
                                recompensa_dinheiro_p2 = 300
                            elif dificuldade_ia == "medio":
                                recompensa_dinheiro_p2 = 750
                            else:  # dificil
                                recompensa_dinheiro_p2 = 1500
                        elif posicao_jogador_p2 == 3:
                            vencedor_p2 = "CORRIDA FINALIZADA!"
                            if dificuldade_ia == "facil":
                                recompensa_dinheiro_p2 = 150
                            elif dificuldade_ia == "medio":
                                recompensa_dinheiro_p2 = 400
                            else:  # dificil
                                recompensa_dinheiro_p2 = 800
                        else:
                            vencedor_p2 = "CORRIDA FINALIZADA!"
                            if dificuldade_ia == "facil":
                                recompensa_dinheiro_p2 = 100
                            elif dificuldade_ia == "medio":
                                recompensa_dinheiro_p2 = 200
                            else:  # dificil
                                recompensa_dinheiro_p2 = 400
                        
                        if not hasattr(principal, '_recompensa_corrida_p2_calculada'):
                            gerenciador_progresso.adicionar_dinheiro(recompensa_dinheiro_p2)
                            principal._recompensa_corrida_p2_calculada = recompensa_dinheiro_p2
                        else:
                            recompensa_dinheiro_p2 = principal._recompensa_corrida_p2_calculada
                        
                        tela_fim_mostrada_p2 = True
                        trofeu_p2 = obter_trofeu_por_posicao(posicao_jogador_p2) if posicao_jogador_p2 else trofeu_vazio
                        
                        if posicao_jogador_p2 is not None:
                            tempo_final_p2 = corrida.tempo_final.get(carro2)
                            if tempo_final_p2 is not None:
                                numero_pista = mapa_selecionado if mapa_selecionado is not None else 1
                                
                                if gerenciador_progresso.registrar_recorde(numero_pista, tempo_final_p2):
                                    print(f"Novo recorde na pista {numero_pista}: {tempo_final_p2:.2f}s")
                                
                                if posicao_jogador_p2 == 1:
                                    gerenciador_progresso.registrar_trofeu(numero_pista, "ouro")
                                elif posicao_jogador_p2 == 2:
                                    gerenciador_progresso.registrar_trofeu(numero_pista, "prata")
                                elif posicao_jogador_p2 == 3:
                                    gerenciador_progresso.registrar_trofeu(numero_pista, "bronze")
                        
                        tempo_final_formatado_p2 = None
                        if posicao_jogador_p2 is not None:
                            tempo_final_p2 = corrida.tempo_final.get(carro2)
                            if tempo_final_p2 is not None:
                                mm = int(tempo_final_p2 // 60)
                                ss = tempo_final_p2 % 60
                                tempo_final_formatado_p2 = f"Tempo: {mm:02d}:{ss:05.2f}"
                        
                        estado_fim_jogo_p2 = [
                            vencedor_p2,
                            tempo_final_formatado_p2 or "",  # Mostrar tempo ao invés de "CORRIDA FINALIZADA!" duplicado
                            trofeu_p2,
                            posicao_jogador_p2,
                            None,
                            recompensa_dinheiro_p2,
                            0,
                            [0.0, 0.0, 0.0, 0.0]  # 4 opções possíveis (incluindo "ASSISTIR JOGADOR")
                        ]

        if tipo_jogo == TipoJogo.CORRIDA and corrida.iniciada:
            if modo_jogo == ModoJogo.DOIS_JOGADORES:
                # Se player 2 está assistindo player 1 e player 1 terminou, sair do modo espectador
                if p2_espectador and carro1 is not None and corrida.finalizou.get(carro1, False):
                    p2_espectador = False
                
                if not tela_fim_mostrada_p1 and corrida.finalizou.get(carro1, False):
                    vencedor_p1 = None
                    recompensa_dinheiro_p1 = 0
                    posicao_jogador_p1 = None
                    
                    todos_carros = [c for c in carros if c is not None]
                    posicao_jogador_p1 = obter_posicao_jogador(carro1, todos_carros)
                    
                    if posicao_jogador_p1 == 1:
                        vencedor_p1 = "JOGADOR 1 VENCEU!"
                        if dificuldade_ia == "facil":
                            recompensa_dinheiro_p1 = 600
                        elif dificuldade_ia == "medio":
                            recompensa_dinheiro_p1 = 1500
                        else:  # dificil
                            recompensa_dinheiro_p1 = 3000
                    elif posicao_jogador_p1 == 2:
                        vencedor_p1 = "CORRIDA FINALIZADA!"
                        if dificuldade_ia == "facil":
                            recompensa_dinheiro_p1 = 300
                        elif dificuldade_ia == "medio":
                            recompensa_dinheiro_p1 = 750
                        else:  # dificil
                            recompensa_dinheiro_p1 = 1500
                    elif posicao_jogador_p1 == 3:
                        vencedor_p1 = "CORRIDA FINALIZADA!"
                        if dificuldade_ia == "facil":
                            recompensa_dinheiro_p1 = 150
                        elif dificuldade_ia == "medio":
                            recompensa_dinheiro_p1 = 400
                        else:  # dificil
                            recompensa_dinheiro_p1 = 800
                    else:
                        vencedor_p1 = "CORRIDA FINALIZADA!"
                        if dificuldade_ia == "facil":
                            recompensa_dinheiro_p1 = 100
                        elif dificuldade_ia == "medio":
                            recompensa_dinheiro_p1 = 200
                        else:  # dificil
                            recompensa_dinheiro_p1 = 400
                    
                    if not hasattr(principal, '_recompensa_corrida_p1_calculada'):
                        gerenciador_progresso.adicionar_dinheiro(recompensa_dinheiro_p1)
                        principal._recompensa_corrida_p1_calculada = recompensa_dinheiro_p1
                    else:
                        recompensa_dinheiro_p1 = principal._recompensa_corrida_p1_calculada
                    
                    tela_fim_mostrada_p1 = True
                    trofeu_p1 = obter_trofeu_por_posicao(posicao_jogador_p1) if posicao_jogador_p1 else trofeu_vazio
                    
                    if posicao_jogador_p1 is not None:
                        tempo_final_p1 = corrida.tempo_final.get(carro1)
                        if tempo_final_p1 is not None:
                            numero_pista = mapa_selecionado if mapa_selecionado is not None else 1
                            
                            novo_recorde = gerenciador_progresso.registrar_recorde(numero_pista, tempo_final_p1)
                            if novo_recorde:
                                print(f"Novo recorde na pista {numero_pista}: {tempo_final_p1:.2f}s")
                                gerenciador_achievements.atualizar_estatistica("recordes_estabelecidos", incrementar=True)
                            
                            if posicao_jogador_p1 == 1:
                                gerenciador_progresso.registrar_trofeu(numero_pista, "ouro")
                                if not gerenciador_achievements.esta_desbloqueado("trofeu_ouro"):
                                    if gerenciador_achievements.desbloquear("trofeu_ouro", gerenciador_progresso):
                                        from core.achievements import ACHIEVEMENTS
                                        from core.i18n import t
                                        ach_trofeu = ACHIEVEMENTS["trofeu_ouro"]
                                        nome_traduzido = t("achievements.trofeu_ouro")
                                        popup_achievement.mostrar(nome_traduzido, ach_trofeu['recompensa'])
                            elif posicao_jogador_p1 == 2:
                                gerenciador_progresso.registrar_trofeu(numero_pista, "prata")
                            elif posicao_jogador_p1 == 3:
                                gerenciador_progresso.registrar_trofeu(numero_pista, "bronze")
                            
                            gerenciador_achievements.atualizar_estatistica("corridas_completas", incrementar=True)
                            achievements_desbloqueados = gerenciador_achievements.verificar_achievements(gerenciador_progresso)
                            
                            numero_pista = mapa_selecionado if mapa_selecionado is not None else 1
                            gerenciador_estatisticas.registrar_corrida_completa(numero_pista, posicao_jogador_p1, tempo_final_p1)
                            # Verificar se Rex deve aparecer (primeira corrida, modo 1 jogador) - DEPOIS de registrar a corrida
                            if modo_jogo == ModoJogo.UM_JOGADOR:
                                rex.verificar_aparecer()
                            if novo_recorde:
                                gerenciador_estatisticas.registrar_recorde(numero_pista)
                                gerenciador_desafios.atualizar_progresso("estabelecer_recorde", 1, gerenciador_progresso)
                            if posicao_jogador_p1 in [1, 2, 3]:
                                gerenciador_estatisticas.registrar_trofeu()
                            
                            gerenciador_desafios.atualizar_progresso("completar_corridas", 1, gerenciador_progresso)
                            if posicao_jogador_p1 == 1:
                                # A vitória já é registrada em registrar_corrida_completa quando posicao_final == 1
                                gerenciador_desafios.atualizar_progresso("vencer_corridas", 1, gerenciador_progresso)
                            
                            colisoes_na_corrida = getattr(principal, '_colisoes_na_corrida', 0)
                            if colisoes_na_corrida == 0:
                                gerenciador_desafios.atualizar_progresso("completar_sem_colisao", 1, gerenciador_progresso)
                            principal._colisoes_na_corrida = 0
                            from core.i18n import t
                            for ach in achievements_desbloqueados:
                                nome_traduzido = t(f"achievements.{ach['id']}")
                                popup_achievement.mostrar(nome_traduzido, ach['recompensa'])
                    
                    tempo_final_formatado_p1 = None
                    if posicao_jogador_p1 is not None:
                        tempo_final_p1 = corrida.tempo_final.get(carro1)
                        if tempo_final_p1 is not None:
                            mm = int(tempo_final_p1 // 60)
                            ss = tempo_final_p1 % 60
                            tempo_final_formatado_p1 = f"Tempo: {mm:02d}:{ss:05.2f}"
                    
                    estado_fim_jogo_p1 = [
                        vencedor_p1,
                        tempo_final_formatado_p1 or "",
                        trofeu_p1,
                        posicao_jogador_p1,
                        None,
                        recompensa_dinheiro_p1,
                        0,
                        [0.0, 0.0, 0.0]
                    ]
                
                if carro2 is not None and not tela_fim_mostrada_p2 and corrida.finalizou.get(carro2, False):
                    if estado_fim_jogo_p1 is not None:
                        # Apenas marcar como terminado e calcular dados necessários para resultados finais
                        tela_fim_mostrada_p2 = True
                        todos_carros = [c for c in carros if c is not None]
                        posicao_jogador_p2 = obter_posicao_jogador(carro2, todos_carros)
                        
                        # Calcular recompensa
                        if posicao_jogador_p2 == 1:
                            if dificuldade_ia == "facil":
                                recompensa_dinheiro_p2 = 600
                            elif dificuldade_ia == "medio":
                                recompensa_dinheiro_p2 = 1500
                            else:  # dificil
                                recompensa_dinheiro_p2 = 3000
                        elif posicao_jogador_p2 == 2:
                            if dificuldade_ia == "facil":
                                recompensa_dinheiro_p2 = 300
                            elif dificuldade_ia == "medio":
                                recompensa_dinheiro_p2 = 750
                            else:  # dificil
                                recompensa_dinheiro_p2 = 1500
                        elif posicao_jogador_p2 == 3:
                            if dificuldade_ia == "facil":
                                recompensa_dinheiro_p2 = 150
                            elif dificuldade_ia == "medio":
                                recompensa_dinheiro_p2 = 400
                            else:  # dificil
                                recompensa_dinheiro_p2 = 800
                        else:
                            if dificuldade_ia == "facil":
                                recompensa_dinheiro_p2 = 100
                            elif dificuldade_ia == "medio":
                                recompensa_dinheiro_p2 = 200
                            else:  # dificil
                                recompensa_dinheiro_p2 = 400
                        
                        if not hasattr(principal, '_recompensa_corrida_p2_calculada'):
                            gerenciador_progresso.adicionar_dinheiro(recompensa_dinheiro_p2)
                            principal._recompensa_corrida_p2_calculada = recompensa_dinheiro_p2
                        else:
                            recompensa_dinheiro_p2 = principal._recompensa_corrida_p2_calculada
                        
                        trofeu_p2 = obter_trofeu_por_posicao(posicao_jogador_p2) if posicao_jogador_p2 else trofeu_vazio
                        
                        if posicao_jogador_p2 is not None:
                            tempo_final_p2 = corrida.tempo_final.get(carro2)
                            if tempo_final_p2 is not None:
                                numero_pista = mapa_selecionado if mapa_selecionado is not None else 1
                                
                                if gerenciador_progresso.registrar_recorde(numero_pista, tempo_final_p2):
                                    print(f"Novo recorde na pista {numero_pista}: {tempo_final_p2:.2f}s")
                                
                                if posicao_jogador_p2 == 1:
                                    gerenciador_progresso.registrar_trofeu(numero_pista, "ouro")
                                elif posicao_jogador_p2 == 2:
                                    gerenciador_progresso.registrar_trofeu(numero_pista, "prata")
                                elif posicao_jogador_p2 == 3:
                                    gerenciador_progresso.registrar_trofeu(numero_pista, "bronze")
                        
                        estado_fim_jogo_p2 = [
                            "CORRIDA FINALIZADA!",
                            "",
                            trofeu_p2,
                            posicao_jogador_p2,
                            None,
                            recompensa_dinheiro_p2,
                            0,
                            [0.0]
                        ]
                        # Criar tela de resultados finais imediatamente (não esperar próximo ciclo do loop de eventos)
                        # Duplicar a lógica de criação da tela de resultados finais aqui
                        # Verificar se ambos os carros finalizaram (não apenas se os estados existem)
                        carro1_finalizou = corrida.finalizou.get(carro1, False) if carro1 is not None else False
                        carro2_finalizou = corrida.finalizou.get(carro2, False) if carro2 is not None else False
                        ambos_finalizaram = carro1_finalizou and carro2_finalizou
                        
                        if ambos_finalizaram and estado_resultados_finais is None:
                            todos_carros = [c for c in carros if c is not None]
                            resultados = []
                            
                            for carro in todos_carros:
                                posicao = obter_posicao_jogador(carro, todos_carros)
                                tempo = corrida.tempo_final.get(carro)
                                recompensa = 0
                                trofeu = None
                                
                                if carro == carro1:
                                    nome = "JOGADOR 1"
                                    # Se estado_fim_jogo_p1 existe, usar dele, senão calcular recompensa baseado na posição
                                    if estado_fim_jogo_p1 is not None:
                                        recompensa = estado_fim_jogo_p1[5]
                                        trofeu = estado_fim_jogo_p1[2]
                                    else:
                                        # Player 1 virou espectador, calcular recompensa baseado na posição
                                        if posicao == 1:
                                            recompensa = 600 if dificuldade_ia == "facil" else 1500 if dificuldade_ia == "medio" else 3000
                                        elif posicao == 2:
                                            recompensa = 300 if dificuldade_ia == "facil" else 750 if dificuldade_ia == "medio" else 1500
                                        elif posicao == 3:
                                            recompensa = 150 if dificuldade_ia == "facil" else 400 if dificuldade_ia == "medio" else 800
                                        else:
                                            recompensa = 100 if dificuldade_ia == "facil" else 200 if dificuldade_ia == "medio" else 400
                                        trofeu = obter_trofeu_por_posicao(posicao) if posicao else trofeu_vazio
                                elif carro == carro2:
                                    nome = "JOGADOR 2"
                                    # Se estado_fim_jogo_p2 existe, usar dele, senão calcular recompensa baseado na posição
                                    if estado_fim_jogo_p2 is not None:
                                        recompensa = estado_fim_jogo_p2[5]
                                        trofeu = estado_fim_jogo_p2[2]
                                    else:
                                        # Player 2 virou espectador, calcular recompensa baseado na posição
                                        if posicao == 1:
                                            recompensa = 600 if dificuldade_ia == "facil" else 1500 if dificuldade_ia == "medio" else 3000
                                        elif posicao == 2:
                                            recompensa = 300 if dificuldade_ia == "facil" else 750 if dificuldade_ia == "medio" else 1500
                                        elif posicao == 3:
                                            recompensa = 150 if dificuldade_ia == "facil" else 400 if dificuldade_ia == "medio" else 800
                                        else:
                                            recompensa = 100 if dificuldade_ia == "facil" else 200 if dificuldade_ia == "medio" else 400
                                        trofeu = obter_trofeu_por_posicao(posicao) if posicao else trofeu_vazio
                                else:
                                    nome = carro.nome if hasattr(carro, 'nome') else "IA"
                                    if posicao == 1:
                                        recompensa = 600 if dificuldade_ia == "facil" else 1500 if dificuldade_ia == "medio" else 3000
                                    elif posicao == 2:
                                        recompensa = 300 if dificuldade_ia == "facil" else 750 if dificuldade_ia == "medio" else 1500
                                    elif posicao == 3:
                                        recompensa = 150 if dificuldade_ia == "facil" else 400 if dificuldade_ia == "medio" else 800
                                    else:
                                        recompensa = 100 if dificuldade_ia == "facil" else 200 if dificuldade_ia == "medio" else 400
                                    trofeu = obter_trofeu_por_posicao(posicao) if posicao else trofeu_vazio
                                
                                resultados.append({
                                    "posicao": posicao,
                                    "nome": nome,
                                    "tempo": tempo,
                                    "trofeu": trofeu,
                                    "dinheiro": recompensa
                                })
                            
                            resultados.sort(key=lambda x: x["posicao"] if x["posicao"] else 999)
                            
                            estado_resultados_finais = {
                                "resultados": resultados,
                                "opcoes": [
                                    ("TROCAR CARRO", "trocar_carro"),
                                    ("REINICIAR JOGO", "reiniciar"),
                                    ("MENU PRINCIPAL", "menu")
                                ],
                                "opcao_atual": 0
                            }
                            estado_fim_jogo_p1 = None
                            estado_fim_jogo_p2 = None
                    else:
                        vencedor_p2 = None
                        recompensa_dinheiro_p2 = 0
                        posicao_jogador_p2 = None
                        
                        todos_carros = [c for c in carros if c is not None]
                        posicao_jogador_p2 = obter_posicao_jogador(carro2, todos_carros)
                        
                        if posicao_jogador_p2 == 1:
                            vencedor_p2 = "JOGADOR 2 VENCEU!"
                            if dificuldade_ia == "facil":
                                recompensa_dinheiro_p2 = 600
                            elif dificuldade_ia == "medio":
                                recompensa_dinheiro_p2 = 1500
                            else:  # dificil
                                recompensa_dinheiro_p2 = 3000
                        elif posicao_jogador_p2 == 2:
                            vencedor_p2 = "CORRIDA FINALIZADA!"
                            if dificuldade_ia == "facil":
                                recompensa_dinheiro_p2 = 300
                            elif dificuldade_ia == "medio":
                                recompensa_dinheiro_p2 = 750
                            else:  # dificil
                                recompensa_dinheiro_p2 = 1500
                        elif posicao_jogador_p2 == 3:
                            vencedor_p2 = "CORRIDA FINALIZADA!"
                            if dificuldade_ia == "facil":
                                recompensa_dinheiro_p2 = 150
                            elif dificuldade_ia == "medio":
                                recompensa_dinheiro_p2 = 400
                            else:  # dificil
                                recompensa_dinheiro_p2 = 800
                        else:
                            vencedor_p2 = "CORRIDA FINALIZADA!"
                            if dificuldade_ia == "facil":
                                recompensa_dinheiro_p2 = 100
                            elif dificuldade_ia == "medio":
                                recompensa_dinheiro_p2 = 200
                            else:  # dificil
                                recompensa_dinheiro_p2 = 400
                        
                        if not hasattr(principal, '_recompensa_corrida_p2_calculada'):
                            gerenciador_progresso.adicionar_dinheiro(recompensa_dinheiro_p2)
                            principal._recompensa_corrida_p2_calculada = recompensa_dinheiro_p2
                        else:
                            recompensa_dinheiro_p2 = principal._recompensa_corrida_p2_calculada
                        
                        tela_fim_mostrada_p2 = True
                        trofeu_p2 = obter_trofeu_por_posicao(posicao_jogador_p2) if posicao_jogador_p2 else trofeu_vazio
                        
                        if posicao_jogador_p2 is not None:
                            tempo_final_p2 = corrida.tempo_final.get(carro2)
                            if tempo_final_p2 is not None:
                                numero_pista = mapa_selecionado if mapa_selecionado is not None else 1
                                
                                if gerenciador_progresso.registrar_recorde(numero_pista, tempo_final_p2):
                                    print(f"Novo recorde na pista {numero_pista}: {tempo_final_p2:.2f}s")
                                
                                if posicao_jogador_p2 == 1:
                                    gerenciador_progresso.registrar_trofeu(numero_pista, "ouro")
                                elif posicao_jogador_p2 == 2:
                                    gerenciador_progresso.registrar_trofeu(numero_pista, "prata")
                                elif posicao_jogador_p2 == 3:
                                    gerenciador_progresso.registrar_trofeu(numero_pista, "bronze")
                        
                        tempo_final_formatado_p2 = None
                        if posicao_jogador_p2 is not None:
                            tempo_final_p2 = corrida.tempo_final.get(carro2)
                            if tempo_final_p2 is not None:
                                mm = int(tempo_final_p2 // 60)
                                ss = tempo_final_p2 % 60
                                tempo_final_formatado_p2 = f"Tempo: {mm:02d}:{ss:05.2f}"
                        
                        estado_fim_jogo_p2 = [
                            vencedor_p2,
                            tempo_final_formatado_p2 or "",
                            trofeu_p2,
                            posicao_jogador_p2,
                            None,
                            recompensa_dinheiro_p2,
                            0,
                            [0.0, 0.0, 0.0]
                        ]

        alguem_venceu = corrida.alguem_finalizou()

        while acumulador_dt >= dt_fixo:
            # Se a tela de resultados finais está ativa, ninguém pode controlar
            pode_controlar_p1 = (modo_jogo != ModoJogo.DOIS_JOGADORES or estado_fim_jogo_p1 is None) and not p1_espectador and estado_resultados_finais is None
            pode_controlar_p2 = (modo_jogo != ModoJogo.DOIS_JOGADORES or estado_fim_jogo_p2 is None) and not p2_espectador and estado_resultados_finais is None
            pode_controlar_geral_p1 = (estado_fim_jogo is None and pode_controlar_p1)
            
            if corrida.pode_controlar() and not jogo_pausado and pode_controlar_geral_p1:
                pos_antes = (carro1.x, carro1.y)
                # Obter inputs de controle ou usar teclado
                inputs_p1 = gerenciador_gamepad.obter_inputs_carro("p1", teclas)
                # Se há inputs de controle mas não tem freio_mao configurado, usar teclado como fallback
                if inputs_p1 is not None and "freio_mao" not in inputs_p1:
                    inputs_p1["freio_mao"] = inputs_p1.get("freio_mao", False) or teclas[pygame.K_SPACE]
                # Se não há controle, passar None para usar teclado normalmente (freio de mão será processado no carro_fisica)
                carro1.atualizar(teclas, None, dt_fixo, camera, superficie_pista_renderizada, inputs_controle=inputs_p1, player_id="p1")
                pos_depois = (carro1.x, carro1.y)
                
                distancia_frame = math.sqrt((pos_depois[0] - pos_antes[0])**2 + (pos_depois[1] - pos_antes[1])**2)
                gerenciador_estatisticas.registrar_distancia(distancia_frame)
                
                if getattr(carro1, 'drift_ativado', False):
                    gerenciador_estatisticas.registrar_drift()
                
                turbo_pressionado = (inputs_p1.get("turbo", False) if inputs_p1 else False) or (teclas[carro1.turbo_key] if carro1.turbo_key else False)
                if turbo_pressionado:
                    gerenciador_estatisticas.registrar_turbo()
                    if not hasattr(principal, '_ultimo_turbo_frame'):
                        principal._ultimo_turbo_frame = -1
                    frame_atual = pygame.time.get_ticks() // 100
                    if frame_atual != principal._ultimo_turbo_frame:
                        principal._ultimo_turbo_frame = frame_atual
                        gerenciador_desafios.atualizar_progresso("usar_turbo", 1, gerenciador_progresso)
                dist_movimento = ((pos_depois[0] - pos_antes[0])**2 + (pos_depois[1] - pos_antes[1])**2)**0.5
                if dist_movimento > 100:
                    print(f"AVISO: Possível teleporte detectado! De {pos_antes} para {pos_depois} (distância: {dist_movimento})")
                    if pista_tiles is not None:
                        carro1.x, carro1.y = pos_antes
                        print(f"Posição restaurada para: {pos_antes}")
                
                # Gravar ghost (para modo relógio ou drift, 1 jogador)
                if (tipo_jogo == TipoJogo.GHOST or tipo_jogo == TipoJogo.DRIFT) and modo_jogo == ModoJogo.UM_JOGADOR:
                    if ghost_recorder_p1:
                        if not ghost_recorder_p1.gravando and corrida.iniciada:
                            ghost_recorder_p1.iniciar_gravacao()
                        if ghost_recorder_p1.gravando:
                            ghost_recorder_p1.atualizar(dt_fixo, carro1)

            if carro2 is not None and not jogo_pausado:
                if modo_jogo == ModoJogo.DOIS_JOGADORES:
                    if pode_controlar_p2 and corrida.pode_controlar():
                        # Obter inputs de controle ou usar teclado
                        inputs_p2 = gerenciador_gamepad.obter_inputs_carro("p2", teclas)
                        # Se há inputs de controle mas não tem freio_mao configurado, usar teclado como fallback
                        if inputs_p2 is not None and "freio_mao" not in inputs_p2:
                            inputs_p2["freio_mao"] = inputs_p2.get("freio_mao", False) or teclas[pygame.K_KP0]
                        # Se não há controle, passar None para usar teclado normalmente (freio de mão será processado no carro_fisica)
                        carro2.atualizar(teclas, None, dt_fixo, camera, superficie_pista_renderizada, inputs_controle=inputs_p2, player_id="p2")
                elif USAR_IA_NO_CARRO_2 and corrida.iniciada:
                    if not corrida.finalizou.get(carro2, False):
                        outros_carros_p2 = [c for c in carros if c != carro2]
                        IA2.controlar(carro2, None, None, dt_fixo, superficie_pista_renderizada, corrida_iniciada=corrida.iniciada, outros_carros=outros_carros_p2)
                elif corrida.pode_controlar():
                    carro2.atualizar(teclas, None, dt_fixo, camera, superficie_pista_renderizada)

            if (tipo_jogo == TipoJogo.GHOST or tipo_jogo == TipoJogo.DRIFT) and modo_jogo == ModoJogo.UM_JOGADOR and ghost_player_p1 is not None:
                if not ghost_player_p1.esta_ativo() and corrida.iniciada:
                    ghost_player_p1.iniciar()
                if ghost_player_p1.esta_ativo():
                    ghost_player_p1.atualizar(dt_fixo)
            
            if not jogo_pausado and corrida.iniciada:
                for i, (carro_ia, instancia_ia) in enumerate(zip(carros_ia, instancias_ia)):
                    if not corrida.finalizou.get(carro_ia, False):
                        pos_antes_bot = (carro_ia.x, carro_ia.y)
                        # Passar lista de outros carros para a IA evitar colisões
                        outros_carros = [c for c in carros if c != carro_ia]
                        instancia_ia.controlar(carro_ia, None, None, dt_fixo, superficie_pista_renderizada, corrida_iniciada=corrida.iniciada, outros_carros=outros_carros)
                        pos_depois_bot = (carro_ia.x, carro_ia.y)
                        dist_movimento_bot = ((pos_depois_bot[0] - pos_antes_bot[0])**2 + (pos_depois_bot[1] - pos_antes_bot[1])**2)**0.5
                        if dist_movimento_bot > 100:
                            print(f"AVISO: Teleporte do bot {carro_ia.nome} detectado! De {pos_antes_bot} para {pos_depois_bot} (distância: {dist_movimento_bot})")
                            if pista_tiles is not None:
                                carro_ia.x, carro_ia.y = pos_antes_bot
                                print(f"Posição do bot {carro_ia.nome} restaurada para: {pos_antes_bot}")

                def detectar_colisao_carros(carro1, carro2):
                    dx = carro1.x - carro2.x
                    dy = carro1.y - carro2.y
                    distancia = math.sqrt(dx*dx + dy*dy)
                    raio_carro = 28.0
                    return distancia < (raio_carro * 2)
                
                def resolver_colisao_carros(carro1, carro2, dt):
                    dx = carro1.x - carro2.x
                    dy = carro1.y - carro2.y
                    distancia = math.sqrt(dx*dx + dy*dy)
                    
                    if distancia < 0.01:
                        distancia = 0.01
                    
                    nx = dx / distancia
                    ny = dy / distancia
                    v1x, v1y = carro1.vx, carro1.vy
                    v2x, v2y = carro2.vx, carro2.vy
                    v_rel = (v1x - v2x) * nx + (v1y - v2y) * ny
                    
                    if v_rel > 0:
                        return
                    
                    distancia_minima = 56.0
                    sobreposicao = (distancia_minima - distancia) * 0.5
                    if sobreposicao > 0:
                        carro1.x += nx * sobreposicao
                        carro1.y += ny * sobreposicao
                        carro2.x -= nx * sobreposicao
                        carro2.y -= ny * sobreposicao
                    
                    massa_total = carro1.m + carro2.m
                    if massa_total > 0:
                        elasticidade = 0.3
                        impulso = (1.0 + elasticidade) * v_rel / massa_total
                        fator_massa1 = carro2.m / massa_total
                        fator_massa2 = carro1.m / massa_total
                        
                        carro1.vx -= nx * impulso * fator_massa1 * carro1.m
                        carro1.vy -= ny * impulso * fator_massa1 * carro1.m
                        carro2.vx += nx * impulso * fator_massa2 * carro2.m
                        carro2.vy += ny * impulso * fator_massa2 * carro2.m
                        
                        ponto_colisao_x = (carro1.x + carro2.x) / 2
                        ponto_colisao_y = (carro1.y + carro2.y) / 2
                        intensidade = min(abs(v_rel) / 50.0, 2.0)
                        if hasattr(principal, '_emissor_colisao'):
                            principal._emissor_colisao.spawn(ponto_colisao_x, ponto_colisao_y, nx, ny, intensidade)
                
                for i, carro_a in enumerate(carros):
                    for j, carro_b in enumerate(carros[i+1:], start=i+1):
                        # Não processar colisões se algum dos carros já terminou
                        carro_a_terminou = corrida.finalizou.get(carro_a, False)
                        carro_b_terminou = corrida.finalizou.get(carro_b, False)
                        if not carro_a_terminou and not carro_b_terminou:
                            if detectar_colisao_carros(carro_a, carro_b):
                                resolver_colisao_carros(carro_a, carro_b, dt_fixo)
                                if carro_a == carro1 or carro_b == carro1:
                                    numero_pista = mapa_selecionado if mapa_selecionado is not None else 1
                                    gerenciador_estatisticas.registrar_colisao(numero_pista)
                                    principal._colisoes_na_corrida = getattr(principal, '_colisoes_na_corrida', 0) + 1
                
                voltas_antes = corrida.voltas.get(carro1, 0)
                for c in carros:
                    corrida.atualizar_progresso_carro(c)
                
                voltas_depois = corrida.voltas.get(carro1, 0)
                if voltas_depois > voltas_antes:
                    numero_pista = mapa_selecionado if mapa_selecionado is not None else 1
                    gerenciador_estatisticas.registrar_volta(numero_pista)
                    gerenciador_desafios.atualizar_progresso("completar_voltas", 1, gerenciador_progresso)

                if tipo_jogo == TipoJogo.DRIFT:
                    jogo_terminado_p1 = (modo_jogo == ModoJogo.DOIS_JOGADORES and estado_fim_jogo_p1 is not None) or (modo_jogo != ModoJogo.DOIS_JOGADORES and jogo_terminado)
                    jogo_terminado_p2 = (modo_jogo == ModoJogo.DOIS_JOGADORES and estado_fim_jogo_p2 is not None)
                    
                    if (pode_controlar_p1 or modo_jogo != ModoJogo.DOIS_JOGADORES) and not jogo_terminado_p1:
                        vlong, vlat = carro1._mundo_para_local(carro1.vx, carro1.vy)
                        velocidade_kmh = abs(vlong) * 0.5
                        angulo_drift = abs(math.degrees(math.atan2(vlat, max(0.1, abs(vlong)))))
                        drift_ativado = getattr(carro1, 'drift_ativado', False)
                        derrapando = getattr(carro1, 'drifting', False)
                        has_skidmarks = derrapando and getattr(carro1, 'drift_intensidade', 0) > 0.05
                        na_grama = getattr(carro1, 'na_grama', False)
                        
                        drift_scoring.update(
                            dt_fixo,
                            angulo_drift,
                            velocidade_kmh,
                            carro1.x,
                            carro1.y,
                            drift_ativado,
                            derrapando,
                            collision_force=0.0,
                            has_skidmarks=has_skidmarks,
                            na_grama=na_grama
                        )
                    
                    if carro2 is not None and drift_scoring_p2 is not None:
                        if (pode_controlar_p2 or modo_jogo != ModoJogo.DOIS_JOGADORES) and not jogo_terminado_p2:
                            vlong2, vlat2 = carro2._mundo_para_local(carro2.vx, carro2.vy)
                            velocidade_kmh2 = abs(vlong2) * 0.5
                            angulo_drift2 = abs(math.degrees(math.atan2(vlat2, max(0.1, abs(vlong2)))))
                            drift_ativado2 = getattr(carro2, 'drift_ativado', False)
                            derrapando2 = getattr(carro2, 'drifting', False)
                            has_skidmarks2 = derrapando2 and getattr(carro2, 'drift_intensidade', 0) > 0.05
                            na_grama2 = getattr(carro2, 'na_grama', False)
                            
                            drift_scoring_p2.update(
                                dt_fixo,
                                angulo_drift2,
                                velocidade_kmh2,
                                carro2.x,
                                carro2.y,
                                drift_ativado2,
                                derrapando2,
                                collision_force=0.0,
                                has_skidmarks=has_skidmarks2,
                                na_grama=na_grama2
                            )

            acumulador_dt -= dt_fixo

        camera.atualizar(dt)

        if camera_p1 is not None and camera_p2 is not None:
            camera_p1.atualizar(dt)
            camera_p2.atualizar(dt)

        if modo_jogo != ModoJogo.DOIS_JOGADORES:
            if hasattr(carro1, 'vx') and hasattr(carro1, 'vy'):
                vel_sq = carro1.vx*carro1.vx + carro1.vy*carro1.vy
                velocidade = math.sqrt(vel_sq) if vel_sq > 0.01 else 0.0
                if hasattr(carro1, 'velocidade_kmh'):
                    velocidade_atual_kmh = carro1.velocidade_kmh
                    velocidade_maxima = gerenciador_achievements.obter_estatistica("velocidade_maxima")
                    if velocidade_atual_kmh > velocidade_maxima:
                        gerenciador_achievements.atualizar_estatistica("velocidade_maxima", velocidade_atual_kmh)
                if velocidade < 20:
                    zoom = 1.8
                elif velocidade < 50:
                    zoom = 1.8 - (velocidade / 50) * 0.4
                elif velocidade < 100:
                    zoom = 1.4 - ((velocidade - 50) / 50) * 0.3
                else:
                    zoom = 1.1 - min((velocidade - 100) / 150, 1.0) * 0.2
                
                zoom = max(0.9, min(1.8, zoom))
                camera.zoom += (zoom - camera.zoom) * min(dt * 2.0, 0.1)
                offset_y = (1.0 - camera.zoom) * 60
                dt_smooth = max(dt, 0.001)

        if modo_jogo == ModoJogo.DOIS_JOGADORES and carro2 is not None:
            metade_largura = LARGURA // 2
            superficie_p1 = pygame.Surface((metade_largura, ALTURA))
            superficie_p2 = pygame.Surface((metade_largura, ALTURA))

            # Se player 1 é espectador, seguir carro 2, senão seguir carro 1
            if p1_espectador and carro2 is not None:
                camera_p1.set_alvo(carro2)
            else:
                camera_p1.set_alvo(carro1)
            
            # Se player 1 é espectador, usar velocidade do carro 2 para zoom
            carro_para_zoom_p1 = carro2 if p1_espectador and carro2 is not None else carro1
            if hasattr(carro_para_zoom_p1, 'vx') and hasattr(carro_para_zoom_p1, 'vy'):
                vel_sq_p1 = carro_para_zoom_p1.vx*carro_para_zoom_p1.vx + carro_para_zoom_p1.vy*carro_para_zoom_p1.vy
                velocidade_p1 = math.sqrt(vel_sq_p1) if vel_sq_p1 > 0.01 else 0.0
                if velocidade_p1 < 20:
                    zoom_p1 = 1.6
                elif velocidade_p1 < 50:
                    zoom_p1 = 1.6 - (velocidade_p1 / 50) * 0.3
                elif velocidade_p1 < 100:
                    zoom_p1 = 1.3 - ((velocidade_p1 - 50) / 50) * 0.2
                else:
                    zoom_p1 = 1.1 - min((velocidade_p1 - 100) / 150, 1.0) * 0.1
                zoom_p1 = max(0.9, min(1.6, zoom_p1))
                camera_p1.zoom += (zoom_p1 - camera_p1.zoom) * dt * 2.0
            
            camera_p1.desenhar_fundo(superficie_p1, img_pista)
            carro1.skidmarks.desenhar(superficie_p1, camera_p1)
            if carro2 is not None:
                carro2.skidmarks.desenhar(superficie_p1, camera_p1)
            for carro_ia in carros_ia:
                if camera_p1.esta_visivel(carro_ia.x, carro_ia.y, 50):
                    carro_ia.skidmarks.desenhar(superficie_p1, camera_p1)
            carros_visiveis_p1 = [carro for carro in carros if camera_p1.esta_visivel(carro.x, carro.y, 30)]
            for carro in carros_visiveis_p1:
                carro.desenhar(superficie_p1, camera=camera_p1)
            # Se player 1 é espectador, mostrar checkpoint do player 2
            if p1_espectador and carro2 is not None:
                checkpoint_atual_p1 = corrida.proximo_checkpoint.get(carro2, 0)
                carro_para_checkpoint = carro2
            else:
                checkpoint_atual_p1 = corrida.proximo_checkpoint.get(carro1, 0)
                carro_para_checkpoint = carro1
            if not corrida.finalizou.get(carro_para_checkpoint, False) and checkpoints:
                idx_cp = checkpoint_atual_p1 % len(checkpoints)
                cp = checkpoints[idx_cp]
                if len(cp) >= 3:
                    cx, cy, angulo = cp[0], cp[1], cp[2]
                else:
                    cx, cy = cp[0], cp[1]
                    angulo = 0
                screen_x, screen_y = camera_p1.mundo_para_tela(cx, cy)
                
                if 0 <= screen_x <= metade_largura and 0 <= screen_y <= ALTURA:
                    CHECKPOINT_LARGURA = 300
                    CHECKPOINT_ESPESSURA = 4
                    superficie_rect = pygame.Surface((CHECKPOINT_LARGURA, CHECKPOINT_ESPESSURA), pygame.SRCALPHA)
                    cor_checkpoint = (0, 255, 255, 80)
                    superficie_rect.fill(cor_checkpoint)
                    pygame.draw.rect(superficie_rect, (0, 255, 255), 
                                    pygame.Rect(0, 0, CHECKPOINT_LARGURA, CHECKPOINT_ESPESSURA), 1)
                    
                    if angulo != 0:
                        superficie_rect = pygame.transform.rotate(superficie_rect, -angulo)
                    
                    rect_rotacionado = superficie_rect.get_rect(center=(int(screen_x), int(screen_y)))
                    
                    superficie_p1.blit(superficie_rect, rect_rotacionado)
                    
                    texto_checkpoint = fonte_checkpoint.render(str(idx_cp + 1), True, (255, 255, 255))
                    texto_rect = texto_checkpoint.get_rect(center=(int(screen_x), int(screen_y)))
                    fundo_texto = pygame.Surface((texto_rect.width + 8, texto_rect.height + 4), pygame.SRCALPHA)
                    fundo_texto.fill((0, 0, 0, 200))
                    superficie_p1.blit(fundo_texto, (texto_rect.x - 4, texto_rect.y - 2))
                    superficie_p1.blit(texto_checkpoint, texto_rect)

            # Se player 2 é espectador, seguir carro 1, senão seguir carro 2
            if p2_espectador and carro1 is not None:
                camera_p2.set_alvo(carro1)
            else:
                camera_p2.set_alvo(carro2)
            
            # Se player 2 é espectador, usar velocidade do carro 1 para zoom
            carro_para_zoom_p2 = carro1 if p2_espectador and carro1 is not None else carro2
            if hasattr(carro_para_zoom_p2, 'vx') and hasattr(carro_para_zoom_p2, 'vy'):
                vel_sq_p2 = carro_para_zoom_p2.vx*carro_para_zoom_p2.vx + carro_para_zoom_p2.vy*carro_para_zoom_p2.vy
                velocidade_p2 = math.sqrt(vel_sq_p2) if vel_sq_p2 > 0.01 else 0.0
                if velocidade_p2 < 20:
                    zoom_p2 = 1.6
                elif velocidade_p2 < 50:
                    zoom_p2 = 1.6 - (velocidade_p2 / 50) * 0.3
                elif velocidade_p2 < 100:
                    zoom_p2 = 1.3 - ((velocidade_p2 - 50) / 50) * 0.2
                else:
                    zoom_p2 = 1.1 - min((velocidade_p2 - 100) / 150, 1.0) * 0.1
                zoom_p2 = max(0.9, min(1.6, zoom_p2))
                camera_p2.zoom += (zoom_p2 - camera_p2.zoom) * dt * 2.0
            
            camera_p2.desenhar_fundo(superficie_p2, img_pista)
            carro1.skidmarks.desenhar(superficie_p2, camera_p2)
            if carro2:
                carro2.skidmarks.desenhar(superficie_p2, camera_p2)
            for carro_ia in carros_ia:
                if camera_p2.esta_visivel(carro_ia.x, carro_ia.y, 50):
                    carro_ia.skidmarks.desenhar(superficie_p2, camera_p2)
            carros_visiveis_p2 = [carro for carro in carros if camera_p2.esta_visivel(carro.x, carro.y, 30)]
            for carro in carros_visiveis_p2:
                carro.desenhar(superficie_p2, camera=camera_p2)
            checkpoint_atual_p2 = corrida.proximo_checkpoint.get(carro2, 0)
            if not corrida.finalizou.get(carro2, False) and checkpoints:
                idx_cp2 = checkpoint_atual_p2 % len(checkpoints)
                cp2 = checkpoints[idx_cp2]
                if len(cp2) >= 3:
                    cx2, cy2, angulo2 = cp2[0], cp2[1], cp2[2]
                else:
                    cx2, cy2 = cp2[0], cp2[1]
                    angulo2 = 0
                screen_x2, screen_y2 = camera_p2.mundo_para_tela(cx2, cy2)
                
                if 0 <= screen_x2 <= metade_largura and 0 <= screen_y2 <= ALTURA:
                    CHECKPOINT_LARGURA = 300
                    CHECKPOINT_ESPESSURA = 4
                    superficie_rect2 = pygame.Surface((CHECKPOINT_LARGURA, CHECKPOINT_ESPESSURA), pygame.SRCALPHA)
                    cor_checkpoint2 = (255, 255, 0, 80)
                    superficie_rect2.fill(cor_checkpoint2)
                    pygame.draw.rect(superficie_rect2, (255, 255, 0), 
                                    pygame.Rect(0, 0, CHECKPOINT_LARGURA, CHECKPOINT_ESPESSURA), 1)
                    
                    if angulo2 != 0:
                        superficie_rect2 = pygame.transform.rotate(superficie_rect2, -angulo2)
                    
                    rect_rotacionado2 = superficie_rect2.get_rect(center=(int(screen_x2), int(screen_y2)))
                    
                    superficie_p2.blit(superficie_rect2, rect_rotacionado2)
                    
                    texto_checkpoint2 = fonte_checkpoint.render(str(idx_cp2 + 1), True, (255, 255, 255))
                    texto_rect2 = texto_checkpoint2.get_rect(center=(int(screen_x2), int(screen_y2)))
                    fundo_texto2 = pygame.Surface((texto_rect2.width + 8, texto_rect2.height + 4), pygame.SRCALPHA)
                    fundo_texto2.fill((0, 0, 0, 200))
                    superficie_p2.blit(fundo_texto2, (texto_rect2.x - 4, texto_rect2.y - 2))
                    superficie_p2.blit(texto_checkpoint2, texto_rect2)
            
            if hasattr(principal, '_emissor_colisao'):
                principal._emissor_colisao.update(dt_fixo)
                principal._emissor_colisao.draw(superficie_p1, camera_p1)
                principal._emissor_colisao.draw(superficie_p2, camera_p2)

            tela.blit(superficie_p1, (0, 0))
            tela.blit(superficie_p2, (metade_largura, 0))
            
            pygame.draw.line(tela, (0, 0, 0), (metade_largura, 0), (metade_largura, ALTURA), 2)
            camera.set_alvo(carro1)

        else:
            if pista_tiles is not None:
                camera.desenhar_fundo(tela, superficie_pista_renderizada)
            else:
                camera.desenhar_fundo(tela, img_pista)
            carro1.skidmarks.desenhar(tela, camera)
            for carro_ia in carros_ia:
                if camera.esta_visivel(carro_ia.x, carro_ia.y, 50):
                    carro_ia.skidmarks.desenhar(tela, camera)
            if carro2 is not None:
                carro2.skidmarks.desenhar(tela, camera)
            
            principal._emissor_colisao.update(dt_fixo)
            principal._emissor_colisao.draw(tela, camera)
            
            if (tipo_jogo == TipoJogo.GHOST or tipo_jogo == TipoJogo.DRIFT) and modo_jogo == ModoJogo.UM_JOGADOR and ghost_player_p1 is not None:
                if ghost_player_p1.esta_ativo() and camera.esta_visivel(ghost_player_p1.x, ghost_player_p1.y, 40):
                    sx, sy = camera.mundo_para_tela(ghost_player_p1.x, ghost_player_p1.y)
                    if hasattr(carro1, 'sprite_base'):
                        angulo_ghost = ghost_player_p1.angulo
                        sprite_ghost = pygame.transform.rotozoom(carro1.sprite_base, angulo_ghost, camera.zoom)
                        # Criar superfície com transparência (alpha = 120/255 = ~47%)
                        sprite_ghost_alpha = sprite_ghost.copy()
                        sprite_ghost_alpha.set_alpha(120)
                        rect_ghost = sprite_ghost_alpha.get_rect(center=(int(sx), int(sy)))
                        tela.blit(sprite_ghost_alpha, rect_ghost.topleft)
            
            if hasattr(principal, '_emissor_colisao'):
                principal._emissor_colisao.update(dt_fixo)
                principal._emissor_colisao.draw(tela, camera)
            
            carros_visiveis = [carro for carro in carros if camera.esta_visivel(carro.x, carro.y, 40)]
            if len(carros_visiveis) > 2:
                carros_ordenados = sorted(
                    carros_visiveis, key=lambda c: (c.x - camera.cx) ** 2 + (c.y - camera.cy) ** 2
                )
            else:
                carros_ordenados = carros_visiveis
            for carro in carros_ordenados:
                carro.desenhar(tela, camera=camera)

        if debug_IA or mostrar_debug:
            if modo_jogo != ModoJogo.DOIS_JOGADORES and carro2 is not None and IA2:
                IA2.desenhar_debug(tela, camera=camera, mostrar_todos_checkpoints=False)
            for instancia_ia in instancias_ia:
                if instancia_ia:
                    instancia_ia.desenhar_debug(tela, camera=camera, mostrar_todos_checkpoints=False)

        if checkpoint_manager.modo_edicao:
            checkpoint_manager.desenhar(tela, camera)

        if checkpoints and not checkpoint_manager.modo_edicao:
            if modo_jogo != ModoJogo.DOIS_JOGADORES:
                checkpoint_atual = corrida.proximo_checkpoint.get(carro1, 0)
                if not corrida.finalizou.get(carro1, False):
                    idx_cp = checkpoint_atual % len(checkpoints)
                    # Obter coordenadas e ângulo do checkpoint
                    cp = checkpoints[idx_cp]
                    if len(cp) >= 3:
                        cx, cy, angulo = cp[0], cp[1], cp[2]
                    else:
                        cx, cy = cp[0], cp[1]
                        angulo = 0
                    
                    screen_x, screen_y = camera.mundo_para_tela(cx, cy)
                    
                    if 0 <= screen_x <= LARGURA and 0 <= screen_y <= ALTURA:
                        CHECKPOINT_LARGURA = 300
                        CHECKPOINT_ESPESSURA = 4
                        superficie_rect = pygame.Surface((CHECKPOINT_LARGURA, CHECKPOINT_ESPESSURA), pygame.SRCALPHA)
                        cor_checkpoint = (0, 255, 255, 80)
                        superficie_rect.fill(cor_checkpoint)
                        pygame.draw.rect(superficie_rect, (0, 255, 255), 
                                       pygame.Rect(0, 0, CHECKPOINT_LARGURA, CHECKPOINT_ESPESSURA), 1)
                        
                        if angulo != 0:
                            superficie_rect = pygame.transform.rotate(superficie_rect, -angulo)
                        
                        rect_rotacionado = superficie_rect.get_rect(center=(int(screen_x), int(screen_y)))
                        
                        tela.blit(superficie_rect, rect_rotacionado)
                        
                        texto_checkpoint = fonte_checkpoint.render(str(idx_cp + 1), True, (255, 255, 255))
                        texto_rect = texto_checkpoint.get_rect(center=(int(screen_x), int(screen_y)))
                        fundo_texto = pygame.Surface((texto_rect.width + 8, texto_rect.height + 4), pygame.SRCALPHA)
                        fundo_texto.fill((0, 0, 0, 200))
                        tela.blit(fundo_texto, (texto_rect.x - 4, texto_rect.y - 2))
                        tela.blit(texto_checkpoint, texto_rect)

        if mostrar_hud:
            if modo_jogo == ModoJogo.DOIS_JOGADORES and carro2 is not None:
                metade_largura = LARGURA // 2
                
                superficie_hud_p1 = pygame.Surface((metade_largura, ALTURA), pygame.SRCALPHA)
                hud.desenhar_hud_completo(superficie_hud_p1, carro1, dt, offset_x=0)
                tela.blit(superficie_hud_p1, (0, 0))
                
                pontuacoes_alvo = None
                if tipo_jogo == TipoJogo.DRIFT:
                    num_checkpoints = len(checkpoints) if checkpoints else 19
                    pontuacoes_alvo = obter_pontuacoes_alvo(num_checkpoints, voltas_objetivo, dificuldade_ia)
                    hud.desenhar_posicao_voltas(tela, corrida, carro1, carros, posicao=(10, 10), tipo_jogo=tipo_jogo, drift_scoring=drift_scoring, pontuacoes_alvo=pontuacoes_alvo, trofeu_ouro=trofeu_ouro, trofeu_prata=trofeu_prata, trofeu_bronze=trofeu_bronze, trofeu_vazio=trofeu_vazio)
                else:
                    hud.desenhar_posicao_voltas(tela, corrida, carro1, carros, posicao=(10, 10), tipo_jogo=tipo_jogo)
                
                superficie_hud_p2 = pygame.Surface((metade_largura, ALTURA), pygame.SRCALPHA)
                hud.desenhar_hud_completo(superficie_hud_p2, carro2, dt, offset_x=0)
                tela.blit(superficie_hud_p2, (metade_largura, 0))
                
                if tipo_jogo == TipoJogo.DRIFT:
                    drift_scoring_p2_para_hud = drift_scoring_p2 if drift_scoring_p2 is not None else drift_scoring
                    hud.desenhar_posicao_voltas(tela, corrida, carro2, carros, posicao=(LARGURA - 10, 10), alinhar_direita=True, tipo_jogo=tipo_jogo, drift_scoring=drift_scoring_p2_para_hud, pontuacoes_alvo=pontuacoes_alvo, trofeu_ouro=trofeu_ouro, trofeu_prata=trofeu_prata, trofeu_bronze=trofeu_bronze, trofeu_vazio=trofeu_vazio)
                else:
                    hud.desenhar_posicao_voltas(tela, corrida, carro2, carros, posicao=(LARGURA - 10, 10), alinhar_direita=True, tipo_jogo=tipo_jogo)
                
                if pista_tiles is not None:
                    limites_pista = pista_tiles.calcular_limites_reais_pista(numero_pista)
                    checkpoints_para_minimapa = corrida.checkpoints if corrida.checkpoints else checkpoints
                    
                    minimapa_tamanho = 180
                    minimapa_x = (LARGURA - minimapa_tamanho) // 2
                    minimapa_y = 10
                    
                    hud.desenhar_minimapa(tela, carro1, checkpoints_para_minimapa, camera_p1, 
                                        posicao=(minimapa_x, minimapa_y), 
                                        imagem_minimapa=minimapa_imagem, 
                                        limites_pista=limites_pista,
                                        todos_carros=carros)
                else:
                    minimapa_tamanho = 180
                    minimapa_x = (LARGURA - minimapa_tamanho) // 2
                    minimapa_y = 10
                    hud.desenhar_minimapa(tela, carro1, checkpoints, camera_p1, 
                                        posicao=(minimapa_x, minimapa_y),
                                        todos_carros=carros)
            else:
                hud.desenhar_hud_completo(tela, carro1, dt)

                pontuacoes_alvo = None
                if tipo_jogo == TipoJogo.DRIFT:
                    num_checkpoints = len(checkpoints) if checkpoints else 19
                    pontuacoes_alvo = obter_pontuacoes_alvo(num_checkpoints, voltas_objetivo, dificuldade_ia)
                    hud.desenhar_posicao_voltas(tela, corrida, carro1, carros, posicao=(10, 10), tipo_jogo=tipo_jogo, drift_scoring=drift_scoring, pontuacoes_alvo=pontuacoes_alvo, trofeu_ouro=trofeu_ouro, trofeu_prata=trofeu_prata, trofeu_bronze=trofeu_bronze, trofeu_vazio=trofeu_vazio)
                else:
                    hud.desenhar_posicao_voltas(tela, corrida, carro1, carros, posicao=(10, 10), tipo_jogo=tipo_jogo)

                if pista_tiles is not None:
                    limites_pista = pista_tiles.calcular_limites_reais_pista(numero_pista)
                    minimapa_tamanho = 200
                    minimapa_x = 10
                    minimapa_y = resolucao[1] - minimapa_tamanho - 10
                    checkpoints_para_minimapa = corrida.checkpoints if corrida.checkpoints else checkpoints
                    hud.desenhar_minimapa(tela, carro1, checkpoints_para_minimapa, camera, 
                                        posicao=(minimapa_x, minimapa_y), 
                                        imagem_minimapa=minimapa_imagem, 
                                        limites_pista=limites_pista,
                                        todos_carros=carros)

                hud.desenhar_aviso_contra_mao(tela, carro1, dt)

        if jogo_terminado and tipo_jogo == TipoJogo.DRIFT and not tela_fim_mostrada:
            if not hasattr(principal, '_recompensa_drift_calculada'):
                # Recompensas de drift baseadas na dificuldade (como Need for Speed)
                if dificuldade_ia == "facil":
                    recompensa_drift = int(pontuacao_final / 150)
                elif dificuldade_ia == "medio":
                    recompensa_drift = int(pontuacao_final / 120)
                else:  # dificil
                    recompensa_drift = int(pontuacao_final / 100)
                gerenciador_progresso.adicionar_dinheiro(recompensa_drift)

                numero_pista = mapa_selecionado if mapa_selecionado is not None else 1
                chave_recorde = f"{numero_pista}_{voltas_objetivo}"
                if gerenciador_progresso.registrar_recorde_drift(chave_recorde, pontuacao_final):
                    print(f"Novo recorde de drift na pista {numero_pista} ({voltas_objetivo} voltas): {pontuacao_final:.0f} pontos")

                principal._recompensa_drift_calculada = recompensa_drift
            else:
                recompensa_drift = principal._recompensa_drift_calculada

            tela_fim_mostrada = True
            num_checkpoints = len(checkpoints) if checkpoints else 19
            pontuacoes_alvo = obter_pontuacoes_alvo(num_checkpoints, voltas_objetivo, dificuldade_ia)
            trofeu_drift = obter_trofeu_por_pontuacao(pontuacao_final, pontuacoes_alvo)

            estado_fim_jogo = [
                "DRIFT FINALIZADO!",
                "TODOS OS CHECKPOINTS COLETADOS!",
                trofeu_drift,
                None,
                pontuacao_final,
                recompensa_drift,
                0,
                [0.0, 0.0, 0.0]
            ]

            if mostrar_drift_hud and tipo_jogo == TipoJogo.DRIFT:
                fonte_drift = pygame.font.Font(None, 24)

        corrida.desenhar_semaforo(tela, largura_atual, altura_atual)

        if modo_jogo == ModoJogo.DOIS_JOGADORES:
            # Se ambos terminaram, mostrar tela de resultados finais
            if estado_resultados_finais is not None:
                desenhar_tela_resultados_finais(tela, estado_resultados_finais, dt)
            else:
                # Caso contrário, mostrar telas individuais
                # Só mostrar tela individual se o outro jogador ainda não terminou
                if estado_fim_jogo_p1 is not None and estado_fim_jogo_p2 is None:
                    desenhar_tela_fim_jogo(tela, estado_fim_jogo_p1, dt, lado='esquerdo')
                elif estado_fim_jogo_p2 is not None and estado_fim_jogo_p1 is None:
                    desenhar_tela_fim_jogo(tela, estado_fim_jogo_p2, dt, lado='direito')
                # Se ambos terminaram, não desenhar telas individuais (resultados finais será criado no próximo ciclo)
        else:
            # Modo singleplayer - usar tela de resultados finais
            if estado_resultados_finais is not None:
                desenhar_tela_resultados_finais(tela, estado_resultados_finais, dt)
            elif estado_fim_jogo is not None:
                # Fallback para tela individual (caso ainda exista algum código que use)
                desenhar_tela_fim_jogo(tela, estado_fim_jogo, dt)

        # Desenhar Akira (se ativa, modo 1 jogador e não estiver na tela de fim de jogo ou resultados finais) - tem prioridade sobre todos
        if akira.ativo and modo_jogo == ModoJogo.UM_JOGADOR and estado_fim_jogo is None and estado_fim_jogo_p1 is None and estado_fim_jogo_p2 is None and estado_resultados_finais is None:
            akira.desenhar_dialogo(tela, dt)
        # Desenhar Rex (se ativo, modo 1 jogador, Akira não estiver ativa e não estiver na tela de fim de jogo ou resultados finais) - tem prioridade sobre Crank
        elif rex.ativo and modo_jogo == ModoJogo.UM_JOGADOR and estado_fim_jogo is None and estado_fim_jogo_p1 is None and estado_fim_jogo_p2 is None and estado_resultados_finais is None:
            rex.desenhar_dialogo(tela, dt)
        # Desenhar Crank (se ativo, modo 1 jogador, Akira/Rex não estiverem ativos e não estiver na tela de fim de jogo ou resultados finais) - tem prioridade sobre mercador alien
        elif crank.ativo and modo_jogo == ModoJogo.UM_JOGADOR and estado_fim_jogo is None and estado_fim_jogo_p1 is None and estado_fim_jogo_p2 is None and estado_resultados_finais is None:
            crank.desenhar_dialogo(tela, dt)
        # Desenhar mercador alien (se ativo, modo 1 jogador, Akira/Rex/Crank não estiverem ativos e não estiver na tela de fim de jogo ou resultados finais) - deve aparecer sobre tudo
        elif mercador_alien.ativo and modo_jogo == ModoJogo.UM_JOGADOR and estado_fim_jogo is None and estado_fim_jogo_p1 is None and estado_fim_jogo_p2 is None and estado_resultados_finais is None:
            mercador_alien.desenhar_dialogo(tela, dt)

        if modo_jogo != ModoJogo.DOIS_JOGADORES and tipo_jogo != TipoJogo.DRIFT and not tela_fim_mostrada:
            if corrida.finalizou.get(carro1, False):
                vencedor = None
                recompensa_dinheiro = 0
                posicao_jogador = None

                todos_carros = [c for c in carros if c is not None]
                posicao_jogador = obter_posicao_jogador(carro1, todos_carros)

                if posicao_jogador == 1:
                    vencedor = "JOGADOR VENCEU!"
                    if dificuldade_ia == "facil":
                        recompensa_dinheiro = 600
                    elif dificuldade_ia == "medio":
                        recompensa_dinheiro = 1500
                    else:  # dificil
                        recompensa_dinheiro = 3000
                elif posicao_jogador == 2:
                    vencedor = "CORRIDA FINALIZADA!"
                    if dificuldade_ia == "facil":
                        recompensa_dinheiro = 300
                    elif dificuldade_ia == "medio":
                        recompensa_dinheiro = 750
                    else:  # dificil
                        recompensa_dinheiro = 1500
                elif posicao_jogador == 3:
                    vencedor = "CORRIDA FINALIZADA!"
                    if dificuldade_ia == "facil":
                        recompensa_dinheiro = 150
                    elif dificuldade_ia == "medio":
                        recompensa_dinheiro = 400
                    else:  # dificil
                        recompensa_dinheiro = 800
                else:
                    vencedor = "CORRIDA FINALIZADA!"
                    if dificuldade_ia == "facil":
                        recompensa_dinheiro = 100
                    elif dificuldade_ia == "medio":
                        recompensa_dinheiro = 200
                    else:  # dificil
                        recompensa_dinheiro = 400

                gerenciador_progresso.adicionar_dinheiro(recompensa_dinheiro)

                # Registrar corrida no Crank (mas não aparecer ainda - só após fechar tela de fim de jogo)
                colisoes_na_corrida = getattr(principal, '_colisoes_na_corrida', 0)
                venceu = (posicao_jogador == 1)
                crank.registrar_corrida(posicao_jogador, colisoes_na_corrida, venceu)

                tela_fim_mostrada = True

                if tipo_jogo == TipoJogo.GHOST:
                    tempo_final = corrida.tempo_final.get(carro1)
                    if tempo_final is not None:
                        numero_pista = mapa_selecionado if mapa_selecionado is not None else 1
                        tempos_alvo = obter_tempos_alvo(numero_pista, voltas_objetivo, dificuldade_ia)
                        trofeu = obter_trofeu_por_tempo(tempo_final, tempos_alvo)
                        if trofeu == trofeu_ouro:
                            gerenciador_progresso.registrar_trofeu(numero_pista, "ouro")
                        elif trofeu == trofeu_prata:
                            gerenciador_progresso.registrar_trofeu(numero_pista, "prata")
                        elif trofeu == trofeu_bronze:
                            gerenciador_progresso.registrar_trofeu(numero_pista, "bronze")
                    else:
                        trofeu = trofeu_vazio
                else:
                    trofeu = obter_trofeu_por_posicao(posicao_jogador) if posicao_jogador else trofeu_vazio

                tempo_final = corrida.tempo_final.get(carro1)
                if tempo_final is not None:
                    numero_pista = mapa_selecionado if mapa_selecionado is not None else 1

                    recorde_antes = gerenciador_progresso.obter_recorde(numero_pista)

                    novo_recorde = gerenciador_progresso.registrar_recorde(numero_pista, tempo_final)
                    if novo_recorde:
                        print(f"Novo recorde na pista {numero_pista}: {tempo_final:.2f}s")
                        # Atualizar estatística de recordes
                        gerenciador_achievements.atualizar_estatistica("recordes_estabelecidos", incrementar=True)

                        # Salvar ghost (sempre no modo relógio se melhor, ou quando novo recorde no modo drift)
                        if (tipo_jogo == TipoJogo.GHOST or tipo_jogo == TipoJogo.DRIFT):
                            if ghost_recorder_p1 and ghost_recorder_p1.gravando:
                                salvar_ghost = False
                                if tipo_jogo == TipoJogo.GHOST:
                                    if recorde_antes is None or tempo_final < recorde_antes:
                                        salvar_ghost = True
                                elif tipo_jogo == TipoJogo.DRIFT and novo_recorde:
                                    salvar_ghost = True

                                if salvar_ghost:
                                    ghost_recorder_p1.parar_gravacao()
                                    frames_gravados = ghost_recorder_p1.obter_dados()
                                    if frames_gravados and len(frames_gravados) > 0:
                                        # Verificação adicional no método salvar_ghost
                                        if tipo_jogo == TipoJogo.GHOST:
                                            gerenciador_ghosts.salvar_ghost(numero_pista, frames_gravados, tempo_final, "GHOST")
                                        elif tipo_jogo == TipoJogo.DRIFT:
                                            # Para drift, o score já foi verificado em novo_recorde
                                            # Mas não temos o score aqui, então vamos confiar na verificação anterior
                                            gerenciador_ghosts.salvar_ghost(numero_pista, frames_gravados)
                                else:
                                    # Não é melhor volta, limpar frames para economizar memória
                                    if ghost_recorder_p1 and ghost_recorder_p1.gravando:
                                        ghost_recorder_p1.parar_gravacao()
                                        ghost_recorder_p1.limpar()

                        if tipo_jogo == TipoJogo.GHOST:
                            if trofeu == trofeu_ouro:
                                if not gerenciador_achievements.esta_desbloqueado("trofeu_ouro"):
                                    if gerenciador_achievements.desbloquear("trofeu_ouro", gerenciador_progresso):
                                        from core.achievements import ACHIEVEMENTS
                                        from core.i18n import t
                                        ach_trofeu = ACHIEVEMENTS["trofeu_ouro"]
                                        nome_traduzido = t("achievements.trofeu_ouro")
                                        popup_achievement.mostrar(nome_traduzido, ach_trofeu['recompensa'])
                        else:
                            if posicao_jogador == 1:
                                gerenciador_progresso.registrar_trofeu(numero_pista, "ouro")
                                if not gerenciador_achievements.esta_desbloqueado("trofeu_ouro"):
                                    if gerenciador_achievements.desbloquear("trofeu_ouro", gerenciador_progresso):
                                        from core.achievements import ACHIEVEMENTS
                                        from core.i18n import t
                                        ach_trofeu = ACHIEVEMENTS["trofeu_ouro"]
                                        nome_traduzido = t("achievements.trofeu_ouro")
                                        popup_achievement.mostrar(nome_traduzido, ach_trofeu['recompensa'])
                            elif posicao_jogador == 2:
                                gerenciador_progresso.registrar_trofeu(numero_pista, "prata")
                            elif posicao_jogador == 3:
                                gerenciador_progresso.registrar_trofeu(numero_pista, "bronze")

                        gerenciador_achievements.atualizar_estatistica("corridas_completas", incrementar=True)
                        achievements_desbloqueados = gerenciador_achievements.verificar_achievements(gerenciador_progresso)
                        
                        numero_pista = mapa_selecionado if mapa_selecionado is not None else 1
                        # No modo GHOST/DRIFT, usar posicao_jogador e tempo_final que já foram definidos acima
                        gerenciador_estatisticas.registrar_corrida_completa(numero_pista, posicao_jogador, tempo_final)
                        # Verificar se Rex deve aparecer (primeira corrida, modo 1 jogador) - DEPOIS de registrar a corrida
                        if modo_jogo == ModoJogo.UM_JOGADOR:
                            rex.verificar_aparecer()
                        from core.i18n import t
                        for ach in achievements_desbloqueados:
                            nome_traduzido = t(f"achievements.{ach['id']}")
                            popup_achievement.mostrar(nome_traduzido, ach['recompensa'])

                resultados = []

                for carro in todos_carros:
                    posicao = obter_posicao_jogador(carro, todos_carros)
                    tempo = corrida.tempo_final.get(carro)
                    recompensa = 0
                    trofeu_carro = None

                    if carro == carro1:
                        nome = "JOGADOR"
                        recompensa = recompensa_dinheiro
                        trofeu_carro = trofeu
                    else:
                        nome = carro.nome if hasattr(carro, 'nome') else "IA"
                        if posicao == 1:
                            recompensa = 600 if dificuldade_ia == "facil" else 1500 if dificuldade_ia == "medio" else 3000
                        elif posicao == 2:
                            recompensa = 300 if dificuldade_ia == "facil" else 750 if dificuldade_ia == "medio" else 1500
                        elif posicao == 3:
                            recompensa = 150 if dificuldade_ia == "facil" else 400 if dificuldade_ia == "medio" else 800
                        else:
                            recompensa = 100 if dificuldade_ia == "facil" else 200 if dificuldade_ia == "medio" else 400
                        trofeu_carro = obter_trofeu_por_posicao(posicao) if posicao else trofeu_vazio

                    resultados.append({
                        "posicao": posicao,
                        "nome": nome,
                        "tempo": tempo,
                        "trofeu": trofeu_carro,
                        "dinheiro": recompensa
                    })

                # Ordenar por posição
                resultados.sort(key=lambda x: x["posicao"] if x["posicao"] else 999)
                estado_resultados_finais = {
                    "resultados": resultados,
                    "opcoes": [
                        ("TROCAR CARRO", "trocar_carro"),
                        ("REINICIAR JOGO", "reiniciar"),
                        ("MENU PRINCIPAL", "menu")
                    ],
                    "opcao_atual": 0
                }
                # Limpar estado de fim de jogo individual para evitar sobreposição
                estado_fim_jogo = None

        if jogo_pausado:
            from core.menu import render_text
            
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            tela.blit(overlay, (0, 0))
            
            caixa_largura = 500
            caixa_altura = 400
            caixa_x = (LARGURA - caixa_largura) // 2
            caixa_y = (ALTURA - caixa_altura) // 2
            
            caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
            caixa_fundo.fill((0, 0, 0, 200))
            tela.blit(caixa_fundo, (caixa_x, caixa_y))
            pygame.draw.rect(tela, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
            
            titulo_texto = render_text("JOGO PAUSADO", 48, (255, 255, 255), bold=True, pixel_style=True)
            titulo_x = caixa_x + (caixa_largura - titulo_texto.get_width()) // 2
            tela.blit(titulo_texto, (titulo_x, caixa_y + 20))
            
            opcoes_pausa_formatadas = [
                ("CONTINUAR", "continuar"),
                ("REINICIAR JOGO", "reiniciar"),
                ("MENU PRINCIPAL", "menu")
            ]
            
            altura_total_opcoes = len(opcoes_pausa_formatadas) * 60
            offset_opcoes = caixa_y + caixa_altura - altura_total_opcoes - 20
            
            if not hasattr(principal, '_hover_animation_pause'):
                principal._hover_animation_pause = [0.0] * len(opcoes_pausa_formatadas)
            
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_in_caixa = (caixa_x <= mouse_x <= caixa_x + caixa_largura and
                            caixa_y <= mouse_y <= caixa_y + caixa_altura)
            
            hover_speed = 8.0
            opcao_hover = -1
            if mouse_in_caixa:
                for i, (nome, chave) in enumerate(opcoes_pausa_formatadas):
                    y_opcao = offset_opcoes + i * 60
                    opcao_rect = pygame.Rect(caixa_x + 20, y_opcao - 5, caixa_largura - 40, 60)
                    if opcao_rect.collidepoint(mouse_x, mouse_y):
                        opcao_hover = i
                        break
            
            for i in range(len(opcoes_pausa_formatadas)):
                if i == opcao_hover or i == opcao_pausa_selecionada:
                    principal._hover_animation_pause[i] = min(1.0, principal._hover_animation_pause[i] + hover_speed * dt)
                else:
                    principal._hover_animation_pause[i] = max(0.0, principal._hover_animation_pause[i] - hover_speed * dt)
            
            if not mouse_in_caixa:
                for i in range(len(opcoes_pausa_formatadas)):
                    if i != opcao_pausa_selecionada:
                        principal._hover_animation_pause[i] = max(0.0, principal._hover_animation_pause[i] - hover_speed * dt * 1.5)
            
            # Desenhar cursor do controle se houver controle conectado
            animacao_cursor_pausa = getattr(principal, '_animacao_cursor_pausa', 0.0)
            tem_controle = gerenciador_gamepad.obter_numero_controles() > 0
            if tem_controle:
                animacao_cursor_pausa = (animacao_cursor_pausa + 3.0 * dt) % (2.0 * math.pi)
                principal._animacao_cursor_pausa = animacao_cursor_pausa
            
            for i, (nome, chave) in enumerate(opcoes_pausa_formatadas):
                y_opcao = offset_opcoes + i * 60
                hover_progress = principal._hover_animation_pause[i]
                
                # Determinar cor baseado no estado
                if i == opcao_pausa_selecionada:
                    cor = (255, 255, 255)
                    # Desenhar cursor do controle
                    if tem_controle:
                        cursor_alpha = int(128 + 127 * abs(math.sin(animacao_cursor_pausa)))
                        cursor_rect = pygame.Rect(caixa_x + 20, y_opcao - 5, caixa_largura - 40, 60)
                        pygame.draw.rect(tela, (0, 200, 255), cursor_rect, 3)
                        cursor_surface = pygame.Surface((cursor_rect.width, cursor_rect.height), pygame.SRCALPHA)
                        cursor_surface.fill((0, 200, 255, cursor_alpha // 4))
                        tela.blit(cursor_surface, cursor_rect.topleft)
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
                    tela.blit(hover_surface, hover_rect.topleft)
                
                # Desenhar texto da opção
                opcao_texto = render_text(nome, 32, cor, bold=True, pixel_style=True)
                opcao_x = caixa_x + (caixa_largura - opcao_texto.get_width()) // 2
                tela.blit(opcao_texto, (opcao_x, y_opcao))

        # Atualizar e desenhar popup de achievements
        popup_achievement.atualizar(dt)
        popup_achievement.desenhar(tela)

        pygame.display.update()

if __name__ == "__main__":
    from core.menu import run
    run()

