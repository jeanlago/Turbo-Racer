# src/core/pc_corridas.py
"""
Sistema de Corridas no PC
Tela para selecionar e iniciar corridas no modo campanha
"""

import os
import json
import pygame
from typing import Optional, Dict
from config import LARGURA, ALTURA, DIR_PROJETO, FPS

def _get_render_text():
    from core.menu import render_text
    return render_text

def _sincronizar_missoes_com_estatisticas(gerenciador_missoes):
    """Sincroniza missões com estatísticas de corridas completadas"""
    from core.estatisticas import gerenciador_estatisticas
    
    # Mapeamento de missões para race_id e pista
    mapeamento_missoes = {
        "m6_batismo_de_pista": ("training_01", 1),
        # Adicionar outros mapeamentos conforme necessário
    }
    
    gerenciador_estatisticas.carregar()
    
    for missao_id, (race_id, numero_pista) in mapeamento_missoes.items():
        if not gerenciador_missoes.esta_completa(missao_id):
            stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(numero_pista)
            if stats_pista:
                melhor_tempo = stats_pista.get("melhor_tempo")
                melhor_posicao = stats_pista.get("melhor_posicao")
                
                # Se a corrida foi completada (tem estatísticas)
                if melhor_tempo is not None and melhor_posicao is not None:
                    gerenciador_missoes.completar_missao(missao_id)

