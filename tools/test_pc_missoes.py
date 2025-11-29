# tools/test_pc_missoes.py
"""
Arquivo de teste para ajustar tamanhos e layout da tela de missões do PC
Execute este arquivo para testar e ajustar os tamanhos dos elementos

CONTROLES:
- E: Ativar/desativar modo de edição
- No modo edição:
  - Clique e arraste: Mover painéis
  - Clique e arraste nos cantos: Redimensionar painéis
  - +/-: Ajustar espaçamento entre missões
  - PgUp/PgDn: Ajustar altura dos itens
  - S: Salvar configurações
  - L: Carregar configurações
"""

import os
import sys
import json

diretorio_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
diretorio_src = os.path.join(diretorio_raiz, 'src')
sys.path.insert(0, diretorio_src)
sys.path.insert(0, diretorio_raiz)

from config import LARGURA, ALTURA, FPS, DIR_UI

import pygame

from core.menu import render_text

PAINEL_ESQ_X = 50
PAINEL_ESQ_Y = 100
PAINEL_ESQ_LARGURA = 500
PAINEL_ESQ_ALTURA = 500

PAINEL_DIR_X = 600
PAINEL_DIR_Y = 100
PAINEL_DIR_LARGURA = 600
PAINEL_DIR_ALTURA = 450

TAMANHO_FONTE_TITULO = 12
TAMANHO_FONTE_MISSAO = 20
TAMANHO_FONTE_OBJETIVO = 35

ESPACAMENTO_MISSOES = 55
ALTURA_ITEM_MISSAO = 45

BTN_INICIAR_X = LARGURA // 2 - 120
BTN_INICIAR_Y = ALTURA - 80
BTN_INICIAR_LARGURA = 240
BTN_INICIAR_ALTURA = 40

CONFIG_FILE = os.path.join(diretorio_raiz, "tools", "pc_missoes_config.json")

def salvar_config():
    """Salva as configurações atuais em um arquivo JSON"""
    global PAINEL_ESQ_X, PAINEL_ESQ_Y, PAINEL_ESQ_LARGURA, PAINEL_ESQ_ALTURA
    global PAINEL_DIR_X, PAINEL_DIR_Y, PAINEL_DIR_LARGURA, PAINEL_DIR_ALTURA
    global TAMANHO_FONTE_TITULO, TAMANHO_FONTE_MISSAO, TAMANHO_FONTE_OBJETIVO
    global ESPACAMENTO_MISSOES, ALTURA_ITEM_MISSAO
    global BTN_INICIAR_X, BTN_INICIAR_Y, BTN_INICIAR_LARGURA, BTN_INICIAR_ALTURA
    
    config = {
        "PAINEL_ESQ_X": PAINEL_ESQ_X,
        "PAINEL_ESQ_Y": PAINEL_ESQ_Y,
        "PAINEL_ESQ_LARGURA": PAINEL_ESQ_LARGURA,
        "PAINEL_ESQ_ALTURA": PAINEL_ESQ_ALTURA,
        "PAINEL_DIR_X": PAINEL_DIR_X,
        "PAINEL_DIR_Y": PAINEL_DIR_Y,
        "PAINEL_DIR_LARGURA": PAINEL_DIR_LARGURA,
        "PAINEL_DIR_ALTURA": PAINEL_DIR_ALTURA,
        "TAMANHO_FONTE_TITULO": TAMANHO_FONTE_TITULO,
        "TAMANHO_FONTE_MISSAO": TAMANHO_FONTE_MISSAO,
        "TAMANHO_FONTE_OBJETIVO": TAMANHO_FONTE_OBJETIVO,
        "ESPACAMENTO_MISSOES": ESPACAMENTO_MISSOES,
        "ALTURA_ITEM_MISSAO": ALTURA_ITEM_MISSAO,
        "BTN_INICIAR_X": BTN_INICIAR_X,
        "BTN_INICIAR_Y": BTN_INICIAR_Y,
        "BTN_INICIAR_LARGURA": BTN_INICIAR_LARGURA,
        "BTN_INICIAR_ALTURA": BTN_INICIAR_ALTURA
    }
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        if os.path.exists(CONFIG_FILE):
            print(f"✓ Configurações salvas em: {CONFIG_FILE}")
            print(f"  Botão: X={BTN_INICIAR_X}, Y={BTN_INICIAR_Y}, L={BTN_INICIAR_LARGURA}, A={BTN_INICIAR_ALTURA}")
            return True
        else:
            print(f"✗ Erro: Arquivo não foi criado em {CONFIG_FILE}")
            return False
    except Exception as e:
        print(f"✗ Erro ao salvar: {e}")
        import traceback
        traceback.print_exc()
        return False

