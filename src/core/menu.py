import os
import pygame
from enum import Enum
from config import LARGURA, ALTURA, FPS, CAMINHO_MENU, CONFIGURACOES, MAPAS_DISPONIVEIS
import main
from core.musica import gerenciador_musica
from core.popup_musica import popup_musica

def scale_to_cover(img_surf, target_w, target_h):
    iw, ih = img_surf.get_size()
    scale = max(target_w/iw, target_h/ih)
    surf = pygame.transform.smoothscale(img_surf, (int(iw*scale), int(ih*scale)))
    x = (surf.get_width() - target_w) // 2
    y = (surf.get_height() - target_h) // 2
    return surf.subsurface((x, y, target_w, target_h)).copy()

def render_text(text, size, color=(255,255,255), bold=True):
    pygame.font.init()
    font = pygame.font.SysFont("arial", size, bold=bold)
    return font.render(text, True, color)

class Escolha(Enum):
    JOGAR = 0
    SELECIONAR_CARROS = 1
    SELECIONAR_MAPAS = 2
    OPCOES = 3
    SAIR = 4

def menu_loop(screen) -> Escolha:
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)

    itens = ["JOGAR", "SELECIONAR CARROS", "SELECIONAR MAPAS", "OPÇÕES", "SAIR"]
    idx = 0
    clock = pygame.time.Clock()

    # posições do texto (coluna esquerda)
    base_x = int(LARGURA * 0.10)
    base_y = int(ALTURA * 0.30)
    passo = 70

    while True:
        dt = clock.tick(FPS) / 1000.0  # Converter para segundos
        
        # Atualizar música
        gerenciador_musica.verificar_fim_musica()
        popup_musica.atualizar(dt)
        
        # Verificar hover do pop-up
        mouse_x, mouse_y = pygame.mouse.get_pos()
        popup_musica.verificar_hover(mouse_x, mouse_y)
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return Escolha.SAIR
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_UP, pygame.K_w):
                    idx = (idx - 1) % len(itens)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    idx = (idx + 1) % len(itens)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return Escolha(idx)
                elif ev.key == pygame.K_ESCAPE:
                    return Escolha.SAIR
                elif ev.key == pygame.K_m:
                    # Alternar música
                    if gerenciador_musica.musica_tocando:
                        gerenciador_musica.parar_musica()
                    else:
                        gerenciador_musica.tocar_musica()
                elif ev.key == pygame.K_n:
                    # Próxima música
                    gerenciador_musica.proxima_musica()
                    if gerenciador_musica.musica_tocando:
                        popup_musica.mostrar(gerenciador_musica.obter_nome_musica_atual())
            if ev.type == pygame.MOUSEMOTION:
                mx, my = ev.pos
                # detecta hover do mouse nas opções
                for i in range(len(itens)):
                    tx = base_x
                    ty = base_y + i*passo
                    rect = pygame.Rect(tx, ty-10, 380, 50)
                    if rect.collidepoint(mx, my):
                        idx = i
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # Verificar clique no pop-up de música
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
                    return Escolha(idx)

        # desenha
        screen.blit(bg, (0, 0))

        # leve faixa escura à esquerda p/ legibilidade (não altera sua imagem)
        overlay = pygame.Surface((int(LARGURA*0.42), ALTURA), pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 150))
        screen.blit(overlay, (0, 0))

        # título
        screen.blit(render_text("TURBO RACER", 56, (0,255,230)), (base_x, base_y-90))

        # itens
        for i, txt in enumerate(itens):
            sel = (i == idx)
            color = (255, 220, 150) if sel else (230, 240, 255)
            surf = render_text(txt, 36, color)
            x = base_x
            y = base_y + i*passo
            screen.blit(surf, (x, y))
            if sel:
                # brilho simples sob a opção ativa
                underline = pygame.Surface((surf.get_width(), 4), pygame.SRCALPHA)
                underline.fill((255, 180, 60, 180))
                screen.blit(underline, (x, y + surf.get_height() + 6))

        # Desenhar pop-up de música
        popup_musica.desenhar(screen)
        
        pygame.display.flip()

