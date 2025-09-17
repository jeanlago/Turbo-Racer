import os
import pygame
from config import (
    LARGURA, ALTURA, FPS, TURBO_P1, TURBO_P2,
    USAR_IA_NO_CARRO_2, MODO_DRIFT, CONFIGURACOES,
    MAPAS_DISPONIVEIS, MAPA_ATUAL, obter_caminho_mapa, obter_caminho_guias
)
from core.pista import (
    carregar_pista, gerar_rota_pp, eh_pixel_da_pista, eh_pixel_transitavel,
    salvar_waypoints, densificar, suavizar_chaikin, desenhar_rota_debug,
    desenhar_checkpoints, extrair_checkpoints, calcular_posicoes_iniciais
)
from core.checkpoint_manager import CheckpointManager
from core.carro import Carro
from core.corrida import GerenciadorCorrida, GerenciadorDrift
from core.camera import Camera
from core.ia_simples import IASimples
from core.musica import gerenciador_musica

CARROS_DISPONIVEIS = [
    {"nome": "Mustang", "prefixo_cor": "Car1", "posicao": (570, 145), "sprite_selecao": "Car1"},
    {"nome": "Carro 2", "prefixo_cor": "Car2", "posicao": (570, 190), "sprite_selecao": "Car2"},
    {"nome": "Carro 3", "prefixo_cor": "Car3", "posicao": (560, 210), "sprite_selecao": "Car3"},
    {"nome": "Carro 4", "prefixo_cor": "Car4", "posicao": (580, 160), "sprite_selecao": "Car4"},
    {"nome": "Carro 5", "prefixo_cor": "Car5", "posicao": (590, 175), "sprite_selecao": "Car5"},
    {"nome": "Carro 6", "prefixo_cor": "Car6", "posicao": (550, 200), "sprite_selecao": "Car6"},
    {"nome": "Carro 7", "prefixo_cor": "Car7", "posicao": (600, 185), "sprite_selecao": "Car7"},
    {"nome": "Carro 8", "prefixo_cor": "Car8", "posicao": (540, 220), "sprite_selecao": "Car8"},
    {"nome": "Carro 9", "prefixo_cor": "Car9", "posicao": (610, 195), "sprite_selecao": "Car9"},
    {"nome": "Carro 10", "prefixo_cor": "Car10", "posicao": (530, 240), "sprite_selecao": "Car10"},
    {"nome": "Carro 11", "prefixo_cor": "Car11", "posicao": (620, 205), "sprite_selecao": "Car11"},
    {"nome": "Carro 12", "prefixo_cor": "Car12", "posicao": (520, 260), "sprite_selecao": "Car12"},
]