def _carregar_config_pc_missoes():
    """Carrega configurações do arquivo JSON se existir, senão retorna valores padrão"""
    config_file = os.path.join(DIR_PROJETO, "tools", "pc_missoes_config.json")
    
    # Valores padrão (do arquivo test_pc_missoes.py)
    config = {
        "PAINEL_ESQ_X": 50,
        "PAINEL_ESQ_Y": 100,
        "PAINEL_ESQ_LARGURA": 500,
        "PAINEL_ESQ_ALTURA": 500,
        "PAINEL_DIR_X": 600,
        "PAINEL_DIR_Y": 100,
        "PAINEL_DIR_LARGURA": 600,
        "PAINEL_DIR_ALTURA": 450,
        "TAMANHO_FONTE_TITULO": 12,
        "TAMANHO_FONTE_MISSAO": 20,
        "TAMANHO_FONTE_OBJETIVO": 35,
        "ESPACAMENTO_MISSOES": 55,
        "ALTURA_ITEM_MISSAO": 45,
        "BTN_INICIAR_X": LARGURA // 2 - 120,
        "BTN_INICIAR_Y": ALTURA - 80,
        "BTN_INICIAR_LARGURA": 240,
        "BTN_INICIAR_ALTURA": 40
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_carregada = json.load(f)
                # Atualizar apenas as chaves que existem no arquivo
                for key in config:
                    if key in config_carregada:
                        config[key] = config_carregada[key]
        except Exception as e:
            print(f"Aviso: Erro ao carregar configuração do PC: {e}")
    
    return config

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

def pc_corridas_loop(screen) -> Optional[dict]:
    """
    Loop principal da tela de corridas no PC
    Retorna um dicionário com informações da corrida selecionada ou None se cancelado
    
    Formato retornado:
    {
        "pista": 1,  # Número da pista (1-9)
        "voltas": 1,
        "dificuldade": "medio"
    }
    """
    from core.pista_tiles import PistaTiles
    from core.progresso import gerenciador_progresso
    from core.missoes import gerenciador_missoes
    
    clock = pygame.time.Clock()
    render_text = _get_render_text()
    
    # Carregar configurações
    config = _carregar_config_pc_missoes()
    
    # Recarregar missões para garantir dados atualizados
    gerenciador_missoes.carregar()
    
    # Sincronizar missões com estatísticas de corridas (verificar se corridas foram completadas)
    _sincronizar_missoes_com_estatisticas(gerenciador_missoes)
    
    # Garantir que as mudanças sejam salvas
    gerenciador_missoes.salvar()
    
    # Obter todas as missões
    todas_missoes = gerenciador_missoes.obter_todas_missoes()
    
    missao_selecionada_idx = 0
    missao_hover_idx = None
    scroll_offset = 0  # Offset para scroll das missões
    
    missao_ativa = gerenciador_missoes.obter_missao_ativa()
    if missao_ativa:
        for i, missao in enumerate(todas_missoes):
            if missao["id"] == missao_ativa["id"]:
                missao_selecionada_idx = i
                break
    
    def eh_missao_corrida(missao):
        if not missao:
            return False
        objetivo = missao.get("objetivo", "").lower()
        palavras_corrida = ["corrida", "corra", "circuito", "pista", "race", "teste de fluxo"]
        return any(palavra in objetivo for palavra in palavras_corrida)
    
    def obter_race_id_da_missao(missao):
        """Mapeia missões para race_id"""
        if not missao:
            return None
        missao_id = missao.get("id", "")
        # Mapeamento de missões para corridas
        mapeamento = {
            "m6_batismo_de_pista": "training_01",
            # Adicionar outros mapeamentos conforme necessário
        }
        return mapeamento.get(missao_id)
    
    def carregar_config_corrida(race_id):
        """Carrega configuração da corrida do races.json"""
        if not race_id:
            return None
        try:
            caminho_races = os.path.join(DIR_PROJETO, "data", "races.json")
            if os.path.exists(caminho_races):
                with open(caminho_races, 'r', encoding='utf-8') as f:
                    races_data = json.load(f)
                    for race in races_data.get("races", []):
                        if race.get("id") == race_id:
                            return race
        except Exception as e:
            print(f"Erro ao carregar corrida {race_id}: {e}")
        return None
    
    pista_selecionada = 1
    voltas_selecionadas = 1
    dificuldade_selecionada = "medio"
    dificuldades = ["facil", "medio", "dificil"]
    dificuldade_idx = 1
    
    pista_tiles = PistaTiles()
    minimapa_selecionado = None
    
    from config import DIR_UI
    caminho_tela_pc = os.path.join(DIR_UI, "tela_pc.png")
    if os.path.exists(caminho_tela_pc):
        bg_raw = pygame.image.load(caminho_tela_pc).convert_alpha()
        bg = pygame.transform.scale(bg_raw, (LARGURA, ALTURA))
    else:
        bg = pygame.Surface((LARGURA, ALTURA))
        bg.fill((20, 20, 30))
    
    running = True
    
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    missao_selecionada_idx = max(0, missao_selecionada_idx - 1)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    missao_selecionada_idx = min(len(todas_missoes) - 1, missao_selecionada_idx + 1)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if missao_selecionada_idx < len(todas_missoes):
                        missao_atual = todas_missoes[missao_selecionada_idx]
                        if eh_missao_corrida(missao_atual):
                            voltas_selecionadas = max(1, voltas_selecionadas - 1)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if missao_selecionada_idx < len(todas_missoes):
                        missao_atual = todas_missoes[missao_selecionada_idx]
                        if eh_missao_corrida(missao_atual):
                            voltas_selecionadas = min(10, voltas_selecionadas + 1)
                elif event.key == pygame.K_TAB:
                    if missao_selecionada_idx < len(todas_missoes):
                        missao_atual = todas_missoes[missao_selecionada_idx]
                        if eh_missao_corrida(missao_atual):
                            dificuldade_idx = (dificuldade_idx + 1) % len(dificuldades)
                            dificuldade_selecionada = dificuldades[dificuldade_idx]
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if missao_selecionada_idx < len(todas_missoes):
                        missao_atual = todas_missoes[missao_selecionada_idx]
                        if eh_missao_corrida(missao_atual):
                            race_id = obter_race_id_da_missao(missao_atual)
                            race_config = carregar_config_corrida(race_id) if race_id else None
                            sem_bots = race_config.get("sem_bots", False) if race_config else False
                            # Se a corrida tem configuração, usar os valores dela
                            if race_config:
                                pista_selecionada = race_config.get("track", pista_selecionada)
                                voltas_selecionadas = race_config.get("laps", voltas_selecionadas)
                                dificuldade_selecionada = race_config.get("difficulty", dificuldade_selecionada)
                            return {
                                "pista": pista_selecionada,
                                "voltas": voltas_selecionadas,
                                "dificuldade": dificuldade_selecionada,
                                "race_id": race_id,
                                "sem_bots": sem_bots
                            }
            
            elif event.type == pygame.MOUSEWHEEL:
                # Scroll com a roda do mouse
                painel_esq_y = 100
                painel_esq_altura = 500
                espacamento_missoes = 55
                altura_item_missao = 45
                y_inicio = painel_esq_y + 50
                area_visivel_altura = painel_esq_altura - 100  # Altura disponível para missões
                max_itens_visiveis = int(area_visivel_altura / espacamento_missoes)
                
                if event.y > 0:  # Scroll para cima
                    scroll_offset = max(0, scroll_offset - 1)
                elif event.y < 0:  # Scroll para baixo
                    max_scroll = max(0, len(todas_missoes) - max_itens_visiveis)
                    scroll_offset = min(max_scroll, scroll_offset + 1)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    
                    painel_esq_x = config["PAINEL_ESQ_X"]
                    painel_esq_y = config["PAINEL_ESQ_Y"]
                    painel_esq_largura = config["PAINEL_ESQ_LARGURA"]
                    painel_esq_altura = config["PAINEL_ESQ_ALTURA"]
                    espacamento_missoes = config["ESPACAMENTO_MISSOES"]
                    altura_item_missao = config["ALTURA_ITEM_MISSAO"]
                    y_inicio = painel_esq_y + 50
                    area_visivel_altura = painel_esq_altura - 100
                    max_itens_visiveis = int(area_visivel_altura / espacamento_missoes)
                    
                    # Verificar clique nas missões visíveis
                    for i in range(scroll_offset, min(scroll_offset + max_itens_visiveis, len(todas_missoes))):
                        y_missao = y_inicio + (i - scroll_offset) * espacamento_missoes
                        if (painel_esq_x + 15 <= mouse_x <= painel_esq_x + painel_esq_largura - 15 and
                            y_missao <= mouse_y <= y_missao + altura_item_missao):
                            missao_selecionada_idx = i
                            break
                    
                    btn_iniciar_x = config["BTN_INICIAR_X"]
                    btn_iniciar_y = config["BTN_INICIAR_Y"]
                    btn_iniciar_largura = config["BTN_INICIAR_LARGURA"]
                    btn_iniciar_altura = config["BTN_INICIAR_ALTURA"]
                    if (btn_iniciar_x <= mouse_x <= btn_iniciar_x + btn_iniciar_largura and
                        btn_iniciar_y <= mouse_y <= btn_iniciar_y + btn_iniciar_altura):
                        if missao_selecionada_idx < len(todas_missoes):
                            missao_atual = todas_missoes[missao_selecionada_idx]
                            if eh_missao_corrida(missao_atual):
                                race_id = obter_race_id_da_missao(missao_atual)
                                race_config = carregar_config_corrida(race_id) if race_id else None
                                sem_bots = race_config.get("sem_bots", False) if race_config else False
                                # Se a corrida tem configuração, usar os valores dela
                                if race_config:
                                    pista_selecionada = race_config.get("track", pista_selecionada)
                                    voltas_selecionadas = race_config.get("laps", voltas_selecionadas)
                                    dificuldade_selecionada = race_config.get("difficulty", dificuldade_selecionada)
                                return {
                                    "pista": pista_selecionada,
                                    "voltas": voltas_selecionadas,
                                    "dificuldade": dificuldade_selecionada,
                                    "race_id": race_id,
                                    "sem_bots": sem_bots
                                }
            
            elif event.type == pygame.MOUSEMOTION:
                pass
        
        screen.blit(bg, (0, 0))
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        painel_esq_x = config["PAINEL_ESQ_X"]
        painel_esq_y = config["PAINEL_ESQ_Y"]
        painel_esq_largura = config["PAINEL_ESQ_LARGURA"]
        painel_esq_altura = config["PAINEL_ESQ_ALTURA"]
        espacamento_missoes = config["ESPACAMENTO_MISSOES"]
        altura_item_missao = config["ALTURA_ITEM_MISSAO"]
        y_inicio = painel_esq_y + 50
        area_visivel_altura = painel_esq_altura - 100  # Altura disponível para missões (descontando título e margens)
        max_itens_visiveis = int(area_visivel_altura / espacamento_missoes)
        
        # Ajustar scroll para manter a missão selecionada visível
        if missao_selecionada_idx < scroll_offset:
            scroll_offset = missao_selecionada_idx
        elif missao_selecionada_idx >= scroll_offset + max_itens_visiveis:
            scroll_offset = missao_selecionada_idx - max_itens_visiveis + 1
        
        # Garantir que scroll_offset não seja negativo ou maior que o necessário
        max_scroll = max(0, len(todas_missoes) - max_itens_visiveis)
        scroll_offset = max(0, min(scroll_offset, max_scroll))
        
        # Calcular índices visíveis
        idx_inicio = scroll_offset
        idx_fim = min(scroll_offset + max_itens_visiveis, len(todas_missoes))
        
        missao_hover_idx = None
        for i in range(idx_inicio, idx_fim):
            y_missao = y_inicio + (i - scroll_offset) * espacamento_missoes
            if (painel_esq_x + 15 <= mouse_x <= painel_esq_x + painel_esq_largura - 15 and
                y_missao <= mouse_y <= y_missao + altura_item_missao):
                missao_hover_idx = i
                break
        
        titulo = render_text("MISSÕES", 28, (255, 255, 255), bold=True, pixel_style=True)
        titulo_x = (LARGURA - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, 30))
        
        # Usar altura do config (já carregada na linha 232)
        pygame.draw.rect(screen, (255, 255, 0), (painel_esq_x, painel_esq_y, painel_esq_largura, painel_esq_altura), 3)
        
        painel_esq_titulo = render_text("MISSÕES", config["TAMANHO_FONTE_TITULO"], (255, 255, 0), bold=True, pixel_style=True)
        screen.blit(painel_esq_titulo, (painel_esq_x + 15, painel_esq_y + 15))
        
        # Se não há missões disponíveis, mostrar mensagem
        if len(todas_missoes) == 0:
            mensagem_vazio = render_text("Nenhuma missão disponível", config["TAMANHO_FONTE_MISSAO"], (150, 150, 150), bold=False, pixel_style=True)
            mensagem_y = painel_esq_y + 100
            screen.blit(mensagem_vazio, (painel_esq_x + 20, mensagem_y))
        else:
            # Desenhar apenas as missões visíveis
            for i in range(idx_inicio, idx_fim):
                missao = todas_missoes[i]
                y_missao = y_inicio + (i - scroll_offset) * espacamento_missoes
                
                # Verificar se está dentro dos limites do painel
                if y_missao < painel_esq_y or y_missao + altura_item_missao > painel_esq_y + painel_esq_altura:
                    continue
                
                esta_completa = gerenciador_missoes.esta_completa(missao["id"])
                
                if i == missao_selecionada_idx:
                    cor_fundo = (100, 150, 255, 200)
                    cor_texto = (255, 255, 255)
                    bold = True
                elif i == missao_hover_idx:
                    cor_fundo = (80, 80, 80, 200)
                    cor_texto = (200, 200, 255)
                    bold = False
                else:
                    cor_fundo = (40, 40, 40, 150)
                    cor_texto = (180, 180, 180)
                    bold = False
                
                if esta_completa:
                    cor_texto = (150, 255, 150) if i != missao_selecionada_idx else (200, 255, 200)
                
                item_bg = pygame.Surface((painel_esq_largura - 30, altura_item_missao), pygame.SRCALPHA)
                item_bg.fill(cor_fundo)
                screen.blit(item_bg, (painel_esq_x + 15, y_missao))
                
                nome_missao = missao.get("nome", "Missão sem nome")
                if esta_completa:
                    nome_missao = "✓ " + nome_missao
                nome_texto = render_text(nome_missao, config["TAMANHO_FONTE_MISSAO"], cor_texto, bold=bold, pixel_style=True)
                texto_y = y_missao + (altura_item_missao - nome_texto.get_height()) // 2
                screen.blit(nome_texto, (painel_esq_x + 20, texto_y))
            
            # Desenhar indicador de scroll se houver mais missões
            if len(todas_missoes) > max_itens_visiveis:
                barra_scroll_x = painel_esq_x + painel_esq_largura - 15
                barra_scroll_y = y_inicio
                barra_scroll_largura = 8
                barra_scroll_altura = area_visivel_altura
                
                # Calcular posição e tamanho do indicador
                scroll_ratio = scroll_offset / max(1, len(todas_missoes) - max_itens_visiveis)
                indicador_altura = max(20, int(barra_scroll_altura * (max_itens_visiveis / len(todas_missoes))))
                indicador_y = barra_scroll_y + int((barra_scroll_altura - indicador_altura) * scroll_ratio)
                
                # Desenhar barra de scroll
                pygame.draw.rect(screen, (100, 100, 100), (barra_scroll_x, barra_scroll_y, barra_scroll_largura, barra_scroll_altura))
                pygame.draw.rect(screen, (200, 200, 200), (barra_scroll_x, indicador_y, barra_scroll_largura, indicador_altura))
        
        if missao_selecionada_idx < len(todas_missoes):
            missao_selecionada_atual = todas_missoes[missao_selecionada_idx]
            missao_eh_corrida = eh_missao_corrida(missao_selecionada_atual)
            
            if missao_eh_corrida and minimapa_selecionado is None:
                minimapa_selecionado = pista_tiles.carregar_minimapa(pista_selecionada)
        else:
            missao_selecionada_atual = None
            missao_eh_corrida = False
        
        painel_x = config["PAINEL_DIR_X"]
        painel_y = config["PAINEL_DIR_Y"]
        painel_largura = config["PAINEL_DIR_LARGURA"]
        painel_altura = config["PAINEL_DIR_ALTURA"]
        
        pygame.draw.rect(screen, (255, 255, 0), (painel_x, painel_y, painel_largura, painel_altura), 3)
        
        painel_titulo = render_text("OBJETIVO DA MISSÃO", config["TAMANHO_FONTE_TITULO"], (255, 255, 0), bold=True, pixel_style=True)
        screen.blit(painel_titulo, (painel_x + 20, painel_y + 20))
        
        if missao_selecionada_atual:
            objetivo = missao_selecionada_atual.get("objetivo", "Nenhum objetivo definido")
            palavras = objetivo.split()
            linhas = []
            linha_atual = ""
            y_texto = painel_y + 80
            
            for palavra in palavras:
                teste_linha = linha_atual + (" " if linha_atual else "") + palavra
                teste_texto = render_text(teste_linha, config["TAMANHO_FONTE_OBJETIVO"], (255, 255, 255), bold=False, pixel_style=True)
                if teste_texto.get_width() > painel_largura - 40:
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
            
            num_linhas_objetivo = len(linhas[:15])
            for i, linha in enumerate(linhas[:15]):
                linha_texto = render_text(linha, config["TAMANHO_FONTE_OBJETIVO"], (255, 255, 255), bold=False, pixel_style=True)
                screen.blit(linha_texto, (painel_x + 20, y_texto + i * 42))
            
            if missao_eh_corrida:
                nome_circuito = NOMES_PISTAS.get(pista_selecionada, f"Pista {pista_selecionada}")
                y_circuito = y_texto + (num_linhas_objetivo * 42) + 20
                circuito_label = render_text("Circuito:", 30, (255, 255, 0), bold=True, pixel_style=True)
                screen.blit(circuito_label, (painel_x + 20, y_circuito))
                circuito_nome = render_text(nome_circuito, 35, (255, 255, 255), bold=True, pixel_style=True)
                screen.blit(circuito_nome, (painel_x + 20, y_circuito + 40))
        else:
            objetivo_texto = render_text("Nenhum objetivo definido", config["TAMANHO_FONTE_OBJETIVO"], (150, 150, 150), bold=False, pixel_style=True)
            screen.blit(objetivo_texto, (painel_x + 20, painel_y + 60))
        
        btn_iniciar_x = config["BTN_INICIAR_X"]
        btn_iniciar_y = config["BTN_INICIAR_Y"]
        btn_iniciar_largura = config["BTN_INICIAR_LARGURA"]
        btn_iniciar_altura = config["BTN_INICIAR_ALTURA"]
        
        btn_bg = pygame.Surface((btn_iniciar_largura, btn_iniciar_altura), pygame.SRCALPHA)
        btn_bg.fill((0, 150, 0, 200))
        pygame.draw.rect(btn_bg, (255, 255, 255), (0, 0, btn_iniciar_largura, btn_iniciar_altura), 2)
        screen.blit(btn_bg, (btn_iniciar_x, btn_iniciar_y))
        
        btn_texto = render_text("INICIAR (ENTER)", 14, (255, 255, 255), bold=True, pixel_style=True)
        btn_texto_x = btn_iniciar_x + (btn_iniciar_largura - btn_texto.get_width()) // 2
        btn_texto_y = btn_iniciar_y + (btn_iniciar_altura - btn_texto.get_height()) // 2
        screen.blit(btn_texto, (btn_texto_x, btn_texto_y))
        
        if missao_selecionada_atual and missao_eh_corrida:
            instrucoes = render_text("↑↓ navegar | ← → voltas | TAB dificuldade | ENTER iniciar | ESC voltar", 12, (150, 150, 150), bold=False, pixel_style=True)
        else:
            instrucoes = render_text("↑↓ navegar | Clique selecionar | ESC voltar", 12, (150, 150, 150), bold=False, pixel_style=True)
        screen.blit(instrucoes, (10, ALTURA - 25))
        
        pygame.display.flip()
    
    return None

