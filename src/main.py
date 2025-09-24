import os
import math
import pygame
from config import (
    LARGURA, ALTURA, FPS, TURBO_P1, TURBO_P2,
    USAR_IA_NO_CARRO_2, CONFIGURACOES,
    MAPAS_DISPONIVEIS, MAPA_ATUAL, obter_caminho_mapa, obter_caminho_guias,
    obter_lista_mapas
)
from core.pista import (
    carregar_pista, eh_pixel_transitavel, calcular_posicoes_iniciais, extrair_checkpoints
)
from core.checkpoint_manager import CheckpointManager
from core.carro import Carro
from core.carro_fisica import CarroFisica
from core.corrida import GerencIAdorCorrida
from core.camera import Camera
from core.ia import IA
from core.musica import gerencIAdor_musica
from core.hud import HUD
from core.game_modes import ModoJogo, TipoJogo
from core.drift_scoring import DriftScoring

CARROS_DISPONIVEIS = [
    {"nome": "Nissan 350Z", "prefixo_cor": "Car1", "posicao": (570, 145), "sprite_selecao": "Car1", "tipo_tracao": "rear", "tamanho_oficina": (850, 550), "posicao_oficina": (LARGURA//2 - 430, 170)},
    {"nome": "BMW M3 95' ", "prefixo_cor": "Car2", "posicao": (570, 190), "sprite_selecao": "Car2", "tipo_tracao": "rear", "tamanho_oficina": (600, 300), "posicao_oficina": (LARGURA//2 - 300, 380)},
    {"nome": "Chevrolet Camaro", "prefixo_cor": "Car3", "posicao": (560, 210), "sprite_selecao": "Car3", "tipo_tracao": "rear", "tamanho_oficina": (580, 550), "posicao_oficina": (LARGURA//2 - 320, 200)},
    {"nome": "Toyota Supra", "prefixo_cor": "Car4", "posicao": (570, 190), "sprite_selecao": "Car4", "tipo_tracao": "rear", "tamanho_oficina": (600, 300), "posicao_oficina": (LARGURA//2 - 300, 380)},
    {"nome": "Toyota Trueno", "prefixo_cor": "Car5", "posicao": (590, 175), "sprite_selecao": "Car5", "tipo_tracao": "rear", "tamanho_oficina": (600, 300), "posicao_oficina": (LARGURA//2 - 300, 380)},
    {"nome": "Nissan Skyline", "prefixo_cor": "Car6", "posicao": (550, 200), "sprite_selecao": "Car6", "tipo_tracao": "front", "tamanho_oficina": (900, 650), "posicao_oficina": (LARGURA//2 - 490, 215)},
    {"nome": "Nissan Silvia S13", "prefixo_cor": "Car7", "posicao": (600, 185), "sprite_selecao": "Car7", "tipo_tracao": "rear", "tamanho_oficina": (600, 300), "posicao_oficina": (LARGURA//2 - 300, 380)},
    {"nome": "Mazda RX-7", "prefixo_cor": "Car8", "posicao": (540, 220), "sprite_selecao": "Car8", "tipo_tracao": "awd", "tamanho_oficina": (600, 300), "posicao_oficina": (LARGURA//2 - 300, 380)},
    {"nome": "Toyota Celica", "prefixo_cor": "Car9", "posicao": (610, 195), "sprite_selecao": "Car9", "tipo_tracao": "rear", "tamanho_oficina": (600, 300), "posicao_oficina": (LARGURA//2 - 350, 380)},
    {"nome": "Volkswagem Fusca", "prefixo_cor": "Car10", "posicao": (530, 240), "sprite_selecao": "Car10", "tipo_tracao": "front", "tamanho_oficina": (750, 550), "posicao_oficina": (LARGURA//2 - 400, 250)},
    {"nome": "Mitsubishi Lancer", "prefixo_cor": "Car11", "posicao": (620, 205), "sprite_selecao": "Car11", "tipo_tracao": "rear", "tamanho_oficina": (900, 650), "posicao_oficina": (LARGURA//2 - 490, 150)},
    {"nome": "Porsche 911 77'", "prefixo_cor": "Car12", "posicao": (520, 260), "sprite_selecao": "Car12", "tipo_tracao": "rear", "tamanho_oficina": (900, 650), "posicao_oficina": (LARGURA//2 - 490, 215)},
]

def principal(carro_selecionado_p1=0, carro_selecionado_p2=1, mapa_selecionado=None, modo_jogo=ModoJogo.UM_JOGADOR, tipo_jogo=TipoJogo.CORRIDA, voltas=1):
    pygame.init()

    from config import carregar_configuracoes
    carregar_configuracoes()

    resolucao = CONFIGURACOES["video"]["resolucao"]
    fullscreen = CONFIGURACOES["video"]["fullscreen"]
    tela_cheIA_sem_bordas = CONFIGURACOES["video"]["tela_cheIA_sem_bordas"]
    qualidade_alta = CONFIGURACOES["video"]["qualidade_alta"]
    vsync = CONFIGURACOES["video"]["vsync"]
    fps_max = max(CONFIGURACOES["video"]["fps_max"], 200)  # mínimo 200

    flags_display = 0
    if fullscreen:
        flags_display |= pygame.FULLSCREEN
    elif tela_cheIA_sem_bordas:
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

    img_pista, mask_pista, mask_guias = carregar_pista()

    checkpoint_manager = CheckpointManager(mapa_atual)

    if checkpoint_manager.checkpoints:
        checkpoints = checkpoint_manager.checkpoints
        print(f"IA vai seguir {len(checkpoints)} checkpoints do arquivo")
    else:
        checkpoints = extrair_checkpoints(mask_guias)
        if checkpoints:
            print(f"IA vai seguir {len(checkpoints)} checkpoints extraídos do mapa")
            checkpoint_manager.checkpoints = checkpoints
            checkpoint_manager.salvar_checkpoints()
        else:
            checkpoints = [(640, 360)]
            print("Nenhum checkpoint encontrado, usando centro da tela")

    largura_atual, altura_atual = resolucao
    camera = Camera(largura_atual, altura_atual, *img_pista.get_size(), zoom=1.0)

    largura_pista, altura_pista = img_pista.get_size()
    camera.cx = largura_pista // 2
    camera.cy = altura_pista // 2

    modo_drift_atual = CONFIGURACOES["jogo"]["modo_drift"]
    mostrar_fps = CONFIGURACOES["video"]["mostrar_fps"]
    mostrar_debug = CONFIGURACOES["jogo"]["mostrar_debug"]

    fonte = pygame.font.SysFont("consolas", 26)
    fonte_small = pygame.font.SysFont("consolas", 18)
    fonte_checkpoint = pygame.font.SysFont("consolas", 18, bold=True)
    fonte_debug = pygame.font.SysFont("consolas", 16)
    fonte_debug_bold = pygame.font.SysFont("consolas", 16, bold=True)

    voltas_objetivo = voltas
    corrida = GerencIAdorCorrida(fonte, checkpoints, voltas_objetivo)

    carro_p1 = CARROS_DISPONIVEIS[carro_selecionado_p1]
    carro_p2 = CARROS_DISPONIVEIS[carro_selecionado_p2]

    posicoes_iniciais = calcular_posicoes_iniciais(mask_guias)
    pos_inicial_p1 = posicoes_iniciais['p1']
    pos_inicial_p2 = posicoes_iniciais['p2']
    pos_inicial_IA = posicoes_iniciais['IA']

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

    carro2 = None
    if modo_jogo == ModoJogo.DOIS_JOGADORES and tipo_jogo != TipoJogo.DRIFT:
        carro2 = CarroFisica(
            pos_inicial_p2[0], pos_inicial_p2[1],
            carro_p2["prefixo_cor"],
            (pygame.K_UP, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_DOWN),
            turbo_key=TURBO_P2,
            nome=carro_p2["nome"],
            tipo_tracao=carro_p2.get("tipo_tracao", CarroFisica.TRACAO_TRASEIRA)
        )
        carros.append(carro2)

    carro3 = None
    if tipo_jogo != TipoJogo.DRIFT and modo_jogo != ModoJogo.DOIS_JOGADORES:
        carro3 = Carro(pos_inicial_IA[0], pos_inicial_IA[1], "Car3", (0, 0, 0, 0), nome="IA-1")
        carros.append(carro3)

    for c in carros:
        corrida.registrar_carro(c)

    camera.set_alvo(carro1)

    hud = HUD()
    mostrar_hud = True

    drift_scoring = DriftScoring()
    mostrar_drift_hud = tipo_jogo == TipoJogo.DRIFT

    camera_p1 = None
    camera_p2 = None
    if modo_jogo == ModoJogo.DOIS_JOGADORES and carro2 is not None:
        metade_largura = LARGURA // 2
        camera_p1 = Camera(metade_largura, ALTURA, *img_pista.get_size(), zoom=1.0)
        camera_p2 = Camera(metade_largura, ALTURA, *img_pista.get_size(), zoom=1.0)
        camera_p1.cx = largura_pista // 2
        camera_p1.cy = altura_pista // 2
        camera_p2.cx = largura_pista // 2
        camera_p2.cy = altura_pista // 2

    def is_on_track(x, y):
        return eh_pixel_transitavel(mask_guias, x, y)

    IA2 = IA(checkpoints, nome="IA-1")
    IA3 = IA(checkpoints, nome="IA-2")
    debug_IA = True

    IA_update_timer = 0.0
    IA_update_interval = 1.0 / 20.0

    tempo_drift = 60.0
    tempo_restante = tempo_drift
    jogo_pausado = False
    jogo_terminado = False
    pontuacao_final = 0

    # estado de edição/drag de checkpoint
    arrastando_checkpoint = False
    checkpoint_em_arraste = -1
    arrastando_camera = False
    ultimo_clique_tempo = 0
    debounce_tempo = 200

    if CONFIGURACOES["audio"]["musica_habilitada"] and CONFIGURACOES["audio"]["musica_no_jogo"]:
        gerencIAdor_musica.definir_volume(CONFIGURACOES["audio"]["volume_musica"])
        if not gerencIAdor_musica.musica_tocando:
            if CONFIGURACOES["audio"]["musica_aleatorIA"]:
                gerencIAdor_musica.musica_aleatorIA()
            else:
                gerencIAdor_musica.tocar_musica()

    rodando = True
    alguem_venceu = False
    dt_fixo = 1.0 / 240.0  # 240 Hz para velocidade normal
    acumulador_dt = 0.0
    max_dt = 0.1

    while rodando:
        dt = relogio.tick(fps_max) / 1000.0
        dt = min(dt, max_dt)
        acumulador_dt += dt
        
        # Debug removido para melhor performance

        gerencIAdor_musica.verificar_fim_musica()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                rodando = False

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    if not jogo_terminado and not alguem_venceu:
                        jogo_pausado = not jogo_pausado
                        print(f"Jogo {'pausado' if jogo_pausado else 'retomado'}")
                    else:
                        return
                elif ev.key == pygame.K_F1:
                    debug_IA = not debug_IA
                    IA2.debug = IA3.debug = debug_IA
                elif ev.key == pygame.K_h:
                    mostrar_hud = not mostrar_hud
                    print(f"HUD: {'Ativado' if mostrar_hud else 'Desativado'}")

                # turbo (hold) – leitura feita dentro de atualizar()
                if ev.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                    pass

                # Drift hold (Space ativa/desativa flags do e-brake assistido)
                if ev.key == pygame.K_SPACE:
                    carro1.ativar_drift()
                if ev.key in (pygame.K_LSHIFT, pygame.K_RSHIFT) and carro2 is not None:
                    carro2.drift_hold = True

            elif ev.type == pygame.KEYUP:
                if ev.key == pygame.K_SPACE:
                    carro1.desativar_drift()
                if ev.key in (pygame.K_LSHIFT, pygame.K_RSHIFT) and carro2 is not None:
                    carro2.drift_hold = False

            elif ev.type == pygame.MOUSEBUTTONDOWN:
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
                            print(f"Checkpoint {indice} selecionado para arrastar")
                        else:
                            mods = pygame.key.get_mods()
                            if mods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL | pygame.KMOD_CTRL):
                                checkpoint_manager.adicionar_checkpoint_na_posicao(ev.pos[0], ev.pos[1], camera)
                            else:
                                arrastando_camera = True
                                checkpoint_manager.checkpoint_selecionado = -1
                                print("Modo arrastar câmera ativado - arraste para mover a câmera")

            elif ev.type == pygame.MOUSEBUTTONUP:
                if ev.button == 1:
                    if arrastando_checkpoint:
                        arrastando_checkpoint = False
                        checkpoint_em_arraste = -1
                        checkpoint_manager.checkpoint_em_arraste = -1
                        print("Checkpoint solto")
                    elif arrastando_camera:
                        arrastando_camera = False
                        print("Câmera solta")

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

        if not corrida.inicIAda:
            corrida.atualizar_contagem(dt)
        corrida.atualizar_tempo(dt)

        if tipo_jogo == TipoJogo.DRIFT and not jogo_pausado and not jogo_terminado:
            tempo_restante -= dt
            if tempo_restante <= 0:
                tempo_restante = 0
                jogo_terminado = True
                pontuacao_final = drift_scoring.points
                print(f"Tempo esgotado! Pontuação final: {pontuacao_final}")

        alguem_venceu = corrida.alguem_finalizou()

        # física com dt fixo
        while acumulador_dt >= dt_fixo:
            if corrida.pode_controlar() and not jogo_pausado and not jogo_terminado and not alguem_venceu:
                # player 1
                carro1.atualizar(teclas, mask_guias, dt_fixo)

                # player 2 (humano ou IA auxiliar)
                if carro2 is not None:
                    if modo_jogo == ModoJogo.DOIS_JOGADORES:
                        carro2.atualizar(teclas, mask_guias, dt_fixo)
                    elif USAR_IA_NO_CARRO_2 and not alguem_venceu:
                        IA2.controlar(carro2, mask_guias, is_on_track, dt_fixo)
                    else:
                        carro2.atualizar(teclas, mask_guias, dt_fixo)

                # IA principal (modo 1 jogador)
                if carro3 is not None and not alguem_venceu:
                    IA3.controlar(carro3, mask_guias, is_on_track, dt_fixo)

                # progresso nos checkpoints
                for c in carros:
                    corrida.atualizar_progresso_carro(c)

                # Drift scoring usando slip real (u/v)
                if tipo_jogo == TipoJogo.DRIFT:
                    vlong, vlat = carro1._mundo_para_local(carro1.vx, carro1.vy)
                    velocidade_kmh = abs(vlong) * 1.0 * (200.0 / 650.0)  # escala automática
                    angulo_drift = abs(math.degrees(math.atan2(vlat, max(0.1, abs(vlong)))))
                    drift_ativado = getattr(carro1, 'drift_ativado', False)
                    derrapando = getattr(carro1, 'drifting', False)

                    drift_scoring.update(
                        dt_fixo,
                        angulo_drift,
                        velocidade_kmh,
                        carro1.x,
                        carro1.y,
                        drift_ativado,
                        derrapando,
                        collision_force=0.0
                    )

            acumulador_dt -= dt_fixo

        IA_update_timer += dt
        if IA_update_timer >= IA_update_interval:
            IA_update_timer = 0.0
            # IA já atualizou no passo fixo

        camera.atualizar(dt)

        if camera_p1 is not None and camera_p2 is not None:
            camera_p1.atualizar(dt)
            camera_p2.atualizar(dt)

        # câmera dinâmica para 1 jogador
        if modo_jogo != ModoJogo.DOIS_JOGADORES:
            if hasattr(carro1, 'vx') and hasattr(carro1, 'vy'):
                velocidade = math.hypot(carro1.vx, carro1.vy)
                if velocidade < 30:
                    zoom = 1.4 - (velocidade / 30) * 0.3
                elif velocidade < 80:
                    zoom = 1.1 - ((velocidade - 30) / 50) * 0.3
                else:
                    zoom = 0.8 - min((velocidade - 80) / 120, 1.0) * 0.1
                zoom = max(0.7, min(1.4, zoom))
                camera.zoom += (zoom - camera.zoom) * dt * 0.8
                offset_y = (1.0 - camera.zoom) * 40
                camera.cy += (carro1.y + offset_y - camera.cy) * dt * 1.5
                camera.cx += (carro1.x - camera.cx) * dt * 2.0

        renderizar_frame = True

        if renderizar_frame:
            # split-screen 2P
            if modo_jogo == ModoJogo.DOIS_JOGADORES and carro2 is not None:
                metade_largura = LARGURA // 2
                superficie_p1 = pygame.Surface((metade_largura, ALTURA))
                superficie_p2 = pygame.Surface((metade_largura, ALTURA))

                # lado esquerdo (P1)
                camera_p1.set_alvo(carro1)
                camera_p1.desenhar_fundo(superficie_p1, img_pista)
                # Desenhar skidmarks antes dos carros (por baixo)
                carro1.skidmarks.desenhar(superficie_p1, camera_p1)
                carros_visiveis_p1 = [carro for carro in carros if camera_p1.esta_visivel(carro.x, carro.y, 30)]
                for carro in carros_visiveis_p1:
                    carro.desenhar(superficie_p1, camera=camera_p1)
                checkpoint_atual_p1 = corrida.proximo_checkpoint.get(carro1, 0)
                if not corrida.finalizou.get(carro1, False):
                    idx_cp = checkpoint_atual_p1 % len(checkpoints)
                    cx, cy = checkpoints[idx_cp]
                    screen_x, screen_y = camera_p1.mundo_para_tela(cx, cy)
                    pygame.draw.circle(superficie_p1, (0, 255, 255), (int(screen_x), int(screen_y)), 20, 4)
                    pygame.draw.circle(superficie_p1, (0, 200, 255), (int(screen_x), int(screen_y)), 16)
                    texto_checkpoint = fonte_checkpoint.render(str(idx_cp + 1), True, (255, 255, 255))
                    texto_rect = texto_checkpoint.get_rect(center=(int(screen_x), int(screen_y)))
                    superficie_p1.blit(texto_checkpoint, texto_rect)

                # lado direito (P2)
                camera_p2.set_alvo(carro2)
                camera_p2.desenhar_fundo(superficie_p2, img_pista)
                # Desenhar skidmarks antes dos carros (por baixo)
                if carro2:
                    carro2.skidmarks.desenhar(superficie_p2, camera_p2)
                carros_visiveis_p2 = [carro for carro in carros if camera_p2.esta_visivel(carro.x, carro.y, 30)]
                for carro in carros_visiveis_p2:
                    carro.desenhar(superficie_p2, camera=camera_p2)
                checkpoint_atual_p2 = corrida.proximo_checkpoint.get(carro2, 0)
                if not corrida.finalizou.get(carro2, False):
                    idx_cp2 = checkpoint_atual_p2 % len(checkpoints)
                    cx2, cy2 = checkpoints[idx_cp2]
                    screen_x2, screen_y2 = camera_p2.mundo_para_tela(cx2, cy2)
                    pygame.draw.circle(superficie_p2, (255, 255, 0), (int(screen_x2), int(screen_y2)), 20, 4)
                    pygame.draw.circle(superficie_p2, (255, 200, 0), (int(screen_x2), int(screen_y2)), 16)
                    texto_checkpoint2 = fonte_checkpoint.render(str(idx_cp2 + 1), True, (0, 0, 0))
                    texto_rect2 = texto_checkpoint2.get_rect(center=(int(screen_x2), int(screen_y2)))
                    superficie_p2.blit(texto_checkpoint2, texto_rect2)

                tela.blit(superficie_p1, (0, 0))
                tela.blit(superficie_p2, (metade_largura, 0))
                pygame.draw.line(tela, (255, 255, 255), (metade_largura, 0), (metade_largura, ALTURA), 2)
                camera.set_alvo(carro1)

            else:
                # 1 jogador
                camera.desenhar_fundo(tela, img_pista)
                # Desenhar skidmarks antes dos carros (por baixo)
                carro1.skidmarks.desenhar(tela, camera)
                carros_visiveis = [carro for carro in carros if camera.esta_visivel(carro.x, carro.y, 50)]
                carros_ordenados = sorted(
                    carros_visiveis, key=lambda c: (c.x - camera.cx) ** 2 + (c.y - camera.cy) ** 2
                )
                for carro in carros_ordenados:
                    carro.desenhar(tela, camera=camera)

        # Debug IA (opcional)
        if renderizar_frame and (debug_IA or mostrar_debug):
            if modo_jogo != ModoJogo.DOIS_JOGADORES and carro2 is not None:
                IA2.desenhar_debug(tela, camera=camera, mostrar_todos_checkpoints=False)
            if carro3 is not None:
                IA3.desenhar_debug(tela, camera=camera, mostrar_todos_checkpoints=False)

        # Editor de checkpoints
        if renderizar_frame and checkpoint_manager.modo_edicao:
            checkpoint_manager.desenhar(tela, camera)

        # Próximo checkpoint do player, em 1P
        if renderizar_frame and checkpoints and not checkpoint_manager.modo_edicao and tipo_jogo != TipoJogo.DRIFT:
            if modo_jogo != ModoJogo.DOIS_JOGADORES:
                checkpoint_atual = corrida.proximo_checkpoint.get(carro1, 0)
                if not corrida.finalizou.get(carro1, False):
                    idx_cp = checkpoint_atual % len(checkpoints)
                    cx, cy = checkpoints[idx_cp]
                    screen_x, screen_y = camera.mundo_para_tela(cx, cy)
                    pygame.draw.circle(tela, (0, 255, 255), (int(screen_x), int(screen_y)), 20, 4)
                    pygame.draw.circle(tela, (0, 200, 255), (int(screen_x), int(screen_y)), 16)
                    texto_checkpoint = fonte_checkpoint.render(str(idx_cp + 1), True, (255, 255, 255))
                    texto_rect = texto_checkpoint.get_rect(center=(int(screen_x), int(screen_y)))
                    tela.blit(texto_checkpoint, texto_rect)

        if renderizar_frame:
            # HUD completo
            if mostrar_hud:
                if modo_jogo == ModoJogo.DOIS_JOGADORES and carro2 is not None:
                    hud.desenhar_hud_completo(tela, carro1)
                    hud.desenhar_hud_completo(tela, carro2)
                else:
                    hud.desenhar_hud_completo(tela, carro1)

                # Timer modo drift
                if tipo_jogo == TipoJogo.DRIFT:
                    minutos = int(tempo_restante // 60)
                    segundos = int(tempo_restante % 60)
                    tempo_texto = f"Tempo: {minutos:02d}:{segundos:02d}"
                    if tempo_restante > 30:
                        cor_tempo = (255, 255, 255)
                    elif tempo_restante > 10:
                        cor_tempo = (255, 255, 0)
                    else:
                        cor_tempo = (255, 0, 0)
                    fonte_tempo = pygame.font.Font(None, 48)
                    texto_tempo = fonte_tempo.render(tempo_texto, True, cor_tempo)
                    tela.blit(texto_tempo, (LARGURA - 200, 50))

                    if jogo_pausado:
                        fonte_pause = pygame.font.Font(None, 72)
                        texto_pause = fonte_pause.render("PAUSADO", True, (255, 255, 255))
                        texto_pause_rect = texto_pause.get_rect(center=(LARGURA//2, ALTURA//2))
                        tela.blit(texto_pause, texto_pause_rect)
                        fonte_instrucao = pygame.font.Font(None, 36)
                        texto_instrucao = fonte_instrucao.render("Pressione ESC para continuar", True, (200, 200, 200))
                        texto_instrucao_rect = texto_instrucao.get_rect(center=(LARGURA//2, ALTURA//2 + 50))
                        tela.blit(texto_instrucao, texto_instrucao_rect)

                    if jogo_terminado and tipo_jogo == TipoJogo.DRIFT:
                        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                        overlay.fill((0, 0, 0, 150))
                        tela.blit(overlay, (0, 0))
                        fonte_titulo = pygame.font.Font(None, 72)
                        texto_titulo = fonte_titulo.render("TEMPO ESGOTADO!", True, (255, 255, 255))
                        texto_titulo_rect = texto_titulo.get_rect(center=(LARGURA//2, ALTURA//2 - 100))
                        tela.blit(texto_titulo, texto_titulo_rect)
                        fonte_pontuacao = pygame.font.Font(None, 48)
                        texto_pontuacao = fonte_pontuacao.render(f"Pontuação Final: {pontuacao_final}", True, (255, 255, 0))
                        texto_pontuacao_rect = texto_pontuacao.get_rect(center=(LARGURA//2, ALTURA//2 - 20))
                        tela.blit(texto_pontuacao, texto_pontuacao_rect)
                        fonte_instrucao = pygame.font.Font(None, 36)
                        texto_instrucao = fonte_instrucao.render("Pressione ESC para voltar ao menu", True, (200, 200, 200))
                        texto_instrucao_rect = texto_instrucao.get_rect(center=(LARGURA//2, ALTURA//2 + 50))
                        tela.blit(texto_instrucao, texto_instrucao_rect)

                # HUD de drift (1P)
                if mostrar_drift_hud and tipo_jogo == TipoJogo.DRIFT:
                    fonte_drift = pygame.font.Font(None, 24)
                    drift_scoring.draw_hud(tela, 20, 20, fonte_drift)

            if mostrar_fps:
                fps_atual = int(relogio.get_fps())
                fps_texto = fonte_small.render(f"FPS: {fps_atual}", True, (255, 255, 255))
                tela.blit(fps_texto, (largura_atual - 100, 10))
                if mostrar_debug:
                    from core.pista import obter_estatisticas_cache
                    stats = obter_estatisticas_cache()
                    cache_texto = fonte_small.render(f"Cache: {stats['hit_rate']:.1f}% ({stats['cache_size']})", True, (255, 255, 255))
                    tela.blit(cache_texto, (largura_atual - 200, 30))

            corrida.desenhar_semaforo(tela, largura_atual, altura_atual)
            if corrida.alguem_finalizou():
                corrida.desenhar_podio(tela, largura_atual, altura_atual, [carro1, carro2, carro3])

            # telas de vitória
            if modo_jogo == ModoJogo.DOIS_JOGADORES and carro2 is not None and alguem_venceu:
                vencedor = None
                if corrida.finalizou.get(carro1, False):
                    vencedor = "JOGADOR 1"
                elif corrida.finalizou.get(carro2, False):
                    vencedor = "JOGADOR 2"
                if vencedor:
                    overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 150))
                    tela.blit(overlay, (0, 0))
                    fonte_vitoria = pygame.font.Font(None, 72)
                    texto_vitoria = fonte_vitoria.render(f"{vencedor} VENCEU!", True, (255, 215, 0))
                    texto_vitoria_rect = texto_vitoria.get_rect(center=(LARGURA//2, ALTURA//2 - 80))
                    tela.blit(texto_vitoria, texto_vitoria_rect)
                    fonte_parou = pygame.font.Font(None, 48)
                    texto_parou = fonte_parou.render("CORRIDA FINALIZADA!", True, (255, 255, 255))
                    texto_parou_rect = texto_parou.get_rect(center=(LARGURA//2, ALTURA//2 - 20))
                    tela.blit(texto_parou, texto_parou_rect)
                    fonte_instrucao = pygame.font.Font(None, 36)
                    texto_instrucao = fonte_instrucao.render("Pressione ESC para voltar ao menu", True, (200, 200, 200))
                    texto_instrucao_rect = texto_instrucao.get_rect(center=(LARGURA//2, ALTURA//2 + 50))
                    tela.blit(texto_instrucao, texto_instrucao_rect)

            elif modo_jogo != ModoJogo.DOIS_JOGADORES and alguem_venceu and tipo_jogo != TipoJogo.DRIFT:
                vencedor = None
                if corrida.finalizou.get(carro1, False):
                    vencedor = "JOGADOR VENCEU!"
                elif carro3 and corrida.finalizou.get(carro3, False):
                    vencedor = "IA VENCEU!"
                if vencedor:
                    overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 150))
                    tela.blit(overlay, (0, 0))
                    fonte_vitoria = pygame.font.Font(None, 72)
                    texto_vitoria = fonte_vitoria.render(vencedor, True, (255, 215, 0))
                    texto_vitoria_rect = texto_vitoria.get_rect(center=(LARGURA//2, ALTURA//2 - 80))
                    tela.blit(texto_vitoria, texto_vitoria_rect)
                    fonte_parou = pygame.font.Font(None, 48)
                    texto_parou = fonte_parou.render("CORRIDA FINALIZADA!", True, (255, 255, 255))
                    texto_parou_rect = texto_parou.get_rect(center=(LARGURA//2, ALTURA//2 - 20))
                    tela.blit(texto_parou, texto_parou_rect)
                    fonte_instrucao = pygame.font.Font(None, 36)
                    texto_instrucao = fonte_instrucao.render("Pressione ESC para voltar ao menu", True, (200, 200, 200))
                    texto_instrucao_rect = texto_instrucao.get_rect(center=(LARGURA//2, ALTURA//2 + 50))
                    tela.blit(texto_instrucao, texto_instrucao_rect)

        pygame.display.update()

if __name__ == "__main__":
    from core.menu import run
    run()
