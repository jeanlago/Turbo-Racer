import os
import math
import pygame
from config import (
    LARGURA, ALTURA, FPS, TURBO_P1, TURBO_P2,
    USAR_IA_NO_CARRO_2, CONFIGURACOES,
    MAPAS_DISPONIVEIS, MAPA_ATUAL, obter_caminho_mapa, obter_caminho_guias,
    obter_lista_mapas, CAMINHO_TROFEU_OURO, CAMINHO_TROFEU_PRATA, CAMINHO_TROFEU_BRONZE, CAMINHO_TROFEU_VAZIO
)
from core.pista import (
    carregar_pista, eh_pixel_transitavel, calcular_posicoes_iniciais, extrair_checkpoints
)
from core.checkpoint_manager import CheckpointManager
from core.carro_fisica import CarroFisica
from core.corrida import GerencIAdorCorrida
from core.camera import Camera
from core.ia import IA
from core.musica import gerencIAdor_musica
from core.hud import HUD
from core.game_modes import ModoJogo, TipoJogo
from core.drift_scoring import DriftScoring
from core.progresso import gerenciador_progresso
from config import CAMINHO_MENU

CARROS_DISPONIVEIS = [
    {"nome": "Nissan 350Z", "prefixo_cor": "Car1", "posicao": (570, 145), "sprite_selecao": "Car1", "tipo_tracao": "rear", "tamanho_oficina": (850, 550), "posicao_oficina": (LARGURA//2 - 430, 170), "preco": 0},  # Gratuito (primeiro carro)
    {"nome": "BMW M3 95' ", "prefixo_cor": "Car2", "posicao": (570, 190), "sprite_selecao": "Car2", "tipo_tracao": "rear", "tamanho_oficina": (600, 300), "posicao_oficina": (LARGURA//2 - 300, 380), "preco": 1500},
    {"nome": "Chevrolet Camaro", "prefixo_cor": "Car3", "posicao": (560, 210), "sprite_selecao": "Car3", "tipo_tracao": "rear", "tamanho_oficina": (580, 550), "posicao_oficina": (LARGURA//2 - 320, 200), "preco": 2000},
    {"nome": "Toyota Supra", "prefixo_cor": "Car4", "posicao": (570, 190), "sprite_selecao": "Car4", "tipo_tracao": "rear", "tamanho_oficina": (600, 300), "posicao_oficina": (LARGURA//2 - 300, 380), "preco": 2500},
    {"nome": "Toyota Trueno", "prefixo_cor": "Car5", "posicao": (590, 175), "sprite_selecao": "Car5", "tipo_tracao": "rear", "tamanho_oficina": (600, 300), "posicao_oficina": (LARGURA//2 - 300, 380), "preco": 1800},
    {"nome": "Nissan Skyline", "prefixo_cor": "Car6", "posicao": (550, 200), "sprite_selecao": "Car6", "tipo_tracao": "front", "tamanho_oficina": (900, 650), "posicao_oficina": (LARGURA//2 - 490, 215), "preco": 3000},
    {"nome": "Nissan Silvia S13", "prefixo_cor": "Car7", "posicao": (600, 185), "sprite_selecao": "Car7", "tipo_tracao": "rear", "tamanho_oficina": (600, 300), "posicao_oficina": (LARGURA//2 - 300, 380), "preco": 2200},
    {"nome": "Mazda RX-7", "prefixo_cor": "Car8", "posicao": (540, 220), "sprite_selecao": "Car8", "tipo_tracao": "awd", "tamanho_oficina": (600, 300), "posicao_oficina": (LARGURA//2 - 300, 380), "preco": 3500},
    {"nome": "Toyota Celica", "prefixo_cor": "Car9", "posicao": (610, 195), "sprite_selecao": "Car9", "tipo_tracao": "rear", "tamanho_oficina": (600, 300), "posicao_oficina": (LARGURA//2 - 350, 380), "preco": 2000},
    {"nome": "Volkswagem Fusca", "prefixo_cor": "Car10", "posicao": (530, 240), "sprite_selecao": "Car10", "tipo_tracao": "front", "tamanho_oficina": (750, 550), "posicao_oficina": (LARGURA//2 - 400, 250), "preco": 1200},
    {"nome": "Mitsubishi Lancer", "prefixo_cor": "Car11", "posicao": (620, 205), "sprite_selecao": "Car11", "tipo_tracao": "rear", "tamanho_oficina": (900, 650), "posicao_oficina": (LARGURA//2 - 490, 150), "preco": 2800},
    {"nome": "Porsche 911 77'", "prefixo_cor": "Car12", "posicao": (520, 260), "sprite_selecao": "Car12", "tipo_tracao": "rear", "tamanho_oficina": (900, 650), "posicao_oficina": (LARGURA//2 - 490, 215), "preco": 4000},
]

def principal(carro_selecionado_p1=0, carro_selecionado_p2=1, mapa_selecionado=None, modo_jogo=ModoJogo.UM_JOGADOR, tipo_jogo=TipoJogo.CORRIDA, voltas=1, dificuldade_ia="medio"):
    # Resetar flag de recompensa de drift
    if hasattr(principal, '_recompensa_drift_calculada'):
        delattr(principal, '_recompensa_drift_calculada')
    
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
    else:
        checkpoints = extrair_checkpoints(mask_guias)
        if checkpoints:
            checkpoint_manager.checkpoints = checkpoints
            checkpoint_manager.salvar_checkpoints()
        else:
            checkpoints = [(640, 360)]

    largura_atual, altura_atual = resolucao
    camera = Camera(largura_atual, altura_atual, *img_pista.get_size(), zoom=1.8)  # Zoom inicial mais próximo

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
    
    # Carregar troféus
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
    corrida = GerencIAdorCorrida(fonte, checkpoints, voltas_objetivo)
    
    def obter_posicao_jogador(carro_jogador, todos_carros):
        """Retorna a posição do jogador (1, 2, 3, etc.) baseado nos tempos finais"""
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
        """Retorna o troféu baseado na posição (1=ouro, 2=prata, 3=bronze, outros=vazio)"""
        if posicao == 1:
            return trofeu_ouro
        elif posicao == 2:
            return trofeu_prata
        elif posicao == 3:
            return trofeu_bronze
        else:
            return trofeu_vazio
    
    def obter_trofeu_por_pontuacao(pontuacao):
        """Retorna o troféu baseado na pontuação de drift"""
        if pontuacao >= 50000:  # Alta pontuação = ouro
            return trofeu_ouro
        elif pontuacao >= 20000:  # Média pontuação = prata
            return trofeu_prata
        elif pontuacao >= 5000:  # Baixa pontuação = bronze
            return trofeu_bronze
        else:
            return trofeu_vazio
    
    def processar_tela_fim_jogo(ev, estado):
        """Processa eventos da tela de fim de jogo e retorna ação escolhida"""
        from core.menu import verificar_clique_opcao
        
        if estado is None:
            return None
        
        titulo, subtitulo, trofeu, posicao, pontuacao, recompensa, opcao_atual, hover_animation = estado
        opcoes = [
            ("REINICIAR JOGO", "reiniciar"),
            ("TROCAR CARRO", "trocar_carro"),
            ("MENU PRINCIPAL", "menu")
        ]
        
        # Caixa
        caixa_largura = 500
        caixa_altura = 650
        caixa_x = (LARGURA - caixa_largura) // 2
        caixa_y = (ALTURA - caixa_altura) // 2
        
        # Calcular offset das opções - posicionar no inferior do retângulo
        altura_total_opcoes = 3 * 60  # 3 opções com 60px cada
        offset_opcoes = caixa_y + caixa_altura - altura_total_opcoes - 20  # 20px do fundo
        
        # Processar eventos
        if ev.type == pygame.QUIT:
            return "sair"
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            mouse_x, mouse_y = ev.pos
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
    
    def desenhar_tela_fim_jogo(tela, estado, dt):
        """Desenha o popup de fim de jogo sobre a tela atual"""
        if estado is None:
            return
        
        from core.menu import render_text, verificar_clique_opcao
        
        titulo, subtitulo, trofeu, posicao, pontuacao, recompensa, opcao_atual, hover_animation = estado
        opcoes = [
            ("REINICIAR JOGO", "reiniciar"),
            ("TROCAR CARRO", "trocar_carro"),
            ("MENU PRINCIPAL", "menu")
        ]
        
        # Caixa
        caixa_largura = 500
        caixa_altura = 650
        caixa_x = (LARGURA - caixa_largura) // 2
        caixa_y = (ALTURA - caixa_altura) // 2
        
        # Calcular offset das opções - posicionar no inferior do retângulo
        altura_total_opcoes = 3 * 60  # 3 opções com 60px cada
        offset_opcoes = caixa_y + caixa_altura - altura_total_opcoes - 20  # 20px do fundo
        
        # Overlay escuro sobre o jogo
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        tela.blit(overlay, (0, 0))
        
        # Caixa
        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 200))
        tela.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(tela, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        # Hover
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
        
        # Título
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
        carro3 = CarroFisica(
            pos_inicial_IA[0], pos_inicial_IA[1],
            "Car3",
            (0, 0, 0, 0),
            turbo_key=pygame.K_t,
            nome="IA-1",
            tipo_tracao=CarroFisica.TRACAO_TRASEIRA
        )
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
        camera_p1 = Camera(metade_largura, ALTURA, *img_pista.get_size(), zoom=1.6)
        camera_p2 = Camera(metade_largura, ALTURA, *img_pista.get_size(), zoom=1.6)
        camera_p1.cx = largura_pista // 2
        camera_p1.cy = altura_pista // 2
        camera_p2.cx = largura_pista // 2
        camera_p2.cy = altura_pista // 2

    def is_on_track(x, y):
        return eh_pixel_transitavel(mask_guias, x, y)

    IA2 = IA(checkpoints, nome="IA-1", dificuldade=dificuldade_ia)
    IA3 = IA(checkpoints, nome="IA-2", dificuldade=dificuldade_ia)
    debug_IA = True

    if tipo_jogo == TipoJogo.DRIFT:
        if dificuldade_ia == "facil":
            tempo_drift = 90.0
        elif dificuldade_ia == "dificil":
            tempo_drift = 30.0
        else:
            tempo_drift = 60.0
    else:
        tempo_drift = 60.0
    
    tempo_restante = tempo_drift
    jogo_pausado = False
    jogo_terminado = False
    pontuacao_final = 0
    tela_fim_mostrada = False
    acao_fim_jogo = None
    estado_fim_jogo = None
    
    opcao_pausa_selecionada = 0
    opcoes_pausa = ["Continuar", "Reiniciar", "Voltar ao Menu"]

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
    dt_fixo = 1.0 / 120.0
    acumulador_dt = 0.0
    max_dt = 0.1

    while rodando:
        dt = relogio.tick(fps_max) / 1000.0
        dt = min(dt, max_dt)
        acumulador_dt += dt

        gerencIAdor_musica.verificar_fim_musica()

        for ev in pygame.event.get():
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
                        return
                    elif acao == "menu" or acao == "sair":
                        return
                continue
            
            if ev.type == pygame.QUIT:
                rodando = False

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    if estado_fim_jogo is not None:
                        return
                    elif not jogo_terminado and not alguem_venceu:
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
                
                # Atualizar dificuldade das IAs
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
                    if ev.key == pygame.K_UP:
                        opcao_pausa_selecionada = (opcao_pausa_selecionada - 1) % len(opcoes_pausa)
                    elif ev.key == pygame.K_DOWN:
                        opcao_pausa_selecionada = (opcao_pausa_selecionada + 1) % len(opcoes_pausa)
                    elif ev.key == pygame.K_RETURN or ev.key == pygame.K_SPACE:
                        if opcao_pausa_selecionada == 0:
                            jogo_pausado = False
                        elif opcao_pausa_selecionada == 1:
                            return principal(carro_selecionado_p1, carro_selecionado_p2, mapa_selecionado, modo_jogo, tipo_jogo, voltas)
                        elif opcao_pausa_selecionada == 2:
                            return

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

        if not corrida.inicIAda:
            corrida.atualizar_contagem(dt)
        corrida.atualizar_tempo(dt)

        if tipo_jogo == TipoJogo.DRIFT and not jogo_pausado and not jogo_terminado and corrida.inicIAda:
            tempo_restante -= dt
            if tempo_restante <= 0:
                tempo_restante = 0
                jogo_terminado = True
                pontuacao_final = drift_scoring.points

        alguem_venceu = corrida.alguem_finalizou() if tipo_jogo != TipoJogo.DRIFT else False

        while acumulador_dt >= dt_fixo:
            if corrida.pode_controlar() and not jogo_pausado and estado_fim_jogo is None:
                carro1.atualizar(teclas, mask_guias, dt_fixo, camera)

                if carro2 is not None:
                    if modo_jogo == ModoJogo.DOIS_JOGADORES:
                        carro2.atualizar(teclas, mask_guias, dt_fixo, camera)
                    elif USAR_IA_NO_CARRO_2 and not alguem_venceu:
                        IA2.controlar(carro2, mask_guias, is_on_track, dt_fixo)
                    else:
                        carro2.atualizar(teclas, mask_guias, dt_fixo, camera)

                if carro3 is not None and not alguem_venceu:
                    IA3.controlar(carro3, mask_guias, is_on_track, dt_fixo)

                if len(carros) <= 3 and tipo_jogo != TipoJogo.DRIFT:
                    for c in carros:
                        corrida.atualizar_progresso_carro(c)

                if tipo_jogo == TipoJogo.DRIFT:
                    vlong, vlat = carro1._mundo_para_local(carro1.vx, carro1.vy)
                    velocidade_kmh = abs(vlong) * 0.5
                    angulo_drift = abs(math.degrees(math.atan2(vlat, max(0.1, abs(vlong)))))
                    drift_ativado = getattr(carro1, 'drift_ativado', False)
                    derrapando = getattr(carro1, 'drifting', False)
                    has_skidmarks = derrapando and getattr(carro1, 'drift_intensidade', 0) > 0.05

                    drift_scoring.update(
                        dt_fixo,
                        angulo_drift,
                        velocidade_kmh,
                        carro1.x,
                        carro1.y,
                        drift_ativado,
                        derrapando,
                        collision_force=0.0,
                        has_skidmarks=has_skidmarks
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
                camera.zoom += (zoom - camera.zoom) * dt * 2.0
                offset_y = (1.0 - camera.zoom) * 60
                camera.cy += (carro1.y + offset_y - camera.cy) * dt * 2.5
                camera.cx += (carro1.x - camera.cx) * dt * 3.0

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
            carros_visiveis_p1 = [carro for carro in carros if camera_p1.esta_visivel(carro.x, carro.y, 30)]
            for carro in carros_visiveis_p1:
                carro.desenhar(superficie_p1, camera=camera_p1)
            checkpoint_atual_p1 = corrida.proximo_checkpoint.get(carro1, 0) 
            if not corrida.finalizou.get(carro1, False) and checkpoints and tipo_jogo != TipoJogo.DRIFT:
                idx_cp = checkpoint_atual_p1 % len(checkpoints)
                cx, cy = checkpoints[idx_cp]
                screen_x, screen_y = camera_p1.mundo_para_tela(cx, cy)
                pygame.draw.circle(superficie_p1, (0, 255, 255), (int(screen_x), int(screen_y)), 20, 4)
                pygame.draw.circle(superficie_p1, (0, 200, 255), (int(screen_x), int(screen_y)), 16)
                texto_checkpoint = fonte_checkpoint.render(str(idx_cp + 1), True, (255, 255, 255))
                texto_rect = texto_checkpoint.get_rect(center=(int(screen_x), int(screen_y)))
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
            if carro2:
                carro2.skidmarks.desenhar(superficie_p2, camera_p2)
            carros_visiveis_p2 = [carro for carro in carros if camera_p2.esta_visivel(carro.x, carro.y, 30)]
            for carro in carros_visiveis_p2:
                carro.desenhar(superficie_p2, camera=camera_p2)
            checkpoint_atual_p2 = corrida.proximo_checkpoint.get(carro2, 0)
            if not corrida.finalizou.get(carro2, False) and checkpoints and tipo_jogo != TipoJogo.DRIFT:
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
            camera.desenhar_fundo(tela, img_pista)
            carro1.skidmarks.desenhar(tela, camera)
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
            if modo_jogo != ModoJogo.DOIS_JOGADORES and carro2 is not None:
                IA2.desenhar_debug(tela, camera=camera, mostrar_todos_checkpoints=False)
            if carro3 is not None:
                IA3.desenhar_debug(tela, camera=camera, mostrar_todos_checkpoints=False)

        if checkpoint_manager.modo_edicao:
            checkpoint_manager.desenhar(tela, camera)

        if checkpoints and not checkpoint_manager.modo_edicao and tipo_jogo != TipoJogo.DRIFT:
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

        if mostrar_hud:
            if modo_jogo == ModoJogo.DOIS_JOGADORES and carro2 is not None:
                hud.desenhar_hud_completo(tela, carro1)
                hud.desenhar_hud_completo(tela, carro2)
            else:
                hud.desenhar_hud_completo(tela, carro1)

            if tipo_jogo == TipoJogo.DRIFT:
                minutos = int(tempo_restante // 60)
                segundos = int(tempo_restante % 60)
                tempo_texto = f"{minutos:02d}:{segundos:02d}"
                
                if tempo_restante > 30:
                    cor_tempo = (255, 255, 255)
                    cor_fundo = (0, 0, 0, 100)
                elif tempo_restante > 10:
                    cor_tempo = (255, 255, 0)
                    cor_fundo = (100, 100, 0, 120)
                else:
                    cor_tempo = (255, 0, 0)
                    cor_fundo = (100, 0, 0, 120)
                
                if not hasattr(principal, '_fonte_tempo_cache'):
                    principal._fonte_tempo_cache = pygame.font.Font(None, 64)
                    principal._texto_tempo_cache = None
                    principal._tempo_texto_cache = None
                
                if principal._tempo_texto_cache != tempo_texto:
                    principal._texto_tempo_cache = principal._fonte_tempo_cache.render(tempo_texto, True, cor_tempo)
                    principal._tempo_texto_cache = tempo_texto
                
                texto_tempo = principal._texto_tempo_cache
                
                timer_width = texto_tempo.get_width() + 40
                timer_height = texto_tempo.get_height() + 20
                timer_x = (LARGURA - timer_width) // 2
                timer_y = 20
                
                timer_surface = pygame.Surface((timer_width, timer_height), pygame.SRCALPHA)
                pygame.draw.rect(timer_surface, cor_fundo, (0, 0, timer_width, timer_height), border_radius=15)
                pygame.draw.rect(timer_surface, (255, 255, 255, 30), (0, 0, timer_width, timer_height), 2, border_radius=15)
                
                blur_surface = pygame.Surface((timer_width, timer_height), pygame.SRCALPHA)
                pygame.draw.rect(blur_surface, (255, 255, 255, 20), (0, 0, timer_width, timer_height), border_radius=15)
                timer_surface.blit(blur_surface, (0, 0), special_flags=pygame.BLEND_ADD)
                
                tela.blit(timer_surface, (timer_x, timer_y))
                texto_rect = texto_tempo.get_rect(center=(LARGURA//2, timer_y + timer_height//2))
                tela.blit(texto_tempo, texto_rect)

            if jogo_pausado:
                if not hasattr(principal, '_fonte_pause_cache'):
                    principal._fonte_pause_cache = pygame.font.Font(None, 72)
                    principal._fonte_instrucao_cache = pygame.font.Font(None, 36)
                    principal._texto_pause_cache = principal._fonte_pause_cache.render("PAUSADO", True, (255, 255, 255))
                    principal._texto_instrucao_cache = principal._fonte_instrucao_cache.render("Pressione ESC para continuar", True, (200, 200, 200))
                
                texto_pause_rect = principal._texto_pause_cache.get_rect(center=(LARGURA//2, ALTURA//2))
                tela.blit(principal._texto_pause_cache, texto_pause_rect)
                texto_instrucao_rect = principal._texto_instrucao_cache.get_rect(center=(LARGURA//2, ALTURA//2 + 50))
                tela.blit(principal._texto_instrucao_cache, texto_instrucao_rect)

            if jogo_terminado and tipo_jogo == TipoJogo.DRIFT and not tela_fim_mostrada:
                if not hasattr(principal, '_recompensa_drift_calculada'):
                    recompensa_drift = int(pontuacao_final / 100)
                    gerenciador_progresso.adicionar_dinheiro(recompensa_drift)
                    principal._recompensa_drift_calculada = recompensa_drift
                else:
                    recompensa_drift = principal._recompensa_drift_calculada
                
                tela_fim_mostrada = True
                trofeu_drift = obter_trofeu_por_pontuacao(pontuacao_final)
                
                estado_fim_jogo = [
                    "TEMPO ESGOTADO!",
                    "DRIFT FINALIZADO!",
                    trofeu_drift,
                    None,  # posicao
                    pontuacao_final,
                    recompensa_drift,
                    0,
                    [0.0, 0.0, 0.0]
                ]

            if mostrar_drift_hud and tipo_jogo == TipoJogo.DRIFT:
                fonte_drift = pygame.font.Font(None, 24)
                hud_x = LARGURA - 250
                hud_y = 20
                drift_scoring.draw_hud(tela, hud_x, hud_y, fonte_drift)

        corrida.desenhar_semaforo(tela, largura_atual, altura_atual)
        
        if estado_fim_jogo is not None:
            desenhar_tela_fim_jogo(tela, estado_fim_jogo, dt)

        if modo_jogo == ModoJogo.DOIS_JOGADORES and carro2 is not None and alguem_venceu and not tela_fim_mostrada:
            vencedor = None
            posicao_p1 = None
            posicao_p2 = None
            if corrida.finalizou.get(carro1, False):
                vencedor = "JOGADOR 1"
            elif corrida.finalizou.get(carro2, False):
                vencedor = "JOGADOR 2"
            
            todos_carros = [c for c in carros if c is not None]
            posicao_p1 = obter_posicao_jogador(carro1, todos_carros)
            posicao_p2 = obter_posicao_jogador(carro2, todos_carros)
            
            if vencedor:
                tela_fim_mostrada = True
                trofeu_vencedor = trofeu_vazio
                if vencedor == "JOGADOR 1" and posicao_p1:
                    trofeu_vencedor = obter_trofeu_por_posicao(posicao_p1)
                elif vencedor == "JOGADOR 2" and posicao_p2:
                    trofeu_vencedor = obter_trofeu_por_posicao(posicao_p2)
                
                estado_fim_jogo = [
                    f"{vencedor} VENCEU!",
                    "CORRIDA FINALIZADA!",
                    trofeu_vencedor,
                    posicao_p1 if vencedor == "JOGADOR 1" else posicao_p2,
                    None,
                    None,
                    0,
                    [0.0, 0.0, 0.0]
                ]

        elif modo_jogo != ModoJogo.DOIS_JOGADORES and alguem_venceu and tipo_jogo != TipoJogo.DRIFT and not tela_fim_mostrada:
            vencedor = None
            recompensa_dinheiro = 0
            posicao_jogador = None
            if corrida.finalizou.get(carro1, False):
                vencedor = "JOGADOR VENCEU!"
                recompensa_base = 500
                if dificuldade_ia == "facil":
                    recompensa_dinheiro = recompensa_base
                elif dificuldade_ia == "medio":
                    recompensa_dinheiro = int(recompensa_base * 1.5)
                else:
                    recompensa_dinheiro = int(recompensa_base * 2.0)
                gerenciador_progresso.adicionar_dinheiro(recompensa_dinheiro)
                todos_carros = [c for c in carros if c is not None]
                posicao_jogador = obter_posicao_jogador(carro1, todos_carros)
            elif carro3 and corrida.finalizou.get(carro3, False):
                vencedor = "IA VENCEU!"
                recompensa_dinheiro = 100
                gerenciador_progresso.adicionar_dinheiro(recompensa_dinheiro)
                todos_carros = [c for c in carros if c is not None]
                posicao_jogador = obter_posicao_jogador(carro1, todos_carros)
            if vencedor:
                tela_fim_mostrada = True
                trofeu = obter_trofeu_por_posicao(posicao_jogador) if posicao_jogador else trofeu_vazio
                
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
            if not hasattr(principal, '_overlay_pausa_cache'):
                principal._overlay_pausa_cache = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                principal._overlay_pausa_cache.fill((0, 0, 0, 180))
                principal._fonte_titulo_pausa_cache = pygame.font.Font(None, 72)
                principal._fonte_opcoes_pausa_cache = pygame.font.Font(None, 48)
                principal._fonte_instrucoes_pausa_cache = pygame.font.Font(None, 24)
                principal._texto_titulo_pausa_cache = principal._fonte_titulo_pausa_cache.render("JOGO PAUSADO", True, (255, 255, 255))
                principal._texto_instrucoes_pausa_cache = principal._fonte_instrucoes_pausa_cache.render("Use ↑↓ para navegar, ENTER/SPACE para selecionar", True, (200, 200, 200))
                principal._textos_opcoes_cache = {}
            
            tela.blit(principal._overlay_pausa_cache, (0, 0))
            texto_titulo_rect = principal._texto_titulo_pausa_cache.get_rect(center=(LARGURA//2, ALTURA//2 - 150))
            tela.blit(principal._texto_titulo_pausa_cache, texto_titulo_rect)
            
            for i, opcao in enumerate(opcoes_pausa):
                cor = (255, 255, 255) if i == opcao_pausa_selecionada else (150, 150, 150)
                seta = "► " if i == opcao_pausa_selecionada else "  "
                cache_key = (i, opcao, cor)
                
                if cache_key not in principal._textos_opcoes_cache:
                    principal._textos_opcoes_cache[cache_key] = principal._fonte_opcoes_pausa_cache.render(seta + opcao, True, cor)
                
                texto_opcao = principal._textos_opcoes_cache[cache_key]
                texto_opcao_rect = texto_opcao.get_rect(center=(LARGURA//2, ALTURA//2 - 50 + i * 60))
                tela.blit(texto_opcao, texto_opcao_rect)
            
            texto_instrucoes_rect = principal._texto_instrucoes_pausa_cache.get_rect(center=(LARGURA//2, ALTURA//2 + 150))
            tela.blit(principal._texto_instrucoes_pausa_cache, texto_instrucoes_rect)

        pygame.display.update()

if __name__ == "__main__":
    from core.menu import run
    run()