def selecionar_mapas_loop(screen):
    bg_raw = pygame.image.load(CAMINHO_MENU).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)
    
    mapas = list(MAPAS_DISPONIVEIS.keys())
    indice = 0
    relogio = pygame.time.Clock()
    
    base_x = int(LARGURA * 0.10)
    base_y = int(ALTURA * 0.30)
    passo = 60
    
    while True:
        dt = relogio.tick(FPS) / 1000.0
        
        gerenciador_musica.verificar_fim_musica()
        popup_musica.atualizar(dt)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
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
                    if gerenciador_musica.musica_tocando:
                        gerenciador_musica.parar_musica()
                    else:
                        gerenciador_musica.tocar_musica()
        
        screen.blit(bg, (0, 0))
        
        titulo = render_text("SELECIONAR MAPA", 48, (255, 255, 0))
        screen.blit(titulo, (base_x, base_y - 80))
        
        for i, mapa_id in enumerate(mapas):
            mapa_info = MAPAS_DISPONIVEIS[mapa_id]
            nome_mapa = mapa_info["nome"]
            
            if i == indice:
                cor = (255, 255, 0)
                tamanho = 36
            else:
                cor = (255, 255, 255)
                tamanho = 32
            
            texto = render_text(nome_mapa, tamanho, cor)
            screen.blit(texto, (base_x, base_y + i * passo))
        
        instrucoes = [
            "↑ ↓: Navegar",
            "ENTER: Selecionar",
            "ESC: Voltar",
            "M: Alternar música"
        ]
        
        for i, instrucao in enumerate(instrucoes):
            texto_instrucao = render_text(instrucao, 20, (200, 200, 200), bold=False)
            screen.blit(texto_instrucao, (base_x, ALTURA - 120 + i * 25))
        
        popup_musica.desenhar(screen)
        
        pygame.display.flip()