def autodromo_corridas_loop(screen) -> Optional[dict]:
    """
    Loop específico para o autódromo - mostra apenas corridas do Circuito da Coroa
    Retorna um dicionário com informações da corrida selecionada ou None se cancelado
    """
    from core.progresso import gerenciador_progresso
    
    clock = pygame.time.Clock()
    render_text = _get_render_text()
    
    # Corridas do Circuito da Coroa
    corridas_coroa = [
        {"id": "crown_stage1", "nome": "Circuito da Coroa - Etapa 1", "track": 8, "laps": 2, "difficulty": "dificil"},
        {"id": "crown_stage2", "nome": "Circuito da Coroa - Etapa 2", "track": 8, "laps": 2, "difficulty": "dificil"},
        {"id": "crown_stage3", "nome": "Circuito da Coroa - Etapa 3", "track": 8, "laps": 2, "difficulty": "dificil"},
        {"id": "crown_final", "nome": "Corrida Final do Circuito da Coroa", "track": 8, "laps": 3, "difficulty": "dificil"}
    ]
    
    # Verificar quais corridas estão desbloqueadas
    corridas_desbloqueadas = []
    if not hasattr(gerenciador_progresso, 'corridas_desbloqueadas'):
        gerenciador_progresso.corridas_desbloqueadas = set()
    
    for corrida in corridas_coroa:
        race_id = corrida["id"]
        if race_id in gerenciador_progresso.corridas_desbloqueadas:
            corridas_desbloqueadas.append(corrida)
    
    if not corridas_desbloqueadas:
        # Nenhuma corrida desbloqueada - mostrar mensagem
        bg = pygame.Surface((LARGURA, ALTURA))
        bg.fill((20, 20, 30))
        screen.blit(bg, (0, 0))
        
        mensagem = render_text("Nenhuma corrida do Circuito da Coroa disponível ainda.", 32, (255, 255, 255), bold=True, pixel_style=True)
        mensagem_x = (LARGURA - mensagem.get_width()) // 2
        mensagem_y = ALTURA // 2 - 50
        screen.blit(mensagem, (mensagem_x, mensagem_y))
        
        instrucao = render_text("Pressione ESC para voltar", 20, (150, 150, 150), bold=False, pixel_style=True)
        instrucao_x = (LARGURA - instrucao.get_width()) // 2
        instrucao_y = mensagem_y + 80
        screen.blit(instrucao, (instrucao_x, instrucao_y))
        
        pygame.display.flip()
        
        aguardando = True
        while aguardando:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
            clock.tick(FPS)
        
        return None
    
    corrida_selecionada_idx = 0
    
    # Fundo
    from config import DIR_UI
    caminho_tela_pc = os.path.join(DIR_UI, "tela_pc.png")
    if os.path.exists(caminho_tela_pc):
        bg_raw = pygame.image.load(caminho_tela_pc).convert_alpha()
        bg = pygame.transform.scale(bg_raw, (LARGURA, ALTURA))
    else:
        bg = pygame.Surface((LARGURA, ALTURA))
        bg.fill((20, 20, 30))
    
    running = True
    
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    corrida_selecionada_idx = max(0, corrida_selecionada_idx - 1)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    corrida_selecionada_idx = min(len(corridas_desbloqueadas) - 1, corrida_selecionada_idx + 1)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if corrida_selecionada_idx < len(corridas_desbloqueadas):
                        corrida = corridas_desbloqueadas[corrida_selecionada_idx]
                        return {
                            "pista": corrida["track"],
                            "voltas": corrida["laps"],
                            "dificuldade": corrida["difficulty"],
                            "race_id": corrida["id"],
                            "sem_bots": False
                        }
        
        screen.blit(bg, (0, 0))
        
        # Título
        titulo = render_text("CIRCUITO DA COROA - AUTÓDROMO", 48, (255, 215, 0), bold=True, pixel_style=True)
        titulo_x = (LARGURA - titulo.get_width()) // 2
        screen.blit(titulo, (titulo_x, 30))
        
        # Lista de corridas
        lista_y = 150
        espacamento = 80
        
        for i, corrida in enumerate(corridas_desbloqueadas):
            y_pos = lista_y + i * espacamento
            
            # Destaque para corrida selecionada
            if i == corrida_selecionada_idx:
                highlight = pygame.Surface((LARGURA - 200, 60), pygame.SRCALPHA)
                highlight.fill((255, 215, 0, 50))
                screen.blit(highlight, (100, y_pos - 10))
                pygame.draw.rect(screen, (255, 215, 0), (100, y_pos - 10, LARGURA - 200, 60), 3)
            
            # Nome da corrida
            nome_cor = (255, 255, 255) if i == corrida_selecionada_idx else (200, 200, 200)
            nome_texto = render_text(corrida["nome"], 28, nome_cor, bold=(i == corrida_selecionada_idx), pixel_style=True)
            screen.blit(nome_texto, (120, y_pos))
            
            # Informações
            info_texto = f"Pista {corrida['track']} | {corrida['laps']} voltas | Dificuldade: {corrida['difficulty']}"
            info_cor = (180, 180, 180) if i == corrida_selecionada_idx else (120, 120, 120)
            info = render_text(info_texto, 18, info_cor, bold=False, pixel_style=True)
            screen.blit(info, (120, y_pos + 35))
        
        # Instruções
        instrucoes = render_text("↑↓ navegar | ENTER iniciar | ESC voltar", 16, (150, 150, 150), bold=False, pixel_style=True)
        screen.blit(instrucoes, (10, ALTURA - 30))
        
        pygame.display.flip()
    
    return None