def principal(carro_selecionado_p1=0, carro_selecionado_p2=1, mapa_selecionado=None):
    pygame.init()
    
    from config import carregar_configuracoes
    carregar_configuracoes()
    
    resolucao = CONFIGURACOES["video"]["resolucao"]
    fullscreen = CONFIGURACOES["video"]["fullscreen"]
    tela_cheia_sem_bordas = CONFIGURACOES["video"]["tela_cheia_sem_bordas"]
    qualidade_alta = CONFIGURACOES["video"]["qualidade_alta"]
    vsync = CONFIGURACOES["video"]["vsync"]
    fps_max = CONFIGURACOES["video"]["fps_max"]
    
    flags_display = 0
    if fullscreen:
        flags_display |= pygame.FULLSCREEN
    elif tela_cheia_sem_bordas:
        flags_display |= pygame.NOFRAME
    
    if qualidade_alta:
        pygame.display.set_mode(resolucao, flags_display)
    else:
        pygame.display.set_mode(resolucao, flags_display)
    
    tela = pygame.display.set_mode(resolucao, flags_display)
    
    pygame.display.set_caption("Turbo Racer")
    relogio = pygame.time.Clock()

    from config import MAPA_ATUAL
    mapa_atual = mapa_selecionado if mapa_selecionado and mapa_selecionado in MAPAS_DISPONIVEIS else MAPA_ATUAL
    
    if mapa_atual != MAPA_ATUAL:
        import config
        config.MAPA_ATUAL = mapa_atual
        from config import obter_caminho_mapa, obter_caminho_guias
        config.CAMINHO_MAPA = obter_caminho_mapa()
        config.CAMINHO_GUIAS = obter_caminho_guias()
    
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
    mostrar_fps = CONFIGURACOES["jogo"]["mostrar_fps"]
    mostrar_debug = CONFIGURACOES["jogo"]["mostrar_debug"]

    fonte = pygame.font.SysFont("consolas", 26)
    fonte_small = pygame.font.SysFont("consolas", 18)
    corrida = GerenciadorCorrida(fonte)
    drift = GerenciadorDrift(fonte) if modo_drift_atual else None

    carro_p1 = CARROS_DISPONIVEIS[carro_selecionado_p1]
    carro_p2 = CARROS_DISPONIVEIS[carro_selecionado_p2]
    
    posicoes_iniciais = calcular_posicoes_iniciais(mask_guias)
    pos_inicial_p1 = posicoes_iniciais['p1']
    pos_inicial_p2 = posicoes_iniciais['p2']
    pos_inicial_ia = posicoes_iniciais['ia']
    
    carro1 = Carro(
        pos_inicial_p1[0], pos_inicial_p1[1],
        carro_p1["prefixo_cor"], 
        (pygame.K_w, pygame.K_d, pygame.K_a, pygame.K_s), 
        turbo_key=TURBO_P1,
        nome=carro_p1["nome"]
    )
    carro2 = Carro(
        pos_inicial_p2[0], pos_inicial_p2[1],
        carro_p2["prefixo_cor"], 
        (pygame.K_UP, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_DOWN), 
        turbo_key=TURBO_P2,
        nome=carro_p2["nome"]
    )
    carro3 = Carro(pos_inicial_ia[0], pos_inicial_ia[1], "Car3", (0, 0, 0, 0), nome="IA-1")

    for c in [carro1, carro2, carro3]:
        corrida.registrar_carro(c)

    camera.set_alvo(carro1)

    ia2 = IASimples(checkpoints, nome="IA-1")
    ia3 = IASimples(checkpoints, nome="IA-2")
    debug_ia = True
    debug_rota = False

    gravando = False
    pontos_gravados = []
    distancia_minima_registro = 18.0
    
    arrastando_checkpoint = False
    checkpoint_em_arraste = -1

    def is_on_track(x, y):
        return eh_pixel_transitavel(mask_guias, x, y)
    
    if CONFIGURACOES["audio"]["musica_habilitada"] and CONFIGURACOES["audio"]["musica_no_jogo"]:
        gerenciador_musica.definir_volume(CONFIGURACOES["audio"]["volume_musica"])
        if not gerenciador_musica.musica_tocando:
            if CONFIGURACOES["audio"]["musica_aleatoria"]:
                gerenciador_musica.musica_aleatoria()
            else:
                gerenciador_musica.tocar_musica()
    
    rodando = True
    while rodando:
        dt = relogio.tick(fps_max) / 1000.0
        
        gerenciador_musica.verificar_fim_musica()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                rodando = False

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_F1:
                    debug_ia = not debug_ia
                    ia2.debug = ia3.debug = debug_ia
                elif ev.key == pygame.K_F2:
                    debug_rota = not debug_rota
                elif ev.key == pygame.K_F3:
                    gravando = not gravando
                    if gravando:
                        pontos_gravados.clear()
                elif ev.key == pygame.K_F4:
                    if len(pontos_gravados) >= 6:
                        base = pontos_gravados[:]
                        base = suavizar_chaikin(base, iters=2)
                        base = densificar(base, passo=26)
                        salvar_waypoints(base)
                        rota = base
                        ia2.wp = [pygame.Vector2(p) for p in rota]
                        ia3.wp = [pygame.Vector2(p) for p in rota]
                elif ev.key == pygame.K_c:
                    pontos_gravados.clear()
                # Controles do editor de checkpoints
                elif ev.key == pygame.K_F5:
                    # Salvar checkpoints
                    if checkpoint_manager.salvar_checkpoints():
                        print("Checkpoints salvos com sucesso!")
                    else:
                        print("Erro ao salvar checkpoints!")
                elif ev.key == pygame.K_F6:
                    # Carregar checkpoints
                    checkpoint_manager.carregar_checkpoints()
                    # Atualizar IAs com novos checkpoints
                    checkpoints = checkpoint_manager.checkpoints
                    ia2.checkpoints = checkpoints
                    ia3.checkpoints = checkpoints
                    print(f"Checkpoints recarregados: {len(checkpoints)} pontos")
                elif ev.key == pygame.K_F7:
                    # Alternar modo de edição de checkpoints
                    checkpoint_manager.alternar_modo_edicao()
                elif ev.key == pygame.K_F8:
                    # Limpar todos os checkpoints
                    checkpoint_manager.checkpoints = []
                    checkpoint_manager.salvar_checkpoints()
                    checkpoints = []
                    ia2.checkpoints = []
                    ia3.checkpoints = []
                    print("Todos os checkpoints foram removidos!")
                elif ev.key == pygame.K_F9:
                    # Trocar para próximo mapa
                    mapas = list(MAPAS_DISPONIVEIS.keys())
                    indice_atual = mapas.index(mapa_atual)
                    proximo_indice = (indice_atual + 1) % len(mapas)
                    novo_mapa = mapas[proximo_indice]
                    
                    if checkpoint_manager.trocar_mapa(novo_mapa):
                        # Recarregar pista e checkpoints
                        import config
                        config.MAPA_ATUAL = novo_mapa
                        config.CAMINHO_MAPA = obter_caminho_mapa()
                        config.CAMINHO_GUIAS = obter_caminho_guias()
                        
                        img_pista, mask_pista, mask_guias = carregar_pista()
                        checkpoints = checkpoint_manager.checkpoints
                        ia2.checkpoints = checkpoints
                        ia3.checkpoints = checkpoints
                        
                        # Atualizar posições iniciais para o novo mapa
                        posicoes_iniciais = calcular_posicoes_iniciais(mask_guias)
                        pos_inicial_p1 = posicoes_iniciais['p1']
                        pos_inicial_p2 = posicoes_iniciais['p2']
                        pos_inicial_ia = posicoes_iniciais['ia']
                        
                        carro1.x, carro1.y = pos_inicial_p1
                        carro2.x, carro2.y = pos_inicial_p2
                        carro3.x, carro3.y = pos_inicial_ia
                        
                        print(f"Trocado para mapa: {MAPAS_DISPONIVEIS[novo_mapa]['nome']}")
                elif ev.key == pygame.K_m:
                    # Alternar música
                    if gerenciador_musica.musica_tocando:
                        gerenciador_musica.parar_musica()
                    else:
                        gerenciador_musica.tocar_musica()
                elif ev.key == pygame.K_n:
                    # Próxima música
                    gerenciador_musica.proxima_musica()
                elif ev.key == pygame.K_F11:
                    # Alternar entre modos de tela: Janela -> Tela Cheia Sem Bordas -> Fullscreen -> Janela
                    if not fullscreen and not tela_cheia_sem_bordas:
                        # Janela -> Tela Cheia Sem Bordas
                        tela_cheia_sem_bordas = True
                        fullscreen = False
                        display_flags = pygame.NOFRAME
                    elif tela_cheia_sem_bordas and not fullscreen:
                        # Tela Cheia Sem Bordas -> Fullscreen
                        tela_cheia_sem_bordas = False
                        fullscreen = True
                        display_flags = pygame.FULLSCREEN
                    else:
                        # Fullscreen -> Janela
                        fullscreen = False
                        tela_cheia_sem_bordas = False
                        display_flags = 0
                    
                    # Aplicar novo modo
                    tela = pygame.display.set_mode(resolucao, display_flags)
                    
                    # Atualizar configurações
                    CONFIGURACOES["video"]["fullscreen"] = fullscreen
                    CONFIGURACOES["video"]["tela_cheia_sem_bordas"] = tela_cheia_sem_bordas

                # ---------- TURBO (Ctrl) P1 e P2 (barra/hold) ----------
                if ev.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                    # (se quiser “burst”, chame carro1.usar_turbo_burst() aqui em vez do hold)
                    pass  # o hold é lido direto no update por tecla

                # ---------- DRIFT HOLD ----------
                # P1: Space
                if ev.key == pygame.K_SPACE:
                    carro1.drift_hold = True
                # P2: Shift (L/R)
                if ev.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    carro2.drift_hold = True

            elif ev.type == pygame.KEYUP:
                if ev.key == pygame.K_SPACE:
                    carro1.drift_hold = False
                if ev.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    carro2.drift_hold = False
            
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    if checkpoint_manager.modo_edicao:
                        mundo_x, mundo_y = camera.tela_para_mundo(ev.pos[0], ev.pos[1])
                        indice = checkpoint_manager.encontrar_checkpoint_proximo(mundo_x, mundo_y, 30)
                        
                        if indice >= 0:
                            arrastando_checkpoint = True
                            checkpoint_em_arraste = indice
                            checkpoint_manager.checkpoint_selecionado = indice
                            checkpoint_manager.checkpoint_em_arraste = indice
                        else:
                            checkpoint_manager.processar_clique(ev.pos[0], ev.pos[1], camera)
            
            elif ev.type == pygame.MOUSEBUTTONUP:
                if ev.button == 1:
                    if arrastando_checkpoint:
                        arrastando_checkpoint = False
                        checkpoint_em_arraste = -1
                        checkpoint_manager.checkpoint_em_arraste = -1
            
            elif ev.type == pygame.MOUSEMOTION:
                if arrastando_checkpoint and checkpoint_em_arraste >= 0:
                    mundo_x, mundo_y = camera.tela_para_mundo(ev.pos[0], ev.pos[1])
                    checkpoint_manager.mover_checkpoint(checkpoint_em_arraste, mundo_x, mundo_y)

        teclas = pygame.key.get_pressed()
        
        checkpoint_manager.processar_teclado(teclas)

        if not corrida.iniciada:
            corrida.atualizar_contagem(dt)
        corrida.atualizar_tempo(dt)

        if corrida.pode_controlar():
            carro1.atualizar(teclas, mask_guias, dt)

            if gravando:
                if not pontos_gravados:
                    pontos_gravados.append((carro1.x, carro1.y))
                else:
                    lx, ly = pontos_gravados[-1]
                    dx, dy = carro1.x - lx, carro1.y - ly
                    if dx*dx + dy*dy >= distancia_minima_registro*distancia_minima_registro:
                        pontos_gravados.append((carro1.x, carro1.y))

            if USAR_IA_NO_CARRO_2:
                ia2.controlar(carro2, mask_guias, is_on_track, dt)
            else:
                carro2.atualizar(teclas, mask_guias, dt)

            ia3.controlar(carro3, mask_guias, is_on_track, dt)

            for c in (carro1, carro2, carro3):
                corrida.atualizar_progresso_carro(c)

            if modo_drift_atual and drift is not None:
                drift.atualizar(carro1, dt)

        camera.atualizar(dt)

        camera.desenhar_fundo(tela, img_pista)

        carro1.desenhar(tela, camera=camera)
        carro2.desenhar(tela, camera=camera)
        carro3.desenhar(tela, camera=camera)

        if debug_ia or mostrar_debug:
            ia2.desenhar_debug(tela, camera=camera)
            ia3.desenhar_debug(tela, camera=camera)
        
        checkpoint_manager.desenhar(tela, camera)

        if gravando:
            for (x, y) in pontos_gravados:
                sx, sy = camera.mundo_para_tela(x, y)
                pygame.draw.circle(tela, (255, 100, 100), (int(sx), int(sy)), 3)
            msg = "[GRAVANDO WAYPOINTS] F3: parar | F4: salvar | C: limpar"
            sombra = fonte_small.render(msg, True, (0, 0, 0))
            txt = fonte_small.render(msg, True, (255, 220, 120))
            tela.blit(sombra, (20+1, altura_atual-28+1))
            tela.blit(txt, (20, altura_atual-28))

        if modo_drift_atual and drift is not None:
            drift.desenhar_hud(tela, 8, 8)
        else:
            corrida.desenhar_hud(tela, [carro1, carro2, carro3])

        if mostrar_fps:
            fps_atual = int(relogio.get_fps())
            fps_texto = fonte_small.render(f"FPS: {fps_atual}", True, (255, 255, 255))
            tela.blit(fps_texto, (largura_atual - 100, 10))
        
        if checkpoint_manager.modo_edicao:
            controles_texto = [
                "F7: Sair do modo edição",
                "F5: Salvar checkpoints",
                "F6: Carregar checkpoints",
                "F8: Limpar todos",
                "F9: Próximo mapa",
                "Clique: Adicionar/Mover",
                "DEL: Remover selecionado"
            ]
            
            for i, texto in enumerate(controles_texto):
                cor = (255, 255, 0) if i < 2 else (200, 200, 200)
                tela.blit(fonte_small.render(texto, True, cor), (largura_atual - 300, 10 + i * 20))
        else:
            tela.blit(fonte_small.render("F7: Modo edição de checkpoints", True, (255, 255, 255)), 
                     (largura_atual - 300, 10))

        corrida.desenhar_semaforo(tela, largura_atual, altura_atual)
        if corrida.alguem_finalizou():
            corrida.desenhar_podio(tela, largura_atual, altura_atual, [carro1, carro2, carro3])


        pygame.display.update()

if __name__ == "__main__":
    from core.menu import run
    run()