def selecionar_carros_loop(screen):
    from config import CAMINHO_OFICINA, DIR_SPRITES, DIR_CAR_SELECTION
    bg_raw = pygame.image.load(CAMINHO_OFICINA).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)
    
    # Importar a lista de carros do main
    from main import CARROS_DISPONIVEIS
    
    carro_p1 = 0
    carro_p2 = 0
    fase_selecao = 1  # 1 = P1 selecionando, 2 = P2 selecionando, 3 = confirmando
    
    # Variáveis para transição
    transicao_ativa = False
    transicao_tempo = 0.0
    transicao_duracao = 0.8  # 800ms - mais lenta
    transicao_direcao = 1  # 1 = direita para esquerda, -1 = esquerda para direita
    carro_atual_pos = 0.0  # Posição X do carro atual (0 = centro)
    carro_proximo_pos = 1.0  # Posição X do próximo carro (1 = fora da tela direita)
    carro_anterior = None  # Carro que estava sendo exibido antes da transição
    
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
            # Redimensionar sprite para exibição grande (ocupando bastante da tela)
            # Padronizar tamanho: manter proporção e centralizar em canvas fixo
            sprite_original = sprite
            # Calcular escala para manter proporção
            escala_x = 900 / sprite_original.get_width()
            escala_y = 650 / sprite_original.get_height()
            escala = min(escala_x, escala_y)  # Usar a menor escala para manter proporção
            
            # Redimensionar mantendo proporção
            nova_largura = int(sprite_original.get_width() * escala)
            nova_altura = int(sprite_original.get_height() * escala)
            sprite_redimensionado = pygame.transform.scale(sprite_original, (nova_largura, nova_altura))
            
            # Criar canvas fixo de 900x650
            sprite = pygame.Surface((900, 650), pygame.SRCALPHA)
            # Centralizar o sprite redimensionado no canvas
            x_offset = (900 - nova_largura) // 2
            y_offset = (650 - nova_altura) // 2
            sprite.blit(sprite_redimensionado, (x_offset, y_offset))
            
            sprites_carros[carro['prefixo_cor']] = sprite
        except:
            # Se não conseguir carregar, criar um retângulo como fallback
            sprite = pygame.Surface((900, 650), pygame.SRCALPHA)
            pygame.draw.rect(sprite, (100, 100, 100), (0, 0, 900, 650))
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
            # Interpolação suave (ease-in-out)
            progresso = transicao_tempo / transicao_duracao
            # Ease-in-out cubic para movimento mais natural
            if progresso < 0.5:
                progresso = 4 * progresso * progresso * progresso
            else:
                progresso = 1 - pow(-2 * progresso + 2, 3) / 2
            
            # Carro atual sai pela direção oposta
            carro_atual_pos = -transicao_direcao * progresso
            # Próximo carro entra pela direção oposta
            carro_proximo_pos = transicao_direcao * (1 - progresso)
    
    clock = pygame.time.Clock()
    
    while True:
        dt = clock.tick(FPS) / 1000.0  # Converter para segundos
        
        # Atualizar transição
        atualizar_transicao(dt)
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return None, None
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return None, None
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    if not transicao_ativa:  # Só permite navegação se não estiver em transição
                        if fase_selecao == 1:
                            iniciar_transicao(-1, carro_p1)  # Esquerda para direita
                            carro_p1 = (carro_p1 - 1) % len(CARROS_DISPONIVEIS)
                        elif fase_selecao == 2:
                            iniciar_transicao(-1, carro_p2)  # Esquerda para direita
                            carro_p2 = (carro_p2 - 1) % len(CARROS_DISPONIVEIS)
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    if not transicao_ativa:  # Só permite navegação se não estiver em transição
                        if fase_selecao == 1:
                            iniciar_transicao(1, carro_p1)  # Direita para esquerda
                            carro_p1 = (carro_p1 + 1) % len(CARROS_DISPONIVEIS)
                        elif fase_selecao == 2:
                            iniciar_transicao(1, carro_p2)  # Direita para esquerda
                            carro_p2 = (carro_p2 + 1) % len(CARROS_DISPONIVEIS)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if not transicao_ativa:  # Só permite confirmação se não estiver em transição
                        if fase_selecao == 1:
                            fase_selecao = 2  # P1 confirmou, vai para P2
                        elif fase_selecao == 2:
                            return carro_p1, carro_p2  # P2 confirmou, retorna seleções
        
        # Desenhar
        screen.blit(bg, (0, 0))
        
        # Overlay escuro sutil
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        screen.blit(overlay, (0, 0))
        
        # Título
        screen.blit(render_text("OFICINA", 36, (0,255,230)), (LARGURA//2 - 250, 20))
        
        if fase_selecao == 1:
            # FASE 1: Player 1 selecionando
            screen.blit(render_text("JOGADOR 1 - ESCOLHA SEU CARRO", 28, (255, 180, 60)), (LARGURA//2 - 120, 50))
            
            # Instruções
            screen.blit(render_text("← → navegar | ENTER confirmar | ESC voltar", 18, (200, 200, 200)), (LARGURA//2 - 100, 60))
            
            # Carro selecionado P1 - Grande e centralizado
            if transicao_ativa:
                # Durante transição: desenhar carro anterior saindo e novo carro entrando
                carro_anterior_obj = CARROS_DISPONIVEIS[carro_anterior]
                carro_atual_obj = CARROS_DISPONIVEIS[carro_p1]
                sprite_anterior = sprites_carros[carro_anterior_obj['prefixo_cor']]
                sprite_atual = sprites_carros[carro_atual_obj['prefixo_cor']]
                
                # Calcular posições
                pos_x_anterior = LARGURA//2 - 500 + int(carro_atual_pos * LARGURA)
                pos_x_atual = LARGURA//2 - 500 + int(carro_proximo_pos * LARGURA)
                
                # Desenhar carro anterior saindo
                screen.blit(sprite_anterior, (pos_x_anterior, 135))
                # Desenhar novo carro entrando
                screen.blit(sprite_atual, (pos_x_atual, 135))
            else:
                # Sem transição: desenhar carro atual normalmente
                carro_atual = CARROS_DISPONIVEIS[carro_p1]
                sprite_atual = sprites_carros[carro_atual['prefixo_cor']]
                screen.blit(sprite_atual, (LARGURA//2 - 500, 135))
            
            # Nome do carro (abaixo do carro)
            screen.blit(render_text(carro_atual['nome'], 36, (255, 255, 255)), (LARGURA//2 - 100, 800))
            
            
            # Botão confirmar
            screen.blit(render_text("ENTER - CONFIRMAR CARRO", 24, (0, 255, 0)), (LARGURA//2 - 120, 840))
            
        elif fase_selecao == 2:
            # FASE 2: Player 2 selecionando
            screen.blit(render_text("JOGADOR 2 - ESCOLHA SEU CARRO", 28, (255, 180, 60)), (LARGURA//2 - 120, 50))
            
            # Mostrar carro do P1 já selecionado (pequeno, no canto)
            carro_p1_selecionado = CARROS_DISPONIVEIS[carro_p1]
            sprite_p1 = pygame.transform.scale(sprites_carros[carro_p1_selecionado['prefixo_cor']], (120, 80))
            screen.blit(render_text("P1:", 20, (255, 255, 255)), (50, 100))
            screen.blit(sprite_p1, (50, 120))
            screen.blit(render_text(carro_p1_selecionado['nome'], 16, (255, 255, 255)), (50, 210))
            
            # Instruções
            screen.blit(render_text("← → navegar | ENTER confirmar | ESC voltar", 18, (200, 200, 200)), (LARGURA//2 - 180, 60))
            
            # Carro selecionado P2 - Grande e centralizado
            if transicao_ativa:
                # Durante transição: desenhar carro anterior saindo e novo carro entrando
                carro_anterior_obj = CARROS_DISPONIVEIS[carro_anterior]
                carro_atual_obj = CARROS_DISPONIVEIS[carro_p2]
                sprite_anterior = sprites_carros[carro_anterior_obj['prefixo_cor']]
                sprite_atual = sprites_carros[carro_atual_obj['prefixo_cor']]
                
                # Calcular posições
                pos_x_anterior = LARGURA//2 - 500 + int(carro_atual_pos * LARGURA)
                pos_x_atual = LARGURA//2 - 500 + int(carro_proximo_pos * LARGURA)
                
                # Desenhar carro anterior saindo
                screen.blit(sprite_anterior, (pos_x_anterior, 135))
                # Desenhar novo carro entrando
                screen.blit(sprite_atual, (pos_x_atual, 135))
            else:
                # Sem transição: desenhar carro atual normalmente
                carro_atual = CARROS_DISPONIVEIS[carro_p2]
                sprite_atual = sprites_carros[carro_atual['prefixo_cor']]
                screen.blit(sprite_atual, (LARGURA//2 - 500, 135))
            
            # Nome do carro (abaixo do carro)
            screen.blit(render_text(carro_atual['nome'], 36, (255, 255, 255)), (LARGURA//2 - 100, 800))
            
            
            # Botão confirmar
            screen.blit(render_text("ENTER - CONFIRMAR CARRO", 24, (0, 255, 0)), (LARGURA//2 - 120, 840))
        
        pygame.display.flip()

def opcoes_loop(screen):
    """Tela de opções do jogo com navegação melhorada"""
    from config import CAMINHO_OFICINA, CONFIGURACOES, salvar_configuracoes
    bg_raw = pygame.image.load(CAMINHO_OFICINA).convert_alpha()
    bg = scale_to_cover(bg_raw, LARGURA, ALTURA)
    
    # Categorias de opções
    categorias = ["AUDIO", "VIDEO", "CONTROLES", "JOGO"]
    categoria_atual = 0
    opcao_atual = 0
    
    # Opções por categoria
    opcoes_categorias = {
        "AUDIO": [
            ("Volume Master", "audio", "volume_master", 0.0, 1.0, 0.1),
            ("Volume Música", "audio", "volume_musica", 0.0, 1.0, 0.1),
            ("Volume Efeitos", "audio", "volume_efeitos", 0.0, 1.0, 0.1),
            ("Áudio Habilitado", "audio", "audio_habilitado", 0, 1, 1),
            ("Música Habilitada", "audio", "musica_habilitada", 0, 1, 1),
            ("Música no Menu", "audio", "musica_no_menu", 0, 1, 1),
            ("Música no Jogo", "audio", "musica_no_jogo", 0, 1, 1),
            ("Música Aleatória", "audio", "musica_aleatoria", 0, 1, 1)
        ],
        "VIDEO": [
            ("Fullscreen", "video", "fullscreen", 0, 1, 1),
            ("Tela Cheia Sem Bordas", "video", "tela_cheia_sem_bordas", 0, 1, 1),
            ("Qualidade Alta", "video", "qualidade_alta", 0, 1, 1),
            ("VSync", "video", "vsync", 0, 1, 1),
            ("FPS Máximo", "video", "fps_max", 30, 120, 30)
        ],
        "CONTROLES": [
            ("Sensibilidade", "controles", "sensibilidade_volante", 0.1, 2.0, 0.1),
            ("Inverter Volante", "controles", "inverter_volante", 0, 1, 1),
            ("Auto Centro", "controles", "auto_centro", 0, 1, 1)
        ],
        "JOGO": [
            ("Dificuldade IA", "jogo", "dificuldade_ia", 0.1, 2.0, 0.1),
            ("Modo Drift", "jogo", "modo_drift", 0, 1, 1),
            ("Mostrar FPS", "jogo", "mostrar_fps", 0, 1, 1),
            ("Mostrar Debug", "jogo", "mostrar_debug", 0, 1, 1)
        ]
    }
    
    clock = pygame.time.Clock()
    
    while True:
        dt = clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            elif ev.type == pygame.MOUSEMOTION:
                # Detectar hover do mouse nas opções
                mouse_x, mouse_y = ev.pos
                opcoes = opcoes_categorias[categorias[categoria_atual]]
                for i, (nome, cat, chave, min_val, max_val, step) in enumerate(opcoes):
                    y_opc = 180
                    opcao_rect = pygame.Rect(50, y_opc + i * 45 - 5, LARGURA - 100, 40)
                    if opcao_rect.collidepoint(mouse_x, mouse_y):
                        opcao_atual = i
                        break
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1:  # Botão esquerdo
                    mouse_x, mouse_y = ev.pos
                    
                    # Verificar se clicou nos botões de ação
                    botao_aplicar_rect = pygame.Rect(LARGURA - 200, ALTURA - 120, 150, 40)
                    botao_sair_rect = pygame.Rect(50, ALTURA - 120, 150, 40)
                    
                    if botao_aplicar_rect.collidepoint(mouse_x, mouse_y):
                        # Aplicar configurações
                        salvar_configuracoes()
                        return True
                    elif botao_sair_rect.collidepoint(mouse_x, mouse_y):
                        # Sair sem salvar
                        return True
                    
                    # Verificar se clicou em uma opção
                    opcoes = opcoes_categorias[categorias[categoria_atual]]
                    for i, (nome, cat, chave, min_val, max_val, step) in enumerate(opcoes):
                        y_opc = 180
                        opcao_rect = pygame.Rect(50, y_opc + i * 45 - 5, LARGURA - 100, 40)
                        if opcao_rect.collidepoint(mouse_x, mouse_y):
                            opcao_atual = i
                            # Alternar valor se for booleano
                            valor_atual = CONFIGURACOES[cat][chave]
                            if isinstance(valor_atual, bool):
                                CONFIGURACOES[cat][chave] = not valor_atual
                            break
                    
                    # Verificar se clicou nas categorias
                    cat_x = 50
                    cat_y = ALTURA - 120
                    for i, cat in enumerate(categorias):
                        cat_rect = pygame.Rect(cat_x + i * 120, cat_y + 25, 100, 25)
                        if cat_rect.collidepoint(mouse_x, mouse_y):
                            categoria_atual = i
                            opcao_atual = 0
                            break
            elif ev.type == pygame.MOUSEBUTTONUP:
                if ev.button == 1:  # Botão esquerdo solto
                    # Finalizar arrasto de barra de progresso
                    pass
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    salvar_configuracoes()
                    return True
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    # Navegar entre opções da categoria atual
                    if opcao_atual > 0:
                        opcao_atual -= 1
                    else:
                        # Se estiver na primeira opção, vai para a última
                        opcao_atual = len(opcoes_categorias[categorias[categoria_atual]]) - 1
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    # Navegar entre opções da categoria atual
                    if opcao_atual < len(opcoes_categorias[categorias[categoria_atual]]) - 1:
                        opcao_atual += 1
                    else:
                        # Se estiver na última opção, vai para a primeira
                        opcao_atual = 0
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    # Diminuir valor da opção atual
                    opcoes = opcoes_categorias[categorias[categoria_atual]]
                    if opcao_atual < len(opcoes):
                        nome, cat, chave, min_val, max_val, step = opcoes[opcao_atual]
                        valor_atual = CONFIGURACOES[cat][chave]
                        if isinstance(valor_atual, bool):
                            CONFIGURACOES[cat][chave] = not valor_atual
                        elif valor_atual > min_val:
                            CONFIGURACOES[cat][chave] = max(min_val, valor_atual - step)
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    # Aumentar valor da opção atual
                    opcoes = opcoes_categorias[categorias[categoria_atual]]
                    if opcao_atual < len(opcoes):
                        nome, cat, chave, min_val, max_val, step = opcoes[opcao_atual]
                        valor_atual = CONFIGURACOES[cat][chave]
                        if isinstance(valor_atual, bool):
                            CONFIGURACOES[cat][chave] = not valor_atual
                        elif valor_atual < max_val:
                            CONFIGURACOES[cat][chave] = min(max_val, valor_atual + step)
                elif ev.key == pygame.K_TAB:
                    # Alternar entre categorias
                    categoria_atual = (categoria_atual + 1) % len(categorias)
                    opcao_atual = 0
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    # Aplicar configuração (para opções booleanas)
                    opcoes = opcoes_categorias[categorias[categoria_atual]]
                    if opcao_atual < len(opcoes):
                        nome, cat, chave, min_val, max_val, step = opcoes[opcao_atual]
                        valor_atual = CONFIGURACOES[cat][chave]
                        if isinstance(valor_atual, bool):
                            CONFIGURACOES[cat][chave] = not valor_atual
        
        # Desenhar
        screen.blit(bg, (0, 0))
        
        # Overlay escuro
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Título
        screen.blit(render_text("OPÇÕES", 48, (0,255,230)), (LARGURA//2 - 100, 30))
        
        # Instruções melhoradas
        instrucoes = [
            "↑ ↓ navegar opções | ← → ajustar valores | TAB mudar categoria | MOUSE clicar",
            "ENTER/SPACE alternar ON/OFF | BOTÕES APLICAR/SAIR | F11 alternar tela"
        ]
        for i, instrucao in enumerate(instrucoes):
            screen.blit(render_text(instrucao, 16, (200, 200, 200)), (LARGURA//2 - 200, 80 + i * 20))
        
        # Categoria atual (destaque)
        categoria_nome = categorias[categoria_atual]
        screen.blit(render_text(f"CATEGORIA: {categoria_nome}", 24, (255, 180, 60)), (50, 130))
        
        # Opções da categoria atual
        opcoes = opcoes_categorias[categoria_nome]
        y_opc = 180
        for i, (nome, cat, chave, min_val, max_val, step) in enumerate(opcoes):
            # Cor baseada na seleção
            if i == opcao_atual:
                cor = (255, 180, 60)  # Amarelo para selecionado
                cor_valor = (255, 255, 100)  # Amarelo claro para valor
                # Fundo para opção selecionada
                fundo = pygame.Surface((LARGURA - 100, 40), pygame.SRCALPHA)
                fundo.fill((255, 180, 60, 30))
                screen.blit(fundo, (50, y_opc + i * 45 - 5))
            else:
                cor = (255, 255, 255)  # Branco para não selecionado
                cor_valor = (200, 200, 200)  # Cinza para valor
            
            # Nome da opção
            screen.blit(render_text(nome, 22, cor), (70, y_opc + i * 45))
            
            # Valor atual com formatação melhorada
            valor_atual = CONFIGURACOES[cat][chave]
            if isinstance(valor_atual, bool):
                valor_texto = "ON" if valor_atual else "OFF"
                cor_valor = (100, 255, 100) if valor_atual else (255, 100, 100)
            elif isinstance(valor_atual, float):
                valor_texto = f"{valor_atual:.1f}"
            else:
                valor_texto = str(valor_atual)
            
            # Posição do valor (lado direito)
            valor_x = LARGURA - 200
            screen.blit(render_text(valor_texto, 20, cor_valor), (valor_x, y_opc + i * 45))
            
            # Barra de progresso para valores numéricos
            if not isinstance(valor_atual, bool):
                barra_w = 150
                barra_h = 8
                barra_x = valor_x - barra_w - 20
                barra_y = y_opc + i * 45 + 10
                
                # Fundo da barra
                pygame.draw.rect(screen, (50, 50, 50), (barra_x, barra_y, barra_w, barra_h))
                
                # Preenchimento da barra
                progresso = (valor_atual - min_val) / (max_val - min_val)
                preenchimento_w = int(barra_w * progresso)
                pygame.draw.rect(screen, (100, 200, 255), (barra_x, barra_y, preenchimento_w, barra_h))
        
        # Indicador de categoria
        cat_x = 50
        cat_y = ALTURA - 120
        screen.blit(render_text("Categorias:", 18, (200, 200, 200)), (cat_x, cat_y))
        
        for i, cat in enumerate(categorias):
            if i == categoria_atual:
                cor_cat = (255, 180, 60)
                # Destacar categoria atual
                pygame.draw.rect(screen, (255, 180, 60, 50), (cat_x + i * 120, cat_y + 25, 100, 25))
            else:
                cor_cat = (150, 150, 150)
            
            screen.blit(render_text(cat, 16, cor_cat), (cat_x + i * 120, cat_y + 25))
        
        # Botões de ação clicáveis (posicionados mais acima para não sobrepor instruções)
        botao_aplicar_rect = pygame.Rect(LARGURA - 200, ALTURA - 120, 150, 40)
        botao_sair_rect = pygame.Rect(50, ALTURA - 120, 150, 40)
        
        # Verificar hover dos botões
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hover_aplicar = botao_aplicar_rect.collidepoint(mouse_x, mouse_y)
        hover_sair = botao_sair_rect.collidepoint(mouse_x, mouse_y)
        
        # Cores dos botões baseadas no hover
        cor_aplicar = (120, 255, 120) if hover_aplicar else (100, 255, 100)
        cor_sair = (255, 120, 120) if hover_sair else (255, 100, 100)
        
        # Desenhar botões
        pygame.draw.rect(screen, cor_aplicar, botao_aplicar_rect)
        pygame.draw.rect(screen, cor_sair, botao_sair_rect)
        
        # Borda dos botões
        pygame.draw.rect(screen, (255, 255, 255), botao_aplicar_rect, 2)
        pygame.draw.rect(screen, (255, 255, 255), botao_sair_rect, 2)
        
        # Texto dos botões
        screen.blit(render_text("APLICAR", 18, (255, 255, 255)), (botao_aplicar_rect.x + 50, botao_aplicar_rect.y + 12))
        screen.blit(render_text("SAIR", 18, (255, 255, 255)), (botao_sair_rect.x + 50, botao_sair_rect.y + 12))
        
        # Instruções adicionais (posicionadas abaixo dos botões)
        screen.blit(render_text("TAB - MUDAR CATEGORIA", 16, (200, 200, 200)), (LARGURA - 250, ALTURA - 70))
        
        pygame.display.flip()

def run():
    from config import CONFIGURACOES, carregar_configuracoes
    pygame.init()
    pygame.display.set_caption("Turbo Racer — Menu")
    
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
    
    while True:
        escolha = menu_loop(screen)
        
        if escolha == Escolha.JOGAR:
            # Parar música do menu se não deve tocar no jogo
            if not CONFIGURACOES["audio"]["musica_no_jogo"]:
                gerenciador_musica.parar_musica()
            # inicia seu jogo original com carros selecionados
            main.principal(carro_p1, carro_p2)
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
        elif escolha == Escolha.SELECIONAR_MAPAS:
            # Abre tela de seleção de mapas
            selecionar_mapas_loop(screen)
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
