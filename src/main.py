import os
import math
import pygame
from config import (
    LARGURA, ALTURA, FPS, TURBO_P1, TURBO_P2,
    USAR_IA_NO_CARRO_2, CONFIGURACOES,
    MAPAS_DISPONIVEIS, MAPA_ATUAL, obter_caminho_mapa, obter_caminho_guias
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
    {"nome": "Nissan Skyline", "prefixo_cor": "Car6", "posicao": (550, 200), "sprite_selecao": "Car6", "tipo_tracao": "front", "tamanho_oficina": (900, 650), "posicao_oficina": (LARGURA//2 - 450, 215)},
    {"nome": "Nissan Silvia S13", "prefixo_cor": "Car7", "posicao": (600, 185), "sprite_selecao": "Car7", "tipo_tracao": "rear", "tamanho_oficina": (600, 300), "posicao_oficina": (LARGURA//2 - 300, 380)},
    {"nome": "Mazda RX-7", "prefixo_cor": "Car8", "posicao": (540, 220), "sprite_selecao": "Car8", "tipo_tracao": "awd", "tamanho_oficina": (600, 300), "posicao_oficina": (LARGURA//2 - 300, 380)},
    {"nome": "Toyota Celica", "prefixo_cor": "Car9", "posicao": (610, 195), "sprite_selecao": "Car9", "tipo_tracao": "rear", "tamanho_oficina": (600, 300), "posicao_oficina": (LARGURA//2 - 350, 380)},
    {"nome": "Volkswagem Fusca", "prefixo_cor": "Car10", "posicao": (530, 240), "sprite_selecao": "Car10", "tipo_tracao": "front", "tamanho_oficina": (750, 550), "posicao_oficina": (LARGURA//2 - 400, 250)},
    {"nome": "Mitsubishi Lancer", "prefixo_cor": "Car11", "posicao": (620, 205), "sprite_selecao": "Car11", "tipo_tracao": "rear", "tamanho_oficina": (600, 300), "posicao_oficina": (LARGURA//2 - 300, 380)},
    {"nome": "Subaru WRX", "prefixo_cor": "Car12", "posicao": (520, 260), "sprite_selecao": "Car12", "tipo_tracao": "awd", "tamanho_oficina": (600, 300), "posicao_oficina": (LARGURA//2 - 300, 380)},
]

def principal(carro_selecionado_p1=0, carro_selecionado_p2=1, mapa_selecionado=None, modo_jogo=ModoJogo.UM_JOGADOR, tipo_jogo=TipoJogo.CORRIDA):
    pygame.init()
    
    from config import carregar_configuracoes
    carregar_configuracoes()
    
    resolucao = CONFIGURACOES["video"]["resolucao"]
    fullscreen = CONFIGURACOES["video"]["fullscreen"]
    tela_cheIA_sem_bordas = CONFIGURACOES["video"]["tela_cheIA_sem_bordas"]
    qualidade_alta = CONFIGURACOES["video"]["qualidade_alta"]
    vsync = CONFIGURACOES["video"]["vsync"]
    fps_max = max(CONFIGURACOES["video"]["fps_max"], 200)  # Mínimo 200 FPS
    
    flags_display = 0
    if fullscreen:
        flags_display |= pygame.FULLSCREEN
    elif tela_cheIA_sem_bordas:
        flags_display |= pygame.NOFRAME
    
    # Aplicar configurações de qualidade
    tela = pygame.display.set_mode(resolucao, flags_display)
    
    # Configurar VSync se habilitado
    if vsync:
        pygame.display.set_mode(resolucao, flags_display | pygame.DOUBLEBUF)
    
    pygame.display.set_caption("Turbo Racer")
    relogio = pygame.time.Clock()
    
    # Configurar fonte para FPS se habilitado
    if CONFIGURACOES["video"]["mostrar_fps"]:
        pygame.font.init()
        fonte_fps = pygame.font.Font(None, 36)
    
    # Função para aplicar qualidade nas imagens
    def aplicar_qualidade_imagem(imagem):
        if not qualidade_alta:
            # Reduzir qualidade da imagem para melhor performance
            largura, altura = imagem.get_size()
            nova_largura = largura // 2
            nova_altura = altura // 2
            imagem_redimensionada = pygame.transform.scale(imagem, (nova_largura, nova_altura))
            return pygame.transform.scale(imagem_redimensionada, (largura, altura))
        return imagem

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
    
    # Câmeras separadas serão criadas após a criação dos carros

    modo_drift_atual = CONFIGURACOES["jogo"]["modo_drift"]
    mostrar_fps = CONFIGURACOES["video"]["mostrar_fps"]
    mostrar_debug = CONFIGURACOES["jogo"]["mostrar_debug"]

    # CrIAr fontes uma única vez para evitar recrIAção
    fonte = pygame.font.SysFont("consolas", 26)
    fonte_small = pygame.font.SysFont("consolas", 18)
    fonte_checkpoint = pygame.font.SysFont("consolas", 18, bold=True)
    fonte_debug = pygame.font.SysFont("consolas", 16)
    fonte_debug_bold = pygame.font.SysFont("consolas", 16, bold=True)
    corrida = GerencIAdorCorrida(fonte)
    # drift = GerencIAdorDrift(fonte) if modo_drift_atual else None  # Removido - não usado

    carro_p1 = CARROS_DISPONIVEIS[carro_selecionado_p1]
    carro_p2 = CARROS_DISPONIVEIS[carro_selecionado_p2]
    
    posicoes_iniciais = calcular_posicoes_iniciais(mask_guias)
    pos_inicial_p1 = posicoes_iniciais['p1']
    pos_inicial_p2 = posicoes_iniciais['p2']
    pos_inicial_IA = posicoes_iniciais['IA']
    
    # Criar carros baseado no modo de jogo
    carros = []
    
    # Sempre criar o jogador 1
    carro1 = CarroFisica(
        pos_inicial_p1[0], pos_inicial_p1[1],
        carro_p1["prefixo_cor"], 
        (pygame.K_w, pygame.K_d, pygame.K_a, pygame.K_s), 
        turbo_key=TURBO_P1,
        nome=carro_p1["nome"],
        tipo_tracao=carro_p1.get("tipo_tracao", CarroFisica.TRACAO_TRASEIRA)
    )
    carros.append(carro1)
    
    # Criar jogador 2 apenas se não for modo drift e for 2 jogadores
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
    
    # Criar IA apenas se não for modo drift e não for 2 jogadores
    carro3 = None
    if tipo_jogo != TipoJogo.DRIFT and modo_jogo != ModoJogo.DOIS_JOGADORES:
        carro3 = Carro(pos_inicial_IA[0], pos_inicial_IA[1], "Car3", (0, 0, 0, 0), nome="IA-1")
        carros.append(carro3)

    # Registrar carros na corrida
    for c in carros:
        corrida.registrar_carro(c)

    camera.set_alvo(carro1)
    
    # InicIAlizar HUD
    hud = HUD()
    mostrar_hud = True  # Por padrão, mostrar HUD
    
    # InicIAlizar sistema de drift scoring
    drift_scoring = DriftScoring()
    mostrar_drift_hud = tipo_jogo == TipoJogo.DRIFT
    
    # Criar câmeras separadas para modo 2 jogadores
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
    
    # InicIAlizar IAs
    IA2 = IA(checkpoints, nome="IA-1")
    IA3 = IA(checkpoints, nome="IA-2")
    debug_IA = True
    
    # Otimização: limitar taxa de atualização da IA
    IA_update_timer = 0.0
    IA_update_interval = 1.0 / 30.0  # Atualizar IA a 30 FPS em vez de 60
    
    # Sistema de tempo e pause
    tempo_drift = 60.0  # 1 minuto para modo drift
    tempo_restante = tempo_drift
    jogo_pausado = False
    jogo_terminado = False
    pontuacao_final = 0
    
    # Variáveis de controle de checkpoint
    arrastando_checkpoint = False
    checkpoint_em_arraste = -1
    arrastando_camera = False
    ultimo_clique_tempo = 0
    debounce_tempo = 200  # 200ms de debounce
    
    if CONFIGURACOES["audio"]["musica_habilitada"] and CONFIGURACOES["audio"]["musica_no_jogo"]:
        gerencIAdor_musica.definir_volume(CONFIGURACOES["audio"]["volume_musica"])
        if not gerencIAdor_musica.musica_tocando:
            if CONFIGURACOES["audio"]["musica_aleatorIA"]:
                gerencIAdor_musica.musica_aleatorIA()
            else:
                gerencIAdor_musica.tocar_musica()
    
    rodando = True
    dt_fixo = 1.0 / 60.0  # Delta time fixo para física estável
    acumulador_dt = 0.0
    max_dt = 0.25  # Limitar delta time máximo
    
    while rodando:
        dt = relogio.tick(fps_max) / 1000.0
        dt = min(dt, max_dt)  # Limitar delta time máximo
        acumulador_dt += dt
        
        gerencIAdor_musica.verificar_fim_musica()

        # Processar eventos
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                rodando = False
            

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    # Sistema de pause
                    if not jogo_terminado:
                        jogo_pausado = not jogo_pausado
                        print(f"Jogo {'pausado' if jogo_pausado else 'retomado'}")
                    else:
                        # Se o jogo terminou, ESC volta ao menu
                        return
                elif ev.key == pygame.K_F1:
                    debug_IA = not debug_IA
                    IA2.debug = IA3.debug = debug_IA
                elif ev.key == pygame.K_h:
                    # Alternar HUD
                    mostrar_hud = not mostrar_hud
                    print(f"HUD: {'Ativado' if mostrar_hud else 'Desativado'}")

                # ---------- TURBO (Ctrl) P1 e P2 (barra/hold) ----------
                if ev.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                    # (se quiser “burst”, chame carro1.usar_turbo_burst() aqui em vez do hold)
                    pass  # o hold é lido direto no update por tecla

                # ---------- DRIFT HOLD ----------
                # P1: Space (CarroFisica - drift por clique)
                if ev.key == pygame.K_SPACE:
                    carro1.ativar_drift(teclas)
                # P2: Shift (L/R) - sistema antigo
                if ev.key in (pygame.K_LSHIFT, pygame.K_RSHIFT) and carro2 is not None:
                    carro2.drift_hold = True

            elif ev.type == pygame.KEYUP:
                if ev.key == pygame.K_SPACE:
                    carro1.desativar_drift()
                if ev.key in (pygame.K_LSHIFT, pygame.K_RSHIFT) and carro2 is not None:
                    carro2.drift_hold = False
            
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    if checkpoint_manager.modo_edicao:
                        # Debounce para evitar múltiplos cliques
                        tempo_atual = pygame.time.get_ticks()
                        if tempo_atual - ultimo_clique_tempo < debounce_tempo:
                            pass  # Ignorar clique muito rápido
                        else:
                            ultimo_clique_tempo = tempo_atual
                            
                            mundo_x, mundo_y = camera.tela_para_mundo(ev.pos[0], ev.pos[1])
                            indice = checkpoint_manager.encontrar_checkpoint_proximo(mundo_x, mundo_y, 30)
                            
                            if indice >= 0:
                                # Clicou em checkpoint - arrastar checkpoint
                                arrastando_checkpoint = True
                                checkpoint_em_arraste = indice
                                checkpoint_manager.checkpoint_selecionado = indice
                                checkpoint_manager.checkpoint_em_arraste = indice
                                print(f"Checkpoint {indice} selecionado para arrastar")
                            else:
                                # Verificar se Ctrl está pressionado para adicionar checkpoint
                                if teclas[pygame.K_LCTRL] or teclas[pygame.K_RCTRL]:
                                    checkpoint_manager.adicionar_checkpoint_na_posicao(ev.pos[0], ev.pos[1], camera)
                                else:
                                    # Clicou em área vazia - arrastar câmera
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
            
            elif ev.type == pygame.MOUSEMOTION:
                if checkpoint_manager.modo_edicao:
                    if arrastando_checkpoint and checkpoint_em_arraste >= 0:
                        # Arrastar checkpoint
                        mundo_x, mundo_y = camera.tela_para_mundo(ev.pos[0], ev.pos[1])
                        checkpoint_manager.mover_checkpoint(checkpoint_em_arraste, mundo_x, mundo_y)
                    elif arrastando_camera:
                        # Arrastar câmera - usar movimento relativo
                        if hasattr(ev, 'rel') and (ev.rel[0] != 0 or ev.rel[1] != 0):
                            # Sensibilidade ajustada para movimento mais suave
                            sensibilidade = 1.0 / camera.zoom
                            camera.cx -= ev.rel[0] * sensibilidade
                            camera.cy -= ev.rel[1] * sensibilidade

        teclas = pygame.key.get_pressed()
        
        checkpoint_manager.processar_teclado(teclas)
        checkpoint_manager.processar_teclas_f(teclas)

        if not corrida.inicIAda:
            corrida.atualizar_contagem(dt)
        corrida.atualizar_tempo(dt)
        
        # Sistema de tempo para modo drift
        if tipo_jogo == TipoJogo.DRIFT and not jogo_pausado and not jogo_terminado:
            tempo_restante -= dt
            if tempo_restante <= 0:
                tempo_restante = 0
                jogo_terminado = True
                pontuacao_final = drift_scoring.points
                print(f"Tempo esgotado! Pontuação final: {pontuacao_final}")

        # Verificar se alguém venceu no modo 2 jogadores
        alguem_venceu = False
        if modo_jogo == ModoJogo.DOIS_JOGADORES and carro2 is not None:
            if (hasattr(carro1, 'terminou_corrida') and carro1.terminou_corrida) or \
               (hasattr(carro2, 'terminou_corrida') and carro2.terminou_corrida):
                alguem_venceu = True

        # Física com delta time fixo para estabilidade
        while acumulador_dt >= dt_fixo:
            if corrida.pode_controlar() and not jogo_pausado and not jogo_terminado and not alguem_venceu:
                # Atualizar jogador 1
                carro1.atualizar(teclas, mask_guias, dt_fixo)


                # Atualizar jogador 2 se existir
                if carro2 is not None:
                    if modo_jogo == ModoJogo.DOIS_JOGADORES:
                        # No modo 2 jogadores, carro2 é controlado pelo jogador 2
                        carro2.atualizar(teclas, mask_guias, dt_fixo)
                    elif USAR_IA_NO_CARRO_2 and not alguem_venceu:
                        # No modo 1 jogador, carro2 pode ser IA (só se ninguém venceu)
                        IA2.controlar(carro2, mask_guias, is_on_track, dt_fixo)
                    else:
                        carro2.atualizar(teclas, mask_guias, dt_fixo)

                # Atualizar IA se existir (só se ninguém venceu)
                if carro3 is not None and not alguem_venceu:
                    IA3.controlar(carro3, mask_guias, is_on_track, dt_fixo)

                # Atualizar progresso de todos os carros
                for c in carros:
                    corrida.atualizar_progresso_carro(c)

                # Sistema de drift antigo removido - usando DriftScoring
                
                # Atualizar drift scoring se estiver no modo drift
                if tipo_jogo == TipoJogo.DRIFT:
                    # Calcular ângulo de drift e velocidade
                    velocidade_kmh = abs(carro1.velocidade) * 20.0
                    angulo_drift = abs(carro1.angulo) * 180.0 / math.pi
                    
                    # Verificar se está derrapando
                    drift_ativado = hasattr(carro1, 'drift_ativo') and carro1.drift_ativo
                    derrapando = hasattr(carro1, 'derrapando') and carro1.derrapando
                    
                    # Atualizar sistema de pontuação
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
        
        # Atualizar IA com taxa limitada para melhor performance
        IA_update_timer += dt
        if IA_update_timer >= IA_update_interval:
            IA_update_timer = 0.0
            # IA já foi atualizada no loop de física acima

        camera.atualizar(dt)
        
        # Atualizar câmeras separadas para modo 2 jogadores
        if camera_p1 is not None and camera_p2 is not None:
            camera_p1.atualizar(dt)
            camera_p2.atualizar(dt)
        
        # Câmera dinâmica para modo 1 jogador (incluindo drift)
        if modo_jogo != ModoJogo.DOIS_JOGADORES:
            # Calcular velocidade do jogador
            if hasattr(carro1, 'vx') and hasattr(carro1, 'vy'):
                velocidade = math.sqrt(carro1.vx * carro1.vx + carro1.vy * carro1.vy)
                
                # Definir zoom baseado na velocidade (mais conservador)
                # Velocidade baixa (0-30): zoom alto (1.4-1.1)
                # Velocidade média (30-80): zoom médio (1.1-0.8)
                # Velocidade alta (80+): zoom baixo (0.8-0.7)
                if velocidade < 30:
                    # Interpolação linear entre 1.4 e 1.1
                    zoom = 1.4 - (velocidade / 30) * 0.3
                elif velocidade < 80:
                    # Interpolação linear entre 1.1 e 0.8
                    zoom = 1.1 - ((velocidade - 30) / 50) * 0.3
                else:
                    # Interpolação linear entre 0.8 e 0.7 para velocidades altas
                    zoom = 0.8 - min((velocidade - 80) / 120, 1.0) * 0.1
                
                # Limitar zoom entre 0.7 e 1.4 (mais conservador)
                zoom = max(0.7, min(1.4, zoom))
                
                # Aplicar zoom suavemente com interpolação muito mais lenta
                camera.zoom = camera.zoom + (zoom - camera.zoom) * dt * 0.8
                
                # Ajustar posição da câmera de forma mais suave
                # Usar apenas offset vertical para evitar tremulação horizontal
                offset_y = (1.0 - camera.zoom) * 40   # Offset vertical reduzido
                
                # Aplicar offset muito mais suavemente
                camera.cy = camera.cy + (carro1.y + offset_y - camera.cy) * dt * 1.5
                
                # Manter a câmera seguindo o carro normalmente no eixo X
                camera.cx = camera.cx + (carro1.x - camera.cx) * dt * 2.0

        # Renderização sempre ativa - otimizações serão feitas em outros lugares
        renderizar_frame = True
        
        if renderizar_frame:
            # Verificar se é modo 2 jogadores para dividir a tela
            if modo_jogo == ModoJogo.DOIS_JOGADORES and carro2 is not None:
                # Dividir tela em duas metades
                metade_largura = LARGURA // 2
                
                # Criar superfícies para cada jogador
                superficie_p1 = pygame.Surface((metade_largura, ALTURA))
                superficie_p2 = pygame.Surface((metade_largura, ALTURA))
                
                # Renderizar jogador 1 (lado esquerdo)
                camera_p1.set_alvo(carro1)
                camera_p1.desenhar_fundo(superficie_p1, img_pista)
                
                # Culling para jogador 1
                carros_visiveis_p1 = []
                for carro in carros:
                    if camera_p1.esta_visivel(carro.x, carro.y, 30):
                        carros_visiveis_p1.append(carro)
                
                # Renderizar carros visíveis para jogador 1
                for carro in carros_visiveis_p1:
                    carro.desenhar(superficie_p1, camera=camera_p1)
                
                # Renderizar checkpoints para jogador 1 (lado esquerdo)
                if hasattr(carro1, 'checkpoint_atual') and carro1.checkpoint_atual < len(checkpoints):
                    cx, cy = checkpoints[carro1.checkpoint_atual]
                    screen_x, screen_y = camera_p1.mundo_para_tela(cx, cy)
                    
                    # Desenhar próximo checkpoint para o player 1 (azul)
                    pygame.draw.circle(superficie_p1, (0, 255, 255), (int(screen_x), int(screen_y)), 20, 4)
                    pygame.draw.circle(superficie_p1, (0, 200, 255), (int(screen_x), int(screen_y)), 16)
                    
                    # Número do checkpoint para jogador 1
                    texto_checkpoint = fonte_checkpoint.render(str(carro1.checkpoint_atual + 1), True, (255, 255, 255))
                    texto_rect = texto_checkpoint.get_rect(center=(int(screen_x), int(screen_y)))
                    superficie_p1.blit(texto_checkpoint, texto_rect)
                
                # Renderizar jogador 2 (lado direito)
                camera_p2.set_alvo(carro2)
                camera_p2.desenhar_fundo(superficie_p2, img_pista)
                
                # Culling para jogador 2
                carros_visiveis_p2 = []
                for carro in carros:
                    if camera_p2.esta_visivel(carro.x, carro.y, 30):
                        carros_visiveis_p2.append(carro)
                
                # Renderizar carros visíveis para jogador 2
                for carro in carros_visiveis_p2:
                    carro.desenhar(superficie_p2, camera=camera_p2)
                
                # Renderizar checkpoints para jogador 2 (lado direito)
                if carro2 is not None and hasattr(carro2, 'checkpoint_atual') and carro2.checkpoint_atual < len(checkpoints):
                    cx2, cy2 = checkpoints[carro2.checkpoint_atual]
                    screen_x2, screen_y2 = camera_p2.mundo_para_tela(cx2, cy2)
                    
                    # Desenhar próximo checkpoint para o jogador 2 (amarelo)
                    pygame.draw.circle(superficie_p2, (255, 255, 0), (int(screen_x2), int(screen_y2)), 20, 4)
                    pygame.draw.circle(superficie_p2, (255, 200, 0), (int(screen_x2), int(screen_y2)), 16)
                    
                    # Número do checkpoint para jogador 2
                    texto_checkpoint2 = fonte_checkpoint.render(str(carro2.checkpoint_atual + 1), True, (0, 0, 0))
                    texto_rect2 = texto_checkpoint2.get_rect(center=(int(screen_x2), int(screen_y2)))
                    superficie_p2.blit(texto_checkpoint2, texto_rect2)
                
                # Desenhar as superfícies na tela principal
                tela.blit(superficie_p1, (0, 0))
                tela.blit(superficie_p2, (metade_largura, 0))
                
                # Desenhar linha divisória
                pygame.draw.line(tela, (255, 255, 255), (metade_largura, 0), (metade_largura, ALTURA), 2)
                
                # Restaurar câmera principal para jogador 1
                camera.set_alvo(carro1)
            else:
                # Modo normal (1 jogador ou drift)
                camera.desenhar_fundo(tela, img_pista)

                # Culling de objetos - só renderizar carros visíveis (otimizado)
                carros_visiveis = []
                for carro in carros:
                    if camera.esta_visivel(carro.x, carro.y, 30):  # Margem reduzida para 30px
                        carros_visiveis.append(carro)
                
                # Renderizar carros visíveis
                for carro in carros_visiveis:
                    carro.desenhar(tela, camera=camera)

        # Debug da IA - só renderizar se necessário
        if renderizar_frame and (debug_IA or mostrar_debug):
            # Só desenhar debug da IA se carro2 for uma IA (modo 1 jogador)
            if modo_jogo != ModoJogo.DOIS_JOGADORES and carro2 is not None:
                IA2.desenhar_debug(tela, camera=camera, mostrar_todos_checkpoints=False)
            if carro3 is not None:
                IA3.desenhar_debug(tela, camera=camera, mostrar_todos_checkpoints=False)          
        
        # Checkpoints - só renderizar se necessário
        if renderizar_frame and checkpoint_manager.modo_edicao:
            checkpoint_manager.desenhar(tela, camera)
        
        # Sistema de checkpoints para o player (apenas se não for modo drift)
        if checkpoints and not checkpoint_manager.modo_edicao and tipo_jogo != TipoJogo.DRIFT:
            # InicIAlizar checkpoint atual do player se não existir
            if not hasattr(carro1, 'checkpoint_atual'):
                carro1.checkpoint_atual = 0
            
            # Verificar se passou pelo checkpoint atual
            if carro1.checkpoint_atual < len(checkpoints):
                cx, cy = checkpoints[carro1.checkpoint_atual]
                dist = math.sqrt((cx - carro1.x)**2 + (cy - carro1.y)**2)
                
                # Detecção múltipla para ser mais responsiva
                passou_checkpoint = False
                
                # Método 1: DistâncIA direta
                if dist < 60:
                    passou_checkpoint = True
                
                # Método 2: Projeção (passou "através" do checkpoint)
                if carro1.checkpoint_atual < len(checkpoints) - 1:
                    proximo_cx, proximo_cy = checkpoints[carro1.checkpoint_atual + 1]
                    vetor_checkpoint = (proximo_cx - cx, proximo_cy - cy)
                    vetor_carro = (carro1.x - cx, carro1.y - cy)
                    
                    produto_escalar = vetor_checkpoint[0] * vetor_carro[0] + vetor_checkpoint[1] * vetor_carro[1]
                    if produto_escalar > 0 and dist < 80:
                        passou_checkpoint = True
                
                # Método 3: Velocidade e direção
                if hasattr(carro1, 'vx') and hasattr(carro1, 'vy'):
                    velocidade = math.sqrt(carro1.vx*carro1.vx + carro1.vy*carro1.vy)
                    if velocidade > 0.5:  # Se estiver se movendo
                        direcao_movimento = (carro1.vx, carro1.vy)
                        direcao_checkpoint = (proximo_cx - carro1.x, proximo_cy - carro1.y) if carro1.checkpoint_atual < len(checkpoints) - 1 else (0, 0)
                        
                        if (math.sqrt(direcao_movimento[0]**2 + direcao_movimento[1]**2) > 0.1 and
                            math.sqrt(direcao_checkpoint[0]**2 + direcao_checkpoint[1]**2) > 0.1):
                            
                            norm_mov = math.sqrt(direcao_movimento[0]**2 + direcao_movimento[1]**2)
                            norm_check = math.sqrt(direcao_checkpoint[0]**2 + direcao_checkpoint[1]**2)
                            
                            cos_angulo = (direcao_movimento[0] * direcao_checkpoint[0] + 
                                         direcao_movimento[1] * direcao_checkpoint[1]) / (norm_mov * norm_check)
                            
                            if cos_angulo > 0.5 and dist < 80:  # Movendo na direção do próximo checkpoint
                                passou_checkpoint = True
                
                if passou_checkpoint:
                    carro1.checkpoint_atual += 1
                    print(f"Player passou pelo checkpoint {carro1.checkpoint_atual}!")
                    
                    # Verificar se terminou todos os checkpoints
                    if carro1.checkpoint_atual >= len(checkpoints):
                        print(f"Player 1 terminou a corrida! Todos os {len(checkpoints)} checkpoints completados!")
                        carro1.checkpoint_atual = len(checkpoints)  # Manter no último checkpoint
                        # Adicionar flag de vitória
                        if not hasattr(carro1, 'terminou_corrida'):
                            carro1.terminou_corrida = True
                
                # Verificar checkpoint para jogador 2 se existir (mesma lógica do jogador 1)
                if modo_jogo == ModoJogo.DOIS_JOGADORES and carro2 is not None:
                    if not hasattr(carro2, 'checkpoint_atual'):
                        carro2.checkpoint_atual = 0
                    
                    if carro2.checkpoint_atual < len(checkpoints):
                        cx2, cy2 = checkpoints[carro2.checkpoint_atual]
                        dist2 = math.sqrt((cx2 - carro2.x)**2 + (cy2 - carro2.y)**2)
                        
                        # Detecção múltipla para ser mais responsiva (mesma lógica do jogador 1)
                        passou_checkpoint2 = False
                        
                        # Método 1: Distância direta
                        if dist2 < 60:
                            passou_checkpoint2 = True
                        
                        # Método 2: Direção e próximo checkpoint
                        if not passou_checkpoint2 and carro2.checkpoint_atual < len(checkpoints) - 1:
                            proximo_cx2, proximo_cy2 = checkpoints[carro2.checkpoint_atual + 1]
                            vetor_checkpoint2 = (proximo_cx2 - cx2, proximo_cy2 - cy2)
                            vetor_carro2 = (carro2.x - cx2, carro2.y - cy2)
                            
                            produto_escalar2 = vetor_checkpoint2[0] * vetor_carro2[0] + vetor_checkpoint2[1] * vetor_carro2[1]
                            if produto_escalar2 > 0 and dist2 < 80:
                                passou_checkpoint2 = True
                        
                        # Método 3: Velocidade e direção
                        if not passou_checkpoint2 and hasattr(carro2, 'vx') and hasattr(carro2, 'vy'):
                            velocidade2 = math.sqrt(carro2.vx*carro2.vx + carro2.vy*carro2.vy)
                            if velocidade2 > 0.5:  # Se estiver se movendo
                                direcao_movimento2 = (carro2.vx, carro2.vy)
                                direcao_checkpoint2 = (proximo_cx2 - carro2.x, proximo_cy2 - carro2.y) if carro2.checkpoint_atual < len(checkpoints) - 1 else (0, 0)
                                
                                if (math.sqrt(direcao_movimento2[0]**2 + direcao_movimento2[1]**2) > 0.1 and
                                    math.sqrt(direcao_checkpoint2[0]**2 + direcao_checkpoint2[1]**2) > 0.1):
                                    
                                    norm_mov2 = math.sqrt(direcao_movimento2[0]**2 + direcao_movimento2[1]**2)
                                    norm_check2 = math.sqrt(direcao_checkpoint2[0]**2 + direcao_checkpoint2[1]**2)
                                    
                                    cos_angulo2 = (direcao_movimento2[0] * direcao_checkpoint2[0] + 
                                                 direcao_movimento2[1] * direcao_checkpoint2[1]) / (norm_mov2 * norm_check2)
                                    
                                    if cos_angulo2 > 0.5 and dist2 < 80:  # Movendo na direção do próximo checkpoint
                                        passou_checkpoint2 = True
                        
                        if passou_checkpoint2:
                            carro2.checkpoint_atual += 1
                            print(f"Player 2 passou pelo checkpoint {carro2.checkpoint_atual}!")
                            
                            # Verificar se terminou todos os checkpoints
                            if carro2.checkpoint_atual >= len(checkpoints):
                                print(f"Player 2 terminou a corrida! Todos os {len(checkpoints)} checkpoints completados!")
                                carro2.checkpoint_atual = len(checkpoints)  # Manter no último checkpoint
                                # Adicionar flag de vitória
                                if not hasattr(carro2, 'terminou_corrida'):
                                    carro2.terminou_corrida = True
            
            # Mostrar próximo checkpoint do player (apenas para modo 1 jogador ou drift)
            if modo_jogo != ModoJogo.DOIS_JOGADORES and hasattr(carro1, 'checkpoint_atual') and carro1.checkpoint_atual < len(checkpoints):
                cx, cy = checkpoints[carro1.checkpoint_atual]
                screen_x, screen_y = camera.mundo_para_tela(cx, cy)
                
                # Desenhar próximo checkpoint para o player (maior)
                pygame.draw.circle(tela, (0, 255, 255), (int(screen_x), int(screen_y)), 20, 4)  # Círculo azul maior
                pygame.draw.circle(tela, (0, 200, 255), (int(screen_x), int(screen_y)), 16)  # Preenchimento maior
                
                # Número do checkpoint (maior) - usar fonte pré-crIAda
                texto_checkpoint = fonte_checkpoint.render(str(carro1.checkpoint_atual + 1), True, (255, 255, 255))
                texto_rect = texto_checkpoint.get_rect(center=(int(screen_x), int(screen_y)))
                tela.blit(texto_checkpoint, texto_rect)

        # Sistema de gravação removido - não usado

        if renderizar_frame:
            # Desenhar HUD personalizado
            if mostrar_hud:
                if modo_jogo == ModoJogo.DOIS_JOGADORES and carro2 is not None:
                    # HUD para modo 2 jogadores - dividir a tela
                    metade_largura = LARGURA // 2
                    
                    # HUD jogador 1 (lado esquerdo)
                    hud.desenhar_hud_completo(tela, carro1)
                    hud.desenhar_minimapa(tela, carro1, checkpoints, camera)
                    
                    # HUD jogador 2 (lado direito)
                    hud.desenhar_hud_completo(tela, carro2)
                    hud.desenhar_minimapa(tela, carro2, checkpoints, camera)
                else:
                    # HUD normal (1 jogador ou drift)
                    hud.desenhar_hud_completo(tela, carro1)
                    # Desenhar minimapa apenas se não for modo drift
                    if tipo_jogo != TipoJogo.DRIFT:
                        hud.desenhar_minimapa(tela, carro1, checkpoints, camera)
                    
                    # Renderizar tempo para modo drift
                    if tipo_jogo == TipoJogo.DRIFT:
                        # Tempo restante
                        minutos = int(tempo_restante // 60)
                        segundos = int(tempo_restante % 60)
                        tempo_texto = f"Tempo: {minutos:02d}:{segundos:02d}"
                        
                        # Cor baseada no tempo restante
                        if tempo_restante > 30:
                            cor_tempo = (255, 255, 255)  # Branco
                        elif tempo_restante > 10:
                            cor_tempo = (255, 255, 0)    # Amarelo
                        else:
                            cor_tempo = (255, 0, 0)      # Vermelho
                        
                        # Renderizar tempo
                        fonte_tempo = pygame.font.Font(None, 48)
                        texto_tempo = fonte_tempo.render(tempo_texto, True, cor_tempo)
                        tela.blit(texto_tempo, (LARGURA - 200, 50))
                    
                    # Renderizar pause
                    if jogo_pausado:
                        fonte_pause = pygame.font.Font(None, 72)
                        texto_pause = fonte_pause.render("PAUSADO", True, (255, 255, 255))
                        texto_pause_rect = texto_pause.get_rect(center=(LARGURA//2, ALTURA//2))
                        tela.blit(texto_pause, texto_pause_rect)
                        
                        fonte_instrucao = pygame.font.Font(None, 36)
                        texto_instrucao = fonte_instrucao.render("Pressione ESC para continuar", True, (200, 200, 200))
                        texto_instrucao_rect = texto_instrucao.get_rect(center=(LARGURA//2, ALTURA//2 + 50))
                        tela.blit(texto_instrucao, texto_instrucao_rect)
                    
                    # Renderizar tela de fim de jogo para drift
                    if jogo_terminado and tipo_jogo == TipoJogo.DRIFT:
                        # Overlay escuro
                        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                        overlay.fill((0, 0, 0, 150))
                        tela.blit(overlay, (0, 0))
                        
                        # Título
                        fonte_titulo = pygame.font.Font(None, 72)
                        texto_titulo = fonte_titulo.render("TEMPO ESGOTADO!", True, (255, 255, 255))
                        texto_titulo_rect = texto_titulo.get_rect(center=(LARGURA//2, ALTURA//2 - 100))
                        tela.blit(texto_titulo, texto_titulo_rect)
                        
                        # Pontuação final
                        fonte_pontuacao = pygame.font.Font(None, 48)
                        texto_pontuacao = fonte_pontuacao.render(f"Pontuação Final: {pontuacao_final}", True, (255, 255, 0))
                        texto_pontuacao_rect = texto_pontuacao.get_rect(center=(LARGURA//2, ALTURA//2 - 20))
                        tela.blit(texto_pontuacao, texto_pontuacao_rect)
                        
                        # Instruções
                        fonte_instrucao = pygame.font.Font(None, 36)
                        texto_instrucao = fonte_instrucao.render("Pressione ESC para voltar ao menu", True, (200, 200, 200))
                        texto_instrucao_rect = texto_instrucao.get_rect(center=(LARGURA//2, ALTURA//2 + 50))
                        tela.blit(texto_instrucao, texto_instrucao_rect)
                
                # Desenhar HUD de drift se estiver no modo drift
                if mostrar_drift_hud and tipo_jogo == TipoJogo.DRIFT:
                    fonte_drift = pygame.font.Font(None, 24)
                    if modo_jogo == ModoJogo.DOIS_JOGADORES and carro2 is not None:
                        # Drift HUD para modo 2 jogadores - dividir a tela
                        metade_largura = LARGURA // 2
                        drift_scoring.draw_hud(tela, 20, 20, fonte_drift)  # Jogador 1
                        # TODO: Implementar drift scoring para jogador 2 se necessário
                    else:
                        # Drift HUD normal (1 jogador)
                        drift_scoring.draw_hud(tela, 20, 20, fonte_drift)
            
            # HUD original removido - usando HUD personalizado

            if mostrar_fps:
                fps_atual = int(relogio.get_fps())
                fps_texto = fonte_small.render(f"FPS: {fps_atual}", True, (255, 255, 255))
                tela.blit(fps_texto, (largura_atual - 100, 10))
                
                # Mostrar estatísticas de cache (debug)
                if mostrar_debug:
                    from core.pista import obter_estatisticas_cache
                    stats = obter_estatisticas_cache()
                    cache_texto = fonte_small.render(f"Cache: {stats['hit_rate']:.1f}% ({stats['cache_size']})", True, (255, 255, 255))
                    tela.blit(cache_texto, (largura_atual - 200, 30))
        
        # Textos de controles removidos para interface mais limpa
        # O editor de checkpoints ainda funciona com as teclas F7, F5, F6, etc.

        if renderizar_frame:
            corrida.desenhar_semaforo(tela, largura_atual, altura_atual)
            if corrida.alguem_finalizou():
                corrida.desenhar_podio(tela, largura_atual, altura_atual, [carro1, carro2, carro3])
            
            # Tela de vitória para modo 2 jogadores
            if modo_jogo == ModoJogo.DOIS_JOGADORES and carro2 is not None:
                vencedor = None
                if hasattr(carro1, 'terminou_corrida') and carro1.terminou_corrida:
                    vencedor = "JOGADOR 1"
                elif hasattr(carro2, 'terminou_corrida') and carro2.terminou_corrida:
                    vencedor = "JOGADOR 2"
                
                if vencedor:
                    # Overlay escuro
                    overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 150))
                    tela.blit(overlay, (0, 0))
                    
                    # Título de vitória
                    fonte_vitoria = pygame.font.Font(None, 72)
                    texto_vitoria = fonte_vitoria.render(f"{vencedor} VENCEU!", True, (255, 215, 0))
                    texto_vitoria_rect = texto_vitoria.get_rect(center=(LARGURA//2, ALTURA//2 - 80))
                    tela.blit(texto_vitoria, texto_vitoria_rect)
                    
                    # Mensagem de que o jogo parou
                    fonte_parou = pygame.font.Font(None, 48)
                    texto_parou = fonte_parou.render("CORRIDA FINALIZADA!", True, (255, 255, 255))
                    texto_parou_rect = texto_parou.get_rect(center=(LARGURA//2, ALTURA//2 - 20))
                    tela.blit(texto_parou, texto_parou_rect)
                    
                    # Instruções
                    fonte_instrucao = pygame.font.Font(None, 36)
                    texto_instrucao = fonte_instrucao.render("Pressione ESC para voltar ao menu", True, (200, 200, 200))
                    texto_instrucao_rect = texto_instrucao.get_rect(center=(LARGURA//2, ALTURA//2 + 50))
                    tela.blit(texto_instrucao, texto_instrucao_rect)


        pygame.display.update()

if __name__ == "__main__":
    from core.menu import run
    run()
