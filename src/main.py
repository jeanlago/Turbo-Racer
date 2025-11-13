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
from config import CAMINHO_MENU

CARROS_DISPONIVEIS = [
    {"nome": "Nissan 350Z", "prefixo_cor": "Car1", "posicao": (570, 145), "sprite_selecao": "Car1", "tipo_tracao": "Traseira", "tamanho_oficina": (850, 550), "posicao_oficina": (203, 183), "preco": 0},  # Gratuito (primeiro carro)
    {"nome": "BMW M3 95' ", "prefixo_cor": "Car2", "posicao": (570, 190), "sprite_selecao": "Car2", "tipo_tracao": "Traseira", "tamanho_oficina": (770, 415), "posicao_oficina": (233, 298), "preco": 3000},
    {"nome": "Chevrolet Camaro", "prefixo_cor": "Car3", "posicao": (560, 210), "sprite_selecao": "Car3", "tipo_tracao": "Traseira", "tamanho_oficina": (720, 470), "posicao_oficina": (263, 281), "preco": 4000},
    {"nome": "Toyota Supra", "prefixo_cor": "Car4", "posicao": (570, 190), "sprite_selecao": "Car4", "tipo_tracao": "Traseira", "tamanho_oficina": (755, 400), "posicao_oficina": (242, 326), "preco": 5000},
    {"nome": "Toyota Trueno", "prefixo_cor": "Car5", "posicao": (590, 175), "sprite_selecao": "Car5", "tipo_tracao": "Traseira", "tamanho_oficina": (740, 495), "posicao_oficina": (231, 240), "preco": 5600},
    {"nome": "Nissan Skyline", "prefixo_cor": "Car6", "posicao": (550, 200), "sprite_selecao": "Car6", "tipo_tracao": "Frontal", "tamanho_oficina": (730, 400), "posicao_oficina": (244, 329), "preco": 6000},
    {"nome": "Nissan Silvia S13", "prefixo_cor": "Car7", "posicao": (600, 185), "sprite_selecao": "Car7", "tipo_tracao": "Traseira", "tamanho_oficina": (855, 470), "posicao_oficina": (179, 318), "preco": 6400},
    {"nome": "Mazda RX-7", "prefixo_cor": "Car8", "posicao": (540, 220), "sprite_selecao": "Car8", "tipo_tracao": "Traseira", "tamanho_oficina": (805, 505), "posicao_oficina": (197, 240), "preco": 7000},
    {"nome": "Toyota Celica", "prefixo_cor": "Car9", "posicao": (610, 195), "sprite_selecao": "Car9", "tipo_tracao": "Traseira", "tamanho_oficina": (730, 425), "posicao_oficina": (240, 308), "preco": 9000},
    {"nome": "Volkswagem Fusca", "prefixo_cor": "Car10", "posicao": (530, 240), "sprite_selecao": "Car10", "tipo_tracao": "Frontal", "tamanho_oficina": (720, 485), "posicao_oficina": (242, 230), "preco": 12400},
    {"nome": "Mitsubishi Lancer", "prefixo_cor": "Car11", "posicao": (620, 205), "sprite_selecao": "Car11", "tipo_tracao": "Traseira", "tamanho_oficina": (955, 705), "posicao_oficina": (147, 86), "preco": 15600},
    {"nome": "Porsche 911 77'", "prefixo_cor": "Car12", "posicao": (520, 260), "sprite_selecao": "Car12", "tipo_tracao": "Traseira", "tamanho_oficina": (935, 675), "posicao_oficina": (153, 196), "preco": 25000},
    {"nome": "Audi Quattro S1", "prefixo_cor": "Car13", "posicao": (520, 260), "sprite_selecao": "Car13", "tipo_tracao": "AWD", "tamanho_oficina": (935, 675), "posicao_oficina": (153, 196), "preco": 17000}
]

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
    fps_max = max(CONFIGURACOES["video"]["fps_max"], 200)  # mínimo 200

    flags_display = 0
    if fullscreen:
        flags_display |= pygame.FULLSCREEN
    elif tela_cheia_sem_bordas:
        flags_display |= pygame.NOFRAME

    tela = pygame.display.set_mode(resolucao, flags_display)
    if vsync:
        pygame.display.set_mode(resolucao, flags_display | pygame.DOUBLEBUF)

    pygame.display.set_caption("Turbo Racer")
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
    checkpoints_grip = carregar_checkpoints_grip(numero_pista)
    
    if checkpoints_grip:
        checkpoints = checkpoints_grip
        print(f"Checkpoints do GRIP carregados: {len(checkpoints)}")
    else:
        pos_inicial_tiles = pista_tiles.obter_posicao_inicial()
        centro_x, centro_y = 2500, 2500
        checkpoints = [(centro_x + pos_inicial_tiles[0], centro_y + pos_inicial_tiles[1])]
        print(f"Usando checkpoint padrão baseado em tiles: {checkpoints[0]}")
    
    minimapa_imagem = pista_tiles.carregar_minimapa(numero_pista)
    
    checkpoint_manager = CheckpointManager(mapa_atual)
    checkpoint_manager.checkpoints = checkpoints

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
        
        altura_total_opcoes = 3 * 60
        offset_opcoes = caixa_y + caixa_altura - altura_total_opcoes - 20
        if ev.type == pygame.QUIT:
            return "sair"
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
        
        altura_total_opcoes = 3 * 60
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
        
        for i in range(len(opcoes)):
            if i == opcao_hover:
                hover_animation[i] = min(1.0, hover_animation[i] + hover_speed * dt)
            else:
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt)
        if not mouse_in_caixa:
            for i in range(len(opcoes)):
                hover_animation[i] = max(0.0, hover_animation[i] - hover_speed * dt * 1.5)
        
        titulo_texto = render_text(titulo, 48, (255, 255, 255), bold=True, pixel_style=True)
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
            
            texto = render_text(nome, 24, cor_texto, bold=True, pixel_style=True)
            tela.blit(texto, (caixa_x + 30, y))
    
    carro_p1 = CARROS_DISPONIVEIS[carro_selecionado_p1]
    carro_p2 = CARROS_DISPONIVEIS[carro_selecionado_p2]

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

    carro1 = CarroFisica(
        pos_inicial_p1[0], pos_inicial_p1[1],
        carro_p1["prefixo_cor"],
        (pygame.K_w, pygame.K_d, pygame.K_a, pygame.K_s),
        turbo_key=TURBO_P1,
        nome=carro_p1["nome"],
        tipo_tracao=carro_p1.get("tipo_tracao", CarroFisica.TRACAO_TRASEIRA)
    )
    carros.append(carro1)
    
    camera.cx = carro1.x
    camera.cy = carro1.y
    print(f"Câmera inicializada na posição do carro: ({camera.cx}, {camera.cy})")

    carro2 = None
    if modo_jogo == ModoJogo.DOIS_JOGADORES and pos_inicial_p2 is not None:
        carro2 = CarroFisica(
            pos_inicial_p2[0], pos_inicial_p2[1],
            carro_p2["prefixo_cor"],
            (pygame.K_UP, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_DOWN),
            turbo_key=TURBO_P2,
            nome=carro_p2["nome"],
            tipo_tracao=carro_p2.get("tipo_tracao", CarroFisica.TRACAO_TRASEIRA)
        )
        carros.append(carro2)

    carros_ia = []
    if tipo_jogo != TipoJogo.DRIFT:
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
        
        for i, (pos_ia, carro_data) in enumerate(zip(posicoes_ia, carros_selecionados_ia)):
            carro_ia = CarroFisica(
                pos_ia[0], pos_ia[1],
                carro_data["prefixo_cor"],
                (0, 0, 0, 0),
                turbo_key=pygame.K_t,
                nome=f"IA-{i+1}",
                tipo_tracao=carro_data.get("tipo_tracao", CarroFisica.TRACAO_TRASEIRA)
            )
            carro_ia.eh_bot = True
            carro_ia.skidmarks.max_skidmarks = 80
            carros_ia.append(carro_ia)
            carros.append(carro_ia)
            print(f"IA-{i+1} usando carro: {carro_data['nome']} ({carro_data['prefixo_cor']})")

    for c in carros:
        corrida.registrar_carro(c)

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
        # Usar os mesmos limites da câmera principal (superfície expandida)
        camera_p1 = Camera(metade_largura, ALTURA, largura_pista, altura_pista, zoom=1.6)
        camera_p2 = Camera(metade_largura, ALTURA, largura_pista, altura_pista, zoom=1.6)
        # Posição inicial das câmeras (centro da pista no sistema original)
        camera_p1.cx = 2500 + offset_x_superficie
        camera_p1.cy = 2500 + offset_y_superficie
        camera_p2.cx = 2500 + offset_x_superficie
        camera_p2.cy = 2500 + offset_y_superficie
        # Armazenar offset para as câmeras do modo 2 jogadores
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
    for i, carro_ia in enumerate(carros_ia):
        instancia_ia = IA(checkpoints_ia, nome=carro_ia.nome, dificuldade=dificuldade_ia)
        instancias_ia.append(instancia_ia)
        print(f"Criada {instancia_ia.nome} com {len(checkpoints_ia)} checkpoints")
    
    IA2 = instancias_ia[0] if len(instancias_ia) > 0 else None
    IA3 = instancias_ia[1] if len(instancias_ia) > 1 else None
    IA4 = instancias_ia[2] if len(instancias_ia) > 2 else None
    debug_IA = True

    # Modo drift agora usa checkpoints, não tempo
    jogo_pausado = False
    jogo_terminado = False
    pontuacao_final = 0
    tela_fim_mostrada = False
    acao_fim_jogo = None
    estado_fim_jogo = None
    
    # Estados de fim de jogo separados para modo 2 jogadores
    tela_fim_mostrada_p1 = False
    tela_fim_mostrada_p2 = False
    estado_fim_jogo_p1 = None
    estado_fim_jogo_p2 = None
    pontuacao_final_p1 = 0
    pontuacao_final_p2 = 0
    
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

        gerenciador_musica.verificar_fim_musica()

        for ev in pygame.event.get():
            if modo_jogo == ModoJogo.DOIS_JOGADORES:
                evento_processado = False
                if estado_fim_jogo_p1 is not None:
                    if hasattr(ev, 'pos'):
                        if ev.pos[0] < LARGURA // 2:
                            acao = processar_tela_fim_jogo(ev, estado_fim_jogo_p1, lado='esquerdo')
                            if acao:
                                evento_processado = True
                                if acao == "reiniciar":
                                    return principal(carro_selecionado_p1, carro_selecionado_p2, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                                elif acao == "trocar_carro":
                                    from core.menu import selecionar_carros_loop
                                    resultado = selecionar_carros_loop(tela)
                                    if resultado:
                                        carro_p1_idx, carro_p2_idx = resultado
                                        return principal(carro_p1_idx, carro_p2_idx, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                                    estado_fim_jogo_p1 = None
                                    continue
                                elif acao == "menu" or acao == "sair":
                                    return
                    elif ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_ESCAPE or estado_fim_jogo_p2 is None:
                            acao = processar_tela_fim_jogo(ev, estado_fim_jogo_p1, lado='esquerdo')
                            if acao:
                                evento_processado = True
                                if acao == "reiniciar":
                                    return principal(carro_selecionado_p1, carro_selecionado_p2, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                                elif acao == "trocar_carro":
                                    from core.menu import selecionar_carros_loop
                                    resultado = selecionar_carros_loop(tela)
                                    if resultado:
                                        carro_p1_idx, carro_p2_idx = resultado
                                        return principal(carro_p1_idx, carro_p2_idx, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                                    estado_fim_jogo_p1 = None
                                    continue
                                elif acao == "menu" or acao == "sair":
                                    return
                
                if estado_fim_jogo_p2 is not None and not evento_processado:
                    if hasattr(ev, 'pos'):
                        if ev.pos[0] >= LARGURA // 2:
                            acao = processar_tela_fim_jogo(ev, estado_fim_jogo_p2, lado='direito')
                            if acao:
                                evento_processado = True
                                if acao == "reiniciar":
                                    return principal(carro_selecionado_p1, carro_selecionado_p2, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                                elif acao == "trocar_carro":
                                    from core.menu import selecionar_carros_loop
                                    resultado = selecionar_carros_loop(tela)
                                    if resultado:
                                        carro_p1_idx, carro_p2_idx = resultado
                                        return principal(carro_p1_idx, carro_p2_idx, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                                    estado_fim_jogo_p2 = None
                                    continue
                                elif acao == "menu" or acao == "sair":
                                    return
                    elif ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_ESCAPE or estado_fim_jogo_p1 is None:
                            acao = processar_tela_fim_jogo(ev, estado_fim_jogo_p2, lado='direito')
                            if acao:
                                evento_processado = True
                                if acao == "reiniciar":
                                    return principal(carro_selecionado_p1, carro_selecionado_p2, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                                elif acao == "trocar_carro":
                                    from core.menu import selecionar_carros_loop
                                    resultado = selecionar_carros_loop(tela)
                                    if resultado:
                                        carro_p1_idx, carro_p2_idx = resultado
                                        return principal(carro_p1_idx, carro_p2_idx, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                                    estado_fim_jogo_p2 = None
                                    continue
                                elif acao == "menu" or acao == "sair":
                                    return
                
                if evento_processado:
                    continue
            else:
                if estado_fim_jogo is not None:
                    acao = processar_tela_fim_jogo(ev, estado_fim_jogo)
                    if acao:
                        if acao == "reiniciar":
                            return principal(carro_selecionado_p1, carro_selecionado_p2, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                        elif acao == "trocar_carro":
                            from core.menu import selecionar_carros_loop
                            resultado = selecionar_carros_loop(tela)
                            if resultado:
                                carro_p1_idx, carro_p2_idx = resultado
                                return principal(carro_p1_idx, carro_p2_idx, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                            estado_fim_jogo = None
                            continue
                        elif acao == "menu" or acao == "sair":
                            return
                    continue
            
            if ev.type == pygame.QUIT:
                rodando = False

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    if estado_fim_jogo is not None:
                        return
                    elif not jogo_terminado:
                        jogo_pausado = not jogo_pausado
                        opcao_pausa_selecionada = 0
                elif ev.key == pygame.K_F1:
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

                if ev.key == pygame.K_SPACE:
                    carro1.ativar_drift()
                if ev.key in (pygame.K_LSHIFT, pygame.K_RSHIFT) and carro2 is not None:
                    carro2.drift_hold = True
                
                if jogo_pausado:
                    if ev.key == pygame.K_UP or ev.key == pygame.K_w:
                        opcao_pausa_selecionada = (opcao_pausa_selecionada - 1) % len(opcoes_pausa)
                    elif ev.key == pygame.K_DOWN or ev.key == pygame.K_s:
                        opcao_pausa_selecionada = (opcao_pausa_selecionada + 1) % len(opcoes_pausa)
                    elif ev.key == pygame.K_RETURN or ev.key == pygame.K_SPACE:
                        if opcao_pausa_selecionada == 0:
                            jogo_pausado = False
                        elif opcao_pausa_selecionada == 1:
                            return principal(carro_selecionado_p1, carro_selecionado_p2, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                        elif opcao_pausa_selecionada == 2:
                            return

            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # Processar clique do mouse no pause
                if jogo_pausado:
                    caixa_largura = 500
                    caixa_altura = 400
                    caixa_x = (LARGURA - caixa_largura) // 2
                    caixa_y = (ALTURA - caixa_altura) // 2
                    mouse_x, mouse_y = ev.pos
                    mouse_in_caixa = (caixa_x <= mouse_x <= caixa_x + caixa_largura and
                                    caixa_y <= mouse_y <= caixa_y + caixa_altura)
                    if mouse_in_caixa:
                        altura_total_opcoes = 3 * 60
                        offset_opcoes = caixa_y + caixa_altura - altura_total_opcoes - 20
                        opcoes_pausa_formatadas = [
                            ("CONTINUAR", "continuar"),
                            ("REINICIAR JOGO", "reiniciar"),
                            ("MENU PRINCIPAL", "menu")
                        ]
                        for i, (nome, chave) in enumerate(opcoes_pausa_formatadas):
                            y_opcao = offset_opcoes + i * 60
                            opcao_rect = pygame.Rect(caixa_x + 20, y_opcao - 5, caixa_largura - 40, 60)
                            if opcao_rect.collidepoint(mouse_x, mouse_y):
                                if i == 0:
                                    jogo_pausado = False
                                elif i == 1:
                                    return principal(carro_selecionado_p1, carro_selecionado_p2, mapa_selecionado, modo_jogo, tipo_jogo, voltas, dificuldade_ia)
                                elif i == 2:
                                    return
                                break

            elif ev.type == pygame.KEYUP:
                if ev.key == pygame.K_SPACE:
                    carro1.desativar_drift()
                if ev.key in (pygame.K_LSHIFT, pygame.K_RSHIFT) and carro2 is not None:
                    carro2.drift_hold = False

            elif ev.type == pygame.MOUSEBUTTONDOWN:
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
            corrida.atualizar_contagem(dt)
        corrida.atualizar_tempo(dt, jogo_pausado)

        if tipo_jogo == TipoJogo.DRIFT and corrida.iniciada:
            if not tela_fim_mostrada_p1 and corrida.finalizou.get(carro1, False):
                pontuacao_final_p1 = drift_scoring.points
                tela_fim_mostrada_p1 = True
                num_checkpoints = len(checkpoints) if checkpoints else 19
                pontuacoes_alvo = obter_pontuacoes_alvo(num_checkpoints, voltas_objetivo, dificuldade_ia)
                trofeu_drift_p1 = obter_trofeu_por_pontuacao(pontuacao_final_p1, pontuacoes_alvo)
                
                if not hasattr(principal, '_recompensa_drift_p1_calculada'):
                    recompensa_drift_p1 = int(pontuacao_final_p1 / 200)
                    gerenciador_progresso.adicionar_dinheiro(recompensa_drift_p1)
                    numero_pista = mapa_selecionado if mapa_selecionado is not None else 1
                    chave_recorde = f"{numero_pista}_{voltas_objetivo}"
                    if gerenciador_progresso.registrar_recorde_drift(chave_recorde, pontuacao_final_p1):
                        print(f"Novo recorde de drift na pista {numero_pista} ({voltas_objetivo} voltas): {pontuacao_final_p1:.0f} pontos")
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
                    [0.0, 0.0, 0.0]
                ]
            
            if modo_jogo == ModoJogo.DOIS_JOGADORES and carro2 is not None and drift_scoring_p2 is not None:
                if not tela_fim_mostrada_p2 and corrida.finalizou.get(carro2, False):
                    pontuacao_final_p2 = drift_scoring_p2.points
                    tela_fim_mostrada_p2 = True
                    num_checkpoints = len(checkpoints) if checkpoints else 19
                    pontuacoes_alvo = obter_pontuacoes_alvo(num_checkpoints, voltas_objetivo, dificuldade_ia)
                    trofeu_drift_p2 = obter_trofeu_por_pontuacao(pontuacao_final_p2, pontuacoes_alvo)
                    
                    if not hasattr(principal, '_recompensa_drift_p2_calculada'):
                        recompensa_drift_p2 = int(pontuacao_final_p2 / 200)
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
                        [0.0, 0.0, 0.0]
                    ]
            
            if modo_jogo != ModoJogo.DOIS_JOGADORES:
                if corrida.finalizou.get(carro1, False):
                    jogo_terminado = True
                    pontuacao_final = drift_scoring.points

        alguem_venceu = corrida.alguem_finalizou()

        while acumulador_dt >= dt_fixo:
            pode_controlar_p1 = (modo_jogo != ModoJogo.DOIS_JOGADORES or estado_fim_jogo_p1 is None)
            pode_controlar_p2 = (modo_jogo != ModoJogo.DOIS_JOGADORES or estado_fim_jogo_p2 is None)
            pode_controlar_geral_p1 = (estado_fim_jogo is None and pode_controlar_p1)
            
            if corrida.pode_controlar() and not jogo_pausado and pode_controlar_geral_p1:
                pos_antes = (carro1.x, carro1.y)
                carro1.atualizar(teclas, None, dt_fixo, camera, superficie_pista_renderizada)
                pos_depois = (carro1.x, carro1.y)
                dist_movimento = ((pos_depois[0] - pos_antes[0])**2 + (pos_depois[1] - pos_antes[1])**2)**0.5
                if dist_movimento > 100:
                    print(f"AVISO: Possível teleporte detectado! De {pos_antes} para {pos_depois} (distância: {dist_movimento})")
                    if pista_tiles is not None:
                        carro1.x, carro1.y = pos_antes
                        print(f"Posição restaurada para: {pos_antes}")

            if carro2 is not None and not jogo_pausado:
                if modo_jogo == ModoJogo.DOIS_JOGADORES:
                    if pode_controlar_p2 and corrida.pode_controlar():
                        carro2.atualizar(teclas, None, dt_fixo, camera, superficie_pista_renderizada)
                elif USAR_IA_NO_CARRO_2 and corrida.iniciada:
                    if not corrida.finalizou.get(carro2, False):
                        IA2.controlar(carro2, None, None, dt_fixo, superficie_pista_renderizada, corrida_iniciada=corrida.iniciada)
                elif corrida.pode_controlar():
                    carro2.atualizar(teclas, None, dt_fixo, camera, superficie_pista_renderizada)

            if not jogo_pausado and corrida.iniciada:
                for i, (carro_ia, instancia_ia) in enumerate(zip(carros_ia, instancias_ia)):
                    if not corrida.finalizou.get(carro_ia, False):
                        pos_antes_bot = (carro_ia.x, carro_ia.y)
                        instancia_ia.controlar(carro_ia, None, None, dt_fixo, superficie_pista_renderizada, corrida_iniciada=corrida.iniciada)
                        pos_depois_bot = (carro_ia.x, carro_ia.y)
                        dist_movimento_bot = ((pos_depois_bot[0] - pos_antes_bot[0])**2 + (pos_depois_bot[1] - pos_antes_bot[1])**2)**0.5
                        if dist_movimento_bot > 100:
                            print(f"AVISO: Teleporte do bot {carro_ia.nome} detectado! De {pos_antes_bot} para {pos_depois_bot} (distância: {dist_movimento_bot})")
                            if pista_tiles is not None:
                                carro_ia.x, carro_ia.y = pos_antes_bot
                                print(f"Posição do bot {carro_ia.nome} restaurada para: {pos_antes_bot}")

                for c in carros:
                    corrida.atualizar_progresso_carro(c)

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

            camera_p1.set_alvo(carro1)
            
            if hasattr(carro1, 'vx') and hasattr(carro1, 'vy'):
                vel_sq_p1 = carro1.vx*carro1.vx + carro1.vy*carro1.vy
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
            checkpoint_atual_p1 = corrida.proximo_checkpoint.get(carro1, 0) 
            if not corrida.finalizou.get(carro1, False) and checkpoints:
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

            camera_p2.set_alvo(carro2)
            
            if hasattr(carro2, 'vx') and hasattr(carro2, 'vy'):
                vel_sq_p2 = carro2.vx*carro2.vx + carro2.vy*carro2.vy
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
                    recompensa_drift = int(pontuacao_final / 200)
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
            if estado_fim_jogo_p1 is not None:
                desenhar_tela_fim_jogo(tela, estado_fim_jogo_p1, dt, lado='esquerdo')
            if estado_fim_jogo_p2 is not None:
                desenhar_tela_fim_jogo(tela, estado_fim_jogo_p2, dt, lado='direito')
        else:
            if estado_fim_jogo is not None:
                desenhar_tela_fim_jogo(tela, estado_fim_jogo, dt)

        if modo_jogo != ModoJogo.DOIS_JOGADORES and tipo_jogo != TipoJogo.DRIFT and not tela_fim_mostrada:
            if corrida.finalizou.get(carro1, False):
                vencedor = None
                recompensa_dinheiro = 0
                posicao_jogador = None
                
                todos_carros = [c for c in carros if c is not None]
                posicao_jogador = obter_posicao_jogador(carro1, todos_carros)
                
                if posicao_jogador == 1:
                    vencedor = "JOGADOR VENCEU!"
                    recompensa_base = 150
                    if dificuldade_ia == "facil":
                        recompensa_dinheiro = recompensa_base
                    elif dificuldade_ia == "medio":
                        recompensa_dinheiro = int(recompensa_base * 1.5)
                    else:
                        recompensa_dinheiro = int(recompensa_base * 2.0)
                else:
                    vencedor = "CORRIDA FINALIZADA!"
                    recompensa_dinheiro = 30
                
                gerenciador_progresso.adicionar_dinheiro(recompensa_dinheiro)
                
                tela_fim_mostrada = True
                trofeu = obter_trofeu_por_posicao(posicao_jogador) if posicao_jogador else trofeu_vazio
                
                if posicao_jogador is not None:
                    tempo_final = corrida.tempo_final.get(carro1)
                    if tempo_final is not None:
                        numero_pista = mapa_selecionado if mapa_selecionado is not None else 1
                        
                        if gerenciador_progresso.registrar_recorde(numero_pista, tempo_final):
                            print(f"Novo recorde na pista {numero_pista}: {tempo_final:.2f}s")
                        
                        if posicao_jogador == 1:
                            gerenciador_progresso.registrar_trofeu(numero_pista, "ouro")
                        elif posicao_jogador == 2:
                            gerenciador_progresso.registrar_trofeu(numero_pista, "prata")
                        elif posicao_jogador == 3:
                            gerenciador_progresso.registrar_trofeu(numero_pista, "bronze")
                
                estado_fim_jogo = [
                    vencedor,
                    "CORRIDA FINALIZADA!",
                    trofeu,
                    posicao_jogador,
                    None,
                    recompensa_dinheiro,
                    0,
                    [0.0, 0.0, 0.0]
                ]

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
            
            for i, (nome, chave) in enumerate(opcoes_pausa_formatadas):
                y_opcao = offset_opcoes + i * 60
                hover_progress = principal._hover_animation_pause[i]
                
                if i == opcao_pausa_selecionada:
                    cor = (255, 255, 255)
                elif hover_progress > 0.1:
                    cor = (200, 200, 255)
                else:
                    cor = (150, 150, 150)
                
                if hover_progress > 0:
                    hover_alpha = int(30 * hover_progress)
                    hover_rect = pygame.Rect(caixa_x + 20, y_opcao - 5, caixa_largura - 40, 60)
                    hover_surface = pygame.Surface((hover_rect.width, hover_rect.height), pygame.SRCALPHA)
                    hover_surface.fill((0, 200, 255, hover_alpha))
                    tela.blit(hover_surface, hover_rect.topleft)
                
                opcao_texto = render_text(nome, 32, cor, bold=True, pixel_style=True)
                opcao_x = caixa_x + (caixa_largura - opcao_texto.get_width()) // 2
                tela.blit(opcao_texto, (opcao_x, y_opcao))

        pygame.display.update()

if __name__ == "__main__":
    from core.menu import run
    run()