def carregar_config():
    """Carrega configurações de um arquivo JSON"""
    global PAINEL_ESQ_X, PAINEL_ESQ_Y, PAINEL_ESQ_LARGURA, PAINEL_ESQ_ALTURA
    global PAINEL_DIR_X, PAINEL_DIR_Y, PAINEL_DIR_LARGURA, PAINEL_DIR_ALTURA
    global TAMANHO_FONTE_TITULO, TAMANHO_FONTE_MISSAO, TAMANHO_FONTE_OBJETIVO
    global ESPACAMENTO_MISSOES, ALTURA_ITEM_MISSAO
    global BTN_INICIAR_X, BTN_INICIAR_Y, BTN_INICIAR_LARGURA, BTN_INICIAR_ALTURA
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                PAINEL_ESQ_X = config.get("PAINEL_ESQ_X", PAINEL_ESQ_X)
                PAINEL_ESQ_Y = config.get("PAINEL_ESQ_Y", PAINEL_ESQ_Y)
                PAINEL_ESQ_LARGURA = config.get("PAINEL_ESQ_LARGURA", PAINEL_ESQ_LARGURA)
                PAINEL_ESQ_ALTURA = config.get("PAINEL_ESQ_ALTURA", PAINEL_ESQ_ALTURA)
                PAINEL_DIR_X = config.get("PAINEL_DIR_X", PAINEL_DIR_X)
                PAINEL_DIR_Y = config.get("PAINEL_DIR_Y", PAINEL_DIR_Y)
                PAINEL_DIR_LARGURA = config.get("PAINEL_DIR_LARGURA", PAINEL_DIR_LARGURA)
                PAINEL_DIR_ALTURA = config.get("PAINEL_DIR_ALTURA", PAINEL_DIR_ALTURA)
                TAMANHO_FONTE_TITULO = config.get("TAMANHO_FONTE_TITULO", TAMANHO_FONTE_TITULO)
                TAMANHO_FONTE_MISSAO = config.get("TAMANHO_FONTE_MISSAO", TAMANHO_FONTE_MISSAO)
                TAMANHO_FONTE_OBJETIVO = config.get("TAMANHO_FONTE_OBJETIVO", TAMANHO_FONTE_OBJETIVO)
                ESPACAMENTO_MISSOES = config.get("ESPACAMENTO_MISSOES", ESPACAMENTO_MISSOES)
                ALTURA_ITEM_MISSAO = config.get("ALTURA_ITEM_MISSAO", ALTURA_ITEM_MISSAO)
                BTN_INICIAR_X = config.get("BTN_INICIAR_X", BTN_INICIAR_X)
                BTN_INICIAR_Y = config.get("BTN_INICIAR_Y", BTN_INICIAR_Y)
                BTN_INICIAR_LARGURA = config.get("BTN_INICIAR_LARGURA", BTN_INICIAR_LARGURA)
                BTN_INICIAR_ALTURA = config.get("BTN_INICIAR_ALTURA", BTN_INICIAR_ALTURA)
            return True
        except Exception as e:
            print(f"Erro ao carregar: {e}")
            return False
    return False

def detectar_canto_redimensionamento(x, y, largura, altura, mouse_x, mouse_y, margem=10):
    """Detecta qual canto está sendo arrastado para redimensionar"""
    # Cantos: 0=esquerda-topo, 1=direita-topo, 2=esquerda-baixo, 3=direita-baixo
    if abs(mouse_x - x) < margem and abs(mouse_y - y) < margem:
        return 0  # Esquerda-Topo
    elif abs(mouse_x - (x + largura)) < margem and abs(mouse_y - y) < margem:
        return 1  # Direita-Topo
    elif abs(mouse_x - x) < margem and abs(mouse_y - (y + altura)) < margem:
        return 2  # Esquerda-Baixo
    elif abs(mouse_x - (x + largura)) < margem and abs(mouse_y - (y + altura)) < margem:
        return 3  # Direita-Baixo
    return None

def main():
    global PAINEL_ESQ_X, PAINEL_ESQ_Y, PAINEL_ESQ_LARGURA, PAINEL_ESQ_ALTURA
    global PAINEL_DIR_X, PAINEL_DIR_Y, PAINEL_DIR_LARGURA, PAINEL_DIR_ALTURA
    global ESPACAMENTO_MISSOES, ALTURA_ITEM_MISSAO
    global BTN_INICIAR_X, BTN_INICIAR_Y, BTN_INICIAR_LARGURA, BTN_INICIAR_ALTURA
    
    pygame.init()
    screen = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Teste - Tela de Missões do PC (E para editar)")
    clock = pygame.time.Clock()
    
    carregar_config()
    
    caminho_tela_pc = os.path.join(DIR_UI, "tela_pc.png")
    if os.path.exists(caminho_tela_pc):
        bg_raw = pygame.image.load(caminho_tela_pc).convert_alpha()
        bg = pygame.transform.scale(bg_raw, (LARGURA, ALTURA))
    else:
        bg = pygame.Surface((LARGURA, ALTURA))
        bg.fill((20, 20, 30))
    
    missoes_exemplo = [
        {"id": "m1", "nome": "Primeira Faísca", "objetivo": "Encontre a garagem do Crank no bairro baixo."},
        {"id": "m2", "nome": "Teste de Sobrevivência", "objetivo": "Complete a corrida de teste da garagem do Crank."},
        {"id": "m3", "nome": "Rota da Ferrugem", "objetivo": "Vá até o Fosso de Ferrugem e fale com Boris."},
        {"id": "m4", "nome": "Coração de Sucata", "objetivo": "Compre uma peça principal com Boris para melhorar seu carro."},
        {"id": "m5", "nome": "Cirurgia na Garagem", "objetivo": "Volte à garagem do Crank e instale a nova peça."},
        {"id": "m6", "nome": "Batismo de Pista", "objetivo": "Corra no Circuito de Treino e termine a corrida."},
    ]
    
    missao_selecionada = 0
    missao_hover = None
    
    modo_edicao = False
    arrastando_painel_esq = False
    arrastando_painel_dir = False
    arrastando_botao = False
    redimensionando_esq = None
    redimensionando_dir = None
    redimensionando_botao = None
    offset_x = 0
    offset_y = 0
    largura_inicial = 0
    altura_inicial = 0
    x_inicial = 0
    y_inicial = 0
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_e:
                    modo_edicao = not modo_edicao
                elif event.key == pygame.K_s and modo_edicao:
                    if salvar_config():
                        print("✓ Configurações salvas com sucesso!")
                        print(f"  Botão salvo: X={BTN_INICIAR_X}, Y={BTN_INICIAR_Y}, L={BTN_INICIAR_LARGURA}, A={BTN_INICIAR_ALTURA}")
                elif event.key == pygame.K_l and modo_edicao:
                    if carregar_config():
                        print("Configurações carregadas!")
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    if not modo_edicao:
                        missao_selecionada = max(0, missao_selecionada - 1)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if not modo_edicao:
                        missao_selecionada = min(len(missoes_exemplo) - 1, missao_selecionada + 1)
                elif modo_edicao:
                    if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        ESPACAMENTO_MISSOES = min(100, ESPACAMENTO_MISSOES + 1)
                    elif event.key == pygame.K_MINUS:
                        ESPACAMENTO_MISSOES = max(10, ESPACAMENTO_MISSOES - 1)
                    elif event.key == pygame.K_PAGEUP:
                        ALTURA_ITEM_MISSAO = min(100, ALTURA_ITEM_MISSAO + 1)
                    elif event.key == pygame.K_PAGEDOWN:
                        ALTURA_ITEM_MISSAO = max(10, ALTURA_ITEM_MISSAO - 1)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo
                    if modo_edicao:
                        canto_esq = detectar_canto_redimensionamento(
                            PAINEL_ESQ_X, PAINEL_ESQ_Y, PAINEL_ESQ_LARGURA, PAINEL_ESQ_ALTURA, mouse_x, mouse_y
                        )
                        canto_dir = detectar_canto_redimensionamento(
                            PAINEL_DIR_X, PAINEL_DIR_Y, PAINEL_DIR_LARGURA, PAINEL_DIR_ALTURA, mouse_x, mouse_y
                        )
                        canto_botao = detectar_canto_redimensionamento(
                            BTN_INICIAR_X, BTN_INICIAR_Y, BTN_INICIAR_LARGURA, BTN_INICIAR_ALTURA, mouse_x, mouse_y
                        )
                        
                        if canto_esq is not None:
                            redimensionando_esq = canto_esq
                            largura_inicial = PAINEL_ESQ_LARGURA
                            altura_inicial = PAINEL_ESQ_ALTURA
                            x_inicial = PAINEL_ESQ_X
                            y_inicial = PAINEL_ESQ_Y
                            offset_x = mouse_x - PAINEL_ESQ_X
                            offset_y = mouse_y - PAINEL_ESQ_Y
                        elif canto_dir is not None:
                            redimensionando_dir = canto_dir
                            largura_inicial = PAINEL_DIR_LARGURA
                            altura_inicial = PAINEL_DIR_ALTURA
                            x_inicial = PAINEL_DIR_X
                            y_inicial = PAINEL_DIR_Y
                            offset_x = mouse_x - PAINEL_DIR_X
                            offset_y = mouse_y - PAINEL_DIR_Y
                        elif (PAINEL_ESQ_X <= mouse_x <= PAINEL_ESQ_X + PAINEL_ESQ_LARGURA and
                              PAINEL_ESQ_Y <= mouse_y <= PAINEL_ESQ_Y + PAINEL_ESQ_ALTURA):
                            arrastando_painel_esq = True
                            offset_x = mouse_x - PAINEL_ESQ_X
                            offset_y = mouse_y - PAINEL_ESQ_Y
                        elif canto_botao is not None:
                            redimensionando_botao = canto_botao
                            largura_inicial = BTN_INICIAR_LARGURA
                            altura_inicial = BTN_INICIAR_ALTURA
                            x_inicial = BTN_INICIAR_X
                            y_inicial = BTN_INICIAR_Y
                            offset_x = mouse_x - BTN_INICIAR_X
                            offset_y = mouse_y - BTN_INICIAR_Y
                        elif (PAINEL_DIR_X <= mouse_x <= PAINEL_DIR_X + PAINEL_DIR_LARGURA and
                              PAINEL_DIR_Y <= mouse_y <= PAINEL_DIR_Y + PAINEL_DIR_ALTURA):
                            arrastando_painel_dir = True
                            offset_x = mouse_x - PAINEL_DIR_X
                            offset_y = mouse_y - PAINEL_DIR_Y
                        elif (BTN_INICIAR_X <= mouse_x <= BTN_INICIAR_X + BTN_INICIAR_LARGURA and
                              BTN_INICIAR_Y <= mouse_y <= BTN_INICIAR_Y + BTN_INICIAR_ALTURA):
                            arrastando_botao = True
                            offset_x = mouse_x - BTN_INICIAR_X
                            offset_y = mouse_y - BTN_INICIAR_Y
                    else:
                        y_inicio = PAINEL_ESQ_Y + 50
                        for i, missao in enumerate(missoes_exemplo):
                            y_missao = y_inicio + i * ESPACAMENTO_MISSOES
                            if (PAINEL_ESQ_X + 15 <= mouse_x <= PAINEL_ESQ_X + PAINEL_ESQ_LARGURA - 15 and
                                y_missao <= mouse_y <= y_missao + ALTURA_ITEM_MISSAO):
                                missao_selecionada = i
                                break
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    arrastando_painel_esq = False
                    arrastando_painel_dir = False
                    arrastando_botao = False
                    redimensionando_esq = None
                    redimensionando_dir = None
                    redimensionando_botao = None
            
            elif event.type == pygame.MOUSEMOTION:
                if modo_edicao:
                    if arrastando_painel_esq:
                        PAINEL_ESQ_X = mouse_x - offset_x
                        PAINEL_ESQ_Y = mouse_y - offset_y
                        # Limitar dentro da tela
                        PAINEL_ESQ_X = max(0, min(PAINEL_ESQ_X, LARGURA - PAINEL_ESQ_LARGURA))
                        PAINEL_ESQ_Y = max(0, min(PAINEL_ESQ_Y, ALTURA - PAINEL_ESQ_ALTURA))
                    elif arrastando_painel_dir:
                        PAINEL_DIR_X = mouse_x - offset_x
                        PAINEL_DIR_Y = mouse_y - offset_y
                        # Limitar dentro da tela
                        PAINEL_DIR_X = max(0, min(PAINEL_DIR_X, LARGURA - PAINEL_DIR_LARGURA))
                        PAINEL_DIR_Y = max(0, min(PAINEL_DIR_Y, ALTURA - PAINEL_DIR_ALTURA))
                    elif redimensionando_esq is not None:
                        dx = mouse_x - (x_inicial + offset_x)
                        dy = mouse_y - (y_inicial + offset_y)
                        
                        if redimensionando_esq == 0:  # Esquerda-Topo
                            PAINEL_ESQ_X = x_inicial + dx
                            PAINEL_ESQ_LARGURA = largura_inicial - dx
                            PAINEL_ESQ_Y = y_inicial + dy
                            PAINEL_ESQ_ALTURA = altura_inicial - dy
                        elif redimensionando_esq == 1:  # Direita-Topo
                            PAINEL_ESQ_LARGURA = largura_inicial + dx
                            PAINEL_ESQ_Y = y_inicial + dy
                            PAINEL_ESQ_ALTURA = altura_inicial - dy
                        elif redimensionando_esq == 2:  # Esquerda-Baixo
                            PAINEL_ESQ_X = x_inicial + dx
                            PAINEL_ESQ_LARGURA = largura_inicial - dx
                            PAINEL_ESQ_ALTURA = altura_inicial + dy
                        elif redimensionando_esq == 3:  # Direita-Baixo
                            PAINEL_ESQ_LARGURA = largura_inicial + dx
                            PAINEL_ESQ_ALTURA = altura_inicial + dy
                        
                        # Limites mínimos
                        PAINEL_ESQ_LARGURA = max(100, PAINEL_ESQ_LARGURA)
                        PAINEL_ESQ_ALTURA = max(100, PAINEL_ESQ_ALTURA)
                        PAINEL_ESQ_X = max(0, min(PAINEL_ESQ_X, LARGURA - PAINEL_ESQ_LARGURA))
                        PAINEL_ESQ_Y = max(0, min(PAINEL_ESQ_Y, ALTURA - PAINEL_ESQ_ALTURA))
                    elif redimensionando_dir is not None:
                        dx = mouse_x - (x_inicial + offset_x)
                        dy = mouse_y - (y_inicial + offset_y)
                        
                        if redimensionando_dir == 0:  # Esquerda-Topo
                            PAINEL_DIR_X = x_inicial + dx
                            PAINEL_DIR_LARGURA = largura_inicial - dx
                            PAINEL_DIR_Y = y_inicial + dy
                            PAINEL_DIR_ALTURA = altura_inicial - dy
                        elif redimensionando_dir == 1:  # Direita-Topo
                            PAINEL_DIR_LARGURA = largura_inicial + dx
                            PAINEL_DIR_Y = y_inicial + dy
                            PAINEL_DIR_ALTURA = altura_inicial - dy
                        elif redimensionando_dir == 2:  # Esquerda-Baixo
                            PAINEL_DIR_X = x_inicial + dx
                            PAINEL_DIR_LARGURA = largura_inicial - dx
                            PAINEL_DIR_ALTURA = altura_inicial + dy
                        elif redimensionando_dir == 3:  # Direita-Baixo
                            PAINEL_DIR_LARGURA = largura_inicial + dx
                            PAINEL_DIR_ALTURA = altura_inicial + dy
                        
                        # Limites mínimos
                        PAINEL_DIR_LARGURA = max(100, PAINEL_DIR_LARGURA)
                        PAINEL_DIR_ALTURA = max(100, PAINEL_DIR_ALTURA)
                        PAINEL_DIR_X = max(0, min(PAINEL_DIR_X, LARGURA - PAINEL_DIR_LARGURA))
                        PAINEL_DIR_Y = max(0, min(PAINEL_DIR_Y, ALTURA - PAINEL_DIR_ALTURA))
                    elif arrastando_botao:
                        BTN_INICIAR_X = mouse_x - offset_x
                        BTN_INICIAR_Y = mouse_y - offset_y
                        # Limitar dentro da tela
                        BTN_INICIAR_X = max(0, min(BTN_INICIAR_X, LARGURA - BTN_INICIAR_LARGURA))
                        BTN_INICIAR_Y = max(0, min(BTN_INICIAR_Y, ALTURA - BTN_INICIAR_ALTURA))
                    elif redimensionando_botao is not None:
                        dx = mouse_x - (x_inicial + offset_x)
                        dy = mouse_y - (y_inicial + offset_y)
                        
                        if redimensionando_botao == 0:  # Esquerda-Topo
                            BTN_INICIAR_X = x_inicial + dx
                            BTN_INICIAR_LARGURA = largura_inicial - dx
                            BTN_INICIAR_Y = y_inicial + dy
                            BTN_INICIAR_ALTURA = altura_inicial - dy
                        elif redimensionando_botao == 1:  # Direita-Topo
                            BTN_INICIAR_LARGURA = largura_inicial + dx
                            BTN_INICIAR_Y = y_inicial + dy
                            BTN_INICIAR_ALTURA = altura_inicial - dy
                        elif redimensionando_botao == 2:  # Esquerda-Baixo
                            BTN_INICIAR_X = x_inicial + dx
                            BTN_INICIAR_LARGURA = largura_inicial - dx
                            BTN_INICIAR_ALTURA = altura_inicial + dy
                        elif redimensionando_botao == 3:  # Direita-Baixo
                            BTN_INICIAR_LARGURA = largura_inicial + dx
                            BTN_INICIAR_ALTURA = altura_inicial + dy
                        
                        # Limites mínimos
                        BTN_INICIAR_LARGURA = max(50, BTN_INICIAR_LARGURA)
                        BTN_INICIAR_ALTURA = max(20, BTN_INICIAR_ALTURA)
                        BTN_INICIAR_X = max(0, min(BTN_INICIAR_X, LARGURA - BTN_INICIAR_LARGURA))
                        BTN_INICIAR_Y = max(0, min(BTN_INICIAR_Y, ALTURA - BTN_INICIAR_ALTURA))
        
        # Verificar hover
        missao_hover = None
        if not modo_edicao:
            y_inicio = PAINEL_ESQ_Y + 50
            for i, missao in enumerate(missoes_exemplo):
                y_missao = y_inicio + i * ESPACAMENTO_MISSOES
                if (PAINEL_ESQ_X + 15 <= mouse_x <= PAINEL_ESQ_X + PAINEL_ESQ_LARGURA - 15 and
                    y_missao <= mouse_y <= y_missao + ALTURA_ITEM_MISSAO):
                    missao_hover = i
                    break
        
        screen.blit(bg, (0, 0))
        
        titulo = render_text("MISSÕES", 28, (255, 255, 255), bold=True, pixel_style=True)
        titulo_x = (LARGURA - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, 30))
        
        cor_borda = (255, 255, 0) if modo_edicao else (255, 255, 0)
        pygame.draw.rect(screen, cor_borda, (PAINEL_ESQ_X, PAINEL_ESQ_Y, PAINEL_ESQ_LARGURA, PAINEL_ESQ_ALTURA), 3)
        
        if modo_edicao:
            margem = 10
            cantos = [
                (PAINEL_ESQ_X, PAINEL_ESQ_Y),
                (PAINEL_ESQ_X + PAINEL_ESQ_LARGURA, PAINEL_ESQ_Y),
                (PAINEL_ESQ_X, PAINEL_ESQ_Y + PAINEL_ESQ_ALTURA),
                (PAINEL_ESQ_X + PAINEL_ESQ_LARGURA, PAINEL_ESQ_Y + PAINEL_ESQ_ALTURA)
            ]
            for cx, cy in cantos:
                pygame.draw.circle(screen, (255, 0, 0), (cx, cy), margem)
        
        painel_esq_titulo = render_text("MISSÕES", TAMANHO_FONTE_TITULO, (255, 255, 0), bold=True, pixel_style=True)
        screen.blit(painel_esq_titulo, (PAINEL_ESQ_X + 15, PAINEL_ESQ_Y + 15))
        
        y_inicio = PAINEL_ESQ_Y + 50
        for i, missao in enumerate(missoes_exemplo):
            y_missao = y_inicio + i * ESPACAMENTO_MISSOES
            
            if i == missao_selecionada:
                cor_fundo = (100, 150, 255, 200)
                cor_texto = (255, 255, 255)
                bold = True
            elif i == missao_hover:
                cor_fundo = (80, 80, 80, 200)
                cor_texto = (200, 200, 255)
                bold = False
            else:
                cor_fundo = (40, 40, 40, 150)
                cor_texto = (180, 180, 180)
                bold = False
            
            item_bg = pygame.Surface((PAINEL_ESQ_LARGURA - 30, ALTURA_ITEM_MISSAO), pygame.SRCALPHA)
            item_bg.fill(cor_fundo)
            screen.blit(item_bg, (PAINEL_ESQ_X + 15, y_missao))
            
            nome_texto = render_text(missao["nome"], TAMANHO_FONTE_MISSAO, cor_texto, bold=bold, pixel_style=True)
            texto_y = y_missao + (ALTURA_ITEM_MISSAO - nome_texto.get_height()) // 2
            screen.blit(nome_texto, (PAINEL_ESQ_X + 20, texto_y))
        
        pygame.draw.rect(screen, cor_borda, (PAINEL_DIR_X, PAINEL_DIR_Y, PAINEL_DIR_LARGURA, PAINEL_DIR_ALTURA), 3)
        
        if modo_edicao:
            cantos = [
                (PAINEL_DIR_X, PAINEL_DIR_Y),
                (PAINEL_DIR_X + PAINEL_DIR_LARGURA, PAINEL_DIR_Y),
                (PAINEL_DIR_X, PAINEL_DIR_Y + PAINEL_DIR_ALTURA),
                (PAINEL_DIR_X + PAINEL_DIR_LARGURA, PAINEL_DIR_Y + PAINEL_DIR_ALTURA)
            ]
            for cx, cy in cantos:
                pygame.draw.circle(screen, (255, 0, 0), (cx, cy), margem)
        
        painel_dir_titulo = render_text("OBJETIVO DA MISSÃO", TAMANHO_FONTE_TITULO, (255, 255, 0), bold=True, pixel_style=True)
        screen.blit(painel_dir_titulo, (PAINEL_DIR_X + 20, PAINEL_DIR_Y + 20))
        
        if 0 <= missao_selecionada < len(missoes_exemplo):
            missao_atual = missoes_exemplo[missao_selecionada]
            objetivo = missao_atual.get("objetivo", "Nenhum objetivo definido")
            
            def eh_missao_corrida(missao):
                if not missao:
                    return False
                objetivo = missao.get("objetivo", "").lower()
                palavras_corrida = ["corrida", "corra", "circuito", "pista", "race", "teste de fluxo"]
                return any(palavra in objetivo for palavra in palavras_corrida)
            
            missao_eh_corrida = eh_missao_corrida(missao_atual)
            
            NOMES_PISTAS = {
                1: "Pista Principal",
                2: "Circuito Urbano",
                3: "Montanha Akira",
                4: "Pista Industrial",
                5: "Circuito Velocidade",
                6: "Pista Técnica",
                7: "Circuito Desafio",
                8: "Pista Elite",
                9: "Circuito da Coroa"
            }
            pista_selecionada = 1  # Para teste, usar pista 1
            
            # Quebrar texto em múltiplas linhas
            palavras = objetivo.split()
            linhas = []
            linha_atual = ""
            # Aumentar espaçamento entre título e descrição
            y_texto = PAINEL_DIR_Y + 80
            
            for palavra in palavras:
                teste_linha = linha_atual + (" " if linha_atual else "") + palavra
                teste_texto = render_text(teste_linha, TAMANHO_FONTE_OBJETIVO, (255, 255, 255), bold=False, pixel_style=True)
                if teste_texto.get_width() > PAINEL_DIR_LARGURA - 40:
                    if linha_atual:
                        linhas.append(linha_atual)
                        linha_atual = palavra
                    else:
                        linhas.append(palavra)
                        linha_atual = ""
                else:
                    linha_atual = teste_linha
            
            if linha_atual:
                linhas.append(linha_atual)
            
            # Desenhar linhas do objetivo
            num_linhas_objetivo = len(linhas[:15])
            for i, linha in enumerate(linhas[:15]):
                linha_texto = render_text(linha, TAMANHO_FONTE_OBJETIVO, (255, 255, 255), bold=False, pixel_style=True)
                screen.blit(linha_texto, (PAINEL_DIR_X + 20, y_texto + i * 42))
            
            # Se for missão de corrida, mostrar o nome do circuito abaixo da descrição
            if missao_eh_corrida:
                nome_circuito = NOMES_PISTAS.get(pista_selecionada, f"Pista {pista_selecionada}")
                y_circuito = y_texto + (num_linhas_objetivo * 42) + 20
                circuito_label = render_text("Circuito:", 30, (255, 255, 0), bold=True, pixel_style=True)
                screen.blit(circuito_label, (PAINEL_DIR_X + 20, y_circuito))
                circuito_nome = render_text(nome_circuito, 35, (255, 255, 255), bold=True, pixel_style=True)
                screen.blit(circuito_nome, (PAINEL_DIR_X + 20, y_circuito + 40))
        
        btn_bg = pygame.Surface((BTN_INICIAR_LARGURA, BTN_INICIAR_ALTURA), pygame.SRCALPHA)
        btn_bg.fill((0, 150, 0, 200))
        pygame.draw.rect(btn_bg, (255, 255, 255), (0, 0, BTN_INICIAR_LARGURA, BTN_INICIAR_ALTURA), 2)
        screen.blit(btn_bg, (BTN_INICIAR_X, BTN_INICIAR_Y))
        
        btn_texto = render_text("INICIAR (ENTER)", 14, (255, 255, 255), bold=True, pixel_style=True)
        btn_texto_x = BTN_INICIAR_X + (BTN_INICIAR_LARGURA - btn_texto.get_width()) // 2
        btn_texto_y = BTN_INICIAR_Y + (BTN_INICIAR_ALTURA - btn_texto.get_height()) // 2
        screen.blit(btn_texto, (btn_texto_x, btn_texto_y))
        
        if modo_edicao:
            margem = 8
            cantos = [
                (BTN_INICIAR_X, BTN_INICIAR_Y),
                (BTN_INICIAR_X + BTN_INICIAR_LARGURA, BTN_INICIAR_Y),
                (BTN_INICIAR_X, BTN_INICIAR_Y + BTN_INICIAR_ALTURA),
                (BTN_INICIAR_X + BTN_INICIAR_LARGURA, BTN_INICIAR_Y + BTN_INICIAR_ALTURA)
            ]
            for cx, cy in cantos:
                pygame.draw.circle(screen, (255, 0, 0), (cx, cy), margem)
        
        if modo_edicao:
            instrucoes = render_text(
                "MODO EDIÇÃO: Arraste para mover | Arraste cantos para redimensionar | +/- espaçamento | PgUp/PgDn altura | S salvar | L carregar | E sair",
                11, (255, 255, 0), bold=False, pixel_style=True
            )
        else:
            instrucoes = render_text("↑↓ navegar | Clique selecionar | E editar | ESC sair", 12, (150, 150, 150), bold=False, pixel_style=True)
        screen.blit(instrucoes, (10, ALTURA - 25))
        
        debug_text = render_text(
            f"Painel Esq: {PAINEL_ESQ_X},{PAINEL_ESQ_Y} {PAINEL_ESQ_LARGURA}x{PAINEL_ESQ_ALTURA} | "
            f"Painel Dir: {PAINEL_DIR_X},{PAINEL_DIR_Y} {PAINEL_DIR_LARGURA}x{PAINEL_DIR_ALTURA} | "
            f"Botão: {BTN_INICIAR_X},{BTN_INICIAR_Y} {BTN_INICIAR_LARGURA}x{BTN_INICIAR_ALTURA} | "
            f"Espaçamento: {ESPACAMENTO_MISSOES} | Altura Item: {ALTURA_ITEM_MISSAO}",
            10, (100, 100, 100), bold=False, pixel_style=True
        )
        screen.blit(debug_text, (10, ALTURA - 45))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
